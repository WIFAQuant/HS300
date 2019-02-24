# 沪深300指数纯因子组合构建

> WIFA量化组，2019年春。

依据多因子模型，尝试对沪深300指数构建纯因子组合。

# Step 1：因子数据库构建

因子数据分为**风格因子**和**风险因子**。

其中风格因子又分为大类因子和细分类因子，最终风格因子会由细分类因子合成。

风格因子共选取以下7个大类中的19个因子：

- VALUE：EPS_TTM/P、BPS_LR/P、CFPS_TTM/P、SP_TTM/P 
- GROWTH：NetProfit_SQ_YOY、Sales_SQ_YOY、ROE_SQ_YOY 
- PROFIT：ROE_TTM、ROA_TTM 
- QUALITY：Debt2Asset、AssetTurnover、InvTurnover 
- MOMENTUM：Ret1M、Ret3M、Ret6M 
- VOLATILITY：RealizedVol_3M、RealizedVol_6M 
- LIQUIDITY：Turnover_ave_1M、Turnover_ave_3M 

风险因子选取以下2个大类中的2个因子：

- INDUSTRY：中信一级行业 
- SIZE：Ln_MarketValue 

由于数据限制和平台选择，最终确定的因子和最初选取的因子比较如下：

最初选取因子|最终确定因子
:--:|:--:
EPS_TTM/P|PE_TTM
BPS_LR/P|PB_LYR
CFPS_TTM/P|PCF_NCF_TTM
SP_TTM/P|PS_TTM
NetProfit_SQ_YOY|YOYPROFIT
Sales_SQ_YOY|YOY_OR
ROE_SQ_YOY|YOYROE
ROE_TTM|ROE_TTM
ROA_TTM|ROA_TTM
Debt2Asset|DEBTTOASSETS
AssetTurnover|ASSETSTURN
InvTurnover|INVTURN
Ret1M|PCT_CHG
Ret3M|PCT_CHG
Ret6M|PCT_CHG
RealizedVol_3M|UNDERLYINGHISVOL_90D
RealizedVol_6M|UNDERLYINGHISVOL_90D
Turnover_ave_1M|TECH_TURNOVERRATE20
Turnover_ave_3M|TECH_TURNOVERRATE60
中信一级行业列表|INDUSTRY_SW
Ln_MarketValue|VAL_LNMV

> 数据来源为万德金融数据库，通过WindPy API获取。
>
> 获取与存储数据的代码详见“H3 Data Fetching and Storing.py” 文件。
> 
> 其中“最终确定因子”列即为其万德指标字段名。
>
> 数据保存在“H3 Data” ("HS300 Data" 的缩写) 文件夹中，格式为CSV，直接用全小写的万德指标名命名。
> 即 "<万德指标名>.csv"，如 "pe_ttm.csv"
> 
> 数据格式如下：
> 行/列 | 股票代号（000001.SZ）
>  :--|--:
>  交易日期（YYYYMMDD） | 相应因子暴露


# Step 2：因子数据处理

> 对因子数据进行处理。

如图为任取9个因子的沪深300的暴露数据在2005~2018年分布统计图。👇

![overview.png](https://storage.live.com/items/A3FA4B9C0717EA26!53613?authkey=AH5Re-C6ttiO_oc)

从图中可以看出绝大多数因子都存在极差过大、分布不均的现象。
而过大或过小的数据会影响到统计分析的结果，所以需要对离群值和极值进行处理。

## 2.1 去极值

去极值的方法采用调整因子值中的离群值至指定阈值的上下限，从而减小离群值对统计的偏差。

离群值的阈值上下限定义的方法主要有三种：

1. MAD法
2. 3σ法
3. 百分位法

### 2.1.1 MAD法 (Median Absolute Deviation)

取因子的中位数，加减每个因子与该中位数的绝对偏差值的中位数乘上给定参数（此处经过调参设定默认为100倍）得到上下阈值。

经过MAD法去极值后的因子数据概览如下：

![MAD.png](https://storage.live.com/items/A3FA4B9C0717EA26!53689?authkey=AH5Re-C6ttiO_oc)

### 2.1.2 3σ法

取所有因子数据的标准差（即σ），偏离平均值给定参数（此处默认为三倍）标准差处设为上下阈值。

经过3σ法去极值后的因子数据概览如下：

![3σ.png](https://storage.live.com/items/A3FA4B9C0717EA26!53690?authkey=AH5Re-C6ttiO_oc)

### 2.1.3 百分位法

取给定百分位作为上下阈值。（此处经过调参设定为下限1.5%，上限98.5%分位点）

经过百分位法去极值后的因子数据概览如下：

![percentile.png](https://storage.live.com/items/A3FA4B9C0717EA26!53691?authkey=AH5Re-C6ttiO_oc)

### 2.1.4 去极值研究。

实际上，即使经过调参尽可能地使三种主流的去极值方法的结果互相接近，并不至于出现过于集中的阈值，仍然有可能出现非常显著不同的效果。

以每股现金流为例，将原始数据和三种去极值的方法处理后的因子数据放在同一张图里，由于值域相差太大，甚至根本无法从图中找到不同的方法对应的图表。（如下图：分别采用三种去极值方法处理后的每股现金流数据与其原始数据图👇）

![Comparison(pcf_ncf_ttm).png](https://i.loli.net/2019/02/24/5c7215995823d.png)

究其原因，是其原始数据的集中度就非常高，以至于不同方法去极值计算出相差甚远的阈值。（如下图：全部A股样本期内每股现金流的密度分布图👇）

![original pcf_ncf_ttm.png](https://storage.live.com/items/A3FA4B9C0717EA26!53692?authkey=AH5Re-C6ttiO_oc)

所以经过百分位去极值后，尽管值域缩小了近6000倍，但仍然非常集中。

另外，这种离差过大的数据去极值的时候还会出现一个问题：造成阈值部分出现异常高的“虚假”数据，而这也是我们不愿意看到的。（如下图：每股现金流经过约束最严格的百分位去极值处理后的分布图👇）

![percentile filter pcf_ncf_ttm.png](https://storage.live.com/items/A3FA4B9C0717EA26!53693?authkey=AH5Re-C6ttiO_oc)

> 注意图中 [-1000, 1000] 处异常的“突起”。
> 
> 这是由于过多超出上下阈值的数据被迫调整为上下阈值，导致阈值处的数据分布特别密集。

但在大多数情况下（数据分布相对均匀时，此处以ROE为例），各种方法与原始数据相差不大。（如下图：ROE数据的原始数据及分别经过三种去极值方法处理后的分布图👇）

![Comparison(roe_ttm).png](https://i.loli.net/2019/02/24/5c72160804bbb.png)

## 2.2 填补缺失值

