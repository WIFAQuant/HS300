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

最初选取因子|最终确定因子|因子解释
:--:|:--:|:--:
EPS_TTM/P|PE_TTM|市盈率
BPS_LR/P|PB_LYR|市净率
CFPS_TTM/P|PCF_NCF_TTM|市现率（现金净流量）
SP_TTM/P|PS_TTM|市销率
NetProfit_SQ_YOY|YOYPROFIT|净利润同比增长率
Sales_SQ_YOY|YOY_OR|营业收入同比增长率
ROE_SQ_YOY|YOYROE|净资产收益率同比增长率
ROE_TTM|ROE_TTM2|净资产收益率
ROA_TTM|ROA_TTM2|总资产净利率
Debt2Asset|DEBTTOASSETS|资产负债率
AssetTurnover|ASSETSTURN|总资产周转率
InvTurnover|INVTURN|存货周转率
Ret1M|PCT_CHG|涨跌幅
Ret3M|PCT_CHG|涨跌幅
Ret6M|PCT_CHG|涨跌幅
RealizedVol_3M|UNDERLYINGHISVOL_90D|90日历史波动率
RealizedVol_6M|UNDERLYINGHISVOL_90D|90日历史波动率
Turnover_ave_1M|TECH_TURNOVERRATE20|20日平均换手率
Turnover_ave_3M|TECH_TURNOVERRATE60|60日平均换手率
中信一级行业列表|INDUSTRY_SW|申万行业名称
Ln_MarketValue|VAL_LNMV|对数市值

> （注：Ret1M, Ret3M, Ret6M皆由PCT_CHG合成；RealizedVol_3M, RealizedVol_6M皆由UNDERLYINGHISVOL_90D代替。） 
>
> 数据来源为万德金融数据库，通过WindPy API获取。
> 
> 其中“最终确定因子”列即为其万德指标字段名。
>
> （数据保存在“H3 Data” ("HS300 Data" 的缩写) 文件夹中，格式为CSV，直接用全小写的万德指标名命名。
> 即 "<万德指标名>.csv"，如 "pe_ttm.csv"）
> 
> 获取的原始数据储存在"H3 Data/Raw Data"文件夹里。

数据格式如下：

行/列 | 股票代号（000001.SZ）
:--|--:
交易日期（YYYYMMDD） | 相应因子暴露


# Step 2：因子数据处理

> 对因子数据进行处理。

如图为任取9个因子的沪深300的暴露数据在2005~2018年分布统计图。👇

![overview.png](https://storage.live.com/items/A3FA4B9C0717EA26!53613?authkey=AH5Re-C6ttiO_oc)

从图中可以看出绝大多数因子都存在极差过大、分布不均的现象。
而过大或过小的数据会影响到统计分析的结果，所以需要对数据进行处理。

## 2.1 填补缺失值

由于万德输出的当季度财务数据只在报告期有数据，而在该季度的其他月份没有数据，所以针对这个现象采用“**向前填充**”来填补缺失值。

```Python3
data.fillna(method = 'ffill', inplace = True)
```

填补前：

![Pre Filled.png](https://storage.live.com/items/A3FA4B9C0717EA26!53793?authkey=AH5Re-C6ttiO_oc)

填补后：

![Filled.png](https://storage.live.com/items/A3FA4B9C0717EA26!53794?authkey=AH5Re-C6ttiO_oc)

针对剩余的缺失数据，我们将在数据[标准化](##2.3标准化)处理后统一填充为零。

## 2.2 去极值

去极值的方法采用调整因子值中的离群值至指定阈值的上下限，从而减小**离群值**和**极值**对统计的偏差。

离群值的阈值上下限定义的方法主要有三种：

1. MAD法
2. 3σ法
3. 百分位法

### 2.2.1 MAD法 (Median Absolute Deviation)

取因子的中位数，加减每个因子与该中位数的绝对偏差值的中位数乘上给定参数（此处经过调参设定默认为100倍）得到上下阈值。

经过MAD法去极值后的因子数据概览如下：

![MAD.png](https://storage.live.com/items/A3FA4B9C0717EA26!53689?authkey=AH5Re-C6ttiO_oc)

### 2.2.2 3σ法

取所有因子数据的标准差（即σ），偏离平均值给定参数（此处默认为三倍）标准差处设为上下阈值。

经过3σ法去极值后的因子数据概览如下：

![3σ.png](https://storage.live.com/items/A3FA4B9C0717EA26!53690?authkey=AH5Re-C6ttiO_oc)

### 2.2.3 百分位法

取给定百分位作为上下阈值。（此处经过调参设定为下限1.5%，上限98.5%分位点）

经过百分位法去极值后的因子数据概览如下：

![percentile.png](https://storage.live.com/items/A3FA4B9C0717EA26!53691?authkey=AH5Re-C6ttiO_oc)

### 2.2.4 去极值研究。

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

但在大多数情况下（数据分布相对均匀时，此处以ROE为例），各种方法以及原始数据相差不大。（如下图：资产周转率数据的原始数据及分别经过三种去极值方法处理后的分布图👇）

![Comparison(assetsturn).png](https://i.loli.net/2019/02/24/5c7290ae9f0be.png)

经过比较研究，我们最终选取阈值选取相对最为合理，较少阈值异常“突起”，同时保留较宽值域的**参数值为100的MAD法**进行去极值处理。

## 2.3 标准化

标准化处理数据的目的就是去除其**量纲**。

这样做可以使得：

- 数据更加集中
- 不同数据之间可以互相比较和进行回归等

主流的标准化的方法有两种：

标准化方法|原理|优点|缺点
:--|:--|:--:|:--:
对原始因子值标准化|减去均值后，除以标准差|保留更多信息|对数据分布有要求
对因子排序值标准化|因子排序值进行上述处理|适用性更广泛|非参数统计法

它们都能使得数据的：

- 均值为0
- 标准差为1

由于已经对数据进行去极值处理，我们最终选取对原始因子值进行标准化(z-score)的方法进行标准化。

> 2.1， 2.2， 2.3的数据处理部分的：
>
> 数据保存在"H3 Data/Processed Data"文件夹里。

（如下图为经过去极值、标准化处理后的数据密度分布图一览👇）

![Processed Data.png](https://i.loli.net/2019/02/24/5c7291ceea91d.png)

## 2.4 中性化

中性化的目的是剔除数据中多余的风险暴露。

根据某些因子（指标）选股的时候，由于某些因子之间具有较强的相关性，故时常会有我们不希望看到的“**偏向**”，导致投资组合不够**分散**。

例如以下四个指标：

- 市现率
- 净利润同比增长率
- 净资产收益率同比增长率
- 存货周转率

沪深300股票指数中共包含17个行业（根据申万一级行业分类），分别统计沪深300指数中各行业以上四个指标的平均值，结果如下图所示👇。

![Industry Comparison.png](https://i.loli.net/2019/02/24/5c72a95c76124.png)

从图中可以看到，不同行业的不同指标相差十倍、千倍乃至万倍都有。

> *有色金属行业的平均市现率是家用电器行业的负十八万倍。*

那么，依据市现率因子选取出的股票必然对平均市现率高的行业有偏向，而我们希望投资组合中的行业尽可能分散，故我们希望对行业进行中性化。（同理，我们也希望对市值进行中性化。）

中性化的主要做法就是通过回归得到一个与风险因子（行业因子、市值因子）**线性无关**的因子。（即线性回归后的残差项作为中性化后的新因子。）如此一来，中性化处理后的因子与风险因子之间的相关性就严格为零。

> 不过这样做中性化并不一定总能彻底地剔除因子的多余信息。因为线性回归要求两个前提假设：
> 
> - 因子之间线性相关
> - 残差正态独立同分布
>
> 而在因子数据中这两个假设都不一定成立。（例如在[2.2去极值](##2.2去极值)步骤中密度过高的阈值就对数据的分布造成了破坏）

但直观的说，根据[Brinson资产配置分析](https://www.investopedia.com/terms/a/attribution-analysis.asp)超额收益理论来看，如果投资组合中风险因子配置资产权重等于基准资产中其之权重，则做到了中性化。

此处简便起见，我们依然采用线性回归作为中性化的处理方法。

回归方式如下：

- 被解释变量：前述数据处理后的因子数据

- 解释变量：

  - 市值因子
  - 行业因子（作为指示变量）

最终回归方程的**残差**项即为中性化后的因子暴露。

（如下图，为选取四个因子指标进行行业中性化前后的结果，以展示中性化的一般结果👇，可以看出中性化导致分布更均匀、更接近均值）

![overview neutralization.png](https://i.loli.net/2019/02/25/5c73f9c1689f9.png)

> 数据处理中性化部分的：
>
> 数据保存在"H3 Data/Neutralized Data"文件夹里。

最终经过所有因子数据处理步骤之后，原来的因子数据分布图变为了这样。

（经过所有数据处理步骤后的因子数据密度分布图一览👇）

![overview after data processing.png](https://i.loli.net/2019/02/25/5c740407138d5.png)

可以看出数据经过处理后分布变得更加接近标准正态分布了一些。

# Step 3：大类因子合成

前面两个步骤已经把风格因子的细分类因子数据经过数据处理并保存了下来，这一步把细分类因子合成为大类因子。使得最终合成后只剩下：

- VALUE
- GROWTH
- PROFIT
- QUALITY
- VOLATILITY
- MOMENTUM
- LIQUIDITY

这七个因子，我们的目标就是构建这七个因子的**纯因子组合**。

> 从这一步开始为方便提取数据，将数据从"pandas.DataFrame"转换为"pandas.PanelData"。
>
> 数据格式为：
>
> - index: stock codes
> - factor names
>
> 可以用以下方法提取特定时间的所有因子的所有股票数据：
>
> ```Python3
> Large_factor.major_xs("20050131")
> ```

大类因子合成的方式是通过IC_IR加权合成。

> 大类因子合成部分的：
>
> - 代码详见“Data_Composition.py” 文件。
> - 数据保存在"H3 Data/Composition Data"文件夹里。

# Step 4：收益预测模型

### 多元线性回归
$$r_j^t = \sum_{k=1}^K X_{jk}^t*f_k^t+u_j^t$$

为解决异方差性，使用了WLS加权最小二乘法进行回归

### 估计因子预期收益 

由多元线性回归可以得到所有因子的历史收益率序列，使用历史数据估计T+1期因子预期收益率的方法有很多种。

此处采取历史均值法，N=12。（即采取前12个月的因子历史收益率均值作为T+1期因子的预期收益率）

$f_k^{T+1}=\dfrac{\sum_{t=T-N+1}T f_k^t}{N}$



### 计算股票预期收益

根据因子预期收益估计值$(f_1^{T+1},f_2^{T+1},f_3^{T+1}...f_K^{T+1})$与T期因子载荷矩阵$X^{T}$得到股票预期收益：

$r_j^{T+1}=\sum_{k=1}^K X_{jk}^{T}*f_k^{T+1}$

即可计算出T+1期个股的预期收益率 $(r_1^{T+1},r_2^{T+1},r_3^{T+1}...r_N^{T+1})$