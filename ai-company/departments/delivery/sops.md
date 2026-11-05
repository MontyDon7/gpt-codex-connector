# Delivery Standard Operating Procedures

These SOPs govern the `delivery` department of Lumenhall Partners (client delivery and consulting: scoping, staffing humans and AI agents, engagements, milestones, scope changes, quality). Department head: Oliver Thackeray, Managing Partner, Delivery (COMPANY.md §9.2). The department agent class is `DeliveryAgent`. Price points, rate card, billing terms and delegations are quoted from COMPANY.md §3, §3.5, §7 and §9.3; the quality gate and pyramid are from COMPANY.md §4; agent limits are from COMPANY.md §9.4. Lifecycle topic names follow CONVENTIONS.md §7. Sim time is an integer `due_day`; real-world SLAs are in business days (BD) unless stated.

Role shorthand used below: **MP** = Managing Partner, Delivery (Thackeray); **Principal** = engagement principal/sponsor lead; **EM** = Engagement Manager (manager level); **SC** = Senior Consultant; **Delivery Ops Lead** = staffing, resource and utilisation owner; **QA Lead** = delivery quality owner (manager level or above, human); **Agent** = `DeliveryAgent` and its sub-agents (research, analysis, drafting, QA-check and monitoring digital colleagues), each with a named human owner (COMPANY.md §9.4).

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-DELIVERY-01 | Proposal scoping and estimation | `sales.proposal_requested` | Principal (agent drafts) | Scoping pack back to Sales in 3 BD (Spark/Pilot), 5 BD (Sprint/Build), 8 BD (Programme/Scale) |
| SOP-DELIVERY-02 | Lead pre-shaping and demand signal | `sales.lead_qualified`, `data.forecast_updated` | Delivery Ops Lead | Capacity note within 2 BD of lead; forecast reconciled within 2 BD of data refresh |
| SOP-DELIVERY-03 | Staffing an engagement | `sales.deal_won` | Delivery Ops Lead | Staffing request raised within 1 BD of deal won; named team within 5 BD |
| SOP-DELIVERY-04 | Engagement kickoff | `legal.contract_signed`, `finance.billing_schedule_created` | Engagement Manager | Kickoff within 10 BD of signature, only after both triggers received |
| SOP-DELIVERY-05 | Milestone delivery, QA gate and acceptance | Weekly engagement review (Monday) and milestone due date | Engagement Manager | Deliverable QA'd 2 BD before client release; `delivery.milestone_reached` within 1 BD of written acceptance |
| SOP-DELIVERY-06 | Scope change and change orders | `external.client_scope_request` | Engagement Manager (Principal approves) | Impact assessment in 2 BD; change order issued in 3 BD; no work before signature |
| SOP-DELIVERY-07 | Quality monitoring and issue management | `data.agent_quality_report_published`, `customer_success.support_escalated`, `customer_success.feedback_received` | QA Lead | Triage in 4 working hours (high/critical), 1 BD (medium/low); critical fix plan in 1 BD |
| SOP-DELIVERY-08 | Engagement close-out and handover to Keep | Final acceptance milestone; `customer_success.renewal_confirmed` | Engagement Manager | Close-out pack in 5 BD; `delivery.engagement_completed` in 2 BD of close-out sign-off |
| SOP-DELIVERY-09 | Weekly capacity forecast and hiring trigger | Weekly (Friday 12:00); `people.new_hire_started`, `people.engagement_survey_completed` | Delivery Ops Lead | Forecast published every Friday; hire request within 2 BD of a red threshold |
| SOP-DELIVERY-10 | Client risk, churn and dispute response | `customer_success.churn_risk_flagged`, `customer_success.health_score_updated`, `legal.client_dispute_raised` | Principal (MP for disputes) | Risk huddle in 2 BD (churn flag), 1 BD (dispute); action plan in 3 BD |
| SOP-DELIVERY-11 | AI agent and platform capability adoption | `product.agent_capability_added`, `product.release_shipped`, `product.roadmap_published`, `data.benchmark_ready` | AI Delivery Lead | Impact review in 5 BD; engagement agent changes only after AI risk review where material |
| SOP-DELIVERY-12 | Security incident on a client engagement | `it_security.incident_detected` | Engagement Manager (MP informed for high/critical) | Acknowledge in 1 hour (critical), 4 hours (high); client holding statement drafted in 4 hours |
| SOP-DELIVERY-13 | Annual budget, OKRs and strategy alignment | `finance.budget_cycle_opened`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated`, `executive.crisis_declared` | Managing Partner, Delivery | Budget submission by cycle deadline (target 10 BD after open); OKR cascade in 10 BD of `executive.okrs_set`; crisis posture in 1 BD |

## SOP-DELIVERY-01: Proposal scoping and estimation

**Owner**: Principal on the opportunity (Manager for Spark/Pilot); drafting by the Agent. Approver of price floor: MP.
**Trigger**: `sales.proposal_requested`.
**Inputs**: `deal_id`, `client_id`, `client_name`, `service_line`, `tier` (as requested), `summary` of the client problem, requested `due_day`; discovery notes from the qualified lead; client systems landscape; any RFP text.

### Steps
1. [agent] Parse the request, create a scoping workspace keyed by `deal_id`, and pull comparable closed engagements (same tier, sector, systems) from the engagement library, with actual vs planned effort.
2. [agent] Draft the effort model: work breakdown by phase, days by level (Partner, Principal, Manager, Senior Consultant, Consultant, Analyst) and agent-days, against the tier envelope (for example Forge Build: 1 Principal part-time, 1 Manager, 2 Senior Consultants, 1 Consultant and 3 to 5 AI agents; COMPANY.md §4).
3. [human] Principal runs a 45-minute scoping call with the client sponsor to confirm outcomes, in-scope and out-of-scope systems, data access, client-side dependencies and acceptance criteria.
4. [human] Principal selects the tier (COMPANY.md §3.1 to §3.3) and agrees assumptions. Any scope that does not fit a published tier is built as a tier plus an explicit change-order allowance priced at rate card (COMPANY.md §3.5); never a bespoke fixed fee.
5. [agent] Compute cost-to-deliver and margin: loaded day costs, agent-day cost, subcontractor need, T&E (expenses capped at 5% of fee, COMPANY.md §7). Flag if projected engagement gross margin is below the 48% FY2026 company floor (58% FY2027, 64% FY2028; COMPANY.md §5.1).
6. [human] Manager peer-reviews the estimate; MP signs off any estimate where margin is below the floor, the delivery span exceeds the tier's standard duration by more than 20%, or an unproven agent capability is assumed.
7. [agent] Identify delivery risks (data readiness, integration access, sponsor availability, regulated data) and record the staffing profile and earliest start date by checking the capacity forecast (SOP-DELIVERY-09).
8. [human] Principal approves the scoping pack, then the Agent publishes it.

### Outputs and messages
- `delivery.scoping_completed` (recipients: sales, finance): body keys `deal_id`, `client_id`, `client_name`, `service_line`, `tier`, `amount_gbp` (recommended list price), `duration_weeks`, `effort_days`, `agent_days`, `est_margin_pct`, `earliest_start_day`, `risks` (list), `summary`, `due_day`.
- If the request exceeds the tier envelope and needs senior staff not available within 45 days: also `delivery.hire_requested` (see SOP-DELIVERY-09).

### SLA and controls
- Back to Sales in 3 BD for Spark/Pilot, 5 BD for Sprint/Build, 8 BD for Programme/Scale.
- Four-eyes: no scoping pack leaves delivery without human Principal approval (COMPANY.md §4 quality gate applies to anything client-facing).
- Estimates are recorded with a version; actual-vs-estimate variance is reviewed at close-out (SOP-DELIVERY-08) and feeds the estimating model.
- Prices come only from COMPANY.md §3; discounting is a Sales decision under COMPANY.md §9.3, never delivery's.

### Exceptions and escalation
- Deal total contract value expected at or above £500k: MP informs the CEO before the pack is released (CEO approves via the sales deal approval path, COMPANY.md §9.3).
- Client demands fixed-price outcome guarantees or uncapped liability: stop and route to Legal via Sales; do not scope around it.
- Scoping not complete by the SLA: Delivery Ops Lead tells the Sales head with a revised date; two consecutive misses go to the MP.

## SOP-DELIVERY-02: Lead pre-shaping and demand signal

**Owner**: Delivery Ops Lead.
**Trigger**: `sales.lead_qualified`; also `data.forecast_updated`.
**Inputs**: `lead_id`, `client_name`, `service_line`, indicative `tier`, qualification notes; the latest pipeline forecast from Data (probability-weighted proposals and wins by service line).

### Steps
1. [agent] Log the qualified lead as a probability-weighted demand line (qualification to proposal 50%, proposal to win 30%; COMPANY.md §5.3) against the capacity model by service line and week.
2. [agent] On `data.forecast_updated`, re-run the demand-versus-capacity view for the next 26 weeks and highlight weeks where weighted demand exceeds 90% of bookable capacity.
3. [human] Delivery Ops Lead reviews the highlights weekly with the MP; where a sector-specific lead needs a domain specialist not on the bench, flags it to the assigned Principal early.
4. [human] Principal optionally offers a 30-minute pre-sales technical call on request from Sales; the call is non-billable and capped at one per lead.
5. [agent] Update the capacity model and queue the numbers for the Friday forecast (SOP-DELIVERY-09).

### Outputs and messages
- No direct emission; feeds `delivery.capacity_forecast_updated` (SOP-DELIVERY-09), keys `service_line`, `weighted_demand_days`.
- Advice to Sales is sent as an internal task note on the lead, not a bus topic.

### SLA and controls
- Capacity note within 2 BD of `sales.lead_qualified`; forecast reconciled within 2 BD of `data.forecast_updated`.
- Control: demand is only recorded at probability-weighted values; unweighted pipeline never drives hiring.

### Exceptions and escalation
- Weighted demand exceeds bookable capacity in more than 4 consecutive weeks: escalate to the MP for a hiring or subcontractor decision under SOP-DELIVERY-09.

## SOP-DELIVERY-03: Staffing an engagement

**Owner**: Delivery Ops Lead; approver: Principal and MP (for Partner/Principal allocation).
**Trigger**: `sales.deal_won`.
**Inputs**: `deal_id`, `client_id`, `client_name`, `service_line`, `tier`, `amount_gbp`, win notes; the approved scoping pack from SOP-DELIVERY-01; capacity forecast; skills matrix; client conflicts list.

### Steps
1. [agent] Create the engagement record `EN-nnnn` linked to `deal_id` and `client_id`, with status `pending_contract`, and copy the scoping pack (team profile, days, risks).
2. [agent] Propose a staffing plan by role and named person, matching skills (sector, systems, regulated-data clearance), availability (target utilisation 70% blended; Analyst/Consultant 80%, Manager 65%, Principal 50%, Partner 35%; COMPANY.md §4) and pyramid balance (Partner 5%, Principal 10%, Manager 20%, Senior Consultant 30%, Consultant 25%, Analyst 10%).
3. [agent] Propose the agent team: research, analysis, drafting, QA-check and monitoring agents (3 to 5 for Forge Build), each with an accountable human owner from the engagement team; confirm agent provisioning lead time of 5 days (COMPANY.md §8).
4. [human] Delivery Ops Lead checks conflicts (no one staffed on a direct competitor engagement within the confidentiality window), leave, and that no person exceeds 100% allocation across engagements.
5. [human] Principal and MP confirm the plan. Any person allocated above 90% for more than 4 weeks needs MP approval.
6. [human] Delivery Ops Lead raises the request to People and Operations for the roles or equipment that are not already on the bench: contractor engagement, laptops, client-site access (see below). Gaps that cannot be filled in 45 days (COMPANY.md §8) trigger SOP-DELIVERY-09 hiring.
7. [agent] Publish the staffing request and reserve the allocations in the resource tool with a soft hold until contract signature (SOP-DELIVERY-04).

### Outputs and messages
- `delivery.staffing_requested` (recipients: people, operations): body keys `engagement_id`, `client_id`, `client_name`, `service_line`, `tier`, `roles` (list of `{level, count, start_day}`), `agent_count`, `start_day`, `needs_contractors` (bool), `due_day`.
- `delivery.hire_requested` when a permanent role gap exists: `department` = `delivery`, `role`, `level`, `count`, `reason`, `due_day` (see SOP-DELIVERY-09).

### SLA and controls
- Staffing request raised within 1 BD of `sales.deal_won`; named team within 5 BD; hard allocation only after `legal.contract_signed`.
- Controls: conflicts check, allocation cap, pyramid check, named human owner for every agent (COMPANY.md §9.4), no engagement starts with a Principal or Manager unnamed.

### Exceptions and escalation
- Required seniority unavailable: MP decides between delaying start (agree with client via Sales), subcontractor/associate (COMPANY.md §5.2 line), or reallocating from a lower-priority engagement.
- Subcontractors need a signed NDA and a completed vendor check before client access (Legal, Operations, IT Security).

## SOP-DELIVERY-04: Engagement kickoff

**Owner**: Engagement Manager; sponsor: Principal.
**Trigger**: `legal.contract_signed` and `finance.billing_schedule_created` (both required; either alone only updates engagement state); `people.new_hire_started` marks a new joiner available for allocation.
**Inputs**: `contract_id`, `engagement_id`, `client_id`, `amount_gbp`, signature date, billing schedule (30% on signature, 40% at mid-point milestone, 30% on acceptance for fixed-fee work; COMPANY.md §7), approved staffing plan, scoping pack.

### Steps
1. [agent] On `legal.contract_signed`, set the engagement to `contract_signed` and attach contract terms that affect delivery: IP, data protection, acceptance criteria, liability cap, security schedule, key-person clause.
2. [agent] On `finance.billing_schedule_created`, map billing milestones to delivery milestones and verify the mid-point and acceptance milestones exist in the plan with dates; flag a mismatch to the Engagement Manager.
3. [human] Engagement Manager confirms the project plan: milestones (with `due_day`), RAID log, governance (weekly status, fortnightly steering with the sponsor), and client dependencies with dates.
4. [human] Delivery Ops Lead converts soft holds into hard allocations; any new joiner announced by `people.new_hire_started` is added to the bench with access-ready status once IT Security and Operations confirm provisioning.
5. [human] Principal and EM hold the client kickoff meeting; confirm sponsor, working team, data access requests, and the agent register entries (agent name, owner, systems touched, data classes).
6. [agent] Create the engagement workspace (documents, risk log, agent logging for audit under COMPANY.md §9.4), and generate the first two-week plan and the standing weekly report template.
7. [human] EM confirms client data access has been approved by the client DPO or equivalent, and that agents have least-privilege access only.

### Outputs and messages
- `delivery.engagement_kickoff` (recipients: customer_success, finance, operations, data): body keys `engagement_id`, `client_id`, `client_name`, `contract_id`, `service_line`, `tier`, `amount_gbp`, `start_day`, `end_day`, `milestones` (list of `{name, due_day, billing_pct}`), `team` (list), `agent_count`, `summary`.

### SLA and controls
- Kickoff within 10 BD of signature; no billable work is logged before signature (change orders are signed before work starts, COMPANY.md §7).
- Control: kickoff is blocked until both contract and billing-schedule events are recorded; milestones in the plan must reconcile to the billing schedule 1:1.

### Exceptions and escalation
- Billing schedule not received within 3 BD of signature: EM chases the Finance contact; at 5 BD, MP raises with the CFO.
- Client unable to provide data access by the planned start: log as a client-dependency RAID item and agree a revised start in writing; the fixed fee stands, but extra days caused by client delay are chargeable at rate card as a change order (SOP-DELIVERY-06).

## SOP-DELIVERY-05: Milestone delivery, QA gate and acceptance

**Owner**: Engagement Manager; reviewer: Manager or above independent of the author; acceptor: client sponsor.
**Trigger**: Weekly engagement review (Monday 10:00) and each milestone `due_day`.
**Inputs**: engagement plan, deliverable drafts, agent outputs with run logs, acceptance criteria from the contract, weekly status data.

### Steps
1. [agent] Each Monday, compute plan health per engagement: percent complete versus plan, days burned versus budget, open RAID items, and agent run-success rate. Rate engagements green, amber (more than 10% days overrun on plan) or red (more than 20% or a milestone slipping beyond 5 BD).
2. [human] EM reviews the Agent's health report, corrects it, and reports to the Principal; amber/red items get a recovery plan within 2 BD.
3. [agent] Draft the milestone deliverable (analysis, model, documentation, agent configuration notes) and run the automated QA checks: source traceability, numerical reconciliation, template compliance, PII and confidentiality scan, and consistency against prior deliverables.
4. [human] Author self-reviews; a human Manager or above (never the author) completes the quality gate review of every client deliverable before release (COMPANY.md §4). Agent outputs used in client deliverables are logged for audit (COMPANY.md §9.4).
5. [human] Principal signs off milestones that carry billing triggers or executive-level content.
6. [human] EM presents the deliverable to the client sponsor and obtains written acceptance against the contractual acceptance criteria (email or signed acceptance form).
7. [agent] On acceptance, record the date, update percent-complete (fixed fee recognised on percentage-of-completion, COMPANY.md §7), and publish the milestone event so Finance can invoice within 2 BD of acceptance.

### Outputs and messages
- `delivery.milestone_reached` (recipients: finance, customer_success): body keys `engagement_id`, `client_id`, `milestone` (name), `milestone_no`, `billing_pct` (30, 40 or 30 for fixed-fee), `amount_gbp` (billable portion), `accepted_day`, `pct_complete`, `status` (`green`|`amber`|`red`).
- On a failed gate or client rejection: `delivery.quality_issue_raised` (see SOP-DELIVERY-07).

### SLA and controls
- Deliverable passes the Manager review at least 2 BD before client release; milestone event published within 1 BD of written acceptance so the invoice is issued within the 2-business-day target (COMPANY.md §7).
- Controls: no client release without human QA; no milestone event without written acceptance on file; agent cannot mark acceptance. Mid-point milestone (the 40% billing trigger) needs Principal sign-off.

### Exceptions and escalation
- Client does not respond within 5 BD of delivery: EM escalates to the sponsor and records "deemed acceptance" only where the contract allows it, with Legal confirming.
- Milestone slips more than 5 BD: Principal informs the client sponsor and Sales/Customer Success via the status report; MP informed at 10 BD.

## SOP-DELIVERY-06: Scope change and change orders

**Owner**: Engagement Manager; approver: Principal (up to £25,000), MP (above £25,000 or any change moving the end date by more than 4 weeks).
**Trigger**: `external.client_scope_request`.
**Inputs**: `engagement_id` or `client_id`, client request text, current plan, remaining budget and contingency, rate card (COMPANY.md §3.5).

### Steps
1. [agent] Classify the request: clarification, in-scope refinement, change to the deliverable set, or new work; match against contract scope clauses and acceptance criteria.
2. [agent] Draft the impact assessment: additional effort by level and agent-days, effect on milestones, dependencies, risk, and price at rate card (Partner £2,400, Principal £1,800, Manager £1,400, Senior Consultant £1,050, Consultant £800, Analyst £550, AI agent-day £350).
3. [human] EM validates the assessment and discusses it with the client sponsor; decides whether to absorb it (goodwill, capped at 3 person-days per engagement without Principal approval) or to charge it.
4. [human] Principal approves the commercial position. Where the change introduces new IP, data, or regulated processing, Legal reviews the wording.
5. [agent] Issue the change-order draft to Sales, Finance and Legal for review; Finance sets the billing, Legal papers it.
6. [human] The client signs the change order before any extra work starts (COMPANY.md §7).
7. [agent] Update the plan, budget and milestones, and the engagement's end date and amount.

### Outputs and messages
- `delivery.scope_change_requested` (recipients: sales, finance, legal): body keys `engagement_id`, `client_id`, `client_name`, `change_ref`, `amount_gbp` (change-order value at rate card), `effort_days`, `agent_days`, `schedule_impact_days`, `summary`, `due_day`.

### SLA and controls
- Impact assessment in 2 BD; change order issued in 3 BD; work on the change does not start before client signature; changes above £25,000 are reported in the weekly MP review.
- Control: change-order value always computed from the rate card; discounting on change orders follows COMPANY.md §9.3 (Sales head up to 10%).

### Exceptions and escalation
- Client instructs work verbally: EM confirms in writing within 1 BD; if the client declines to sign, the work stops and the EM informs the Principal; repeated scope creep over 15% of fee is flagged to Customer Success and Sales.
- Disputed change: hand to Legal (SOP-DELIVERY-10).

## SOP-DELIVERY-07: Quality monitoring and issue management

**Owner**: QA Lead (human, manager level or above); remediation owner: Engagement Manager.
**Trigger**: `data.agent_quality_report_published`; `customer_success.support_escalated`; `customer_success.feedback_received`.
**Inputs**: agent quality report (accuracy, hallucination rate, task success, latency, drift) per engagement/agent; client support escalations; client feedback (CSAT, NPS comments); QA gate findings.

### Steps
1. [agent] Ingest each trigger and map it to an engagement and, where relevant, a specific delivered agent or deliverable.
2. [agent] Score severity: `critical` (client data exposure, wrong output used in a decision or regulatory filing, or agent in production causing client financial impact), `high` (SLA breach on a Keep agent, a milestone-blocking defect, or a CSAT of 2 or lower), `medium` (defect with workaround), `low` (cosmetic or enhancement).
3. [human] QA Lead confirms severity, assigns the Engagement Manager as owner and (for agent defects) the accountable agent owner.
4. [human] EM contacts the client within 4 working hours for high/critical and agrees a containment step (for example, pausing an agent or reverting to a manual process).
5. [agent] Run root-cause assistance: compare configuration changes, data drift, prompt or model changes and logs; propose a fix and regression tests.
6. [human] QA Lead approves the fix; a Manager or above re-reviews any corrected deliverable before re-release (COMPANY.md §4). Material changes to client-facing agents require the AI risk review (`product.ai_risk_review_requested` then `legal.ai_risk_review_completed`; COMPANY.md §9.4).
7. [agent] Record the issue, cause, time to resolve, and any credit or concession agreed; feed lessons to the engagement library and the quality KPIs.

### Outputs and messages
- `delivery.quality_issue_raised` (recipients: customer_success, executive): body keys `engagement_id`, `client_id`, `client_name`, `severity`, `issue_type` (`agent_accuracy`|`deliverable_defect`|`sla_breach`|`client_complaint`), `summary`, `owner`, `fix_due_day`, `client_notified` (bool).

### SLA and controls
- Triage within 4 working hours for high/critical; 1 BD for medium/low; critical fix plan in 1 BD; high fix in 5 BD; medium in 10 BD. Every quality event is logged regardless of severity.
- Controls: agent defects require a named human owner; a client-facing fix is never auto-released; two high issues on one engagement in 30 days trigger a Principal-led recovery review.

### Exceptions and escalation
- Critical issues are also notified to the MP immediately and, where personal data may be involved, to IT Security and Legal (see SOP-DELIVERY-12); regulator notification is never made by delivery or an agent (COMPANY.md §9.4).
- Dispute over fault or fees: SOP-DELIVERY-10.

## SOP-DELIVERY-08: Engagement close-out and handover to Keep

**Owner**: Engagement Manager; sponsor: Principal; Keep handover: Customer Success manager.
**Trigger**: final acceptance milestone reached; also `customer_success.renewal_confirmed` (a Keep retainer or renewal starting, which requires a delivery handover or capacity reservation).
**Inputs**: final acceptance, outstanding RAID items, actual days and agent-days, margin actuals, client satisfaction score, agent register entries, runbooks.

### Steps
1. [human] EM completes the close-out checklist: all milestones accepted, change orders signed and billed, open defects resolved or contractually accepted, client data returned or deleted per contract, access revoked.
2. [agent] Compile the delivery actuals: effort versus estimate by phase, margin versus the scoping estimate, utilisation, agent-run costs, lessons learned.
3. [human] Principal reviews the actuals and variance; the Delivery Ops Lead updates the estimating benchmarks.
4. [human] For Forge engagements that move to Keep (target: a Keep retainer attached to every Forge Build/Scale; COMPANY.md §2): the EM produces the runbook, monitoring dashboards, support-day plan and agent register transfer with Customer Success; agents transferred to Keep retain a named human owner.
5. [human] On `customer_success.renewal_confirmed`, Delivery Ops Lead reserves recurring capacity for the Keep scope (support days: Essential 5, Plus 15 per quarter; COMPANY.md §3.3) and, for Keep Enterprise, an embedded team.
6. [human] Principal and Sales agree the next-step recommendation (for example Compass Spark to Forge Pilot) and log it for the client's Customer Success manager.
7. [agent] Update the engagement status to `completed`, release team allocations and publish the completion event.

### Outputs and messages
- `delivery.engagement_completed` (recipients: finance, customer_success, sales, data): body keys `engagement_id`, `client_id`, `client_name`, `service_line`, `tier`, `amount_gbp` (final billed value), `actual_days`, `planned_days`, `margin_pct`, `csat` (1 to 5), `handover_to_keep` (bool), `next_step_recommendation`.

### SLA and controls
- Close-out pack in 5 BD from final acceptance; `delivery.engagement_completed` within 2 BD of close-out sign-off, so Finance can release the final 30% invoice within 2 BD of acceptance (COMPANY.md §7).
- Controls: close-out cannot complete with unbilled change orders or unrevoked access; margin actuals are reconciled to Finance within the month.

### Exceptions and escalation
- Client has not signed final acceptance: escalate to the sponsor, then to the Managing Partner and Legal after 10 BD; revenue recognition follows percentage-of-completion only for accepted work (COMPANY.md §7).
- Engagement margin below 30% of plan: MP reviews root cause and decides a corrective action for the estimating model.

## SOP-DELIVERY-09: Weekly capacity forecast and hiring trigger

**Owner**: Delivery Ops Lead; approver: MP; hiring approval: CEO for headcount outside budget (COMPANY.md §9.3).
**Trigger**: weekly schedule (Friday 12:00); `people.new_hire_started` (new capacity), `people.engagement_survey_completed` (retention and burnout signal), and `data.forecast_updated` (demand input from SOP-DELIVERY-02).
**Inputs**: resource tool allocations, weighted pipeline demand, leave calendar, attrition forecast (14% in Y1 easing to 11% in Y3; COMPANY.md §8), time-to-hire of 45 days, survey results by team.

### Steps
1. [agent] Compute bookable capacity per level for the next 13 and 26 weeks, subtracting leave, training, bench and non-billable duties; compute utilisation versus the 70% blended target and by level.
2. [agent] Compare against committed engagements and probability-weighted demand; produce the coverage ratio (bookable days divided by demand days) per level and service line.
3. [agent] Set the signal: green (coverage 1.0 to 1.15), amber (0.9 to 1.0 or above 1.15), red (below 0.9 for 4 or more consecutive weeks).
4. [human] Delivery Ops Lead reviews and adjusts for known context (a client delaying a start, a key person leaving), and reviews survey sub-scores: a team with an engagement score drop of 10 points or more gets a manager conversation within 5 BD.
5. [human] MP decides actions: reallocate, subcontract (Subcontractors line, COMPANY.md §5.2), pause new starts, or raise a hiring request where the red persists. Hiring respects the pyramid (COMPANY.md §4) and the budget (SOP-DELIVERY-13).
6. [agent] Raise the hiring request with role, level, count, start target and justification; add new hires to the bench schedule on `people.new_hire_started` with a ramp assumption (50% billable in month 1, 80% in month 2, 100% in month 3).
7. [agent] Publish the forecast to Sales, People, Executive and Finance.

### Outputs and messages
- `delivery.capacity_forecast_updated` (recipients: sales, people, executive, finance): body keys `week_start_day`, `horizon_weeks`, `utilisation_pct`, `bookable_days` (by level), `demand_days`, `coverage_ratio`, `signal` (`green`|`amber`|`red`), `earliest_new_start_day`, `summary`.
- `delivery.hire_requested` (recipient: people): body keys `department` = `delivery`, `role`, `level`, `count`, `reason`, `due_day`, `budgeted` (bool), `agent_count_to_provision` (optional).

### SLA and controls
- Forecast published every Friday; hire request within 2 BD of a red signal confirmed by MP; unbudgeted headcount needs CEO approval before requisition opens (`executive.headcount_approved`).
- Controls: forecast always uses probability-weighted demand; no individual shown above 100% allocation; agent provisioning requests (5-day lead time) go with each human hiring request at the 0.5 agent-per-human ratio (COMPANY.md §2).

### Exceptions and escalation
- Utilisation below 60% for 4 weeks: MP reviews pipeline and Sales pace; consider redeploying to internal delivery projects (methods, agent build).
- Utilisation above 85% for 6 weeks or a team survey burnout flag: MP freezes new engagement starts for that team and escalates to People.

## SOP-DELIVERY-10: Client risk, churn and dispute response

**Owner**: Principal of record for the client (MP for disputes and any client above 10% of revenue); partners: Customer Success, Legal.
**Trigger**: `customer_success.churn_risk_flagged`; `customer_success.health_score_updated`; `legal.client_dispute_raised`.
**Inputs**: health score and drivers, churn risk reason, open engagements and Keep agents for the client, quality issue log, financial position (invoices outstanding), contract and dispute notice.

### Steps
1. [agent] Build a client risk brief: engagement status, milestone slippage, open quality issues (SOP-DELIVERY-07), recent scope changes, sponsor changes, delivery team stability and Keep SLA performance.
2. [human] For a churn flag or a health score below 60, the Principal and EM hold a risk huddle with the Customer Success manager within 2 BD to agree root cause and owner.
3. [human] For `legal.client_dispute_raised`, the MP and Legal agree in 1 BD that delivery will not communicate with the client on disputed matters other than through the agreed channel; EM compiles a factual chronology (plans, acceptances, change orders, defects, communications) within 3 BD.
4. [agent] Draft the recovery or response plan options (additional senior time, re-baselined plan, agent remediation) with cost and margin impact; no concessions drafted as commitments.
5. [human] Principal decides the remedial action within the limits set by COMPANY.md §9.3 (any discount above 10% or non-standard terms go to the Finance head and CEO). Goodwill days are capped at 3 person-days per engagement without Principal approval (same cap as SOP-DELIVERY-06).
6. [human] EM runs the action plan with weekly checkpoints; Customer Success tracks the health score; the Agent updates the capacity impact.
7. [agent] Record outcome and lessons; if the client is lost, trigger close-out of live work under SOP-DELIVERY-08.

### Outputs and messages
- `delivery.quality_issue_raised` when risk is driven by a delivery defect (body per SOP-DELIVERY-07).
- `delivery.capacity_forecast_updated` if the plan materially changes staffing (body per SOP-DELIVERY-09).
- `delivery.scope_change_requested` if the resolution involves a change order or credit (body per SOP-DELIVERY-06).

### SLA and controls
- Risk huddle in 2 BD (churn flag), 1 BD (dispute); action plan within 3 BD; weekly checkpoint until health score recovers above 70 for 4 weeks.
- Controls: delivery staff never admit liability or discuss settlement without Legal; no client communication on a disputed matter by an agent.

### Exceptions and escalation
- Dispute involving potential damages or an uncapped liability clause: General Counsel and CEO decide (COMPANY.md §9.3).
- Executive sponsor at client escalates to Lumenhall's CEO: MP briefs the CEO within the day.

## SOP-DELIVERY-11: AI agent and platform capability adoption

**Owner**: AI Delivery Lead (human, principal level, accountable for the agent library); MP approves exceptions.
**Trigger**: `product.agent_capability_added`; `product.release_shipped`; `product.roadmap_published`; `data.benchmark_ready`.
**Inputs**: release notes, capability description, roadmap, evaluation benchmarks for agent tasks, agent register, current engagement agent configurations.

### Steps
1. [agent] Map the capability or release to current and planned engagements; list which engagement agents or Keep-managed agents could use it, and which are exposed to deprecations or behavior changes.
2. [agent] On `data.benchmark_ready`, compare benchmark results (accuracy, cost per task, latency) against the current agent configurations and propose model or prompt changes with expected gains.
3. [human] AI Delivery Lead reviews the proposals in the weekly design forum and assigns trials on internal or low-risk workloads first.
4. [human] For any change to a live client-facing agent, the EM obtains client approval and requests the AI risk review (`product.ai_risk_review_requested`) and waits for `legal.ai_risk_review_completed` before deployment (COMPANY.md §9.4).
5. [agent] Run the evaluation suite on the candidate; the QA Lead approves the release only if accuracy is no worse than the baseline and cost per task does not rise more than 10%.
6. [human] On `product.roadmap_published`, MP and AI Delivery Lead update the delivery roadmap, the estimating model (agent-day assumptions; compute and model cost fall about 15% a year; COMPANY.md §8) and training plans.
7. [agent] Update the agent register and the leverage metrics (agents per human).

### Outputs and messages
- No dedicated bus emission by default; the outputs are internal tasks and updated estimating assumptions. If an adoption changes capacity (for example, a capability removes a manual task) the Agent emits `delivery.capacity_forecast_updated` (body per SOP-DELIVERY-09). A defect found in a trial raises `delivery.quality_issue_raised` (body per SOP-DELIVERY-07).

### SLA and controls
- Impact review in 5 BD of a release or capability; benchmark review in 5 BD; roadmap update in 10 BD.
- Controls: no live client agent is changed without human sign-off, an AI risk review where the change is material, and a rollback plan; all changes are logged in the agent register.

### Exceptions and escalation
- A release causes regression in a live client agent: treat as a quality issue (SOP-DELIVERY-07) and roll back within 1 BD.
- Capability suggests an engagement risk (for example, a training-data or licensing issue): refer to Legal and IT Security before use.

## SOP-DELIVERY-12: Security incident on a client engagement

**Owner**: Engagement Manager for the affected engagement; MP informed on high/critical; IT Security leads the incident.
**Trigger**: `it_security.incident_detected`.
**Inputs**: incident id, severity, affected systems, whether client data or client systems are involved, affected engagements and agents, current handling instructions from IT Security.

### Steps
1. [agent] Match the incident to engagements, client systems, delivery staff and agents by systems and credentials involved, and list the affected clients with their contractual security and notification clauses.
2. [human] EM acknowledges within 1 hour (critical) or 4 hours (high), and follows IT Security's containment instructions (for example, pausing agent runs, rotating client credentials, suspending shared workspaces).
3. [agent] Pause affected agents where IT Security instructs; the agent's actions and logs are preserved for forensic review.
4. [human] Principal drafts, with Customer Success and Legal, the client holding statement within 4 hours; no technical details are given until IT Security approves.
5. [human] Delivery freezes releases and deliverable transfers for the affected engagement until IT Security clears them.
6. [agent] Maintain the incident timeline for the engagement and update the plan impact (milestones at risk, days lost).
7. [human] After resolution, EM and QA Lead run a lessons-learned review within 10 BD, and any plan changes are handled under SOP-DELIVERY-06.

### Outputs and messages
- `delivery.quality_issue_raised` when delivery output or an agent was a contributor or victim (body per SOP-DELIVERY-07, `issue_type`=`sla_breach` or `agent_accuracy`, `severity` mirrors the incident).
- `delivery.capacity_forecast_updated` if the incident requires staff to be diverted for more than 5 BD.

### SLA and controls
- Acknowledge in 1 hour (critical) or 4 hours (high); client holding statement in 4 hours; the MP is informed of all high and critical incidents within 1 hour.
- Controls: personal-data breach notification to the ICO within 72 hours is General Counsel's decision with CISO and CEO (COMPANY.md §9.3); delivery staff and agents never notify regulators or clients about a breach on their own authority (COMPANY.md §9.4).

### Exceptions and escalation
- Severity `critical` may trigger `executive.crisis_declared`, which switches delivery into the crisis posture in SOP-DELIVERY-13.
- Incident involving a client with a Keep Enterprise 24x7 cover: the embedded team lead takes first response in addition to the EM.

## SOP-DELIVERY-13: Annual budget, OKRs and strategy alignment

**Owner**: Managing Partner, Delivery (Oliver Thackeray); preparer: Delivery Ops Lead with the Finance business partner.
**Trigger**: `finance.budget_cycle_opened`; `executive.budget_approved`; `executive.okrs_set`; `executive.strategy_updated`; `executive.crisis_declared`.
**Inputs**: the budget template; capacity forecast (SOP-DELIVERY-09); headcount plan; pipeline demand; agent compute costs; subcontractor plans; prior-year actuals; KPI definitions in `kpis.md`; the economics model in `economics.md`.

### Steps
1. [agent] On `finance.budget_cycle_opened`, produce a draft department budget: people cost by level at average headcount and loaded cost (base x 1.28), AI compute and tooling, subcontractors and associates, T&E and other lines, tied to the demand forecast (COMPANY.md §5.4 and §6.1 are the envelope).
2. [human] MP reviews and challenges the draft with the CFO's business partner; the cost-of-revenue effect is checked against target gross margin (48% FY2026, 58% FY2027, 64% FY2028; COMPANY.md §5.1), since delivery plus Customer Success cost forms cost of revenue.
3. [human] MP signs the submission; budget owners for non-people lines (AI compute, subcontractors) are named.
4. [agent] On `executive.budget_approved`, load the approved budget, headcount and targets into the department tracking, set spend alerts at 90% of any line, and issue the hiring plan for approved roles.
5. [human] On `executive.okrs_set`, MP cascades the objectives into delivery OKRs and personal goals within 10 BD; the KPIs that map to company OKRs (utilisation, margin, on-time delivery, client satisfaction) are re-baselined.
6. [human] On `executive.strategy_updated`, MP and Principals review service mix, pricing alignment, geographic plans (US office Q1 FY2027) and training priorities, and update the delivery plan.
7. [human] On `executive.crisis_declared`, MP triggers the crisis posture within 1 BD: freeze discretionary spend and non-critical hiring, protect live engagements and Keep SLAs first, and run a daily capacity and risk call until the crisis is lifted.

### Outputs and messages
- `delivery.budget_submitted` (recipient: finance): body keys `department` = `delivery`, `budget_cycle` (for example `BUD-2026`), `people_gbp`, `non_people_gbp`, `total_gbp`, `headcount_humans`, `headcount_agents`, `assumptions` (summary), `submitted_day`.
- `delivery.hire_requested` for roles approved in the plan and ready to open (body per SOP-DELIVERY-09).

### SLA and controls
- Budget submitted within 10 BD of the cycle opening (or by the deadline in the opening message if earlier); spend alert at 90% of any line; monthly variance review with Finance; any non-budgeted spend over £50k needs CFO approval and over £250k CEO approval (COMPANY.md §9.3).
- Controls: submitted totals must reconcile to the department envelope within £5k (see `economics.md`); no hiring outside the approved budget without `executive.headcount_approved`.

### Exceptions and escalation
- Finance returns the budget above the envelope: MP resubmits within 3 BD with a prioritised reduction list (first levers: subcontractor mix, agent compute efficiency, hire phasing).
- A material variance (above 10% on a line for two consecutive months) is reported to the CFO and the CEO with a recovery plan.

## Appendix: Topic coverage matrix

| Topic | Direction | SOP |
|---|---|---|
| `customer_success.churn_risk_flagged` | subscribe | SOP-DELIVERY-10 |
| `customer_success.feedback_received` | subscribe | SOP-DELIVERY-07 |
| `customer_success.health_score_updated` | subscribe | SOP-DELIVERY-10 |
| `customer_success.renewal_confirmed` | subscribe | SOP-DELIVERY-08 |
| `customer_success.support_escalated` | subscribe | SOP-DELIVERY-07 |
| `data.agent_quality_report_published` | subscribe | SOP-DELIVERY-07 |
| `data.benchmark_ready` | subscribe | SOP-DELIVERY-11 |
| `data.forecast_updated` | subscribe | SOP-DELIVERY-02, SOP-DELIVERY-09 |
| `executive.budget_approved` | subscribe | SOP-DELIVERY-13 |
| `executive.crisis_declared` | subscribe | SOP-DELIVERY-13 |
| `executive.okrs_set` | subscribe | SOP-DELIVERY-13 |
| `executive.strategy_updated` | subscribe | SOP-DELIVERY-13 |
| `external.client_scope_request` | subscribe | SOP-DELIVERY-06 |
| `finance.billing_schedule_created` | subscribe | SOP-DELIVERY-04 |
| `finance.budget_cycle_opened` | subscribe | SOP-DELIVERY-13 |
| `it_security.incident_detected` | subscribe | SOP-DELIVERY-12 |
| `legal.client_dispute_raised` | subscribe | SOP-DELIVERY-10 |
| `legal.contract_signed` | subscribe | SOP-DELIVERY-04 |
| `people.engagement_survey_completed` | subscribe | SOP-DELIVERY-09 |
| `people.new_hire_started` | subscribe | SOP-DELIVERY-04, SOP-DELIVERY-09 |
| `product.agent_capability_added` | subscribe | SOP-DELIVERY-11 |
| `product.release_shipped` | subscribe | SOP-DELIVERY-11 |
| `product.roadmap_published` | subscribe | SOP-DELIVERY-11 |
| `sales.deal_won` | subscribe | SOP-DELIVERY-03 |
| `sales.lead_qualified` | subscribe | SOP-DELIVERY-02 |
| `sales.proposal_requested` | subscribe | SOP-DELIVERY-01 |
| `delivery.budget_submitted` | publish | SOP-DELIVERY-13 |
| `delivery.capacity_forecast_updated` | publish | SOP-DELIVERY-09 |
| `delivery.engagement_completed` | publish | SOP-DELIVERY-08 |
| `delivery.engagement_kickoff` | publish | SOP-DELIVERY-04 |
| `delivery.hire_requested` | publish | SOP-DELIVERY-09, SOP-DELIVERY-13 |
| `delivery.milestone_reached` | publish | SOP-DELIVERY-05 |
| `delivery.quality_issue_raised` | publish | SOP-DELIVERY-07 |
| `delivery.scope_change_requested` | publish | SOP-DELIVERY-06 |
| `delivery.scoping_completed` | publish | SOP-DELIVERY-01 |
| `delivery.staffing_requested` | publish | SOP-DELIVERY-03 |
