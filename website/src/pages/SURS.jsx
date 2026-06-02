import React from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';
import { sursData } from '../data/csupData';
import PageNavigation from '../components/PageNavigation';

export default function SURS() {
  const SursTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl z-50 relative">
          <p className="text-white font-medium">{payload[0].name}</p>
          <p className="text-cyan-400 font-bold">{payload[0].value} Test Cases</p>
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
          <div className="p-3 bg-green-500/20 rounded-xl">
            <ShieldCheck className="w-8 h-8 text-green-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold">Synthetic User Reliability Score (SURS)</h1>
        </div>
        <p className="text-xl text-slate-400 mb-12 max-w-3xl">
          SURS is a composite metric indicating the degree of trust you should place in the LLM's A/B test preference. Reliability is not validity—SURS measures how stable the synthetic signal is, not whether it perfectly matches humans.
        </p>

        <div className="grid lg:grid-cols-3 gap-6 mb-16">
          <div className="glass-card p-6 border-t-4 border-t-green-500 hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheck className="w-6 h-6 text-green-400" />
              <h3 className="text-xl font-bold text-white">High Reliability</h3>
            </div>
            <div className="text-4xl font-black text-green-400/20 absolute top-4 right-4">4</div>
            <p className="text-slate-300 text-sm mb-4">
              The LLM yields consistent preferences across all persona types, prompt variations, order permutations, and model families.
            </p>
            <div className="bg-green-500/10 p-3 rounded-lg text-green-300 text-xs font-semibold">
              Action: Safe to trust synthetic output.
            </div>
          </div>

          <div className="glass-card p-6 border-t-4 border-t-yellow-500 hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 mb-4">
              <ShieldAlert className="w-6 h-6 text-yellow-400" />
              <h3 className="text-xl font-bold text-white">Moderate Reliability</h3>
            </div>
            <div className="text-4xl font-black text-yellow-400/20 absolute top-4 right-4">24</div>
            <p className="text-slate-300 text-sm mb-4">
              Significant variance exists due to wording or models, but the overall ensemble still points to a statistically significant winner.
            </p>
            <div className="bg-yellow-500/10 p-3 rounded-lg text-yellow-300 text-xs font-semibold">
              Action: Use with caveats; rely strictly on ensemble aggregation.
            </div>
          </div>

          <div className="glass-card p-6 border-t-4 border-t-red-500 hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-red-400" />
              <h3 className="text-xl font-bold text-white">Low Reliability</h3>
            </div>
            <div className="text-4xl font-black text-red-400/20 absolute top-4 right-4">5</div>
            <p className="text-slate-300 text-sm mb-4">
              The LLM is highly confused. Position bias dominates, or models completely disagree. The signal is effectively random noise.
            </p>
            <div className="bg-red-500/10 p-3 rounded-lg text-red-300 text-xs font-semibold">
              Action: Escalate to live human A/B testing. Do not trust.
            </div>
          </div>
        </div>

        <div className="glass-card p-8 flex flex-col md:flex-row items-center gap-8">
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-white mb-4">SURS Distribution in our Corpus</h3>
            <p className="text-slate-300 mb-6">
              Out of the 33 evaluated UI test cases in our study, only 4 were classified as Highly Reliable. The vast majority (24) were Moderate, demonstrating why single-shot LLM A/B testing is fundamentally flawed and requires ensemble calibration.
            </p>
          </div>
          <div className="w-full md:w-1/2 h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sursData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {sursData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip content={<SursTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <PageNavigation 
          prev={{ name: 'Results', path: '/results' }} 
          next={{ name: 'Documentation', path: '/docs' }} 
        />
      </motion.div>
    </div>
  );
}
