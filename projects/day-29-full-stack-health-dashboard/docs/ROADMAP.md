# Roadmap — Dashboard de salud full-stack

Este roadmap organiza el desarrollo incremental del proyecto del Día 29. Prioriza una demo local segura y reproducible antes de incorporar datos personales, proveedores externos o capacidades reguladas.

> **Límite clínico:** el producto no debe diagnosticar, prescribir, priorizar atención ni emitir recomendaciones médicas. Cualquier propuesta que pueda influir en decisiones de salud requiere evaluación de profesionales sanitarios, privacidad, seguridad, legal y regulación antes de diseñarse, implementarse o demostrarse como funcionalidad clínica.

## Leyenda

- **MVP:** imprescindible para una primera demostración full-stack local.
- **Posterior:** mejora planificada fuera de la primera entrega.
- **Prioridad:** P0 (bloqueante), P1 (alta), P2 (media), P3 (baja).
- **Complejidad:** S (pequeña), M (media), L (alta), XL (muy alta).

## Resumen de fases

| Fase | Alcance | Entrega | Estado | Progreso verificado | Prioridad | Complejidad |
|---|---|---|---|---|:---:|:---:|
| 0 | Preparación y límites | Repositorio, decisiones y política de datos | MVP | Completada | P0 | S |
| 1 | Arquitectura y contratos | Monorepo, contrato HTTP y fixtures | MVP | Completada | P0 | M |
| 2 | Fundaciones técnicas | Configuración, calidad y ejecución local | MVP | Completada | P0 | M |
| 3 | Backend | API, validación y fuente local | MVP | Completada | P0 | M |
| 4 | Frontend | Shell, estados y cliente de datos | MVP | Completada | P0 | M |
| 5 | Métricas y dashboard | Registro manual y visualización no clínica | MVP | Completada | P0 | L |
| 6 | Autenticación, perfiles y persistencia | Cuentas y datos aislados por persona | Posterior | Pendiente | P1 | XL |
| 7 | Integraciones | Importaciones consentidas y fallback | Posterior | Pendiente | P2 | L |
| 8 | Pruebas, accesibilidad y seguridad | Calidad integral y controles | MVP/P1 | Completada (controles básicos MVP) | P0 | L |
| 9 | Observabilidad y despliegue | Operación, entrega y monitorización | Posterior | Pendiente | P1 | L |
| 10 | Mantenimiento y evolución | Ciclo de soporte y gobernanza | Posterior | Pendiente | P1 | M |

---

## Fase 0 — Preparación, alcance y límites de producto

**Tipo:** MVP · **Prioridad:** P0 · **Complejidad:** S · **Progreso:** Completada

### Evidencia de progreso

La fase se completó durante la primera tarea: [README.md](README.md) define el propósito, usuarios objetivo, alcance del MVP, exclusiones y aviso no clínico; [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md) fija el uso exclusivo de datos sintéticos y la política de secretos; [data/fixtures/health-dashboard.sample.json](data/fixtures/health-dashboard.sample.json) es un fixture reproducible y marcado como ficticio. La política de fallback local está documentada en [README.md](README.md).

### Objetivos

- Delimitar el dashboard como herramienta personal de visualización no clínica.
- Establecer que la demo usa únicamente datos sintéticos o introducidos manualmente para pruebas locales.
- Documentar restricciones de privacidad, integraciones y uso de datos.

### Entregables

- [README.md](README.md) completo en español.
- [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md) con controles mínimos.
- Declaración de funcionalidades excluidas y aviso no clínico.

### Tareas principales

- Confirmar usuarios objetivo, alcance MVP y límites clínicos.
- Definir la política de no incluir secretos ni datos de salud reales.
- Alinear el proyecto con la política de fallback local del repositorio.

### Dependencias

- Ninguna.

### Criterios de aceptación

- La documentación deja claro que no se ofrecen diagnósticos ni recomendaciones médicas.
- Las fuentes de datos iniciales son sintéticas y reproducibles.
- Los límites de privacidad son visibles antes de cualquier propuesta de integración.

---

## Fase 1 — Arquitectura inicial, contratos y modelo de datos

**Tipo:** MVP · **Prioridad:** P0 · **Complejidad:** M · **Progreso:** Completada

### Evidencia de progreso

La estructura separa [frontend/](frontend/), [backend/](backend/), [shared/](shared/), [data/](data/) e [infra/](infra/). El contrato versionado canónico está en [shared/contracts/v1/dashboard.schema.json](shared/contracts/v1/dashboard.schema.json); sus tipos TypeScript sincronizados se encuentran en [shared/types/dashboard.ts](shared/types/dashboard.ts) y el consumidor de frontend los expone mediante [frontend/src/lib/dashboard-contract.ts](frontend/src/lib/dashboard-contract.ts). El backend materializa la validación con modelos Pydantic en [backend/src/domain/contracts.py](backend/src/domain/contracts.py) y conserva los límites de proveedor mediante los puertos [backend/src/repositories/dashboard_repository.py](backend/src/repositories/dashboard_repository.py) y [backend/src/core/authentication.py](backend/src/core/authentication.py).

El fixture sintético representativo [data/fixtures/health-dashboard.sample.json](data/fixtures/health-dashboard.sample.json) declara la versión `v1`, perfil, métricas y mediciones no clínicas con fechas ISO 8601. [backend/tests/test_dashboard_contract.py](backend/tests/test_dashboard_contract.py) verifica que el fixture es válido, que sus referencias e identificadores son coherentes, que se rechazan propiedades no declaradas y que el esquema mantiene la versión y el límite no clínico. La compatibilidad y evolución del contrato están documentadas en [docs/API_CONTRACT.md](docs/API_CONTRACT.md) y la separación de capas en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

La verificación final de esta fase pasó mediante [scripts/verify-local.cmd](scripts/verify-local.cmd), validación JSON, compilación Python, `pytest` (6 pruebas), ESLint, comprobación de tipos TypeScript, Vitest y build de Next.js. La ruta HTTP `/api/v1` se mantiene deliberadamente fuera de esta fase y corresponde a la Fase 3.

### Objetivos

- Definir límites entre interfaz, API, dominio, repositorios y contratos compartidos.
- Diseñar un contrato mínimo para métricas no clínicas, sin acoplarlo a una base de datos o proveedor.
- Establecer la versión inicial de API y el fallback local.

### Entregables

- Estructura [frontend/](frontend/), [backend/](backend/), [shared/](shared/), [data/](data/) e [infra/](infra/).
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) y [docs/API_CONTRACT.md](docs/API_CONTRACT.md).
- Fixture JSON sintético y esquema/documentación de contrato inicial.

### Tareas principales

- Definir recursos previstos: perfil, métrica, medición y serie temporal.
- Establecer convenciones de fechas, unidades, validación y errores HTTP.
- Documentar que los nombres de métricas no implican interpretación clínica.
- Preparar puertos de repositorio y autenticación sin seleccionar proveedor.

### Dependencias

- Fase 0.

### Criterios de aceptación

- La estructura separa frontend, backend y contratos sin duplicar responsabilidades.
- El contrato documenta ejemplos sintéticos, validación y compatibilidad.
- La API puede evolucionar sin cambiar la UI directamente contra un proveedor externo.

---

## Fase 2 — Fundaciones técnicas y experiencia de desarrollo

**Tipo:** MVP · **Prioridad:** P0 · **Complejidad:** M · **Progreso:** Completada

### Evidencia de progreso

El frontend cuenta con Next.js, TypeScript estricto, Tailwind, ESLint y Vitest en [frontend/](frontend/); el backend usa FastAPI, pytest y metadatos de proyecto en [backend/pyproject.toml](backend/pyproject.toml). Los archivos de entorno de ejemplo y [.gitignore](.gitignore) permiten una ejecución local sin secretos. [frontend/next.config.ts](frontend/next.config.ts) fija `outputFileTracingRoot` para que Next.js use correctamente la raíz del monorepo cuando haya archivos de bloqueo fuera de `frontend/`.

Los puntos de entrada mínimos permanecen cubiertos por [backend/tests/test_health.py](backend/tests/test_health.py) y [frontend/tests/page.test.ts](frontend/tests/page.test.ts); [frontend/tests/dashboard-contract.test.ts](frontend/tests/dashboard-contract.test.ts) comprueba que el consumidor frontend expone la versión de contrato compartida. [scripts/verify-local.cmd](scripts/verify-local.cmd) comprueba los artefactos requeridos sin instalar dependencias y [scripts/verify-quality.cmd](scripts/verify-quality.cmd) reúne validación JSON, `compileall`, `pytest`, ESLint, comprobación de tipos, Vitest y build de Next.js. La instalación, ejecución y contribución sin credenciales están documentadas en [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) y enlazadas desde [README.md](README.md).

La verificación final pasó con `scripts\\verify-quality.cmd`: validación JSON del esquema y fixture, compilación Python, `pytest` (6 pruebas), ESLint, TypeScript, Vitest (2 pruebas) y build de Next.js. No quedan entregables pendientes dentro del alcance de la Fase 2; rutas de datos, cliente HTTP y estados funcionales corresponden a las Fases 3 y 4.

### Objetivos

- Hacer reproducible la instalación, configuración y comprobación local.
- Añadir configuraciones mínimas de calidad sin dependencias no justificadas.

### Entregables

- Configuración de Next.js, TypeScript, Tailwind y FastAPI.
- Archivos de entorno de ejemplo sin secretos.
- Puntos de entrada mínimos y pruebas de humo.
- Script de verificación local y guía de contribución.

### Tareas principales

- Configurar tipado estricto, lint y build en frontend.
- Configurar pytest y metadatos de proyecto en backend.
- Añadir [scripts/verify-local.cmd](scripts/verify-local.cmd) para verificar la estructura sin instalar dependencias.
- Ignorar entornos virtuales, dependencias, builds y archivos de entorno locales.

### Dependencias

- Fase 1.

### Criterios de aceptación

- Los comandos documentados en [README.md](README.md) coinciden con archivos reales.
- Las configuraciones no requieren credenciales para ejecutarse.
- Las pruebas de humo identifican los puntos de entrada mínimos.

---

## Fase 3 — Backend y acceso a datos local

**Tipo:** MVP · **Prioridad:** P0 · **Complejidad:** M · **Progreso:** Completada

### Evidencia de progreso

La aplicación creada por [backend/src/main.py](backend/src/main.py) conserva el health check técnico `GET /health` y publica la API versionada mediante [backend/src/api/v1.py](backend/src/api/v1.py): `GET /api/v1/dashboard` devuelve el fixture sintético validado y `POST /api/v1/measurements` registra mediciones manuales exclusivamente en memoria para la demostración local. Las rutas no realizan inferencias, alertas ni valoraciones médicas.

La configuración tipada de [backend/src/core/settings.py](backend/src/core/settings.py) resuelve el fixture local y un conjunto explícito de orígenes CORS; rechaza comodines y [backend/src/main.py](backend/src/main.py) limita los métodos a `GET` y `POST`. El adaptador [backend/src/repositories/local_fixture_repository.py](backend/src/repositories/local_fixture_repository.py) valida el JSON y sus referencias, copia el dashboard para evitar mutaciones externas y genera identificadores de mediciones manuales sin base de datos ni red. El puerto [backend/src/repositories/dashboard_repository.py](backend/src/repositories/dashboard_repository.py) mantiene separadas las rutas de la fuente de datos.

Los modelos Pydantic de solicitudes, respuestas y errores en [backend/src/domain/contracts.py](backend/src/domain/contracts.py) validan identificadores, números finitos y fechas; los controladores de excepción de [backend/src/main.py](backend/src/main.py) normalizan errores de solicitud, métrica inexistente y fuente no disponible sin revelar configuración sensible. [backend/tests/test_dashboard_api.py](backend/tests/test_dashboard_api.py) cubre lectura correcta, estado vacío, alta manual, entrada inválida, métrica no encontrada, fallo del repositorio y CORS; [backend/tests/test_local_fixture_repository.py](backend/tests/test_local_fixture_repository.py) cubre carga, referencias inválidas, métrica desconocida e identificadores únicos. El contrato y la operación actualizados están documentados en [docs/API_CONTRACT.md](docs/API_CONTRACT.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) y [README.md](README.md).

La verificación final pasó con [scripts/verify-quality.cmd](scripts/verify-quality.cmd): validación JSON, `compileall`, `pytest` (17 pruebas), ESLint, comprobación de tipos TypeScript, Vitest (2 pruebas) y build de Next.js. [scripts/verify-local.cmd](scripts/verify-local.cmd) también pasó; `git diff --check` no informó errores de espacios. No quedan entregables pendientes dentro del alcance de la Fase 3.

### Objetivos

- Implementar una API versionada para servir datos sintéticos validados.
- Mantener servicios, reglas y adaptadores separados de las rutas HTTP.

### Entregables

- Rutas `/api/v1` para lectura de dashboard y carga controlada de mediciones manuales de demo.
- Modelos Pydantic para solicitudes, respuestas y errores.
- Repositorio en memoria o basado en fixture local.
- Pruebas unitarias y de API.

### Tareas principales

- Añadir configuración tipada y CORS restringido a desarrollo.
- Validar formato, unidad, fecha y rango técnico antes de persistir o devolver una medición.
- Implementar manejo uniforme de errores y trazabilidad sin datos sensibles.
- Documentar el contrato generado y ejemplos de petición/respuesta sintéticos.

### Dependencias

- Fases 1 y 2.

### Criterios de aceptación

- La API pasa sus pruebas sin red, base de datos ni credenciales.
- Una respuesta inválida no llega a la interfaz como medición válida.
- Las rutas no realizan inferencias, alertas ni valoraciones médicas.
- El health check técnico sigue disponible y no revela configuración sensible.

---

## Fase 4 — Frontend, navegación y estados de datos

**Tipo:** MVP · **Prioridad:** P0 · **Complejidad:** M · **Progreso:** Completada

### Evidencia de progreso

[frontend/src/app/page.tsx](frontend/src/app/page.tsx) y [frontend/src/components/dashboard-view.tsx](frontend/src/components/dashboard-view.tsx) implementan un shell responsive y semántico con navegación por anclas, enlace para saltar al contenido, foco visible, aviso no clínico y una tabla textual navegable por teclado. La interfaz representa explícitamente los estados de carga, datos disponibles, fuente alternativa activa y conjunto de mediciones vacío; ninguna interacción esencial depende de hover o color.

[frontend/src/lib/dashboard-client.ts](frontend/src/lib/dashboard-client.ts) consume `GET /api/v1/dashboard` usando `NEXT_PUBLIC_API_BASE_URL`, y [frontend/src/lib/dashboard-validation.ts](frontend/src/lib/dashboard-validation.ts) valida de forma estricta la estructura, versión, fechas, valores finitos, identificadores y referencias del contrato antes de entregar datos a la presentación. Ante un error HTTP, de red o de contrato inválido, el cliente carga el fixture sintético local y muestra una advertencia recuperable que identifica el origen activo. El fallback es funcional y no sustituye la integración con mocks ni datos creados por componentes.

[frontend/tests/dashboard-client.test.ts](frontend/tests/dashboard-client.test.ts) cubre respuesta válida y vacía, fallo de red, error HTTP, contrato malformado y referencias de mediciones inválidas. Junto con [frontend/tests/dashboard-contract.test.ts](frontend/tests/dashboard-contract.test.ts) y [frontend/tests/page.test.ts](frontend/tests/page.test.ts), la suite frontend suma 7 pruebas. Las instrucciones, arquitectura y alcance se actualizaron en [README.md](README.md), [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) y [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

La verificación final pasó con [scripts/verify-quality.cmd](scripts/verify-quality.cmd): validación JSON, `compileall`, `pytest` (17 pruebas), ESLint, comprobación de tipos TypeScript, Vitest (7 pruebas) y build de Next.js. [scripts/verify-local.cmd](scripts/verify-local.cmd) y `git diff --check` también pasaron. No quedan entregables pendientes dentro del alcance de la Fase 4.

### Objetivos

- Construir un shell de aplicación responsive y accesible.
- Conectar la interfaz con la API mediante un cliente desacoplado y fallback local.

### Entregables

- Layout, navegación y estados de carga, vacío, error y datos disponibles.
- Cliente HTTP tipado y validación de datos recibidos.
- Adaptador de fixture local para desarrollo y demo.
- Pruebas de componentes y de flujo de carga.

### Tareas principales

- Definir jerarquía visual, mensajes no clínicos y manejo de errores recuperables.
- Configurar el origen de API con `NEXT_PUBLIC_API_BASE_URL`.
- Garantizar que la UI representa una fuente no disponible sin ocultar el error.
- Revisar navegación por teclado y responsive desde el primer componente.

### Dependencias

- Fases 1, 2 y 3.

### Criterios de aceptación

- La aplicación inicia con fixture local si la API no está disponible.
- El usuario puede identificar el origen y estado de los datos mostrados.
- No hay interacción esencial dependiente exclusivamente de hover o color.

---

## Fase 5 — Dashboard de métricas y registro manual no clínico

**Tipo:** MVP · **Prioridad:** P0 · **Complejidad:** L · **Progreso:** Completada

### Evidencia de progreso

[frontend/src/components/dashboard-view.tsx](frontend/src/components/dashboard-view.tsx) muestra tarjetas de resumen con el último registro y su cantidad por métrica, filtros temporales de 7 días, 30 días o todo el historial, y una serie cronológica no clínica. Cada serie cuenta con su alternativa tabular equivalente, descripciones accesibles y estados explícitos cuando el periodo no contiene datos. La presentación identifica unidad, fecha y origen, sin etiquetar valores como normales, anómalos, riesgos ni objetivos.

El formulario de captura manual valida en el navegador que exista un valor finito y una fecha antes de enviar `POST /api/v1/measurements`; el cliente [frontend/src/lib/dashboard-client.ts](frontend/src/lib/dashboard-client.ts) valida también la respuesta del servidor antes de actualizar la sesión. La medición se incorpora al dashboard local en memoria y comunica confirmación o error recuperable. El flujo sigue siendo reproducible con el fixture y no incorpora persistencia, autenticación ni proveedores externos.

Las transformaciones puras para ordenar, filtrar por rango, agrupar series y resumir el último registro están en [frontend/src/lib/dashboard-metrics.ts](frontend/src/lib/dashboard-metrics.ts). [frontend/tests/dashboard-metrics.test.ts](frontend/tests/dashboard-metrics.test.ts) cubre filtros, inmutabilidad, series, estados vacíos y resúmenes; [frontend/tests/dashboard-client.test.ts](frontend/tests/dashboard-client.test.ts) cubre envío manual y respuesta inválida además del fallback previo. La verificación final pasó con [scripts/verify-quality.cmd](scripts/verify-quality.cmd): validación JSON, `compileall`, `pytest` (17 pruebas), ESLint, TypeScript, Vitest (13 pruebas) y build de Next.js. [scripts/verify-local.cmd](scripts/verify-local.cmd) también pasó.

### Objetivos

- Ofrecer una visualización útil de métricas personales de ejemplo.
- Permitir un flujo manual de demostración sin convertir valores en conclusiones médicas.

### Entregables

- Tarjetas de resumen, filtros temporales, tendencia y tabla alternativa para gráficos.
- Formulario de captura manual con validación técnica y mensajes de confirmación.
- Métricas de demo documentadas, por ejemplo actividad, descanso autodeclarado o hidratación, sin umbrales clínicos.
- Cobertura de cálculos de presentación y comportamiento de filtros.

### Tareas principales

- Implementar transformaciones puras para series, rangos y agregados visuales.
- Diferenciar medidas, unidades y fechas sin etiquetar valores como normales o anómalos.
- Incluir contexto de captura, origen y limitaciones de cada dato.
- Añadir alternativa tabular y descripciones accesibles para toda visualización.

### Dependencias

- Fases 3 y 4.

### Criterios de aceptación

- El dashboard funciona con fixture y datos manuales de demo.
- Los cálculos se prueban de forma aislada y las gráficas tienen alternativa textual o tabular.
- La interfaz no comunica diagnóstico, riesgo, objetivo terapéutico ni recomendación.
- La demo es reproducible sin servicios externos.

---

## Fase 6 — Autenticación, usuarios, perfiles y persistencia

**Tipo:** Posterior · **Prioridad:** P1 · **Complejidad:** XL · **Progreso:** Pendiente

### Evidencia de progreso

No hay modelo de usuario, autenticación, autorización, base de datos, migraciones ni pruebas de aislamiento. [backend/.env.example](backend/.env.example) únicamente reserva `DATABASE_URL` y `AUTH_PROVIDER`, y [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) aplaza la selección de ambos; estas plantillas no constituyen implementación.

### Objetivos

- Incorporar cuentas y aislamiento estricto de datos por usuario.
- Seleccionar persistencia y proveedor de identidad a partir de requisitos reales y revisión de riesgo.

### Entregables

- Modelo de usuario, perfil y propiedad de recurso.
- Autenticación, autorización y ciclo de sesión documentados.
- Migraciones, respaldo, retención y borrado de datos.
- Pruebas de control de acceso y auditoría.

### Tareas principales

- Realizar análisis de amenazas y evaluación de impacto de privacidad.
- Elegir proveedor de identidad y base de datos con criterios de seguridad, coste y región.
- Implementar hash/gestión de credenciales o flujo OIDC según la decisión aprobada.
- Añadir consentimiento, exportación, eliminación y gestión de cuenta cuando sea aplicable.

### Dependencias

- MVP completo, revisión de [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md) y decisión de arquitectura aprobada.

### Criterios de aceptación

- Ningún usuario puede acceder a recursos de otro usuario.
- Secretos y tokens no se registran ni se exponen a clientes no autorizados.
- La retención, el borrado y la exportación están documentados y verificados.
- Se completa la revisión legal/regulatoria aplicable antes de datos reales.

---

## Fase 7 — Integraciones y fuentes de datos externas

**Tipo:** Posterior · **Prioridad:** P2 · **Complejidad:** L · **Progreso:** Pendiente

### Evidencia de progreso

No existen adaptadores, autorizaciones de proveedor ni sincronizaciones. El fallback local se definió como convención en [README.md](README.md) y el fixture sintético existe, pero no hay una integración que pueda fallar ni una implementación que demuestre el fallback.

### Objetivos

- Evaluar importaciones opcionales de dispositivos o servicios bajo consentimiento explícito.
- Mantener la demo íntegra sin dependencia de proveedor.

### Entregables

- Adaptadores por proveedor detrás de puertos de dominio.
- Flujo de autorización y revocación consentido.
- Mapeo, normalización y trazabilidad del origen del dato.
- Fixtures/mocks por integración.

### Tareas principales

- Validar permisos, cuota, seguridad y política de privacidad del proveedor.
- Limitar el alcance de datos importados y su frecuencia.
- Diseñar reintentos, errores, revocación y borrado de datos importados.
- Documentar la decisión de fallback T+30 del repositorio.

### Dependencias

- Fase 6, evaluación de privacidad y proveedor validado.

### Criterios de aceptación

- La pérdida de una integración no bloquea el dashboard ni la demo local.
- Cada dato muestra su origen y momento de sincronización.
- La revocación corta nuevos accesos y ejecuta el tratamiento acordado de datos.

---

## Fase 8 — Calidad, seguridad y accesibilidad transversal

**Tipo:** MVP para controles básicos; P1 para profundidad avanzada · **Prioridad:** P0 · **Complejidad:** L · **Progreso:** Completada (controles básicos MVP)

### Evidencia de progreso

La suite se ejecuta por capas sin red de servicios ni credenciales: [backend/tests/test_dashboard_api.py](backend/tests/test_dashboard_api.py) prueba el recorrido integrado de crear una medición manual y recuperarla con el dashboard de la misma sesión; [frontend/tests/dashboard-client.test.ts](frontend/tests/dashboard-client.test.ts) cubre el cliente, fallback y validación del contrato; [frontend/tests/dashboard-metrics.test.ts](frontend/tests/dashboard-metrics.test.ts) cubre transformaciones puras; y [frontend/tests/accessibility-regression.test.ts](frontend/tests/accessibility-regression.test.ts) preserva el enlace de salto, semántica, estados anunciados, etiquetas, tabla alternativa y foco visible. No se añade un navegador E2E completo porque el recorrido MVP ya se cubre en los límites HTTP y de presentación con las dependencias existentes; la comprobación manual de teclado, lector de pantalla, contraste y zoom queda explícita en la checklist antes de una demo.

[backend/src/domain/contracts.py](backend/src/domain/contracts.py), [backend/src/main.py](backend/src/main.py) y [backend/tests/test_dashboard_api.py](backend/tests/test_dashboard_api.py) demuestran validación de entradas, CORS restringido y errores normalizados sin eco de valores. [scripts/check-secrets.py](scripts/check-secrets.py) detecta patrones de secretos en archivos versionables; [scripts/verify-quality.cmd](scripts/verify-quality.cmd) lo ejecuta junto con validación JSON, compilación Python, pytest, ESLint, TypeScript, Vitest, build y `npm audit --omit=dev --audit-level=high`. El frontend se actualizó a Next.js 16.3.6 y la auditoría de dependencias de ejecución no informa vulnerabilidades. [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md) contiene la checklist manual y los límites para datos reales.

Los controles avanzados siguen fuera de alcance hasta Fases 6, 7 y 9: pruebas de autenticación/autorización, persistencia, análisis de amenazas formal, CI/CD, observabilidad y revisión profesional/regulatoria previa a datos reales. No se representan como implementados en este MVP.

### Objetivos

- Asegurar fiabilidad, protección de datos y uso inclusivo en todas las fases.

### Entregables

- Suite de pruebas unitaria, integración y extremo a extremo acorde al alcance.
- Checklist de accesibilidad y revisión de seguridad.
- Automatización de lint, tipos, pruebas, build y detección de secretos.

### Tareas principales

- Establecer objetivos de cobertura útiles por capa, sin perseguir métricas vacías.
- Validar inputs, controlar CORS, errores y registros.
- Revisar contraste, foco, semántica, tamaño táctil y alternativas a gráficos.
- Realizar análisis de dependencias y revisión de amenazas antes de cada despliegue.

### Dependencias

- Transversal; comienza en Fase 2 y se amplía con cada entrega.

### Criterios de aceptación

- Las comprobaciones automatizadas pasan antes de integrar cambios.
- Los recorridos principales son utilizables con teclado y lector de pantalla.
- No se incluyen datos sensibles, secretos o tokens en repositorio, logs o fixtures.
- La seguridad de autenticación y autorización se prueba antes de habilitar datos reales.

---

## Fase 9 — Observabilidad, despliegue y operación

**Tipo:** Posterior · **Prioridad:** P1 · **Complejidad:** L · **Progreso:** Pendiente

### Evidencia de progreso

[infra/README.md](infra/README.md) indica expresamente que no hay proveedor, configuración de despliegue ni secretos seleccionados. El health check técnico existe, pero no hay pipeline, logs estructurados, métricas, alertas, runbook, backups ni despliegue; por ello no se considera avance de la fase.

### Objetivos

- Preparar una entrega controlada y operaciones observables sin exponer información sensible.

### Entregables

- Configuración de despliegue por entorno y pipeline de CI/CD.
- Logs estructurados, health checks, métricas técnicas y alertas operativas.
- Runbook de incidentes, respaldo y recuperación.

### Tareas principales

- Definir hosting, regiones, HTTPS, secretos gestionados y configuración por entorno.
- Añadir instrumentación que no incluya valores sanitarios ni identificadores directos.
- Configurar backups cifrados, restauración probada y rotación de secretos.
- Realizar revisión de seguridad de despliegue y prueba de recuperación.

### Dependencias

- Fases 6 y 8; validación de privacidad y seguridad para datos reales.

### Criterios de aceptación

- Los entornos se despliegan sin secretos en código ni archivos de configuración versionados.
- Se detectan fallos técnicos sin registrar información de salud.
- Existe un procedimiento probado para incidente, rollback y restauración.

---

## Fase 10 — Mantenimiento, gobernanza y evolución responsable

**Tipo:** Posterior · **Prioridad:** P1 · **Complejidad:** M · **Progreso:** Pendiente

### Evidencia de progreso

La documentación inicial establece límites de seguridad, privacidad y evolución responsable, pero no hay calendario de actualizaciones, política de soporte, canal de vulnerabilidades, responsables ni proceso de gobernanza operativo. Esta fase permanece pendiente.

### Objetivos

- Mantener el producto, dependencias y controles de datos de forma sostenible.
- Gobernar cualquier evolución de alcance hacia dominios regulados.

### Entregables

- Calendario de actualización de dependencias y revisiones de seguridad.
- Política de soporte, reporte de vulnerabilidades y gestión de incidencias.
- Registro de decisiones arquitectónicas y revisiones de privacidad.

### Tareas principales

- Revisar periódicamente permisos, retención, integraciones y accesos.
- Mantener fixtures de demo y pruebas de regresión independientes de proveedores.
- Evaluar cambios clínicos potenciales con profesionales y asesoramiento legal antes de planificarlos.
- Documentar deprecaciones y migraciones de contrato.

### Dependencias

- Fases 6, 8 y 9 según el ámbito desplegado.

### Criterios de aceptación

- Hay responsables y cadencia definidos para actualizaciones y vulnerabilidades.
- Los cambios incompatibles tienen migración y comunicación documentadas.
- Ninguna capacidad clínica se entrega sin validación profesional, legal, de privacidad y seguridad explícitamente registrada.

## Orden de implementación recomendado del MVP

1. Completar Fases 0, 1 y 2 para consolidar la base documental y técnica.
2. Implementar Fase 3 con fixture local y pruebas de contrato.
3. Desarrollar Fase 4 para mostrar estados y conectar el cliente desacoplado.
4. Cerrar Fase 5 con visualizaciones, captura manual de demo y accesibilidad.
5. Aplicar los controles de Fase 8 en cada paso, y ejecutar la verificación final descrita en [README.md](README.md).

Las Fases 6 a 10 no forman parte del MVP y no deben iniciar tratamiento de información sanitaria real hasta completar sus dependencias y revisiones correspondientes.
