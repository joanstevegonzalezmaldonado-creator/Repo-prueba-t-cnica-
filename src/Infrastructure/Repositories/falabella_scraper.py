"""
Scraper para Falabella
"""
import logging
import re
from typing import List
from urllib.parse import quote

from .base_scraper import BaseScraper
from ...Domain.Entities import Product

logger = logging.getLogger(__name__)


class FalabellaScraper(BaseScraper):
    """
    Scraper específico para la tienda Falabella Colombia.
    Implementa los métodos abstractos del Template Method.
    """
    
    @property
    def store_name(self) -> str:
        return "Falabella"
    
    @property  
    def base_url(self) -> str:
        return "https://www.falabella.com.co"
    
    def get_category_url(self, category: str, page: int = 1) -> str:
        """
        Construye la URL de búsqueda de Falabella.
        """
        encoded_category = quote(category)
        return f"{self.base_url}/falabella-co/search?Ntt={encoded_category}&page={page}"
    
    def parse_products(self, html_content: str, category: str) -> List[Product]:
        """
        Parsea el HTML de Falabella y extrae productos.
        """
        products = []
        soup = self._create_soup(html_content)
        
        # Selectores específicos de Falabella
        product_selectors = [
            'div[data-pod]',
            'div.pod',
            'div.product-pod',
            'article[class*="pod"]',
            'div[class*="ProductPod"]',
            'div.search-results-4-grid',
            'div[class*="product-card"]',
            'section[class*="product"]'
        ]
        
        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                product_elements = elements
                logger.debug(f"Falabella - Selector: {selector} ({len(elements)} productos)")
                break
        
        if not product_elements:
            product_elements = soup.find_all('div', class_=re.compile(r'pod|product', re.I))[:50]
        
        for element in product_elements:
            try:
                product = self._extract_product_data(element, category)
                if product and product.name and product.price > 0:
                    products.append(product)
            except Exception as e:
                logger.debug(f"Error extrayendo producto Falabella: {e}")
                continue
        
        return products
    
    def _extract_product_data(self, element, category: str) -> Product:
        """Extrae datos de un elemento de producto de Falabella."""
        # Nombre
        name_selectors = [
            'b.pod-subTitle',
            'span.pod-subTitle',
            'a.pod-link span',
            'span[class*="productName"]',
            'b[class*="title"]',
            'a.pod-link',
            '*[class*="title"]',
            '*[class*="name"]',
            'b', 'h3', 'h2'
        ]
        
        name = ""
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem:
                text = name_elem.get_text(strip=True)
                if text and len(text) > 5:
                    name = text
                    break
        
        # Precio - Falabella tiene estructura específica
        price_selectors = [
            'li.prices-0 span',
            'span[class*="Price"]',
            'span.copy10',
            'ol.prices span',
            '*[class*="price"]',
            'li.prices span'
        ]
        
        price = 0.0
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self._clean_price(price_text)
                if price > 0:
                    break
        
        # Búsqueda alternativa de precio
        if price == 0:
            all_text = element.get_text()
            price_match = re.search(r'\$[\d.,]+', all_text)
            if price_match:
                price = self._clean_price(price_match.group())
        
        # Rating
        rating = None
        rating_selectors = [
            'span[class*="rating"]',
            'div[class*="rating"]',
            '*[class*="stars"]',
            '*[class*="review"]'
        ]
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
