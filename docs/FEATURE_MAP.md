# Bản đồ Tính năng Hệ thống LEAF_AI (FEATURE MAP)

Tài liệu này phân tích toàn bộ **18 tính năng cốt lõi** của hệ thống LEAF_AI. Mỗi tính năng được phân tích xuyên suốt qua tất cả các tầng: **Frontend Component → API Call → Backend Route → Business Logic Service → AI Model / Database → Phản hồi UI**.

---

## 1. Bảng Tổng hợp Tính năng (Feature Matrix Summary)

| STT | Tính năng | Frontend Component | API Function | Backend Endpoint | Service / Model / DB | Kết quả Đầu ra trên UI |
|---|---|---|---|---|---|---|
| 1 | **Trang chủ (HomePage)** | [HomePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/HomePage.tsx) | *N/A (Static + Nav)* | *N/A* | *N/A* | Hero banner, thống kê mô hình V3, các nút điều hướng nhanh |
| 2 | **Upload ảnh từ thiết bị** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `prediction_service` + `YOLOModelService` | Preview ảnh tức thì, chuẩn bị luồng byte gửi API |
| 3 | **Chụp ảnh từ Camera** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(blob)` | `POST /api/predict` | `prediction_service` + `YOLOModelService` | Stream video thời gian thực từ webcam, chụp snapshot thành file ảnh |
| 4 | **Chẩn đoán bệnh lá bằng AI** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `model/tomato_v3/best.pt` | Báo cáo chi tiết: Tên bệnh, loài cây, độ tin cậy %, mức độ nguy hiểm |
| 5 | **Vẽ Bounding Box trực quan** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `YOLOModelService.predict` | Các khung viền màu sắc bao quanh từng tổn thương trên lá |
| 6 | **Nhận diện & Gom nhóm Đa bệnh** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `prediction_service.group_diseases` | Tổng hợp số đốm bệnh theo từng loài bệnh xuất hiện đồng thời |
| 7 | **Xác định Bệnh chính (Primary)** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `prediction_service` | Thẻ làm nổi bật bệnh chiếm tỷ trọng tổn thương cao nhất |
| 8 | **Danh sách Bệnh đồng nhiễm** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `prediction_service` | Danh sách các bệnh phụ kèm độ tin cậy và số lượng vết bệnh |
| 9 | **Thư viện Bệnh hại cây trồng** | [DiseaseLibraryPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiseaseLibraryPage.tsx) | `fetchDiseases(search, plant)` | `GET /api/diseases` | `Disease` Table (SQLite) | Lưới hiển thị danh mục bệnh, hỗ trợ tìm kiếm và lọc theo loài cây |
| 10 | **Chi tiết Bệnh & Triệu chứng** | [DiseaseDetailPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiseaseDetailPage.tsx) | `fetchDiseaseDetail(id)` | `GET /api/diseases/{id}` | `Disease` Table (SQLite) | Bách khoa toàn thư: Tên khoa học, tác nhân, triệu chứng 3 giai đoạn |
| 11 | **Phác đồ Quản lý Dịch hại (IPM)** | [CarePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/CarePage.tsx) | `fetchCareRecommendations(id)` | `GET /api/care/{id}` | `CareRecommendation` Table | Các giải pháp phòng trừ sinh học, hóa học, canh tác theo chuẩn IPM |
| 12 | **Lịch sử Chẩn đoán** | [HistoryPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/HistoryPage.tsx) | `fetchHistory()` | `GET /api/history` | `DiagnosisHistory` Table | Danh sách các mẫu lá đã khám trong quá khứ kèm mốc thời gian |
| 13 | **Xóa Bản ghi Lịch sử** | [HistoryPage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/HistoryPage.tsx) | `deleteHistoryItem(id)` | `DELETE /api/history/{id}`| `DiagnosisHistory` Table | Xóa bản ghi khỏi cơ sở dữ liệu và làm mới danh sách tức thì |
| 14 | **Khuyến nghị Xử lý Tức thì** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `CareRecommendation` Table | Danh sách hành động ưu tiên cao (Khẩn cấp, Khuyên dùng, Phòng ngừa) |
| 15 | **Xử lý Lá Khỏe / Không Bệnh** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `YOLOModelService` (`no_detection`) | Thông báo cây phát triển khỏe mạnh, gợi ý chế độ duy trì dinh dưỡng |
| 16 | **Xử lý Lỗi & Phòng vệ Ảnh** | [DiagnosePage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/pages/DiagnosePage.tsx) | `diagnoseLeaf(file)` | `POST /api/predict` | `PIL.Image.open().verify()` | Thông báo lỗi thân thiện khi tải file sai định dạng, file hỏng, quá dung lượng |
| 17 | **Chống Vỡ Ảnh (Safe Image)** | [SafeImage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/SafeImage.tsx) | *N/A (Client Error Event)* | *N/A* | Fallback Placeholder SVG | Tự động chuyển sang ảnh thay thế khi ảnh gốc trên server bị mất |
| 18 | **Đồ họa Không gian 3D & Shader** | [ThreeLeaf.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/ThreeLeaf.tsx) & [CanvasShader.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/CanvasShader.tsx) | *N/A (WebGL)* | *N/A* | Client GPU | Mô hình lá cây 3D xoay tương tác và hiệu ứng nền sinh học sống động |

---

## 2. Phân tích Chuyên sâu Từng Tính năng

### Feature 1: Trang chủ & Điều hướng (HomePage)
- **Mô tả**: Trang đích đầu tiên khi người dùng truy cập, giới thiệu công nghệ AI V3 (640x640), tỷ lệ Recall 80.8% trên Đốm vi khuẩn, và các lối tắt nhanh tới Chẩn đoán và Thư viện.
- **Tương tác**: Người dùng có thể bấm "Chẩn đoán ngay" (chuyển sang tab `diagnose`) hoặc "Khám phá Thư viện bệnh" (chuyển sang tab `library`).

### Feature 2 & 3: Tải ảnh & Chụp ảnh Camera (Upload & Webcam Capture)
- **Mô tả**: Cho phép người dùng linh hoạt cung cấp hình ảnh lá cây cần kiểm tra.
- **Luồng xử lý**:
  - Khi tải file: Lắng nghe sự kiện `onChange` từ `<input type="file" accept="image/*">`.
  - Khi bật camera: Gọi `navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })` để mở camera sau của điện thoại hoặc webcam máy tính. Khi bấm chụp, chụp khung hình từ `<video>` sang `<canvas>` ẩn và xuất ra `Blob` định dạng JPEG.

### Feature 4, 5, 6, 7, 8: Bộ tính năng Chẩn đoán AI Toàn diện (Comprehensive AI Diagnosis)
- **Mô tả**: Cốt lõi của hệ thống LEAF_AI, giải quyết bài toán phát hiện tổn thương đa vùng trên mặt lá.
- **Thuật toán xử lý tại Backend**:
  1. Mô hình YOLOv8n V3 quét qua ảnh và trả về danh sách $N$ bounding box dạng:
     $$\text{Detection} = \{ \text{class\_id}, \text{disease}, \text{confidence}, [x_1, y_1, x_2, y_2] \}$$
  2. Bỏ qua mọi box có $\text{confidence} < \text{MODEL\_CONFIDENCE\_THRESHOLD}$ (mặc định $0.25$).
  3. Gom các box cùng loại bệnh để tính toán:
     - `max_confidence`: Độ tin cậy cao nhất tìm thấy của bệnh đó.
     - `detection_count`: Số lượng đốm bệnh xuất hiện trên lá.
     - `confidence_level`: Chuỗi tiếng Việt mô tả độ tin cậy.
  4. Đánh giá cờ `is_multi_disease`: Thiết lập `True` nếu phát hiện từ 2 loại bệnh khác nhau trở lên trên cùng một chiếc lá.
  5. Bệnh có điểm cao nhất được chọn làm `primary_disease`.

### Feature 9 & 10: Thư viện Bệnh & Chi tiết Bách khoa Toàn thư (Disease Knowledge Base)
- **Mô tả**: Cung cấp kiến thức nông nghiệp chính xác, có cơ sở khoa học về các bệnh hại phổ biến trên cây trồng (hiện tại bao gồm: *Đốm vi khuẩn*, *Sương mai / Mốc sương*, *Đốm vòng / Cháy sớm*).
- **Cấu trúc Dữ liệu Chi tiết**:
  - Tên khoa học, tên tiếng Anh, tác nhân gây bệnh (nấm *Alternaria solani*, *Phytophthora infestans*, vi khuẩn *Xanthomonas campestris*).
  - Triệu chứng phân tầng rõ ràng: Giai đoạn mới chớm, Giai đoạn phát triển mạnh, Giai đoạn nghiêm trọng.
  - Phân biệt với các bệnh tương tự nhằm tránh nhầm lẫn trong thực tế.

### Feature 11 & 14: Quản lý Dịch hại Tổng hợp (IPM) & Khuyến nghị
- **Mô tả**: Hệ thống không chỉ dừng lại ở việc phát hiện bệnh mà còn cung cấp cẩm nang hành động cụ thể cho nhà nông theo triết lý IPM (Integrated Pest Management).
- **Nội dung bao gồm**:
  - Biện pháp canh tác & vệ sinh đồng ruộng: tỉa cành thông thoáng, xử lý tàn dư.
  - Quản lý nước tưới và dinh dưỡng: tránh tưới phun mưa lúc chiều tối, cân đối tỷ lệ Đạm - Lân - Kali.
  - Phòng trừ sinh học: sử dụng chế phẩm *Bacillus subtilis*, *Trichoderma*, đồng sinh học.
  - Nguyên tắc dùng thuốc bảo vệ thực vật: danh mục hoạt chất khuyên dùng, thời gian cách ly (PHI), phòng tránh hiện tượng kháng thuốc.

### Feature 12 & 13: Quản lý Lịch sử Chẩn đoán (History CRUD)
- **Mô tả**: Tự động lưu lại mọi lần khám lá vào cơ sở dữ liệu SQLite kèm liên kết ảnh tĩnh đã tải lên.
- **Thao tác**: Người dùng có thể xem lại ảnh gốc, mức độ tin cậy và xóa bỏ những bản ghi không còn cần thiết thông qua nút bấm xóa (gọi `DELETE /api/history/{id}`).

### Feature 15: Xử lý Lá Khỏe Mạnh (Healthy Leaf & Hard Negatives)
- **Mô tả**: Trong trường hợp ảnh lá không có bất kỳ tổn thương nào hoặc chỉ có vết bẩn bình thường, mô hình AI sẽ trả về `status: "no_detection"`.
- **Giao diện**: Hiển thị thẻ màu xanh lá dịu mắt, chúc mừng người trồng và đưa ra lời khuyên duy trì chế độ chăm sóc hiện tại.

### Feature 16 & 17: Phòng vệ Dữ liệu & Chống Vỡ Ảnh (Defensive Design)
- **Phòng vệ Backend**: Kiểm tra tính hợp lệ của file bằng `PIL.verify()`, từ chối file rỗng, file văn bản đổi tên thành `.jpg` hoặc file vượt quá 10MB.
- **Chống vỡ ảnh Frontend**: Component [SafeImage.tsx](file:///c:/Users/Admin/Leaf-Disease-Detection/frontend/src/components/SafeImage.tsx) bắt sự kiện `onError` của thẻ `<img>`, tự động render một khung SVG hình chiếc lá trang nhã thay vì icon ảnh vỡ mặc định của trình duyệt.
