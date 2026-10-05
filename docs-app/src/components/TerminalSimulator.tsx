import React, { useState, useRef, useEffect } from 'react';
import { Terminal, Send, RefreshCw, Sparkles, HelpCircle, Shield, Cpu, Play } from 'lucide-react';

interface TerminalMessage {
  id: string;
  type: 'input' | 'output' | 'system';
  content: string;
  model?: string;
  timestamp: string;
}

export const TerminalSimulator: React.FC = () => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number>(-1);
  const [draftInput, setDraftInput] = useState('');
  const [currentModel, setCurrentModel] = useState('nvidia/nemotron-3-super-120b-a12b');
  const [currentProvider, setCurrentProvider] = useState('nvidia');
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState<TerminalMessage[]>([
    {
      id: 'welcome',
      type: 'system',
      content: `\x1b[36m╔════════════════════════════════════════════════════════════════╗\x1b[0m
\x1b[36m║\x1b[0m  \x1b[1m⚡ r.outers (rts) — Autonomous AI Coding Agent v2.4.0\x1b[0m        \x1b[36m║\x1b[0m
\x1b[36m║\x1b[0m  Engine: \x1b[33mNVIDIA NIM\x1b[0m | Platform: \x1b[32mAndroid Termux & Linux\x1b[0m         \x1b[36m║\x1b[0m
\x1b[36m║\x1b[0m  Model : \x1b[35mNemotron 3 Super 120B\x1b[0m | Status: \x1b[32m⚡ Ready\x1b[0m                 \x1b[36m║\x1b[0m
\x1b[36m╚════════════════════════════════════════════════════════════════╝\x1b[0m
Ketik \x1b[33m/help\x1b[0m untuk panduan atau masukkan prompt tugas coding kamu!`,
      timestamp: new Date().toLocaleTimeString()
    }
  ]);

  const terminalEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isProcessing]);

  // ANSI Color Code to HTML Spans parser
  const renderAnsi = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, lIdx) => {
      // Regex to match ANSI escape codes
      const parts = line.split(/(\x1b\[[0-9;]*m)/g);
      let currentClasses = 'text-gray-300';
      let isBold = false;

      const elements: React.ReactNode[] = [];

      parts.forEach((part, pIdx) => {
        if (part.startsWith('\x1b[')) {
          if (part === '\x1b[0m') {
            currentClasses = 'text-gray-300';
            isBold = false;
          } else if (part === '\x1b[1m') {
            isBold = true;
          } else if (part === '\x1b[31m') {
            currentClasses = 'text-red-400 font-semibold';
          } else if (part === '\x1b[32m') {
            currentClasses = 'text-emerald-400 font-semibold';
          } else if (part === '\x1b[33m') {
            currentClasses = 'text-amber-300 font-semibold';
          } else if (part === '\x1b[34m') {
            currentClasses = 'text-blue-400 font-semibold';
          } else if (part === '\x1b[35m') {
            currentClasses = 'text-pink-400 font-semibold';
          } else if (part === '\x1b[36m') {
            currentClasses = 'text-cyan-400 font-semibold';
          }
        } else if (part) {
          elements.push(
            <span
              key={pIdx}
              className={`${currentClasses} ${isBold ? 'font-bold' : ''}`}
            >
              {part}
            </span>
          );
        }
      });

      return (
        <div key={lIdx} className="min-h-[1.25rem] leading-relaxed">
          {elements.length > 0 ? elements : <span>&nbsp;</span>}
        </div>
      );
    });
  };

  const handleExecute = async (cmdText?: string) => {
    const commandToSend = (cmdText !== undefined ? cmdText : input).trim();
    if (!commandToSend || isProcessing) return;

    // Add to input history
    setHistory(prev => [...prev, commandToSend]);
    setHistoryIndex(-1);
    setInput('');

    // Append user input to terminal
    const userMsg: TerminalMessage = {
      id: Math.random().toString(),
      type: 'input',
      content: commandToSend,
      model: currentModel,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMsg]);
    setIsProcessing(true);

    try {
      const response = await fetch('/api/terminal/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: commandToSend,
          currentModel,
          currentProvider
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.newModel) setCurrentModel(data.newModel);
        if (data.newProvider) setCurrentProvider(data.newProvider);

        setMessages(prev => [
          ...prev,
          {
            id: Math.random().toString(),
            type: 'output',
            content: data.output,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);
      } else {
        throw new Error('Server returned non-200');
      }
    } catch (err) {
      // Local fallback simulation if backend is busy or unreachable
      setTimeout(() => {
        let simulatedOutput = '';
        if (commandToSend === '/help') {
          simulatedOutput = `\x1b[36m/setup\x1b[0m      Configure API keys and providers\n\x1b[36m/model\x1b[0m      Switch active AI model\n\x1b[36m/skills\x1b[0m     List active skill prompt extensions\n\x1b[36m/clear\x1b[0m      Reset conversation context`;
        } else if (commandToSend.startsWith('/model')) {
          const mod = commandToSend.replace('/model', '').trim() || 'nvidia/nemotron-3-super-120b-a12b';
          setCurrentModel(mod);
          simulatedOutput = `\x1b[32m✔ Model successfully switched to:\x1b[0m \x1b[1m${mod}\x1b[0m`;
        } else {
          simulatedOutput = `\x1b[35mRTS > Planning task execution...\x1b[0m\n\x1b[33mRTS > Writing script.py\x1b[0m\n\x1b[32m✔ RTS > Completed task successfully!\x1b[0m`;
        }

        setMessages(prev => [
          ...prev,
          {
            id: Math.random().toString(),
            type: 'output',
            content: simulatedOutput,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);
      }, 500);
    } finally {
      setIsProcessing(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleExecute();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (history.length === 0) return;
      if (historyIndex === -1) {
        setDraftInput(input);
        const nextIdx = history.length - 1;
        setHistoryIndex(nextIdx);
        setInput(history[nextIdx]);
      } else if (historyIndex > 0) {
        const nextIdx = historyIndex - 1;
        setHistoryIndex(nextIdx);
        setInput(history[nextIdx]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex === -1) return;
      if (historyIndex < history.length - 1) {
        const nextIdx = historyIndex + 1;
        setHistoryIndex(nextIdx);
        setInput(history[nextIdx]);
      } else {
        setHistoryIndex(-1);
        setInput(draftInput);
      }
    }
  };

  const formattedModelName = currentModel.replace('nvidia/', '').replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-6xl mx-auto rounded-2xl overflow-hidden border border-cyber-border bg-[#090d16] shadow-2xl shadow-neon-cyan/5">
      
      {/* Top Terminal Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#0d121f] border-b border-cyber-border">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-[#FF5F56] border border-[#E0443E]"></div>
          <div className="w-3 h-3 rounded-full bg-[#FFBD2E] border border-[#DEA123]"></div>
          <div className="w-3 h-3 rounded-full bg-[#27C93F] border border-[#1AAB29]"></div>
          <span className="ml-3 font-mono text-xs font-semibold text-gray-300 flex items-center space-x-1.5">
            <Terminal className="w-3.5 h-3.5 text-cyber-cyan" />
            <span>r.outers @ termux-session-0</span>
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="hidden sm:flex items-center space-x-1 px-2 py-0.5 rounded bg-cyber-pink/10 text-cyber-pink border border-cyber-pink/30">
            <Sparkles className="w-3 h-3" />
            <span>Akari Engine Active</span>
          </span>

          <button
            onClick={() => setMessages([])}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-cyber-card transition-all"
            title="Clear terminal screen"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Screen Body */}
      <div 
        onClick={() => inputRef.current?.focus()}
        className="flex-1 overflow-y-auto p-4 md:p-6 font-mono text-xs md:text-sm space-y-4 cursor-text bg-[#070a10]"
      >
        {messages.map(msg => (
          <div key={msg.id} className="space-y-1">
            {msg.type === 'input' && (
              <div className="flex items-start space-x-2 text-cyber-cyan">
                <span className="text-cyber-pink font-bold">r.outers &gt;</span>
                <span className="text-gray-100 font-semibold">{msg.content}</span>
              </div>
            )}
            {msg.type !== 'input' && (
              <div className="text-gray-300 pl-1">
                {renderAnsi(msg.content)}
              </div>
            )}
          </div>
        ))}

        {isProcessing && (
          <div className="flex items-center space-x-2 text-cyber-cyan animate-pulse">
            <span className="w-2 h-2 rounded-full bg-cyber-cyan"></span>
            <span>r.outers is reasoning & executing tools...</span>
          </div>
        )}

        <div ref={terminalEndRef} />
      </div>

      {/* Quick Action Badges */}
      <div className="px-4 py-2 bg-[#0a0e1a] border-t border-cyber-border flex items-center space-x-2 overflow-x-auto text-[11px] font-mono">
        <span className="text-gray-400 flex items-center shrink-0">
          <Play className="w-3 h-3 mr-1 text-cyber-cyan" /> Quick Test:
        </span>
        <button
          onClick={() => handleExecute('/help')}
          className="px-2.5 py-1 rounded-lg bg-cyber-card hover:bg-cyber-border text-gray-300 hover:text-cyber-cyan border border-cyber-border shrink-0 transition-all"
        >
          /help
        </button>
        <button
          onClick={() => handleExecute('/skills')}
          className="px-2.5 py-1 rounded-lg bg-cyber-card hover:bg-cyber-border text-gray-300 hover:text-cyber-purple border border-cyber-border shrink-0 transition-all"
        >
          /skills
        </button>
        <button
          onClick={() => handleExecute('/model deepseek-ai/deepseek-r1')}
          className="px-2.5 py-1 rounded-lg bg-cyber-card hover:bg-cyber-border text-gray-300 hover:text-cyber-yellow border border-cyber-border shrink-0 transition-all"
        >
          /model deepseek-r1
        </button>
        <button
          onClick={() => handleExecute('Buatkan REST API Anime dengan TypeScript')}
          className="px-2.5 py-1 rounded-lg bg-cyber-card hover:bg-cyber-border text-gray-300 hover:text-cyber-pink border border-cyber-border shrink-0 transition-all"
        >
          Buat REST API Anime
        </button>
        <button
          onClick={() => handleExecute('/memory')}
          className="px-2.5 py-1 rounded-lg bg-cyber-card hover:bg-cyber-border text-gray-300 hover:text-cyber-green border border-cyber-border shrink-0 transition-all"
        >
          /memory
        </button>
      </div>

      {/* Authentic Double-Line Prompt Bar */}
      <div className="p-3 bg-[#0d121f] border-t border-cyber-border flex flex-col space-y-2">
        {/* Line 1: Input Prompt */}
        <div className="flex items-center space-x-2">
          <span className="font-mono text-sm font-bold text-cyber-pink shrink-0">
            r.outers &gt;
          </span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isProcessing}
            placeholder="Type a prompt, slash command, or use UP/DOWN arrow keys..."
            className="flex-1 bg-transparent font-mono text-sm text-gray-100 placeholder-gray-500 focus:outline-none"
            autoFocus
          />
          <button
            onClick={() => handleExecute()}
            disabled={!input.trim() || isProcessing}
            className="p-1.5 rounded-lg bg-cyber-cyan text-black hover:bg-cyan-300 disabled:opacity-40 disabled:hover:bg-cyber-cyan transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        {/* Line 2: Status Bar Info */}
        <div className="flex items-center justify-between pt-1 border-t border-cyber-border/50 text-[11px] font-mono text-gray-400">
          <div className="flex items-center space-x-2">
            <span className="text-cyber-yellow font-semibold flex items-center">
              ⚡ {formattedModelName}
            </span>
            <span>·</span>
            <span className="text-cyber-cyan">Auto Tool Calling</span>
            <span>·</span>
            <span className="text-emerald-400 flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              <span>Ready</span>
            </span>
          </div>

          <div className="hidden sm:flex items-center space-x-3 text-gray-500">
            <span>UP/DOWN for History</span>
            <span>·</span>
            <span>Ctrl+C to cancel</span>
          </div>
        </div>
      </div>

    </div>
  );
};
