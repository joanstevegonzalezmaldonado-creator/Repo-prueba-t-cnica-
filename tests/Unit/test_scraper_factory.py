"""
Tests Unitarios - Factory de Scrapers
"""
import pytest

from src.Infrastructure.Repositories import (
    ScraperFactory,
    ExitoScraper,
    JumboScraper,
    FalabellaScraper
)
from src.Domain.Interfaces import IProductScraper


class TestScraperFactory:
    """Tests para ScraperFactory (Patrón Factory)."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.factory = ScraperFactory()
    
    def test_create_exito_scraper(self):
        """Test creación de scraper de Éxito."""
        scraper = self.factory.create_scraper("exito")
        
        assert isinstance(scraper, IProductScraper)
        assert isinstance(scraper, ExitoScraper)
        assert scraper.store_name == "Exito"
    
    def test_create_jumbo_scraper(self):
        """Test creación de scraper de Jumbo."""
        scraper = self.factory.create_scraper("jumbo")
        
        assert isinstance(scraper, IProductScraper)
        assert isinstance(scraper, JumboScraper)
        assert scraper.store_name == "Jumbo"
    
    def test_create_falabella_scraper(self):
        """Test creación de scraper de Falabella."""
        scraper = self.factory.create_scraper("falabella")
        
        assert isinstance(scraper, IProductScraper)
        assert isinstance(scraper, FalabellaScraper)
        assert scraper.store_name == "Falabella"
    
    def test_create_invalid_scraper(self):
        """Test error al crear scraper inválido."""
        with pytest.raises(ValueError) as exc_info:
            self.factory.create_scraper("tienda_invalida")
        
        assert "no soportada" in str(exc_info.value)
    
    def test_get_available_stores(self):
        """Test obtener tiendas disponibles."""
        stores = self.factory.get_available_stores()
        
        assert "exito" in stores
        assert "jumbo" in stores
        assert "falabella" in stores
        assert len(stores) == 3


class TestScraperInterface:
    """Tests para verificar que los scrapers implementan la interfaz."""
    
    def test_exito_scraper_interface(self):
        """Test interfaz de ExitoScraper."""
        scraper = ExitoScraper()
        
        assert hasattr(scraper, 'store_name')
        assert hasattr(scraper, 'base_url')
        assert hasattr(scraper, 'get_category_url')
        assert hasattr(scraper, 'parse_products')
        assert hasattr(scraper, 'scrape_category')
    
    def test_exito_category_url(self):
        """Test generación de URL de categoría."""
        scraper = ExitoScraper()
        url = scraper.get_category_url("celulares", 1)
        
        assert "exito.com" in url
        assert "celulares" in url
    
    def test_jumbo_category_url(self):
        """Test generación de URL de categoría."""
        scraper = JumboScraper()
        url = scraper.get_category_url("laptops", 2)
        
        assert "tiendasjumbo.co" in url
        assert "page=2" in url
    
    def test_falabella_category_url(self):
        """Test generación de URL de categoría."""
        scraper = FalabellaScraper()
        url = scraper.get_category_url("televisores", 1)
        
        assert "falabella.com.co" in url
