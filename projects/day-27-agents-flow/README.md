# Día 27 — Flujo de agentes

> Microproyecto del reto **30 Días, 30 Proyectos**. Identificador y ruta canónicos: `projects/day-27-agents-flow`.

## Propósito

Diseñar una CLI de Python que transforme una solicitud textual en un resultado editorial trazable mediante tres roles coordinados: investigación, redacción y revisión. El proyecto demuestra cómo un orquestador controla el orden de los agentes, conserva sus artefactos intermedios y decide si el borrador está aprobado o requiere corrección.

El flujo local será la ruta principal de la entrega. Microsoft Foundry y AutoGen son integraciones opcionales posteriores; no serán necesarios para instalar, ejecutar, probar ni demostrar el MVP.

## Objetivos

- Recibir una solicitud no vacía como entrada de la CLI.
- Ejecutar de manera secuencial los agentes `researcher`, `writer` y `reviewer`.
- Intercambiar contratos estructurados entre roles en lugar de texto implícito.
- Devolver un resultado JSON con la solicitud, los hallazgos, el borrador, la revisión y una decisión final.
- Mantener el flujo determinista y reproducible en modo local.
- Aislar futuros proveedores LLM para que no alteren el contrato del orquestador.

## Alcance del MVP

### Incluye

- Una CLI local de Python 3.11+ con una solicitud textual.
- Validación de entrada y salida JSON UTF-8.
- Un agente investigador que derive hallazgos estructurados de la solicitud.
- Un agente redactor que construya un borrador a partir de esos hallazgos.
- Un agente revisor que evalúe criterios explícitos y emita `approved` o `changes_requested`.
- Un orquestador que aplique la secuencia, propague artefactos y conserve trazabilidad.
- Fixtures locales y pruebas sin red ni credenciales.

### Fuera de alcance

- Ejecución paralela, conversaciones abiertas entre agentes, memoria persistente o reintentos autónomos.
- Recuperación web, conectores de documentos, bases de datos, autenticación o interfaz gráfica.
- Uso obligatorio de LLM, credenciales cloud, modelos hospedados o despliegue de agentes.
- Generación de contenido profesional garantizado, verificación factual externa o moderación avanzada.
- Iteración automática tras una decisión de `changes_requested`; el MVP informa la revisión, pero no vuelve a redactar.

## Funcionalidades previstas

| Prioridad | Funcionalidad | Resultado observable |
| --- | --- | --- |
| P0 | Validación de solicitud | Mensajes de error estables para texto ausente o vacío. |
| P0 | Orquestación secuencial | Los roles se ejecutan siempre en el orden investigación → redacción → revisión. |
| P0 | Contratos de artefactos | Hallazgos, borrador y revisión tienen campos documentados y serializables. |
| P0 | Revisión explícita | La decisión final identifica aprobación o cambios requeridos y sus motivos. |
| P0 | Salida JSON trazable | La respuesta conserva entradas y salidas de cada etapa. |
| P0 | Modo local | Ejecución y pruebas sin red, claves ni proveedor externo. |
| P1 | Adaptador LLM | Un proveedor Foundry u AutoGen puede sustituir roles locales tras validarse antes de T+30. |

## Arquitectura inicial

La arquitectura separa el dominio del flujo, la coordinación, los adaptadores de roles y la presentación CLI:

```text
solicitud
   │
   ▼
CLI / presentación ── valida y serializa JSON
   │
   ▼
orquestador ── controla secuencia, contexto y decisión final
   ├── investigador ── produce hallazgos estructurados
   ├── redactor ────── produce borrador desde hallazgos
   └── revisor ─────── produce decisión y observaciones
   │
   ▼
resultado trazable
```

La implementación se organiza en el paquete `src/agents_flow/`:

- `contracts.py`: tipos inmutables y validaciones de `Request`, `ResearchBrief`, `Draft`, `Review` y `WorkflowResult`.
- `errors.py`: errores de dominio con códigos públicos estables.
- `main.py`: punto de entrada de la CLI, ejecución del flujo y publicación de JSON UTF-8.
- `agents/local.py`: adaptadores locales deterministas de investigador, redactor y revisor.
- `agents/__init__.py`: exportaciones de los adaptadores de roles locales.
- `orchestrator.py`: caso de uso que coordina etapas, artefactos y errores de etapa.
- `presentation.py`: serializador estable del resultado agregado de la Fase 4.

La Fase 8 cierra la entrega con evidencia verificable y un recurso de publicación profesional. La evaluación opcional de la Fase 6 se descartó conforme a la puerta T+30 al no disponer de Azure Developer CLI (`azd`) para validar autenticación e invocación mínima de Microsoft Foundry. Los contratos y el serializador `serialize_contract` de la Fase 1 se preservan como API de compatibilidad, pero la ejecución principal ya realiza el flujo completo. No existen proveedores LLM ni llamadas externas.

## Flujo de trabajo de los agentes

1. La persona usuaria proporciona una solicitud, por ejemplo: `Explica los beneficios de pruebas automatizadas para una API pequeña`.
2. La CLI valida que el texto contiene caracteres distintos de espacios y crea un `Request`.
3. El investigador extrae el tema, objetivo, restricciones y una lista breve de hallazgos locales derivados de la solicitud; no realiza llamadas web.
4. El redactor recibe únicamente el `ResearchBrief` y crea un borrador con estructura explícita.
5. El revisor recibe el `Draft` y el `ResearchBrief`, evalúa cobertura, claridad y presencia de las restricciones y devuelve una decisión junto con observaciones.
6. El orquestador reúne los artefactos en `WorkflowResult` y la CLI lo emite como JSON.

Cada etapa recibe solo el contrato que necesita. La coordinación no depende de mensajes globales mutables ni de una conversación no estructurada.

### Contrato activo de la CLI — Fase 4

La CLI admite una única solicitud posicional `PROMPT` y la opción `--format json`. `PROMPT` debe ser una cadena con al menos un carácter distinto de espacio; su contenido se conserva sin normalizar. Los formatos distintos de `json` son rechazados por el analizador de argumentos.

Una ejecución correcta devuelve exclusivamente este JSON UTF-8 por salida estándar:

```json
{
  "format": "json",
  "phase": 3,
  "status": "completed",
  "request": { "prompt": "..." },
  "research_brief": {
    "topic": "...",
    "objective": "...",
    "constraints": ["..."],
    "findings": ["..."]
  },
  "draft": { "content": "..." },
  "review": { "decision": "approved", "observations": ["..."] },
  "decision": "approved"
}
```

Los errores de dominio, incluidos los de etapa como `research_stage_failed`, se escriben exclusivamente por salida de error estándar y el proceso termina con código `2`:

```json
{
  "error": {
    "code": "invalid_prompt",
    "message": "prompt must contain non-whitespace text"
  }
}
```

Los códigos de validación incluyen `invalid_prompt_type`, `invalid_prompt`, `invalid_phase`, `invalid_status`, `invalid_format` e `invalid_workflow_result`. La API `serialize_contract` conserva el documento `contract_only` de la Fase 1 para integraciones que todavía necesiten ese contrato; la CLI ya no lo emite.

### Agentes locales de la Fase 2

Los adaptadores de [`src/agents_flow/agents/local.py`](src/agents_flow/agents/local.py) están disponibles como `LocalResearcher`, `LocalWriter` y `LocalReviewer`. Operan exclusivamente sobre contratos inmutables y no leen archivos, variables de entorno, red, hora, memoria previa ni estado global.

- `LocalResearcher.research(Request)` deriva `topic`, `objective`, dos restricciones explícitas y dos hallazgos de la solicitud. Los hallazgos indican que son locales y no fuentes recuperadas.
- `LocalWriter.write(ResearchBrief)` genera un `Draft` que incorpora tema, objetivo, hallazgos y restricciones del resumen recibido.
- `LocalReviewer.review(ResearchBrief, Draft)` comprueba de forma literal la cobertura de tema, objetivo y restricciones. Devuelve `approved` con observaciones de trazabilidad, o `changes_requested` con una observación por cada elemento faltante. No vuelve a redactar.

`ResearchBrief`, `Draft` y `Review` validan sus campos semánticamente. Las decisiones permitidas son `approved` y `changes_requested`; esta última requiere al menos una observación.

### Orquestación y trazabilidad de la Fase 3

`WorkflowOrchestrator.run(Request)` ejecuta estrictamente `research` → `writing` → `review`. El redactor recibe el `ResearchBrief` generado y el revisor recibe ese resumen junto con el `Draft`; no acceden a una solicitud global mutable. Al completarse, `WorkflowResult` conserva `request`, `research_brief`, `draft` y `review`, con `phase: 3` y `status: "completed"`.

Los adaptadores se pueden inyectar en `WorkflowOrchestrator` para pruebas o evoluciones posteriores. Un `DomainError` o excepción inesperada de una etapa se transforma en `StageError`, con un código estable como `research_stage_failed`; el flujo se detiene y no ejecuta etapas posteriores.

### Presentación JSON de la Fase 4

`serialize_workflow(WorkflowResult)` en [`src/agents_flow/presentation.py`](src/agents_flow/presentation.py) transforma únicamente resultados completados de Fase 3 en valores JSON nativos: las tuplas de restricciones, hallazgos y observaciones se publican como listas. El documento conserva la decisión tanto dentro de `review` como en el campo de nivel superior `decision` para una automatización directa.

## Estructura de directorios

```text
projects/day-27-agents-flow/
├── README.md                    # Guía específica del proyecto
├── ROADMAP.md                   # Fases, entregables y criterios de cierre
├── pyproject.toml                # Paquete Python, distribución src/ y configuración de pytest
├── requirements.txt              # Única dependencia de prueba: pytest
├── src/
│   └── agents_flow/
│       ├── __init__.py           # Exportaciones públicas del paquete
│       ├── contracts.py          # Contratos inmutables y validaciones semánticas
│       ├── errors.py             # Errores de dominio
│       ├── main.py               # CLI y publicación JSON de la Fase 4
│       ├── orchestrator.py       # Coordinación determinista de la Fase 3
│       ├── presentation.py       # Serializador JSON del resultado agregado
│       ├── agents/
│       │   ├── __init__.py       # Exportaciones de adaptadores locales
│       │   └── local.py          # Investigador, redactor y revisor deterministas
│       └── .gitkeep              # Conservado como archivo base de Fase 0
├── tests/
│   ├── test_contracts.py         # Contratos, inmutabilidad y validaciones
│   ├── test_local_agents.py      # Adaptadores locales y determinismo
│   ├── test_main.py              # CLI, ayuda, salida y errores
│   ├── test_orchestrator.py      # Orden, trazabilidad y fallos de etapa
│   ├── test_demo_asset.py        # Recurso de demo y comando reproducible
│   ├── test_final_delivery_assets.py # Evidencia final y copy de LinkedIn
│   ├── test_phase_five_fixtures.py # Integración respaldada por fixtures locales
│   ├── test_presentation.py      # Serialización JSON y resultados válidos
│   └── .gitkeep                  # Conservado como archivo base de Fase 0
├── data/
│   ├── workflow_cases.json       # Escenarios aprobados, cambios y validación
│   └── .gitkeep                 # Archivo base conservado de la Fase 0
└── assets/
    ├── demo-15s.md              # Guion cronometrado y reproducción local
    ├── final-delivery.md        # Evidencia, alcance congelado y cierre verificable
    ├── linkedin-post.md         # Copy profesional basado en capacidades verificadas
    └── .gitkeep                 # Archivo base conservado de la Fase 0
```

Los archivos `.gitkeep` no tienen significado de ejecución. Se conservan los de `src/agents_flow/`, `tests/`, `data/` y `assets/` como archivos base de la Fase 0; `workflow_cases.json` aporta los escenarios reutilizables de la Fase 5, `assets/demo-15s.md` el guion reproducible de la Fase 7 y `assets/final-delivery.md` la evidencia de cierre de la Fase 8. El proyecto usa biblioteca estándar en tiempo de ejecución; no se crea `.env.example` porque no hay configuración ni integración externa.

## Requisitos

### Estado actual: Fase 8 — Verificación y entrega

- Python 3.11 o superior.
- `pytest` para ejecutar la suite de pruebas.
- Sin acceso a red, variables de entorno ni dependencias de ejecución adicionales.

Microsoft Foundry o AutoGen solo se incorporan como integración P1 si la autenticación y una invocación mínima se validan antes de T+30. En este entorno, la comprobación oficial detectó que falta `azd`; por tanto, la integración se descartó y no se creó `.env.example`, no se añadieron credenciales y no se incorporaron dependencias de proveedor. Una reevaluación futura deberá conservar el modo local y documentar únicamente configuración sin secretos.

## Instalación y uso

### Instalación

```text
python -m pip install -e .
python -m pip install pytest
```

### Ejecución actual de la CLI

```text
python -m agents_flow.main "Explica los beneficios de pruebas automatizadas para una API pequeña"
python -m agents_flow.main --help
```

El primer comando ejecuta investigación, redacción y revisión locales y publica todos los artefactos junto con la decisión final. La salida correcta usa únicamente stdout; errores de entrada o de una etapa usan únicamente stderr y código de proceso `2`.

### Demo reproducible de 15 segundos

El guion cronometrado está en [`assets/demo-15s.md`](assets/demo-15s.md). Tras instalar las dependencias, ejecute exactamente el comando del guion; la salida debe incluir `research_brief`, `draft`, `review` y `decision: "approved"`. El mismo caso `approved` vive en [`data/workflow_cases.json`](data/workflow_cases.json) y está cubierto por una prueba de regresión. La demo es local, no genera archivos y no requiere red, secretos ni proveedor LLM.

## Cierre verificable y publicación

La evidencia reproducible de la entrega está en [`assets/final-delivery.md`](assets/final-delivery.md). Incluye el alcance congelado, los comandos de verificación, los criterios de aceptación y los límites reales del MVP. El copy profesional para publicar el proyecto está en [`assets/linkedin-post.md`](assets/linkedin-post.md); solo comunica capacidades sustentadas por el código, los fixtures y las pruebas del repositorio.

## Integración opcional y fallback

- **Ruta principal:** roles locales deterministas que transforman la solicitud sin red ni secretos.
- **Evaluación de Fase 6:** la integración con Microsoft Foundry se descartó porque falta Azure Developer CLI (`azd`), impidiendo validar autenticación e invocación mínima dentro de la puerta T+30.
- **No incorporado:** no existe adaptador remoto, configuración `.env`, credencial, dependencia de proveedor ni llamada externa en esta entrega.
- **Fallback obligatorio:** los adaptadores locales mantienen los contratos de entrada y salida y continúan siendo la única ruta activa para CLI y pruebas.
- **Criterio para una reevaluación:** solo podrá añadirse un proveedor aislado tras validar autenticación e invocación mínima; un fallo deberá seguir dejando operativo el modo local sin modificar la CLI ni el orquestador.

## Estrategia de pruebas

Las pruebas en `tests/` priorizan comportamiento observable y determinismo. Los escenarios compartidos de `data/workflow_cases.json` fijan una solicitud aprobada, una revisión con cambios requeridos y una solicitud inválida, sin requerir red ni credenciales:

1. **Contratos y validación:** solicitud vacía, contratos inválidos, resultados agregados y errores de dominio con códigos estables en `tests/test_contracts.py`.
2. **Roles locales:** `tests/test_local_agents.py` verifica artefactos reproducibles, trazabilidad del borrador, aprobación y cambios requeridos sin red ni estado compartido.
3. **Orquestador:** `tests/test_orchestrator.py` verifica orden obligatorio, propagación de artefactos, determinismo y detención ante errores.
4. **CLI y presentación:** `tests/test_main.py` y `tests/test_presentation.py` comprueban JSON completo, UTF-8, salida de error separada, errores de etapa y compatibilidad del serializador legado.
5. **Fixtures e integración:** `tests/test_phase_five_fixtures.py` carga los escenarios de `data/workflow_cases.json` para comprobar aprobación de extremo a extremo, cambios requeridos, validación, UTF-8 y fallos controlados de escritura y revisión.
6. **Demo:** `tests/test_demo_asset.py` comprueba que el guion de 15 segundos conserva el comando local, los artefactos trazables, la decisión y la compatibilidad con el caso aprobado.
7. **Cierre:** `tests/test_final_delivery_assets.py` protege los comandos, valores observables y límites declarados en la evidencia final, además de las afirmaciones verificadas del copy de LinkedIn.
8. **Fallback:** pruebas de adaptadores simulados para confirmar que una indisponibilidad remota no afecta al modo local.

Ninguna prueba P0 depende de Foundry, AutoGen, red, cuota o credenciales.

## Criterios de aceptación del MVP

- Una solicitud válida ejecuta investigación, redacción y revisión en el orden documentado.
- El resultado JSON contiene artefactos identificables de cada rol y una decisión final.
- Las reglas del revisor y los límites del modo local son explícitos y verificables.
- Las entradas inválidas producen errores claros sin iniciar roles posteriores.
- La misma solicitud produce el mismo resultado local.
- La suite local se ejecuta sin red, credenciales ni proveedor externo.
- Un proveedor remoto opcional, si se implementa, no altera ni bloquea el fallback local.
- La guía final incluye instalación, uso, prueba, integración opcional, fallback y demo breve.

## Entrega completada

La Fase 8 está cerrada sin ampliar el alcance: la evidencia está versionada, los recursos enlazados son comprobables y el flujo principal permanece local, determinista y sin secretos. El historial de decisiones, prioridades y límites se conserva en [ROADMAP.md](ROADMAP.md). Las posibles mejoras posteriores siguen siendo opcionales y no forman parte de esta entrega.
