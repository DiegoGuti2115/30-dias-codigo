# Demo local de 15 segundos — Validador de configuración

## Preparación

Ejecuta la demo desde [`projects/day-14-env-config-validator`](..), después de una instalación limpia y compilación:

```text
npm ci
npm run build
```

Los archivos usados son [`data/fixtures/valid-configuration.env`](../data/fixtures/valid-configuration.env), [`data/fixtures/invalid-configuration.env`](../data/fixtures/invalid-configuration.env) y [`data/fixtures/valid-schema.json`](../data/fixtures/valid-schema.json). Son datos sintéticos; no abras ni muestres su contenido durante la grabación.

## Guion

| Tiempo  | Acción visible                                                        | Narración o texto                                                            |
| ------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 0–2 s   | Muestra el título y el comando de ayuda.                              | “Valido un `.env` explícito contra un esquema JSON local.”                   |
| 2–7 s   | Ejecuta la validación correcta.                                       | “El caso válido devuelve un único resumen JSON por stdout.”                  |
| 7–11 s  | Señala `"valid":true`, el contador de advertencias y `"secret":true`. | “El resumen solo muestra estado y origen; el secreto nunca aparece.”         |
| 11–15 s | Ejecuta el caso inválido redirigiendo stderr y muestra su JSON.       | “El caso inválido usa stderr y código de salida cinco, sin revelar valores.” |

## Comandos de grabación

```text
node ./dist/cli.js --help
node ./dist/cli.js ./data/fixtures/valid-configuration.env ./data/fixtures/valid-schema.json
node ./dist/cli.js ./data/fixtures/invalid-configuration.env ./data/fixtures/valid-schema.json 2> demo-error.json
```

El tercer comando termina con código `5`. Para mostrar el error de forma separada, usa:

```text
Get-Content ./demo-error.json
Remove-Item ./demo-error.json
```

En una terminal POSIX, el equivalente es `cat demo-error.json` y `rm demo-error.json`.

## Reglas de seguridad de la demo

- No muestres el contenido de los archivos `.env`, incluidos los fixtures sintéticos.
- No incluyas valores de variables en narración, captura, subtítulos, nombre de archivo ni logs.
- Muestra solo las envolturas públicas: el resumen correcto contiene `secret: true` sin valor y el error solo enumera claves, códigos y reglas.
- No uses red, servicios externos, `process.env`, credenciales ni una aplicación adicional.
- Elimina el archivo temporal `demo-error.json` al terminar; no es una salida persistente del proyecto.

La forma de la CLI, los canales y los códigos están definidos en [`docs/CONTRATO_V1.md`](../docs/CONTRATO_V1.md); la guía detallada de instalación y comprobación está en [`docs/USO_LOCAL.md`](../docs/USO_LOCAL.md).
