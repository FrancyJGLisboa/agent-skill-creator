---
name: technical-analysis-engine
description: Component skill for comprehensive technical analysis including indicators calculation, pattern recognition, signal generation, and trend analysis for financial markets.
---

# Technical Analysis Engine

This component skill provides comprehensive technical analysis capabilities for the financial analysis suite.

## When to Use This Component Skill

Use this skill when you need to:
- Calculate technical indicators (RSI, MACD, Bollinger Bands)
- Identify chart patterns and formations
- Generate trading signals based on technical criteria
- Analyze market trends and momentum
- Perform multi-timeframe analysis
- Backtest technical strategies

## Technical Indicators

### Trend Indicators
- **Moving Averages**: SMA, EMA, WMA with customizable periods
- **MACD**: Standard and custom configurations
- **ADX**: Trend strength measurement
- **Aroon**: Trend indicator

### Momentum Indicators
- **RSI**: Relative Strength Index with divergence detection
- **Stochastic**: Fast and slow stochastic oscillators
- **Williams %R**: Williams Percent Range
- **CCI**: Commodity Channel Index

### Volatility Indicators
- **Bollinger Bands**: Standard and custom deviations
- **ATR**: Average True Range
- **Keltner Channels**: Volatility-based channels
- **Donchian Channels**: Price channel indicators

### Volume Indicators
- **On-Balance Volume**: OBV calculations
- **Volume Profile**: Volume at price levels
- **Money Flow Index**: MFI indicator
- **Accumulation/Distribution**: A/D line

## Pattern Recognition

### Chart Patterns
- **Head and Shoulders**: Bullish and bearish formations
- **Triangles**: Ascending, descending, and symmetrical
- **Flags and Pennants**: Continuation patterns
- **Double Tops/Bottoms**: Reversal patterns

### Candlestick Patterns
- **Doji**: Indecision patterns
- **Engulfing**: Bullish and bearish engulfing
- **Hammer/Hanging Man**: Reversal patterns
- **Morning/Evening Star**: Multi-candle patterns

## Signal Generation

### Buy Signals
- RSI oversold conditions
- MACD bullish crossover
- Bollinger Band breakout
- Pattern completion confirmation

### Sell Signals
- RSI overbought conditions
- MACD bearish crossover
- Support level break
- Bearish pattern confirmation

## Usage Examples

**Basic analysis:**
"Calculate RSI, MACD, and Bollinger Bands for AAPL"

**Signal generation:**
"Generate buy/sell signals for tech stocks using RSI and MACD"

**Pattern analysis:**
"Identify head and shoulders patterns in S&P 500 stocks"

**Multi-timeframe:**
"Analyze BTC on daily and 4-hour timeframes"

## Scripts Available

- `scripts/indicators.py` - Technical indicator calculations
- `scripts/patterns.py` - Chart pattern recognition
- `scripts/signals.py` - Trading signal generation
- `scripts/backtest.py` - Strategy backtesting
- `scripts/multi_timeframe.py` - Multi-timeframe analysis

## Integration

This component skill integrates with:
- **Data Acquisition**: Receives cleaned market data
- **Portfolio Optimizer**: Provides signals for allocation
- **Financial Reporting**: Supplies analysis for reports

## Configuration

Configuration in `config/technical_analysis.json`:
```json
{
  "indicators": {
    "rsi": {
      "period": 14,
      "overbought": 70,
      "oversold": 30
    },
    "macd": {
      "fast": 12,
      "slow": 26,
      "signal": 9
    }
  },
  "signals": {
    "min_confidence": 0.7,
    "confirmation_required": true
  }
}
```

## Output Formats

- JSON with indicator values and signals
- CSV with time series data
- Charts and visualizations
- Alert notifications

This is a **Component Skill** within the Financial Analysis Suite - specialized in technical analysis and signal generation.