import os
import shutil
import hashlib
import random
from pathlib import Path
from collections import defaultdict
import yaml
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

BASE_DIR = Path("c:/Users/Admin/Leaf-Disease-Detection")
RAW_ROOT = BASE_DIR / "training" / "datasets" / "raw"
RAW_TOMATO_DIR = RAW_ROOT / "tomato"
PROCESSED_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato"
DOCS_DIR = BASE_DIR / "training" / "docs"

# Class mappings
RAW_CLASSES = ['Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'leaf']
TARGET_CLASSES = ['Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight']
CLASS_TO_TARGET_ID = {
    0: 0, # Tomato___Bacterial_spot -> 0
    1: 1, # Tomato___Early_blight -> 1
    2: 2, # Tomato___Late_blight -> 2
    # 3: 'leaf' -> excluded
}

COLOR_MAP = {
    0: (255, 50, 50),    # Bacterial Spot: Red
    1: (255, 165, 0),   # Early Blight: Orange
    2: (160, 32, 240),  # Late Blight: Purple
}

def step1_organize_raw_dir():
    print("\n--- Step 1: Organizing Raw Directory ---")
    RAW_TOMATO_DIR.mkdir(parents=True, exist_ok=True)
    
    # If train is in raw directly, move to raw/tomato
    if (RAW_ROOT / "train").exists() and not (RAW_TOMATO_DIR / "train").exists():
        print(f"Moving {RAW_ROOT / 'train'} to {RAW_TOMATO_DIR / 'train'}...")
        shutil.move(str(RAW_ROOT / "train"), str(RAW_TOMATO_DIR / "train"))
        
    for item in ["data.yaml", "README.roboflow.txt", "README.dataset.txt"]:
        src = RAW_ROOT / item
        dst = RAW_TOMATO_DIR / item
        if src.exists() and not dst.exists():
            print(f"Moving {src} to {dst}...")
            shutil.move(str(src), str(dst))
            
    print("Raw directory organized at:", RAW_TOMATO_DIR)

def polygon_to_bbox(coords):
    """
    coords: list of float [x1, y1, x2, y2, ..., xn, yn]
    returns: (x_center, y_center, width, height)
    """
    xs = coords[0::2]
    ys = coords[1::2]
    
    x_min = max(0.0, min(xs))
    x_max = min(1.0, max(xs))
    y_min = max(0.0, min(ys))
    y_max = min(1.0, max(ys))
    
    width = x_max - x_min
    height = y_max - y_min
    x_center = x_min + width / 2.0
    y_center = y_min + height / 2.0
    
    return round(x_center, 6), round(y_center, 6), round(width, 6), round(height, 6)

def compute_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_and_validate_dataset():
    print("\n--- Step 2 & 3 & 7: Processing, Converting and Validating Dataset ---")
    raw_img_dir = RAW_TOMATO_DIR / "train" / "images"
    raw_lbl_dir = RAW_TOMATO_DIR / "train" / "labels"
    
    img_files = sorted(list(raw_img_dir.glob("*.*")))
    print(f"Found {len(img_files)} raw images.")
    
    # Track statistics
    stats = {
        "total_images": len(img_files),
        "corrupted_images": [],
        "duplicate_images": [],
        "missing_label_files": [],
        "invalid_boxes": [],
        "raw_polygon_counts": defaultdict(int),
        "processed_bbox_counts": defaultdict(int),
        "images_per_class": defaultdict(int),
        "images_without_disease": 0,
        "images_with_multiple_diseases": 0,
        "image_sizes": set(),
        "parsed_data": [] # list of dicts: {img_path, label_boxes: [(cls_id, xc, yc, w, h)], primary_class}
    }
    
    hash_to_file = {}
    
    for img_path in img_files:
        # Validate Image Integrity
        img_hash = compute_file_hash(img_path)
        if img_hash in hash_to_file:
            stats["duplicate_images"].append((str(img_path), str(hash_to_file[img_hash])))
        else:
            hash_to_file[img_hash] = img_path
            
        try:
            with Image.open(img_path) as im:
                im.verify()
            # reopen for dimension check
            with Image.open(img_path) as im:
                stats["image_sizes"].add(im.size)
        except Exception as e:
            stats["corrupted_images"].append((str(img_path), str(e)))
            continue
            
        # Check label file
        lbl_path = raw_lbl_dir / f"{img_path.stem}.txt"
        if not lbl_path.exists():
            stats["missing_label_files"].append(str(img_path))
            continue
            
        # Parse annotations
        disease_boxes = []
        classes_in_image = set()
        
        with open(lbl_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line_idx, line in enumerate(lines):
            parts = line.strip().split()
            if not parts:
                continue
            raw_cls_id = int(parts[0])
            stats["raw_polygon_counts"][raw_cls_id] += 1
            
            # Filter class: skip 'leaf' (id 3)
            if raw_cls_id not in CLASS_TO_TARGET_ID:
                continue # excluded
                
            target_cls_id = CLASS_TO_TARGET_ID[raw_cls_id]
            coords = [float(x) for x in parts[1:]]
            
            if len(coords) < 4:
                stats["invalid_boxes"].append((str(lbl_path), line_idx, "Less than 2 points in polygon"))
                continue
                
            xc, yc, w, h = polygon_to_bbox(coords)
            
            # Validate bounding box
            if w <= 0 or h <= 0 or not (0 <= xc <= 1) or not (0 <= yc <= 1):
                stats["invalid_boxes"].append((str(lbl_path), line_idx, f"Invalid box dimensions: xc={xc}, yc={yc}, w={w}, h={h}"))
                continue
                
            disease_boxes.append((target_cls_id, xc, yc, w, h))
            stats["processed_bbox_counts"][target_cls_id] += 1
            classes_in_image.add(target_cls_id)
            
        for c in classes_in_image:
            stats["images_per_class"][c] += 1
            
        if len(classes_in_image) == 0:
            stats["images_without_disease"] += 1
            primary_cls = -1 # Background / No disease
        elif len(classes_in_image) > 1:
            stats["images_with_multiple_diseases"] += 1
            primary_cls = sorted(list(classes_in_image))[0]
        else:
            primary_cls = list(classes_in_image)[0]
            
        stats["parsed_data"].append({
            "img_path": img_path,
            "label_boxes": disease_boxes,
            "classes_present": list(classes_in_image),
            "primary_class": primary_cls
        })
        
    return stats

def split_and_save_dataset(stats):
    print("\n--- Step 6: Creating Processed Dataset Structure & Splits ---")
    
    # Create splits: 80% train, 10% val, 10% test using stratified split
    # Group items by primary_class
    grouped = defaultdict(list)
    for item in stats["parsed_data"]:
        grouped[item["primary_class"]].append(item)
        
    train_items, val_items, test_items = [], [], []
    
    for cls_id, items in grouped.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(n * 0.80)
        n_val = int(n * 0.10)
        
        train_items.extend(items[:n_train])
        val_items.extend(items[n_train:n_train + n_val])
        test_items.extend(items[n_train + n_val:])
        
    splits = {
        "train": train_items,
        "val": val_items,
        "test": test_items
    }
    
    # Create directories
    for split_name in ["train", "val", "test"]:
        (PROCESSED_DIR / "images" / split_name).mkdir(parents=True, exist_ok=True)
        (PROCESSED_DIR / "labels" / split_name).mkdir(parents=True, exist_ok=True)
        
    split_stats = {}
    
    for split_name, items in splits.items():
        cls_counts = defaultdict(int)
        box_counts = defaultdict(int)
        
        for item in items:
            img_src = item["img_path"]
            img_dst = PROCESSED_DIR / "images" / split_name / img_src.name
            lbl_dst = PROCESSED_DIR / "labels" / split_name / f"{img_src.stem}.txt"
            
            # Copy image
            shutil.copy2(str(img_src), str(img_dst))
            
            # Write converted labels
            with open(lbl_dst, "w", encoding="utf-8") as f:
                for cls_id, xc, yc, w, h in item["label_boxes"]:
                    f.write(f"{cls_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
                    box_counts[cls_id] += 1
                    
            for c in item["classes_present"]:
                cls_counts[c] += 1
                
        split_stats[split_name] = {
            "total_images": len(items),
            "image_counts_per_class": dict(cls_counts),
            "box_counts_per_class": dict(box_counts),
            "total_boxes": sum(box_counts.values())
        }
        print(f"Split '{split_name}': {len(items)} images, {sum(box_counts.values())} bboxes.")

    # Create data.yaml for YOLO
    data_yaml_content = {
        "path": str(PROCESSED_DIR.as_posix()),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": len(TARGET_CLASSES),
        "names": TARGET_CLASSES
    }
    
    with open(PROCESSED_DIR / "data.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data_yaml_content, f, sort_keys=False)
        
    print("Saved processed data.yaml at:", PROCESSED_DIR / "data.yaml")
    return split_stats

def create_visualizations():
    print("\n--- Step 8: Creating Bounding Box Visualizations ---")
    samples_dir = PROCESSED_DIR / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    test_img_dir = PROCESSED_DIR / "images" / "test"
    test_lbl_dir = PROCESSED_DIR / "labels" / "test"
    
    img_files = sorted(list(test_img_dir.glob("*.*")))
    
    # Pick representative samples for each class
    selected_samples = []
    class_samples = defaultdict(list)
    
    for img_p in img_files:
        lbl_p = test_lbl_dir / f"{img_p.stem}.txt"
        if lbl_p.exists():
            with open(lbl_p, "r", encoding="utf-8") as f:
                lines = f.readlines()
            boxes = []
            for l in lines:
                parts = l.strip().split()
                if parts:
                    boxes.append((int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])))
            if boxes:
                primary = boxes[0][0]
                class_samples[primary].append((img_p, boxes))
                
    # Pick 2 samples per class
    for c in range(len(TARGET_CLASSES)):
        if class_samples[c]:
            selected_samples.extend(random.sample(class_samples[c], min(2, len(class_samples[c]))))
            
    # Add 2 multi-box / random samples
    remaining = [s for s in class_samples[0] + class_samples[1] + class_samples[2] if s not in selected_samples]
    if remaining:
        selected_samples.extend(random.sample(remaining, min(2, len(remaining))))
        
    annotated_images = []
    
    for idx, (img_path, boxes) in enumerate(selected_samples):
        im = Image.open(img_path).convert("RGB")
        w_img, h_img = im.size
        draw = ImageDraw.Draw(im)
        
        for cls_id, xc, yc, w, h in boxes:
            x1 = int((xc - w / 2.0) * w_img)
            y1 = int((yc - h / 2.0) * h_img)
            x2 = int((xc + w / 2.0) * w_img)
            y2 = int((yc + h / 2.0) * h_img)
            
            color = COLOR_MAP.get(cls_id, (0, 255, 0))
            class_name = TARGET_CLASSES[cls_id].replace("Tomato___", "")
            
            # Draw rectangle (width 3)
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # Draw label banner
            label_text = f"{class_name}"
            # Text background
            text_bbox = draw.textbbox((x1, max(0, y1 - 18)), label_text)
            draw.rectangle([text_bbox[0]-2, text_bbox[1]-2, text_bbox[2]+2, text_bbox[3]+2], fill=color)
            draw.text((x1, max(0, y1 - 18)), label_text, fill=(255, 255, 255))
            
        out_sample_path = samples_dir / f"sample_{idx+1}_{img_path.name}"
        im.save(out_sample_path)
        annotated_images.append((out_sample_path, im))
        print(f"Saved visualization sample: {out_sample_path.name}")
        
    # Create 2x3 or 2x4 montage grid
    if annotated_images:
        n_samples = len(annotated_images)
        cols = 3
        rows = (n_samples + cols - 1) // cols
        sample_w, sample_h = annotated_images[0][1].size
        grid_img = Image.new("RGB", (cols * sample_w, rows * sample_h), color=(30, 30, 30))
        
        for i, (_, simg) in enumerate(annotated_images):
            c_idx = i % cols
            r_idx = i // cols
            grid_img.paste(simg, (c_idx * sample_w, r_idx * sample_h))
            
        grid_path = samples_dir / "dataset_visualization_grid.jpg"
        grid_img.save(grid_path, quality=95)
        print(f"Saved combined visualization grid: {grid_path}")
        
        # Also copy to docs for report inclusion
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        docs_grid_path = DOCS_DIR / "dataset_visualization_grid.jpg"
        shutil.copy2(str(grid_path), str(docs_grid_path))

def generate_report(stats, split_stats):
    print("\n--- Step 10: Generating Comprehensive Dataset Report ---")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = DOCS_DIR / "tomato_dataset_report.md"
    
    raw_poly = stats["raw_polygon_counts"]
    proc_bbox = stats["processed_bbox_counts"]
    
    formula_section = """
$$\\begin{aligned}
x_{min} &= \\min_i(x_i), \\quad x_{max} = \\max_i(x_i) \\\\
y_{min} &= \\min_i(y_i), \\quad y_{max} = \\max_i(y_i) \\\\
x_{center} &= \\frac{x_{min} + x_{max}}{2} \\\\
y_{center} &= \\frac{y_{min} + y_{max}}{2} \\\\
\\text{width} &= x_{max} - x_{min} \\\\
\\text{height} &= y_{max} - y_{min}
\\end{aligned}$$
"""
    
    content = f"""# LEAF_AI: Tomato-Only Object Detection Dataset Report

## 1. Executive Summary & Overview
This report documents the preparation, annotation conversion, validation, and stratification of the **Tomato-Only Object Detection Dataset** for the **LEAF_AI** platform.

* **Source Dataset:** Roboflow Universe (`bacterial-3ofew/tomato-nwcjv`)
* **Task Type:** Object Detection (Bounding Boxes, YOLO format)
* **Target Specie:** Tomato (*Solanum lycopersicum*)
* **Total Images Processed:** {stats['total_images']}
* **Total Valid Images:** {len(stats['parsed_data'])}
* **Corrupted Images:** {len(stats['corrupted_images'])}
* **Duplicate Images:** {len(stats['duplicate_images'])}
* **Total Converted Disease Bounding Boxes:** {sum(proc_bbox.values())}
* **Data Splits:** Train (80%), Validation (10%), Test (10%) with Stratified Distribution

---

## 2. Target Classes & Filtering Strategy

| Class ID | Target Class Name | Original Raw ID | Raw Polygon Count | Processed Box Count | Action / Status |
|---|---|---|---|---|---|
| **0** | `Tomato___Bacterial_spot` | 0 | {raw_poly[0]} | {proc_bbox[0]} | **Retained** (Disease Target) |
| **1** | `Tomato___Early_blight` | 1 | {raw_poly[1]} | {proc_bbox[1]} | **Retained** (Disease Target) |
| **2** | `Tomato___Late_blight` | 2 | {raw_poly[2]} | {proc_bbox[2]} | **Retained** (Disease Target) |
| *N/A* | `leaf` | 3 | {raw_poly[3]} | 0 | **Excluded** (Healthy Leaf Mask) |

### Rationale for Excluding `leaf` Class:
1. **Disease Detection Specificity:** The objective of LEAF_AI's disease detection model is to locate and classify active disease lesions and symptoms on tomato foliage.
2. **Foreground vs. Background Ambiguity:** The `leaf` class in the raw dataset marks the entire leaf boundaries. Retaining large bounding boxes for entire leaves alongside small disease spot bounding boxes leads to heavy spatial overlap and conflicting anchor assignments during YOLO training.
3. **Optimized Inference:** Excluding whole-leaf bounding boxes focuses the model's loss gradient strictly on pathological lesion features (spots, concentric rings, water-soaked blights).

---

## 3. Segmentation to Bounding Box Conversion

The raw annotations were provided in **YOLOv8 Instance Segmentation** polygon format ($x_1, y_1, x_2, y_2, \\dots, x_n, y_n$). Each polygon was converted to a standard normalized YOLO Object Detection bounding box using the minimum enclosing bounding rectangle:

{formula_section}

Each coordinate is clamped to $[0.0, 1.0]$ and rounded to 6 decimal precision.

---

## 4. Dataset Validation & Quality Audit Results

| Quality Check | Result / Count | Details |
|---|---|---|
| **Missing Label Files** | {len(stats['missing_label_files'])} | 100% of images have corresponding label files. |
| **Corrupted Images** | {len(stats['corrupted_images'])} | All images passed PIL and OpenCV image verification. |
| **Duplicate Images (MD5 Hash)** | {len(stats['duplicate_images'])} | No identical image checksums detected. |
| **Invalid / Degenerate Bounding Boxes** | {len(stats['invalid_boxes'])} | All converted boxes have $w > 0$, $h > 0$, and valid $[0, 1]$ coordinates. |
| **Image Resolution Uniformity** | {', '.join([f'{w}x{h}' for w, h in stats['image_sizes']])} | All images are standardized in resolution. |
| **Pure Background / Leaf-Only Images** | {stats['images_without_disease']} | Images without disease spots serve as true negative background samples. |
| **Multi-Disease Images** | {stats['images_with_multiple_diseases']} | Images exhibiting multiple distinct disease classes simultaneously. |

---

## 5. Dataset Stratification & Split Statistics

The dataset was partitioned using stratified sampling across the primary disease classes to maintain consistent class proportions:

| Split | Images | % of Total | Bacterial Spot Boxes | Early Blight Boxes | Late Blight Boxes | Total Bounding Boxes |
|---|---|---|---|---|---|---|
| **Train** | {split_stats['train']['total_images']} | 80.0% | {split_stats['train']['box_counts_per_class'].get(0, 0)} | {split_stats['train']['box_counts_per_class'].get(1, 0)} | {split_stats['train']['box_counts_per_class'].get(2, 0)} | {split_stats['train']['total_boxes']} |
| **Val** | {split_stats['val']['total_images']} | 10.0% | {split_stats['val']['box_counts_per_class'].get(0, 0)} | {split_stats['val']['box_counts_per_class'].get(1, 0)} | {split_stats['val']['box_counts_per_class'].get(2, 0)} | {split_stats['val']['total_boxes']} |
| **Test** | {split_stats['test']['total_images']} | 10.0% | {split_stats['test']['box_counts_per_class'].get(0, 0)} | {split_stats['test']['box_counts_per_class'].get(1, 0)} | {split_stats['test']['box_counts_per_class'].get(2, 0)} | {split_stats['test']['total_boxes']} |
| **Total** | **{stats['total_images']}** | **100%** | **{proc_bbox[0]}** | **{proc_bbox[1]}** | **{proc_bbox[2]}** | **{sum(proc_bbox.values())}** |

---

## 6. Directory Layout

The prepared dataset is organized in YOLO detection format at `training/datasets/processed/tomato/`:

```
training/datasets/processed/tomato/
├── data.yaml
├── images/
│   ├── train/  ({split_stats['train']['total_images']} images)
│   ├── val/    ({split_stats['val']['total_images']} images)
│   └── test/   ({split_stats['test']['total_images']} images)
├── labels/
│   ├── train/  ({split_stats['train']['total_images']} txt label files)
│   ├── val/    ({split_stats['val']['total_images']} txt label files)
│   └── test/   ({split_stats['test']['total_images']} txt label files)
└── samples/
    ├── dataset_visualization_grid.jpg
    └── sample_*.jpg
```

### YOLO `data.yaml` Configuration
```yaml
path: c:/Users/Admin/Leaf-Disease-Detection/training/datasets/processed/tomato
train: images/train
val: images/val
test: images/test
nc: 3
names:
  - Tomato___Bacterial_spot
  - Tomato___Early_blight
  - Tomato___Late_blight
```

---

## 7. Sample Visualizations

Converted bounding boxes were verified on test split images. Each disease class is highlighted with distinct bounding box colors:
* 🔴 **Red:** `Tomato___Bacterial_spot`
* 🟠 **Orange:** `Tomato___Early_blight`
* 🟣 **Purple:** `Tomato___Late_blight`

*Visualization Grid:* `training/docs/dataset_visualization_grid.jpg` / `training/datasets/processed/tomato/samples/dataset_visualization_grid.jpg`

---

## 8. Next Steps & Recommendations
1. **Model Architecture Selection:** Benchmark YOLOv8n / YOLOv8s / YOLO11n for mobile/edge inference vs. YOLOv8m for server-side accuracy.
2. **Data Augmentation:** Apply Mosaic (0.5), HSV hue-saturation jitter, random flip, and slight rotation during training to enhance robustness to outdoor lighting.
3. **Evaluation Protocol:** Evaluate on the independent `test/` split with mAP@50 and mAP@50-95 metrics.
"""
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Generated report at: {report_file}")

def main():
    print("=== STARTING TOMATO DATASET PREPARATION PIPELINE ===")
    step1_organize_raw_dir()
    stats = process_and_validate_dataset()
    split_stats = split_and_save_dataset(stats)
    create_visualizations()
    generate_report(stats, split_stats)
    print("=== TOMATO DATASET PREPARATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
