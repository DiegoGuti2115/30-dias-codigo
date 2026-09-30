# Guion de demo reproducible

## Objetivo

Mostrar el flujo completo del MVP en menos de quince segundos, sin credenciales ni servicios externos. La carga, búsqueda y filtros usan el fixture local validado [`data/projects.json`](../data/projects.json); abrir **Código** requiere conexión para navegar al repositorio público de GitHub.

## Preparación

1. Desde la raíz del proyecto, ejecutar `npm run dev`.
2. Abrir [http://localhost:3000](http://localhost:3000).
3. Mantener el navegador en una ventana de escritorio o móvil; no se requiere iniciar sesión ni configurar variables de entorno.

## Recorrido principal — 12 a 15 segundos

| Tiempo | Acción | Resultado visible o anunciado |
| --- | --- | --- |
| 0–2 s | Abrir la página. | Aparece el catálogo estático con 30 proyectos; si la ruta entra en carga, se ve el estado con skeletons y mensaje anunciado. |
| 2–5 s | Escribir `Pomodoro` en **Buscar proyectos**. | El contador anuncia «1 proyecto encontrado» y queda visible **Temporizador Pomodoro**. |
| 5–8 s | Seleccionar una categoría y una tecnología, o usar **Restablecer criterios**. | Los filtros se combinan y el contador se actualiza sin recargar la página. |
| 8–11 s | Pulsar **Restablecer criterios**. | Regresan los 30 proyectos. |
| 11–15 s | Abrir **Código** en cualquier tarjeta. | El navegador navega al directorio validado del proyecto elegido en el monorepo público de GitHub. |

## Recorrido de recuperación opcional

1. Buscar `inexistente`.
2. Mostrar el mensaje «No encontramos proyectos con esos criterios».
3. Activar **Ver todos los proyectos** para recuperar los 30 resultados.

La recuperación de error de fuente y el límite de error de App Router están cubiertos por pruebas; no es necesario modificar el fixture durante una demo pública.

## Checklist previo

- Ejecutar los comandos de [`quality-verification.md`](quality-verification.md).
- Revisar la matriz de [`accessibility-test-matrix.md`](accessibility-test-matrix.md) si cambia el navegador, el viewport o la versión publicada.
- Comprobar que el enlace **Código** elegido apunta al directorio correspondiente en [`DiegoGuti2115/30-dias-codigo`](https://github.com/DiegoGuti2115/30-dias-codigo).
- No mostrar herramientas de desarrollo, datos locales ajenos ni tokens durante la grabación.
