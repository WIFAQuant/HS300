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
def industry_comparison(factor_name = "pb_lyr"):
    # All industry in HS300.
    sw_industry_data = get_processed_data("industry_sw")
    sw_industry_list = list(sw_industry_data.iloc[:, 0].unique())
    # Use certain factor data for comparison example between industry.
    compare_data = get_data(factor_name)
    compare_industry = pd.DataFrame(
        index = sw_industry_list, 
        columns = [factor_name]
    )
    for industry in sw_industry_list:
        industry_stock_code_list = list(sw_industry_data[
            sw_industry_data.iloc[:, 0] == industry
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
    significant_comparison_industry_list = [
        "pcf_ncf_ttm", 
        "yoyprofit", 
        "yoyroe", 
        "invturn"
    ]
    plt.figure(figsize = (21, 18))
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
        plt.xticks(rotation = 60)
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
plot_industry_comparison()

#%%
