# CASIA 2.0 data

This folder is where you place the dataset yourself. The project does not download it and does not ship sample photos labeled as CASIA.

## Download

1. CASIA 2.0 image tampering dataset: https://www.kaggle.com/datasets/divg07/casia-20-image-tampering-detection-dataset
2. Corrected ground truth (optional, for reference only): https://github.com/SunnyHaze/CASIA2.0-Corrected-Groundtruth

Kaggle usually requires an account. Download the archive in a browser, then extract it on your machine. Do not commit the images.

## Folder layout

Put the extracted images under `data/raw`. Either of these layouts works:

```text
data/raw/Au/*.jpg
data/raw/Tp/*.jpg
```

```text
data/raw/CASIA2/Au/*.jpg
data/raw/CASIA2/Tp/*.tif
```

Supported photo extensions: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tif`, `.tiff`.

If you also download the corrected masks, keep them in a separate folder whose name contains `groundtruth`, `gt`, `mask`, or `annotation`. Those files are skipped. Do not mix mask images into `Au` or `Tp`.

## How labels are chosen

- Folder `Au`, `authentic`, or `pristine` means Likely Authentic (label 0).
- Folder `Tp`, `tampered`, `spliced`, or `manipulated` means Potentially Manipulated (label 1).
- A filename starting with `Au_` or `Tp_` is used the same way.
- If the folder and the filename disagree, the file is excluded and listed as ambiguous.
- Files that match neither rule are excluded. The script does not guess.

CASIA tampered names often contain authentic ids such as `sec00001`. When those ids match an `Au_sec_00001` file in the same raw folder, the related files are forced into the same train, validation, or test split. Links that do not match a file in the folder are reported and are not treated as known groups.

## Prepare

From `backend` on Windows PowerShell, after the virtual environment is active:

```powershell
python -m src.prepare_data
```

The command writes:

- `data/processed/manifest.csv` with `path`, `label`, `label_name`, `split`, `group_id`
- `data/processed/prep_report.json` with class counts, missing classes, duplicates, unreadable files, and leakage notes

Default split is 70% train, 15% validation, 15% test. The default subset size is 2000 images, balanced by class when enough data exists. Smaller folders are kept as they are. The test split is not used by training.
