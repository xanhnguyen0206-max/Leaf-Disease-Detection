from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TreatmentSourceSchema(BaseModel):
    id: str
    organization: str
    title: str
    url: Optional[str]

    class Config:
        from_attributes = True

class TreatmentStepProgressSchema(BaseModel):
    completed: bool
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class TreatmentStepSchema(BaseModel):
    id: str
    sequence: int
    title: str
    description: str
    why_it_matters: Optional[str]
    timing: Optional[str]
    is_required: bool
    progress: Optional[TreatmentStepProgressSchema]
    sources: List[TreatmentSourceSchema]

    class Config:
        from_attributes = True

class TreatmentPhaseSchema(BaseModel):
    id: str
    name: str
    sequence: int
    steps: List[TreatmentStepSchema]

    class Config:
        from_attributes = True

class TreatmentPlanProgressSummary(BaseModel):
    completed: int
    total: int
    percentage: float

class TreatmentPlanSchema(BaseModel):
    id: str
    diagnosis_id: str
    disease_id: str
    plan_version: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    phases: List[TreatmentPhaseSchema]
    progress: Optional[TreatmentPlanProgressSummary] = None

    class Config:
        from_attributes = True

class TreatmentFeedbackCreate(BaseModel):
    effectiveness_percent: int
    comment: Optional[str] = None
