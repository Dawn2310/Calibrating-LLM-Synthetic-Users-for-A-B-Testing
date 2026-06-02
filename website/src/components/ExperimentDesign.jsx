import React from 'react';
import { motion } from 'framer-motion';

export default function ExperimentDesign() {
  return (
    <section id="design" className="section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title">Experiment Design</h2>
        <p className="section-subtitle">A multi-phase evaluation protocol enforcing rigorous counterbalancing.</p>

        <div className="grid lg:grid-cols-3 gap-6 mt-12">
          <div className="glass-card p-6 flex flex-col justify-between">
            <div>
              <div className="text-cyan-400 font-bold mb-2">Phase 1: Pilot</div>
              <h3 className="text-xl font-bold text-white mb-3">Basic Prompting</h3>
              <p className="text-slate-400 text-sm">Baseline test cases using zero-shot prompting without personas or strict counterbalancing. Used to establish initial variance.</p>
            </div>
            <div className="mt-6 text-sm font-mono text-slate-500">~2,000 API Calls</div>
          </div>
          
          <div className="glass-card p-6 flex flex-col justify-between border-t-2 border-t-indigo-500">
            <div>
              <div className="text-indigo-400 font-bold mb-2">Phase 2: Main Evaluation</div>
              <h3 className="text-xl font-bold text-white mb-3">Persona & Ensemble</h3>
              <p className="text-slate-400 text-sm">Full implementation of the pipeline across 4 models, utilizing varied persona depths (demographic, biographical, interview-style).</p>
            </div>
            <div className="mt-6 text-sm font-mono text-slate-500">~25,000 API Calls</div>
          </div>

          <div className="glass-card p-6 flex flex-col justify-between">
            <div>
              <div className="text-purple-400 font-bold mb-2">Phase 3: Position Bias</div>
              <h3 className="text-xl font-bold text-white mb-3">Counterbalance Verification</h3>
              <p className="text-slate-400 text-sm">Targeted experiment swapping Variant A and B in the prompt to measure and isolate position bias directly.</p>
            </div>
            <div className="mt-6 text-sm font-mono text-slate-500">~5,000 API Calls</div>
          </div>
        </div>
        
        <div className="mt-12 glass-card p-8 bg-slate-900/40">
          <h3 className="text-xl font-bold text-white mb-6 text-center">The Position Bias Problem</h3>
          <div className="flex flex-col md:flex-row items-center justify-center gap-8">
            <div className="flex-1 border border-white/10 rounded-xl p-4 bg-white/5 text-center w-full">
              <div className="text-sm text-slate-400 mb-2">Order 1 (Original)</div>
              <div className="flex justify-center gap-2 font-mono">
                <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded">Variant A</span>
                <span className="text-slate-500">vs</span>
                <span className="px-3 py-1 bg-amber-500/20 text-amber-300 rounded">Variant B</span>
              </div>
            </div>
            <div className="hidden md:block text-slate-500 font-bold">AND</div>
            <div className="flex-1 border border-white/10 rounded-xl p-4 bg-white/5 text-center w-full">
              <div className="text-sm text-slate-400 mb-2">Order 2 (Swapped)</div>
              <div className="flex justify-center gap-2 font-mono">
                <span className="px-3 py-1 bg-amber-500/20 text-amber-300 rounded">Variant B</span>
                <span className="text-slate-500">vs</span>
                <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded">Variant A</span>
              </div>
            </div>
          </div>
          <p className="text-center text-slate-400 mt-6 text-sm max-w-2xl mx-auto">
            By querying both permutations and enforcing agreement (the model must choose Variant A regardless of its position), we effectively neutralize position bias.
          </p>
        </div>
      </motion.div>
    </section>
  );
}
