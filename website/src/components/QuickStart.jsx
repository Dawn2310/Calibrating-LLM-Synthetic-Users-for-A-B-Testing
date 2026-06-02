import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Copy, Check } from 'lucide-react';

const CodeBlock = ({ label, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mb-6">
      <h4 className="text-sm font-semibold text-cyan-400 mb-2 px-1 uppercase tracking-wider">{label}</h4>
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
};

export default function QuickStart() {
  return (
    <section id="quickstart" className="section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Quick Start</h2>
        <p className="section-subtitle text-center mx-auto">Replicate our experiments or run CSUP on your own A/B testing corpora.</p>
        
        <div className="grid lg:grid-cols-2 gap-8 mt-12">
          <div className="glass-card p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6">
              <Terminal className="w-6 h-6 text-indigo-400" />
              <h3 className="text-xl font-bold text-white">1. Setup Environment</h3>
            </div>
            
            <CodeBlock 
              label="Install Dependencies" 
              code={`pip install openai anthropic groq pandas tqdm`} 
            />
            
            <CodeBlock 
              label="Set API Keys" 
              code={`export OPENAI_API_KEY="your-key"\nexport ANTHROPIC_API_KEY="your-key"\nexport GROQ_API_KEY="your-key"\nexport DEEPSEEK_API_KEY="your-key"`} 
            />
            
            <CodeBlock 
              label="Initialize Database" 
              code={`python scripts/pipeline.py --init`} 
            />
          </div>

          <div className="glass-card p-6 md:p-8">
            <div className="flex items-center gap-3 mb-6">
              <Terminal className="w-6 h-6 text-cyan-400" />
              <h3 className="text-xl font-bold text-white">2. Run Experiments</h3>
            </div>
            
            <CodeBlock 
              label="Run Phases (1 = Pilot, 2 = Main, 3 = Position Bias)" 
              code={`python scripts/pipeline.py --phase 2`} 
            />
            
            <CodeBlock 
              label="Export Data" 
              code={`python scripts/db_to_csv.py`} 
            />
            
            <CodeBlock 
              label="Analyze Reliability & SURS" 
              code={`python scripts/csup_analysis.py`} 
            />
          </div>
        </div>
      </motion.div>
    </section>
  );
}
