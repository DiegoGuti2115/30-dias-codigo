# Estrategia de publicación en LinkedIn — Día 06

## 1. Posicionamiento editorial

### Objetivo de la publicación

Convertir el proyecto en una historia de aprendizaje práctico sobre cómo diseñar una herramienta pequeña con límites explícitos: una política definida antes del código, una CLI local, una demostración educativa y decisiones de privacidad verificables.

El objetivo no es presentar el proyecto como un producto de autenticación ni como un medidor de fortaleza. La publicación debe generar conversación cualificada sobre diseño seguro, pruebas, Unicode, accesibilidad y aprendizaje mediante proyectos terminados.

### Audiencia principal

1. Desarrolladores y estudiantes de Python interesados en proyectos pequeños con una arquitectura clara.
2. Profesionales de ciberseguridad, AppSec y privacidad que valoran la minimización de datos y los límites de alcance.
3. Personas que aprenden programación construyendo proyectos públicos y reproducibles.

### Ángulo narrativo

**Una contraseña es un dato sensible incluso en una herramienta pequeña: por eso el primer entregable fue el contrato, no la interfaz.**

La tensión de la historia no es “he creado un validador de contraseñas”, sino: “¿cómo enseño reglas de validación sin normalizar la exposición de credenciales ni afirmar más seguridad de la que realmente ofrece una política simple?”.

### Formato recomendado y orden de publicación

Publicar un carrusel nativo en PDF de 9 diapositivas con un texto de acompañamiento breve. El carrusel facilita explicar una decisión técnica por pantalla y ofrece una experiencia legible en móvil. Evitar un vídeo de pantalla: el valor está en la claridad de las decisiones y los estados de la demo, no en velocidad de interacción.

Orden recomendado:

1. Publicación principal con carrusel y copy.
2. Comentario inicial del autor, publicado inmediatamente después, con enlaces al repositorio y a la guía local.
3. Respuestas durante las primeras 24–48 horas: priorizar preguntas sobre límites, Unicode, privacidad, pruebas y accesibilidad.
4. Entre 5 y 7 días después, una publicación corta de seguimiento sobre un aprendizaje concreto: por ejemplo, por qué “cumplir una política” no equivale a “ser una contraseña fuerte”.

## 2. Calendario realista

| Momento | Acción | Resultado esperado |
|---|---|---|
| Día -3 | Revisar capturas, eliminar cualquier dato personal, probar el carrusel en un móvil y preparar el PDF. | Material seguro y legible. |
| Día -2 | Compartir el borrador con una persona técnica y otra no técnica. | Detectar ambigüedades y promesas excesivas. |
| Día -1 | Revisar enlaces públicos, texto alternativo, contraste y el comentario inicial. | Publicación lista y accesible. |
| Día 0, 08:30–10:00 hora local | Publicar el carrusel y el copy. | Alcance inicial durante la franja laboral. |
| Día 0, primeros 30 minutos | Añadir el comentario con enlaces y responder las primeras interacciones. | Reducir fricción para quien quiera revisar el proyecto. |
| Día 1 | Responder preguntas con ejemplos conceptuales; no pedir ni aceptar contraseñas reales. | Conversación segura y útil. |
| Día 5–7 | Publicar seguimiento con una lección puntual y enlazar de nuevo al proyecto. | Reforzar aprendizaje y continuidad. |

La franja propuesta es una hipótesis práctica, no una garantía de alcance. Conviene ajustarla con datos propios de actividad de la audiencia.

## 3. Mensajes que deben sostener la historia

### Problema

Las políticas de contraseña suelen tratarse como una lista rápida de condiciones. Sin embargo, una herramienta didáctica que evalúa texto sensible debe decidir cómo recibe la entrada, qué no guarda, qué no imprime, qué casos Unicode admite y cómo prueba todo ello sin versionar credenciales.

### Solución

El proyecto fija una política v1 antes de implementarla: entre 12 y 128 caracteres Unicode, presencia de mayúscula, minúscula, dígito decimal y carácter especial, y ausencia de espacios Unicode. El validador devuelve un resultado global y diagnósticos deterministas, sin incluir la entrada ni su longitud exacta.

### Demostración interactiva

La landing en [`assets/demo-interactiva.html`](../assets/demo-interactiva.html) es un recurso educativo estático, local y sin dependencias externas. Reproduce en el navegador las reglas documentadas para mostrar estados sintéticos. No sustituye la CLI real, no hace llamadas de red, no utiliza almacenamiento del navegador y no debe recibir una contraseña real.

### Decisiones técnicas que merece la pena destacar

- Contrato v1 y escenarios sintéticos antes de la implementación.
- Separación entre política, validación pura, presentación y CLI.
- Entrada de la CLI sin eco mediante [`getpass`](../src/main.py:23).
- Reglas Unicode, incluyendo dígitos decimales, espacios y marcas combinantes.
- Salida determinista y pruebas de no revelación.
- Landing accesible con estructura semántica, foco visible, región [`aria-live`](../assets/demo-interactiva.html:125) y [`prefers-reduced-motion`](../assets/demo-interactiva.html:72).

### Aprendizaje que debe cerrar el relato

La lección no es “más reglas producen más seguridad”. Es que una funcionalidad pequeña mejora cuando el alcance, las amenazas razonables y el comportamiento verificable se definen antes de programar.

## 4. Carrusel: guion, capturas y estados

Todas las capturas deben salir de la landing local en [`assets/demo-interactiva.html`](../assets/demo-interactiva.html), no de una terminal con datos introducidos. Ocultar barra del navegador, escritorio, pestañas, extensiones, reloj, notificaciones y cualquier identificador personal.

| # | Parte de la interfaz y estado | Texto sobre la imagen | Objetivo | Elemento visual protagonista |
|---|---|---|---|---|
| 1 | Vista hero limpia; sin interacción de la demo. | **Validar no es autenticar. Y tampoco es exponer datos.** | Gancho: abrir una tensión de seguridad sin sensacionalismo. | Titular grande, gradiente y tarjeta del comando real. |
| 2 | Sección “Qué comprueba exactamente”, con las reglas visibles. | **Una política explícita antes que una lista ambigua.** | Presentar el problema: reglas sin contrato generan expectativas confusas. | Bloques de seis reglas, con “No estima fortaleza” resaltado. |
| 3 | Demo con campo vacío; panel de resultado oculto. | **La demo es local. Usa solo texto sintético.** | Separar la experiencia educativa del uso de credenciales reales. | Aviso azul “Entorno educativo local”. |
| 4 | Demo con el estado inválido sintético `demo2026`; panel de resultado visible. | **Un fallo debe explicar la regla, no revelar la entrada.** | Mostrar diagnósticos de longitud, mayúscula y carácter especial en orden estable. | Panel de resultados rojo y lista de diagnósticos. |
| 5 | Demo con el estado inválido sintético `Demo Local#2026Aa`; panel de resultado visible. | **Los espacios Unicode también forman parte del contrato.** | Mostrar que un candidato puede cumplir categorías y aun así fallar por espacio. | Diagnóstico “No se permiten espacios en blanco.” |
| 6 | Demo con un estado válido generado por el botón; ocultar el valor del campo usando el tipo password. | **Cumple la política v1. No significa “imposible de atacar”.** | Diferenciar conformidad y fortaleza. | Estado verde y cinco reglas aprobadas. |
| 7 | Sección “Un núcleo puro detrás de una frontera segura”. | **Política → validador → presentación → CLI** | Explicar arquitectura sin enseñar código pequeño o ilegible. | Las cuatro tarjetas del flujo y el comando `check`. |
| 8 | Secciones de privacidad y calidad; si no caben, componer una captura limpia de ambas. | **Sin red. Sin logs. Sin persistencia. Con pruebas.** | Mostrar decisiones de seguridad, accesibilidad y comprobación. | Lista de límites + tarjetas de calidad. |
| 9 | Pie de landing o hero reencuadrado, con un bloque de CTA añadido en diseño. | **¿Qué límite definirías antes de escribir la primera línea?** | Invitar a conversación técnica y dirigir al repositorio. | CTA claro, nombre del reto y URL corta pública si existe. |

No usar la palabra “contraseña” como contenido visible del campo en las diapositivas 4–6: el control debe conservar `type="password"` y mostrar puntos. El texto de cada diapositiva debe explicar el estado sin reproducir la cadena sintética sobre la imagen.

## 5. Datos sintéticos permitidos para las capturas

Los ejemplos son exclusivamente estados de demostración. No deben presentarse como contraseñas recomendadas ni reutilizarse fuera de la captura.

| Estado | Valor sintético solo para preparar la captura | Resultado esperado en la demo | Uso recomendado |
|---|---|---|---|
| Inválido: faltan varias categorías | `demo2026` | Fallan longitud, mayúscula y carácter especial. | Diapositiva 4. |
| Inválido: contiene espacio | `Demo Local#2026Aa` | Falla por espacio; las demás categorías se cumplen. | Diapositiva 5. |
| Válido: estado generado | Usar el botón “Generar ejemplo sintético”; no escribir ni mostrar el valor en la composición final. | Resultado global válido y reglas aprobadas. | Diapositiva 6. |

No publicar valores que parezcan credenciales personales, patrones de organizaciones, nombres, fechas reales, dominios, correos, tokens ni combinaciones que se describan como “seguras”. No animar a copiar ningún ejemplo.

## 6. Dirección de arte, exportación y accesibilidad

### Formato y composición

- Usar formato vertical 4:5, `1080 × 1350 px`; es el más favorable para lectura en móvil dentro del feed.
- Exportar el carrusel como un único PDF de alta calidad; conservar también los PNG individuales para archivo y reutilización.
- Mantener márgenes internos de al menos `72 px` en cada borde y no colocar texto crítico en la franja inferior.
- Usar una única familia sans serif coherente con la landing. Titular: 64–84 px; subtítulo: 34–42 px; cuerpo: mínimo 28–32 px en el lienzo final.
- Máximo 12–18 palabras de mensaje principal por diapositiva y, como máximo, dos líneas cortas de apoyo. La explicación extensa pertenece al copy, no a la imagen.
- Usar los colores de la landing: azul/cian para contexto, verde para regla cumplida y rojo suave para fallo. No depender solo del color: sumar iconos, etiquetas o texto.
- Mantener el mismo patrón: número de diapositiva discreto, titular arriba, captura o composición central y una firma breve “Día 06 · 30 Días, 30 Proyectos”.

### Nombres de archivo

Usar nombres ordenados y sin datos sensibles:

```text
linkedin-day06-01-portada-1080x1350.png
linkedin-day06-02-problema-1080x1350.png
linkedin-day06-03-demo-local-1080x1350.png
linkedin-day06-04-fallo-categorias-1080x1350.png
linkedin-day06-05-fallo-espacio-1080x1350.png
linkedin-day06-06-resultado-valido-1080x1350.png
linkedin-day06-07-arquitectura-1080x1350.png
linkedin-day06-08-privacidad-calidad-1080x1350.png
linkedin-day06-09-cta-1080x1350.png
linkedin-day06-carrusel.pdf
```

### Texto alternativo sugerido

Añadir texto alternativo manual a cada imagen al publicar, si la interfaz de LinkedIn lo permite. Debe describir la información, no el diseño decorativo:

1. “Portada del proyecto Día 06: Validador de políticas de contraseña v1. Mensaje: validar no es autenticar ni exponer datos.”
2. “Seis reglas de la política v1: longitud Unicode, mayúscula, minúscula, dígito decimal, carácter especial y ausencia de espacios.”
3. “Demo web local con aviso de usar solo texto sintético y de que no realiza llamadas de red ni guarda la entrada.”
4. “Demo con resultado no válido y diagnósticos de longitud, mayúscula y carácter especial, sin mostrar la entrada.”
5. “Demo con diagnóstico de espacio no permitido, sin mostrar el contenido introducido.”
6. “Demo con resultado válido según la política v1 y cinco reglas aprobadas; la imagen aclara que no equivale a una garantía de seguridad.”
7. “Diagrama visual de la arquitectura: política, validador, presentación y CLI.”
8. “Resumen de privacidad y calidad: sin red, logs ni persistencia; pruebas locales y características de accesibilidad.”
9. “Llamada a la acción: qué límite definir antes de escribir la primera línea de código.”

## 7. Copy recomendado para la publicación

**Validar una política no es autenticar. Y tampoco debería obligarnos a exponer una contraseña.**

En el Día 06 de mi reto “30 Días, 30 Proyectos” construí un validador local de políticas de contraseña con Python 3.11+.

La parte interesante no fue añadir una lista de condiciones. Fue definir primero el contrato: qué se valida, en qué orden se informa y qué datos no deben salir de la evaluación.

La política v1 comprueba:

- entre 12 y 128 caracteres Unicode;
- al menos una mayúscula, una minúscula, un dígito decimal y un carácter especial;
- ausencia de espacios Unicode.

El proyecto separa la política, el validador puro, la presentación y la CLI. La entrada se solicita sin eco y los resultados no incluyen el texto evaluado, fragmentos ni su longitud exacta. Tampoco hay red, telemetría, logs, persistencia ni dependencias externas.

Además añadí una landing local y accesible para explicar la política con datos sintéticos. La demo se ejecuta en el navegador solo con fines educativos: no es una interfaz de autenticación, no evalúa filtraciones, no estima entropía y no convierte una contraseña “válida” en una contraseña garantizada como segura.

Mi aprendizaje principal: en funcionalidades pequeñas, el valor está muchas veces en los límites que decides explícitamente antes de programar. Un contrato claro hace más sencillas las pruebas, las decisiones de privacidad y la comunicación honesta del alcance.

¿Qué requisito de seguridad o privacidad definirías antes de escribir la primera línea de una herramienta así?

#Python #Ciberseguridad #DesarrolloSeguro #Testing #Privacidad #Accesibilidad #Unicode #AprenderProgramando #30Dias30Proyectos

## 8. Comentario inicial recomendado

Dejo aquí los recursos para revisar el proyecto con calma:

- Repositorio: **[sustituir por URL pública del repositorio]**
- Contrato de la política v1: **[sustituir por URL pública a `docs/CONTRATO.md`]**
- Demo local: desde la raíz del repositorio, ejecutar `python -m http.server 8000 -d projects/day-06-password-policy-checker` y abrir `http://localhost:8000/assets/demo-interactiva.html`.

La demo usa únicamente estados sintéticos. Por favor, no introduzcas una contraseña real ni compartas credenciales en los comentarios.

## 9. Riesgos de comunicación y afirmaciones que se deben evitar

| Evitar | Motivo | Sustituir por |
|---|---|---|
| “Comprueba si tu contraseña es segura.” | Sobrepromete: la política no mide entropía, filtraciones ni resistencia a ataques. | “Comprueba conformidad con una política v1 explícita.” |
| “Protege tus contraseñas.” | Sugiere protección, almacenamiento o gestión que no existen. | “Minimiza la exposición durante una evaluación local.” |
| “Valida contraseñas reales en la demo.” | Invita a introducir un secreto en un recurso educativo. | “Usa solo texto sintético; la demo no debe recibir credenciales reales.” |
| “No guarda nada, por tanto es totalmente seguro.” | La ausencia de persistencia no elimina todos los riesgos del dispositivo, navegador o entorno. | “No implementa persistencia ni red; sigue siendo una demo educativa local.” |
| “Cumple estándares de seguridad.” | No se ha declarado ni evaluado una certificación o norma concreta. | “La política está documentada y probada dentro del alcance v1.” |
| “Genera contraseñas seguras.” | El proyecto no es un generador; el botón crea un estado sintético de demostración. | “Genera un ejemplo sintético para ilustrar un resultado.” |
| Mostrar un valor legible, incluso ficticio, como ejemplo de éxito. | Puede normalizar patrones copiables o confundirse con una recomendación. | Ocultar el campo y explicar el estado mediante diagnósticos y reglas. |

Antes de publicar, confirmar que las URLs son públicas, que el repositorio no contiene valores sensibles y que las capturas no muestran datos locales, pestañas, perfiles ni notificaciones.
