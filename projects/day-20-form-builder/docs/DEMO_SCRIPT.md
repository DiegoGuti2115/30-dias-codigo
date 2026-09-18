# Guion de demo: Constructor de formularios

Duración objetivo: 15 segundos.

## Preparación

```bash
npm install
npm run dev
```

Abrir la URL local que muestre Vite. Si existe un borrador anterior, usar una ventana privada o limpiar el almacenamiento del sitio para comenzar con el fixture de contacto.

## Secuencia

1. **0-3 s:** mostrar el constructor con los cinco campos del formulario de contacto y la previsualización sincronizada.
2. **3-6 s:** pulsar `+ Número` para añadir un campo nuevo; comprobar que aparece en la lista y en la previsualización.
3. **6-9 s:** cambiar la etiqueta del nuevo campo, moverlo una posición y mostrar que la vista previa refleja el orden actualizado.
4. **9-12 s:** abrir `Probar formulario`, pulsar `Validar formulario` con campos obligatorios vacíos y mostrar los errores junto a cada control.
5. **12-15 s:** completar los campos mínimos, validar correctamente y pulsar `Exportar JSON` para descargar la definición.

## Resultado esperado

- El constructor y la previsualización comparten la misma definición.
- Los errores aparecen sin perder los valores introducidos.
- La confirmación indica que el envío es simulado y local.
- El archivo JSON descargado contiene una definición validable del formulario.

## Fallback de demo

Si `localStorage` no está disponible o falla, la cabecera muestra `Modo memoria`. La edición y la validación continúan funcionando durante la sesión, aunque una recarga no conserva los cambios.