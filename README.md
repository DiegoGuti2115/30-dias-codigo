# 🚀 30 Días, 30 Proyectos de Desarrollo

Reto práctico de ingeniería de software: diseñar, programar, documentar y publicar una herramienta funcional cada día de septiembre.

## 🎯 Objetivo

Construir 30 soluciones atómicas orientadas a automatización, APIs, frontend reactivo, IA y agentes. Cada entrega se documenta en GitHub y LinkedIn, manteniendo un límite rígido de tres horas diarias.

## 🛠️ Stack tecnológico

- **Lenguajes:** Python 3.11+, TypeScript.
- **Backend:** FastAPI, Pydantic.
- **Frontend:** Next.js, React, Tailwind CSS, SWR.
- **Datos y validación:** Zod, IndexedDB, Redis opcional.
- **IA y cloud opcionales:** Azure AI Foundry, OpenAI API, Azure Blob Storage, Azure AI Search.

## ⚡ Política de integraciones

Los servicios externos y cloud pueden usarse si su configuración es ágil y mejora la demostración. Cada proyecto que los use debe incluir un fallback local, fixture o mock que garantice la entrega si fallan credenciales, permisos, cuota, red o proveedor.

- Los secretos nunca se suben al repositorio. Consulta [`.env.example`](.env.example).
- Si una integración no valida una conexión o petición/respuesta antes de T+30, se usa el fallback local.
- Las instrucciones completas están en [`docs/DAILY_WORKFLOW.md`](docs/DAILY_WORKFLOW.md).

## 📅 Registro de proyectos

| Día | Proyecto | Categoría | Stack | Código | Demo / Post |
| :---: | :--- | :--- | :--- | :---: | :---: |
| 01 | Clasificador de descargas | Automatización | Python | [Ver](projects/day-01-download-sorter) | Pendiente |
| 02 | Renombrador masivo | Automatización | Python | [Ver](projects/day-02-bulk-file-renamer) | Pendiente |
| 03 | Conversor JSON ↔ CSV | Datos | Python | [Ver](projects/day-03-json-csv-converter) | Pendiente |
| 04 | Analizador de logs | Monitorización | Python | [Ver](projects/day-04-log-analyzer) | Pendiente |
| 05 | Generador de índice Markdown | Utilidad | Python | [Ver](projects/day-05-markdown-toc) | Pendiente |
| 06 | Validador de políticas de contraseña | Seguridad | Python | [Ver](projects/day-06-password-policy-checker) | Pendiente |
| 07 | Backup local y Azure Blob | Cloud storage | Python, Azure SDK | [Ver](projects/day-07-backup-azure-blob) | Pendiente |
| 08 | Limpiador de datos CSV | Datos | Python | [Ver](projects/day-08-csv-data-cleaner) | [Demo local](projects/day-08-csv-data-cleaner/assets/DEMO_15S.md) |
| 09 | API de portfolio | API | FastAPI | [Ver](projects/day-09-portfolio-api) | Pendiente |
| 10 | API CRUD de tareas | API | FastAPI, Pydantic | [Ver](projects/day-10-task-api) | Pendiente |
| 11 | API de análisis de texto | API | FastAPI | [Ver](projects/day-11-text-analysis-api) | Pendiente |
| 12 | API de inspección de archivos | API | FastAPI, Azure Blob opcional | [Ver](projects/day-12-upload-inspector-api) | Pendiente |
| 13 | Generador de slugs | CLI | TypeScript | [Ver](projects/day-13-url-slug-generator) | Pendiente |
| 14 | Validador de configuración | Configuración | TypeScript, Zod | [Ver](projects/day-14-env-config-validator) | Pendiente |
| 15 | Divisor de gastos | Utilidad | TypeScript | [Ver](projects/day-15-expense-splitter) | Pendiente |
| 16 | Temporizador Pomodoro | Frontend | React, TypeScript | [Ver](projects/day-16-pomodoro-timer) | Pendiente |
| 17 | Rastreador de hábitos | Frontend | React, IndexedDB, Redis opcional | [Ver](projects/day-17-habit-tracker) | Pendiente |
| 18 | Buscador de notas | Frontend | React, IndexedDB | [Ver](projects/day-18-notes-search) | Pendiente |
| 19 | Kanban mínimo | Frontend | React, TypeScript | [Ver](projects/day-19-kanban-mini) | Pendiente |
| 20 | Constructor de formularios | Frontend | React, Zod | [Ver](projects/day-20-form-builder) | Pendiente |
| 21 | Dashboard de métricas | Frontend | Next.js, Tailwind CSS | [Ver](projects/day-21-dashboard-metrics) | Pendiente |
| 22 | Playground de cliente API | Frontend | Next.js, SWR | [Ver](projects/day-22-api-client-playground) | Pendiente |
| 23 | Asistente de chat IA | IA | React, Foundry/OpenAI opcional | [Ver](projects/day-23-ai-chat-assistant) | Pendiente |
| 24 | Laboratorio de plantillas de prompt | IA | React, Zod, Foundry/OpenAI opcional | [Ver](projects/day-24-prompt-template-lab) | Pendiente |
| 25 | Fragmentador de documentos | IA / Datos | Python | [Ver](projects/day-25-document-chunker) | Pendiente |
| 26 | Recuperador por palabras clave | IA / Búsqueda | Python, Azure AI Search opcional | [Ver](projects/day-26-keyword-retriever) | Pendiente |
| 27 | Flujo de agentes | IA / Agentes | Python, Foundry/AutoGen opcional | [Ver](projects/day-27-agent-workflow) | Pendiente |
| 28 | Validador de datasets de evaluación | IA / Calidad | Python, Pydantic | [Ver](projects/day-28-evaluation-dataset-validator) | Pendiente |
| 29 | Dashboard de salud full-stack | Full stack | FastAPI, React | [Ver](projects/day-29-fullstack-health-dashboard) | Pendiente |
| 30 | Catálogo de proyectos | Portfolio | Next.js, Tailwind CSS | [Ver](projects/day-30-project-catalog) | Pendiente |

## 📁 Estructura de cada proyecto

```text
projects/day-XX-nombre/
├── src/                 # Código ejecutable
├── tests/               # Pruebas o verificaciones reproducibles
├── data/                # Fixtures y datos de muestra
├── assets/              # GIF/vídeo y recursos de demo
├── README.md            # Instalación, uso, integración y fallback
├── .env.example         # Solo si existen variables opcionales
└── requirements.txt | package.json
```

Las plantillas reutilizables están en [`projects/_templates`](projects/_templates): Python CLI, FastAPI y React/Next.js.

## 📣 Publicación

La plantilla de LinkedIn está disponible en [`docs/LINKEDIN_TEMPLATE.md`](docs/LINKEDIN_TEMPLATE.md). Cada post incluye problema, decisión técnica, fallback si aplica, demo funcional y enlace directo al código.

## 📄 Licencia

Distribuido bajo la licencia MIT. Consulta [`LICENSE`](LICENSE).
