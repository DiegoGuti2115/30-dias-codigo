# Roadmap — API CRUD de tareas

Este roadmap ordena el desarrollo de la API. Las Fases 0 a 7 están completadas; solo las mejoras posteriores permanecen pendientes.

## Fase 0 — Preparación inicial

**Objetivo:** dejar un espacio de trabajo coherente con el stack FastAPI y Pydantic, sin código fuente funcional.

- Crear los directorios de código, pruebas, datos, activos y documentación.
- Reservar los módulos Python para aplicación, esquemas, servicio, repositorio y errores.
- Documentar el propósito, alcance, arquitectura y restricciones iniciales.
- Mantener todos los archivos Python vacíos.

**Resultado esperado:** estructura documental preparada para iniciar el diseño técnico.

## Fase 1 — Definición del contrato de la API — Completada

**Objetivo:** acordar el comportamiento público antes de implementar endpoints.

- Definir el recurso tarea y sus campos obligatorios, opcionales y de solo lectura.
- Establecer las operaciones CRUD, rutas, métodos HTTP y códigos de estado esperados.
- Describir formatos de respuesta para éxito, validación, recurso inexistente y errores generales.
- Decidir las reglas de creación, consulta, actualización total, actualización parcial, completitud y eliminación.
- Documentar criterios de ordenación, filtrado o paginación solo si aportan valor al alcance atómico.

**Resultado esperado:** contrato HTTP revisable y sin ambigüedades.

**Estado:** completada. El contrato público está disponible en `docs/CONTRATO_API_V1.md`.

## Fase 2 — Configuración de entorno y dependencias — Completada

**Objetivo:** preparar una ejecución local reproducible del backend.

- Declarar las dependencias de FastAPI, Pydantic, servidor ASGI y herramientas de prueba.
- Definir la versión mínima compatible de Python.
- Documentar instalación, ejecución local y verificación básica.
- Establecer convenciones de formato, calidad y ejecución de pruebas.
- Confirmar que no se necesitan secretos ni integraciones externas para la primera versión.

**Resultado esperado:** entorno local documentado y listo para desarrollar.

**Estado:** completada. Las dependencias se declaran en `requirements.txt`, la compatibilidad con Python 3.11+ en `pyproject.toml` y la guía de entorno y calidad en `README.md`.

## Fase 3 — Modelado y validación de tareas — Completada

**Objetivo:** materializar los contratos de datos acordados.

- Implementar esquemas separados para creación, lectura y actualización de tareas.
- Aplicar restricciones de formato, obligatoriedad y longitud.
- Definir la representación de identificadores, estado y metadatos.
- Verificar que las entradas inválidas generen errores comprensibles y consistentes.

**Resultado esperado:** modelos Pydantic que protegen el contrato de la API.

**Estado:** completada. Se implementaron los esquemas Pydantic de creación, reemplazo, actualización, lectura y listado, junto con pruebas deterministas de validación de contrato.

## Fase 4 — Persistencia local y reglas de negocio — Completada

**Objetivo:** disponer de un núcleo CRUD independiente de HTTP.

- Implementar un repositorio local en memoria con identificadores únicos.
- Implementar el servicio de tareas con creación, lectura, listado, actualización y eliminación.
- Determinar el comportamiento ante recursos inexistentes y actualizaciones incompletas.
- Mantener el estado local determinista y aislado para pruebas.

**Resultado esperado:** operaciones de dominio verificables sin depender de rutas HTTP.

**Estado:** completada. Se implementaron el repositorio local en memoria, el servicio CRUD y el error de recurso inexistente; las pruebas cubren identificadores únicos, orden determinista, aislamiento por instancia, actualización total y parcial, eliminación y recursos ausentes. Verificaciones ejecutadas: `python -m pytest -q` (28 passed) y `git diff --check`.

## Fase 5 — Capa HTTP con FastAPI — Completada

**Objetivo:** exponer el servicio mediante el contrato REST definido.

- Crear la aplicación FastAPI y configurar metadatos de documentación.
- Implementar los endpoints CRUD de tareas.
- Conectar validación, servicio y repositorio mediante responsabilidades explícitas.
- Traducir errores de dominio a respuestas HTTP uniformes.
- Incluir una comprobación básica de disponibilidad si el contrato la contempla.

**Resultado esperado:** API local funcional con documentación interactiva generada por el framework.

**Estado:** completada. Se creó la aplicación FastAPI con metadatos OpenAPI, los endpoints CRUD bajo `/api/v1/tasks`, la traducción uniforme de errores de dominio y de solicitudes semánticamente inválidas, y el manejo de método no permitido. Las pruebas HTTP verifican documentación, operaciones CRUD, validación, recursos inexistentes y errores de método.

## Fase 6 — Pruebas automatizadas — Completada

**Objetivo:** demostrar la corrección del contrato y prevenir regresiones.

- Probar creación, listado, consulta individual, actualización y eliminación.
- Probar validación de entradas y códigos de estado.
- Probar recursos inexistentes, identificadores inválidos y casos límite de actualización.
- Verificar el aislamiento del estado entre pruebas.
- Añadir pruebas de regresión para los comportamientos acordados.

**Resultado esperado:** suite automatizada que cubra flujos correctos y fallos relevantes.

**Estado:** completada. Se amplió la suite determinista para cubrir el flujo HTTP CRUD, orden de creación, aislamiento entre instancias, actualización parcial, descripción vacía, recursos inexistentes en todas las operaciones, validaciones sin mutación y no reutilización de identificadores. Verificaciones ejecutadas: `python -m pytest -q` (41 passed) y `git diff --check`.

## Fase 7 — Documentación de entrega y demostración — Completada

**Objetivo:** hacer el proyecto comprensible y reproducible para terceros.

- Completar instrucciones de instalación, configuración, ejecución y pruebas.
- Publicar el contrato HTTP con ejemplos exclusivamente documentales cuando el formato esté estabilizado.
- Documentar decisiones, limitaciones y comportamiento del almacenamiento local.
- Preparar un activo de demostración corto que muestre una operación CRUD completa.
- Revisar que no haya secretos ni información sensible en el repositorio.

**Resultado esperado:** entrega autocontenida, demostrable y lista para publicar.

**Estado:** completada. Se añadió la guía reproducible [`docs/GUIA_DE_ENTREGA.md`](docs/GUIA_DE_ENTREGA.md), se actualizaron el contrato y el README con ejemplos documentales y se incorporó [`assets/DEMO_CRUD.md`](assets/DEMO_CRUD.md) con un flujo CRUD manual. La revisión de contenido sensible solo encontró menciones documentales de seguridad. Verificaciones ejecutadas: `python -m pytest -q` (41 passed) y `git diff --check`.

## Fase 8 — Posibles mejoras posteriores

**Objetivo:** ampliar el proyecto sin comprometer el núcleo CRUD.

- Sustituir el repositorio en memoria por persistencia durable con migraciones.
- Añadir filtros, ordenación y paginación.
- Incorporar etiquetas, prioridades, fechas límite o recurrencias.
- Añadir autenticación y separación de tareas por usuario.
- Implementar observabilidad, límites de uso, versionado de API y despliegue.
- Evaluar una interfaz web como proyecto independiente o extensión explícita.

**Resultado esperado:** lista priorizable de evoluciones, mantenida fuera del alcance de la primera entrega.