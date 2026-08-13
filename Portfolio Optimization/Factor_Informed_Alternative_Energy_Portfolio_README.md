# Factor-Informed Alternative Energy Portfolio

## Overview

**Research question:** Can a factor-informed, constraint-based portfolio improve downside risk and tracking error in a clean-energy ETF portfolio while preserving long-run returns?

This project constructs and backtests an active portfolio of five clean-energy ETFs — **ICLN, TAN, FAN, LIT, and QCLN** — using mean-variance optimization, macro-factor-informed expected returns, shrinkage, and walk-forward out-of-sample testing.

The final model improved risk-adjusted performance relative to an equal-weight benchmark, with the strongest gains coming from **better expected-return estimation and factor allocation rather than statistically significant alpha**.

## Investment Universe & Factor Framework

The portfolio was designed to capture distinct parts of the alternative-energy ecosystem:

| ETF | Exposure |
|---|---|
| ICLN | Diversified clean energy |
| TAN | Solar |
| FAN | Wind |
| LIT | Lithium and battery technology |
| QCLN | Clean energy and clean technology |

To understand systematic exposures, the analysis used **SPY, QQQ, and TLT** as proxies for market, growth, and interest-rate risk. **WTI crude oil** was later incorporated as a predictive macroeconomic factor to capture commodity and geopolitical dynamics.

Initial factor decomposition showed meaningful market exposure across all five ETFs, with additional growth sensitivity in several of the more long-duration clean-energy investments.

## Portfolio Construction

The first strategy used a benchmark-plus-active-tilt framework with the five clean-energy ETFs plus SPY, QQQ, and TLT as investable assets.

A baseline mean-variance optimizer proved unstable. With limited constraints, it generated large long and short positions and materially worse drawdowns than the equal-weight benchmark. Adding position constraints improved stability, but the optimizer continued to exploit noisy estimates rather than produce a robust portfolio.

This led to a structural change: **SPY, QQQ, and TLT were removed from the investable universe and instead used as information for expected-return estimation.** The final portfolio returned to the five clean-energy ETFs with long-only constraints and a 40% maximum weight per asset.

## Estimation Risk: Improving μ and Σ

A central finding was that **expected-return estimation was a larger source of instability than covariance estimation**.

With only a 36-month rolling estimation window, sample mean returns were noisy and caused large changes in optimized weights. The model therefore:

1. Smoothed factor inputs using a 12-month trailing average.
2. Combined factor-implied expected returns with historical mean returns.
3. Shrunk the combined expected-return estimate toward zero.
4. Re-estimated the covariance matrix using the current rolling training window.

Shrinking expected returns improved Sharpe ratio, volatility, and maximum drawdown. By contrast, Ledoit-Wolf covariance shrinkage alone did not materially improve results, suggesting that instability in **μ**, rather than **Σ**, was the more important problem in this relatively small ETF universe.

## Backtesting Framework

The strategy was evaluated using a **walk-forward, out-of-sample backtest**.

At each rebalance date:

- Expected returns were re-estimated using only information available at that point.
- Covariance matrices were recomputed from the current training window.
- Portfolio weights were held constant until the next scheduled rebalance.
- Performance metrics were calculated exclusively from out-of-sample returns.
- ETF, factor, and benchmark data were aligned to a common month-end index.

This structure was designed to prevent stale parameters and in-sample information from contaminating reported performance.

## Results

| Strategy | Annualized Return | Annualized Volatility | Sharpe | Max Drawdown |
|---|---:|---:|---:|---:|
| Strong-Shrink Historical μ | 12.18% | 22.93% | 0.531 | -47.26% |
| **Final Factor Model μ** | **12.49%** | **22.14%** | **0.564** | **-45.81%** |
| Equal-Weight Benchmark | 12.70% | 25.53% | 0.498 | -54.75% |

The final factor-informed portfolio sacrificed a small amount of raw return relative to the equal-weight benchmark while producing **lower volatility, a higher Sharpe ratio, and a maximum drawdown almost nine percentage points smaller**.

Monthly rebalancing produced the highest Sharpe ratio, but quarterly and semiannual results were similar, indicating that the improvement was driven primarily by **estimation quality rather than trading frequency**.

## Factor Attribution

A Fama-French regression showed that neither the strategy nor the benchmark generated statistically significant alpha.

Instead, the strategy's improved risk-adjusted performance was associated with **lower market exposure and more efficient factor allocation**. This distinction is important: the model improved the portfolio primarily through risk management rather than by uncovering persistent abnormal returns.

## Key Takeaways

- **Estimation discipline mattered more than optimizer complexity.** Improving noisy expected-return estimates contributed more than changing the optimization framework.
- **More investable factors did not necessarily improve the portfolio.** Allowing SPY, QQQ, and TLT into the optimizer amplified exposures; using them as information was more effective.
- **Risk-adjusted performance can improve without alpha.** The final strategy's advantage came from lower volatility, lower drawdown, and better factor allocation.
- **Out-of-sample design matters.** Re-estimating inputs at every rebalance and separating training from evaluation made comparisons more credible.
- **Portfolio construction is ultimately a signal-allocation problem.** The usefulness of a sophisticated optimizer depends heavily on the quality of the inputs it receives.

## Methods & Tools

`Mean-Variance Optimization` · `Factor Modeling` · `Expected-Return Shrinkage` · `Covariance Estimation` · `Fama-French Regression` · `Walk-Forward Backtesting` · `Risk Attribution` · `Python`

## Potential Extensions

Future work could expand the investable universe to hydrogen or nuclear-energy funds, incorporate macroeconomic regime signals, and explicitly model transaction costs within the optimization framework.
