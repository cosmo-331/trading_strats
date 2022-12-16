# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 17:35:28 2022

@author: Thinkpad
"""
import backtrader as bt
import backtrader.indicators as ind
from datetime import datetime
import tushare as ts
import FunctionsLib as FL
import Plots
import single_stock_strats
import pandas as pd
ts.set_token('99858a63ddbc39334d2e61af5aa19f5ac5f5da5a2c109262ed68a092') #token如果失效，需要登陆Tushare官网刷新后更改
pro = ts.pro_api()
def single_stock_test(strat, stock_list = ['000002.SZ'], start_date = datetime(2019,1,1),
             end_date = datetime.today(), commission = 0.0005):
    '''
    Tests an implemented strategy that are prewritten for a single 
    stock over a period.

    Parameters
    ----------
    strategy : backtrader.Strategy
        Some written strategies in "single_stock_strats"
    stock_ID : str, optional
        The ID of the stock we wish to backtest the strategy. The default 
        is '000002.SZ'.
    start_date : datetime, optional
        The default is datetime(2010,1,1).
    end_date : datetime, optional
        The default is datetime.today().
    commission : float, optional
        The default is 0.0005.

    Returns
    -------
    cerebro : backtrader.Cerebro
        the backtrader Cerebro object, returned for further analysis.

    '''
    # get the data from api
    order_history = {'date': [],
                     'stock_ID': [],
                     'type': [],
                     'price': []}
    for stock in stock_list:
        df = pro.daily(ts_code = stock, start_date = '20190101')
        df.index = df['trade_date'].apply(FL.timefromstr)
        df = df.rename({'vol':'volume'}, axis = 1)
        df = df.iloc[::-1]
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strat)
        cerebro.broker.setcash(100000.0)
        data = bt.feeds.PandasData(dataname=df,
                                  fromdate = start_date,
                                  todate = end_date)
        cerebro.adddata(data)
        print(stock)
        res = cerebro.run()
        orders = res[0].transactions
        order_history['date'] += orders['date']
        order_history['type'] += orders['type']
        order_history['price'] += orders['price']
        order_history['stock_ID'] += [stock for i in range(len(orders['price']))]
    return order_history
if __name__ == '__main__':
    stocks = FL.stock_filter()[:100]
    results = single_stock_test(single_stock_strats.DFP, stock_list=stocks)
    pd.DataFrame(results).to_csv('order_history.csv')