import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function Problem() {
  return (
    <section id="problem" className="section-container pt-32">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
      >
        <h2 className="section-title text-center">The Research Question</h2>
        <p className="section-subtitle text-center mx-auto text-xl text-slate-300">
          "Can LLM synthetic users produce reliable A/B test signals — and how do we know when they can't?"
        </p>

        <div className="grid md:grid-cols-2 gap-8 mt-16">
          <div className="glass-card p-8 border-t-4 border-t-red-500/50 hover:bg-slate-800/50 transition-colors">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-red-500/10 rounded-xl">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <h3 className="text-2xl font-bold text-white">The Flawed Assumption</h3>
            </div>
            <p className="text-slate-300 leading-relaxed mb-4">
              Many researchers treat LLMs as a <span className="text-white font-medium">clean preference generator</span>. They prompt the model once and assume the output reflects a stable, human-like judgment.
            </p>
            <ul className="space-y-3 text-slate-400">
              <li className="flex items-start gap-2">
                <span className="text-red-400 mt-1">✗</span>
                Ignores position bias (A vs B order)
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-400 mt-1">✗</span>
                Susceptible to prompt wording changes
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-400 mt-1">✗</span>
                Vulnerable to sampling variance
              </li>
            </ul>
          </div>

          <div className="glass-card p-8 border-t-4 border-t-cyan-500/50 hover:bg-slate-800/50 transition-colors">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-cyan-500/10 rounded-xl">
                <CheckCircle2 className="w-8 h-8 text-cyan-400" />
              </div>
              <h3 className="text-2xl font-bold text-white">Our Approach: Noisy Measurement</h3>
            </div>
            <p className="text-slate-300 leading-relaxed mb-4">
              We treat the LLM as a <span className="text-white font-medium">noisy instrument</span>. By decomposing the variance across multiple dimensions, we can isolate the true semantic design signal from the noise.
            </p>
            <ul className="space-y-3 text-slate-400">
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 mt-1">✓</span>
                Counterbalance presentation order
              </li>
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 mt-1">✓</span>
                Ensemble across multiple LLM families
              </li>
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 mt-1">✓</span>
                Quantify reliability via SURS metric
              </li>
            </ul>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
