#!/usr/bin/env python3
"""
QQQM动量策略测试脚本
测试两种动量策略在QQQM上的表现
"""

import backtrader as bt
from datetime import datetime
import argparse
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.backtest_config import BACKTEST_CONFIG
from src.data.simple_data_feed import get_yahoo_data_safe, CSVDataFeed, get_sample_data
from src.strategies.qqqm_momentum import QQQMMomentum, QQQMMomentumEnhanced

def test_qqqm_strategy(strategy_class, symbol='QQQM', plot=False):
    """测试QQQM策略"""
    
    print(f"\n{'='*60}")
    print(f"测试 {strategy_class.__name__} 在 {symbol} 上的表现")
    print(f"时间段: {BACKTEST_CONFIG['fromdate'].date()} 到 {BACKTEST_CONFIG['todate'].date()}")
    print(f"{'='*60}")
    
    # 创建cerebro引擎
    cerebro = bt.Cerebro()
    
    # 设置初始资金和佣金
    cerebro.broker.setcash(BACKTEST_CONFIG['cash'])
    cerebro.broker.setcommission(commission=BACKTEST_CONFIG['commission'])
    
    # 获取数据
    print(f"获取 {symbol} 数据...")
    try:
        # 尝试获取真实数据，失败则使用示例数据
        data_df = get_yahoo_data_safe(
            symbol, 
            BACKTEST_CONFIG['fromdate'], 
            BACKTEST_CONFIG['todate']
        )
        
        if data_df.empty:
            print(f"使用示例数据")
            data_df = get_sample_data(symbol, BACKTEST_CONFIG['fromdate'], BACKTEST_CONFIG['todate'])
            
        data_feed = CSVDataFeed(dataname=data_df)
        cerebro.adddata(data_feed)
        
    except Exception as e:
        print(f"数据获取错误: {e}")
        return None
    
    # 添加策略
    strategy_params = BACKTEST_CONFIG['strategies'].get('qqqm_momentum', {})
    cerebro.addstrategy(strategy_class, **strategy_params)
    
    # 添加分析器
    for analyzer_name in BACKTEST_CONFIG['analyzers']:
        try:
            analyzer_class = getattr(bt.analyzers, analyzer_name)
            cerebro.addanalyzer(analyzer_class, _name=analyzer_name)
        except AttributeError:
            print(f"警告: 分析器 {analyzer_name} 不存在")
    
    # 运行回测
    print("运行回测...")
    try:
        results = cerebro.run()
        strat = results[0]
        
        # 基本结果
        final_value = cerebro.broker.getvalue()
        initial_cash = BACKTEST_CONFIG['cash']
        profit = final_value - initial_cash
        profit_pct = (profit / initial_cash) * 100
        
        print(f"\n回测结果:")
        print(f"初始资金: ${initial_cash:,.2f}")
        print(f"最终价值: ${final_value:,.2f}")
        print(f"总利润: ${profit:,.2f}")
        print(f"总回报率: {profit_pct:.2f}%")
        
        # 分析器结果
        if hasattr(strat, 'analyzers'):
            for analyzer_name, analyzer in strat.analyzers.getitems():
                analysis = analyzer.get_analysis()
                if analysis:
                    print(f"\n{analyzer_name} 分析:")
                    for key, value in analysis.items():
                        if isinstance(value, (int, float)):
                            key_str = str(key).lower()
                            if 'drawdown' in key_str or 'ratio' in key_str:
                                print(f"  {key}: {value:.4f}")
                            elif 'return' in key_str:
                                print(f"  {key}: {value:.2f}%")
                            else:
                                print(f"  {key}: {value}")
                        elif isinstance(value, dict):
                            print(f"  {key}: {value}")
        
        # 绘制图表
        if plot:
            print("\n生成图表...")
            cerebro.plot(style='candlestick', volume=True)
        
        return strat
        
    except Exception as e:
        print(f"回测错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_strategies():
    """比较两种QQQM策略"""
    
    print(f"\n{'='*60}")
    print("QQQM动量策略比较")
    print(f"{'='*60}")
    
    strategies = [
        ('基础动量策略', QQQMMomentum),
        ('增强动量策略', QQQMMomentumEnhanced)
    ]
    
    results = []
    
    for strategy_name, strategy_class in strategies:
        print(f"\n测试 {strategy_name}...")
        strat = test_qqqm_strategy(strategy_class, plot=False)
        
        if strat:
            final_value = strat.cerebro.broker.getvalue()
            initial_cash = BACKTEST_CONFIG['cash']
            profit_pct = ((final_value - initial_cash) / initial_cash) * 100
            
            # 获取夏普比率
            sharpe_ratio = 0
            if hasattr(strat, 'analyzers') and 'SharpeRatio' in strat.analyzers:
                sharpe_analysis = strat.analyzers.SharpeRatio.get_analysis()
                sharpe_ratio = sharpe_analysis.get('sharperatio', 0)
            
            # 获取最大回撤
            max_drawdown = 0
            if hasattr(strat, 'analyzers') and 'DrawDown' in strat.analyzers:
                drawdown_analysis = strat.analyzers.DrawDown.get_analysis()
                max_drawdown = drawdown_analysis.get('max', {}).get('drawdown', 0)
            
            results.append({
                'name': strategy_name,
                'final_value': final_value,
                'return_pct': profit_pct,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            })
    
    # 打印比较结果
    if results:
        print(f"\n{'='*60}")
        print("策略比较结果:")
        print(f"{'='*60}")
        print(f"{'策略名称':<20} {'最终价值':<12} {'回报率':<10} {'夏普比率':<12} {'最大回撤':<12}")
        print(f"{'-'*70}")
        
        for r in results:
            print(f"{r['name']:<20} ${r['final_value']:>10,.2f} {r['return_pct']:>9.2f}% "
                  f"{r['sharpe_ratio']:>11.4f} {r['max_drawdown']:>11.2f}%")

def main():
    parser = argparse.ArgumentParser(description='QQQM动量策略测试')
    parser.add_argument('--strategy', choices=['basic', 'enhanced', 'compare'], 
                       default='compare', help='测试的策略类型')
    parser.add_argument('--symbol', default='QQQM', help='测试的标的')
    parser.add_argument('--plot', action='store_true', help='显示图表')
    
    args = parser.parse_args()
    
    print("QQQM动量策略测试")
    print(f"标的: {args.symbol}")
    print(f"时间段: {BACKTEST_CONFIG['fromdate'].date()} 到 {BACKTEST_CONFIG['todate'].date()}")
    
    if args.strategy == 'basic':
        test_qqqm_strategy(QQQMMomentum, args.symbol, args.plot)
    elif args.strategy == 'enhanced':
        test_qqqm_strategy(QQQMMomentumEnhanced, args.symbol, args.plot)
    else:
        compare_strategies()
        
        # 也测试基础策略并显示图表
        if args.plot:
            print(f"\n{'='*60}")
            print("显示基础策略图表...")
            test_qqqm_strategy(QQQMMomentum, args.symbol, plot=True)

if __name__ == "__main__":
    main()