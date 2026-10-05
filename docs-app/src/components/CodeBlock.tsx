import React, { useState } from 'react';
import { Check, Copy, Terminal } from 'lucide-react';

interface CodeBlockProps {
  code: string;
  language?: string;
  filename?: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ code, language = 'bash', filename }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy', err);
    }
  };

  return (
    <div className="relative group my-4 rounded-xl overflow-hidden border border-cyber-border bg-[#0d121f] shadow-lg">
      {filename && (
        <div className="flex items-center justify-between px-4 py-2 bg-[#090d16] border-b border-cyber-border text-xs text-gray-400 font-mono">
          <div className="flex items-center space-x-2">
            <Terminal className="w-3.5 h-3.5 text-cyber-cyan" />
            <span className="text-gray-300 font-medium">{filename}</span>
          </div>
          <span className="uppercase text-[10px] tracking-wider text-gray-500">{language}</span>
        </div>
      )}

      <div className="relative p-4 font-mono text-sm overflow-x-auto text-gray-200">
        <button
          onClick={handleCopy}
          className="absolute right-3 top-3 p-1.5 rounded-lg bg-cyber-card/80 hover:bg-cyber-card border border-cyber-border text-gray-400 hover:text-cyber-cyan transition-all opacity-0 group-hover:opacity-100"
          title="Copy code"
        >
          {copied ? (
            <span className="flex items-center text-xs text-cyber-green space-x-1 px-1">
              <Check className="w-3.5 h-3.5" />
              <span>Copied!</span>
            </span>
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>

        <pre className="text-sm leading-relaxed whitespace-pre">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};
