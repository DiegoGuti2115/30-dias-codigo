# Día 2 — Renombrador masivo de archivos

> Proyecto de automatización en Python del reto **30 Días, 30 Proyectos**.

## Resumen ejecutivo

Herramienta CLI local para planificar y ejecutar reemplazos literales en lote sobre el **nombre base** de archivos. Muestra una previsualización inmutable por defecto; solo modifica archivos al incluir `--apply`. Una ejecución confirmada registra un manifiesto JSON para inspeccionar o deshacer los cambios de forma igualmente segura.

La implementación está en [`src/main.py`](src/main.py) y las pruebas en [`tests/test_main.py`](tests/test_main.py).

## Problema

Renombrar manualmente muchos archivos que comparten una parte de su nombre es repetitivo y propenso a sobrescribir un archivo existente. El proyecto resuelve un único problema: sustituir texto literal en los nombres de un directorio local explícito, evitando modificaciones accidentales y proporcionando reversión verificable.

## Alcance

### Incluye

- Directorio de entrada indicado explícitamente en línea de comandos.
- Reemplazo literal, sensible a mayúsculas/minúsculas, en el nombre sin extensión.
- Conservación automática de la extensión, incluidos archivos sin extensión.
- Filtro opcional por glob mediante `--pattern`.
- Previsualización determinista y sin cambios por defecto.
- Aplicación solo mediante la confirmación explícita `--apply`.
- Protección contra sobrescrituras, destinos repetidos y conflictos de mayúsculas/minúsculas.
- Renombrado seguro de ciclos e intercambios con nombres temporales únicos.
- Manifiesto JSON atómico dentro del directorio de entrada.
- Operación `undo` previsualizable y confirmada con `--apply`.
- Pruebas locales con `unittest` y sin dependencias externas.

### No incluye

- Exploración recursiva, procesado de directorios o de enlaces simbólicos.
- Renombrado por expresiones regulares, normalización automática o numeración.
- Resolución automática de conflictos mediante sufijos.
- Interfaz gráfica, vigilancia de carpetas, tareas programadas o servicios cloud.
- Garantía de deshacer cambios externos realizados después de aplicar el plan.

## Requisitos

- Python 3.11 o superior.
- Ninguna dependencia de terceros; consulte [`requirements.txt`](requirements.txt).

## Uso

Desde la raíz del repositorio, cree primero una previsualización:

```powershell
python projects/day-02-bulk-file-renamer/src/main.py rename "<directorio>" --find "-borrador" --replace "-final" --pattern "*.txt"
```

La herramienta solo muestra `origen -> destino` y no modifica el contenido. Tras revisar el plan, confírmelo:

```powershell
python projects/day-02-bulk-file-renamer/src/main.py rename "<directorio>" --find "-borrador" --replace "-final" --pattern "*.txt" --apply
```

El reemplazo afecta únicamente al nombre base: `informe-borrador.txt` pasa a `informe-final.txt`, mientras la extensión `.txt` se conserva.

## Tutorial práctico: renombrar borradores de texto

Esta herramienta evita renombrar a mano archivos que comparten una etiqueta en el nombre. Trabaja sobre un directorio local indicado de forma explícita, cambia solo el **nombre base** —no el contenido ni la extensión— y prepara un plan seguro antes de modificar nada.

### Archivos de práctica

El directorio [`data/tutorial-files`](data/tutorial-files) contiene una colección aislada para seguir el ejemplo:

- `informe-enero-draft.txt` y `informe-febrero-draft.txt`: archivos de texto que sí coinciden con el ejemplo.
- `resumen-proyecto-draft.md`: contiene `-draft`, pero su extensión no coincide con el filtro de texto.
- `imagen-draft.jpg`: archivo de ejemplo usado únicamente para demostrar el filtro de extensión; no representa una imagen binaria real.
- `notas-finales.txt`: archivo de texto que no contiene `-draft` y, por tanto, no debe cambiar.

Antes de realizar una operación, revise los nombres actuales desde la raíz del repositorio:

```powershell
Get-ChildItem "projects/day-02-bulk-file-renamer/data/tutorial-files" -File | Select-Object -ExpandProperty Name
```

### 1. Preparar una previsualización

El subcomando `rename` crea un plan de renombrado. Su primer argumento es el directorio que se procesará. Las opciones `--find` y `--replace` indican el texto literal que se sustituirá en el nombre sin extensión; `--pattern` limita qué nombres de archivo se consideran mediante un glob. En este caso, `--pattern "*.txt"` selecciona únicamente archivos cuyo nombre termina en `.txt`.

Ejecute la siguiente simulación:

```bash
python projects/day-02-bulk-file-renamer/src/main.py rename "projects/day-02-bulk-file-renamer/data/tutorial-files" --find "-draft" --replace "-final" --pattern "*.txt"
```

Como no se incluye `--apply`, la herramienta imprime el directorio, una `Previsualización (renombrado):`, cada relación `origen -> destino` y el total, seguido de `No se realizaron cambios. Añada --apply para confirmar.` Los archivos permanecen intactos. Para este conjunto, el plan incluye los dos informes `.txt` con `-draft`; no incluye `resumen-proyecto-draft.md` ni `imagen-draft.jpg` porque no satisfacen `*.txt`, y tampoco incluye `notas-finales.txt` porque no contiene el texto buscado.

### 2. Aplicar el plan revisado

Tras confirmar que la previsualización es la esperada, añada `--apply` para ejecutar exactamente ese plan:

```bash
python projects/day-02-bulk-file-renamer/src/main.py rename "projects/day-02-bulk-file-renamer/data/tutorial-files" --find "-draft" --replace "-final" --pattern "*.txt" --apply
```

Con `--apply`, la aplicación vuelve a mostrar la previsualización, renombra los archivos del plan y confirma la operación con un mensaje `Aplicado: ...`. Después, revise el contenido de la carpeta:

```powershell
Get-ChildItem "projects/day-02-bulk-file-renamer/data/tutorial-files" -File | Select-Object -ExpandProperty Name
```

Los nombres de los informes pasan a terminar en `-final.txt`. `imagen-draft.jpg` sigue igual aunque contenga `-draft`, porque `--pattern "*.txt"` excluye cualquier extensión distinta de `.txt`. `notas-finales.txt` también se conserva porque el reemplazo literal solo actúa cuando `--find` aparece en el nombre base.

La aplicación crea además [`data/tutorial-files/.bulk-file-renamer-manifest.json`](data/tutorial-files/.bulk-file-renamer-manifest.json) de forma predeterminada. El manifiesto guarda el directorio y las parejas de origen y destino del plan completado; sirve para validar y preparar la reversión posterior. El archivo se crea tras concluir correctamente el renombrado.

### 3. Revisar y deshacer mediante el manifiesto

Primero puede inspeccionar el estado actual de la carpeta con el mismo comando de PowerShell anterior. Para preparar una reversión sin cambiar archivos, use `undo` con la ruta del manifiesto:

```bash
python projects/day-02-bulk-file-renamer/src/main.py undo "projects/day-02-bulk-file-renamer/data/tutorial-files/.bulk-file-renamer-manifest.json"
```

Esta ejecución muestra una `Previsualización (deshacer):` y no modifica nombres hasta recibir confirmación. Cuando el plan inverso sea correcto, aplíquelo con:

```bash
python projects/day-02-bulk-file-renamer/src/main.py undo "projects/day-02-bulk-file-renamer/data/tutorial-files/.bulk-file-renamer-manifest.json" --apply
```

La operación muestra el plan, restaura los nombres registrados y termina con `Deshecho: ...`. Compruebe de nuevo la carpeta:

```powershell
Get-ChildItem "projects/day-02-bulk-file-renamer/data/tutorial-files" -File | Select-Object -ExpandProperty Name
```

### Precauciones al elegir rutas y nombres

- Indique siempre la ruta del directorio que realmente desea procesar; la herramienta no explora subcarpetas.
- Revise toda previsualización antes de usar `--apply`, tanto al renombrar como al deshacer.
- El texto de `--find` se busca de forma literal y distingue mayúsculas de minúsculas. La extensión se preserva automáticamente.
- La herramienta bloquea el plan si un destino ya existe fuera del propio plan o si dos archivos acabarían con el mismo destino; no crea sufijos para resolver conflictos.
- El manifiesto se debe conservar junto a los archivos mientras se necesite deshacer. Si los archivos esperados se eliminan o se modifican externamente, `undo` valida el estado y puede bloquearse sin realizar cambios.
- Las rutas de entrada y del manifiesto deben apuntar al mismo directorio procesado; un manifiesto personalizado para `rename` debe guardarse dentro de ese directorio.

### Valores que comienzan por guion en PowerShell

Los valores literales de `--find` y `--replace` pueden comenzar por uno o varios guiones. Por ejemplo, este comando es válido y se interpreta como `-draft` → `-final`:

```powershell
python projects/day-02-bulk-file-renamer/src/main.py rename "projects/day-02-bulk-file-renamer/data/fixture-files" --find "-draft" --replace "-final" --pattern "*.txt"
```

Las comillas de PowerShell conservan el valor como un único argumento, pero no cambian que comience por `-`. La CLI normaliza específicamente los valores de `--find` y `--replace` antes de delegar en `argparse`, por lo que la sintaxis separada anterior funciona. El problema original no era de PowerShell: `argparse` interpretaba el token siguiente que empezaba por guion como otra opción y concluía que faltaba el valor de `--find`.

También sigue siendo válida la sintaxis explícita con signo igual, equivalente y compatible con `argparse`:

```powershell
python projects/day-02-bulk-file-renamer/src/main.py rename "projects/day-02-bulk-file-renamer/data/fixture-files" --find=-draft --replace=-final --pattern "*.txt"
```

Para eliminar el texto encontrado, el reemplazo vacío debe escribirse con signo igual:

```powershell
python projects/day-02-bulk-file-renamer/src/main.py rename "projects/day-02-bulk-file-renamer/data/fixture-files" --find=-draft --replace= --pattern "*.txt"
```

`--find` no puede estar vacío por seguridad. `--replace` sí puede estarlo. Revise siempre la previsualización antes de añadir `--apply`.

### Deshacer

Una aplicación exitosa genera por defecto `.bulk-file-renamer-manifest.json` en el directorio procesado. Previsualice la reversión antes de confirmarla:

```powershell
python projects/day-02-bulk-file-renamer/src/main.py undo "<directorio>\.bulk-file-renamer-manifest.json"
python projects/day-02-bulk-file-renamer/src/main.py undo "<directorio>\.bulk-file-renamer-manifest.json" --apply
```

Use `--manifest "<directorio>\registro.json"` con `rename` para elegir otro nombre de manifiesto, siempre dentro del mismo directorio de entrada.

## Seguridad y validaciones

| Situación | Comportamiento |
|---|---|
| Directorio inválido | Error antes de planificar o cambiar archivos. |
| Sin coincidencias | Previsualización con total cero; no hay cambios. |
| `--find` vacío | Error, para impedir que todos los nombres se alteren accidentalmente. |
| Destino ya ocupado por un archivo ajeno al plan | Error; no se sobrescribe ni elimina nada. |
| Dos candidatos con el mismo destino | Error; el plan completo se bloquea. |
| Cambios de solo mayúsculas o ciclos | Admitidos mediante nombres temporales únicos. |
| Subcarpeta o enlace simbólico | Se ignora; nunca se explora ni se sigue. |
| Error de permisos, bloqueo o E/S | Se informa con salida no nula y se intenta recuperar los movimientos ya iniciados. |
| Manifiesto alterado o archivos cambiados externamente | El deshacer se bloquea antes de modificar contenido. |

El sistema valida el plan completo antes de efectuar el primer movimiento. El manifiesto se escribe de modo atómico únicamente después de terminar todos los renombrados. Ninguna herramienta puede garantizar una reversión absoluta si otro proceso modifica, elimina o bloquea archivos entre la aplicación y el deshacer; por eso `undo` vuelve a validar el estado actual y exige `--apply`.

## Fixture de demostración

Copie [`data/fixture-files`](data/fixture-files) a una ubicación temporal antes de usarla, para conservar el fixture base:

```powershell
Copy-Item -Recurse projects/day-02-bulk-file-renamer/data/fixture-files "$env:TEMP\bulk-renamer-demo"
python projects/day-02-bulk-file-renamer/src/main.py rename "$env:TEMP\bulk-renamer-demo" --find "-draft" --replace "-final" --pattern "*.txt"
```

## Pruebas

Ejecute las pruebas desde la raíz:

```powershell
python -m unittest discover -s projects/day-02-bulk-file-renamer/tests -v
```

Cubren previsualización inmutable, filtros glob, conservación de extensión, conflictos, staging de ciclos, manifiesto, deshacer y manifiestos obsoletos.

## Criterios de aceptación

- [x] La ejecución sin `--apply` no modifica archivos.
- [x] La operación confirmada solo cambia el plan validado.
- [x] No se sobrescribe un archivo existente ni se resuelven conflictos automáticamente.
- [x] Los directorios y enlaces simbólicos no se procesan.
- [x] Una aplicación exitosa genera un manifiesto local y un deshacer válido puede restaurar los nombres.
- [x] El deshacer se previsualiza y requiere confirmación explícita.
- [x] Existen pruebas locales reproducibles sin servicios, secretos ni dependencias externas.
