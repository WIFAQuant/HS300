#%% [markdown]
# # HS300指数纯因子组合构建
# 
# > WIFA量化组，2019年春。
# 
# ## Step 2: Factor Database building.

#%%
import os           # for getting working directory.
path = os.getcwd()  # current working directory.
import pandas as pd # for wrapping csv file.

#%%
# Import Wind Module for getting data.
import WindPy as w
from WindPy import *
w.start()

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
        # "roe_ttm2", 
        # "roa_ttm2", 
        "debttoassets", 
        "assetsturn", 
        "invturn",  
        "pct_chg", 
        # "underlyinghisvol_90d", 
        # "tech_turnoverrate20", 
        # "tech_turnoverrate60", 
        # "industry_sw", 
        # "val_lnmv"
        # The last 5 data haven't been downloaded yet for quota exceeded.
    ]

#%%
def get_hs300_stocks_list():
    '''
    Return:
        hs300 stocks list. (pd.DataFrame)
    '''
    file_path = path + "\\H3 Data\\Raw Data\\hs300.csv"
    if os.path.isfile(file_path):
        hs300_data = pd.read_csv(
            open(
                file_path, 
                'r', 
                encoding = "utf-8"
            ), 
            index_col = [0]
        )
    else:
        # Getting the stock list of HS300.
        hs300_stocks_list = list(w.wset(
            "sectorconstituent", 
            "date=2019-02-20;windcode=000300.SH", # base on recent date.
            usedf = True
        )[1]['wind_code'])
        hs300_data = pd.DataFrame(
            data = hs300_stocks_list, 
            columns = ["HS300"]
        )
        hs300_data.to_csv(file_path)
    return list(hs300_data["HS300"])

#%%
get_hs300_stocks_list()

#%%
def data_fetching_and_storing(
    start = "2005-01-01", 
    end = "2019-02-20"
):
    '''
    Parameters:
        start: start date (YYYY-MM-DD). (str)
        end: end date (YYYY-MM-DD). (str)
    Return:
        save raw data to "\\H3 Data\\Raw Data\\" as csv.
    '''
    # Import data from wind and store it as csv.
    for factor in get_factor_list():
        factor_data = w.wsd(
            get_hs300_stocks_list(), 
            factor, 
            start, 
            end, 
            "Period=M", 
            usedf = True # use pandas dataframe.
        )[1]             # the result is a tuple with the [1] part is what we need.
        # Make a new directory (H3 Data) for storing data.
        file_path = path + "\\H3 Data\\Raw Data\\" + factor + ".csv" # name the data file by it's factor string.
        factor_data.to_csv(file_path)                      # store data.

#%%
data_fetching_and_storing()

#%%
def sw_industry_data_fetching_and_storing():
    '''
    Return:
        save SHENWAN industry data to "\\H3 Data\\Raw Data\\" as csv.
    '''
    industry_sw = w.wsd(
        get_hs300_stocks_list(), 
        "industry_sw", 
        "2019-02-20", 
        "2019-02-20", # set the start and end date as the same.
        "industryType=1;Period=M",
        usedf = True 
    )[1]
    file_path = path + "\\H3 Data\\Raw Data\\industry_sw.csv"
    industry_sw.to_csv(file_path)

#%%
sw_industry_data_fetching_and_storing()