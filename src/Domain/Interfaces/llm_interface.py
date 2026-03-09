"""
Interfaces de LLM
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..Entities import AIResponse


class ILLMStrategy(ABC):
    """
    Interfaz para proveedores de LLM.
    Permite intercambiar entre Ollama, LM Studio, etc.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nombre del proveedor de LLM."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nombre del modelo en uso."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el servicio LLM está disponible.
        
        Returns:
            True si el servicio está activo
        """
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str) -> AIResponse:
        """
        Genera una respuesta del modelo LLM.
        
        Args:
            prompt: Texto de entrada para el modelo
            
        Returns:
            Respuesta del modelo encapsulada en AIResponse
        """
        pass
    
    @abstractmethod
    def analyze_products(self, products_data: str, query: str) -> AIResponse:
        """
        Analiza datos de productos con una consulta específica.
        
        Args:
            products_data: Datos de productos en formato texto
            query: Consulta de análisis
            
        Returns:
            Respuesta del análisis
        """
        pass


class ILLMContext(ABC):
    """
    Contexto para el patrón Strategy de LLM.
    Permite cambiar la estrategia en tiempo de ejecución.
    """
    
    @abstractmethod
    def set_strategy(self, strategy: ILLMStrategy) -> None:
        """
        Establece la estrategia de LLM a usar.
        
        Args:
            strategy: Estrategia de LLM
        """
        pass
    
    @abstractmethod
    def get_current_provider(self) -> str:
        """
        Obtiene el nombre del proveedor actual.
        
        Returns:
            Nombre del proveedor
        """
        pass
    
    @abstractmethod
    def analyze(self, data: str, queries: List[str]) -> List[AIResponse]:
        """
        Ejecuta múltiples consultas de análisis.
        
        Args:
            data: Datos a analizar
            queries: Lista de consultas
            
        Returns:
            Lista de respuestas del modelo
        """
        pass
