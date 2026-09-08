# Aplicación HTTP pública — Fase 4

> **Estado:** implementada localmente. La aplicación FastAPI expone únicamente las rutas de lectura definidas en el contrato v1 y usa el fixture sintético local como fuente.

La Fase 4 conecta el repositorio y servicio de la Fase 3 con FastAPI. No añade escrituras, autenticación, red externa, variables de entorno ni persistencia adicional.

## Componentes

| Archivo | Responsabilidad |
|---|---|
| [`src/main.py`](../src/main.py) | Crea la aplicación, compone repositorio y servicio, registra rutas y traduce errores controlados. |
| [`src/schemas.py`](../src/schemas.py) | Declara los modelos públicos de respuesta y proyecta entidades de dominio sin campos internos. |
| [`tests/test_http_api.py`](../tests/test_http_api.py) | Verifica rutas, serialización, orden, errores, salud e instancias aisladas. |

`create_app(fixture_path)` permite crear una aplicación aislada para cada fixture de prueba. La aplicación predeterminada usa [`data/fixtures/portfolio-v1.json`](../data/fixtures/portfolio-v1.json).

## Rutas implementadas

| Método | Ruta | Respuesta de éxito |
|---|---|---|
| `GET` | `/health` | `200` con `{ "status": "ok" }` sin cargar el fixture. |
| `GET` | `/api/v1/profile` | `200` con el perfil público. |
| `GET` | `/api/v1/projects` | `200` con `{ "items": [...] }` ordenado. |
| `GET` | `/api/v1/projects/{slug}` | `200` con el detalle del proyecto público. |
| `GET` | `/api/v1/skills` | `200` con `{ "items": [...] }` ordenado. |
| `GET` | `/api/v1/experience` | `200` con `{ "items": [...] }` ordenado. |

Las respuestas se modelan explícitamente y nunca exponen metadatos fuente como `public`. Los campos opcionales sin valor se omiten en lugar de serializarse como `null`.

## Validación y errores

- Un `slug` que no cumple `^[a-z0-9]+(?:-[a-z0-9]+)*$` recibe la validación estándar `422` de FastAPI.
- Un `slug` válido que no identifica un proyecto público, incluido un proyecto privado, recibe `404` con `project_not_found`.
- Un error controlado de carga del fixture recibe `500` con `internal_error`, sin ruta local ni detalle de excepción.
- `/health` permanece disponible aunque el fixture no pueda cargarse, conforme al contrato de salud mínimo.

## Ejecución y verificación

Desde [`projects/day-09-portfolio-api`](..), con Python 3.11+:

```text
python -m pip install -r requirements.txt
python -m uvicorn main:app --app-dir src --reload
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Con el servidor en ejecución, FastAPI publica OpenAPI en `http://127.0.0.1:8000/openapi.json` y la interfaz interactiva en `http://127.0.0.1:8000/docs`.
