# Día 12 — API de inspección de archivos

> Microproyecto del reto [30 Días, 30 Proyectos](../../README.md). Estado actual: versión 1 local, sin estado y sin persistencia completada y verificada; incluye contrato público, núcleo determinista, capa HTTP FastAPI, regresión automatizada y guía de entrega segura.

## Propósito

Ofrecer una API HTTP local para inspeccionar **un archivo cargado por solicitud** sin persistirlo. La versión 1 devuelve metadatos de la carga, tamaño, tipo de medio declarado, extensión, comprobaciones seguras del nombre y una huella de contenido no reversible.

## Alcance de la primera versión

- Recepción de un único archivo mediante una solicitud multipart.
- Inspección local y efímera durante la solicitud.
- Resultado estructurado con nombre de archivo tratado como dato no confiable, extensión normalizada, tamaño, tipo de medio declarado y huella de contenido.
- Validaciones de presencia, unicidad, tamaño y nombre inseguro.
- Documentación OpenAPI generada por FastAPI para la ruta pública.
- Procesamiento local como ruta garantizada de demostración y entrega.

## Fuera de alcance

- Persistencia de archivos, base de datos, colas, cuentas de usuario o autenticación.
- Ejecución, apertura, descompresión o análisis semántico del contenido.
- Antivirus, detección de malware, validación de firma binaria o garantía de que el tipo declarado coincida con el contenido.
- Lotes, carpetas, archivos remotos por URL o inspección recursiva.
- Integración Azure Blob en la primera versión funcional.

## Decisiones cerradas de la versión 1

La especificación raíz únicamente establece FastAPI y Azure Blob opcional. Para eliminar la ambigüedad, se confirma como alcance mínimo la inspección local de una carga única; Azure Blob queda como mejora posterior y nunca debe sustituir el flujo local.

El contrato [docs/CONTRATO_API_V1.md](docs/CONTRATO_API_V1.md) fija la única operación prevista: `POST /api/v1/inspect`, con un único campo multipart `file`, límite de 5 MiB, huella SHA-256 hexadecimal, semántica del tipo de medio declarado, reglas de extensión y comprobaciones seguras de nombre. También define respuestas correctas y errores uniformes. No se añadirán campos ni validaciones fuera de ese contrato.

## Tecnologías

- Python 3.11 o superior.
- FastAPI para la capa HTTP y OpenAPI.
- Pydantic para contratos de entrada y salida.
- Pytest y HTTPX para pruebas unitarias, HTTP y de entrega.
- Biblioteca estándar de Python para el cálculo local de la huella SHA-256.
- Azure Blob Storage solo como integración opcional futura; no forma parte de la versión 1.

Las dependencias de ejecución se declaran en [requirements.txt](requirements.txt) y los metadatos junto con la configuración de Pytest, Ruff y MyPy se encuentran en [pyproject.toml](pyproject.toml). [python-multipart](https://pypi.org/project/python-multipart/) habilita el parseo multipart de la única ruta pública; no se incluye ninguna integración cloud.

No existen variables de entorno ni secretos obligatorios en la versión 1. [`.gitignore`](.gitignore) evita versionar entornos virtuales, cachés, archivos `.env` y artefactos generados.

## Instalación

Desde la raíz de [projects/day-12-upload-inspector-api](.) cree un entorno aislado e instale las dependencias declaradas:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Los metadatos de [pyproject.toml](pyproject.toml) duplican los rangos del manifiesto y configuran las herramientas de desarrollo. El proyecto se ejecuta directamente desde su raíz; use [requirements.txt](requirements.txt) como vía de instalación reproducible.

## Verificación

Valide la resolución de dependencias, el contrato y la calidad desde la raíz del proyecto:

```powershell
python -m pip check
python -m pytest -q
python -m ruff check src tests
python -m mypy src tests
python -m compileall -q src tests
```

Las Fases 3 y 4 incorporan pruebas unitarias de los contratos Pydantic, la normalización segura del nombre y el núcleo de inspección local. La Fase 5 añade pruebas HTTP del contrato, incluidos multipart, límites, errores y OpenAPI. La Fase 6 añade regresión de entrega contra el fixture versionado, límite exacto, metadatos ausentes, nombres Unicode, extensiones ambiguas, errores sin filtración interna y aislamiento tras un error. La Fase 7 consolida la ejecución, demostración y revisión final en [docs/GUIA_DE_ENTREGA.md](docs/GUIA_DE_ENTREGA.md). La aplicación se ejecuta localmente con `python -m uvicorn src.main:app --reload`.

## Arquitectura

La arquitectura separa el transporte HTTP de la inspección pura y del contrato de datos:

```text
Cliente HTTP
    |
FastAPI route
    |
Validation and request limits
    |
Inspection service
    |-- filename and extension checks
    |-- media type and size extraction
    `-- content fingerprint
    |
Structured response
```

La ruta no contiene reglas de inspección. El servicio no realiza operaciones de red, persistencia ni acceso a rutas del sistema proporcionadas por el cliente.

## Estructura del proyecto

```text
projects/day-12-upload-inspector-api/
├── README.md
├── ROADMAP.md
├── docs/
│   └── CONTRATO_API_V1.md
├── src/
├── tests/
├── data/
│   ├── fixtures/
│   └── expected/
└── assets/
```

| Ruta | Función |
|---|---|
| [README.md](README.md) | Contexto, límites, arquitectura y evolución prevista. |
| [ROADMAP.md](ROADMAP.md) | Fases, prioridades, dependencias, riesgos y aceptación. |
| [docs/CONTRATO_API_V1.md](docs/CONTRATO_API_V1.md) | Fuente de verdad futura para el contrato HTTP y sus decisiones bloqueantes. |
| [docs](docs) | Contrato público y documentación de entrega de la versión 1. |
| [docs/GUIA_DE_ENTREGA.md](docs/GUIA_DE_ENTREGA.md) | Instalación, comprobaciones reproducibles, demostración local segura y lista de cierre. |
| [src/filename_validation.py](src/filename_validation.py) | Evaluación pura, segura y determinista de nombre y extensión, sin acceso a rutas ni al sistema de archivos. |
| [src/schemas.py](src/schemas.py) | Modelos Pydantic estrictos para las respuestas correctas y de error del contrato v1. |
| [src/inspection.py](src/inspection.py) | Servicio local puro que recorre una secuencia binaria en bloques, mide su tamaño y calcula SHA-256 sin persistencia ni acceso a rutas. |
| [src/main.py](src/main.py) | Transporte FastAPI: ruta multipart, OpenAPI y adaptación segura de errores, delegando en el núcleo local. |
| [tests](tests) | Pruebas unitarias de contratos, validaciones y núcleo local, más pruebas HTTP y de entrega del contrato v1. |
| [data/fixtures](data/fixtures) | Archivos de entrada no sensibles y controlados para regresión local. |
| [data/expected](data/expected) | Respuestas esperadas versionadas para regresión del núcleo local. |
| [assets](assets) | Evidencias de demostración y materiales de publicación futuros. |

## Flujo de trabajo aplicado

1. Cerrar el contrato de la API y las decisiones de seguridad documentadas. **Completado en la Fase 1.**
2. Declarar el entorno y las dependencias en la Fase 2, sin secretos obligatorios. **Completado.**
3. Implementar y probar la inspección local determinista antes de exponer HTTP. **Completado.**
4. Conectar la capa FastAPI sin duplicar reglas del servicio. **Completado.**
5. Ejecutar pruebas de contrato, límites y regresión con fixtures controlados. **Completado.**
6. Preparar documentación de entrega, demostración local y revisión de secretos. **Completado.**

La secuencia detallada, sus prioridades y criterios de aceptación se encuentra en [ROADMAP.md](ROADMAP.md).

## Estrategia de pruebas

La suite cubre unidades de normalización de nombre, extensión y huella; límites de carga; errores multipart y de validación; respuesta HTTP; determinismo; aislamiento de solicitudes; y comparación de entrega contra fixtures seguros versionados. No se cargan archivos sensibles, ejecutables de terceros ni material con datos personales.

## Seguridad y privacidad

- Todo nombre de archivo, tipo MIME y contenido recibido se considerará no confiable.
- El nombre nunca se usará como ruta ni se incluirá sin tratamiento en registros, cabeceras o errores.
- Se impondrá un límite explícito antes de procesar contenido completo y se evitará retener bytes más allá de la solicitud.
- La huella se publicará solo como identificador de contenido; no sustituye controles de seguridad ni revela el contenido de manera intencional.
- No se implementará almacenamiento ni se registrará el contenido. Las políticas futuras deberán evitar registrar nombres completos o huellas si crean un riesgo de correlación.
- Las credenciales de Azure, si se evalúan más adelante, permanecerán fuera del repositorio y la aplicación deberá funcionar sin ellas.

## Despliegue posterior

La primera entrega se verifica localmente. Cualquier despliegue posterior deberá incorporar límites de cuerpo de solicitud en proxy y aplicación, HTTPS, controles de abuso, registros minimizados, observabilidad y una política de retención nula o explícita. La versión 1 no define infraestructura ni configuración operativa cloud.

## Entrega de la versión 1

La versión 1 se entrega localmente sin Azure ni secretos obligatorios. Siga [docs/GUIA_DE_ENTREGA.md](docs/GUIA_DE_ENTREGA.md) para instalar dependencias, ejecutar las comprobaciones, iniciar Uvicorn y demostrar la operación con el fixture no sensible versionado. La guía también documenta escenarios de error, revisión de registros y la lista de cierre.

## Próximos pasos

- Evaluar Azure Blob únicamente después de aceptar la versión local y documentar sus credenciales, permisos, contingencias y fallback.
