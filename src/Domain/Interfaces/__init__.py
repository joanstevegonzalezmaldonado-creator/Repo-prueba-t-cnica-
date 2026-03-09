"""
Interfaces del Dominio
"""
from .scraper_interface import IProductScraper, IScraperFactory
from .llm_interface import ILLMStrategy, ILLMContext
from .repository_interface import IProductRepository, IAIResponseRepository

__all__ = [
    "IProductScraper", 
    "IScraperFactory",
    "ILLMStrategy", 
    "ILLMContext",
    "IProductRepository",
    "IAIResponseRepository"
]
