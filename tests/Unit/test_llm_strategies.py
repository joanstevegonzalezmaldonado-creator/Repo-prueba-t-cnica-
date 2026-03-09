"""
Tests Unitarios - Estrategias LLM
"""
import pytest
from unittest.mock import Mock, patch

from src.Domain.ValueObjects import AIConfig, LLMProvider
from src.Infrastructure.ExternalServices import (
    OllamaStrategy,
    LMStudioStrategy,
    LLMContext,
    create_llm_context
)


class TestOllamaStrategy:
    """Tests para OllamaStrategy (Patrón Strategy)."""
    
    def test_provider_name(self):
        """Test nombre del proveedor."""
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        strategy = OllamaStrategy(config)
        
        assert strategy.provider_name == "Ollama"
        assert strategy.model_name == "llama2"
    
    def test_invalid_provider(self):
        """Test error con proveedor incorrecto."""
        config = AIConfig(
            provider=LLMProvider.LM_STUDIO,
            model="model"
        )
        
        with pytest.raises(ValueError):
            OllamaStrategy(config)
    
    @patch('requests.get')
    def test_is_available_true(self, mock_get):
        """Test disponibilidad cuando Ollama está corriendo."""
        mock_get.return_value = Mock(status_code=200)
        
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        strategy = OllamaStrategy(config)
        
        assert strategy.is_available() is True
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_is_available_false(self, mock_get):
        """Test disponibilidad cuando Ollama no está corriendo."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        strategy = OllamaStrategy(config)
        
        assert strategy.is_available() is False


class TestLMStudioStrategy:
    """Tests para LMStudioStrategy (Patrón Strategy)."""
    
    def test_provider_name(self):
        """Test nombre del proveedor."""
        config = AIConfig(
            provider=LLMProvider.LM_STUDIO,
            model="local-model"
        )
        strategy = LMStudioStrategy(config)
        
        assert strategy.provider_name == "LM Studio"
        assert strategy.model_name == "local-model"
    
    def test_invalid_provider(self):
        """Test error con proveedor incorrecto."""
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="model"
        )
        
        with pytest.raises(ValueError):
            LMStudioStrategy(config)


class TestLLMContext:
    """Tests para LLMContext (Contexto del Patrón Strategy)."""
    
    def test_create_context_ollama(self):
        """Test creación de contexto con Ollama."""
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        context = LLMContext(config)
        
        assert context.get_current_provider() == "Ollama"
    
    def test_create_context_lm_studio(self):
        """Test creación de contexto con LM Studio."""
        config = AIConfig(
            provider=LLMProvider.LM_STUDIO,
            model="model"
        )
        context = LLMContext(config)
        
        assert context.get_current_provider() == "LM Studio"
    
    def test_set_strategy(self):
        """Test cambio de estrategia en tiempo de ejecución."""
        config_ollama = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        config_lm = AIConfig(
            provider=LLMProvider.LM_STUDIO,
            model="model"
        )
        
        context = LLMContext(config_ollama)
        assert context.get_current_provider() == "Ollama"
        
        new_strategy = LMStudioStrategy(config_lm)
        context.set_strategy(new_strategy)
        assert context.get_current_provider() == "LM Studio"
    
    def test_create_llm_context_factory(self):
        """Test factory function."""
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        context = create_llm_context(config)
        
        assert isinstance(context, LLMContext)
        assert context.get_current_provider() == "Ollama"
