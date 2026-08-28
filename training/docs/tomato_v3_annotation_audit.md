# Tomato V3 Dataset & Annotation Quality Audit Report

**Dataset Root:** `training/datasets/processed/tomato_v3/`  
**Base Source:** `training/datasets/processed/tomato_v2/` (Unmodified V2 preserved for benchmark)  
**Target Class for Audit:** `Tomato___Bacterial_spot` (Class ID 0)  
**Date:** August 27, 2026  

---

## 1. Summary of Dataset Splits

| Split | Total Images | Images with Bacterial Spot | Bacterial Spot Boxes (V2) | Normalized Boxes (V3) | Early Blight Boxes | Late Blight Boxes | Safe Merges |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train** | 1291 | 385 | 2992 | 2992 | 1354 | 1793 | 4 |
| **Val** | 161 | 48 | 339 | 339 | 129 | 219 | 0 |
| **Test** | 162 | 48 | 396 | 396 *(Untouched)* | 138 | 251 | 0 (Strict Benchmark) |
| **Total** | **1,614** | **481** | **3727** | **3723** | **1,621** | **2,263** | **4** |

> [!NOTE]
> The **Test split is 100% identical to V2** without any label removal or modification, ensuring completely fair side-by-side benchmark evaluation.

---

## 2. Morphological Analysis of Bacterial Spot Annotations

- **Total Bacterial Spot Bounding Boxes Inspected:** 3727
- **10th Percentile Area ($P_{10}$):** 0.000463 (~13.8px square at 640x640 vs 8.3px at 384x384)
- **25th Percentile Area ($P_{25}$):** 0.000802 (~18.1px square at 640x640)
- **Median Area ($P_{50}$):** 0.001608 (~25.7px square at 640x640)
- **75th Percentile Area ($P_{75}$):** 0.004217
- **90th Percentile Area ($P_{90}$):** 0.016068
- **Mean Area:** 0.010616

### Size Distribution Breakdown

| Category | Area Definition | Box Count | Percentage | Detection Impact |
| :--- | :--- | :---: | :---: | :--- |
| **Microscopic** | $< 0.05\%$ ($< 0.0005$) | 441 | 11.83% | Near CNN resolution limit at 384x384; resolved at 640x640 |
| **Very Small** | $0.05\% - 0.5\%$ | 2467 | 66.19% | Primary target of 640x640 resolution scale |
| **Small** | $0.5\% - 2.0\%$ | 514 | 13.79% | Standard medium spots |
| **Medium** | $2.0\% - 8.0\%$ | 187 | 5.02% | Confluent necrotic spots |
| **Large / Cluster** | $8.0\% - 15.0\%$ | 65 | 1.74% | Moderate lesion clusters |
| **Giant Cluster** | $> 15.0\%$ | 53 | 1.42% | Whole-leaf grouping inconsistency |

---

## 3. Annotation Outliers & Normalization Decisions

1. **Safe Duplicate Merges:** 4 overlapping tiny bounding boxes (IoU > 0.85) were merged into tight single bounding boxes in the training/validation splits.
2. **Giant Cluster Annotations:** 53 boxes covering $>15\%$ image area were flagged. In accordance with safety rules, these were **NOT deleted**; instead, gentle multi-scale training and appropriate IoU matching are utilized to maintain recall.
3. **No Synthetic Labels:** Zero synthetic labels were introduced.

---

## 4. Conclusion & Readiness for V3 Training

The Dataset V3 is verified and ready for YOLOv8n 640x640 training at `training/datasets/processed/tomato_v3/data.yaml`.
