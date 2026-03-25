import React from 'react';
import ParticleBackground from './components/ParticleBackground';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Problem from './components/Problem';
import Solution from './components/Solution';
import TokenPower from './components/TokenPower';
import TheOrder from './components/TheOrder';
import NeetiBook from './components/NeetiBook';
import Roadmap from './components/Roadmap';
import Quiz from './components/Quiz';
import CallToAction from './components/CallToAction';
import Footer from './components/Footer';
import MarketZone from './components/MarketZone';
import FullChartPage from './components/FullChartPage';
import BottomNav from './components/BottomNav';
import './index.css';

function App() {
  const [view, setView] = React.useState('landing');

  if (view === 'chart') {
    return <FullChartPage onBack={() => setView('landing')} />;
  }

  return (
    <>
      <ParticleBackground />
      <Navbar />
      
      {/* Main Content Wrapper - ensures it sits above particles */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        <Hero />
        <Problem />
        <Solution />
        <TokenPower />
        <MarketZone onOpenFullChart={() => setView('chart')} />
        <TheOrder />
        <NeetiBook />
        <Roadmap />
        <Quiz />
        <CallToAction />
        <Footer />
      </div>

      <BottomNav view={view} setView={setView} />
    </>
  );
}

export default App;
