import { openDB } from 'idb';
import { useCallback } from 'react';
import type { ChatSession } from '../types/chat';

const DB_NAME = 'AiChatDB';
const STORE_NAME = 'sessions';

// Inicialización Lazy (Singleton pattern)
const initDB = async () => {
  return openDB(DB_NAME, 1, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    },
  });
};

export function useStorage() {
  const saveSession = useCallback(async (session: ChatSession) => {
    try {
      const db = await initDB();
      await db.put(STORE_NAME, session);
      console.log(`[Storage] Sesión ${session.id} guardada.`);
    } catch (error) {
      console.error('[Storage] Error al guardar la sesión:', error);
    }
  }, []);

  const loadSession = useCallback(async (id: string): Promise<ChatSession | undefined> => {
    try {
      const db = await initDB();
      return await db.get(STORE_NAME, id);
    } catch (error) {
      console.error('[Storage] Error al cargar la sesión:', error);
      return undefined;
    }
  }, []);

  return { saveSession, loadSession };
}   