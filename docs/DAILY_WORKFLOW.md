# SOP diario — 30 Días, 30 Proyectos

## Bloques fijos

| Bloque | Tiempo | Resultado obligatorio |
|---|---:|---|
| Desarrollo | T0–T+120 min | Flujo principal implementado y comprobado localmente. |
| Documentación | T+120–T+150 min | README local, índice global y GIF/vídeo de 15 segundos. |
| Despliegue | T+150–T+165 min | Verificación final, commit y push a `main`. |
| Publicación | T+165–T+180 min | Post de LinkedIn con demo y enlace al código. |

## Política de integraciones externas

Una clave API, cuenta externa, recurso cloud o conexión entre servicios puede utilizarse si:

1. Aporta valor directo a la demo.
2. Las credenciales y la configuración pueden validarse con rapidez.
3. Existe una alternativa local, mock, fixture o modo demo documentado.
4. No se versionan secretos: usa `.env`; describe las variables sin valores en `.env.example`.

Durante los primeros 30 minutos solo se intentará una integración que tenga un fallback definido. Si antes de T+30 no existe una conexión o petición/respuesta validada, se abandona la integración para ese día y se implementa el fallback.

## Puertas de control

### Antes de T0

- Problema único, entrada, salida y flujo feliz definidos.
- Demo prevista y dependencias conocidas.
- Ruta principal, integración opcional y fallback local identificados.

### T+30

- Si una integración externa no está validada, activar el fallback irreversible.

### T+90

- Si el flujo feliz no está listo, eliminar primero integración opcional, persistencia no esencial, estilos avanzados, reintentos, métricas, autenticación y despliegue.

### T+120

- Congelar alcance. Corregir únicamente errores bloqueantes de la función principal, documentación o demo.

## Definition of Done

- [ ] El flujo principal funciona siguiendo instrucciones limpias.
- [ ] El fallback local está comprobado cuando existe una integración externa.
- [ ] Dependencias y versiones están aisladas en el proyecto.
- [ ] No hay secretos; las variables están documentadas en `.env.example` si aplican.
- [ ] README local con instalación, uso, prueba, integración y fallback.
- [ ] Prueba automatizada mínima o guion manual reproducible.
- [ ] Índice raíz actualizado con código, demo y post.
- [ ] GIF/vídeo de 15 segundos y recurso fuente guardados en `assets/`.
- [ ] Commit `feat: implementacion dia XX` enviado a `main`.
- [ ] Post de LinkedIn publicado con enlace directo al proyecto.
