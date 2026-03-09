"""
Repositorio de Respuestas de IA - Persistencia
"""
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from ...Domain.Entities import AIResponse
from ...Domain.Interfaces import IAIResponseRepository

logger = logging.getLogger(__name__)


class AIResponseRepository(IAIResponseRepository):
    """Implementación del repositorio de respuestas de IA."""
    
    def __init__(self, output_dir: str = "output"):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_responses(self, responses: List[AIResponse], filename: str) -> str:
        """
        Guarda las respuestas en un archivo Markdown.
        
        Args:
            responses: Lista de respuestas de IA
            filename: Nombre del archivo (se forzará .md)
            
        Returns:
            Ruta del archivo guardado
        """
        filepath = self._output_dir / filename
        if not filename.endswith('.md'):
            filepath = filepath.with_suffix('.md')
        
        content = self._generate_markdown(responses)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Guardadas {len(responses)} respuestas en {filepath}")
        return str(filepath)
    
    def _generate_markdown(self, responses: List[AIResponse]) -> str:
        """Genera contenido Markdown con todas las respuestas."""
        lines = [
            "# Análisis de IA - Resultados del Scraping",
            "",
            f"*Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "---",
            ""
        ]
        
        for i, response in enumerate(responses, 1):
            lines.extend([
                f"## Análisis {i}: {response.query[:100]}{'...' if len(response.query) > 100 else ''}",
                "",
                f"**Proveedor:** {response.provider}  ",
                f"**Modelo:** {response.model}  ",
                f"**Fecha:** {response.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "### Respuesta",
                "",
                response.response,
                "",
                "---",
                ""
            ])
        
        lines.extend([
            "## Información del Proceso",
            "",
            f"- **Total de consultas:** {len(responses)}",
            f"- **Proveedor utilizado:** {responses[0].provider if responses else 'N/A'}",
            f"- **Modelo utilizado:** {responses[0].model if responses else 'N/A'}",
        ])
        
        return "\n".join(lines)
