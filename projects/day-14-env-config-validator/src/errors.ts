export type SchemaErrorCode =
  | 'E_SCHEMA_JSON_PARSE'
  | 'E_SCHEMA_INVALID'
  | 'E_SCHEMA_UNKNOWN_FIELD'
  | 'E_SCHEMA_UNKNOWN_REFERENCE'
  | 'E_SCHEMA_INVALID_PATTERN'
  | 'E_SCHEMA_DUPLICATE_DEPENDENCY';

export interface SchemaIssue {
  readonly code: SchemaErrorCode;
  readonly path: string;
  readonly message: string;
}

/**
 * Error de dominio seguro para la compilación del esquema v1.
 *
 * No conserva ni serializa valores de configuración; solo expone un código,
 * una ruta declarativa y un mensaje apto para un futuro adaptador de CLI.
 */
export class SchemaCompilationError extends Error {
  public readonly code: SchemaErrorCode;
  public readonly issues: readonly SchemaIssue[];

  public constructor(code: SchemaErrorCode, issues: readonly SchemaIssue[]) {
    super('El esquema no cumple el contrato v1.');
    this.name = 'SchemaCompilationError';
    this.code = code;
    this.issues = Object.freeze([...issues]);
  }
}

export function schemaIssue(code: SchemaErrorCode, path: string, message: string): SchemaIssue {
  return Object.freeze({ code, path, message });
}
