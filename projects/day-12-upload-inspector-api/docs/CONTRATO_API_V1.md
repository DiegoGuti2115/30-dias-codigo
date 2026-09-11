# Contrato API v1 — Inspección de archivos

## Estado y compatibilidad

Este documento es la fuente de verdad pública de la versión 1. Cierra las decisiones de la Fase 1 de [ROADMAP.md](../ROADMAP.md) y prevalece sobre cualquier detalle interno de una implementación posterior.

- **Versión de contrato:** v1.
- **Ruta pública:** `POST /api/v1/inspect`.
- **Formato de solicitud:** `multipart/form-data`.
- **Formato de respuesta:** `application/json; charset=utf-8`.
- **Sin estado:** cada solicitud se procesa independientemente; la API no persiste archivos, resultados ni metadatos.
- **Compatibilidad:** cualquier cambio incompatible de ruta, campos obligatorios, límites, códigos o semántica requerirá una nueva versión. Solo podrán añadirse campos opcionales de respuesta sin cambiar la versión.

## Alcance y garantías

La versión 1 inspecciona exactamente un archivo recibido localmente en una solicitud multipart. Devuelve el tamaño, el tipo de medio declarado por el cliente, la extensión deducida del nombre, comprobaciones de seguridad del nombre y la huella SHA-256 del contenido.

La API **no** abre, ejecuta, descomprime, interpreta, almacena ni intenta identificar el formato real del contenido. El tipo de medio y la extensión son metadatos no confiables; una respuesta correcta no certifica inocuidad, autenticidad, formato real ni ausencia de malware.

## Operación

| Campo | Valor |
|---|---|
| Método | `POST` |
| Ruta | `/api/v1/inspect` |
| Tipo de contenido admitido | `multipart/form-data` con límite y boundary válidos |
| Campo multipart obligatorio | `file` |
| Número de archivos | Exactamente uno, bajo el campo `file` |
| Campos multipart adicionales | No permitidos |
| Autenticación | No requerida en v1 |
| Tamaño máximo del contenido | 5 MiB (5.242.880 bytes) |

No se definen en v1 rutas de historial, descarga, almacenamiento, cargas múltiples, URL remotas ni Azure Blob.

## Solicitud correcta

La solicitud debe contener una única parte de archivo llamada `file`. Su nombre de archivo es obligatorio y debe cumplir las reglas de la sección siguiente. Los archivos vacíos son válidos: tienen tamaño `0` y la huella SHA-256 del flujo vacío.

El límite de 5 MiB corresponde exclusivamente a los bytes del contenido del archivo, no a una afirmación sobre el tamaño total de la codificación multipart. La futura implementación deberá rechazar una carga excedida antes de conservar o procesar más bytes de los permitidos y calcular la huella en bloques acotados.

## Reglas del nombre de archivo y extensión

El nombre de archivo se considera información no confiable. Nunca se utiliza como ruta local, identificador de almacenamiento, cabecera HTTP ni parte de un mensaje de error. La respuesta puede reflejarlo únicamente como dato JSON del contrato y una implementación no debe registrarlo por defecto.

Un nombre es válido si se cumplen todas estas reglas:

1. Existe, contiene entre 1 y 255 puntos de código Unicode y no está formado solo por espacios Unicode.
2. No contiene caracteres de control Unicode.
3. No contiene `/` ni `\\`.
4. No es `.` ni `..`.
5. No contiene el segmento `..` entre separadores; aunque los separadores ya están prohibidos, esta comprobación se conserva como defensa explícita contra traversal.

La respuesta conserva el nombre recibido como `filename`; no lo transforma en ruta ni le atribuye seguridad fuera de las comprobaciones publicadas. La comparación para las comprobaciones se hace sobre la cadena recibida; v1 no realiza normalización Unicode del nombre.

La extensión es informativa y se deriva así:

- Se toma la porción posterior al último `.` del nombre válido y se transforma con minúsculas Unicode.
- La extensión es `null` si no hay punto, si el punto es el primer carácter y no existe otro punto posterior (por ejemplo, `.env`), o si es el último carácter (por ejemplo, `report.`).
- En nombres con varios puntos se usa únicamente el último sufijo: `archive.tar.gz` produce `gz`.
- La extensión no contiene el punto y no se usa para validar el contenido ni permitir o denegar tipos.

Una extensión se marca como ambigua cuando el nombre tiene más de un punto significativo (no inicial) antes del último sufijo; por ejemplo, `archive.tar.gz` y `invoice.pdf.exe` son ambiguos. La ambigüedad es una señal informativa, no un rechazo.

## Tipo de medio declarado y huella

`media_type_declared` refleja el tipo de medio declarado en la parte multipart, si existe, sin validarlo ni intentar detectarlo desde los bytes. Cuando no exista, es `null`. Su presencia no modifica el resultado ni habilita análisis de contenido.

La huella se calcula con **SHA-256** sobre todos los bytes exactos del archivo, en su orden original. Se devuelve como una cadena de 64 caracteres hexadecimales ASCII en minúsculas. Es un identificador determinista de contenido, no un mecanismo de autorización, cifrado, desinfección ni detección de malware.

## Respuesta correcta

Una solicitud válida devuelve `200 OK`:

```json
{
  "filename": "report.PDF",
  "size_bytes": 18,
  "media_type_declared": "application/pdf",
  "extension": "pdf",
  "filename_checks": {
    "is_safe": true,
    "has_path_separator": false,
    "has_traversal_sequence": false,
    "has_control_characters": false,
    "has_ambiguous_extension": false
  },
  "content_fingerprint": {
    "algorithm": "sha256",
    "value": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  }
}
```

| Campo | Tipo | Regla |
|---|---|---|
| `filename` | cadena | Nombre recibido, válido según este contrato; se trata exclusivamente como dato. |
| `size_bytes` | entero no negativo | Número de bytes exactos del contenido. |
| `media_type_declared` | cadena o `null` | Tipo declarado por la parte multipart; no es una detección de contenido. |
| `extension` | cadena o `null` | Último sufijo normalizado según las reglas de extensión. |
| `filename_checks.is_safe` | booleano | Siempre `true` en una respuesta correcta. |
| `filename_checks.has_path_separator` | booleano | Siempre `false` en una respuesta correcta. |
| `filename_checks.has_traversal_sequence` | booleano | Siempre `false` en una respuesta correcta. |
| `filename_checks.has_control_characters` | booleano | Siempre `false` en una respuesta correcta. |
| `filename_checks.has_ambiguous_extension` | booleano | Indicador informativo de múltiples extensiones significativas. |
| `content_fingerprint.algorithm` | cadena | Siempre `sha256` en v1. |
| `content_fingerprint.value` | cadena | SHA-256 hexadecimal en minúsculas de 64 caracteres. |

## Respuestas de error

Todos los errores devuelven JSON con la siguiente envoltura. Los mensajes no deben contener contenido del archivo, rutas del sistema, trazas, nombres de archivo ni detalles internos.

```json
{
  "error": {
    "code": "validation_error",
    "message": "La solicitud no cumple el contrato.",
    "details": [
      {
        "field": "file",
        "rule": "required",
        "message": "Debe enviarse exactamente un archivo en el campo file."
      }
    ]
  }
}
```

`details` es una lista, posiblemente vacía. Cada elemento tiene `field`, `rule` y `message` como cadenas seguras y genéricas.

| Estado | Código | Cuándo se usa |
|---:|---|---|
| 400 | `malformed_multipart` | El cuerpo multipart no puede interpretarse o no incluye un boundary válido. |
| 413 | `file_too_large` | El contenido del archivo excede 5.242.880 bytes. |
| 415 | `unsupported_media_type` | La solicitud no usa `multipart/form-data`. |
| 422 | `validation_error` | Falta `file`, hay más de un archivo, existen campos adicionales, el nombre es inválido o falla otra regla de solicitud definida por este contrato. |
| 405 | `method_not_allowed` | Se usa un método distinto de `POST` en la ruta. |
| 500 | `internal_error` | Fallo inesperado no atribuible al cliente; no expone detalles internos. |

Para validaciones del campo de archivo, `field` es `file`. Para campos multipart adicionales, `field` es su nombre cuando sea seguro representarlo; de otro modo, es `body`. Las reglas públicas previstas incluyen `required`, `exactly_one`, `extra_field`, `filename_required`, `filename_invalid` y `max_size`.

## Ejemplos documentales

### Archivo vacío válido

Una parte `file` con nombre válido y cero bytes devuelve `200 OK`, `size_bytes: 0` y `content_fingerprint.value` igual a:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### Nombre inseguro

Una carga cuyo nombre contiene `../` o `\\` devuelve `422 Unprocessable Entity` con `error.code` igual a `validation_error`, regla `filename_invalid` y sin reflejar el nombre enviado en el mensaje.

### Tamaño excedido

Una carga de 5.242.881 bytes devuelve `413 Payload Too Large` con `error.code` igual a `file_too_large`. No debe calcularse ni devolverse una huella parcial.

## Límites y no objetivos

- El límite de 5 MiB no implementa rate limiting ni controla límites de proxy o servidor ASGI; el despliegue futuro deberá aplicar límites equivalentes fuera de la aplicación.
- El procesamiento se limita a metadatos, comprobaciones de nombre y SHA-256; no hay lectura semántica del documento.
- No se persisten bytes, resultados, nombre, huella ni metadatos entre solicitudes.
- No hay configuración de algoritmos, tipos permitidos, extensiones permitidas ni autenticación en v1.
- Azure Blob no forma parte de este contrato; cualquier extensión futura deberá conservar el flujo local o versionar diferencias públicas.
