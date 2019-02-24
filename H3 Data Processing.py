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
        forward-filled factor data. (pd.DataFrame)
            index: months. (np.int64)
            columns: stocks code list. (str)
    '''
    data = pd.read_csv(
        open(
            path + "\\H3 Data\\" + factor_name + ".csv", 
            'r', # read-only mode for data protection.
            encoding = "utf-8"
        ), 
        index_col = [0]
    )
    # Forward-fill nan to make quarter report fill the month.
    data.fillna(method = 'ffill', inplace = True) 
    return data

#%%
def get_values(data):
    '''
    Parameter:
        data: input data. (pd.DataFrame)
    Return:
        a list of all values in data except nan. (list)
    '''
    # Collect all non-nan value into data_list.
    value_list = []
    for i in range(len(data.columns)): 
        # is there a way to avoid loop?
        value_list += data.iloc[:, i].dropna().tolist()
    return value_list

#%%
# Get an overview of 9 of the factors histogram distribution plot.
plt.figure(figsize = (10, 10))
for i in range(9):
    plt.subplot(int("33" + str(i+1)))
    sns.distplot(get_values(
        data = get_data(factor_list[i])
    ))
    plt.title(factor_list[i])
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
        self.data = data
        self.values = get_values(
            data = data
        )
    
    def original(self):
        '''
        Return:
            original unfiltered data. (pd.DataFrame)
        '''
        return self.data
    
    def MAD(self, n = 100):
        '''
        Parameter:
            n: how many times new median. (int)
        Return:
            filtered data. (pd.DataFrame)
        '''
        median = np.percentile(self.values, 50)
        new_median = np.percentile(
            get_values(abs(self.data - median)), 50
        )
        min_range = median - n * new_median
        max_range = median + n * new_median
        return self.data.clip(min_range, max_range, axis = 1)
    
    def three_sigma(self, n = 3):
        '''
        Parameter:
            n: how many sigmas. (int)
        Return:
            filtered data. (pd.DataFrame)
        '''
        min_range = np.mean(self.values) - n * np.std(self.values)
        max_range = np.mean(self.values) + n * np.std(self.values)
        return self.data.clip(min_range, max_range, axis = 1)
    
    def percentile_filter(self, min = 1.5, max = 98.5):
        '''
        Parameters:
            min: minimum percentage. (float)
            max: maximum percentage. (float)
        Return:
            filtered data. (pd.DataFrame)
        '''
        min_range = np.percentile(self.values, min)
        max_range = np.percentile(self.values, max)
        return np.clip(self.data, min_range, max_range)

#%%
# Get an overview of MAD method filtering.
plt.figure(figsize = (10, 10))
for i in range(9):
    plt.subplot(int("33" + str(i+1)))
    sns.distplot(get_values(
        data = Filter(factor_list[i]).MAD()
    ))
    plt.title(factor_list[i])
plt.suptitle("绝对值差中位数法(MAD法)去极值后")
plt.savefig(path + "\\H3 Plots\\MAD.png")

#%%
# Get an overview of 3 sigma method filtering.
plt.figure(figsize = (10, 10))
for i in range(9):
    plt.subplot(int("33" + str(i+1)))
    sns.distplot(get_values(
        data = Filter(factor_list[i]).three_sigma()
    ))
    plt.title(factor_list[i])
plt.suptitle("3σ法去极值后")
plt.savefig(path + "\\H3 Plots\\3σ.png")

#%%
# Get an overview of percentile method filtering.
plt.figure(figsize = (10, 10))
for i in range(9):
    plt.subplot(int("33" + str(i+1)))
    sns.distplot(get_values(
        data = Filter(factor_list[i]).percentile_filter()
    ))
    plt.title(factor_list[i])
plt.suptitle("百分位法去极值后")
plt.savefig(path + "\\H3 Plots\\percentile.png")

#%%
plt.figure(figsize = (8, 5))
sns.distplot(get_values(
    data = Filter("pcf_ncf_ttm").original()
), label = "Percentile")
plt.legend()
plt.title("每股现金流：原始数据")
plt.savefig(path + "\\H3 Plots\\original pcf_ncf_ttm.png")

#%%
plt.figure(figsize = (8, 5))
sns.distplot(get_values(
    data = Filter("pcf_ncf_ttm").percentile_filter()
), label = "Percentile")
plt.legend()
plt.title("每股现金流：百分位去极值")
plt.savefig(path + "\\H3 Plots\\percentile filter pcf_ncf_ttm.png")

#%%
plt.figure(figsize = (8, 5))
sns.distplot(get_values(
    data = Filter("pcf_ncf_ttm").original()
), label = "Original")
sns.distplot(get_values(
    data = Filter("pcf_ncf_ttm").MAD()
), label = "MAD")
sns.distplot(get_values(
    data = Filter("pcf_ncf_ttm").three_sigma()
), label = "3σ")
sns.distplot(get_values(
    data = Filter("pcf_ncf_ttm").percentile_filter()
), label = "Percentile")
plt.legend()
plt.title("不同去极值方法的比较（以每股现金流为例）")
plt.savefig(path + "\\H3 Plots\\Comparison(pcf_ncf_ttm).png")

#%%
plt.figure(figsize = (8, 5))
sns.distplot(get_values(
    data = Filter("roe_ttm").original()
), label = "Original")
sns.distplot(get_values(
    data = Filter("roe_ttm").MAD()
), label = "MAD")
sns.distplot(get_values(
    data = Filter("roe_ttm").three_sigma()
), label = "3σ")
sns.distplot(get_values(
    data = Filter("roe_ttm").percentile_filter()
), label = "Percentile")
plt.legend()
plt.title("不同去极值方法的比较（以ROE为例）")
plt.savefig(path + "\\H3 Plots\\Comparison(roe_ttm).png")

#%%
