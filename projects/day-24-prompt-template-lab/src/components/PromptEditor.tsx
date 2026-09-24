interface PromptEditorProps {
    template: string;
    onChange: (value: string) => void;
    varCount: number;
}

export const PromptEditor = ({ template, onChange, varCount }: PromptEditorProps) => (
    <div className="panel editor-col" style={{ flex: '1.25' }}>
        <div className="panel-header">
            <span className="panel-label">System message</span>
            <div className="panel-meta">
                <div className="live-dot">
                    <span />
                    <span />
                </div>
                <span className={`chip ${varCount > 0 ? 'accent' : ''}`}>
                    {varCount} var{varCount !== 1 ? 's' : ''}
                </span>
            </div>
        </div>
        <textarea
            className="prompt-textarea"
            value={template}
            onChange={e => onChange(e.target.value)}
            spellCheck={false}
            placeholder="Escribe tu plantilla. Usa {{variable}} para inyectar datos dinámicos…"
        />
    </div>
);