# Ejemplos de respuestas HTTP v1

> **Estado:** respuestas implementadas y verificadas en la Fase 4. Los valores reflejan el fixture sintético local actual y la forma JSON definida en [`docs/CONTRATO_API_V1.md`](../docs/CONTRATO_API_V1.md).

Las rutas, códigos y estructuras de este documento están disponibles localmente mediante [`src/main.py`](../src/main.py). Los valores proceden del fixture de demo y pueden cambiar únicamente mediante una actualización coordinada de contrato, fixture y pruebas.

## `GET /health` — 200 OK

```json
{
  "status": "ok"
}
```

## `GET /api/v1/profile` — 200 OK

```json
{
  "name": "Jordan Vega",
  "headline": "Backend developer focused on reliable APIs",
  "summary": "Builds small, maintainable services with clear contracts and local-first demos.",
  "location": "Remote, Europe",
  "links": [
    {
      "label": "Portfolio",
      "url": "https://portfolio.example.test"
    }
  ]
}
```

## `GET /api/v1/projects` — 200 OK

La representación de lista no incluye `description`.

```json
{
  "items": [
    {
      "slug": "portfolio-api",
      "title": "Portfolio API",
      "summary": "Read-only API contract for a professional portfolio.",
      "technologies": [
        "Python",
        "FastAPI",
        "Pydantic"
      ],
      "status": "active",
      "featured": true,
      "published_at": "2026-09",
      "links": [
        {
          "label": "Repository",
          "url": "https://code.example.test/portfolio-api"
        }
      ]
    },
    {
      "slug": "log-summary-tool",
      "title": "Log Summary Tool",
      "summary": "Local utility for deterministic log summaries.",
      "technologies": [
        "Python"
      ],
      "status": "completed",
      "featured": false,
      "published_at": "2026-08"
    }
  ]
}
```

## `GET /api/v1/projects/{slug}` — 200 OK

Ejemplo para `GET /api/v1/projects/portfolio-api`:

```json
{
  "slug": "portfolio-api",
  "title": "Portfolio API",
  "summary": "Read-only API contract for a professional portfolio.",
  "description": "A local-first API design that exposes only public profile information, projects, skills and experience.",
  "technologies": [
    "Python",
    "FastAPI",
    "Pydantic"
  ],
  "status": "active",
  "featured": true,
  "published_at": "2026-09",
  "links": [
    {
      "label": "Repository",
      "url": "https://code.example.test/portfolio-api"
    }
  ]
}
```

## `GET /api/v1/projects/{slug}` — 404 Not Found

Ejemplo para un `slug` válido que no identifica un proyecto público:

```json
{
  "error": {
    "code": "project_not_found",
    "message": "The requested public project was not found."
  }
}
```

## `GET /api/v1/projects/{slug}` — 422 Unprocessable Content

Ejemplo para un `slug` que incumple la gramática, como `Portfolio_API`. El contenido exacto de `msg` puede variar según FastAPI/Pydantic; el estado, `loc` y `type` forman parte del contrato de validación.

```json
{
  "detail": [
    {
      "loc": [
        "path",
        "slug"
      ],
      "msg": "String should match pattern '^[a-z0-9]+(?:-[a-z0-9]+)*$'",
      "type": "string_pattern_mismatch"
    }
  ]
}
```

## `GET /api/v1/skills` — 200 OK

```json
{
  "items": [
    {
      "name": "FastAPI",
      "category": "backend",
      "context": "API design and OpenAPI-first contracts."
    },
    {
      "name": "Python",
      "category": "backend"
    },
    {
      "name": "Git",
      "category": "tools",
      "context": "Version control and reproducible delivery workflows."
    }
  ]
}
```

## `GET /api/v1/experience` — 200 OK

```json
{
  "items": [
    {
      "organization": "Sample Systems Lab",
      "role": "Backend Developer",
      "summary": "Designed small HTTP services and their validation contracts.",
      "started_at": "2025-02",
      "technologies": [
        "Python",
        "FastAPI"
      ]
    },
    {
      "organization": "Example Learning Institute",
      "role": "Software Engineering Program",
      "summary": "Completed project-based practice in API and data tooling.",
      "started_at": "2023-09",
      "ended_at": "2024-06",
      "technologies": [
        "Python",
        "Git"
      ]
    }
  ]
}
```

## Error interno — 500 Internal Server Error

La aplicación oculta detalles internos y usa esta forma para una fuente local incompatible o un fallo inesperado:

```json
{
  "error": {
    "code": "internal_error",
    "message": "An unexpected error occurred."
  }
}
```

## Casos de colección vacía

Las colecciones públicas vacías son válidas y se diferencian de un fallo de fuente:

```json
{
  "items": []
}
```
