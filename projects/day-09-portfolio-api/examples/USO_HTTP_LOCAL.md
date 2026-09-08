# Uso HTTP local reproducible

> Ejecutar estos ejemplos contra la API local ya implementada. No envían credenciales, no modifican datos y no requieren red externa.

## 1. Iniciar el servidor

Desde [`projects/day-09-portfolio-api`](..), con Python 3.11+:

```text
python -m pip install -r requirements.txt
python -m uvicorn main:app --app-dir src --reload
```

El servidor local queda disponible en `http://127.0.0.1:8000`. Mantener esa terminal abierta durante las peticiones siguientes. La interfaz OpenAPI está en [`/docs`](http://127.0.0.1:8000/docs) y el documento JSON en [`/openapi.json`](http://127.0.0.1:8000/openapi.json).

## 2. Consultas de éxito en PowerShell

Abrir otra terminal PowerShell y ejecutar:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/profile
Invoke-RestMethod http://127.0.0.1:8000/api/v1/projects
Invoke-RestMethod http://127.0.0.1:8000/api/v1/projects/portfolio-api
Invoke-RestMethod http://127.0.0.1:8000/api/v1/skills
Invoke-RestMethod http://127.0.0.1:8000/api/v1/experience
```

Resultados esperados:

- `/health` devuelve `status` igual a `ok` sin evaluar la disponibilidad del fixture.
- `/api/v1/projects` devuelve primero `portfolio-api` y después `log-summary-tool`.
- El detalle `portfolio-api` incluye `description`; la lista de proyectos no.
- Ninguna respuesta contiene `public`, `profile_public`, borradores ni valores opcionales `null`.

Las cargas JSON completas de referencia están en [`RESPUESTAS_PLANIFICADAS.md`](RESPUESTAS_PLANIFICADAS.md).

## 3. Errores comprobables sin ocultar el estado

`Invoke-RestMethod` convierte los códigos no exitosos en excepciones. Este auxiliar conserva el estado y el cuerpo JSON para inspeccionar los contratos negativos:

```powershell
function Invoke-PortfolioRequest([string]$Path) {
  try {
    $response = Invoke-WebRequest "http://127.0.0.1:8000$Path"
    [pscustomobject]@{ StatusCode = $response.StatusCode; Body = $response.Content | ConvertFrom-Json }
  } catch {
    $response = $_.Exception.Response
    $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
    [pscustomobject]@{ StatusCode = [int]$response.StatusCode; Body = $reader.ReadToEnd() | ConvertFrom-Json }
  }
}

Invoke-PortfolioRequest '/api/v1/projects/not-found'
Invoke-PortfolioRequest '/api/v1/projects/draft-internal-notes'
Invoke-PortfolioRequest '/api/v1/projects/Portfolio-API'
```

Resultados esperados:

| Petición | Estado | Cuerpo esperado |
|---|---:|---|
| `not-found` | `404` | `error.code` igual a `project_not_found`. |
| `draft-internal-notes` | `404` | Mismo cuerpo que el ausente; no revela que el fixture lo contiene. |
| `Portfolio-API` | `422` | Raíz `detail` como lista; el primer elemento identifica `path`, `slug` y un `type`. |

La v1 no tiene operaciones de escritura. Por ejemplo, este comando recibe `405`:

```powershell
Invoke-PortfolioRequest '/api/v1/projects' # úsalo solo para GET
Invoke-WebRequest -Method Post -Uri http://127.0.0.1:8000/api/v1/projects -ContentType application/json -Body '{}'
```

## 4. Alternativa con curl.exe

En Windows, usar explícitamente `curl.exe` para evitar el alias de PowerShell:

```text
curl.exe --fail-with-body http://127.0.0.1:8000/health
curl.exe --fail-with-body http://127.0.0.1:8000/api/v1/projects/portfolio-api
curl.exe --include http://127.0.0.1:8000/api/v1/projects/not-found
curl.exe --include http://127.0.0.1:8000/api/v1/projects/Portfolio-API
```

Los dos últimos comandos muestran las cabeceras y permiten observar respectivamente `404` y `422`.

## Límites y seguridad

Los ejemplos solo usan `127.0.0.1`, datos sintéticos del fixture local y rutas `GET`. No añaden tokens, ficheros de entorno, secretos, datos personales ni dependencias externas. No se debe publicar una demostración si muestra rutas personales, terminales con variables sensibles o datos distintos de los fixtures aprobados.