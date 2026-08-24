from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

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
