import React, { useState } from 'react';
import { Code2, Play, Check, Copy, ArrowRight, Activity, Server, Clock } from 'lucide-react';
import { CodeBlock } from './CodeBlock';

export const ApiPlayground: React.FC = () => {
  const [activeEndpoint, setActiveEndpoint] = useState('/api/status');
  const [method, setMethod] = useState<'GET' | 'POST'>('GET');
  const [postBody, setPostBody] = useState(JSON.stringify({ input: '/skills' }, null, 2));
  const [responseJson, setResponseJson] = useState<string>('Click "Send Request" to fetch live response...');
  const [statusCode, setStatusCode] = useState<number | null>(null);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const endpoints = [
    { path: '/api/status', method: 'GET', desc: 'Agent health, active version, and architecture' },
    { path: '/api/models', method: 'GET', desc: 'Complete list of supported NVIDIA NIM models' },
    { path: '/api/skills', method: 'GET', desc: 'Active dynamic prompt skill extensions' },
    { path: '/api/commands', method: 'GET', desc: 'Slash commands reference & usage specs' },
    { path: '/api/terminal/execute', method: 'POST', desc: 'Simulate autonomous agent prompt run' }
  ];

  const handleSelectEndpoint = (ep: typeof endpoints[0]) => {
    setActiveEndpoint(ep.path);
    setMethod(ep.method as 'GET' | 'POST');
    if (ep.method === 'POST') {
      setPostBody(JSON.stringify({ input: 'Buatkan script python crawler', currentModel: 'nvidia/nemotron-3-super-120b-a12b' }, null, 2));
    }
  };

  const handleSendRequest = async () => {
    setLoading(true);
    const start = performance.now();
    try {
      const options: RequestInit = {
        method,
        headers: { 'Content-Type': 'application/json' }
      };
      if (method === 'POST') {
        options.body = postBody;
      }

      const res = await fetch(activeEndpoint, options);
      const data = await res.json();
      const end = performance.now();

      setStatusCode(res.status);
      setResponseTime(Math.round(end - start));
      setResponseJson(JSON.stringify(data, null, 2));
    } catch (err: any) {
      setStatusCode(500);
      setResponseJson(JSON.stringify({ error: err.message }, null, 2));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-[#0d1628] via-[#101e28] to-[#0c1c24] border border-cyber-border">
        <div className="flex items-center space-x-2 text-cyber-green text-xs font-mono font-bold uppercase tracking-wider mb-2">
          <Server className="w-4 h-4" />
          <span>Fullstack Express Backend API</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">Interactive REST API Explorer</h1>
        <p className="text-gray-400 text-sm max-w-2xl mt-1">
          Query the documentation backend in real-time. All responses are served dynamically via JSON endpoints.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left: Endpoint Picker */}
        <div className="lg:col-span-1 space-y-2">
          <span className="text-xs font-mono uppercase text-gray-400 font-bold px-1">Available Endpoints</span>
          <div className="space-y-2">
            {endpoints.map((ep, idx) => {
              const isSelected = activeEndpoint === ep.path;
              return (
                <div
                  key={idx}
                  onClick={() => handleSelectEndpoint(ep)}
                  className={`p-3.5 rounded-xl cursor-pointer border transition-all ${
                    isSelected
                      ? 'bg-cyber-card border-cyber-green/50 shadow-md shadow-emerald-500/5'
                      : 'bg-[#090d16] border-cyber-border hover:bg-cyber-card/60'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                      ep.method === 'GET' ? 'bg-cyber-cyan/20 text-cyber-cyan border border-cyber-cyan/30' : 'bg-cyber-pink/20 text-cyber-pink border border-cyber-pink/30'
                    }`}>
                      {ep.method}
                    </span>
                    <span className="font-mono text-xs font-semibold text-gray-200">{ep.path}</span>
                  </div>
                  <p className="text-[11px] text-gray-400 mt-1.5 line-clamp-1">{ep.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Request & Response Console */}
        <div className="lg:col-span-2 space-y-4">
          
          {/* Request Header Bar */}
          <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center space-x-2 w-full sm:w-auto font-mono text-xs">
              <span className={`px-2.5 py-1 rounded font-bold ${method === 'GET' ? 'bg-cyber-cyan/20 text-cyber-cyan' : 'bg-cyber-pink/20 text-cyber-pink'}`}>
                {method}
              </span>
              <span className="text-gray-100 font-semibold">{activeEndpoint}</span>
            </div>

            <button
              onClick={handleSendRequest}
              disabled={loading}
              className="w-full sm:w-auto px-4 py-2 rounded-lg bg-cyber-green text-black font-semibold text-xs flex items-center justify-center space-x-1.5 hover:bg-emerald-400 disabled:opacity-50 transition-all shadow-md"
            >
              <Play className="w-3.5 h-3.5 fill-black" />
              <span>{loading ? 'Sending...' : 'Send Request'}</span>
            </button>
          </div>

          {/* If POST, show payload editor */}
          {method === 'POST' && (
            <div className="p-4 rounded-xl bg-[#090d16] border border-cyber-border space-y-2">
              <span className="text-xs font-mono text-gray-400 font-bold block">JSON Request Payload:</span>
              <textarea
                value={postBody}
                onChange={e => setPostBody(e.target.value)}
                rows={4}
                className="w-full bg-[#05080f] font-mono text-xs p-3 rounded-lg border border-cyber-border text-gray-200 focus:outline-none focus:border-cyber-cyan/50"
              />
            </div>
          )}

          {/* Response Box */}
          <div className="p-4 rounded-xl bg-[#070a10] border border-cyber-border space-y-3">
            <div className="flex items-center justify-between border-b border-cyber-border/60 pb-2.5 text-xs font-mono">
              <span className="text-gray-400 flex items-center">
                <Activity className="w-3.5 h-3.5 mr-1.5 text-cyber-green" /> Response Output
              </span>

              {statusCode !== null && (
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${statusCode >= 200 && statusCode < 300 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                    Status: {statusCode} OK
                  </span>
                  <span className="text-gray-400 flex items-center">
                    <Clock className="w-3 h-3 mr-1" /> {responseTime} ms
                  </span>
                </div>
              )}
            </div>

            <pre className="font-mono text-xs text-gray-200 overflow-x-auto max-h-96 p-2 bg-[#05080f] rounded-lg border border-cyber-border/40 leading-relaxed">
              <code>{responseJson}</code>
            </pre>
          </div>

        </div>

      </div>

    </div>
  );
};
