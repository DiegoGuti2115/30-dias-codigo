# Uso local y verificación de entrega

Esta guía permite instalar, ejecutar y comprobar el Generador de slugs v1 en una terminal local. El comportamiento normativo de normalización, ayuda, errores y códigos de salida está definido en [CONTRATO_V1.md](CONTRATO_V1.md).

## Requisitos

- Node.js 22 o superior.
- npm 10 o superior.
- Una terminal con UTF-8 para visualizar los ejemplos con acentos.

No se requieren variables de entorno, secretos, red, servicios externos ni datos de usuario.

## Instalación limpia

Desde `projects/day-13-url-slug-generator`:

```powershell
npm ci
```

`npm ci` instala exactamente las herramientas bloqueadas en `package-lock.json`. Los directorios `node_modules/` y `dist/` son generados y están excluidos del control de versiones.

## Compilación y ejecución

Compile la CLI antes de invocarla:

```powershell
npm run build
node dist/cli.js "Guía rápida de TypeScript"
```

Salida esperada:

```text
guia-rapida-de-typescript
```

El manifiesto declara además el binario local `slug-generator`. Tras instalar el paquete como dependencia local, la misma interfaz es:

```text
slug-generator <texto>
```

El texto es el único argumento posicional. Inclúyalo entre comillas si contiene espacios.

## Ayuda, canales y códigos de salida

```powershell
node dist/cli.js --help
node dist/cli.js -h
```

- Un slug correcto y la ayuda se escriben en salida estándar y terminan con código `0`.
- Un error de contenido se escribe en salida de error y termina con código `1`.
- Un error de uso se escribe en salida de error y termina con código `2`.
- La herramienta no usa color, interacción ni entrada estándar; sus mensajes son texto plano apto para redirección y lectores de pantalla.

Ejemplos de errores controlados:

```powershell
node dist/cli.js
node dist/cli.js "---"
node dist/cli.js --unicode "Hola"
```

Consulte los mensajes exactos y la tabla completa de diagnósticos en [CONTRATO_V1.md](CONTRATO_V1.md).

## Comprobación de calidad

Ejecute los comandos siguientes desde el directorio del proyecto:

```powershell
npm run format
npm run quality
npm run build
npm test
```

- `format` aplica Prettier a los archivos configurados.
- `quality` ejecuta TypeScript sin emisión y verifica formato.
- `build` genera la CLI en `dist/`.
- `test` recompila y ejecuta las pruebas unitarias y de proceso con el runner integrado de Node.js.

La suite es local y determinista: no depende de hora, zona horaria, configuración regional, red, secretos ni datos personales.

## Límites de la versión 1

La utilidad normaliza una sola entrada de texto y no resuelve colisiones, no persiste valores, no procesa lotes, no lee archivos ni entrada estándar, y no translitera exhaustivamente alfabetos no latinos. Para las reglas exactas, consulte [README.md](../README.md) y [DECISIONES.md](DECISIONES.md).
