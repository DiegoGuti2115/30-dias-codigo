# Despliegue y operación de producción

## Estado final

El catálogo se publica como aplicación Next.js estática con datos locales validados. No necesita variables de entorno, secretos, base de datos ni un proveedor externo para cargar el MVP; los enlaces **Código** navegan al repositorio público de GitHub y requieren red al abrirse.

No se ha creado una URL pública desde este entorno porque no hay cuenta ni permisos de un proveedor de hosting configurados. La versión de producción se puede ejecutar localmente de forma idéntica mediante:

```bash
npm run build
npm run start
```

La instancia de producción verificada en este entorno está disponible en [http://127.0.0.1:3000](http://127.0.0.1:3000). `localhost` puede usarse cuando el host local resuelva a la misma interfaz.

## Plataforma recomendada

Usar un hosting compatible con Next.js, preferiblemente Vercel o cualquier plataforma que ejecute `npm run build` y `npm run start`. La elección es reversible: la aplicación no usa APIs propietarias ni configuración específica de proveedor.

### Configuración mínima del proveedor

| Ajuste | Valor |
| --- | --- |
| Directorio raíz | `projects/day-30-project-catalog` si se despliega desde el repositorio completo; raíz del repositorio si se publica este proyecto de forma aislada. |
| Instalación | `npm install` o `npm ci` cuando exista un historial de lockfile versionado. |
| Build | `npm run build` |
| Inicio | `npm run start` si el proveedor requiere un proceso Node. |
| Variables de entorno | Ninguna. |

## Cabeceras de seguridad

[`next.config.ts`](../next.config.ts) aplica a todas las rutas:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

También desactiva el encabezado `X-Powered-By`. No se define una Content Security Policy restrictiva porque los enlaces **Código** navegan al monorepo público de GitHub; cualquier CSP futura debe permitir y comprobar ese destino antes de aplicarse.

## Checklist previo a una URL pública

1. Ejecutar los comandos de [`quality-verification.md`](quality-verification.md).
2. Completar la revisión manual de [`accessibility-test-matrix.md`](accessibility-test-matrix.md) y la comprobación limitada de [`performance-and-polish.md`](performance-and-polish.md).
3. Confirmar que cada enlace **Código** resuelve al directorio correspondiente en [`DiegoGuti2115/30-dias-codigo`](https://github.com/DiegoGuti2115/30-dias-codigo) y que la rama `main` está disponible.
4. Verificar la ruta `/`, búsqueda, filtros, restablecimiento, cero resultados, carga y recuperación de error en el dominio definitivo.
5. Comprobar las cabeceras anteriores desde la URL pública y registrar la URL en [`README.md`](../README.md) y [`publication-draft.md`](publication-draft.md).

## Verificación local realizada

El 30 de septiembre de 2026, el servidor de producción local respondió `200` en `http://127.0.0.1:3000/` con `Content-Type: text/html; charset=utf-8`, el título de catálogo y el contador inicial de 30 proyectos. También se verificaron `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy`; `X-Powered-By` no está presente.

## Rollback

El rollback consiste en restaurar el último despliegue correcto del proveedor o volver a desplegar el commit anterior. El fixture local sigue incluido en el artefacto de build, por lo que no requiere restaurar servicios ni datos externos.
