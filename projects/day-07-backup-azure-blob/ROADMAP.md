# Roadmap — Backup local y Azure Blob

## Objetivo de la primera versión

Planificar y construir una utilidad de backup acotada que realice una copia local verificable de un origen explícito y que pueda cargar esa copia a Azure Blob Storage de forma opcional. La entrega debe conservar una ruta local demostrable cuando las credenciales, permisos, cuota, red o el proveedor cloud no estén disponibles.

La información global solo establece que el proyecto pertenece a la categoría de almacenamiento cloud y que prevé Python y Azure SDK. Por ello, este roadmap no fija todavía la interfaz, el modelo de autenticación, la unidad exacta de backup, la estrategia de nombres, la compresión, la retención ni la restauración. Esas decisiones se resolverán mediante documentación antes de la implementación.

## Principios rectores

1. **El backup local es la base.** Debe ser verificable y no depender de Azure.
2. **Azure es opcional y no bloqueante.** La integración se abandona en favor del fallback si no se valida antes de T+30, conforme a [`docs/DAILY_WORKFLOW.md`](../../docs/DAILY_WORKFLOW.md).
3. **No se versionan secretos.** Cualquier valor sensible vivirá fuera del repositorio; las variables futuras se documentarán sin valores.
4. **Preservación antes que conveniencia.** La solución no deberá alterar el origen durante el flujo normal.
5. **Contrato antes de código.** Las reglas de copia, verificación, errores y límites se aprobarán antes de crear lógica, fixtures o configuración.
6. **Alcance atómico.** La primera versión excluye sincronización, automatización, retención avanzada y otros proveedores.

## Dependencias entre fases

```text
Fase 0 — Base documental y estructural
  → Fase 1 — Contrato de backup, seguridad y recuperación
    → Fase 2 — Escenarios, fixtures y referencias
      → Fase 3 — Núcleo de copia local y verificación
        → Fase 4 — Interfaz y flujo local completo
          → Fase 5 — Integración opcional con Azure Blob
            → Fase 6 — Pruebas, documentación, revisión y puesta en producción
```

La Fase 5 depende de que el flujo local esté validado, pero no es un bloqueo para el resultado mínimo: si Azure no supera su validación temprana, el cierre se basará en el flujo local y en la documentación explícita del fallback.

## Fases de trabajo

### Fase 0 — Base documental y estructural

**Estado:** completada en esta tarea.

**Objetivo:** aislar el proyecto del Día 07 y establecer su propósito, alcance, riesgos, estructura y evolución sin introducir comportamiento funcional.

**Alcance:**

- Crear únicamente directorios reservados para código, pruebas, datos, documentación, ejemplos y recursos de demo.
- Elaborar [`README.md`](README.md) y este [`ROADMAP.md`](ROADMAP.md).
- Documentar el fallback local obligatorio, la condición opcional de Azure y las ambigüedades aún abiertas.

**Entregables:**

- Estructura bajo [`projects/day-07-backup-azure-blob`](.).
- [`README.md`](README.md) y [`ROADMAP.md`](ROADMAP.md).

**Dependencias:** ninguna.

**Criterios de finalización:**

- No existen archivos de código, dependencias, configuraciones funcionales, scripts, fixtures, pruebas ni contenido ejecutable.
- La estructura solo contiene directorios vacíos y documentación Markdown.
- README y roadmap comparten el mismo alcance: fallback local y Azure Blob opcional.

**Validaciones necesarias:** revisión manual de estructura, contenido documental y cambios limitados al proyecto del Día 07.

### Fase 1 — Contrato de backup, seguridad y recuperación

**Estado:** completada.

**Objetivo:** resolver las decisiones indispensables para un flujo de backup seguro, pequeño y verificable antes de implementar.

**Alcance:**

- Definir la unidad de backup aceptada y la política para archivos, directorios, subdirectorios, enlaces y elementos no admitidos.
- Definir origen, destino local, conflictos, nombres, sobrescritura, permisos y rutas no admisibles.
- Establecer qué significa una copia correcta y el método de verificación apropiado para la v1.
- Decidir la interfaz mínima y sus entradas, salidas, estados y códigos de resultado.
- Precisar el comportamiento de errores, interrupciones y limpieza de operaciones incompletas.
- Delimitar el alcance de una posible restauración o confirmar que queda fuera de la v1.
- Definir el uso de Azure Blob, requisitos de configuración, forma de autenticación a evaluar y criterio de activación del fallback.
- Documentar restricciones de secretos, datos personales, registros y recursos de demostración.

**Entregables:** contrato de comportamiento y seguridad en [`docs/CONTRATO.md`](docs/CONTRATO.md), registro de decisiones y actualización de [`README.md`](README.md).

**Dependencias:** Fase 0 completada.

**Criterios de finalización:**

- Cada entrada admisible, resultado esperado y error relevante tiene una definición documental.
- La política de no modificación del origen y la verificación local están especificadas.
- La interfaz mínima está elegida sin añadir funcionalidades accesorias.
- La ruta Azure y el fallback tienen condiciones de uso claras.
- No se introduce código, configuración funcional, dependencia ni dato de prueba.

**Validaciones necesarias:** revisión de coherencia contra el registro global, la política de integraciones y los límites de tres horas del reto.

**Resultado:** [`docs/CONTRATO.md`](docs/CONTRATO.md) define la CLI futura `backup`, un único archivo o directorio regular como origen, un destino local existente, rechazo de enlaces y tipos especiales, publicación temporal, colisiones, relaciones de rutas, verificación por estructura, tamaño y SHA-256 efímero, y limpieza limitada de artefactos propios. También delimita restauración fuera de alcance, reserva Azure Blob para la Fase 5 con cadena de conexión y contenedor externos, y activa el fallback local cuando Azure no se valide o falle. [`README.md`](README.md) refleja esas decisiones. No se añadieron código, dependencias, configuración, fixtures, referencias, ejemplos ejecutables ni pruebas.

### Fase 2 — Escenarios, fixtures y resultados de referencia

**Estado:** completada.

**Objetivo:** transformar el contrato en escenarios seguros y reproducibles antes de crear lógica.

**Alcance:**

- Diseñar árboles de origen pequeños y no sensibles para los casos normales y de error.
- Preparar referencias para estructura copiada, resultados de verificación y diagnósticos permitidos.
- Cubrir casos de origen inexistente, destino no válido, conflicto, interrupción simulada y permisos cuando la plataforma lo permita.
- Describir escenarios de integración Azure mediante mocks, dobles o mecanismos equivalentes que no requieran una cuenta real.
- Crear trazabilidad entre requisitos, escenarios y resultados esperados.

**Entregables previstos:** fixtures no sensibles en [`data/fixtures`](data/fixtures), resultados de referencia en [`data/expected`](data/expected) y documentación de escenarios en [`docs`](docs).

**Dependencias:** contrato aprobado en Fase 1.

**Criterios de finalización:**

- Todos los requisitos y errores del contrato disponen de una cobertura de escenario definida.
- Ningún fixture, referencia o ejemplo contiene datos personales, secretos o credenciales.
- Los casos permiten comprobar que el origen se preserva y que la copia local puede verificarse.
- La estrategia de simulación remota evita dependencia de red y cuenta Azure para las pruebas.

**Validaciones necesarias:** revisión de privacidad, trazabilidad y reproducibilidad de los escenarios.

**Resultado:** [`docs/ESCENARIOS_FASE_2.md`](docs/ESCENARIOS_FASE_2.md) define escenarios locales de éxito, validación, conflictos, relaciones de rutas, enlaces, tipos especiales, permisos, interrupción, divergencia de verificación y publicación, además de cuatro escenarios Azure reservados para dobles futuros. [`data/fixtures/scenario-catalog.json`](data/fixtures/scenario-catalog.json) registra el catálogo declarativo y tres orígenes sintéticos; [`data/expected/local-copy-manifests.json`](data/expected/local-copy-manifests.json) registra las estructuras, tipos de raíz, rutas relativas, tamaños y propiedades de fallo esperadas, sin persistir hashes. Los fixtures versionados son texto inocuo y el directorio vacío se crea en la futura prueba para conservar su semántica. No se añadieron código, dependencias, configuración funcional, pruebas ni integración Azure.

### Fase 3 — Núcleo de copia local y verificación

**Estado:** completada.

**Objetivo:** implementar y comprobar el núcleo local sin acoplarlo a la interfaz ni a Azure.

**Alcance:**

- Implementar las validaciones de ruta y la planificación definida por el contrato.
- Implementar la operación local de copia de la unidad admitida.
- Implementar la verificación definida para la v1 y resultados estructurados.
- Aplicar las garantías de preservación, errores controlados y limpieza acordadas.
- Crear pruebas unitarias y de integración local basadas en los escenarios aprobados.

**Entregables técnicos previstos:** módulos bajo [`src`](src), pruebas bajo [`tests`](tests) y actualización de la documentación cuando el comportamiento aprobado necesite precisión.

**Dependencias:** Fase 2 completada.

**Criterios de finalización:**

- Los escenarios locales contratados se completan o fallan de forma controlada.
- La verificación distingue una copia correcta de una incompleta o incompatible según el contrato.
- El origen no se modifica en los escenarios de prueba.
- Las pruebas no requieren red, secretos ni Azure SDK.

**Validaciones necesarias:** ejecución local de pruebas, inspección de árboles de archivos y revisión de errores y limpieza.

**Resultado:** [`src/validation.py`](src/validation.py) valida rutas, tipos, enlaces/junctions, recorrido previo, permisos accesibles, conflictos y relaciones de árbol; [`src/local_backup.py`](src/local_backup.py) coordina copia temporal propia, verificación, publicación y limpieza limitada; [`src/verification.py`](src/verification.py) genera manifiestos efímeros y compara tipo, estructura, tamaño y SHA-256. [`tests/test_local_backup.py`](tests/test_local_backup.py) cubre los tres éxitos de referencia, validaciones, conflicto/repetición segura, relaciones de rutas, enlaces cuando el entorno los admite, fallos inyectados de copia/verificación/publicación, preservación del origen y el límite Azure. La ejecución estándar usa solo Python y la biblioteca estándar, sin red, secretos ni SDK; está documentada en [`docs/VERIFICACION_FASE_3.md`](docs/VERIFICACION_FASE_3.md). La CLI permanece expresamente pendiente de la Fase 4.

### Fase 4 — Interfaz y flujo local completo

**Estado:** completada.

**Objetivo:** exponer la capacidad local mediante la interfaz mínima definida y producir una experiencia verificable de extremo a extremo.

**Alcance:**

- Implementar el punto de entrada y el formato de solicitud aprobados.
- Conectar validación, copia, verificación y comunicación de resultados.
- Tratar argumentos o solicitudes inválidas, errores previsibles e interrupciones sin mensajes ambiguos ni datos sensibles.
- Elaborar guía de uso local y una demostración basada en datos de ejemplo no sensibles.

**Entregables técnicos y documentales previstos:** interfaz futura en [`src`](src), pruebas de flujo en [`tests`](tests), guía en [`examples`](examples), documentación operativa en [`docs`](docs) y recurso de demo en [`assets`](assets).

**Dependencias:** Fase 3 completada.

**Criterios de finalización:**

- Una persona puede ejecutar y verificar el backup local siguiendo la documentación.
- Los resultados distinguen éxito, fallo y condiciones no admitidas conforme al contrato.
- Las pruebas cubren el flujo principal y los errores prioritarios.
- La demostración local no contiene secretos ni depende de Azure.

**Validaciones necesarias:** ejecución limpia desde una copia del repositorio, guion manual reproducible y revisión de documentación.

**Resultado:** [`src/main.py`](src/main.py) implementa la CLI contratada `python src/main.py backup <SOURCE_PATH> <DESTINATION_DIRECTORY> [--azure]` y delega el trabajo local en el núcleo de Fase 3. La CLI traduce éxitos a código `0`, errores de sintaxis a `2`, y fallos locales o interrupciones a `1`, sin mostrar trazas, hashes, contenido, secretos ni rutas temporales. La solicitud `--azure` conserva la copia local publicada y comunica explícitamente el fallback, sin SDK, configuración ni red; el adaptador remoto continúa reservado para Fase 5. [`tests/test_cli.py`](tests/test_cli.py) cubre el flujo por subproceso, rutas relativas, archivos, directorios anidados, directorios vacíos, errores de uso, fallos locales, conflictos, interrupciones y fallback. [`examples/USO.md`](examples/USO.md) ofrece un guion reproducible con fixtures sintéticos, y [`docs/VERIFICACION_FASE_4.md`](docs/VERIFICACION_FASE_4.md) documenta las salidas, límites y comprobaciones.

### Fase 5 — Integración opcional con Azure Blob

**Estado:** completada. El adaptador aislado está validado con dobles y la ruta real autorizada se comprobó el 2026-09-06 mediante una carga controlada de un fixture, con configuración externa no expuesta.

**Objetivo:** añadir el destino Azure Blob solo si aporta valor a la demo y puede validarse sin comprometer el flujo local.

**Alcance:**

- Añadir un adaptador aislado de Azure Blob según el contrato y la decisión de autenticación aprobada.
- Declarar las dependencias estrictamente necesarias y, si aplica, documentar variables opcionales sin valores.
- Verificar una conexión o transferencia real dentro de la ventana T+30.
- Traducir fallos de credenciales, permisos, cuota, red o proveedor a resultados controlados.
- Mantener pruebas remotas aisladas mediante mocks o dobles y sin secretos en el repositorio.

**Entregables técnicos y documentales previstos:** adaptador remoto bajo [`src`](src), dependencias y archivo de variables de ejemplo solo si están justificados, pruebas de integración aislada en [`tests`](tests) y documentación de la ruta Azure/fallback en [`docs`](docs) y [`README.md`](README.md).

**Dependencias:** Fase 4 completada, configuración Azure disponible de manera segura y decisión de continuar tras la validación temprana.

**Criterios de finalización:**

- La carga remota está validada o se ha descartado explícitamente antes de T+30.
- Un fallo remoto no invalida ni borra una copia local correcta.
- Los secretos no aparecen en código, pruebas, ejemplos, documentación, salida ni control de versiones.
- La suite estándar permanece reproducible sin conectividad ni una cuenta Azure.

**Validaciones necesarias:** pruebas simuladas y revisión de configuración y secretos. Una transferencia real mínima es una comprobación operativa explícita para un entorno autorizado; no es requisito de la suite local. El 2026-09-04 se verificaron de forma no sensible la instalación del SDK y una sesión Azure CLI. El 2026-09-06 se verificó la ruta contractual mediante `AZURE_STORAGE_CONNECTION_STRING` y `AZURE_STORAGE_CONTAINER_NAME` disponibles solo en la sesión local.

**Resultado:** [`src/azure_blob.py`](src/azure_blob.py) encapsula la carga Azure mediante importación diferida del SDK y una fábrica inyectable. La CLI valida la configuración estricta antes de crear contenido local cuando se solicita `--azure`; una configuración ausente devuelve `1` sin artefactos. Tras una publicación local correcta, los fallos remotos conservan el backup local y devuelven `0` con un diagnóstico seguro. La convención aprobada es `backups/<SOURCE_BASENAME>` para archivos y `backups/<SOURCE_BASENAME>/<RELATIVE_POSIX_PATH>` para directorios; los directorios vacíos no generan blobs. [`tests/test_azure_blob.py`](tests/test_azure_blob.py) usa dobles sin red y [`requirements.txt`](requirements.txt) declara el SDK opcional. La ejecución del 2026-09-04 completó 24 pruebas y compilación, confirmó que las dos variables requeridas estaban ausentes y ejercitó el rechazo estricto de `--azure` sin mutación local. El 2026-09-06, con las dos variables requeridas fuera del repositorio, una ejecución controlada con `data/fixtures/regular-file/sample-note.txt` confirmó una copia local verificada y la carga correcta de un blob. No se documentan secretos ni identificadores de recursos. La evidencia y el procedimiento reproducible sin secretos están en [`docs/VERIFICACION_FASE_5.md`](docs/VERIFICACION_FASE_5.md).

### Fase 6 — Pruebas, documentación, revisión y puesta en producción

**Estado:** completada tras la revisión final de pruebas, documentación, secretos y artefactos del 2026-09-06.

**Objetivo:** cerrar una entrega publicable que sea comprensible, demostrable y coherente con el reto.

**Alcance:**

- Ejecutar pruebas unitarias, integración local, regresión de escenarios y validaciones del adaptador remoto si fue incluido.
- Revisar preservación del origen, manejo de fallos, cobertura de fallback y ausencia de secretos.
- Completar el README operativo, contrato, guía de uso, límites, recuperación y demo.
- Comprobar consistencia entre comportamiento, pruebas, fixtures, referencias y documentación.
- Preparar recurso visual breve y materiales de publicación según las convenciones del repositorio.
- Realizar verificación final y publicar únicamente el alcance efectivamente implementado.

**Entregables previstos:** suite final, documentación actualizada, demo en [`assets`](assets), enlace o registro de publicación y actualización del índice global cuando corresponda.

**Dependencias:** Fase 4 completada; Fase 5 solo si Azure se incluyó finalmente.

**Criterios de finalización:**

- El flujo local principal funciona y puede demostrarse sin Azure.
- Si Azure fue incluido, su fallback está documentado y verificado.
- La documentación identifica requisitos, límites, configuración opcional, recuperación y riesgos reales.
- No hay secretos, datos personales ni archivos temporales no deseados versionados.
- La entrega satisface la definición de terminado del reto aplicable en [`docs/DAILY_WORKFLOW.md`](../../docs/DAILY_WORKFLOW.md).

**Validaciones necesarias:** suite completa, revisión manual de un flujo desde copia limpia, revisión de secretos, revisión de cambios y comprobación final de demo/publicación.

**Resultado:** se revisaron contrato, implementación, pruebas, fixtures, README, ejemplos y evidencias de las fases anteriores. La ruta local continúa demostrable sin Azure; la ruta remota se validó de forma controlada sin registrar configuración sensible. La suite local, la compilación y las comprobaciones de cambios, secretos y artefactos se ejecutan como cierre final antes de publicación.

## Estrategia de pruebas y calidad

| Área | Verificación prevista |
|---|---|
| Contrato | Trazabilidad de requisitos, entradas, resultados y errores. |
| Rutas y seguridad | Entradas no admitidas, conflictos, permisos y preservación del origen. |
| Copia local | Estructura, contenido y criterios de verificación aprobados. |
| Recuperación | Limpieza y mensajes ante operaciones incompletas, según contrato. |
| Azure Blob | Adaptador aislado, credenciales ausentes, errores de proveedor y degradación al fallback. |
| Regresión | Comparación con fixtures y resultados no sensibles. |
| Documentación | Coherencia entre README, contrato, ejemplos, comportamiento y demo. |

La ejecución de calidad no dependerá de Azure para la ruta normal de pruebas. Las comprobaciones con recursos reales serán explícitas, opcionales y nunca una condición para ejecutar la suite local.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| La definición de backup es ambigua | Aprobar contrato antes de implementar o crear datos de prueba. |
| Azure no se puede usar a tiempo | Activar el fallback local antes de T+30 y documentar la decisión. |
| Secretos en archivos o salidas | Usar variables no versionadas, inspección de cambios y pruebas/documentación sin valores reales. |
| El origen se altera durante una copia fallida | Diseñar preservación, operaciones controladas y pruebas específicas antes de integrar Azure. |
| La verificación no detecta copias incompletas | Definir criterios de integridad apropiados y referencias en la Fase 1. |
| El alcance deriva hacia sincronización o automatización | Mantener esas capacidades fuera de la v1 y aplicar la puerta T+90. |
| Las pruebas son frágiles por red o cloud | Aislar el proveedor mediante mocks o dobles y hacer local la suite estándar. |
| Permisos o rutas varían por plataforma | Declarar plataformas soportadas y probar los límites posibles en el entorno objetivo. |

## Decisiones pendientes tras la Fase 1

- Alternativas de autenticación, como identidad administrada, y compatibilidad de entornos Azure.
- Estrategia de reintentos, clasificación detallada de errores del SDK y telemetría.
- Metadatos que una versión futura pueda preservar o verificar.
- Copias incrementales, versionado, retención, compresión, cifrado y deduplicación.
- Restauración explícita y verificación posterior de una restauración.
- Compatibilidad formal con rutas de red, sistemas de archivos especiales y atributos de plataforma.

La interfaz, la unidad respaldada, el destino, las colisiones, la verificación local, la recuperación limitada y las variables Azure previstas ya se resolvieron en [`docs/CONTRATO.md`](docs/CONTRATO.md). Las decisiones restantes no deben introducirse de forma implícita en las fases posteriores.