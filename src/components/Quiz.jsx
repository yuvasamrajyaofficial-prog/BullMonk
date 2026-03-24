import React, { useState } from 'react';

const Quiz = () => {
  const [step, setStep] = useState(0);
  const [score, setScore] = useState(0);

  const questions = [
    {
      q: "The market crashes 30% in one day. What do you do?",
      options: [
        { text: "Sell everything before it goes to 0", value: 0 },
        { text: "Close the chart, touch grass, buy more", value: 1 }
      ]
    },
    {
      q: "Your favorite influencer says a coin is 'dead'. What's your move?",
      options: [
        { text: "Panic swap to the new shiny dog coin", value: 0 },
        { text: "Ignore the noise. Maintain conviction.", value: 1 }
      ]
    },
    {
      q: "What is your timeframe for success?",
      options: [
        { text: "By next Tuesday", value: 0 },
        { text: "However long the cycle takes", value: 1 }
      ]
    }
  ];

  const handleAnswer = (value) => {
    setScore(score + value);
    setStep(step + 1);
  };

  const getResult = () => {
    if (score === 3) return {
      title: "Awakened BullMonk",
      desc: "Your hands are forged in diamond. You feel no fear. Welcome to the Order.",
      color: "var(--accent-gold)"
    };
    if (score === 2) return {
      title: "Initiate",
      desc: "You are learning discipline, but the noise still affects you. Keep meditating.",
      color: "var(--accent-green)"
    };
    return {
      title: "Panic Trader",
      desc: "The market uses you as exit liquidity. Let go of your fear and join the Order.",
      color: "var(--accent-red)"
    };
  };

  const copyResult = () => {
    const res = getResult();
    const text = `I am a ${res.title}. Are you a Panic Trader or a BullMonk? Find out at bullmonk.xyz`;
    navigator.clipboard.writeText(text);
    alert("Result copied! Share it on X/Telegram.");
  };

  return (
    <section id="quiz" className="section flex-center" style={{ minHeight: '80vh' }}>
      <div className="container" style={{ maxWidth: '800px', width: '100%' }}>
        <div className="glass-card" style={styles.card}>
          {step < questions.length ? (
            <>
              <div className="text-secondary mb-2" style={{ textTransform: 'uppercase', letterSpacing: '2px', fontSize: '0.9rem' }}>
                Question {step + 1} of {questions.length}
              </div>
              <h3 className="heading-md mb-4" style={{ color: '#fff' }}>
                {questions[step].q}
              </h3>
              
              <div className="flex-column" style={{ gap: '1rem' }}>
                {questions[step].options.map((opt, i) => (
                  <button 
                    key={i} 
                    className="btn btn-outline" 
                    style={styles.optionBtn}
                    onClick={() => handleAnswer(opt.value)}
                  >
                    {opt.text}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center animate-breathe">
              <div className="text-secondary mb-2" style={{ textTransform: 'uppercase', letterSpacing: '2px' }}>
                Your Result
              </div>
              <h2 className="heading-lg mb-2" style={{ color: getResult().color, textShadow: `0 0 20px ${getResult().color}` }}>
                {getResult().title}
              </h2>
              <p className="text-secondary mb-4" style={{ fontSize: '1.2rem' }}>
                {getResult().desc}
              </p>
              
              <button className="btn btn-primary" onClick={copyResult} style={{ width: '100%' }}>
                Share Result to Join
              </button>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

const styles = {
  card: {
    padding: '4rem 3rem',
    position: 'relative',
    overflow: 'hidden',
  },
  optionBtn: {
    width: '100%',
    textAlign: 'left',
    justifyContent: 'flex-start',
    padding: '1.5rem 2rem',
    border: '1px solid rgba(255,255,255,0.1)',
    color: '#fff',
    textTransform: 'none',
    fontSize: '1.1rem',
    fontFamily: 'var(--font-body)',
  }
};

export default Quiz;
