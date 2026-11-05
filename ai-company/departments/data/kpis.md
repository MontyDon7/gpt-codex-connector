# Data and Analytics KPIs

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| kpi_report_on_time_rate | Firm KPI report on-time rate | percent | 95 | 97 | 98 | Higher is better | Monthly | Chief Data and AI Officer |
| data_quality_pass_rate | Data quality check pass rate | percent | 95 | 97 | 98.5 | Higher is better | Weekly | Senior Data Engineer (Chief Data and AI Officer in FY2026) |
| forecast_mape_bookings | Bookings forecast error (MAPE, 90-day) | percent | 15 | 10 | 8 | Lower is better | Monthly | Senior Forecasting Scientist (Chief Data and AI Officer until hired) |
| certified_metric_coverage | Certified metric coverage | percent | 80 | 90 | 95 | Higher is better | Monthly | Chief Data and AI Officer |
| certified_dashboard_share | Dashboards using only certified metrics | percent | 70 | 85 | 95 | Higher is better | Monthly | BI and Analytics Analyst (Chief Data and AI Officer in FY2026) |
| dq_issue_mttr_days | Data quality issue mean time to resolve | days | 5 | 3 | 2 | Lower is better | Weekly | Data Engineering Manager (Chief Data and AI Officer until hired) |
| access_review_completion | Quarterly access review completion | percent | 100 | 100 | 100 | Higher is better | Quarterly | Data Governance Lead (Chief Data and AI Officer until hired) |
| agent_eval_coverage | Registered agents evaluated in the last 30 days | percent | 80 | 95 | 100 | Higher is better | Monthly | Principal Data Architect (Chief Data and AI Officer until hired) |
| client_data_segregation_breaches | Client-data segregation breaches | count | 0 | 0 | 0 | Lower is better | Continuous, reported monthly | Chief Data and AI Officer |
| retention_schedule_compliance | Datasets within retention schedule | percent | 95 | 98 | 100 | Higher is better | Quarterly | Data Governance Lead (Chief Data and AI Officer until hired) |
| platform_cost_per_active_client_gbp | Data platform non-people cost per active client | GBP | 2,100 | 1,700 | 2,900 | Lower is better | Quarterly | Chief Data and AI Officer |

FY2028 platform cost per client rises because the department adds forecasting and agent-evaluation compute and governance tooling for 150 agents (see `economics.md` §3); it is a spending cap, not an efficiency claim.

## 2. Definitions and formulas

All metrics below are registered in the metric registry with an id, a formula, a source and an owner. A metric becomes **certified** once its formula has been peer-reviewed, tested against a hand calculation and signed off by the owner.

### Firm metrics computed from the event stream (single source of truth)

These are the numbers the Data agent computes from department events. Money is GBP, ex-VAT (COMPANY.md §3).

| Metric id | Formula | Source topic(s) |
|---|---|---|
| leads_generated | count of `marketing.lead_generated` (distinct `lead_id`) | marketing |
| leads_qualified | count of `sales.lead_qualified` (distinct `lead_id`) | sales |
| lead_to_qualified_rate | leads_qualified / leads_generated (target 25%, COMPANY.md §5.3) | derived |
| open_pipeline_gbp | sum of `amount_gbp` for proposals sent and not yet won or lost | `sales.proposal_sent` minus `sales.deal_won` and `sales.deal_lost` |
| proposals_sent | count of distinct `deal_id` in `sales.proposal_sent` | sales |
| win_rate | deals_won / (deals_won + deals_lost) (target 30%, COMPANY.md §5.3) | `sales.deal_won`, `sales.deal_lost` |
| bookings_gbp | sum of `amount_gbp` on `sales.deal_won` | sales |
| active_engagements | kickoffs minus completions | `delivery.engagement_kickoff`, `delivery.engagement_completed` |
| invoiced_gbp | sum of `amount_gbp` on `finance.invoice_issued` | finance |
| collected_gbp | sum of `amount_gbp` on `finance.payment_received` | finance |
| outstanding_receivables_gbp | invoiced_gbp minus collected_gbp | derived |
| dso_days | mean of (payment day minus invoice day) for matched invoices (target at or below 45, COMPANY.md §7) | finance |
| keep_arr_gbp | annual value of Keep deals won and renewals confirmed, minus churned annual value (COMPANY.md §5.1 targets £1.5m at FY2026 year end) | sales, customer_success |
| active_clients | distinct `client_id` on won deals minus churned | sales, customer_success |
| client_health_avg | mean of latest `score` per client from `customer_success.health_score_updated` | customer_success |
| churned_clients | count of `customer_success.client_churned` | customer_success |

Revenue in the sense of COMPANY.md §5.1 is recognised revenue (percentage-of-completion for fixed fee, straight-line for Keep, COMPANY.md §7) and is owned by Finance. The Data agent reports `invoiced_gbp` as the billing proxy and takes recognised revenue from `finance.month_end_closed` when it is supplied; it never overwrites Finance's figure.

### Department KPIs

| KPI id | Formula |
|---|---|
| kpi_report_on_time_rate | reports published by working day 3 of the month / reports due, rolling 12 months |
| data_quality_pass_rate | checks passed / checks run across all monitored feeds, weekly |
| forecast_mape_bookings | mean over forecasts of abs(actual bookings in window minus forecast) / actual, window = 90 days; at least 4 forecasts before the KPI is scored |
| certified_metric_coverage | certified metrics in use / metrics in use in executive reporting |
| certified_dashboard_share | dashboards with 100% certified metrics / live dashboards |
| dq_issue_mttr_days | mean (resolved day minus raised day) of issues closed in period |
| access_review_completion | access reviews completed by due date / reviews due |
| agent_eval_coverage | registered agents with an evaluation run in the last 30 days / registered agents |
| client_data_segregation_breaches | confirmed events where data of client A was exposed to a scope of client B; any occurrence triggers the security incident chain |
| retention_schedule_compliance | datasets whose oldest record is inside the retention period / datasets in scope |
| platform_cost_per_active_client_gbp | non-people department spend / active clients (COMPANY.md §5.1: 24, 65, 140) |

## 3. Reporting cadence and data sources

| Cadence | Report | Audience | Source |
|---|---|---|---|
| Daily (automatic) | Data quality digest, freshness status | Data team | Pipeline logs and check results |
| Weekly | Quality pass rate and open issue ageing | Data team, Operations | Data Quality Monitor Agent |
| Monthly, by working day 3 | Firm KPI report (`data.kpi_report_published`) | Executive, Finance | Event stream, certified marts |
| Monthly | Bookings and revenue forecast (`data.forecast_updated`) | Sales, Finance, Delivery, Executive | Forecasting Agent |
| Quarterly | Agent quality report (`data.agent_quality_report_published`) | Product, Delivery, Executive | Agent Quality Evaluation Agent |
| Quarterly | Access review, retention review, benchmark refresh | Executive, IT Security, Legal | Governance and Lineage Agent |
| Per board meeting | Board KPI pack | Board via CEO | Certified marts, signed off by the Chief Data and AI Officer |

Source systems are the event stream from each department (CONVENTIONS.md §7), the ledger via Finance, the client relationship record via Sales and Customer Success, the HR system via People, and external market feeds (`external.market_data_published`). Where two sources disagree the order of precedence is: Finance ledger for money, Sales CRM for deal stage, People HR system for headcount, Customer Success platform for health.

## 4. Links to company targets

| Company target | KPI link |
|---|---|
| Win rate 30%, lead-to-qualified 25%, sales cycle about 75 days (COMPANY.md §5.3, §8.2) | win_rate, lead_to_qualified_rate and open_pipeline_gbp are computed here and reported monthly |
| Revenue £6.0m, £19.5m, £46.2m and active clients 24, 65, 140 (COMPANY.md §5.1) | invoiced_gbp, active_clients, bookings_gbp reconciled to Finance month-end close (`finance.month_end_closed`) |
| Keep ARR £1.5m, £6.5m, £17.0m (COMPANY.md §5.1) | keep_arr_gbp |
| Net revenue retention 115% and 118%, logo retention 83% and 85% (COMPANY.md §5.1) | churned_clients, active_clients and renewals feed the retention calculation |
| DSO at or below 45 days (COMPANY.md §7) | dso_days |
| ISO 27001, SOC 2 Type II, UK GDPR (COMPANY.md §8.7) | access_review_completion, retention_schedule_compliance, client_data_segregation_breaches provide evidence |
| AI agent governance and register (COMPANY.md §9.4) | agent_eval_coverage |
| Department budget £140k, £360k, £1,410k (COMPANY.md §5.4) | platform_cost_per_active_client_gbp |
| Leverage 0.5 to 0.65 agents per delivery human (COMPANY.md §2) | agent_eval_coverage keeps that leverage measurable and safe |
