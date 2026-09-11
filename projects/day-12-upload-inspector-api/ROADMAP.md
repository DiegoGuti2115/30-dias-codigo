# Roadmap — API de inspección de archivos

Este roadmap organiza la creación de la primera versión local de la API. Tras las Fases 0 a 6, el proyecto cuenta con preparación documental y de entorno, contratos de datos estrictos, normalización segura, un núcleo local de inspección, una capa HTTP FastAPI sin estado y una regresión automatizada de entrega.

## Prioridad y objetivo de la versión 1

**Prioridad P0:** entregar una API local, sin estado y sin persistencia que inspeccione un único archivo multipart por solicitud. El resultado deberá informar metadatos de carga, tamaño, tipo de medio declarado, extensión, comprobaciones seguras del nombre y una huella de contenido segura.

**Exclusiones P0:** almacenamiento, autenticación, cargas múltiples, acceso por URL, análisis de contenido, detección de malware y Azure Blob. Azure Blob es una mejora P2 posterior, supeditada a que la ruta local esté aceptada y conservando esta como fallback.

## Estado actual de las fases

- [x] **Fase 0 — Preparación documental y estructural:** completada.
- [x] **Fase 1 — Contrato público y seguridad de entrada:** completada.
- [x] **Fase 2 — Entorno, calidad y límites operativos:** completada.
- [x] **Fase 3 — Contratos de datos y normalización segura:** completada.
- [x] **Fase 4 — Núcleo de inspección local:** completada.
- [x] **Fase 5 — Capa HTTP FastAPI:** completada.
- [x] **Fase 6 — Pruebas automatizadas y regresión:** completada.
- [x] **Fase 7 — Entrega, demostración y revisión final:** completada.
- [ ] **Fase 8 — Azure Blob y operación posterior:** pendiente.

## Dependencias entre fases

```text
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6 → Fase 7
                                  |                     |
                                  └──────→ Fase 5       └──→ Fase 7

Fase 8 depende de la aceptación de la versión 1
```

- La Fase 1 es la fuente de verdad para las interfaces, límites y errores de las Fases 3 a 6.
- La Fase 2 habilita la ejecución y comprobación de las fases de implementación.
- Las Fases 3 y 4 podrán avanzar en paralelo una vez estabilizados el contrato y el entorno.
- La Fase 5 depende de los contratos y del núcleo de inspección; la Fase 6 valida la integración completa.
- La Fase 7 consolida evidencia solo cuando la versión 1 haya superado todas las comprobaciones.

## Fase 0 — Preparación documental y estructural — Completada

**Objetivo:** reservar un espacio de trabajo escalable sin introducir código, pruebas ni configuración funcional.

**Entregables:**

- [README.md](README.md) con alcance, arquitectura, seguridad, despliegue y estructura.
- Este roadmap con prioridades, riesgos y secuencia.
- [docs/CONTRATO_API_V1.md](docs/CONTRATO_API_V1.md) como plantilla de decisión del contrato.
- Directorios vacíos [src](src), [tests](tests), [data/fixtures](data/fixtures), [data/expected](data/expected) y [assets](assets).

**Dependencias:** ninguna.

**Criterios de aceptación:** la estructura está enlazada desde su documentación, no contiene código de aplicación, configuraciones ejecutables, dependencias ni pruebas, y no altera proyectos ajenos.

## Fase 1 — Contrato público y seguridad de entrada — Completada, P0

**Objetivo:** definir un contrato HTTP versión 1 que permita implementar y probar sin inventar comportamiento.

**Entregables:** actualización de [docs/CONTRATO_API_V1.md](docs/CONTRATO_API_V1.md) con endpoint, formato multipart, campo del archivo, respuesta, errores, límites y ejemplos exclusivamente documentales.

**Estado alcanzado:** completada. El contrato v1 define `POST /api/v1/inspect`, `multipart/form-data`, un único campo `file`, un límite de 5 MiB de contenido, SHA-256 hexadecimal en minúsculas, representación del tipo de medio declarado, reglas de nombre/extensión y una envoltura uniforme de errores. La operación local no persiste, no interpreta el contenido y no integra Azure Blob.

**Decisiones técnicas bloqueantes:**

- **Cerrado:** ruta `POST /api/v1/inspect`, versión v1 y campo multipart obligatorio `file`.
- **Cerrado:** límite de 5.242.880 bytes de contenido; ausencia, multiplicidad y campos adicionales son validaciones 422; tamaño excedido es 413; multipart malformado es 400.
- **Cerrado:** SHA-256 sobre los bytes originales, codificado como 64 caracteres hexadecimales ASCII en minúsculas; identifica contenido, no detecta formato ni malware.
- **Cerrado:** respuesta con nombre recibido como dato, tamaño, tipo declarado opcional, extensión normalizada, comprobaciones de nombre y huella.
- **Cerrado:** se rechazan nombres vacíos, solo de espacios, con control Unicode, separadores, `.`/`..` o secuencia de traversal; las extensiones múltiples se informan como ambigüedad y no se bloquean.
- **Cerrado:** errores 400, 405, 413, 415, 422 y 500 con envoltura segura sin contenido, rutas, trazas ni nombres de archivo.

**Dependencias:** Fase 0.

**Riesgos y mitigaciones:** la ambigüedad de MIME o extensión se mitiga al describirlos expresamente como valor declarado y sufijo derivado, nunca como validación de contenido. El riesgo de consumo de memoria se reduce con el límite conservador de 5 MiB y el requisito de lectura por bloques para la implementación. La huella permite correlación; no se registrará ni persistirá por defecto.

**Criterios de aceptación:** completados mediante revisión documental. Una persona puede construir solicitudes, respuestas y pruebas de límite con el contrato; el documento fija ejemplos de archivo vacío, nombre inseguro y tamaño excedido, y explica explícitamente lo que la API no certifica.

**Verificación realizada:** revisión cruzada del contrato con el alcance de [README.md](README.md), la secuencia de fases y las convenciones FastAPI de los proyectos 10 y 11. No se ejecutaron pruebas ni herramientas de calidad: Fase 1 no añade código, dependencias, configuración ni suite automatizada. Esas verificaciones permanecen correctamente en las Fases 2 a 6.

**Pendientes y desviaciones:** no hay desviaciones. La implementación de los límites, el parseo multipart, la huella, los modelos, las respuestas HTTP y sus pruebas sigue pendiente y no se marca como entregada.

## Fase 2 — Entorno, calidad y límites operativos — Completada, P0

**Objetivo:** preparar una base Python/FastAPI reproducible y mínima antes de implementar.

**Entregables:** [requirements.txt](requirements.txt) declara FastAPI, Pydantic, Uvicorn y `python-multipart` para las capas posteriores, junto con Pytest, HTTPX, Ruff y MyPy. [pyproject.toml](pyproject.toml) concentra metadatos de Python 3.11+, los mismos rangos de ejecución, extras de desarrollo y configuración de Pytest, Ruff y MyPy. [`.gitignore`](.gitignore) excluye entornos, cachés, artefactos y archivos `.env`; [README.md](README.md) documenta la instalación mediante el manifiesto y los comandos de comprobación previstos.

**Decisión mínima de fase:** `python-multipart` se declara ahora porque FastAPI lo requerirá para aceptar el `multipart/form-data` fijado por el contrato, pero no se ha creado aún una ruta ni parseo multipart. El manifiesto [requirements.txt](requirements.txt), no la instalación editable, es la vía de instalación reproducible mientras no exista un paquete de aplicación en [src](src).

**Dependencias:** Fases 0 y 1.

**Riesgos y mitigaciones:** los rangos compatibles, compartidos entre ambos manifiestos, reducen incompatibilidades. El requisito multipart queda declarado desde el entorno, pero el límite de 5 MiB sigue siendo un requisito pendiente de implementar y probar en las Fases 4–6. No hay secretos, variables obligatorias ni servicios externos: no existe [`.env.example`](.env.example) en este proyecto porque aún no requiere configuración por variables de entorno; el patrón de exclusión queda preparado en [`.gitignore`](.gitignore).

**Criterios de aceptación:** completados para la preparación de fase. La coherencia de dependencias se comprobó con `python -m pip check`, que informó `No broken requirements found`; `python -m ruff check src tests` no informó incidencias; `python -m compileall src tests` terminó sin errores; y `git diff --check -- .` no detectó errores de espacios. Como no existen módulos Python ni pruebas en esta fase, `python -m pytest -q` terminó con `no tests ran` y código 5, y MyPy informó que no había archivos Python en `src`; estos diagnósticos confirman que no se ha adelantado implementación, no una suite aprobada.

**Pendientes y desviaciones:** no hay desviaciones de alcance. [README.md](README.md) conserva como vía documentada la instalación con [requirements.txt](requirements.txt) y los comandos de validación; no se ha verificado ni se presenta como necesaria una instalación editable. Aunque [pyproject.toml](pyproject.toml) contiene metadatos de construcción, todavía no hay un paquete de aplicación instalable en [src](src). No se añadieron módulos, endpoints, modelos, servicios, validadores, parseo multipart ni pruebas funcionales; permanecen pendientes en las Fases 3 a 6. La verificación de arranque con Uvicorn no aplica hasta la Fase 5.

## Fase 3 — Contratos de datos y normalización segura — Completada, P0

**Objetivo:** materializar los modelos y decisiones de seguridad del contrato sin exponer HTTP todavía.

**Entregables:** [src/schemas.py](src/schemas.py) aporta modelos Pydantic estrictos para respuestas correctas y errores; [src/filename_validation.py](src/filename_validation.py) aporta evaluación, validación y derivación de extensión puras. [tests/test_schemas.py](tests/test_schemas.py) y [tests/test_filename_validation.py](tests/test_filename_validation.py) cubren sus invariantes de contrato.

**Dependencias:** Fases 1 y 2.

**Estado alcanzado:** los modelos rechazan propiedades no declaradas y coerciones implícitas, limitan el tamaño representable a 5 MiB y fijan los códigos de error, la estructura de detalles y la huella SHA-256 hexadecimal. La validación preserva el nombre Unicode recibido sin usarlo como ruta, rechaza valores vacíos, de solo espacios, de más de 255 puntos de código, de control, con separadores o segmentos de traversal, y deriva la extensión y su ambigüedad de forma determinista.

**Riesgos y mitigaciones:** usar un nombre de carga como ruta o modificarlo de forma opaca. Se conserva como dato, no como ruta ni identificador de sistema; no se realiza normalización Unicode, resolución de rutas, detección de contenido ni acceso al sistema de archivos.

**Criterios de aceptación:** completados. Entradas límite y nombres hostiles producen evaluaciones o errores deterministas; los modelos rechazan campos y estados no permitidos por el contrato y exigen coherencia entre nombre, extensión e indicadores publicados.

**Verificación realizada:** `python -m pytest -q` aprobó 30 pruebas; `python -m ruff check src tests`, `python -m mypy src tests` y `python -m compileall -q src tests` terminaron sin incidencias. `python -m pip check` no se considera aprobado en el intérprete global por un conflicto preexistente y ajeno entre `playwright` y `pyee`; las dependencias declaradas para este proyecto se instalaron correctamente.

**Pendientes y desviaciones:** no hay desviaciones de alcance. El cálculo de tamaño y huella sobre bytes, la lectura por bloques, fixtures de inspección, multipart, endpoints FastAPI y pruebas HTTP quedan explícitamente en las Fases 4 a 6.

## Fase 4 — Núcleo de inspección local — Completada, P0

**Objetivo:** implementar una inspección pura, determinista, efímera y desacoplada de HTTP.

**Entregables:** [src/inspection.py](src/inspection.py) aporta el servicio local que obtiene tamaño, tipo declarado, extensión, comprobaciones de nombre y huella SHA-256. El fixture no sensible [data/fixtures/phase-4-sample.txt](data/fixtures/phase-4-sample.txt) y su respuesta [data/expected/phase-4-sample.json](data/expected/phase-4-sample.json) fijan una regresión controlada. [tests/test_inspection.py](tests/test_inspection.py) cubre el núcleo.

**Dependencias:** Fases 1, 2 y 3.

**Estado alcanzado:** `inspect_file` recibe un flujo binario y metadatos no confiables, valida primero el nombre heredado de la Fase 3 y recorre los bytes en bloques de 64 KiB. Calcula tamaño y SHA-256 sin persistir, abrir rutas, realizar red, registrar datos ni conservar el contenido. Rechaza más de 5 MiB antes de devolver una huella y construye únicamente `InspectionResponse` coherentes con el contrato.

**Riesgos y mitigaciones:** cargar archivos completos puede exceder recursos; la lectura se limita a bloques y usa una lectura centinela para detectar el byte que supera 5 MiB. La huella permite correlación; el servicio no la registra ni persiste. El nombre validado permanece como dato y nunca forma una ruta.

**Criterios de aceptación:** completados. El mismo contenido y metadatos definidos generan el mismo resultado; no hay red, disco de aplicación, persistencia, rutas construidas con el nombre ni estado compartido.

**Verificación realizada:** `python -m pytest -q` aprobó 39 pruebas; `python -m ruff check src tests`, `python -m mypy src tests` y `python -m compileall -q src tests` terminaron sin incidencias. Las pruebas cubren contenido conocido y vacío, determinismo, extensiones ambiguas, límite exacto y excedido, lectura acotada, nombre inválido previo a lectura, tipo declarado estricto y fixture versionado.

**Pendientes y desviaciones:** no hay desviaciones de alcance. El parseo multipart, la traducción a errores HTTP, rutas FastAPI y pruebas HTTP continúan explícitamente en las Fases 5 y 6.

## Fase 5 — Capa HTTP FastAPI — Completada, P0

**Objetivo:** exponer exclusivamente el contrato de inspección acordado mediante FastAPI y OpenAPI.

**Entregables:** [src/main.py](src/main.py) aporta la aplicación FastAPI, `POST /api/v1/inspect`, comprobación del tipo multipart y boundary, validación de cardinalidad/campos, adaptación de errores y metadatos OpenAPI. La ruta delega la validación de nombre, el límite por contenido y SHA-256 en [src/inspection.py](src/inspection.py). [tests/test_http_api.py](tests/test_http_api.py) cubre solicitudes válidas, archivo vacío, validaciones, multipart malformado, tipo no admitido, límite, OpenAPI y aislamiento entre solicitudes.

**Dependencias:** Fases 1 a 4.

**Estado alcanzado:** la respuesta correcta usa el contrato `InspectionResponse`; los errores 400, 405, 413, 415, 422 y 500 se traducen a la envoltura pública sin incluir el nombre, contenido ni detalles internos. La capa HTTP no persiste ni interpreta archivos y no duplica el cálculo de tamaño, huella o reglas de seguridad del núcleo.

**Riesgos y mitigaciones:** duplicar reglas en la ruta o aceptar tipos/volúmenes no definidos. La ruta queda limitada a transporte, parseo multipart, cardinalidad y adaptación de errores; el núcleo conserva la lectura acotada y la validación de datos. Las excepciones inesperadas se convierten en un error interno seguro.

**Criterios de aceptación:** completados. OpenAPI documenta la operación multipart exclusiva y las pruebas confirman formatos y códigos de solicitudes válidas e inválidas sin estado compartido ni almacenamiento de la carga.

**Verificación realizada:** `python -m pytest -q` aprobó 52 pruebas; `python -m ruff check src tests`, `python -m mypy src tests` y `python -m compileall -q src tests` terminaron sin incidencias. Se eliminaron los `__pycache__` y `.pyc` generados por la compilación; no se detectó `.coverage` dentro de `src` o `tests`, y `git diff --check -- projects/day-12-upload-inspector-api` no informó errores de espacios.

## Fase 6 — Pruebas automatizadas y regresión — Completada, P0

**Objetivo:** demostrar el contrato, la seguridad básica y la estabilidad de la implementación.

**Entregables:** las pruebas unitarias de las Fases 3 y 4, las pruebas HTTP de la Fase 5 y [tests/test_delivery.py](tests/test_delivery.py) completan la cobertura de entrega. Se reutilizan el fixture seguro [data/fixtures/phase-4-sample.txt](data/fixtures/phase-4-sample.txt) y el resultado esperado versionado [data/expected/phase-4-sample.json](data/expected/phase-4-sample.json), sin introducir datos sensibles.

**Dependencias:** Fases 2 a 5.

**Estado alcanzado:** la regresión de entrega compara la respuesta HTTP con el fixture versionado, acepta exactamente 5 MiB, conserva un tipo declarado ausente como `null`, preserva nombres Unicode seguros, informa extensiones ambiguas, convierte fallos inesperados en un error interno sin detalles de implementación y confirma el aislamiento de solicitudes después de un error. La suite existente cubre además archivo válido y vacío, ausencia y multiplicidad de archivos, tipos declarados, nombres hostiles, límite excedido, determinismo de la huella y multipart malformado.

**Riesgos y mitigaciones:** los tests usan únicamente bytes generados o fixtures locales controlados; no realizan red, persistencia ni acceso a rutas suministradas por el cliente. Las comprobaciones de errores verifican el sobre público y evitan aceptar filtraciones de nombres, contenido o detalles internos.

**Criterios de aceptación:** completados. La suite reproducible y la comparación con fixtures están aprobadas; `python -m compileall -q src tests`, `python -m pytest -q`, `python -m ruff check src tests` y `python -m mypy src tests` se ejecutan sin incidencias. La revisión de espacios, la limpieza de artefactos generados y el estado final del árbol se verifican antes del cierre de la fase.

## Fase 7 — Entrega, demostración y revisión final — Completada, P0

**Objetivo:** dejar una versión 1 comprensible, demostrable y segura para publicación.

**Entregables:** [README.md](README.md) se actualiza con el estado verificable de la versión 1 y [docs/GUIA_DE_ENTREGA.md](docs/GUIA_DE_ENTREGA.md) concentra instalación, comprobaciones reproducibles, demostración local breve, escenarios públicos y lista de cierre. La demostración usa exclusivamente [data/fixtures/phase-4-sample.txt](data/fixtures/phase-4-sample.txt) y su resultado esperado [data/expected/phase-4-sample.json](data/expected/phase-4-sample.json).

**Dependencias:** Fases 1 a 6.

**Estado alcanzado:** la guía inicia la aplicación localmente en `127.0.0.1`, envía el fixture seguro al único endpoint v1 y especifica los valores deterministas que se deben comprobar. Documenta el alcance y las exclusiones reales, los comandos de calidad, los errores públicos relevantes y la revisión de secretos, registros, referencias y artefactos. No se añadieron rutas, dependencias, configuración cloud ni cambios al contrato.

**Riesgos y mitigaciones:** la entrega evita datos reales y recuerda que nombres, bytes y huellas pueden tener impacto de privacidad. La aplicación no requiere secretos; [`.gitignore`](.gitignore) excluye `.env`, entornos y artefactos. Las referencias de ejecución permanecen locales y Azure Blob sigue fuera de la versión 1.

**Criterios de aceptación:** completados. El README, la guía y el contrato describen la misma operación `POST /api/v1/inspect`; la demostración no usa datos sensibles; las pruebas de las Fases 3 a 6 conservan la verificación automatizada de comportamiento. Las comprobaciones de compilación, pruebas, Ruff, MyPy y espacios se ejecutan antes del cierre, junto con la limpieza de artefactos y la revisión del árbol de trabajo.

## Fase 8 — Azure Blob y operación posterior — Pendiente, P2

**Objetivo:** evaluar inspección de objetos Azure Blob sin degradar la ruta local.

**Entregables previstos:** diseño de autenticación y permisos mínimos, configuración no versionada, prueba de conectividad, estrategia de errores y fallback local documentado.

**Dependencias:** Fase 7 y aceptación explícita de la versión 1.

**Riesgos y criterios de cambio:** credenciales, permisos, cuota, red o proveedor pueden fallar. Según la política raíz, si la integración no valida una petición/respuesta antes de T+30, se mantiene la demostración sobre el flujo local. Cualquier acceso a Blob requerirá políticas de retención, aislamiento de contenedores, control de acceso y revisión de exposición de datos.

**Criterios de aceptación:** la integración es estrictamente opcional, no almacena secretos en el repositorio, valida permisos mínimos y preserva la misma semántica de inspección o versiona las diferencias.

## Criterio de salida de la primera versión

La versión 1 está lista: las Fases 1 a 7 están aceptadas, con contrato cerrado, procesamiento local de un archivo, respuesta limitada al alcance, pruebas reproducibles, ausencia de persistencia y documentación congruente. Azure Blob y cualquier extensión quedan fuera de este criterio.
