from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.database.models import Disease
from app.schemas.disease import DiseaseSchema

router = APIRouter()

@router.get("/diseases", response_model=List[DiseaseSchema])
def get_diseases(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên bệnh hoặc triệu chứng"),
    plant: Optional[str] = Query(None, description="Lọc theo loài cây trồng"),
    db: Session = Depends(get_db)
):
    query = db.query(Disease)
    if plant and plant != "Tất cả":
        query = query.filter(Disease.plant == plant)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Disease.name.ilike(search_pattern)) | 
            (Disease.description.ilike(search_pattern)) |
            (Disease.plant.ilike(search_pattern))
        )
    return query.all()

@router.get("/diseases/{disease_id}", response_model=DiseaseSchema)
def get_disease_detail(disease_id: str, db: Session = Depends(get_db)):
    disease = db.query(Disease).filter(Disease.id == disease_id).first()
    if not disease:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin bệnh cây trồng.")
    return disease
