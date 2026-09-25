# Roadmap — Document Splitter

## Objetivo del MVP

Entregar en un máximo de tres horas una CLI local que reciba un archivo TXT, PDF con texto o DOCX, extraiga su contenido, lo divida en fragmentos con solapamiento y guarde un JSON trazable. No requiere credenciales, nube ni base de datos.

## Alcance y supuestos

- Entrada: un archivo por ejecución (`.txt`, `.pdf`, `.docx`).
- PDF compatible: documento con texto extraíble; un PDF escaneado se rechaza con un mensaje claro.
- Fragmentación: por caracteres, intentando respetar párrafos, oraciones y espacios.
- Salida: un archivo JSON local con metadatos y lista ordenada de fragmentos.
- Límite inicial recomendado: 25 MB por documento.
- El procesamiento de directorios, OCR, API y fragmentación por tokens quedan fuera del MVP.

## Fases y prioridades

| Fase | Prioridad | Objetivo | Tareas | Dependencias | Entregable | Criterio de aceptación |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Base | P0 | Ejecutar una CLI mínima | Crear `requirements.txt`, paquete Python, comando y configuración de argumentos | Python 3.11+ | CLI que acepta ruta, tamaño y solapamiento | `python -m document_splitter.main --help` funciona |
| 2. Validación | P0 | Rechazar entradas incorrectas pronto | Comprobar existencia, extensión, tamaño, vacío y `overlap < chunk_size` | Fase 1 | Validador y pruebas | Los casos inválidos terminan con mensaje y código distinto de cero |
| 3. Extracción | P0 | Obtener texto ordenado | Implementar extractores TXT, PDF con PyMuPDF y DOCX con python-docx | Fase 2 | Selector de extractor y fixtures | Un fixture de cada formato devuelve texto no vacío y en orden |
| 4. Fragmentación | P0 | Crear fragmentos útiles | Normalizar espacios, cortar por párrafo/oración/espacio, aplicar solapamiento e índices | Fase 3 | Fragmentador y pruebas | Ningún fragmento supera el límite salvo palabra indivisible; índices consecutivos |
| 5. Resultado | P0 | Guardar salida trazable | Calcular SHA-256, crear `chunk_id`, escribir JSON y resumen por consola | Fase 4 | `output/<archivo>.json` | Cada fragmento incluye origen, índice, rangos y parámetros usados |
| 6. Cierre | P0 | Demostrar calidad básica | Añadir pruebas de fragmentador, validador y flujo TXT; documentar uso | Fases 1–5 | README, tests y demo con fixture | `pytest` pasa y la guía permite reproducir el resultado |

## Estado de la Fase 0 — Base del proyecto

**Estado: completada el 25/09/2026.** Esta fase cubre únicamente la preparación indicada en el bloque `0:00–0:20`: estructura mínima ejecutable, empaquetado, dependencia de pruebas y contrato de argumentos. No incluye validación de documentos, extracción, fragmentación ni generación de resultados.

- [x] Creado [`pyproject.toml`](../pyproject.toml) con distribución `src/` y requisito Python 3.11+.
- [x] Creado [`requirements.txt`](../requirements.txt) con `pytest`; PyMuPDF y `python-docx` se incorporarán en la fase de extracción.
- [x] Creado el paquete [`src/document_splitter/__init__.py`](../src/document_splitter/__init__.py) y el punto de entrada [`src/document_splitter/main.py`](../src/document_splitter/main.py).
- [x] Definido el contrato CLI: argumento opcional `source` y opciones `--chunk-size`, `--overlap` y `--output`, con valores documentados de 1000 y 150 caracteres.
- [x] Preparada la configuración de pruebas en [`pytest.ini`](../pytest.ini) y pruebas de contrato de CLI en [`tests/test_main.py`](../tests/test_main.py).
- [x] Creado [`.gitignore`](../.gitignore) para cachés Python, entradas, temporales y resultados locales.
- [x] Verificado `python -m pip install -e .`, `python -m pytest -q`, `python -m document_splitter.main --help`, `python -m compileall -q src` y `git diff --check`.

**Pendiente y deliberadamente fuera de Fase 0:** comprobaciones de existencia, extensión, tamaño y coherencia de parámetros (Fase 1); dependencias y adaptadores PDF/DOCX (Fase 2); y cualquier lectura, fragmentación o escritura de documentos. La CLI acepta los argumentos como contrato público, pero aún no procesa `source`.

## Estado de la Fase 1 — Validación de entrada

**Estado: completada el 25/09/2026.** La CLI valida una solicitud con documento antes de cualquier extracción o generación de salida y devuelve el código `2` para errores de validación.

- [x] Implementado [`validators/document.py`](../src/document_splitter/validators/document.py) con la excepción `DocumentValidationError` y el modelo `ValidatedDocument`.
- [x] Validada existencia de ruta, tipo archivo regular, extensión permitida (`.txt`, `.pdf`, `.docx` sin distinguir mayúsculas), archivo no vacío y límite de 25 MiB.
- [x] Validada la coherencia de fragmentación: `chunk_size > 0`, `overlap >= 0` y `overlap < chunk_size`.
- [x] Integrada la validación en [`main.py`](../src/document_splitter/main.py); el CLI comunica el error por `stderr` sin mostrar contenido del archivo.
- [x] Añadidas pruebas de rutas inexistentes, directorios, extensiones no permitidas, archivos vacíos, límite de tamaño, parámetros límite y códigos de salida en [`tests/test_validator.py`](../tests/test_validator.py) y [`tests/test_main.py`](../tests/test_main.py).
- [x] Verificado que las entradas inválidas terminan con mensaje y código distinto de cero; la ejecución válida se limita a validar y aún no lee ni procesa contenido.

**Decisión técnica:** la comprobación de extensión es una lista permitida inicial y no sustituye la inspección del formato del archivo. La detección de PDF/DOCX inválido y la lectura de contenido se implementarán con los extractores de la Fase 2. La ruta se resuelve en el resultado validado para que las fases posteriores trabajen con una ubicación canónica.

**Siguiente dependencia:** la Fase 2 puede consumir `ValidatedDocument` para seleccionar el extractor y añadir PyMuPDF y `python-docx`. No se ha adelantado funcionalidad de extracción, normalización, fragmentación ni escritura JSON.

## Estado de la Fase 2 — Extracción de texto

**Estado: completada el 25/09/2026.** Tras validar la entrada, la CLI selecciona un extractor por extensión y confirma únicamente la cantidad de texto extraído. La normalización, fragmentación y salida JSON permanecen fuera de esta fase.

- [x] Añadidos [`PyMuPDF`](../requirements.txt) y [`python-docx`](../requirements.txt) como dependencias de extracción, declaradas también en [`pyproject.toml`](../pyproject.toml).
- [x] Implementada la interfaz común y los errores tipados en [`extractors/base.py`](../src/document_splitter/extractors/base.py).
- [x] Implementada la lectura UTF-8 no vacía para TXT en [`extractors/txt.py`](../src/document_splitter/extractors/txt.py), manteniendo el texto y su orden.
- [x] Implementada la extracción de PDF página a página en [`extractors/pdf.py`](../src/document_splitter/extractors/pdf.py). Los PDF corruptos, protegidos o sin texto extraíble informan un error claro; OCR sigue fuera del MVP.
- [x] Implementada la extracción de párrafos no vacíos y ordenados de DOCX en [`extractors/docx.py`](../src/document_splitter/extractors/docx.py). Tablas y elementos avanzados no se procesan en esta fase.
- [x] Implementado el selector central por extensión en [`extractors/registry.py`](../src/document_splitter/extractors/registry.py).
- [x] Integrada la extracción en [`main.py`](../src/document_splitter/main.py), conservando el código `2` para validación y usando el código `3` para errores de extracción.
- [x] Añadidos fixtures reales TXT, PDF y DOCX y pruebas de orden, contenido no vacío, selector y archivos corruptos en [`tests/test_extractors.py`](../tests/test_extractors.py); la CLI también cubre el resultado de extracción.
- [x] Verificado `python -m pip install -e .` y `python -m pytest -q` (`30 passed`).

**Pendiente y deliberadamente fuera de Fase 2:** normalización, fragmentación con solapamiento, hashes, metadatos de fragmentos y escritura JSON. La CLI no imprime el contenido extraído ni genera archivos de salida en esta fase.

## Estado de la Fase 3 — Normalización y fragmentación

**Estado: completada el 25/09/2026.** La CLI normaliza de forma conservadora el texto extraído y genera fragmentos ordenados en memoria. Aún no persiste fragmentos ni incorpora hashes, rangos o metadatos de salida.

- [x] Implementada la normalización en [`processors/normalizer.py`](../src/document_splitter/processors/normalizer.py): normaliza saltos de línea, espacios horizontales y líneas vacías redundantes sin reordenar texto.
- [x] Implementado [`chunkers/text.py`](../src/document_splitter/chunkers/text.py) con `TextChunk`, índices consecutivos y corte por caracteres.
- [x] Aplicada la prioridad de corte: párrafo, oración, espacio y corte seguro; una palabra indivisible puede superar `chunk_size`.
- [x] Aplicado solapamiento por caracteres con progreso garantizado entre fragmentos y validación defensiva para llamadas directas.
- [x] Integrada la fragmentación en [`main.py`](../src/document_splitter/main.py) después de la extracción. Los códigos `2` y `3` de validación y extracción se conservan; una ejecución correcta comunica la cantidad de fragmentos sin mostrar texto ni escribir JSON.
- [x] Añadidas pruebas de Unicode, espacios y saltos irregulares, prioridad de límites, solapamiento, palabra larga, texto vacío, parámetros inválidos, límites e índices en [`tests/test_chunker.py`](../tests/test_chunker.py), además de actualizar la prueba del flujo CLI.
- [x] Verificado `python -m pytest -q` (`41 passed`).

**Pendiente y deliberadamente fuera de Fase 3:** SHA-256, identificadores de fragmento, rangos de caracteres persistidos, página, serialización JSON y escritura en `output/`; corresponden a la Fase 4 de resultados.

## Estado de la Fase 4 — Resultado trazable

**Estado: completada el 25/09/2026.** Tras extraer, normalizar y fragmentar, la CLI construye un resultado determinista y lo persiste como JSON local sin sobrescribir resultados existentes.

- [x] Añadidos los modelos inmutables `DocumentResult` y `ResultChunk` en [`models.py`](../src/document_splitter/models.py) para definir el contrato de salida estable.
- [x] Conservados los índices consecutivos de la Fase 3 y añadidos `start_char` y `end_char` relativos al texto normalizado en [`chunkers/text.py`](../src/document_splitter/chunkers/text.py).
- [x] Implementado `document_id` como SHA-256 de los bytes originales del archivo y `chunk_id` determinista con formato `<document_id>-<index>` en [`utils/hashing.py`](../src/document_splitter/utils/hashing.py) y [`services/results.py`](../src/document_splitter/services/results.py).
- [x] Implementada serialización JSON UTF-8 estable, salida predeterminada `output/<archivo>.json`, creación de directorios y escritura atómica sin sobrescritura en [`utils/files.py`](../src/document_splitter/utils/files.py).
- [x] Integrada la creación y persistencia del resultado en [`main.py`](../src/document_splitter/main.py). Los errores de hash o escritura devuelven código `4`; los códigos `2` y `3` para validación y extracción se mantienen.
- [x] Añadidas pruebas de hashes deterministas, metadatos, índices, rangos, serialización, lectura JSON, ruta por defecto, conflictos de escritura y flujo CLI en [`tests/test_results.py`](../tests/test_results.py), [`tests/test_chunker.py`](../tests/test_chunker.py) y [`tests/test_main.py`](../tests/test_main.py).

**Contrato aplicado:** `source` contiene exclusivamente el nombre del archivo para evitar rutas dependientes del entorno; `document_id` identifica los bytes de entrada; `chunks` se mantiene ordenado por `index` y cada fragmento contiene `id`, `index`, `text`, `start_char` y `end_char`. La página se omite porque la interfaz actual de extractores no expone una correspondencia de caracteres por página; no se infiere información no disponible.

**Fuera de la Fase 4:** OCR, procesamiento de directorios, JSONL, fragmentación por tokens, API, bases de datos y enriquecimiento adicional de metadatos.

## Estado de la Fase 5 — Cierre y demostración

**Estado: completada el 25/09/2026.** El MVP queda documentado y cubierto por una suite reproducible, conservando el flujo local de un único archivo y el contrato JSON de la Fase 4.

- [x] Actualizada la guía de uso en [`README.md`](README.md): instalación, argumentos, ruta de salida predeterminada, contrato JSON, códigos de salida, limitaciones y comandos de verificación.
- [x] Documentado un flujo reproducible con el fixture TXT incluido, incluyendo inspección y limpieza del JSON de demostración.
- [x] Añadida una prueba end-to-end del fixture TXT documentado en [`tests/test_main.py`](../tests/test_main.py), que comprueba JSON legible, orden e integración CLI.
- [x] Mantenida la cobertura de validación, extractores, normalización, fragmentación, solapamiento, rangos, hash, serialización, conflicto de escritura y códigos de error de las fases previas.
- [x] Verificado `python -m pytest -q`, `python -m document_splitter.main --help`, `python -m compileall -q src` y `git diff --check`.

**Resultado:** la guía permite reproducir el flujo completo del MVP sin dependencias de red ni artefactos persistentes; no se incorporan capacidades posteriores al MVP.

## Orden de ejecución sugerido (tres horas)

| Tiempo | Actividad | Resultado verificable |
| --- | --- | --- |
| 0:00–0:20 | Estructura, dependencias y CLI | Comando de ayuda operativo |
| 0:20–0:45 | Validación y modelo de salida | Errores de entrada cubiertos por pruebas |
| 0:45–1:25 | TXT y fragmentador | Flujo completo sobre un TXT de fixture |
| 1:25–2:00 | PDF y DOCX | Un fixture por formato extraído correctamente |
| 2:00–2:25 | JSON, hash y metadatos | Salida inspeccionable en `output/` |
| 2:25–2:50 | Pruebas, errores y README | Ejecución reproducible |
| 2:50–3:00 | Demo y corrección final | Comando de ejemplo completado |

## Contrato de salida MVP

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

El orden se reconstruye con `index`; `document_id` permite relacionar todos los fragmentos con el archivo original. La página no se serializa en el MVP actual porque los extractores no exponen una correspondencia fiable entre el texto normalizado y las páginas de origen.

## Riesgos técnicos y mitigación

| Riesgo | Impacto | Mitigación para la entrega |
| --- | --- | --- |
| PDF escaneado o cifrado | No hay texto extraíble | Detectar texto vacío/error y explicar que OCR no está incluido |
| PDF con columnas | Orden de lectura imperfecto | Documentar limitación y priorizar extracción por página |
| Fragmento sin separador | Corte poco natural | Buscar párrafo, oración y espacio antes del corte estricto |
| Archivo muy grande | Consumo de memoria/tiempo | Rechazar sobre el límite configurable |
| DOCX con elementos complejos | Contenido parcial | Extraer párrafos; tablas y elementos avanzados quedan documentados como mejora |
| Dependencia externa falla | Instalación bloqueada | Mantener salida y fragmentación con librería estándar para TXT; PDF/DOCX son dependencias explícitas |

## Posterior al MVP

1. Procesar directorios y escribir JSONL para corpus grandes.
2. Añadir estrategia por palabras, oraciones o tokens.
3. Soportar HTML y Markdown con nuevos extractores.
4. Incorporar OCR opcional para PDF escaneado.
5. Exponer la misma lógica mediante FastAPI o integrarla con un índice vectorial.

Estas mejoras solo se abordarán tras validar que el flujo local de archivo único cumple los criterios P0.

