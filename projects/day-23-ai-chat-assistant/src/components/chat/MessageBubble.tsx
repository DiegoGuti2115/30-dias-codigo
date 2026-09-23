import type { Message } from '../../types/chat';
import { User, Sparkles } from 'lucide-react';

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className="group w-full hover:bg-neutral-900/30 transition-colors py-6">
      <div className="max-w-3xl mx-auto flex gap-6 px-4">
        <div className={`flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg border ${
          isUser 
            ? 'bg-neutral-800 border-neutral-700 text-neutral-300' 
            : 'bg-transparent border-neutral-800 text-neutral-400'
        }`}>
          {isUser ? <User size={16} /> : <Sparkles size={16} />}
        </div>
        <div className="flex-1 space-y-1 overflow-hidden">
          <div className="font-medium text-sm text-neutral-400 mb-2">
            {isUser ? 'Tú' : 'Assistant'}
          </div>
          <div className="text-neutral-200 text-[15px] leading-relaxed whitespace-pre-wrap">
            {message.content}
          </div>
        </div>
      </div>
    </div>
  );
}