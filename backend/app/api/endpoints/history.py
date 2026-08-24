from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.database.models import DiagnosisHistory
from app.schemas.diagnosis import DiagnosisHistoryResponse

router = APIRouter()

@router.get("/history", response_model=List[DiagnosisHistoryResponse])
def get_diagnosis_history(db: Session = Depends(get_db)):
    items = db.query(DiagnosisHistory).order_by(DiagnosisHistory.created_at.desc()).all()
    return items

@router.get("/history/{history_id}", response_model=DiagnosisHistoryResponse)
def get_diagnosis_item(history_id: str, db: Session = Depends(get_db)):
    item = db.query(DiagnosisHistory).filter(DiagnosisHistory.id == history_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi chẩn đoán.")
    return item

@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diagnosis_item(history_id: str, db: Session = Depends(get_db)):
    item = db.query(DiagnosisHistory).filter(DiagnosisHistory.id == history_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi chẩn đoán.")
    db.delete(item)
    db.commit()
    return None
