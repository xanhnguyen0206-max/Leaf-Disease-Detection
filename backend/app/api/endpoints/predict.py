import os
import io
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError
from app.database.session import get_db
from app.services.prediction_service import prediction_service
from app.schemas.diagnosis import DiagnosisResult

logger = logging.getLogger(__name__)
router = APIRouter()

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

@router.post("/predict", response_model=DiagnosisResult)
async def predict_leaf(
    file: UploadFile = File(...),
    conf_threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Optional confidence threshold (0.0 - 1.0)"),
    db: Session = Depends(get_db)
):
    # 1. Validate filename
    if not file.filename or not file.filename.strip():
        raise HTTPException(status_code=400, detail="Tên file không hợp lệ hoặc để trống.")
        
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng ảnh '{ext}' không được hỗ trợ. Vui lòng tải lên ảnh định dạng JPG, JPEG, PNG hoặc WEBP."
        )
        
    # 2. Read and validate file content length
    try:
        contents = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(status_code=400, detail="Không thể đọc nội dung file tải lên.")

    if not contents or len(contents) == 0:
        raise HTTPException(status_code=400, detail="File tải lên trống (kích thước 0 bytes).")

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Kích thước file vượt quá giới hạn cho phép (10MB).")

    # 3. Validate image integrity (detect corrupted or fake images)
    try:
        image_stream = io.BytesIO(contents)
        with Image.open(image_stream) as img:
            img.verify()
    except (UnidentifiedImageError, Exception) as img_err:
        logger.warning(f"Uploaded file failed image verification: {img_err}")
        raise HTTPException(
            status_code=400,
            detail="File tải lên bị hỏng hoặc không phải là định dạng hình ảnh hợp lệ."
        )

    # 4. Run prediction pipeline
    try:
        result = prediction_service.process_prediction(
            file_bytes=contents,
            filename=file.filename,
            db=db,
            conf_threshold=conf_threshold
        )
        return result
    except FileNotFoundError as fnf_err:
        logger.error(f"Model or resource file not found: {fnf_err}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi cấu hình hệ thống AI: {str(fnf_err)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error during leaf disease diagnosis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi hệ thống khi phân tích và nhận diện bệnh lá: {str(e)}"
        )

