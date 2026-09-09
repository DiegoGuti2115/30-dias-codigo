# Día 10 — API CRUD de tareas

Microproyecto del reto **30 Días, 30 Proyectos** para diseñar una API HTTP clara, verificable y local de gestión de tareas.

## Estado

Las Fases 0 a 7 están completadas. La API se entrega con contrato HTTP, aplicación FastAPI, núcleo CRUD local, pruebas deterministas, guía de uso y demostración. Solo permanecen pendientes las mejoras posteriores de [`ROADMAP.md`](ROADMAP.md).

## Inicio rápido

Desde [`projects/day-10-task-api`](.) en PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

Abra `http://127.0.0.1:8000/docs` para la interfaz OpenAPI, ejecute `python -m pytest -q` para comprobar la suite y siga [`assets/DEMO_CRUD.md`](assets/DEMO_CRUD.md) para un flujo CRUD completo. La guía reproducible de entrega está en [`docs/GUIA_DE_ENTREGA.md`](docs/GUIA_DE_ENTREGA.md).

## Propósito y alcance

La futura API administrará una única colección local de tareas mediante creación, consulta, actualización total o parcial y eliminación. El contrato público está definido en [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md).

El alcance de la primera versión incluye:

- Tareas con identificador, título, descripción opcional, estado de completitud y marcas temporales.
- Operaciones CRUD bajo el prefijo HTTP `/api/v1`.
- Validación de datos y respuestas coherentes para éxito, errores de entrada y recursos inexistentes.
- Persistencia local en memoria como fallback reproducible, sin infraestructura externa.

No incluye autenticación, usuarios, base de datos, servicios cloud, interfaz web, notificaciones, etiquetas, adjuntos, recurrencias, filtros, ordenación configurable ni paginación.

## Arquitectura prevista

```text
Cliente HTTP
    ↓
Aplicación FastAPI
    ↓
Esquemas Pydantic y validación
    ↓
Servicio de tareas
    ↓
Repositorio local en memoria
```

Los módulos respetan esta separación:

- [`src/schemas.py`](src/schemas.py): esquemas Pydantic para creación, reemplazo, actualización parcial, lectura y listas de tareas.
- [`src/main.py`](src/main.py): aplicación FastAPI, rutas CRUD y traducción de errores de dominio a HTTP.
- [`src/service.py`](src/service.py): operaciones CRUD de dominio independientes de HTTP.
- [`src/repository.py`](src/repository.py): repositorio local en memoria con identificadores únicos y orden de creación.
- [`src/errors.py`](src/errors.py): error de dominio para recursos de tarea inexistentes.
- [`tests/test_tasks.py`](tests/test_tasks.py): pruebas deterministas de esquemas, repositorio, servicio y contrato HTTP.

## Entrega y demostración

- [`docs/GUIA_DE_ENTREGA.md`](docs/GUIA_DE_ENTREGA.md): instalación, ejecución, verificaciones, decisiones, límites y revisión de seguridad.
- [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md): contrato HTTP implementado con ejemplos documentales de solicitudes, respuestas y errores.
- [`assets/DEMO_CRUD.md`](assets/DEMO_CRUD.md): demostración breve con PowerShell de creación, consulta, actualización, listado y eliminación.

## Validación y dominio implementados

Los modelos Pydantic de la Fase 3 establecen el límite de datos antes de que existan rutas HTTP:

- `TaskCreate`: requiere un título; asigna `description` a `null` y `completed` a `false` cuando se omiten.
- `TaskReplace`: requiere todos los campos editables para el futuro reemplazo total.
- `TaskUpdate`: admite uno o más campos editables para la futura actualización parcial; distingue entre omitir `description` y enviarla como `null`.
- `TaskRead`: representa una tarea completa con identificador positivo y marcas temporales con zona horaria.
- `TaskList`: representa la respuesta de colección mediante la propiedad `items`.

Todos los modelos rechazan campos desconocidos, incluidos los campos de solo lectura en los datos de entrada. Los títulos se recortan antes de validar su longitud y deben contener entre 1 y 120 caracteres; las descripciones textuales admiten hasta 1.000 caracteres; `completed` requiere un booleano estricto.

La Fase 4 implementa un repositorio en memoria aislado por instancia y un servicio de tareas para crear, consultar, listar, reemplazar, actualizar parcialmente y eliminar. Los identificadores son positivos y monotónicos; los listados conservan el orden de creación; las marcas temporales se generan en UTC. Las operaciones sobre recursos ausentes generan `TaskNotFoundError`, para su futura traducción uniforme en la capa HTTP.

## Tecnologías y requisitos

- Python 3.11 o superior, declarado en [`pyproject.toml`](pyproject.toml).
- FastAPI para la capa HTTP y documentación interactiva.
- Pydantic para contratos y validación de datos.
- Uvicorn como servidor ASGI local.
- Pytest y HTTPX para pruebas automatizadas.

Las versiones compatibles están declaradas en [`requirements.txt`](requirements.txt). No se necesitan secretos, variables de entorno ni integraciones externas para la primera versión.

## Instalación

Desde [`projects/day-10-task-api`](.) en PowerShell:

1. Crear un entorno virtual: `py -3.11 -m venv .venv`.
2. Activarlo: `.\.venv\Scripts\Activate.ps1`.
3. Instalar las dependencias: `python -m pip install -r requirements.txt`.

El proyecto no incluye un archivo de configuración de secretos porque la API funciona íntegramente de forma local. La instalación alternativa sin activar PowerShell y las comprobaciones de entrega están detalladas en [`docs/GUIA_DE_ENTREGA.md`](docs/GUIA_DE_ENTREGA.md).

## Ejecución y verificación

La aplicación HTTP se ejecuta desde la raíz del proyecto con `python -m uvicorn src.main:app --reload`. La documentación interactiva está disponible localmente en `http://127.0.0.1:8000/docs` y el esquema OpenAPI en `http://127.0.0.1:8000/openapi.json`. El flujo manual completo está en [`assets/DEMO_CRUD.md`](assets/DEMO_CRUD.md).

Las pruebas actuales validan los esquemas Pydantic, el núcleo CRUD local y el contrato HTTP completo, incluidas validaciones, errores, aislamiento de estado y regresiones. Se ejecutan desde la raíz del proyecto con `python -m pytest -q`.

Para verificar el entorno se puede ejecutar `python --version`, `python -m pip check` y `python -m compileall src tests` después de instalar las dependencias.

## Convenciones de calidad

- Usar Python 3.11+ y anotaciones de tipo en todo código nuevo.
- Mantener responsabilidades separadas entre HTTP, esquemas, servicio, repositorio y errores.
- Ejecutar `python -m pytest` antes de entregar cambios que incluyan implementación o pruebas.
- Verificar sintaxis con `python -m compileall src tests`.
- No añadir dependencias sin una necesidad explícita y documentada.
- No incluir secretos, credenciales ni configuraciones específicas de una máquina.
- Mantener el contrato HTTP como fuente de verdad; todo cambio público debe actualizar [`docs/CONTRATO_API_V1.md`](docs/CONTRATO_API_V1.md).

## Estructura del proyecto

```text
projects/day-10-task-api/
├── assets/
│   └── DEMO_CRUD.md        Demostración manual breve del flujo CRUD
├── data/
│   └── fixtures/           Datos de prueba futuros
├── docs/
│   ├── CONTRATO_API_V1.md  Contrato HTTP público y ejemplos documentales
│   └── GUIA_DE_ENTREGA.md  Instalación, verificación, límites y seguridad
├── src/
│   ├── schemas.py          Esquemas y validaciones Pydantic
│   ├── errors.py           Errores de dominio
│   ├── main.py             Aplicación y rutas FastAPI
│   ├── repository.py       Persistencia local en memoria
│   └── service.py          Reglas de negocio CRUD
├── tests/
│   └── test_tasks.py       Pruebas de esquemas, núcleo CRUD y contrato HTTP
├── pyproject.toml          Metadatos y versión mínima de Python
├── requirements.txt        Dependencias de desarrollo y ejecución
├── README.md               Guía del proyecto y entorno
└── ROADMAP.md              Fases de desarrollo
```

## Decisiones técnicas

- **FastAPI y Pydantic:** son el stack definido por el reto y proporcionan validación y documentación HTTP consistentes.
- **Arquitectura por capas:** reduce el acoplamiento y hace verificables las reglas de negocio.
- **Validación antes de lógica:** los contratos de entrada y salida se implementan antes de persistencia y rutas, de acuerdo con el roadmap.
- **Repositorio en memoria:** ofrece persistencia local determinista, aislada por instancia y sin credenciales ni servicios externos.
- **Alcance atómico:** filtros, paginación, persistencia durable y autenticación quedan fuera de la primera versión.
