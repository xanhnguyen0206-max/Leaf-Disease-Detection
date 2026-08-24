# LEAF_AI — Plant Leaf Disease Detection Platform

LEAF_AI is an interactive, full-stack artificial intelligence platform for plant disease diagnosis, treatment recommendations, and agricultural knowledge lookup.

The visual design system is derived from Google Stitch prototypes, featuring a high-tech dark theme, organic glassmorphism, WebGL canvas shaders, and Three.js 3D renderings.

---

## 1. Project Overview

LEAF_AI allows farmers and agronomists to:
- Upload or capture images of diseased plant leaves.
- Perform real-time AI scanning and receive disease identification with confidence scoring.
- Access tailored care recommendations and actionable treatment steps.
- Maintain a diagnosis history to monitor crop health over time.
- Search an agricultural disease library covering symptoms, causes, and severity metrics.

---

## 2. System Architecture

The application is structured into decoupled, modular components:

```
[ Frontend (React + TS) ] ──(HTTP/REST)──> [ Backend (FastAPI) ]
                                                   │
                                        ┌──────────┴──────────┐
                                        ▼                     ▼
                                [ SQLite Database ]   [ PredictionService ]
                                                              │
                                                      ┌───────┴───────┐
                                                      ▼               ▼
                                              [ Mock Service ] [ Future AI Model ]
```

---

## 3. Folder Structure

```
Leaf-Disease-Detection/
├── _stitch_source/                          # Preserved original Stitch HTML prototypes
├── frontend/                                # React + TypeScript + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/                      # Navbar, BottomNav, CanvasShader, ThreeLeaf, etc.
│   │   ├── pages/                           # Home, Diagnose, DiseaseLibrary, History, Care, About
│   │   ├── services/                        # api.ts (Prediction & database service client)
│   │   ├── types/                           # Domain TypeScript interfaces
│   │   └── index.css                        # Design tokens & glassmorphism utilities
│   ├── package.json
│   └── vite.config.ts
├── backend/                                 # Python + FastAPI + SQLite
│   ├── app/
│   │   ├── main.py                          # FastAPI entrypoint & router registration
│   │   ├── api/endpoints/                   # Health, predict, history, diseases, care
│   │   ├── database/                        # SQLAlchemy models, session setup & seed data
│   │   ├── services/                        # Prediction & model service abstractions
│   │   └── schemas/                         # Pydantic validation schemas
│   ├── uploads/                             # Uploaded leaf images storage
│   ├── tests/                               # Pytest automated test suite
│   ├── requirements.txt
│   └── pytest.ini
├── model/                                   # Model artifacts directory (Separated)
│   └── README.md                            # Documentation for model export & integration
├── training/                                # Model training pipeline (Separated)
│   ├── datasets/
│   ├── notebooks/
│   ├── scripts/
│   ├── configs/
│   └── README.md
├── tests/                                   # General integration test docs
├── docs/                                    # Architecture & API reference docs
├── .env.example
├── .gitignore
└── README.md                                # Master project documentation
```

---

## 4. Software Requirements

- **Node.js**: `v18.x` or higher
- **Python**: `3.10` or higher
- **npm**: `v9.x` or higher
- **git**: for version control

---

## 5. Installation & Setup

### Clone & Navigate
```bash
cd C:\Users\Admin\Leaf-Disease-Detection
```

### Backend Installation
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Installation
```bash
cd ../frontend
npm install
```

---

## 6. Environment Variables

Create a `.env` file in the root directory (or copy from `.env.example`):

```ini
PROJECT_NAME="LeafAI Platform API"
VERSION="1.0.0"
API_V1_STR="/api"
PORT=8000
HOST="0.0.0.0"
VITE_API_BASE_URL="http://localhost:8000/api"
```

---

## 7. Running the Application

Running the application requires two active terminal windows.

### Terminal 1: Launch Backend (FastAPI)
```bash
cd C:\Users\Admin\Leaf-Disease-Detection\backend
python app/main.py
```
*The FastAPI server starts at **http://localhost:8000**. Database seed data is initialized automatically.*
*Interactive API docs available at **http://localhost:8000/docs**.*

### Terminal 2: Launch Frontend (Vite)
```bash
cd C:\Users\Admin\Leaf-Disease-Detection\frontend
npm run dev
```
*The React application starts at **http://localhost:3000**.*

---

## 8. Automated Testing

### Running Backend Unit & API Tests
```bash
cd C:\Users\Admin\Leaf-Disease-Detection\backend
pytest
```
*Runs Pytest covering health check, image prediction upload, disease library queries, care recommendations, and history deletion.*

---

## 9. Step-by-Step Manual Test Flow

Follow this step-by-step verification flow:

1. **Open Home Page**: Navigate to `http://localhost:3000`. Observe WebGL background shader, 3D rotating leaf wireframe mesh, and platform metrics.
2. **Navigate to Diagnose**: Click "Chẩn đoán ngay" in the top navbar or primary hero CTA.
3. **Upload Image**: Drag and drop a leaf image file or click to select a file (JPG, PNG, WEBP).
4. **Preview Image**: Inspect the high-resolution leaf image preview canvas.
5. **Start Analysis**: Click "Bắt đầu phân tích bệnh".
6. **Scanner Animation**: Observe the interactive green scanner line animation and glowing status indicator.
7. **View Prediction Card**: Inspect the SVG confidence ring (e.g. `95%`), plant classification (`Cà chua`), identified disease (`Bệnh úa sớm`), and care recommendations.
8. **Check History**: Navigate to `Lịch sử` tab. Verify that the recent diagnosis record appears with timestamp and confidence score.
9. **Delete History Record**: Click "Xóa bản ghi" to remove the item from history.
10. **Open Disease Library**: Click `Thư viện` tab.
11. **Search & Filter**: Type `cà chua` into the search input or click the `Khoai tây` filter chip.
12. **View Disease Detail**: Click "Xem chi tiết bệnh" on any card to view detailed symptoms and care guidelines.

---

## 10. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Check API server operational status |
| `POST` | `/api/predict` | Upload leaf image for AI diagnosis |
| `GET` | `/api/history` | List all historical diagnoses |
| `GET` | `/api/history/{id}` | Get single diagnosis record by UUID |
| `DELETE` | `/api/history/{id}` | Delete diagnosis record by UUID |
| `GET` | `/api/diseases` | List disease library (supports `search` & `plant` filters) |
| `GET` | `/api/diseases/{id}` | Detailed disease info and symptoms |
| `GET` | `/api/care/{disease_id}` | Treatment recommendations for a disease |

---

## 11. Mock AI & Future Model Integration Guide

Currently, `backend/app/services/model_service.py` uses `MockModelService` to simulate prediction results with realistic latency and confidence metrics.

### To integrate your trained AI model:

1. Train your model inside `training/` (e.g., using YOLOv8, PyTorch, or ResNet).
2. Save trained model weights to `model/model.pt` and class index mapping to `model/classes.json`.
3. In `backend/app/services/model_service.py`, replace `MockModelService` with your PyTorch inference loader:
   ```python
   import torch

   class TrainedModelService:
       def __init__(self):
           self.model = torch.load("model/model.pt")
           self.model.eval()

       def predict(self, image_path: str):
           # Load image, preprocess, run model inference
           tensor = preprocess(image_path)
           outputs = self.model(tensor)
           ...
           return {"plant": plant, "disease": disease, "confidence": conf, ...}
   ```
4. **No frontend code changes are needed** because the API contract (`POST /api/predict`) remains identical.

---

## 12. Troubleshooting Guide

- **Port Conflict (8000 or 3000 in use)**:
  Change `PORT` in `backend/app/core/config.py` or `vite.config.ts`.
- **CORS Error**:
  Ensure `CORSMiddleware` in `backend/app/main.py` is enabled for `http://localhost:3000`.
- **Backend Offline Warning in Frontend**:
  The frontend automatically switches to client-side mock data if the FastAPI backend is not running, ensuring smooth demonstration fallback.
