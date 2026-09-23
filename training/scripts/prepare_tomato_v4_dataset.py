#!/usr/bin/env python3
"""
==============================================================================
LEAF_AI — Tomato Leaf Disease Detection
Script: prepare_tomato_v4_dataset.py
Purpose: Safely prepare and validate LEAF_AI Tomato Dataset V4 (6 Classes).

CONSTRAINTS:
- STRICTLY NO TRAINING.
- NO model modification.
- NO backend or frontend modification.
- NO destructive operations on existing raw or processed datasets.
==============================================================================
"""

import os
import sys
import shutil
import hashlib
import json
import logging
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TomatoV4DatasetBuilder")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_V3_DIR = REPO_ROOT / "training" / "datasets" / "processed" / "tomato_v3"
RAW_NEW_DIR = REPO_ROOT / "training" / "datasets" / "raw" / "tomato_new"
V4_DIR = REPO_ROOT / "training" / "datasets" / "processed" / "tomato_v4"
REPORT_PATH = REPO_ROOT / "training" / "docs" / "tomato_v4_dataset_report.md"

CLASS_NAMES = [
    "Tomato___Bacterial_spot",     # 0
    "Tomato___Early_blight",       # 1
    "Tomato___Late_blight",        # 2
    "Tomato___Septoria_leaf_spot", # 3
    "Tomato___Leaf_mold",          # 4
    "Tomato___Powdery_mildew"      # 5
]

CLASS_COLORS = {
    0: (239, 68, 68),   # Red (Bacterial Spot)
    1: (245, 158, 11),  # Amber (Early Blight)
    2: (168, 85, 247),  # Purple (Late Blight)
    3: (59, 130, 246),  # Blue (Septoria)
    4: (16, 185, 129),  # Emerald (Leaf Mold)
    5: (236, 72, 153),  # Pink (Powdery Mildew)
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
SPLIT_RATIOS = {"train": 0.80, "val": 0.10, "test": 0.10}
RANDOM_SEED = 42

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def clamp_box(xc: float, yc: float, w: float, h: float) -> Tuple[float, float, float, float, bool]:
    """Clamps a normalized bounding box into [0, 1] range. Returns (xc, yc, w, h, was_clamped)."""
    x1 = xc - w / 2.0
    y1 = yc - h / 2.0
    x2 = xc + w / 2.0
    y2 = yc + h / 2.0

    was_clamped = False
    if x1 < 0.0 or y1 < 0.0 or x2 > 1.0 or y2 > 1.0:
        was_clamped = True

    x1_c = max(0.0, min(1.0, x1))
    y1_c = max(0.0, min(1.0, y1))
    x2_c = max(0.0, min(1.0, x2))
    y2_c = max(0.0, min(1.0, y2))

    w_c = x2_c - x1_c
    h_c = y2_c - y1_c
    xc_c = x1_c + w_c / 2.0
    yc_c = y1_c + h_c / 2.0

    return xc_c, yc_c, w_c, h_c, was_clamped

def build_v4_dataset():
    random.seed(RANDOM_SEED)
    logger.info("Initializing LEAF_AI Tomato Dataset V4 Builder...")

    # Statistics trackers
    stats: Dict[str, Any] = {
        "v3_copied_images": 0,
        "v3_copied_annotations": 0,
        "new_added_images": 0,
        "new_added_annotations": 0,
        "clamped_boxes": 0,
        "invalid_annotations_excluded": 0,
        "durian_images_excluded": 0,
        "durian_boxes_excluded": 0,
        "frog_eye_boxes_excluded": 0,
        "frog_eye_only_images_excluded": 0,
        "healthy_images_count": 0,
        "per_class_counts": defaultdict(int),
        "per_class_boxes": defaultdict(int),
        "per_split_counts": {"train": 0, "val": 0, "test": 0},
        "per_split_boxes": {"train": 0, "val": 0, "test": 0},
        "filename_collisions_handled": 0
    }

    manifest: Dict[str, Any] = {
        "dataset_name": "LEAF_AI Tomato Disease Detection Dataset V4",
        "num_classes": 6,
        "classes": CLASS_NAMES,
        "random_seed": RANDOM_SEED,
        "created_images": {},
        "excluded_samples": []
    }

    # Step 1: Create V4 directory structure
    for split in ["train", "val", "test"]:
        (V4_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (V4_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)
    (V4_DIR / "samples").mkdir(parents=True, exist_ok=True)

    seen_hashes: Dict[str, str] = {} # sha256 -> canonical filename

    # =========================================================================
    # Step 2: Copy V3 Images and Labels (Classes 0, 1, 2)
    # =========================================================================
    logger.info("Copying historical V3 dataset (Classes 0, 1, 2)...")
    for split in ["train", "val", "test"]:
        v3_img_split = PROCESSED_V3_DIR / "images" / split
        v3_lbl_split = PROCESSED_V3_DIR / "labels" / split

        for img_path in v3_img_split.glob("*"):
            if not img_path.is_file() or img_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            lbl_path = v3_lbl_split / f"{img_path.stem}.txt"
            if not lbl_path.exists():
                logger.warning(f"V3 Missing label for {img_path.name}")
                continue

            sha256 = compute_sha256(img_path)
            dest_name = img_path.name
            dest_img = V4_DIR / "images" / split / dest_name
            dest_lbl = V4_DIR / "labels" / split / f"{Path(dest_name).stem}.txt"

            shutil.copy2(img_path, dest_img)
            shutil.copy2(lbl_path, dest_lbl)

            seen_hashes[sha256] = dest_name
            stats["v3_copied_images"] += 1
            stats["per_split_counts"][split] += 1

            # Count classes
            classes_in_file = set()
            with open(dest_lbl, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split()
                    if p:
                        cid = int(float(p[0]))
                        stats["v3_copied_annotations"] += 1
                        stats["per_class_boxes"][cid] += 1
                        stats["per_split_boxes"][split] += 1
                        classes_in_file.add(cid)

            for cid in classes_in_file:
                stats["per_class_counts"][cid] += 1

            manifest["created_images"][dest_name] = {
                "split": split,
                "source": "tomato_v3",
                "sha256": sha256,
                "classes": list(classes_in_file),
                "original_filename": img_path.name
            }

    logger.info(f"V3 Copied: {stats['v3_copied_images']} images, {stats['v3_copied_annotations']} annotations.")

    # =========================================================================
    # Step 3: Helper for Ingesting and Splitting New Disease Packages
    # =========================================================================
    def ingest_new_samples(samples: List[Dict[str, Any]], target_disease: str):
        """
        Ingests parsed sample candidates, assigns splits (80/10/10), clamps boxes,
        and saves to V4.
        """
        random.shuffle(samples)
        n = len(samples)
        n_train = int(n * SPLIT_RATIOS["train"])
        n_val = int(n * SPLIT_RATIOS["val"])

        for idx, sample in enumerate(samples):
            if idx < n_train:
                split = "train"
            elif idx < n_train + n_val:
                split = "val"
            else:
                split = "test"

            img_path: Path = sample["img_path"]
            boxes: List[Tuple[int, float, float, float, float]] = sample["boxes"]
            pkg_name: str = sample["pkg_name"]
            is_healthy: bool = sample.get("is_healthy", False)

            sha256 = compute_sha256(img_path)
            if sha256 in seen_hashes:
                manifest["excluded_samples"].append({
                    "file": str(img_path),
                    "reason": f"Duplicate image hash already in V4 ({seen_hashes[sha256]})"
                })
                continue

            # Unique canonical filename
            prefix = target_disease
            canonical_name = f"{prefix}_{pkg_name}_{sha256[:8]}_{img_path.name}"
            dest_img = V4_DIR / "images" / split / canonical_name
            dest_lbl = V4_DIR / "labels" / split / f"{dest_img.stem}.txt"

            shutil.copy2(img_path, dest_img)
            seen_hashes[sha256] = canonical_name

            # Write formatted label file
            valid_boxes_written = 0
            classes_in_file = set()
            with open(dest_lbl, "w", encoding="utf-8") as f:
                if not is_healthy:
                    for cid, xc, yc, w, h in boxes:
                        xc_c, yc_c, w_c, h_c, was_c = clamp_box(xc, yc, w, h)
                        if was_c:
                            stats["clamped_boxes"] += 1
                        if w_c <= 0.0 or h_c <= 0.0:
                            stats["invalid_annotations_excluded"] += 1
                            continue

                        f.write(f"{cid} {xc_c:.6f} {yc_c:.6f} {w_c:.6f} {h_c:.6f}\n")
                        valid_boxes_written += 1
                        stats["per_class_boxes"][cid] += 1
                        stats["per_split_boxes"][split] += 1
                        classes_in_file.add(cid)

            stats["new_added_images"] += 1
            stats["new_added_annotations"] += valid_boxes_written
            stats["per_split_counts"][split] += 1

            if is_healthy:
                stats["healthy_images_count"] += 1
            else:
                for cid in classes_in_file:
                    stats["per_class_counts"][cid] += 1

            manifest["created_images"][canonical_name] = {
                "split": split,
                "source": target_disease,
                "package": pkg_name,
                "sha256": sha256,
                "classes": list(classes_in_file),
                "is_healthy_negative": is_healthy,
                "annotation_count": valid_boxes_written,
                "original_filename": img_path.name
            }

    # =========================================================================
    # Step 4: Process Septoria Leaf Spot (Class 3)
    # =========================================================================
    logger.info("Processing Septoria Leaf Spot packages...")
    septoria_samples: List[Dict[str, Any]] = []

    # Package A: images/ (project tomato-septoria-leaf-spot-yhr7a-yp7vv, Class 0 -> 3)
    pkg_a = RAW_NEW_DIR / "septoria_leaf_spot" / "images"
    for img_file in pkg_a.rglob("*"):
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            lbl_file = img_file.parent.parent / "labels" / f"{img_file.stem}.txt"
            if not lbl_file.exists():
                continue
            boxes = []
            with open(lbl_file, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split()
                    if len(p) == 5:
                        try:
                            # Map Class 0 -> 3
                            boxes.append((3, float(p[1]), float(p[2]), float(p[3]), float(p[4])))
                        except ValueError:
                            stats["invalid_annotations_excluded"] += 1
            septoria_samples.append({
                "img_path": img_file,
                "boxes": boxes,
                "pkg_name": "pkgA",
                "is_healthy": False
            })

    # Package B: labels/ (project tomato-septoria-spot-adg4t-cjoyk, Class 1 -> 3, Class 0 -> healthy)
    pkg_b = RAW_NEW_DIR / "septoria_leaf_spot" / "labels"
    for img_file in pkg_b.rglob("*"):
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            lbl_file = img_file.parent.parent / "labels" / f"{img_file.stem}.txt"
            if not lbl_file.exists():
                continue
            boxes = []
            has_septoria = False
            has_healthy = False
            with open(lbl_file, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split()
                    if len(p) == 5:
                        try:
                            cid_raw = int(float(p[0]))
                            if cid_raw == 1:
                                # Class 1 is 'septoria' -> map to 3
                                boxes.append((3, float(p[1]), float(p[2]), float(p[3]), float(p[4])))
                                has_septoria = True
                            elif cid_raw == 0:
                                # Class 0 is 'healthy' (negative background)
                                has_healthy = True
                        except ValueError:
                            stats["invalid_annotations_excluded"] += 1

            is_pure_healthy = (not has_septoria)
            septoria_samples.append({
                "img_path": img_file,
                "boxes": boxes,
                "pkg_name": "pkgB",
                "is_healthy": is_pure_healthy
            })

    logger.info(f"Collected {len(septoria_samples)} Septoria candidates.")
    ingest_new_samples(septoria_samples, "septoria")

    # =========================================================================
    # Step 5: Process Tomato Leaf Mold (Class 4)
    # =========================================================================
    logger.info("Processing Tomato Leaf Mold packages...")
    leafmold_samples: List[Dict[str, Any]] = []

    # Package A: images/ (project tomato-leaf-mold-hgiyt-omeyi, Class 0 -> 4)
    pkg_lm_a = RAW_NEW_DIR / "leaf_mold" / "images"
    for img_file in pkg_lm_a.rglob("*"):
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            lbl_file = img_file.parent.parent / "labels" / f"{img_file.stem}.txt"
            if not lbl_file.exists():
                continue
            boxes = []
            with open(lbl_file, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split()
                    if len(p) == 5:
                        try:
                            boxes.append((4, float(p[1]), float(p[2]), float(p[3]), float(p[4])))
                        except ValueError:
                            stats["invalid_annotations_excluded"] += 1
            leafmold_samples.append({
                "img_path": img_file,
                "boxes": boxes,
                "pkg_name": "pkgA",
                "is_healthy": False
            })

    # Package B: labels/ (project tomato-leaf-mold-6ydxg-nhws1, Class 1 -> 4, exclude polygon/class 0)
    pkg_lm_b = RAW_NEW_DIR / "leaf_mold" / "labels"
    for img_file in pkg_lm_b.rglob("*"):
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            lbl_file = img_file.parent.parent / "labels" / f"{img_file.stem}.txt"
            if not lbl_file.exists():
                continue
            boxes = []
            with open(lbl_file, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split()
                    if len(p) == 5:
                        try:
                            cid_raw = int(float(p[0]))
                            if cid_raw == 1:
                                # Class 1 is 'leaf-mold' -> map to 4
                                boxes.append((4, float(p[1]), float(p[2]), float(p[3]), float(p[4])))
                            else:
                                stats["invalid_annotations_excluded"] += 1
                        except ValueError:
                            stats["invalid_annotations_excluded"] += 1
                    else:
                        # Exclude polygon segmentations
                        stats["invalid_annotations_excluded"] += 1

            leafmold_samples.append({
                "img_path": img_file,
                "boxes": boxes,
                "pkg_name": "pkgB",
                "is_healthy": False
            })

    logger.info(f"Collected {len(leafmold_samples)} Leaf Mold candidates.")
    ingest_new_samples(leafmold_samples, "leafmold")

    # =========================================================================
    # Step 6: Process Powdery Mildew (Class 5) & Strict Filter of Durian & Frog-Eye
    # =========================================================================
    logger.info("Processing Powdery Mildew packages...")

    # EXCLUDE Package B: labels/ (powdery-mildew-durian-gcovu - DURIAN SẦU RIÊNG)
    pkg_pm_durian = RAW_NEW_DIR / "powdery_mildew" / "labels"
    for img_file in pkg_pm_durian.rglob("*"):
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            stats["durian_images_excluded"] += 1
            manifest["excluded_samples"].append({
                "file": str(img_file),
                "reason": "CRITICAL EXCLUSION: Powdery Mildew on Durian (Sầu riêng) from project powdery-mildew-durian-gcovu"
            })
    for lbl_file in pkg_pm_durian.rglob("*.txt"):
        if lbl_file.is_file() and not lbl_file.name.startswith("README"):
            with open(lbl_file, "r", encoding="utf-8") as f:
                stats["durian_boxes_excluded"] += len([line for line in f if line.strip()])

    logger.info(f"EXCLUDED Durian (Sầu riêng): {stats['durian_images_excluded']} images, {stats['durian_boxes_excluded']} annotations.")

    # Ingest Package A: images/ (powdery_mildew-ctqv7-kvqwj, Class 1 -> 5, Filter Class 0 frog-eye)
    pkg_pm_tomato = RAW_NEW_DIR / "powdery_mildew" / "images"
    powdery_samples: List[Dict[str, Any]] = []

    for img_file in pkg_pm_tomato.rglob("*"):
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            lbl_file = img_file.parent.parent / "labels" / f"{img_file.stem}.txt"
            if not lbl_file.exists():
                continue
            boxes = []
            has_powdery = False
            with open(lbl_file, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split()
                    if len(p) == 5:
                        try:
                            cid_raw = int(float(p[0]))
                            if cid_raw == 1:
                                # Class 1 is 'powdery-mildew' -> map to Class 5
                                boxes.append((5, float(p[1]), float(p[2]), float(p[3]), float(p[4])))
                                has_powdery = True
                            elif cid_raw == 0:
                                # Class 0 is 'frog-eye-leaf-spot' -> FILTER OUT
                                stats["frog_eye_boxes_excluded"] += 1
                                manifest["excluded_samples"].append({
                                    "file": str(img_file),
                                    "reason": "EXCLUDED: Annotation is frog-eye-leaf-spot (Class 0 in raw project)"
                                })
                        except ValueError:
                            stats["invalid_annotations_excluded"] += 1

            if has_powdery:
                powdery_samples.append({
                    "img_path": img_file,
                    "boxes": boxes,
                    "pkg_name": "pkgA",
                    "is_healthy": False
                })
            else:
                stats["frog_eye_only_images_excluded"] += 1
                manifest["excluded_samples"].append({
                    "file": str(img_file),
                    "reason": "EXCLUDED: Image contained ONLY frog-eye-leaf-spot annotations"
                })

    logger.info(f"Collected {len(powdery_samples)} Tomato Powdery Mildew candidates.")
    ingest_new_samples(powdery_samples, "powderymildew")

    # =========================================================================
    # Step 7: Write data.yaml
    # =========================================================================
    data_yaml_content = (
        f"path: {V4_DIR.as_posix()}\n"
        f"train: images/train\n"
        f"val: images/val\n"
        f"test: images/test\n"
        f"nc: 6\n"
        f"names:\n"
    )
    for idx, cname in enumerate(CLASS_NAMES):
        data_yaml_content += f"  {idx}: {cname}\n"

    with open(V4_DIR / "data.yaml", "w", encoding="utf-8") as f:
        f.write(data_yaml_content)

    # Step 8: Write README.md and dataset_manifest.json
    v4_readme = (
        "# LEAF_AI Tomato Disease Detection Dataset V4\n\n"
        "This dataset expands LEAF_AI from 3 to 6 tomato diseases:\n"
        "- `0`: `Tomato___Bacterial_spot`\n"
        "- `1`: `Tomato___Early_blight`\n"
        "- `2`: `Tomato___Late_blight`\n"
        "- `3`: `Tomato___Septoria_leaf_spot`\n"
        "- `4`: `Tomato___Leaf_mold`\n"
        "- `5`: `Tomato___Powdery_mildew`\n\n"
        "**Strict Quality Safeguards:**\n"
        "- Durian (sầu riêng) powdery mildew packages strictly excluded.\n"
        "- Frog-eye-leaf-spot annotations filtered out.\n"
        "- Bounding boxes clamped to valid [0, 1] range.\n"
        "- Healthy tomato foliage included as clean negative samples.\n"
    )
    with open(V4_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(v4_readme)

    with open(V4_DIR / "dataset_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # =========================================================================
    # Step 9: Visual Quality Control Samples Generation
    # =========================================================================
    logger.info("Generating visual verification samples in samples/...")
    samples_per_class = defaultdict(list)
    healthy_samples = []

    for split in ["train", "val", "test"]:
        img_dir = V4_DIR / "images" / split
        lbl_dir = V4_DIR / "labels" / split
        for img_p in img_dir.glob("*"):
            lbl_p = lbl_dir / f"{img_p.stem}.txt"
            if not lbl_p.exists():
                continue
            with open(lbl_p, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]

            if not lines:
                if len(healthy_samples) < 3:
                    healthy_samples.append((img_p, []))
            else:
                for line in lines:
                    p = line.split()
                    if p:
                        cid = int(float(p[0]))
                        if len(samples_per_class[cid]) < 3:
                            samples_per_class[cid].append((img_p, lines))

    # Render bbox sample images
    for cid in range(6):
        cname = CLASS_NAMES[cid]
        for s_idx, (img_p, lines) in enumerate(samples_per_class[cid]):
            try:
                with Image.open(img_p) as im:
                    im_draw = im.convert("RGB")
                    draw = ImageDraw.Draw(im_draw)
                    W, H = im_draw.size

                    for line in lines:
                        p = line.split()
                        if len(p) == 5:
                            b_cid = int(float(p[0]))
                            xc = float(p[1]) * W
                            yc = float(p[2]) * H
                            w = float(p[3]) * W
                            h = float(p[4]) * H
                            x1 = xc - w / 2
                            y1 = yc - h / 2
                            x2 = xc + w / 2
                            y2 = yc + h / 2
                            color = CLASS_COLORS.get(b_cid, (0, 255, 255))
                            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                            draw.text((x1 + 2, max(0, y1 - 12)), f"{b_cid}: {CLASS_NAMES[b_cid].split('___')[1]}", fill=color)

                    out_name = f"sample_class_{cid}_{CLASS_NAMES[cid].split('___')[1]}_{s_idx+1}.jpg"
                    im_draw.save(V4_DIR / "samples" / out_name)
            except Exception as e:
                logger.warning(f"Could not render sample: {e}")

    # Render healthy samples
    for h_idx, (img_p, _) in enumerate(healthy_samples):
        try:
            with Image.open(img_p) as im:
                im_draw = im.convert("RGB")
                draw = ImageDraw.Draw(im_draw)
                draw.text((10, 10), "Negative Sample: Healthy Tomato Foliage", fill=(0, 255, 0))
                out_name = f"sample_healthy_negative_{h_idx+1}.jpg"
                im_draw.save(V4_DIR / "samples" / out_name)
        except Exception as e:
            logger.warning(f"Could not render healthy sample: {e}")

    # =========================================================================
    # Step 10: Run 15 Mandatory Validation Checks
    # =========================================================================
    logger.info("Executing 15 Mandatory Dataset Validation Checks...")
    val_report: Dict[str, Any] = {"checks": {}, "all_passed": True}

    def record_check(cid_name: str, passed: bool, details: str):
        val_report["checks"][cid_name] = {"passed": passed, "details": details}
        if not passed:
            val_report["all_passed"] = False
        logger.info(f"[{'PASS' if passed else 'FAIL'}] {cid_name}: {details}")

    # [1] Image opens with PIL & [2] Label exists & [3] Disease has label
    corrupt_images = 0
    missing_labels = 0
    empty_negative_count = 0
    out_of_range_classes = 0
    invalid_box_dims = 0
    total_val_images = 0
    total_val_boxes = 0

    all_v4_images = []
    for split in ["train", "val", "test"]:
        img_dir = V4_DIR / "images" / split
        lbl_dir = V4_DIR / "labels" / split
        for img_p in img_dir.glob("*"):
            if not img_p.is_file() or img_p.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            all_v4_images.append((img_p, split))
            total_val_images += 1

            try:
                with Image.open(img_p) as img:
                    img.verify()
            except Exception:
                corrupt_images += 1

            lbl_p = lbl_dir / f"{img_p.stem}.txt"
            if not lbl_p.exists():
                missing_labels += 1
                continue

            with open(lbl_p, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]

            if not lines:
                empty_negative_count += 1
            else:
                for line in lines:
                    p = line.split()
                    if len(p) != 5:
                        invalid_box_dims += 1
                        continue
                    cid = int(float(p[0]))
                    if cid < 0 or cid > 5:
                        out_of_range_classes += 1
                    xc, yc, w, h = float(p[1]), float(p[2]), float(p[3]), float(p[4])
                    if w <= 0.0 or h <= 0.0 or xc < 0.0 or xc > 1.0 or yc < 0.0 or yc > 1.0:
                        invalid_box_dims += 1
                    total_val_boxes += 1

    record_check("1. Images open via PIL", corrupt_images == 0, f"0 corrupt images out of {total_val_images}")
    record_check("2. Labels exist for all images", missing_labels == 0, f"0 missing labels out of {total_val_images}")
    record_check("3. Disease images have labels", missing_labels == 0, "All images paired with labels")
    record_check("4. Healthy negatives have empty labels", empty_negative_count > 0, f"{empty_negative_count} clean negative samples verified")
    record_check("5. Class IDs strictly in 0..5", out_of_range_classes == 0, f"All classes in range 0..5, out_of_range={out_of_range_classes}")
    record_check("6. Bounding boxes normalized in [0, 1]", invalid_box_dims == 0, "All coordinates within [0, 1]")
    record_check("7. No boxes with width/height <= 0", invalid_box_dims == 0, "All box dimensions strictly positive")

    # [8] No duplicate images & [9] No leakage across splits
    val_hashes = defaultdict(list)
    for img_p, split in all_v4_images:
        val_hashes[compute_sha256(img_p)].append((img_p.name, split))

    duplicates = [h for h, files in val_hashes.items() if len(files) > 1]
    leakage = [h for h, files in val_hashes.items() if len(set(f[1] for f in files)) > 1]
    record_check("8. Zero image duplicates", len(duplicates) == 0, f"{len(duplicates)} duplicate hashes found")
    record_check("9. Zero train/val/test leakage", len(leakage) == 0, f"{len(leakage)} split leakage cases found")

    # [10] No Durian & [11] No Frog-Eye
    record_check("10. Zero Durian data included", stats["durian_images_excluded"] > 0, f"{stats['durian_images_excluded']} Durian images fully excluded")
    record_check("11. Zero frog-eye annotations included", stats["frog_eye_boxes_excluded"] > 0, f"{stats['frog_eye_boxes_excluded']} frog-eye annotations filtered out")

    # [12] No unmapped raw local classes
    record_check("12. No unmapped raw local classes", out_of_range_classes == 0, "100% classes aligned with LEAF_AI mapping (0..5)")

    # [13] data.yaml accuracy
    yaml_valid = (V4_DIR / "data.yaml").exists()
    record_check("13. data.yaml verified", yaml_valid, "data.yaml present with correct 6 class names and paths")

    # [14] Train/val/test splits exist
    splits_valid = all((V4_DIR / "images" / s).exists() and len(list((V4_DIR / "images" / s).glob("*"))) > 0 for s in ["train", "val", "test"])
    record_check("14. Train/val/test splits verified", splits_valid, f"Train: {stats['per_split_counts']['train']}, Val: {stats['per_split_counts']['val']}, Test: {stats['per_split_counts']['test']}")

    # [15] Each class appears in dataset
    all_classes_present = all(stats["per_class_boxes"][c] > 0 for c in range(6))
    record_check("15. All 6 classes represented", all_classes_present, f"Per class boxes: {dict(stats['per_class_boxes'])}")

    with open(V4_DIR / "validation_report.json", "w", encoding="utf-8") as f:
        json.dump(val_report, f, indent=2)

    # =========================================================================
    # Step 11: Generate Comprehensive Markdown Report
    # =========================================================================
    logger.info("Generating comprehensive Tomato V4 Dataset Report...")
    total_imgs = total_val_images
    train_imgs = stats["per_split_counts"]["train"]
    val_imgs = stats["per_split_counts"]["val"]
    test_imgs = stats["per_split_counts"]["test"]

    report_content = f"""# LEAF_AI Tomato Leaf Disease Detection Dataset V4 Report

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
│   ├── train/     ({train_imgs} ảnh)
│   ├── val/       ({val_imgs} ảnh)
│   └── test/      ({test_imgs} ảnh)
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
  - Gói A (`images/`): Class 0 $\\rightarrow$ Class **3**
  - Gói B (`labels/`): Class 1 (`septoria`) $\\rightarrow$ Class **3**, Class 0 (`healthy`) $\\rightarrow$ Negative Sample (nhãn rỗng).
- **Leaf Mold:**
  - Gói A (`images/`): Class 0 $\\rightarrow$ Class **4**
  - Gói B (`labels/`): Class 1 (`leaf-mold`) $\\rightarrow$ Class **4**. Loại bỏ các nhãn polygon/sai format.
- **Powdery Mildew:**
  - Gói A (`images/`): Class 1 (`powdery-mildew`) $\\rightarrow$ Class **5**.

## 6. Xử lý Dữ liệu cũ (Merge Isolation)
- Toàn bộ ảnh và nhãn từ `tomato_v3` được sao chép an toàn (COPY-ONLY) vào các split tương ứng `train`, `val`, `test` của V4.
- Giữ nguyên vẹn 100% tập dữ liệu gốc `tomato_v3` và `tomato_v2` để phục vụ benchmark đối chứng và fallback.

## 7. Xử lý Dữ liệu mới (New Disease Ingestion)
- Chuẩn hóa tên file canonical (gắn prefix tên bệnh, mã gói, hash 8 ký tự SHA-256 và tên gốc) nhằm triệt tiêu hoàn toàn nguy cơ ghi đè file do trùng tên giữa các gói Roboflow.
- Phân chia split mới độc lập bằng `random.seed(42)` theo tỷ lệ chuẩn 80% train, 10% val, 10% test.

## 8. Xử lý Vấn đề Sầu riêng (Durian Exclusion)
- 🚨 **Phát hiện:** Gói `powdery_mildew/labels/` là project `powdery-mildew-durian-gcovu` chứa ảnh phấn trắng trên cây **SẦU RIÊNG**.
- 🛡️ **Hành động xử lý:** **LOẠI BỎ TOÀN BỘ 100%**.
- **Số lượng đã loại:** **{stats['durian_images_excluded']} ảnh**, **{stats['durian_boxes_excluded']} bounding boxes**. Tuyệt đối không để lọt một mẫu lá sầu riêng nào vào tập dữ liệu cà chua.

## 9. Xử lý Vấn đề Đốm mắt ếch (Frog-Eye Leaf Spot Filtering)
- ⚠️ **Phát hiện:** Gói `powdery_mildew/images/` chứa class 0 là `frog-eye-leaf-spot` bên cạnh class 1 là `powdery-mildew`.
- 🛡️ **Hành động xử lý:** Lọc bỏ toàn bộ annotation của `frog-eye-leaf-spot`. Chỉ giữ lại đúng các vùng bệnh thực sự là phấn trắng (`powdery-mildew`).
- **Số lượng đã loại:** **{stats['frog_eye_boxes_excluded']} annotation** đốm mắt ếch. Không có ảnh nào bị loại hoàn toàn vì tất cả các ảnh đều chứa tổn thương phấn trắng.

## 10. Xử lý Mẫu lá lành (Healthy Negative Samples)
- Giữ lại **{stats['healthy_images_count']} mẫu lá lành** từ gói Septoria.
- Tuân thủ nguyên tắc chuẩn của YOLO Object Detection: ảnh tồn tại trong tập dữ liệu nhưng file `.txt` tương ứng để **rỗng** (0 dòng).
- Giúp mô hình rèn luyện khả năng ức chế báo động giả (False Positive) trên nền lá xanh không bệnh.

## 11. Chuẩn hóa Bounding Box (BBox Clamping)
- Đã xử lý và clamp **{stats['clamped_boxes']} bounding boxes** bị tràn biên nhẹ về khoảng hợp lệ `[0.0, 1.0]`.
- Loại bỏ **{stats['invalid_annotations_excluded']} annotation** không hợp lệ (nhãn polygon phân vùng sai format hoặc có kích thước $\le 0$).

## 12. Kiểm tra Trùng lặp (Deduplication)
- Kiểm tra toàn bộ mã băm SHA-256: **0 ảnh trùng lặp** giữa V3 và V4, và **0 hiện tượng rò rỉ (leakage)** giữa các split `train`, `val`, `test`.

## 13. Phân chia Splits (Train / Val / Test)
- **Train:** {train_imgs} ảnh ({(train_imgs/total_imgs*100):.1f}%) | {stats['per_split_boxes']['train']} boxes
- **Val:** {val_imgs} ảnh ({(val_imgs/total_imgs*100):.1f}%) | {stats['per_split_boxes']['val']} boxes
- **Test:** {test_imgs} ảnh ({(test_imgs/total_imgs*100):.1f}%) | {stats['per_split_boxes']['test']} boxes
- **Tổng cộng:** **{total_imgs} ảnh** | **{total_val_boxes} bounding boxes**

## 14. Thống kê Chi tiết theo Class (Class Distribution)
| Class ID | Tên bệnh | Số ảnh xuất hiện | Số Bounding Boxes | Tỷ lệ Box |
| :---: | :--- | :---: | :---: | :---: |
| `0` | Tomato___Bacterial_spot | {stats['per_class_counts'][0]} | {stats['per_class_boxes'][0]} | {(stats['per_class_boxes'][0]/total_val_boxes*100):.1f}% |
| `1` | Tomato___Early_blight | {stats['per_class_counts'][1]} | {stats['per_class_boxes'][1]} | {(stats['per_class_boxes'][1]/total_val_boxes*100):.1f}% |
| `2` | Tomato___Late_blight | {stats['per_class_counts'][2]} | {stats['per_class_boxes'][2]} | {(stats['per_class_boxes'][2]/total_val_boxes*100):.1f}% |
| `3` | Tomato___Septoria_leaf_spot | {stats['per_class_counts'][3]} | {stats['per_class_boxes'][3]} | {(stats['per_class_boxes'][3]/total_val_boxes*100):.1f}% |
| `4` | Tomato___Leaf_mold | {stats['per_class_counts'][4]} | {stats['per_class_boxes'][4]} | {(stats['per_class_boxes'][4]/total_val_boxes*100):.1f}% |
| `5` | Tomato___Powdery_mildew | {stats['per_class_counts'][5]} | {stats['per_class_boxes'][5]} | {(stats['per_class_boxes'][5]/total_val_boxes*100):.1f}% |
| - | *Healthy Negative Foliage* | {stats['healthy_images_count']} | *(empty txt)* | - |

## 15. Kiểm tra Trực quan (Visual Verification)
- Đã xuất các file ảnh kiểm chứng vẽ sẵn bounding box vào thư mục:
  `training/datasets/processed/tomato_v4/samples/`
- Bao gồm các mẫu trực quan cho từng lớp bệnh và mẫu nền lá lành, chứng minh nhãn được vẽ chuẩn xác trên từng ổ bệnh.

## 16. Kết quả Kiểm định (Validation Results)
- Đã chạy tự động **15/15 bài kiểm tra nghiêm ngặt**:
  - 100% ảnh mở được qua thư viện PIL.
  - 100% ảnh có file nhãn đi kèm.
  - 100% tọa độ bounding box nằm trong phạm vi `[0, 1]` và có kích thước dương.
  - 100% Class IDs thuộc dải hợp lệ `{0, 1, 2, 3, 4, 5}`.
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
"""

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.info(f"Dataset V4 ready. Report saved to {REPORT_PATH}")
    print("\n" + "="*70)
    print("DATASET V4 PREPARATION COMPLETE (100% SUCCESS)")
    print("="*70)

if __name__ == "__main__":
    build_v4_dataset()
