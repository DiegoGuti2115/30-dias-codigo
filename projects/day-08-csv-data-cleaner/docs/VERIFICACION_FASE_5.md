# Verificación de entrega — Fase 5

## Alcance verificado

La v1 implementa exclusivamente el flujo local contractual:

```text
python src/main.py clean <SOURCE_CSV> <PLAN_JSON> <OUTPUT_CSV> <SUMMARY_JSON>
```

[`src/main.py`](../src/main.py) coordina validación, carga, plan, limpieza y publicación. El núcleo permanece separado: [`src/csv_profile.py`](../src/csv_profile.py), [`src/plan.py`](../src/plan.py) y [`src/cleaner.py`](../src/cleaner.py) no publican archivos. [`src/output.py`](../src/output.py) concentra validación de rutas y publicación no destructiva.

No hay dependencias de terceros, red, credenciales, archivos de configuración, telemetría ni fallback externo: el modo local es el producto y la demo.

## Evidencia automatizada

Ejecutar desde [`projects/day-08-csv-data-cleaner`](..):

```text
python -m py_compile src/csv_profile.py src/plan.py src/cleaner.py src/output.py src/main.py
python -m unittest discover -s tests -v
```

La suite comprueba:

- lectura estricta CSV UTF-8/UTF-8 BOM, límites, encabezados, filas y dialecto de coma;
- esquema cerrado y orden fijo del plan JSON v1;
- las cinco operaciones, contadores, colisiones de encabezado y referencias deterministas;
- CLI de subproceso: éxito, ausencia de cambios, argumentos inválidos, entrada ausente, plan inválido y conflicto de rutas;
- preservación del origen y comparación de resultados con las referencias;
- publicación de dos artefactos y limpieza de resultado parcial y temporales propios tras un fallo inyectado;
- repetición determinista, límites, privacidad de stdout/stderr y ausencia de residuos generados por la suite de entrega.

## Comprobación manual reproducible

El flujo feliz, el caso válido sin cambios y un error de CLI se describen con comandos copiables en [`examples/USO.md`](../examples/USO.md). El resultado feliz se compara con [`data/expected/happy-cleaned.csv`](../data/expected/happy-cleaned.csv) y [`data/expected/happy-summary.json`](../data/expected/happy-summary.json); el origen se compara byte a byte antes y después.

La demostración de hasta 15 segundos está preparada en [`assets/DEMO_15S.md`](../assets/DEMO_15S.md). Usa solo los fixtures sintéticos aprobados, no precisa red ni secretos, y elimina su directorio temporal al finalizar.

## Revisión de seguridad y entrega

- Los fixtures y referencias son sintéticos y no contienen secretos ni datos personales.
- El resumen y los diagnósticos no imprimen filas, valores de celdas, planes completos, trazas ni rutas temporales.
- El resumen solo publica estructura y contadores; los encabezados inocuos son el único metadato textual del CSV.
- El origen, el plan y salidas existentes nunca se sobrescriben.
- Las salidas se preparan como temporales propios y se limpian cuando la publicación falla.
- [`README.md`](../README.md), [`docs/CONTRATO.md`](CONTRATO.md), [`examples/USO.md`](../examples/USO.md), las referencias y el material de demo describen el comportamiento implementado.
- La entrega no afirma atomicidad de dos archivos frente a fallos externos o concurrencia, ni soporte de capacidades excluidas por el contrato.

## Estado de entrega

La Fase 5 queda lista para cierre cuando las órdenes anteriores pasen desde una copia limpia, la demo manual se ejecute con los fixtures y se confirme que no quedan directorios `__pycache__`, archivos `.pyc`, temporales `.csv-cleaner-*` ni publicaciones de prueba dentro del proyecto.
