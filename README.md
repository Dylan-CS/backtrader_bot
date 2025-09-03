# Backtrader Trading Bot

A comprehensive algorithmic trading backtest engine built on Backtrader for developing, testing, and optimizing trading strategies.

## Features

- **Multiple Strategy Support**: Easily implement and test various trading strategies
- **Yahoo Finance Integration**: Real-time and historical market data integration
- **Configurable Backtesting**: Flexible configuration for different market conditions
- **Technical Indicators**: Built-in support for common technical analysis indicators
- **Performance Analytics**: Comprehensive performance metrics and analysis
- **Modular Architecture**: Clean, maintainable code structure for easy extension

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backtrader_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: For TA-Lib installation, you may need to install system dependencies first:
```bash
# Ubuntu/Debian
sudo apt-get install libta-lib-dev

# macOS
brew install ta-lib
```

### Running a Backtest

Run a simple SMA crossover strategy on Apple stock:
```bash
python backtest_engine.py --strategy sma_crossover --symbol AAPL
```

Customize the backtest parameters:
```bash
python backtest_engine.py --strategy sma_crossover --symbol MSFT
```

## Project Structure

```
backtrader_bot/
├── backtest_engine.py      # Main backtest execution script
├── config/
│   └── backtest_config.py  # Backtest configuration settings
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── data_feeds.py   # Data feed implementations
│   └── strategies/
│       ├── __init__.py
│       └── sma_crossover.py # Sample SMA crossover strategy
├── requirements.txt        # Python dependencies
├── ROADMAP.md             # Development roadmap
└── README.md              # This file
```

## Configuration

Edit `config/backtest_config.py` to customize backtest parameters:

```python
BACKTEST_CONFIG = {
    'cash': 10000.0,           # Initial capital
    'commission': 0.001,       # Broker commission rate
    'stake': 10,               # Number of shares per trade
    'fromdate': datetime(2020, 1, 1),  # Backtest start date
    'todate': datetime(2023, 12, 31),   # Backtest end date
    'data_feed': 'yfinance',   # Data source
    'symbols': ['AAPL', 'MSFT', 'GOOGL'],  # Supported symbols
    'strategies': {
        'sma_crossover': {
            'fast_period': 10,  # Fast SMA period
            'slow_period': 30   # Slow SMA period
        }
    },
    'analyzers': ['Returns', 'DrawDown', 'SharpeRatio', 'TradeAnalyzer']
}
```

## Creating Strategies

Strategies are implemented in the `src/strategies/` directory. Here's an example SMA crossover strategy:

```python
import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (
        ('fast_period', 10),  # Fast SMA period
        ('slow_period', 30),  # Slow SMA period
    )

    def __init__(self):
        self.fast_sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)

    def next(self):
        if not self.position:
            if self.crossover > 0:  # Fast SMA crosses above slow SMA
                self.buy()
        elif self.crossover < 0:    # Fast SMA crosses below slow SMA
            self.close()
```

To create a new strategy:

1. Create a new Python file in `src/strategies/`
2. Implement your strategy class inheriting from `bt.Strategy`
3. Add strategy configuration to `config/backtest_config.py`
4. Test with: `python backtest_engine.py --strategy your_strategy_name`

## Data Feeds

The project supports multiple data sources through the `src/data/data_feeds.py` module:

- **Yahoo Finance**: Real-time and historical market data
- Custom data feeds can be added by extending `bt.feeds.PandasData`

Example usage:
```python
from src.data.data_feeds import get_yahoo_data

data = get_yahoo_data('AAPL', start_date, end_date)
```

## Performance Metrics

The backtest engine includes comprehensive performance analysis:

- **Returns**: Total return and annualized return
- **DrawDown**: Maximum drawdown and recovery analysis
- **Sharpe Ratio**: Risk-adjusted returns
- **Trade Analyzer**: Detailed trade statistics

## Development Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development plans including:

- Phase 1: Core Infrastructure (Completed)
- Phase 2: Enhanced Features (In Progress)
- Phase 3: Production Features
- Phase 4: Advanced Capabilities

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue on GitHub
- Check the documentation in this README
- Review the Backtrader documentation at [www.backtrader.com](https://www.backtrader.com)

## Disclaimer

This software is for educational and research purposes only. Past performance is not indicative of future results. Trading financial instruments involves risk, and you should carefully consider your investment objectives and risk tolerance before trading.