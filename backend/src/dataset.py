"""Manifest dataset. Training applies a horizontal flip; validation and test do not."""

import random

import pandas as pd
import torch
from PIL import Image, UnidentifiedImageError
from torch.utils.data import Dataset

import config
from src.ela import ElaError, preprocess_image
from src.utils import resolve_manifest_path


class DatasetError(Exception):
    """Manifest or image loading failed."""


def load_manifest(path=None) -> pd.DataFrame:
    manifest_path = config.MANIFEST_PATH if path is None else path
    if not manifest_path.is_file():
        raise DatasetError(
            "No manifest was found. Run python -m src.prepare_data after placing CASIA 2.0 under data/raw."
        )
    frame = pd.read_csv(manifest_path)
    required = {"path", "label", "split"}
    missing = required.difference(frame.columns)
    if missing:
        raise DatasetError(f"Manifest is missing columns: {sorted(missing)}")
    return frame


def records_for_split(frame: pd.DataFrame, split: str) -> list[dict]:
    subset = frame[frame["split"] == split]
    return subset.to_dict(orient="records")


class ElaManifestDataset(Dataset):
    def __init__(self, records: list[dict], train: bool = False):
        if not records:
            raise DatasetError("The requested split has no images.")
        self.records = records
        self.train = train

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int):
        record = self.records[index]
        path = resolve_manifest_path(str(record["path"]))
        try:
            with Image.open(path) as image:
                image.load()
                tensor = preprocess_image(image)
        except (ElaError, UnidentifiedImageError, OSError, FileNotFoundError) as exc:
            raise DatasetError(f"Could not read an image listed in the manifest: {path.name}") from exc
        if self.train and random.random() < 0.5:
            tensor = torch.flip(tensor, dims=[2])
        label = torch.tensor(float(record["label"]), dtype=torch.float32)
        return tensor, label
