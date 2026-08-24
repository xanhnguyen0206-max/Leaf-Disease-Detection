# LeafAI FastAPI Backend Service

Production-ready backend API service for plant leaf disease diagnosis and library lookup.

## API Specification

- `GET /api/health`: Health status check.
- `POST /api/predict`: Multipart image upload endpoint for leaf diagnosis.
- `GET /api/history`: Retrieve past diagnosis records.
- `GET /api/history/{id}`: Get single diagnosis record details.
- `DELETE /api/history/{id}`: Remove a diagnosis record.
- `GET /api/diseases`: Disease library listing with search (`?search=`) and plant filter (`?plant=`).
- `GET /api/diseases/{id}`: Detailed disease info and symptoms.
- `GET /api/care/{disease_id}`: Treatment and care recommendations.

## Running locally

```bash
pip install -r requirements.txt
python app/main.py
```
Or with uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
