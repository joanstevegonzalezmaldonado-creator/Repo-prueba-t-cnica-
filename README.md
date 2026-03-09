# Web Scraper + IA para Tiendas Colombianas

**Autor:** Joan Steven Gonzalez Maldonado

Sistema de web scraping para extraer productos de tiendas colombianas (Éxito, Alkosto, Falabella) con análisis automático usando modelos de IA locales como Ollama o LM Studio.

---

## Qué hace este proyecto

- Extrae productos de las principales tiendas de e-commerce en Colombia
- Soporta Ollama y LM Studio como proveedores de IA (intercambiables)
- Genera archivos JSON/CSV con los productos
- Crea un resumen con análisis de IA en Markdown
- Implementa 3 patrones de diseño: Strategy, Factory y Template Method

---

## Estructura del proyecto

```
├── src/
│   ├── Domain/                    # Capa de dominio
│   │   ├── Entities/              # Product, AIResponse
│   │   ├── Interfaces/            # Contratos abstractos
│   │   └── ValueObjects/          # Configuraciones
│   │
│   ├── Application/               # Casos de uso
│   │   ├── UseCases/              # ScrapingUseCase, AIAnalysisUseCase
│   │   ├── DTOs/                  # Objetos de transferencia
│   │   └── Services/              # Servicios de aplicación
│   │
│   ├── Infrastructure/            # Implementaciones concretas
│   │   ├── Repositories/          # Scrapers (Éxito, Alkosto, Falabella)
│   │   └── ExternalServices/      # Estrategias LLM (Ollama, LM Studio)
│   │
│   └── Presentation/              # Interfaz CLI
│       └── Controllers/           # Controlador de línea de comandos
│
├── tests/                         # Tests unitarios e integración
├── output/                        # Archivos generados
├── config.json                    # Configuración opcional
└── requirements.txt               # Dependencias
```

---

## Patrones de diseño implementados

### 1. Strategy Pattern
Permite cambiar el proveedor de IA (Ollama o LM Studio) sin modificar el código. Las estrategias están en `Infrastructure/ExternalServices/`.

### 2. Factory Pattern  
Crea el scraper correcto según la tienda seleccionada. Implementado en `Infrastructure/Repositories/scraper_factory.py`.

### 3. Template Method Pattern
Define el algoritmo base de scraping. Cada tienda implementa sus propios selectores. Ver `Infrastructure/Repositories/base_scraper.py`.

---

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/web-scraper-ia-colombia.git
cd web-scraper-ia-colombia
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

Activar en Windows:
```bash
.venv\Scripts\activate
```

Activar en Linux/Mac:
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar Ollama (para el análisis con IA)

Descargar desde: https://ollama.ai

Una vez instalado, descargar un modelo:
```bash
ollama pull llama3.2
```

Verificar que está corriendo:
```bash
ollama list
```

---

## Cómo usar

### Ejecución básica

```bash
python -m src.main --stores exito --category celulares --pages 1 --provider ollama --model llama3.2
```

### Parámetros disponibles

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `--stores` | Tiendas a scrapear | `exito`, `alkosto`, `falabella` |
| `--category` | Categoría de productos | `celulares`, `laptops`, `televisores` |
| `--pages` | Número de páginas | `1`, `2`, `3` |
| `--provider` | Proveedor de IA | `ollama`, `lm_studio` |
| `--model` | Modelo de IA | `llama3.2`, `mistral` |
| `--format` | Formato de salida | `json`, `csv` |
| `--skip-ai` | Omitir análisis de IA | (sin valor) |

### Ejemplos

Scrapear múltiples tiendas:
```bash
python -m src.main --stores exito alkosto --category laptops --pages 2 --provider ollama --model llama3.2
```

Solo scraping sin IA:
```bash
python -m src.main --stores exito --category celulares --pages 1 --skip-ai
```

Exportar a CSV:
```bash
python -m src.main --stores falabella --category televisores --format csv --skip-ai
```

Usar LM Studio en lugar de Ollama:
```bash
python -m src.main --stores exito --category celulares --provider lm_studio --model local-model
```

---

## Archivos generados

Después de ejecutar, encontrarás en la carpeta `output/`:

- `results.json` - Lista de productos extraídos
- `ai_summary.md` - Análisis generado por la IA

---

## Configuración alternativa

Puedes usar un archivo `config.json` en lugar de parámetros CLI:

```json
{
    "stores": ["exito", "alkosto"],
    "category": "celulares",
    "pages": 2,
    "format": "json",
    "provider": "ollama",
    "model": "llama3.2",
    "skip_ai": false
}
```

Ejecutar con config:
```bash
python -m src.main --config config.json
```

---

## Ejecutar tests

```bash
pytest tests/ -v
```

---

## Requisitos

- Python 3.10+
- Google Chrome instalado
- Ollama o LM Studio (para análisis con IA)

---

## Notas

- El scraping puede tardar unos segundos por página debido a que las tiendas usan JavaScript
- El análisis con IA puede demorar 1-3 minutos dependiendo del modelo y cantidad de productos
- Si Ollama da timeout, intenta con un modelo más pequeño como `qwen2.5:0.5b`

## 📤 Archivos de Salida

### results.json / results.csv
Contiene los productos extraídos:
```json
{
    "total_products": 50,
    "products": [
        {
            "name": "iPhone 15 Pro Max 256GB",
            "price": 5499000,
            "store": "Éxito",
            "category": "celulares",
            "rating": 4.8,
            "url": "https://...",
            "extracted_at": "2026-03-08T10:30:00"
        }
    ]
}
```

### ai_summary.md
Análisis generado por la IA:
```markdown
# Análisis de IA - Resultados del Scraping

## Análisis 1: Resume los resultados obtenidos...

**Proveedor:** Ollama
**Modelo:** llama2

### Respuesta
El análisis de los 50 productos extraídos muestra...
- Precio promedio: $2,500,000
- Rango de precios: $500,000 - $6,000,000
...
```

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src

# Solo tests unitarios
pytest tests/Unit/

# Tests específicos
pytest tests/Unit/test_scraper_factory.py -v
```

## 🔧 Decisiones Técnicas

1. **Clean Architecture**: Separación clara de responsabilidades en capas independientes.

2. **Strategy Pattern**: Elegido para proveedores de IA porque permite:
   - Cambiar entre Ollama y LM Studio sin modificar código
   - Agregar nuevos proveedores fácilmente
   - Testing con mocks

3. **Factory Pattern**: Elegido para scrapers porque:
   - Encapsula la lógica de creación
   - Permite agregar nuevas tiendas sin modificar clientes
   - Centraliza la configuración de scrapers

4. **Template Method Pattern**: Elegido para el flujo de scraping porque:
   - Define un algoritmo común (fetch → parse → save)
   - Permite personalizar pasos específicos por tienda
   - Reutiliza código común (manejo de errores, delays)

5. **Requests + BeautifulSoup**: Elegido sobre Selenium/Playwright porque:
   - Más ligero y rápido
   - Suficiente para sitios con contenido estático
   - Menor complejidad de setup

## 📊 Presentación (7 minutos)

1. **Demostración del Scraper** (2 min)
   - Ejecutar con múltiples tiendas
   - Mostrar logs de progreso

2. **Archivos Generados** (1 min)
   - Abrir `results.json`
   - Mostrar estructura de datos

3. **Análisis de IA** (2 min)
   - Mostrar `ai_summary.md`
   - Explicar consultas realizadas

4. **Decisiones Técnicas** (2 min)
   - Patrones de diseño utilizados
   - Arquitectura limpia
   - Manejo de errores

## 📝 Notas Importantes

- El scraping a tiendas reales puede fallar si cambian su estructura HTML
- Ollama o LM Studio deben estar corriendo antes de ejecutar el análisis
- Se respetan delays entre requests para evitar bloqueos
- Los errores no detienen la ejecución (se registran y continúa)
