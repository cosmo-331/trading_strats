# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
import datetime
import time
import re

#初始化tushare接口
ts.set_token('99858a63ddbc39334d2e61af5aa19f5ac5f5da5a2c109262ed68a092') #token如果失效，需要登陆Tushare官网刷新后更改
pro = ts.pro_api()



cal = pro.query('trade_cal', start_date = '20000101', end_date = '20241231', is_open = '1')
trade_days = np.array(cal['cal_date'].apply(int).tolist())
def last_trade_date(today = datetime.datetime.today()):
    '''
    get the latest trade date x such that x <= today

    Parameters
    ----------
    today : datetime
        the desired date for the query. The default is datetime.datetime.today().

    Returns
    -------
    str
        that trade date we got.

    '''
    today = today.strftime('%Y%m%d')
    last_day = trade_days[np.searchsorted(trade_days, today, side = 'right')-1]
    return str(last_day)

def previous_trade_date(today):
    '''
    get the latest trade date x such that x < today

    Parameters
    ----------
    today : datetime
        the desired date for the query.

    Returns
    -------
    str
        that trade date we got.

    '''
    today = today.strftime('%Y%m%d')
    ans = trade_days[np.searchsorted(trade_days, today, side = 'left')-1]
    return str(ans)

def next_trade_date(today):
    '''
    get the earliest trade date x such that today < x

    Parameters
    ----------
    today : datetime
        the desired date for the query.

    Returns
    -------
    str
        that trade date we got.

    '''
    today = today.strftime('%Y%m%d')
    ans = trade_days[np.searchsorted(trade_days, today, side = 'right')]
    return str(ans)
    
df = pro.stock_basic(market = '主板, 中小板, 创业板')

def timefromstr(s):
    year = int(s[:4])
    month = int(s[4:6])
    day = int(s[6:])
    return datetime.datetime(year, month, day)

def stock_filter(today = datetime.datetime.today()):
    #数据初筛
    df = pro.stock_basic(market = '主板, 中小板, 创业板') #只选取主板、中小板及创业板股票
    data = df[df['name'].str.contains('ST') == False] #删除ST数据
    code_list = data['ts_code'].values.tolist() 
    
    #获取最新交易日
    trade_date = last_trade_date(today)
    
    # 条件1：筛选价格在[10,500]之间的股票
    price = pro.daily(trade_date = trade_date)
    afford_stock = price[(price['close'] >= 10 ) & (price['close'] <= 500)].ts_code.tolist()

    # 条件2：删除停牌的股票
    suspend_stock = pro.suspend_d(suspend_type = 'S', trade_date = trade_date)['ts_code'].tolist()

    # 条件3：删除负利润股票，后期可根据基准面信息全面筛选
    income_data = pro.income_vip(period = '', fields = 'ts_code, n_income') #period为对应季度的净利润数据
    pos_income_stocks = income_data[income_data['n_income'] >= 0].ts_code.tolist()
    
    # 条件4：删除次新股票
    new_stock = data[timefromstr(trade_date) - data['list_date'].apply(timefromstr) <= datetime.timedelta(365)]['ts_code'].to_list()

    
    stock = list(set(code_list) & set(afford_stock) & set(pos_income_stocks) -set(new_stock) - set(suspend_stock))
    return stock
    
    
if __name__ == '__main__':
    print(last_trade_date())
    stock = stock_filter()
    print(stock[50:100])