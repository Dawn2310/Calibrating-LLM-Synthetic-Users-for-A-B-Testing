import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Terminal, FolderTree } from 'lucide-react';
import CodeBlock from '../components/CodeBlock';
import ProjectStructure from '../components/ProjectStructure';
import PageNavigation from '../components/PageNavigation';

export default function Docs() {
  return (
    <div className="pt-32 pb-20 section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-purple-500/20 rounded-xl">
            <BookOpen className="w-8 h-8 text-purple-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold">Documentation</h1>
        </div>
        <p className="text-xl text-slate-400 mb-12 max-w-3xl">
          Everything you need to replicate our experiments or run the CSUP pipeline on your own A/B testing corpora.
        </p>

        <div className="mb-16">
          <ProjectStructure />
        </div>

        <div className="glass-card p-6 md:p-10 mb-12 border-t-4 border-t-indigo-500">
          <div className="flex items-center gap-3 mb-8">
            <Terminal className="w-6 h-6 text-indigo-400" />
            <h2 className="text-2xl font-bold text-white">Quick Start Guide</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-bold text-white mb-4">1. Environment Setup</h3>
              <p className="text-sm text-slate-400 mb-4">Install required dependencies and set your API keys for the ensemble models.</p>
              
              <CodeBlock 
                label="Install Dependencies" 
                code={`pip install openai anthropic groq pandas tqdm`} 
              />
              
              <CodeBlock 
                label="Set API Keys" 
                code={`export OPENAI_API_KEY="sk-..."\nexport ANTHROPIC_API_KEY="sk-ant-..."\nexport GROQ_API_KEY="gsk_..."\nexport DEEPSEEK_API_KEY="sk-..."`} 
              />
            </div>
            
            <div>
              <h3 className="text-xl font-bold text-white mb-4">2. Execution & Analysis</h3>
              <p className="text-sm text-slate-400 mb-4">Initialize the database, run the phases, and calculate SURS.</p>
              
              <CodeBlock 
                label="Initialize Database" 
                code={`python scripts/pipeline.py --init`} 
              />
              
              <CodeBlock 
                label="Run Experiments (Phase 2: Full Persona)" 
                code={`python scripts/pipeline.py --phase 2`} 
              />
              
              <CodeBlock 
                label="Export & Analyze Results" 
                code={`python scripts/db_to_csv.py\npython scripts/csup_analysis.py`} 
              />
            </div>
          </div>
        </div>

        <PageNavigation 
          prev={{ name: 'SURS', path: '/surs' }} 
          next={{ name: 'Citation', path: '/citation' }} 
        />
      </motion.div>
    </div>
  );
}
