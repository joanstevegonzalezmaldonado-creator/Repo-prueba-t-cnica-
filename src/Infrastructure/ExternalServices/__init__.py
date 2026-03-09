"""
Servicios Externos - Estrategias de LLM
"""
from .llm_base import BaseLLMStrategy
from .ollama_strategy import OllamaStrategy
from .lm_studio_strategy import LMStudioStrategy
from .llm_context import LLMContext, create_llm_context

__all__ = [
    "BaseLLMStrategy",
    "OllamaStrategy",
    "LMStudioStrategy", 
    "LLMContext",
    "create_llm_context"
]
