"""Build a labeled manifest from a local CASIA-style folder.

Labels come only from documented folder names or filename prefixes.
Uncertain labels are excluded and reported. Ground-truth masks are skipped.
"""

import argparse
import csv
import hashlib
import random
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image, UnidentifiedImageError

import config
from src.utils import ensure_dir, project_relative, write_json

IMAGE_EXTENSIONS = config.ALLOWED_EXTENSIONS
MASK_DIR_NAMES = {
    "gt",
    "gts",
    "groundtruth",
    "groundtruths",
    "ground_truth",
    "ground-truth",
    "mask",
    "masks",
    "annotation",
    "annotations",
}
AUTHENTIC_DIRS = {"au", "authentic", "authentics", "pristine"}
TAMPERED_DIRS = {"tp", "tampered", "tamper", "spliced", "manipulated"}

AUTHENTIC_NAME = re.compile(r"(?i)^au_([a-z]{3})_(\d+)")
NAME_AUTHENTIC = re.compile(r"(?i)^(au|authentic)([_\-.]|$)")
NAME_TAMPERED = re.compile(r"(?i)^(tp|tampered)([_\-.]|$)")
SOURCE_TOKEN = re.compile(r"(?i)([a-z]{3})(\d{4,5})")


class UnionFind:
    def __init__(self):
        self.parent = {}

    def add(self, item):
        self.parent.setdefault(item, item)

    def find(self, item):
        self.add(item)
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left, right):
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left != root_right:
            self.parent[root_right] = root_left


def _is_mask_path(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    if parts.intersection(MASK_DIR_NAMES):
        return True
    stem = path.stem.lower()
    return stem.endswith("_gt") or stem.endswith("_mask") or "groundtruth" in stem


def _folder_label(path: Path):
    for part in reversed(path.parts[:-1]):
        name = part.lower()
        if name in AUTHENTIC_DIRS:
            return config.LABEL_AUTHENTIC
        if name in TAMPERED_DIRS:
            return config.LABEL_MANIPULATED
    return None


def _name_label(path: Path):
    stem = path.name
    if NAME_AUTHENTIC.match(stem):
        return config.LABEL_AUTHENTIC
    if NAME_TAMPERED.match(stem):
        return config.LABEL_MANIPULATED
    return None


def authentic_key(path: Path):
    match = AUTHENTIC_NAME.match(path.name)
    if not match:
        return None
    return f"{match.group(1).lower()}{int(match.group(2)):05d}"


def tampered_keys(path: Path) -> list[str]:
    if _name_label(path) != config.LABEL_MANIPULATED:
        return []
    keys = []
    for letters, digits in SOURCE_TOKEN.findall(path.stem):
        keys.append(f"{letters.lower()}{int(digits):05d}")
    return keys


def _file_md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _readable(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.load()
        return True
    except (UnidentifiedImageError, OSError, ValueError):
        return False


def discover_images(raw_dir: Path) -> dict:
    report = {
        "raw_dir": project_relative(raw_dir) if raw_dir.exists() else str(raw_dir.name),
        "skipped_masks": [],
        "unreadable": [],
        "duplicates": [],
        "ambiguous": [],
        "unlabeled": [],
        "accepted": [],
    }
    if not raw_dir.is_dir():
        report["error"] = "Dataset directory does not exist."
        return report

    seen_hashes = {}
    for path in sorted(raw_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        try:
            relative = path.resolve().relative_to(config.PROJECT_ROOT).as_posix()
        except ValueError:
            relative = path.resolve().relative_to(raw_dir.resolve()).as_posix()
        if _is_mask_path(path):
            report["skipped_masks"].append(relative)
            continue
        digest = _file_md5(path)
        if digest in seen_hashes:
            report["duplicates"].append({"path": relative, "duplicate_of": seen_hashes[digest]})
            continue
        if not _readable(path):
            report["unreadable"].append(relative)
            continue
        folder_label = _folder_label(path)
        name_label = _name_label(path)
        if folder_label is not None and name_label is not None and folder_label != name_label:
            report["ambiguous"].append(
                {"path": relative, "folder_label": folder_label, "name_label": name_label}
            )
            continue
        label = folder_label if folder_label is not None else name_label
        if label is None:
            report["unlabeled"].append(relative)
            continue
        seen_hashes[digest] = relative
        report["accepted"].append(
            {
                "path": relative,
                "absolute": path,
                "label": int(label),
                "auth_key": authentic_key(path),
                "source_keys": tampered_keys(path),
            }
        )
    return report


def assign_groups(records: list[dict]) -> tuple[list[dict], list[str]]:
    """Union-find on reliable CASIA source ids so related files share a split."""
    notes = []
    known_auth = {record["auth_key"] for record in records if record["auth_key"]}
    union = UnionFind()
    for record in records:
        union.add(record["path"])
    linked = 0
    unresolved = 0
    for record in records:
        keys = []
        if record["auth_key"]:
            keys.append(record["auth_key"])
        for key in record["source_keys"]:
            if key in known_auth:
                keys.append(key)
            else:
                unresolved += 1
        for key in keys:
            union.union(record["path"], f"key:{key}")
        if record["label"] == config.LABEL_MANIPULATED and record["source_keys"] and keys:
            linked += 1
        elif record["label"] == config.LABEL_MANIPULATED and record["source_keys"] and not any(
            key in known_auth for key in record["source_keys"]
        ):
            notes.append(
                f"No matching authentic file for source ids in {Path(record['path']).name}. "
                "It was placed in its own group."
            )
    if unresolved:
        notes.append(
            f"{unresolved} tampered source-id references did not match an authentic file in this folder. "
            "Those links were not used for grouping. If the missing originals are added later, "
            "rerun prepare_data so they share a split."
        )
    if linked == 0:
        notes.append(
            "No reliable original/manipulated filename links were found. "
            "Splits are grouped only by file, so source leakage cannot be ruled out from names alone."
        )
    for record in records:
        record["group_id"] = union.find(record["path"])
    return records, notes


def select_balanced_subset(records: list[dict], subset_size: int, seed: int) -> tuple[list[dict], str]:
    if subset_size <= 0 or len(records) <= subset_size:
        return records, "All accepted images were kept because the folder is within the subset size."
    groups = defaultdict(list)
    for record in records:
        groups[record["group_id"]].append(record)
    order = list(groups.keys())
    random.Random(seed).shuffle(order)
    target = subset_size // 2
    counts = {config.LABEL_AUTHENTIC: 0, config.LABEL_MANIPULATED: 0}
    chosen = []
    deferred = []
    for group_id in order:
        items = groups[group_id]
        next_counts = counts.copy()
        overflow = False
        for item in items:
            next_counts[item["label"]] += 1
            if next_counts[item["label"]] > target:
                overflow = True
        if overflow:
            deferred.append(items)
            continue
        counts = next_counts
        chosen.extend(items)
    for items in deferred:
        if len(chosen) >= subset_size:
            break
        chosen.extend(items)
    if len(chosen) > subset_size:
        # Drop whole trailing groups until the cap is met, keeping groups intact.
        grouped = defaultdict(list)
        for item in chosen:
            grouped[item["group_id"]].append(item)
        trimmed = []
        for group_id in list(grouped.keys()):
            if len(trimmed) >= subset_size:
                break
            trimmed.extend(grouped[group_id])
        chosen = trimmed
    note = (
        f"Selected {len(chosen)} images toward a class-balanced subset of {subset_size}. "
        "Groups of related files were kept together, so the exact size and balance can differ slightly."
    )
    return chosen, note


def assign_splits(records: list[dict], ratios: tuple[float, float, float], seed: int) -> list[str]:
    if abs(sum(ratios) - 1.0) > 1e-6:
        raise ValueError("Split ratios must sum to 1.")
    groups = defaultdict(list)
    for record in records:
        groups[record["group_id"]].append(record)
    order = sorted(groups)
    random.Random(seed).shuffle(order)
    total = len(records)
    targets = {
        "train": ratios[0] * total,
        "val": ratios[1] * total,
        "test": ratios[2] * total,
    }
    counts = {"train": 0, "val": 0, "test": 0}
    notes = []
    for group_id in order:
        items = groups[group_id]
        split = min(counts, key=lambda name: counts[name] / targets[name] if targets[name] else counts[name])
        for item in items:
            item["split"] = split
        counts[split] += len(items)
    notes.append(
        "Related images that shared a reliable source id were assigned to the same split. "
        f"Resulting counts: train={counts['train']}, val={counts['val']}, test={counts['test']}."
    )
    return notes


def class_summary(records: list[dict]) -> dict:
    counts = {
        config.CLASS_NAMES[config.LABEL_AUTHENTIC]: sum(
            1 for record in records if record["label"] == config.LABEL_AUTHENTIC
        ),
        config.CLASS_NAMES[config.LABEL_MANIPULATED]: sum(
            1 for record in records if record["label"] == config.LABEL_MANIPULATED
        ),
    }
    missing = [name for name, count in counts.items() if count == 0]
    present = [count for count in counts.values() if count]
    imbalance = None
    if len(present) == 2 and max(present) > 0:
        imbalance = round(min(present) / max(present), 4)
    return {"class_counts": counts, "missing_classes": missing, "minority_majority_ratio": imbalance}


def write_manifest(records: list[dict], manifest_path: Path) -> None:
    ensure_dir(manifest_path.parent)
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "label", "label_name", "split", "group_id"])
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "path": record["path"],
                    "label": record["label"],
                    "label_name": config.CLASS_NAMES[record["label"]],
                    "split": record["split"],
                    "group_id": record["group_id"],
                }
            )


def prepare(
    raw_dir: Path | None = None,
    manifest_path: Path | None = None,
    report_path: Path | None = None,
    subset_size: int = config.SUBSET_SIZE,
    ratios: tuple[float, float, float] = config.SPLIT_RATIOS,
    seed: int = config.SEED,
) -> dict:
    raw_dir = config.RAW_DIR if raw_dir is None else raw_dir
    manifest_path = config.MANIFEST_PATH if manifest_path is None else manifest_path
    report_path = config.PREP_REPORT_PATH if report_path is None else report_path
    discovered = discover_images(raw_dir)
    records = discovered.pop("accepted")
    records, leakage_notes = assign_groups(records)
    records, subset_note = select_balanced_subset(records, subset_size, seed)
    split_notes = assign_splits(records, ratios, seed) if records else []
    summary = class_summary(records)
    paths = [record["path"] for record in records]
    overlap = {
        "train_val": sorted(set(_paths(records, "train")) & set(_paths(records, "val"))),
        "train_test": sorted(set(_paths(records, "train")) & set(_paths(records, "test"))),
        "val_test": sorted(set(_paths(records, "val")) & set(_paths(records, "test"))),
    }
    report = {
        "status": "ready" if records and not summary["missing_classes"] else "incomplete",
        "image_count": len(records),
        "subset_note": subset_note,
        "class_summary": summary,
        "split_counts": {
            split: sum(1 for record in records if record["split"] == split) for split in ("train", "val", "test")
        },
        "skipped_mask_count": len(discovered["skipped_masks"]),
        "unreadable_count": len(discovered["unreadable"]),
        "duplicate_count": len(discovered["duplicates"]),
        "ambiguous_count": len(discovered["ambiguous"]),
        "unlabeled_count": len(discovered["unlabeled"]),
        "ambiguous_examples": discovered["ambiguous"][:20],
        "unlabeled_examples": discovered["unlabeled"][:20],
        "unreadable_examples": discovered["unreadable"][:20],
        "duplicate_examples": discovered["duplicates"][:20],
        "leakage_notes": leakage_notes + split_notes,
        "split_overlap": overlap,
        "manifest": project_relative(manifest_path) if records else None,
        "label_rules": (
            "Authentic if a parent folder is Au/authentic/pristine or the filename starts with Au_. "
            "Manipulated if a parent folder is Tp/tampered/spliced/manipulated or the filename starts with Tp_. "
            "Folder and filename must agree when both are present. Mask folders are excluded."
        ),
    }
    if records:
        write_manifest(records, manifest_path)
    elif manifest_path.is_file():
        manifest_path.unlink()
    write_json(report_path, report)
    report["unique_paths"] = len(set(paths))
    return report


def _paths(records, split):
    return [record["path"] for record in records if record["split"] == split]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a CASIA-style manifest.")
    parser.add_argument("--raw-dir", type=Path, default=config.RAW_DIR)
    parser.add_argument("--manifest", type=Path, default=config.MANIFEST_PATH)
    parser.add_argument("--report", type=Path, default=config.PREP_REPORT_PATH)
    parser.add_argument("--subset-size", type=int, default=config.SUBSET_SIZE)
    parser.add_argument("--seed", type=int, default=config.SEED)
    args = parser.parse_args()
    report = prepare(
        raw_dir=args.raw_dir,
        manifest_path=args.manifest,
        report_path=args.report,
        subset_size=args.subset_size,
        seed=args.seed,
    )
    print(f"status={report['status']} images={report['image_count']}")
    print(f"classes={report['class_summary']['class_counts']}")
    print(f"splits={report['split_counts']}")
    if report["class_summary"]["missing_classes"]:
        print(f"missing_classes={report['class_summary']['missing_classes']}")
    for note in report["leakage_notes"]:
        print(f"note: {note}")
    if report["image_count"] == 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
