# Contrato v1 — Backup local, verificación y Azure Blob opcional

## Propósito

Este contrato fija el comportamiento de la primera versión del proyecto **Backup local y Azure Blob** antes de crear fixtures, dependencias, configuración o lógica funcional. La v1 realizará una copia local verificable de un único origen explícito hacia un directorio de destino local existente. Azure Blob Storage será un destino remoto opcional y posterior: nunca sustituye la copia local ni bloquea la demostración.

Las decisiones de este documento son deliberadamente pequeñas para respetar el reto de tres horas y la política de integraciones del repositorio. Cualquier comportamiento no definido aquí queda fuera de la v1.

## Principios de seguridad, preservación y alcance

- Una operación procesa exactamente un origen local y un directorio de destino local.
- La operación normal no modifica, mueve, elimina, renombra ni comprime el origen.
- La copia local se prepara en una ubicación temporal controlada dentro del destino y solo se publica cuando la verificación termina correctamente.
- Sin `--azure`, la copia local es obligatoria. Con `--azure`, la configuración remota se valida antes de cualquier mutación local; tras esa validación, la carga ocurre después de una copia local correcta y no puede reemplazarla.
- La v1 no usa red, credenciales, dependencias de terceros ni servicios externos para el flujo local.
- No se versionan secretos, datos personales ni contenido real de backups en documentación, fixtures, referencias, ejemplos, pruebas o recursos de demo.
- Los diagnósticos describen rutas y condiciones operativas, pero nunca valores de configuración sensibles.
- No hay sincronización, programación, observación de cambios, retención, deduplicación, cifrado propio, múltiples proveedores ni restauración automatizada.

## Unidad de backup admitida

La v1 admite una única ruta de origen que represente exactamente uno de estos tipos:

| Tipo de origen | Admisible | Contenido que se copia |
|---|:---:|---|
| Archivo regular | Sí | El archivo y sus bytes. |
| Directorio regular | Sí | El directorio, todos sus subdirectorios y los archivos regulares descendientes. |
| Directorio vacío | Sí | El directorio vacío. |
| Enlace simbólico o junction | No | No se sigue ni se copia. |
| Dispositivo, FIFO, socket u otro tipo especial | No | No se copia. |

Para un directorio, cualquier enlace simbólico, junction o elemento especial encontrado durante el recorrido invalida toda la solicitud antes de copiar contenido. La v1 no intenta resolver enlaces ni ofrecer una opción para seguirlos. Esta regla evita escapes de árbol, ciclos y diferencias de comportamiento entre Windows y otros sistemas.

La operación preserva la estructura relativa de directorios y los bytes de cada archivo. La v1 no promete preservar permisos, propietario, ACL, atributos de plataforma, fechas, enlaces duros, flujos alternativos de datos, xattrs ni otros metadatos del sistema de archivos.

## Rutas y destino local

La interfaz futura recibe rutas explícitas, que se interpretan mediante las convenciones de la plataforma. Las rutas relativas son admisibles y se resuelven respecto del directorio de trabajo de la ejecución. Antes de operar, la implementación futura deberá obtener una representación normalizada y comprobar las condiciones de este contrato.

| Elemento | Regla contractual |
|---|---|
| Origen | Debe existir, ser accesible para lectura y ser un archivo o directorio regular admitido. |
| Destino | Debe existir, ser un directorio regular accesible para crear contenido y no ser enlace simbólico o junction. |
| Nombre de la copia | Es el nombre base del origen, sin transformaciones ni marcas temporales. |
| Ubicación final | Es el hijo directo `<DESTINATION_DIRECTORY>/<SOURCE_BASENAME>`. |
| Conflicto | Si ya existe una entrada con esa ubicación final, la operación falla y no la modifica. |
| Igualdad de rutas | Origen y ubicación final no pueden representar la misma ubicación. |
| Recursión | Cuando el origen es directorio, el destino no puede estar dentro de su árbol; tampoco puede ser ancestro del origen. |
| Permisos | Falta de lectura en el origen, de exploración en un directorio o de creación/publicación en el destino es un error controlado. |

No se admiten destino inexistente, rutas de red o nube con semántica no verificable, comodines, múltiples orígenes, archivos de lista, entrada estándar ni una ruta de salida que sustituya directamente al origen. La implementación podrá aceptar rutas de red del sistema únicamente si las APIs locales las tratan como rutas regulares y si el contrato completo puede verificarse; la primera suite de la v1 no dependerá de ellas.

## Plan, copia y publicación segura

La operación futura tendrá tres etapas visibles para el diseño interno, aunque la interfaz no tiene que exponerlas como subcomandos:

1. **Planificación y validación:** comprobar tipo de origen, recorrido admisible, destino, colisiones y relaciones entre rutas antes de crear la copia final.
2. **Copia aislada:** construir una copia temporal como hija del directorio de destino. El nombre temporal debe ser inequívocamente interno, no colisionar con la ubicación final y no ser presentado como backup terminado.
3. **Verificación y publicación:** verificar la copia temporal; únicamente si la verificación es correcta, publicar el directorio o archivo temporal en la ubicación final mediante la operación más segura disponible dentro del mismo sistema de archivos.

Si falla la validación, la copia, la verificación o la publicación, la ubicación final no debe aparecer ni modificarse. La implementación intentará eliminar solo el artefacto temporal que haya creado para esa operación. Si la limpieza falla, comunicará una advertencia de limpieza sin borrar, alterar ni inspeccionar otras rutas del destino. No se debe eliminar una ubicación final preexistente para completar una operación.

La v1 no garantiza atomicidad frente a apagado del sistema, caída del proceso, antivirus, cambios concurrentes o semánticas particulares de sistemas de archivos. El contrato exige reducir la ventana de publicación y no presentar como éxito un resultado cuya verificación no haya concluido.

## Definición de copia correcta y verificación local

Una copia local es correcta solamente si, después de copiar y antes de publicar, se cumplen todas estas condiciones:

1. La raíz temporal tiene el mismo tipo contractual que el origen: archivo regular o directorio regular.
2. Para un directorio, el conjunto de rutas relativas de directorios y archivos regulares coincide exactamente entre origen y copia; los directorios vacíos deben estar presentes.
3. Para cada archivo regular correspondiente, el tamaño en bytes coincide.
4. Para cada archivo regular correspondiente, el resumen SHA-256 calculado sobre los bytes completos coincide.
5. La copia no contiene enlaces simbólicos, junctions ni elementos especiales.
6. La lectura y el resumen del origen y de la copia finalizan sin errores controlables.

SHA-256 se usa exclusivamente para comprobar igualdad de bytes durante una única operación local. No se presenta como cifrado, control de acceso, firma, mecanismo de deduplicación ni garantía contra cambios posteriores. Los resúmenes no se persisten, no se envían a Azure, no se muestran por defecto y no son parte del nombre de backup.

La v1 detecta los cambios de origen observables durante su lectura mediante la verificación anterior. Si el origen cambia de forma que cause diferencia, desaparición, error de lectura o cambio de estructura, la operación falla y no publica la copia. No puede garantizar una instantánea coherente frente a escrituras concurrentes que produzcan una coincidencia indetectable; por ello, el origen debe permanecer estable durante la operación para una garantía práctica de consistencia.

## Interfaz de línea de comandos definida

La interfaz futura tendrá un único subcomando y esta forma:

```text
python src/main.py backup <SOURCE_PATH> <DESTINATION_DIRECTORY> [--azure]
```

| Elemento | Obligatorio | Comportamiento definido |
|---|:---:|---|
| `backup` | Sí | Solicita una única operación de backup v1. |
| `<SOURCE_PATH>` | Sí | Ruta explícita a un archivo o directorio local admisible. |
| `<DESTINATION_DIRECTORY>` | Sí | Directorio local existente que contendrá la copia final. |
| `--azure` | No | Solicita la carga remota posterior solo cuando la integración de Fase 5 haya sido validada. |
| Argumentos adicionales u opciones desconocidas | No permitidos | Producen un mensaje de uso y no crean contenido. |

Sin `--azure`, la operación solo realiza el flujo local. Con `--azure`, antes de crear una copia temporal o publicar contenido local se validan las dos variables de configuración remota obligatorias. Si están presentes, la copia local y su verificación siguen siendo obligatorias; la carga remota se intentará únicamente después de publicar el backup local. No habrá confirmación interactiva, modo dry-run, selección de perfiles, lectura por entrada estándar, batch, compresión, restauración, borrado ni salida a archivo.

Esta decisión adopta una CLI de Python por ser la interfaz mínima y coherente con el stack del repositorio. Es una definición contractual: el comando no existe todavía y no debe invocarse hasta la Fase 4.

## Resultados, diagnósticos y códigos de salida

La representación interna futura deberá separar el estado local del estado remoto. No debe incluir secretos, cadenas de conexión, tokens, contenido de archivos, hashes, ni rutas temporales en la salida normal.

| Situación | Salida estándar prevista | Salida de error prevista | Código |
|---|---|---|:---:|
| Copia local y verificación correctas sin `--azure` | Confirmación estable de backup local y ruta final. | Vacía. | `0` |
| Copia local correcta y carga Azure correcta | Confirmación estable de ambos destinos, sin secretos. | Vacía. | `0` |
| Argumentos incompletos, subcomando u opción inválidos | Vacía. | Mensaje de uso accionable. | `2` |
| Origen o destino no admisible, conflicto, relación de rutas no permitida o permiso insuficiente | Vacía. | Diagnóstico breve de entrada o destino. | `1` |
| Error durante recorrido, copia, verificación, publicación o limpieza | Vacía. | Diagnóstico breve sin traza por defecto. | `1` |
| `--azure` solicitado sin configuración remota válida | Vacía. | Diagnóstico remoto breve; no crea ni publica contenido local. | `1` |
| Azure falla después de un backup local correcto | Confirmación del backup local. | Diagnóstico remoto breve y activación del fallback. | `0` |

El código `0` con `--azure` indica que la configuración remota era válida y que el objetivo obligatorio —backup local verificado— ha terminado correctamente, incluso cuando un fallo remoto posterior haya activado el fallback. La ausencia o el valor vacío de cualquiera de las variables Azure requeridas devuelve `1` antes de tocar el destino local. La salida debe identificar inequívocamente que Azure no se completó para no confundir el fallback con una réplica remota. Un fallo local siempre devuelve `1`, aunque se haya solicitado Azure, porque no puede iniciarse ni declararse correcta la ruta remota.

Los errores previsibles no mostrarán trazas internas, rutas temporales, detalles de proveedores ni textos de excepción que puedan contener datos sensibles. La ruta explícita de origen o destino puede mostrarse en un diagnóstico si es necesaria para corregir la solicitud; la implementación no debe expandirla con listados de contenido.

## Azure Blob Storage: condición opcional y fallback

Azure Blob no forma parte del flujo ejecutable de esta fase. Se reserva para la Fase 5 y solo podrá añadirse si se validan una conexión y una transferencia antes de T+30, conforme a [`docs/DAILY_WORKFLOW.md`](../../../docs/DAILY_WORKFLOW.md). Si no ocurre, la integración se abandona para la entrega del día y la copia local verificada es el resultado final.

Si se implementa, la ruta remota tendrá estas reglas:

- La solicitud explícita `--azure` habilita el intento; nunca habrá carga automática.
- La autenticación usa una cadena de conexión proporcionada fuera del repositorio mediante la variable `AZURE_STORAGE_CONNECTION_STRING`.
- El contenedor se indica mediante `AZURE_STORAGE_CONTAINER_NAME`; ambas variables deben existir y no estar vacías antes de crear la copia local. Su ausencia es un error controlado con código `1`, sin artefactos locales.
- No se crean valores de ejemplo funcionales, secretos ficticios ni archivos `.env`. El archivo [`.env.example`](../.env.example) de Fase 5 describe las variables sin valores.
- La dependencia declarada es `azure-storage-blob` y el SDK se importa de forma diferida: la ruta local no necesita instalarlo ni puede abrir red durante la importación.
- Los blobs usan el prefijo fijo `backups/`. Para un archivo, el nombre es `backups/<SOURCE_BASENAME>`; para un directorio, cada archivo regular publicado se carga como `backups/<SOURCE_BASENAME>/<RELATIVE_POSIX_PATH>`. Los directorios vacíos no generan blobs ni marcadores: la carga remota correcta de un árbol sin archivos informa cero blobs. No se sobrescriben blobs ni se eliminan objetos remotos en v1.
- Un error de credenciales, permisos, contenedor, cuota, red, proveedor o transferencia después de publicar la copia local activa el fallback y no altera ni elimina ese backup local correcto.
- Las pruebas habituales usan mocks o dobles; una cuenta Azure real no es requisito para la suite local.

## Restauración y capacidades excluidas

La v1 no ofrece subcomando, automatización ni garantía de restauración. La existencia y la verificación de una copia local son el límite de recuperación de la primera versión. Una fase futura podría definir una restauración explícita hacia una ubicación nueva y vacía, con validación equivalente, pero no puede sobreescribir un origen ni añadirse implícitamente.

También quedan fuera de alcance: historial, retención, limpieza de backups, sincronización bidireccional, copias incrementales, deduplicación, compresión, cifrado de contenido, protección con contraseña, blobs de archivo, restauración desde Azure, acceso a varios contenedores y soporte para otros proveedores cloud.

## Restricciones de secretos, datos y registros

- Nunca se almacenan ni muestran cadenas de conexión, tokens, claves, SAS, credenciales de cuenta ni archivos `.env`.
- Los nombres y el contenido de los archivos reales del origen no se añaden a recursos versionados, ejemplos, fixtures, snapshots, aserciones ni demostraciones.
- Los logs futuros no incluirán secretos, contenido de archivos, hashes, listados completos de árboles ni rutas temporales.
- Los fixtures de Fase 2 usarán árboles sintéticos con contenido inocuo y nombres genéricos; las referencias registrarán solo las propiedades necesarias para verificar el contrato.
- La documentación puede referirse a nombres de variables de entorno, rutas simbólicas y nombres de argumentos, pero no a valores de entorno reales o con apariencia de secreto.
- No se transmite contenido a Azure a menos que `--azure` se solicite explícitamente y la integración haya sido validada.

## Criterios de aceptación de Fase 1

- La unidad admisible, el tratamiento de directorios, archivos, enlaces y tipos especiales está definido sin ambigüedad.
- Origen, destino, relaciones de ruta, nombre final, colisiones, permisos y rutas no admisibles tienen un resultado contractual.
- La copia correcta y la verificación local especifican estructura, tamaños y SHA-256 sin persistir resúmenes.
- La preservación del origen, la publicación segura, los fallos y la limpieza de temporales están delimitados.
- La CLI, sus entradas, estados, salidas y códigos de retorno están definidos sin implementar el comando.
- La ruta Azure, su autenticación prevista, sus variables futuras y su fallback local tienen condiciones de activación claras.
- Restauración, automatización y capacidades no esenciales están explícitamente fuera de la v1.
- La documentación prohíbe secretos y datos reales en recursos versionados.
- Esta fase no añade código, dependencias, configuración funcional, fixtures, referencias, ejemplos ejecutables ni pruebas.

## Decisiones aplazadas

- Alternativas de autenticación, como identidad administrada, y compatibilidad de entornos Azure.
- Estrategia de reintentos, clasificación detallada de errores del SDK y telemetría.
- Metadatos que una versión futura pueda preservar o verificar.
- Copias incrementales, versionado, retención, compresión, cifrado y deduplicación.
- Restauración explícita y verificación posterior de una restauración.
- Compatibilidad formal con rutas de red, sistemas de archivos especiales y atributos de plataforma.
