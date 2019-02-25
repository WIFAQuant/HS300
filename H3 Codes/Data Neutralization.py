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
import math
from statsmodels import regression
import statsmodels.api as sm

#%%
def get_factor_list():
    '''
    Return:
        factor list. (list)
    '''
    # The factor list stores the factor string I need.
    return [
        "pe_ttm", 
        "pb_lyr", 
        "pcf_ncf_ttm", 
        "ps_ttm", 
        "yoyprofit",
        "yoy_or", 
        "yoyroe", 
        # "roe_ttm",  # weired
        # "roa_ttm",  # weired
        "debttoassets", 
        "assetsturn", 
        "invturn",  
        "pct_chg", 
        # "underlyinghisvol_90d", 
        # "tech_turnoverrate20", 
        # "tech_turnoverrate60", 
        # "val_lnmv"
        # The last 4 data haven't been downloaded yet for quota exceeded.
    ]

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
            # Extract raw data.
            path + "\\H3 Data\\Raw Data\\" + factor_name + ".csv", 
            'r', # read-only mode for data protection.
            encoding = "utf-8"
        ), 
        index_col = [0]
    )
    # Forward-fill nan to make quarter report fill the month.
    data.fillna(method = 'ffill', inplace = True) 
    return data

#%%
def get_processed_data(factor_name): # get data from disk.
    '''
    Parameter:
        factor_name: name of factors in Wind. (str)
    Return:
        processed factor data. (pd.DataFrame)
            index: months. (np.int64)
            columns: stocks code list. (str)
    '''
    data = pd.read_csv(
        open(
            # Extract raw data.
            path + "\\H3 Data\\Processed Data\\" + factor_name + ".csv", 
            'r', # read-only mode for data protection.
            encoding = "utf-8"
        ), 
        index_col = [0]
    )
    return data

#%%
def get_industry_data():
    '''
    Return:
        SHENWAN industry data. (pd.DataFrame)      
    '''
    return get_processed_data("industry_sw")

#%%
def get_industry_list():
    '''
    Return:
        industry list in HS300 stocks list.
    '''
    return list(get_industry_data().iloc[:, 0].unique())

#%%
def industry_comparison(factor_name):
    '''
    Parameter:
        factor_name: name of factors in Wind. (str)
    Return:
        average factor value of each industries. (pd.DataFrame)
            index: industry. (str)
            columns: factor name. (str)
    '''
    # All industry in HS300.
    sw_industry_list = get_industry_list()
    # Use certain factor data for comparison example between industry.
    compare_data = get_data(factor_name)
    compare_industry = pd.DataFrame(
        index = sw_industry_list, 
        columns = [factor_name]
    )
    for industry in sw_industry_list:
        industry_stock_code_list = list(get_data("industry_sw")[
            get_data("industry_sw").iloc[:, 0] == industry
        ].index)
        # Some industry is not in HS300. 
        try:
            industry_data = compare_data[industry_stock_code_list]
            compare_industry.loc[
                industry, factor_name
            ] = np.mean(np.mean(industry_data))
        except:
            continue
    compare_industry.dropna(inplace = True)
    return compare_industry

#%%
def plot_industry_comparison():
    '''
    Return:
        save a 2*2 plot of average factor of each industries, 
        which are all siginificantly different. 
    '''
    # Choose 4 factors that's significantly different among industries. 
    significant_comparison_industry_list = [
        "pcf_ncf_ttm", 
        "yoyprofit", 
        "yoyroe", 
        "invturn"
    ]
    plt.figure(figsize = (21, 18)) # it's a big plot.
    for i in range(len(significant_comparison_industry_list)):
        plot_data = industry_comparison(
            significant_comparison_industry_list[i]
        )
        plt.subplot(int("22" + str(i+1)))
        sns.barplot(
            x = plot_data.index, 
            y = significant_comparison_industry_list[i], 
            data = plot_data
        )
        plt.xticks(rotation = 60) # rotate to avoid overlap text.
        plt.title(
            significant_comparison_industry_list[i], 
            fontsize = 21
        )
    plt.suptitle(
        "沪深300中不同行业部分因子平均值比较", 
        fontsize = 36
    )
    plt.savefig(path + "\\H3 Plots\\Industry Comparison.png")

#%%
# plot_industry_comparison()

#%%
# print(round(
#     industry_comparison("pcf_ncf_ttm").loc["有色金属", "pcf_ncf_ttm"] /  
#     industry_comparison("pcf_ncf_ttm").loc["家用电器", "pcf_ncf_ttm"] , 
#     0
# ))

#%%
# get_industry_data()

#%%
def get_industry_exposure(factor_name):
    '''
    Parameter:
        factor_name: name of factors in Wind. (str)
    Return:
        industry exposure data. (pd.DataFrame)
    '''
    file_path = path + "\\H3 Data\\Neutralized Data\\industry exposure " + factor_name + ".csv"
    if os.path.isfile(file_path):
        industry_exposure = pd.read_csv(
            open(
                file_path, 
                'r', 
                encoding = "utf-8"
            ), 
            index_col = [0]
        )
    else:
        # Don't know why but different factor data has different hs300 stocks list, 
        # so specify which factor is essential.
        hs300_stock_list = list(get_data(factor_name).columns)
        industry_exposure = pd.DataFrame(
            index = get_industry_list(), 
            columns = hs300_stock_list
        )
        for stock in hs300_stock_list:
            try:
                industry_exposure.loc[
                    get_industry_data().loc[
                        stock, 
                        "INDUSTRY_SW"
                    ], 
                    stock
                ] = 1
            except:
                continue
        industry_exposure.fillna(0, inplace = True)
        industry_exposure.to_csv(file_path)
    return industry_exposure

#%%
# get_industry_exposure()

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
def neutralize(
    factor_name, 
    market_capital = True, 
    industry = True
):
    '''
    Parameters:
        factor_name: name of factors in Wind. (str)
        market_capital: whether market-capital-neutralize or not. (bool)
        industry: whether industry-neutralize or not. (bool)
    Return:
        neutralized data. (pd.DataFrame)
    '''
    y = get_processed_data(factor_name).T.fillna(0) # don't know why but there's still nan.
    industry_dummy = get_industry_exposure(factor_name)
    if market_capital:
        ln_market_capital = get_data("val_lnmv")
        if industry:
            x = pd.concat(
                [
                    ln_market_capital, 
                    industry_dummy
                ], 
                axis = 1
            )
        else:
            x = ln_market_capital
    elif industry:
        x = industry_dummy.T
    result = sm.OLS(
        y.astype(float), 
        x.astype(float)
    ).fit()
    return result.resid.T

#%%
def plot_industry_neutralization(factor_name):
    '''
    Return: 
        a plot of neutralization comparison.
    '''
    plt.figure(figsize = (8, 5))
    sns.kdeplot(get_values(
        data = get_processed_data(factor_name)
    ), label = "未经中性化")
    sns.kdeplot(get_values(
        data = neutralize(
            factor_name, 
            market_capital = False, 
            industry = True
        )
    ), label = "行业中性化")
    plt.legend()
    plt.title("对" + factor_name + "进行中性化处理前后比较")

#%%
def overview_neutralization(factor_list):
    '''
    Parameter:
        factor_list: list of factor names. (list)
    Return:
        save a 2*2 plot of neutralization comparison.
    '''
    factor_list = factor_list
    plt.figure(figsize = (10, 10))
    for i in range(len(factor_list)):
        plt.subplot(int("22" + str(i+1)))
        sns.kdeplot(get_values(
            data = get_processed_data(factor_list[i])
        ), label = "未经中性化")
        sns.kdeplot(get_values(
            data = neutralize(
                factor_list[i], 
                market_capital = False, 
                industry = True
            )
        ), label = "行业中性化")
        plt.legend()
        plt.title("对" + factor_list[i] + "进行中性化处理前后比较")
    plt.suptitle("行业中性化的典型结果")
    plt.savefig(path + "\\H3 Plots\\overview neutralization.png")

#%%
# overview_neutralization([
#     "pb_lyr", 
#     "debttoassets", 
#     "assetsturn", 
#     "invturn"
# ])

#%%
def neutralize_and_store_data():
    '''
    Return:
        save industry neutralized data in 
        "\\H3 Data\\Neutralized Data\\".
    '''
    for factor in get_factor_list():
        file_path = path + "\\H3 Data\\Neutralized Data\\" + factor + ".csv"
        neutralized_data = neutralize(
            factor, 
            market_capital = False, 
            industry = True
        )
        neutralized_data.to_csv(file_path)

#%%
neutralize_and_store_data()

#%%
def get_neutralized_data(factor_name):
    '''
    Parameter:
        factor_name: name of factors in Wind. (str)
    Return:
        neutralized factor data. (pd.DataFrame)
            index: months. (np.int64)
            columns: stocks code list. (str)
    '''
    data = pd.read_csv(
        open(
            path + "\\H3 Data\\Neutralized Data\\" + factor_name + ".csv", 
            'r', # read-only mode for data protection.
            encoding = "utf-8"
        ), 
        index_col = [0]
    )
    return data
