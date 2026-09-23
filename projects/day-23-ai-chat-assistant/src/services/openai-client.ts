import type { Message, ModelConfig } from '../types/chat';
export async function streamCompletion(messages: Message[], config: ModelConfig): Promise<ReadableStream<Uint8Array>> {
  const isAzure = config.provider === 'azure';
  const apiKey = isAzure ? import.meta.env.VITE_AZURE_API_KEY : import.meta.env.VITE_OPENAI_API_KEY;
  
  const endpoint = isAzure
    ? `${import.meta.env.VITE_AZURE_ENDPOINT}openai/deployments/${import.meta.env.VITE_AZURE_DEPLOYMENT}/chat/completions?api-version=2024-02-15-preview`
    : 'https://api.openai.com/v1/chat/completions';

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (isAzure) {
    headers['api-key'] = apiKey;
  } else {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }

  const payload = {
    model: config.model,
    messages: messages.map(m => ({ role: m.role, content: m.content })),
    temperature: config.temperature,
    max_tokens: config.maxTokens,
    stream: true,
  };

  const response = await fetch(endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.body as ReadableStream<Uint8Array>;
}