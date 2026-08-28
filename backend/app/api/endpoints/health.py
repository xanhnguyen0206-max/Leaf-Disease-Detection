import os
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    model_loaded = os.path.exists(settings.MODEL_PATH)
    # Relative clean path representation for safety
    rel_model_path = os.path.relpath(settings.MODEL_PATH, settings.PROJECT_ROOT).replace("\\", "/")
    
    return {
        "status": "ok",
        "service": "LeafAI Backend",
        "version": settings.VERSION,
        "model": {
            "type": settings.MODEL_TYPE,
            "path": rel_model_path,
            "loaded": model_loaded,
            "confidence_threshold": settings.MODEL_CONFIDENCE_THRESHOLD,
            "device": settings.MODEL_DEVICE
        }
    }
