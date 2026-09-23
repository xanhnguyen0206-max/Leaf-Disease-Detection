import os
import shutil
from pathlib import Path
from ultralytics import YOLO

def main():
    # Define paths
    base_dir = Path("C:/Users/Admin/Leaf-Disease-Detection")
    dataset_yaml = base_dir / "training/datasets/processed/tomato_v4/data.yaml"
    project_dir = base_dir / "training/runs/tomato_v4"
    model_output_dir = base_dir / "model/tomato_v4"
    
    print(f"Starting Model V4 Training...")
    print(f"Dataset YAML: {dataset_yaml}")
    print(f"Project Dir: {project_dir}")
    print(f"Model Output Dir: {model_output_dir}")
    
    # Initialize model
    checkpoint_path = project_dir / "train/weights/last.pt"
    if checkpoint_path.exists():
        print(f"Found checkpoint at {checkpoint_path}. Resuming training...")
        model = YOLO(str(checkpoint_path))
        results = model.train(resume=True)
    else:
        model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)
        
        # Train the model
        results = model.train(
            data=str(dataset_yaml),
            epochs=25,
            patience=8,
            batch=16,
            imgsz=640,
            optimizer="AdamW",
            seed=42,
            project=str(project_dir),
            name="train",
            exist_ok=True,
            device="cpu", # Fallback to CPU since no CUDA device is found
        )
    
    print("Training completed. Evaluating on test set...")
    
    # Evaluate on test set
    metrics = model.val(
        data=str(dataset_yaml),
        split="test",
        project=str(project_dir),
        name="test_eval",
        exist_ok=True
    )
    
    # Save the best model to the model/tomato_v4 directory
    model_output_dir.mkdir(parents=True, exist_ok=True)
    
    best_model_path = project_dir / "train/weights/best.pt"
    dest_model_path = model_output_dir / "best.pt"
    
    if best_model_path.exists():
        shutil.copy2(best_model_path, dest_model_path)
        print(f"Copied best model to {dest_model_path}")
    else:
        print(f"WARNING: Best model not found at {best_model_path}")
        
    # Copy configuration files for reproducibility
    if dataset_yaml.exists():
        shutil.copy2(dataset_yaml, model_output_dir / "data.yaml")
        print(f"Copied data.yaml to {model_output_dir}")
        
    args_yaml = project_dir / "train/args.yaml"
    if args_yaml.exists():
        shutil.copy2(args_yaml, model_output_dir / "args.yaml")
        print(f"Copied args.yaml to {model_output_dir}")

    print("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
