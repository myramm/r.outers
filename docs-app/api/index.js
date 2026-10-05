import express from 'express';
import cors from 'cors';

const app = express();

app.use(cors());
app.use(express.json());

// 1. Health & Status
app.get('/api/status', (req, res) => {
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
    config_file: '~/.routers_config.json'
  });
});

// 2. Models Catalog
app.get('/api/models', (req, res) => {
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
    }
  ];
  res.json({ count: models.length, models });
});

// 3. Skills Catalog
app.get('/api/skills', (req, res) => {
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
    }
  ];
  res.json({ count: skills.length, skills });
});

// 4. Slash Commands Reference
app.get('/api/commands', (req, res) => {
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
app.post('/api/terminal/execute', (req, res) => {
  const { input, currentModel = 'nvidia/nemotron-3-super-120b-a12b', currentProvider = 'nvidia' } = req.body;
  const trimmed = (input || '').trim();

  if (!trimmed) {
    return res.json({ output: '', newModel: currentModel, newProvider: currentProvider });
  }

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
        output: `\x1b[36mActive Model:\x1b[0m \x1b[33m${currentModel}\x1b[0m\nType \x1b[1m/model <name>\x1b[0m to switch (e.g. \x1b[32m/model nemotron\x1b[0m)`,
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
 Active Buffer  : 3,420 tokens (2.6% used)`,
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

  // Simulated code response
  return res.json({
    output: `\x1b[35mRTS > Planning project architecture...\x1b[0m
\x1b[33mRTS > Writing main.py (38 lines)\x1b[0m
\x1b[36m⚡ RTS > Running python3 main.py\x1b[0m
\x1b[32m✔ RTS > Completed task successfully!\x1b[0m

Perintah berhasil dijalankan! Konfigurasi manual tersimpan di ~/.routers_config.json 🚀`,
    newModel: currentModel,
    newProvider: currentProvider
  });
});

export default app;
