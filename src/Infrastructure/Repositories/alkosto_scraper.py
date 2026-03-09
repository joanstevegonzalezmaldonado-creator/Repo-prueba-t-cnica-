"""
Scraper para Alkosto
"""
import logging
import re
from typing import List
from urllib.parse import quote

from .base_scraper import BaseScraper
from ...Domain.Entities import Product

logger = logging.getLogger(__name__)


class AlkostoScraper(BaseScraper):
    """
    Scraper específico para la tienda Alkosto.
    Implementa los métodos abstractos del Template Method.
    """
    
    @property
    def store_name(self) -> str:
        return "Alkosto"
    
    @property
    def base_url(self) -> str:
        return "https://www.alkosto.com"
    
    def get_category_url(self, category: str, page: int = 1) -> str:
        """
        Construye la URL de búsqueda de Alkosto.
        Alkosto usa un formato diferente para categorías.
        """
        encoded_category = quote(category)
        return f"{self.base_url}/search?q={encoded_category}&page={page}"
    
    def parse_products(self, html_content: str, category: str) -> List[Product]:
        """
        Parsea el HTML de Alkosto y extrae productos.
        """
        products = []
        soup = self._create_soup(html_content)
        
        # Selectores para productos en Alkosto (VTEX based)
        product_selectors = [
            'div.vtex-search-result-3-x-galleryItem',
            'article.vtex-product-summary',
            'div[class*="galleryItem"]',
            'div[class*="productCard"]',
            'div.product-item',
            'li.product',
            'div[data-testid*="product"]'
        ]
        
        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                product_elements = elements
                logger.debug(f"Alkosto - Selector: {selector} ({len(elements)} productos)")
                break
        
        if not product_elements:
            product_elements = soup.find_all('div', class_=re.compile(r'product|gallery', re.I))[:50]
        
        for element in product_elements:
            try:
                product = self._extract_product_data(element, category)
                if product and product.name and product.price > 0:
                    products.append(product)
            except Exception as e:
                logger.debug(f"Error extrayendo producto Alkosto: {e}")
                continue
        
        return products
    
    def _extract_product_data(self, element, category: str) -> Product:
        """Extrae datos de un elemento de producto de Alkosto."""
        # Nombre
        name_selectors = [
            'span.vtex-product-summary-2-x-productBrand',
            'h2.vtex-product-summary-2-x-productBrand',
            'span[class*="productBrand"]',
            'span[class*="productName"]',
            'h3.product-name',
            'a.product-name',
            '*[class*="name"]',
            'h3', 'h2'
        ]
        
        name = ""
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem:
                text = name_elem.get_text(strip=True)
                if text and len(text) > 3:
                    name = text
                    break
        
        # Precio
        price_selectors = [
            'span.vtex-product-price-1-x-sellingPriceValue',
            'span[class*="sellingPrice"]',
            'span[class*="currencyInteger"]',
            'span.price',
            'div.price',
            '*[class*="price"]'
        ]
        
        price = 0.0
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                if price > 0:
                    break
        
        # Si no encontramos precio, buscar en todo el elemento
        if price == 0:
            all_text = element.get_text()
            price_match = re.search(r'\$[\d.,]+', all_text)
            if price_match:
                price = self._clean_price(price_match.group())
        
        # Rating
        rating = None
        rating_selectors = ['*[class*="rating"]', '*[class*="stars"]', '*[class*="review"]']
        for selector in rating_selectors:
            rating_elem = element.select_one(selector)
            if rating_elem:
                rating = self._clean_rating(rating_elem.get_text(strip=True))
                if rating:
                    break
        
        # URL
        url = None
        link = element.find('a', href=True)
        if link:
            href = link['href']
            url = href if href.startswith('http') else f"{self.base_url}{href}"
        
        # Imagen
        image_url = None
        img = element.find('img')
        if img:
            image_url = img.get('src') or img.get('data-src')
        
        return Product(
            name=name[:200] if name else "",
            price=price,
            store=self.store_name,
            category=category,
            rating=rating,
            url=url,
            image_url=image_url
        )
