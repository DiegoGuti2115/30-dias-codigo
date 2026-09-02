# Verificación — Fase 6

La Fase 6 cierra la v1 con regresión reproducible, documentación operativa y una demostración sintética local. Mantiene separadas las responsabilidades de interpretación, generación, actualización protegida y CLI definidas por [`CONTRATO.md`](CONTRATO.md).

## Entregables de cierre

- [`README.md`](../README.md) declara el estado final, requisitos, alcance, límites y verificación disponible.
- [`examples/USO.md`](../examples/USO.md) describe la preparación con Python 3.11+, vista previa, actualización explícita, códigos de salida, recuperación y comandos de comprobación.
- [`assets/demo-document.md`](../assets/demo-document.md) es un documento Markdown sintético con delimitadores válidos. Puede inspeccionarse mediante `python src/main.py assets/demo-document.md` sin modificarlo.
- [`tests/test_quality_regression.py`](../tests/test_quality_regression.py) prueba el proceso público de Python, no solo funciones internas.

## Regresión añadida

La cobertura de cierre verifica que:

- Una ruta relativa produce la vista previa de referencia completa y no modifica el documento de trabajo.
- Una ruta absoluta con extensión `.markdown` actualiza un documento UTF-8 con BOM, Unicode y CRLF.
- La actualización conserva BOM, CRLF y contenido exterior; una repetición no duplica el índice.
- La ejecución de [`main()`](../src/main.py:95) configura la salida estándar para no traducir los saltos de línea de una vista previa. Esto completa la preservación observable desde la terminal local, incluida la salida CRLF.

Los tests anteriores cubren los fixtures de encabezados, Unicode, duplicados, regiones de código, bloque ausente/incompleto/invertido/duplicado/inválido, documento sin encabezados, permisos, rutas, codificación, persistencia atómica y diagnósticos deterministas.

## Uso reproducible

Desde [`projects/day-05-markdown-toc`](..):

```text
python src/main.py assets/demo-document.md
copy assets\demo-document.md demo-working.md
python src/main.py demo-working.md --write
```

La primera orden presenta una vista previa. La segunda prepara una copia local y la tercera persiste exclusivamente el interior del bloque. En sistemas con `cp`, puede sustituirse la orden `copy` por `cp`.

## Verificaciones ejecutadas

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -c "…validación de todos los JSON de data/expected…"
python -c "…SHA-256 de data/fixtures/*.md…"
git diff --check -- .
git status --short --untracked-files=all
```

La suite completa termina correctamente con 31 pruebas. Las comprobaciones finales validan referencias JSON, confirman que los fixtures no se modifican, revisan espacios de Git y eliminan los directorios `__pycache__` generados.

## Límites reales de la v1

La versión final no procesa directorios, lotes, entrada estándar, enlaces simbólicos ni rutas de salida independientes. Solo admite UTF-8 y encabezados ATX fuera de bloques de código delimitados; no crea delimitadores, no interpreta Setext/HTML/extensiones de proveedor ni replica perfiles de anclas de plataformas. No requiere dependencias externas, credenciales, red ni servicios de terceros.
