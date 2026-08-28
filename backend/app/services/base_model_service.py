from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseModelService(ABC):
    @abstractmethod
    def predict(self, image_path: str, conf_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Run inference on the given image path and return predictions.
        
        Expected return dictionary structure:
        {
            "plant": str,
            "disease": str,                 # Primary disease name for display
            "primary_disease": str,         # Raw class name or healthy
            "confidence": float,            # Confidence score between 0.0 and 1.0
            "severity": str,                # Severity level
            "status": str,                  # 'detected' or 'no_detection'
            "detections": [                 # List of detected bounding boxes
                {
                    "class_id": int,
                    "disease": str,
                    "confidence": float,
                    "bbox": {"x1": float, "y1": float, "x2": float, "y2": float}
                }
            ],
            "recommendations": [...]        # Optional pre-filled or handled by prediction service
        }
        """
        pass
