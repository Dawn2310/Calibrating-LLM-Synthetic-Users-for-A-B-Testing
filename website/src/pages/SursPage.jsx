import React from 'react';
import { Link } from 'react-router-dom';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer
} from 'recharts';
import { ArrowLeft, ShieldCheck, ArrowRight } from 'lucide-react';
import { PageWrapper } from '../components';
import { sursData, radarData } from '../data';

export default function SursPage() {
  return (
    <PageWrapper>
      {/* ── HEADER ── */}
      <section className="page-header section">
        <div className="container">
          <Link to="/" className="back-link animate-fade-in"><ArrowLeft size={16} /> Back to Home</Link>
          <div className="animate-fade-in delay-1">
            <div className="section-eyebrow"><ShieldCheck size={14} /> Reliability Metric</div>
            <h1 className="page-title">Synthetic User <span className="text-gradient-teal">Reliability Score</span></h1>
            <p className="page-desc">
              SURS combines five stability coefficients into a single composite score.
              It tells you whether a result is trustworthy — not whether it matches human preference.
            </p>
          </div>
        </div>
      </section>

      {/* ── FORMULA ── */}
      <section className="section">
        <div className="container-narrow">
          <div className="surs-formula-block animate-fade-in">
            <h3 style={{ marginBottom: 'var(--space-4)', textAlign: 'center' }}>The SURS Formula</h3>
            <div className="surs-formula">
              SURS = Σ w<sub>c</sub> · R<sub>c</sub> &nbsp;&nbsp; where w = 0.20 for all components
            </div>
            <p style={{ textAlign: 'center', marginTop: 'var(--space-4)', color: 'var(--text-secondary)' }}>
              Equal weighting across all five stability dimensions. Each component captures a
              different axis of measurement noise.
            </p>
          </div>
        </div>
      </section>

      {/* ── FIVE COMPONENTS ── */}
      <section className="section section-border-top bg-surface">
        <div className="container">
          <div className="section-header text-center animate-fade-in">
            <h2 className="section-title">Five <span className="text-gradient">Components</span></h2>
          </div>

          <div className="surs-cards-grid">
            {sursData.map((s, i) => (
              <div key={i} className="surs-card animate-fade-in" style={{ animationDelay: `${(i + 1) * 100}ms` }}>
                <div className="surs-card-symbol mono">{s.symbol}</div>
                <h4>{s.component}</h4>
                <p>{s.description}</p>
                <div className="surs-card-weight">Weight: <span className="mono">{s.weight}</span></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── RADAR CHART ── */}
      <section className="section section-border-top">
        <div className="container">
          <div className="surs-radar-layout">
            <div className="animate-fade-in">
              <h2 className="section-title" style={{ marginBottom: 'var(--space-6)' }}>SURS <span className="text-gradient-teal">Profiles</span></h2>
              <p style={{ marginBottom: 'var(--space-6)' }}>
                The radar chart shows typical component profiles for high, moderate, and low
                SURS test cases. Notice how "Prompt Robustness" is the primary differentiator —
                cases that fail tend to be highly prompt-sensitive.
              </p>

              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>SURS Range</th>
                      <th>Level</th>
                      <th>Recommended Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="mono">≥ 0.80</td>
                      <td><span className="surs-badge surs-high">HIGH</span></td>
                      <td>Usable as early-stage directional signal</td>
                    </tr>
                    <tr>
                      <td className="mono">0.60 – 0.79</td>
                      <td><span className="surs-badge surs-moderate">MODERATE</span></td>
                      <td>Exploratory only; validate with humans</td>
                    </tr>
                    <tr>
                      <td className="mono">{'<'} 0.60</td>
                      <td><span className="surs-badge surs-low">LOW</span></td>
                      <td>Do not trust; commission human study</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="chart-container animate-fade-in delay-3">
              <div className="chart-title">Component Profiles by Reliability Level</div>
              <ResponsiveContainer width="100%" height={380}>
                <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.08)" />
                  <PolarAngleAxis dataKey="axis" tick={{ fill: '#8b8b9e', fontSize: 13 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 1]} tick={{ fill: '#5a5a6e', fontSize: 10 }} />
                  <Radar name="High SURS" dataKey="high" stroke="#34d399" fill="#34d399" fillOpacity={0.15} strokeWidth={2} />
                  <Radar name="Moderate" dataKey="moderate" stroke="#fbbf24" fill="#fbbf24" fillOpacity={0.08} strokeWidth={2} />
                  <Radar name="Low SURS" dataKey="low" stroke="#f87171" fill="#f87171" fillOpacity={0.06} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
              <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-6)', marginTop: 'var(--space-4)', flexWrap: 'wrap' }}>
                <span className="surs-badge surs-high">● High (4 cases)</span>
                <span className="surs-badge surs-moderate">● Moderate (24 cases)</span>
                <span className="surs-badge surs-low">● Low (5 cases)</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── CASE DISTRIBUTION ── */}
      <section className="section section-border-top bg-elevated">
        <div className="container">
          <div className="stat-grid animate-fade-in" style={{ maxWidth: '700px', margin: '0 auto' }}>
            <div className="stat-card">
              <div className="stat-value" style={{ color: 'var(--accent-emerald)' }}>4</div>
              <div className="stat-label">High Reliability</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: 'var(--accent-amber)' }}>24</div>
              <div className="stat-label">Moderate Reliability</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: 'var(--accent-red)' }}>5</div>
              <div className="stat-label">Low Reliability</div>
            </div>
          </div>
          <p className="animate-fade-in delay-2" style={{ textAlign: 'center', marginTop: 'var(--space-6)', maxWidth: '600px', margin: 'var(--space-6) auto 0' }}>
            Out of 33 test cases, 28 (85%) achieved at least moderate reliability after CSUP calibration —
            only 5 cases remained too noisy for any synthetic signal.
          </p>
        </div>
      </section>

      {/* ── BOTTOM NAV ── */}
      <section className="section">
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
          <Link to="/pipeline" className="btn btn-secondary btn-lg">
            <ArrowLeft size={18} /> Pipeline
          </Link>
          <Link to="/models" className="btn btn-primary btn-lg">
            Models Evaluated <ArrowRight size={18} />
          </Link>
        </div>
      </section>
    </PageWrapper>
  );
}
