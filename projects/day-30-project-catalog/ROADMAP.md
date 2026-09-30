# Roadmap — Catálogo de proyectos

## Propósito del plan

Este roadmap organiza la evolución del Catálogo de proyectos desde una base documental y técnica hasta una aplicación lista para mostrar y desplegar. El orden prioriza un MVP local, accesible y verificable antes de añadir mejoras visuales, optimizaciones o integraciones opcionales.

**Estado actual:** Fases 0 a 10 completadas. El catálogo valida sus datos locales en el límite, comunica fallos recuperables y queda cerrado con una operación de producción local verificable. Los enlaces **Código** se restringen al directorio correspondiente del monorepo público de GitHub; abrirlos requiere red, pero el catálogo sigue funcionando sin secretos ni servicios remotos.

## Principios de ejecución

- Mantener el alcance atómico: primero descubrir y acceder a proyectos; las capacidades secundarias solo se añadirán si no comprometen el MVP.
- Conservar `data/projects.json` como fuente local reproducible y fallback de toda integración futura.
- Separar contrato, servicios, lógica de catálogo y presentación según la estructura descrita en [README.md](README.md).
- Incorporar accesibilidad, validación, gestión de errores y pruebas dentro de cada fase, no como correcciones finales.
- No introducir secretos ni servicios obligatorios que impidan ejecutar la demo local.

## Dependencias globales

- Node.js 20 o superior y npm.
- Dependencias declaradas en `package.json` e instaladas con `npm install`.
- El fixture `data/projects.json` disponible para desarrollo, pruebas y demo.
- Las decisiones y comandos de [README.md](README.md) prevalecen sobre este plan si evolucionan de forma documentada.

---

## Fase 0 — Definición y planificación inicial

**Prioridad:** completada

### Objetivo

Alinear el propósito de portfolio, el alcance del MVP, los límites del proyecto y los criterios que permitirán avanzar sin reorganizaciones posteriores.

### Tareas principales

- Documentar problema, objetivo, funcionalidades previstas y exclusiones en `README.md`.
- Definir la fuente local como ruta principal del MVP y como fallback obligatorio.
- Establecer convenciones de calidad, accesibilidad, privacidad y demostración.
- Crear este roadmap con dependencias y criterios de finalización trazables.

### Dependencias

- Normas del reto establecidas en el README de la raíz del repositorio.

### Criterios de finalización

- El alcance evita backend, autenticación e integraciones obligatorias.
- La documentación explica cómo continuar el proyecto sin contexto adicional.
- La fuente de datos y el fallback están definidos sin requerir secretos.

### Resultado esperado

Una visión compartida y acotada del Catálogo de proyectos, preparada para orientar las decisiones técnicas y funcionales.

---

## Fase 1 — Arquitectura y configuración del proyecto

**Prioridad:** alta
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- Base de Next.js 15 con App Router, React 19 y TypeScript estricto en `src/app/`; la página raíz es intencionadamente un shell sin lógica de producto.
- Scripts `dev`, `build`, `start`, `lint` y `test` en `package.json`; Vitest permite una suite vacía temporalmente porque la fase no incorpora comportamiento verificable.
- Tailwind CSS mediante PostCSS, ESLint con reglas `next/core-web-vitals` y exclusión de artefactos generados, y configuración de pruebas en JSDOM.
- Alias `@/*` hacia `src/*`, resolución de JSON y objetivo ECMAScript 2022 en `tsconfig.json`.
- `outputFileTracingRoot` se fija en `next.config.ts` al directorio del proyecto para aislar los trazados de Next.js ante los lockfiles del workspace padre.
- Puntos de extensión creados y conservados con `.gitkeep` solo en directorios sin responsabilidad de archivo actual: `src/components/`, `src/features/catalog/`, `src/lib/`, `src/types/`, `tests/`, `assets/` y `docs/`.
- `data/projects.json` permanece como colección versionada vacía: poblarla, tiparla y validarla corresponde exclusivamente a la Fase 2.
- `.gitignore` y `package-lock.json` cubren artefactos locales y una instalación reproducible.

### Objetivo

Disponer de una base de Next.js reproducible, modular y comprobable, sin implementar todavía comportamiento de producto no planificado.

### Tareas principales

- Mantener `package.json`, TypeScript estricto, Next.js, PostCSS, ESLint y Vitest alineados con los proyectos frontend del reto.
- Configurar scripts de desarrollo, build, lint y pruebas.
- Crear el shell mínimo de App Router y los puntos de extensión en `src/app/`, `src/components/`, `src/features/catalog/`, `src/lib/`, `src/types/` y `tests/`.
- Añadir `.gitignore` y resolver dependencias en `package-lock.json`.
- Confirmar que cada carpeta tiene una responsabilidad única y documentada.

### Dependencias

- Fase 0 completada.
- Node.js y npm disponibles.

### Criterios de finalización

- `npm install` completa la instalación reproducible.
- `npm run lint`, `npm test` y `npm run build` pueden ejecutarse con la configuración base.
- No existe lógica de catálogo repartida fuera de sus límites de responsabilidad.

### Resultado esperado

Un proyecto de Next.js listo para recibir funcionalidades sin cambios estructurales de gran alcance.

---

## Fase 2 — Contrato y gestión de datos local

**Prioridad:** alta
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- `data/projects.json` contiene las 30 entregas registradas en el README raíz, con categorías normalizadas, tecnologías, resúmenes y enlaces GitHub comprobables hacia cada directorio del monorepo.
- `src/types/catalog.ts` concentra el contrato inmutable del catálogo, las categorías permitidas y el resultado discriminado de carga.
- `src/lib/catalog-schema.ts` valida el contrato con Zod antes de exponer datos a cualquier consumidor: versión, campos obligatorios, rangos de día, categoría, metadatos locales, tecnologías y enlaces GitHub restringidos; también rechaza días, identificadores, tecnologías y destinos duplicados o inconsistentes.
- `src/lib/catalog-source.ts` encapsula el fixture local y devuelve un resultado explícito `ok`/error para datos inválidos o fallos de lectura, sin permitir carga parcial.
- `tests/catalog-schema.test.ts` cubre normalización válida, identificadores duplicados, incoherencia entre día e identificador, enlaces externos no permitidos, tecnologías duplicadas, carga del fallback local y fixture vacío inválido.
- La configuración de Vitest resuelve el alias `@/` para ejecutar las mismas importaciones que el código de la aplicación. No se añadieron dependencias ni se conectó todavía la fuente a la interfaz; esa integración corresponde a la Fase 4.

### Objetivo

Definir una fuente local de proyectos segura, validada y estable para alimentar el MVP y las pruebas.

### Tareas principales

- Completar `data/projects.json` con entradas representativas de la mini-serie y enlaces relativos verificables.
- Definir los tipos de dominio en `src/types/`.
- Crear el esquema Zod y el cargador/adaptador de datos en `src/lib/`.
- Validar campos obligatorios, identificadores únicos, días permitidos, arrays de tecnologías, categorías y enlaces seguros.
- Resolver estados de fixture vacío, datos inválidos y error de lectura mediante un resultado explícito para la interfaz.
- Preparar pruebas de contrato, normalización y fallback local.

### Dependencias

- Fase 1 completada.
- Fixture inicial disponible en `data/projects.json`.

### Criterios de finalización

- Datos válidos se transforman a un modelo de dominio tipado.
- Datos incompletos o inconsistentes no llegan a los componentes de presentación.
- Las pruebas cubren contratos válidos, inválidos y duplicados.
- La aplicación puede operar sin red, credenciales o proveedor externo.

### Resultado esperado

Una capa de datos local y validada, desacoplada de la interfaz y extensible a integraciones futuras.

---

## Fase 3 — Diseño de interfaz y sistema visual

**Prioridad:** alta
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- `src/app/globals.css` define tokens de color, tipografía, espaciado, superficies, bordes, foco, responsive y reducción de movimiento; la composición evita desbordamiento horizontal desde 320 px y evoluciona a dos y tres columnas.
- `src/components/catalog-shell.tsx` aporta cabecera, pie, marca y enlace para saltar al contenido principal. `src/components/catalog-state.tsx` unifica las variantes de carga, colección vacía y error con regiones etiquetadas.
- `src/features/catalog/` contiene los componentes de presentación del dominio: tarjeta, rejilla de muestra y skeleton. Las tarjetas reutilizan el contrato validado sin introducir navegación, búsqueda, filtrado ni enlaces de proyecto funcionales, que siguen siendo responsabilidad de la Fase 4.
- `src/app/page.tsx` compone una jerarquía estática de portada, resumen, muestra de tarjetas y estados de sistema. Solo usa tres proyectos para validar el contenido visual representativo; no implementa exploración de la colección.
- `tests/catalog-presentation.test.tsx` cubre landmarks, enlace de salto, encabezados, muestra de tarjetas, ausencia intencionada de enlaces de Fase 4 y las tres variantes de estado. Vitest se configura con JSX automático para que las pruebas JSX reproduzcan el runtime de React.

### Objetivo

Definir una experiencia visual consistente, responsive y accesible antes de construir todas las interacciones.

### Tareas principales

- Diseñar jerarquía de portada, cabecera, resumen de colección, controles de exploración, rejilla de tarjetas y pie.
- Establecer tokens de color, tipografía, espaciado, bordes, elevación y estados de interacción en los estilos globales.
- Crear componentes reutilizables y agnósticos del dominio en `src/components/`.
- Crear componentes de presentación específicos del catálogo en `src/features/catalog/`.
- Diseñar las variantes de móvil, tableta y escritorio sin depender de hover.
- Preparar skeleton, estados vacío y error como parte del sistema visual.

### Dependencias

- Fase 1 completada.
- Contrato de proyecto definido en Fase 2 para representar contenido realista.

### Criterios de finalización

- La jerarquía y los componentes cubren las pantallas del MVP.
- La interfaz no genera desplazamiento horizontal en viewport pequeño.
- Todos los controles tienen estados de foco, hover y deshabilitado cuando correspondan.
- La revisión manual confirma contraste, semántica y navegación por teclado en la estructura estática.

### Resultado esperado

Un lenguaje visual mantenible que permite implementar el MVP sin duplicar patrones ni estilos.

---

## Fase 4 — Funcionalidades principales del catálogo (MVP)

**Prioridad:** crítica
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- `src/app/page.tsx` conecta la página con el cargador local validado y entrega las 30 entradas al navegador del catálogo; el error de fuente conserva el estado visual de la Fase 3.
- `src/features/catalog/catalog-browser.tsx` implementa búsqueda textual, filtros combinables de categoría y tecnología, contador anunciado mediante `aria-live`, restablecimiento y estado explícito de cero resultados. Los controles son elementos nativos etiquetados y navegables con teclado.
- `src/features/catalog/catalog-utils.ts` mantiene búsqueda, filtros, orden de opciones y detección de filtros activos como funciones puras, sin mezclar cálculos de dominio con el componente cliente.
- Las tarjetas de `src/features/catalog/catalog-card.tsx` muestran los recursos validados por el contrato local con enlaces relativos; no se aceptan ni se generan destinos externos en el flujo del MVP.
- `tests/catalog-utils.test.ts` cubre búsqueda, combinación de criterios, ausencia de coincidencias y opciones derivadas. `tests/catalog-browser.test.tsx` cubre búsqueda, filtros, contador, estado vacío, restablecimiento y enlaces. Las expectativas de presentación existentes se actualizaron de la muestra estática a la colección completa.

### Objetivo

Convertir la base en un catálogo navegable que permita descubrir y abrir proyectos desde una colección local.

### Tareas principales

- Conectar la página principal con el cargador local validado.
- Renderizar resumen de colección y tarjetas de proyecto.
- Añadir búsqueda textual y filtros explícitos por categoría y tecnología.
- Mostrar contador de resultados y acción de restablecimiento.
- Implementar enlaces seguros hacia código, demo o documentación disponibles.
- Construir estados de carga, vacío, sin coincidencias y error.
- Mantener los cálculos de filtrado y ordenación como funciones puras testeables.

### Dependencias

- Fase 2 completada para cargar datos validados.
- Fase 3 completada para reutilizar los patrones de interfaz.

### Criterios de finalización

- Una persona puede encontrar un proyecto por texto, categoría o tecnología.
- Los filtros se combinan y se pueden borrar de forma predecible.
- Las tarjetas muestran información suficiente y los enlaces llevan al recurso correcto.
- No hay dependencia de red para completar el flujo de demo.
- Se prueban búsqueda, filtros, resultados y estados de error principales.

### Resultado esperado

Un MVP local funcional, navegable, responsive y preparado para demostración.

---

## Fase 5 — Validación y manejo de errores

**Prioridad:** alta
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- `src/lib/catalog-schema.ts` restringe los destinos **Código** al directorio del proyecto correspondiente dentro de `https://github.com/DiegoGuti2115/30-dias-codigo/tree/main/projects/`, rechazando hosts, repositorios, ramas y rutas no autorizadas.
- `src/lib/catalog-source.ts` separa la lectura de la normalización mediante `loadCatalogFromLoader`; los datos inválidos devuelven `invalid-data` y los fallos de lectura devuelven `read-error`, sin propagar contenido parcial a la interfaz.
- `src/components/catalog-state.tsx` acepta una acción de recuperación opcional. La página usa un enlace interno de reintento ante errores de fuente y `src/app/error.tsx` actúa como límite de error de App Router con botón de reintento, mensaje no técnico y registro del fallo solo en consola.
- Los estados de error conservan regiones y encabezados etiquetados; los controles nativos de filtrado mantienen foco cuando se usan con teclado.
- `tests/catalog-schema.test.ts` cubre destinos GitHub no autorizados y cargadores que fallan. `tests/catalog-error-handling.test.tsx` cubre recuperación de la fuente y límite de error. `tests/catalog-browser.test.tsx` comprueba que los selectores conservan el foco durante interacción por teclado.

### Objetivo

Hacer explícitos los límites de confianza de los datos y proporcionar recuperación clara ante errores previsibles.

### Tareas principales

- Reforzar el esquema de datos y los mensajes de validación para entradas corruptas o incompletas.
- Aislar errores del origen de datos en límites apropiados de la aplicación.
- Ofrecer mensajes comprensibles, una acción de reintento o vuelta al catálogo y conservar el fallback local.
- Validar parámetros de URL si se incorpora filtrado o detalle mediante rutas.
- Evitar renderizado de contenido no confiable y revisar atributos de enlaces externos.

### Dependencias

- Fase 2 completada.
- Fase 4 implementada para validar flujos reales de usuario.

### Criterios de finalización

- La aplicación no muestra información parcialmente inválida como correcta.
- Los errores se comunican sin detalles internos ni bloqueos irreversibles.
- Los escenarios inválidos cuentan con pruebas automatizadas.
- El fixture local permite recuperar la demostración si falla una futura fuente remota.

### Resultado esperado

Un catálogo robusto ante datos defectuosos, estados vacíos y fallos recuperables.

---

## Fase 6 — Accesibilidad e inclusión

**Prioridad:** alta
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- `src/features/catalog/catalog-browser.tsx` relaciona cada control de exploración con instrucciones persistentes y el contador de resultados mediante `aria-describedby`. El contador usa una región `status` atómica y la colección de resultados está identificada como región; el estado sin coincidencias anuncia su aparición de forma no intrusiva.
- Los controles nativos mantienen un orden de foco lógico y siguen funcionando solo con teclado. La acción ahora se denomina «Restablecer criterios», comunica mejor su alcance y se deshabilita cuando no hay nada que borrar.
- `src/app/globals.css` conserva foco visible y reducción de movimiento, y amplía el objetivo de interacción de los enlaces de recursos a una altura mínima de 44 px. El texto de ayuda y los estados no dependen únicamente del color o del hover.
- `docs/accessibility-test-matrix.md` documenta una matriz manual reproducible para teclado, lector de pantalla, móvil, zoom, contraste, reducción de movimiento, recuperación y enlaces GitHub.
- `tests/catalog-browser.test.tsx` cubre la relación entre controles, ayuda y contador; estado habilitado de restablecimiento; anuncio y recuperación de cero resultados; y el flujo de foco con teclado. La suite completa sigue cubriendo landmarks, estados y enlaces validados.

### Objetivo

Garantizar que la exploración del catálogo sea utilizable con teclado, lector de pantalla, distintos tamaños de pantalla y preferencias de movimiento.

### Tareas principales

- Revisar landmarks, encabezados, nombres accesibles y relaciones entre filtros, resultados y mensajes.
- Garantizar foco visible, orden lógico y operación por teclado de todos los controles.
- Asociar etiquetas, ayuda y errores a cada entrada de búsqueda o filtro.
- Verificar contraste, información no dependiente del color, objetivos táctiles y reducción de movimiento.
- Añadir anuncios apropiados para cambios de resultados y estados asíncronos.
- Documentar una matriz de pruebas manuales de accesibilidad en `docs/`.

### Dependencias

- Fases 3 y 4 completadas.
- Fase 5 para revisar estados de error finales.

### Criterios de finalización

- Todo el flujo del MVP se completa solo con teclado.
- La información principal se entiende sin color, hover ni puntero preciso.
- Las revisiones de lector de pantalla y viewport móvil no detectan barreras críticas conocidas.
- Las regresiones accesibles prioritarias tienen cobertura automatizada cuando sea viable.

### Resultado esperado

Una experiencia inclusiva y robusta en los escenarios de navegación más relevantes.

---

## Fase 7 — Calidad y pruebas

**Prioridad:** alta
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- `vitest.config.ts` registra `tests/setup.ts` como configuración compartida. El setup limpia el DOM y restaura mocks tras cada caso, evitando acumulación de renders o estado de spies entre pruebas de componentes.
- `tests/catalog-schema.test.ts` amplía las regresiones del límite de confianza: rutas de repositorio incongruentes, campos no permitidos y preservación determinista de la serie local completa en orden de días.
- `tests/catalog-utils.test.ts` verifica que la búsqueda normaliza espacios sin mutar la colección y que las opciones de filtros se mantienen únicas y ordenadas de forma determinista.
- `docs/quality-verification.md` registra los comandos de validación, la cobertura actual, la revisión manual de accesibilidad y las limitaciones priorizadas. La suite no depende de red, secretos ni servicios externos.
- Las pruebas existentes de presentación, navegación por teclado, estados vacío/error/sin resultados, recuperación y límite de error continúan como cobertura de los flujos críticos del MVP.

### Objetivo

Consolidar una red de seguridad automatizada y verificaciones manuales reproducibles antes de optimizar o publicar.

### Tareas principales

- Completar pruebas de tipos, esquema, carga, filtros, ordenación, componentes y flujos del MVP.
- Añadir pruebas de regresión para los estados vacío, error y sin resultados.
- Configurar utilidades de test compartidas solo si evitan duplicación real.
- Revisar lint, compilación de producción y errores de hidratación.
- Ejecutar pruebas responsive y de accesibilidad documentadas.
- Registrar los comandos de verificación y cualquier limitación conocida en `docs/`.

### Dependencias

- Fases 2 a 6 completadas.

### Criterios de finalización

- `npm run lint`, `npm test` y `npm run build` terminan sin errores.
- Las funciones de dominio y los flujos críticos tienen cobertura significativa.
- Las pruebas son deterministas y no dependen de red ni secretos.
- Las limitaciones restantes están documentadas y priorizadas.

### Resultado esperado

Una versión verificable que permite refactorizar y evolucionar el catálogo con confianza.

---

## Fase 8 — Optimización y pulido

**Prioridad:** media
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- La build de producción se midió antes y después de los cambios: la ruta estática `/` pasa de 4.85 kB a 4.9 kB y mantiene 107 kB de First Load JS compartido. No se añadieron dependencias, red, imágenes remotas ni renderizados de servidor adicionales.
- `src/features/catalog/catalog-browser.tsx` usa `useDeferredValue` para diferir el cálculo de resultados durante una entrada rápida y comunica el estado transitorio con un contador y una región de resultados `aria-busy`, sin cambiar los filtros, el contrato ni la navegación existente.
- `src/app/loading.tsx` implementa el límite de carga de App Router con tres tarjetas skeleton, estado `aria-busy`, encabezado y mensaje anunciado. `src/app/globals.css` usa `content-visibility` en tarjetas y limita el hover a dispositivos que lo soportan; la preferencia de reducción de movimiento sigue teniendo prioridad.
- `src/app/layout.tsx` actualiza los metadatos para describir el catálogo entregado y declarar la aplicación indexable.
- `tests/catalog-loading.test.tsx` cubre el estado de carga accesible y `tests/catalog-browser.test.tsx` comprueba el estado estable de la región diferida. `docs/performance-and-polish.md` registra medición, decisiones y revisión manual para dispositivos limitados.

### Objetivo

Mejorar rendimiento, claridad y percepción de calidad sin sacrificar simplicidad ni accesibilidad.

### Tareas principales

- Medir tamaño de bundle y evitar dependencias o renderizados innecesarios.
- Optimizar imágenes y metadatos de contenido cuando existan recursos de demo.
- Revisar estrategia de renderizado y carga diferida de elementos no críticos.
- Mejorar mensajes, microinteracciones accesibles y estados de transición.
- Comprobar la experiencia en conexiones y dispositivos limitados.

### Dependencias

- Fase 7 completada para preservar una línea base verificable.

### Criterios de finalización

- No se introducen regresiones de accesibilidad ni de funcionalidad.
- Las mejoras se justifican con una medición o un problema de experiencia identificado.
- La navegación principal se mantiene ágil en móvil y escritorio.

### Resultado esperado

Un catálogo pulido, eficiente y agradable de usar en condiciones realistas.

---

## Fase 9 — Documentación y demostración

**Prioridad:** media
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- `README.md` se actualiza para describir el MVP realmente entregado: 30 proyectos, búsqueda y filtros, estados recuperables, contrato validado, fallback local, accesibilidad, rendimiento, estructura, comandos y exclusiones vigentes.
- `docs/demo-script.md` documenta un recorrido reproducible de 12 a 15 segundos para carga, búsqueda, filtros, restablecimiento y apertura de un recurso local, además de una variante de recuperación sin tocar el fixture.
- `docs/publication-draft.md` contiene texto breve, puntos comunicables, checklist de capturas, checklist previa y límites reales de publicación. No se añaden imágenes ni GIF provisionales: `assets/` permanece reservado hasta disponer de recursos finales optimizados.
- La documentación enlaza las matrices de calidad, accesibilidad y rendimiento ya verificadas. No se declara URL pública ni proveedor de hosting; esas decisiones quedan explícitamente para la Fase 10.
- `tests/catalog-presentation.test.tsx` protege los metadatos de producción que describen la colección entregada y su indexación normal.

### Objetivo

Dejar el proyecto comprensible, demostrable y mantenible por cualquier persona que llegue al repositorio.

### Tareas principales

- Actualizar `README.md` para reflejar funcionalidad realmente entregada, decisiones y comandos verificados.
- Crear en `docs/` un guion de demo reproducible y un borrador de publicación.
- Añadir en `assets/` capturas o GIF de la experiencia final, si son necesarios para la comunicación.
- Documentar arquitectura, modelo de datos, fallback y limitaciones conocidas cuando el detalle lo requiera.
- Verificar todos los enlaces internos y rutas mencionadas.

### Dependencias

- Fases 4 a 8 completadas.

### Criterios de finalización

- Una persona puede instalar, ejecutar, probar y entender el proyecto solo con la documentación.
- La demo cubre carga, exploración y apertura de un proyecto en menos de quince segundos.
- No hay instrucciones, estados ni referencias desactualizadas.

### Resultado esperado

Un cierre documental de calidad para el proyecto final de la mini-serie.

---

## Fase 10 — Despliegue y cierre de producción

**Prioridad:** media
**Estado:** completada y verificada el 30 de septiembre de 2026.

### Entregables y decisiones implementadas

- `next.config.ts` mantiene el trazado aislado del proyecto y añade cabeceras de protección aplicadas a todas las rutas: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy`; también desactiva `X-Powered-By` sin introducir dependencias ni configuración externa.
- `docs/deployment.md` documenta la estrategia reversible de hosting compatible con Next.js, los comandos, el directorio raíz según el contexto de despliegue, cabeceras, checklist, rollback y ausencia intencionada de variables de entorno.
- La versión de producción se compiló y se ejecuta localmente en `http://127.0.0.1:3000`. La ruta `/` respondió `200`, conserva el catálogo inicial de 30 proyectos y entrega las cabeceras configuradas sin revelar `X-Powered-By`.
- `README.md` y `docs/publication-draft.md` registran la URL local, el estado de cierre y el límite real: no se creó una URL pública porque el entorno no proporciona cuenta ni permisos de un proveedor. La configuración queda lista para un hosting posterior sin convertirlo en requisito del MVP.
- La revisión manual de teclado, responsive, accesibilidad y flujos recuperables permanece definida en la matriz de Fase 6; las pruebas automatizadas conservan cobertura de carga, estados de error, cero resultados, filtros y enlaces GitHub validados.

### Objetivo

Publicar una versión estable del catálogo con una estrategia operativa mínima y reversible.

### Tareas principales

- Elegir una plataforma compatible con Next.js sin convertirla en dependencia obligatoria de desarrollo.
- Configurar variables de entorno solo si una integración opcional las necesita, usando `.env.example` sin secretos.
- Ejecutar build de producción, revisión final de enlaces, responsive, accesibilidad y errores.
- Definir cabeceras o configuraciones de seguridad que correspondan al hosting elegido.
- Publicar la demo, registrar la URL resultante y actualizar la documentación.

### Dependencias

- Fases 7 y 9 completadas.
- Cuenta y permisos del proveedor de despliegue, si se decide publicar.

### Criterios de finalización

- La versión desplegada reproduce el flujo del MVP con la fuente local o fallback equivalente.
- No se exponen secretos ni se requiere una integración externa para que la demo funcione.
- La compilación y las pruebas de calidad han sido verificadas antes de publicar.
- La documentación incluye el estado de despliegue y cualquier paso de operación necesario.

### Resultado esperado

Una versión pública, estable y documentada del Catálogo de proyectos, lista para cerrar la mini-serie.