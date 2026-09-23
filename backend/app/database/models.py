from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class DiagnosisHistory(Base):
    __tablename__ = "diagnosis_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    image_url = Column(String, nullable=True)
    heatmap_url = Column(String, nullable=True)
    plant = Column(String, nullable=False)
    disease = Column(String, nullable=False)
    primary_disease = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, nullable=True, default="detected")
    detections = Column(JSON, nullable=True)
    detected_diseases = Column(JSON, nullable=True)
    is_multi_disease = Column(Boolean, nullable=True, default=False)
    recommendations = Column(JSON, nullable=True)
    
    # AI Fallback metadata
    fallback_used = Column(Boolean, nullable=True, default=False)
    final_source = Column(String, nullable=True, default="yolo")
    yolo_result = Column(JSON, nullable=True)
    ai_result = Column(JSON, nullable=True)
    fallback_status = Column(String, nullable=True, default="not_configured")
    
    created_at = Column(DateTime, default=get_utc_now)

    treatment_plans = relationship("TreatmentPlan", back_populates="diagnosis", cascade="all, delete-orphan")

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    plant = Column(String, nullable=False)
    scientific_name = Column(String, nullable=True)
    english_name = Column(String, nullable=True)
    severity = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    overview = Column(Text, nullable=True)
    pathogen = Column(String, nullable=True)
    favorable_conditions = Column(String, nullable=True)
    transmission = Column(JSON, nullable=True)
    risk_level_explanation = Column(Text, nullable=True)
    
    # Symptoms by stage
    symptoms = Column(JSON, nullable=False)
    early_symptoms = Column(JSON, nullable=True)
    mid_symptoms = Column(JSON, nullable=True)
    severe_symptoms = Column(JSON, nullable=True)
    similar_diseases_diff = Column(JSON, nullable=True)

    # Integrated Disease Management & Prevention
    prevention_before_planting = Column(JSON, nullable=True)
    prevention_during_growth = Column(JSON, nullable=True)
    water_management = Column(Text, nullable=True)
    nutrition_management = Column(Text, nullable=True)
    density_management = Column(Text, nullable=True)
    field_sanitation = Column(Text, nullable=True)
    pruning_guide = Column(Text, nullable=True)
    crop_rotation_guide = Column(Text, nullable=True)
    biological_control = Column(JSON, nullable=True)
    chemical_control_principles = Column(JSON, nullable=True)
    aftercare_monitoring = Column(JSON, nullable=True)
    common_mistakes = Column(JSON, nullable=True)
    when_to_seek_help = Column(Text, nullable=True)
    safety_notes = Column(Text, nullable=True)
    sources = Column(JSON, nullable=True)
    image_url = Column(String, nullable=True)

    recommendations = relationship("CareRecommendation", back_populates="disease_obj", cascade="all, delete-orphan")

class CareRecommendation(Base):
    __tablename__ = "care_recommendations"

    id = Column(String, primary_key=True, default=generate_uuid)
    disease_id = Column(String, ForeignKey("diseases.id"), nullable=False)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium")

    disease_obj = relationship("Disease", back_populates="recommendations")

class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"

    id = Column(String, primary_key=True, default=generate_uuid)
    diagnosis_id = Column(String, ForeignKey("diagnosis_history.id"), nullable=False)
    disease_id = Column(String, ForeignKey("diseases.id"), nullable=False)
    plan_version = Column(String, nullable=False, default="1.0")
    status = Column(String, nullable=False, default="NOT_STARTED") # NOT_STARTED, IN_PROGRESS, COMPLETED
    created_at = Column(DateTime, default=get_utc_now)
    completed_at = Column(DateTime, nullable=True)

    diagnosis = relationship("DiagnosisHistory", back_populates="treatment_plans")
    disease = relationship("Disease", backref="treatment_plans")
    phases = relationship("TreatmentPhase", back_populates="plan", cascade="all, delete-orphan", order_by="TreatmentPhase.sequence")
    feedbacks = relationship("TreatmentFeedback", back_populates="plan", cascade="all, delete-orphan")


class TreatmentPhase(Base):
    __tablename__ = "treatment_phases"

    id = Column(String, primary_key=True, default=generate_uuid)
    treatment_plan_id = Column(String, ForeignKey("treatment_plans.id"), nullable=False)
    name = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)

    plan = relationship("TreatmentPlan", back_populates="phases")
    steps = relationship("TreatmentStep", back_populates="phase", cascade="all, delete-orphan", order_by="TreatmentStep.sequence")


class TreatmentStep(Base):
    __tablename__ = "treatment_steps"

    id = Column(String, primary_key=True, default=generate_uuid)
    treatment_phase_id = Column(String, ForeignKey("treatment_phases.id"), nullable=False)
    sequence = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    why_it_matters = Column(Text, nullable=True)
    timing = Column(String, nullable=True) # e.g., "IMMEDIATE", "WEEKLY", "CONDITIONAL"
    is_required = Column(Boolean, default=True)

    phase = relationship("TreatmentPhase", back_populates="steps")
    progress = relationship("TreatmentStepProgress", uselist=False, back_populates="step", cascade="all, delete-orphan")
    sources = relationship("TreatmentSource", back_populates="step", cascade="all, delete-orphan")


class TreatmentStepProgress(Base):
    __tablename__ = "treatment_step_progress"

    id = Column(String, primary_key=True, default=generate_uuid)
    treatment_step_id = Column(String, ForeignKey("treatment_steps.id"), nullable=False, unique=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    step = relationship("TreatmentStep", back_populates="progress")


class TreatmentSource(Base):
    __tablename__ = "treatment_sources"

    id = Column(String, primary_key=True, default=generate_uuid)
    treatment_step_id = Column(String, ForeignKey("treatment_steps.id"), nullable=False)
    organization = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    accessed_at = Column(DateTime, nullable=True)

    step = relationship("TreatmentStep", back_populates="sources")


class TreatmentFeedback(Base):
    __tablename__ = "treatment_feedback"

    id = Column(String, primary_key=True, default=generate_uuid)
    diagnosis_id = Column(String, ForeignKey("diagnosis_history.id"), nullable=False)
    treatment_plan_id = Column(String, ForeignKey("treatment_plans.id"), nullable=False)
    effectiveness_percent = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    plan = relationship("TreatmentPlan", back_populates="feedbacks")

