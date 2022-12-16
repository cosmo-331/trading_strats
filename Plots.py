# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 10:43:29 2022

@author: Thinkpad
"""
import mplfinance as mpf
import FunctionsLib as FL
def klines_with_signals(df, start_date, end_date, mav_tuple, buy_points = list(), sell_points = list()):
    df.index = df.trade_date.apply(FL.timefromstr)
    df = df.sort_index(ascending = True)
    df = df.loc[start_date: end_date]
    df_new = df[['open','high','low','close','vol']]
    df_new.columns = ['Open', 'High', 'Low', 'Close',"Volume"]
    mav_legend = ['MA'+str(i) for i in mav_tuple]
    df_new.index.rename("date",inplace=True)
    mc = mpf.make_marketcolors(up='red',down='green',inherit=True)
    s = mpf.make_mpf_style(base_mpf_style='charles',
                          rc={'font.family':'SimHei'},
                          marketcolors=mc)
    
    up = df['high'].max()
    down = df['low'].min()
    buy_sig = df['low'].loc[buy_points] - (up-down)*0.05
    df['buy_sig'] = buy_sig
    sell_sig = df['high'].loc[sell_points] + (up-down)*0.05
    df['sell_sig'] = sell_sig
    add_plots = [mpf.make_addplot(df['buy_sig'], 
                                  scatter = True, 
                                  markersize = 500, 
                                  marker = '$B$'),
                 mpf.make_addplot(df['sell_sig'], 
                                  scatter = True,
                                  markersize = 500,
                                  marker = '$S$')
                 ]
    
    
    fig, axlist = mpf.plot(df_new,type='candle',figsize=(16,8),volume=True,
            addplot = add_plots, mav=mav_tuple,figscale=1.5,
            xrotation=15,datetime_format='%Y-%m-%d',
            title='',ylabel='price',ylabel_lower='volume',
            tight_layout=True,style=s, returnfig = True)
    axlist[0].legend(mav_legend)
    
    mpf.show()
    return (axlist, fig)

    