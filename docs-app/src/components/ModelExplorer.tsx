import React, { useState, useEffect } from 'react';
import { Cpu, Search, Copy, Check, Zap, Sparkles, Filter, ShieldCheck, Terminal } from 'lucide-react';

interface ModelItem {
  id: string;
  name: string;
  provider: string;
  category: string;
  context: string;
  speed: string;
  tools: boolean;
  recommended: boolean;
  tags: string[];
}

export const ModelExplorer: React.FC = () => {
  const [models, setModels] = useState<ModelItem[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [copiedModel, setCopiedModel] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/models')
      .then(res => res.json())
      .then(data => {
        setModels(data.models || []);
        setLoading(false);
      })
      .catch(() => {
        // Fallback default list
        setModels([
          {
            id: 'nvidia/nemotron-3-super-120b-a12b',
            name: 'Nemotron 3 Super 120B',
            provider: 'NVIDIA NIM',
            category: 'Flagship Reasoning & Coding',
            context: '128k',
            speed: 'Ultra Fast (<1.2s TTFT)',
            tools: true,
            recommended: true,
            tags: ['Default', 'Fast', 'Precise Tool Calling']
          },
          {
            id: 'openai/gpt-oss-20b',
            name: 'GPT-OSS 20B',
            provider: 'NVIDIA NIM',
            category: 'Lightweight Agentic',
            context: '32k',
            speed: 'Instant (<400ms)',
            tools: true,
            recommended: true,
            tags: ['Zero-Lag', 'Low-Memory', 'Termux-Optimized']
          },
          {
            id: 'deepseek-ai/deepseek-r1',
            name: 'DeepSeek R1',
            provider: 'NVIDIA NIM',
            category: 'Deep Chain-of-Thought Reasoning',
            context: '64k',
            speed: 'Reasoning Mode',
            tools: true,
            recommended: true,
            tags: ['Math & Logic', 'Architecture Planning']
          },
          {
            id: 'qwen/qwen2.5-coder-32b-instruct',
            name: 'Qwen 2.5 Coder 32B',
            provider: 'NVIDIA NIM',
            category: 'Specialized Coding',
            context: '32k',
            speed: 'Very Fast',
            tools: true,
            recommended: true,
            tags: ['Python / Go / TS Master', 'Diffs']
          }
        ]);
        setLoading(false);
      });
  }, []);

  const handleCopyCommand = (modelId: string) => {
    const cmd = `/model ${modelId}`;
    navigator.clipboard.writeText(cmd);
    setCopiedModel(modelId);
    setTimeout(() => setCopiedModel(null), 2000);
  };

  const filteredModels = models.filter(m => {
    const matchesQuery = m.name.toLowerCase().includes(search.toLowerCase()) ||
                         m.id.toLowerCase().includes(search.toLowerCase()) ||
                         m.tags.some(t => t.toLowerCase().includes(search.toLowerCase()));
    if (selectedCategory === 'all') return matchesQuery;
    if (selectedCategory === 'recommended') return matchesQuery && m.recommended;
    return matchesQuery && m.category.toLowerCase().includes(selectedCategory.toLowerCase());
  });

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      
      {/* Header Banner */}
      <div className="relative rounded-2xl p-6 md:p-8 bg-gradient-to-r from-[#10172b] via-[#151128] to-[#1a1024] border border-cyber-border overflow-hidden">
        <div className="relative z-10 space-y-2">
          <div className="flex items-center space-x-2 text-cyber-yellow text-xs font-mono font-bold uppercase tracking-wider">
            <Zap className="w-4 h-4 fill-cyber-yellow" />
            <span>Multi-Model Router Architecture</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            NVIDIA NIM 80+ Models & Custom Providers
          </h1>
          <p className="text-gray-400 text-sm max-w-2xl leading-relaxed">
            Switch effortlessly between ultra-fast sub-400ms agents, 128k context flagships, and deep reasoning models in real-time using <code className="text-cyber-cyan font-mono">/model &lt;id&gt;</code>.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-cyber-card border border-cyber-border">
        
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-3 text-gray-500" />
          <input
            type="text"
            placeholder="Search by name, ID, or tag..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-[#090d16] border border-cyber-border rounded-lg text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyber-cyan/50"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto overflow-x-auto text-xs font-medium">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              selectedCategory === 'all'
                ? 'bg-cyber-cyan text-black font-semibold'
                : 'bg-[#090d16] text-gray-400 hover:text-white border border-cyber-border'
            }`}
          >
            All Models
          </button>
          <button
            onClick={() => setSelectedCategory('recommended')}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              selectedCategory === 'recommended'
                ? 'bg-cyber-pink text-white font-semibold'
                : 'bg-[#090d16] text-gray-400 hover:text-white border border-cyber-border'
            }`}
          >
            ⭐ Recommended
          </button>
          <button
            onClick={() => setSelectedCategory('reasoning')}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              selectedCategory === 'reasoning'
                ? 'bg-cyber-purple text-white font-semibold'
                : 'bg-[#090d16] text-gray-400 hover:text-white border border-cyber-border'
            }`}
          >
            🧠 Deep Reasoning
          </button>
          <button
            onClick={() => setSelectedCategory('coding')}
            className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition-all ${
              selectedCategory === 'coding'
                ? 'bg-cyber-yellow text-black font-semibold'
                : 'bg-[#090d16] text-gray-400 hover:text-white border border-cyber-border'
            }`}
          >
            💻 Coding Masters
          </button>
        </div>

      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredModels.map(model => (
          <div
            key={model.id}
            className={`relative p-5 rounded-2xl border transition-all hover:scale-[1.01] ${
              model.recommended
                ? 'bg-[#0e1424] border-cyber-cyan/30 shadow-lg shadow-neon-cyan/5'
                : 'bg-cyber-card border-cyber-border'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-bold text-gray-100 text-base">{model.name}</h3>
                  {model.recommended && (
                    <span className="text-[10px] uppercase font-bold font-mono px-2 py-0.5 rounded-full bg-cyber-pink/20 text-cyber-pink border border-cyber-pink/40">
                      Recommended
                    </span>
                  )}
                </div>
                <div className="text-xs font-mono text-gray-400">{model.id}</div>
              </div>

              <button
                onClick={() => handleCopyCommand(model.id)}
                className="p-2 rounded-lg bg-[#090d16] border border-cyber-border text-gray-400 hover:text-cyber-cyan transition-all"
                title="Copy /model command"
              >
                {copiedModel === model.id ? (
                  <span className="flex items-center text-[11px] text-cyber-green space-x-1 font-mono">
                    <Check className="w-3.5 h-3.5" />
                    <span>Copied!</span>
                  </span>
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>

            <div className="mt-4 grid grid-cols-3 gap-2 text-xs font-mono pt-3 border-t border-cyber-border/60">
              <div>
                <span className="text-gray-500 block text-[10px]">CONTEXT</span>
                <span className="text-cyber-cyan font-semibold">{model.context}</span>
              </div>
              <div>
                <span className="text-gray-500 block text-[10px]">SPEED / TTFT</span>
                <span className="text-cyber-yellow font-semibold">{model.speed}</span>
              </div>
              <div>
                <span className="text-gray-500 block text-[10px]">TOOL CALLING</span>
                <span className="text-cyber-green font-semibold flex items-center">
                  <ShieldCheck className="w-3 h-3 mr-1 inline" /> 100% Native
                </span>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-1.5">
              {model.tags.map((tag, tIdx) => (
                <span
                  key={tIdx}
                  className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#090d16] text-gray-300 border border-cyber-border"
                >
                  {tag}
                </span>
              ))}
            </div>

            <div className="mt-4 pt-3 border-t border-cyber-border/40 flex items-center justify-between text-xs font-mono">
              <span className="text-gray-400">Switch via CLI:</span>
              <code className="text-cyber-pink bg-cyber-pink/10 px-2 py-0.5 rounded border border-cyber-pink/20">
                /model {model.id.split('/')[1] || model.id}
              </code>
            </div>

          </div>
        ))}
      </div>

    </div>
  );
};
