# Landing web local y demostración educativa

## Propósito

[`../assets/demo-interactiva.html`](../assets/demo-interactiva.html) es una landing page local para explicar el Validador de políticas de contraseña v1. Presenta el alcance real del proyecto, sus reglas, flujo, arquitectura, pruebas y límites de privacidad.

La página no sustituye la CLI ni añade una interfaz web al producto v1. Es un recurso estático de documentación y demostración: su JavaScript reproduce las reglas documentadas en el navegador para fines educativos.

## Inicio local

Desde la raíz del repositorio, inicia un servidor estático de la biblioteca estándar:

```text
python -m http.server 8000 -d projects/day-06-password-policy-checker
```

Abre esta dirección local en el navegador:

```text
http://localhost:8000/assets/demo-interactiva.html
```

No requiere dependencias, instalación, credenciales, red ni servicios de terceros. También puede abrirse directamente como archivo local, aunque el servidor estático facilita una revisión uniforme de enlaces y navegación.

## Demostración interactiva

- La demostración solo debe recibir texto sintético y no sensible.
- El botón de generación crea un valor sintético en memoria para ilustrar una entrada que cumple las reglas; no es una recomendación de credencial para uso real.
- La evaluación se realiza dentro del navegador mientras la página está abierta.
- La página no usa `fetch`, almacenamiento web, cookies, telemetría, formularios remotos ni llamadas de red.
- La visualización conserva el mismo orden de reglas, mensajes y condición global definidos por [`CONTRATO.md`](CONTRATO.md).
- La longitud exacta y el contenido introducido no se muestran en el panel de resultados.

La CLI real sigue teniendo una única forma de ejecución y solicita la entrada sin eco:

```text
python src/main.py check
```

Consulta los límites y los códigos de salida de la herramienta real en [`USO_SEGURO.md`](USO_SEGURO.md).

## Accesibilidad y diseño

La página usa estructura semántica, navegación por anclas, enlace para saltar a la demostración, etiquetas asociadas al campo, resultados con región `aria-live`, foco visible, controles operables con teclado y diseño responsive. Las transiciones se reducen cuando el sistema comunica `prefers-reduced-motion`.

## Verificación

Desde la raíz del repositorio:

```text
python -m unittest discover -s projects/day-06-password-policy-checker/tests -p "test_*.py" -v
python -m compileall -q projects/day-06-password-policy-checker/src
git diff --check
```

La comprobación de la web es manual y local: revisar la navegación con teclado, el comportamiento en ancho móvil, el botón de generar, el botón de limpiar y el orden de diagnósticos para una entrada sintética que no cumple la política.
