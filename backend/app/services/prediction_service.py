import os
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.model_service import model_service
from app.services.ai_fallback_service import ai_fallback_service
from app.database.models import DiagnosisHistory, Disease, CareRecommendation, TreatmentPlan, TreatmentPhase, TreatmentStep, TreatmentSource
from app.database.treatment_knowledge import TREATMENT_PLANS_KNOWLEDGE
from app.core.config import settings

logger = logging.getLogger(__name__)

# Mapping YOLO class names to Database Disease IDs
DISEASE_DB_ID_MAP = {
    "Tomato___Bacterial_spot": "tomato_bacterial_spot",
    "Tomato___Early_blight": "tomato_early_blight",
    "Tomato___Late_blight": "tomato_late_blight",
    "Tomato___Septoria_leaf_spot": "tomato_septoria_leaf_spot",
    "Tomato___Leaf_mold": "tomato_leaf_mold",
    "Tomato___Powdery_mildew": "tomato_powdery_mildew",
    "Potato___Late_blight": "potato_late_blight",
    "Apple___Powdery_mildew": "apple_powdery_mildew",
    "Corn___Common_rust": "corn_common_rust",
}

# Vietnamese display names for classes
DISEASE_DISPLAY_MAP = {
    "Tomato___Bacterial_spot": "Bệnh đốm vi khuẩn cà chua",
    "Tomato___Early_blight": "Bệnh úa sớm cà chua",
    "Tomato___Late_blight": "Bệnh sương mai cà chua",
    "Tomato___Septoria_leaf_spot": "Bệnh đốm mắt cua cà chua",
    "Tomato___Leaf_mold": "Bệnh nấm mốc lá cà chua",
    "Tomato___Powdery_mildew": "Bệnh phấn trắng cà chua",
    "Potato___Late_blight": "Bệnh sương mai khoai tây",
    "Apple___Powdery_mildew": "Bệnh phấn trắng táo",
    "Corn___Common_rust": "Bệnh rỉ sắt ngô",
}

DEFAULT_NO_DETECTION_RECOMMENDATIONS = [
    {
        "title": "Không phát hiện vùng bệnh rõ ràng",
        "description": "Mẫu lá không biểu hiện dấu hiệu bệnh thuộc các lớp mô hình đã được huấn luyện. Cây vẫn có thể gặp vấn đề dinh dưỡng, rễ hoặc bệnh ngoài phạm vi nhận diện."
    },
    {
        "title": "Quan sát và chụp lại nếu cần",
        "description": "Nếu thấy lá có đốm lạ hoặc biến màu, hãy chụp cận cảnh mặt trên và mặt dưới lá ở nơi đủ sáng để kiểm tra lại."
    },
    {
        "title": "Tham khảo sổ tay chăm sóc & IPM",
        "description": "Truy cập mục Chăm sóc để tra cứu quy trình tưới nước, dinh dưỡng cân đối và kiểm tra sức khỏe cây định kỳ hàng tuần."
    }
]

def get_confidence_level_label(conf: float) -> str:
    if conf >= 0.75:
        return "Độ tin cậy cao"
    elif conf >= 0.50:
        return "Độ tin cậy trung bình"
    else:
        return "Dấu hiệu cần kiểm tra thêm"

class PredictionService:
    def process_prediction(
        self,
        file_bytes: bytes,
        filename: str,
        db: Session,
        conf_threshold: Optional[float] = None
    ) -> DiagnosisHistory:
        file_ext = os.path.splitext(filename)[1].lower() or ".jpg"
        unique_name = f"{uuid.uuid4()}{file_ext}"
        saved_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        
        with open(saved_path, "wb") as f:
            f.write(file_bytes)
            
        relative_url = f"/uploads/{unique_name}"
        
        # Run active model prediction
        pred_data = model_service.predict(saved_path, conf_threshold=conf_threshold)
        
        raw_primary_disease = pred_data.get("primary_disease", "no_detection")
        status = pred_data.get("status", "detected")
        plant = pred_data.get("plant", "Cà chua")
        detections = pred_data.get("detections", [])

        # Group detections by disease class
        grouped_by_disease: Dict[str, List[Dict[str, Any]]] = {}
        for det in detections:
            d_name = det.get("disease", "Unknown")
            if d_name not in grouped_by_disease:
                grouped_by_disease[d_name] = []
            grouped_by_disease[d_name].append(det)

        detected_diseases_list: List[Dict[str, Any]] = []

        for d_name, d_dets in grouped_by_disease.items():
            max_conf = max([d["confidence"] for d in d_dets]) if d_dets else 0.0
            det_count = len(d_dets)
            db_id = DISEASE_DB_ID_MAP.get(d_name)
            
            disease_record = None
            if db_id:
                disease_record = db.query(Disease).filter(Disease.id == db_id).first()
            if not disease_record:
                disease_record = db.query(Disease).filter(Disease.name.ilike(f"%{d_name}%")).first()

            if disease_record:
                display_name = disease_record.name
                severity_val = disease_record.severity
                desc = disease_record.description
                syms = disease_record.symptoms or []
                db_care = db.query(CareRecommendation).filter(CareRecommendation.disease_id == disease_record.id).all()
                recs = [{"title": c.title, "description": c.description} for c in db_care] if db_care else [
                    {"title": "Phòng ngừa và xử lý", "description": disease_record.description}
                ]
                matched_id = disease_record.id
            else:
                display_name = DISEASE_DISPLAY_MAP.get(d_name, d_name)
                severity_val = "Trung bình"
                desc = f"Phát hiện dấu hiệu của {display_name}"
                syms = ["Xuất hiện tổn thương trên bề mặt lá"]
                recs = [
                    {"title": "Cắt tỉa lá bệnh", "description": "Loại bỏ các lá có biểu hiện bệnh để tránh lây lan."},
                    {"title": "Kiểm tra độ ẩm", "description": "Tưới nước tại gốc, giữ tán lá khô ráo."}
                ]
                matched_id = db_id

            detected_diseases_list.append({
                "disease": d_name,
                "disease_name": display_name,
                "plant": plant,
                "disease_id": matched_id,
                "max_confidence": round(max_conf, 4),
                "detection_count": det_count,
                "severity": severity_val,
                "confidence_level": get_confidence_level_label(max_conf),
                "description": desc,
                "symptoms": syms,
                "recommendations": recs,
                "detections": d_dets
            })

        # Sort detected disease groups descending by max_confidence
        detected_diseases_list.sort(key=lambda g: g["max_confidence"], reverse=True)

        is_multi_disease = len(detected_diseases_list) > 1

        if not detected_diseases_list or status == "no_detection" or raw_primary_disease in ["Healthy", "no_detection"]:
            status = "no_detection"
            primary_disease = "Healthy"
            disease_name = "Không phát hiện vùng bệnh phù hợp"
            severity = "Chưa phát hiện bệnh"
            confidence = 0.0
            recommendations = DEFAULT_NO_DETECTION_RECOMMENDATIONS
            detected_diseases_list = []
            is_multi_disease = False
        else:
            primary_group = detected_diseases_list[0]
            primary_disease = primary_group["disease"]
            disease_name = primary_group["disease_name"]
            confidence = primary_group["max_confidence"]
            severity = primary_group["severity"]
            recommendations = primary_group["recommendations"]

        fallback_used = False
        final_source = "yolo"
        yolo_result = {
            "primary_disease": primary_disease,
            "confidence": confidence,
            "status": status
        }
        ai_result = None
        fallback_status = "not_configured" if not settings.AI_FALLBACK_ENABLED else "bypassed"

        # AI Fallback Logic
        if settings.AI_FALLBACK_ENABLED:
            if status == "no_detection" or confidence < settings.YOLO_HIGH_CONFIDENCE:
                fallback_status = "triggered"
                ai_resp = ai_fallback_service.analyze(
                    image_bytes=file_bytes,
                    filename=filename,
                    yolo_disease=primary_disease,
                    yolo_confidence=confidence
                )
                
                if ai_resp:
                    fallback_used = True
                    final_source = "ai_fallback"
                    fallback_status = "success"
                    ai_result = ai_resp.model_dump()
                    
                    if not ai_resp.is_tomato_leaf or ai_resp.disease in ["NOT_TOMATO_LEAF", "UNCERTAIN"]:
                        status = "uncertain" if ai_resp.disease == "UNCERTAIN" else "not_tomato_leaf"
                        primary_disease = ai_resp.disease
                        disease_name = "Không xác định" if status == "uncertain" else "Không phải lá cà chua"
                        severity = "Không áp dụng"
                        confidence = ai_resp.confidence
                        recommendations = [
                            {"title": "Kết luận từ AI (Dự phòng)", "description": ai_resp.reason},
                            {"title": "Đề xuất", "description": "Vui lòng chụp lại ảnh lá cà chua rõ nét hơn."}
                        ]
                    else:
                        # Map back to disease info
                        new_disease = ai_resp.disease
                        db_id = DISEASE_DB_ID_MAP.get(new_disease)
                        disease_record = None
                        if db_id:
                            disease_record = db.query(Disease).filter(Disease.id == db_id).first()
                        if not disease_record:
                            disease_record = db.query(Disease).filter(Disease.name.ilike(f"%{new_disease}%")).first()

                        if disease_record:
                            primary_disease = new_disease
                            disease_name = disease_record.name
                            confidence = ai_resp.confidence
                            severity = disease_record.severity
                            db_care = db.query(CareRecommendation).filter(CareRecommendation.disease_id == disease_record.id).all()
                            recs = [{"title": c.title, "description": c.description} for c in db_care] if db_care else [
                                {"title": "Phòng ngừa và xử lý", "description": disease_record.description}
                            ]
                            recs.insert(0, {"title": "Kết luận từ AI (Dự phòng)", "description": ai_resp.reason})
                            recommendations = recs
                else:
                    fallback_status = "failed"

        diagnosis = DiagnosisHistory(
            id=str(uuid.uuid4()),
            image_url=relative_url,
            heatmap_url=None,
            plant=plant,
            disease=disease_name,
            primary_disease=primary_disease,
            confidence=confidence,
            severity=severity,
            status=status,
            detections=detections,
            detected_diseases=detected_diseases_list,
            is_multi_disease=is_multi_disease,
            recommendations=recommendations,
            fallback_used=fallback_used,
            final_source=final_source,
            yolo_result=yolo_result,
            ai_result=ai_result,
            fallback_status=fallback_status
        )
        
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        
        # Check if we should create a Treatment Plan
        if status != "no_detection" and fallback_status != "UNCERTAIN" and primary_disease in TREATMENT_PLANS_KNOWLEDGE:
            plan_data = TREATMENT_PLANS_KNOWLEDGE[primary_disease]
            
            # Map disease_id to actual db disease id
            db_id = DISEASE_DB_ID_MAP.get(primary_disease)
            if db_id:
                disease_record = db.query(Disease).filter(Disease.id == db_id).first()
                if disease_record:
                    plan = TreatmentPlan(
                        diagnosis_id=diagnosis.id,
                        disease_id=disease_record.id,
                        plan_version=plan_data["plan_version"]
                    )
                    db.add(plan)
                    db.flush() # flush to get plan.id
                    
                    for phase_data in plan_data["phases"]:
                        phase = TreatmentPhase(
                            treatment_plan_id=plan.id,
                            name=phase_data["name"],
                            sequence=phase_data["sequence"]
                        )
                        db.add(phase)
                        db.flush()
                        
                        for step_data in phase_data["steps"]:
                            step = TreatmentStep(
                                treatment_phase_id=phase.id,
                                sequence=step_data["sequence"],
                                title=step_data["title"],
                                description=step_data["description"],
                                why_it_matters=step_data.get("why_it_matters"),
                                timing=step_data.get("timing"),
                                is_required=step_data.get("is_required", True)
                            )
                            db.add(step)
                            db.flush()
                            
                            for source_data in step_data.get("sources", []):
                                source = TreatmentSource(
                                    treatment_step_id=step.id,
                                    organization=source_data["organization"],
                                    title=source_data["title"],
                                    url=source_data.get("url")
                                )
                                db.add(source)
                                
                    db.commit()
        
        return diagnosis

prediction_service = PredictionService()

