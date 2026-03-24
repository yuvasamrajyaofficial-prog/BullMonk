import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const TokenPower = () => {
  const sectionRef = useRef(null);
  const itemsRef = useRef([]);
  itemsRef.current = [];

  const addToRefs = (el) => {
    if (el && !itemsRef.current.includes(el)) {
      itemsRef.current.push(el);
    }
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        itemsRef.current,
        { x: -50, opacity: 0 },
        {
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 70%",
            end: "bottom 30%",
            toggleActions: "play none none reverse"
          },
          x: 0,
          opacity: 1,
          duration: 0.8,
          stagger: 0.2,
          ease: "power2.out"
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="token" className="section" style={styles.section}>
      <div className="container">
        <h2 className="heading-lg text-center mb-4">
          The <span className="text-gradient-green">Power</span> of BullMonk
        </h2>

        <div className="grid grid-3 mt-4">
          {/* Feature 1 */}
          <div ref={addToRefs} className="glass-card flex-column" style={styles.card}>
            <div style={styles.iconWrapper}>
              <span style={styles.icon}>0%</span>
            </div>
            <h3 className="heading-md mb-1 text-green">Low Fees</h3>
            <p className="text-secondary" style={{ textAlign: 'center' }}>
              Zero friction. Transact without bleeding. The network belongs to the Order.
            </p>
          </div>

          {/* Feature 2 */}
          <div ref={addToRefs} className="glass-card flex-column" style={styles.card}>
            <div style={styles.iconWrapper}>
              <span style={styles.icon}>🤝</span>
            </div>
            <h3 className="heading-md mb-1 text-green">Community-Driven</h3>
            <p className="text-secondary" style={{ textAlign: 'center' }}>
              No VCs, no presale dumps. Fair launch, pure vibes, collective discipline.
            </p>
          </div>

          {/* Feature 3 */}
          <div ref={addToRefs} className="glass-card flex-column" style={styles.card}>
            <div style={styles.iconWrapper}>
              <span style={styles.icon}>💎</span>
            </div>
            <h3 className="heading-md mb-1 text-green">Built for Holders</h3>
            <p className="text-secondary" style={{ textAlign: 'center' }}>
              Patience is rewarded. The weak sell, the strong accumulate.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

const styles = {
  section: {
    minHeight: '60vh',
    display: 'flex',
    alignItems: 'center',
    background: 'linear-gradient(to bottom, transparent, rgba(46, 204, 113, 0.05), transparent)',
  },
  card: {
    padding: '2.5rem 2rem',
    alignItems: 'center',
    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  },
  iconWrapper: {
    width: '70px',
    height: '70px',
    borderRadius: '12px',
    background: 'rgba(46, 204, 113, 0.1)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: '1.2rem',
    border: '1px solid rgba(46, 204, 113, 0.3)',
    boxShadow: '0 0 15px var(--accent-green-glow) inset',
  },
  icon: {
    fontSize: '1.8rem',
    fontWeight: 'bold',
    color: 'var(--accent-green)',
    fontFamily: 'var(--font-heading)',
  }
};

export default TokenPower;
