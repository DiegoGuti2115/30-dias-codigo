# Día 29 — Dashboard de salud full-stack

Aplicación web personal del Día 29 del reto [30 Días, 30 Proyectos](../../README.md). El proyecto proporciona una base full-stack para registrar, consultar y visualizar métricas de bienestar introducidas manualmente o cargadas desde datos sintéticos, con una separación clara entre interfaz, API y contratos.

> **Estado:** las Fases 1 a 5 y los controles básicos de la Fase 8 están completados: el dashboard filtra y resume métricas sintéticas, presenta series y tablas accesibles, permite registrar mediciones manuales durante la sesión local y ejecuta controles reproducibles de calidad, secretos y dependencias. No hay persistencia durable ni autenticación.
>
> **Aviso importante:** esta aplicación no es un producto sanitario, no diagnostica, no prescribe, no ofrece recomendaciones médicas y no sustituye a profesionales de la salud. Cualquier ampliación clínica requerirá validación profesional, legal y regulatoria independiente antes de su uso.

## Propósito

Centralizar métricas personales de salud y bienestar en un dashboard privado, comprensible y accesible. La primera entrega demostrará el flujo técnico completo con datos de muestra reproducibles, sin depender de servicios externos ni de información sanitaria real.

## Usuarios objetivo

- Personas que desean explorar visualmente métricas personales registradas de forma manual.
- Desarrolladores que necesitan una referencia acotada de integración entre [FastAPI](backend/src/main.py) y [Next.js](frontend/src/app/page.tsx).
- Revisores del reto que requieren una demo local reproducible sin credenciales externas.

## Alcance

### MVP planificado

- Dashboard personal con métricas de muestra y entradas manuales claramente etiquetadas.
- API HTTP versionada para consultar el estado de la aplicación y los contratos previstos.
- Visualización responsive de resúmenes, tendencias no clínicas y estados vacíos, de carga o error, con alternativa tabular.
- Preparación estructural para cuentas, perfiles y persistencia, sin implementar autenticación ni acceso a una base de datos.
- Fixtures locales sintéticos como fuente de datos y fallback obligatorio.
- Validación de contratos en los límites de frontend y backend.

### Fuera de alcance del MVP

- Diagnósticos, triaje, prescripciones, recomendaciones terapéuticas, alertas clínicas o cálculos clínicos.
- Interpretación médica automatizada o decisiones que afecten a la salud de una persona.
- Conexión obligatoria a wearables, historiales clínicos, aseguradoras o proveedores sanitarios.
- Uso de datos de salud reales, almacenamiento de secretos o despliegue productivo.
- Autenticación, autorización, recuperación de cuenta y persistencia de perfiles reales.

### Evolución prevista

Las mejoras posteriores podrán añadir autenticación, perfiles, almacenamiento persistente, importación consentida e integraciones opcionales. Toda integración externa deberá conservar un fixture o mock local funcional, conforme a la política del repositorio. Las funcionalidades con impacto clínico solo podrán considerarse después de una evaluación explícita de profesionales cualificados, privacidad, seguridad y normativa aplicable.

## Arquitectura general

El repositorio se organiza como un monorepo ligero. El frontend consume contratos HTTP del backend; durante el desarrollo inicial puede cargar fixtures sintéticos locales. Los contratos compartidos se describen en documentación y se mantendrán alineados con los modelos de la API.

```text
Navegador
  └─ frontend/  Next.js + React + TypeScript + Tailwind CSS
       ├─ componentes y vistas
       ├─ cliente HTTP tipado y validación de contrato
       └─ fixture sintético de fallback
                 │ HTTP / JSON
                 ▼
     backend/   FastAPI + Pydantic + Python 3.11+
       ├─ rutas versionadas
       ├─ modelos y servicios de dominio
       └─ preparación para repositorios de persistencia
                 │
                 └─ base de datos futura (no implementada)

shared/         contratos, esquemas y convenciones compartidas
```

La arquitectura separa la presentación, el acceso a datos, los contratos y el dominio para mantener testeables las reglas futuras y reducir el acoplamiento con proveedores.

## Tecnologías y decisiones adoptadas

| Área | Tecnología o decisión | Estado |
|---|---|---|
| Frontend | Next.js, React y TypeScript | Shell responsive, accesible y conectado a la API local |
| Estilos | Tailwind CSS y CSS global | Diseño responsive con foco visible y tabla alternativa textual |
| Validación cliente | Adaptador TypeScript sin dependencias adicionales | Valida el contrato `v1` antes de presentar datos |
| Backend | FastAPI y Pydantic | API local `v1` con fixture validado y CORS restringido |
| Runtime backend | Python 3.11 o superior | Definido por el repositorio |
| Pruebas backend | pytest y cliente HTTP de FastAPI | Rutas, repositorio y recorrido `POST` seguido de `GET` cubiertos |
| Pruebas frontend | Vitest | Contrato, cliente, fallback, cálculos, filtros y regresiones de accesibilidad cubiertos |
| Seguridad de desarrollo | Escáner local de secretos y auditoría npm de dependencias de ejecución | Integrados en la verificación de calidad |
| Datos iniciales | JSON sintético local | Decisión adoptada; fallback obligatorio |
| Persistencia y autenticación | Interfaces y variables de entorno, sin proveedor ni dependencia | Pospuesto para no anticipar decisiones |

No se añade Redis, base de datos, proveedor de identidad ni servicio cloud en esta fase. Su selección requerirá una necesidad implementada, evaluación de seguridad y un fallback local.

## Requisitos previos

- Node.js 20 o superior y npm.
- Python 3.11 o superior.
- Un navegador moderno con JavaScript habilitado.
- Git, si se va a clonar o contribuir al repositorio.

## Instalación

Desde la raíz del proyecto:

```bash
copy .env.example .env
copy frontend\.env.example frontend\.env.local
copy backend\.env.example backend\.env

cd frontend && npm install
cd ..\backend && python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En PowerShell, sustituye la activación por `./.venv/Scripts/Activate.ps1` cuando corresponda. No copies secretos reales a ningún archivo versionado.

## Ejecución local

Abre dos terminales desde la raíz del proyecto.

```bash
cd backend
.venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

```bash
cd frontend
npm run dev
```

La interfaz estará disponible en `http://localhost:3000` y la documentación interactiva de la API en `http://localhost:8000/docs` cuando se ejecute el backend. La API local expone `GET /health`, `GET /api/v1/dashboard` y `POST /api/v1/measurements`; sirve exclusivamente el fixture sintético y las mediciones manuales se conservan solo mientras el proceso permanece activo. La vista permite filtrar el historial, consultar una serie cronológica junto con su tabla equivalente y registrar valores de demostración, sin establecer umbrales ni recomendaciones. Consulta [docs/API_CONTRACT.md](docs/API_CONTRACT.md) antes de integrar un consumidor.

## Variables de entorno

Los archivos de ejemplo no contienen secretos y son la única fuente permitida para documentar configuración.

| Archivo | Variable | Propósito | Obligatoria |
|---|---|---|:---:|
| [.env.example](.env.example) | `HEALTH_DASHBOARD_ENV` | Entorno lógico de ejecución | No |
| [frontend/.env.example](frontend/.env.example) | `NEXT_PUBLIC_API_BASE_URL` | URL base pública de la API local | No |
| [backend/.env.example](backend/.env.example) | `APP_ENV` | Entorno de la API | No |
| [backend/.env.example](backend/.env.example) | `CORS_ORIGINS` | Orígenes permitidos durante desarrollo | No |
| [backend/.env.example](backend/.env.example) | `DATABASE_URL` | Reserva para persistencia futura; no se usa aún | No |
| [backend/.env.example](backend/.env.example) | `AUTH_PROVIDER` | Reserva para autenticación futura; no se usa aún | No |

Los valores que empiezan por `NEXT_PUBLIC_` se exponen al navegador: nunca deben incluir claves, tokens ni información personal. Los archivos locales de entorno están excluidos por [.gitignore](.gitignore).

## Estructura del proyecto

```text
day-29-full-stack-health-dashboard/
├── README.md
├── ROADMAP.md
├── .env.example
├── .gitignore
├── frontend/
│   ├── .env.example
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── postcss.config.mjs
│   ├── tailwind.config.ts
│   ├── src/app/                 # Rutas, layout y estilos de Next.js
│   ├── src/components/          # Componentes de interfaz
│   ├── src/lib/                 # Cliente API, validación y utilidades
│   └── tests/                   # Pruebas de UI
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── src/main.py              # Aplicación FastAPI y health check técnico
│   ├── src/api/                 # Rutas HTTP versionadas
│   ├── src/core/                # Configuración y seguridad transversal
│   ├── src/domain/              # Modelos y reglas futuras
│   ├── src/repositories/        # Puertos de persistencia futuros
│   └── tests/                   # Pruebas de API
├── shared/
│   ├── contracts/               # Contratos JSON y notas de sincronización
│   └── types/                   # Tipos TypeScript compartidos previstos
├── data/fixtures/               # Datos sintéticos; nunca datos personales
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SECURITY_AND_PRIVACY.md
│   └── API_CONTRACT.md
├── tests/                       # Pruebas de integración y criterios comunes
├── scripts/                     # Automatizaciones reproducibles
├── assets/                      # Recursos estáticos de demo
└── infra/                       # Plantillas de despliegue y configuración futura
```

## Seguridad y privacidad de datos de salud

El tratamiento de datos de salud implica categorías especialmente sensibles. Aunque esta fase usa exclusivamente fixtures sintéticos, las fases posteriores deben cumplir como mínimo con los criterios detallados en [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md):

- Minimización de datos, propósito explícito y consentimiento informado antes de recopilar información real.
- Privacidad desde el diseño: retención limitada, separación de identificadores, exportación y borrado verificables.
- Cifrado en tránsito mediante HTTPS y cifrado de datos en reposo cuando exista persistencia.
- Autenticación robusta, autorización por recurso, principio de mínimo privilegio y registro de auditoría sin datos sensibles.
- Validación de entradas, control de tasa, gestión segura de sesiones y secretos fuera del repositorio.
- Evaluación legal y regulatoria aplicable —incluido RGPD cuando proceda— antes de procesar datos reales.
- Prohibición de incluir datos identificables, historiales reales, tokens o capturas sensibles en fixtures, pruebas, logs, issues o demos.

## Estrategia de pruebas

La calidad se construye por capas:

1. **Backend:** pruebas unitarias de modelos y servicios, y pruebas de rutas mediante cliente HTTP.
2. **Frontend:** pruebas de componentes, validación de contratos y estados de carga, vacío y error.
3. **Integración:** comprobación del contrato entre frontend, API y fixtures locales.
4. **Seguridad:** análisis estático, revisión de configuración, comprobación de secretos y pruebas de autorización cuando exista autenticación.
5. **Accesibilidad:** navegación por teclado, foco visible, contraste, etiquetas semánticas y alternativa textual para gráficos.
6. **Regresión:** ejecución de lint, chequeo de tipos, pruebas y build en cada cambio relevante.

Comandos de calidad:

```bat
scripts\verify-local.cmd
scripts\verify-quality.cmd
```

El segundo comando ejecuta la validación JSON, compilación y pruebas Python, escaneo local de secretos, ESLint, comprobación de tipos TypeScript, Vitest, build de Next.js y auditoría de dependencias de ejecución. La checklist manual de accesibilidad y seguridad está en [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md); la guía detallada de instalación, ejecución local y contribución está en [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Convenciones de desarrollo

- Idioma de documentación y mensajes de interfaz: español; identificadores de código: inglés claro y consistente.
- TypeScript en modo estricto; componentes pequeños, tipados y sin lógica de dominio acoplada a la presentación.
- Python con anotaciones de tipo, modelos Pydantic en los límites de la API y dependencias explícitas.
- Rutas de API con versión, por ejemplo `/api/v1`; el cliente frontend usa únicamente contratos HTTP y nunca módulos internos del backend.
- Datos de prueba deterministas, sintéticos y pequeños; cada integración externa conserva un fallback local.
- Formato y calidad mediante ESLint/TypeScript en frontend y herramientas Python configuradas en backend antes de cada entrega.
- Commits pequeños y descriptivos con alcance, por ejemplo `docs: define health dashboard architecture`.

## Guía para contribuir

1. Revisa [ROADMAP.md](ROADMAP.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) y [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md).
2. Crea una rama con un cambio acotado y evita mezclar refactorizaciones no relacionadas.
3. No incluyas secretos, información personal ni datos de salud reales.
4. Mantén los contratos y sus consumidores sincronizados; documenta cambios incompatibles.
5. Ejecuta los comandos de calidad aplicables antes de abrir una contribución.
6. Explica el alcance, las pruebas realizadas, el fallback local y cualquier impacto de seguridad o privacidad.
7. Solicita revisión técnica y, para cualquier capacidad sanitaria, validación profesional y normativa antes de promocionarla.

## Documentación relacionada

- [ROADMAP.md](ROADMAP.md): fases, MVP y mejoras posteriores.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): límites y decisiones técnicas iniciales.
- [docs/API_CONTRACT.md](docs/API_CONTRACT.md): contrato HTTP inicial y evolución prevista.
- [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md): controles y restricciones de datos sensibles.
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): instalación, ejecución local y verificaciones reproducibles.

## Licencia

Este proyecto forma parte del repositorio distribuido bajo licencia MIT. Consulta [LICENSE](../../LICENSE).
