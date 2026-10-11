"""API tests. No full dataset and no claim of a trained project model."""

from pathlib import Path

import pytest
import torch
from fastapi.testclient import TestClient
from PIL import Image

import config
import main
from main import app
from src.model import build_model


@pytest.fixture()
def client():
    return TestClient(app)


def test_health_missing_weights(client, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CHECKPOINT_PATH", tmp_path / "missing.pt")
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["model_ready"] is False
    assert body["status"] == "not_ready"
    assert "Traceback" not in response.text


def test_analyze_missing_weights(client, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CHECKPOINT_PATH", tmp_path / "missing.pt")
    image = tmp_path / "tiny.jpg"
    Image.new("RGB", (8, 8), (1, 2, 3)).save(image, format="JPEG")
    with image.open("rb") as handle:
        response = client.post("/api/analyze", files={"file": ("tiny.jpg", handle, "image/jpeg")})
    assert response.status_code == 503
    assert "Traceback" not in response.text


def test_analyze_invalid_upload(client, tmp_path, monkeypatch):
    checkpoint = tmp_path / "model.pt"
    model = build_model(dropout=0.0)
    torch.save({"state_dict": model.state_dict(), "dropout": 0.0}, checkpoint)
    monkeypatch.setattr(config, "CHECKPOINT_PATH", checkpoint)
    response = client.post("/api/analyze", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 400
    response = client.post(
        "/api/analyze", files={"file": ("photo.jpg", b"not-really-jpeg", "image/jpeg")}
    )
    assert response.status_code == 400


def test_analyze_success_shape(client, tmp_path, monkeypatch):
    checkpoint = tmp_path / "model.pt"
    model = build_model(dropout=0.0)
    torch.save({"state_dict": model.state_dict(), "dropout": 0.0}, checkpoint)
    monkeypatch.setattr(config, "CHECKPOINT_PATH", checkpoint)
    image = tmp_path / "tiny.png"
    Image.new("RGB", (12, 12), (30, 90, 200)).save(image, format="PNG")
    with image.open("rb") as handle:
        response = client.post("/api/analyze", files={"file": ("tiny.png", handle, "image/png")})
    assert response.status_code == 200
    body = response.json()
    assert body["predicted_class"] in {*config.CLASS_NAMES.values(), "Not sure"}
    assert 0.0 <= body["model_score"] <= 1.0
    assert body["ela_png_base64"]
    assert body["ela_map_png_base64"]
    assert body["label"] in {"Likely Authentic", "Potentially Manipulated", "Not sure"}
    assert body["score"] == body["model_score"]
    assert len(body["ela_stats"]["histogram"]) == 16
    assert len(body["sha256"]) == 64
    assert "calibrated probability" in body["score_label"]


def test_metrics_pending(client, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "METRICS_PATH", tmp_path / "metrics.json")
    monkeypatch.setattr(config, "HISTORY_PATH", tmp_path / "history.json")
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


def test_plot_name_validation(client, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EVAL_DIR", tmp_path)
    response = client.get("/api/plots/not_a_plot.png")
    assert response.status_code == 404
    response = client.get("/api/plots/..%2F..%2Fetc%2Fpasswd")
    assert response.status_code == 404
    missing = client.get("/api/plots/loss_curve.png")
    assert missing.status_code == 404


def test_health_and_predict_aliases(client, tmp_path, monkeypatch):
    import numpy as np

    checkpoint = tmp_path / "model.pt"
    model = build_model(dropout=0.0)
    torch.save({"state_dict": model.state_dict(), "dropout": 0.0}, checkpoint)
    monkeypatch.setattr(config, "CHECKPOINT_PATH", checkpoint)
    alias = client.get("/health")
    original = client.get("/api/health")
    assert alias.status_code == 200
    assert alias.json()["model_ready"] is True
    assert alias.json()["status"] == original.json()["status"]

    array = np.zeros((48, 48, 3), dtype=np.uint8)
    array[:, :24] = (20, 40, 80)
    array[:, 24:] = (220, 180, 40)
    image = tmp_path / "split.png"
    Image.fromarray(array).save(image)
    with image.open("rb") as handle:
        low = client.post(
            "/predict",
            files={"file": ("split.png", handle, "image/png")},
            data={"quality": "40", "scale": "4"},
        )
    with image.open("rb") as handle:
        high = client.post(
            "/predict",
            files={"file": ("split.png", handle, "image/png")},
            data={"quality": "95", "scale": "30"},
        )
    assert low.status_code == 200
    assert high.status_code == 200
    assert low.json()["ela_quality"] == 40
    assert high.json()["ela_scale"] == 30.0
    assert low.json()["ela_png_base64"] != high.json()["ela_png_base64"]
    assert 0.0 <= low.json()["model_score"] <= 1.0


def test_predict_tiny_checkpoint_and_missing(client, tmp_path, monkeypatch):
    image = tmp_path / "tiny.png"
    Image.new("RGB", (8, 8), (12, 34, 56)).save(image, format="PNG")
    missing = tmp_path / "missing.pt"
    monkeypatch.setattr(config, "CHECKPOINT_PATH", missing)
    main.service.model = None
    main.service.ready = False
    with image.open("rb") as handle:
        absent = client.post("/predict", files={"file": ("tiny.png", handle, "image/png")})
    assert absent.status_code != 500
    assert absent.headers["content-type"].startswith("application/json")
    assert "detail" in absent.json()
    assert "Traceback" not in absent.text
    assert "checkpoint" not in absent.text.lower()

    checkpoint = tmp_path / "tiny.pt"
    model = build_model(dropout=0.0)
    torch.save({"state_dict": model.state_dict(), "dropout": 0.0}, checkpoint)
    monkeypatch.setattr(config, "CHECKPOINT_PATH", checkpoint)
    main.service.model = None
    main.service.ready = False
    with image.open("rb") as handle:
        ready = client.post("/predict", files={"file": ("tiny.png", handle, "image/png")})
    assert ready.status_code == 200
    body = ready.json()
    assert body["threshold"] == config.DECISION_THRESHOLD
    assert isinstance(body["regions"], list)

    with image.open("rb") as handle:
        bad = client.post(
            "/predict",
            files={"file": ("tiny.png", handle, "image/png")},
            data={"quality": "nope", "scale": "10"},
        )
    assert bad.status_code == 400
    assert bad.headers["content-type"].startswith("application/json")
    assert "Traceback" not in bad.text
    assert str(tmp_path) not in bad.text


def test_predict_without_opencv_is_json(client, tmp_path, monkeypatch):
    checkpoint = tmp_path / "tiny.pt"
    model = build_model(dropout=0.0)
    torch.save({"state_dict": model.state_dict(), "dropout": 0.0}, checkpoint)
    monkeypatch.setattr(config, "CHECKPOINT_PATH", checkpoint)
    main.service.model = None
    main.service.ready = False

    import builtins

    real_import = builtins.__import__

    def guarded(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "cv2":
            raise ImportError("No module named cv2")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded)
    image = tmp_path / "tiny.png"
    Image.new("RGB", (8, 8), (9, 9, 9)).save(image, format="PNG")
    with image.open("rb") as handle:
        response = client.post("/predict", files={"file": ("tiny.png", handle, "image/png")})
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["detail"] == "Inference failed for this image."
    assert "Traceback" not in response.text
    assert "cv2" not in response.text
    assert str(tmp_path) not in response.text


def test_dataset_status_missing(client, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PREP_REPORT_PATH", tmp_path / "prep_report.json")
    monkeypatch.setattr(config, "MANIFEST_PATH", tmp_path / "manifest.csv")
    response = client.get("/api/dataset/status")
    assert response.status_code == 200
    body = response.json()
    assert body["training_data_ready"] is False
    assert "/workspace" not in response.text
    assert "\\\\" not in response.text or "Users" not in response.text
