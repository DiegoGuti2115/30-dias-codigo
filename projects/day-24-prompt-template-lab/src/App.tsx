import { useState, useEffect } from 'react';
import { PromptEditor } from './components/PromptEditor';
import { VariablesForm } from './components/VariablesForm';
import { OutputPanel } from './components/OutputPanel';
import { extractTemplateVariables } from './schemas/promptSchema';
import { renderPrompt } from './services/promptRenderer';
import { generateText } from './services/llmProvider';
import fallbackDataRaw from '../data/fallback_responses.json';

const fallbackData = fallbackDataRaw as Record<string, string>;

export default function App() {
    const [template, setTemplate] = useState<string>(
        'Actúa como un {{rol}} y resume el siguiente texto de forma concisa:\n\n{{documento}}'
    );
    const [variables, setVariables] = useState<string[]>([]);
    const [payload, setPayload] = useState<Record<string, string>>({});
    const [isMockMode, setIsMockMode] = useState<boolean>(true);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [output, setOutput] = useState<string>('');
    const [validationErrors, setValidationErrors] = useState<string[]>([]);
    const [networkError, setNetworkError] = useState<string>('');

    useEffect(() => {
        const extracted = extractTemplateVariables(template);
        setVariables(extracted);
        setPayload(prev => {
            const next = { ...prev };
            Object.keys(next).forEach(key => {
                if (!extracted.includes(key)) delete next[key];
            });
            return next;
        });
    }, [template]);

    const handleExecute = async () => {
        setValidationErrors([]);
        setNetworkError('');
        setOutput('');

        const renderResult = renderPrompt(template, payload);
        if (!renderResult.success || !renderResult.renderedPrompt) {
            setValidationErrors(renderResult.errors || ['Error en contrato de validación.']);
            return;
        }

        setIsLoading(true);
        try {
            if (isMockMode) {
                await new Promise(r => setTimeout(r, 850));
                setOutput(fallbackData.default || 'Respuesta mock inyectada exitosamente.');
            } else {
                const response = await generateText(renderResult.renderedPrompt);
                setOutput(response.text);
                if (response.isFallback && response.errorDetails) {
                    setNetworkError(`Fallback activado: ${response.errorDetails}`);
                }
            }
        } catch (err: any) {
            setNetworkError(err.message || 'Error crítico en el orquestador LLM.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="app">
            <header className="header">
                <div className="logo">
                    <div className="logo-icon">{'{/}'}</div>
                    <span className="logo-name">Prompt Template Lab</span>
                    <span className="logo-ver">v1.0</span>
                </div>

                <div className="mode-toggle">
                    <button
                        className={`mode-btn ${isMockMode ? 'mock-active' : ''}`}
                        onClick={() => setIsMockMode(true)}
                    >
                        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <circle cx="8" cy="8" r="5.5"/><path d="M8 5v3l2 1.5"/>
                        </svg>
                        Mock
                    </button>
                    <button
                        className={`mode-btn ${!isMockMode ? 'api-active' : ''}`}
                        onClick={() => setIsMockMode(false)}
                    >
                        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path d="M2 8h3m6 0h3M8 2v3m0 6v3"/><circle cx="8" cy="8" r="2.5"/>
                        </svg>
                        API Local
                    </button>
                </div>
            </header>

            <main className="workspace">
                <div className="editor-col">
                    <PromptEditor
                        template={template}
                        onChange={setTemplate}
                        varCount={variables.length}
                    />
                </div>

                <div className="right-col">
                    <VariablesForm
                        variables={variables}
                        payload={payload}
                        onChange={(k, v) => setPayload(prev => ({ ...prev, [k]: v }))}
                        errors={validationErrors}
                        isLoading={isLoading}
                        onExecute={handleExecute}
                    />
                    <OutputPanel
                        output={output}
                        networkError={networkError}
                        isLoading={isLoading}
                    />
                </div>
            </main>
        </div>
    );
}