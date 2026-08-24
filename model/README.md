# LeafAI Model Storage

This directory is reserved for trained AI model artifacts used by the LeafAI backend.

## Expected Directory Structure

When a model is trained and ready for production, place the model files here:

```
model/
├── model.pt           # PyTorch / YOLOv8 / EfficientNet model weights
├── classes.json       # Mapping of class index to disease names and metadata
├── config.json        # Inference hyperparameters, input image resolution, normalization stats
└── README.md          # Model metadata, versioning, and architecture notes
```

## Backend Integration Workflow

1. Train a plant leaf disease detection model inside `training/`.
2. Export the final model weights (`model.pt` or `model.onnx`) and save them to `model/`.
3. Create `classes.json` mapping output tensor indices to disease IDs:
   ```json
   {
     "0": "tomato_early_blight",
     "1": "potato_late_blight",
     "2": "apple_powdery_mildew",
     "3": "rose_black_spot",
     "4": "corn_common_rust"
   }
   ```
4. Update `backend/app/services/model_service.py` by switching from `MockModelService` to `TrainedModelService`.
5. The backend REST API (`POST /api/predict`) remains unchanged, ensuring seamless frontend integration without any UI modifications.
