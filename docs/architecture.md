# LeafAI Architecture Documentation

```
[ User Browser / Client ]
          │
          ├──> React + TypeScript Frontend (Port 3000)
          │         │
          │         ├── WebGL Shader Canvas & Three.js 3D Leaf Mesh
          │         ├── Multi-Disease Visual Overlay (Color-Coded Bounding Boxes)
          │         ├── SafeImage Fallback & Offline Disease Asset Component
          │         ├── 6-Tab Scientific Disease Detail & Library
          │         ├── 12-Section IPM & Weekly Monitoring Master Guide
          │         └── API Client Service Abstraction (services/api.ts)
          │                   │
          │                   ▼
          └──> FastAPI Backend REST API (Port 8000)
                    │
                    ├── CORS Middleware & Static File Mount (/uploads)
                    ├── Pydantic Input/Output Schemas (DetectedDiseaseGroup)
                    ├── Database Repository (SQLite / SQLAlchemy)
                    │         ├── diseases (20+ Agronomic & Scientific fields)
                    │         ├── care_recommendations (Categorized phác đồ)
                    │         └── diagnosis_history (Multi-disease persistent logs)
                    │
                    └── Prediction Service (prediction_service.py)
                              │
                              ├── Multi-Disease Detection Grouping & Ranking
                              ├── Primary vs Additional Disease Disambiguation
                              ├── Database Knowledge Enrichment (No LLM hallucinations)
                              │
                              └── YOLOModelService (model/tomato_v3/best.pt @ 640x640)
                                        │
                                        └── Ultralytics YOLOv8n Weights Checkpoint
```

