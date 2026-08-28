# Sổ tay Bảo trì, Nâng cấp & Mở rộng Hệ thống (MAINTENANCE GUIDE)

Tài liệu này là cẩm nang thực hành cho các lập trình viên và kỹ sư AI khi cần bảo trì, thay đổi mô hình, bổ sung bệnh mới, thêm giống cây trồng mới, hoặc mở rộng kiến trúc hệ thống **LEAF_AI** trong tương lai.

---

## 1. Hướng dẫn Thay đổi hoặc Chuyển đổi Model AI (Model Switching)

### 1.1. Chuyển đổi giữa Model V3 (Mặc định) và Model V2 (Backup)
Hệ thống LEAF_AI đã được thiết kế sẵn cơ chế chuyển đổi qua biến môi trường mà **không cần sửa mã nguồn**:

- **Cách 1: Thiết lập qua Biến Môi trường (Recommended)**:
  ```powershell
  # Chuyển sang mô hình V2 (384x384)
  $env:MODEL_VERSION="v2"
  $env:MODEL_IMG_SIZE="384"
  python -m app.main

  # Chuyển lại mô hình V3 Production (640x640)
  $env:MODEL_VERSION="v3"
  $env:MODEL_IMG_SIZE="640"
  python -m app.main
  ```

- **Cách 2: Chỉ định đường dẫn file Weights tùy ý**:
  ```powershell
  $env:MODEL_PATH="c:/Users/Admin/Leaf-Disease-Detection/model/custom_model/best.pt"
  $env:MODEL_IMG_SIZE="640"
  python -m app.main
  ```

- **Cách 3: Chạy ở chế độ Giả lập (Mock Mode) khi máy không có PyTorch/YOLO**:
  ```powershell
  $env:MODEL_TYPE="mock"
  python -m app.main
  ```

### 1.2. Nạp Mô hình Huấn luyện Mới Hoàn toàn (Deploying a New Trained Model)
Khi đội ngũ AI hoàn thành việc huấn luyện một mô hình YOLO mới (ví dụ: `v4_yolov8m_640.pt`):
1. **Bước 1**: Tạo thư mục mới `model/tomato_v4/`.
2. **Bước 2**: Copy file weights vào `model/tomato_v4/best.pt`.
3. **Bước 3**: Tạo file `model/tomato_v4/classes.json` chứa danh sách nhãn index chính xác từ `data.yaml`.
4. **Bước 4**: Cập nhật file [config.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/core/config.py) hoặc thiết lập biến môi trường `MODEL_PATH`.
5. **Bước 5**: Chạy bộ test hồi quy [test_yolo_service.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/tests/test_yolo_service.py) để xác nhận mô hình nạp thành công vào bộ nhớ.

---

## 2. Hướng dẫn Bổ sung Bệnh Mới vào Hệ thống (Adding a New Disease)

Khi mô hình AI được nâng cấp để nhận diện thêm bệnh mới (ví dụ: *Bệnh Thán thư / Anthracnose* hoặc *Bệnh Đốm lá Septoria*), bạn cần thực hiện theo các bước chuẩn sau:

### Bước 1: Cập nhật Lớp AI Model Mapping
1. Thêm nhãn mới vào file `classes.json` của model:
   ```json
   {
     "0": "Tomato___Bacterial_spot",
     "1": "Tomato___Early_blight",
     "2": "Tomato___Late_blight",
     "3": "Tomato___Septoria_leaf_spot"
   }
   ```
2. Cập nhật ánh xạ tên hiển thị tiếng Việt trong hàm `_normalize_disease_name()` tại [prediction_service.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/prediction_service.py#L33):
   ```python
   name_mapping = {
       "Tomato___Bacterial_spot": "Đốm vi khuẩn trên lá cà chua",
       "Tomato___Early_blight": "Bệnh đốm vòng (Cháy sớm) trên lá cà chua",
       "Tomato___Late_blight": "Bệnh mốc sương (Sương mai) trên lá cà chua",
       "Tomato___Septoria_leaf_spot": "Bệnh đốm lá Septoria trên cà chua",
   }
   ```

### Bước 2: Nạp Dữ liệu Bách khoa Toàn thư vào Cơ sở Dữ liệu (Seed Data)
Mở file [seed.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/database/seed.py) và thêm một đối tượng `Disease` mới vào danh sách `diseases_data`:
```python
{
    "id": "tomato_septoria_leaf_spot",
    "name": "Bệnh đốm lá Septoria trên cà chua",
    "plant": "Cà chua",
    "scientific_name": "Septoria lycopersici",
    "english_name": "Septoria Leaf Spot",
    "severity": "medium",
    "description": "Bệnh do nấm Septoria lycopersici gây ra, tạo các đốm nhỏ hình tròn có viền sẫm màu...",
    "overview": "...",
    "pathogen": "Nấm Septoria lycopersici",
    "favorable_conditions": "Nhiệt độ 20-25°C, độ ẩm cao, mưa nhiều...",
    "symptoms": ["Xuất hiện đốm tròn nhỏ 2-3mm", "Tâm đốm màu xám trắng, viền nâu đậm"],
    "prevention_before_planting": ["Vệ sinh sạch tàn dư vụ trước", "Luân canh cây trồng khác họ"],
    "prevention_during_growth": ["Tưới nước gốc, tránh làm ướt lá", "Phun phòng ngừa bằng hoạt chất gốc đồng"],
    "sources": ["FAO Plant Protection Guide", "IPM Tomato Manual"]
}
```
*Ghi chú: Khi khởi động lại Backend, hàm `seed_database()` sẽ tự động nạp bản ghi này vào cơ sở dữ liệu.*

### Bước 3: Đồng bộ Frontend TypeScript Types (Nếu có thêm trường đặc thù)
Kiểm tra file [types/index.ts](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/types/index.ts) để đảm bảo các interface `Disease` và `DiagnosisResult` đã bao quát đầy đủ các thuộc tính mới.

---

## 3. Hướng dẫn Mở rộng Sang Cây Trồng Khác (Adding a New Plant Species)

Nếu muốn mở rộng hệ sinh thái LEAF_AI từ **Cà chua** sang các loại cây ăn trái hoặc hoa màu khác (ví dụ: *Lúa, Ớt, Dưa leo, Ngô*):

1. **Thu thập Dữ liệu & Huấn luyện**:
   - Chuẩn bị dữ liệu ảnh trong thư mục `training/datasets/raw/pepper/` hoặc `rice/`.
   - Chạy script huấn luyện tương tự [train_tomato_v3.py](file:///c:/Users/Admin/Leaf-Disease-Detection/training/scripts/train_tomato_v3.py).
   - Xuất model ra `model/pepper/best.pt`.
2. **Cập nhật Backend Logic**:
   - Mở rộng hàm `_detect_plant_type()` trong [prediction_service.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/prediction_service.py) để tự động nhận biết hoặc tiếp nhận tham số `plant_type` từ query parameter API.
3. **Cập nhật Bộ lọc Frontend**:
   - Thêm nút tab hoặc dropdown chọn cây trồng tại [DiseaseLibraryPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiseaseLibraryPage.tsx) và [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx).

---

## 4. Hướng dẫn Điều chỉnh Ngưỡng Tin cậy (Confidence Threshold Tuning)

- **Mặc định toàn hệ thống**: Ngưỡng tin cậy được đặt là `0.25` (25%).
- **Cách thay đổi biến môi trường mặc định**:
  ```powershell
  $env:MODEL_CONFIDENCE_THRESHOLD="0.30"
  python -m app.main
  ```
- **Cách thay đổi theo từng request**:
  Người dùng hoặc ứng dụng client có thể truyền trực tiếp qua Query Param:
  `POST /api/predict?conf_threshold=0.40`
  Backend sẽ ưu tiên giá trị query parameter này thay cho cấu hình mặc định.

---

## 5. Kiến trúc Tích hợp AI Fallback trong Tương lai (Cloud AI Fallback Architecture)

Hệ thống LEAF_AI đã được thiết kế sẵn mẫu thiết kế **Strategy / Adapter Pattern** thông qua class trừu tượng [BaseModelService](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/base_model_service.py).

Khi bạn muốn tích hợp dịch vụ AI dự phòng từ Cloud (như Google Cloud Vision API, OpenAI GPT-4o Vision, hoặc AWS Rekognition) khi mô hình cục bộ không chắc chắn ($\text{confidence} < 0.35$):

### Sơ đồ Cắm Module Mở rộng (Plug-in Architecture):

```text
FastAPI /api/predict
       │
       ▼
PredictionService
       │
       ├───► 1. Gọi YOLOModelService (Local On-premise)
       │          │
       │          ├──► Nếu confidence >= 0.35: Trả về kết quả ngay
       │          │
       │          └──► Nếu confidence < 0.35 hoặc status == 'no_detection':
       │                     │
       │                     ▼
       └──────────► 2. Kích hoạt CloudVisionFallbackService (Cloud API)
                             │
                             └──► Phân tích bổ sung & xác thực kết quả
```

### Mã nguồn Triển khai Mẫu (Sample Fallback Service Implementation):
```python
# backend/app/services/cloud_fallback_service.py
from app.services.base_model_service import BaseModelService

class CloudVisionFallbackService(BaseModelService):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def predict(self, image_input, conf_threshold=0.25):
        # Gọi API Google Gemini / OpenAI Vision
        # Chuyển đổi kết quả về chuẩn Diagnosis dict {status, primary_disease, confidence, detections}
        pass
```
*Nhờ kiến trúc interface đồng nhất, `PredictionService` có thể chuyển mạch sang dịch vụ Cloud chỉ bằng 1 dòng lệnh mà không làm thay đổi bất kỳ thành phần nào trên Frontend!*
