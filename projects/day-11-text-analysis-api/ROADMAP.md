# Roadmap — API de análisis de texto

Este roadmap ordena el desarrollo de la API de análisis de texto. Las **Fases 0, 1, 2, 3, 4, 5, 6 y 7** están completadas; la Fase 8 permanece planificada.

## Dependencias entre fases

```text
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6 → Fase 7 → Fase 8
                                  └──────────────→ Fase 6
```

- La Fase 1 fija el contrato que condiciona modelos, lógica, pruebas y documentación.
- La Fase 2 proporciona el entorno necesario para desarrollar, probar y ejecutar las Fases 3 a 6.
- Las Fases 3 y 4 pueden avanzar en paralelo únicamente cuando las reglas de la Fase 1 estén estabilizadas; ambas deben finalizar antes de la capa HTTP de la Fase 5.
- La Fase 6 requiere la implementación de modelos, análisis y ruta HTTP.
- La Fase 7 consolida la evidencia generada en las fases anteriores.
- La Fase 8 depende de una versión 1 aceptada y publicada.

## Fase 0 — Preparación documental y estructural — Completada

**Objetivo:** dejar un espacio de trabajo coherente, escalable y libre de código funcional.

**Tareas:**

- Crear los directorios de aplicación, documentación, pruebas, fixtures, resultados esperados y activos.
- Reservar módulos Python para HTTP, contratos, análisis, tokenización y palabras clave.
- Documentar propósito, alcance, exclusiones, arquitectura, tecnologías, convenciones y criterios de aceptación.
- Crear la configuración mínima no ejecutable y el roadmap.
- Garantizar que todos los archivos Python estén completamente vacíos.

**Dependencias:** ninguna.

**Resultado esperado:** estructura inicial documentada, sin dependencias instaladas, sin lógica de negocio, sin endpoints y sin contenido en archivos Python.

## Fase 1 — Definición del contrato de la API — Completada

**Objetivo:** acordar un comportamiento público verificable antes de implementar modelos o rutas.

**Tareas:**

- Definir `POST /api/v1/analyze`, su tipo de contenido, estructura de solicitud, respuesta y códigos HTTP.
- Precisar campos de métricas: caracteres, caracteres sin espacios, palabras, frases, párrafos y tiempo de lectura.
- Precisar la representación de frecuencias de palabras y palabras clave, incluidos límites y orden de salida.
- Establecer reglas explícitas de tokenización, normalización, mayúsculas, puntuación, números, Unicode, espacios, frases, párrafos, palabras vacías y desempates.
- Definir restricciones de entrada, límites de tamaño y respuestas para contenido inválido o vacío.
- Publicar ejemplos exclusivamente documentales y criterios de compatibilidad en [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md).

**Dependencias:** Fase 0.

**Resultado esperado:** contrato HTTP versión 1 sin ambigüedades y aprobado como fuente de verdad.

**Estado:** completada. Se definió el contrato público en [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md), incluyendo `POST /api/v1/analyze`, JSON UTF-8, solicitud estricta con `text` de 1 a 10.000 caracteres, respuesta, métricas, frecuencia de palabras, palabras clave, límites, ordenación, normalización Unicode, tokenización, frases, párrafos y errores JSON. Se fijó el procesamiento local, sin estado y determinista; las palabras clave se limitan a cinco elementos después de excluir una lista cerrada de palabras vacías. El contrato prevalece sobre la petición de implementar modelos, lógica, endpoints y pruebas: esos entregables pertenecen expresamente a las Fases 3, 4, 5 y 6, que se conservan pendientes. Archivos modificados: [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md) y [`ROADMAP.md`](ROADMAP.md). Verificación: revisión manual de coherencia, cálculo documental del ejemplo y `python -m pytest -q`, cuyo resultado fue `no tests ran` (código de salida 5), como corresponde a la suite vacía que se implementará en la Fase 6.

## Fase 2 — Configuración de entorno y calidad — Completada

**Objetivo:** preparar una ejecución local reproducible antes de implementar.

**Tareas:**

- Declarar versiones compatibles de FastAPI, Pydantic, Uvicorn, Pytest y HTTPX en [`requirements.txt`](requirements.txt).
- Completar los metadatos de Python y de herramientas en [`pyproject.toml`](pyproject.toml).
- Decidir y documentar herramientas de formato, lint y comprobación de tipos solo si son necesarias para el alcance.
- Confirmar que no existen secretos, variables de entorno ni servicios externos obligatorios.
- Verificar instalación aislada, resolución de dependencias y comandos de calidad documentados.

**Dependencias:** Fases 0 y 1.

**Resultado esperado:** entorno local versionado, instalable y documentado sin incorporar reglas de análisis.

**Estado:** completada. Se declararon las dependencias de ejecución, pruebas y calidad con rangos compatibles en [`requirements.txt`](requirements.txt) y se configuraron metadatos, extras de desarrollo, Pytest, Ruff y MyPy en [`pyproject.toml`](pyproject.toml). El [`README.md`](README.md) documenta la instalación aislada, la instalación editable opcional y los comandos de verificación. No se añadieron secretos, variables de entorno obligatorias, servicios externos, modelos, reglas de análisis, endpoints ni pruebas funcionales. Verificación realizada en un entorno virtual aislado: `python -m pip check` informó `No broken requirements found`; `python -m pytest -q` informó `no tests ran` por la suite vacía reservada para la Fase 6; Ruff informó `All checks passed!`; MyPy informó `Success: no issues found in 7 source files`; y `compileall` finalizó sin errores. Una revisión de credenciales en los archivos propios, excluyendo `.venv`, no encontró asignaciones de contraseña, clave API ni secreto. Archivos modificados: [`requirements.txt`](requirements.txt), [`pyproject.toml`](pyproject.toml), [`README.md`](README.md) y [`ROADMAP.md`](ROADMAP.md).

## Fase 3 — Modelado y validación de datos — Completada

**Objetivo:** materializar los contratos de entrada y salida acordados.

**Tareas:**

- Implementar esquemas Pydantic para solicitud, métricas, elementos de frecuencia, palabras clave y respuesta.
- Aplicar límites, obligatoriedad y rechazo de campos no permitidos según el contrato.
- Definir errores de validación consistentes antes de llamar a la capa de análisis.
- Especificar y comprobar la serialización de todos los campos de salida.

**Dependencias:** Fases 1 y 2.

**Resultado esperado:** modelos de datos que protegen el contrato y aíslan entradas inválidas de la lógica de análisis.

**Estado:** completada. Se implementaron en [`src/schemas.py`](src/schemas.py) modelos Pydantic v2 estrictos para la solicitud, métricas, frecuencias, palabras clave, respuesta correcta y respuesta de error. Los modelos rechazan campos adicionales, exigen `text` como cadena de 1 a 10.000 caracteres, conservan el texto sin recortes, restringen métricas a enteros no negativos, recuentos de frecuencia a enteros positivos y palabras clave a un máximo de cinco. Los códigos de error se limitan al conjunto público del contrato y los detalles de error se serializan con una lista vacía por defecto. Se añadió [`tests/test_schemas.py`](tests/test_schemas.py) con cobertura de casos válidos, límites, tipos inválidos, campos extra, serialización y errores. Para que MyPy resuelva correctamente el espacio de nombres sin añadir archivos de paquete ajenos al alcance, se activó `explicit_package_bases` en [`pyproject.toml`](pyproject.toml). No se implementaron tokenización, métricas, palabras clave, rutas HTTP ni traducción de errores HTTP, que permanecen en las Fases 4 y 5; las pruebas de integración siguen reservadas para la Fase 6. Verificación: 14 pruebas pasaron; Ruff y MyPy finalizaron sin incidencias; `compileall` y la validación de TOML finalizaron correctamente; `git diff --check -- .` no informó errores; y la revisión de credenciales, excluyendo `.venv`, no encontró asignaciones sensibles. Archivos modificados: [`src/schemas.py`](src/schemas.py), [`tests/test_schemas.py`](tests/test_schemas.py), [`pyproject.toml`](pyproject.toml), [`README.md`](README.md) y [`ROADMAP.md`](ROADMAP.md).

## Fase 4 — Núcleo determinista de análisis — Completada

**Objetivo:** implementar métricas textuales puras e independientes de HTTP.

**Tareas:**

- Implementar tokenización y normalización conforme a las reglas de la Fase 1.
- Calcular caracteres, caracteres sin espacios, palabras, frases, párrafos y tiempo estimado de lectura.
- Calcular frecuencias ordenadas de forma estable y seleccionar palabras clave con reglas explícitas.
- Añadir fixtures representativos y resultados esperados para texto vacío, espacios, puntuación, Unicode, repeticiones, párrafos y empates.
- Evitar estado global, acceso de red, persistencia y dependencias de proveedores externos.

**Dependencias:** Fases 1, 2 y 3.

**Resultado esperado:** servicio de análisis puro, determinista y verificable de forma aislada.

**Estado:** completada. Se implementó el núcleo local y sin efectos secundarios en [`src/analyzer.py`](src/analyzer.py), [`src/tokenizer.py`](src/tokenizer.py) y [`src/keywords.py`](src/keywords.py), reutilizando los modelos de [`src/schemas.py`](src/schemas.py). El procesamiento normaliza palabras con NFC y minúsculas Unicode, conserva diacríticos, separa por cualquier carácter que no sea letra o dígito y calcula métricas, frases, párrafos y tiempo de lectura de acuerdo con el contrato. Las frecuencias se ordenan por recuento descendente y palabra ascendente; las palabras clave excluyen la lista cerrada de palabras vacías y se limitan a cinco. Se añadieron el fixture [`data/fixtures/contract-example.txt`](data/fixtures/contract-example.txt), su resultado versionado en [`data/expected/contract-example.json`](data/expected/contract-example.json) y pruebas unitarias en [`tests/test_analyzer.py`](tests/test_analyzer.py) para espacios, puntuación, Unicode, normalización, repeticiones, empates, frases, párrafos, límite de palabras clave, lectura y determinismo. No se implementaron rutas FastAPI, gestión HTTP de errores, persistencia, red ni estado compartido; esas responsabilidades permanecen en las Fases 5 y 6. Archivos modificados: [`src/analyzer.py`](src/analyzer.py), [`src/tokenizer.py`](src/tokenizer.py), [`src/keywords.py`](src/keywords.py), [`tests/test_analyzer.py`](tests/test_analyzer.py), [`data/fixtures/contract-example.txt`](data/fixtures/contract-example.txt), [`data/expected/contract-example.json`](data/expected/contract-example.json), [`README.md`](README.md) y [`ROADMAP.md`](ROADMAP.md).

## Fase 5 — Capa HTTP con FastAPI

**Objetivo:** exponer el núcleo de análisis mediante el contrato REST acordado.

**Tareas:**

- Crear la aplicación FastAPI y sus metadatos OpenAPI.
- Implementar exclusivamente `POST /api/v1/analyze`.
- Conectar esquemas, servicio de análisis y respuestas HTTP sin duplicar reglas lingüísticas en la ruta.
- Traducir fallos de validación y errores inesperados a respuestas coherentes, según contrato.
- Verificar documentación OpenAPI y aislamiento entre solicitudes.

**Dependencias:** Fases 1, 2, 3 y 4.

**Resultado esperado:** API local funcional con documentación interactiva y comportamiento consistente.

**Estado:** completada. Se creó la aplicación en [`src/main.py`](src/main.py) con metadatos OpenAPI y la única ruta pública `POST /api/v1/analyze`. La ruta valida [`AnalyzeRequest`](src/schemas.py), delega el resultado en [`analyze_text`](src/analyzer.py) y devuelve [`AnalyzeResponse`](src/schemas.py), sin duplicar las reglas del núcleo determinista. La capa HTTP exige `application/json` —incluido el parámetro opcional de charset— y traduce JSON malformado, errores de validación, método no permitido y errores inesperados a la envoltura JSON definida en el contrato. Se añadieron pruebas deterministas en [`tests/test_api.py`](tests/test_api.py) para respuestas correctas, charset, JSON malformado, payloads inválidos, tipo de contenido no admitido, métodos no permitidos y OpenAPI; las pruebas existentes confirman el aislamiento entre ejecuciones del núcleo. Verificación: `pytest -q` finalizó con `40 passed` (dos advertencias deprecadas originadas en dependencias de FastAPI/Starlette), Ruff informó `All checks passed!`, MyPy informó `Success: no issues found in 8 source files` y `compileall` finalizó sin errores. Archivos modificados: [`src/main.py`](src/main.py), [`tests/test_api.py`](tests/test_api.py), [`README.md`](README.md) y [`ROADMAP.md`](ROADMAP.md).

## Fase 6 — Pruebas automatizadas

**Objetivo:** demostrar el cumplimiento del contrato y prevenir regresiones.

**Tareas:**

- Implementar pruebas unitarias para tokenización, métricas, frecuencias, palabras clave y desempates.
- Implementar pruebas HTTP para solicitudes válidas, entradas inválidas, límites y estructura de respuestas.
- Ejecutar fixtures y comparar con resultados esperados versionados.
- Probar determinismo y ausencia de estado compartido entre ejecuciones o solicitudes.
- Ejecutar pruebas, comprobación de sintaxis y las herramientas de calidad adoptadas en la Fase 2.

**Dependencias:** Fases 2, 3, 4 y 5.

**Resultado esperado:** suite automatizada reproducible que cubre los flujos correctos y los fallos relevantes.

**Estado:** completada. Se consolidó la cobertura existente de esquemas, tokenización, métricas, frecuencias, palabras clave, desempates, errores HTTP y OpenAPI con las regresiones de extremo a extremo en [`tests/test_integration.py`](tests/test_integration.py). La nueva suite ejecuta el fixture [`data/fixtures/contract-example.txt`](data/fixtures/contract-example.txt) contra `POST /api/v1/analyze` y lo compara con [`data/expected/contract-example.json`](data/expected/contract-example.json); también verifica el límite válido de 10.000 caracteres, el rechazo de 10.001 caracteres sin invocar el análisis, la forma del esquema de los errores 400/415/405 y el aislamiento entre solicitudes. Las pruebas unitarias y HTTP previas permanecen sin cambios de comportamiento. Verificación: `pytest -q` pasó con la suite completa; Ruff, MyPy, `compileall`, `pip check`, la validación TOML y `git diff --check -- .` finalizaron sin incidencias. La revisión de patrones de credenciales en los archivos del proyecto no encontró secretos. Archivos modificados: [`tests/test_integration.py`](tests/test_integration.py), [`README.md`](README.md) y [`ROADMAP.md`](ROADMAP.md).

## Fase 7 — Documentación de entrega y demostración

**Objetivo:** hacer que el proyecto sea comprensible, reproducible y publicable.

**Tareas:**

- Actualizar el README con comandos realmente verificados de instalación, ejecución y pruebas.
- Completar contrato, decisiones de segmentación, límites y errores en [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md).
- Completar la guía reproducible de instalación, verificación y seguridad en [`docs/GUIA_DE_ENTREGA.md`](docs/GUIA_DE_ENTREGA.md).
- Preparar una demostración breve en [`assets`](assets) que muestre entrada, llamada y resultado.
- Revisar que no haya secretos, información sensible ni dependencias externas innecesarias.

**Dependencias:** Fases 1 a 6.

**Resultado esperado:** entrega autocontenida, demostrable, documentada y lista para publicar.

**Estado:** completada. Se actualizó [`README.md`](README.md) con el estado real, la estructura final y el acceso a la guía de entrega. El contrato público en [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md) dejó de describir una API futura y vincula su ejemplo estable con el fixture y resultado versionados. Se completó [`docs/GUIA_DE_ENTREGA.md`](docs/GUIA_DE_ENTREGA.md) con instalación, ejecución local, comprobaciones de calidad, límites y consideraciones de seguridad; se añadió la demostración reproducible [`assets/DEMO_HTTP.md`](assets/DEMO_HTTP.md) y las pruebas de entrega [`tests/test_delivery.py`](tests/test_delivery.py) para preservar sus referencias y comandos esenciales. La documentación confirma que la versión 1 no necesita secretos, persistencia ni dependencias externas. Verificación: la suite completa, Ruff, MyPy, `compileall`, `pip check`, validación TOML, `git diff --check -- .`, revisión de archivos ignorados y búsqueda de patrones de credenciales finalizaron sin incidencias propias del proyecto. Archivos modificados: [`README.md`](README.md), [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md), [`docs/GUIA_DE_ENTREGA.md`](docs/GUIA_DE_ENTREGA.md), [`assets/DEMO_HTTP.md`](assets/DEMO_HTTP.md), [`tests/test_delivery.py`](tests/test_delivery.py) y [`ROADMAP.md`](ROADMAP.md).

## Fase 8 — Despliegue y mejoras posteriores

**Objetivo:** evolucionar la versión 1 sin comprometer su núcleo determinista.

**Tareas:**

- Diseñar y automatizar un despliegue con configuración segura por entorno.
- Incorporar health checks, logs estructurados, métricas y observabilidad.
- Evaluar límites de solicitud, rate limiting, autenticación y políticas de retención antes de almacenar datos.
- Valorar idiomas configurables, listas de palabras vacías por idioma, detección de idioma, análisis de sentimiento o proveedores NLP opcionales con fallback local.
- Mantener compatibilidad de contrato o versionar públicamente los cambios incompatibles.

**Dependencias:** Fase 7 y aceptación completa de la versión 1.

**Resultado esperado:** backlog priorizado para operación y extensiones futuras, fuera del alcance de la primera entrega.