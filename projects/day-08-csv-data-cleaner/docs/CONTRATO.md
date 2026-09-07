# Contrato v1 — CSV, plan de limpieza y publicación local

## Propósito y alcance

Este contrato fija el comportamiento implementado de la primera versión del **Limpiador de datos CSV**. La v1 procesa exactamente un CSV local con encabezado, aplica únicamente un plan JSON explícito y publica un CSV limpio y un resumen JSON en rutas nuevas y separadas del origen.

El contrato prioriza limpieza mecánica conservadora, trazabilidad y preservación del origen. Cualquier comportamiento no definido en este documento queda fuera de la v1. La evidencia de implementación y entrega se registra en [`ROADMAP.md`](../ROADMAP.md) y [`VERIFICACION_FASE_5.md`](VERIFICACION_FASE_5.md).

## Principios contractuales

- La ejecución es local: no usa red, credenciales, cuentas, telemetría persistente ni servicios externos.
- El origen se abre solo para lectura y no se mueve, sobrescribe, renombra ni elimina.
- Un plan es obligatorio; la herramienta no recomienda ni ejecuta operaciones por inferencia.
- Las transformaciones se limitan a reglas mecánicas definidas aquí; no corrigen semántica, tipos, unidades ni valores de negocio.
- La salida limpia y el resumen son artefactos distintos, explícitos y nuevos; ninguno puede sustituir el origen ni al otro artefacto.
- Las mediciones, el orden de operaciones, los diagnósticos y la serialización deben ser deterministas para la misma entrada y el mismo plan.
- Los informes y errores no incluirán valores de celdas, filas completas, contenido de archivos ni datos personales innecesarios.
- La biblioteca estándar de Python 3.11+ es suficiente para la v1. No se declara ninguna dependencia externa.

## Entorno y límites de recursos

| Aspecto | Regla v1 |
|---|---|
| Runtime | Python 3.11 o superior. |
| Plataforma objetivo | Windows 11 en el entorno del reto; las rutas se interpretan con las convenciones de la plataforma. |
| Unidad de trabajo | Un único archivo CSV por ejecución. No se aceptan directorios, patrones, lotes, stdin ni listas de archivos. |
| Tamaño máximo del origen | 10 MiB (10 × 1024 × 1024 bytes). |
| Filas de datos máximas | 10 000, sin contar encabezado. |
| Columnas máximas | 100. |
| Estrategia de procesamiento | En memoria. Los límites anteriores acotan de manera explícita este diseño simple. |
| Exceso de límite | Error controlado antes de publicar una salida; no se garantiza perfil completo si el límite se descubre durante la lectura. |

La v1 no pretende servir ficheros grandes ni procesamiento en streaming. Un archivo que exceda el límite de tamaño se rechaza antes de decodificarlo; los límites de filas o columnas se rechazan al detectarse.

## CSV de entrada admitido

### Codificación y sintaxis

El origen debe cumplir todas las reglas siguientes:

| Elemento | Regla contractual |
|---|---|
| Codificación | UTF-8 o UTF-8 con BOM. La implementación deberá leer mediante una codificación equivalente a `utf-8-sig`; otras codificaciones se rechazan como error de entrada. |
| Delimitador | Coma ASCII (`,`) exclusivamente. No hay detección automática ni soporte de punto y coma, tabulación u otros dialectos. |
| Comillas | Comilla doble ASCII (`"`) como carácter de comillas CSV estándar. |
| Escape | Se usa el duplicado de comillas estándar CSV; no se admite un carácter de escape alternativo. |
| Terminadores | Se aceptan LF y CRLF al leer. La salida futura usará LF para una referencia reproducible. |
| Espacios tras delimitador | Son contenido del campo; no se ignoran automáticamente. Solo pueden cambiarse mediante `trim_fields`. |
| Encabezado | La primera fila es obligatoria y representa los encabezados. |
| Filas de datos | Cada fila posterior debe tener exactamente el mismo número de campos que el encabezado. |
| Archivo vacío | No admisible: se rechaza porque no contiene encabezado. |
| Solo encabezado | Admisible: representa cero filas de datos. |
| CSV sintácticamente malformado | Se rechaza; no se intenta recuperar, reparar ni adivinar contenido. |

La implementación usa un lector CSV de la biblioteca estándar con el límite de tamaño de campo configurado de forma suficiente para el límite de archivo, sin ampliar las demás reglas del dialecto.

### Encabezados

Los encabezados se preservan en su orden original. Antes de ejecutar el plan, cada encabezado debe ser una cadena no vacía y único por comparación exacta. Un encabezado vacío, un encabezado duplicado exacto o una fila de encabezado ausente es un error controlado; no se crea ninguna salida.

La operación `normalize_headers` puede modificar los encabezados conforme a sus reglas. El conjunto resultante debe volver a ser no vacío y único por comparación exacta. Si la normalización causa una colisión, el plan es incompatible con el origen y toda la ejecución falla antes de publicar resultados.

La v1 no hace comparación insensible a mayúsculas, normalización Unicode, traducción ni generación automática de nombres de columna.

### Valores, filas y seguridad de hoja de cálculo

Todos los campos se tratan como texto. La v1 no infiere, convierte ni valida números, fechas, booleanos, fórmulas, unidades o tipos de negocio.

| Concepto | Definición contractual |
|---|---|
| Valor vacío | Campo cuya cadena es exactamente `""` en el CSV ya decodificado. |
| Marcador faltante | Campo no vacío cuya cadena coincide exactamente con un marcador configurado por `replace_missing_markers`. Por defecto no existe una lista implícita. |
| Fila completamente vacía | Fila de datos donde todos los campos son la cadena vacía exacta antes de ejecutar cualquier operación. Una fila que contiene uno o más espacios no es vacía. |
| Duplicado exacto | Una fila de datos cuyos campos, en el mismo orden, son idénticos a los de una fila anterior conservada tras las operaciones anteriores del plan. |
| Espacio recortable | Cualquier carácter para el que `str.isspace()` es verdadero al inicio o al final de un campo. |

La v1 no modifica celdas que puedan ser interpretadas como fórmulas por hojas de cálculo. En concreto, no antepone apóstrofos ni escapa valores que empiezan por `=`, `+`, `-` o `@`, porque tal modificación alteraría el contenido. El resumen incluirá únicamente un recuento agregado de campos que empiezan por alguno de esos caracteres, llamado `formula_like_cell_count`; nunca incluirá sus valores, posiciones ni filas. Abrir posteriormente el CSV producido en una hoja de cálculo sigue siendo responsabilidad de quien lo use; la v1 advierte mediante ese recuento, pero no garantiza neutralización de CSV injection.

## Plan JSON v1

### Forma, codificación y validación

El plan es un único archivo JSON local codificado en UTF-8, sin BOM. Debe contener un objeto JSON con exactamente estas claves de nivel superior:

```json
{
  "version": 1,
  "operations": []
}
```

| Clave | Tipo | Regla |
|---|---|---|
| `version` | entero JSON | Obligatorio y exactamente `1`. |
| `operations` | lista JSON | Obligatoria, no vacía y con un máximo de cinco operaciones. |

No se permiten claves adicionales en el objeto raíz ni en una operación. JSON inválido, una codificación no UTF-8, una raíz no objeto, tipos incorrectos, claves desconocidas, una versión distinta, operaciones vacías o más de cinco operaciones son errores de plan. Ninguna salida se publica ante estos errores.

Cada elemento de `operations` debe ser un objeto con la clave obligatoria `operation`. No puede aparecer dos veces la misma operación. La lista se declara en cualquier orden, pero la implementación debe validarla y ejecutarla en el orden contractual fijo de la sección siguiente. Esta elección evita que el resultado dependa de una reordenación accidental del archivo de plan.

### Operaciones autorizadas y orden fijo

La v1 acepta exclusivamente estas operaciones:

| Orden | Identificador | Claves exactas | Semántica | Medida de resultado |
|:---:|---|---|---|---|
| 1 | `normalize_headers` | `operation` | Recorta espacios recortables de ambos extremos de cada encabezado. No cambia caracteres internos, caso ni Unicode. | `headers_changed`: número de encabezados cuyo texto cambió. |
| 2 | `drop_empty_rows` | `operation` | Elimina filas completamente vacías según la definición anterior, evaluada sobre el CSV de origen antes de cualquier operación. | `rows_removed`: número de filas eliminadas. |
| 3 | `trim_fields` | `operation` | Recorta espacios recortables de ambos extremos de cada campo de todas las filas aún presentes. No toca encabezados. | `fields_changed`: número de campos cuyo texto cambió. |
| 4 | `replace_missing_markers` | `operation`, `markers` | Para cada campo de filas aún presentes, si coincide exactamente con un marcador configurado, lo reemplaza por la cadena vacía. La coincidencia se evalúa después de `trim_fields` si ambas se solicitan. | `fields_replaced`: número de campos reemplazados. |
| 5 | `drop_exact_duplicates` | `operation` | Conserva la primera aparición de cada fila exacta y elimina posteriores apariciones, después de todas las operaciones anteriores solicitadas. | `rows_removed`: número de filas eliminadas. |

`normalize_headers`, `drop_empty_rows`, `trim_fields` y `drop_exact_duplicates` no admiten claves adicionales. Para `replace_missing_markers`, `markers` es obligatorio y debe ser una lista no vacía de entre uno y diez textos JSON no vacíos, únicos por comparación exacta. Un marcador vacío se prohíbe para impedir confundir valores ya vacíos con cambios solicitados.

La aplicación no añade operaciones, parámetros opcionales, selectores de columnas, valores por defecto implícitos ni reglas de ejecución condicional. Un plan puede solicitar una operación que no produzca cambios: se considera éxito y registra el contador `0`.

### Compatibilidad del plan

Antes de transformar o crear artefactos temporales, la implementación:

1. Leer y validar por completo el plan JSON.
2. Validar el CSV y sus encabezados originales.
3. Evaluar si `normalize_headers`, cuando se solicita, produciría encabezados vacíos o duplicados.
4. Rechazar la solicitud si cualquier operación es incompatible con el origen o excede los límites.

No existe una operación configurable por columna en la v1; por ello, no hay referencias de columna que validar. La ejecución no debe publicar resultados si falla cualquiera de estas comprobaciones previas.

## Perfil e informe JSON

El perfil se calcula sobre los datos originales ya validados, antes de aplicar transformaciones. El resumen JSON de una ejecución correcta debe serializarse en UTF-8, con claves ordenadas y sin campos de fecha, identificadores aleatorios, rutas temporales, contenido de celdas ni otros datos no deterministas.

La estructura de nivel superior es exactamente:

```text
{
  "status",
  "source",
  "plan",
  "profile_before",
  "profile_after",
  "operations",
  "warnings"
}
```

| Clave | Tipo y contenido permitido |
|---|---|
| `status` | Cadena fija `"success"`. |
| `source` | Objeto con `file_name` —solo el nombre base de la ruta de origen—, `size_bytes`, `data_row_count` y `column_count`. No incluye ruta completa ni contenido. |
| `plan` | Objeto con `version: 1` y `requested_operations`: lista de identificadores en el orden contractual fijo. |
| `profile_before` | Objeto con `headers`, `empty_value_count`, `empty_row_count`, `exact_duplicate_row_count` y `formula_like_cell_count`. `headers` es una lista de encabezados permitida porque forma parte de la estructura pública del CSV; no incluye filas ni valores. |
| `profile_after` | Objeto con las mismas claves que `profile_before`, calculado sobre el resultado limpio antes de escribirlo. |
| `operations` | Lista ordenada de resultados, cada uno con `operation` y exactamente la métrica definida en la tabla de operaciones. |
| `warnings` | Lista ordenada de códigos de advertencia. En v1 solo puede contener `"formula_like_cells_present"` si el perfil posterior tiene un recuento mayor que cero; de otro modo es una lista vacía. |

`empty_value_count` cuenta únicamente campos vacíos exactos. `empty_row_count` usa la definición de fila completamente vacía de este contrato. `exact_duplicate_row_count` cuenta filas que son duplicadas de alguna aparición previa bajo comparación exacta, sin eliminar filas; el cálculo respeta el orden de la entrada. `formula_like_cell_count` cuenta campos no vacíos cuyo primer carácter es `=`, `+`, `-` o `@`.

El resumen se produce solo tras completar correctamente la transformación y publicar ambos artefactos. En una ejecución fallida no se escribe un resumen de error como sustituto de la salida prevista; los errores se comunican por la CLI.

## Rutas, salidas y publicación segura

### Entradas y salidas CLI

La interfaz v1 tiene una única forma:

```text
python src/main.py clean <SOURCE_CSV> <PLAN_JSON> <OUTPUT_CSV> <SUMMARY_JSON>
```

| Elemento | Obligatorio | Regla |
|---|:---:|---|
| `clean` | Sí | Solicita una única limpieza v1. |
| `<SOURCE_CSV>` | Sí | Ruta explícita a un archivo CSV de entrada admisible. |
| `<PLAN_JSON>` | Sí | Ruta explícita a un archivo JSON de plan admisible. |
| `<OUTPUT_CSV>` | Sí | Ruta explícita y nueva para el CSV limpio. |
| `<SUMMARY_JSON>` | Sí | Ruta explícita y nueva para el resumen. |
| Argumentos u opciones extra | No permitidos | Error de uso sin crear artefactos. |

Las rutas relativas se resuelven respecto del directorio de trabajo. Antes de procesar, la implementación normaliza las rutas y verifica:

- El origen y el plan existen, son archivos regulares y son legibles.
- Las dos rutas de salida no existen y sus directorios padre existen, son directorios regulares y permiten crear archivos.
- Origen, plan, salida CSV y salida JSON representan cuatro ubicaciones distintas.
- Ninguna salida es un enlace simbólico, junction o ruta que se resuelva sobre el origen o el plan.
- Las salidas no pueden tener el mismo nombre de archivo ni ser la misma ubicación tras normalización.

La v1 no crea directorios padre, no sobrescribe resultados existentes y no admite rutas de directorio como origen, plan o salida. Las rutas de red solo están soportadas si el sistema las presenta como rutas regulares y todas las comprobaciones del contrato pueden aplicarse; la suite estándar no dependerá de ellas.

### Publicación

Tras validar ruta, plan y CSV, el proceso construye los resultados en archivos temporales propios dentro de los directorios padre de sus salidas. Solo después de generar con éxito el CSV limpio y un resumen que corresponda a ese resultado publica ambos archivos en sus rutas finales mediante la operación más segura disponible en el mismo sistema de archivos.

Si falla la validación, lectura, transformación, serialización, escritura o publicación:

- no se debe modificar el origen, el plan ni una salida existente;
- no se debe presentar una salida parcial como resultado correcto;
- la implementación debe intentar eliminar únicamente los temporales creados por esa ejecución;
- un fallo de limpieza puede comunicarse como advertencia breve, sin inspeccionar ni borrar otros archivos;
- la v1 no garantiza atomicidad de dos archivos frente a corte eléctrico, caída del proceso, antivirus o concurrencia externa.

## Salidas, errores y códigos de retorno

La CLI no imprime contenido de celdas, filas, plan completo, excepciones sin filtrar, rutas temporales ni trazas por defecto. Puede mencionar el nombre base del origen y las rutas finales solicitadas para que la persona usuaria corrija una operación, siempre que no liste contenido.

| Situación | stdout | stderr | Código |
|---|---|---|:---:|
| Ejecución correcta | Confirmación breve y las dos rutas finales. | Vacío. | `0` |
| Argumentos faltantes, subcomando u opción no válida | Vacío. | Mensaje de uso accionable. | `2` |
| Ruta, permiso, tamaño, límite CSV, codificación, sintaxis CSV, encabezado o plan no admisible | Vacío. | Diagnóstico breve y seguro. | `1` |
| Incompatibilidad del plan, colisión de encabezados o salida existente | Vacío. | Diagnóstico breve y seguro. | `1` |
| Fallo durante transformación, escritura, publicación o limpieza | Vacío. | Diagnóstico breve sin traza por defecto; advertencia de limpieza si aplica. | `1` |
| Interrupción controlada | Vacío. | Mensaje breve de operación interrumpida. | `1` |

El código `0` significa únicamente que ambos artefactos contractuales se publicaron correctamente. No existe modo parcial, dry-run, confirmación interactiva, salida alternativa, registro persistente ni canal de red.

## Privacidad, datos y registros

- El CSV debe considerarse potencialmente sensible aunque sea local.
- No se versionarán datos reales, datos personales, secretos ni capturas de contenido real en fixtures, pruebas, ejemplos, referencias o demo.
- El informe usa recuentos y estructura; no contiene valores de datos ni filas completas. Los encabezados se permiten como metadatos de estructura, pero los fixtures deberán usar nombres inocuos.
- La aplicación no habilita logging persistente. Los diagnósticos no interpolan valores de celdas, texto de excepciones sin filtrar ni contenido del plan.
- Las rutas explícitas podrán aparecer en mensajes solo cuando sean necesarias para resolver un error; no se incluirán rutas temporales.
- La v1 no analiza macros, fórmulas, estilos o contenido ejecutable: trata los campos como texto.

## Capacidades excluidas y aplazadas

Quedan fuera de la v1: autodetección de dialecto; otros delimitadores o codificaciones; lectura sin encabezado; reparación de CSV malformado; selección de columnas; normalización Unicode; limpieza por expresiones regulares; inferencia o conversión de tipos; imputación; deduplicación difusa; integración con hojas de cálculo, bases de datos, APIs, cloud o IA; lotes y directorios; streaming; historial; telemetría; sobrescritura; y neutralización automática de CSV injection.

La v1 tampoco conserva metadatos de archivos, permisos, tiempos ni formato ajeno a los datos CSV. La compatibilidad más amplia solo puede proponerse en una fase futura con nuevo contrato y pruebas.

## Decisiones verificadas de Fase 1

- Python, plataforma, límites, estrategia en memoria y condiciones de rechazo están definidos.
- Dialecto, codificación, BOM, encabezados, filas irregulares, valores vacíos, filas vacías y duplicados tienen semántica inequívoca.
- Las cinco operaciones, sus parámetros, orden, precondiciones y contadores están cerrados sin reglas implícitas.
- El esquema JSON del plan y del resumen está definido, incluida la política contra claves desconocidas y datos sensibles.
- Origen, plan, salidas, colisiones, relaciones de rutas, archivos temporales, publicación y fallos están delimitados.
- La CLI `clean` y todos sus códigos de retorno están documentados e implementados.
- La política de campos interpretables como fórmula está decidida y sus límites están declarados.
- Esta fase no agrega código funcional, fixtures, resultados de referencia, dependencias, configuración ejecutable ni pruebas funcionales.

## Decisiones aplazadas

- Soporte para delimitadores, dialectos, codificaciones o encabezados alternativos.
- Streaming, límites superiores y desempeño con archivos grandes.
- Selección de columnas, regex, normalización Unicode y reglas de limpieza configurables adicionales.
- Modo de previsualización o confirmación de un plan.
- Neutralización configurable de valores que podrían ser interpretados por hojas de cálculo.
- Sobrescritura explícita, versionado de salidas, recuperación de operaciones incompletas y auditoría persistente.
- API, interfaz gráfica, automatización, procesamiento por lotes e integraciones externas.
