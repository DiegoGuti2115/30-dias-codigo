export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 p-4 w-16 bg-gray-800 rounded-2xl rounded-tl-sm border border-gray-700">
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
    </div>
  );
}