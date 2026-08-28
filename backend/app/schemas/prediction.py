from pydantic import BaseModel, Field
from typing import List, Optional, Any

class BoundingBox(BaseModel):
    x1: float = Field(..., description="Top-left X coordinate")
    y1: float = Field(..., description="Top-left Y coordinate")
    x2: float = Field(..., description="Bottom-right X coordinate")
    y2: float = Field(..., description="Bottom-right Y coordinate")

class DetectionItem(BaseModel):
    class_id: int = Field(..., description="Numeric class identifier from YOLO model")
    disease: str = Field(..., description="Detected disease class name")
    confidence: float = Field(..., description="Prediction confidence between 0.0 and 1.0")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates for detected region")

class DetectedDiseaseGroup(BaseModel):
    disease: str = Field(..., description="Raw YOLO disease class name (e.g. Tomato___Bacterial_spot)")
    disease_name: str = Field(..., description="Human-friendly display name (e.g. Bệnh đốm vi khuẩn cà chua)")
    plant: str = Field(default="Cà chua", description="Host plant name")
    disease_id: Optional[str] = Field(None, description="Database ID matching diseases table for deep navigation")
    max_confidence: float = Field(..., description="Maximum confidence score among detections of this class")
    detection_count: int = Field(..., description="Number of detected lesion regions of this class")
    severity: str = Field(default="Trung bình", description="Disease severity level")
    confidence_level: str = Field(default="Độ tin cậy cao", description="Text description: Độ tin cậy cao / Độ tin cậy trung bình / Dấu hiệu cần kiểm tra thêm")
    description: Optional[str] = Field(None, description="Brief description of the disease")
    symptoms: Optional[List[str]] = Field(default=[], description="Common symptoms")
    recommendations: Optional[List[Any]] = Field(default=[], description="Targeted recommendations for this disease")
    detections: List[DetectionItem] = Field(default=[], description="All bounding box detections for this disease")

class PredictionRawResult(BaseModel):
    plant: str = "Tomato"
    status: str = "detected"  # 'detected' or 'no_detection'
    primary_disease: str
    confidence: float
    detections: List[DetectionItem] = []
    detected_diseases: List[DetectedDiseaseGroup] = []
    is_multi_disease: bool = False
