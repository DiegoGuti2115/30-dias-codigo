# Revisión de seguridad: Dashboard de métricas

Fecha de revisión: 2026-09-21.

## Alcance revisado

- Código fuente de `src/`.
- Fixture de `data/metrics-dashboard.json`.
- Configuración y dependencias declaradas en `package.json`.
- Archivos de documentación y recursos de `assets/`.

## Hallazgos

### Secretos y configuración

- No hay variables de entorno, tokens, claves API, contraseñas ni cadenas de conexión en el proyecto.
- La fuente HTTP opcional recibe una URL explícita y no incorpora credenciales automáticamente.
- El fixture local contiene únicamente datos sintéticos de demostración.

### Validación de datos

- Toda fuente se valida mediante el esquema Zod antes de llegar a la interfaz.
- Las fechas, valores numéricos, identificadores y periodos tienen restricciones explícitas.
- Una respuesta HTTP no exitosa o inválida activa el fallback local.

### Interfaz

- No se renderiza HTML proveniente del dataset.
- Los valores se presentan mediante nodos React y no se evalúa contenido como código.
- Los controles de selección, la tabla y los estados de error tienen estructura semántica.

### Dependencias

- `npm audit` reporta vulnerabilidades transitivas pendientes en el árbol instalado. No se ejecutó `npm audit fix --force` porque podría introducir cambios incompatibles con el reto.
- El riesgo queda documentado para una actualización controlada posterior.

## Resultado

No se encontraron secretos versionables ni vulnerabilidades introducidas por el código de aplicación durante esta revisión. El riesgo residual principal está en las vulnerabilidades transitivas reportadas por npm y debe revisarse antes de un despliegue público.

## Validaciones ejecutadas

```bash
npm test
npm run lint
npm run build
```
