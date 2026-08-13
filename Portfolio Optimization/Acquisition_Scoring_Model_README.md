# Acquisition Scoring Model

## Overview

This project develops a systematic screening and ranking framework for **lower-middle-market acquisition targets** using company financials, ownership structure, business-model characteristics, and post-acquisition value-creation potential.

The model converts raw company data into an acquisition pipeline by combining:

- hard investment filters,
- multi-entity ownership detection,
- financial quality and growth scoring,
- sellability and ownership analysis,
- priority classification, and
- value-creation scoring.

The objective is not to replace fundamental diligence. It is to make a large sourcing universe **more comparable, auditable, and actionable before deeper investment review**.

## Investment Screen

Companies must first pass a set of hard filters designed around the target acquisition profile.

| Criterion | Screen |
|---|---|
| EBITDA | €1M–€5M |
| Debt / EBITDA | ≤ 4.0x |
| Revenue Model | Excludes project-based businesses |
| EBITDA Consistency | No 2+ consecutive negative EBITDA years |
| Ownership / Group Structure | Screens VC/PE/corporate-owned multi-entity groups |

These filters focus the pipeline on businesses that are appropriately sized, financially viable, and structurally suitable for acquisition.

## Detecting Hidden Multi-Entity Groups

Legal entities do not always correspond neatly to economic businesses. To identify cases where operations may be fragmented across related companies, the model builds a **weighted group-signal score** using:

- shared ultimate shareholders,
- shared phone numbers,
- shared website domains, and
- shared addresses.

Shareholder, phone, and website matches receive greater weight than addresses because industrial parks and shared locations can create false positives.

Companies with strong group signals are flagged for deeper review, particularly where fragmented EBITDA or intercompany activity could distort the apparent economics of the target.

## Business Model & Ownership Classification

The pipeline classifies businesses as **recurring, project-based, mixed, or unclear** based on available company information. It also distinguishes B2B businesses from consumer-facing or unknown models.

Ownership is categorized as **family/founder-owned** or **VC/PE/corporate-owned**, while shareholder concentration and entity complexity are used to estimate transaction complexity.

These classifications allow financial performance to be interpreted alongside the practical characteristics that can affect sourcing and execution.

## Acquisition Scoring Framework

Companies that pass the hard filters receive three component scores.

### Quality Score

Measures financial health, profitability, cash generation, leverage, productivity, and earnings stability using:

- EBITDA margin,
- free-cash-flow-to-EBITDA conversion,
- debt-to-EBITDA,
- EBITDA per employee, and
- consecutive years of positive EBITDA.

### Growth Score

Measures operating momentum using:

- three-year revenue CAGR, and
- three-year EBITDA CAGR.

### Sellability Score

Measures transaction attractiveness and structural simplicity using:

- company age,
- number of legal entities,
- shareholder concentration, and
- ownership type.

The three scores are combined into a **3–30 total score**, which determines pipeline priority.

| Total Score | Priority |
|---|---|
| ≥ 24 | Very High |
| 20–23 | High |
| 16–19 | Medium |
| 12–15 | Low |
| < 12 | Exclude |

## Sourcing Categories

The model translates quantitative scores into sourcing actions.

**Low-Hanging Fruit** identifies very-high-priority, founder/family-owned companies with simple structures and no hidden-group flags.

**Hidden Gems** are high- or very-high-priority targets whose more complex ownership or entity structures warrant deeper diligence.

**Medium Prospects** are viable founder-led businesses suitable for follow-up, while hard-filter failures and low-priority companies are screened out.

This layer is intended to make the output useful for an investment team rather than simply producing a numerical ranking.

## Value-Creation Framework

The model also scores seven potential post-acquisition value-creation levers:

1. **Professionalization** — introducing systems, pricing discipline, CRM, and financial controls.
2. **Revenue Growth** — expanding sales capacity, geography, services, or products.
3. **Margin Expansion** — addressing supplier costs, overhead, and operating inefficiencies.
4. **Buy-and-Build** — identifying businesses that could serve as consolidation platforms.
5. **Pricing Power** — assessing opportunities to move toward value-based pricing or premium offerings.
6. **Customer Diversification** — reducing concentration risk where appropriate.
7. **Digital Transformation** — introducing software and automation into manual operating processes.

The resulting value-creation score provides a structured starting point for assessing **where returns could come from after acquisition**, rather than evaluating targets only on current financial performance.

## Financial Metrics

The model derives a standardized set of investment metrics from SABI company data, including:

- EBITDA margin
- cash-flow margin
- FCF / EBITDA conversion
- EBITDA per employee
- three-year revenue CAGR
- three-year EBITDA CAGR
- debt / EBITDA
- company age

Missing observations are treated as missing rather than zero, and company identifiers such as phone numbers and website domains are normalized before entity matching.

## Investment Workflow

The output is designed to support three stages of the investment process:

**Sourcing:** Rank targets, identify founder-owned opportunities, and focus outreach on the highest-priority companies.

**Due Diligence:** Independently validate hard-filter criteria, investigate complex entity structures, and assess the most relevant value-creation levers.

**Portfolio Management:** Compare realized operating performance with acquisition assumptions and identify which value-creation initiatives ultimately drove returns.

This creates a feedback loop in which realized outcomes can be used to refine the scoring framework over time.

## Key Takeaways

- **Screening should combine financial and structural information.** Attractive margins and growth do not automatically make a business executable as an acquisition.
- **Ownership structure can hide economic complexity.** Entity-resolution signals help identify businesses that require consolidated analysis.
- **Ranking should lead to an action.** Priority and sourcing categories translate model outputs into a practical acquisition pipeline.
- **Value creation belongs in the initial screen.** Assessing potential operating levers helps distinguish attractive businesses from attractive investments.
- **The model is a diligence prioritization tool, not a substitute for diligence.** Several classifications and value-creation assumptions require independent validation before an investment decision.

## Methods & Tools

`Private Equity Screening` · `Financial Ratio Analysis` · `Rule-Based Classification` · `Weighted Scoring Models` · `Entity Resolution` · `Data Cleaning & Normalization` · `Value-Creation Analysis` · `SABI`
