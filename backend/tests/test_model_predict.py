"""CNN shape and prediction behavior on synthetic data."""

from pathlib import Path

import pytest
import torch
from PIL import Image

import config
from src.model import ForgeryCNN, build_model
from src.predict import PredictError, load_model, predict_image


def test_cnn_output_shape():
    model = ForgeryCNN(dropout=0.0)
    model.eval()
    batch = torch.zeros(4, 3, 128, 128)
    with torch.inference_mode():
        logits = model(batch)
    assert tuple(logits.shape) == (4,)


def test_missing_checkpoint(tmp_path: Path):
    with pytest.raises(PredictError):
        load_model(tmp_path / "missing.pt")


def test_prediction_fields_with_random_weights(tmp_path: Path):
    model = build_model(dropout=0.0)
    path = tmp_path / "tiny.pt"
    torch.save({"state_dict": model.state_dict(), "dropout": 0.0}, path)
    loaded = load_model(path)
    image = Image.new("RGB", (32, 32), (10, 180, 40))
    result = predict_image(image, model=loaded)
    assert result["predicted_class"] in {*config.CLASS_NAMES.values(), "Not sure"}
    assert 0.0 <= result["model_score"] <= 1.0
    assert "not a calibrated probability" in result["score_label"]
    assert result["ela_image"].size == image.size or result["ela_image"].size[0] <= config.MAX_SIDE


def test_bad_checkpoint(tmp_path: Path):
    path = tmp_path / "bad.pt"
    path.write_bytes(b"not a torch file")
    with pytest.raises(PredictError):
        load_model(path)
