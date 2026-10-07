import React from 'react';
import { FiTrendingUp, FiShield, FiCpu, FiGithub, FiExternalLink, FiServer, FiTerminal } from 'react-icons/fi';

export default function Footer() {
  return (
    <footer style={{ background: '#030712', borderTop: '1px solid var(--border-subtle)', position: 'relative', zIndex: 10, padding: '60px 24px 24px 24px' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        
        {/* Top Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '40px', marginBottom: '48px' }}>
          
          {/* Brand info */}
          <div style={{ maxWidth: '340px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'var(--accent-gold-gradient)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 16px rgba(245, 166, 35, 0.4)'
              }}>
                <span style={{ fontSize: '18px', fontWeight: 900, color: '#000', lineHeight: 1 }}>B</span>
              </div>
              <span style={{ fontSize: '20px', fontWeight: 800, color: '#fff', letterSpacing: '-0.5px' }}>
                BULL<span style={{ background: 'var(--accent-gold-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>MONK</span>
              </span>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: '1.6', margin: '0 0 16px 0' }}>
              Production-grade institutional algorithmic and AI quantitative trading engine supporting Indian Equities (NSE), NIFTY F&O, Crypto, and Global Forex.
            </p>

            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span style={{ fontSize: '11px', padding: '4px 8px', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.2)', fontFamily: 'JetBrains Mono' }}>
                202/202 Tests Passing
              </span>
              <span style={{ fontSize: '11px', padding: '4px 8px', borderRadius: '4px', background: 'rgba(255, 255, 255, 0.05)', color: '#94a3b8', fontFamily: 'JetBrains Mono' }}>
                v2.4.0-algo
              </span>
            </div>
          </div>

          {/* Subsystems */}
          <div>
            <h4 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '1px', marginBottom: '16px' }}>
              Platform Subsystems
            </h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              <li><a href="#market-data" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>NIFTY 50 Market Data Engine</a></li>
              <li><a href="#option-chain" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>High-Speed Option Greeks Ladder</a></li>
              <li><a href="#ai-lab" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>AI Hypothesis to Python Generator</a></li>
              <li><a href="#backtesting" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Vectorized & Tick Backtester</a></li>
              <li><a href="#risk" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Sub-Millisecond Pre-Trade Risk Gate</a></li>
            </ul>
          </div>

          {/* Quantitative Stack */}
          <div>
            <h4 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '1px', marginBottom: '16px' }}>
              Technology Architecture
            </h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              <li><span style={{ color: 'var(--text-secondary)' }}>Python 3.12 Core Quantitative Engine</span></li>
              <li><span style={{ color: 'var(--text-secondary)' }}>Parquet ZSTD Compressed Local Cache</span></li>
              <li><span style={{ color: 'var(--text-secondary)' }}>GBM + Jump Diffusion Synthetic Engine</span></li>
              <li><span style={{ color: 'var(--text-secondary)' }}>DhanHQ & Zerodha Kite Connect APIs</span></li>
              <li><span style={{ color: 'var(--text-secondary)' }}>Event-Driven State Machine Runner</span></li>
            </ul>
          </div>

          {/* Compliance & Repo */}
          <div>
            <h4 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '1px', marginBottom: '16px' }}>
              Open Source & Verification
            </h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              <li>
                <a 
                  href="https://github.com/yuvasamrajyaofficial-prog/BullMonk" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  style={{ color: '#38bdf8', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                >
                  <FiGithub /> GitHub Repository <FiExternalLink size={12} />
                </a>
              </li>
              <li><a href="#architecture" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Architecture Verification</a></li>
              <li><a href="#risk" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>SEBI Risk Management Protocols</a></li>
              <li><span style={{ color: 'var(--text-secondary)' }}>Offline Deterministic Mode: Enabled</span></li>
            </ul>
          </div>

        </div>

        {/* Regulatory & Institutional Notice */}
        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '24px', marginBottom: '24px' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '11px', lineHeight: '1.6', margin: 0 }}>
            <strong>Institutional Quantitative Trading Disclaimer:</strong> BullMonk is an algorithmic trading engineering framework designed for systematic quantitative research, strategy backtesting, and automated trade execution. Algorithmic trading and derivative transactions (Futures & Options) involve substantial risk of loss and are not suitable for all investors. All algorithms must be backtested, walk-forward verified, and paper-traded prior to live capital deployment. Pre-trade risk parameters and SEBI compliance guidelines should be maintained at all times.
          </p>
        </div>

        {/* Copyright Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', color: 'var(--text-muted)', fontSize: '11px', fontFamily: 'JetBrains Mono' }}>
          <div>
            &copy; {new Date().getFullYear()} BullMonk Quantitative Trading Systems. All rights reserved.
          </div>
          <div>
            Powered by Python 3.12 • Parquet Cache • Low Latency Order OMS
          </div>
        </div>

      </div>
    </footer>
  );
}
