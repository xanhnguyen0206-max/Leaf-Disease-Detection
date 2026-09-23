from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class AIFallbackResponse(BaseModel):
    is_tomato_leaf: bool
    disease: Optional[str] = None
    confidence: float = 0.0
    reason: str = ""
    provider: str

class BaseAIProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured and available."""
        pass

    @abstractmethod
    def analyze_image(self, image_bytes: bytes, filename: str, yolo_primary_disease: str, yolo_confidence: float) -> AIFallbackResponse:
        """
        Analyze the image and return a fallback response.
        The AI should evaluate independently but can use YOLO results as preliminary evidence.
        """
        pass
