import React, { useState, useEffect, useRef } from 'react';
import { Search, X, BookOpen, Terminal, Cpu, Layers, ArrowRight } from 'lucide-react';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectResult: (sectionId: string, tabName?: string) => void;
}

export const SearchModal: React.FC<SearchModalProps> = ({ isOpen, onClose, onSelectResult }) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const searchItems = [
    { id: 'quickstart', title: '1-Line Quickstart & Installation', category: 'Installation', icon: Terminal, tab: 'docs', desc: 'Install r.outers CLI on Android Termux or Linux VPS in 1 command.' },
    { id: 'architecture', title: 'Double-Line Prompt & TUI Loop', category: 'Architecture', icon: BookOpen, tab: 'docs', desc: 'Raw terminal mode, UP/DOWN arrow history, and status bar.' },
    { id: 'models', title: 'NVIDIA NIM 80+ Models Catalog', category: 'Models', icon: Cpu, tab: 'models', desc: 'Browse Nemotron-3 Super, DeepSeek-R1, Qwen-2.5, GLM-5.3.' },
    { id: 'skills', title: 'Anti-Slop & Superpowers Skills', category: 'Skills', icon: Layers, tab: 'skills', desc: 'Live prompt filters, code comment hygiene, and TDD enforcement.' },
    { id: 'tools', title: 'Autonomous Tool Calling Pipeline', category: 'Features', icon: Terminal, tab: 'docs', desc: 'Run shell commands, read/write files, and keyboard ask_user modal.' },
    { id: 'commands', title: 'Slash Commands Cheatsheet', category: 'Reference', icon: BookOpen, tab: 'docs', desc: 'Comprehensive list of /setup, /model, /skills, /memory, /clear.' },
    { id: 'uninstall', title: 'Uninstallation Guide', category: 'Maintenance', icon: BookOpen, tab: 'docs', desc: 'Clean removal script and environment cleanup.' }
  ];

  const filtered = searchItems.filter(item =>
    item.title.toLowerCase().includes(query.toLowerCase()) ||
    item.desc.toLowerCase().includes(query.toLowerCase()) ||
    item.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setSelectedIndex(0);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev < filtered.length - 1 ? prev + 1 : prev));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : 0));
      } else if (e.key === 'Enter' && filtered[selectedIndex]) {
        e.preventDefault();
        const selected = filtered[selectedIndex];
        onSelectResult(selected.id, selected.tab);
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filtered, selectedIndex, onClose, onSelectResult]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div 
        className="w-full max-w-2xl bg-[#0d121f] border border-cyber-border rounded-2xl shadow-2xl overflow-hidden shadow-neon-cyan/10 flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-cyber-border bg-[#090d16]">
          <Search className="w-5 h-5 text-cyber-cyan mr-3" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search documentation, slash commands, models..."
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            className="w-full bg-transparent text-gray-100 placeholder-gray-500 text-sm focus:outline-none"
          />
          <button 
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-white rounded-lg hover:bg-cyber-card"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="py-12 text-center text-gray-400 text-sm">
              No results found for "<span className="text-cyber-cyan">{query}</span>"
            </div>
          ) : (
            filtered.map((item, index) => {
              const Icon = item.icon;
              const isSelected = index === selectedIndex;
              return (
                <div
                  key={item.id}
                  onClick={() => {
                    onSelectResult(item.id, item.tab);
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`flex items-start justify-between p-3 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-cyber-card border border-cyber-cyan/40 shadow-sm'
                      : 'hover:bg-cyber-card/60 border border-transparent'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${isSelected ? 'bg-cyber-cyan/20 text-cyber-cyan' : 'bg-cyber-border/40 text-gray-400'}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-semibold text-gray-100">{item.title}</span>
                        <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyber-border/60 text-gray-400">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">{item.desc}</p>
                    </div>
                  </div>
                  <ArrowRight className={`w-4 h-4 self-center transition-transform ${isSelected ? 'text-cyber-cyan translate-x-1' : 'text-gray-600'}`} />
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="flex items-center justify-between px-4 py-2.5 bg-[#090d16] border-t border-cyber-border text-[11px] text-gray-400 font-mono">
          <div className="flex items-center space-x-4">
            <span><kbd className="px-1.5 py-0.5 rounded bg-cyber-card border border-cyber-border">↑↓</kbd> Navigate</span>
            <span><kbd className="px-1.5 py-0.5 rounded bg-cyber-card border border-cyber-border">Enter</kbd> Select</span>
            <span><kbd className="px-1.5 py-0.5 rounded bg-cyber-card border border-cyber-border">Esc</kbd> Close</span>
          </div>
          <span className="text-cyber-pink">r.outers v2.4.0</span>
        </div>

      </div>
    </div>
  );
};
