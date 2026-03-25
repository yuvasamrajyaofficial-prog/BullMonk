import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { FaTelegramPlane } from 'react-icons/fa';
import { FaXTwitter } from 'react-icons/fa6';

gsap.registerPlugin(ScrollTrigger);

const TheOrder = () => {
  const sectionRef = useRef(null);
  const titleRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context((self) => {
      // Title reveal
      gsap.fromTo(
        titleRef.current,
        { scale: 0.9, opacity: 0 },
        {
          scrollTrigger: {
            trigger: titleRef.current,
            start: "top 80%",
            end: "bottom 60%",
            toggleActions: "play none none reverse"
          },
          scale: 1,
          opacity: 1,
          duration: 1,
          ease: "power2.out"
        }
      );

      // Stats stagger
      const stats = self.selector('.stat-box');
      gsap.fromTo(
        stats,
        { y: 30, opacity: 0 },
        {
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 60%",
            end: "bottom 20%",
            toggleActions: "play none none reverse"
          },
          y: 0,
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
    <section ref={sectionRef} id="order" className="section" style={styles.section}>
      <div className="container" style={{ textAlign: 'center' }}>
        <div ref={titleRef} style={styles.content}>
          <h2 className="heading-lg mb-2">
            This is not just a coin.<br />
            <span className="text-gradient-gold">This is discipline in motion.</span>
          </h2>
          <p className="text-secondary mb-4" style={{ fontSize: '1.2rem', maxWidth: '700px', margin: '0 auto' }}>
            The Order is growing. While the rest of the market acts on emotion, we act on strategy. Join the inner circle.
          </p>

          <div className="flex-center flex-center-mobile" style={{ gap: '1.5rem', marginBottom: '4rem' }}>
            <a href="https://t.me/bullmonkcoin" target="_blank" rel="noreferrer" className="btn glass-card" style={styles.socialBtn}>
              <FaTelegramPlane size={24} style={{ marginRight: '0.8rem', color: '#0088cc' }} />
              Join The Order
            </a>
            <a href="https://x.com" target="_blank" rel="noreferrer" className="btn glass-card" style={styles.socialBtn}>
              <FaXTwitter size={24} style={{ marginRight: '0.8rem' }} />
              Follow the Awakened
            </a>
          </div>
        </div>

        <div className="grid grid-3">
          {/* Stat 1 */}
          <div className="stat-box" style={styles.statBox}>
            <div className="text-gradient-gold mb-1" style={styles.statNumber}>10k+</div>
            <div className="text-secondary text-uppercase" style={{ letterSpacing: '2px' }}>Followers</div>
          </div>

          {/* Stat 2 */}
          <div className="stat-box" style={styles.statBox}>
            <div className="text-gradient-gold mb-1" style={styles.statNumber}>$0</div>
            <div className="text-secondary text-uppercase" style={{ letterSpacing: '2px' }}>VC Funding</div>
          </div>

          {/* Stat 3 */}
          <div className="stat-box" style={styles.statBox}>
            <div className="text-gradient-gold mb-1" style={styles.statNumber}>100%</div>
            <div className="text-secondary text-uppercase" style={{ letterSpacing: '2px' }}>Conviction</div>
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
    background: 'var(--bg-deep)',
    borderTop: '1px solid rgba(245, 166, 35, 0.1)',
    borderBottom: '1px solid rgba(245, 166, 35, 0.1)',
  },
  content: {
    position: 'relative',
    zIndex: 2,
  },
  socialBtn: {
    padding: '1rem 2rem',
    textTransform: 'none',
    border: '1px solid var(--border-subtle)',
    color: 'var(--text-primary)',
    textDecoration: 'none',
    letterSpacing: '0px',
  },
  statBox: {
    padding: '2rem',
    background: 'transparent',
  },
  statNumber: {
    fontSize: '4rem',
    fontWeight: 800,
    fontFamily: 'var(--font-heading)',
    lineHeight: 1,
    filter: 'drop-shadow(0 0 10px rgba(245, 166, 35, 0.3))',
  }
};

export default TheOrder;
