import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Activity, Beaker, Bot, Users, CheckCircle, ArrowRight, ShieldAlert } from 'lucide-react';
import { metrics } from '../data/csupData';
import PageNavigation from '../components/PageNavigation';

export default function Home() {
  const metricCards = [
    { label: 'API Calls', value: metrics.apiCalls, icon: <Activity className="w-5 h-5 text-cyan-400" /> },
    { label: 'Test Cases', value: metrics.testCases, icon: <Beaker className="w-5 h-5 text-purple-400" /> },
    { label: 'Models', value: metrics.models, icon: <Bot className="w-5 h-5 text-blue-400" /> },
    { label: 'Personas', value: metrics.personas, icon: <Users className="w-5 h-5 text-pink-400" /> },
    { label: 'Experiments', value: metrics.experiments, icon: <CheckCircle className="w-5 h-5 text-green-400" /> },
  ];

  return (
    <div className="pt-32 pb-20 overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-cyan-500/10 rounded-full blur-[120px] opacity-50 pointer-events-none"></div>
      
      <div className="max-w-7xl mx-auto px-6 relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-sm font-medium tracking-wide">
            Calibrated Synthetic-User Pipeline
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">
              CSUP
            </span>
          </h1>
          
          <div className="glass-card max-w-3xl mx-auto p-8 mb-12 border-t-4 border-t-cyan-500">
            <div className="flex items-center justify-center gap-3 mb-4">
              <ShieldAlert className="w-6 h-6 text-cyan-400" />
              <h2 className="text-2xl font-bold text-white">The Research Question</h2>
            </div>
            <p className="text-xl text-slate-300 italic mb-4">
              "Can LLM synthetic users produce reliable A/B test signals — and how do we know when they can't?"
            </p>
            <p className="text-slate-400">
              Many researchers treat LLMs as a clean preference generator. We treat them as a <strong className="text-white">noisy measurement instrument</strong>. CSUP isolates true semantic design signal from systemic noise (position bias, prompt wording, repeat sampling) to deliver calibrated reliability scores.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
            <Link to="/pipeline" className="primary-button w-full sm:w-auto flex items-center justify-center gap-2">
              Explore Pipeline <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/results" className="secondary-button w-full sm:w-auto">
              View Results
            </Link>
            <Link to="/docs" className="secondary-button w-full sm:w-auto">
              Read Documentation
            </Link>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-5 gap-4 md:gap-6"
        >
          {metricCards.map((metric, idx) => (
            <div key={idx} className="glass-card p-6 flex flex-col items-center justify-center text-center group hover:-translate-y-1 transition-transform">
              <div className="mb-3 p-3 bg-white/5 rounded-full group-hover:scale-110 transition-transform">
                {metric.icon}
              </div>
              <div className="text-3xl font-bold text-white mb-1">{metric.value}</div>
              <div className="text-sm text-slate-400 font-medium">{metric.label}</div>
            </div>
          ))}
        </motion.div>
        
        <PageNavigation 
          next={{ name: 'Pipeline', path: '/pipeline' }} 
        />
      </div>
    </div>
  );
}
