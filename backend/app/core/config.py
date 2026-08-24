import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LeafAI Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'leafai.db')}"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
