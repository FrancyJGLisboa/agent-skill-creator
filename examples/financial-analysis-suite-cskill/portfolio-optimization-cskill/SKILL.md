---
name: portfolio-optimizer
description: Component skill for portfolio optimization using modern portfolio theory, risk metrics, efficient frontier calculation, and asset allocation strategies.
---

# Portfolio Optimizer

This component skill provides sophisticated portfolio optimization capabilities for the financial analysis suite.

## When to Use This Component Skill

Use this skill when you need to:
- Optimize asset allocation using Modern Portfolio Theory
- Calculate efficient frontier and optimal portfolios
- Perform risk assessment and stress testing
- Analyze portfolio correlation and diversification
- Generate portfolio recommendations
- Backtest portfolio performance

## Optimization Methods

### Mean-Variance Optimization
- **Markowitz Optimization**: Classical MPT approach
- **Efficient Frontier**: Calculate optimal risk-return combinations
- **Sharpe Ratio Maximization**: Find best risk-adjusted returns
- **Minimum Variance**: Lowest risk portfolio

### Advanced Optimization
- **Black-Litterman Model**: Incorporate views and equilibrium
- **Robust Optimization**: Handle estimation error
- **Factor Models**: Risk factor-based optimization
- **Regime-Based**: Different optimization for market conditions

### Constraints Support
- **Weight Constraints**: Min/max allocation limits
- **Sector Constraints**: Industry/sector allocation limits
- **Turnover Constraints**: Limit trading activity
- **Cardinality Constraints**: Limit number of assets

## Risk Metrics

### Portfolio Risk Measures
- **Volatility**: Standard deviation of returns
- **VaR**: Value at Risk (95%, 99% confidence)
- **CVaR**: Conditional Value at Risk
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Beta**: Market sensitivity

### Risk Contributions
- **Marginal VaR**: Individual asset risk contribution
- **Component VaR**: Decomposition of total risk
- **Diversification Ratio**: Benefit of diversification

## Asset Classes Supported

- **Equities**: Stocks and ETFs
- **Fixed Income**: Bonds and bond funds
- **Commodities**: Gold, oil, agricultural products
- **Real Estate**: REITs and property funds
- **Cryptocurrencies**: Digital assets
- **Cash**: Cash equivalents and money market

## Usage Examples

**Basic optimization:**
"Optimize portfolio with AAPL, MSFT, GOOG for maximum Sharpe ratio"

**Risk-focused:**
"Find minimum variance portfolio with tech stocks and bonds"

**Constraints:**
"Optimize portfolio with max 10% per stock and min 5% bonds"

**Multi-period:**
"Create quarterly rebalancing strategy for retirement portfolio"

## Scripts Available

- `scripts/optimizer.py` - Main optimization engine
- `scripts/risk_metrics.py` - Risk calculation utilities
- `scripts/efficient_frontier.py` - Efficient frontier calculation
- `scripts/backtester.py` - Portfolio performance backtesting
- `scripts/rebalancer.py` - Portfolio rebalancing strategies

## Integration

This component skill integrates with:
- **Data Acquisition**: Gets asset returns and data
- **Technical Analysis**: Uses signals for timing
- **Financial Reporting**: Provides optimization results

## Configuration

Configuration in `config/portfolio_optimization.json`:
```json
{
  "optimization": {
    "method": "sharpe_ratio",
    "risk_free_rate": 0.02,
    "frequency": "daily"
  },
  "constraints": {
    "min_weight": 0.01,
    "max_weight": 0.30,
    "max_turnover": 0.20
  },
  "risk_metrics": {
    "var_confidence": 0.95,
    "drawdown_period": 252
  }
}
```

## Output Reports

- **Optimal Weights**: Recommended asset allocation
- **Risk Metrics**: Portfolio risk characteristics
- **Efficient Frontier**: Risk-return tradeoff curve
- **Performance Attribution**: Source of returns
- **Rebalancing Schedule**: When and how to rebalance

## Stress Testing

- **Market Scenarios**: Historical crisis periods
- **Monte Carlo**: Random scenario generation
- **Factor Shocks**: Interest rate, volatility changes
- **Correlation Breakdown**: Stress test diversification

This is a **Component Skill** within the Financial Analysis Suite - specialized in portfolio optimization and risk management.