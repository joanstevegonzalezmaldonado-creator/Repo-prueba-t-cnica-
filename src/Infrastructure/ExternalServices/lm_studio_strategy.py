"""
Estrategia de LLM para LM Studio
"""
import requests
import logging
from datetime import datetime

from .llm_base import BaseLLMStrategy
from ...Domain.Entities import AIResponse
from ...Domain.ValueObjects import AIConfig, LLMProvider

logger = logging.getLogger(__name__)


class LMStudioStrategy(BaseLLMStrategy):
    """
    Estrategia concreta para LM Studio.
    LM Studio expone una API compatible con OpenAI en el puerto 1234.
    """
    
    def __init__(self, config: AIConfig):
        if config.provider != LLMProvider.LM_STUDIO:
            raise ValueError("Esta estrategia solo soporta LM Studio")
        super().__init__(config)
    
    @property
    def provider_name(self) -> str:
        return "LM Studio"
    
    def is_available(self) -> bool:
        """Verifica si LM Studio está ejecutándose."""
        try:
            response = requests.get(f"{self._base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_available_models(self) -> list:
        """Obtiene la lista de modelos disponibles en LM Studio."""
        try:
            response = requests.get(f"{self._base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["id"] for model in data.get("data", [])]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo modelos de LM Studio: {e}")
        return []
    
    def generate_response(self, prompt: str) -> AIResponse:
        """
        Genera una respuesta usando la API compatible con OpenAI de LM Studio.
        Endpoint: /v1/chat/completions
        """
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un asistente experto en análisis de datos de e-commerce."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": False
        }
        
        result = self._make_request("/v1/chat/completions", payload)
        
        if result and "choices" in result:
            choice = result["choices"][0] if result["choices"] else {}
            message = choice.get("message", {})
            usage = result.get("usage", {})
            
            return AIResponse(
                query=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                response=message.get("content", "Sin respuesta"),
                model=self._model,
                provider=self.provider_name,
                created_at=datetime.now(),
                tokens_used=usage.get("total_tokens")
            )
        
        return AIResponse(
            query=prompt[:200] + "..." if len(prompt) > 200 else prompt,
            response="Error: No se pudo obtener respuesta de LM Studio. Verifica que el servidor local esté ejecutándose.",
            model=self._model,
            provider=self.provider_name,
            created_at=datetime.now()
        )
