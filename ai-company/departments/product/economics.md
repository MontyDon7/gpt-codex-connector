# Product Economics

> All figures are modeled assumptions in line with typical industry ranges, not real data. Facts are taken from COMPANY.md and cited inline. Money is GBP and ex-VAT unless stated. Owner: Anika Rao, Chief Product Officer.

## 1. Budget

Department scope: product management and R&D for the internal AI agent platform, reusable Forge components and Keep tooling; roadmap, stage gates, AI model evaluation and red-teaming, AI risk review triggers, pricing and packaging proposals. Product is an operating-expense department, not cost of revenue (COMPANY.md §5.1).

### 1.1 Budget by line (£k)

| Line | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| **People (loaded, see section 2)** | **220** | **520** | **1,360** |
| Product agents: compute, model usage and licences (0 / 2 / 6 agents at year end) | 0 | 30 | 92 |
| Evaluation and red-team compute: golden-set runs, model bake-offs, model API usage | 18 | 20 | 60 |
| Platform R&D compute: prototypes, fine-tuning experiments, sandbox environments | 4 | 10 | 155 |
| Product tooling: roadmap, feedback, analytics, experimentation, design and test platforms | 12 | 15 | 85 |
| Client and user research: panels, participant incentives, usability testing | 6 | 8 | 45 |
| External red-team and AI assurance (CREST-style testing share, specialist adversarial testing) | 4 | 8 | 80 |
| Training, conferences, standards memberships | 4 | 6 | 28 |
| Contingency (unallocated, CPO-held) | 2 | 3 | 55 |
| **Non-people total** | **50** | **100** | **600** |
| **Total (people + non-people)** | **270** | **620** | **1,960** |

Check: non-people FY2026 0+18+4+12+6+4+4+2 = 50; FY2027 30+20+10+15+8+8+6+3 = 100; FY2028 92+60+155+85+45+80+28+55 = 600.

FY2028 non-people spend rises sharply because platform R&D moves from prototypes to production-grade multi-agent capability for Forge Scale, Keep Enterprise 24x7 cover and the US, the evaluation harness has to cover about 150 agents company-wide (COMPANY.md §6), and external assurance is needed ahead of SOC 2 and EU AI Act-aligned client reviews (COMPANY.md §8).

### 1.2 Ratios

| Ratio | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Revenue (COMPANY.md §5.1), £k | 6,000 | 19,500 | 46,200 |
| Product cost as % of revenue | 4.5% | 3.2% | 4.2% |
| Product cost as % of total company cost (§5.2: 7.5m / 17.8m / 39.0m) | 3.6% | 3.5% | 5.0% |
| Non-people share of department cost | 18.5% | 16.1% | 30.6% |
| Average company humans per average Product human (29 / 74 / 170 over 1.25 / 3.5 / 11.0) | 23.2 | 21.1 | 15.5 |
| Year-end company agents per Product agent (22 / 70 / 150 over 0 / 2 / 6) | n/a | 35 | 25 |

Product cost as a share of revenue stays within 3% to 5% in every year. FY2028 rises because platform R&D and assurance scale ahead of the 230-human, 150-agent company.

## 2. Headcount cost build-up

Loaded cost = base salary x 1.28 (employer NI, pension, benefits, bonus accrual; COMPANY.md §5.2, §8 item 5). Base salaries sit inside COMPANY.md §6.2 bands. Average headcount (FTE) is time-weighted for in-year starts (Q1 = 1.00, Q2 = 0.75, Q3 = 0.50, Q4 = 0.25). US hires would carry +15% on base (§6.2); none are planned in Product.

### 2.1 FY2026 (year-end humans 2; average 1.25 FTE)

| Role | Level key | Band (£) | Base (£k) | Avg FTE | Base cost (£k) | Loaded (£k) |
|---|---|---|---|---|---|---|
| Chief Product Officer | head | 140,000 to 200,000 | 145 | 1.00 | 145.0 | 185.6 |
| Product Manager (starts Q4) | manager | 92,000 to 115,000 | 105 | 0.25 | 26.3 | 33.6 |
| **Total** | | | | **1.25** | **171.3** | **219.2** |

### 2.2 FY2027 (year-end humans 5; average 3.5 FTE)

| Role | Level key | Band (£) | Base (£k) | Avg FTE | Base cost (£k) | Loaded (£k) |
|---|---|---|---|---|---|---|
| Chief Product Officer | head | 140,000 to 200,000 | 152 | 1.00 | 152.0 | 194.6 |
| Product Manager (1st) | manager | 92,000 to 115,000 | 110 | 1.00 | 110.0 | 140.8 |
| AI Evaluation and Red Team Lead (starts Q2) | manager | 92,000 to 115,000 | 100 | 0.75 | 75.0 | 96.0 |
| Senior AI Engineer (starts Q3) | senior_consultant | 72,000 to 90,000 | 85 | 0.50 | 42.5 | 54.4 |
| Product Manager (2nd, starts Q4) | manager | 92,000 to 115,000 | 98 | 0.25 | 24.5 | 31.4 |
| **Total** | | | | **3.50** | **404.0** | **517.2** |

### 2.3 FY2028 (year-end humans 12; average 11.0 FTE)

| Role | Level key | Band (£) | Base (£k) | Avg FTE | Base cost (£k) | Loaded (£k) |
|---|---|---|---|---|---|---|
| Chief Product Officer | head | 140,000 to 200,000 | 165 | 1.00 | 165.0 | 211.2 |
| Director of Agent Platform (starts Q1) | principal | 120,000 to 155,000 | 140 | 1.00 | 140.0 | 179.2 |
| Product Manager (1st) | manager | 92,000 to 115,000 | 114 | 1.00 | 114.0 | 145.9 |
| Product Manager (2nd) | manager | 92,000 to 115,000 | 100 | 1.00 | 100.0 | 128.0 |
| Product Manager (3rd, starts Q2) | manager | 92,000 to 115,000 | 96 | 0.75 | 72.0 | 92.2 |
| AI Evaluation and Red Team Lead | manager | 92,000 to 115,000 | 104 | 1.00 | 104.0 | 133.1 |
| Senior AI Engineer (1st) | senior_consultant | 72,000 to 90,000 | 88 | 1.00 | 88.0 | 112.6 |
| Senior AI Engineer (2nd, starts Q1) | senior_consultant | 72,000 to 90,000 | 85 | 1.00 | 85.0 | 108.8 |
| AI Engineer (1st, starts Q1) | consultant | 55,000 to 70,000 | 66 | 1.00 | 66.0 | 84.5 |
| AI Engineer (2nd, starts Q2) | consultant | 55,000 to 70,000 | 64 | 0.75 | 48.0 | 61.4 |
| Product Analyst (starts Q2) | analyst | 38,000 to 48,000 | 44 | 0.75 | 33.0 | 42.2 |
| Product Designer (starts Q2) | consultant | 55,000 to 70,000 | 62 | 0.75 | 46.5 | 59.5 |
| **Total** | | | | **11.00** | **1,061.5** | **1,358.6** |

Year-end humans FY2026 / FY2027 / FY2028 = 2 / 5 / 12, equal to the product row of COMPANY.md §6.1 and the roles in `blueprint.md` section 3. The people lines are shown in section 1 as £220k, £520k and £1,360k, being the computed £219.2k, £517.2k and £1,358.6k plus rounding to the envelope (CPO-held bonus accrual true-up of £0.8k, £2.8k and £1.4k).

### 2.4 AI agent cost (inside the non-people agent line)

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Agents at year end (COMPANY.md §6.1) | 0 | 2 | 6 |
| Average agents in year (FY2027: Evaluation and Red-Team from Q2, Roadmap and Feedback Synthesis from Q3; FY2028: first two full year, Release and Vulnerability Tracking and AI Risk Review Pack from Q2, second Evaluation and Red-Team and Pricing and Packaging Analysis from Q3) | 0 | 1.25 | 4.5 |
| Fully loaded cost per agent-year, £k (inside the §5.2 range £20k to £35k; falls about 15% a year per §8 item 4; FY2028 equals the Finance planning figure) | n/a | 24.0 | 20.5 |
| Agent cost, £k | 0 | 30 | 92 |

Agents draft, evaluate and propose; they may not release to clients, pass a gate, approve a risk review or change a price (COMPANY.md §9.4).

## 3. Pricing and unit economics

Product does not sell and has no price list of its own. Its economics are (a) the cost of building and assuring capabilities, (b) the delivery cost it removes through reuse, (c) the price-sensitivity of the list prices it proposes changes to, and (d) the economics of an agent-day.

### 3.1 Cost per capability and per evaluation

| Metric | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Product total cost, £k (§5.4) | 270 | 620 | 1,960 |
| Reusable capabilities shipped (KPI `capabilities_shipped`) | 6 | 14 | 28 |
| Total Product cost per capability shipped, £k | 45.0 | 44.3 | 70.0 |
| Release trains (14-day cadence; FY2026 starts after platform set-up) | 20 | 26 | 26 |
| Evaluation reports issued (G3 and G4, plus model bake-offs; assumption) | 30 | 60 | 120 |
| Evaluation and red-team compute per evaluation report, £ (line / reports) | 600 | 333 | 500 |
| External red-team and assurance per live client-facing agent at year end, £ (FY2026: 3 agents; FY2027: 9; FY2028: 25; assumption) | 1,333 | 889 | 3,200 |

Cost per capability rises in FY2028 because the capability set moves from single-agent skills to multi-agent orchestration, Keep Enterprise 24x7 support and US-ready variants, each carrying a heavier assurance burden. Evaluation compute per report falls in FY2027 (unit costs fall about 15% a year, COMPANY.md §8, and golden sets are reused) and rises in FY2028 because golden sets grow from 200 to 500 cases per agent and agent count rises.

### 3.2 Platform reuse savings

Delivery cost of a Forge engagement is proxied by the company cost-of-revenue share (1 minus gross margin, COMPANY.md §5.1: 52% / 42% / 36%) applied to Forge revenue (COMPANY.md §5.1: £2.40m / £7.80m / £18.48m). A reusable component is assumed to cut 10% of delivery cost on an engagement that uses it (assumption, section 4).

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Forge revenue, £k | 2,400 | 7,800 | 18,480 |
| Forge delivery cost proxy, £k | 1,248 | 3,276 | 6,653 |
| Share of engagements using platform components (KPI `platform_reuse_pct`) | 40% | 60% | 75% |
| Delivery cost saved at 10% on reusing engagements, £k | 49.9 | 196.6 | 499.0 |
| Saving as % of Product total cost | 18.5% | 31.7% | 25.5% |

Direct, measurable delivery savings recover roughly a fifth to a third of Product's cost. The remainder is justified by what is not counted here: faster Forge delivery, differentiation in sales, higher Keep retention (net revenue retention 115% and 118%, COMPANY.md §5.1), and risk avoided by the gate and red-team process. Finance reviews the reuse assumption each quarter and the Chief Product Officer must present the evidence for any year in which savings fall below 15% of Product cost.

### 3.3 Price sensitivity for pricing and packaging proposals

Product proposes; Finance models; Executive approves (SOP-PRODUCT-09, COMPANY.md §9.3). The table shows the revenue effect of a 1% list-price change at modeled mix (COMPANY.md §5.1), assuming no volume response.

| Revenue by line, £k | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Compass | 2,700 | 6,825 | 12,936 |
| Forge | 2,400 | 7,800 | 18,480 |
| Keep | 900 | 4,875 | 14,784 |
| Revenue of 1% price change, Compass, £k | 27.0 | 68.3 | 129.4 |
| Revenue of 1% price change, Forge, £k | 24.0 | 78.0 | 184.8 |
| Revenue of 1% price change, Keep, £k | 9.0 | 48.8 | 147.8 |
| **Revenue of 1% price change, all lines, £k** | **60.0** | **195.0** | **462.0** |

Keep annual uplift is CPI + 2% capped at 7% (COMPANY.md §7). With CPI at 3% (assumption) the uplift is 5% on opening Keep ARR (year-end ARR of the prior year, COMPANY.md §5.1): FY2027 £1.5m x 5% = £75k; FY2028 £6.5m x 5% = £325k. At the 7% cap the amounts are £105k and £455k. Any list-price proposal must show its interaction with this uplift and cannot apply retrospectively to signed contracts.

Packaging guardrail used by the Pricing and Packaging Analysis Agent and the Product Manager: a proposed tier or package must model a gross margin at or above the company gross margin target for the year (48% / 58% / 64%, COMPANY.md §5.1), using the agent-day rate of £350 and the human rate card (COMPANY.md §3.5) for any added days.

### 3.4 AI agent-day economics

The rate card prices an AI agent-day at £350 (COMPANY.md §3.5). Annual loaded agent cost is £25.0k (FY2026 company-wide planning figure from Finance), £24.0k (FY2027) and £20.5k (FY2028).

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Agent cost per year, £k | 25.0 | 24.0 | 20.5 |
| Break-even billed agent-days per agent-year (cost / £350) | 71 | 69 | 59 |
| Revenue if billed 50% of 220 working days (110 days), £k | 38.5 | 38.5 | 38.5 |
| Gross margin on a 50%-billed agent | 35% | 38% | 47% |

A rate-card review is triggered if the break-even exceeds 90 days or the gross margin on a 50%-billed agent falls below 30%; the next-year effect of the 15% annual fall in compute cost (COMPANY.md §8) is the main lever, and any change goes through SOP-PRODUCT-09.

## 4. Assumptions

1. Loaded cost = base x 1.28; average FTE is weighted by start quarter (Q1 1.00, Q2 0.75, Q3 0.50, Q4 0.25). Base salaries step up each January; the Chief Product Officer's and first Product Manager's bases are shown by year.
2. Time-to-hire 45 days for humans and 5 days for agent provisioning (COMPANY.md §8). Requisitions open a quarter before the start quarter.
3. Agent cost per agent-year £24.0k in FY2027 and £20.5k in FY2028 (inside the £20k to £35k range, COMPANY.md §5.2, falling about 15% a year per §8 item 4). No Product agents in FY2026 (COMPANY.md §6.1).
4. Reuse saving of 10% of delivery cost per reusing Forge engagement, and the company cost-of-revenue share as a proxy for Forge delivery cost, are modeled assumptions to be validated by Delivery and Finance after the first six months of FY2026.
5. Evaluation reports per year (30 / 60 / 120), live client-facing agents at year end (3 / 9 / 25) and release trains (20 / 26 / 26) are planning assumptions derived from the 24 / 65 / 140 active clients (COMPANY.md §5.1) and the 14-day cadence in SOP-PRODUCT-03.
6. CPI for the Keep uplift illustration is 3%.
7. Non-people lines exclude Delivery's client-specific compute and subcontractors, which sit in the delivery budget (COMPANY.md §5.4).
8. No Product spend above £50k is made outside the budget without CFO approval, and above £250k without the CEO (COMPANY.md §9.3).

## 5. Reconciliation to COMPANY.md

COMPANY.md §5.4 row for `product`: people £220k / £520k / £1,360k; non-people £50k / £100k / £600k; total £270k / £620k / £1,960k.

| £k | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| People per this document (section 1) | 220 | 520 | 1,360 |
| People computed from build-up (section 2) | 219.2 | 517.2 | 1,358.6 |
| Difference between computed and envelope people cost | -0.8 | -2.8 | -1.4 |
| Non-people per this document | 50 | 100 | 600 |
| **Total per this document** | **270** | **620** | **1,960** |
| COMPANY.md §5.4 total | 270 | 620 | 1,960 |
| Delta | 0 | 0 | 0 |

The computed people cost is within £5k of the envelope in every year (largest delta £2.8k), and the budget total matches §5.4 exactly. Headcount equals COMPANY.md §6.1 (2 / 5 / 12 humans; 0 / 2 / 6 agents).
