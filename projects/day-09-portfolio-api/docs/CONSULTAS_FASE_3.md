# Capa de consulta y composición — Fase 3

> **Estado:** implementada localmente. La Fase 4 posterior consume esta capa desde FastAPI; los límites originales de esta fase siguen sin acoplamiento HTTP.

La Fase 3 separa la carga de datos de las reglas de lectura sobre el catálogo validado de la Fase 2. Sus módulos no escriben fixtures, no acceden a red y no incorporan dependencias adicionales.

## Responsabilidades

| Módulo | Responsabilidad |
|---|---|
| [`src/repository.py`](../src/repository.py) | Carga el catálogo una sola vez mediante el cargador validado y expone entidades de dominio en orden físico. |
| [`src/services.py`](../src/services.py) | Filtra entidades con `public: true`, aplica ordenación v1 y resuelve proyectos por `slug` exacto. |
| [`src/errors.py`](../src/errors.py) | Declara errores de dominio controlados, sin códigos ni respuestas HTTP. |

El repositorio traduce cualquier [`FixtureLoadError`](../src/fixtures.py) a `FixtureSourceError`. El servicio traduce una búsqueda de proyecto público ausente —incluido un registro privado— a `ProjectNotFoundError`. La Fase 4 mapea esos errores a `500` y `404`, respectivamente, en [`src/main.py`](../src/main.py).

## Consultas disponibles

`PortfolioQueryService` ofrece únicamente consultas de dominio:

- `get_profile()` devuelve el perfil único validado;
- `list_projects()` devuelve proyectos públicos;
- `get_project_by_slug(slug)` busca por igualdad exacta;
- `list_skills()` devuelve habilidades públicas;
- `list_experience()` devuelve experiencia pública.

Los resultados son modelos de dominio Pydantic. Los metadatos fuente `public` continúan presentes internamente; la proyección a JSON se realiza únicamente en [`src/schemas.py`](../src/schemas.py) durante la Fase 4.

## Orden v1 aplicado

- Proyectos: destacados primero; después, fecha `published_at` descendente; registros sin fecha al final; finalmente `slug` ascendente.
- Habilidades: `category` ascendente en orden ASCII y `name` ascendente.
- Experiencia: `started_at` descendente; con el mismo inicio, una experiencia vigente antes de una finalizada y luego `ended_at` descendente; finalmente organización y rol ascendentes.

El orden se calcula en cada consulta a partir de los datos públicos. Ni el repositorio ni el servicio modifican el catálogo, listas origen o fixture JSON.

## Verificación local

Desde [`projects/day-09-portfolio-api`](..), con Python 3.11+:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -c "from pathlib import Path; import sys; sys.path.insert(0, 'src'); from fixtures import load_fixture_catalog; catalog = load_fixture_catalog(Path('data/fixtures/portfolio-v1.json')); print(f'validated fixture catalog v{catalog.version}: {catalog.profile.name}')"
```

[`tests/test_queries.py`](../tests/test_queries.py) cubre visibilidad, detalle por `slug` exacto, ausencia controlada, carga única, errores de fuente, ordenación y preservación de la fuente. Las pruebas HTTP, esquemas de respuesta y códigos HTTP de la Fase 4 se documentan en [`HTTP_FASE_4.md`](HTTP_FASE_4.md) y se cubren en [`tests/test_http_api.py`](../tests/test_http_api.py).
