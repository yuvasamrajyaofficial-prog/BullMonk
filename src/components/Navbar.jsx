import React, { useState } from 'react';
import { FaSun, FaMoon, FaBars, FaTimes, FaTerminal, FaShieldAlt, FaChartLine, FaRobot, FaLayerGroup, FaCalculator } from 'react-icons/fa';
import { useTheme } from '../context/ThemeContext';

const Navbar = ({ activeTab, setActiveTab }) => {
  const { theme, toggleTheme } = useTheme();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Terminal', icon: FaTerminal },
    { id: 'market-data', label: 'Market Data & NIFTY', icon: FaChartLine },
    { id: 'feature-engine', label: 'Quant Indicators', icon: FaCalculator },
    { id: 'option-chain', label: 'Option Chain', icon: FaLayerGroup },
    { id: 'ai-lab', label: 'AI Strategy Lab', icon: FaRobot },
    { id: 'backtesting', label: 'Backtester', icon: FaChartLine },
    { id: 'risk-gateway', label: 'Risk & Execution', icon: FaShieldAlt },
    { id: 'architecture', label: 'Architecture', icon: FaLayerGroup },
  ];

  const handleSelect = (id) => {
    setActiveTab(id);
    setMobileOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      <nav style={styles.nav}>
        <div className="container flex-between" style={styles.container}>
          {/* Logo */}
          <div style={styles.logoGroup} onClick={() => handleSelect('overview')}>
            <span className="text-gradient-gold" style={styles.brand}>BullMonk</span>
            <span style={styles.badgeQuant}>QUANT AI</span>
          </div>

          {/* Nav Items (Desktop) */}
          <div className="hide-mobile" style={styles.links}>
            {navItems.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item.id)}
                  style={{
                    ...styles.navBtn,
                    color: isActive ? 'var(--accent-gold)' : 'var(--text-secondary)',
                    borderBottom: isActive ? '2px solid var(--accent-gold)' : '2px solid transparent',
                  }}
                >
                  <Icon size={12} style={{ opacity: isActive ? 1 : 0.6 }} />
                  {item.label}
                </button>
              );
            })}
          </div>

          {/* Actions & Session indicators */}
          <div style={styles.actions}>
            {/* NSE Market Session Indicator */}
            <div className="hide-mobile" style={styles.sessionPill}>
              <span className="status-dot status-dot-green" />
              <span>NSE: 09:15-15:30 IST</span>
            </div>

            {/* Launch Paper Trading Button */}
            <button
              className="btn btn-primary btn-sm hide-mobile"
              onClick={() => handleSelect('ai-lab')}
              style={{ fontWeight: 700 }}
            >
              AI Strategy Lab
            </button>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              style={styles.iconBtn}
              aria-label="Toggle Theme"
              title="Toggle theme"
            >
              {theme === 'dark' ? <FaSun size={15} color="#F5A623" /> : <FaMoon size={15} color="#F5A623" />}
            </button>

            {/* Mobile Hamburger */}
            <button
              className="hide-desktop"
              onClick={() => setMobileOpen(!mobileOpen)}
              style={styles.iconBtn}
              aria-label="Toggle Navigation"
            >
              {mobileOpen ? <FaTimes size={18} /> : <FaBars size={18} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Drawer */}
      {mobileOpen && (
        <div style={styles.mobileDrawer}>
          <div style={{ padding: '1rem' }}>
            <div style={{ marginBottom: '1rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={styles.sessionPill}>
                <span className="status-dot status-dot-green" />
                <span>NSE Market: ACTIVE</span>
              </div>
            </div>
            {navItems.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item.id)}
                  style={{
                    ...styles.mobileNavBtn,
                    color: isActive ? 'var(--accent-gold)' : 'var(--text-primary)',
                    background: isActive ? 'rgba(245, 166, 35, 0.1)' : 'transparent',
                  }}
                >
                  <Icon size={14} color={isActive ? '#F5A623' : '#94A3B8'} />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
};

const styles = {
  nav: {
    position: 'sticky',
    top: '32px',
    width: '100%',
    background: 'var(--bg-glass)',
    backdropFilter: 'blur(20px)',
    borderBottom: '1px solid var(--border-card)',
    zIndex: 90,
  },
  container: {
    height: '62px',
  },
  logoGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.6rem',
    cursor: 'pointer',
  },
  brand: {
    fontSize: '1.45rem',
    fontWeight: 800,
    letterSpacing: '-0.02em',
  },
  badgeQuant: {
    fontSize: '0.65rem',
    fontWeight: 800,
    letterSpacing: '0.08em',
    padding: '2px 6px',
    borderRadius: '4px',
    background: 'rgba(245, 166, 35, 0.15)',
    color: 'var(--accent-gold)',
    border: '1px solid rgba(245, 166, 35, 0.3)',
  },
  links: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.2rem',
    height: '100%',
  },
  navBtn: {
    background: 'transparent',
    border: 'none',
    padding: '0 0.85rem',
    height: '62px',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.45rem',
    fontSize: '0.86rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.18s ease',
  },
  actions: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  sessionPill: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.45rem',
    padding: '0.3rem 0.75rem',
    borderRadius: '999px',
    background: 'rgba(0, 245, 160, 0.08)',
    border: '1px solid rgba(0, 245, 160, 0.25)',
    color: 'var(--profit-green)',
    fontSize: '0.74rem',
    fontWeight: 600,
    fontFamily: 'var(--font-mono)',
  },
  iconBtn: {
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid var(--border-subtle)',
    borderRadius: '8px',
    width: '36px',
    height: '36px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--text-primary)',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  mobileDrawer: {
    position: 'fixed',
    top: '94px',
    left: 0,
    width: '100%',
    background: 'var(--bg-card)',
    backdropFilter: 'blur(24px)',
    borderBottom: '1px solid var(--border-card)',
    zIndex: 89,
    boxShadow: 'var(--shadow-card)',
  },
  mobileNavBtn: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    border: 'none',
    fontSize: '0.95rem',
    fontWeight: 600,
    cursor: 'pointer',
    textAlign: 'left',
    marginBottom: '0.25rem',
  },
};

export default Navbar;
