# Data and Analytics Economics

All figures are fictional modelled assumptions in GBP. Loaded cost per human = base salary x 1.28 (COMPANY.md §5.2, §8.5). Averages use average headcount in the year (COMPANY.md §5.4).

## 1. Budget

| Line (£k) | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| People (humans, loaded) | 90 | 250 | 1,000 |
| Non-people: AI agent compute and licences | 15 | 58 | 165 |
| Non-people: warehouse, storage and pipeline compute | 12 | 20 | 100 |
| Non-people: BI and semantic-layer licences | 8 | 12 | 40 |
| Non-people: observability, data quality, catalogue and lineage tooling | 5 | 8 | 60 |
| Non-people: external market data and benchmark feeds | 6 | 8 | 30 |
| Non-people: training, certifications and conferences | 4 | 4 | 8 |
| Non-people: privacy tooling (DPIA, retention automation), audit support | 0 | 0 | 7 |
| **Non-people total** | 50 | 110 | 410 |
| **Department total** | 140 | 360 | 1,410 |

Non-people lines sum: FY2026 15+12+8+5+6+4+0 = 50; FY2027 58+20+12+8+8+4+0 = 110; FY2028 165+100+40+60+30+8+7 = 410. In the FY2028 column the observability line includes £20k observability and £40k governance, catalogue and lineage tooling (£60k).

## 2. Headcount cost build-up

Base salaries are inside the COMPANY.md §6.2 bands. Fraction is the share of the year in post (start dates from `blueprint.md` §5). Loaded cost = base x 1.28.

### FY2026 (average humans 0.50)

| Role | Base (£) | Loaded (£) | Fraction of year | Cost (£k) |
|---|---|---|---|---|
| Chief Data and AI Officer (starts 2026-07-01) | 140,000 | 179,200 | 0.50 | 89.6 |
| **Total** | | | **0.50 FTE** | **89.6 (budget 90)** |

### FY2027 (average humans 1.75)

| Role | Base (£) | Loaded (£) | Fraction of year | Cost (£k) |
|---|---|---|---|---|
| Chief Data and AI Officer | 140,000 | 179,200 | 1.00 | 179.2 |
| Senior Data Engineer (starts Q3) | 82,000 | 104,960 | 0.50 | 52.5 |
| BI and Analytics Analyst (starts Q4) | 62,000 | 79,360 | 0.25 | 19.8 |
| **Total** | | | **1.75 FTE** | **251.5 (budget 250)** |

### FY2028 (average humans 7.58)

| Role | Base (£) | Loaded (£) | Fraction of year | Cost (£k) |
|---|---|---|---|---|
| Chief Data and AI Officer | 150,000 | 192,000 | 1.00 | 192.0 |
| Principal Data Architect (Q1, 2028-01-03) | 145,000 | 185,600 | 1.00 | 185.6 |
| Senior Data Engineer (existing) | 82,000 | 104,960 | 1.00 | 105.0 |
| BI and Analytics Analyst (existing) | 62,000 | 79,360 | 1.00 | 79.4 |
| Data Engineering Manager (Q1, from 2028-02-01) | 112,000 | 143,360 | 0.92 | 131.4 |
| Senior Forecasting Scientist (Q1, from 2028-02-01) | 90,000 | 115,200 | 0.92 | 105.6 |
| Data Governance Lead (Q2, from 2028-04-01) | 108,000 | 138,240 | 0.75 | 103.7 |
| Senior Data Engineer, second (Q2, from 2028-04-01) | 82,000 | 104,960 | 0.75 | 78.7 |
| BI and Analytics Analyst, second (Q4, from 2028-10-01) | 62,000 | 79,360 | 0.25 | 19.8 |
| **Total** | | | **7.58 FTE** | **1,001.2 (budget 1,000)** |

Year-end humans 1, 3 and 9 equal COMPANY.md §6.1. Cost of one head per level (loaded, full year): manager £138k to £143k, senior consultant £105k to £115k, consultant £79k, principal £186k.

## 3. Pricing and unit economics

The data department is an internal service: it has no price list and sells nothing to clients. Its economics are cost per unit of service and its share of company cost. Derivations use COMPANY.md §5.1 (revenue, clients) and §5.2 (average humans).

| Unit metric | FY2026 | FY2027 | FY2028 | Derivation |
|---|---|---|---|---|
| Department cost as % of revenue | 2.3% | 1.8% | 3.1% | 140/6,000; 360/19,500; 1,410/46,200 |
| Department cost per active client (£) | 5,833 | 5,538 | 10,071 | 140k/24; 360k/65; 1,410k/140 |
| Non-people cost per active client (£) | 2,083 | 1,692 | 2,929 | 50k/24; 110k/65; 410k/140 (KPI targets round to 2,100 / 1,700 / 2,900) |
| Department cost per average company human (£) | 4,828 | 4,865 | 8,294 | 140k/29; 360k/74; 1,410k/170 |
| Average AI agents in service (data) | 0.75 | 2.9 | 6.6 | Provisioning dates in `blueprint.md` §5; FY2026 is 0.75 because the Metrics and KPI Reporting Agent runs at full cost only from Q2 (Series A close), with Q1 a pilot on Finance's warehouse allowance |
| Fully loaded cost per data agent-year (£) | 20,000 | 20,000 | 25,000 | Agent compute line / average agents; inside the £20k to £35k range of COMPANY.md §5.2; unit costs fall about 15% a year (COMPANY.md §8.4) but scope grows |
| Cost per monthly KPI report (£) | 1,167 | 3,000 | 11,750 | Assume 10% of department cost is spent on the monthly report: 0.1 x 140k / 12; 0.1 x 360k / 12; 0.1 x 1,410k / 12 (report scope grows with certified metrics and clients) |
| Equivalent external cost of an agent-day (£) | 350 | 350 | 350 | AI agent-day rate, COMPANY.md §3.5 (for internal charge-back comparison only) |

Leverage: in FY2028 the six agents deployed beyond the metrics agent carry routine monitoring, forecasting runs, evaluation and lineage work that would otherwise need roughly 3 to 4 additional analysts (about £250k to £320k loaded); the agents cost about £165k in compute.

Platform cost drivers: warehouse compute scales with event volume (about 1.5 events per client per day per source system, 12 source systems in FY2028); BI licences scale with viewers (target 80% of humans weekly active); governance tooling scales with the number of registered agents and metrics.

Chargeback: none. Delivery engagements that need client-specific analytics are staffed by Delivery at rate-card (COMPANY.md §3.5), not by Data, to keep cost of revenue clean (COMPANY.md §5.1).

## 4. Assumptions

1. The Chief Data and AI Officer starts 2026-07-01; before that the Metrics and KPI Reporting Agent, Finance and Operations cover reporting (Finance holds the ledger; the agent runs on the event stream).
2. Salary bases are mid-band choices within COMPANY.md §6.2. No US hires before FY2028 H2; US +15% premium would add about £15k loaded to any single hire at £82,000 base and is not in the budget.
3. Employer on-costs 28% of base (COMPANY.md §8.5); attrition is not modelled separately (backfills assumed at the same base and lead time, COMPANY.md §8.3).
4. Agent cost per agent-year £20k in FY2026 and FY2027 and £25k in FY2028 (higher model usage and evaluation workloads), inside COMPANY.md §5.2.
5. The cost of the department's agents is carried in the non-people envelope (COMPANY.md §5.4 "Non-people spend includes AI compute and tooling").
6. Warehouse and BI vendors are priced on consumption with annual commit; vendor approval follows `operations.vendor_review_requested` and IT Security vendor risk assessment.
7. Unbudgeted spend above £50k needs CFO approval and above £250k CEO approval (COMPANY.md §9.3).
8. Revenue, clients and average humans are taken from COMPANY.md §5.1 and §5.2 without change.

## 5. Reconciliation to COMPANY.md

COMPANY.md §5.4 row for `data` (£k): People 90 / 250 / 1,000; Non-people 50 / 110 / 410; Total 140 / 360 / 1,410.

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| People, computed (§2 above) | 89.6 | 251.5 | 1,001.2 |
| People, budget | 90 | 250 | 1,000 |
| Non-people (§1 above) | 50 | 110 | 410 |
| Total, computed | 139.6 | 361.5 | 1,411.2 |
| Total, §5.4 envelope | 140 | 360 | 1,410 |
| Delta (£k) | -0.4 | +1.5 | +1.2 |

All deltas are within the £5k tolerance. Headcount ties to COMPANY.md §6.1: 1 / 3 / 9 humans and 1 / 3 / 7 agents. Cost of revenue is unaffected: `data` is an operating-expense department (COMPANY.md §5.1).
