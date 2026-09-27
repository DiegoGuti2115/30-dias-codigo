# Roadmap — Flujo de agentes

## Objetivo del MVP

Entregar en un máximo de tres horas una CLI de Python 3.11+ que reciba una solicitud textual y coordine, de manera local y determinista, los roles de investigación, redacción y revisión. La respuesta deberá ser JSON trazable, conservar los artefactos intermedios y no requerir red, credenciales ni un proveedor LLM.

Microsoft Foundry y AutoGen son mejoras P1. Solo podrán añadirse si una configuración y una invocación mínima se validan antes de T+30; nunca sustituyen ni retrasan el flujo local.

## Principios de ejecución

- Se prioriza un único caso de uso: solicitud → investigación → redacción → revisión → resultado JSON.
- El orquestador conoce el orden de las etapas; los agentes solo conocen su contrato de entrada.
- Los artefactos intercambiados son estructuras validadas, no un estado global de conversación.
- El modo local debe ser determinista y suficiente para demo y pruebas.
- Las dependencias se introducen únicamente cuando sean necesarias para una fase P0.
- Se aplican las puertas del reto: integración remota fuera si no se valida antes de T+30; reducción de alcance a T+90; congelación a T+120.

## Fases priorizadas

| Fase | Prioridad | Objetivo | Entregables | Criterio de finalización |
| --- | --- | --- | --- | --- |
| 0. Planificación y estructura | P0 | Definir el alcance y preparar el espacio de trabajo sin comportamiento ejecutable. | `README.md`, `ROADMAP.md`, `src/agents_flow/.gitkeep`, `tests/.gitkeep`, `data/.gitkeep`, `assets/.gitkeep`. | La documentación describe exactamente los directorios existentes, la ruta canónica es `projects/day-27-agents-flow` y no hay código, dependencias ni credenciales. |
| 1. Contrato y base de la CLI | P0 | Congelar la interfaz mínima y el modelo de datos del flujo. | Manifiesto Python, paquete `agents_flow`, punto de entrada, contratos de solicitud, artefactos, resultado y errores. | La ayuda de CLI, los tipos y la documentación describen los mismos argumentos, campos, estados y códigos de salida; no hay red ni llamadas LLM. |
| 2. Agentes locales deterministas | P0 | Implementar cada rol con entradas y salidas independientes. | Adaptadores locales de investigador, redactor y revisor; reglas explícitas de investigación derivada, borrador y revisión. | Para la misma solicitud cada rol devuelve el mismo artefacto validado; ningún rol consulta internet, archivos externos o estado global. |
| 3. Orquestación y trazabilidad | P0 | Coordinar las tres etapas y conservar su contexto. | Caso de uso `orchestrator`, propagación de artefactos, resultado agregado y manejo de errores de etapa. | El orden investigación → redacción → revisión es verificable; una etapa fallida impide ejecutar las posteriores y el resultado exitoso conserva todos los artefactos. |
| 4. Presentación CLI y JSON | P0 | Exponer el flujo completo a una persona usuaria o automatización. | Serializador de respuesta, salida de errores, ejemplos de uso y códigos de proceso. | Un comando documentado produce JSON UTF-8 válido; las entradas inválidas informan un error claro sin emitir una respuesta de éxito. |
| 5. Fixtures y pruebas | P0 | Demostrar que el modo local cumple el contrato. | Fixtures en `data/`, pruebas de contratos, roles, orquestador, CLI y presentación. | La suite se ejecuta sin red ni credenciales y cubre solicitud vacía, orden de etapas, aprobación, cambios requeridos y errores. |
| 6. Integración LLM opcional | P1 | Evaluar adaptadores de Microsoft Foundry o AutoGen sin acoplar el núcleo. | Adaptador aislado, `.env.example` solo si aplica, pruebas simuladas y documentación de proveedor. | La autenticación y una invocación mínima se validan antes de T+30; el fallo del proveedor no modifica ni bloquea el modo local. Si no valida, la fase se descarta. |
| 7. Documentación y demo | P0 | Preparar una entrega reproducible y comunicable. | README final, guion o recurso de hasta 15 segundos en `assets/`, limitaciones y fallback actualizados. | Una persona puede instalar, ejecutar y verificar el flujo local desde una copia limpia, observando entrada, etapas y decisión final. |
| 8. Verificación y entrega | P0 | Cerrar sin ampliar alcance. | Ejecución de pruebas, revisión de secretos, verificación de formato, árbol final e índice global actualizado. | Se cumplen los criterios de aceptación, no hay secretos ni referencias rotas y el enlace raíz apunta a `projects/day-27-agents-flow`. |

## Estado de la fase 0

**Estado: completada.** La fase prepara exclusivamente el plan y los directorios que necesita la arquitectura; no implementa código funcional ni añade dependencias.

- [x] Definido el caso de uso de investigación, redacción y revisión en [README.md](README.md).
- [x] Documentados alcance, exclusiones, arquitectura, flujo, requisitos previstos, fallback y pruebas en [README.md](README.md).
- [x] Creado este roadmap con prioridades, entregables y criterios de finalización.
- [x] Reservados `src/agents_flow/`, `tests/`, `data/` y `assets/` mediante archivos `.gitkeep`.
- [x] Establecida `projects/day-27-agents-flow` como ruta canónica en el índice global.

**Pendiente y fuera de la fase 0:** adaptadores de agentes, fixtures, variables de entorno, integración Foundry/AutoGen y demo. Estos elementos pertenecen a las fases 2–8.

## Estado de la fase 1 — Contrato y base de la CLI

**Estado: completada.** Se ha congelado una interfaz mínima, los contratos públicos y una CLI funcional de validación. Esta fase no ejecuta agentes, no genera investigación, borrador o revisión, y no accede a red ni a proveedores LLM.

- [x] Creado [`pyproject.toml`](pyproject.toml) con distribución `src/`, requisito Python 3.11+ y configuración de `pytest`.
- [x] Creado [`requirements.txt`](requirements.txt) con `pytest>=8,<9` como única dependencia de prueba; la ejecución usa exclusivamente la biblioteca estándar.
- [x] Creado el paquete [`src/agents_flow/`](src/agents_flow/) con exportaciones públicas, contratos y errores de dominio.
- [x] Definidos los contratos inmutables `Request`, `ResearchBrief`, `Draft`, `Review` y `WorkflowResult` en [`src/agents_flow/contracts.py`](src/agents_flow/contracts.py). Los tres artefactos de roles se reservan para la Fase 2.
- [x] Fijada la CLI [`python -m agents_flow.main PROMPT`](src/agents_flow/main.py): acepta un `PROMPT` posicional no vacío y `--format json`; una entrada válida produce `phase: 1` y `status: "contract_only"`.
- [x] Fijados los errores de dominio JSON por salida de error estándar y el código de proceso `2` para las validaciones de la CLI.
- [x] Añadidas pruebas de contratos y CLI en [`tests/test_contracts.py`](tests/test_contracts.py) y [`tests/test_main.py`](tests/test_main.py).
- [x] Verificados instalación editable, suite de pruebas, compilación, importación y formato de diferencias sin llamadas de red ni a modelos.

**Pendiente y deliberadamente fuera de la fase 1:** validación semántica de `ResearchBrief`, `Draft` y `Review`; adaptadores de investigador, redactor y revisor; orquestación; resultado completo; fixtures; serialización final; variables de entorno; integración Foundry/AutoGen y demo. Estos elementos pertenecen a las fases 2–8.

## Estado de la fase 2 — Agentes locales deterministas

**Estado: completada.** Se han incorporado roles locales independientes para investigación, redacción y revisión. Cada rol recibe solamente su contrato de entrada, devuelve un artefacto inmutable validado y no accede a red, archivos externos, variables de entorno, reloj, aleatoriedad ni estado global. La CLI mantiene intencionadamente su contrato `contract_only` de la Fase 1 hasta que la Fase 3 añada el orquestador.

- [x] Añadidos `LocalResearcher`, `LocalWriter` y `LocalReviewer` en [`src/agents_flow/agents/local.py`](src/agents_flow/agents/local.py), con exportaciones en [`src/agents_flow/agents/__init__.py`](src/agents_flow/agents/__init__.py).
- [x] El investigador deriva tema, objetivo, restricciones y hallazgos declarados como locales desde `Request`, sin recuperación externa.
- [x] El redactor consume únicamente `ResearchBrief` y construye un `Draft` que conserva tema, objetivo, hallazgos y restricciones.
- [x] El revisor aplica reglas explícitas de cobertura literal para tema, objetivo y restricciones; devuelve `approved` o `changes_requested` con observaciones trazables, sin reiniciar la redacción.
- [x] Añadida validación semántica inmutable para `ResearchBrief`, `Draft` y `Review` en [`src/agents_flow/contracts.py`](src/agents_flow/contracts.py), incluidas las decisiones permitidas y las observaciones obligatorias cuando se solicitan cambios.
- [x] Añadidas pruebas reproducibles de determinismo, trazabilidad, aprobación, cambios requeridos e inválidos en [`tests/test_local_agents.py`](tests/test_local_agents.py).
- [x] Verificada la suite sin red ni credenciales después de incorporar los roles locales.

**Pendiente y fuera de la fase 2:** orquestación secuencial, propagación de errores de etapa, resultado agregado, conexión de los roles a la CLI, serialización final, fixtures, integración opcional y demo. Estos elementos corresponden a las fases 3–8.

## Estado de la fase 3 — Orquestación y trazabilidad

**Estado: completada.** El caso de uso local coordina los tres roles en memoria, conserva cada artefacto validado y detiene el flujo ante el primer fallo. La CLI mantiene el contrato `contract_only` de la Fase 1; la serialización pública del resultado agregado queda deliberadamente reservada para la Fase 4.

- [x] Creado [`src/agents_flow/orchestrator.py`](src/agents_flow/orchestrator.py) con `WorkflowOrchestrator` y puertos inyectables para investigador, redactor y revisor.
- [x] Fijado el orden verificable investigación → redacción → revisión y el paso exclusivo de `Request`, `ResearchBrief` y `Draft` entre las etapas correspondientes.
- [x] Extendidos los contratos para representar el resultado completado de la orquestación: `request`, `research_brief`, `draft`, `review`, `phase: 3` y `status: "completed"`, sin alterar el contrato heredado de Fase 1.
- [x] Añadido `StageError` para propagar fallos de etapa con códigos estables como `research_stage_failed`; las etapas posteriores no se ejecutan.
- [x] Exportado el orquestador y el error de etapa desde [`src/agents_flow/__init__.py`](src/agents_flow/__init__.py).
- [x] Añadidas pruebas de orden, propagación exacta de artefactos, determinismo, detención ante error y resultados agregados en [`tests/test_orchestrator.py`](tests/test_orchestrator.py) y [`tests/test_contracts.py`](tests/test_contracts.py).

**Pendiente y fuera de la fase 3:** serialización del resultado agregado, salida JSON completa por CLI, fixtures, integración opcional y demo. Estos elementos corresponden a las fases 4–8.

## Estado de la fase 4 — Presentación CLI y JSON

**Estado: completada.** La CLI ejecuta ahora el flujo local completo y publica un documento JSON UTF-8 trazable con todos los artefactos y la decisión final. Las validaciones y los fallos de etapa se informan exclusivamente por stderr con código de proceso `2`; no se imprime una respuesta de éxito cuando hay error.

- [x] Creado [`src/agents_flow/presentation.py`](src/agents_flow/presentation.py) con `serialize_workflow`, que convierte un `WorkflowResult` completado en valores JSON nativos y valida formato y estado.
- [x] Integrada la ejecución de `WorkflowOrchestrator` y el serializador de resultado agregado en [`src/agents_flow/main.py`](src/agents_flow/main.py), sin alterar los argumentos `PROMPT` y `--format json`.
- [x] La respuesta correcta contiene `format`, `phase`, `status`, solicitud, resumen de investigación, borrador, revisión y decisión final; las tuplas se serializan como listas.
- [x] Conservado `serialize_contract` como API compatible para el contrato `contract_only` de Fase 1, aunque la CLI principal ya emite el flujo completo.
- [x] Añadidas pruebas de serialización, resultado completo, errores de etapa, separación stdout/stderr y compatibilidad en [`tests/test_presentation.py`](tests/test_presentation.py) y [`tests/test_main.py`](tests/test_main.py).

**Pendiente y fuera de la fase 4:** fixtures reutilizables, ampliación de pruebas P0, integración opcional y demo. Estos elementos corresponden a las fases 5–8.

## Estado de la fase 5 — Fixtures y pruebas

**Estado: completada.** Se han añadido escenarios JSON locales y pruebas de integración que demuestran el contrato del modo determinista sin red, credenciales, proveedores ni estado compartido.

- [x] Creado [`data/workflow_cases.json`](data/workflow_cases.json) con una solicitud aprobada, un caso de cambios requeridos y una solicitud inválida, bajo UTF-8.
- [x] Añadido [`tests/test_phase_five_fixtures.py`](tests/test_phase_five_fixtures.py), que consume los escenarios para verificar el resultado trazable, la revisión `approved`, `changes_requested`, el error de solicitud vacía y la salida JSON UTF-8 de CLI.
- [x] Extendida la cobertura de errores de orquestación para fallos de escritura y revisión, comprobando sus códigos `writing_stage_failed` y `review_stage_failed`.
- [x] Mantenidas las pruebas existentes de contratos, roles, orquestación, presentación, CLI y compatibilidad heredada; la suite no realiza llamadas de red ni requiere credenciales.
- [x] Verificadas suite, compilación, ayuda y ejecución representativa de la CLI; se han limpiado las cachés de compilación.

**Pendiente y fuera de la fase 5:** integración LLM opcional, demo y cierre final. Estos elementos corresponden a las fases 6–8.

## Estado de la fase 6 — Integración LLM opcional

**Estado: descartada conforme a la puerta T+30.** Se evaluó una integración con Microsoft Foundry, pero el entorno no dispone de Azure Developer CLI (`azd`), requisito mínimo para iniciar la validación de autenticación y la invocación remota. Al no poder demostrar ambas condiciones sin introducir configuración, credenciales ni dependencias no verificadas, no se añade adaptador, `.env.example` ni dependencia de proveedor.

- [x] Evaluado el prerrequisito local de la ruta de Microsoft Foundry mediante su comprobación oficial de dependencias.
- [x] Confirmado que no se puede validar autenticación ni una invocación mínima en este entorno por ausencia de `azd`.
- [x] Descartada la integración opcional sin modificar contratos, orquestador, CLI, serialización, fixtures ni el modo local determinista.
- [x] Conservado el fallback local probado, sin red ni credenciales, como única ruta de ejecución del MVP.

**Pendiente y fuera de la fase 6:** demo y cierre final. Estos elementos corresponden a las fases 7–8.

## Estado de la fase 7 — Documentación y demo

**Estado: completada.** La entrega cuenta con documentación de instalación, ejecución, pruebas, fallback y limitaciones, junto con una demo local cronometrada, reproducible y sin servicios externos.

- [x] Creado [`assets/demo-15s.md`](assets/demo-15s.md) con un guion de 15 segundos que muestra solicitud, ejecución, artefactos y decisión final.
- [x] La demo usa el escenario `approved` de [`data/workflow_cases.json`](data/workflow_cases.json) y el comando público `python -m agents_flow.main`, sin duplicar ni alterar el flujo.
- [x] Añadido [`tests/test_demo_asset.py`](tests/test_demo_asset.py) para proteger el contenido esencial del recurso y verificar que su comando continúa produciendo una decisión `approved`.
- [x] Actualizado [`README.md`](README.md) con la reproducción desde copia limpia, ubicación de la demo, fallback local y limitaciones reales de la integración LLM descartada.
- [x] Conservado el funcionamiento íntegramente local, determinista y sin credenciales, red ni dependencias adicionales de ejecución.

**Pendiente y fuera de la fase 7:** verificación y entrega final, sin ampliar funcionalidades. Corresponde a la fase 8.

## Estado de la fase 8 — Verificación y entrega

**Estado: completada.** Se congeló el alcance del MVP, se materializó evidencia reproducible de entrega y se comprobó que la comunicación profesional describe únicamente capacidades verificables. No se añadieron funciones, proveedores ni configuraciones externas.

- [x] Creado [`assets/final-delivery.md`](assets/final-delivery.md) con comandos de reproducción, evidencia de criterios de aceptación, límites del MVP e integridad de la entrega.
- [x] Creado [`assets/linkedin-post.md`](assets/linkedin-post.md) con un copy profesional en español sustentado por las capacidades locales verificadas y una sección que evita afirmaciones no implementadas.
- [x] Añadido [`tests/test_final_delivery_assets.py`](tests/test_final_delivery_assets.py) para proteger los comandos, resultados observables y límites esenciales de los recursos de cierre.
- [x] Actualizado [`README.md`](README.md) para enlazar la evidencia de cierre y la publicación, describir el árbol final y declarar la Fase 8 como estado actual.
- [x] Preservados contratos, CLI, salida JSON UTF-8, modo local determinista y fallback sin red, credenciales o proveedor externo.
- [x] Revisada la entrega para evitar secretos, referencias rotas y errores de espacio en diferencias; las cachés locales permanecen excluidas mediante [`.gitignore`](.gitignore).

**Cierre final:** el MVP queda entregado con la integración LLM opcional descartada conforme a T+30. Las evoluciones posteriores enumeradas en este roadmap no forman parte de esta versión.

## Criterios de aceptación por flujo

### Solicitud y validación

- La solicitud debe contener texto distinto de espacios.
- Los errores de entrada se representan con códigos estables y una salida separada de la respuesta correcta.
- Ninguna etapa de agentes comienza si la solicitud es inválida.

### Investigación local

- El investigador identifica tema, objetivo y restricciones a partir de la solicitud.
- Los hallazgos se declaran como derivados de la entrada, no como datos recuperados externamente.
- La salida respeta un contrato estructurado y determinista.

### Redacción local

- El redactor consume un `ResearchBrief` válido, no la solicitud global mutable.
- El borrador conserva el tema y las restricciones que correspondan.
- El comportamiento no depende de red, hora, aleatoriedad ni memoria previa.

### Revisión local

- El revisor recibe el borrador y el resumen de investigación necesarios para evaluar cobertura y claridad.
- La decisión es `approved` o `changes_requested` y contiene observaciones trazables.
- El MVP informa la decisión y no reinicia automáticamente la redacción.

### Orquestación y salida

- El orquestador ejecuta los roles en el orden fijado.
- Un resultado exitoso serializa solicitud, investigación, borrador y revisión.
- Un fallo de etapa se propaga de forma controlada y evita las etapas siguientes.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Confundir hallazgos locales con investigación factual | Expectativas incorrectas sobre el resultado | Declarar en contrato y documentación que el investigador deriva artefactos de la solicitud y no consulta fuentes externas. |
| Acoplar roles a un proveedor LLM | El MVP depende de credenciales, red o cuota | Mantener contratos y adaptadores locales como ruta principal; encapsular todo proveedor en `agents/`. |
| Estado conversacional implícito | Resultados difíciles de probar | Pasar únicamente objetos de contrato entre etapas y devolverlos en el resultado. |
| Revisión poco verificable | Decisiones inconsistentes | Definir criterios de cobertura, claridad y restricciones antes de implementar el revisor. |
| Expansión hacia herramientas o memoria | Incumplimiento del límite diario | Posponer herramientas, recuperación, persistencia, paralelismo y bucles automáticos para una evolución posterior. |
| Fallo de Foundry, AutoGen, permisos o cuota | Bloqueo de demo | Aplicar la puerta T+30 y conservar el modo local sin red como fallback. |

## Orden sugerido dentro del límite diario

| Tiempo | Actividad | Resultado verificable |
| --- | --- | --- |
| 0:00–0:20 | Crear contrato, manifiesto y CLI mínima | Entradas y salida temporal documentadas. |
| 0:20–0:55 | Implementar contratos y agentes locales | Artefactos de cada rol reproducibles. |
| 0:55–1:25 | Implementar orquestador y respuesta agregada | Flujo local completo en memoria. |
| 1:25–1:45 | Conectar presentación CLI y errores | JSON ejecutable de extremo a extremo. |
| 1:45–2:10 | Evaluar proveedor opcional solo si aporta valor | Adaptador validado o fallback irreversible. |
| 2:10–2:35 | Añadir fixtures y pruebas | Suite local sin red. |
| 2:35–2:50 | Completar documentación y demo | Instrucciones y guion reproducibles. |
| 2:50–3:00 | Verificar, congelar alcance y preparar entrega | Sin referencias rotas ni secretos. |

## Definición de terminado específica

- El flujo local procesa una solicitud válida con los tres roles en el orden documentado.
- La respuesta JSON contiene artefactos de investigación, borrador, revisión y decisión final.
- Los contratos, reglas de revisión y errores se documentan y se comprueban con casos reproducibles.
- La ejecución principal y la suite P0 no requieren red, proveedor externo ni credenciales.
- Todo adaptador remoto opcional está aislado, documentado y tiene fallback local probado.
- [README.md](README.md) contiene instalación, uso, pruebas, integración opcional, fallback, limitaciones y demo final cuando proceda.
- `assets/` contiene un recurso breve que muestre solicitud, ejecución y resultado antes de la entrega.
- El índice raíz enlaza la ruta canónica `projects/day-27-agents-flow`.

## Evolución posterior al MVP

1. Añadir un bucle explícito y acotado de corrección cuando el revisor solicite cambios.
2. Incorporar recuperación de fuentes locales con citas, como proyecto o fase independiente.
3. Permitir adaptadores LLM adicionales bajo los mismos contratos de roles.
4. Añadir métricas de latencia, calidad y trazas sin convertirlas en requisito del flujo local.
5. Evaluar orquestación paralela solo para etapas que no compartan dependencias de datos.
