# Copy para LinkedIn — Día 27: Flujo de agentes

## Texto para publicar

Hoy cierro el Día 27 de mi reto **30 Días, 30 Proyectos**: un flujo de agentes local y determinista construido con Python.

El problema: coordinar investigación, redacción y revisión sin convertir el sistema en una conversación opaca ni depender de red, credenciales o un proveedor LLM.

La decisión técnica fue separar cada etapa mediante contratos inmutables y dejar que un orquestador controle el orden del flujo:

`solicitud → investigación → redacción → revisión → JSON trazable`

Cada ejecución conserva la solicitud, el resumen de investigación, el borrador, la revisión y la decisión final (`approved` o `changes_requested`). La CLI produce JSON UTF-8 y comunica los errores de forma estable por stderr.

También prioricé la reproducibilidad: el proyecto incluye fixtures, pruebas de contratos, roles, orquestación, CLI y una demo local de 15 segundos. Todo funciona sin red, secretos ni servicios externos.

La integración opcional con Microsoft Foundry se evaluó, pero se descartó al no poder validar autenticación e invocación mínima dentro de la ventana prevista. En lugar de introducir una dependencia frágil, mantuve el fallback local como ruta única, verificable y lista para demo.

🔗 Código y guía: `projects/day-27-agents-flow`
🎬 Demo reproducible: `assets/demo-15s.md`
✅ Evidencia de cierre: `assets/final-delivery.md`

#Python #AIEngineering #AgentesIA #SoftwareEngineering #Testing #CLI #30Dias30Proyectos

## Capacidades verificadas que sustenta este texto

- CLI local con una solicitud textual y respuesta JSON UTF-8.
- Orquestación secuencial de investigación, redacción y revisión.
- Contratos inmutables, artefactos trazables y errores de dominio estables.
- Decisiones `approved` y `changes_requested` basadas en reglas locales explícitas.
- Fixtures y pruebas automatizadas sin red ni credenciales.
- Demo local versionada de 15 segundos.

No afirmar: investigación factual externa, uso actual de un LLM, Microsoft Foundry activo, citas de fuentes, reintentos automáticos, memoria persistente o despliegue cloud.
