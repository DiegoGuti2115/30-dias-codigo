import type { Message } from '../types/chat';
import mockResponses from '../../data/mock-responses.json';

export async function streamMockCompletion(messages: Message[]): Promise<ReadableStream<Uint8Array>> {
  const responses = mockResponses as string[];
  const lastMessage = messages[messages.length - 1];
  
  // Selección de respuesta pseudo-aleatoria basada en longitud del mensaje para ser determinista en pruebas
  const replyIndex = lastMessage ? lastMessage.content.length % responses.length : 0;
  const reply = responses[replyIndex];

  const encoder = new TextEncoder();
  let i = 0;

  return new ReadableStream({
    async start(controller) {
      const pushChar = () => {
        if (i < reply.length) {
          // Empaquetar en formato SSE de OpenAI para no tener que bifurcar la lógica de parseo en Fase 4
          const chunk = JSON.stringify({ choices: [{ delta: { content: reply[i] } }] });
          controller.enqueue(encoder.encode(`data: ${chunk}\n\n`));
          i++;
          setTimeout(pushChar, 15);
        } else {
          controller.enqueue(encoder.encode('data: [DONE]\n\n'));
          controller.close();
        }
      };
      pushChar();
    }
  });
}