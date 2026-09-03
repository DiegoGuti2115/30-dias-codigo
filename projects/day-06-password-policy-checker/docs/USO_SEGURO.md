# Uso seguro de la CLI v1

## Ejecución

Desde el directorio del proyecto, ejecuta únicamente:

```text
python src/main.py check
```

La aplicación solicita una única contraseña mediante el mecanismo sin eco de la biblioteca estándar. La entrada no se acepta mediante argumentos, variables de entorno, archivos, tuberías, entrada estándar ni opciones de configuración.

El único subcomando de la v1 es `check`. Un subcomando ausente, desconocido o acompañado de argumentos adicionales no solicita ninguna entrada; escribe lo siguiente en la salida de error y termina con código `2`:

```text
Uso: python src/main.py check
```

No hay opciones adicionales, modo de demostración ni formato alternativo en esta versión.

## Salida y códigos de retorno

Una evaluación terminada escribe únicamente en la salida estándar mensajes estáticos del contrato, en este orden:

1. Estado global.
2. Mensajes de las reglas principales incumplidas en el orden `length`, `uppercase`, `lowercase`, `digit`, `special`.
3. El mensaje de espacio en blanco, si procede.

Los códigos de retorno son:

| Situación | Salida | Código |
|---|---|:---:|
| Política satisfecha | Estado global válido. | `0` |
| Política evaluada e incumplida | Estado global no válido y requisitos incumplidos. | `1` |
| Uso no permitido | Mensaje de uso en stderr, sin solicitar entrada. | `2` |
| Cancelación, EOF, aviso de lectura sin eco o fallo del terminal | Error breve de interacción segura en stderr. | `1` |
| Error interno controlable | Error breve y genérico en stderr. | `1` |

## Límites de seguridad

- La CLI no imprime la entrada, su longitud, caracteres detectados, posiciones, fragmentos, hash ni representaciones derivadas.
- La salida no declara qué categorías se detectaron: solo comunica requisitos incumplidos permitidos por [`CONTRATO.md`](CONTRATO.md).
- Si el entorno no permite una lectura sin eco, la ejecución se cancela. No existe una alternativa visible ni basada en `stdin`.
- La aplicación no crea ni lee archivos de datos durante una comprobación, no registra eventos y no realiza conexiones de red.
- Python no garantiza el borrado físico de memoria; la implementación limita la referencia de la entrada al ciclo de evaluación.

## Verificación local

La suite se ejecuta sin red ni dependencias externas:

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

Las pruebas construyen valores efímeros únicamente en memoria. Los catálogos y referencias versionados contienen condiciones y estados abstractos, no entradas evaluables. La prueba de regresión [`../tests/test_quality_regression.py`](../tests/test_quality_regression.py) comprueba además la coherencia entre catálogo, referencias y presentación contractual.

## Demostración reproducible sin secretos

La guía [`../examples/USO.md`](../examples/USO.md) describe los requisitos locales, escenarios sintéticos, interpretación de resultados y los comandos de cierre. No publica ni requiere una contraseña de ejemplo: la demostración se reproduce exclusivamente mediante las referencias y la suite de pruebas.
