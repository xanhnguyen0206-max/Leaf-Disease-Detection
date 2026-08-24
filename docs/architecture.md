# LeafAI Architecture Documentation

```
[ User Browser / Client ]
          │
          ├──> React + TypeScript Frontend (Port 3000)
          │         │
          │         ├── WebGL Shader Canvas & Three.js 3D Leaf Mesh
          │         └── API Client Service Abstraction (services/api.ts)
          │                   │
          │                   ▼
          └──> FastAPI Backend REST API (Port 8000)
                    │
                    ├── CORS Middleware & Static File Mount (/uploads)
                    ├── Pydantic Input/Output Schemas
                    ├── Database Repository (SQLite / SQLAlchemy)
                    │
                    └── Prediction Service
                              │
                              ├──> [ Current: MockModelService ]
                              │
                              └──> [ Future: TrainedModelService ]
                                        │
                                        └── Model Weights (model/model.pt)
```
