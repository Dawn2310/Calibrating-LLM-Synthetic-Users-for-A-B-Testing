import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, FlaskConical } from 'lucide-react';
import { metrics } from '../data/csupData';
import PageNavigation from '../components/PageNavigation';

export default function Experiments() {
  const phases = [
    {
      title: "Position-Bias Calibration",
      calls: metrics.positionBiasCalls,
      desc: "Isolated testing to measure LLM preference for 'Variant A' simply because it appears first. We enforce A/B–B/A agreement."
    },
    {
      title: "Full Persona Experiment",
      calls: metrics.fullPersonaCalls,
      desc: "Injected 60 distinct personas (demographic, biographical, and interview-style) to simulate heterogeneous user populations."
    },
    {
      title: "Prompt Robustness",
      calls: metrics.promptRobustnessCalls,
      desc: "Altered the phrasing, vocabulary, and syntactic structure of the prompt to test semantic stability."
    },
    {
      title: "Repeat Stability",
      calls: metrics.repeatStabilityCalls,
      desc: "Queried the exact same prompt multiple times (T=0.7) to measure non-deterministic sampling variance."
    }
  ];

  return (
    <div className="pt-32 pb-20 section-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-green-500/20 rounded-xl">
            <FlaskConical className="w-8 h-8 text-green-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold">Experiment Design</h1>
        </div>
        <p className="text-xl text-slate-400 mb-12 max-w-3xl">
          We evaluated {metrics.baseScenarios} base scenarios and {metrics.promptVariants} prompt variants (total {metrics.testCases} test cases) across 4 experimental phases.
        </p>

        <div className="relative border-l-2 border-slate-700/50 pl-8 ml-4 space-y-12 mb-16">
          {phases.map((phase, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="absolute -left-[43px] top-1 w-6 h-6 rounded-full bg-slate-900 border-4 border-green-500"></div>
              <div className="glass-card p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-2xl font-bold text-white">{phase.title}</h3>
                  <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-sm font-mono text-cyan-400">
                    {phase.calls} API Calls
                  </span>
                </div>
                <p className="text-slate-300">{phase.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="glass-card p-8 border-t-4 border-t-purple-500">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle2 className="w-6 h-6 text-purple-400" />
            <h3 className="text-2xl font-bold text-white">Human Validation Ground Truth</h3>
          </div>
          <p className="text-slate-300 mb-4">
            A parallel human study was conducted to establish ground truth for the A/B tests. The resulting data (anonymized) is reserved in the `data/human/` directory to validate the predictive power of the CSUP synthetic output.
          </p>
        </div>

        <PageNavigation 
          prev={{ name: 'Pipeline', path: '/pipeline' }} 
          next={{ name: 'Models', path: '/models' }} 
        />
      </motion.div>
    </div>
  );
}
