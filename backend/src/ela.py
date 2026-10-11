"""Error Level Analysis.

ELA resaves an image as JPEG and takes the absolute difference from the
original pixels. Regions that compress differently often appear brighter.
That is a compression clue, not proof that an image was forged.
"""

from io import BytesIO

import numpy as np
from PIL import Image, UnidentifiedImageError

import config


class ElaError(Exception):
    """The image could not be decoded or converted for ELA."""


def load_rgb(source) -> Image.Image:
    """Load bytes or a PIL image and return RGB. Does not write to disk."""
    try:
        if isinstance(source, Image.Image):
            image = source
        else:
            image = Image.open(BytesIO(source) if isinstance(source, (bytes, bytearray)) else source)
        image.load()
        return image.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ElaError("The file is not a readable image.") from exc


def limit_max_side(image: Image.Image, max_side: int = config.MAX_SIDE) -> Image.Image:
    width, height = image.size
    longest = max(width, height)
    if longest <= max_side:
        return image
    scale = max_side / float(longest)
    resized = image.resize(
        (max(1, int(round(width * scale))), max(1, int(round(height * scale)))),
        Image.Resampling.BILINEAR,
    )
    return resized


def compute_ela(
    image: Image.Image,
    quality: int = config.ELA_QUALITY,
    scale: float = config.ELA_SCALE,
) -> np.ndarray:
    """Return a uint8 HxWx3 ELA image. Constant images become zeros."""
    rgb = image.convert("RGB")
    buffer = BytesIO()
    rgb.save(buffer, format="JPEG", quality=int(quality))
    buffer.seek(0)
    recompressed = Image.open(buffer).convert("RGB")
    original = np.asarray(rgb, dtype=np.float32)
    compressed = np.asarray(recompressed, dtype=np.float32)
    if original.shape != compressed.shape:
        compressed = np.asarray(
            recompressed.resize(rgb.size, Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    difference = np.abs(original - compressed)
    peak = float(difference.max()) if difference.size else 0.0
    if peak < 1e-6:
        return np.zeros_like(original, dtype=np.uint8)
    amplified = np.clip(difference * float(scale), 0, 255)
    return amplified.astype(np.uint8)


def ela_to_png_bytes(ela: np.ndarray) -> bytes:
    buffer = BytesIO()
    Image.fromarray(ela, mode="RGB").save(buffer, format="PNG")
    return buffer.getvalue()


def preprocess_image(
    image: Image.Image,
    image_size=config.IMAGE_SIZE,
    quality: int = config.ELA_QUALITY,
    scale: float = config.ELA_SCALE,
    max_side: int = config.MAX_SIDE,
) -> "torch.Tensor":
    """ELA then resize. Identical path for training and inference."""
    import torch

    prepared = limit_max_side(image.convert("RGB"), max_side=max_side)
    ela = compute_ela(prepared, quality=quality, scale=scale)
    ela_image = Image.fromarray(ela, mode="RGB").resize(image_size, Image.Resampling.BILINEAR)
    array = np.asarray(ela_image, dtype=np.float32) / 255.0
    array = (array - config.NORM_MEAN) / config.NORM_STD
    tensor = torch.from_numpy(array).permute(2, 0, 1).contiguous()
    return tensor


def ela_statistics(ela: np.ndarray) -> dict:
    """Summaries of one ELA image. Nothing here is a model score."""
    gray = ela.mean(axis=2) if ela.ndim == 3 else ela.astype(np.float32)
    gray = gray.astype(np.float32)
    histogram, _edges = np.histogram(gray, bins=16, range=(0, 256))
    below = float((gray < config.ELA_UNIFORM_CUTOFF).mean()) if gray.size else 0.0
    return {
        "mean_error": float(gray.mean()) if gray.size else 0.0,
        "max_error": float(gray.max()) if gray.size else 0.0,
        "histogram": [int(count) for count in histogram.tolist()],
        "uniform_area_pct": below * 100.0,
    }


def ela_regions(ela: np.ndarray, limit: int = 3) -> list[dict]:
    """Up to three hotspot boxes from connected components on the ELA map."""
    try:
        import cv2
    except ImportError as exc:
        raise ElaError("Hotspot regions need OpenCV, which is not installed.") from exc
    try:
        gray = ela.mean(axis=2) if ela.ndim == 3 else ela.astype(np.float32)
        gray_u8 = np.clip(gray, 0, 255).astype(np.uint8)
        mask = (gray_u8 >= config.ELA_HOTSPOT_CUTOFF).astype(np.uint8)
        count, labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
        height, width = gray_u8.shape
        boxes = []
        for index in range(1, count):
            x, y, w, h, area = (int(value) for value in stats[index])
            if area < 4 or w < 1 or h < 1:
                continue
            region = gray[labels == index]
            mean_error = float(region.mean()) if region.size else 0.0
            severity = "elevated" if mean_error >= config.ELA_HOTSPOT_CUTOFF else "low"
            boxes.append(
                {
                    "x": float(x / width),
                    "y": float(y / height),
                    "w": float(w / width),
                    "h": float(h / height),
                    "severity": severity,
                    "mean_error": mean_error,
                    "area": area,
                }
            )
        boxes.sort(key=lambda item: item["area"], reverse=True)
        for box in boxes:
            box.pop("area", None)
        return boxes[:limit]
    except ElaError:
        raise
    except Exception as exc:
        raise ElaError("Hotspot regions could not be computed.") from exc


def preview_ela_image(
    image: Image.Image,
    quality: int = config.ELA_QUALITY,
    scale: float = config.ELA_SCALE,
) -> Image.Image:
    """ELA visualization at the same working resolution used before the CNN resize."""
    prepared = limit_max_side(image.convert("RGB"), max_side=config.MAX_SIDE)
    return Image.fromarray(compute_ela(prepared, quality=quality, scale=scale), mode="RGB")
