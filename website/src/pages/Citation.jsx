import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, GitBranch } from 'lucide-react';
import CodeBlock from '../components/CodeBlock';
import PageNavigation from '../components/PageNavigation';

export default function Citation() {
  const citationCode = `@article{csup2026,
  title     = {From Synthetic Users to Calibrated Instruments: Decomposing Uncertainty in LLM-Based A/B Testing},
  author    = {Nguyen Luong Hai Dang and Duong Quoc Huu},
  journal   = {Preprint},
  year      = {2026}
}`;

  return (
    <div className="pt-32 pb-20 section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        <div className="glass-card p-8 md:p-12 relative overflow-hidden mb-8">
          <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl"></div>
          
          <div className="relative z-10">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-4 bg-indigo-500/20 rounded-2xl">
                <BookOpen className="w-8 h-8 text-indigo-400" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">Citation & License</h1>
                <p className="text-slate-400">Please cite our work if you use CSUP in your research.</p>
              </div>
            </div>

            <div className="mt-8">
              <CodeBlock label="BibTeX Citation" code={citationCode} />
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="glass-card p-6 flex flex-col items-center text-center justify-center">
            <GitBranch className="w-8 h-8 text-white mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Open Source Repository</h3>
            <p className="text-slate-400 text-sm mb-6">
              The full CSUP codebase, analysis scripts, and cleaned datasets are publicly available.
            </p>
            <a href="https://github.com/Dawn2310/Calibrating-LLM-Synthetic-Users-for-A-B-Testing" target="_blank" rel="noopener noreferrer" className="secondary-button text-sm">View on GitHub</a>
          </div>

          <div className="glass-card p-6 flex flex-col justify-center">
            <h3 className="text-xl font-bold text-white mb-4 text-center">Authors</h3>
            <ul className="space-y-4">
              <li className="flex items-center gap-4 p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">N</div>
                <div>
                  <div className="text-white font-medium">Nguyen Luong Hai Dang</div>
                  <div className="text-xs text-slate-400">Lead Researcher</div>
                </div>
              </li>
              <li className="flex items-center gap-4 p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">D</div>
                <div>
                  <div className="text-white font-medium">Duong Quoc Huu</div>
                  <div className="text-xs text-slate-400">Co-Researcher</div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <PageNavigation 
          prev={{ name: 'Documentation', path: '/docs' }} 
        />
      </motion.div>
    </div>
  );
}
