import React from 'react';
import { TickerTape, AdvancedRealTimeChart } from 'react-ts-tradingview-widgets';
import { FaExpand } from 'react-icons/fa';

const MarketZone = ({ onOpenFullChart }) => {
  return (
    <section className="section" id="market">
      <div className="container">
        <div className="text-center mb-4">
          <h2 className="heading-lg text-gradient-gold">Global Market Nexus</h2>
          <p className="text-secondary mb-3" style={{ maxWidth: '600px', margin: '0 auto' }}>
            Track the pulse of Crypto, Forex, and traditional markets in real-time. Stay ahead of the herd with our integrated terminal.
          </p>

          <button 
                onClick={onOpenFullChart}
                className="btn mt-3"
                style={{
                  padding: '10px 20px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  background: 'rgba(20, 20, 25, 0.9)',
                  border: '1px solid var(--accent-gold)',
                  color: 'var(--accent-gold)',
                  cursor: 'pointer',
                  borderRadius: '4px',
                  transition: 'background 0.3s ease'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = 'rgba(245, 166, 35, 0.15)'}
                onMouseOut={(e) => e.currentTarget.style.background = 'rgba(20, 20, 25, 0.9)'}
          >
                <FaExpand style={{ marginRight: '8px' }} /> View Full Terminal
          </button>
        </div>

        {/* Scrolling Ticker Tape */}
        <div className="mb-2" style={{ borderRadius: '8px', overflow: 'hidden' }}>
          <TickerTape 
            colorTheme="dark" 
            displayMode="regular" 
            symbols={[
              { proName: "FOREXCOM:SPXUSD", title: "S&P 500" },
              { proName: "FOREXCOM:NSXUSD", title: "Nasdaq 100" },
              { proName: "BINANCE:BTCUSDT", title: "Bitcoin" },
              { proName: "BINANCE:ETHUSDT", title: "Ethereum" },
              { proName: "BINANCE:SOLUSDT", title: "Solana" },
              { proName: "OANDA:EURUSD", title: "EUR/USD" }
            ]}
          />
        </div>

        {/* Desktop Interface */}
        <div className="mt-4 hide-mobile">
          <div 
            className="glow-gold-box"
            style={{ 
              height: '700px', 
              padding: 0, 
              overflow: 'hidden', 
              position: 'relative',
              background: 'rgba(20, 20, 25, 0.7)',
              backdropFilter: 'blur(12px)',
              WebkitBackdropFilter: 'blur(12px)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              borderRadius: '16px'
            }}
          >
            <div style={{ flex: 1, height: '100%', width: '100%', paddingTop: '0' }}>
              <AdvancedRealTimeChart 
                symbol="BINANCE:BTCUSD" 
                theme="dark" 
                interval="5"
                autosize 
                allow_symbol_change={true}
                hide_side_toolbar={false}
                details={true}
                calendar={false}
                watchlist={[
                  // CRYPTOCURRENCIES
                  "BINANCE:BTCUSDT",
                  "BINANCE:ETHUSDT",
                  "BINANCE:SOLUSDT",
                  "BINANCE:BNBUSDT",
                  "BINANCE:XRPUSDT",
                  "BINANCE:DOGEUSDT",
                  "BINANCE:ADAUSDT",
                  "BINANCE:AVAXUSDT",
                  "BINANCE:DOTUSDT",
                  "BINANCE:LINKUSDT",
                  "BINANCE:MATICUSDT",
                  
                  // FOREX & METALS
                  "OANDA:EURUSD",
                  "OANDA:GBPUSD",
                  "OANDA:USDJPY",
                  "OANDA:AUDUSD",
                  "OANDA:USDCAD",
                  "OANDA:USDCHF",
                  "OANDA:NZDUSD",
                  "OANDA:EURGBP",
                  "OANDA:EURJPY",
                  "OANDA:GBPJPY",
                  "OANDA:XAUUSD", // Gold
                  "OANDA:XAGUSD", // Silver
                  "OANDA:WTICOUSD", // WTI Crude Oil
                  
                  // GLOBAL INDICES
                  "FOREXCOM:SPXUSD", // S&P 500
                  "FOREXCOM:NSXUSD", // Nasdaq 100
                  "FOREXCOM:DJI",    // Dow Jones 30
                  "INDEX:UKX",       // FTSE 100
                  "INDEX:DEU40",     // DAX
                  "INDEX:NKY",       // Nikkei 225
                  "INDEX:CAC40",     // CAC 40

                  // USA BIG TECH STOCKS
                  "NASDAQ:AAPL",
                  "NASDAQ:MSFT",
                  "NASDAQ:NVDA",
                  "NASDAQ:AMZN",
                  "NASDAQ:GOOGL",
                  "NASDAQ:META",
                  "NASDAQ:TSLA",
                  "NASDAQ:NFLX"
                ]}
              />
            </div>
          </div>
        </div>

        {/* Mobile Interface Launcher */}
        <div className="mt-4 hide-desktop text-center">
            <div 
              className="glow-gold-box" 
              onClick={onOpenFullChart} 
              style={{ 
                cursor: 'pointer', 
                padding: '2.5rem 1rem',
                background: 'rgba(20, 20, 25, 0.7)',
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                borderRadius: '16px',
                transition: 'all 0.3s ease'
              }}
            >
                <div style={{ padding: '20px', background: 'rgba(245, 166, 35, 0.1)', display: 'inline-block', borderRadius: '50%', marginBottom: '1rem' }}>
                    <FaExpand size={30} className="text-gold" />
                </div>
                <h3 className="heading-md" style={{ color: 'var(--text-primary)' }}>Launch Terminal</h3>
                <p className="text-secondary" style={{ maxWidth: '80%', margin: '0 auto', fontSize: '0.95rem' }}>Open the full-screen interactive market dashboard designed for mobile analysis.</p>
                <div className="mt-3">
                    <span style={{ color: 'var(--accent-gold)', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '1px', fontSize: '0.85rem' }}>Tap to Expand</span>
                </div>
            </div>
        </div>
      </div>
    </section>
  );
};

export default MarketZone;
