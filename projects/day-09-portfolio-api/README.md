# Día 09 — API de portfolio

> Microproyecto del reto **30 Días, 30 Proyectos**. **Estado: Fases 0 a 6 completadas.** API FastAPI local, pública y de solo lectura, respaldada por fixtures sintéticos; no existe despliegue publicado.

Una API HTTP v1 pequeña y verificable para consultar un perfil profesional, proyectos, habilidades y experiencia sin que un consumidor acceda directamente a los datos fuente. Usa Python 3.11+, FastAPI y Pydantic, y funciona completamente en local sin red, credenciales ni servicios cloud.

## Qué incluye

- Seis rutas `GET` públicas: salud, perfil, proyectos, detalle, habilidades y experiencia.
- Fixture JSON sintético, versionado y validado antes de responder.
- Separación entre fixture de dominio, consultas ordenadas y proyecciones HTTP públicas.
- OpenAPI y documentación interactiva de FastAPI.
- Errores seguros y estables para `404` y `500`, más validación estándar `422`.
- Suite `unittest`, ejemplos HTTP reproducibles y un guion de demo local de 15 segundos.

## Alcance y límites de v1

La API expone únicamente información marcada como pública y solo admite consultas. No incorpora CRUD, autenticación, autorización, base de datos, ORM, paginación, filtros, búsqueda, CORS, telemetría, almacenamiento cloud, frontend ni integraciones externas. Las operaciones `POST`, `PUT`, `PATCH` y `DELETE` no están definidas y reciben `405` en las rutas existentes.

Los datos del fixture son sintéticos y no contienen secretos, direcciones postales, teléfonos, correos, credenciales ni identificadores de cuentas. Los metadatos internos como `public` y los registros privados no se serializan en las respuestas.

## Rutas disponibles

| Método | Ruta | Éxito | Notas |
|---|---|---:|---|
| `GET` | `/health` | `200` | Responde `{ "status": "ok" }` sin cargar el fixture. |
| `GET` | `/api/v1/profile` | `200` | Perfil público único. |
| `GET` | `/api/v1/projects` | `200` | Colección pública ordenada. |
| `GET` | `/api/v1/projects/{slug}` | `200` | Detalle de un proyecto público. |
| `GET` | `/api/v1/skills` | `200` | Habilidades públicas ordenadas. |
| `GET` | `/api/v1/experience` | `200` | Experiencia pública ordenada. |

Las rutas de dominio usan el prefijo fijo `/api/v1`. Los contratos completos de campos, orden, límites y semántica están en [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md); las respuestas reales de referencia están en [`examples/RESPUESTAS_PLANIFICADAS.md`](examples/RESPUESTAS_PLANIFICADAS.md).

## Instalación y ejecución local

Desde [`projects/day-09-portfolio-api`](.):

```text
python -m pip install -r requirements.txt
python -m uvicorn main:app --app-dir src --reload
```

El servidor local escucha, por defecto, en `http://127.0.0.1:8000`.

- OpenAPI JSON: [`http://127.0.0.1:8000/openapi.json`](http://127.0.0.1:8000/openapi.json)
- Interfaz interactiva: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

El parámetro `--app-dir src` es necesario porque los módulos de la aplicación importan desde [`src`](src). Para validaciones puntuales del fixture desde Python también debe añadirse `src` al `PYTHONPATH` o usarse `sys.path.insert(0, 'src')`, tal como muestran las guías de verificación.

## Uso HTTP reproducible

Con el servidor anterior en ejecución, en PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/profile
Invoke-RestMethod http://127.0.0.1:8000/api/v1/projects
Invoke-RestMethod http://127.0.0.1:8000/api/v1/projects/portfolio-api
Invoke-RestMethod http://127.0.0.1:8000/api/v1/skills
Invoke-RestMethod http://127.0.0.1:8000/api/v1/experience
```

Ejemplos de éxito, `404`, `422` y `500`, junto con comandos que conservan el código de estado HTTP, están en [`examples/USO_HTTP_LOCAL.md`](examples/USO_HTTP_LOCAL.md). El demo cronometrado se encuentra en [`assets/DEMO_15S.md`](assets/DEMO_15S.md).

## Errores y privacidad

| Situación | Estado | Forma de respuesta |
|---|---:|---|
| Proyecto público encontrado | `200` | Recurso público validado. |
| `slug` válido ausente o privado | `404` | `ErrorResponse` con `project_not_found`; ambos casos son indistinguibles. |
| `slug` inválido | `422` | Objeto estándar de FastAPI con lista `detail`. |
| Fixture inválido o fallo inesperado | `500` | `ErrorResponse` con `internal_error`, sin trazas ni rutas locales. |
| Escritura en una ruta existente | `405` | Respuesta estándar del framework. |

Los campos opcionales sin valor se omiten; no se publican como `null`. Las respuestas son modelos explícitos de [`src/schemas.py`](src/schemas.py), no modelos de fixture.

## Arquitectura

```text
Cliente HTTP
  -> rutas FastAPI y proyecciones públicas
  -> PortfolioQueryService (visibilidad y orden)
  -> FixtureRepository (carga única)
  -> fixture JSON validado por Pydantic
```

| Componente | Responsabilidad |
|---|---|
| [`src/models.py`](src/models.py) y [`src/fixtures.py`](src/fixtures.py) | Validar el catálogo JSON local. |
| [`src/repository.py`](src/repository.py) | Cargar y conservar el catálogo validado. |
| [`src/services.py`](src/services.py) | Filtrar visibilidad, ordenar y buscar por `slug` exacto. |
| [`src/schemas.py`](src/schemas.py) | Declarar y construir las respuestas públicas. |
| [`src/main.py`](src/main.py) | Componer FastAPI, rutas y límites seguros de error. |

## Pruebas y verificación

Ejecutar desde el directorio del proyecto, una orden cada vez:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -c "import sys; from pathlib import Path; sys.path.insert(0, 'src'); from fixtures import load_fixture_catalog; catalog = load_fixture_catalog(Path('data/fixtures/portfolio-v1.json')); print(f'fixture-valid: v{catalog.version}, projects={len(catalog.projects)}')"
python -c "import sys; sys.path.insert(0, 'src'); from main import app; schema = app.openapi(); print(sorted(schema['paths'])); assert all(set(operations) == {'get'} for operations in schema['paths'].values()); print('openapi-read-only: ok')"
```

Resultado esperado: la suite pasa, la compilación no informa errores, el fixture imprime `fixture-valid: v1, projects=3` y OpenAPI contiene solo operaciones `GET`. La guía completa de calidad y entrega es [`docs/VERIFICACION_FASE_6.md`](docs/VERIFICACION_FASE_6.md); la verificación específica de robustez de Fase 5 se mantiene en [`docs/VERIFICACION_FASE_5.md`](docs/VERIFICACION_FASE_5.md).

## Documentación relacionada

- [`ROADMAP.md`](ROADMAP.md): fases y estado de entrega.
- [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md): contrato HTTP v1.
- [`docs/FIXTURES_FASE_2.md`](docs/FIXTURES_FASE_2.md): formato y seguridad del fixture.
- [`docs/CONSULTAS_FASE_3.md`](docs/CONSULTAS_FASE_3.md): visibilidad y ordenación.
- [`docs/HTTP_FASE_4.md`](docs/HTTP_FASE_4.md): composición FastAPI.
- [`docs/VERIFICACION_FASE_5.md`](docs/VERIFICACION_FASE_5.md): robustez, límites y privacidad.
- [`docs/VERIFICACION_FASE_6.md`](docs/VERIFICACION_FASE_6.md): comprobación de entrega local.

## Limitación vigente

No hay URL desplegada ni configuración de producción. La posible publicación, CORS, configuración de entorno, observabilidad y mantenimiento pertenecen explícitamente a la Fase 7 y no forman parte de esta entrega local.
