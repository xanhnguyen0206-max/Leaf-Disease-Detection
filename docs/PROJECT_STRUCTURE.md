# Cấu trúc Thư mục Toàn diện Dự án LEAF_AI (PROJECT STRUCTURE)

Tài liệu này phản ánh **chính xác 100% cấu trúc thư mục và tập tin thực tế** của toàn bộ dự án `LEAF_AI` (`Leaf-Disease-Detection`). Không sử dụng cấu trúc giả định.

---

## 1. Sơ đồ Cây Thư mục Tổng thể (Real Directory Tree)

```text
LEAF_AI/ (c:/Users/Admin/Leaf-Disease-Detection)
│
├── .env.example                          # File mẫu cấu hình biến môi trường
├── .gitignore                            # Khai báo các file/thư mục Git bỏ qua
├── README.md                             # Tài liệu tổng quan gốc của repository
├── yolov8n.pt                            # Weights pre-trained gốc YOLOv8 nano của Ultralytics (COCO)
│
├── backend/                              # [RUNTIME BACKEND] Toàn bộ mã nguồn API Server & Database
│   ├── pytest.ini                        # Cấu hình kiểm thử pytest
│   ├── README.md                         # Hướng dẫn riêng cho Backend
│   ├── requirements.txt                  # Danh sách dependencies Python
│   ├── leafai.db                         # Database SQLite lưu trữ dữ liệu bệnh & lịch sử
│   │
│   ├── app/                              # Package chính của ứng dụng FastAPI
│   │   ├── __init__.py
│   │   ├── main.py                       # Điểm khởi động ứng dụng FastAPI, cấu hình CORS, static files, routers
│   │   │
│   │   ├── api/                          # Tầng định tuyến API (API Routers & Endpoints)
│   │   │   ├── __init__.py
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── health.py             # GET /api/health (Kiểm tra trạng thái hệ thống và AI Model)
│   │   │       ├── predict.py            # POST /api/predict (Tiếp nhận ảnh, chẩn đoán bệnh lá)
│   │   │       ├── history.py            # GET /api/history, GET /api/history/{id}, DELETE /api/history/{id}
│   │   │       ├── diseases.py           # GET /api/diseases, GET /api/diseases/{id} (Thư viện bệnh cây)
│   │   │       └── care.py               # GET /api/care/{disease_id} (Khuyến nghị chăm sóc / IPM)
│   │   │
│   │   ├── core/                         # Cấu hình và thiết lập cốt lõi
│   │   │   ├── __init__.py
│   │   │   └── config.py                 # Pydantic BaseSettings, đọc ENV, định nghĩa MODEL_PATH, THRESHOLD, PORT
│   │   │
│   │   ├── database/                     # Tầng cơ sở dữ liệu SQLAlchemy
│   │   │   ├── __init__.py
│   │   │   ├── session.py                # Khởi tạo SQLAlchemy Engine, SessionLocal, get_db Dependency
│   │   │   ├── models.py                 # ORM Models (Disease, CareRecommendation, DiagnosisHistory)
│   │   │   └── seed.py                   # Migration schema SQLite & nạp dữ liệu mẫu ban đầu
│   │   │
│   │   ├── schemas/                      # Data Transfer Objects (Pydantic Models) cho validation & serialize
│   │   │   ├── __init__.py
│   │   │   ├── prediction.py             # Schemas cho BoundingBox, DetectionItem, DiseaseGroupSummary
│   │   │   ├── diagnosis.py              # Schemas cho DiagnosisResult, DiagnosisHistoryResponse
│   │   │   └── disease.py                # Schemas cho DiseaseSchema, CareRecommendationSchema
│   │   │
│   │   ├── services/                     # Tầng Business Logic & AI Model Inference
│   │   │   ├── __init__.py
│   │   │   ├── base_model_service.py     # Abstract Base Class định nghĩa interface chuẩn cho AI Model
│   │   │   ├── yolo_model_service.py     # Triển khai YOLOv8 inference, lọc threshold, tính BoundingBox pixel
│   │   │   ├── model_service.py          # Factory singleton & Mock Model Service
│   │   │   └── prediction_service.py     # Điều phối toàn bộ luồng: lưu ảnh, gọi AI, gom nhóm, truy vấn DB, lưu lịch sử
│   │   │
│   │   └── utils/                        # Tiện ích bổ trợ
│   │       ├── __init__.py
│   │       └── image.py                  # Hàm kiểm tra định dạng và dung lượng file ảnh
│   │
│   ├── tests/                            # Bộ kiểm thử tự động của Backend
│   │   ├── __init__.py
│   │   ├── test_api.py                   # 16 integration tests kiểm thử toàn bộ API endpoints
│   │   └── test_yolo_service.py          # Unit & regression tests kiểm thử mô hình YOLO và service
│   │
│   └── uploads/                          # Thư mục lưu trữ ảnh tải lên từ người dùng (phục vụ qua /uploads)
│
├── frontend/                             # [RUNTIME FRONTEND] Ứng dụng Single Page Application (SPA)
│   ├── index.html                        # HTML entry point, nạp Google Fonts & Material Symbols
│   ├── package.json                      # Quản lý dependencies Node.js (React, Vite, Tailwind, Three.js)
│   ├── package-lock.json                 # Khóa phiên bản dependencies npm
│   ├── postcss.config.js                 # Cấu hình PostCSS cho Tailwind
│   ├── tailwind.config.js                # Cấu hình theme màu sắc Stitch UI, Glassmorphism, Typography
│   ├── tsconfig.json                     # Cấu hình TypeScript compiler
│   ├── tsconfig.node.json                # Cấu hình TypeScript cho Vite config
│   ├── vite.config.ts                    # Cấu hình Vite dev server & Reverse Proxy (/api, /uploads -> :8000)
│   ├── README.md                         # Hướng dẫn riêng cho Frontend
│   │
│   ├── public/                           # Static assets không qua bundling
│   │
│   └── src/                              # Mã nguồn chính của Frontend
│       ├── main.tsx                      # Entry point React 18 createRoot
│       ├── App.tsx                       # Root Component, quản lý Router, View State, Navigation
│       ├── index.css                     # Global CSS, Tailwind directives, custom glassmorphism styles
│       │
│       ├── assets/                       # Thư mục chứa hình ảnh, icons nội bộ
│       │
│       ├── components/                   # Các UI Components tái sử dụng
│       │   ├── Navbar.tsx                # Header điều hướng chính trên Desktop/Tablet
│       │   ├── BottomNav.tsx             # Bottom Navigation Bar tối ưu cho Mobile
│       │   ├── SafeImage.tsx             # Component hiển thị ảnh chống lỗi vỡ ảnh (fallback tự động)
│       │   ├── CanvasShader.tsx          # Hiệu ứng nền Organic Ambient WebGL Shader
│       │   └── ThreeLeaf.tsx             # 3D Procedural Leaf rendering bằng Three.js
│       │
│       ├── pages/                        # Các màn hình (Views) của ứng dụng
│       │   ├── HomePage.tsx              # Trang chủ: Hero banner, thống kê, phím tắt chẩn đoán nhanh
│       │   ├── DiagnosePage.tsx          # Trang chẩn đoán: Upload ảnh, Camera, vẽ Bounding Box, báo cáo AI
│       │   ├── DiseaseLibraryPage.tsx    # Thư viện bệnh hại: Tìm kiếm, lọc theo cây, danh mục bệnh
│       │   ├── DiseaseDetailPage.tsx     # Chi tiết bệnh: Triệu chứng từng giai đoạn, phác đồ IPM chuyên sâu
│       │   ├── CarePage.tsx              # Hướng dẫn chăm sóc & quản lý dịch hại tổng hợp IPM
│       │   ├── HistoryPage.tsx           # Lịch sử chẩn đoán: Xem lại các lần khám lá và xóa bản ghi
│       │   └── AboutPage.tsx             # Giới thiệu dự án, sứ mệnh và kiến trúc kỹ thuật
│       │
│       ├── services/                     # Tầng kết nối API
│       │   └── api.ts                    # Client HTTP (fetch API) bọc tất cả endpoint REST Backend
│       │
│       └── types/                        # TypeScript Type Definitions
│           └── index.ts                  # Khai báo interfaces: DiagnosisResult, Disease, Care, DetectionItem...
│
├── model/                                # [RUNTIME AI WEIGHTS] Nơi chứa các phiên bản mô hình AI đã huấn luyện
│   ├── README.md                         # Hướng dẫn & quy chuẩn lưu trữ Model Weights
│   ├── tomato/                           # Model V1 Baseline (320x320)
│   │   ├── best.pt                       # PyTorch weights V1
│   │   ├── classes.json                  # Mapping id -> class name
│   │   └── metadata.json                 # Thông số huấn luyện và metrics V1
│   ├── tomato_v2/                        # Model V2 (384x384, bổ sung Hard Negatives)
│   │   ├── best.pt                       # PyTorch weights V2 (Backup/Fallback)
│   │   ├── classes.json                  # Mapping id -> class name V2
│   │   └── metadata.json                 # Metrics và phân tích False Positive V2
│   └── tomato_v3/                        # Model V3 PRODUCTION (640x640, nâng cấp nhận diện Bacterial Spot)
│       ├── best.pt                       # PyTorch weights V3 (Đang nạp trực tiếp vào Backend)
│       ├── classes.json                  # Mapping id -> class name V3
│       └── metadata.json                 # Chi tiết kiểm định V3, mAP, Recall và Confusion Matrix
│
├── training/                             # [OFFLINE TRAINING PIPELINE] Toàn bộ quy trình huấn luyện & nghiên cứu AI
│   ├── datasets/                         # Quản lý dữ liệu huấn luyện
│   │   ├── raw/                          # Dữ liệu ảnh thô tải từ Roboflow / Kaggle
│   │   │   ├── tomato/                   # Dataset thô gốc
│   │   │   └── tomato_extra/             # Dataset bổ sung lá khỏe & bệnh cho V2/V3
│   │   └── processed/                    # Dữ liệu chuẩn hóa format YOLO (images/ labels/ data.yaml)
│   │       ├── tomato/                   # Dataset processed V1
│   │       ├── tomato_v2/                # Dataset processed V2 (kèm hard_negatives)
│   │       └── tomato_v3/                # Dataset processed V3 (tối ưu kích thước 640x640)
│   │
│   ├── scripts/                          # Các script tự động hóa huấn luyện và kiểm định
│   │   ├── prepare_tomato_dataset.py     # Chuẩn hóa dataset V1
│   │   ├── prepare_tomato_v2_dataset.py  # Chuẩn hóa dataset V2 và lọc Hard Negatives
│   │   ├── create_tomato_v3_dataset.py   # Xây dựng dataset V3
│   │   ├── inspect_tomato_extra.py       # Kiểm tra chất lượng dữ liệu bổ sung
│   │   ├── audit_bacterial_spot.py       # Phân tích chuyên sâu lỗi nhận diện Đốm vi khuẩn
│   │   ├── train_tomato.py               # Script huấn luyện YOLOv8 V1
│   │   ├── train_tomato_v2.py            # Script huấn luyện YOLOv8 V2
│   │   ├── train_tomato_v3.py            # Script huấn luyện YOLOv8 V3
│   │   ├── test_inference.py             # Script test inference độc lập trên tập ảnh
│   │   ├── test_v2_integration_api.py   # Test tích hợp API với model V2
│   │   └── test_v3_integration_api.py   # Test tích hợp API với model V3
│   │
│   ├── runs/                             # Logs, checkpoint và biểu đồ đầu ra sau mỗi lần train
│   │   ├── tomato/                       # Output runs V1 (biểu đồ F1, PR, Confusion Matrix, predictions)
│   │   ├── tomato_v2/                    # Output runs V2 (audit, integration tests, curves)
│   │   └── tomato_v3/                    # Output runs V3 (v3_yolov8n_640 weights, benchmark, comparison)
│   │
│   └── docs/                             # Báo cáo khoa học & kỹ thuật chi tiết của các đợt huấn luyện
│       ├── tomato_dataset_report.md
│       ├── tomato_training_report.md
│       ├── tomato_v2_training_report.md
│       ├── tomato_v3_training_report.md
│       ├── tomato_v3_annotation_audit.md
│       ├── bacterial_spot_audit_report.md
│       └── figures_v3/                   # Hình ảnh trực quan hóa kết quả kiểm định V3
│
├── docs/                                 # [DOCUMENTATION ROOT] Bộ tài liệu kỹ thuật hoàn chỉnh của dự án
│   ├── README.md                         # Danh mục và mục lục tài liệu
│   ├── PROJECT_STRUCTURE.md              # Tài liệu cấu trúc thư mục (file này)
│   ├── ARCHITECTURE_DEEP_DIVE.md         # Phân tích kiến trúc đa tầng chuyên sâu
│   ├── SYSTEM_DATA_FLOW.md               # Luồng dữ liệu toàn hệ thống từ Frontend tới AI/DB
│   ├── FEATURE_MAP.md                    # Bản đồ chức năng toàn diện
│   ├── FILE_FEATURE_MATRIX.md            # Ma trận ánh xạ từng tập tin - chức năng - quan hệ gọi
│   ├── TECH_STACK.md                     # Danh mục công nghệ, thư viện, phiên bản và lý do sử dụng
│   ├── DEPENDENCY_MAP.md                 # Sơ đồ phụ thuộc giữa các modules
│   ├── MAINTENANCE_GUIDE.md              # Sổ tay bảo trì, nâng cấp mô hình và mở rộng hệ thống
│   ├── RUNBOOK.md                        # Hướng dẫn vận hành, cài đặt và kiểm thử từ A-Z
│   ├── TROUBLESHOOTING.md                # Cẩm nang xử lý sự cố thực tế
│   ├── LEAF_AI_COMPLETE_CODEBASE_GUIDE.md# Hướng dẫn giải thích mã nguồn chi tiết cho người mới
│   └── LEAF_AI_DOCUMENTATION_AUDIT_REPORT.md # Báo cáo kiểm định toàn diện codebase
│
├── runs/                                 # Thư mục lưu trữ tạm các runs mặc định của Ultralytics
│   └── detect/                           # Cache validation và training mặc định
│
├── tests/                                # Thư mục gốc dự phòng cho generic system tests
│
└── _stitch_source/                       # Bản thiết kế giao diện gốc (Google Stitch Design Prototypes)
    ├── digital_canopy/DESIGN.md          # Quy chuẩn thiết kế giao diện (Màu sắc, Typography, Spacing)
    ├── diagnose_leaf_interactive/        # HTML prototype & screenshot trang Chẩn đoán
    ├── disease_library_interactive/      # HTML prototype & screenshot Thư viện bệnh
    ├── history_interactive/              # HTML prototype & screenshot Lịch sử
    ├── leafai_home_interactive/          # HTML prototype & screenshot Trang chủ
    ├── leaf_ai_premium_motion_experience/# HTML prototype hiệu ứng động cao cấp
    ├── shader/                           # Mã shader WebGL thử nghiệm
    └── three.js/                         # Thử nghiệm Three.js 3D rendering
```

---

## 2. Phân loại Chi tiết Từng Thư mục (Directory Deep Dive)

### 2.1. Thư mục `backend/`
- **Mục đích**: Chứa toàn bộ máy chủ API dịch vụ, cơ sở dữ liệu SQLite, logic nghiệp vụ chẩn đoán bệnh và interface điều khiển mô hình AI.
- **Có sử dụng tại Runtime không?**: **CÓ (BẮT BUỘC)**. Đây là runtime backend chạy trên cổng `8000`.
- **Chi tiết các thư mục con**:
  - `backend/app/`: Mã nguồn chính của ứng dụng FastAPI.
  - `backend/app/api/endpoints/`: Định nghĩa các route REST API (`/health`, `/predict`, `/history`, `/diseases`, `/care`). Nhận request từ HTTP, validate tham số, gọi service và trả về JSON.
  - `backend/app/core/`: Chứa file `config.py` đọc biến môi trường, định cấu hình đường dẫn weights (`MODEL_PATH`), ngưỡng tin cậy (`MODEL_CONFIDENCE_THRESHOLD`), thiết bị (`MODEL_DEVICE: cpu/cuda`).
  - `backend/app/database/`: Chứa kết nối SQLAlchemy (`session.py`), ORM Models (`models.py`), và logic khởi tạo/nâng cấp bảng dữ liệu (`seed.py`).
  - `backend/app/schemas/`: Chứa các Pydantic schema dùng để validate dữ liệu đầu vào và định hình cấu trúc dữ liệu trả về cho API.
  - `backend/app/services/`: Trọng tâm xử lý nghiệp vụ: nạp mô hình YOLO vào RAM khi khởi động, nhận diện đối tượng qua ảnh, gom nhóm bệnh, tính bounding box theo tọa độ thực, truy vấn phác đồ điều trị và lưu lịch sử.
  - `backend/app/utils/`: Chứa các hàm phụ trợ kiểm tra tính hợp lệ của file ảnh (`image.py`).
  - `backend/tests/`: Chứa các kịch bản test tự động dùng `pytest` để đảm bảo backend hoạt động chính xác trước khi deploy.
  - `backend/uploads/`: Lưu trữ các file ảnh được người dùng gửi lên để hiển thị lại trên giao diện hoặc xem trong lịch sử.

---

### 2.2. Thư mục `frontend/`
- **Mục đích**: Giao diện người dùng nền web xây dựng trên React 18, Vite, TypeScript và Tailwind CSS. Cung cấp trải nghiệm tương tác mượt mà, hỗ trợ cả máy tính lẫn điện thoại.
- **Có sử dụng tại Runtime không?**: **CÓ (BẮT BUỘC)**. Ứng dụng chạy trên cổng `3000` (ở chế độ phát triển) hoặc được build thành static files (`dist/`) khi chạy production.
- **Chi tiết các thư mục con**:
  - `frontend/src/pages/`: Chứa 7 trang hiển thị chính (`HomePage`, `DiagnosePage`, `DiseaseLibraryPage`, `DiseaseDetailPage`, `CarePage`, `HistoryPage`, `AboutPage`).
  - `frontend/src/components/`: Chứa các UI components dùng chung: thanh điều hướng (`Navbar`, `BottomNav`), hiển thị ảnh an toàn (`SafeImage`), hiệu ứng nền WebGL (`CanvasShader`) và lá cây 3D tương tác (`ThreeLeaf`).
  - `frontend/src/services/`: Chứa module `api.ts` thực hiện các cuộc gọi HTTP `fetch` tới backend thông qua reverse proxy của Vite.
  - `frontend/src/types/`: Khai báo toàn bộ kiểu dữ liệu TypeScript đồng bộ với các schema trả về từ Backend.

---

### 2.3. Thư mục `model/`
- **Mục đích**: Lưu trữ các file trọng số mô hình đã được huấn luyện hoàn chỉnh (`best.pt`), kèm file ánh xạ nhãn (`classes.json`) và thông số kiểm định (`metadata.json`).
- **Có sử dụng tại Runtime không?**: **CÓ (BẮT BUỘC)**. Backend nạp file `model/tomato_v3/best.pt` trực tiếp vào RAM lúc khởi động để thực hiện suy luận (Inference).
- **Phân loại các thư mục con**:
  - `model/tomato/`: Mô hình V1 Baseline (320x320) - phục vụ lưu trữ lịch sử và benchmark.
  - `model/tomato_v2/`: Mô hình V2 (384x384, khắc phục False Positive nhờ Hard Negatives) - dùng làm phương án dự phòng (Backup/Fallback).
  - `model/tomato_v3/`: Mô hình V3 Production (640x640, tối ưu độ phân giải cao cho đốm vi khuẩn nhỏ) - **đang được ứng dụng chính thức sử dụng**.

---

### 2.4. Thư mục `training/`
- **Mục đích**: Chứa toàn bộ môi trường nghiên cứu, dữ liệu mẫu, mã nguồn huấn luyện và báo cáo thử nghiệm của nhóm AI/Data Science.
- **Có sử dụng tại Runtime không?**: **KHÔNG**. Thư mục này chỉ phục vụ môi trường huấn luyện ngoại tuyến (Offline Development / Research / Training Pipeline).
- **Chi tiết các thư mục con**:
  - `training/datasets/`: Chứa dữ liệu ảnh thô (`raw/`) và dữ liệu đã qua tiền xử lý, chia tập train/val/test theo chuẩn định dạng YOLO (`processed/`).
  - `training/scripts/`: Các mã nguồn Python tự động hóa việc chia tập dữ liệu, chuẩn bị nhãn, huấn luyện mô hình và kiểm định API.
  - `training/runs/`: Nơi lưu lại các artifacts sinh ra trong quá trình huấn luyện: đồ thị độ chính xác (PR curve, F1 curve), ma trận nhầm lẫn (Confusion Matrix), ảnh dự đoán kiểm thử và trọng số sau từng epoch.
  - `training/docs/`: Các báo cáo kỹ thuật phân tích hiệu năng mô hình qua từng phiên bản.

---

### 2.5. Thư mục `docs/`
- **Mục đích**: Chứa toàn bộ tài liệu kỹ thuật, sơ đồ kiến trúc, bản đồ phụ thuộc, hướng dẫn bảo trì và cẩm nang vận hành của hệ thống.
- **Có sử dụng tại Runtime không?**: **KHÔNG**. Phục vụ các nhà phát triển, kỹ sư vận hành và người mới tiếp cận dự án.

---

### 2.6. Thư mục `_stitch_source/`
- **Mục đích**: Chứa các file nguyên mẫu thiết kế UI/UX ban đầu được tạo ra từ Google Stitch (HTML/CSS mocks và ảnh chụp màn hình).
- **Có sử dụng tại Runtime không?**: **KHÔNG**. Phục vụ tra cứu phong cách thiết kế, tone màu, shader và cấu trúc UI chuẩn.
