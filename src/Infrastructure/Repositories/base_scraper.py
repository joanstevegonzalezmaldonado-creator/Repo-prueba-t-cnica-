"""
Scraper Base con Selenium
Define el esqueleto del algoritmo de scraping (Template Method)
"""
import logging
import time
import re
from abc import abstractmethod
from typing import List, Optional
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from ...Domain.Entities import Product
from ...Domain.Interfaces import IProductScraper

logger = logging.getLogger(__name__)


class BaseScraper(IProductScraper):
    """
    Clase base abstracta que implementa el patrón Template Method.
    Usa Selenium para manejar páginas con JavaScript.
    """
    
    def __init__(self):
        self._driver: Optional[webdriver.Chrome] = None
        self._delay_between_requests = 3  # segundos
        self._page_load_wait = 10  # segundos para esperar carga de página
    
    def _init_driver(self) -> webdriver.Chrome:
        """Inicializa el driver de Chrome con opciones optimizadas."""
        if self._driver is not None:
            return self._driver
            
        chrome_options = Options()
        # Ejecutar en modo headless (sin ventana visible)
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Deshabilitar imágenes para cargar más rápido
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Driver de Chrome inicializado correctamente")
            return self._driver
        except Exception as e:
            logger.error(f"Error inicializando Chrome driver: {e}")
            raise
    
    def _close_driver(self):
        """Cierra el driver de forma segura."""
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
    
    # Template Method - Algoritmo principal
    def scrape_category(self, category: str, num_pages: int = 2) -> List[Product]:
        """
        TEMPLATE METHOD: Define el esqueleto del algoritmo de scraping.
        Los pasos específicos son implementados por las subclases.
        """
        all_products: List[Product] = []
        
        logger.info(f"Iniciando scraping de {self.store_name} - Categoría: {category}")
        
        try:
            # Inicializar driver
            self._init_driver()
            
            for page in range(1, num_pages + 1):
                try:
                    # Paso 1: Construir URL (hook method)
                    url = self.get_category_url(category, page)
                    logger.info(f"Página {page}/{num_pages}: {url}")
                    
                    # Paso 2: Obtener HTML con Selenium
                    html_content = self._fetch_page(url)
                    if not html_content:
                        logger.warning(f"No se pudo obtener contenido de página {page}")
                        continue
                    
                    # Paso 3: Parsear productos (hook method)
                    products = self.parse_products(html_content, category)
                    
                    if products:
                        all_products.extend(products)
                        logger.info(f"Extraídos {len(products)} productos de página {page}")
                    else:
                        logger.warning(f"No se encontraron productos en página {page}")
                    
                    # Paso 4: Delay entre requests
                    if page < num_pages:
                        self._wait_between_requests()
                        
                except Exception as e:
                    # No detenemos la ejecución ante errores
                    logger.error(f"Error en página {page}: {e}")
                    continue
        
        finally:
            # Siempre cerrar el driver
            self._close_driver()
        
        logger.info(f"Total extraído de {self.store_name}: {len(all_products)} productos")
        return all_products
    
    # Métodos de soporte
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Obtiene el contenido HTML de una página usando Selenium.
        Espera a que el JavaScript cargue el contenido.
        """
        try:
            self._driver.get(url)
            
            # Esperar a que la página cargue
            time.sleep(2)  # Espera inicial
            
            # Esperar elementos específicos o timeout
            self._wait_for_products()
            
            # Scroll para cargar productos lazy-loaded
            self._scroll_page()
            
            return self._driver.page_source
            
        except TimeoutException:
            logger.warning(f"Timeout esperando carga de {url}")
            return self._driver.page_source  # Retornar lo que haya cargado
        except WebDriverException as e:
            logger.error(f"Error de WebDriver: {e}")
            return None
        except Exception as e:
            logger.error(f"Error obteniendo página {url}: {e}")
            return None
    
    def _wait_for_products(self):
        """Espera a que los productos se carguen. Puede ser sobrescrito."""
        try:
            # Esperar por elementos comunes de productos
            WebDriverWait(self._driver, self._page_load_wait).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "div[class*='product'], article[class*='product'], div[class*='card'], div[class*='item']"))
            )
        except TimeoutException:
            logger.debug("Timeout esperando productos, continuando...")
    
    def _scroll_page(self):
        """Hace scroll para cargar productos lazy-loaded."""
        try:
            # Scroll gradual
            for i in range(3):
                self._driver.execute_script(f"window.scrollTo(0, {(i+1) * 1000});")
                time.sleep(0.5)
            # Volver arriba
            self._driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
        except Exception:
            pass
    
    def _wait_between_requests(self) -> None:
        """Espera entre requests para evitar bloqueos."""
        time.sleep(self._delay_between_requests)
    
    def _clean_price(self, price_text: str) -> float:
        """
        Limpia y convierte un texto de precio a número.
        Maneja formatos como: $1.234.567, $1,234,567, 1234567
        """
        if not price_text:
            return 0.0
        
        # Eliminar todo excepto números y puntos/comas
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        
        # Manejar formato colombiano (1.234.567) vs americano (1,234,567)
        if cleaned.count('.') > 1:
            # Formato colombiano con múltiples puntos como separador de miles
            cleaned = cleaned.replace('.', '')
        elif '.' in cleaned and ',' in cleaned:
            # Formato mixto, asumir punto como miles y coma como decimal
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # Solo comas, asumir como separador de miles
            cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def _clean_rating(self, rating_text: str) -> Optional[float]:
        """Limpia y convierte un texto de rating a número."""
        if not rating_text:
            return None
        
        # Buscar números con decimales
        match = re.search(r'(\d+[.,]?\d*)', rating_text)
        if match:
            try:
                return float(match.group(1).replace(',', '.'))
            except ValueError:
                pass
        return None
    
    def _create_soup(self, html_content: str) -> BeautifulSoup:
        """Crea un objeto BeautifulSoup para parsear HTML."""
        return BeautifulSoup(html_content, 'html.parser')
    
    # Hook methods
    def before_scraping(self) -> None:
        """Hook: Ejecutado antes de iniciar el scraping."""
        pass
    
    def after_scraping(self, products: List[Product]) -> List[Product]:
        """Hook: Ejecutado después del scraping. Permite post-procesamiento."""
        return products
