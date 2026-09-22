# Hoja de Ruta: Playground de cliente API (Día 22)

El plan prioriza un MVP demostrable en tres horas. Las fases se completan en orden: primero un flujo local fiable, después la interfaz y por último la calidad y publicación.

## Fase 0: Alcance y estructura

- [x] Redactar `README.md` con alcance, seguridad, integración y fallback.
- [x] Redactar este `ROADMAP.md`.
- [x] Definir `src/app`, `src/components`, `src/hooks`, `src/lib`, `tests`, `data`, `assets` y `docs`.
- [x] Fijar un MVP basado en mocks internos sin credenciales.

**Criterio de salida:** el problema, las restricciones de seguridad, el MVP y la estructura están definidos sin implementación funcional.

## Fase 1: Base de proyecto y contrato — 25 min

- [x] Inicializar Next.js, TypeScript estricto, Tailwind, ESLint, Vitest y Testing Library.
- [x] Definir tipos y esquemas Zod para solicitud, pares clave-valor, respuesta e historial.
- [x] Crear solicitudes de ejemplo y un límite de tamaño para cuerpo e historial.
- [x] Añadir rutas mock `GET`, `POST` y error deliberado.
- [x] Cubrir la validación de URL, JSON, cabeceras y sanitización.

**Criterio de salida:** el modelo valida y serializa una solicitud sin React ni red.
**Estado:** Fase completada. `src/lib/schema.ts` valida método, URL HTTP(S), pares activos, cabeceras sin duplicados, JSON y límites. `src/lib/request.ts` serializa solicitudes y elimina cabeceras sensibles del historial. El fixture incluye `GET` y `POST`; las rutas mock ofrecen perfil, eco y un error 503. `npm test` pasa 6 pruebas; `npm run lint` y `npm run build` pasan.

## Fase 2: Ejecutor y respuesta — 35 min

- [x] Construir la URL final a partir de parámetros y cabeceras.
- [x] Implementar el adaptador `fetch` con tiempo de inicio/fin y cancelación.
- [x] Interpretar cuerpos JSON, texto, vacíos y no legibles de forma segura.
- [x] Diferenciar respuesta HTTP, error de red, timeout y cancelación.
- [x] Probar opciones de `fetch`, formateo de respuesta y errores.

**Criterio de salida:** una petición mock devuelve un modelo de respuesta completo y consistente.

**Estado:** Fase completada. `src/lib/client.ts` construye URL y `RequestInit` con `credentials: 'omit'`, aplica timeout/cancelación y devuelve un resultado discriminado. Las respuestas 4xx/5xx permanecen inspeccionables; red, timeout y cancelación son estados separados. Se formatean JSON, texto, cuerpos vacíos y no legibles. `npm test` pasa 10 pruebas; lint y comprobación de tipos pasan.

## Fase 3: Editor de solicitud — 40 min

- [x] Crear selector de método y campo URL.
- [x] Crear editores dinámicos de parámetros y cabeceras.
- [x] Crear editor de cuerpo JSON con errores en línea.
- [x] Añadir ejemplos recuperables y botón Enviar accesible.
- [x] Implementar estados de validación, envío y cancelación.

**Criterio de salida:** se puede componer y ejecutar una petición mock solo con teclado.

**Estado:** Fase completada. `useRequestComposer` encapsula borrador, errores, ejecución y cancelación; `RequestEditor` presenta controles semánticos, mensajes asociados por `aria-describedby` y estado anunciado con `aria-live`. Incluye ejemplos GET/POST, editores dinámicos y protección de GET sin cuerpo. `npm test` pasa 12 pruebas; lint y TypeScript estricto pasan.

## Fase 4: Inspector de respuesta e historial — 35 min

- [x] Mostrar estado, duración, cabeceras y cuerpo de la respuesta.
- [x] Formatear JSON sin interpretar HTML recibido.
- [x] Guardar solicitudes recientes sanitizadas en `localStorage`.
- [x] Permitir restaurar y eliminar una entrada del historial.
- [x] Mostrar vacío, carga, error y respuesta HTTP fallida de manera distinguible.

**Criterio de salida:** una persona entiende el resultado y puede repetir una solicitud sin exponer secretos.

**Estado:** Fase completada. `ResponseInspector` muestra respuestas HTTP como texto seguro, con estado, duración, tipo, cabeceras y cuerpo. `RequestHistory` permite restaurar, eliminar y vaciar entradas. `src/lib/history.ts` valida `localStorage`, limita las entradas y tolera JSON corrupto. Antes de persistir se eliminan cabeceras sensibles y el cuerpo completo de cada solicitud. `npm test` pasa 14 pruebas; lint, TypeScript y build pasan.

## Fase 5: SWR, calidad y responsive — 25 min

- [x] Usar SWR para cargar y revalidar ejemplos/mock metadata sin acoplar la UI al endpoint.
- [x] Añadir botón de reintento y revalidación manual donde sea útil.
- [x] Probar flujo de envío, validación, historial y error.
- [x] Revisar foco, semántica, contraste, desktop y móvil.
- [x] Ejecutar `npm test`, `npm run lint` y `npm run build`.

**Criterio de salida:** el MVP funciona de forma reproducible sin red externa ni credenciales.

## Fase 6: Demo y publicación — 20 min

- [x] Redactar `docs/DEMO_SCRIPT.md` para una demostración de 15 segundos.
- [x] Capturar una imagen o GIF del flujo completo.
- [x] Redactar `docs/LINKEDIN_POST.md` con problema, decisión de seguridad y fallback.
- [x] Actualizar README y el registro raíz con enlaces de demo/publicación.

**Criterio de salida:** el proyecto se instala, valida y demuestra mediante documentación reproducible.

## Criterios de terminado

- Se construyen y validan solicitudes `GET`, `POST`, `PUT`, `PATCH` y `DELETE`.
- El resultado muestra estado, tiempo, cabeceras y cuerpo sin renderizar contenido activo.
- Los mocks permiten completar la demo sin servicios externos.
- El historial es local, limitado y no conserva secretos.
- Los estados de validación, carga, respuesta HTTP y error de red son claros.
- La interfaz es utilizable con teclado y en móvil.
- `npm test`, `npm run lint` y `npm run build` pasan.

## Mejoras futuras

- Variables de entorno locales cifradas por el navegador o solo en memoria.
- Colecciones exportables e importables.
- Autenticación temporal por encabezado, sin persistencia.
- Soporte de GraphQL, carga de archivos y WebSockets.
- Proxy de desarrollo opt-in con una revisión de seguridad específica.
