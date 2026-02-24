"""
简单数据源 - 避免yfinance兼容性问题
使用pandas-datareader或直接CSV
"""

import backtrader as bt
import pandas as pd
import datetime

class CSVDataFeed(bt.feeds.PandasData):
    """CSV数据源"""
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', None),
    )

def get_sample_data(symbol='QQQM', start_date=None, end_date=None):
    """
    获取示例数据（模拟QQQM数据）
    实际使用时应该替换为真实数据源
    """
    if start_date is None:
        start_date = datetime.datetime(2020, 1, 1)
    if end_date is None:
        end_date = datetime.datetime(2023, 12, 31)
    
    # 创建示例数据（实际项目应该使用真实数据）
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    n_days = len(dates)
    
    # 模拟QQQM价格数据（实际应该从API获取）
    import numpy as np
    np.random.seed(42)
    
    base_price = 150.0
    returns = np.random.normal(0.0005, 0.015, n_days)
    prices = base_price * np.exp(np.cumsum(returns))
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': prices * (1 + np.random.normal(0, 0.002, n_days)),
        'high': prices * (1 + np.abs(np.random.normal(0.005, 0.003, n_days))),
        'low': prices * (1 - np.abs(np.random.normal(0.005, 0.003, n_days))),
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, n_days)
    }, index=dates)
    
    return data

def get_yahoo_data_safe(symbol, start_date, end_date):
    """
    安全的yfinance包装器，处理兼容性问题
    """
    try:
        import yfinance as yf
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        print(f"警告: yfinance失败 ({e})，使用示例数据")
        return get_sample_data(symbol, start_date, end_date)