import os
import sys
import json
import shutil
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch

from ultralytics import YOLO

BASE_DIR = Path("c:/Users/Admin/Leaf-Disease-Detection")
DATASET_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2"
MODEL_PATH = BASE_DIR / "model" / "tomato_v2" / "best.pt"
AUDIT_DIR = BASE_DIR / "training" / "runs" / "tomato_v2" / "audit" / "bacterial_spot"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = {
    0: "Tomato___Bacterial_spot",
    1: "Tomato___Early_blight",
    2: "Tomato___Late_blight"
}

CLASS_SHORT_NAMES = {
    0: "Bacterial Spot",
    1: "Early Blight",
    2: "Late Blight"
}

def box_iou(boxA, boxB):
    # box: (x1, y1, x2, y2)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
    boxAArea = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    boxBArea = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])
    unionArea = boxAArea + boxBArea - interArea
    return interArea / unionArea if unionArea > 0 else 0.0

def run_deep_audit():
    print("==================================================")
    print("  LEAF_AI: BACTERIAL SPOT DEEP AUDIT ANALYSIS")
    print("==================================================")
    
    # ----------------------------------------------------
    # STEP 1: DATASET & BBOX SIZE ANALYSIS
    # ----------------------------------------------------
    print("\n--- 1. Analyzing Dataset & Bounding Box Distributions ---")
    
    class_boxes = defaultdict(list) # cid -> list of (w, h, area, split, img_name)
    class_img_counts = defaultdict(lambda: defaultdict(int)) # cid -> split -> count
    total_imgs_per_split = defaultdict(int)
    
    for split in ["train", "val", "test"]:
        lbl_dir = DATASET_DIR / "labels" / split
        img_dir = DATASET_DIR / "images" / split
        lbl_files = sorted(list(lbl_dir.glob("*.txt")))
        total_imgs_per_split[split] = len(lbl_files)
        
        for lf in lbl_files:
            cids_in_file = set()
            with open(lf, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    cid = int(parts[0])
                    xc, yc, w, h = map(float, parts[1:5])
                    area = w * h
                    class_boxes[cid].append({
                        "w": w,
                        "h": h,
                        "area": area,
                        "split": split,
                        "img_name": lf.stem
                    })
                    cids_in_file.add(cid)
            for c in cids_in_file:
                class_img_counts[c][split] += 1
                
    # Summary of box counts
    print(f"Total Dataset Images: {sum(total_imgs_per_split.values())} (Train: {total_imgs_per_split['train']}, Val: {total_imgs_per_split['val']}, Test: {total_imgs_per_split['test']})")
    
    bbox_stats = {}
    for cid, cname in CLASS_NAMES.items():
        boxes = class_boxes[cid]
        areas = np.array([b["area"] for b in boxes])
        widths = np.array([b["w"] for b in boxes])
        heights = np.array([b["h"] for b in boxes])
        
        # Categorization:
        # Very Small: area < 0.005 (0.5% of image area)
        # Small: 0.005 <= area < 0.02 (0.5% - 2%)
        # Medium: 0.02 <= area < 0.08 (2% - 8%)
        # Large: area >= 0.08 (> 8%)
        v_small = np.sum(areas < 0.005)
        small = np.sum((areas >= 0.005) & (areas < 0.02))
        med = np.sum((areas >= 0.02) & (areas < 0.08))
        large = np.sum(areas >= 0.08)
        n = len(areas)
        
        bbox_stats[cname] = {
            "total_boxes": n,
            "train_boxes": sum(1 for b in boxes if b["split"] == "train"),
            "val_boxes": sum(1 for b in boxes if b["split"] == "val"),
            "test_boxes": sum(1 for b in boxes if b["split"] == "test"),
            "train_images": class_img_counts[cid]["train"],
            "val_images": class_img_counts[cid]["val"],
            "test_images": class_img_counts[cid]["test"],
            "total_images": sum(class_img_counts[cid].values()),
            "avg_boxes_per_img": n / max(1, sum(class_img_counts[cid].values())),
            "min_area": float(np.min(areas)),
            "max_area": float(np.max(areas)),
            "mean_area": float(np.mean(areas)),
            "median_area": float(np.median(areas)),
            "p10_area": float(np.percentile(areas, 10)),
            "p25_area": float(np.percentile(areas, 25)),
            "p50_area": float(np.percentile(areas, 50)),
            "p75_area": float(np.percentile(areas, 75)),
            "p90_area": float(np.percentile(areas, 90)),
            "very_small_count": int(v_small),
            "very_small_pct": float(v_small / n * 100),
            "small_count": int(small),
            "small_pct": float(small / n * 100),
            "medium_count": int(med),
            "medium_pct": float(med / n * 100),
            "large_count": int(large),
            "large_pct": float(large / n * 100),
            "mean_pixel_dim_384": float(np.mean(np.sqrt(areas)) * 384),
            "median_pixel_dim_384": float(np.median(np.sqrt(areas)) * 384),
            "p10_pixel_dim_384": float(np.percentile(np.sqrt(areas), 10) * 384),
            "mean_pixel_dim_640": float(np.mean(np.sqrt(areas)) * 640),
            "median_pixel_dim_640": float(np.median(np.sqrt(areas)) * 640),
            "p10_pixel_dim_640": float(np.percentile(np.sqrt(areas), 10) * 640),
        }
        
    print("\n--- Bounding Box Area Comparison ---")
    for cname, s in bbox_stats.items():
        print(f"\n{cname}:")
        print(f"  Total boxes: {s['total_boxes']} in {s['total_images']} images (Avg: {s['avg_boxes_per_img']:.1f} boxes/img)")
        print(f"  Area P10: {s['p10_area']:.6f} | P25: {s['p25_area']:.6f} | Median: {s['median_area']:.6f} | Mean: {s['mean_area']:.6f} | P75: {s['p75_area']:.6f} | P90: {s['p90_area']:.6f}")
        print(f"  Size Breakdown: Very Small={s['very_small_pct']:.1f}%, Small={s['small_pct']:.1f}%, Med={s['medium_pct']:.1f}%, Large={s['large_pct']:.1f}%")
        print(f"  Equivalent Square Dimension at 384x384: Median={s['median_pixel_dim_384']:.1f}px (P10={s['p10_pixel_dim_384']:.1f}px)")
        print(f"  Equivalent Square Dimension at 640x640: Median={s['median_pixel_dim_640']:.1f}px (P10={s['p10_pixel_dim_640']:.1f}px)")

    # ----------------------------------------------------
    # STEP 2: TEST SET INFERENCE & ERROR TAXONOMY
    # ----------------------------------------------------
    print("\n--- 2. Running Test Set Inference & Ground Truth Matching ---")
    model = YOLO(str(MODEL_PATH))
    
    test_img_dir = DATASET_DIR / "images" / "test"
    test_lbl_dir = DATASET_DIR / "labels" / "test"
    test_img_paths = sorted(list(test_img_dir.glob("*.jpg")))
    
    print(f"Found {len(test_img_paths)} images in test set.")
    
    # Detailed per-ground-truth tracking for Bacterial Spot
    bacterial_gt_total = 0
    bacterial_correct = 0
    bacterial_confused_early_blight = 0
    bacterial_confused_late_blight = 0
    bacterial_missed = 0
    bacterial_poor_loc = 0 # matched with IoU between 0.10 and 0.30
    bacterial_low_conf = 0 # matched but confidence < 0.40
    
    bacterial_confidences_correct = []
    bacterial_confidences_confused = []
    
    # Confidence distribution for ALL Bacterial Spot predictions
    all_bacterial_pred_confs = []
    
    hard_cases = {
        "missed": [],        # Images with high proportion of missed bacterial spots
        "confused_eb": [],   # Images where bacterial spot was predicted as Early Blight
        "low_conf": [],      # Images where bacterial spot had confidence < 0.40
        "poor_loc": []       # Images with poor bounding box alignment
    }
    
    image_eval_results = []
    
    for img_p in test_img_paths:
        lbl_p = test_lbl_dir / f"{img_p.stem}.txt"
        gt_boxes = []
        if lbl_p.exists():
            with open(lbl_p, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    cid = int(parts[0])
                    xc, yc, w, h = map(float, parts[1:5])
                    x1 = xc - w / 2.0
                    y1 = yc - h / 2.0
                    x2 = xc + w / 2.0
                    y2 = yc + h / 2.0
                    gt_boxes.append({
                        "cid": cid,
                        "bbox": (x1, y1, x2, y2),
                        "w": w,
                        "h": h,
                        "area": w * h
                    })
                    
        # Run inference at low threshold (0.10) to detect low-confidence objects too
        preds = model.predict(source=str(img_p), conf=0.10, verbose=False)[0]
        
        pred_boxes = []
        for b in preds.boxes:
            p_cid = int(b.cls[0].item())
            p_conf = float(b.conf[0].item())
            xyxyn = b.xyxyn[0].tolist()
            pred_boxes.append({
                "cid": p_cid,
                "conf": p_conf,
                "bbox": tuple(xyxyn)
            })
            if p_cid == 0:
                all_bacterial_pred_confs.append(p_conf)
                
        # Match Bacterial Spot GTs
        bacterial_gts_in_img = [g for g in gt_boxes if g["cid"] == 0]
        bacterial_gt_total += len(bacterial_gts_in_img)
        
        img_missed = 0
        img_confused_eb = 0
        img_low_conf = 0
        img_poor_loc = 0
        img_correct = 0
        
        matched_preds = set()
        
        for g in bacterial_gts_in_img:
            g_box = g["bbox"]
            best_iou = 0.0
            best_p = None
            best_p_idx = -1
            
            for p_idx, p in enumerate(pred_boxes):
                iou = box_iou(g_box, p["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_p = p
                    best_p_idx = p_idx
                    
            if best_p is not None and best_iou >= 0.30:
                matched_preds.add(best_p_idx)
                if best_p["cid"] == 0: # Correct class
                    if best_p["conf"] >= 0.25:
                        bacterial_correct += 1
                        img_correct += 1
                        bacterial_confidences_correct.append(best_p["conf"])
                        if best_p["conf"] < 0.40:
                            bacterial_low_conf += 1
                            img_low_conf += 1
                    else:
                        bacterial_low_conf += 1
                        img_low_conf += 1
                        bacterial_missed += 1 # Filtered by 0.25 threshold
                        img_missed += 1
                elif best_p["cid"] == 1: # Confused as Early Blight
                    bacterial_confused_early_blight += 1
                    img_confused_eb += 1
                    bacterial_confidences_confused.append(best_p["conf"])
                elif best_p["cid"] == 2: # Confused as Late Blight
                    bacterial_confused_late_blight += 1
            elif best_p is not None and 0.10 <= best_iou < 0.30:
                bacterial_poor_loc += 1
                img_poor_loc += 1
                if best_p["cid"] == 1:
                    bacterial_confused_early_blight += 1
                    img_confused_eb += 1
            else:
                bacterial_missed += 1
                img_missed += 1
                
        if len(bacterial_gts_in_img) > 0:
            rec = {
                "img_path": img_p,
                "gt_count": len(bacterial_gts_in_img),
                "correct": img_correct,
                "missed": img_missed,
                "confused_eb": img_confused_eb,
                "low_conf": img_low_conf,
                "poor_loc": img_poor_loc,
                "gt_boxes": gt_boxes,
                "pred_boxes": pred_boxes
            }
            image_eval_results.append(rec)
            if img_confused_eb > 0:
                hard_cases["confused_eb"].append(rec)
            if img_missed >= 3 or (len(bacterial_gts_in_img) > 0 and img_missed / len(bacterial_gts_in_img) > 0.5):
                hard_cases["missed"].append(rec)
            if img_low_conf > 0:
                hard_cases["low_conf"].append(rec)
            if img_poor_loc > 0:
                hard_cases["poor_loc"].append(rec)

    # Calculate statistics table
    print("\n--- Bacterial Spot Error Taxonomy (on 395 GT boxes in Test Set) ---")
    error_taxonomy = [
        {"Error Type": "Correctly Detected (Class 0, IoU >= 0.30, Conf >= 0.25)", "Count": bacterial_correct, "Percentage": bacterial_correct / max(1, bacterial_gt_total) * 100},
        {"Error Type": "Missed / False Negative (No overlap or Conf < 0.25)", "Count": bacterial_missed, "Percentage": bacterial_missed / max(1, bacterial_gt_total) * 100},
        {"Error Type": "Confused as Early Blight (Class 0 GT -> Class 1 Pred)", "Count": bacterial_confused_early_blight, "Percentage": bacterial_confused_early_blight / max(1, bacterial_gt_total) * 100},
        {"Error Type": "Confused as Late Blight (Class 0 GT -> Class 2 Pred)", "Count": bacterial_confused_late_blight, "Percentage": bacterial_confused_late_blight / max(1, bacterial_gt_total) * 100},
        {"Error Type": "Poor Localization (0.10 <= IoU < 0.30)", "Count": bacterial_poor_loc, "Percentage": bacterial_poor_loc / max(1, bacterial_gt_total) * 100},
        {"Error Type": "Low Confidence Detections (0.25 <= Conf < 0.40)", "Count": bacterial_low_conf, "Percentage": bacterial_low_conf / max(1, bacterial_gt_total) * 100},
    ]
    for row in error_taxonomy:
        print(f"  {row['Error Type']:<60} | Count: {row['Count']:<4} | {row['Percentage']:.1f}%")

    # ----------------------------------------------------
    # STEP 3: CONFIDENCE ANALYSIS
    # ----------------------------------------------------
    confs_arr = np.array(all_bacterial_pred_confs)
    print("\n--- Bacterial Spot Prediction Confidence Distribution ---")
    conf_ranges = {
        "Below 0.25 (< 0.25)": np.sum(confs_arr < 0.25),
        "0.25 - 0.40": np.sum((confs_arr >= 0.25) & (confs_arr < 0.40)),
        "0.40 - 0.50": np.sum((confs_arr >= 0.40) & (confs_arr < 0.50)),
        "0.50 - 0.70": np.sum((confs_arr >= 0.50) & (confs_arr < 0.70)),
        "Above 0.70 (> 0.70)": np.sum(confs_arr >= 0.70),
    }
    for rng, count in conf_ranges.items():
        print(f"  {rng:<25}: {count:<4} ({count / len(confs_arr) * 100:.1f}%)")
    print(f"  Mean Conf (Correct Detections): {np.mean(bacterial_confidences_correct):.4f}" if bacterial_confidences_correct else "  Mean Conf: N/A")
    print(f"  Mean Conf (Confused as Early Blight): {np.mean(bacterial_confidences_confused):.4f}" if bacterial_confidences_confused else "  Mean Conf Confused: N/A")

    # ----------------------------------------------------
    # STEP 4: ANNOTATION QUALITY & MORPHOLOGY ANALYSIS
    # ----------------------------------------------------
    print("\n--- 4. Checking Annotation Quality & Anomalies ---")
    suspicious_annotations = []
    
    for split in ["train", "val", "test"]:
        lbl_dir = DATASET_DIR / "labels" / split
        for lf in lbl_dir.glob("*.txt"):
            with open(lf, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    parts = line.strip().split()
                    if not parts: continue
                    cid = int(parts[0])
                    if cid != 0: continue
                    xc, yc, w, h = map(float, parts[1:5])
                    area = w * h
                    aspect = w / max(1e-5, h)
                    
                    # Criteria for anomaly:
                    # 1. Extremely tiny (area < 0.0004 or dimension < 0.015, e.g. < 5px)
                    if area < 0.0004:
                        suspicious_annotations.append({
                            "file": f"{split}/{lf.name}",
                            "line": idx + 1,
                            "issue": "Suspiciously tiny box (Area < 0.04% of image, <6px)",
                            "bbox": (xc, yc, w, h),
                            "area": area
                        })
                    # 2. Extremely large for bacterial spot (spot disease usually < 0.05, if > 0.15 it's whole leaf/group)
                    elif area > 0.15:
                        suspicious_annotations.append({
                            "file": f"{split}/{lf.name}",
                            "line": idx + 1,
                            "issue": "Suspiciously huge box for Bacterial Spot (Covers multi-lesions or whole foliage)",
                            "bbox": (xc, yc, w, h),
                            "area": area
                        })
                    # 3. Extreme aspect ratio (aspect > 6 or aspect < 0.16)
                    elif aspect > 6.0 or aspect < 0.16:
                        suspicious_annotations.append({
                            "file": f"{split}/{lf.name}",
                            "line": idx + 1,
                            "issue": f"Extreme aspect ratio ({aspect:.2f}:1) - likely sliver or boundary artifact",
                            "bbox": (xc, yc, w, h),
                            "area": area
                        })
                        
    print(f"Total Suspicious / Inconsistent Annotations Detected: {len(suspicious_annotations)} out of {len(class_boxes[0])} Bacterial Spot boxes ({len(suspicious_annotations)/len(class_boxes[0])*100:.2f}%)")
    print("Sample Suspicious Annotations:")
    for sa in suspicious_annotations[:8]:
        print(f"  [{sa['file']}:L{sa['line']}] {sa['issue']} (w={sa['bbox'][2]:.4f}, h={sa['bbox'][3]:.4f}, area={sa['area']:.5f})")

    # ----------------------------------------------------
    # STEP 5: VISUALIZE HARD CASES & CONFUSION GRID
    # ----------------------------------------------------
    print("\n--- 5. Generating Hard Case Visualizations ---")
    generate_audit_visualizations(hard_cases, AUDIT_DIR)

    audit_summary = {
        "bbox_stats": bbox_stats,
        "error_taxonomy": error_taxonomy,
        "conf_ranges": {k: int(v) for k, v in conf_ranges.items()},
        "suspicious_count": len(suspicious_annotations),
        "suspicious_samples": suspicious_annotations[:10],
        "hard_cases_counts": {k: len(v) for k, v in hard_cases.items()}
    }
    
    with open(AUDIT_DIR / "audit_metrics.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2)
    print(f"Saved audit metrics JSON to {AUDIT_DIR / 'audit_metrics.json'}")
    
    return audit_summary

def generate_audit_visualizations(hard_cases, output_dir):
    """
    Creates visual comparison grids showing ground truth vs predictions on hard cases:
    - bacterial_spot_hard_cases.jpg
    - bacterial_spot_confused_with_early_blight.jpg
    """
    colors = {
        "gt_bs": (255, 50, 50),     # Ground Truth Bacterial Spot (Red)
        "pred_bs": (0, 255, 120),   # Predicted Bacterial Spot (Green)
        "pred_eb": (255, 165, 0),   # Predicted Early Blight (Orange)
        "pred_lb": (160, 32, 240)   # Predicted Late Blight (Purple)
    }
    
    # 1. Main Hard Cases Grid: 6 samples (2 Confused with EB, 2 Missed, 2 Low Conf)
    selected = []
    if hard_cases["confused_eb"]:
        selected.extend(hard_cases["confused_eb"][:3])
    if hard_cases["missed"]:
        for m in hard_cases["missed"]:
            if m not in selected and len(selected) < 6:
                selected.append(m)
    if len(selected) < 6 and hard_cases["low_conf"]:
        for lc in hard_cases["low_conf"]:
            if lc not in selected and len(selected) < 6:
                selected.append(lc)
                
    if not selected:
        print("No hard cases to visualize.")
        return
        
    cell_w, cell_h = 384, 384
    cols = 2 # Left: Ground Truth, Right: Predictions
    rows = len(selected)
    
    grid = Image.new("RGB", (cell_w * 2, cell_h * rows + 80), color=(20, 20, 20))
    draw = ImageDraw.Draw(grid)
    draw.text((20, 15), "LEAF_AI BACTERIAL SPOT AUDIT: GROUND TRUTH (LEFT) vs. YOLO V2 PREDICTIONS (RIGHT)", fill=(255, 255, 255))
    draw.text((20, 45), "Legend: RED = Ground Truth Bacterial Spot | GREEN = Pred Bacterial Spot | ORANGE = Pred Early Blight", fill=(200, 200, 200))
    
    for row_idx, item in enumerate(selected):
        img_p = item["img_path"]
        y_offset = row_idx * cell_h + 80
        
        # Left: Ground Truth
        with Image.open(img_p) as im:
            im_gt = im.convert("RGB").resize((cell_w, cell_h))
            d_gt = ImageDraw.Draw(im_gt)
            for g in item["gt_boxes"]:
                cid = g["cid"]
                x1, y1, x2, y2 = g["bbox"]
                px1 = int(x1 * cell_w)
                py1 = int(y1 * cell_h)
                px2 = int(x2 * cell_w)
                py2 = int(y2 * cell_h)
                col = (255, 50, 50) if cid == 0 else ((255, 165, 0) if cid == 1 else (160, 32, 240))
                d_gt.rectangle([px1, py1, px2, py2], outline=col, width=2)
                d_gt.text((px1 + 2, py1 + 2), f"GT:{CLASS_SHORT_NAMES[cid]}", fill=col)
            d_gt.text((10, 10), f"GT: {item['gt_count']} Bacterial Spots", fill=(255, 255, 255))
            grid.paste(im_gt, (0, y_offset))
            
        # Right: Predictions
        with Image.open(img_p) as im:
            im_pred = im.convert("RGB").resize((cell_w, cell_h))
            d_pred = ImageDraw.Draw(im_pred)
            for p in item["pred_boxes"]:
                if p["conf"] < 0.20: continue
                p_cid = p["cid"]
                x1, y1, x2, y2 = p["bbox"]
                px1 = int(x1 * cell_w)
                py1 = int(y1 * cell_h)
                px2 = int(x2 * cell_w)
                py2 = int(y2 * cell_h)
                
                if p_cid == 0:
                    col = (0, 255, 120) # Green (Bacterial Spot)
                elif p_cid == 1:
                    col = (255, 165, 0) # Orange (Early Blight)
                else:
                    col = (160, 32, 240)
                    
                d_pred.rectangle([px1, py1, px2, py2], outline=col, width=2)
                d_pred.text((px1 + 2, py1 + 2), f"{CLASS_SHORT_NAMES[p_cid]}:{p['conf']:.2f}", fill=col)
                
            info_str = f"Pred: {item['correct']} Correct, {item['missed']} Missed, {item['confused_eb']} Confused EB"
            d_pred.text((10, 10), info_str, fill=(255, 255, 255))
            grid.paste(im_pred, (cell_w, y_offset))
            
    out_grid_path = output_dir / "bacterial_spot_hard_cases.jpg"
    grid.save(out_grid_path, quality=90)
    print(f"Saved Hard Cases visualization grid to {out_grid_path}")

if __name__ == "__main__":
    run_deep_audit()
