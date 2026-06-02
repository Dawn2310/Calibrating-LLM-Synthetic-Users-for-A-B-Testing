import React from 'react';
import { motion } from 'framer-motion';
import { Bot, Zap, Cpu, BrainCircuit, ShieldAlert } from 'lucide-react';
import PageNavigation from '../components/PageNavigation';

export default function Models() {
  const models = [
    { name: 'GPT-4o', provider: 'OpenAI API', endpoint: 'api.openai.com', type: 'Proprietary, Dense/MoE', icon: <Cpu className="w-8 h-8 text-emerald-400" />, desc: 'Flagship reasoning and multimodal capabilities' },
    { name: 'Claude 3.5 Sonnet', provider: 'Anthropic API', endpoint: 'api.anthropic.com', type: 'Proprietary, Dense', icon: <BrainCircuit className="w-8 h-8 text-amber-400" />, desc: 'Advanced nuance and instruction following' },
    { name: 'Llama 3.3 70B', provider: 'Together AI', endpoint: 'api.together.xyz', type: 'Open-weight, Dense', icon: <Zap className="w-8 h-8 text-blue-400" />, desc: 'High-speed open-weights inference' },
    { name: 'DeepSeek-V4-Flash', provider: 'DeepSeek API', endpoint: 'api.deepseek.com', type: 'Open-weight, MoE', icon: <Bot className="w-8 h-8 text-cyan-400" />, desc: 'Specialized reasoning models' },
  ];

  return (
    <div className="pt-32 pb-20 section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-blue-500/20 rounded-xl">
            <Cpu className="w-8 h-8 text-blue-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold">Evaluated Models</h1>
        </div>
        <p className="text-xl text-slate-400 mb-12 max-w-3xl">
          We benchmarked the pipeline across 4 frontier models to evaluate whether multi-model ensembles can mitigate provider-specific alignment biases.
        </p>
        
        <div className="grid lg:grid-cols-2 gap-6 mt-12 mb-16">
          {models.map((model, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="glass-card p-6 flex items-start gap-6 hover:bg-white/5 transition-colors group"
            >
              <div className="p-4 rounded-2xl bg-slate-800/50 group-hover:scale-110 transition-transform duration-300">
                {model.icon}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-1">{model.name}</h3>
                <div className="text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-1">{model.provider}</div>
                <div className="text-xs font-mono text-slate-500 mb-3">{model.endpoint}</div>
                <p className="text-sm text-slate-300 mb-3">{model.desc}</p>
                <div className="inline-block px-2 py-1 bg-white/5 rounded text-xs text-slate-400">
                  {model.type}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="glass-card p-8 border-l-4 border-l-cyan-500">
          <div className="flex items-center gap-3 mb-4">
            <ShieldAlert className="w-6 h-6 text-cyan-400" />
            <h3 className="text-2xl font-bold text-white">Why Ensemble Matters</h3>
          </div>
          <p className="text-slate-300 mb-4 leading-relaxed">
            Proprietary models (like GPT-4o and Claude) often share similar RLHF alignment penalties, leading to correlated biases in A/B testing (e.g., favoring overly polite or verbose UI text). Open-weight models (Llama 3.3) and diverse MoE architectures (DeepSeek) have different training distributions. 
            <br/><br/>
            By ensembling across these distinct families, CSUP ensures that a "winning" A/B variant is actually better designed, rather than just catering to the specific alignment quirk of one API provider.
          </p>
        </div>

        <PageNavigation 
          prev={{ name: 'Experiments', path: '/experiments' }} 
          next={{ name: 'Results', path: '/results' }} 
        />
      </motion.div>
    </div>
  );
}
