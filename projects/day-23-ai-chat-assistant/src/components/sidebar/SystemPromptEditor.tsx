// SystemPromptEditor.tsx
import { useChatContext } from '../../store/chat-context';

export function SystemPromptEditor() {
  const { state, dispatch } = useChatContext();
  return (
    <div className="flex flex-col gap-2 px-1 flex-grow">
      <label className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">
        Instrucciones
      </label>
      <textarea
        value={state.config.systemPrompt}
        onChange={(e) => dispatch({ type: 'SET_MODEL', payload: { systemPrompt: e.target.value } })}
        className="w-full h-32 bg-neutral-900/50 text-neutral-300 rounded-lg p-3 text-sm border border-neutral-800 focus:border-neutral-600 outline-none resize-none transition-colors leading-relaxed"
        placeholder="Comportamiento del agente..."
      />
    </div>
  );
}