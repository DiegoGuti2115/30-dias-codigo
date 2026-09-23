import React, { createContext, useContext, useReducer, type ReactNode } from 'react';
import type { Message, ChatSession, ModelConfig } from '../types/chat';

interface ChatState {
  session: ChatSession;
  config: ModelConfig;
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'UPDATE_LAST_MESSAGE'; payload: string }
  | { type: 'CLEAR_SESSION' }
  | { type: 'SET_MODEL'; payload: Partial<ModelConfig> }
  | { type: 'LOAD_SESSION'; payload: ChatSession };

const generateId = () => crypto.randomUUID();

const initialState: ChatState = {
  session: {
    id: generateId(),
    title: 'Nueva Conversación',
    messages: [],
    createdAt: Date.now(),
    updatedAt: Date.now(),
  },
  config: {
    provider: (import.meta.env.VITE_OPENAI_API_KEY || import.meta.env.VITE_AZURE_API_KEY) ? 'openai' : 'mock',
    model: import.meta.env.VITE_OPENAI_MODEL || 'gpt-4o',
    temperature: 0.7,
    systemPrompt: 'Eres un asistente de IA útil y conciso.',
  },
};

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        session: {
          ...state.session,
          messages: [...state.session.messages, action.payload],
          updatedAt: Date.now(),
        },
      };
    case 'UPDATE_LAST_MESSAGE': {
      const messages = [...state.session.messages];
      const lastIndex = messages.length - 1;
      if (lastIndex >= 0) {
        messages[lastIndex] = {
          ...messages[lastIndex],
          content: messages[lastIndex].content + action.payload,
        };
      }
      return {
        ...state,
        session: { ...state.session, messages, updatedAt: Date.now() },
      };
    }
    case 'CLEAR_SESSION':
      return {
        ...state,
        session: {
          ...initialState.session,
          id: generateId(),
          createdAt: Date.now(),
          updatedAt: Date.now(),
        },
      };
    case 'SET_MODEL':
      return {
        ...state,
        config: { ...state.config, ...action.payload },
      };
    case 'LOAD_SESSION':
      return {
        ...state,
        session: action.payload,
      };
    default:
      return state;
  }
}

const ChatContext = createContext<{
  state: ChatState;
  dispatch: React.Dispatch<ChatAction>;
} | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  return (
    <ChatContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext debe usarse dentro de un ChatProvider');
  }
  return context;
}