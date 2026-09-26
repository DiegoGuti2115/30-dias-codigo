# Día 26 — Recuperador de palabras clave

> Microproyecto del reto **30 Días, 30 Proyectos**. Identificador canónico: `day-26-keyword-retrieval-tool`.

## Estado

**Fase 8 — Verificación y entrega completada.** El flujo local, la documentación, el recurso de demo y los controles de formato y secretos se han revisado para la entrega; Azure AI Search continúa siendo una integración opcional y aislada.

## Contrato de la CLI final

La interfaz pública se ejecuta con [`python -m keyword_retrieval.main QUERY`](../src/keyword_retrieval/main.py) y define los siguientes argumentos:

| Argumento | Tipo | Valor predeterminado | Regla de validación |
| --- | --- | --- | --- |
| `QUERY` | Texto posicional | — | Debe contener texto distinto de espacios. |
| `--provider local\|azure` | Opción | `local` | `local` usa el corpus determinista; `azure` requiere configuración Azure AI Search válida. |
| `--corpus PATH` | Ruta | `data/corpus.json` | Solo para `local`: debe existir, ser un archivo JSON UTF-8 legible y cumplir el esquema de corpus. |
| `--limit INT` | Entero | `10` | Debe ser mayor que cero y limita los resultados devueltos sin cambiar su orden. |
| `--format json` | Opción | `json` | Solo se admite JSON. |

Cuando la entrada es válida, la CLI imprime un objeto JSON UTF-8 con `phase: 5`, `status: "completed"`, `source`, la consulta original, `normalized_terms`, `limit`, `format`, contadores y `results`. El modo `local` conserva `corpus`, `document_count`, `matched_terms` y su puntuación léxica determinista. El modo `azure` identifica el índice mediante `index`, marca `source: "azure_ai_search"` y conserva la puntuación devuelta por el proveedor; no pretende que su orden sea equivalente al ranking local.

Los errores de dominio se imprimen como JSON en la salida de error estándar y el proceso devuelve el código `2`:

```json
{"error": {"code": "invalid_limit", "message": "limit must be greater than zero"}}
```

### Ejemplos de uso

```text
python -m keyword_retrieval.main "azure search"
python -m keyword_retrieval.main "retrieval" --limit 1
python -m keyword_retrieval.main "unmatched-term"
python -m keyword_retrieval.main "keyword retrieval" --limit 0
python -m keyword_retrieval.main "azure search" --provider azure --limit 2
```

La ayuda del comando se consulta con [`python -m keyword_retrieval.main --help`](../src/keyword_retrieval/main.py).

### Contrato del corpus local

El corpus predeterminado es [`../data/corpus.json`](../data/corpus.json): un array JSON no vacío de documentos. Cada documento debe contener exactamente los campos necesarios para la siguiente fase:

```json
{"id": "identificador-estable", "content": "Texto no vacío del documento."}
```

Las reglas de Fase 2 son: extensión `.json`, codificación UTF-8, JSON válido, raíz de tipo array no vacío, documentos objeto, `id` de texto no vacío y único, y `content` de texto no vacío. Las validaciones reutilizables se encuentran en [`../src/keyword_retrieval/corpus.py`](../src/keyword_retrieval/corpus.py) y los errores de dominio en [`../src/keyword_retrieval/errors.py`](../src/keyword_retrieval/errors.py).

### Recuperación local de Fase 3

El servicio de [`../src/keyword_retrieval/retrieval.py`](../src/keyword_retrieval/retrieval.py) aplica estas reglas deterministas:

- Convierte texto a minúsculas Unicode mediante `casefold` y elimina marcas diacríticas; por tanto, `CAFÉ` y `café` producen el término `cafe`.
- Divide en palabras Unicode por espacios, puntuación y guiones; los guiones bajos no forman parte de una palabra.
- Compara únicamente palabras completas normalizadas: no hay coincidencias parciales, sinónimos ni búsqueda semántica.
- Conserva la primera aparición de cada término de consulta; los términos repetidos no incrementan la puntuación.
- Un resultado recibe un punto por cada término de consulta distinto presente en su documento y expone esos términos en el orden de la consulta.
- Excluye documentos sin coincidencias y ordena por puntuación descendente y, en empate, por `id` ascendente.

`RetrievalResult` contiene `document_id`, `score` y `matched_terms`. La capa [`../src/keyword_retrieval/presentation.py`](../src/keyword_retrieval/presentation.py) la convierte en cada elemento de `results` con `id`, `score`, `matched_terms` y `preview`. La vista previa normaliza espacios y se limita a 120 caracteres; añade `…` si se trunca.

Una consulta sin coincidencias finaliza correctamente con `match_count: 0`, `result_count: 0` y `results: []`; no es un error de dominio. `match_count` refleja todas las coincidencias antes del límite y `result_count` las coincidencias serializadas después de aplicarlo.

## Propósito

Resolver de forma local y reproducible la recuperación de los documentos más relevantes de un corpus pequeño a partir de una consulta de palabras clave. El resultado permitirá inspeccionar qué documentos coinciden, por qué términos y en qué orden determinista se priorizan.

El proyecto continúa el flujo de preparación documental del Día 25: sus fragmentos o documentos de texto podrán convertirse posteriormente en entradas del corpus, pero este proyecto no implementará fragmentación ni extracción de formatos en su MVP.

## Alcance del MVP previsto

- Recibir una consulta textual y un corpus local pequeño de documentos de texto o registros JSON.
- Normalizar consulta y contenido de forma explícita y reproducible antes de comparar palabras clave.
- Recuperar documentos que contengan uno o más términos de la consulta.
- Calcular una puntuación local determinista basada en coincidencias de palabras clave.
- Devolver resultados ordenados con identificador, puntuación, términos coincidentes y una vista previa segura del contenido.
- Exponer el flujo mediante una interfaz de línea de comandos de Python.
- Emitir una salida JSON inspeccionable y apta para usarse como entrada de una etapa posterior.
- Incorporar Azure AI Search solo como integración opcional, después de validar completamente el flujo local.

## Fuera de alcance

- Búsqueda semántica, embeddings, modelos generativos o reranking mediante LLM.
- Indexación automática de directorios, crawling web, base de datos, interfaz web, autenticación o multiusuario.
- Ingesta de PDF, DOCX, OCR u otros formatos binarios.
- Persistencia remota obligatoria o dependencia de credenciales cloud para la demostración.
- Ajuste de relevancia avanzado, sinónimos, corrección ortográfica, facetas o filtros complejos.
- Compatibilidad garantizada con corpus grandes; el MVP se limitará deliberadamente a una colección local pequeña.

## Flujo general de uso previsto

1. La persona usuaria prepara un corpus local con documentos identificables.
2. Indica una consulta de palabras clave y, si se necesita, la ubicación del corpus.
3. La herramienta valida que la consulta y el corpus cumplen el contrato mínimo.
4. Normaliza texto y consulta, localiza coincidencias y calcula una puntuación explicable.
5. Ordena los documentos aplicando desempates estables.
6. Muestra un resumen y escribe o devuelve el resultado JSON.
7. De forma opcional, una fase posterior podrá ejecutar la misma consulta contra Azure AI Search, sin reemplazar el modo local de demostración.

## Entradas y salidas esperadas

### Entradas

| Entrada | Formato previsto | Reglas iniciales |
| --- | --- | --- |
| Consulta | Texto no vacío | Se segmentará y normalizará antes de buscar. |
| Corpus local | JSON o archivos de texto definidos por el contrato futuro | Cada documento necesitará un identificador único y contenido textual. |
| Límite de resultados | Entero opcional | Restringirá el número de documentos devueltos sin alterar el orden de relevancia. |
| Configuración cloud opcional | Variables de entorno documentadas en una fase posterior | Nunca será necesaria para el flujo local. |

### Salida

La salida prevista será un objeto JSON con la consulta original, sus términos normalizados, el número de resultados y una lista ordenada de coincidencias. Cada coincidencia incluirá, como mínimo, un identificador de documento, puntuación, términos que coincidieron y una vista previa textual.

El contrato definitivo de campos, tipos, errores y códigos de salida se documentará antes de implementar la lógica de recuperación. La ordenación deberá ser determinista, incluso cuando dos documentos obtengan la misma puntuación.

## Funcionalidades previstas

| Prioridad | Funcionalidad | Resultado observable |
| --- | --- | --- |
| P0 | Validación de consulta y corpus | Errores claros para datos ausentes, vacíos o inválidos. |
| P0 | Normalización de palabras clave | Comparaciones coherentes ante mayúsculas, espacios y puntuación básica. |
| P0 | Recuperación local | Documentos coincidentes ordenados de forma estable. |
| P0 | Explicación mínima | Términos coincidentes y puntuación por resultado. |
| P0 | Salida JSON | Resultado consumible e inspeccionable localmente. |
| P1 | Adaptador de Azure AI Search | Consulta opcional equivalente con el proveedor, si se valida antes de T+30. |
| P1 | Comparación de modos | Información clara sobre si el resultado procede del índice local o cloud. |

## Decisiones técnicas iniciales

- **Runtime:** Python 3.11 o superior, conforme al stack base del repositorio.
- **Interfaz:** una CLI local para mantener la solución atómica, automatizable y demostrable en el límite diario de tres horas.
- **Ruta principal:** recuperación local basada en palabras clave y biblioteca estándar siempre que sea viable.
- **Formato de intercambio:** JSON UTF-8 para el corpus de fixture y los resultados, por ser legible, portable y fácil de validar.
- **Relevancia:** puntuación explicable por coincidencia de términos; no se presentará como búsqueda semántica.
- **Determinismo:** normalización, puntuación y desempate definidos de manera explícita para posibilitar pruebas reproducibles.
- **Arquitectura futura:** separación entre carga de corpus, normalización, recuperación, serialización y adaptador opcional de proveedor.
- **Seguridad:** los secretos no se versionarán. Si la integración cloud llega a implementarse, se añadirá entonces un archivo de ejemplo de variables sin valores reales.

## Dependencias

| Área | Dependencia | Estado |
| --- | --- | --- |
| Ejecución local y adaptador Azure REST | Python 3.11+ y biblioteca estándar | Activa en la Fase 5. |
| Pruebas de contrato | `pytest>=8,<9` | Declarada en [`../requirements.txt`](../requirements.txt). |
| Empaquetado y configuración de pruebas | `setuptools` y configuración de `pytest` | Declarados en [`../pyproject.toml`](../pyproject.toml). |
| Azure AI Search | API REST oficial mediante `urllib.request` | Opcional; validada sin añadir dependencias. |

La instalación prevista es `python -m pip install -e . -r requirements.txt`. El ejemplo no secreto [`.env.example`](../.env.example) documenta `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX_NAME` y `AZURE_SEARCH_API_KEY`; [`.env.local`](../.env.local) está excluido de Git y nunca debe versionarse.

## Integración opcional y fallback

### Azure AI Search (Fase 5)

El adaptador [`../src/keyword_retrieval/azure_search.py`](../src/keyword_retrieval/azure_search.py) usa la API REST `2024-07-01` con una API key proporcionada únicamente por variables de entorno. El índice validado debe disponer de `id` como clave recuperable y de `content` como cadena `searchable` y `retrievable`. La consulta cloud solicita únicamente `id` y `content`, limita con `--limit`, y adapta la respuesta a JSON sin imprimir secretos.

1. Copie [`.env.example`](../.env.example) a un archivo local ignorado, por ejemplo `.env.local`, y complete sus tres valores reales.
2. Exporte esas variables en la sesión antes de ejecutar la CLI. En PowerShell: `Get-Content .env.local | Where-Object { $_ -match '^[^#=]+=' } | ForEach-Object { $name, $value = $_ -split '=', 2; [Environment]::SetEnvironmentVariable($name, $value, 'Process') }`.
3. Ejecute `python -m keyword_retrieval.main "azure search" --provider azure --limit 2`.

Si falta configuración, el servicio no responde, el índice no es válido o la petición remota falla, la CLI devuelve un error de dominio JSON con código `azure_search_*` y código de salida `2`. El modo `local` no lee ninguna credencial, no usa red y sigue siendo el comando de demostración principal.

- **Ruta principal:** corpus local de fixture y recuperación determinista por palabras clave.
- **Integración opcional:** Azure AI Search podrá añadir valor demostrativo únicamente si credenciales, recurso, índice y petición de prueba se validan antes de T+30.
- **Fallback obligatorio:** el corpus local y sus fixtures permitirán ejecutar y verificar el flujo completo sin red, cuota, permisos ni proveedor externo.
- **Criterio de cambio:** si la integración no se valida antes de T+30, se abandona para la entrega diaria y se conserva exclusivamente el modo local.

## Verificación reproducible

```text
python -m pip install -r requirements.txt
python -m pytest
python -m keyword_retrieval.main --help
python -m keyword_retrieval.main "azure search"
python -m keyword_retrieval.main "unmatched-term"
python -m keyword_retrieval.main "retrieval" --limit 1
python -m compileall -q src
# Tras exportar las variables de Azure AI Search:
python -m keyword_retrieval.main "azure search" --provider azure --limit 2
```

Las pruebas en [`../tests/test_corpus.py`](../tests/test_corpus.py) cubren validación de solicitud, ruta, JSON y esquema. Las de [`../tests/test_retrieval.py`](../tests/test_retrieval.py) verifican normalización, tokenización, puntuación, coincidencia exacta, empates y ausencia de resultados. [`../tests/test_presentation.py`](../tests/test_presentation.py) comprueba serialización, contadores y vistas previas; [`../tests/test_main.py`](../tests/test_main.py) completa el flujo CLI local con fixtures, límite y orden determinista. Las pruebas en [`../tests/test_azure_search.py`](../tests/test_azure_search.py) conservan el proveedor opcional aislado mediante respuestas simuladas, sin llamadas externas.

## Demo local de 15 segundos

El guion reproducible de [la demo local](../assets/demo-local.md) muestra entrada, acción y salida en menos de 15 segundos con el proveedor predeterminado `local`. No carga [`.env.local`](../.env.local), no accede a Azure y muestra tanto una coincidencia como el caso válido sin resultados. Puede grabarse directamente como GIF o vídeo si el canal de publicación exige un formato visual.

## Estructura del proyecto

La estructura final mantiene el estándar del repositorio:

- [`../src/keyword_retrieval/`](../src/keyword_retrieval/): paquete de Python, validadores, recuperación, presentación y punto de entrada de la CLI.
- [`../tests/`](../tests/): pruebas reproducibles de validación, recuperación, serialización y flujo CLI de Fase 6.
- [`../data/`](../data/): fixtures y corpus de muestra locales; contiene [`corpus.json`](../data/corpus.json).
- [`../assets/`](../assets/): recurso de demostración; [`demo-local.md`](../assets/demo-local.md) contiene el guion de hasta 15 segundos con entrada, acción y salida.
- [`ROADMAP.md`](ROADMAP.md): fases, prioridades, límites y criterios de avance.
- [`../pyproject.toml`](../pyproject.toml): metadatos de proyecto, distribución `src/` y configuración de pruebas.

## Criterios de aceptación del MVP

- La herramienta acepta una consulta válida y un corpus local documentado sin requerir servicios externos.
- La normalización y la regla de puntuación están documentadas y producen el mismo orden para las mismas entradas.
- Cada resultado explica al menos su identificador, puntuación y palabras clave coincidentes.
- Una consulta sin coincidencias devuelve una respuesta JSON válida y comprensible.
- Las entradas inválidas finalizan con un error claro y reproducible.
- El modo local se cubre con fixtures y pruebas o un guion manual reproducible.
- La integración Azure, si se implementa, utiliza variables de entorno sin secretos en el repositorio y no bloquea el fallback local.
- La guía final incluirá instalación, ejecución, ejemplo de entrada y salida, pruebas, integración, fallback y limitaciones.
- El recurso de demostración mostrará entrada, acción y resultado en un máximo de 15 segundos.
- El índice raíz, la demostración y la publicación se actualizarán únicamente en la fase de entrega que corresponda.

## Riesgos y límites iniciales

| Riesgo o límite | Mitigación prevista |
| --- | --- |
| Consulta ambigua o con pocas palabras | Mostrar coincidencias y puntuación explícitas, sin atribuir comprensión semántica al sistema. |
| Empates de relevancia | Aplicar un desempate estable documentado. |
| Corpus mal formado | Validar estructura, identificadores únicos y contenido textual antes de recuperar. |
| Diferencias con Azure AI Search | Mantener contratos de salida diferenciados y declarar que el modo local es el fallback demostrable. |
| Credenciales, red o cuota cloud | Activar de forma irreversible el modo local al llegar a T+30 sin validación. |
| Crecimiento del corpus | Mantener un límite de corpus pequeño para el MVP y diferir indexación avanzada. |

## Plan de desarrollo

Las fases priorizadas, entregables y condiciones de avance están en [`ROADMAP.md`](ROADMAP.md). La integración opcional con Azure AI Search se validó contra el índice configurado antes de activar el adaptador; no se añaden interfaz gráfica, embeddings ni capacidades semánticas.

## Limitaciones y entrega

La recuperación local está diseñada para un corpus JSON pequeño y controlado. No implementa búsqueda semántica, embeddings, LLM, indexación de directorios, formatos binarios ni ranking avanzado. Azure AI Search no es necesario para instalar, probar, demostrar o usar el flujo local; si no hay credenciales, red o cuota, use el proveedor predeterminado `local` y el corpus fixture.

La entrega incluye el guion final en [`../assets/demo-local.md`](../assets/demo-local.md), el texto de publicación en [`../assets/linkedin-post.md`](../assets/linkedin-post.md) y el índice raíz enlaza el identificador canónico del proyecto y su demo local. La publicación externa, la grabación opcional como GIF o vídeo y el `commit`/`push` quedan fuera de los archivos que puede generar esta herramienta; el material local necesario para realizarlos ya está preparado.
