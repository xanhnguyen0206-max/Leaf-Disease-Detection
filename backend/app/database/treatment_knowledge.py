TREATMENT_PLANS_KNOWLEDGE = {
    "Tomato___Bacterial_spot": {
        "disease_id": "Tomato___Bacterial_spot",
        "plan_version": "1.0",
        "phases": [
            {
                "name": "Đánh giá & Xác nhận",
                "sequence": 1,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Kiểm tra triệu chứng đặc trưng",
                        "description": "Xác nhận các đốm nhỏ, sẫm màu, úng nước trên lá và trái. Bệnh thường xuất hiện sau những đợt mưa ẩm ướt.",
                        "why_it_matters": "Bacterial spot dễ bị nhầm với Septoria. Việc xác định đúng giúp tránh sử dụng sai biện pháp xử lý.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Bacterial Spot Management", "url": "https://ipm.ucanr.edu/agriculture/tomato/bacterial-spot/"}
                        ]
                    }
                ]
            },
            {
                "name": "Vệ sinh & Quản lý môi trường",
                "sequence": 2,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Tránh tưới phun lên tán lá",
                        "description": "Chuyển sang tưới nhỏ giọt hoặc tưới gốc. Tránh làm ướt lá, đặc biệt là vào buổi chiều tối.",
                        "why_it_matters": "Vi khuẩn lây lan mạnh mẽ qua các giọt nước bắn. Giữ lá khô là biện pháp kiểm soát quan trọng nhất.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Bacterial Spot Management", "url": "https://ipm.ucanr.edu/agriculture/tomato/bacterial-spot/"}
                        ]
                    },
                    {
                        "sequence": 2,
                        "title": "Tránh làm việc khi tán cây ướt",
                        "description": "Không cắt tỉa, thu hoạch hay đi lại giữa các luống cà chua khi lá đang ướt do sương hoặc mưa.",
                        "why_it_matters": "Dụng cụ và quần áo có thể vô tình mang vi khuẩn từ cây bệnh sang cây khỏe.",
                        "timing": "CONDITIONAL",
                        "is_required": True,
                        "sources": [
                            {"organization": "Cornell University", "title": "Bacterial Spot of Tomato", "url": "https://ecommons.cornell.edu/"}
                        ]
                    }
                ]
            },
            {
                "name": "Kiểm soát & Can thiệp",
                "sequence": 3,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Áp dụng biện pháp kiểm soát gốc đồng (Copper-based)",
                        "description": "Nếu bệnh mới xuất hiện và điều kiện thời tiết tiếp tục ẩm ướt, có thể sử dụng các chế phẩm chứa đồng được cấp phép tại địa phương.",
                        "why_it_matters": "Đồng có tác dụng bảo vệ, ngăn ngừa nhiễm mới. Tuy nhiên nó không chữa được lá đã bệnh.",
                        "timing": "CONDITIONAL",
                        "is_required": False,
                        "sources": [
                            {"organization": "FAO", "title": "Tomato IPM", "url": "https://www.fao.org/3/a0870e/a0870e.pdf"}
                        ]
                    }
                ]
            },
            {
                "name": "Theo dõi & Đánh giá",
                "sequence": 4,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Theo dõi sự lây lan định kỳ",
                        "description": "Kiểm tra sự xuất hiện của các đốm mới trên lá non hoặc trái mỗi 3-5 ngày.",
                        "why_it_matters": "Giúp đánh giá hiệu quả của các biện pháp quản lý môi trường.",
                        "timing": "WEEKLY",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Bacterial Spot Management", "url": "https://ipm.ucanr.edu/agriculture/tomato/bacterial-spot/"}
                        ]
                    }
                ]
            }
        ]
    },
    "Tomato___Early_blight": {
        "disease_id": "Tomato___Early_blight",
        "plan_version": "1.0",
        "phases": [
            {
                "name": "Đánh giá & Vệ sinh",
                "sequence": 1,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Xác định và loại bỏ lá bệnh ở gốc",
                        "description": "Cắt bỏ các lá già phía dưới có vết bệnh hình vòng cung đồng tâm. Bỏ vào túi kín hoặc tiêu hủy xa vườn.",
                        "why_it_matters": "Bệnh thường bắt đầu từ lá già gần mặt đất. Loại bỏ giúp giảm nguồn lây nhiễm.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "Cornell University", "title": "Early Blight of Tomato", "url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/early-blight-of-tomato/"}
                        ]
                    },
                    {
                        "sequence": 2,
                        "title": "Vệ sinh dụng cụ cắt tỉa",
                        "description": "Khử trùng kéo/dụng cụ cắt tỉa bằng cồn hoặc dung dịch thuốc tẩy sau khi cắt lá bệnh.",
                        "why_it_matters": "Ngăn ngừa việc lây lan nấm từ cây này sang cây khác thông qua dụng cụ.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Early Blight", "url": "https://ipm.ucanr.edu/agriculture/tomato/early-blight/"}
                        ]
                    }
                ]
            },
            {
                "name": "Quản lý độ ẩm",
                "sequence": 2,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Phủ gốc (Mulching)",
                        "description": "Phủ lớp vật liệu hữu cơ hoặc màng phủ rơm rạ quanh gốc cây.",
                        "why_it_matters": "Ngăn đất và bào tử nấm bắn lên lá dưới khi mưa hoặc tưới nước.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Early Blight", "url": "https://ipm.ucanr.edu/agriculture/tomato/early-blight/"}
                        ]
                    },
                    {
                        "sequence": 2,
                        "title": "Kiểm soát cách tưới",
                        "description": "Tưới vào gốc, tránh làm ướt lá. Nếu tưới phun mưa, hãy tưới vào sáng sớm để lá khô nhanh trong ngày.",
                        "why_it_matters": "Bào tử nấm cần độ ẩm bề mặt lá kéo dài để nảy mầm và xâm nhập.",
                        "timing": "DAILY",
                        "is_required": True,
                        "sources": [
                            {"organization": "Cornell University", "title": "Early Blight of Tomato", "url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/early-blight-of-tomato/"}
                        ]
                    }
                ]
            },
            {
                "name": "Can thiệp",
                "sequence": 3,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Cân nhắc sử dụng thuốc bảo vệ thực vật sinh học hoặc hóa học",
                        "description": "Sử dụng các sản phẩm gốc đồng hoặc thuốc diệt nấm phổ rộng được phép. Áp dụng theo đúng hướng dẫn trên nhãn.",
                        "why_it_matters": "Thuốc diệt nấm chỉ có tác dụng bảo vệ lá mới, không làm lành lá đã bệnh. Cần phun phòng ngừa hoặc ngay khi mới chớm.",
                        "timing": "CONDITIONAL",
                        "is_required": False,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Early Blight", "url": "https://ipm.ucanr.edu/agriculture/tomato/early-blight/"}
                        ]
                    }
                ]
            }
        ]
    },
    "Tomato___Late_blight": {
        "disease_id": "Tomato___Late_blight",
        "plan_version": "1.0",
        "phases": [
            {
                "name": "Hành động Khẩn cấp",
                "sequence": 1,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Loại bỏ và tiêu hủy cây nhiễm nặng",
                        "description": "Nếu bệnh lan nhanh, nhổ bỏ toàn bộ cây nhiễm, cho vào túi rác kín và vứt bỏ hoặc tiêu hủy. Không ủ phân.",
                        "why_it_matters": "Late blight lây lan cực kỳ nhanh chóng và có thể tàn phá toàn bộ khu vườn trong vài ngày.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "Cornell University", "title": "Late Blight of Tomato", "url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/late-blight/"}
                        ]
                    }
                ]
            },
            {
                "name": "Bảo vệ các cây còn lại",
                "sequence": 2,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Kiểm tra kỹ lưỡng các cây lân cận",
                        "description": "Tìm kiếm các vết đốm sẫm màu, úng nước, có lớp nấm trắng ở mặt dưới lá.",
                        "why_it_matters": "Phát hiện sớm trên các cây chưa biểu hiện bệnh nặng giúp bảo vệ chúng kịp thời.",
                        "timing": "DAILY",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Late Blight", "url": "https://ipm.ucanr.edu/agriculture/tomato/late-blight/"}
                        ]
                    },
                    {
                        "sequence": 2,
                        "title": "Áp dụng thuốc diệt nấm phòng ngừa",
                        "description": "Phun các loại thuốc diệt nấm được cấp phép (như chlorothalonil, gốc đồng...) lên các cây chưa biểu hiện bệnh.",
                        "why_it_matters": "Khi Late Blight đã xuất hiện, các cây khỏe cần được bảo vệ bằng hóa chất/sinh học vì bệnh lây qua gió rất mạnh.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "Cornell University", "title": "Late Blight Management", "url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/late-blight/"}
                        ]
                    }
                ]
            }
        ]
    },
    "Tomato___Septoria_leaf_spot": {
        "disease_id": "Tomato___Septoria_leaf_spot",
        "plan_version": "1.0",
        "phases": [
            {
                "name": "Vệ sinh đồng ruộng",
                "sequence": 1,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Cắt bỏ lá bệnh phía dưới",
                        "description": "Loại bỏ cẩn thận các lá ở phần gốc có nhiều đốm tròn nhỏ (tâm xám, viền sẫm).",
                        "why_it_matters": "Bệnh lây lan từ dưới lên trên. Cắt bỏ giúp làm chậm quá trình lây lan.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Septoria Leaf Spot", "url": "https://ipm.ucanr.edu/"}
                        ]
                    }
                ]
            },
            {
                "name": "Quản lý độ ẩm",
                "sequence": 2,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Tưới nước dưới gốc",
                        "description": "Tuyệt đối không tưới lên tán lá.",
                        "why_it_matters": "Bào tử nấm cần nước để nảy mầm và bắn lên các lá cao hơn.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "Cornell University", "title": "Septoria Leaf Spot of Tomato", "url": "https://www.vegetables.cornell.edu/"}
                        ]
                    }
                ]
            }
        ]
    },
    "Tomato___Leaf_mold": {
        "disease_id": "Tomato___Leaf_mold",
        "plan_version": "1.0",
        "phases": [
            {
                "name": "Quản lý luân chuyển không khí",
                "sequence": 1,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Tăng cường thông gió",
                        "description": "Nếu trồng trong nhà kính/màng, cần mở cửa thông gió hoặc dùng quạt. Nếu trồng ngoài trời, tỉa bớt các cành lá quá dày.",
                        "why_it_matters": "Bệnh này phát triển mạnh trong điều kiện độ ẩm rất cao (>85%). Giảm độ ẩm là chìa khóa.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Leaf Mold", "url": "https://ipm.ucanr.edu/"}
                        ]
                    }
                ]
            }
        ]
    },
    "Tomato___Powdery_mildew": {
        "disease_id": "Tomato___Powdery_mildew",
        "plan_version": "1.0",
        "phases": [
            {
                "name": "Quản lý tán cây",
                "sequence": 1,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Tỉa bớt lá để tăng độ bắt nắng",
                        "description": "Loại bỏ những lá già, lá bị nấm trắng bao phủ nặng.",
                        "why_it_matters": "Nấm phấn trắng phát triển tốt trong điều kiện bóng râm. Tăng ánh sáng giúp hạn chế nấm.",
                        "timing": "IMMEDIATE",
                        "is_required": True,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Powdery Mildew", "url": "https://ipm.ucanr.edu/agriculture/tomato/powdery-mildew/"}
                        ]
                    }
                ]
            },
            {
                "name": "Can thiệp bổ sung",
                "sequence": 2,
                "steps": [
                    {
                        "sequence": 1,
                        "title": "Sử dụng các chế phẩm sinh học/hóa học",
                        "description": "Áp dụng dầu Neem, lưu huỳnh, hoặc thuốc diệt nấm chuyên dụng theo hướng dẫn.",
                        "why_it_matters": "Giúp bảo vệ các lá chưa nhiễm và hạn chế sự lan rộng của bào tử nấm.",
                        "timing": "CONDITIONAL",
                        "is_required": False,
                        "sources": [
                            {"organization": "UC IPM", "title": "Tomato Powdery Mildew", "url": "https://ipm.ucanr.edu/agriculture/tomato/powdery-mildew/"}
                        ]
                    }
                ]
            }
        ]
    }
}
