"""
Value Objects de Configuración - Capa de Dominio
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class StoreType(Enum):
    """Tipos de tiendas soportadas."""
    EXITO = "exito"
    JUMBO = "jumbo"
    FALABELLA = "falabella"
    
    @classmethod
    def from_string(cls, value: str) -> "StoreType":
        """Crea un StoreType desde un string."""
        value_lower = value.lower()
        for store in cls:
            if store.value == value_lower:
                return store
        raise ValueError(f"Tienda no soportada: {value}")


class LLMProvider(Enum):
    """Proveedores de LLM soportados."""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    
    @classmethod
    def from_string(cls, value: str) -> "LLMProvider":
        """Crea un LLMProvider desde un string."""
        value_lower = value.lower().replace("-", "_").replace(" ", "_")
        for provider in cls:
            if provider.value == value_lower:
                return provider
        raise ValueError(f"Proveedor LLM no soportado: {value}")


@dataclass(frozen=True)
class ScrapingConfig:
    """Configuración inmutable para el proceso de scraping."""
    
    stores: List[StoreType]
    category: str
    num_pages: int = 2
    output_format: str = "json"  # "json" o "csv"
    
    def __post_init__(self):
        if self.num_pages < 1:
            raise ValueError("El número de páginas debe ser al menos 1")
        if self.output_format not in ["json", "csv"]:
            raise ValueError("Formato de salida debe ser 'json' o 'csv'")


@dataclass(frozen=True)
class AIConfig:
    """Configuración inmutable para el análisis con IA."""
    
    provider: LLMProvider
    model: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    
    def __post_init__(self):
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("La temperatura debe estar entre 0 y 2")
    
    def get_base_url(self) -> str:
        """Obtiene la URL base según el proveedor."""
        if self.base_url:
            return self.base_url
        if self.provider == LLMProvider.OLLAMA:
            return "http://localhost:11434"
        elif self.provider == LLMProvider.LM_STUDIO:
            return "http://localhost:1234"
        return "http://localhost:11434"
