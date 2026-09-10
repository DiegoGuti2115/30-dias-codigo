# Demostración breve — API de análisis de texto

Esta demostración usa el fixture [`data/fixtures/contract-example.txt`](../data/fixtures/contract-example.txt) y muestra el flujo completo de la única operación pública.

## 1. Iniciar la API

Desde la raíz del proyecto:

```powershell
python -m uvicorn src.main:app --reload
```

## 2. Entrada y llamada

El texto de entrada es:

```text
La API analiza texto. La API devuelve métricas útiles.
```

Ejecute la llamada en otra consola PowerShell:

```powershell
$body = @{ text = "La API analiza texto. La API devuelve métricas útiles." } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/analyze" -ContentType "application/json" -Body $body
```

## 3. Resultado esperado

La respuesta `200 OK` es JSON UTF-8 y coincide con [`data/expected/contract-example.json`](../data/expected/contract-example.json):

```json
{
  "metrics": {
    "character_count": 54,
    "character_count_without_whitespace": 46,
    "word_count": 9,
    "sentence_count": 2,
    "paragraph_count": 1,
    "estimated_reading_time_seconds": 3
  },
  "word_frequencies": [
    {"word": "api", "count": 2},
    {"word": "la", "count": 2},
    {"word": "analiza", "count": 1},
    {"word": "devuelve", "count": 1},
    {"word": "métricas", "count": 1},
    {"word": "texto", "count": 1},
    {"word": "útiles", "count": 1}
  ],
  "keywords": [
    {"word": "api", "count": 2},
    {"word": "analiza", "count": 1},
    {"word": "devuelve", "count": 1},
    {"word": "métricas", "count": 1},
    {"word": "texto", "count": 1}
  ]
}
```

Las reglas de normalización, segmentación, ordenación y errores están definidas en [`docs/CONTRATO_API_V1.md`](../docs/CONTRATO_API_V1.md).