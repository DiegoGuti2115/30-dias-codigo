# Guía de entrega — API de inspección de archivos v1

## Propósito y alcance verificado

Esta guía describe cómo ejecutar y demostrar localmente la versión 1 ya verificada. La fuente de verdad del comportamiento público es [CONTRATO_API_V1.md](CONTRATO_API_V1.md).

La entrega acepta exactamente un archivo en el campo multipart `file` mediante `POST /api/v1/inspect`. Procesa los bytes de forma local y efímera, informa tamaño, tipo declarado, extensión, comprobaciones de nombre y SHA-256. No persiste archivos, resultados ni metadatos.

Quedan fuera de esta entrega el almacenamiento, autenticación, cargas múltiples, URLs remotas, análisis o ejecución de contenido, detección de malware y Azure Blob.

## Requisitos

- Python 3.11 o superior.
- Un entorno virtual local recomendado.
- Ninguna variable de entorno, secreto, cuenta cloud o servicio externo.

Desde la raíz del proyecto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Comprobaciones reproducibles

Ejecute estas comprobaciones antes de una demostración o entrega:

```powershell
python -m compileall -q src tests
python -m pytest -q
python -m ruff check src tests
python -m mypy src tests
```

La suite incluye unidades, contrato HTTP y regresión de entrega. El fixture seguro [../data/fixtures/phase-4-sample.txt](../data/fixtures/phase-4-sample.txt) se compara con [../data/expected/phase-4-sample.json](../data/expected/phase-4-sample.json) para fijar una respuesta determinista conocida.

## Demostración local breve

1. Inicie el servidor desde la raíz del proyecto:

   ```powershell
   python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
   ```

2. En otra terminal, envíe exclusivamente el fixture no sensible incluido en el repositorio:

   ```powershell
   curl.exe -sS -X POST http://127.0.0.1:8000/api/v1/inspect -F "file=@data/fixtures/phase-4-sample.txt;type=text/plain"
   ```

3. Compruebe una respuesta `200 OK` con los valores del resultado esperado versionado: nombre `phase-4-sample.txt`, tamaño `19`, tipo declarado `text/plain`, extensión `txt` y huella SHA-256 `2d1defc09b2948c1d59fde60b0fedd4c0155f8d28e954ab3c9dd28e2e64ab167`.

4. Consulte la documentación generada localmente si necesita revisar la única operación publicada:

   ```text
   http://127.0.0.1:8000/docs
   ```

No use nombres, contenido ni tipos de medio reales o sensibles durante la demostración. La respuesta contiene la huella del contenido; no la publique si puede crear un riesgo de correlación.

## Escenarios de comprobación pública

| Escenario | Solicitud | Resultado esperado |
|---|---|---|
| Archivo válido | Una parte `file` con nombre seguro | `200` y la representación de inspección v1 |
| Archivo vacío | Una parte `file` válida sin bytes | `200`, tamaño `0` y SHA-256 del flujo vacío |
| Más de 5 MiB | Una parte `file` de 5.242.881 bytes | `413` con `file_too_large` |
| Nombre inseguro | Una parte `file` cuyo nombre contiene separador o traversal | `422` con `validation_error`, sin reflejar el nombre |
| Multipart malformado | Cuerpo multipart sin boundary válido o no interpretable | `400` con `malformed_multipart` |
| Tipo de solicitud incorrecto | Solicitud que no usa `multipart/form-data` | `415` con `unsupported_media_type` |

Los formatos detallados de respuesta y error permanecen en [CONTRATO_API_V1.md](CONTRATO_API_V1.md). Esta guía no añade rutas, campos, límites ni códigos nuevos.

## Revisión final de seguridad, registros y referencias

- No se requieren secretos ni configuración de entorno para v1; no hay archivos `.env` de entrega.
- [../.gitignore](../.gitignore) excluye entornos virtuales, cachés, cobertura, artefactos de compilación y archivos `.env`.
- La inspección no abre rutas proporcionadas por el cliente, no realiza red, no persiste bytes y no registra contenido, nombres o huellas.
- Los errores públicos no incluyen el contenido, nombres de archivo, rutas del sistema, trazas ni detalles internos.
- Las únicas referencias de ejecución son locales: dependencias declaradas en [../requirements.txt](../requirements.txt), configuración de herramientas en [../pyproject.toml](../pyproject.toml) y el contrato v1. Azure Blob no es una dependencia ni un requisito de esta entrega.
- Revise que el material de demostración, capturas y salidas compartidas solo contenga el fixture seguro incluido en el repositorio.

## Lista de cierre

- [ ] Las cuatro comprobaciones reproducibles terminan sin incidencias.
- [ ] La demostración usa el fixture seguro y devuelve el resultado esperado versionado.
- [ ] No se han añadido secretos, archivos `.env`, contenido sensible, artefactos de cobertura ni cachés.
- [ ] El contrato público, el README y esta guía describen la misma única operación local.
- [ ] La revisión de cambios no incluye rutas ajenas a este proyecto.
