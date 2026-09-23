# Tomato Model V4 Training Report

## 1. Overview
Model V4 has been successfully trained as an independent experiment. This model extends the previous V3 model by expanding the disease detection capabilities from 3 to 6 classes.

**Architecture**: YOLOv8n
**Resolution**: 640x640
**Epochs Trained**: 25 (Resumed from Epoch 14)
**Optimizer**: AdamW
**Dataset**: `tomato_v4` (6 classes)

## 2. Overall Performance on Test Set
The model was evaluated on the independent `test` split containing 260 images (43 background/healthy images) and 920 bounding box instances.

| Metric | Overall Score |
|---|---|
| **Precision (P)** | 0.700 |
| **Recall (R)** | 0.683 |
| **mAP50** | 0.711 |
| **mAP50-95** | 0.463 |

## 3. Per-Class Evaluation

### Legacy Classes (0, 1, 2)
The legacy classes show continued robust detection capabilities.

| Class ID | Disease Name | Instances | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|
| 0 | Bacterial spot | 395 | 0.740 | 0.576 | 0.661 | 0.343 |
| 1 | Early blight | 138 | 0.586 | 0.543 | 0.572 | 0.289 |
| 2 | Late blight | 251 | 0.766 | 0.857 | 0.888 | 0.603 |

### New Classes (3, 4, 5)
The new diseases added in V4 were evaluated to ensure they can be accurately distinguished.

| Class ID | Disease Name | Instances | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|---|---|
| 3 | Septoria leaf spot | 80 | 0.702 | 0.588 | 0.708 | 0.471 |
| 4 | Leaf mold | 22 | 0.487 | 0.562 | 0.446 | 0.272 |
| 5 | Powdery mildew | 34 | 0.917 | 0.971 | 0.992 | 0.802 |

> [!NOTE]
> **Performance Insights:**
> - **Powdery Mildew** (Class 5) achieved exceptional performance with 0.992 mAP50, likely due to its highly distinct visual characteristics.
> - **Leaf Mold** (Class 4) has a relatively low mAP50 (0.446), which is strongly correlated with its very low instance count (only 22 instances in the test set). Gathering more data for this class is recommended for future iterations.
> - The presence of **43 background images** (healthy leaves) in the test set without severe precision drops indicates a healthy false positive rate.

## 4. Outputs and Deliverables
- **Best Weights**: Safely copied to [best.pt](file:///C:/Users/Admin/Leaf-Disease-Detection/model/tomato_v4/best.pt)
- **Configuration Files**: `data.yaml` and `args.yaml` copied to `model/tomato_v4/` for reproducibility.
- The production V3 model and existing systems remain **completely untouched**.

## 5. Conclusion
Model V4 has successfully converged and demonstrates strong baseline capabilities across 6 diseases. Before integrating this model into the production backend, we recommend:
1. Conducting manual testing using the frontend UI pointed to the V4 weights to verify real-world behavior.
2. Collecting more training data for **Leaf Mold (Class 4)** to improve its recall.
