import React, { useState } from 'react';
import { FaLayerGroup, FaInfoCircle, FaArrowUp, FaArrowDown } from 'react-icons/fa';

// 50-point strike ladder matching our Phase 2 data.nifty specifications
const SPOT_PRICE = 24024.50;
const ATM_STRIKE = 24000;

const STRIKES_DATA = [
  { strike: 23800, callLtp: 312.40, callChg: 24.5, callIv: 13.2, callDelta: 0.78, callOi: 1420000, putLtp: 88.20, putChg: -16.4, putIv: 13.8, putDelta: -0.22, putOi: 2840000 },
  { strike: 23850, callLtp: 274.10, callChg: 22.0, callIv: 13.0, callDelta: 0.72, callOi: 1890000, putLtp: 101.50, putChg: -18.2, putIv: 13.6, putDelta: -0.28, putOi: 2310000 },
  { strike: 23900, callLtp: 236.80, callChg: 19.4, callIv: 12.8, callDelta: 0.65, callOi: 2450000, putLtp: 116.30, putChg: -20.1, putIv: 13.4, putDelta: -0.35, putOi: 3120000 },
  { strike: 23950, callLtp: 201.20, callChg: 16.8, callIv: 12.7, callDelta: 0.58, callOi: 2980000, putLtp: 134.70, putChg: -22.4, putIv: 13.2, putDelta: -0.42, putOi: 3450000 },
  { strike: 24000, strikeAtm: true, callLtp: 168.50, callChg: 14.2, callIv: 12.6, callDelta: 0.50, callOi: 4210000, putLtp: 154.20, putChg: -25.0, putIv: 13.0, putDelta: -0.50, putOi: 4890000 },
  { strike: 24050, callLtp: 138.90, callChg: 11.5, callIv: 12.5, callDelta: 0.42, callOi: 3650000, putLtp: 176.80, putChg: -27.8, putIv: 13.1, putDelta: -0.58, putOi: 3780000 },
  { strike: 24100, callLtp: 112.40, callChg: 9.1, callIv: 12.5, callDelta: 0.35, callOi: 3820000, putLtp: 202.10, putChg: -30.5, putIv: 13.3, putDelta: -0.65, putOi: 2940000 },
  { strike: 24150, callLtp: 89.20, callChg: 7.0, callIv: 12.6, callDelta: 0.28, callOi: 2910000, putLtp: 231.50, putChg: -32.8, putIv: 13.5, putDelta: -0.72, putOi: 2150000 },
  { strike: 24200, callLtp: 69.80, callChg: 5.2, callIv: 12.8, callDelta: 0.22, callOi: 4120000, putLtp: 264.40, putChg: -35.2, putIv: 13.7, putDelta: -0.78, putOi: 1680000 },
];

const NiftyOptionChainView = () => {
  const [expiry, setExpiry] = useState('27-FEB-2025');

  return (
    <section id="option-chain" style={styles.section}>
      <div className="container">
        {/* Header */}
        <div className="section-header">
          <div className="section-tag">
            <FaLayerGroup size={11} />
            <span>NFO Derivatives Infrastructure</span>
          </div>
          <h2 className="section-title">
            NIFTY 50 <span className="text-gradient-gold">Option Chain Ladder</span>
          </h2>
          <p className="section-desc">
            Institutional European Index Options (CE / PE) with 50-point strike spacing,
            Greeks modeling, and real-time In-The-Money (ITM) / At-The-Money (ATM) classification.
          </p>
        </div>

        {/* Spot & Expiry Bar */}
        <div className="glass-card" style={styles.topBar}>
          <div style={styles.spotGroup}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>NIFTY 50 SPOT:</span>
            <span className="font-mono" style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-gold)' }}>
              {SPOT_PRICE.toFixed(2)}
            </span>
            <span className="badge badge-profit">+112.40 (+0.47%)</span>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              ATM Strike: <strong className="font-mono text-gold">{ATM_STRIKE}</strong>
            </span>
          </div>

          <div style={styles.expiryGroup}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>EXPIRY:</span>
            {['27-FEB-2025', '06-MAR-2025', '27-MAR-2025'].map(exp => (
              <button
                key={exp}
                onClick={() => setExpiry(exp)}
                style={{
                  ...styles.expiryBtn,
                  background: expiry === exp ? 'var(--accent-gold)' : 'rgba(255, 255, 255, 0.05)',
                  color: expiry === exp ? '#000' : 'var(--text-secondary)',
                  fontWeight: expiry === exp ? 700 : 500,
                }}
              >
                {exp}
              </button>
            ))}
          </div>
        </div>

        {/* Chain Table */}
        <div className="glass-card" style={styles.tableCard}>
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th colSpan="5" style={{ ...styles.thHeader, color: 'var(--profit-green)' }}>
                    CALL OPTIONS (CE)
                  </th>
                  <th style={{ ...styles.thHeader, color: 'var(--accent-gold)' }}>
                    STRIKE
                  </th>
                  <th colSpan="5" style={{ ...styles.thHeader, color: 'var(--loss-red)' }}>
                    PUT OPTIONS (PE)
                  </th>
                </tr>
                <tr style={styles.subHeaderRow}>
                  <th style={styles.th}>OI</th>
                  <th style={styles.th}>IV %</th>
                  <th style={styles.th}>DELTA</th>
                  <th style={styles.th}>CHG</th>
                  <th style={styles.th}>LTP</th>

                  <th style={{ ...styles.th, background: 'rgba(245, 166, 35, 0.12)' }}>STRIKE</th>

                  <th style={styles.th}>LTP</th>
                  <th style={styles.th}>CHG</th>
                  <th style={styles.th}>DELTA</th>
                  <th style={styles.th}>IV %</th>
                  <th style={styles.th}>OI</th>
                </tr>
              </thead>
              <tbody>
                {STRIKES_DATA.map((row, idx) => {
                  const isAtm = row.strike === ATM_STRIKE;
                  const isCallItm = row.strike < SPOT_PRICE;
                  const isPutItm = row.strike > SPOT_PRICE;

                  return (
                    <tr
                      key={idx}
                      style={{
                        ...styles.row,
                        background: isAtm ? 'rgba(245, 166, 35, 0.14)' : 'transparent',
                      }}
                    >
                      {/* Calls */}
                      <td style={{ ...styles.td, ...styles.itmCall(isCallItm) }} className="font-mono">
                        {(row.callOi / 100000).toFixed(1)}L
                      </td>
                      <td style={{ ...styles.td, ...styles.itmCall(isCallItm) }} className="font-mono">
                        {row.callIv}%
                      </td>
                      <td style={{ ...styles.td, ...styles.itmCall(isCallItm) }} className="font-mono">
                        {row.callDelta}
                      </td>
                      <td style={{ ...styles.td, ...styles.itmCall(isCallItm), color: 'var(--profit-green)' }} className="font-mono">
                        +{row.callChg}
                      </td>
                      <td style={{ ...styles.td, ...styles.itmCall(isCallItm), fontWeight: 700 }} className="font-mono">
                        {row.callLtp.toFixed(2)}
                      </td>

                      {/* Center Strike */}
                      <td style={{ ...styles.tdStrike, ...(isAtm ? styles.atmStrikeCell : {}) }}>
                        <span className="font-mono" style={{ fontWeight: 800 }}>{row.strike}</span>
                        {isAtm && <span style={styles.atmBadge}>ATM</span>}
                      </td>

                      {/* Puts */}
                      <td style={{ ...styles.td, ...styles.itmPut(isPutItm), fontWeight: 700 }} className="font-mono">
                        {row.putLtp.toFixed(2)}
                      </td>
                      <td style={{ ...styles.td, ...styles.itmPut(isPutItm), color: 'var(--loss-red)' }} className="font-mono">
                        {row.putChg}
                      </td>
                      <td style={{ ...styles.td, ...styles.itmPut(isPutItm) }} className="font-mono">
                        {row.putDelta}
                      </td>
                      <td style={{ ...styles.td, ...styles.itmPut(isPutItm) }} className="font-mono">
                        {row.putIv}%
                      </td>
                      <td style={{ ...styles.td, ...styles.itmPut(isPutItm) }} className="font-mono">
                        {(row.putOi / 100000).toFixed(1)}L
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Legend */}
        <div style={styles.legend}>
          <div style={styles.legendItem}>
            <span style={{ width: 12, height: 12, background: 'rgba(0, 245, 160, 0.08)', border: '1px solid rgba(0, 245, 160, 0.3)', display: 'inline-block' }} />
            <span>Call ITM (Strike &lt; Spot)</span>
          </div>
          <div style={styles.legendItem}>
            <span style={{ width: 12, height: 12, background: 'rgba(245, 166, 35, 0.3)', border: '1px solid var(--accent-gold)', display: 'inline-block' }} />
            <span>ATM Strike (Nearest 50 Multiple)</span>
          </div>
          <div style={styles.legendItem}>
            <span style={{ width: 12, height: 12, background: 'rgba(255, 71, 87, 0.08)', border: '1px solid rgba(255, 71, 87, 0.3)', display: 'inline-block' }} />
            <span>Put ITM (Strike &gt; Spot)</span>
          </div>
          <div style={styles.legendItem}>
            <FaInfoCircle color="#94A3B8" size={12} />
            <span>Standard Contract Lot Size: 75 Units | European Style (Cash Settled)</span>
          </div>
        </div>
      </div>
    </section>
  );
};

const styles = {
  section: {
    padding: '4rem 0',
    borderBottom: '1px solid var(--border-subtle)',
  },
  topBar: {
    padding: '1.25rem 1.5rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '1rem',
    marginBottom: '1.5rem',
  },
  spotGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.85rem',
    flexWrap: 'wrap',
  },
  expiryGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  expiryBtn: {
    border: 'none',
    padding: '0.35rem 0.85rem',
    borderRadius: '6px',
    fontSize: '0.8rem',
    cursor: 'pointer',
    fontFamily: 'var(--font-mono)',
  },
  tableCard: {
    padding: '1rem',
    overflow: 'hidden',
  },
  tableWrapper: {
    width: '100%',
    overflowX: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    textAlign: 'center',
    fontSize: '0.84rem',
  },
  thHeader: {
    padding: '0.75rem',
    fontWeight: 800,
    letterSpacing: '0.05em',
    fontSize: '0.86rem',
    borderBottom: '1px solid var(--border-subtle)',
  },
  subHeaderRow: {
    borderBottom: '1px solid var(--border-subtle)',
  },
  th: {
    padding: '0.5rem 0.6rem',
    color: 'var(--text-muted)',
    fontSize: '0.72rem',
    fontWeight: 700,
    letterSpacing: '0.04em',
  },
  row: {
    borderBottom: '1px solid rgba(255, 255, 255, 0.03)',
    transition: 'background 0.15s ease',
  },
  td: {
    padding: '0.55rem 0.6rem',
    color: 'var(--text-secondary)',
  },
  tdStrike: {
    padding: '0.55rem 0.85rem',
    background: 'rgba(255, 255, 255, 0.04)',
    color: 'var(--text-primary)',
    fontWeight: 700,
    position: 'relative',
  },
  atmStrikeCell: {
    background: 'rgba(245, 166, 35, 0.25)',
    color: '#FFD700',
    borderLeft: '2px solid var(--accent-gold)',
    borderRight: '2px solid var(--accent-gold)',
  },
  atmBadge: {
    fontSize: '0.62rem',
    fontWeight: 800,
    padding: '1px 4px',
    borderRadius: '3px',
    background: 'var(--accent-gold)',
    color: '#000',
    marginLeft: '6px',
  },
  itmCall: (isItm) => ({
    background: isItm ? 'rgba(0, 245, 160, 0.04)' : 'transparent',
    color: isItm ? 'var(--text-primary)' : 'var(--text-muted)',
  }),
  itmPut: (isItm) => ({
    background: isItm ? 'rgba(255, 71, 87, 0.04)' : 'transparent',
    color: isItm ? 'var(--text-primary)' : 'var(--text-muted)',
  }),
  legend: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.8rem',
    flexWrap: 'wrap',
    marginTop: '1.25rem',
    fontSize: '0.78rem',
    color: 'var(--text-secondary)',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.45rem',
  },
};

export default NiftyOptionChainView;
