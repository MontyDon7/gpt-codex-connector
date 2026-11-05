# Sales KPIs

Department: `sales` (lead qualification, proposals, deal desk, pricing and discount authority, renewals proposals, pipeline, quota and commission; agent class `SalesAgent`), headed by the Chief Revenue Officer, Rahul Mehta (COMPANY.md §9.2). Budget: £850k / £2,100k / £4,600k (COMPANY.md §5.4). Headcount: 5 / 14 / 26 humans and 3 / 9 / 18 agents (COMPANY.md §6.1). All figures are modelled assumptions, not real data. The FY2026 targets below are the values exposed in `agent.py` as `KPIS` (same ids, units, targets and directions).

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| new_logos_won | New logos won (`sales.deal_won` on a first engagement) | count / year | 24 | 45 | 85 | higher is better | weekly | Chief Revenue Officer |
| win_rate | Proposal win rate | percent | 30.0 | 30.0 | 30.0 | higher is better | monthly | Sales Director (CRO until Q2 FY2027) |
| lead_to_qualified_rate | Lead-to-qualified rate (`sales.lead_qualified` on leads from `marketing.lead_generated`) | percent | 25.0 | 25.0 | 25.0 | higher is better | monthly | Sales Director (CRO until Q2 FY2027) |
| qualified_to_proposal_rate | Qualified-to-proposal rate | percent | 50.0 | 50.0 | 50.0 | higher is better | monthly | Sales Director (CRO until Q2 FY2027) |
| sales_cycle_days | Average sales cycle, qualification to acceptance | days | 75 | 75 | 70 | lower is better | monthly | Chief Revenue Officer |
| blended_cac_gbp | Blended CAC per new logo (sales plus marketing cost / new logos) | GBP | 70,000 | 88,000 | 107,000 | lower is better | quarterly | Chief Revenue Officer |
| new_logo_acv_bookings_gbp | New-logo ACV bookings | GBP / year | 6,000,000 | 13,500,000 | 28,050,000 | higher is better | monthly | Chief Revenue Officer |
| pipeline_coverage_ratio | Pipeline coverage of remaining bookings plan | ratio | 3.3 | 3.3 | 3.3 | higher is better | weekly | Sales Operations Manager (CRO until Q2 FY2027) |
| average_discount_percent | Average discount on proposals sent | percent | 6.0 | 6.0 | 6.0 | lower is better | monthly | Sales Operations Manager (CRO until Q2 FY2027) |
| proposal_turnaround_days | Proposal turnaround, `sales.proposal_requested` to `sales.proposal_sent` | days | 10 | 10 | 8 | lower is better | weekly | Sales Operations Manager (CRO until Q2 FY2027) |
| forecast_accuracy_percent | Forecast accuracy, next-quarter new-logo bookings | percent | 80.0 | 85.0 | 88.0 | higher is better | quarterly | Sales Operations Manager (CRO until Q2 FY2027) |
| renewal_proposal_on_time_percent | Keep renewal proposals issued at least 60 days before term end | percent | 90.0 | 92.0 | 95.0 | higher is better | monthly | Renewals and Expansion Manager (CRO until Q3 FY2027) |
| quota_attainment_percent | Aggregate quota attainment (new-logo bookings / assigned quota) | percent | 90.0 | 90.0 | 90.0 | higher is better | monthly | Sales Director (CRO until Q2 FY2027) |
| cost_per_proposal_gbp | Sales cost per proposal sent | GBP | 10,625 | 14,000 | 16,254 | lower is better | quarterly | Chief Revenue Officer |
| discount_policy_compliance_percent | Proposals issued with the required approvals recorded (COMPANY.md §9.3) | percent | 100.0 | 100.0 | 100.0 | higher is better | monthly | Sales Operations Manager (CRO until Q2 FY2027) |

## 2. Definitions and formulas

Fiscal year is the calendar year; Year 1 = FY2026 (COMPANY.md §1). Counts are for the full fiscal year. A "new logo" is a client with no earlier signed engagement; expansion deals, change orders and renewals are excluded from every new-logo KPI and reported separately. Days are calendar (simulation) days unless stated.

| KPI id | Formula and rules |
|---|---|
| new_logos_won | Count of distinct new clients for which Sales emitted `sales.deal_won`, where the deal source is inbound, outbound, referral or RFP and the client has no earlier signed engagement. Targets equal COMPANY.md §5.1 and §5.3 (24 / 45 / 85). Counted at client acceptance, not at signature; a deal that fails at contract stage is reversed. |
| win_rate | `sales.deal_won` / (`sales.deal_won` + `sales.deal_lost`) x 100 for new-logo proposals decided in the period. Deals lost before a proposal is sent (executive decline, client churn) are excluded from the denominator and reported as `qualified_not_proposed`. Target 30% (COMPANY.md §5.3, §8 item 2). |
| lead_to_qualified_rate | `sales.lead_qualified` count for leads created in the period / `marketing.lead_generated` count for the same cohort x 100. Cohort basis, measured 90 days after creation. Both lead stages (`mql` and `nurture`) are in the denominator, because COMPANY.md §5.3 counts 640 leads of which 25% qualify. Planning assumption: `mql` leads qualify at about 50% and `nurture` leads at about 5%; with 45% of leads at `mql` that gives 0.45 x 50% + 0.55 x 5% = 25.3%. Target 25% (COMPANY.md §5.3). Shared with Marketing, which reports the same ratio. |
| qualified_to_proposal_rate | Proposals sent (`sales.proposal_sent`) / qualified opportunities (`sales.lead_qualified`) for the same cohort x 100. Cohort basis, measured 120 days after qualification. Excludes expansion and change orders when reported against the funnel. Target 50% (COMPANY.md §5.3). |
| sales_cycle_days | Mean of (acceptance day minus `sales.proposal_requested` day) for new-logo deals with `sales.deal_won` in the period. Target 75 / 75 / 70 days (COMPANY.md §5.3). Typical breakdown: scoping and pricing 7 days, proposal issued by day 10, client decision window about 63 days including security review and contract negotiation (`economics.md` section 3.7). |
| blended_cac_gbp | (Sales department total cost + Marketing department total cost) / new logos won, in the same fiscal year. Cost is the department total (people plus non-people) from `economics.md` section 1 and the marketing row in COMPANY.md §5.4. FY2026: (£850k + £830k) / 24 = £70.0k; FY2027: (£2,100k + £1,850k) / 45 = £87.8k; FY2028: (£4,600k + £4,500k) / 85 = £107.1k. Targets are the rounded COMPANY.md §5.3 values (£70k / £88k / £107k). Sales's share is `sales_cost_per_new_logo` of £35.4k / £46.7k / £54.1k. |
| new_logo_acv_bookings_gbp | Sum of net contract value (list price less discount, first-year value for Keep) of new-logo deals at acceptance. Targets are new logos x ACV (COMPANY.md §5.1): 24 x £250k = £6.0m; 45 x £300k = £13.5m; 85 x £330k = £28.05m. Renewals, expansion and change orders are excluded; they are reported as `expansion_and_renewal_bookings_gbp` in the monthly pack. |
| pipeline_coverage_ratio | Open pipeline at list price in stages `scoped` to `contract` (not yet won or lost), expiring in the next two quarters, divided by the new-logo bookings plan still to be won for those two quarters. Target 3.3 = 1 / 30% win rate (COMPANY.md §5.3), so coverage at 3.3x reproduces plan at the planned win rate. Below 3.0 for two consecutive weeks triggers a pipeline plan (SOP-SALES-10). |
| average_discount_percent | Mean of `discount_pct` on proposals sent in the period, weighted by list price x 100. Typical discount is 10% or less (COMPANY.md §3). Target 6.0% leaves headroom below the 10% Sales head authority; a monthly value above 8% triggers a deal desk review. |
| proposal_turnaround_days | Mean calendar days from `sales.proposal_requested` to `sales.proposal_sent`. Target 10 days (7-day scoping window plus 3 days to assemble; the code `due_day` offsets are 7 and 10). Deals waiting on Executive approval are counted in full, not paused. FY2028 target 8 days after the Proposal Writer starts. |
| forecast_accuracy_percent | 1 minus absolute percentage error of the weighted next-quarter new-logo bookings forecast taken at the start of the quarter against actual bookings, x 100. Weighted pipeline uses the stage weights in `economics.md` section 3.5. |
| renewal_proposal_on_time_percent | `sales.renewal_proposal_sent` messages issued at least 60 days before the Keep term end / all renewal proposals issued x 100. Term end is the `due_day` carried by `customer_success.renewal_due`. |
| quota_attainment_percent | New-logo bookings credited to quota carriers / assigned quota x 100, aggregate. Assigned quota is 110% of the bookings plan (6.6m / 14.85m / 30.855m), so 90% attainment equals 99% of plan. |
| cost_per_proposal_gbp | Sales department total cost / proposals sent in the year. FY2026 £850k / 80 = £10,625; FY2027 £2,100k / 150 = £14,000; FY2028 £4,600k / 283 = £16,254. The rise follows the shift to larger deals (Forge Build and Scale, Compass Programme) and US pursuits (`economics.md` section 3.2). |
| discount_policy_compliance_percent | Proposals sent with the approvals required by COMPANY.md §9.3 recorded before issue / all proposals sent x 100. Required approvals: discount above 10% or non-standard payment terms (Finance head and CEO), net value of £500k or more (CEO), net value above £1.5m (Board notified and approving), non-standard legal terms (General Counsel and CEO). Target 100%; any miss is reported to the CEO in the next monthly pack. |

## 3. Reporting cadence and data sources

| Cadence | Forum | Content | Data source |
|---|---|---|---|
| Daily | SDR and account executive stand-up | New leads and age in queue, scoping and pricing gates outstanding, approvals pending | CRM, bus messages (`marketing.lead_generated`, `delivery.scoping_completed`, `finance.pricing_check_completed`) |
| Weekly (Monday) | Pipeline review (CRO, Sales Director, Sales Operations Manager) | `new_logos_won`, `pipeline_coverage_ratio`, `proposal_turnaround_days`, stage ageing, stalled deals | CRM, Pipeline and Forecast Agent weekly review |
| Monthly | Sales performance review with Marketing and Finance | All monthly KPIs, discount log, quota and commission, renewal calendar, lost-deal reasons | CRM, finance month-end close (`finance.month_end_closed`), deal desk log |
| Quarterly | Business review; Board pack input | `blended_cac_gbp`, `cost_per_proposal_gbp`, `forecast_accuracy_percent`, cohort conversion, hiring gates | Data department KPI report (`data.kpi_report_published`), Marketing and Finance |
| Annually | Budget cycle (opens Q4, `finance.budget_cycle_opened`) | Target reset and `sales.budget_submitted`; quota plan | `economics.md`, prior-year actuals, OKRs (`executive.okrs_set`) |

Systems of record: the CRM for leads, deals and stages (one record per `deal_id`); the CPQ and deal desk log for price, discount and approvals; the finance ledger for cost and cash. The Data department owns the attribution and funnel definitions and signs off the quarterly figures; Sales may not restate a prior quarter without Data and Finance agreement. The agent exposes a monthly KPI snapshot (`sales.activity.monthly_kpi_snapshot`) from its own state, which Data reconciles to the CRM.

Data quality controls: every deal carries `lead_id` (or `rfp_id`, `engagement_id` or `client_id` for expansion), `source`, `tier`, `list_price_gbp`, `discount_pct` and the approvals list; deals without a source are excluded from channel reporting and reported separately (below 2% of deals); a deal moved to `won` without a signed contract id is flagged within one business day.

## 4. Links to company targets

| Company target | Source | How sales KPIs roll up |
|---|---|---|
| 24 / 45 / 85 new logos; 80 / 150 / 283 proposals; 160 / 300 / 567 qualified; 640 / 1,200 / 2,267 leads | COMPANY.md §5.1, §5.3 | `new_logos_won`, `win_rate`, `qualified_to_proposal_rate` and `lead_to_qualified_rate` are the stage conversions of the funnel; the product of 25% x 50% x 30% is 3.75% of leads to a new logo (24 / 640). |
| Blended CAC £70k / £88k / £107k (sales + marketing cost / new logos) | COMPANY.md §5.3, §5.4 | `blended_cac_gbp`: sales £850k / £2,100k / £4,600k plus marketing £830k / £1,850k / £4,500k = £1,680k / £3,950k / £9,100k over 24 / 45 / 85 logos. Sales's share is about 51%, 53% and 51%; Marketing's `marketing_cost_per_new_logo` is the other half. |
| Average sales cycle 75 / 75 / 70 days | COMPANY.md §5.3 | `sales_cycle_days`; capacity-driven start lag (14 days when delivery utilisation exceeds 85%) is quoted to the client but does not extend the cycle. |
| Revenue £6.0m / £19.5m / £46.2m; average revenue per client £250k / £300k / £330k | COMPANY.md §5.1 | `new_logo_acv_bookings_gbp` is new logos x ACV (£6.0m / £13.5m / £28.05m); retained-client revenue (£6.0m in FY2027, £18.15m in FY2028) is carried by Customer Success and renewals. |
| Net revenue retention 115% / 118%; Keep ARR £1.5m / £6.5m / £17.0m; Keep attached to every Forge Build or Scale and at least 40% of Compass Programmes | COMPANY.md §5.1, §2 | `renewal_proposal_on_time_percent` protects renewals; expansion deals (SOP-SALES-09) feed NRR; no sales KPI owns NRR, which Customer Success owns. |
| Typical discount 10% or less; approvals per delegation table | COMPANY.md §3, §9.3 | `average_discount_percent` and `discount_policy_compliance_percent`. |
| Gross margin 48% / 58% / 64% | COMPANY.md §5.1 | Discount and margin floors (`economics.md` section 3.5) protect gross margin; each 1 point of average discount is 1% of new-logo bookings. |
| US share of revenue 0% / 15% / 30% | COMPANY.md §1 | US pursuits start Q1 FY2027; leads from US companies are parked before then (SOP-SALES-01) and the New York presence is costed in `economics.md` section 1. |
| Agent governance: no unreviewed client-facing release; human owner per agent | COMPANY.md §9.4 | `discount_policy_compliance_percent` and the human review gate on every proposal. |

## 5. Targets reset rules

- Targets are reset only through the annual budget cycle or an `executive.okrs_set` or `executive.strategy_updated` change; in-year changes need CRO and CFO agreement and are recorded in the quarterly review.
- If `lead_to_qualified_rate` falls below 20% for two consecutive months, the Sales Director and Marketing's Demand Generation Lead jointly review the 60-point qualification threshold and the marketing stage threshold within 10 business days (SOP-SALES-01).
- If `win_rate` is below 25% for a quarter, no additional lead-generation spend is released; proposal quality and pricing review come first (see `economics.md` sensitivities).
- If `pipeline_coverage_ratio` is below 3.0 for two consecutive weeks, the Sales Director presents a pipeline plan (outbound targets, partner introductions, Marketing campaign asks) at the next weekly review.
- If `average_discount_percent` exceeds 8% in a month, every discounted deal in that month is reviewed by the CRO and the Sales Operations Manager.
