# Danh mục Công nghệ & Thư viện (TECH STACK)

Tài liệu này liệt kê đầy đủ **100% công nghệ, framework, thư viện và công cụ thực tế** đang được sử dụng trong dự án LEAF_AI, bao gồm số hiệu phiên bản, phạm vi sử dụng, mục đích kỹ thuật và lý do lựa chọn.

---

## 1. Bảng Tổng hợp Công nghệ Toàn diện (Tech Stack Catalog)

| Công nghệ / Thư viện | Phiên bản | Phân vùng sử dụng | Tác dụng trong hệ thống | Vì sao cần / Lý do lựa chọn |
|---|---|---|---|---|
| **Python** | 3.10+ / 3.13 | Backend, AI Training | Ngôn ngữ lập trình chính cho Backend và AI | Hệ sinh thái Machine Learning phong phú nhất (PyTorch, Ultralytics, PIL) |
| **FastAPI** | `>=0.104.0` | Backend API | Web Framework xây dựng REST API bất đồng bộ | Tốc độ thực thi cực nhanh (ASGI), tự động sinh tài liệu Swagger/OpenAPI, tích hợp sẵn Pydantic validation |
| **Uvicorn** | `>=0.24.0` | Backend Server | ASGI Server hiệu năng cao cho Python | Xử lý đa kết nối đồng thời mượt mà, hỗ trợ HTTP/1.1 và WebSockets |
| **SQLAlchemy** | `>=2.0.23` | Backend Database | Thư viện ORM (Object-Relational Mapping) | Trừu tượng hóa truy vấn SQL, quản lý quan hệ bảng (Relationship), bảo vệ chống SQL Injection |
| **SQLite** | 3.x (Built-in) | Backend Database | Cơ sở dữ liệu quan hệ nhúng (`leafai.db`) | Không cần cài đặt server DB phức tạp, dễ dàng sao lưu, di động và cực kỳ nhẹ cho edge deployment |
| **Pydantic** | `>=2.5.0` | Backend Data Layer | Khung định nghĩa và validate Schema dữ liệu | Đảm bảo tính toàn vẹn của dữ liệu đầu vào/đầu ra, tự động chuyển đổi kiểu dữ liệu (Serialization/Deserialization) |
| **Pydantic Settings**| `>=2.0.0` | Backend Core | Quản lý biến môi trường (`BaseSettings`) | Đọc cấu hình từ biến môi trường của hệ thống một cách an toàn và có kiểu dữ liệu rõ ràng |
| **python-multipart** | `>=0.0.6` | Backend API | Thư viện giải mã dữ liệu multipart/form-data | Bắt buộc phải có để FastAPI có thể tiếp nhận file upload từ client (`UploadFile = File(...)`) |
| **Ultralytics (YOLOv8)**| `>=8.0.0` | AI Inference, Training | Framework Object Detection tiên tiến nhất | Cung cấp kiến trúc YOLOv8n (nano) siêu nhẹ, tốc độ suy luận dưới 300ms trên CPU, độ chính xác mAP cao |
| **PyTorch** | `>=2.0.0` | AI Inference, Training | Nền tảng Deep Learning nền tảng | Động cơ tính toán tensor, thực thi mô hình nơ-ron trên CPU và GPU (CUDA) |
| **Pillow (PIL)** | `>=10.0.0` | Backend Utils, Training | Thư viện xử lý hình ảnh Python | Mở, giải mã ma trận điểm ảnh, kiểm tra tính toàn vẹn `img.verify()`, vẽ nhãn bounding box |
| **Pytest** | `>=7.4.3` | Backend Testing | Khung kiểm thử tự động (Unit & Integration) | Dễ viết test fixture, báo cáo kết quả kiểm thử trực quan, hỗ trợ kiểm thử API và AI service |
| **HTTPX** | `>=0.25.1` | Backend Testing | Client HTTP bất đồng bộ cho Python | Dùng cùng `fastapi.testclient.TestClient` để gửi request kiểm thử API nội bộ |
| **React** | `^18.2.0` | Frontend UI | Thư viện xây dựng giao diện người dùng | Quản lý Component theo Declarative UI, xử lý Virtual DOM hiệu quả, hệ sinh thái phong phú |
| **TypeScript** | `^5.2.2` | Frontend UI | Ngôn ngữ JavaScript có định kiểu tĩnh | Phát hiện lỗi logic ngay lúc compile, đồng bộ chính xác Type với Pydantic Schemas của Backend |
| **Vite** | `^5.0.0` | Frontend Tooling | Build tool & Dev server thế hệ mới | Khởi động dev server tức thì nhờ native ESM, HMR cực nhanh, tích hợp Reverse Proxy sang Backend |
| **Tailwind CSS** | `^3.3.5` | Frontend Styling | Utility-first CSS Framework | Tùy biến giao diện theo Design System Digital Canopy nhanh chóng, không bị phình to kích thước CSS |
| **PostCSS & Autoprefixer**| `^8.4.31` / `^10.4.16` | Frontend Build | Xử lý và tiền xử lý CSS | Tự động thêm tiền tố vendor CSS (-webkit, -moz) tương thích đa trình duyệt |
| **Three.js** | `^0.158.0` | Frontend Visuals | Thư viện đồ họa 3D WebGL cho trình duyệt | Dựng mô hình lá cây 3D xoay tương tác sống động ngay trên trang chủ |
| **Lucide React** | `^0.294.0` | Frontend Icons | Bộ icon SVG hiện đại, sắc nét | Cung cấp các biểu tượng trực quan: camera, upload, lá cây, khiên bảo vệ, cảnh báo |
| **Google Stitch Design System** | Custom CSS | Frontend UI | Hệ thống thiết kế giao diện cao cấp | Tối ưu trải nghiệm với bảng màu xanh tự nhiên, hiệu ứng kính mờ (Glassmorphism), viền phát sáng |

---

## 2. Lý do Lựa chọn Kiến trúc Công nghệ (Architectural Rationale)

1. **Tại sao chọn FastAPI thay vì Django hay Flask?**
   - *Tốc độ*: FastAPI được xây dựng trên Starlette và Pydantic, cho tốc độ xử lý ngang ngửa Node.js và Go.
   - *Async Native*: Hỗ trợ xử lý bất đồng bộ, rất phù hợp khi tiếp nhận các file ảnh dung lượng lớn mà không làm nghẽn tiến trình (non-blocking IO).
   - *Auto Documentation*: Tự động tạo Swagger UI tại `/docs`, giúp đội ngũ frontend tra cứu endpoint dễ dàng.

2. **Tại sao chọn YOLOv8n (Nano) thay vì YOLOv8x hay ResNet thông thường?**
   - *Kích thước siêu nhỏ*: File weights chỉ nặng **6.2 MB**, cực kỳ gọn nhẹ để nạp vào bộ nhớ.
   - *Tốc độ suy luận CPU*: Chạy ổn định từ **100ms - 350ms** trên máy tính thông thường không có card đồ họa rời (GPU).
   - *Đa nhiệm*: Không chỉ phân loại ảnh (Classification) mà còn định vị chính xác vị trí tổn thương (Object Detection) thông qua bounding box.

3. **Tại sao chọn React + Vite + TypeScript thay vì Next.js hay Create React App?**
   - *Đơn giản & Nhẹ*: Không cần máy chủ Node.js trung gian để render (SSR), ứng dụng client-side SPA tương thích hoàn hảo khi đóng gói phân phối.
   - *Tốc độ Build*: Vite sử dụng esbuild viết bằng Go giúp nạp trang và cập nhật mã nguồn (HMR) gần như tức thì.
   - *Độ an toàn Type*: TypeScript ngăn chặn 99% lỗi truy cập thuộc tính `undefined` khi render dữ liệu từ API.
