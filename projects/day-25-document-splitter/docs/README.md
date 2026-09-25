# Document Splitter

CLI local para validar un documento, extraer su texto, normalizarlo, dividirlo en fragmentos trazables y guardar un resultado JSON reproducible.

## Alcance del MVP

Procesa **un archivo por ejecución** con formato TXT (UTF-8), PDF con texto seleccionable o DOCX. No necesita credenciales, red, nube ni base de datos.

- PDF escaneado, cifrado o corrupto: se rechaza; OCR no forma parte del MVP.
- DOCX: se extraen párrafos con texto; tablas y elementos avanzados no se procesan.
- La fragmentación es por caracteres, no por tokens.
- El procesamiento de directorios y la salida JSONL quedan fuera del alcance.

## Requisitos e instalación

- Python 3.11 o superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

También se puede instalar el paquete en modo editable:

```powershell
python -m pip install -e .
```

## Uso

```powershell
python -m document_splitter.main --help
python -m document_splitter.main ruta/al/documento.txt
python -m document_splitter.main ruta/al/manual.pdf --chunk-size 1000 --overlap 150 --output output/manual.json
```

Argumentos:

- `source`: ruta de un archivo `.txt`, `.pdf` o `.docx`.
- `--chunk-size`: máximo recomendado de caracteres por fragmento; valor predeterminado `1000`.
- `--overlap`: caracteres que se repiten entre fragmentos; valor predeterminado `150`. Debe ser mayor o igual que cero y menor que `--chunk-size`.
- `--output`: destino JSON opcional. Si se omite, se usa `output/<nombre-del-archivo>.json` desde el directorio actual.

La CLI crea los directorios padres del destino cuando no existen y **no sobrescribe** resultados existentes. Especifica otra ruta o elimina el resultado anterior para repetir una ejecución.

## Ejemplo reproducible

Desde la raíz del proyecto, el fixture TXT incluido permite ejecutar el flujo completo sin crear entradas permanentes:

```powershell
python -m document_splitter.main tests/fixtures/sample.txt --chunk-size 30 --overlap 5 --output output/sample-result.json
Get-Content output/sample-result.json
Remove-Item output/sample-result.json
```

La consola informa el número de fragmentos y la ruta absoluta del resultado. El comando no muestra el contenido del documento.

## Contrato JSON

La salida se codifica como UTF-8, tiene formato legible y es determinista para los mismos bytes de entrada, parámetros y texto extraído.

```json
{
  "source": "manual.pdf",
  "document_id": "sha256:...",
  "chunk_size": 1000,
  "overlap": 150,
  "chunks": [
    {
      "id": "sha256:...-0",
      "index": 0,
      "text": "Contenido del fragmento.",
      "start_char": 0,
      "end_char": 250
    }
  ]
}
```

- `source` contiene solo el nombre del archivo, no una ruta dependiente del equipo.
- `document_id` es el SHA-256 de los bytes originales del archivo.
- `id` es `<document_id>-<index>`.
- `index` comienza en `0` y permite reconstruir el orden.
- `start_char` y `end_char` son rangos semiabiertos sobre el texto normalizado: `text == normalized[start_char:end_char]`.
- La página no se incluye: los extractores actuales no proporcionan una correspondencia fiable entre caracteres normalizados y páginas.

## Códigos de salida y errores

| Código | Situación |
| --- | --- |
| `0` | Ejecución correcta (o invocación sin `source`). |
| `2` | Error de validación: ruta, extensión, tamaño, archivo vacío o parámetros. |
| `3` | Error de extracción: formato corrupto, PDF no extraíble/protegido o TXT no UTF-8. |
| `4` | Error al calcular el hash o al escribir el resultado. |

La validación limita los documentos a 25 MiB, comprueba que la ruta sea un archivo regular y rechaza extensiones no admitidas antes de la extracción. Los errores se escriben en `stderr` y no exponen el texto completo del documento.

## Desarrollo y verificación

```powershell
python -m pytest -q
python -m document_splitter.main --help
python -m compileall -q src
git diff --check
```

Las pruebas cubren validación, extracción de los tres formatos, normalización, límites de fragmentación, solapamiento, rangos, hash, JSON, conflictos de salida y el flujo CLI con TXT.

## Arquitectura

```text
Archivo -> validación -> extractor -> normalización -> fragmentador
        -> resultado trazable -> JSON local
```

- [`validators/`](../src/document_splitter/validators/): archivo y parámetros.
- [`extractors/`](../src/document_splitter/extractors/): adaptadores TXT, PDF y DOCX.
- [`processors/`](../src/document_splitter/processors/): normalización conservadora.
- [`chunkers/`](../src/document_splitter/chunkers/): límites, solapamiento e índices.
- [`services/`](../src/document_splitter/services/): composición del resultado.
- [`utils/`](../src/document_splitter/utils/): hash y escritura JSON segura.

Consulta [`ARCHITECTURE.md`](ARCHITECTURE.md) para las decisiones de diseño y [`ROADMAP.md`](ROADMAP.md) para el alcance entregado.
