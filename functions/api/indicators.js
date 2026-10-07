export async function onRequestGet() {
  const indicators = {
    "ADX": {
      "name": "ADX",
      "version": "1.0.0",
      "category": "trend",
      "description": "Average Directional Index with +DI and -DI",
      "parameters": { "period": 14 },
      "output_columns": ["adx_14", "plus_di_14", "minus_di_14"],
      "warmup_period": 28
    },
    "ATR": {
      "name": "ATR",
      "version": "1.0.0",
      "category": "volatility",
      "description": "Wilder's Average True Range",
      "parameters": { "period": 14 },
      "output_columns": ["atr_14"],
      "warmup_period": 14
    },
    "BOLLINGERBANDS": {
      "name": "BollingerBands",
      "version": "1.0.0",
      "category": "volatility",
      "description": "Bollinger Bands (Upper, Middle, Lower, Bandwidth, %B)",
      "parameters": { "period": 20, "std_dev": 2.0 },
      "output_columns": ["bb_upper_20_2.0", "bb_middle_20", "bb_lower_20_2.0", "bb_width_20_2.0", "bb_percent_b_20_2.0"],
      "warmup_period": 20
    },
    "CVD": {
      "name": "CVDProxy",
      "version": "1.0.0",
      "category": "volume",
      "description": "Candle-derived CVD proxy (not true tick order-flow)",
      "parameters": {},
      "output_columns": ["candle_delta", "cumulative_delta", "session_cumulative_delta"],
      "warmup_period": 1
    },
    "EMA": {
      "name": "EMA",
      "version": "1.0.0",
      "category": "trend",
      "description": "Exponential Moving Average",
      "parameters": { "period": 20 },
      "output_columns": ["ema_20"],
      "warmup_period": 20
    },
    "HMA": {
      "name": "HMA",
      "version": "1.0.0",
      "category": "trend",
      "description": "Hull Moving Average",
      "parameters": { "period": 14 },
      "output_columns": ["hma_14"],
      "warmup_period": 17
    },
    "ICHIMOKU": {
      "name": "IchimokuCloud",
      "version": "1.0.0",
      "category": "ichimoku",
      "description": "Ichimoku Kinko Hyo with causal cloud alignment",
      "parameters": { "conversion_period": 9, "base_period": 26, "leading_span_b_period": 52, "displacement": 26 },
      "output_columns": ["tenkan", "kijun", "senkou_a", "senkou_b", "chikou", "price_above_cloud", "cloud_bullish"],
      "warmup_period": 78
    },
    "MACD": {
      "name": "MACD",
      "version": "1.0.0",
      "category": "momentum",
      "description": "Moving Average Convergence Divergence",
      "parameters": { "fast_period": 12, "slow_period": 26, "signal_period": 9 },
      "output_columns": ["macd_12_26", "macd_signal_9", "macd_hist_12_26_9"],
      "warmup_period": 34
    },
    "OBV": {
      "name": "OBV",
      "version": "1.0.0",
      "category": "volume",
      "description": "On-Balance Volume",
      "parameters": {},
      "output_columns": ["obv"],
      "warmup_period": 1
    },
    "RSI": {
      "name": "RSI",
      "version": "1.0.0",
      "category": "momentum",
      "description": "Wilder's Relative Strength Index bound [0, 100]",
      "parameters": { "period": 14 },
      "output_columns": ["rsi_14"],
      "warmup_period": 15
    },
    "SMA": {
      "name": "SMA",
      "version": "1.0.0",
      "category": "trend",
      "description": "Simple Moving Average",
      "parameters": { "period": 14 },
      "output_columns": ["sma_14"],
      "warmup_period": 14
    },
    "SUPERTREND": {
      "name": "Supertrend",
      "version": "1.0.0",
      "category": "trend",
      "description": "Supertrend Trailing Band and Direction",
      "parameters": { "period": 10, "multiplier": 3.0 },
      "output_columns": ["supertrend_10_3.0", "supertrend_direction_10_3.0"],
      "warmup_period": 10
    },
    "VWAP": {
      "name": "SessionVWAP",
      "version": "1.0.0",
      "category": "volume",
      "description": "Session-aware Volume Weighted Average Price",
      "parameters": {},
      "output_columns": ["vwap"],
      "warmup_period": 1
    }
  };

  return new Response(JSON.stringify(indicators), {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "public, max-age=3600"
    }
  });
}
