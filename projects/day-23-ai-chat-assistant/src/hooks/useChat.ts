    import { useEffect, useCallback } from 'react';
import { useChatContext } from '../store/chat-context';
import { useStorage } from './useStorage';
import type { Message } from '../types/chat';

export function useChat() {
  const { state, dispatch } = useChatContext();
  const { saveSession } = useStorage();

  // 1. Auto-guardado: Persiste la sesión de forma asíncrona tras cada cambio en los mensajes
  useEffect(() => {
    if (state.session.messages.length > 0) {
      const timeoutId = setTimeout(() => {
        saveSession(state.session);
      }, 500); // Debounce de 500ms para evitar sobreescribir DB en cada chunk del stream
      
      return () => clearTimeout(timeoutId);
    }
  }, [state.session, saveSession]);

  // 2. Función base para añadir mensajes (la integración del stream vendrá en la Fase 4)
  const addUserMessage = useCallback((content: string) => {
    const newMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };
    dispatch({ type: 'ADD_MESSAGE', payload: newMessage });
    return newMessage;
  }, [dispatch]);

  const addAssistantPlaceholder = useCallback(() => {
    const placeholder: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '', // Comenzará vacío y se llenará con UPDATE_LAST_MESSAGE
      timestamp: Date.now(),
    };
    dispatch({ type: 'ADD_MESSAGE', payload: placeholder });
  }, [dispatch]);

  return { 
    state, 
    dispatch, 
    addUserMessage,
    addAssistantPlaceholder
  };
}