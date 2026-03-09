"""
Entidad de Producto - Capa de Dominio
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """Entidad que representa un producto extraído del scraping."""
    
    name: str
    price: float
    store: str
    category: str
    rating: Optional[float] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    extracted_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "name": self.name,
            "price": self.price,
            "store": self.store,
            "category": self.category,
            "rating": self.rating,
            "url": self.url,
            "image_url": self.image_url,
            "extracted_at": self.extracted_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Crea una instancia desde un diccionario."""
        extracted_at = data.get("extracted_at")
        if isinstance(extracted_at, str):
            extracted_at = datetime.fromisoformat(extracted_at)
        elif extracted_at is None:
            extracted_at = datetime.now()
            
        return cls(
            name=data.get("name", ""),
            price=float(data.get("price", 0)),
            store=data.get("store", ""),
            category=data.get("category", ""),
            rating=data.get("rating"),
            url=data.get("url"),
            image_url=data.get("image_url"),
            extracted_at=extracted_at
        )
    
    def __str__(self) -> str:
        rating_str = f" - Rating: {self.rating}" if self.rating else ""
        return f"{self.name} - ${self.price:,.0f} ({self.store}){rating_str}"
