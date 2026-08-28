# Luồng Dữ liệu Toàn Hệ thống LEAF_AI (SYSTEM DATA FLOW)

Tài liệu này mô tả chi tiết từng bước luồng dữ liệu (Data Flow) di chuyển qua các tầng của hệ thống **LEAF_AI**: từ tương tác của người dùng trên trình duyệt, qua API Client, Reverse Proxy, FastAPI, Business Logic, AI Inference Model, Cơ sở dữ liệu SQLite, và quay trở lại hiển thị trên giao diện người dùng.

---

## 1. Luồng Chẩn đoán Bệnh Lá (AI Diagnosis Data Flow - Core Flow)

Đây là luồng dữ liệu quan trọng và phức tạp nhất trong toàn bộ hệ thống.

### 1.1. Sơ đồ Tuần tự Chi tiết (Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    actor User as Nông dân / Người dùng
    participant UI as DiagnosePage.tsx
    participant API as api.ts (fetch client)
    participant Proxy as Vite Proxy (:3000 -> :8000)
    participant Fast as FastAPI (predict.py)
    participant Svc as PredictionService
    participant YOLO as YOLOModelService (in RAM)
    participant DB as SQLite DB (SessionLocal)

    User->>UI: Tải ảnh lá hoặc Chụp trực tiếp từ Camera
    UI->>UI: Hiển thị Preview ảnh, kích hoạt trạng thái "Đang phân tích..."
    UI->>API: Gọi diagnoseLeaf(file, confThreshold)
    API->>API: Đóng gói ảnh vào new FormData() ('file', blob)
    API->>Proxy: HTTP POST /api/predict (Multipart Form-Data)
    Proxy->>Fast: Forward request tới FastAPI backend (:8000)
    
    Fast->>Fast: 1. Validate đuôi file (.jpg, .png, .webp)
    Fast->>Fast: 2. Validate kích thước file (< 10MB)
    Fast->>Fast: 3. PIL Image.open().verify() chống file hỏng
    
    Fast->>Svc: process_prediction(file_bytes, filename, db, conf_threshold)
    Svc->>Svc: 1. Sinh UUID filename & lưu ảnh vào backend/uploads/
    Svc->>YOLO: predict(image_path_or_bytes, conf_threshold)
    
    Note over YOLO: YOLOv8n V3 (640x640) chạy suy luận trên PyTorch CPU/GPU
    YOLO->>YOLO: 2. Lọc detections theo confidence_threshold (mặc định 0.25)
    YOLO->>YOLO: 3. Chuyển đổi bounding box sang tọa độ pixel thực (x1, y1, x2, y2)
    YOLO-->>Svc: Trả về dict: {status, primary_disease, confidence, detections}

    alt Trường hợp: Phát hiện bệnh (status == 'detected')
        Svc->>Svc: 4. Gom nhóm detections theo class bệnh (Multi-disease grouping)
        Svc->>Svc: 5. Tính số đốm bệnh & max_confidence cho từng bệnh
        Svc->>Svc: 6. Gán mức độ tin cậy tự nhiên (Cao / Trung bình / Cần kiểm tra)
        Svc->>DB: 7. Truy vấn bảng 'diseases' lấy thông tin chi tiết & phác đồ
        DB-->>Svc: Trả về Disease object & CareRecommendations
        Svc->>DB: 8. Tạo bản ghi DiagnosisHistory & commit vào SQLite
        DB-->>Svc: Lưu thành công (id sinh tự động)
    else Trường hợp: Lá khỏe hoặc Không phát hiện (status == 'no_detection')
        Svc->>Svc: Đặt disease = "Không phát hiện bệnh / Cây khỏe mạnh"
        Svc->>DB: Lưu bản ghi lá khỏe vào DiagnosisHistory
        DB-->>Svc: Commit thành công
    end

    Svc-->>Fast: Trả về DiagnosisResult Pydantic schema
    Fast-->>Proxy: HTTP 200 OK (JSON Response)
    Proxy-->>API: Trả JSON về frontend
    API-->>UI: DiagnosisResult object

    UI->>UI: Cập nhật state result, tắt loading
    UI->>UI: Vẽ các Bounding Box đè lên ảnh (theo tỷ lệ hiển thị)
    UI->>UI: Hiển thị Thẻ Bệnh Chính, Các Bệnh Đồng Nhiễm & Khuyến nghị xử lý
    UI-->>User: Giao diện trực quan kết quả chẩn đoán
```

---

### 1.2. Giải thích Chi tiết Từng Bước Chuyển Dịch Dữ liệu

1. **Khởi tạo dữ liệu tại Frontend**:
   - Người dùng bấm nút "Chọn ảnh từ thiết bị" hoặc bấm "Bật camera" để chụp ảnh lá cây.
   - Trình duyệt tạo một đối tượng JavaScript `File` hoặc `Blob`.
   - `URL.createObjectURL(file)` được tạo ngay lập tức để người dùng xem trước (Preview) ảnh trong khi chờ kết quả.
2. **Vận chuyển qua HTTP**:
   - `api.ts` bọc file vào đối tượng `FormData`: `formData.append('file', file)`.
   - Gửi yêu cầu `POST /api/predict` kèm query parameter `?conf_threshold=0.25` nếu người dùng tùy chỉnh.
3. **Tiếp nhận & Phòng vệ tại FastAPI**:
   - FastAPI đọc headers `Content-Type: multipart/form-data`.
   - Kiểm tra định dạng đuôi file trong whitelist: `[".jpg", ".jpeg", ".png", ".webp"]`.
   - Sử dụng thư viện `PIL.Image.open(io.BytesIO(contents)).verify()` để xác thực luồng byte có đúng là ma trận ảnh hợp lệ hay không, ngăn chặn triệt để tấn công upload file giả mạo hoặc file bị lỗi giữa chừng.
4. **Xử lý tại AI Model (YOLOv8n V3)**:
   - Mô hình AI nằm sẵn trong bộ nhớ RAM từ khi khởi động server.
   - Quá trình suy luận tính toán trên tensor ảnh đầu vào chuẩn hóa kích thước 640x640.
   - Đầu ra của mạng nơ-ron là các hộp dự đoán `(x1, y1, x2, y2, confidence, class_id)`.
   - Các hộp có độ tin cậy nhỏ hơn `conf_threshold` sẽ bị loại bỏ hoàn toàn.
   - Các hộp hợp lệ được chuyển đổi sang kích thước ảnh gốc của người dùng.
5. **Gom nhóm nghiệp vụ & Truy vấn Cơ sở Dữ liệu**:
   - `prediction_service.py` tổng hợp các đốm bệnh cùng loại. Ví dụ: Phát hiện 4 đốm `Tomato___Bacterial_spot` (max conf: 0.85) và 1 đốm `Tomato___Early_blight` (conf: 0.42).
   - Xác định bệnh có độ tin cậy cao nhất là `Tomato___Bacterial_spot`.
   - Truy vấn bảng `diseases` với `id = "tomato_bacterial_spot"` để lấy toàn bộ thông tin khoa học, triệu chứng và giải pháp IPM.
6. **Lưu vết Lịch sử (Persistence)**:
   - Một bản ghi `DiagnosisHistory` được tạo với `id` dạng UUID v4, lưu đường dẫn ảnh tĩnh `/uploads/xxx.jpg`, danh sách bounding box và thời gian theo chuẩn UTC.
7. **Hiển thị Phía Trình duyệt (Rendering)**:
   - React nhận JSON trả về từ backend, đối chiếu với interface `DiagnosisResult`.
   - Sử dụng CSS Absolute Positioning kết hợp với tỷ lệ ma trận ảnh để vẽ khung chữ nhật bao quanh từng đốm bệnh trên lá.

---

## 2. Luồng Tra cứu Thư viện Bệnh (Disease Library Data Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng
    participant UI as DiseaseLibraryPage.tsx
    participant API as api.ts (fetchDiseases)
    participant Fast as diseases.py (/api/diseases)
    participant DB as SQLite DB

    User->>UI: Truy cập trang Thư viện bệnh hoặc gõ từ khóa tìm kiếm
    UI->>API: fetchDiseases(searchQuery, selectedPlant)
    API->>Fast: HTTP GET /api/diseases?search=dom&plant=Cà chua
    Fast->>DB: SELECT * FROM diseases WHERE plant = 'Cà chua' AND (name LIKE '%dom%' OR description LIKE '%dom%')
    DB-->>Fast: Danh sách các đối tượng Disease ORM
    Fast-->>API: HTTP 200 OK (List of DiseaseSchema JSON)
    API-->>UI: Danh sách bệnh đã lọc
    UI-->>User: Hiển thị lưới thẻ bệnh (Grid Card) với hình ảnh và mức độ nguy hiểm
```

---

## 3. Luồng Xem Chi tiết Bệnh & Phác đồ IPM (Disease Detail Data Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng
    participant UI as DiseaseDetailPage.tsx
    participant API as api.ts (fetchDiseaseDetail, fetchCareRecommendations)
    participant Fast as diseases.py & care.py
    participant DB as SQLite DB

    User->>UI: Bấm vào một thẻ bệnh (ví dụ: tomato_bacterial_spot)
    UI->>API: 1. fetchDiseaseDetail("tomato_bacterial_spot")
    UI->>API: 2. fetchCareRecommendations("tomato_bacterial_spot")
    
    par Lấy chi tiết bệnh
        API->>Fast: GET /api/diseases/tomato_bacterial_spot
        Fast->>DB: Query bảng diseases theo ID
        DB-->>Fast: Chi tiết bệnh (tên khoa học, triệu chứng 3 giai đoạn, phòng trị)
        Fast-->>API: JSON DiseaseSchema
    and Lấy khuyến nghị chăm sóc
        API->>Fast: GET /api/care/tomato_bacterial_spot
        Fast->>DB: Query bảng care_recommendations theo disease_id
        DB-->>Fast: Danh sách các biện pháp phòng trị
        Fast-->>API: JSON List[CareRecommendationSchema]
    end

    API-->>UI: Cập nhật State: disease & careItems
    UI-->>User: Hiển thị giao diện bách khoa toàn thư đầy đủ triệu chứng và biện pháp xử lý
```

---

## 4. Luồng Quản lý Lịch sử Chẩn đoán (History Management Data Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Người dùng
    participant UI as HistoryPage.tsx
    participant API as api.ts (fetchHistory, deleteHistoryItem)
    participant Fast as history.py (/api/history)
    participant DB as SQLite DB

    User->>UI: Mở tab "Lịch sử"
    UI->>API: fetchHistory()
    API->>Fast: HTTP GET /api/history
    Fast->>DB: SELECT * FROM diagnosis_history ORDER BY created_at DESC
    DB-->>Fast: Danh sách các lần chẩn đoán
    Fast-->>API: HTTP 200 OK (JSON List)
    API-->>UI: Danh sách lịch sử
    UI-->>User: Hiển thị danh sách các mẫu lá kèm ảnh, tên bệnh và thời gian

    opt Người dùng bấm "Xóa bản ghi"
        User->>UI: Bấm icon thùng rác xóa bản ghi
        UI->>API: deleteHistoryItem(historyId)
        API->>Fast: HTTP DELETE /api/history/{historyId}
        Fast->>DB: DELETE FROM diagnosis_history WHERE id = historyId
        DB-->>Fast: Commit thành công
        Fast-->>API: HTTP 204 No Content
        API-->>UI: Xóa thành công
        UI->>UI: Cập nhật UI loại bỏ thẻ bị xóa khỏi danh sách
    end
```
