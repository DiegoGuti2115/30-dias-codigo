# Decisiones de alcance — Generador de slugs

Este documento registra decisiones necesarias para iniciar el proyecto 13 sin atribuirlas al índice raíz. El índice solo fija **Generador de slugs**, categoría **CLI** y tecnología **TypeScript**; las decisiones siguientes concretan la primera versión local. Los cambios posteriores deberán documentar su impacto en [README.md](../README.md) y [ROADMAP.md](../ROADMAP.md).

## D-01 — Entrada única por argumento de CLI

**Decisión:** la interfaz v1 acepta exactamente un texto como argumento posicional. La ayuda solo se admite aislada mediante `--help` o `-h`; no hay subcomandos, opciones adicionales ni reconstrucción de varios argumentos.

**Motivo:** mantiene el proyecto atómico, elimina la ambigüedad de argumentos sin comillas y permite demostrar claramente entrada y salida en terminal.

**Consecuencia:** lectura por archivo, entrada estándar, modo interactivo y procesamiento por lotes quedan fuera de la versión 1. La ausencia, los argumentos múltiples, las opciones desconocidas y la ayuda combinada con texto son errores de uso con código `2`, según [CONTRATO_V1.md](CONTRATO_V1.md). La Fase 4 implementa esta interpretación en [src/cli.ts](../src/cli.ts).

## D-02 — Salida ASCII restringida

**Decisión:** un resultado correcto solo contiene letras ASCII en minúscula, dígitos y guiones simples.

**Motivo:** es compatible con rutas y sistemas que esperan identificadores conservadores, y aporta una forma canónica clara.

**Consecuencia:** no se preservan caracteres Unicode en la salida. Los alfabetos sin transliteración definida no producen caracteres equivalentes automáticamente.

## D-03 — Diacríticos mediante normalización Unicode

**Decisión:** se usará normalización Unicode de compatibilidad `NFKD` y eliminación de marcas combinantes como regla base para acentos latinos. La v1 añade una tabla mínima cerrada: `ß`/`ẞ`→`ss`, `æ`/`Æ`→`ae`, `œ`/`Œ`→`oe`, `ø`/`Ø`→`o`, `ð`/`Ð`→`d`, `þ`/`Þ`→`th`, `ł`/`Ł`→`l`, `đ`/`Đ`→`d` e `ı`→`i`.

**Motivo:** cubre de forma predecible los acentos y casos latinos frecuentes sin añadir una dependencia de transliteración.

**Consecuencia:** no se promete una transliteración universal. Caracteres no incluidos en la descomposición o tabla se descartan conforme a la semántica de frontera definida en [CONTRATO_V1.md](CONTRATO_V1.md); toda extensión requerirá actualizar contrato, escenarios y pruebas.

## D-04 — Símbolos y separadores como frontera de palabra

**Decisión:** los grupos de caracteres no permitidos situados entre fragmentos conservables se convertirán en un único guion.

**Motivo:** evita concatenaciones ambiguas como convertir `a/b` en `ab` y unifica espacios, guiones tipográficos, barras, subrayados y puntuación.

**Consecuencia:** los símbolos de borde se eliminan y el resultado no contiene guiones iniciales, finales ni consecutivos. Los caracteres no latinos descartados entre fragmentos ASCII siguen esta misma regla y forman una frontera.

## D-05 — Error si no queda contenido normalizable

**Decisión:** cadenas vacías, de solo espacios o que se reducen a símbolos o caracteres descartados provocan error; no se devuelve una cadena vacía.

**Motivo:** un slug vacío no es un segmento de URL utilizable y ocultaría errores de entrada.

**Consecuencia:** la CLI diferencia la salida correcta de los diagnósticos y devuelve código `1` para este error de contenido; los mensajes exactos quedan fijados en [CONTRATO_V1.md](CONTRATO_V1.md).

## D-06 — Sin resolución de colisiones

**Decisión:** la utilidad no añade sufijos ni consulta estado externo para garantizar unicidad.

**Motivo:** el generador es puro y sin persistencia; no posee el contexto necesario para determinar disponibilidad.

**Consecuencia:** quien integre el slug será responsable de detectar colisiones y aplicar su propia política de unicidad.

## D-07 — Dependencias e infraestructura mínimas

**Decisión:** la versión 1 no incorpora servicios externos, secretos ni variables de entorno. La Fase 2 establece Node.js 22 o superior, npm 10 o superior, TypeScript, `@types/node` y Prettier como herramientas locales de desarrollo.

**Motivo:** Node y npm proporcionan un entorno ampliamente disponible para una CLI TypeScript atómica; TypeScript habilita compilación y tipos, y Prettier ofrece formato determinista sin añadir un framework o linter de reglas no necesarias.

**Consecuencia:** el manifiesto y el bloqueo de dependencias quedan versionados en [package.json](../package.json) y [package-lock.json](../package-lock.json), con instrucciones en [ENTORNO_FASE_2.md](ENTORNO_FASE_2.md). No se crea archivo de variables de ejemplo ni configuración cloud.

## D-08 — Accesibilidad de terminal

**Decisión:** la ayuda y los errores se comunican mediante texto plano, canales estándar y códigos de salida; el color no porta información exclusiva.

**Motivo:** permite usar redirección, automatización y lectores de pantalla sin perder información.

**Consecuencia:** no se requieren interfaces visuales ni dependencias de presentación para cumplir el alcance.

## Revisión de decisiones

La Fase 1 cerró el contrato y los escenarios en [CONTRATO_V1.md](CONTRATO_V1.md) y [ESCENARIOS_FASE_1.md](ESCENARIOS_FASE_1.md); la Fase 2 cerró el entorno en [ENTORNO_FASE_2.md](ENTORNO_FASE_2.md); las Fases 3 y 4 implementaron respectivamente el núcleo y el adaptador CLI; la Fase 5 automatizó las validaciones y la Fase 6 documentó la entrega en [USO_LOCAL.md](USO_LOCAL.md). Cualquier cambio posterior deberá indicar qué ejemplos, pruebas, criterios de aceptación y fases del roadmap se ven afectados.
