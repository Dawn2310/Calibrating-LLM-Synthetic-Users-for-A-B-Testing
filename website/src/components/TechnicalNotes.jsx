import React from 'react';
import { motion } from 'framer-motion';
import { Database, FolderTree, Clock, Hash, Bot } from 'lucide-react';

export default function TechnicalNotes() {
  const notes = [
    { icon: <Database className="w-6 h-6 text-blue-400" />, title: "SQLite Checkpointing", desc: "Results are saved continuously. If an API rate limit interrupts execution, the pipeline resumes safely." },
    { icon: <FolderTree className="w-6 h-6 text-green-400" />, title: "Relative Paths", desc: "Data loading logic handles relative paths natively. Ensure execution from the repository root." },
    { icon: <Clock className="w-6 h-6 text-purple-400" />, title: "Rate Limiting", desc: "Anthropic and Groq API calls are staggered using exponential backoff to prevent HTTP 429 drops." },
    { icon: <Hash className="w-6 h-6 text-cyan-400" />, title: "Run Numbers", desc: "Every unique API request is indexed with a run_number (1-20) to ensure exact repeatability analysis." },
    { icon: <Bot className="w-6 h-6 text-red-400" />, title: "DeepSeek Reasoning", desc: "DeepSeek parsing logic strips chain-of-thought blocks before extracting the semantic A/B choice." },
  ];

  return (
    <section id="technical" className="section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Technical Notes</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
          {notes.map((note, idx) => (
            <div key={idx} className="glass-card p-6 hover:bg-white/5 transition-colors">
              <div className="mb-4">{note.icon}</div>
              <h3 className="text-lg font-bold text-white mb-2">{note.title}</h3>
              <p className="text-sm text-slate-400">{note.desc}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </section>
  );
}
