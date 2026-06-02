import React from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { ArrowLeft, Activity, Users, RefreshCcw, BarChart3 } from 'lucide-react';
import { PageWrapper, CustomTooltip } from '../components';
import { varianceData, agreementData } from '../data';

export default function FindingsPage() {
  return (
    <PageWrapper>
      {/* ── HEADER ── */}
      <section className="page-header section">
        <div className="container">
          <Link to="/" className="back-link animate-fade-in"><ArrowLeft size={16} /> Back to Home</Link>
          <div className="animate-fade-in delay-1">
            <div className="section-eyebrow"><Activity size={14} /> Key Findings</div>
            <h1 className="page-title">Why Raw LLM A/B Testing <span className="text-gradient-alt">Fails</span></h1>
            <p className="page-desc">
              Three critical insights from evaluating four LLM families across 33 test-case variants
              in UI/UX, Copywriting, and Recommendation domains.
            </p>
          </div>
        </div>
      </section>

      {/* ── FINDING 1: ILLUSION OF PREFERENCE ── */}
      <section className="section">
        <div className="container">
          <div className="finding-block animate-fade-in">
            <div className="finding-number">01</div>
            <div className="finding-content">
              <h2>The Illusion of Preference</h2>
              <p>
                A naïve A/B test with a single prompt might seem definitive — "68% chose Design A."
                But our variance decomposition of <strong>30,179 API calls</strong> reveals that
                <strong> 41.2%</strong> of the observed variance comes from <em>how the question was phrased</em>,
                not from the design difference itself.
              </p>
              <p>
                The semantic signal — the thing you actually want to measure — accounts for only 32.2%.
                In other words, <strong>the prompt is louder than the signal</strong>. Two teams running
                "the same" A/B test with different prompts can reach opposite conclusions.
              </p>
            </div>
          </div>

          <div className="chart-container animate-fade-in delay-2" style={{ marginTop: 'var(--space-8)' }}>
            <div className="chart-title">Variance Decomposition — Share of Total Variance (%)</div>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={varianceData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" unit="%" stroke="#5a5a6e" tick={{ fill: '#8b8b9e', fontSize: 12 }} />
                <YAxis
                  dataKey="name" type="category" width={130}
                  stroke="transparent"
                  tick={{ fill: '#f0f0f5', fontSize: 13, fontFamily: 'Inter' }}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={28}>
                  {varianceData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="insight-cards animate-fade-in delay-3" style={{ marginTop: 'var(--space-8)' }}>
            <div className="variance-insight">
              <div className="insight-highlight text-gradient-alt">41.2%</div>
              <h4>Prompt Wording</h4>
              <p>The largest single source of variance. Different phrasings produce statistically different preference distributions on identical design pairs.</p>
            </div>
            <div className="variance-insight">
              <div className="insight-highlight text-gradient">32.2%</div>
              <h4>Semantic Signal</h4>
              <p>The actual design preference you want to measure. With raw testing, it's drowned out by prompt artifacts and sampling noise.</p>
            </div>
            <div className="variance-insight">
              <div className="insight-highlight" style={{ color: 'var(--accent-teal)' }}>25.1%</div>
              <h4>Repeat Sampling</h4>
              <p>Even with the same prompt and same model, repeating the query yields different answers ~25% of the time.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── FINDING 2: ORDER BIAS ── */}
      <section className="section section-border-top bg-surface">
        <div className="container">
          <div className="finding-block animate-fade-in">
            <div className="finding-number">02</div>
            <div className="finding-content">
              <h2>Position Bias — The 37.7% Flip</h2>
              <p>
                When we swap the display order (A/B → B/A), <strong>37.7%</strong> of LLM verdicts
                flip to the other option. The model isn't comparing designs — it's often just
                picking whichever design appears first (or second, depending on the model family).
              </p>
              <p>
                This is why CSUP's first step is <strong>order counterbalancing</strong>: run both
                A/B and B/A orders, then normalize slots to semantic choices. This single step
                cuts instability from σ = 0.333 to σ = 0.090.
              </p>
            </div>
          </div>

          <div className="stat-grid animate-fade-in delay-2" style={{ marginTop: 'var(--space-8)', maxWidth: '700px', margin: 'var(--space-8) auto 0' }}>
            <div className="stat-card">
              <div className="stat-value text-gradient-alt">37.7%</div>
              <div className="stat-label">Verdicts Flipped by Order</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient-teal">σ 0.090</div>
              <div className="stat-label">After Counterbalancing</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FINDING 3: HALLUCINATION OF DEPTH ── */}
      <section className="section section-border-top">
        <div className="container">
          <div className="finding-block animate-fade-in">
            <div className="finding-number">03</div>
            <div className="finding-content">
              <h2>The Hallucination of Depth</h2>
              <p>
                Intuition says richer personas should produce more reliable results. Our data
                says the opposite. Cross-model agreement <strong>drops</strong> as persona detail increases:
              </p>
              <ul className="finding-list">
                <li><strong>Demographic</strong> personas (age, gender, occupation): <span className="mono" style={{ color: 'var(--accent-emerald)' }}>71.1% agreement</span></li>
                <li><strong>Biographical</strong> personas (+ habits, preferences): <span className="mono" style={{ color: 'var(--accent-amber)' }}>68.3% agreement</span></li>
                <li><strong>Interview-grounded</strong> personas (+ verbatim quotes): <span className="mono" style={{ color: 'var(--accent-red)' }}>65.5% agreement</span></li>
              </ul>
              <p>
                More detail gives each model more "room to interpret," introducing new variance
                rather than grounding the evaluation. We call this the <em>hallucination of depth</em>.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── BETWEEN-MODEL AGREEMENT TABLE ── */}
      <section className="section section-border-top bg-elevated">
        <div className="container">
          <div className="section-header text-center animate-fade-in">
            <div className="section-eyebrow"><RefreshCcw size={14} /> Experiment 1</div>
            <h2 className="section-title">Between-Model <span className="text-gradient">Agreement</span></h2>
            <p className="section-desc">
              Fleiss' κ = 0.619 across 16,560 persona-conditioned iterations — substantial agreement,
              but not interchangeable. Agreement is reliability, not validity.
            </p>
          </div>

          <div className="container-narrow">
            <div className="table-wrapper animate-fade-in delay-2">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model Pair</th>
                    <th>Cohen's κ</th>
                    <th>Raw Agreement</th>
                  </tr>
                </thead>
                <tbody>
                  {agreementData.map((row, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{row.pair}</td>
                      <td><code style={{ color: 'var(--accent-purple)' }}>{row.kappa.toFixed(3)}</code></td>
                      <td>{row.agree}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* ── BOTTOM NAV ── */}
      <section className="section">
        <div className="container text-center">
          <Link to="/pipeline" className="btn btn-primary btn-lg">
            Next: The CSUP Pipeline <ArrowLeft size={18} style={{ transform: 'rotate(180deg)' }} />
          </Link>
        </div>
      </section>
    </PageWrapper>
  );
}
