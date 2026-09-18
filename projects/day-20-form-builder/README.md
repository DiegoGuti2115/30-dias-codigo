# Constructor de formularios

Aplicación web del Día 20 del reto [30 Días, 30 Proyectos](../../README.md). Permite diseñar formularios sencillos desde el navegador, ordenar sus campos y probar el resultado antes de publicarlo o exportarlo.

**Estado:** Fase 7 completada. El contrato de datos, las operaciones inmutables, la interfaz responsive, la validación de respuestas, la persistencia local, la exportación JSON, la cobertura de calidad y la documentación de publicación están implementados.

## Problema

Crear un formulario pequeño suele implicar editar HTML manualmente, repetir estilos y comprobar la validación en varios lugares. Este proyecto concentra el diseño, la configuración de campos y la previsualización en una única interfaz local, con reglas explícitas y sin depender de un backend.

## Objetivo del MVP

Permitir que una persona construya un formulario básico mediante una interfaz visual, configure sus campos, pruebe la validación y obtenga una definición serializable del formulario.

## Alcance

- Crear un formulario con nombre, título y descripción opcionales.
- Añadir campos de tipo texto, email, número, área de texto, selección y checkbox.
- Configurar para cada campo una etiqueta, nombre interno, texto de ayuda y obligatoriedad.
- Configurar opciones para los campos de selección.
- Reordenar campos y editar su configuración.
- Eliminar campos con una acción explícita.
- Mostrar una previsualización del formulario en modo usuario.
- Validar el formulario generado según las reglas configuradas.
- Mostrar errores de configuración y de cumplimentación junto al campo correspondiente.
- Exportar la definición del formulario como JSON descargable o copiable.
- Conservar el borrador localmente cuando el almacenamiento del navegador esté disponible.
- Mantener un fallback en memoria si la persistencia local falla.
- Adaptar la experiencia a escritorio y móvil.
- Mantener la lógica del modelo y la validación separadas de los componentes React.

## Fuera de alcance

- Cuentas, autenticación, permisos o colaboración en tiempo real.
- Envío real de respuestas a un servidor.
- Base de datos remota, API o panel de respuestas.
- Constructor de lógica condicional avanzada.
- Subida de archivos, firma digital, captcha o pagos.
- Temas visuales completos y personalización CSS arbitraria.
- Drag and drop avanzado con librerías externas en la primera versión.
- Generación automática de formularios desde lenguaje natural.
- Integraciones externas o credenciales obligatorias.

## Tecnologías previstas

- React 19.
- TypeScript.
- Vite.
- Zod para validar la definición del formulario y los valores introducidos.
- CSS propio con variables de diseño y comportamiento responsive.
- Vitest para pruebas unitarias.
- ESLint.
- Persistencia local mediante `localStorage` o un adaptador equivalente, encapsulado detrás de una interfaz pequeña.

## Requisitos

- Node.js 20 o superior.
- npm.
- Navegador moderno con soporte para almacenamiento local.

## Instalación y comandos previstos

La configuración inicial de npm y los scripts de validación ya están disponibles:

```bash
npm install
npm run dev
npm run build
npm run lint
npm test
npm run preview
```

La interfaz Vite/React, la persistencia local y la exportación JSON ya están disponibles. `npm test`, `npm run build` y `npm run lint` validan el proyecto.

## Experiencia principal

1. La aplicación abre un formulario de ejemplo o un lienzo vacío.
2. La persona usuaria añade un campo y elige su tipo.
3. Configura etiqueta, nombre interno, ayuda, obligatoriedad y opciones cuando corresponda.
4. Reordena los campos y observa la previsualización actualizada.
5. Cambia al modo de prueba y completa el formulario.
6. La aplicación muestra errores de validación sin recargar la página.
7. La persona usuaria corrige los valores y obtiene una confirmación de envío local.
8. Puede exportar la definición del formulario y recuperar el borrador después de recargar.

## Modelo y reglas

- El formulario tiene un identificador estable, nombre, título, descripción y una lista ordenada de campos.
- Cada campo tiene un identificador estable, nombre interno, tipo, etiqueta, ayuda opcional, obligatoriedad y posición.
- Los nombres internos son obligatorios, se normalizan y no pueden repetirse dentro del mismo formulario.
- Las etiquetas son obligatorias después de eliminar espacios exteriores.
- Los tipos `select` requieren al menos una opción válida y no permiten valores duplicados.
- Un campo `checkbox` representa un valor booleano.
- Los campos de texto y área de texto aceptan reglas básicas de longitud cuando estén configuradas.
- Los campos `email` deben cumplir una validación de correo razonable en el modo de prueba.
- Los campos `number` deben producir valores numéricos y respetar límites configurados si existen.
- El orden de los campos se conserva al editar, mover o eliminar.
- La definición exportada debe poder validarse de nuevo sin depender de React.

## Persistencia y fallback local

- **Ruta principal:** estado local de React durante la edición y persistencia del borrador mediante un adaptador de almacenamiento del navegador.
- **Fallback:** si el almacenamiento no existe o falla una lectura o escritura, la sesión continúa en memoria y la interfaz muestra un aviso no bloqueante.
- **Fixture:** `data/` contendrá una definición de formulario de ejemplo para iniciar la demo sin configuración manual.
- **Criterio de cambio:** si la persistencia no funciona antes de T+30, se conserva la experiencia en memoria y se continúa con la demostración.
- No se requieren credenciales ni servicios externos para el MVP.

## Decisiones técnicas previstas

- La definición del formulario, las operaciones de añadir, editar, mover y eliminar, y la validación de respuestas vivirán en funciones puras.
- Zod validará tanto el contrato serializado del formulario como los datos de configuración introducidos por la interfaz.
- Un hook coordinará el estado del constructor, mientras los componentes se enfocarán en presentación y eventos.
- El modo constructor y el modo previsualización compartirán la misma definición para evitar divergencias entre lo diseñado y lo probado.
- El adaptador de persistencia quedará aislado de la UI para que un fallo del navegador no rompa la edición.
- La exportación usará una representación estable y versionable, preparada para futuras migraciones.
- Los controles de reordenación tendrán una alternativa explícita accesible; el arrastre visual no será el único camino.

## Estructura prevista

```text
day-20-form-builder/
├── README.md                 # Alcance, reglas, decisiones y fallback
├── ROADMAP.md                # Fases, tareas y criterios de salida
├── package.json              # Dependencias y scripts de validación
├── package-lock.json         # Versiones reproducibles de dependencias
├── tsconfig.json             # Configuración estricta de TypeScript
├── vitest.config.ts          # Configuración de pruebas
├── src/
│   ├── components/           # Constructor, previsualización, campos y controles
│   ├── hooks/                # Estado del formulario y persistencia coordinada
│   └── utils/                # Tipos, esquemas Zod y operaciones puras
├── tests/                    # Pruebas de modelo, validación y flujos principales
├── data/                     # Definiciones de formularios de ejemplo
├── assets/                   # Capturas y recursos de demostración
└── docs/                     # Guion de demo y borrador de publicación
```

## Validación prevista

- Crear, editar, mover y eliminar campos sin perder la configuración restante.
- Rechazar nombres internos vacíos o duplicados.
- Validar opciones obligatorias y duplicadas en campos de selección.
- Probar obligatoriedad, correo, número, longitud y checkbox.
- Comprobar que la previsualización usa el mismo contrato que el constructor.
- Exportar e importar una definición sin cambios semánticos.
- Recuperar el borrador tras recargar cuando el almacenamiento está disponible.
- Mantener la sesión utilizable en memoria cuando el almacenamiento falla.
- Revisar teclado, foco, mensajes accesibles y responsive en escritorio y móvil.
- Ejecutar lint, build y la suite completa antes de cerrar el proyecto.

Las Fases 3 a 7 ya fueron validadas con `npm run build`, `npm run lint` y `npm test`. La aplicación React incluye edición de campos, opciones de selección, reordenación explícita, eliminación, previsualización sincronizada, modo de prueba, persistencia local, fallback en memoria y exportación JSON. La revisión de seguridad está documentada en `docs/SECURITY_REVIEW.md`.

## Demo prevista

La demostración mostrará la creación de un formulario de contacto, la adición y reordenación de campos, un error de validación corregido en la previsualización y la exportación final de la definición. El guion reproducible está en [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md), el borrador de publicación en [`docs/LINKEDIN_POST.md`](docs/LINKEDIN_POST.md) y la revisión de seguridad en [`docs/SECURITY_REVIEW.md`](docs/SECURITY_REVIEW.md).

Consulta [ROADMAP.md](ROADMAP.md) para el plan de implementación por fases.
