import os
import hashlib
from pathlib import Path
from collections import defaultdict
from PIL import Image

def inspect_tomato_extra():
    base_dir = Path("c:/Users/Admin/Leaf-Disease-Detection")
    extra_dir = base_dir / "training" / "datasets" / "raw" / "tomato_extra"
    
    print(f"Inspecting directory: {extra_dir}")
    if not extra_dir.exists():
        print(f"Error: {extra_dir} does not exist!")
        return

    folders = [f for f in extra_dir.iterdir() if f.is_dir()]
    print(f"Found subfolders: {[f.name for f in folders]}")
    
    report_data = {}
    all_hashes = {}
    duplicates = []
    corrupted = []
    small_images = []
    
    annotation_extensions = {'.txt', '.xml', '.json', '.csv', '.yaml', '.yml'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff'}
    
    for folder in sorted(folders):
        folder_name = folder.name
        files = list(folder.rglob('*'))
        
        img_files = []
        ann_files = []
        other_files = []
        
        resolutions = []
        formats = defaultdict(int)
        
        for f in files:
            if f.is_dir():
                continue
            ext = f.suffix.lower()
            if ext in image_extensions:
                img_files.append(f)
                formats[ext] += 1
            elif ext in annotation_extensions:
                ann_files.append(f)
            else:
                other_files.append(f)
                
        # Check images
        for img_p in img_files:
            try:
                # MD5 hash
                with open(img_p, 'rb') as fp:
                    h = hashlib.md5(fp.read()).hexdigest()
                if h in all_hashes:
                    duplicates.append((img_p, all_hashes[h]))
                else:
                    all_hashes[h] = img_p
                
                with Image.open(img_p) as img:
                    w, h_dim = img.size
                    resolutions.append((w, h_dim))
                    if w < 64 or h_dim < 64:
                        small_images.append((img_p, (w, h_dim)))
            except Exception as e:
                corrupted.append((img_p, str(e)))
                
        report_data[folder_name] = {
            "image_count": len(img_files),
            "formats": dict(formats),
            "annotation_files_count": len(ann_files),
            "annotation_files": [f.name for f in ann_files[:10]],
            "other_files": [f.name for f in other_files],
            "resolutions_sample": resolutions[:5],
            "unique_resolutions": set(resolutions),
            "total_files": len(files)
        }

    print("\n=== SUMMARY OF INSPECTION ===")
    for folder_name, data in report_data.items():
        print(f"\nFolder: {folder_name}")
        print(f"  Images: {data['image_count']}")
        print(f"  Formats: {data['formats']}")
        print(f"  Annotation files: {data['annotation_files_count']} (Samples: {data['annotation_files']})")
        print(f"  Other files: {len(data['other_files'])}")
        print(f"  Unique resolutions: {len(data['unique_resolutions'])}")
        if data['resolutions_sample']:
            print(f"  Sample resolutions: {data['resolutions_sample']}")
            
    print("\n=== QUALITY CHECK ===")
    print(f"Corrupted images: {len(corrupted)}")
    for c in corrupted:
        print(f"  {c}")
    print(f"Duplicates: {len(duplicates)}")
    for d in duplicates[:10]:
        print(f"  {d[0].name} == {d[1].name} ({d[0].parent.name} vs {d[1].parent.name})")
    print(f"Extremely small images (<64x64): {len(small_images)}")
    for s in small_images:
        print(f"  {s}")

if __name__ == '__main__':
    inspect_tomato_extra()
