# Ma trận Ánh xạ Tập tin - Chức năng - Tính năng (FILE FEATURE MATRIX)

Tài liệu này tổng hợp toàn bộ các tập tin quan trọng trong codebase **LEAF_AI**, làm rõ vai trò, tính năng phục vụ, thành phần nào gọi tới nó và nó phụ thuộc/gọi tới những thành phần nào.

---

## 1. Backend Core & Services Matrix

| Tập tin | Vai trò / Nhiệm vụ cốt lõi | Tính năng phục vụ | Được gọi / Import bởi | Gọi / Phụ thuộc vào |
|---|---|---|---|---|
| [main.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/main.py) | Khởi động FastAPI server, cấu hình CORS, static files `/uploads`, nạp seed database | Toàn bộ hệ thống Backend | Uvicorn / Khởi động server | `config.py`, `seed.py`, tất cả routers trong `app/api/endpoints/*` |
| [config.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/core/config.py) | Đọc ENV, quản lý cấu hình tập trung (`MODEL_PATH`, `THRESHOLD`, `DATABASE_URL`) | Cấu hình & Tích hợp Model | `main.py`, `session.py`, `health.py`, `prediction_service.py`, `yolo_model_service.py` | `pydantic_settings.BaseSettings`, `os` |
| [session.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/database/session.py) | Tạo SQLAlchemy Engine, SessionLocal và dependency `get_db` | Quản lý phiên cơ sở dữ liệu | Tất cả API Endpoints và Services cần truy vấn DB | `config.settings.DATABASE_URL`, `sqlalchemy` |
| [models.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/database/models.py) | Định nghĩa ORM models: `Disease`, `CareRecommendation`, `DiagnosisHistory` | Lưu trữ dữ liệu quan hệ | `session.py`, `seed.py`, `prediction_service.py`, tất cả endpoints | `sqlalchemy.orm.declarative_base`, `Base` |
| [seed.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/database/seed.py) | Khởi tạo bảng SQLite, migration các cột mới và nạp dữ liệu bách khoa toàn thư | Khởi tạo dữ liệu & Migration | `main.py` (sự kiện `@app.on_event("startup")`) | `models.py`, `session.py`, `leafai.db` |
| [base_model_service.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/base_model_service.py) | Abstract Base Class định nghĩa interface chuẩn `predict()` cho mọi AI Model | Trừu tượng hóa AI Layer | `yolo_model_service.py`, `model_service.py` | `abc.ABC`, `abc.abstractmethod` |
| [yolo_model_service.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/yolo_model_service.py) | Tải weights PyTorch `best.pt`, chạy suy luận YOLOv8, lọc ngưỡng, chuẩn hóa bbox pixel | AI Inference & Object Detection | `prediction_service.py`, `test_yolo_service.py` | `ultralytics.YOLO`, `base_model_service.py`, `config.settings` |
| [model_service.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/model_service.py) | Factory tạo Model Service (Mock hoặc YOLO) dựa trên biến môi trường | Dependency Injection cho AI | `test_yolo_service.py` | `yolo_model_service.py`, `base_model_service.py` |
| [prediction_service.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/services/prediction_service.py) | Điều phối luồng chẩn đoán: lưu ảnh, gọi AI, gom nhóm đa bệnh, truy vấn DB, lưu lịch sử | Chẩn đoán AI & Báo cáo kết quả | `api/endpoints/predict.py` | `yolo_model_service.py`, `models.py`, `schemas/diagnosis.py` |
| [image.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/utils/image.py) | Tiện ích kiểm tra định dạng và dung lượng file ảnh upload | Kiểm tra hợp lệ đầu vào | `api/endpoints/predict.py` | `os`, `PIL` |

---

## 2. Backend API Endpoints Matrix

| Tập tin Endpoint | Phương thức HTTP & URL | Vai trò xử lý | Gọi tới Service / DB | Trả về Schema |
|---|---|---|---|---|
| [health.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/api/endpoints/health.py) | `GET /api/health` | Kiểm tra trạng thái máy chủ, model path và tình trạng nạp model | `os.path.exists(settings.MODEL_PATH)` | `{"status": "ok", "service": "...", "model": {...}}` |
| [predict.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/api/endpoints/predict.py) | `POST /api/predict` | Tiếp nhận file ảnh, kiểm tra tính toàn vẹn `PIL.verify()`, gọi chẩn đoán | `prediction_service.process_prediction()` | [DiagnosisResult](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/schemas/diagnosis.py) |
| [history.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/api/endpoints/history.py) | `GET /api/history`<br>`GET /api/history/{id}`<br>`DELETE /api/history/{id}` | Lấy danh sách lịch sử, xem chi tiết và xóa bản ghi chẩn đoán | Truy vấn / Xóa trực tiếp trên bảng `DiagnosisHistory` qua `db: Session` | [DiagnosisHistoryResponse](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/schemas/diagnosis.py) |
| [diseases.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/api/endpoints/diseases.py) | `GET /api/diseases`<br>`GET /api/diseases/{id}` | Tra cứu danh bạ bệnh, hỗ trợ tìm kiếm theo tên và lọc theo loài cây | Truy vấn bảng `Disease` | [DiseaseSchema](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/schemas/disease.py) |
| [care.py](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/api/endpoints/care.py) | `GET /api/care/{disease_id}` | Lấy danh sách các khuyến nghị điều trị và phòng ngừa theo bệnh | Truy vấn bảng `CareRecommendation` | [CareRecommendationSchema](file:///c:/Users/Admin/Leaf-Disease-Detection/backend/app/schemas/disease.py) |

---

## 3. Frontend Pages & Components Matrix

| Tập tin Frontend | Vai trò giao diện | Được gọi bởi | Gọi / Tương tác với | Dữ liệu & State quản lý |
|---|---|---|---|---|
| [App.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/App.tsx) | Root Component, quản lý thanh điều hướng, Router điều khiển màn hình active | `main.tsx` | `Navbar`, `BottomNav`, `HomePage`, `DiagnosePage`, `DiseaseLibraryPage`, `DiseaseDetailPage`, `CarePage`, `HistoryPage`, `AboutPage` | `currentTab`, `selectedDiseaseId` |
| [HomePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/HomePage.tsx) | Màn hình trang chủ: Hero banner, thống kê mô hình, nút chuyển hướng | `App.tsx` | Callback `onNavigate` | Không có state phức tạp |
| [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | Màn hình chẩn đoán: Upload file, Webcam capture, vẽ Bounding Box, báo cáo AI | `App.tsx` | `services/api.ts.diagnoseLeaf`, `SafeImage` | `file`, `preview`, `analyzing`, `result`, `isCameraOpen`, `videoStream` |
| [DiseaseLibraryPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiseaseLibraryPage.tsx) | Màn hình danh mục bệnh: Tìm kiếm, lọc theo cây trồng, hiển thị thẻ bệnh | `App.tsx` | `services/api.ts.fetchDiseases`, `SafeImage` | `diseases`, `searchQuery`, `selectedPlant`, `loading` |
| [DiseaseDetailPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiseaseDetailPage.tsx) | Màn hình bách khoa toàn thư: Tên khoa học, triệu chứng 3 giai đoạn, cẩm nang IPM | `App.tsx` | `services/api.ts.fetchDiseaseDetail`, `fetchCareRecommendations`, `SafeImage` | `disease`, `careItems`, `loading`, `activeStageTab` |
| [CarePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/CarePage.tsx) | Màn hình hướng dẫn phòng trừ và quản lý dịch hại tổng hợp chung | `App.tsx` | `services/api.ts.fetchCareRecommendations` | `recommendations`, `loading` |
| [HistoryPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/HistoryPage.tsx) | Màn hình lịch sử: Xem lại các lần chẩn đoán quá khứ và nút xóa bản ghi | `App.tsx` | `services/api.ts.fetchHistory`, `deleteHistoryItem` | `history`, `loading` |
| [AboutPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/AboutPage.tsx) | Màn hình giới thiệu dự án, kiến trúc kỹ thuật và sứ mệnh nông nghiệp | `App.tsx` | Static information | Không có state |
| [SafeImage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/SafeImage.tsx) | Component hiển thị hình ảnh an toàn, tự động kích hoạt fallback khi ảnh lỗi | `DiagnosePage`, `DiseaseLibraryPage`, `DiseaseDetailPage` | Thẻ `<img>` và sự kiện `onError` | `hasError`, `isLoading` |
| [Navbar.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/Navbar.tsx) | Thanh điều hướng đầu trang hiển thị trên Desktop / Laptop | `App.tsx` | Callback chuyển tab `onNavigate` | Active navigation item |
| [BottomNav.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/BottomNav.tsx) | Thanh điều hướng đáy màn hình tối ưu cho trải nghiệm ngón tay cái trên Mobile | `App.tsx` | Callback chuyển tab `onNavigate` | Active navigation item |
| [ThreeLeaf.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/ThreeLeaf.tsx) | Trình diễn mô hình 3D Procedural Leaf bằng Three.js | `HomePage.tsx` | `three.js` (Canvas WebGL) | Animation frame loop, rotation matrix |
| [CanvasShader.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/CanvasShader.tsx) | Hiệu ứng nền Organic Gradient WebGL Shader | `App.tsx` | WebGL Context, GLSL Fragment Shader | Shader uniforms (time, resolution, mouse) |
| [api.ts](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/services/api.ts) | HTTP Client bọc các hàm `fetch()` gọi tới backend qua reverse proxy | Tất cả Pages | `/api/*` endpoints | Trả về Promise chứa dữ liệu đã parse JSON |
| [index.ts (types)](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/types/index.ts) | Định nghĩa toàn bộ kiểu dữ liệu TypeScript đồng bộ với Backend Pydantic | Toàn bộ ứng dụng Frontend | Pydantic Schemas | `DiagnosisResult`, `Disease`, `CareRecommendation` |

---

## 4. AI Training & Benchmark Matrix

| Script Huấn luyện | Mục tiêu kỹ thuật | Input | Output | Mô hình tạo ra |
|---|---|---|---|---|
| [train_tomato.py](file:///c:/Users/Admin/Leaf-Disease-Detection/training/scripts/train_tomato.py) | Huấn luyện Baseline V1 | `datasets/processed/tomato/data.yaml` (320x320) | `runs/tomato/` | `model/tomato/best.pt` |
| [train_tomato_v2.py](file:///c:/Users/Admin/Leaf-Disease-Detection/training/scripts/train_tomato_v2.py) | Huấn luyện V2 triệt tiêu False Positive nhờ Hard Negatives | `datasets/processed/tomato_v2/data.yaml` (384x384) | `runs/tomato_v2/` | `model/tomato_v2/best.pt` (Backup) |
| [train_tomato_v3.py](file:///c:/Users/Admin/Leaf-Disease-Detection/training/scripts/train_tomato_v3.py) | Huấn luyện V3 Production tối ưu nhận diện đốm vi khuẩn nhỏ | `datasets/processed/tomato_v3/data.yaml` (640x640) | `runs/tomato_v3/` | `model/tomato_v3/best.pt` (Active Production) |
| [audit_bacterial_spot.py](file:///c:/Users/Admin/Leaf-Disease-Detection/training/scripts/audit_bacterial_spot.py) | Kiểm toán chuyên sâu các trường hợp đốm vi khuẩn kích thước nhỏ | Bounding box ground truth vs proposals | Báo cáo `audit_metrics.json` | Phân tích Recall theo kích thước tổn thương |
| [test_v3_integration_api.py](file:///c:/Users/Admin/Leaf-Disease-Detection/training/scripts/test_v3_integration_api.py) | Kiểm thử toàn diện API backend với mô hình V3 trên ảnh thật | Bộ ảnh test thực tế | Báo cáo tích hợp tại `docs/` | Xác thực end-to-end hiệu năng hệ thống |
