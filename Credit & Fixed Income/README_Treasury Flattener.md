# Investments HW4 — DV01-Neutral 2s10s Treasury Flattener

A backtest of a duration-neutral Treasury curve flattener: short the 2-year, long the 10-year,
DV01-matched and rebalanced weekly, with yields modeled via the Nelson-Siegel-Svensson (NSS)
curve. Performance is decomposed into spread, convexity, and time (carry + cash) components, and
compared across two margin/leverage regimes.

## Strategy overview

- **Trade:** short the 2-year zero, long the 10-year zero, sized so the position is DV01-neutral
  (`hedge_ratio = DV01_10 / DV01_2`).
- **Yield curve:** built from the Fed's GSW Nelson-Siegel-Svensson parameters
  (`BETA0–BETA3`, `TAU1`, `TAU2`), sampled at Friday closes.
- **Sample period:** 1983-12-30 to 2025-09-05, resampled weekly (`W-FRI`).
- **Capital:** $1,000,000 initial equity, margin-constrained gross exposure
  (`max_gross = equity / margin_rate`), rebalanced every week.
- **Financing:** uninvested/short-proceeds cash accrues interest at the model's 1-week yield.

## Cumulative return

The position is unwound and re-hedged every week: each week's P&L is split into a **carry** leg
(rolling last week's curve forward by one week) and a **yield** leg (the jump from last week's
curve to this week's curve at the rolled maturity), plus cash interest on the financing balance.
Cumulative return is `(1 + weekly_return).cumprod() - 1`.

## Convexity risk over time

For each week's DV01-neutral book, a ±10bp parallel shock is applied to the curve and the
resulting P&L is averaged (`0.5 * (PnL_up + PnL_down)`) to isolate the pure second-order
(convexity) effect, using the constant-maturity DV02 (`T² · P`) for each leg. This is tracked as a
time series rather than realized P&L — it's a measure of *how much convexity exposure the book is
carrying each week*, not what it earned.

## P&L decomposition (spread / convexity / time / residual)

Each week's realized P&L is attributed to:
- **Spread** — first-order return from the change in the 2Y and 10Y yields, weighted by DV01.
- **Convexity** — second-order return from the same yield changes, weighted by DV02.
- **Time** — carry/roll-down as the bonds age one week, plus interest on the cash balance.
- **Residual** — realized P&L minus the sum of the three components above.

> To gain a deeper understanding of the economic and risk factors driving the performance of the
> DV01-neutral 2s10s Treasury flattener strategy, the weekly profit and loss (P&L) was decomposed
> into its principal components: spread return, convexity return, time return, and a residual
> term. This decomposition isolates how much of the total return can be attributed to first-order
> yield spread movements, second-order convexity effects, and the passage of time through carry
> and roll-down. By distinguishing these sources, the analysis provides a clear view of which
> factors primarily determine the profitability and stability of the strategy. The results are
> summarized in the cumulative decomposition plot, where each component's contribution to the
> total return is visually represented.
>
> **Spread return.** The spread component represents the first-order return arising from changes
> in the 10-year and 2-year yields, weighted by their respective DV01 exposures. This term
> captures how the portfolio reacts to movements in the slope of the yield curve. In the plot, the
> spread line exhibits the largest swings and closely tracks the total cumulative P&L, indicating
> that most weekly gains and losses are driven by yield-curve dynamics. Positive performance
> occurs when the yield curve flattens (long-term yields fall relative to short-term yields),
> while steepening episodes cause temporary declines. Over the full sample, the spread return is
> the dominant driver of cumulative performance.
>
> **Convexity return.** The convexity component reflects the second-order (curvature) effect of
> yield changes on bond prices. Although the portfolio was constructed to be DV01-neutral, it
> retained residual convexity exposure because the 10-year leg possesses higher convexity than the
> 2-year leg. As a result, large parallel shifts in yields generated asymmetric price effects,
> producing modest gains when yields declined and small losses when yields rose. The convexity
> contribution remained relatively small and smooth over time, rarely exceeding a few thousand
> dollars per week. Nevertheless, it provided a slight stabilizing influence during volatile
> periods when long-term yields fell sharply, partially offsetting adverse spread movements.
> Overall, convexity effects were positive on average but not a material source of cumulative
> performance.
>
> **Time return.** The time component captures the combined impact of bond carry, roll-down along
> the yield curve, and interest accrued on the cash position. Each week, as the bonds aged by one
> week, their prices changed mechanically even if the yield curve itself remained static. This
> carry effect, combined with cash interest earned at the one-week Treasury rate, generated a
> consistent positive contribution over time. In the cumulative results, the time component
> exhibits a steady upward slope, reflecting the typical yield premium of the long bond relative
> to the short bond. Although modest in scale compared to the spread effect, this component added
> incremental stability and a small but persistent income stream throughout the sample period.
>
> **Residual return.** The residual component measures the portion of realized P&L not explained
> by the first three theoretical components. It encompasses numerical approximation errors,
> higher-order effects, and minor discrepancies inherent in weekly revaluation. In the results,
> the residual term oscillated closely around zero without exhibiting long-term drift, confirming
> that the analytical decomposition accurately reproduces the realized trading outcomes. This
> validates the internal consistency between the duration–convexity framework and the empirical
> portfolio simulation.
>
> **Overall interpretation.** The cumulative decomposition plot clearly indicates that spread
> returns overwhelmingly dominate the total P&L of the DV01-neutral flattener strategy, while time
> and convexity components provide smaller but stabilizing contributions. The negligible residual
> term further confirms the robustness of the model implementation and the numerical accuracy of
> the simulation. Economically, these results demonstrate that the flattener strategy's
> performance is primarily driven by changes in the yield-curve slope rather than by carry income
> or convexity asymmetry. Although the DV01-neutral structure effectively eliminates exposure to
> parallel shifts in yields, the trade remains sensitive to curve-slope dynamics, which ultimately
> determine its profitability over time.

*(Insert the cumulative decomposition plot from the notebook here.)*

## 10% vs. 2% margin

The same strategy is re-run with the margin requirement (and thus target leverage) lowered from
10% (~10x) to 2% (~50x), holding everything else fixed.

> Lowering the margin requirement from 10% to 2% significantly worsens the cumulative return of
> the DV01-neutral 2s10s strategy. At a 10% margin (around 10× leverage), the strategy remains
> relatively stable and delivers consistent positive performance. At a 2% margin (around 50×
> leverage), the excessive leverage amplifies convexity and curve-shape risks, causing the
> portfolio's equity to fall to very low levels.
>
> Thus, while a higher margin requirement supports sustainable performance, it also shows that
> increasing leverage does not necessarily lead to higher returns but instead magnifies risk and
> instability.

*(Insert the 2% vs. 10% margin comparison plot from the notebook here.)*

## Files

- `Hw4investments_Final.ipynb` — full notebook: NSS curve construction, weekly DV01-neutral
  backtest, convexity-risk series, P&L decomposition, and the 2%-vs-10%-margin comparison.
- `gsw_yields_2025.csv` — GSW Nelson-Siegel-Svensson yield curve parameters (not included in this
  repo if it's the instructor-provided dataset — add it to `.gitignore` or link to the Fed source
  instead of committing it, depending on your course's data-sharing policy).

## Running it

```bash
pip install pandas numpy matplotlib jupyter
jupyter notebook Hw4investments_Final.ipynb
```

Place `gsw_yields_2025.csv` in the same directory as the notebook before running.
