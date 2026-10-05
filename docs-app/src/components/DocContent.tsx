import React from 'react';
import { Terminal, Zap, Shield, Cpu, Layers, BookOpen, Trash2, Sparkles, CheckCircle, AlertTriangle, ArrowRight, Heart } from 'lucide-react';
import { CodeBlock } from './CodeBlock';

interface DocContentProps {
  activeSection: string;
  onNavigateTab: (tab: string) => void;
}

export const DocContent: React.FC<DocContentProps> = ({ activeSection, onNavigateTab }) => {
  return (
    <div className="max-w-4xl mx-auto space-y-12 py-2">

      {/* QUICKSTART SECTION */}
      {activeSection === 'quickstart' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-cyan uppercase font-bold tracking-wider">Installation Guide</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">1-Line Quickstart Installation</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              Install and configure <code className="text-cyber-cyan font-mono font-bold">r.outers (rts)</code> on your Android Termux device or Linux VPS in a single command.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-gradient-to-r from-cyber-card to-[#12192c] border border-cyber-cyan/30">
            <h3 className="text-sm font-bold text-cyber-cyan flex items-center">
              <Zap className="w-4 h-4 mr-2" /> One-Line Installation (Curl)
            </h3>
            <p className="text-xs text-gray-400 mt-1">
              Automatically clones the repository, installs required dependencies, creates alias symlinks in <code className="text-gray-300 font-mono">/usr/local/bin</code> (Linux) or <code className="text-gray-300 font-mono">$PREFIX/bin</code> (Termux), and launches the setup wizard:
            </p>
            <CodeBlock
              language="bash"
              code="curl -sL https://raw.githubusercontent.com/myramm/r.outers/main/install.sh | bash"
            />
          </div>

          <div className="space-y-3">
            <h2 className="text-lg font-bold text-white">Manual Installation</h2>
            <p className="text-xs text-gray-400">If you prefer manual installation from source:</p>
            <CodeBlock
              language="bash"
              filename="Terminal"
              code={`# 1. Clone repository
git clone https://github.com/myramm/r.outers.git ~/r_outers

# 2. Navigate and set executable permissions
cd ~/r_outers && chmod +x rts

# 3. Create global symlink
ln -sf ~/r_outers/rts $PREFIX/bin/rts 2>/dev/null || sudo ln -sf ~/r_outers/rts /usr/local/bin/rts

# 4. Launch r.outers
rts`}
            />
          </div>

          <div className="p-4 rounded-xl bg-[#0d1322] border border-cyber-border space-y-2">
            <h3 className="text-sm font-semibold text-white flex items-center">
              <Sparkles className="w-4 h-4 mr-2 text-cyber-pink" /> First Run Setup
            </h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              On first launch, <code className="text-cyber-cyan font-mono">rts</code> will prompt you to configure your API Key for NVIDIA NIM, Clouvia, or OpenAI Compatible APIs. You can re-run this anytime by typing <code className="text-cyber-yellow font-mono">/setup</code> or editing the JSON file directly.
            </p>
          </div>
        </section>
      )}

      {/* MANUAL JSON CONFIGURATION SECTION */}
      {activeSection === 'json-config' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-green uppercase font-bold tracking-wider">Manual Configuration</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Setup Manual via JSON File</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              Semua model, provider, custom endpoint, API key, dan timeout dapat diatur secara manual melalui file <code className="text-cyber-cyan font-mono font-bold">~/.routers_config.json</code>.
            </p>
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white flex items-center">
              <Code2 className="w-4 h-4 mr-2 text-cyber-green" /> Format Lengkap ~/.routers_config.json
            </h2>
            <p className="text-xs text-gray-400">
              Kamu bisa membuat atau mengedit file ini langsung menggunakan <code className="text-gray-200 font-mono">nano ~/.routers_config.json</code>:
            </p>
            <CodeBlock
              language="json"
              filename="~/.routers_config.json"
              code={`{
  "active_provider": "nvidia",
  "providers": {
    "nvidia": {
      "name": "NVIDIA NIM",
      "base_url": "https://integrate.api.nvidia.com/v1",
      "api_key": "nvapi-your-key-here",
      "model": "nvidia/nemotron-3-super-120b-a12b",
      "timeout": 180,
      "temperature": 0.2,
      "max_tokens": 8192
    },
    "clouvia": {
      "name": "Clouvia Router",
      "base_url": "https://router.clouvia.id/v1",
      "api_key": "your-clouvia-key",
      "model": "free-model",
      "timeout": 120
    },
    "atria": {
      "name": "Atria ASI",
      "base_url": "https://api.atria-asi.ai/v1",
      "api_key": "your-atria-key",
      "model": "Atria-Dawn-Preview",
      "timeout": 120
    },
    "custom_openai": {
      "name": "Custom Endpoint / Ollama / Local",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "model": "qwen2.5-coder:32b",
      "timeout": 180
    }
  },
  "settings": {
    "theme": "tokyonight",
    "prompt_style": "double_line",
    "history_file": "~/.routers_history",
    "skills_dir": "~/.agents/skills"
  }
}`}
            />
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white">Penjelasan Parameter JSON:</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-cyber-card border border-cyber-border">
                <span className="font-mono text-cyber-yellow font-bold">active_provider</span>
                <p className="text-gray-400 mt-1">ID provider yang sedang aktif digunakan (<code className="text-gray-200">"nvidia"</code>, <code className="text-gray-200">"clouvia"</code>, <code className="text-gray-200">"atria"</code>, dsb).</p>
              </div>
              <div className="p-3 rounded-xl bg-cyber-card border border-cyber-border">
                <span className="font-mono text-cyber-cyan font-bold">base_url</span>
                <p className="text-gray-400 mt-1">Endpoint API kompatibel OpenAI (bisa lokal Ollama, vLLM, DeepInfra, SambaNova, dsb).</p>
              </div>
              <div className="p-3 rounded-xl bg-cyber-card border border-cyber-border">
                <span className="font-mono text-cyber-pink font-bold">model</span>
                <p className="text-gray-400 mt-1">ID model target (contoh: <code className="text-gray-200">nvidia/nemotron-3-super-120b-a12b</code>).</p>
              </div>
              <div className="p-3 rounded-xl bg-cyber-card border border-cyber-border">
                <span className="font-mono text-cyber-green font-bold">timeout</span>
                <p className="text-gray-400 mt-1">Durasi batas waktu request dalam detik (default 180 detik untuk model reasoning).</p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ANDROID TERMUX SETUP */}
      {activeSection === 'termux-setup' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-pink uppercase font-bold tracking-wider">Mobile Environment</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Android Termux Configuration</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              r.outers is engineered specifically for Android Termux with zero memory overhead, sub-second latency, and touch/keyboard optimized raw terminal controls.
            </p>
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white">Prerequisites on Termux</h2>
            <CodeBlock
              language="bash"
              code={`# Update packages and install python + git + curl
pkg update -y && pkg install -y python git curl

# Allow storage access (optional, to edit phone files)
termux-setup-storage`}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-2">
              <span className="text-cyber-cyan font-bold text-sm block">📱 Touch & Arrow Keys</span>
              <p className="text-xs text-gray-400 leading-relaxed">
                Use the Termux extra-keys row (UP / DOWN) to cycle through previous prompt history seamlessly.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-2">
              <span className="text-cyber-green font-bold text-sm block">⚡ Battery & RAM Saver</span>
              <p className="text-xs text-gray-400 leading-relaxed">
                Written in lightweight Python without heavy background daemons to keep mobile CPU usage at near zero.
              </p>
            </div>
          </div>
        </section>
      )}

      {/* UNINSTALLATION SECTION */}
      {activeSection === 'uninstall' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-red-400 uppercase font-bold tracking-wider">Maintenance</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Uninstallation & Cleanup</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              Need to remove r.outers? Use our clean uninstaller script that removes all symlinks, config files, and caches safely.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-red-950/20 border border-red-500/30 space-y-2">
            <h3 className="text-sm font-bold text-red-400 flex items-center">
              <Trash2 className="w-4 h-4 mr-2" /> 1-Line Uninstall Script
            </h3>
            <CodeBlock
              language="bash"
              code="curl -sL https://raw.githubusercontent.com/myramm/r.outers/main/uninstall.sh | bash"
            />
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white">Manual Clean Removal</h2>
            <CodeBlock
              language="bash"
              code={`# 1. Remove binary symlinks
rm -f $PREFIX/bin/rts /usr/local/bin/rts /usr/bin/rts ~/.local/bin/rts

# 2. Remove configuration and history
rm -rf ~/.routers_config.json ~/.routers_history

# 3. Remove cloned repository
rm -rf ~/r_outers`}
            />
          </div>
        </section>
      )}

      {/* ARCHITECTURE & DOUBLE-LINE PROMPT */}
      {activeSection === 'architecture' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-yellow uppercase font-bold tracking-wider">Terminal UI</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Double-Line Prompt & TUI Loop</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              r.outers features a modernized terminal layout dividing input and telemetry into two distinct lines for crystal-clear readability.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-[#090d16] border border-cyber-border font-mono text-xs md:text-sm space-y-2 text-gray-200">
            <div className="text-cyber-pink font-bold flex items-center space-x-2">
              <span>r.outers &gt;</span>
              <span className="text-gray-300 font-normal">buatkan script crawler anime</span>
            </div>
            <div className="text-gray-500 text-xs border-t border-cyber-border/60 pt-1.5 flex items-center space-x-2">
              <span className="text-cyber-yellow font-semibold">⚡ Nemotron 3 Super 120B</span>
              <span>·</span>
              <span className="text-cyber-cyan">Auto Tool Calling</span>
              <span>·</span>
              <span className="text-cyber-green">Ready</span>
            </div>
          </div>

          <div className="space-y-3">
            <h2 className="text-base font-bold text-white">Key Components</h2>
            <ul className="space-y-2 text-xs text-gray-300">
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-cyber-cyan shrink-0 mt-0.5" />
                <span><b>Line 1 (Input Line):</b> Carries the active prompt <code className="text-cyber-pink font-mono">r.outers &gt;</code> and accepts multi-line input, slash commands, or standard natural language.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-cyber-yellow shrink-0 mt-0.5" />
                <span><b>Line 2 (Telemetry Status Bar):</b> Displays active model name (formatted cleanly), tool execution mode, and readiness state.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-cyber-green shrink-0 mt-0.5" />
                <span><b>Persistent History Buffer:</b> Automatically saved to <code className="text-gray-300 font-mono">~/.routers_history</code> across sessions.</span>
              </li>
            </ul>
          </div>
        </section>
      )}

      {/* HISTORY NAVIGATION */}
      {activeSection === 'history-navigation' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-cyan uppercase font-bold tracking-wider">Keyboard Navigation</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Arrow Key History Cycling</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              Navigate past prompts with <kbd className="px-1.5 py-0.5 rounded bg-cyber-card border border-cyber-border font-mono text-xs">UP</kbd> and <kbd className="px-1.5 py-0.5 rounded bg-cyber-card border border-cyber-border font-mono text-xs">DOWN</kbd> arrow keys without losing your current typed draft.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-3">
            <h3 className="text-sm font-bold text-white">How It Works</h3>
            <ul className="space-y-2 text-xs text-gray-300">
              <li>• Press <b className="text-cyber-cyan">UP</b> arrow once: Saves your current typed draft and loads your most recent prompt.</li>
              <li>• Press <b className="text-cyber-cyan">UP</b> repeatedly: Steps back through older historical inputs.</li>
              <li>• Press <b className="text-cyber-pink">DOWN</b>: Steps forward toward newer inputs.</li>
              <li>• Press <b className="text-cyber-pink">DOWN</b> past the newest input: Restores your original in-progress draft!</li>
            </ul>
          </div>

          <div className="pt-2">
            <button
              onClick={() => onNavigateTab('simulator')}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyber-pink to-cyber-cyan text-white text-xs font-bold flex items-center space-x-2 shadow-neon-pink"
            >
              <span>Try it in the Live Terminal Simulator</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </section>
      )}

      {/* AUTONOMOUS TOOLS SECTION */}
      {activeSection === 'tools' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-green uppercase font-bold tracking-wider">Tool Execution Engine</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Autonomous Tool Calling Pipeline</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              r.outers executes file operations, terminal commands, and interactive user prompts safely with real-time feedback.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-1.5">
              <span className="text-xs font-mono font-bold text-cyber-cyan">READ & WRITE</span>
              <p className="text-xs text-gray-400">
                <code className="text-gray-200 font-mono">RTS &gt; Reading &#123;file&#125; (120 lines)</code><br/>
                <code className="text-gray-200 font-mono">RTS &gt; Writing &#123;file&#125; (45 lines)</code>
              </p>
            </div>

            <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-1.5">
              <span className="text-xs font-mono font-bold text-cyber-yellow">SHELL EXECUTION</span>
              <p className="text-xs text-gray-400">
                <code className="text-gray-200 font-mono">⚡ RTS &gt; Running &#123;command&#125;</code><br/>
                Streams live stdout and stderr in real-time.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-1.5 md:col-span-2">
              <span className="text-xs font-mono font-bold text-cyber-pink">INTERACTIVE ASK_USER MODAL</span>
              <p className="text-xs text-gray-400">
                When the agent needs clarification or options, it renders a keyboard-navigable modal (<kbd className="px-1 py-0.5 rounded bg-[#090d16] font-mono text-[10px]">UP</kbd>/<kbd className="px-1 py-0.5 rounded bg-[#090d16] font-mono text-[10px]">DOWN</kbd> + <kbd className="px-1 py-0.5 rounded bg-[#090d16] font-mono text-[10px]">ENTER</kbd>) with custom text write-in fallback!
              </p>
            </div>
          </div>
        </section>
      )}

      {/* NVIDIA NIM & MODELS */}
      {activeSection === 'nvidia-nim' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-yellow uppercase font-bold tracking-wider">AI Infrastructure</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">NVIDIA NIM 80+ Model Router</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              Connect to NVIDIA NIM for industrial-grade enterprise inference speeds and access to cutting edge open-weights models.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-2">
            <h3 className="text-sm font-bold text-white">How to Get a Free NVIDIA NIM API Key</h3>
            <ol className="list-decimal list-inside text-xs text-gray-300 space-y-1.5 leading-relaxed">
              <li>Visit <a href="https://build.nvidia.com" target="_blank" rel="noreferrer" className="text-cyber-cyan underline">build.nvidia.com</a> and create a free account.</li>
              <li>Navigate to any model (e.g. <b>Nemotron-3 Super</b>) and click <b>Get API Key</b>.</li>
              <li>Run <code className="text-cyber-yellow font-mono">/setup</code> in r.outers and paste your API key (<code className="text-gray-400 font-mono">nvapi-...</code>).</li>
            </ol>
          </div>

          <div className="pt-2">
            <button
              onClick={() => onNavigateTab('models')}
              className="px-4 py-2 rounded-xl bg-cyber-yellow text-black text-xs font-bold flex items-center space-x-2"
            >
              <span>Explore All 80+ Models Catalog</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </section>
      )}

      {/* REASONING ENGINE */}
      {activeSection === 'reasoning-engine' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-purple uppercase font-bold tracking-wider">Chain of Thought</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Deep Reasoning Token Engine</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              r.outers natively parses <code className="text-cyber-purple font-mono">reasoning_content</code> from models like DeepSeek-R1 and GLM-5.3 with extended 180s HTTP timeout buffers.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-2">
            <h3 className="text-sm font-bold text-white">Zero-Timeout Architecture</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Reasoning models generate complex chain-of-thought tokens before returning the final solution. r.outers uses a dedicated 180-second keep-alive connection so your mobile Termux session never disconnects mid-thought.
            </p>
          </div>
        </section>
      )}

      {/* SKILLS SECTION */}
      {activeSection === 'skills' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-purple uppercase font-bold tracking-wider">Dynamic Plugins</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Anti-Slop & Prompt Skills</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              Enhance coding quality, eliminate boilerplate, and enforce design taste automatically.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-3">
            <h3 className="text-sm font-bold text-white">Anti-Slop Modes</h3>
            <ul className="space-y-2 text-xs text-gray-300">
              <li>• <b className="text-cyber-cyan">DURING:</b> Live filter applied during code generation to prevent generic AI tells from being written in the first place.</li>
              <li>• <b className="text-cyber-pink">AFTER:</b> Post-generation audit mode creating a numbered list of findings for selective refactoring.</li>
            </ul>
          </div>

          <div className="pt-2">
            <button
              onClick={() => onNavigateTab('skills')}
              className="px-4 py-2 rounded-xl bg-cyber-purple text-white text-xs font-bold flex items-center space-x-2"
            >
              <span>View Full Skill Catalog</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </section>
      )}

      {/* SLASH COMMANDS */}
      {activeSection === 'commands' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-cyber-yellow uppercase font-bold tracking-wider">Reference</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Slash Commands Cheatsheet</h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              Quick commands accessible anywhere in the interactive r.outers prompt.
            </p>
          </div>

          <div className="overflow-x-auto rounded-xl border border-cyber-border bg-cyber-card">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#090d16] text-gray-400 border-b border-cyber-border uppercase text-[10px]">
                <tr>
                  <th className="p-3">Command</th>
                  <th className="p-3">Usage</th>
                  <th className="p-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cyber-border/50 text-gray-300">
                <tr>
                  <td className="p-3 font-bold text-cyber-yellow">/setup</td>
                  <td className="p-3 text-gray-400">/setup</td>
                  <td className="p-3 font-sans">Configure API keys & provider routing</td>
                </tr>
                <tr>
                  <td className="p-3 font-bold text-cyber-cyan">/model</td>
                  <td className="p-3 text-gray-400">/model [id]</td>
                  <td className="p-3 font-sans">Switch or search active LLM model</td>
                </tr>
                <tr>
                  <td className="p-3 font-bold text-cyber-pink">/provider</td>
                  <td className="p-3 text-gray-400">/provider [nvidia|clouvia]</td>
                  <td className="p-3 font-sans">Switch AI provider backend</td>
                </tr>
                <tr>
                  <td className="p-3 font-bold text-cyber-purple">/skills</td>
                  <td className="p-3 text-gray-400">/skills</td>
                  <td className="p-3 font-sans">List active dynamic skills</td>
                </tr>
                <tr>
                  <td className="p-3 font-bold text-cyber-green">/add-skill</td>
                  <td className="p-3 text-gray-400">/add-skill &lt;url&gt;</td>
                  <td className="p-3 font-sans">Install skill from Git repo</td>
                </tr>
                <tr>
                  <td className="p-3 font-bold text-gray-300">/memory</td>
                  <td className="p-3 text-gray-400">/memory</td>
                  <td className="p-3 font-sans">View active context tokens & turns</td>
                </tr>
                <tr>
                  <td className="p-3 font-bold text-red-400">/clear</td>
                  <td className="p-3 text-gray-400">/clear</td>
                  <td className="p-3 font-sans">Reset conversation context window</td>
                </tr>
                <tr>
                  <td className="p-3 font-bold text-gray-400">/exit</td>
                  <td className="p-3 text-gray-400">/exit</td>
                  <td className="p-3 font-sans">Save history and exit CLI</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* FAQ & TROUBLESHOOTING */}
      {activeSection === 'faq' && (
        <section className="space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-mono text-gray-400 uppercase font-bold tracking-wider">Support</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Troubleshooting & FAQs</h1>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-1.5">
              <h3 className="text-sm font-bold text-white">Q: Cursor or terminal display looks strange after exit?</h3>
              <p className="text-xs text-gray-400">
                Run <code className="text-cyber-cyan font-mono">stty sane</code> or <code className="text-cyber-cyan font-mono">reset</code> in your terminal to restore standard terminal mode.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border space-y-1.5">
              <h3 className="text-sm font-bold text-white">Q: How do I upgrade r.outers to the latest version?</h3>
              <p className="text-xs text-gray-400">
                Simply re-run the 1-line installation script: <code className="text-cyber-pink font-mono">curl -sL https://raw.githubusercontent.com/myramm/r.outers/main/install.sh | bash</code>
              </p>
            </div>
          </div>
        </section>
      )}

    </div>
  );
};
