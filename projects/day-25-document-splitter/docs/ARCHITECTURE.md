# Arquitectura técnica — Document Splitter

## Enfoque para una entrega de tres horas

El MVP será una **CLI local en Python**. Procesa un archivo cada vez, genera JSON y no usa servicios externos. Esta decisión reduce configuración, permite una demo fiable y deja una base simple para ampliar formatos o añadir API después.

### Propósito y alcance

El sistema recibe un archivo, valida que sea compatible, extrae texto, lo divide en fragmentos y guarda el resultado con metadatos. Resuelve la preparación rápida de documentos para búsqueda, RAG o análisis sin perder el orden del contenido ni el vínculo con el archivo original.

**Supuestos:**

- Soporte MVP: TXT, PDF con texto seleccionable y DOCX.
- PDF escaneado/OCR no se incluye inicialmente; se informa como error claro.
- Salida local en JSON; no hay base de datos, autenticación ni nube.
- El límite de tamaño se configura para evitar procesamientos costosos.

## Flujo de procesamiento

```text
Archivo → validación → extractor por formato → normalización
       → fragmentador → metadatos → archivo JSON de resultado
```

1. El punto de entrada recibe ruta, tamaño de fragmento y solapamiento.
2. El validador comprueba existencia, extensión permitida, tamaño y contenido.
3. El extractor obtiene texto ordenado: página por página en PDF, párrafo por párrafo en DOCX y lectura UTF-8 en TXT.
4. El normalizador elimina espacios redundantes sin reordenar texto.
5. El fragmentador corta preferiblemente por párrafos y oraciones; usa un corte seguro si una unidad supera el límite.
6. Cada fragmento conserva su índice, rangos de texto y referencia de origen.
7. El escritor produce un JSON y muestra un resumen o un error accionable por consola.

## Criterios de fragmentación y trazabilidad

| Regla | MVP |
| --- | --- |
| Tamaño | `chunk_size` en caracteres, valor recomendado: 1.000 |
| Solapamiento | `overlap` en caracteres, valor recomendado: 150; siempre menor que `chunk_size` |
| Prioridad de corte | Párrafo → oración → espacio → corte estricto |
| Orden | `index` consecutivo empezando en `0` |
| Identidad del documento | Hash SHA-256 del archivo |
| Identidad de fragmento | `<hash_documento>-<index>` |
| Metadatos | Nombre, formato, índice, rango de caracteres, página si existe y configuración usada |

Para documentos grandes, el MVP impone un tamaño máximo y procesa el texto por bloques cuando sea posible. La salida se escribe una vez finalizado el archivo. Una evolución posterior puede usar JSONL y streaming para lotes muy grandes.

## Componentes

| Componente | Responsabilidad |
| --- | --- |
| `main.py` | Punto de entrada CLI y composición de dependencias |
| `validators` | Reglas de archivo y parámetros de fragmentación |
| `extractors` | Lectura de TXT, PDF y DOCX bajo una interfaz común |
| `processors` | Normalización y coordinación del flujo |
| `chunkers` | División por estrategia y solapamiento |
| `models` | Estructuras `Document` y `Chunk` |
| `services` | Construcción de metadatos y resultado final |
| `utils` | Hash, rutas y utilidades de texto |

Un extractor nuevo (por ejemplo HTML o Markdown) solo debe implementar la misma función de extracción y registrarse en el selector de formatos. OCR, API HTTP e integraciones de IA quedan fuera del MVP y se añaden como adaptadores, sin alterar la lógica de fragmentación.

## Estructura de carpetas

```text
.
├── README.md                    # Guía de instalación, uso y alcance
├── requirements.txt             # Dependencias Python del MVP
├── .gitignore                   # Ignora temporales, entradas y resultados
├── src/
│   └── document_splitter/
│       ├── __init__.py          # Paquete Python
│       ├── main.py              # CLI: procesa un documento
│       ├── models.py            # Document, Chunk y resultado
│       ├── validators/
│       │   └── document.py      # Formato, tamaño, ruta y parámetros
│       ├── extractors/
│       │   ├── base.py          # Interfaz común de extractores
│       │   ├── txt.py           # Extracción TXT
│       │   ├── pdf.py           # Extracción PDF con PyMuPDF
│       │   ├── docx.py          # Extracción DOCX con python-docx
│       │   └── registry.py      # Selecciona extractor por extensión
│       ├── processors/
│       │   └── normalizer.py    # Limpieza conservadora de texto
│       ├── chunkers/
│       │   └── text.py          # Corte por caracteres y solapamiento
│       ├── services/
│       │   └── splitter.py      # Orquesta extracción y fragmentación
│       └── utils/
│           ├── hashing.py       # SHA-256 del documento
│           └── files.py         # Rutas y escritura segura de JSON
├── tests/
│   ├── test_validator.py        # Validaciones de entrada
│   ├── test_chunker.py          # Tamaño, orden y solapamiento
│   ├── test_extractors.py       # TXT/PDF/DOCX con fixtures
│   └── fixtures/                # Documentos pequeños de prueba
├── data/
│   ├── input/                   # Documentos locales, ignorados por Git
│   └── tmp/                     # Archivos temporales, ignorados por Git
├── output/                      # JSON generados, ignorado por Git
├── docs/
│   ├── ROADMAP.md               # Plan de desarrollo
│   └── ARCHITECTURE.md          # Este documento
└── assets/                      # Capturas o GIF de demostración
```

## Tecnologías recomendadas

- **Python 3.11+**: ejecución portable y ecosistema documental.
- **PyMuPDF**: extracción rápida de texto PDF y referencia de página.
- **python-docx**: lectura de párrafos de archivos DOCX.
- **pytest**: pruebas rápidas de fragmentación y extractores.
- **JSON estándar**: salida simple, legible e integrable sin infraestructura.

## Manejo de errores y seguridad

- Rechazar extensiones no permitidas, archivos vacíos y tamaños superiores al límite.
- Informar errores específicos para PDF cifrado, corrupto o sin texto extraíble.
- No registrar el texto completo en consola; mostrar ruta, etapa y mensaje de corrección.
- Mantener `data/input/`, `data/tmp/` y `output/` fuera del control de versiones.
- Resolver rutas antes de abrir archivos y limitar el procesamiento al directorio de trabajo configurado.

## Extensiones posteriores

1. Fragmentación por tokens para un modelo concreto.
2. HTML y Markdown mediante extractores adicionales.
3. OCR opcional para PDF escaneado.
4. Salida JSONL y procesamiento de directorios para corpus grandes.
5. API FastAPI o integración con un índice vectorial, manteniendo el modo local como fallback.
