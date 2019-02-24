#%% [markdown]
# # HS300指数纯因子组合构建
# 
# # Step 1: Factor Database Building.

#%%
import os             # for getting working directory.
path = os.getcwd()    # current working directory.
import pandas as pd   # for wrapping csv file.
import numpy as np    # for numerical manipulation.
import seaborn as sns # for plotting.
sns.set(style = "darkgrid")

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
def data_fetching_and_storing(
    start = "2005-01-01", 
    end = "2019-02-20"
):
    # The factor list stores the factor string I need.
    factor_list = [
        # "pe_ttm", 
        # "pb_lyr", 
        # "pcf_ncf_ttm", 
        # "ps_ttm", 
        # "yoyprofit",
        #"yoy_or",
        #"yoyroe",
        #"roe_ttm",
        #"roa_ttm",
        #"debttoassets",
        #"assetsturn",
        #"invturn",
        #"pct_chg",
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
        file_path = path + "\\多因子\\HS300-master\\H3 Data\\" + factor + ".csv" # name the data file by it's factor string.
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
    file_path = path + "\\多因子\\HS300-master\\H3 Data\\\\industry_sw.csv"
    industry_sw.to_csv(file_path)

#%%
sw_industry_data_fetching_and_storing()

#%% [markdown]
# > Below are process to turn existing excel file into csv file.

#%%
# other_factors_excel_data = pd.ExcelFile(r"C:\\Users\\kaspe\\OneDrive\\Desktop\\Factors.xlsx")
# other_factor_list = other_factors_excel_data.sheet_names

#%%
# def convert_excel_to_csv():
#     for factor in other_factor_list:
#         factor_data = pd.read_excel(
#             r"C:\\Users\\kaspe\\OneDrive\\Desktop\\Factors.xlsx", 
#             sheet_name = factor, 
#             index_col = 0 # or pandas will create an index automatically.
#         )
#         file_path = path + "\\H3 Data\\" + factor + ".csv"
#         factor_data.to_csv(file_path)

#%%
# convert_excel_to_csv()

#%% [markdown]
# # Step 2: Factor Data Processing.

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
    df = pd.read_csv(
        open(
            path + "\\多因子\\HS300-master\\H3 Data\\" + factor_name + ".csv",
            'r', # read-only mode for data protection.
            encoding = "utf-8"
        ),
        index_col = [0]
    )
    df.index = pd.to_datetime(df.index).strftime('%Y%m%d')
    return df

#%%
# Get an overview of the data.
def overview(factor_name):
    '''
    Parameter:
        factor_name: name of factors in Wind. (str)
    Return:
        kernel density estimation of factor data.
    '''
    sns.distplot(
        get_data(factor_name).dropna().to_numpy().tolist()[0], 
        hist = False, 
        rug = True
    )#Single feature chart，not plot a (normed) histogram,draw a rugplot on the support axis

#%%
overview("pb_lyr")

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


##################################################################################################################
# STEP_3
def get_group_data(list):
    datadict = {}
    for i in list:
        df = get_data(i)# this should be the processed data
        datadict[i] = df
    panel = pd.Panel(datadict)
    return panel

class Large_factor_merge(object):
    '''
    Parameters:

    '''
    def __init__(self, Large_factor):
        if Large_factor == 'VALUE':
            list = ["pe_ttm","pb_lyr","pcf_ncf_ttm","ps_ttm"]
        elif Large_factor =='GROWTH':
            list = ["yoyprofit","yoy_or","yoyroe"]
        elif Large_factor =='PROFIT':
            list = ["roe_ttm","roa_ttm"]
        elif Large_factor == 'QUALITY':
            list = ["debttoassets","assetsturn","invturn"]
        elif Large_factor =='MOMENTUM':
            list = ['pct_chg']# This will be modified
        elif Large_factor =='VOLATILITY':
            list = ["underlyinghisvol_90d","tech_turnoverrate20"]
        elif Large_factor == 'LIQUIDITY':
            list = ["tech_turnoverrate60","tech_turnoverrate120"]
        data = get_group_data(list)
        self.data = data
        self.Large_factor = Large_factor
    # Define the following function for you can read clearly and can acquire the data of every step.
    def Caculate_IC(self):
        stock_return = get_data('pct_chg')# This will be modified
        datadict = {}
        for i in self.data.items:
            df = self.data[i]
            IC = pd.DataFrame(columns=['IC_monthly'],index = df.index[0:len(df)-1])
            IC_group = []
            for j in range(len(df)-1):
                cor = df.iloc[j].corr(stock_return.iloc[j+1])
                IC_group.append(cor)
            IC['IC_monthly'] = IC_group
            datadict[i] = IC
        IC_Large = pd.Panel(datadict)
        return IC_Large

    def Caculate_IR(self):
        IC_Large = self.Caculate_IC()
        weight_df = pd.DataFrame(columns=['weights'],index=self.data.items)
        weight = []
        for i in IC_Large.items:
            df = IC_Large[i]
            IR = df.iloc[-24:,0].mean()/df.iloc[-24:,0].std()
            weight.append(IR)
        weight = [x/sum(weight) for x in weight] #adjust the sum of weight to 1.0
        weight_df['weights'] = weight
        return weight_df

    def Factors_merge(self):
        weight = self.Caculate_IR()
        # I don't find more attribute for panel data for sum.
        Factors_sum = pd.DataFrame(0,columns=self.data.minor_axis,index=self.data.major_axis)
        for i in self.data.items:
            df = self.data[i]
            new_df = df*weight.loc[i,'weights']
            Factors_sum = Factors_sum +new_df
        return Factors_sum

Factor_dict = {}
for i in ['VALUE','GROWTH','PROFIT','QUALITY','MOMENTUM','VOLATILITY','LIQUIDITY']:
    Factor_data = Large_factor_merge(i).Factors_merge()
    Factor_dict[i] = Factor_data
Large_factor = pd.Panel(Factor_dict)
# when you want to use one factor,you can edit'Large_factor[the name of the factor]'


# ###############################################################################################################
# STEP 5
# 假设了之前很多回归的计算结果
from scipy.optimize import minimize
All_Factors = ['VALUE','GROWTH','PROFIT','QUALITY','MOMENTUM','VOLATILITY','LIQUIDITY','INDUSTRY','SIZE']
Factor_income =pd.DataFrame(-1+2*np.random.random((170,9)),columns=['VALUE','GROWTH','PROFIT','QUALITY','MOMENTUM','VOLATILITY','LIQUIDITY','INDUSTRY','SIZE'],
                            index = get_data('ps_ttm').index)
Stock_predict = pd.DataFrame(-0.1+np.random.random((300,1))/3,columns=['yeild_forecast'],index = get_data('ps_ttm').columns)
Factor_predict = pd.DataFrame(-0.1+np.random.random((300,9))/3,columns=['VALUE','GROWTH','PROFIT','QUALITY','MOMENTUM','VOLATILITY','LIQUIDITY','INDUSTRY','SIZE'],index = get_data('ps_ttm').columns)
#每只股票的在不同时间点的残差，可以等于实际的股票收益率-预测的股票收益率
Stock_Residual = pd.DataFrame(-0.1+np.random.random((170,300))/5,columns = get_data('ps_ttm').columns,index = get_data('ps_ttm').index)


class Portfolio_Optimization(object):
    def __init__(self, Target_factors ,time_window):
        self.Target_factors = Target_factors
        self.time_window = time_window

    def Factor_covariance(self):
        factors = Factor_income.iloc[-self.time_window:]
        Cov = np.cov(factors.values.T)
        return Cov

    # 预测残差风险这一部分很复杂，用到半衰期权重和贝叶斯收缩，和波动性调整，其实不约束风险时，不用计算此项，先把框架搭起来，
    # 后面计算组合的夏普比率要用到组合方差，就要用到残差风险，后续研究我们再仔细研究这一部分具体怎么算
    def Trait_risk_forecast(self):
        Res = pd.DataFrame(-0.1+np.random.random((300,300))/5)
        return Res

    def optimization(self):
        Cov = self.Factor_covariance()
        Res = self.Trait_risk_forecast()
        yeild_T_1 = Stock_predict

        #非线性规划
        x0 = np.random.rand(300)
        x0 /= sum(x0)
        Non_target_factors = list(set(All_Factors) ^ set(self.Target_factors))
        n = len(Non_target_factors)
        m = list(range(n))
        b = [0]*9
        b[0:n-1] = m
        # 此处我尝试了各种方法，用i遍历非目标纯因子然后生成条件，但是生成的条件在优化模型中没有被成功约束，最后只能全部写出来9个因子条件，
        # 对于目标纯因子，序数取的0，即条件是重复的非目标因子约束，这里的条件数据类型是tuple，tuple不能被增加，我试过先用list添加然后转为tuple,
        # 仍然没有被成功识别，如果有更简便的方法，欢迎提出
        # 最小化的函数
        func = lambda x: -(yeild_T_1 * np.mat(x).T).sum()[0]
        cons4 = ({'type': 'eq', 'fun': lambda x: x.sum() - 1},
                 {'type': 'ineq','fun': lambda x:(0.03-abs((Factor_predict[[Non_target_factors[b[0]]]]*np.mat(x).T).sum()[0]))},
                 {'type': 'ineq', 'fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[1]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq', 'fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[2]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq', 'fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[3]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq', 'fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[4]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[5]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[6]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[7]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[8]]]] * np.mat(x).T).sum()[0]))},
                 )
        # 如果要添加波动性约束，条件要改为以下，我写的是限制波动小于3%
        '''cons4 = ({'type': 'eq', 'fun': lambda x: x.sum() - 1},
                 {'type': 'ineq','fun': lambda x: (0.03 -((np.mat(Factor_predict).T*np.mat(x).T).T*Cov*(np.mat(Factor_predict).T*np.mat(x).T))[0,0]
                                    +(np.mat(x)*np.mat(Res)*np.mat(x).T))[0,0]},
                {'type': 'ineq', 'fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[0]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[1]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[2]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[3]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[4]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[5]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[6]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[7]]]] * np.mat(x).T).sum()[0]))},
                 {'type': 'ineq','fun': lambda x: (0.03 - abs((Factor_predict[[Non_target_factors[b[8]]]] * np.mat(x).T).sum()[0]))},
                 )'''
        c = (0,1)
        bnds = tuple([c]*300)#边界条件为0-1
        res = minimize(func, x0, method='SLSQP', constraints=cons4,bounds = bnds)
        Stock_weight = pd.DataFrame(res.x,columns=['Portfolio Weight'],index = Stock_predict.index)
        return  Stock_weight, -res.fun

# 目标纯因子为'VALUE','GROWTH','PROFIT'，使用历史时间段为过去32个月，仅对非目标纯因子偏离做约束条件，最大化收益，返回权重和组合收益
[Stock_weight,Portfolio_Return]= Portfolio_Optimization(['VALUE','GROWTH','PROFIT'],32).optimization()



