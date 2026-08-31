# Día 1 — Clasificador de descargas

> Proyecto de automatización en Python del reto **30 Días, 30 Proyectos**.

## Resumen ejecutivo

Clasificador de descargas organiza de forma segura archivos de un directorio local indicado explícitamente. Clasifica únicamente archivos regulares de primer nivel por extensión, los mueve a carpetas de categoría y muestra cada resultado en la terminal.

La primera versión es local, no recursiva y no destructiva: no presupone la carpeta personal de descargas, no usa servicios externos, no sobrescribe destinos existentes y deja sin cambios los archivos desconocidos o sin extensión. La implementación está en [`src/main.py`](src/main.py) y las pruebas automatizadas en [`tests/test_main.py`](tests/test_main.py).

## Problema

Las descargas pueden acumular archivos heterogéneos cuya organización manual es repetitiva. Este proyecto resuelve un único problema: clasificar de manera segura los archivos reconocidos de un directorio local sin alterar subcarpetas, archivos no reconocidos ni archivos que entren en conflicto con un destino existente.

## Alcance

### Incluye

- Directorio de entrada indicado explícitamente en la línea de comandos.
- Clasificación local por extensión de archivos regulares de primer nivel.
- Creación de carpetas de categoría cuando sea necesaria.
- Movimiento sin sobrescritura de archivos reconocidos.
- Resumen de archivos movidos, desconocidos, conflictos y errores.
- Pruebas automatizadas y fixture local reproducible.

### No incluye

- Detección automática de la carpeta personal de descargas.
- Exploración recursiva de subcarpetas.
- Interfaz gráfica, ejecución programada o vigilancia continua.
- Servicios externos, credenciales, variables de entorno o dependencias de terceros.
- Clasificación por contenido, MIME o inteligencia artificial.
- Renombrado automático, deduplicación, registro persistente o reversión automática.

## Requisitos

- Python 3.11 o superior.
- No se requieren dependencias de terceros; se usa únicamente la biblioteca estándar. Consulte [`requirements.txt`](requirements.txt).

## Reglas de clasificación

| Extensión admitida | Categoría de destino |
|---|---|
| `.png` | `Imágenes` |
| `.txt` | `Documentos` |
| `.zip` | `Comprimidos` |
| `.wav` | `Audio` |
| `.mp4` | `Vídeo` |

Las extensiones se comparan sin distinguir mayúsculas de minúsculas. Cada extensión admitida pertenece a una única categoría.

## Comportamiento seguro

| Situación | Comportamiento |
|---|---|
| Directorio inexistente o no válido | La ejecución termina con un error antes de realizar cambios. |
| Archivo reconocido | Se mueve a su categoría si no existe un destino con el mismo nombre. |
| Archivo sin extensión o extensión no admitida | Permanece en el directorio de entrada y se informa como desconocido. |
| Conflicto de nombre | El archivo de origen permanece intacto; no se sobrescribe, elimina ni renombra ningún archivo. |
| Subcarpeta | Se ignora; no se procesa su contenido. |
| Error de movimiento | Se informa y el procesamiento continúa con elementos independientes. |
| Nueva ejecución | Los archivos ya clasificados no se revisan porque están en subcarpetas; los desconocidos y conflictos siguen sin modificarse. |

El resumen muestra el origen y destino de cada movimiento. La reversión automática no forma parte de esta versión; el registro de terminal permite identificar movimientos para revisarlos o revertirlos manualmente si fuera necesario.

## Estructura del proyecto

```text
projects/day-01-download-sorter/
├── src/main.py                    # CLI y lógica de clasificación
├── tests/test_main.py             # Pruebas automatizadas con unittest
├── data/fixture-downloads/        # Fixture base reproducible
├── requirements.txt               # Sin dependencias de terceros
└── README.md
```

## Uso

Desde la raíz del repositorio, el programa recibe como último argumento el directorio que debe organizar:

python "30-dias-codigo/projects/day-01-download-sorter/src/main.py" "30-dias-codigo/projects/day-01-download-sorter/data/fixture-downloads"

python "30-dias-codigo/projects/day-01-download-sorter/src/main.py" "30-dias-codigo/projects/day-01-download-sorter/data/fixture-downloads"
```

El directorio de entrada se modifica al ejecutar el clasificador. Para preservar el fixture base, copie [`data/fixture-downloads`](data/fixture-downloads) a un directorio temporal y ejecute la herramienta sobre esa copia.

En Windows PowerShell, un flujo de demostración reproducible desde la raíz es:

```powershell
Copy-Item -Recurse projects/day-01-download-sorter/data/fixture-downloads "$env:TEMP\fixture-downloads-demo"
python projects/day-01-download-sorter/src/main.py "$env:TEMP\fixture-downloads-demo"
```

Si el directorio temporal ya existe, elimínelo o use un nombre nuevo antes de copiarlo. Las rutas con espacios deben escribirse entre comillas.

## Fixture y resultado esperado

El fixture base está en [`data/fixture-downloads`](data/fixture-downloads). Antes de ejecutar sobre una copia contiene:

- un candidato por categoría: `imagen-prueba.png`, `documento-prueba.txt`, `archivo-prueba.zip`, `audio-prueba.wav` y `video-prueba.mp4`;
- `archivo-desconocido.xyz`, que debe permanecer en la raíz;
- `SIN_EXTENSION`, que debe permanecer en la raíz;
- la subcarpeta `Subcarpeta intacta`, cuyo contenido no debe cambiar;
- el conflicto entre `conflicto.png` en la raíz y `Imágenes/conflicto.png`.

En una copia limpia del fixture, el resultado esperado es: cinco movimientos, dos archivos desconocidos, un conflicto y cero errores. El archivo `conflicto.png` de la raíz y el contenido de `Subcarpeta intacta` deben conservarse.

## Pruebas y verificación

Ejecute las pruebas desde la raíz del repositorio:

```powershell
python -m unittest discover -s projects/day-01-download-sorter/tests -v
```

Las pruebas cubren el flujo feliz, extensiones no reconocidas, archivos sin extensión, subcarpetas, conflictos de nombre, directorio de entrada inválido e idempotencia de una segunda ejecución.

Para comprobar la higiene del cambio local:

```powershell
git diff --check -- projects/day-01-download-sorter
git status --short -- projects/day-01-download-sorter
```

## Criterios de aceptación

- [x] Se valida el directorio de entrada antes de modificar contenido.
- [x] Solo se procesan archivos regulares de primer nivel.
- [x] Las extensiones `.png`, `.txt`, `.zip`, `.wav` y `.mp4` se mueven a sus categorías definidas.
- [x] Los archivos desconocidos y sin extensión permanecen intactos.
- [x] No se sobrescribe, elimina ni renombra un archivo ante un conflicto.
- [x] Las subcarpetas y su contenido permanecen intactos.
- [x] La terminal informa de movimientos, omisiones, conflictos, errores y totales.
- [x] Existe una prueba automatizada local y reproducible.
- [x] El proyecto no usa secretos, integraciones externas ni dependencias de terceros.

## Estado de entrega

El flujo funcional y la verificación local están completos. Para completar el proceso global del reto todavía quedan actividades de publicación fuera de la implementación local: preparar el GIF o vídeo de hasta 15 segundos, actualizar el índice raíz con demo/publicación, realizar el commit y push, y publicar el post de LinkedIn conforme a [`docs/DAILY_WORKFLOW.md`](../../docs/DAILY_WORKFLOW.md).
