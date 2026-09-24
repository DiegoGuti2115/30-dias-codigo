import { describe, it, expect } from 'vitest';
import { extractTemplateVariables } from '../src/schemas/promptSchema';
import { renderPrompt } from '../src/services/promptRenderer';

describe('Prompt Engineering Pipeline: Motor de Renderizado', () => {
    
    it('debe extraer múltiples variables correctamente, ignorando duplicados', () => {
        const template = "Actúa como un {{rol}}. El usuario dice: {{mensaje}}. Recuerda, eres un {{rol}}.";
        const vars = extractTemplateVariables(template);
        expect(vars).toEqual(['rol', 'mensaje']);
        expect(vars.length).toBe(2);
    });

    it('debe renderizar el prompt exitosamente si el contrato de variables se cumple', () => {
        const template = "Traduce '{{texto}}' al idioma {{idioma}}.";
        const payload = { texto: "Hello world", idioma: "Español" };
        
        const result = renderPrompt(template, payload);
        
        expect(result.success).toBe(true);
        expect(result.renderedPrompt).toBe("Traduce 'Hello world' al idioma Español.");
        expect(result.errors).toBeUndefined();
    });

    it('debe rechazar la inyección y devolver errores si faltan variables', () => {
        const template = "Genera un resumen sobre {{tema}} con un tono {{tono}}.";
        const payload = { tema: "Agentes RAG" }; // Falta 'tono'
        
        const result = renderPrompt(template, payload);
        
        expect(result.success).toBe(false);
        expect(result.renderedPrompt).toBeUndefined();
        expect(result.errors).toBeDefined();
        expect(result.errors?.[0]).toContain('tono');
    });

    it('debe manejar prompts estáticos sin variables de inyección', () => {
        const template = "Eres un asistente útil y conciso.";
        const result = renderPrompt(template, {});
        
        expect(result.success).toBe(true);
        expect(result.renderedPrompt).toBe(template);
    });
});