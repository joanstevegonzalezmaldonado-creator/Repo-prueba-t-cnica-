"""
Repositorio de Productos - Persistencia
"""
import json
import csv
import logging
from pathlib import Path
from typing import List

from ...Domain.Entities import Product
from ...Domain.Interfaces import IProductRepository

logger = logging.getLogger(__name__)


class ProductRepository(IProductRepository):
    """Implementación del repositorio de productos."""
    
    def __init__(self, output_dir: str = "output"):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_products(self, products: List[Product], filename: str) -> str:
        """
        Guarda productos en JSON o CSV según la extensión.
        
        Args:
            products: Lista de productos
            filename: Nombre del archivo (con extensión)
            
        Returns:
            Ruta completa del archivo guardado
        """
        filepath = self._output_dir / filename
        
        if filename.endswith('.json'):
            return self._save_json(products, filepath)
        elif filename.endswith('.csv'):
            return self._save_csv(products, filepath)
        else:
            # Default a JSON
            filepath = filepath.with_suffix('.json')
            return self._save_json(products, filepath)
    
    def _save_json(self, products: List[Product], filepath: Path) -> str:
        """Guarda productos en formato JSON."""
        data = {
            "total_products": len(products),
            "products": [p.to_dict() for p in products]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Guardados {len(products)} productos en {filepath}")
        return str(filepath)
    
    def _save_csv(self, products: List[Product], filepath: Path) -> str:
        """Guarda productos en formato CSV."""
        if not products:
            logger.warning("No hay productos para guardar")
            return str(filepath)
        
        fieldnames = ['name', 'price', 'store', 'category', 'rating', 'url', 'image_url', 'extracted_at']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for product in products:
                writer.writerow(product.to_dict())
        
        logger.info(f"Guardados {len(products)} productos en {filepath}")
        return str(filepath)
    
    def load_products(self, filename: str) -> List[Product]:
        """Carga productos desde un archivo."""
        filepath = self._output_dir / filename
        
        if not filepath.exists():
            logger.error(f"Archivo no encontrado: {filepath}")
            return []
        
        if filename.endswith('.json'):
            return self._load_json(filepath)
        elif filename.endswith('.csv'):
            return self._load_csv(filepath)
        
        return []
    
    def _load_json(self, filepath: Path) -> List[Product]:
        """Carga productos desde JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        products_data = data.get('products', data) if isinstance(data, dict) else data
        return [Product.from_dict(p) for p in products_data]
    
    def _load_csv(self, filepath: Path) -> List[Product]:
        """Carga productos desde CSV."""
        products = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(Product.from_dict(row))
        return products
