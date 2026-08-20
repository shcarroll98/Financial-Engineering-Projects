 Financial Engineering Projects

This repository includes coursework from UCLA's Master of Financial Engineering program and independent research
organized by topic area. Each project includes a notebook with the code and either an embedded explanation or a separate markdown.

The private company screening projects (Colombia fundamentals
screening, a Spain/SABI acquisition-sourcing pipeline) are from internship or research related work outside of the MFE program.

## Equity Research Sample

- **[PCA and Clustering for Return Prediction](equity-research/pca_and_clustering.ipynb)** —
  Compresses six stocks' returns into two PCA portfolios and shows out-of-sample R² is nearly
  unchanged vs. regressing on all six directly; separately, k-means clusters the 25 Fama-French
  size/book-to-market portfolios purely on realized return co-movement and recovers a size/value
  structure similar to the original sort. 

## Credit & Fixed Income Samples

- **[Merton Model for Credit Risk, and the LTCM Case](credit-and-fixed-income/merton_credit_risk.ipynb)**
  — Solves the Merton structural credit model (asset value, asset volatility, distance to
  default, default probability, expected recovery) as a nonlinear system via `fsolve`. 
  
- **[Black-Derman-Toy Interest Rate Tree](credit-and-fixed-income/bdt_interest_rate_tree.ipynb)**
  — Calibrates a BDT short-rate tree to exactly match an observed discount curve (30 maturities,
  bisection-based calibration), then prices a European call on a coupon bond via backward
  induction, with an American-exercise extension. 

## Portfolio Optimization Sample

- **[Feedforward Stochastic Discount Factor Network](portfolio-optimization/feedforward_sdf_network.ipynb)**
  — Implements a no-arbitrage SDF asset-pricing model as a small neural network in PyTorch,
  comparing `optimizer.step()` against a hand-written gradient-descent update to verify autodiff
  reproduces a manually-derived backward pass starting from the model’s error/loss and working
  backward through the neural network to calculate how much each parameter contributed to that error.
  

## Risk Management Sample

- **[Adaptive Deep Hedging](risk-management/adaptive-deep-hedging/adaptive_deep_hedging.ipynb)**
  — A neural-network hedging policy trained end-to-end to minimize tail risk (CVaR), benchmarked
  against Black-Scholes delta and Whalley-Wilmott hedging across GBM and Heston-simulated
  markets, transaction cost regimes, and a barrier option, with a regime-aware extension that
  survives volatility spikes outside its training range.
  
- **[VaR Backtesting, GARCH & Extreme Value Theory](risk-management/var_backtesting_and_evt.ipynb)**
  — Historical, exponentially-weighted, EWMA, and GARCH(1,1) Value-at-Risk, backtested against
  realized exceptions; an Extreme Value Theory approach that corrects the tail-risk
  underestimation of normal-distribution assumptions; and a live 2-day 99% VaR estimate for an
  S&P 500 position ahead of an FOMC announcement.
  
- **[Price-Dividend Ratio Decomposition](risk-management/pd_ratio_decomposition.ipynb)** —
  Decomposes the price-dividend ratio into cash-flow and discount-rate components from the
  Campbell-Shiller present-value identity, shows analytically and in a 10,000-period Monte Carlo
  simulation that discount-rate shocks dominate valuation variance, and fits a VAR(1) to test
  predictability of returns, the pd ratio, and dividend growth. 

---

**Also on my GitHub:** [credit-risk-classification](https://github.com/shcarroll98/credit-risk-classification)
(Logistic regression for loan default risk) · [Project4](https://github.com/shcarroll98/Project4)
(S&P 500 stock growth predictors) · [Project-Three](https://github.com/shcarroll98/Project-Three)
(ESG ratings & S&P 500 data engineering)

