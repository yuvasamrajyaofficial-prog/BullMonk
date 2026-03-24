import React, { useState, useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Import newly generated images
import bookImg1 from '../assets/neeti_book1.png';
import bookImg2 from '../assets/neeti_book2.png';
import bookImg3 from '../assets/neeti_book3.png';
import bookImg4 from '../assets/bullmonk-hero.png';

gsap.registerPlugin(ScrollTrigger);

const NeetiBook = () => {
  const [currentPage, setCurrentPage] = useState(0);
  const sectionRef = useRef(null);
  const contentRef = useRef(null);

  const chapters = [
    {
      title: "Book I: The Awakening",
      subtitle: "Understanding the Cycle",
      image: bookImg1,
      philosophy: "Why the masses buy at the top. The psychology of euphoria and the trap of the 'infinite pump.' Before one can conquer the market, one must realize they are trapped in its illusion.",
      economics: "The mechanics of exit liquidity. How whales use retail euphoria to distribute assets. Understanding Accumulation, Markup, Distribution, and Markdown phases."
    },
    {
      title: "Book II: Internal Mastery",
      subtitle: "The Discipline of the Monk",
      image: bookImg2,
      philosophy: "The noise of the crowd leads to madness. Truth is found in silence. To own everything, you must be willing to lose everything without losing your mind.",
      economics: "Ignoring influencers and FUD. The superiority of high time preference (Macro holding) vs low time preference (Day trading). Death by a thousand trading fees."
    },
    {
      title: "Book III: External Execution",
      subtitle: "The Strategies of the Order",
      image: bookImg3,
      philosophy: "The seed grows in the dark dirt, unseen by the world until it sprouts. The Monk does not swing his sword at the air. He waits for the perfect strike.",
      economics: "Dollar Cost Averaging (DCA) during the bear market. Buying when blood is in the streets. Letting trades come to you. Identifying deep value and macro bottoms."
    },
    {
      title: "Book IV: The Kingdom of the Awakened",
      subtitle: "The BullMonk Society",
      image: bookImg4,
      philosophy: "Individual wealth is fleeting. A collective order shifts the paradigm. The cycle will end, and it will begin again. The Monk is never surprised.",
      economics: "How conviction filters out short speculators. Achieving escape velocity from active labor. Preparing deployment capital for the inevitable crash to generate generational wealth."
    }
  ];

  const handleNext = () => {
    if (currentPage < chapters.length - 1) {
      animateTransition(() => setCurrentPage(currentPage + 1));
    }
  };

  const handlePrev = () => {
    if (currentPage > 0) {
      animateTransition(() => setCurrentPage(currentPage - 1));
    }
  };

  const animateTransition = (callback) => {
    gsap.to(contentRef.current, {
      opacity: 0,
      y: 20,
      duration: 0.3,
      onComplete: () => {
        callback();
        gsap.to(contentRef.current, { opacity: 1, y: 0, duration: 0.4, delay: 0.1 });
      }
    });
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        sectionRef.current,
        { opacity: 0, scale: 0.95 },
        {
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 75%",
            end: "bottom 60%",
            toggleActions: "play none none reverse"
          },
          opacity: 1,
          scale: 1,
          duration: 1,
          ease: "power2.out"
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} id="neeti" className="section" style={styles.section}>
      <div className="container">
        <div className="text-center mb-4">
          <h2 className="heading-lg mb-1">
            BullMonk <span className="text-gradient-gold">Neeti</span>
          </h2>
          <p className="text-secondary" style={{ fontSize: '1.2rem', textTransform: 'uppercase', letterSpacing: '2px' }}>
            The Monk's Wisdom on Wealth & Markets
          </p>
        </div>

        <div className="glass-card" style={styles.bookContainer}>
          <div ref={contentRef} className="grid grid-2" style={styles.bookContent}>
            
            {/* Left Side: Image */}
            <div style={styles.imageSide}>
              <div style={styles.imageWrapper}>
                <img 
                  src={chapters[currentPage].image} 
                  alt={chapters[currentPage].title} 
                  style={styles.image} 
                />
                <div style={styles.imageOverlay}></div>
              </div>
            </div>

            {/* Right Side: Text & Controls */}
            <div style={styles.textSide} className="flex-column">
              <div style={{ flex: 1 }}>
                <div style={styles.chapterBadge}>Chapter {currentPage + 1} of {chapters.length}</div>
                <h3 className="heading-md text-gold mt-1 mb-1">{chapters[currentPage].title}</h3>
                <h4 className="mb-3 text-secondary" style={{ fontStyle: 'italic', fontSize: '1.1rem' }}>
                  "{chapters[currentPage].subtitle}"
                </h4>
                
                <div className="mb-3">
                  <strong className="text-gradient-red" style={{ display: 'block', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Philosophy</strong>
                  <p className="text-primary" style={{ lineHeight: '1.8' }}>
                    {chapters[currentPage].philosophy}
                  </p>
                </div>
                
                <div>
                  <strong className="text-gradient-green" style={{ display: 'block', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Economics</strong>
                  <p className="text-secondary" style={{ lineHeight: '1.8' }}>
                    {chapters[currentPage].economics}
                  </p>
                </div>
              </div>

              {/* Pagination Controls */}
              <div className="flex-between mt-4" style={styles.controls}>
                <button 
                  className="btn btn-outline" 
                  onClick={handlePrev} 
                  disabled={currentPage === 0}
                  style={{ ...styles.pageBtn, opacity: currentPage === 0 ? 0.3 : 1, cursor: currentPage === 0 ? 'not-allowed' : 'pointer' }}
                >
                  &larr; Previous Page
                </button>
                <div className="text-muted" style={{ fontFamily: 'var(--font-heading)' }}>
                  {currentPage + 1} / {chapters.length}
                </div>
                <button 
                  className="btn btn-outline" 
                  onClick={handleNext} 
                  disabled={currentPage === chapters.length - 1}
                  style={{ ...styles.pageBtn, opacity: currentPage === chapters.length - 1 ? 0.3 : 1, cursor: currentPage === chapters.length - 1 ? 'not-allowed' : 'pointer' }}
                >
                  Next Page &rarr;
                </button>
              </div>
            </div>
            
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
    background: 'radial-gradient(circle at top, rgba(20, 15, 5, 0.4) 0%, transparent 70%)',
  },
  bookContainer: {
    padding: '0', 
    overflow: 'hidden',
    border: '1px solid rgba(245, 166, 35, 0.2)',
    boxShadow: '0 20px 50px rgba(0,0,0,0.5), 0 0 20px var(--accent-gold-glow) inset',
  },
  bookContent: {
    gap: 0, // removed gap for full width image
    minHeight: '500px',
  },
  imageSide: {
    padding: 0,
    background: '#050508',
  },
  imageWrapper: {
    position: 'relative',
    width: '100%',
    height: '100%',
    minHeight: '300px',
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    transition: 'transform 0.5s ease',
  },
  imageOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'linear-gradient(to right, transparent, rgba(10, 10, 15, 0.9) 100%)',
  },
  textSide: {
    padding: '3rem',
    background: 'rgba(10, 10, 15, 0.9)',
    justifyContent: 'space-between',
  },
  chapterBadge: {
    display: 'inline-block',
    padding: '0.3rem 0.8rem',
    background: 'rgba(245, 166, 35, 0.1)',
    border: '1px solid var(--accent-gold)',
    color: 'var(--accent-gold)',
    borderRadius: '20px',
    fontSize: '0.8rem',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    fontFamily: 'var(--font-heading)',
  },
  controls: {
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    paddingTop: '1.5rem',
  },
  pageBtn: {
    padding: '0.5rem 1rem',
    fontSize: '0.9rem',
    textTransform: 'none',
  }
};

// Add responsive adjustments dynamically
if (typeof window !== 'undefined') {
  const isMobile = window.innerWidth < 768;
  if(isMobile) {
      styles.imageOverlay.background = 'linear-gradient(to bottom, transparent, rgba(10, 10, 15, 1) 100%)';
      styles.textSide.padding = '1.5rem';
  }
}

export default NeetiBook;
