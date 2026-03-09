"""
Controlador CLI - Punto de entrada por línea de comandos
"""
import argparse
import logging
import sys
from typing import List, Optional

from ...Application.Services import ApplicationService


def setup_logging(verbose: bool = False):
    """Configura el sistema de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reducir verbosidad de requests/urllib3
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos CLI."""
    parser = argparse.ArgumentParser(
        description='Web Scraper + IA - Extrae productos de tiendas colombianas y analiza con IA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  # Scraping completo con análisis IA usando Ollama
  python -m src.main --stores exito alkosto --category celulares --pages 2 --provider ollama --model llama2
  
  # Scraping con LM Studio
  python -m src.main --stores falabella --category laptops --provider lm_studio --model local-model
  
  # Solo scraping (sin IA)
  python -m src.main --stores exito --category televisores --skip-ai
  
  # Formato CSV
  python -m src.main --stores alkosto --category audifonos --format csv --provider ollama --model mistral
  
  # Con archivo de configuración
  python -m src.main --config config.json
"""
    )
    
    # Argumentos de scraping
    parser.add_argument(
        '--stores', '-s',
        nargs='+',
        choices=['exito', 'alkosto', 'falabella'],
        default=['exito'],
        help='Tiendas a scrapear (default: exito)'
    )
    
    parser.add_argument(
        '--category', '-c',
        type=str,
        default='celulares',
        help='Categoría de productos a buscar (default: celulares)'
    )
    
    parser.add_argument(
        '--pages', '-p',
        type=int,
        default=2,
        help='Número de páginas por tienda (default: 2)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv'],
        default='json',
        help='Formato de salida (default: json)'
    )
    
    # Argumentos de IA
    parser.add_argument(
        '--provider',
        choices=['ollama', 'lm_studio'],
        default='ollama',
        help='Proveedor de LLM (default: ollama)'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='llama2',
        help='Modelo de IA a usar (default: llama2)'
    )
    
    parser.add_argument(
        '--skip-ai',
        action='store_true',
        help='Omitir análisis de IA'
    )
    
    # Otros argumentos
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output',
        help='Directorio de salida (default: output)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Archivo de configuración JSON (sobreescribe otros argumentos)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose con más información de debug'
    )
    
    parser.add_argument(
        '--list-stores',
        action='store_true',
        help='Lista las tiendas disponibles y sale'
    )
    
    parser.add_argument(
        '--list-providers',
        action='store_true',
        help='Lista los proveedores de IA disponibles y sale'
    )
    
    return parser


def load_config_file(config_path: str) -> dict:
    """Carga configuración desde archivo JSON."""
    import json
    from pathlib import Path
    
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_cli():
    """Ejecuta la aplicación desde CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Crear servicio
    service = ApplicationService(output_dir=args.output)
    
    # Comandos de lista
    if args.list_stores:
        print("Tiendas disponibles:")
        for store in service.get_available_stores():
            print(f"  - {store}")
        return 0
    
    if args.list_providers:
        print("Proveedores de IA disponibles:")
        for provider in service.get_available_providers():
            print(f"  - {provider}")
        return 0
    
    # Cargar configuración desde archivo si se especifica
    config = {}
    if args.config:
        try:
            config = load_config_file(args.config)
            logger.info(f"Configuración cargada desde: {args.config}")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return 1
    
    # Obtener parámetros (config file tiene prioridad)
    stores = config.get('stores', args.stores)
    category = config.get('category', args.category)
    num_pages = config.get('pages', args.pages)
    output_format = config.get('format', args.format)
    provider = config.get('provider', args.provider)
    model = config.get('model', args.model)
    skip_ai = config.get('skip_ai', args.skip_ai)
    
    # Mostrar configuración
    print("\n" + "=" * 60)
    print("CONFIGURACIÓN")
    print("=" * 60)
    print(f"Tiendas: {', '.join(stores)}")
    print(f"Categoría: {category}")
    print(f"Páginas: {num_pages}")
    print(f"Formato: {output_format}")
    print(f"Proveedor IA: {provider}")
    print(f"Modelo: {model}")
    print(f"Análisis IA: {'No' if skip_ai else 'Sí'}")
    print("=" * 60 + "\n")
    
    try:
        # Ejecutar pipeline
        result = service.run_full_pipeline(
            stores=stores,
            category=category,
            num_pages=num_pages,
            llm_provider=provider,
            llm_model=model,
            output_format=output_format,
            skip_ai=skip_ai
        )
        
        # Mostrar resumen
        print("\n" + result.to_summary())
        
        return 0 if result.scraping_result.success else 1
        
    except KeyboardInterrupt:
        logger.info("\nEjecución cancelada por el usuario")
        return 130
    except Exception as e:
        logger.error(f"Error durante la ejecución: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_cli())
