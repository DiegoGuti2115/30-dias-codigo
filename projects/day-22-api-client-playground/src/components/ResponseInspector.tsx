import type { ApiExecutionResult } from '../lib/types'

type ResponseInspectorProps = {
  result: ApiExecutionResult | null
}

export function ResponseInspector({ result }: ResponseInspectorProps) {
  if (!result) {
    return <section aria-labelledby="response-title" className="response-inspector"><h2 id="response-title">Respuesta</h2><p>Aún no hay una respuesta que inspeccionar.</p></section>
  }

  if (result.kind !== 'response') {
    return (
      <section aria-labelledby="response-title" className="response-inspector" role="alert">
        <h2 id="response-title">Respuesta</h2>
        <p>{result.message}</p>
      </section>
    )
  }

  const { response } = result
  return (
    <section aria-labelledby="response-title" className="response-inspector">
      <div className="response-heading">
        <h2 id="response-title">Respuesta</h2>
        <span className={result.isHttpError ? 'status-code status-code-error' : 'status-code'}>{response.status} {response.statusText}</span>
      </div>
      <dl className="response-meta">
        <div><dt>Duración</dt><dd>{Math.round(response.durationMs)} ms</dd></div>
        <div><dt>Tipo</dt><dd>{response.contentType ?? 'No especificado'}</dd></div>
        <div><dt>Cuerpo</dt><dd>{response.bodyKind}</dd></div>
      </dl>
      <h3>Cabeceras</h3>
      {response.headers.length === 0 ? <p>La respuesta no contiene cabeceras accesibles.</p> : (
        <dl className="headers-list">
          {response.headers.map((header) => <div key={header.key}><dt>{header.key}</dt><dd>{header.value}</dd></div>)}
        </dl>
      )}
      <h3>Cuerpo</h3>
      <pre aria-label="Cuerpo de la respuesta" className="response-body">{response.body || 'Sin cuerpo'}</pre>
    </section>
  )
}
