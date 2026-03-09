"""
Servicio de Aplicación Principal
"""
import logging
from typing import List, Optional

from ..DTOs import PipelineResultDTO, ScrapingResultDTO, AIAnalysisResultDTO
from ..UseCases import ScrapingUseCase, AIAnalysisUseCase, PipelineUseCase
from ...Domain.ValueObjects import ScrapingConfig, AIConfig, StoreType, LLMProvider
from ...Infrastructure.Repositories import ScraperFactory, ProductRepository, AIResponseRepository

logger = logging.getLogger(__name__)


class ApplicationService:
    """
    Servicio de aplicación que expone la funcionalidad principal.
    Actúa como fachada para los casos de uso.
    """
    
    def __init__(self, output_dir: str = "output"):
        # Inicializar repositorios
        self._product_repo = ProductRepository(output_dir)
        self._ai_repo = AIResponseRepository(output_dir)
        
        # Inicializar factory
        self._scraper_factory = ScraperFactory()
        
        # Inicializar casos de uso
        self._scraping_use_case = ScrapingUseCase(
            self._scraper_factory,
            self._product_repo
        )
        self._ai_use_case = AIAnalysisUseCase(
            self._product_repo,
            self._ai_repo
        )
        self._pipeline_use_case = PipelineUseCase(
            self._scraping_use_case,
            self._ai_use_case
        )
    
    def run_full_pipeline(
        self,
        stores: List[str],
        category: str,
        num_pages: int,
        llm_provider: str,
        llm_model: str,
        output_format: str = "json",
        custom_queries: Optional[List[str]] = None,
        skip_ai: bool = False
    ) -> PipelineResultDTO:
        """
        Ejecuta el pipeline completo de scraping + análisis IA.
        
        Args:
            stores: Lista de tiendas (exito, alkosto, falabella)
            category: Categoría a buscar
            num_pages: Número de páginas por tienda
            llm_provider: Proveedor de LLM (ollama, lm_studio)
            llm_model: Nombre del modelo
            output_format: Formato de salida (json, csv)
            custom_queries: Consultas personalizadas
            skip_ai: Omitir análisis de IA
            
        Returns:
            Resultado completo del pipeline
        """
        # Crear configuraciones
        store_types = [StoreType.from_string(s) for s in stores]
        
        scraping_config = ScrapingConfig(
            stores=store_types,
            category=category,
            num_pages=num_pages,
            output_format=output_format
        )
        
        ai_config = AIConfig(
            provider=LLMProvider.from_string(llm_provider),
            model=llm_model
        )
        
        # Ejecutar pipeline
        return self._pipeline_use_case.execute(
            scraping_config=scraping_config,
            ai_config=ai_config,
            custom_queries=custom_queries,
            skip_ai=skip_ai
        )
    
    def run_scraping_only(
        self,
        stores: List[str],
        category: str,
        num_pages: int,
        output_format: str = "json"
    ) -> ScrapingResultDTO:
        """Ejecuta solo el scraping."""
        store_types = [StoreType.from_string(s) for s in stores]
        
        config = ScrapingConfig(
            stores=store_types,
            category=category,
            num_pages=num_pages,
            output_format=output_format
        )
        
        return self._pipeline_use_case.execute_scraping_only(config)
    
    def run_ai_analysis_only(
        self,
        products_file: str,
        llm_provider: str,
        llm_model: str,
        custom_queries: Optional[List[str]] = None
    ) -> AIAnalysisResultDTO:
        """Ejecuta solo el análisis de IA."""
        config = AIConfig(
            provider=LLMProvider.from_string(llm_provider),
            model=llm_model
        )
        
        return self._pipeline_use_case.execute_ai_only(
            config=config,
            products_file=products_file,
            queries=custom_queries
        )
    
    def get_available_stores(self) -> List[str]:
        """Obtiene las tiendas disponibles."""
        return self._scraper_factory.get_available_stores()
    
    def get_available_providers(self) -> List[str]:
        """Obtiene los proveedores de LLM disponibles."""
        return [p.value for p in LLMProvider]
