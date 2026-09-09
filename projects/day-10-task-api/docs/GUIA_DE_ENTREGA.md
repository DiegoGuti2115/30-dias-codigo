# Guía de entrega — API CRUD de tareas

Esta guía permite instalar, ejecutar, comprobar y demostrar la versión 1 de la API desde el directorio [`projects/day-10-task-api`](..). La interfaz pública se define en [`CONTRATO_API_V1.md`](CONTRATO_API_V1.md) y la demostración guiada está en [`../assets/DEMO_CRUD.md`](../assets/DEMO_CRUD.md).

## Requisitos

- Python 3.11 o superior.
- Una terminal PowerShell en Windows, o comandos equivalentes en otro sistema operativo.
- No se requieren cuentas, credenciales, servicios externos ni variables de entorno.

## Instalación reproducible

Desde la raíz de este proyecto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si la directiva de ejecución de PowerShell impide activar el entorno, ejecute el intérprete del entorno virtual de forma explícita:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Las versiones compatibles están acotadas en [`../requirements.txt`](../requirements.txt) y la versión mínima de Python se declara en [`../pyproject.toml`](../pyproject.toml).

## Ejecución local

Con el entorno virtual activado y desde la raíz del proyecto:

```powershell
python -m uvicorn src.main:app --reload
```

El servidor escucha de forma predeterminada en `http://127.0.0.1:8000`. Mientras permanezca en ejecución, los recursos disponibles son:

- Documentación interactiva: `http://127.0.0.1:8000/docs`
- Esquema OpenAPI: `http://127.0.0.1:8000/openapi.json`
- Colección de tareas: `http://127.0.0.1:8000/api/v1/tasks`

Detenga el servidor con `Ctrl+C`. Cada nuevo arranque crea una instancia nueva y vacía del almacenamiento local.

## Verificación

Ejecute las comprobaciones desde la raíz del proyecto:

```powershell
python -m pytest -q
python -m compileall src tests
python -m pip check
```

La suite es local y determinista: no requiere red, credenciales ni una instancia de Uvicorn en ejecución. `pip check` también puede informar conflictos preexistentes de paquetes instalados globalmente que no pertenezcan a este proyecto; las dependencias declaradas para la API son las de [`../requirements.txt`](../requirements.txt).

Para revisar espacios en cambios controlados por Git, desde la raíz del repositorio principal ejecute:

```powershell
git diff --check
```

## Decisiones y límites de la versión 1

- La aplicación usa FastAPI para la interfaz HTTP y Pydantic para validar cuerpos y respuestas.
- El servicio y el repositorio están separados de la capa HTTP para mantener las reglas CRUD comprobables sin servidor.
- El repositorio vive exclusivamente en memoria. Su contenido se pierde al detener el proceso, no se comparte entre instancias de aplicación y no ofrece concurrencia, copias de seguridad ni recuperación.
- Los identificadores son enteros positivos, monotonamente crecientes y no se reutilizan durante la vida de una instancia.
- El listado conserva el orden de creación. No existen filtros, ordenación configurable ni paginación.
- Las fechas se generan en UTC y se devuelven en formato ISO 8601 con zona horaria.
- La API no incorpora autenticación, usuarios, base de datos, secretos, configuración por entorno, servicios cloud ni interfaz web.

Las evoluciones que exceden estos límites se mantienen como propuestas en [`../ROADMAP.md`](../ROADMAP.md).

## Seguridad de la entrega

El proyecto no almacena secretos ni requiere archivos `.env`. No añada credenciales, tokens, claves de API, volcados de datos reales ni archivos de configuración locales al repositorio. Antes de publicar, revise los archivos que se vayan a incluir con:

```powershell
git status --short
git diff --check
```
