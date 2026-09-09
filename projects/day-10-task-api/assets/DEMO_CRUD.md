# Demostración CRUD corta

Ejecute primero la API desde [`../README.md`](../README.md):

```powershell
python -m uvicorn src.main:app --reload
```

Con el servidor disponible en `http://127.0.0.1:8000`, ejecute estos comandos de PowerShell en otra terminal. La demostración usa solo datos ficticios y cubre creación, consulta, actualización parcial, listado y eliminación.

## 1. Crear una tarea

```powershell
$task = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/tasks -ContentType 'application/json' -Body '{"title":"Preparar demostración","description":"Ejecutar el flujo CRUD","completed":false}'
$task
```

Resultado esperado: estado HTTP `201` y una tarea con `id` positivo, fechas UTC y `completed` en `false`.

## 2. Consultar la tarea creada

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/tasks/$($task.id)"
```

Resultado esperado: estado HTTP `200` y la misma representación.

## 3. Actualizar parcialmente su estado

```powershell
$updated = Invoke-RestMethod -Method Patch -Uri "http://127.0.0.1:8000/api/v1/tasks/$($task.id)" -ContentType 'application/json' -Body '{"completed":true}'
$updated
```

Resultado esperado: estado HTTP `200`, `completed` en `true`, `created_at` sin cambios y `updated_at` actualizado.

## 4. Listar la colección

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/api/v1/tasks
```

Resultado esperado: estado HTTP `200` y un objeto con `items`, que contiene la tarea actualizada en orden de creación.

## 5. Eliminar la tarea

```powershell
Invoke-WebRequest -Method Delete -Uri "http://127.0.0.1:8000/api/v1/tasks/$($task.id)" | Select-Object StatusCode, Content
```

Resultado esperado: estado HTTP `204` y cuerpo vacío. Una consulta posterior al mismo identificador devuelve `404` con el código `task_not_found`.

La colección se conserva solo mientras la instancia de Uvicorn esté activa. Al detener y reiniciar el servidor, el listado vuelve a estar vacío.
