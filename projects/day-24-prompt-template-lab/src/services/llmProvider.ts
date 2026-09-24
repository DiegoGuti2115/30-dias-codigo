import fallbackDataRaw from '../../data/fallback_responses.json';

interface FallbackData {
    default: string;
    summarize: string;
    translate: string;
    code: string;
}

const fallbackData = fallbackDataRaw as FallbackData;

export interface LLMResponse {
    text: string;
    isFallback: boolean;
    errorDetails?: string;
}

/**
 * Cliente API para Ollama con patrón Circuit Breaker ajustado.
 */
export const generateText = async (prompt: string, model: string = 'phi3'): Promise<LLMResponse> => {
    const controller = new AbortController();
    
    // CORRECCIÓN: Aumentamos el umbral del Circuit Breaker a 60 segundos (60000ms).
    // Esto da margen a Ollama para el 'cold start' (cargar el modelo en memoria) 
    // y generar la inferencia completa sin interrupciones asíncronas.
    const timeoutId = setTimeout(() => controller.abort(), 60000); 

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: model,
                prompt: prompt,
                stream: false 
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId); 

        if (!response.ok) {
            throw new Error(`HTTP Status: ${response.status}`);
        }

        const data = await response.json();
        
        return {
            text: data.response,
            isFallback: false
        };

    } catch (error: any) {
        clearTimeout(timeoutId);
        
        const isTimeout = error.name === 'AbortError' || error.message.includes('aborted');
        // Actualizamos el mensaje de log para reflejar el nuevo umbral
        const errorMessage = isTimeout ? 'Timeout (60s) superado.' : error.message;
        
        console.warn("⚠️ LLM Local Inaccesible o latencia excedida. Conmutando a Fallback. Detalle:", errorMessage);
        
        let mockText = fallbackData.default;
        const lowerPrompt = prompt.toLowerCase();
        
        if (lowerPrompt.includes('resum') || lowerPrompt.includes('summar')) {
            mockText = fallbackData.summarize;
        } else if (lowerPrompt.includes('traduc') || lowerPrompt.includes('translat')) {
            mockText = fallbackData.translate;
        } else if (lowerPrompt.includes('códig') || lowerPrompt.includes('code') || lowerPrompt.includes('python')) {
            mockText = fallbackData.code;
        }

        return {
            text: mockText,
            isFallback: true,
            errorDetails: errorMessage
        };
    }
};