# Día 22 — Playground de cliente API

Aplicación web del Día 22 del reto [30 Días, 30 Proyectos](../../README.md). Permite construir solicitudes HTTP, enviarlas desde una interfaz guiada y revisar su respuesta sin instalar una herramienta de escritorio.

**Estado:** Fase 4 completada — base, contrato, ejecutor HTTP, editor accesible, inspector de respuesta e historial local seguro disponibles.

## Problema

Probar una API durante el desarrollo suele requerir alternar entre documentación, terminal y herramientas externas. Para peticiones sencillas, esa fricción ralentiza la exploración del contrato y dificulta compartir un caso reproducible.

## Objetivo del MVP

Permitir configurar y ejecutar una petición `GET`, `POST`, `PUT`, `PATCH` o `DELETE`, inspeccionar de forma clara su respuesta y volver a lanzar solicitudes recientes, todo desde el navegador.

## Alcance

- Editor de método, URL, parámetros de consulta, cabeceras y cuerpo JSON.
- Validación local de URL, filas de cabeceras/parámetros y JSON antes del envío.
- Panel de respuesta con estado HTTP, duración, cabeceras y cuerpo formateado.
- Historial local y limitado de solicitudes recientes, sin secretos.
- Solicitudes de ejemplo reproducibles mediante rutas mock internas.
- Estados de carga, error de red, error HTTP y respuesta vacía.
- Interfaz responsive, navegable con teclado y sin información crítica dependiente del color.

## Fuera de alcance

- Autenticación persistente, gestión de usuarios o sincronización en la nube.
- Almacenamiento de tokens, contraseñas o cabeceras `Authorization` en el historial.
- Colecciones compartidas, generación de SDK o importación de Postman.
- WebSockets, GraphQL, subida de archivos, proxy de servidor o automatización de pruebas.
- Sustituir una herramienta profesional de pruebas de API.

## Tecnologías previstas

- Next.js con App Router, React y TypeScript estricto.
- Tailwind CSS para layout y estados responsive.
- SWR para el estado de datos de las rutas de ejemplo y revalidación manual.
- Zod para validar el borrador de solicitud, la configuración y fixtures.
- `fetch` nativo para ejecutar solicitudes.
- Vitest y Testing Library para modelo, validación y flujos principales.

## Requisitos y comandos previstos

- Node.js 20 o superior y npm.

```bash
npm install
npm run dev
npm test
npm run lint
npm run build
npm run start
```

No habrá credenciales obligatorias. La demo usará rutas mock de Next.js; una URL pública solo será una opción adicional. Las restricciones CORS del navegador se comunicarán claramente cuando afecten a una URL externa.

## Experiencia principal

1. La persona abre el playground con una petición de ejemplo precargada.
2. Selecciona método, URL y edita parámetros, cabeceras o cuerpo JSON.
3. La app valida los datos y ejecuta la petición al pulsar **Enviar**.
4. La respuesta presenta código, tiempo, cabeceras y cuerpo legible.
5. La solicitud se guarda en un historial local sanitizado y puede restaurarse.
6. Si la red o CORS impiden ejecutar una URL externa, puede completar la demostración con las rutas mock.

## Reglas de seguridad y datos

- El cliente no enviará credenciales del navegador: las peticiones usarán `credentials: "omit"`.
- El historial eliminará cabeceras sensibles (`authorization`, `cookie`, `x-api-key`) y nunca guardará secretos.
- Los cuerpos se tratarán como texto; no se renderizará HTML recibido.
- Se limitarán el tamaño del cuerpo y el número de entradas del historial para evitar bloquear la interfaz.
- Una respuesta HTTP no exitosa se mostrará como resultado de la petición, no como un fallo silencioso.

## Datos, integración y fallback

- **Ruta principal de la demo:** handlers mock en `src/app/api/mock/` con respuestas deterministas.
- **Integración opcional:** cualquier endpoint CORS-compatible proporcionado por la persona usuaria.
- **Fallback:** las rutas mock aseguran que el flujo completo se pueda demostrar sin red, cuenta ni credenciales.
- Si una integración externa no se valida antes de T+30, se mantiene el modo mock como fuente de demo.

## Estructura prevista

```text
day-22-api-client-playground/
├── README.md
├── ROADMAP.md
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
├── src/
│   ├── app/                 # Rutas, layout, página, estilos y mocks de Next.js
│   │   └── api/mock/        # Route handlers para una demo reproducible
│   ├── components/          # Editor de solicitud, respuesta, historial y estados
│   ├── hooks/               # Borrador, envío y persistencia local
│   └── lib/                 # Tipos, Zod, sanitización, fetch y formateadores
├── tests/                   # Pruebas unitarias y de interacción
├── data/                    # Peticiones de ejemplo y fixtures de respuesta
├── assets/                  # Capturas, GIF y recursos de demo
└── docs/                    # Guion de demo, post y revisión de seguridad
```

## Validación

- Rechazar URL, cabeceras, parámetros o JSON inválidos antes de enviar.
- Confirmar la construcción correcta de URL, query string y opciones de `fetch`.
- Comprobar estados de éxito, 4xx/5xx, red, timeout y respuesta sin cuerpo.
- Comprobar que el historial no persiste cabeceras sensibles ni excede su límite.
- Revisar foco, teclado, contraste y responsive en escritorio y móvil.
- Ejecutar `npm test`, `npm run lint` y `npm run build` antes de cerrar el proyecto.

Consulta [ROADMAP.md](ROADMAP.md) para el desarrollo por fases.

## Estado del proyecto

**Fase 6 completada — proyecto cerrado.**

Todas las fases del [ROADMAP](ROADMAP.md) están completadas:

| Fase | Descripción | Estado |
|------|-------------|--------|
| 0 | Alcance y estructura | ✅ |
| 1 | Base de proyecto y contrato | ✅ |
| 2 | Ejecutor y respuesta | ✅ |
| 3 | Editor de solicitud | ✅ |
| 4 | Inspector de respuesta e historial | ✅ |
| 5 | SWR, calidad y responsive | ✅ |
| 6 | Demo y publicación | ✅ |

## Demo

Flujo completo documentado en [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md).

```bash
npm install && npm run dev
# Abrir http://localhost:3000
```

## Seguridad

Revisión completa en [`docs/SECURITY_REVIEW.md`](docs/SECURITY_REVIEW.md). Resumen:

- Sin credenciales enviadas (`credentials: 'omit'`).
- Sin secretos en `localStorage` (sanitización automática).
- Sin renderizado de HTML externo.
- Sin servicios externos obligatorios para la demo.