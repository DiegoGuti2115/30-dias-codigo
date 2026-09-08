# Verificación reproducible — Fase 5

> **Propósito:** comprobar localmente la robustez de la API v1 ya implementada, sin añadir despliegue, red externa, credenciales ni rutas de escritura.

La cobertura de la Fase 5 se concentra en [`tests/test_http_api.py`](../tests/test_http_api.py): contratos de error `404`, `422` y `500`; límites del `slug`; privacidad de las proyecciones JSON; ausencia de valores opcionales serializados como `null`; y mantenimiento del contrato de solo lectura también en OpenAPI.

## Precondiciones

Ejecutar desde [`projects/day-09-portfolio-api`](..), con Python 3.11+ y las dependencias locales instaladas:

```text
python -m pip install -r requirements.txt
```

El proyecto usa exclusivamente el fixture sintético [`data/fixtures/portfolio-v1.json`](../data/fixtures/portfolio-v1.json). No requiere variables de entorno, credenciales, conexión de red ni proveedor cloud.

## Comprobaciones automatizadas

Ejecutar cada comando de forma independiente:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -c "import sys; from pathlib import Path; sys.path.insert(0, 'src'); from fixtures import load_fixture_catalog; catalog = load_fixture_catalog(Path('data/fixtures/portfolio-v1.json')); print(f'fixture-valid: v{catalog.version}, projects={len(catalog.projects)}')"
python -c "import sys; sys.path.insert(0, 'src'); from main import app; schema = app.openapi(); print('routes:', sorted(schema['paths'])); assert all(set(operations) == {'get'} for operations in schema['paths'].values()); print('openapi-read-only: ok')"
```

La primera orden valida todos los escenarios positivos y negativos. Incluye, entre otros:

- `404` idéntico para un proyecto ausente y para uno privado.
- `422` estructurado para mayúsculas, guiones inválidos y el límite superior de 80 caracteres del `slug`; un `slug` válido de 80 caracteres llega al `404` de dominio.
- `500` estable, sin detalles de excepciones ni rutas locales, tanto ante fallo de fixture como ante una excepción inesperada.
- Ausencia de `public`, `profile_public`, datos privados y campos opcionales con valor `null` en todas las respuestas públicas.
- Rechazo `405` de escrituras y especificación OpenAPI limitada a operaciones `GET`.

## Revisión de higiene del cambio

Desde la raíz del repositorio, revisar también:

```text
git diff --check -- projects/day-09-portfolio-api
git status --short -- projects/day-09-portfolio-api
git diff --stat -- projects/day-09-portfolio-api
```

Si el directorio del proyecto todavía no está seguido por Git, `git status --short` puede mostrarlo como no rastreado y `git diff --stat` no tendrá cambios rastreados que resumir. Esa condición del repositorio no modifica la validez de las verificaciones locales.

## Comprobación manual opcional

Para inspección interactiva, iniciar la aplicación local:

```text
python -m uvicorn main:app --app-dir src --reload
```

Después, consultar [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) o [`http://127.0.0.1:8000/openapi.json`](http://127.0.0.1:8000/openapi.json). La comprobación manual no sustituye la suite automatizada.