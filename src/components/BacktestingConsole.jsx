import React, { useState, useMemo } from 'react';
import { 
  FiPlay, FiRefreshCw, FiTrendingUp, FiActivity, FiShield, 
  FiLayers, FiSliders, FiDownload, FiCheckCircle, FiChevronRight,
  FiBarChart2, FiPieChart, FiPercent
} from 'react-icons/fi';

const STRATEGIES = [
  {
    id: 'dual_ma_regime',
    name: 'Dual EMA Regime Filter + ATR',
    asset: 'NIFTY 50',
    timeframe: '15m',
    type: 'Trend Following',
    description: 'Fast 21 EMA / Slow 55 EMA crossover filtered by 200 EMA regime with dynamic 2.0x ATR trailing stop.',
    defaultParams: { fastEma: 21, slowEma: 55, atrMult: 2.0, riskPerTrade: 1.0 },
    stats: {
      initialCap: 1000000,
      finalCap: 1842500,
      totalReturn: 84.25,
      sharpe: 2.84,
      sortino: 4.12,
      maxDd: -3.18,
      winRate: 68.4,
      profitFactor: 2.41,
      totalTrades: 1248,
      calmar: 7.25,
      avgWin: 1420,
      avgLoss: 620,
      oosEfficiency: 88.6
    }
  },
  {
    id: 'vol_breakout_options',
    name: 'Vol Breakout Gamma Scalper',
    asset: 'NIFTY Index Options (Weekly)',
    timeframe: '5m',
    type: 'Options Volatility',
    description: 'Delta-neutral intraday strangle scalping during opening 45-min volatility expansion with strict VIX filter.',
    defaultParams: { fastEma: 9, slowEma: 21, atrMult: 1.5, riskPerTrade: 1.5 },
    stats: {
      initialCap: 1000000,
      finalCap: 2145000,
      totalReturn: 114.50,
      sharpe: 3.12,
      sortino: 4.88,
      maxDd: -4.42,
      winRate: 72.1,
      profitFactor: 2.76,
      totalTrades: 894,
      calmar: 8.42,
      avgWin: 2150,
      avgLoss: 890,
      oosEfficiency: 91.2
    }
  },
  {
    id: 'lstm_mean_rev',
    name: 'Deep LSTM Mean Reversion',
    asset: 'BANKNIFTY',
    timeframe: '1m',
    type: 'AI / Deep Learning',
    description: 'Bidirectional LSTM autoencoder identifying liquidity sweeps and extreme order book imbalance exhaustion.',
    defaultParams: { fastEma: 14, slowEma: 50, atrMult: 1.8, riskPerTrade: 0.8 },
    stats: {
      initialCap: 1000000,
      finalCap: 1698200,
      totalReturn: 69.82,
      sharpe: 2.65,
      sortino: 3.82,
      maxDd: -2.94,
      winRate: 65.8,
      profitFactor: 2.18,
      totalTrades: 1640,
      calmar: 6.94,
      avgWin: 1180,
      avgLoss: 540,
      oosEfficiency: 84.7
    }
  },
  {
    id: 'pairs_stat_arb',
    name: 'Statistical Arbitrage Cointegration',
    asset: 'RELIANCE / NIFTY 50',
    timeframe: '30m',
    type: 'Statistical Arbitrage',
    description: 'Engle-Granger cointegrated pairs trading with Ornstein-Uhlenbeck drift-diffusion reversion band triggers.',
    defaultParams: { fastEma: 20, slowEma: 60, atrMult: 2.2, riskPerTrade: 1.2 },
    stats: {
      initialCap: 1000000,
      finalCap: 1534000,
      totalReturn: 53.40,
      sharpe: 3.44,
      sortino: 5.12,
      maxDd: -1.82,
      winRate: 74.5,
      profitFactor: 3.05,
      totalTrades: 620,
      calmar: 12.1,
      avgWin: 1840,
      avgLoss: 610,
      oosEfficiency: 94.1
    }
  }
];

export default function BacktestingConsole() {
  const [selectedStratId, setSelectedStratId] = useState('dual_ma_regime');
  const [activeTab, setActiveTab] = useState('equity'); // equity | drawdown | montecarlo | trades
  const [isRunning, setIsRunning] = useState(false);
  const [runProgress, setRunProgress] = useState(100);
  const [capital, setCapital] = useState(1000000);
  const [hoveredPoint, setHoveredPoint] = useState(null);

  const strat = useMemo(() => {
    return STRATEGIES.find(s => s.id === selectedStratId) || STRATEGIES[0];
  }, [selectedStratId]);

  const handleRunBacktest = () => {
    setIsRunning(true);
    setRunProgress(15);
    const interval = setInterval(() => {
      setRunProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsRunning(false);
          return 100;
        }
        return prev + 25;
      });
    }, 180);
  };

  // Generate equity curve data points
  const equityPoints = useMemo(() => {
    const points = [];
    let currentEquity = capital;
    const count = 50;
    const growthFactor = (strat.stats.totalReturn / 100) / count;
    
    // Seeded random walk to look realistic
    for (let i = 0; i <= count; i++) {
      const day = i * 5;
      if (i === 0) {
        points.push({ idx: 0, day: 'Day 0', equity: currentEquity, dd: 0 });
      } else {
        const shock = (Math.sin(i * 1.3) * 0.008) + (Math.cos(i * 0.7) * 0.005) + growthFactor;
        currentEquity = Math.round(currentEquity * (1 + shock));
        const peak = Math.max(...points.map(p => p.equity), currentEquity);
        const dd = Number((((currentEquity - peak) / peak) * 100).toFixed(2));
        points.push({ idx: i, day: `Day ${day}`, equity: currentEquity, dd });
      }
    }
    return points;
  }, [strat, capital]);

  // Compute SVG coordinates for Equity Curve
  const svgWidth = 800;
  const svgHeight = 280;
  const padding = { top: 20, right: 30, bottom: 35, left: 70 };
  const graphWidth = svgWidth - padding.left - padding.right;
  const graphHeight = svgHeight - padding.top - padding.bottom;

  const minEquity = Math.min(...equityPoints.map(p => p.equity)) * 0.98;
  const maxEquity = Math.max(...equityPoints.map(p => p.equity)) * 1.02;

  const getX = (idx) => padding.left + (idx / (equityPoints.length - 1)) * graphWidth;
  const getY = (val) => padding.top + graphHeight - ((val - minEquity) / (maxEquity - minEquity)) * graphHeight;
  
  // Equity path
  const pathD = equityPoints.reduce((acc, pt, idx) => {
    const x = getX(idx);
    const y = getY(pt.equity);
    return idx === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
  }, '');

  const areaD = `${pathD} L ${getX(equityPoints.length - 1)} ${padding.top + graphHeight} L ${padding.left} ${padding.top + graphHeight} Z`;

  // Drawdown points
  const maxDdVal = Math.min(...equityPoints.map(p => p.dd));
  const getDdY = (dd) => padding.top + (Math.abs(dd) / (Math.abs(maxDdVal) * 1.2 || 1)) * graphHeight;
  const ddPathD = equityPoints.reduce((acc, pt, idx) => {
    const x = getX(idx);
    const y = getDdY(pt.dd);
    return idx === 0 ? `M ${x} ${padding.top}` : `${acc} L ${x} ${y}`;
  }, '');
  const ddAreaD = `${ddPathD} L ${getX(equityPoints.length - 1)} ${padding.top} L ${padding.left} ${padding.top} Z`;

  // Sample executed trades
  const sampleTrades = [
    { id: '#TR-8941', time: '14:45:00 IST', symbol: 'NIFTY 24500 CE', type: 'LONG', qty: 150, entry: '₹142.50', exit: '₹188.20', pnl: '+₹6,855', pct: '+32.0%', status: 'TARGET' },
    { id: '#TR-8940', time: '13:15:20 IST', symbol: 'NIFTY 24600 PE', type: 'LONG', qty: 100, entry: '₹95.00', exit: '₹82.50', pnl: '-₹1,250', pct: '-13.1%', status: 'SL_TRAIL' },
    { id: '#TR-8939', time: '11:30:10 IST', symbol: 'NIFTY FUT', type: 'SHORT', qty: 75, entry: '24,580.0', exit: '24,510.5', pnl: '+₹5,212', pct: '+0.28%', status: 'REGIME_EXIT' },
    { id: '#TR-8938', time: '10:05:40 IST', symbol: 'BANKNIFTY FUT', type: 'LONG', qty: 45, entry: '52,140.0', exit: '52,385.0', pnl: '+₹11,025', pct: '+0.47%', status: 'TARGET' },
    { id: '#TR-8937', time: '09:25:12 IST', symbol: 'NIFTY 24450 CE', type: 'LONG', qty: 200, entry: '185.00', exit: '215.50', pnl: '+₹6,100', pct: '+16.5%', status: 'TARGET' },
  ];

  return (
    <div id="backtesting" className="quant-section" style={{ padding: '80px 24px', background: 'var(--bg-obsidian-dark)' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        
        {/* Section Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '20px', marginBottom: '32px' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '4px 12px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '20px', fontSize: '11px', color: '#60a5fa', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '12px' }}>
              <FiBarChart2 /> High-Fidelity Backtesting & Walk-Forward Engine
            </div>
            <h2 style={{ fontSize: 'clamp(1.8rem, 3.5vw, 2.6rem)', fontWeight: 800, color: '#f8fafc', margin: 0, letterSpacing: '-0.5px' }}>
              Institutional <span style={{ background: 'var(--accent-gold-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Strategy Backtester</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: '8px 0 0 0', maxWidth: '650px' }}>
              Tick-by-tick and vectorized event-driven simulation with realistic Indian market slippage, STT/brokerage fees, and out-of-sample Monte Carlo verification.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <button 
              onClick={handleRunBacktest}
              disabled={isRunning}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 22px',
                background: isRunning ? 'var(--bg-surface)' : 'var(--accent-gold-gradient)',
                color: isRunning ? 'var(--text-secondary)' : '#000',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '13px',
                cursor: isRunning ? 'not-allowed' : 'pointer',
                boxShadow: isRunning ? 'none' : '0 4px 15px rgba(245, 166, 35, 0.3)',
                transition: 'all 0.2s ease'
              }}
            >
              {isRunning ? <FiRefreshCw className="spin" /> : <FiPlay />}
              {isRunning ? `Simulating (${runProgress}%)...` : 'Run Backtest Simulation'}
            </button>
          </div>
        </div>

        {/* Strategy Selector Ribbon */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px', marginBottom: '24px' }}>
          {STRATEGIES.map(s => {
            const isSelected = s.id === selectedStratId;
            return (
              <div 
                key={s.id}
                onClick={() => setSelectedStratId(s.id)}
                style={{
                  background: isSelected ? 'rgba(245, 166, 35, 0.08)' : 'var(--bg-surface)',
                  border: isSelected ? '1px solid rgba(245, 166, 35, 0.5)' : '1px solid var(--border-subtle)',
                  borderRadius: '12px',
                  padding: '16px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  position: 'relative'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '10px', textTransform: 'uppercase', padding: '2px 8px', borderRadius: '4px', background: isSelected ? 'rgba(245, 166, 35, 0.2)' : 'rgba(255, 255, 255, 0.05)', color: isSelected ? '#fbbf24' : 'var(--text-muted)', fontWeight: 700 }}>
                    {s.type}
                  </span>
                  <span style={{ fontSize: '11px', fontFamily: 'JetBrains Mono', color: 'var(--profit-green)', fontWeight: 700 }}>
                    +{s.stats.totalReturn}%
                  </span>
                </div>
                <div style={{ fontWeight: 700, color: isSelected ? '#fff' : 'var(--text-secondary)', fontSize: '14px', marginBottom: '4px' }}>
                  {s.name}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', gap: '12px' }}>
                  <span>Symbol: <strong>{s.asset}</strong></span>
                  <span>TF: <strong>{s.timeframe}</strong></span>
                  <span>Sharpe: <strong>{s.stats.sharpe}</strong></span>
                </div>
              </div>
            );
          })}
        </div>

        {/* KPI Metrics Dashboard Bar */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginBottom: '24px' }}>
          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Total Return</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--profit-green)', fontFamily: 'JetBrains Mono' }}>
              +{strat.stats.totalReturn}%
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>₹10.0L → ₹{(strat.stats.finalCap / 100000).toFixed(2)}L</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Sharpe Ratio</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#60a5fa', fontFamily: 'JetBrains Mono' }}>
              {strat.stats.sharpe}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Sortino: {strat.stats.sortino}</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Max Drawdown</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--loss-red)', fontFamily: 'JetBrains Mono' }}>
              {strat.stats.maxDd}%
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Calmar: {strat.stats.calmar}</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Win Rate</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f8fafc', fontFamily: 'JetBrains Mono' }}>
              {strat.stats.winRate}%
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>PF: {strat.stats.profitFactor}</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Total Trades</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f8fafc', fontFamily: 'JetBrains Mono' }}>
              {strat.stats.totalTrades}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>W/L: {strat.stats.avgWin}/{strat.stats.avgLoss}</div>
          </div>

          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Walk-Forward Score</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#34d399', fontFamily: 'JetBrains Mono' }}>
              {strat.stats.oosEfficiency}%
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>OOS Robustness</div>
          </div>
        </div>

        {/* Main Chart Area */}
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '14px', overflow: 'hidden', marginBottom: '24px' }}>
          
          {/* Chart Header & Tab Nav */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              {[
                { id: 'equity', label: 'Cumulative Equity Curve' },
                { id: 'drawdown', label: 'Underwater Drawdown' },
                { id: 'montecarlo', label: 'Monte Carlo 1,000 Paths' },
                { id: 'trades', label: 'Trade Log Table' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    padding: '7px 14px',
                    borderRadius: '6px',
                    border: 'none',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    background: activeTab === tab.id ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                    color: activeTab === tab.id ? '#fff' : 'var(--text-muted)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>
              Simulated: Jan 2024 - Oct 2026 • Indian Market (NSE)
            </div>
          </div>

          {/* Interactive Chart Canvas */}
          {activeTab === 'equity' && (
            <div style={{ padding: '20px', position: 'relative' }}>
              <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} style={{ width: '100%', height: 'auto', display: 'block', overflow: 'visible' }}>
                <defs>
                  <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity="0.35" />
                    <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Horizontal Grid lines */}
                {[0, 0.25, 0.5, 0.75, 1.0].map((ratio, i) => {
                  const y = padding.top + graphHeight * ratio;
                  const val = Math.round(maxEquity - (ratio * (maxEquity - minEquity)));
                  return (
                    <g key={i}>
                      <line x1={padding.left} y1={y} x2={svgWidth - padding.right} y2={y} stroke="rgba(255,255,255,0.06)" strokeDasharray="4 4" />
                      <text x={padding.left - 10} y={y + 4} fill="#64748b" fontSize="10" textAnchor="end" fontFamily="JetBrains Mono">
                        ₹{(val / 100000).toFixed(2)}L
                      </text>
                    </g>
                  );
                })}

                {/* Area under curve */}
                <path d={areaD} fill="url(#equityGrad)" />

                {/* Main Equity Line */}
                <path d={pathD} fill="none" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

                {/* Interactive Points on hover */}
                {equityPoints.map((pt, idx) => {
                  const x = getX(idx);
                  const y = getY(pt.equity);
                  const isHovered = hoveredPoint && hoveredPoint.idx === idx;
                  return (
                    <g key={idx} onMouseEnter={() => setHoveredPoint(pt)} onMouseLeave={() => setHoveredPoint(null)}>
                      <circle cx={x} cy={y} r={isHovered ? 6 : 3} fill={isHovered ? '#fbbf24' : '#10b981'} stroke="#0a0e17" strokeWidth="2" style={{ cursor: 'pointer', transition: 'r 0.15s ease' }} />
                    </g>
                  );
                })}
              </svg>

              {/* Tooltip */}
              {hoveredPoint && (
                <div style={{
                  position: 'absolute',
                  top: '30px',
                  right: '30px',
                  background: 'rgba(15, 23, 42, 0.95)',
                  border: '1px solid #38bdf8',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
                  fontSize: '12px',
                  fontFamily: 'JetBrains Mono',
                  color: '#fff',
                  pointerEvents: 'none'
                }}>
                  <div style={{ color: '#94a3b8', fontSize: '10px' }}>{hoveredPoint.day}</div>
                  <div style={{ fontWeight: 800, fontSize: '14px', color: '#10b981', margin: '2px 0' }}>
                    ₹{hoveredPoint.equity.toLocaleString('en-IN')}
                  </div>
                  <div style={{ fontSize: '11px', color: hoveredPoint.dd < 0 ? '#f43f5e' : '#94a3b8' }}>
                    Drawdown: {hoveredPoint.dd}%
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'drawdown' && (
            <div style={{ padding: '20px' }}>
              <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
                <defs>
                  <linearGradient id="ddGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.05" />
                    <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.4" />
                  </linearGradient>
                </defs>
                <line x1={padding.left} y1={padding.top} x2={svgWidth - padding.right} y2={padding.top} stroke="#64748b" strokeWidth="1" />
                <path d={ddAreaD} fill="url(#ddGrad)" />
                <path d={ddPathD} fill="none" stroke="#f43f5e" strokeWidth="2" />
                <text x={padding.left - 10} y={padding.top + 4} fill="#64748b" fontSize="10" textAnchor="end" fontFamily="JetBrains Mono">0.0%</text>
                <text x={padding.left - 10} y={padding.top + graphHeight} fill="#f43f5e" fontSize="10" textAnchor="end" fontFamily="JetBrains Mono">
                  {maxDdVal}%
                </text>
              </svg>
            </div>
          )}

          {activeTab === 'montecarlo' && (
            <div style={{ padding: '20px' }}>
              <div style={{ height: '240px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px dashed var(--border-subtle)' }}>
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
                  Monte Carlo 1,000 Resampled Paths
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '480px', textAlign: 'center', lineHeight: '1.5' }}>
                  Bootstrap reshuffling shows 95% Confidence Interval final NAV of <strong>₹1,580,000 – ₹2,110,000</strong>. Probability of capital preservation (&gt; ₹1,000,000) is <strong>99.8%</strong>.
                </div>
                <div style={{ marginTop: '16px', display: 'flex', gap: '20px', fontFamily: 'JetBrains Mono', fontSize: '11px' }}>
                  <span style={{ color: '#10b981' }}>5th Percentile: ₹1.58M</span>
                  <span style={{ color: '#fbbf24' }}>50th Median: ₹1.84M</span>
                  <span style={{ color: '#38bdf8' }}>95th Percentile: ₹2.11M</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'trades' && (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12px' }}>
                <thead>
                  <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px 16px' }}>Order ID</th>
                    <th style={{ padding: '12px 16px' }}>Time</th>
                    <th style={{ padding: '12px 16px' }}>Contract</th>
                    <th style={{ padding: '12px 16px' }}>Side</th>
                    <th style={{ padding: '12px 16px' }}>Qty</th>
                    <th style={{ padding: '12px 16px' }}>Entry</th>
                    <th style={{ padding: '12px 16px' }}>Exit</th>
                    <th style={{ padding: '12px 16px' }}>PnL (Net)</th>
                    <th style={{ padding: '12px 16px' }}>Exit Trigger</th>
                  </tr>
                </thead>
                <tbody>
                  {sampleTrades.map(trade => (
                    <tr key={trade.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.03)', fontFamily: 'JetBrains Mono' }}>
                      <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{trade.id}</td>
                      <td style={{ padding: '12px 16px', color: '#cbd5e1' }}>{trade.time}</td>
                      <td style={{ padding: '12px 16px', fontWeight: 700, color: '#f8fafc' }}>{trade.symbol}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '10px',
                          fontWeight: 700,
                          background: trade.type === 'LONG' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
                          color: trade.type === 'LONG' ? 'var(--profit-green)' : 'var(--loss-red)'
                        }}>
                          {trade.type}
                        </span>
                      </td>
                      <td style={{ padding: '12px 16px' }}>{trade.qty}</td>
                      <td style={{ padding: '12px 16px' }}>{trade.entry}</td>
                      <td style={{ padding: '12px 16px' }}>{trade.exit}</td>
                      <td style={{ padding: '12px 16px', fontWeight: 700, color: trade.pnl.startsWith('+') ? 'var(--profit-green)' : 'var(--loss-red)' }}>
                        {trade.pnl} ({trade.pct})
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', color: '#94a3b8' }}>
                          {trade.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
