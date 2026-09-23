import random
from typing import Optional
from app.services.providers.base_ai_provider import BaseAIProvider, AIFallbackResponse
from app.core.config import settings

class MockAIProvider(BaseAIProvider):
    def is_available(self) -> bool:
        return settings.AI_FALLBACK_PROVIDER == "mock"

    def analyze_image(self, image_bytes: bytes, filename: str, yolo_primary_disease: str, yolo_confidence: float) -> AIFallbackResponse:
        # Simulate some processing delay if needed, but not strictly required for unit tests
        
        # Simple deterministic behavior based on filename or just return the YOLO disease with higher confidence
        # For our mock testing cases:
        fname = filename.lower()
        if "not_leaf" in fname or "dog" in fname or "car" in fname:
            return AIFallbackResponse(
                is_tomato_leaf=False,
                disease="NOT_TOMATO_LEAF",
                confidence=0.99,
                reason="Hình ảnh không chứa lá cà chua. Đây có vẻ là một vật thể khác.",
                provider="mock"
            )
        
        if "uncertain" in fname or "blur" in fname:
            return AIFallbackResponse(
                is_tomato_leaf=True,
                disease="UNCERTAIN",
                confidence=0.3,
                reason="Hình ảnh mờ hoặc không đủ bằng chứng để phân loại chính xác.",
                provider="mock"
            )

        # Map to valid diseases
        valid_diseases = [
            "Tomato___Bacterial_spot",
            "Tomato___Early_blight",
            "Tomato___Late_blight",
            "Tomato___Septoria_leaf_spot",
            "Tomato___Leaf_mold",
            "Tomato___Powdery_mildew"
        ]

        disease = yolo_primary_disease
        if disease not in valid_diseases:
             disease = random.choice(valid_diseases)

        # If it's a test for a specific disease based on name
        for valid_disease in valid_diseases:
            if valid_disease.lower().split("___")[-1] in fname:
                disease = valid_disease
                break

        return AIFallbackResponse(
            is_tomato_leaf=True,
            disease=disease,
            confidence=round(random.uniform(0.75, 0.95), 2),
            reason=f"Phân tích độc lập (Mock AI) xác nhận các dấu hiệu của {disease} trên bề mặt lá.",
            provider="mock"
        )
