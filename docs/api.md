# LeafAI API Reference

### Health Check
`GET /api/health`
- **Response**: `{"status": "ok", "service": "LeafAI Backend", "version": "1.0.0"}`

### Predict Leaf Disease
`POST /api/predict`
- **Content-Type**: `multipart/form-data`
- **Body**: `file` (Image file: JPG, PNG, WEBP, max 10MB)
- **Response**:
```json
{
  "id": "diagnosis-uuid",
  "plant": "Cà chua",
  "disease": "Bệnh úa sớm cà chua (Early Blight)",
  "confidence": 0.947,
  "severity": "Trung bình",
  "recommendations": [
    {
      "title": "Cắt tỉa lá bệnh",
      "description": "Cắt bỏ ngay các lá già ở tầng dưới có vết đốm."
    }
  ],
  "image_url": "/uploads/unique-uuid.jpg",
  "heatmap_url": null,
  "created_at": "2026-08-24T15:00:00Z"
}
```

### Disease Library
`GET /api/diseases?search={query}&plant={plant_name}`
`GET /api/diseases/{disease_id}`

### Diagnosis History
`GET /api/history`
`GET /api/history/{id}`
`DELETE /api/history/{id}`

### Care Recommendations
`GET /api/care/{disease_id}`
