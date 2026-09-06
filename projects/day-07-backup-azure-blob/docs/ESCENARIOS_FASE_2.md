# Escenarios, fixtures y referencias — Fase 2

## Propósito y límite de fase

Este inventario transforma el contrato v1 en datos de prueba sintéticos, resultados de referencia y trazabilidad. No implementa la copia, la verificación, la CLI, pruebas automatizadas, dependencias ni configuración de Azure. Esos elementos quedan reservados para las fases 3 a 6 de [`ROADMAP.md`](../ROADMAP.md).

El catálogo declarativo está en [`data/fixtures/scenario-catalog.json`](../data/fixtures/scenario-catalog.json) y las propiedades esperadas de copias correctas están en [`data/expected/local-copy-manifests.json`](../data/expected/local-copy-manifests.json). Los árboles de origen versionados son pequeños, inocuos y se ubican bajo [`data/fixtures`](../data/fixtures).

## Convenciones de los fixtures

- Todos los nombres, rutas y contenidos son sintéticos; no representan backups reales ni contienen datos personales, secretos o credenciales.
- Los archivos de los fixtures contienen texto corto y estable en UTF-8. Los directorios vacíos se describen de forma declarativa porque un directorio vacío no se conserva por sí solo en control de versiones.
- Los manifiestos esperados registran tipo de raíz, rutas relativas y tamaños. No persisten valores SHA-256: en la v1 se calculan solo durante una operación futura, conforme a [`CONTRATO.md`](CONTRATO.md).
- Las rutas descritas son relativas al directorio del proyecto. Las pruebas futuras construirán los destinos temporales y las condiciones no representables como un árbol versionado.
- Ningún escenario requiere red, cuenta Azure, SDK de Azure o variables de entorno.

## Escenarios locales

| ID | Entrada sintética | Resultado de referencia | Requisito contractual cubierto |
|---|---|---|---|
| `regular-file-success` | Archivo regular `regular-file/sample-note.txt`. | Copia verificable con el mismo nombre, tamaño y bytes. | Archivo regular, nombre final, igualdad de bytes y SHA-256. |
| `directory-tree-success` | Directorio con dos archivos, un subdirectorio y un directorio vacío declarado. | Árbol relativo, directorios vacíos y tamaños coincidentes. | Directorio regular, preservación de estructura y directorios vacíos. |
| `empty-directory-success` | Directorio de origen sin entradas, creado efímeramente por la prueba futura. | Directorio final vacío del mismo nombre. | Directorio vacío admisible. |
| `missing-source` | Ruta sintética inexistente. | Error controlado; no hay copia temporal ni final. | Existencia y lectura del origen. |
| `destination-missing` | Directorio de destino sintético inexistente. | Error controlado; no se crea el destino. | Destino existente obligatorio. |
| `destination-not-directory` | Archivo regular usado como destino. | Error controlado; no se modifica el archivo. | Tipo del destino. |
| `final-name-conflict` | La entrada final con el nombre base del origen ya existe. | Error controlado; la entrada existente queda intacta. | Sin sobrescritura ni modificación de conflictos. |
| `same-final-location` | Origen y ubicación final representan la misma ruta. | Error controlado; no se opera. | Igualdad de rutas no admisible. |
| `destination-inside-source` | Destino incluido dentro de un directorio de origen. | Error controlado antes de copiar. | Prevención de recursión. |
| `destination-ancestor-of-source` | Destino es ancestro de un directorio de origen. | Error controlado antes de copiar. | Relación de rutas no permitida. |
| `source-symlink` | Enlace simbólico o junction usado como origen, cuando la plataforma lo permita. | Error controlado; no se sigue el enlace. | Rechazo de enlaces. |
| `nested-symlink` | Enlace simbólico o junction dentro de un árbol de origen, cuando la plataforma lo permita. | Error controlado; no se publica una copia parcial. | Recorrido seguro de directorios. |
| `unsupported-source-entry` | Elemento especial disponible en la plataforma de prueba. | Escenario condicional: rechazo controlado o exclusión documentada si no puede crearse. | Rechazo de tipos especiales. |
| `source-read-permission-denied` | Lectura o exploración del origen revocada, cuando la plataforma lo permita. | Error controlado; no se publica copia final. | Permisos de origen. |
| `destination-write-permission-denied` | Escritura/publicación en destino revocada, cuando la plataforma lo permita. | Error controlado; no se modifica la ubicación final. | Permisos de destino. |
| `copy-interrupted` | Fallo inyectado durante la futura copia temporal. | Error controlado, sin publicación final; se intenta limpiar solo el temporal propio. | Copia aislada, publicación y limpieza limitada. |
| `verification-mismatch` | Divergencia inyectada entre origen y copia temporal. | Error controlado, sin publicación final; no se presenta éxito. | Tamaño, SHA-256 y publicación después de verificar. |
| `publish-failure` | Fallo inyectado al publicar la copia ya verificada. | Error controlado; ubicación final ausente o sin modificar; limpieza limitada. | Error de publicación. |

Los escenarios marcados como condicionales se ejecutarán únicamente donde el sistema de archivos permita construir el estado de forma fiable. Su ausencia por limitación de plataforma no autoriza a seguir enlaces ni a aceptar tipos especiales en producción.

## Referencias de resultados

Los resultados locales se expresan como propiedades, no como salidas ejecutables:

- Un escenario `*-success` debe producir, en una implementación futura, un backup local publicado y verificable, con salida de éxito y código `0` conforme a [`CONTRATO.md`](CONTRATO.md).
- Los escenarios de validación, conflicto, permisos, copia, verificación o publicación deben terminar controladamente, no publicar una ubicación final nueva y corresponder al código `1` futuro.
- La sintaxis inválida de la CLI se reserva para las pruebas de Fase 4 y deberá corresponder al código `2`; no se implementa ni se simula como comando en esta fase.
- Los hashes no aparecen en fixtures, referencias ni diagnósticos de referencia. Su comparación futura será efímera por archivo.

## Simulación de Azure sin cuenta real

La Fase 5 implementa el adaptador aislado. La suite sigue usando dobles y no requiere red, cuenta Azure ni SDK instalado para ejecutar sus pruebas:

| ID | Doble | Resultado contractual |
|---|---|---|
| `azure-missing-configuration` | Configuración remota ausente. | No se intenta red ni se crea contenido local; error claro y código `1`. |
| `azure-upload-success` | Doble que acepta todas las cargas. | Backup local y remoto confirmados; código `0`. |
| `azure-upload-failure` | Doble que falla durante una carga. | Se conserva la copia local; diagnóstico remoto y fallback; código `0`. |

La convención aprobada es `backups/<SOURCE_BASENAME>` para un archivo y `backups/<SOURCE_BASENAME>/<RELATIVE_POSIX_PATH>` para cada archivo de un directorio. Los directorios vacíos no generan marcadores. No hay reintentos, metadatos ni autenticación alternativa en v1.

## Trazabilidad por sección contractual

| Sección de [`CONTRATO.md`](CONTRATO.md) | Escenarios o referencia |
|---|---|
| Unidad de backup admitida | `regular-file-success`, `directory-tree-success`, `empty-directory-success`, `source-symlink`, `nested-symlink`, `unsupported-source-entry`. |
| Rutas y destino local | `missing-source`, `destination-missing`, `destination-not-directory`, `final-name-conflict`, `same-final-location`, `destination-inside-source`, `destination-ancestor-of-source`, permisos. |
| Plan, copia y publicación segura | `copy-interrupted`, `publish-failure`, y la ausencia de publicación en todos los errores. |
| Verificación local | Manifiestos `regular-file-success` y `directory-tree-success`; `verification-mismatch`. |
| Resultados y códigos | Referencias de resultados locales y escenarios Azure reservados. |
| Azure Blob y fallback | `azure-missing-configuration`, `azure-upload-success`, `azure-upload-failure`. |
| Secretos, datos y registros | Convenciones de fixtures y revisión de privacidad de este documento. |

## Revisión de privacidad y reproducibilidad

- Los contenidos versionados son únicamente frases de demostración sin identidad, credenciales, rutas de máquina ni información operativa real.
- Las referencias no incluyen hashes, tokens, cadenas de conexión, datos de Azure ni contenido de archivos más allá del propio fixture sintético.
- Los errores se describen por categoría; no contienen trazas, rutas temporales ni mensajes de excepciones.
- La ejecución futura deberá crear permisos denegados, enlaces, interrupciones y divergencias dentro de directorios temporales aislados, y eliminarlos al terminar cada prueba.
