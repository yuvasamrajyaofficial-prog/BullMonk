import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import FloatingCandles from './FloatingCandles';
import monkImage from '../assets/bullmonk-hero.png';

const Hero = () => {
  const containerRef = useRef(null);
  const textRef = useRef(null);
  const monkRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Reveal animation
      gsap.fromTo(
        textRef.current.children,
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, stagger: 0.2, ease: "power3.out", delay: 0.5 }
      );

      // Monk reveal
      gsap.fromTo(
        monkRef.current,
        { scale: 0.9, opacity: 0, filter: 'blur(10px)' },
        { scale: 1, opacity: 1, filter: 'blur(0px)', duration: 1.5, ease: "power2.out", delay: 0.8 }
      );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={containerRef} className="section flex-center" style={styles.hero}>
      <FloatingCandles />
      
      <div className="container grid grid-2" style={{ alignItems: 'center', zIndex: 2 }}>
        {/* Left: Content */}
        <div ref={textRef} style={styles.content} className="hero-content text-center-mobile">
          <h2 className="heading-md text-gradient-gold" style={{ fontFamily: 'var(--font-body)', fontWeight: 300, letterSpacing: '2px', textTransform: 'uppercase' }}>
            While the market panics...
          </h2>
          <h1 className="heading-xl mt-1 mb-2 glow-text">
            We Remain <br />
            <span className="text-gradient-gold">Still.</span>
          </h1>
          <p className="mb-4" style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '80%' }}>
            BullMonk has awakened. The cycle belongs to those with discipline.
          </p>
          
          <div className="flex-center hero-buttons" style={{ justifyContent: 'flex-start', gap: '1.5rem' }}>
            <button className="btn btn-primary animate-pulse">
              Join The Order
            </button>
            <button className="btn btn-outline">
              Buy Now
            </button>
          </div>
        </div>

        {/* Right: Visual */}
        <div className="flex-center hero-visual" style={styles.visual}>
            {/* Glowing Aura Background */}
            <div style={styles.aura}></div>
            
            {/* Meditating Monk */}
            <img 
              ref={monkRef}
              src={monkImage} 
              alt="BullMonk Meditating" 
              className="animate-breathe"
              style={styles.monkImage} 
            />
        </div>
      </div>
    </section>
  );
};

const styles = {
  hero: {
    minHeight: '100vh',
    paddingTop: '80px', // Offset for navbar
    position: 'relative',
    overflow: 'hidden',
  },
  content: {
    position: 'relative',
    zIndex: 10,
  },
  visual: {
    position: 'relative',
    height: '600px',
  },
  aura: {
    position: 'absolute',
    width: '400px',
    height: '400px',
    background: 'radial-gradient(circle, rgba(245,166,35,0.15) 0%, rgba(0,0,0,0) 70%)',
    borderRadius: '50%',
    zIndex: 1,
    animation: 'pulse 4s infinite alternate',
  },
  monkImage: {
    width: '100%',
    maxWidth: '500px',
    height: 'auto',
    objectFit: 'contain',
    position: 'relative',
    zIndex: 2,
    filter: 'drop-shadow(0 0 20px rgba(245,166,35,0.3))',
  }
};

export default Hero;
