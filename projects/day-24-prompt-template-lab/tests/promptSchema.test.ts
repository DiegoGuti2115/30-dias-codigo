import { describe, it, expect } from 'vitest';
import { createPayloadSchema, extractTemplateVariables } from '../src/schemas/promptSchema';

describe('ML Data Contract: Validador Dinámico Zod', () => {
    
    it('debe extraer correctamente las variables para construir el contrato', () => {
        const template = "Resume el {{documento}} usando un tono {{tono}}.";
        const variables = extractTemplateVariables(template);
        
        expect(variables).toEqual(['documento', 'tono']);
        expect(variables.length).toBe(2);
    });

    it('debe rechazar un payload si falta una variable requerida desde la UI', () => {
        const variables = ['contexto', 'pregunta'];
        const schema = createPayloadSchema(variables);

        // Simulamos un estado de React donde el usuario omitió 'pregunta'
        const result = schema.safeParse({ contexto: 'Datos del sistema RAG...' });

        expect(result.success).toBe(false);
        if (!result.success) {
            const errorMessage = result.error.issues[0].message;
            expect(errorMessage).toBe("Falta la variable requerida: 'pregunta'.");
        }
    });

    it('debe rechazar un payload si la variable contiene solo espacios en blanco (Mutación inválida)', () => {
        const variables = ['idioma'];
        const schema = createPayloadSchema(variables);

        // Simulamos un input de usuario que intenta engañar la validación
        const result = schema.safeParse({ idioma: '    ' });

        expect(result.success).toBe(false);
        if (!result.success) {
            const errorMessage = result.error.issues[0].message;
            // El refinamiento '.trim().length > 0' intercepta y dispara nuestro error custom
            expect(errorMessage).toBe("Falta la variable requerida: 'idioma'.");
        }
    });

    it('debe aceptar un payload completo y estructurado', () => {
        const variables = ['rol', 'tarea'];
        const schema = createPayloadSchema(variables);

        // Estado ideal proveniente de VariablesForm.tsx
        const result = schema.safeParse({ 
            rol: 'Arquitecto de IA', 
            tarea: 'Diseñar un sistema de validación de agentes' 
        });

        expect(result.success).toBe(true);
    });
});