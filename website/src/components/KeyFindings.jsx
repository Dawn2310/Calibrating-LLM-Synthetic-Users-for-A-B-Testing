import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';

export default function KeyFindings() {
  const varianceData = [
    { name: 'Semantic Design', value: 32.2, fill: '#0ea5e9' },
    { name: 'Repeat Sampling', value: 25.1, fill: '#8b5cf6' },
    { name: 'Prompt Wording', value: 24.3, fill: '#6366f1' },
    { name: 'Display Order', value: 7.5, fill: '#14b8a6' },
    { name: 'Persona Depth', value: 5.5, fill: '#f59e0b' },
    { name: 'Model Family', value: 5.4, fill: '#ec4899' },
  ];

  const sursData = [
    { name: 'High', value: 4, fill: '#22c55e' },
    { name: 'Moderate', value: 24, fill: '#eab308' },
    { name: 'Low', value: 5, fill: '#ef4444' },
  ];

  const personaData = [
    { name: 'Demographic', value: 71.1 },
    { name: 'Biographical', value: 62.7 },
    { name: 'Interview', value: 65.5 },
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl">
          <p className="text-white font-medium">{payload[0].payload.name}</p>
          <p className="text-cyan-400">{payload[0].value}%</p>
        </div>
      );
    }
    return null;
  };

  const SursTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl">
          <p className="text-white font-medium">{payload[0].name}</p>
          <p className="text-cyan-400">{payload[0].value} Test Cases</p>
        </div>
      );
    }
    return null;
  };

  return (
    <section id="findings" className="section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="section-title text-center">Key Findings</h2>
        <p className="section-subtitle text-center mx-auto">Analytics drawn from over 32,000 API calls across 33 UI/UX test cases.</p>
        
        <div className="grid lg:grid-cols-2 gap-8 mt-12">
          {/* Variance Decomposition */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-6">Variance Decomposition</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={varianceData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <YAxis dataKey="name" type="category" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} width={100} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {varianceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-sm text-slate-400 mt-4 text-center">
              Prompt wording and repeat sampling together explain ~50% of the variance in LLM choices.
            </p>
          </div>

          {/* SURS Distribution */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-bold text-white mb-6">SURS Distribution</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sursData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sursData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip content={<SursTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <p className="text-sm text-slate-400 mt-4 text-center">
              Only 4/33 cases were "Highly Reliable". The majority (24) are "Moderate", requiring ensemble interpretation.
            </p>
          </div>

          {/* Persona Depth */}
          <div className="glass-card p-6 lg:col-span-2">
            <h3 className="text-lg font-bold text-white mb-6">The "Hallucination of Depth"</h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={personaData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} domain={[50, 100]} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={60} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-sm text-slate-400 mt-4 text-center max-w-2xl mx-auto">
              Richer personas <span className="text-white font-medium">reduce</span> cross-model consensus rather than improving it. Demographic personas achieved 71.1% consensus, while deeper Biographical personas dropped to 62.7%.
            </p>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
