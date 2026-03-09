"""
Clase base para estrategias de LLM
Permite intercambiar proveedores de IA (Ollama, LM Studio)
"""
import requests
import logging
from typing import Optional
from abc import ABC, abstractmethod

from ...Domain.Entities import AIResponse
from ...Domain.Interfaces import ILLMStrategy
from ...Domain.ValueObjects import AIConfig

logger = logging.getLogger(__name__)


class BaseLLMStrategy(ILLMStrategy, ABC):
    """
    Clase base abstracta para estrategias de LLM.
    Implementa funcionalidad común y define el template.
    """
    
    def __init__(self, config: AIConfig):
        self._config = config
        self._base_url = config.get_base_url()
        self._model = config.model
        self._temperature = config.temperature
        self._max_tokens = config.max_tokens
    
    @property
    def model_name(self) -> str:
        return self._model
    
    def _make_request(self, endpoint: str, payload: dict) -> Optional[dict]:
        """
        Realiza una petición HTTP al servicio LLM.
        Maneja errores para no detener la ejecución.
        """
        url = f"{self._base_url}{endpoint}"
        try:
            logger.info(f"Enviando petición a {url}...")
            response = requests.post(url, json=payload, timeout=300)  # 5 minutos
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            logger.error(f"No se pudo conectar a {self.provider_name} en {self._base_url}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al conectar con {self.provider_name} (modelo puede estar procesando)")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a {self.provider_name}: {e}")
            return None
    
    def analyze_products(self, products_data: str, query: str) -> AIResponse:
        """
        Analiza productos con una consulta específica.
        Construye un prompt contextualizado para el análisis.
        """
        full_prompt = f"""Eres un analista de datos de e-commerce. 
Analiza los siguientes datos de productos extraídos mediante web scraping:

{products_data}

CONSULTA: {query}

Proporciona un análisis detallado y estructurado en español."""

        return self.generate_response(full_prompt)
