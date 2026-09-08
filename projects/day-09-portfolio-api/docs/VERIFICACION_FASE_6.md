# Verificación de entrega local — Fase 6

> **Propósito:** permitir que otra persona ejecute, consulte, pruebe y demuestre la API v1 desde una copia local, sin añadir alcance de despliegue.

La Fase 6 documenta exclusivamente comportamientos ya verificados: rutas `GET`, fixture sintético local, errores seguros, OpenAPI y pruebas. No crea configuración de producción, CORS, autenticación, operaciones de escritura, servicios externos ni una URL pública.

## 1. Preparación limpia

Desde [`projects/day-09-portfolio-api`](..), con Python 3.11+:

```text
python -m pip install -r requirements.txt
```

El único origen de datos es [`data/fixtures/portfolio-v1.json`](../data/fixtures/portfolio-v1.json). No hay archivo `.env` requerido, credenciales, red, cloud ni dependencias fuera de [`requirements.txt`](../requirements.txt).

## 2. Verificación automatizada

Ejecutar cada comando por separado desde el directorio del proyecto:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -c "import sys; from pathlib import Path; sys.path.insert(0, 'src'); from fixtures import load_fixture_catalog; catalog = load_fixture_catalog(Path('data/fixtures/portfolio-v1.json')); print(f'fixture-valid: v{catalog.version}, projects={len(catalog.projects)}')"
python -c "import sys; sys.path.insert(0, 'src'); from main import app; schema = app.openapi(); print('routes:', sorted(schema['paths'])); assert all(set(operations) == {'get'} for operations in schema['paths'].values()); print('openapi-read-only: ok')"
```

Resultados esperados:

- La suite completa finaliza con `OK`.
- La compilación no emite errores.
- El fixture imprime `fixture-valid: v1, projects=3`.
- OpenAPI lista exactamente `/health`, `/api/v1/profile`, `/api/v1/projects`, `/api/v1/projects/{slug}`, `/api/v1/skills` y `/api/v1/experience`; cada operación es `GET`.

La cobertura de robustez de `404`, `422`, `500`, límites, privacidad y rechazos de escritura se explica en [`VERIFICACION_FASE_5.md`](VERIFICACION_FASE_5.md).

## 3. Ejecución e inspección manual

Iniciar la aplicación:

```text
python -m uvicorn main:app --app-dir src --reload
```

Abrir [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) y ejecutar las seis operaciones `GET`, o seguir los comandos de [`examples/USO_HTTP_LOCAL.md`](../examples/USO_HTTP_LOCAL.md). Comprobar como mínimo:

1. `/health` devuelve `200` y `{ "status": "ok" }`.
2. `/api/v1/projects` devuelve `portfolio-api` antes de `log-summary-tool`.
3. `/api/v1/projects/portfolio-api` devuelve el detalle público con `description`.
4. `/api/v1/projects/not-found` devuelve el `404` seguro `project_not_found`.
5. `/api/v1/projects/Portfolio-API` devuelve validación `422` con `detail`.
6. Ninguna respuesta pública contiene `public`, `profile_public`, registros privados o valores `null` opcionales.

Los cuerpos de referencia están en [`examples/RESPUESTAS_PLANIFICADAS.md`](../examples/RESPUESTAS_PLANIFICADAS.md). El guion de grabación breve está en [`assets/DEMO_15S.md`](../assets/DEMO_15S.md).

## 4. Revisión de entrega e higiene

Desde la raíz del repositorio:

```text
git diff --check -- projects/day-09-portfolio-api
git status --short -- projects/day-09-portfolio-api
git diff --stat -- projects/day-09-portfolio-api
```

Revisar también que no se hayan añadido archivos `.env`, secretos, tokens, datos personales, archivos generados, bases de datos, capturas con información sensible ni cambios fuera de [`projects/day-09-portfolio-api`](..). Si el directorio del proyecto aún no está rastreado por Git, `git status --short` puede mostrar `??` y `git diff --stat` no tendrá cambios rastreados que resumir.

## Decisión conservadora

El contrato de [`docs/CONTRATO_API_V1.md`](CONTRATO_API_V1.md) sigue siendo la autoridad para rutas y respuestas. La Fase 6 solo hace consumible y demostrable ese contrato: no modifica [`src/main.py`](../src/main.py), no añade métodos HTTP ni promete disponibilidad fuera de `127.0.0.1`.