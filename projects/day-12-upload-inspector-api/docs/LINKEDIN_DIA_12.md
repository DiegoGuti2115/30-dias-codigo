# Texto de publicación verificable — Día 12/30

## Titular

> Día 12/30 — Construí una API local que inspecciona un archivo y devuelve metadatos verificables, sin almacenarlo.

## Cuerpo

Cuando una aplicación recibe un archivo, el nombre, la extensión y el tipo MIME llegan desde el cliente. Son metadatos útiles, pero no prueban el contenido ni certifican que el archivo sea seguro.

Para este Día 12 construí una API HTTP local con FastAPI que recibe exactamente un archivo en `multipart/form-data` y responde con su nombre validado, tamaño, tipo de medio declarado, extensión derivada y una huella SHA-256 de los bytes recibidos.

La decisión clave fue limitar el alcance: cada carga se procesa de forma efímera, sin persistir archivos, resultados ni metadatos. La v1 también valida el nombre para rechazar separadores, intentos de traversal y caracteres de control; procesa el contenido en bloques y fija un máximo de 5 MiB.

El resultado no intenta interpretar el archivo ni detectar su formato real. Tampoco es un antivirus, no detecta malware y no valida que el MIME declarado coincida con los bytes. Precisamente por eso el contrato deja explícitos tanto los datos que ofrece como sus límites.

La arquitectura separa el transporte HTTP de la inspección pura: FastAPI gestiona la solicitud multipart y el núcleo local valida, mide y calcula la huella. Las pruebas unitarias, HTTP y de entrega cubren el contrato, límites, errores seguros, determinismo y aislamiento entre solicitudes.

## Cierre

- **Stack:** Python 3.11+, FastAPI, Pydantic, Pytest, HTTPX y SHA-256 de la biblioteca estándar.
- **Código:** [`projects/day-12-upload-inspector-api`](..).
- **Carrusel:** [`assets/carrusel-linkedin.html`](../assets/carrusel-linkedin.html).
- **Contrato:** [`docs/CONTRATO_API_V1.md`](CONTRATO_API_V1.md).

¿Qué comprobarías primero al recibir un archivo: límite, nombre, tipo declarado o trazabilidad del contenido?

`#30Dias30Proyectos #BuildInPublic #Python #FastAPI #APISecurity #FileUpload #Testing`

## Guion del carrusel

1. **Portada:** la pregunta sobre qué ocurre antes de confiar en un archivo.
2. **Problema:** el nombre, extensión y MIME son datos declarados por el cliente.
3. **Contexto:** una v1 local, efímera y limitada a 5 MiB.
4. **Solución:** recepción multipart, validación del nombre, lectura por bloques y SHA-256.
5. **Funcionalidades:** huella, extensión, MIME declarado y errores uniformes.
6. **Flujo:** `POST /api/v1/inspect` con un ejemplo del fixture seguro.
7. **Diferenciador:** separación de responsabilidades, errores sin filtraciones y pruebas.
8. **CTA:** debate sobre las primeras comprobaciones al recibir una carga.
