"""Standard-library web interface for the local JSON and CSV converter."""

from __future__ import annotations

import argparse
import base64
import json
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from converters import (
    load_csv_records,
    load_json_records,
    write_csv_to_json,
    write_json_to_csv,
)
from validators import ConversionError

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
FIXTURES_DIRECTORY = PROJECT_DIRECTORY / "data" / "fixtures"
MAX_UPLOAD_BYTES = 2_000_000


PAGE = r'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Conversor local y privado de JSON a CSV y de CSV a JSON.">
  <title>Convertidor JSON ↔ CSV</title>
  <style>
    :root { --ink:#172033; --muted:#697386; --line:#dbe2ea; --surface:#fff; --canvas:#f6f8fb; --accent:#5b4bdb; --accent-dark:#4338a9; --success:#057a55; --danger:#c81e1e; --warning:#9a6700; --shadow:0 18px 50px rgba(23,32,51,.09); }
    * { box-sizing:border-box; } body { margin:0; background:var(--canvas); color:var(--ink); font:16px/1.5 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    button,input { font:inherit; } button { cursor:pointer; } button:focus-visible,input:focus-visible { outline:3px solid rgba(91,75,219,.35); outline-offset:3px; }
    .shell { width:min(1160px, calc(100% - 32px)); margin:auto; } header { padding:32px 0 20px; display:flex; justify-content:space-between; gap:24px; align-items:center; } .brand { display:flex; gap:12px; align-items:center; font-weight:800; letter-spacing:-.02em; } .mark { width:38px; height:38px; display:grid; place-items:center; background:var(--accent); color:white; border-radius:11px; font-weight:900; } .local { color:var(--success); font-size:.9rem; font-weight:650; }
    .hero { padding:40px 0 34px; display:grid; grid-template-columns:1.4fr .8fr; gap:32px; align-items:end; } h1 { max-width:750px; margin:0; font-size:clamp(2.25rem, 6vw, 4.8rem); line-height:1.02; letter-spacing:-.065em; } .lead { max-width:650px; color:var(--muted); font-size:1.12rem; margin:20px 0 0; } .hero-note { border-left:3px solid var(--accent); padding:8px 0 8px 17px; color:var(--muted); font-size:.94rem; }
    .card { background:var(--surface); border:1px solid var(--line); border-radius:20px; box-shadow:var(--shadow); } .workspace { padding:clamp(20px,4vw,38px); }
    .step-label { display:block; color:var(--muted); font-size:.78rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; margin-bottom:10px; } .choices { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; } .choice { text-align:left; border:1px solid var(--line); border-radius:13px; background:white; padding:16px; color:var(--ink); } .choice strong,.choice span { display:block; } .choice span { color:var(--muted); font-size:.86rem; margin-top:3px; } .choice[aria-pressed="true"] { background:#f0efff; border-color:var(--accent); box-shadow:inset 0 0 0 1px var(--accent); }
    .section { margin-top:28px; } .upload { border:1.5px dashed #aab7c7; border-radius:16px; background:#fbfcfe; min-height:160px; padding:25px; display:grid; place-items:center; text-align:center; transition:.2s; } .upload.drag { border-color:var(--accent); background:#f0efff; } .upload p { margin:4px 0; } .upload small { color:var(--muted); } .file-button { color:var(--accent-dark); text-decoration:underline; font-weight:750; } #file { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
    .examples { display:flex; gap:10px; flex-wrap:wrap; } .example { border:1px solid var(--line); border-radius:999px; padding:8px 12px; background:#fff; color:var(--ink); font-size:.88rem; } .example:hover { border-color:var(--accent); color:var(--accent-dark); }
    .file-info { display:none; align-items:center; gap:10px; margin-top:12px; color:var(--muted); font-size:.9rem; } .file-info.show { display:flex; } .file-info button { border:0; background:transparent; color:var(--accent-dark); text-decoration:underline; padding:0; }
    .convert { border:0; border-radius:13px; background:var(--accent); color:white; width:100%; margin-top:28px; padding:15px 18px; font-weight:800; transition:.2s; } .convert:hover:not(:disabled) { background:var(--accent-dark); transform:translateY(-1px); } .convert:disabled { opacity:.55; cursor:not-allowed; }
    .status { display:none; margin:22px 0 0; border-radius:12px; padding:13px 15px; } .status.show { display:block; } .status.loading { background:#eef2ff; color:#3730a3; } .status.success { background:#ecfdf3; color:var(--success); } .status.error { background:#fff1f2; color:var(--danger); }
    .result { display:none; margin-top:28px; } .result.show { display:block; } .result-head { display:flex; justify-content:space-between; gap:16px; align-items:center; margin-bottom:12px; } .result h2 { font-size:1.1rem; margin:0; } .download { text-decoration:none; background:#14213d; color:#fff; padding:10px 13px; border-radius:10px; font-size:.9rem; font-weight:750; } pre { margin:0; max-height:350px; overflow:auto; padding:18px; border-radius:13px; background:#111827; color:#e5edf8; font:13px/1.55 ui-monospace, SFMono-Regular, Consolas, monospace; white-space:pre-wrap; word-break:break-word; }
    .flow { padding:54px 0; } .flow h2,.rules h2 { letter-spacing:-.035em; } .flow-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; } .flow-item { padding:20px; border:1px solid var(--line); background:white; border-radius:15px; } .flow-number { color:var(--accent); font-size:.84rem; font-weight:850; } .flow-item h3 { margin:8px 0 5px; font-size:1rem; } .flow-item p { margin:0; color:var(--muted); font-size:.9rem; }
    .rules { padding:30px; margin-bottom:40px; } .rules p,.rules li { color:var(--muted); } .rules ul { padding-left:20px; } footer { padding:0 0 30px; text-align:center; color:var(--muted); font-size:.86rem; }
    @media (max-width:700px) { header { padding-top:20px; } .local { display:none; } .hero { grid-template-columns:1fr; padding-top:22px; } .choices,.flow-grid { grid-template-columns:1fr; } .workspace { padding:21px; } .result-head { align-items:flex-start; flex-direction:column; } }
  </style>
</head>
<body>
  <div class="shell">
    <header><div class="brand"><span class="mark">↔</span><span>Convertidor JSON · CSV</span></div><span class="local">● Procesamiento local</span></header>
    <main>
      <section class="hero"><div><h1>Convierte datos sin perder el control.</h1><p class="lead">Transforma JSON y CSV desde tu navegador. La validación y la conversión se ejecutan con el mismo núcleo fiable de la herramienta de línea de comandos.</p></div><p class="hero-note">Los archivos se procesan temporalmente en tu equipo y no se envían a servicios externos.</p></section>
      <section class="card workspace" aria-labelledby="converter-title"><h2 id="converter-title" class="sr-only" style="position:absolute;left:-10000px">Área de conversión</h2>
        <div><span class="step-label">1 · Dirección</span><div class="choices"><button class="choice" type="button" data-direction="json-to-csv" aria-pressed="true"><strong>JSON a CSV</strong><span>Objetos planos a columnas</span></button><button class="choice" type="button" data-direction="csv-to-json" aria-pressed="false"><strong>CSV a JSON</strong><span>Filas de texto a objetos</span></button></div></div>
        <div class="section"><span class="step-label">2 · Archivo</span><div id="dropzone" class="upload"><div><p><strong>Arrastra tu archivo aquí</strong> o <label class="file-button" for="file">selecciónalo desde tu equipo</label>.</p><small id="file-hint">Acepta archivos .json</small></div><input id="file" type="file" accept=".json,application/json" aria-describedby="file-hint"></div><div id="file-info" class="file-info"><span id="file-name"></span><button id="clear-file" type="button">Quitar archivo</button></div></div>
        <div class="section"><span class="step-label">O prueba un ejemplo</span><div class="examples"><button class="example" type="button" data-example="people.json" data-direction="json-to-csv">people.json → CSV</button><button class="example" type="button" data-example="catalog.csv" data-direction="csv-to-json">catalog.csv → JSON</button></div></div>
        <button id="convert" class="convert" type="button" disabled>Convertir a CSV</button><div id="status" class="status" role="status" aria-live="polite"></div>
        <section id="result" class="result" aria-labelledby="result-title"><div class="result-head"><h2 id="result-title">Vista previa del resultado</h2><a id="download" class="download" href="#" download>Descargar archivo</a></div><pre id="preview" tabindex="0"></pre></section>
      </section>
      <section class="flow" aria-labelledby="flow-title"><h2 id="flow-title">Un flujo claro, cuatro pasos.</h2><div class="flow-grid"><article class="flow-item"><span class="flow-number">01</span><h3>Entrada</h3><p>Elige la dirección y carga un archivo.</p></article><article class="flow-item"><span class="flow-number">02</span><h3>Validación</h3><p>Comprobamos formato, cabeceras y estructura.</p></article><article class="flow-item"><span class="flow-number">03</span><h3>Transformación</h3><p>Aplicamos las reglas del conversor CLI.</p></article><article class="flow-item"><span class="flow-number">04</span><h3>Salida</h3><p>Revisa el resultado y descárgalo.</p></article></div></section>
      <section class="card rules"><h2>Reglas reales de esta versión</h2><ul><li>JSON debe ser una lista no vacía de objetos planos; no se admiten listas ni objetos anidados.</li><li>CSV necesita cabeceras no vacías y sin duplicados; cada campo se conserva como texto al generar JSON.</li><li>Las claves ausentes en JSON se escriben como celdas vacías en CSV. Se admite UTF-8 y archivos de hasta 2 MB.</li></ul></section>
    </main><footer>JSON ↔ CSV · Sin dependencias externas · Python estándar</footer>
  </div>
<script>
(() => {
  const state = { direction: 'json-to-csv', file: null, example: null };
  const input = document.querySelector('#file'), dropzone = document.querySelector('#dropzone'), info = document.querySelector('#file-info'), fileName = document.querySelector('#file-name'), convert = document.querySelector('#convert'), status = document.querySelector('#status'), result = document.querySelector('#result'), preview = document.querySelector('#preview'), download = document.querySelector('#download');
  function directionLabel() { return state.direction === 'json-to-csv' ? 'CSV' : 'JSON'; }
  function updateUi() { document.querySelectorAll('[data-direction]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.direction === state.direction))); input.accept = state.direction === 'json-to-csv' ? '.json,application/json' : '.csv,text/csv'; document.querySelector('#file-hint').textContent = 'Acepta archivos .' + (state.direction === 'json-to-csv' ? 'json' : 'csv'); convert.textContent = 'Convertir a ' + directionLabel(); convert.disabled = !state.file && !state.example; }
  function showStatus(message, type) { status.textContent = message; status.className = 'status show ' + type; }
  function setFile(file, example) { state.file = file || null; state.example = example || null; if (file || example) { fileName.textContent = example || (file.name + ' · ' + Math.ceil(file.size / 1024) + ' KB'); info.classList.add('show'); } else { input.value = ''; info.classList.remove('show'); } result.classList.remove('show'); updateUi(); }
  document.querySelectorAll('.choice').forEach(button => button.addEventListener('click', () => { state.direction = button.dataset.direction; setFile(null, null); updateUi(); }));
  document.querySelectorAll('.example').forEach(button => button.addEventListener('click', () => { state.direction = button.dataset.direction; setFile(null, button.dataset.example); updateUi(); }));
  input.addEventListener('change', () => setFile(input.files[0], null)); document.querySelector('#clear-file').addEventListener('click', () => setFile(null, null));
  ['dragenter','dragover'].forEach(event => dropzone.addEventListener(event, event => { event.preventDefault(); dropzone.classList.add('drag'); })); ['dragleave','drop'].forEach(event => dropzone.addEventListener(event, event => { event.preventDefault(); dropzone.classList.remove('drag'); })); dropzone.addEventListener('drop', event => { const file = event.dataTransfer.files[0]; if (file) setFile(file, null); });
  convert.addEventListener('click', async () => { convert.disabled = true; result.classList.remove('show'); showStatus('Validando y transformando el archivo…', 'loading'); try { let name, content; if (state.example) { const response = await fetch('/api/example/' + encodeURIComponent(state.example)); if (!response.ok) throw new Error('No se pudo cargar el ejemplo.'); const example = await response.json(); name = example.name; content = example.content; } else { name = state.file.name; content = await state.file.text(); } const response = await fetch('/api/convert', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({direction:state.direction, filename:name, content}) }); const payload = await response.json(); if (!response.ok) throw new Error(payload.error || 'No se pudo convertir el archivo.'); preview.textContent = payload.preview; download.href = payload.download_url; download.download = payload.output_name; download.textContent = 'Descargar ' + payload.output_name; showStatus('Conversión completada: ' + payload.count + ' registro(s) procesado(s).', 'success'); result.classList.add('show'); } catch (error) { showStatus(error.message, 'error'); } finally { convert.disabled = !state.file && !state.example; } }); updateUi();
})();
</script>
</body></html>'''


class ConverterWebHandler(BaseHTTPRequestHandler):
    """Serve the UI plus a small JSON API backed by the CLI conversion services."""

    server_version = "JsonCsvConverter/1.0"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path == "/" or self.path == "/index.html":
            self._send_bytes(PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path.startswith("/api/example/"):
            self._serve_example()
            return
        self._send_error(HTTPStatus.NOT_FOUND, "Ruta no encontrada.")

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/api/convert":
            self._send_error(HTTPStatus.NOT_FOUND, "Ruta no encontrada.")
            return
        try:
            request = self._read_json_body()
            response = convert_request(request)
        except ConversionError as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        except (TypeError, ValueError, KeyError) as error:
            self._send_json({"error": f"Solicitud no válida: {error}"}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(response)

    def log_message(self, format: str, *args: Any) -> None:
        """Keep local server output concise and avoid logging request bodies."""
        print(f"[web] {self.address_string()} - {format % args}")

    def _read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            raise ConversionError("La solicitud no contiene un archivo.")
        if content_length > MAX_UPLOAD_BYTES * 2:
            raise ConversionError("La solicitud supera el límite de 2 MB.")
        try:
            data = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ConversionError("La solicitud debe contener JSON UTF-8 válido.") from error
        if not isinstance(data, dict):
            raise ConversionError("La solicitud debe ser un objeto JSON.")
        return data

    def _serve_example(self) -> None:
        name = self.path.removeprefix("/api/example/")
        if name not in {"people.json", "catalog.csv"}:
            self._send_error(HTTPStatus.NOT_FOUND, "Ejemplo no encontrado.")
            return
        try:
            content = (FIXTURES_DIRECTORY / name).read_text(encoding="utf-8")
        except OSError:
            self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "No se pudo cargar el ejemplo.")
            return
        self._send_json({"name": name, "content": content})

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def _send_error(self, status: HTTPStatus, message: str) -> None:
        self._send_json({"error": message}, status)

    def _send_bytes(self, content: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)


def convert_request(request: dict[str, Any]) -> dict[str, Any]:
    """Convert request content through the existing file-based conversion services."""
    direction = request.get("direction")
    filename = request.get("filename")
    content = request.get("content")
    expected_suffix = ".json" if direction == "json-to-csv" else ".csv"
    if direction not in {"json-to-csv", "csv-to-json"}:
        raise ConversionError("Selecciona una dirección de conversión válida.")
    if not isinstance(filename, str) or Path(filename).suffix.lower() != expected_suffix:
        raise ConversionError(f"El archivo debe tener la extensión {expected_suffix}.")
    if not isinstance(content, str) or not content.strip():
        raise ConversionError("El archivo está vacío.")
    if len(content.encode("utf-8")) > MAX_UPLOAD_BYTES:
        raise ConversionError("El archivo supera el límite de 2 MB.")

    output_suffix = ".csv" if direction == "json-to-csv" else ".json"
    with tempfile.TemporaryDirectory(prefix="json-csv-web-") as directory:
        input_path = Path(directory) / f"input{expected_suffix}"
        output_path = Path(directory) / f"output{output_suffix}"
        input_path.write_text(content, encoding="utf-8", newline="")
        if direction == "json-to-csv":
            records = load_json_records(input_path)
            count = write_json_to_csv(records, output_path)
        else:
            _, records = load_csv_records(input_path)
            count = write_csv_to_json(records, output_path)
        output_bytes = output_path.read_bytes()

    output_name = f"{Path(filename).stem}{output_suffix}"
    media_type = "text/csv" if output_suffix == ".csv" else "application/json"
    return {
        "count": count,
        "output_name": output_name,
        "preview": output_bytes.decode("utf-8"),
        "download_url": f"data:{media_type};base64,{base64.b64encode(output_bytes).decode('ascii')}",
    }


def build_parser() -> argparse.ArgumentParser:
    """Build command-line arguments for the local development server."""
    parser = argparse.ArgumentParser(description="Inicia la interfaz web del convertidor JSON y CSV.")
    parser.add_argument("--host", default="127.0.0.1", help="Host local donde escuchar.")
    parser.add_argument("--port", default=8000, type=int, help="Puerto HTTP local.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Start the local web server until interrupted."""
    arguments = build_parser().parse_args(argv)
    server = ThreadingHTTPServer((arguments.host, arguments.port), ConverterWebHandler)
    print(f"Interfaz web disponible en http://{arguments.host}:{arguments.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
