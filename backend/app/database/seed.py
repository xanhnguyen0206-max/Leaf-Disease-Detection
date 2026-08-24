from app.database.session import SessionLocal, Base, engine
from app.database.models import Disease, CareRecommendation, DiagnosisHistory
from datetime import datetime, timezone

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Disease).first():
        db.close()
        return

    diseases_data = [
        {
            "id": "tomato_early_blight",
            "name": "Bệnh úa sớm cà chua (Early Blight)",
            "plant": "Cà chua",
            "severity": "Trung bình",
            "description": "Nấm Alternaria solani gây ra các vết đốm sẫm màu với các vòng tròn đồng tâm, dẫn đến rụng lá và giảm năng suất.",
            "symptoms": [
                "Vết đốm hình tròn màu nâu đen trên lá già",
                "Quầng vàng xung quanh các vết tổn thương",
                "Lá héo khô và rụng dần từ gốc lên ngọn"
            ],
            "image_url": "https://images.unsplash.com/photo-1592417817098-8f3d6eb1b7a5?w=600&auto=format&fit=crop",
            "care": [
                {"category": "Xử lý nguồn bệnh", "title": "Cắt tỉa lá bệnh", "description": "Loại bỏ và tiêu hủy toàn bộ các lá già ở tầng dưới có triệu chứng bệnh.", "priority": "high"},
                {"category": "Tưới nước", "title": "Tưới gốc không làm ướt lá", "description": "Sử dụng hệ thống tưới nhỏ giọt hoặc tưới trực tiếp vào gốc cây vào buổi sáng.", "priority": "high"},
                {"category": "Phòng trừ sinh học", "title": "Phun chế phẩm Trichoderma", "description": "Phun các bào tử nấm đối kháng Trichoderma định kỳ 7-10 ngày/lần.", "priority": "medium"}
            ]
        },
        {
            "id": "potato_late_blight",
            "name": "Bệnh sương mai khoai tây (Late Blight)",
            "plant": "Khoai tây",
            "severity": "Nghiêm trọng",
            "description": "Tác nhân Phytophthora infestans gây hoại tử lá nhanh chóng và thối củ tàn khốc trong điều kiện ẩm ướt.",
            "symptoms": [
                "Vết đốm mọng nước màu xanh tái ở mép lá",
                "Lớp mốc trắng như nhung ở mặt dưới lá vào buổi sáng",
                "Thân cây bị thâm đen và gãy gập"
            ],
            "image_url": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&auto=format&fit=crop",
            "care": [
                {"category": "Thuốc bảo vệ thực vật", "title": "Phun gốc Đồng sulfat / Mancozeb", "description": "Phun thuốc trừ nấm gốc Đồng hoặc Mancozeb ngay khi xuất hiện thời tiết nồm ẩm.", "priority": "high"},
                {"category": "Thông gió", "title": "Tăng khoảng cách hàng cây", "description": "Tăng luồng không khí lưu thông xung quanh tán lá bằng cách vặt bớt chồi phụ.", "priority": "medium"}
            ]
        },
        {
            "id": "apple_powdery_mildew",
            "name": "Bệnh phấn trắng táo (Powdery Mildew)",
            "plant": "Táo",
            "severity": "Trung bình",
            "description": "Nấm Podosphaera leucotricha tạo lớp bột màu trắng xám trên bề mặt lá và chồi non, làm xoắn lá.",
            "symptoms": [
                "Lớp bột mịn màu trắng phủ trên mặt lá",
                "Lá non bị mỏng, cong queo và dị dạng",
                "Chồi phát triển chậm và thoái hóa"
            ],
            "image_url": "https://images.unsplash.com/photo-1567306301408-9b74779a11af?w=600&auto=format&fit=crop",
            "care": [
                {"category": "Xử lý tự nhiên", "title": "Phun dung dịch baking soda hoặc sữa tươi", "description": "Pha dung dịch sữa tươi 10% hoặc baking soda phun đều lên 2 mặt lá.", "priority": "medium"},
                {"category": "Tỉa cành", "title": "Tỉa thông thoáng tán cây", "description": "Tắt bớt cành vượt giúp ánh nắng chiếu sâu vào lòng tán.", "priority": "low"}
            ]
        },
        {
            "id": "corn_common_rust",
            "name": "Bệnh rỉ sắt ngô (Common Rust)",
            "plant": "Ngô",
            "severity": "Nhẹ",
            "description": "Nấm Puccinia sorghi gây ra các ổ bọc nổi màu nâu đỏ trên cả hai mặt lá ngô.",
            "symptoms": [
                "Các mụn nhỏ li ti màu vàng sẫm hoặc nâu rỉ sắt",
                "Mụn vỡ ra giải phóng bột bào tử màu nâu",
                "Lá bị khô cháy sớm khi nấm phát triển mạnh"
            ],
            "image_url": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=600&auto=format&fit=crop",
            "care": [
                {"category": "Dinh dưỡng", "title": "Bổ sung Kali và Canxi", "description": "Tăng cường sức đề kháng cho vách tế bào bằng phân bón lá giàu Kali.", "priority": "medium"}
            ]
        }
    ]

    for d_item in diseases_data:
        care_items = d_item.pop("care")
        disease = Disease(**d_item)
        db.add(disease)
        db.commit()

        for c_item in care_items:
            care = CareRecommendation(disease_id=disease.id, **c_item)
            db.add(care)
        db.commit()

    sample_history = DiagnosisHistory(
        plant="Cà chua",
        disease="Bệnh úa sớm cà chua (Early Blight)",
        confidence=0.947,
        severity="Trung bình",
        image_url="https://images.unsplash.com/photo-1592417817098-8f3d6eb1b7a5?w=600&auto=format&fit=crop",
        heatmap_url=None,
        recommendations=[
            {"title": "Cắt tỉa lá bệnh", "description": "Loại bỏ các lá già ở tầng dưới có vết đốm."},
            {"title": "Tưới nước hợp lý", "description": "Tránh làm ướt bề mặt lá vào buổi tối."}
        ],
        created_at=datetime.now(timezone.utc)
    )
    db.add(sample_history)
    db.commit()
    db.close()
