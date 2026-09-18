import { FieldEditor } from './components/FieldEditor'
import { FormPreview } from './components/FormPreview'
import { useFormBuilder } from './hooks/useFormBuilder'
import { downloadFormDefinition } from './utils/exportForm'
import { FIELD_TYPES, type FieldType } from './utils/types'

const typeLabels: Record<FieldType, string> = {
  text: 'Texto',
  email: 'Email',
  number: 'Número',
  textarea: 'Área de texto',
  select: 'Selección',
  checkbox: 'Checkbox',
}

export const App = () => {
  const builder = useFormBuilder()

  return (
    <main className="app-shell">
      <header className="site-header">
        <a className="brand" href="/" aria-label="Constructor de formularios, inicio"><span className="brand__mark">20</span><span>Constructor<br /><strong>de formularios</strong></span></a>
        <div className="header-meta"><button type="button" className="export-button" onClick={() => downloadFormDefinition(builder.form)}>Exportar JSON <span>↗</span></button><span className={`status-chip ${builder.persistence === 'memory' ? 'status-chip--memory' : ''}`}><i /> {builder.persistence === 'memory' ? 'Modo memoria' : 'Guardado local'}</span><span className="version-label">MVP / Fase 05</span></div>
      </header>

      <div className="page-intro">
        <div><span className="eyebrow">Estudio de formularios · 2026</span><h1>Diseña una experiencia<br /><em>que pida lo justo.</em></h1></div>
        <p className="intro-copy">Construye el formulario campo a campo. La vista previa se actualiza mientras trabajas para que cada decisión tenga contexto.</p>
      </div>

      <div className="workspace">
        <section className="builder-panel" aria-labelledby="builder-title">
          <div className="panel-heading"><div><span className="eyebrow">01 / Configuración</span><h2 id="builder-title">{builder.form.title}</h2></div><span className="field-count">{builder.form.fields.length} campos</span></div>
          <div className="form-meta">
            <label>Nombre del formulario<input value={builder.form.title} onChange={() => undefined} readOnly /></label>
            <label>Descripción<textarea value={builder.form.description} onChange={() => undefined} readOnly rows={2} /></label>
          </div>
          {builder.error && <div className="error-banner" role="alert"><span>!</span>{builder.error}<button type="button" onClick={builder.clearError} aria-label="Cerrar mensaje">×</button></div>}
          <div className="fields-heading"><span>Campos del formulario</span><span className="line" /></div>
          <div className="field-list">
            {builder.form.fields.map((field, index) => <FieldEditor key={field.id} field={field} index={index} total={builder.form.fields.length} onUpdate={(patch) => builder.update(field.id, patch)} onMove={(direction) => builder.move(field.id, direction)} onRemove={() => builder.remove(field.id)} />)}
          </div>
          <div className="add-field-row"><span>Añadir un campo</span><div className="add-field-controls">{FIELD_TYPES.map((type) => <button type="button" key={type} onClick={() => builder.add(type)}><span>+</span>{typeLabels[type]}</button>)}</div></div>
        </section>
        <FormPreview form={builder.form} />
      </div>

      <footer className="site-footer"><span>Sin backend. Diseñado para iterar rápido.</span><span>30 DÍAS / 30 PROYECTOS <b>·</b> DÍA 20</span></footer>
    </main>
  )
}