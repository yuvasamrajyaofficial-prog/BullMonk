import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const Problem = () => {
  const sectionRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context((self) => {
      const textElements = self.selector('.reveal-text');
      textElements.forEach((text, index) => {
        gsap.fromTo(
          text,
          { 
            y: 50, 
            opacity: 0,
            scale: 0.9,
            filter: 'blur(10px)'
          },
          {
            scrollTrigger: {
              trigger: text,
              start: "top 80%",
              end: "bottom 60%",
              toggleActions: "play none none reverse"
            },
            y: 0,
            opacity: 1,
            scale: 1,
            filter: 'blur(0px)',
            duration: 1,
            ease: "power3.out",
            delay: index * 0.2 // Stagger
          }
        );
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="problem" className="section flex-center" style={styles.problem}>
      <div className="container" style={{ textAlign: 'center' }}>
        <h2 className="heading-lg text-gradient-red reveal-text" style={styles.line}>
          You bought late.
        </h2>
        
        <h2 className="heading-lg text-muted reveal-text" style={styles.line}>
          You sold in fear.
        </h2>
        
        <h2 className="heading-lg glow-text mb-4 reveal-text" style={{...styles.line, color: '#fff' }}>
          You missed the cycle.
        </h2>

        <div className="reveal-text" style={styles.divider}></div>

        <p className="text-secondary reveal-text" style={{ fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto', letterSpacing: '1px' }}>
          This is the pain of the uninitiated. The noise of the market was designed to break you. But it doesn't have to be this way.
        </p>
      </div>
    </section>
  );
};

const styles = {
  problem: {
    minHeight: '80vh',
    background: 'linear-gradient(to bottom, transparent, rgba(20, 10, 10, 0.4), transparent)',
  },
  line: {
    fontFamily: 'var(--font-heading)',
    marginBottom: '2rem',
  },
  divider: {
    width: '1px',
    height: '100px',
    background: 'linear-gradient(to bottom, transparent, var(--accent-red), transparent)',
    margin: '3rem auto',
    opacity: 0.5,
  }
};

export default Problem;
