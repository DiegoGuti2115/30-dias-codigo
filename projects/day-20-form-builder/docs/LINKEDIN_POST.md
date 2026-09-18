# Borrador de publicación

## Constructor de formularios: diseñar, probar y exportar sin backend

En el Día 20 del reto construí un constructor de formularios local con React, TypeScript, Zod y Vite.

El problema era sencillo: para un formulario pequeño, editar HTML a mano mezcla estructura, reglas y presentación. La solución separa el contrato de datos, las operaciones del constructor y la experiencia visual.

El MVP permite:

- Añadir y configurar campos de texto, email, número, área de texto, selección y checkbox.
- Reordenar y eliminar campos con controles accesibles.
- Probar respuestas con validación de obligatoriedad, formato, límites y opciones.
- Persistir el borrador en `localStorage` y continuar en modo memoria si el navegador falla.
- Exportar una definición JSON validada con Zod.

La decisión técnica más importante fue mantener las reglas puras y separadas de React. Así, las operaciones del constructor y la validación se prueban sin montar la interfaz ni depender del navegador.

No hay backend ni credenciales en este MVP. El fallback local permite hacer la demo incluso sin red o sin almacenamiento disponible.

La suite termina con cobertura de modelo, validación, persistencia, accesibilidad estructural y casos límite. El código está disponible en el proyecto del Día 20.

#React #TypeScript #Vite #Zod #Frontend #30Dias30Proyectos