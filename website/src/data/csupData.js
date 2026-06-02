// src/data/csupData.js

export const varianceData = [
  { name: 'Semantic Design Signal', value: 32.2, fill: '#0ea5e9' },
  { name: 'Repeat Sampling', value: 25.1, fill: '#8b5cf6' },
  { name: 'Prompt Wording', value: 24.3, fill: '#6366f1' },
  { name: 'Display Order', value: 7.5, fill: '#14b8a6' },
  { name: 'Persona Depth', value: 5.5, fill: '#f59e0b' },
  { name: 'Model Family', value: 5.4, fill: '#ec4899' },
];

export const calibrationPipelineData = [
  { stage: 'Raw Single-Model Output', stdev: 0.333 },
  { stage: 'Counterbalancing', stdev: 0.090 },
  { stage: 'Ensemble Aggregation', stdev: 0.320 },
  { stage: 'Full CSUP Pipeline', stdev: 0.075 },
];

export const sursData = [
  { name: 'High', value: 4, fill: '#22c55e', desc: 'Highly reliable \u2014 safe to trust' },
  { name: 'Moderate', value: 24, fill: '#eab308', desc: 'Usable with caveats / ensemble reliance' },
  { name: 'Low', value: 5, fill: '#ef4444', desc: 'Unreliable \u2014 escalate to human testing' },
];

export const personaDepthData = [
  { name: 'Demographic', value: 71.1 },
  { name: 'Biographical', value: 62.7 },
  { name: 'Interview-style', value: 65.5 },
];

export const ensembleData = [
  { k: 'k=1', min: 0.901, max: 0.945 },
  { k: 'k=2', min: 0.924, max: 0.924 },
  { k: 'k=3', min: 0.943, max: 0.943 },
  { k: 'k=4', min: 1.000, max: 1.000 },
];

export const metrics = {
  apiCalls: '~32,000',
  testCases: 33,
  models: 4,
  personas: 60,
  experiments: 9,
  baseScenarios: 23,
  promptVariants: 10,
  positionBiasCalls: '~4,600',
  fullPersonaCalls: '~16,560',
  promptRobustnessCalls: '~7,200',
  repeatStabilityCalls: '~7,200',
};

export const pipelineStages = [
  { id: 'persona-simulation', title: 'Persona Simulation', desc: 'Inject diverse demographic & context profiles', target: 'Homogeneity Bias' },
  { id: 'counterbalancing', title: 'A/B-B/A Counterbalancing', desc: 'Swap Variant order to nullify position bias', target: 'Display Order Bias' },
  { id: 'prompt-robustness', title: 'Prompt Robustness Testing', desc: 'Alter phrasing structure and vocabulary', target: 'Wording Sensitivity' },
  { id: 'repeat-sampling', title: 'Repeat Sampling', desc: 'Query multiple times to capture temperature variance', target: 'Sampling Noise' },
  { id: 'ensemble', title: 'Multi-Model Ensemble', desc: 'Aggregate across distinct LLM families', target: 'Model-specific Bias' },
  { id: 'surs', title: 'SURS Reliability Score', desc: 'Compute Synthetic User Reliability Score', target: 'Confidence Output' },
  { id: 'confidence-interval', title: 'Reliability-Adjusted CI', desc: 'Expand confidence bands based on SURS', target: 'Statistical Validity' },
  { id: 'human-escalation', title: 'Human Escalation Decision', desc: 'Fallback to human testing for Low-SURS cases', target: 'Real-world Safety' },
];
