from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import TreatmentPlan, TreatmentStepProgress, TreatmentFeedback, TreatmentStep, DiagnosisHistory
from app.schemas.treatment_plan import TreatmentPlanSchema, TreatmentFeedbackCreate
from datetime import datetime, timezone
from sqlalchemy import func

router = APIRouter()

def get_utc_now():
    return datetime.now(timezone.utc)

@router.get("/treatment-plans/{diagnosis_id}", response_model=TreatmentPlanSchema)
def get_treatment_plan(diagnosis_id: str, db: Session = Depends(get_db)):
    plan = db.query(TreatmentPlan).filter(TreatmentPlan.diagnosis_id == diagnosis_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Không tìm thấy lộ trình chăm sóc cho chẩn đoán này.")
    
    # Calculate progress
    total_steps = 0
    completed_steps = 0
    
    for phase in plan.phases:
        for step in phase.steps:
            if step.is_required:
                total_steps += 1
                if step.progress and step.progress.completed:
                    completed_steps += 1
                    
    percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
    
    plan_dict = {
        "id": plan.id,
        "diagnosis_id": plan.diagnosis_id,
        "disease_id": plan.disease_id,
        "plan_version": plan.plan_version,
        "status": plan.status,
        "created_at": plan.created_at,
        "completed_at": plan.completed_at,
        "phases": plan.phases,
        "progress": {
            "completed": completed_steps,
            "total": total_steps,
            "percentage": percentage
        }
    }
    
    return plan_dict

@router.patch("/treatment-plans/{plan_id}/steps/{step_id}")
def update_step_progress(plan_id: str, step_id: str, completed: bool, db: Session = Depends(get_db)):
    step = db.query(TreatmentStep).join(TreatmentStep.phase).filter(
        TreatmentStep.id == step_id,
        TreatmentStep.phase.has(treatment_plan_id=plan_id)
    ).first()
    
    if not step:
        raise HTTPException(status_code=404, detail="Không tìm thấy bước cần cập nhật.")
        
    progress = step.progress
    if not progress:
        progress = TreatmentStepProgress(treatment_step_id=step.id)
        db.add(progress)
        
    progress.completed = completed
    progress.completed_at = get_utc_now() if completed else None
    
    # Update plan status
    db.commit()
    
    plan = db.query(TreatmentPlan).filter(TreatmentPlan.id == plan_id).first()
    if plan:
        all_required_completed = True
        has_started = False
        
        for phase in plan.phases:
            for s in phase.steps:
                if s.progress and s.progress.completed:
                    has_started = True
                if s.is_required and (not s.progress or not s.progress.completed):
                    all_required_completed = False
                    
        if all_required_completed:
            plan.status = "COMPLETED"
            plan.completed_at = get_utc_now()
        elif has_started:
            plan.status = "IN_PROGRESS"
            plan.completed_at = None
        else:
            plan.status = "NOT_STARTED"
            plan.completed_at = None
            
        db.commit()
        
    return {"message": "Đã cập nhật trạng thái bước."}

@router.post("/treatment-plans/{plan_id}/feedback")
def submit_feedback(plan_id: str, feedback: TreatmentFeedbackCreate, db: Session = Depends(get_db)):
    plan = db.query(TreatmentPlan).filter(TreatmentPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Không tìm thấy lộ trình.")
        
    # Check if feedback already exists
    existing = db.query(TreatmentFeedback).filter(TreatmentFeedback.treatment_plan_id == plan_id).first()
    if existing:
        existing.effectiveness_percent = feedback.effectiveness_percent
        existing.comment = feedback.comment
    else:
        new_feedback = TreatmentFeedback(
            diagnosis_id=plan.diagnosis_id,
            treatment_plan_id=plan_id,
            effectiveness_percent=feedback.effectiveness_percent,
            comment=feedback.comment
        )
        db.add(new_feedback)
        
    db.commit()
    return {"message": "Đã lưu đánh giá."}
