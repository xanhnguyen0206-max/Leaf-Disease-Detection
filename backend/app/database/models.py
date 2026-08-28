from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
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
    created_at = Column(DateTime, default=get_utc_now)

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
