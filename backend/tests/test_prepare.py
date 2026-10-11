"""Dataset discovery, labels, and split integrity on a tiny fake folder."""

from PIL import Image

from src.prepare_data import prepare


def _save(path, color):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (16, 16), color).save(path, format="JPEG", quality=95)


def test_labels_masks_duplicates_and_splits(tmp_path):
    raw = tmp_path / "raw"
    _save(raw / "Au" / "Au_sec_00001.jpg", (10, 20, 30))
    _save(raw / "Au" / "Au_sec_00002.jpg", (20, 30, 40))
    _save(raw / "Au" / "Au_nat_00003.jpg", (30, 40, 50))
    _save(raw / "Tp" / "Tp_D_CRN_S_N_sec00001_sec00002_00100.jpg", (200, 10, 10))
    _save(raw / "Tp" / "Tp_D_CRN_S_N_nat00003_nat00004_00101.jpg", (10, 200, 10))
    _save(raw / "Tp" / "Tp_plain_00003.jpg", (10, 10, 200))
    _save(raw / "Au" / "Tp_should_not_guess.jpg", (1, 2, 3))
    _save(raw / "notes" / "random_photo.jpg", (4, 5, 6))
    _save(raw / "groundtruth" / "Tp_D_CRN_S_N_sec00001_sec00002_00100.png", (255, 255, 255))
    # Exact duplicate bytes of the first authentic image.
    source = raw / "Au" / "Au_sec_00001.jpg"
    duplicate = raw / "Au" / "Au_sec_00009.jpg"
    duplicate.write_bytes(source.read_bytes())
    broken = raw / "Au" / "Au_sec_00008.jpg"
    broken.write_bytes(b"not-an-image")

    manifest = tmp_path / "manifest.csv"
    report_path = tmp_path / "prep_report.json"
    report = prepare(raw_dir=raw, manifest_path=manifest, report_path=report_path, subset_size=100, seed=1)

    assert report["skipped_mask_count"] == 1
    assert report["duplicate_count"] == 1
    assert report["unreadable_count"] == 1
    assert report["ambiguous_count"] == 1
    assert report["unlabeled_count"] == 1
    assert report["class_summary"]["missing_classes"] == []
    assert report["image_count"] == 6
    for pair in report["split_overlap"].values():
        assert pair == []

    text = manifest.read_text(encoding="utf-8")
    assert "Au_sec_00001.jpg" in text
    assert "groundtruth" not in text
    assert "random_photo" not in text
    assert "Tp_should_not_guess" not in text

    import csv

    splits = {}
    with manifest.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            splits[row["path"]] = (row["split"], row["group_id"])
    linked = [
        key
        for key in splits
        if key.endswith("Au_sec_00001.jpg")
        or key.endswith("Au_sec_00002.jpg")
        or key.endswith("sec00001_sec00002_00100.jpg")
    ]
    assert len({splits[key][1] for key in linked}) == 1
    assert len({splits[key][0] for key in linked}) == 1
