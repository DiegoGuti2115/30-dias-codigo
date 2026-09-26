# Roadmap — Recuperador de palabras clave

## Objetivo del MVP

Entregar en un máximo de tres horas una CLI de Python 3.11+ que reciba una consulta y un corpus local pequeño, recupere documentos por coincidencia de palabras clave normalizadas, los ordene con una puntuación explicable y emita un resultado JSON determinista. La ejecución completa deberá funcionar sin red ni credenciales.

Azure AI Search se considera una mejora opcional de demostración; no forma parte del camino crítico y no podrá retrasar ni sustituir la recuperación local.

## Principios y límites de ejecución

- Se prioriza un único flujo local, atómico y demostrable: consulta, recuperación y resultado JSON.
- El corpus inicial será pequeño y controlado mediante fixtures locales.
- La relevancia se basará exclusivamente en coincidencias léxicas documentadas; no habrá embeddings, LLM ni búsqueda semántica.
- Cada fase P0 incluye su validación antes de pasar a la siguiente.
- Si Azure AI Search no valida recurso, credenciales y petición/respuesta antes de T+30, se descarta para la entrega diaria y se mantiene el fallback local.
- No se añadirán secretos; un archivo de ejemplo de entorno se creará solo si la integración opcional se implementa.

## Fases y prioridades

| Fase | Prioridad | Objetivo | Tareas | Dependencias | Entregable | Criterio de aceptación |
| --- | --- | --- | --- | --- | --- | --- |
| 0. Planificación y estructura | P0 | Preparar una base coherente sin implementar comportamiento | Documentar propósito, alcance, contrato previsto, fallback, criterios de aceptación y roadmap; crear directorios estándar vacíos | Normas del repositorio y plantilla Python CLI | `README.md`, `ROADMAP.md`, `src/`, `tests/`, `data/`, `assets/` | Documentación y estructura coherentes; sin código, fixtures, manifiestos ni configuración definitiva |
| 1. Contrato y base local | P0 | Fijar el contrato mínimo del flujo feliz | Definir argumentos CLI, forma del corpus, esquema del resultado, códigos de error y límites del MVP; declarar solo las dependencias necesarias | Fase 0 | Punto de entrada mínimo y contrato documentado | La ayuda de CLI y el contrato describen la misma consulta, corpus y salida; no hay acceso cloud |
| 2. Corpus y validación | P0 | Rechazar pronto entradas incoherentes | Crear fixtures de corpus pequeño; validar ruta, JSON o formato elegido, identificadores únicos, texto no vacío, consulta y límite de resultados | Fase 1 | Cargador/validador y fixtures | Entradas válidas se cargan de manera reproducible; errores comunes finalizan con mensaje claro y código no nulo |
| 3. Normalización y recuperación local | P0 | Obtener coincidencias relevantes de forma determinista | Normalizar texto y consulta; tokenizar con reglas documentadas; calcular coincidencias y puntuación; aplicar desempates estables | Fase 2 | Servicio local de recuperación | La misma consulta y corpus producen el mismo orden; cada resultado identifica términos coincidentes y puntuación |
| 4. Resultado y experiencia CLI | P0 | Exponer el resultado inspeccionable | Conectar la CLI, limitar resultados, serializar JSON UTF-8, informar consultas sin coincidencias y errores de dominio | Fase 3 | Ejecución de extremo a extremo local | Un comando documentado genera o muestra JSON válido con consulta, términos y resultados ordenados |
| 5. Integración opcional con Azure AI Search | P1 | Evaluar una consulta cloud sin comprometer el MVP | Añadir configuración no secreta, validar una conexión y consulta mínima, adaptar respuesta y distinguir origen del resultado | Fases 1–4, recurso Azure, credenciales e índice disponibles antes de T+30 | Adaptador opcional y `.env.example` si aplica | La integración se prueba antes de T+30; si falla o no está disponible, se elimina del camino de entrega sin afectar al modo local |
| 6. Validación y pruebas | P0 | Demostrar fiabilidad del comportamiento P0 | Cubrir validación, normalización, puntuación, empates, ausencia de resultados, serialización y flujo CLI con fixtures | Fases 2–4 | Suite de pruebas o verificación manual reproducible | El flujo local y los casos límite definidos pasan sin red; los resultados son deterministas |
| 7. Documentación y demo | P0 | Permitir reproducir y comunicar la entrega | Completar instalación, uso, ejemplos, contrato final, limitaciones, integración y fallback; crear demo de hasta 15 segundos | Fases 1–6 | README final y recurso en `assets/` | Una persona puede ejecutar el modo local limpio siguiendo la guía y observar entrada, acción y salida |
| 8. Verificación y entrega | P0 | Cerrar la entrega diaria sin ampliar alcance | Ejecutar verificaciones, revisar secretos, comprobar formato, actualizar el índice raíz solo si corresponde y preparar publicación | Fases 6–7 | Entrega verificable y materiales de publicación | Se cumple la Definition of Done del repositorio, incluido fallback local, documentación y demo |

## Estado de la Fase 0 — Planificación y estructura

**Estado: completada el 25/09/2026.** Esta fase se limitó a preparar la documentación y la estructura inicial del proyecto. No incorpora código ejecutable, dependencias, fixtures, pruebas, configuración de entorno ni integración externa.

- [x] Documentado el propósito, alcance del MVP, exclusiones, entradas y salidas previstas, decisiones técnicas, dependencias previstas, fallback local, riesgos y criterios de aceptación en [`README.md`](README.md).
- [x] Documentadas las fases P0/P1, prioridades, entregables, criterios de aceptación, límites de tiempo, riesgos y Definition of Done en [`ROADMAP.md`](ROADMAP.md).
- [x] Conservada la estructura estándar vacía: [`../src/`](../src/), [`../tests/`](../tests/), [`../data/`](../data/) y [`../assets/`](../assets/).
- [x] Preservados los directorios vacíos con [`../src/.gitkeep`](../src/.gitkeep), [`../tests/.gitkeep`](../tests/.gitkeep), [`../data/.gitkeep`](../data/.gitkeep) y [`../assets/.gitkeep`](../assets/.gitkeep).
- [x] Confirmado que Azure AI Search es opcional, que el corpus local es la ruta principal y que el fallback se activa si no hay validación antes de T+30.

**Pendiente y fuera de la Fase 0:** contrato definitivo de la CLI, manifiesto de dependencias, punto de entrada, corpus fixture, validación de entradas, normalización, puntuación, recuperación, serialización, pruebas ejecutables, demo e integración Azure. Estos elementos pertenecen a las Fases 1–8 y no se adelantan en esta entrega.

## Estado de la Fase 1 — Contrato y base local

**Estado: completada el 25/09/2026.** Se ha establecido el contrato mínimo de la CLI sin cargar corpus, validar entradas de dominio, normalizar texto, recuperar documentos ni acceder a servicios externos.

- [x] Creado [`../pyproject.toml`](../pyproject.toml) con distribución `src/`, requisito Python 3.11+ y configuración de `pytest`.
- [x] Creado [`../requirements.txt`](../requirements.txt) con la única dependencia de desarrollo necesaria: `pytest>=8,<9`; la ejecución usa exclusivamente la biblioteca estándar.
- [x] Creado el paquete [`../src/keyword_retrieval/__init__.py`](../src/keyword_retrieval/__init__.py) y el punto de entrada [`../src/keyword_retrieval/main.py`](../src/keyword_retrieval/main.py).
- [x] Definido el contrato CLI: `QUERY` obligatorio, `--corpus` con valor previsto `data/corpus.json`, `--limit` con valor previsto `10` y `--format json`.
- [x] Definida una salida JSON de contrato que declara `phase: 1` y `status: "contract-only"`, evitando presentar la solicitud como una recuperación ejecutada.
- [x] Añadidas pruebas de argumentos predeterminados y argumentos documentados en [`../tests/test_main.py`](../tests/test_main.py).
- [x] Documentados instalación, ejecución, ayuda, contrato temporal, estructura y límites de fase en [`README.md`](README.md).

**Decisión técnica:** `argparse`, `json` y `pathlib` de la biblioteca estándar bastan para congelar el contrato de la CLI. La ruta del corpus se conserva como `Path` durante el análisis de argumentos y se serializa como texto; no se comprueba su existencia hasta la Fase 2.

**Pendiente y deliberadamente fuera de la Fase 1:** fixture de corpus, validación de consulta, ruta, estructura JSON, identificadores, contenido, límite o formato real; normalización, coincidencias, puntuación, ranking, salida de resultados, adaptador Azure y demo. Estos elementos permanecen en las Fases 2–8.

## Estado de la Fase 2 — Corpus y validación

**Estado: completada el 25/09/2026.** La CLI valida una solicitud y un corpus JSON local antes de continuar, pero no normaliza texto, no busca coincidencias, no calcula puntuaciones y no serializa resultados de recuperación.

- [x] Creado el fixture local [`../data/corpus.json`](../data/corpus.json) con documentos JSON pequeños, identificables y reproducibles.
- [x] Creado [`../src/keyword_retrieval/corpus.py`](../src/keyword_retrieval/corpus.py) con el cargador reutilizable, el tipo inmutable `Document` y validadores de solicitud y corpus.
- [x] Fijado el contrato del corpus: archivo `.json` UTF-8 válido con raíz array no vacía; cada documento requiere `id` de texto no vacío y único, y `content` de texto no vacío.
- [x] Creado [`../src/keyword_retrieval/errors.py`](../src/keyword_retrieval/errors.py) con errores de dominio de código estable para fallos de solicitud, ruta, lectura, JSON y esquema.
- [x] Conectada la validación con [`../src/keyword_retrieval/main.py`](../src/keyword_retrieval/main.py): los errores de dominio se emiten como JSON por `stderr` y terminan con código `2`; las solicitudes válidas informan `phase: 2`, `status: "validated-only"` y `document_count`.
- [x] Añadidas pruebas en [`../tests/test_corpus.py`](../tests/test_corpus.py) y actualizadas las de [`../tests/test_main.py`](../tests/test_main.py) para cubrir rutas, JSON, esquema, documentos, consulta, límite y contrato CLI.
- [x] Documentado el contrato de validación, fixture, código de salida y ejemplos en [`README.md`](README.md).

**Pendiente y deliberadamente fuera de la Fase 2:** normalización, tokenización, coincidencias, puntuación, ordenación, límite efectivo de resultados, lista de resultados, consultas sin coincidencias, serialización final, Azure y demo. Estos elementos pertenecen a las Fases 3–8.

## Estado de la Fase 3 — Normalización y recuperación local

**Estado: completada el 25/09/2026.** Se ha incorporado el servicio local de normalización, coincidencia léxica, puntuación y ordenación determinista. Por el límite confirmado de esta fase, la CLI conserva el contrato de Fase 2 (`phase: 2`, `status: "validated-only"`); no aplica todavía el límite, no serializa resultados y no informa consultas sin coincidencias.

- [x] Creado [`../src/keyword_retrieval/retrieval.py`](../src/keyword_retrieval/retrieval.py) como capa de dominio independiente de la CLI.
- [x] Fijada la normalización: `casefold` Unicode, eliminación de marcas diacríticas y tokenización por palabras Unicode, espacios y puntuación.
- [x] Fijada la coincidencia léxica por palabra completa normalizada; no hay coincidencias parciales, sinónimos, embeddings ni búsqueda semántica.
- [x] Fijada la puntuación explicable: un punto por cada término distinto de la consulta que aparezca en el documento; repetir un término de consulta no aumenta la puntuación.
- [x] Excluidos los documentos sin coincidencias y aplicado el desempate estable por `id` ascendente después de ordenar por puntuación descendente.
- [x] Añadidas pruebas en [`../tests/test_retrieval.py`](../tests/test_retrieval.py) para acentos, mayúsculas, puntuación, espacios, coincidencias exactas, términos repetidos, ausencia de resultados y empates.
- [x] Conservados sin cambio los argumentos, la ayuda, las validaciones y los errores públicos de [`../src/keyword_retrieval/main.py`](../src/keyword_retrieval/main.py).
- [x] Documentadas las reglas y límites de Fase 3 en [`README.md`](README.md).

**Pendiente y deliberadamente fuera de la Fase 3:** conectar el servicio con la CLI, aplicar `--limit`, serializar resultados, declarar el contrato JSON de resultados y responder a consultas sin coincidencias mediante CLI. Estos elementos pertenecen a la Fase 4; Azure y demo permanecen en las Fases 5–8.

## Estado de la Fase 4 — Resultado y experiencia CLI

**Estado: completada el 25/09/2026.** La CLI integra validación, carga de corpus, recuperación local, límite y respuesta JSON UTF-8 determinista, sin red ni dependencias adicionales.

- [x] Conectado [`../src/keyword_retrieval/main.py`](../src/keyword_retrieval/main.py) con el servicio de recuperación de Fase 3, conservando los argumentos existentes y los errores de dominio de Fase 2.
- [x] Creado [`../src/keyword_retrieval/presentation.py`](../src/keyword_retrieval/presentation.py) para separar la construcción de la respuesta pública de la CLI y de la recuperación.
- [x] Fijado el contrato exitoso: `phase: 4`, `status: "completed"`, consulta original, `normalized_terms`, corpus, tamaño de corpus, límite, formato, número de coincidencias totales, número de resultados devueltos y lista `results`.
- [x] Serializado cada resultado con `id`, `score`, `matched_terms` y `preview`; la vista previa reduce espacios y se limita a 120 caracteres con `…` cuando se trunca.
- [x] Aplicado `--limit` después del ranking estable; `match_count` conserva todas las coincidencias y `result_count` expresa las entregadas.
- [x] Definido el caso sin coincidencias como respuesta exitosa con `match_count: 0`, `result_count: 0` y `results: []`.
- [x] Conservada la salida JSON de errores por `stderr` y el código `2` para entradas o corpus inválidos.
- [x] Actualizadas las pruebas CLI en [`../tests/test_main.py`](../tests/test_main.py) y creadas las pruebas de presentación en [`../tests/test_presentation.py`](../tests/test_presentation.py).
- [x] Documentado el contrato, los ejemplos y las verificaciones de Fase 4 en [`README.md`](README.md).

**Pendiente y deliberadamente fuera de la Fase 4:** Azure AI Search, configuración cloud, credenciales, adaptador remoto, demo, publicación y validaciones adicionales de entrega. Estos elementos pertenecen a las Fases 5–8.

## Estado de la Fase 5 — Integración opcional con Azure AI Search

**Estado: completada el 26/09/2026.** La integración cloud se validó contra un recurso, índice y consulta reales antes de incorporarse como proveedor opcional. El flujo local permanece como valor predeterminado, determinista y completamente independiente de red o credenciales.

- [x] Creado [`../.env.example`](../.env.example) con los nombres no secretos `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX_NAME` y `AZURE_SEARCH_API_KEY`, junto con [`.gitignore`](../.gitignore) para excluir archivos de configuración locales.
- [x] Validado el acceso API-key a un índice de Azure AI Search y una consulta mínima `azure search` contra el índice configurado antes de implementar el modo cloud.
- [x] Creado [`../src/keyword_retrieval/azure_search.py`](../src/keyword_retrieval/azure_search.py), un adaptador aislado que usa la API REST oficial con biblioteca estándar, limita resultados, adapta `id`, `content` y `@search.score`, y expone errores de dominio estables.
- [x] Añadido `--provider local|azure` a [`../src/keyword_retrieval/main.py`](../src/keyword_retrieval/main.py). `local` sigue siendo el predeterminado; `azure` se activa explícitamente y exige variables de entorno válidas.
- [x] Distinguido el origen mediante `source: "local"` o `source: "azure_ai_search"`; la respuesta cloud identifica el índice y preserva la puntuación del proveedor sin simular el ranking léxico local.
- [x] Añadido [`../data/azure-search-upload.json`](../data/azure-search-upload.json) como carga reproducible de documentos de demostración para un índice con `id` como clave y `content` buscable/recuperable.
- [x] Creadas pruebas de adaptador en [`../tests/test_azure_search.py`](../tests/test_azure_search.py) y pruebas CLI de los modos local/cloud y errores de configuración en [`../tests/test_main.py`](../tests/test_main.py).
- [x] Actualizado [`README.md`](README.md) con configuración, ejecución, contrato diferenciado, límites y fallback.

**Límite explícito:** Azure AI Search sigue siendo una mejora P1 de demostración. Si deja de estar disponible, devuelve un error de dominio solo para `--provider azure`; se omite ese proveedor y se conserva `--provider local` como ruta de entrega. No se incorporan SDKs, embeddings, búsqueda semántica, sincronización automática ni credenciales versionadas.

## Estado de la Fase 6 — Validación y pruebas

**Estado: completada el 26/09/2026.** La fiabilidad del flujo P0 local queda demostrada mediante una suite reproducible que no requiere red ni credenciales. La cobertura cloud opcional se conserva aislada y simulada para no convertir Azure en dependencia de las verificaciones P0.

- [x] Verificado el contrato de validación de consulta, límite, ruta, JSON y esquema de corpus en [`../tests/test_corpus.py`](../tests/test_corpus.py) y [`../tests/test_main.py`](../tests/test_main.py).
- [x] Verificadas la normalización Unicode, tokenización, puntuación por términos distintos, coincidencia exacta, empates por `id` y ausencia de resultados en [`../tests/test_retrieval.py`](../tests/test_retrieval.py).
- [x] Verificada la serialización local, incluidos contadores, límite, explicaciones y vistas previas normalizadas y acotadas, en [`../tests/test_presentation.py`](../tests/test_presentation.py).
- [x] Añadido un flujo CLI integral con fixture temporal que cubre normalización, términos repetidos, puntuación, desempate y límite en [`../tests/test_main.py`](../tests/test_main.py).
- [x] Ejecutada la suite local sin red: `python -m pytest -q` finaliza correctamente con resultados deterministas.

**Límite explícito:** esta fase valida el camino P0 local de las Fases 2–4. No amplía el algoritmo, el contrato local ni hace depender la suite de una consulta Azure real; el adaptador P1 mantiene sus pruebas aisladas.

## Estado de la Fase 7 — Documentación y demo

**Estado: completada el 26/09/2026.** La guía final documenta instalación, uso local, contrato, pruebas, integración opcional, fallback y limitaciones. El recurso reproducible de demostración muestra una entrada, la acción local y la salida JSON sin requerir red ni credenciales.

- [x] Consolidado [`README.md`](README.md) con instalación, argumentos, contrato de salida, ejemplos de coincidencia, límite, ausencia de resultados y error de validación.
- [x] Documentada la integración opcional de Azure AI Search, sus variables no secretas, sus errores y el fallback local independiente de credenciales.
- [x] Documentadas las limitaciones del MVP: corpus pequeño, recuperación léxica y ausencia de capacidades semánticas, embeddings, LLM o indexación automática.
- [x] Creado [`../assets/demo-local.md`](../assets/demo-local.md), un guion cronometrado de hasta 15 segundos que muestra entrada, acción y salida con el corpus local.
- [x] Conservado el modo `local` como ruta demostrable principal; la demo no realiza llamadas Azure ni lee secretos.

**Límite explícito:** esta fase no modifica la lógica de recuperación ni publica materiales externos. El guion puede grabarse como GIF o vídeo si el canal de publicación lo solicita; la verificación final y la publicación se reservan para la Fase 8.

## Estado de la Fase 8 — Verificación y entrega

**Estado: completada el 26/09/2026.** Se ha cerrado la entrega sin ampliar el alcance: las verificaciones locales, la revisión de secretos, el control de formato y la preparación de los materiales de publicación se han realizado sobre el flujo local reproducible.

- [x] Ejecutadas la suite local, la compilación del paquete y las invocaciones representativas de la CLI sin red ni credenciales.
- [x] Confirmados los casos de coincidencia, límite, ausencia de resultados y error de validación; el modo `local` sigue siendo el fallback principal.
- [x] Revisados los archivos versionados: no incluyen `.env.local` ni valores configurados de Azure AI Search; [`.env.example`](../.env.example) conserva exclusivamente marcadores no secretos.
- [x] Comprobado el formato con `git diff --check` y consolidada la documentación de entrega junto con el recurso reproducible [`../assets/demo-local.md`](../assets/demo-local.md).
- [x] Actualizado el índice raíz [`../../../README.md`](../../../README.md) con el identificador canónico [`../`](../) y el enlace a la demo local.
- [x] Preparados los materiales dentro del repositorio para publicación: README final, demo cronometrada, texto para LinkedIn en [`../assets/linkedin-post.md`](../assets/linkedin-post.md) y comandos de verificación reproducibles.

**Límite explícito:** la fase no añade funcionalidad, no sustituye el fallback local por Azure, no versiona secretos ni realiza acciones externas irreversibles. La grabación opcional, el post de LinkedIn y el `commit`/`push` deben ejecutarse manualmente por la persona responsable usando los materiales ya preparados.

## Orden sugerido para el límite diario

| Tiempo | Actividad | Resultado verificable |
| --- | --- | --- |
| 0:00–0:20 | Revisar contrato, crear base local y declarar dependencias mínimas | CLI inicial y estructura confirmadas |
| 0:20–0:45 | Construir corpus de fixture y validación | Errores de entrada reproducibles |
| 0:45–1:20 | Implementar normalización, coincidencias y puntuación | Ranking local determinista sobre el fixture |
| 1:20–1:45 | Integrar CLI y serialización JSON | Flujo local de extremo a extremo |
| 1:45–2:10 | Intentar Azure AI Search solo si aporta valor y hay recursos disponibles | Integración validada o fallback local irreversible |
| 2:10–2:35 | Añadir pruebas de comportamiento y casos límite | Verificaciones locales completadas |
| 2:35–2:50 | Completar README y grabar demo | Uso y resultado reproducibles |
| 2:50–3:00 | Revisión final, entrega y publicación | Alcance congelado y materiales preparados |

## Contrato funcional previsto

### Corpus local

La Fase 2 fija JSON UTF-8 como formato de corpus y `data/corpus.json` como ruta predeterminada. El contrato validado de cada documento exige:

- Un identificador único y estable.
- Contenido textual no vacío.
- Metadatos opcionales solo si son necesarios para la demo.

### Consulta

La CLI recibe una cadena con al menos un carácter distinto de espacios. Normaliza consulta y documentos con `casefold` Unicode y sin marcas diacríticas; tokeniza por palabras Unicode, por lo que espacios y puntuación separan términos y las coincidencias son por palabra completa.

### Resultado JSON

El resultado definitivo incluirá, como mínimo:

- Consulta original y términos normalizados.
- Número de coincidencias encontradas y número de resultados devueltos.
- Lista ordenada de documentos con identificador, puntuación, términos coincidentes y vista previa.
- Origen del resultado cuando exista un modo opcional cloud.

`RetrievalResult(document_id, score, matched_terms)` se presenta como un objeto JSON con `id`, `score`, `matched_terms` y `preview`. La respuesta incluye la consulta original, sus términos normalizados, los contadores de coincidencias antes y después del límite, y una lista vacía válida cuando no hay coincidencias.

## Estrategia de relevancia prevista

1. Aplicar `casefold` Unicode y eliminar marcas diacríticas de consulta y contenido.
2. Separar palabras mediante espacios, puntuación y guiones; comparar únicamente tokens completos.
3. Conservar cada término normalizado de consulta solo en su primera aparición.
4. Localizar los términos distintos de la consulta que aparezcan en cada documento y asignar un punto por término coincidente.
5. Excluir documentos sin coincidencias, ordenar por puntuación descendente y resolver empates con `id` ascendente.

El algoritmo se mantendrá deliberadamente simple y explicable. Cualquier técnica semántica se pospone para una evolución posterior al MVP.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación para la entrega |
| --- | --- | --- |
| Ambigüedad entre búsqueda léxica y semántica | Expectativas incorrectas | Nombrar y documentar la solución como recuperación por palabras clave; exponer coincidencias y puntuación |
| Formato de corpus inestable | Errores o datos no comparables | Fijar un único fixture y contrato P0 antes de implementar recuperación |
| Empates o ranking opaco | Resultados no reproducibles | Definir una fórmula simple y un desempate estable, cubiertos por pruebas |
| Fallo de Azure, cuota, permisos o red | Bloqueo de demo | Mantener el modo local completo como ruta principal y activar fallback en T+30 |
| Dependencias innecesarias | Riesgo de instalación y tiempo | Priorizar biblioteca estándar y añadir paquetes solo con justificación del MVP |
| Expansión de alcance | No completar el flujo principal | Aplicar las puertas T+90 y T+120: retirar primero cloud, mejoras de ranking, persistencia y UX adicional |

## Definition of Done específica

- El flujo local consulta un corpus fixture y produce resultados ordenados sin acceso a red.
- La salida JSON es válida, tiene contrato documentado y explica la coincidencia de cada resultado.
- La puntuación, normalización y desempate se verifican con casos reproducibles.
- Las entradas inválidas y la ausencia de coincidencias tienen una respuesta clara.
- Las dependencias se declaran y aíslan dentro del proyecto cuando se introduzcan.
- Si existe integración Azure, cuenta con variables documentadas sin secretos y fallback local validado.
- El README final describe instalación, ejecución, pruebas, integración opcional, fallback y limitaciones.
- `assets/` contiene una demostración breve de entrada, acción y resultado.
- La verificación final no añade capacidades fuera del alcance definido.

## Posterior al MVP

1. Añadir ponderación configurable, coincidencia de frases y operadores simples.
2. Importar corpus desde fragmentos generados por herramientas previas del reto.
3. Incorporar indexación de directorios y formatos adicionales con límites explícitos.
4. Comparar recuperación local con Azure AI Search mediante un adaptador aislado.
5. Incorporar búsqueda semántica, embeddings o una API únicamente como proyecto o fase independiente, tras validar el MVP léxico.
