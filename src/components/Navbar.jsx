import React from 'react';
import { FaTelegramPlane } from 'react-icons/fa';
import { FaXTwitter } from 'react-icons/fa6'; // Twitter X icon

const Navbar = () => {
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
        <div className="nav-links" style={styles.links}>
          <a href="#philosophy" style={styles.link}>Philosophy</a>
          <a href="#token" style={styles.link}>Token</a>
          <a href="#order" style={styles.link}>The Order</a>
        </div>

        {/* CTA & Socials */}
        <div className="nav-actions flex-center" style={styles.actions}>
            <a href="https://t.me" target="_blank" rel="noreferrer" style={styles.socialIcon}>
                <FaTelegramPlane size={20} />
            </a>
            <a href="https://x.com" target="_blank" rel="noreferrer" style={styles.socialIcon}>
                <FaXTwitter size={20} />
            </a>
          <button className="btn btn-outline" style={{ padding: '0.5rem 1.5rem', fontSize: '0.9rem', marginLeft: '1rem' }}>
            Buy Now
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
    background: 'rgba(10, 10, 15, 0.8)',
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
