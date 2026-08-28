import os
import json
import time
import shutil
from pathlib import Path
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torch
from ultralytics import YOLO

BASE_DIR = Path("c:/Users/Admin/Leaf-Disease-Detection")
MODEL_PATH = BASE_DIR / "model" / "tomato" / "best.pt"
TEST_IMG_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato" / "images" / "test"
TEST_LBL_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato" / "labels" / "test"
OUTPUT_DIR = BASE_DIR / "training" / "runs" / "tomato" / "inference_test"

CLASS_NAMES = {
    0: "Tomato___Bacterial_spot",
    1: "Tomato___Early_blight",
    2: "Tomato___Late_blight"
}

SHORT_NAMES = {
    0: "Bacterial_spot",
    1: "Early_blight",
    2: "Late_blight"
}

CLASS_COLORS = {
    0: (230, 40, 40),    # Bacterial Spot: Red
    1: (245, 140, 0),    # Early Blight: Orange/Amber
    2: (150, 40, 220),   # Late Blight: Purple/Violet
}

def compute_iou(box1, box2):
    """
    box: [x1, y1, x2, y2]
    """
    xA = max(box1[0], box2[0])
    yA = max(box1[1], box2[1])
    xB = min(box1[2], box2[2])
    yB = min(box1[3], box2[3])
    
    inter_w = max(0.0, xB - xA)
    inter_h = max(0.0, yB - yA)
    inter_area = inter_w * inter_h
    
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area
    
    if union_area <= 0:
        return 0.0
    return inter_area / union_area

def run_test_inference():
    print("\n=======================================================")
    print("  LEAF_AI: TESTING BEST MODEL ON UNSEEN TEST DATASET")
    print("=======================================================\n")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load YOLO model
    print(f"Loading trained weights: {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))
    
    test_img_files = sorted(list(TEST_IMG_DIR.glob("*.*")))
    print(f"Found {len(test_img_files)} test images in {TEST_IMG_DIR}\n")
    
    results_summary = {
        "total_images": len(test_img_files),
        "correct_detection": [],    # list of dicts
        "incorrect_detection": [],  # list of dicts
        "no_detection": [],         # list of dicts
        "per_class_summary": defaultdict(lambda: {"total_images": 0, "correct": 0, "incorrect": 0, "no_detection": 0})
    }
    
    sample_visuals = []
    
    for idx, img_path in enumerate(test_img_files):
        # 1. Parse Ground Truth Labels
        lbl_path = TEST_LBL_DIR / f"{img_path.stem}.txt"
        gt_boxes = []
        gt_classes = set()
        
        if lbl_path.exists():
            with open(lbl_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for l in lines:
                parts = l.strip().split()
                if parts:
                    cls_id = int(parts[0])
                    xc, yc, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                    gt_boxes.append((cls_id, xc, yc, w, h))
                    gt_classes.add(cls_id)
                    
        primary_gt_class = list(gt_classes)[0] if gt_classes else -1
        primary_gt_name = CLASS_NAMES.get(primary_gt_class, "None")
        
        results_summary["per_class_summary"][primary_gt_name]["total_images"] += 1
        
        # 2. Run Inference
        preds = model.predict(source=str(img_path), conf=0.25, imgsz=320, device="cpu", verbose=False)
        res = preds[0]
        
        pred_boxes = []
        pred_classes = set()
        
        for b in res.boxes:
            p_cls = int(b.cls[0].item())
            p_conf = float(b.conf[0].item())
            xyxy = b.xyxy[0].tolist()
            pred_boxes.append({
                "class_id": p_cls,
                "class_name": CLASS_NAMES.get(p_cls, f"Class_{p_cls}"),
                "confidence": round(p_conf, 4),
                "bbox_xyxy": [round(v, 1) for v in xyxy]
            })
            pred_classes.add(p_cls)
            
        # 3. Categorize Detection Outcome
        # Status can be: 'CORRECT', 'INCORRECT', 'NO_DETECTION'
        if len(pred_boxes) == 0:
            status = "NO_DETECTION"
            reason = "Model did not predict any bounding boxes above confidence threshold 0.25."
            results_summary["no_detection"].append({
                "filename": img_path.name,
                "ground_truth_classes": [CLASS_NAMES[c] for c in gt_classes],
                "reason": reason
            })
            results_summary["per_class_summary"][primary_gt_name]["no_detection"] += 1
        elif gt_classes == pred_classes or (primary_gt_class in pred_classes and len(pred_classes.difference(gt_classes)) == 0):
            status = "CORRECT"
            reason = f"Correctly detected {', '.join([SHORT_NAMES[c] for c in pred_classes])} ({len(pred_boxes)} boxes)."
            results_summary["correct_detection"].append({
                "filename": img_path.name,
                "ground_truth_classes": [CLASS_NAMES[c] for c in gt_classes],
                "predicted_classes": [CLASS_NAMES[c] for c in pred_classes],
                "num_boxes": len(pred_boxes),
                "avg_confidence": round(float(np.mean([b["confidence"] for b in pred_boxes])), 4),
                "max_confidence": round(float(max([b["confidence"] for b in pred_boxes])), 4)
            })
            results_summary["per_class_summary"][primary_gt_name]["correct"] += 1
        else:
            status = "INCORRECT"
            reason = f"Mismatch: GT={list(gt_classes)}, Pred={list(pred_classes)}"
            results_summary["incorrect_detection"].append({
                "filename": img_path.name,
                "ground_truth_classes": [CLASS_NAMES[c] for c in gt_classes],
                "predicted_classes": [CLASS_NAMES[c] for c in pred_classes],
                "num_boxes": len(pred_boxes),
                "predictions": pred_boxes
            })
            results_summary["per_class_summary"][primary_gt_name]["incorrect"] += 1
            
        # 4. Generate Visualized Prediction Image
        im = Image.open(img_path).convert("RGB")
        w_img, h_img = im.size
        draw = ImageDraw.Draw(im)
        
        # Draw predictions
        for b in pred_boxes:
            c_id = b["class_id"]
            conf = b["confidence"]
            x1, y1, x2, y2 = b["bbox_xyxy"]
            color = CLASS_COLORS.get(c_id, (0, 255, 0))
            s_name = SHORT_NAMES.get(c_id, f"Class_{c_id}")
            
            # Bounding box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # Badge text
            badge_text = f"{s_name} {conf:.2f}"
            t_box = draw.textbbox((x1, max(0, y1 - 18)), badge_text)
            draw.rectangle([t_box[0]-2, t_box[1]-2, t_box[2]+2, t_box[3]+2], fill=color)
            draw.text((x1, max(0, y1 - 18)), badge_text, fill=(255, 255, 255))
            
        # Draw status banner on top
        banner_color = (34, 139, 34) if status == "CORRECT" else ((220, 20, 60) if status == "INCORRECT" else (100, 100, 100))
        draw.rectangle([0, 0, w_img, 24], fill=banner_color)
        status_label = f"[{status}] GT: {SHORT_NAMES.get(primary_gt_class, 'None')} | Preds: {len(pred_boxes)}"
        draw.text((6, 4), status_label, fill=(255, 255, 255))
        
        out_img_path = OUTPUT_DIR / f"pred_{img_path.name}"
        im.save(out_img_path)
        
        if idx < 12:
            sample_visuals.append(im)
            
    # Build 3x4 Summary Grid
    if sample_visuals:
        cols = 4
        rows = (len(sample_visuals) + cols - 1) // cols
        pw, ph = sample_visuals[0].size
        grid = Image.new("RGB", (cols * pw, rows * ph), color=(30, 30, 30))
        for i, s_im in enumerate(sample_visuals):
            grid.paste(s_im, ((i % cols) * pw, (i // cols) * ph))
        grid_path = OUTPUT_DIR / "test_inference_grid.jpg"
        grid.save(grid_path, quality=95)
        print(f"Saved test inference visual grid at: {grid_path}")
        
    # Save JSON summary
    json_path = OUTPUT_DIR / "test_inference_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)
    print(f"Saved test inference JSON results at: {json_path}")
    
    # Save Markdown report
    generate_markdown_report(results_summary)
    
    return results_summary

def generate_markdown_report(res):
    md_path = OUTPUT_DIR / "inference_summary.md"
    
    total = res["total_images"]
    n_correct = len(res["correct_detection"])
    n_incorrect = len(res["incorrect_detection"])
    n_none = len(res["no_detection"])
    
    p_correct = (n_correct / total) * 100 if total > 0 else 0
    p_incorrect = (n_incorrect / total) * 100 if total > 0 else 0
    p_none = (n_none / total) * 100 if total > 0 else 0
    
    lines = [
        "# LEAF_AI: Tomato Model Test Set Inference Evaluation Report",
        "",
        f"* **Model Evaluated:** `model/tomato/best.pt` (YOLOv8n Baseline)",
        f"* **Test Image Directory:** `training/datasets/processed/tomato/images/test/`",
        f"* **Total Unseen Test Images:** {total}",
        f"* **Confidence Threshold:** `0.25`",
        f"* **Inference Output Directory:** `training/runs/tomato/inference_test/`",
        "",
        "---",
        "",
        "## 1. Overall Test Results Summary",
        "",
        "| Outcome Category | Image Count | Percentage | Description |",
        "|---|:---:|:---:|---|",
        f"|  **Correct Detection** | **{n_correct}** | **{p_correct:.1f}%** | Model detected correct disease class matching Ground Truth. |",
        f"|  **Incorrect Detection** | **{n_incorrect}** | **{p_incorrect:.1f}%** | Misclassification or unexpected disease class detected. |",
        f"|  **No Detection (Missed)** | **{n_none}** | **{p_none:.1f}%** | Disease present in GT but no bboxes predicted $\\ge 0.25$. |",
        f"| **Total Evaluated** | **{total}** | **100.0%** | **Complete Unseen Test Set** |",
        "",
        "---",
        "",
        "## 2. Per-Class Diagnostic Performance Breakdown",
        "",
        "| Ground Truth Disease Class | Total Test Images | Correct | Incorrect | No Detection | Accuracy Rate |",
        "|---|:---:|:---:|:---:|:---:|:---:|",
    ]
    
    for cname in ["Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight"]:
        stats = res["per_class_summary"].get(cname, {"total_images": 0, "correct": 0, "incorrect": 0, "no_detection": 0})
        t_c = stats["total_images"]
        c_corr = stats["correct"]
        c_inc = stats["incorrect"]
        c_none = stats["no_detection"]
        acc = (c_corr / t_c * 100) if t_c > 0 else 0.0
        lines.append(f"| **`{cname}`** | {t_c} | {c_corr} | {c_inc} | {c_none} | **{acc:.1f}%** |")
        
    lines.extend([
        "",
        "---",
        "",
        "## 3. Detailed Image-by-Image Classification Breakdown",
        "",
        "### 3.1 Correctly Detected Images (" + str(n_correct) + " images)",
        "",
        "| # | Image Filename | Disease Class | Boxes Found | Max Conf | Avg Conf |",
        "|---|---|---|:---:|:---:|:---:|",
    ])
    
    for i, item in enumerate(res["correct_detection"]):
        d_name = item["predicted_classes"][0].replace("Tomato___", "") if item["predicted_classes"] else "None"
        lines.append(f"| {i+1} | `{item['filename']}` | **{d_name}** | {item['num_boxes']} | {item['max_confidence']:.2f} | {item['avg_confidence']:.2f} |")
        
    lines.extend([
        "",
        "### 3.2 Incorrectly Detected Images (" + str(n_incorrect) + " images)",
        "",
        "| # | Image Filename | Ground Truth Class | Predicted Class | Notes / Misclassification |",
        "|---|---|---|---|---|",
    ])
    
    if n_incorrect == 0:
        lines.append("| — | *None* | — | — | *No false classification errors found.* |")
    else:
        for i, item in enumerate(res["incorrect_detection"]):
            gt_s = ", ".join([c.replace("Tomato___", "") for c in item["ground_truth_classes"]])
            pred_s = ", ".join([c.replace("Tomato___", "") for c in item["predicted_classes"]])
            lines.append(f"| {i+1} | `{item['filename']}` | **{gt_s}** | **{pred_s}** | Confused with {pred_s} |")
            
    lines.extend([
        "",
        "### 3.3 Missed Detections / No Bounding Boxes (" + str(n_none) + " images)",
        "",
        "| # | Image Filename | Ground Truth Class | Observation |",
        "|---|---|---|---|",
    ])
    
    if n_none == 0:
        lines.append("| — | *None* | — | *No missed images. 100% of images had detections.* |")
    else:
        for i, item in enumerate(res["no_detection"]):
            gt_s = ", ".join([c.replace("Tomato___", "") for c in item["ground_truth_classes"]])
            lines.append(f"| {i+1} | `{item['filename']}` | **{gt_s}** | Lesions below threshold or low contrast |")
            
    lines.extend([
        "",
        "---",
        "",
        "## 4. Visual Inspection Artifacts",
        "",
        "* **Visual Grid (12 sample images):** `training/runs/tomato/inference_test/test_inference_grid.jpg`",
        "* **Full 60 Annotated Test Images:** Available in `training/runs/tomato/inference_test/pred_*.jpg`",
        "",
        "Each image is marked with a color-coded top banner:",
        "- 🟩 **Green Banner:** `[CORRECT]` Detection matches ground truth",
        "- 🟥 **Red Banner:** `[INCORRECT]` Misclassification / class mismatch",
        "- ⬛ **Grey Banner:** `[NO_DETECTION]` No boxes detected"
    ])
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved Markdown report at: {md_path}")

if __name__ == "__main__":
    run_test_inference()
