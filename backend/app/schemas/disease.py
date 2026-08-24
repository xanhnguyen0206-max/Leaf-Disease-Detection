from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class CareRecommendationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    disease_id: str
    category: str
    title: str
    description: str
    priority: str

class DiseaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    plant: str
    description: str
    symptoms: List[str]
    severity: str
    image_url: Optional[str] = None
    recommendations: Optional[List[CareRecommendationSchema]] = None
