# Uso local y Azure reproducible — Fase 5

## Requisitos

- Python 3.11 o superior.
- Un origen local admisible: un archivo regular o un directorio regular.
- Un directorio de destino existente y escribible.
- Para el modo local: ninguna instalación adicional, red, cuenta Azure, credencial ni variable de entorno.
- Para `--azure`: instalar [`requirements.txt`](../requirements.txt) y definir localmente las dos variables descritas en [`.env.example`](../.env.example), sin versionar valores.

La interfaz disponible es [`src/main.py`](../src/main.py) y aplica todas las reglas de seguridad del [`CONTRATO.md`](../docs/CONTRATO.md): no sigue enlaces ni junctions, no crea el destino, no sobrescribe conflictos y no modifica el origen.

## Sintaxis

Ejecuta desde la raíz de [`projects/day-07-backup-azure-blob`](..):

```text
python src/main.py backup <SOURCE_PATH> <DESTINATION_DIRECTORY> [--azure]
```

La ruta final se calcula como `<DESTINATION_DIRECTORY>/<SOURCE_BASENAME>`. Debe estar libre antes de ejecutar el comando.

## Demostración local con datos sintéticos

Crea un destino temporal fuera del árbol de fixtures. En PowerShell:

```powershell
$demoDestination = Join-Path $env:TEMP "day07-backup-demo"
New-Item -ItemType Directory -Force $demoDestination | Out-Null
python src/main.py backup data/fixtures/directory-tree $demoDestination
Get-ChildItem -Recurse $demoDestination
```

La salida de éxito tiene este formato estable:

```text
Local backup verified: <DESTINATION_DIRECTORY>\directory-tree
```

El árbol publicado contiene `inventory.txt`, `nested/details.txt` y el directorio vacío `empty-folder`. La copia se valida antes de publicarse mediante tipo de raíz, estructura relativa, tamaño y SHA-256 efímero. Los tamaños y la estructura de referencia se conservan en [`local-copy-manifests.json`](../data/expected/local-copy-manifests.json); los hashes no se muestran ni se almacenan.

## Verificar el resultado

Ejecuta las pruebas locales desde la raíz del proyecto:

```text
python -m unittest discover -s tests -t . -v
python -m compileall -q src tests
```

La suite cubre archivo, directorio anidado, directorio vacío, rutas relativas, errores de entrada, conflictos, limpieza, configuración Azure y el adaptador con dobles sin red.

## Errores y códigos de salida

| Situación | Salida | Código |
|---|---|:---:|
| Copia local publicada y verificada | Confirmación en salida estándar. | `0` |
| Sintaxis, subcomando u opción no válidos | Uso accionable en salida de error. | `2` |
| Ruta no admisible, conflicto, copia, verificación, publicación o interrupción | Diagnóstico local breve en salida de error, sin traza por defecto. | `1` |
| `--azure` sin configuración Azure válida | Diagnóstico remoto breve; no crea contenido local. | `1` |
| Error Azure después de publicar la copia local | Confirmación local y diagnóstico de fallback. | `0` |
| Copia local y Azure correctas | Confirmación de ambos destinos. | `0` |

Una ejecución repetida sobre el mismo origen y destino falla con código `1` porque la ruta final ya existe. Ese comportamiento preserva el backup previo; no es una operación de sincronización ni de sobrescritura.

## Azure Blob opcional

Instala el SDK únicamente si vas a usar la ruta remota:

```text
python -m pip install -r requirements.txt
```

Define `AZURE_STORAGE_CONNECTION_STRING` y `AZURE_STORAGE_CONTAINER_NAME` en el entorno de la sesión. Ambos deben existir y no estar vacíos antes de ejecutar `--azure`; de lo contrario, el comando devuelve `1` sin crear una copia local.

```powershell
$env:AZURE_STORAGE_CONNECTION_STRING = "<valor-no-versionado>"
$env:AZURE_STORAGE_CONTAINER_NAME = "<contenedor-existente>"
python src/main.py backup data/fixtures/regular-file/sample-note.txt $demoDestination --azure
```

El adaptador carga sin sobrescritura: un archivo usa `backups/sample-note.txt`; un directorio usa `backups/<nombre-del-origen>/<ruta-relativa-posix>`. Los directorios vacíos no generan blobs. Cualquier fallo de Azure que ocurra después de la publicación local conserva esa copia y se informa como fallback con código `0`. La suite no realiza tráfico de red; una transferencia con cuenta autorizada es una comprobación manual independiente.
