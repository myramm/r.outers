import React, { useState, useEffect } from 'react';
import { Layers, Sparkles, Shield, Code, CheckCircle, ArrowRight, Download, BookOpen } from 'lucide-react';
import { CodeBlock } from './CodeBlock';

export const SkillCatalog: React.FC = () => {
  const [skills, setSkills] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/skills')
      .then(res => res.json())
      .then(data => setSkills(data.skills || []))
      .catch(() => {
        setSkills([
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
        ]);
      });
  }, []);

  const sampleSkillYaml = `---
name: custom-audit
description: Custom code security and performance audit skill
---

# Custom Audit Skill Rules
1. Never leave plaintext credentials or private keys in source code.
2. Ensure all external user inputs are validated and sanitized.
3. Keep memory allocation minimal on mobile Termux runtimes.`;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      
      {/* Header Banner */}
      <div className="relative rounded-2xl p-6 md:p-8 bg-gradient-to-r from-[#170e28] via-[#101426] to-[#0c1824] border border-cyber-border overflow-hidden">
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-cyber-purple text-xs font-mono font-bold uppercase tracking-wider">
            <Sparkles className="w-4 h-4 fill-cyber-purple" />
            <span>Extensible Agent Architecture</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Dynamic Skill & Anti-Slop Ecosystem
          </h1>
          <p className="text-gray-400 text-sm max-w-2xl leading-relaxed">
            Skills are lightweight markdown instructions and prompt hooks that dynamically enhance r.outers capabilities without requiring code rebuilds.
          </p>
        </div>
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {skills.map((skill, idx) => (
          <div key={idx} className="p-6 rounded-2xl bg-cyber-card border border-cyber-border hover:border-cyber-purple/50 transition-all shadow-lg flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="p-2 rounded-xl bg-cyber-purple/20 text-cyber-purple border border-cyber-purple/30">
                    <Layers className="w-4 h-4" />
                  </span>
                  <h3 className="font-bold text-gray-100 text-base">{skill.name}</h3>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#090d16] text-gray-400 border border-cyber-border">
                  {skill.category}
                </span>
              </div>

              <p className="text-sm text-gray-300 leading-relaxed">
                {skill.description}
              </p>

              <div className="space-y-1.5 pt-2">
                <span className="text-[10px] uppercase font-mono text-gray-500 font-bold block">Supported Modes:</span>
                <div className="flex flex-wrap gap-1.5">
                  {skill.modes.map((mode: string, mIdx: number) => (
                    <span key={mIdx} className="text-xs font-mono px-2.5 py-1 rounded-md bg-[#090d16] text-cyber-cyan border border-cyber-border">
                      {mode}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-cyber-border/60 flex items-center justify-between text-xs font-mono">
              <span className="text-gray-500">Author: {skill.author}</span>
              <span className="text-cyber-green flex items-center">
                <CheckCircle className="w-3.5 h-3.5 mr-1" /> Active in CLI
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* How to create a new skill section */}
      <div className="p-6 md:p-8 rounded-2xl bg-[#0d121f] border border-cyber-border space-y-4">
        <div className="flex items-center space-x-2">
          <Code className="w-5 h-5 text-cyber-cyan" />
          <h2 className="text-lg font-bold text-white">How to Create and Install Custom Skills</h2>
        </div>
        <p className="text-sm text-gray-300 leading-relaxed">
          You can create a custom skill by placing a <code className="text-cyber-pink font-mono">SKILL.md</code> file in <code className="text-cyber-cyan font-mono">~/.agents/skills/your-skill-name/SKILL.md</code> or install it directly via Git:
        </p>

        <CodeBlock
          filename="SKILL.md"
          language="yaml"
          code={sampleSkillYaml}
        />

        <div className="pt-2">
          <span className="text-xs font-mono text-gray-400 block mb-2">Install via r.outers CLI:</span>
          <CodeBlock
            language="bash"
            code="r.outers > /add-skill https://github.com/myramm/apktool-skill"
          />
        </div>
      </div>

    </div>
  );
};
