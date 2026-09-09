# Contrato HTTP v1 — API CRUD de tareas

## Estado y propósito

Este documento define el contrato público implementado de la primera versión de la API CRUD de tareas. La aplicación FastAPI, los modelos Pydantic, el repositorio local, el servicio CRUD y la suite automatizada materializan las reglas descritas aquí.

La API administra una única colección local de tareas. No tiene usuarios, autenticación, integraciones externas ni persistencia durable en esta versión. Para instalarla, ejecutarla y comprobarla, consulte la [`GUIA_DE_ENTREGA.md`](GUIA_DE_ENTREGA.md).

## Convenciones generales

- La interfaz será HTTP sobre JSON.
- Las rutas se versionarán bajo el prefijo `/api/v1`.
- Los nombres de propiedades JSON usarán `snake_case`.
- Todas las fechas usarán el formato ISO 8601 en UTC, con indicador de zona horaria.
- Los identificadores de tarea serán enteros positivos asignados por el servidor y no reutilizados durante la vida de una instancia de la aplicación.
- El contenido de las respuestas será JSON salvo en la eliminación exitosa, que no tendrá cuerpo.
- La API no expondrá detalles internos, trazas ni datos de infraestructura en las respuestas de error.

## Recurso tarea

Una tarea representa una unidad de trabajo administrable dentro de la colección local.

| Campo | Tipo JSON | Creación | Reemplazo total | Actualización parcial | Respuesta | Descripción |
|---|---|:---:|:---:|:---:|:---:|---|
| `id` | entero positivo | No | No | No | Sí | Identificador único de solo lectura. |
| `title` | cadena | Sí | Sí | Opcional | Sí | Título visible y obligatorio de la tarea. |
| `description` | cadena o nulo | No | Sí | Opcional | Sí | Descripción opcional; se puede establecer como nula. |
| `completed` | booleano | No | Sí | Opcional | Sí | Estado de finalización; su valor inicial es pendiente. |
| `created_at` | fecha-hora ISO 8601 UTC | No | No | No | Sí | Instante de creación, de solo lectura. |
| `updated_at` | fecha-hora ISO 8601 UTC | No | No | No | Sí | Instante de última modificación, de solo lectura. |

### Reglas de datos

- `title` debe ser una cadena de texto no vacía tras retirar espacios externos.
- `title` tendrá entre 1 y 120 caracteres tras esa normalización.
- `description`, cuando se proporcione como texto, tendrá como máximo 1.000 caracteres. La cadena vacía es válida y distinta de `null`.
- `completed` solo admitirá valores booleanos JSON.
- Los campos de solo lectura enviados por un cliente se rechazarán como entrada inválida; el servidor no los aceptará ni los sobrescribirá.
- En la creación, la ausencia de `description` equivale a `null` y la ausencia de `completed` equivale a `false`.
- Cada actualización que altere una tarea actualizará `updated_at`. Una operación que no cambie valores continuará siendo válida y dejará una representación consistente; la política concreta sobre actualizar su marca temporal se fijará durante la implementación y se documentará si difiere de esta regla.

## Recursos y operaciones

| Operación | Método | Ruta | Solicitud | Respuesta exitosa |
|---|---|---|---|---|
| Crear una tarea | POST | `/api/v1/tasks` | Campos de creación | 201 con la tarea creada |
| Listar tareas | GET | `/api/v1/tasks` | Sin cuerpo | 200 con una colección de tareas |
| Consultar una tarea | GET | `/api/v1/tasks/{task_id}` | Sin cuerpo | 200 con la tarea solicitada |
| Reemplazar una tarea | PUT | `/api/v1/tasks/{task_id}` | Representación completa editable | 200 con la tarea actualizada |
| Actualizar parcialmente una tarea | PATCH | `/api/v1/tasks/{task_id}` | Uno o más campos editables | 200 con la tarea actualizada |
| Eliminar una tarea | DELETE | `/api/v1/tasks/{task_id}` | Sin cuerpo | 204 sin cuerpo |

No se definirá una operación independiente para completar una tarea: el cambio de `completed` se realizará mediante la actualización total o parcial. No se expondrán rutas adicionales para etiquetas, prioridades, fechas límite, usuarios ni autenticación.

## Ejemplos documentales

Los siguientes ejemplos describen solicitudes y respuestas representativas. Las marcas temporales e identificadores son ilustrativos; el servidor los asigna en cada instancia.

### Crear una tarea

`POST /api/v1/tasks`

```json
{
  "title": "Preparar demostración",
  "description": "Ejecutar el flujo CRUD",
  "completed": false
}
```

Respuesta `201`:

```json
{
  "id": 1,
  "title": "Preparar demostración",
  "description": "Ejecutar el flujo CRUD",
  "completed": false,
  "created_at": "2026-01-01T10:00:00+00:00",
  "updated_at": "2026-01-01T10:00:00+00:00"
}
```

### Actualizar parcialmente una tarea

`PATCH /api/v1/tasks/1`

```json
{
  "completed": true
}
```

Respuesta `200`:

```json
{
  "id": 1,
  "title": "Preparar demostración",
  "description": "Ejecutar el flujo CRUD",
  "completed": true,
  "created_at": "2026-01-01T10:00:00+00:00",
  "updated_at": "2026-01-01T10:05:00+00:00"
}
```

### Error por tarea inexistente

`GET /api/v1/tasks/999`

Respuesta `404`:

```json
{
  "error": {
    "code": "task_not_found",
    "message": "Task 999 was not found."
  }
}
```

## Formatos de respuesta exitosa

### Tarea individual

Las respuestas exitosas de creación, consulta y actualización devolverán un objeto JSON con todos los campos de respuesta del recurso tarea: `id`, `title`, `description`, `completed`, `created_at` y `updated_at`.

### Colección de tareas

El listado devolverá un objeto JSON con una propiedad `items`, cuyo valor será una lista de tareas completas. Aunque no haya tareas, `items` será una lista vacía.

En esta versión no habrá parámetros de filtrado, ordenación ni paginación. El listado mantendrá el orden ascendente de creación por identificador para ofrecer resultados deterministas. Esta decisión reduce el alcance atómico y evita semánticas de consulta que no aportan valor al CRUD básico.

### Eliminación

Una eliminación exitosa devolverá el estado 204 y no incluirá cuerpo ni contenido JSON.

## Semántica de operaciones

### Creación

La creación exige `title`. `description` y `completed` son opcionales y recibirán sus valores por defecto cuando no se incluyan. El servidor asignará `id`, `created_at` y `updated_at`; estos últimos coincidirán al crear el recurso.

### Consulta individual y listado

La consulta individual devuelve la representación actual de la tarea identificada. El listado devuelve todas las tareas existentes. Ninguna consulta modifica el estado de la colección.

### Reemplazo total

El reemplazo total exige los campos editables `title`, `description` y `completed`. Debe proporcionar una representación completa del estado editable de la tarea. No se permite enviar `id`, `created_at` ni `updated_at`.

### Actualización parcial

La actualización parcial exige al menos uno de los campos editables `title`, `description` o `completed`. Los campos no enviados conservarán su valor actual. Enviar `description` con `null` elimina su contenido opcional; enviar una cadena vacía conserva explícitamente una descripción vacía.

### Eliminación

La eliminación retira la tarea de la colección. Una solicitud posterior sobre el mismo identificador debe recibir el error de recurso inexistente. El identificador no se reasignará a una nueva tarea durante la misma instancia de la aplicación.

## Errores

### Formato común de error de aplicación

Los errores de recurso inexistente y los errores generales controlados usarán un objeto JSON con esta semántica:

| Propiedad | Tipo | Descripción |
|---|---|---|
| `error` | objeto | Información normalizada del error. |
| `error.code` | cadena | Código estable y legible por máquina. |
| `error.message` | cadena | Explicación legible para consumidores. |
| `error.details` | objeto o lista, opcional | Información adicional segura, si aplica. |

Los errores de validación conservarán el formato estándar de FastAPI/Pydantic previsto por el framework: un objeto JSON con una propiedad `detail` que contiene una lista de problemas de validación. La implementación deberá asegurar que este formato no incluya información interna.

### Estados de error

| Estado | Código de error | Cuándo se devuelve |
|---:|---|---|
| 400 | `invalid_request` | Solicitud sintácticamente procesable pero semánticamente inválida fuera de las validaciones de campo estándar, como un `PATCH` sin campos editables. |
| 404 | `task_not_found` | No existe una tarea para el identificador solicitado. |
| 405 | `method_not_allowed` | Se usa un método no admitido en una ruta publicada. |
| 422 | Formato estándar de validación | Ruta, cuerpo o datos de entrada no cumplen el contrato de tipo, formato o restricciones. |
| 500 | `internal_error` | Error inesperado; la respuesta no expondrá detalles técnicos. |

Las operaciones exitosas usarán exclusivamente los estados 200, 201 o 204 definidos en la tabla de recursos. No se definirá un estado de error específico para concurrencia, autorización o persistencia, pues no forman parte de esta versión.

## Criterios de aceptación de la Fase 1

La Fase 1 se considerará documentada de forma suficiente cuando este contrato permita responder sin ambigüedad a las siguientes cuestiones:

- Qué campos forman una tarea, cuáles son obligatorios, opcionales y de solo lectura.
- Qué restricciones se aplican a los campos editables.
- Qué operaciones CRUD existen, con qué método y ruta se invocan.
- Qué respuesta y estado devuelve cada operación exitosa.
- Qué significan el reemplazo total, la actualización parcial, el cambio de completitud y la eliminación.
- Qué respuesta se espera para entradas inválidas, tareas inexistentes, métodos no permitidos e incidentes inesperados.
- Que el listado no tiene filtrado, ordenación configurable ni paginación, y el motivo de esa decisión.

## Límites de implementación

La implementación usa almacenamiento local en memoria: su contenido se pierde al detener el proceso y no se comparte entre instancias. No incorpora concurrencia, persistencia durable, autenticación, usuarios, filtros, ordenación configurable ni paginación. Las posibles extensiones se mantienen en [`../ROADMAP.md`](../ROADMAP.md).