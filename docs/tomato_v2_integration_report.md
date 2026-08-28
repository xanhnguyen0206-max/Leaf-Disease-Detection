# LEAF_AI: Tomato Disease Model V2 Full-Stack Integration Report

**Date:** August 26, 2026  
**Status:** COMPLETE & VERIFIED — READY FOR MANUAL WEB TESTING  
**Default Model:** `model/tomato_v2/best.pt`  
**Preserved Baseline:** `model/tomato/best.pt`  

---

## 1. Files Modified & Added

| Component | File Path | Action | Description |
| :--- | :--- | :---: | :--- |
| **Backend Core** | `backend/app/core/config.py` | [MODIFY] | Switched default `MODEL_PATH` to `model/tomato_v2/best.pt` with env var override support. |
| **Backend API** | `backend/app/api/endpoints/health.py` | [MODIFY] | Enhanced `/api/health` to return model loading status, relative path, and confidence threshold. |
| **Integration Test** | `training/scripts/test_v2_integration_api.py` | [NEW] | Automated real-image API integration test with visual output saving. |
| **Model Artifacts** | `model/tomato_v2/best.pt` | [NEW] | Retrained YOLOv8n V2 weights (6.2 MB). |
| **Model Classes** | `model/tomato_v2/classes.json` | [NEW] | Target class mapping (0: Bacterial Spot, 1: Early Blight, 2: Late Blight). |
| **Model Metadata** | `model/tomato_v2/metadata.json` | [NEW] | Model training metrics, input size, and false-positive benchmarks. |
| **Documentation** | `README.md` | [MODIFY] | Updated with quickstart run commands and model switching documentation. |
| **Documentation** | `docs/model_integration.md` | [MODIFY] | Comprehensive integration guide with V2 specs. |
| **Documentation** | `docs/tomato_v2_integration_report.md` | [NEW] | This master integration report. |

---

## 2. Model & Target Class Mapping

- **Default Model Path:** `model/tomato_v2/best.pt`
- **Architecture:** YOLOv8n (PyTorch / Ultralytics)
- **Input Size:** 384x384 (supports native multi-scale inference)
- **Inference Device:** `cpu` (configurable via `MODEL_DEVICE`)
- **Default Confidence Threshold:** `0.25` (configurable via `MODEL_CONFIDENCE_THRESHOLD`)
- **Target Classes:**
  - `0`: `Tomato___Bacterial_spot` -> *Bệnh đốm vi khuẩn cà chua*
  - `1`: `Tomato___Early_blight` -> *Bệnh úa sớm cà chua*
  - `2`: `Tomato___Late_blight` -> *Bệnh sương mai cà chua*
- **Healthy Handling:** Produces `status: "no_detection"`, `primary_disease: "Healthy"`, `confidence: 0.0`, with curated preventative care recommendations.

---

## 3. Backend Automated Test Results (`pytest`)

Ran complete backend test suite:
```bash
python -m pytest backend/tests -v
```

**Result:** **17 PASSED, 0 FAILED** (40.89s execution time).

### Verified Test Cases
- `test_health_endpoint`: Passed (Returns 200 OK and model status)
- `test_diseases_endpoint`: Passed (Returns disease library)
- `test_disease_detail_endpoint`: Passed (Returns details for all 3 tomato diseases)
- `test_care_recommendations_endpoint`: Passed (Returns database care recommendations)
- `test_history_endpoint`: Passed (Retrieves diagnosis records)
- `test_predict_real_yolo_image`: Passed (Runs real YOLOv8n V2 inference and returns bounding boxes)
- `test_predict_empty_upload`: Passed (Rejects 0-byte upload with 400 Bad Request)
- `test_predict_invalid_image_data`: Passed (Rejects non-image byte content with 400 Bad Request)
- `test_predict_unsupported_extension`: Passed (Rejects unsupported file formats with 400 Bad Request)
- `test_predict_confidence_param`: Passed (Properly applies query param `conf_threshold`)
- `test_history_delete`: Passed (Deletes history items cleanly)
- `test_model_loading_success`: Passed (Loads model weights once into memory)
- `test_model_loading_missing_file`: Passed (Raises clear FileNotFoundError if weights missing)
- `test_yolo_inference_valid_image`: Passed (Validates bounding box structure)
- `test_yolo_confidence_threshold`: Passed (Verifies confidence threshold filtering)
- `test_yolo_no_detection_handling`: Passed (Handles blank image gracefully)
- `test_model_switching_mock_and_yolo`: Passed (Factory supports dynamic switching)

---

## 4. Frontend Build & Type Validation (`npm run build`)

Ran production build in `frontend/`:
```bash
cd frontend
npm run build
```

**Result:** **0 ERRORS, 0 WARNINGS** (Built in 7.34s, output in `dist/`).
- Verified TypeScript types align with backend schemas (`BoundingBox`, `DetectionItem`, `DiagnosisResult`).
- Verified Vite proxy routes `/api` and `/uploads` to `http://127.0.0.1:8000`.

---

## 5. Real-Image API Verification

Tested against real images from `training/datasets/processed/tomato_v2/images/test/` and `hard_negatives/`:

| Test Image Case | Expected Ground Truth | Actual API Prediction | Confidence | Detections Count | Status | Result |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Healthy Tomato Leaf** | Healthy / Negative | `Healthy` | `0.00` | 0 | `no_detection` | **PASS** |
| **Bacterial Spot** | Bacterial Spot | `Tomato___Bacterial_spot` | `0.84` | 23 spots | `detected` | **PASS** |
| **Early Blight** | Early Blight | `Tomato___Early_blight` | `0.84` | 7 lesions | `detected` | **PASS** |
| **Late Blight** | Late Blight | `Tomato___Late_blight` | `0.91` | 2 lesions | `detected` | **PASS** |
| **Hard Negative (Shadows)** | Healthy / Complex | `Healthy` | `0.00` | 0 | `no_detection` | **PASS** |
| **Hard Negative (Soil / Dark)** | Healthy / Dark | `Healthy` | `0.00` | 0 | `no_detection` | **PASS** |

Visualizations saved under `training/runs/tomato_v2/integration_tests/`.

---

## 6. Healthy False-Positive Benchmark

- **Baseline Model (`model/tomato/best.pt`):** 29 / 33 false positives (**87.9% False Positive Rate** on healthy leaves).
- **V2 Model (`model/tomato_v2/best.pt`):** 0 / 33 false positives (**0.0% False Positive Rate**).
- **Outcome:** Background false-positive triggers on healthy leaves are **100% eliminated**.

---

## 7. History & Database Verification

- Every successful prediction via `POST /api/predict` persists a `DiagnosisHistory` record with image URL, bounding boxes, confidence, primary disease, severity, and database care recommendations.
- `GET /api/history` and `GET /api/history/{id}` return complete diagnostic details.
- `DELETE /api/history/{id}` cleanly removes records without damaging the database.

---

## 8. Exact Commands to Run LEAF_AI

### Terminal 1 — Backend (FastAPI)
```powershell
cd C:\Users\Admin\Leaf-Disease-Detection\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API available at:* **`http://127.0.0.1:8000`**  
*Swagger Documentation:* **`http://127.0.0.1:8000/docs`**

### Terminal 2 — Frontend (React + Vite)
```powershell
cd C:\Users\Admin\Leaf-Disease-Detection\frontend
npm run dev
```
*Frontend available at:* **`http://localhost:3000`** *(or `http://localhost:3001` if port 3000 is occupied)*

---

## 9. Remaining Issues & Notes

- **Zero Blocking Issues:** The full-stack pipeline (Frontend -> FastAPI -> YOLOv8n V2 -> Database -> Responsive Bounding Boxes -> History) is operating smoothly.
- **Rollback Option:** If needed, the baseline model remains accessible at `model/tomato/best.pt` simply by setting `MODEL_PATH=model/tomato/best.pt`.
