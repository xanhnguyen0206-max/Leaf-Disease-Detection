import os
import sys
import io
import json
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path("c:/Users/Admin/Leaf-Disease-Detection/backend")
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

BASE_DIR = Path("c:/Users/Admin/Leaf-Disease-Detection")
TEST_IMG_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2" / "images" / "test"
TEST_LBL_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2" / "labels" / "test"
HARD_NEG_DIR = BASE_DIR / "training" / "datasets" / "processed" / "tomato_v2" / "hard_negatives"
OUT_DIR = BASE_DIR / "training" / "runs" / "tomato_v2" / "integration_tests"

OUT_DIR.mkdir(parents=True, exist_ok=True)

CLASS_COLORS = {
    0: (255, 50, 50),    # Bacterial Spot: Red
    1: (255, 165, 0),   # Early Blight: Orange
    2: (160, 32, 240),  # Late Blight: Purple
}

def test_real_images():
    print("==========================================")
    print("  LEAF_AI: REAL IMAGE API INTEGRATION TEST")
    print("==========================================\n")
    
    # 1. Health check verification
    health_res = client.get("/api/health")
    print(f"Health Check: {health_res.status_code} -> {health_res.json()}")
    assert health_res.status_code == 200
    assert health_res.json()["model"]["loaded"] is True
    
    # 2. Select test images
    test_cases = []
    
    # Find Healthy image
    healthy_candidates = [p for p in TEST_IMG_DIR.glob("*.jpg") if not (TEST_LBL_DIR / f"{p.stem}.txt").read_text().strip()]
    if healthy_candidates:
        test_cases.append((healthy_candidates[0], "Healthy Tomato Leaf (Test Split)"))
        
    # Find Bacterial Spot
    for img_p in TEST_IMG_DIR.glob("*.jpg"):
        lbl_p = TEST_LBL_DIR / f"{img_p.stem}.txt"
        if lbl_p.exists():
            lines = [l for l in lbl_p.read_text().splitlines() if l.strip()]
            cids = [int(l.split()[0]) for l in lines]
            if 0 in cids and img_p not in [x[0] for x in test_cases]:
                test_cases.append((img_p, "Bacterial Spot (Tomato___Bacterial_spot)"))
                break
                
    # Find Early Blight
    for img_p in TEST_IMG_DIR.glob("*.jpg"):
        lbl_p = TEST_LBL_DIR / f"{img_p.stem}.txt"
        if lbl_p.exists():
            lines = [l for l in lbl_p.read_text().splitlines() if l.strip()]
            cids = [int(l.split()[0]) for l in lines]
            if 1 in cids and img_p not in [x[0] for x in test_cases]:
                test_cases.append((img_p, "Early Blight (Tomato___Early_blight)"))
                break
                
    # Find Late Blight
    for img_p in TEST_IMG_DIR.glob("*.jpg"):
        lbl_p = TEST_LBL_DIR / f"{img_p.stem}.txt"
        if lbl_p.exists():
            lines = [l for l in lbl_p.read_text().splitlines() if l.strip()]
            cids = [int(l.split()[0]) for l in lines]
            if 2 in cids and img_p not in [x[0] for x in test_cases]:
                test_cases.append((img_p, "Late Blight (Tomato___Late_blight)"))
                break
                
    # Hard negative
    hard_negs = list(HARD_NEG_DIR.glob("*.jpg"))
    if hard_negs:
        test_cases.append((hard_negs[0], "Hard Negative (Shadow / Complex Foliage)"))
        if len(hard_negs) > 1:
            test_cases.append((hard_negs[1], "Hard Negative (Dark / Soil Background)"))
            
    print(f"Testing {len(test_cases)} real image test cases against /api/predict:\n")
    
    results_summary = []
    
    for idx, (img_path, desc) in enumerate(test_cases):
        with open(img_path, "rb") as f:
            file_bytes = f.read()
            
        files = {"file": (img_path.name, file_bytes, "image/jpeg")}
        res = client.post("/api/predict", files=files)
        assert res.status_code == 200, f"Failed on {img_path}: {res.text}"
        data = res.json()
        
        # Visualize predictions
        im = Image.open(img_path).convert("RGB")
        w, h = im.size
        draw = ImageDraw.Draw(im)
        
        dets = data.get("detections", [])
        for det in dets:
            cid = det.get("class_id", 0)
            conf = det.get("confidence", 0.0)
            disease = det.get("disease", "")
            bbox = det.get("bbox", {})
            x1, y1, x2, y2 = int(bbox.get("x1", 0)), int(bbox.get("y1", 0)), int(bbox.get("x2", 0)), int(bbox.get("y2", 0))
            
            color = CLASS_COLORS.get(cid, (0, 255, 0))
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            label = f"{disease.split('___')[-1]}: {conf:.2f}"
            draw.text((x1 + 3, y1 + 3), label, fill=color)
            
        out_file = OUT_DIR / f"test_{idx:02d}_{img_path.stem[:20]}.jpg"
        im.save(out_file, quality=90)
        
        status = data.get("status")
        primary_disease = data.get("primary_disease")
        confidence = data.get("confidence")
        rec_count = len(data.get("recommendations", []))
        
        print(f"[{idx+1}/{len(test_cases)}] {desc}:")
        print(f"  Status: {status} | Primary: {primary_disease} | Conf: {confidence:.2f} | Detections: {len(dets)} | Recommendations: {rec_count}")
        print(f"  Saved visual to: {out_file.name}\n")
        
        results_summary.append({
            "test_case": desc,
            "image": img_path.name,
            "status": status,
            "primary_disease": primary_disease,
            "confidence": confidence,
            "num_detections": len(dets),
            "output_image": str(out_file.as_posix())
        })
        
    # Check History persistence
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    print(f"History verification: {len(hist_data)} entries found in database.")
    assert len(hist_data) >= len(test_cases)
    
    print("ALL REAL IMAGE API TESTS PASSED SUCCESSFULLY!")
    return results_summary

if __name__ == "__main__":
    test_real_images()
