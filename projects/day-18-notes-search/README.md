# Buscador de Notas

Aplicación web del Día 18 del reto 30 Días de Código. Permite crear, consultar y organizar notas desde una interfaz rápida con búsqueda instantánea en el navegador.

## Objetivo

Construir una herramienta de notas pequeña, útil y offline-first que permita localizar información sin depender de un backend ni de una conexión a Internet.

## Alcance del MVP

- Crear notas con título, contenido y etiquetas.
- Editar y eliminar notas existentes.
- Buscar por coincidencias en título, contenido y etiquetas.
- Filtrar por etiqueta.
- Ordenar por fecha de actualización.
- Mostrar estados vacíos para una colección sin notas y para búsquedas sin resultados.
- Persistir las notas en IndexedDB.
- Mantener un fallback en memoria si IndexedDB no está disponible.
- Adaptar la interfaz a escritorio y móvil.
- Cubrir la lógica de búsqueda y persistencia con pruebas automatizadas.

## Fuera de alcance

- Sincronización entre dispositivos.
- Autenticación y cuentas de usuario.
- Editor Markdown enriquecido.
- Compartición pública de notas.
- Backend, API o base de datos remota.
- Integración con Redis u otros servicios externos.

## Tecnologías

- React 19.
- TypeScript.
- Vite.
- Tailwind CSS.
- IndexedDB mediante `idb`.
- Vitest para pruebas.
- ESLint.

## Requisitos

- Node.js 20 o superior.
- npm.
- Un navegador moderno con soporte para IndexedDB.

## Instalación y comandos

La configuración inicial de npm y los scripts ya están disponibles.

Los comandos son:

```bash
npm install
npm run dev
npm run build
npm run lint
npm test
npm run preview
```

## Experiencia principal

1. La aplicación carga las notas iniciales desde IndexedDB.
2. La persona usuaria escribe una consulta o selecciona una etiqueta.
3. La lista se actualiza mostrando coincidencias sin recargar la página.
4. Al seleccionar una nota, puede leerla o editarla.
5. Las altas, modificaciones y eliminaciones se guardan localmente.
6. Una recarga conserva el contenido previamente guardado.

La búsqueda es tolerante a mayúsculas y minúsculas, y trata título, contenido y etiquetas como un único índice lógico para el MVP. La lógica de filtrado se mantiene separada de la interfaz para poder probarla con datos puros.

El motor usa una coincidencia AND entre los términos de una consulta: cada término debe aparecer en el título, contenido o etiquetas de la nota. El filtro de etiqueta es exacto después de normalizar mayúsculas, espacios y el prefijo `#`. Los resultados se ordenan de forma estable y usan el identificador como desempate.

## Fallback local

IndexedDB es la fuente de persistencia principal. Si no está disponible o falla una operación, la aplicación conservará la sesión actual en memoria y mostrará la interfaz sin bloquear el flujo de trabajo. Los datos de ejemplo vivirán en `data/` y servirán para validar la experiencia durante el desarrollo.

No se usarán servicios externos en el MVP, por lo que no son necesarias credenciales ni un archivo `.env.example` en esta fase.

## Estructura

```text
day-18-notes-search/
├── src/
│   ├── components/   # Interfaz: buscador, lista, detalle y formulario
│   ├── db/           # Adaptador IndexedDB y datos iniciales
│   ├── hooks/        # Estado y operaciones de notas
│   └── utils/        # Tipos y lógica pura de búsqueda y filtros
├── tests/            # Pruebas unitarias y de persistencia
├── data/             # Fixtures de notas para desarrollo y demo
├── assets/           # Recursos de demostración
├── docs/             # Guion de demo y material de publicación
├── README.md
└── ROADMAP.md
```

El fixture inicial se encuentra en `data/notes.json`. El modelo `Note`, las consultas y las reglas de normalización viven en `src/utils/`.

## Reglas del modelo

- El título es obligatorio después de eliminar espacios exteriores.
- El contenido puede estar vacío para permitir notas rápidas.
- Las etiquetas se guardan sin `#`, en minúsculas, normalizadas y sin duplicados.
- Las fechas se representan como cadenas ISO 8601 en UTC.
- La búsqueda utilizará una versión normalizada del texto, pero conservará título y contenido originales para su presentación.

## Decisiones de diseño

- La búsqueda se ejecutará en cliente para ofrecer respuesta inmediata y funcionamiento sin red.
- El almacenamiento se encapsulará detrás de un adaptador para no acoplar los componentes a IndexedDB.
- Las operaciones de búsqueda, filtrado, ordenación y normalización serán funciones puras.
- La eliminación será una acción explícita y deberá poder cancelarse o confirmarse desde la interfaz.
- La interfaz distinguirá entre colección vacía, consulta sin coincidencias y carga inicial.

La base local `notes-search` contiene el object store `notes`, con el identificador de la nota como clave primaria y un índice de `updatedAt`. En la primera apertura, el adaptador carga `data/notes.json` solo si el store está vacío. Las operaciones de alta, edición y eliminación se ejecutan de forma optimista en la interfaz y se persisten mediante el hook `useNotes`.

Si IndexedDB no está disponible o una operación falla, `useNotes` conserva el estado en memoria, cambia la cabecera a `Modo memoria` y muestra un aviso no bloqueante. La aplicación sigue siendo utilizable, aunque esos cambios no sobreviven al cierre o recarga de la pestaña.

## Validación completada

- Crear, editar y eliminar una nota.
- Buscar por título, contenido y etiqueta.
- Comprobar que la búsqueda ignora diferencias de mayúsculas y minúsculas.
- Combinar texto de búsqueda con un filtro de etiqueta.
- Verificar la ordenación por actualización más reciente.
- Persistir cambios, cerrar y reabrir el almacenamiento, y recuperar las notas.
- Comprobar el fallback cuando IndexedDB no está disponible.
- Verificar navegación básica con teclado y etiquetas accesibles.

La validación final contiene 15 pruebas automatizadas distribuidas entre reglas del modelo, búsqueda, persistencia y fallback. También se ejecutaron `npm run lint` y `npm run build` correctamente, y se comprobó la interfaz en viewport de escritorio y móvil sin desbordamiento horizontal.

El flujo de demostración está documentado en [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) y el borrador de publicación en [docs/LINKEDIN_POST.md](docs/LINKEDIN_POST.md).

Consulta [ROADMAP.md](ROADMAP.md) para el plan de implementación por fases.