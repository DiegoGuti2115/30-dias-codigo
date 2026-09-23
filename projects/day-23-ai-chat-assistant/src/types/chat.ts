export type Role = 'system' | 'user' | 'assistant';

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: number;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

export interface ModelConfig {
  provider: 'openai' | 'azure' | 'mock';
  model: string;
  temperature: number;
  maxTokens?: number;
  systemPrompt?: string;
}