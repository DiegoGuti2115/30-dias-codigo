# Escenarios de uso

Los siguientes comandos se ejecutan desde la raíz del repositorio.

## JSON a CSV

Convierte el fixture [`people.json`](../data/fixtures/people.json) a un archivo temporal elegido por la persona usuaria:

```powershell
python projects/day-03-json-csv-converter/src/main.py json-to-csv "projects/day-03-json-csv-converter/data/fixtures/people.json" "<ruta-de-salida>\people.csv"
```

## CSV a JSON

Convierte el fixture [`catalog.csv`](../data/fixtures/catalog.csv) a un archivo JSON:

```powershell
python projects/day-03-json-csv-converter/src/main.py csv-to-json "projects/day-03-json-csv-converter/data/fixtures/catalog.csv" "<ruta-de-salida>\catalog.json"
```

Si el destino existe, añada `--overwrite` únicamente después de revisar la ruta.
