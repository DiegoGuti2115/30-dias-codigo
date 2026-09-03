# Guía reproducible y demostración segura

## Requisitos y preparación

- Python 3.11 o superior.
- Una copia local del repositorio.
- Un terminal que permita solicitar texto sin eco mediante la biblioteca estándar.
- Ninguna dependencia, red, credencial, archivo de configuración ni variable de entorno.

Desde `projects/day-06-password-policy-checker`, la única ejecución interactiva admitida es:

```text
python src/main.py check
```

La aplicación solicitará una única entrada sin eco. No se debe proporcionar una contraseña mediante argumentos, tuberías, archivos, variables de entorno, capturas de pantalla ni grabaciones. Si el terminal no admite la lectura sin eco, finaliza con un diagnóstico seguro; usa un terminal local compatible en lugar de buscar una alternativa de entrada visible.

## Qué comprueba la política v1

La política fija exige, en este orden, una longitud de 12 a 128 caracteres Unicode, al menos una mayúscula Unicode, una minúscula Unicode, un dígito decimal Unicode y un carácter especial permitido. Cualquier espacio Unicode invalida además la evaluación. Las definiciones completas, incluido el tratamiento de combinantes, están en [`../docs/CONTRATO.md`](../docs/CONTRATO.md).

La política solo comprueba conformidad con estos requisitos. No estima fortaleza, entropía, reutilización, patrones, filtraciones ni seguridad frente a ataques.

## Demostración sin secretos

La demostración se basa en escenarios declarativos, no en valores de entrada. El catálogo [`../data/fixtures/scenario-catalog.json`](../data/fixtures/scenario-catalog.json) describe únicamente categorías, longitudes y presencia de espacios. Las referencias [`../data/expected/scenario-results.json`](../data/expected/scenario-results.json) fijan resultados booleanos y orden de reglas.

| Escenario sintético | Condición descrita | Resultado de referencia |
|---|---|---|
| `all-rules-satisfied` | Longitud admisible y todas las categorías requeridas. | Válido. |
| `combined-failures` | Varias categorías o condiciones incumplidas. | No válido; los diagnósticos siguen el orden contractual. |
| `minimum-length` / `maximum-length` | Límite inferior o superior incluido. | La regla de longitud se satisface. |
| `above-maximum-length` | Longitud superior al máximo. | No válido por longitud. |
| `unicode-categories` | Categorías Unicode admitidas por el contrato. | Se evalúan con las clasificaciones Unicode de Python. |
| `combining-marks-only` | Solo marcas combinantes. | No satisfacen por sí mismas categorías principales. |
| `whitespace-present` | Al menos un espacio Unicode. | No válido e informa el diagnóstico de espacio al final. |

Para reproducir la demostración y toda la regresión sin introducir ninguna contraseña, ejecuta:

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

La suite genera candidatos efímeros solo en memoria y verifica cada escenario frente a las referencias. La prueba [`../tests/test_quality_regression.py`](../tests/test_quality_regression.py) también comprueba la coherencia catálogo-referencias, el formato contractual de cada resultado y la ausencia de patrones de asignación de secretos en los recursos versionados.

## Interpretación segura de la salida

En una comprobación interactiva finalizada, la salida estándar contiene primero el estado global. Si la evaluación no cumple la política, continúan únicamente los requisitos incumplidos en orden fijo: longitud, mayúscula, minúscula, dígito decimal, carácter especial y, por último, espacio en blanco. No se muestra la entrada, su longitud, caracteres, posiciones, fragmentos ni derivados.

| Situación | Canal | Código |
|---|---|:---:|
| Política satisfecha | Salida estándar. | `0` |
| Política evaluada pero incumplida | Salida estándar. | `1` |
| Uso inválido | Salida de error, sin leer entrada. | `2` |
| Cancelación o terminal no seguro | Salida de error, sin evaluar entrada. | `1` |
| Error interno controlado | Salida de error, sin traza. | `1` |

Los textos completos de uso, errores y límites están documentados en [`../docs/USO_SEGURO.md`](../docs/USO_SEGURO.md).

## Verificación final local

Ejecuta estas comprobaciones desde la raíz del repositorio:

```text
python -m unittest discover -s projects/day-06-password-policy-checker/tests -p "test_*.py" -v
python -m compileall -q projects/day-06-password-policy-checker/src
git diff --check
git status --short
```

El segundo comando puede crear directorios de caché de Python; elimínalos antes de revisar el estado final. La verificación no requiere conectividad ni servicios externos.
