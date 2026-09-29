# Tipos compartidos

[dashboard.ts](dashboard.ts) expone los tipos TypeScript del contrato `v1`. La interfaz debe importarlos mediante [frontend/src/lib/dashboard-contract.ts](../../frontend/src/lib/dashboard-contract.ts), que evita duplicar formas de datos en componentes.

Los tipos se sincronizan manualmente con [shared/contracts/v1/dashboard.schema.json](../contracts/v1/dashboard.schema.json) y con los modelos Pydantic de [backend/src/domain/contracts.py](../../backend/src/domain/contracts.py). No contienen reglas de negocio ni interpretación clínica.
