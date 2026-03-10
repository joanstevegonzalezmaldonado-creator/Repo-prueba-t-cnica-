"""
Scraper para Jumbo Colombia
"""
import logging
import re
from typing import List
from urllib.parse import quote

from .base_scraper import BaseScraper
from ...Domain.Entities import Product

logger = logging.getLogger(__name__)


class JumboScraper(BaseScraper):
    """
    Scraper específico para la tienda Jumbo Colombia.
    Implementa los métodos abstractos del Template Method.
    """
    
    @property
    def store_name(self) -> str:
        return "Jumbo"
    
    @property
    def base_url(self) -> str:
        return "https://www.tiendasjumbo.co"
    
    def get_category_url(self, category: str, page: int = 1) -> str:
        """
        Construye la URL de búsqueda de Jumbo.
        """
        encoded_category = quote(category)
        offset = (page - 1) * 20
        return f"{self.base_url}/{encoded_category}?map=ft&page={page}&from={offset}&to={offset+19}"
    
    def parse_products(self, html_content: str, category: str) -> List[Product]:
        """
        Parsea el HTML de Jumbo y extrae productos.
        """
        products = []
        seen_urls = set()
        soup = self._create_soup(html_content)
        
        # Selectores para productos de Jumbo (VTEX)
        product_selectors = [
            'div[class*="vtex-search-result"] article',
            'div[class*="galleryItem"]',
            'article[class*="product"]',
            'div[class*="product-card"]',
            'section[class*="product"]',
            'div.product-item',
            'article',
        ]
        
        product_elements = []
        
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                valid_elements = []
                for el in elements:
                    text = el.get_text()
                    if '$' in text and len(text) > 20:
                        valid_elements.append(el)
                
                if valid_elements:
                    product_elements = valid_elements
                    logger.info(f"Selector '{selector}': {len(valid_elements)} productos")
                    break
        
        # Fallback: buscar contenedores con precios
        if not product_elements:
            logger.info("Buscando contenedores con precios...")
            all_price_elements = soup.find_all(string=re.compile(r'\$[\d.,]+'))
            for price_text in all_price_elements[:50]:
                parent = price_text.find_parent(['article', 'div', 'li', 'section'])
                if parent and parent not in product_elements:
                    text = parent.get_text()
                    if len(text) > 30:
                        product_elements.append(parent)
        
        logger.info(f"Total elementos a procesar: {len(product_elements)}")
        
        for element in product_elements:
            try:
                product = self._extract_product_data(element, category)
                if product and product.name and product.price > 0:
                    if product.url and product.url not in seen_urls:
                        seen_urls.add(product.url)
                        products.append(product)
                        logger.debug(f"Producto: {product.name[:40]}... - ${product.price:,.0f}")
                    elif not product.url:
                        products.append(product)
            except Exception as e:
                logger.debug(f"Error extrayendo producto: {e}")
                continue
        
        return products
    
    def _extract_product_data(self, element, category: str) -> Product:
        """Extrae datos de un elemento de producto de Jumbo."""
        
        # Buscar nombre
        name = ""
        name_selectors = [
            'span[class*="productBrand"]',
            'h3[class*="productName"]',
            'span[class*="productName"]',
            'a[class*="productName"]',
            'h3 a',
            'h2 a',
            '*[class*="name"]',
            'h3',
            'h2',
        ]
        
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem:
                text = name_elem.get_text(strip=True)
                if text and len(text) > 5:
                    name = text
                    break
        
        # Buscar precio
        price = 0.0
        price_selectors = [
            'span[class*="sellingPrice"]',
            'span[class*="currencyInteger"]',
            'div[class*="price"]',
            'span[class*="price"]',
            '*[class*="Price"]',
        ]
        
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                if '$' in price_text or price_text.replace('.', '').replace(',', '').isdigit():
                    price = self._clean_price(price_text)
                    if 100 < price < 100000000:
                        break
        
        # Fallback: buscar precio en todo el texto
        if price == 0:
            all_text = element.get_text()
            prices_found = re.findall(r'\$\s*([\d.]+)', all_text)
            for price_str in prices_found:
                parsed = self._clean_price('$' + price_str)
                if 100 < parsed < 100000000:
                    price = parsed
                    break
        
        # Buscar rating
        rating = None
        rating_elem = element.select_one('[class*="rating"], [class*="Rating"], [class*="stars"]')
        if rating_elem:
            rating = self._clean_rating(rating_elem.get_text(strip=True))
        
        # URL del producto
        url = None
        link_elem = element.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            url = href if href.startswith('http') else f"{self.base_url}{href}"
        
        # Imagen
        image_url = None
        img_elem = element.find('img')
        if img_elem:
            image_url = img_elem.get('src') or img_elem.get('data-src')
        
        return Product(
            name=name[:200] if name else "",
            price=price,
            store=self.store_name,
            category=category,
            rating=rating,
            url=url,
            image_url=image_url
        )
