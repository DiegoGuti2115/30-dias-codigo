import { extractTemplateVariables, createPayloadSchema } from '../schemas/promptSchema';

export interface RenderResult {
    success: boolean;
    renderedPrompt?: string;
    errors?: string[];
}

/**
 * Motor de inyección puro: fusiona la plantilla con el payload de variables,
 * aplicando validación estricta del contrato previo a la renderización.
 */
export const renderPrompt = (
    template: string, 
    payload: Record<string, string>
): RenderResult => {
    // 1. Extraer los requisitos del prompt
    const requiredVariables = extractTemplateVariables(template);
    
    // 2. Fast-return si es un prompt estático (sin variables)
    if (requiredVariables.length === 0) {
        return { success: true, renderedPrompt: template };
    }

    // 3. Crear el contrato Zod dinámico y validar el input
    const schema = createPayloadSchema(requiredVariables);
    const validation = schema.safeParse(payload);

    if (!validation.success) {
        const errorMessages = validation.error.issues.map(issue => issue.message);
        return { success: false, errors: errorMessages };
    }

    // 4. Inyección de dependencias en el string (Reemplazo iterativo)
    let finalPrompt = template;
    requiredVariables.forEach(variable => {
        const regex = new RegExp(`\\{\\{${variable}\\}\\}`, 'g');
        // Aserción de tipo segura (as string) para satisfacer al compilador TS
        // tras usar z.any().refine() en el esquema.
        finalPrompt = finalPrompt.replace(regex, validation.data[variable] as string);
    });

    return { success: true, renderedPrompt: finalPrompt };
};