# Cierre verificable — Flujo de agentes

## Alcance congelado

Esta entrega cierra el MVP local descrito en [`README.md`](../README.md) y [`ROADMAP.md`](../ROADMAP.md). No añade proveedores, red, credenciales, memoria, reintentos automáticos ni nuevas rutas de ejecución.

La única ruta activa es la CLI local que coordina investigación, redacción y revisión de forma determinista. La evaluación opcional de Microsoft Foundry se descartó en la Fase 6 porque no se pudo validar `azd`, autenticación e invocación mínima dentro de la puerta T+30.

## Evidencia reproducible

Desde la raíz del proyecto, ejecutar:

```text
python -m pip install -e .
python -m pip install -r requirements.txt
python -m pytest -q
python -m compileall -q src
python -m agents_flow.main --help
python -m agents_flow.main "Explica la trazabilidad del café local."
git diff --check
```

La ejecución representativa debe emitir exclusivamente JSON UTF-8 en salida estándar con estos valores de nivel superior:

```json
{
  "format": "json",
  "phase": 3,
  "status": "completed",
  "decision": "approved"
}
```

El escenario coincide con `approved` de [`data/workflow_cases.json`](../data/workflow_cases.json) y con el guion de [`assets/demo-15s.md`](demo-15s.md). La salida completa conserva `request`, `research_brief`, `draft` y `review` para inspección trazable.

## Comprobaciones de aceptación

| Criterio | Evidencia versionada |
| --- | --- |
| Solicitud válida y respuesta JSON | [`src/agents_flow/main.py`](../src/agents_flow/main.py) y [`tests/test_main.py`](../tests/test_main.py) |
| Orden investigación → redacción → revisión | [`src/agents_flow/orchestrator.py`](../src/agents_flow/orchestrator.py) y [`tests/test_orchestrator.py`](../tests/test_orchestrator.py) |
| Roles locales deterministas | [`src/agents_flow/agents/local.py`](../src/agents_flow/agents/local.py) y [`tests/test_local_agents.py`](../tests/test_local_agents.py) |
| Fixtures de aprobación, cambios y entrada inválida | [`data/workflow_cases.json`](../data/workflow_cases.json) y [`tests/test_phase_five_fixtures.py`](../tests/test_phase_five_fixtures.py) |
| Demo breve reproducible | [`assets/demo-15s.md`](demo-15s.md) y [`tests/test_demo_asset.py`](../tests/test_demo_asset.py) |
| Sin secretos ni configuración remota | [`.gitignore`](../.gitignore), [`README.md`](../README.md) y ausencia deliberada de un archivo `.env.example` |

## Límites conocidos

- Los hallazgos se derivan solo de la solicitud; no son investigación factual ni incorporan fuentes externas.
- Una decisión `changes_requested` se informa, pero no inicia una nueva redacción automáticamente.
- No hay integración LLM activa, despliegue cloud, recuperación documental, persistencia ni paralelismo.
- La ausencia de `azd` descartó la integración opcional; el flujo local sigue siendo completo para la demo y las pruebas.

## Integridad de la entrega

La comprobación `git diff --check` detecta errores de espacio en las diferencias. Antes de publicar, se revisan archivos de configuración y documentación para confirmar que no contienen secretos. Las cachés de Python y de `pytest` son artefactos locales excluidos por [`.gitignore`](../.gitignore) y se eliminan tras la verificación.
