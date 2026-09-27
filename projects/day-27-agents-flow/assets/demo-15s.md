# Demo local — 15 segundos

## Objetivo

Mostrar una ejecución completa y reproducible del flujo local: solicitud, investigación, redacción, revisión y decisión final. No requiere red, credenciales, proveedor LLM ni variables de entorno.

## Guion cronometrado

| Tiempo | Acción o narración | Evidencia visible |
| --- | --- | --- |
| 0–3 s | «Introduzco una solicitud en la CLI local.» | `python -m agents_flow.main "Explica la trazabilidad del café local."` |
| 3–8 s | «El orquestador ejecuta investigación, redacción y revisión en ese orden.» | JSON con `research_brief`, `draft` y `review`. |
| 8–12 s | «Los artefactos se conservan para poder inspeccionar la trazabilidad.» | `request.prompt`, hallazgos, contenido y observaciones. |
| 12–15 s | «La decisión final queda lista para automatización.» | `"decision": "approved"`. |

## Resultado esperado

El comando emite exclusivamente un documento JSON UTF-8 por salida estándar. Debe contener `phase: 3`, `status: "completed"` y `decision: "approved"`. Para un error de entrada, por ejemplo una solicitud compuesta solo por espacios, no se produce salida correcta: se escribe el JSON de error por salida de error estándar y el proceso termina con código `2`.

## Reproducción desde una copia limpia

```text
python -m pip install -e .
python -m pip install -r requirements.txt
python -m agents_flow.main "Explica la trazabilidad del café local."
```

El escenario de la demo coincide con el caso `approved` de `data/workflow_cases.json`, usado por las pruebas locales. La demo no genera archivos ni modifica el repositorio.
