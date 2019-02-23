#%% [markdown]
# # HS300指数纯因子组合构建
# 
# > WIFA量化组，2019年春。

#%%
import os                                    # for getting working directory.
path = os.getcwd()                           # current working directory.
import pandas as pd                          # for wrapping csv file.
import numpy as np                           # for numerical manipulation.
import seaborn as sns                        # for plotting.
sns.set(style = "darkgrid")                  # set seaborn style.
import matplotlib.pyplot as plt              # specify "plt".
plt.rcParams['font.sans-serif'] = ['SimHei'] # For displaying chinese.
plt.rcParams['axes.unicode_minus']=False     # For displaying minus sign.

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
    # "underlyinghisvol_90d", 
    # "tech_turnoverrate20", 
    # "tech_turnoverrate60", 
    # "tech_turnoverrate120", 
    # "val_lnmv"
    # The last 5 data haven't been downloaded yet for quota exceeded.
]

#%% [markdown]
# # Step 2：Factor Data Processing.

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
        histogram distribution plot of factor data.
    '''
    data = get_data(factor_name)
    # Forward-fill nan to make quarter report fill the month.
    data.fillna(method = 'ffill', inplace = True) 
    # Collect all non-nan value into data_list.
    value_list = []
    for i in range(len(data.columns)): 
        # is there a way to avoid loop?
        value_list += data.iloc[:, i].dropna().tolist()
    sns.distplot(
        value_list, 
        # hist = False, 
        # rug = True
    )
    plt.title(factor_name)

#%%
# Get an overview of 9 of the factors histogram distribution plot.
plt.figure(figsize = (10, 10))
for i in range(9):
    plt.subplot(int("33" + str(i+1)))
    overview(factor_list[i])
plt.suptitle("不同因子在A股的历史数据分布")
plt.savefig(path + "\\H3 Plots\\overview.png")

#%% [markdown]
# ## 2.1 Filter Extreme Value.

#%%
class Filter(object):
    '''
    Parameters:
        factor_name: name of factors in Wind. (str)
    '''
    def __init__(self, factor_name):
        data = get_data(factor_name)
        data.fillna(method = 'ffill', inplace = True) 
        value_list = []
        for i in range(len(data.columns)):
            value_list += data.iloc[:, i].dropna().tolist()
        self.data = data
        self.values = value_list
    
    def median_absolute_deviation(self, n = 3):
        median = np.percentile(self.values, 50) # the 50 percentile of the factor.
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
# Get an overview of MAD method filtering.
plt.figure(figsize = (10, 10))
for i in range(9):
    plt.subplot(int("33" + str(i+1)))
    overview(factor_list[i])
plt.suptitle("不同因子在A股的历史数据分布")
plt.savefig(path + "\\H3 Plots\\overview.png")

#%% [markdown]
# ## Risk Factors Neutralization.

#%%
