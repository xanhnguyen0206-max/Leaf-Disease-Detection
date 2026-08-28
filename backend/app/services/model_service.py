import random
import logging
from typing import Dict, Any, Optional
from app.services.base_model_service import BaseModelService
from app.core.config import settings

logger = logging.getLogger(__name__)

class MockModelService(BaseModelService):
    def __init__(self):
        self.classes = [
            {
                "plant": "Cà chua",
                "disease": "Bệnh úa sớm cà chua (Early Blight)",
                "primary_disease": "Tomato___Early_blight",
                "severity": "Trung bình",
                "recommendations": [
                    {"title": "Cắt tỉa lá bệnh", "description": "Cắt bỏ ngay các lá xuất hiện đốm nâu đồng tâm để tránh bào tử lây lan."},
                    {"title": "Tưới nước nhỏ giọt", "description": "Chỉ tưới ẩm gốc cây, giữ lá hoàn toàn khô ráo."},
                    {"title": "Phun chế phẩm nấm đối kháng", "description": "Sử dụng nấm Trichoderma định kỳ 7 ngày/lần."}
                ]
            },
            {
                "plant": "Cà chua",
                "disease": "Bệnh đốm vi khuẩn cà chua (Bacterial Spot)",
                "primary_disease": "Tomato___Bacterial_spot",
                "severity": "Nghiêm trọng",
                "recommendations": [
                    {"title": "Phun thuốc gốc Đồng", "description": "Sử dụng chế phẩm diệt khuẩn gốc Đồng phun đều mặt lá."},
                    {"title": "Cách ly cây bệnh", "description": "Tránh tưới nước bắn lên tán lá để ngăn vi khuẩn lây lan."}
                ]
            },
            {
                "plant": "Cà chua",
                "disease": "Bệnh sương mai cà chua (Late Blight)",
                "primary_disease": "Tomato___Late_blight",
                "severity": "Nghiêm trọng",
                "recommendations": [
                    {"title": "Phun thuốc gốc Đồng / Mancozeb", "description": "Sử dụng Bordeaux hoặc Mancozeb phun phủ đều tán lá."},
                    {"title": "Cải thiện thông gió", "description": "Tỉa thông thoáng tán cây để giảm độ ẩm ướt."}
                ]
            },
            {
                "plant": "Cà chua",
                "disease": "Cây khỏe mạnh (Không phát hiện bệnh)",
                "primary_disease": "Healthy",
                "severity": "Khỏe mạnh",
                "recommendations": [
                    {"title": "Duy trì chế độ chăm sóc", "description": "Tán lá hoàn toàn khỏe mạnh, tiếp tục duy trì tưới nước và phân bón định kỳ."},
                    {"title": "Theo dõi định kỳ", "description": "Chụp ảnh kiểm tra lại sau 14 ngày."}
                ]
            }
        ]

    def predict(self, image_path: str, conf_threshold: Optional[float] = None) -> Dict[str, Any]:
        # Simulate AI inference logic
        result = random.choice(self.classes)
        confidence = round(random.uniform(0.88, 0.98), 4)
        is_healthy = result["primary_disease"] == "Healthy"
        
        detections = []
        if not is_healthy:
            detections.append({
                "class_id": 1 if "Early" in result["primary_disease"] else (0 if "Bacterial" in result["primary_disease"] else 2),
                "disease": result["primary_disease"],
                "confidence": confidence,
                "bbox": {"x1": 100.0, "y1": 100.0, "x2": 300.0, "y2": 300.0}
            })

        return {
            "plant": result["plant"],
            "disease": result["disease"],
            "primary_disease": result["primary_disease"],
            "confidence": 0.0 if is_healthy else confidence,
            "severity": result["severity"],
            "status": "no_detection" if is_healthy else "detected",
            "detections": detections,
            "recommendations": result["recommendations"]
        }

# Global instances for reuse
_yolo_instance: Optional[BaseModelService] = None
_mock_instance: Optional[MockModelService] = None

def get_model_service(model_type: Optional[str] = None) -> BaseModelService:
    """
    Factory function returning the configured model service instance.
    Loads YOLOModelService or MockModelService as a singleton.
    """
    global _yolo_instance, _mock_instance
    target_type = (model_type or settings.MODEL_TYPE).strip().lower()

    if target_type == "mock":
        if _mock_instance is None:
            _mock_instance = MockModelService()
        return _mock_instance
    elif target_type == "yolo":
        if _yolo_instance is None:
            from app.services.yolo_model_service import YOLOModelService
            _yolo_instance = YOLOModelService()
        return _yolo_instance
    else:
        logger.warning(f"Unknown MODEL_TYPE '{target_type}', falling back to YOLOModelService.")
        if _yolo_instance is None:
            from app.services.yolo_model_service import YOLOModelService
            _yolo_instance = YOLOModelService()
        return _yolo_instance

# Default model service instance for backward compatibility
class _ModelServiceProxy(BaseModelService):
    def predict(self, image_path: str, conf_threshold: Optional[float] = None) -> Dict[str, Any]:
        return get_model_service().predict(image_path, conf_threshold=conf_threshold)

model_service = _ModelServiceProxy()

