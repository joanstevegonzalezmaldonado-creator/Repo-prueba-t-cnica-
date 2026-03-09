"""
Capa de Dominio - Núcleo de la aplicación
"""
from .Entities import Product, AIResponse
from .ValueObjects import ScrapingConfig, AIConfig, StoreType, LLMProvider
from .Interfaces import (
    IProductScraper, 
    IScraperFactory, 
    ILLMStrategy, 
    ILLMContext,
    IProductRepository,
    IAIResponseRepository
)

__all__ = [
    "Product",
    "AIResponse",
    "ScrapingConfig",
    "AIConfig",
    "StoreType",
    "LLMProvider",
    "IProductScraper",
    "IScraperFactory",
    "ILLMStrategy",
    "ILLMContext",
    "IProductRepository",
    "IAIResponseRepository"
]
