#!/usr/bin/env python3

import backtrader as bt
from datetime import datetime
import argparse
import importlib

from config.backtest_config import BACKTEST_CONFIG
from src.data.data_feeds import YahooFinanceData, get_yahoo_data

def run_backtest(strategy_name, symbol, **kwargs):
    cerebro = bt.Cerebro()
    
    cerebro.broker.setcash(BACKTEST_CONFIG['cash'])
    cerebro.broker.setcommission(commission=BACKTEST_CONFIG['commission'])
    
    data = get_yahoo_data(symbol, BACKTEST_CONFIG['fromdate'], BACKTEST_CONFIG['todate'])
    data_feed = YahooFinanceData(dataname=data)
    cerebro.adddata(data_feed)
    
    strategy_module = importlib.import_module(f'src.strategies.{strategy_name}')
    strategy_class = getattr(strategy_module, 'SMACrossover')
    
    strategy_params = BACKTEST_CONFIG['strategies'].get(strategy_name, {})
    cerebro.addstrategy(strategy_class, **strategy_params)
    
    for analyzer in BACKTEST_CONFIG['analyzers']:
        cerebro.addanalyzer(getattr(bt.analyzers, analyzer), _name=analyzer)
    
    results = cerebro.run()
    
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    print(f"Profit/Loss: {cerebro.broker.getvalue() - BACKTEST_CONFIG['cash']:.2f}")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backtrader Backtest Engine')
    parser.add_argument('--strategy', default='sma_crossover', help='Strategy to use')
    parser.add_argument('--symbol', default='AAPL', help='Symbol to backtest')
    
    args = parser.parse_args()
    
    print(f"Running backtest for {args.symbol} using {args.strategy} strategy")
    results = run_backtest(args.strategy, args.symbol)