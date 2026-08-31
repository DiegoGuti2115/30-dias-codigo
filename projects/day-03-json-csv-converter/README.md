# Día 03 — Conversor JSON ↔ CSV

> Herramienta CLI local en Python para convertir archivos JSON a CSV y CSV a JSON de forma predecible y verificable.

## Propósito

El proyecto resuelve una necesidad concreta de intercambio de datos tabulares: transformar colecciones simples de registros entre JSON y CSV sin depender de servicios externos, navegador ni almacenamiento cloud.

La primera versión se ejecutará exclusivamente en el equipo local. Recibirá una ruta de entrada y una ruta de salida explícitas, validará el formato de origen y generará el archivo convertido cuando el destino sea seguro.

## Características previstas

- Conversión bidireccional entre JSON y CSV.
- Ejecución mediante una interfaz de línea de comandos local.
- Compatibilidad con JSON cuya raíz sea una lista de objetos planos.
- Lectura y generación de CSV con una fila de cabeceras.
- Determinación estable de las columnas a partir de las claves encontradas en los registros JSON.
- Conservación de las cabeceras CSV como claves en la salida JSON.
- Interpretación de todos los valores de CSV como texto al convertir a JSON.
- Validación anticipada de entradas y rutas para evitar salidas incompletas o ambiguas.
- Bloqueo de sobrescritura de archivos de salida por defecto; se prevé una opción explícita para autorizarla.
- Uso planificado de la biblioteca estándar de Python, sin dependencias de terceros.

## Alcance de la primera versión

### Incluye

- Conversión de un archivo JSON válido a un archivo CSV.
- Conversión de un archivo CSV válido a un archivo JSON.
- JSON con una lista de objetos planos: cada registro es un objeto y sus valores son escalares compatibles con la representación acordada.
- CSV con cabeceras no vacías y no duplicadas.
- Codificación UTF-8 y manejo de comillas, delimitadores y saltos de línea mediante el soporte estándar de CSV.
- Mensajes de error claros ante problemas de formato, datos no admitidos, rutas inválidas o destinos ya existentes.
- Fixtures, resultados esperados y pruebas automatizadas locales.

### No incluye

- Aplanamiento automático de objetos o listas JSON anidados.
- JSON cuya raíz sea un objeto único, una lista de valores o cualquier valor que no sea una lista de objetos planos.
- Inferencia de tipos desde CSV: números, booleanos, fechas, valores nulos y ceros iniciales permanecerán como texto en JSON.
- Procesamiento por lotes, exploración recursiva de directorios o vigilancia de carpetas.
- Interfaz gráfica, API web, autenticación, persistencia remota o integraciones cloud.
- Formatos adicionales como XML, YAML, XLSX, Parquet o TSV.

## Requisitos

- Python 3.11 o superior.
- Acceso de lectura al archivo de entrada y de escritura al directorio de salida.
- No se requieren credenciales, variables de entorno ni servicios externos.

## Instalación prevista

La primera versión no requerirá paquetes externos. Tras clonar el repositorio, la ejecución prevista será desde la raíz mediante el intérprete de Python disponible en el sistema.

El archivo [`requirements.txt`](requirements.txt) queda incluido para mantener las dependencias aisladas y documentar que la primera versión no necesita instalaciones adicionales.

## Uso previsto de la CLI

La interfaz aún no está implementada. Se documenta el contrato previsto para que la implementación, las pruebas y los ejemplos compartan una única expectativa.

Se contemplan dos operaciones:

- `json-to-csv`: convierte un archivo JSON permitido a CSV.
- `csv-to-json`: convierte un archivo CSV con cabeceras a JSON.

Cada operación requerirá:

- una ruta de entrada;
- una ruta de salida;
- una opción explícita prevista, como `--overwrite`, únicamente cuando se acepte reemplazar un destino existente.

### Conversión JSON a CSV

Flujo conceptual:

1. La persona indica un archivo JSON de entrada y una ruta CSV de salida.
2. La herramienta comprueba que el JSON se pueda analizar y que su raíz sea una lista de objetos planos.
3. Reúne las claves de los objetos para formar las cabeceras CSV en un orden estable.
4. Escribe una fila por objeto; las claves ausentes se representan como celdas vacías.
5. Si la salida ya existe, la operación se detiene salvo que se autorice expresamente la sobrescritura.

### Conversión CSV a JSON

Flujo conceptual:

1. La persona indica un archivo CSV de entrada y una ruta JSON de salida.
2. La herramienta verifica que exista una fila de cabeceras válidas.
3. Convierte cada fila en un objeto cuyas claves son las cabeceras.
4. Genera una lista JSON de objetos planos.
5. Todos los valores leídos desde CSV se mantienen como texto, incluidas secuencias que parezcan números, booleanos, fechas o valores nulos.

## Ejemplos conceptuales

### JSON a CSV

Entrada conceptual en [`data/fixtures`](data/fixtures): una lista de registros con las claves `id`, `nombre` y `ciudad`.

Resultado conceptual en [`data/expected`](data/expected): un CSV con las cabeceras `id`, `nombre` y `ciudad`, seguido de una fila por registro. Si un registro no aporta `ciudad`, la celda correspondiente queda vacía.

### CSV a JSON

Entrada conceptual en [`data/fixtures`](data/fixtures): un CSV con las cabeceras `codigo`, `activo` y `referencia`.

Resultado conceptual en [`data/expected`](data/expected): una lista de objetos donde valores como `0012`, `true` y `2026-09-01` permanecen como cadenas de texto. Esta decisión evita conversiones implícitas y pérdida de información.

## Comportamiento esperado

| Situación | Comportamiento previsto |
|---|---|
| JSON válido con lista de objetos planos | Conversión a CSV permitida. |
| JSON con objeto anidado o lista anidada | Rechazo con un mensaje que indique el límite del formato. |
| CSV sin cabeceras | Rechazo antes de crear la salida. |
| Cabecera CSV vacía o duplicada | Rechazo para prevenir claves ambiguas o pérdida de datos. |
| Archivo de entrada inexistente o no legible | Error accionable; no se crea salida. |
| Directorio de salida inexistente o sin permisos | Error accionable; no se crea salida. |
| Archivo de salida ya existente | Bloqueo por defecto. Solo una opción explícita prevista permitirá reemplazarlo. |
| CSV con valores que parecen tipos no textuales | Conversión a cadenas de texto en JSON. |

## Manejo de errores

La implementación futura deberá validar todo lo necesario antes de escribir el archivo final. Los errores deberán identificar la causa y, cuando sea posible, la ruta o fila implicada. Como mínimo se cubrirán:

- sintaxis JSON inválida;
- raíz JSON no admitida;
- objetos JSON anidados o valores no escalares no admitidos;
- CSV vacío, sin cabeceras o con cabeceras inválidas;
- errores de codificación, lectura o escritura;
- extensiones incoherentes con la operación solicitada;
- colisión con una salida existente sin autorización explícita.

No se considera aceptable modificar un archivo de entrada ni sustituir una salida existente por defecto.

## Estructura del proyecto

```text
projects/day-03-json-csv-converter/
├── src/                 # Punto de entrada, conversión y validaciones futuras
├── tests/               # Pruebas automatizadas futuras
├── docs/                # Decisiones y documentación complementaria
├── data/
│   ├── fixtures/        # Entradas reproducibles para pruebas y demo
│   └── expected/        # Salidas de referencia verificables
├── examples/            # Materiales de uso y escenarios conceptuales
├── assets/              # GIF, vídeo y recursos de la demo
├── README.md            # Documentación principal
├── ROADMAP.md           # Plan de implementación y evolución
├── requirements.txt     # Dependencias del proyecto
└── .gitignore           # Exclusiones locales de desarrollo
```

Los módulos Python previstos en [`src/main.py`](src/main.py), [`src/converters.py`](src/converters.py) y [`src/validators.py`](src/validators.py), así como los archivos de prueba en [`tests/test_converters.py`](tests/test_converters.py) y [`tests/test_cli.py`](tests/test_cli.py), se mantienen vacíos en esta etapa. No contienen implementación, comentarios ni código ejecutable.

## Datos de prueba y ejemplos

- [`data/fixtures`](data/fixtures) alojará archivos de entrada representativos y mínimos.
- [`data/expected`](data/expected) conservará las salidas de referencia correspondientes.
- [`examples`](examples) reunirá escenarios de uso que no sustituyen las pruebas automatizadas.
- [`assets`](assets) almacenará la demostración visual final y su recurso fuente.

Los fixtures no deben contener datos personales, credenciales ni información sensible.

## Pruebas previstas

La suite futura comprobará como mínimo:

- conversión JSON a CSV con claves uniformes y no uniformes;
- conversión CSV a JSON con preservación textual de los valores;
- filas con comas, comillas y saltos de línea;
- rechazo de JSON anidado y raíces no permitidas;
- rechazo de CSV sin cabeceras, con cabeceras vacías o duplicadas;
- protección frente a sobrescrituras;
- mensajes y códigos de salida de la CLI.

## Contribución

1. Revise el alcance de la primera versión y el plan en [`ROADMAP.md`](ROADMAP.md).
2. Mantenga la herramienta local, determinista y sin dependencias externas salvo una justificación explícita.
3. Añada o actualice fixtures y pruebas con cada cambio funcional.
4. Documente cualquier cambio de comportamiento, especialmente si afecta a la representación de valores o a la seguridad de las rutas de salida.
5. No añada soporte de JSON anidado, inferencia de tipos u otros formatos dentro de la primera versión sin aprobar antes la ampliación de alcance.

## Estado

El proyecto se encuentra en fase de preparación estructural y documental. La implementación de la CLI, las conversiones y las pruebas está planificada y no se ha iniciado en los archivos Python.
