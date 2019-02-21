#%%
import os
import pandas as pd
path = os.getcwd()

#%% [markdown]
# Experiment with converting Wind data into hdf5 and then use pandas to get back.

#%%
import WindPy as w
from WindPy import *
w.start()

#%%
start = "2005-01-01"
end = "2019-02-20"

hs300_stocks_list = list(w.wset(
    "sectorconstituent", 
    "date="+end+";windcode=000300.SH", 
    usedf = True
)[1]['wind_code'])

#%%
# yoyprofit.
yoyprofit = w.wsd(
    hs300_stocks_list, 
    "yoyprofit", 
    "2005-01-01", 
    "2019-02-20", 
    "Period=M", 
    usedf = True
)[1]
file_path = path + "\\H3 Data\\yoyprofit.csv"
yoyprofit.to_csv(file_path)

#%%
# ps_ttm
ps_ttm = w.wsd(
    hs300_stocks_list, 
    "ps_ttm", 
    "2005-01-01", 
    "2019-02-20", 
    "Period=M", 
    usedf = True
)[1]
file_path = path + "\\H3 Data\\ps_ttm.csv"
ps_ttm.to_csv(file_path)

#%%
factor_list = [
    "return_1m", 
    "pct_chg", 
    "underlyinghisvol_90d", 
    "tech_turnoverrate20", 
    "tech_turnoverrate60", 
    "tech_turnoverrate120", 
    "val_lnmv"
]

#%%
for factor in factor_list:
    factor_data = w.wsd(
        hs300_stocks_list, 
        factor, 
        start, 
        end, 
        "Period=M", 
        usedf = True
    )[1]
    file_path = path + "\\H3 Data\\" + factor + ".csv"
    factor_data.to_csv(file_path)

#%%
zxyj_industry = w.wset(
    "sectorconstituent",
    "date=2019-02-21;sectorid=a39901012e000000", 
    usedf = True
)[1]
file_path = path + "\\H3 Data\\zxyj_industry.csv"
zxyj_industry.to_csv(file_path)

#%%
