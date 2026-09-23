import { useState, useCallback } from 'react';
import { useChatContext } from '../store/chat-context';
import { getChatStream } from '../services/ai-service';
import { parseSSEStream } from '../utils/sse-parser';
import type { Message } from '../types/chat';

export function useStream() {
  const { state, dispatch } = useChatContext();
  const [isStreaming, setIsStreaming] = useState(false);

  const startStream = useCallback(async (messages: Message[]) => {
    setIsStreaming(true);
    let buffer = '';

    try {
      const stream = await getChatStream(messages, state.config);
      const reader = stream.getReader();
      const decoder = new TextDecoder();

      while (true) {
        // Leemos el stream de red nativo
        const { done: streamDone, value } = await reader.read();

        if (streamDone) break;

        // Decodificamos los bytes a texto usando { stream: true } para no perder bytes multi-byte (ej. emojis cortados)
        const chunkString = decoder.decode(value, { stream: true });
        
        // Extraemos el contenido parseado y actualizamos el buffer
        const { content, newBuffer, done: sseDone } = parseSSEStream(chunkString, buffer);
        buffer = newBuffer;

        // Si hay texto nuevo, despachamos el chunk al reducer
        if (content) {
          dispatch({ type: 'UPDATE_LAST_MESSAGE', payload: content });
        }

        // Si recibimos el evento data: [DONE], cortamos el bucle
        if (sseDone) break;
      }
    } catch (error) {
      console.error('[Stream Hook Error]', error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido de red';
      
      // Manejo de errores: Mostramos el error directamente en la burbuja del asistente
      dispatch({ 
        type: 'UPDATE_LAST_MESSAGE', 
        payload: `\n\n**⚠️ Error de conexión:** Hubo un problema al procesar la respuesta (${errorMessage}). Por favor, revisa tus credenciales o cambia al Modo Demo en la configuración.` 
      });
    } finally {
      setIsStreaming(false);
    }
  }, [state.config, dispatch]);

  return { isStreaming, startStream };
}