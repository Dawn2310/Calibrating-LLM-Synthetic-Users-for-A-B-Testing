import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Folder, FolderOpen, FileText, FileJson, FileSpreadsheet, Database, Code } from 'lucide-react';

const TreeItem = ({ name, type, children, level = 0 }) => {
  const [isOpen, setIsOpen] = useState(true);
  const isFolder = type === 'folder';

  const getIcon = () => {
    if (isFolder) return isOpen ? <FolderOpen className="w-4 h-4 text-blue-400" /> : <Folder className="w-4 h-4 text-blue-400" />;
    if (name.endsWith('.md')) return <FileText className="w-4 h-4 text-slate-400" />;
    if (name.endsWith('.jsonl')) return <FileJson className="w-4 h-4 text-yellow-400" />;
    if (name.endsWith('.csv') || name.endsWith('.xlsx')) return <FileSpreadsheet className="w-4 h-4 text-green-400" />;
    if (name.endsWith('.db')) return <Database className="w-4 h-4 text-purple-400" />;
    if (name.endsWith('.py')) return <Code className="w-4 h-4 text-blue-500" />;
    return <FileText className="w-4 h-4 text-slate-400" />;
  };

  return (
    <div className="font-mono text-sm">
      <div 
        className={`flex items-center gap-2 py-1.5 px-2 hover:bg-white/5 rounded cursor-pointer select-none transition-colors ${level > 0 ? 'ml-4 border-l border-white/10' : ''}`}
        onClick={() => isFolder && setIsOpen(!isOpen)}
        style={{ paddingLeft: `${level === 0 ? 0.5 : 0.5}rem` }}
      >
        {getIcon()}
        <span className={isFolder ? 'text-blue-100 font-semibold' : 'text-slate-300'}>{name}</span>
      </div>
      <AnimatePresence>
        {isFolder && isOpen && children && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            {children.map((child, idx) => (
              <TreeItem key={idx} {...child} level={level + 1} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default function ProjectStructure() {
  const structure = [
    {
      name: 'analysis', type: 'folder', children: [
        { name: 'tables/', type: 'folder' },
        { name: 'csup_results/', type: 'folder' },
      ]
    },
    {
      name: 'data', type: 'folder', children: [
        { name: 'human/', type: 'folder' },
        { name: 'api_calls.csv', type: 'file' },
        { name: 'cleaned_master_dataset.csv', type: 'file' },
        { name: 'experiment.db', type: 'file' },
        { name: 'position_bias.csv', type: 'file' },
        { name: 'synthetic_user_pipeline.db', type: 'file' },
      ]
    },
    {
      name: 'references', type: 'folder', children: [
        { name: 'ab_test_corpus_redesigned.xlsx', type: 'file' },
        { name: 'metadata.csv', type: 'file' },
      ]
    },
    {
      name: 'scripts', type: 'folder', children: [
        { name: 'csup_analysis.py', type: 'file' },
        { name: 'db_to_csv.py', type: 'file' },
        { name: 'pipeline.py', type: 'file' },
        { name: 'position_bias_test.py', type: 'file' },
        { name: 'utils.py', type: 'file' },
      ]
    },
    {
      name: 'survey', type: 'folder', children: [
        { name: 'responses.jsonl', type: 'file' },
      ]
    }
  ];

  return (
    <section id="structure" className="section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title">Project Structure</h2>
        <p className="section-subtitle">A transparent, reproducible repository layout containing all datasets, analysis scripts, and evaluation corpora.</p>
        
        <div className="glass-card rounded-2xl overflow-hidden border border-white/10 max-w-3xl mx-auto shadow-2xl">
          <div className="bg-slate-900/80 px-4 py-3 flex items-center gap-2 border-b border-white/10">
            <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            <div className="ml-4 text-xs font-mono text-slate-400">~/csup-project</div>
          </div>
          <div className="p-4 bg-[#0a0f1d]/80 overflow-x-auto">
            {structure.map((item, idx) => (
              <TreeItem key={idx} {...item} />
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
}
