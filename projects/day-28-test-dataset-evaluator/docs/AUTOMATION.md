# Automatización e integraciones opcionales

La fase 5 mantiene la validación local como ruta principal. La automatización, las métricas y cualquier publicación externa se construyen a partir de [`ValidationReport`](../src/evaluation_dataset_validator/models/contracts.py:70), por lo que no modifican reglas, contratos de entrada ni el informe JSON canónico.

## Puerta local y CI

Ejecute la misma puerta portátil que usa CI:

```bash
python scripts/precommit_check.py
```

El comando compila [`src`](../src) y [`tests`](../tests), y ejecuta la suite completa con el intérprete activo. El flujo de GitHub Actions en [`ci.yml`](../.github/workflows/ci.yml) instala el proyecto editable y ejecuta exactamente ese comando; no requiere secretos ni servicios remotos.

## Métricas de observabilidad

La CLI puede proyectar el resumen canónico hacia dos formatos locales:

```bash
python -m evaluation_dataset_validator.main data/examples/phase4-valid.json --metrics-format json --metrics-output output/metrics.json
python -m evaluation_dataset_validator.main data/examples/phase4-valid.json --metrics-format prometheus --metrics-output output/metrics.prom
```

- `json`: serializa `is_valid`, conteos base, agregados existentes y cobertura.
- `prometheus`: emite gauges en el formato de exposición de texto; no inicia un servidor ni necesita una dependencia de Prometheus.

Si no se proporciona `--metrics-output`, se deriva una ruta desde `--report`: `.metrics.json` o `.prom`. `--metrics-output` exige un único `--metrics-format` para evitar destinos ambiguos.

## Publicación opcional y fallback

`--publish-webhook URL` publica la misma proyección JSON mediante `POST`. Si no se puede conectar, si el endpoint es inválido o si responde fuera de 2xx, la validación ya finalizada **no cambia su código de salida**: se persiste el mismo payload en `--publish-fallback` (por defecto `output/integration-fallback.json`) y se informa del fallback en consola.

```bash
python -m evaluation_dataset_validator.main data/examples/phase4-valid.json --publish-webhook http://127.0.0.1:1/unavailable --publish-fallback output/fallback.json
```

El adaptador webhook no almacena credenciales, no reintenta y no se usa en pruebas de demostración. Las pruebas sustituyen el publicador por implementaciones locales que fallan de forma controlada; por ello no dependen de red ni de secretos.

## Límites

La publicación webhook es un adaptador HTTP mínimo, no un cliente de una plataforma de evaluación concreta ni un almacenamiento cloud. El fallback local garantiza que una integración externa no impide el informe, las reglas locales ni la reproducibilidad de las pruebas.
