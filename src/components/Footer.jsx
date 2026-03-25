import React from 'react';

const Footer = () => {
  return (
    <footer style={styles.footer} className="flex-column text-center">
      <div className="container" style={{ padding: '2rem 0' }}>
        <h3 className="heading-md text-gold mb-1" style={{ fontSize: '1.5rem' }}>
          BullMonk
        </h3>
        <p className="text-muted mb-2">
          Patience is power.
        </p>
        
        <div className="flex-center mb-2" style={{ gap: '1rem' }}>
          <a href="https://t.me/bullmonkcoin" target="_blank" rel="noopener noreferrer" style={styles.link}>Telegram</a>
          <span className="text-muted">|</span>
          <a href="https://x.com" style={styles.link}>X (Twitter)</a>
          <span className="text-muted">|</span>
          <a href="#token" style={styles.link}>Token</a>
        </div>
        
        <p className="text-secondary" style={{ fontSize: '0.8rem', opacity: 0.5 }}>
          Disclaimer: $BULLMONK is a meme coin created for entertainment and community building. It has no intrinsic value or expectation of financial return. Cryptocurrencies are highly volatile. Do your own research. Not financial advice.
        </p>
      </div>
      
      <div style={styles.bottomBar}>
        <p className="text-muted" style={{ fontSize: '0.8rem' }}>
          &copy; {new Date().getFullYear()} BullMonk. All rights reserved. Let the paper hands fold.
        </p>
      </div>
    </footer>
  );
};

const styles = {
  footer: {
    background: 'var(--bg-deep)',
    borderTop: '1px solid var(--border-subtle)',
    position: 'relative',
    zIndex: 10, // Above particles
  },
  link: {
    color: 'var(--text-secondary)',
    textDecoration: 'none',
    transition: 'color 0.3s ease',
  },
  bottomBar: {
    background: '#020204',
    padding: '1rem 0',
    width: '100%',
  }
};

export default Footer;
