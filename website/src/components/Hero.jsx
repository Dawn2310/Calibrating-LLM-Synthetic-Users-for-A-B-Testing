import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Beaker, Bot, CheckCircle } from 'lucide-react';

export default function Hero() {
  const metrics = [
    { label: 'API Calls', value: '~32,000', icon: <Activity className="w-5 h-5 text-cyan-400" /> },
    { label: 'Test Cases', value: '33', icon: <Beaker className="w-5 h-5 text-purple-400" /> },
    { label: 'Models Tested', value: '4', icon: <Bot className="w-5 h-5 text-blue-400" /> },
    { label: 'SURS Categories', value: '3', icon: <CheckCircle className="w-5 h-5 text-green-400" /> },
  ];

  return (
    <section id="hero" className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/20 rounded-full blur-[120px] opacity-50 pointer-events-none"></div>
      
      <div className="max-w-6xl mx-auto px-6 relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-block mb-4 px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-sm font-medium tracking-wide">
            Research Project 2026
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">
              CSUP
            </span>
            <br />
            Calibrated Synthetic-User Pipeline
          </h1>
          <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto mb-10 leading-relaxed">
            Reliability-aware LLM-based A/B testing as <span className="text-white font-semibold">noisy measurement</span>, not raw preference generation.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
            <a href="#pipeline" className="primary-button w-full sm:w-auto">
              View Pipeline
            </a>
            <a href="#findings" className="secondary-button w-full sm:w-auto">
              Key Findings
            </a>
            <a href="#citation" className="secondary-button w-full sm:w-auto">
              Citation
            </a>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6"
        >
          {metrics.map((metric, idx) => (
            <div key={idx} className="glass-card p-6 flex flex-col items-center justify-center text-center">
              <div className="mb-3 p-3 bg-white/5 rounded-full">
                {metric.icon}
              </div>
              <div className="text-3xl font-bold text-white mb-1">{metric.value}</div>
              <div className="text-sm text-slate-400 font-medium">{metric.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
