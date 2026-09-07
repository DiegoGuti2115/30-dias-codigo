# Día 08 — Limpiador de datos CSV

> Microproyecto del reto **30 Días, 30 Proyectos**. **Estado: v1 entregable — Fases 0 a 5 completadas.**

Utilidad local de Python para aplicar una limpieza mecánica, explícita y no destructiva a **un único CSV**. Recibe un plan JSON v1, publica un CSV limpio y un resumen JSON determinista, y nunca sobrescribe el origen.

La especificación normativa está en [`docs/CONTRATO.md`](docs/CONTRATO.md). Los escenarios y referencias sintéticas están en [`docs/ESCENARIOS_FASE_2.md`](docs/ESCENARIOS_FASE_2.md), [`data/fixtures`](data/fixtures) y [`data/expected`](data/expected).

## Requisitos e instalación

- Python **3.11+**.
- Windows 11 es la plataforma objetivo del reto.
- Solo se utiliza la biblioteca estándar: no hay dependencias, red, credenciales, cuentas ni configuración adicional.

No es necesario instalar paquetes. Desde [`projects/day-08-csv-data-cleaner`](.):

```text
python --version
python -m unittest discover -s tests -v
```

## Uso

La única forma admitida es:

```text
python src/main.py clean <SOURCE_CSV> <PLAN_JSON> <OUTPUT_CSV> <SUMMARY_JSON>
```

Las rutas relativas se resuelven desde el directorio de trabajo. El origen y el plan deben existir, ser archivos regulares y legibles. Las dos salidas deben ser rutas nuevas, con directorios padre existentes, y las cuatro ubicaciones deben ser distintas.

Ejemplo reproducible:

```text
mkdir tmp
python src/main.py clean data/fixtures/happy-input.csv data/fixtures/plan-all-operations.json tmp/happy-cleaned.csv tmp/happy-summary.json
```

En éxito, la CLI escribe únicamente las dos rutas finales en stdout y devuelve `0`. No imprime filas, celdas, el plan completo, trazas ni rutas temporales.

| Situación | Canal | Código |
|---|---|:---:|
| Ambos artefactos publicados | stdout | `0` |
| Error de ruta, CSV, plan, límites, transformación o publicación | stderr | `1` |
| Sintaxis, subcomando u opciones inválidas | stderr | `2` |

La guía con comprobaciones byte a byte, escenario sin cambios, error reproducible y limpieza se encuentra en [`examples/USO.md`](examples/USO.md).

## Plan JSON v1

El plan usa UTF-8 sin BOM y un esquema cerrado:

```json
{
  "version": 1,
  "operations": [
    {"operation": "trim_fields"}
  ]
}
```

Las operaciones se validan y ejecutan siempre en este orden contractual, aunque se declaren en otro orden:

1. `normalize_headers`: recorta los extremos de cada encabezado.
2. `drop_empty_rows`: elimina filas cuyos campos eran todos vacíos en el origen.
3. `trim_fields`: recorta los extremos de los campos de filas conservadas.
4. `replace_missing_markers`: sustituye por vacío los marcadores explícitos de `markers`.
5. `drop_exact_duplicates`: conserva la primera fila exacta después de los pasos anteriores.

Una operación válida puede no modificar datos y seguirá siendo un éxito con contador `0`. El plan no admite operaciones repetidas, desconocidas ni parámetros adicionales. Consulta la definición completa y las precondiciones en [`docs/CONTRATO.md`](docs/CONTRATO.md).

## Entradas, resultados y límites

La v1 admite CSV UTF-8 o UTF-8 con BOM, delimitado exclusivamente por comas, con comillas CSV estándar y encabezado obligatorio. Lee LF y CRLF; publica CSV UTF-8 con LF y JSON UTF-8, claves ordenadas, dos espacios de indentación y salto de línea final.

Límites contractuales:

| Recurso | Máximo |
|---|---:|
| Tamaño del CSV origen | 10 MiB |
| Filas de datos | 10 000 |
| Columnas | 100 |

El resumen JSON incluye solo estructura y contadores: nombre base y tamaño del origen, plan efectivo, perfiles anterior/posterior, resultados por operación y advertencias. Nunca incluye filas ni valores de celdas. Los encabezados se incluyen como metadato estructural. Los valores que empiezan por `=`, `+`, `-` o `@` no se modifican; solo se cuentan para advertir sobre el riesgo al abrir el resultado en una hoja de cálculo.

## Seguridad y publicación

- El origen y el plan se leen; no se mueven, renombran, borran ni sobrescriben.
- Las salidas no pueden existir, coincidir entre sí ni resolver sobre una entrada.
- No se crean directorios padre ni se sobrescriben resultados existentes.
- Antes de publicar, CSV y resumen se escriben en temporales propios dentro de sus directorios de destino.
- Si falla la segunda publicación, se elimina el resultado propio ya publicado y los temporales propios. La v1 no promete atomicidad de dos archivos ante corte eléctrico, caída del proceso, antivirus o concurrencia externa.
- No existe telemetría, logging persistente, servicios remotos ni secretos.

## Alcance excluido

No incluye autodetección de dialecto, otros delimitadores o codificaciones, CSV sin encabezado, reparación de CSV malformado, streaming, selección de columnas, expresiones regulares, inferencia de tipos, limpieza semántica, deduplicación difusa, sobrescritura, lotes, directorios, API, UI, cloud ni formatos distintos de CSV.

Un punto y coma dentro de un campo no activa autodetección: bajo el dialecto de coma es contenido válido de un campo.

## Verificación y demo

La suite cubre núcleo, validación de plan, CLI, rutas, límites, publicación, regresión contra referencias, determinismo y ausencia de artefactos propios. La verificación de entrega se documenta en [`docs/VERIFICACION_FASE_5.md`](docs/VERIFICACION_FASE_5.md).

El guion de demo local, de hasta 15 segundos y sin datos sensibles, está en [`assets/DEMO_15S.md`](assets/DEMO_15S.md). El texto publicable, limitado a afirmaciones verificables, está en [`docs/LINKEDIN_DIA_08.md`](docs/LINKEDIN_DIA_08.md).

## Estructura

```text
projects/day-08-csv-data-cleaner/
├── assets/                    # Guion y fuente de demo local
├── data/
│   ├── expected/              # Referencias deterministas
│   └── fixtures/              # Entradas sintéticas e inocuas
├── docs/                      # Contrato, escenarios y evidencia
├── examples/                  # Uso manual reproducible
├── src/
│   ├── csv_profile.py         # Carga y perfil CSV
│   ├── plan.py                # Validación del plan JSON
│   ├── cleaner.py             # Transformaciones puras
│   ├── output.py              # Rutas y publicación segura
│   └── main.py                # CLI contractual clean
└── tests/                     # Unidad, integración y entrega
```
