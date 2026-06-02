import React from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { ArrowLeft, Layers, ArrowRight } from 'lucide-react';
import { PageWrapper, CustomTooltip } from '../components';
import { pipelineStages } from '../data';

export default function PipelinePage() {
  return (
    <PageWrapper>
      {/* ── HEADER ── */}
      <section className="page-header section">
        <div className="container">
          <Link to="/" className="back-link animate-fade-in"><ArrowLeft size={16} /> Back to Home</Link>
          <div className="animate-fade-in delay-1">
            <div className="section-eyebrow"><Layers size={14} /> Framework</div>
            <h1 className="page-title">The <span className="text-gradient">CSUP</span> Pipeline</h1>
            <p className="page-desc">
              Calibrated Synthetic User Protocol — a four-stage pipeline that converts raw LLM outputs
              into a calibrated directional signal with a measurable reliability score.
            </p>
          </div>
        </div>
      </section>

      {/* ── PHILOSOPHY ── */}
      <section className="section">
        <div className="container-narrow">
          <div className="finding-block animate-fade-in">
            <div className="finding-number">⚡</div>
            <div className="finding-content">
              <h2>Not a Replacement — a Triage Tool</h2>
              <p>
                CSUP does not claim LLMs replace human testers. Instead, it determines whether
                a synthetic result is <strong>stable enough</strong> to serve as an early-stage
                directional signal — or whether the noise is so high that the result should be
                discarded and a human study commissioned instead.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── PIPELINE STEPS ── */}
      <section className="section section-border-top bg-surface">
        <div className="container">
          <div className="pipeline-detail-grid">
            {[
              {
                n: '1',
                title: 'Persona Simulation',
                desc: '60 personas at 3 depth levels (demographic, biographical, interview-grounded) across 20 market segments.',
                details: [
                  'Each persona is uniquely generated from demographic distributions matching real market data.',
                  '3 depth levels test how much persona detail affects evaluation stability.',
                  'Segments cover age, gender, occupation, and tech familiarity combinations.',
                ],
                color: 'var(--accent-pink)',
              },
              {
                n: '2',
                title: 'Order Counterbalancing',
                desc: 'Run A/B and B/A orders; normalize display slots to semantic design choices.',
                details: [
                  'Each design pair is evaluated in both presentation orders.',
                  'Removes positional bias — the 37.7% flip rate observed in raw outputs.',
                  'This single step cuts instability from σ = 0.333 to σ = 0.090.',
                ],
                color: 'var(--accent-blue)',
              },
              {
                n: '3',
                title: 'Repeat Sampling',
                desc: 'N = 3 identical runs per condition; aggregate via majority vote.',
                details: [
                  'Temperature = 0.7 introduces stochastic variation between runs.',
                  'Majority voting filters out one-off hallucinations and random drift.',
                  'Captures intra-model stability across identical queries.',
                ],
                color: 'var(--accent-purple)',
              },
              {
                n: '4',
                title: 'Multi-Model Ensemble',
                desc: 'Query 4 model families and aggregate via majority vote.',
                details: [
                  'GPT-4o (OpenAI), Claude 3.5 Sonnet (Anthropic), Llama 3.3 70B (Meta), DeepSeek-V4-Flash (DeepSeek).',
                  'Diverse architectures (Dense + MoE) reduce single-model alignment bias.',
                  'Final verdict requires cross-family consensus.',
                ],
                color: 'var(--accent-teal)',
              },
            ].map((step, i) => (
              <div key={i} className="pipeline-detail-card animate-fade-in" style={{ '--accent': step.color }}>
                <div className="pipeline-detail-header">
                  <div className="step-number-lg">{step.n}</div>
                  <div>
                    <h3>{step.title}</h3>
                    <p className="pipeline-detail-summary">{step.desc}</p>
                  </div>
                </div>
                <ul className="pipeline-detail-list">
                  {step.details.map((d, j) => (
                    <li key={j}>{d}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── INSTABILITY CHART ── */}
      <section className="section section-border-top">
        <div className="container">
          <div className="section-header text-center animate-fade-in">
            <h2 className="section-title">Instability <span className="text-gradient-teal">Reduction</span></h2>
            <p className="section-desc">
              Standard deviation of P(A) across 33 test cases at each pipeline stage.
            </p>
          </div>

          <div style={{ maxWidth: '700px', margin: '0 auto' }}>
            <div className="chart-container animate-fade-in delay-2">
              <ResponsiveContainer width="100%" height={360}>
                <BarChart data={pipelineStages} margin={{ top: 10, right: 20, left: 10, bottom: 30 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                  <XAxis
                    dataKey="stage" stroke="transparent"
                    tick={{ fill: '#8b8b9e', fontSize: 12 }}
                    angle={-10} textAnchor="end" height={50}
                  />
                  <YAxis stroke="#5a5a6e" tick={{ fill: '#8b8b9e', fontSize: 12 }} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                  <Bar dataKey="std" radius={[6, 6, 0, 0]} barSize={56}>
                    {pipelineStages.map((_, i) => (
                      <Cell key={i} fill={i === 3 ? '#2dd4bf' : '#9b6dff'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="stat-grid animate-fade-in delay-3" style={{ marginTop: 'var(--space-8)', maxWidth: '700px', margin: 'var(--space-8) auto 0' }}>
            <div className="stat-card">
              <div className="stat-value text-gradient-alt">σ 0.333</div>
              <div className="stat-label">Raw Output</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient-teal">σ 0.077</div>
              <div className="stat-label">Full CSUP</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient">77%</div>
              <div className="stat-label">Reduction</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── BOTTOM NAV ── */}
      <section className="section">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
          <Link to="/findings" className="btn btn-secondary btn-lg">
            <ArrowLeft size={18} /> Findings
          </Link>
          <Link to="/surs" className="btn btn-primary btn-lg">
            SURS Reliability Score <ArrowRight size={18} />
          </Link>
        </div>
      </section>
    </PageWrapper>
  );
}
