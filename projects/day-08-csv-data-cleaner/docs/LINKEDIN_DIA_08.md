# Texto de publicación verificable — Día 08/30

## Titular

> Día 08/30 — Construí un limpiador local de CSV con un plan explícito y salidas no destructivas.

## Cuerpo

Los CSV de trabajo suelen acumular espacios accidentales, marcadores faltantes, filas vacías o duplicados exactos. Corregirlos manualmente es repetitivo y deja poca trazabilidad.

Construí **Limpiador de datos CSV**, una CLI local en Python que recibe un CSV y un plan JSON v1. La decisión técnica principal fue usar únicamente la biblioteca estándar y un plan cerrado: así las cinco operaciones mecánicas son explícitas, ordenadas y medibles.

La herramienta publica un CSV limpio y un resumen JSON separado. Valida las rutas antes de procesar, nunca sobrescribe el origen y prepara ambas salidas mediante temporales propios. La suite compara los resultados con fixtures sintéticos de referencia y cubre errores de CLI y publicación.

Para respetar el alcance, dejé fuera autodetección de dialectos, inferencia de tipos, limpieza semántica, lotes, cloud y UI. La demo local usa fixtures, no necesita red ni credenciales, y muestra: entrada → plan → comando `clean` → CSV limpio y resumen.

## Cierre

- **Stack:** Python 3.11+, biblioteca estándar.
- **Código:** [`projects/day-08-csv-data-cleaner`](..).
- **Demo:** seguir [`assets/DEMO_15S.md`](../assets/DEMO_15S.md).

`#30Dias30Proyectos #BuildInPublic #Python #DataCleaning #CSV`
