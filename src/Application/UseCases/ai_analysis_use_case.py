"""
Caso de Uso: Análisis con IA
"""
import logging
import time
import json
from typing import List, Optional
from pathlib import Path

from ..DTOs import AIAnalysisResultDTO
from ...Domain.Entities import AIResponse, Product
from ...Domain.ValueObjects import AIConfig
from ...Infrastructure.ExternalServices import LLMContext, create_llm_context
from ...Infrastructure.Repositories import ProductRepository, AIResponseRepository

logger = logging.getLogger(__name__)


class AIAnalysisUseCase:
    """
    Caso de uso para ejecutar análisis con IA.
    Coordina la lectura de datos, consultas al LLM y persistencia.
    """
    
    # Consultas predefinidas para el análisis
    DEFAULT_QUERIES = [
        "Genera un informe ejecutivo con: Top 3 productos más baratos, Top 3 más caros, y precio promedio por marca. Presenta la información en tablas.",
        "Lista las mejores ofertas disponibles considerando relación calidad-precio y explica brevemente por qué son buenas compras."
    ]
    
    def __init__(
        self,
        product_repository: ProductRepository,
        ai_response_repository: AIResponseRepository
    ):
        self._product_repo = product_repository
        self._ai_repo = ai_response_repository
        self._llm_context: Optional[LLMContext] = None
    
    def execute(
        self,
        config: AIConfig,
        products_file: str,
        custom_queries: Optional[List[str]] = None
    ) -> AIAnalysisResultDTO:
        """
        Ejecuta el análisis de IA sobre los productos.
        
        Args:
            config: Configuración de IA
            products_file: Archivo con los productos
            custom_queries: Consultas personalizadas (opcional)
            
        Returns:
            DTO con los resultados del análisis
        """
        start_time = time.time()
        
        # Inicializar contexto LLM (Strategy Pattern)
        self._llm_context = create_llm_context(config)
        
        # Verificar disponibilidad
        if not self._llm_context.is_available():
            logger.warning(f"Servicio LLM no disponible: {config.provider.value}")
            return AIAnalysisResultDTO(
                provider=config.provider.value,
                model=config.model,
                queries_executed=0,
                file_path="",
                execution_time=time.time() - start_time,
                is_available=False,
                error_message=f"El servicio {config.provider.value} no está disponible. Verifica que esté ejecutándose."
            )
        
        logger.info(f"LLM disponible: {self._llm_context.get_current_provider()}")
        
        # Cargar productos
        products = self._load_products(products_file)
        if not products:
            return AIAnalysisResultDTO(
                provider=config.provider.value,
                model=config.model,
                queries_executed=0,
                file_path="",
                execution_time=time.time() - start_time,
                is_available=True,
                error_message="No se encontraron productos para analizar"
            )
        
        # Preparar datos para el análisis
        products_data = self._format_products_for_analysis(products)
        
        # Ejecutar consultas
        queries = custom_queries if custom_queries else self.DEFAULT_QUERIES
        logger.info(f"Ejecutando {len(queries)} consultas de análisis...")
        
        responses = self._llm_context.analyze(products_data, queries)
        
        # Guardar respuestas
        file_path = self._ai_repo.save_responses(responses, "ai_summary.md")
        
        execution_time = time.time() - start_time
        
        return AIAnalysisResultDTO(
            provider=self._llm_context.get_current_provider(),
            model=config.model,
            queries_executed=len(responses),
            file_path=file_path,
            execution_time=execution_time,
            is_available=True
        )
    
    def _load_products(self, products_file: str) -> List[Product]:
        """Carga productos desde el archivo."""
        try:
            # Extraer solo el nombre del archivo
            filename = Path(products_file).name
            return self._product_repo.load_products(filename)
        except Exception as e:
            logger.error(f"Error cargando productos: {e}")
            return []
    
    def _format_products_for_analysis(self, products: List[Product]) -> str:
        """Formatea los productos para enviar al LLM."""
        lines = [
            f"Total de productos: {len(products)}",
            "",
            "Datos de productos:",
            "-" * 50
        ]
        
        # Estadísticas básicas
        by_store = {}
        prices = []
        
        for p in products:
            if p.store not in by_store:
                by_store[p.store] = []
            by_store[p.store].append(p)
            if p.price > 0:
                prices.append(p.price)
        
        lines.append(f"\nProductos por tienda:")
        for store, store_products in by_store.items():
            lines.append(f"  - {store}: {len(store_products)}")
        
        if prices:
            lines.extend([
                f"\nEstadísticas de precios:",
                f"  - Mínimo: ${min(prices):,.0f}",
                f"  - Máximo: ${max(prices):,.0f}",
                f"  - Promedio: ${sum(prices)/len(prices):,.0f}",
            ])
        
        lines.append("\nListado de productos:")
        lines.append("-" * 50)
        
        # Limitar a 50 productos para no exceder contexto del LLM
        for i, product in enumerate(products[:50], 1):
            rating_str = f", Rating: {product.rating}" if product.rating else ""
            lines.append(f"{i}. [{product.store}] {product.name} - ${product.price:,.0f}{rating_str}")
        
        if len(products) > 50:
            lines.append(f"\n... y {len(products) - 50} productos más")
        
        return "\n".join(lines)
