"""
Repositorios e Implementaciones de Scrapers
"""
from .base_scraper import BaseScraper
from .exito_scraper import ExitoScraper
from .jumbo_scraper import JumboScraper
from .falabella_scraper import FalabellaScraper
from .scraper_factory import ScraperFactory, get_scraper_factory
from .product_repository import ProductRepository
from .ai_response_repository import AIResponseRepository

__all__ = [
    "BaseScraper",
    "ExitoScraper", 
    "JumboScraper",
    "FalabellaScraper",
    "ScraperFactory",
    "get_scraper_factory",
    "ProductRepository",
    "AIResponseRepository"
]
