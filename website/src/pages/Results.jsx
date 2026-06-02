import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, LineChart, Line } from 'recharts';
import { varianceData, sursData, personaDepthData, calibrationPipelineData, ensembleData } from '../data/csupData';
import { BarChart3 } from 'lucide-react';
import PageNavigation from '../components/PageNavigation';

export default function Results() {
  const CustomTooltip = ({ active, payload, suffix = '%' }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl z-50 relative">
          <p className="text-white font-medium">{payload[0].payload.name || payload[0].payload.stage || payload[0].payload.k}</p>
          <p className="text-cyan-400 font-bold">{payload[0].value}{suffix}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="pt-32 pb-20 section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-amber-500/20 rounded-xl">
            <BarChart3 className="w-8 h-8 text-amber-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold">Analytics Dashboard</h1>
        </div>
        <p className="text-xl text-slate-400 mb-12 max-w-3xl">
          Visualizing the impact of the CSUP pipeline on isolating semantic signal from systemic noise.
        </p>
        
        <div className="grid lg:grid-cols-2 gap-8 mt-8">
          {/* Variance Decomposition */}
          <div className="glass-card p-6 flex flex-col h-[450px]">
            <h3 className="text-lg font-bold text-white mb-2">Variance Decomposition</h3>
            <p className="text-sm text-slate-400 mb-6 flex-grow-0">
              Prompt wording and repeat sampling together explain ~50% of the variance in LLM choices, severely diminishing the true Semantic Design signal if unchecked.
            </p>
            <div className="flex-grow w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={varianceData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                  <YAxis dataKey="name" type="category" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} width={110} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {varianceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Calibration Pipeline Standard Deviation */}
          <div className="glass-card p-6 flex flex-col h-[450px]">
            <h3 className="text-lg font-bold text-white mb-2">Calibration Pipeline Stability</h3>
            <p className="text-sm text-slate-400 mb-6 flex-grow-0">
              The CSUP pipeline drastically reduces standard deviation (from 0.333 down to 0.075) across test cases, yielding a much tighter confidence interval.
            </p>
            <div className="flex-grow w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={calibrationPipelineData} margin={{ top: 20, right: 30, left: 0, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="stage" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 10 }} angle={-25} textAnchor="end" />
                  <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                  <Tooltip content={<CustomTooltip suffix=" StdDev" />} />
                  <Line type="monotone" dataKey="stdev" stroke="#06b6d4" strokeWidth={3} dot={{ r: 6, fill: '#06b6d4', strokeWidth: 2, stroke: '#0f172a' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Persona Depth */}
          <div className="glass-card p-6 flex flex-col h-[400px]">
            <h3 className="text-lg font-bold text-white mb-2">The "Hallucination of Depth"</h3>
            <p className="text-sm text-slate-400 mb-6 flex-grow-0">
              Richer personas <strong className="text-white">reduce</strong> cross-model consensus rather than improving it. Deep biographical profiles cause model divergence.
            </p>
            <div className="flex-grow w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={personaDepthData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                  <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} domain={[50, 80]} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={60} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Ensemble Agreement */}
          <div className="glass-card p-6 flex flex-col h-[400px]">
            <h3 className="text-lg font-bold text-white mb-2">Multi-Model Ensemble Agreement</h3>
            <p className="text-sm text-slate-400 mb-6 flex-grow-0">
              As ensemble size (k) increases, the aggregate agreement approaches 1.000, effectively stabilizing the final predicted preference.
            </p>
            <div className="flex-grow w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={ensembleData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="k" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                  <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} domain={[0.85, 1.05]} />
                  <Tooltip content={<CustomTooltip suffix="" />} />
                  <Line type="monotone" dataKey="min" stroke="#a855f7" strokeWidth={3} dot={{ r: 6, fill: '#a855f7' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        <PageNavigation 
          prev={{ name: 'Models', path: '/models' }} 
          next={{ name: 'SURS', path: '/surs' }} 
        />
      </motion.div>
    </div>
  );
}
