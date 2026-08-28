# LEAF_AI Tomato YOLOv8n V3 Backend Integration Report

**Date:** August 27, 2026  
**System:** LEAF_AI Plant Leaf Disease Detection Platform  
**Integration Scope:** YOLOv8n V3 Model (640x640 Resolution) Production Backend Deployment  
**Status:** **SUCCESSFUL (100% Tests & Benchmark Inferences Passed)**

---

## 1. Overview of Integrated Model

| Property | Value / Specification |
| :--- | :--- |
| **Model Version** | YOLOv8n V3 (High-Resolution Bacterial Spot Optimized) |
| **Active Model Path** | `model/tomato_v3/best.pt` |
| **Metadata File** | `model/tomato_v3/metadata.json` |
| **Classes File** | `model/tomato_v3/classes.json` |
| **Input Resolution** | **640x640** (Ultralytics Auto-Letterbox) |
| **Class Mapping** | `0`: `Tomato___Bacterial_spot`<br>`1`: `Tomato___Early_blight`<br>`2`: `Tomato___Late_blight` |
| **Backup Model** | `model/tomato_v2/best.pt` (Preserved 100% untouched) |
| **Benchmark Test Performance** | **0.768 mAP@50** (vs 0.743 in V2), **80.8% Bacterial Spot Detection** |

---

## 2. Files Changed & Architectural Updates

| File Modified / Created | Action | Purpose & Description |
| :--- | :---: | :--- |
| [`backend/app/core/config.py`](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/core/config.py) | **[MODIFY]** | Updated default `MODEL_PATH` to `model/tomato_v3/best.pt`, added `MODEL_VERSION` (`v3`/`v2`) and `MODEL_IMG_SIZE` (`640`) environment variable support without hard-coded local paths. |
| [`backend/app/services/yolo_model_service.py`](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/yolo_model_service.py) | **[MODIFY]** | Loads V3 model once into memory as a singleton, parses `classes.json` metadata, supports `imgsz=640`, adds `postprocess_detections()` hook, and determines primary disease. |
| [`backend/app/services/prediction_service.py`](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/prediction_service.py) | **[MODIFY]** | Implemented safe no-detection handling with helpful agricultural recommendations, preventing absolute claims of "Healthy". Preserves database diagnosis history. |
| [`backend/tests/test_yolo_service.py`](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/tests/test_yolo_service.py) | **[MODIFY]** | Added tests for 640x640 loading, 3-class metadata verification, real test images (Bacterial Spot, Early Blight, Late Blight), post-processing box filtering, and model switching (V3, V2, Mock). |
| [`backend/tests/test_api.py`](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/tests/test_api.py) | **[MODIFY]** | Full API test coverage across 14 scenarios including upload validation, error responses, query params, history persistence, and deletion. |
| [`training/scripts/test_v3_integration_api.py`](file:///c:/Users/Admin/Leaf-Disease-Detection/training/scripts/test_v3_integration_api.py) | **[NEW]** | Automated real-image API benchmark script across test split images and hard negatives. |
| [`docs/v3_backend_integration_test.md`](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/v3_backend_integration_test.md) | **[NEW]** | Detailed per-image inference results table (Image, Expected, Predicted, Confidence, Boxes, Result). |
| [`README.md`](file:///c:/Users/Admin/Leaf-Disease-Detection/README.md) | **[MODIFY]** | Updated production model description, active paths, and environment variable switching instructions. |
| [`backend/README.md`](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/README.md) | **[MODIFY]** | Updated backend documentation with V3 model details, Swagger URL, and uvicorn startup instructions. |
| [`docs/model_integration.md`](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/model_integration.md) | **[MODIFY]** | Updated integration guide for V3 specification and operational guidelines. |

---

## 3. Automated Test Suite Results (Pytest)

Command executed:
```bash
python -m pytest backend/tests -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Leaf-Disease-Detection\backend
configfile: pytest.ini

backend\tests\test_api.py::test_health_endpoint PASSED                   [  4%]
backend\tests\test_api.py::test_diseases_endpoint PASSED                 [  8%]
backend\tests\test_api.py::test_disease_detail_endpoint PASSED           [ 12%]
backend\tests\test_api.py::test_care_recommendations_endpoint PASSED     [ 16%]
backend\tests\test_api.py::test_history_endpoint PASSED                  [ 20%]
backend\tests\test_api.py::test_predict_bacterial_spot_real_image PASSED [ 25%]
backend\tests\test_api.py::test_predict_early_blight_real_image PASSED   [ 29%]
backend\tests\test_api.py::test_predict_late_blight_real_image PASSED    [ 33%]
backend\tests\test_api.py::test_predict_healthy_leaf PASSED              [ 37%]
backend\tests\test_api.py::test_predict_empty_upload PASSED              [ 41%]
backend\tests\test_api.py::test_predict_invalid_image_data PASSED        [ 45%]
backend\tests\test_api.py::test_predict_unsupported_extension PASSED     [ 50%]
backend\tests\test_api.py::test_predict_confidence_param PASSED          [ 54%]
backend\tests\test_api.py::test_multiple_detections_and_bbox_structure PASSED [ 58%]
backend\tests\test_api.py::test_history_persistence_and_delete PASSED    [ 62%]
backend\tests\test_yolo_service.py::test_v3_model_loading_success PASSED [ 66%]
backend\tests\test_yolo_service.py::test_model_loading_missing_file PASSED [ 70%]
backend\tests\test_yolo_service.py::test_v3_inference_bacterial_spot PASSED [ 75%]
backend\tests\test_yolo_service.py::test_v3_inference_early_blight PASSED [ 79%]
backend\tests\test_yolo_service.py::test_v3_inference_late_blight PASSED [ 83%]
backend\tests\test_yolo_service.py::test_v3_confidence_threshold PASSED  [ 87%]
backend\tests\test_yolo_service.py::test_v3_no_detection_on_blank_image PASSED [ 91%]
backend\tests\test_yolo_service.py::test_postprocess_detections_filters_invalid_boxes PASSED [ 95%]
backend\tests\test_yolo_service.py::test_model_version_switching_v3_v2_mock PASSED [100%]

====================== 24 passed in 37.31s =======================
```

- **Total Tests:** 24
- **Passed:** 24 (100%)
- **Failed:** 0

---

## 4. Real Image Inference Benchmark Results

Script executed:
```bash
python training/scripts/test_v3_integration_api.py
```

Summary from [`docs/v3_backend_integration_test.md`](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/v3_backend_integration_test.md):

| Test Category | Images Tested | Expected Class | Accuracy | Bounding Boxes Detected |
| :--- | :---: | :--- | :---: | :--- |
| **Bacterial Spot (Đốm vi khuẩn)** | 4 | `Tomato___Bacterial_spot` | **100%** | Up to 23 precise boxes per image |
| **Early Blight (Úa sớm)** | 3 | `Tomato___Early_blight` | **100%** | 9 - 11 bounding boxes per image |
| **Late Blight (Sương mai)** | 3 | `Tomato___Late_blight` | **100%** | 2 - 6 bounding boxes per image |
| **Healthy Foliage (Lá khỏe)** | 3 | `Healthy` / `no_detection` | **100%** | 0 false alarm boxes |
| **Hard Negatives (Nền phức tạp)** | 3 | `no_detection` | **100%** | 0 false alarm boxes |

---

## 5. Frontend Compatibility Verification

- **API Contract:** Maintained 100% identical JSON schema matching [`backend/app/schemas/diagnosis.py`](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/schemas/diagnosis.py) and [`frontend/src/types/index.ts`](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/types/index.ts).
- **Bounding Boxes Rendering:** Normalized coordinates scale correctly on the frontend Canvas/Image overlay.
- **Frontend Changes Required:** **NO (Không cần sửa frontend)**. The existing UI and API client in `frontend/src/services/api.ts` and `frontend/src/pages/DiagnosePage.tsx` work seamlessly.

---

## 6. How to Run & Test

### Starting the Production Backend:
```bash
cd c:\Users\Admin\Leaf-Disease-Detection\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Accessing Swagger UI:
- **Swagger Documentation:** http://127.0.0.1:8000/docs
- **ReDoc Documentation:** http://127.0.0.1:8000/redoc

### Running Automated Verification:
```bash
python -m pytest backend/tests -v
python training/scripts/test_v3_integration_api.py
```
