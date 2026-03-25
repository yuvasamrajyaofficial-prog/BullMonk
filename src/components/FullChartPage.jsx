import React, { useState } from 'react';
import { AdvancedRealTimeChart } from 'react-ts-tradingview-widgets';
import { FaArrowLeft } from 'react-icons/fa';
import { watchlists } from '../utils/watchlists';

const FullChartPage = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState('crypto');

  const tabs = [
    { id: 'crypto', label: 'Crypto' },
    { id: 'india', label: 'India' },
    { id: 'global', label: 'Global' },
    { id: 'forex', label: 'Forex' }
  ];

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      backgroundColor: '#0a0a0f', /* Deep dark identical to TradingView native */
      display: 'flex',
      flexDirection: 'column',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 99999
    }}>
      {/* Header Bar */}
      <div style={{
        height: '60px',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 20px',
        justifyContent: 'space-between',
        background: 'rgba(10, 10, 15, 0.95)'
      }}>
        <button 
          onClick={onBack}
          style={{
            display: 'flex',
            alignItems: 'center',
            background: 'transparent',
            border: '1px solid rgba(245, 166, 35, 0.3)',
            color: 'var(--accent-gold)',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontFamily: 'var(--font-heading)',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            transition: 'all 0.3s ease'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = 'rgba(245, 166, 35, 0.1)'}
          onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <FaArrowLeft style={{ marginRight: '8px' }} /> Back to BullMonk
        </button>

        {/* Watchlist Tabs UI */}
        <div className="hide-mobile" style={{ display: 'flex', gap: '8px' }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: activeTab === tab.id ? 'rgba(245, 166, 35, 0.2)' : 'transparent',
                color: activeTab === tab.id ? 'var(--accent-gold)' : 'var(--text-secondary)',
                border: `1px solid ${activeTab === tab.id ? 'var(--accent-gold)' : 'transparent'}`,
                padding: '6px 16px',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontWeight: activeTab === tab.id ? 'bold' : 'normal',
                fontSize: '0.85rem'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
        
        {/* Dynamic Watchlist Mobile Override */}
        <div className="hide-desktop" style={{ display: 'flex', gap: '4px', overflowX: 'auto', paddingBottom: '4px' }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: activeTab === tab.id ? 'rgba(245, 166, 35, 0.2)' : 'transparent',
                color: activeTab === tab.id ? 'var(--accent-gold)' : 'var(--text-secondary)',
                border: `1px solid ${activeTab === tab.id ? 'var(--accent-gold)' : 'transparent'}`,
                padding: '4px 10px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.75rem',
                whiteSpace: 'nowrap'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="hide-mobile" style={{ fontFamily: 'var(--font-heading)', color: 'var(--accent-gold)', fontSize: '1.2rem', fontWeight: 'bold' }}>
          Global Market Nexus
        </div>
      </div>

      {/* Main Chart Container */}
      <div style={{ flex: 1, width: '100%' }}>
        <AdvancedRealTimeChart 
          key={activeTab} // Forces iframe reload when tab changes to flush the watchlist properly
          symbol="BINANCE:BTCUSDT" 
          theme="dark" 
          interval="5"
          autosize 
          allow_symbol_change={true}
          hide_side_toolbar={false}
          details={true}
          calendar={false}
          watchlist={watchlists[activeTab]}
        />
      </div>
    </div>
  );
};

export default FullChartPage;
