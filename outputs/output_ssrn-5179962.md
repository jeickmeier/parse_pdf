**Geopolitical skewness risk and bond returns**

Fuwei Jiangᵃ, Jie Kangᵇ*, Ruzheng Tianᵇ

**Abstract:** We propose FarmSkew, a novel measure of global geopolitical skewness risk, and examines its predictive power for U.S. Treasury bond returns. Using 44 country- (region-) specifical geopolitical risk indices and the Factor-Augmented Regularized Model (FARM), we decompose global geopolitical risks into common factors and idiosyncratic components, isolating skewness in predictive idiosyncratic risks. Empirically, FarmSkew significantly predicts excess bond returns across maturities, outperforming historical average benchmark and existing mean-level measures. Asset allocation exercises show that FarmSkew generates substantial portfolio gains for mean-variance investors. Its predictive power stems from forecasting declines in real economic activity and demand-driven disinflation shocks. FarmSkew also provides insights into interest rate expectation errors, credit spreads, and Treasury auction outcomes.

**Keywords:** Geopolitical risk; Bond return; Machine learning; Out-of-sample forecast; Asset allocation;

**JEL classification:** C53; G11; G12; G17.

---

ᵃ Xiamen University, Department of Finance at School of Economics, Wang Yanan Institute for Studies in Economics. Xiamen, CN 361005. E-mail addresses: jfuwei@gmail.com  
ᵇ Central University of Finance and Economics, China Economics and Management Academy, Beijing, CN 100081. E-mail addresses: kidmankong@163.com (Kang), 2022212461@email.cufe.edu.cn (Tian)  
* Corresponding author  

---

Alt-text: Title page of a research paper on geopolitical skewness risk and bond returns with author names and abstract.

1. Introduction

The predictability of bond risk premium is a long-standing topic in finance research, with significant implications for asset pricing, portfolio management, and monetary policy. While the Expectations Hypothesis and Liquidity Preference Theory suggest that bond returns are largely unpredictable, a growing body of literature has identified time-varying and predictable components in bond risk premia. These components are often linked to macroeconomic variables, term structure dynamics, and other risk factors. However, one open question in this literature is the role of geopolitical risk (GPR) in shaping bond market dynamics.

Geopolitical events—ranging from military conflicts and terrorist attacks to diplomatic tensions—exert profound effects on global financial markets by altering investor sentiment, risk appetite, and economic expectations. Existing literatures document that GPR influences asset prices and investment decisions across various markets, including equities, foreign exchange, and commodities. Yet, the impact of global geopolitical risks on bond markets, particularly in the context of higher-order moments such as skewness risk, remains largely underexplored. This paper fills this gap by introducing a novel measure of global geopolitical skewness risk (GPRS) from a broad set of country- (region-) specifical geopolitical risk (GPRC) indices with machine learning, and investigating its predictive power for U.S. Treasury bond returns.

There are three potential challenges for predicting bond returns with global geopolitical risks. First, even though one may naturally link GPR with bond market given that bonds, particularly U.S. Treasuries, are typically regarded as safe-haven assets during periods of heightened geopolitical uncertainty, the relationship between GPR and future bond returns is not likely to be straightforward. Geopolitical events can lead to flight-to-safety effects, which drive bond prices up and yields down. However, these effects could be transitory as the risk aversion sentiment caused by worldwide influential geopolitical events, such as 9/11 Attacks and the outbreak of Iraq War, should be quicky incorporated by Treasury prices as long as the market is at least weak efficient. Therefore, it might be unreliable to predict bond returns with widely perceived components of global geopolitical tensions from a safe asset perspective.

Second, traditional aggregate geopolitical risk indices primarily reflect the mean level of global geopolitical uncertainty, which fails to sufficiently depict tail risk. The general sense of overall risk environment might not fully capture heightened market stress, as it averages out the impact of extreme events. For example, during periods of relative calm, the mean level of geopolitical risk might be low, but the risk of sudden, severe events, such as terrorist attacks and military conflicts, could still be significant. Third, for the Treasury bond of a particular country, e.g. the United States, the forecasting power of global geopolitical risks can be sparse across countries (regions), and the candidate countries (regions) whose geopolitical risks contain predictive signals tend to be time-varying. This concern is reasonable, as the geopolitical impact of one country (region) to another country (region) should be dynamic according to the development of bilateral economic, trade, military, and diplomatic relations.

To address these issues, we employ 44 GPRC indies developed by Caldara and Iacoviello (2022) to construct a new measure of geopolitical skewness risk (GPSR) under the Factor-Augmented Regularized Model (FARM) framework proposed by Fan et al. (2020). The FARM framework is particularly well-suited for our analysis because it allows us to decompose the co-movement of geopolitical risks across countries into common global factors and country- (region-) specific idiosyncratic components. This decomposition is important because geopolitical risks in different countries (regions) can be highly correlated due to shared economic fundamentals and global trends. By isolating the idiosyncratic components, we can better capture the unique predictive information contained in country- (region-) specific geopolitical risks. Moreover, the FARM framework addresses the challenges of high dimensionality in global geopolitical risk data, which can complicate traditional regression analysis.

Specifically, our methodology involves three key steps. First, we use principal component analysis (PCA) to estimate the common global factors from geopolitical risks across 44 countries (regions). Second, we employ Elastic-net regression to select the idiosyncratic geopolitical risk (IGPR) components that historically predict U.S. Treasury bond returns. This step is critical because it allows us to focus on the most relevant geopolitical risks for bond market predictability, while filtering out noise and irrelevant information. Finally, we calculate the cross-sectional skewness of the selected IGPR components to construct our GPRS measure,

namely FarmSkew. This measure captures the asymmetry in the cross-sectional distribution of predictive IGPR components, providing a novel indicator of geopolitical skewness risk.

The empirical results of our study provide strong support for the predictive power of FarmSkew. In-sample regression analyses show that FarmSkew significantly predicts excess returns of U.S. Treasury bonds across different maturities, with economically meaningful slopes and high \(R^2\) values. For example, a one standard deviation increase in FarmSkew is associated with a 1.02% decrease in 3-year bond returns, a 1.73% decrease in 5-year bond returns, and a 2.83% decrease in 10-year bond returns. These results are robust to the inclusion of traditional yield curve factors and real-time macroeconomic predictors, suggesting that FarmSkew provides unique information beyond what is captured by existing models.

Out-of-sample forecasting exercises further confirm the predictive power of FarmSkew. Using an expanding window approach, we find that FarmSkew consistently outperforms the historical average benchmark, with out-of-sample \(R^2\) (\(R^2_{os}\)) values of 14.26%, 14.15%, and 11.19% for 3-year, 5-year, and 10-year bonds, respectively. These results are statistically significant at the 1% level, indicating that FarmSkew not only predicts bond returns in-sample but also delivers meaningful out-of-sample forecasts. Moreover, the economic value of FarmSkew is evident in asset allocation exercises, where a mean-variance investor using FarmSkew to forecast bond returns achieves substantial certainty equivalent return (CER) gains and manipulation-proof performance (MPP) improvements relative to the benchmark.

The economic intuition behind the predictive power of FarmSkew lies in its ability to capture both the expected and unexpected channels through which geopolitical risk affects bond markets. On the expected return channel, we find that FarmSkew predicts declines in real economic activity, such as reduced consumer spending, lower industrial production, and higher unemployment. These economic downturns increase the ex-ante risk premium required by investors, leading to higher bond returns. On the unexpected return channel, FarmSkew is associated with disinflation shocks, particularly those driven by demand-side factors. These shocks reduce inflation expectations and increase the real value of bond payoffs, further driving bond prices up and yields down. Together, these channels explain why FarmSkew is positively associated with future bond returns.

In addition to its predictive power for bond returns, FarmSkew also provides valuable

insights into other aspects of financial markets. For instance, we find that FarmSkew predicts interest rate expectation errors, particularly for short-term rates, suggesting that it captures investors’ biased beliefs about future monetary policy. Moreover, FarmSkew is positively associated with future credit spreads, indicating that it reflects concerns over debt deflation and default risk in corporate bond markets. Finally, we show that FarmSkew has explanatory power for the bid-to-cover ratio (BCR) in U.S. Treasury auctions, particularly for short-term Treasuries, highlighting its role in shaping market sentiment and investor behavior in the primary market.

Our study contributes to the literature in several important ways. First, to the best of our knowledge, we are the first to explore the predictive power of global geopolitical risks on U.S. Treasury bond returns, uncovering a previously overlooked dimension of bond market dynamics. By shifting the focus from traditional macroeconomic and financial factors to the asymmetric nature of geopolitical risks, we reveal how extreme geopolitical events—often underestimated by mean-level measures—is related with bond market movements. Second, we propose a novel approach to constructing cross-sectional distribution characteristics and emphasize the importance of skewness risk in financial markets. Using the FARM method, we filter out global trends to isolate idiosyncratic risks, offering a sharper lens through which to view the predictive power of geopolitical skewness. Third, we provide compelling evidence of global risk spillover, demonstrating how international geopolitical shocks ripple through to the U.S. Treasury market. This underscores the interconnectedness of global financial markets and highlights the importance of incorporating international geopolitical developments into local financial market analysis. Together, these contributions advance our understanding of bond return predictability and offer practical tools for investors navigating an increasingly uncertain global landscape.

The remainder of the paper is organized as follows. Section 2 reviews the literature on bond return predictability and geopolitical risk. Section 3 details the data and construction of FarmSkew. Section 4 evaluates the predictive power of and economic value FarmSkew. Section 5 explores the economic mechanisms linking FarmSkew to bond returns. Section 6 extends the analysis by examining the relationship between FarmSkew and other financial market variables, Section 7 concludes the paper.

2. Literature review

Predicting Treasury bond returns and risk premia has been a central topic in finance research. The foundational theories of the term structure of interest rates, notably the Expectations Hypothesis and the Liquidity Preference Theory, maintain that bond returns exhibit unpredictability. According to these theoretical frameworks, the expected excess holding returns on long-term bonds demonstrate no time variation, implying that historical means serve as the most efficient predictor of future returns. The academic literature has identified numerous variables indicating that the risk premium required for holding Treasury bonds contains a time-varying and predictable component. One strand of research focuses on predictive information within the term structure of interest rates, including forward spreads (Fama and Bliss, 1987; Fama, 2006), yield spreads (Keim and Stambaugh, 1986; Campbell and Shiller, 1991), and forward rates (Cochrane and Piazzesi, 2005; Dahlquist and Hasseltoft, 2013; Zhu, 2015). Another strand of research examines predictive factors beyond the yield curve, revealing a broad array of factors, including jump risk (Wright and Zhou, 2009), option prices (Almeida et al., 2011), and macroeconomic variables (Ilmanen, 1995; Moench, 2008; Cooper and Priestley, 2009; Ludvigson and Ng, 2009; Favero et al 2012; Joslin et al 2014). These studies have motivated our research into the predictability of Treasury bond returns and risk premia.

The focus of our attention is geopolitical risk (GPR), which is broadly defined as the risks associated with wars, terrorism, and tensions between states (Caldara and Iacoviello, 2022). GPR represents one of the crucial determinants that influence asset prices and investment decisions (Berkman et al., 2011; Pástor and Veronesi, 2013). Prior research on geopolitical risk has primarily focused on stock markets (Narayan et al., 2022; Zaremba et al., 2022), foreign exchange markets (Liu and Zhang, 2024), and commodity markets (Brandt and Gao, 2019; Gkillas et al., 2020). Our study extends this line of research by investigating the empirical relationship between geopolitical risk and bond yields.

Our study closely relates to the application of the Factor-Augmented Regression Method (FARM), proposed by (Fan et al., 2020), which provides a consistent estimation strategy to

 

A page of text discussing literature review on Treasury bond returns, risk premia, and geopolitical risk.

overcome cross-sectional dependence. In economic or financial datasets, covariates typically exhibit common movement patterns, as these indicators are influenced by similar economic fundamentals and are highly correlated (Forbes and Rigobon, 2002; Stock and Watson, 2002a, b; Ludvigson and Ng, 2009). Therefore, regression analysis must account for the strong correlation structure among covariates. We employ FARM to decompose the co-movement component of geopolitical risks across countries, enabling us to isolate country- (region-) specific idiosyncratic geopolitical risks. This decomposition allows us to explore whether these country- (region-) level idiosyncratic components contain predictive information for US Treasury bonds, beyond the common international geopolitical risk factors.

Higher-order moments characterize the asymmetry and kurtosis of distributions. Extant literature has documented substantial evidence of negative skewness in stock returns and its implications for asset pricing and portfolio management (Neuberger, 2012). Harvey and Siddique (2000) demonstrate that conditional co-skewness helps explain cross-sectional variations in expected returns. Dittmar (2002) and Poti and Wang (2010) provide evidence that skewness and kurtosis contribute to explaining cross-sectional returns of industry-sorted portfolios. The conditional distribution of macroeconomic skewness, which measures unbalanced risks around baseline outlooks, exhibits predictive power for aggregate stock returns, suggesting that expected returns compensate for skewness risk. Bauer et al (2024) indicates that changes in the conditional skewness of Treasury yields reflect shifts in interest rate risk perceptions and predict Treasury risk premia. The literature has yet to examine whether the skewness of heterogeneous geopolitical risks at the country level contains predictive information for Treasury returns. Our study aims to address this empirical question by investigating the relationship between country- (region-) specific geopolitical risk skewness and sovereign bond market predictability.

 

Alt-text: A page of text discussing the decomposition of geopolitical risks and the role of skewness in predicting Treasury returns.

3. Data and Methodology

**3.1 Data**

Our study employs the yield curve dataset developed by Liu and Wu (2021), which is constructed via a nonparametric kernel smoothing approach with an innovatively designed adaptive bandwidth to enhance the fit of Treasury yields. This dataset not only retains the informational integrity of the original data but also demonstrates superior performance by minimizing pricing errors relative to existing yield curve datasets. In this paper, the period of monthly bond yield data spans from January 1985 to December 2023, focusing on zero-coupon U.S. Treasury bonds with maturities ranging from 2 to 10 years. In constructing bond returns, we adhere strictly to the methodologies outlined by Cochrane and Piazzesi (2005) and Ludvigson and Ng (2009). Let \( p_t^{(n)} \) denote the natural logarithm of the nominal price of a bond at time \( t \) with \( n \) years remaining to maturity, which pays 1 at maturity. The continuously compounded yield for an \( n \)-year bond is then defined by the following equation:

\[
y_t^{(n)} = -\frac{1}{n} p_t^{(n)},
\tag{1}
\]

where \( p_t^{(n)} \) is the log bond price of the \( n \)-year zero-coupon bond at month \( t \). Our analysis focuses on the excess return of bonds with a one-year holding period. We calculate the holding period return from purchasing an \( n \)-year bond at the end of month \( t \) and selling it as an \( (n - 1) \)-year bond at the end of month \( t + 12 \). The excess return is then defined as the difference between the holding period return of the \( n \)-year bond and the risk-free rate.

\[
r_{t+12}^{(n)} = p_{t+12}^{(n-1)} - p_t^{(n)},
\tag{2}
\]

\[
rx_{t+12}^{(n)} = r_{t+12}^{(n)} - y_t^{(1)},
\tag{3}
\]

where \( y_t^{(1)} \) is the yield of 1-year bond at month \( t \).

To quantitatively capture the degree of geopolitical uncertainty, we use the news-based geopolitical uncertainty index developed by Caldara and Iacoviello (2022). This GPR index (CI-GPR index hereafter) is constructed by standardizing the frequency of news articles that mention terms related to adverse geopolitical events. The index is derived from data collected. 

Alt-text: A page of academic text describing data and methodology for yield curve dataset and geopolitical uncertainty index.

from 10 major newspapers: the Chicago Tribune, the Daily Telegraph, the Financial Times, the Globe and Mail, the Guardian, the Los Angeles Times, the New York Times, USA Today, the Wall Street Journal, and the Washington Post, and is available on a monthly frequency. In constructing this index, the authors categorize the news content into eight groups: War Threats, Peace Threats, Military Buildups, Nuclear Threats, Terror Threats, Beginning of War, Escalation of War, and Terror Acts. Based on these categories, they further construct two sub-indices: geopolitical threat risk (CI-GPRT) index, which includes terms related to the first five categories, and geopolitical act risk (CI-GPRA) index, which includes terms related to the last three categories. To, construct predictors from cross-sectional global geopolitical risks, we use monthly country- (region-) specific geopolitical risk (GPRC) indices of 44 countries worldwide, spanning from January 1985 to December 2022.

**3.2 Measuring geopolitical skewness risk**

In this subsection, we introduce the methodology of measuring geopolitical skewness risk (GPSR) based on the 44 GPRC indices of Caldara and Iacoviello (2022). We first construct the cross-sectional moments directly using original GPRC data as a baseline specification, then we employ the factor-augmented regularized model (FARM) by Fan et al. (2020) to propose our GPSR index aligned with bond return prediction.

**3.2.1 Original GPRC-based skewness**

To calculate original GPRC-based skewness, we first standardize all GPRC indices to have zeros means and unit standard deviations for comparability across countries (regions). The standardization is recursively performed with an expanding window to ensure the real-time availability of constructed variables. Specifically, we set the first 120 months (1985:01-1994:12) as the initial estimation period, and begin to standardize the GPRC indices from the 121st month onwards. Then, after each time the indices are standardized, we compute the cross-sectional Pearson skewness for the last month \( t \) of the expanding window as follows:

\[
Skew_t = \frac{3 \times \left(\overline{GPRC}_t - \hat{M}_t \right)}{\hat{\sigma}_t}
\]  (4)

where \(\overline{GPRC_t}\), \(\hat{M}_t\), and \(\hat{\sigma}_t\) are the cross-sectional average, median, and standard deviation of GPRC indices at month \(t\). Repeating the above manners till the end of our sample period, we obtain a time series of Skew spanning from 1995:01-2022:12. Instead of the commonly used Fisher skewness, we focus on Pearson skewness in this paper because it is less influenced by outliers. However, as we document latter, our core findings are robust to different skewness calculation approaches. As comparison, we will also add the lower-order moments, i.e. variance (Var) and average (Avg), in forecasting performance evaluation. All these variables are smoothed by taking 12-month moving average.

**3.2.2 FARM-based skewness**

In the context of bond return prediction, an apparent defect of original GPRC-based moments is the absence of target information, which may cause the failure of capturing potential predictive power of cross-sectional distribution of global geopolitical risks. There are two key challenges in exploiting the cross-sectional characteristics of GPRC indices for prediction: high dimensionality and strong cross-sectional dependence. On one hand, the high dimensionality problem is intuitive, as it is not likely the geopolitical risks of all 44 countries (regions) are informative in forecasting future U.S. Treasury bond returns for every month. On the other hand, the presence of strong co-movement in GPRC indices across countries (regions) suggests that directly using traditional variable selection methods, such as correlation filter and LASSO, may fail to efficiently extract country- (region-) specific predictive signals.

To address these issues, we employ the factor-augmented regularized model (FARM) framework of Fan et al. (2020) before calculating skewness. In our study, the role of FARM is to first remove the common global risk components that we hypothesize to be quickly incorporated into bond prices and thus leave little predictive information, and then select the idiosyncratic GPRC components that historically predict bond returns in a regularized regression.

Formally, we take three steps to construct FARM-based skewness (FarmSkew hereafter). In the first step, we assume that the standardized GPRC indices have the following factor structure: 

[Page ends here] 

Alt-text: A page of academic text discussing FARM-based skewness in bond return prediction.

\[
GPRC_{i,t} = \Lambda_i' F_t + u_{i,t} \,,
\]
where \( F_t \) represents a \( k \times 1 \) vector of unobservable common factors capturing the trends of global geopolitical risks, \( \Lambda_i \) denotes country (region) \( i \)'s exposure to these global factors, and \( u_{i,t} \) reflects idiosyncratic geopolitical risk (IGPR) variations. To determine the optimal number of factors \( k \), we employ the information criteria developed by Bai and Ng (2002), which balances model fit against over-parameterization. Using principal component analysis (PCA) to estimate the common factors, we run regression (5) and measure IGPR with the residuals:

\[
IGPR_{i,t} = GPRC_{i,t} - \hat{\Lambda}_i' \hat{F}_t \,.
\]

In the second step, we employ the Elastic-net regression proposed by Zou and Hastie (2005) to select predictive IGPR indices. The model can be written as:

\[
r x_{t+12}^{(n)} = b_0 + \sum_{i=1}^N b_i IGPR_{i,t} + \varepsilon_{t+12}^{(n)}
\]

\[
\hat{\mathbf{b}} = \arg \min_{b_0,b_1,\ldots,b_N} \sum_{j=1}^t \left( r x_{j+12}^{(n)} - b_0 - \sum_{i=1}^N b_i IGPR_{i,j} \right)^2 + \lambda \alpha \sum_{i=1}^N |b_i| + \frac{\lambda (1-\alpha)}{2} \sum_{i=1}^N b_i^2
\]

where \( N \) is the number of IGPR indices, \( b_i \) represents the coefficient of the \( i \)-th IGPR index, and \( \lambda \) and \( \alpha \) are tuning parameters. The tuning parameters are determined through a data-driven approach: we reserve the last 12 observations of our expanding sample for validation and choose the values of \( \lambda \) and \( \alpha \) that minimizes the mean squared prediction error over this period. This approach is designed to identify the most predictive signals in recent period for each time point. We set the candidate values of \( \lambda \) and \( \alpha \) as \(\{0.03, 0.3, 3\}\) and \(\{0.3, 0.9\}\), respectively. After estimating the Elastic-net regression, we select the IGPR indices whose coefficients are not zero and denote them as \(\{IGPR_k^S\}_{k=1}^{n_t}\), where \(IGPR_k^S\) is the \(k\)-th selected IGPR index and \(n_t\) is the number of all selected IGPR indices at month \(t\).\(^1\)

In the third step, we calculate the cross-sectional Pearson skewness for the last observations of \(\{IGPR_k^S\}_{k=1}^{n_t}\):

\[
FarmSkew_t = \frac{3 \times (\overline{IGPR_t^S} - \tilde{M}_t^S)}{\hat{\sigma}_t^S}
\]

---

\(^1\) To rationalize the number of selected IGPR indices, we impose a restriction that \(0.3 \times N \leq n_t \leq 0.7 \times N\). In particular, we run a ridge regression and select the IGPRs with top 30% or 70% absolute coefficients correspondingly if \(n_t\) is beyond our desired range.

---

Alt-text: A page of academic text with mathematical formulas describing a model for geopolitical risk and Elastic-net regression.

where \( \overline{IGPR_t^S} \), \( \hat{M}_t^S \), and \( \hat{\sigma}_t^S \) are the cross-sectional average, median, and standard deviation of \(\{IGPR_{k,t}^S\}_{k=1}^{n_t}\).

Consistent with the manner of constructing original GPRC-based skewness, we let 1985:01-1994:12 be the initial estimation period, and recursively repeat the above steps from 1995:01 onwards with an expanding window till the end of our sample period, thereby generating a real-time FarmSkew series spanning from 1995:01 to 2022:12. Without loss of generality, we separately construct FarmSkew series using 3-year, 5-year, and 10-year bond returns, and take their equally-weighted average as our GPSR measure. Similarly, we calculate the FARM-based lower-order moments, i.e. FARM-based variance (FarmVar) and FARM-based average (FarmAvg), as competitors. Again, all these variables are smoothed by taking 12-month moving average.

**Please insert Figure 1 about here**

Figure 1 plots the time series of FarmSkew and the CI-GPR index. Two findings emerge from the figure. First, FarmSkew exhibits pronounced spikes during periods of heightened geopolitical uncertainty, particularly around recessionary episodes such as the downturn in the early 2000s and the 2008 Global Financial Crisis. These spikes suggest that FarmSkew may capture the geopolitical events which are potentially linked to market stress. Second, the movements of FarmSkew and CI-GPR index are not consistently synchronous. On one hand, both FarmSkew and CI-GPR sharply increase when certain terrorist incidents take place, such as the U.S. embassy bombings in 1998 and the USS Cole bombing in 2000. On the other hand, FarmSkew moves ahead of CI-GPR for the worldwide significant geopolitical events. For example, FarmSkew clearly climbs right before 911 Attacks and the outbreaks of Afghanistan, Iraq, and Russia-Ukraine Wars, and when these events take place, CI-GPR soars while FarmSkew drops. Moreover, FarmSkew reaches high points at several conflicts, such as the escalation of Iran nuclear issue in 2011 and the Venezuelan Crisis in 2019, however, CI-GPR remains relatively stable at these time points. The different sensitivities can be attributed to distinct construction methods of the two indices: FarmSkew is constructed in a selective and supervised way where the worldwide trends are filtered out and only historically predictive IGPRs enter the calculation of skewness, while CI-GPR is a more aggregated measure depicting the mean level of global geopolitical risk. The divergences also highlight the unique ability of

FarmSkew to capture the asymmetric nature of geopolitical risks, transcending the information contained in CI-GPR index.

**Please insert Figure 2 about here**

To look closer at our GPSR measure from a perspective of global geopolitical risk evolution, we further investigate the dynamic marginal contribution of each IGPR index to FarmSkew. Specifically, we define country (region) \(i\)'s marginal contribution at month \(t\) as:

\[
MC_{i,t} = FarmSkew_t - FarmSkew_t^i,
\]

where \(FarmSkew_t^i\) denotes the FarmSkew constructed without country (region) \(i\)'s IGPR index at month \(t\), that is, we eliminate country (region) \(i\)'s IGPR index in the third step of FarmSkew construction even if it is selected by Elastic-net.

Figure 2 presents the heatmap of the marginal contributions. The heatmap reveals significant heterogeneity in geopolitical risk across regions and over time. During 1995-2000, the IGPRs of European countries, such as Finland, Hungary, Norway, Poland, Portugal, and Sweden, contribute most to FarmSkew, likely due to the eastward expansions of the North Atlantic Treaty Organization (NATO) and the European Union (EU). In addition, the marginal contributions of Mexico during 1995-1996 and U.S. during 1998-2000 are also notable, which may be caused by the deterioration of U.S.-Mexico border security situation and the frequent terrorism events against U.S., respectively. In 2000s, countries in South America and Asia, such as Venezuela, Brazil, and Philippines, play important roles, which may be related to the United States' Asia-Pacific strategy and the rise of South America's left-wing governments during this period. After 2010, the contributions tend to be dispersive, and some relatively noticeable marginal increases of FarmSkew are generated by regions or countries including Finland, France, Hong Kong, Thailand, Ukraine, and Venezuela. The heatmap provides insights into the construction of FarmSkew, as these cross-sectional variations suggest that the predictive IGPRs are not static but evolve with global political developments.

**3.3 Descriptive statistics**

**Please insert Table 1 about here**

Table 1 provides descriptive statistics for all GPR-based variables, including FarmSkew, FarmVar, FarmAvg, Skew, Var, Avg, CI-GPR, CI-GPRT, and CI-GPRA, and the excess returns of 3-year, 5-year, and 10-year bonds. The sample period is over 1995:01-2022:12, aligning with the cross-sectional moments.

FarmSkew exhibits a mean of 0.34 with a standard deviation of 0.16, indicating that the selected IGPRCs are averagely right-skewed and, thus, likely to yield extremely high values over the sample period. The skewness of -0.06 and kurtosis of 2.46 suggest that FarmSkew is close to be normally distributed, which is similar with the case of FarmAvg. In contrast, FarmVar, Var, and Avg exhibit greater skewness and kurtosis, while the distribution of Skew is left-skewed. The table also highlights the differences between the cross-sectional moments and the geopolitical risk measures of Caldara and Iacoviello (2022). In particular, CI-GPR, CI-GPRT, and CI-GPRA all exhibit notably higher skewness and kurtosis, indicating they are substantially more fat-tail-distributed. These statistics reveal that FarmSkew is less correlated with Caldara and Iacoviello (2022)’s measures, thus, it may be able to provide unique information that is not captured by existing indices.

4. Forecasting performance evaluation

In this section, we provide the empirical results on forecasting performance evaluation. Section 4.1 evaluates the in-sample performance of FarmSkew and the competing predictors. Section 4.2 performs the incremental predictive power test. Section 4.3 discusses out-of-sample forecasting abilities. Section 4.4 assesses the economic value of bond return predictability through asset allocation.

**4.1. In-sample analysis**

We run the following regression to assess the in-sample performance of FarmSkew and the competing predictors in predicting annual excess bond returns:

\[
rx_{t+12}^{(n)} = \alpha + \beta Z_t + \epsilon_{t+12}^{(n)}, \quad n = 3, 5, 10,
\]

(11)

where \( Z_t \) is one of the candidate predictors at month \( t \). To facilitate interpretation, each individual predictor is standardized to have zero mean and unit standard deviation.

**Please insert Table 2 about here**

Table 2 reports the in-sample regression results. FarmSkew demonstrates significantly predictive power across all maturities. For instance, a one standard deviation increase of FarmSkew is associated with a 1.02% decrease of 3-year bond returns, generating a \( t \) statistic of 3.50 and an \( R^2 \) of 17.75%. This performance is consistently strong for 5-year and 10-year bonds, with 1% level statistically significant slopes of 1.73% and 2.83%, respectively. The performance of FarmSkew contrasts with the weaker or insignificant results for other predictors. For example, FarmVar has a slope of 0.10 (\( t \) statistic = 0.34) for 3-year bond returns, with an \( R^2 \) of only 0.17%. Similarly, FarmAvg and the original GPRC-based moments show limited predictive abilities, with \( t \) statistics ranging from 0.51 to -1.73 across different maturities. As for the GPR indices of Caldara and Iacoviello (2022), only CI-GPRT shows some predictive power, particularly for 3-year maturity. The slope for CI-GPRT in predicting 3-year bond returns is -0.59% (\( t \) statistic = -2.05), with an \( R^2 \) of 5.86%. However, the magnitude of predictability is relatively small compared to that of FarmSkew.

**4.2. Incremental predictive power analysis**

To examine whether the predictors provide incremental predictive power beyond the yield curve, we estimate the following regressions:

\[
rx_{t+12}^{(n)} = \alpha + \boldsymbol{\gamma}' \mathbf{PC}_t + \varepsilon_{t+12}^{(n)}, \quad n=3,5,10,
\]

\[
rx_{t+12}^{(n)} = \alpha + \beta Z_t + \boldsymbol{\gamma}' \mathbf{PC}_t + \varepsilon_{t+12}^{(n)}, \quad n=3,5,10,
\]

where \(\mathbf{PC}_t\) represents the first three principal components of the yield curve (level, slope, and curvature). As demonstrated by Litterman and Scheinkman (1991), these components explain the majority of cross-sectional variation in yields.

In addition to yield curve, macroeconomic variables are another important strand of predictors for Treasury bond risk premium. Following Ghysels et al. (2018) and Huang et al. (2023), we collected 51 real-time macroeconomic variables from the ALFRED database to construct a single macro predictor. These variables strike a balance between the number of

variables and the length of time series observations, and they are all available during our sample period (1995:01-2022:12) and transformed to be stationary. These 51 macroeconomic variables cover a broad spectrum of economic categories, including output and income, labor and unemployment, consumption expenditure and housing indicators, monetary aggregates and credit, and price indices. Consistent with Ghysels et al. (2018) and Huang et al. (2023), we uniformly assume a one-month publication lag for these variables and retain the latest observable version for variables with multiple updates within a month. When no version is recorded for a given month, the previous month's version is used to avoid introducing forward-looking bias.

Following Ghysels et al. (2014) and Jonas N. Eriksen (2017), we first use PCA extract latent common factors of the macroeconomic variables. The optimal number of factors is also determined by the Bai and Ng (2002) information criteria. Subsequently, in line with Ludvigson and Ng (2009), we employ the Schwartz-Bayesian Information Criterion to select the optimal subset of factors and their nonlinear transformations. In the end, we regress the average returns across 2- to 10-year bonds on the selected factors and nonlinear transformations, and take the fitted values as the single macro predictor. Similarly, to test the incremental predictive power of GPR predictors over the macro predictor, we run the following regressions:

\[
r x_{t+12}^{(n)} = \alpha + \gamma M_t + \varepsilon_{t+12}^{(n)}, \quad n=3,5,10,
\]  
(14)

\[
r x_{t+12}^{(n)} = \alpha + \beta Z_t + \gamma M_t + \varepsilon_{t+12}^{(n)}, \quad n=3,5,10,
\]  
(15)

where \(M_t\) represent the macro predictor at month \(t\).

**Please insert Table 3 about here**

For the above two groups of regressions, we are interested in the slope \(\beta\) and the incremental \(R^2\) (\(\Delta R^2\)), and Table 3 presents these results. Panel A controls for the first three principal components of yields, while Panel B controls for the single factor extracted from 51 real-time macro variables. Panel A indicates that FarmSkew continues to exhibit significant predictive power after controlling for yield curve factors, with \(\Delta R^2\) values of 19.95%, 18.38%, and 13.30% for 3-year, 5-year, and 10-year bonds, respectively. The slopes of FarmSkew remain statistically significant at 1% level. For example, the coefficient in predicting 3-year bond returns is 1.10%, with a \(t\) statistic of 4.40. Among the competing predictors, only FarmVar

---

Image description: A page of academic text with two formulas labeled (14) and (15) and a placeholder note for Table 3. The text discusses macroeconomic variables, PCA extraction, regression models, and predictive power of certain variables.

shows substantial predictive power particularly for 5- and 10-year bonds. It delivers significant slopes of 1.55% and 3.61%, and \( \Delta R^{2} \) values of 10.17% and 15.78% for 5- and 10-year bonds, respectively. In Panel B, FarmSkew maintains its performance after controlling for the real-time macroeconomic predictor. All the slopes are significant at 1% level and the \( \Delta R^{2} \) values exceed 12% across different maturities. As for the competing predictors, Var and CI-GPRT are the only two yield certain predictive power. However, their power is limited in forecasting 3-year bond returns, and the magnitudes of their \( \Delta R^{2} \)s (3.01% and 5.09%, respectively) are small relative to that of FarmSkew. Taken together, these results suggest that FarmSkew provides unique information beyond what is captured by traditional yield curve factors and real-macro variables.

**4.3. Out-of-sample analysis**

In this section, we examine the out-of-sample predictive power of GPR variables for U.S. Treasury bond risk premia. Consistent with in-sample analysis, we consider 3-, 5-, and 10-year bonds to investigate how predictive performance varies across different bond maturities. The out-of-sample forecasting begins with an initial training period from 1995:01 to 1999:12, during which we estimate predictive regressions to generate the first out-of-sample forecast for 2000:01. Thus, the out-of-sample evaluation period spans from January 2000 to December 2022. The length of our initial estimation period strikes a balance between securing sufficient observations for precise initial parameter estimation and maintaining a relatively long out-of-sample period for forecast evaluation. We recursively expand the estimation window and repeat this procedure to obtain out-of-sample predictions until the end of our sample period. In particular, the forecast for excess return of holding \( n \)-year bond over months \( t + 1 \) to \( t + 12 \) is given by:

\[
\hat{r}x_{t+12}^{(n)} = \hat{\alpha}_{t} + \hat{\beta}_{t} Z_{t}, \quad n = 3, 5, 10,
\tag{16}
\]

where \( \hat{\alpha}_{t} \) and \( \hat{\beta}_{t} \) are estimated by regressing \( \{ r x_{j+12}^{(n)} \}_{j=1}^{t-12} \) on a constant and \( \{ Z_{j} \}_{j=1}^{t-12} \).

Following Campbell and Thompson (2008), we calculate the \( R_{os}^{2} \) statistic as:

\[
R_{os}^{2} = 1 - \frac{\sum_{t=R}^{T-12} \left( r x_{t+12}^{(n)} - \hat{r}x_{t+12}^{(n)} \right)^{2}}{\sum_{t=R}^{T-12} \left( r x_{t+12}^{(n)} - \bar{r}x_{t+12}^{(n)} \right)^{2}},
\tag{17}
\]

17

where \(R\) and \(T\) respectively represent the lengths of initial training period and full sample period, and \(\widehat{r x}_{t+12}^{(n)}\) and \(\widetilde{r x}_{t+12}^{(n)}\) respectively denote the forecasted values from the prediction model and the expectations hypothesis (historical average) benchmark. To assess the statistical significance of \(R_{OS}^2\), we implement the Mean Square Forecast Error (MSFE)-adjusted statistic developed by Clark and West (2007). This test evaluates the null hypothesis that the MSFE of the benchmark model is less than or equal to the MSFE of the predictor-driven forecasts (\(R_{OS}^2 \leq 0\)).

**Please insert Table 4 about here**

Table 4 displays the evaluation results for out-of-sample performance. FarmSkew substantially outperforms the historical average benchmark, with \(R_{OS}^2\) values of 14.26%, 14.15%, and 11.19% for 3-year, 5-year, and 10-year bonds, respectively. These results are statistically significant at the 1% level, indicating that FarmSkew not only predict bond returns in-sample but also delivers meaningful out-of-sample forecasts. The performance of FarmSkew strongly contrasts with the weak results for other predictors, as none of these predictors show positive \(R_{OS}^2\) values. It is worth noting that the FARM-based cross-sectional moments consistently perform better than those based on original GPRC indexes for bonds of all maturities, which highlights the effect of our methodology in exploring out-of-sample predictability.

**Please insert Figure 3 about here**

To further evaluate the robustness of forecasting performance, we follow Goyal and Welch (2008), Rapach and Zhou (2013), and Eriksen (2015) to compute the Cumulative Difference of Squared Prediction Error (CDSPE). Specifically, the CDSPE up to month \(t\) is computed as:

\[
CDSPE_t = \sum_{j=R}^t \left( r x_{j+12}^{(n)} - \widehat{r x}_{j+12}^{(n)} \right)^2 - \sum_{j=R}^t \left( r x_{j+12}^{(n)} - \widetilde{r x}_{j+12}^{(n)} \right)^2,
\]

(18)

Figure 3 plots the CDSPE time series. Despite temporary declines during the early evaluation periods, the upward CDSPE trends for bonds with different maturities indicate that FarmSkew consistently outperforms the historical average benchmark. By comparison, the CDSPE curves of FarmVar climb during the early periods but fail to maintain the trend most of time, while FarmAvg shows no predictive power throughout the entire out-of-sample evaluation. This comparison further demonstrates the superior forecasting ability of cross-sectional

skewness relative to the lower-order moments. In summary, the CDSPE results underscore FarmSkew’s robustness as a predictor of bond returns.

**4.4. Asset allocation exercise**

Previous studies, such as Thornton and Valente (2012) and Sarno et al. (2016), find that translating statistical predictability into economic value is challenging for government bond investors. To evaluate the economic value of FarmSkew in predicting bond returns, we consider an asset allocation exercise for a mean-variance investor. The investor’s portfolio comprises two bonds: a risk-free 1-year bond and a risky *n*-year bond. Based on the expected returns given by the predictive model, the investor chooses the weights \(\omega_t^{(n)}\) to invest in the risky bond and \(1 - \omega_t^{(n)}\) to invest in the risk-free bond. Then, the portfolio return is written as:

\[
r_{p,t+12}^{(n)} = y_t^{(1)} + \omega_t^{(n)} r_{x,t+12}^{(n)} , \tag{19}
\]

The mean-variance investor selects the investment weight for risky *n*-year bond to solve the following expected utility maximization problem:

\[
\max_{\omega_t^{(n)}} \mathbb{E}_t \left[ r_{p,t+12}^{(n)} \right] - \frac{\gamma}{2} \mathrm{Var}_t \left[ r_{p,t+12}^{(n)} \right], \tag{20}
\]

where \(\gamma\) represents the risk aversion coefficient of the mean-variance investor. Following Eriksen (2017), we set \(\gamma\) equal to 10. This value is higher than those normally considered in literature, such as 3 (Campbell and Thompson, 2008; Thornton and Valente, 2012; Rapach and Zhou, 2013) and 5 (Sarno et al., 2016; Huang et al., 2023). However, as denoted by Gargano et al. (2017), lower values of \(\gamma\) tend to push the weights on risky bonds to the upper limits of investment constraints. This occurs more frequently for the EH benchmark, making it difficult to clearly differentiate between competing hypotheses. The solution to the above optimization problem is given by:

\[
\omega_t^{(n)} = \frac{1}{\gamma} \frac{\mathbb{E}_t \left[ r_{x,t+12}^{(n)} \right]}{\mathrm{Var}_t \left[ r_{x,t+12}^{(n)} \right]} , \tag{21}
\]

where \(\mathbb{E}_t \left[ r_{x,t+12}^{(n)} \right]\) and \(\mathrm{Var}_t \left[ r_{x,t+12}^{(n)} \right]\) are conditional expectation and variance of \(r_{x,t+12}^{(n)}\). We estimate \(\mathrm{Var}_t \left[ r_{x,t+12}^{(n)} \right]\) with an expanding window. To prevent investors from taking

extreme positions, we restrict \(\omega_t^{(n)}\) to lie within the range \([0, 1.5]\), which can be translated into setting a maximum leverage ratio of 50% and prohibiting short-selling of risky bonds. The certainty equivalent return (CER) of the portfolio can be expressed as:

\[
\text{CER} = \hat{\mu}_{p,(n)} - \frac{\gamma}{2} \hat{\sigma}_{p,(n)}^2 \tag{22}
\]

where \(\hat{\mu}_{p,(n)}\) and \(\hat{\sigma}_{p,(n)}^2\) are the sample mean and variance of \(n\)-year bond portfolio returns, respectively. We compute the CER gain by calculating the difference in CER between an investor using predictive model and an investor relying on the benchmark prediction (historical average). CER gain measures the improvement in investor returns achieved by switching from the benchmark prediction model to alternative predictive models. This can be interpreted as the annualized percentage management fee that the investor would be willing to pay to switch from the benchmark to another predictive model. In addition to CER gain, we also consider an alternative measure, the manipulation-proof performance (MPP) (Goetzmann et al., 2007). The MPP improvement is defined as:

\[
\text{MPP} = \frac{1}{1-\gamma} \ln \left( \frac{1}{G} \sum_{t=R}^{T-12} \begin{bmatrix} \hat{r}_{p,t+12}^{(n)} \\ y_{t+12}^{(1)} \end{bmatrix}^{1-\gamma} \right) - \frac{1}{1-\gamma} \ln \left( \frac{1}{G} \sum_{t=R}^{T-12} \begin{bmatrix} \tilde{r}_{p,t+12}^{(n)} \\ y_{t+12}^{(1)} \end{bmatrix}^{1-\gamma} \right), \tag{23}
\]

where \(\hat{r}_{p,t+12}^{(n)}\) and \(\tilde{r}_{p,t+12}^{(n)}\) represent the portfolio returns given by using predictive model and historical average forecast, respectively, and \(G\) is the length of out-of-sample evaluation period.

**Please insert Table 5 about here**

Table 5 reports the CER gains and MPP improvements under a transaction cost of 20 basis points (bps). The results of Table 5 basically echo the findings in Table 4, further confirming the economic value of our GPSR measure’s out-of-sample forecasts. Specifically, FarmSkew generates CER gains of 4.58%, 11.85%, and 6.68% for 3-year, 5-year, and 10-year bonds, respectively. Similarly, the MPP improvements are substantial, particularly for longer maturities. In contrast, the portfolio performance of other predictors all fail to surpass the benchmark except for the 10-year bond MPP improvement of 1.53 delivered by CI-GPRA. Therefore, these results underscore the practical utility of FarmSkew for investors seeking to

enhance portfolio performance by incorporating geopolitical risk into their bond return forecasts.

**4.5. Robustness with alternative skewness measures**

So far, we have testified the predictive power of FarmSkew constructed with Pearson skewness. One may naturally ask that if the forecasting performance depends on specific type of skewness. To address this concern, we consider other two alternative measures of skewness, i.e. Fisher skewness and Bowley skewness, and evaluate the performance of FarmSkew based on these measures.

As the most commonly used statistical measure quantifying the asymmetry of a probability distribution, Fisher skewness directly incorporates the third standardized moment of the distribution. When applying Fisher skewness, the FarmSkew for month \(t\) is calculated as:

\[
FarmSkew_t^F = \frac{\frac{1}{n_t} \sum_{i=1}^{n_t} \left( IGPR_{i,t}^S - \overline{IGPR_t^S} \right)^3}{\left( \frac{1}{n_t} \sum_{i=1}^{n_t} \left( IGPR_{i,t}^S - \overline{IGPR_t^S} \right)^2 \right)^{\frac{3}{2}}} \ , \tag{24}
\]

where \(\overline{IGPR_t^S}\) is the mean of \(\{IGPR_{i,t}^S\}_{i=1}^{n_t}\).

Unlike Pearson skewness and Fisher skewness, Bowley skewness is a measure of skewness totally based on quantiles. It quantifies the asymmetry of a dataset by comparing the relative distances between the lower and upper quantiles and the median. Under the setting of Bowley skewness, the FarmSkew for month \(t\) is calculated as:

\[
FarmSkew_t^B = \frac{(Q_t^3 - Q_t^2) - (Q_t^2 - Q_t^1)}{Q_t^3 - Q_t^1} \ , \tag{25}
\]

where \(Q_t^1\), \(Q_t^2\), and \(Q_t^3\) represent the first, second, and third quantile of \(\{IGPR_{i,t}^S\}_{i=1}^{n_t}\).

Typically, \(Q_t^1\), \(Q_t^2\), and \(Q_t^3\) equal to the 25th, 50th, and 75th percentiles in Bowley skewness. To emphasize the role of tail risk, we set \(Q_t^1\) and \(Q_t^3\) as the 10th and 90th percentiles.

**Please insert Table 6 about here**

Table 6 reports the in- and out-of-sample forecasting performance of FarmSkew using Fisher skewness and Bowley skewness. For maturities of 3-year, 5-year, and 10-year, the FarmSkew measures based on two alternative kinds of skewness are all positively associated with future bond returns at 1% significance level. The slopes range from 0.58% to 2.65% for

---

Alt-text: A page of academic text discussing robustness of skewness measures with formulas for Fisher and Bowley skewness.

Fisher skewness, and from 1.12% to 3.00% for Bowley skewness. Besides, the two different FarmSkew measures consistently outperform historical average benchmark out-of-sample. For 3-year, 5-year, and 10-year bonds, the \( R_{OS}^2 \) statistics of Fisher (Bowley) skewness are 1.24% (20.39%), 4.62% (18.82%), and 7.94% (12.90%), respectively. Since Fisher skewness, as previously mentioned, is more sensitive to extreme observations and likely to be noisy as a pure moment estimation, the superiority of Bowley skewness over Fisher skewness is not surprising. Overall, Table 5 demonstrates that under FARM framework, Fisher and Bowley skewness measures display qualitatively similar predictive power with that of Pearson skewness, indicating the robustness of FarmSkew with respect to skewness construction method.

5. Economic mechanisms

In this section, we explore the potential mechanisms underlying bond return predictability. Asset pricing theories indicate that rational, utility-maximizing investors require compensation for bearing macroeconomic risk. In this context, we demonstrate that our GPSR measure predicts the bond market through two channels: the expected return channel, by forecasting real economic activity, and the unexpected return channel, by relating to disinflation shocks.

**5.1 Real economic activity**

The link between real economic activity and bond risk premium has been intensively discussed in theorical literature. For instance, in spirit of the habit model of Campbell and Cochrane (1999), Buraschi and Jiltsov (2007) and Wachter (2006) show that variation in economic fundamentals should account for term structure dynamics and, consequently, excess bond returns, while Joslin et al. (2014) develop an arbitrage-free dynamic term structure model and find that output risk that is unspanned by yield curve largely affect term premiums in Treasury markets. Given the positive correlation between FarmSkew and future bond returns, we can reasonably infer that FarmSkew signals economic downturn risk, which induces high ex-ante risk premium required by investors.

 

Alt-text: A page of text discussing Fisher and Bowley skewness, economic mechanisms, and real economic activity in bond return predictability.

The adverse impact of geopolitical risk on economic condition is intuitive. Wars, terrorist attacks, and other geopolitical events act as exogenous shocks that heighten economic uncertainty (Wang et al., 2024). To comprehensively investigate the lead-lag relationship between GPSR and U.S. economic activity, we consider a series of macro indicators, including real personal consumption expenditures per capita (RPCE), real gross private domestic investment (RINV), real exports of goods and services (REXP), net private saving (NPS), industrial production (INDPRO), and unemployment rate (UNRATE). Among them, RPCE, RINV, REXP, and NPS are available in quarterly frequency, while INDPRO and UNRATE are monthly data.² For quarterly macro variables, we run the following regression

\[
\Delta M_{t+4} = \alpha + \beta GPSR_t + \epsilon_{t+4} \,,
\]

where \(\Delta M_{t+4} = M_{t+4} - M_t\) represents the annual change of the logarithm of RPCE, RINV, REXP, or NPS, and \(GPSR_t\) denotes the Skew or FarmSkew in quarter \(t\). Quarterly GPSR is obtained by taking quarterly average of monthly GPSR. For monthly macro variables, the predictive regression is:

\[
\Delta M_{t+12} = \alpha + \beta GPSR_t + \epsilon_{t+12} \,,
\]

where \(\Delta M_{t+12} = M_{t+12} - M_t\) represents the annual change of log INDPRO or UNATE, and \(GPSR_t\) denotes the Skew or FarmSkew in month \(t\).

**Please insert Table 7 about here**

Table 7 reports the regression results of predicting real economic condition with Skew and FarmSkew. Although Skew negatively predict REXP at 5% significance level, it shows no forecasting power on other five macro variables. By contrast, five out of six slopes of FarmSkew are statistically significant. Specifically, a one standard deviation increase of FarmSkew is associated with 0.29, 0.38, and 0.24 standard deviation decreases in future annual growths of RPCE, REXP, and INDPRO, and 0.43 and 0.35 standard deviation increases in future annual NPS growth and UNRATE change. These results suggest that FarmSkew not only predicts declines in exports, as generally expected, but also reflects weakened consumer confidence and increased precautionary savings. Consequently, FarmSkew serves as an effective predictor of slowing output growth and rising unemployment. Taken together, these

---

² Macro indicators are acquired from the website of Federal Reserve Bank of St. Louis

---

Alt-text: A page of academic text discussing the impact of geopolitical risk on economic conditions with formulas and references to Table 7.

findings support the assumption that our GPSR measure captures information about economic activity slowdown based on which bond investors anticipate higher returns as compensation for bearing downside risks.

**5.2 Disinflation shock**

Since inflation erodes the real value of nominal bond payoffs, it is typically considered, in addition to real economic activity, as another important driving force of bond prices (e.g., Ludvigson and Ng, 2009; Joslin et al., 2014). With a consumption-based asset pricing model, Brandt and Wang (2003) show that innovations about consumption growth and inflation both result in time-varying aggregate risk aversion. Contrary to consumption growth, an unexpected increase (decrease) in inflation temporarily raises (reduces) aggregate risk aversion, thus leads to higher (lower) ex-post risk premiums and lower (higher) prices of risky assets. Therefore, an association between high FarmSkew and subsequent disinflation shocks may also explain why our GPSR measure positively predicts bond returns. To test this hypothesis, we run the following regression:

\[
D_{t+1:t+12} = \alpha + \beta GPSR_t + \varepsilon_{t+1:t+12} \,,
\]

(28)

where \(D_{t+1:t+12} = \pi_{t+1:t+12} - \hat{\pi}_{t+1:t+12}\) denotes the difference between the actual inflation over the next 12 months \(\pi_{t+1:t+12}\) and the corresponding inflation expectation \(\hat{\pi}_{t+1:t+12}\) from the Surveys of Consumers by University of Michigan in month \(t\).

Suppose that FarmSkew indeed positively forecasts unexpected disinflation, one may naturally ask which component, i.e. demand- or supply-driven disinflation shock, does it forecast? On one hand, investors may underestimate the depression in consumption caused by global geopolitical risks, giving rise to an unexpected decrease in demand-side inflation. On the other hand, commodities such as oil can be overpriced due to panic sentiment when geopolitical situation is tense, and subsequent supply-side inflation declines unexpectedly as commodity prices fall back. To answer this question, we first regress Cleveland Fed 1-year inflation expectation on year-to-year percentage changes in food and energy consumer price indexes, and use the fitted values and residuals as estimates of demand- and supply-driven

 

The page ends mid-sentence.

Alt-text: A page of academic text discussing disinflation shock and bond pricing, including a regression formula.

inflation expectations, respectively.³ Then, we employ the demand- and supply-driven inflation components proposed by Shapiro (2024) and run a regression similar with ():

\[
D_{t+1:t+12}^c = \alpha + \beta GPSR_t + \varepsilon_{t+1:t+12}, \quad c = d \text{ or } s,
\]

(29)  
where \(D_{t+1:t+12}^d\) (\(D_{t+1:t+12}^s\)) represents the difference between demand- (supply-) driven inflation component and demand- (supply-) driven inflation expectation.⁴

**Please insert Table 8 about here**

Table 8 displays the results of regressions (28) and (29). Neither unexpected inflation nor its demand- and supply-driven components can be significantly forecasted by Skew. By comparison, FarmSkew demonstrates substantial predictive power for future inflation shocks, with a one standard deviation increase in FarmSkew associated with a 0.23 standard deviation decline in unexpected inflation. More importantly, the predictability concentrates in the demand-driven component of unexpected inflation, with a slope of -0.32 significant at 1% level. For the supply-driven component, the slope is nearly zero. Therefore, we can conclude that our GPSR measure is inked with future disinflation shocks by negatively forecasting unexpected demand-driven inflation.

Our findings align with the theory of Cieslak and Pflueger (2023), which links “good” and “bad” inflation to demand and supply shocks. According to Cieslak and Pflueger (2023), “good” inflation is negatively correlated with the stochastic discount factor (SDF), while “bad” inflation is positively correlated with the SDF. In this framework, “good” inflation rises during expansions when consumption growth is high and falls during recessions when investors place greater value on payoffs. As a result, when inflation is “good”, low risk premiums are sufficient for investors to hold Treasury bonds, as they serve as valuable hedges. For “bad” inflation, the situation is opposite. Jointly, Table 6 and Table 7 show that FarmSkew has predictive power on “good” disinflation shocks, and thus it is positively associated with future bond returns.

---

³ Eickmeier and Hofmann (2022) suggest that energy price shock serves as a supply factor of inflation variation, while and Shapiro (2024) find both food and energy prices drive supply-side inflation.  
⁴ Data of demand- and supply-driven inflation components are available on Shapiro’s website.

---

Alt-text: A page of academic text discussing inflation expectations, regression analysis, and predictive power of FarmSkew on inflation shocks.

6. Further analysis

We perform a series of extended analyses in this section to look closer on the economic implications of our GPSR measure. First, we examine if FarmSkew is connected with the errors in investors’ expectations about interest rate. Second, we demonstrate the relation between FarmSkew and credit spreads. Third, we discuss the influence of GPSR on primary Treasury market.

**6.1. Interest rate expectation error**

Cieslak (2018) documents significant and enduring biases in investors' forecasts of short-term interest rates throughout the business cycle. She argues that investors tend to overestimate future short-term rates and, thus, underestimate future bond returns, especially during economic downturns and Fed easing cycles. As previously we have testified the positive link between FarmSkew and unexpected disinflation, it is reasonable to expect our GPSR measure to be positively associated with the overestimation of future interest rates, given that interest rate is a key tool to counteract inflation for central banks.

To test if FarmSkew predicts interest rate expectation error, we run the following regression:

\[
E_{t+1}^m = \alpha + \beta GPSR_t + \epsilon_{t+1}, \quad m = 3M \text{ or } 10Y,
\]

where \(E_{t+1}^m\) is the interest rate expectation error computed as the difference between the actual rate of 3-month (3M) Treasury bill or 10-year (10Y) Treasury bond in quarter \(t + 1\) and the corresponding forecast made in quarter \(t\), and \(GPSR_t\) denotes the Skew or FarmSkew in quarter \(t\). The interest rate forecasts we use come from the Survey of Professional Forecasters (SPF) conducted by Philadelphia Fed.⁵

**Please insert Table 9 about here**

The results of regression (30) reported in Table 9 demonstrate that FarmSkew indeed predicts interest rate expectation errors significantly, while Skew exhibits no such forecasting

---

⁵ Because the SPF data are only available at quarterly, we use quarterly GPSR measures and interest rates by taking quarterly average of monthly values.

power. More specifically, for 3-month (10-year) interest rate, a one standard deviation increase of FarmSkew is associated with a 0.39 (0.26) standard deviation decrease of expectation error, and the slope is significant at 1% (5%) level. It is noteworthy that the correlation between FarmSkew and expectation error is substantially stronger for 3-month rate than for 10-year rate, which is consistent with the finding of Cieslak (2018) that the forecast biases primarily manifest in short-term interest rates. In summary, these results imply that FarmSkew captures investors’ biased belief on interest rates and, therefore, it is potentially informative for monetary policy makers in monitoring market expectations.

**6.2. Credit spread**

Although our study focuses on Treasury bonds which are regarded as free of credit risk, analyzing the relationship between GPSR and credit spreads may provide valuable insights for corporate bond investors. Kang and Pflueger (2015) suggest that corporate bond yields are influenced by concerns over debt deflation. For nominal bonds, lower-than-expected inflation raises real debt burdens and the likelihood of default. By constructing a real business cycle model where firms make optimal but infrequent adjustments to capital structure, Kang and Pflueger (2015) show that higher uncertainty or procyclicality in inflation significantly increases excess corporate yields relative to default-free yields. In this context, the link between FarmSkew and unexpected disinflation naturally raises a question that whether FarmSkew predicts credit spreads.

Our investigation in this subsection is based on the following regression:

\( CS_{t+1} = \alpha + \beta GPSR_t + \varepsilon_{t+1} \), (31)

where \( CS_{t+1} \) is the log credit spread in month \( t + 1 \), and \( GPSR_t \) denotes the Skew or FarmSkew in month \( t \). We consider three sorts of credit spreads: the spread between yields of Moody's BAA and AAA corporate bonds with maturities 20 years and above, the spread between yields of Moody's AAA corporate bond and Treasury bond with maturity of 20 years, and the spread between yields of Moody's BAA corporate bond and Treasury bond with maturity of 20 years.

**Please insert Table 10 about here**

Alt-text: A page of text discussing the relationship between FarmSkew, GPSR, and credit spreads in corporate bonds.

Table 10 clearly demonstrates that Skew is barely correlated with future BAA-AAA credit spreads, even though it significantly forecasts AAA-Treasury and BAA-Treasury spreads. In contrast, FarmSkew significantly predicts all credit spreads, with a one standard deviation increase of FarmSkew associated with 0.28, 0.29, and 0.33 standard deviation increases of future BAA-AAA, AAA-Treasury, and BAA-Treasury spreads, respectively. A potential explanation for the different performances of Skew and FarmSkew is that Skew is more likely to reflect the persistent fear sentiment from global geopolitical tensions, therefore its predictive power on credit spreads stems from flight-to-safety behaviors and concentrates in the spreads between corporate bonds and Treasuries. The correlation between FarmSkew and future credit spread, as we hypothesize, is driven by the predictive power of FarmSkew on unexpected disinflations, leading to the predictabilities of all three kinds of default likelihood differences.

**6.3. Treasury auction**

Our last analysis centers on the primary market of U.S. Treasuries. In related literature, the information content of Treasury auction is typically regarded as an important issue in financial economics (e.g., Cammack, 1991; Beetsma et al., 2018; Beetsma et al., 2020). One crucial metric for assessing the success of an auction is the “bid-to-cover ratio” (BCR), which is calculated as the total value of bids received during the auction divided by the total amount of newly issued debt. Therefore, if GPSR helps to explain the variation of BCR, it may capture non-negligible driving force of Treasury market sentiment.

To test the explanatory power of GPSR on BCR, we obtain the Treasury auction data from the official website of U.S. fiscal database, and separately calculate monthly BCRs based on all Treasuries, Treasury notes, bills, and 1-year bonds, and the Treasury bonds with maturity longer than one year. In addition to GPSR, we follow Beetsma et al. (2020) and employ several control variables, including lagged BCR, Treasury yield, the ex-post Treasury supply (i.e. the amount that is accepted at the auction), and the logarithm of Merrill Lynch Option Volatility Estimate (MOVE) index.⁶ We perform our analysis by running the univariate regression:

---

⁶ For the BCR based on Treasury bonds with maturity longer than one year, Treasury yield is the average of the yields of 5-year, 10-year, 20-year, and 30-year bonds. For the BCR based on Treasury notes, bills, and 1-year bonds, Treasury yield is the average of the yields of 1-month, 3-month, and 6-month bills, and 1-year bond. For the BCR based on all Treasuries, Treasury yield is the average of all Treasuries mentioned above. The Treasury supplies are

\[
\Delta BCR_{t+12} = \alpha + \beta GPSR_t + \varepsilon_{t+12} \,,
\tag{32}
\]

and the multivariate regression:

\[
\Delta BCR_{t+12} = \alpha + \beta_1 GPSR_t + \beta_2 BCR_t + \beta_3 Yield_t + \beta_4 Supply_t + \beta_5 MOVE_t + \varepsilon_{t+12} \,,
\tag{33}
\]

where \(\Delta BCR_{t+12}\) is the BCR change of the next 12 months, and \(GPSR_t\) represents the Skew or FarmSkew in month \(t\).  

**Please insert Table 11 about here**

We report the regression results in Table 11. The univariate regression results in panel A indicate that Skew is significantly and negatively correlated with future BCR changes for all auctions. However, after controlling for other explanatory variables, the slopes of Skew shrink toward zero. In contrast, the results in panel B suggest that for all auctions and the auctions covering Treasuries with maturities of one year or less, FarmSkew not only predicts BCR in univariate regressions, but also provides significant marginal explanatory power in multivariate regressions.

Moreover, there are two other points worth noting. First, the effect of GPSR on BCR is particularly pronounced for Treasuries with maturities of one year or less. This is probably because short-term Treasuries are more qualified to be safe assets relative to those with longer maturities during high GPSR periods, motivating more bids for short-term Treasuries in the auctions. Second, the predictive signs of Skew are negative while the counterparts of FarmSkew are positive. A potential reason is that Skew is not processed with FARM framework, so it represents the easily perceived GPSR which can be incorporated by Treasury market without lag. When Skew is high, investors may overreact in the primary market, leading to reversion of bid requirements in future auctions. As for FarmSkew, it is constructed with supervised machine learning and, thus, can be regarded as a bond-return-implied GPSR proxy, which means investors may overlook the information carried by FarmSkew, delaying the influence of GPSR on Treasury auctions.

Overall, the above evidences reveal that global geopolitical risk can play an enormous role in the primary Treasury market. Considering that unsuccessful auctions typically increase

---

inflation-adjusted.  
As MOVE index originates in December 2002, the sample period of multivariate regressions is 2002:12-2022:12.

funding costs, our findings could be valuable for debt management offices (DMOs) who are keen on avoiding undersubscribed auctions (Beetsma et al., 2020).

7. Conclusion

This paper introduces a novel measure of global geopolitical skewness risk, FarmSkew, and demonstrates its significant predictive power for U.S. Treasury bond returns. By employing the Factor-Augmented Regularized Model (FARM) framework, we decompose global geopolitical risks into common global factors and country- (region-) specific idiosyncratic components, isolating the skewness of idiosyncratic risks that contain unique predictive information. Our results show that FarmSkew outperforms extant mean-level measures of geopolitical risk, such as the Caldara and Iacoviello (2022) GPR index, both in-sample and out-of-sample. The economic value of FarmSkew is further validated through asset allocation exercises, where it generates substantial certainty equivalent return (CER) gains and manipulation-proof performance (MPP) improvements for mean-variance investors.

The economic mechanisms underlying FarmSkew’s predictive power are twofold. First, it captures the expected return channel by forecasting declines in real economic activity, such as reduced consumer spending and higher unemployment, which increase the ex-ante risk premium required by investors. Second, it relates to the unexpected return channel by predicting disinflation shocks, particularly those driven by demand-side factors, which reduce inflation expectations and drive bond prices up. Additionally, FarmSkew provides insights into other financial market dynamics, including interest rate expectation errors, credit spreads, and Treasury auction outcomes, highlighting its broader relevance for investors and policymakers.

Our findings underscore the importance of international risk spillover and considering higher-order moments, such as skewness, in assessing geopolitical risk and its impact on financial markets. Future research could extend this framework to other asset classes and other categories of risk measures, or explore the role of geopolitical skewness risk in global financial markets.

References

Beetsma, R., Giuliodori, M., Hanson, J., & de Jong, F. (2020). Determinants of the bid-to-cover ratio in Eurozone sovereign debt auctions. *Journal of Empirical Finance*, 58, 96-120.

Almeida, C., Graveline, J. J., & Joslin, S. (2011). Do interest rate options contain information about excess returns?. *Journal of Econometrics*, 164(1), 35-44.

Bai, J., & Ng, S. (2002). Determining the number of factors in approximate factor models. *Econometrica*, 70(1), 191-221.

Bauer, M., & Chernov, M. (2024). Interest rate skewness and biased beliefs. *Journal of Finance*, 79(1), 173-217.

Beetsma, R., Giuliodori, M., Hanson, J., & de Jong, F. (2018). Bid-to-cover and yield changes around public debt auctions in the euro area. *Journal of Banking & Finance*, 87, 118-134.

Brandt, M. W., & Gao, L. (2019). Macro fundamentals or geopolitical events? A textual analysis of news events for crude oil. *Journal of Empirical Finance*, 51, 64-94.

Brandt, M. W., & Wang, K. Q. (2003). Time-varying risk aversion and unexpected inflation. *Journal of Monetary Economics*, 50(7), 1457-1498.

Buraschi, A., & Jiltsov, A. (2007). Habit formation and macroeconomic models of the term structure of interest rates. *Journal of Finance*, 62(6), 3009-3063.

Caldara, D., & Iacoviello, M. (2022). Measuring geopolitical risk. *American Economic Review*, 112(4), 1194-1225.

Cammack, E. B. (1991). Evidence on bidding strategies and the information in Treasury bill auctions. *Journal of Political Economy*, 99(1), 100-130.

Campbell, J. Y., & Shiller, R. J. (1991). Yield spreads and interest rate movements: A bird's eye view. *Review of Economic Studies*, 58(3), 495-514.

Cieslak, A. (2018). Short-rate expectations and unexpected returns in treasury bonds. *Review of Financial Studies*, 31(9), 3265-3306.

Cieslak, A., & Pflueger, C. (2023). Inflation and asset returns. *Annual Review of Financial Economics*, 15(1), 433-448.

Alt-text: A page of academic references in a bibliography section.

Cieslak, A., & Povala, P. (2015). Expected returns in Treasury bonds. *Review of Financial Studies*, 28(10), 2859-2901.

Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics*, 138(1), 291-311.

Cochrane, J. H., & Piazzesi, M. (2005). Bond risk premia. *American Economic Review*, 95(1), 138-160.

Cooper, I., & Priestley, R. (2009). Time-varying risk premiums and the output gap. *Review of Financial Studies*, 22(7), 2801-2833.

Diebold, F. X., & Mariano, R. S. (1995). Com paring predictive accuracy. *Journal of Business and Economic Statistics*, 13(3), 253-263.

Dittmar, R. F. (2002). Nonlinear pricing kernels, kurtosis preference, and evidence from the cross section of equity returns. *Journal of Finance*, 57(1), 369-403.

Dockner, E. J., Mayer, M., & Zechner, J. (2013). Sovereign bond risk premiums. Available at SSRN 2275916.

Eickmeier, S., & Hofmann, B. (2022). What drives inflation? Disentangling demand and supply factors. Deutsche Bundesbank Discussion Paper No. 46/2022.

Fama, E. F. (2006). The behavior of interest rates. *Review of Financial Studies*, 19(2), 359-379.

Fama, E. F., & Bliss, R. R. (1987). The information in long-maturity forward rates. *American Economic Review*, 680-692.

Fan, J., Ke, Y., & Wang, K. (2020). Factor-adjusted regularized model selection. *Journal of Econometrics*, 216(1), 71-85.

Favero, C. A., Niu, L., & Sala, L. (2012). Term structure forecasting: No-arbitrage restrictions versus large information set. *Journal of Forecasting*, 31(2), 124-156.

Forbes, K. J., & Rigobon, R. (2002). No contagion, only interdependence: measuring stock market comovements. *Journal of Finance*, 57(5), 2223-2261.

Gargano, A., Pettenuzzo, D., & Timmermann, A. (2019). Bond return predictability: Economic value and links to the macroeconomy. *Management Science*, 65(2), 508-540.

Gkillas, K., Gupta, R., & Pierdzioch, C. (2020). Forecasting realized gold volatility: Is there a role of geopolitical risks?. *Finance Research Letters*, 35, 101280.

 

Alt-text: A page of academic references in finance and economics.

Harvey, C. R., & Siddique, A. (2000). Conditional skewness in asset pricing tests. *Journal of Finance*, 55(3), 1263-1295.

Huang, D., Jiang, F., Li, K., Tong, G., & Zhou, G. (2023). Are bond returns predictable with real-time macro data?. *Journal of Econometrics*, 237(2), 105438.

Ilmanen, A. (1995). Time-varying expected returns in international bond markets. *Journal of Finance*, 50(2), 481-506.

Ioannidis, C., & Ka, K. (2021). Economic policy uncertainty and bond risk premia. *Journal of Money, Credit and Banking*, 53(6), 1479-1522.

Joslin, S., Priebsch, M., & Singleton, K. J. (2014). Risk premiums in dynamic term structure models with unspanned macro risks. *Journal of Finance*, 69(3), 1197-1233.

Kang, J., & Pflueger, C. E. (2015). Inflation risk in corporate bonds. *Journal of Finance*, 70(1), 115-162.

Keim, D. B., & Stambaugh, R. F. (1986). Predicting returns in the stock and bond markets. *Journal of Financial Economics*, 17(2), 357-390.

Liu, X., & Zhang, X. (2024). Geopolitical risk and currency returns. *Journal of Banking & Finance*, 161, 107097.

Liu, Y., & Wu, J. C. (2021). Reconstructing the yield curve. *Journal of Financial Economics*, 142(3), 1395-1425.

Ludvigson, S. C., & Ng, S. (2009). Macro factors in bond risk premia. *Review of Financial Studies*, 22(12), 5027-5067.

Moench, E. (2008). Forecasting the yield curve in a data-rich environment: A no-arbitrage factor-augmented VAR approach. *Journal of Econometrics*, 146(1), 26-43.

Narayan, P. K. (2022). Understanding exchange rate shocks during COVID-19. *Finance Research Letters*, 45, 102181.

Neuberger, A. (2012). Realized skewness. *Review of Financial Studies*, 25(11), 3423-3455.

Pástor, Ľ., & Veronesi, P. (2013). Political uncertainty and risk premia. *Journal of Financial Economics*, 110(3), 520-545.

Poti, V., & Wang, D. (2010). The coskewness puzzle. *Journal of Banking & Finance*, 34(8), 1827-1838.

 

Alt-text: A list of academic references related to finance and economics.

Rapach, D. E., Strauss, J. K., & Zhou, G. (2013). International stock return predictability: What is the role of the United States?. *Journal of Finance*, 68(4), 1633-1662.  
Sarno, L., Tsiakas, I., & Ulloa, B. (2016). What drives international portfolio flows?. *Journal of International Money and Finance*, 60, 53-72.  
Shapiro, A. H. (2024). Decomposing Supply-and Demand-Driven Inflation. Journal of Money, Credit and Banking. *Forthcoming*.  
Stock, J. H., & Watson, M. W. (2002). Forecasting using principal components from a large number of predictors. *Journal of the American statistical association*, 97(460), 1167-1179.  
Stock, J. H., & Watson, M. W. (2002). Macroeconomic forecasting using diffusion indexes. *Journal of Business & Economic Statistics*, 20(2), 147-162.  
Thornton, D. L., & Valente, G. (2012). Out-of-sample predictions of bond excess returns and forward rates: An asset allocation perspective. *Review of Financial Studies*, 25(10), 3141-3168.  
Wachter, J. A. (2006). A consumption-based model of the term structure of interest rates. *Journal of Financial Economics*, 79(2), 365-399.  
Wang, X., Wu, Y., & Xu, W. (2024). Geopolitical risk and investment. *Journal of Money, Credit and Banking*, 56(8), 2023-2059.  
Welch, I., & Goyal, A. (2008). A comprehensive look at the empirical performance of equity premium prediction. *Review of Financial Studies*, 21(4), 1455-1508.  
Wright, J. H., & Zhou, H. (2009). Bond risk premia and realized jump risk. *Journal of Banking & Finance*, 33(12), 2333-2345.  
Zaremba, A., Cakici, N., Demir, E., & Long, H. (2022). When bad news is good news: Geopolitical risk and the cross-section of emerging market stock returns. *Journal of Financial Stability*, 58, 100964.  
Zhao, F., Zhou, G., & Zhu, X. (2021). Unspanned global macro risks in bond returns. *Management Science*, 67(12), 7825-7843.  
Zhu, X. (2015). Out-of-sample bond risk premium predictions: A global common factor. *Journal of International Money and Finance*, 51, 155-173.  

Figures and tables

Figure 1. FarmSkew and CI-GPR index, 1995:01–2022:12. The vertical bars correspond to NBER-dated recessions.

Alt-text: Line graph showing FarmSkew and CI-GPR index from 1995 to 2022 with annotations for major geopolitical events and shaded vertical bars for recessions.

Figure 2. Heatmap of IGPRs’ marginal contributions to FarmSkew, 1995:01–2022:12.

Alt-text: Heatmap showing marginal contributions of IGPRs to FarmSkew for various countries from 1995 to 2022, with a color scale from blue (negative) to red (positive).

|       | 3-year | 5-year | 10-year |
|-------|--------|--------|---------|
| FarmSkew | Blue line | Blue line | Blue line |
| FarmVar  | Red line  | Red line  | Red line  |
| FarmAvg  | Green line| Green line| Green line|

Figure 3. The cumulative sum of difference between the squared prediction error of historical average benchmark forecast and squared prediction error of the predictive model, namely CDSPE, 2000:01-2022:12. The vertical bars correspond to NBER-dated recession.

Alt-text: Three line graphs showing cumulative sum of differences in squared prediction errors for 3-year, 5-year, and 10-year horizons with vertical bars indicating recessions.

**Table 1. Descriptive statistics**

| Predictor                  | Mean  | Std. Dev. | Min    | Max     | Skewness | Kurtosis |
|----------------------------|-------|-----------|--------|---------|----------|----------|
| FarmSkew                   | 0.34  | 0.16      | -0.02  | 0.74    | -0.06    | 2.46     |
| FarmVar                   | 0.54  | 0.32      | 0.14   | 1.78    | 1.52     | 5.45     |
| FarmAvg                   | 0.00  | 0.06      | -0.22  | 0.15    | -0.05    | 3.31     |
| Skew                      | 0.62  | 0.13      | 0.32   | 0.91    | -0.30    | 2.36     |
| Var                       | 0.87  | 0.65      | 0.19   | 4.02    | 2.76     | 12.70    |
| Avg                       | 0.00  | 0.35      | -0.46  | 1.36    | 1.42     | 4.97     |
| CI-GPR                    | 98.67 | 50.07     | 39.05  | 512.53  | 4.41     | 31.46    |
| CI-GPRT                   | 98.67 | 43.40     | 36.69  | 403.71  | 3.07     | 17.30    |
| CI-GPRA                   | 99.76 | 80.12     | 28.45  | 854.07  | 5.79     | 49.38    |
| \( r x_{t+12}^{(3)} \) (%) | 0.88  | 2.42      | -7.14  | 7.27    | -0.30    | 3.62     |
| \( r x_{t+12}^{(5)} \) (%) | 1.72  | 4.26      | -11.86 | 12.40   | -0.33    | 3.14     |
| \( r x_{t+12}^{(10)} \) (%)| 3.16  | 7.99      | -20.60 | 20.47   | -0.31    | 2.87     |

Note: FarmSkew, FarmVar, and FarmAvg denote the cross-sectional skewness, variance, and average of the idiosyncratic geopolitical risk (IGPR) measures selected by FARM procedure. Skew, Var, and Avg denote the cross-sectional skewness, variance, and average of the original country- (region-) specific geopolitical risk (GPRC) indices. CI-GPR, CI-GPRT, and CI-GPRA represent the global geopolitical risk, geopolitical threat risk, and geopolitical act risk indexes of Caldara and Iacoviello (2022). The sample period is over 1995:01-2022:12.

 

Alt-text: A table showing descriptive statistics for various geopolitical risk predictors including mean, standard deviation, minimum, maximum, skewness, and kurtosis values.

Table 2. In-sample performance

| Predictor | 3-year |       |       | 5-year |       |       | 10-year |       |       |
|-----------|--------|-------|-------|--------|-------|-------|---------|-------|-------|
|           | β (%)  | t stat. | R² (%) | β (%)  | t stat. | R² (%) | β (%)   | t stat. | R² (%) |
| FarmSkew  | 1.02***| 3.50  | 17.75 | 1.73***| 3.61  | 16.51 | 2.83*** | 3.17  | 12.53 |
| FarmVar   | 0.10   | 0.34  | 0.17  | 0.41   | 0.78  | 0.95  | 1.09    | 1.03  | 1.85  |
| FarmAvg   | 0.30   | 1.12  | 1.57  | 0.35   | 0.67  | 0.69  | 0.55    | 0.51  | 0.48  |
| Skew      | -0.29  | -0.67 | 1.40  | -0.42  | -0.59 | 0.97  | -0.71   | -0.60 | 0.79  |
| Var       | -0.47**| -1.73 | 3.73  | -0.62  | -1.26 | 2.15  | -1.21   | -1.28 | 2.31  |
| Avg       | -0.36  | -0.96 | 2.17  | -0.42  | -0.67 | 0.97  | -0.82   | -0.72 | 1.06  |
| CI-GPR    | -0.24  | -0.64 | 0.97  | -0.14  | -0.25 | 0.11  | -0.04   | -0.04 | 0.00  |
| CI-GPRT   | -0.59**| -2.05 | 5.86  | -0.77* | -1.69 | 3.28  | -1.29   | -1.40 | 2.59  |
| CI-GPRA   | 0.11   | 0.25  | 0.22  | 0.43   | 0.61  | 1.04  | 1.06    | 0.95  | 1.76  |

Note: This table reports the in-sample regression results of predicting excess returns of holding 3-year, 5year, or 10-year bond for one year. FarmSkew, FarmVar, and FarmAvg denote the cross-sectional skewness, variance, and average of the idiosyncratic geopolitical risk (IGPR) measures selected by FARM procedure. Skew, Var, and Avg denote the cross-sectional skewness, variance, and average of the original country- (region-) specific geopolitical risk (GPRC) indices. CI-GPR, CI-GPRT, and CI-GPRA represent the global geopolitical risk, geopolitical threat risk, and geopolitical act risk indexes of Caldara and Iacoviello (2022). The Newey-West t statistics are calculated with 12 lags. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. The sample period is over 1995:01-2022:12. All predictors are standardized for easy comparison.

 

Alt-text: Table showing in-sample regression results for predicting excess returns of 3-year, 5-year, and 10-year bonds with various geopolitical risk predictors.

**Table 3. Incremental power relative to yield curve and real-time macro predictors**

| Predictor | 3-year |  |  | 5-year |  |  | 10-year |  |  |
|-----------|--------|--|--|--------|--|--|---------|--|--|
|           | β (%)  | t stat. | ΔR² (%) | β (%)  | t stat. | ΔR² (%) | β (%)   | t stat. | ΔR² (%) |
| **Panel A: Controlling for the first three principal components of yields** | | | | | | | | | |
| FarmSkew  | 1.10*** | 4.40 | 19.95 | 1.87*** | 4.29 | 18.38 | 2.99*** | 3.45 | 13.30 |
| FarmVar   | 0.69    | 2.26 | 6.11  | 1.55*** | 2.93 | 10.17 | 3.61*** | 3.41 | 15.78 |
| FarmAvg   | 0.49    | 2.05 | 3.32  | 0.64    | 1.38 | 1.75  | 1.34    | 1.33 | 1.86  |
| Skew      | 0.35    | 0.90 | 1.26  | 0.71    | 1.09 | 1.78  | 1.61    | 1.56 | 2.73  |
| Var       | -0.06   | -0.20| -0.21 | 0.11    | 0.21 | -0.20 | 0.36    | 0.33 | -0.08 |
| Avg       | 0.03    | 0.08 | -0.24 | 0.17    | 0.28 | -0.13 | 0.23    | 0.20 | -0.17 |
| CI-GPR    | -0.14   | -0.40| 0.04  | -0.13   | -0.22| -0.17 | -0.32   | -0.34| -0.09 |
| CI-GPRT   | -0.25   | -0.88| 0.65  | -0.26   | -0.50| 0.05  | -0.36   | -0.36| -0.07 |
| CI-GPRA   | -0.07   | -0.16| -0.19 | -0.07   | -0.10| -0.23 | -0.37   | -0.35| -0.06 |
| **Panel B: Controlling for real-time macro predictor** | | | | | | | | | |
| FarmSkew  | 1.02*** | 3.56 | 17.44 | 1.75*** | 3.73 | 16.27 | 2.86*** | 3.34 | 12.32 |
| FarmVar   | 0.10    | 0.35 | -0.41 | 0.42    | 0.80 | 0.40  | 1.11    | 1.05 | 1.35  |
| FarmAvg   | 0.30    | 1.10 | 0.92  | 0.34    | 0.65 | 0.03  | 0.51    | 0.47 | -0.18 |
| Skew      | -0.27   | -0.64| 0.69  | -0.39   | -0.55| 0.24  | -0.62   | -0.54| 0.03  |
| Var       | -0.46*  | -1.70| 3.01  | -0.60   | -1.21| 1.40  | -1.15   | -1.20| 1.50  |
| Avg       | -0.35   | -0.94| 1.49  | -0.40   | -0.65| 0.29  | -0.77   | -0.68| 0.34  |
| CI-GPR    | -0.24   | -0.64| 0.38  | -0.14   | -0.25| -0.48 | -0.04   | -0.05| -0.58 |
| CI-GPRT   | -0.58** | -2.01| 5.09  | -0.74   | -1.63| 2.45  | -1.21   | -1.32| 1.71  |
| CI-GPRA   | 0.10    | 0.23 | -0.42 | 0.41    | 0.57 | 0.32  | 0.98    | 0.89 | 0.94  |

Table showing incremental power of various predictors relative to yield curve and real-time macro predictors for 3-year, 5-year, and 10-year horizons.

Note: This table reports the slopes, Newey-West t-statistics, and incremental \(R^{2}s\) (\(\Delta R^{2}s\)) of GPR-based variables relative to yield curve and real-time macro predictors in predicting bond returns, where yield curve predictors are the first three principal components of the 1- to 10-year yields, and the real-time macro predictor is the single factor extracted from 51 real-time macro variables. FarmSkew, FarmVar, and FarmAvg denote the cross-sectional skewness, variance, and average of the idiosyncratic geopolitical risk (IGPR) measures selected by FARM procedure. Skew, Var, and Avg denote the cross-sectional skewness, variance, and average of the original country- (region-) specific geopolitical risk (GPRC) indices. CI-GPR, CI-GPRT, and CI-GPRA represent the global geopolitical risk, geopolitical threat risk, and geopolitical act risk indexes of Caldara and Iacoviello (2022). The Newey-West t statistics are calculated with 12 lags. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. The sample period is over 1995:01-2022:12. All predictors are standardized for easy comparison.

Alt-text: Text note explaining the contents and significance of a table related to GPR-based variables and bond returns.

**Table 4. Out-of-sample performance**

| Predictor | 3-year |  | 5-year |  | 10-year |  |
|-----------|--------|----|--------|----|---------|----|
|           | \(R^2_{OS} \, (%)\) | MSFE adj. | \(R^2_{OS} \, (%)\) | MSFE adj. | \(R^2_{OS} \, (%)\) | MSFE adj. |
| FarmSkew  | 14.26*** | 6.82 | 14.15*** | 6.18 | 11.19*** | 5.18 |
| FarmVar   | -6.24   | -0.25 | -7.09   | 1.06 | -7.91**  | 2.13 |
| FarmAvg   | -1.53   | 1.73 | -3.48   | 1.13 | -5.69    | 0.37 |
| Skew      | -23.27  | -5.35 | -22.43  | -5.45 | -17.57   | -5.16 |
| Var       | -17.42  | -2.66 | -22.19  | -1.54 | -21.52   | -1.73 |
| Avg       | -28.45  | -5.00 | -27.23  | 5.22 | -24.66   | -4.72 |
| CI-GPR    | -17.46  | -3.90 | -15.02  | -3.90 | -8.71    | -3.15 |
| CI-GPRT   | -2.03   | 0.97  | -3.88   | -0.40 | -3.59    | -0.73 |
| CI-GPRA   | -16.10  | -4.77 | -12.77  | -1.80 | -7.77    | 0.57 |

Note: This table reports the out-of-sample performance of forecasting excess returns of holding 3-year, 5-year, or 10-year bond for one year. FarmSkew, FarmVar, and FarmAvg denote the cross-sectional skewness, variance, and average of the idiosyncratic geopolitical risk (IGPR) measures selected by FARM procedure. Skew, Var, and Avg denote the cross-sectional skewness, variance, and average of the original country- (region-) specific geopolitical risk (GPRC) indices. CI-GPR, CI-GPRT, and CI-GPRA represent the global geopolitical risk, geopolitical threat risk, and geopolitical act risk indexes of Caldara and Iacoviello (2022). The \(R^2_{OS}\) is the Campbell and Thompson (2008) out-of-sample \(R^2\), which is tested by the Clark and West (2007) MSFE-adjusted statistic. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. The out-of-sample period is over 2000:01-2022:12.

 

Alt-text: Table showing out-of-sample performance metrics for forecasting excess returns on 3-year, 5-year, and 10-year bonds using various geopolitical risk predictors.

**Table 5. Portfolio performance**

| Predictor | CER gain (%) |       |       | MPP improvement |       |       |
|-----------|--------------|-------|-------|-----------------|-------|-------|
|           | 3-year       | 5-year| 10-year| 3-year          | 5-year| 10-year|
| FarmSkew  | 4.58         | 11.85 | 6.68  | 3.92            | 13.75 | 12.55 |
| FarmVar   | -3.03        | -3.77 | -11.50| -4.60           | -3.16 | -2.53 |
| FarmAvg   | -1.87        | -3.75 | -5.29 | -2.11           | -1.36 | -2.55 |
| Skew      | -3.95        | -4.22 | -7.67 | -6.49           | -5.62 | -8.39 |
| Var       | -3.06        | -4.46 | -13.72| -4.70           | -4.56 | -12.44|
| Avg       | -2.94        | -3.68 | -5.69 | -3.96           | -4.43 | -6.27 |
| CI-GPR    | -2.48        | -2.70 | -2.83 | -2.56           | -10.02| -2.68 |
| CI-GPRT   | -1.65        | -1.44 | -0.88 | -1.52           | -7.79 | -0.53 |
| CI-GPRA   | -0.60        | -0.91 | -1.88 | -1.07           | -5.97 | 1.53  |

Note: This table reports the portfolio gains of forecasting bond returns with transaction costs of 20 basis points. We consider two portfolio gain measures: certainty equivalent return (CER) gain and Goetzmann et al. (2007) manipulation-proof performance (MPP) improvement, which are calculated as the incremental values of using the GPR-based forecasts relative to the benchmark of historical average forecasts. We assume a mean–variance investor, with risk aversion coefficient \(\gamma = 10\) and investment horizon of one year, decides to allocate his wealth between a 1-year (risk-free) bond and an n-year bond (n = 3, 5, 10), and estimates the expected n-year bond return by using the GPR-based variables. FarmSkew, FarmVar, and FarmAvg denote the cross-sectional skewness, variance, and average of the idiosyncratic geopolitical risk (IGPR) measures selected by FARM procedure. Skew, Var, and Avg denote the cross-sectional skewness, variance, and average of the original country- (region-) specific geopolitical risk (GPRC) indices. CI-GPR, CI-GPRT, and CI-GPRA represent the

[The text is cut off here.]

---

Alt-text: Table showing portfolio performance metrics CER gain (%) and MPP improvement for different predictors over 3-year, 5-year, and 10-year horizons.

global geopolitical risk, geopolitical threat risk, and geopolitical act risk indexes of Caldara and Iacoviello (2022). All the expected bond returns are recursively estimated with expanding windows. The investment period is 2000:01-2022:12.

**Table 6. Performance of FarmSkew with alternative skewness measures**

|                        | Fisher skewness          |               |               | Bowley skewness          |               |               |
|------------------------|-------------------------|---------------|---------------|-------------------------|---------------|---------------|
|                        | 3-year                  | 5-year        | 10-year       | 3-year                  | 5-year        | 10-year       |
| \(\beta\) (%)          | 0.58***                 | 1.23***       | 2.65***       | 1.12***                 | 1.87***       | 3.00***       |
| t stat.                | 2.35                    | 2.88          | 3.06          | 4.60                    | 4.54          | 3.80          |
| \(R^2\) (%)            | 5.73                    | 8.36          | 10.99         | 21.44                   | 19.17         | 14.13         |
| \(R^2_{OS}\) (%)       | 1.24***                 | 4.62***       | 7.94***       | 20.39***                | 18.82***      | 12.90***      |
| MSFE adj.              | 3.07                    | 4.05          | 4.66          | 9.26                    | 8.25          | 6.42          |

Note: This table reports the in- and out-of-sample forecasting performance of the FarmSkew measures constructed by Fisher skewness and Bowley skewness. The forecasting targets are the excess returns of holding 3-year, 5-year, and 10-year bonds for one year. The Newey-West \(t\) statistics are calculated with 12 lags. The \(R^2_{OS}\) is the Campbell and Thompson (2008) out-of-sample \(R^2\), which is tested by the Clark and West (2007) MSFE-adjusted statistic. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. The in-sample period is over 1995:01-2022:12, and the out-of-sample period is over 2000:01-2022:12. The FarmSkew measures are standardized for easy comparison.

 

Alt-text: Table showing performance metrics of FarmSkew with Fisher and Bowley skewness for 3-year, 5-year, and 10-year bonds.

**Table 7. Forecasting real economic condition**

| Macro indicator | \(\beta\) | t stat. | \(R^2\) (%) | \(\beta\) | t stat. | \(R^2\) (%) |
|-----------------|-----------|---------|-------------|-----------|---------|-------------|
|                 | **Skew**  |         |             | **FarmSkew** |         |             |
| RPCE            | 0.08      | 0.48    | 0.58        | -0.29**   | -1.96   | 8.27        |
| RINV            | 0.07      | 0.46    | 0.49        | -0.19     | -1.16   | 3.62        |
| REXP            | -0.30**   | -2.34   | 9.23        | -0.38**   | -2.53   | 14.39       |
| NPS             | 0.01      | 0.10    | 0.02        | 0.43***   | 3.97    | 18.72       |
| INDPRO          | -0.13     | -0.77   | 1.73        | -0.24*    | -1.79   | 5.76        |
| UNRATE          | -0.08     | -0.46   | 0.57        | 0.35***   | 2.29    | 12.08       |

Note: This table reports the regression results of forecasting future economic condition with GPSR. Skew and FarmSkew indicate original-GPR- and FARM-based GPSR measures, respectively. Macro indicators include annual growth rates of real personal consumption expenditures per capita (RPCE), real gross private domestic investment (RINV), real exports of goods and services (REXP), net private saving (NPS), and industrial production (INDPRO), and annual change of unemployment rate (UNRATE). For the quarterly RPCE, RINV, REXP, and NPS, we use the quarterly average of monthly GPSR measures and calculate Newey-West \(t\) statistics with 3 lags. For the monthly INDPRO and UNRATE, we calculate Newey-West \(t\) statistics with 12 lags. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. The sample period is over 1995:01-2022:12 or 1995Q1-2022Q4. All variables are standardized for easy comparison.

---

Alt-text: Table showing regression results for forecasting economic indicators using Skew and FarmSkew measures with coefficients, t statistics, and R-squared values.

**Table 8. Forecasting unexpected inflation**

| Inflation variable                 | Skew                      | FarmSkew                  |
|----------------------------------|---------------------------|---------------------------|
|                                  | \(\beta\) | t stat. | \(R^2\) (%) | \(\beta\) | t stat. | \(R^2\) (%) |
| Unexpected inflation             | 0.12      | 0.82    | 1.52       | -0.23**  | -2.36   | 5.30       |
| Unexpected demand-driven inflation | 0.21      | 1.35    | 4.41       | -0.32*** | -2.75   | 10.17      |
| Unexpected supply-driven inflation | -0.03     | -0.23   | 0.11       | 0.00     | -0.02   | 0.00       |

Note: This table reports the regression results of forecasting unexpected inflation with GPSR. Skew and FarmSkew indicate original-GPR- and FARM-based GPSR measures, respectively. Unexpected inflation is the difference between the actual inflation over the next 12 months and the corresponding inflation expectation from the Surveys of Consumers by University of Michigan. Unexpected demand- (supply-) driven inflation is the difference between the demand- (supply-) driven component of actual inflation over the next 12 months and the corresponding demand- (supply-) driven inflation expectation. Newey-West \(t\) statistics are calculated with 12 lags. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. The sample period is over 1995:01-2022:12. All variables are standardized for easy comparison.

 

Alt-text: Table showing regression results for forecasting unexpected inflation with Skew and FarmSkew measures, including coefficients, t statistics, and R-squared values.

**Table 9. GPSR and interest rate expectation error**

| Term      | Skew                |               |               | FarmSkew           |               |               |
|-----------|---------------------|---------------|---------------|--------------------|---------------|---------------|
|           | \(\beta\)           | t stat.       | \(R^2\) (%)   | \(\beta\)          | t stat.       | \(R^2\) (%)   |
| 3-month   | 0.21                | 1.36          | 4.21          | -0.39***           | -4.20         | 15.44         |
| 10-year   | 0.05                | 0.53          | 0.29          | -0.26**            | -2.40         | 6.57          |

Note: This table reports the regression results of forecasting interest rate expectation errors with GPSR. Skew and FarmSkew indicate original-GPR- and FARM-based GPSR measures, respectively. Interest rate expectation error is computed as the difference between the actual rate of 3-month Treasury bill or 10-year Treasury bond and the corresponding forecast from the Survey of Professional Forecasters (SPF) conducted by Philadelphia Fed. Newey-West \(t\) statistics are calculated with 3 lags. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. The sample period is over 1995Q1-2022Q4. All variables are standardized for easy comparison.

 

A table showing regression results of forecasting interest rate expectation errors with GPSR for 3-month and 10-year terms, including beta coefficients, t statistics, and R-squared values for Skew and FarmSkew measures.

**Table 10. GPSR and future credit spread**

| Credit spread | Skew                |                |               | FarmSkew           |                |               |
|---------------|---------------------|----------------|---------------|--------------------|----------------|---------------|
|               | \(\beta\)           | t stat.        | \(R^2\) (%)   | \(\beta\)          | t stat.        | \(R^2\) (%)   |
| BAA-AAA       | -0.01               | -0.19          | 0.01          | 0.28*              | 1.83           | 7.77          |
| AAA-Treasury  | 0.01                | 0.14           | 0.01          | 0.29**             | 2.46           | 8.36          |
| BAA-Treasury  | 0.02                | 0.32           | 0.03          | 0.33**             | 2.39           | 11.05         |

Note: This table reports the regression results of forecasting monthly credit spread changes with GPSR. Skew and FarmSkew indicate original-GPR- and FARM-based GPSR measures, respectively. BAA-AAA, AAA-Treasury, and BAA-Treasury represent the log spread between yields of Moody’s BAA and AAA corporate bonds with maturities 20 years and above, the log spread between yields of Moody’s AAA corporate bond and Treasury bond with maturity of 20 years, and the log spread between yields of Moody’s BAA corporate bond and Treasury bond with maturity of 20 years, respectively. Newey-West \(t\) statistics are calculated with 12 lags. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. The sample period is over 1995:01-2022:12. All variables are standardized for easy comparison.

 

Alt-text: Table showing regression results of GPSR and future credit spread with Skew and FarmSkew statistics for different credit spreads.

**Table 11. GPSR and the bid-to-cover ratio of Treasury auction**

| Dependent variable: Annual change of BCR | All maturities |  | Maturity ≤ 1 year |  | Maturity > 1 year |  |
|------------------------------------------|----------------|--|-------------------|--|-------------------|--|
|                                          | (1)            | (2) | (3)               | (4) | (5)               | (6) |
| **Panel A: Measuring GPSR with Skew**    |                |     |                   |     |                   |     |
| GPSR                                     | -0.27***       | -0.03 | -0.24***          | -0.10 | -0.16*            | -0.01 |
|                                          | (-3.98)        | (-0.30) | (-3.57)           | (-0.89) | (-1.89)           | (-0.10) |
| lagged BCR                               |                | 0.17 |                   | 0.23* |                   | -0.37*** |
|                                          |                | (1.28) |                   | (1.77) |                   | (-4.47) |
| Yield                                    |                | 0.48*** |                   | 0.42*** |                   | 0.01 |
|                                          |                | (3.95) |                   | (3.17) |                   | (0.05) |
| Supply                                   |                | 0.36*** |                   | 0.40*** |                   | 0.22*** |
|                                          |                | (4.33) |                   | (5.36) |                   | (2.67) |
| MOVE                                     |                | 0.43*** |                   | 0.46*** |                   | 0.45*** |
|                                          |                | (3.53) |                   | (3.43) |                   | (4.20) |
| Observations                             | 336            | 241 | 336               | 241 | 336               | 241 |
| Adj. \(R^2\)                            | 0.07           | 0.43 | 0.06              | 0.40 | 0.03              | 0.43 |

| **Panel B: Measuring GPSR with FarmSkew** |                |     |                   |     |                   |     |
| GPSR                                     | 0.24*          | 0.36*** | 0.26**            | 0.34*** | -0.13             | 0.04 |
|                                          | (1.92)         | (4.83) | (2.15)            | (4.03) | (-1.10)           | (0.67) |
| lagged BCR                               |                | 0.10 |                   | 0.10* |                   | -0.38*** |
|                                          |                | (1.00) |                   | (0.81) |                   | (-4.48) |
| Yield                                    |                | 0.47*** |                   | 0.38*** |                   | 0.02 |

 

Alt-text: Table showing regression results of GPSR and bid-to-cover ratio of Treasury auctions for different maturities and models.

|                | (4.28) | (2.84) | (0.16) |
|----------------|--------|--------|--------|
| Supply         | 0.32***| 0.33***| 0.22***|
|                | (5.12) | (4.90) | (2.76) |
| MOVE           | 0.41***| 0.44***| 0.44***|
|                | (5.07) | (4.84) | (4.38) |
| Observations   | 336    | 241    |        |
| Adj. \(R^2\)   | 0.06   | 0.56   |        |
|                | 336    | 241    |        |
|                | 0.07   | 0.51   |        |
|                | 336    | 241    |        |
|                | 0.02   | 0.43   |        |

Note: This table presents the results of the regressions examining the effect of GPSR on the bid-to-cover ratio (BCR) of Treasury action. The control variables include lagged BCR, Treasury yield, the ex-post Treasury supply, and the logarithm of Merrill Lynch Option Volatility Estimate (MOVE) index. “All maturities” means all Treasury auctions. “Maturity ≤ 1 year” means the auctions covering Treasury notes, bills, and 1-year bond. “Maturity > 1 year” means the auctions covering the Treasury bonds with maturities longer than one year. In panel A and panel B, the GPSR is original-GPR- and FARM-based, respectively. The sample period is over 1995:01-2022:12 for univariate regressions and 2002:12-2022:12 for multivariate regressions. The Newey-West \(t\) statistics in the brackets are calculated with 6 lags. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively. All variables are standardized for easy comparison.

Alt-text: Table showing regression results of GPSR effect on bid-to-cover ratio with statistics and significance levels.