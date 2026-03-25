import React, { useState } from 'react';
import { FaTelegramPlane, FaSun, FaMoon, FaBars, FaTimes } from 'react-icons/fa';
import { FaXTwitter } from 'react-icons/fa6';
import { useTheme } from '../context/ThemeContext';

const Navbar = ({ setView }) => {
  const { theme, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleNav = (target) => {
    setMenuOpen(false);
    if (target === 'philosophy') {
      setView && setView('philosophy');
    } else if (target === 'landing') {
      setView && setView('landing');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      // Scroll to section
      setView && setView('landing');
      setTimeout(() => {
        const el = document.getElementById(target);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  };

  return (
    <>
      <nav className="navbar" style={styles.nav}>
        <div className="container flex-between" style={styles.container}>
          {/* Logo */}
          <div className="logo" style={styles.logo} onClick={() => handleNav('landing')}>
            <span className="text-gradient-gold" style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-heading)' }}>
              BullMonk
            </span>
          </div>

          {/* Links (Desktop) */}
          <div className="nav-links hide-mobile" style={styles.links}>
            <a href="#" onClick={(e) => { e.preventDefault(); handleNav('philosophy'); }} style={styles.link}>Philosophy</a>
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

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="btn btn-outline"
              style={{ padding: '0.4rem 0.8rem', fontSize: '1rem', marginLeft: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? <FaSun /> : <FaMoon />}
            </button>

            {/* Hamburger (Mobile Only) */}
            <button
              className="hide-desktop"
              onClick={() => setMenuOpen(!menuOpen)}
              style={{
                background: 'transparent',
                border: '1px solid rgba(245, 166, 35, 0.3)',
                color: 'var(--accent-gold)',
                padding: '6px 8px',
                borderRadius: '6px',
                cursor: 'pointer',
                marginLeft: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              aria-label="Menu"
            >
              {menuOpen ? <FaTimes size={18} /> : <FaBars size={18} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Slide-Down Menu */}
      <div style={{
        position: 'fixed',
        top: menuOpen ? '65px' : '-300px',
        left: 0,
        width: '100%',
        zIndex: 99,
        background: 'var(--bg-card)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(245, 166, 35, 0.15)',
        padding: menuOpen ? '24px 20px' : '0 20px',
        transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
        opacity: menuOpen ? 1 : 0,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <a href="#" onClick={(e) => { e.preventDefault(); handleNav('philosophy'); }} style={styles.mobileLink}>
          Philosophy
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); handleNav('token'); }} style={styles.mobileLink}>
          Token
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); handleNav('order'); }} style={styles.mobileLink}>
          The Order
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); handleNav('market'); }} style={styles.mobileLink}>
          Markets
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); handleNav('neeti'); }} style={styles.mobileLink}>
          Neeti Book
        </a>
        <button
          className="btn"
          onClick={() => setMenuOpen(false)}
          style={{
            width: '100%',
            padding: '12px',
            background: 'rgba(245, 166, 35, 0.15)',
            border: '1px solid var(--accent-gold)',
            color: 'var(--accent-gold)',
            borderRadius: '8px',
            cursor: 'pointer',
            fontFamily: 'var(--font-heading)',
            fontSize: '0.9rem',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginTop: '8px'
          }}
        >
          Buy Now
        </button>
      </div>

      {/* Overlay backdrop */}
      {menuOpen && (
        <div
          onClick={() => setMenuOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'rgba(0,0,0,0.5)',
            zIndex: 98
          }}
        />
      )}
    </>
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
    borderBottom: '1px solid var(--border-subtle)',
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
  mobileLink: {
    color: 'var(--text-primary)',
    textDecoration: 'none',
    fontSize: '1.05rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '2px',
    fontFamily: 'var(--font-heading)',
    padding: '8px 0',
    borderBottom: '1px solid var(--border-subtle)',
    transition: 'color 0.3s ease',
  },
  actions: {
    gap: '0.7rem'
  },
  socialIcon: {
    color: 'var(--text-secondary)',
    transition: 'all 0.3s ease',
    display: 'flex',
    alignItems: 'center'
  }
};

export default Navbar;
