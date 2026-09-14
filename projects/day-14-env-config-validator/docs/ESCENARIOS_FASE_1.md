# Catálogo de escenarios — Fase 1

Este catálogo transforma el contrato [CONTRATO_V1.md](CONTRATO_V1.md) en vectores documentales para implementar y probar en fases posteriores. No es un fixture ejecutable, no requiere TypeScript ni incorpora valores secretos reales.

## Convenciones

- Los nombres y valores son sintéticos. `demo-token-12345` es un valor ficticio reservado para describir redacción y no debe aparecer en resultados públicos futuros.
- `OK` representa una configuración aceptada y un resumen JSON con `valid: true`.
- `ERROR` representa una envoltura JSON en stderr con la categoría, identificador y código de proceso indicados.
- `WARN` representa un resultado correcto con una advertencia en el resumen JSON.
- `ENV:` muestra contenido conceptual del archivo `.env`; `SCHEMA:` resume solo las reglas relevantes del esquema JSON v1.
- La Fase 2 podrá convertir estos casos en fixtures sintéticos sin alterar su significado. Las Fases 3 a 6 deberán mantener la trazabilidad de los identificadores.

## Interfaz de CLI y códigos de proceso

| ID   | Invocación conceptual                               | Estado | stdout       | stderr / código                | Regla                            |
| ---- | --------------------------------------------------- | ------ | ------------ | ------------------------------ | -------------------------------- |
| C-01 | `env-config-validator demo.env schema.json`         | OK     | Resumen JSON | Vacía / `0`                    | Dos rutas y datos válidos.       |
| C-02 | `env-config-validator --help`                       | OK     | Ayuda exacta | Vacía / `0`                    | Ayuda aislada.                   |
| C-03 | `env-config-validator -h`                           | OK     | Ayuda exacta | Vacía / `0`                    | Ayuda corta aislada.             |
| C-04 | `env-config-validator`                              | ERROR  | Vacía        | `E_USAGE_ARGUMENTS` / `2`      | Faltan rutas.                    |
| C-05 | `env-config-validator demo.env`                     | ERROR  | Vacía        | `E_USAGE_ARGUMENTS` / `2`      | Falta esquema.                   |
| C-06 | `env-config-validator a.env b.json extra`           | ERROR  | Vacía        | `E_USAGE_ARGUMENTS` / `2`      | Hay argumentos adicionales.      |
| C-07 | `env-config-validator --help demo.env schema.json`  | ERROR  | Vacía        | `E_USAGE_ARGUMENTS` / `2`      | Ayuda combinada.                 |
| C-08 | `env-config-validator --format json a.env b.json`   | ERROR  | Vacía        | `E_USAGE_UNKNOWN_OPTION` / `2` | No hay opciones adicionales.     |
| C-09 | Ruta `.env` inexistente o no legible                | ERROR  | Vacía        | `E_INPUT_READ` / `3`           | Error de entrada.                |
| C-10 | Archivo `.env` con UTF-8 inválido                   | ERROR  | Vacía        | `E_INPUT_NOT_UTF8` / `3`       | Codificación no admitida.        |
| C-11 | Archivo `.env` con línea no asignable               | ERROR  | Vacía        | `E_INPUT_ENV_PARSE` / `3`      | Sintaxis `.env` inválida.        |
| C-12 | Esquema con JSON inválido                           | ERROR  | Vacía        | `E_SCHEMA_JSON_PARSE` / `4`    | JSON no interpretable.           |
| C-13 | Esquema semánticamente inválido                     | ERROR  | Vacía        | `E_SCHEMA_INVALID` / `4`       | Reglas incompatibles.            |
| C-14 | Configuración contra esquema válido con incidencias | ERROR  | Vacía        | `E_CONFIG_*` / `5`             | Incumplimiento de configuración. |

## Presencia, vacío y valores por defecto

Supóngase una variable `NAME` de tipo `string`, salvo que se indique otra regla.

| ID   | ENV          | SCHEMA                                          | Estado           | Resultado o diagnóstico           | Regla cubierta              |
| ---- | ------------ | ----------------------------------------------- | ---------------- | --------------------------------- | --------------------------- |
| P-01 | `NAME=alice` | `required: true`                                | OK               | `NAME`: `valid`, origen `env`     | Valor presente.             |
| P-02 | Sin `NAME`   | `required: true`                                | ERROR            | `E_CONFIG_REQUIRED`               | Obligatoria ausente.        |
| P-03 | `NAME=`      | `required: true, minLength: 1`                  | ERROR            | `E_CONFIG_CONSTRAINT`             | Vacío presente, no ausente. |
| P-04 | Sin `NAME`   | `required: false`                               | OK               | `NAME`: `absent`, origen `none`   | Opcional ausente.           |
| P-05 | Sin `NAME`   | `required: true, default: "demo"`               | OK               | `NAME`: `valid`, origen `default` | Defecto cubre ausencia.     |
| P-06 | `NAME=`      | `required: true, default: "demo", minLength: 1` | ERROR            | `E_CONFIG_CONSTRAINT`             | Defecto no sustituye vacío. |
| P-07 | Sin `NAME`   | `required: false, default: "demo"`              | OK               | `NAME`: `valid`, origen `default` | Defecto opcional.           |
| P-08 | Sin `NAME`   | `required: true, default: 4` para `string`      | ERROR de esquema | `E_SCHEMA_INVALID`                | Defecto incompatible.       |

## Tipos y restricciones

| ID   | ENV                                   | SCHEMA relevante                            | Estado | Resultado o diagnóstico | Regla cubierta                 |
| ---- | ------------------------------------- | ------------------------------------------- | ------ | ----------------------- | ------------------------------ |
| T-01 | `TITLE=Servicio demo`                 | `string, minLength: 3, maxLength: 32`       | OK     | `TITLE` válida          | Cadena dentro de límites.      |
| T-02 | `TITLE=ab`                            | `string, minLength: 3`                      | ERROR  | `E_CONFIG_CONSTRAINT`   | Longitud mínima.               |
| T-03 | `REGION=eu-west-1`                    | `string, pattern: ^[a-z]+-[a-z]+-[0-9]+$`   | OK     | `REGION` válida         | Patrón válido.                 |
| T-04 | `REGION=EU WEST`                      | Patrón de T-03                              | ERROR  | `E_CONFIG_CONSTRAINT`   | Patrón no satisfecho.          |
| T-05 | `APP_PORT=3000`                       | `number, integer: true, min: 1, max: 65535` | OK     | `APP_PORT` válida       | Entero dentro de límites.      |
| T-06 | `APP_PORT=3.5`                        | `number, integer: true`                     | ERROR  | `E_CONFIG_CONSTRAINT`   | Entero requerido.              |
| T-07 | `APP_PORT=Infinity`                   | `number`                                    | ERROR  | `E_CONFIG_TYPE`         | Número no finito.              |
| T-08 | `ENABLED=true`                        | `boolean`                                   | OK     | `ENABLED` válida        | Booleano literal.              |
| T-09 | `ENABLED=TRUE`                        | `boolean`                                   | ERROR  | `E_CONFIG_TYPE`         | Mayúsculas sin transformación. |
| T-10 | `PLAN=pro`                            | `enum, values: ["free", "pro"]`             | OK     | `PLAN` válida           | Enumeración.                   |
| T-11 | `PLAN=enterprise`                     | Enum de T-10                                | ERROR  | `E_CONFIG_CONSTRAINT`   | Valor fuera de enumeración.    |
| T-12 | `PUBLIC_URL=https://example.test/api` | `url`                                       | OK     | `PUBLIC_URL` válida     | URL HTTPS absoluta.            |
| T-13 | `PUBLIC_URL=ftp://example.test`       | `url`                                       | ERROR  | `E_CONFIG_CONSTRAINT`   | Protocolo no permitido.        |
| T-14 | `PUBLIC_URL=https://example.test`     | `url, protocols: ["https:"]`                | OK     | `PUBLIC_URL` válida     | Protocolo personalizado.       |

## Listas JSON y transformaciones

| ID   | ENV                      | SCHEMA relevante                                               | Estado           | Resultado o diagnóstico     | Regla cubierta                      |
| ---- | ------------------------ | -------------------------------------------------------------- | ---------------- | --------------------------- | ----------------------------------- |
| L-01 | `HOSTS=["api","worker"]` | `list, items: string, minItems: 1`                             | OK               | `HOSTS` válida              | Lista JSON de cadenas.              |
| L-02 | `PORTS=[3000,3001]`      | `list, items: number`                                          | OK               | `PORTS` válida              | Lista JSON de números.              |
| L-03 | `FLAGS=[true,false]`     | `list, items: boolean`                                         | OK               | `FLAGS` válida              | Lista JSON de booleanos.            |
| L-04 | `HOSTS=["api",2]`        | `list, items: string`                                          | ERROR            | `E_CONFIG_TYPE`             | Elementos no homogéneos.            |
| L-05 | `HOSTS={"api":true}`     | `list, items: string`                                          | ERROR            | `E_CONFIG_TYPE`             | Debe ser array JSON.                |
| L-06 | `HOSTS=api,worker`       | `list, items: string`                                          | ERROR            | `E_CONFIG_TYPE`             | Sin JSON ni `splitComma`.           |
| L-07 | `HOSTS=api, worker`      | `list, items: string, transforms: ["splitComma"]`              | OK               | `HOSTS` válida              | Separación segura por coma.         |
| L-08 | `HOSTS=`                 | `list, items: string, transforms: ["splitComma"]`              | OK               | Lista con un elemento vacío | Semántica de cadena vacía.          |
| L-09 | `TITLE=  Mi Servicio  `  | `string, transforms: ["trim"]`                                 | OK               | `TITLE` válida              | Recorte Unicode.                    |
| L-10 | `ENABLED=TRUE`           | `boolean, transforms: ["lowercase"]`                           | OK               | `ENABLED` válida            | Transformación antes de conversión. |
| L-11 | `PLAN=PRO`               | `enum, values: ["free", "pro"], transforms: ["lowercase"]`     | OK               | `PLAN` válida               | Transformación antes de enum.       |
| L-12 | `PORTS=[3000]`           | `number, transforms: ["parseJson"]`                            | ERROR de esquema | `E_SCHEMA_INVALID`          | Transformación incompatible.        |
| L-13 | `HOSTS=api,worker`       | `list, items: string, transforms: ["splitComma", "parseJson"]` | ERROR de esquema | `E_SCHEMA_INVALID`          | Transformaciones incompatibles.     |
| L-14 | `TITLE=x`                | `string, transforms: ["executeJs"]`                            | ERROR de esquema | `E_SCHEMA_INVALID`          | Código no permitido.                |

## Patrones y restricciones inválidas de esquema

| ID   | Fragmento de esquema              | Estado | Diagnóstico                | Regla cubierta                |
| ---- | --------------------------------- | ------ | -------------------------- | ----------------------------- |
| S-01 | `pattern.source: "("`             | ERROR  | `E_SCHEMA_INVALID_PATTERN` | RegExp inválida.              |
| S-02 | `pattern.flags: "g"`              | ERROR  | `E_SCHEMA_INVALID`         | Flag no permitido.            |
| S-03 | `pattern.source` de 257 unidades  | ERROR  | `E_SCHEMA_INVALID`         | Límite de patrón.             |
| S-04 | `minLength: 8, maxLength: 4`      | ERROR  | `E_SCHEMA_INVALID`         | Límites invertidos.           |
| S-05 | `type: "number", pattern: {...}`  | ERROR  | `E_SCHEMA_INVALID`         | Restricción ajena al tipo.    |
| S-06 | `type: "enum", values: []`        | ERROR  | `E_SCHEMA_INVALID`         | Enum vacío.                   |
| S-07 | `type: "list", items: "object"`   | ERROR  | `E_SCHEMA_INVALID`         | Elemento no admitido.         |
| S-08 | Regla con `script: "return true"` | ERROR  | `E_SCHEMA_UNKNOWN_FIELD`   | Campo ejecutable desconocido. |
| S-09 | Raíz con `version: "v2"`          | ERROR  | `E_SCHEMA_INVALID`         | Versión no admitida.          |
| S-10 | Raíz con `plugins: []`            | ERROR  | `E_SCHEMA_UNKNOWN_FIELD`   | Plugins fuera de alcance.     |

## Claves no declaradas

| ID   | ENV                           | SCHEMA                                | Estado | Resultado o diagnóstico                        | Regla cubierta                     |
| ---- | ----------------------------- | ------------------------------------- | ------ | ---------------------------------------------- | ---------------------------------- |
| U-01 | `KNOWN=x`, `LEGACY_FLAG=on`   | Declara `KNOWN`, `unknownKeys: allow` | OK     | Sin advertencia para `LEGACY_FLAG`             | Ignorar desconocida.               |
| U-02 | Mismo ENV                     | Declara `KNOWN`, `unknownKeys: warn`  | WARN   | `W_CONFIG_UNKNOWN_KEY` con clave `LEGACY_FLAG` | Advertencia.                       |
| U-03 | Mismo ENV                     | Declara `KNOWN`, `unknownKeys: error` | ERROR  | `E_CONFIG_UNKNOWN_KEY`                         | Desconocida invalida.              |
| U-04 | `UNDECLARED=demo-token-12345` | `unknownKeys: warn`                   | WARN   | Advertencia sin valor                          | Valor de desconocida no se filtra. |

## Dependencias

| ID   | ENV                                                  | Dependencia                                     | Estado           | Resultado o diagnóstico         | Regla cubierta                   |
| ---- | ---------------------------------------------------- | ----------------------------------------------- | ---------------- | ------------------------------- | -------------------------------- |
| D-01 | `CLIENT_ID=demo`, `CLIENT_SECRET=placeholder-value`  | `allOrNone: [CLIENT_ID, CLIENT_SECRET]`         | OK               | Ambas válidas                   | Grupo completo.                  |
| D-02 | `CLIENT_ID=demo`                                     | `allOrNone: [CLIENT_ID, CLIENT_SECRET]`         | ERROR            | `E_CONFIG_ALL_OR_NONE`          | Grupo parcial.                   |
| D-03 | Sin ambas claves                                     | `allOrNone: [CLIENT_ID, CLIENT_SECRET]`         | OK               | Sin incidencia                  | Grupo ausente completo.          |
| D-04 | `SMTP_USER=demo`                                     | `requires: SMTP_USER -> SMTP_PASSWORD`          | ERROR            | `E_CONFIG_REQUIRES`             | Requiere clave ausente.          |
| D-05 | `SMTP_USER=demo`, `SMTP_PASSWORD=placeholder-value`  | Misma regla                                     | OK               | Sin incidencia                  | Requisito satisfecho.            |
| D-06 | `LOCAL_MODE=true`, `REMOTE_URL=https://example.test` | `forbids: LOCAL_MODE -> REMOTE_URL`             | ERROR            | `E_CONFIG_FORBIDS`              | Presencia simultánea prohibida.  |
| D-07 | `LOCAL_MODE=true`                                    | Misma regla                                     | OK               | Sin incidencia                  | Solo una clave presente.         |
| D-08 | `A=x`                                                | `requires: A -> MISSING` sin declarar `MISSING` | ERROR de esquema | `E_SCHEMA_UNKNOWN_REFERENCE`    | Referencia desconocida.          |
| D-09 | Sin `TOKEN`, defecto de `TOKEN` presente             | `requires: TOKEN -> ENDPOINT`                   | ERROR            | `E_CONFIG_REQUIRES`             | El defecto cuenta como presente. |
| D-10 | `A=x`, `B=y`                                         | Dos reglas estructuralmente idénticas           | ERROR de esquema | `E_SCHEMA_DUPLICATE_DEPENDENCY` | Dependencia duplicada.           |

## Redacción de secretos y envoltorios públicos

| ID   | ENV                                  | SCHEMA                                                         | Estado | Resultado o diagnóstico público                  | Regla cubierta             |
| ---- | ------------------------------------ | -------------------------------------------------------------- | ------ | ------------------------------------------------ | -------------------------- |
| R-01 | `API_TOKEN=demo-token-12345`         | `API_TOKEN: string, secret: true, minLength: 12`               | OK     | Variable con `secret: true`, sin valor           | Secreto válido redacted.   |
| R-02 | `API_TOKEN=short`                    | `API_TOKEN: string, secret: true, minLength: 12`               | ERROR  | `E_CONFIG_CONSTRAINT`; sin `short`               | Error de secreto redacted. |
| R-03 | Sin `API_TOKEN`                      | `API_TOKEN: string, secret: true, required: true`              | ERROR  | `E_CONFIG_REQUIRED`; sin valores                 | Falta secreto.             |
| R-04 | Sin `API_TOKEN`                      | `API_TOKEN: string, secret: true, default: "demo-token-12345"` | OK     | Origen `default`, sin valor ni longitud          | Defecto secreto redacted.  |
| R-05 | Cualquier fallo de entrada o esquema | Cualquier esquema                                              | ERROR  | `issues` no incluye contenido ni rutas absolutas | Diagnóstico seguro.        |

## Trazabilidad para fases posteriores

- La Fase 2 prepara únicamente el entorno necesario para convertir este catálogo en pruebas, sin cambiar el contrato.
- La Fase 3 implementará la validación y compilación de `S-*`, y rechazará los casos de esquema indicados antes de procesar `.env`.
- La Fase 4 implementará el pipeline de `P-*`, `T-*`, `L-*`, `U-*`, `D-*` y `R-*` sobre datos ya parseados.
- La Fase 5 implementará los casos `C-*` y la adaptación de archivos/códigos de proceso.
- La Fase 6 automatizará las regresiones, incluido que los valores ficticios de `R-*` y `U-04` no aparezcan en ninguna salida pública.
- Todo cambio de vector exige actualizar el contrato y justificarlo en [DECISIONES.md](DECISIONES.md).
