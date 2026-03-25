import React from 'react';
import { FaTelegramPlane, FaSun, FaMoon } from 'react-icons/fa';
import { FaXTwitter } from 'react-icons/fa6'; // Twitter X icon
import { useTheme } from '../context/ThemeContext';

const Navbar = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="navbar" style={styles.nav}>
      <div className="container flex-between" style={styles.container}>
        {/* Logo */}
        <div className="logo" style={styles.logo}>
          <span className="text-gradient-gold" style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-heading)' }}>
            BullMonk
          </span>
        </div>

        {/* Links (Desktop) */}
        <div className="nav-links hide-mobile" style={styles.links}>
          <a href="#philosophy" style={styles.link}>Philosophy</a>
          <a href="#token" style={styles.link}>Token</a>
          <a href="#order" style={styles.link}>The Order</a>
        </div>

        {/* CTA & Socials */}
        <div className="nav-actions flex-center" style={styles.actions}>
            <a href="https://t.me/bullmonkcoin" target="_blank" rel="noreferrer" style={styles.socialIcon}>
                <FaTelegramPlane size={20} />
            </a>
            <a href="https://x.com" target="_blank" rel="noreferrer" style={styles.socialIcon}>
                <FaXTwitter size={20} />
            </a>
          <button className="btn btn-outline hide-mobile" style={{ padding: '0.4rem 1.5rem', fontSize: '0.9rem', marginLeft: '0.5rem' }}>
            Buy Now
          </button>
          
          {/* Theme Toggle Button */}
          <button 
            onClick={toggleTheme} 
            className="btn btn-outline" 
            style={{ padding: '0.4rem 0.8rem', fontSize: '1rem', marginLeft: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? <FaSun /> : <FaMoon />}
          </button>
        </div>
      </div>
    </nav>
  );
};

const styles = {
  nav: {
    position: 'fixed',
    top: 0,
    width: '100%',
    zIndex: 100,
    background: 'var(--bg-card)',
    backdropFilter: 'blur(10px)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
    padding: '1rem 0',
  },
  container: {
     height: '100%',
  },
  logo: {
      cursor: 'pointer'
  },
  links: {
    display: 'flex',
    gap: '2rem',
  },
  link: {
    color: 'var(--text-secondary)',
    textDecoration: 'none',
    fontSize: '0.9rem',
    fontWeight: 500,
    textTransform: 'uppercase',
    letterSpacing: '1px',
    transition: 'color 0.3s ease',
  },
  actions: {
      gap: '1rem'
  },
  socialIcon: {
      color: 'var(--text-secondary)',
      transition: 'all 0.3s ease',
      display: 'flex',
      alignItems: 'center'
  }
};

export default Navbar;
