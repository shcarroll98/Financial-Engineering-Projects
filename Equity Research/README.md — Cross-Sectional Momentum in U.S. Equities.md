# Cross-Sectional Momentum in U.S. Equities

## Project Overview

This project tests whether the **cross-sectional momentum anomaly** documented in the academic literature persists in U.S. equities over the period **1990–2024**.

Momentum refers to the tendency of stocks that have performed well relative to their peers to continue outperforming in the near term, while recent underperformers tend to continue underperforming.

Using monthly CRSP data, stocks are ranked according to their prior returns and sorted into ten momentum portfolios. The strategy then compares the subsequent returns of the highest-momentum stocks ("Winners") with those of the lowest-momentum stocks ("Losers").

The analysis asks three primary questions:

1. Do past winners continue to outperform past losers?
2. Is the resulting Winner-minus-Loser return statistically significant?
3. Can momentum returns be explained by conventional market, size, and value risk factors?

---

## Data

The analysis uses monthly U.S. equity data from the **CRSP Monthly Stock File** obtained through WRDS.

The sample covers:

**January 1990 – December 2024**

and includes securities traded on:

- NYSE
- AMEX
- NASDAQ

The primary variables used are monthly stock returns, prices, shares outstanding, trading volume, exchange codes, and security identifiers.

Market equity is calculated as:

\[
ME_{i,t}=|P_{i,t}|\times Shares_{i,t}
\]

Fama–French market, size, and value factors are subsequently incorporated to test whether momentum returns represent exposure to conventional systematic risk factors.

---

# Momentum Strategy

## 12–2 Momentum Signal

Stocks are ranked each month using a **12–2 momentum signal**, which measures cumulative past performance while excluding the most recent month.

Conceptually,

\[
MOM_{i,t}=\prod_{\tau=t-12}^{t-2}(1+R_{i,\tau})-1
\]

Skipping the most recent month helps separate medium-term momentum from very short-term return reversal effects.

Stocks are then sorted into **ten momentum deciles each month**.

- **Decile 1:** Lowest past returns — "Losers"
- **Decile 10:** Highest past returns — "Winners"

Equal-weighted monthly returns are calculated for each portfolio.

The primary momentum portfolio is:

\[
WML_t=R_{Winner,t}-R_{Loser,t}
\]

A positive WML return indicates that recent winners subsequently outperform recent losers.

---

# Performance Analysis

For the Winner, Loser, and Winner-minus-Loser portfolios, the analysis calculates:

- Mean monthly return
- Monthly volatility
- t-statistic
- Annualized return
- Annualized volatility
- Sharpe ratio
- Number of monthly observations

The results show a meaningful continuation pattern among high-momentum stocks. The Winner portfolio generated an average monthly return of approximately **1.53%**, indicating that stocks with strong prior performance continued, on average, to earn relatively strong subsequent returns.

More importantly, the Winner-minus-Loser portfolio provides a direct test of the momentum anomaly. Positive average WML returns indicate that the relationship is not simply a general equity-market effect: stocks with the strongest prior performance outperform stocks with the weakest prior performance.

The statistical significance of WML is evaluated using:

\[
t=\frac{\bar{R}_{WML}}
{s_{WML}/\sqrt{T}}
\]

This distinguishes persistent momentum performance from returns that could plausibly result from sampling variation.

---

# Cumulative Performance

The project also constructs the cumulative wealth of the Winner-minus-Loser strategy:

\[
Wealth_T=\prod_{t=1}^{T}(1+R_{WML,t})
\]

This analysis illustrates an important feature of momentum strategies: **positive long-run average returns do not imply smooth performance**.

Momentum can experience substantial drawdowns and periods in which the historical relationship between winners and losers temporarily reverses.

The cumulative-return series therefore provides information that the average return alone cannot capture, particularly regarding the path and consistency of momentum profitability.

---

# Has Momentum Weakened Over Time?

To examine whether the anomaly has remained stable, the sample is divided into two periods:

- **1990–2004**
- **2005–2024**

Mean WML returns and t-statistics are calculated separately for each period.

This comparison is economically important because momentum has become one of the most widely documented and traded equity anomalies. If momentum returns are materially weaker in the later period, several mechanisms could contribute:

- Greater institutional awareness of momentum
- Increased quantitative and factor-based investing
- Lower trading costs
- Faster information dissemination
- Greater arbitrage activity
- Crowding in systematic momentum strategies

A decline in profitability would therefore not necessarily invalidate the original momentum literature. Instead, it could indicate that the market environment changed after the anomaly became widely known and increasingly incorporated into professional investment strategies.

---

# Fama–French Factor Regression

Raw momentum returns may arise because the Winner-minus-Loser portfolio is systematically exposed to conventional sources of equity risk.

To investigate this possibility, WML returns are regressed on the Fama–French three factors:

\[
R_{WML,t}
=
\alpha
+
\beta_M(MKT-RF)_t
+
\beta_S SMB_t
+
\beta_H HML_t
+
\epsilon_t
\]

where:

- **MKT − RF** represents the market excess return
- **SMB** captures the size factor
- **HML** captures the value factor
- **α** measures abnormal momentum performance unexplained by these factors

The estimated monthly alpha is approximately **0.88%** and is statistically significant at conventional levels.

This is one of the most important findings of the project.

A positive and statistically significant alpha suggests that the momentum premium cannot be fully explained by exposure to the market, size, or value factors. In other words, the strategy's historical performance appears to contain a return component distinct from the traditional Fama–French risk factors.

This finding is consistent with momentum being a separate empirical return phenomenon rather than simply a repackaging of conventional equity factor exposures.

---

# Behavioral Interpretation

The persistence of momentum presents a challenge to the simplest form of the efficient-market hypothesis. If publicly observable past returns contain information about future relative performance, prices may not incorporate information instantaneously.

Several behavioral mechanisms could produce this pattern.

### Investor Underreaction

Investors may initially underreact to new fundamental information.

If positive information is incorporated into prices gradually, stocks receiving favorable information can continue appreciating after the initial announcement. Similarly, negative information may produce continued underperformance.

### Conservatism Bias

Investors may revise prior beliefs too slowly when new information arrives.

Rather than immediately adjusting valuations to reflect a change in fundamentals, investors may require repeated evidence before materially changing their expectations.

This gradual updating process can generate return continuation.

### Limited Attention

Investors have finite attention and processing capacity.

Information that is economically relevant to a company may therefore diffuse through the market gradually rather than being incorporated into prices immediately.

### Analyst Forecast Drift

Analyst expectations may also adjust gradually following new information.

If earnings forecasts and price targets are revised incrementally rather than immediately, changes in expectations can contribute to persistent price movements in the same direction.

### Confirmation Bias

Investors may overweight information consistent with their existing beliefs while discounting evidence that contradicts them.

This behavior can delay the incorporation of information that materially changes a company's outlook, contributing to subsequent price continuation as expectations eventually adjust.

---

# Interpretation

Overall, the results are broadly consistent with the historical momentum literature, including the return continuation documented by **Jegadeesh and Titman (1993)**.

The evidence suggests three main conclusions.

First, stocks with strong prior performance continued to generate relatively strong subsequent returns over the sample.

Second, the Winner-minus-Loser construction indicates that the effect is associated with **cross-sectional return continuation**, rather than simply positive aggregate equity-market performance.

Third, the positive Fama–French alpha suggests that conventional market, size, and value exposures do not fully account for the strategy's performance.

Taken together, the results are consistent with behavioral explanations centered on **investor underreaction and gradual information diffusion**.

At the same time, momentum should not be interpreted as a risk-free arbitrage opportunity. Its profitability varies substantially over time, and the strategy can experience significant periods of underperformance and reversal.

---

# Limitations

Several limitations should be considered when interpreting the results.

### Transaction Costs

The analysis evaluates portfolio returns before explicitly incorporating trading costs.

Momentum strategies can require substantial turnover, so commissions, bid-ask spreads, market impact, and other implementation costs could materially reduce realized returns.

### Equal-Weighted Portfolios

The analysis uses equal-weighted decile portfolios. As a result, smaller securities can have greater influence than they would in a value-weighted implementation.

### Survivorship and Security Filters

The analysis relies on the securities contained in the CRSP sample and applies exchange-based filters. Additional filters based on security type, price, liquidity, or share codes could affect the resulting portfolios.

### Factor Specification

The Fama–French regression uses the traditional three-factor model. Additional factors, particularly profitability, investment, and other systematic return characteristics, could provide a more comprehensive risk-adjusted performance test.

### Structural Change

The 1990–2024 sample spans major changes in market structure, trading technology, information dissemination, and quantitative investing. Momentum profitability therefore should not be assumed to be constant across the entire period.

---

# Key Takeaways

The empirical analysis provides evidence of cross-sectional momentum in U.S. equities between 1990 and 2024.

The strongest-performing stocks over the formation period subsequently earned higher average returns than weaker-performing stocks, while the Winner-minus-Loser strategy generated returns that were not fully explained by the Fama–French market, size, and value factors.

The results are consistent with the idea that **prices may adjust gradually to information**, allowing relative performance to persist over intermediate horizons.

However, the time variation in momentum performance and the practical importance of transaction costs illustrate the distinction between identifying an anomaly statistically and implementing it profitably in real markets.

---

## Methods & Tools

**Data:** CRSP via WRDS, Fama–French factors  
**Language:** Python  
**Libraries:** pandas, NumPy, statsmodels  
**Methods:** Cross-sectional portfolio sorting, momentum factor construction, hypothesis testing, cumulative-return analysis, subperiod analysis, OLS factor regression  
**Sample:** U.S. equities, 1990–2024