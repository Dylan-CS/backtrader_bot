import backtrader as bt
import yfinance as yf
import pandas as pd

class YahooFinanceData(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
        ('openinterest', None),
    )

def get_yahoo_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date, progress=False)
    # Flatten the multi-level columns if they exist
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)  # Keep the price level, drop ticker
    return data