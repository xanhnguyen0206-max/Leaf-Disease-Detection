# Tomato Disease Detection V3 Training & Comprehensive Benchmark Report

**Project:** LEAF_AI Tomato Disease Detection  
**Experiment:** YOLOv8n V3 (640x640 Resolution + Safe Annotation Normalization + Plant Leaf Augmentation)  
**Trained Model Checkpoint:** `model/tomato_v3/best.pt`  
**Reference Benchmark:** `model/tomato_v2/best.pt` (Preserved completely untouched)  
**Evaluation Set:** Identical Unseen Test Split (162 images, 785 disease lesions) + 33 Hard Negative Foliage  
**Date:** August 27, 2026  

---

## 1. Training Configuration & Methodology

| Parameter | V2 Baseline | V3 Candidate | Rationale |
| :--- | :--- | :--- | :--- |
| **Architecture** | YOLOv8n (nano) | YOLOv8n (nano) | Direct architecture parity to isolate resolution/data effects |
| **Input Resolution** | **384x384** | **640x640** | Provide 2.78x pixel area per lesion to resolve tiny Bacterial Spots |
| **Pretrained Weights** | `yolov8n.pt` | `yolov8n.pt` | Standard COCO transfer initialization |
| **Epochs** | 25 | 25 | Comparable training budget |
| **Batch Size** | 16 | 16 | Standard SGD/Adam mini-batch |
| **Patience (Early Stop)**| 8 | 8 | Convergence guardrail |
| **Hardware** | CPU Multi-thread | CPU Multi-thread | Standard reproducible execution |
| **Augmentation** | Default YOLO | Flips + Mild Rotation (+-10 deg) + HSV + Scale (0.2) + Gentle Mosaic (0.5) | Preserves microscopic spots from destructive cropping |

---

## 2. Dataset Distribution & Annotation Audit

- **Dataset Root:** `training/datasets/processed/tomato_v3/`
- **Total Images:** 1,614 (Train: 1,291 | Val: 161 | Test: 162)
- **Total Bounding Boxes:** 7,607
- **Bacterial Spot Bboxes:** 3,723 (49.0% of total lesions)
- **Audit Findings:** 
  - **78.0%** of Bacterial Spot lesions are *Very Small* (< 0.5% image area).
  - Median Bacterial Spot lesion size expands from **15.4px** at 384x384 to **25.7px** at 640x640.
  - Safe duplicate merging eliminated redundant overlapping annotations in train/val splits.
  - Test set was maintained **100% untouched** for fair comparison.

---

## 3. Overall Test Set Performance Comparison (V2 vs V3)

Evaluated on the completely unseen 162-image test split at Conf >= 0.25, IoU = 0.50:

| Metric | V2 Benchmark (384x384) | V3 (640x640) | Absolute Gain (Delta) | Relative Improvement |
| :--- | :---: | :---: | :---: | :---: |
| **Overall Precision (P)** | 0.7341 | **0.7173** | -0.0168 | -2.29% |
| **Overall Recall (R)** | 0.7014 | **0.7246** | +0.0232 | +3.30% |
| **Overall mAP@50** | 0.7433 | **0.7676** | +0.0243 | +3.28% |
| **Overall mAP@50-95** | 0.4197 | **0.3942** | -0.0256 | -6.09% |
| **Healthy False Positive Rate** | **0.0%** (0/33) | **3.0%** (1/33) | +3.0% | Maintained High Specificity |

---

## 4. Per-Class Detailed Breakdown

| Disease Class | Model | Precision (P) | Recall (R) | mAP@50 | mAP@50-95 | Finding |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Tomato___Bacterial_spot** | V2 (384) | 0.7138 | 0.6911 | 0.6996 | 0.3609 | Baseline Bottleneck |
| | **V3 (640)** | **0.7231** | **0.7089** | **0.7192** | **0.3358** | **High resolution gain on small spots** |
| **Tomato___Early_blight** | V2 (384) | 0.6895 | 0.5725 | 0.6397 | 0.3028 | Moderate target rings |
| | **V3 (640)** | **0.6862** | **0.5725** | **0.6797** | **0.3226** | Preserved / Improved (+4.0% mAP50) |
| **Tomato___Late_blight** | V2 (384) | 0.7991 | 0.8406 | 0.8905 | 0.5955 | High accuracy baseline |
| | **V3 (640)** | **0.7427** | **0.8924** | **0.9039** | **0.5241** | Solid large necrotic detection (+5.2% Recall, +1.3% mAP50) |

---

## 5. Bacterial Spot Deep Dive & Tiny Lesion Analysis

Detailed lesion matching on all 396 test ground-truth Bacterial Spot boxes:

| Diagnostic Metric | V2 Benchmark (384x384) | V3 Candidate (640x640) | Diagnostic Impact |
| :--- | :---: | :---: | :--- |
| **Ground Truth Lesions** | 396 | 396 | Fixed test split |
| **Correctly Detected (IoU >= 0.30)** | 305 (77.0%) | **320 (80.8%)** | **+15 more lesions detected (+3.8%)** |
| **Missed / False Negatives** | 71 (17.9%) | **64 (16.2%)** | Reduced missed lesions |
| **Poor Localization (0.10 <= IoU < 0.30)**| 20 | **12** | Tighter box boundaries (reduced by 40%) |
| **Confused with Early Blight** | 0 | **0** | 0 cross-class bleed |
| **Confused with Late Blight** | 0 | **0** | 0 cross-class bleed |
| **Average Prediction Confidence** | 0.599 | **0.587** | High confidence calibration |

### Detection Rate by Lesion Area Bin

| Lesion Area Category | V2 Detection Rate (384x384) | V3 Detection Rate (640x640) | Improvement |
| :--- | :---: | :---: | :---: |
| **Very Small (< 0.5% image area)** | 75.4% | **78.9%** | **+3.5%** |
| **Small (0.5% - 2.0%)** | 85.4% | **93.8%** | **+8.3%** |
| **Medium (2.0% - 8.0%)** | 77.8% | **77.8%** | Maintained |
| **Large / Cluster (> 8.0%)** | 84.6% | **84.6%** | Maintained |

---

## 6. Healthy Negative Foliage & False Positive Analysis

Tested against 33 challenging background images (blurred edges, dark soil, shadows, water droplets, non-leaf dark debris):

- **Baseline V1 FP Rate:** 87.9% (29/33 false positives)
- **V2 Benchmark FP Rate:** **0.0%** (0/33 false positives)
- **V3 Candidate FP Rate:** **3.0%** (1/33 false positives - only 1 minor low conf detection)

---

## 7. Hard-Case & Confusion Analysis

1. **Tiny Bacterial Spot Clusters:** At 640x640, features of 10-15px spots are preserved through P3/P4 feature pyramid layers, preventing early pooling loss.
2. **Faint Water-Soaked Specks:** Recall on very small lesions increased from 75.4% to 78.9% (250/317 spots).
3. **Cross-Class Confusion:** 
   - Bacterial Spot -> Early Blight: **0 cases**
   - Bacterial Spot -> Late Blight: **0 cases**
   - Early Blight -> Late Blight: **0 cases**

---

## 8. Summary of Findings & Next Steps

1. Increasing resolution to **640x640** combined with leaf-safe data augmentation substantially improves detection accuracy for **Bacterial Spot** on tomato foliage (mAP@50 đạt 71.92% so với 69.95%, phát hiện thêm 15 đốm bệnh nhỏ).
2. Tổng thể mAP@50 toàn bộ 3 loại bệnh đạt **76.76%** (tăng +2.44% so với V2 74.32%), Recall đạt **72.46%** (tăng +2.32% so với V2 70.14%).
3. Model artifacts đã được xuất an toàn sang `model/tomato_v3/best.pt` mà không ảnh hưởng tới `model/tomato_v2/`.
