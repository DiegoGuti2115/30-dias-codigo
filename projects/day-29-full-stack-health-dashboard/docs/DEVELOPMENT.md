# Desarrollo local y comprobaciones

## Objetivo

Esta guía describe una ejecución local reproducible del monorepo sin credenciales, red de terceros ni datos de salud reales. La fuente de referencia es el fixture sintético versionado en [data/fixtures/health-dashboard.sample.json](../data/fixtures/health-dashboard.sample.json).

## Requisitos

- Node.js 20 o superior con npm.
- Python 3.11 o superior.
- Dependencias ya instaladas en `frontend/` y en un entorno virtual local de `backend/`.

## Configuración inicial

Desde la raíz del proyecto en `cmd.exe`:

```bat
copy .env.example .env
copy frontend\.env.example frontend\.env.local
copy backend\.env.example backend\.env
cd frontend && npm install
cd ..\backend && python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Los tres archivos de ejemplo contienen únicamente valores locales. No agregues secretos, tokens ni datos personales. Los archivos de entorno locales, el entorno virtual, `node_modules` y los artefactos de build están excluidos en [.gitignore](../.gitignore).

## Ejecución de los puntos de entrada

Abre dos terminales desde la raíz del proyecto:

```bat
cd backend
.venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

```bat
cd frontend
npm run dev
```

Los puntos de entrada comprobables son:

- Backend: `GET http://localhost:8000/health`, que devuelve disponibilidad técnica sin configuración ni datos sensibles.
- Backend: `GET http://localhost:8000/api/v1/dashboard`, que sirve y valida el fixture sintético local.
- Backend: `POST http://localhost:8000/api/v1/measurements`, que añade una medición manual solo en la memoria del proceso actual.
- Frontend: `http://localhost:3000`, interfaz no clínica que consulta `GET /api/v1/dashboard` mediante `NEXT_PUBLIC_API_BASE_URL`, filtra periodos, muestra series y permite enviar registros manuales.

El cliente frontend valida la respuesta antes de mostrarla. Si el backend no está disponible, responde con error o incumple el contrato `v1`, se carga automáticamente el fixture local y se muestra un aviso con el origen de los datos. La interfaz ofrece periodos de 7/30 días o historial completo y una tabla alternativa para cada serie. El formulario manual envía `POST /api/v1/measurements`; los datos permanecen en memoria y el cliente valida la respuesta antes de incorporarla. Para comprobar el fallback, inicia solo el frontend y abre `http://localhost:3000`. Consulta [docs/API_CONTRACT.md](API_CONTRACT.md) para los cuerpos, códigos HTTP y errores de `/api/v1`.

## Verificaciones

El script [scripts/verify-local.cmd](../scripts/verify-local.cmd) verifica que los artefactos estructurales requeridos existen sin instalar dependencias:

```bat
scripts\verify-local.cmd
```

El script [scripts/verify-quality.cmd](../scripts/verify-quality.cmd) ejecuta, en orden y sin credenciales, toda la batería local:

```bat
scripts\verify-quality.cmd
```

Incluye validación JSON de contrato y fixture, `compileall`, escaneo local de secretos, `pytest`, ESLint, comprobación estricta de tipos TypeScript, Vitest, build de Next.js y auditoría de dependencias de ejecución. Para ejecutar comprobaciones aisladas:

```bat
python scripts\check-secrets.py
python -m json.tool shared\contracts\v1\dashboard.schema.json
python -m json.tool data\fixtures\health-dashboard.sample.json
python -m compileall -q backend\src backend\tests
python -m pytest backend\tests -q
cd frontend && npm run lint && npm run typecheck && npm test && npm run build
cd frontend && npm audit --omit=dev --audit-level=high
```

La auditoría npm exige red para consultar el registro y revisa únicamente dependencias de producción. Si se usa `pip check`, debe invocarse con `backend\.venv\Scripts\python -m pip check` después de instalar los requisitos del proyecto; no se considera válida una comprobación sobre paquetes globales ajenos al entorno virtual.

La prueba de regresión de accesibilidad automatiza los invariantes estructurales del recorrido principal. Antes de una demo, completa también la revisión manual de teclado, foco, contraste y zoom de la checklist en [SECURITY_AND_PRIVACY.md](SECURITY_AND_PRIVACY.md).

## Contribución segura

1. Revisa [ROADMAP.md](../ROADMAP.md), [docs/ARCHITECTURE.md](ARCHITECTURE.md), [docs/API_CONTRACT.md](API_CONTRACT.md) y [docs/SECURITY_AND_PRIVACY.md](SECURITY_AND_PRIVACY.md).
2. Mantén los cambios acotados a una fase y conserva la separación entre frontend, backend, contratos y fixtures.
3. Si cambia un contrato, actualiza el esquema, tipos, modelos, fixture y pruebas dentro del mismo cambio; crea una versión nueva ante una incompatibilidad.
4. Ejecuta [scripts/verify-quality.cmd](../scripts/verify-quality.cmd) antes de integrar y completa la checklist manual aplicable en [SECURITY_AND_PRIVACY.md](SECURITY_AND_PRIVACY.md).
5. No incluyas datos reales, identificadores personales, secretos, archivos `.env`, builds ni dependencias no justificadas.
