from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class DiagnosisHistory(Base):
    __tablename__ = "diagnosis_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    image_url = Column(String, nullable=True)
    heatmap_url = Column(String, nullable=True)
    plant = Column(String, nullable=False)
    disease = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    plant = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    symptoms = Column(JSON, nullable=False)
    severity = Column(String, nullable=False)
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
