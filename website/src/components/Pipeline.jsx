import React from 'react';
import { motion } from 'framer-motion';
import { Users, RefreshCw, Repeat, Layers, ShieldCheck, CheckCircle } from 'lucide-react';

export default function Pipeline() {
  const steps = [
    { id: 1, title: 'Persona Simulation', desc: 'Inject diverse demographic & context profiles', icon: <Users className="w-6 h-6" /> },
    { id: 2, title: 'Counterbalancing', desc: 'Swap Variant A/B order to nullify position bias', icon: <RefreshCw className="w-6 h-6" /> },
    { id: 3, title: 'Repeat Sampling', desc: 'Query multiple times to capture temperature variance', icon: <Repeat className="w-6 h-6" /> },
    { id: 4, title: 'Multi-Model Ensemble', desc: 'Aggregate across distinct LLM families', icon: <Layers className="w-6 h-6" /> },
    { id: 5, title: 'SURS Calculation', desc: 'Compute Synthetic User Reliability Score', icon: <ShieldCheck className="w-6 h-6" /> },
    { id: 6, title: 'Reliability Decision', desc: 'Trust, cautiously use, or escalate to human testing', icon: <CheckCircle className="w-6 h-6" /> },
  ];

  return (
    <section id="pipeline" className="section-container relative">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
      >
        <h2 className="section-title">The CSUP Pipeline</h2>
        <p className="section-subtitle">A robust, 6-stage architecture to isolate true semantic preference from systemic LLM noise.</p>

        <div className="relative mt-16">
          {/* Connecting line */}
          <div className="absolute top-1/2 left-0 w-full h-1 bg-gradient-to-r from-cyan-500/20 via-indigo-500/50 to-purple-500/20 -translate-y-1/2 hidden lg:block rounded-full"></div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 relative z-10">
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                className="glass-card p-6 flex flex-col items-center text-center hover:-translate-y-2 transition-transform duration-300 relative group"
              >
                <div className="w-12 h-12 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center text-cyan-400 mb-4 group-hover:scale-110 group-hover:bg-cyan-500/20 transition-all duration-300 shadow-lg shadow-black/50">
                  {step.icon}
                </div>
                <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/50 flex items-center justify-center text-sm font-bold text-indigo-300">
                  {step.id}
                </div>
                <h3 className="text-lg font-bold text-white mb-2 leading-tight">{step.title}</h3>
                <p className="text-sm text-slate-400">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
}
