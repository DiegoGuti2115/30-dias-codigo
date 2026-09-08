# Demo local de 15 segundos — Día 09

## Propósito

Mostrar el flujo real y verificable de la API v1: datos sintéticos locales, respuestas públicas y contrato exclusivamente `GET`.

```text
Fixture sintético validado → consulta local → respuesta HTTP pública
```

No hay despliegue, red saliente, credenciales ni datos personales reales.

## Preparación

Desde [`projects/day-09-portfolio-api`](..), con Python 3.11+ y una terminal visible:

```text
python -m uvicorn main:app --app-dir src
```

El servidor local queda disponible en `http://127.0.0.1:8000`. Muestra únicamente la interfaz local [`/docs`](http://127.0.0.1:8000/docs), las rutas públicas o los fixtures sintéticos aprobados. No muestres rutas personales, credenciales ni archivos ajenos al proyecto.

## Guion cronometrado

| Tiempo | Acción visible | Mensaje |
|---:|---|---|
| 0–3 s | Abrir `http://127.0.0.1:8000/docs`. | «API FastAPI local y de solo lectura.» |
| 3–6 s | Ejecutar `GET /health`. | «La aplicación responde sin depender del fixture.» |
| 6–10 s | Ejecutar `GET /api/v1/projects`. | «Los proyectos públicos salen de un fixture sintético validado.» |
| 10–13 s | Ejecutar `GET /api/v1/projects/portfolio-api`. | «El detalle expone un esquema público explícito.» |
| 13–15 s | Mostrar que las operaciones documentadas son `GET`. | «Sin rutas de escritura ni despliegue público en v1.» |

## Comprobación alternativa por terminal

Con el servidor en ejecución:

```text
curl.exe --fail-with-body http://127.0.0.1:8000/health
curl.exe --fail-with-body http://127.0.0.1:8000/api/v1/projects
curl.exe --include http://127.0.0.1:8000/api/v1/projects/draft-internal-notes
```

La última petición debe devolver `404` con `project_not_found`; no debe confirmar que el registro existe ni exponer campos internos de visibilidad.

## Cierre

Detén Uvicorn al terminar. No publiques la demo si el servidor no responde localmente, si la interfaz muestra métodos distintos de `GET` o si aparece información distinta de los fixtures sintéticos del proyecto.