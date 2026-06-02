import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check, BookOpen } from 'lucide-react';

export default function Citation() {
  const [copied, setCopied] = useState(false);
  const citationCode = `@article{csup2026,
  title     = {From Synthetic Users to Calibrated Instruments: Decomposing Uncertainty in LLM-Based A/B Testing},
  author    = {Nguyen Luong Hai Dang and Duong Quoc Huu},
  journal   = {Preprint},
  year      = {2026}
}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(citationCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="citation" className="section-container pb-32">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <div className="glass-card p-8 md:p-12 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl"></div>
          
          <div className="relative z-10">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-4 bg-indigo-500/20 rounded-2xl">
                <BookOpen className="w-8 h-8 text-indigo-400" />
              </div>
              <div>
                <h2 className="text-3xl font-bold text-white mb-1">Citation & License</h2>
                <p className="text-slate-400">If you use CSUP in your research, please cite our paper.</p>
              </div>
            </div>

            <div className="relative group mt-8 rounded-xl overflow-hidden bg-[#0a0f1d] border border-white/10 shadow-2xl">
              <pre className="p-6 overflow-x-auto font-mono text-sm text-cyan-300">
                {citationCode}
              </pre>
              <button 
                onClick={handleCopy}
                className="absolute top-4 right-4 p-2 rounded-lg bg-white/10 border border-white/10 text-white hover:bg-white/20 transition-all opacity-0 group-hover:opacity-100"
              >
                {copied ? <Check className="w-5 h-5 text-green-400" /> : <Copy className="w-5 h-5" />}
              </button>
            </div>

            <div className="mt-8 flex items-center justify-center">
              <div className="px-4 py-2 rounded-full border border-slate-700 bg-slate-800/50 text-slate-300 text-sm font-medium flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                Released under the MIT License
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
