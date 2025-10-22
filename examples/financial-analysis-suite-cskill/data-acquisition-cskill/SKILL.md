---
name: financial-data-acquisition
description: Component skill for acquiring financial market data from multiple sources including APIs, CSV files, and real-time feeds. Handles data validation, storage, and updates for the financial analysis suite.
---

# Financial Data Acquisition

This component skill handles all data acquisition needs for the financial analysis suite.

## When to Use This Component Skill

Use this skill when you need to:
- Download market data from APIs (Alpha Vantage, Yahoo Finance)
- Import data from CSV/Excel files
- Validate and clean financial data
- Store data in standardized format
- Update datasets with new data
- Handle missing data and outliers

## Primary Functions

### API Data Sources
- **Alpha Vantage**: Real-time and historical data
- **Yahoo Finance**: Comprehensive market data
- **FRED**: Economic indicators and data
- **Custom APIs**: User-defined data sources

### Data Types Supported
- Stock prices (OHLCV)
- Financial statements
- Economic indicators
- Currency exchange rates
- Commodity prices
- Cryptocurrency data

### Data Processing
- Validation and quality checks
- Missing data imputation
- Outlier detection
- Data normalization
- Time series alignment

## Usage Examples

**Download stock data:**
"Get daily price data for AAPL, MSFT, GOOG from last 2 years"

**Import from file:**
"Import portfolio data from portfolio.csv and validate"

**Update existing data:**
"Update SPY data with latest prices and validate quality"

**Economic data:**
"Download GDP, unemployment, and inflation data from FRED"

## Scripts Available

- `scripts/api_fetcher.py` - Main API data fetching
- `scripts/file_importer.py` - CSV/Excel data import
- `scripts/data_validator.py` - Data quality validation
- `scripts/data_cleaner.py` - Data cleaning utilities
- `scripts/storage_manager.py` - Data storage and retrieval

## Data Storage

Data is stored in standardized format:
- `data/raw/` - Original data files
- `data/processed/` - Cleaned and validated data
- `data/cache/` - Temporary cache files

## Integration

This component skill integrates with:
- **Technical Analysis Engine**: Provides cleaned data
- **Portfolio Optimizer**: Supplies asset data
- **Financial Reporting**: Delivers data for reports

## Configuration

Configuration in `config/data_sources.json`:
```json
{
  "alpha_vantage": {
    "api_key": "YOUR_KEY_HERE",
    "rate_limit": 5
  },
  "default_period": "2y",
  "validation_rules": {
    "min_data_points": 100,
    "max_missing_pct": 0.05
  }
}
```

## Error Handling

- API rate limit management
- Network error recovery
- Data format validation
- Fallback data sources
- Automatic retry mechanisms

This is a **Component Skill** within the Financial Analysis Suite - specialized in data acquisition and preparation.