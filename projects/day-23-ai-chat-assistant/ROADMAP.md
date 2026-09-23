# ROADMAP — Day 23: Asistente de Chat IA

Tiempo total estimado: **≤ 3 horas** · Límite estricto del reto.

---

## Fase 0 — Setup (15 min)

- [x] Crear proyecto con Vite + React + TypeScript: `npm create vite@latest . -- --template react-ts`
- [x] Instalar dependencias: `tailwindcss`, `idb`, `lucide-react`
- [x] Configurar `tailwind.config.ts` y añadir directivas en `index.css`
- [x] Crear `.env.example` con las variables de OpenAI y Azure
- [x] Definir tipos base en `src/types/chat.ts` (`Message`, `Role`, `ChatSession`, `ModelConfig`)

---

## Fase 1 — Servicio de IA y fallback (30 min)

- [x] Implementar `src/services/openai-client.ts`
  - Función `streamCompletion(messages, config)` → `ReadableStream`
  - Compatible con OpenAI y Azure AI Foundry (mismo endpoint `/chat/completions`)
- [x] Implementar `src/services/mock-client.ts`
  - Lee respuestas de `data/mock-responses.json`
  - Simula delay y streaming carácter a carácter
- [x] Implementar `src/services/ai-service.ts`
  - Lógica de selección: credenciales presentes → cliente real, si no → mock
  - Retry automático con un intento extra antes de caer al fallback

**Checkpoint:** test unitario que verifica que el mock devuelve stream correctamente.

---

## Fase 2 — Estado global y persistencia (25 min)

- [x] Crear `src/store/chat-context.tsx`
  - `useReducer` con acciones: `ADD_MESSAGE`, `UPDATE_LAST_MESSAGE`, `CLEAR_SESSION`, `SET_MODEL`
  - Provider que expone estado y dispatch
- [x] Implementar `src/hooks/useStorage.ts`
  - Guardar y cargar `ChatSession` en IndexedDB con `idb`
  - Auto-guardado tras cada mensaje completado
- [x] Implementar `src/hooks/useChat.ts`
  - Orquesta llamada al servicio, actualización del stream en el store y persistencia

**Checkpoint:** consola del navegador muestra mensajes entrando al store y persistiéndose en IndexedDB.

---

## Fase 3 — Componentes UI (50 min)

- [x] `src/components/layout/ChatLayout.tsx` — estructura base (sidebar + área de chat)
- [x] `src/components/chat/MessageList.tsx` — lista de mensajes con scroll automático al fondo
- [x] `src/components/chat/MessageBubble.tsx` — burbuja usuario/asistente + soporte Markdown básico
- [x] `src/components/chat/TypingIndicator.tsx` — indicador animado mientras llega el stream
- [x] `src/components/chat/ChatInput.tsx` — textarea con envío por `Enter` (Shift+Enter para salto de línea)
- [x] `src/components/sidebar/ModelSelector.tsx` — dropdown con modelos configurables
- [x] `src/components/sidebar/SystemPromptEditor.tsx` — textarea editable para el system prompt
- [x] `src/components/sidebar/ExportButton.tsx` — descarga conversación como `.md`

**Checkpoint:** UI funcional end-to-end en modo demo sin credenciales.

---

## Fase 4 — Hook de streaming (20 min)

- [x] Implementar `src/hooks/useStream.ts`
  - Lee el `ReadableStream`, decodifica con `TextDecoder`
  - Parsea eventos `data: {...}` del formato SSE de OpenAI
  - Llama a `dispatch(UPDATE_LAST_MESSAGE)` en cada chunk
- [x] Manejar evento `[DONE]` y estado de carga (`isStreaming`)
- [x] Manejar errores de red y timeout (mostrar mensaje de error en la burbuja)

**Checkpoint:** mensaje del asistente aparece carácter a carácter en la UI.

---

## Fase 5 — Integración real y pruebas (20 min) (Parada debido a falta de tokens)

- [ ] Probar con credenciales reales (OpenAI o Azure AI Foundry)
- [ ] Verificar que el fallback mock se activa si se retiran las vars de entorno
- [ ] Ajustar estilos responsivos para mobile
- [ ] Ejecutar suite de tests: `npm run test:run`
- [ ] Corregir cualquier bug encontrado

---

## Fase 6 — Documentación y publicación (20 min)

- [x] Grabar demo de ≤ 15 s y guardar como `assets/demo.gif`
- [x] Redactar `docs/LINKEDIN_POST.md` siguiendo la plantilla del reto
- [x] Commit con mensaje: `feat(day-23): AI chat assistant with streaming and mock fallback`
- [x] Push a GitHub y publicar post en LinkedIn

---

## Árbol de archivos objetivo
``` text
src/
├── components/
│ ├── chat/
│ │ ├── ChatInput.tsx
│ │ ├── MessageBubble.tsx
│ │ ├── MessageList.tsx
│ │ └── TypingIndicator.tsx
│ ├── layout/
│ │ └── ChatLayout.tsx
│ └── sidebar/
│ ├── ExportButton.tsx
│ ├── ModelSelector.tsx
│ └── SystemPromptEditor.tsx
├── hooks/
│ ├── useChat.ts
│ ├── useStorage.ts
│ └── useStream.ts
├── services/
│ ├── ai-service.ts
│ ├── mock-client.ts
│ └── openai-client.ts
├── store/
│ └── chat-context.tsx
├── types/
│ └── chat.ts
├── utils/
│ ├── export.ts
│ └── sse-parser.ts
└── main.tsx
```

---

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| CORS al llamar a Azure desde el browser | Media | Usar proxy Vite en dev; en prod, AZURE_OPENAI permite origen `*` |
| Cuota agotada durante la demo | Baja | Fallback mock siempre activo |
| Parsing SSE roto en chunks parciales | Media | Buffer acumulativo en `sse-parser.ts` antes de parsear |
| IndexedDB bloqueado en Safari privado | Baja | Catch silencioso, estado solo en memoria |