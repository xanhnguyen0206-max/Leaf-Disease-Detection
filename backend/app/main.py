import os
import sys
from pathlib import Path

# Ensure the backend directory is in sys.path so 'app' package imports succeed
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.database.seed import seed_database
from app.api.endpoints import health, predict, history, diseases, care

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/api/openapi.json"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(predict.router, prefix=settings.API_V1_STR, tags=["Prediction"])
app.include_router(history.router, prefix=settings.API_V1_STR, tags=["History"])
app.include_router(diseases.router, prefix=settings.API_V1_STR, tags=["Diseases"])
app.include_router(care.router, prefix=settings.API_V1_STR, tags=["Care"])

@app.on_event("startup")
def startup_event():
    seed_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
