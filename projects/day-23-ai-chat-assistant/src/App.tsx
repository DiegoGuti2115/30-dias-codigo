import { ChatLayout } from './components/layout/ChatLayout';
import { MessageList } from './components/chat/MessageList';
import { ChatInput } from './components/chat/ChatInput';
import { useChat } from './hooks/useChat';
import { useStream } from './hooks/useStream';
import type { Message } from './types/chat';

function App() {
  const { state, addUserMessage, addAssistantPlaceholder } = useChat();
  const { isStreaming, startStream } = useStream();

  const handleSendMessage = async (text: string) => {
    const userMsg = addUserMessage(text);
    
    // Construimos el array de mensajes para la API incluyendo el System Prompt
    const apiMessages: Message[] = [
      { id: crypto.randomUUID(), role: 'system', content: state.config.systemPrompt || '', timestamp: Date.now() },
      ...state.session.messages,
      userMsg
    ];

    addAssistantPlaceholder();
    await startStream(apiMessages);
  };

  return (
    <ChatLayout>
      <MessageList isStreaming={isStreaming} />
      <ChatInput onSendMessage={handleSendMessage} disabled={isStreaming} />
    </ChatLayout>
  );
}

export default App;