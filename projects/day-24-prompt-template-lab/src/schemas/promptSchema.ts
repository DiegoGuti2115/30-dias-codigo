import { z } from 'zod';

/**
 * Analiza una plantilla de texto y extrae las variables definidas entre dobles llaves.
 * Ejemplo: "Hola {{nombre}}" -> ["nombre"]
 */
export const extractTemplateVariables = (template: string): string[] => {
    const regex = /\{\{([^}]+)\}\}/g;
    const matches = [...template.matchAll(regex)];
    return Array.from(new Set(matches.map(match => match[1].trim())));
};

/**
 * Construye dinámicamente un esquema Zod basado en las variables extraídas.
 * Utiliza un refinamiento personalizado para garantizar compatibilidad estricta
 * de TypeScript y mensajes de error exactos para la FSM.
 */
export const createPayloadSchema = (variables: string[]) => {
    const schemaShape: Record<string, z.ZodTypeAny> = {};
    
    variables.forEach(variable => {
        // z.any().refine() bypasses las restricciones de $ZodStringParams 
        // e intercepta valores undefined antes de que Zod emita su error por defecto.
        schemaShape[variable] = z.any().refine(
            (val) => typeof val === 'string' && val.trim().length > 0,
            { message: `Falta la variable requerida: '${variable}'.` }
        );
    });

    return z.object(schemaShape);
};