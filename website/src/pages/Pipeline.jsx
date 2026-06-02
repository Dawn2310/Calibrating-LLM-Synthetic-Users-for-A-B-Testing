import React from 'react';
import { motion } from 'framer-motion';
import { pipelineStages } from '../data/csupData';
import { Layers } from 'lucide-react';
import PageNavigation from '../components/PageNavigation';

export default function Pipeline() {
  return (
    <div className="pt-32 pb-20 section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-indigo-500/20 rounded-xl">
            <Layers className="w-8 h-8 text-indigo-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold">CSUP Pipeline</h1>
        </div>
        <p className="text-xl text-slate-400 mb-12 max-w-3xl">
          The pipeline consists of 8 rigorous stages designed to strip away systemic LLM noise and extract a clean, calibrated semantic preference signal.
        </p>

        <div className="grid lg:grid-cols-2 gap-6">
          {pipelineStages.map((stage, idx) => (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="glass-card p-6 flex flex-col justify-between group hover:border-cyan-500/30 transition-all cursor-default"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/50 flex items-center justify-center text-sm font-bold text-indigo-300">
                      {idx + 1}
                    </div>
                    <h3 className="text-xl font-bold text-white group-hover:text-cyan-400 transition-colors">{stage.title}</h3>
                  </div>
                </div>
                <p className="text-slate-300 mb-6">{stage.desc}</p>
              </div>
              <div className="bg-[#040814]/50 p-4 rounded-xl border border-white/5">
                <span className="text-xs uppercase font-bold text-slate-500 tracking-wider">Targeted Noise</span>
                <p className="text-red-400 font-medium mt-1">{stage.target}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <PageNavigation 
          prev={{ name: 'Home', path: '/' }} 
          next={{ name: 'Experiments', path: '/experiments' }} 
        />
      </motion.div>
    </div>
  );
}
