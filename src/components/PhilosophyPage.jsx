import React from 'react';
import { FaArrowLeft } from 'react-icons/fa';

import originImg from '../assets/philosophy-origin.png';
import pillarsImg from '../assets/philosophy-pillars.png';
import charactersImg from '../assets/philosophy-characters.png';
import visionImg from '../assets/philosophy-vision.png';

const PhilosophyPage = ({ onBack }) => {

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-deep)',
      color: 'var(--text-primary)',
      paddingTop: '80px',
      paddingBottom: '60px'
    }}>
      {/* Sticky Header */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        zIndex: 200,
        background: 'var(--bg-card)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(245, 166, 35, 0.15)',
        padding: '14px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <button
          onClick={onBack}
          className="btn btn-outline"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 16px', fontSize: '0.85rem' }}
        >
          <FaArrowLeft /> Back to BullMonk
        </button>
        <span style={{ fontFamily: 'var(--font-heading)', color: 'var(--accent-gold)', fontSize: '1.3rem', fontWeight: 'bold' }}>
          The Philosophy
        </span>
        <div style={{ width: '120px' }}></div>
      </div>

      <div style={{ maxWidth: '960px', margin: '0 auto', padding: '0 20px' }}>

        {/* === SECTION 1: THE ORIGIN === */}
        <section style={{ marginBottom: '80px' }}>
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <p style={{ color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '3px', fontSize: '0.85rem', marginBottom: '12px' }}>Chapter I</p>
            <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: 'clamp(2rem, 5vw, 3.2rem)', marginBottom: '20px', lineHeight: 1.2 }}>
              The <span style={{ color: 'var(--accent-gold)' }}>Origin</span> of BullMonk
            </h1>
          </div>
          <div style={{ borderRadius: '16px', overflow: 'hidden', marginBottom: '30px', border: '1px solid rgba(245, 166, 35, 0.15)' }}>
            <img src={originImg} alt="BullMonk Origin" style={{ width: '100%', height: 'auto', display: 'block' }} />
          </div>
          <div style={{ lineHeight: 1.9, fontSize: '1.05rem' }}>
            <p style={{ marginBottom: '18px', color: 'var(--text-secondary)' }}>
              <strong style={{ color: 'var(--text-primary)' }}>In the ruins of the 2008 financial catastrophe</strong>, when Lehman Brothers crumbled and $10 trillion evaporated from global markets overnight, a trader stood motionless on the floor of a silent exchange. He had lost everything—his capital, his reputation, and his belief in the system he had worshipped.
            </p>
            <p style={{ marginBottom: '18px', color: 'var(--text-secondary)' }}>
              He didn't scream. He didn't blame the market-makers or the regulators. Instead, he walked away from every screen, every ticker, every notification — and <strong style={{ color: '#00d4aa' }}>vanished into silence</strong>.
            </p>
            <p style={{ marginBottom: '18px', color: 'var(--text-secondary)' }}>
              For years, he studied in isolation. Not charts—but <strong style={{ color: '#c084fc' }}>human psychology</strong>. Not candlesticks—but <strong style={{ color: '#f97316' }}>cycles of civilization</strong>. He studied the tulip traders of 1637, the railroad speculators of 1845, the dot-com dreamers of 2000. He realized they were all the same person, acting out the same script across centuries.
            </p>
            <p style={{ color: 'var(--text-primary)', fontStyle: 'italic', fontSize: '1.15rem', padding: '20px 30px', borderLeft: '3px solid var(--accent-gold)', background: 'rgba(245, 166, 35, 0.05)', borderRadius: '0 8px 8px 0' }}>
            "Markets are not numbers. They are human behavior trapped in a loop of greed and fear. The one who masters himself, masters the market."
            </p>
            <p style={{ marginTop: '18px', color: 'var(--text-secondary)' }}>
              When he returned, he was no longer a trader. He was something else entirely—<strong style={{ color: 'var(--accent-gold)' }}>half beast, half ascetic</strong>. The raw, unstoppable momentum of a Bull fused with the infinite patience and discipline of a Monk. The world would come to know him as <strong style={{ color: 'var(--accent-gold)', fontSize: '1.1rem' }}>BullMonk</strong>.
            </p>
          </div>
        </section>

        {/* === SECTION 2: THE FIVE PILLARS === */}
        <section style={{ marginBottom: '80px' }}>
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <p style={{ color: '#c084fc', textTransform: 'uppercase', letterSpacing: '3px', fontSize: '0.85rem', marginBottom: '12px' }}>Chapter II</p>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: 'clamp(1.8rem, 4vw, 2.8rem)', marginBottom: '20px' }}>
              The Five <span style={{ color: '#c084fc' }}>Pillars</span> of Market Mastery
            </h2>
          </div>
          <div style={{ borderRadius: '16px', overflow: 'hidden', marginBottom: '40px', border: '1px solid rgba(192, 132, 252, 0.2)' }}>
            <img src={pillarsImg} alt="Five Pillars" style={{ width: '100%', height: 'auto', display: 'block' }} />
          </div>

          {/* Pillar Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(270px, 1fr))', gap: '20px' }}>
            {[
              { num: 'I', title: 'Patience Over Panic', color: '#ef4444', desc: 'The Herd sells red. The Monk buys blood. 90% of trading profit comes from the 10% of time you spend waiting. Every crash in history has been followed by a recovery that rewarded only the patient.' },
              { num: 'II', title: 'Discipline Over Desire', color: '#00d4aa', desc: 'Revenge trading, over-leveraging, FOMO entries — these are the weapons the market uses against you. A BullMonk takes fewer trades, but each one is a surgical strike of conviction.' },
              { num: 'III', title: 'Knowledge Over Noise', color: '#c084fc', desc: 'Influencers pump. Media creates fear. Twitter breeds chaos. The Monk silences every source except the raw data: volume, order flow, macroeconomic cycles, and on-chain analytics.' },
              { num: 'IV', title: 'Cycles Over Predictions', color: '#f97316', desc: 'BullMonk does not predict the future. He understands that markets move in repeating psychological cycles — Accumulation, Markup, Distribution, Markdown — and positions accordingly.' },
              { num: 'V', title: 'Legacy Over Profit', color: '#3b82f6', desc: 'True wealth isn\'t a number on a screen. It is financial freedom — the ability to choose how you spend your time. BullMonk builds generational systems, not quick flips.' }
            ].map((pillar, i) => (
              <div key={i} style={{
                background: 'var(--bg-card)',
                backdropFilter: 'blur(10px)',
                border: `1px solid ${pillar.color}33`,
                borderRadius: '12px',
                padding: '28px',
                transition: 'all 0.3s ease'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px' }}>
                  <span style={{ fontFamily: 'var(--font-heading)', fontSize: '1.8rem', color: pillar.color, fontWeight: 'bold' }}>{pillar.num}</span>
                  <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', color: pillar.color }}>{pillar.title}</h3>
                </div>
                <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, fontSize: '0.95rem' }}>{pillar.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* === SECTION 3: THE CHARACTERS === */}
        <section style={{ marginBottom: '80px' }}>
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <p style={{ color: '#00d4aa', textTransform: 'uppercase', letterSpacing: '3px', fontSize: '0.85rem', marginBottom: '12px' }}>Chapter III</p>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: 'clamp(1.8rem, 4vw, 2.8rem)', marginBottom: '20px' }}>
              The <span style={{ color: '#00d4aa' }}>Characters</span> of The Order
            </h2>
          </div>
          <div style={{ borderRadius: '16px', overflow: 'hidden', marginBottom: '40px', border: '1px solid rgba(0, 212, 170, 0.2)' }}>
            <img src={charactersImg} alt="The Characters" style={{ width: '100%', height: 'auto', display: 'block' }} />
          </div>

          {/* Character Profiles */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {[
              { name: '🧘 BullMonk', role: 'The Awakened Trader', color: 'var(--accent-gold)', bio: 'Ageless. Emotionless under pressure. Sees patterns across decades. Lost everything in the 2008 collapse, disappeared into isolation, studied the psychology of civilizations, and returned as the market\'s ultimate strategist. He does not predict — he prepares.' },
              { name: '🔥 Arjun — The Rookie', role: 'Audience Proxy', color: '#ef4444', bio: 'A 22-year-old Indian college dropout who threw his savings into crypto during a bull run. Emotional, impulsive, but fundamentally intelligent. He represents every new trader who must learn through mistakes. Under BullMonk\'s guidance, he transforms from a gambler into a disciplined operator.' },
              { name: '💰 Victor — The Whale', role: 'Institutional Power', color: '#3b82f6', bio: 'A 55-year-old former Goldman Sachs managing director. Cold, calculating, speaks only in data and probabilities. He moves markets silently. Initially antagonistic, he eventually recognizes BullMonk\'s wisdom and becomes a reluctant ally.' },
              { name: '🧠 Dr. Meera Sharma — The Economist', role: 'The Brain', color: '#c084fc', bio: 'A 38-year-old ex-RBI advisor. Data-driven, sharp, skeptical of BullMonk\'s philosophy at first. She represents the academic, numbers-first approach to markets. Her transformation comes when she realizes that data alone cannot explain human irrationality.' },
              { name: '⚡ Kira — The Manipulator', role: 'The Shadow', color: '#f97316', bio: 'A 30-year-old anonymous dark-web market operator. BullMonk\'s former student who chose the dark path. She orchestrates pump-and-dump schemes, insider trades, and represents everything the market participants should fear. The cautionary tale made human.' }
            ].map((char, i) => (
              <div key={i} style={{
                background: 'var(--bg-card)',
                backdropFilter: 'blur(10px)',
                border: `1px solid ${char.color}33`,
                borderRadius: '14px',
                padding: '28px 32px',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
                  <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', color: char.color, margin: 0 }}>{char.name}</h3>
                  <span style={{ background: `${char.color}22`, color: char.color, padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 'bold' }}>{char.role}</span>
                </div>
                <p style={{ color: 'var(--text-secondary)', lineHeight: 1.8, fontSize: '0.95rem', margin: 0 }}>{char.bio}</p>
              </div>
            ))}
          </div>
        </section>

        {/* === SECTION 4: THE VISION === */}
        <section style={{ marginBottom: '40px' }}>
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <p style={{ color: '#f97316', textTransform: 'uppercase', letterSpacing: '3px', fontSize: '0.85rem', marginBottom: '12px' }}>Chapter IV</p>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: 'clamp(1.8rem, 4vw, 2.8rem)', marginBottom: '20px' }}>
              The <span style={{ color: '#f97316' }}>Vision</span> — Market Ascension
            </h2>
          </div>
          <div style={{ borderRadius: '16px', overflow: 'hidden', marginBottom: '40px', border: '1px solid rgba(249, 115, 22, 0.2)' }}>
            <img src={visionImg} alt="The Vision" style={{ width: '100%', height: 'auto', display: 'block' }} />
          </div>
          <div style={{ lineHeight: 1.9, fontSize: '1.05rem' }}>
            <p style={{ marginBottom: '18px', color: 'var(--text-secondary)' }}>
              <strong style={{ color: 'var(--text-primary)' }}>BullMonk is not a meme coin.</strong> It is a <strong style={{ color: '#f97316' }}>content universe</strong>, a <strong style={{ color: '#c084fc' }}>financial education movement</strong>, and a <strong style={{ color: '#00d4aa' }}>global community</strong> united by a single belief:
            </p>
            <p style={{ color: 'var(--text-primary)', fontStyle: 'italic', fontSize: '1.2rem', padding: '24px 30px', textAlign: 'center', borderLeft: 'none', background: 'rgba(249, 115, 22, 0.05)', borderRadius: '12px', border: '1px solid rgba(249, 115, 22, 0.15)' }}>
              "The market is not your enemy. Your emotions are."
            </p>

            <h3 style={{ fontFamily: 'var(--font-heading)', color: '#ef4444', marginTop: '40px', marginBottom: '16px', fontSize: '1.3rem' }}>Season Structure</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '30px' }}>
              {[
                { s: 'Season 1', title: 'Origin of Markets', years: '1600s–1929', color: 'var(--accent-gold)', desc: 'Barter to Wall Street. Tulip Mania to the Great Depression. The birth of greed.' },
                { s: 'Season 2', title: 'Chaos & Learning', years: '1971–2008', color: '#ef4444', desc: 'Dot-com. Subprime. The crisis that broke BullMonk — and made him disappear.' },
                { s: 'Season 3', title: 'Transformation', years: 'Timeless', color: '#c084fc', desc: 'Psychology. Wyckoff. Discipline. Emotional mastery. The silent rebirth.' },
                { s: 'Season 4', title: 'Return of BullMonk', years: '2009–2021', color: '#00d4aa', desc: 'Bitcoin. DeFi. Meme Wars. BullMonk returns to guide the next generation.' },
                { s: 'Season 5', title: 'The Modern War', years: '2022–Now', color: '#f97316', desc: 'AI revolution. Inflation wars. India Rising. The Order is built.' }
              ].map((season, i) => (
                <div key={i} style={{
                  background: 'var(--bg-card)',
                  borderRadius: '10px',
                  padding: '20px',
                  border: `1px solid ${season.color}33`
                }}>
                  <span style={{ color: season.color, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '2px', fontWeight: 'bold' }}>{season.s} · {season.years}</span>
                  <h4 style={{ fontFamily: 'var(--font-heading)', color: season.color, margin: '8px 0', fontSize: '1.05rem' }}>{season.title}</h4>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6, margin: 0 }}>{season.desc}</p>
                </div>
              ))}
            </div>

            <h3 style={{ fontFamily: 'var(--font-heading)', color: '#3b82f6', marginTop: '40px', marginBottom: '16px', fontSize: '1.3rem' }}>Our Agenda</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {[
                { icon: '📺', title: 'Content Empire', desc: 'Daily educational content across YouTube, Instagram, X, and Telegram. Real history. Real psychology. No fake gurus.' },
                { icon: '🧠', title: 'Financial Literacy', desc: 'Teaching the world how markets actually work — from candlestick basics to institutional order-flow — through the BullMonk story universe.' },
                { icon: '🌍', title: 'Global Community', desc: 'Building "The Order" — a worldwide collective of disciplined traders and investors who think in decades, not minutes.' },
                { icon: '🪙', title: 'Token Ecosystem', desc: 'The $BULLMONK token powers access to exclusive content, governance of The Order, and participation in the community\'s future.' }
              ].map((item, i) => (
                <div key={i} style={{
                  background: 'var(--bg-card)',
                  borderRadius: '10px',
                  padding: '24px',
                  border: '1px solid rgba(59, 130, 246, 0.15)'
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '12px' }}>{item.icon}</div>
                  <h4 style={{ fontFamily: 'var(--font-heading)', color: '#3b82f6', marginBottom: '8px' }}>{item.title}</h4>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.7, margin: 0 }}>{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer Quote */}
        <div style={{ textAlign: 'center', padding: '40px 20px', borderTop: '1px solid rgba(245, 166, 35, 0.1)' }}>
          <p style={{ fontFamily: 'var(--font-heading)', color: 'var(--accent-gold)', fontSize: 'clamp(1rem, 3vw, 1.4rem)', fontStyle: 'italic', maxWidth: '700px', margin: '0 auto', lineHeight: 1.6 }}>
            "Every empire starts with a single story told to one person who believed it. Tell it well enough, and the world will follow."
          </p>
          <p style={{ color: 'var(--text-muted)', marginTop: '12px', letterSpacing: '2px', textTransform: 'uppercase', fontSize: '0.8rem' }}>— BullMonk, Book VI: Ascension</p>
        </div>
      </div>
    </div>
  );
};

export default PhilosophyPage;
