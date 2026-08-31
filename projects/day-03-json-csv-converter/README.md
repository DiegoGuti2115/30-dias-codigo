# Día 03 — Conversor JSON ↔ CSV

> Herramienta local en Python 3.11+ con CLI e interfaz web para convertir archivos JSON a CSV y CSV a JSON de forma segura, determinista y sin dependencias externas.

## Propósito

Esta herramienta transforma datos tabulares simples entre JSON y CSV desde la línea de comandos o desde una interfaz web local. Ambas entradas usan el mismo núcleo de validación y conversión, por lo que aplican exactamente las mismas reglas de formato.

No utiliza servicios externos, almacenamiento cloud ni credenciales. La interfaz web se sirve en `localhost`; cada conversión se procesa en un directorio temporal y el resultado se entrega para su descarga.

## Características

- Conversión bidireccional mediante los comandos `json-to-csv` y `csv-to-json`.
- JSON de entrada limitado a una lista no vacía de objetos planos.
- CSV con una única fila de cabeceras no vacías y no duplicadas.
- Columnas JSON → CSV en orden de primera aparición de cada clave.
- Celdas vacías para claves JSON ausentes y valores JSON `null`.
- Representación textual estable de booleanos JSON: `true` y `false`.
- Valores CSV preservados como texto al generar JSON, incluidos `0012`, `true` y fechas.
- Compatibilidad con comas, comillas y saltos de línea en celdas mediante la biblioteca estándar `csv`.
- Escritura atómica: un fallo durante la generación no deja una salida parcial.
- Bloqueo de sobrescritura por defecto; `--overwrite` es una confirmación explícita.
- Mensajes de error en español y código de salida `2` para errores de conversión o validación.
- Interfaz web responsive con carga de archivos, ejemplos, estado de procesamiento, vista previa y descarga.
- Límite explícito de 2 MB por archivo en la interfaz web local.

## Alcance

### Incluye

- Archivos `.json` UTF-8 y `.csv` UTF-8.
- JSON cuya raíz sea una lista de objetos planos con valores de texto, números, booleanos o nulos.
- CSV con cabeceras válidas y filas con el mismo o menor número de campos que las cabeceras.
- Filas CSV vacías: se convierten en objetos cuyas claves tienen valores de texto vacíos.

### No incluye

- Aplanamiento ni reconstrucción automática de objetos o listas JSON anidados.
- JSON vacío, raíces JSON que no sean listas u objetos de registro vacíos.
- Inferencia de tipos desde CSV.
- Delimitadores configurables, TSV, XLSX, XML, YAML, Parquet u otros formatos.
- Procesamiento por lotes, recursivo, streaming, API pública o integraciones cloud.

## Requisitos e instalación

- Python 3.11 o superior.
- No hay dependencias de terceros; [`requirements.txt`](requirements.txt) se conserva como registro explícito de esa decisión.

No es necesario instalar paquetes. Ejecute los comandos desde la raíz del repositorio.

## Uso

### Interfaz web local

Desde la raíz del repositorio, inicie el servidor estándar:

```powershell
python projects/day-03-json-csv-converter/src/web.py
```

Abra `http://127.0.0.1:8000` en el navegador. La página permite cargar un JSON o CSV, cambiar la dirección de conversión, usar `people.json` o `catalog.csv` como ejemplos, revisar la salida y descargarla. Detenga el servidor con `Ctrl+C`.

Opcionalmente, cambie host o puerto:

```powershell
python projects/day-03-json-csv-converter/src/web.py --host 127.0.0.1 --port 8080
```

### Línea de comandos

#### JSON a CSV

```powershell
python projects/day-03-json-csv-converter/src/main.py json-to-csv "<entrada.json>" "<salida.csv>"
```

Ejemplo con el fixture incluido:

```powershell
python projects/day-03-json-csv-converter/src/main.py json-to-csv "projects/day-03-json-csv-converter/data/fixtures/people.json" "$env:TEMP\people.csv"
```

#### CSV a JSON

```powershell
python projects/day-03-json-csv-converter/src/main.py csv-to-json "<entrada.csv>" "<salida.json>"
```

Ejemplo con el fixture incluido:

```powershell
python projects/day-03-json-csv-converter/src/main.py csv-to-json "projects/day-03-json-csv-converter/data/fixtures/catalog.csv" "$env:TEMP\catalog.json"
```

#### Sobrescribir una salida existente

La herramienta rechaza un destino existente por seguridad. Tras revisar la ruta, añada `--overwrite`:

```powershell
python projects/day-03-json-csv-converter/src/main.py json-to-csv "<entrada.json>" "<salida.csv>" --overwrite
```

Consulte la ayuda disponible:

```powershell
python projects/day-03-json-csv-converter/src/main.py --help
python projects/day-03-json-csv-converter/src/main.py json-to-csv --help
```

## Ejemplo de comportamiento

Para una lista JSON con registros de claves no uniformes, las cabeceras CSV se forman por primera aparición. Una clave que no aparezca en un registro produce una celda vacía.

Al convertir CSV a JSON, una fila conceptual con `codigo=0012`, `activo=true` y `referencia=2026-09-01` se convierte en un objeto cuyos tres valores son cadenas. Esta regla evita perder ceros iniciales o alterar códigos que parezcan otros tipos.

Los fixtures en [`data/fixtures`](data/fixtures) y la salida de referencia [`data/expected/catalog.json`](data/expected/catalog.json) muestran este comportamiento.

## Errores y seguridad

| Situación | Resultado |
|---|---|
| Ruta de entrada inexistente o extensión incorrecta | Error; no se crea salida. |
| JSON inválido, vacío, anidado o con raíz no permitida | Error descriptivo; no se crea salida. |
| CSV vacío, sin cabeceras, con cabeceras vacías o duplicadas | Error descriptivo; no se crea salida. |
| Una fila CSV tiene más campos que cabeceras | Error que indica la fila; no se crea salida. |
| Directorio de salida inexistente | Error; no se crea salida. |
| Salida existente sin `--overwrite` | Error y conservación íntegra de la salida previa. |
| Fallo al escribir | La salida temporal se elimina y el destino existente no se sustituye. |

## Pruebas y comprobaciones

Ejecute la suite desde la raíz del repositorio:

```powershell
python -m unittest discover -s projects/day-03-json-csv-converter/tests -v
```

La cobertura incluye transformaciones en ambos sentidos, caracteres especiales, saltos de línea, preservación textual, validación de JSON y CSV, extensiones, sobrescritura, ejecución del script en un proceso Python limpio e integración de la capa web (éxito, errores y descarga).

Compruebe la sintaxis de los módulos antes de entregar:

```powershell
python -m compileall projects/day-03-json-csv-converter/src projects/day-03-json-csv-converter/tests
```

No se requiere compilación ni formateador externo: el proyecto usa únicamente la biblioteca estándar.

## Estructura

```text
projects/day-03-json-csv-converter/
├── src/
│   ├── main.py           # CLI y códigos de salida
│   ├── web.py            # Servidor HTTP local y UI web
│   ├── converters.py     # Lectura, conversión y escritura atómica
│   └── validators.py     # Reglas de formato, rutas y seguridad
├── tests/                # Pruebas unitarias e integración CLI/web
├── data/
│   ├── fixtures/         # Entradas locales reproducibles
│   └── expected/         # Salidas de referencia
├── docs/                 # Decisiones técnicas
├── examples/             # Escenarios de uso ejecutables
├── assets/               # Recurso de demo pendiente
├── README.md
├── ROADMAP.md
└── requirements.txt
```

## Decisiones técnicas

Las decisiones de formato, orden de columnas, valores nulos, preservación textual y escritura segura se recogen en [`docs/DECISIONES.md`](docs/DECISIONES.md). La evolución futura se describe en [`ROADMAP.md`](ROADMAP.md).

## Contribución

1. Mantenga el alcance local y sin dependencias externas salvo justificación aprobada.
2. Añada fixtures y pruebas para cada cambio de comportamiento.
3. Preserve la compatibilidad con Python 3.11+ y la política de no sobrescribir por defecto.
4. No añada JSON anidado, inferencia de tipos o formatos adicionales como parte de esta primera versión.

## Estado

Primera versión funcional: CLI e interfaz web local, validaciones compartidas, escritura segura, fixtures y pruebas automatizadas implementadas.
