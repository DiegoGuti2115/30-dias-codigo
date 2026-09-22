# Guion de demo — Playground de cliente API

Demostración reproducible en 15 segundos. No requiere red externa, cuenta ni credenciales.

## Requisitos previos

```bash
git clone <repo-url> day-22-api-client-playground
cd day-22-api-client-playground
npm install
npm run dev
```

Abrir `http://localhost:3000` en el navegador.

## Flujo principal (15 s)

| # | Acción | Resultado esperado |
|---|--------|--------------------|
| 1 | Seleccionar **GET /api/mock/profile** en "Cargar ejemplo" | URL y método se precargan |
| 2 | Pulsar **Enviar solicitud** | Panel de respuesta muestra `200 OK`, duración y JSON formateado |
| 3 | Seleccionar **POST /api/mock/echo** en "Cargar ejemplo" | Método cambia a POST y aparece cuerpo JSON |
| 4 | Pulsar **Enviar solicitud** | Respuesta eco con el cuerpo enviado |
| 5 | Comprobar **Solicitudes recientes** | Las dos peticiones aparecen en el historial local |
| 6 | Pulsar una entrada del historial | El editor restaura método, URL y parámetros |

## Flujo de error (5 s adicionales)

| # | Acción | Resultado esperado |
|---|--------|--------------------|
| 7 | Seleccionar **GET /api/mock/error** | Respuesta `503 Service Unavailable` en rojo |
| 8 | Escribir una URL inválida (`ftp://…`) y pulsar Enviar | Error de validación inline antes de enviar |

## Puntos de conversación

- **Sin credenciales:** la demo funciona íntegramente con rutas mock de Next.js.
- **Seguridad:** `authorization`, `cookie` y `x-api-key` se eliminan del historial antes de persistir.
- **Sin renderizado activo:** el cuerpo HTML recibido se muestra como texto plano.
- **Cancelación:** pulsar Enviar y luego Cancelar antes de que responda muestra el estado "cancelada".

## Fallback

Si la red o CORS bloquean una URL externa, volver a los mocks: toda la funcionalidad queda demostrada sin salir de `localhost`.