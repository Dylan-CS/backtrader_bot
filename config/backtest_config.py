from datetime import datetime

BACKTEST_CONFIG = {
    'cash': 10000.0,
    'commission': 0.001,
    'stake': 10,
    'fromdate': datetime(2020, 1, 1),
    'todate': datetime(2023, 12, 31),
    'data_feed': 'yfinance',
    'symbols': ['AAPL', 'MSFT', 'GOOGL'],
    'strategies': {
        'sma_crossover': {
            'fast_period': 10,
            'slow_period': 30
        }
    },
    'analyzers': ['Returns', 'DrawDown', 'SharpeRatio', 'TradeAnalyzer']
}