# Publicación de LinkedIn — Día 06

## Texto propuesto

**Día 06 de 30 Días, 30 Proyectos: Validador de políticas de contraseña.**

Construí una herramienta CLI local en Python 3.11+ para comprobar una política de contraseña explícita sin convertir la entrada en un dato persistente.

El foco no está en “puntuar” una contraseña, sino en hacer visible y verificable una política v1 concreta:

- longitud entre 12 y 128 caracteres Unicode;
- presencia de mayúscula, minúscula, dígito decimal y carácter especial;
- ausencia de espacios Unicode;
- diagnóstico determinista de los requisitos incumplidos.

La parte más importante del proyecto fue el límite de privacidad:

- la CLI solicita la entrada sin eco con la biblioteca estándar;
- no acepta la contraseña mediante argumentos, archivos, `stdin` o variables de entorno;
- no usa red, APIs, telemetría, logs ni persistencia;
- los resultados no incluyen la entrada, su longitud, fragmentos ni derivados;
- los escenarios y referencias de prueba son sintéticos.

La arquitectura separa la política, el validador puro, la presentación y la CLI. Esto permite probar reglas, Unicode, espacios, límites, errores de interacción, códigos de salida y no revelación de forma aislada.

También añadí una landing local, interactiva y accesible para explicar la política y explorarla con datos sintéticos. La demo se ejecuta por completo en el navegador, no realiza llamadas de red y deja claro que no debe usarse una credencial real.

La suite actual cubre núcleo, CLI, regresión y salvaguardas estáticas de la web. Se ejecuta localmente sin dependencias externas.

Repositorio y demostración local:
- lee [`README.md`](../README.md) y el [`CONTRATO.md`](CONTRATO.md);
- inicia la web con `python -m http.server 8000 -d projects/day-06-password-policy-checker`;
- abre `http://localhost:8000/assets/demo-interactiva.html`.

#Python #Ciberseguridad #DesarrolloSeguro #CLI #Testing #Unicode #Privacidad #30Dias30Proyectos

## Notas de publicación

- Sustituye los enlaces relativos por la URL pública del repositorio antes de publicar.
- No incluyas capturas que muestren una credencial real o una entrada introducida durante la demostración.
- Describe la herramienta como comprobación de conformidad con una política, no como medidor de fortaleza ni garantía de seguridad.
