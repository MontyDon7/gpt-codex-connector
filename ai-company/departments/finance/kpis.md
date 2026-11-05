# Finance KPIs

Department: `finance` (FP&A, accounting, billing, collections, treasury, budgeting, pricing checks). Head: Chief Financial Officer, Hannah Whitcombe (COMPANY.md §9.2). Agent class: `FinanceAgent`. All figures are modeled assumptions in GBP unless stated.

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| dso_days | Days sales outstanding | days | 45 | 42 | 40 | lower is better | monthly | Billing and Collections Specialist (CFO until Q4 FY2026, then Finance Manager until hired in Q2 FY2027) |
| invoice_timeliness_pct | Invoices issued within 2 business days of milestone acceptance | percent | 95 | 97 | 98 | higher is better | weekly | Billing and Collections Specialist (Finance Manager until hired) |
| bad_debt_pct_revenue | Bad debt written off as share of revenue | percent | 1.0 | 0.8 | 0.6 | lower is better | quarterly | CFO |
| overdue_ar_over_60_pct | Receivables more than 60 days past invoice date as share of open AR | percent | 8 | 6 | 5 | lower is better | weekly | Billing and Collections Specialist |
| collections_ladder_adherence_pct | Overdue invoices actioned on the due ladder day (day 31, 38, 45, 60) | percent | 90 | 95 | 97 | higher is better | weekly | Billing and Collections Specialist |
| month_end_close_days | Working days from month end to books closed | days | 8 | 6 | 5 | lower is better | monthly | Finance Manager (Financial Controller from Q2 FY2028) |
| forecast_accuracy_pct | Revenue forecast accuracy, next-quarter, 1 minus absolute percentage error | percent | 90 | 93 | 95 | higher is better | quarterly | Finance Manager |
| cash_runway_months | Cash runway at trailing 3-month net burn (floor; no target for profitable months) | months | 18 | 24 | 24 | higher is better | monthly | CFO |
| gross_margin_pct | Gross margin | percent | 48 | 58 | 64 | higher is better | monthly | CFO (with delivery and customer_success heads) |
| ebitda_margin_pct | EBITDA margin | percent | -25 | 9 | 16 | higher is better | monthly | CFO |
| budget_variance_pct | Absolute department-level budget variance, year to date | percent | 5 | 4 | 3 | lower is better | monthly | Finance Manager |
| pricing_check_sla_pct | Deals priced-checked within 1 business day of `sales.deal_approval_requested` or `sales.proposal_requested` | percent | 95 | 97 | 98 | higher is better | weekly | Finance Manager (CFO until Q4 FY2026; FinanceAgent drafts, human approves) |

Twelve KPIs. The FY2026 targets above are the values exposed in `agent.py` as `KPIS`. Units follow `core.Kpi`: percent values are plain numbers (45, not 0.45), days and months are plain numbers; `higher_is_better` is False for `dso_days`, `bad_debt_pct_revenue`, `overdue_ar_over_60_pct`, `month_end_close_days` and `budget_variance_pct`.

## 2. Definitions and formulas

| KPI id | Formula | Notes and exclusions |
|---|---|---|
| dso_days | closing trade receivables incl. VAT / credit sales incl. VAT in the trailing 90 days x 90 | Countback method over 90 days to damp milestone lumpiness. Keep invoices (monthly in advance) are included. Disputed invoices stay in until credited. Target ties to the DSO ceiling of 45 days (COMPANY.md §7). |
| invoice_timeliness_pct | invoices with `issued_date - acceptance_date <= 2 business days` / all invoices triggered by a milestone or acceptance in the period x 100 | Trigger is `delivery.milestone_reached` or acceptance on `delivery.engagement_completed`. Signature-triggered 30% invoices run from `legal.contract_signed`. Keep monthly invoices are measured against the 1st of the month. Rule of record: COMPANY.md §7. |
| bad_debt_pct_revenue | (write-offs + change in expected-credit-loss provision) in the period / revenue in the period x 100 | Year-to-date measure. Policy ceiling is below 1% of revenue (COMPANY.md §7). Provision method: 1% of current, 5% of 31 to 60 days, 25% of 61 to 90 days, 50% of over 90 days, specific provision for disputed amounts. |
| overdue_ar_over_60_pct | open invoices more than 60 days past invoice date / total open invoices x 100 (by value) | The day-60 point is also the legal-letter point on the ladder (COMPANY.md §7). Measured at each Friday cut-off. |
| collections_ladder_adherence_pct | ladder actions completed on or before the scheduled day / ladder actions due in the period x 100 | Ladder: reminder day 31, call day 38, finance-head escalation day 45, legal letter day 60 (COMPANY.md §7). Maps to `finance.invoice_overdue` and `finance.collections_escalated`. Day counted from invoice date on net 30 terms. |
| month_end_close_days | business days from the last calendar day of the month to CFO sign-off of the close checklist | Emits `finance.month_end_closed`. FY2026 target 8 working days reflects a two-person team and a new ledger; 5 days by FY2028 once the Financial Controller is in post and revenue recognition is automated. |
| forecast_accuracy_pct | 100 x (1 - abs(forecast revenue - actual revenue) / actual revenue) for the quarter, forecast taken at the start of the quarter | Percentage-of-completion revenue for Compass and Forge plus straight-line Keep (COMPANY.md §7). Uses `delivery.capacity_forecast_updated` and `data.forecast_updated` as inputs. |
| cash_runway_months | closing cash and cash equivalents / average monthly net cash outflow of the trailing 3 months | Reported only while the trailing net cash flow is negative; when positive, reported as "not constrained" and the KPI is met by definition. Includes the £10m Series A in Q2 FY2026 (COMPANY.md §1). Floor policy: never below 12 months without a Board paper. |
| gross_margin_pct | (revenue - cost of revenue) / revenue x 100 | Cost of revenue = total cost of `delivery` and `customer_success` (COMPANY.md §5.1). Targets are the COMPANY.md figures; Finance owns measurement, not delivery levers. |
| ebitda_margin_pct | (revenue - total costs excluding D&A, interest, tax) / revenue x 100 | Targets: -£1.5m on £6.0m (-25%), £1.7m on £19.5m (9%), £7.2m on £46.2m (16%) (COMPANY.md §5.1). |
| budget_variance_pct | abs(actual YTD spend - budget YTD spend) / budget YTD spend x 100, measured per department and reported as the median and worst department | Budget is the §5.4 envelope phased monthly. `finance.budget_variance_flagged` fires when a department's variance exceeds 10% or £25k, whichever is lower. The KPI target applies to the median department; no department above 10%. |
| pricing_check_sla_pct | pricing checks completed within 1 business day / pricing checks requested x 100 | A pricing check compares quoted price to list prices (COMPANY.md §3), flags discount above 10% (Finance head and CEO approval, §9.3), non-standard payment terms and total contract value of £500k or more. Emits `finance.pricing_check_completed`. |

Guardrail: no KPI is reported as met if the underlying ledger period is still open. Figures reported to the Board come only from the closed month.

## 3. Reporting cadence and data sources

| Cadence | Report | Audience | KPIs covered | Source system (modeled) |
|---|---|---|---|---|
| Weekly (Friday cut-off) | AR and collections dashboard | CFO, Billing and Collections Specialist, CRO for named overdue accounts | invoice_timeliness_pct, overdue_ar_over_60_pct, collections_ladder_adherence_pct, pricing_check_sla_pct | Billing and AR sub-ledger; contract and milestone feed from `delivery.milestone_reached`, `legal.contract_signed` |
| Monthly (working day 8 in FY2026, then 6, then 5) | Management accounts pack | Executive team | dso_days, month_end_close_days, gross_margin_pct, ebitda_margin_pct, budget_variance_pct, cash_runway_months | General ledger (cloud accounting package), bank feeds, payroll journal from `people` |
| Monthly (working day 10) | 13-week cash forecast refresh | CFO, CEO | cash_runway_months | Bank balances, AR ageing, AP run, payroll, VAT and PAYE quarterly dates; emits `finance.cash_forecast_updated` |
| Quarterly (within 15 working days of quarter end) | Board finance report and rolling forecast | Board, Audit and Risk Committee (chair Marcus Ellery) | forecast_accuracy_pct, bad_debt_pct_revenue, all headline KPIs | Closed ledger, `data.kpi_report_published`, `executive.board_meeting_held` calendar |
| Annual (Q4) | Budget cycle BUD-<year> and KPI target reset | Board | all | `finance.budget_cycle_opened`, `*.budget_submitted`, `finance.budget_consolidated`, `executive.budget_approved` |

Data-quality controls:

1. Every KPI has one named calculation owner (section 1) and a second reviewer; the CFO signs the monthly pack.
2. Each KPI is recomputed from ledger extracts at close, not carried forward from the weekly dashboard.
3. Restatements of a prior period KPI of more than 1 percentage point (or 1 day for day-count KPIs) are footnoted in the next Board pack.
4. AI agent outputs (draft ageing commentary, variance narratives) are labelled as agent-drafted and reviewed by a human before circulation (COMPANY.md §9.4). Agents never approve payments above £10,000.
5. Cash and AR figures reconcile to bank and sub-ledger totals before the pack is released; unreconciled items over £5,000 block the close.

## 4. Links to company targets

| Company target (COMPANY.md) | Finance KPI(s) | How Finance moves or protects it |
|---|---|---|
| Revenue £6.0m / £19.5m / £46.2m (§5.1) | forecast_accuracy_pct, invoice_timeliness_pct | Accurate percentage-of-completion recognition and a quarterly rolling forecast; fast invoicing converts accepted milestones to cash. |
| Gross margin 48% / 58% / 64% (§5.1) | gross_margin_pct | Finance measures cost of revenue (delivery plus customer_success, §5.1, §5.4) monthly, flags scope creep via change-order pricing at the rate card (§3.5), and runs pricing checks so discounts do not erode margin. |
| EBITDA -£1.5m / £1.7m / £7.2m (§5.1) | ebitda_margin_pct, budget_variance_pct | Department envelopes of £7.5m / £17.8m / £39.0m total (§5.4) are the control total; variance flags keep spend inside them. |
| Total cost £7.5m / £17.8m / £39.0m (§5.2) | budget_variance_pct | Monthly variance versus the §5.4 envelope; unbudgeted spend above £50k needs CFO and above £250k CEO approval (§9.3). |
| Finance department budget £310k / £730k / £1,500k (§5.4) | month_end_close_days, forecast_accuracy_pct | KPIs improve as headcount grows from 2 to 5 to 10 humans (§6.1) and agents from 2 to 5 to 9 (§6.1); the department budget is itself tracked under budget_variance_pct. |
| DSO <= 45 days (§7) | dso_days, overdue_ar_over_60_pct, collections_ladder_adherence_pct | Net 30 terms, ladder at day 31 / 38 / 45 / 60, and Finance-head escalation. FY2027 and FY2028 targets tighten to 42 and 40 days as US contracts (15% and 30% of revenue, §1) are collected on stricter terms. |
| Bad debt below 1% of revenue (§7) | bad_debt_pct_revenue | Credit checks at proposal stage, ladder adherence and the day-60 legal letter. Target tightens from 1.0% to 0.6% as client mix matures. |
| Invoices issued within 2 business days of milestone acceptance (§7) | invoice_timeliness_pct | Billing schedule created at signature (`finance.billing_schedule_created`) and agent-drafted invoices queued against milestones. |
| Keep ARR £1.5m / £6.5m / £17.0m at year end (§5.1) | invoice_timeliness_pct, dso_days | Keep invoices monthly in advance with annual CPI + 2% uplift capped at 7% (§7); Finance verifies uplifts are invoiced from each renewal date. |
| Series A of £10m in Q2 FY2026 and seed of £3.5m (§1) | cash_runway_months | 13-week cash forecast and runway floor of 12 months (Board paper if breached) protect the post-raise plan through the FY2026 EBITDA loss of £1.5m. |
| Discount and non-standard terms approvals (§9.3) | pricing_check_sla_pct | Every discount above 10%, non-standard payment term, or deal of £500k or more is routed to Finance head and CEO within 1 business day. |
| No client concentration above 15% of revenue (§8) | forecast_accuracy_pct (supporting) | Finance reports top-client share quarterly alongside the forecast; breaches go to the Audit and Risk Committee. |

Cross-department dependencies: billing speed depends on `delivery.milestone_reached` being published on acceptance; DSO depends on `external.client_payment_received` and `finance.payment_received` matching within one business day; budget variance depends on each department submitting its `<dept>.budget_submitted` during the budget cycle.
