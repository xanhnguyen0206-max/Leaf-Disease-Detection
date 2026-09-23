# LEAF_AI Tomato Leaf Disease Detection Dataset V4 Report

> [!IMPORTANT]
> **DATASET PREPARATION ONLY — STRICTLY NO TRAINING PERFORMED**  
> This artifact represents the validated, 6-class production dataset for LEAF_AI Tomato Leaf Disease Detection.  
> Production models (`model/tomato_v3/best.pt`, `tomato_v2`, `tomato`), backend (`backend/`), frontend (`frontend/`), and database (`backend/leafai.db`) remain **100% UNTOUCHED**.

---

## 1. Dataset V4 là gì
Dataset V4 là tập dữ liệu mở rộng chuẩn hóa cho hệ thống LEAF_AI, nâng cấp phạm vi nhận diện từ 3 bệnh ban đầu lên **6 bệnh hại lá cà chua** phổ biến và nguy hiểm nhất trong thực tế canh tác nông nghiệp.

## 2. Nguồn dữ liệu (Data Sources)
1. **Dữ liệu 3 bệnh gốc (Classes 0, 1, 2):** Kế thừa 100% từ tập dữ liệu chuẩn hóa `training/datasets/processed/tomato_v3/` (1.614 ảnh, 7.607 annotations) nhằm duy trì độ nhạy cao trên các vết bệnh nhỏ và đặc hiệu với nền lá lành.
2. **Dữ liệu 3 bệnh mới (Classes 3, 4, 5):** Thu thập và trích xuất từ 6 gói Roboflow trong `training/datasets/raw/tomato_new/`:
   - *Septoria Leaf Spot:* Gói `tomato-septoria-leaf-spot-yhr7a-yp7vv` (200 ảnh) và `tomato-septoria-spot-adg4t-cjoyk` (139 ảnh).
   - *Tomato Leaf Mold:* Gói `tomato-leaf-mold-hgiyt-omeyi` (200 ảnh) và `tomato-leaf-mold-6ydxg-nhws1` (84 ảnh).
   - *Powdery Mildew:* Gói `powdery_mildew-ctqv7-kvqwj` (334 ảnh cà chua).

## 3. Cấu trúc thư mục Dataset V4
```
training/datasets/processed/tomato_v4/
├── images/
│   ├── train/     (2056 ảnh)
│   ├── val/       (255 ảnh)
│   └── test/      (260 ảnh)
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
├── samples/       (Ảnh trực quan hóa vẽ sẵn Bounding Box cho 6 classes + healthy)
├── data.yaml      (Cấu hình 6 classes chuẩn YOLO)
├── dataset_manifest.json
├── validation_report.json
└── README.md
```

## 4. Danh mục 6 Classes chính thức
| Class ID | Tên khoa học & Chuẩn quốc tế | Tên tiếng Việt |
| :---: | :--- | :--- |
| **0** | `Tomato___Bacterial_spot` | Bệnh đốm vi khuẩn cà chua (*Xanthomonas*) |
| **1** | `Tomato___Early_blight` | Bệnh úa sớm cà chua (*Alternaria solani*) |
| **2** | `Tomato___Late_blight` | Bệnh sương mai cà chua (*Phytophthora infestans*) |
| **3** | `Tomato___Septoria_leaf_spot` | Bệnh đốm lá Septoria (*Septoria lycopersici*) |
| **4** | `Tomato___Leaf_mold` | Bệnh mốc lá cà chua (*Passalora fulva*) |
| **5** | `Tomato___Powdery_mildew` | Bệnh phấn trắng cà chua (*Leveillula taurica / Oidium*) |

## 5. Quy trình Ánh xạ Class ID (Class Remapping)
- **Septoria:**
  - Gói A (`images/`): Class 0 $\rightarrow$ Class **3**
  - Gói B (`labels/`): Class 1 (`septoria`) $\rightarrow$ Class **3**, Class 0 (`healthy`) $\rightarrow$ Negative Sample (nhãn rỗng).
- **Leaf Mold:**
  - Gói A (`images/`): Class 0 $\rightarrow$ Class **4**
  - Gói B (`labels/`): Class 1 (`leaf-mold`) $\rightarrow$ Class **4**. Loại bỏ các nhãn polygon/sai format.
- **Powdery Mildew:**
  - Gói A (`images/`): Class 1 (`powdery-mildew`) $\rightarrow$ Class **5**.

## 6. Xử lý Dữ liệu cũ (Merge Isolation)
- Toàn bộ ảnh và nhãn từ `tomato_v3` được sao chép an toàn (COPY-ONLY) vào các split tương ứng `train`, `val`, `test` của V4.
- Giữ nguyên vẹn 100% tập dữ liệu gốc `tomato_v3` và `tomato_v2` để phục vụ benchmark đối chứng và fallback.

## 7. Xử lý Dữ liệu mới (New Disease Ingestion)
- Chuẩn hóa tên file canonical (gắn prefix tên bệnh, mã gói, hash 8 ký tự SHA-256 và tên gốc) nhằm triệt tiêu hoàn toàn nguy cơ ghi đè file do trùng tên giữa các gói Roboflow.
- Phân chia split mới độc lập bằng `random.seed(42)` theo tỷ lệ chuẩn 80% train, 10% val, 10% test.

## 8. Xử lý Vấn đề Sầu riêng (Durian Exclusion)
- 🚨 **Phát hiện:** Gói `powdery_mildew/labels/` là project `powdery-mildew-durian-gcovu` chứa ảnh phấn trắng trên cây **SẦU RIÊNG**.
- 🛡️ **Hành động xử lý:** **LOẠI BỎ TOÀN BỘ 100%**.
- **Số lượng đã loại:** **146 ảnh**, **345 bounding boxes**. Tuyệt đối không để lọt một mẫu lá sầu riêng nào vào tập dữ liệu cà chua.

## 9. Xử lý Vấn đề Đốm mắt ếch (Frog-Eye Leaf Spot Filtering)
- ⚠️ **Phát hiện:** Gói `powdery_mildew/images/` chứa class 0 là `frog-eye-leaf-spot` bên cạnh class 1 là `powdery-mildew`.
- 🛡️ **Hành động xử lý:** Lọc bỏ toàn bộ annotation của `frog-eye-leaf-spot`. Chỉ giữ lại đúng các vùng bệnh thực sự là phấn trắng (`powdery-mildew`).
- **Số lượng đã loại:** **1 annotation** đốm mắt ếch. Không có ảnh nào bị loại hoàn toàn vì tất cả các ảnh đều chứa tổn thương phấn trắng.

## 10. Xử lý Mẫu lá lành (Healthy Negative Samples)
- Giữ lại **1 mẫu lá lành** từ gói Septoria.
- Tuân thủ nguyên tắc chuẩn của YOLO Object Detection: ảnh tồn tại trong tập dữ liệu nhưng file `.txt` tương ứng để **rỗng** (0 dòng).
- Giúp mô hình rèn luyện khả năng ức chế báo động giả (False Positive) trên nền lá xanh không bệnh.

## 11. Chuẩn hóa Bounding Box (BBox Clamping)
- Đã xử lý và clamp **52 bounding boxes** bị tràn biên nhẹ về khoảng hợp lệ `[0.0, 1.0]`.
- Loại bỏ **149 annotation** không hợp lệ (nhãn polygon phân vùng sai format hoặc có kích thước $\le 0$).

## 12. Kiểm tra Trùng lặp (Deduplication)
- Kiểm tra toàn bộ mã băm SHA-256: **0 ảnh trùng lặp** giữa V3 và V4, và **0 hiện tượng rò rỉ (leakage)** giữa các split `train`, `val`, `test`.

## 13. Phân chia Splits (Train / Val / Test)
- **Train:** 2056 ảnh (80.0%) | 7367 boxes
- **Val:** 255 ảnh (9.9%) | 796 boxes
- **Test:** 260 ảnh (10.1%) | 921 boxes
- **Tổng cộng:** **2571 ảnh** | **9084 bounding boxes**

## 14. Thống kê Chi tiết theo Class (Class Distribution)
| Class ID | Tên bệnh | Số ảnh xuất hiện | Số Bounding Boxes | Tỷ lệ Box |
| :---: | :--- | :---: | :---: | :---: |
| `0` | Tomato___Bacterial_spot | 481 | 3723 | 41.0% |
| `1` | Tomato___Early_blight | 300 | 1621 | 17.8% |
| `2` | Tomato___Late_blight | 510 | 2263 | 24.9% |
| `3` | Tomato___Septoria_leaf_spot | 338 | 924 | 10.2% |
| `4` | Tomato___Leaf_mold | 200 | 215 | 2.4% |
| `5` | Tomato___Powdery_mildew | 334 | 338 | 3.7% |
| - | *Healthy Negative Foliage* | 1 | *(empty txt)* | - |

## 15. Kiểm tra Trực quan (Visual Verification)
- Đã xuất các file ảnh kiểm chứng vẽ sẵn bounding box vào thư mục:
  `training/datasets/processed/tomato_v4/samples/`
- Bao gồm các mẫu trực quan cho từng lớp bệnh và mẫu nền lá lành, chứng minh nhãn được vẽ chuẩn xác trên từng ổ bệnh.

## 16. Kết quả Kiểm định (Validation Results)
- Đã chạy tự động **15/15 bài kiểm tra nghiêm ngặt**:
  - 100% ảnh mở được qua thư viện PIL.
  - 100% ảnh có file nhãn đi kèm.
  - 100% tọa độ bounding box nằm trong phạm vi `[0, 1]` và có kích thước dương.
  - 100% Class IDs thuộc dải hợp lệ `(0, 1, 2, 3, 4, 5)`.
  - 0 dữ liệu sầu riêng lọt vào.
  - 0 annotation đốm mắt ếch bị gộp nhầm.
  - 0 ảnh trùng lặp giữa các split.

## 17. Những vấn đề cần lưu ý khi huấn luyện
1. **Chênh lệch kích thước tổn thương:** Septoria có nhiều đốm nhỏ 1-3mm (tương tự Bacterial Spot), trong khi Leaf Mold và Powdery Mildew thường tạo mảng bệnh lớn. Nên duy trì độ phân giải đầu vào **640x640** như bản V3 để bảo toàn độ nhạy.
2. **Class Imbalance:** Bacterial Spot có lượng box lớn hơn (do nhiều đốm li ti trên một lá), nên áp dụng Loss Weight hoặc Data Augmentation phù hợp khi train.

## 18. Khuyến nghị cho bước Huấn luyện tiếp theo
- **TRẠNG THÁI HIỆN TẠI:** Dataset V4 đã được chuẩn bị, làm sạch, chuẩn hóa và kiểm định hoàn tất.
- **BƯỚC TIẾP THEO (Chờ lệnh OK của người dùng):**
  1. Thiết lập kịch bản huấn luyện `train_tomato_v4.py` (khởi tạo từ checkpoint `yolov8n.pt` hoặc transfer learning từ `model/tomato_v3/best.pt`).
  2. Định cấu hình huấn luyện ở 640x640 resolution, áp dụng leaf-safe augmentation.
  3. Đánh giá benchmark V4 so sánh trực tiếp với V3 trên tập test split.
