### Nuevo Contenido para `ROADMAP.md`

```markdown
# 🗺️ Roadmap de Implementación: Day 24 (Local Pivot)

## Fase 1: Fundamentos y Estructura (0-30 min)
- [x] Inicializar proyecto React con TypeScript.
- [x] Crear la estructura de directorios alineada a estándares ML (`src/config`, `src/services`, `src/schemas`, `data/`, `tests/`).
- [x] Instalar dependencias (`zod`, `lucide-react`).

## Fase 2: Motor de Renderizado y Contratos (30-60 min)
- [x] Codificar `src/schemas/promptSchema.ts`: Configurar Zod para parsear plantillas y extraer requerimientos de variables (ej. regex para `{{token}}`).
- [x] Crear `src/services/promptRenderer.ts`: Lógica de inyección pura para fusionar la plantilla con el payload de variables.

## Fase 3: Integración LLM Local y Pipeline de Fallback (60-100 min)
- [x] Configurar `data/fallback_responses.json` con respuestas pre-calculadas por categoría de prompt.
- [x] Desarrollar `src/services/llmProvider.ts`:
    - Implementar un cliente `fetch` que apunte al endpoint local (`http://localhost:11434/api/generate`).
    - Implementar un patrón *Circuit Breaker*: si la API local rechaza la conexión o supera un timeout de 3 segundos, hacer *fallback* transparente al JSON.

## Fase 4: Interfaz de Usuario Reactiva (100-150 min)
- [x] Construir `PromptEditor.tsx` para la redacción del sistema y usuario.
- [x] Construir `VariablesForm.tsx` (formulario mutante basado en las variables detectadas por el esquema Zod).
- [x] Ensamblar en `App.tsx`, añadiendo un *toggle* visual en la UI para forzar el modo "Mock" frente a "Inferencia Local".

## Fase 5: Pruebas y Cierre Diario (150-180 min)
- [x] Escribir tests en `/tests` para asegurar que el validador Zod rechaza payloads incompletos.
- [x] Grabar el `DEMO_15S.md` demostrando el renderizado exitoso tanto con inferencia real como con mock.
- [x] Realizar commit y push final al repositorio.