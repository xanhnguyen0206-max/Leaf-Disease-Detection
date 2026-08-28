import os
import shutil
import hashlib
import random
from pathlib import Path
from collections import defaultdict, Counter
import yaml
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

BASE_DIR = Path("c:/Users/Admin/Leaf-Disease-Detection")
PROCESSED_BASELINE_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato"
RAW_EXTRA_DIR = BASE_DIR / "training" / "datasets" / "raw" / "tomato_extra"
PROCESSED_V2_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2"
DOCS_DIR = BASE_DIR / "training" / "docs"

# Target Classes
TARGET_CLASSES = ['Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight']
TARGET_CLASS_NAMES = {
    0: 'Tomato___Bacterial_spot',
    1: 'Tomato___Early_blight',
    2: 'Tomato___Late_blight'
}

COLOR_MAP = {
    0: (255, 50, 50),    # Bacterial Spot: Red
    1: (255, 165, 0),   # Early Blight: Orange
    2: (160, 32, 240),  # Late Blight: Purple
}

def compute_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def collect_baseline_data():
    print("\n--- Collecting Baseline Dataset ---")
    baseline_records = []
    
    for split in ["train", "val", "test"]:
        img_dir = PROCESSED_BASELINE_DIR / "images" / split
        lbl_dir = PROCESSED_BASELINE_DIR / "labels" / split
        
        if not img_dir.exists():
            continue
            
        for img_p in img_dir.glob("*.*"):
            if img_p.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                continue
                
            lbl_p = lbl_dir / f"{img_p.stem}.txt"
            boxes = []
            classes_present = set()
            
            if lbl_p.exists():
                with open(lbl_p, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if not parts:
                            continue
                        cid = int(parts[0])
                        xc, yc, w, h = map(float, parts[1:5])
                        boxes.append((cid, xc, yc, w, h))
                        classes_present.add(cid)
                        
            if len(classes_present) == 0:
                primary_cls = -1 # Healthy / Negative
            elif len(classes_present) == 1:
                primary_cls = list(classes_present)[0]
            else:
                primary_cls = sorted(list(classes_present))[0]
                
            baseline_records.append({
                "source": f"baseline_{split}",
                "img_path": img_p,
                "prefix": "base_",
                "boxes": boxes,
                "classes_present": list(classes_present),
                "primary_class": primary_cls,
                "is_healthy": (len(boxes) == 0)
            })
            
    print(f"Collected {len(baseline_records)} baseline records.")
    return baseline_records

def collect_extra_data():
    print("\n--- Collecting Tomato Extra Dataset ---")
    extra_records = []
    
    folder_mapping = {
        "bacterial_spot": 0,
        "early_blight": 1,
        "late_blight": 2,
        "healthy": -1 # Special negative class
    }
    
    for folder_name, target_cid in folder_mapping.items():
        folder_dir = RAW_EXTRA_DIR / folder_name
        if not folder_dir.exists():
            continue
            
        img_files = list(folder_dir.rglob("*.jpg")) + list(folder_dir.rglob("*.jpeg")) + list(folder_dir.rglob("*.png"))
        print(f"Folder '{folder_name}': {len(img_files)} images found.")
        
        for img_p in img_files:
            lbl_p = img_p.parent.parent / "labels" / f"{img_p.stem}.txt"
            boxes = []
            classes_present = set()
            
            if target_cid == -1:
                # Healthy -> negative class (empty label)
                boxes = []
                primary_cls = -1
                is_healthy = True
            else:
                is_healthy = False
                if lbl_p.exists():
                    with open(lbl_p, "r", encoding="utf-8") as f:
                        for line in f:
                            parts = line.strip().split()
                            if not parts:
                                continue
                            try:
                                xc, yc, w, h = map(float, parts[1:5])
                                if 0 <= xc <= 1 and 0 <= yc <= 1 and 0 < w <= 1 and 0 < h <= 1:
                                    boxes.append((target_cid, xc, yc, w, h))
                                    classes_present.add(target_cid)
                            except Exception:
                                pass
                primary_cls = target_cid
                
            extra_records.append({
                "source": f"extra_{folder_name}",
                "img_path": img_p,
                "prefix": f"ext_{folder_name[:4]}_",
                "boxes": boxes,
                "classes_present": list(classes_present),
                "primary_class": primary_cls,
                "is_healthy": is_healthy
            })
            
    print(f"Collected {len(extra_records)} extra records.")
    return extra_records

def prepare_v2_dataset():
    print("==========================================")
    print("  LEAF_AI: TOMATO DATASET V2 PREPARATION")
    print("==========================================")
    
    # 1. Collect datasets
    baseline_records = collect_baseline_data()
    extra_records = collect_extra_data()
    all_records = baseline_records + extra_records
    print(f"\nTotal combined candidate images: {len(all_records)}")
    
    # 2. Quality check and duplicate removal
    seen_hashes = {}
    valid_records = []
    duplicates = []
    corrupted = []
    
    for rec in all_records:
        p = rec["img_path"]
        try:
            with Image.open(p) as img:
                img.verify()
        except Exception as e:
            corrupted.append((p, str(e)))
            continue
            
        h = compute_file_hash(p)
        if h in seen_hashes:
            duplicates.append((p, seen_hashes[h]))
        else:
            seen_hashes[h] = p
            valid_records.append(rec)
            
    print(f"Integrity Check: {len(valid_records)} unique valid images (Corrupted: {len(corrupted)}, Duplicates: {len(duplicates)})")
    
    # 3. Stratified Split (80% train, 10% val, 10% test)
    grouped = defaultdict(list)
    for rec in valid_records:
        grouped[rec["primary_class"]].append(rec)
        
    train_records = []
    val_records = []
    test_records = []
    hard_negatives = []
    
    for cls_id, items in sorted(grouped.items()):
        random.shuffle(items)
        n = len(items)
        n_train = int(round(n * 0.80))
        n_val = int(round(n * 0.10))
        
        train_slice = items[:n_train]
        val_slice = items[n_train:n_train + n_val]
        test_slice = items[n_train + n_val:]
        
        train_records.extend(train_slice)
        val_records.extend(val_slice)
        test_records.extend(test_slice)
        
        if cls_id == -1:
            hard_negatives.extend(test_slice)
            
        cls_name = TARGET_CLASS_NAMES.get(cls_id, "Healthy_Negative")
        print(f"Class '{cls_name}' ({cls_id}): Total={n} -> Train={len(train_slice)}, Val={len(val_slice)}, Test={len(test_slice)}")
        
    splits = {
        "train": train_records,
        "val": val_records,
        "test": test_records
    }
    
    # 4. Clean & create destination directories
    if PROCESSED_V2_DIR.exists():
        shutil.rmtree(PROCESSED_V2_DIR)
    PROCESSED_V2_DIR.mkdir(parents=True, exist_ok=True)
    
    for split_name in ["train", "val", "test"]:
        (PROCESSED_V2_DIR / "images" / split_name).mkdir(parents=True, exist_ok=True)
        (PROCESSED_V2_DIR / "labels" / split_name).mkdir(parents=True, exist_ok=True)
        
    hard_neg_dir = PROCESSED_V2_DIR / "hard_negatives"
    hard_neg_dir.mkdir(parents=True, exist_ok=True)
    
    samples_dir = PROCESSED_V2_DIR / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    # 5. Write images & labels
    split_summary = {}
    
    for split_name, records in splits.items():
        box_counts = Counter()
        healthy_count = 0
        
        for idx, rec in enumerate(records):
            src_img = rec["img_path"]
            dst_name = f"{rec['prefix']}{src_img.stem}_{idx:04d}.jpg"
            dst_img = PROCESSED_V2_DIR / "images" / split_name / dst_name
            dst_lbl = PROCESSED_V2_DIR / "labels" / split_name / f"{Path(dst_name).stem}.txt"
            
            # For healthy images, resize high-res images down to max dimension 640 to save disk space while preserving detail
            if rec["is_healthy"]:
                healthy_count += 1
                with Image.open(src_img) as im:
                    im_rgb = im.convert("RGB")
                    # Resize proportionally if large
                    if max(im_rgb.size) > 640:
                        im_rgb.thumbnail((640, 640), Image.Resampling.LANCZOS)
                    im_rgb.save(dst_img, "JPEG", quality=85, optimize=True)
            else:
                # Disease images
                with Image.open(src_img) as im:
                    im_rgb = im.convert("RGB")
                    im_rgb.save(dst_img, "JPEG", quality=85, optimize=True)
                
            # Write label file (empty for healthy)
            with open(dst_lbl, "w", encoding="utf-8") as f:
                if not rec["is_healthy"]:
                    for cid, xc, yc, w, h in rec["boxes"]:
                        f.write(f"{cid} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
                        box_counts[cid] += 1
                        
        split_summary[split_name] = {
            "total_images": len(records),
            "healthy_images": healthy_count,
            "disease_images": len(records) - healthy_count,
            "box_counts": dict(box_counts),
            "total_boxes": sum(box_counts.values())
        }
        print(f"\nWritten {split_name} split: {len(records)} images ({healthy_count} healthy negatives, {sum(box_counts.values())} bboxes)")
        
    # Copy hard negative test set
    print(f"\nWriting dedicated hard negatives evaluation set to {hard_neg_dir}...")
    for idx, rec in enumerate(hard_negatives):
        src_img = rec["img_path"]
        dst_name = f"hard_neg_{src_img.stem}_{idx:04d}.jpg"
        with Image.open(src_img) as im:
            im_rgb = im.convert("RGB")
            if max(im_rgb.size) > 640:
                im_rgb.thumbnail((640, 640), Image.Resampling.LANCZOS)
            im_rgb.save(hard_neg_dir / dst_name, "JPEG", quality=85, optimize=True)
            
    # 6. Generate data.yaml
    data_yaml_content = {
        "path": str(PROCESSED_V2_DIR.as_posix()),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": 3,
        "names": TARGET_CLASSES
    }
    
    data_yaml_path = PROCESSED_V2_DIR / "data.yaml"
    with open(data_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data_yaml_content, f, sort_keys=False)
    print(f"\nCreated data.yaml at {data_yaml_path}")
    
    # 7. Generate Dataset Visualization Grid (Phase 7)
    generate_visualization_grid(PROCESSED_V2_DIR, samples_dir / "dataset_visualization_grid.jpg")
    
    print("\nDataset V2 Summary:")
    for split_name, summary in split_summary.items():
        print(f"  [{split_name.upper()}]: {summary['total_images']} imgs ({summary['healthy_images']} healthy, {summary['disease_images']} disease) | Boxes: {summary['box_counts']} (Total={summary['total_boxes']})")
        
    return split_summary

def generate_visualization_grid(dataset_dir, output_grid_path):
    print("\n--- Generating Dataset Visualization Grid ---")
    
    class_samples = {
        0: [], # Bacterial Spot
        1: [], # Early Blight
        2: [], # Late Blight
        -1: [] # Healthy
    }
    
    train_img_dir = dataset_dir / "images" / "train"
    train_lbl_dir = dataset_dir / "labels" / "train"
    
    for img_p in sorted(train_img_dir.glob("*.jpg")):
        lbl_p = train_lbl_dir / f"{img_p.stem}.txt"
        with open(lbl_p, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            
        if not lines:
            if len(class_samples[-1]) < 4:
                class_samples[-1].append((img_p, []))
        else:
            boxes = []
            for line in lines:
                parts = line.split()
                cid = int(parts[0])
                xc, yc, w, h = map(float, parts[1:5])
                boxes.append((cid, xc, yc, w, h))
            cids = {b[0] for b in boxes}
            for c in cids:
                if len(class_samples[c]) < 4:
                    class_samples[c].append((img_p, boxes))
                    
        if all(len(v) >= 4 for v in class_samples.values()):
            break
            
    # Draw 4x4 Grid
    cell_w, cell_h = 320, 320
    grid_img = Image.new("RGB", (cell_w * 4, cell_h * 4 + 160), color=(30, 30, 30))
    draw = ImageDraw.Draw(grid_img)
    
    row_titles = [
        "Class 0: Bacterial Spot (Red)",
        "Class 1: Early Blight (Orange)",
        "Class 2: Late Blight (Purple)",
        "Healthy Leaves: Negative Samples (Zero BBoxes)"
    ]
    
    for row_idx, target_c in enumerate([0, 1, 2, -1]):
        samples = class_samples[target_c]
        row_y = row_idx * cell_h + 40
        draw.text((20, row_y - 30), row_titles[row_idx], fill=(255, 255, 255))
        
        for col_idx in range(4):
            col_x = col_idx * cell_w
            if col_idx < len(samples):
                img_p, boxes = samples[col_idx]
                with Image.open(img_p) as im:
                    im_resized = im.resize((cell_w, cell_h)).convert("RGB")
                    d = ImageDraw.Draw(im_resized)
                    for cid, xc, yc, bw, bh in boxes:
                        x1 = int((xc - bw/2) * cell_w)
                        y1 = int((yc - bh/2) * cell_h)
                        x2 = int((xc + bw/2) * cell_w)
                        y2 = int((yc + bh/2) * cell_h)
                        color = COLOR_MAP.get(cid, (0, 255, 0))
                        d.rectangle([x1, y1, x2, y2], outline=color, width=3)
                        d.text((x1 + 3, y1 + 3), TARGET_CLASS_NAMES[cid].split("___")[-1], fill=color)
                    grid_img.paste(im_resized, (col_x, row_y))
                    
    grid_img.save(output_grid_path, quality=90)
    print(f"Visualization grid saved to {output_grid_path}")

if __name__ == "__main__":
    prepare_v2_dataset()
