# LeafAI FastAPI Backend Service

Production-ready backend API service for plant leaf disease diagnosis and agricultural library lookup.

## Production Model

- **Current Active Model**: YOLOv8n V3 (`model/tomato_v3/best.pt`)
- **Input Resolution**: 640x640 (Auto letterbox preserved)
- **Supported Formats**: JPG, JPEG, PNG, WEBP (Max 10MB)
- **Output**: Plant, Primary disease, Confidence score, Bounding boxes, Severity, Recommendations, Diagnosis ID
- **Backup Model**: YOLOv8n V2 (`model/tomato_v2/best.pt`)

## API Specification

- `GET /api/health`: Health status check and model metadata.
- `POST /api/predict`: Multipart image upload endpoint for leaf diagnosis (`?conf_threshold=`).
- `GET /api/history`: Retrieve past diagnosis records.
- `GET /api/history/{id}`: Get single diagnosis record details.
- `DELETE /api/history/{id}`: Remove a diagnosis record.
- `GET /api/diseases`: Disease library listing with search (`?search=`) and plant filter (`?plant=`).
- `GET /api/diseases/{id}`: Detailed disease info and symptoms.
- `GET /api/care/{disease_id}`: Treatment and care recommendations.

## Running Locally

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive Swagger Docs**: http://127.0.0.1:8000/docs
- **Alternative ReDoc**: http://127.0.0.1:8000/redoc
