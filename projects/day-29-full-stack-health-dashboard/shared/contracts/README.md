# Contratos compartidos

El contrato canónico actual es [v1/dashboard.schema.json](v1/dashboard.schema.json). Define el fixture no clínico de dashboard y se sincroniza con:

- [backend/src/domain/contracts.py](../../backend/src/domain/contracts.py), para validación Pydantic.
- [shared/types/dashboard.ts](../types/dashboard.ts), para consumidores TypeScript.
- [backend/tests/test_dashboard_contract.py](../../backend/tests/test_dashboard_contract.py), para validar fixture y reglas esenciales.

No se añaden campos sin actualizar todos los consumidores. Los cambios incompatibles requieren una nueva versión de esquema y una migración documentada en [docs/API_CONTRACT.md](../../docs/API_CONTRACT.md).
