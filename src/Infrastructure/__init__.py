"""
Capa de Infraestructura
"""
from .ExternalServices import (
    OllamaStrategy,
    LMStudioStrategy,
    LLMContext,
    create_llm_context
)
from .Repositories import (
    BaseScraper,
    ExitoScraper,
    AlkostoScraper,
    FalabellaScraper,
    ScraperFactory,
    get_scraper_factory,
    ProductRepository,
    AIResponseRepository
)

__all__ = [
    "OllamaStrategy",
    "LMStudioStrategy",
    "LLMContext",
    "create_llm_context",
    "BaseScraper",
    "ExitoScraper",
    "AlkostoScraper", 
    "FalabellaScraper",
    "ScraperFactory",
    "get_scraper_factory",
    "ProductRepository",
    "AIResponseRepository"
]
