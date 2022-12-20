# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 14:27:40 2022

@author: Thinkpad
"""
import backtrader as bt
import backtrader.indicators as ind
from datetime import datetime
import tushare as ts
import FunctionsLib as FL
import Plots
import numpy as np

class MA_cross(bt.Strategy):
    params = (
        ('pfast', 5),
        ('pslow', 20)
    )
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.MAslow = bt.indicators.MovingAverageSimple(self.datas[0], period = self.params.pslow)
        self.MAfast = bt.indicators.MovingAverageSimple(self.datas[0], period = self.params.pfast)
        
    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.broker.get_cash())
        if (self.MAfast[0]<self.MAslow[0]) & (self.MAfast[-1] > self.MAslow[-1]) :
            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.order = self.close()
        if (self.MAfast[0]>self.MAslow[0]) & (self.MAfast[-1]<self.MAslow[-1]):
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.order = self.buy(size = int(self.broker.get_cash()/self.dataclose[0]))
            
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

class MACD(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.macd = ind.MACDHisto(self.datas[0])
        
    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.broker.get_cash())
        if (self.macd[0]<0) & (self.macd[-1] > 0) :
            if self.position:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
        if (self.macd[0]>0) & (self.macd[-1]<0):
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.order = self.buy(size = int(self.broker.get_cash()/self.dataclose[0]))
            
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

def is_dfp(is_pos, vol):
    if (is_pos[0] > 0) & (is_pos[1] < 0) & (is_pos[2] > 0):
        if(vol[1]<vol[0]*0.9) & (vol[2]*0.9 > vol[1]):
            return True
    return False

def is_dfp(is_pos, vol):
    if (is_pos[0] > 0) & (is_pos[1] < 0) & (is_pos[2] > 0):
        if(vol[1]<vol[0]) & (vol[2] > vol[1]):
            return True
    return False

def is_sssf(is_pos, vol):
    minn = min(is_pos[0], is_pos[-1])
    maxx = max(is_pos[1:-1])
    if(minn > 0) & (maxx < 0):
        minn = min(vol[0], vol[-1])
        maxx = max(vol[1:-1])
        if minn > maxx:
            return True
    return False

def is_support(low):
    if (low[0]>low[1]) & (low[1]>low[2]) & (low[3]>low[2]) & (low[4]>low[3]):
        return True
    return False

class DFP(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.change = (self.datas[0].close - self.datas[0].open)
        self.MA5 = ind.MovingAverageSimple(self.datas[0], period = 5)
        self.MA20 = ind.MovingAverageSimple(self.datas[0], period = 20)
        self.vol = self.datas[0].volume
        self.dataopen = self.datas[0].open
        self.datalow = self.datas[0].low
        self.datahigh = self.datas[0].high
        self.EMA15 = ind.EMA(self.datas[0], period = 15)
        self.support = -1
        self.resistance = -1
        self.cost = -1
        self.transactions = {'date': [],
                             'type': [],
                             'price': []}
    
    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.broker.get_cash())
        
        if is_support([self.datalow[i] for i in range(-4,1)]):
            self.support = self.datalow[-2]
        if is_support([-self.datahigh[i] for i in range(-4,1)]):
            self.resistance = self.datahigh[-2]
        #self.log('close: %.2f' % self.dataclose[0])
        if self.position:
            # 止损
            if self.dataclose[0] < self.cost*0.9:
                self.order = self.close()
            # 涨到压力位附近卖掉
            if self.datahigh[0] > self.resistance*0.9+self.support*0.1:
                #self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
        else:
            if self.datalow[0]<self.resistance*0.1+self.support*0.9:
                for num in range(1,4):
                    for i in range(-num-6,-num-3):
                        if self.vol[i] > np.mean([self.vol[j] for j in range(i-5, i)])*1.1:
                            if is_sssf([self.change[k] for k in range(i, i+num+2)], 
                                      [self.vol[k] for k in range(i, i+num+2)]):
                                minn = min([self.dataclose[k] for k in range(i+1, i+num+1)])
                                maxx = max([self.dataopen[k] for k in range(i+1, i+num+1)])
                                if (maxx<self.dataclose[i]) & (minn>self.dataopen[i]):
                                    maxx = 0
                                    mean = 0.5 * (self.vol[i] + self.vol[i+num+1])
                                    for j in range(i+num+1,1):
                                        maxx = max(maxx, self.vol[j])
                                    if maxx < mean*0.9:
                                        #self.log('DFP found on %s' % self.datas[0].datetime.date(i))
                                        #self.log('BUY CREATE, %.2f' % self.dataclose[0])
                                        self.order = self.buy()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # An active Buy/Sell order has been submitted/accepted - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            
            if order.isbuy():
                #cap = cap / order.executed.price
                #now_time = self.datas.datetime.date(0)
                self.log(f' BUY EXECUTED, {order.executed.price:.2f}')
                self.cost = order.executed.price
                self.transactions['date'].append(self.datas[0].datetime.date(0))
                self.transactions['price'].append(order.executed.price)
                self.transactions['type'].append('BUY')
            elif order.issell():
                #cap = cap * order.executed.price
                #total_time = (self.datas.datetime.date(0) - now_time).days + total_time
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
                self.transactions['date'].append(self.datas[0].datetime.date(0))
                self.transactions['price'].append(order.executed.price)                                 
                self.transactions['type'].append('SELL')
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None
