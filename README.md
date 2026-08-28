# LEAF_AI — Plant Leaf Disease Detection Platform

LEAF_AI is an interactive, full-stack artificial intelligence platform for plant disease diagnosis, treatment recommendations, and agricultural knowledge lookup.

The visual design system is derived from Google Stitch prototypes, featuring a high-tech dark theme, organic glassmorphism, WebGL canvas shaders, and Three.js 3D renderings.

---

# Run LEAF_AI

## Backend

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Frontend

```bash
cd frontend
npm run dev
```

## Open

- **Web Application**: http://localhost:3000 *(or `http://localhost:3001` if port 3000 is occupied)*
- **Interactive API Docs (Swagger)**: http://127.0.0.1:8000/docs

---

## 1. Model Configuration & Switching

The default production model is **LEAF_AI Tomato Disease Detection V3** (`model/tomato_v3/best.pt`), trained at **640x640 resolution** with leaf-safe data augmentation and annotation normalization. It achieves **0.768 mAP@50** on unseen test data, **80.8% detection sensitivity** on tiny Bacterial Spot lesions, and maintains high background specificity.

The previous **V2 model** (`model/tomato_v2/best.pt`) is preserved as a verified backup and can be activated at any time.

### Default Production Model (V3)
- **Default Path**: `model/tomato_v3/best.pt`
- **Input Resolution**: `640x640`
- **Metadata**: `model/tomato_v3/metadata.json`
- **Classes**:
  - `0`: `Tomato___Bacterial_spot` (Bệnh đốm vi khuẩn cà chua)
  - `1`: `Tomato___Early_blight` (Bệnh úa sớm cà chua)
  - `2`: `Tomato___Late_blight` (Bệnh sương mai cà chua)

### How to Switch Models

You can configure the active model via environment variables or `.env` file without modifying source code:

```ini
# Use V3 Model (Default Production):
MODEL_TYPE=yolo
MODEL_VERSION=v3
MODEL_PATH=model/tomato_v3/best.pt
MODEL_IMG_SIZE=640
MODEL_CONFIDENCE_THRESHOLD=0.25
MODEL_DEVICE=cpu

# Or Switch to V2 Backup Model:
MODEL_VERSION=v2
MODEL_PATH=model/tomato_v2/best.pt
MODEL_IMG_SIZE=384

# Or Rollback / Test with Baseline Model:
MODEL_PATH=model/tomato/best.pt
```

The baseline model at `model/tomato/best.pt` remains preserved for regression testing and benchmarking.

---

## 2. System Architecture

```
[ Frontend (React + TS + Vite) ] ──(HTTP/REST Proxy)──> [ Backend (FastAPI) ]
                                                                │
                                                    ┌───────────┴───────────┐
                                                    ▼                       ▼
                                            [ SQLite Database ]    [ PredictionService ]
                                            (Curated Care Guides)           │
                                                                    ┌───────┴───────┐
                                                                    ▼               ▼
                                                           [ YOLOModelService ] [ MockModelService ]
                                                        (model/tomato_v2/best.pt) (Optional dev mock)
```

---

## 3. Folder Structure

```
Leaf-Disease-Detection/
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
│   │   ├── services/                        # YOLO & Mock model services, PredictionService
│   │   ├── core/                            # App settings & model configuration
│   │   └── schemas/                         # Pydantic validation schemas
│   ├── uploads/                             # Uploaded leaf images storage
│   ├── tests/                               # Pytest automated test suite
│   ├── requirements.txt
│   └── pytest.ini
├── model/                                   # Trained model artifacts
│   ├── tomato_v2/                           # DEFAULT V2 Model Checkpoint
│   │   ├── best.pt                          # YOLOv8n weights checkpoint
│   │   ├── classes.json                     # Class label mapping
│   │   └── metadata.json                    # Model training & evaluation metrics
│   └── tomato/                              # Preserved Baseline Model Checkpoint
│       ├── best.pt
│       ├── classes.json
│       └── metadata.json
├── training/                                # Model training pipeline & datasets
│   ├── datasets/processed/tomato_v2/        # Processed V2 YOLO dataset (train/val/test)
│   ├── datasets/raw/tomato_extra/           # Raw extra dataset
│   ├── scripts/                             # Dataset preparation, training & evaluation scripts
│   └── docs/                                # Detailed training & inspection reports
├── docs/                                    # Technical documentation
│   ├── tomato_v2_integration_report.md      # Full-stack integration report
│   ├── model_integration.md                 # Complete YOLO model integration & API guide
│   ├── architecture.md
│   └── api.md
├── .env.example
├── .gitignore
└── README.md                                # Master project documentation
```

---

## 4. Software Requirements

- **Node.js**: `v18.x` or higher
- **Python**: `3.10` or higher
- **npm**: `v9.x` or higher

---

## 5. Installation & Setup

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

## 6. Automated Testing

### Backend Pytest Suite
```bash
python -m pytest backend/tests -v
```

### Real Image API Integration Test
```bash
python training/scripts/test_v2_integration_api.py
```

### Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 7. Model Integration Details

For full technical specifications on YOLO model inference, bounding box structures, database recommendations, and model upgrade procedures, see:
- [Model Integration Guide](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/model_integration.md)
- [Tomato V2 Training Report](file:///c:/Users/Admin/Leaf-Disease-Detection/training/docs/tomato_v2_training_report.md)
- [Full-Stack Integration Report](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/tomato_v2_integration_report.md)
