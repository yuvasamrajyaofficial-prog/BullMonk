import React from 'react';
import { AdvancedRealTimeChart } from 'react-ts-tradingview-widgets';
import { FaArrowLeft } from 'react-icons/fa';

const FullChartPage = ({ onBack }) => {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#050508', position: 'relative', display: 'flex', flexDirection: 'column' }}>
      {/* Header bar */}
      <div style={{ 
        padding: '0.8rem 1.5rem', 
        display: 'flex', 
        alignItems: 'center', 
        background: 'rgba(10, 10, 15, 0.95)', 
        borderBottom: '1px solid rgba(245, 166, 35, 0.2)' 
      }}>
        <button 
          onClick={onBack}
          className="btn btn-outline"
          style={{ display: 'flex', alignItems: 'center', padding: '0.5rem 1rem', fontSize: '0.9rem', borderRadius: '4px' }}
        >
          <FaArrowLeft style={{ marginRight: '0.5rem' }} /> Back to BullMonk
        </button>
        <div style={{ marginLeft: 'auto', fontFamily: 'var(--font-heading)', color: 'var(--accent-gold)', fontWeight: 'bold', fontSize: '1.2rem', letterSpacing: '1px' }}>
          GLOBAL MARKET NEXUS
        </div>
      </div>

      {/* Main Chart Container */}
      <div style={{ flex: 1, width: '100%' }}>
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
  );
};

export default FullChartPage;
