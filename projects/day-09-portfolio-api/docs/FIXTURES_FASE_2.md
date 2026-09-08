# Fixtures y validación de dominio — Fase 2

> **Estado:** validación local implementada. Las Fases 3 y 4 posteriores añadieron consultas, ordenación y transporte HTTP; esta fase conserva el límite de validación de la fuente.

La Fase 2 incorpora una fuente de datos local, sintética y determinista en [`data/fixtures/portfolio-v1.json`](../data/fixtures/portfolio-v1.json), junto con modelos Pydantic y un cargador validador en [`src/models.py`](../src/models.py) y [`src/fixtures.py`](../src/fixtures.py).

## Formato de la fuente

El fixture es un único documento JSON UTF-8 con versión fija `1`:

```text
portfolio-v1.json
├── version: 1
├── profile_public: true
├── profile
├── projects[]
├── skills[]
└── experience[]
```

Los registros de colecciones tienen el metadato fuente `public`. Este campo controla la proyección pública y no pertenece al contrato HTTP. Las Fases 3 y 4 filtran explícitamente los registros con `public: false` y no serializan ese metadato en respuestas.

## Validaciones aplicadas

Los modelos rechazan campos no declarados y validan las restricciones de [`CONTRATO_API_V1.md`](CONTRATO_API_V1.md):

- textos no vacíos y límites máximos;
- `slug` de proyecto con la gramática v1 y longitud de 1 a 80;
- fechas mensuales `YYYY-MM` con mes válido;
- enlaces HTTP(S) absolutos;
- enumeraciones de estado de proyecto y categoría de habilidad;
- listas de tecnologías no vacías, limitadas y únicas sin distinguir mayúsculas/minúsculas;
- `ended_at >= started_at`;
- unicidad de `slug` entre proyectos públicos;
- unicidad de `(category, name)` entre habilidades públicas, sin distinguir mayúsculas/minúsculas.

El cargador convierte errores de lectura, JSON inválido o incumplimiento del dominio en `FixtureLoadError`, sin publicar detalles de la ruta ni el contenido fuente.

## Datos de demo

Los datos son deterministas y locales. Incluyen valores públicos de ejemplo consistentes con [`RESPUESTAS_PLANIFICADAS.md`](../examples/RESPUESTAS_PLANIFICADAS.md), además de algunos registros fuente no públicos para probar el metadato de visibilidad en fases posteriores.

No hay secretos, credenciales, datos de contacto, direcciones postales, correos, cuentas externas ni servicios de red.

## Verificación local

Desde [`projects/day-09-portfolio-api`](..), con Python 3.11+:

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -c "import sys; from pathlib import Path; sys.path.insert(0, 'src'); from fixtures import load_fixture_catalog; catalog=load_fixture_catalog(Path('data/fixtures/portfolio-v1.json')); print(catalog.version)"
```

La suite [`tests/test_fixtures.py`](../tests/test_fixtures.py) comprueba carga repetible del fixture válido, restricciones de campos, fechas, enlaces, cronología, unicidad y errores controlados de carga.

## Límite de fase

La Fase 2 termina en el modelo de dominio validado. La carga no conserva estado global, no ordena colecciones, no busca por `slug`, no filtra registros ni genera objetos de respuesta. Estas responsabilidades se implementaron después en la Fase 3 y se documentan en [`CONSULTAS_FASE_3.md`](CONSULTAS_FASE_3.md). La Fase 4 añade endpoints, servidor HTTP y documentación OpenAPI, descritos en [`HTTP_FASE_4.md`](HTTP_FASE_4.md).
