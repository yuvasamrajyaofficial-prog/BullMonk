import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const Roadmap = () => {
  const sectionRef = useRef(null);
  const lineRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context((self) => {
      // Line animation
      gsap.fromTo(
        lineRef.current,
        { height: 0 },
        {
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top center",
            end: "bottom center",
            scrub: 1
          },
          height: "100%",
          ease: "none"
        }
      );

      // Phase reveals
      const phases = self.selector('.roadmap-phase');
      phases.forEach((phase, index) => {
        gsap.fromTo(
          phase,
          { x: index % 2 === 0 ? 50 : -50, opacity: 0 },
          {
            scrollTrigger: {
              trigger: phase,
              start: "top 80%",
              end: "bottom 60%",
              toggleActions: "play none none reverse"
            },
            x: 0,
            opacity: 1,
            duration: 0.8,
            ease: "power2.out"
          }
        );
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="roadmap" className="section" style={styles.section}>
      <div className="container">
        <h2 className="heading-lg text-center mb-4">
          The <span className="text-gradient-gold">Path</span>
        </h2>

        <div style={styles.timeline}>
          {/* Timeline Line */}
          <div className="roadmap-line-bg" style={styles.lineBg}></div>
          <div ref={lineRef} className="roadmap-line-fill" style={styles.lineFill}></div>

          {/* Phase 1 */}
          <div className="glass-card roadmap-phase" style={{...styles.phase, ...styles.leftPhase}}>
            <div className="roadmap-node-left" style={styles.phaseNode}>1</div>
            <h3 className="heading-md text-gold mb-1">Awakening</h3>
            <p className="text-secondary">
              The monk opens his eyes. We build the foundation, gather the first disciples, and establish the philosophy. Stealth accumulation begins.
            </p>
          </div>

          {/* Phase 2 */}
          <div className="glass-card roadmap-phase" style={{...styles.phase, ...styles.rightPhase}}>
            <div className="roadmap-node-right" style={styles.phaseNode}>2</div>
            <h3 className="heading-md text-gold mb-1">Expansion</h3>
            <p className="text-secondary">
              The teachings spread. Viral mechanics activate. We convert the panic sellers into disciplined holders. The Order multiplies.
            </p>
          </div>

          {/* Phase 3 */}
          <div className="glass-card roadmap-phase" style={{...styles.phase, ...styles.leftPhase}}>
            <div className="roadmap-node-left" style={styles.phaseNode}>3</div>
            <h3 className="heading-md text-gold mb-1">Domination</h3>
            <p className="text-secondary">
              The market recognizes the silent giant. CEX listings follow community demand. We swallow the weak hands.
            </p>
          </div>

          {/* Phase 4 */}
          <div className="glass-card roadmap-phase" style={{...styles.phase, ...styles.rightPhase}}>
            <div className="roadmap-node-right" style={styles.phaseNode}>4</div>
            <h3 className="heading-md mb-1 glow-text">Global Order</h3>
            <p className="text-secondary">
              BullMonk is no longer a coin. It is a movement. The cycle is mastered. The believers are rewarded.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

const styles = {
  section: {
    minHeight: '100vh',
    padding: '8rem 0',
  },
  timeline: {
    position: 'relative',
    maxWidth: '800px',
    margin: '0 auto',
    padding: '2rem 0',
  },
  lineBg: {
    position: 'absolute',
    left: '50%',
    top: 0,
    bottom: 0,
    width: '2px',
    background: 'var(--border-subtle)',
    transform: 'translateX(-50%)',
    zIndex: 1,
  },
  lineFill: {
    position: 'absolute',
    left: '50%',
    top: 0,
    width: '2px',
    background: 'linear-gradient(to bottom, var(--accent-gold), var(--accent-red))',
    transform: 'translateX(-50%)',
    zIndex: 2,
    boxShadow: '0 0 15px var(--accent-gold-glow)',
  },
  phase: {
    position: 'relative',
    width: 'calc(50% - 3rem)',
    marginBottom: '4rem',
    zIndex: 3,
  },
  leftPhase: {
    marginRight: 'auto',
    textAlign: 'right',
  },
  rightPhase: {
    marginLeft: 'auto',
    textAlign: 'left',
  },
  phaseNode: {
    position: 'absolute',
    top: '20px',
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: '#0a0a0f',
    border: '2px solid var(--accent-gold)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontWeight: 'bold',
    fontFamily: 'var(--font-heading)',
    color: 'var(--accent-gold)',
    boxShadow: '0 0 15px var(--accent-gold-glow)',
    zIndex: 4,
  }
};

export default Roadmap;
