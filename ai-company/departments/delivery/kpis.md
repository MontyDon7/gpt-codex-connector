# Delivery KPIs

Department: `delivery` (client delivery and consulting: scoping, staffing humans and AI agents, engagements, milestones, scope changes, quality). Head: Managing Partner, Delivery (Oliver Thackeray, COMPANY.md §9.2). Agent class: `DeliveryAgent`. All figures are modeled assumptions derived from COMPANY.md; none are real data.

Delivery is the largest cost-of-revenue department (COMPANY.md §5.4: £2,980k / £7,400k / £15,000k), so its KPIs are the main operational levers behind the company gross margin of 48% / 58% / 64% (§5.1).

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| billable_utilisation | Billable utilisation (delivery humans, blended) | percent | 66 | 70 | 70 | higher is better | weekly | Delivery Operations Lead |
| on_time_milestone_rate | On-time milestone delivery | percent | 85 | 88 | 90 | higher is better | weekly | Engagement Managers (rolled up by Principals) |
| first_pass_qa_rate | Deliverables passing Manager QA gate first time | percent | 82 | 87 | 90 | higher is better | weekly | Quality Lead |
| scope_change_rate | Engagements with at least one scope change request | percent | 30 | 25 | 22 | lower is better | monthly | Engagement Managers |
| client_csat | Client satisfaction at milestone and close (1 to 5 scale) | score | 4.3 | 4.4 | 4.5 | higher is better | monthly | Managing Partner, Delivery |
| agent_leverage_ratio | AI agents per delivery human (year-end) | ratio | 0.43 | 0.48 | 0.50 | higher is better | monthly | Head of AI Delivery |
| delivery_gross_margin | Engagement gross margin (fees recognised minus direct delivery cost) | percent | 50 | 62 | 67 | higher is better | monthly | Managing Partner, Delivery |
| quality_escapes_per_engagement | Client-reported defects after release per completed engagement | count | 0.5 | 0.4 | 0.3 | lower is better | monthly | Quality Lead |
| time_to_staff_days | Time from staffing request to named, started team | business days | 10 | 8 | 7 | lower is better | monthly | Delivery Operations Lead |
| keep_attach_rate | Completed Forge Build / Forge Scale / Compass Programme engagements handed to Keep with a signed or proposed retainer | percent | 70 | 85 | 90 | higher is better | quarterly | Principals (with Customer Success) |
| delivery_attrition | Annualised voluntary attrition, delivery humans | percent | 14 | 12 | 11 | lower is better | quarterly | Managing Partner, Delivery (with People) |
| subcontractor_cost_ratio | Subcontractor and associate spend as share of delivery department cost | percent | 30 | 24 | 23 | lower is better | quarterly | Delivery Operations Lead |

Twelve KPIs. The FY2026 column is the set exposed as `KPIS: list[core.Kpi]` in `agent.py`; `higher_is_better` follows the Direction column.

## 2. Definitions and formulas

### 2.1 billable_utilisation

`billable_hours / available_hours`, summed across delivery humans in the period. Available hours = contractual hours minus approved leave, public holidays and statutory absence. Billable hours = time booked to client engagements (fixed-fee engagements are measured on effort booked, not on fee). Internal, bench, pre-sales scoping that is not yet won, training and recruitment time are non-billable.

Role-level reference targets (COMPANY.md §4), stated at FY2027/FY2028 steady state:

| Level | Target utilisation |
|---|---|
| Analyst / Consultant | 80% |
| Senior Consultant | 75% (interpolated between 80% and 65%; reported separately) |
| Manager | 65% |
| Principal | 50% |
| Partner | 35% |
| Blended (weighted by the §4 staffing pyramid) | 70% |

The FY2026 blended target is 66% because a 14-person team has a disproportionate share of leadership time and a ramp-up period for new joiners (first 4 weeks at 50%). Amber below target minus 3 points; red below target minus 6 points. AI agent-days are excluded from this KPI and tracked in `agent_leverage_ratio`.

### 2.2 on_time_milestone_rate

`milestones accepted on or before the contractual date / milestones due in the period`. A milestone is "accepted" when the client sponsor signs off (the trigger for the invoice under COMPANY.md §7, issued within 2 business days). A milestone re-baselined by a signed change order is measured against the new date but flagged; re-baselines caused by client delay are tagged `client_dependency` and reported separately so Delivery is not penalised for them, though the headline rate uses the original date. Source event: `delivery.milestone_reached`.

### 2.3 first_pass_qa_rate

`deliverables approved by the reviewing Manager (or above) without a rework request / deliverables submitted to the quality gate`. The gate is mandatory for every client deliverable (COMPANY.md §4, §9.4). Deliverables containing agent-drafted content count in the same population; the ratio for agent-assisted versus human-only deliverables is reported as a diagnostic, not a KPI. Rework request = reviewer returns the document with at least one blocking comment (formatting-only comments do not count).

### 2.4 scope_change_rate

`engagements with at least one raised scope change request / engagements active in the period` (trailing 12 months for stability). Source event: `delivery.scope_change_requested`. The KPI is lower-is-better as a proxy for scoping quality, but it is not driven to zero: well-handled change orders at rate card (COMPANY.md §3.5) are healthy margin. Diagnostic: change-order value as a percentage of base fee, and percentage of change requests signed before work started (target 100%).

### 2.5 client_csat

Mean of the sponsor's 1 to 5 score at each accepted milestone pulse survey and at engagement close, weighted equally per engagement. Reported on a 1 to 5 scale. Responses are collected by Customer Success and arrive via `customer_success.feedback_received`. Minimum 70% response coverage of live engagements; below that the KPI is shown as "provisional".

### 2.6 agent_leverage_ratio

`AI agents attached to delivery / delivery humans`, at period end. FY2026 to FY2028 targets are derived from COMPANY.md §6.1: 6/14 = 0.43, 22/46 = 0.48, 52/104 = 0.50. This sits within the §2 leverage range of roughly 0.5 to 0.65 agents per delivery human, at its lower end because the hiring plan front-loads humans. A secondary diagnostic is agent-days billed per engagement at the £350 agent-day rate (COMPANY.md §3.5).

### 2.7 delivery_gross_margin

`(recognised fee revenue on delivery engagements minus direct delivery cost) / recognised fee revenue`. Direct delivery cost = people cost of delivery humans (base x 1.28), AI compute and tooling charged to engagements, subcontractors and associates. Revenue is recognised on percentage-of-completion for fixed fee and straight-line monthly for Keep (COMPANY.md §7). This delivery-only measure sits above the company gross margin target (48% / 58% / 64%, COMPANY.md §5.1) because company cost of revenue also carries the Customer Success department (£140k / £790k / £1,630k).

Worked check for FY2026: revenue £6.0m; delivery cost £2.98m; Customer Success cost £0.14m; gross margin = (6.00 - 3.12) / 6.00 = 48%. Delivery-only margin = (6.00 - 2.98) / 6.00 = 50.3%, matching the 50% target. FY2027: (19.5 - 7.40) / 19.5 = 62.1%, target 62%. FY2028: (46.2 - 15.0) / 46.2 = 67.5%, target 67%.

### 2.8 quality_escapes_per_engagement

`client-reported defects on released deliverables (post-acceptance) / engagements completed in the period`. A defect is a confirmed factual, analytical or functional error in a released deliverable or production agent, as logged through `delivery.quality_issue_raised` (severity 1 to 3). Severity 1 (client-impacting, material) additionally triggers a root-cause review within 5 business days. Excluded: change requests and requirements the client changed after acceptance.

### 2.9 time_to_staff_days

Business days from `delivery.staffing_requested` to the date the last required named role has started on the engagement (humans) or has been provisioned (agents; COMPANY.md §8 assumes 5 days for agent provisioning). If the plan requires an external hire, the clock stops at the requisition handoff and a separate hiring KPI (time-to-hire 45 days, COMPANY.md §8) applies; this KPI measures internal allocation only. Reported as the median and the 90th percentile; the target applies to the median.

### 2.10 keep_attach_rate

`engagements of type Forge Build, Forge Scale or Compass Programme that closed in the period with a Keep retainer signed or a formal retainer proposal issued / all such engagements that closed in the period`. COMPANY.md §2 sets the commercial target: a Keep retainer attached to every Forge Build/Scale and at least 40% of Compass Programmes. The delivery KPI measures the handoff discipline (retainer proposed at close), which is why the target is 70% / 85% / 90% across the combined population. Source event: `delivery.engagement_completed` joined to `sales.renewal_proposal_sent` and `customer_success.renewal_confirmed`.

### 2.11 delivery_attrition

`delivery humans who left voluntarily in trailing 12 months / average delivery humans in the same period`. COMPANY.md §8 sets company attrition at 14% in Y1 falling to 11% in Y3; the delivery targets equal those figures. Regretted losses (Senior Consultant and above, or any named engagement lead mid-engagement) are reported separately. Source: `people.engagement_survey_completed` for leading indicators and People's leaver records.

### 2.12 subcontractor_cost_ratio

`subcontractor and associate spend attributed to delivery / total delivery department cost`. Using COMPANY.md §5.2 (subcontractors £0.9m / £1.8m / £3.5m) against §5.4 delivery totals of £2,980k / £7,400k / £15,000k gives 30% / 24% / 23%. Subcontractors are used as flex capacity and for specialist skills; the ratio falls as the permanent bench and agent leverage grow. Subcontracted work still passes the Manager QA gate and is covered by the data-processing agreement.

## 3. Reporting cadence and data sources

| Cadence | Forum | Content | Audience |
|---|---|---|---|
| Weekly (Monday) | Delivery staffing and delivery-health meeting | utilisation, on-time milestones, first-pass QA, open quality issues, 6-week capacity forecast (`delivery.capacity_forecast_updated`) | Managing Partner, Principals, Delivery Operations Lead |
| Monthly (working day 5, after finance close) | Delivery business review | all monthly KPIs, engagement margin by engagement, agent leverage, scope change log, CSAT | Managing Partner, CFO, COO |
| Quarterly | Delivery quarterly review and company OKR check-in | quarterly KPIs, attach rate, attrition, subcontractor ratio, OKR progress against `executive.okrs_set` | CEO, executive team, Board pack input |
| Annual | Budget cycle (`finance.budget_cycle_opened` then `delivery.budget_submitted`) | target reset, headcount and non-people envelope check against COMPANY.md §5.4 | CFO, CEO |

Data sources:

| KPI | System of record | Events consumed or produced |
|---|---|---|
| billable_utilisation | Time-entry system (PSA), HR roster | `people.new_hire_started` (ramp status), publishes `delivery.capacity_forecast_updated` |
| on_time_milestone_rate | PSA milestone plan, client acceptance records | publishes `delivery.milestone_reached` |
| first_pass_qa_rate | Quality-gate register (Manager review log) | consumes `data.agent_quality_report_published` |
| scope_change_rate | Change-order register | publishes `delivery.scope_change_requested`; consumes `external.client_scope_request` |
| client_csat | Customer Success survey tool | consumes `customer_success.feedback_received`, `customer_success.health_score_updated` |
| agent_leverage_ratio | Agent register (Data and IT Security) | consumes `product.agent_capability_added`, `product.release_shipped` |
| delivery_gross_margin | Finance ledger, PSA cost allocation | consumes `finance.billing_schedule_created`; publishes `delivery.budget_submitted` |
| quality_escapes_per_engagement | Quality-issue log | publishes `delivery.quality_issue_raised`; consumes `customer_success.support_escalated` |
| time_to_staff_days | PSA resourcing module | publishes `delivery.staffing_requested`, `delivery.hire_requested`; consumes `sales.deal_won`, `legal.contract_signed` |
| keep_attach_rate | CRM, Keep contract register | publishes `delivery.engagement_completed`; consumes `customer_success.renewal_confirmed` |
| delivery_attrition | HR information system | publishes `delivery.hire_requested`; consumes `people.engagement_survey_completed` |
| subcontractor_cost_ratio | Finance ledger (subcontractor cost centres) | consumes `finance.budget_cycle_opened` |

Data quality controls: time entries lock at 17:00 each Friday with an exception report to engagement managers by Monday; KPI values are recomputed from source each month (no manual overrides without a logged reason); Customer Success and Delivery reconcile the engagement list monthly so the denominators match.

Escalation thresholds: any KPI red for two consecutive periods goes to the Managing Partner with a written recovery plan; a Severity 1 quality escape or a milestone more than 10 business days late is escalated the same day to the Managing Partner and the Chief Customer Officer. In a declared crisis (`executive.crisis_declared`) the cadence moves to daily for utilisation, milestones and quality issues.

## 4. Links to company targets

| Company target (COMPANY.md) | Delivery KPI contribution |
|---|---|
| §5.1 Revenue £6.0m / £19.5m / £46.2m | Revenue is recognised on percentage-of-completion; `on_time_milestone_rate` drives milestone billing (30/40/30, §7) and therefore revenue timing and cash. `time_to_staff_days` bounds start-up delay after `sales.deal_won`. |
| §5.1 Gross margin 48% / 58% / 64% | `billable_utilisation`, `delivery_gross_margin`, `agent_leverage_ratio`, `subcontractor_cost_ratio` and `first_pass_qa_rate` (rework hours) are the direct levers. Delivery is 50% / 38% / 32% of revenue as cost (§5.4), so a one-point improvement in delivery margin is worth about £60k / £195k / £462k of gross profit. |
| §5.1 Net revenue retention 115% / 118% and Keep ARR £1.5m / £6.5m / £17.0m | `keep_attach_rate`, `client_csat` and `quality_escapes_per_engagement` feed retention and expansion; delivery hands each completed Forge Build/Scale to Keep (§2). |
| §5.1 Logo retention 83% / 85% | `client_csat` and `quality_escapes_per_engagement` are leading indicators for `customer_success.churn_risk_flagged`. |
| §4 Delivery model (utilisation 70% blended, pyramid, QA gate) | `billable_utilisation` and `first_pass_qa_rate` measure the model directly. |
| §5.4 Delivery budget £2,980k / £7,400k / £15,000k | `delivery_gross_margin` and `subcontractor_cost_ratio` are the budget-compliance KPIs; variance beyond 5% is escalated through the budget cycle. |
| §6.1 Delivery headcount 14 / 46 / 104 humans, 6 / 22 / 52 agents | `agent_leverage_ratio` is derived from these rows; `time_to_staff_days` and `delivery_attrition` track hiring plan execution. |
| §8 Assumptions (attrition 14% to 11%, time-to-hire 45 days, agent provisioning 5 days) | `delivery_attrition` and `time_to_staff_days` use them as baselines. |
| §9.4 AI agent governance (human QA before release) | `first_pass_qa_rate` and `quality_escapes_per_engagement` evidence that agent-assisted work is reviewed and reliable. |
