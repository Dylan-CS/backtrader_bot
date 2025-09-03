#!/usr/bin/env python3

import backtrader as bt
import numpy as np

class MomentumStrategy(bt.Strategy):
    params = (
        ('period', 20),      # Lookback period for momentum calculation
        ('threshold', 0.02), # Minimum momentum threshold to enter trades
        ('stop_loss', 0.05), # 5% stop loss
        ('take_profit', 0.10), # 10% take profit
        ('trail_stop', 0.03), # 3% trailing stop
    )

    def __init__(self):
        # Keep track of closing prices
        self.dataclose = self.datas[0].close
        
        # Momentum indicator (rate of change)
        self.momentum = bt.indicators.ROC(self.dataclose, period=self.params.period)
        
        # Simple moving average for trend confirmation
        self.sma = bt.indicators.SimpleMovingAverage(self.dataclose, period=50)
        
        # Order reference
        self.order = None
        
        # Track entry price for stop loss/take profit calculations
        self.entry_price = None
        
        # Track trailing stop
        self.trailing_stop = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.entry_price = order.executed.price
                self.trailing_stop = self.entry_price * (1 - self.params.trail_stop)
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.entry_price = None
                self.trailing_stop = None

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        # Check if an order is pending
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Buy conditions: positive momentum above threshold and price above SMA
            if (self.momentum[0] > self.params.threshold and 
                self.dataclose[0] > self.sma[0]):
                
                self.log(f'BUY CREATE, Momentum: {self.momentum[0]:.4f}, Price: {self.dataclose[0]:.2f}')
                self.order = self.buy()
                
        else:
            # We are in the market, check exit conditions
            current_price = self.dataclose[0]
            
            # Update trailing stop
            if current_price > self.trailing_stop / (1 - self.params.trail_stop):
                self.trailing_stop = current_price * (1 - self.params.trail_stop)
            
            # Exit conditions:
            # 1. Momentum turns negative
            # 2. Price falls below trailing stop
            # 3. Price hits take profit level
            # 4. Price hits stop loss level
            
            take_profit_level = self.entry_price * (1 + self.params.take_profit)
            stop_loss_level = self.entry_price * (1 - self.params.stop_loss)
            
            if (self.momentum[0] < 0 or 
                current_price <= self.trailing_stop or
                current_price >= take_profit_level or
                current_price <= stop_loss_level):
                
                self.log(f'SELL CREATE, Momentum: {self.momentum[0]:.4f}, Price: {current_price:.2f}')
                self.order = self.sell()

    def stop(self):
        self.log(f'(Momentum Period {self.params.period}) Ending Value: {self.broker.getvalue():.2f}')

# Strategy optimization parameters
class MomentumStrategyOpt(MomentumStrategy):
    def __init__(self):
        super().__init__()
        
        # Add optimization parameters
        self.params.period = range(10, 30, 5)      # Test periods from 10 to 25 in steps of 5
        self.params.threshold = [0.01, 0.02, 0.03] # Different momentum thresholds
        self.params.stop_loss = [0.03, 0.05, 0.07] # Different stop loss levels
        self.params.take_profit = [0.08, 0.10, 0.12] # Different take profit levels