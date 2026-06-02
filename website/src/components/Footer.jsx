import React from 'react';

export default function Footer() {
  return (
    <footer className="py-10 text-center text-slate-500 text-sm border-t border-white/10 mt-16 bg-[#040814]/80">
      <div className="max-w-7xl mx-auto px-6 flex flex-col items-center">
        <div className="w-8 h-8 mb-4 rounded-lg bg-gradient-to-br from-cyan-400 to-indigo-500 flex items-center justify-center text-white font-bold text-xs opacity-50">
          CS
        </div>
        <p className="mb-2">© 2026 CSUP Project Team. All rights reserved.</p>
        <p className="mb-4">Calibrated Synthetic-User Pipeline for LLM-Based A/B Testing.</p>
        <div className="flex items-center gap-4 text-xs">
          <span className="px-3 py-1 rounded-full border border-slate-700 bg-slate-800 text-slate-400">MIT License</span>
          <span className="px-3 py-1 rounded-full border border-slate-700 bg-slate-800 text-slate-400">Preprint 2026</span>
        </div>
      </div>
    </footer>
  );
}
