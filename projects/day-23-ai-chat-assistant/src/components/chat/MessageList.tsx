import { useEffect, useRef } from 'react';
import { useChatContext } from '../../store/chat-context';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';

export function MessageList({ isStreaming }: { isStreaming: boolean }) {
  const { state } = useChatContext();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.session.messages, isStreaming]);

  return (
    <div className="flex-1 overflow-y-auto p-4 w-full">
      {state.session.messages.length === 0 ? (
        <div className="h-full flex items-center justify-center text-neutral-500 text-sm">
          Envía un mensaje para comenzar la conversación.
        </div>
      ) : (
        <div className="py-4 space-y-2">
          {state.session.messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isStreaming && <TypingIndicator />}
          <div ref={bottomRef} className="h-4" />
        </div>
      )}
    </div>
  );
}