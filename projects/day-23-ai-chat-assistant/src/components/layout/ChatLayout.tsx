import type { ReactNode } from 'react';
import { ModelSelector } from '../sidebar/ModelSelector';
import { SystemPromptEditor } from '../sidebar/SystemPromptEditor';
import { ExportButton } from '../sidebar/ExportButton';
import { Sparkles } from 'lucide-react';

export function ChatLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen w-full bg-[#09090b] text-neutral-200 font-sans overflow-hidden">
      <aside className="hidden md:flex w-72 flex-col border-r border-neutral-800/60 p-6 gap-8 bg-[#09090b] flex-shrink-0">
        <div className="flex items-center gap-3 px-1">
          <div className="p-1.5 bg-neutral-800/50 rounded-lg border border-neutral-700/50 shadow-sm">
            <Sparkles size={18} className="text-neutral-300" />
          </div>
          <span className="text-sm font-medium tracking-wide text-neutral-200">
            AI Assistant
          </span>
        </div>
        <div className="flex flex-col gap-6">
          <ModelSelector />
          <SystemPromptEditor />
        </div>
        <div className="mt-auto">
          <ExportButton />
        </div>
      </aside>
      
      {/* El main ahora es una columna Flex estricta que ocupa toda la altura */}
      <main className="flex-1 flex flex-col h-screen min-w-0 bg-[#09090b]">
        {children}
      </main>
    </div>
  );
}