import type { Message, ModelConfig } from '../types/chat';
import { streamCompletion } from './openai-client';
import { streamMockCompletion } from './mock-client';

export async function getChatStream(messages: Message[], config: ModelConfig, retries = 1): Promise<ReadableStream<Uint8Array>> {
  const hasOpenAI = Boolean(import.meta.env.VITE_OPENAI_API_KEY);
  const hasAzure = Boolean(import.meta.env.VITE_AZURE_API_KEY && import.meta.env.VITE_AZURE_ENDPOINT);
  
  const hasRealCredentials = (config.provider === 'openai' && hasOpenAI) || (config.provider === 'azure' && hasAzure);

  if (!hasRealCredentials || config.provider === 'mock') {
    return streamMockCompletion(messages);
  }

  try {
    return await streamCompletion(messages, config);
  } catch (error) {
    if (retries > 0) {
      console.warn(`[AI Service] Error detectado. Reintentando... (${retries} intentos restantes)`);
      return getChatStream(messages, config, retries - 1);
    }
    console.error('[AI Service] Fallaron los intentos. Activando fallback a modo demo.', error);
    return streamMockCompletion(messages);
  }
}