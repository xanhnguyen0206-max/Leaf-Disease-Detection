# LEAF_AI: Tomato-Only Object Detection Dataset Report

## 1. Executive Summary & Overview
This report documents the preparation, annotation conversion, validation, and stratification of the **Tomato-Only Object Detection Dataset** for the **LEAF_AI** platform.

* **Source Dataset:** Roboflow Universe (`bacterial-3ofew/tomato-nwcjv`)
* **Task Type:** Object Detection (Bounding Boxes, YOLO format)
* **Target Specie:** Tomato (*Solanum lycopersicum*)
* **Total Images Processed:** 600
* **Total Valid Images:** 600
* **Corrupted Images:** 0
* **Duplicate Images:** 0
* **Total Converted Disease Bounding Boxes:** 3829
* **Data Splits:** Train (80%), Validation (10%), Test (10%) with Stratified Distribution

---

## 2. Target Classes & Filtering Strategy

| Class ID | Target Class Name | Original Raw ID | Raw Polygon Count | Processed Box Count | Action / Status |
|---|---|---|---|---|---|
| **0** | `Tomato___Bacterial_spot` | 0 | 2351 | 2351 | **Retained** (Disease Target) |
| **1** | `Tomato___Early_blight` | 1 | 1005 | 1005 | **Retained** (Disease Target) |
| **2** | `Tomato___Late_blight` | 2 | 473 | 473 | **Retained** (Disease Target) |
| *N/A* | `leaf` | 3 | 601 | 0 | **Excluded** (Healthy Leaf Mask) |

### Rationale for Excluding `leaf` Class:
1. **Disease Detection Specificity:** The objective of LEAF_AI's disease detection model is to locate and classify active disease lesions and symptoms on tomato foliage.
2. **Foreground vs. Background Ambiguity:** The `leaf` class in the raw dataset marks the entire leaf boundaries. Retaining large bounding boxes for entire leaves alongside small disease spot bounding boxes leads to heavy spatial overlap and conflicting anchor assignments during YOLO training.
3. **Optimized Inference:** Excluding whole-leaf bounding boxes focuses the model's loss gradient strictly on pathological lesion features (spots, concentric rings, water-soaked blights).

---

## 3. Segmentation to Bounding Box Conversion

The raw annotations were provided in **YOLOv8 Instance Segmentation** polygon format ($x_1, y_1, x_2, y_2, \dots, x_n, y_n$). Each polygon was converted to a standard normalized YOLO Object Detection bounding box using the minimum enclosing bounding rectangle:


$$\begin{aligned}
x_{min} &= \min_i(x_i), \quad x_{max} = \max_i(x_i) \\
y_{min} &= \min_i(y_i), \quad y_{max} = \max_i(y_i) \\
x_{center} &= \frac{x_{min} + x_{max}}{2} \\
y_{center} &= \frac{y_{min} + y_{max}}{2} \\
\text{width} &= x_{max} - x_{min} \\
\text{height} &= y_{max} - y_{min}
\end{aligned}$$


Each coordinate is clamped to $[0.0, 1.0]$ and rounded to 6 decimal precision.

---

## 4. Dataset Validation & Quality Audit Results

| Quality Check | Result / Count | Details |
|---|---|---|
| **Missing Label Files** | 0 | 100% of images have corresponding label files. |
| **Corrupted Images** | 0 | All images passed PIL and OpenCV image verification. |
| **Duplicate Images (MD5 Hash)** | 0 | No identical image checksums detected. |
| **Invalid / Degenerate Bounding Boxes** | 0 | All converted boxes have $w > 0$, $h > 0$, and valid $[0, 1]$ coordinates. |
| **Image Resolution Uniformity** | 640x640, 512x512, 256x256 | All images are standardized in resolution. |
| **Pure Background / Leaf-Only Images** | 0 | Images without disease spots serve as true negative background samples. |
| **Multi-Disease Images** | 0 | Images exhibiting multiple distinct disease classes simultaneously. |

---

## 5. Dataset Stratification & Split Statistics

The dataset was partitioned using stratified sampling across the primary disease classes to maintain consistent class proportions:

| Split | Images | % of Total | Bacterial Spot Boxes | Early Blight Boxes | Late Blight Boxes | Total Bounding Boxes |
|---|---|---|---|---|---|---|
| **Train** | 480 | 80.0% | 1875 | 797 | 383 | 3055 |
| **Val** | 60 | 10.0% | 283 | 124 | 49 | 456 |
| **Test** | 60 | 10.0% | 193 | 84 | 41 | 318 |
| **Total** | **600** | **100%** | **2351** | **1005** | **473** | **3829** |

---

## 6. Directory Layout

The prepared dataset is organized in YOLO detection format at `training/datasets/processed/tomato/`:

```
training/datasets/processed/tomato/
├── data.yaml
├── images/
│   ├── train/  (480 images)
│   ├── val/    (60 images)
│   └── test/   (60 images)
├── labels/
│   ├── train/  (480 txt label files)
│   ├── val/    (60 txt label files)
│   └── test/   (60 txt label files)
└── samples/
    ├── dataset_visualization_grid.jpg
    └── sample_*.jpg
```

### YOLO `data.yaml` Configuration
```yaml
path: c:/Users/Admin/Leaf-Disease-Detection/training/datasets/processed/tomato
train: images/train
val: images/val
test: images/test
nc: 3
names:
  - Tomato___Bacterial_spot
  - Tomato___Early_blight
  - Tomato___Late_blight
```

---

## 7. Sample Visualizations

Converted bounding boxes were verified on test split images. Each disease class is highlighted with distinct bounding box colors:
* 🔴 **Red:** `Tomato___Bacterial_spot`
* 🟠 **Orange:** `Tomato___Early_blight`
* 🟣 **Purple:** `Tomato___Late_blight`

*Visualization Grid:* `training/docs/dataset_visualization_grid.jpg` / `training/datasets/processed/tomato/samples/dataset_visualization_grid.jpg`

---

## 8. Next Steps & Recommendations
1. **Model Architecture Selection:** Benchmark YOLOv8n / YOLOv8s / YOLO11n for mobile/edge inference vs. YOLOv8m for server-side accuracy.
2. **Data Augmentation:** Apply Mosaic (0.5), HSV hue-saturation jitter, random flip, and slight rotation during training to enhance robustness to outdoor lighting.
3. **Evaluation Protocol:** Evaluate on the independent `test/` split with mAP@50 and mAP@50-95 metrics.
