import { calcBlackScholes } from './options-greeks.js';

export async function onRequestPost({ request }) {
  try {
    const body = await request.json();
    const { spot, available_strikes, time_to_expiry_years, volatility, target_delta, option_type = "call", risk_free_rate = 0.065 } = body;

    if (!spot || !available_strikes || !volatility || target_delta === undefined) {
      return new Response(JSON.stringify({ error: "Missing required fields" }), { status: 400 });
    }

    const isCall = option_type.toLowerCase() === 'call' || option_type.toLowerCase() === 'ce';
    let target = parseFloat(target_delta);
    if (!isCall && target > 0) {
      target = -target;
    }

    let bestStrike = null;
    let bestDiff = Infinity;
    let bestGreeks = null;
    const evaluated = [];

    for (const k of available_strikes) {
      const strikeVal = parseFloat(k);
      const greeks = calcBlackScholes(
        parseFloat(spot),
        strikeVal,
        parseFloat(time_to_expiry_years),
        parseFloat(volatility),
        parseFloat(risk_free_rate),
        option_type
      );

      const diff = Math.abs(greeks.delta - target);
      evaluated.push({
        strike: strikeVal,
        delta: Math.round(greeks.delta * 10000) / 10000,
        diff: Math.round(diff * 10000) / 10000,
        price: Math.round(greeks.price * 100) / 100,
        gamma: Math.round(greeks.gamma * 1000000) / 1000000,
        theta: Math.round(greeks.theta_daily * 100) / 100,
        vega: Math.round(greeks.vega_1pct * 100) / 100
      });

      if (diff < bestDiff) {
        bestDiff = diff;
        bestStrike = strikeVal;
        bestGreeks = greeks;
      }
    }

    return new Response(JSON.stringify({
      selected_strike: bestStrike,
      target_delta: target,
      actual_delta: Math.round(bestGreeks.delta * 10000) / 10000,
      delta_error: Math.round(bestDiff * 10000) / 10000,
      theoretical_price: Math.round(bestGreeks.price * 100) / 100,
      gamma: Math.round(bestGreeks.gamma * 1000000) / 1000000,
      theta_daily: Math.round(bestGreeks.theta_daily * 100) / 100,
      vega_1pct: Math.round(bestGreeks.vega_1pct * 100) / 100,
      all_evaluated: evaluated
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
