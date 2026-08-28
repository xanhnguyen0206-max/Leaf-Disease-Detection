# Deep Audit Report: Bacterial Spot Detection Performance — LEAF_AI Tomato YOLO V2

**Audit Target:** LEAF_AI Tomato Disease Detection Model V2 (`model/tomato_v2/best.pt`)  
**Scope:** In-depth diagnosis of Bacterial Spot (*Tomato___Bacterial_spot*) detection bottlenecks, lesion morphology, dataset distribution, annotation consistency, resolution impact, and error taxonomy.  
**Mode:** Analysis-Only (No dataset modifications, no model training).  
**Date:** August 26, 2026  

---

## 1. Executive Summary

While the **Tomato YOLO V2 model** achieved a **100% elimination of background false positives** on healthy leaves (0.0% FP rate vs. 87.9% baseline) and increased overall test mAP@50 to **0.7430**, **Bacterial Spot** remains the most challenging class (mAP@50-95 of **0.361** vs. 0.595 for Late Blight).

This empirical audit conducted on the complete dataset (1,614 images, 7,611 bounding boxes) and test evaluation set (162 images, 395 ground-truth Bacterial Spot boxes) reveals three primary underlying causes:

1. **Extreme Lesion Miniaturization:** **78.0%** of all Bacterial Spot bounding boxes are categorized as *Very Small* ($< 0.5\%$ of image area). The median Bacterial Spot lesion occupies only a **15.4px $\times$ 15.4px** square at 384x384 resolution (with the 10th percentile at just **8.3px $\times$ 8.3px**), which pushes the limits of standard P3/P4 stride feature pyramids on YOLOv8n.
2. **Sub-threshold Confidence Suppression:** **21.2%** of ground-truth Bacterial Spot lesions are missed not due to misclassification, but because their detection confidence falls below the 0.25 threshold (**40.5%** of all raw candidate Bacterial Spot proposals score $< 0.25$).
3. **Annotation Inconsistency:** **9.07%** of Bacterial Spot annotations in the dataset exhibit severe style contradictions between granular spot-level labeling ($< 10\text{px}$) and whole-cluster / leaf-level groupings ($> 200\text{px}$).

---

## 2. Current Performance Benchmark

Evaluated on the completely unseen test split (162 images, 784 total disease boxes):

| Disease Class | Ground Truth Boxes | Precision (P) | Recall (R) | mAP@50 | mAP@50-95 | Relative Bottleneck |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Tomato___Bacterial_spot** | **395** | **0.714** | **0.691** | **0.700** | **0.361** | **Lowest localization tightness (mAP50-95: 0.361)** |
| **Tomato___Early_blight** | 138 | 0.689 | 0.572 | 0.640 | 0.303 | Lower recall on faint early-stage rings |
| **Tomato___Late_blight** | 251 | 0.799 | 0.841 | 0.890 | 0.595 | High accuracy on large necrotic lesions |
| **All Classes Combined** | **784** | **0.734** | **0.701** | **0.743** | **0.420** | Healthy FP Rate = **0.0%** |

---

## 3. Dataset Distribution & Morphological Breakdown

Comparative dataset distribution across the entire Dataset V2:

| Metric | Bacterial Spot (Class 0) | Early Blight (Class 1) | Late Blight (Class 2) | Comparison & Finding |
| :--- | :---: | :---: | :---: | :--- |
| **Total Images Containing Disease** | 481 | 300 | 510 | Bacterial Spot has ample image coverage (29.8% of dataset) |
| **Total Bounding Boxes** | **3,727** | 1,621 | 2,263 | Bacterial Spot has **49.0%** of all disease annotations in V2 |
| **Average Boxes per Image** | **7.75 boxes/img** | 5.40 boxes/img | 4.44 boxes/img | Highest box density (clusters of scattered speckles) |
| **Median Relative Area ($w \times h$)** | **0.001608 (0.16%)** | 0.006461 (0.65%) | 0.013396 (1.34%) | **Bacterial Spot lesions are 4x smaller than EB and 8.3x smaller than LB** |
| **Mean Relative Area** | **0.010616** | 0.021618 | 0.035636 | Skewed by occasional large cluster annotations |
| **10th Percentile Area (P10)** | **0.000463** | 0.001011 | 0.002480 | P10 represents microscopic 8px lesions |
| **25th Percentile Area (P25)** | **0.000802** | 0.002134 | 0.005624 | Over 25% of boxes are $< 11\text{px}$ |
| **75th Percentile Area (P75)** | **0.004217** | 0.020679 | 0.033291 | 75% of Bacterial Spot boxes are smaller than median Early Blight |
| **90th Percentile Area (P90)** | **0.016068** | 0.053245 | 0.072923 | Only 10% exceed 0.016 relative area |

### Bounding Box Size Categorization
- **Very Small ($< 0.5\%$ of image area):** **78.0%** (2,907 boxes)
- **Small ($0.5\% - 2.0\%$ of image area):** **13.8%** (514 boxes)
- **Medium ($2.0\% - 8.0\%$ of image area):** **5.0%** (186 boxes)
- **Large ($> 8.0\%$ of image area):** **3.2%** (120 boxes)

---

## 4. Test Set Error Taxonomy (395 Bacterial Spot GT Boxes)

Running inference on all 162 test images with ground-truth matching ($\text{IoU} \ge 0.30, \text{Conf} \ge 0.25$):

| Bacterial Spot Outcome / Error Type | Box Count | Percentage of GT | Diagnostic Interpretation |
| :--- | :---: | :---: | :--- |
| **Correctly Detected** ($\text{IoU} \ge 0.30, \text{Conf} \ge 0.25$) | **293** | **74.18%** | Solid baseline detection on clear, isolated lesions. |
| **Missed / False Negative** ($\text{IoU} < 0.30$ or $\text{Conf} < 0.25$) | **84** | **21.27%** | Tiny spots below resolution limit or confidence threshold. |
| **Poor Localization** ($0.10 \le \text{IoU} < 0.30$) | **19** | **4.81%** | Offset center points on irregular cluster boundaries. |
| **Confused as Early Blight** (Class 0 GT $\rightarrow$ Class 1 Pred) | **0** | **0.00%** | When bboxes match, class discrimination is 100% correct. |
| **Confused as Late Blight** (Class 0 GT $\rightarrow$ Class 2 Pred) | **0** | **0.00%** | Zero cross-class bleed onto Late Blight. |
| **Low Confidence Detections** ($0.25 \le \text{Conf} < 0.40$) | **110** | **27.85%** | Over 1/4 of valid detections hover near the decision boundary. |

---

## 5. Investigation of Bacterial Spot vs. Early Blight Confusion

A crucial real-world question was whether the model confuses Bacterial Spot with Early Blight:

### Key Findings
1. **At the Individual Bounding Box Level:** Ground-truth Bacterial Spot lesions are **never predicted as Early Blight** (0/395 bounding box cross-predictions on test data). When a bounding box is generated for a spot lesion, YOLOv8n classifies it as Bacterial Spot with high accuracy.
2. **At the Whole-Image Diagnostic Level:** When an image contains multiple tiny bacterial spots, if the model fails to detect the faint spots due to the 0.25 threshold or sub-pixel downsampling, a secondary pattern on the leaf (such as a slight brown tip or edge) can be picked up as a low-confidence Early Blight lesion, changing the primary diagnosis.
3. **Morphological Distinction:**
   - **Bacterial Spot:** Small, water-soaked dark brown/black angular specks (median 15px), often surrounded by a faint yellow halo, distributed densely across leaflets.
   - **Early Blight:** Larger brown concentric target-like rings (median 31px), typically originating on older lower leaves with wider chlorotic margins.

---

## 6. Annotation Quality & Inconsistency Analysis

A comprehensive audit of all 3,727 Bacterial Spot annotations identified **338 inconsistent / anomalous labels (9.07%)**:

### Types of Identified Labeling Anomalies
1. **Huge Cluster Grouping vs. Individual Spot Discrepancy:**
   - In several baseline files (e.g., `train/base_Tomato_Bacterial_spot00001...:L3`, `train/base_Tomato_Bacterial_spot00004...:L11`, `train/base_Tomato_Bacterial_spot00012...:L3`), annotators created massive boxes ($w > 0.40, h > 0.50$, area $> 20\%$) covering entire branches and dozens of spots at once.
   - In contrast, in files like `train/base_Tomato_Bacterial_spot00016...` and `ext_bact_...`, individual spots of size $w=0.017, h=0.014$ were annotated individually.
   - **Impact on Model:** The object detector's DFL (Distribution Focal Loss) is severely penalized when predicting individual spots if the ground truth demands a single gigantic box enclosing healthy leaf tissue between spots.
2. **Microscopic Sub-Pixel Boxes ($< 0.04\%$ Area):**
   - 42 annotations have areas smaller than 0.0004 ($< 6\text{px} \times 6\text{px}$). At standard CNN strides, these labels provide almost zero gradient signal.

---

## 7. Image Resolution Analysis: 384x384 vs. 640x640

| Metric | Current Training (384x384) | Standard High-Res (640x640) | Resolution Impact Ratio |
| :--- | :---: | :---: | :---: |
| **Total Pixels per Image** | 147,456 px | 409,600 px | **2.78x pixel density** |
| **Median Bacterial Spot Dimensions** | **15.4 px $\times$ 15.4 px** (237 px²) | **25.7 px $\times$ 25.7 px** (660 px²) | **+178% pixel area** |
| **P10 Bacterial Spot Dimensions** | **8.3 px $\times$ 8.3 px** (68 px²) | **13.8 px $\times$ 13.8 px** (190 px²) | **+179% pixel area** |
| **P3 Layer Receptive Stride (Stride 8)** | Lesion spans **~1.9 grid cells** | Lesion spans **~3.2 grid cells** | Drastically improved anchor/feature alignment |
| **P4 Layer Receptive Stride (Stride 16)** | Lesion spans **< 1.0 grid cell (lost)** | Lesion spans **1.6 grid cells (captured)** | Prevents complete loss of small speckles |

### Conclusion on Resolution
At **384x384**, the smallest 25% of Bacterial Spot lesions occupy less than $11\text{px} \times 11\text{px}$, falling below the effective feature resolution of YOLOv8's deeper stages. Training at **640x640** would provide a **2.78x increase in feature pixels**, directly resolving the primary physical bottleneck for small spot localization.

---

## 8. Prediction Confidence Distribution

Analysis of all candidate Bacterial Spot predictions on test images:

- **Below 0.25 ($< 0.25$):** **40.5%** (305 proposals) — Faint / small spots suppressed by default threshold.
- **0.25 to 0.40:** **17.5%** (132 proposals) — Valid detections near threshold boundary.
- **0.40 to 0.50:** **9.4%** (71 proposals) — Medium confidence detections.
- **0.50 to 0.70:** **17.8%** (134 proposals) — Solid high-confidence detections.
- **Above 0.70 ($> 0.70$):** **14.7%** (111 proposals) — High confidence detections.
- **Mean Confidence of Correct Detections:** **0.6037**

*Note on Threshold Adjustment:* Lowering `MODEL_CONFIDENCE_THRESHOLD` from 0.25 to 0.20 would increase Bacterial Spot recall from 69.1% to ~74%, but could risk introducing minor false detections on borderline textures. The true solution is improving feature resolution and label consistency.

---

## 9. Root-Cause Ranking

| Impact Level | Root Cause Factor | Evidence & Justification |
| :---: | :--- | :--- |
| **HIGH IMPACT** | **1. Tiny Lesion Size vs. 384x384 Input Size** | **78.0% of boxes are $< 0.5\%$ area** (median 15.4px). The smallest 25% fall below 11px, exceeding YOLOv8n P3/P4 stride Nyquist resolution. |
| **HIGH IMPACT** | **2. Annotation Style Inconsistency** | **9.07% of annotations conflict** between granular single-spot boxes and gigantic multi-lesion cluster boxes ($> 20\%$ leaf area). |
| **MEDIUM IMPACT** | **3. Sub-threshold Confidence Attenuation** | 40.5% of raw network proposals score $< 0.25$ due to faint lesion contrast in shadow/leaf veins. |
| **MEDIUM IMPACT** | **4. YOLOv8n (Nano) Backbone Capacity** | Lightweight 3.0M parameter backbone has limited capacity for multi-scale feature representation compared to YOLOv8s. |
| **LOW IMPACT** | **5. Class Imbalance** | Bacterial Spot already represents **49.0% of all bounding boxes** (3,727 boxes) and 481 images in V2; raw data quantity is not the bottleneck. |

---

## 10. Recommended Next Experiment

### **SINGLE Primary Recommendation: Train YOLOv8n at 640x640 with Standardized Small-Object Anchor Loss**

### Why this is the highest-leverage experiment:
1. **Directly addresses the #1 root cause:** Increasing resolution from 384x384 to 640x640 expands lesion pixel area by **2.78x** (median lesion goes from 15.4px to 25.7px, P10 from 8.3px to 13.8px). This allows YOLOv8's P3 detection head to cleanly resolve individual bacterial spots without modifying model architecture.
2. **Zero manual re-annotation overhead required:** Leverages the existing validated Dataset V2 directly.

### Exact Experiment Specification:
- **Architecture:** YOLOv8n (`yolov8n.pt`)
- **Input Resolution:** `imgsz = 640`
- **Dataset:** Dataset V2 (`training/datasets/processed/tomato_v2/data.yaml`)
- **Batch Size:** 16 (or 8 for CPU RAM fitting)
- **Epochs:** 25 with early stopping `patience = 8`
- **Data Augmentation:** Maintain mosaic + mixup in first 15 epochs, close mosaic in final 10 epochs.
- **Success Criteria:**
  - Bacterial Spot **Recall $\ge 0.78$** (current: 0.691)
  - Bacterial Spot **mAP@50 $\ge 0.77$** (current: 0.700)
  - Bacterial Spot **mAP@50-95 $\ge 0.42$** (current: 0.361)
  - Healthy False Positive Rate maintained at **0.0%**
