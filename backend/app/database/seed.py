import json
from sqlalchemy import text
from app.database.session import SessionLocal, Base, engine
from app.database.models import Disease, CareRecommendation, DiagnosisHistory
from datetime import datetime, timezone

def _ensure_schema_columns():
    """Migrate SQLite tables if new columns were added to models."""
    with engine.connect() as conn:
        try:
            # 1. diagnosis_history table migrations
            result = conn.execute(text("PRAGMA table_info(diagnosis_history)"))
            diag_cols = {row[1] for row in result.fetchall()}
            if diag_cols:
                if "primary_disease" not in diag_cols:
                    conn.execute(text("ALTER TABLE diagnosis_history ADD COLUMN primary_disease VARCHAR"))
                if "status" not in diag_cols:
                    conn.execute(text("ALTER TABLE diagnosis_history ADD COLUMN status VARCHAR DEFAULT 'detected'"))
                if "detections" not in diag_cols:
                    conn.execute(text("ALTER TABLE diagnosis_history ADD COLUMN detections JSON"))
                if "detected_diseases" not in diag_cols:
                    conn.execute(text("ALTER TABLE diagnosis_history ADD COLUMN detected_diseases JSON"))
                if "is_multi_disease" not in diag_cols:
                    conn.execute(text("ALTER TABLE diagnosis_history ADD COLUMN is_multi_disease BOOLEAN DEFAULT 0"))
                conn.commit()

            # 2. diseases table migrations
            result_dis = conn.execute(text("PRAGMA table_info(diseases)"))
            dis_cols = {row[1] for row in result_dis.fetchall()}
            if dis_cols:
                new_disease_cols = [
                    ("scientific_name", "VARCHAR"),
                    ("english_name", "VARCHAR"),
                    ("overview", "TEXT"),
                    ("pathogen", "VARCHAR"),
                    ("favorable_conditions", "VARCHAR"),
                    ("transmission", "JSON"),
                    ("risk_level_explanation", "TEXT"),
                    ("early_symptoms", "JSON"),
                    ("mid_symptoms", "JSON"),
                    ("severe_symptoms", "JSON"),
                    ("similar_diseases_diff", "JSON"),
                    ("prevention_before_planting", "JSON"),
                    ("prevention_during_growth", "JSON"),
                    ("water_management", "TEXT"),
                    ("nutrition_management", "TEXT"),
                    ("density_management", "TEXT"),
                    ("field_sanitation", "TEXT"),
                    ("pruning_guide", "TEXT"),
                    ("crop_rotation_guide", "TEXT"),
                    ("biological_control", "JSON"),
                    ("chemical_control_principles", "JSON"),
                    ("aftercare_monitoring", "JSON"),
                    ("common_mistakes", "JSON"),
                    ("when_to_seek_help", "TEXT"),
                    ("safety_notes", "TEXT"),
                    ("sources", "JSON"),
                ]
                for col_name, col_type in new_disease_cols:
                    if col_name not in dis_cols:
                        conn.execute(text(f"ALTER TABLE diseases ADD COLUMN {col_name} {col_type}"))
                conn.commit()
        except Exception as e:
            print(f"Schema migration notice: {e}")

def seed_database():
    Base.metadata.create_all(bind=engine)
    _ensure_schema_columns()
    db = SessionLocal()

    diseases_data = [
        {
            "id": "tomato_bacterial_spot",
            "name": "Bệnh đốm vi khuẩn cà chua",
            "scientific_name": "Xanthomonas hortorum pv. gardneri / Xanthomonas perforans",
            "english_name": "Bacterial Spot of Tomato",
            "plant": "Cà chua",
            "severity": "Nghiêm trọng",
            "description": "Vi khuẩn Xanthomonas spp. gây các vết đốm sũng nước nhỏ màu nâu đen, quầng vàng, làm suy kiệt tán lá và rụng hoa quả non.",
            "overview": "Bệnh đốm vi khuẩn là một trong những bệnh truyền nhiễm nguy hiểm nhất trên cây cà chua tại các vùng khí hậu nhiệt đới và cận nhiệt đới ẩm. Bệnh tấn công tất cả các bộ phận trên mặt đất gồm lá, thân, cuống hoa và quả, làm giảm nghiêm trọng diện tích quang hợp và chất lượng thương phẩm.",
            "pathogen": "Vi khuẩn Gram âm Xanthomonas spp. (X. perforans, X. gardneri, X. vesicatoria)",
            "favorable_conditions": "Nhiệt độ ấm 24°C - 30°C, độ ẩm không khí cao >85%, mưa rào kèm gió lớn hoặc sử dụng hệ thống tưới phun mưa trên cao.",
            "transmission": [
                "Hạt giống hoặc cây con ươm nhiễm mầm bệnh ban đầu",
                "Tàn dư cây trồng vụ trước chưa phân hủy trong đất",
                "Nước bắn từ mưa hoặc hệ thống tưới phun mưa",
                "Dụng cụ cắt tỉa và tay người thao tác khi tán lá còn ẩm ướt"
            ],
            "risk_level_explanation": "Mức độ Nghiêm trọng: Bệnh lây lan theo cấp số nhân trong mùa mưa, có thể làm rụng tới 70-90% tán lá và gây cháy hoa làm mất trắng năng suất nếu không kiểm soát sớm.",
            "symptoms": [
                "Vết đốm nhỏ 1-3mm màu nâu đen ngậm nước ở hai mặt lá",
                "Viền lá xuất hiện vết cháy sém hoặc quầng vàng",
                "Lá biến dạng, khô giòn và rụng hàng loạt"
            ],
            "early_symptoms": [
                "Xuất hiện các đốm nhỏ li ti 1-2mm dạng sũng nước (water-soaked) ở mặt dưới lá già",
                "Mép lá có biểu hiện héo nhẹ từng chấm nhỏ"
            ],
            "mid_symptoms": [
                "Các đốm mở rộng lên 3-5mm, chuyển sang màu nâu sẫm hoặc đen với quầng vàng sáng bao quanh",
                "Tâm vết bệnh bị khô và rách lỗ chỗ (hiệu ứng thủng lá - shot hole)"
            ],
            "severe_symptoms": [
                "Các vết bệnh liên kết lại thành mảng cháy lớn, toàn bộ lá vàng khô và rụng trơ cành",
                "Cuống hoa bị thâm đen gây rụng hoa; quả non xuất hiện đốm đen dạng vảy sần sùi đường kính 3-6mm"
            ],
            "similar_diseases_diff": [
                "Phân biệt với Bệnh úa sớm: Vết đốm vi khuẩn nhỏ hơn, không có các vòng tròn đồng tâm đặc trưng như nấm Alternaria.",
                "Phân biệt với Đốm mắt cua (Septoria): Đốm Septoria thường có tâm màu xám trắng với viền đen rất mỏng."
            ],
            "prevention_before_planting": [
                "Chỉ sử dụng hạt giống sạch bệnh đã qua xử lý nhiệt (50°C trong 25 phút) hoặc ngâm dung dịch khử trùng theo chuẩn",
                "Khử trùng khay ươm, giá thể và nhà lưới trước khi gieo trồng",
                "Luân canh với cây trồng không cùng ký chủ (ngô, lúa, đậu đỗ) tối thiểu 2-3 năm"
            ],
            "prevention_during_growth": [
                "Sử dụng hệ thống tưới nhỏ giọt dưới gốc, tuyệt đối không tưới phun mưa làm ướt tán lá",
                "Duy trì khoảng cách trồng thông thoáng (hàng cách hàng 70cm, cây cách cây 50cm)",
                "Không tỉa cành hoặc làm cỏ khi tán lá còn ướt sương sáng"
            ],
            "water_management": "Tưới nước nhỏ giọt vào buổi sáng sớm tại vùng rễ, kiểm soát độ ẩm nhà màng dưới 80%, không để nước đọng trên bề mặt lá quá 2 giờ.",
            "nutrition_management": "Bón phân cân đối N-P-K. Tránh bón thừa đạm (N) làm mỏng vách tế bào lá; tăng cường Canxi (Ca) và Silic (Si) để gia cố lớp biểu bì.",
            "density_management": "Mật độ khuyến cáo 2.800 - 3.200 cây/1.000m². Tỉa bớt lá già sát mặt đất để tăng lưu thông không khí.",
            "field_sanitation": "Thu gom toàn bộ lá bệnh rụng và chồi tỉa cho vào túi kín đem tiêu hủy xa ruộng trồng, không ủ phân hữu cơ lộ thiên từ tàn dư bệnh.",
            "pruning_guide": "Khử trùng kéo cắt bằng cồn 70 độ hoặc dung dịch Javel pha loãng 1% sau mỗi hàng cây. Chỉ cắt tỉa vào ngày nắng ráo từ 9h sáng đến 3h chiều.",
            "crop_rotation_guide": "Luân canh tối thiểu 2 năm với các cây họ Hòa thảo (ngô, lúa) hoặc họ Đậu. Không luân canh với ớt, cà tím, khoai tây.",
            "biological_control": [
                "Phun định kỳ chế phẩm vi khuẩn đối kháng Bacillus subtilis hoặc Bacillus amyloliquefaciens khi cây con ra ngôi",
                "Ứng dụng Bacteriophage (thực khuẩn thể đặc hiệu Xanthomonas) nếu có điều kiện tiếp cận nguồn sinh học đã đăng ký"
            ],
            "chemical_control_principles": [
                "Khi bệnh chớm xuất hiện: Sử dụng các chế phẩm gốc Đồng (Copper Hydroxide, Copper Oxychloride) luân phiên hoặc phối hợp Mancozeb theo đúng hướng dẫn trên nhãn sản phẩm được cơ quan chức năng địa phương cấp phép.",
                "Tuân thủ nghiêm ngặt thời gian cách ly (PHI) và nguyên tắc 4 đúng (Đúng thuốc, đúng liều, đúng lúc, đúng cách).",
                "Tránh phun thuốc gốc đồng liên tục trong thời tiết nắng gắt trên 32°C vì dễ gây độc cho cây (cháy viền lá)."
            ],
            "aftercare_monitoring": [
                "Kiểm tra lại mặt dưới lá sau 5-7 ngày xử lý",
                "Theo dõi các lá non mới ra xem có xuất hiện đốm nước mới hay không"
            ],
            "common_mistakes": [
                "Lầm tưởng là nấm bệnh và chỉ phun thuốc trừ nấm phổ hẹp (không có tác dụng diệt khuẩn)",
                "Tưới phun mưa vào chiều tối khiến lá ướt suốt đêm tạo điều kiện vi khuẩn xâm nhập khí khổng",
                "Cắt tỉa cành hàng loạt khi trời đang mưa ẩm"
            ],
            "when_to_seek_help": "Khi bệnh lan nhanh hơn 30% diện tích vườn trong vòng 48 giờ sau mưa bão, cần liên hệ cán bộ khuyến nông hoặc trạm bảo vệ thực vật địa phương.",
            "safety_notes": "Trang bị đầy đủ bảo hộ lao động (khẩu trang, găng tay, kính mắt) khi pha chế và phun thuốc BVTV. Rửa sạch bình phun và thu gom bao bì đúng nơi quy định.",
            "sources": [
                "FAO Plant Production and Protection Series - Integrated Pest Management for Tomato",
                "University of California Statewide Integrated Pest Management Program (UC IPM) - Tomato Bacterial Spot",
                "Cornell Cooperative Extension - Vegetable MD Online: Bacterial Diseases of Tomato",
                "EPPO Global Database - Xanthomonas hortorum pv. gardneri / Xanthomonas perforans"
            ],
            "image_url": "/images/diseases/tomato_bacterial_spot.jpg",
            "care": [
                {"category": "Thuốc bảo vệ thực vật", "title": "Phun chế phẩm gốc Đồng theo nhãn", "description": "Sử dụng chế phẩm gốc Đồng (Copper Hydroxide) được đăng ký hợp pháp, phun phủ đều khi bệnh chớm xuất hiện.", "priority": "high"},
                {"category": "Vệ sinh đồng ruộng", "title": "Thu gom tiêu hủy tàn dư bệnh", "description": "Tỉa bỏ các lá già bệnh dưới gốc, gom vào túi kín tiêu hủy, tránh để bào tử khuẩn lây lan.", "priority": "high"},
                {"category": "Biện pháp canh tác", "title": "Chuyển sang tưới nhỏ giọt", "description": "Tưới nước tại gốc, giữ lá khô ráo, tránh làm văng đất chứa vi khuẩn lên tán lá.", "priority": "medium"}
            ]
        },
        {
            "id": "tomato_early_blight",
            "name": "Bệnh úa sớm cà chua",
            "scientific_name": "Alternaria solani / Alternaria linariae",
            "english_name": "Early Blight of Tomato / Target Spot",
            "plant": "Cà chua",
            "severity": "Trung bình",
            "description": "Nấm Alternaria solani gây các vết đốm nâu đen có vòng tròn đồng tâm hình bia bắn, gây rụng lá từ gốc lên ngọn và thối cuống quả.",
            "overview": "Bệnh úa sớm (Early Blight) là bệnh phổ biến bậc nhất trên cây họ Cà. Nấm bệnh tấn công chủ yếu trên các lá già ở tầng dưới khi cây bắt đầu mang quả, làm giảm khả năng nuôi quả và khiến quả bị rám nắng do mất bóng râm của tán lá.",
            "pathogen": "Nấm bất toàn Alternaria solani Sorauer",
            "favorable_conditions": "Nhiệt độ 24°C - 29°C, xen kẽ giữa giai đoạn khô ráo và các đợt mưa phùn ẩm ướt, sương mù kéo dài hoặc đọng sương ban đêm.",
            "transmission": [
                "Bào tử phân sinh phát tán theo gió và giọt nước mưa bắn",
                "Tồn dư trong xác bã thực vật vụ trước và cỏ dại họ Cà",
                "Hạt giống nhiễm nấm trên vỏ hạt"
            ],
            "risk_level_explanation": "Mức độ Trung bình đến Cao: Nếu không can thiệp, bệnh sẽ làm trơ trụi toàn bộ lá tầng dưới và giữa, quả bị thối đen phần cuống làm giảm 30-50% sản lượng.",
            "symptoms": [
                "Vết đốm hình tròn màu nâu đen trên lá già",
                "Vòng tròn đồng tâm đặc trưng dạng hình bia bắn",
                "Lá héo vàng và rụng dần từ gốc lên ngọn"
            ],
            "early_symptoms": [
                "Các chấm nhỏ màu nâu sẫm xuất hiện trên những lá già sát mặt đất",
                "Vết đốm bắt đầu mở rộng thành hình tròn hoặc bầu dục đường kính 3-5mm"
            ],
            "mid_symptoms": [
                "Hình thành các vân vòng tròn đồng tâm (concentric rings) rất rõ như hình bia bắn",
                "Quầng lá xung quanh vết bệnh chuyển sang màu vàng sáng (chlorosis)"
            ],
            "severe_symptoms": [
                "Nhiều vết đốm liên kết lại làm toàn bộ phiến lá khô giòn, gãy cụt",
                "Vết bệnh loét sâu trên thân cây màu nâu đen lõm vào; cuống quả bị thối đen làm rụng quả hàng loạt"
            ],
            "similar_diseases_diff": [
                "Phân biệt với Bệnh sương mai: Úa sớm có vòng tròn đồng tâm khô ráo, không xuất hiện lớp mốc trắng như nhung ở mặt dưới lá.",
                "Phân biệt với Đốm vi khuẩn: Vết bệnh úa sớm lớn hơn nhiều (5-15mm) và có vân đồng tâm đặc trưng."
            ],
            "prevention_before_planting": [
                "Sử dụng giống cà chua có tính chống chịu hoặc kháng nấm Alternaria",
                "Xử lý đất kỹ bằng vôi bột hoặc phơi ải diệt nguồn nấm trước khi trồng",
                "Phủ luống bằng màng phủ nilon nông nghiệp để ngăn nấm từ đất bắn lên lá khi trời mưa"
            ],
            "prevention_during_growth": [
                "Tỉa sạch toàn bộ các lá già sát mặt đất (cách mặt luống 20-30cm) sau khi cây bén rễ hồi xanh",
                "Bón phân cân đối, cung cấp đủ Kali và Silic giúp thành tế bào lá dày dặn",
                "Tránh bón thừa đạm làm tán lá rậm rạp ẩm ướt"
            ],
            "water_management": "Tưới nước nhỏ giọt vào sáng sớm để bề mặt đất khô ráo trước khi đêm xuống. Tránh tưới phun mưa.",
            "nutrition_management": "Bổ sung phân bón hữu cơ hoai mục, duy trì tỷ lệ N:K hợp lý 1:1.5 trong giai đoạn nuôi quả.",
            "density_management": "Duy trì mật độ hàng kép hoặc hàng đơn hợp lý, khoảng cách cây tối thiểu 45-50cm.",
            "field_sanitation": "Thường xuyên thu gom lá già rụng, dọn sạch cỏ dại họ Cà (cà dại, cỏ tầm bóp) xung quanh vườn.",
            "pruning_guide": "Tỉa cành phụ (chồi nách) định kỳ, giữ cho thân chính thông thoáng đón ánh sáng mặt trời.",
            "crop_rotation_guide": "Luân canh 2-3 vụ với cây họ Thập tự (bắp cải, súp lơ), họ Hành tỏi hoặc họ Đậu.",
            "biological_control": [
                "Sử dụng nấm đối kháng Trichoderma harzianum tưới gốc và phun tán định kỳ 10-14 ngày/lần",
                "Phun chế phẩm sinh học chứa Bacillus velezensis hoặc dịch chiết xuất từ tỏi/neem phòng ngừa sớm"
            ],
            "chemical_control_principles": [
                "Sử dụng thuốc BVTV gốc hoạt chất tiếp xúc (Mancozeb, Chlorothalonil) hoặc hoạt chất lưu dẫn (Azoxystrobin, Difenoconazole) được phép lưu hành khi thời tiết có độ ẩm cao.",
                "Tuân thủ nghiêm ngặt thời gian cách ly (PHI) và liều lượng hướng dẫn trên nhãn."
            ],
            "aftercare_monitoring": [
                "Kiểm tra tán lá dưới định kỳ 2 lần/tuần",
                "Theo dõi tốc độ khô của các vết đốm cũ sau khi phun thuốc"
            ],
            "common_mistakes": [
                "Để lá già tiếp xúc trực tiếp với mặt đất ẩm",
                "Bón phân đạm quá mức khiến cây ra lá non mềm yếu dễ nhiễm nấm",
                "Không dọn tàn dư sau thu hoạch khiến nấm lưu tồn sang vụ sau"
            ],
            "when_to_seek_help": "Khi vết bệnh lan lên tầng lá thứ 3 và xuất hiện vết loét trên thân chính, cần tham vấn chuyên gia BVTV để có giải pháp chặn đứng dịch hại.",
            "safety_notes": "Đảm bảo trang bị bảo hộ lao động đầy đủ, không phun ngược chiều gió và không xả nước thải bình phun ra nguồn nước sinh hoạt.",
            "sources": [
                "FAO Integrated Pest Management Guidelines for Protected Cultivation",
                "University of Florida IFAS Extension - Early Blight of Tomato (EDIS Publication PP348)",
                "Purdue University Extension - Tomato Diseases: Early Blight (BP-141-W)",
                "CABI Digital Library - Alternaria solani Datasheet"
            ],
            "image_url": "/images/diseases/tomato_early_blight.jpg",
            "care": [
                {"category": "Xử lý nguồn bệnh", "title": "Cắt tỉa lá già dưới gốc", "description": "Tỉa bỏ toàn bộ lá già ở tầng dưới cách mặt đất 25cm để ngăn nấm từ đất lây lên.", "priority": "high"},
                {"category": "Tưới nước", "title": "Tưới gốc nhỏ giọt", "description": "Chỉ tưới dưới gốc cây vào buổi sáng, giữ tán lá hoàn toàn khô ráo.", "priority": "high"},
                {"category": "Phòng trừ sinh học", "title": "Ứng dụng Trichoderma", "description": "Sử dụng chế phẩm nấm đối kháng Trichoderma tưới gốc định kỳ 10 ngày/lần.", "priority": "medium"}
            ]
        },
        {
            "id": "tomato_late_blight",
            "name": "Bệnh sương mai cà chua",
            "scientific_name": "Phytophthora infestans",
            "english_name": "Late Blight of Tomato",
            "plant": "Cà chua",
            "severity": "Nghiêm trọng",
            "description": "Nấm noãn Phytophthora infestans phát triển bùng phát trong thời tiết lạnh ẩm sương mù, làm cháy rụi toàn bộ tán lá và thối cứng quả cà chua.",
            "overview": "Bệnh sương mai (Late Blight) là dịch hại nguy hiểm nhất trong lịch sử nông nghiệp trên cây cà chua và khoai tây. Trong điều kiện thời tiết thuận lợi (mát mẻ, sương mù, mưa dầm), mầm bệnh có thể phá hủy hoàn toàn một ruộng cà chua chỉ trong vòng 5-7 ngày.",
            "pathogen": "Oomycete (Nấm noãn) Phytophthora infestans (Mont.) de Bary",
            "favorable_conditions": "Nhiệt độ mát mẻ 15°C - 22°C kết hợp độ ẩm không khí rất cao >90%, sương mù dày đặc hoặc mưa phùn kéo dài nhiều ngày.",
            "transmission": [
                "Bào tử phân sinh và bào tử du động phát tán theo gió xa hàng chục kilômét",
                "Nước mưa và dòng nước tưới tràn",
                "Lây chéo từ các ruộng khoai tây hoặc cà chua lân cận"
            ],
            "risk_level_explanation": "Mức độ Cực kỳ nghiêm trọng: Bệnh có tốc độ lây lan nhanh như vũ bão, phá hủy cả lá, thân và quả, gây tổn thất 100% nếu không phun phòng kịp thời.",
            "symptoms": [
                "Vết đốm úng nước màu xanh xám loang lổ ở đầu và mép lá",
                "Lớp mốc trắng như sương tuyết ở mặt dưới lá trong điều kiện ẩm",
                "Thân và cuống lá xuất hiện vệt thâm đen, dễ gãy gập"
            ],
            "early_symptoms": [
                "Các đốm màu xanh nhạt hoặc xanh xám úng nước xuất hiện ở chóp hoặc mép của lá non phía trên",
                "Vết bệnh mở rộng nhanh chóng và không bị giới hạn bởi gân lá"
            ],
            "mid_symptoms": [
                "Vết bệnh chuyển sang màu nâu đen ướt sũng; sáng sớm có lớp mốc tơ trắng mịn ở mặt dưới lá",
                "Cuống lá và thân cây xuất hiện các vệt loét màu nâu đen bóng, giòn và dễ gãy"
            ],
            "severe_symptoms": [
                "Toàn bộ tán lá bị cháy sém và nhũn đen như bị nước sôi luộc chín",
                "Quả cà chua xuất hiện các mảng màu nâu sẫm, bề mặt chai cứng như da thuộc, quả rụng hàng loạt"
            ],
            "similar_diseases_diff": [
                "Phân biệt với Bệnh úa sớm: Sương mai lây lan cực nhanh, vết bệnh ủng nước và có mốc trắng mặt dưới lá, không có vòng tròn đồng tâm khô.",
                "Phân biệt với Đốm vi khuẩn: Sương mai tấn công cả ngọn non, vết bệnh lớn dạng loang lổ chứ không phải các đốm chấm nhỏ 1-3mm."
            ],
            "prevention_before_planting": [
                "Chọn các giống cà chua có gen kháng sương mai (như gen Ph-2, Ph-3)",
                "Trồng trên luống cao thoát nước tốt, che phủ nilon chống úng rễ",
                "Không trồng cà chua gần các cánh đồng khoai tây vụ đông xuân"
            ],
            "prevention_during_growth": [
                "Mở rộng thông gió tối đa trong nhà màng để giảm độ ẩm không khí",
                "Cắt tỉa bớt các cành phụ vô hiệu để tán lá nhận đủ ánh sáng mặt trời",
                "Thường xuyên theo dõi dự báo thời tiết để chủ động phòng ngừa trước các đợt không khí lạnh kèm sương mù"
            ],
            "water_management": "Chỉ tưới dưới gốc vào buổi sáng. Ngừng tưới tràn trong những ngày trời nồm ẩm sương mù.",
            "nutrition_management": "Tăng cường Kali và phân bón vi lượng chứa Kẽm (Zn), Đồng (Cu) để tăng sức đề kháng.",
            "density_management": "Khoảng cách hàng tối thiểu 70-80cm, cây cách cây 50cm để gió lưu thông tốt.",
            "field_sanitation": "Ngay khi phát hiện cây bệnh đầu tiên, phải nhổ bỏ cẩn thận cho vào túi nilon đem tiêu hủy ngay để tránh bào tử bay theo gió.",
            "pruning_guide": "Không tỉa cành khi trời mù sương ẩm ướt. Khử trùng dụng cụ kỹ càng.",
            "crop_rotation_guide": "Luân canh tối thiểu 3 năm với cây họ Hòa thảo, họ Bầu bí hoặc họ Thập tự.",
            "biological_control": [
                "Phun phòng ngừa bằng chế phẩm vi sinh chứa Bacillus subtilis hoặc Streptomyces spp.",
                "Phun dung dịch đồng sunfat sinh học hoặc tinh dầu thực vật phòng ngừa nấm bám dính"
            ],
            "chemical_control_principles": [
                "Phun thuốc phòng ngừa trước khi có đợt sương mù kéo dài bằng hoạt chất tiếp xúc (Mancozeb, Propineb).",
                "Khi bệnh chớm xuất hiện: Sử dụng các hoạt chất đặc trị nấm noãn (Metalaxyl, Cymoxanil, Dimethomorph, Fosetyl-Aluminium) được cấp phép theo đúng nhãn.",
                "Luân phiên các nhóm hoạt chất có cơ chế tác động khác nhau để chống hiện tượng nấm kháng thuốc (quản lý FRAC)."
            ],
            "aftercare_monitoring": [
                "Theo dõi vườn hàng ngày vào buổi sáng sớm",
                "Kiểm tra mặt dưới lá non xem còn lớp mốc trắng hay không"
            ],
            "common_mistakes": [
                "Chờ đến khi cả vườn bị cháy đen mới bắt đầu phun thuốc (quá muộn)",
                "Phun một loại hoạt chất liên tục nhiều lần gây lờn thuốc/kháng thuốc",
                "Vứt bỏ cây bệnh bừa bãi bên bờ mương khiến bào tử phát tán khắp vùng"
            ],
            "when_to_seek_help": "Bệnh sương mai là dịch hại khẩn cấp. Khi thấy lớp mốc trắng đầu tiên xuất hiện trong thời tiết nồm ẩm, cần thông báo ngay cho đội BVTV cơ sở.",
            "safety_notes": "Tuân thủ nghiêm ngặt thời gian cách ly để đảm bảo nông sản an toàn không tồn dư hóa chất khi thu hoạch.",
            "sources": [
                "FAO Global Initiative on Late Blight Management",
                "Cornell University - Late Blight Management Guide for Tomato & Potato",
                "European and Mediterranean Plant Protection Organization (EPPO) - Phytophthora infestans",
                "USDA ARS - Plant Disease Research: Late Blight Protocols"
            ],
            "image_url": "/images/diseases/tomato_late_blight.jpg",
            "care": [
                {"category": "Thuốc trừ nấm", "title": "Phun phòng ngừa theo nhãn", "description": "Sử dụng hoạt chất đặc trị nấm noãn được đăng ký (Mancozeb, Metalaxyl) phun trước đợt sương mù.", "priority": "high"},
                {"category": "Thông gió", "title": "Tối đa hóa độ thông thoáng", "description": "Cắt tỉa cành phụ, mở rộng cửa thông gió nhà màng để giảm độ ẩm dưới 85%.", "priority": "high"},
                {"category": "Tiêu hủy mầm bệnh", "title": "Cách ly cây nhiễm bệnh sớm", "description": "Nhổ bỏ cây nhiễm bệnh đầu tiên, bọc túi kín đem tiêu hủy tránh phát tán bào tử.", "priority": "high"}
            ]
        },
        {
            "id": "potato_late_blight",
            "name": "Bệnh sương mai khoai tây",
            "scientific_name": "Phytophthora infestans",
            "english_name": "Late Blight of Potato",
            "plant": "Khoai tây",
            "severity": "Nghiêm trọng",
            "description": "Tác nhân Phytophthora infestans gây hoại tử lá nhanh chóng và thối củ tàn khốc trong điều kiện ẩm ướt.",
            "overview": "Bệnh sương mai khoai tây là nguyên nhân chính gây ra nạn đói lịch sử tại châu Âu thế kỷ 19. Bệnh phá hủy toàn bộ diện tích lá trong thời gian ngắn và xâm nhập xuống củ làm củ bị thối nhũn và bốc mùi hôi thối trong quá trình bảo quản.",
            "pathogen": "Phytophthora infestans (Mont.) de Bary",
            "favorable_conditions": "Nhiệt độ 12°C - 20°C, độ ẩm không khí >90%, sương mù ẩm ướt kéo dài.",
            "transmission": [
                "Củ giống nhiễm bệnh mang mầm mống từ vụ trước",
                "Bào tử phân sinh bay theo gió từ các ruộng lân cận",
                "Nước mưa cuốn trôi bào tử từ lá xuống củ trong đất"
            ],
            "risk_level_explanation": "Mức độ Nghiêm trọng: Có thể làm giảm 80-100% sản lượng củ và lây lan trên diện rộng chỉ trong vài ngày thời tiết mưa phùn.",
            "symptoms": [
                "Vết đốm mọng nước màu xanh tái ở mép lá",
                "Lớp mốc trắng như nhung ở mặt dưới lá vào buổi sáng",
                "Thân cây bị thâm đen và củ bị thối nâu"
            ],
            "early_symptoms": [
                "Vết đốm ngậm nước màu xanh xám ở chóp và mép lá",
                "Lá hơi rũ xuống vào sáng sớm"
            ],
            "mid_symptoms": [
                "Vết bệnh chuyển sang màu nâu sẫm, viền úng nước lan rộng nhanh",
                "Lớp mốc tơ trắng mịn phát triển mạnh ở mặt dưới lá"
            ],
            "severe_symptoms": [
                "Toàn bộ thân lá thâm đen, gục ngã và thối rữa",
                "Vỏ củ khoai tây có vết nâu xám lõm vào, thịt củ bị thối nâu khô xốp hoặc thối ướt thứ cấp"
            ],
            "similar_diseases_diff": [
                "Phân biệt với Bệnh đốm vòng Alternaria: Sương mai lan nhanh hơn nhiều, vết bệnh ướt có mốc trắng thay vì vân đồng tâm khô."
            ],
            "prevention_before_planting": [
                "Chỉ sử dụng củ giống chứng nhận sạch bệnh",
                "Vun luống cao và phủ đất dày trên mặt củ để bào tử từ lá không thấm xuống củ khi mưa",
                "Tiêu hủy củ khoai tây phế phẩm và cây mọc tự nhiên quanh bờ ruộng"
            ],
            "prevention_during_growth": [
                "Theo dõi sát sao các đợt gió mùa đông bắc kèm mưa phùn để phun phòng sớm",
                "Cắt bỏ toàn bộ thân lá trước khi thu hoạch 10-14 ngày để vỏ củ dày và tránh bào tử bám vào củ"
            ],
            "water_management": "Tưới rãnh thấm hoặc tưới nhỏ giọt, thoát nước triệt để không để ứ đọng trên luống.",
            "nutrition_management": "Bón lót đầy đủ phân hữu cơ hoai mục và Kali, tránh bón thừa đạm.",
            "density_management": "Hàng cách hàng 60-70cm, cây cách cây 30cm.",
            "field_sanitation": "Dọn sạch cỏ dại và cây khoai tây sót sau mỗi vụ thu hoạch.",
            "pruning_guide": "Cắt tỉa cành gãy dập, thu gom tiêu hủy.",
            "crop_rotation_guide": "Luân canh với ngô, lúa nước hoặc đậu đỗ tối thiểu 3 vụ.",
            "biological_control": [
                "Ứng dụng chế phẩm sinh học đối kháng Bacillus subtilis tưới định kỳ"
            ],
            "chemical_control_principles": [
                "Phun thuốc phòng ngừa chứa hoạt chất Mancozeb, Chlorothalonil trước khi có mưa phùn.",
                "Khi bệnh xuất hiện: Luân phiên các nhóm thuốc đặc trị nấm noãn được cấp phép theo hướng dẫn trên nhãn."
            ],
            "aftercare_monitoring": [
                "Kiểm tra củ sau thu hoạch bảo quản ở nơi khô mát, loại bỏ ngay củ có dấu hiệu đốm nâu"
            ],
            "common_mistakes": [
                "Sử dụng củ thương phẩm trôi nổi không rõ nguồn gốc làm củ giống",
                "Vun luống quá nông khiến củ bị lộ ra ngoài dễ nhiễm nấm từ lá",
                "Thu hoạch ngay khi thân lá còn xanh nhiễm bệnh khiến bào tử dính vào củ"
            ],
            "when_to_seek_help": "Khi phát hiện các ổ dịch sương mai đầu tiên trên diện tích canh tác tập trung.",
            "safety_notes": "Tuân thủ nghiêm ngặt bảo hộ lao động và thời gian cách ly thuốc BVTV trước khi thu hoạch củ.",
            "sources": [
                "FAO Global Potato Late Blight Network (EuroBlight / AsiaBlight)",
                "International Potato Center (CIP) - Late Blight Management",
                "CABI Compendium - Phytophthora infestans"
            ],
            "image_url": "/images/diseases/potato_late_blight.jpg",
            "care": [
                {"category": "Thuốc bảo vệ thực vật", "title": "Phun phòng ngừa theo nhãn", "description": "Sử dụng chế phẩm đặc trị nấm noãn được cấp phép, phun phủ kín hai mặt lá khi thời tiết lạnh ẩm.", "priority": "high"},
                {"category": "Canh tác", "title": "Vun luống cao phủ dày đất", "description": "Vun đất cao che phủ củ sâu tối thiểu 10-15cm để ngăn bào tử nấm từ lá ngấm xuống củ.", "priority": "high"}
            ]
        },
        {
            "id": "apple_powdery_mildew",
            "name": "Bệnh phấn trắng táo",
            "scientific_name": "Podosphaera leucotricha",
            "english_name": "Apple Powdery Mildew",
            "plant": "Táo",
            "severity": "Trung bình",
            "description": "Nấm Podosphaera leucotricha tạo lớp bột màu trắng xám trên bề mặt lá và chồi non, làm xoắn lá và giảm quang hợp.",
            "overview": "Bệnh phấn trắng là bệnh hại phổ biến trên cây ăn quả thân gỗ như táo, lê. Bệnh làm biến dạng chồi non, cản trở quá trình ra hoa đậu quả và làm giảm chất lượng mẫu mã vỏ quả.",
            "pathogen": "Podosphaera leucotricha (Ellis & Everh.) E.S. Salmon",
            "favorable_conditions": "Nhiệt độ 19°C - 25°C, độ ẩm không khí cao vào ban đêm kết hợp ban ngày khô ráo, tán cây rậm rạp thiếu nắng.",
            "transmission": [
                "Sợi nấm qua đông trong chồi ngủ và phát triển khi chồi bung lộc xuân",
                "Bào tử phân sinh phát tán tự do theo gió"
            ],
            "risk_level_explanation": "Mức độ Trung bình: Làm chồi non ngừng phát triển, lá nhỏ cong queo, quả bị rám sần sùi (russeting) làm giảm giá trị thương phẩm.",
            "symptoms": [
                "Lớp bột mịn màu trắng phủ trên mặt lá",
                "Lá non bị mỏng, cong queo và dị dạng",
                "Chồi phát triển chậm và thoái hóa"
            ],
            "early_symptoms": [
                "Lớp màng bột trắng xám mỏng xuất hiện ở mặt dưới các lá non mới bung",
                "Rìa lá non hơi cong nhẹ lên phía trên"
            ],
            "mid_symptoms": [
                "Lớp phấn trắng bao phủ cả 2 mặt lá và bao bọc toàn bộ chồi ngọn non",
                "Lá trở nên cứng giòn, chuyển dần sang màu nâu nhạt"
            ],
            "severe_symptoms": [
                "Chồi non bị thui chột không thể vươn dài, lá rụng sớm",
                "Vỏ quả non bị phủ màng phấn, sau lớn lên tạo thành các vết nứt mạng nhện sần sùi"
            ],
            "similar_diseases_diff": [
                "Phân biệt với Bệnh ghẻ táo (Apple Scab): Ghẻ táo tạo vết đốm nâu đen dạng nhung ô liu, không có lớp phấn trắng mịn như bột mì."
            ],
            "prevention_before_planting": [
                "Lựa chọn các giống táo có tính kháng cao với nấm phấn trắng",
                "Trồng cây ở vị trí đón nhiều ánh sáng mặt trời chiếu trực tiếp và thông thoáng gió"
            ],
            "prevention_during_growth": [
                "Cắt tỉa các chồi bị nhiễm bệnh trong kỳ nghỉ đông trước khi cây đâm chồi xuân",
                "Tỉa mở rộng tán cây tạo hình dạng phễu hoặc chữ Y giúp ánh nắng chiếu vào lòng tán"
            ],
            "water_management": "Tưới gốc, duy trì độ ẩm đất ổn định, tránh để cây bị stress khô hạn.",
            "nutrition_management": "Bón phân hữu cơ vi sinh, không bón thừa đạm vào mùa phát lộc non.",
            "density_management": "Khoảng cách cây trong vườn tối thiểu 4-5m.",
            "field_sanitation": "Thu gom cành lá cắt tỉa đem tiêu hủy xa vườn.",
            "pruning_guide": "Thường xuyên kiểm tra và cắt bỏ các chồi trắng (primary mildew shoots) vào đầu mùa xuân.",
            "crop_rotation_guide": "Không áp dụng trực tiếp cho cây lâu năm; chú trọng vệ sinh vườn.",
            "biological_control": [
                "Phun dầu khoáng sinh học hoặc dầu hạt Neem được cấp phép",
                "Ứng dụng nấm đối kháng Ampelomyces quisqualis hoặc vi khuẩn Bacillus subtilis"
            ],
            "chemical_control_principles": [
                "Sử dụng các chế phẩm chứa Lưu huỳnh (Sulfur) hoặc các hoạt chất ức chế sinh tổng hợp Sterol (DMI) được đăng ký theo đúng nhãn.",
                "Tránh phun lưu huỳnh khi nhiệt độ ngoài trời vượt quá 30°C để tránh gây cháy lá."
            ],
            "aftercare_monitoring": [
                "Theo dõi các lứa đọt non tiếp theo"
            ],
            "common_mistakes": [
                "Để tán cây quá rậm rạp cản trở ánh nắng",
                "Phun thuốc trừ nấm không đều làm sót các chồi ngọn non trên cao"
            ],
            "when_to_seek_help": "Khi hơn 40% chồi non trên cây bị bao phủ bởi phấn trắng trong giai đoạn ra hoa đậu quả.",
            "safety_notes": "Mang khẩu trang và kính bảo hộ khi phun chế phẩm lưu huỳnh.",
            "sources": [
                "University of California IPM Pest Management Guidelines: Apple Powdery Mildew",
                "Washington State University Extension - Tree Fruit Powdery Mildew",
                "EPPO Data Sheets on Quarantine Pests"
            ],
            "image_url": "/images/diseases/apple_powdery_mildew.jpg",
            "care": [
                {"category": "Tỉa cành", "title": "Cắt bỏ chồi nhiễm phấn trắng", "description": "Kiểm tra và cắt bỏ các ngọn chồi phủ phấn trắng vào đầu mùa xuân để ngắt nguồn lây lan.", "priority": "high"},
                {"category": "Sinh học", "title": "Phun dầu khoáng hoặc lưu huỳnh", "description": "Sử dụng chế phẩm sinh học hoặc lưu huỳnh hữu cơ theo hướng dẫn nhãn khi chồi bắt đầu bung.", "priority": "medium"}
            ]
        },
        {
            "id": "corn_common_rust",
            "name": "Bệnh rỉ sắt ngô",
            "scientific_name": "Puccinia sorghi",
            "english_name": "Common Rust of Corn / Maize",
            "plant": "Ngô",
            "severity": "Nhẹ",
            "description": "Nấm Puccinia sorghi tạo các ổ mụn nổi màu nâu đỏ rỉ sắt trên cả hai mặt lá ngô, làm giảm hiệu suất quang hợp.",
            "overview": "Bệnh rỉ sắt ngô là bệnh lá phổ biến ở hầu hết các vùng trồng ngô trên thế giới. Bệnh thường xuất hiện khi cây chuẩn bị trổ cờ phun râu trong điều kiện độ ẩm cao và thời tiết mát mẻ.",
            "pathogen": "Puccinia sorghi Schwein.",
            "favorable_conditions": "Nhiệt độ mát mẻ 16°C - 23°C kết hợp độ ẩm không khí rất cao >95% và thời gian đọng sương kéo dài trên 6 giờ.",
            "transmission": [
                "Bào tử hạ (urediniospores) phát tán theo luồng không khí đi xa hàng trăm kilômét",
                "Lây truyền qua ký chủ phụ là các loài chua me đất (Oxalis spp.)"
            ],
            "risk_level_explanation": "Mức độ Nhẹ đến Trung bình: Phần lớn các giống ngô lai hiện nay có sức chống chịu tốt; bệnh chỉ gây thiệt hại đáng kể nếu bùng phát sớm trước giai đoạn trổ cờ.",
            "symptoms": [
                "Các mụn nhỏ li ti màu vàng sẫm hoặc nâu rỉ sắt",
                "Mụn vỡ ra giải phóng bột bào tử màu nâu đỏ",
                "Lá bị khô cháy sớm khi nấm phát triển mạnh"
            ],
            "early_symptoms": [
                "Xuất hiện các đốm nhỏ màu vàng nhạt li ti rải rác trên phiến lá"
            ],
            "mid_symptoms": [
                "Hình thành các ổ mụn mủ nổi gồ lên (pustules) hình bầu dục màu nâu đỏ rỉ sắt ở cả 2 mặt lá",
                "Mụn vỡ ra giải phóng lớp bột phấn màu gỉ sắt dính vào tay khi chạm vào"
            ],
            "severe_symptoms": [
                "Các mụn mủ dày đặc liên kết lại làm phiến lá bị khô cháy từ chóp vào, lá giòn dễ rách",
                "Cuối vụ các mụn mủ chuyển sang màu đen sẫm (bào tử đông - teliospores)"
            ],
            "similar_diseases_diff": [
                "Phân biệt với Bệnh rỉ sắt miền Nam (Southern Rust - Puccinia polysora): Rỉ sắt miền Nam có mụn mủ nhỏ hơn, màu vàng cam sáng và tập trung chủ yếu ở mặt trên lá trong điều kiện nhiệt độ cao hơn (>27°C)."
            ],
            "prevention_before_planting": [
                "Lựa chọn các giống ngô lai có gen kháng bệnh rỉ sắt (như các giống mang gen Rp)",
                "Gieo trồng đúng khung thời vụ để tránh giai đoạn cây non gặp đợt mưa lạnh kéo dài"
            ],
            "prevention_during_growth": [
                "Bón phân cân đối N-P-K, bổ sung đủ Kali để tăng độ cứng cáp cho lá",
                "Không trồng quá dày làm che khuất ánh sáng và giữ ẩm ướt trong ruộng ngô"
            ],
            "water_management": "Thoát nước rãnh tốt, không để ngập úng gốc ngô.",
            "nutrition_management": "Tránh bón thừa đạm ở giai đoạn ngô vươn lóng trổ cờ.",
            "density_management": "Mật độ khuyến cáo 55.000 - 65.000 cây/ha tùy theo giống ngô.",
            "field_sanitation": "Diệt trừ các loài cỏ dại ký chủ phụ (chua me đất Oxalis) xung quanh bờ ruộng.",
            "pruning_guide": "Không áp dụng cắt tỉa cho ngô; loại bỏ lá già khô héo sau khi bắp đã thụ phấn.",
            "crop_rotation_guide": "Luân canh với đậu tương, lạc hoặc lúa nước.",
            "biological_control": [
                "Bảo tồn các loài thiên địch tự nhiên và vi sinh vật đối kháng tự nhiên trong đất"
            ],
            "chemical_control_principles": [
                "Chỉ cần can thiệp hóa học khi bệnh xuất hiện sớm trước khi trổ cờ trên các giống ngô mẫn cảm và dự báo thời tiết ẩm mát kéo dài.",
                "Sử dụng các hoạt chất trừ nấm nhóm Triazole hoặc Strobilurin được cấp phép theo hướng dẫn trên nhãn."
            ],
            "aftercare_monitoring": [
                "Theo dõi tỷ lệ lá bị bao phủ bởi mụn rỉ sắt ở tầng lá nuôi bắp"
            ],
            "common_mistakes": [
                "Phun thuốc khi cây đã vào giai đoạn chín sáp (không mang lại hiệu quả kinh tế)",
                "Nhầm lẫn giữa rỉ sắt thường và rỉ sắt miền Nam dẫn đến chọn thời điểm phòng ngừa sai"
            ],
            "when_to_seek_help": "Khi bệnh xuất hiện ở giai đoạn ngô 6-8 lá và lan rộng nhanh trên tầng lá giữa.",
            "safety_notes": "Tuân thủ hướng dẫn an toàn lao động và bảo vệ môi trường.",
            "sources": [
                "FAO Maize Production Guidelines - Pest & Disease Management",
                "Purdue University Extension - Common and Southern Rust of Corn (BP-82-W)",
                "Iowa State University Extension - Corn Rust Diseases"
            ],
            "image_url": "/images/diseases/corn_common_rust.jpg",
            "care": [
                {"category": "Giống & Dinh dưỡng", "title": "Chọn giống kháng & Bổ sung Kali", "description": "Sử dụng giống ngô lai kháng rỉ sắt và bón đủ phân Kali để củng cố vách tế bào lá.", "priority": "high"},
                {"category": "Mật độ", "title": "Giữ khoảng cách hàng hợp lý", "description": "Không trồng quá dày để ánh nắng xuyên qua tán lá, giảm thời gian lá ướt sương.", "priority": "medium"}
            ]
        }
    ]

    for d_item in diseases_data:
        care_items = d_item.pop("care")
        existing = db.query(Disease).filter(Disease.id == d_item["id"]).first()
        if not existing:
            disease = Disease(**d_item)
            db.add(disease)
            db.commit()

            for c_item in care_items:
                care = CareRecommendation(disease_id=disease.id, **c_item)
                db.add(care)
            db.commit()
        else:
            # Update existing record with rich fields
            for key, val in d_item.items():
                setattr(existing, key, val)
            db.commit()

            # Refresh care recommendations
            db.query(CareRecommendation).filter(CareRecommendation.disease_id == existing.id).delete()
            for c_item in care_items:
                care = CareRecommendation(disease_id=existing.id, **c_item)
                db.add(care)
            db.commit()

    if not db.query(DiagnosisHistory).first():
        sample_history = DiagnosisHistory(
            plant="Cà chua",
            disease="Bệnh úa sớm cà chua (Early Blight)",
            primary_disease="Tomato___Early_blight",
            confidence=0.947,
            severity="Trung bình",
            status="detected",
            image_url="/images/diseases/tomato_early_blight.jpg",
            heatmap_url=None,
            is_multi_disease=False,
            detections=[
                {
                    "class_id": 1,
                    "disease": "Tomato___Early_blight",
                    "confidence": 0.947,
                    "bbox": {"x1": 120.0, "y1": 80.0, "x2": 310.0, "y2": 240.0}
                }
            ],
            detected_diseases=[
                {
                    "disease": "Tomato___Early_blight",
                    "disease_name": "Bệnh úa sớm cà chua (Early Blight)",
                    "plant": "Cà chua",
                    "disease_id": "tomato_early_blight",
                    "max_confidence": 0.947,
                    "detection_count": 1,
                    "severity": "Trung bình",
                    "confidence_level": "Độ tin cậy cao",
                    "description": "Nấm Alternaria solani gây các vết đốm sẫm màu hình bia bắn.",
                    "symptoms": [
                        "Vết đốm hình tròn màu nâu đen trên lá già",
                        "Vòng tròn đồng tâm đặc trưng dạng hình bia bắn"
                    ],
                    "recommendations": [
                        {"title": "Cắt tỉa lá già dưới gốc", "description": "Tỉa bỏ toàn bộ lá già ở tầng dưới cách mặt đất 25cm."},
                        {"title": "Tưới gốc nhỏ giọt", "description": "Chỉ tưới dưới gốc cây vào buổi sáng, giữ tán lá khô ráo."}
                    ],
                    "detections": [
                        {
                            "class_id": 1,
                            "disease": "Tomato___Early_blight",
                            "confidence": 0.947,
                            "bbox": {"x1": 120.0, "y1": 80.0, "x2": 310.0, "y2": 240.0}
                        }
                    ]
                }
            ],
            recommendations=[
                {"title": "Cắt tỉa lá già dưới gốc", "description": "Tỉa bỏ toàn bộ lá già ở tầng dưới cách mặt đất 25cm để ngăn nấm từ đất lây lên."},
                {"title": "Tưới gốc nhỏ giọt", "description": "Chỉ tưới dưới gốc cây vào buổi sáng, giữ tán lá hoàn toàn khô ráo."}
            ],
            created_at=datetime.now(timezone.utc)
        )
        db.add(sample_history)
        db.commit()

    db.close()
    print("Database seeded with comprehensive scientific agricultural knowledge.")

