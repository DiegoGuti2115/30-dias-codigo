# Decisiones de implementación

- La herramienta es una CLI local; no incorpora interfaz web, API ni integraciones externas.
- Los subcomandos son `json-to-csv` y `csv-to-json`.
- Las columnas de JSON a CSV siguen el orden de la primera aparición de cada clave.
- Las claves ausentes en un registro JSON se emiten como celdas vacías.
- Los valores `null`, `true` y `false` se representan respectivamente como vacío, `true` y `false` en CSV.
- CSV a JSON conserva todos los valores como texto. No hay inferencia de números, booleanos, fechas ni nulos.
- La escritura usa un archivo temporal en el directorio destino y lo reemplaza al terminar correctamente.
- La sobrescritura requiere `--overwrite`; las rutas de entrada nunca se modifican.
