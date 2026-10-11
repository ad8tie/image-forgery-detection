"""Project configuration. Paths are relative to the repository root."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MANIFEST_PATH = PROCESSED_DIR / "manifest.csv"
PREP_REPORT_PATH = PROCESSED_DIR / "prep_report.json"

OUTPUT_DIR = BACKEND_ROOT / "outputs"
CHECKPOINT_PATH = OUTPUT_DIR / "checkpoints" / "best_model.pt"
HISTORY_PATH = OUTPUT_DIR / "history.json"
EVAL_DIR = OUTPUT_DIR / "eval"
METRICS_PATH = EVAL_DIR / "metrics.json"

# Preprocess. Train and inference must share these values.
IMAGE_SIZE = (128, 128)
MAX_SIDE = 1024
ELA_QUALITY = 90
ELA_SCALE = 15.0
# ELA pixels are 0–255. Values below this cutoff are treated as even compression.
ELA_UNIFORM_CUTOFF = 25.0
# Connected components are grown from pixels at or above this cutoff.
ELA_HOTSPOT_CUTOFF = 40.0
NORM_MEAN = 0.5
NORM_STD = 0.5

BATCH_SIZE = 8
EPOCHS = 15
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
DROPOUT = 0.3
SEED = 42
SUBSET_SIZE = 2000
SPLIT_RATIOS = (0.70, 0.15, 0.15)
EARLY_STOPPING_PATIENCE = 4

UPLOAD_MAX_BYTES = 15 * 1024 * 1024
ALLOWED_UPLOAD_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/bmp",
    "image/tiff",
    "image/tif",
    "image/x-ms-bmp",
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

# Label 1 is the positive class for precision, recall, and F1.
LABEL_AUTHENTIC = 0
LABEL_MANIPULATED = 1
CLASS_NAMES = {
    LABEL_AUTHENTIC: "Likely Authentic",
    LABEL_MANIPULATED: "Potentially Manipulated",
}

ALLOWED_PLOTS = {
    "loss_curve.png",
    "accuracy_curve.png",
    "confusion_matrix.png",
}

DECISION_THRESHOLD = 0.5
