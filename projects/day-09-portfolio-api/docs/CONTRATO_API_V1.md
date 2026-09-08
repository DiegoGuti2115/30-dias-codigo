# Contrato HTTP — API de portfolio v1

> **Estado:** contrato de diseño cerrado en la Fase 1 e implementado localmente en la Fase 4. Las Fases 2 y 3 aportan fixtures, validación y consultas de dominio; [`src/main.py`](../src/main.py) expone los endpoints HTTP y [`src/schemas.py`](../src/schemas.py) define sus respuestas públicas.

Este documento es la fuente contractual para las fases posteriores de la API de portfolio. Complementa el alcance de [`README.md`](../README.md) y cierra los requisitos de la Fase 1 de [`ROADMAP.md`](../ROADMAP.md): recursos, tipos, obligatoriedad, formatos, datos públicos, orden, errores y semántica HTTP.

## 1. Convenciones generales

| Regla | Contrato |
|---|---|
| Protocolo | HTTP sobre una aplicación local FastAPI; el host y puerto se eligen al ejecutar Uvicorn. |
| Formato de éxito y error | JSON UTF-8 con `Content-Type: application/json`. |
| Versionado | Las rutas de dominio usan el prefijo fijo `/api/v1`. La comprobación operativa `/health` queda fuera del prefijo. |
| Métodos permitidos | Únicamente `GET` en las rutas de este contrato. No se define cuerpo de petición. |
| Estado | Las consultas son idempotentes, no modifican datos y no tienen efectos laterales. |
| Autenticación | No requerida ni admitida en v1; todos los recursos definidos son públicos. |
| Persistencia | La fuente local y determinista está definida en [`FIXTURES_FASE_2.md`](FIXTURES_FASE_2.md); la capa de consulta local de Fase 3 está implementada y no depende de HTTP. |
| Paginación y filtros | No existen en v1. Las colecciones devuelven el conjunto público completo dentro de los límites que defina la Fase 2. |
| Fechas | Cadenas ISO 8601 de precisión mensual, exactamente `YYYY-MM`, con mes entre `01` y `12`. |
| Enlaces | URL absoluta con esquema `https` o `http`; se prefiere `https`. |
| Campos opcionales | Se omiten de la respuesta cuando no hay valor público; no se serializan como `null`. |
| Campos no definidos | No deben aparecer en respuestas públicas. |

La API no usa ni expondrá secretos, direcciones, teléfonos, identificadores de cuentas, correos personales, notas privadas, borradores, información de administración ni metadatos internos.

## 2. Convenciones de tipos y restricciones

| Nombre | Tipo JSON | Restricción contractual |
|---|---|---|
| `non_empty_string` | string | Texto Unicode no vacío después de recortar extremos; máximo 500 caracteres, salvo que se indique otro límite. |
| `short_text` | string | `non_empty_string` de máximo 160 caracteres. |
| `summary` | string | `non_empty_string` de máximo 500 caracteres. |
| `description` | string | `non_empty_string` de máximo 2.000 caracteres. |
| `slug` | string | 1 a 80 caracteres; minúsculas ASCII, números y guiones simples; expresión `^[a-z0-9]+(?:-[a-z0-9]+)*$`. |
| `url` | string | URL absoluta válida con esquema `https` o `http`; máximo 2.048 caracteres. |
| `month` | string | Fecha mensual ISO 8601: `YYYY-MM`; año de cuatro dígitos y mes de `01` a `12`. |
| `string_list` | array | Lista de valores `non_empty_string` únicos, en el orden declarado, con un máximo de 20 elementos. |
| `boolean` | boolean | Valor JSON `true` o `false`. |

Los textos no se interpretan como HTML. Los consumidores deben tratarlos como texto plano. Los fixtures se validan antes de la publicación y las respuestas HTTP se proyectan mediante modelos públicos explícitos.

## 3. Recursos públicos

### 3.1 Perfil

El recurso representa una única identidad profesional pública. La v1 no admite múltiples perfiles.

| Campo | Tipo | Obligatorio | Reglas |
|---|---|:---:|---|
| `name` | `non_empty_string` | Sí | Nombre de presentación; máximo 120 caracteres. |
| `headline` | `short_text` | Sí | Titular profesional breve. |
| `summary` | `summary` | Sí | Resumen profesional público. |
| `location` | `short_text` | No | Ubicación general no sensible; no incluye dirección postal. |
| `links` | array de objetos `ProfileLink` | No | Máximo 5; se omite si no hay enlaces. |

Cada objeto `ProfileLink` usa este contrato:

| Campo | Tipo | Obligatorio | Reglas |
|---|---|:---:|---|
| `label` | `short_text` | Sí | Etiqueta pública del enlace. |
| `url` | `url` | Sí | Destino HTTP(S) público. |

### 3.2 Proyecto

El recurso representa trabajo público de portfolio. Una respuesta de lista ofrece una vista resumida; el detalle añade `description`.

| Campo | Tipo | Lista | Detalle | Reglas |
|---|---|:---:|:---:|---|
| `slug` | `slug` | Sí | Sí | Identificador único y estable del proyecto. |
| `title` | `short_text` | Sí | Sí | Título público del proyecto. |
| `summary` | `summary` | Sí | Sí | Resumen corto del valor o propósito. |
| `description` | `description` | No | Sí | Descripción ampliada en texto plano. |
| `technologies` | `string_list` | Sí | Sí | Tecnologías visibles; máximo 20. |
| `status` | enum | Sí | Sí | Uno de `active`, `completed` o `archived`. |
| `featured` | `boolean` | Sí | Sí | Indica prioridad de presentación; no es autorización ni visibilidad. |
| `published_at` | `month` | No | No | Mes público de publicación o finalización; se omite si no existe. |
| `links` | array de objetos `ProjectLink` | No | No | Máximo 3; se omite si no hay enlaces. |

Cada objeto `ProjectLink` usa este contrato:

| Campo | Tipo | Obligatorio | Reglas |
|---|---|:---:|---|
| `label` | `short_text` | Sí | Etiqueta de destino, por ejemplo, `Repository` o `Demo`. |
| `url` | `url` | Sí | Destino HTTP(S) público. |

`published_at` no se incluye en el detalle porque el detalle es una extensión de la representación de lista: si existe en la fuente pública, se incluye en ambas representaciones. El campo aparece como opcional en la tabla de detalle para indicar que puede estar ausente, no para excluirlo de dicha respuesta.

### 3.3 Habilidad

Una habilidad es una competencia declarada públicamente. La v1 no modela porcentajes, años de experiencia ni evaluaciones subjetivas.

| Campo | Tipo | Obligatorio | Reglas |
|---|---|:---:|---|
| `name` | `short_text` | Sí | Nombre de la habilidad. |
| `category` | enum | Sí | Uno de `backend`, `frontend`, `data`, `cloud`, `tools` o `other`. |
| `context` | `summary` | No | Contexto breve y verificable; se omite si no aplica. |

La combinación `category` + `name`, comparada sin distinción de mayúsculas/minúsculas y tras recortar espacios, debe ser única en el conjunto público.

### 3.4 Experiencia

El recurso representa una experiencia profesional o educativa relevante. No incluye historial completo ni datos de contacto de organizaciones o personas.

| Campo | Tipo | Obligatorio | Reglas |
|---|---|:---:|---|
| `organization` | `short_text` | Sí | Organización, institución o contexto público. |
| `role` | `short_text` | Sí | Puesto, programa o rol. |
| `summary` | `summary` | Sí | Resumen público de responsabilidades o aprendizaje. |
| `started_at` | `month` | Sí | Mes de inicio. |
| `ended_at` | `month` | No | Mes de finalización; se omite para una experiencia vigente. |
| `technologies` | `string_list` | No | Tecnologías públicas asociadas; se omite si no aplica. |

Cuando `ended_at` esté presente, su valor debe ser igual o posterior a `started_at` en orden cronológico mensual.

## 4. Visibilidad, integridad y orden de colecciones

### 4.1 Datos públicos

La fuente local contiene metadatos de control, pero la capa de respuesta solo publica entidades explícitamente marcadas como públicas. Los campos de control no aparecen nunca en JSON. La Fase 2 expresa esta marca como el booleano fuente `public`, descrito en [`FIXTURES_FASE_2.md`](FIXTURES_FASE_2.md).

Un proyecto con estado `archived` puede ser público. Un borrador, una entidad privada o una entidad no marcada explícitamente como pública no puede aparecer en ninguna colección ni ser recuperable por su `slug`.

### 4.2 Unicidad e identificación

- Cada `slug` de proyecto público es único en comparación exacta y se ajusta a la gramática definida.
- El segmento `{slug}` se compara de forma exacta; no se normaliza a minúsculas ni se acepta una variante distinta.
- Los títulos y nombres no son identificadores y no se usan para recuperar recursos.

### 4.3 Orden determinista

Las colecciones no aceptan parámetros de ordenación. La implementación publica exactamente este orden:

| Colección | Regla primaria | Regla secundaria | Desempate final |
|---|---|---|---|
| Proyectos | `featured=true` antes de `featured=false` | `published_at` descendente; ausente después de fecha presente | `slug` ascendente |
| Habilidades | `category` ascendente según orden literal ASCII de sus valores contractuales | `name` ascendente, comparación Unicode simple | `name` original ascendente |
| Experiencia | `started_at` descendente | `ended_at` descendente; experiencia vigente sin `ended_at` antes de una finalizada con mismo inicio | `organization` ascendente, después `role` ascendente |

El orden se calcula sobre los valores públicos normalizados por validación. La respuesta no revela el orden físico de la fuente.

## 5. Endpoints

### 5.1 `GET /health`

| Aspecto | Contrato |
|---|---|
| Propósito | Confirmar que la aplicación puede atender solicitudes HTTP. |
| Autenticación | Ninguna. |
| Parámetros | Ninguno. |
| Éxito | `200 OK` y un objeto `HealthResponse`. |
| Errores propios | Ninguno previsto; un fallo inesperado usa el contrato 500 global. |

`HealthResponse`:

| Campo | Tipo | Obligatorio | Valor contractual |
|---|---|:---:|---|
| `status` | string | Sí | Literal `ok`. |

Este endpoint no certifica que los fixtures de dominio sean válidos ni que todos los recursos estén disponibles; esa comprobación queda fuera del contrato de salud mínimo.

### 5.2 `GET /api/v1/profile`

| Aspecto | Contrato |
|---|---|
| Propósito | Obtener el único perfil público. |
| Autenticación | Ninguna. |
| Parámetros | Ninguno. |
| Éxito | `200 OK` y una representación `Profile`. |
| Error de ausencia | `500 Internal Server Error` si la fuente no permite construir el perfil único; no se usa `404` porque el perfil es requisito de la aplicación. |

### 5.3 `GET /api/v1/projects`

| Aspecto | Contrato |
|---|---|
| Propósito | Listar todos los proyectos públicos en su vista resumida. |
| Autenticación | Ninguna. |
| Parámetros | Ninguno; filtros y paginación quedan fuera de v1. |
| Éxito | `200 OK` y un objeto `ProjectListResponse`. Una colección vacía válida devuelve `items: []`. |
| Error de fuente | `500 Internal Server Error` conforme al error global. |

`ProjectListResponse` contiene únicamente `items`, una matriz de `ProjectSummary` ordenada según la sección 4.3.

### 5.4 `GET /api/v1/projects/{slug}`

| Aspecto | Contrato |
|---|---|
| Propósito | Obtener el detalle público de un proyecto identificado por `slug`. |
| Autenticación | Ninguna. |
| Parámetro de ruta | `slug`, obligatorio; debe cumplir `^[a-z0-9]+(?:-[a-z0-9]+)*$` y tener entre 1 y 80 caracteres. |
| Éxito | `200 OK` y una representación `ProjectDetail`. |
| `slug` con formato inválido | `422 Unprocessable Content` con el error de validación. |
| `slug` válido pero no encontrado o no público | `404 Not Found` y `ErrorResponse` con código `project_not_found`. |
| Error de fuente | `500 Internal Server Error` conforme al error global. |

Un proyecto privado, borrador o ausente produce la misma respuesta 404 para no revelar su existencia.

### 5.5 `GET /api/v1/skills`

| Aspecto | Contrato |
|---|---|
| Propósito | Listar las habilidades públicas. |
| Autenticación | Ninguna. |
| Parámetros | Ninguno. |
| Éxito | `200 OK` y un objeto `SkillListResponse`; una colección vacía válida devuelve `items: []`. |
| Error de fuente | `500 Internal Server Error` conforme al error global. |

`SkillListResponse` contiene únicamente `items`, una matriz de `Skill` en el orden de la sección 4.3.

### 5.6 `GET /api/v1/experience`

| Aspecto | Contrato |
|---|---|
| Propósito | Listar experiencias públicas relevantes. |
| Autenticación | Ninguna. |
| Parámetros | Ninguno. |
| Éxito | `200 OK` y un objeto `ExperienceListResponse`; una colección vacía válida devuelve `items: []`. |
| Error de fuente | `500 Internal Server Error` conforme al error global. |

`ExperienceListResponse` contiene únicamente `items`, una matriz de `Experience` en el orden de la sección 4.3.

## 6. Formato de errores

### 6.1 Error de dominio controlado

Los errores controlados de dominio, actualmente el 404 de proyecto, usan `ErrorResponse`:

| Campo | Tipo | Obligatorio | Reglas |
|---|---|:---:|---|
| `error.code` | string | Sí | Código estable en `snake_case`. |
| `error.message` | string | Sí | Mensaje seguro para consumidores; no incluye trazas, rutas locales ni valores privados. |

Ejemplo semántico: un `slug` válido que no identifica un proyecto público devuelve `404` con `error.code` igual a `project_not_found`.

### 6.2 Error de validación de solicitud

Un `slug` mal formado devuelve `422 Unprocessable Content`. La aplicación conserva el formato estructurado estándar de validación de FastAPI/Pydantic, con una clave raíz `detail` que es una lista. Cada elemento incluye, como mínimo, `loc`, `msg` y `type`. El texto humano de `msg` no se considera estable; los consumidores deben usar el estado, `loc` y `type`.

### 6.3 Error interno

Los fallos inesperados o una fuente de datos que no cumple el contrato devuelven `500 Internal Server Error`:

```json
{
  "error": {
    "code": "internal_error",
    "message": "An unexpected error occurred."
  }
}
```

La respuesta 500 no incluye detalles de excepción, nombres de archivos, directorios, variables de entorno ni la carga de datos. El registro local seguro y su formato se decidirán en Fase 5. La implementación actual traduce los errores controlados de fuente a esta respuesta.

## 7. Semántica HTTP adicional

| Situación | Estado | Cuerpo |
|---|---:|---|
| Método permitido y recurso disponible | 200 | JSON de éxito correspondiente. |
| Método no definido para una ruta existente | 405 | Formato del framework; no se define personalización en v1. |
| Ruta inexistente | 404 | Formato del framework; solo el 404 de proyecto usa `ErrorResponse` garantizado. |
| Parámetro de ruta inválido | 422 | Error estándar de validación. |
| Proyecto válido no encontrado o no público | 404 | `ErrorResponse` con `project_not_found`. |
| Fuente inválida o fallo no controlado | 500 | `ErrorResponse` con `internal_error`. |

No se definen redirecciones, negociación de contenido alternativa, ETags, caché HTTP ni CORS en la Fase 1.

## 8. Lista de verificación para Fase 2 y posteriores

La implementación deberá poder demostrar que:

- Los fixtures representan exclusivamente datos sintéticos o públicos aptos para demo.
- Todos los recursos satisfacen las restricciones de las secciones 2 y 3.
- El perfil único está disponible y los `slug` públicos son únicos.
- Las colecciones respetan exactamente el orden de la sección 4.3.
- El detalle de proyecto no expone metadatos de visibilidad ni otros campos internos.
- Las rutas de la sección 5 coinciden con modelos, códigos HTTP y errores descritos.
- No se añaden métodos de escritura, autenticación ni autorización sin una revisión explícita del contrato.
