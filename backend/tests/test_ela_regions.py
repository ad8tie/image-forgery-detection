"""ELA summaries come from the pixels, not from a fixed report."""

import numpy as np

from src.ela import ela_regions, ela_statistics
from src.predict import verdict_name


def test_verdict_band_around_threshold():
    assert verdict_name(0.5, 0.5) == "Not sure"
    assert verdict_name(0.59, 0.5) == "Not sure"
    assert verdict_name(0.2, 0.5) == "Likely Authentic"
    assert verdict_name(0.9, 0.5) == "Potentially Manipulated"


def test_stats_and_hotspot_come_from_the_map():
    ela = np.zeros((40, 60, 3), dtype=np.uint8)
    ela[10:22, 12:28] = 180
    stats = ela_statistics(ela)
    assert len(stats["histogram"]) == 16
    assert stats["histogram"][-1] == 0 or stats["max_error"] >= 180
    assert stats["max_error"] >= 180
    assert 0 <= stats["uniform_area_pct"] <= 100
    regions = ela_regions(ela)
    assert len(regions) == 1
    box = regions[0]
    assert box["severity"] == "elevated"
    assert 0 <= box["x"] < 1
    assert 0 < box["w"] <= 1
    assert box["mean_error"] >= 40
