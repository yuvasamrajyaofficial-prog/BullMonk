import React from 'react';
import { FaHome, FaChartLine, FaCoins, FaUsers } from 'react-icons/fa';

const BottomNav = ({ view, setView }) => {
  const navigateTo = (targetView, hash) => {
    setView(targetView);
    if (hash) {
      setTimeout(() => {
        const el = document.getElementById(hash);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="bottom-nav">
      <div 
        className={`nav-item ${view === 'landing' ? 'active' : ''}`} 
        onClick={() => navigateTo('landing', '')}>
        <FaHome size={20} />
        <span>Home</span>
      </div>
      <div 
        className={`nav-item ${view === 'chart' ? 'active' : ''}`} 
        onClick={() => navigateTo('chart', '')}>
        <FaChartLine size={20} />
        <span>Markets</span>
      </div>
      <div 
        className="nav-item" 
        onClick={() => navigateTo('landing', 'token')}>
        <FaCoins size={20} />
        <span>Token</span>
      </div>
      <div 
        className="nav-item" 
        onClick={() => navigateTo('landing', 'order')}>
        <FaUsers size={20} />
        <span>The Order</span>
      </div>
    </div>
  );
};

export default BottomNav;
