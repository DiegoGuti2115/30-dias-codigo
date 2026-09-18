# Hoja de Ruta: Constructor de formularios (Día 20)

El desarrollo se divide en fases pequeñas para mantener el límite de tres horas del reto y conservar un incremento demostrable en cada etapa. Todas las tareas parten pendientes porque esta primera entrega solo define documentación y estructura.

## Fase 0: Alcance y estructura

- [x] Crear la carpeta `projects/day-20-form-builder`.
- [x] Redactar `README.md` con problema, alcance, reglas y fallback.
- [x] Redactar este `ROADMAP.md`.
- [x] Reservar `src`, `tests`, `data`, `assets` y `docs`.
- [x] Reservar `src/components`, `src/hooks` y `src/utils`.
- [x] Confirmar que el MVP no requiere backend ni credenciales.

**Criterio de salida:** el contrato del MVP y la estructura de trabajo están definidos sin incluir implementación.

**Estado:** Fase completada. La estructura base y la documentación inicial están preparadas para comenzar el contrato de datos.

## Fase 1: Contrato del formulario y fixtures

- [x] Definir los tipos `FormDefinition`, `FormField`, `FieldType` y `FieldOption`.
- [x] Definir el esquema Zod de la definición serializada.
- [x] Fijar los tipos iniciales: `text`, `email`, `number`, `textarea`, `select` y `checkbox`.
- [x] Definir reglas para identificadores, nombres internos, etiquetas, posiciones y opciones.
- [x] Preparar una definición de formulario de ejemplo en `data/`.
- [x] Crear funciones puras para normalizar y clonar definiciones.

**Criterio de salida:** una definición válida puede leerse, validarse y transformarse sin depender de React ni del navegador.

**Estado:** Fase completada. El contrato vive en `src/utils/`, el fixture de contacto en `data/contact-form.json` y las reglas principales tienen pruebas puras.

## Fase 2: Operaciones del constructor

- [x] Implementar añadir campo con valores iniciales según el tipo.
- [x] Implementar edición de propiedades comunes y específicas por tipo.
- [x] Implementar reordenación con controles explícitos.
- [x] Implementar eliminación con una operación pura que la futura UI podrá confirmar.
- [x] Mantener nombres internos únicos y posiciones consistentes.
- [x] Cubrir las operaciones con pruebas de datos puros.

**Criterio de salida:** el modelo puede representar cualquier formulario del MVP y sus operaciones no mutan el estado original.

**Estado:** Fase completada. `src/utils/operations.ts` expone operaciones inmutables para añadir, actualizar, mover y eliminar campos; cada resultado se normaliza y vuelve a validar con Zod. La suite cubre defaults por tipo, nombres únicos, reordenación, eliminación, errores y ausencia de mutaciones.

## Fase 3: Interfaz del constructor

- [x] Construir el layout responsive del constructor.
- [x] Crear la lista de campos configurables.
- [x] Crear el selector de tipo y los paneles de configuración por campo.
- [x] Añadir edición de etiqueta, nombre, ayuda, obligatoriedad y reglas.
- [x] Añadir configuración de opciones para `select`.
- [x] Mostrar errores de configuración junto al control correspondiente.
- [x] Añadir estados de formulario vacío y de configuración válida.
- [x] Revisar navegación por teclado, foco y nombres accesibles.

**Criterio de salida:** una persona puede diseñar un formulario completo desde el navegador sin editar archivos.

**Estado:** Fase completada. La interfaz React se compone de un constructor responsive, editores por tipo, controles accesibles de reordenación y eliminación, y una previsualización sincronizada. Las operaciones del dominio gestionan los errores de configuración sin bloquear la aplicación.

## Fase 4: Previsualización y validación

- [x] Renderizar cada tipo de campo a partir de la definición compartida.
- [x] Crear el modo de prueba separado del modo constructor.
- [x] Validar obligatoriedad, email, número, longitud, opciones y checkbox.
- [x] Mostrar errores por campo sin perder los valores introducidos.
- [x] Mostrar una confirmación de envío local cuando los datos sean válidos.
- [x] Cubrir el motor de validación con pruebas de casos válidos y erróneos.

**Criterio de salida:** la previsualización se comporta según el mismo contrato que el constructor y permite corregir errores de forma clara.

**Estado:** Fase completada. `src/utils/responseValidation.ts` contiene el motor puro de validación y `FormPreview` ofrece modos de diseño y prueba, errores por campo, preservación de valores y confirmación de envío simulado. La suite cubre respuestas válidas, obligatorios, email, longitud, selección y checkbox.

## Fase 5: Persistencia, exportación y fallback

- [x] Implementar el adaptador de almacenamiento local.
- [x] Guardar y recuperar el borrador del formulario.
- [x] Cargar el fixture solo cuando no exista un borrador.
- [x] Añadir fallback en memoria ante ausencia o fallo del almacenamiento.
- [x] Exponer un aviso no bloqueante cuando se active el modo memoria.
- [x] Exportar la definición validada como JSON.
- [x] Probar la recuperación tras recargar y la exportación sin pérdida semántica.

**Criterio de salida:** el constructor sigue siendo útil offline, permite recuperar el trabajo y produce una definición portable.

**Estado:** Fase completada. `src/utils/storage.ts` encapsula `localStorage` con validación Zod, el hook hidrata el último borrador y persiste las operaciones, y la interfaz cambia a modo memoria cuando el navegador no permite leer o escribir. La exportación descarga una definición JSON validada; las pruebas cubren lectura inicial, persistencia, datos corruptos y serialización.

## Fase 6: Pruebas, accesibilidad y responsive

- [x] Probar operaciones del modelo con formularios vacíos y con varios campos.
- [x] Probar unicidad de nombres y normalización de espacios.
- [x] Probar reglas específicas de cada tipo de campo.
- [x] Probar edición, reordenación y eliminación sin pérdida de datos.
- [x] Probar persistencia y fallback en memoria.
- [x] Probar exportación de definiciones válidas.
- [x] Validar foco, teclado, mensajes de error y etiquetas accesibles.
- [x] Revisar escritorio, tablet y móvil sin overflow horizontal.
- [x] Ejecutar lint, build y la suite completa.

**Criterio de salida:** el flujo principal y sus casos límite tienen verificaciones reproducibles y la aplicación compila sin errores.

**Estado:** Fase completada. La suite cubre formularios vacíos, los seis tipos de campo, límites numéricos, errores de persistencia, exportación y operaciones inmutables. El preview usa etiquetas explícitas, roles de tabs, foco visible y controles accesibles; el layout fue revisado en escritorio y móvil sin overflow horizontal. `npm test`, `npm run build` y `npm run lint` pasan.

## Fase 7: Documentación, demo y publicación

- [x] Redactar `docs/DEMO_SCRIPT.md` con una demo reproducible de 15 segundos.
- [x] Capturar una referencia visual del constructor y la previsualización.
- [x] Redactar `docs/LINKEDIN_POST.md` con el problema, las decisiones y el fallback.
- [x] Actualizar `README.md` con los comandos y el estado real del proyecto.
- [x] Confirmar que no hay secretos ni archivos de entorno reales.
- [x] Marcar como completados únicamente los criterios verificados.

**Criterio de salida:** el proyecto puede instalarse, validarse, demostrarse y enlazarse desde el catálogo principal.

**Estado:** Fase completada. El guion de demo, el borrador de publicación, la referencia visual y la revisión de seguridad están documentados. La auditoría no encontró secretos ni vulnerabilidades conocidas en dependencias; el proyecto queda preparado para revisión y primer commit del MVP.

## Criterios de terminado

- Se puede crear y configurar un formulario con los tipos del MVP.
- Los campos pueden editarse, reordenarse y eliminarse sin inconsistencias.
- La previsualización refleja la definición actual y valida las respuestas.
- Los nombres internos son únicos y la definición exportada es válida.
- El borrador persiste localmente cuando el almacenamiento está disponible.
- El modo memoria mantiene la aplicación utilizable cuando el almacenamiento falla.
- Las reglas de negocio, validación y persistencia tienen pruebas reproducibles.
- La interfaz funciona en escritorio y móvil y es navegable con teclado.
- `README.md` permite instalar, ejecutar y validar el proyecto.

## Mejoras futuras

- Drag and drop con soporte completo de teclado y puntero.
- Más tipos de campo, como fecha, radio, teléfono y rango.
- Lógica condicional entre campos.
- Temas visuales y personalización de estilos.
- Importación de definiciones JSON existentes.
- Exportación a HTML accesible.
- Guardado de varias plantillas locales.
- Envío opcional a una API con autenticación y control de spam.
