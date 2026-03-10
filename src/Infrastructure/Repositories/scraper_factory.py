"""
Factory de Scrapers
Crea el scraper apropiado según la tienda
"""
import logging
from typing import Dict, Type, List

from ...Domain.Interfaces import IProductScraper, IScraperFactory
from ...Domain.ValueObjects import StoreType
from .base_scraper import BaseScraper
from .exito_scraper import ExitoScraper
from .jumbo_scraper import JumboScraper
from .falabella_scraper import FalabellaScraper

logger = logging.getLogger(__name__)


class ScraperFactory(IScraperFactory):
    """
    Encapsula la creación de scrapers específicos para cada tienda.
    Permite agregar nuevas tiendas sin modificar el código cliente.
    """
    
    # Registro de scrapers disponibles
    _scrapers: Dict[StoreType, Type[BaseScraper]] = {
        StoreType.EXITO: ExitoScraper,
        StoreType.JUMBO: JumboScraper,
        StoreType.FALABELLA: FalabellaScraper
    }
    
    def create_scraper(self, store_type: str) -> IProductScraper:
        """
        Crea una instancia del scraper correspondiente al tipo de tienda.
        
        Args:
            store_type: Nombre de la tienda (exito, jumbo, falabella)
            
        Returns:
            Instancia del scraper específico
            
        Raises:
            ValueError: Si el tipo de tienda no está soportado
        """
        try:
            store_enum = StoreType.from_string(store_type)
        except ValueError:
            available = ", ".join(self.get_available_stores())
            raise ValueError(f"Tienda '{store_type}' no soportada. Disponibles: {available}")
        
        scraper_class = self._scrapers.get(store_enum)
        if not scraper_class:
            raise ValueError(f"No hay scraper registrado para {store_type}")
        
        logger.info(f"Creando scraper para: {store_type}")
        return scraper_class()
    
    def get_available_stores(self) -> List[str]:
        """Retorna la lista de tiendas disponibles."""
        return [store.value for store in self._scrapers.keys()]
    
    @classmethod
    def register_scraper(cls, store_type: StoreType, scraper_class: Type[BaseScraper]) -> None:
        """
        Permite registrar nuevos scrapers dinámicamente.
        Extensibilidad del patrón Factory.
        
        Args:
            store_type: Tipo de tienda
            scraper_class: Clase del scraper
        """
        cls._scrapers[store_type] = scraper_class
        logger.info(f"Scraper registrado para: {store_type.value}")


def get_scraper_factory() -> ScraperFactory:
    """Factory function para obtener la instancia de ScraperFactory."""
    return ScraperFactory()
