import React, { useState, useEffect } from 'react';
import { TickerTape, AdvancedRealTimeChart } from 'react-ts-tradingview-widgets';
import { FaExpand, FaCompress } from 'react-icons/fa';

const MarketZone = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Prevent background scrolling when expanded
  useEffect(() => {
    if (isExpanded) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto'; // Reset
    }
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isExpanded]);

  const expandedStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    zIndex: 99999,
    background: 'rgba(5, 5, 8, 0.98)',
    backdropFilter: 'blur(20px)',
    padding: '10px',
    display: 'flex',
    flexDirection: 'column'
  };

  const normalStyle = {
    height: '700px', 
    padding: 0, 
    overflow: 'hidden',
    position: 'relative'
  };

  return (
    <section className="section" id="market">
      <div className="container">
        <div className="text-center mb-4">
          <h2 className="heading-lg text-gradient-gold">Global Market Nexus</h2>
          <p className="text-secondary" style={{ maxWidth: '600px', margin: '0 auto' }}>
            Track the pulse of Crypto, Forex, and traditional markets in real-time. Stay ahead of the herd with our integrated terminal.
          </p>
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

        {/* Single Unified Advanced Chart */}
        <div className="mt-4">
          <div 
            className={`glass-card glow-gold-box ${isExpanded ? '' : ''}`} 
            style={isExpanded ? expandedStyle : normalStyle}
          >
            {/* Header for expanded view or just a floating button for normal view */}
            <div style={{
              position: 'absolute',
              top: isExpanded ? '20px' : '15px',
              right: isExpanded ? '20px' : '60px',
              zIndex: 100
            }}>
              <button 
                onClick={() => setIsExpanded(!isExpanded)}
                className="btn glass-card"
                style={{
                  padding: '8px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  background: 'rgba(20, 20, 25, 0.9)',
                  border: '1px solid var(--accent-gold)',
                  color: 'var(--accent-gold)',
                  cursor: 'pointer'
                }}
              >
                {isExpanded ? (
                  <><FaCompress style={{ marginRight: '8px' }} /> Default View</>
                ) : (
                  <><FaExpand style={{ marginRight: '8px' }} /> Full Chart</>
                )}
              </button>
            </div>

            <div style={{ flex: 1, height: '100%', width: '100%', paddingTop: isExpanded ? '60px' : '0' }}>
              <AdvancedRealTimeChart 
                symbol="BINANCE:BTCUSD" 
                theme="dark" 
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
      </div>
    </section>
  );
};

export default MarketZone;
