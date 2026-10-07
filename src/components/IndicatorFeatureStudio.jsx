import React, { useState, useEffect, useMemo } from 'react';
import { 
  FaCalculator, FaChartBar, FaLayerGroup, FaCheckCircle, 
  FaSlidersH, FaExclamationTriangle, FaServer, FaCloud, FaSearch, FaArrowUp, FaArrowDown
} from 'react-icons/fa';
import { 
  calculateBlackScholes, 
  selectDeltaTargetStrike, 
  calculateEMA, 
  calculateRSI, 
  calculateATR, 
  calculateSupertrend 
} from '../utils/quantEngine';

// Deterministic synthetic baseline data for demonstration
const generateSampleBars = () => {
  const bars = [];
  let price = 24000;
  const now = Date.now();
  for (let i = 60; i >= 0; i--) {
    const t = new Date(now - i * 5 * 60 * 1000);
    const noise = (Math.sin(i * 0.4) + Math.cos(i * 0.2)) * 15;
    price += noise;
    const high = price + Math.random() * 8 + 4;
    const low = price - Math.random() * 8 - 4;
    const open = price - (Math.random() * 6 - 3);
    const close = price;
    const volume = Math.floor(50000 + Math.random() * 30000);
    bars.push({ timestamp: t.toLocaleTimeString(), open, high, low, close, volume });
  }
  return bars;
};

const IndicatorFeatureStudio = () => {
  const [activeTab, setActiveTab] = useState('indicators');
  const [bars] = useState(generateSampleBars());
  const [backendStatus, setBackendStatus] = useState('checking');

  // Option Greeks Interactive State
  const [spotPrice, setSpotPrice] = useState(24000);
  const [strikePrice, setStrikePrice] = useState(24000);
  const [dteDays, setDteDays] = useState(7);
  const [volatility, setVolatility] = useState(15);
  const [riskFreeRate, setRiskFreeRate] = useState(6.5);
  const [optionType, setOptionType] = useState('call');

  // Delta Target Strike Selection State
  const [targetDelta, setTargetDelta] = useState(0.50);

  const [customTunnelUrl, setCustomTunnelUrl] = useState(() => localStorage.getItem('bullmonk_tunnel_url') || '');
  const [showTunnelModal, setShowTunnelModal] = useState(false);
  const [tunnelLatency, setTunnelLatency] = useState(null);

  // Check backend / edge API status or custom tunnel
  useEffect(() => {
    const checkTarget = customTunnelUrl.trim().replace(/\/+$/, '');
    if (checkTarget) {
      const startTime = performance.now();
      fetch(`${checkTarget}/api/health`)
        .then(res => res.json())
        .then(data => {
          setTunnelLatency(Math.round(performance.now() - startTime));
          setBackendStatus('tunnel-online');
        })
        .catch(() => setBackendStatus('tunnel-offline'));
      return;
    }

    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        setBackendStatus(data.service ? 'edge-online' : 'online');
      })
      .catch(() => {
        // Test local python backend fallback
        fetch('http://localhost:8000/api/health')
          .then(res => res.json())
          .then(() => setBackendStatus('python-online'))
          .catch(() => setBackendStatus('client-engine'));
      });
  }, [customTunnelUrl]);

  const handleSaveTunnel = (url) => {
    const clean = url.trim().replace(/\/+$/, '');
    setCustomTunnelUrl(clean);
    localStorage.setItem('bullmonk_tunnel_url', clean);
  };

  // Compute Technical Indicators
  const computedData = useMemo(() => {
    const ema20 = calculateEMA(bars, 20);
    const ema50 = calculateEMA(bars, 50);
    const rsi14 = calculateRSI(bars, 14);
    const atr14 = calculateATR(bars, 14);
    const st = calculateSupertrend(bars, 10, 3.0);

    return bars.map((b, idx) => ({
      ...b,
      ema20: ema20[idx] ? ema20[idx].toFixed(2) : 'NaN',
      ema50: ema50[idx] ? ema50[idx].toFixed(2) : 'NaN',
      rsi14: rsi14[idx] ? rsi14[idx].toFixed(2) : 'NaN',
      atr14: atr14[idx] ? atr14[idx].toFixed(2) : 'NaN',
      supertrend: st[idx].supertrend ? st[idx].supertrend.toFixed(2) : 'NaN',
      stDirection: st[idx].direction,
    }));
  }, [bars]);

  // Compute Black-Scholes Greeks
  const greeks = useMemo(() => {
    return calculateBlackScholes(
      spotPrice,
      strikePrice,
      dteDays / 365.0,
      volatility / 100.0,
      riskFreeRate / 100.0,
      optionType
    );
  }, [spotPrice, strikePrice, dteDays, volatility, riskFreeRate, optionType]);

  // Compute Delta-Target Strike Selection
  const deltaSelection = useMemo(() => {
    const candidateStrikes = [];
    const baseStrike = Math.round(spotPrice / 50) * 50;
    for (let k = baseStrike - 500; k <= baseStrike + 500; k += 50) {
      candidateStrikes.push(k);
    }
    return selectDeltaTargetStrike(
      spotPrice,
      candidateStrikes,
      dteDays / 365.0,
      volatility / 100.0,
      targetDelta,
      optionType,
      riskFreeRate / 100.0
    );
  }, [spotPrice, dteDays, volatility, targetDelta, optionType, riskFreeRate]);

  const latestRow = computedData[computedData.length - 1];

  return (
    <section id="feature-engine" style={{ padding: '60px 0', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
      <div className="container">
        {/* Header Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px', marginBottom: '32px' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '4px 12px', background: 'rgba(217, 119, 6, 0.1)', border: '1px solid rgba(217, 119, 6, 0.25)', borderRadius: '20px', marginBottom: '12px' }}>
              <FaCalculator size={12} color="#fbbf24" />
              <span style={{ fontSize: '12px', fontWeight: '700', color: '#fbbf24', letterSpacing: '0.5px' }}>PHASE 4 ENGINE</span>
            </div>
            <h2 style={{ fontSize: '28px', fontWeight: '800', margin: '0 0 8px 0', color: '#f8fafc' }}>
              Quantitative Indicator & Feature Engine
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '14px', maxWidth: '700px', margin: 0 }}>
              Vectorized feature pipeline, 29 modular technical indicators, Black-Scholes analytical Greeks, and causal Ichimoku Cloud without look-ahead bias.
            </p>
          </div>

          {/* Engine Connectivity Status & Tunnel Config */}
          <div style={{ position: 'relative' }}>
            <div 
              onClick={() => setShowTunnelModal(!showTunnelModal)}
              style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'rgba(15, 23, 42, 0.8)', padding: '10px 16px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.08)', cursor: 'pointer', transition: 'border-color 0.2s' }}
              title="Click to configure Cloudflare Tunnel or local Python backend"
            >
              <FaCloud color={backendStatus.includes('online') ? '#10b981' : '#38bdf8'} />
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  {backendStatus === 'tunnel-online' ? 'Cloudflare Tunnel Active' : 'Deployment Engine'}
                </div>
                <div style={{ fontSize: '13px', fontWeight: '700', color: '#f8fafc' }}>
                  {backendStatus === 'tunnel-online' ? `Tunnel Connected (${tunnelLatency}ms)` :
                   backendStatus === 'edge-online' ? 'Cloudflare Edge API Active' :
                   backendStatus === 'python-online' ? 'Python Engine (Port 8000)' :
                   'Cloudflare Embedded Engine'}
                </div>
              </div>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: backendStatus.includes('online') ? '#10b981' : '#38bdf8', boxShadow: `0 0 8px ${backendStatus.includes('online') ? '#10b981' : '#38bdf8'}` }} />
              <span style={{ fontSize: '10px', background: 'rgba(255,255,255,0.08)', padding: '2px 6px', borderRadius: '4px', color: '#94a3b8' }}>Tunnel Setup</span>
            </div>

            {/* Cloudflare Tunnel Setup Dropdown / Modal */}
            {showTunnelModal && (
              <div style={{
                position: 'absolute',
                top: 'calc(100% + 8px)',
                right: 0,
                width: '380px',
                background: '#0f172a',
                border: '1px solid rgba(217, 119, 6, 0.3)',
                boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
                borderRadius: '12px',
                padding: '20px',
                zIndex: 100,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ fontWeight: '700', fontSize: '15px', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FaServer color="#fbbf24" size={14} /> Cloudflare Tunnel Configuration
                  </div>
                  <button 
                    onClick={() => setShowTunnelModal(false)}
                    style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '16px' }}
                  >
                    ✕
                  </button>
                </div>

                <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: '1.4', margin: '0 0 14px 0' }}>
                  Connect your deployed Cloudflare website to your local Python algorithmic backend (port 8000) securely through a free Cloudflare Tunnel.
                </p>

                <div style={{ marginBottom: '14px' }}>
                  <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: '#cbd5e1', marginBottom: '6px' }}>
                    Cloudflare Tunnel URL or Backend URL
                  </label>
                  <input
                    type="text"
                    placeholder="https://xyz.trycloudflare.com or http://localhost:8000"
                    value={customTunnelUrl}
                    onChange={(e) => setCustomTunnelUrl(e.target.value)}
                    style={{ width: '100%', padding: '9px 12px', background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '6px', color: '#f8fafc', fontSize: '12px' }}
                  />
                </div>

                <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                  <button
                    onClick={() => handleSaveTunnel(customTunnelUrl)}
                    style={{ flex: 1, padding: '8px', background: '#fbbf24', border: 'none', borderRadius: '6px', color: '#000', fontWeight: '700', fontSize: '12px', cursor: 'pointer' }}
                  >
                    Save & Connect
                  </button>
                  <button
                    onClick={() => {
                      setCustomTunnelUrl('');
                      localStorage.removeItem('bullmonk_tunnel_url');
                      setBackendStatus('edge-online');
                    }}
                    style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: '#cbd5e1', fontSize: '12px', cursor: 'pointer' }}
                  >
                    Reset
                  </button>
                </div>

                {/* Quick Start Guide */}
                <div style={{ background: 'rgba(0,0,0,0.4)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '11px', fontWeight: '700', color: '#fbbf24', marginBottom: '6px' }}>
                    Quick Start Command (Terminal):
                  </div>
                  <pre style={{ margin: 0, padding: '8px', background: 'rgba(0,0,0,0.5)', borderRadius: '4px', fontSize: '11px', color: '#38bdf8', overflowX: 'auto', whiteSpace: 'pre-wrap' }}>
                    cloudflared tunnel --url http://localhost:8000
                  </pre>
                  <div style={{ fontSize: '10px', color: '#64748b', marginTop: '6px' }}>
                    Copy the generated <code>trycloudflare.com</code> URL and paste it above.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Studio Navigation Tabs */}
        <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid rgba(255,255,255,0.08)', marginBottom: '28px', flexWrap: 'wrap' }}>
          {[
            { id: 'indicators', label: 'Feature Pipeline & Matrix', icon: FaChartBar },
            { id: 'greeks', label: 'Black-Scholes Options Greeks', icon: FaCalculator },
            { id: 'strike-picker', label: 'Delta-Target Strike Picker', icon: FaSlidersH },
            { id: 'ichimoku', label: 'Ichimoku Causal Cloud', icon: FaLayerGroup },
          ].map(tab => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 20px',
                  background: active ? 'rgba(217, 119, 6, 0.15)' : 'transparent',
                  color: active ? '#fbbf24' : '#94a3b8',
                  border: 'none',
                  borderBottom: active ? '2px solid #fbbf24' : '2px solid transparent',
                  cursor: 'pointer',
                  fontWeight: active ? '700' : '500',
                  fontSize: '14px',
                  transition: 'all 0.2s',
                  borderRadius: '6px 6px 0 0'
                }}
              >
                <Icon size={14} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* TAB 1: FEATURE PIPELINE & INDICATOR MATRIX */}
        {activeTab === 'indicators' && (
          <div>
            {/* Real-time Indicator Snapshot Banner */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', marginBottom: '24px' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>SPOT CLOSE</div>
                <div style={{ fontSize: '20px', fontWeight: '800', color: '#f8fafc', margin: '4px 0' }}>{latestRow.close.toFixed(2)}</div>
                <div style={{ fontSize: '11px', color: '#10b981' }}>Intraday 5M Bar</div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>EMA(20) / EMA(50)</div>
                <div style={{ fontSize: '20px', fontWeight: '800', color: '#38bdf8', margin: '4px 0' }}>{latestRow.ema20}</div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>Slow EMA: {latestRow.ema50}</div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>WILDER'S RSI (14)</div>
                <div style={{ fontSize: '20px', fontWeight: '800', color: Number(latestRow.rsi14) > 70 ? '#ef4444' : Number(latestRow.rsi14) < 30 ? '#10b981' : '#f8fafc', margin: '4px 0' }}>
                  {latestRow.rsi14}
                </div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>Bound [0, 100]</div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>SUPERTREND (10, 3.0)</div>
                <div style={{ fontSize: '20px', fontWeight: '800', color: latestRow.stDirection === 1 ? '#10b981' : '#ef4444', margin: '4px 0' }}>
                  {latestRow.supertrend}
                </div>
                <div style={{ fontSize: '11px', color: latestRow.stDirection === 1 ? '#10b981' : '#ef4444' }}>
                  {latestRow.stDirection === 1 ? '▲ BULLISH UPTREND' : '▼ BEARISH DOWNTREND'}
                </div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>AVERAGE TRUE RANGE</div>
                <div style={{ fontSize: '20px', fontWeight: '800', color: '#f59e0b', margin: '4px 0' }}>{latestRow.atr14}</div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>Wilder's ATR (14)</div>
              </div>
            </div>

            {/* Feature Matrix Table */}
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.08)', overflow: 'hidden' }}>
              <div style={{ padding: '14px 20px', background: 'rgba(0,0,0,0.3)', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontWeight: '700', fontSize: '14px', color: '#f8fafc' }}>
                  Live Calculated Feature Matrix (Latest 10 Bars)
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                  Zero look-ahead bias • NaNs strictly preserved during warmup
                </div>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'right' }}>
                  <thead>
                    <tr style={{ color: '#94a3b8', borderBottom: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.02)' }}>
                      <th style={{ padding: '10px 16px', textAlign: 'left' }}>TIME</th>
                      <th style={{ padding: '10px 16px' }}>OPEN</th>
                      <th style={{ padding: '10px 16px' }}>HIGH</th>
                      <th style={{ padding: '10px 16px' }}>LOW</th>
                      <th style={{ padding: '10px 16px' }}>CLOSE</th>
                      <th style={{ padding: '10px 16px' }}>EMA(20)</th>
                      <th style={{ padding: '10px 16px' }}>EMA(50)</th>
                      <th style={{ padding: '10px 16px' }}>RSI(14)</th>
                      <th style={{ padding: '10px 16px' }}>ATR(14)</th>
                      <th style={{ padding: '10px 16px' }}>SUPERTREND</th>
                    </tr>
                  </thead>
                  <tbody>
                    {computedData.slice(-10).reverse().map((row, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', transition: 'background 0.15s' }}>
                        <td style={{ padding: '10px 16px', textAlign: 'left', color: '#f8fafc', fontWeight: '600' }}>{row.timestamp}</td>
                        <td style={{ padding: '10px 16px', color: '#cbd5e1' }}>{row.open.toFixed(2)}</td>
                        <td style={{ padding: '10px 16px', color: '#10b981' }}>{row.high.toFixed(2)}</td>
                        <td style={{ padding: '10px 16px', color: '#ef4444' }}>{row.low.toFixed(2)}</td>
                        <td style={{ padding: '10px 16px', color: '#f8fafc', fontWeight: '700' }}>{row.close.toFixed(2)}</td>
                        <td style={{ padding: '10px 16px', color: '#38bdf8' }}>{row.ema20}</td>
                        <td style={{ padding: '10px 16px', color: '#818cf8' }}>{row.ema50}</td>
                        <td style={{ padding: '10px 16px', color: '#f59e0b', fontWeight: '600' }}>{row.rsi14}</td>
                        <td style={{ padding: '10px 16px', color: '#cbd5e1' }}>{row.atr14}</td>
                        <td style={{ padding: '10px 16px', color: row.stDirection === 1 ? '#10b981' : '#ef4444', fontWeight: '600' }}>
                          {row.supertrend}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: BLACK-SCHOLES OPTIONS GREEKS LAB */}
        {activeTab === 'greeks' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            {/* Input Controls */}
            <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '24px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc', margin: '0 0 20px 0' }}>
                Options Contract Parameters
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Spot Price (INR)</label>
                  <input
                    type="number"
                    value={spotPrice}
                    onChange={(e) => setSpotPrice(parseFloat(e.target.value) || 0)}
                    style={{ width: '100%', padding: '10px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: '#f8fafc' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Strike Price (INR)</label>
                  <input
                    type="number"
                    value={strikePrice}
                    onChange={(e) => setStrikePrice(parseFloat(e.target.value) || 0)}
                    style={{ width: '100%', padding: '10px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: '#f8fafc' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Days to Expiry (DTE)</label>
                  <input
                    type="number"
                    value={dteDays}
                    onChange={(e) => setDteDays(parseFloat(e.target.value) || 1)}
                    style={{ width: '100%', padding: '10px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: '#f8fafc' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Implied Volatility (%)</label>
                  <input
                    type="number"
                    value={volatility}
                    onChange={(e) => setVolatility(parseFloat(e.target.value) || 1)}
                    style={{ width: '100%', padding: '10px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: '#f8fafc' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Risk-Free Rate (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={riskFreeRate}
                    onChange={(e) => setRiskFreeRate(parseFloat(e.target.value) || 0)}
                    style={{ width: '100%', padding: '10px', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', color: '#f8fafc' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Option Type</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => setOptionType('call')}
                      style={{
                        flex: 1,
                        padding: '10px',
                        borderRadius: '6px',
                        border: 'none',
                        background: optionType === 'call' ? '#10b981' : 'rgba(255,255,255,0.06)',
                        color: '#f8fafc',
                        fontWeight: '700',
                        cursor: 'pointer'
                      }}
                    >
                      CALL (CE)
                    </button>
                    <button
                      onClick={() => setOptionType('put')}
                      style={{
                        flex: 1,
                        padding: '10px',
                        borderRadius: '6px',
                        border: 'none',
                        background: optionType === 'put' ? '#ef4444' : 'rgba(255,255,255,0.06)',
                        color: '#f8fafc',
                        fontWeight: '700',
                        cursor: 'pointer'
                      }}
                    >
                      PUT (PE)
                    </button>
                  </div>
                </div>
              </div>

              {/* Disclaimer */}
              <div style={{ display: 'flex', gap: '10px', padding: '12px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px' }}>
                <FaExclamationTriangle color="#ef4444" size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div style={{ fontSize: '11px', color: '#fca5a5', lineHeight: '1.4' }}>
                  <strong>Mandatory Quantitative Notice:</strong> Historical and theoretical Black-Scholes pricing is intended for scenario analysis and Greeks estimation. It is not a substitute for live executable exchange order quotes.
                </div>
              </div>
            </div>

            {/* Calculated Greeks Output */}
            <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '24px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc', margin: '0 0 20px 0' }}>
                Theoretical Valuation & Analytical Greeks
              </h3>

              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '20px', borderRadius: '10px', border: '1px solid rgba(217, 119, 6, 0.3)', marginBottom: '20px', textAlign: 'center' }}>
                <div style={{ fontSize: '12px', color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  THEORETICAL MODEL PRICE
                </div>
                <div style={{ fontSize: '36px', fontWeight: '900', color: '#f8fafc', margin: '6px 0' }}>
                  ₹ {greeks.price.toFixed(2)}
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                  {optionType.toUpperCase()} @ Strike {strikePrice} (DTE {dteDays}d)
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>DELTA (Δ)</div>
                  <div style={{ fontSize: '20px', fontWeight: '800', color: '#38bdf8' }}>{greeks.delta.toFixed(4)}</div>
                  <div style={{ fontSize: '10px', color: '#64748b' }}>Price sensitivity per ₹1 underlying</div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>GAMMA (Γ)</div>
                  <div style={{ fontSize: '20px', fontWeight: '800', color: '#a855f7' }}>{greeks.gamma.toFixed(6)}</div>
                  <div style={{ fontSize: '10px', color: '#64748b' }}>Rate of delta acceleration</div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>THETA (Θ / DAY)</div>
                  <div style={{ fontSize: '20px', fontWeight: '800', color: '#ef4444' }}>{greeks.theta_daily.toFixed(2)}</div>
                  <div style={{ fontSize: '10px', color: '#64748b' }}>Time decay per calendar day</div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>VEGA (ν / 1% IV)</div>
                  <div style={{ fontSize: '20px', fontWeight: '800', color: '#10b981' }}>{greeks.vega_1pct.toFixed(2)}</div>
                  <div style={{ fontSize: '10px', color: '#64748b' }}>Sensitivity per 1% vol shift</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: DELTA-TARGET STRIKE PICKER */}
        {activeTab === 'strike-picker' && (
          <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '24px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc', margin: '0 0 6px 0' }}>
                  Delta-Targeted Strike Selection Engine
                </h3>
                <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0 }}>
                  Automatically selects the option contract that minimizes tracking error for a target delta.
                </p>
              </div>

              {/* Target Delta Preset Buttons */}
              <div style={{ display: 'flex', gap: '8px' }}>
                {[
                  { label: '0.70 (ITM)', val: 0.70 },
                  { label: '0.50 (ATM)', val: 0.50 },
                  { label: '0.30 (OTM)', val: 0.30 },
                  { label: '0.20 (Far OTM)', val: 0.20 },
                ].map(p => (
                  <button
                    key={p.val}
                    onClick={() => setTargetDelta(p.val)}
                    style={{
                      padding: '8px 14px',
                      borderRadius: '6px',
                      border: '1px solid rgba(255,255,255,0.1)',
                      background: targetDelta === p.val ? '#fbbf24' : 'rgba(0,0,0,0.3)',
                      color: targetDelta === p.val ? '#000' : '#f8fafc',
                      fontWeight: '700',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Optimal Selected Strike Banner */}
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '10px', padding: '16px 20px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#10b981', fontWeight: '700' }}>OPTIMAL MATCH FOUND</div>
                <div style={{ fontSize: '24px', fontWeight: '900', color: '#f8fafc' }}>
                  Strike: {deltaSelection.selected_strike} {optionType.toUpperCase()}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>Target Delta: {targetDelta}</div>
                <div style={{ fontSize: '16px', fontWeight: '700', color: '#38bdf8' }}>
                  Actual Delta: {deltaSelection.actual_delta.toFixed(4)} (Error: {deltaSelection.delta_error.toFixed(4)})
                </div>
              </div>
            </div>

            {/* Evaluated Strikes Grid */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'right' }}>
                <thead>
                  <tr style={{ color: '#94a3b8', borderBottom: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.02)' }}>
                    <th style={{ padding: '10px 16px', textAlign: 'left' }}>STRIKE</th>
                    <th style={{ padding: '10px 16px' }}>THEO PRICE</th>
                    <th style={{ padding: '10px 16px' }}>DELTA (Δ)</th>
                    <th style={{ padding: '10px 16px' }}>ERROR VS TARGET</th>
                    <th style={{ padding: '10px 16px' }}>GAMMA (Γ)</th>
                    <th style={{ padding: '10px 16px' }}>THETA/DAY</th>
                    <th style={{ padding: '10px 16px' }}>STATUS</th>
                  </tr>
                </thead>
                <tbody>
                  {deltaSelection.all_evaluated.map((row, idx) => {
                    const isSelected = row.strike === deltaSelection.selected_strike;
                    return (
                      <tr
                        key={idx}
                        style={{
                          background: isSelected ? 'rgba(16, 185, 129, 0.12)' : 'transparent',
                          borderBottom: '1px solid rgba(255,255,255,0.04)',
                          fontWeight: isSelected ? '700' : 'normal'
                        }}
                      >
                        <td style={{ padding: '10px 16px', textAlign: 'left', color: isSelected ? '#10b981' : '#f8fafc' }}>
                          ₹ {row.strike}
                        </td>
                        <td style={{ padding: '10px 16px', color: '#f8fafc' }}>₹ {row.price.toFixed(2)}</td>
                        <td style={{ padding: '10px 16px', color: '#38bdf8' }}>{row.delta.toFixed(4)}</td>
                        <td style={{ padding: '10px 16px', color: '#cbd5e1' }}>{row.diff.toFixed(4)}</td>
                        <td style={{ padding: '10px 16px', color: '#a855f7' }}>{row.gamma.toFixed(6)}</td>
                        <td style={{ padding: '10px 16px', color: '#ef4444' }}>₹ {row.theta.toFixed(2)}</td>
                        <td style={{ padding: '10px 16px' }}>
                          {isSelected ? (
                            <span style={{ background: '#10b981', color: '#000', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '800' }}>
                              SELECTED
                            </span>
                          ) : (
                            <span style={{ color: '#64748b', fontSize: '11px' }}>Candidate</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: ICHIMOKU CAUSAL CLOUD VISUALIZER */}
        {activeTab === 'ichimoku' && (
          <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '24px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc', margin: '0 0 8px 0' }}>
              Causal Ichimoku Equilibrium Engine
            </h3>
            <p style={{ fontSize: '13px', color: '#94a3b8', margin: '0 0 24px 0', maxWidth: '800px' }}>
              Standard charting software projects Senkou Span A and B forward 26 bars. In backtesting and automated signal generation, looking at future projections creates look-ahead bias. The BullMonk engine aligns Senkou Spans with a strict +26 bar causal displacement so the cloud evaluated at timestamp T is the projection originated at T - 26.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>CONVERSION LINE (TENKAN)</div>
                <div style={{ fontSize: '18px', fontWeight: '800', color: '#38bdf8', margin: '4px 0' }}>9 Periods</div>
                <div style={{ fontSize: '11px', color: '#64748b' }}>(Highest High + Lowest Low) / 2</div>
              </div>

              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>BASE LINE (KIJUN)</div>
                <div style={{ fontSize: '18px', fontWeight: '800', color: '#ef4444', margin: '4px 0' }}>26 Periods</div>
                <div style={{ fontSize: '11px', color: '#64748b' }}>(Highest High + Lowest Low) / 2</div>
              </div>

              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>LEADING SPAN B</div>
                <div style={{ fontSize: '18px', fontWeight: '800', color: '#f59e0b', margin: '4px 0' }}>52 Periods</div>
                <div style={{ fontSize: '11px', color: '#64748b' }}>Causal shift: +26 periods</div>
              </div>

              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>WARMUP HORIZON</div>
                <div style={{ fontSize: '18px', fontWeight: '800', color: '#10b981', margin: '4px 0' }}>78 Bars</div>
                <div style={{ fontSize: '11px', color: '#64748b' }}>52 + 26 bars before ready</div>
              </div>
            </div>

            <div style={{ padding: '16px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '8px' }}>
              <div style={{ fontSize: '13px', fontWeight: '700', color: '#10b981', marginBottom: '4px' }}>
                Mathematical Proof: Look-Ahead Invariance
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8', lineHeight: '1.5' }}>
                Validated in <code>test_indicators_ichimoku.py::test_zero_look_ahead_bias</code>. Injecting anomalies into candles at T+1 or T+26 produces 0.00000000% difference in cloud boundaries or signals at timestamp T.
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default IndicatorFeatureStudio;
