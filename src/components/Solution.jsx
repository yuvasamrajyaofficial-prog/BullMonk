import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const Solution = () => {
  const sectionRef = useRef(null);
  const titleRef = useRef(null);
  const cardsRef = useRef([]);
  cardsRef.current = [];

  const addToRefs = (el) => {
    if (el && !cardsRef.current.includes(el)) {
      cardsRef.current.push(el);
    }
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Title reveal
      gsap.fromTo(
        titleRef.current,
        { y: 30, opacity: 0 },
        {
          scrollTrigger: {
            trigger: titleRef.current,
            start: "top 80%",
            end: "bottom 60%",
            toggleActions: "play none none reverse"
          },
          y: 0,
          opacity: 1,
          duration: 1,
          ease: "power2.out"
        }
      );

      // Cards stagger
      gsap.fromTo(
        cardsRef.current,
        { y: 50, opacity: 0, scale: 0.95 },
        {
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 60%",
            end: "bottom 20%",
            toggleActions: "play none none reverse"
          },
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 0.8,
          stagger: 0.2,
          ease: "back.out(1.2)"
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="philosophy" className="section" style={styles.section}>
      <div className="container">
        <div ref={titleRef} style={styles.header}>
          <h2 className="heading-lg mb-2">
            BullMonk doesn't chase the market.<br/>
            <span className="text-gradient-gold">He becomes it.</span>
          </h2>
          <p className="text-secondary" style={{ fontSize: '1.2rem', maxWidth: '800px', margin: '0 auto' }}>
            In chaos, there is opportunity. While the masses panic sell at the bottom and FOMO buy at the top, the Order remains still. We accumulate in silence. We hold with conviction.
          </p>
        </div>

        <div className="grid grid-3 mt-4">
          {/* Card 1 */}
          <div ref={addToRefs} className="glass-card flex-column" style={styles.card}>
            <div style={styles.iconWrapper}>
              <span style={styles.icon}>🧘</span>
            </div>
            <h3 className="heading-md mb-1 text-gold">Mastery</h3>
            <p className="text-secondary">
              Panic is the enemy. Patience is power. We do not react to the noise. We observe, we learn, and we execute without emotion.
            </p>
          </div>

          {/* Card 2 */}
          <div ref={addToRefs} className="glass-card flex-column" style={styles.card}>
            <div style={styles.iconWrapper}>
              <span style={styles.icon}>💎</span>
            </div>
            <h3 className="heading-md mb-1 text-gold">Conviction</h3>
            <p className="text-secondary">
              Diamond hands are built in the depths of the bear market. When others see red candles and fear, BullMonk sees discount and accumulation.
            </p>
          </div>

          {/* Card 3 */}
          <div ref={addToRefs} className="glass-card flex-column" style={styles.card}>
            <div style={styles.iconWrapper}>
              <span style={styles.icon}>👁️</span>
            </div>
            <h3 className="heading-md mb-1 text-gold">Vision</h3>
            <p className="text-secondary">
              We look past the daily charts and 5-minute candles. The true cycle is measured in years. We ascend while the impatient get shaken out.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

const styles = {
  section: {
    minHeight: '80vh',
    display: 'flex',
    alignItems: 'center',
  },
  header: {
    textAlign: 'center',
    marginBottom: '4rem',
  },
  card: {
    padding: '3rem 2rem',
    textAlign: 'center',
    alignItems: 'center',
    height: '100%',
  },
  iconWrapper: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: 'rgba(245, 166, 35, 0.1)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: '1.5rem',
    border: '1px solid rgba(245, 166, 35, 0.3)',
    boxShadow: '0 0 20px var(--accent-gold-glow) inset',
  },
  icon: {
    fontSize: '2.5rem',
    filter: 'drop-shadow(0 0 10px rgba(245, 166, 35, 0.5))',
  }
};

export default Solution;
