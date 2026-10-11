"""ELA unit tests using tiny synthetic images. These are not CASIA samples."""

import numpy as np
import pytest
from PIL import Image

from src.ela import ElaError, compute_ela, load_rgb, preprocess_image


def test_ela_shape_and_range():
    image = Image.fromarray(np.random.default_rng(0).integers(0, 255, (40, 30, 3), dtype=np.uint8))
    ela = compute_ela(image, quality=90, scale=15)
    assert ela.shape == (40, 30, 3)
    assert ela.dtype == np.uint8
    assert int(ela.min()) >= 0
    assert int(ela.max()) <= 255


def test_constant_image_is_safe():
    image = Image.new("RGB", (24, 24), (128, 128, 128))
    ela = compute_ela(image)
    assert ela.shape == (24, 24, 3)
    assert np.isfinite(ela).all()
    assert int(ela.max()) <= 255


def test_near_constant_image_is_safe():
    array = np.full((20, 20, 3), 90, dtype=np.uint8)
    array[0, 0, 0] = 91
    ela = compute_ela(Image.fromarray(array))
    assert ela.shape == (20, 20, 3)
    assert np.isfinite(ela).all()


def test_corrupt_bytes_raise():
    with pytest.raises(ElaError):
        load_rgb(b"this is not an image")


def test_preprocess_tensor_shape():
    image = Image.new("RGB", (50, 60), (20, 40, 60))
    tensor = preprocess_image(image)
    assert tuple(tensor.shape) == (3, 128, 128)
    assert tensor.dtype.is_floating_point
