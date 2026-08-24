import os
import shutil
import uuid
from sqlalchemy.orm import Session
from app.services.model_service import model_service
from app.database.models import DiagnosisHistory
from app.core.config import settings

class PredictionService:
    def process_prediction(self, file_bytes: bytes, filename: str, db: Session) -> DiagnosisHistory:
        file_ext = os.path.splitext(filename)[1].lower() or ".jpg"
        unique_name = f"{uuid.uuid4()}{file_ext}"
        saved_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        
        with open(saved_path, "wb") as f:
            f.write(file_bytes)
            
        relative_url = f"/uploads/{unique_name}"
        
        # Run model prediction
        pred_data = model_service.predict(saved_path)
        
        diagnosis = DiagnosisHistory(
            id=str(uuid.uuid4()),
            image_url=relative_url,
            heatmap_url=None,
            plant=pred_data["plant"],
            disease=pred_data["disease"],
            confidence=pred_data["confidence"],
            severity=pred_data["severity"],
            recommendations=pred_data["recommendations"]
        )
        
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        return diagnosis

prediction_service = PredictionService()
