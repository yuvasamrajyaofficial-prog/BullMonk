import React, { useState } from 'react';
import { 
  FiShield, FiZap, FiServer, FiAlertTriangle, FiCheckCircle, 
  FiCpu, FiLock, FiActivity, FiRefreshCw, FiArrowRight, FiSliders
} from 'react-icons/fi';

export default function RiskAndExecutionGateway() {
  const [circuitBreakerTriggered, setCircuitBreakerTriggered] = useState(false);
  const [testLog, setTestLog] = useState([
    { id: 'EV-1092', time: '14:32:01.104', type: 'PRE_TRADE_CHECK', result: 'PASSED', msg: 'Order #9812 within 1.5% fat-finger collar & max position size.' },
    { id: 'EV-1091', time: '14:28:44.892', type: 'ROUTING_DISPATCH', result: 'FILLED', msg: 'Routed to DhanHQ low-latency gateway. Fill latency: 1.2ms.' },
    { id: 'EV-1090', time: '14:15:22.012', type: 'MARGIN_CHECK', result: 'PASSED', msg: 'Portfolio margin utilization verified at 38.0% (Cap: 80.0%).' }
  ]);

  const handleSimulateRiskBreach = () => {
    setCircuitBreakerTriggered(true);
    const newEvent = {
      id: `EV-${Math.floor(1000 + Math.random() * 9000)}`,
      time: new Date().toLocaleTimeString('en-US', { hour12: false }) + '.' + Math.floor(100 + Math.random() * 899),
      type: 'RISK_CIRCUIT_BREAKER',
      result: 'REJECTED',
      msg: 'CRITICAL: Sizing limit exceeded (Attempted 35.0% NAV vs 15.0% cap). Order dropped in 0.42ms.'
    };
    setTestLog(prev => [newEvent, ...prev]);

    setTimeout(() => {
      setCircuitBreakerTriggered(false);
    }, 4500);
  };

  const brokers = [
    {
      name: 'DhanHQ API v2',
      asset: 'Indian Equities & F&O',
      latency: '1.2ms',
      uptime: '99.99%',
      status: 'CONNECTED',
      badge: 'Primary F&O Gateway',
      rateLimit: '25 req/s',
      color: '#10b981'
    },
    {
      name: 'Zerodha Kite Connect',
      asset: 'Cash Equities & Commodity',
      latency: '2.1ms',
      uptime: '99.95%',
      status: 'CONNECTED',
      badge: 'Cash Gateway',
      rateLimit: '10 req/s',
      color: '#38bdf8'
    },
    {
      name: 'Binance Futures',
      asset: 'Crypto Perps (BTC/ETH)',
      latency: '4.8ms',
      uptime: '99.98%',
      status: 'CONNECTED',
      badge: 'Crypto Liquidity',
      rateLimit: '50 req/s',
      color: '#f59e0b'
    },
    {
      name: 'Interactive Brokers',
      asset: 'Forex & Global Stocks',
      latency: '6.4ms',
      uptime: '99.90%',
      status: 'STANDBY',
      badge: 'Global Router',
      rateLimit: '15 req/s',
      color: '#a855f7'
    }
  ];

  return (
    <div id="risk-gateway" className="quant-section" style={{ padding: '80px 24px', background: 'var(--bg-obsidian-surface)' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '20px', marginBottom: '32px' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '4px 12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '20px', fontSize: '11px', color: '#f87171', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '12px' }}>
              <FiShield /> Sub-Millisecond Pre-Trade Risk & Smart OMS
            </div>
            <h2 style={{ fontSize: 'clamp(1.8rem, 3.5vw, 2.6rem)', fontWeight: 800, color: '#f8fafc', margin: 0, letterSpacing: '-0.5px' }}>
              Institutional <span style={{ background: 'var(--accent-gold-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Risk Guardrails & Routing</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: '8px 0 0 0', maxWidth: '650px' }}>
              Every algorithm passes strict deterministic pre-trade risk checks before order dispatch. SEBI compliant risk collars with zero-latency fail-safes.
            </p>
          </div>

          <button 
            onClick={handleSimulateRiskBreach}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              background: circuitBreakerTriggered ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              border: circuitBreakerTriggered ? '1px solid #ef4444' : '1px solid var(--border-subtle)',
              borderRadius: '8px',
              color: circuitBreakerTriggered ? '#ef4444' : '#f8fafc',
              fontSize: '13px',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <FiAlertTriangle />
            {circuitBreakerTriggered ? 'Killswitch Triggered!' : 'Test Risk Killswitch'}
          </button>
        </div>

        {/* 6 Pre-Trade Risk Gates */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '32px' }}>
          
          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '12px', padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FiLock color="#10b981" /> Drawdown Circuit Breaker
              </span>
              <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', fontWeight: 700 }}>ACTIVE</span>
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'JetBrains Mono', color: '#10b981', margin: '4px 0' }}>
              -1.12% <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>/ -5.00% Limit</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Instant liquidation if intraday peak-to-trough hits 5.0%.</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '12px', padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FiSliders color="#38bdf8" /> Max Position Size Collar
              </span>
              <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', fontWeight: 700 }}>ENFORCED</span>
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'JetBrains Mono', color: '#38bdf8', margin: '4px 0' }}>
              7.4% <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>/ 15.0% NAV Cap</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Maximum 15% single ticker capital allocation per execution.</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '12px', padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FiZap color="#fbbf24" /> Fat-Finger Price Band
              </span>
              <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(251, 191, 36, 0.15)', color: '#fbbf24', fontWeight: 700 }}>±1.50%</span>
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'JetBrains Mono', color: '#fbbf24', margin: '4px 0' }}>
              0.08% <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Slippage Deviation</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Orders beyond 1.5% of prevailing Last Traded Price are dropped.</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '12px', padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FiAlertTriangle color="#a855f7" /> Daily Loss Hard Stop
              </span>
              <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7', fontWeight: 700 }}>SAFE</span>
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'JetBrains Mono', color: 'var(--profit-green)', margin: '4px 0' }}>
              +₹14,250 <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>/ -₹50k Stop</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Global killswitch disarms all active algorithms upon breach.</div>
          </div>

        </div>

        {/* Multi-Broker Routing Gateway Grid */}
        <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FiServer color="#60a5fa" /> Connected Low-Latency Broker Gateways
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '32px' }}>
          {brokers.map((broker, idx) => (
            <div 
              key={idx}
              style={{
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '20px',
                position: 'relative'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  {broker.badge}
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', fontSize: '11px', color: broker.color, fontWeight: 700 }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: broker.color }}></span>
                  {broker.status}
                </span>
              </div>

              <div style={{ fontSize: '16px', fontWeight: 800, color: '#f8fafc', marginBottom: '4px' }}>
                {broker.name}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                {broker.asset}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', paddingTop: '12px', borderTop: '1px solid var(--border-subtle)', fontFamily: 'JetBrains Mono', fontSize: '11px' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '10px' }}>ROUNDTRIP</span>
                  <strong style={{ color: '#f8fafc' }}>{broker.latency}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '10px' }}>THROUGHPUT</span>
                  <strong style={{ color: '#f8fafc' }}>{broker.rateLimit}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Live OMS Audit Log */}
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '12px', overflow: 'hidden' }}>
          <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FiActivity color="#10b981" /> Order Management System (OMS) Audit Stream
            </span>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>
              Sub-millisecond Pre-Trade Telemetry
            </span>
          </div>

          <div style={{ padding: '12px 20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {testLog.map((log, idx) => (
              <div 
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '16px',
                  padding: '10px 14px',
                  background: log.result === 'REJECTED' ? 'rgba(239, 68, 68, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  border: log.result === 'REJECTED' ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid transparent',
                  borderRadius: '6px',
                  fontFamily: 'JetBrains Mono',
                  fontSize: '12px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ color: '#94a3b8', fontSize: '11px' }}>{log.time}</span>
                  <span style={{ 
                    padding: '2px 6px', 
                    borderRadius: '4px', 
                    fontSize: '10px', 
                    fontWeight: 700,
                    background: log.result === 'PASSED' ? 'rgba(16, 185, 129, 0.15)' : log.result === 'FILLED' ? 'rgba(56, 189, 248, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: log.result === 'PASSED' ? '#10b981' : log.result === 'FILLED' ? '#38bdf8' : '#ef4444'
                  }}>
                    {log.result}
                  </span>
                  <span style={{ color: '#cbd5e1' }}>{log.msg}</span>
                </div>
                <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>{log.id}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
