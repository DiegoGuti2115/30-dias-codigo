'use client'

import { useRequestComposer } from '../hooks/useRequestComposer'
import { BODY_FORMATS, HTTP_METHODS, type KeyValuePair } from '../lib/types'
import { RequestHistory } from './RequestHistory'
import { ResponseInspector } from './ResponseInspector'

type PairSectionProps = {
  title: string
  section: 'query' | 'headers'
  pairs: KeyValuePair[]
  errors: Record<string, string>
  onAdd: (section: 'query' | 'headers') => void
  onRemove: (section: 'query' | 'headers', index: number) => void
  onUpdate: (section: 'query' | 'headers', index: number, patch: Partial<KeyValuePair>) => void
}

function PairSection({ title, section, pairs, errors, onAdd, onRemove, onUpdate }: PairSectionProps) {
  return (
    <fieldset className="editor-section">
      <legend>{title}</legend>
      {pairs.map((pair, index) => {
        const error = errors[`${section}.${index}.key`]
        return (
          <div className="pair-row" key={`${section}-${index}`}>
            <label className="checkbox-label">
              <input
                aria-label={`Activar ${title.toLowerCase()} ${index + 1}`}
                checked={pair.enabled}
                onChange={(event) => onUpdate(section, index, { enabled: event.target.checked })}
                type="checkbox"
              />
              <span className="sr-only">Activar</span>
            </label>
            <label className="sr-only" htmlFor={`${section}-key-${index}`}>Nombre</label>
            <input
              aria-describedby={error ? `${section}-error-${index}` : undefined}
              aria-invalid={Boolean(error)}
              id={`${section}-key-${index}`}
              onChange={(event) => onUpdate(section, index, { key: event.target.value })}
              placeholder="Nombre"
              type="text"
              value={pair.key}
            />
            <label className="sr-only" htmlFor={`${section}-value-${index}`}>Valor</label>
            <input
              id={`${section}-value-${index}`}
              onChange={(event) => onUpdate(section, index, { value: event.target.value })}
              placeholder="Valor"
              type="text"
              value={pair.value}
            />
            <button
              aria-label={`Eliminar ${title.toLowerCase()} ${index + 1}`}
              className="secondary-button"
              onClick={() => onRemove(section, index)}
              type="button"
            >
              Eliminar
            </button>
            {error && <p className="field-error" id={`${section}-error-${index}`}>{error}</p>}
          </div>
        )
      })}
      <button className="secondary-button" onClick={() => onAdd(section)} type="button">
        Añadir {title.toLowerCase()}
      </button>
    </fieldset>
  )
}

export function RequestEditor() {
  const composer = useRequestComposer()

  const status = composer.isSending
    ? 'Enviando solicitud…'
    : composer.result?.kind === 'response'
      ? `Respuesta ${composer.result.response.status} recibida.`
      : composer.result?.kind === 'timeout'
        ? composer.result.message
        : composer.result?.kind === 'aborted'
          ? composer.result.message
          : composer.result?.kind === 'network-error'
            ? composer.result.message
            : ''

  return (
    <form
      className="request-editor"
      onSubmit={(event) => { event.preventDefault(); void composer.send() }}
    >

      {/* ── Encabezado + línea de petición ── */}
      <div className="glass-card">
        <div className="editor-heading">
          <div>
            <p className="eyebrow">Día 22 · Cliente HTTP</p>
            <h1>Playground de <span>cliente API</span></h1>
            <p>Construye una solicitud, pruébala con los mocks locales y revisa su resultado.</p>
          </div>
          <div className="examples-loader">
            <label>
              Cargar ejemplo
              <select
                defaultValue=""
                disabled={composer.examplesLoading}
                onChange={(event) => composer.loadExample(Number(event.target.value))}
              >
                <option disabled value="">
                  {composer.examplesLoading ? 'Cargando…' : 'Selecciona una solicitud'}
                </option>
                {composer.requestExamples.map((example, index) => (
                  <option key={`${example.method}-${example.url}`} value={index}>
                    {example.method} {example.url}
                  </option>
                ))}
              </select>
            </label>
            {composer.examplesError && (
              <div className="examples-error">
                <span className="field-error">Usando ejemplos locales.</span>
                <button
                  className="secondary-button"
                  onClick={composer.reloadExamples}
                  type="button"
                >
                  Reintentar
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="request-line" style={{ marginTop: '1.25rem' }}>
          <label>
            Método
            <select
              onChange={(event) => composer.setMethod(event.target.value as (typeof HTTP_METHODS)[number])}
              value={composer.draft.method}
            >
              {HTTP_METHODS.map((method) => (
                <option key={method} value={method}>{method}</option>
              ))}
            </select>
          </label>
          <label className="url-field">
            URL
            <input
              aria-describedby={composer.errors.url ? 'url-error' : undefined}
              aria-invalid={Boolean(composer.errors.url)}
              onChange={(event) => composer.setUrl(event.target.value)}
              placeholder="https://api.example.com/resources"
              required
              type="url"
              value={composer.draft.url}
            />
            {composer.errors.url && (
              <span className="field-error" id="url-error">{composer.errors.url}</span>
            )}
          </label>
        </div>
      </div>

      {/* ── Parámetros y cabeceras ── */}
      <div className="glass-card" style={{ display: 'grid', gap: '1rem' }}>
        <PairSection
          errors={composer.errors}
          onAdd={composer.addPair}
          onRemove={composer.removePair}
          onUpdate={composer.updatePair}
          pairs={composer.draft.query}
          section="query"
          title="Parámetros"
        />
        <PairSection
          errors={composer.errors}
          onAdd={composer.addPair}
          onRemove={composer.removePair}
          onUpdate={composer.updatePair}
          pairs={composer.draft.headers}
          section="headers"
          title="Cabeceras"
        />
      </div>

      {/* ── Cuerpo ── */}
      <div className="glass-card">
        <fieldset className="editor-section">
          <legend>Cuerpo</legend>
          <label>
            Formato
            <select
              disabled={composer.draft.method === 'GET'}
              onChange={(event) => composer.setBodyFormat(event.target.value as (typeof BODY_FORMATS)[number])}
              value={composer.draft.bodyFormat}
            >
              {BODY_FORMATS.map((format) => (
                <option key={format} value={format}>
                  {format === 'none' ? 'Sin cuerpo' : 'JSON'}
                </option>
              ))}
            </select>
          </label>
          <label>
            Contenido
            <textarea
              aria-describedby={composer.errors.body ? 'body-error' : undefined}
              aria-invalid={Boolean(composer.errors.body)}
              disabled={composer.draft.bodyFormat === 'none'}
              onChange={(event) => composer.setBody(event.target.value)}
              placeholder='{ "nombre": "valor" }'
              rows={8}
              value={composer.draft.body}
            />
            {composer.errors.body && (
              <span className="field-error" id="body-error">{composer.errors.body}</span>
            )}
          </label>
        </fieldset>
      </div>

      {/* ── Acciones ── */}
      <div className="editor-actions">
        <button disabled={composer.isSending} type="submit">
          {composer.isSending ? 'Enviando…' : 'Enviar solicitud'}
        </button>
        {composer.isSending && (
          <button className="secondary-button" onClick={composer.cancel} type="button">
            Cancelar
          </button>
        )}
      </div>

      <p aria-live="polite" className="request-status" role="status">{status}</p>
      {composer.errors.form && (
        <p className="field-error" role="alert">{composer.errors.form}</p>
      )}

      <ResponseInspector result={composer.result} />
      <RequestHistory
        entries={composer.history}
        onClear={composer.clearHistory}
        onRemove={composer.removeHistoryEntry}
        onRestore={composer.restoreHistoryEntry}
      />
    </form>
  )
}