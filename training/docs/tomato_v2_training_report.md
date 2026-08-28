# LEAF_AI: Tomato Disease Detection YOLOv8n V2 Training & Evaluation Report

**Model Name:** LEAF_AI Tomato Disease Detection YOLOv8n V2  
**Date:** August 26, 2026  
**Architecture:** Ultralytics YOLOv8n (Pretrained fine-tuning from `yolov8n.pt`)  
**Hardware:** CPU Execution (Intel Core i7-6500U, 4 Multi-threaded Workers)  
**Dataset:** Dataset V2 (`training/datasets/processed/tomato_v2/`)  
**Model Artifacts:** `model/tomato_v2/` (`best.pt`, `classes.json`, `metadata.json`)  

---

## 1. Executive Summary & Key Achievements

The primary objective of the **Dataset V2 expansion and retraining** was twofold:
1. **Eliminate Background False Positives:** The original baseline model suffered from an 87.9% false-positive rate on healthy tomato leaves and dark/blurred background regions (misclassifying them as Early Blight).
2. **Improve Detection Performance & Class Balance:** Increase coverage and bounding box precision across Bacterial Spot, Early Blight, and Late Blight.

### Key Results
- **False Positive Rate on Hard Negative Healthy Leaves:** Reduced from **87.9% (Baseline)** down to **0.0% (V2 Model)** — a **100% elimination** of false background detections.
- **Test mAP@50:** Increased from **0.6968 (Baseline)** to **0.7430 (V2)** (**+4.62% absolute gain**).
- **Test Precision:** Increased from **0.6937 (Baseline)** to **0.7340 (V2)** (**+4.03% absolute gain**).
- **Test Recall:** Increased from **0.6541 (Baseline)** to **0.7010 (V2)** (**+4.69% absolute gain**).
- **Test mAP@50-95:** Increased from **0.4037 (Baseline)** to **0.4200 (V2)** (**+1.63% absolute gain**).
- **Late Blight mAP@50:** Reached **0.8900** (0.799 Precision, 0.841 Recall).

---

## 2. Dataset V2 Composition & Splits

Dataset V2 combines the 600 baseline images with 1,014 newly inspected, validated images from `training/datasets/raw/tomato_extra/`.

### 2.1. Overall Dataset Summary

| Category | Description | Count | Total Bounding Boxes |
| :--- | :--- | :---: | :---: |
| **Total Images** | Combined Baseline + Extra | **1,614** | **7,610** |
| **Healthy Negative Images** | Negative samples (empty `.txt` labels) | **323** | **0** (Clean background) |
| **Disease Images** | Images containing 1+ disease boxes | **1,291** | **7,610** |
| **Excluded Images** | Unusable / unannotated images | **0** | **0** |

### 2.2. Valid Bounding Boxes per Disease Class

| Class ID | Target Class Name | Baseline Boxes | Extra Added Boxes | Total V2 Boxes |
| :---: | :--- | :---: | :---: | :---: |
| `0` | `Tomato___Bacterial_spot` | 2,351 | 1,376 | **3,727** |
| `1` | `Tomato___Early_blight` | 1,005 | 616 | **1,621** |
| `2` | `Tomato___Late_blight` | 473 | 1,790 | **2,263** |
| **Total** | **All Diseases** | **3,829** | **3,782** | **7,611** |

### 2.3. Stratified Train / Validation / Test Splits

| Split | Images | Healthy Negative Images | Disease Images | Disease Bounding Boxes | Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Train** | 1,291 | 258 | 1,033 | 6,139 | 80.0% |
| **Validation** | 161 | 32 | 129 | 687 | 10.0% |
| **Test** | 162 | 33 | 129 | 785 | 10.0% |
| **Total** | **1,614** | **323** | **1,291** | **7,611** | **100.0%** |

*Note: In addition, a dedicated subset of 33 test-slice healthy images is archived at `training/datasets/processed/tomato_v2/hard_negatives/` for benchmark verification.*

---

## 3. Training Configuration

| Parameter | Configuration Value | Rationale |
| :--- | :--- | :--- |
| **Base Architecture** | YOLOv8n (`yolov8n.pt`) | Lightweight, fast CPU inference, mobile-ready edge compatibility |
| **Input Image Size** | 384 x 384 | Optimal balance between localization detail and efficient CPU training |
| **Batch Size** | 32 | Maximizes CPU SIMD / AVX2 vectorization efficiency |
| **Total Epochs** | 25 | Sufficient convergence with early stopping safeguard |
| **Early Stopping Patience** | 8 epochs | Prevents overfitting while allowing fine-tuning |
| **Optimizer** | AdamW (`lr=0.001429`, `momentum=0.9`) | Stable gradient updates and adaptive weight decay |
| **RAM Dataset Caching** | Enabled (`cache=True`, ~0.5 GB RAM) | Eliminates disk I/O bottlenecks during CPU training |
| **Training Duration** | 2.74 hours | Full 25 epochs completed |

---

## 4. Benchmark Evaluation: Baseline vs. Model V2

Evaluation on the completely unseen test split (**162 test images**, 33 healthy negatives, 784 ground-truth bounding boxes):

### 4.1. Overall Test Metrics Comparison

| Metric | Baseline Model (`model/tomato/best.pt`) | V2 Model (`model/tomato_v2/best.pt`) | Absolute Improvement | Relative Gain |
| :--- | :---: | :---: | :---: | :---: |
| **Precision** | 0.6937 | **0.7340** | **+0.0403** | **+5.8%** |
| **Recall** | 0.6541 | **0.7010** | **+0.0469** | **+7.2%** |
| **mAP@50** | 0.6968 | **0.7430** | **+0.0462** | **+6.6%** |
| **mAP@50-95** | 0.4037 | **0.4200** | **+0.0163** | **+4.0%** |
| **Hard Negative False Positive Rate** | **87.9%** (29/33 false detections) | **0.0%** (0/33 false detections) | **-87.9%** | **100% Fixed** |

### 4.2. Per-Class Test Performance (V2 Model)

| Disease Class | Test Images | Ground Truth Boxes | Precision (P) | Recall (R) | mAP@50 | mAP@50-95 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `Tomato___Bacterial_spot` | 48 | 395 | **0.714** | **0.691** | **0.700** | **0.361** |
| `Tomato___Early_blight` | 30 | 138 | **0.689** | **0.572** | **0.640** | **0.303** |
| `Tomato___Late_blight` | 51 | 251 | **0.799** | **0.841** | **0.890** | **0.595** |
| **All Classes Combined** | **162** | **784** | **0.734** | **0.701** | **0.743** | **0.420** |

---

## 5. False Positive & Real-World Case Evaluation

### 5.1. Hard Negative Benchmark
- **Test set:** 33 healthy tomato leaf images with bright, dark, shadowed, and blurred background regions.
- **Baseline Model:** Falsely triggered 29 bounding boxes (primarily misidentifying dark background borders and leaf edges as `Early_blight`).
- **V2 Model:** Produced **0 false positive bounding boxes** across all 33 images.

### 5.2. Real-World Prediction Visualizations
Sample prediction outputs saved in `training/runs/tomato_v2/predictions/`:

1. `pred_00_ext_heal...jpg`: Healthy Leaf (Bright Background) -> **Clean (0 detections)**.
2. `pred_01_ext_heal...jpg`: Healthy Leaf (Shadowed Background) -> **Clean (0 detections)**.
3. `pred_02_ext_heal...jpg`: Healthy Leaf (Blurred Foliage Background) -> **Clean (0 detections)**.
4. `pred_03_base_Tomato_Bacterial_spo...jpg`: Bacterial Spot -> **23 spot lesions detected** (Conf: `0.84 - 0.26`).
5. `pred_04_base_Tomato_Early_blight...jpg`: Early Blight -> **7 concentric lesions detected** (Conf: `0.84 - 0.45`).
6. `pred_05_base_Tomato_Late_blight...jpg`: Late Blight -> **Water-soaked lesion detected** (Conf: `0.91`).
7. `pred_06_hard_neg...jpg`: Hard Negative Complex Background -> **Clean (0 detections)**.
8. `pred_07_hard_neg...jpg`: Hard Negative Soil / Stem Texture -> **Clean (0 detections)**.

---

## 6. Model Artifacts & Deployment

The trained model artifacts are exported to:
- **Weights:** `model/tomato_v2/best.pt` (6.2 MB)
- **Class Mappings:** `model/tomato_v2/classes.json`
- **Model Metadata:** `model/tomato_v2/metadata.json`

The baseline model at `model/tomato/best.pt` remains untouched and preserved for regression testing and benchmarking.

---

## 7. Reproduction Commands

To reproduce the dataset preparation and training from scratch:

```powershell
# 1. Inspect Raw Extra Dataset
python training/scripts/inspect_tomato_extra.py

# 2. Prepare Dataset V2 (Stratified Splits, Empty Labels for Healthy)
python training/scripts/prepare_tomato_v2_dataset.py

# 3. Train & Evaluate YOLOv8n V2 Model
python training/scripts/train_tomato_v2.py --epochs 25 --batch 32 --imgsz 384 --patience 8
```

---

## 8. Limitations & Recommendations for Next Steps

1. **Early Blight Recall:** Early blight recall reached 57.2% on test images with small, early-stage spots. Future iterations could incorporate mosaic-free fine-tuning on high-resolution crops of faint early blight lesions.
2. **Backend / Frontend Integration:** When ready, the FastAPI backend in `app/services/detection.py` and `app/main.py` can be pointed to `model/tomato_v2/best.pt` to activate the improved model in production.
