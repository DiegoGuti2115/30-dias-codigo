# Uso local — Validador de configuración

## Requisitos

- Node.js `>=22.0.0`.
- npm `>=10.0.0`.
- Dos archivos locales explícitos: un `.env` y un esquema JSON `v1`.

La herramienta no usa red, cuentas, credenciales propias ni `process.env`. No busca archivos automáticamente ni modifica las entradas.

## Instalación limpia

Desde [`projects/day-14-env-config-validator`](..):

```text
npm ci
npm run build
```

La compilación genera [`dist/cli.js`](../dist/cli.js), que está ignorado por Git junto con [`node_modules`](../node_modules).

## Uso

Ejecuta la CLI con exactamente dos rutas posicionales:

```text
node ./dist/cli.js <ruta-env> <ruta-schema>
```

También está disponible el nombre declarado por el paquete después de compilar:

```text
npm exec -- env-config-validator <ruta-env> <ruta-schema>
```

La ayuda no requiere archivos:

```text
node ./dist/cli.js --help
node ./dist/cli.js -h
```

La ayuda se escribe como texto plano en stdout y termina con código `0`.

## Ejecución reproducible con datos sintéticos

Los fixtures versionados no son una configuración real y solo usan valores ficticios. Desde el directorio del proyecto:

```text
node ./dist/cli.js ./data/fixtures/valid-configuration.env ./data/fixtures/valid-schema.json
```

El comando termina con código `0`, escribe un único JSON en stdout y deja stderr vacío. El resumen contiene estado, origen y el indicador `secret`, pero nunca valores de configuración.

Para observar un fallo seguro de configuración:

```text
node ./dist/cli.js ./data/fixtures/invalid-configuration.env ./data/fixtures/valid-schema.json
```

El comando termina con código `5`, deja stdout vacío y escribe un único JSON de error en stderr. Sus incidencias describen claves y reglas, sin incluir los valores recibidos.

Puedes comparar las envolturas públicas con [`data/expected/valid-summary.json`](../data/expected/valid-summary.json) y [`data/expected/invalid-configuration.json`](../data/expected/invalid-configuration.json). No copies los valores de los fixtures a documentación, capturas ni logs.

## Canales y códigos de salida

| Situación                                                  | stdout          | stderr        | Código |
| ---------------------------------------------------------- | --------------- | ------------- | ------ |
| Validación correcta                                        | Un resumen JSON | Vacío         | `0`    |
| Ayuda aislada                                              | Texto plano     | Vacío         | `0`    |
| Uso inválido u opción desconocida                          | Vacío           | Un error JSON | `2`    |
| Archivo no legible, no regular, no UTF-8 o `.env` inválido | Vacío           | Un error JSON | `3`    |
| JSON de esquema inválido o esquema incompatible            | Vacío           | Un error JSON | `4`    |
| Configuración que incumple un esquema válido               | Vacío           | Un error JSON | `5`    |
| Fallo interno controlado                                   | Vacío           | Un error JSON | `1`    |

Los detalles de códigos, envolturas y semántica están en [`CONTRATO_V1.md`](CONTRATO_V1.md).

## Esquema mínimo

El esquema debe ser JSON estricto con `version: "v1"` y un mapa no vacío de variables. Este ejemplo es sintético y no incluye secretos:

```json
{
  "version": "v1",
  "variables": {
    "APP_PORT": {
      "type": "number",
      "required": true,
      "integer": true,
      "min": 1,
      "max": 65535
    }
  }
}
```

Consulta la gramática completa, transformaciones permitidas, restricciones y dependencias en [`CONTRATO_V1.md`](CONTRATO_V1.md). La CLI rechaza campos desconocidos, sintaxis no JSON y construcciones ejecutables; no interpreta YAML, TOML, expresiones, comandos, imports ni plugins.

## Comprobación antes de entregar

Desde el directorio del proyecto ejecuta:

```text
npm run format:check
npm run build
npm run typecheck
npm test
npm run quality
```

La suite cubre el compilador de esquema, el motor puro, la CLI y regresiones con fixtures sintéticos. No depende de red, hora, zona horaria, configuración regional, credenciales ni variables de entorno de la máquina.

## Solución de problemas

| Síntoma                         | Acción local                                                                                                           |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `npm ci` falla                  | Comprueba las versiones de Node.js y npm indicadas arriba y ejecuta el comando dentro del proyecto.                    |
| No existe `dist/cli.js`         | Ejecuta `npm run build` antes de invocar la CLI.                                                                       |
| Código `2`                      | Ejecuta `node ./dist/cli.js --help` y proporciona exactamente las dos rutas solicitadas.                               |
| Código `3`                      | Comprueba que ambas rutas existen, apuntan a archivos regulares UTF-8 y que el `.env` usa asignaciones `NOMBRE=valor`. |
| Código `4`                      | Valida que el esquema sea JSON estricto y cumpla la gramática `v1`; revisa las incidencias JSON de stderr.             |
| Código `5`                      | Corrige las claves o reglas indicadas en el error JSON; los valores no se muestran por diseño.                         |
| Necesitas investigar una salida | Redirige stdout y stderr por separado; no añadas logs con contenido de `.env` ni valores secretos.                     |

## Límites operativos

Esta validación confirma solo que los dos archivos explícitos cumplen el contrato local. No verifica conectividad, credenciales, DNS, seguridad de URLs ni la compatibilidad final con una aplicación consumidora. La herramienta es atómica y sin estado: lee entradas, valida y finaliza sin escribir archivos ni conservar datos.
