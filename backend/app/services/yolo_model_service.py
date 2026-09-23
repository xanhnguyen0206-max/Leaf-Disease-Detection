import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from ultralytics import YOLO
from app.services.base_model_service import BaseModelService
from app.core.config import settings

logger = logging.getLogger(__name__)

# Default Class ID to name mapping for tomato disease detector
TOMATO_CLASSES = {
    0: "Tomato___Bacterial_spot",
    1: "Tomato___Early_blight",
    2: "Tomato___Late_blight",
    3: "Tomato___Septoria_leaf_spot",
    4: "Tomato___Leaf_mold",
    5: "Tomato___Powdery_mildew"
}

# Human-friendly Vietnamese display names
TOMATO_DISPLAY_NAMES = {
    "Tomato___Bacterial_spot": "Bệnh đốm vi khuẩn cà chua (Bacterial Spot)",
    "Tomato___Early_blight": "Bệnh úa sớm cà chua (Early Blight)",
    "Tomato___Late_blight": "Bệnh sương mai cà chua (Late Blight)",
    "Tomato___Septoria_leaf_spot": "Bệnh đốm mắt cua cà chua (Septoria Leaf Spot)",
    "Tomato___Leaf_mold": "Bệnh nấm mốc lá cà chua (Leaf Mold)",
    "Tomato___Powdery_mildew": "Bệnh phấn trắng cà chua (Powdery Mildew)",
    "Healthy": "Không phát hiện dấu hiệu bệnh rõ ràng",
    "no_detection": "Không phát hiện dấu hiệu bệnh rõ ràng"
}

class YOLOModelService(BaseModelService):
    def __init__(
        self,
        model_path: Optional[str] = None,
        default_conf: Optional[float] = None,
        device: Optional[str] = None,
        imgsz: Optional[int] = None
    ):
        self.model_path = model_path or settings.MODEL_PATH
        self.conf_threshold = default_conf if default_conf is not None else settings.MODEL_CONFIDENCE_THRESHOLD
        self.device = device or settings.MODEL_DEVICE
        self.imgsz = imgsz or settings.MODEL_IMG_SIZE
        self.model: Optional[YOLO] = None
        self.classes: Dict[int, str] = dict(TOMATO_CLASSES)
        self._load_model()

    def _load_model(self):
        """Loads the YOLO model into memory once, loads classes.json if available, and verifies weights exist."""
        if not os.path.exists(self.model_path):
            abs_path = os.path.abspath(self.model_path)
            error_msg = f"YOLO model file not found at path: '{self.model_path}' (Absolute: '{abs_path}'). Please verify model weights exist."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Check adjacent classes.json metadata if available
        model_dir = Path(self.model_path).parent
        classes_json_path = model_dir / "classes.json"
        if classes_json_path.exists():
            try:
                with open(classes_json_path, "r", encoding="utf-8") as f:
                    raw_classes = json.load(f)
                    self.classes = {int(k): v for k, v in raw_classes.items()}
                logger.info(f"Loaded {len(self.classes)} classes from {classes_json_path}")
            except Exception as e:
                logger.warning(f"Could not parse {classes_json_path}: {e}. Using default class mapping.")

        try:
            logger.info(f"Loading YOLO model weights from: {self.model_path} (imgsz={self.imgsz}) on device: {self.device}")
            self.model = YOLO(self.model_path)
            
            # Sync model class names if available
            if hasattr(self.model, "names") and self.model.names:
                for cid, cname in self.model.names.items():
                    self.classes[int(cid)] = cname
                    
            logger.info(f"Successfully loaded YOLO model into memory. Registered classes: {self.classes}")
        except Exception as e:
            error_msg = f"Failed to initialize YOLO model from '{self.model_path}': {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def postprocess_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extensible post-processing hook for bounding boxes:
        - Filters invalid / degenerate bounding boxes
        - Enables future extension: leaf region filtering, tiny bbox filtering, background filtering
        """
        valid_detections = []
        for det in detections:
            bbox = det.get("bbox", {})
            x1, y1, x2, y2 = bbox.get("x1", 0), bbox.get("y1", 0), bbox.get("x2", 0), bbox.get("y2", 0)
            
            # Discard inverted or 0-area boxes
            if x2 <= x1 or y2 <= y1:
                continue
                
            valid_detections.append(det)
            
        return valid_detections

    def predict(self, image_path: str, conf_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Runs YOLO object detection on the given image path at configured resolution.
        """
        if self.model is None:
            raise RuntimeError("YOLO model is not loaded.")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        conf = conf_threshold if conf_threshold is not None else self.conf_threshold

        try:
            results = self.model.predict(
                source=image_path,
                conf=conf,
                imgsz=self.imgsz,
                device=self.device,
                verbose=False
            )
        except Exception as e:
            logger.error(f"Error during YOLO model inference on '{image_path}': {str(e)}")
            raise RuntimeError(f"YOLO inference failed: {str(e)}") from e

        raw_detections: List[Dict[str, Any]] = []

        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf_val = float(box.conf[0].item())
                    disease_name = self.classes.get(cls_id, self.model.names.get(cls_id, f"Class_{cls_id}"))
                    
                    xyxy = box.xyxy[0].tolist()
                    bbox = {
                        "x1": round(float(xyxy[0]), 2),
                        "y1": round(float(xyxy[1]), 2),
                        "x2": round(float(xyxy[2]), 2),
                        "y2": round(float(xyxy[3]), 2)
                    }

                    raw_detections.append({
                        "class_id": cls_id,
                        "disease": disease_name,
                        "confidence": round(conf_val, 4),
                        "bbox": bbox
                    })

        # Apply post-processing filtering hook
        detections = self.postprocess_detections(raw_detections)

        # Sort detections descending by confidence
        detections.sort(key=lambda d: d["confidence"], reverse=True)

        if detections:
            # Aggregate detection counts/confidences by disease
            disease_scores: Dict[str, float] = {}
            for d in detections:
                dname = d["disease"]
                disease_scores[dname] = disease_scores.get(dname, 0.0) + d["confidence"]
            
            # Primary disease is chosen by highest top confidence
            primary_detection = detections[0]
            primary_disease = primary_detection["disease"]
            primary_confidence = primary_detection["confidence"]
            status = "detected"
            display_disease = TOMATO_DISPLAY_NAMES.get(primary_disease, primary_disease)
            plant_name = "Cà chua"
        else:
            primary_disease = "Healthy"
            primary_confidence = 0.0
            status = "no_detection"
            display_disease = TOMATO_DISPLAY_NAMES["no_detection"]
            plant_name = "Cà chua"

        return {
            "plant": plant_name,
            "disease": display_disease,
            "primary_disease": primary_disease,
            "confidence": primary_confidence,
            "status": status,
            "detections": detections
        }
