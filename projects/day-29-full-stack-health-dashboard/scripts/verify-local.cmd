@echo off
setlocal

REM Verifica archivos de la estructura inicial sin instalar dependencias.
set "missing=0"

for %%F in (
  "README.md"
  "ROADMAP.md"
  ".env.example"
  "frontend\package.json"
  "frontend\src\app\page.tsx"
  "frontend\src\components\dashboard-view.tsx"
  "frontend\src\lib\dashboard-client.ts"
  "frontend\src\lib\dashboard-validation.ts"
  "frontend\tests\dashboard-contract.test.ts"
  "frontend\tests\dashboard-client.test.ts"
  "frontend\tests\accessibility-regression.test.ts"
  "frontend\src\lib\dashboard-metrics.ts"
  "frontend\tests\dashboard-metrics.test.ts"
  "backend\requirements.txt"
  "backend\src\main.py"
  "backend\src\api\v1.py"
  "backend\src\core\settings.py"
  "backend\src\repositories\local_fixture_repository.py"
  "backend\tests\test_dashboard_api.py"
  "backend\tests\test_local_fixture_repository.py"
  "docs\ARCHITECTURE.md"
  "docs\API_CONTRACT.md"
  "docs\SECURITY_AND_PRIVACY.md"
  "docs\DEVELOPMENT.md"
  "shared\contracts\v1\dashboard.schema.json"
  "shared\types\dashboard.ts"
  "backend\src\domain\contracts.py"
  "backend\tests\test_dashboard_contract.py"
  "data\fixtures\health-dashboard.sample.json"
  "scripts\check-secrets.py"
  "scripts\verify-quality.cmd"
) do (
  if not exist %%~F (
    echo FALTA: %%~F
    set "missing=1"
  ) else (
    echo OK: %%~F
  )
)

if "%missing%"=="1" (
  echo.
  echo La estructura inicial esta incompleta.
  exit /b 1
)

echo.
echo La estructura y las herramientas locales requeridas estan disponibles.
exit /b 0
