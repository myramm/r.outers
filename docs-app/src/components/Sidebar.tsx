import React from 'react';
import { BookOpen, Terminal, Cpu, Layers, Code2, ShieldAlert, Sparkles, HelpCircle, ArrowRight, Trash2 } from 'lucide-react';

interface SidebarProps {
  activeSection: string;
  setActiveSection: (id: string) => void;
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  setActiveSection,
  mobileOpen,
  setMobileOpen
}) => {
  const docGroups = [
    {
      title: 'Getting Started',
      items: [
        { id: 'quickstart', label: '1-Line Quickstart', icon: Terminal, badge: 'Popular' },
        { id: 'json-config', label: 'Manual JSON Setup', icon: Code2, badge: 'JSON' },
        { id: 'termux-setup', label: 'Android Termux Setup', icon: Cpu, badge: 'Mobile' },
        { id: 'uninstall', label: 'Uninstallation', icon: Trash2 }
      ]
    },
    {
      title: 'Core Architecture',
      items: [
        { id: 'architecture', label: 'Double-Line Prompt & TUI', icon: Sparkles },
        { id: 'history-navigation', label: 'Arrow History Navigation', icon: Terminal },
        { id: 'tools', label: 'Autonomous Tool Calling', icon: Code2, badge: 'Live Exec' }
      ]
    },
    {
      title: 'Models & Providers',
      items: [
        { id: 'nvidia-nim', label: 'NVIDIA NIM 80+ Models', icon: Cpu, badge: '80+ Models' },
        { id: 'reasoning-engine', label: 'Deep Reasoning Tokens', icon: Sparkles }
      ]
    },
    {
      title: 'Extensibility',
      items: [
        { id: 'skills', label: 'Anti-Slop & Skills', icon: Layers },
        { id: 'commands', label: 'Slash Commands Cheatsheet', icon: BookOpen }
      ]
    },
    {
      title: 'Help & Reference',
      items: [
        { id: 'faq', label: 'Troubleshooting & FAQ', icon: HelpCircle }
      ]
    }
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/70 backdrop-blur-sm md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Panel */}
      <aside
        className={`fixed md:sticky top-16 left-0 z-30 w-64 md:w-72 h-[calc(100vh-4rem)] overflow-y-auto p-4 bg-[#080b11] border-r border-cyber-border transition-transform duration-200 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="space-y-6">
          {docGroups.map((group, gIdx) => (
            <div key={gIdx} className="space-y-1.5">
              <h4 className="px-3 text-[11px] font-mono font-bold uppercase tracking-wider text-gray-500">
                {group.title}
              </h4>
              <div className="space-y-0.5">
                {group.items.map(item => {
                  const Icon = item.icon;
                  const isActive = activeSection === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        setActiveSection(item.id);
                        setMobileOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-cyber-card text-cyber-cyan font-semibold border border-cyber-cyan/30 shadow-sm'
                          : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-card/50'
                      }`}
                    >
                      <div className="flex items-center space-x-2.5">
                        <Icon className={`w-4 h-4 ${isActive ? 'text-cyber-cyan' : 'text-gray-500'}`} />
                        <span>{item.label}</span>
                      </div>

                      {item.badge && (
                        <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded font-bold uppercase ${
                          item.badge === 'Popular' ? 'bg-cyber-pink/20 text-cyber-pink border border-cyber-pink/30' :
                          item.badge === '80+ Models' ? 'bg-cyber-yellow/20 text-cyber-yellow border border-cyber-yellow/30' :
                          'bg-cyber-cyan/20 text-cyber-cyan border border-cyber-cyan/30'
                        }`}>
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </aside>
    </>
  );
};
