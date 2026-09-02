# Verificación — Fase 3

La Fase 3 implementa únicamente el núcleo sin efectos de interpretación y generación de índice. No valida rutas, delimitadores, codificación, permisos, modos CLI ni realiza escrituras: esas responsabilidades siguen asignadas a las fases 4 y 5 en [`ROADMAP.md`](../ROADMAP.md).

## Alcance verificado

- [`src/parser.py`](../src/parser.py) reconoce encabezados ATX con hasta tres espacios de sangría, de uno a seis `#`, separador horizontal obligatorio y texto no vacío.
- El intérprete conserva línea física, nivel y texto visible; no interpreta la sintaxis Markdown en línea.
- Los encabezados Setext no son elegibles en v1.
- Los bloques cercados con acentos graves o virgulillas se excluyen según tipo y longitud; un bloque sin cierre excluye el resto del documento.
- [`src/toc.py`](../src/toc.py) aplica NFKD, elimina marcas combinantes, conserva letras/números Unicode, normaliza espacios y guiones, usa `seccion` como reserva y sufija duplicados en orden físico.
- La jerarquía usa dos espacios por profundidad y no crea niveles vacíos ante saltos de encabezado.
- La implementación no lee ni escribe rutas durante la interpretación o generación.

## Comandos ejecutados

Desde [`projects/day-05-markdown-toc`](..):

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -c "…validación JSON y comprobación de solo lectura…"
git diff --check -- .
```

Resultados observados:

- Las 13 pruebas unitarias de [`tests/test_parser.py`](../tests/test_parser.py) y [`tests/test_toc.py`](../tests/test_toc.py) finalizaron correctamente.
- La compilación de [`src`](../src) y [`tests`](../tests) finalizó sin errores.
- Todos los JSON de [`data/expected`](../data/expected) se decodificaron correctamente.
- Procesar todos los fixtures no modificó ninguno de los archivos de [`data/fixtures`](../data/fixtures).
- La comprobación de espacios con `git diff --check` finalizó correctamente.

## Referencias ejercitadas

Las pruebas comparan directamente las referencias de [`data/expected`](../data/expected) para [`complex-valid.md`](../data/fixtures/complex-valid.md), [`atx-edge-cases.md`](../data/fixtures/atx-edge-cases.md) y [`fenced-code-unclosed.md`](../data/fixtures/fenced-code-unclosed.md). También cubren documentos vacíos o sin encabezados, Setext, fences con cierres insuficientes, Unicode, puntuación, duplicados y saltos de nivel.

Los fixtures de delimitadores ausentes, incompletos, invertidos, duplicados o inválidos, así como códigos de salida, permisos, UTF-8, finales de línea y preservación, permanecen sin implementación deliberadamente. Son verificaciones de [`src/rewriter.py`](../src/rewriter.py) y [`src/main.py`](../src/main.py) para las Fases 4 y 5; ambos módulos siguen vacíos.
