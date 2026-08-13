# Adaptive Deep Hedging

### A Neural-Network Hedging Policy Trained End-to-End on Tail Risk

**UCLA Anderson — MGMTMFE 413: Machine Learning for Asset Management**

## Overview

**Research question:** Can a neural network learn a more robust option-hedging policy than classical delta-based methods when markets include transaction costs, stochastic volatility, and path-dependent payoffs?

This project implements a **deep hedging** framework in PyTorch in which a feedforward neural network acts directly as the hedging policy. Rather than minimizing average hedging error, the network is trained end-to-end to minimize **95% Conditional Value-at-Risk (CVaR)** of hedging losses.

The learned policy is benchmarked against:

- No hedge
- Black-Scholes delta hedging
- Whalley-Wilmott no-trade-band hedging

Testing spans vanilla and barrier options, geometric Brownian motion and Heston stochastic volatility, multiple transaction-cost regimes, and out-of-distribution volatility shocks.

## Why Deep Hedging?

Black-Scholes delta hedging is exact only under idealized assumptions: continuous trading, no transaction costs, constant volatility, and a correctly specified payoff model.

Real markets violate those assumptions.

Transaction costs penalize frequent rebalancing, volatility changes through time, and path-dependent instruments such as barrier options create exposures that a vanilla delta hedge does not fully capture.

Deep hedging reframes the problem as **stochastic optimization**. At each daily rebalance, a neural network observes the current market state and chooses the hedge position that minimizes tail risk across simulated paths.

## Model Architecture

The hedging policy is a feedforward multilayer perceptron with four state variables:

- log-moneyness, `log(S/K)`
- time to expiry
- current hedge position
- instantaneous volatility

The selected architecture contains **three hidden layers of 64 units with ReLU activations** and a scalar output representing the next hedge position.

Network depth was selected using held-out validation. The three-layer specification achieved the lowest validation CVaR among architectures with one through four hidden layers.

## Tail-Risk Objective

The network minimizes CVaR at the 95% confidence level rather than mean squared hedging error.

For loss \(L\),

\[
CVaR_{\alpha}(L)
=
\min_v
\left[
v + \frac{1}{1-\alpha}\mathbb{E}\left[(L-v)^+\right]
\right].
\]

The Rockafellar-Uryasev representation makes the tail-risk objective differentiable, allowing both the neural-network parameters and the auxiliary VaR parameter to be optimized using gradient descent.

This focuses training directly on the **worst 5% of hedging outcomes** rather than treating gains and losses symmetrically.

## Market Calibration & Simulation

The simulation environment is linked to observed equity-market behavior using **10 years of S&P 500 daily returns**.

A **GARCH(1,1) model with Student-t innovations** is fitted to the historical return series. The resulting analysis captures persistent volatility and fat-tailed returns and informs the volatility used in simulation.

Two price processes are implemented:

### Geometric Brownian Motion

GBM provides the controlled benchmark. In a frictionless GBM market, Black-Scholes delta is the theoretically correct hedge, allowing the pipeline to be sanity-checked against financial theory.

### Heston Stochastic Volatility

The Heston model introduces stochastic variance and negative spot-volatility correlation, creating an incomplete market in which no analytical optimal hedge exists.

Both simulators are implemented in PyTorch so the full hedging process remains differentiable during training.

## Training & Evaluation

Training uses online stochastic gradient descent:

- **1,200 gradient steps**
- **2,048 newly simulated paths per step**
- Adam optimization
- L2 weight-decay regularization
- fresh paths at every training step

Final performance is evaluated on **20,000 held-out simulated paths** never used during training.

Reported metrics include:

- mean hedging P&L
- P&L volatility
- CVaR95
- portfolio turnover
- paired statistical tests
- bootstrap confidence intervals

## Experiment 1 — Vanilla Call Under Transaction Costs

The baseline experiment prices a European call under GBM with **0.5% proportional transaction costs**.

| Method | Mean P&L | Std. P&L | CVaR95 | Turnover |
|---|---:|---:|---:|---:|
| Black-Scholes Delta | -4.147 | 0.585 | 5.631 | 1.711 |
| Whalley-Wilmott | -3.569 | 0.856 | 5.324 | 0.563 |
| **Deep Hedger** | **-3.763** | **0.679** | **4.966** | **0.975** |

The deep hedger reduced CVaR by **11.8% relative to Black-Scholes delta** and **6.7% relative to Whalley-Wilmott**.

It also reduced turnover by **43% relative to daily Black-Scholes delta hedging**.

Both CVaR improvements were statistically significant in the project's paired tests.

## Experiment 2 — Transaction-Cost Generalization

A network trained at a 0.5% transaction cost was evaluated across six cost regimes without retraining.

At and above the training cost, the learned policy matched or outperformed Whalley-Wilmott. At very low transaction costs, Whalley-Wilmott performed slightly better as the optimal policy approached continuous rebalancing.

The experiment illustrates an important limitation of learned policies: **robustness depends on how closely the training environment represents the environment in which the model is deployed.**

## Experiment 3 — Learning a No-Trade Region

Whalley-Wilmott predicts analytically that the optimal no-trade-band width scales with transaction costs to the one-third power.

Without being explicitly given this rule, the neural network learned the same qualitative behavior: its no-trade region widened monotonically as transaction costs increased.

The learned band was narrower than the analytical Whalley-Wilmott band, consistent with the difference in objectives: Whalley-Wilmott uses a mean-variance criterion, while the neural network directly minimizes tail CVaR.

## Experiment 4 — Heston Stochastic Volatility

Under Heston dynamics, the deep hedger observes realized instantaneous volatility while classical baselines use a fixed long-run volatility assumption.

| Method | CVaR95 |
|---|---:|
| Black-Scholes Delta | 6.024 |
| Whalley-Wilmott | 5.728 |
| **Deep Hedger** | **5.273** |

The learned policy improved CVaR by **7.9% relative to Whalley-Wilmott**.

This comparison includes an intentional information advantage: the network observes current volatility while the classical benchmarks use a constant volatility input. That distinction is treated as a model-design feature rather than hidden in the comparison.

## Experiment 5 — Barrier Option Hedging

The largest advantage appears for an **up-and-out barrier call**, where the payoff depends on the full path of the underlying.

| Method | CVaR95 |
|---|---:|
| Black-Scholes Delta | 5.281 |
| **Deep Hedger** | **4.099** |

The deep hedger reduced CVaR by approximately **22% relative to Black-Scholes delta**.

The mechanism is economically interpretable. As the underlying approaches the knock-out barrier, classical delta can require abrupt and expensive hedge adjustments. The network instead learns to reduce exposure earlier, producing a smoother anticipatory hedge.

## Experiment 6 — Regime-Aware Training

The primary extension tests whether training across multiple volatility environments improves robustness to market regime shifts.

A standard deep hedger trained at a fixed 20% volatility performed poorly when evaluated at an unseen crisis volatility of 45%.

The regime-aware model was instead trained across:

\[
\sigma \sim U(0.10, 0.40).
\]

At the unseen 45% volatility level:

| Model | CVaR95 |
|---|---:|
| Fixed-Volatility Deep Hedger | 16.50 |
| Whalley-Wilmott | 10.24 |
| **Regime-Aware Deep Hedger** | **10.88** |

Regime-aware training reduced tail loss by **34% relative to the fixed-volatility deep hedger** and brought performance to within roughly 6% of the analytical Whalley-Wilmott benchmark.

The network accomplished this by using its volatility input to widen its learned no-trade region during high-volatility environments.

## Experiment 7 — Drift Invariance

Derivative-pricing theory predicts that the optimal hedge should not depend on the expected return of the underlying.

The trained network was evaluated across drift assumptions from **0% to 20%**. CVaR varied by less than 0.01 across the tested range.

This provides an empirical integrity check that the network learned a hedge driven by **volatility and option state rather than directional return forecasts**.

## Results Summary

| Experiment | Setting | Result |
|---|---|---|
| Vanilla Call | GBM, 0.5% costs | 6.7% lower CVaR than Whalley-Wilmott; 43% less turnover than BS delta |
| Cost Generalization | Six cost regimes | Robust near/above training cost |
| No-Trade Band | Five cost levels | Learned qualitative transaction-cost scaling |
| Heston | Stochastic volatility | 7.9% lower CVaR than Whalley-Wilmott |
| Barrier Option | Path-dependent payoff | 22% lower CVaR than BS delta |
| Crisis Stress | Unseen 45% volatility | Regime-aware training reduced CVaR 34% vs. fixed-volatility deep hedger |
| Drift Invariance | 0%–20% drift | CVaR range < 0.01 |

## Key Takeaways

- **Optimize the risk that matters.** Training directly on CVaR targets severe hedging losses rather than average squared error.
- **Transaction costs change the optimal hedge.** The learned policy trades substantially less than daily delta hedging and develops a no-trade region.
- **Path dependence creates room for adaptive models.** The strongest improvement occurs for the barrier option, where classical delta hedging is structurally limited.
- **Robustness must be trained, not assumed.** A fixed-regime neural network can fail badly under volatility shifts; exposing the model to multiple regimes materially improves crisis performance.
- **Machine learning should still respect financial theory.** Zero-cost convergence toward Black-Scholes delta, transaction-cost-dependent no-trade behavior, and drift invariance provide checks that the model learned economically sensible relationships.

## Limitations

- Heston parameters are based on representative literature values rather than a formal calibration to options-market data.
- The lowest-cost no-trade-band experiments use a relatively coarse grid.
- The regime-aware model uses a uniform volatility distribution rather than one estimated directly from historical regime dynamics.
- An LSTM or other architecture with explicit path memory could potentially improve barrier-option hedging.

## Methods & Tools

`Deep Hedging` · `Neural Networks` · `PyTorch` · `CVaR` · `GARCH(1,1)` · `Student-t Innovations` · `GBM` · `Heston Stochastic Volatility` · `Black-Scholes Delta` · `Whalley-Wilmott` · `Monte Carlo Simulation` · `Stochastic Optimization` · `Bootstrap Inference`

## References

- Buehler, H., Gonon, L., Teichmann, J., & Wood, B. (2019). *Deep Hedging*. Quantitative Finance, 19(8), 1271–1291.
- Black, F., & Scholes, M. (1973). *The Pricing of Options and Corporate Liabilities*. Journal of Political Economy, 81(3), 637–654.
- Merton, R. (1973). *Theory of Rational Option Pricing*. Bell Journal of Economics and Management Science, 4(1), 141–183.
- Rockafellar, R. T., & Uryasev, S. (2000). *Optimization of Conditional Value-at-Risk*. Journal of Risk, 2(3), 21–42.
- Whalley, A. E., & Wilmott, P. (1997). *An Asymptotic Analysis of an Optimal Hedging Model for Option Pricing with Transaction Costs*. Mathematical Finance, 7(3), 307–324.

See the full project report for the complete literature review, mathematical formulation, experimental design, and additional references.
