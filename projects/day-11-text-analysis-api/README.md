# Día 11 — API de análisis de texto

Microproyecto del reto **30 Días, 30 Proyectos** para diseñar una API HTTP local, clara y verificable que reciba texto y devuelva métricas lingüísticas deterministas.

## Estado

Las **Fases 0, 1, 2, 3, 4, 5, 6 y 7** están completadas. El proyecto dispone de documentación de entrega, contrato público, configuración versionada, esquemas Pydantic estrictos, un núcleo de análisis textual puro, una capa HTTP FastAPI funcional y una suite de regresión determinista. Expone exclusivamente `POST /api/v1/analyze`, no persiste textos y no depende de servicios externos.

El alcance está organizado en [`ROADMAP.md`](ROADMAP.md). El contrato público de la versión 1 está definido en [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md) y prevalece sobre la implementación.

## Propósito

Ofrecer un punto de entrada HTTP único para analizar un texto proporcionado por el cliente y devolver un resumen cuantitativo interpretable. La primera versión se centrará en conteos básicos, frecuencia de palabras y palabras clave, sin depender de servicios externos.

## Alcance previsto de la versión 1

La API expone un único endpoint: `POST /api/v1/analyze`.

Tras validar una entrada textual, el análisis devolverá:

- Número total de caracteres.
- Número de caracteres excluyendo espacios en blanco.
- Número de palabras.
- Número de frases.
- Número de párrafos.
- Tiempo estimado de lectura.
- Frecuencia de palabras normalizadas y ordenadas de forma determinista.
- Palabras clave seleccionadas y ordenadas según reglas documentadas.

La representación de solicitud y respuesta, los límites, la normalización, la definición de frase y párrafo, el tratamiento de signos y la política de desempate están definidos en el contrato antes de crear modelos o rutas.

## Fuera de alcance

Para conservar un alcance atómico, la primera versión no incluirá:

- Detección de idioma, análisis de sentimiento, resumen, traducción ni corrección gramatical.
- Modelos de aprendizaje automático, proveedores NLP, APIs cloud ni credenciales.
- Persistencia de textos o resultados, base de datos, caché o colas.
- Autenticación, autorización, usuarios, cuotas ni límites de uso distribuidos.
- Procesamiento de archivos, carga de documentos o interfaz web.
- Despliegue productivo, observabilidad avanzada o internacionalización completa.

## Arquitectura

```text
Cliente HTTP
    ↓
Aplicación FastAPI y ruta POST /api/v1/analyze
    ↓
Esquemas Pydantic de entrada y salida
    ↓
Servicio de análisis (orquestación de métricas)
    ↓
Tokenizador y normalización determinista
    ↓
Cálculo de frecuencias y selección de palabras clave
```

La estructura separa responsabilidades para facilitar cambios y pruebas aisladas:

- [`src/main.py`](src/main.py): aplicación FastAPI, metadatos OpenAPI, ruta HTTP y traducción de errores del contrato.
- [`src/schemas.py`](src/schemas.py): contratos Pydantic estrictos de solicitud, métricas, frecuencias, palabras clave, respuesta y errores.
- [`src/analyzer.py`](src/analyzer.py): orquestación pura de métricas y composición del resultado.
- [`src/tokenizer.py`](src/tokenizer.py): reglas puras de segmentación y normalización textual.
- [`src/keywords.py`](src/keywords.py): palabras vacías y selección determinista de palabras clave.
- [`tests/test_analyzer.py`](tests/test_analyzer.py): pruebas unitarias de métricas, reglas lingüísticas y casos límite.
- [`tests/test_api.py`](tests/test_api.py): pruebas HTTP y de la especificación OpenAPI.
- [`tests/test_integration.py`](tests/test_integration.py): regresiones HTTP de extremo a extremo con fixture, límites, errores e aislamiento de solicitudes.
- [`data/fixtures`](data/fixtures): textos de entrada reproducibles para las pruebas.
- [`data/expected`](data/expected): resultados esperados versionados para regresiones.

## Tecnologías y requisitos

- Python 3.11 o superior.
- FastAPI para la capa HTTP y documentación OpenAPI.
- Pydantic para contratos y validación.
- Uvicorn como servidor ASGI local.
- Pytest y HTTPX para pruebas automatizadas.

Las versiones compatibles de ejecución, pruebas y calidad se declaran en [`requirements.txt`](requirements.txt); los metadatos, configuración de Pytest, Ruff y MyPy están en [`pyproject.toml`](pyproject.toml). No se necesitan secretos, variables de entorno ni integraciones externas para la versión 1.

## Instalación

Desde la raíz de [`projects/day-11-text-analysis-api`](.) cree un entorno virtual e instale las dependencias declaradas:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Para instalar también el perfil de desarrollo definido en [`pyproject.toml`](pyproject.toml), use `python -m pip install -e ".[dev]"`.

## Ejecución local

Inicie la API desde la raíz del proyecto con Uvicorn:

```powershell
python -m uvicorn src.main:app --reload
```

La documentación interactiva está disponible en `http://127.0.0.1:8000/docs` y la especificación OpenAPI en `http://127.0.0.1:8000/openapi.json`. La única operación pública es `POST /api/v1/analyze`; acepta JSON UTF-8 y devuelve JSON UTF-8 conforme a [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md). La instalación, seguridad, verificación y demostración reproducibles están reunidas en [`docs/GUIA_DE_ENTREGA.md`](docs/GUIA_DE_ENTREGA.md).

## Pruebas y calidad

Ejecute la suite desde la raíz del proyecto con:

```powershell
python -m pytest -q
```

Las pruebas cubren métricas normales y límites, normalización, frecuencias, selección de palabras clave, validación, contrato HTTP, OpenAPI y ausencia de estado compartido. Durante el desarrollo, ejecute también:

```powershell
python -m ruff check src tests
python -m mypy src tests
python -m compileall src tests
python -m pip check
```

Ruff y MyPy están declarados para el perfil de desarrollo. Las Fases 3 y 4 incorporan pruebas de esquemas y del núcleo de análisis; la Fase 5 añade pruebas de la capa HTTP y de OpenAPI; y la Fase 6 completa las regresiones de extremo a extremo contra el fixture versionado, los límites de entrada, los errores y el aislamiento entre solicitudes.

## Convenciones de desarrollo

- Usar Python 3.11+ con anotaciones de tipo en todo código que se incorpore después de esta fase.
- Mantener separadas las capas HTTP, esquemas, análisis, tokenización y palabras clave.
- Diseñar cálculos puros, deterministas y sin estado global para facilitar pruebas reproducibles.
- Establecer en el contrato las reglas de texto antes de implementarlas; toda variación pública actualizará [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md).
- Añadir fixtures y resultados esperados antes o junto con cada regla de análisis nueva.
- No añadir dependencias sin una necesidad explícita, justificada y documentada.
- No incluir secretos, credenciales, datos sensibles ni configuraciones específicas de una máquina.
- Ejecutar pruebas y comprobación de sintaxis antes de entregar fases con implementación.

## Criterios de aceptación de la versión 1

La primera versión se considerará aceptada cuando:

1. `POST /api/v1/analyze` esté documentado e implementado conforme a un contrato versionado.
2. Una entrada textual válida produzca todas las métricas básicas acordadas, frecuencias y palabras clave.
3. Las reglas de tokenización, normalización, segmentación y desempate produzcan resultados deterministas.
4. Las entradas inválidas reciban respuestas HTTP coherentes, sin ejecutar el análisis.
5. La suite automatizada cubra flujos correctos, entradas límite y fallos de contrato con fixtures reproducibles.
6. La API pueda instalarse, ejecutarse y verificarse de forma local sin servicios externos ni secretos.
7. La documentación incluya instrucciones verificadas, contrato, decisiones, límites y una demostración breve.

## Estructura del proyecto

```text
projects/day-11-text-analysis-api/
├── assets/
│   ├── DEMO_HTTP.md           Demostración reproducible de la llamada HTTP
│   └── carrusel-linkedin.html Presentación interactiva local de cinco diapositivas
├── data/
│   ├── expected/              Resultados de referencia versionados
│   └── fixtures/              Textos de prueba reproducibles
├── docs/
│   ├── CONTRATO_API_V1.md     Contrato HTTP público de la versión 1
│   └── GUIA_DE_ENTREGA.md     Instalación, verificación, seguridad y entrega
├── src/
│   ├── analyzer.py            Núcleo puro de análisis y composición del resultado
│   ├── keywords.py            Selección determinista de palabras clave
│   ├── main.py                Aplicación FastAPI, ruta y errores HTTP
│   ├── schemas.py             Contratos Pydantic y validación de datos
│   └── tokenizer.py           Normalización y segmentación textual
├── tests/
│   ├── test_analyzer.py       Pruebas unitarias del núcleo de análisis
│   ├── test_api.py            Pruebas de contrato HTTP y OpenAPI
│   ├── test_integration.py    Regresiones HTTP de extremo a extremo
│   └── test_schemas.py        Pruebas de validación y serialización de esquemas
├── .gitignore                 Exclusiones locales de Git
├── pyproject.toml             Metadatos y configuración de calidad
├── README.md                  Guía y alcance del proyecto
├── requirements.txt           Dependencias de ejecución, pruebas y calidad
└── ROADMAP.md                 Plan de desarrollo por fases
```

La capa HTTP delega el análisis en el núcleo local, puro y determinista; no duplica reglas lingüísticas, no almacena textos, no accede a servicios externos y no conserva estado entre solicitudes. Para abrir la presentación local de cinco diapositivas destinada a la demostración del proyecto, use [`assets/carrusel-linkedin.html`](assets/carrusel-linkedin.html) directamente en un navegador; no requiere dependencias ni llamadas de red.

## Decisiones iniciales

- **Un único endpoint de análisis:** concentra el alcance de la API y simplifica el contrato inicial.
- **Procesamiento local y determinista:** elimina dependencias de red, coste, credenciales y resultados variables.
- **Separación por responsabilidades:** evita acoplar reglas lingüísticas a FastAPI y permite probarlas de forma aislada.
- **Contrato antes de código:** define métricas ambiguas antes de implementar y reduce regresiones de comportamiento.
- **Fixtures y resultados esperados versionados:** aportan evidencia reproducible para reglas de texto que evolucionen.

## Roadmap

El desarrollo detallado, sus dependencias y resultados esperados se encuentran en [`ROADMAP.md`](ROADMAP.md).