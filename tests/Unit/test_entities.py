"""
Tests Unitarios - Entidades del Dominio
"""
import pytest
from datetime import datetime

from src.Domain.Entities import Product, AIResponse


class TestProduct:
    """Tests para la entidad Product."""
    
    def test_create_product(self):
        """Test creación básica de producto."""
        product = Product(
            name="iPhone 15",
            price=4500000,
            store="Éxito",
            category="celulares"
        )
        
        assert product.name == "iPhone 15"
        assert product.price == 4500000
        assert product.store == "Éxito"
        assert product.category == "celulares"
        assert product.rating is None
    
    def test_create_product_with_rating(self):
        """Test creación de producto con rating."""
        product = Product(
            name="Samsung Galaxy",
            price=3000000,
            store="Alkosto",
            category="celulares",
            rating=4.5
        )
        
        assert product.rating == 4.5
    
    def test_product_to_dict(self):
        """Test conversión a diccionario."""
        product = Product(
            name="Test Product",
            price=100000,
            store="Test",
            category="test"
        )
        
        data = product.to_dict()
        
        assert data["name"] == "Test Product"
        assert data["price"] == 100000
        assert "extracted_at" in data
    
    def test_product_from_dict(self):
        """Test creación desde diccionario."""
        data = {
            "name": "Test",
            "price": 50000,
            "store": "Test Store",
            "category": "test"
        }
        
        product = Product.from_dict(data)
        
        assert product.name == "Test"
        assert product.price == 50000
    
    def test_product_str(self):
        """Test representación string."""
        product = Product(
            name="Producto",
            price=150000,
            store="Tienda",
            category="cat"
        )
        
        str_repr = str(product)
        
        assert "Producto" in str_repr
        assert "150,000" in str_repr
        assert "Tienda" in str_repr


class TestAIResponse:
    """Tests para la entidad AIResponse."""
    
    def test_create_ai_response(self):
        """Test creación de respuesta de IA."""
        response = AIResponse(
            query="Test query",
            response="Test response",
            model="llama2",
            provider="Ollama"
        )
        
        assert response.query == "Test query"
        assert response.response == "Test response"
        assert response.model == "llama2"
        assert response.provider == "Ollama"
    
    def test_ai_response_to_markdown(self):
        """Test conversión a Markdown."""
        response = AIResponse(
            query="¿Cuál es el precio promedio?",
            response="El precio promedio es $500,000",
            model="llama2",
            provider="Ollama"
        )
        
        md = response.to_markdown()
        
        assert "## Consulta" in md
        assert "precio promedio" in md
        assert "## Respuesta" in md
        assert "Ollama" in md
    
    def test_ai_response_to_dict(self):
        """Test conversión a diccionario."""
        response = AIResponse(
            query="Test",
            response="Result",
            model="model",
            provider="provider"
        )
        
        data = response.to_dict()
        
        assert data["query"] == "Test"
        assert data["response"] == "Result"
        assert "created_at" in data
