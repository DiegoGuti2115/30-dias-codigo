export function parseSSEStream(chunk: string, buffer: string): { content: string, newBuffer: string, done: boolean } {
  // 1. Unimos el remanente anterior con el nuevo chunk recibido
  let combinedBuffer = buffer + chunk;
  let content = '';
  let done = false;

  // 2. Los eventos SSE completos siempre terminan en doble salto de línea
  const messages = combinedBuffer.split('\n\n');

  // 3. El último elemento podría ser un evento incompleto. Lo sacamos y lo devolvemos como nuevo buffer.
  combinedBuffer = messages.pop() || '';

  // 4. Procesamos solo los mensajes garantizados como completos
  for (const message of messages) {
    const lines = message.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const dataStr = line.slice(6).trim();

        if (dataStr === '[DONE]') {
          done = true;
          continue;
        }

        try {
          const parsed = JSON.parse(dataStr);
          const deltaContent = parsed.choices?.[0]?.delta?.content;
          if (deltaContent) {
            content += deltaContent;
          }
        } catch (e) {
          // Fallback seguro: Si un JSON viene malformado desde el proveedor, 
          // logueamos el error pero no rompemos el stream de la UI.
          console.warn('[SSE Parser] Error parseando JSON de un mensaje completo:', e, dataStr);
        }
      }
    }
  }

  return { content, newBuffer: combinedBuffer, done };
}