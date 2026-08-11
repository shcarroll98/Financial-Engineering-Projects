# Acquisition Sourcing Pipeline — Spain (SABI Data)

A search-fund-style deal-sourcing pipeline that screens private Spanish companies down to a
prioritized, callable target list, built on SABI (Iberian company registry) financial data.

## What it does

1. **Hard filters** exclude companies that don't fit an acquisition thesis before any scoring
   happens: EBITDA between €1–5M, debt-to-EBITDA under 4x, no more than one year of negative
   EBITDA, recurring (not project-based) revenue, and no VC/PE parent combined with a
   multi-entity ownership structure.
2. **Hidden-group detection** flags companies that are really fragments of a larger ownership
   structure, matching on shared shareholder name, phone number, website domain, and registered
   address — weighted differently, since a shared industrial-park address is much weaker evidence
   than a shared shareholder or phone number.
3. **Three component scores** (Quality, Growth, Sellability, each 1–10) combine into a
   `TOTAL_SCORE` (3–30) that drives a `PRIORITY` tier (VERY HIGH / HIGH / MEDIUM / LOW / EXCLUDE).
4. **Seven value-creation-lever scores** (professionalization, revenue growth, margin expansion,
   buy-and-build, pricing power, customer concentration, digital transformation) flag *why* a
   given target is attractive for post-acquisition improvement, not just that it clears the bar.
5. **Category assignment** (Low-Hanging Fruit / Hidden Gem / Medium Prospect / Exclude) maps each
   qualified company directly to a sourcing strategy.
6. **Excel export** produces a 9-sheet workbook built for a calling team, not just an analyst —
   including a `QUALIFIED_LEADS` executive summary and an `ACTION_LIST` sheet with blank
   call-status and notes columns.

## Hard filters (automatic exclusions)

| Filter | Threshold | Rationale |
|---|---|---|
| VC/PE/corporate parent | Exclude if `Ownership_Type = VC/PE/CORP` and `GROUP_SIGNAL_SCORE ≥ 6` | Targets should be independent, founder-led, or family-owned |
| EBITDA range | €1M – €5M | Fits the mid-market SME segment |
| Debt-to-EBITDA | Max 4.0x | Overleveraged targets carry limited acquisition capacity and refinancing risk |
| Revenue predictability | Exclude if business model is project-based | Recurring revenue (contracts, subscriptions) is more valuable than lumpy project work |
| EBITDA consistency | Max 1 consecutive negative year | 2+ years of losses indicates structural problems, not a temporary dip |

## Multi-entity / hidden-group detection

`GROUP_SIGNAL_SCORE` (0–10) sums weighted signals across companies:

| Signal | Weight | Match basis |
|---|---|---|
| Shared shareholder (GUO name) | 3 | Same Global Ultimate Owner name in ≥2 companies |
| Shared phone number | 3 | Same cleaned number (spaces/hyphens/`+34` stripped) in ≥2 companies |
| Shared website domain | 3 | Same domain (protocol/path ignored) in ≥2 companies |
| Shared address | 1 | Same street + postal code + city — lowest weight, since an industrial park can share an address without being the same ownership group |

`FLAG_HIDDEN_GROUP = "Yes"` if the company has VC/PE ownership with any group signal, or a group
signal score ≥ 6 regardless of ownership type — either case warrants deeper diligence for
fragmented economics or cross-subsidiary transactions before treating the target as one clean
entity.

## Scoring system (1–10 scale each, summing to a 3–30 `TOTAL_SCORE`)

**QUALITY_SCORE** — profitability, cash generation, leverage, productivity, and earnings
stability (EBITDA margin, FCF-to-EBITDA conversion, debt-to-EBITDA, EBITDA per employee, years
of consecutive positive EBITDA).

**GROWTH_SCORE** — 3-year revenue and EBITDA CAGR.

**SELLABILITY_SCORE** — company age, ownership type (family/founder scores higher — cleaner
negotiation), shareholder concentration (fewer shareholders scores higher), and structural
simplicity (single entity vs. a multi-entity group).

| Score | Priority |
|---|---|
| ≥24 | VERY HIGH |
| 20–23 | HIGH |
| 16–19 | MEDIUM |
| 12–15 | LOW |
| <12 | EXCLUDE |

## Value-creation levers (1–10 each, independent of the acquisition-fit score)

| Lever | Scores higher when | Opportunity |
|---|---|---|
| Professionalization | Family/founder-owned + company age >20y | Replace intuition-driven management with systems, CRM, financial controls |
| Revenue growth | Revenue CAGR <5% + B2B market | Hire sales, expand geographies/products |
| Margin expansion | EBITDA margin <10% | Renegotiate suppliers, cut redundant overhead |
| Buy-and-build | B2B + <100 employees | Consolidate 2–3 competitors in a fragmented market |
| Pricing power | EBITDA margin >20% + B2B | Move from cost-plus to value-based pricing |
| Customer concentration | (generic — no customer data in SABI) | Reduce reliance on top-3 customers; requires manual diligence |
| Digital transformation | Company age >15y or B2C | Modernize manual/legacy processes |

## Category classification (sourcing strategy)

| Category | Criteria | Strategy |
|---|---|---|
| Low-Hanging Fruit | VERY HIGH + family/founder + simple structure, no hidden group | Direct founder outreach |
| Hidden Gem | HIGH/VERY HIGH + (hidden group or complex structure) | Deep diligence, multi-stakeholder process |
| Medium Prospect | HIGH/MEDIUM + simple structure + founder-led | Follow-up pipeline |
| Exclude/Excluded | Below threshold or failed a hard filter | Screen out |

## Financial metrics computed

| Metric | Formula |
|---|---|
| EBITDA margin | EBITDA / Revenue |
| Cashflow margin | Cashflow / Revenue |
| FCF-to-EBITDA conversion | Cashflow / EBITDA (≥60% = good quality of earnings) |
| EBITDA per employee | EBITDA (€K) / Employees |
| Revenue CAGR (3y) | (Revenue_current / Revenue_2yr-ago)^(1/2) − 1 |
| EBITDA CAGR (3y) | (EBITDA_current / EBITDA_2yr-ago)^(1/2) − 1 |
| Debt-to-EBITDA | Long-term debt / EBITDA |
| Company age | (Today − Founding date) / 365.25 |

## Output workbook

`QUALIFIED_LEADS` (executive summary) · `FINAL_RANKING` · `SCORE_SUMMARY` ·
`VALUE_CREATION_LEVERS` · `OWNERSHIP_BUSINESS_MODEL` · `HARD_FILTERS` · `FINANCIAL_METRICS` ·
`COMPANY_DETAILS` · `HIDDEN_GROUP_ANALYSIS` · `ACTION_LIST` (with blank call-status/notes columns
for a sourcing team).

## Interpretation guide

**For sourcing teams:** start with VERY HIGH-priority Low-Hanging-Fruit companies, then
HIGH-priority Hidden Gems (multi-stakeholder deals); use `VALUE_CREATION_SCORE` to identify
post-acquisition upside; use the hard-filter sheet to explain rejections to stakeholders.

**For due diligence:** verify hard-filter criteria independently; deep-dive companies scoring
≥24; assess value-creation levers in detail (especially revenue growth and margin expansion);
validate business-model classification through customer/vendor interviews.

**For portfolio management:** track actual vs. forecasted value creation per lever; benchmark
portfolio companies against their `QUALITY_SCORE` at acquisition; refine the scoring model based
on realized outcomes.

## Data source

SABI (Sistema de Análisis de Balances Ibéricos) export, Spanish-language column headers
translated to English on load. Numeric and date fields coerced and cleaned; empty/null values
treated as missing, not zero.
