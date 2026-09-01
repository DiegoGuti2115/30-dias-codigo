# Contrato v1 — Formatos de entrada y CLI

## Propósito

Este documento fija el comportamiento de la primera versión del Analizador de logs antes de implementar código. El contrato cubre un único archivo local por ejecución y dos formatos elegidos explícitamente: texto común y JSON Lines.

## Principios

- La CLI no detecta formatos automáticamente: la persona usuaria debe elegir uno.
- El archivo se procesa secuencialmente, una línea por vez.
- Cada línea representa como máximo un evento.
- Los datos de entrada no se modifican y la primera versión no genera archivos de salida.
- Las líneas inválidas se omiten del análisis, se contabilizan y se muestran en el resumen.
- La primera versión usa UTF-8. Un archivo que no pueda decodificarse con UTF-8 se considera un error de ejecución.
- Los eventos se conservan en su orden de aparición para el reporte filtrado.

## Vocabulario normalizado

Cada evento válido tendrá, internamente, estos campos:

| Campo | Tipo previsto | Obligatorio | Significado |
|---|---|:---:|---|
| `line_number` | entero positivo | Sí | Línea física de origen, empezando en 1. |
| `timestamp` | texto | Sí | Marca temporal tal como se recibió, tras validación sintáctica. |
| `level` | texto normalizado | Sí | Nivel de severidad reconocido en mayúsculas. |
| `message` | texto | Sí | Mensaje no vacío del evento. |
| `metadata` | mapeo | No | Campos JSON Lines adicionales que v1 no agrega ni presenta. |

La v1 valida que exista una marca temporal no vacía; no convertirá zonas horarias ni ordenará por fecha. La especificación exacta de la marca temporal se limita a ISO 8601 en JSON Lines y al mismo texto delimitado en el formato común.

## Niveles de severidad

| Nivel normalizado | Orden | Entra en el reporte de errores |
|---|:---:|:---:|
| `DEBUG` | 10 | No |
| `INFO` | 20 | No |
| `WARNING` | 30 | No |
| `ERROR` | 40 | Sí |
| `CRITICAL` | 50 | Sí |

- La comparación no distingue mayúsculas de minúsculas en la entrada y normaliza a mayúsculas.
- Un nivel fuera de esta lista invalida la línea.
- El reporte de errores de la v1 usa un umbral fijo de `ERROR`; no habrá una opción de umbral configurable inicialmente.

## Formato `common`

### Gramática

Cada evento válido ocupa una línea con exactamente tres segmentos principales:

```text
<TIMESTAMP> <LEVEL> <MESSAGE>
```

- `TIMESTAMP`: texto ISO 8601 sin espacios. Ejemplo: `2026-09-01T08:30:00Z`.
- `LEVEL`: uno de los niveles definidos arriba.
- `MESSAGE`: texto no vacío; puede contener espacios y se conserva completo después del segundo separador.
- Los tres segmentos se separan mediante uno o más espacios horizontales.
- Las líneas vacías o compuestas solo por espacios se consideran inválidas y se contabilizan.

### Ejemplos conceptuales

```text
2026-09-01T08:30:00Z INFO Servicio iniciado
2026-09-01T08:31:04+02:00 ERROR No se pudo conectar con la base de datos
```

No se admiten prefijos arbitrarios, pilas multilínea, campos entre corchetes ni continuaciones de línea en la primera versión. Estas variantes requieren perfiles de parser futuros.

## Formato `jsonl`

Cada línea no vacía debe ser un objeto JSON independiente. Se requieren estos campos:

| Campo JSON | Tipo | Regla |
|---|---|---|
| `timestamp` | cadena | No vacía y con sintaxis ISO 8601. |
| `level` | cadena | Debe normalizar a un nivel admitido. |
| `message` | cadena | No vacía. |

- Las claves adicionales se preservarán como metadatos internos, sin afectar el resumen v1.
- Una línea que no sea JSON válido, no sea un objeto, carezca de un campo requerido o lo tenga con tipo inválido se contabiliza como inválida.
- Una línea vacía también se contabiliza como inválida para mantener trazabilidad del archivo.

Ejemplo conceptual:

```json
{"timestamp":"2026-09-01T08:31:04Z","level":"error","message":"No se pudo conectar","service":"api"}
```

## Interfaz de línea de comandos propuesta

La primera implementación expondrá un único comando con esta forma:

```text
python src/main.py analyze <LOG_PATH> --format <common|jsonl> [--errors]
```

| Elemento | Obligatorio | Comportamiento |
|---|:---:|---|
| `analyze` | Sí | Subcomando único de la v1. |
| `<LOG_PATH>` | Sí | Ruta a un archivo local UTF-8 legible. |
| `--format` | Sí | Selecciona `common` o `jsonl`; no hay autodetección. |
| `--errors` | No | Añade al resumen el reporte de eventos `ERROR` y `CRITICAL`, conservando el orden de entrada. |

Sin `--errors`, la salida contiene únicamente el resumen. El número de mensajes frecuentes mostrado se fijará en tres durante la implementación y se documentará junto con el formato exacto de salida. La v1 no acepta glob, directorios, stdin, filtros temporales ni archivos de resultado.

## Resumen y reporte previstos

El resumen de una ejecución correcta incluirá:

1. Ruta y formato procesado.
2. Total de líneas leídas.
3. Total de eventos válidos e inválidos.
4. Conteo por nivel, incluido cero para niveles sin eventos válidos.
5. Hasta tres mensajes más frecuentes, con desempate por primera aparición.

Con `--errors`, se agregará un reporte de los eventos `ERROR` y `CRITICAL` con número de línea, timestamp, nivel y mensaje. Si no existen coincidencias, se indicará explícitamente sin tratarlo como un error.

## Errores y códigos de salida

| Situación | Resultado previsto | Código |
|---|---|:---:|
| Ejecución válida, incluso con líneas inválidas | Resumen en salida estándar. | 0 |
| Argumentos incompletos o formato no permitido | Mensaje de uso accionable. | 2 |
| Ruta inexistente, no es archivo, no es legible o no se puede decodificar | Error de entrada en salida de error. | 1 |
| Archivo sin eventos válidos | Error de análisis en salida de error; no hay resumen parcial. | 1 |
| Error inesperado de lectura | Error breve en salida de error, sin traza por defecto. | 1 |

Las líneas inválidas no causan por sí mismas una salida no válida; se reportarán como parte del resumen. El detalle por línea inválida no se imprimirá en v1 para no exponer potencialmente datos sensibles ni saturar la terminal.

## Criterios de aceptación

- Un fixture `common` válido con los cinco niveles produce conteos correctos.
- Un fixture `jsonl` válido acepta claves adicionales sin alterar las métricas base.
- Cada línea inválida aumenta el contador de inválidas y no aparece en el reporte de errores.
- `--errors` muestra solo `ERROR` y `CRITICAL` en el orden original.
- Un archivo vacío o compuesto únicamente por líneas inválidas finaliza con código 1.
- Una ruta inexistente, un formato inválido y una codificación no UTF-8 finalizan con el código especificado.
- Ninguna ejecución modifica el archivo de entrada ni requiere configuración, secretos o conectividad externa.

## Decisiones aplazadas

- Soporte de otros timestamps, niveles personalizados y alias como `WARN`.
- Perfiles para Nginx, Apache, Python logging, Docker, Kubernetes u otros proveedores.
- Autodetección de formato.
- Exportación del resumen, filtros configurables, múltiples archivos y seguimiento en tiempo real.
