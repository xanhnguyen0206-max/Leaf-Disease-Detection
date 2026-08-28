# Tomato Extra Dataset Inspection & Quality Report

## 1. Executive Summary
This report details the inspection, quality verification, and annotation validation of the newly added raw dataset located at `training/datasets/raw/tomato_extra/`.

The inspection confirms that the dataset contains **1,014 valid images** organized into 4 disease/condition folders (`bacterial_spot`, `early_blight`, `healthy`, `late_blight`). All disease images possess valid, normalized YOLO-format bounding box annotations (`[0, 1]` coordinates), while healthy images provide ground truth negative samples (which will have empty YOLO label files for background training).

---

## 2. Dataset Overview & Image Statistics

| Folder Name | Disease / Condition Target | Image Count | Image Format | Resolutions | Label Files | Annotation Format | Total Valid BBoxes |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `bacterial_spot` | `Tomato___Bacterial_spot` (Class 0) | 281 | JPEG (`.jpg`) | 640 x 640 | 281 | YOLO Bounding Box | 1,376 |
| `early_blight` | `Tomato___Early_blight` (Class 1) | 100 | JPEG (`.jpg`) | 256 x 256 | 100 | YOLO Bounding Box | 616 |
| `healthy` | Healthy Leaves (Negative Background) | 323 | JPEG (`.jpg`) | 4640x3472, 4128x3096 | 323 | Negative (Empty Label) | 0 (Negative) |
| `late_blight` | `Tomato___Late_blight` (Class 2) | 310 | JPEG (`.jpg`) | 640 x 640 | 310 | YOLO Bounding Box | 1,790 |
| **Total** | **All Classes** | **1,014** | **JPEG** | **Various** | **1,014** | **YOLO Standard** | **3,782** |

---

## 3. Detailed Inspection Checklist

### 3.1. Number of Images & Formats
- **Total Images:** 1,014
- **Format:** 100% JPEG (`.jpg`), all valid and readable.
- **Corrupted / Unreadable Images:** 0
- **Extremely Small Images (<64x64):** 0

### 3.2. Existing Annotations & Format Analysis
- **Annotation Type:** YOLO Bounding Box (`class_id x_center y_center width height`).
- **Coordinate Validation:** All coordinates are normalized floats within `[0.0, 1.0]`, with strictly positive widths and heights ($w > 0, h > 0$).
- **Invalid / Out-of-bounds Bounding Boxes:** 0
- **Missing Label/Image Pairs:** 0 (Every image has a corresponding label file).

### 3.3. Annotation Class Mapping
- **`bacterial_spot`**: Raw annotations contain spot annotations across disease stages. All mapped to Target Class `0: Tomato___Bacterial_spot` (1,376 bboxes).
- **`early_blight`**: All annotations map to Target Class `1: Tomato___Early_blight` (616 bboxes).
- **`late_blight`**: Raw annotations delineate late blight lesions. All mapped to Target Class `2: Tomato___Late_blight` (1,790 bboxes).
- **`healthy`**: Contains whole leaf bounding boxes in raw format; mapped to **empty label files** (0 lines) in Dataset V2 to provide background negative learning samples and suppress false positives.

### 3.4. Duplicate & Hash Collision Analysis
- **MD5 Hash Overlap with Raw Tomato (Baseline):** 0 duplicates found (100% new images).
- **MD5 Hash Overlap with Processed Tomato (Baseline):** 0 duplicates found.
- **Internal Duplicates within `tomato_extra`:** 0 duplicates.

---

## 4. Usability & Next Step Determination
- **Usable New Disease Images for Detection:** 691 images (3,782 bounding boxes)
- **Usable New Healthy Background Images:** 323 images (negative samples)
- **Excluded Images (due to missing annotations / corruption):** 0 images
- **Conclusion:** The new dataset is 100% complete, properly annotated with bounding boxes, and ready for integration into **Dataset V2** (`training/datasets/processed/tomato_v2/`).
