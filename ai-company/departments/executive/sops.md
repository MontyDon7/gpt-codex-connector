# Executive Standard Operating Procedures

## Overview

Steps marked [human] are done by the named human; steps marked [agent] are done by the Executive Chief-of-Staff Agent (`ExecutiveAgent`) within the limits in `blueprint.md` Section 4 and `COMPANY.md §9.4`. Business days are Monday to Friday in London. Delegations of authority are in `COMPANY.md §9.3`.

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-EXECUTIVE-01 | Deal approval (£500k or more) | `sales.deal_approval_requested`, `sales.proposal_sent` | Chief Executive Officer | 2 business days (48 hours) from request |
| SOP-EXECUTIVE-02 | Board meetings and Board-level approvals | `external.board_request`; quarterly schedule | Chief of Staff | Pack 5 working days before meeting; minutes within 5 working days after |
| SOP-EXECUTIVE-03 | Headcount approval and executive hiring | `people.requisition_opened`, `people.hire_requested` | Chief Executive Officer | 5 business days; in-plan 2 business days |
| SOP-EXECUTIVE-04 | Annual budget and OKR cycle | `finance.budget_cycle_opened`, `finance.budget_submitted`, `finance.budget_consolidated` | Chief Executive Officer | Own submission within 10 business days of cycle open; approval within 10 business days of consolidation |
| SOP-EXECUTIVE-05 | In-year performance and cash review | `finance.month_end_closed`, `finance.budget_variance_flagged`, `finance.cash_forecast_updated`, `data.kpi_report_published`, `data.forecast_updated` | Chief of Staff | KPI review by working day 8; variance response within 5 business days |
| SOP-EXECUTIVE-06 | Crisis declaration and command | `it_security.incident_detected`, `it_security.data_breach_confirmed`, `it_security.incident_resolved`, `legal.regulator_notification_filed`, `marketing.brand_incident_raised` | Chief Executive Officer | Declaration within 4 hours of trigger (FY2026) |
| SOP-EXECUTIVE-07 | Strategy refresh and pricing governance | `product.pricing_change_proposed`, `product.roadmap_published`, `legal.regulatory_change_noted` | Strategy and Transformation Lead | Pricing decision 5 business days; quarterly strategy review |
| SOP-EXECUTIVE-08 | Key-client and commercial escalation | `customer_success.churn_risk_flagged`, `customer_success.client_churned`, `finance.collections_escalated`, `sales.deal_won`, `sales.deal_lost`, `legal.client_dispute_raised`, `delivery.quality_issue_raised` | Chief Executive Officer | Sponsor contact within 3 business days (24 hours if critical) |
| SOP-EXECUTIVE-09 | Contract exception approval | `legal.contract_risk_flagged` | Chief Executive Officer | 2 business days |
| SOP-EXECUTIVE-10 | Governance, risk and assurance oversight | `legal.compliance_finding_raised`, `legal.ai_risk_review_completed`, `it_security.certification_status_updated`, `operations.continuity_test_completed`, `operations.process_improvement_proposed`, `data.agent_quality_report_published`, `delivery.capacity_forecast_updated`, `people.engagement_survey_completed` | Chief of Staff | Owner and due date assigned within 2 business days |

## SOP-EXECUTIVE-01: Deal approval (£500k or more)

**Owner**: Chief Executive Officer (Chief of Staff runs the decision desk).
**Trigger**: `sales.deal_approval_requested`. `sales.proposal_sent` is watched: a proposal of £500k or more with no approval request after 3 business days creates a chase task.
**Inputs**: `deal_id`, `client_id`, `client_name`, `amount_gbp` (total contract value), `tier`, `service_line`, optional `discount_pct`, `duration_months`, `gross_margin_pct`, `uncapped_liability`, `non_standard_terms`.

### Steps

1. [agent] Log receipt and start the SLA clock. Look up the delegation: below £500,000 no CEO approval is needed (decision `not_required`); £500,000 to £1,500,000 CEO; above £1,500,000 Board (`COMPANY.md §9.3`).
2. [agent] Compute client concentration: (existing contracted annual revenue for the client plus this deal annualised as `amount_gbp x 12 / duration_months`) divided by the planned revenue for the year (£6.0m, £19.5m, £46.2m; `COMPANY.md §5.1`). Above 15% is a block; above 10% is a Board notification (`COMPANY.md §8`, assumption 8).
3. [agent] Apply controls in order and collect reasons: discount above 15% declines (A7 in `economics.md`); discount above 10% adds the condition "Finance head concurrence" (`COMPANY.md §9.3`); stated gross margin below 35% declines (A8); uncapped liability or non-standard IP or data terms add the condition "General Counsel sign-off" (`COMPANY.md §9.3`).
4. [human] Chief of Staff reviews the draft decision, adds commercial context (pipeline, capacity from `delivery.capacity_forecast_updated`), and passes it to the CEO.
5. [human] CEO approves, approves with conditions, or declines. Decisions that pass every control may be pre-approved by the CEO as a standing rule so that the agent broadcasts them immediately.
6. [agent] For deals above £1,500,000: publish the decision `referred_to_board`, add the deal to the next Board agenda (or an ad hoc written consent, 5 working days), and publish the final decision `approved` or `declined` with `approver: "Board of Directors"` after ratification.
7. [agent] Record the decision, reasons and conditions in the decision log with the elapsed hours.

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.deal_decision_made` | `*` (Sales, Finance, Legal) | `deal_id`, `client_id`, `client_name`, `amount_gbp`, `decision` (`approved`, `approved_with_conditions`, `declined`, `referred_to_board`, `not_required`), `approver`, `conditions`, `reasons`, `concentration_pct`, `decided_day`, `board_ratified`, `summary` |

### SLA and controls

- Decision within 48 hours (FY2026), 36 hours (FY2027), 24 hours (FY2028).
- Maker-checker: the agent drafts, a human approves above the standing rule. The CEO never approves a deal she has personally negotiated without the Chief of Staff's control check.
- Evidence: control results are stored with the decision; quarterly sample of 10% reviewed by the Audit and Risk Committee chair.

### Exceptions and escalation

- CEO unavailable: Chair (Priya Raman) acts for deals up to £1.5m with the CFO's concurrence.
- Concentration above 10%: Board chair notified within 5 business days.
- A deal approved with conditions cannot move to `sales.deal_won` until Legal confirms the conditions are in the contract.

## SOP-EXECUTIVE-02: Board meetings and Board-level approvals

**Owner**: Chief of Staff (Board and Investor Relations Manager from FY2027).
**Trigger**: `external.board_request` (Board member, investor or Chair asks for a meeting, paper or decision); quarterly schedule (target 15 January, April, July and October).
**Inputs**: request `kind` (`strategy_review`, `ad_hoc_meeting`, `information_request`, `investor_update`), `requested_by`, `agenda`, `notice_days`, optional `strategy_change`.

### Steps

1. [agent] Classify the request. Quarterly meetings are scheduled from the calendar; ad hoc requests get a date at `notice_days` (default 7, 5 for written consent, 1 during a crisis).
2. [human] Chief of Staff agrees the agenda with the Chair and sets the papers owner: Finance for financials, Data for KPIs, Legal for governance and risk, Delivery and Sales for pipeline.
3. [agent] Draft the Board pack: KPI table (`kpis.md`), financials (`finance.month_end_closed`), cash runway (`finance.cash_forecast_updated`), pipeline and decisions log, risk register, OKR progress.
4. [human] CEO and Chief of Staff review; the pack is issued 5 working days before the meeting.
5. [human] Meeting is held with the five directors (Priya Raman, Imogen Hartley, Tomas Beckett, Adaeze Okafor, Marcus Ellery; `COMPANY.md §9.1`). The Board approves the annual budget, executive hires, deals above £1.5m and any change to the strategy.
6. [agent] Publish `executive.board_meeting_held` with decisions and actions. If the Board approved a strategy change, publish `executive.strategy_updated` with `board_approved: true`.
7. [human] Minutes are issued within 5 working days; actions are tracked weekly.

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.board_meeting_held` | `*` (Finance, Legal, Data) | `meeting_id`, `meeting_type`, `agenda`, `decisions`, `attendees`, `pack_issued_day`, `minutes_due_day`, `held_day`, `requested_by` |
| `executive.strategy_updated` | `*` (all departments) | `version`, `summary`, `changes`, `board_approved`, `effective_day` |

### SLA and controls

- Pack on time at 100% target (`board_pack_on_time_pct`).
- Conflicts: any director with an interest in an item (for example an investor director on a financing) is recorded and recused.
- Board decisions are recorded as resolutions; Legal keeps the minute book.

### Exceptions and escalation

- Quorum not achievable: use written resolution; Legal confirms validity under the articles.
- Request from an investor outside the Board: Chief of Staff answers within 5 business days; anything price-sensitive goes through the Chair.

## SOP-EXECUTIVE-03: Headcount approval and executive hiring

**Owner**: Chief Executive Officer (Chief of Staff validates in-plan requests).
**Trigger**: `people.requisition_opened` (from any department, via People), and `people.hire_requested` (People's own requests come straight to the executive).
**Inputs**: `requisition_id`, `department`, `role_title`, `level`, `replacement` (backfill flag), `in_budget`, `business_case`, `critical_role`.

### Steps

1. [agent] Check state: crisis active (non-critical roles are deferred), department hiring hold (set by SOP-EXECUTIVE-05), and cash runway below 12 months (deferred unless `critical_role`).
2. [agent] Test against the plan: headcount adds allowed this year = the department's year-end headcount for the year minus the prior year (`COMPANY.md §6.1`); approvals already given this year are counted. Backfills are always in plan.
3. [agent] Classify: in plan or backfill (basis `in_plan` or `backfill`); outside plan with a `business_case` (basis `business_case`, CEO decision, reported at the next Board); outside plan with no case (declined).
4. [human] Chief of Staff validates in-plan requests (2 business days). CEO decides outside-plan requests (5 business days). Roles of head level or in the Executive department are referred to the Board for approval (`COMPANY.md §9.1`).
5. [agent] Publish `executive.headcount_approved` for approvals. For refusals or deferrals, publish the same topic with `approved: false`, `decision: "declined"` and the `reason`, so People and Finance close the requisition.
6. [agent] For the executive department's own planned hires, emit `executive.hire_requested` after the budget is approved (SOP-EXECUTIVE-04).

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.headcount_approved` | `*` (People, Finance) | `requisition_id`, `department`, `role_title`, `approved`, `basis`, `approver`, `fiscal_year`, `conditions`, `decided_day` (refusals add `decision`, `reason`) |
| `executive.hire_requested` | `people` | `requisition_id`, `department`, `role_title`, `level`, `justification`, `target_start_day`, `salary_band_gbp` |

### SLA and controls

- 5 business days (3 in FY2028). Every approval cites the budget line; Finance reconciles approvals to the headcount plan (38, 110, 230 humans; `COMPANY.md §6`).
- Salary offer must sit in the band for the level (`COMPANY.md §6.2`); outside band needs the CEO and the Remuneration Committee.

### Exceptions and escalation

- Hiring freeze: declared by the CEO when runway falls below 12 months or a crisis is active; only `critical_role` requisitions proceed.
- Agents may not make final hiring decisions (`COMPANY.md §9.4`): this SOP approves headcount, not candidates.

## SOP-EXECUTIVE-04: Annual budget and OKR cycle

**Owner**: Chief Executive Officer.
**Trigger**: `finance.budget_cycle_opened` (Q4), `finance.budget_submitted` (Finance's own submission comes to the executive), `finance.budget_consolidated`.
**Inputs**: `fiscal_year`, `budget_id` (`BUD-2026` format), department submissions, consolidated total, envelope guidance from `COMPANY.md §5.4`.

### Steps

1. [human] Strategy and Transformation Lead publishes planning guidance: revenue and margin targets (`COMPANY.md §5.1`), headcount plan (`COMPANY.md §6.1`), priorities.
2. [agent] On `finance.budget_cycle_opened`, build and publish the executive department's submission: people (from `economics.md` Section 2), non-people lines, headcount and agents.
3. [agent] On `finance.budget_submitted` from Finance, record it and check it against its envelope.
4. [agent] On `finance.budget_consolidated`, compare the consolidated total to the envelope total (£7,500k, £17,800k, £39,000k; `COMPANY.md §5.4`). Within 2% above the envelope: approve. More than 2% above: approve at the envelope with `status: approved_with_reductions` and the reduction recorded.
5. [human] CEO reviews; Board approves the annual budget at the Q4 meeting (`COMPANY.md §9.1`).
6. [agent] Publish `executive.budget_approved` and `executive.okrs_set` for the new year. Publish `executive.hire_requested` for executive roles planned in the new year.
7. [agent] Clear department hiring holds raised in the prior year.

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.budget_submitted` | `finance` | `department`, `fiscal_year`, `people_gbp`, `non_people_gbp`, `total_gbp`, `headcount`, `agents` |
| `executive.budget_approved` | `*` (all) | `budget_id`, `fiscal_year`, `status`, `approved_total_gbp`, `by_department`, `reductions_gbp`, `conditions`, `decided_day` |
| `executive.okrs_set` | `*` (all) | `fiscal_year`, `objectives` (id, objective, key results), `owner`, `effective_day` |

### SLA and controls

- Own submission within 10 business days; approval within 10 business days of consolidation; budget in force by 1 January.
- Department totals must equal `COMPANY.md §5.4` within £5k or carry a written variance explanation.

### Exceptions and escalation

- Consolidated total above envelope by more than 5%: Board paper with options (reduce hiring, defer non-people spend).
- Missing department submission after 10 business days: CEO calls the department head; Finance proceeds with the prior-year baseline.

## SOP-EXECUTIVE-05: In-year performance and cash review

**Owner**: Chief of Staff (CEO for decisions).
**Trigger**: `finance.month_end_closed`, `finance.budget_variance_flagged`, `finance.cash_forecast_updated`, `data.kpi_report_published`, `data.forecast_updated`.
**Inputs**: `revenue_gbp`, `ytd_revenue_gbp`, `ebitda_gbp`, `gross_margin_pct`, `variance_pct`, `department`, `runway_months`, `kpis`, forecast `delta_pct`.

### Steps

1. [agent] Update KPI actuals (`revenue_gbp_m`, `ebitda_margin_pct`, `gross_margin_pct`, `cash_runway_months`, others from `data.kpi_report_published`).
2. [agent] Compare year-to-date revenue with the phased plan (plan x elapsed months / 12). More than 10% behind: create a re-forecast task (owner CFO, due in 5 business days). Three consecutive months behind: report to the Chair.
3. [agent] On a budget variance of 15% or more for a department: set a hiring hold for that department and create a task for the CFO and the department head. Lower variances are logged for the monthly review.
4. [agent] On a forecast revision of -10% or worse: create a task to rerun scenarios and bring options to the next weekly meeting.
5. [agent] On runway below 12 months: hiring freeze for non-critical roles. Below 6 months: declare a liquidity crisis (SOP-EXECUTIVE-06).
6. [human] Chief of Staff runs the monthly KPI review by working day 8 and records decisions.

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.crisis_declared` (liquidity only) | `*` | see SOP-EXECUTIVE-06 |
| Internal records | none | `executive.activity.kpi_updated`, `executive.activity.variance_review`, `executive.activity.forecast_review` log events |

### SLA and controls

- Monthly KPI review by working day 8; variance response within 5 business days.
- The CEO approves non-budgeted spend above £250,000; the CFO between £50,000 and £250,000 (`COMPANY.md §9.3`).

### Exceptions and escalation

- Two consecutive months of negative EBITDA worse than plan by more than £150k (10% of the FY2026 loss): Board chair informed.

## SOP-EXECUTIVE-06: Crisis declaration and command

**Owner**: Chief Executive Officer (commander); Chief of Staff (crisis secretary).
**Trigger**: `it_security.incident_detected` (severity `critical`), `it_security.data_breach_confirmed`, `legal.regulator_notification_filed`, `marketing.brand_incident_raised` (severity `critical`); stand-down on `it_security.incident_resolved`. Also called from SOP-EXECUTIVE-05 (liquidity) and SOP-EXECUTIVE-08 (key-client loss).
**Inputs**: `incident_id`, `severity`, `summary`, categories of data affected, `client_id`.

### Steps

1. [agent] Evaluate against the trigger table: critical security incident (declare); confirmed personal data breach (declare, starts the 72 hour ICO clock, `COMPANY.md §9.3`); regulator notification filed (declare if none active); critical brand incident (declare); loss of a client above 10% of revenue (declare); runway below 6 months (declare).
2. [agent] If not already declared for this `incident_id`, publish `executive.crisis_declared`, assign `crisis_id`, name the CEO as commander, set a daily review at 09:00 and draft a holding statement (the LLM draft is a proposal only).
3. [human] CEO confirms or stands down within 4 hours. General Counsel, CISO and CEO decide on ICO notification; only humans notify regulators (`COMPANY.md §9.4`).
4. [agent] Schedule an ad hoc Board call within 1 day for critical crises (`executive.board_meeting_held`, type `crisis`).
5. [agent] Hiring freeze for non-critical requisitions while the crisis is active.
6. [human] Daily crisis review: actions, client communications, Legal and CISO updates.
7. [agent] On `it_security.incident_resolved` for the same incident: stand down, log the duration, and create a post-incident review task due in 10 business days.

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.crisis_declared` | `*` (all departments) | `crisis_id`, `category`, `severity`, `trigger_topic`, `incident_id`, `summary`, `commander`, `war_room_cadence`, `next_review_day`, `declared_day`, `actions`, `briefing` |
| `executive.board_meeting_held` | `*` | meeting type `crisis`; see SOP-EXECUTIVE-02 |

### SLA and controls

- Declaration within 4 hours (FY2026), 2 hours thereafter (`crisis_declaration_hours`).
- Single commander; decisions logged with time stamps; no external statement without General Counsel review.

### Exceptions and escalation

- CEO unreachable: Chief of Staff declares on the CEO's standing instruction and informs the Chair.
- Multiple concurrent crises: the CEO appoints a second commander from the executive team.

## SOP-EXECUTIVE-07: Strategy refresh and pricing governance

**Owner**: Strategy and Transformation Lead.
**Trigger**: `product.pricing_change_proposed`, `product.roadmap_published`, `legal.regulatory_change_noted`; quarterly strategy review.
**Inputs**: `change_id`, `tier`, `service_line`, `old_price_gbp`, `new_price_gbp`, `margin_impact_pct`, `impact` (regulatory), roadmap items.

### Steps

1. [agent] For a pricing proposal, compute the change percentage against the list price in `COMPANY.md §3` and check Finance's margin input.
2. [agent] Approve changes of 15% or less in absolute terms with non-negative margin impact; effective date 30 days after approval. Larger or margin-negative changes are returned to the Product sponsor by a task (no topic is published) and go to the Board if the sponsor insists.
3. [human] Strategy and Transformation Lead reviews against competitive data and the discount policy (typical discount 10% or less, `COMPANY.md §3`).
4. [agent] Publish `executive.pricing_change_approved` for approvals (Finance, Sales, Marketing, Product update their systems).
5. [agent] For `product.roadmap_published` and `legal.regulatory_change_noted`: log, create a review task for the next quarterly strategy review; strategic regulatory impact is added to the Board agenda.
6. [human] Quarterly strategy review: confirm or revise the strategy. Any change to the strategy in `COMPANY.md` needs Board approval before `executive.strategy_updated` is published (SOP-EXECUTIVE-02).

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.pricing_change_approved` | `*` (Sales, Finance, Marketing, Product) | `change_id`, `tier`, `service_line`, `old_price_gbp`, `new_price_gbp`, `change_pct`, `effective_day`, `conditions` |
| `executive.strategy_updated` | `*` | see SOP-EXECUTIVE-02 |

### SLA and controls

- Pricing decisions in 5 business days; no price change takes effect on signed or proposed deals without Legal review.
- Keep annual uplift stays CPI + 2% (cap 7%; `COMPANY.md §7`); a change to this needs Board approval.

### Exceptions and escalation

- Disagreement between Product and Sales on price: CEO decides after a one-page scenario note from the Strategy Intelligence Agent.

## SOP-EXECUTIVE-08: Key-client and commercial escalation

**Owner**: Chief Executive Officer.
**Trigger**: `customer_success.churn_risk_flagged`, `customer_success.client_churned`, `finance.collections_escalated`, `sales.deal_won`, `sales.deal_lost`, `legal.client_dispute_raised`, `delivery.quality_issue_raised`.
**Inputs**: `client_id`, `client_name`, `annual_value_gbp` or `amount_gbp`, `severity`, `days_overdue`, `invoice_id`.

### Steps

1. [agent] `sales.deal_won`: update the client revenue ledger used for the concentration check; log the win. `sales.deal_lost` of £500k or more: create a loss-review task for the CRO (due 10 business days).
2. [agent] `customer_success.churn_risk_flagged` with annual value of £250,000 or more: create an executive-sponsor call task for the CEO due in 3 business days.
3. [agent] `customer_success.client_churned`: update the ledger; if the client was 10% or more of plan revenue, declare a crisis (SOP-EXECUTIVE-06); otherwise create a lessons-learned task.
4. [agent] `finance.collections_escalated` (day 45 on the ladder, `COMPANY.md §7`): create a CEO sponsor call task for amounts of £100,000 or more, due in 3 business days.
5. [agent] `legal.client_dispute_raised`: critical severity or amount of £500,000 or more creates a CEO task due in 24 hours and, for critical, a crisis assessment.
6. [agent] `delivery.quality_issue_raised`: high or critical severity creates an executive sponsor task; critical is due in 24 hours.
7. [human] CEO or the sponsor calls the client, agrees the recovery plan with the department head, and records the outcome.

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.crisis_declared` (key-client loss, critical dispute) | `*` | see SOP-EXECUTIVE-06 |
| Internal records | none | `executive.activity.client_ledger_updated`, `executive.activity.sponsor_task_created` |

### SLA and controls

- Sponsor contact within 3 business days, 24 hours if critical.
- Client ledger must reconcile to Finance billing monthly.

### Exceptions and escalation

- A dispute where the claim exceeds £1.5m is a Board matter and goes on the next agenda or an ad hoc meeting.

## SOP-EXECUTIVE-09: Contract exception approval

**Owner**: Chief Executive Officer (with General Counsel).
**Trigger**: `legal.contract_risk_flagged`.
**Inputs**: `contract_id`, `deal_id`, `risk_level` (`low`, `medium`, `high`, `critical`), `issue`, optional `mitigation`, `amount_gbp`, `client_id`.

### Steps

1. [agent] Log the flag and the contract exception category (uncapped liability, non-standard IP, non-standard data terms, other).
2. [agent] Low and medium risk: no CEO decision needed, note on the deal record. High or critical with a stated mitigation: draft `approved_with_conditions`. High or critical without mitigation: draft `declined` (renegotiate).
3. [human] General Counsel and CEO jointly decide (`COMPANY.md §9.3`: uncapped liability or non-standard IP or data terms need both).
4. [agent] Publish `executive.deal_decision_made` with the exception decision so that Sales, Finance and Legal hold the same record.

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| `executive.deal_decision_made` | `*` | `deal_id`, `contract_id`, `decision`, `approver`, `conditions`, `reasons`, `exception: true`, `decided_day` |

### SLA and controls

- 2 business days. Signing remains a human act of an authorised signatory; agents never sign (`COMPANY.md §9.4`).

### Exceptions and escalation

- Exception on a deal above £1.5m: Board approval required; handled under SOP-EXECUTIVE-01 step 6.

## SOP-EXECUTIVE-10: Governance, risk and assurance oversight

**Owner**: Chief of Staff.
**Trigger**: `legal.compliance_finding_raised`, `legal.ai_risk_review_completed`, `it_security.certification_status_updated`, `operations.continuity_test_completed`, `operations.process_improvement_proposed`, `data.agent_quality_report_published`, `delivery.capacity_forecast_updated`, `people.engagement_survey_completed`.
**Inputs**: `severity`, `finding_id`, `outcome`, `certification`, `status`, `result`, `estimated_cost_gbp`, `shortfall_fte`, `utilisation_pct`, `engagement_score`, `quality_score`.

### Steps

1. [agent] Compliance finding: high or critical creates a task for the COO with a due date of 5 business days; log all findings for the Audit and Risk Committee.
2. [agent] AI risk review outcome `rejected` or `approved_with_conditions`: log and create a follow-up task for the Chief Product Officer; both reported to the Board AI governance item.
3. [agent] Certification: ISO 27001 `achieved` marks the US launch gate item as met; `lapsed` or `suspended` creates a CEO task (US launch gate needs ISO 27001, SOC 2 Type II in FY2027, `COMPANY.md §8`).
4. [agent] Continuity test `failed`: task for the COO due in 10 business days. Process improvement: if cost is above £250,000 the CEO decides; £50,000 to £250,000 the CFO; below that the proposer's head (`COMPANY.md §9.3`).
5. [agent] Agent quality report below 85 or with open critical issues: task for the Chief Data and AI Officer.
6. [agent] Capacity forecast with a shortfall of 3 FTE or more, or utilisation above 85% (target 70%, `COMPANY.md §4`): task to prioritise related requisitions in SOP-EXECUTIVE-03.
7. [agent] Engagement score below 60: leadership action-plan task for the Chief People Officer, due in 10 business days.
8. [human] Chief of Staff reviews all open governance tasks weekly.

### Outputs and messages

| Topic | Recipient | Body keys |
|---|---|---|
| Internal records | none | `executive.activity.governance_review`, `executive.activity.certification_status`, tasks owned by the named heads |

### SLA and controls

- Owner and due date assigned within 2 business days; overdue governance tasks are reported on the Board risk register.

### Exceptions and escalation

- Repeat finding (same area twice in 12 months): referred to the Audit and Risk Committee chair, Marcus Ellery.
