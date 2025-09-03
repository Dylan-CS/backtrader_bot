#!/usr/bin/env python3

import backtrader as bt
import numpy as np

class MomentumStrategyV2(bt.Strategy):
    params = (
        ('momentum_period', 14),    # RSI period for momentum
        ('entry_threshold', 60),    # RSI > 60 for bullish momentum
        ('exit_threshold', 40),     # RSI < 40 to exit
        ('atr_period', 14),         # ATR period for volatility
        ('atr_multiplier', 2.0),    # ATR multiplier for stop loss
        ('risk_per_trade', 0.02),   # 2% risk per trade
        ('min_momentum', 0.05),     # Minimum price momentum requirement
        ('trend_filter', 50),       # SMA period for trend filter
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        
        # RSI for momentum measurement
        self.rsi = bt.indicators.RSI(self.dataclose, period=self.params.momentum_period)
        
        # ATR for volatility-based position sizing and stop loss
        self.atr = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        
        # Trend filter - 50-day SMA
        self.sma = bt.indicators.SimpleMovingAverage(self.dataclose, period=self.params.trend_filter)
        
        # Price momentum (ROC)
        self.momentum = bt.indicators.ROC(self.dataclose, period=10)
        
        self.order = None
        self.entry_price = None
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Size: {order.executed.size}')
                self.entry_price = order.executed.price
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, PnL: {order.executed.pnl:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        if self.order:
            return

        cash = self.broker.getcash()
        portfolio_value = self.broker.getvalue()
        
        if not self.position:
            # Entry conditions:
            # 1. Strong momentum (RSI > entry threshold)
            # 2. Price above trend filter (SMA)
            # 3. Minimum momentum requirement
            if (self.rsi[0] > self.params.entry_threshold and
                self.dataclose[0] > self.sma[0] and
                self.momentum[0] > self.params.min_momentum):
                
                # Position sizing based on ATR stop loss
                risk_amount = portfolio_value * self.params.risk_per_trade
                atr_stop = self.atr[0] * self.params.atr_multiplier
                
                if atr_stop > 0:
                    position_size = risk_amount / atr_stop
                    position_size = int(position_size)
                    
                    if position_size > 0 and cash > position_size * self.dataclose[0]:
                        self.log(f'BUY CREATE, RSI: {self.rsi[0]:.1f}, Momentum: {self.momentum[0]:.3f}')
                        self.order = self.buy(size=position_size)
                        
        else:
            # Exit conditions:
            # 1. Momentum weakens (RSI < exit threshold)
            # 2. Price below trend filter
            # 3. Stop loss based on ATR
            
            current_price = self.dataclose[0]
            stop_loss_price = self.entry_price - (self.atr[0] * self.params.atr_multiplier)
            
            if (self.rsi[0] < self.params.exit_threshold or
                current_price < self.sma[0] or
                current_price <= stop_loss_price):
                
                self.log(f'SELL CREATE, RSI: {self.rsi[0]:.1f}, Price: {current_price:.2f}')
                self.order = self.sell()

    def stop(self):
        final_value = self.broker.getvalue()
        initial_cash = self.broker.startingcash
        total_return = (final_value - initial_cash) / initial_cash * 100
        
        self.log(f'Final Strategy Performance:')
        self.log(f'Ending Value: ${final_value:.2f}')
        self.log(f'Total Return: {total_return:.2f}%')
        self.log(f'Number of Trades: {len(self)}')
        
        if len(self) > 0:
            avg_trade = (final_value - initial_cash) / len(self)
            self.log(f'Average Trade PnL: ${avg_trade:.2f}')