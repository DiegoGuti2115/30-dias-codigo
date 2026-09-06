# Día 07 — Backup local y Azure Blob

> Microproyecto del reto **30 Días, 30 Proyectos**. Las fases 0 a 5 están completadas: estructura, contrato, referencias, núcleo local, CLI y adaptador Azure Blob aislado. La integración real requiere configuración local no versionada y no se valida mediante la suite estándar.

## Propósito y contexto

Este proyecto corresponde al Día 07 del reto y aborda el problema de disponer de una copia de respaldo de un origen local con un destino remoto opcional en Azure Blob Storage. Se enmarca en la categoría de almacenamiento cloud y prevé Python y Azure SDK como tecnologías de referencia, según el registro global en [`README.md`](../../README.md).

El reto exige entregas atómicas y con un límite operativo de tres horas. Por ello, la primera versión se planificará como una utilidad de backup deliberadamente acotada, verificable y recuperable si el servicio cloud no está disponible.

## Objetivos de la primera versión

La versión inicial incluye:

- Seleccionar un origen local explícito para una operación de backup acotada.
- Preparar y ejecutar una copia local verificable como ruta mínima de continuidad.
- Permitir, de forma opcional, la carga de la copia resultante a Azure Blob Storage cuando la integración esté validada.
- Comunicar el resultado de cada destino y los errores previsibles sin exponer secretos.
- Conservar una demostración reproducible mediante recursos locales cuando Azure no pueda utilizarse.

La ruta local y el adaptador Azure opcional están implementados. La transferencia real permanece condicionada a la autenticación autorizada por el contrato y disponible fuera del repositorio.

## Alcance aprobado y límites

### Incluido en la planificación

- Un flujo de backup para un origen local definido por la persona usuaria.
- Un destino local de respaldo como fallback obligatorio y verificable.
- Un destino remoto opcional basado en Azure Blob Storage.
- Validaciones documentadas de rutas, resultado y estado de la transferencia.
- Datos de prueba no sensibles y verificaciones reproducibles en fases posteriores.

### Fuera de alcance de la primera versión

- Sincronización bidireccional o continua.
- Programación automática, servicio residente, monitorización o alertas.
- Copias incrementales, deduplicación, versionado complejo o gestión de retención.
- Restauración automatizada más allá de la validación que se defina antes de implementar.
- Cifrado propio, gestión de claves, autenticación de usuarios o control de acceso personalizado.
- Interfaz web, API, base de datos, procesamiento distribuido o múltiples proveedores cloud.
- Carga de secretos al repositorio, telemetría o transferencia de datos a proveedores distintos de Azure Blob cuando se active la ruta remota.

## Requisitos conocidos

### Funcionales

Los requisitos funcionales están definidos e implementados conforme al contrato v1 de [`docs/CONTRATO.md`](docs/CONTRATO.md):

1. Reciba un único origen explícito —archivo regular o directorio regular— y un directorio local de destino existente.
2. Rechace enlaces, junctions, tipos especiales, colisiones, relaciones de ruta recursivas y otros casos no admitidos por el contrato.
3. Produzca una copia local aislada que pueda verificarse mediante estructura, tamaños y SHA-256 efímero por archivo antes de publicarla.
4. Active la carga opcional a Azure Blob solo después de validar configuración, credenciales y conectividad.
5. Informe separadamente el resultado local y, cuando aplique, el resultado remoto sin incluir secretos ni contenido de archivos.
6. Mantenga un fallback local utilizable si Azure no está disponible antes de la puerta T+30 definida en [`docs/DAILY_WORKFLOW.md`](../../docs/DAILY_WORKFLOW.md).

### No funcionales

- **Seguridad:** ningún secreto, cadena de conexión ni token se versionará; las variables se documentarán sin valores solo si llegan a ser necesarias.
- **Privacidad:** los datos de origen no se incluirán en fixtures, ejemplos, logs de prueba ni recursos de demo.
- **Fiabilidad:** una incidencia remota no deberá invalidar un backup local correctamente terminado.
- **Trazabilidad:** los resultados y diagnósticos deberán ser claros, deterministas donde sea posible y aptos para verificación.
- **Portabilidad:** se priorizará una ejecución local compatible con Python 3.11 o superior; los detalles por plataforma se decidirán en el contrato.
- **Limitación de alcance:** se evitarán capacidades no esenciales para preservar el carácter atómico del reto.

## Tecnologías

| Área | Tecnología o decisión | Estado |
|---|---|---|
| Lenguaje y ejecución local | Python 3.11 o superior | Implementado |
| Acceso remoto opcional | `azure-storage-blob` | Implementado con importación diferida |
| Almacenamiento local | Sistema de archivos local | Implementado como base y fallback |
| Secretos | Variables de entorno no versionadas | Implementado mediante plantilla sin valores |
| Dependencias | [`requirements.txt`](requirements.txt) | Declaradas para la ruta `--azure` |

[`.env.example`](.env.example) documenta, sin valores, las dos variables autorizadas por el contrato: `AZURE_STORAGE_CONNECTION_STRING` y `AZURE_STORAGE_CONTAINER_NAME`. La sesión Azure CLI y la identidad administrada no sustituyen estas variables en la v1; las alternativas de autenticación siguen fuera de alcance.

## Flujo local y Azure disponibles

La ruta local requiere Python 3.11 o superior y solo la biblioteca estándar. La ruta `--azure` requiere instalar [`requirements.txt`](requirements.txt), pero el SDK se carga únicamente tras solicitar Azure: el modo local no necesita credenciales, SDK ni red.

Desde [`projects/day-07-backup-azure-blob`](.), se ejecuta una copia local con:

```text
python src/main.py backup <SOURCE_PATH> <DESTINATION_DIRECTORY> [--azure]
```

[`run_local_backup()`](src/local_backup.py:83) valida y planifica primero, crea una copia temporal propia dentro del destino, compara estructura, tamaños y SHA-256 efímero, y solo después publica la copia. [`main.py`](src/main.py) comunica el resultado mediante la CLI sin duplicar la lógica del núcleo. La sintaxis inválida termina con código `2`; un fallo local controlado termina con código `1`; una copia publicada y verificada termina con código `0`.

Con `--azure`, la CLI exige que `AZURE_STORAGE_CONNECTION_STRING` y `AZURE_STORAGE_CONTAINER_NAME` estén presentes y no vacías **antes** de crear contenido local. Si falta una, informa un error remoto seguro, devuelve `1` y no deja artefactos. Una vez publicada la copia local, carga cada archivo regular con `overwrite=False`; un error remoto posterior conserva la copia y devuelve `0` con fallback explícito.

Los nombres remotos son `backups/<SOURCE_BASENAME>` para un archivo y `backups/<SOURCE_BASENAME>/<RELATIVE_POSIX_PATH>` para un directorio. Los directorios vacíos no producen blobs ni marcadores. Copie [`.env.example`](.env.example) fuera de control de versiones o establezca las dos variables en su entorno local; no añada sus valores al repositorio. La guía está en [`examples/USO.md`](examples/USO.md) y la verificación de Fase 5 en [`docs/VERIFICACION_FASE_5.md`](docs/VERIFICACION_FASE_5.md).

Las validaciones se ejecutan con:

```text
python -m unittest discover -s tests -t . -v
python -m compileall -q src tests
```

## Arquitectura

La arquitectura separa la lógica de planificación y validación del backup de la interfaz y del proveedor remoto.

| Componente | Directorio | Responsabilidad |
|---|---|---|
| Interfaz y coordinación | [`src`](src) | Recibir la solicitud, aplicar el flujo y comunicar resultados. |
| Operación local | [`src`](src) | Preparar, ejecutar y verificar la copia de fallback local. |
| Adaptador de Azure Blob | [`src`](src) | Encapsular la carga remota opcional y sus errores controlados. |
| Pruebas | [`tests`](tests) | Comprobar contratos, flujo local, integración simulada y regresiones. |
| Fixtures | [`data/fixtures`](data/fixtures) | Contener estructuras y contenido no sensible. |
| Resultados esperados | [`data/expected`](data/expected) | Registrar referencias verificables no secretas. |
| Documentación | [`docs`](docs) | Mantener contrato, decisiones, seguridad y procedimientos. |
| Ejemplos | [`examples`](examples) | Alojar guías reproducibles. |
| Recursos de demo | [`assets`](assets) | Guardar el recurso visual final sin datos personales ni secretos. |

El flujo es: solicitud explícita → validación de alcance y rutas → copia y verificación local → intento remoto opcional validado → informe de resultados. La copia local es una condición previa y el fallback de la demostración; Azure no sustituye la comprobación local.

## Organización actual

- [`src`](src): CLI, núcleo local de validación, planificación, copia, manifiestos/verificación, errores, recuperación y adaptador Azure aislado.
- [`tests`](tests): pruebas unitarias, de integración local, CLI y adaptador remoto mediante dobles sin red.
- [`data/fixtures`](data/fixtures): catálogo declarativo y árboles sintéticos no sensibles de Fase 2.
- [`data/expected`](data/expected): manifiestos de estructura, tamaños y propiedades esperadas de Fase 2; no incluyen hashes persistidos.
- [`docs`](docs): contrato y trazabilidad de escenarios de Fase 2.
- [`examples`](examples): guía reproducible de uso local con datos sintéticos.
- [`assets`](assets): recurso textual de demostración local, sin datos sensibles ni secretos.
- [`README.md`](README.md): definición documental de propósito, alcance y estructura.
- [`ROADMAP.md`](ROADMAP.md): planificación de fases, dependencias y criterios de cierre.

## Decisiones iniciales y ambigüedades resueltas

1. **Fallback local obligatorio.** La política global exige un fallback para integraciones externas; el contrato v1 adopta una copia local verificada como ruta mínima de entrega.
2. **Azure Blob opcional.** El registro global indica Azure SDK, pero no impone que Azure sea un requisito de ejecución. La ruta remota solo se intentará tras una copia local correcta y únicamente si se valida antes de T+30.
3. **CLI mínima disponible.** La CLI implementa el único subcomando `backup`, con un origen explícito, un directorio de destino local y la opción remota explícita `--azure`. La opción conserva el fallback local mientras Azure sigue pendiente de Fase 5.
4. **Copia segura acotada.** La v1 admitirá un archivo o directorio regular, rechazará enlaces y tipos especiales, evitará conflictos y publicará solo una copia temporal que haya superado la verificación contractual.
5. **Verificación local definida.** La igualdad se comprobará con estructura, tamaños y SHA-256 efímero por archivo, sin persistir ni mostrar resúmenes.
6. **Sin configuración anticipada.** No se reservan archivos de dependencias ni variables de entorno para no introducir contenido funcional antes de que la integración esté justificada en Fase 5.

## Criterios de aceptación de la primera versión

La primera versión solo podrá considerarse terminada cuando:

- El contrato defina entrada, salida, política de copia, errores, verificación y límites del flujo.
- El backup local complete su escenario principal y pueda verificarse con recursos no sensibles.
- La integración con Azure Blob se haya validado dentro de la ventana prevista o se haya desactivado explícitamente a favor del fallback local.
- La solución no requiera secretos versionados y documente las variables opcionales sin valores si llegaran a existir.
- Las pruebas cubran validaciones, copia local, errores previsibles, comportamiento de fallback y el adaptador remoto mediante mecanismos no dependientes de una cuenta real.
- La documentación distinga con precisión entre la ruta local disponible y la ruta Azure opcional.
- La demo y las instrucciones finales puedan ejecutarse de forma reproducible sin depender exclusivamente de conectividad, cuota, permisos o credenciales cloud.

## Estrategia general de calidad

La calidad se organizará por capas: contrato primero; fixtures y resultados de referencia después; implementación local; integración opcional; y cierre con pruebas, documentación y demo. Las validaciones priorizarán la preservación del origen, la exactitud de la copia local, el tratamiento seguro de secretos y rutas, y la degradación controlada de la integración cloud.

La ruta Azure deberá probarse con aislamiento suficiente para evitar que credenciales, cuotas o red hagan frágil la suite. La demostración final mostrará el flujo local y, solo si está disponible y validado, el resultado remoto; en caso contrario explicará y ejercitará el fallback.

## Riesgos y supuestos

| Riesgo o supuesto | Tratamiento planificado |
|---|---|
| Credenciales, permisos, cuota o red de Azure no disponibles | Validar antes de T+30 y pasar al fallback local si falla. |
| Pérdida o modificación del origen durante la copia | Definir validaciones y una estrategia de operación segura antes de implementar. |
| Ambigüedad sobre qué se respalda y cómo se verifica | Cerrar un contrato explícito antes de crear lógica o fixtures. |
| Exposición accidental de secretos o datos de muestra | Usar variables no versionadas y fixtures sintéticos; revisar documentación y recursos. |
| Aumento de alcance por capacidades de sincronización o automatización | Mantener esas capacidades fuera de la v1. |
| Diferencias de rutas y permisos entre plataformas | Documentar límites y validar los escenarios soportados durante diseño y pruebas. |

El supuesto aprobado para esta planificación es que una copia local verificable satisface la entrega mínima si Azure Blob no se puede validar con rapidez. El contrato ya selecciona una CLI mínima, la unidad de backup, la nomenclatura local, la verificación y la autenticación Azure prevista; los detalles remotos y las capacidades avanzadas siguen aplazados en [`docs/CONTRATO.md`](docs/CONTRATO.md).

## Estado y próximos pasos

Las fases 0 a 5 están completadas. El contrato v1 de [`docs/CONTRATO.md`](docs/CONTRATO.md) define también la configuración estricta de `--azure`, los nombres de blobs y el fallback posterior a una publicación local correcta. [`src/azure_blob.py`](src/azure_blob.py) mantiene el proveedor aislado, difiere el SDK y traduce errores sin exponer detalles. No se versionan secretos ni se realizan llamadas de red en la suite. La transferencia con una cuenta autorizada sigue siendo una comprobación operativa manual opcional. La secuencia completa se encuentra en [`ROADMAP.md`](ROADMAP.md).