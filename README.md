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

The default production model is **LEAF_AI Tomato Disease Detection V4** (`model/tomato_v4/best.pt`). This upgraded model supports 6 classes (including new diseases like Leaf Mold, Powdery Mildew, and Septoria Leaf Spot) and is integrated with our advanced Treatment Journey framework.

*Note: The raw and processed Tomato V4 dataset (images) is deliberately excluded from this GitHub repository to avoid large file issues. To retrain the model, you will need to download the dataset externally and place it in the appropriate `training/datasets` structure as required by the training scripts.*

The previous V2 and V3 models are preserved as verified backups and can be activated at any time.

### Default Production Model (V4)
- **Default Path**: `model/tomato_v4/best.pt`
- **Training Config**: `model/tomato_v4/data.yaml`
- **Classes** (6 total):
  - `0`: `Tomato___Bacterial_spot`
  - `1`: `Tomato___Early_blight`
  - `2`: `Tomato___Late_blight`
  - `3`: `Tomato___Leaf_Mold`
  - `4`: `Tomato___powdery_mildew`
  - `5`: `Tomato___Septoria_leaf_spot`

### How to Switch Models

You can configure the active model via environment variables or `.env` file without modifying source code:

```ini
# Use V4 Model (Default Production):
MODEL_TYPE=yolo
MODEL_VERSION=v4
MODEL_PATH=model/tomato_v4/best.pt
MODEL_IMG_SIZE=640
MODEL_CONFIDENCE_THRESHOLD=0.25
MODEL_DEVICE=cpu

# Or Switch to V3 Backup Model:
MODEL_VERSION=v3
MODEL_PATH=model/tomato_v3/best.pt
MODEL_IMG_SIZE=640
```

The baseline models remain preserved for regression testing and benchmarking.

---

## 2. Tomato V4 Dataset & Reproducibility

GitHub contains the source code, training scripts, configs, and the final production model for Tomato V4. However, the heavy raw and processed image datasets are deliberately stored outside of GitHub on Google Drive.

### Repository vs Dataset Storage
| Storage | Purpose |
|---------|---------|
| **GitHub** | Source code, model weights (`best.pt`), training scripts, configs, documentation |
| **Google Drive** | Large Tomato datasets (Raw & Processed images/labels) |

**Google Drive Link:** [LEAF_AI Tomato V4 Datasets](https://drive.google.com/drive/folders/1sOvX_ULlLlyowvvkS2DAyyPxgxEs2_r9?usp=drive_link)

To retrain or reproduce the V4 model from scratch, you must download the dataset and place it in the correct location relative to your project root (`PROJECT_ROOT`). The direct dataset used for training V4 is the `processed/tomato_v4` dataset. (The `raw` datasets are also backed up on Drive if you wish to rebuild the processed dataset from scratch).

### Expected Dataset Structure
Download the processed dataset and extract it so that it resides precisely at `training/datasets/processed/tomato_v4/`.

The expected structure inside your project should look like this:
```text
Leaf-Disease-Detection/ (PROJECT_ROOT)
└── training/
    └── datasets/
        └── processed/
            └── tomato_v4/
                ├── data.yaml
                ├── images/
                │   ├── train/
                │   ├── val/
                │   └── test/
                ├── labels/
                │   ├── train/
                │   ├── val/
                │   └── test/
                └── samples/
```

### Tomato V4 Reproducibility Checklist

Follow these exact steps to reproduce the training environment and retrain the model:

- [ ] **Clone repository**: Clone this GitHub repository to your local machine.
- [ ] **Download dataset**: Download the `processed/tomato_v4` dataset from the Google Drive link above.
- [ ] **Restore dataset into project**: Extract the dataset and place it exactly at `training/datasets/processed/tomato_v4/` relative to your `PROJECT_ROOT`. Do not use absolute paths (e.g. `C:\Users\Admin\...`).
- [ ] **Verify `data.yaml`**: Ensure `training/datasets/processed/tomato_v4/data.yaml` exists and correctly maps the 6 classes.
- [ ] **Verify training script**: The training script is located at `training/scripts/train_tomato_v4.py`.
- [ ] **Run training**: Execute the training script from the project root:
      ```bash
      python training/scripts/train_tomato_v4.py
      ```
- [ ] **Verify generated model**: The newly trained model will typically be outputted in the `runs/` directory (e.g., `runs/detect/train/weights/best.pt`). You can overwrite the production model at `model/tomato_v4/best.pt` with this new weight file.
- [ ] **Run backend/frontend**: Start the backend and frontend servers as instructed in the Run section.
- [ ] **Test prediction**: Test the new model using the Diagnose page or the API.

---

## 3. System Architecture

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

## 4. Folder Structure

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

## 5. Software Requirements

- **Node.js**: `v18.x` or higher
- **Python**: `3.10` or higher
- **npm**: `v9.x` or higher

---

## 6. Installation & Setup

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

## 7. Automated Testing

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

## 8. Model Integration Details

For full technical specifications on YOLO model inference, bounding box structures, database recommendations, and model upgrade procedures, see:
- [Model Integration Guide](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/model_integration.md)
- [Tomato V2 Training Report](file:///c:/Users/Admin/Leaf-Disease-Detection/training/docs/tomato_v2_training_report.md)
- [Full-Stack Integration Report](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/tomato_v2_integration_report.md)
