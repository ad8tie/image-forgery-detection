"""Train the ELA CNN. The test split is never loaded here."""

import argparse
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import f1_score
from torch import nn
from torch.utils.data import DataLoader, WeightedRandomSampler

import config
from src.dataset import DatasetError, ElaManifestDataset, load_manifest, records_for_split
from src.model import build_model
from src.utils import ensure_dir, set_seed, write_json


def choose_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    """Pick a cutoff on validation scores only. Ties stay closest to 0.5.

    The positive class is edited (label 1). The test split must not be passed here.
    """
    fallback = float(config.DECISION_THRESHOLD)
    if scores.size == 0 or len(set(labels.tolist())) < 2:
        return fallback
    best_threshold = fallback
    best_f1 = -1.0
    for threshold in np.linspace(0.05, 0.95, 19):
        predictions = (scores >= threshold).astype(int)
        score = float(f1_score(labels, predictions, pos_label=config.LABEL_MANIPULATED, zero_division=0))
        closer = abs(float(threshold) - fallback) < abs(best_threshold - fallback)
        if score > best_f1 + 1e-6 or (abs(score - best_f1) <= 1e-6 and closer):
            best_f1 = score
            best_threshold = float(threshold)
    return best_threshold


def collect_scores(model, loader, device):
    model.eval()
    scores = []
    labels = []
    with torch.inference_mode():
        for images, batch_labels in loader:
            logits = model(images.to(device))
            scores.append(torch.sigmoid(logits).cpu())
            labels.append(batch_labels.cpu())
    return torch.cat(scores).numpy(), torch.cat(labels).numpy().astype(int)


def balanced_sampler(records: list[dict]) -> WeightedRandomSampler:
    """Sample each class equally often, using training-split counts only."""
    labels = [int(record["label"]) for record in records]
    counts = {config.LABEL_AUTHENTIC: 0, config.LABEL_MANIPULATED: 0}
    for label in labels:
        if label not in counts:
            raise DatasetError("A training label is neither authentic (0) nor edited (1).")
        counts[label] += 1
    if counts[config.LABEL_AUTHENTIC] == 0 or counts[config.LABEL_MANIPULATED] == 0:
        return None
    weights = [1.0 / counts[label] for label in labels]
    return WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)


def run_epoch(model, loader, criterion, optimizer, device):
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    total_correct = 0.0
    total = 0
    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)
        if training:
            optimizer.zero_grad(set_to_none=True)
        with torch.set_grad_enabled(training):
            logits = model(images)
            loss = criterion(logits, labels)
            if training:
                loss.backward()
                optimizer.step()
        batch = labels.shape[0]
        total += batch
        total_loss += float(loss.item()) * batch
        predictions = (torch.sigmoid(logits) >= config.DECISION_THRESHOLD).float()
        total_correct += float((predictions == labels).sum().item())
    return total_loss / total, total_correct / total


def train(
    manifest_path=None,
    checkpoint_path=None,
    history_path=None,
    epochs: int = config.EPOCHS,
    batch_size: int = config.BATCH_SIZE,
    learning_rate: float = config.LEARNING_RATE,
    patience: int = config.EARLY_STOPPING_PATIENCE,
    seed: int = config.SEED,
) -> dict:
    set_seed(seed)
    frame = load_manifest(manifest_path)
    train_records = records_for_split(frame, "train")
    val_records = records_for_split(frame, "val")
    if not train_records or not val_records:
        raise DatasetError("Training needs both a train split and a val split in the manifest.")
    sampler = balanced_sampler(train_records)
    train_loader = DataLoader(
        ElaManifestDataset(train_records, train=True),
        batch_size=batch_size,
        shuffle=sampler is None,
        sampler=sampler,
        num_workers=0,
    )
    val_loader = DataLoader(
        ElaManifestDataset(val_records, train=False),
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )
    device = torch.device("cpu")
    model = build_model()
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=config.WEIGHT_DECAY)
    checkpoint_path = config.CHECKPOINT_PATH if checkpoint_path is None else checkpoint_path
    history_path = config.HISTORY_PATH if history_path is None else history_path
    ensure_dir(checkpoint_path.parent)
    history = {"epochs": [], "best_epoch": None, "best_val_loss": None, "stopped_early": False}
    best_loss = float("inf")
    best_state = None
    best_epoch = None
    wait = 0
    for epoch in range(1, epochs + 1):
        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = run_epoch(model, val_loader, criterion, None, device)
        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_accuracy": train_acc,
            "val_loss": val_loss,
            "val_accuracy": val_acc,
        }
        history["epochs"].append(row)
        print(
            f"epoch={epoch} train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}"
        )
        if val_loss < best_loss:
            best_loss = val_loss
            best_epoch = epoch
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            wait = 0
            torch.save(
                {
                    "state_dict": best_state,
                    "epoch": epoch,
                    "val_loss": val_loss,
                    "image_size": config.IMAGE_SIZE,
                    "dropout": config.DROPOUT,
                    "ela_quality": config.ELA_QUALITY,
                    "ela_scale": config.ELA_SCALE,
                },
                checkpoint_path,
            )
        else:
            wait += 1
            if wait >= patience:
                history["stopped_early"] = True
                print(f"early_stopping epoch={epoch} patience={patience}")
                break
    if best_state is None:
        raise DatasetError("Training did not produce a checkpoint.")
    model.load_state_dict(best_state)
    val_scores, val_labels = collect_scores(model, val_loader, device)
    threshold = choose_threshold(val_scores, val_labels)
    torch.save(
        {
            "state_dict": best_state,
            "epoch": best_epoch,
            "val_loss": best_loss,
            "image_size": config.IMAGE_SIZE,
            "dropout": config.DROPOUT,
            "ela_quality": config.ELA_QUALITY,
            "ela_scale": config.ELA_SCALE,
            "decision_threshold": threshold,
            "label_authentic": config.LABEL_AUTHENTIC,
            "label_manipulated": config.LABEL_MANIPULATED,
        },
        checkpoint_path,
    )
    history["best_epoch"] = best_epoch
    history["best_val_loss"] = best_loss
    history["decision_threshold"] = threshold
    history["checkpoint"] = checkpoint_path.name
    write_json(history_path, history)
    print(f"validation_threshold={threshold:.2f}")
    return history


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the forgery CNN on the train split.")
    parser.add_argument("--manifest", type=Path, default=config.MANIFEST_PATH)
    parser.add_argument("--checkpoint", type=Path, default=config.CHECKPOINT_PATH)
    parser.add_argument("--history", type=Path, default=config.HISTORY_PATH)
    parser.add_argument("--epochs", type=int, default=config.EPOCHS)
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=config.LEARNING_RATE)
    parser.add_argument("--patience", type=int, default=config.EARLY_STOPPING_PATIENCE)
    parser.add_argument("--seed", type=int, default=config.SEED)
    args = parser.parse_args()
    train(
        manifest_path=args.manifest,
        checkpoint_path=args.checkpoint,
        history_path=args.history,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        patience=args.patience,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
