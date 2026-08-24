from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.database.models import CareRecommendation
from app.schemas.disease import CareRecommendationSchema

router = APIRouter()

@router.get("/care/{disease_id}", response_model=List[CareRecommendationSchema])
def get_care_recommendations(disease_id: str, db: Session = Depends(get_db)):
    items = db.query(CareRecommendation).filter(CareRecommendation.disease_id == disease_id).all()
    return items
