from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.prediction_service import prediction_service
from app.schemas.diagnosis import DiagnosisResult
import os

router = APIRouter()

@router.post("/predict", response_model=DiagnosisResult)
async def predict_leaf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Không tìm thấy tên file.")
        
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail=f"Định dạng ảnh '{ext}' không hợp lệ. Vui lòng chọn JPG, PNG hoặc WEBP.")
        
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Kích thước file vượt quá 10MB.")
        
    try:
        result = prediction_service.process_prediction(contents, file.filename, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi phân tích ảnh: {str(e)}")
