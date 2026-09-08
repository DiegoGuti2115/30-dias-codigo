# Roadmap — Día 09: API de portfolio

> **Estado actual:** Fases 0, 1, 2, 3, 4, 5 y 6 completadas. Existen contrato HTTP, fixture local sintético, validación Pydantic, capa de consulta, aplicación FastAPI, verificación automatizada y documentación reproducible para consumo y demo local; no existe despliegue.

Este roadmap desarrolla el alcance definido en [`README.md`](README.md): una API pública y de solo lectura para perfil, proyectos, habilidades y experiencia. Se basa en FastAPI y Pydantic, usa datos locales como fuente inicial y no incluye autenticación en la v1.

## Principios de entrega

- Priorizar un flujo local, demostrable y verificable dentro del límite operativo del reto.
- Mantener el alcance de la v1: consultas públicas; no CRUD ni administración.
- Usar fixtures locales como ruta principal y fallback permanente; no depender de red, credenciales o cloud.
- No versionar secretos ni datos personales innecesarios.
- Congelar el alcance ante retrasos: según [`docs/DAILY_WORKFLOW.md`](../../docs/DAILY_WORKFLOW.md), primero se eliminan extras antes que el flujo de lectura principal.

## Dependencias entre fases

```text
Fase 0 ──► Fase 1 ──► Fase 2 ──► Fase 3 ──► Fase 4 ──► Fase 5 ──► Fase 6
               │                         │                         │
               └────────► Fase 7 ◄──────┴─────────────────────────┘
```

- La Fase 1 define los contratos que condicionan fixtures, esquemas, rutas y pruebas.
- La Fase 2 debe concluir antes de exponer respuestas HTTP reales.
- La Fase 3 habilita las rutas de lectura de la Fase 4.
- La Fase 5 verifica la implementación de las fases anteriores.
- La Fase 6 documenta y demuestra únicamente comportamientos ya verificados.
- La Fase 7 cubre despliegue y mantenimiento posterior; no bloquea la entrega local mínima.

## Fases

### Fase 0 — Preparación y delimitación

**Prioridad:** P0 — imprescindible.
**Estado:** Completada.

| Aspecto | Definición |
|---|---|
| Objetivo | Preparar la documentación y el esqueleto sin escribir código ni contenido de datos. |
| Dependencias | Ninguna. |
| Entregables | [`README.md`](README.md), este roadmap y directorios vacíos para código, pruebas, fixtures, documentación, ejemplos y demo. |
| No permitido | Endpoints, modelos, servicios, middleware, configuración ejecutable, dependencias, migraciones, fixtures o pruebas. |
| Cierre | La estructura coincide con la documentación; los archivos existentes son solo documentación; no se sobrescribe ningún proyecto previo. |

### Fase 1 — Contrato de recursos y API

**Prioridad:** P0 — imprescindible.
**Estado:** Completada.

| Aspecto | Definición |
|---|---|
| Objetivo | Convertir el alcance funcional en un contrato preciso antes de implementar. |
| Dependencias | Fase 0 cerrada. |
| Actividades | Definir campos, tipos, obligatoriedad, formatos de fecha, ejemplos seguros, orden de colecciones, errores y semántica HTTP. Confirmar el prefijo `/api/v1` y las rutas de lectura. |
| Entregables | Documento contractual en [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md) y ejemplos de respuestas en [`examples/RESPUESTAS_PLANIFICADAS.md`](examples/RESPUESTAS_PLANIFICADAS.md), sin afirmar disponibilidad antes de implementar. |
| Cierre | Completado: cada endpoint planificado tiene respuesta, errores y reglas verificables; el contrato no deja ambigüedad sobre datos públicos ni `slug` de proyecto. |

**Contrato mínimo a cerrar:**

- `GET /health`
- `GET /api/v1/profile`
- `GET /api/v1/projects`
- `GET /api/v1/projects/{slug}`
- `GET /api/v1/skills`
- `GET /api/v1/experience`

### Fase 2 — Datos locales y validación de dominio

**Prioridad:** P0 — imprescindible.
**Estado:** Completada.

| Aspecto | Definición |
|---|---|
| Objetivo | Crear datos de demo locales, inocuos y deterministas, junto con sus esquemas de validación. |
| Dependencias | Fase 1 cerrada. |
| Actividades | Incorporar fixtures de perfil, proyectos, habilidades y experiencia; definir esquemas Pydantic; validar unicidad de `slug`, tipos, fechas, enlaces y campos públicos. |
| Entregables | Fixture en [`data/fixtures/portfolio-v1.json`](data/fixtures/portfolio-v1.json), modelos y cargador en [`src/models.py`](src/models.py) y [`src/fixtures.py`](src/fixtures.py), pruebas en [`tests/test_fixtures.py`](tests/test_fixtures.py) y guía en [`docs/FIXTURES_FASE_2.md`](docs/FIXTURES_FASE_2.md). |
| Cierre | Completado: el fixture se carga sin red ni secretos, satisface el contrato y los datos inválidos son rechazados por pruebas deterministas. |

### Fase 3 — Capa de consulta y composición

**Prioridad:** P0 — imprescindible.
**Estado:** Completada.

| Aspecto | Definición |
|---|---|
| Objetivo | Separar el acceso local a datos de las reglas de consulta. |
| Dependencias | Fase 2 cerrada. |
| Actividades | Implementar un repositorio local de fixtures y servicios de lectura; establecer orden determinista; resolver detalle por `slug`; distinguir ausencia de recurso de fallo interno. |
| Entregables | Completados: [`src/repository.py`](src/repository.py), [`src/services.py`](src/services.py), [`src/errors.py`](src/errors.py) y pruebas unitarias en [`tests/test_queries.py`](tests/test_queries.py). |
| Cierre | Completado: las consultas devuelven entidades válidas, ordenadas y sin modificar la fuente; un `slug` desconocido o no público produce [`ProjectNotFoundError`](src/errors.py), mientras que un fallo de carga se traduce a [`FixtureSourceError`](src/errors.py). No se creó transporte HTTP. |

### Fase 4 — Aplicación FastAPI y endpoints públicos

**Prioridad:** P0 — imprescindible.
**Estado:** Completada.

| Aspecto | Definición |
|---|---|
| Objetivo | Exponer el flujo de consulta mediante HTTP y JSON. |
| Dependencias | Fase 3 cerrada. |
| Actividades | Completadas: creación de aplicación FastAPI, registro de rutas, modelos de respuesta, códigos HTTP y conexión con servicios. Incluye comprobación mínima de salud. |
| Entregables | Completados: [`src/main.py`](src/main.py), [`src/schemas.py`](src/schemas.py), dependencias en [`requirements.txt`](requirements.txt), pruebas de integración en [`tests/test_http_api.py`](tests/test_http_api.py) y guía en [`docs/HTTP_FASE_4.md`](docs/HTTP_FASE_4.md). |
| Cierre | Completado: todos los endpoints de Fase 1 responden localmente; las respuestas cumplen esquemas públicos explícitos; no hay rutas de escritura ni autenticación. |

### Fase 5 — Robustez, errores, seguridad y pruebas

**Prioridad:** P0 — imprescindible para cierre técnico.
**Estado:** Completada.

| Aspecto | Definición |
|---|---|
| Objetivo | Verificar contratos, entradas inválidas y ausencia de exposición accidental. |
| Dependencias | Fases 2 a 4 terminadas. |
| Actividades | Completadas: se verifican respuestas consistentes `404`, `422` y `500` sin trazas; orden y serialización pública; límites y formas inválidas de `slug`; ausencia de campos internos, registros privados y valores `null`; y el contrato de solo lectura en HTTP y OpenAPI. Se revisó el fixture sintético local. |
| Entregables | Cobertura ampliada en [`tests/test_http_api.py`](tests/test_http_api.py) y guía reproducible en [`docs/VERIFICACION_FASE_5.md`](docs/VERIFICACION_FASE_5.md). |
| Cierre | Completado: 22 pruebas pasan localmente; se validaron compilación, fixture y OpenAPI. No hay secretos, escrituras ni dependencias externas. |

### Fase 6 — Documentación, demo y cierre de entrega

**Prioridad:** P0 — imprescindible para la publicación del reto.
**Estado:** Completada.

| Aspecto | Definición |
|---|---|
| Objetivo | Hacer consumible y demostrable la API implementada. |
| Dependencias | Fases 4 y 5 cerradas. |
| Actividades | Completadas: se actualizaron instalación, ejecución, uso, pruebas, OpenAPI, errores y fallback local en [`README.md`](README.md); se añadieron ejemplos HTTP reproducibles y un guion de demo local de 15 segundos. |
| Entregables | [`README.md`](README.md), guía de uso en [`examples/USO_HTTP_LOCAL.md`](examples/USO_HTTP_LOCAL.md), guion en [`assets/DEMO_15S.md`](assets/DEMO_15S.md), guía en [`docs/VERIFICACION_FASE_6.md`](docs/VERIFICACION_FASE_6.md) y prueba de entrega en [`tests/test_delivery.py`](tests/test_delivery.py). |
| Cierre | Completado: una copia limpia puede ejecutar, consultar, probar y demostrar el flujo local. Pasan 25 pruebas; compilación, fixture, OpenAPI de solo lectura y revisión de diff están verificados. No se añadió despliegue ni se amplió el contrato v1. |

### Fase 7 — Despliegue y mantenimiento futuro

**Prioridad:** P2 — posterior a la entrega local.

| Aspecto | Definición |
|---|---|
| Objetivo | Evaluar una publicación segura y sostenibilidad del proyecto sin ampliar indebidamente la v1. |
| Dependencias | Fase 6 cerrada. |
| Actividades | Elegir plataforma de despliegue, configurar variables sin secretos versionados, validar endpoint público y CORS solo si hay consumidor conocido. Planificar versionado, observabilidad mínima, actualización de datos y compatibilidad. |
| Entregables | Guía de despliegue, configuración de entorno documentada, lista de comprobación de seguridad y registro de decisiones. |
| Cierre | El despliegue reproduce el comportamiento local, no expone secretos y cuenta con verificación de salud y plan de reversión. |

## Backlog diferido explícitamente

Estos elementos requieren una decisión posterior y no se deben incorporar a la v1 sin actualizar el alcance:

1. CRUD administrativo y autenticación/autorización asociada.
2. Base de datos, ORM, migraciones o panel de edición.
3. Filtros, búsqueda, paginación y caché avanzados.
4. Gestión de imágenes o archivos en almacenamiento cloud.
5. Métricas, telemetría y límites de tasa.
6. Cliente web del portfolio.
7. Versionado adicional de la API o compatibilidad con clientes externos.

## Criterios generales de finalización del proyecto

El proyecto podrá considerarse entregable cuando se cumplan todos los puntos:

- [x] La API pública de solo lectura expone perfil, proyectos, detalle de proyecto, habilidades y experiencia.
- [x] Los datos locales funcionan sin red, credenciales ni proveedor externo.
- [x] Todos los contratos de respuesta y error están documentados y probados.
- [x] No hay rutas de escritura, autenticación ni autorización en la v1.
- [x] Las pruebas automatizadas y el flujo manual reproducible pasan en local.
- [x] La documentación OpenAPI está disponible al ejecutar la aplicación.
- [x] El README incluye instalación, uso, pruebas, seguridad, limitaciones y fallback real.
- [x] No existen secretos ni datos sensibles en el repositorio.
- [x] Existe una demo local breve y evidencia de verificación final.
