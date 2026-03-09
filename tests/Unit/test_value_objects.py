"""
Tests Unitarios - Value Objects del Dominio
"""
import pytest

from src.Domain.ValueObjects import (
    ScrapingConfig, 
    AIConfig, 
    StoreType, 
    LLMProvider
)


class TestStoreType:
    """Tests para el enum StoreType."""
    
    def test_store_type_values(self):
        """Test valores del enum."""
        assert StoreType.EXITO.value == "exito"
        assert StoreType.ALKOSTO.value == "alkosto"
        assert StoreType.FALABELLA.value == "falabella"
    
    def test_from_string_valid(self):
        """Test creación desde string válido."""
        store = StoreType.from_string("exito")
        assert store == StoreType.EXITO
        
        store = StoreType.from_string("ALKOSTO")
        assert store == StoreType.ALKOSTO
    
    def test_from_string_invalid(self):
        """Test creación desde string inválido."""
        with pytest.raises(ValueError):
            StoreType.from_string("tienda_invalida")


class TestLLMProvider:
    """Tests para el enum LLMProvider."""
    
    def test_provider_values(self):
        """Test valores del enum."""
        assert LLMProvider.OLLAMA.value == "ollama"
        assert LLMProvider.LM_STUDIO.value == "lm_studio"
    
    def test_from_string_valid(self):
        """Test creación desde string válido."""
        provider = LLMProvider.from_string("ollama")
        assert provider == LLMProvider.OLLAMA
        
        provider = LLMProvider.from_string("lm_studio")
        assert provider == LLMProvider.LM_STUDIO
        
        # Variaciones
        provider = LLMProvider.from_string("lm-studio")
        assert provider == LLMProvider.LM_STUDIO
    
    def test_from_string_invalid(self):
        """Test creación desde string inválido."""
        with pytest.raises(ValueError):
            LLMProvider.from_string("chatgpt")


class TestScrapingConfig:
    """Tests para ScrapingConfig."""
    
    def test_create_config(self):
        """Test creación de configuración."""
        config = ScrapingConfig(
            stores=[StoreType.EXITO],
            category="celulares",
            num_pages=3
        )
        
        assert len(config.stores) == 1
        assert config.category == "celulares"
        assert config.num_pages == 3
        assert config.output_format == "json"
    
    def test_config_invalid_pages(self):
        """Test validación de páginas."""
        with pytest.raises(ValueError):
            ScrapingConfig(
                stores=[StoreType.EXITO],
                category="test",
                num_pages=0
            )
    
    def test_config_invalid_format(self):
        """Test validación de formato."""
        with pytest.raises(ValueError):
            ScrapingConfig(
                stores=[StoreType.EXITO],
                category="test",
                output_format="xml"
            )
    
    def test_config_immutable(self):
        """Test inmutabilidad (frozen dataclass)."""
        config = ScrapingConfig(
            stores=[StoreType.EXITO],
            category="test"
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            config.category = "otro"


class TestAIConfig:
    """Tests para AIConfig."""
    
    def test_create_config(self):
        """Test creación de configuración."""
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        
        assert config.provider == LLMProvider.OLLAMA
        assert config.model == "llama2"
        assert config.temperature == 0.7
    
    def test_get_base_url_ollama(self):
        """Test URL base para Ollama."""
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2"
        )
        
        assert config.get_base_url() == "http://localhost:11434"
    
    def test_get_base_url_lm_studio(self):
        """Test URL base para LM Studio."""
        config = AIConfig(
            provider=LLMProvider.LM_STUDIO,
            model="model"
        )
        
        assert config.get_base_url() == "http://localhost:1234"
    
    def test_get_base_url_custom(self):
        """Test URL base personalizada."""
        config = AIConfig(
            provider=LLMProvider.OLLAMA,
            model="llama2",
            base_url="http://custom:8080"
        )
        
        assert config.get_base_url() == "http://custom:8080"
    
    def test_invalid_temperature(self):
        """Test validación de temperatura."""
        with pytest.raises(ValueError):
            AIConfig(
                provider=LLMProvider.OLLAMA,
                model="llama2",
                temperature=3.0
            )
