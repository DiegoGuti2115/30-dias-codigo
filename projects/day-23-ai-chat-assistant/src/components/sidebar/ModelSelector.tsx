// ModelSelector.tsx
import { useChatContext } from '../../store/chat-context';

export function ModelSelector() {
  const { state, dispatch } = useChatContext();
  return (
    <div className="flex flex-col gap-2 px-1">
      <label className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">
        Modelo
      </label>
      <select
        value={state.config.provider}
        onChange={(e) => dispatch({ type: 'SET_MODEL', payload: { provider: e.target.value as any } })}
        className="w-full bg-neutral-900/50 text-neutral-200 rounded-lg p-2.5 text-sm border border-neutral-800 focus:border-neutral-600 outline-none appearance-none cursor-pointer transition-colors"
      >
        <option value="openai">OpenAI (GPT-4o)</option>
        <option value="azure">Azure AI Foundry</option>
        <option value="mock">Modo Demo</option>
      </select>
    </div>
  );
}