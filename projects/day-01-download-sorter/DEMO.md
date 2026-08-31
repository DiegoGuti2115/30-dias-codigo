# Guion de demo — Día 1: Clasificador de descargas

## Objetivo

Mostrar en una demo breve que la CLI clasifica archivos regulares del primer nivel de un directorio indicado explícitamente, por extensión y sin sobrescribir destinos existentes. La grabación debe demostrar el flujo completo: preparación segura, estado inicial, ejecución, resultado, casos protegidos y pruebas automatizadas.

La propuesta se ciñe a la implementación de [`src/main.py`](src/main.py): Python 3.11+ y biblioteca estándar, sin GUI, monitorización, clasificación por contenido ni recorrido recursivo. El proyecto forma parte del reto **30 Días, 30 Proyectos**, como confirma [`README.md`](README.md).

## Duración y formato recomendados

- **Duración:** 75–90 segundos.
- **Formato:** 16:9, 1080p, terminal PowerShell a pantalla completa, fuente de al menos 18 px y sin notificaciones.
- **Ritmo:** mostrar comandos completos y sus resultados; eliminar tiempos de espera en edición, pero conservar 1–2 segundos para leer el resumen y el árbol final.
- **Principio visual:** enseña resultado observable antes que detalles internos del código.

## Preparación segura

> **No ejecutar la CLI sobre una carpeta personal ni directamente sobre [`data/fixture-downloads`](data/fixture-downloads).** La CLI mueve los archivos reconocidos del directorio indicado.

La estructura disponible del fixture contiene los casos de seguridad reales: `archivo-desconocido.xyz`, `SIN_EXTENSION`, `conflicto.png`, `Imágenes/conflicto.png` y `Subcarpeta intacta/contenido.txt`. Al inspeccionar el estado actual, los candidatos de categoría ya están dentro de `Audio`, `Comprimidos`, `Documentos` e `Imágenes`, y no se observa `video-prueba.mp4`. Por ello, el siguiente bloque prepara **una copia temporal independiente** y restablece un estado inicial reproducible para la grabación. Crea un archivo vacío `video-prueba.mp4` únicamente en esa copia; es válido para demostrar la regla de extensión porque la implementación no inspecciona el contenido del archivo.

Ejecutar desde la raíz del repositorio, en Windows PowerShell:

```powershell
$demo = Join-Path $env:TEMP "day-01-download-sorter-demo"
Remove-Item -Recurse -Force $demo -ErrorAction SilentlyContinue
Copy-Item -Recurse "projects/day-01-download-sorter/data/fixture-downloads" $demo
Move-Item "$demo\Audio\audio-prueba.wav" "$demo\audio-prueba.wav"
Move-Item "$demo\Comprimidos\archivo-prueba.zip" "$demo\archivo-prueba.zip"
Move-Item "$demo\Documentos\documento-prueba.txt" "$demo\documento-prueba.txt"
Move-Item "$demo\Imágenes\imagen-prueba.png" "$demo\imagen-prueba.png"
New-Item -ItemType File -Path "$demo\video-prueba.mp4" | Out-Null
```

La copia en `$demo` es el único directorio que se modifica durante la demo. El fixture original y los archivos personales quedan intactos.

## Archivos y resultado que se deben enseñar

### Estado inicial en la copia temporal

| Caso | Elemento que aparece en pantalla | Resultado esperado |
|---|---|---|
| Imagen reconocida | `imagen-prueba.png` | Se mueve a `Imágenes`. |
| Documento reconocido | `documento-prueba.txt` | Se mueve a `Documentos`. |
| Comprimido reconocido | `archivo-prueba.zip` | Se mueve a `Comprimidos`. |
| Audio reconocido | `audio-prueba.wav` | Se mueve a `Audio`. |
| Vídeo reconocido | `video-prueba.mp4` | Se mueve a `Vídeo`. |
| Extensión no admitida | `archivo-desconocido.xyz` | Permanece en la raíz como desconocido. |
| Sin extensión | `SIN_EXTENSION` | Permanece en la raíz como desconocido. |
| Conflicto de destino | `conflicto.png` y `Imágenes/conflicto.png` | Ambos permanecen; no se sobrescribe ni renombra ninguno. |
| Subcarpeta | `Subcarpeta intacta/contenido.txt` | Permanece intacta; no se procesa. |

En una copia recién preparada, la salida esperada es `movidos=5`, `desconocidos=2`, `conflictos=1` y `errores=0`. Esto coincide con las comprobaciones de [`tests/test_main.py`](tests/test_main.py).

## Comandos de la grabación

### 1. Mostrar el estado inicial

```powershell
tree /F $demo
```

Dejar visibles los cinco candidatos en la raíz, `archivo-desconocido.xyz`, `SIN_EXTENSION`, `conflicto.png`, la carpeta `Imágenes` con su conflicto existente y `Subcarpeta intacta`.

### 2. Ejecutar la CLI

```powershell
python projects/day-01-download-sorter/src/main.py "$demo"
```

Mantener visible la salida completa. Deben aparecer cinco líneas `MOVIDO`, dos líneas `OMITIDO desconocido`, una línea `OMITIDO conflicto` y el resumen. La lógica imprime estas decisiones desde [`sort_downloads()`](src/main.py:31).

### 3. Mostrar el árbol final

```powershell
tree /F $demo
```

Resaltar `Audio/audio-prueba.wav`, `Comprimidos/archivo-prueba.zip`, `Documentos/documento-prueba.txt`, `Imágenes/imagen-prueba.png` y `Vídeo/video-prueba.mp4`. Mostrar también que los tres archivos protegidos continúan en la raíz y que el contenido de la subcarpeta persiste.

### 4. Verificar los casos especiales en pantalla

```powershell
Write-Host "Archivos que permanecen en la raíz:"; Get-ChildItem -File $demo -Name
Write-Host "Contenido de subcarpeta preservada:"; Get-ChildItem -File "$demo\Subcarpeta intacta" -Name
Write-Host "Conflicto en raíz:" (Test-Path "$demo\conflicto.png")
Write-Host "Conflicto preexistente:" (Test-Path "$demo\Imágenes\conflicto.png")
```

El primer comando debe mostrar `archivo-desconocido.xyz`, `SIN_EXTENSION` y `conflicto.png`. Los dos últimos deben imprimir `True`.

### 5. Ejecutar las pruebas

```powershell
python -m unittest discover -s projects/day-01-download-sorter/tests -v
```

Dejar visible el cierre exitoso. Las pruebas verifican el flujo feliz, desconocidos, ausencia de extensión, subcarpetas, conflictos, directorio inválido e idempotencia, según [`tests/test_main.py`](tests/test_main.py).

## Flujo visual de grabación

| Tiempo | Pantalla | Acción y mensaje clave |
|---|---|---|
| 0–6 s | Título y terminal limpia | Título: **Día 1 — Clasificador de descargas**. Subtítulo: *Python 3.11+ · biblioteca estándar*. |
| 6–16 s | Árbol inicial | Presentar el desorden controlado y los cuatro casos de seguridad: desconocidos, conflicto y subcarpeta. |
| 16–23 s | Código, máximo dos planos | Mostrar el mapa de extensiones en [`CATEGORY_BY_EXTENSION`](src/main.py:12) y el control de conflicto en [`sort_downloads()`](src/main.py:52). No recorrer el archivo completo. |
| 23–31 s | Terminal | Mostrar la preparación de la copia temporal. Añadir texto: *Demo sobre copia segura; no toca archivos personales*. |
| 31–47 s | Terminal durante la ejecución | Ejecutar la CLI y hacer zoom breve en `MOVIDO`, `OMITIDO desconocido`, `OMITIDO conflicto` y el resumen. |
| 47–59 s | Árbol final | Mostrar las cinco carpetas de destino y los elementos preservados. |
| 59–68 s | Terminal | Ejecutar las comprobaciones de conflicto y subcarpeta. |
| 68–80 s | Terminal | Ejecutar `unittest`; dejar visible el resultado correcto. |
| 80–90 s | Tarjeta final | Cerrar con **30 Días, 30 Proyectos — Día 1 completado**. |

## Narración sugerida, palabra por palabra

> «Día 1 de 30 Días, 30 Proyectos. Una carpeta de descargas puede mezclar imágenes, documentos, audio y archivos comprimidos, y ordenarla a mano es repetitivo.
>
> Este proyecto en Python clasifica archivos de primer nivel por extensión: PNG, TXT, ZIP, WAV y MP4. La regla es explícita y no necesita dependencias externas.
>
> Para la demo trabajo solo con una copia temporal del fixture. Así no modifico ni el fixture original ni archivos personales.
>
> Antes de ejecutar vemos cinco candidatos, dos archivos que deben quedar sin tocar, una subcarpeta y un conflicto de nombre ya preparado.
>
> Al lanzar la CLI, cada movimiento queda registrado. Los archivos desconocidos se omiten y, si ya existe un destino, el archivo original permanece intacto: no hay sobrescritura ni renombrado automático.
>
> El resumen confirma cinco movimientos, dos desconocidos, un conflicto y cero errores.
>
> El árbol final muestra los archivos organizados en sus categorías. También comprobamos que el conflicto, los desconocidos y la subcarpeta se conservaron.
>
> Por último, las pruebas automatizadas validan el comportamiento y la seguridad. Día 1 completado: una automatización local, pequeña y verificable.»

## Explicación técnica breve

- [`parse_arguments()`](src/main.py:84) exige que el directorio de entrada se indique en la línea de comandos.
- [`sort_downloads()`](src/main.py:31) valida que sea un directorio antes de actuar.
- Solo procesa elementos para los que [`Path.is_file()`](src/main.py:42) es verdadero, por lo que no entra en subcarpetas.
- La categoría sale de [`CATEGORY_BY_EXTENSION`](src/main.py:12) y compara la extensión en minúsculas.
- Antes de mover, [`Path.exists()`](src/main.py:53) evita sobrescribir un archivo de destino.
- El resumen se construye con [`Counter`](src/main.py:72) e informa movimientos, desconocidos, conflictos y errores.

## Errores que conviene evitar

- Ejecutar sobre `Downloads`, Escritorio o el fixture original en vez de `$demo`.
- Afirmar que explora subcarpetas, detecta tipos MIME, renombra conflictos o revierte cambios: esas funciones no están implementadas.
- Mostrar demasiado código. Dos planos breves bastan para explicar reglas y protección contra conflictos.
- Ocultar o cortar las líneas del resumen y las pruebas: son la evidencia principal de la demo.
- Usar una terminal con fuente pequeña, notificaciones, rutas truncadas o comandos parcialmente fuera de pantalla.
- Ejecutar el bloque de preparación sin `Remove-Item`: una copia temporal previa puede impedir una demostración repetible.

## Lista final de comprobación

- [ ] Python 3.11 o superior disponible con `python --version`.
- [ ] Terminal PowerShell a pantalla completa, fuente legible y notificaciones desactivadas.
- [ ] Se ha creado `$demo` a partir de [`data/fixture-downloads`](data/fixture-downloads), sin alterar el fixture base.
- [ ] El árbol inicial muestra los cinco candidatos y los casos protegidos.
- [ ] La ejecución se realiza exclusivamente con `python projects/day-01-download-sorter/src/main.py "$demo"`.
- [ ] El resumen muestra 5 movimientos, 2 desconocidos, 1 conflicto y 0 errores.
- [ ] El árbol final y las comprobaciones confirman que desconocidos, conflicto y subcarpeta permanecen intactos.
- [ ] `python -m unittest discover -s projects/day-01-download-sorter/tests -v` termina correctamente.
- [ ] El cierre menciona **30 Días, 30 Proyectos** y anima a seguir el reto.
