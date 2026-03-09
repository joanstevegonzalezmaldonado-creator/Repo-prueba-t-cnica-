"""
Caso de Uso: Ejecutar Scraping
"""
import logging
import time
from typing import List
from collections import defaultdict

from ..DTOs import ScrapingResultDTO
from ...Domain.Entities import Product
from ...Domain.ValueObjects import ScrapingConfig, StoreType
from ...Infrastructure.Repositories import ScraperFactory, ProductRepository

logger = logging.getLogger(__name__)


class ScrapingUseCase:
    """
    Caso de uso para ejecutar el proceso de scraping.
    Orquesta los scrapers y la persistencia de resultados.
    """
    
    def __init__(
        self,
        scraper_factory: ScraperFactory,
        product_repository: ProductRepository
    ):
        self._factory = scraper_factory
        self._repository = product_repository
    
    def execute(self, config: ScrapingConfig) -> ScrapingResultDTO:
        """
        Ejecuta el scraping según la configuración.
        
        Args:
            config: Configuración de scraping
            
        Returns:
            DTO con los resultados del scraping
        """
        start_time = time.time()
        all_products: List[Product] = []
        products_by_store: dict = defaultdict(int)
        errors: List[str] = []
        
        logger.info(f"Iniciando scraping - Categoría: {config.category}, Páginas: {config.num_pages}")
        logger.info(f"Tiendas: {[s.value for s in config.stores]}")
        
        for store_type in config.stores:
            try:
                # Factory crea el scraper apropiado
                scraper = self._factory.create_scraper(store_type.value)
                
                # Ejecutar scraping (Template Method)
                products = scraper.scrape_category(
                    category=config.category,
                    num_pages=config.num_pages
                )
                
                all_products.extend(products)
                products_by_store[store_type.value] = len(products)
                
                logger.info(f"✓ {store_type.value}: {len(products)} productos")
                
            except Exception as e:
                error_msg = f"Error en {store_type.value}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                products_by_store[store_type.value] = 0
        
        # Guardar resultados
        filename = f"results.{config.output_format}"
        file_path = self._repository.save_products(all_products, filename)
        
        execution_time = time.time() - start_time
        
        return ScrapingResultDTO(
            total_products=len(all_products),
            products_by_store=dict(products_by_store),
            file_path=file_path,
            execution_time=execution_time,
            errors=errors
        )
    
    def get_available_stores(self) -> List[str]:
        """Retorna las tiendas disponibles."""
        return self._factory.get_available_stores()
