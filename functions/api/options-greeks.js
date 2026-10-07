function erf(x) {
  // Approximation of erf with max error 1.5e-7
  const sign = x >= 0 ? 1 : -1;
  x = Math.abs(x);
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;

  const t = 1.0 / (1.0 + p * x);
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
  return sign * y;
}

function normCdf(x) {
  return 0.5 * (1.0 + erf(x / Math.sqrt(2.0)));
}

function normPdf(x) {
  return (1.0 / Math.sqrt(2.0 * Math.PI)) * Math.exp(-0.5 * x * x);
}

export function calcBlackScholes(spot, strike, tteYears, vol, r = 0.065, optionType = 'call') {
  const isCall = optionType.toLowerCase() === 'call' || optionType.toLowerCase() === 'ce';
  
  if (tteYears <= 0) {
    const intrinsic = isCall ? Math.max(0, spot - strike) : Math.max(0, strike - spot);
    const delta = isCall ? (spot > strike ? 1.0 : (spot === strike ? 0.5 : 0.0)) : (spot < strike ? -1.0 : (spot === strike ? -0.5 : 0.0));
    return {
      price: intrinsic,
      delta: delta,
      gamma: 0,
      theta_daily: 0,
      theta_annual: 0,
      vega_1pct: 0,
      vega_annual: 0
    };
  }

  const sqrtT = Math.sqrt(tteYears);
  const volSqrtT = vol * sqrtT;
  const d1 = (Math.log(spot / strike) + (r + 0.5 * vol * vol) * tteYears) / volSqrtT;
  const d2 = d1 - volSqrtT;

  const cdfD1 = normCdf(d1);
  const cdfD2 = normCdf(d2);
  const pdfD1 = normPdf(d1);
  const discount = Math.exp(-r * tteYears);

  const gamma = pdfD1 / (spot * volSqrtT);
  const vegaAnnual = spot * pdfD1 * sqrtT;
  const vega1pct = vegaAnnual / 100.0;

  let price, delta, thetaAnnual;
  if (isCall) {
    price = spot * cdfD1 - strike * discount * cdfD2;
    delta = cdfD1;
    thetaAnnual = -(spot * pdfD1 * vol) / (2.0 * sqrtT) - r * strike * discount * cdfD2;
  } else {
    const cdfNegD1 = normCdf(-d1);
    const cdfNegD2 = normCdf(-d2);
    price = strike * discount * cdfNegD2 - spot * cdfNegD1;
    delta = cdfD1 - 1.0;
    thetaAnnual = -(spot * pdfD1 * vol) / (2.0 * sqrtT) + r * strike * discount * cdfNegD2;
  }

  const thetaDaily = thetaAnnual / 365.0;

  return {
    price: Math.max(0, price),
    delta: delta,
    gamma: gamma,
    theta_daily: thetaDaily,
    theta_annual: thetaAnnual,
    vega_1pct: vega1pct,
    vega_annual: vegaAnnual
  };
}

export async function onRequestPost({ request }) {
  try {
    const body = await request.json();
    const { spot, strike, time_to_expiry_years, volatility, risk_free_rate = 0.065, option_type = "call" } = body;

    if (!spot || !strike || !volatility || !time_to_expiry_years) {
      return new Response(JSON.stringify({ error: "Missing required fields" }), { status: 400 });
    }

    const greeks = calcBlackScholes(
      parseFloat(spot),
      parseFloat(strike),
      parseFloat(time_to_expiry_years),
      parseFloat(volatility),
      parseFloat(risk_free_rate),
      option_type
    );

    return new Response(JSON.stringify({
      spot,
      strike,
      option_type,
      price: Math.round(greeks.price * 100) / 100,
      delta: Math.round(greeks.delta * 10000) / 10000,
      gamma: Math.round(greeks.gamma * 1000000) / 1000000,
      theta_daily: Math.round(greeks.theta_daily * 100) / 100,
      theta_annual: Math.round(greeks.theta_annual * 100) / 100,
      vega_1pct: Math.round(greeks.vega_1pct * 100) / 100,
      disclaimer: "Historical/theoretical option pricing is not a substitute for live executable option quotes."
    }), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 400 });
  }
}
