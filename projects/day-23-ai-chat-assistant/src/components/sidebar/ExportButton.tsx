import { useChatContext } from '../../store/chat-context';
import { Download } from 'lucide-react';

export function ExportButton() {
  const { state } = useChatContext();

  const handleExport = () => {
    const text = state.session.messages
      .map((m) => `**${m.role.toUpperCase()}**:\n${m.content}\n`)
      .join('\n---\n\n');
    
    const blob = new Blob([text], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={handleExport}
      className="flex items-center justify-center gap-2 w-full bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 rounded-xl p-3 text-sm transition-all backdrop-blur-md cursor-pointer"
    >
      <Download size={16} className="text-sky-400" />
      Exportar a Markdown
    </button>
  );
}