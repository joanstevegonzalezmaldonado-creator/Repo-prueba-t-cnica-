"""
Entidad de Respuesta de IA - Capa de Dominio
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AIResponse:
    """Entidad que representa una respuesta del modelo de IA."""
    
    query: str
    response: str
    model: str
    provider: str
    created_at: datetime = field(default_factory=datetime.now)
    tokens_used: Optional[int] = None
    
    def to_markdown(self) -> str:
        """Convierte la respuesta a formato Markdown."""
        return f"""## Consulta
{self.query}

## Respuesta ({self.provider} - {self.model})
{self.response}

---
*Generado el: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "query": self.query,
            "response": self.response,
            "model": self.model,
            "provider": self.provider,
            "created_at": self.created_at.isoformat(),
            "tokens_used": self.tokens_used
        }
