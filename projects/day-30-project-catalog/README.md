# Día 30 — Catálogo de proyectos

Aplicación web de cierre del reto [30 Días, 30 Proyectos](../../README.md). Reúne las 30 entregas en un catálogo local, accesible y verificable para descubrir proyectos, entender su propósito y abrir sus recursos validados en GitHub.

**Estado:** Fases 0 a 10 completadas. El catálogo usa datos locales validados, incluye recuperación ante errores y cuenta con una configuración de producción local verificable. La consulta del código de cada proyecto navega al repositorio público de GitHub y requiere conectividad.

## Funcionalidades entregadas

- Catálogo completo de 30 proyectos con día, categoría, resumen, tecnologías y enlace de código en GitHub.
- Búsqueda por nombre, resumen, categoría o tecnología.
- Filtros combinables de categoría y tecnología, contador anunciado y restablecimiento de criterios.
- Estados accesibles de carga, resultados vacíos, error de datos y error de renderizado recuperable.
- Navegación por teclado, enlace para saltar al contenido, foco visible, objetivos táctiles y reducción de movimiento.
- Carga de App Router con skeletons y filtrado diferido para conservar la respuesta de la interfaz.
- Renderizado estático y fixture reproducible, sin secretos, proveedores ni llamadas de red.

## Requisitos

- Node.js 20 o superior.
- npm.
- Un navegador moderno con JavaScript habilitado.

## Instalación y ejecución

Desde este directorio:

```bash
npm install
npm run dev
```

Abrir [http://localhost:3000](http://localhost:3000). Para comprobar la compilación servida localmente:

```bash
npm run build
npm run start
```

## Verificación

Ejecutar antes de revisar, demostrar o publicar:

```bash
npm run lint
npm test
npm run build
git diff --check
git status --short
```

La documentación ampliada de cobertura, límites y comprobaciones está en [`docs/quality-verification.md`](docs/quality-verification.md). La suite es determinista y no requiere red ni credenciales.

## Uso del catálogo

1. Escribir una palabra en **Buscar proyectos** o elegir categoría y tecnología.
2. Combinar criterios para acotar la colección; el contador anuncia los resultados.
3. Usar **Restablecer criterios** para volver a los 30 proyectos.
4. Abrir **Código** en una tarjeta para acceder al directorio validado del proyecto en [el monorepo de GitHub](https://github.com/DiegoGuti2115/30-dias-codigo).
5. Si no hay coincidencias, elegir **Ver todos los proyectos**. Si la fuente no puede prepararse, usar **Volver a intentar**.

## Datos, validación y fallback

[`data/projects.json`](data/projects.json) es la fuente principal y el fallback obligatorio del MVP. Antes de llegar a la interfaz, [`src/lib/catalog-schema.ts`](src/lib/catalog-schema.ts) valida con Zod:

- versión, estructura estricta y campos obligatorios;
- IDs, días y tecnologías únicos;
- categoría permitida y coherencia entre ID, día y ruta de repositorio;
- `repositoryPath` local coherente como metadato del checkout y enlaces HTTPS restringidos al directorio correspondiente en el monorepo de GitHub configurado.

[`src/lib/catalog-source.ts`](src/lib/catalog-source.ts) separa lectura y normalización. Los datos inválidos y los fallos de lectura devuelven resultados explícitos sin exponer una colección parcial. Una futura fuente remota debe ser opcional, mantener este fixture y conservar el mismo límite de validación.

## Arquitectura

```text
src/
├── app/                 # Rutas, layout, estados loading/error y estilos globales
├── components/          # Shell y estados visuales compartidos
├── features/catalog/    # Búsqueda, filtros, tarjetas y skeletons del dominio
├── lib/                 # Esquema Zod y fuente local validada
└── types/               # Contratos TypeScript del catálogo
data/projects.json       # Fixture local versionado y fallback
tests/                   # Contrato, dominio, interfaz, accesibilidad y recuperación
docs/                    # Demo, publicación, calidad, accesibilidad y rendimiento
```

Los componentes no leen archivos ni normalizan datos. La lógica de filtros vive en funciones puras y los componentes reciben únicamente el contrato validado.

## Accesibilidad y experiencia

- HTML semántico con landmarks, encabezados y regiones etiquetadas.
- Skip link, foco visible y controles nativos operables solo con teclado.
- Etiquetas, instrucciones y anuncios `aria-live` asociados a filtros y resultados.
- Estados comprensibles que no dependen únicamente del color.
- Diseño responsive desde 320 px, sin desplazamiento horizontal intencionado.
- Respeto de `prefers-reduced-motion` y hover aplicado únicamente cuando el dispositivo lo soporta.

Consultar la matriz manual de teclado, lector de pantalla, móvil, zoom, contraste y movimiento en [`docs/accessibility-test-matrix.md`](docs/accessibility-test-matrix.md).

## Rendimiento

La ruta `/` se prerenderiza de forma estática. La referencia de la última build es **4.9 kB** de JavaScript de ruta y **107 kB** de First Load JS compartido. Las tarjetas usan `content-visibility`, y los filtros se difieren durante entrada rápida sin cambiar el comportamiento del MVP. Detalles y revisión en dispositivos limitados: [`docs/performance-and-polish.md`](docs/performance-and-polish.md).

## Demo y publicación

- Guion de demostración de menos de 15 segundos: [`docs/demo-script.md`](docs/demo-script.md).
- Borrador de publicación y checklist previa: [`docs/publication-draft.md`](docs/publication-draft.md).
- Operación local de producción, plataforma recomendada, cabeceras, checklist y rollback: [`docs/deployment.md`](docs/deployment.md).
- **URL disponible en este entorno:** [http://localhost:3000](http://localhost:3000) al ejecutar `npm run build && npm run start`. Es una URL local, no pública.
- No se ha publicado una URL pública porque este entorno no dispone de cuenta ni permisos de hosting. La configuración no depende de proveedor y queda lista para desplegar cuando existan esas credenciales.

## Fuera de alcance del MVP

- Autenticación, cuentas, administración, colaboración o favoritos sincronizados.
- Base de datos, backend propio, analítica, CMS o integración autenticada con GitHub.
- Edición de proyectos desde la interfaz, recomendaciones de IA o comentarios.
- Recursos externos necesarios para cargar, buscar o filtrar el catálogo; los enlaces **Código** apuntan al repositorio público de GitHub.

## Seguridad y privacidad

No se versionan secretos, tokens ni archivos `.env` locales. El catálogo no renderiza HTML no confiable y valida enlaces antes de mostrarlos. Cualquier integración futura debe documentar permisos mínimos, límites, errores y fallback local.

## Licencia

Este proyecto forma parte del reto distribuido bajo licencia MIT. Consulta la licencia en la raíz del repositorio.
