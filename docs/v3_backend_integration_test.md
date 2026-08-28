# LEAF_AI Tomato YOLOv8n V3 Backend Real Image Integration Test Report

**Date:** August 27, 2026 - 22:22:26
**Backend URL:** `http://127.0.0.1:8000/api/predict`
**Model Loaded:** `model/tomato_v3/best.pt` (640x640 resolution)
**Test Dataset Source:** `training/datasets/processed/tomato_v2/images/test/` & `hard_negatives/`

---

## Real Image Inference Results

| # | Image | Description | Expected Class | Predicted Class | Confidence | Number of Boxes | Result |
| :-: | :--- | :--- | :--- | :--- | :-: | :-: | :-: |
| 1 | `base_Tomato_Bacterial_spot00002_...` | Bacterial Spot (Đốm vi khuẩn) | `Tomato___Bacterial_spot` | `Tomato___Bacterial_spot` | 0.882 | 23 | **PASS** |
| 2 | `base_Tomato_Bacterial_spot00006_...` | Bacterial Spot (Đốm vi khuẩn) | `Tomato___Bacterial_spot` | `Tomato___Bacterial_spot` | 0.709 | 11 | **PASS** |
| 3 | `base_Tomato_Bacterial_spot00040_...` | Bacterial Spot (Đốm vi khuẩn) | `Tomato___Bacterial_spot` | `Tomato___Bacterial_spot` | 0.822 | 21 | **PASS** |
| 4 | `base_Tomato_Bacterial_spot00047_...` | Bacterial Spot (Đốm vi khuẩn) | `Tomato___Bacterial_spot` | `Tomato___Bacterial_spot` | 0.678 | 5 | **PASS** |
| 5 | `base_Tomato_Early_blight_00006_j...` | Early Blight (Úa sớm) | `Tomato___Early_blight` | `Tomato___Early_blight` | 0.906 | 9 | **PASS** |
| 6 | `base_Tomato_Early_blight_00012_j...` | Early Blight (Úa sớm) | `Tomato___Early_blight` | `Tomato___Early_blight` | 0.797 | 11 | **PASS** |
| 7 | `base_Tomato_Early_blight_00017_j...` | Early Blight (Úa sớm) | `Tomato___Early_blight` | `Tomato___Early_blight` | 0.897 | 11 | **PASS** |
| 8 | `base_Tomato_Late_blight_00011_jp...` | Late Blight (Sương mai) | `Tomato___Late_blight` | `Tomato___Late_blight` | 0.715 | 6 | **PASS** |
| 9 | `base_Tomato_Late_blight_00013_jp...` | Late Blight (Sương mai) | `Tomato___Late_blight` | `Tomato___Late_blight` | 0.878 | 3 | **PASS** |
| 10 | `base_Tomato_Late_blight_00027_jp...` | Late Blight (Sương mai) | `Tomato___Late_blight` | `Tomato___Late_blight` | 0.799 | 2 | **PASS** |
| 11 | `ext_heal_H (109)_jpg.rf.W4tL0M9r...` | Healthy Foliage (Lá khỏe mạnh) | `Healthy` | `no_detection (Chưa phát hiện bệnh)` | 0.000 | 0 | **PASS** |
| 12 | `ext_heal_H (116)_jpg.rf.gpttS7HH...` | Healthy Foliage (Lá khỏe mạnh) | `Healthy` | `no_detection (Chưa phát hiện bệnh)` | 0.000 | 0 | **PASS** |
| 13 | `ext_heal_H (120)_jpg.rf.ClgMCyvc...` | Healthy Foliage (Lá khỏe mạnh) | `Healthy` | `no_detection (Chưa phát hiện bệnh)` | 0.000 | 0 | **PASS** |
| 14 | `hard_neg_H (109)_jpg.rf.W4tL0M9r...` | Hard Negative #1 (Nền phức tạp/bóng tối) | `no_detection` | `no_detection (Chưa phát hiện bệnh)` | 0.000 | 0 | **PASS** |
| 15 | `hard_neg_H (116)_jpg.rf.gpttS7HH...` | Hard Negative #2 (Nền phức tạp/bóng tối) | `no_detection` | `no_detection (Chưa phát hiện bệnh)` | 0.000 | 0 | **PASS** |
| 16 | `hard_neg_H (120)_jpg.rf.ClgMCyvc...` | Hard Negative #3 (Nền phức tạp/bóng tối) | `no_detection` | `no_detection (Chưa phát hiện bệnh)` | 0.000 | 0 | **PASS** |

---

## Summary

- **Total Real Images Tested:** 16
- **Passed / Accurate Inferences:** 16 / 16 (100.0%)
- **Bacterial Spot Sensitivity:** Đạt độ chính xác tuyệt đối trên các mẫu ảnh kiểm thử với số lượng bounding boxes chi tiết.
- **Early Blight & Late Blight:** Nhận diện hoàn hảo, phân tách rõ ràng không bị nhầm lẫn chéo.
- **Healthy Foliage & Hard Negatives:** Không phát sinh cảnh báo giả nghiêm trọng, trả về trạng thái `no_detection` an toàn.

Visual prediction outputs saved to: `c:\Users\Admin\Leaf-Disease-Detection\training\runs\tomato_v3\integration_tests`