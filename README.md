# Web Scraper con IA para Tiendas Colombianas

**Autor:** Joan Steven Gonzalez Maldonado

Hice este proyecto para extraer productos de tiendas como Éxito, Jumbo y Falabella, y luego analizar los datos con inteligencia artificial usando Ollama o LM Studio.

---

## Qué hace

- Extrae productos (nombre, precio, URL) de tiendas colombianas
- Analiza los datos con IA local (Ollama o LM Studio)
- Genera un archivo JSON o CSV con los productos
- Crea un resumen en Markdown con el análisis de la IA

---

## Requisitos previos

Antes de empezar necesitas tener instalado:

- **Python 3.10 o superior** - [Descargar aquí](https://www.python.org/downloads/)
- **Google Chrome** - El scraper usa Selenium con Chrome
- **Ollama** (opcional, para análisis con IA) - [Descargar aquí](https://ollama.ai)

---

## Instalación paso a paso

### 1. Clonar el repositorio

Abre una terminal y ejecuta:

```bash
git clone https://github.com/joanstevegonzalezmaldonado-creator/Repo-prueba-t-cnica-.git
cd Repo-prueba-t-cnica-
```

### 2. Crear el entorno virtual

En Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

En Linux/Mac:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Deberías ver `(.venv)` al inicio de tu terminal, eso significa que el entorno está activo.

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto instala BeautifulSoup, Selenium, Requests y las demás librerías necesarias.

### 4. Instalar Ollama (para el análisis con IA)

Si quieres usar el análisis con IA, necesitas Ollama:

1. Descarga Ollama desde https://ollama.ai
2. Instálalo y ábrelo
3. Descarga un modelo ejecutando en terminal:

```bash
ollama pull llama3.2
```

Puedes verificar que está funcionando con:
```bash
ollama list
```

---

## Cómo usar

### Ejecución básica

Para extraer celulares de Éxito y analizarlos con IA:

```bash
python -m src.main --stores exito --category celulares --pages 1 --provider ollama --model llama3.2
```

### Solo scraping (sin IA)

Si no tienes Ollama o no quieres usar IA:

```bash
python -m src.main --stores exito --category celulares --pages 1 --skip-ai
```

### Múltiples tiendas

```bash
python -m src.main --stores exito jumbo --category laptops --pages 2 --skip-ai
```

### Exportar a CSV

```bash
python -m src.main --stores exito --category televisores --format csv --skip-ai
```

---

## Parámetros disponibles

| Parámetro | Qué hace | Valores |
|-----------|----------|---------|
| `--stores` | Tiendas a scrapear | `exito`, `jumbo`, `falabella` |
| `--category` | Categoría de productos | `celulares`, `laptops`, `televisores`, etc. |
| `--pages` | Páginas a extraer por tienda | `1`, `2`, `3`... |
| `--provider` | Proveedor de IA | `ollama`, `lm_studio` |
| `--model` | Modelo de IA | `llama3.2`, `mistral`, etc. |
| `--format` | Formato de salida | `json`, `csv` |
| `--skip-ai` | Omitir análisis de IA | (sin valor) |

---

## Archivos generados

Después de ejecutar, encontrarás en la carpeta `output/`:

- **results.json** - Lista de productos extraídos con nombre, precio, tienda, URL, etc.
- **ai_summary.md** - Análisis generado por la IA (si no usaste `--skip-ai`)

---

## Estructura del proyecto

Usé Clean Architecture para organizar el código:

```
src/
├── Domain/                 # El núcleo del negocio
│   ├── Entities/          # Product y AIResponse
│   ├── Interfaces/        # Contratos que deben cumplir las implementaciones
│   └── ValueObjects/      # Configuraciones y tipos
│
├── Application/           # Casos de uso y lógica de aplicación
│   ├── UseCases/         # ScrapingUseCase, AIAnalysisUseCase
│   ├── DTOs/             # Objetos para transferir datos
│   └── Services/         # Coordinación de casos de uso
│
├── Infrastructure/        # Implementaciones concretas
│   ├── Repositories/     # Los scrapers (Éxito, Jumbo, Falabella)
│   └── ExternalServices/ # Conexión con Ollama y LM Studio
│
└── Presentation/         # Interfaz de usuario
    └── Controllers/      # El CLI que procesa los argumentos
```

---

## Patrones de diseño

Implementé 3 patrones:

### Strategy
Para poder cambiar entre Ollama y LM Studio sin tocar el código. Están en `Infrastructure/ExternalServices/`.

### Factory
Para crear el scraper correcto según la tienda. Está en `Infrastructure/Repositories/scraper_factory.py`.

### Template Method
Define los pasos del scraping (construir URL → obtener HTML → parsear productos). Cada tienda implementa su propia forma de parsear. Está en `Infrastructure/Repositories/base_scraper.py`.

---

## Ejecutar los tests

```bash
pytest tests/ -v
```

---

## Problemas comunes

**El scraper no extrae productos:**
Las tiendas cambian su HTML frecuentemente. Si no funciona, puede que haya que actualizar los selectores en los archivos de cada scraper.

**Ollama da timeout:**
El análisis puede tardar 2-5 minutos dependiendo del modelo. Si da timeout, prueba con un modelo más pequeño:
```bash
ollama pull qwen2.5:0.5b
python -m src.main --stores exito --category celulares --provider ollama --model qwen2.5:0.5b
```

**Error de Chrome/Selenium:**
Asegúrate de tener Google Chrome instalado. El driver se descarga automáticamente.

---

## Tecnologías usadas

- Python 3.10+
- Selenium + BeautifulSoup (scraping)
- Ollama / LM Studio (IA local)
- Clean Architecture
