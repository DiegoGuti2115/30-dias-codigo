# Roadmap — Conversor JSON ↔ CSV

## Objetivo de entrega

Construir una herramienta CLI local en Python 3.11+ que convierta archivos JSON a CSV y CSV a JSON con validaciones explícitas, resultados reproducibles y protección frente a sobrescrituras accidentales.

La primera versión se limita a JSON como lista de objetos planos y CSV con cabeceras. La conversión de CSV a JSON preservará todos los valores como texto.

## Principios de ejecución

- Mantener un problema único y un flujo principal pequeño, conforme al límite temporal del reto.
- Usar rutas de entrada y salida explícitas; no explorar directorios ni modificar entradas.
- Validar datos y destino antes de crear el resultado final.
- Preferir la biblioteca estándar de Python para no añadir dependencias innecesarias.
- Conservar fixtures y pruebas locales para demostrar el comportamiento sin servicios externos.
- Congelar el alcance de la primera versión una vez validado el flujo completo.

## Fase 0 — Preparación estructural y documental

**Estado:** completada.

**Propósito:** dejar una base de proyecto clara sin incorporar implementación ejecutable.

**Entregables:**

- Directorios para código, pruebas, documentación, ejemplos, fixtures, resultados esperados y recursos de demo.
- Archivos Python vacíos en [`src/main.py`](src/main.py), [`src/converters.py`](src/converters.py), [`src/validators.py`](src/validators.py), [`tests/test_converters.py`](tests/test_converters.py) y [`tests/test_cli.py`](tests/test_cli.py).
- Documentación inicial en [`README.md`](README.md).
- Este roadmap en [`ROADMAP.md`](ROADMAP.md).
- Archivos de soporte [`requirements.txt`](requirements.txt) y [`.gitignore`](.gitignore).

**Criterio de salida:** el alcance está documentado y no existe implementación en archivos Python.

## Fase 1 — Definición de interfaces y criterios de aceptación

**Propósito:** concretar el contrato de la CLI y las reglas de transformación antes de escribir la lógica.

**Actividades:**

- Elegir los nombres definitivos de los subcomandos para JSON a CSV y CSV a JSON.
- Definir argumentos obligatorios para entrada y salida.
- Definir la opción explícita de sobrescritura y su semántica.
- Establecer mensajes de éxito, errores y códigos de retorno.
- Fijar el orden estable de columnas para JSON a CSV.
- Precisar la política para claves ausentes, valores vacíos y archivos vacíos.
- Redactar criterios de aceptación verificables.

**Entregables:**

- Contrato de CLI actualizado en [`README.md`](README.md).
- Lista de casos de aceptación en [`docs`](docs).
- Matriz inicial de entradas válidas e inválidas.

**Dependencias:** fase 0 completada.

**Criterio de salida:** el comportamiento esperado puede implementarse y probarse sin ambigüedades.

## Fase 2 — Diseño de datos y fixtures

**Propósito:** disponer de ejemplos mínimos que definan la conversión y los errores esperados.

**Actividades:**

- Crear JSON válidos con objetos de claves uniformes y no uniformes.
- Crear CSV válidos con cabeceras y valores que parezcan números, booleanos, fechas, nulos y códigos con ceros iniciales.
- Preparar casos con comas, comillas y saltos de línea dentro de celdas.
- Preparar entradas inválidas: JSON mal formado, raíz no permitida, anidamiento, CSV sin cabecera y cabeceras duplicadas o vacías.
- Definir resultados de referencia en [`data/expected`](data/expected).

**Entregables:**

- Fixtures en [`data/fixtures`](data/fixtures).
- Salidas verificables en [`data/expected`](data/expected).
- Inventario de escenarios en [`docs`](docs).

**Dependencias:** reglas cerradas en fase 1.

**Criterio de salida:** cada caso de aceptación tiene una entrada y un resultado o error esperado.

## Fase 3 — Implementación del núcleo de conversión

**Propósito:** implementar transformaciones puras, deterministas y reutilizables, separadas de la interacción por CLI.

**Actividades:**

- Implementar lectura y validación del formato JSON admitido.
- Convertir una lista de objetos planos en cabeceras y filas CSV.
- Completar celdas vacías para claves ausentes de acuerdo con la política de fase 1.
- Implementar lectura de CSV con cabeceras válidas.
- Convertir cada fila CSV en un objeto JSON.
- Preservar los valores CSV como texto sin inferir tipos.
- Escribir JSON y CSV con codificación UTF-8 y comportamiento estable.

**Entregables:**

- Lógica de transformación en [`src/converters.py`](src/converters.py).
- Validaciones de estructura de datos en [`src/validators.py`](src/validators.py).

**Dependencias:** fases 1 y 2.

**Criterio de salida:** el núcleo convierte los fixtures válidos sin depender de la CLI.

## Fase 4 — Interfaz CLI y seguridad de archivos

**Propósito:** exponer el núcleo mediante una experiencia de terminal segura y clara.

**Actividades:**

- Implementar el punto de entrada en [`src/main.py`](src/main.py).
- Parsear subcomandos y argumentos documentados.
- Verificar existencia, lectura y extensión de la entrada.
- Verificar el directorio de destino y bloquear por defecto archivos de salida ya existentes.
- Incorporar la opción explícita de sobrescritura definida en fase 1.
- Asegurar que un error de validación no deja resultados parciales.
- Emitir mensajes accionables y códigos de salida coherentes.

**Entregables:**

- CLI funcional para ambos sentidos de conversión.
- Comportamiento seguro ante colisiones de salida y errores de E/S.

**Dependencias:** fase 3.

**Criterio de salida:** una persona puede convertir un fixture desde la terminal sin editar código ni archivos de configuración.

## Fase 5 — Validaciones y manejo de errores

**Propósito:** hacer explícitos los límites del formato y evitar pérdida de información o resultados ambiguos.

**Actividades:**

- Rechazar JSON que no sea una lista de objetos planos.
- Rechazar objetos o listas anidadas en JSON.
- Rechazar CSV sin cabeceras y con cabeceras vacías o duplicadas.
- Tratar de forma documentada archivos vacíos y filas incompletas.
- Gestionar errores de sintaxis, codificación, permisos, rutas y escritura.
- Confirmar que los valores CSV no se convierten automáticamente a tipos JSON.

**Entregables:**

- Validaciones completas en [`src/validators.py`](src/validators.py).
- Tabla de errores actualizada en [`README.md`](README.md).

**Dependencias:** fases 3 y 4.

**Criterio de salida:** todas las entradas no admitidas fallan antes de escribir una salida final.

## Fase 6 — Pruebas automatizadas

**Propósito:** comprobar el flujo feliz, la preservación de decisiones de formato y las protecciones de seguridad.

**Actividades:**

- Probar JSON a CSV con datos uniformes y heterogéneos.
- Probar CSV a JSON y verificar que los valores sean cadenas de texto.
- Probar caracteres especiales compatibles con CSV.
- Probar los errores de formato, cabeceras y anidamiento.
- Probar rutas inexistentes y bloqueo de sobrescritura.
- Probar códigos de salida y mensajes principales de la CLI.

**Entregables:**

- Pruebas del núcleo en [`tests/test_converters.py`](tests/test_converters.py).
- Pruebas de la CLI en [`tests/test_cli.py`](tests/test_cli.py).
- Guía de ejecución de pruebas en [`README.md`](README.md).

**Dependencias:** fases 4 y 5.

**Criterio de salida:** la suite se ejecuta localmente y cubre los criterios de aceptación de la primera versión.

## Fase 7 — Documentación y demostración

**Propósito:** permitir reproducir la instalación, uso, prueba y demostración del proyecto.

**Actividades:**

- Sustituir el uso previsto por comandos CLI reales y comprobados.
- Documentar el flujo de instalación y pruebas desde una copia limpia.
- Incorporar ejemplos basados en fixtures sin datos sensibles.
- Documentar límites, errores y la decisión de preservar texto desde CSV.
- Grabar un GIF o vídeo de hasta 15 segundos que muestre entrada, acción y salida.
- Guardar el recurso de demo en [`assets`](assets).

**Entregables:**

- [`README.md`](README.md) finalizado.
- Material de demostración en [`assets`](assets).
- Ejemplos reproducibles en [`examples`](examples).

**Dependencias:** fase 6.

**Criterio de salida:** una persona puede seguir la documentación y reproducir una conversión completa.

## Fase 8 — Empaquetado y cierre de la primera versión

**Propósito:** realizar una entrega estable, autocontenida y publicable dentro del reto.

**Actividades:**

- Revisar que no haya secretos ni dependencias no documentadas.
- Confirmar compatibilidad con Python 3.11+.
- Verificar el proyecto desde un entorno limpio.
- Congelar el alcance y corregir solo bloqueantes.
- Actualizar el enlace del Día 03 y los materiales de demo/publicación del repositorio principal.

**Entregables:**

- Primera versión funcional validada.
- Dependencias aisladas en [`requirements.txt`](requirements.txt).
- Documentación, pruebas y demo disponibles localmente.

**Dependencias:** fase 7.

**Criterio de salida:** se cumplen los criterios de terminado del reto para el flujo principal local.

## Funcionalidades incluidas en la primera versión

- CLI local bidireccional JSON ↔ CSV.
- JSON como lista de objetos planos.
- CSV con una fila de cabeceras.
- Valores CSV conservados como texto en JSON.
- Columnas estables y tratamiento documentado de claves ausentes.
- Validaciones de formato y rutas.
- Bloqueo de sobrescritura por defecto y autorización explícita prevista.
- Fixtures, pruebas automatizadas, documentación y demo local.

## Mejoras posteriores — Fuera de alcance

Las siguientes capacidades no se implementarán como parte de la primera versión:

### JSON anidado

- Aplanamiento configurable de objetos y listas anidadas.
- Reconstrucción de estructuras anidadas al leer CSV.
- Convenciones de rutas de claves o separadores configurables.

### Tipos y esquemas

- Inferencia de números, booleanos, nulos, fechas y horas.
- Esquemas explícitos para forzar o validar tipos.
- Tratamiento configurable de valores ausentes y nulos.

### Rendimiento y procesamiento masivo

- Conversión de múltiples archivos o directorios.
- Procesamiento recursivo.
- Streaming para archivos de gran tamaño.
- Paralelización, métricas y registros avanzados.

### Experiencia de usuario

- Interfaz gráfica de escritorio o web.
- Previsualización interactiva.
- Confirmaciones visuales, historial o deshacer.

### Formatos e integraciones

- XML, YAML, XLSX, TSV, Parquet u otros formatos.
- Integración con almacenamiento cloud, APIs externas o bases de datos.
- Autenticación, usuarios o colaboración remota.

## Riesgos y decisiones a vigilar

- CSV no conserva tipos JSON por sí mismo; la primera versión resuelve esta ambigüedad manteniendo todo como texto al generar JSON.
- La elección del orden de las columnas debe documentarse y probarse para que las salidas sean estables.
- La sobrescritura debe seguir siendo una excepción explícita para prevenir pérdida de datos.
- Cualquier ampliación hacia anidamiento, inferencia de tipos o formatos nuevos requiere revisar fixtures, validaciones, pruebas y documentación antes de implementarse.
