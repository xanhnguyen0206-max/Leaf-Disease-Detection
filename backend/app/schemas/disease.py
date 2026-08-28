from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any

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
    scientific_name: Optional[str] = None
    english_name: Optional[str] = None
    severity: str
    description: str
    overview: Optional[str] = None
    pathogen: Optional[str] = None
    favorable_conditions: Optional[str] = None
    transmission: Optional[List[str]] = None
    risk_level_explanation: Optional[str] = None
    
    symptoms: List[str]
    early_symptoms: Optional[List[str]] = None
    mid_symptoms: Optional[List[str]] = None
    severe_symptoms: Optional[List[str]] = None
    similar_diseases_diff: Optional[List[str]] = None

    prevention_before_planting: Optional[List[str]] = None
    prevention_during_growth: Optional[List[str]] = None
    water_management: Optional[str] = None
    nutrition_management: Optional[str] = None
    density_management: Optional[str] = None
    field_sanitation: Optional[str] = None
    pruning_guide: Optional[str] = None
    crop_rotation_guide: Optional[str] = None
    biological_control: Optional[List[str]] = None
    chemical_control_principles: Optional[List[str]] = None
    aftercare_monitoring: Optional[List[str]] = None
    common_mistakes: Optional[List[str]] = None
    when_to_seek_help: Optional[str] = None
    safety_notes: Optional[str] = None
    sources: Optional[List[str]] = None
    image_url: Optional[str] = None
    recommendations: Optional[List[CareRecommendationSchema]] = None
