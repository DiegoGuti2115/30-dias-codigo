# Ejemplos reproducibles

Todos los comandos de este documento se ejecutan desde la raíz de [`day-04-log-analyzer`](..). No requieren instalación de paquetes, red, credenciales ni archivos externos: usan exclusivamente los fixtures sintéticos incluidos en el repositorio.

## Resumen `common`

```text
python src/main.py analyze data/fixtures/common-valid.log --format common
```

Resultado esperado:

- código de salida `0`;
- siete eventos válidos y cero líneas inválidas;
- conteos `DEBUG: 1`, `INFO: 2`, `WARNING: 1`, `ERROR: 2` y `CRITICAL: 1`;
- los tres mensajes frecuentes en orden determinista.

## Resumen y reporte de errores `jsonl`

```text
python src/main.py analyze data/fixtures/jsonl-valid.jsonl --format jsonl --errors
```

Resultado esperado:

- código de salida `0`;
- resumen de seis eventos válidos;
- reporte con los eventos `ERROR` y `CRITICAL` en el orden físico del fixture;
- ningún metadato JSON Lines adicional en la salida.

## Líneas inválidas toleradas

```text
python src/main.py analyze data/fixtures/common-invalid.log --format common --errors
```

Resultado esperado: código `0`, dos eventos válidos, cuatro líneas inválidas y un reporte que indica que no existen eventos `ERROR` o `CRITICAL`. El detalle de las líneas rechazadas no se imprime.

## Error de análisis reproducible

```text
python src/main.py analyze data/fixtures/empty.log --format common
```

Resultado esperado: código `1`, salida estándar vacía y el mensaje `Error de análisis: el archivo no contiene eventos válidos.` en la salida de error.

## Comprobación de la copia local

```text
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Ambos comandos deben finalizar correctamente en una copia limpia del proyecto con los fixtures locales.