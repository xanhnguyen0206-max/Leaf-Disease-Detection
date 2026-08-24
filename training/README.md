# LeafAI Model Training Pipeline

This directory contains the machine learning dataset definitions, training scripts, experimentation notebooks, and configuration files for LeafAI.

## Folder Structure

- `datasets/`: Plant Village / custom leaf disease image datasets.
- `notebooks/`: Jupyter Notebooks for exploratory data analysis (EDA), data augmentation experiments, and model evaluation.
- `scripts/`: Production training scripts (e.g., `train.py`, `evaluate.py`, `export.py`).
- `configs/`: Training hyperparameters, model architecture choices (YOLOv8, ResNet50, EfficientNet-B4), and data augmentations.

## Step-by-Step Training Workflow

### 1. Dataset Setup
Download leaf disease datasets (e.g. PlantVillage dataset) into `training/datasets/plant_village/`:
```
training/datasets/plant_village/
├── train/
├── val/
└── test/
```

### 2. Run Training Script
```bash
python training/scripts/train.py --config training/configs/yolov8_leaf.yaml --epochs 50
```

### 3. Evaluate & Export Weights
```bash
python training/scripts/export.py --weights training/runs/best.pt --output model/model.pt
```

### 4. Connect to Backend
Copy the exported `model.pt` and `classes.json` to `model/` directory. The backend `ModelService` will automatically detect and load the weights.
