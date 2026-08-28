# Cẩm nang Giải thích Mã nguồn Toàn diện LEAF_AI (COMPLETE CODEBASE GUIDE)

Tài liệu này được biên soạn nhằm giải thích toàn bộ mã nguồn của dự án **LEAF_AI** bằng ngôn ngữ con người trực quan, rõ ràng, giúp một kỹ sư mới tiếp cận có thể nắm bắt và làm chủ toàn bộ hệ thống mà không cần phải tự mở từng dòng mã nguồn để suy đoán.

---

## 1. Vòng đời Mô hình AI trong Bộ nhớ (Model Memory Lifecycle & Singleton Pattern)

### 1.1. Vấn đề của việc Nạp Mô hình theo từng Yêu cầu (Request-level Loading)
Một sai lầm phổ biến khi mới xây dựng hệ thống AI là nạp mô hình (`YOLO("best.pt")`) bên trong hàm xử lý request (`predict_leaf`). Điều này dẫn đến các hậu quả nghiêm trọng:
1. **Thời gian phản hồi chậm**: Mỗi lần nạp file `.pt` từ ổ đĩa vào RAM và khởi tạo đồ thị tính toán PyTorch mất từ **1.5 đến 3 giây**.
2. **Quá tải CPU / Tràn bộ nhớ RAM**: Khi có 10 người dùng đồng thời gửi ảnh, hệ thống sẽ cố nạp 10 bản sao của mô hình vào bộ nhớ, gây ra lỗi hết RAM (`Out of Memory Crash`).

### 1.2. Giải pháp Singleton của LEAF_AI
LEAF_AI giải quyết triệt để vấn đề trên bằng mô hình **Singleton nạp sẵn vào bộ nhớ (Pre-warmed Model in RAM)**:

```text
[Khởi động Ứng dụng Backend (FastAPI Startup)]
                   │
                   ▼
       [Khởi tạo Module Services]
                   │
                   ▼
  [YOLOModelService.__init__() được gọi 1 LẦN DUY NHẤT]
                   │
                   ├──► Đọc cấu hình settings.MODEL_PATH ("model/tomato_v3/best.pt")
                   ├──► Tải trọng số PyTorch và giữ đối tượng self.model trong RAM
                   └──► Khởi tạo danh sách nhãn classes (0: Bacterial Spot, 1: Early Blight, 2: Late Blight)
                   │
                   ▼
 [Máy chủ sẵn sàng lắng nghe tại Cổng 8000 (Ready for Requests)]
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
[Request 1 từ User A]       [Request 2 từ User B]
    │                             │
    ├──► Dùng chung self.model    └──► Dùng chung self.model
    └──► Suy luận chỉ mất 150ms        └──► Suy luận chỉ mất 150ms
```

---

## 2. Giải thích Chi tiết Từng Module & Lớp Mã nguồn Backend

### 2.1. Lớp Trừu tượng [BaseModelService](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/base_model_service.py)
- **Mục đích**: Định nghĩa một "bản giao kèo" (Interface Contract) chuẩn cho tất cả các mô hình AI trong hệ thống.
- **Tại sao cần abstraction này?**: Giúp tách biệt hoàn toàn tầng API nghiệp vụ khỏi công nghệ AI cụ thể. Sau này nếu nhóm AI muốn chuyển từ YOLO sang EfficientNet, Swin Transformer, hoặc Cloud Vision API, tầng API và Frontend hoàn toàn không bị ảnh hưởng.
- **Phương thức bắt buộc**:
  ```python
  @abstractmethod
  def predict(self, image_input: Union[str, bytes], conf_threshold: Optional[float] = None) -> Dict[str, Any]:
      """Mọi model service bắt buộc phải nhận ảnh và trả về dictionary chuẩn."""
      pass
  ```

---

### 2.2. Lớp Thực thi [YOLOModelService](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/yolo_model_service.py)
- **Mục đích**: Hiện thực hóa việc suy luận bằng mô hình YOLOv8n trên ảnh lá cây.
- **Các phương thức chính**:
  1. `__init__(model_path, imgsz=640, default_conf=0.25, device="cpu")`: Nạp mô hình PyTorch, lưu độ phân giải chuẩn và thiết lập thiết bị tính toán.
  2. `predict(image_input, conf_threshold)`:
     - Chuyển đổi dữ liệu ảnh thành đối tượng PIL Image.
     - Thực thi suy luận: `self.model.predict(source=image, imgsz=640, conf=threshold, device="cpu")`.
     - Lặp qua các hộp dự đoán (`results[0].boxes`), trích xuất tọa độ chuẩn hóa và chuyển thành tọa độ pixel thực của ảnh gốc `[x1, y1, x2, y2]`.
     - Gọi `postprocess_detections()` để loại bỏ các hộp bất thường (ví dụ: chiều rộng hoặc chiều cao $\le 0$, hoặc tọa độ $x_2 < x_1$).
     - Xác định bệnh xuất hiện nhiều nhất và trả về cấu trúc kết quả.

---

### 2.3. Dịch vụ Nghiệp vụ [PredictionService](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/prediction_service.py)
- **Mục đích**: Là trái tim điều phối toàn bộ nghiệp vụ chẩn đoán giữa API, Mô hình AI và Cơ sở dữ liệu.
- **Phương thức chính `process_prediction(file_bytes, filename, db, conf_threshold)`**:
  - **Bước 1**: Sinh mã UUID duy nhất và lưu file ảnh vào thư mục `backend/uploads/{uuid}.jpg`.
  - **Bước 2**: Gửi byte ảnh tới `self.model_service.predict()`.
  - **Bước 3 - Gom nhóm Đa bệnh (Multi-disease Grouping)**:
    - Tạo từ điển gom nhóm các đốm bệnh theo từng loài bệnh.
    - Tính `detection_count` (số vết bệnh) và `max_confidence` (độ tin cậy cao nhất).
    - Chuyển đổi điểm số sang nhãn ngôn ngữ tự nhiên:
      - Nếu $\ge 0.70$: *"Độ tin cậy cao"*
      - Nếu từ $0.50$ đến $0.69$: *"Độ tin cậy trung bình"*
      - Nếu $< 0.50$: *"Dấu hiệu cần kiểm tra thêm"*
  - **Bước 4 - Truy vấn Cơ sở Dữ liệu**:
    - Tìm kiếm thông tin bệnh trong bảng `diseases` dựa trên class ID.
    - Lấy danh sách các khuyến nghị điều trị tương ứng từ bảng `care_recommendations`.
  - **Bước 5 - Lưu Lịch sử**:
    - Tạo bản ghi mới trong bảng `diagnosis_history` với đường dẫn ảnh tĩnh `/uploads/{uuid}.jpg`.
    - Commit vào SQLite.
  - **Bước 6**: Đóng gói toàn bộ thành đối tượng `DiagnosisResult` trả về cho API Controller.

---

## 3. So sánh Bốn Tầng Mô hình Dữ liệu (Models vs Schemas vs DTOs vs TypeScript Types)

Đây là một trong những khái niệm quan trọng nhất để hiểu cách dữ liệu di chuyển xuyên suốt hệ thống LEAF_AI:

```text
[ SQLite Database ] ──► (1) SQLAlchemy ORM Model (models.py)
                              │
                              ▼ (Chuyển đổi nội bộ Backend)
                        (2) Pydantic Schema (schemas/diagnosis.py)
                              │
                              ▼ (Vận chuyển qua HTTP Network dưới dạng JSON)
                        (3) REST API Response (JSON Payload)
                              │
                              ▼ (Biên dịch trên Trình duyệt)
[ React Frontend ]  ──► (4) TypeScript Interface (types/index.ts)
```

| Tầng Dữ liệu | Ví dụ File | Mục đích & Đặc tính |
|---|---|---|
| **1. Database ORM Model** | [models.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/database/models.py) (`Disease`, `DiagnosisHistory`) | Đại diện cho cấu trúc bảng vật lý trong SQLite, có kiểu dữ liệu của DB (`Column`, `String`, `ForeignKey`), quản lý quan hệ bảng (`relationship`). |
| **2. Pydantic Schema** | [schemas/diagnosis.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/schemas/diagnosis.py) (`DiagnosisResult`) | Định nghĩa và validate dữ liệu ở tầng ứng dụng Python, tự động chuyển đổi ORM sang Python Dictionary/JSON (`from_attributes = True`). |
| **3. API Response** | `POST /api/predict` JSON | Chuỗi văn bản JSON thuần túy truyền qua mạng Internet thông qua giao thức HTTP. |
| **4. TypeScript Interface** | [types/index.ts](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/types/index.ts) (`DiagnosisResult`) | Quy định kiểu dữ liệu tĩnh trên trình duyệt, giúp React IDE gợi ý cú pháp (`autocomplete`) và cảnh báo lỗi lúc viết code giao diện. |

---

## 4. Thuật toán Ra Quyết định của Mô hình AI (Decision Logic)

### Tình huống Thực tế: Mô hình Phát hiện Nhiều Đốm Bệnh Đồng Thời
Giả sử người dùng tải lên một chiếc lá cà chua bị nhiễm cả 2 loại bệnh với các hộp phát hiện như sau:
- **Đốm 1**: `Tomato___Bacterial_spot` với độ tin cậy `0.82`
- **Đốm 2**: `Tomato___Bacterial_spot` với độ tin cậy `0.78`
- **Đốm 3**: `Tomato___Early_blight` với độ tin cậy `0.61`
- **Đốm 4**: `Tomato___Late_blight` với độ tin cậy `0.21`

### Quy trình Xử lý Chính xác của Backend:
1. **Lọc Ngưỡng (Threshold Filtering với ngưỡng mặc định 0.25)**:
   - Đốm 4 (`Late_blight` conf 0.21) bị loại bỏ ngay lập tức vì $< 0.25$.
   - Giữ lại Đốm 1, 2 và 3.
2. **Gom nhóm Đa bệnh (Multi-disease Aggregation)**:
   - Nhóm 1: `Tomato___Bacterial_spot` → Có **2 đốm**, độ tin cậy tối đa là **0.82 (82%)**, mức độ: *"Độ tin cậy cao"*.
   - Nhóm 2: `Tomato___Early_blight` → Có **1 đốm**, độ tin cậy tối đa là **0.61 (61%)**, mức độ: *"Độ tin cậy trung bình"*.
3. **Xác định Cờ Đa bệnh & Bệnh chính**:
   - Cờ `is_multi_disease` được đặt là `True`.
   - Bệnh chính (`primary_disease`) được xác định là: **`Tomato___Bacterial_spot`** (vì có độ tin cậy cao nhất 0.82 và số đốm nhiều nhất).
4. **Hiển thị trên Giao diện Frontend**:
   - Thẻ to nhất hiển thị: *"Đốm vi khuẩn trên lá cà chua (82%) - Bệnh chính"*.
   - Mục mở rộng bên dưới hiển thị thêm: *"Phát hiện dấu hiệu đồng nhiễm: Bệnh đốm vòng (61%) - 1 vị trí tổn thương"*.
   - Trên ảnh lá sẽ vẽ 2 hộp màu đỏ bao quanh đốm vi khuẩn và 1 hộp màu cam bao quanh đốm bệnh cháy sớm.
