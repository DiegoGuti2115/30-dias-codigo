# Día 04 — Analizador de logs

> Microproyecto del reto **30 Días, 30 Proyectos**.

## Estado

Primera versión completada. La herramienta analiza de forma local un único archivo UTF-8 en formato `common` o `jsonl`, normaliza los eventos válidos, produce un resumen determinista y, opcionalmente, lista los eventos `ERROR` y `CRITICAL`.

El alcance, decisiones y criterios de la entrega están en [`ROADMAP.md`](ROADMAP.md). El comportamiento contractual de formatos, errores y códigos está en [`docs/CONTRATO.md`](docs/CONTRATO.md). Los casos sintéticos disponibles están inventariados en [`docs/ESCENARIOS.md`](docs/ESCENARIOS.md).

## Requisitos e instalación

- Python 3.11 o superior.
- No hay dependencias externas: [`requirements.txt`](requirements.txt) se mantiene vacío de forma intencional.
- No se necesitan red, credenciales, configuración ni servicios externos.

Desde la raíz de este proyecto, comprueba la versión disponible:

```text
python --version
```

## Ejecución

La interfaz acepta un único comando:

```text
python src/main.py analyze <LOG_PATH> --format <common|jsonl> [--errors]
```

Ejemplos con los fixtures locales:

```text
python src/main.py analyze data/fixtures/common-valid.log --format common
python src/main.py analyze data/fixtures/jsonl-valid.jsonl --format jsonl --errors
```

`--format` es obligatorio y no hay detección automática. `--errors` añade el reporte de eventos `ERROR` y `CRITICAL` en su orden físico de entrada. El resumen muestra ruta, formato, líneas leídas, eventos válidos, líneas inválidas, los cinco conteos de severidad y hasta tres mensajes frecuentes; los empates de frecuencia respetan la primera aparición.

Los ejemplos con resultado y código esperado están en [`examples/USO.md`](examples/USO.md). El recurso de demostración listo para consulta local está en [`assets/demo-common-valid.txt`](assets/demo-common-valid.txt).

## Formatos admitidos

### `common`

Cada línea válida contiene marca temporal ISO 8601, nivel y mensaje no vacío:

```text
2026-09-01T08:30:00Z INFO Servicio iniciado
```

Los niveles aceptados son `DEBUG`, `INFO`, `WARNING`, `ERROR` y `CRITICAL`, sin distinguir mayúsculas de minúsculas en la entrada.

### `jsonl`

Cada línea no vacía debe ser un objeto JSON independiente con `timestamp`, `level` y `message` como cadenas válidas. Las claves adicionales se conservan internamente como metadatos, pero no se agregan ni se muestran en la v1:

```json
{"timestamp":"2026-09-01T08:31:04Z","level":"error","message":"No se pudo conectar","service":"api"}
```

Consulta las reglas completas en [`docs/CONTRATO.md`](docs/CONTRATO.md).

## Resultados, errores y códigos de salida

| Situación | Salida | Código |
|---|---|:---:|
| Análisis válido, incluso con líneas inválidas | Resumen en salida estándar. | `0` |
| Argumentos incompletos o formato no permitido | Ayuda de `argparse` en salida de error. | `2` |
| Ruta inexistente, directorio, archivo no UTF-8 o lectura fallida | Error breve y accionable en salida de error. | `1` |
| Archivo vacío o sin eventos válidos | Error de análisis en salida de error, sin resumen parcial. | `1` |

Las líneas inválidas se cuentan, pero su contenido y diagnóstico no se imprimen para evitar exponer datos potencialmente sensibles. Los errores previsibles no muestran trazas.

## Límites de la v1

- Procesa un único archivo local por ejecución y lo consume secuencialmente, línea a línea.
- No admite autodetección de formato, directorios, globs, entrada estándar ni varios archivos.
- No modifica la entrada ni genera archivos de salida.
- No incluye filtros temporales, umbrales configurables, exportación, monitorización, alertas ni integración externa.
- Solo acepta UTF-8 y los cinco niveles de severidad definidos por el contrato.

## Pruebas y comprobación reproducible

Todos los datos de prueba son sintéticos y están incluidos localmente. Desde una copia limpia de este directorio, ejecuta:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

La suite cubre parsing secuencial, formatos, severidades, Unicode, resultados de referencia, salida determinista, argumentos, rutas, UTF-8 y códigos de salida. Las referencias estructuradas viven en [`data/expected`](data/expected) y los logs de entrada en [`data/fixtures`](data/fixtures).

## Estructura

- [`src`](src): modelos, parsers, análisis, presentación y CLI.
- [`tests`](tests): pruebas unitarias e integración real mediante proceso CLI.
- [`data/fixtures`](data/fixtures): entradas sintéticas válidas e inválidas.
- [`data/expected`](data/expected): agregados de referencia reproducibles.
- [`docs`](docs): contrato y escenarios de aceptación.
- [`examples`](examples): comandos de uso verificables.
- [`assets`](assets): recurso local de demostración.
