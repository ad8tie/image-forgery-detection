"""One-epoch smoke test on four synthetic images. Not a CASIA result."""

from PIL import Image

import config
from src.evaluate import evaluate
from src.prepare_data import prepare
from src.train import train


def _save(path, color):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 32), color).save(path, format="JPEG", quality=90)


def test_train_and_evaluate_smoke(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    monkeypatch.setattr(config, "RAW_DIR", raw)
    colors = [(20, 20, 20), (200, 200, 200), (20, 180, 20), (180, 20, 20)]
    _save(raw / "Au" / "Au_sec_00001.jpg", colors[0])
    _save(raw / "Au" / "Au_sec_00002.jpg", colors[1])
    _save(raw / "Tp" / "Tp_aaa_00001.jpg", colors[2])
    _save(raw / "Tp" / "Tp_aaa_00002.jpg", colors[3])
    manifest = tmp_path / "manifest.csv"
    report = tmp_path / "prep.json"
    prepare(raw_dir=raw, manifest_path=manifest, report_path=report, subset_size=10, seed=2)
    checkpoint = tmp_path / "model.pt"
    history = tmp_path / "history.json"
    result = train(
        manifest_path=manifest,
        checkpoint_path=checkpoint,
        history_path=history,
        epochs=1,
        batch_size=2,
        patience=1,
        seed=2,
    )
    assert checkpoint.is_file()
    saved = __import__("torch").load(checkpoint, map_location="cpu", weights_only=False)
    assert saved["label_authentic"] == 0
    assert saved["label_manipulated"] == 1
    assert 0.0 < saved["decision_threshold"] < 1.0
    assert result["epochs"]
    assert "train_loss" in result["epochs"][0]
    assert "val_loss" in result["epochs"][0]
    metrics = evaluate(
        manifest_path=manifest,
        checkpoint_path=checkpoint,
        history_path=history,
        eval_dir=tmp_path / "eval",
        batch_size=2,
    )
    assert metrics["status"] == "complete"
    assert metrics["test_samples"] >= 1
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert metrics["decision_threshold"] == saved["decision_threshold"]
    assert "balanced_accuracy" in metrics
    assert "majority_class_accuracy" in metrics
    assert (tmp_path / "eval" / "confusion_matrix.png").is_file()
