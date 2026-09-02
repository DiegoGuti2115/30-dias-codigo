# Guía local de uso

Esta guía reproduce el flujo v1 con Python 3.11 o superior y solo recursos incluidos en el repositorio. No necesita instalación de paquetes, credenciales, red ni servicios externos.

## Preparación

Abra una terminal en [`projects/day-05-markdown-toc`](..). La herramienta usa únicamente la biblioteca estándar de Python:

```text
python --version
```

La versión debe ser Python 3.11 o superior.

## Vista previa segura

El modo predeterminado genera el documento completo propuesto en la salida estándar y no modifica el archivo:

```text
python src/main.py assets/demo-document.md
```

Para guardar la vista previa en otro recurso local sin tocar el documento de demostración:

```text
python src/main.py assets/demo-document.md > demo-preview.md
```

El índice de la demostración incluye los encabezados ATX elegibles y conserva sin cambios todo lo situado fuera de los delimitadores literales.

## Actualización explícita

Trabaje sobre una copia para mantener el recurso de demostración disponible para repeticiones:

```text
copy assets\demo-document.md demo-working.md
python src/main.py demo-working.md --write
python src/main.py demo-working.md
```

En sistemas con una utilidad `cp`, el primer paso equivalente es `cp assets/demo-document.md demo-working.md`. La actualización correcta escribe exactamente:

```text
Índice actualizado.
```

Una segunda actualización no duplica el índice: conserva el mismo documento y vuelve a comunicar éxito.

## Reglas operativas

- La ruta debe designar un único archivo regular local con extensión `.md` o `.markdown`.
- El archivo debe poder leerse como UTF-8; un BOM UTF-8 inicial se conserva.
- El documento debe tener exactamente este bloque, sin espacios ni texto adicional en sus líneas:

  ```text
  <!-- markdown-toc:start -->
  <!-- markdown-toc:end -->
  ```

- Sin [`--write`](../src/main.py:29) no hay persistencia. Con [`--write`](../src/main.py:29), solo se reemplaza el interior del bloque.
- Se reconocen encabezados ATX de nivel 1 a 6 fuera de bloques de código delimitados. Setext, HTML y extensiones de Markdown no pertenecen a v1.

Las reglas completas de sintaxis, anclas, preservación y seguridad están en [`docs/CONTRATO.md`](../docs/CONTRATO.md).

## Estados y recuperación

| Situación | Código | Canal | Recuperación local |
|---|:---:|---|---|
| Vista previa o actualización válida | `0` | salida estándar | Revise la vista previa antes de usar [`--write`](../src/main.py:29). |
| Argumento ausente o no permitido | `2` | salida de error | Ejecute `python src/main.py <DOCUMENT_PATH> [--write]`. |
| Ruta, extensión, lectura, UTF-8, bloque o actualización no válidos | `1` | salida de error | Corrija el recurso o los delimitadores y vuelva a ejecutar. El original permanece intacto ante estos errores manejados. |

La herramienta no crea delimitadores, no procesa directorios, enlaces simbólicos ni lotes y no repara enlaces existentes. Consulte los límites completos en [`README.md`](../README.md) y [`ROADMAP.md`](../ROADMAP.md).

## Verificación reproducible

Desde el directorio del proyecto:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Las pruebas usan datos sintéticos de [`data/fixtures`](../data/fixtures), referencias de [`data/expected`](../data/expected) y copias temporales para no modificar los archivos de entrada.
