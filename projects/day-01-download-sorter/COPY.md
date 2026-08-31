# Día 1/30 — Clasificador de descargas: empezar automatizando sin poner los archivos en riesgo

Arranca **30 días, 30 proyectos**, un reto práctico de ingeniería de software: durante septiembre diseñaré, programaré, documentaré y publicaré una herramienta funcional cada día.

El objetivo es construir 30 soluciones pequeñas y concretas, con un máximo de tres horas por entrega, para practicar automatización, APIs, frontend reactivo, IA y agentes. Cada proyecto quedará documentado en el repositorio y acompañado de una publicación con una demostración de su funcionamiento. La hoja de ruta completa está en el [README principal](../../README.md).

El primer proyecto marca el criterio de toda la serie: resolver un problema real con un alcance deliberadamente acotado, un comportamiento verificable y límites claros.

## Proyecto del día 1: Clasificador de descargas

Una carpeta de descargas puede reunir imágenes, documentos, archivos comprimidos, audio y vídeo. Ordenarla manualmente es repetitivo; automatizarla sin medidas de seguridad puede ser peor que dejarla como está.

Por eso he creado un clasificador local en Python que recibe **un directorio indicado explícitamente** y organiza únicamente sus archivos regulares de primer nivel según la extensión:

| Extensión | Carpeta de destino |
|---|---|
| `.png` | `Imágenes` |
| `.txt` | `Documentos` |
| `.zip` | `Comprimidos` |
| `.wav` | `Audio` |
| `.mp4` | `Vídeo` |

La implementación está en [`src/main.py`](src/main.py) y usa Python 3.11 o superior junto con la biblioteca estándar; no requiere dependencias de terceros.

## Qué hace — y qué protege

La herramienta crea las carpetas de categoría cuando son necesarias, mueve los archivos reconocidos y muestra en la terminal cada decisión junto con un resumen de movimientos, archivos desconocidos, conflictos y errores.

También incorpora decisiones de seguridad importantes:

- No presupone ni accede automáticamente a la carpeta personal de Descargas.
- No entra en subcarpetas ni procesa su contenido.
- Deja intactos los archivos sin extensión o con extensiones no admitidas.
- Si ya existe el mismo nombre en destino, conserva el archivo de origen: no sobrescribe, elimina ni renombra archivos.
- Valida el directorio de entrada antes de modificar su contenido.
- Una segunda ejecución no vuelve a procesar los archivos ya clasificados, porque quedan dentro de subcarpetas.

Esta primera entrega permite practicar una CLI con argumentos, operaciones seguras sobre el sistema de archivos, clasificación con [`pathlib.Path`](src/main.py:9), manejo de errores, resultados trazables en terminal y pruebas automatizadas con [`unittest`](tests/test_main.py:8).

## Pruébalo de forma segura

El proyecto incluye un fixture reproducible en [`data/fixture-downloads`](data/fixture-downloads). Como el clasificador mueve archivos, la forma recomendada de explorarlo es trabajar sobre una copia temporal, no sobre el fixture original ni sobre archivos personales.

Desde la raíz del repositorio, en Windows PowerShell:

```powershell
Copy-Item -Recurse projects/day-01-download-sorter/data/fixture-downloads "$env:TEMP\fixture-downloads-demo"
python projects/day-01-download-sorter/src/main.py "$env:TEMP\fixture-downloads-demo"
```

En una copia limpia, la ejecución esperada realiza cinco movimientos, informa dos archivos desconocidos, detecta un conflicto de nombre y termina sin errores. La subcarpeta incluida en el fixture permanece intacta.

Para ejecutar la suite de verificación:

```powershell
python -m unittest discover -s projects/day-01-download-sorter/tests -v
```

El detalle del alcance, las reglas de clasificación y los resultados esperados está disponible en el [README del proyecto](README.md). El guion de demostración reproducible se encuentra en [DEMO.md](DEMO.md).

## El aprendizaje de hoy

Automatizar no consiste solo en mover archivos: también consiste en decidir explícitamente qué no tocar. En este proyecto, el directorio debe indicarse de forma manual, las subcarpetas se ignoran, los casos desconocidos se preservan y los conflictos nunca se resuelven destruyendo información.

Día 1 completado: una automatización local, pequeña y verificable como punto de partida para los próximos 29 proyectos.

#30Dias30Proyectos #BuildInPublic #Python #Automatizacion #DesarrolloDeSoftware
