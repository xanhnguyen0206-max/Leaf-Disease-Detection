# Sơ đồ Phụ thuộc Module & Dịch vụ (DEPENDENCY MAP)

Tài liệu này cung cấp bản đồ phân cấp phụ thuộc (Dependency Graph) giữa các trang giao diện (Frontend Pages), dịch vụ gọi API (Frontend API Services), bộ điều khiển đầu cuối (Backend Endpoints), tầng xử lý nghiệp vụ (Business Services), tầng mô hình trí tuệ nhân tạo (AI Models) và tầng cơ sở dữ liệu quan hệ (Database Tables).

---

## 1. Sơ đồ Phụ thuộc Module Toàn Hệ thống (End-to-End Dependency Graph)

```mermaid
graph LR
    subgraph Frontend_Pages["FRONTEND PAGES"]
        P_Home["HomePage.tsx"]
        P_Diag["DiagnosePage.tsx"]
        P_Lib["DiseaseLibraryPage.tsx"]
        P_Detail["DiseaseDetailPage.tsx"]
        P_Care["CarePage.tsx"]
        P_Hist["HistoryPage.tsx"]
        P_About["AboutPage.tsx"]
    end

    subgraph Frontend_Services["FRONTEND API CLIENT"]
        API_Diag["api.ts: diagnoseLeaf()"]
        API_Lib["api.ts: fetchDiseases()"]
        API_Detail["api.ts: fetchDiseaseDetail()"]
        API_Care["api.ts: fetchCareRecommendations()"]
        API_Hist["api.ts: fetchHistory()"]
        API_DelHist["api.ts: deleteHistoryItem()"]
        API_Health["api.ts: checkHealth()"]
    end

    subgraph Backend_Endpoints["FASTAPI ENDPOINTS"]
        EP_Predict["POST /api/predict\n(predict.py)"]
        EP_Diseases["GET /api/diseases\n(diseases.py)"]
        EP_DiseaseDetail["GET /api/diseases/{id}\n(diseases.py)"]
        EP_Care["GET /api/care/{id}\n(care.py)"]
        EP_History["GET /api/history\n(history.py)"]
        EP_DelHistory["DELETE /api/history/{id}\n(history.py)"]
        EP_Health["GET /api/health\n(health.py)"]
    end

    subgraph Backend_Services["BUSINESS LOGIC & AI SERVICES"]
        S_Pred["PredictionService\n(prediction_service.py)"]
        S_YOLO["YOLOModelService\n(yolo_model_service.py)"]
        S_Base["BaseModelService\n(base_model_service.py)"]
        S_Img["Image Utils\n(utils/image.py)"]
    end

    subgraph AI_Weights["AI MODEL WEIGHTS"]
        W_V3["model/tomato_v3/best.pt\n(Active Production 640x640)"]
        W_V2["model/tomato_v2/best.pt\n(Backup Model 384x384)"]
    end

    subgraph Database_Tables["SQLITE DATABASE (leafai.db)"]
        DB_Disease["Table: diseases\n(models.Disease)"]
        DB_Care["Table: care_recommendations\n(models.CareRecommendation)"]
        DB_History["Table: diagnosis_history\n(models.DiagnosisHistory)"]
    end

    %% Frontend to API mapping
    P_Diag --> API_Diag
    P_Lib --> API_Lib
    P_Detail --> API_Detail
    P_Detail --> API_Care
    P_Care --> API_Care
    P_Hist --> API_Hist
    P_Hist --> API_DelHist
    P_Home -.-> API_Health

    %% API Client to Backend Endpoints
    API_Diag --> EP_Predict
    API_Lib --> EP_Diseases
    API_Detail --> EP_DiseaseDetail
    API_Care --> EP_Care
    API_Hist --> EP_History
    API_DelHist --> EP_DelHistory
    API_Health --> EP_Health

    %% Endpoints to Services / DB
    EP_Predict --> S_Pred
    EP_Predict --> S_Img
    EP_Diseases --> DB_Disease
    EP_DiseaseDetail --> DB_Disease
    EP_Care --> DB_Care
    EP_History --> DB_History
    EP_DelHistory --> DB_History

    %% Prediction Service internal graph
    S_Pred --> S_YOLO
    S_Pred --> DB_Disease
    S_Pred --> DB_Care
    S_Pred --> DB_History

    %% YOLO Service to Base and Weights
    S_YOLO --implements--> S_Base
    S_YOLO --> W_V3
    S_YOLO -.can switch to.-> W_V2
```

---

## 2. Bảng Quan hệ Phụ thuộc Chi tiết Từng Module

### 2.1. Tầng Giao diện (Frontend Layer)

| Màn hình | Dịch vụ API được gọi | Endpoint Backend tương ứng | Thành phần Backend xử lý |
|---|---|---|---|
| **DiagnosePage** | `diagnoseLeaf(file, confThreshold)` | `POST /api/predict` | `predict.py` → `prediction_service` → `YOLOModelService` → `leafai.db` |
| **DiseaseLibraryPage** | `fetchDiseases(search, plant)` | `GET /api/diseases` | `diseases.py` → `db.query(Disease)` |
| **DiseaseDetailPage** | `fetchDiseaseDetail(id)`<br>`fetchCareRecommendations(id)` | `GET /api/diseases/{id}`<br>`GET /api/care/{id}` | `diseases.py` → `db.query(Disease)`<br>`care.py` → `db.query(CareRecommendation)` |
| **CarePage** | `fetchCareRecommendations(id)` | `GET /api/care/{id}` | `care.py` → `db.query(CareRecommendation)` |
| **HistoryPage** | `fetchHistory()`<br>`deleteHistoryItem(id)` | `GET /api/history`<br>`DELETE /api/history/{id}` | `history.py` → `db.query(DiagnosisHistory)`<br>`history.py` → `db.delete(item)` |

---

### 2.2. Tầng Xử lý Nghiệp vụ & Mô hình AI (Backend Core & AI Layer)

| Module / Lớp | Kế thừa / Cài đặt Interface | Phụ thuộc vào Modules | Được sử dụng bởi |
|---|---|---|---|
| `BaseModelService` | `abc.ABC` | `abc` | `YOLOModelService`, `MockModelService` |
| `YOLOModelService` | `BaseModelService` | `ultralytics.YOLO`, `torch`, `PIL`, `config.settings` | `prediction_service.py`, `test_yolo_service.py` |
| `PredictionService` | *Singleton Class* | `YOLOModelService`, `models.Disease`, `models.DiagnosisHistory`, `schemas.diagnosis` | `api/endpoints/predict.py` |
| `seed_database` | *Migration Routine* | `sqlalchemy.text`, `models.Base`, `session.engine` | `app/main.py` (Startup Hook) |

---

### 2.3. Tầng Cơ sở Dữ liệu (Database Relationships)

```mermaid
erDiagram
    DISEASES ||--o{ CARE_RECOMMENDATIONS : "has 1..N"
    DISEASES {
        string id PK "e.g. tomato_bacterial_spot"
        string name "Đốm vi khuẩn trên lá cà chua"
        string plant "Cà chua"
        string scientific_name "Xanthomonas campestris pv. vesicatoria"
        string severity "high"
        text description "Mô tả tổng quan"
        json symptoms "Danh sách triệu chứng"
        json early_symptoms "Triệu chứng giai đoạn đầu"
        json mid_symptoms "Triệu chứng giai đoạn phát triển"
        json severe_symptoms "Triệu chứng giai đoạn nghiêm trọng"
        json similar_diseases_diff "Phân biệt với bệnh tương tự"
        json prevention_before_planting "Phòng trừ trước khi trồng"
        json prevention_during_growth "Phòng trừ trong quá trình lớn"
        json sources "Tài liệu khoa học tham khảo"
    }

    CARE_RECOMMENDATIONS {
        string id PK "UUID v4"
        string disease_id FK "Liên kết tới diseases.id"
        string category "chemical / biological / cultural"
        string title "Tiêu đề biện pháp"
        text description "Mô tả chi tiết cách thực hiện"
        string priority "high / medium / low"
    }

    DIAGNOSIS_HISTORY {
        string id PK "UUID v4"
        string image_url "/uploads/xxx.jpg"
        string plant "Cà chua"
        string disease "Tên bệnh phát hiện"
        string primary_disease "Tomato___Bacterial_spot"
        float confidence "0.85"
        string severity "high"
        string status "detected / no_detection"
        json detections "Danh sách bounding box chi tiết"
        json detected_diseases "Gom nhóm thống kê đa bệnh"
        boolean is_multi_disease "true / false"
        json recommendations "Khuyến nghị xử lý tức thì"
        datetime created_at "UTC Timestamp"
    }
```
