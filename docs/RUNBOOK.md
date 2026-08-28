# Cẩm nang Vận hành & Cài đặt Hệ thống (OPERATIONAL RUNBOOK)

Tài liệu này cung cấp hướng dẫn từng bước từ đầu (Step-by-Step) để cài đặt môi trường, khởi động Backend, khởi động Frontend, kiểm tra kết nối API, chạy bộ test tự động và đóng gói sản phẩm.

---

## 1. Yêu cầu Tiền đề (Prerequisites)

- **Hệ điều hành**: Windows 10/11, macOS, hoặc Ubuntu Linux.
- **Python**: Phiên bản `3.10` trở lên (Khuyến nghị Python 3.10, 3.11 hoặc 3.13).
- **Node.js**: Phiên bản `18.x` hoặc `20.x` LTS trở lên.
- **Git**: Đã cài đặt trên máy.

---

## 2. Cài đặt Môi trường & Dependencies

### 2.1. Cài đặt Backend Dependencies
Mở PowerShell hoặc Terminal tại thư mục gốc của dự án (`c:\Users\Admin\Leaf-Disease-Detection`):

```powershell
# Di chuyển vào thư mục backend
cd backend

# Tạo môi trường ảo Python (Virtual Environment)
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
# source .venv/bin/activate

# Nâng cấp pip và cài đặt các thư viện bắt buộc
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.2. Cài đặt Frontend Dependencies
Mở một cửa sổ Terminal khác:

```powershell
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt toàn bộ packages Node.js
npm install
```

---

## 3. Khởi động Hệ thống (Running the Application)

### 3.1. Khởi động Backend API Server
Trong cửa sổ terminal của `backend` (đã kích hoạt `.venv`):

```powershell
# Cách 1: Chạy trực tiếp qua Uvicorn module
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Cách 2: Chạy thông qua script chính
python -m app.main
```
*Khi khởi động thành công, server sẽ lắng nghe tại `http://localhost:8000`. Console sẽ hiển thị thông báo đã nạp mô hình `tomato_v3/best.pt` và seed dữ liệu database hoàn tất.*

### 3.2. Khởi động Frontend Dev Server
Trong cửa sổ terminal của `frontend`:

```powershell
npm run dev
```
*Frontend sẽ khởi chạy tại `http://localhost:3000` (hoặc `http://localhost:5173` tùy thiết lập). Hãy mở trình duyệt và truy cập `http://localhost:3000`.*

---

## 4. Kiểm tra Kết nối & Kiểm định Hệ thống (Health Check & Verification)

### 4.1. Kiểm tra Trạng thái API & Model qua Endpoint `/health`
Bạn có thể kiểm tra nhanh bằng PowerShell hoặc cURL:

```powershell
curl http://127.0.0.1:8000/api/health
```

**Phản hồi kỳ vọng (HTTP 200 OK)**:
```json
{
  "status": "ok",
  "service": "LeafAI Backend",
  "version": "1.0.0",
  "model": {
    "type": "yolo",
    "path": "model/tomato_v3/best.pt",
    "loaded": true,
    "confidence_threshold": 0.25,
    "device": "cpu"
  }
}
```

### 4.2. Tra cứu Tài liệu OpenAPI / Swagger UI
Truy cập trên trình duyệt web:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc UI**: `http://localhost:8000/redoc`

---

## 5. Chạy Bộ Kiểm thử Tự động (Running Automated Tests)

Hệ thống đi kèm bộ kiểm thử tự động toàn diện dùng `pytest` bao gồm 16 test cases cho API và bộ test kiểm định suy luận YOLO.

```powershell
# Chuyển vào thư mục backend
cd backend

# Chạy toàn bộ test suites
pytest -v

# Chạy riêng kiểm thử API Endpoints
pytest -v tests/test_api.py

# Chạy riêng kiểm thử AI YOLO Service
pytest -v tests/test_yolo_service.py
```

**Kết quả mong đợi**: Tất cả các test cases đều đạt trạng thái `PASSED (100%)`.

---

## 6. Kiểm định Tính năng trên Giao diện Web (Manual Verification Flow)

1. **Kiểm tra Trang chủ**:
   - Truy cập `http://localhost:3000`, quan sát Hero Banner, hiệu ứng 3D Leaf xoay tương tác và thống kê độ chính xác mô hình V3.
2. **Kiểm tra Chẩn đoán tải ảnh**:
   - Chuyển sang tab **Chẩn đoán**.
   - Bấm "Chọn ảnh từ thiết bị", chọn một ảnh lá bệnh (ví dụ trong thư mục `training/datasets/processed/tomato_v2/images/test/`).
   - Quan sát hiệu ứng quét ảnh, sau đó xác nhận xuất hiện các khung chữ nhật Bounding Box và Thẻ chẩn đoán bệnh chính.
3. **Kiểm tra Chụp ảnh Webcam/Camera**:
   - Bấm "Chụp ảnh từ camera", cấp quyền truy cập camera cho trình duyệt, bấm "Chụp ảnh" và kiểm tra kết quả phân tích.
4. **Kiểm tra Thư viện bệnh**:
   - Mở tab **Thư viện bệnh**, gõ "đốm" vào ô tìm kiếm, bấm vào thẻ "Đốm vi khuẩn trên lá cà chua" để xem toàn bộ triệu chứng 3 giai đoạn và phác đồ IPM.
5. **Kiểm tra Lịch sử**:
   - Mở tab **Lịch sử**, kiểm tra mẫu lá vừa chẩn đoán đã được lưu vào danh sách. Thử bấm nút "Xóa bản ghi" để xác nhận tính năng xóa hoạt động tốt.

---

## 7. Đóng gói cho Môi trường Production (Production Build)

### 7.1. Build Frontend Bundle
```powershell
cd frontend
npm run build
```
*Thư mục `frontend/dist/` sẽ được tạo ra chứa mã nguồn HTML/JS/CSS đã được nén và tối ưu hóa tối đa.*

### 7.2. Chạy Backend với Multi-workers trong Production
```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
