import { useState, useRef } from 'react';
import type { KeyboardEvent } from 'react';
import { ArrowUp } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (text.trim() && !disabled) {
      onSendMessage(text.trim());
      setText('');
      if (textareaRef.current) textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full p-4 bg-[#09090b] flex-shrink-0 border-t border-neutral-900/50">
      <div className="max-w-3xl mx-auto relative flex items-end bg-[#171717] rounded-2xl border border-neutral-800 p-2 shadow-sm transition-all focus-within:border-neutral-600">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe un mensaje..."
          disabled={disabled}
          className="w-full max-h-48 min-h-[44px] bg-transparent text-neutral-200 placeholder-neutral-500 resize-none outline-none py-3 px-4 text-[15px] disabled:opacity-50"
          rows={1}
        />
        <button
          onClick={handleSubmit}
          disabled={!text.trim() || disabled}
          className="mb-1 mr-1 p-2 bg-neutral-200 text-black hover:bg-white disabled:bg-neutral-800 disabled:text-neutral-500 rounded-xl transition-colors cursor-pointer flex-shrink-0"
        >
          <ArrowUp size={18} strokeWidth={2.5} />
        </button>
      </div>
      <div className="text-center mt-3 text-xs text-neutral-600 font-medium tracking-wide">
        Día 23 · 30 Días, 30 Proyectos
      </div>
    </div>
  );
}