"""
Tests de Integración - Pipeline Completo
"""
import pytest
import tempfile
import os
from pathlib import Path

from src.Application.Services import ApplicationService


class TestIntegrationPipeline:
    """Tests de integración para el pipeline."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Crea un directorio temporal para tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_service_initialization(self, temp_output_dir):
        """Test inicialización del servicio."""
        service = ApplicationService(output_dir=temp_output_dir)
        
        stores = service.get_available_stores()
        providers = service.get_available_providers()
        
        assert len(stores) == 3
        assert "exito" in stores
        assert "ollama" in providers
        assert "lm_studio" in providers
    
    @pytest.mark.skip(reason="Requiere conexión real a tiendas")
    def test_scraping_only(self, temp_output_dir):
        """Test de scraping sin IA."""
        service = ApplicationService(output_dir=temp_output_dir)
        
        result = service.run_scraping_only(
            stores=["exito"],
            category="celulares",
            num_pages=1,
            output_format="json"
        )
        
        assert result is not None
        assert os.path.exists(result.file_path)
    
    @pytest.mark.skip(reason="Requiere Ollama o LM Studio corriendo")
    def test_full_pipeline(self, temp_output_dir):
        """Test del pipeline completo."""
        service = ApplicationService(output_dir=temp_output_dir)
        
        result = service.run_full_pipeline(
            stores=["exito"],
            category="celulares",
            num_pages=1,
            llm_provider="ollama",
            llm_model="llama2",
            output_format="json",
            skip_ai=True  # Skip AI para test
        )
        
        assert result is not None
        assert result.scraping_result is not None
