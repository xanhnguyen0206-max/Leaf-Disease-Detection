import httpx
import logging
import base64
from app.services.providers.base_ai_provider import BaseAIProvider, AIFallbackResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class GrokProvider(BaseAIProvider):
    def is_available(self) -> bool:
        return settings.AI_FALLBACK_PROVIDER == "grok" and bool(settings.XAI_API_KEY) and settings.AI_FALLBACK_ENABLED

    def analyze_image(self, image_bytes: bytes, filename: str, yolo_primary_disease: str, yolo_confidence: float) -> AIFallbackResponse:
        # NOTE: IN THE CURRENT STATE NO EXTERNAL AI API CALLS ARE MADE
        # This is a structural implementation for future enablement.
        
        # Guard clause
        if not self.is_available():
            raise RuntimeError("Grok provider is not available or properly configured.")

        # Prepare payload
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        prompt = f"""
Review this image independently.
Determine whether the image contains a tomato leaf.
If it is a tomato leaf, classify only among the supported six tomato diseases: 
Tomato___Bacterial_spot, Tomato___Early_blight, Tomato___Late_blight, Tomato___Septoria_leaf_spot, Tomato___Leaf_mold, Tomato___Powdery_mildew.
Use the YOLO preliminary result ({yolo_primary_disease} with {yolo_confidence*100:.2f}%) only as supporting evidence, not as ground truth.
If the image is not a tomato leaf, return disease as NOT_TOMATO_LEAF.
If the evidence is insufficient, return disease as UNCERTAIN.
Respond in JSON format with keys: is_tomato_leaf (boolean), disease (string), confidence (float 0.0-1.0), reason (string in Vietnamese).
"""
        
        # Real API call logic would go here:
        # try:
        #     with httpx.Client(timeout=settings.AI_FALLBACK_TIMEOUT) as client:
        #         response = client.post(
        #             "https://api.x.ai/v1/chat/completions",
        #             headers={
        #                 "Authorization": f"Bearer {settings.XAI_API_KEY}",
        #                 "Content-Type": "application/json"
        #             },
        #             json={
        #                 "model": "grok-vision-beta",
        #                 "messages": [
        #                     {
        #                         "role": "user",
        #                         "content": [
        #                             {"type": "text", "text": prompt},
        #                             {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        #                         ]
        #                     }
        #                 ]
        #             }
        #         )
        #         response.raise_for_status()
        #         # parse json...
        # except Exception as e:
        #     logger.error(f"Grok API failed: {e}")
        #     raise e

        # Since we are NOT calling the API yet (as per requirements), if somehow this is called we return a structural error or default.
        # But this code shouldn't execute right now since XAI_API_KEY is empty and provider is mock.
        
        return AIFallbackResponse(
            is_tomato_leaf=True,
            disease=yolo_primary_disease,
            confidence=0.8,
            reason="Placeholder for real Grok implementation.",
            provider="grok"
        )
