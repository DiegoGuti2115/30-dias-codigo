# Guion de Demostración (15 segundos)

Este guion está diseñado para grabar la demostración del flujo principal (ideal en formato vertical u horizontal para la actualización diaria). Utiliza exclusivamente datos sintéticos, asegurando que no se expone información sensible.

**Preparación:**
- Terminal abierta en el directorio `projects/day-15-expense-splitter`.
- Proyecto previamente compilado (`npm run build`).

**Secuencia (0:00 - 0:15):**

1. **(0:00 - 0:04) El Fixture:**
   - *Visual:* Muestra brevemente el archivo `data/fixtures/viaje.json` en el editor.
   - *Voz/Texto:* "Día 15: Divisor de Gastos. Aquí tenemos un JSON con los gastos de un viaje entre varias personas."

2. **(0:04 - 0:09) La Ejecución:**
   - *Visual:* Pasa a la terminal y ejecuta `npm exec expense-splitter -- ./data/fixtures/viaje.json`.
   - *Voz/Texto:* "Ejecutamos nuestra CLI local con el archivo de entrada puro, sin dependencias externas."

3. **(0:09 - 0:15) El Resultado:**
   - *Visual:* Haz un poco de scroll en la terminal para mostrar el JSON de salida, enfocándote en los arrays `balances` y `transfers`.
   - *Voz/Texto:* "Y obtenemos al instante quién debe a quién y las transferencias exactas en céntimos para liquidar las deudas de forma determinista."