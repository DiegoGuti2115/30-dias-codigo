# Verificación — Fase 4

La Fase 4 incorpora la sustitución protegida del bloque de índice y su persistencia segura. La interfaz CLI, el análisis de argumentos y la presentación de mensajes o códigos de salida siguen asignados a la Fase 5 en [`ROADMAP.md`](../ROADMAP.md).

## Alcance verificado

- [`src/rewriter.py`](../src/rewriter.py) valida un único bloque delimitado literal y emite los diagnósticos contractuales para bloques ausentes, incompletos, invertidos, duplicados o inválidos.
- [`build_preview()`](../src/rewriter.py:65) produce el documento propuesto sin operaciones de sistema de archivos y solo sustituye el contenido interior del bloque.
- [`update_file()`](../src/rewriter.py:78) valida el recurso, conserva BOM UTF-8, saltos de línea, ausencia de salto final y contenido exterior, y evita una escritura cuando el resultado es idéntico.
- La persistencia escribe primero un temporal en el directorio de destino, sincroniza su contenido, conserva el modo disponible y reemplaza atómicamente el original. Un error de persistencia elimina el temporal y conserva el original.
- La fase rechaza recursos no regulares, enlaces simbólicos, extensiones no Markdown, UTF-8 inválido y archivos sin bits de escritura antes de reemplazar el original.

## Comandos ejecutados

Desde [`projects/day-05-markdown-toc`](..):

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -c "…validación JSON y huellas de fixtures…"
git diff --check -- .
git status --short --untracked-files=all
```

Resultados observados:

- Las 23 pruebas unitarias de [`tests/test_parser.py`](../tests/test_parser.py), [`tests/test_toc.py`](../tests/test_toc.py) y [`tests/test_rewriter.py`](../tests/test_rewriter.py) finalizaron correctamente.
- La compilación de [`src`](../src) y [`tests`](../tests) finalizó sin errores.
- Los cuatro JSON de [`data/expected`](../data/expected) se decodificaron correctamente.
- Las huellas de los diez fixtures Markdown se conservaron durante las verificaciones.
- Las pruebas de actualización ejercitan idempotencia, preservación exterior, BOM, saltos mixtos, contenido sin encabezados, permisos, UTF-8 inválido y fallo simulado de reemplazo sin temporales residuales.

## Límites pendientes

La Fase 4 expone una API de actualización para un documento ya seleccionado; no implementa argumentos CLI, salida estándar/errores ni códigos de retorno. Esas responsabilidades, junto con la validación de solicitud desde terminal, permanecen en [`src/main.py`](../src/main.py) y [`tests/test_cli.py`](../tests/test_cli.py) para la Fase 5.
