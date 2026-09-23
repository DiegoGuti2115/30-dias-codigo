import { describe, it, expect } from 'vitest';
import { streamMockCompletion } from '../../src/services/mock-client';

describe('Mock Client', () => {
  it('debe devolver un ReadableStream válido con formato SSE', async () => {
    const mockMessages = [{ id: '1', role: 'user', content: 'hola', timestamp: Date.now() }];
    const stream = await streamMockCompletion(mockMessages as any);
    
    expect(stream).toBeInstanceOf(ReadableStream);
    
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    
    const { value, done } = await reader.read();
    expect(done).toBe(false);
    
    const chunkString = decoder.decode(value);
    expect(chunkString).toContain('data: {');
    expect(chunkString).toContain('"choices"');
    expect(chunkString).toContain('"delta"');
    expect(chunkString).toContain('"content"');
  });
});