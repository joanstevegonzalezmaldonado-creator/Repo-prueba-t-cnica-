"""
Caso de Uso: Pipeline Completo
Orquesta el flujo completo: Scraping -> Análisis IA
"""
import logging
import time
from typing import List, Optional

from ..DTOs import PipelineResultDTO, ScrapingResultDTO, AIAnalysisResultDTO
from ...Domain.ValueObjects import ScrapingConfig, AIConfig
from .scraping_use_case import ScrapingUseCase
from .ai_analysis_use_case import AIAnalysisUseCase

logger = logging.getLogger(__name__)


class PipelineUseCase:
    """
    Caso de uso que orquesta el flujo completo de la aplicación.
    1. Ejecuta el scraping
    2. Ejecuta el análisis de IA
    """
    
    def __init__(
        self,
        scraping_use_case: ScrapingUseCase,
        ai_analysis_use_case: AIAnalysisUseCase
    ):
        self._scraping = scraping_use_case
        self._ai_analysis = ai_analysis_use_case
    
    def execute(
        self,
        scraping_config: ScrapingConfig,
        ai_config: AIConfig,
        custom_queries: Optional[List[str]] = None,
        skip_ai: bool = False
    ) -> PipelineResultDTO:
        """
        Ejecuta el pipeline completo.
        
        Args:
            scraping_config: Configuración de scraping
            ai_config: Configuración de IA
            custom_queries: Consultas personalizadas para IA
            skip_ai: Si True, omite el análisis de IA
            
        Returns:
            DTO con todos los resultados
        """
        start_time = time.time()
        
        # FASE 1: Scraping
        logger.info("=" * 60)
        logger.info("FASE 1: SCRAPING")
        logger.info("=" * 60)
        
        scraping_result = self._scraping.execute(scraping_config)
        
        logger.info(f"Scraping completado: {scraping_result.total_products} productos")
        
        # FASE 2: Análisis IA
        ai_result = None
        
        if not skip_ai and scraping_result.success:
            logger.info("")
            logger.info("=" * 60)
            logger.info("FASE 2: ANÁLISIS CON IA")
            logger.info("=" * 60)
            
            ai_result = self._ai_analysis.execute(
                config=ai_config,
                products_file=scraping_result.file_path,
                custom_queries=custom_queries
            )
            
            if ai_result.is_available:
                logger.info(f"Análisis completado: {ai_result.queries_executed} consultas")
            else:
                logger.warning(f"Análisis IA no disponible: {ai_result.error_message}")
        elif skip_ai:
            logger.info("Análisis IA omitido por configuración")
        else:
            logger.warning("No se ejecutó análisis IA: sin productos disponibles")
        
        total_time = time.time() - start_time
        
        return PipelineResultDTO(
            scraping_result=scraping_result,
            ai_result=ai_result,
            total_execution_time=total_time
        )
    
    def execute_scraping_only(self, config: ScrapingConfig) -> ScrapingResultDTO:
        """Ejecuta solo el scraping."""
        return self._scraping.execute(config)
    
    def execute_ai_only(
        self,
        config: AIConfig,
        products_file: str,
        queries: Optional[List[str]] = None
    ) -> AIAnalysisResultDTO:
        """Ejecuta solo el análisis de IA."""
        return self._ai_analysis.execute(config, products_file, queries)
