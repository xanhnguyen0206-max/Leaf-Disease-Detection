import logging
from typing import Optional, Dict, Any, Type
from app.services.providers.base_ai_provider import BaseAIProvider, AIFallbackResponse
from app.services.providers.mock_ai_provider import MockAIProvider
from app.services.providers.grok_provider import GrokProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIFallbackService:
    def __init__(self):
        # Register available providers
        self.providers: Dict[str, Type[BaseAIProvider]] = {
            "mock": MockAIProvider,
            "grok": GrokProvider
        }
        
    def get_provider(self) -> Optional[BaseAIProvider]:
        if not settings.AI_FALLBACK_ENABLED:
            return None
            
        provider_name = settings.AI_FALLBACK_PROVIDER.lower()
        provider_cls = self.providers.get(provider_name)
        
        if not provider_cls:
            logger.warning(f"AI provider '{provider_name}' is not registered.")
            return None
            
        provider_instance = provider_cls()
        if provider_instance.is_available():
            return provider_instance
            
        return None

    def analyze(self, image_bytes: bytes, filename: str, yolo_disease: str, yolo_confidence: float) -> Optional[AIFallbackResponse]:
        provider = self.get_provider()
        
        if not provider:
            logger.info("AI Fallback requested but no provider is available or enabled.")
            return None
            
        try:
            logger.info(f"Triggering AI Fallback using provider: {settings.AI_FALLBACK_PROVIDER}")
            response = provider.analyze_image(
                image_bytes=image_bytes,
                filename=filename,
                yolo_primary_disease=yolo_disease,
                yolo_confidence=yolo_confidence
            )
            return response
        except Exception as e:
            logger.error(f"AI Fallback provider failed during analysis: {e}")
            return None

ai_fallback_service = AIFallbackService()
