# Revisión de seguridad

Fecha de revisión: 2026-09-18.

## Alcance

Se revisaron todos los archivos versionables del proyecto, excluyendo `node_modules`, builds y cachés generados.

## Hallazgos

- **Secretos y credenciales:** no se encontraron API keys, tokens, contraseñas, claves privadas, JWT ni cadenas con forma de credencial.
- **Integraciones externas:** no hay backend, API, autenticación ni variables de entorno requeridas.
- **Persistencia:** el único almacenamiento es `localStorage` del origen de la aplicación. El contenido se valida con Zod antes de hidratarlo y escribirlo.
- **Exportación:** el JSON se genera como `Blob`; no se interpreta como HTML ni se inserta como markup.
- **Entrada de usuario:** React escapa el contenido que se muestra en etiquetas, ayudas y opciones. No se usa `dangerouslySetInnerHTML`.
- **Dependencias:** `npm audit --audit-level=moderate` no reportó vulnerabilidades.
- **Repositorio:** `.gitignore` excluye `node_modules`, `dist`, `.env`, logs y artefactos de grabación; el lockfile queda incluido para reproducibilidad.
- **Privacidad:** Google Fonts es la única petición externa de la interfaz. Si se requiere una distribución sin terceros, las fuentes deben autoalojarse antes de publicar.

## Riesgos residuales

- `localStorage` no es un almacén cifrado: no debe usarse para datos personales sensibles.
- El modo memoria evita perder la sesión activa ante un fallo, pero no ofrece recuperación tras cerrar o recargar.
- La aplicación de desarrollo no define cabeceras HTTP de seguridad; el servidor de producción deberá configurar CSP, HSTS, `X-Content-Type-Options` y política de `Referrer`.

## Conclusión

No hay bloqueadores de seguridad para el primer commit del MVP local. Antes de una publicación de producción deberán resolverse las cabeceras del servidor y decidir si se elimina la dependencia de Google Fonts.