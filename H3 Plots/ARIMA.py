# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 23:55:37 2019
ARIMA TEST
@author: lixuan
"""
from scipy.optimize import minimize
# from WindPy import *
# import WindPy as w                           # for data fetching.
import statsmodels.api as sm                 # for OLS result.
from statsmodels import regression           # for OLS.
import math                                  # math calculation.
import matplotlib.pyplot as plt              # specify "plt".
import seaborn as sns                        # for plotting.
import numpy as np                           # for numerical manipulation.
import pandas as pd                          # for wrapping csv file.
import os                  
from statsmodels.tsa.stattools import adfuller

F = pd.read_csv(open("D:\coco\WORK\WIFA\HS300\H3 Data\ARIMA_data\F_df.csv",'r',encoding="utf-8"), index_col=[0])


ind=list(F.index)
ind=[str(i) for i in ind]
ind=[i[0:4]+'-'+i[4:6]+'-'+i[6:8] for i in ind]
F.index = pd.to_datetime(ind)
#时间格式

ts = F['GROWTH']


# 移动平均图
def draw_trend(timeseries, size):
    f = plt.figure(facecolor='white')
    # 对size个数据进行移动平均
    rol_mean = timeseries.rolling(window=size).mean()
    # 对size个数据移动平均的方差
    rol_std = timeseries.rolling(window=size).std()
 
    timeseries.plot(color='blue', label='Original')
    rol_mean.plot(color='red', label='Rolling Mean')
    rol_std.plot(color='black', label='Rolling standard deviation')
    plt.legend(loc='best')
    plt.title(ts.name + 'Rolling Mean & Standard Deviation') #对原代码加了ts.name 画图用
    plt.show()
 
def draw_ts(timeseries):
    f = plt.figure(facecolor='white')
    timeseries.plot(color='blue')
    plt.show()
 
#Dickey-Fuller test:
def teststationarity(ts):
    dftest = adfuller(ts)
    # 对上述函数求得的值进行语义描述
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    return dfoutput



draw_trend(ts,12)
draw_ts(ts)
teststationarity(ts)



from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


def draw_acf_pacf(ts,lags):
    f = plt.figure(facecolor='white')
    ax1 = f.add_subplot(211)
    plot_acf(ts,ax=ax1,lags=lags)
    ax2 = f.add_subplot(212)
    plot_pacf(ts,ax=ax2,lags=lags)
    plt.subplots_adjust(hspace=0.5)
    plt.show()
    
draw_acf_pacf(ts,30)



for i in F.columns:
    ts = F[i]
    print(i)
    draw_trend(ts,12)
    draw_acf_pacf(ts,30)
    print(teststationarity(ts))




from statsmodels.tsa.arima_model import ARIMA
model = ARIMA(ts, order=(p,d,q)) 
result_arima = model.fit( disp=-1, method='css')


'''
VALUE 平稳√
Test Statistic                -9.874532e+00
p-value                        3.914286e-17
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
GROWTH
Test Statistic                -1.018399e+01
p-value                        6.581765e-18
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
PROFIT 平稳√
Test Statistic                -9.972023e+00
p-value                        2.227401e-17
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
QUALITY
Test Statistic                -1.018471e+01
p-value                        6.554733e-18
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
MOMENTUM 平稳√
Test Statistic                -9.692955e+00
p-value                        1.123724e-16
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
VOLATILITY
Test Statistic                -1.063178e+01
p-value                        5.192104e-19
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
LIQUIDITY 平稳√
Test Statistic                -8.653080e+00
p-value                        5.053453e-14
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
market
Test Statistic                  -2.415998
p-value                          0.137272
#Lags Used                       8.000000
Number of Observations Used    111.000000
Critical Value (1%)             -3.490683
Critical Value (5%)             -2.887952
Critical Value (10%)            -2.580857
dtype: float64
银行
Test Statistic                -1.004036e+01
p-value                        1.501902e-17
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
房地产 平稳√
Test Statistic                -9.561410e+00
p-value                        2.420326e-16
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
通信 平稳√
Test Statistic                -9.681588e+00
p-value                        1.200624e-16
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
家用电器 平稳√
Test Statistic                  -3.265178
p-value                          0.016509
#Lags Used                       6.000000
Number of Observations Used    113.000000
Critical Value (1%)             -3.489590
Critical Value (5%)             -2.887477
Critical Value (10%)            -2.580604
dtype: float64
机械设备 平稳√
Test Statistic                -9.068440e+00
p-value                        4.367920e-15
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
非银金融 平稳√
Test Statistic                -9.079048e+00
p-value                        4.103438e-15
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
汽车 平稳√
Test Statistic                -8.724267e+00
p-value                        3.321210e-14
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
化工 平稳√
Test Statistic                -8.639735e+00
p-value                        5.467133e-14
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
电子 平稳√
Test Statistic                -6.659750e+00
p-value                        4.880941e-09
#Lags Used                     1.000000e+00
Number of Observations Used    1.180000e+02
Critical Value (1%)           -3.487022e+00
Critical Value (5%)           -2.886363e+00
Critical Value (10%)          -2.580009e+00
dtype: float64
医药生物 平稳√
Test Statistic                -9.549655e+00
p-value                        2.592398e-16
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
食品饮料
Test Statistic                -1.096015e+01
p-value                        8.366224e-20
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
有色金属 平稳√
Test Statistic                -8.636485e+00
p-value                        5.572907e-14
#Lags Used                     1.000000e+00
Number of Observations Used    1.180000e+02
Critical Value (1%)           -3.487022e+00
Critical Value (5%)           -2.886363e+00
Critical Value (10%)          -2.580009e+00
dtype: float64
钢铁 平稳√
Test Statistic                  -5.012623
p-value                          0.000021
#Lags Used                       2.000000
Number of Observations Used    117.000000
Critical Value (1%)             -3.487517
Critical Value (5%)             -2.886578
Critical Value (10%)            -2.580124
dtype: float64
国防军工 平稳√
Test Statistic                -9.011876e+00
p-value                        6.094787e-15
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
建筑材料
Test Statistic                -1.055267e+01
p-value                        8.100005e-19
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
公用事业
Test Statistic                  -3.181954
p-value                          0.021053
#Lags Used                       3.000000
Number of Observations Used    116.000000
Critical Value (1%)             -3.488022
Critical Value (5%)             -2.886797
Critical Value (10%)            -2.580241
dtype: float64
综合 平稳√
Test Statistic                -9.271716e+00
p-value                        1.321364e-15
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
农林牧渔 平稳√
Test Statistic                -5.929155e+00
p-value                        2.403552e-07
#Lags Used                     2.000000e+00
Number of Observations Used    1.170000e+02
Critical Value (1%)           -3.487517e+00
Critical Value (5%)           -2.886578e+00
Critical Value (10%)          -2.580124e+00
dtype: float64
计算机
Test Statistic                -1.010187e+01
p-value                        1.054277e-17
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
采掘 平稳√
Test Statistic                -9.692568e+00
p-value                        1.126254e-16
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
交通运输 平稳√
Test Statistic                -8.889708e+00
p-value                        1.252108e-14
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
商业贸易 平稳√
Test Statistic                -5.925572e+00
p-value                        2.448332e-07
#Lags Used                     1.000000e+00
Number of Observations Used    1.180000e+02
Critical Value (1%)           -3.487022e+00
Critical Value (5%)           -2.886363e+00
Critical Value (10%)          -2.580009e+00
dtype: float64
传媒
Test Statistic                  -1.820965
p-value                          0.370104
#Lags Used                       7.000000
Number of Observations Used    112.000000
Critical Value (1%)             -3.490131
Critical Value (5%)             -2.887712
Critical Value (10%)            -2.580730
dtype: float64
建筑装饰 平稳√
Test Statistic                -8.592502e+00
p-value                        7.222464e-14
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
电气设备 平稳√
Test Statistic                -9.520093e+00
p-value                        3.081407e-16
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
轻工制造 平稳√
Test Statistic                -9.731649e+00
p-value                        8.971365e-17
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
休闲服务
Test Statistic                -1.094894e+01
p-value                        8.898993e-20
#Lags Used                     0.000000e+00
Number of Observations Used    1.190000e+02
Critical Value (1%)           -3.486535e+00
Critical Value (5%)           -2.886151e+00
Critical Value (10%)          -2.579896e+00
dtype: float64
纺织服装 平稳√
Test Statistic                  -3.741765
p-value                          0.003563
#Lags Used                       3.000000
Number of Observations Used    116.000000
Critical Value (1%)             -3.488022
Critical Value (5%)             -2.886797
Critical Value (10%)            -2.580241
dtype: float64
'''