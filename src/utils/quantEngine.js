/**
 * BullMonk Client & Edge Quantitative Calculation Engine
 * 
 * Provides:
 * - Technical Indicators (SMA, EMA, WMA, HMA, Supertrend, ADX, RSI, Stochastic, MACD, ATR, Bollinger Bands, OBV, Session VWAP, CVD Proxy, Ichimoku Cloud)
 * - Analytical Black-Scholes European Option Pricing & Greeks
 * - Delta-Target Strike Selector
 * - Seamless fallback: queries Python Backend (http://localhost:8000) or Cloudflare Functions (/api/*) or executes locally.
 */

// Error Function erf approximation
function erf(x) {
  const sign = x >= 0 ? 1 : -1;
  const absX = Math.abs(x);
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;

  const t = 1.0 / (1.0 + p * absX);
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-absX * absX);
  return sign * y;
}

export function normCdf(x) {
  return 0.5 * (1.0 + erf(x / Math.sqrt(2.0)));
}

export function normPdf(x) {
  return (1.0 / Math.sqrt(2.0 * Math.PI)) * Math.exp(-0.5 * x * x);
}

// -----------------------------------------------------------------------------
// Black-Scholes European Option Greeks
// -----------------------------------------------------------------------------
export function calculateBlackScholes(spot, strike, tteYears, vol, r = 0.065, optionType = 'call') {
  const isCall = optionType.toLowerCase() === 'call' || optionType.toLowerCase() === 'ce';
  const s = parseFloat(spot);
  const k = parseFloat(strike);
  const t = parseFloat(tteYears);
  const sigma = parseFloat(vol);
  const rate = parseFloat(r);

  if (t <= 1e-12) {
    const intrinsic = isCall ? Math.max(0, s - k) : Math.max(0, k - s);
    const delta = isCall ? (s > k ? 1.0 : (s === k ? 0.5 : 0.0)) : (s < k ? -1.0 : (s === k ? -0.5 : 0.0));
    return {
      price: intrinsic,
      delta,
      gamma: 0,
      theta_daily: 0,
      theta_annual: 0,
      vega_1pct: 0,
      vega_annual: 0,
    };
  }

  if (sigma <= 1e-12) {
    const pvStrike = k * Math.exp(-rate * t);
    const intrinsic = isCall ? Math.max(0, s - pvStrike) : Math.max(0, pvStrike - s);
    const delta = isCall ? (s > pvStrike ? 1.0 : 0.0) : (s < pvStrike ? -1.0 : 0.0);
    return {
      price: intrinsic,
      delta,
      gamma: 0,
      theta_daily: 0,
      theta_annual: 0,
      vega_1pct: 0,
      vega_annual: 0,
    };
  }

  const sqrtT = Math.sqrt(t);
  const volSqrtT = sigma * sqrtT;
  const d1 = (Math.log(s / k) + (rate + 0.5 * sigma * sigma) * t) / volSqrtT;
  const d2 = d1 - volSqrtT;

  const cdfD1 = normCdf(d1);
  const cdfD2 = normCdf(d2);
  const pdfD1 = normPdf(d1);
  const discount = Math.exp(-rate * t);

  const gamma = pdfD1 / (s * volSqrtT);
  const vegaAnnual = s * pdfD1 * sqrtT;
  const vega1pct = vegaAnnual / 100.0;

  let price, delta, thetaAnnual;
  if (isCall) {
    price = s * cdfD1 - k * discount * cdfD2;
    delta = cdfD1;
    thetaAnnual = -(s * pdfD1 * sigma) / (2.0 * sqrtT) - rate * k * discount * cdfD2;
  } else {
    const cdfNegD1 = normCdf(-d1);
    const cdfNegD2 = normCdf(-d2);
    price = k * discount * cdfNegD2 - s * cdfNegD1;
    delta = cdfD1 - 1.0;
    thetaAnnual = -(s * pdfD1 * sigma) / (2.0 * sqrtT) + rate * k * discount * cdfNegD2;
  }

  return {
    price: Math.max(0, price),
    delta,
    gamma,
    theta_daily: thetaAnnual / 365.0,
    theta_annual: thetaAnnual,
    vega_1pct: vega1pct,
    vega_annual: vegaAnnual,
  };
}

// -----------------------------------------------------------------------------
// Delta-Target Option Selection
// -----------------------------------------------------------------------------
export function selectDeltaTargetStrike(spot, availableStrikes, tteYears, vol, targetDelta, optionType = 'call', r = 0.065) {
  const isCall = optionType.toLowerCase() === 'call' || optionType.toLowerCase() === 'ce';
  let target = parseFloat(targetDelta);
  if (!isCall && target > 0) target = -target;

  let bestStrike = null;
  let bestDiff = Infinity;
  let bestGreeks = null;
  const evaluated = [];

  for (const k of availableStrikes) {
    const strikeVal = parseFloat(k);
    const greeks = calculateBlackScholes(spot, strikeVal, tteYears, vol, r, optionType);
    const diff = Math.abs(greeks.delta - target);

    evaluated.push({
      strike: strikeVal,
      delta: greeks.delta,
      diff,
      price: greeks.price,
      gamma: greeks.gamma,
      theta: greeks.theta_daily,
      vega: greeks.vega_1pct,
    });

    if (diff < bestDiff) {
      bestDiff = diff;
      bestStrike = strikeVal;
      bestGreeks = greeks;
    }
  }

  return {
    selected_strike: bestStrike,
    target_delta: target,
    actual_delta: bestGreeks ? bestGreeks.delta : 0,
    delta_error: bestDiff,
    theoretical_price: bestGreeks ? bestGreeks.price : 0,
    greeks: bestGreeks,
    all_evaluated: evaluated,
  };
}

// -----------------------------------------------------------------------------
// Technical Indicators Vectorized Calculations
// -----------------------------------------------------------------------------
export function calculateSMA(data, period = 14, key = 'close') {
  const result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j][key];
      }
      result.push(sum / period);
    }
  }
  return result;
}

export function calculateEMA(data, period = 20, key = 'close') {
  const result = [];
  const k = 2.0 / (period + 1);
  let prevEma = null;

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else if (i === period - 1) {
      let sum = 0;
      for (let j = 0; j < period; j++) sum += data[j][key];
      prevEma = sum / period;
      result.push(prevEma);
    } else {
      const val = data[i][key];
      prevEma = val * k + prevEma * (1 - k);
      result.push(prevEma);
    }
  }
  return result;
}

export function calculateRSI(data, period = 14, key = 'close') {
  const result = [];
  if (data.length < period + 1) return data.map(() => null);

  let avgGain = 0;
  let avgLoss = 0;

  for (let i = 1; i <= period; i++) {
    const diff = data[i][key] - data[i - 1][key];
    if (diff > 0) avgGain += diff;
    else avgLoss += Math.abs(diff);
  }
  avgGain /= period;
  avgLoss /= period;

  for (let i = 0; i < period; i++) result.push(null);

  const initialRs = avgLoss === 0 ? 100 : avgGain / avgLoss;
  result.push(100 - (100 / (1 + initialRs)));

  for (let i = period + 1; i < data.length; i++) {
    const diff = data[i][key] - data[i - 1][key];
    const gain = diff > 0 ? diff : 0;
    const loss = diff < 0 ? Math.abs(diff) : 0;

    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;

    if (avgLoss === 0) {
      result.push(100);
    } else {
      const rs = avgGain / avgLoss;
      result.push(100 - (100 / (1 + rs)));
    }
  }

  return result;
}

export function calculateATR(data, period = 14) {
  const result = [];
  const tr = [];

  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      tr.push(data[0].high - data[0].low);
    } else {
      const h = data[i].high;
      const l = data[i].low;
      const prevC = data[i - 1].close;
      tr.push(Math.max(h - l, Math.abs(h - prevC), Math.abs(l - prevC)));
    }
  }

  let prevAtr = null;
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else if (i === period - 1) {
      let sum = 0;
      for (let j = 0; j < period; j++) sum += tr[j];
      prevAtr = sum / period;
      result.push(prevAtr);
    } else {
      prevAtr = (prevAtr * (period - 1) + tr[i]) / period;
      result.push(prevAtr);
    }
  }
  return result;
}

export function calculateSupertrend(data, period = 10, multiplier = 3.0) {
  const atr = calculateATR(data, period);
  const result = [];
  let prevUpper = null;
  let prevLower = null;
  let prevDir = 1;

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1 || atr[i] === null) {
      result.push({ supertrend: null, direction: 1, upper: null, lower: null });
      continue;
    }

    const hl2 = (data[i].high + data[i].low) / 2.0;
    const basicUpper = hl2 + multiplier * atr[i];
    const basicLower = hl2 - multiplier * atr[i];

    let finalUpper, finalLower;
    if (prevUpper === null) {
      finalUpper = basicUpper;
      finalLower = basicLower;
    } else {
      finalUpper = (basicUpper < prevUpper || data[i - 1].close > prevUpper) ? basicUpper : prevUpper;
      finalLower = (basicLower > prevLower || data[i - 1].close < prevLower) ? basicLower : prevLower;
    }

    let dir = prevDir;
    if (prevDir === 1) {
      dir = data[i].close < finalLower ? -1 : 1;
    } else {
      dir = data[i].close > finalUpper ? 1 : -1;
    }

    const st = dir === 1 ? finalLower : finalUpper;
    prevUpper = finalUpper;
    prevLower = finalLower;
    prevDir = dir;

    result.push({
      supertrend: st,
      direction: dir,
      upper: finalUpper,
      lower: finalLower
    });
  }

  return result;
}
