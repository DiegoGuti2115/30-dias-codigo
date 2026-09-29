# Seguridad y privacidad

## Principios obligatorios

1. Usar solo datos sintéticos en repositorio, fixtures, pruebas, capturas y demos.
2. No guardar secretos en código, documentación, variables públicas, logs ni control de versiones.
3. Recopilar la menor cantidad de datos posible y solo para un propósito documentado.
4. Exigir consentimiento explícito antes de cualquier dato real o integración externa.
5. Aplicar autenticación robusta, autorización por recurso y mínimo privilegio antes de cuentas reales.
6. Cifrar comunicaciones con HTTPS y datos persistidos cuando se introduzca almacenamiento.
7. Establecer retención, exportación, borrado, incidentes y auditoría antes de producción.

## Controles de desarrollo aplicados al MVP

- Validar toda entrada en frontend y backend: los modelos Pydantic rechazan entradas técnicas inválidas y el cliente valida las respuestas antes de presentarlas.
- Restringir CORS por entorno; no usar comodines en producción. La API local acepta únicamente los orígenes configurados y los métodos `GET` y `POST`.
- Evitar que logs y mensajes de error incluyan valores de métricas, identificadores o tokens; los controladores HTTP devuelven errores técnicos normalizados.
- Ejecutar `python scripts\\check-secrets.py` para revisar patrones de claves privadas, credenciales y asignaciones de secretos en los archivos versionables del proyecto.
- Ejecutar `npm audit --omit=dev --audit-level=high` desde `frontend/` para bloquear vulnerabilidades de alta severidad en dependencias de ejecución.
- Mantener fixtures deterministas, mínimos y claramente marcados como sintéticos.

## Checklist de revisión antes de integrar

### Accesibilidad

- [ ] El recorrido de carga, filtro y captura manual es usable solo con teclado, incluidos el enlace de salto y el foco visible.
- [ ] Cada control tiene una etiqueta o nombre accesible, y los estados de carga, éxito y error se anuncian de forma comprensible.
- [ ] La información de tendencias tiene una alternativa tabular y no depende solo de color, hover o gráficos.
- [ ] Se revisan contraste, zoom al 200 % y tamaño de controles en un navegador real antes de publicar una demo.

### Seguridad y privacidad

- [ ] Solo se incluyen fixtures, pruebas y capturas sintéticos; no hay datos personales, sanitarios reales, secretos ni tokens.
- [ ] `scripts\\verify-quality.cmd` finaliza correctamente, incluyendo el escaneo local de secretos y la auditoría de dependencias de ejecución.
- [ ] Los cambios de API mantienen validación de entradas, errores sin eco de valores y CORS explícitamente restringido.
- [ ] Cualquier cambio que incorpore autenticación, persistencia o datos reales se detiene hasta completar evaluación de amenazas, privacidad, autorización por recurso y revisión profesional aplicable.

## Antes de datos reales

Antes de tratar datos personales o sanitarios deben completarse una evaluación de impacto de privacidad, análisis de amenazas, revisión de seguridad, asesoramiento legal/regulatorio aplicable —incluido RGPD cuando corresponda— y validación del modelo de consentimiento. Este documento no constituye asesoramiento legal.

## Capacidades clínicas

No se implementarán funciones de diagnóstico, recomendación, triaje, prescripción o alerta clínica sin validación explícita de profesionales sanitarios cualificados y de las obligaciones regulatorias aplicables.
