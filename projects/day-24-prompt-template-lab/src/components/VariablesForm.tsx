interface VariablesFormProps {
    variables: string[];
    payload: Record<string, string>;
    onChange: (key: string, value: string) => void;
    errors: string[];
    isLoading: boolean;
    onExecute: () => void;
}

export const VariablesForm = ({ variables, payload, onChange, errors, isLoading, onExecute }: VariablesFormProps) => (
    <div className="panel vars-panel">
        <div className="panel-header">
            <span className="panel-label">Variables</span>
            <div className="panel-meta">
                <div style={{
                    width: 6, height: 6, borderRadius: '50%', flexShrink: 0,
                    background: variables.length > 0 ? 'var(--accent)' : 'var(--text-3)',
                    boxShadow: variables.length > 0 ? '0 0 8px var(--accent-glow)' : 'none',
                    transition: 'all 0.3s'
                }} />
                <span className="chip" style={{ color: variables.length > 0 ? 'var(--accent)' : undefined }}>
                    {variables.length > 0 ? 'contrato activo' : 'sin variables'}
                </span>
            </div>
        </div>

        <div className="vars-body">
            {variables.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">{'{}'}</div>
                    <p className="empty-text">Plantilla estática.<br />Sin variables detectadas.</p>
                </div>
            ) : (
                <>
                    {errors.length > 0 && (
                        <div className="error-banner">
                            {errors.map((err, i) => (
                                <div key={i} className="error-row">
                                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                                        <circle cx="8" cy="8" r="6"/><path d="M8 5v4M8 11v.5"/>
                                    </svg>
                                    {err}
                                </div>
                            ))}
                        </div>
                    )}
                    {variables.map(v => (
                        <div key={v} className="var-field var-group">
                            <label className="var-label">{`{{${v}}}`}</label>
                            <input
                                className="var-input"
                                type="text"
                                value={payload[v] || ''}
                                onChange={e => onChange(v, e.target.value)}
                                placeholder="Asignar valor…"
                            />
                        </div>
                    ))}
                </>
            )}
        </div>

        <div className="run-zone">
            <button className="run-btn" onClick={onExecute} disabled={isLoading}>
                {isLoading ? (
                    <>
                        <div className="spinner" />
                        <span>Procesando…</span>
                    </>
                ) : (
                    <>
                        <svg viewBox="0 0 16 16" fill="currentColor">
                            <path d="M4 2.5l10 5.5-10 5.5V2.5z"/>
                        </svg>
                        <span>Compilar e inferir</span>
                    </>
                )}
            </button>
        </div>
    </div>
);