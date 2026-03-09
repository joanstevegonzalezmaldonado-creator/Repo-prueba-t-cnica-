"""
Contexto para el patrón Strategy de LLM
"""
import logging
from typing import List, Optional

from ...Domain.Entities import AIResponse
from ...Domain.Interfaces import ILLMStrategy, ILLMContext
from ...Domain.ValueObjects import AIConfig, LLMProvider
from .ollama_strategy import OllamaStrategy
from .lm_studio_strategy import LMStudioStrategy

logger = logging.getLogger(__name__)


class LLMContext(ILLMContext):
    """
    Contexto que mantiene la referencia a la estrategia de LLM actual.
    """
    
    def __init__(self, config: AIConfig):
        """
        Inicializa el contexto con una configuración.
        Crea automáticamente la estrategia apropiada.
        """
        self._strategy: Optional[ILLMStrategy] = None
        self._config = config
        self._initialize_strategy()
    
    def _initialize_strategy(self) -> None:
        """Inicializa la estrategia según el proveedor configurado."""
        if self._config.provider == LLMProvider.OLLAMA:
            self._strategy = OllamaStrategy(self._config)
        elif self._config.provider == LLMProvider.LM_STUDIO:
            self._strategy = LMStudioStrategy(self._config)
        else:
            raise ValueError(f"Proveedor no soportado: {self._config.provider}")
        
        logger.info(f"Estrategia LLM inicializada: {self._strategy.provider_name}")
    
    def set_strategy(self, strategy: ILLMStrategy) -> None:
        """Permite cambiar la estrategia en tiempo de ejecución."""
        self._strategy = strategy
        logger.info(f"Estrategia LLM cambiada a: {strategy.provider_name}")
    
    def get_current_provider(self) -> str:
        """Obtiene el nombre del proveedor actual."""
        if self._strategy:
            return self._strategy.provider_name
        return "Ninguno"
    
    def is_available(self) -> bool:
        """Verifica si el servicio LLM actual está disponible."""
        if self._strategy:
            return self._strategy.is_available()
        return False
    
    def analyze(self, data: str, queries: List[str]) -> List[AIResponse]:
        """
        Ejecuta múltiples consultas de análisis usando la estrategia actual.
        
        Args:
            data: Datos a analizar (productos en formato texto)
            queries: Lista de consultas a realizar
            
        Returns:
            Lista de respuestas del modelo
        """
        if not self._strategy:
            raise RuntimeError("No hay estrategia de LLM configurada")
        
        responses = []
        for query in queries:
            logger.info(f"Ejecutando consulta: {query[:50]}...")
            try:
                response = self._strategy.analyze_products(data, query)
                responses.append(response)
                logger.info(f"Respuesta recibida de {self._strategy.provider_name}")
            except Exception as e:
                logger.error(f"Error en consulta '{query[:30]}...': {e}")
                # No detenemos la ejecución, creamos una respuesta de error
                responses.append(AIResponse(
                    query=query,
                    response=f"Error al procesar la consulta: {str(e)}",
                    model=self._strategy.model_name,
                    provider=self._strategy.provider_name
                ))
        
        return responses


def create_llm_context(config: AIConfig) -> LLMContext:
    """
    Factory function para crear el contexto LLM apropiado.
    
    Args:
        config: Configuración de IA
        
    Returns:
        Contexto LLM inicializado
    """
    return LLMContext(config)
