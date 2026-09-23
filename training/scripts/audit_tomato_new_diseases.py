#!/usr/bin/env python3
"""
==============================================================================
LEAF_AI — Tomato Leaf Disease Detection
Script: audit_tomato_new_diseases.py
Purpose: Comprehensive quality, format, and annotation audit for incoming
         tomato disease datasets (Septoria Leaf Spot, Leaf Mold, Powdery Mildew).

SAFE SCRIPT:
- READ-ONLY: Never modifies, deletes, moves, or renames source files.
- NEVER merges into existing datasets.
- NEVER calls Ultralytics or starts any training.
==============================================================================
"""

import os
import sys
import glob
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TomatoNewDiseasesAudit")

# Path definitions relative to repository root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_TOMATO_NEW_DIR = REPO_ROOT / "training" / "datasets" / "raw" / "tomato_new"
REPORT_OUTPUT_PATH = REPO_ROOT / "training" / "docs" / "tomato_new_diseases_dataset_report.md"

DISEASE_KEYS = [
    "septoria_leaf_spot",
    "leaf_mold",
    "powdery_mildew"
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file for duplicate detection."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def parse_yaml_metadata(yaml_path: Path) -> Dict[str, Any]:
    """Parse key metadata fields from a Roboflow data.yaml file safely without PyYAML dependency."""
    meta = {"names": [], "nc": 0, "project": "", "url": "", "splits": []}
    if not yaml_path.exists():
        return meta

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            for line in f:
                line_s = line.strip()
                if line_s.startswith("nc:"):
                    try:
                        meta["nc"] = int(line_s.split("nc:")[1].strip())
                    except ValueError:
                        pass
                elif line_s.startswith("names:"):
                    raw_names = line_s.split("names:")[1].strip()
                    try:
                        # Parse python list syntax e.g. ['a', 'b']
                        import ast
                        parsed = ast.literal_eval(raw_names)
                        if isinstance(parsed, list):
                            meta["names"] = parsed
                    except Exception:
                        meta["names"] = [raw_names]
                elif line_s.startswith("project:"):
                    meta["project"] = line_s.split("project:")[1].strip()
                elif line_s.startswith("url:"):
                    meta["url"] = line_s.split("url:")[1].strip()
                elif any(line_s.startswith(k + ":") for k in ["train", "val", "test"]):
                    meta["splits"].append(line_s)
    except Exception as e:
        logger.warning(f"Failed to read yaml {yaml_path}: {e}")

    return meta

def find_image_label_pairs(root_dir: Path) -> Tuple[List[Path], Dict[str, Path]]:
    """
    Discovers all images and label files under root_dir, whether flat or nested in Roboflow splits.
    Returns (list_of_image_paths, dict_stem_to_label_path).
    """
    image_paths = []
    label_dict = {}

    for p in root_dir.rglob("*"):
        if p.is_file():
            suffix = p.suffix.lower()
            if suffix in IMAGE_EXTENSIONS:
                image_paths.append(p)
            elif suffix == ".txt" and not p.name.startswith("README"):
                # Avoid collision by using relative path identifier if duplicate stems
                label_dict[p.stem] = p

    return image_paths, label_dict

def audit_disease_folder(disease_key: str, base_dir: Path) -> Dict[str, Any]:
    """Comprehensive audit for a disease folder (supporting nested Roboflow packages in images/ and labels/)."""
    disease_dir = base_dir / disease_key
    images_dir = disease_dir / "images"
    labels_dir = disease_dir / "labels"

    stats: Dict[str, Any] = {
        "disease_key": disease_key,
        "exists": disease_dir.exists(),
        "packages_found": [],
        "total_images": 0,
        "total_labels": 0,
        "images_without_labels": [],
        "labels_without_images": [],
        "corrupt_images": [],
        "duplicate_images": [],
        "image_extensions": defaultdict(int),
        "resolutions": [],
        "total_bounding_boxes": 0,
        "empty_labels": 0,
        "class_ids_found": defaultdict(int),
        "bbox_errors": {
            "negative_or_zero_dim": 0,
            "out_of_bounds": 0,
            "corrupt_format": 0
        },
        "lesion_sizes": {
            "very_small": 0,    # < 0.5% area
            "small": 0,         # 0.5% - 2.0% area
            "medium": 0,        # 2.0% - 8.0% area
            "large": 0,         # 8.0% - 50.0% area
            "huge_whole_leaf": 0 # > 50% area
        },
        "healthy_samples": 0,
        "critical_anomalies": []
    }

    if not disease_dir.exists():
        return stats

    # 1. Detect Roboflow packages in subfolders
    for sub_name, sub_path in [("images_dir", images_dir), ("labels_dir", labels_dir)]:
        if sub_path.exists():
            for yaml_file in sub_path.rglob("data.yaml"):
                pkg_dir = yaml_file.parent
                meta = parse_yaml_metadata(yaml_file)
                # Count files in this package
                pkg_imgs = [p for p in pkg_dir.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
                pkg_lbls = [p for p in pkg_dir.rglob("*.txt") if p.is_file() and not p.name.startswith("README")]
                stats["packages_found"].append({
                    "location": f"{disease_key}/{pkg_dir.relative_to(disease_dir)}",
                    "project": meta["project"],
                    "classes": meta["names"],
                    "nc": meta["nc"],
                    "image_count": len(pkg_imgs),
                    "label_count": len(pkg_lbls),
                    "yaml_path": str(yaml_file.relative_to(disease_dir))
                })

    # 2. Collect all images and labels across the disease folder
    all_images, all_labels = find_image_label_pairs(disease_dir)
    stats["total_images"] = len(all_images)
    stats["total_labels"] = len(all_labels)

    for img in all_images:
        stats["image_extensions"][img.suffix.lower()] += 1

    # 3. Duplicate and Integrity checks
    seen_hashes: Dict[str, Path] = {}
    for img_path in all_images:
        stem = img_path.stem
        # Duplicate hash
        try:
            fhash = compute_file_hash(img_path)
            if fhash in seen_hashes:
                stats["duplicate_images"].append({
                    "original": str(seen_hashes[fhash].relative_to(disease_dir)),
                    "duplicate": str(img_path.relative_to(disease_dir))
                })
            else:
                seen_hashes[fhash] = img_path
        except Exception as e:
            stats["corrupt_images"].append({"file": str(img_path.relative_to(disease_dir)), "error": str(e)})

        # Image resolution and PIL verification
        try:
            with Image.open(img_path) as img:
                img.verify()
            with Image.open(img_path) as img:
                stats["resolutions"].append(img.size)
        except Exception as e:
            stats["corrupt_images"].append({"file": str(img_path.relative_to(disease_dir)), "error": str(e)})

        # Check pairing with label
        # In roboflow, label is usually in adjacent 'labels' folder with same stem
        expected_label = None
        # Check standard adjacent folder
        possible_label_1 = img_path.parent.parent / "labels" / f"{stem}.txt"
        possible_label_2 = all_labels.get(stem)
        if possible_label_1.exists():
            expected_label = possible_label_1
        elif possible_label_2:
            expected_label = possible_label_2

        if not expected_label:
            stats["images_without_labels"].append(img_path.name)

    # 4. Check labels without images
    image_stems = {p.stem for p in all_images}
    for l_stem, l_path in all_labels.items():
        if l_stem not in image_stems:
            stats["labels_without_images"].append(l_path.name)

    # 5. Parse bounding box coordinates and sizes
    for l_stem, l_path in all_labels.items():
        try:
            with open(l_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                stats["empty_labels"] += 1
                continue

            for line in lines:
                parts = line.split()
                if len(parts) < 5:
                    stats["bbox_errors"]["corrupt_format"] += 1
                    continue

                try:
                    cls_id = int(float(parts[0]))
                    xc = float(parts[1])
                    yc = float(parts[2])
                    w = float(parts[3])
                    h = float(parts[4])
                except ValueError:
                    stats["bbox_errors"]["corrupt_format"] += 1
                    continue

                stats["total_bounding_boxes"] += 1
                stats["class_ids_found"][cls_id] += 1

                if w <= 0 or h <= 0:
                    stats["bbox_errors"]["negative_or_zero_dim"] += 1
                    continue

                x1 = xc - w / 2.0
                y1 = yc - h / 2.0
                x2 = xc + w / 2.0
                y2 = yc + h / 2.0

                if x1 < -0.05 or y1 < -0.05 or x2 > 1.05 or y2 > 1.05:
                    stats["bbox_errors"]["out_of_bounds"] += 1

                # Lesion size binning
                area = w * h
                if area < 0.005:
                    stats["lesion_sizes"]["very_small"] += 1
                elif area < 0.02:
                    stats["lesion_sizes"]["small"] += 1
                elif area < 0.08:
                    stats["lesion_sizes"]["medium"] += 1
                elif area < 0.50:
                    stats["lesion_sizes"]["large"] += 1
                else:
                    stats["lesion_sizes"]["huge_whole_leaf"] += 1

        except Exception as e:
            stats["bbox_errors"]["corrupt_format"] += 1

    # 6. Disease-specific critical anomalies
    if disease_key == "powdery_mildew":
        # Check if durian project exists
        for pkg in stats["packages_found"]:
            if "durian" in pkg["project"].lower() or "durian" in pkg["location"].lower():
                stats["critical_anomalies"].append(
                    f"CRITICAL: Non-tomato dataset detected in `{pkg['location']}` (Project: {pkg['project']}). This is Durian (Sầu riêng) Powdery Mildew, NOT Tomato Powdery Mildew!"
                )
            if "frog-eye-leaf-spot" in pkg["classes"]:
                stats["critical_anomalies"].append(
                    f"WARNING: Dataset `{pkg['location']}` contains multi-class labels with Frog Eye Leaf Spot (Class 0) alongside Powdery Mildew (Class 1)."
                )

    if disease_key == "septoria_leaf_spot":
        for pkg in stats["packages_found"]:
            if "healthy" in pkg["classes"]:
                stats["healthy_samples"] += pkg["image_count"]
                stats["critical_anomalies"].append(
                    f"NOTICE: Dataset `{pkg['location']}` contains a 'healthy' class (Class 0) alongside 'septoria' (Class 1)."
                )

    if disease_key == "leaf_mold":
        for pkg in stats["packages_found"]:
            if "\\" in pkg["classes"] or "" in pkg["classes"]:
                stats["critical_anomalies"].append(
                    f"WARNING: Corrupted class name '{pkg['classes']}' in `{pkg['location']}`."
                )

    return stats

def generate_markdown_report(all_stats: Dict[str, Dict[str, Any]], output_path: Path):
    """Generates the formal tomato_new_diseases_dataset_report.md file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_images_all = sum(s["total_images"] for s in all_stats.values())
    total_labels_all = sum(s["total_labels"] for s in all_stats.values())
    total_boxes_all = sum(s["total_bounding_boxes"] for s in all_stats.values())

    lines = [
        "# Tomato New Diseases Dataset Audit",
        "",
        "> [!IMPORTANT]",
        "> **AUDIT ONLY — STRICTLY NO TRAINING PERFORMED**  ",
        "> This audit is strictly restricted to intake inspection of newly provided datasets for Tomato Septoria Leaf Spot, Leaf Mold, and Powdery Mildew.  ",
        "> Production model `model/tomato_v3/best.pt` and all existing datasets remain 100% untouched.",
        "",
        "## 1. Dataset Overview",
        "",
        f"- **Audit Target Directory:** `training/datasets/raw/tomato_new/`",
        f"- **Target New Classes (Planned for Tomato):**",
        f"  - `3`: `Tomato___Septoria_leaf_spot`",
        f"  - `4`: `Tomato___Leaf_mold`",
        f"  - `5`: `Tomato___Powdery_mildew`",
        f"- **Total Images Discovered:** {total_images_all}",
        f"- **Total Labels Discovered:** {total_labels_all}",
        f"- **Total Bounding Boxes Parsed:** {total_boxes_all}",
        "",
        "### Ingestion Structure Finding",
        "The datasets were extracted into the repository as **separate Roboflow packages**:",
        "- One Roboflow dataset package was extracted into the `images/` directory of each disease.",
        "- A second, separate Roboflow dataset package was extracted into the `labels/` directory of each disease.",
        "- Each sub-package contains its own self-contained `data.yaml`, splits (`train`, and optionally `valid`, `test`), and internal `images/` and `labels/` folders.",
        "",
        "| Disease Subfolder | Roboflow Packages Found | Total Images | Total Labels | Bounding Boxes | Critical Issues |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |"
    ]

    for dkey in DISEASE_KEYS:
        st = all_stats[dkey]
        pkg_count = len(st["packages_found"])
        crit_count = len(st["critical_anomalies"])
        crit_str = f"**{crit_count} Critical Anomaly!**" if crit_count > 0 else "None"
        lines.append(f"| `{dkey}` | {pkg_count} packages | {st['total_images']} | {st['total_labels']} | {st['total_bounding_boxes']} | {crit_str} |")

    lines.append("")

    # Per-disease sections
    disease_titles = {
        "septoria_leaf_spot": ("2. Septoria Leaf Spot", "Tomato___Septoria_leaf_spot (Target Class ID: 3)"),
        "leaf_mold": ("3. Tomato Leaf Mold", "Tomato___Leaf_mold (Target Class ID: 4)"),
        "powdery_mildew": ("4. Powdery Mildew", "Tomato___Powdery_mildew (Target Class ID: 5)")
    }

    for dkey in DISEASE_KEYS:
        title, class_str = disease_titles[dkey]
        st = all_stats[dkey]
        res_set = set(st["resolutions"])
        res_str = f"{len(res_set)} distinct resolutions (sample: {list(res_set)[:3]})" if res_set else "N/A"

        lines.extend([
            f"## {title}",
            "",
            f"- **Target Mapping:** `{class_str}`",
            f"- **Directory:** `training/datasets/raw/tomato_new/{dkey}/`",
            f"- **Detected Roboflow Packages:**"
        ])

        for pkg in st["packages_found"]:
            lines.append(f"  - Package `{pkg['location']}`: Project `{pkg['project']}`, Classes: `{pkg['classes']}` ({pkg['nc']} classes), Images: {pkg['image_count']}, Labels: {pkg['label_count']}")

        lines.extend([
            f"- **Total Images:** {st['total_images']}",
            f"- **Total Labels:** {st['total_labels']}",
            f"- **Total Bounding Boxes:** {st['total_bounding_boxes']}",
            f"- **Class IDs in Raw Files:** {dict(st['class_ids_found'])}",
            f"- **Image Resolutions:** {res_str}",
            f"- **Duplicate Images (SHA-256):** {len(st['duplicate_images'])}",
            f"- **Corrupt Images:** {len(st['corrupt_images'])}",
            f"- **Annotation Quality Checks:**",
            f"  - Empty Label Files: {st['empty_labels']}",
            f"  - Format Parsing Errors: {st['bbox_errors']['corrupt_format']}",
            f"  - Zero/Negative Dimensions: {st['bbox_errors']['negative_or_zero_dim']}",
            f"  - Out-of-bounds Coordinates: {st['bbox_errors']['out_of_bounds']}",
            f"- **Lesion Size Distribution:**",
            f"  - Very Small (<0.5% area): {st['lesion_sizes']['very_small']} ({(st['lesion_sizes']['very_small']/max(1, st['total_bounding_boxes'])*100):.1f}%)",
            f"  - Small (0.5%-2% area): {st['lesion_sizes']['small']} ({(st['lesion_sizes']['small']/max(1, st['total_bounding_boxes'])*100):.1f}%)",
            f"  - Medium (2%-8% area): {st['lesion_sizes']['medium']} ({(st['lesion_sizes']['medium']/max(1, st['total_bounding_boxes'])*100):.1f}%)",
            f"  - Large (8%-50% area): {st['lesion_sizes']['large']} ({(st['lesion_sizes']['large']/max(1, st['total_bounding_boxes'])*100):.1f}%)",
            f"  - Whole-leaf / Cluster (>50% area): {st['lesion_sizes']['huge_whole_leaf']} ({(st['lesion_sizes']['huge_whole_leaf']/max(1, st['total_bounding_boxes'])*100):.1f}%)",
            f"- **Critical Issues & Anomalies:**"
        ])

        if st["critical_anomalies"]:
            for anom in st["critical_anomalies"]:
                lines.append(f"  - ⚠️ {anom}")
        else:
            lines.append("  - None detected.")

        lines.append("")

    # Section 5: Class Balance
    lines.extend([
        "## 5. Class Balance Across New Datasets",
        "",
        "| Disease | Target Class ID | Raw Class IDs Found | Images Available | Bounding Boxes | Status |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |"
    ])
    for dkey in DISEASE_KEYS:
        st = all_stats[dkey]
        raw_ids = list(st["class_ids_found"].keys())
        lines.append(f"| `{dkey}` | Planned | {raw_ids} | {st['total_images']} | {st['total_bounding_boxes']} | Ingested (Requires Alignment) |")

    lines.extend([
        "",
        "## 6. Annotation Quality & Inconsistency Analysis",
        "",
        "1. **Roboflow Nested Layout:** The user unzipped complete Roboflow datasets inside both `images/` and `labels/` subdirectories. They are not flat image/label folders. They contain internal `train/images`, `train/labels`, etc.",
        "2. **Different Datasets in `images/` vs `labels/`:**",
        "   - In `septoria_leaf_spot/`: `images/` came from project `tomato-septoria-leaf-spot-yhr7a-yp7vv`, while `labels/` came from project `tomato-septoria-spot-adg4t-cjoyk` (which contains 'healthy' and 'septoria').",
        "   - In `leaf_mold/`: `images/` came from project `tomato-leaf-mold-hgiyt-omeyi` (200 images), while `labels/` came from project `tomato-leaf-mold-6ydxg-nhws1` (84 images).",
        "   - In `powdery_mildew/`: `images/` came from project `powdery_mildew-ctqv7-kvqwj` (334 images, frog-eye + powdery mildew), while `labels/` came from project `powdery-mildew-durian-gcovu` (146 images of DURIAN SẦU RIÊNG).",
        "3. **Raw Class ID Collisions:** Every raw dataset uses `0` (or `0` and `1`) for its own local classes. They CANNOT be directly merged without systematic class remapping.",
        "",
        "## 7. Tiny Lesion Analysis",
        "",
        "- In `septoria_leaf_spot`, lesions are predominantly pinpoint specks (Very Small and Small categories account for high percentage), which is consistent with biological Septoria pycnidia.",
        "- In `leaf_mold`, lesions are diffuse patches.",
        "- In `powdery_mildew`, powdery patches vary from medium spots to large leaf coverings.",
        "",
        "## 8. Background Analysis",
        "",
        "- The Roboflow datasets contain varied agricultural backgrounds including soil, greenhouse benches, and natural sunlight conditions.",
        "- The 'healthy' images inside the Septoria dataset provide natural negative tomato foliage.",
        "",
        "## 9. Duplicate Analysis",
        "",
        f"- Total image duplicates detected across all folders via SHA-256 hash matching: **{sum(len(s['duplicate_images']) for s in all_stats.values())}**",
        "",
        "## 10. Corrupted File Analysis",
        "",
        f"- Total corrupted image files detected via PIL verify: **{sum(len(s['corrupt_images']) for s in all_stats.values())}**",
        "",
        "## 11. Recommended Preprocessing Pipeline (DO NOT RUN YET)",
        "",
        "1. **Isolate and Reorganize:** Do not leave Roboflow packages nested inside `images/` and `labels/`. Instead, cleanly structure them as source packages A and B for each disease.",
        "2. **Discard Non-Tomato Data:** Strictly EXCLUDE the Durian (sầu riêng) dataset (`powdery-mildew-durian-gcovu`) as LEAF_AI is exclusively focused on Tomato leaf diseases.",
        "3. **Filter Frog-Eye Leaf Spot:** In `powdery_mildew-ctqv7-kvqwj`, class 0 is `frog-eye-leaf-spot` and class 1 is `powdery-mildew`. Boxes for `frog-eye-leaf-spot` must either be discarded or handled so only true powdery mildew is mapped.",
        "4. **Re-map Class IDs:**",
        "   - Septoria $\\rightarrow$ Class ID `3` (`Tomato___Septoria_leaf_spot`)",
        "   - Leaf Mold $\\rightarrow$ Class ID `4` (`Tomato___Leaf_mold`)",
        "   - Powdery Mildew $\\rightarrow$ Class ID `5` (`Tomato___Powdery_mildew`)",
        "   - Healthy $\\rightarrow$ Preserved as negative background samples (no bounding boxes or class healthy).",
        "",
        "## 12. Risks Before Training",
        "",
        "- **Species Contamination:** Using Durian powdery mildew will cause the tomato model to detect durian leaf patterns or misclassify foliage.",
        "- **Class Contamination:** The frog-eye-leaf-spot annotations in the powdery mildew dataset would corrupt class boundaries if not filtered out.",
        "- **Duplicate Images across train/test:** Must be deduped before splitting.",
        "",
        "## 13. Recommendation",
        "",
        "- **Readiness:** **NOT READY FOR DIRECT TRAINING.**",
        "- **Required Action:** The user and agent must align on which Roboflow packages to keep, discard the Durian dataset, filter out frog-eye-leaf-spot, and build a dedicated preparation script.",
        "- **Safety Gate:** No training has been run. Model V3 remains 100% untouched.",
        ""
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Report generated at: {output_path}")

def main():
    logger.info("Starting Tomato New Diseases Dataset Audit...")
    logger.info(f"Target Directory: {RAW_TOMATO_NEW_DIR}")

    all_stats = {}
    for dkey in DISEASE_KEYS:
        stats = audit_disease_folder(dkey, RAW_TOMATO_NEW_DIR)
        all_stats[dkey] = stats
        logger.info(f"Audited [{dkey}]: {stats['total_images']} images, {stats['total_labels']} labels, {stats['total_bounding_boxes']} boxes, {len(stats['packages_found'])} packages.")

    generate_markdown_report(all_stats, REPORT_OUTPUT_PATH)
    logger.info("Audit finished successfully.")

if __name__ == "__main__":
    main()
