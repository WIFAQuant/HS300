#%% [markdown]
# # HS300指数纯因子组合构建
# 
# > WIFA量化组，2019年春。
# 
# 依据多因子模型，尝试对沪深300指数构建纯因子组合。
# 
# # Step 1：因子数据库构建
# 
# > 数据来源为万德金融数据库，通过WindPy API获取。
# 
# 因子数据分为*风格因子*和*风险因子*。
# 
# 其中风格因子又分为大类因子和细分类因子，最终风格因子会由细分类因子合成。
# 
# 风格因子共选取以下7个大类中的19个因子：
# 
# - VALUE：EPS_TTM/P、BPS_LR/P、CFPS_TTM/P、SP_TTM/P 
# - GROWTH：NetProfit_SQ_YOY、Sales_SQ_YOY、ROE_SQ_YOY 
# - PROFIT：ROE_TTM、ROA_TTM 
# - QUALITY：Debt2Asset、AssetTurnover、InvTurnover 
# - MOMENTUM：Ret1M、Ret3M、Ret6M 
# - VOLATILITY：RealizedVol_3M、RealizedVol_6M 
# - LIQUIDITY：Turnover_ave_1M、Turnover_ave_3M 
# 
# 风险因子选取以下2个大类中的2个因子：
# 
# - INDUSTRY：中信一级行业 
# - SIZE：Ln_MarketValue 
# 
# 由于数据限制和平台选择，最终确定的因子和最初选取的因子比较如下：
# 
# 最初选取因子|最终确定因子
# :--:|:--:
# EPS_TTM/P|PE_TTM
# BPS_LR/P|PB_LYR
# CFPS_TTM/P|PCF_NCF_TTM
# SP_TTM/P|PS_TTM
# NetProfit_SQ_YOY|YOYPROFIT
# Sales_SQ_YOY|YOY_OR
# ROE_SQ_YOY|YOYROE
# ROE_TTM|ROE_TTM
# ROA_TTM|ROA_TTM
# Debt2Asset|DEBTTOASSETS
# AssetTurnover|ASSETSTURN
# InvTurnover|INVTURN
# Ret1M|PCT_CHG
# Ret3M|PCT_CHG
# Ret6M|PCT_CHG
# RealizedVol_3M|UNDERLYINGHISVOL_90D
# RealizedVol_6M|UNDERLYINGHISVOL_90D
# Turnover_ave_1M|TECH_TURNOVERRATE20
# Turnover_ave_3M|TECH_TURNOVERRATE60
# 中信一级行业列表|INDUSTRY_SW
# Ln_MarketValue|VAL_LNMV
# 
# > 其中“最终确定因子”即为其万德指标字段名。

#%%
import os             # for getting working directory.
path = os.getcwd()    # current working directory.
import pandas as pd   # for wrapping csv file.
import numpy as np    # for numerical manipulation.
import seaborn as sns # for plotting.
sns.set(style = "darkgrid")
import matplotlib.pyplot as plt

#%%
# Import Wind Module for getting data.
import WindPy as w
from WindPy import *
w.start()

#%%
# Getting the stock list of HS300.
hs300_stocks_list = list(w.wset(
    "sectorconstituent", 
    "date=2019-02-20;windcode=000300.SH", # base on recent date.
    usedf = True
)[1]['wind_code'])

#%%
# The factor list stores the factor string I need.
factor_list = [
    "pe_ttm", 
    "pb_lyr", 
    "pcf_ncf_ttm", 
    "ps_ttm", 
    "yoyprofit",
    "yoy_or", 
    "yoyroe", 
    "roe_ttm", 
    "roa_ttm", 
    "debttoassets", 
    "assetsturn", 
    "invturn",  
    "pct_chg", 
    "underlyinghisvol_90d", 
    "tech_turnoverrate20", 
    "tech_turnoverrate60", 
    "tech_turnoverrate120", 
    "val_lnmv"
]

#%%
def data_fetching_and_storing(
    start = "2005-01-01", 
    end = "2019-02-20"
):
    # Import data from wind and store it as csv.
    for factor in factor_list:
        factor_data = w.wsd(
            hs300_stocks_list, 
            factor, 
            start, 
            end, 
            "Period=M", 
            usedf = True # use pandas dataframe.
        )[1]             # the result is a tuple with the [1] part is what we need.
        # Make a new directory (H3 Data) for storing data.
        file_path = path + "\\H3 Data\\" + factor + ".csv" # name the data file by it's factor string.
        factor_data.to_csv(file_path)                      # store data.

#%%
data_fetching_and_storing()

#%%
def sw_industry_data_fetching_and_storing():
    industry_sw = w.wsd(
        hs300_stocks_list, 
        "industry_sw", 
        "2019-02-20", 
        "2019-02-20", # set the start and end date as the same.
        "industryType=1;Period=M",
        usedf = True 
    )[1]
    file_path = path + "\\H3 Data\\industry_sw.csv"
    industry_sw.to_csv(file_path)

#%%
sw_industry_data_fetching_and_storing()

#%% [markdown]
# 数据保存在“H3 Data” ("HS300 Data" 的缩写) 文件夹中，格式为CSV，直接用全小写的万德指标名命名。
# 
# 数据格式如下：
# - index: 日期（YYYYMMDD）。(numpy.int64)
# - columns: 股票代号（XXXXXX.XX）。(str)
# 
# > 即 "<万德指标名>.csv"，如 "pe_ttm.csv"
# # Step 2：因子数据处理
# 
# 对因子数据进行处理

#%%
def get_data(factor_name): # get data from disk.
    '''
    Parameter:
        factor_name: name of factors in Wind. (str)
    Return:
        factor data. (pd.DataFrame)
            index: months. (np.int64)
            columns: stocks code list. (str)
    '''
    return pd.read_csv(
        open(
            path + "\\H3 Data\\" + factor_name + ".csv", 
            'r', # read-only mode for data protection.
            encoding = "utf-8"
        ), 
        index_col = [0]
    )

#%%
# Get an overview of the data.
def overview(factor_name):
    '''
    Parameter:
        factor_name: name of factors in Wind. (str)
    Return:
        kernel density estimation of factor data.
    '''
    data = get_data(factor_name)
    # Collect all non-nan value into data_list.
    data_list = []
    for i in range(len(data.columns)): # is there a way to avoid loop?
        data_list += data.iloc[:, i].dropna().tolist()
    sns.distplot(
        data_list, 
        hist = False, 
        rug = True
    )
    plt.title(factor_name)

#%% [markdown]
# 过大或过小的数据会影响到统计分析的结果，所以需要对离群值和极值进行处理。

#%%
plt.figure(figsize = (10, 10))
for i in range(9):
    plt.subplot(int("33" + str(i+1)))
    overview(factor_list[i])
plt.savefig(path + "\\H3 Plots\\overview.png")

#%% [markdown]
# ## 2.1 Filter Extreme Value.
# ## 2.2 Fill Missing Value.

#%%
class Filter_and_Fill(object):
    '''
    Parameters:

    '''
    def __init__(self, factor_name):
        data = get_data(factor_name)
        data.fillna(method = 'ffill', inplace = True) # forward-fill nan.
        data.fillna(method = 'bfill', inplace = True) # back-fill remained nan.
        self.data = data
    
    def median_absolute_deviation(self, n = 3):
        median = np.percentile(self.data, 50) # the 50 percentile of the factor.
        new_median = np.percentile(
            abs(self.data - median), 
            50
        )
        min_range = median - n * new_median
        max_range = median + n * new_median
        return np.clip(self.data, min_range, max_range)
    
    def three_sigma(self, n = 3):
        min_range = self.data.mean() - n * self.data.std()
        max_range = self.data.mean() + n * self.data.std()
        return self.data.clip(min_range, max_range, axis = 1)

#%%
# e.g. using three sigma and forward fill to clean assetsturn data.
Filter_and_Fill("assetsturn").three_sigma()

#%% [markdown]
# ## Risk Factors Neutralization.

#%%
