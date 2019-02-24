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
    # "tech_turnoverrate120", 
    # "val_lnmv"
    # The last 5 data haven't been downloaded yet for quota exceeded.
]

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
get_processed_data("roe_ttm").head()

#%%
