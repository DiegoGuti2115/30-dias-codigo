@echo off
setlocal

REM Ejecuta comprobaciones reproducibles sin credenciales; npm audit consulta el registro.
set "project_root=%~dp0.."

pushd "%project_root%" || exit /b 1

call scripts\verify-local.cmd
if errorlevel 1 goto :failure

python -m json.tool shared\contracts\v1\dashboard.schema.json > NUL
if errorlevel 1 goto :failure

python -m json.tool data\fixtures\health-dashboard.sample.json > NUL
if errorlevel 1 goto :failure

python -m compileall -q backend\src backend\tests
if errorlevel 1 goto :failure

python scripts\check-secrets.py
if errorlevel 1 goto :failure

python -m pytest backend\tests -q
if errorlevel 1 goto :failure

pushd frontend || goto :failure
call npm run lint
if errorlevel 1 goto :failure_frontend

call npm run typecheck
if errorlevel 1 goto :failure_frontend

call npm test
if errorlevel 1 goto :failure_frontend

call npm run build
if errorlevel 1 goto :failure_frontend

call npm audit --omit=dev --audit-level=high
if errorlevel 1 goto :failure_frontend

popd
popd
echo.
echo Las comprobaciones de calidad finalizaron correctamente.
exit /b 0

:failure_frontend
popd
:failure
popd
echo.
echo Una comprobacion de calidad fallo.
exit /b 1
