import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LeafAI Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PROJECT_ROOT: str = os.path.dirname(BASE_DIR)
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'leafai.db')}"

    # Model Configuration
    MODEL_TYPE: str = os.environ.get("MODEL_TYPE", "yolo")  # Options: 'yolo', 'mock'
    MODEL_VERSION: str = os.environ.get("MODEL_VERSION", "v3").lower()  # Options: 'v3', 'v2'
    
    # Path resolution: explicit MODEL_PATH > MODEL_VERSION (v2 or v3 default)
    _DEFAULT_MODEL_PATH: str = os.path.join(
        PROJECT_ROOT, "model", "tomato_v2" if os.environ.get("MODEL_VERSION", "v3").lower() == "v2" else "tomato_v3", "best.pt"
    )
    MODEL_PATH: str = os.environ.get("MODEL_PATH", _DEFAULT_MODEL_PATH)
    MODEL_IMG_SIZE: int = int(os.environ.get("MODEL_IMG_SIZE", "640" if os.environ.get("MODEL_VERSION", "v3").lower() == "v3" else "384"))
    MODEL_CONFIDENCE_THRESHOLD: float = float(os.environ.get("MODEL_CONFIDENCE_THRESHOLD", "0.25"))
    MODEL_DEVICE: str = os.environ.get("MODEL_DEVICE", "cpu")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
