# Post para LinkedIn

¿De verdad necesitas una nube para marcar un hábito?

En el Día 17 de #30DiasDeCodigo construí un rastreador de hábitos con React, TypeScript, Vite y Tailwind CSS.

Pero el reto no era dibujar una lista bonita.

Era conseguir que la aplicación siguiera siendo útil cuando no hay conexión.

Por eso implementé un enfoque local-first:

- Los datos se guardan en IndexedDB mediante `idb`.
- El estado se recupera al abrir la aplicación.
- Los cambios sobreviven a una recarga.
- La primera ejecución se inicializa con datos mock.
- Si IndexedDB no está disponible, existe un fallback en memoria.

La interfaz permite crear hábitos, elegir frecuencia y color, marcar los últimos siete días y eliminar un hábito junto con su historial.

También añadí pruebas para tres casos que suelen olvidarse:

1. Recuperar datos guardados en una nueva sesión.
2. Marcar y desmarcar una fecha pasada.
3. Eliminar un hábito sin dejar registros huérfanos.

Resultado: 4 pruebas pasando, build correcto y lint limpio.

La lección de hoy: la persistencia local no es solo una optimización. Puede ser la diferencia entre una herramienta que funciona en el mundo real y otra que depende de que todo salga perfecto.

¿En tus aplicaciones prefieres empezar por la nube o por una experiencia local que después sincroniza?

#React #TypeScript #IndexedDB #OfflineFirst #Frontend
