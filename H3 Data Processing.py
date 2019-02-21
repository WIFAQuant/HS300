#%% [markdown]
# Data Process

#%%
import os           # for getting working directory.
import pandas as pd # for wrapping csv file.
path = os.getcwd()  # current working directory.

#%%
# Import Wind Module for getting data.
import WindPy as w
from WindPy import *
w.start()

#%%
def data_fetching_and_storing(
    start = "2005-01-01", 
    end = "2019-02-20"
):
    # Getting the stock list of HS300 on end date.
    hs300_stocks_list = list(w.wset(
        "sectorconstituent", 
        "date="+end+";windcode=000300.SH", 
        usedf = True
    )[1]['wind_code'])
    # The factor list stores the factor string I need.
    factor_list = [
        "yoyprofit", 
        "ps_ttm"
        "return_1m", 
        "pct_chg", 
        "underlyinghisvol_90d", 
        "tech_turnoverrate20", 
        "tech_turnoverrate60", 
        "tech_turnoverrate120", 
        "val_lnmv"
    ]
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
zxyj_industry = w.wset(
    "sectorconstituent",
    "date=2019-02-21;sectorid=a39901012e000000", 
    usedf = True
)[1]
file_path = path + "\\H3 Data\\zxyj_industry.csv"
zxyj_industry.to_csv(file_path)