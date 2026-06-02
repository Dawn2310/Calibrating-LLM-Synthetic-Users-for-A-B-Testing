import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FlaskConical } from 'lucide-react';
import { PageWrapper } from '../components';
import { modelsInfo, agreementData } from '../data';

export default function ModelsPage() {
  return (
    <PageWrapper>
      {/* ── HEADER ── */}
      <section className="page-header section">
        <div className="container">
          <Link to="/" className="back-link animate-fade-in"><ArrowLeft size={16} /> Back to Home</Link>
          <div className="animate-fade-in delay-1">
            <div className="section-eyebrow"><FlaskConical size={14} /> Experimental Setup</div>
            <h1 className="page-title">Models <span className="text-gradient">Evaluated</span></h1>
            <p className="page-desc">
              Four LLMs from distinct architectural families, queried at temperature 0.7
              with JSON-constrained output. Diversity across providers reduces single-vendor bias.
            </p>
          </div>
        </div>
      </section>

      {/* ── MODEL CARDS ── */}
      <section className="section">
        <div className="container">
          <div className="models-detail-grid">
            {modelsInfo.map((m, i) => (
              <div key={i} className="model-detail-card animate-fade-in" style={{ animationDelay: `${(i + 1) * 100}ms` }}>
                <div className="model-card-icon">{m.icon}</div>
                <h3>{m.name}</h3>
                <div className="model-card-type">{m.provider}</div>
                <div className="model-card-arch">{m.arch}</div>
                <div className="model-detail-specs">
                  <div className="spec-row">
                    <span>Temperature</span>
                    <span className="mono">0.7</span>
                  </div>
                  <div className="spec-row">
                    <span>Output Format</span>
                    <span className="mono">JSON</span>
                  </div>
                  <div className="spec-row">
                    <span>Calls/Test Case</span>
                    <span className="mono">~914</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── PAIRWISE AGREEMENT ── */}
      <section className="section section-border-top bg-surface">
        <div className="container">
          <div className="section-header text-center animate-fade-in">
            <h2 className="section-title">Pairwise <span className="text-gradient">Agreement</span></h2>
            <p className="section-desc">
              Cohen's κ between each model pair. GPT-4o and Llama 3.3 show the highest pairwise
              agreement (κ = 0.664), while Claude and Llama are most divergent (κ = 0.576).
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
                    <th>Level</th>
                  </tr>
                </thead>
                <tbody>
                  {agreementData.map((row, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{row.pair}</td>
                      <td><code style={{ color: 'var(--accent-purple)' }}>{row.kappa.toFixed(3)}</code></td>
                      <td>{row.agree}</td>
                      <td>
                        <span className={`surs-badge ${row.kappa >= 0.61 ? 'surs-moderate' : 'surs-moderate'}`}>
                          {row.kappa >= 0.61 ? 'SUBSTANTIAL' : 'MODERATE'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* ── COST ANALYSIS ── */}
      <section className="section section-border-top">
        <div className="container">
          <div className="section-header text-center animate-fade-in">
            <h2 className="section-title">Cost <span className="text-gradient-teal">Analysis</span></h2>
          </div>

          <div className="stat-grid animate-fade-in delay-2" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <div className="stat-card">
              <div className="stat-value text-gradient">30,179</div>
              <div className="stat-label">Total API Calls</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient-teal">~$14</div>
              <div className="stat-label">Total Cost</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient-alt">$0.42</div>
              <div className="stat-label">Per Test Case</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient">{'<'}$0.001</div>
              <div className="stat-label">Per API Call</div>
            </div>
          </div>

          <p className="animate-fade-in delay-3" style={{ textAlign: 'center', marginTop: 'var(--space-8)', maxWidth: '600px', margin: 'var(--space-8) auto 0' }}>
            The entire 30K-call experiment costs less than compensating <strong>a single user-study participant</strong>
            at standard market-research rates.
          </p>
        </div>
      </section>

      {/* ── BOTTOM NAV ── */}
      <section className="section">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
          <Link to="/surs" className="btn btn-secondary btn-lg">
            <ArrowLeft size={18} /> SURS Score
          </Link>
          <Link to="/" className="btn btn-primary btn-lg">
            Back to Home <ArrowLeft size={18} style={{ transform: 'rotate(180deg)' }} />
          </Link>
        </div>
      </section>
    </PageWrapper>
  );
}
