import React, { useState } from 'react';
import ParticleBackground from './components/ParticleBackground';
import LiveTickerBar from './components/LiveTickerBar';
import Navbar from './components/Navbar';
import QuantHero from './components/QuantHero';
import MarketDataExplorer from './components/MarketDataExplorer';
import NiftyOptionChainView from './components/NiftyOptionChainView';
import AIStrategyLab from './components/AIStrategyLab';
import BacktestingConsole from './components/BacktestingConsole';
import RiskAndExecutionGateway from './components/RiskAndExecutionGateway';
import ArchitectureHealthConsole from './components/ArchitectureHealthConsole';
import Footer from './components/Footer';
import './index.css';

function App() {
  const [activeSection, setActiveSection] = useState('overview');

  return (
    <div className="quant-app" style={{ minHeight: '100vh', background: 'var(--bg-obsidian)', color: '#f8fafc', position: 'relative' }}>
      {/* Background Matrix Particles */}
      <ParticleBackground />

      {/* Real-Time Live Ticker Bar */}
      <div style={{ position: 'relative', zIndex: 30 }}>
        <LiveTickerBar />
      </div>

      {/* Main Navigation Bar */}
      <Navbar 
        activeTab={activeSection} 
        setActiveTab={setActiveSection} 
        activeSection={activeSection} 
        setActiveSection={setActiveSection} 
      />

      {/* Main Application Container */}
      <main style={{ position: 'relative', zIndex: 1 }}>
        {/* Institutional Quant Hero Section */}
        <QuantHero 
          onNavigate={(id) => {
            setActiveSection(id);
            const el = document.getElementById(id);
            if (el) el.scrollIntoView({ behavior: 'smooth' });
          }} 
        />

        {/* Market Data & Synthetic Engine Subsystem */}
        <MarketDataExplorer />

        {/* NIFTY 50 Option Chain & Greeks Ladder */}
        <NiftyOptionChainView />

        {/* AI Prompt-to-Strategy Engine */}
        <AIStrategyLab />

        {/* High-Fidelity Backtesting & Monte Carlo Console */}
        <BacktestingConsole />

        {/* Pre-Trade Risk Management & Multi-Broker Gateway */}
        <RiskAndExecutionGateway />

        {/* System Architecture & Test Verification Status */}
        <ArchitectureHealthConsole />
      </main>

      {/* Institutional Quantitative Trading Footer */}
      <Footer />
    </div>
  );
}

export default App;
