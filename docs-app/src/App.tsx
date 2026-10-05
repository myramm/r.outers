import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DocContent } from './components/DocContent';
import { TerminalSimulator } from './components/TerminalSimulator';
import { ModelExplorer } from './components/ModelExplorer';
import { SkillCatalog } from './components/SkillCatalog';
import { ApiPlayground } from './components/ApiPlayground';
import { SearchModal } from './components/SearchModal';
import { Heart, Sparkles, Terminal, BookOpen, Cpu, Layers, Code2 } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'docs' | 'simulator' | 'models' | 'skills' | 'playground'>('docs');
  const [activeSection, setActiveSection] = useState('quickstart');
  const [searchOpen, setSearchOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Global Cmd+K / Ctrl+K listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setSearchOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSelectSearchResult = (sectionId: string, tabName?: string) => {
    if (tabName && ['docs', 'simulator', 'models', 'skills', 'playground'].includes(tabName)) {
      setActiveTab(tabName as any);
    } else {
      setActiveTab('docs');
    }
    setActiveSection(sectionId);
  };

  return (
    <div className="min-h-screen bg-[#080b11] text-gray-100 flex flex-col selection:bg-cyber-pink selection:text-white">
      
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={(t) => setActiveTab(t as any)}
        onOpenSearch={() => setSearchOpen(true)}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />

      {/* Global Search Dialog */}
      <SearchModal
        isOpen={searchOpen}
        onClose={() => setSearchOpen(false)}
        onSelectResult={handleSelectSearchResult}
      />

      {/* Main Content Area */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 flex">
        
        {/* If Docs tab is active, show Sidebar + DocContent */}
        {activeTab === 'docs' && (
          <>
            <Sidebar
              activeSection={activeSection}
              setActiveSection={setActiveSection}
              mobileOpen={mobileMenuOpen}
              setMobileOpen={setMobileMenuOpen}
            />

            <main className="flex-1 py-8 px-0 md:px-8 overflow-y-auto">
              <DocContent
                activeSection={activeSection}
                onNavigateTab={(tab) => setActiveTab(tab as any)}
              />
            </main>
          </>
        )}

        {/* Live Terminal Simulator View */}
        {activeTab === 'simulator' && (
          <main className="flex-1 py-6 w-full">
            <TerminalSimulator />
          </main>
        )}

        {/* 80+ Models Explorer View */}
        {activeTab === 'models' && (
          <main className="flex-1 py-8 w-full">
            <ModelExplorer />
          </main>
        )}

        {/* Skill Catalog View */}
        {activeTab === 'skills' && (
          <main className="flex-1 py-8 w-full">
            <SkillCatalog />
          </main>
        )}

        {/* REST API Tester View */}
        {activeTab === 'playground' && (
          <main className="flex-1 py-8 w-full">
            <ApiPlayground />
          </main>
        )}

      </div>

      {/* Cyberpunk & Anime Aesthetic Footer */}
      <footer className="border-t border-cyber-border/80 bg-[#06080d] py-8 text-xs text-gray-400 font-mono">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-gray-200">r.outers (rts) v2.4.0</span>
            <span>—</span>
            <span className="text-gray-400">Autonomous AI Coding Agent for Termux & Linux</span>
          </div>

          <div className="flex items-center space-x-4">
            <span className="flex items-center text-cyber-pink">
              Powered by <Heart className="w-3.5 h-3.5 mx-1 fill-cyber-pink inline" /> Akari Watanabe Energy
            </span>
            <span>·</span>
            <a
              href="https://github.com/myramm/r.outers"
              target="_blank"
              rel="noreferrer"
              className="text-cyber-cyan hover:underline"
            >
              @myramm/r.outers
            </a>
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;
