# Guión de vídeo — Día 28: Validador de datasets de evaluación

## Objetivo

Mostrar en **15 segundos** un flujo real y comprensible: un dataset de evaluación contiene problemas, la CLI lo valida localmente y genera hallazgos accionables antes de que esos datos afecten a la evaluación de un sistema de IA.

El mensaje que debe quedar al final es:

> **Valida tu dataset antes de medir tu IA.**
>
> Local, reproducible y sin credenciales.

## Entregable recomendado

- **Duración:** 12 a 15 segundos.
- **Formato principal:** vídeo vertical MP4, `1080 × 1920`, para LinkedIn.
- **Copia alternativa:** `1920 × 1080` horizontal para GitHub y reutilización.
- **Captura:** pantalla a 1080p o superior; ampliar la terminal al 130–150 % para que el texto sea legible.
- **Audio:** opcional. El vídeo debe entenderse sin audio mediante textos breves en pantalla.
- **Estilo:** fondo oscuro de terminal, texto de alto contraste, un único color de alerta para errores/advertencias y transiciones simples por corte.

## Preparación antes de grabar

1. Abre una terminal en la carpeta del proyecto:

   ```bash
   cd projects/day-28-test-dataset-evaluator
   ```

2. Activa el entorno virtual si ya existe e instala el proyecto según las instrucciones de [`README.md`](../README.md). No muestres instalación en el vídeo: consume tiempo y no demuestra el resultado.

3. Usa el fixture inválido de fase 4 porque reúne los controles diferenciales del proyecto: cobertura, contratos de evaluación y posibles fugas.

4. Prepara el comando de demostración, pero **no lo ejecutes todavía**:

   ```bash
   python -m evaluation_dataset_validator.main data/examples/phase4-invalid.json --config config/phase4-verification.json --report output/phase4-report.json --output-format sarif --output output/phase4-report.sarif
   ```

   Este comando puede finalizar con código `1`; es el comportamiento esperado cuando el dataset contiene hallazgos de severidad `error`. La demostración debe mostrar precisamente que el informe se genera aunque haya errores de validación.

5. Antes de iniciar la captura, limpia o minimiza elementos personales: rutas sensibles, pestañas privadas, notificaciones, nombres de usuario y credenciales. El proyecto no requiere secretos para esta demo.

6. Ten abiertas estas dos vistas, en ventanas o pestañas independientes:

   - La terminal con el comando preparado.
   - El archivo generado `output/phase4-report.json`, abierto después de ejecutar el comando.

7. Configura el terminal para que la salida relevante sea visible. Si hay demasiado texto, aumenta la altura de la ventana, reduce el historial visible o graba dos tomas y únelas mediante cortes.

## Guión visual y de textos

| Tiempo | Qué debe verse | Acción durante la grabación | Texto en pantalla | Locución opcional |
|---|---|---|---|---|
| 0,0–2,0 s | Portada limpia con fondo de terminal desenfocado o captura del JSON inválido. | Añade el título en edición; no necesitas mover el cursor. | **¿Tu dataset de evaluación está listo?**<br>IDs duplicados, cobertura o fugas pueden sesgar la métrica. | “Antes de evaluar un sistema de IA, valida el dataset.” |
| 2,0–5,0 s | Terminal enfocada. Debe verse la ruta del dataset y el comando completo o su parte principal. | Ejecuta el comando con Enter. Mantén el cursor fuera del centro y no hagas scroll. | **JSON · JSONL · CSV**<br>Validación local y determinista. | “Esta CLI valida datasets localmente.” |
| 5,0–8,5 s | Salida de terminal con el resumen y varios hallazgos. Si la salida completa no cabe, muestra los códigos de hallazgo más claros. | Deja que termine el comando. Realiza un corte si la ejecución tarda más de un segundo. | **Detecta problemas antes de la evaluación** | “Detecta estructura inválida, cobertura ausente y posibles fugas.” |
| 8,5–11,5 s | Abre el informe `output/phase4-report.json` o el archivo SARIF. Enfoca `is_valid`, `summary` y 1–2 entradas de `issues`. | Haz un zoom suave en edición sobre los campos, no con zoom manual acelerado. | **Informe JSON canónico + SARIF** | “El resultado queda en un informe reproducible.” |
| 11,5–15,0 s | Pantalla final con una captura estática del informe o una composición sencilla con iconos de terminal, CI y métricas. | Añade URL del repositorio y el CTA en edición. | **Valida tu dataset antes de medir tu IA**<br>Local · reproducible · sin credenciales<br>[URL del repositorio] | “Código y documentación en el repositorio.” |

## Qué debe verse exactamente en el informe

Prioriza campos que demuestren la propuesta de valor sin obligar a leer un JSON completo:

1. `is_valid: false`, para comunicar que la validación detiene la confianza ciega en el dataset.
2. El bloque `summary`, para mostrar que existen recuentos agregados y no solo mensajes aislados.
3. Uno o dos elementos de `issues` con `code`, `severity`, `record_id` y `location` cuando estén disponibles.
4. Si el fixture los genera, prioriza `missing_coverage` y `train_evaluation_leakage`; explican los controles específicos para evaluación de IA.
5. Deja visible la ruta de salida `output/phase4-report.json` o `output/phase4-report.sarif`; prueba que el resultado se conserva e integra en flujo técnico.

No es necesario mostrar cada regla. Evita pantallas con demasiadas líneas, configuraciones extensas o la instalación de dependencias.

## Orden de edición

1. Graba una toma de portada de 2 segundos o créala directamente en el editor.
2. Graba la ejecución de la CLI en una sola toma limpia.
3. Graba una toma separada del informe JSON o SARIF con el contenido ya abierto.
4. Une las tres tomas con cortes directos; evita transiciones llamativas.
5. Inserta los textos del guión. Mantén cada texto en pantalla al menos 1,5 segundos.
6. Añade subtítulos si hay locución. Si no la hay, los textos en pantalla ya deben explicar la secuencia.
7. Exporta en MP4 H.264, 30 fps y revisa el vídeo desde el móvil antes de publicarlo.

## Checklist de revisión

- [ ] La primera pantalla plantea el problema en menos de dos segundos.
- [ ] Se ve una ejecución real de la CLI, no una simulación estática.
- [ ] Se ve al menos un informe generado con hallazgos reales.
- [ ] El texto es legible en una pantalla móvil.
- [ ] No aparecen datos personales, secretos ni notificaciones.
- [ ] El vídeo dura como máximo 15 segundos.
- [ ] La pantalla final contiene el CTA y `[URL del repositorio]` sustituida por el enlace público real.
- [ ] La descripción de LinkedIn usa el copy principal y enlaza al proyecto.

## Variante si el comando tarda demasiado

Graba la pulsación de Enter y corta inmediatamente a una terminal ya terminada con el informe generado. Es una edición válida si no alteras la salida ni presentas resultados inventados. El valor del vídeo está en enseñar el flujo y sus resultados comprobables, no en reproducir el tiempo de ejecución.

## Archivos relacionados

- Uso y comandos: [`README.md`](../README.md).
- Automatización, métricas y fallback: [`AUTOMATION.md`](../docs/AUTOMATION.md).
- Fixture para la demo: [`phase4-invalid.json`](../data/examples/phase4-invalid.json).
- Configuración reproducible: [`phase4-verification.json`](../config/phase4-verification.json).
