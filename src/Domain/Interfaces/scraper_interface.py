"""
Interfaces de Scraper
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..Entities import Product


class IProductScraper(ABC):
    """
    Interfaz base para scrapers de productos.
    Define el contrato que deben cumplir todos los scrapers.
    """
    
    @property
    @abstractmethod
    def store_name(self) -> str:
        """Nombre de la tienda."""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """URL base de la tienda."""
        pass
    
    @abstractmethod
    def get_category_url(self, category: str, page: int = 1) -> str:
        """
        Construye la URL para una categoría específica.
        
        Args:
            category: Nombre de la categoría
            page: Número de página
            
        Returns:
            URL completa de la categoría
        """
        pass
    
    @abstractmethod
    def parse_products(self, html_content: str, category: str) -> List[Product]:
        """
        Parsea el HTML y extrae los productos.
        
        Args:
            html_content: Contenido HTML de la página
            category: Categoría de los productos
            
        Returns:
            Lista de productos extraídos
        """
        pass
    
    @abstractmethod
    def scrape_category(self, category: str, num_pages: int = 2) -> List[Product]:
        """
        Realiza el scraping completo de una categoría.
        
        Args:
            category: Nombre de la categoría
            num_pages: Número de páginas a extraer
            
        Returns:
            Lista de todos los productos encontrados
        """
        pass


class IScraperFactory(ABC):
    """
    Interfaz para la Factory de Scrapers.
    """
    
    @abstractmethod
    def create_scraper(self, store_type: str) -> IProductScraper:
        """
        Crea un scraper para el tipo de tienda especificado.
        
        Args:
            store_type: Tipo de tienda (exito, jumbo, falabella)
            
        Returns:
            Instancia del scraper correspondiente
        """
        pass
    
    @abstractmethod
    def get_available_stores(self) -> List[str]:
        """
        Obtiene la lista de tiendas disponibles.
        
        Returns:
            Lista de nombres de tiendas soportadas
        """
        pass
