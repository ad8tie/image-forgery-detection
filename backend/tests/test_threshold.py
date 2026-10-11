"""Label polarity and validation threshold. No CASIA images."""

import numpy as np
import torch
from PIL import Image

import config
from src.predict import load_model, predict_image
from src.train import choose_threshold


def test_label_polarity_authentic_zero_edited_one():
    assert config.LABEL_AUTHENTIC == 0
    assert config.LABEL_MANIPULATED == 1
    assert config.CLASS_NAMES[0] == "Likely Authentic"
    assert config.CLASS_NAMES[1] == "Potentially Manipulated"


def test_low_scores_choose_threshold_below_half():
    scores = np.full(8, 0.2)
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    threshold = choose_threshold(scores, labels)
    assert threshold < 0.5
    predictions = (scores >= threshold).astype(int)
    assert predictions.tolist() == labels.tolist() or predictions.sum() == 8


def test_checkpoint_threshold_is_used(tmp_path):
    from src.model import build_model

    model = build_model(dropout=0.0)
    path = tmp_path / "model.pt"
    torch.save(
        {"state_dict": model.state_dict(), "dropout": 0.0, "decision_threshold": 0.2},
        path,
    )
    loaded = load_model(path)
    assert loaded.decision_threshold == 0.2
    image = Image.new("RGB", (16, 16), (30, 30, 30))
    result = predict_image(image, model=loaded)
    assert result["predicted_class"] in config.CLASS_NAMES.values()
    assert 0.0 <= result["model_score"] <= 1.0
