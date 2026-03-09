"""
Interfaces de Repositorio - Capa de Dominio
"""
from abc import ABC, abstractmethod
from typing import List
from ..Entities import Product, AIResponse


class IProductRepository(ABC):
    """Interfaz para persistencia de productos."""
    
    @abstractmethod
    def save_products(self, products: List[Product], filename: str) -> str:
        """
        Guarda la lista de productos.
        
        Args:
            products: Lista de productos a guardar
            filename: Nombre del archivo
            
        Returns:
            Ruta del archivo guardado
        """
        pass
    
    @abstractmethod
    def load_products(self, filename: str) -> List[Product]:
        """
        Carga productos desde un archivo.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Lista de productos cargados
        """
        pass


class IAIResponseRepository(ABC):
    """Interfaz para persistencia de respuestas de IA."""
    
    @abstractmethod
    def save_responses(self, responses: List[AIResponse], filename: str) -> str:
        """
        Guarda las respuestas de IA en formato Markdown.
        
        Args:
            responses: Lista de respuestas
            filename: Nombre del archivo
            
        Returns:
            Ruta del archivo guardado
        """
        pass
