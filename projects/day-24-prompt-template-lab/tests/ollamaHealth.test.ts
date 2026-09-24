import { describe, it, expect } from 'vitest';

describe('Infraestructura: Ollama Health Check', () => {
    
    it('debe responder al ping en el puerto local 11434 (Demonio activo)', async () => {
        try {
            // Ollama responde con "Ollama is running" en el endpoint raíz
            const response = await fetch('http://127.0.0.1:11434/');
            const text = await response.text();
            
            expect(response.status).toBe(200);
            expect(text).toContain('Ollama is running');
        } catch (error: any) {
            throw new Error(`CRÍTICO: El demonio de Ollama está apagado o el puerto 11434 está bloqueado. Ejecuta 'ollama serve' en tu terminal. Detalle: ${error.message}`);
        }
    });

    it('debe tener el modelo phi3 instanciado en el registro local', async () => {
        try {
            // Consultamos el registro de modelos locales a través de la API nativa
            const response = await fetch('http://127.0.0.1:11434/api/tags');
            const data = await response.json();
            
            const availableModels = data.models.map((model: any) => model.name);
            const hasPhi3 = availableModels.some((name: string) => name.includes('phi3'));
            
            if (!hasPhi3) {
                throw new Error(`El modelo phi3 no está descargado. Modelos disponibles en memoria: ${availableModels.join(', ')}`);
            }
            
            expect(hasPhi3).toBe(true);
        } catch (error: any) {
            throw new Error(`Fallo al consultar la API de configuración de Ollama. Detalle: ${error.message}`);
        }
    });
});