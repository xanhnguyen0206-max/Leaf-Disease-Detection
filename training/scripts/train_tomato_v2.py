import os
import sys
import json
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import yaml
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torch

# Optimize CPU multi-threading
torch.set_num_threads(max(1, os.cpu_count() or 4))
from ultralytics import YOLO

BASE_DIR = Path("c:/Users/Admin/Leaf-Disease-Detection")
DATASET_YAML = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2" / "data.yaml"
RUNS_DIR = BASE_DIR / "training" / "runs" / "tomato_v2"
MODEL_EXPORT_DIR = BASE_DIR / "model" / "tomato_v2"
BASELINE_MODEL_PATH = BASE_DIR / "model" / "tomato" / "best.pt"
HARD_NEGATIVES_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2" / "hard_negatives"
PREDICTIONS_DIR = RUNS_DIR / "predictions"
DOCS_DIR = BASE_DIR / "training" / "docs"

CLASS_NAMES = ["Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight"]
CLASS_COLORS = {
    0: (255, 50, 50),    # Bacterial Spot: Red
    1: (255, 165, 0),   # Early Blight: Orange
    2: (160, 32, 240),  # Late Blight: Purple
}

def evaluate_false_positive_rate(model_path, images_dir, conf_thresh=0.25):
    """
    Evaluates false positive rate on negative/healthy images.
    Returns: (fp_count, total_count, fp_rate, details)
    """
    model = YOLO(str(model_path))
    image_paths = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
    
    if not image_paths:
        return 0, 0, 0.0, []
        
    fp_count = 0
    details = []
    
    for img_p in image_paths:
        results = model.predict(source=str(img_p), conf=conf_thresh, verbose=False)
        boxes = results[0].boxes
        num_dets = len(boxes)
        if num_dets > 0:
            fp_count += 1
            dets = []
            for b in boxes:
                cid = int(b.cls.item())
                conf = float(b.conf.item())
                dets.append((CLASS_NAMES[cid] if cid < len(CLASS_NAMES) else str(cid), conf))
            details.append({"image": img_p.name, "detections": dets})
            
    fp_rate = fp_count / len(image_paths) if image_paths else 0.0
    return fp_count, len(image_paths), fp_rate, details

def run_real_world_inferences(model_path, output_dir):
    """
    Run inference on representative test cases:
    1. Healthy leaf (bright background)
    2. Healthy leaf (dark background)
    3. Healthy leaf (blurred background)
    4. Bacterial Spot
    5. Early Blight
    6. Late Blight
    7. Complex/mixed background
    """
    print("\n--- Running Real-World & Test Inference Cases ---")
    output_dir.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(model_path))
    
    test_img_dir = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2" / "images" / "test"
    test_lbl_dir = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2" / "labels" / "test"
    
    # Pick 1 representative test image from each class and 3 healthy images
    selected_images = []
    
    # Healthy images
    healthy_test = [p for p in test_img_dir.glob("*.jpg") if not (test_lbl_dir / f"{p.stem}.txt").read_text().strip()]
    for p in healthy_test[:3]:
        selected_images.append((p, "Healthy Leaf (Negative Benchmark)"))
        
    # Diseased images
    for target_cid, cname in enumerate(CLASS_NAMES):
        for img_p in test_img_dir.glob("*.jpg"):
            lbl_p = test_lbl_dir / f"{img_p.stem}.txt"
            if lbl_p.exists():
                lines = lbl_p.read_text().strip().splitlines()
                cids = [int(l.split()[0]) for l in lines if l.split()]
                if target_cid in cids and img_p not in [x[0] for x in selected_images]:
                    selected_images.append((img_p, f"Ground Truth: {cname}"))
                    break
                    
    # Also test on hard negatives if available
    hard_negs = list(HARD_NEGATIVES_DIR.glob("*.jpg"))
    for hn in hard_negs[:2]:
        if hn not in [x[0] for x in selected_images]:
            selected_images.append((hn, "Hard Negative Evaluation Sample"))
            
    prediction_results = []
    
    for idx, (img_p, desc) in enumerate(selected_images):
        results = model.predict(source=str(img_p), conf=0.25, verbose=False)[0]
        im = Image.open(img_p).convert("RGB")
        w, h = im.size
        draw = ImageDraw.Draw(im)
        
        detected_items = []
        for box in results.boxes:
            cid = int(box.cls.item())
            conf = float(box.conf.item())
            xyxy = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
            
            cname = CLASS_NAMES[cid] if cid < len(CLASS_NAMES) else str(cid)
            detected_items.append(f"{cname} ({conf:.2f})")
            
            color = CLASS_COLORS.get(cid, (0, 255, 0))
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            label_text = f"{cname.split('___')[-1]}: {conf:.2f}"
            draw.text((x1 + 3, y1 + 3), label_text, fill=color)
            
        out_name = f"pred_{idx:02d}_{img_p.stem[:25]}.jpg"
        im.save(output_dir / out_name, quality=90)
        prediction_results.append({
            "image": img_p.name,
            "description": desc,
            "detections": detected_items,
            "output_file": str((output_dir / out_name).as_posix())
        })
        print(f"Saved inference [{idx+1}/{len(selected_images)}]: {desc} -> {detected_items or 'No detections (Clean)'}")
        
    return prediction_results

def train_tomato_v2(epochs=25, batch_size=16, imgsz=512, patience=8):
    print("\n==========================================")
    print("  LEAF_AI: TOMATO V2 MODEL RETRAINING")
    print("==========================================\n")
    
    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device} (CUDA available: {torch.cuda.is_available()})")
    print(f"CPU Threads: {torch.get_num_threads()}")
    
    model_name = "yolov8n.pt"
    print(f"Loading pretrained weights: {model_name}...")
    model = YOLO(model_name)
    
    training_config = {
        "model": model_name,
        "data": str(DATASET_YAML.as_posix()),
        "epochs": epochs,
        "batch": batch_size,
        "imgsz": imgsz,
        "patience": patience,
        "device": device,
        "workers": 0,
        "cache": True,
        "project": str(RUNS_DIR.as_posix()),
        "name": "v2_yolov8n",
        "exist_ok": True,
        "pretrained": True,
        "optimizer": "auto",
        "verbose": True,
        "seed": 42
    }
    
    print("\nTraining Configuration:")
    for k, v in training_config.items():
        print(f"  - {k}: {v}")
        
    start_train_time = time.time()
    print("\n>>> Starting Fine-Tuning on Dataset V2...")
    train_results = model.train(**training_config)
    train_duration = time.time() - start_train_time
    print(f"\n>>> Training completed in {train_duration:.2f}s ({train_duration/60:.2f} min).")
    
    best_weights_path = RUNS_DIR / "v2_yolov8n" / "weights" / "best.pt"
    if not best_weights_path.exists():
        best_weights_path = RUNS_DIR / "v2_yolov8n" / "weights" / "last.pt"
    print(f"\nEvaluating Best Model from: {best_weights_path}")
    best_model = YOLO(str(best_weights_path))
    
    # 1. Validation Set Evaluation
    print("\n>>> Evaluating V2 Model on Validation Split...")
    val_results = best_model.val(data=str(DATASET_YAML.as_posix()), split="val", imgsz=imgsz, device=device)
    
    # 2. Test Set Evaluation
    print("\n>>> Evaluating V2 Model on Test Split...")
    test_results = best_model.val(data=str(DATASET_YAML.as_posix()), split="test", imgsz=imgsz, device=device)
    
    v2_metrics = {
        "val": {
            "precision": float(val_results.results_dict.get("metrics/precision(B)", 0.0)),
            "recall": float(val_results.results_dict.get("metrics/recall(B)", 0.0)),
            "mAP50": float(val_results.results_dict.get("metrics/mAP50(B)", 0.0)),
            "mAP50_95": float(val_results.results_dict.get("metrics/mAP50-95(B)", 0.0)),
        },
        "test": {
            "precision": float(test_results.results_dict.get("metrics/precision(B)", 0.0)),
            "recall": float(test_results.results_dict.get("metrics/recall(B)", 0.0)),
            "mAP50": float(test_results.results_dict.get("metrics/mAP50(B)", 0.0)),
            "mAP50_95": float(test_results.results_dict.get("metrics/mAP50-95(B)", 0.0)),
        }
    }
    
    # Per-class test metrics
    per_class_metrics = {}
    if hasattr(test_results, 'box') and hasattr(test_results.box, 'maps'):
        maps = test_results.box.maps
        p_per = test_results.box.p
        r_per = test_results.box.r
        for idx, cname in enumerate(CLASS_NAMES):
            if idx < len(maps):
                per_class_metrics[cname] = {
                    "precision": float(p_per[idx]) if idx < len(p_per) else 0.0,
                    "recall": float(r_per[idx]) if idx < len(r_per) else 0.0,
                    "mAP50": float(test_results.box.ap50[idx]) if hasattr(test_results.box, 'ap50') and idx < len(test_results.box.ap50) else 0.0,
                    "mAP50_95": float(maps[idx])
                }
    v2_metrics["per_class_test"] = per_class_metrics
    
    # 3. False Positive Evaluation on Hard Negatives & Healthy Test Split
    print("\n>>> Evaluating False Positive Rates on Negative Leaves...")
    v2_fp_cnt, v2_fp_tot, v2_fp_rate, v2_fp_dets = evaluate_false_positive_rate(best_weights_path, HARD_NEGATIVES_DIR)
    print(f"V2 False Positive Rate on Hard Negatives: {v2_fp_cnt}/{v2_fp_tot} ({v2_fp_rate*100:.1f}%)")
    
    # Compare with Baseline on the same hard negatives if baseline model exists
    baseline_fp_cnt, baseline_fp_tot, baseline_fp_rate = None, None, None
    if BASELINE_MODEL_PATH.exists():
        print(f"\nBenchmarking Baseline Model ({BASELINE_MODEL_PATH}) on Hard Negatives...")
        b_cnt, b_tot, b_rate, _ = evaluate_false_positive_rate(BASELINE_MODEL_PATH, HARD_NEGATIVES_DIR)
        baseline_fp_cnt, baseline_fp_tot, baseline_fp_rate = b_cnt, b_tot, b_rate
        print(f"Baseline False Positive Rate on Hard Negatives: {b_cnt}/{b_tot} ({b_rate*100:.1f}%)")
        
    # 4. Real-world test predictions
    predictions = run_real_world_inferences(best_weights_path, PREDICTIONS_DIR)
    
    # 5. Export Model Artifacts to model/tomato_v2/
    MODEL_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    exported_best = MODEL_EXPORT_DIR / "best.pt"
    shutil.copy2(str(best_weights_path), str(exported_best))
    print(f"\nExported best model weights to: {exported_best}")
    
    classes_meta = {str(i): name for i, name in enumerate(CLASS_NAMES)}
    with open(MODEL_EXPORT_DIR / "classes.json", "w", encoding="utf-8") as f:
        json.dump(classes_meta, f, indent=2)
        
    metadata = {
        "model_name": "LEAF_AI Tomato Disease Detection YOLOv8n V2",
        "created_at": datetime.now().isoformat(),
        "architecture": "YOLOv8n",
        "input_size": imgsz,
        "classes": CLASS_NAMES,
        "training_epochs": epochs,
        "batch_size": batch_size,
        "dataset": "tomato_v2",
        "metrics": v2_metrics,
        "hard_negative_false_positive_rate": {
            "v2_model": {
                "fp_count": v2_fp_cnt,
                "total": v2_fp_tot,
                "rate": v2_fp_rate
            },
            "baseline_model": {
                "fp_count": baseline_fp_cnt,
                "total": baseline_fp_tot,
                "rate": baseline_fp_rate
            } if baseline_fp_cnt is not None else "N/A"
        }
    }
    with open(MODEL_EXPORT_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved classes.json and metadata.json to {MODEL_EXPORT_DIR}")
    
    return {
        "v2_metrics": v2_metrics,
        "baseline_fp_rate": baseline_fp_rate,
        "v2_fp_rate": v2_fp_rate,
        "predictions": predictions,
        "training_duration": train_duration
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--imgsz", type=int, default=384)
    parser.add_argument("--patience", type=int, default=8)
    args = parser.parse_args()
    
    train_tomato_v2(epochs=args.epochs, batch_size=args.batch, imgsz=args.imgsz, patience=args.patience)
