"""Small shared helpers."""

import json
import random
from pathlib import Path

import numpy as np
import torch

import config


def set_seed(seed: int | None = None) -> int:
    value = config.SEED if seed is None else int(seed)
    random.seed(value)
    np.random.seed(value)
    torch.manual_seed(value)
    return value


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def project_relative(path: Path) -> str:
    """Return a project-relative POSIX path, or a data-relative path if needed."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(config.PROJECT_ROOT).as_posix()
    except ValueError:
        try:
            return resolved.relative_to(config.RAW_DIR.resolve()).as_posix()
        except ValueError:
            return resolved.name


def resolve_manifest_path(stored: str) -> Path:
    """Resolve a manifest path that was stored relative to the project or raw dir."""
    candidate = Path(stored)
    if candidate.is_absolute():
        return candidate
    project_path = (config.PROJECT_ROOT / candidate).resolve()
    if project_path.is_file():
        return project_path
    raw_path = (config.RAW_DIR / candidate).resolve()
    return raw_path


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
