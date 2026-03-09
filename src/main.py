#!/usr/bin/env python
"""
Web Scraper + IA - Punto de entrada principal
Ejecuta el scraping y análisis de productos desde tiendas colombianas

Uso:
    python -m src.main --stores exito alkosto --category celulares --provider ollama --model llama2
    
Ver ayuda completa:
    python -m src.main --help
"""
import sys
from src.Presentation import run_cli

if __name__ == '__main__':
    sys.exit(run_cli())
