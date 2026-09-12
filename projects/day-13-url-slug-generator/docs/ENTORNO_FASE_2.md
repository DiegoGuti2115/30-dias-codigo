# Entorno local — Fase 2

## Decisiones de entorno

La Fase 2 usa **Node.js 22 o superior** y **npm 10 o superior**. Node 22 es una versión LTS compatible con TypeScript moderno y aporta una ejecución local estable sin añadir un runtime alternativo. npm se elige porque se distribuye con Node.js y evita incorporar otro gestor de paquetes para esta CLI atómica.

El entorno se declaró en [`package.json`](../package.json) mediante el campo `engines`. La instalación validada durante esta fase utilizó Node.js `v24.11.1` y npm `11.6.2`, compatibles con los mínimos definidos.

## Dependencias

Solo se declaran herramientas de desarrollo:

| Paquete       | Función                                            | Justificación                                                                   |
| ------------- | -------------------------------------------------- | ------------------------------------------------------------------------------- |
| `typescript`  | Compilación y comprobación estática.               | El proyecto está asignado al stack TypeScript.                                  |
| `@types/node` | Tipos del runtime de Node.js.                      | Prepara la futura CLI sin incluir código de ejecución adicional.                |
| `prettier`    | Formato determinista de archivos de configuración. | Mantiene una convención mínima sin introducir reglas de lint ajenas al alcance. |

No hay dependencias de producción, servicios remotos, variables de entorno, secretos ni configuración cloud.

## Instalación reproducible

Desde [`projects/day-13-url-slug-generator`](..):

```powershell
npm install
```

El archivo [`package-lock.json`](../package-lock.json) se versiona para fijar el árbol de dependencias. Una instalación limpia puede reproducirse con:

```powershell
npm ci
```

## Comandos de desarrollo

| Comando                | Propósito en la versión 1                                                                 |
| ---------------------- | ----------------------------------------------------------------------------------------- |
| `npm run build`        | Compila la CLI TypeScript y el núcleo hacia `dist/`.                                      |
| `npm run typecheck`    | Comprueba tipos sin emitir archivos.                                                      |
| `npm test`             | Recompila y ejecuta las pruebas unitarias y de proceso con el runner estándar de Node.js. |
| `npm run format`       | Aplica Prettier al código, configuración y documentación versionada.                      |
| `npm run format:check` | Verifica el formato sin modificar archivos.                                               |
| `npm run quality`      | Ejecuta comprobación de tipos y verificación de formato.                                  |

## Límites del entorno

El archivo [`src/environment.d.ts`](../src/environment.d.ts) permanece como ancla de compilación del entorno. La normalización, los argumentos, la ayuda y los canales de salida pertenecen respectivamente al núcleo y al adaptador CLI; sus pruebas automatizadas se ejecutan mediante `npm test`.

Los artefactos generados, como `node_modules/`, `dist/` y archivos de información de compilación, están cubiertos por las exclusiones de Node.js ya presentes en [`.gitignore`](../../../.gitignore) de la raíz. Para la instalación, ejecución y verificación de entrega, consulte [USO_LOCAL.md](USO_LOCAL.md).
