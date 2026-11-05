# Customer Success KPIs

Department: `customer_success` (account management, client onboarding, health scoring, support, renewals and churn prevention, Keep retainer support tiers and SLAs). Head: Chief Customer Officer, Tobias Lindgren (COMPANY.md §9.2). Agent class: `CustomerSuccessAgent`. All figures are modeled assumptions in GBP unless stated.

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| net_revenue_retention | Net revenue retention of retained clients | percent | 100 | 115 | 118 | higher is better | quarterly | Chief Customer Officer |
| gross_revenue_retention | Gross revenue retention | percent | 90 | 90 | 91 | higher is better | quarterly | Chief Customer Officer |
| logo_retention | Logo retention | percent | 83 | 83 | 85 | higher is better | quarterly | Chief Customer Officer |
| nps | Net Promoter Score | points | 40 | 45 | 50 | higher is better | quarterly | Customer Success Analyst (Chief Customer Officer until Q3 FY2027) |
| csat | Client satisfaction on closed tickets and milestones | percent | 90 | 91 | 92 | higher is better | monthly | Client Support Specialist (Chief Customer Officer until Q2 FY2027; Client Support Lead from Q1 FY2028) |
| avg_health_score | Average client health score | points | 72 | 74 | 76 | higher is better | weekly | Customer Success Analyst (Chief Customer Officer until Q3 FY2027) |
| green_client_share | Share of active clients in the green band | percent | 60 | 65 | 70 | higher is better | weekly | Chief Customer Officer |
| keep_attach_forge_build_scale | Keep attach rate on Forge Build and Scale clients within 12 months of completion | percent | 75 | 85 | 90 | higher is better | quarterly | Renewals and Commercial Manager (Chief Customer Officer until Q1 FY2028) |
| keep_attach_compass_programme | Keep attach rate on Compass Programme clients within 12 months of completion | percent | 40 | 40 | 45 | higher is better | quarterly | Renewals and Commercial Manager (Chief Customer Officer until Q1 FY2028) |
| support_first_response_sla | Tickets with first response inside the Keep tier SLA | percent | 95 | 96 | 97 | higher is better | weekly | Client Support Specialist (Chief Customer Officer until Q2 FY2027; Client Support Lead from Q1 FY2028) |
| at_risk_save_rate | Flagged at-risk clients retained | percent | 40 | 45 | 50 | higher is better | quarterly | Chief Customer Officer |
| qbr_completion_rate | Keep QBRs held within 21 days of quarter start | percent | 90 | 92 | 95 | higher is better | quarterly | Customer Success Manager (Chief Customer Officer until Q1 FY2027) |
| onboarding_handover_days | Days from contract signature to completed handover | days | 15 | 12 | 10 | lower is better | monthly | Customer Success Manager (Chief Customer Officer until Q1 FY2027) |
| cs_cost_pct_revenue | Customer Success cost as share of revenue | percent | 2.3 | 4.1 | 3.5 | lower is better | monthly | Chief Customer Officer |

Fourteen KPIs. The FY2026 targets above are the values exposed in `agent.py` as `KPIS`. Units follow `core.Kpi`: percent values are plain numbers (90, not 0.90), days and points are plain numbers; `higher_is_better` is False for `onboarding_handover_days` and `cs_cost_pct_revenue`.

## 2. Definitions and formulas

| KPI id | Formula | Notes and exclusions |
|---|---|---|
| net_revenue_retention | revenue in the year from clients that were also active in the prior year / those clients' revenue in the prior year x 100 | Measured on retained clients, as in COMPANY.md §5.1 (115% FY2027, 118% FY2028). Includes expansion, Keep uplift of CPI + 2% (cap 7%) and contraction; excludes revenue from new logos. FY2026 has no prior-year cohort, so 100 is a floor applied from the first renewal cohort in FY2027, and the FY2026 reading is "not yet measurable". Agent field: `nrr_delta_gbp` on `customer_success.renewal_confirmed` |
| gross_revenue_retention | (opening recurring and repeat revenue of the cohort minus churned and contracted revenue, expansion excluded) / opening revenue x 100 | Capped at 100. Sits above logo retention because churn is weighted to Spark, Sprint and Keep Essential clients. Source: `customer_success.client_churned` (`amount_gbp`) and `customer_success.renewal_confirmed` (`previous_amount_gbp`, `amount_gbp`) |
| logo_retention | clients active at both start and end of the year / clients active at start x 100 | COMPANY.md §5.1: 83% FY2027 (20 of 24 retained) and 85% FY2028 (55 of 65). FY2026 target 83 is the planning rate for the first cohort. A client that completes a fixed-fee project and does not buy again is counted as churned only once its last engagement is 12 months complete |
| nps | % promoters (score 9 to 10) minus % detractors (0 to 6) over responses in the period | Relationship survey to the sponsor each quarter plus a post-engagement survey 7 days after `delivery.engagement_completed`. Minimum 10 responses in the period or the reading is shown as provisional. Agent: `feedback_received.category` = promoter, passive or detractor |
| csat | responses scoring 4 or 5 on a 1 to 5 scale / all responses x 100 | Collected on ticket closure and at each delivery milestone. Agent maps a score `s` to the sentiment component as (s - 1) x 25 |
| avg_health_score | mean of `health_score` across non-churned clients, equal-weighted | Score model in sops.md (SOP-CUSTOMER_SUCCESS-02): adoption 25%, delivery 20%, engagement 15%, commercial 15%, sentiment 15%, support 10%. Clients in the first 30 days are included at the baseline of 76.5 (green) until their first signals arrive |
| green_client_share | clients with score 75 or above / non-churned clients x 100 | Bands: green 75 and above, amber 50 to under 75, red under 50 |
| keep_attach_forge_build_scale | Forge Build and Scale engagements completed in the trailing 12 to 24 months with a signed Keep contract within 12 months of completion / those completed engagements x 100 | COMPANY.md §2 sets the policy that Keep attaches to every Forge Build and Scale; the KPI is the realised rate. Recommended tier: Plus after Build, Enterprise after Scale |
| keep_attach_compass_programme | Compass Programme engagements completed with a signed Keep contract within 12 months / completed Compass Programmes x 100 | COMPANY.md §2: at least 40% of Compass Programmes. Recommended tier: Essential |
| support_first_response_sla | tickets whose first human or agent-assisted response was sent within the first-response target for the client's Keep tier and priority / all tickets x 100 | Targets in sops.md (SOP-CUSTOMER_SUCCESS-03). Business-hours clock (10-hour day, 08:00 to 18:00 UK) for Essential and Plus; 24x7 for Enterprise P1 and P2. Auto-acknowledgements do not count |
| at_risk_save_rate | flagged at-risk clients still active 90 days after the flag / clients flagged in the period x 100 | A flag is `customer_success.churn_risk_flagged`. A client that churns after a termination notice is a failed save; one that withdraws its notice, or renews, is a save |
| qbr_completion_rate | Keep clients with a QBR held by day 21 of the quarter / Keep clients due a QBR x 100 | Quarterly QBR for Essential, Plus and Enterprise (COMPANY.md §3.3 lists it for all tiers; Enterprise adds the executive steering committee) |
| onboarding_handover_days | calendar days from `legal.contract_signed` to the day the success plan is agreed and the handover pack is accepted by the named client manager | Median across clients onboarded in the month. Task due dates in the agent: welcome call 2 days, success plan 10 days, Keep onboarding 5 days, kickoff handover 5 days |
| cs_cost_pct_revenue | Customer Success department cost (people plus non-people) / revenue x 100 | Budget basis: £140k / £6,000k = 2.3% (FY2026), £790k / £19,500k = 4.1% (FY2027), £1,630k / £46,200k = 3.5% (FY2028) (COMPANY.md §5.4, §5.1). Part of cost of revenue |

Guardrail: no retention KPI is reported as met for a period until Finance has closed the month in which the last renewal or churn decision of that period took effect.

## 3. Reporting cadence and data sources

| Cadence | Report | Audience | KPIs covered | Source system (modeled) |
|---|---|---|---|---|
| Weekly (Monday) | Client health review | Chief Customer Officer, Customer Success Managers, Managing Partner Delivery for red and amber clients | avg_health_score, green_client_share, support_first_response_sla | Health score store, ticket desk, `delivery.*` and `finance.*` signals |
| Monthly (working day 10) | Customer Success management pack | Executive team | csat, onboarding_handover_days, cs_cost_pct_revenue | Ticket desk, onboarding tracker, Finance ledger extract |
| Quarterly (within 15 working days of quarter end) | Retention and expansion report | Board and Audit and Risk Committee; Sales and Finance | net_revenue_retention, gross_revenue_retention, logo_retention, nps, keep_attach_forge_build_scale, keep_attach_compass_programme, at_risk_save_rate, qbr_completion_rate | Contract register, billing, `customer_success.renewal_confirmed` and `customer_success.client_churned` |
| Annual (Q4) | Budget cycle BUD-<year> and KPI target reset | Board | all | `finance.budget_cycle_opened`, `customer_success.budget_submitted`, `executive.budget_approved` |

Data-quality controls:

1. Each KPI has one named calculation owner (section 1) and the Data department reconciles client counts to Finance's active-client count each quarter.
2. Retention KPIs are recomputed from the contract register and billing extracts, not from the health store.
3. Restatements of a prior-period retention KPI of more than 1 percentage point are footnoted in the next Board pack.
4. Agent-drafted commentary is labelled and reviewed by a human before circulation (COMPANY.md §9.4).
5. Health scores are never edited by hand: corrections are made to the input signal and the model recalculates.

## 4. Links to company targets

| Company target (COMPANY.md) | Customer Success KPI(s) | How Customer Success moves or protects it |
|---|---|---|
| Net revenue retention 115% FY2027, 118% FY2028 (§5.1) | net_revenue_retention, keep_attach_forge_build_scale | Renewal plans 90 days before term end, uplift of CPI + 2% capped at 7% (§7), expansion hand-offs to Sales |
| Logo retention 83% FY2027 (20 of 24) and 85% FY2028 (55 of 65) (§5.1) | logo_retention, at_risk_save_rate, avg_health_score | Early churn-risk flags, executive save plans, post-mortems within 15 business days |
| Revenue of £6.0m / £19.5m / £46.2m (§5.1) | gross_revenue_retention, net_revenue_retention | Retained and expanded revenue from the prior year's cohort is the base of the next year's plan |
| Keep ARR £1.5m / £6.5m / £17.0m at year end (§5.1) | keep_attach_forge_build_scale, keep_attach_compass_programme, support_first_response_sla | Keep attached to every Forge Build and Scale and at least 40% of Compass Programmes (§2); SLAs protect renewal |
| Gross margin 48% / 58% / 64% (§5.1) | cs_cost_pct_revenue | Customer Success is cost of revenue with Delivery (§5.1, §5.4); its cost as a share of revenue is held at 2.3%, 4.1% and 3.5% |
| Customer Success budget £140k / £790k / £1,630k (§5.4) | cs_cost_pct_revenue | KPI tracks the department's own spend against revenue; headcount from 1 to 6 to 14 humans and 1 to 5 to 12 agents (§6.1) |
| Collections ladder: reminder day 31, call day 38, escalation day 45 (§7) | avg_health_score (commercial component) | Overdue invoices lower the commercial component; Customer Success makes the day-38 relationship call alongside Finance |
| Keep tiers with 5 / 15 support days a quarter, named client manager, 24x7 Enterprise cover (§3.3) | support_first_response_sla, qbr_completion_rate | SLA clocks by tier; quarterly QBR for every Keep client; Enterprise steering committee |
| No client above 15% of revenue (§8) | green_client_share (supporting) | Top-client health reviewed weekly by the Chief Customer Officer |
| Land and expand journey from Spark to Keep Plus (§10) | keep_attach_forge_build_scale | Engagement closeout triggers the attach recommendation (`customer_success.expansion_opportunity_identified`) |

Cross-department dependencies: health depends on Delivery publishing `delivery.milestone_reached` and `delivery.quality_issue_raised`, on Finance publishing `finance.invoice_overdue` and `finance.payment_received`, and on Legal publishing `legal.client_dispute_raised`; renewal KPIs depend on Sales publishing `sales.renewal_proposal_sent` and Legal publishing `legal.contract_signed`.
