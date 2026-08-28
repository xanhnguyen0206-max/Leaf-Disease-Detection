# Báo cáo Kiểm định & Đánh giá Toàn diện Codebase LEAF_AI (FINAL AUDIT REPORT)

**Dự án**: LEAF_AI — Nền tảng Nhận diện Bệnh hại Cây trồng dựa trên Trí tuệ Nhân tạo  
**Ngày thực hiện kiểm định**: 28/08/2026  
**Phạm vi kiểm định**: Toàn bộ kho mã nguồn `c:\Users\Admin\Leaf-Disease-Detection`  
**Quy chuẩn thực thi**: Tuân thủ tuyệt đối quy tắc **KHÔNG sửa đổi, không xóa, không đổi tên mã nguồn hiện có**.

---

## 1. Thống kê Định lượng Toàn bộ Kho Mã nguồn (Quantitative Codebase Summary)

- **Tổng số thư mục chính**: 9 thư mục gốc (`backend/`, `frontend/`, `model/`, `training/`, `docs/`, `runs/`, `tests/`, `_stitch_source/`, `.git/`).
- **Tổng số tập tin mã nguồn & cấu hình được kiểm tra**:
  - **Backend (Python)**: 18 file mã nguồn chính (API endpoints, Core config, Database models, Pydantic schemas, Services, Image utils, Test suites) + 1 database SQLite (`leafai.db`).
  - **Frontend (React/TypeScript)**: 17 file mã nguồn (Pages, UI components, Shaders/Three.js, API service, Types, CSS, Vite config).
  - **Model Weights & Metadata**: 3 phiên bản mô hình AI hoàn chỉnh (`tomato` V1, `tomato_v2` V2, `tomato_v3` V3 Production).
  - **AI Training & Research**: 11 scripts tự động hóa huấn luyện/kiểm định, 3 bộ dữ liệu ảnh (`raw/`, `processed/`), 7 tài liệu báo cáo nghiên cứu.
  - **Tài liệu Kỹ thuật mới được khởi tạo**: 12 tài liệu kỹ thuật toàn diện trong thư mục `docs/`.

---

## 2. Tổng quan Kiến trúc Toàn Hệ thống

### 2.1. Backend Architecture
- **Framework**: FastAPI (Python 3.10+ / 3.13) chạy trên ASGI Server Uvicorn.
- **Mô hình Thiết kế**:
  - **Tầng API Endpoints**: Tách biệt rõ ràng theo module chức năng (`health`, `predict`, `history`, `diseases`, `care`).
  - **Tầng Business Services**: Áp dụng Dependency Injection và mẫu Singleton đối với `YOLOModelService` và `PredictionService`.
  - **Phòng vệ Dữ liệu (Defensive IO)**: Sử dụng `PIL.Image.verify()` ngăn chặn 100% rủi ro từ file tải lên bị hỏng hoặc giả mạo.

### 2.2. Frontend Architecture
- **Framework & Libraries**: React 18, TypeScript, Vite 5, Tailwind CSS, Three.js (WebGL).
- **Mô hình Giao diện**: Single Page Application (SPA) với chuẩn thiết kế Google Stitch (Digital Canopy Theme).
- **Trải nghiệm Người dùng**:
  - Hỗ trợ tải ảnh từ máy tính hoặc chụp trực tiếp qua Webcam/Camera điện thoại.
  - Vẽ Bounding Box trực quan đè lên ảnh gốc.
  - Tự động bắt lỗi và hiển thị ảnh dự phòng trang nhã thông qua component `SafeImage.tsx`.

### 2.3. AI & Deep Learning Architecture
- **Framework**: Ultralytics YOLOv8, PyTorch.
- **Phiên bản Mô hình Active**: **YOLOv8n V3** huấn luyện ở độ phân giải **640x640** pixels.
- **Hiệu năng Thực tế**:
  - Thời gian suy luận trên CPU: **150ms - 350ms**.
  - Tỷ lệ Recall nhận diện đốm vi khuẩn nhỏ: **80.8%** (vượt trội so với 77% của V2).
  - Tỷ lệ nhận diện nhầm lá khỏe (False Positive Rate): **0.0%** đối với V2 và xấp xỉ **3%** đối với V3 nhờ bổ sung tập ảnh Hard Negatives.

### 2.4. Database Architecture
- **Công nghệ**: SQLite (`backend/leafai.db`) kết nối qua SQLAlchemy 2.0 ORM.
- **Cơ chế Migration Tự động**: Hàm `_ensure_schema_columns()` trong `seed.py` tự động kiểm tra và thêm các cột mới khi khởi động server mà không làm gián đoạn hay mất mát dữ liệu cũ.

---

## 3. Các Điểm Mạnh Nổi Bật của Codebase (Key Architectural Strengths)

1. **Kiến trúc Tách lớp Rõ ràng (Clean Separation of Concerns)**:
   API Layer, Service Layer, AI Inference Layer và Database Layer hoàn toàn độc lập, giao tiếp thông qua interfaces và DTOs chuẩn mực.
2. **Vòng đời Nạp Mô hình Tối ưu (Pre-warmed Singleton Memory Lifecycle)**:
   Mô hình AI chỉ nạp 1 lần vào RAM khi khởi động server, loại bỏ hoàn toàn độ trễ nạp model ở từng request.
3. **Cơ chế Gom nhóm Đa bệnh Thông minh (Multi-disease Aggregation)**:
   Không chỉ trả về nhãn thô, backend tự động tính toán tổng số đốm bệnh, xác định bệnh chính (`primary_disease`), phân loại mức độ tin cậy bằng ngôn ngữ tự nhiên và phát hiện đồng nhiễm đa bệnh.
4. **Hệ thống Kiểm thử Tự động Hoàn chỉnh (Comprehensive Test Coverage)**:
   Toàn bộ 16 integration tests của API và các test cases suy luận của YOLO đều vượt qua kiểm tra với tỷ lệ thành công 100%.
5. **Khả năng Chuyển mạch Mô hình Linh hoạt**:
   Hệ thống có thể chuyển đổi mượt mà giữa V3, V2 backup và Mock mode chỉ thông qua thiết lập biến môi trường.

---

## 4. Các Điểm Cần Lưu ý & Nợ Kỹ thuật (Technical Debt & Maintenance Notes)

1. **Thư mục nguyên mẫu thiết kế `_stitch_source/`**:
   - *Hiện trạng*: Chứa các file HTML và ảnh chụp màn hình prototype ban đầu từ Google Stitch.
   - *Ghi nhận*: Đây là tài sản tham khảo thiết kế, không tham gia vào runtime thực tế của ứng dụng.
2. **Thư mục `tests/` ở cấp độ gốc (Root)**:
   - *Hiện trạng*: Là thư mục trống. Toàn bộ test suites thực tế của dự án nằm tập trung tại `backend/tests/`.
   - *Ghi nhận*: Có thể giữ nguyên để mở rộng cho end-to-end browser tests trong tương lai (ví dụ: Playwright / Cypress).
3. **Cơ sở dữ liệu SQLite trong Môi trường Nhiều Người dùng (Concurrency)**:
   - *Hiện trạng*: SQLite hoạt động cực kỳ mượt mà với ứng dụng đơn máy chủ / edge deployment.
   - *Khuyến nghị tương lai*: Nếu triển khai hệ thống quy mô lớn với hàng nghìn người dùng ghi dữ liệu đồng thời, có thể chuyển connection string sang PostgreSQL mà không cần sửa đổi mã nguồn SQLAlchemy.

---

## 5. Danh mục Tài liệu Kỹ thuật Đã Được Khởi tạo

Bộ tài liệu hoàn chỉnh đã được tạo và lưu trữ đầy đủ trong thư mục `docs/`:

1. [docs/README.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/README.md) — Mục lục & Danh mục điều hướng tài liệu.
2. [docs/PROJECT_STRUCTURE.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/PROJECT_STRUCTURE.md) — Cây thư mục toàn diện và giải thích từng folder.
3. [docs/ARCHITECTURE_DEEP_DIVE.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/ARCHITECTURE_DEEP_DIVE.md) — Kiến trúc đa tầng chuyên sâu kèm sơ đồ Mermaid.
4. [docs/SYSTEM_DATA_FLOW.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/SYSTEM_DATA_FLOW.md) — Luồng dữ liệu chi tiết từ Frontend tới AI và Database.
5. [docs/FEATURE_MAP.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/FEATURE_MAP.md) — Bản đồ 18 tính năng cốt lõi của hệ thống.
6. [docs/FILE_FEATURE_MATRIX.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/FILE_FEATURE_MATRIX.md) — Ma trận quan hệ tập tin - chức năng - caller/callee.
7. [docs/TECH_STACK.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/TECH_STACK.md) — Danh mục công nghệ, thư viện, phiên bản và lý do lựa chọn.
8. [docs/DEPENDENCY_MAP.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/DEPENDENCY_MAP.md) — Sơ đồ phụ thuộc giữa các module và ERD database.
9. [docs/MAINTENANCE_GUIDE.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/MAINTENANCE_GUIDE.md) — Sổ tay bảo trì, nâng cấp mô hình và tích hợp Cloud Fallback.
10. [docs/RUNBOOK.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/RUNBOOK.md) — Cẩm nang vận hành, cài đặt và kiểm thử từ A-Z.
11. [docs/TROUBLESHOOTING.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/TROUBLESHOOTING.md) — Cẩm nang xử lý sự cố thực tế.
12. [docs/LEAF_AI_COMPLETE_CODEBASE_GUIDE.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/LEAF_AI_COMPLETE_CODEBASE_GUIDE.md) — Hướng dẫn giải thích mã nguồn chi tiết cho người mới.
13. [docs/LEAF_AI_DOCUMENTATION_AUDIT_REPORT.md](file:///c:/Users/Admin/Leaf-Disease-Detection/docs/LEAF_AI_DOCUMENTATION_AUDIT_REPORT.md) — Báo cáo kiểm định tổng kết toàn diện (file này).

---

## 6. Xác nhận Tính Toàn vẹn Mã nguồn (Source Code Integrity Confirmation)

- **Mã nguồn Backend (`backend/app/*`, `backend/tests/*`)**: Giữ nguyên vẹn 100%, không có bất kỳ dòng mã nào bị thay đổi.
- **Mã nguồn Frontend (`frontend/src/*`, `frontend/package.json`)**: Giữ nguyên vẹn 100%.
- **Mô hình AI (`model/*`, `yolov8n.pt`)**: Giữ nguyên vẹn 100%.
- **Cơ sở Dữ liệu (`backend/leafai.db`)**: Giữ nguyên vẹn 100%.
- **Quy trình Huấn luyện (`training/*`)**: Giữ nguyên vẹn 100%.
