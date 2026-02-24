"""
数据源模块 - 使用yfinance获取真实市场数据
"""

import backtrader as bt
import pandas as pd
import datetime

class YahooFinanceData(bt.feeds.PandasData):
    """yfinance数据源适配器"""
    params = (
        ('datetime', None),
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
        ('openinterest', None),
    )

def get_yahoo_data(symbol, start_date, end_date, progress=False):
    """
    使用yfinance获取数据（主函数）
    会尝试多种方法确保获取成功
    """
    # 首先尝试修复版本
    from .yfinance_fixed import get_yfinance_data_fixed
    
    data = get_yfinance_data_fixed(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        progress=progress
    )
    
    # 确保列名正确（Backtrader需要大写列名）
    column_mapping = {
        'open': 'Open',
        'high': 'High', 
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'adj close': 'Adj Close'
    }
    
    # 重命名列
    for old_col, new_col in column_mapping.items():
        if old_col in data.columns:
            data = data.rename(columns={old_col: new_col})
    
    # 检查必要列
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in data.columns:
            raise ValueError(f"数据缺少必要列: {col}")
    
    return data

def test_data_source():
    """测试数据源"""
    print("测试yfinance数据源...")
    
    try:
        data = get_yahoo_data(
            'QQQM',
            datetime.datetime(2023, 1, 1),
            datetime.datetime(2023, 12, 31)
        )
        
        print(f"数据获取成功!")
        print(f"形状: {data.shape}")
        print(f"列: {list(data.columns)}")
        print(f"日期范围: {data.index[0]} 到 {data.index[-1]}")
        
        # 创建Backtrader数据源测试
        data_feed = YahooFinanceData(dataname=data)
        print("Backtrader数据源创建成功!")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_data_source()