# Verificación — Fase 5

La Fase 5 integra la interfaz de línea de comandos sobre el intérprete, generador y actualizador ya verificados. No modifica las reglas puras de Markdown ni la política de persistencia de las fases anteriores.

## Interfaz implementada

Desde [`projects/day-05-markdown-toc`](..):

```text
python src/main.py <DOCUMENT_PATH>
python src/main.py <DOCUMENT_PATH> --write
```

- Sin [`--write`](../src/main.py:29), [`run()`](../src/main.py:30) genera el índice, construye la vista previa y escribe el documento completo propuesto en salida estándar sin persistir cambios.
- Con [`--write`](../src/main.py:29), la CLI reutiliza [`update_file()`](../src/rewriter.py:78) y emite `Índice actualizado.` en salida estándar si la operación termina correctamente.
- La CLI acepta un único documento local `.md` o `.markdown`, rechaza directorios, enlaces simbólicos, extensiones no admitidas, lectura no permitida y UTF-8 inválido antes de interpretar el documento.
- Los errores previsibles se escriben solo en salida de error sin trazas. Los argumentos inválidos devuelven `2`; los errores de entrada, codificación, bloque o actualización devuelven `1`; vista previa y actualización válidas devuelven `0`.

## Cobertura de integración

[`tests/test_cli.py`](../tests/test_cli.py) ejecuta la CLI sobre copias temporales de los fixtures y verifica:

- Vista previa exacta de [`complex-valid.md`](../data/fixtures/complex-valid.md) contra [`complex-valid-preview.md`](../data/expected/complex-valid-preview.md), sin modificar la copia.
- Actualización, mensaje estable e idempotencia sin modificar el fixture original.
- Documento sin encabezados y bloque resultante vacío.
- Todos los escenarios de bloque de [`error-scenarios.json`](../data/expected/error-scenarios.json), sin escritura.
- Ruta inexistente, directorio, extensión no admitida, permiso de lectura, UTF-8 inválido y permiso de escritura.
- Argumento no admitido mediante el proceso real de Python, con código `2`, salida de uso y sin traza interna.

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

- Las 29 pruebas de [`tests`](../tests) finalizaron correctamente.
- La compilación de [`src`](../src) y [`tests`](../tests) finalizó sin errores.
- Los JSON de [`data/expected`](../data/expected) se decodificaron correctamente y los hashes de los fixtures Markdown permanecieron sin cambios.
- La comprobación de espacios finalizó correctamente; no quedan directorios `__pycache__` tras la limpieza.

## Límite pendiente

La Fase 5 entrega la CLI v1 y su integración. La ampliación de guía de uso, demo y cierre integral de calidad sigue asignada a la Fase 6 en [`ROADMAP.md`](../ROADMAP.md).
