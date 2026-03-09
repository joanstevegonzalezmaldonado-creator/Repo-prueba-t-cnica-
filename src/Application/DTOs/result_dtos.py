"""
DTOs - Data Transfer Objects para la capa de aplicación
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ScrapingResultDTO:
    """DTO para resultados de scraping."""
    
    total_products: int
    products_by_store: dict
    file_path: str
    execution_time: float
    errors: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        return self.total_products > 0


@dataclass
class AIAnalysisResultDTO:
    """DTO para resultados del análisis de IA."""
    
    provider: str
    model: str
    queries_executed: int
    file_path: str
    execution_time: float
    is_available: bool = True
    error_message: Optional[str] = None


@dataclass
class PipelineResultDTO:
    """DTO para el resultado completo del pipeline."""
    
    scraping_result: ScrapingResultDTO
    ai_result: Optional[AIAnalysisResultDTO]
    total_execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_summary(self) -> str:
        """Genera un resumen del resultado."""
        lines = [
            "=" * 60,
            "RESUMEN DE EJECUCIÓN",
            "=" * 60,
            f"Fecha: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Tiempo total: {self.total_execution_time:.2f} segundos",
            "",
            "SCRAPING:",
            f"  - Productos extraídos: {self.scraping_result.total_products}",
            f"  - Archivo generado: {self.scraping_result.file_path}",
        ]
        
        for store, count in self.scraping_result.products_by_store.items():
            lines.append(f"  - {store}: {count} productos")
        
        if self.scraping_result.errors:
            lines.append(f"  - Errores: {len(self.scraping_result.errors)}")
        
        if self.ai_result:
            lines.extend([
                "",
                "ANÁLISIS IA:",
                f"  - Proveedor: {self.ai_result.provider}",
                f"  - Modelo: {self.ai_result.model}",
                f"  - Consultas ejecutadas: {self.ai_result.queries_executed}",
                f"  - Archivo generado: {self.ai_result.file_path}",
            ])
            
            if not self.ai_result.is_available:
                lines.append(f"  - ADVERTENCIA: {self.ai_result.error_message}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
