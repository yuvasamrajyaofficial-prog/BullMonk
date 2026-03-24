import React from 'react';

const FloatingCandles = () => {
  return (
    <div style={styles.container}>
      {/* Green Candles (Up) */}
      <div className="animate-float" style={{ ...styles.candle, ...styles.green, top: '20%', left: '10%', height: '120px' }}>
        <div style={styles.wick}></div>
      </div>
      <div className="animate-float-delayed" style={{ ...styles.candle, ...styles.green, top: '60%', right: '15%', height: '80px', animationDelay: '1s' }}>
        <div style={styles.wick}></div>
      </div>
      <div className="animate-float" style={{ ...styles.candle, ...styles.green, top: '30%', right: '5%', height: '150px', animationDelay: '3s', opacity: 0.5 }}>
        <div style={styles.wick}></div>
      </div>

      {/* Red Candles (Down) */}
      <div className="animate-float-delayed" style={{ ...styles.candle, ...styles.red, top: '15%', right: '25%', height: '100px', animationDelay: '0.5s' }}>
        <div style={styles.wick}></div>
      </div>
      <div className="animate-float" style={{ ...styles.candle, ...styles.red, top: '70%', left: '20%', height: '90px', animationDelay: '2s' }}>
        <div style={styles.wick}></div>
      </div>
      <div className="animate-float-delayed" style={{ ...styles.candle, ...styles.red, top: '45%', left: '5%', height: '140px', animationDelay: '4s', opacity: 0.4 }}>
        <div style={styles.wick}></div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    zIndex: 1,
  },
  candle: {
    position: 'absolute',
    width: '24px',
    borderRadius: '4px',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    opacity: 0.8,
    boxShadow: '0 0 20px rgba(0,0,0,0.5)',
  },
  green: {
    background: 'linear-gradient(180deg, #2ecc71 0%, #27ae60 100%)',
    boxShadow: '0 0 15px var(--accent-green-glow)',
  },
  red: {
    background: 'linear-gradient(180deg, #e74c3c 0%, #c0392b 100%)',
    boxShadow: '0 0 15px var(--accent-red-glow)',
  },
  wick: {
    position: 'absolute',
    width: '2px',
    height: '140%', // Extends past the candle body
    background: 'rgba(255, 255, 255, 0.5)',
    zIndex: -1,
  }
};

export default FloatingCandles;
