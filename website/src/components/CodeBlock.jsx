import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export default function CodeBlock({ label, code }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mb-6">
      {label && <h4 className="text-sm font-semibold text-cyan-400 mb-2 px-1 uppercase tracking-wider">{label}</h4>}
      <div className="relative group rounded-xl overflow-hidden bg-[#0d1326] border border-white/10 shadow-lg">
        <div className="absolute top-0 w-full h-8 bg-white/5 border-b border-white/5 flex items-center px-4">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
          </div>
        </div>
        <pre className="p-4 pt-12 overflow-x-auto font-mono text-sm text-slate-300 whitespace-pre-wrap">
          {code}
        </pre>
        <button 
          onClick={handleCopy}
          className="absolute top-10 right-3 p-2 rounded-lg bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:bg-white/10 transition-all opacity-0 group-hover:opacity-100"
          aria-label="Copy code"
        >
          {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}
