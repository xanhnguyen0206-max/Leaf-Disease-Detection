# Tomato Disease Detection Model Integration Guide (Model V3)

This document details the architecture, configuration, inference workflow, and operational instructions for the trained YOLOv8 Tomato Disease Detection model (V3) integrated into the LeafAI backend.

---

## 1. Model Overview & Specifications

- **Default Production Model Path**: `model/tomato_v3/best.pt`
- **Metadata File**: `model/tomato_v3/metadata.json`
- **Classes File**: `model/tomato_v3/classes.json`
- **Backup Model File (Preserved)**: `model/tomato_v2/best.pt`
- **Baseline Model File (Preserved)**: `model/tomato/best.pt`
- **Architecture**: Ultralytics YOLOv8n (Object Detection)
- **Input Resolution**: 640x640 pixels
- **Framework**: PyTorch (`torch`), Ultralytics YOLO (`ultralytics`)
- **Default Device**: `cpu` (or `cuda` if GPU available)
- **Supported Classes**:
  | Class ID | Class Name | Vietnamese Label |
  | :--- | :--- | :--- |
  | `0` | `Tomato___Bacterial_spot` | Bệnh đốm vi khuẩn cà chua |
  | `1` | `Tomato___Early_blight` | Bệnh úa sớm cà chua |
  | `2` | `Tomato___Late_blight` | Bệnh sương mai cà chua |

---

## 2. Model Switching & Rollback

The model path is fully configurable via `app/core/config.py` and environment variables.

### To use V3 Model (Default Production):
```ini
MODEL_TYPE=yolo
MODEL_VERSION=v3
MODEL_PATH=model/tomato_v3/best.pt
MODEL_IMG_SIZE=640
MODEL_CONFIDENCE_THRESHOLD=0.25
MODEL_DEVICE=cpu
```

### To switch to V2 Backup Model:
```ini
MODEL_VERSION=v2
MODEL_PATH=model/tomato_v2/best.pt
MODEL_IMG_SIZE=384
```

### To rollback to Baseline Model:
```ini
MODEL_PATH=model/tomato/best.pt
```

---

## 3. Architecture & Inference Pipeline

The system uses a modular and switchable model service architecture:

```
                  ┌─────────────────────────────────────────┐
                  │          Client / Frontend UI           │
                  └───────────────────┬─────────────────────┘
                                      │ POST /api/predict (Multipart image)
                                      ▼
                  ┌─────────────────────────────────────────┐
                  │       FastAPI Endpoint (predict.py)     │
                  │ - File format & extension validation    │
                  │ - Empty file detection                  │
                  │ - Image integrity verification (Pillow) │
                  └───────────────────┬─────────────────────┘
                                      │ Valid Image Stream
                                      ▼
                  ┌─────────────────────────────────────────┐
                  │ PredictionService (prediction_service.py)│
                  │ - Saves image to /uploads/              │
                  │ - Passes image to Active Model Service  │
                  └───────────────────┬─────────────────────┘
                                      │
         ┌────────────────────────────┴───────────────────────────┐
         │                                                        │
         ▼ (MODEL_TYPE=yolo)                                      ▼ (MODEL_TYPE=mock)
┌─────────────────────────────────┐                    ┌─────────────────────────┐
│        YOLOModelService         │                    │    MockModelService     │
│ - Verified model weights exist  │                    │ - Synthetic predictions │
│ - In-memory YOLO model instance │                    │ - Offline development   │
│ - Multiclass bounding box det.  │                    └─────────────────────────┘
│ - Confidence threshold filtering│
└────────────────┬────────────────┘
                 │ Detections & Primary Disease
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Database Lookup (SQLite / SQLAlchemy)                           │
│ - Fetches curated severity and treatment recommendations from DB│
│ - NO LLM connected: prevents hallucinated advice                │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Response Building & History Storage                             │
│ - Saves DiagnosisHistory record with bounding boxes             │
│ - Returns structured DiagnosisResult JSON to client             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Benchmark Performance: Baseline vs. Model V2

| Metric | Baseline Model (`model/tomato/best.pt`) | V2 Model (`model/tomato_v2/best.pt`) | Improvement |
| :--- | :---: | :---: | :---: |
| **Precision** | 0.6937 | **0.7340** | **+4.03%** |
| **Recall** | 0.6541 | **0.7010** | **+4.69%** |
| **mAP@50** | 0.6968 | **0.7430** | **+4.62%** |
| **mAP@50-95** | 0.4037 | **0.4200** | **+1.63%** |
| **Hard Negative False Positive Rate** | **87.9%** (29/33 false detections) | **0.0%** (0/33 false detections) | **100% Fixed** |

---

## 5. API Specification

### Endpoint: `POST /api/predict`

**Request:**
- **Content-Type**: `multipart/form-data`
- **Query Parameters**:
  - `conf_threshold` *(optional, float)*: Override default confidence threshold (e.g. `?conf_threshold=0.30`).
- **Form Body**:
  - `file`: Image binary (`image/jpeg`, `image/png`, `image/webp`). Maximum size: 10MB.

**Success Response (`200 OK`):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "plant": "Cà chua",
  "disease": "Bệnh úa sớm cà chua (Early Blight)",
  "primary_disease": "Tomato___Early_blight",
  "confidence": 0.8425,
  "severity": "Trung bình",
  "status": "detected",
  "detections": [
    {
      "class_id": 1,
      "disease": "Tomato___Early_blight",
      "confidence": 0.8425,
      "bbox": {
        "x1": 150.5,
        "y1": 120.2,
        "x2": 310.8,
        "y2": 280.4
      }
    }
  ],
  "recommendations": [
    {
      "title": "Cắt tỉa lá bệnh",
      "description": "Cắt bỏ ngay các lá già ở tầng dưới có xuất hiện vết đốm sẫm màu."
    }
  ],
  "image_url": "/uploads/3fa85f64-5717-4562-b3fc-2c963f66afa6.jpg",
  "created_at": "2026-08-26T14:20:00.000000"
}
```

---

## 6. Health & Diagnostics Endpoint: `GET /api/health`

Returns the active model metadata:
```json
{
  "status": "ok",
  "service": "LeafAI Backend",
  "version": "1.0.0",
  "model": {
    "type": "yolo",
    "path": "model/tomato_v2/best.pt",
    "loaded": true,
    "confidence_threshold": 0.25,
    "device": "cpu"
  }
}
```
