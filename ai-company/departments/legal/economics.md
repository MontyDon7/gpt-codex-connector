# Legal Economics

> All figures are modeled assumptions in line with typical industry ranges, not real data. Facts are taken from COMPANY.md and cited inline. Money is GBP and ex-VAT unless stated. Owner: Callum Fraser, General Counsel.

## 1. Budget

Department scope: commercial contracts, data protection and breach response, regulatory change, AI-risk review, disputes, vendor and people legal support, IP and brand, corporate governance (UK entity; US entity from Q1 FY2027). Legal is an operating-expense department, not cost of revenue (COMPANY.md §5.1).

### 1.1 Budget by line (£k)

| Line | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| **People (loaded, see section 2; COMPANY.md §5.4 envelope)** | **210** | **330** | **600** |
| Outside counsel: specialist, litigation, employment, US counsel, breach panel | 45 | 105 | 340 |
| Contract lifecycle management (CLM) and e-signature | 12 | 25 | 60 |
| Legal research and regulatory horizon subscriptions | 5 | 10 | 22 |
| IP filings: trade marks (UK, then US/EU) and registrations | 8 | 14 | 30 |
| Regulatory fees: ICO data protection fee, Companies House, registrations | 3 | 6 | 18 |
| Legal agents: compute, model usage and licences (1 / 3 / 5 agents at year end) | 20 | 40 | 72 |
| Training and CPD: SRA practising certificates, CPD, compliance course content | 7 | 10 | 18 |
| US/EU programme: Delaware entity and state filings, US templates, EU AI Act and EU representative | 0 | 40 | 140 |
| **Non-people total** | **100** | **250** | **700** |
| **Total (people + non-people)** | **310** | **580** | **1,300** |

Check: non-people FY2026 45+12+5+8+3+20+7+0 = 100; FY2027 105+25+10+14+6+40+10+40 = 250; FY2028 340+60+22+30+18+72+18+140 = 700. Totals 210+100 = 310; 330+250 = 580; 600+700 = 1,300. The line values are identical to `NON_PEOPLE_LINES_GBP` in `agent.py`, which the agent returns in `legal.budget_submitted`.

Insurance premiums (professional indemnity, cyber, D&O) are held in Finance and Operations "insurance and professional fees" (COMPANY.md §5.2), not in the Legal budget; Legal prepares the renewal pack each July.

### 1.2 Ratios

| Ratio | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Revenue (COMPANY.md §5.1), £k | 6,000 | 19,500 | 46,200 |
| Legal cost as % of revenue | 5.2% | 3.0% | 2.8% |
| Legal cost as % of total company cost (§5.2: 7.5m / 17.8m / 39.0m) | 4.1% | 3.3% | 3.3% |
| Legal cost per active client (24 / 65 / 140, §5.1), £k | 12.9 | 8.9 | 9.3 |
| Non-people share of department cost | 32% | 43% | 54% |
| Outside counsel as % of non-people | 45% | 42% | 49% |

Non-people spend grows fastest in FY2028 because of the US/EU programme and outside counsel for a larger contract base, while in-house lawyers take the standard work.

## 2. Headcount cost build-up

Loaded cost = base x 1.28 (COMPANY.md §5.2). Average FTE follows start quarter: Q1 = 1.00, Q2 = 0.75, Q3 = 0.50, Q4 = 0.25. Bases are inside the COMPANY.md §6.2 bands and match `blueprint.md` section 3.

| Role (level key) | Planning base £ | Loaded £ | Start | FY2026 avg FTE | FY2027 avg FTE | FY2028 avg FTE | FY2026 £k | FY2027 £k | FY2028 £k |
|---|---|---|---|---|---|---|---|---|---|
| General Counsel (head) | 164,000 | 209,920 | Q1 FY2026 | 1.00 | 1.00 | 1.00 | 209.9 | 209.9 | 209.9 |
| Commercial and Privacy Counsel (manager) | 92,000; 96,600 from 2028-01 | 117,760; 123,648 | Q2 FY2027 | 0 | 0.75 | 1.00 | 0 | 88.3 | 123.6 |
| Contracts Specialist (consultant) | 55,000; 57,750 from 2028-01 | 70,400; 73,920 | Q3 FY2027 | 0 | 0.50 | 1.00 | 0 | 35.2 | 73.9 |
| Privacy and Regulatory Counsel (manager) | 115,000 | 147,200 | Q1 FY2028 | 0 | 0 | 1.00 | 0 | 0 | 147.2 |
| Legal Operations Analyst (analyst) | 44,000 | 56,320 | Q2 FY2028 | 0 | 0 | 0.75 | 0 | 0 | 42.2 |
| **Total** | | | | **1.00** | **2.25** | **4.75** | **209.9** | **333.4** | **596.9** |
| COMPANY.md §5.4 people envelope | | | | | | | 210 | 330 | 600 |
| Delta (build-up minus envelope) | | | | | | | -0.1 | +3.4 | -3.1 |

Derivations: FY2027 = 209.92 + 117.76 x 0.75 (88.32) + 70.40 x 0.50 (35.20) = 333.44. FY2028 = 209.92 + 123.648 + 73.92 + 147.20 + 56.32 x 0.75 (42.24) = 596.93. Year-end humans 1 / 3 / 5 match COMPANY.md §6.1.

## 3. Pricing and unit economics

Legal is an internal service with no external price list. The figures below show what each unit of work costs and the make-or-buy case against outside counsel.

### 3.1 Workload drivers (derived)

| Driver | Derivation | FY2026 | FY2027 | FY2028 |
|---|---|---|---|---|
| Active clients (COMPANY.md §5.1) | given | 24 | 65 | 140 |
| Contract documents (MSA/SOW, Keep order forms, renewals, change orders) | active clients x 2.5 (assumption: 1.5 order documents and 0.5 change orders per client, plus 0.5 amendments/NDAs/renewals) | 60 | 163 | 350 |
| Vendor, contractor and employment documents | humans average (29 / 74 / 170, COMPANY.md §6) x 0.6 hires and leavers per head, plus vendors | 30 | 80 | 170 |
| Estimated DSARs, security questionnaires and AI risk reviews | assumption: 4 / 10 / 24 a quarter combined | 16 | 40 | 96 |

### 3.2 Cost per contract document

Contracting cost pool = 50% of people cost + 80% of CLM and e-signature + 40% of agent cost (the rest of those lines serve compliance and privacy work).

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| People share £k (50% of 210 / 330 / 600) | 105.0 | 165.0 | 300.0 |
| CLM share £k (80% of 12 / 25 / 60) | 9.6 | 20.0 | 48.0 |
| Agent share £k (40% of 20 / 40 / 72) | 8.0 | 16.0 | 28.8 |
| Contracting cost pool £k | 122.6 | 201.0 | 376.8 |
| Contract documents | 60 | 163 | 350 |
| **Internal cost per contract document, £** | **2,043** | **1,233** | **1,077** |

### 3.3 Make-or-buy against outside counsel

| Measure | Value | Derivation |
|---|---|---|
| Outside counsel blended rate | £450 per hour | Assumption: London mid-tier firm, partner/associate blend |
| Outside counsel hours bought | 100 / 233 / 756 | Budget line £45k / £105k / £340k divided by £450 |
| General Counsel internal cost per productive hour | £127 | £209,920 / 1,650 productive hours (assumption) |
| Commercial and Privacy Counsel internal cost per productive hour | £71 | £117,760 / 1,650 |
| Standard contract: outside counsel cost | £2,250 | 5 hours at £450 (assumption) |
| Standard contract: internal cost with playbook, agent first pass and sample check | £1,233 in FY2027 | section 3.2 |
| Saving per standard contract in FY2027 | £1,017 | 2,250 - 1,233 |
| Estimated standard-contract volume in FY2027 | about 120 | 163 documents, of which about 75% are standard paper |
| Estimated avoided outside-counsel spend in FY2027 | about £122k | 120 x £1,017 |

Outside counsel is reserved for: litigation and pre-action disputes, ICO breach response (panel firm on 24-hour call-out), employment tribunal risk, US state law, and complex IP. Non-budgeted spend above £50k needs the CFO and above £250k the CEO (COMPANY.md §9.3).

### 3.4 Exposure avoided and controls

| Item | Basis | Value |
|---|---|---|
| Liability cap standard | 100% of annual fees paid or payable in the prior 12 months (SOP-LEGAL-02) | Forge Build exposure capped at £260,000 rather than uncapped |
| Late payment interest | Base rate assumption 4.0% + 8% (COMPANY.md §7) = 12.0% a year | £90,000 invoice 60 days overdue: £90,000 x 12% x 60/365 = £1,775 plus £100 fixed compensation |
| Keep uplift | CPI + 2%, cap 7% (COMPANY.md §7) | Keep Plus £216,000 x (3.5% + 2.0%) = £227,880 |
| ICO maximum penalty (awareness only) | UK GDPR higher maximum £17.5m or 4% of worldwide turnover, whichever is higher | Reason for the 72-hour control (SOP-LEGAL-05) |

## 4. Assumptions

1. People cost = base x 1.28 (COMPANY.md §5.2), weighted by start quarter; planning bases inside COMPANY.md §6.2 bands. Pay review of 5% applies to Commercial and Privacy Counsel and the Contracts Specialist from 2028-01-01 only.
2. General Counsel planning base £164,000 is inside the head band £140,000 to £200,000 and gives £209.9k loaded, matching the FY2026 envelope of £210k.
3. Agent cost per agent-year is below the company-wide £20k to £35k range (COMPANY.md §5.2) in FY2027 (£40k / 2.5 average agents = £16.0k) and FY2028 (£72k / 5.0 = £14.4k) because legal agents are document-centric, low-volume and share one platform licence. The budget line, not the per-agent cost, is the binding figure.
4. Bank of England base rate assumed 4.0% for the late-payment interest calculation (`BASE_RATE_PCT`); planning CPI 3.0% when a renewal does not supply CPI (`PLANNING_CPI_PCT`).
5. Outside counsel £450 per hour blended; 1,650 productive hours per lawyer-year; 5 hours of outside counsel per standard contract.
6. Contract document volume 2.5 per active client per year; 75% standard paper in FY2027.
7. Insurance, tax advice and payroll advisers are paid from Finance/People/Operations budgets, not Legal.
8. FX: US/EU programme spend is quoted in USD at the fixed planning rate £1 = $1.27 (COMPANY.md §1).
9. No major litigation is budgeted; a litigated dispute is treated as a non-budgeted spend decision for the CFO and CEO.

## 5. Reconciliation to COMPANY.md

COMPANY.md §5.4 row for legal: people £210k / £330k / £600k, non-people £100k / £250k / £700k, total £310k / £580k / £1,300k.

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| People per envelope (£k) | 210 | 330 | 600 |
| People per build-up (£k, section 2) | 209.9 | 333.4 | 596.9 |
| Delta (£k) | -0.1 | +3.4 | -3.1 |
| Non-people per envelope (£k) | 100 | 250 | 700 |
| Non-people per lines (£k, section 1.1) | 100 | 250 | 700 |
| Delta (£k) | 0 | 0 | 0 |
| **Total per envelope (£k)** | **310** | **580** | **1,300** |
| **Total per this document (£k, envelope people + lines)** | **310** | **580** | **1,300** |

The build-up differs from the people envelope by less than £5k in every year, so the department matches COMPANY.md §5.4. Headcount of 1 / 3 / 5 humans and 1 / 3 / 5 agents matches COMPANY.md §6.1.
