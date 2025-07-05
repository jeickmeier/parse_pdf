# Optimal Allocation with Continuous Sharpe Ratio Covariance Bandits

Valeria Varlashova and Paul Alexander Bilokon

---

**Valeria Varlashova**  
is a postgraduate student in the Department of Mathematics at Imperial College London in London, UK.  
**valeria.varlashova23@imperial.ac.uk**

**Paul Alexander Bilokon**  
is a visiting professor in the Department of Mathematics at Imperial College London in London, UK.  
**paul.bilokon01@imperial.ac.uk**

---

### KEY FINDINGS

- Reinforcement learning methods successfully augment the existing portfolio optimization methods.  
- Some of these methods remedy the well-known deficiencies of the Markowitz framework.  
- The authors propose a novel continuous Sharpe ratio covariance (CSRC) algorithm, which outperforms the classical portfolio optimization methods.

### ABSTRACT

Optimal allocation is a crucial task in portfolio management and has been increasingly addressed in recent years through the integration of sequential decision-making problems within reinforcement learning, particularly within the framework of multi-armed bandit (MAB) problems. In this article, the authors propose a novel continuous Sharpe ratio covariance (CSRC) algorithm designed to optimize portfolio weight allocation by taking into account correlations between portfolios, utilizing a continuous semi-bandit framework. This risk-aware algorithm aims to achieve the best trade-off between reward, measured with the Sharpe ratio, and risk, measured with covariance. In this analysis, the authors compare the performance of the CSRC algorithm against traditional portfolio optimization techniques, including equally weighted, positive value, mean, and Sharpe ratio methods, along with more advanced bandit algorithms such as upper confidence bound (UCB), Thompson sampling, and probabilistic Sharpe ratio (PSR). The comparison demonstrates that the CSRC algorithm outperforms the other methods at a statistically significant level.

---

One of the main goals in financial decision making, particularly in portfolio management, is to optimally allocate capital and optimize the balance between risk and return. The classic Markowitz framework, introduced in Markowitz (1952), became the foundation of modern portfolio theory and is used to maximize returns of a portfolio for a given level of risk. The main idea of this framework is to determine the optimal combination of assets by balancing their expected returns with the risks associated with them. Markowitz also introduced the idea of diversification, which essentially says that investors can reduce risk by holding a combination of assets that are not perfectly correlated with each other. This framework, although popular, requires certain assumptions about the market environment, such as normality in returns and a static market environment, that do not represent real-world circumstances and can often assume suboptimal strategies when markets exhibit volatility, nonstationarity, and heavy tails in return distributions.

To address these challenges, recent research (e.g., Auer, Cesa–Bianchi and Fischer 2002) has explored the integration of reinforcement learning techniques, particularly the multi-armed bandit (MAB) framework, into portfolio optimization. The MAB is a classic framework in decision theory, in which an agent, or decision-maker, repeatedly chooses from a set of options, or *arms*, and receives a reward that corresponds to the chosen option. The objective is to maximize the cumulative rewards over time while balancing the trade-off between exploration of untried options with the exploitation of those that have performed the best up until that point. This framework has proved to be very applicable to financial markets, where continuous adaptation and learning from new data is essential. In this context, each arm in the MAB framework can represent a different asset or portfolio strategy, and the decision-maker’s objective is to maximize the cumulative returns over time while managing risk.

In this article, we’ll be using the Sharpe ratio as the *reward* to be maximized. The Sharpe ratio, which is the most widely used metric for comparing the performance of financial assets, describes how much excess return an investor receives for each additional unit of risk they take on. A higher Sharpe ratio indicates a higher investment return compared to the amount of risk. The primary contribution of this work is the development of the continuous Sharpe ratio covariance (CSRC) algorithm, designed to optimize the allocation of weights, which represent a proportion of capital, to different portfolios using a risk-aware continuous decision space setting that takes into account the covariance between portfolios. This algorithm is inspired by the continuous mean–covariance bandit (CMCB) framework introduced by Du et al. (2021), which is another recent development that extends the MAB problem to consider the covariance structure between arms.

The structure of this work is as follows. First, we provide a theoretical foundation of portfolio optimization, including an exploration of the Markowitz mean–variance framework, the Sharpe ratio, and extensions such as the post-modern portfolio theory (PMPT). Next, we introduce the MAB framework, discussing classic algorithms such as Epsilon–Greedy, upper confidence bound (UCB), and Thompson sampling, and explore their application in portfolio management. Finally, we detail the methodology of the CSRC algorithm and other Sharpe ratio approaches and present a comparison of the performance of the CSRC algorithm with that of the other algorithms.

---

### THEORETICAL FOUNDATIONS OF PORTFOLIO OPTIMIZATION

This section provides an overview of modern portfolio theory and introduces important concepts in portfolio optimization, such as the Markowitz mean–variance framework and efficient frontier, the Sharpe ratio, and the post-modern portfolio theory.

#### The Markowitz Mean–Variance Framework

The Markowitz framework was first introduced by Markowitz (1952) and is known as the mean–variance framework. This transformed the way portfolio optimization is perceived and introduced a way to balance risk and return. Before Markowitz, investment approaches primarily prioritized maximizing profits without an assessment of risk. Known as mean–variance optimization, the Markowitz framework introduced a way to build portfolios that maximize expected returns for a certain level of risk, setting the foundation for modern portfolio theory (MPT).

Markowitz proposed that investors should select portfolios by balancing the expected returns and risk, which is determined by the variance of portfolio returns. Consider a portfolio with $n$ assets. The expected return $\mu_p$ of the portfolio is given by:

$$\mu_p = \sum_{i=1}^{n} w_i \mu_i \quad (1)$$

where \(w_i\) is the weight of asset \(i\), and \(\mu_i\) is the projected return of asset \(i\). The risk, measured by the variance \(\sigma_p^2\) of the portfolio’s return, is given as

$$\sigma_p^2 = \sum_{i=1}^{n} \sum_{j=1}^{n} w_i w_j \sigma_{ij} \quad (2)$$

where \(\sigma_{ij}\) is the covariance between the returns of assets \(i\) and \(j\). The main idea behind Markowitz’s strategy is that diversification can reduce a portfolio’s risk. By combining assets that are not perfectly correlated, it is possible to reduce portfolio risk.

Markowitz also introduced the concept of the efficient frontier, which represents the set of portfolios that offer the higher expected return for a given level of risk, or equivalently, the lower risk for a given level of return. The efficient frontier is the solution to the following optimization problem:

$$\textit{Minimize } \sigma_p^2 = \sum_{i=1}^{n} \sum_{j=1}^{n} w_i w_j \sigma_{ij} \quad (3)$$

subject to:

$$\sum_{i=1}^{n} w_i \mu_i = \mu_p \quad \text{and} \quad \sum_{i=1}^{n} w_i = 1 \quad (4)$$

This problem can be solved using methods such as Lagrange multipliers, which give you the portfolio weights that minimize risk for a given return. The resulting portfolios define the efficient frontier, a concept that remains central to portfolio management to this day.

The Markowitz framework was groundbreaking and is still widely used, but it does have certain limitations. This framework assumes that returns are normally distributed, which simplifies the analysis but isn’t true in all financial markets. The model also requires an accurate estimation of the expected returns, variances, and covariances, which can be challenging in practice because of the large number of assets involved and because markets are constantly changing (Cvitanić, Lazrak, and Wang 2008; Markowitz 1952). To address these limitations, later developments in portfolio theory, including post-modern portfolio theory, extended the mean–variance framework by focusing on downside risk measures and nonnormal return distributions.

### The Sharpe Ratio

The Sharpe ratio, introduced by Sharpe (1964), is a very popular measure for assessing the performance of an investment. It is calculated as the ratio of the excess return of a portfolio (compared to the risk-free rate) to its standard deviation:

$$S_p = \frac{\mu_p - r_f}{\sigma_p} \quad (5)$$

where \(r_f\) represents the risk-free rate, \(\mu_p\) is the expected return of the portfolio, and \(\sigma_p\) is the standard deviation of the portfolio’s returns. The Sharpe ratio tells an investor how much they gain with each unit of risk they take on (Cvitanić, Lazrak, and Wang 2008).

The Sharpe ratio is commonly used in the field of finance to compare the performance of different investment portfolios or assets, especially those with different

levels of risk. A higher Sharpe ratio suggests that the returns are better compared to the amount of risk taken. A Sharpe ratio of less than one is considered poor, a Sharpe between one and two is considered good, a Sharpe between two and three is very good, and a Sharpe above three is considered excellent.

A limitation of the Sharpe ratio is that it assumes that returns follow a normal distribution and can’t tell the difference between upward and downward volatility. Because of this, other metrics, such as the Sortino ratio, have been developed to address the downside risk (Liu et al. 2021).

### Post-Modern Portfolio Theory (PMPT)

Post-modern portfolio theory emerged as an extension of the traditional Markowitz framework, addressing some of its key limitations, particularly its symmetric treatment of risk. PMPT focuses on downside risk, which is more aligned with investors’ natural aversion to losses (Liu et al. 2021).

**Risk measures:** In PMPT, risk is measured by downside deviation rather than standard deviation. Downside deviation only considers the negative deviations of returns from a minimum acceptable return (MAR), which better reflects the risks that investors are concerned about. The Sortino ratio is a variant of the Sharpe ratio that uses downside deviation as the risk measure:

$$
\text{Sortino Ratio} = \frac{\mu_p - MAR}{\sigma_D}
$$  
(6)

where $\sigma_D$ is the downside deviation. This metric provides a more accurate assessment of risk-adjusted performance for investors who are primarily concerned with avoiding losses.

Another important metric in PMPT is the omega ratio, which looks at the entire distribution of returns and takes into account both the probability and magnitude of gains and losses. It is calculated as:

$$
\Omega = \frac{\int_L^{\infty} [1 - F(r)] dr}{\int_{-\infty}^L F(r) dr}
$$  
(7)

where $L$ is the threshold return, and $F(r)$ is the cumulative distribution function (CDF) of returns. The omega ratio offers a comprehensive view of the risk–return trade-off, particularly in nonnormal return environments (Liu et al. 2021).

PMPT has been widely adopted in managing portfolios for risk-averse investors, such as retirement funds and insurance companies. By focusing on downside risk, PMPT aligns more closely with the real-world concerns of investors. It also introduces, however, an additional complexity because it requires more sophisticated methods to estimate downside risk measures and to apply them when constructing portfolios.

## REINFORCEMENT LEARNING AND BANDITS

### Introduction to the MAB Framework

The MAB problem is a fundamental model in sequential decision making, especially within reinforcement learning. The main idea is that an algorithm balances a trade-off between exploration and exploitation. This problem involves a scenario in which an agent (decision-maker) has to choose among several options, or arms, in which each option has an unknown reward distribution. The challenge is to balance

exploring different options to gain more information (exploration) and exploiting the best option given the information you have (Slivkins 2019). The MAB framework provides a structured approach to manage this trade-off, making sure that the decision-making process evolves to optimize outcomes over time.

This framework has applications in numerous fields, such as clinical trials, dynamic pricing, and online advertising, in which decisions are made repeatedly over time with the objective of maximizing cumulative rewards. For example, in online advertising, the decision-maker must decide which ad to show to a user to maximize click-through rates, balancing between ads that have performed well in the past and new ads that could potentially perform better.

Although the Markowitz framework remains the paradigm of modern portfolio theory, using a single strategy is not optimal because it is unable to adapt to a changing environment. In recent years, reinforcement learning has been used more extensively to construct portfolio strategies more optimally and solve the problem of portfolio strategies being able to adapt to different investment periods and nonstationarity.

The portfolio problem is turned into a multi-armed bandit problem, in which the arms are taken as different portfolio strategies. Consider a set of $K$ arms, where each arm $i$ is associated with a reward distribution $D_i$. The expected reward of arm $i$ is denoted by $\mu_i = \mathbb{E}[X_{i,t}]$. The objective is to maximize the cumulative reward over $T$ time steps:

$$
\mathbb{E} \left[ \sum_{t=1}^T X_{A_t} \right] \tag{8}
$$

where $A_t$ is the arm selected at time $t$. In this context, *regret* is the difference between the reward that would have been obtained by always playing the best possible arm and the reward actually obtained by following a given strategy (Slivkins 2019):

$$
R(T) = T\mu^* - \mathbb{E} \left[ \sum_{t=1}^T X_{A_t} \right] \tag{9}
$$

where $\mu^* = \max_i \mu_i$ is the expected reward of the optimal arm. Minimizing regret is equivalent to maximizing cumulative reward and serves as the primary goal in MAB problems.

### Classic Bandit Algorithms

**Epsilon-greedy algorithm:** The epsilon-greedy algorithm is one of the simplest methods for addressing the MAB problem. It works by selecting the arm with the highest estimated reward with probability $1 - \epsilon$ (exploitation), and a random arm with probability $\epsilon$ (exploration). This method makes sure that although the decision-maker primarily exploits the arm that currently seems to be the best, there is still a chance to explore other arms, which might turn out to be better than expected. All arms are explored over time, but with decreasing frequency as the algorithm focuses more on exploiting the best-known options (Combes et al. 2015).

The estimated reward $\hat{\mu}_i(t)$ for arm $i$ at time $t$ is updated based on the observed rewards:

$$
\hat{\mu}_i(t) = \frac{1}{N_i(t)} \sum_{s=1}^t X_{i,s} \mathbf{1}_{\{A_s = i\}} \tag{10}
$$

where $N_i(t)$ is the number of times arm $i$ has been selected up to time $t$, and $\mathbf{1}_{\{A_s = i\}}$ is an indicator function that equals one if arm $i$ was chosen at time $s$. The decision rule for selecting the next arm is given by:

$$
A_{t+1} = 
\begin{cases} 
\arg\max_i \hat{\mu}_i(t) & \text{with probability } 1-\epsilon \\
\text{random arm} & \text{with probability } \epsilon 
\end{cases}
\quad (11)
$$

With time, $\epsilon$ is usually reduced to focus more on exploitation, which allows the algorithm to converge toward the optimal arm more frequently (Slivkins 2019). This simple method forms the basis for more sophisticated exploration—exploitation strategies used in more advanced bandit algorithms, which we will explore next.

**Upper confidence bound (UCB) algorithm:** The upper confidence bound algorithm was proposed in Auer, Cesa-Bianchi, and Fischer (2002) and is a fundamental approach to the MAB problem. It works by selecting the arm that maximizes an upper confidence bound on the reward. The main idea is to balance exploration and exploitation by taking into account both the estimated reward and the uncertainty associated with this estimate (Slivkins 2019; Combes et al. 2015).

The UCB algorithm is defined as:

$$
A_{t+1} = \arg\max_i \left( \hat{\mu}_i(t) + \sqrt{\frac{2 \log t}{N_i(t)}} \right) \quad (12)
$$

where $\hat{\mu}_i(t)$ represents the estimated mean reward of arm $i$ at time $t$, and the term 

$$
\sqrt{\frac{2 \log t}{N_i(t)}}
$$ 

accounts for the uncertainty in the estimate. This uncertainty decreases as the arm is selected more frequently, which reflects the increased confidence in the estimated reward. By selecting the arm with the highest upper confidence bound, the algorithm essentially makes sure that arms with higher uncertainty (those that have been played less) are given a chance, therefore encouraging exploration (Degenne and Perchet 2016).

In the context of portfolio optimization, UCB has been applied to the problem of selecting different portfolio strategies. One of the significant challenges in portfolio optimization is that using historical returns to predict future performance is unreliable, and the mean—variance framework is not adequate when dealing with nonnormally distributed returns. Historical variance and covariance estimates often fail to capture the future behavior of assets, and the assumption of normally distributed returns underestimates risk and overestimates return (Markowitz 1952; Gasser, Rammerstorfer, and Weinmayer 2017).

To address these challenges, the UCB algorithm is employed as a nonparametric approach, which allows for portfolio selection without relying on the assumption of normally distributed returns. Shen et al. (2015) and other researchers have demonstrated that the UCB algorithm can effectively navigate the exploration—exploitation trade-off in portfolio selection by treating different portfolio choices as arms. Because this approach doesn’t depend on any specific assumption about the distribution, it is particularly useful when the distribution of returns is difficult to estimate accurately (Degenne and Perchet 2016).

Furthermore, the UCB algorithm has a logarithmic bound on regret (Karnin, Koren, and Somekh 2013):

$$
R(T) = O \left( \sum_{i \neq *} \frac{\log T}{\Delta_i} \right)
\quad (13)
$$

where $\Delta_i = \mu^* - \mu_i$ denotes the difference in expected rewards between the optimal arm and arm $i$. The logarithmic regret indicates that the performance of this algorithm...

improves steadily over time, making it highly effective for long-term decision making (Hou, Tan, and Zhong 2022).

**Thompson sampling:** This is a Bayesian method for solving the MAB problem, which has been gaining popularity in recent years because of its simplicity and effectiveness. In contrast to the UCB method, which follows a fixed rule in arm selection, Thompson sampling takes a probabilistic approach. At each time step, the algorithm samples a possible reward distribution for each arm and picks the arm with the highest expected reward (Karnin, Koren, and Somekh 2013).

In the context of portfolio optimization, Thompson sampling can be used to select between different portfolio allocation strategies, in which each strategy is treated as an arm. It continuously updates the posterior distribution based on observed returns and improves the selection process to favor strategies that perform well while still allowing for the exploration of less frequently chosen strategies (Hou, Tan, and Zhong 2022). This approach is useful in a financial setting in which the distribution of returns is complex and nonstationary.

### Extensions of the MAB Framework

The traditional MAB framework assumes a more simplified model of decision making in which each arm is independent, and the decision space is discrete. In real-world application, however, the environments are much more complex, with risk, covariance among arms, and combinatorial decisions. In this section we discuss some recent extensions to the classic multi-armed bandit problem, including risk-aware bandits, bandits with covariance, combinatorial and continuous bandits, and semi-bandits, which address different types of decision-making challenges.

**Risk-aware bandits:** In financial decision making, risk is as crucial as the expected return. Traditional bandit algorithms typically focus on maximizing the expected reward, but this can lead to decisions that are not optimal from a risk perspective. To address this, risk-aware bandit algorithms have been developed to incorporate risk measures such as variance into the decision-making process.

Sani, Lazaric, and Munos (2012) introduced the application of the classic mean–variance paradigm in bandits, formulating the mean–variance bandit problem in which the learner plays a single arm each time, and the risk is measured by the variance of individual arms. Vakili and Zhao (2015, 2016) further studied this problem under different metrics. The integration of variance as a risk measure aligns with the traditional mean–variance framework but adapted for the sequential nature of bandits. Zhu and Tan (2020) developed this further by creating a Thompson sampling–based algorithm for mean–variance bandits that incorporates variances directly into the sampling process and thus optimizes both risk and return. David and Shimkin (2016) explored Value at Risk (VaR) as a risk measure, and Galichet, Sebag, and Teytaud (2013) explored conditional Value-at-Risk (CVaR) as a measure for risk-aware bandits.

**Bandits with covariance.** Most existing studies on risk-aware bandits typically focus on combinatorial bandit problems, which assume a discrete decision space and are discussed further in the next section, and they don’t consider risk. Instead, they assume independence among arms, which limits their applicability in more complex environments such as the continuous mean–covariance bandit (CMCB) problem. The CMCB problem requires a continuous decision space, which is also discussed further in the next section and considers the covariance between arms, which makes it a more realistic model for financial applications in which asset returns are often correlated (Du et al. 2021). This framework allows the decision-maker to adjust the strategy based on the observed covariance between different arms. In this context, the agent, or the decision-maker, receives feedback not only on the rewards of the individual arms but also on how the rewards are correlated, which

can be very useful information in a portfolio management setting, in which the interaction between assets must be managed to optimize the risk–return profile of the portfolio (Du et al. 2021).  
In the stochastic MAB setting, covariance plays a significant role, especially in financial applications in which assets are often correlated. Several studies have addressed the issue of covariance in combinatorial bandit problems. Degenne and Perchet (2016) studied combinatorial semi-bandits with correlation, assuming a known upper bound on the covariance. They designed an algorithm that uses the assumed prior knowledge to improve decision making by adjusting strategies based on estimated covariance.  

**Combinatorial and continuous bandits.** Combinatorial bandits allow the decision-maker to choose combinations or a subset of arms at each time step and receive a combined reward based on the selected arms, whereas continuous bandits allow the decision-maker to choose a continuous vector, such as a weight vector, at each time step, and the reward is a function of the entire vector. In combinatorial bandits, the action space is discrete and becomes exponentially large because the decision-maker has to evaluate all possible combinations of arms. The challenge here is to explore this large action space efficiently while exploiting combinations that have shown high rewards.  
Continuous bandits have a continuous decision space rather than discrete, which allows the decision-maker to allocate weights, or capital, across a continuous range of options. The CMCB framework (Du et al. 2021) is a recent example of how a continuous decision space can be effectively used in bandit problems. In this framework the decision-maker is not limited to choosing from a finite set of discrete actions, but can actively adjust the allocation based on the information it receives. This approach can be particularly useful in portfolio management, in which the proportion of capital allocated to different assets or portfolios can be continuously adjusted and can offer greater flexibility.  

**Semi-bandits.** The semi-bandit problem is an extension of the classical MAB problem in which an algorithm pulls multiple arms at each stage instead of choosing a single arm at each time step, and the rewards of all pulled arms are revealed, not just the reward for a single arm (Combes et al. 2015).  
Let $S_t \subseteq \{1, 2, \ldots, K\}$ denote the subset of arms selected from a set of $K$ arms at time $t$, and let $X_{i,t}$ represent the reward from arm $i$ at time $t$. The total reward at time $t$ is then the sum of the rewards from the selected arms:  

$$
R(S_t,t) = \sum_{i \in S_t} X_{i,t} \tag{14}
$$

The goal is to maximize the cumulative reward over a sequence of $T$ time steps:  

$$
\mathbb{E} \left[ \sum_{t=1}^T R(S_t, t) \right] \tag{15}
$$

The difference with the single arm variant is that it takes into account the dependency among the arms, which makes it more complex because of the combinatorial nature of the action space (Degenne and Perchet 2016).  
The concept of regret in semi-bandits is similar to that of the MAB framework, but adapted to this setting. Regret is defined as the difference between the cumulative reward of the optimal set of arms and the cumulative reward obtained by the selected strategy:  

$$
R(T) = T \mu^*(S) - \mathbb{E} \left[ \sum_{t=1}^T R(S,t) \right] \tag{16}
$$

where $\mu^*(S)$ is the expected reward of the optimal subset $S$. Minimizing regret in this context requires the decision-maker to efficiently explore the exponentially large space of possible subsets while also exploiting the subsets that have shown high rewards (Combes et al. 2015; Audibert, Bubeck, and Lugosi 2014).

The feedback model in semi-bandits provides more information than in the classic MAB problem because the decision-maker observes the individual rewards for each arm in the selected subset, hence the feedback is more robust, which allows for more sophisticated learning algorithms. One can use the observed rewards to update the estimated value of each arm and improve the selection strategy over time (Degenne and Perchet 2016; Bubeck and Cesa-Bianchi 2012; Kveton et al. 2015).

## METHODOLOGY

### Continuous Sharpe Ratio Covariance Algorithm

This algorithm was inspired by the CMCB full-information feedback setting from Du et al. (2021), in which instead of adding an upper confidence bound, we penalize for the risk.

In our framework, we take a series of equity curves that we treat as portfolios. An equity curve represents the value of a strategy or asset over time, and we obtain an aggregate equity curve by combining the selected equity curves at each time step. The goal is to combine the individual equity curves in the most optimal way by strategically assigning weights to the equity curves in order to obtain the best aggregate equity curve possible.

We take the vector of observed increments between each time step $t$ for all equity curves as the *return*:

$$
\Delta \mathbf{x}_t = \mathbf{x}_t - \mathbf{x}_{t-1} \tag{17}
$$

where $\mathbf{x}_t$ represents the equity curves at time $t$.

We initialize the aggregate equity curve and weight vector that will be applied to the equity curves:

$$
\boldsymbol{\omega}_t = [\omega_t^1, \omega_t^2, \ldots, \omega_t^N], \quad \hat{C}_0 = 0 \tag{18}
$$

where $\boldsymbol{\omega}_t$ is the vector of weights assigned to the equity curves, $\omega_t^i$ is the weight assigned to equity curve $i$ at time $t$, and $\hat{C}_t$ represents the aggregate equity curve over time.

Let $\mu_t$ be the mean vector of the equity curve increments up to time $t$, and $\sigma_t$ the vector of standard deviations of equity curve increments up to time $t$. With the observed increment at each time step, we update the mean and standard deviation vectors,

$$
\hat{\mu}_t = \frac{1}{t} \sum_{s=1}^t \Delta \mathbf{x}_s, \quad 
\hat{\sigma}_t = \sqrt{\frac{1}{t-1} \sum_{s=1}^t \left( \Delta \mathbf{x}_s - \hat{\mu}_t \right)^2 } \tag{19}
$$

and update the covariance matrix structure,

$$
\hat{\Sigma}_t = \frac{1}{t} \sum_{s=1}^t \left( \Delta \mathbf{x}_s - \hat{\mu}_t \right) \left( \Delta \mathbf{x}_s - \hat{\mu}_t \right)^T \tag{20}
$$

Let $SR_t$ be the vector of Sharpe ratios of the equity curves up to time $t$, defined as

$$
\widehat{SR}_t = \frac{\mu_t}{\sigma_t} \tag{21}
$$

The Sharpe ratios are adjusted for risk with the interquartile range (IQR) of the Sharpe ratios observed so far,

$$
\widehat{f}_t(\omega) = \widehat{SR}_t - \big(IQR(\widehat{SR}_t)\big) \tag{22}
$$

and we formulate the risk-adjusted Sharpe ratio covariance function:

$$
f_t(\omega) = \widehat{f}_t(\omega) - \rho \omega_t^{T} \Sigma_t \omega_t \tag{23}
$$

where $\rho$ is the risk-aversion parameter. The weights for the equity curves are then updated based on the computed function, making sure they are nonnegative and normalized:

$$
\omega_t = \max(\omega_t, 0) \tag{24}
$$

$$
\omega_t = \frac{\omega_t}{\sum_{i=1}^d \omega_{t,i}} \tag{25}
$$

We then calculate the aggregate increment,

$$
\Delta C_{t+1} = \omega_t \cdot \Delta x_{t+1} \tag{26}
$$

where $\Delta x_{t+1} = x_{t+1} - x_t$. This aggregate increment is added to the aggregate equity curve so far to obtain the aggregate equity curve at the next time step:

$$
\widehat{C}_{t+1} = \widehat{C}_t + \Delta C_{t+1} \tag{27}
$$

The implementation of this algorithm is seen as follows.

| **Algorithm 1: Continuous Sharpe Ratio Covariance (CSRC) Algorithm** |
|-----------------------------------------------------------------------|
| **Input:** Total time steps ($T$), number of equity curves ($N$), risk aversion parameter ($\rho$) |
| Initialize the weight vector $\omega_0 = \mathbf{0}_N$ and aggregate equity curve $\widehat{C}_0 = 0$ |
| **for** each time step $t=1$ to $T$ **do** |
| &nbsp;&nbsp;&nbsp;&nbsp;**for** each equity curve $i=1$ to $N$ **do** |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Calculate the increment $\Delta x_t^i$ with Equation 17 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Update statistics according to Equations 19–20 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Calculate Sharpe ratios and adjust them for risk with Equations 21–22 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Compute the risk-adjusted SR covariance function <br>$f_t(\omega) = \widehat{f}_t(\omega) - \rho \omega_t^T \Sigma_t \omega_t$ |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Update the weight vector $w_t$ and normalize it |
| &nbsp;&nbsp;&nbsp;&nbsp;**end** |
| &nbsp;&nbsp;&nbsp;&nbsp;Calculate the aggregate increment $\Delta C_{t+1}$ according to Equation 26 |
| &nbsp;&nbsp;&nbsp;&nbsp;Update the aggregate equity curve $\widehat{C}_{t+1}$ with Equation 27 |
| **end** |
| **Output:** Aggregate equity curve ($\widehat{C}_T$) over time, final weight vector ($\omega_t$) at each time $t$ |

This algorithm optimizes the allocation of weights across a number of equity curves by balancing the Sharpe ratio with the associated risk, using a continuous semi-bandit covariance approach. In this algorithm, instead of adding an upper confidence bound, we are using the (IQR) to penalize equity curves that have higher variability in their performance, which is measured with the Sharpe ratios, and reduce the weight applied to them. The algorithm further penalizes the Sharpe ratio based on the portfolio’s overall risk, which is given by the covariance matrix and the portfolio weights, and the magnitude of this adjustment is controlled by a risk aversion parameter. This allows the algorithm to adjust the strategy based on the observed covariance between different arms, or equity curves.

This algorithm has a continuous action space, as it adjusts continuous weights assigned to different equity curves rather than selecting discrete actions or combinations, and is therefore a continuous bandit. The weights are real numbers that can take any value within a continuous range. The decision process involves adjusting the continuous weights assigned to each equity curve based on the Sharpe ratio and the covariance risk, and not simply selecting discrete subsets or combinations of arms, which further demonstrates that it is a continuous bandit problem rather than a combinatorial bandit. Furthermore, this algorithm represents a semi-bandit framework rather than an MAB framework because the algorithm pulls multiple arms at each stage instead of choosing just one arm at each step, and the reward of all the pulled arms are revealed.

### Optimized Sharpe Ratio Approaches

In this analysis, we follow the framework of Ozkaya and Wang (2020). We implement the various portfolio selection strategies outlined in this article using bandit algorithms, specifically UCB1, Thompson sampling, (TS), probabilistic Sharpe ratio (PSR), and a combined UCB-PSR (PW-UCB1) approach.

We have previously discussed that portfolio returns do not follow a normal distribution, and hence portfolio allocation with the classic Markowitz mean–variance framework underestimates the risk. Mertens (2002) showed that if returns are independently and identically distributed (i.i.d.), the assumption of normality can be ignored and the Sharpe ratio still follows a normal distribution. Christie (2005) generalized this result and relaxed the assumption of i.i.d. returns, and Opdyke (2007) showed that these two results are identical. These results combined give a Sharpe ratio that follows a normal distribution and has a closed-form solution for its variance that takes into account the third and fourth moments of the distribution of returns. This result is the basis for most of the algorithms we will be implementing.

Optimizing the Sharpe ratio has been a central goal in portfolio management for decades, with the objective being to maximize return relative to risk. In this section, we will review several algorithms that have been developed to enhance the Sharpe ratio by using different types of bandit methods, and which we will use to conduct an algorithm comparison with the continuous Sharpe ratio covariance algorithm. These include the probabilistic Sharpe ratio (Bailey and Prado 2012), UCB1, probability weighted UCB1 (PW-UCB1), and Thompson sampling.

**Probabilistic Sharpe ratio (PSR):** Bailey and Prado (2012) introduced the probabilistic Sharpe ratio as an improvement of the traditional Sharpe ratio, specifically designed to account for nonnormality and correlation in return distributions. The PSR evaluates the likelihood that a given Sharpe ratio is statistically significant, thus providing a more robust measure of performance.

The PSR is calculated as:

$$
PSR(SR^*) = \Phi \left[
\frac{\widehat{SR} - SR^* \sqrt{n-1}}{\sqrt{1 - \gamma_3 \widehat{SR} + \frac{\gamma_4 - 1}{4} SR^2}}
\right]
\tag{28}
$$

where $\widehat{SR}$ is the estimated Sharpe ratio, $SR^*$ is the target Sharpe ratio, $\gamma_3$ and $\gamma_4$ are the skewness and excess kurtosis of the returns, respectively, and $n$ is the number of observations. This adjustment allows for a more accurate assessment of whether a Sharpe ratio is significantly different from a benchmark, accounting for the higher moments of the return distribution.

**UCB1 algorithm:** For the application of the UCB to the portfolio choice problem, we follow the framework of Shen et al. (2015) and Ozkaya and Wang (2020), which combines the UCB with the classic Sharpe ratio.

Let $SR(k_i)$ be the Sharpe ratio of a portfolio, and $U_t(k_i)$ the uncertainty associated with that portfolio. For this algorithm, Hoeffding’s inequality is used to derive the upper confidence bound:

$$
\mathbb{P}[\mathbb{E}(X) > \bar{X}_t + u] \leq e^{-2 t u^2}
\tag{29}
$$

which can be represented as such for this setting:

$$
\mathbb{P}[SR(k_i) > \widehat{SR}_t + U_t(k_i)] \leq e^{-2 N_t(k_i) U_t(k_i)^2}
\tag{30}
$$

Setting this upper confidence bound to some $p$ and solving for $U_t(k_i)$, we get,

$$
p = e^{-2 N_t(k_i) U_t(k_i)^2} \implies U_t(k_i) = \sqrt{\frac{-\log p}{2 N_t(k_i)}}
\tag{31}
$$

where $N_t(k_i)$ represents the number of times portfolio $k_i$ has been picked. The upper confidence bound taken from Shen et al. (2015) gives the following objective function:

$$
f(k_i) = \widehat{SR}(k_i) + \sqrt{\frac{2 \log(N_t(k) + \tau)}{\tau + N_t(k_i)}}
\tag{32}
$$

where $N_t(k)$ refers to the number of rounds the algorithm has traded, and $\tau$ is the window size that’s used to estimate the Sharpe ratio and covariance matrix. To obtain the top two portfolios, the following function is applied:

$$
k_i^* = \arg \max_i f(k_i)
\tag{33}
$$

The first portfolio is selected from a set of portfolios $l$ that capture market variation, and the second portfolio is selected from portfolios that represent idiosyncratic risk. After the best portfolios are picked, the following first-order condition is applied in order to allocate capital such that the estimated variance is minimized:

$$
\lambda_p = \theta_p^2 \widetilde{\lambda}_{k_i} + (1 - \theta_p)^2 \widetilde{\lambda}_{k_j} \implies \theta_p^* = \arg \min_\theta \lambda_p = \frac{\widetilde{\lambda}_{k_j}}{\widetilde{\lambda}_{k_i} + \widetilde{\lambda}_{k_j}}
\tag{34}
$$

where $\lambda_p$ is the variance of portfolio $p$, $\theta_p$ is the weight that portfolio $k_i$ has on overall portfolio $p$, $\widetilde{\lambda}_{k_i}$ and $\widetilde{\lambda}_{k_j}$ are the variances associated with portfolios $k_i$ and $k_j$, respectively, and $\theta_p^*$ is the optimal value of $\theta_p$ that minimizes the portfolio’s risk, $\lambda_p$.

The final portfolio weights are then,

$$
\omega_p = (1 - \theta_k^*) \widetilde{H}_{k_i} + \theta_k^* \widetilde{H}_{k_j} \tag{35}
$$

where $\omega_p$ represents the final weight vector for portfolio $p$, and $\widetilde{H}_{k_i}$ and $\widetilde{H}_{k_j}$ represent the compositions of portfolios $k_i$ and $k_j$.

The first part in Equation 34 combines the variance contributions of the two chosen portfolios, $k_i$ and $k_j$, weighted by $\theta_p$ and $(1 - \theta_p)$, respectively. The second part, the optimal value resulting from the minimization of portfolio risk with respect to $\theta$, is a function of the relative risks of the two portfolios. And Equation 35 shows that the portfolio weights $\omega_p$ are a linear combination of the two portfolios’ compositions, weighted by the optimal $\theta_p^*$ and its complement $1 - \theta_p^*$.

Recall that the UCB algorithm essentially tries to maximize the upper confidence bound on expected reward, which in this case is the Sharpe ratio. As it picks the arm or portfolio with the highest upper confidence bound, it makes sure that the portfolios with higher uncertainty are chosen more, and the more those portfolios are chosen, their uncertainty decreases. The implementation of this algorithm is seen as follows.

---

**Algorithm 2: UCB1**

**Input:** Window size $\tau$, return matrix $R$

Initialize a reward array and an array that keeps account of how many times a certain portfolio is chosen;

for $t$ in $\{$whole sample period $-\tau\}$ **do**

- Get the covariance matrix of returns from predetermined window size;

- Get the eigenvalue decomposition, sort the eigenvalues and order the eigenvectors accordingly;

- Determine the index of median of eigenvalues $l$;

- Normalize the eigenvectors by its L1 norm, then obtain a new covariance matrix;

- Calculate the historical Sharpe ratio of each orthogonal portfolio, then apply the UCB1 policy function to each portfolio;

- Choose two candidate portfolios by doing $\arg\max$ over the UCB1 policy function, apply first-order condition;

- Store the return of the chosen portfolio and update the number of times each portfolio has been chosen for selected portfolios in the current round;

**end**

**Output:** The final portfolio weight vector $\omega_p$ and the portfolio returns at each time $t$

---

### Probability weighted UCB1 algorithm

The probability weighted UCB1 (PW-UCB1) algorithm is an extension of the UCB1 algorithm, which incorporates probabilistic weighting to better handle the combinatorial nature of the decision space. This algorithm, as opposed to UCB1, takes into account prior knowledge about a distribution. If we have no prior knowledge about a distribution and have to make an assumption, the UCB1 algorithm is helpful because it starts from scratch. But if we have prior knowledge about a distribution, this method may not be optimal and its performance can be improved upon.

We use the distribution of the Sharpe ratio proposed by Mertens (2002):

$$
SR \sim \mathcal{N}\left[\mu_{SR}, \frac{1 + 0.5SR^2 - \gamma_3 SR + \frac{\gamma_4 - 3}{4} SR^2}{n-1}\right]
\tag{36}
$$

Using this distribution, we maximize over

$$
\mathbb{P}(SR \leq \hat{SR}_i - SR^*)
\tag{37}
$$

The greater this probability, the greater the chance that an equity curve will achieve a higher Sharpe ratio compared to some threshold. We modify the UCB1 objective function and weight it by a factor derived from the distribution of the Sharpe ratio, and then select equity curves using this formula:

$$
k_i^* = \arg\max_i \mathbb{P}(SR \leq \hat{SR}_i - SR^*) f(k_i)
\tag{38}
$$

After this, the first-order conditions are applied once again to get the final weights. PW-UCB1 integrates UCB1 instead of maximizing the probability of the Sharpe ratio in order to allow the algorithm to explore different equity curves even if there is another curve that has a higher $\mathbb{P}(SR \geq SR^*)$. Here, $SR^*$ is the mean of Sharpe ratios for all equity curves, so this forces the UCB to create a curve that performs at least better than the average equity curve.

The implementation of this algorithm is very similar to that of UCB1, except for multiplying the UCB1 objective function by the probabilities obtained from the distribution previously mentioned by using the CDF of the standard normal distribution.

Thompson sampling: Thompson sampling is a Bayesian approach that focuses on drawing samples from a posterior distribution and uses the beta-Bernoulli model to select actions. In this context, Thompson sampling is used to select different portfolio strategies, for instance, UCB1, PW-UCB1, PSR, plus a mean–variance strategy and equally weighted strategy. For each strategy, the outcome at each time $t$ is considered either a success or failure, which represents the Bernoulli distribution, and the conjugate of which is the beta distribution:

$$
\mathbb{P}(X_i = 1 | Data) \sim Beta(\alpha, \beta)
\tag{39}
$$

where $X_i = 1$ is a success. At each time step, the parameters $\alpha$ and $\beta$ are updated on whether that round was a success or failure. If a certain strategy achieves the maximum return out of all the strategies in a particular time period, that strategy receives a success for that period. The $\alpha$ is updated for that strategy, $\alpha_{k,t} = \alpha_{k,t-1} + 1$, and for the other strategies, the $\beta$ is updated instead. The algorithm implementation can be seen in the following.

In the next section, we will perform a comparison of the continuous Sharpe ratio covariance algorithm with the algorithms outlined in this section, as well as an equally weighted method, a positive value method, a mean method, and a simplified Sharpe ratio method.

The *equally weighted method* is one of the simplest portfolio strategies, in which all assets or portfolios are allocated the same weight. In this context, all equity curves get assigned the same weight, regardless of their performance.

All weights are equally distributed from the start, and at each time step $t$ the method computes the weight vector $\boldsymbol{\omega}_t$ by assigning each equity curve a weight, in which $N$ is the total number of curves:

$$
\boldsymbol{\omega}_t = \frac{1}{N} \cdot \mathbf{1}_N  \tag{40}
$$

where $\mathbf{1}_N$ is a vector of ones of length $N$ that makes sure each equity curve gets an equal amount of the total allocation.

The *positive value method* aims to pick curves that are performing well by allocating weights to equity curves based on their most recent value. This method makes sure that only curves with positive values get assigned a weight and contribute to the aggregate equity curve.

---

**Algorithm 3: Thompson Sampling**

**Input:** window size $\tau$, equity curve matrix $\mathbf{R}$  

Initialize a reward array, an array that counts how many times a certain equity curve has been chosen, and two arrays that count the number of times a strategy succeeds or fails, respectively;

for $t$ in *{whole sample period - $\tau$}* do  
 Follow the steps in the previous algorithms to obtain three different sets of equity curve weights and include another weight set that gives equal weight to all curves;  
 Draw probabilities for each strategy from the beta distribution, where $\alpha$ and $\beta$ are the number of times a strategy succeeds or fails;  
 Choose the final strategy with $\arg\max_i \mathbb{P}(X_i = 1 | \text{Data})$, where $X_i=1$ indicates a success;  
 Store the increment (return) of the chosen equity curve and update all the arrays;  

end  

**Output:** Final equity curve weight vector $(\boldsymbol{\omega}_p)$ and the aggregate equity curve

---

At each time step $t$, we compute the weight vector $\boldsymbol{\omega}_t$ by picking the positive values from the most recently observed values of the equity curves:

$$
\boldsymbol{\omega}_t^i = \max(x_t^i, 0)  \tag{41}
$$

where $x_t^i$ is the value of the $i$th equity curve at time $t$. The weights are normalized to sum to one:  
$$
\boldsymbol{\omega}_t = \frac{\boldsymbol{\omega}_t}{\sum \boldsymbol{\omega}_t}
$$

The *mean method* allocates weights to equity curves based on their historical mean increments (returns). This method assumes that equity curves with higher average returns are more likely to perform well in the future and gives more weight to those equity curves.

At each time step $t$, we calculate the increment between each equity curve and update the rolling mean for each curve:

$$
\hat{\mu}_t^i = \frac{1}{t} \sum_{s=1}^{t} \Delta x_s^i  \tag{42}
$$

where $\Delta x_s^i = x_s^i - x_{s-1}^i$ is the increment of the $i$th equity curve between time steps $s - 1$ and $s$. The mean values $\hat{\mu}$ are used as the weights allocated to the curves, $\boldsymbol{\omega}_t = \max(\hat{\mu}_t, 0)$ and normalized to sum to one.

The simple Sharpe ratio method is an improvement of the mean method by incorporating both the mean and the standard deviation (risk) or increments to get the Sharpe ratio of each equity curve.  
At each time step $t$, we calculate the rolling Sharpe ratio for each equity curve,

$$
\widehat{SR}_t = \frac{\hat{\mu}_t}{\hat{\sigma}_t} \tag{43}
$$

where $\hat{\mu}_t$ is the rolling mean of the increments, and $\hat{\sigma}_t$ is the rolling standard deviation of increments. The weights are then allocated based on the Sharpe ratios, $\omega_t = \max(\widehat{SR}_t, 0)$ and normalized as usual.

### Algorithm Comparison

To compare all the methods that we have outlined in the previous section, we first generate 100 synthetic equity curves over a period of 1,000 time steps with a drift of 0.02 and volatility of 0.01. Exhibit 1 gives a visual representation of the generated equity curves. We apply each method to these equity curves to create an aggregate equity curve that represents the overall performance of each strategy. Exhibit 2 illustrates the aggregate equity curve for each method.

We conducted a simulation of 100 iterations using these synthetic equity curves, in which for each method we calculated the final aggregated profit and loss (PnL) at the end of each iteration. The methods compared include the equally weighted (EW), positive value (PV), mean, Sharpe ratio (SR), UCB1, Thompson sampling (TS), probabilistic Sharpe ratio (PSR), probability-weighted UCB1 (PW-UCB1), and continuous Sharpe ratio covariance (CSRC) algorithms. The summary statistics of the means and standard deviations of the final PnLs for each method over 100 iterations is presented in Exhibit 3.

---

**EXHIBIT 1**  
_100 Simulated Equity Curves_

[Figure: Plot titled "Equity Curves", showing 100 simulated equity curves over time (0 to 1000). The vertical axis is labeled "Value" and ranges approximately from -0.02 to 0.03. The curves are highly overlapping, showing variability from negative to positive returns.]

## EXHIBIT 2  
**Aggregate Equity Curve for Each Method**

| Panel | Method   | Description             |
|-------|----------|-------------------------|
| A     | EW       | Equity curve over time showing gradual increase to ~0.0015 value |
| B     | PV       | Equity curve rising toward ~0.0035 value             |
| C     | Mean     | Equity curve rising toward ~0.0040 value             |
| D     | SR       | Equity curve rising toward ~0.0040 value             |
| E     | UCB1     | Equity curve peaks early near 0.0015 then declines below zero and recovers |
| F     | PSR      | Equity curve rises steadily toward ~0.00275 value    |
| G     | PW-UCB1  | Equity curve rises, then dips negative, then partially recovers |
| H     | TS       | Equity curve slightly positive, dips negative, then recovers |
| I     | CSRC     | Equity curve rising steadily toward ~0.0075 value    |

*Axes in all panels: X-axis: Time; Y-axis: Value*

---

## EXHIBIT 3  
**Statistical Summary of Final PnL for Each Method**

| Method  | Mean PnL | Standard Deviation |
|---------|----------|--------------------|
| EW      | 0.00194  | 0.00096            |
| PV      | 0.00536  | 0.00191            |
| Mean    | 0.00536  | 0.00190            |
| SR      | 0.00535  | 0.00182            |
| CSRC    | 0.00783  | 0.00306            |
| UCB1    | 0.00192  | 0.00181            |
| TS      | 0.00186  | 0.00138            |
| PSR     | 0.00166  | 0.00161            |
| PW-UCB1 | 0.00182  | 0.00185            |

---

We can see that the CSRC method has the highest mean of 0.00783, which outperforms the other algorithms. This suggests that the CSRC method is quite effective in optimizing allocation, potentially by leveraging the covariance structure of the equity curves. This method also has a standard deviation of 0.00306, which is the highest of all the methods. This indicates that the CSRC algorithm has the potential to achieve high returns, but it also has a higher degree of variability in the outcomes. This demonstrates a trade-off between achieving higher returns and accepting higher risk, which reflects a more aggressive investment strategy in the context of portfolio management.

The EW method has a much lower mean PnL (0.00194) with a corresponding low standard deviation (0.00096), which is the lowest standard deviation out of all the methods. This indicates that this method is less risky but comes at a cost of much lower potential returns.

The PV, mean, and SR methods have higher mean PnLs of around 0.00536, with standard deviations ranging from 0.00182 to 0.00191. This shows that these methods offer a balance between risk and return and are relatively efficient in capturing returns while managing risk.

The PSR, TS, UCB1, and PW-UCB1 methods have the lowest mean values, ranging from 0.00166 to 0.00192. The PSR has the lowest mean PnL and a standard deviation of 0.00161, which indicates that it might not be as effective in this context compared to other methods. The slightly higher standard deviations of UCB1 (0.00181) and PW-UCB1 (0.00185) compared with their mean values suggest that these methods are vulnerable to higher variability in returns, which can potentially make them less reliable.

To look at the distribution of the final PnL across all methods, we generate a kernel density estimate (KDE) plot, shown in Exhibit 4. This plot shows a smoothed estimate of the density functions of the final PnL values.

We can see that the plot confirms our observations. The CSRC method outperforms the other methods and has a higher mean, although the spread is also wider, with fatter tails. We can see that it is the widest distribution, and the right tail extends to the highest mean PnL in the plot. It has the potential to achieve high returns, but also has the highest risk, as demonstrated by its high standard deviation. Its left tail is in line with those of the SR, PV, and mean methods, meaning the probability of negative outcomes is not greater or lower than these algorithms, but the right tail is

---

### EXHIBIT 4  
#### Comparison of the Distributions of All Algorithms

[Figure: Kernel Density Estimate (KDE) plot showing the density of final PnL values for various algorithms]

| Algorithm | Color  |
|-----------|---------|
| EW        | Blue    |
| PV        | Orange  |
| Mean      | Green   |
| SR        | Red     |
| CSRC      | Purple  |
| UCB1      | Brown   |
| TS        | Pink    |
| PSR       | Gray    |
| PW-UCB1   | Olive   |

Axes:  
- X-axis: Mean  
- Y-axis: Density

significantly longer, suggesting the possibility of capturing significantly higher returns in certain scenarios.

The EW method has the highest peak, and the PnL for this method is tightly clustered around a low mean value close to zero. This suggests this method might be more stable and predictable, which could be valuable in situations in which consistency is prioritized. The UCB1 method has a very similar mean as the EW method, but its standard deviation is almost double, which we can see in the wider curve and fatter tails, making it almost twice as risky. The PW-UCB1 method also has a slightly lower mean than the EW, with a standard deviation almost double that of the EW. The TS method has a relatively high peak and wider tails than the EW and is slightly skewed to the left, which pushes its mean slightly lower than that of the EW and may indicate that this method has a higher probability of negative outcomes. It is also riskier, with a higher standard deviation. The PSR method has the lowest mean PnL and has the biggest spread out of the methods whose mean PnLs are the nearest to zero. The PV, mean, and SR methods have a higher mean PnL and a wider spread with fatter tails. These methods offer potentially higher returns at the cost of increased risk and can be valuable in slightly more aggressive strategies in which higher risk is acceptable.

To determine if there is a statistically significant difference between CSRC and the other methods, we perform a Wilcoxon signed-rank test. We chose this test because it is nonparametric and does not assume normality. We can see from Exhibit 4 that our data is not necessarily normal and has heavy tails and skewness. This test is useful for paired comparisons and looks at whether the mean difference between the paired observations is zero. Our goal is to make paired comparisons, looking at the PnL of the CSRC with the other methods on the same set of equity curves across 100 iterations. We perform the test for each pairwise comparison with each method and apply a Bonferroni correction to control for the increased risk of a type I error (a false positive), which occurs when making multiple comparisons.

In Exhibit 5 we present the results of the Wilcoxon signed-rank test comparing the CSRC algorithm with the other algorithms.

We can see that this test gives evidence that the differences in performance between the CSRC and the other algorithms are statistically significant. The P-values are all extremely small, and all are smaller than the Bonferroni-corrected alpha, 0.00625, which means that there is a very low probability that the observed differences occurred by chance.

---

### EXHIBIT 5  
Wilcoxon Signed-Rank Test Results

| Comparison       | Wilcoxon Statistic | P-value           | Significant at $\alpha = 0.00625$? |
|------------------|--------------------|-------------------|------------------------------------|
| CSRC vs. EW      | 3.0                | $4.27 \times 10^{-18}$ | Yes                                |
| CSRC vs. PV      | 202.0              | $1.38 \times 10^{-15}$ | Yes                                |
| CSRC vs. Mean    | 199.0              | $1.27 \times 10^{-15}$ | Yes                                |
| CSRC vs. SR      | 196.0              | $1.17 \times 10^{-15}$ | Yes                                |
| CSRC vs. UCB1    | 15.0               | $6.12 \times 10^{-18}$ | Yes                                |
| CSRC vs. TS      | 5.0                | $4.53 \times 10^{-18}$ | Yes                                |
| CSRC vs. PSR     | 0.0                | $3.90 \times 10^{-18}$ | Yes                                |
| CSRC vs. PW-UCB1 | 14.0               | $5.94 \times 10^{-18}$ | Yes                                |

## CONCLUSION

This article has explored the intersection of portfolio optimization and reinforcement learning and developed a new algorithm for optimal portfolio allocation, the continuous Sharpe ratio covariance (CSRC) algorithm. We began by introducing modern portfolio theory and the relevant models in portfolio optimization, including Markowitz’s mean–variance framework and the Sharpe ratio, as well as discussing their limitations and how they have been addressed with a popular reinforcement learning framework called the multi-armed bandit (MAB) problem. We introduced some classic bandit algorithms, including epsilon-greedy, upper confidence bound (UCB), and Thompson sampling, as well as some more recent extensions to the MAB framework, on which our proposed CSRC algorithm is based on. The CSRC is a risk-aware semi-bandit algorithm that works with a continuous decision space and takes into account the correlation of different portfolios, or equity curves, using the covariance matrix.

We perform simulations and empirical analysis, comparing the CSRC algorithm to the other bandit methods for portfolio optimization that also utilize the Sharpe ratio as the reward, such as UCB1, Thompson sampling, and probabilistic Sharpe ratio. The comparison showed that the CSRC algorithm outperforms the other methods on a statistically significant level, achieving higher mean returns and maintaining a controlled level of risk.

An idea for further research is an improvement of the CSRC algorithm to better handle extreme market conditions, such as sudden and severe volatility spikes. Another idea is to explore incorporating other risk measures, such as conditional Value-at-Risk (CVaR) or downside risk metrics.

## ACKNOWLEDGMENTS

The first author would like to acknowledge the support of Masha Vyatkina.

## REFERENCES

Audibert, J. Y., S. Bubeck, and G. Lugosi. 2014. “Regret in Online Combinatorial Optimization.” *Mathematics of Operations Research* 39 (1): 31–45.

Auer, P., N. Cesa-Bianchi, and P. Fischer. 2002. “Finite-Time Analysis of the Multiarmed Bandit Problem.” *Machine Learning* 47: 235–256.

Bailey, D. H., and M. Lopez de Prado. 2012. “The Sharpe Ratio Efficient Frontier.” *Journal of Risk* 15 (2): 13.

Bubeck, S., and N. Cesa-Bianchi. 2012. “Regret Analysis of Stochastic and Nonstochastic Multi-armed Bandit Problems.” *Foundations and Trends® in Machine Learning* 5 (1): 1–122.

Christie, S. 2005. “Is the Sharpe Ratio Useful in Asset Allocation?” Working paper, Macquarie University.

Combes, R., M. S. Talebi Mazraeh Shahi, A. Proutiere, and M. Lelarge. 2015. “Combinatorial Bandits Revisited.” In *Advances in Neural Information Processing Systems* 28, edited by C. Cortes, N. Lawrence, D. Lee, M. Sugiyama, and R. Garnett, pp. 2116–2124. Montreal: Neural Information Processing Systems Foundation, Inc.

Cvitanić, J., A. Lazrak, and T. Wang. 2008. “Implications of the Sharpe Ratio as a Performance Measure in Multi-Period settings.” *Journal of Economic Dynamics and Control* 32 (5): 1622–1649.

David, Y., and N. Shimkin. 2016. “Pure Exploration for Max-Quantile Bandits.” In *Joint European Conference on Machine Learning and Knowledge Discovery in Databases,* pp. 556–571. Cham: Springer.

Degenne, R., and V. Perchet. 2016. “Combinatorial Semi-Bandit with Known Covariance.” In Advances in Neural Information Processing Systems 29, edited by D. D. Lee, U. von Luxburg, R. Garnett, M. Sugiyama, and I. Guyon, pp. 2972–2980. Red Hook: Curran Associates, Inc.

Du, Y., S. Wang, Z. Fang, and L. Huang. 2021. “Continuous Mean-Covariance Bandits.” Advances in Neural Information Processing Systems 34, edited by M. Ranzato, A. Beygelzimer, Y. Dauphin, P. S. Liang, and J. Wortman Vaughan, pp. 875–886. Red Hook: Curran Associates, Inc.

Galichet, N., M. Sebag, and O. Teytaud. 2013. “Exploration vs. Exploitation vs. Safety: Risk-Aware Multi-Armed Bandits.” In Proceedings of the 5th Asian Conference on Machine Learning, pp. 245–260. New York: Proceedings of Machine Learning Research.

Gasser, S. M., M. Rammerstorfer, and K. Weinmayer. 2017. “Markowitz Revisited: Social Portfolio Engineering.” European Journal of Operational Research 258 (3): 1181–1190.

Hou, Y., V. Tan, and Z. Zhong. 2022. “Almost Optimal Variance-Constrained Best Arm Identification.” IEEE Transactions on Information Theory 69 (4): 2603–2634.

Karnin, Z., T. Koren, and O. Somekh. 2013. “Almost Optimal Exploration in Multi-Armed Bandits.” In Proceedings of the 30th International Conference on Machine Learning, pp. 1238–1246. New York: Proceedings of Machine Learning Research.

Kveton, B., Z. Wen, A. Ashkan, and C. Szepesvari. 2015. “Combinatorial Cascading Bandits.” Advances in Neural Information Processing Systems 28, edited by C. Cortes, N. Lawrence, D. Lee, M. Sugiyama, and R. Garnett, pp. 1450–1458. Montreal: Neural Information Processing Systems Foundation, Inc.

Liu, X., M. Derakhshani, S. Lambotharan, and M. van der Schaar. 2021. “Risk-Aware Multi-Armed Bandits with Refined Upper Confidence Bounds.” IEEE Signal Processing Letters 28: 269–273.

Markowitz, H. 1952. “Portfolio Selection.” The Journal of Finance 7 (1): 77–91.

Mertens, E. 2002. Comments on Variance of the IID Estimator in Lo (2002). Working paper, University of Basel.

Opdyke, J. D. 2007. “Comparing Sharpe Ratios: So Where Are the P-Values?” Journal of Asset Management 8: 308–336.

Ozkaya, G., and Y. Wang. 2020. “Multi-Armed Bandit Approach to Portfolio Choice Problem.” Working paper, Barcelona Graduate School of Economics.

Sani, A., A. Lazaric, and R. Munos. 2012. “Risk-Aversion in Multi-Armed Bandits.” Advances in Neural Information Processing Systems 25, edited by F. Pereira, C. J. Burges, L. Bottou, and K. Q. Weinberger, pp. 3275–3283. Red Hook: Curran Associates, Inc.

Sharpe, W. F. 1964. “Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk.” The Journal of Finance 19 (3): 425–442.

Shen, W., J. Wang, Y. G. Jiang, and H. Zha. 2015. “Portfolio Choices with Orthogonal Bandit Learning.” In Proceedings of the Twenty-Fourth International Joint Conference on Artificial Intelligence, edited by Q. Yang and M. Wooldridge, pp. 974–980. Washington, DC: AAAI Press.

Slivkins, A. 2019. “Introduction to Multi-Armed Bandits.” arXiv:1904.07272v8.

Vakili, S., and Q. Zhao. 2015. “Mean-Variance and Value at Risk in Multi-Armed Bandit Problems.” In 2015 53rd Annual Allerton Conference on Communication, Control, and Computing (Allerton), pp. 1330–1335. New York: IEEE.

——. 2016. “Risk-Averse Multi-Armed Bandit Problems under Mean-Variance Measure.” IEEE Journal of Selected Topics in Signal Processing 10 (6): 1093–1111.

Zhu, Q., and V. Tan. 2020. “Thompson Sampling Algorithms for Mean-Variance Bandits.” In International Conference on Machine Learning, pp. 11599–11608. New York: Proceedings of Machine Learning Research.