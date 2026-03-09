"""
Scraper para Éxito
"""
import logging
import re
from typing import List
from urllib.parse import quote

from .base_scraper import BaseScraper
from ...Domain.Entities import Product

logger = logging.getLogger(__name__)


class ExitoScraper(BaseScraper):
    """
    Scraper específico para la tienda Éxito.
    Implementa los métodos abstractos del Template Method.
    """
    
    @property
    def store_name(self) -> str:
        return "Exito"
    
    @property
    def base_url(self) -> str:
        return "https://www.exito.com"
    
    def get_category_url(self, category: str, page: int = 1) -> str:
        """
        Construye la URL de búsqueda de Éxito.
        """
        encoded_category = quote(category)
        return f"{self.base_url}/{encoded_category}?page={page}"
    
    def parse_products(self, html_content: str, category: str) -> List[Product]:
        """
        Parsea el HTML de Éxito y extrae productos.
        """
        products = []
        seen_urls = set()  # Para evitar duplicados
        soup = self._create_soup(html_content)
        
        # Múltiples selectores para encontrar productos
        product_elements = []
        
        # Intentar varios selectores (orden por probabilidad)
        selectors = [
            '[data-fs-product-card]',
            'article[class*="product"]',
            'div[class*="product-card"]',
            'div[class*="ProductCard"]',
            'section[class*="product"]',
            'li[class*="product"]',
            'article',  # Fallback genérico
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # Filtrar solo elementos que parecen contener productos
                valid_elements = []
                for el in elements:
                    text = el.get_text()
                    # Debe tener un precio para ser un producto
                    if '$' in text and len(text) > 20:
                        valid_elements.append(el)
                
                if valid_elements:
                    product_elements = valid_elements
                    logger.info(f"Selector '{selector}': {len(valid_elements)} productos válidos")
                    break
                else:
                    logger.debug(f"Selector '{selector}': {len(elements)} elementos, 0 con precios")
        
        # Si no encontramos, buscar cualquier enlace que contenga un precio cerca
        if not product_elements:
            logger.info("Buscando contenedores con precios...")
            all_price_elements = soup.find_all(string=re.compile(r'\$[\d.,]+'))
            for price_text in all_price_elements[:50]:  # Revisar primeros 50
                parent = price_text.find_parent(['article', 'div', 'li', 'section'])
                if parent and parent not in product_elements:
                    # Verificar que tenga nombre y precio
                    text = parent.get_text()
                    if len(text) > 30:
                        product_elements.append(parent)
            logger.info(f"Encontrados {len(product_elements)} contenedores con precios")
        
        logger.info(f"Total elementos a procesar: {len(product_elements)}")
        
        for element in product_elements:
            try:
                product = self._extract_product_data(element, category)
                if product and product.name and product.price > 0:
                    # Evitar duplicados por URL
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
        """Extrae datos de un elemento de producto."""
        
        # Buscar nombre del producto - específico para Éxito
        name = ""
        
        # Primero buscar en h3 directamente
        h3_elem = element.find('h3')
        if h3_elem:
            # Buscar texto en el primer h3, excluyendo sub-elementos como marca
            first_text = h3_elem.find(string=True, recursive=False)
            if first_text and len(first_text.strip()) > 5:
                name = first_text.strip()
            else:
                # Buscar en enlaces o spans dentro del h3
                name_link = h3_elem.find('a')
                if name_link:
                    name = name_link.get_text(strip=True)
        
        if not name or len(name) < 5:
            # Buscar cualquier enlace con /p (producto)
            link = element.find('a', href=re.compile(r'/p$'))
            if link:
                link_text = link.get_text(strip=True)
                if len(link_text) > 10:
                    name = link_text
        
        # Limpiar nombre - remover 'SAMSUNG' duplicado al inicio si existe
        if name:
            name = re.sub(r'^(SAMSUNG|Samsung)\s*\|\s*', '', name)
        
        # Buscar precio - específico para Éxito
        price = 0.0
        
        # Buscar spans con clase de precio de Éxito
        price_spans = element.select('span[class*="price"]')
        for span in price_spans:
            price_text = span.get_text(strip=True)
            if '$' in price_text:
                parsed = self._parse_exito_price(price_text)
                if 10000 < parsed < 50000000:
                    price = parsed
                    break
        
        # Si no encontramos, buscar cualquier texto con formato de precio
        if price == 0:
            all_text = element.get_text()
            # Buscar todos los precios en formato colombiano (con espacio después de $)
            prices_found = re.findall(r'\$\s*([\d.]+)', all_text)
            for price_str in prices_found:
                parsed = self._parse_exito_price('$' + price_str)
                if 10000 < parsed < 50000000:
                    price = parsed
                    break
        
        # Buscar rating
        rating = None
        rating_elem = element.select_one('[class*="rating"], [class*="Rating"]')
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
        img_elem = element.find('img', src=True)
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src')
            if src:
                image_url = src
        
        return Product(
            name=name[:200] if name else "",
            price=price,
            store=self.store_name,
            category=category,
            rating=rating,
            url=url,
            image_url=image_url
        )
    
    def _parse_exito_price(self, price_text: str) -> float:
        """Parsea precios específicos del formato de Éxito."""
        if not price_text:
            return 0.0
        
        # Remover símbolo de peso y espacios
        cleaned = price_text.replace('$', '').replace(' ', '').strip()
        
        # Remover puntos que son separadores de miles
        cleaned = cleaned.replace('.', '')
        
        # Si hay coma, es separador decimal (raro en Colombia pero por si acaso)
        cleaned = cleaned.replace(',', '.')
        
        try:
            price = float(cleaned)
            # Validar que sea un precio razonable
            if 1000 < price < 100000000:
                return price
            return 0.0
        except ValueError:
            return 0.0
