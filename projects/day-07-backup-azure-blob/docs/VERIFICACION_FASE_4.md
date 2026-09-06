# Interfaz y flujo local completo — Fase 4

## Alcance implementado

La Fase 4 expone el núcleo local de la Fase 3 mediante la CLI contratada, sin alterar sus reglas de validación, copia temporal, verificación, publicación ni limpieza:

```text
python src/main.py backup <SOURCE_PATH> <DESTINATION_DIRECTORY> [--azure]
```

El punto de entrada es [`main.py`](../src/main.py). [`run_cli()`](../src/main.py:57) analiza la solicitud, delega una única operación local en [`run_local_backup()`](../src/local_backup.py:83) y traduce su resultado estructurado a salida y código de proceso. No contiene lógica de copia, manifiestos ni acceso a Azure.

## Salidas y códigos aplicados

| Resultado | Salida estándar | Salida de error | Código |
|---|---|---|:---:|
| Backup local correcto | `Local backup verified: <FINAL_PATH>` | Vacía. | `0` |
| Solicitud inválida | Vacía. | Uso accionable de `argparse`. | `2` |
| Fallo local controlado | Vacía. | `Local backup failed: <diagnóstico breve>`. | `1` |
| Interrupción local | Vacía. | Diagnóstico breve sin traza. | `1` |
| `--azure` solicitado | Confirmación local tras publicar. | Diagnóstico explícito de fallback. | `0` |

Las salidas no incluyen hashes, contenido de archivos, rutas temporales, credenciales, variables de entorno ni trazas por defecto. Las rutas finales y las rutas explícitas de entrada permanecen permitidas por el contrato para identificar la operación.

## Fallback de Azure

La opción `--azure` solo expresa la solicitud futura definida en el contrato. Durante esta fase no se lee configuración, no se carga SDK, no se añade dependencia, no se intenta conexión ni se transmite contenido. Si el backup local se publica, la CLI conserva el código `0` y comunica que Azure no fue intentado y que el fallback local queda disponible. La integración aislada continúa reservada para la Fase 5.

## Cobertura

[`tests/test_cli.py`](../tests/test_cli.py) cubre el flujo por subproceso y la frontera directa de la CLI:

- Archivo regular, directorio anidado y directorio vacío.
- Rutas relativas resueltas desde el directorio de ejecución.
- Argumentos incompletos, subcomando desconocido y opción desconocida con código `2`.
- Origen inexistente y fallo local controlado con código `1`, sin traza.
- Conflicto en una segunda ejecución, sin sobrescribir la copia previa ni dejar temporales propios.
- Solicitud `--azure` sin red, configuración ni adaptador remoto, conservando el backup local y el código `0`.
- Interrupción convertida a diagnóstico controlado.

La guía manual reproducible y la demostración basada en fixtures sintéticos están en [`examples/USO.md`](../examples/USO.md).

## Validaciones

Desde [`projects/day-07-backup-azure-blob`](..):

```text
python -m unittest discover -s tests -t . -v
python -m compileall -q src tests
```

También se revisan los JSON de fixtures y referencias, la comparación contra [`local-copy-manifests.json`](../data/expected/local-copy-manifests.json), el alcance del proyecto y `git diff --check`. Los directorios `__pycache__` generados se eliminan tras las comprobaciones.

## Límites y siguiente fase

La CLI no añade restauración, sobrescritura, sincronización, automatización, compresión, configuración ni operación remota. La siguiente fase posible es la Fase 5: decidir y, solo si se valida de manera segura, aislar una integración opcional con Azure Blob sin degradar el backup local.
