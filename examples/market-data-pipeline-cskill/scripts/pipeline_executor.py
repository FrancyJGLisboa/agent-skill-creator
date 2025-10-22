#!/usr/bin/env python3
"""
Market Data Pipeline Executor

This module implements the complete end-to-end pipeline for market data processing,
demonstrating how "expertise reutilizível" is executed as a "standard operational procedure".
"""

import pandas as pd
import numpy as np
import yfinance as yf
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAcquisitionStage:
    """Stage 1: Raw Data Acquisition from Multiple Sources"""

    def __init__(self):
        self.name = "Data Acquisition"
        self.cache = {}

    def process(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Acquire raw market data from configured sources

        Input: Configuration with tickers and data sources
        Output: Validated raw data from multiple sources
        """
        logger.info(f"🔄 Starting data acquisition for {config.get('tickers', [])}")

        tickers = config.get('tickers', [])
        period = config.get('period', '1y')
        data_sources = config.get('data_sources', ['yahoo_finance'])

        raw_data = {}

        for ticker in tickers:
            ticker_data = {}

            # Yahoo Finance data
            if 'yahoo_finance' in data_sources:
                try:
                    stock_data = yf.download(ticker, period=period)
                    if not stock_data.empty:
                        ticker_data['yahoo_finance'] = {
                            'data': stock_data.to_dict('records'),
                            'source': 'yahoo_finance',
                            'timestamp': datetime.now().isoformat(),
                            'quality_score': self._calculate_quality_score(stock_data)
                        }
                        logger.info(f"✅ Yahoo Finance data acquired for {ticker}")
                except Exception as e:
                    logger.error(f"❌ Yahoo Finance failed for {ticker}: {e}")

            # Alpha Vantage data (if API key available)
            if 'alpha_vantage' in data_sources and config.get('api_key'):
                try:
                    av_data = self._fetch_alpha_vantage(ticker, config.get('api_key'))
                    if av_data:
                        ticker_data['alpha_vantage'] = av_data
                        logger.info(f"✅ Alpha Vantage data acquired for {ticker}")
                except Exception as e:
                    logger.error(f"❌ Alpha Vantage failed for {ticker}: {e}")

            if ticker_data:
                raw_data[ticker] = ticker_data

        return {
            'raw_data': raw_data,
            'metadata': {
                'processed_tickers': list(raw_data.keys()),
                'sources_used': data_sources,
                'acquisition_time': datetime.now().isoformat(),
                'total_records': sum(len(data['data']) for ticker_data in raw_data.values() for data in ticker_data.values())
            }
        }

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate acquired data quality"""
        logger.info("🔍 Validating data quality...")

        validation_results = {}
        for ticker, ticker_data in data['raw_data'].items():
            validation_results[ticker] = {}

            for source, source_data in ticker_data.items():
                quality_score = source_data.get('quality_score', 0)
                validation_results[ticker][source] = {
                    'is_valid': quality_score > 0.7,
                    'quality_score': quality_score,
                    'record_count': len(source_data.get('data', [])),
                    'completeness': self._check_completeness(source_data.get('data', []))
                }

        data['validation'] = validation_results
        logger.info(f"✅ Data validation completed for {len(validation_results)} tickers")

        return data

    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate data quality score based on completeness and consistency"""
        if df.empty:
            return 0.0

        # Check for missing data
        missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])

        # Check for duplicate dates
        duplicate_pct = df.index.duplicated().sum() / len(df)

        # Calculate quality score (higher is better)
        quality_score = (1 - missing_pct) * (1 - duplicate_pct)

        return min(quality_score, 1.0)

    def _fetch_alpha_vantage(self, ticker: str, api_key: str) -> Dict[str, Any]:
        """Fetch data from Alpha Vantage API"""
        base_url = "https://www.alphavantage.co/query"
        function = "TIME_SERIES_DAILY"

        params = {
            'function': function,
            'symbol': ticker,
            'apikey': api_key,
            'outputsize': 'compact'
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                records = []

                for date_str, values in time_series.items():
                    record = {
                        'date': date_str,
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close']),
                        'volume': int(values['5. volume'])
                    }
                    records.append(record)

                return {
                    'data': records,
                    'source': 'alpha_vantage',
                    'timestamp': datetime.now().isoformat(),
                    'quality_score': 0.95  # Assume high quality for API data
                }

        except Exception as e:
            logger.error(f"Alpha Vantage API error: {e}")
            return None

    def _check_completeness(self, data: List[Dict]) -> float:
        """Check data completeness percentage"""
        if not data:
            return 0.0

        total_fields = len(data[0]) if data else 0
        if total_fields == 0:
            return 0.0

        complete_records = 0
        for record in data:
            if all(value is not None and value != '' for value in record.values()):
                complete_records += 1

        return complete_records / len(data)

class DataProcessingStage:
    """Stage 2: Data Processing and Enrichment"""

    def __init__(self):
        self.name = "Data Processing"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and enrich raw market data

        Input: Validated raw data from Stage 1
        Output: Processed structured data ready for analysis
        """
        logger.info("🔄 Starting data processing and enrichment...")

        processed_data = {}

        for ticker, ticker_data in data['raw_data'].items():
            # Use the best quality source for each ticker
            best_source = self._select_best_source(ticker_data)

            if best_source:
                df = self._convert_to_dataframe(ticker_data[best_source]['data'])

                # Data cleaning and processing
                df = self._clean_data(df)
                df = self._add_derived_features(df)
                df = self._normalize_data(df)

                processed_data[ticker] = {
                    'processed_data': df.to_dict('records'),
                    'source_used': best_source,
                    'processing_stats': {
                        'original_records': len(df),
                        'processed_records': len(df),
                        'features_added': len([col for col in df.columns if col.startswith('derived_')]),
                        'quality_score': self._calculate_processed_quality(df)
                    }
                }

                logger.info(f"✅ Processing completed for {ticker} using {best_source}")

        return {
            'processed_data': processed_data,
            'metadata': {
                'processed_tickers': list(processed_data.keys()),
                'processing_time': datetime.now().isoformat(),
                'total_features': self._count_total_features(processed_data)
            }
        }

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processed data quality"""
        logger.info("🔍 Validating processed data...")

        validation_results = {}
        for ticker, ticker_data in data['processed_data'].items():
            stats = ticker_data['processing_stats']
            validation_results[ticker] = {
                'is_valid': stats['quality_score'] > 0.8,
                'quality_score': stats['quality_score'],
                'feature_count': stats['features_added'],
                'data_integrity': self._check_data_integrity(ticker_data['processed_data'])
            }

        data['processed_validation'] = validation_results
        logger.info(f"✅ Processed data validation completed")

        return data

    def _select_best_source(self, ticker_data: Dict) -> str:
        """Select the best quality data source for a ticker"""
        best_source = None
        best_score = 0

        for source, source_data in ticker_data.items():
            quality_score = source_data.get('quality_score', 0)
            if quality_score > best_score:
                best_score = quality_score
                best_source = source

        return best_source

    def _convert_to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Convert raw data to pandas DataFrame"""
        df = pd.DataFrame(data)

        # Standardize column names
        column_mapping = {
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }

        df = df.rename(columns=column_mapping)

        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

        # Ensure numeric columns are properly typed
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df.sort_index()

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the data"""
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]

        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')

        # Remove outliers (basic method)
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

        return df

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for technical analysis"""
        if 'close' in df.columns:
            # Price changes
            df['derived_price_change'] = df['close'].pct_change()
            df['derived_log_return'] = np.log(df['close'] / df['close'].shift(1))

            # Moving averages
            df['derived_ma_5'] = df['close'].rolling(window=5).mean()
            df['derived_ma_20'] = df['close'].rolling(window=20).mean()
            df['derived_ma_50'] = df['close'].rolling(window=50).mean()

            # Volatility
            df['derived_volatility_20'] = df['derived_log_return'].rolling(window=20).std()

            # Price ranges
            df['derived_daily_range'] = (df['high'] - df['low']) / df['close']
            df['derived_price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])

        if 'volume' in df.columns:
            # Volume features
            df['derived_volume_ma_10'] = df['volume'].rolling(window=10).mean()
            df['derived_volume_ratio'] = df['volume'] / df['derived_volume_ma_10']

        return df

    def _normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize data for consistent processing"""
        # Normalize prices to percentage change from first day
        if 'close' in df.columns:
            first_close = df['close'].iloc[0]
            df['derived_normalized_close'] = (df['close'] / first_close - 1) * 100

        return df

    def _calculate_processed_quality(self, df: pd.DataFrame) -> float:
        """Calculate quality score for processed data"""
        if df.empty:
            return 0.0

        # Check for missing values
        missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])

        # Check data continuity (no large gaps)
        if len(df) > 1:
            date_gaps = df.index.to_series().diff().dt.days
            large_gaps = (date_gaps > 7).sum()
            continuity_score = 1 - (large_gaps / len(df))
        else:
            continuity_score = 1.0

        # Calculate overall quality
        quality_score = (1 - missing_pct) * continuity_score

        return min(quality_score, 1.0)

    def _count_total_features(self, processed_data: Dict) -> int:
        """Count total features across all processed tickers"""
        total_features = 0
        for ticker_data in processed_data.values():
            if ticker_data['processed_data']:
                total_features += len(ticker_data['processed_data'][0]) if ticker_data['processed_data'] else 0
        return total_features

    def _check_data_integrity(self, processed_data: List[Dict]) -> bool:
        """Check integrity of processed data"""
        if not processed_data:
            return False

        # Check for consistent data types
        first_record = processed_data[0]
        for record in processed_data[1:]:
            if type(record) != type(first_record):
                return False

        return True

class TechnicalAnalysisStage:
    """Stage 3: Technical Analysis and Indicator Calculation"""

    def __init__(self):
        self.name = "Technical Analysis"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform technical analysis on processed data

        Input: Processed structured data from Stage 2
        Output: Technical analysis results with indicators
        """
        logger.info("🔄 Starting technical analysis...")

        analysis_results = {}

        for ticker, ticker_data in data['processed_data'].items():
            df = pd.DataFrame(ticker_data['processed_data'])

            # Calculate technical indicators
            indicators = self._calculate_indicators(df)

            # Generate trading signals
            signals = self._generate_signals(df, indicators)

            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(df)

            analysis_results[ticker] = {
                'indicators': indicators,
                'signals': signals,
                'risk_metrics': risk_metrics,
                'analysis_summary': self._create_analysis_summary(indicators, signals, risk_metrics)
            }

            logger.info(f"✅ Technical analysis completed for {ticker}")

        return {
            'analysis_results': analysis_results,
            'metadata': {
                'analyzed_tickers': list(analysis_results.keys()),
                'analysis_time': datetime.now().isoformat(),
                'indicators_calculated': len(list(analysis_results.values())[0]['indicators']) if analysis_results else 0
            }
        }

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate technical analysis results"""
        logger.info("🔍 Validating technical analysis...")

        validation_results = {}
        for ticker, analysis_data in data['analysis_results'].items():
            validation_results[ticker] = {
                'has_indicators': len(analysis_data['indicators']) > 0,
                'has_signals': len(analysis_data['signals']) > 0,
                'has_risk_metrics': len(analysis_data['risk_metrics']) > 0,
                'analysis_complete': bool(analysis_data['analysis_summary'])
            }

        data['analysis_validation'] = validation_results
        logger.info(f"✅ Technical analysis validation completed")

        return data

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        indicators = {}

        if 'close' in df.columns and len(df) >= 20:
            # RSI (Relative Strength Index)
            if len(df) >= 14:
                indicators['rsi'] = self._calculate_rsi(df['close'], 14)

            # MACD
            if len(df) >= 26:
                indicators['macd'] = self._calculate_macd(df['close'])

            # Bollinger Bands
            if len(df) >= 20:
                indicators['bollinger_bands'] = self._calculate_bollinger_bands(df['close'], 20)

            # Moving Averages
            indicators['moving_averages'] = {
                'ma_5': df['close'].rolling(window=5).mean().iloc[-1] if len(df) >= 5 else None,
                'ma_20': df['close'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else None,
                'ma_50': df['close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
            }

            # Price momentum
            indicators['momentum'] = {
                'price_change_1d': ((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) if len(df) >= 2 else 0,
                'price_change_5d': ((df['close'].iloc[-1] / df['close'].iloc[-6]) - 1) if len(df) >= 6 else 0,
                'price_change_20d': ((df['close'].iloc[-1] / df['close'].iloc[-21]) - 1) if len(df) >= 21 else 0
            }

        return indicators

    def _generate_signals(self, df: pd.DataFrame, indicators: Dict) -> List[Dict]:
        """Generate trading signals based on indicators"""
        signals = []

        if 'close' in df.columns and len(df) >= 20:
            current_price = df['close'].iloc[-1]

            # RSI signals
            if 'rsi' in indicators and indicators['rsi']:
                current_rsi = indicators['rsi'][-1]
                if current_rsi < 30:
                    signals.append({
                        'type': 'BUY',
                        'indicator': 'RSI',
                        'reason': f'RSI ({current_rsi:.1f}) indicates oversold condition',
                        'strength': 'STRONG' if current_rsi < 20 else 'MODERATE'
                    })
                elif current_rsi > 70:
                    signals.append({
                        'type': 'SELL',
                        'indicator': 'RSI',
                        'reason': f'RSI ({current_rsi:.1f}) indicates overbought condition',
                        'strength': 'STRONG' if current_rsi > 80 else 'MODERATE'
                    })

            # Moving average signals
            if 'moving_averages' in indicators:
                ma_20 = indicators['moving_averages'].get('ma_20')
                if ma_20 and current_price > ma_20:
                    signals.append({
                        'type': 'BUY',
                        'indicator': 'MA20',
                        'reason': f'Price (${current_price:.2f}) above 20-day MA (${ma_20:.2f})',
                        'strength': 'MODERATE'
                    })
                elif ma_20 and current_price < ma_20:
                    signals.append({
                        'type': 'SELL',
                        'indicator': 'MA20',
                        'reason': f'Price (${current_price:.2f}) below 20-day MA (${ma_20:.2f})',
                        'strength': 'MODERATE'
                    })

            # MACD signals
            if 'macd' in indicators and indicators['macd']:
                macd_line = indicators['macd']['macd']
                signal_line = indicators['macd']['signal']
                if macd_line and signal_line and len(macd_line) >= 2 and len(signal_line) >= 2:
                    # MACD crossover
                    if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
                        signals.append({
                            'type': 'BUY',
                            'indicator': 'MACD',
                            'reason': 'MACD line crossed above signal line',
                            'strength': 'STRONG'
                        })
                    elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
                        signals.append({
                            'type': 'SELL',
                            'indicator': 'MACD',
                            'reason': 'MACD line crossed below signal line',
                            'strength': 'STRONG'
                        })

        return signals

    def _calculate_risk_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate risk metrics"""
        risk_metrics = {}

        if 'close' in df.columns and len(df) >= 20:
            returns = df['close'].pct_change().dropna()

            if len(returns) > 0:
                # Volatility
                risk_metrics['volatility'] = {
                    'daily': returns.std(),
                    'annualized': returns.std() * np.sqrt(252)
                }

                # Maximum drawdown
                cumulative_returns = (1 + returns).cumprod()
                rolling_max = cumulative_returns.expanding().max()
                drawdowns = (cumulative_returns - rolling_max) / rolling_max
                risk_metrics['max_drawdown'] = {
                    'value': drawdowns.min(),
                    'date': drawdowns.idxmin().isoformat() if not drawdowns.empty else None
                }

                # Value at Risk (95%)
                risk_metrics['var_95'] = returns.quantile(0.05)

                # Sharpe ratio (assuming risk-free rate = 2% annual)
                risk_free_rate = 0.02 / 252  # daily risk-free rate
                excess_returns = returns - risk_free_rate
                if len(excess_returns) > 0 and returns.std() > 0:
                    risk_metrics['sharpe_ratio'] = excess_returns.mean() / returns.std() * np.sqrt(252)
                else:
                    risk_metrics['sharpe_ratio'] = 0

        return risk_metrics

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> List[float]:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.fillna(0).tolist()

    def _calculate_macd(self, prices: pd.Series) -> Dict[str, List[float]]:
        """Calculate MACD indicator"""
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line.fillna(0).tolist(),
            'signal': signal_line.fillna(0).tolist(),
            'histogram': histogram.fillna(0).tolist()
        }

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        return {
            'upper': upper_band.fillna(0).tolist(),
            'middle': sma.fillna(0).tolist(),
            'lower': lower_band.fillna(0).tolist()
        }

    def _create_analysis_summary(self, indicators: Dict, signals: List[Dict], risk_metrics: Dict) -> Dict[str, Any]:
        """Create analysis summary"""
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']

        return {
            'total_signals': len(signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'strongest_signal': max(signals, key=lambda x: {'STRONG': 3, 'MODERATE': 2, 'WEAK': 1}.get(x['strength'], 0)) if signals else None,
            'risk_level': self._assess_risk_level(risk_metrics),
            'analysis_confidence': self._calculate_analysis_confidence(indicators, signals)
        }

    def _assess_risk_level(self, risk_metrics: Dict) -> str:
        """Assess overall risk level"""
        if 'max_drawdown' in risk_metrics:
            max_dd = risk_metrics['max_drawdown'].get('value', 0)
            if max_dd < -0.20:
                return 'HIGH'
            elif max_dd < -0.10:
                return 'MEDIUM'
            else:
                return 'LOW'
        return 'UNKNOWN'

    def _calculate_analysis_confidence(self, indicators: Dict, signals: List[Dict]) -> float:
        """Calculate confidence score for analysis"""
        confidence = 0.0

        # Check indicator availability
        if indicators:
            confidence += 0.3

        # Check signal strength
        if signals:
            strong_signals = [s for s in signals if s.get('strength') == 'STRONG']
            confidence += 0.2 + (0.3 * (len(strong_signals) / len(signals)))

        # Check data quality factors
        if len(indicators.get('moving_averages', {})) >= 2:
            confidence += 0.2

        return min(confidence, 1.0)

class InsightGenerationStage:
    """Stage 4: Insight Generation and Reporting"""

    def __init__(self):
        self.name = "Insight Generation"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate actionable insights and create reports

        Input: Technical analysis results from Stage 3
        Output: Actionable investment insights and reports
        """
        logger.info("🔄 Starting insight generation and reporting...")

        insights = {}
        portfolio_insights = {}

        # Process individual ticker insights
        for ticker, analysis_data in data['analysis_results'].items():
            ticker_insights = self._generate_ticker_insights(ticker, analysis_data)
            insights[ticker] = ticker_insights

        # Generate portfolio-level insights
        if len(insights) > 1:
            portfolio_insights = self._generate_portfolio_insights(insights)

        # Create final report
        final_report = self._create_final_report(insights, portfolio_insights, data)

        return {
            'insights': insights,
            'portfolio_insights': portfolio_insights,
            'final_report': final_report,
            'metadata': {
                'generated_insights': len(insights),
                'generation_time': datetime.now().isoformat(),
                'report_format': 'comprehensive_analysis'
            }
        }

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated insights"""
        logger.info("🔍 Validating generated insights...")

        validation_results = {
            'has_insights': len(data['insights']) > 0,
            'has_portfolio_insights': len(data['portfolio_insights']) > 0,
            'has_final_report': bool(data['final_report']),
            'insight_quality': self._assess_insight_quality(data['insights'])
        }

        data['insights_validation'] = validation_results
        logger.info(f"✅ Insight validation completed")

        return data

    def _generate_ticker_insights(self, ticker: str, analysis_data: Dict) -> Dict[str, Any]:
        """Generate insights for individual ticker"""
        indicators = analysis_data['indicators']
        signals = analysis_data['signals']
        risk_metrics = analysis_data['risk_metrics']
        summary = analysis_data['analysis_summary']

        # Generate recommendation
        recommendation = self._generate_recommendation(signals, summary, risk_metrics)

        # Generate key insights
        key_insights = self._extract_key_insights(indicators, signals, risk_metrics)

        # Generate price targets (basic method)
        price_targets = self._generate_price_targets(indicators, risk_metrics)

        return {
            'ticker': ticker,
            'recommendation': recommendation,
            'key_insights': key_insights,
            'price_targets': price_targets,
            'risk_assessment': self._create_risk_assessment(risk_metrics),
            'technical_outlook': self._create_technical_outlook(indicators, signals),
            'actionable_items': self._generate_actionable_items(signals, recommendation)
        }

    def _generate_portfolio_insights(self, insights: Dict) -> Dict[str, Any]:
        """Generate portfolio-level insights"""
        # Aggregate recommendations
        recommendations = [insight['recommendation']['action'] for insight in insights.values()]
        buy_count = recommendations.count('BUY')
        sell_count = recommendations.count('SELL')
        hold_count = recommendations.count('HOLD')

        # Risk aggregation
        risk_levels = [insight['risk_assessment']['level'] for insight in insights.values()]
        portfolio_risk = max(risk_levels) if risk_levels else 'MEDIUM'

        # Portfolio strategy
        portfolio_strategy = self._generate_portfolio_strategy(buy_count, sell_count, hold_count, portfolio_risk)

        return {
            'portfolio_summary': {
                'total_tickers': len(insights),
                'buy_recommendations': buy_count,
                'sell_recommendations': sell_count,
                'hold_recommendations': hold_count
            },
            'portfolio_risk': portfolio_risk,
            'portfolio_strategy': portfolio_strategy,
            'diversification_insights': self._generate_diversification_insights(insights),
            'market_timing': self._assess_market_timing(insights)
        }

    def _create_final_report(self, insights: Dict, portfolio_insights: Dict, data: Dict) -> Dict[str, Any]:
        """Create comprehensive final report"""
        return {
            'executive_summary': self._create_executive_summary(insights, portfolio_insights),
            'detailed_analysis': insights,
            'portfolio_recommendations': portfolio_insights,
            'risk_summary': self._create_risk_summary(insights),
            'actionable_recommendations': self._create_actionable_recommendations(insights, portfolio_insights),
            'methodology': {
                'pipeline_stages': ['Data Acquisition', 'Data Processing', 'Technical Analysis', 'Insight Generation'],
                'indicators_used': list(list(data['analysis_results'].values())[0]['indicators'].keys()) if data['analysis_results'] else [],
                'analysis_confidence': sum(insight['recommendation']['confidence'] for insight in insights.values()) / len(insights) if insights else 0
            },
            'disclaimer': "This analysis is generated by automated systems and should not be considered as financial advice. Please consult with a qualified financial advisor before making investment decisions."
        }

    def _generate_recommendation(self, signals: List[Dict], summary: Dict, risk_metrics: Dict) -> Dict[str, Any]:
        """Generate investment recommendation"""
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']

        # Determine action
        if len(buy_signals) > len(sell_signals) and len(buy_signals) >= 2:
            action = 'BUY'
        elif len(sell_signals) > len(buy_signals) and len(sell_signals) >= 2:
            action = 'SELL'
        else:
            action = 'HOLD'

        # Calculate confidence
        total_signals = len(signals)
        confidence = summary.get('analysis_confidence', 0)

        if action == 'BUY':
            confidence = min(confidence + 0.2, 1.0)
        elif action == 'SELL':
            confidence = min(confidence + 0.2, 1.0)

        return {
            'action': action,
            'confidence': confidence,
            'reasoning': f"Based on {len(buy_signals)} buy signals and {len(sell_signals)} sell signals",
            'time_horizon': 'short_to_medium_term',
            'risk_level': self._assess_risk_level(risk_metrics)
        }

    def _extract_key_insights(self, indicators: Dict, signals: List[Dict], risk_metrics: Dict) -> List[str]:
        """Extract key technical insights"""
        insights = []

        # Momentum insights
        if 'momentum' in indicators:
            momentum_20d = indicators['momentum'].get('price_change_20d', 0)
            if momentum_20d > 0.1:
                insights.append(f"Strong positive momentum over 20 days (+{momentum_20d:.1%})")
            elif momentum_20d < -0.1:
                insights.append(f"Negative momentum over 20 days ({momentum_20d:.1%})")

        # Signal insights
        strong_signals = [s for s in signals if s.get('strength') == 'STRONG']
        if strong_signals:
            signal_types = [s['type'] for s in strong_signals]
            insights.append(f"Strong {', '.join(signal_types)} signals detected")

        # Risk insights
        if 'max_drawdown' in risk_metrics:
            max_dd = risk_metrics['max_drawdown'].get('value', 0)
            if max_dd < -0.15:
                insights.append(f"High historical volatility detected (max drawdown: {max_dd:.1%})")

        return insights

    def _generate_price_targets(self, indicators: Dict, risk_metrics: Dict) -> Dict[str, float]:
        """Generate basic price targets"""
        targets = {}

        if 'moving_averages' in indicators:
            ma_20 = indicators['moving_averages'].get('ma_20')
            ma_50 = indicators['moving_averages'].get('ma_50')

            if ma_20:
                targets['support_20d'] = ma_20 * 0.95
                targets['resistance_20d'] = ma_20 * 1.05

            if ma_50:
                targets['support_50d'] = ma_50 * 0.90
                targets['resistance_50d'] = ma_50 * 1.10

        return targets

    def _create_risk_assessment(self, risk_metrics: Dict) -> Dict[str, Any]:
        """Create risk assessment"""
        risk_level = self._assess_risk_level(risk_metrics)

        risk_factors = []

        if 'volatility' in risk_metrics:
            annual_vol = risk_metrics['volatility'].get('annualized', 0)
            if annual_vol > 0.3:
                risk_factors.append("High volatility")
            elif annual_vol > 0.2:
                risk_factors.append("Moderate volatility")

        if 'max_drawdown' in risk_metrics:
            max_dd = risk_metrics['max_drawdown'].get('value', 0)
            if max_dd < -0.2:
                risk_factors.append("Significant historical drawdowns")

        return {
            'level': risk_level,
            'factors': risk_factors,
            'volatility': risk_metrics.get('volatility', {}).get('annualized', 0),
            'max_drawdown': risk_metrics.get('max_drawdown', {}).get('value', 0),
            'recommendation': self._get_risk_recommendation(risk_level)
        }

    def _create_technical_outlook(self, indicators: Dict, signals: List[Dict]) -> Dict[str, Any]:
        """Create technical outlook summary"""
        outlook = {
            'trend': 'NEUTRAL',
            'momentum': 'NEUTRAL',
            'overall_sentiment': 'NEUTRAL',
            'key_indicators': []
        }

        # Analyze moving averages
        if 'moving_averages' in indicators:
            ma_5 = indicators['moving_averages'].get('ma_5')
            ma_20 = indicators['moving_averages'].get('ma_20')

            if ma_5 and ma_20:
                if ma_5 > ma_20:
                    outlook['trend'] = 'BULLISH'
                    outlook['key_indicators'].append("Price above 20-day MA")
                else:
                    outlook['trend'] = 'BEARISH'
                    outlook['key_indicators'].append("Price below 20-day MA")

        # Analyze momentum
        if 'momentum' in indicators:
            momentum_5d = indicators['momentum'].get('price_change_5d', 0)
            if momentum_5d > 0.05:
                outlook['momentum'] = 'BULLISH'
            elif momentum_5d < -0.05:
                outlook['momentum'] = 'BEARISH'

        # Overall sentiment
        buy_signals = len([s for s in signals if s['type'] == 'BUY'])
        sell_signals = len([s for s in signals if s['type'] == 'SELL'])

        if buy_signals > sell_signals:
            outlook['overall_sentiment'] = 'BULLISH'
        elif sell_signals > buy_signals:
            outlook['overall_sentiment'] = 'BEARISH'

        return outlook

    def _generate_actionable_items(self, signals: List[Dict], recommendation: Dict) -> List[str]:
        """Generate actionable items"""
        items = []

        action = recommendation.get('action', 'HOLD')
        confidence = recommendation.get('confidence', 0)

        if action == 'BUY' and confidence > 0.7:
            items.append("Consider establishing position on next trading day")
            items.append("Set stop-loss at 5% below entry price")
            items.append("Monitor for confirmation signals over next 3-5 days")
        elif action == 'SELL' and confidence > 0.7:
            items.append("Consider reducing or exiting position")
            items.append("Take profits on strong positions")
            items.append("Monitor for reversal signals")
        else:
            items.append("Maintain current position")
            items.append("Continue monitoring for new signals")

        return items

    def _generate_portfolio_strategy(self, buy_count: int, sell_count: int, hold_count: int, portfolio_risk: str) -> Dict[str, Any]:
        """Generate portfolio-level strategy"""
        if buy_count > sell_count + hold_count:
            strategy = 'AGGRESSIVE_GROWTH'
            description = "Multiple buy opportunities suggest bullish market conditions"
        elif sell_count > buy_count + hold_count:
            strategy = 'CONSERVATIVE_DEFENSE'
            description = "Multiple sell signals suggest defensive positioning"
        else:
            strategy = 'BALANCED'
            description = "Mixed signals suggest balanced approach"

        return {
            'strategy': strategy,
            'description': description,
            'risk_adjustment': self._get_risk_adjustment(portfolio_risk),
            'rebalancing_frequency': 'monthly'
        }

    def _generate_diversification_insights(self, insights: Dict) -> Dict[str, Any]:
        """Generate diversification insights"""
        recommendations = [insight['recommendation']['action'] for insight in insights.values()]

        # Check concentration
        buy_concentration = recommendations.count('BUY') / len(recommendations) if recommendations else 0

        return {
            'concentration_risk': 'HIGH' if buy_concentration > 0.7 else 'MEDIUM' if buy_concentration > 0.4 else 'LOW',
            'recommendation_distribution': {
                'BUY': recommendations.count('BUY'),
                'SELL': recommendations.count('SELL'),
                'HOLD': recommendations.count('HOLD')
            },
            'suggestion': 'Consider diversifying across different sectors if concentration is high'
        }

    def _assess_market_timing(self, insights: Dict) -> Dict[str, Any]:
        """Assess market timing opportunities"""
        bullish_signals = sum(1 for insight in insights.values() if insight['technical_outlook']['overall_sentiment'] == 'BULLISH')
        total_tickers = len(insights)

        market_sentiment = bullish_signals / total_tickers if total_tickers > 0 else 0.5

        return {
            'market_sentiment_score': market_sentiment,
            'sentiment': 'BULLISH' if market_sentiment > 0.6 else 'BEARISH' if market_sentiment < 0.4 else 'NEUTRAL',
            'timing_opportunity': 'GOOD' if 0.4 <= market_sentiment <= 0.6 else 'CAUTION',
            'reasoning': f"{bullish_signals}/{total_tickers} tickers showing bullish sentiment"
        }

    def _create_executive_summary(self, insights: Dict, portfolio_insights: Dict) -> Dict[str, Any]:
        """Create executive summary"""
        portfolio_summary = portfolio_insights.get('portfolio_summary', {})

        return {
            'total_analyzed': portfolio_summary.get('total_tickers', 0),
            'primary_action': 'BUY' if portfolio_summary.get('buy_recommendations', 0) > portfolio_summary.get('sell_recommendations', 0) else 'SELL',
            'overall_confidence': 'HIGH' if len(insights) > 0 else 'LOW',
            'key_takeaway': self._generate_key_takeaway(insights, portfolio_insights),
            'next_steps': self._generate_next_steps(portfolio_insights)
        }

    def _create_risk_summary(self, insights: Dict) -> Dict[str, Any]:
        """Create risk summary"""
        risk_levels = [insight['risk_assessment']['level'] for insight in insights.values()]

        return {
            'portfolio_risk': max(risk_levels) if risk_levels else 'MEDIUM',
            'risk_distribution': {
                'HIGH': risk_levels.count('HIGH'),
                'MEDIUM': risk_levels.count('MEDIUM'),
                'LOW': risk_levels.count('LOW')
            },
            'average_volatility': np.mean([insight['risk_assessment'].get('volatility', 0) for insight in insights.values()]) if insights else 0
        }

    def _create_actionable_recommendations(self, insights: Dict, portfolio_insights: Dict) -> List[Dict]:
        """Create actionable recommendations"""
        recommendations = []

        # Portfolio-level recommendations
        strategy = portfolio_insights.get('portfolio_strategy', {})
        if strategy.get('strategy') == 'AGGRESSIVE_GROWTH':
            recommendations.append({
                'type': 'PORTFOLIO',
                'action': 'Consider increasing equity exposure',
                'priority': 'MEDIUM',
                'timeline': '1-3 months'
            })
        elif strategy.get('strategy') == 'CONSERVATIVE_DEFENSE':
            recommendations.append({
                'type': 'PORTFOLIO',
                'action': 'Consider reducing risk exposure',
                'priority': 'HIGH',
                'timeline': 'Immediate'
            })

        # Individual ticker recommendations
        for ticker, insight in insights.items():
            if insight['recommendation']['action'] in ['BUY', 'SELL'] and insight['recommendation']['confidence'] > 0.7:
                recommendations.append({
                    'type': 'TICKER',
                    'ticker': ticker,
                    'action': f"{insight['recommendation']['action']} {ticker}",
                    'priority': 'HIGH' if insight['recommendation']['confidence'] > 0.8 else 'MEDIUM',
                    'timeline': 'Next trading session',
                    'reasoning': insight['recommendation']['reasoning']
                })

        return recommendations

    def _generate_key_takeaway(self, insights: Dict, portfolio_insights: Dict) -> str:
        """Generate key takeaway message"""
        portfolio_summary = portfolio_insights.get('portfolio_summary', {})
        total = portfolio_summary.get('total_tickers', 0)
        buys = portfolio_summary.get('buy_recommendations', 0)
        sells = portfolio_summary.get('sell_recommendations', 0)

        if total == 0:
            return "No actionable insights generated"
        elif buys > sells * 1.5:
            return f"Bullish sentiment detected with {buys}/{total} tickers showing buy signals"
        elif sells > buys * 1.5:
            return f"Bearish sentiment detected with {sells}/{total} tickers showing sell signals"
        else:
            return f"Mixed signals suggest balanced approach with {buys} buy and {sells} sell recommendations"

    def _generate_next_steps(self, portfolio_insights: Dict) -> List[str]:
        """Generate next steps"""
        next_steps = [
            "Review detailed analysis for individual tickers",
            "Consider portfolio rebalancing based on recommendations",
            "Monitor market conditions for confirmation signals",
            "Set up alerts for key price levels and indicators"
        ]

        strategy = portfolio_insights.get('portfolio_strategy', {}).get('strategy', '')
        if strategy == 'AGGRESSIVE_GROWTH':
            next_steps.insert(0, "Research additional growth opportunities in related sectors")
        elif strategy == 'CONSERVATIVE_DEFENSE':
            next_steps.insert(0, "Review stop-loss levels and profit-taking strategies")

        return next_steps

    def _assess_risk_level(self, risk_metrics: Dict) -> str:
        """Assess risk level from metrics"""
        if 'max_drawdown' in risk_metrics:
            max_dd = risk_metrics['max_drawdown'].get('value', 0)
            if max_dd < -0.20:
                return 'HIGH'
            elif max_dd < -0.10:
                return 'MEDIUM'
            else:
                return 'LOW'
        return 'MEDIUM'

    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get risk-based recommendation"""
        recommendations = {
            'HIGH': 'Consider position sizing and risk management strategies',
            'MEDIUM': 'Monitor risk factors and maintain diversified portfolio',
            'LOW': 'Maintain current risk management approach'
        }
        return recommendations.get(risk_level, 'Monitor risk factors')

    def _get_risk_adjustment(self, portfolio_risk: str) -> str:
        """Get risk adjustment recommendation"""
        adjustments = {
            'HIGH': 'Reduce position sizes and increase cash allocation',
            'MEDIUM': 'Maintain balanced risk exposure with diversification',
            'LOW': 'Consider increasing exposure to quality opportunities'
        }
        return adjustments.get(portfolio_risk, 'Maintain current risk profile')

    def _assess_insight_quality(self, insights: Dict) -> str:
        """Assess overall quality of generated insights"""
        if not insights:
            return 'LOW'

        confidence_scores = [insight['recommendation']['confidence'] for insight in insights.values()]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        if avg_confidence > 0.8:
            return 'HIGH'
        elif avg_confidence > 0.6:
            return 'MEDIUM'
        else:
            return 'LOW'

class MarketDataPipeline:
    """
    Complete Market Data Processing Pipeline

    This class demonstrates the end-to-end pipeline architecture where
    "expertise reutilizível" is executed as a "standard operational procedure".
    """

    def __init__(self):
        """Initialize all pipeline stages"""
        self.stages = [
            DataAcquisitionStage(),    # Stage 1: Raw Data Acquisition
            DataProcessingStage(),     # Stage 2: Data Processing & Enrichment
            TechnicalAnalysisStage(),  # Stage 3: Technical Analysis
            InsightGenerationStage()   # Stage 4: Insight Generation & Reporting
        ]

        self.pipeline_name = "Market Data Processing Pipeline"
        self.version = "1.0"

    def execute_pipeline(self, input_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete end-to-end pipeline

        This method demonstrates the flow: Raw Data → Processing → Analysis → Insights
        Each stage processes the output of the previous stage automatically.
        """
        logger.info(f"🚀 Starting {self.pipeline_name} v{self.version}")
        logger.info(f"Processing tickers: {input_config.get('tickers', [])}")

        current_data = input_config
        execution_log = []

        # Execute each pipeline stage
        for i, stage in enumerate(self.stages, 1):
            logger.info(f"🔄 Executing Stage {i}: {stage.name}")

            try:
                # Process data through current stage
                current_data = stage.process(current_data)

                # Validate stage output
                current_data = stage.validate(current_data)

                # Log stage completion
                execution_log.append({
                    'stage': i,
                    'name': stage.name,
                    'status': 'COMPLETED',
                    'timestamp': datetime.now().isoformat()
                })

                logger.info(f"✅ Stage {i} ({stage.name}) completed successfully")

            except Exception as e:
                logger.error(f"❌ Stage {i} ({stage.name}) failed: {e}")
                execution_log.append({
                    'stage': i,
                    'name': stage.name,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

                # Continue execution with error handling
                current_data['pipeline_error'] = {
                    'failed_stage': stage.name,
                    'error': str(e)
                }

        # Add pipeline execution metadata
        current_data['pipeline_execution'] = {
            'pipeline_name': self.pipeline_name,
            'version': self.version,
            'total_stages': len(self.stages),
            'execution_log': execution_log,
            'execution_time': datetime.now().isoformat(),
            'input_config': input_config,
            'success': all(log['status'] == 'COMPLETED' for log in execution_log)
        }

        logger.info(f"🎉 Pipeline execution completed. Success: {current_data['pipeline_execution']['success']}")

        return current_data

    def get_pipeline_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable pipeline summary"""
        execution = results.get('pipeline_execution', {})
        insights = results.get('insights', {})
        portfolio_insights = results.get('portfolio_insights', {})

        summary = f"""
=== PIPELINE EXECUTION SUMMARY ===
Pipeline: {execution.get('pipeline_name', 'Unknown')} v{execution.get('version', 'Unknown')}
Status: {'✅ SUCCESS' if execution.get('success', False) else '❌ FAILED'}
Stages Completed: {len([log for log in execution.get('execution_log', []) if log['status'] == 'COMPLETED'])}/{execution.get('total_stages', 0)}

=== INSIGHTS GENERATED ===
Analyzied Tickers: {len(insights)}
Portfolio Risk: {portfolio_insights.get('portfolio_risk', 'UNKNOWN')}
Strategy: {portfolio_insights.get('portfolio_strategy', {}).get('strategy', 'UNKNOWN')}

=== KEY RECOMMENDATIONS ===
"""

        # Add individual ticker recommendations
        for ticker, insight in insights.items():
            rec = insight.get('recommendation', {})
            summary += f"- {ticker}: {rec.get('action', 'UNKNOWN')} (Confidence: {rec.get('confidence', 0):.1%})\n"

        return summary

def main():
    """Example usage of the Market Data Pipeline"""

    # Example input configuration
    config = {
        'tickers': ['AAPL', 'MSFT', 'GOOGL'],
        'period': '6mo',
        'data_sources': ['yahoo_finance'],
        'api_key': None  # Add Alpha Vantage API key if available
    }

    # Initialize and execute pipeline
    pipeline = MarketDataPipeline()

    try:
        results = pipeline.execute_pipeline(config)

        # Print summary
        print(pipeline.get_pipeline_summary(results))

        # Print final insights
        if 'final_report' in results:
            print("\n=== FINAL REPORT ===")
            executive_summary = results['final_report'].get('executive_summary', {})
            print(f"Key Takeaway: {executive_summary.get('key_takeaway', 'No key takeaway')}")

            actionable_recs = results['final_report'].get('actionable_recommendations', [])
            if actionable_recs:
                print("\nActionable Recommendations:")
                for rec in actionable_recs[:5]:  # Show top 5
                    print(f"- {rec.get('action', 'No action')} (Priority: {rec.get('priority', 'UNKNOWN')})")

        return results

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return None

if __name__ == "__main__":
    main()