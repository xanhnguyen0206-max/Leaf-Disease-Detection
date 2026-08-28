# Cẩm nang Xử lý Sự cố & Khắc phục Lỗi (TROUBLESHOOTING GUIDE)

Tài liệu này tổng hợp toàn bộ các sự cố thường gặp trong quá trình cài đặt, phát triển, vận hành và kiểm thử hệ thống **LEAF_AI**, kèm theo nguyên nhân cốt lõi, cách kiểm tra và phương án khắc phục triệt để.

---

## 1. Bảng Tra cứu Nhanh Sự cố (Troubleshooting Quick Reference)

| Triệu chứng lỗi (Symptoms) | Nguyên nhân khả dĩ (Root Cause) | Cách kiểm tra (Verification) | Hướng xử lý (Fix) |
|---|---|---|---|
| **Backend không khởi động được (Port 8000 in use)** | Cổng 8000 đã bị chiếm bởi tiến trình khác | `netstat -ano \| findstr :8000` | Tắt tiến trình cũ: `taskkill /PID <PID> /F` hoặc đổi port trong uvicorn |
| **Frontend không chạy được (Port 3000 in use)** | Vite không chiếm được port 3000 | Quan sát log terminal Vite | Đổi port trong `vite.config.ts` hoặc tắt app đang chiếm cổng |
| **Lỗi `ModuleNotFoundError` khi chạy Python** | Chưa cài dependencies hoặc chưa kích hoạt `.venv` | `pip list` | Chạy `pip install -r requirements.txt` trong virtualenv |
| **Lỗi `FileNotFoundError: best.pt not found`** | Đường dẫn model sai hoặc chưa tải weights | Kiểm tra file tại `model/tomato_v3/best.pt` | Đặt biến môi trường `MODEL_PATH` trỏ đúng file weights thực tế |
| **Lỗi Upload ảnh: `HTTP 400 Định dạng ảnh không hỗ trợ`** | Tải lên file không phải `.jpg`, `.png`, `.webp` | Kiểm tra đuôi file tải lên | Chọn đúng định dạng ảnh chuẩn |
| **Lỗi Upload ảnh: `HTTP 400 File bị hỏng hoặc rỗng`** | File 0 byte hoặc file văn bản đổi tên thành `.jpg` | Kiểm tra dung lượng và xem ảnh trước | Sử dụng ảnh chụp thực tế có thể mở bằng trình xem ảnh |
| **Ảnh bị vỡ hoặc icon hình chữ nhật đen trên UI** | Đường dẫn ảnh trong DB bị sai hoặc file upload đã bị xóa | Mở trực tiếp link `/uploads/...` trên trình duyệt | Hệ thống đã có `SafeImage.tsx` tự động hiển thị ảnh dự phòng trang nhã |
| **Cơ sở dữ liệu SQLite bị khóa: `OperationalError: database is locked`** | Nhiều tiến trình cùng ghi vào SQLite đồng thời | Kiểm tra các tiến trình Python đang chạy | Khởi động lại backend hoặc tăng timeout SQLite |
| **Không mở được Camera / Webcam trên trình duyệt** | Trình duyệt chưa được cấp quyền truy cập Camera | Kiểm tra biểu tượng Camera trên thanh địa chỉ URL | Bấm "Cho phép (Allow)" truy cập Camera trong cài đặt trình duyệt |
| **YOLO không phát hiện được vết bệnh nào (No detection)** | Ảnh lá quá mờ, chụp quá xa hoặc ngưỡng tin cậy quá cao | Thử giảm `conf_threshold` xuống `0.15` | Chụp cận cảnh rõ nét đốm lá hoặc điều chỉnh thanh ngưỡng |
| **Bounding box lệch vị trí so với đốm bệnh trên màn hình** | Sai tỷ lệ co giãn giữa ảnh thực và ảnh hiển thị CSS | Kiểm tra thuộc tính `object-fit: contain` | Giữ nguyên tỷ lệ khung hình thực của thẻ chứa ảnh trong React |

---

## 2. Hướng dẫn Chi tiết Các Tình huống Sự cố Điển hình

### 2.1. Sự cố Cổng mạng bị Chiếm dụng (Port Conflict)
- **Hiện tượng**: Khi gõ lệnh `uvicorn app.main:app --port 8000`, terminal báo lỗi: `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): only one usage of each socket address is normally permitted`.
- **Cách xử lý trên Windows PowerShell**:
  ```powershell
  # Tìm PID của tiến trình đang chiếm cổng 8000
  netstat -ano | findstr :8000
  
  # Giả sử PID là 12345, tiến hành dừng tiến trình:
  taskkill /PID 12345 /F
  ```

---

### 2.2. Sự cố Không tìm thấy File Model Weights (Model Not Found)
- **Hiện tượng**: Backend trả về lỗi `HTTP 500: Lỗi cấu hình hệ thống AI: YOLO model file not found at ...`.
- **Nguyên nhân**: File `best.pt` nằm ở thư mục khác hoặc biến môi trường `MODEL_PATH` bị cấu hình sai đường dẫn tương đối.
- **Cách khắc phục**:
  1. Kiểm tra sự tồn tại của file:
     `Test-Path "c:\Users\Admin\Leaf-Disease-Detection\model\tomato_v3\best.pt"`
  2. Nếu chuyển sang môi trường khác, hãy export đường dẫn tuyệt đối:
     ```powershell
     $env:MODEL_PATH="c:/Users/Admin/Leaf-Disease-Detection/model/tomato_v3/best.pt"
     python -m app.main
     ```

---

### 2.3. Sự cố Lỗi Kết nối Reverse Proxy (Frontend gọi API báo `ECONNREFUSED`)
- **Hiện tượng**: Khi bấm nút "Chẩn đoán" trên trình duyệt, console báo lỗi đỏ: `POST http://localhost:3000/api/predict net::ERR_CONNECTION_REFUSED`.
- **Nguyên nhân**: Backend FastAPI trên cổng `8000` chưa được bật, khiến Vite Proxy không thể chuyển tiếp request.
- **Cách khắc phục**: Mở một cửa sổ terminal riêng, khởi động backend tại cổng 8000 trước:
  ```powershell
  cd backend
  python -m app.main
  ```

---

### 2.4. Sự cố Cột Cơ sở Dữ liệu Mới Không Tồn Tại (SQLite Schema Migration)
- **Hiện tượng**: Báo lỗi `sqlite3.OperationalError: no such column: primary_disease`.
- **Giải pháp sẵn có**: Backend của LEAF_AI đã tích hợp hàm `_ensure_schema_columns()` trong [seed.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/database/seed.py). Khi khởi động lại server, hàm này tự động thực thi các lệnh `PRAGMA table_info` và `ALTER TABLE ADD COLUMN` để nâng cấp schema mà không làm mất dữ liệu cũ.
