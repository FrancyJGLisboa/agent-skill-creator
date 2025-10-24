"""
Stock Analyzer Skill - Main Orchestrator

This is a simplified reference implementation demonstrating the structure
of a skill with robust 3-layer activation. For a production version,
integrate with actual data sources and indicator libraries.

Example Usage:
    analyzer = StockAnalyzer()
    result = analyzer.analyze("AAPL", ["RSI", "MACD"])
    print(result)
"""

from typing import List, Dict, Optional, Any
from datetime import datetime


class StockAnalyzer:
    """
    Main orchestrator for technical stock analysis

    Capabilities:
    - Technical indicator calculation (RSI, MACD, Bollinger)
    - Buy/sell signal generation
    - Multi-stock comparison
    - Price monitoring and alerts
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize stock analyzer with optional configuration

        Args:
            config: Optional configuration dict with indicator parameters
        """
        self.config = config or self._default_config()
        print(f"[StockAnalyzer] Initialized with config: {self.config['data_source']}")

    def analyze(
        self,
        ticker: str,
        indicators: Optional[List[str]] = None,
        period: str = "1y"
    ) -> Dict[str, Any]:
        """
        Perform technical analysis on a stock

        Args:
            ticker: Stock symbol (e.g., "AAPL", "MSFT")
            indicators: List of indicators to calculate (default: ["RSI", "MACD"])
            period: Time period for analysis (default: "1y")

        Returns:
            Dict containing:
                - ticker: Stock symbol
                - current_price: Latest price
                - indicators: Dict of indicator results
                - signal: Buy/sell/hold recommendation
                - timestamp: Analysis timestamp

        Example:
            >>> analyzer = StockAnalyzer()
            >>> result = analyzer.analyze("AAPL", ["RSI", "MACD"])
            >>> print(result['signal']['action'])
            BUY
        """
        indicators = indicators or ["RSI", "MACD"]

        print(f"\n[StockAnalyzer] Analyzing {ticker}...")
        print(f"  - Indicators: {indicators}")
        print(f"  - Period: {period}")

        # Step 1: Fetch price data (simplified - production would use yfinance)
        price_data = self._fetch_data(ticker, period)

        # Step 2: Calculate indicators
        indicator_results = {}
        for indicator_name in indicators:
            indicator_results[indicator_name] = self._calculate_indicator(
                indicator_name,
                price_data
            )

        # Step 3: Generate trading signal
        signal = self._generate_signal(ticker, price_data, indicator_results)

        # Step 4: Compile results
        result = {
            'ticker': ticker.upper(),
            'current_price': price_data['close'],
            'indicators': indicator_results,
            'signal': signal,
            'timestamp': datetime.now().isoformat(),
            'period': period
        }

        print(f"[StockAnalyzer] Analysis complete for {ticker}")
        print(f"  → Signal: {signal['action']} (confidence: {signal['confidence']})")

        return result

    def compare(
        self,
        tickers: List[str],
        rank_by: str = "momentum",
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple stocks and rank by technical strength

        Args:
            tickers: List of stock symbols
            rank_by: Ranking method ("momentum", "rsi", "composite")
            indicators: Indicators to use for comparison

        Returns:
            Dict containing ranked stocks with scores and analysis

        Example:
            >>> analyzer = StockAnalyzer()
            >>> result = analyzer.compare(["AAPL", "MSFT", "GOOGL"])
            >>> for stock in result['ranked_stocks']:
            >>>     print(f"{stock['ticker']}: {stock['score']}")
        """
        indicators = indicators or ["RSI", "MACD"]

        print(f"\n[StockAnalyzer] Comparing {len(tickers)} stocks...")
        print(f"  - Tickers: {', '.join(tickers)}")
        print(f"  - Rank by: {rank_by}")

        comparisons = []
        for ticker in tickers:
            # Analyze each stock
            analysis = self.analyze(ticker, indicators, period="6mo")

            # Calculate ranking score
            score = self._calculate_ranking_score(analysis, rank_by)

            comparisons.append({
                'ticker': ticker.upper(),
                'analysis': analysis,
                'score': score,
                'rank': 0  # Will be set after sorting
            })

        # Sort by score (highest first)
        comparisons.sort(key=lambda x: x['score'], reverse=True)

        # Assign ranks
        for idx, comparison in enumerate(comparisons, 1):
            comparison['rank'] = idx

        result = {
            'ranked_stocks': comparisons,
            'ranking_method': rank_by,
            'total_analyzed': len(tickers),
            'timestamp': datetime.now().isoformat()
        }

        print(f"[StockAnalyzer] Comparison complete")
        print("  Rankings:")
        for comp in comparisons:
            print(f"    #{comp['rank']}: {comp['ticker']} (score: {comp['score']:.2f})")

        return result

    def monitor(
        self,
        ticker: str,
        condition: str,
        action: str = "notify"
    ) -> Dict[str, Any]:
        """
        Set up monitoring and alerts for a stock

        Args:
            ticker: Stock symbol to monitor
            condition: Alert condition (e.g., "RSI < 30", "MACD crossover")
            action: Action to take when condition met (default: "notify")

        Returns:
            Dict with monitoring configuration

        Example:
            >>> analyzer = StockAnalyzer()
            >>> alert = analyzer.monitor("AAPL", "RSI < 30", "notify")
            >>> print(alert['status'])
            active
        """
        print(f"\n[StockAnalyzer] Setting up monitoring...")
        print(f"  - Ticker: {ticker}")
        print(f"  - Condition: {condition}")
        print(f"  - Action: {action}")

        return {
            'ticker': ticker.upper(),
            'condition': condition,
            'action': action,
            'status': 'active',
            'created': datetime.now().isoformat()
        }

    # Private helper methods

    def _default_config(self) -> Dict:
        """Default configuration for indicators and data sources"""
        return {
            'data_source': 'yahoo_finance',
            'indicators': {
                'RSI': {
                    'period': 14,
                    'overbought': 70,
                    'oversold': 30
                },
                'MACD': {
                    'fast_period': 12,
                    'slow_period': 26,
                    'signal_period': 9
                },
                'Bollinger': {
                    'period': 20,
                    'std_dev': 2
                }
            },
            'signals': {
                'confidence_threshold': 0.7
            }
        }

    def _fetch_data(self, ticker: str, period: str) -> Dict[str, float]:
        """
        Fetch price data for ticker (simplified mock)
        Production version would use yfinance or similar
        """
        # Mock data - production would fetch real data
        return {
            'open': 175.20,
            'high': 178.90,
            'low': 174.50,
            'close': 178.45,
            'volume': 52_000_000
        }

    def _calculate_indicator(
        self,
        indicator_name: str,
        price_data: Dict
    ) -> Dict[str, Any]:
        """
        Calculate technical indicator (simplified mock)
        Production version would use ta-lib or pandas-ta
        """
        if indicator_name == "RSI":
            return {
                'value': 62.3,
                'signal': 'neutral',
                'interpretation': 'RSI above 50 indicates bullish momentum, but not overbought'
            }
        elif indicator_name == "MACD":
            return {
                'macd_line': 2.15,
                'signal_line': 1.89,
                'histogram': 0.26,
                'signal': 'buy',
                'interpretation': 'MACD line crossed above signal line - bullish crossover'
            }
        elif indicator_name == "Bollinger":
            return {
                'upper_band': 185.20,
                'middle_band': 178.45,
                'lower_band': 171.70,
                'position': 'middle',
                'interpretation': 'Price near middle band - neutral volatility'
            }
        else:
            return {'error': f'Unknown indicator: {indicator_name}'}

    def _generate_signal(
        self,
        ticker: str,
        price_data: Dict,
        indicators: Dict
    ) -> Dict[str, Any]:
        """
        Generate trading signal from indicator combination

        Strategy: Combined RSI + MACD approach
        - BUY: RSI healthy and MACD bullish crossover
        - SELL: RSI overbought and MACD bearish
        - HOLD: Otherwise
        """
        rsi = indicators.get('RSI', {}).get('value', 50)
        macd_signal = indicators.get('MACD', {}).get('signal', 'neutral')

        reasoning = []

        # RSI analysis
        if rsi < 30:
            reasoning.append("RSI oversold (< 30) - potential buy opportunity")
            base_signal = "BUY"
            confidence = "moderate"
        elif rsi > 70:
            reasoning.append("RSI overbought (> 70) - potential sell signal")
            base_signal = "SELL"
            confidence = "moderate"
        else:
            reasoning.append(f"RSI at {rsi:.1f} - neutral zone")
            base_signal = "HOLD"
            confidence = "low"

        # MACD analysis
        if macd_signal == "buy":
            reasoning.append("MACD bullish crossover detected")
            if base_signal == "BUY":
                confidence = "high"
            else:
                base_signal = "BUY"
                confidence = "moderate"

        return {
            'action': base_signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'price': price_data['close']
        }

    def _calculate_ranking_score(
        self,
        analysis: Dict,
        method: str
    ) -> float:
        """
        Calculate ranking score based on method

        Args:
            analysis: Stock analysis results
            method: Ranking method (momentum, rsi, composite)

        Returns:
            Numeric score (higher is better)
        """
        if method == "rsi":
            # Higher RSI = higher score (up to 70)
            rsi = analysis['indicators'].get('RSI', {}).get('value', 50)
            return min(rsi, 70)

        elif method == "momentum":
            # Composite momentum score
            rsi = analysis['indicators'].get('RSI', {}).get('value', 50)
            macd_signal = analysis['indicators'].get('MACD', {}).get('signal', 'neutral')

            score = rsi
            if macd_signal == "buy":
                score += 10
            elif macd_signal == "sell":
                score -= 10

            return score

        else:  # composite
            # Weighted combination of indicators
            rsi = analysis['indicators'].get('RSI', {}).get('value', 50)
            macd_hist = analysis['indicators'].get('MACD', {}).get('histogram', 0)

            return (rsi * 0.6) + (macd_hist * 20 * 0.4)


def main():
    """Demo usage of StockAnalyzer skill"""
    print("=" * 60)
    print("Stock Analyzer Skill - Demo")
    print("=" * 60)

    analyzer = StockAnalyzer()

    # Example 1: Single stock analysis
    print("\n--- Example 1: Analyze AAPL ---")
    result = analyzer.analyze("AAPL", ["RSI", "MACD"])
    print(f"\nResult: {result['signal']['action']}")
    print(f"Reasoning: {', '.join(result['signal']['reasoning'])}")

    # Example 2: Multi-stock comparison
    print("\n\n--- Example 2: Compare Tech Stocks ---")
    comparison = analyzer.compare(["AAPL", "MSFT", "GOOGL"], rank_by="momentum")

    # Example 3: Set up monitoring
    print("\n\n--- Example 3: Monitor Stock ---")
    alert = analyzer.monitor("TSLA", "RSI < 30", "notify")
    print(f"\nMonitoring status: {alert['status']}")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
