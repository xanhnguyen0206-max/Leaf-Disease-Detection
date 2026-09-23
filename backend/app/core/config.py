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
    MODEL_VERSION: str = os.environ.get("MODEL_VERSION", "v4").lower()  # Options: 'v4', 'v3', 'v2'
    
    # AI Fallback Configuration
    AI_FALLBACK_ENABLED: bool = os.environ.get("AI_FALLBACK_ENABLED", "false").lower() == "true"
    AI_FALLBACK_PROVIDER: str = os.environ.get("AI_FALLBACK_PROVIDER", "mock")
    XAI_API_KEY: str = os.environ.get("XAI_API_KEY", "")
    YOLO_HIGH_CONFIDENCE: float = float(os.environ.get("YOLO_HIGH_CONFIDENCE", "0.70"))
    YOLO_LOW_CONFIDENCE: float = float(os.environ.get("YOLO_LOW_CONFIDENCE", "0.40"))
    AI_FALLBACK_TIMEOUT: int = int(os.environ.get("AI_FALLBACK_TIMEOUT", "15"))
    
    # Path resolution: explicit MODEL_PATH > MODEL_VERSION
    _DEFAULT_MODEL_PATH: str = os.path.join(
        PROJECT_ROOT, "model", f"tomato_{os.environ.get('MODEL_VERSION', 'v4').lower()}", "best.pt"
    )
    MODEL_PATH: str = os.environ.get("MODEL_PATH", _DEFAULT_MODEL_PATH)
    MODEL_IMG_SIZE: int = int(os.environ.get("MODEL_IMG_SIZE", "640"))
    MODEL_CONFIDENCE_THRESHOLD: float = float(os.environ.get("MODEL_CONFIDENCE_THRESHOLD", "0.25"))
    MODEL_DEVICE: str = os.environ.get("MODEL_DEVICE", "cpu")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
