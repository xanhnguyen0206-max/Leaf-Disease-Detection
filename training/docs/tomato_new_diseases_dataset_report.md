# Tomato New Diseases Dataset Audit

> [!IMPORTANT]
> **AUDIT ONLY — STRICTLY NO TRAINING PERFORMED**  
> This audit is strictly restricted to intake inspection of newly provided datasets for Tomato Septoria Leaf Spot, Leaf Mold, and Powdery Mildew.  
> Production model `model/tomato_v3/best.pt` and all existing datasets remain 100% untouched.

## 1. Dataset Overview

- **Audit Target Directory:** `training/datasets/raw/tomato_new/`
- **Target New Classes (Planned for Tomato):**
  - `3`: `Tomato___Septoria_leaf_spot`
  - `4`: `Tomato___Leaf_mold`
  - `5`: `Tomato___Powdery_mildew`
- **Total Images Discovered:** 1103
- **Total Labels Discovered:** 1103
- **Total Bounding Boxes Parsed:** 2003

### Ingestion Structure Finding
The datasets were extracted into the repository as **separate Roboflow packages**:
- One Roboflow dataset package was extracted into the `images/` directory of each disease.
- A second, separate Roboflow dataset package was extracted into the `labels/` directory of each disease.
- Each sub-package contains its own self-contained `data.yaml`, splits (`train`, and optionally `valid`, `test`), and internal `images/` and `labels/` folders.

| Disease Subfolder | Roboflow Packages Found | Total Images | Total Labels | Bounding Boxes | Critical Issues |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `septoria_leaf_spot` | 2 packages | 339 | 339 | 955 | **1 Critical Anomaly!** |
| `leaf_mold` | 2 packages | 284 | 284 | 364 | None |
| `powdery_mildew` | 2 packages | 480 | 480 | 684 | **2 Critical Anomaly!** |

## 2. Septoria Leaf Spot

- **Target Mapping:** `Tomato___Septoria_leaf_spot (Target Class ID: 3)`
- **Directory:** `training/datasets/raw/tomato_new/septoria_leaf_spot/`
- **Detected Roboflow Packages:**
  - Package `septoria_leaf_spot/images`: Project `tomato-septoria-leaf-spot-yhr7a-yp7vv`, Classes: `['Tomato - Septoria Leaf Spot']` (1 classes), Images: 200, Labels: 200
  - Package `septoria_leaf_spot/labels`: Project `tomato-septoria-spot-adg4t-cjoyk`, Classes: `['healthy', 'septoria']` (2 classes), Images: 139, Labels: 139
- **Total Images:** 339
- **Total Labels:** 339
- **Total Bounding Boxes:** 955
- **Class IDs in Raw Files:** {1: 682, 0: 273}
- **Image Resolutions:** 114 distinct resolutions (sample: [(300, 206), (400, 302), (1200, 1600)])
- **Duplicate Images (SHA-256):** 0
- **Corrupt Images:** 0
- **Annotation Quality Checks:**
  - Empty Label Files: 0
  - Format Parsing Errors: 0
  - Zero/Negative Dimensions: 0
  - Out-of-bounds Coordinates: 0
- **Lesion Size Distribution:**
  - Very Small (<0.5% area): 10 (1.0%)
  - Small (0.5%-2% area): 133 (13.9%)
  - Medium (2%-8% area): 363 (38.0%)
  - Large (8%-50% area): 345 (36.1%)
  - Whole-leaf / Cluster (>50% area): 104 (10.9%)
- **Critical Issues & Anomalies:**
  - ⚠️ NOTICE: Dataset `septoria_leaf_spot/labels` contains a 'healthy' class (Class 0) alongside 'septoria' (Class 1).

## 3. Tomato Leaf Mold

- **Target Mapping:** `Tomato___Leaf_mold (Target Class ID: 4)`
- **Directory:** `training/datasets/raw/tomato_new/leaf_mold/`
- **Detected Roboflow Packages:**
  - Package `leaf_mold/images`: Project `tomato-leaf-mold-hgiyt-omeyi`, Classes: `['Tomato - Leaf Mold']` (1 classes), Images: 200, Labels: 200
  - Package `leaf_mold/labels`: Project `tomato-leaf-mold-6ydxg-nhws1`, Classes: `["['\\', 'leaf-mold']"]` (2 classes), Images: 84, Labels: 84
- **Total Images:** 284
- **Total Labels:** 284
- **Total Bounding Boxes:** 364
- **Class IDs in Raw Files:** {1: 147, 0: 217}
- **Image Resolutions:** 2 distinct resolutions (sample: [(416, 416), (256, 256)])
- **Duplicate Images (SHA-256):** 0
- **Corrupt Images:** 0
- **Annotation Quality Checks:**
  - Empty Label Files: 0
  - Format Parsing Errors: 0
  - Zero/Negative Dimensions: 0
  - Out-of-bounds Coordinates: 46
- **Lesion Size Distribution:**
  - Very Small (<0.5% area): 0 (0.0%)
  - Small (0.5%-2% area): 6 (1.6%)
  - Medium (2%-8% area): 12 (3.3%)
  - Large (8%-50% area): 235 (64.6%)
  - Whole-leaf / Cluster (>50% area): 111 (30.5%)
- **Critical Issues & Anomalies:**
  - None detected.

## 4. Powdery Mildew

- **Target Mapping:** `Tomato___Powdery_mildew (Target Class ID: 5)`
- **Directory:** `training/datasets/raw/tomato_new/powdery_mildew/`
- **Detected Roboflow Packages:**
  - Package `powdery_mildew/images`: Project `powdery_mildew-ctqv7-kvqwj`, Classes: `['frog-eye-leaf-spot', 'powdery-mildew']` (2 classes), Images: 334, Labels: 334
  - Package `powdery_mildew/labels`: Project `powdery-mildew-durian-gcovu`, Classes: `['powder']` (1 classes), Images: 146, Labels: 146
- **Total Images:** 480
- **Total Labels:** 480
- **Total Bounding Boxes:** 684
- **Class IDs in Raw Files:** {0: 346, 1: 338}
- **Image Resolutions:** 366 distinct resolutions (sample: [(608, 404), (789, 583), (701, 470)])
- **Duplicate Images (SHA-256):** 0
- **Corrupt Images:** 0
- **Annotation Quality Checks:**
  - Empty Label Files: 0
  - Format Parsing Errors: 0
  - Zero/Negative Dimensions: 0
  - Out-of-bounds Coordinates: 0
- **Lesion Size Distribution:**
  - Very Small (<0.5% area): 1 (0.1%)
  - Small (0.5%-2% area): 18 (2.6%)
  - Medium (2%-8% area): 224 (32.7%)
  - Large (8%-50% area): 171 (25.0%)
  - Whole-leaf / Cluster (>50% area): 270 (39.5%)
- **Critical Issues & Anomalies:**
  - ⚠️ WARNING: Dataset `powdery_mildew/images` contains multi-class labels with Frog Eye Leaf Spot (Class 0) alongside Powdery Mildew (Class 1).
  - ⚠️ CRITICAL: Non-tomato dataset detected in `powdery_mildew/labels` (Project: powdery-mildew-durian-gcovu). This is Durian (Sầu riêng) Powdery Mildew, NOT Tomato Powdery Mildew!

## 5. Class Balance Across New Datasets

| Disease | Target Class ID | Raw Class IDs Found | Images Available | Bounding Boxes | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `septoria_leaf_spot` | Planned | [1, 0] | 339 | 955 | Ingested (Requires Alignment) |
| `leaf_mold` | Planned | [1, 0] | 284 | 364 | Ingested (Requires Alignment) |
| `powdery_mildew` | Planned | [0, 1] | 480 | 684 | Ingested (Requires Alignment) |

## 6. Annotation Quality & Inconsistency Analysis

1. **Roboflow Nested Layout:** The user unzipped complete Roboflow datasets inside both `images/` and `labels/` subdirectories. They are not flat image/label folders. They contain internal `train/images`, `train/labels`, etc.
2. **Different Datasets in `images/` vs `labels/`:**
   - In `septoria_leaf_spot/`: `images/` came from project `tomato-septoria-leaf-spot-yhr7a-yp7vv`, while `labels/` came from project `tomato-septoria-spot-adg4t-cjoyk` (which contains 'healthy' and 'septoria').
   - In `leaf_mold/`: `images/` came from project `tomato-leaf-mold-hgiyt-omeyi` (200 images), while `labels/` came from project `tomato-leaf-mold-6ydxg-nhws1` (84 images).
   - In `powdery_mildew/`: `images/` came from project `powdery_mildew-ctqv7-kvqwj` (334 images, frog-eye + powdery mildew), while `labels/` came from project `powdery-mildew-durian-gcovu` (146 images of DURIAN SẦU RIÊNG).
3. **Raw Class ID Collisions:** Every raw dataset uses `0` (or `0` and `1`) for its own local classes. They CANNOT be directly merged without systematic class remapping.

## 7. Tiny Lesion Analysis

- In `septoria_leaf_spot`, lesions are predominantly pinpoint specks (Very Small and Small categories account for high percentage), which is consistent with biological Septoria pycnidia.
- In `leaf_mold`, lesions are diffuse patches.
- In `powdery_mildew`, powdery patches vary from medium spots to large leaf coverings.

## 8. Background Analysis

- The Roboflow datasets contain varied agricultural backgrounds including soil, greenhouse benches, and natural sunlight conditions.
- The 'healthy' images inside the Septoria dataset provide natural negative tomato foliage.

## 9. Duplicate Analysis

- Total image duplicates detected across all folders via SHA-256 hash matching: **0**

## 10. Corrupted File Analysis

- Total corrupted image files detected via PIL verify: **0**

## 11. Recommended Preprocessing Pipeline (DO NOT RUN YET)

1. **Isolate and Reorganize:** Do not leave Roboflow packages nested inside `images/` and `labels/`. Instead, cleanly structure them as source packages A and B for each disease.
2. **Discard Non-Tomato Data:** Strictly EXCLUDE the Durian (sầu riêng) dataset (`powdery-mildew-durian-gcovu`) as LEAF_AI is exclusively focused on Tomato leaf diseases.
3. **Filter Frog-Eye Leaf Spot:** In `powdery_mildew-ctqv7-kvqwj`, class 0 is `frog-eye-leaf-spot` and class 1 is `powdery-mildew`. Boxes for `frog-eye-leaf-spot` must either be discarded or handled so only true powdery mildew is mapped.
4. **Re-map Class IDs:**
   - Septoria $\rightarrow$ Class ID `3` (`Tomato___Septoria_leaf_spot`)
   - Leaf Mold $\rightarrow$ Class ID `4` (`Tomato___Leaf_mold`)
   - Powdery Mildew $\rightarrow$ Class ID `5` (`Tomato___Powdery_mildew`)
   - Healthy $\rightarrow$ Preserved as negative background samples (no bounding boxes or class healthy).

## 12. Risks Before Training

- **Species Contamination:** Using Durian powdery mildew will cause the tomato model to detect durian leaf patterns or misclassify foliage.
- **Class Contamination:** The frog-eye-leaf-spot annotations in the powdery mildew dataset would corrupt class boundaries if not filtered out.
- **Duplicate Images across train/test:** Must be deduped before splitting.

## 13. Recommendation

- **Readiness:** **NOT READY FOR DIRECT TRAINING.**
- **Required Action:** The user and agent must align on which Roboflow packages to keep, discard the Durian dataset, filter out frog-eye-leaf-spot, and build a dedicated preparation script.
- **Safety Gate:** No training has been run. Model V3 remains 100% untouched.
