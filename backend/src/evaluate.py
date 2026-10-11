"""Evaluate the saved checkpoint on the held-out test split only."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
)
from torch import nn
from torch.utils.data import DataLoader

import config
from src.dataset import DatasetError, ElaManifestDataset, load_manifest, records_for_split
from src.model import build_model
from src.utils import ensure_dir, read_json, write_json


def _plot_history(history: dict, eval_dir: Path) -> None:
    epochs = [row["epoch"] for row in history.get("epochs", [])]
    if not epochs:
        return
    ensure_dir(eval_dir)
    plt.figure(figsize=(6, 4))
    plt.plot(epochs, [row["train_loss"] for row in history["epochs"]], label="Train")
    plt.plot(epochs, [row["val_loss"] for row in history["epochs"]], label="Validation")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(eval_dir / "loss_curve.png", dpi=120)
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.plot(epochs, [row["train_accuracy"] for row in history["epochs"]], label="Train")
    plt.plot(epochs, [row["val_accuracy"] for row in history["epochs"]], label="Validation")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(eval_dir / "accuracy_curve.png", dpi=120)
    plt.close()


def _plot_confusion(matrix: np.ndarray, labels: list[str], path: Path) -> None:
    plt.figure(figsize=(5, 4))
    plt.imshow(matrix, cmap="Blues")
    plt.xticks([0, 1], labels, rotation=20, ha="right")
    plt.yticks([0, 1], labels)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Test confusion matrix")
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            plt.text(col, row, str(int(matrix[row, col])), ha="center", va="center")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def evaluate(
    manifest_path=None,
    checkpoint_path=None,
    history_path=None,
    eval_dir=None,
    batch_size: int = config.BATCH_SIZE,
) -> dict:
    checkpoint_path = config.CHECKPOINT_PATH if checkpoint_path is None else checkpoint_path
    history_path = config.HISTORY_PATH if history_path is None else history_path
    eval_dir = config.EVAL_DIR if eval_dir is None else eval_dir
    if not checkpoint_path.is_file():
        raise DatasetError("No checkpoint found. Train the model before evaluation.")
    frame = load_manifest(manifest_path)
    records = records_for_split(frame, "test")
    if not records:
        raise DatasetError("The manifest has no test split.")
    loader = DataLoader(
        ElaManifestDataset(records, train=False),
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )
    try:
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    except TypeError:
        checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model = build_model(dropout=checkpoint.get("dropout", config.DROPOUT))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    criterion = nn.BCEWithLogitsLoss()
    logits_all = []
    labels_all = []
    total_loss = 0.0
    total = 0
    with torch.inference_mode():
        for images, labels in loader:
            logits = model(images)
            loss = criterion(logits, labels)
            batch = labels.shape[0]
            total += batch
            total_loss += float(loss.item()) * batch
            logits_all.append(logits.cpu())
            labels_all.append(labels.cpu())
    logits = torch.cat(logits_all)
    labels = torch.cat(labels_all).numpy().astype(int)
    scores = torch.sigmoid(logits).numpy()
    threshold = float(checkpoint.get("decision_threshold", config.DECISION_THRESHOLD))
    predictions = (scores >= threshold).astype(int)
    labels_order = [0, 1]
    matrix = confusion_matrix(labels, predictions, labels=labels_order)
    names = [config.CLASS_NAMES[index] for index in labels_order]
    per_precision, per_recall, per_f1, support = precision_recall_fscore_support(
        labels, predictions, labels=labels_order, zero_division=0
    )
    class_wise = {}
    for index, name in enumerate(names):
        class_wise[name] = {
            "precision": float(per_precision[index]),
            "recall": float(per_recall[index]),
            "f1": float(per_f1[index]),
            "support": int(support[index]),
        }
    positive = config.CLASS_NAMES[config.LABEL_MANIPULATED]
    tn, fp, fn, tp = matrix.ravel()
    metrics = {
        "status": "complete",
        "positive_class": positive,
        "decision_threshold": threshold,
        "score_meaning": (
            "Precision, recall, and F1 use the validation-chosen threshold on the sigmoid of the logit. "
            "That score is a model score, not a calibrated probability. "
            "Older checkpoints without a saved threshold use 0.5."
        ),
        "test_samples": int(total),
        "test_class_counts": {name: int(support[index]) for index, name in enumerate(names)},
        "accuracy": float(accuracy_score(labels, predictions)),
        "balanced_accuracy": (
            float(balanced_accuracy_score(labels, predictions))
            if len(set(labels.tolist())) > 1
            else float(accuracy_score(labels, predictions))
        ),
        "majority_class_accuracy": float(max(support) / support.sum()) if support.sum() else 0.0,
        "precision": float(precision_score(labels, predictions, pos_label=1, zero_division=0)),
        "recall": float(recall_score(labels, predictions, pos_label=1, zero_division=0)),
        "f1": float(f1_score(labels, predictions, pos_label=1, zero_division=0)),
        "loss": total_loss / total,
        "class_wise": class_wise,
        "confusion_matrix": matrix.astype(int).tolist(),
        "confusion_matrix_labels": names,
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "explanation": (
            f"The positive class is {positive}. A false positive is an authentic image "
            "classified as manipulated. A false negative is a manipulated image classified "
            "as authentic. Class imbalance and a small test set change how stable these "
            "numbers are. Accuracy alone can look poor or strong when one class is much larger. "
            "Compare it with balanced accuracy and with majority_class_accuracy, which is the "
            "score of always predicting the bigger test class. Validation chose the checkpoint "
            "and the decision threshold. This test split was not used for training or for that "
            "choice. Results describe this dataset "
            "and this model only, and they do not show that every kind of edit can be detected."
        ),
        "plots": ["loss_curve.png", "accuracy_curve.png", "confusion_matrix.png"],
    }
    ensure_dir(eval_dir)
    if history_path.is_file():
        _plot_history(read_json(history_path), eval_dir)
    _plot_confusion(matrix, names, eval_dir / "confusion_matrix.png")
    write_json(eval_dir / "metrics.json", metrics)
    lines = [
        "metric,value",
        f"accuracy,{metrics['accuracy']}",
        f"balanced_accuracy,{metrics['balanced_accuracy']}",
        f"majority_class_accuracy,{metrics['majority_class_accuracy']}",
        f"decision_threshold,{metrics['decision_threshold']}",
        f"precision,{metrics['precision']}",
        f"recall,{metrics['recall']}",
        f"f1,{metrics['f1']}",
        f"loss,{metrics['loss']}",
        f"test_samples,{metrics['test_samples']}",
        f"false_positives,{fp}",
        f"false_negatives,{fn}",
    ]
    (eval_dir / "metrics.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (eval_dir / "metrics.txt").write_text(
        "\n".join(
            [
                f"Positive class: {positive}",
                f"Test images: {total}",
                f"Accuracy: {metrics['accuracy']:.4f}",
                f"Balanced accuracy: {metrics['balanced_accuracy']:.4f}",
                f"Majority-class accuracy: {metrics['majority_class_accuracy']:.4f}",
                f"Decision threshold: {metrics['decision_threshold']:.2f}",
                f"Precision: {metrics['precision']:.4f}",
                f"Recall: {metrics['recall']:.4f}",
                f"F1: {metrics['f1']:.4f}",
                f"Loss: {metrics['loss']:.4f}",
                f"Confusion matrix (rows actual, columns predicted) {names}: {metrics['confusion_matrix']}",
                metrics["explanation"],
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"test_accuracy={metrics['accuracy']:.4f} f1={metrics['f1']:.4f} samples={total}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the checkpoint on the test split.")
    parser.add_argument("--manifest", type=Path, default=config.MANIFEST_PATH)
    parser.add_argument("--checkpoint", type=Path, default=config.CHECKPOINT_PATH)
    parser.add_argument("--history", type=Path, default=config.HISTORY_PATH)
    parser.add_argument("--eval-dir", type=Path, default=config.EVAL_DIR)
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    args = parser.parse_args()
    evaluate(
        manifest_path=args.manifest,
        checkpoint_path=args.checkpoint,
        history_path=args.history,
        eval_dir=args.eval_dir,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
