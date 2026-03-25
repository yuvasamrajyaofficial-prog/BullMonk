import React from 'react';
import { TickerTape, MarketOverview, AdvancedRealTimeChart } from 'react-ts-tradingview-widgets';

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
              { proName: "FX:EURUSD", title: "EUR/USD" }
            ]}
          />
        </div>

        <div className="grid grid-2 mt-4">
          {/* Advanced Chart */}
          <div className="glass-card glow-gold-box" style={{ height: '550px', padding: 0, overflow: 'hidden' }}>
            <AdvancedRealTimeChart 
              symbol="BINANCE:BTCUSD" 
              theme="dark" 
              autosize 
              allow_symbol_change={true}
              hide_side_toolbar={false}
              details={true}
              hotlist={true}
              calendar={false}
            />
          </div>

          {/* Market Overview */}
          <div className="glass-card glow-gold-box" style={{ height: '550px', padding: 0, overflow: 'hidden' }}>
             <MarketOverview 
              colorTheme="dark" 
              height="100%" 
              width="100%" 
              showFloatingTooltip={true}
              tabs={[
                {
                  title: "Crypto",
                  symbols: [
                    { s: "BINANCE:BTCUSDT", d: "Bitcoin" },
                    { s: "BINANCE:ETHUSDT", d: "Ethereum" },
                    { s: "BINANCE:SOLUSDT", d: "Solana" },
                    { s: "BINANCE:BNBUSDT", d: "BNB" },
                    { s: "BINANCE:DOGEUSDT", d: "Dogecoin" }
                  ],
                },
                {
                  title: "Forex",
                  symbols: [
                    { s: "FX:EURUSD", d: "EUR/USD" },
                    { s: "FX:GBPUSD", d: "GBP/USD" },
                    { s: "FX:USDJPY", d: "USD/JPY" },
                    { s: "FX:AUDUSD", d: "AUD/USD" },
                    { s: "FX:USDCAD", d: "USD/CAD" }
                  ],
                },
                {
                  title: "Indices",
                  symbols: [
                    { s: "FOREXCOM:SPXUSD", d: "S&P 500" },
                    { s: "FOREXCOM:NSXUSD", d: "Nasdaq 100" },
                    { s: "FOREXCOM:DJI", d: "Dow 30" },
                    { s: "INDEX:NKY", d: "Nikkei 225" },
                    { s: "INDEX:DEU40", d: "DAX Index" }
                  ],
                }
              ]}
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default MarketZone;
