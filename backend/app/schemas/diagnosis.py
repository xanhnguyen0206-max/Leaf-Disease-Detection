from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from app.schemas.prediction import BoundingBox, DetectionItem, DetectedDiseaseGroup

class RecommendationItem(BaseModel):
    title: str
    description: str

class DiagnosisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plant: str
    disease: str
    confidence: float
    severity: str
    recommendations: List[RecommendationItem]
    image_url: Optional[str] = None
    heatmap_url: Optional[str] = None
    created_at: datetime
    status: Optional[str] = "detected"
    primary_disease: Optional[str] = None
    detections: Optional[List[DetectionItem]] = []
    detected_diseases: Optional[List[DetectedDiseaseGroup]] = []
    is_multi_disease: Optional[bool] = False

class DiagnosisHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plant: str
    disease: str
    confidence: float
    severity: str
    recommendations: Optional[Any] = None
    image_url: Optional[str] = None
    heatmap_url: Optional[str] = None
    created_at: datetime
    status: Optional[str] = "detected"
    primary_disease: Optional[str] = None
    detections: Optional[Any] = None
    detected_diseases: Optional[Any] = None
    is_multi_disease: Optional[bool] = False

