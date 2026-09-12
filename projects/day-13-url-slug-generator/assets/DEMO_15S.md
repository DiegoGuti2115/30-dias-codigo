# Demostración local — 15 segundos

Demostración breve, local y sin datos sensibles para el Generador de slugs v1.

## Preparación

Desde `projects/day-13-url-slug-generator`, ejecute una vez:

```powershell
npm run build
```

## Guion

| Tiempo aproximado | Acción en terminal                             | Resultado observable                                                       |
| ----------------- | ---------------------------------------------- | -------------------------------------------------------------------------- |
| 0–3 s             | Mostrar el título del proyecto y el comando.   | Se identifica una CLI TypeScript local.                                    |
| 3–8 s             | `node dist/cli.js "Guía rápida de TypeScript"` | `guia-rapida-de-typescript` en salida estándar.                            |
| 8–12 s            | `node dist/cli.js "Straße & Æsir"`             | `strasse-aesir` en salida estándar.                                        |
| 12–15 s           | `node dist/cli.js "---"`                       | Diagnóstico de contenido no normalizable por salida de error y código `1`. |

## Mensaje de cierre

La CLI acepta un único texto, genera un slug ASCII determinista y comunica los errores mediante texto plano y códigos de salida. No usa red, secretos, archivos de usuario ni servicios externos.
