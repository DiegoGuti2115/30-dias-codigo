# Contrato de API v1

## Estado

La Fase 3 implementa una API local y no clínica bajo el prefijo `/api/v1`. No usa red, credenciales, autenticación ni base de datos: [backend/src/repositories/local_fixture_repository.py](../backend/src/repositories/local_fixture_repository.py) valida y carga el fixture sintético [data/fixtures/health-dashboard.sample.json](../data/fixtures/health-dashboard.sample.json) en memoria.

El contrato de datos canónico sigue siendo [shared/contracts/v1/dashboard.schema.json](../shared/contracts/v1/dashboard.schema.json). Sus modelos Pydantic están en [backend/src/domain/contracts.py](../backend/src/domain/contracts.py) y los tipos del consumidor de interfaz en [shared/types/dashboard.ts](../shared/types/dashboard.ts). La API publica el contrato HTTP verificable en `GET /openapi.json` al ejecutar FastAPI.

## Convenciones

- Prefijo: `/api/v1`.
- Formato: JSON UTF-8.
- Fechas: ISO 8601 con zona horaria explícita.
- Identificadores: cadenas opacas con el patrón `^[a-z][a-z0-9-]{2,63}$`.
- CORS: solo los orígenes configurados en `CORS_ORIGINS`; el comodín `*` se rechaza.
- Persistencia: las inserciones manuales solo viven en la memoria del proceso actual y se eliminan al reiniciar.
- Límite clínico: la API no calcula rangos, riesgos, diagnósticos, alertas ni recomendaciones.

## Endpoints

### `GET /health`

Comprueba la disponibilidad técnica sin revelar entorno, configuración ni contenido del fixture.

**Respuesta `200`:**

```json
{ "status": "ok" }
```

### `GET /api/v1/dashboard`

Lee y valida el fixture local antes de devolver una respuesta `HealthDashboardFixture` del contrato `v1`. Una colección `measurements` vacía es una respuesta válida.

**Respuesta `200`:** el objeto definido por [dashboard.schema.json](../shared/contracts/v1/dashboard.schema.json).

**Respuesta `503`:** si el fixture falta, no es JSON válido o no cumple el contrato.

```json
{
  "code": "dashboard_unavailable",
  "message": "La fuente local del dashboard no está disponible.",
  "details": []
}
```

### `POST /api/v1/measurements`

Añade una medición de demostración al repositorio en memoria. La petición no acepta un `id` ni un `source`: el backend genera un identificador opaco y fija `source` en `manual`.

**Cuerpo de petición:**

```json
{
  "metricId": "daily-steps",
  "value": 1200,
  "recordedAt": "2026-09-02T08:00:00Z"
}
```

`metricId` debe existir en el dashboard cargado. `value` debe ser un número finito; esta validación evita valores no serializables sin establecer rangos, objetivos ni interpretación clínica.

**Respuesta `201`:** una `Measurement` del contrato `v1`, con `source: "manual"`.

**Errores:**

| Estado | Código | Cuándo |
|---|---|---|
| `404` | `metric_not_found` | La métrica no existe en el fixture local. |
| `422` | `invalid_request` | Formato, fecha, propiedad o valor de entrada inválido. |
| `503` | `dashboard_unavailable` | El repositorio local no puede cargar un dashboard válido. |

Todos los errores tienen la forma `ErrorResponse` y no reflejan los valores, identificadores o detalles internos de la solicitud:

```json
{
  "code": "invalid_request",
  "message": "La solicitud no cumple el formato requerido.",
  "details": ["float_parsing"]
}
```

## Fuente de verdad y evolución

| Artefacto | Responsabilidad |
|---|---|
| [shared/contracts/v1/dashboard.schema.json](../shared/contracts/v1/dashboard.schema.json) | Esquema JSON Schema de lectura `v1` |
| [backend/src/domain/contracts.py](../backend/src/domain/contracts.py) | Modelos de respuesta, entrada y error aplicados por la API |
| [backend/src/api/v1.py](../backend/src/api/v1.py) | Métodos, rutas, códigos HTTP y OpenAPI |
| [shared/types/dashboard.ts](../shared/types/dashboard.ts) | Tipos TypeScript sincronizados para consumidores |
| [backend/tests/test_dashboard_api.py](../backend/tests/test_dashboard_api.py) | Compatibilidad HTTP, errores, vacío y CORS |

Un cambio incompatible crea una versión nueva bajo [shared/contracts/](../shared/contracts/), mantiene los consumidores de `v1` mientras sea necesario y documenta una migración. Los nombres de métricas y valores permanecen como datos sintéticos de organización, sin interpretación sanitaria.
