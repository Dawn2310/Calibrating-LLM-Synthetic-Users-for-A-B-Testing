import React from 'react';
import { motion } from 'framer-motion';
import { Bot, Zap, Cpu, BrainCircuit } from 'lucide-react';

export default function Models() {
  const models = [
    { name: 'GPT-4o', provider: 'OpenAI API', icon: <Cpu className="w-8 h-8 text-emerald-400" />, desc: 'Flagship reasoning and multimodal capabilities' },
    { name: 'Claude 3.5 Sonnet', provider: 'Anthropic API', icon: <BrainCircuit className="w-8 h-8 text-amber-400" />, desc: 'Advanced nuance and instruction following' },
    { name: 'Llama 3.3 70B', provider: 'Groq API', icon: <Zap className="w-8 h-8 text-blue-400" />, desc: 'High-speed open-weights inference' },
    { name: 'DeepSeek-V4-Flash', provider: 'DeepSeek API', icon: <Bot className="w-8 h-8 text-cyan-400" />, desc: 'Specialized reasoning models' },
  ];

  return (
    <section id="models" className="section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Evaluated Models</h2>
        <p className="section-subtitle text-center mx-auto">We benchmarked our pipeline across four leading frontier models to measure cross-family agreement.</p>
        
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
          {models.map((model, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="glass-card p-6 flex flex-col items-center text-center hover:bg-white/5 transition-colors group"
            >
              <div className="mb-4 p-4 rounded-2xl bg-slate-800/50 group-hover:scale-110 transition-transform duration-300">
                {model.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-1">{model.name}</h3>
              <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-3">{model.provider}</div>
              <p className="text-sm text-slate-400">{model.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
}
