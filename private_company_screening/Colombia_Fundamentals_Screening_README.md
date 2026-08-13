# Fundamentals-Based Screening of Private Companies in Colombia

## Overview

**Research question:** How can public-market factor-investing concepts be adapted to rank private companies when market prices and return histories are unavailable?

This project builds a fundamentals-based screening framework for Colombian private companies using standardized financial statements from the **Superintendencia de Sociedades (Supersociedades)**. The analysis adapts quality, value, and risk concepts to a private-markets setting, where accounting data rather than market prices provides the primary observable information.

The output is a cross-sectional ranking of firms by fundamental strength and risk, a sector-constrained candidate portfolio, and a separate broad-sector allocation view.

Importantly, this is **not an expected-return model**. Because the dataset contains no market-price or return series, the resulting rankings cannot be validated as predictors of future investment performance.

## Data

The analysis uses IFRS-based financial statement data reported by Colombian companies to Supersociedades.

Inputs include:

- Revenue and operating income
- Total assets and liabilities
- Property, plant & equipment (PP&E)
- Intangible assets
- Payables
- Financing costs and interest expense
- EBITDA proxies
- CIIU industry classifications
- Company identifiers

Most observations represent FY2024, making the analysis primarily **cross-sectional rather than time-series based**.

## Data Engineering & Validation

A major part of the project involved identifying and correcting structural issues in the underlying filings.

Supporting notes for PP&E, intangibles, payables, and revenue are reported as long-format rollforward schedules. An initial extraction method could therefore select stale balances, double-count totals and subcomponents, or confuse quarterly revenue with fiscal-year revenue.

The corrected pipeline:

1. Filters each note table to the economically appropriate reporting concept.
2. Matches observations by company identifier and reporting date.
3. Retains the most recent valid reporting period.
4. Separates totals from their underlying subcomponents.
5. Applies accounting sanity checks to validate the resulting data.

After correction, PP&E and intangible-asset ratios no longer exceeded total assets and negative asset-category balances were eliminated.

This validation step materially changed the inputs to the screening model and reinforced a central principle of the project: **a sophisticated scoring framework is only as credible as the accounting data underneath it.**

## Fundamental Factor Construction

Company characteristics are standardized cross-sectionally using z-scores so that firms can be compared relative to peers.

The model focuses on several economically motivated dimensions:

### Profitability
- Operating margin
- Return on assets

### Liquidity & Debt Capacity
- Current ratio
- Interest coverage

### Leverage & Financial Risk
- Debt-to-assets
- Financing-cost burden
- Past-due payables

### Asset Backing
- PP&E-to-assets

These characteristics are combined into two parallel scoring systems: a quality/safety/value framework for reference ranking and a fundamental-strength-versus-risk framework used for candidate selection.

## Fundamental Strength & Risk Indicators

Because realized returns are unavailable, the model deliberately avoids treating accounting characteristics as estimated expected returns.

Instead, a **fundamental strength indicator (`mu_proxy`)** combines profitability, liquidity, asset backing, and interest coverage.

A separate **risk indicator (`risk_proxy`)** captures leverage, overdue-payables exposure, and financing-cost burden.

The final company score balances the two:

`score_net = fundamental strength - 0.70 × risk`

The weights are fixed, disclosed assumptions grounded in corporate-finance intuition rather than coefficients estimated from realized investment outcomes.

## Portfolio Construction

Companies with positive net scores are ranked and the top 50 are retained as the candidate portfolio.

Portfolio weights are:

- proportional to company `score_net`,
- capped at **8% per company**,
- capped at **25% per fine-grained CIIU industry**, and
- renormalized after constraints are applied.

The sector caps prevent a small number of highly ranked firms or industries from dominating the candidate portfolio while preserving the information contained in the fundamental ranking.

The resulting top holdings span industries including professional services, manufacturing, hotels, broadcasting, real estate, machinery distribution, fund administration, agriculture, and wood products.

## Sector Analysis

A separate macro-level analysis maps companies into nine broad economic groups:

- Professional Services
- Manufacturing
- Real Estate
- Technology
- Agriculture
- Energy / Mining
- Construction
- Trade
- Other

Sector strength is based on average company score adjusted for the number of firms in the group.

During implementation, a normalization issue revealed that negative aggregate sector strength could invert the intended ranking. The corrected methodology floors negative sector strength at zero before normalization.

Under the corrected model, the strongest broad exposures were:

| Broad Sector | Weight |
|---|---:|
| Professional Services | 53.05% |
| Manufacturing | 20.94% |
| Real Estate | 19.63% |
| Technology | 6.38% |

The broad-sector view is intentionally separate from the company-level portfolio. The latter remains considerably more diversified because its 25% cap operates at the much finer CIIU-industry level.

## Methodological Diagnostics

Several findings emerged from testing the methodology itself.

### Avoiding Selection Circularity

Factor importance cannot be assessed on a subset that was selected using those same factors without creating circularity. Diagnostics were therefore moved to the **full pre-selection universe**, while portfolio construction continues to use the filtered candidate set.

### Recognizing an Unidentifiable Factor-Weighting Problem

An early approach attempted to estimate factor importance using the mean of each factor's standardized z-score divided by its standard deviation.

On the full population, however, a z-score has mean zero and standard deviation one **by construction**. The proposed signal-to-noise statistic therefore cannot distinguish economically meaningful factors from irrelevant ones.

Rather than retain a calculation that appeared data-driven but was mathematically incapable of identifying factor importance, it was removed.

### Distinguishing Assumptions from Estimated Relationships

Without a return series or later-period operating outcome, the model cannot empirically estimate which accounting characteristics predict future performance.

The final framework therefore uses transparent, economically motivated fixed weights and labels them explicitly as assumptions.

## Economic Interpretation

Within this dataset, companies with stronger **profitability, liquidity, debt-servicing capacity, and asset backing**, combined with lower leverage and financial distress indicators, rank more favorably.

The model also provides a lens into macroeconomic exposure. Real estate and manufacturing contribute real-asset exposure, while professional services and technology provide greater exposure to domestic productivity and human capital.

At the company level, stronger interest coverage and moderate leverage can also indicate greater resilience to tightening credit conditions.

These are **characteristic-based interpretations**, not claims that the factors have been statistically demonstrated to generate excess returns.

## Key Takeaways

- **Public-market factor concepts can be adapted to private-company financial statements**, but their interpretation changes when prices and realized returns are unavailable.
- **Data validation can matter more than model sophistication.** Understanding the structure of accounting filings prevented economically impossible ratios and distorted inputs.
- **A model should not imply more statistical certainty than the data supports.** Without an outcome variable, factor weights are assumptions rather than estimated predictors.
- **Diagnostics must be independent of selection.** Evaluating factors on the same subset they helped select creates circular conclusions.
- **Portfolio constraints translate rankings into investable structure.** Company and industry caps prevent fundamental scores from producing excessive concentration.
- **Unexpected results are often model diagnostics.** The inverted sector ranking exposed a normalization problem that materially changed the final allocation.

## Methods & Tools

`Fundamental Analysis` · `Factor Modeling` · `Cross-Sectional Standardization` · `Financial Statement Analysis` · `Private-Market Screening` · `Portfolio Construction` · `Sector Constraints` · `Data Validation` · `Python`

## Limitations & Next Steps

The largest limitation is the absence of a second period of financial data or a realized outcome variable.

With additional years of data, the framework could move from assumption-based ranking toward empirical validation by testing whether characteristics predict:

- subsequent revenue or EBITDA growth,
- survival or financial distress,
- fundamental improvement,
- earnings volatility,
- sensitivity to interest rates, exchange rates, or commodity prices.

Longer panel data could also support rolling factor estimates, structural-break analysis, and cross-country comparisons.

The key next step is therefore not simply adding model complexity; it is obtaining **an independent outcome against which the model's assumptions can be tested**.
