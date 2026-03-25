import React from 'react';
import { TickerTape, AdvancedRealTimeChart } from 'react-ts-tradingview-widgets';

const MarketZone = () => {
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
          <div className="glass-card glow-gold-box" style={{ height: '700px', padding: 0, overflow: 'hidden' }}>
            <AdvancedRealTimeChart 
              symbol="BINANCE:BTCUSD" 
              theme="dark" 
              autosize 
              allow_symbol_change={true}
              hide_side_toolbar={false}
              details={true}
              calendar={false}
              watchlist={[
                "BINANCE:BTCUSDT",
                "BINANCE:ETHUSDT",
                "BINANCE:SOLUSDT",
                "BINANCE:DOGEUSDT",
                "OANDA:EURUSD",
                "OANDA:GBPUSD",
                "OANDA:USDJPY",
                "OANDA:AUDUSD",
                "OANDA:XAUUSD",
                "FOREXCOM:SPXUSD",
                "FOREXCOM:NSXUSD",
                "FOREXCOM:DJI"
              ]}
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default MarketZone;
