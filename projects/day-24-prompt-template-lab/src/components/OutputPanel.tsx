interface OutputPanelProps {
    output: string;
    networkError: string;
    isLoading: boolean;
}

export const OutputPanel = ({ output, networkError, isLoading }: OutputPanelProps) => (
    <div className="panel output-panel">
        <div className="terminal-bar">
            <div className="terminal-dots">
                <div className="tdot r" />
                <div className="tdot y" />
                <div className="tdot g" />
            </div>
            <span className="terminal-title">output.log</span>
            <span className={`chip ${isLoading ? 'accent' : output ? 'success' : ''}`}>
                {isLoading ? 'running' : output ? 'done' : 'idle'}
            </span>
        </div>
        <div className="output-body">
            {networkError && (
                <div className="net-error">
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M8 2L14 13H2L8 2z"/><path d="M8 7v3M8 12v.5"/>
                    </svg>
                    <span>{networkError}</span>
                </div>
            )}
            {output
                ? <pre className="output-pre">{output}</pre>
                : <span className="output-placeholder">Waiting for LLM trace…</span>
            }
        </div>
    </div>
);