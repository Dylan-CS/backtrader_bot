from datetime import datetime

BACKTEST_CONFIG = {
    'cash': 10000.0,
    'commission': 0.001,
    'stake': 10,
    'fromdate': datetime(2020, 1, 1),
    'todate': datetime(2023, 12, 31),
    'data_feed': 'yfinance',
    'symbols': ['AAPL', 'MSFT', 'GOOGL', 'QQQM'],
    'strategies': {
        'sma_crossover': {
            'fast_period': 10,
            'slow_period': 30
        },
        'qqqm_momentum': {
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'ma_fast': 20,
            'ma_slow': 50,
            'atr_period': 14,
            'atr_multiplier': 2.0,
            'position_size': 0.95
        },
        'qqqm_momentum_enhanced': {
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'ma_fast': 20,
            'ma_slow': 50,
            'atr_period': 14,
            'atr_multiplier': 2.0,
            'position_size': 0.95,
            'volume_ma': 20,
            'min_volume_ratio': 1.2,
            'volatility_threshold': 0.02
        }
    },
    'analyzers': ['Returns', 'DrawDown', 'SharpeRatio', 'TradeAnalyzer', 'TimeReturn']
}