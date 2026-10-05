import express, { Request, Response } from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Serve static frontend in production
const distPath = path.join(__dirname, '..', 'dist');
app.use(express.static(distPath));

// 1. Health & Status
app.get('/api/status', (req: Request, res: Response) => {
  res.json({
    name: 'r.outers (rts)',
    version: '2.4.0',
    description: 'Autonomous AI Coding Agent for Android Termux & Linux',
    status: 'ONLINE',
    author: 'myramm (ラム)',
    muse: 'Akari Watanabe 🌸',
    default_model: 'nvidia/nemotron-3-super-120b-a12b',
    providers: ['nvidia', 'clouvia', 'atria', 'openai_compatible'],
    total_models_available: 84,
    runtime: 'Python 3.10+ / Linux & Android Termux',
    architecture: {
      tui: 'Raw Terminal Mode with Double-Line Prompt & History Buffer',
      tool_engine: 'Autonomous Live Exec with stdout/stderr streaming & ANSI Diffing',
      permission_system: 'Arrow-key Interactive Confirmation Modal'
    }
  });
});

// 2. Models Catalog
app.get('/api/models', (req: Request, res: Response) => {
  const models = [
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
      id: 'meta/llama-3.3-70b-instruct',
      name: 'Llama 3.3 70B Instruct',
      provider: 'NVIDIA NIM',
      category: 'General Purpose & Instruction',
      context: '128k',
      speed: 'High Throughput',
      tools: true,
      recommended: false,
      tags: ['Open-Weights', 'Creative & Code']
    },
    {
      id: 'mistralai/mistral-large-2407',
      name: 'Mistral Large 2',
      provider: 'NVIDIA NIM',
      category: 'Multilingual & Complex Systems',
      context: '128k',
      speed: 'Fast',
      tools: true,
      recommended: false,
      tags: ['Polyglot', '128k Context']
    },
    {
      id: 'qwen/qwen2.5-coder-32b-instruct',
      name: 'Qwen 2.5 Coder 32B',
      provider: 'NVIDIA NIM',
      category: 'Specialized Coding & Refactoring',
      context: '32k',
      speed: 'Very Fast',
      tools: true,
      recommended: true,
      tags: ['Python / Go / TS Master', 'Diffs']
    },
    {
      id: 'z-ai/glm-5.3',
      name: 'GLM 5.3 Reasoning',
      provider: 'NVIDIA NIM',
      category: 'Extended Reasoning Engine',
      context: '64k',
      speed: 'Deep Thinking',
      tools: true,
      recommended: false,
      tags: ['Reasoning Content Streaming']
    },
    {
      id: 'google/gemma-2-27b-it',
      name: 'Gemma 2 27B IT',
      provider: 'NVIDIA NIM',
      category: 'Compact Powerhouse',
      context: '8k',
      speed: 'Instant',
      tools: true,
      recommended: false,
      tags: ['Google Tech', 'Clean Syntax']
    }
  ];
  res.json({ count: models.length, models });
});

// 3. Skills Catalog
app.get('/api/skills', (req: Request, res: Response) => {
  const skills = [
    {
      name: 'antislop',
      author: 'Official',
      description: 'Anti Slop: Core filter to eliminate generic AI patterns, fake copy, and boilerplate.',
      modes: ['DURING (Live filter while coding)', 'AFTER (Post-audit numbered checklist)'],
      category: 'Quality & Aesthetics'
    },
    {
      name: 'superpowers',
      author: 'Community',
      description: 'Dynamic meta-skills framework providing systematic debugging, planning, and TDD.',
      modes: ['Automatic Invocation', 'Subagent Dispatch'],
      category: 'Core Agentic'
    },
    {
      name: 'apktool',
      author: 'myramm',
      description: 'Android APK unpacking, resource extraction, smali bytecode modification, and rebuilding.',
      modes: ['Smali Patches', 'Manifest Decompile'],
      category: 'Reverse Engineering'
    },
    {
      name: 'design-taste-frontend',
      author: 'Official',
      description: 'Anti-slop frontend engine for high-end landing pages, luxury palettes, and motion layouts.',
      modes: ['Design Read Inference', 'Dial Tuning (Variance/Motion/Density)'],
      category: 'UI/UX Engineering'
    },
    {
      name: 'test-driven-development',
      author: 'Official',
      description: 'Enforces red-green-refactor cycle before touching implementation code.',
      modes: ['Pre-implementation Test Verification'],
      category: 'Code Quality'
    },
    {
      name: 'systematic-debugging',
      author: 'Official',
      description: 'Root cause isolation without speculative guesswork or blind fixes.',
      modes: ['Hypothesis Testing', 'Minimal Reproductions'],
      category: 'Reliability'
    }
  ];
  res.json({ count: skills.length, skills });
});

// 4. Slash Commands Reference
app.get('/api/commands', (req: Request, res: Response) => {
  const commands = [
    {
      command: '/setup',
      description: 'Run interactive API key & provider configuration wizard (NVIDIA, Clouvia, Atria).',
      usage: '/setup',
      example: 'r.outers > /setup'
    },
    {
      command: '/model',
      description: 'Switch active LLM model with optional fuzzy search or direct ID.',
      usage: '/model [model_id_or_search]',
      example: 'r.outers > /model nemotron'
    },
    {
      command: '/provider',
      description: 'Switch between NVIDIA NIM, Clouvia, Atria, or custom OpenAI endpoint.',
      usage: '/provider [nvidia|clouvia|atria]',
      example: 'r.outers > /provider nvidia'
    },
    {
      command: '/skills',
      description: 'List all currently active skills and view system prompt injections.',
      usage: '/skills',
      example: 'r.outers > /skills'
    },
    {
      command: '/add-skill',
      description: 'Download and register a new skill from a GitHub repository or URL.',
      usage: '/add-skill <repo_url>',
      example: 'r.outers > /add-skill https://github.com/myramm/apktool-skill'
    },
    {
      command: '/memory',
      description: 'Display active context tokens, conversation history size, and loaded memory.',
      usage: '/memory',
      example: 'r.outers > /memory'
    },
    {
      command: '/clear',
      description: 'Wipe conversation history and reset context window while keeping active model & skills.',
      usage: '/clear',
      example: 'r.outers > /clear'
    },
    {
      command: '/exit',
      description: 'Gracefully exit r.outers CLI and save persistent shell history.',
      usage: '/exit or Ctrl+C / Ctrl+D',
      example: 'r.outers > /exit'
    }
  ];
  res.json({ count: commands.length, commands });
});

// 5. Terminal Simulator Endpoint
app.post('/api/terminal/execute', (req: Request, res: Response) => {
  const { input, currentModel = 'nvidia/nemotron-3-super-120b-a12b', currentProvider = 'nvidia' } = req.body;
  const trimmed = (input || '').trim();

  if (!trimmed) {
    return res.json({ output: '', newModel: currentModel, newProvider: currentProvider });
  }

  // Handle slash commands
  if (trimmed === '/help') {
    return res.json({
      output: `\x1b[36m╭─── r.outers (rts) Command Cheatsheet ──────────────────────────────╮\x1b[0m
│ \x1b[33m/setup\x1b[0m      Configure API keys and providers (NVIDIA NIM / Clouvia)
│ \x1b[33m/model\x1b[0m      Switch active AI model or search 80+ NIM models
│ \x1b[33m/provider\x1b[0m   Switch active AI provider routing
│ \x1b[33m/skills\x1b[0m     List active skill prompt extensions
│ \x1b[33m/add-skill\x1b[0m  Install new skill from Git repository
│ \x1b[33m/memory\x1b[0m     View active conversation token usage
│ \x1b[33m/clear\x1b[0m      Reset conversation context
│ \x1b[33m/exit\x1b[0m       Exit agent session
\x1b[36m╰───────────────────────────────────────────────────────────────────╯\x1b[0m`,
      newModel: currentModel,
      newProvider: currentProvider
    });
  }

  if (trimmed === '/skills') {
    return res.json({
      output: `\x1b[35m[🧩 Active Skills Loaded]\x1b[0m
 1. \x1b[1manti-slop\x1b[0m (DURING mode active) — Filters out boilerplate & AI clichés.
 2. \x1b[1msystematic-debugging\x1b[0m — Root cause diagnosis before code changes.
 3. \x1b[1mapktool-modding\x1b[0m — Android smali bytecode & APK decompilation engine.`,
      newModel: currentModel,
      newProvider: currentProvider
    });
  }

  if (trimmed.startsWith('/model')) {
    const arg = trimmed.replace('/model', '').trim();
    if (!arg) {
      return res.json({
        output: `\x1b[36mActive Model:\x1b[0m \x1b[33m${currentModel}\x1b[0m
Type \x1b[1m/model <name>\x1b[0m to switch (e.g. \x1b[32m/model nemotron\x1b[0m, \x1b[32m/model gpt-oss-20b\x1b[0m, \x1b[32m/model deepseek-r1\x1b[0m)`,
        newModel: currentModel,
        newProvider: currentProvider
      });
    }
    const targetModel = arg.includes('/') ? arg : `nvidia/${arg}`;
    return res.json({
      output: `\x1b[32m✔ Model successfully switched to:\x1b[0m \x1b[1m${targetModel}\x1b[0m`,
      newModel: targetModel,
      newProvider: currentProvider
    });
  }

  if (trimmed.startsWith('/provider')) {
    const prov = trimmed.replace('/provider', '').trim().toLowerCase() || 'nvidia';
    return res.json({
      output: `\x1b[32m✔ Provider switched to:\x1b[0m \x1b[1m${prov.toUpperCase()}\x1b[0m`,
      newModel: currentModel,
      newProvider: prov
    });
  }

  if (trimmed === '/memory') {
    return res.json({
      output: `\x1b[36m[🧠 Memory Telemetry]\x1b[0m
 Context Window : 128,000 tokens
 History Depth  : 4 message turns
 Active Buffer  : 3,420 tokens (2.6% used)
 Skills Payload : 1,280 tokens`,
      newModel: currentModel,
      newProvider: currentProvider
    });
  }

  if (trimmed === '/clear') {
    return res.json({
      output: `\x1b[33m✔ Conversation history and context window reset to clean slate.\x1b[0m`,
      newModel: currentModel,
      newProvider: currentProvider
    });
  }

  // Simulated AI response with autonomous tool calls
  const isCode = trimmed.toLowerCase().includes('buat') || trimmed.toLowerCase().includes('code') || trimmed.toLowerCase().includes('create') || trimmed.toLowerCase().includes('file');
  
  if (isCode) {
    return res.json({
      output: `\x1b[35mRTS > Planning project architecture...\x1b[0m
\x1b[33mRTS > Writing main.py (38 lines)\x1b[0m
\x1b[36m⚡ RTS > Running python3 main.py\x1b[0m
\x1b[32m[Live Output] Server listening on http://127.0.0.1:8000\x1b[0m
\x1b[32m✔ RTS > Completed task successfully!\x1b[0m

Kode telah selesai diimplementasikan dan diverifikasi berjalan lancar! Ada yang ingin ditambahkan? 🚀`,
      newModel: currentModel,
      newProvider: currentProvider
    });
  }

  return res.json({
    output: `\x1b[35mRTS > Thinking...\x1b[0m
Halo! Saya \x1b[1mr.outers (rts)\x1b[0m — autonomous AI coding agent untuk Android Termux & Linux.
Saya siap membantu menulis kode, merestrukturisasi proyek, menjalankan terminal command, atau membongkar APK.

Ketik \x1b[33m/help\x1b[0m untuk melihat daftar perintah slash.`,
    newModel: currentModel,
    newProvider: currentProvider
  });
});

// 6. Global Search
app.get('/api/search', (req: Request, res: Response) => {
  const query = ((req.query.q as string) || '').toLowerCase();
  const database = [
    { title: 'Quickstart & Installation', section: 'getting-started', snippet: 'Install r.outers in 1 line via curl on Termux or Linux VPS.' },
    { title: 'NVIDIA NIM Provider', section: 'providers', snippet: 'Configure 80+ cutting edge LLM models including Nemotron-3, DeepSeek R1.' },
    { title: 'Interactive Keyboard Navigation', section: 'features', snippet: 'Use UP and DOWN arrow keys to cycle through persistent history.' },
    { title: 'Tool Calling & Live Shell', section: 'tools', snippet: 'Live stdout and stderr streaming for run_command with confirmation modal.' },
    { title: 'Anti-Slop Skill', section: 'skills', snippet: 'Prevent generic AI fluff and enforce high-end design and coding standards.' },
    { title: 'Slash Commands Reference', section: 'commands', snippet: 'Full documentation for /setup, /model, /skills, /add-skill, /memory.' },
    { title: 'Android Termux Optimization', section: 'termux', snippet: 'Lightweight zero-lag terminal raw mode designed for mobile screens.' }
  ];

  const results = database.filter(item => 
    item.title.toLowerCase().includes(query) || 
    item.snippet.toLowerCase().includes(query) ||
    item.section.toLowerCase().includes(query)
  );

  res.json({ results });
});

// SPA fallback for all other routes in production
app.get('*', (req: Request, res: Response) => {
  res.sendFile(path.join(distPath, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 r.outers Fullstack Docs Backend listening on port ${PORT}`);
});
