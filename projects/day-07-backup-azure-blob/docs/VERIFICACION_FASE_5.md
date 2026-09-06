# Verificación — Fase 5: Azure Blob opcional

## Alcance comprobado

La Fase 5 añade [`azure_blob.py`](../src/azure_blob.py), un adaptador remoto aislado. No importa `azure-storage-blob` al cargar el programa: el SDK se importa solo en una solicitud `--azure` configurada. Por tanto, el flujo local no necesita dependencias, credenciales ni red.

La política estricta aprobada valida antes de ejecutar el núcleo local que `AZURE_STORAGE_CONNECTION_STRING` y `AZURE_STORAGE_CONTAINER_NAME` existen y no están vacías. Si falla esa validación, la CLI devuelve `1`, escribe un diagnóstico seguro en error estándar y no crea temporales ni una copia final.

Después de una publicación local correcta, los errores del proveedor se transforman en un fallback: se conserva la copia local, se imprime un diagnóstico remoto breve y el código global es `0`. El adaptador no sobrescribe ni elimina blobs.

## Convención remota comprobada

- Archivo: `backups/<SOURCE_BASENAME>`.
- Directorio: `backups/<SOURCE_BASENAME>/<RELATIVE_POSIX_PATH>` para cada archivo regular.
- Directorio sin archivos: cero blobs; no se crean marcadores.
- Cada llamada de carga usa `overwrite=False`.

## Ejecución local

Desde la raíz del proyecto:

```text
python -B -m unittest discover -s tests -t . -v
python -B -m compileall -q src tests
```

[`tests/test_azure_blob.py`](../tests/test_azure_blob.py) usa una fábrica inyectable y clientes falsos para comprobar nombres, contenido, ausencia de sobrescritura, directorios vacíos, configuración y errores de proveedor sin SDK ni red. [`tests/test_cli.py`](../tests/test_cli.py) comprueba que la configuración ausente no modifica el destino y que los resultados remoto correcto/fallido preservan los contratos de salida.

## Comprobación operativa del entorno

La revisión no sensible del 2026-09-04 confirmó que `azure-storage-blob` está disponible y que `az account show --only-show-errors --output none` termina correctamente. En ese momento, las variables contractuales `AZURE_STORAGE_CONNECTION_STRING` y `AZURE_STORAGE_CONTAINER_NAME` no estaban disponibles, por lo que no se realizó una carga real. Una sesión autenticada de Azure CLI no sustituye ese protocolo contractual y las alternativas, incluida identidad administrada, siguen aplazadas en [`docs/CONTRATO.md`](CONTRATO.md).

## Transferencia real comprobada

El 2026-09-06, desde el directorio del proyecto y con la configuración contractual disponible únicamente en la sesión local, se ejecutó:

```powershell
$runId = Get-Date -Format "yyyyMMddHHmmss"
$demoDestination = Join-Path $env:TEMP "day07-backup-real-$runId"
New-Item -ItemType Directory -Force $demoDestination | Out-Null
python src/main.py backup data/fixtures/regular-file/sample-note.txt $demoDestination --azure
```

La CLI confirmó una copia local verificada en un directorio temporal y una publicación remota correcta de un blob. La evidencia no incluye cadena de conexión, identidad, suscripción, cuenta, contenedor ni rutas de datos reales. Esta ejecución confirma la ruta autorizada de la v1: configuración externa mediante las dos variables de entorno, carga no sobrescribible y éxito comunicado por la CLI.

No hay restauración, lectura de objetos ni limpieza remota en v1. No copie secretos, respuestas del proveedor, nombres de cuenta, nombres de contenedor no aprobados ni rutas de datos reales a documentación, pruebas o control de versiones.
