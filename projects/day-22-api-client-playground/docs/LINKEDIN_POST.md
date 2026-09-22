# Post de LinkedIn — Día 22

---

**Día 22/30: construí un cliente HTTP en el navegador — y la parte más difícil no fue el fetch.**

Hoy el reto era claro: un playground para probar APIs directamente desde el navegador, sin instalar Postman ni alternar entre terminal y documentación.

En tres horas tenía editor de método, URL, parámetros, cabeceras y cuerpo JSON, inspector de respuesta con estado, duración y cabeceras, historial local de peticiones recientes, mocks internos para demo sin red y validación en cliente antes de enviar.

**Pero el problema interesante no fue técnico — fue de seguridad.**

Un cliente HTTP en el navegador tiene acceso a las mismas credenciales que el usuario introduce. Decidí tres reglas desde el principio:

1. `credentials: 'omit'` en cada fetch — nunca se envían cookies del navegador.
2. El historial elimina `authorization`, `cookie` y `x-api-key` antes de escribir en `localStorage`.
3. El cuerpo de la respuesta se trata siempre como texto: no se renderiza HTML recibido.

¿El resultado? Una herramienta que puedo compartir con alguien y que no va a filtrar secretos aunque la usen en una red compartida.

**Lo que aprendí hoy:** definir las restricciones de seguridad antes de la primera línea de código es lo que hace que el diseño sea coherente. No fueron parches al final — fueron el andamiaje desde el día cero.

El historial local con sanitización automática es el detalle que más me gusta. Nadie debería tener que recordar "oye, no guardes ese token".

Proyecto, código y demo en los comentarios 👇

#30días30proyectos #TypeScript #NextJS #WebDev #OpenSource #RooCode