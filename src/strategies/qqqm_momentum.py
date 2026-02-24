"""
QQQM Momentum Strategy
动量策略 for Invesco QQQ Trust ETF (QQQM)
"""

import backtrader as bt
import numpy as np

class QQQMMomentum(bt.Strategy):
    """
    QQQM动量策略
    基于相对强弱指数(RSI)和移动平均线(MA)的动量策略
    """
    
    params = (
        ('rsi_period', 14),           # RSI周期
        ('rsi_overbought', 70),       # RSI超买线
        ('rsi_oversold', 30),         # RSI超卖线
        ('ma_fast', 20),              # 快速移动平均线
        ('ma_slow', 50),              # 慢速移动平均线
        ('atr_period', 14),           # ATR周期（波动率）
        ('atr_multiplier', 2.0),      # ATR乘数（止损）
        ('position_size', 0.95),      # 仓位大小（可用资金的百分比）
    )
    
    def __init__(self):
        # 技术指标
        self.rsi = bt.indicators.RelativeStrengthIndex(
            self.data.close, period=self.params.rsi_period
        )
        
        self.ma_fast = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_fast
        )
        
        self.ma_slow = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_slow
        )
        
        # ATR用于动态止损
        self.atr = bt.indicators.AverageTrueRange(
            self.data, period=self.params.atr_period
        )
        
        # 跟踪变量
        self.order = None
        self.stop_price = None
        self.entry_price = None
        
        # 金叉/死叉信号
        self.ma_crossover = bt.indicators.CrossOver(self.ma_fast, self.ma_slow)
        
    def log(self, txt, dt=None):
        """日志记录"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
    
    def notify_order(self, order):
        """订单通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行: 价格={order.executed.price:.2f}, '
                        f'成本={order.executed.value:.2f}, '
                        f'佣金={order.executed.comm:.2f}')
                self.entry_price = order.executed.price
                # 设置止损价：入场价 - 2 * ATR
                self.stop_price = self.entry_price - (self.atr[0] * self.params.atr_multiplier)
            elif order.issell():
                self.log(f'卖出执行: 价格={order.executed.price:.2f}, '
                        f'成本={order.executed.value:.2f}, '
                        f'佣金={order.executed.comm:.2f}')
                self.stop_price = None
                self.entry_price = None
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/被拒绝')
        
        self.order = None
    
    def next(self):
        """每个bar执行"""
        
        # 如果有未完成订单，不执行新逻辑
        if self.order:
            return
        
        # 检查止损
        if self.position and self.stop_price:
            if self.data.close[0] <= self.stop_price:
                self.log(f'触发止损: 当前价={self.data.close[0]:.2f}, 止损价={self.stop_price:.2f}')
                self.sell()
                return
        
        # 动量买入信号（三个条件同时满足）：
        # 1. 快速MA在慢速MA之上（金叉或已在上方）
        # 2. RSI从超卖区回升（<30后回到30以上）
        # 3. 当前没有持仓
        buy_signal = (
            self.ma_crossover[0] > 0 or  # 金叉
            (self.ma_fast[0] > self.ma_slow[0] and self.ma_fast[-1] <= self.ma_slow[-1])  # 刚突破
        )
        
        rsi_oversold_recovery = (
            self.rsi[0] > self.params.rsi_oversold and 
            self.rsi[-1] <= self.params.rsi_oversold
        )
        
        if not self.position and buy_signal and rsi_oversold_recovery:
            # 计算仓位大小
            cash = self.broker.getcash()
            position_value = cash * self.params.position_size
            size = int(position_value / self.data.close[0])
            
            if size > 0:
                self.log(f'买入信号: RSI={self.rsi[0]:.2f}, '
                        f'MA快={self.ma_fast[0]:.2f}, MA慢={self.ma_slow[0]:.2f}')
                self.order = self.buy(size=size)
        
        # 卖出信号（三个条件满足其一）：
        # 1. RSI超买（>70）
        # 2. 死叉信号
        # 3. 快速MA跌破慢速MA
        elif self.position:
            rsi_overbought = self.rsi[0] > self.params.rsi_overbought
            ma_death_cross = self.ma_crossover[0] < 0
            ma_below = self.ma_fast[0] < self.ma_slow[0]
            
            if rsi_overbought or ma_death_cross or ma_below:
                self.log(f'卖出信号: RSI={self.rsi[0]:.2f}, '
                        f'MA快={self.ma_fast[0]:.2f}, MA慢={self.ma_slow[0]:.2f}')
                self.order = self.sell()
    
    def stop(self):
        """策略结束"""
        self.log(f'最终组合价值: {self.broker.getvalue():.2f}')
        if self.position:
            self.log('平仓剩余持仓')
            self.close()


class QQQMMomentumEnhanced(QQQMMomentum):
    """
    QQQM增强动量策略
    添加成交量确认和波动率过滤
    """
    
    params = (
        ('volume_ma', 20),            # 成交量移动平均
        ('min_volume_ratio', 1.2),    # 最小成交量比率（当前成交量/平均成交量）
        ('volatility_threshold', 0.02), # 波动率阈值（日波动率）
    )
    
    def __init__(self):
        super().__init__()
        
        # 成交量指标
        self.volume_ma = bt.indicators.SimpleMovingAverage(
            self.data.volume, period=self.params.volume_ma
        )
        
        # 波动率指标（基于ATR百分比）
        self.volatility = self.atr / self.data.close
        
    def next(self):
        """增强版next方法，添加成交量确认"""
        
        # 计算成交量比率
        volume_ratio = self.data.volume[0] / self.volume_ma[0]
        
        # 计算波动率
        current_volatility = self.volatility[0]
        
        # 过滤条件：成交量足够且波动率不过高
        volume_ok = volume_ratio >= self.params.min_volume_ratio
        volatility_ok = current_volatility <= self.params.volatility_threshold
        
        # 保存原始信号计算
        buy_signal = (
            self.ma_crossover[0] > 0 or
            (self.ma_fast[0] > self.ma_slow[0] and self.ma_fast[-1] <= self.ma_slow[-1])
        )
        
        rsi_oversold_recovery = (
            self.rsi[0] > self.params.rsi_oversold and 
            self.rsi[-1] <= self.params.rsi_oversold
        )
        
        # 增强买入信号：需要成交量确认和合适的波动率
        if not self.position and buy_signal and rsi_oversold_recovery and volume_ok and volatility_ok:
            cash = self.broker.getcash()
            position_value = cash * self.params.position_size
            size = int(position_value / self.data.close[0])
            
            if size > 0:
                self.log(f'增强买入信号: RSI={self.rsi[0]:.2f}, '
                        f'成交量比率={volume_ratio:.2f}, 波动率={current_volatility:.4f}')
                self.order = self.buy(size=size)
        
        # 卖出逻辑保持不变
        elif self.position:
            rsi_overbought = self.rsi[0] > self.params.rsi_overbought
            ma_death_cross = self.ma_crossover[0] < 0
            ma_below = self.ma_fast[0] < self.ma_slow[0]
            
            if rsi_overbought or ma_death_cross or ma_below:
                self.log(f'卖出信号: RSI={self.rsi[0]:.2f}')
                self.order = self.sell()