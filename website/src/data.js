/* Shared data from the paper — used across all pages */

export const varianceData = [
  { name: 'Prompt Wording',  value: 41.2, fill: '#f472b6' },
  { name: 'Semantic Signal',  value: 32.2, fill: '#5b8def' },
  { name: 'Repeat Sampling',  value: 25.1, fill: '#9b6dff' },
  { name: 'Display Order',    value: 0.7,  fill: '#2dd4bf' },
  { name: 'Persona Depth',    value: 0.6,  fill: '#fbbf24' },
  { name: 'Model Family',     value: 0.3,  fill: '#f87171' },
];

export const pipelineStages = [
  { stage: 'Raw Output',         std: 0.333 },
  { stage: '+ Counterbalance',   std: 0.090 },
  { stage: 'Full CSUP',          std: 0.077 },
];

export const sursData = [
  { component: 'Order Robustness',      symbol: 'R_order',   weight: 0.20, description: 'Invariance under A/B ↔ B/A swap' },
  { component: 'Prompt Robustness',     symbol: 'R_prompt',  weight: 0.20, description: 'Stability across paraphrases' },
  { component: 'Repeat Stability',      symbol: 'R_repeat',  weight: 0.20, description: 'Intra-model modal consistency' },
  { component: 'Cross-Model Agreement', symbol: 'R_model',   weight: 0.20, description: "Fleiss' κ across 4 model families" },
  { component: 'Persona Consistency',   symbol: 'R_persona', weight: 0.20, description: 'Agreement across persona depths' },
];

export const agreementData = [
  { pair: 'GPT-4o — Llama 3.3',    kappa: 0.664, agree: '83.2%' },
  { pair: 'DeepSeek — GPT-4o',     kappa: 0.660, agree: '83.0%' },
  { pair: 'Claude — DeepSeek',     kappa: 0.621, agree: '81.2%' },
  { pair: 'Claude — GPT-4o',       kappa: 0.618, agree: '81.0%' },
  { pair: 'DeepSeek — Llama 3.3',  kappa: 0.615, agree: '80.8%' },
  { pair: 'Claude — Llama 3.3',    kappa: 0.576, agree: '78.8%' },
];

export const sursDistribution = [
  { name: 'High (≥0.80)', cases: 4, fill: '#34d399' },
  { name: 'Moderate (0.60-0.79)', cases: 24, fill: '#fbbf24' },
  { name: 'Low (<0.60)', cases: 5, fill: '#f87171' },
];

export const sursExamples = [
  { id: 'COPY-05', score: 0.921, level: 'High', desc: 'Binary cancel vs Pause-first retention' },
  { id: 'UI-01', score: 0.565, level: 'Low', desc: 'Single-page vs Step-by-step checkout' },
  { id: 'UI-09-V2', score: 0.492, level: 'Low', desc: 'Hover-zoom vs "Find Similar" overlay' },
];

export const modelsInfo = [
  { icon: '🟢', name: 'GPT-4o',            provider: 'OpenAI',    arch: 'Dense' },
  { icon: '🟣', name: 'Claude 3.5 Sonnet', provider: 'Anthropic', arch: 'Dense' },
  { icon: '🔵', name: 'Llama 3.3 70B',     provider: 'Meta',      arch: 'Dense' },
  { icon: '⚡', name: 'DeepSeek-V4-Flash',  provider: 'DeepSeek',  arch: 'MoE' },
];

export const experimentsOverview = [
  { id: 1, title: 'Between-Model Agreement',        metric: "Fleiss' κ = 0.619", desc: 'Substantial agreement across 4 model families, but not interchangeable.' },
  { id: 2, title: 'Variance Decomposition',          metric: '41.2% prompt wording', desc: 'Prompt wording dominates over the actual semantic signal.' },
  { id: 3, title: 'Order Bias',                      metric: '37.7% flip rate', desc: 'Swapping A/B order flips the verdict for over a third of cases.' },
  { id: 4, title: 'Persona Depth Paradox',           metric: '69.6% → 61.3%', desc: 'Richer personas reduce consensus rather than improving it.' },
  { id: 5, title: 'CSUP vs. Raw',                    metric: 'σ: 0.333 → 0.077', desc: 'Full pipeline reduces instability by 77%.' },
  { id: 6, title: 'Prompt-Sensitivity Profiling',    metric: '5 templates tested', desc: 'Different phrasings produce significantly different distributions.' },
  { id: 7, title: 'Persona Interaction Effects',     metric: '3 depth levels', desc: 'Interaction between persona depth and model family.' },
  { id: 8, title: 'SURS Reliability Scoring',        metric: '5 components', desc: 'Composite score flags unreliable results before they mislead.' },
  { id: 9, title: 'Cost Analysis',                   metric: '~$25 total', desc: 'Full 30K-call experiment costs less than a single user study participant.' },
];
