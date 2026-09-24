import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { generateText } from '../src/services/llmProvider';
import fallbackDataRaw from '../data/fallback_responses.json';

// Contrato para los datos estáticos
interface FallbackData {
    default: string;
    summarize: string;
    translate: string;
    code: string;
}
const fallbackData = fallbackDataRaw as FallbackData;

// Simulación (Mock) de la API Fetch global
const fetchMock = vi.fn();
global.fetch = fetchMock;

describe('LLM Provider Pipeline: Circuit Breaker y Fallback', () => {
    
    beforeEach(() => {
        fetchMock.mockClear();
        // Silenciamos los console.warn esperados durante los tests de fallback
        // para mantener limpia la consola del runner.
        vi.spyOn(console, 'warn').mockImplementation(() => {});
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('debe devolver la respuesta del LLM cuando el motor local está disponible', async () => {
        // Simulamos una respuesta HTTP 200 OK de Ollama
        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ response: 'Respuesta generada por modelo local.' })
        });

        const result = await generateText('Hola, ¿cómo estás?');

        expect(result.isFallback).toBe(false);
        expect(result.text).toBe('Respuesta generada por modelo local.');
        expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    it('debe conmutar al fallback por defecto si la red falla (Ej. Error 500)', async () => {
        // Simulamos un fallo del servidor local
        fetchMock.mockResolvedValueOnce({
            ok: false,
            status: 500
        });

        const result = await generateText('Un prompt cualquiera');

        expect(result.isFallback).toBe(true);
        expect(result.text).toBe(fallbackData.default);
        expect(result.errorDetails).toContain('HTTP Status: 500');
    });

    it('debe conmutar al fallback de resumen si el prompt solicita resumir y el LLM rechaza conexión', async () => {
        // Simulamos que Ollama está apagado (Connection refused)
        fetchMock.mockRejectedValueOnce(new Error('Connection refused'));

        const result = await generateText('Por favor, resume este texto estructurado.');

        expect(result.isFallback).toBe(true);
        expect(result.text).toBe(fallbackData.summarize);
    });

    it('debe conmutar al fallback de código ante un Timeout (AbortError)', async () => {
        // Simulamos la interrupción por parte del AbortController del Circuit Breaker
        const abortError = new Error('The user aborted a request.');
        abortError.name = 'AbortError';
        fetchMock.mockRejectedValueOnce(abortError);

        const result = await generateText('Genera un código en python para este problema');

        expect(result.isFallback).toBe(true);
        expect(result.text).toBe(fallbackData.code);
        expect(result.errorDetails).toContain('Timeout (3s) superado.');
    });
});