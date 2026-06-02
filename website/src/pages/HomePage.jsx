import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Layers, Activity, SplitSquareHorizontal, Users, BarChart3, ShieldCheck, FlaskConical, ExternalLink } from 'lucide-react';
import { PageWrapper } from '../components';
import { experimentsOverview } from '../data';

export default function HomePage() {
  return (
    <PageWrapper>
      {/* ── HERO ── */}
      <header className="hero section">
        <div className="container">
          <div className="hero-inner animate-fade-in">
            <div className="hero-badge">
              <span className="hero-badge-dot" />
              HCOMP 2026 · Research Paper
            </div>

            <h1 className="hero-title">
              From Synthetic Users to<br />
              <span className="text-gradient">Calibrated Instruments</span>
            </h1>

            <p className="hero-subtitle">
              Decomposing Uncertainty in LLM-Based A/B Testing — a reliability-aware
              framework that treats AI evaluators as noisy measurements, not
              perfect preference engines.
            </p>

            <div className="hero-actions">
              <Link to="/findings" className="btn btn-primary btn-lg">
                Explore Findings <ArrowRight size={18} />
              </Link>
              <Link to="/pipeline" className="btn btn-secondary btn-lg">
                <Layers size={18} /> How CSUP Works
              </Link>
            </div>

            <div className="hero-meta animate-fade-in delay-3">
              <div className="hero-meta-item">
                <div className="hero-meta-value text-gradient">30,179</div>
                <div className="hero-meta-label">API Calls</div>
              </div>
              <div className="hero-meta-item">
                <div className="hero-meta-value text-gradient">4</div>
                <div className="hero-meta-label">LLM Families</div>
              </div>
              <div className="hero-meta-item">
                <div className="hero-meta-value text-gradient">33</div>
                <div className="hero-meta-label">Test Cases</div>
              </div>
              <div className="hero-meta-item">
                <div className="hero-meta-value text-gradient">60</div>
                <div className="hero-meta-label">Personas</div>
              </div>
              <div className="hero-meta-item">
                <div className="hero-meta-value text-gradient">~$14</div>
                <div className="hero-meta-label">Total Cost</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ── KEY STATS BANNER ── */}
      <section className="stats-section">
        <div className="container">
          <div className="stat-grid animate-fade-in">
            <div className="stat-card">
              <div className="stat-value text-gradient-alt">41.2%</div>
              <div className="stat-label">Prompt Wording Variance</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient">37.7%</div>
              <div className="stat-label">Order-Flip Rate (Raw)</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient-teal">σ 0.077</div>
              <div className="stat-label">Post-CSUP Instability</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient">0.619</div>
              <div className="stat-label">Fleiss' κ (4 Models)</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── KEY FINDINGS OVERVIEW ── */}
      <section className="section">
        <div className="container">
          <div className="section-header text-center animate-fade-in">
            <div className="section-eyebrow"><FlaskConical size={14} /> Key Findings</div>
            <h2 className="section-title">Three Critical <span className="text-gradient-alt">Insights</span></h2>
            <p className="section-desc">
              Click each card to explore the full analysis, charts, and data.
            </p>
          </div>

          <div className="findings-grid">
            <Link to="/findings" className="card card-link animate-fade-in delay-1">
              <div className="card-icon card-icon-pink"><Activity size={24} /></div>
              <h3>The Illusion of Preference</h3>
              <p>Prompt wording accounts for <strong>41.2%</strong> of total variance — exceeding the actual semantic signal.</p>
              <span className="card-cta">Read more <ArrowRight size={16} /></span>
            </Link>
            <Link to="/pipeline" className="card card-link animate-fade-in delay-2">
              <div className="card-icon card-icon-blue"><SplitSquareHorizontal size={24} /></div>
              <h3>CSUP Calibration</h3>
              <p>Reduces instability from <strong>σ = 0.333</strong> to <strong>σ = 0.077</strong> — a 77% reduction.</p>
              <span className="card-cta">Explore pipeline <ArrowRight size={16} /></span>
            </Link>
            <Link to="/findings" className="card card-link animate-fade-in delay-3">
              <div className="card-icon card-icon-amber"><Users size={24} /></div>
              <h3>Hallucination of Depth</h3>
              <p>Richer personas <strong>reduce</strong> cross-model consensus from 71.1% to 65.5%.</p>
              <span className="card-cta">See details <ArrowRight size={16} /></span>
            </Link>
          </div>
        </div>
      </section>

      {/* ── ALL 9 EXPERIMENTS OVERVIEW ── */}
      <section className="section section-border-top bg-surface">
        <div className="container">
          <div className="section-header text-center animate-fade-in">
            <div className="section-eyebrow"><BarChart3 size={14} /> Experiments</div>
            <h2 className="section-title">9 Experiments, <span className="text-gradient">One Story</span></h2>
            <p className="section-desc">
              Each experiment peels back a layer of noise in LLM-based evaluation.
            </p>
          </div>

          <div className="experiments-grid animate-fade-in delay-2">
            {experimentsOverview.map((exp) => (
              <div key={exp.id} className="experiment-row">
                <div className="experiment-id">{exp.id}</div>
                <div className="experiment-body">
                  <h4>{exp.title}</h4>
                  <p>{exp.desc}</p>
                </div>
                <div className="experiment-metric mono">{exp.metric}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── AUTHORS ── */}
      <section className="section section-border-top">
        <div className="container">
          <div className="section-header text-center animate-fade-in">
            <div className="section-eyebrow"><Users size={14} /> Authors</div>
            <h2 className="section-title">Research Team</h2>
          </div>

          <div className="authors-card animate-fade-in delay-2">
            <div className="author">
              <div className="author-avatar">ND</div>
              <h4>Nguyen Luong Hai Dang</h4>
              <div className="author-affiliation">Faculty of AI · FPT University</div>
            </div>
            <div className="author">
              <div className="author-avatar">DH</div>
              <h4>Duong Quoc Huu</h4>
              <div className="author-affiliation">Faculty of AI · FPT University</div>
            </div>
          </div>
        </div>
      </section>
    </PageWrapper>
  );
}
