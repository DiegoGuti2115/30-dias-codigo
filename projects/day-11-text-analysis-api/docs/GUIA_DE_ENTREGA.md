# Guía de entrega — API de análisis de texto

Esta guía permite instalar, ejecutar, verificar y demostrar la versión 1 desde la raíz de [`projects/day-11-text-analysis-api`](..). La API es local, determinista, sin estado y no necesita servicios externos, variables de entorno ni credenciales.

## Requisitos

- Python 3.11 o superior.
- Una consola PowerShell en Windows.
- Acceso local al directorio del proyecto.

Las dependencias de ejecución se declaran en [`requirements.txt`](../requirements.txt); el perfil de desarrollo y las herramientas de calidad se definen en [`pyproject.toml`](../pyproject.toml).

## Instalación reproducible

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Como alternativa a la instalación editable, puede instalar las dependencias de ejecución con `python -m pip install -r requirements.txt`.

## Ejecución local

Inicie el servidor desde la raíz del proyecto:

```powershell
python -m uvicorn src.main:app --reload
```

Direcciones locales disponibles:

- Documentación interactiva: `http://127.0.0.1:8000/docs`
- Especificación OpenAPI: `http://127.0.0.1:8000/openapi.json`
- Operación pública: `POST http://127.0.0.1:8000/api/v1/analyze`

La única operación pública acepta `application/json` y devuelve `application/json; charset=utf-8`. No hay autenticación, almacenamiento, historial, carga de archivos ni rutas de consulta.

## Demostración rápida

Con el servidor en ejecución, envíe una solicitud JSON UTF-8:

```powershell
$body = @{ text = "La API analiza texto. La API devuelve métricas útiles." } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/analyze" -ContentType "application/json" -Body $body
```

La respuesta coincide con el resultado de referencia [`data/expected/contract-example.json`](../data/expected/contract-example.json). Para una demostración compacta con entrada, llamada y salida esperada, consulte [`assets/DEMO_HTTP.md`](../assets/DEMO_HTTP.md).

## Verificación completa

Ejecute estos comandos desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m mypy src tests
.\.venv\Scripts\python.exe -m compileall -q src tests
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import tomllib; from pathlib import Path; tomllib.loads(Path('pyproject.toml').read_text(encoding='utf-8')); print('TOML validation passed')"
git diff --check -- .
git status --short
```

La suite cubre esquemas, tokenización, métricas, frecuencias, palabras clave, errores HTTP, OpenAPI, límites, fixture versionado y aislamiento de solicitudes. Las advertencias deprecadas que puedan aparecer durante las pruebas proceden de las dependencias FastAPI/Starlette del cliente de pruebas, no de código del proyecto.

## Seguridad y límites

- No use datos personales, confidenciales o de producción como texto de entrada: el servicio no los persiste, pero el usuario controla su entorno de ejecución local.
- El proyecto no requiere ni incluye claves API, contraseñas, tokens o ficheros `.env`.
- Cada solicitud admite entre 1 y 10.000 caracteres Unicode; una cadena solo de espacios es válida y genera métricas lingüísticas nulas.
- El análisis no detecta idioma, sentimiento, significado, gramática ni relevancia semántica.
- No hay rate limiting, autenticación, despliegue productivo, observabilidad avanzada ni persistencia en la versión 1.

## Referencias de entrega

- Contrato público: [`docs/CONTRATO_API_V1.md`](CONTRATO_API_V1.md)
- Decisiones y estado por fases: [`ROADMAP.md`](../ROADMAP.md)
- Guía principal y estructura: [`README.md`](../README.md)
- Fixture de entrada: [`data/fixtures/contract-example.txt`](../data/fixtures/contract-example.txt)
- Resultado esperado: [`data/expected/contract-example.json`](../data/expected/contract-example.json)
