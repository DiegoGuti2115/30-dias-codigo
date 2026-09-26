# Post de LinkedIn — Día 26

## Texto listo para publicar

Hoy he construido el Día 26 del reto **30 Días, 30 Proyectos**: un recuperador de palabras clave en Python.

El problema: recuperar documentos relevantes de un corpus pequeño sin depender de red, credenciales ni servicios externos.

La solución usa coincidencias léxicas explicables:

- normaliza mayúsculas y acentos;
- compara palabras completas;
- asigna un punto por cada término distinto que coincide;
- ordena por puntuación y resuelve empates por identificador;
- devuelve JSON determinista para automatizar su consumo.

También incorporé Azure AI Search como proveedor opcional mediante REST. El flujo local sigue siendo el fallback principal, probado y demostrable aunque Azure no esté disponible.

La demo local dura menos de 15 segundos y muestra una consulta con resultado y otra sin coincidencias:

```text
python -m keyword_retrieval.main "azure search"
python -m keyword_retrieval.main "unmatched-term"
```

Código y guía: `projects/day-26-keyword-retrieval-tool`

#Python #AzureAISearch #CLI #SoftwareEngineering #30Dias30Proyectos

## Material de publicación

- Use el guion de `demo-local.md` para grabar un GIF o vídeo opcional de hasta 15 segundos.
- Incluya un enlace directo a la carpeta del proyecto y, si procede, al recurso de demo.
- No muestre `.env.local`, valores de Azure ni cabeceras con API keys durante la grabación.
