import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ArrowRight } from 'lucide-react';

export default function PageNavigation({ prev, next }) {
  return (
    <div className="flex flex-col sm:flex-row items-center justify-between mt-16 pt-8 border-t border-white/10 gap-4">
      {prev ? (
        <Link 
          to={prev.path}
          className="flex items-center gap-3 px-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-colors w-full sm:w-auto justify-center sm:justify-start"
        >
          <ArrowLeft className="w-5 h-5 text-slate-400" />
          <div className="text-left">
            <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Previous</div>
            <div className="text-white font-medium">{prev.name}</div>
          </div>
        </Link>
      ) : (
        <div className="hidden sm:block"></div>
      )}

      {next ? (
        <Link 
          to={next.path}
          className="flex items-center gap-3 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 border border-cyan-500/30 hover:border-cyan-500/50 transition-colors w-full sm:w-auto justify-center sm:justify-end"
        >
          <div className="text-right">
            <div className="text-xs text-cyan-500 font-semibold uppercase tracking-wider">Next</div>
            <div className="text-white font-medium">{next.name}</div>
          </div>
          <ArrowRight className="w-5 h-5 text-cyan-400" />
        </Link>
      ) : (
        <div className="hidden sm:block"></div>
      )}
    </div>
  );
}
