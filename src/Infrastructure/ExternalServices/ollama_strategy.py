"""
Estrategia de LLM para Ollama
"""
import requests
import logging
from datetime import datetime

from .llm_base import BaseLLMStrategy
from ...Domain.Entities import AIResponse
from ...Domain.ValueObjects import AIConfig, LLMProvider

logger = logging.getLogger(__name__)


class OllamaStrategy(BaseLLMStrategy):
    """
    Estrategia concreta para Ollama.
    Implementa la generación de respuestas usando la API de Ollama.
    """
    
    def __init__(self, config: AIConfig):
        if config.provider != LLMProvider.OLLAMA:
            raise ValueError("Esta estrategia solo soporta Ollama")
        super().__init__(config)
    
    @property
    def provider_name(self) -> str:
        return "Ollama"
    
    def is_available(self) -> bool:
        """Verifica si Ollama está ejecutándose."""
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_available_models(self) -> list:
        """Obtiene la lista de modelos disponibles en Ollama."""
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo modelos de Ollama: {e}")
        return []
    
    def generate_response(self, prompt: str) -> AIResponse:
        """
        Genera una respuesta usando la API de Ollama.
        Endpoint: /api/generate
        """
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self._temperature,
                "num_predict": self._max_tokens
            }
        }
        
        result = self._make_request("/api/generate", payload)
        
        if result:
            return AIResponse(
                query=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                response=result.get("response", "Sin respuesta"),
                model=self._model,
                provider=self.provider_name,
                created_at=datetime.now(),
                tokens_used=result.get("eval_count")
            )
        
        return AIResponse(
            query=prompt[:200] + "..." if len(prompt) > 200 else prompt,
            response="Error: No se pudo obtener respuesta de Ollama. Verifica que el servicio esté ejecutándose.",
            model=self._model,
            provider=self.provider_name,
            created_at=datetime.now()
        )
