# Demo local — 15 segundos

Esta demo no necesita red, credenciales ni Azure AI Search. Muestra una entrada, la recuperación local y el JSON resultante usando el corpus fixture incluido.

| Tiempo | Acción observable |
| --- | --- |
| 0–3 s | Abrir una terminal en la raíz de `day-26-keyword-retrieval-tool`. |
| 3–6 s | Ejecutar `python -m keyword_retrieval.main "azure search"`. |
| 6–12 s | Observar el resultado JSON local: dos términos normalizados, un documento coincidente, puntuación explicable y origen `local`. |
| 12–15 s | Ejecutar `python -m keyword_retrieval.main "unmatched-term"` para mostrar la respuesta exitosa sin coincidencias. |

## Entrada, acción y salida

```text
$ python -m keyword_retrieval.main "azure search"
{"corpus": "data/corpus.json", "document_count": 3, "format": "json", "limit": 10, "match_count": 1, "normalized_terms": ["azure", "search"], "phase": 5, "query": "azure search", "result_count": 1, "results": [{"id": "azure-optional", "matched_terms": ["azure", "search"], "preview": "Azure AI Search remains optional and must never block the local workflow.", "score": 2}], "source": "local", "status": "completed"}

$ python -m keyword_retrieval.main "unmatched-term"
{"corpus": "data/corpus.json", "document_count": 3, "format": "json", "limit": 10, "match_count": 0, "normalized_terms": ["unmatched", "term"], "phase": 5, "query": "unmatched-term", "result_count": 0, "results": [], "source": "local", "status": "completed"}
```

La CLI imprime el JSON en una sola línea; solo se ajustará visualmente si el visor divide líneas largas. Grabe los cuatro pasos cronometrados como GIF o vídeo únicamente si el canal de publicación exige un formato visual; este guion fuente sigue siendo determinista y reproducible.