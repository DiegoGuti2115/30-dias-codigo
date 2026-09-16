# Rastreador de Hábitos

Aplicación web del Día 17 del reto 30 Días de Código. Permite visualizar hábitos, registrar el cumplimiento de los últimos siete días y crear nuevos hábitos desde un formulario.

## Estado del proyecto

La aplicación cuenta con la interfaz, la persistencia local y las pruebas principales implementadas:

- Listado de hábitos activos.
- Cuadrícula semanal interactiva para marcar y desmarcar días.
- Formulario modal para crear hábitos.
- Frecuencia diaria o semanal.
- Color y descripción configurables por hábito.
- Diseño responsive con Tailwind CSS.
- Persistencia local de hábitos y registros mediante IndexedDB.
- Eliminación de hábitos con limpieza de su historial.

En la primera ejecución se cargan los datos mock como datos iniciales. A partir de ahí, los cambios se guardan en el navegador y sobreviven a una recarga. Si IndexedDB no está disponible, la aplicación conserva los mocks como fallback en memoria.

## Tecnologías

- React 19
- TypeScript
- Vite
- Tailwind CSS 4
- IndexedDB mediante `idb`
- ESLint

## Requisitos

- Node.js 20 o superior.
- npm.

## Instalación

Desde esta carpeta:

```bash
npm install
```

## Comandos

Iniciar el servidor de desarrollo:

```bash
npm run dev
```

Crear una compilación de producción:

```bash
npm run build
```

Comprobar el código con ESLint:

```bash
npm run lint
```

Ejecutar las pruebas automatizadas:

```bash
npm test
```

Previsualizar la compilación de producción:

```bash
npm run preview
```

## Estructura

```text
src/
├── components/
│   ├── HabitForm.tsx      # Modal para crear hábitos
│   ├── HabitList.tsx      # Lista y orquestación de la pantalla
│   └── WeeklyGrid.tsx     # Registro de los últimos siete días
├── db/
│   ├── mocks.ts            # Datos iniciales de desarrollo
│   └── storage.ts          # Adaptador IndexedDB
├── hooks/
│   └── useHabits.ts       # Estado y operaciones de hábitos
├── utils/
│   ├── habitState.ts       # Operaciones puras de estado
│   └── types.ts            # Tipos Habit y HabitLog
├── App.tsx
└── main.tsx
```

Las pruebas viven en `tests/` y cubren persistencia IndexedDB, marcado/desmarcado de fechas pasadas y eliminación de hábitos con historial.

La demo y el borrador de publicación están documentados en:

- [Guion de demo](docs/DEMO_SCRIPT.md).
- [Borrador para LinkedIn](docs/LINKEDIN_POST.md).

## Flujo actual

`App` monta `HabitList`. El hook `useHabits` hidrata el estado desde IndexedDB, consulta el estado de cada día, alterna registros, añade hábitos y elimina el hábito junto con su historial. `HabitForm` emite los datos del nuevo hábito y `HabitList` los incorpora al estado persistido. Si el almacenamiento local no está disponible, el hook mantiene los mocks como fallback para que la interfaz siga funcionando.

### Ciclo de datos

1. `useHabits` abre la base `habit-tracker` mediante `idb`.
2. `storage.ts` lee los object stores `habits` y `logs`.
3. Si ambos están vacíos, se cargan `MOCK_HABITS` y `MOCK_LOGS` como datos iniciales.
4. Las acciones de la interfaz actualizan el estado React.
5. Cada cambio guarda un snapshot completo en IndexedDB.
6. Al recargar, el snapshot reemplaza los datos iniciales y conserva el progreso local.

Redis no forma parte de la aplicación actual. La sincronización remota queda como mejora futura; el fallback vigente es local y evita que la ausencia de IndexedDB deje la interfaz inutilizable.

## Próximos pasos

1. Grabar el GIF de 15 segundos siguiendo `docs/DEMO_SCRIPT.md`.
2. Evaluar la sincronización opcional con Redis como mejora futura.

Consulta [ROADMAP.md](ROADMAP.md) para el detalle de las fases y tareas.
