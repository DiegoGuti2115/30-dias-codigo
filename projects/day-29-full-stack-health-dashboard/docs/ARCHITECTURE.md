# Arquitectura inicial

## Estado

Las Fases 1 a 5 y los controles básicos de la Fase 8 definen los límites del monorepo, el contrato compartido `v1`, una API local funcional y un cliente web desacoplado. El backend sirve datos sintéticos validados mediante `/api/v1`, sin autenticación, base de datos ni proveedor externo; el frontend valida cada respuesta, usa el fixture local cuando la API no está disponible o incumple el contrato y calcula resúmenes y series solo para presentación no clínica.

## Límites

- [frontend/](../frontend/): presentación, navegación accesible, cliente HTTP y consumo del contrato mediante [frontend/src/lib/dashboard-contract.ts](../frontend/src/lib/dashboard-contract.ts). [frontend/src/lib/dashboard-client.ts](../frontend/src/lib/dashboard-client.ts) resuelve la fuente y [frontend/src/lib/dashboard-validation.ts](../frontend/src/lib/dashboard-validation.ts) protege el límite de datos antes de la presentación.
- [backend/](../backend/): API HTTP v1, modelos Pydantic en [backend/src/domain/contracts.py](../backend/src/domain/contracts.py), configuración tipada y puertos de infraestructura.
- [shared/contracts/](../shared/contracts/): JSON Schema versionado, independiente de frameworks.
- [shared/types/](../shared/types/): tipos TypeScript sincronizados con el contrato JSON Schema.
- [data/fixtures/](../data/fixtures/): datos sintéticos locales validados contra el modelo de dominio.
- [infra/](../infra/): documentación de despliegue futura sin proveedor ni secretos.

## Dependencias permitidas

El frontend consume solo tipos publicados desde `shared` y, en fases posteriores, contratos HTTP de la API. No puede depender de repositorios, modelos Pydantic ni proveedores. El backend depende de puertos de persistencia e identidad, no de una base de datos o proveedor concreto.

[DashboardRepository](../backend/src/repositories/dashboard_repository.py) define las operaciones de lectura y alta manual. [LocalFixtureDashboardRepository](../backend/src/repositories/local_fixture_repository.py) lo implementa con el fixture local, lo valida al cargarlo y conserva las altas solo en memoria. [IdentityProvider](../backend/src/core/authentication.py) permanece como puerto sin implementación para una fase posterior.

## Contrato y compatibilidad

El contrato canónico actual es [dashboard.schema.json](../shared/contracts/v1/dashboard.schema.json). Se refleja en [contracts.py](../backend/src/domain/contracts.py) y [dashboard.ts](../shared/types/dashboard.ts). Las pruebas de [test_dashboard_contract.py](../backend/tests/test_dashboard_contract.py) validan el fixture, las referencias de métricas y las restricciones esenciales de versión y propiedades desconocidas.

Cambios compatibles se documentan y prueban dentro de `v1`. Cambios incompatibles crean un directorio de versión nuevo, conservan el contrato anterior mientras haya consumidores y documentan el plan de migración en [API_CONTRACT.md](API_CONTRACT.md).

## Flujo de datos

1. El frontend importa tipos desde su adaptador local de contrato.
2. [frontend/src/components/dashboard-view.tsx](../frontend/src/components/dashboard-view.tsx) solicita el dashboard mediante el cliente HTTP y presenta estados de carga, datos, vacío y fallback.
3. `GET /api/v1/dashboard` obtiene una respuesta validada por el modelo Pydantic `v1`.
4. El cliente valida estructura, versión, fechas, valores e integridad de referencias; solo entonces pasa los datos a la vista.
5. Ante error HTTP, red o contrato inválido, el cliente carga [data/fixtures/health-dashboard.sample.json](../data/fixtures/health-dashboard.sample.json) y muestra el origen alternativo de forma explícita.
6. [frontend/src/lib/dashboard-metrics.ts](../frontend/src/lib/dashboard-metrics.ts) transforma copias de mediciones en series ordenadas, filtros temporales y resúmenes; no determina rangos ni estados de salud.
7. `POST /api/v1/measurements` valida la entrada y delega en `DashboardRepository`; el adaptador local asigna identificador y origen `manual`. El cliente vuelve a validar la respuesta antes de incorporarla al estado de la vista.
8. [backend/src/core/settings.py](../backend/src/core/settings.py) resuelve el fixture y los orígenes CORS sin secretos; los comodines de CORS se rechazan.

## Controles transversales de calidad

- [backend/tests/test_dashboard_api.py](../backend/tests/test_dashboard_api.py) comprueba el recorrido integrado de alta manual seguida de lectura del dashboard dentro de la misma sesión local, además de validación, CORS y errores seguros.
- [frontend/tests/accessibility-regression.test.ts](../frontend/tests/accessibility-regression.test.ts) protege el enlace de salto, las regiones semánticas, etiquetas de formulario, estados anunciados, alternativa tabular y foco visible. Es una regresión estructural; la revisión manual de teclado, contraste y zoom sigue la checklist de [SECURITY_AND_PRIVACY.md](SECURITY_AND_PRIVACY.md).
- [scripts/check-secrets.py](../scripts/check-secrets.py) analiza los archivos versionables relevantes con patrones de credenciales. [scripts/verify-quality.cmd](../scripts/verify-quality.cmd) lo ejecuta junto con lint, tipos, pruebas, build y `npm audit --omit=dev --audit-level=high`.
- El análisis de dependencias se limita a las dependencias de ejecución del frontend. La revisión del entorno Python debe ejecutarse dentro del entorno virtual del proyecto, no contra paquetes globales ajenos al repositorio.

## Decisiones pendientes

La elección de base de datos, autenticación, proveedor cloud, cola y sistema de observabilidad se pospone hasta que exista un requisito probado y una revisión de seguridad y privacidad.
