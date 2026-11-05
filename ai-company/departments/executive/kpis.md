# Executive KPIs

## 1. KPI summary

Eleven KPIs. The first five are company outcomes that the CEO is accountable to the Board for; the remaining six measure the quality and speed of the decisions this department owns. FY2026 targets are exposed in `agent.py` as `KPIS`.

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| revenue_gbp_m | Revenue | £m | 6.0 | 19.5 | 46.2 | Higher is better | Monthly | Chief Executive Officer |
| ebitda_margin_pct | EBITDA margin | percent | -25 | 9 | 16 | Higher is better | Monthly | Chief Executive Officer |
| active_clients | Active clients (billed in year) | count | 24 | 65 | 140 | Higher is better | Monthly | Chief Executive Officer |
| gross_margin_pct | Gross margin | percent | 48 | 58 | 64 | Higher is better | Monthly | Chief Executive Officer |
| top_client_share_pct | Largest client share of revenue | percent | 15 | 15 | 15 | Lower is better | Monthly | Chief Executive Officer |
| okr_attainment_pct | Company OKR attainment | percent | 75 | 75 | 75 | Higher is better | Quarterly | Strategy and Transformation Lead |
| deal_decision_hours | Deal decision turnaround (£500k or more) | hours | 48 | 36 | 24 | Lower is better | Per decision, reported monthly | Chief of Staff |
| headcount_decision_days | Headcount decision turnaround | days | 5 | 5 | 3 | Lower is better | Per decision, reported monthly | Chief of Staff |
| board_pack_on_time_pct | Board packs issued 5 working days before meeting | percent | 100 | 100 | 100 | Higher is better | Quarterly | Chief of Staff |
| crisis_declaration_hours | Time from trigger to crisis decision | hours | 4 | 2 | 2 | Lower is better | Per event | Chief Executive Officer |
| cash_runway_months | Cash runway at forecast burn | months | 24 | 24 | 24 | Higher is better | Monthly | Chief Executive Officer |

## 2. Definitions and formulas

| KPI id | Definition and formula | Source of truth |
|---|---|---|
| revenue_gbp_m | Recognised revenue in the fiscal year. Fixed fee on percentage-of-completion, Keep straight-line monthly (`COMPANY.md §7`). Reported year to date and as full-year forecast. Formula: sum of monthly recognised revenue / 1,000,000. | `finance.month_end_closed` |
| ebitda_margin_pct | EBITDA divided by revenue, times 100. FY2026 plan is -£1.5m on £6.0m = -25%. | `finance.month_end_closed` |
| active_clients | Distinct clients billed at least once in the fiscal year. | `finance.invoice_issued` via Data |
| gross_margin_pct | (Revenue minus cost of revenue) / revenue, times 100. Cost of revenue is the total cost of the delivery and customer_success departments (`COMPANY.md §5.1`). | `finance.month_end_closed` |
| top_client_share_pct | Trailing-12-month revenue from the single largest client divided by trailing-12-month company revenue, times 100. Policy cap is 15%; amber at 10%. | Finance billing ledger via Data |
| okr_attainment_pct | Mean of key-result attainment across company OKRs at quarter end, each capped at 100%. Target is 75%, because OKRs are set as stretch goals. | Strategy and Transformation Lead's OKR tracker |
| deal_decision_hours | Hours from `sales.deal_approval_requested` to `executive.deal_decision_made`, counted over business days only (24 hours per business day). Median over the period. | Event log timestamps (sim days times 24) |
| headcount_decision_days | Business days from `people.requisition_opened` to `executive.headcount_approved` (or refusal). Median. | Event log |
| board_pack_on_time_pct | Board packs issued at least 5 working days before the meeting / packs due, times 100. | Board secretary log |
| crisis_declaration_hours | Hours from the first qualifying trigger (SOP-EXECUTIVE-06 table) to `executive.crisis_declared`. Zero crises in a period reports as not applicable. | Event log |
| cash_runway_months | Cash balance divided by average monthly net cash burn over the next 6 months of the forecast. Floor is 24 months; below 12 triggers a hiring freeze review; below 6 triggers a liquidity crisis. Funding: £3.5m seed and £10m Series A (`COMPANY.md §1`). | `finance.cash_forecast_updated` |

## 3. Reporting cadence and data sources

| Cadence | Event | Content | Producer |
|---|---|---|---|
| Daily during a crisis | Crisis review | Status of actions, notifications, next review time | Chief of Staff |
| Weekly (Monday) | Executive team meeting | Pipeline, decisions awaiting CEO, risks | Chief of Staff |
| Monthly (working day 8) | KPI review | All 11 KPIs against target, using `finance.month_end_closed` and `data.kpi_report_published` | Data (published), Chief of Staff (decision KPIs) |
| Quarterly | Board meeting (target 15 January, April, July, October) | Board pack: KPIs, financials, pipeline, risks, decisions, OKR review | Board and Investor Relations Manager (Chief of Staff in FY2026) |
| Annually (Q4) | Budget and OKR cycle | FY budget, OKRs, strategy refresh | Chief of Staff, Strategy and Transformation Lead |

Data sources: `finance.month_end_closed` (revenue, EBITDA, gross margin), `finance.cash_forecast_updated` (runway), `data.kpi_report_published` (consolidated KPI report), `data.forecast_updated` (forecast revisions), the executive event log (decision and crisis timings) and the OKR tracker. The Executive agent updates the KPI actuals from these messages (`ExecutiveAgent.kpi_snapshot()`).

Thresholds the agent applies: revenue year to date more than 10% behind plan raises a re-forecast task; three consecutive such months are reported to the Board chair; client share above 10% is flagged to the Board; above 15% blocks a deal.

## 4. Links to company targets

| KPI id | Rolls up to | Company target cited |
|---|---|---|
| revenue_gbp_m | Revenue = clients x ACV | £6.0m, £19.5m, £46.2m (`COMPANY.md §5.1`) |
| ebitda_margin_pct | EBITDA | -£1.5m (-25%), £1.7m (9%), £7.2m (16%) (`COMPANY.md §5.1`) |
| active_clients | Active clients | 24, 65, 140 (`COMPANY.md §5.1`) |
| gross_margin_pct | Gross margin | 48%, 58%, 64% (`COMPANY.md §5.1`) |
| top_client_share_pct | Concentration policy | No client above 15% of revenue (`COMPANY.md §8`, assumption 8) |
| okr_attainment_pct | Strategy execution | Strategy and targets in `COMPANY.md §5` and `§8` |
| deal_decision_hours | Sales cycle and win rate | 75-day average cycle, 30% win rate (`COMPANY.md §5.3`); delegation of authority (`COMPANY.md §9.3`) |
| headcount_decision_days | Hiring speed | 45-day time-to-hire, 5-day agent provisioning (`COMPANY.md §8`, assumption 3); headcount plan 38 / 110 / 230 (`COMPANY.md §6`) |
| board_pack_on_time_pct | Board governance | Quarterly Board, Audit and Risk and Remuneration committees (`COMPANY.md §9.1`) |
| crisis_declaration_hours | Breach notification | ICO notification within 72 hours (`COMPANY.md §9.3`) |
| cash_runway_months | Funding | £3.5m seed, £10m Series A (`COMPANY.md §1`); FY2026 EBITDA of -£1.5m (`COMPANY.md §5.1`) |

Executive cost as a share of revenue is tracked in `economics.md` (10.0%, 5.4%, 2.8%) against the department budget of £600k, £1,050k and £1,300k (`COMPANY.md §5.4`).
