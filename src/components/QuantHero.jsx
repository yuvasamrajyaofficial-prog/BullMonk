import React from 'react';
import { FaChartLine, FaRobot, FaShieldAlt, FaCheckCircle, FaDatabase, FaBolt, FaTerminal } from 'react-icons/fa';

const QuantHero = ({ onNavigate }) => {
  return (
    <section id="overview" style={styles.heroSection}>
      <div className="grid-overlay" />

      <div className="container" style={styles.container}>
        {/* Top Tag */}
        <div style={styles.tagWrapper}>
          <div className="section-tag">
            <FaBolt size={11} color="#F5A623" />
            <span>Phase 2 Quantitative Engine Verified</span>
          </div>
        </div>

        {/* Main Headline */}
        <h1 style={styles.title}>
          Institutional Algorithmic & <br />
          <span className="text-gradient-gold">AI Quantitative Trading</span> Platform
        </h1>

        <p style={styles.subtitle}>
          Engineered for <strong>Indian Equities (NSE)</strong>, <strong>NIFTY Index Derivatives (NFO)</strong>,
          <strong> Crypto</strong>, and <strong>Forex</strong>. Built with deterministic backtesting,
          synthetic market-data generation, pre-trade risk gating, and decoupled broker routing.
        </p>

        {/* Action CTAs */}
        <div style={styles.ctaGroup}>
          <button
            className="btn btn-primary"
            onClick={() => onNavigate && onNavigate('market-data')}
            style={{ fontSize: '1rem', padding: '0.8rem 1.8rem' }}
          >
            <FaChartLine />
            Launch NIFTY Market Data
          </button>
          <button
            className="btn btn-outline"
            onClick={() => onNavigate && onNavigate('ai-lab')}
            style={{ fontSize: '1rem', padding: '0.8rem 1.8rem' }}
          >
            <FaRobot />
            AI Strategy Generator
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => onNavigate && onNavigate('architecture')}
            style={{ fontSize: '0.95rem', padding: '0.8rem 1.4rem' }}
          >
            <FaTerminal />
            System Architecture
          </button>
        </div>

        {/* Quant Metric Cards Grid */}
        <div style={styles.statsGrid}>
          <div className="glass-card" style={styles.statCard}>
            <div style={styles.statHeader}>
              <span style={styles.statLabel}>ANNUALIZED SHARPE</span>
              <span className="badge badge-profit">+2.84</span>
            </div>
            <div style={styles.statVal} className="font-mono">2.84</div>
            <div style={styles.statSub}>Sortino 3.62 | Calmar 3.41</div>
          </div>

          <div className="glass-card" style={styles.statCard}>
            <div style={styles.statHeader}>
              <span style={styles.statLabel}>MAX PERIOD DRAWDOWN</span>
              <span className="badge badge-cyan">Controlled</span>
            </div>
            <div style={{ ...styles.statVal, color: 'var(--text-primary)' }} className="font-mono">-3.18%</div>
            <div style={styles.statSub}>Pre-trade circuit breakers active</div>
          </div>

          <div className="glass-card" style={styles.statCard}>
            <div style={styles.statHeader}>
              <span style={styles.statLabel}>ENGINE INTEGRITY</span>
              <span className="badge badge-profit"><FaCheckCircle size={10} /> 100% Pass</span>
            </div>
            <div style={{ ...styles.statVal, color: 'var(--profit-green)' }} className="font-mono">202 / 202</div>
            <div style={styles.statSub}>Unit & integration tests passing</div>
          </div>

          <div className="glass-card" style={styles.statCard}>
            <div style={styles.statHeader}>
              <span style={styles.statLabel}>DATA RESOLUTIONS</span>
              <span className="badge badge-gold">Multi-Asset</span>
            </div>
            <div style={{ ...styles.statVal, color: 'var(--accent-gold)' }} className="font-mono">1m — 1d</div>
            <div style={styles.statSub}>NIFTY Cash, Futures & 50-pt Options</div>
          </div>
        </div>

        {/* Key Feature Pillars */}
        <div style={styles.pillarsGrid}>
          <div style={styles.pillarItem}>
            <FaDatabase color="#F5A623" size={16} />
            <div>
              <div style={styles.pillarTitle}>Parquet Columnar Cache</div>
              <div style={styles.pillarDesc}>Sub-millisecond analytical query speed with exact Decimal precision.</div>
            </div>
          </div>

          <div style={styles.pillarItem}>
            <FaRobot color="#A855F7" size={16} />
            <div>
              <div style={styles.pillarTitle}>Prompt-to-Algo Synthesis</div>
              <div style={styles.pillarDesc}>Translate natural language trading logic into verified Python BaseStrategy code.</div>
            </div>
          </div>

          <div style={styles.pillarItem}>
            <FaShieldAlt color="#00F5A0" size={16} />
            <div>
              <div style={styles.pillarTitle}>Pre-Trade Risk Gatekeeper</div>
              <div style={styles.pillarDesc}>Position limits, daily drawdown limits, and fat-finger order prevention.</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

const styles = {
  heroSection: {
    position: 'relative',
    padding: '4.5rem 0 3rem 0',
    overflow: 'hidden',
    borderBottom: '1px solid var(--border-subtle)',
  },
  container: {
    position: 'relative',
    zIndex: 1,
    textAlign: 'center',
  },
  tagWrapper: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '0.75rem',
  },
  title: {
    fontSize: 'clamp(2.4rem, 5.2vw, 4.2rem)',
    fontWeight: 800,
    lineHeight: 1.15,
    marginBottom: '1.2rem',
    maxWidth: '1000px',
    marginLeft: 'auto',
    marginRight: 'auto',
  },
  subtitle: {
    fontSize: 'clamp(1rem, 1.8vw, 1.25rem)',
    color: 'var(--text-secondary)',
    maxWidth: '820px',
    margin: '0 auto 2.5rem auto',
    lineHeight: 1.6,
  },
  ctaGroup: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '1rem',
    flexWrap: 'wrap',
    marginBottom: '3.5rem',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: '1.25rem',
    marginBottom: '3rem',
    textAlign: 'left',
  },
  statCard: {
    padding: '1.5rem',
  },
  statHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.75rem',
  },
  statLabel: {
    fontSize: '0.72rem',
    fontWeight: 700,
    color: 'var(--text-muted)',
    letterSpacing: '0.05em',
  },
  statVal: {
    fontSize: '2rem',
    fontWeight: 800,
    lineHeight: 1,
    marginBottom: '0.5rem',
  },
  statSub: {
    fontSize: '0.8rem',
    color: 'var(--text-secondary)',
  },
  pillarsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '1.5rem',
    textAlign: 'left',
    padding: '1.5rem',
    borderRadius: '12px',
    background: 'rgba(255, 255, 255, 0.02)',
    border: '1px solid var(--border-subtle)',
  },
  pillarItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.85rem',
  },
  pillarTitle: {
    fontWeight: 700,
    fontSize: '0.95rem',
    color: 'var(--text-primary)',
    marginBottom: '0.2rem',
  },
  pillarDesc: {
    fontSize: '0.82rem',
    color: 'var(--text-secondary)',
    lineHeight: 1.5,
  },
};

export default QuantHero;
