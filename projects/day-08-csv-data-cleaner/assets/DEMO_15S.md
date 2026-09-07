# Demo local de 15 segundos — Día 08

## Propósito

Mostrar el flujo real y verificable de la v1 sin red, secretos ni datos personales:

```text
CSV sintético + plan explícito → clean → CSV limpio + resumen JSON
```

## Preparación

Desde [`projects/day-08-csv-data-cleaner`](..), con Python 3.11+ y una terminal visible:

```text
mkdir demo-tmp
```

Usa exclusivamente [`data/fixtures/happy-input.csv`](../data/fixtures/happy-input.csv) y [`data/fixtures/plan-all-operations.json`](../data/fixtures/plan-all-operations.json). No muestres rutas personales, credenciales ni otros archivos.

## Guion cronometrado

| Tiempo | Acción visible | Mensaje |
|---:|---|---|
| 0–3 s | Abrir `happy-input.csv` y `plan-all-operations.json`. | «CSV sintético y plan JSON explícito.» |
| 3–7 s | Ejecutar el comando. | «La CLI valida, limpia y publica sin tocar el origen.» |
| 7–11 s | Mostrar `demo-tmp/happy-cleaned.csv`. | «El CSV limpio es una salida nueva.» |
| 11–15 s | Mostrar `demo-tmp/happy-summary.json`. | «El resumen registra solo estructura y contadores.» |

Comando de la demo:

```text
python src/main.py clean data/fixtures/happy-input.csv data/fixtures/plan-all-operations.json demo-tmp/happy-cleaned.csv demo-tmp/happy-summary.json
```

La salida correcta devuelve `0`, escribe las dos rutas finales en stdout y no muestra valores de celdas en el diagnóstico.

## Cierre y limpieza

Al terminar la grabación, elimina exclusivamente el directorio creado para la demo:

```text
rmdir /s /q demo-tmp
```

No publiques la demo si el comando no devuelve `0` o si se muestra contenido distinto de los fixtures sintéticos aprobados.
