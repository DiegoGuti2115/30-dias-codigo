# Plan de publicación en LinkedIn — Día 04/30

## Objetivo de comunicación

Presentar el cuarto proyecto del reto **30 Días, 30 Proyectos** como una herramienta CLI local y verificable para transformar un archivo de logs en información operativa: resumen por severidad, mensajes frecuentes y reporte opcional de errores. El post debe poner el foco en una decisión de ingeniería concreta: definir un contrato pequeño y reproducible antes de implementar el parser y la CLI.

## Audiencia

- Personas desarrolladoras que trabajan con Python, herramientas internas o automatización.
- Perfiles de backend, plataforma, SRE u observabilidad interesados en flujos de logs simples y reproducibles.
- Recruiters y responsables técnicos que valoran entregas acotadas, documentadas y con pruebas ejecutables.

## Ángulo narrativo y mensaje principal

**Ángulo:** convertir líneas de log heterogéneas en una salida predecible sin depender de servicios externos.

**Mensaje principal:** una herramienta pequeña puede ser útil y confiable si explicita el formato de entrada, conserva el contexto de cada evento, tolera líneas inválidas y demuestra su resultado con fixtures, referencias y pruebas locales.

## Beneficios que conviene destacar

1. Lee un archivo local UTF-8 de forma secuencial, línea a línea.
2. Admite `common` y `jsonl` mediante selección explícita, evitando una autodetección ambigua.
3. Normaliza eventos válidos a timestamp, nivel, mensaje y número de línea; en JSON Lines conserva las claves extra como metadatos internos.
4. Cuenta eventos válidos e inválidos, muestra los cinco niveles admitidos y calcula hasta tres mensajes frecuentes con desempate por primera aparición.
5. Con `--errors`, lista solamente `ERROR` y `CRITICAL` en el orden físico de entrada.
6. Evita mostrar el contenido de las líneas inválidas en la salida de terminal.
7. Se ejecuta con Python 3.11+ y biblioteca estándar; no requiere red, credenciales ni dependencias externas.

No presentar como funcionalidad disponible: autodetección de formato, análisis de varios archivos o directorios, entrada estándar, filtros temporales, exportación, monitorización, alertas, integración cloud ni perfiles de proveedores de logs.

## Evidencia técnica para cada afirmación

| Afirmación para el post | Evidencia local |
|---|---|
| Procesa un único archivo local `common` o `jsonl`. | [`README.md`](../README.md) y [`CONTRATO.md`](CONTRATO.md). |
| Normaliza eventos y conserva número de línea; clasifica diagnósticos por línea. | [`models.py`](../src/models.py), [`parsers.py`](../src/parsers.py) y [`test_parsers.py`](../tests/test_parsers.py). |
| Calcula severidades, mensajes frecuentes y un reporte determinista de errores. | [`analyzer.py`](../src/analyzer.py), [`reporters.py`](../src/reporters.py) y [`test_analyzer.py`](../tests/test_analyzer.py). |
| La CLI expone `analyze`, `--format` y `--errors`, con códigos `0`, `1` y `2`. | [`main.py`](../src/main.py), [`CONTRATO.md`](CONTRATO.md) y [`test_cli.py`](../tests/test_cli.py). |
| El caso `common` demostrable tiene 7 eventos válidos, 2 `ERROR` y 1 `CRITICAL`. | [`common-valid.log`](../data/fixtures/common-valid.log), [`common-valid-summary.json`](../data/expected/common-valid-summary.json) y [`demo-common-valid.txt`](../assets/demo-common-valid.txt). |
| El caso `jsonl` admite metadatos sin incluirlos en el resumen. | [`jsonl-valid.jsonl`](../data/fixtures/jsonl-valid.jsonl), [`jsonl-valid-summary.json`](../data/expected/jsonl-valid-summary.json) y [`test_cli.py`](../tests/test_cli.py). |
| El proyecto tiene verificación local reproducible. | [`README.md`](../README.md), [`USO.md`](../examples/USO.md) y los tres módulos de [`tests`](../tests). |

## Estructura de la publicación

1. **Titular:** Día 04/30 y resultado observable.
2. **Problema:** revisar texto de logs a mano no facilita identificar severidades, recurrencias ni errores.
3. **Solución:** CLI local con dos formatos seleccionados explícitamente.
4. **Decisión técnica:** parser secuencial → modelo normalizado → análisis → presentación determinista.
5. **Alcance consciente:** un archivo, UTF-8 y sin servicios externos; mencionar una limitación real en lugar de prometer una plataforma de observabilidad.
6. **Prueba visible:** demo con el fixture `common`, incluyendo 7 eventos y el reporte de tres líneas de error/criticidad.
7. **Cierre:** aprendizaje, enlace directo al código y llamada a la acción.

## Texto final listo para publicar

> Día 04/30 — construí un analizador local de logs que convierte un archivo en un resumen reproducible y un reporte de errores.
>
> Cuando un log mezcla niveles, mensajes repetidos y líneas inválidas, leerlo manualmente no ayuda mucho a responder lo básico: ¿qué severidades aparecieron?, ¿qué se repite?, ¿dónde están los errores?
>
> Para el cuarto proyecto de mi reto #30Dias30Proyectos construí una CLI en Python que analiza un único archivo UTF-8 en dos formatos: `common` y JSON Lines (`jsonl`).
>
> La decisión clave fue no mezclar responsabilidades: el parser procesa línea a línea y normaliza cada evento; el análisis calcula conteos y mensajes frecuentes; el presentador genera una salida determinista. Así, con `--errors`, el reporte muestra únicamente eventos `ERROR` y `CRITICAL` conservando su orden de entrada.
>
> La demo usa un fixture sintético de 7 eventos: detecta 2 `ERROR`, 1 `CRITICAL` y repite como mensaje más frecuente “Conexión rechazada por el proveedor”. Las líneas inválidas se contabilizan, pero no se exponen en la salida.
>
> También dejé límites explícitos para esta primera versión: no hay autodetección, monitorización en tiempo real, múltiples archivos, exportación ni servicios externos. Todo funciona con Python 3.11+ y biblioteca estándar.
>
> Lo validé con fixtures locales, resultados de referencia, pruebas unitarias e integración real de la CLI.
>
> Mi aprendizaje de hoy: un contrato de entrada pequeño y pruebas reproducibles dan más valor que añadir funciones ambiguas demasiado pronto.
>
> **Stack:** Python 3.11+, `argparse`, `json`, `re`, `collections`, `pathlib` y `unittest`.
>
> **Código:** https://github.com/DiegoGuti2115/30-dias-codigo/tree/main/projects/day-04-log-analyzer
>
> ¿Qué formato de log te encontrarías primero en una herramienta interna: texto común, JSON Lines u otro perfil específico?
>
> #30Dias30Proyectos #BuildInPublic #Python #CLI #Observabilidad #LogAnalysis #Testing

## Llamada a la acción

Usar la pregunta final del texto publicado: **“¿Qué formato de log te encontrarías primero en una herramienta interna: texto común, JSON Lines u otro perfil específico?”**. Es específica, conecta con el límite consciente de la v1 y no presupone funcionalidades futuras.

## Hashtags

`#30Dias30Proyectos #BuildInPublic #Python #CLI #Observabilidad #LogAnalysis #Testing`

## Demo o captura recomendada

Adjuntar un GIF o vídeo de un máximo de 15 segundos, conforme a [`LINKEDIN_TEMPLATE.md`](../../../docs/LINKEDIN_TEMPLATE.md), grabado desde la raíz del proyecto:

```text
python src/main.py analyze data/fixtures/common-valid.log --format common --errors
```

Guion de 15 segundos:

1. **0–3 s:** mostrar el comando completo y el nombre del fixture sintético.
2. **3–10 s:** mostrar el resumen: 7 líneas leídas, 7 eventos válidos, los cinco conteos y el mensaje repetido dos veces.
3. **10–15 s:** mostrar el reporte en orden físico de las líneas 4, 5 y 6 (`ERROR`, `CRITICAL`, `ERROR`).

La salida exacta de referencia está en [`demo-common-valid.txt`](../assets/demo-common-valid.txt). Si se publica una captura estática en vez de vídeo, incluir solo el resumen y el reporte de errores del fixture; no mostrar logs de producción ni datos sensibles.

## Momento y contexto de publicación

Publicar después de que el proyecto y la demo estén disponibles en la rama principal, idealmente en el bloque de publicación del reto definido en [`DAILY_WORKFLOW.md`](../../../docs/DAILY_WORKFLOW.md): tras la verificación final, el commit y el push. El contexto recomendado es el cierre del Día 04, enlazando el proyecto directamente y adjuntando la demo funcional.

## Variantes de enfoque

- **Ingeniería de producto:** mantener el texto final y enfatizar el alcance consciente: un archivo, dos formatos, sin dependencias externas y con límites explícitos.
- **Calidad y pruebas:** sustituir el segundo párrafo por el valor de fixtures sintéticos, referencias JSON y pruebas de parser, análisis y CLI; conservar el mismo enlace y demo.
- **Observabilidad práctica:** abrir con la pregunta “¿cuántos errores, avisos y mensajes repetidos hay en este archivo?” y demostrar la salida del fixture `common`; no describir la herramienta como plataforma de observabilidad.

## Comprobaciones finales antes de publicar

- [ ] El enlace de código apunta a `projects/day-04-log-analyzer` en la rama publicada.
- [ ] La demo se ha grabado con el comando y fixture indicados y muestra entrada → acción → resultado en 15 segundos o menos.
- [ ] La captura o vídeo contiene únicamente fixtures sintéticos; no contiene datos de producción, secretos ni rutas personales.
- [ ] El post mantiene `common` y `jsonl` como formatos seleccionados explícitamente; no menciona autodetección.
- [ ] El post no promete exportación, alertas, monitorización, múltiples archivos, filtros temporales ni integración cloud.
- [ ] La afirmación de 7 eventos, 2 `ERROR` y 1 `CRITICAL` coincide con [`common-valid-summary.json`](../data/expected/common-valid-summary.json).
- [ ] El post nombra correctamente el flag `--errors` y su filtro fijo para `ERROR` y `CRITICAL`.
- [ ] La mención a pruebas se limita a fixtures, referencias, pruebas unitarias e integración CLI existentes.
- [ ] El texto conserva la estructura problema → decisión técnica → demo → aprendizaje → stack → código de [`LINKEDIN_TEMPLATE.md`](../../../docs/LINKEDIN_TEMPLATE.md).
- [ ] Los saltos de línea, bloque de código, enlace y hashtags se revisan en la vista previa de LinkedIn antes de publicar.