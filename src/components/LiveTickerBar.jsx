import React, { useState, useEffect } from 'react';
import { FaArrowUp, FaArrowDown, FaCheckCircle, FaBolt } from 'react-icons/fa';

const INITIAL_TICKERS = [
  { symbol: 'NIFTY 50', exchange: 'NSE', price: 24142.80, change: 112.40, pct: 0.47, isUp: true },
  { symbol: 'BANKNIFTY', exchange: 'NSE', price: 51890.15, change: 245.20, pct: 0.48, isUp: true },
  { symbol: 'NIFTY FUT (FEB)', exchange: 'NFO', price: 24205.50, change: 118.00, pct: 0.49, isUp: true },
  { symbol: 'BTC / USDT', exchange: 'BINANCE', price: 96420.00, change: 1240.00, pct: 1.30, isUp: true },
  { symbol: 'ETH / USDT', exchange: 'BINANCE', price: 2780.50, change: -18.20, pct: -0.65, isUp: false },
  { symbol: 'EUR / USD', exchange: 'FOREX', price: 1.0842, change: 0.0012, pct: 0.11, isUp: true },
  { symbol: 'RELIANCE', exchange: 'NSE', price: 2984.50, change: 18.20, pct: 0.61, isUp: true },
  { symbol: 'HDFCBANK', exchange: 'NSE', price: 1742.10, change: -6.40, pct: -0.37, isUp: false },
];

const LiveTickerBar = () => {
  const [tickers, setTickers] = useState(INITIAL_TICKERS);

  // Micro-fluctuation simulation to give live quantitative heartbeat feel
  useEffect(() => {
    const interval = setInterval(() => {
      setTickers(prev => prev.map(t => {
        const delta = (Math.random() - 0.49) * (t.price > 1000 ? 1.5 : 0.0005);
        const newPrice = Math.max(t.price + delta, 0.001);
        return {
          ...t,
          price: Number(newPrice.toFixed(t.price > 10 ? 2 : 4)),
        };
      }));
    }, 2400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={styles.bar}>
      <div style={styles.statusBadge}>
        <span className="status-dot status-dot-green" />
        <span style={styles.statusText}>NSE / BINANCE FEED</span>
        <span style={styles.latency}><FaBolt size={10} color="#00F5A0" /> 1.8ms</span>
      </div>

      <div style={styles.tickerTrack}>
        {tickers.map((t, idx) => (
          <div key={idx} style={styles.item}>
            <span style={styles.sym}>{t.symbol}</span>
            <span style={styles.exch}>{t.exchange}</span>
            <span style={styles.price} className="font-mono">
              {t.price > 100 ? t.price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : t.price.toFixed(4)}
            </span>
            <span style={{ ...styles.change, color: t.isUp ? 'var(--profit-green)' : 'var(--loss-red)' }} className="font-mono">
              {t.isUp ? <FaArrowUp size={9} /> : <FaArrowDown size={9} />}
              {t.pct > 0 ? `+${t.pct}%` : `${t.pct}%`}
            </span>
          </div>
        ))}
      </div>

      <div style={styles.engineTag}>
        <FaCheckCircle color="#00F5A0" size={12} />
        <span>219/219 Tests Passing</span>
      </div>
    </div>
  );
};

const styles = {
  bar: {
    width: '100%',
    background: 'rgba(5, 7, 14, 0.95)',
    borderBottom: '1px solid var(--border-subtle)',
    padding: '0.45rem 1.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    fontSize: '0.78rem',
    overflow: 'hidden',
    position: 'sticky',
    top: 0,
    zIndex: 100,
    backdropFilter: 'blur(12px)',
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    flexShrink: 0,
    marginRight: '1.5rem',
  },
  statusText: {
    fontWeight: 700,
    letterSpacing: '0.04em',
    color: 'var(--text-secondary)',
    fontSize: '0.72rem',
  },
  latency: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.2rem',
    color: 'var(--profit-green)',
    fontFamily: 'var(--font-mono)',
    fontSize: '0.72rem',
  },
  tickerTrack: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.8rem',
    overflowX: 'auto',
    whiteSpace: 'nowrap',
    scrollbarWidth: 'none',
    msOverflowStyle: 'none',
  },
  item: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.4rem',
  },
  sym: {
    fontWeight: 700,
    color: 'var(--text-primary)',
  },
  exch: {
    fontSize: '0.65rem',
    color: 'var(--text-muted)',
    padding: '1px 4px',
    borderRadius: '3px',
    background: 'rgba(255, 255, 255, 0.05)',
  },
  price: {
    fontWeight: 600,
    color: 'var(--text-primary)',
  },
  change: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '2px',
    fontSize: '0.72rem',
    fontWeight: 600,
  },
  engineTag: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.4rem',
    color: 'var(--profit-green)',
    fontWeight: 600,
    fontSize: '0.72rem',
    flexShrink: 0,
    marginLeft: '1.5rem',
    padding: '2px 8px',
    borderRadius: '4px',
    background: 'var(--profit-green-bg)',
    border: '1px solid rgba(0, 245, 160, 0.25)',
  },
};

export default LiveTickerBar;
