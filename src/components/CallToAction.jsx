import React from 'react';

const CallToAction = () => {
  return (
    <section className="section flex-center text-center" style={styles.section}>
      <div className="container" style={{ position: 'relative', zIndex: 2 }}>
        <h2 className="heading-lg mb-2">
          The next cycle has already begun.<br />
          <span className="text-gradient-red" style={{ filter: 'drop-shadow(0 0 10px rgba(231, 76, 60, 0.5))' }}>
            Are you ready?
          </span>
        </h2>
        <p className="text-secondary mb-4" style={{ fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto' }}>
          Stop letting the market control you. Take control of your portfolio and your mindset. Buy BullMonk, join the Order, and master the cycle.
        </p>
        
        <button className="btn btn-primary animate-pulse" style={styles.ctaBtn}>
          Buy Now
        </button>
      </div>

      {/* Decorative Glows */}
      <div style={{...styles.glow, ...styles.leftGlow}}></div>
      <div style={{...styles.glow, ...styles.rightGlow}}></div>
    </section>
  );
};

const styles = {
  section: {
    minHeight: '60vh',
    position: 'relative',
    overflow: 'hidden',
    borderTop: '1px solid rgba(231, 76, 60, 0.1)',
  },
  ctaBtn: {
    padding: '1.2rem 4rem',
    fontSize: '1.2rem',
    letterSpacing: '2px',
    background: 'linear-gradient(90deg, #f5a623 0%, #e74c3c 100%)',
    boxShadow: '0 0 30px rgba(245, 166, 35, 0.4)',
    border: 'none',
    color: '#000',
  },
  glow: {
    position: 'absolute',
    width: '400px',
    height: '400px',
    borderRadius: '50%',
    filter: 'blur(100px)',
    zIndex: 1,
    opacity: 0.2,
  },
  leftGlow: {
    left: '-100px',
    bottom: '-100px',
    background: 'var(--accent-red)',
  },
  rightGlow: {
    right: '-100px',
    top: '-100px',
    background: 'var(--accent-gold)',
  }
};

export default CallToAction;
