# Verificación del núcleo local — Fase 3

## Alcance implementado

La Fase 3 implementa exclusivamente el núcleo local reutilizable, sin CLI, red, Azure SDK, credenciales ni configuración remota. El punto de coordinación programático es [`run_local_backup()`](../src/local_backup.py:67). La interfaz de línea de comandos definida en [`CONTRATO.md`](CONTRATO.md) sigue reservada para la Fase 4.

Las responsabilidades están separadas:

| Responsabilidad | Módulo | Comportamiento |
|---|---|---|
| Valores estructurados | [`models.py`](../src/models.py) | Plan, manifiesto efímero, verificación y resultado controlado. |
| Errores controlados | [`errors.py`](../src/errors.py) | Categorías estables para validación, copia, verificación y publicación. |
| Validación y planificación | [`validation.py`](../src/validation.py) | Normaliza rutas sin resolver enlaces, inspecciona el árbol antes de copiar, detecta colisiones y relaciones no permitidas. |
| Manifiestos y verificación | [`verification.py`](../src/verification.py) | Compara tipo de raíz, directorios, archivos, tamaños y SHA-256 solo en memoria. |
| Copia, publicación y recuperación | [`local_backup.py`](../src/local_backup.py) | Copia a un temporal propio dentro del destino, verifica y publica mediante reemplazo dentro del mismo sistema de archivos; limpia solo ese temporal si hay fallo. |

## Garantías aplicadas

1. Solo se admiten un archivo regular o un directorio regular, incluido un directorio vacío.
2. Se rechazan enlaces simbólicos, junctions/reparse points de Windows y tipos especiales tanto en la raíz como dentro del árbol.
3. El destino debe existir, ser un directorio regular y no ser enlace; no se crean destinos implícitamente.
4. La ubicación final es el hijo directo con el nombre base del origen. Un conflicto siempre falla y deja intacta la entrada existente.
5. Para un origen de directorio, el destino no puede estar dentro del origen ni ser su ancestro.
6. La copia se realiza en un temporal con el prefijo interno `.backup-v1-` dentro del destino. La publicación solo ocurre tras una verificación correcta.
7. La verificación construye manifiestos no persistidos y exige igualdad de tipo, rutas relativas, directorios vacíos, tamaños y SHA-256 por archivo.
8. Ante una excepción de copia, verificación o publicación, el núcleo devuelve un resultado estructurado, no publica el destino final y solo intenta eliminar el temporal que creó.

La publicación usa la operación de reemplazo del sistema dentro del mismo directorio. No se promete atomicidad frente a apagados, antivirus, cambios concurrentes u otras semánticas externas, tal como limita el contrato.

## Cobertura de escenarios

[`tests/test_local_backup.py`](../tests/test_local_backup.py) cubre los escenarios locales que se pueden construir de forma determinista en la suite estándar:

- `regular-file-success`, `directory-tree-success` y `empty-directory-success`, comparados contra [`local-copy-manifests.json`](../data/expected/local-copy-manifests.json).
- `missing-source`, `destination-missing`, `destination-not-directory`, `final-name-conflict` y reejecución segura.
- `destination-inside-source` y `destination-ancestor-of-source`.
- `source-symlink` y `nested-symlink`, cuando el entorno permite crear enlaces.
- Interrupción de copia, divergencia de verificación y fallo de publicación mediante inyección interna de operaciones.
- Detección de una copia modificada después de copiar.
- Presencia de los escenarios Azure reservados sin añadir adaptador remoto ni dependencia Azure.

Los escenarios de permisos y de elementos especiales permanecen dependientes de las capacidades del sistema de archivos y privilegios del proceso. La implementación los rechaza cuando las APIs locales los exponen; la suite estándar no cambia permisos ni crea dispositivos/FIFO para evitar resultados frágiles o inseguros en Windows.

## Ejecución de validaciones

Desde [`projects/day-07-backup-azure-blob`](..), sin instalación adicional:

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

La implementación utiliza exclusivamente la biblioteca estándar de Python 3.11+; por ello no se añadió [`requirements.txt`](../requirements.txt). Los directorios `__pycache__` generados por compilación o pruebas son artefactos locales y no deben versionarse.

## Límite de Azure y evolución posterior

Azure permanece bloqueado fuera de este núcleo. No existe adaptador, conexión, variable de entorno, secreto, SDK ni intento de red. Los cuatro escenarios remotos del catálogo siguen siendo referencias para la Fase 5.

La Fase 4 ya añadió la CLI contratada sin modificar la política de validación, publicación o verificación establecida aquí. Su flujo, guía y cobertura se documentan en [`VERIFICACION_FASE_4.md`](VERIFICACION_FASE_4.md). La siguiente fase posible es la Fase 5, limitada a una integración Azure Blob aislada y opcional.
