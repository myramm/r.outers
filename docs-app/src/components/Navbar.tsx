import React from 'react';
import { Terminal, Search, Github, Zap, BookOpen, Layers, Cpu, Code2, Menu, X } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenSearch: () => void;
  mobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenSearch,
  mobileMenuOpen,
  setMobileMenuOpen
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-cyber-border/80 bg-[#080b11]/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left: Brand Logo & Version */}
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-gray-400 hover:text-white rounded-lg hover:bg-cyber-card"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <div 
            onClick={() => setActiveTab('docs')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyber-pink to-cyber-cyan flex items-center justify-center shadow-neon-cyan group-hover:scale-105 transition-transform">
              <Zap className="w-5 h-5 text-white fill-white" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
                  r.outers
                </span>
                <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-cyber-pink/20 text-cyber-pink border border-cyber-pink/40 font-semibold">
                  rts v2.4.0
                </span>
              </div>
              <span className="text-[10px] text-gray-400 font-mono">
                Autonomous AI Agent CLI
              </span>
            </div>
          </div>
        </div>

        {/* Center: Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 font-medium text-sm">
          <button
            onClick={() => setActiveTab('docs')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg transition-all ${
              activeTab === 'docs'
                ? 'bg-cyber-card text-cyber-cyan border border-cyber-border shadow-sm'
                : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-card/50'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Documentation</span>
          </button>

          <button
            onClick={() => setActiveTab('simulator')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg transition-all ${
              activeTab === 'simulator'
                ? 'bg-cyber-card text-cyber-pink border border-cyber-pink/30 shadow-neon-pink/20 shadow-sm'
                : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-card/50'
            }`}
          >
            <Terminal className="w-4 h-4" />
            <span>Terminal Simulator</span>
            <span className="w-2 h-2 rounded-full bg-cyber-pink animate-pulse"></span>
          </button>

          <button
            onClick={() => setActiveTab('models')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg transition-all ${
              activeTab === 'models'
                ? 'bg-cyber-card text-cyber-yellow border border-cyber-border shadow-sm'
                : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-card/50'
            }`}
          >
            <Cpu className="w-4 h-4" />
            <span>80+ Models</span>
          </button>

          <button
            onClick={() => setActiveTab('skills')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg transition-all ${
              activeTab === 'skills'
                ? 'bg-cyber-card text-cyber-purple border border-cyber-border shadow-sm'
                : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-card/50'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Skill Catalog</span>
          </button>

          <button
            onClick={() => setActiveTab('playground')}
            className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg transition-all ${
              activeTab === 'playground'
                ? 'bg-cyber-card text-cyber-green border border-cyber-border shadow-sm'
                : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-card/50'
            }`}
          >
            <Code2 className="w-4 h-4" />
            <span>REST API</span>
          </button>
        </nav>

        {/* Right: Search trigger & GitHub */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenSearch}
            className="flex items-center space-x-2.5 px-3 py-1.5 rounded-xl bg-cyber-card border border-cyber-border text-gray-400 hover:text-gray-200 hover:border-cyber-cyan/50 text-xs transition-all shadow-inner"
          >
            <Search className="w-3.5 h-3.5 text-cyber-cyan" />
            <span className="hidden sm:inline">Search docs...</span>
            <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-[#090d16] text-gray-400 rounded border border-cyber-border">
              ⌘K
            </kbd>
          </button>

          <a
            href="https://github.com/myramm/r.outers"
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1.5 p-2 rounded-xl bg-cyber-card border border-cyber-border text-gray-300 hover:text-white hover:border-cyber-pink/50 transition-all"
            title="GitHub Repository"
          >
            <Github className="w-4 h-4" />
          </a>
        </div>

      </div>
    </header>
  );
};
