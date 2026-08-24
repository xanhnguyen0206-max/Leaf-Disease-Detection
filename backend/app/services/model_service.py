import random
from typing import Dict, Any

class MockModelService:
    def __init__(self):
        self.classes = [
            {
                "plant": "Cà chua",
                "disease": "Bệnh úa sớm cà chua (Early Blight)",
                "severity": "Trung bình",
                "recommendations": [
                    {"title": "Cắt tỉa lá bệnh", "description": "Cắt bỏ ngay các lá xuất hiện đốm nâu đồng tâm để tránh bào tử lây lan."},
                    {"title": "Tưới nước nhỏ giọt", "description": "Chỉ tưới ẩm gốc cây, giữ lá hoàn toàn khô ráo."},
                    {"title": "Phun chế phẩm nấm đối kháng", "description": "Sử dụng nấm Trichoderma định kỳ 7 ngày/lần."}
                ]
            },
            {
                "plant": "Khoai tây",
                "disease": "Bệnh sương mai khoai tây (Late Blight)",
                "severity": "Nghiêm trọng",
                "recommendations": [
                    {"title": "Phun thuốc gốc Đồng", "description": "Sử dụng Bordeaux hoặc Mancozeb phun phủ đều tán lá."},
                    {"title": "Cách ly khu vực trồng", "description": "Ngừng tưới phun sương và kiểm tra củ dưới đất."}
                ]
            },
            {
                "plant": "Táo",
                "disease": "Bệnh phấn trắng táo (Powdery Mildew)",
                "severity": "Trung bình",
                "recommendations": [
                    {"title": "Phun dung dịch Baking Soda", "description": "Pha 5g baking soda + 1 lít nước phun đều tán lá."},
                    {"title": "Tỉa thông thoáng tán", "description": "Loại bỏ cành rậm rạp để đón ánh nắng."}
                ]
            },
            {
                "plant": "Thực vật (Tán lá)",
                "disease": "Lá khỏe mạnh (Healthy)",
                "severity": "Khỏe mạnh",
                "recommendations": [
                    {"title": "Duy trì chế độ chăm sóc", "description": "Tán lá hoàn toàn khỏe mạnh, tiếp tục duy trì tưới nước và phân bón định kỳ."},
                    {"title": "Theo dõi định kỳ", "description": "Chụp ảnh kiểm tra lại sau 14 ngày."}
                ]
            }
        ]

    def predict(self, image_path: str) -> Dict[str, Any]:
        # Simulate AI inference logic
        result = random.choice(self.classes)
        confidence = round(random.uniform(0.88, 0.98), 3)
        
        return {
            "plant": result["plant"],
            "disease": result["disease"],
            "confidence": confidence,
            "severity": result["severity"],
            "recommendations": result["recommendations"]
        }

model_service = MockModelService()
