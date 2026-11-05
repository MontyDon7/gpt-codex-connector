# Sales Standard Operating Procedures

These procedures govern the `sales` department (lead qualification, proposals, deal desk, pricing and discount authority, renewals proposals, pipeline, quotas and commission; agent class `SalesAgent`). The department head is the Chief Revenue Officer, Rahul Mehta (COMPANY.md §9.2). The department budget is £850k in FY2026 (£600k people, £250k non-people), £2,100k in FY2027 and £4,600k in FY2028 (COMPANY.md §5.4). Headcount is 5 humans and 3 AI agents at end FY2026, 14 and 9 at end FY2027, 26 and 18 at end FY2028 (COMPANY.md §6.1). The funnel the SOPs serve is 640 / 1,200 / 2,267 leads, 160 / 300 / 567 qualified opportunities, 80 / 150 / 283 proposals and 24 / 45 / 85 new logos for FY2026 / FY2027 / FY2028 (COMPANY.md §5.3).

Conventions used throughout:

- Steps are marked `[human]` or `[agent]`. Agents draft, score, analyse, monitor and propose; they never sign a contract, approve a discount, release a client-facing proposal without human review, approve a payment above £10,000 or notify a regulator (COMPANY.md §9.4).
- Role names are working titles from `blueprint.md`: **CRO** (Chief Revenue Officer, Rahul Mehta, the "Sales head" of COMPANY.md §9.3), **Sales Director**, **Senior Account Executive**, **Account Executive**, **Sales Development Representative** (SDR), **Solutions Consultant**, **Sales Operations Manager**, **Renewals and Expansion Manager**, **Deal Desk Analyst**, **Sales Operations Analyst**, **Proposal Writer**, and the sales agents (Lead Triage, Proposal Drafting, Pipeline and Forecast, Deal Desk, Renewals Radar, RFP Response, Account Research). Where a role does not yet exist, the cover named in `blueprint.md` applies: the CRO covers the Sales Director and Sales Operations Manager until Q2 FY2027, and the Renewals and Expansion Manager until Q3 FY2027.
- "Business day" (BD) means Monday to Friday excluding UK bank holidays. In the simulation `due_day` values are integer days from day 0 (Monday 2026-01-05); calendar-day SLAs are written as days.
- Business IDs follow CONVENTIONS.md §4: lead `LD-00001`, client `CL-0001`, deal `DL-0001`, proposal `PR-0001`, contract `CT-0001`, engagement `EN-0001`, invoice `INV-2026-0001`, budget cycle `BUD-2026`. Every message in a deal chain carries `deal_id`.
- Standing rule for all SOPs: one CRM record per deal; every discount, term and approval is recorded on that record before the proposal is issued; no client name or logo is used in marketing without written consent (Marketing, Legal).
- Constants defined in these SOPs (thresholds, SLAs, rates) are listed once in the section "Policy constants" at the end and are mirrored in `agent.py`.

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-SALES-01 | Lead qualification and hand-off (stages `mql` and `nurture`) | `marketing.lead_generated` | Sales Development Representative | `mql`: desk-check 1 BD, discovery call 2 BD; `nurture`: desk-check 5 BD |
| SOP-SALES-02 | Scoping gate and stalled-deal chase | `delivery.scoping_completed` | Senior Account Executive | Scoping gate cleared the day the pack arrives; stalled-deal chase after 14 days |
| SOP-SALES-03 | Proposal build, pricing and deal desk | `finance.pricing_check_completed` | Sales Operations Manager | Proposal ready within 3 days of both gates; sent within 10 days of the request |
| SOP-SALES-04 | Security review and contract terms | `it_security.security_questionnaire_completed`, `legal.security_terms_reviewed`, `legal.contract_risk_flagged`, `it_security.certification_status_updated` | Solutions Consultant | Security review 10 days; high-risk contract flag actioned within 3 days |
| SOP-SALES-05 | Deal approval under the delegations of authority | `executive.deal_decision_made` | Chief Revenue Officer | Approval pack within 1 BD of build; decision requested within 5 days |
| SOP-SALES-06 | Close, contract hand-off and commission accrual | `legal.contract_drafted`, `legal.contract_signed` and the client decision timer `sales.internal.client_decision` | Account Executive | Contract walk-through within 3 days of draft; contract due 14 days after acceptance |
| SOP-SALES-07 | RFP bid decision and response | `external.rfp_received` | Solutions Consultant | Bid or no-bid within 2 BD; response before the client deadline |
| SOP-SALES-08 | Renewals and churn defence | `customer_success.renewal_due`, `customer_success.renewal_confirmed`, `customer_success.churn_risk_flagged`, `customer_success.client_churned`, `customer_success.health_score_updated` | Renewals and Expansion Manager | Renewal proposal at least 60 days before term end; executive call within 2 days of a churn flag |
| SOP-SALES-09 | Expansion, next offer and change orders | `customer_success.expansion_opportunity_identified`, `delivery.engagement_completed`, `delivery.scope_change_requested` | Senior Account Executive | Expansion deal opened within 1 BD; change order priced within 2 BD |
| SOP-SALES-10 | Pipeline review, forecast and capacity inputs | `data.forecast_updated`, `delivery.capacity_forecast_updated` and the Monday and monthly schedules | Sales Operations Manager | Weekly review each Monday; monthly snapshot on the 1st |
| SOP-SALES-11 | Offer, price, collateral and marketing-programme changes | `executive.pricing_change_approved`, `product.pricing_change_proposed`, `product.agent_capability_added`, `product.roadmap_published`, `marketing.campaign_launched`, `marketing.content_published`, `marketing.event_scheduled` | Sales Operations Manager | Price list updated within 1 BD of approval; collateral within 10 days |
| SOP-SALES-12 | Planning, budget, OKRs and hiring | `finance.budget_cycle_opened`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated` | Chief Revenue Officer | Budget submitted by the cycle deadline; hire requests within 5 BD of approval |
| SOP-SALES-13 | Receivables interlock and commission release | `finance.invoice_overdue`, `finance.payment_received` | Sales Operations Manager | Relationship call within 2 days of an overdue notice |
| SOP-SALES-14 | Crisis mode | `executive.crisis_declared` | Chief Revenue Officer | Re-forecast and top-10 briefing within 2 days |
| SOP-SALES-15 | Quota, commission and monthly performance review | Monthly schedule (3rd business day) | Sales Operations Manager | Pack issued by business day 5 |

## SOP-SALES-01: Lead qualification and hand-off (stages `mql` and `nurture`)

**Owner**: Sales Development Representative (accountable: Sales Director; CRO until Q2 FY2027). Agent: Lead Triage Agent.
**Trigger**: `marketing.lead_generated`. Marketing emits this for every genuine lead (COMPANY.md §5.3 counts 640 / 1,200 / 2,267 leads, of which 25% qualify). Each message carries `stage` of `mql` (marketing score 60 or above) or `nurture` (below 60, already enrolled in Marketing's 90-day nurture sequence).
**Inputs**: body keys `lead_id`, `company`, `client_name`, `contact_name`, `contact_role`, `employees`, `sector` (or `industry`), `source`, `score` (marketing score 0 to 100), `stage`, `score_reasons`, `service_line`, `tier`, `amount_gbp`, `severity`, `summary`; Companies House record; existing CRM records (existing client or open deal); country or region.

### Steps

1. [agent] Validate the payload and check duplicates: same `lead_id` already worked, or same company with an open deal. A duplicate is merged and routed to the owning account executive without a new deal.
2. [agent] Park US leads before the US launch: a lead whose `country` or `region` is US and whose date is before 2027-01-01 (Q1 FY2027 New York opening, COMPANY.md §1) is logged as parked and returned to Marketing's nurture list; no deal is created.
3. [agent] Apply the ICP gate (COMPANY.md §2): `employees` between 200 and 2,000 inclusive. A lead outside the range is disqualified (logged) unless the SDR overrides for a named strategic account.
4. [agent] Compute the sales qualification score (0 to 100): company size in the ICP range 30; sector in the ICP list (financial services, healthcare services, logistics, manufacturing, retail, professional services) 20; board-level sponsor 25 (`board_sponsor` true, or marketing reason `senior_buyer`, or a contact at director level or above); defined operational pain 15 (a `pain` or `need` field, or marketing reason `named_pain_point`); budget confirmed 10 (`budget_confirmed`). The marketing `score` and `stage` are inputs to prioritisation, not a substitute for this score.
5. [agent] Prioritise by stage: `mql` leads go first in the queue; `nurture` leads are desk-checked from data already held (no call is made unless the sales score reaches the threshold). Severity `high` (marketing score 85 or above) and referral sources are flagged for same-day contact.
6. [human] SDR calls every `mql` lead within 2 BD of receipt, confirms the sponsor, pain and budget, and updates the evidence behind the score. A lead from a company above 2,000 employees, or from a named competitor, journalist or regulator, is reviewed by the Sales Director before any decision.
7. [agent] Decide: qualified if the sales score is 60 or above and the size gate is met; otherwise disqualified and returned to Marketing's nurture track (no bus message; the activity log records score and reasons). Planning conversion is about 50% for `mql` leads and about 5% for `nurture` leads (blended about 25%, COMPANY.md §5.3).
8. [agent] For a qualified lead: choose the first offer (the lead's `tier` if it is in the price list, otherwise from `service_interest`: compass to Compass Spark, forge to Forge Pilot, keep to Keep Essential), assign `deal_id` (`DL-nnnn`) and `client_id` (`CL-nnnn`), set the deal stage to `qualified`.
9. [agent] Emit `sales.lead_qualified` and `sales.proposal_requested` (section Outputs); the scoping due date is 7 days and the proposal due date 10 days from now.
10. [human] Senior Account Executive or Account Executive accepts the deal within 1 BD, confirms the scoping call date and the board sponsor.

### Outputs and messages

- `sales.lead_qualified` (to `marketing`, `delivery`, `data`): `deal_id`, `client_id`, `client_name`, `lead_id`, `service_line`, `tier`, `amount_gbp` (net or list price), `employees`, `industry`, `source`, `summary`, `due_day` (day + 7).
- `sales.proposal_requested` (to `delivery`, `finance`): the same deal keys plus `requested_discount_pct`, `change_order` (false), `scoping_due_day` (day + 7), `due_day` (day + 10), `summary`.
- Activity log: `sales.activity.lead_qualified`, `sales.activity.lead_disqualified`, `sales.activity.lead_parked` with `lead_id`, `score` and reasons.

### SLA and controls

- `mql`: desk-check within 1 BD, discovery call within 2 BD of receipt; `nurture`: desk-check within 5 BD.
- Qualification threshold: score 60 and size gate; changes need CRO approval, a 90-day back-test and a joint review with Marketing's Demand Generation Lead (marketing SOP-MARKETING-01 threshold of 60 is a separate marketing score).
- Weekly audit by the Sales Director: 20 random disqualified leads and 20 random qualified leads checked against the rubric; error rate above 10% triggers a model review.
- UK GDPR and PECR: contacts on the suppression list are not contacted; data subject requests go to Legal within 1 BD.

### Exceptions and escalation

- Lead claims a board mandate or urgency: SDR phones within 4 business hours and flags to the CRO.
- Qualified lead has an existing client: routed to the Renewals and Expansion Manager, handled under SOP-SALES-09.
- `nurture` lead that scores 60 or more on the sales rubric: accepted normally and recorded as a model learning case for Marketing's weekly audit (reported in the monthly pack, SOP-SALES-15).
- Lead acceptance rate below 15% over 10 leads: Sales Director and Marketing's Demand Generation Lead review ICP scoring within 7 days.

## SOP-SALES-02: Scoping gate and stalled-deal chase

**Owner**: Senior Account Executive (accountable: Sales Director; CRO until Q2 FY2027).
**Trigger**: `delivery.scoping_completed`; also the daily stalled-deal check.
**Inputs**: body keys `deal_id` (or `proposal_id`, `lead_id`, `engagement_id`, `client_id`), `client_id`, `service_line`, `tier`, `amount_gbp` (recommended list price), `estimated_value_gbp`, `duration_weeks`, `effort_days`, `est_margin_pct`, `earliest_start_day`, `risks`, `due_day`.

### Steps

1. [agent] Match the message to the open deal (by `deal_id`, `proposal_id`, `lead_id`, `engagement_id`, or the latest open deal for the `client_id`). If no deal is found, log `sales.activity.unmatched` and raise a task for the Sales Operations Manager.
2. [agent] Mark the scoping gate cleared, record the scoping day, move the deal from `qualified` to `scoped`, and store the scoped value if present (not for change orders).
3. [human] Senior Account Executive reads the scoping pack with the Solutions Consultant: confirms scope boundaries, assumptions, client dependencies and risks, and aligns the tier and price before the pricing check returns.
4. [agent] If the Finance pricing check is also in, proceed to SOP-SALES-03 the same day.
5. [agent] Daily: any deal still at `qualified` or `scoped` more than 14 days after the request (twice the 7-day scoping SLA) is chased once: a high-priority task to chase Delivery and Finance, due in 1 day, and an activity log entry.
6. [human] Sales Director escalates to the Managing Partner, Delivery (Oliver Thackeray) if a Programme or Scale scoping pack is later than 8 BD, or to the CFO (Hannah Whitcombe) if the Finance pricing check is later than 1 BD.

### Outputs and messages

- No bus message is emitted by this step on its own; the deal advances to SOP-SALES-03. For reference the request that starts the scoping clock is `sales.proposal_requested` (to `delivery`, `finance`) with keys `deal_id`, `client_id`, `client_name`, `service_line`, `tier`, `amount_gbp`, `requested_discount_pct`, `change_order`, `scoping_due_day`, `due_day`, `summary`; it is emitted from SOP-SALES-01 (new logos), SOP-SALES-07 (RFPs) and SOP-SALES-09 (expansion and change orders).
- Activity log: `sales.activity.gate_chase`, `sales.activity.unmatched`.

### SLA and controls

- Scoping returned by Delivery within 3 BD (Spark, Pilot), 5 BD (Sprint, Build), 8 BD (Programme, Scale) (delivery SOP-DELIVERY-01); the sales planning window is 7 days.
- Only one chase per deal; a second delay goes to the CRO.

### Exceptions and escalation

- Scoping pack shows estimated value more than 20% above or below the requested tier: Sales proposes re-tiering to the client; the deal desk records the change.
- Delivery declares no capacity: the deal is held and the Sales Director informs the client of a later start (see SOP-SALES-10).

## SOP-SALES-03: Proposal build, pricing and deal desk

**Owner**: Sales Operations Manager (CRO until Q2 FY2027; Deal Desk Analyst for day-to-day from Q3 FY2028). Agents: Proposal Drafting Agent, Deal Desk Agent.
**Trigger**: `finance.pricing_check_completed`.
**Inputs**: body keys `deal_id`, `proposal_id`, `client_id`, `service_line`, `tier`, `amount_gbp`, `list_price_gbp`, `discount_pct`, `margin_pct`, `terms_ok`, `approved`, `max_discount_pct`, `approval_required`; the scoping pack; the price list (`economics.md` section 3.5); the client's requested discount and terms.

### Steps

1. [agent] Match the deal and mark the pricing gate cleared. If Finance returns `approved` false, set the discount cap to 0% and raise a high-priority re-pricing task due in 3 days. If Finance returns a `max_discount_pct`, store it as the cap.
2. [agent] When both the scoping and pricing gates are cleared, and no proposal exists yet: assign `proposal_id` (`PR-nnnn`), set the stage to `proposal_build`, and price the deal: discount is the requested discount limited by any Finance cap and, in crisis mode, by the 5% ceiling; net price is list price less discount.
3. [agent] Determine the approvals required (COMPANY.md §9.3): discount above 10%; non-standard payment terms; net value of £500k or more; net value above £1.5m; non-standard legal terms or open risk flags. Record the list on the deal; a discount of 10% or less with standard terms is approved by the CRO and logged.
4. [agent] Emit `sales.security_review_requested` unless the security review is waived (expansion, change orders: client already cleared), due in 10 days.
5. [agent] If any approval is required, emit `sales.deal_approval_requested` (SOP-SALES-05); the proposal is held until the decision.
6. [agent] Proposal Drafting Agent assembles the proposal: scope, deliverables, team, timeline, price, milestone billing (30% on signature, 40% at mid-point, 30% on acceptance, expenses capped at 5% of fee), payment terms net 30, the start date (and the delivery start lag if capacity is tight, SOP-SALES-10), validity of 30 days.
7. [human] Account Executive or Senior Account Executive reviews and edits the draft; the Sales Director (CRO until Q2 FY2027) approves the proposal before issue; a Delivery Principal confirms scope for £260k or more.
8. [agent] When the security questionnaire and terms review are in, and any approval is granted, release the proposal: stage `proposal_sent`, emit `sales.proposal_sent`, start the client decision timer (SOP-SALES-06).
9. [human] Account Executive walks the client sponsor through the proposal within 2 BD; the decision date and the buying committee are recorded.

### Outputs and messages

- `sales.security_review_requested` (to `it_security`, `legal`): deal keys plus `summary`, `due_day` (day + 10).
- `sales.deal_approval_requested` (to `executive`, `finance`, `legal`): deal keys plus `discount_pct`, `reasons` (any of `discount_above_10pct`, `non_standard_payment_terms`, `deal_at_least_500k`, `deal_above_1_5m`, `non_standard_legal_terms`), `approvers`, `board_notification` (true above £1.5m), `summary`, `due_day` (day + 5).
- `sales.proposal_sent` (to `executive`, `data`): deal keys, `list_price_gbp`, `discount_pct`, `delivery_start_lag_days`, `summary`, `due_day` (day + 30, the validity period).
- Activity log: `sales.activity.proposal_built`, `sales.activity.discount_approved` (within CRO authority).

### SLA and controls

- Proposal built within 3 days of both gates; sent within 10 days of `sales.proposal_requested` (KPI `proposal_turnaround_days`).
- Control: no proposal is issued with a discount above 10% or non-standard payment terms without a recorded approval (COMPANY.md §9.3); KPI `discount_policy_compliance_percent` is 100%.
- Control: the proposal price must equal the price list (or an approved price override) less the recorded discount; the Deal Desk Agent rejects any price outside this.
- Control: no proposal claims a capability that has not been shipped (source is `product.agent_capability_added`).
- Deals at or above £500k carry a margin and cash pack from Finance (finance SOP-FINANCE-02).

### Exceptions and escalation

- Finance rejects the pricing (`approved` false): re-price at list, re-submit; if the client insists on the original discount, escalate to the CFO and CEO.
- Client requests changed milestone weighting or payment on completion: non-standard terms, approvals as above.
- Proposal not yet issued 14 days after both gates: Sales Director review; the deal is re-qualified if the sponsor has gone quiet.

## SOP-SALES-04: Security review and contract terms

**Owner**: Solutions Consultant (Senior Account Executive until Q3 FY2026).
**Trigger**: `it_security.security_questionnaire_completed`, `legal.security_terms_reviewed`, `legal.contract_risk_flagged`, `it_security.certification_status_updated`.
**Inputs**: body keys `deal_id` (or `client_id`, `proposal_id`), `blocking_gaps`, `severity`, `summary`, `certification`, `status`; the questionnaire pack and security terms (DPA, liability, IP).

### Steps

1. [agent] On `it_security.security_questionnaire_completed`: mark the questionnaire gate cleared. If `blocking_gaps` are present, add the flag `security_gap`, raise a high-priority task to close the gaps within 5 days, and add the non-standard legal terms approval (General Counsel and CEO).
2. [agent] On `legal.security_terms_reviewed`: mark the terms gate cleared.
3. [agent] On `legal.contract_risk_flagged`: log the severity; if `high` or `critical`, add a risk flag and the non-standard legal terms approval, raise a high-priority negotiation task due in 3 days, and, if the proposal is built but not yet sent, re-open approval (SOP-SALES-05).
4. [agent] On `it_security.certification_status_updated`: store the certification and its status (ISO 27001 achieved by end FY2026, Cyber Essentials Plus FY2026, SOC 2 Type II FY2027, COMPANY.md §8 item 7). Proposal and RFP templates may only cite a certification whose stored status is current.
5. [human] Solutions Consultant answers any residual client questions, runs the security call with the client's CISO if required, and agrees fallback positions with the Chief Information Security Officer (Wei Zhang) and the General Counsel (Callum Fraser).
6. [agent] When both the questionnaire and terms gates are cleared (and approvals granted), the proposal is released through SOP-SALES-03.

### Outputs and messages

- `sales.deal_approval_requested` (to `executive`, `finance`, `legal`) with reason `non_standard_legal_terms` when a security gap or a high or critical contract risk is found (keys as SOP-SALES-03).
- Activity log: `sales.activity.contract_risk`, `sales.activity.certification`.

### SLA and controls

- Security review completed within 10 days of `sales.security_review_requested`; a high or critical risk is actioned within 3 days.
- Waiver: expansion deals and change orders for an existing client whose security review is current are not re-reviewed; the waiver is recorded on the deal.
- Control: contracts with uncapped liability or non-standard IP or data terms need the General Counsel and CEO (COMPANY.md §9.3).

### Exceptions and escalation

- Certification lapses or is suspended: CRO informs open pursuits within 1 BD and withdraws the claim from templates; Legal advises on contractual representations.
- Client demands terms outside the standard (for example uncapped liability): no proposal is issued; General Counsel and CEO decide; if declined the deal is lost with reason `competitor` or `no_decision` as appropriate.

## SOP-SALES-05: Deal approval under the delegations of authority

**Owner**: Chief Revenue Officer.
**Trigger**: `executive.deal_decision_made`.
**Inputs**: body keys `deal_id`, `decision` (`approved`, `rejected` or `declined`), `conditions`, `summary`; the approval pack from SOP-SALES-03; the Finance opinion (finance SOP-FINANCE-02).

### Steps

1. [agent] Match the decision to the deal and log it.
2. [agent] If the decision is a rejection or decline: mark the deal lost with reason `executive_declined` and emit `sales.deal_lost`.
3. [agent] Otherwise record the approval and re-run the proposal-release check (SOP-SALES-03 step 8): the proposal is released if the security and terms gates are also cleared.
4. [human] CRO reads any conditions (for example, a changed payment schedule) and updates the proposal before issue; conditions that change the price or terms are re-checked by Finance.
5. [human] For deals above £1.5m the CRO briefs the Board directors through the CEO; the Board notification is recorded on the deal.
6. [human] The approval log records approver, date, reason, condition and the discount; Sales Operations Manager reviews the log monthly (SOP-SALES-15).

### Outputs and messages

- `sales.deal_approval_requested` (defined in SOP-SALES-03; re-issued when a risk flag is added after the request): approvers by reason: discount above 10% or non-standard payment terms, Finance head and CEO; net value £500k or more, CEO; net value above £1.5m, Board; non-standard legal terms, General Counsel and CEO.
- `sales.proposal_sent` on approval (keys as SOP-SALES-03).
- `sales.deal_lost` on decline: deal keys plus `reason` (`executive_declined`), `summary`.

### SLA and controls

- Approval pack issued within 1 BD of the proposal build; decision requested within 5 days (`due_day`); Finance opinion within 1 BD of the request; CFO and CEO decision within 2 BD for discounts above 10%.
- Control: the proposal is never released while `approval` is pending; the agent cannot approve on behalf of any approver.

### Exceptions and escalation

- No decision after 5 days: CRO escalates to the CEO's Chief of Staff; after 8 days the deal is flagged at risk to the client.
- Decision conditions that make the deal unprofitable: Sales Director and Finance Manager re-price or withdraw.

## SOP-SALES-06: Close, contract hand-off and commission accrual

**Owner**: Account Executive (Senior Account Executive for £260k or more).
**Trigger**: `legal.contract_drafted`, `legal.contract_signed`, and the client decision timer `sales.internal.client_decision` (an internal message the agent sends itself when a proposal is issued; it stands for the client's answer, which in operation is recorded by the Account Executive).
**Inputs**: `deal_id`, `contract_id` (`CT-nnnn`), signed contract, client decision and reason, `delay_days` (client decision window by tier, `economics.md` section 3.7).

### Steps

1. [human] Account Executive records the client's decision on the deal (accept, decline, no decision, timing) and, for a decline, the loss reason: `price`, `competitor`, `no_decision` or `timing` (others are logged as free text).
2. [agent] On acceptance: stage becomes `contract`, bookings and cycle days are recorded, and `sales.deal_won` is emitted to Legal (contract drafting), Finance (billing schedule), Delivery (staffing), Customer Success, Executive and Data. The contract is due 14 days after acceptance.
3. [agent] On decline: stage `lost`, loss recorded, `sales.deal_lost` emitted (to Marketing for win and loss review and nurture, Executive, Data).
4. [agent] On `legal.contract_drafted`: store `contract_id` and raise a high-priority task to walk the client through the contract within 3 days.
5. [human] Account Executive walks the client's sponsor and procurement through the contract with Legal on call; changes go to Legal, never agreed by Sales.
6. [agent] On `legal.contract_signed`: stage `won`; commission accrued at 1.7% of the net contract value (`economics.md` section 3.4) and logged.
7. [human] Account Executive introduces the client to the Delivery engagement lead and the Customer Success manager within 2 BD of signature and records the hand-over pack (stakeholders, success criteria, commercial promises).

### Outputs and messages

- `sales.deal_won` (to `legal`, `finance`, `delivery`, `customer_success`, `executive`, `data`): deal keys including `proposal_id`, `amount_gbp` (net), `discount_pct`, `source`, `summary`, `due_day` (day + 14).
- `sales.deal_lost` (to `marketing`, `executive`, `data`): deal keys plus `reason`, `summary`.
- Activity log: `sales.activity.contract_drafted`, `sales.activity.contract_signed` (with `commission_gbp`).

### SLA and controls

- Win reported within 1 BD of the client's acceptance; contract walk-through within 3 days of the draft; signature within 14 days of acceptance.
- Agents never sign or countersign; signature authority sits with the CEO (and per Legal's authority matrix).
- Commission accrues only on a signed contract; unsigned wins do not accrue.
- Loss reasons are coded within 3 BD and reviewed with Marketing monthly (marketing SOP-MARKETING-03).

### Exceptions and escalation

- Contract not signed 30 days after acceptance: CRO and General Counsel review; the deal is reversed from bookings if the client withdraws.
- Client signs a variant draft: Legal returns it to Sales; no start of work before signature unless the CEO approves a written letter of intent.

## SOP-SALES-07: RFP bid decision and response

**Owner**: Solutions Consultant (accountable: Sales Director; CRO until Q2 FY2027). Agent: RFP Response Agent.
**Trigger**: `external.rfp_received`.
**Inputs**: body keys `rfp_id`, `client_name`, `employees`, `estimated_value_gbp`, `due_day`, `tier`, `requirements`, `evaluation_criteria`.

### Steps

1. [agent] Apply the no-bid rules: no bid if the estimated value is below the minimum engagement (£90,000, the Forge Pilot list price, COMPANY.md §3.2); no bid if the response window is under 10 days; no bid if the client has fewer than 200 or more than 2,000 employees (outside the ICP, COMPANY.md §2).
2. [human] Sales Director (CRO for £500k or more) reviews the bid decision with the Solutions Consultant within 2 BD against evaluation criteria, incumbent, relationship, capacity and margin; the decision and reasons are logged.
3. [agent] If the bid is accepted: choose the tier (stated tier or the largest fixed-fee tier not above the estimated value; Keep is excluded for RFPs), open a deal with source `rfp`, and emit `sales.lead_qualified` and `sales.proposal_requested` with `rfp_due_day` set.
4. [agent] RFP Response Agent assembles the compliance matrix, drafts the answers from the approved answer library, and prepares the security evidence with IT Security.
5. [human] Solutions Consultant and Proposal Writer (Account Executive until Q4 FY2028) edit the response; Delivery Principal reviews the approach; Finance runs the pricing check (SOP-SALES-03).
6. [human] Sales Director signs off the submission before the deadline; the CEO is informed of RFPs of £500k or more.
7. [human] Debrief with the client after a loss; learning is fed to Marketing through `sales.deal_lost`.

### Outputs and messages

- `sales.lead_qualified` and `sales.proposal_requested` (as SOP-SALES-01) with `source` `rfp`, `rfp_id` and `rfp_due_day`.
- Activity log: `sales.activity.rfp_bid`, `sales.activity.rfp_no_bid` with `reasons`.

### SLA and controls

- Bid or no-bid within 2 BD; submission at least 1 BD before the deadline.
- Control: no uncapped liability or non-standard IP or data terms may be accepted in an RFP response without the General Counsel and CEO (COMPANY.md §9.3).
- Control: the RFP response uses only price list prices and approved discounts.

### Exceptions and escalation

- Reference or case study requested: Customer Success and Marketing supply approved material only (client consent held by Legal).
- Request for pricing below the margin floor: escalated through SOP-SALES-05.

## SOP-SALES-08: Renewals and churn defence

**Owner**: Renewals and Expansion Manager (CRO until Q3 FY2027). Agent: Renewals Radar Agent.
**Trigger**: `customer_success.renewal_due`, `customer_success.renewal_confirmed`, `customer_success.churn_risk_flagged`, `customer_success.client_churned`, `customer_success.health_score_updated`.
**Inputs**: body keys `client_id`, `client_name`, `contract_id`, `tier`, `annual_value_gbp` (or `amount_gbp`), `cpi_pct`, `health_score`, `severity`, `due_day` (term end); the Keep contract; QBR notes.

### Steps

1. [agent] On `customer_success.renewal_due`: compute the uplift: CPI plus 2% (planning CPI 3.0% if not supplied), capped at 7% (COMPANY.md §7). If the client is flagged at risk or the health score is below 60, waive the uplift (save offer).
2. [agent] Compute the new annual value (previous value x (1 + uplift)), assign `proposal_id`, record whether it is on time (at least 60 days before the term end) and update the renewal ledger.
3. [human] Renewals and Expansion Manager reviews the proposal with the Customer Success manager (Chief Customer Officer, Tobias Lindgren, for Enterprise tier); any additional concession within 10% is approved by the CRO, above that by the Finance head and CEO.
4. [agent] Emit `sales.renewal_proposal_sent` (to `customer_success`, `finance`, `legal`).
5. [agent] On `customer_success.churn_risk_flagged`: record the client as at risk and raise a task for an executive call within 2 days (high priority for high or critical severity).
6. [agent] On `customer_success.health_score_updated`: store the score; a score below 60 raises an account review task due in 5 days.
7. [agent] On `customer_success.renewal_confirmed`: clear the at-risk flag, record renewal bookings and on-time status.
8. [agent] On `customer_success.client_churned`: record churn, clear the at-risk flag, and close every open deal for that client with reason `client_churned` (emitting `sales.deal_lost` for each).
9. [human] CRO or the Renewals and Expansion Manager holds the executive call, agrees the save plan with Customer Success and Delivery, and records the outcome.

### Outputs and messages

- `sales.renewal_proposal_sent` (to `customer_success`, `finance`, `legal`): `client_id`, `client_name`, `contract_id`, `proposal_id`, `service_line` (`keep`), `tier`, `amount_gbp`, `previous_amount_gbp`, `uplift_pct`, `save_offer`, `summary`, `due_day` (term end).
- `sales.deal_lost` for open deals of a churned client: deal keys plus `reason` (`client_churned`), `summary`.
- Activity log: `sales.activity.renewal_proposal`, `sales.activity.churn_risk`, `sales.activity.health_score`, `sales.activity.renewal_confirmed`, `sales.activity.client_churned`.

### SLA and controls

- Renewal proposal issued at least 60 days before term end (KPI `renewal_proposal_on_time_percent` target 90%); executive call within 2 days of a churn flag; account review within 5 days of a health score below 60.
- Control: renewal uplift never exceeds 7%; the uplift is not waived without a recorded at-risk reason.
- Control: no renewal discount above 10% without the Finance head and CEO.

### Exceptions and escalation

- Client gives notice of termination (`external.client_notice_of_termination` goes to Customer Success): Sales supports the save plan if asked; if the client churns the deal is closed as above.
- Renewal due in under 60 days when notified: the proposal is issued immediately and flagged late in the monthly pack.

## SOP-SALES-09: Expansion, next offer and change orders

**Owner**: Senior Account Executive (Renewals and Expansion Manager for Keep, from Q3 FY2027).
**Trigger**: `customer_success.expansion_opportunity_identified`, `delivery.engagement_completed`, `delivery.scope_change_requested`.
**Inputs**: body keys `client_id`, `client_name`, `tier`, `service_line`, `engagement_id`, `days_by_level` (or `extra_days` and `level`), `summary`, `employees`, `industry`; the current engagement record.

### Steps

1. [agent] On `customer_success.expansion_opportunity_identified`: open an expansion deal for the stated tier (Keep Essential for service line keep, Forge Pilot otherwise, if no tier is given), unless the client already has an open deal at that tier (log a duplicate and stop).
2. [agent] On `delivery.engagement_completed`: log the completion; propose the next offer on the land-and-expand ladder (COMPANY.md §2, §10): Compass Spark to Forge Pilot, Compass Sprint to Forge Pilot, Compass Programme to Keep Plus, Forge Pilot to Forge Build, Forge Build to Keep Plus, Forge Scale to Keep Enterprise; open the expansion deal.
3. [agent] On `delivery.scope_change_requested`: price the change at the rate card (COMPANY.md §3.5) by level and days (`days_by_level` or `extra_days`), open a change-order deal (gate "scoping" already cleared by Delivery, security review waived), and request a pricing check. A change with no priceable days is logged and a task is raised.
4. [agent] Expansion and change-order deals carry `security_waived` true; they follow SOP-SALES-03 for pricing and approvals; for expansion, `sales.lead_qualified` is announced; for change orders it is not.
5. [human] Account Executive (with Customer Success manager) tests the expansion with the sponsor, agrees the commercial conversation and the proposal; change orders must be signed before work starts (COMPANY.md §7).
6. [human] The Renewals and Expansion Manager ensures every Forge Build or Scale is accompanied by a Keep proposal (COMPANY.md §2) and at least 40% of Compass Programmes.

### Outputs and messages

- `sales.lead_qualified` (expansion only) and `sales.proposal_requested` (as SOP-SALES-01) with `source` `expansion`, `engagement_completed` or `change_order` and `change_order` true for change orders.
- Activity log: `sales.activity.engagement_completed`, `sales.activity.expansion_duplicate`, `sales.activity.change_order`, `sales.activity.change_order_unpriced`.

### SLA and controls

- Expansion deal opened within 1 BD; change order priced within 2 BD; no work starts on a change before the change order is signed.
- Control: rate-card prices only; agent-day £350; no discount on change orders without the same approvals as SOP-SALES-03.

### Exceptions and escalation

- Client has an overdue invoice: new proposal is held until Finance releases (SOP-SALES-13).
- Delivery completes an engagement for a client in a churn-risk state: the expansion proposal is combined with the save plan under SOP-SALES-08.

## SOP-SALES-10: Pipeline review, forecast and capacity inputs

**Owner**: Sales Operations Manager (CRO until Q2 FY2027). Agent: Pipeline and Forecast Agent.
**Trigger**: `data.forecast_updated`, `delivery.capacity_forecast_updated`; the weekly (Monday) pipeline review; the monthly snapshot (first day of the month); the daily stalled-deal check.
**Inputs**: Data's forecast (`data.forecast_updated` body), Delivery's utilisation and capacity status (`utilisation_pct`, `capacity_status`), CRM pipeline.

### Steps

1. [agent] On `data.forecast_updated`: store the forecast and compute the weighted pipeline using the stage weights (`economics.md` section 3.7).
2. [agent] On `delivery.capacity_forecast_updated`: if utilisation is above 85% or the capacity status is `tight`, quote a 14-day delivery start lag on new proposals; otherwise 0.
3. [agent] Monday: weekly pipeline review: open deals by stage, weighted pipeline, stage ageing, crisis flag, coverage.
4. [agent] First day of the month: monthly KPI snapshot of the KPIs the agent can measure (`kpis.md`), published to Data.
5. [human] Sales Director leads the weekly review: deals stalled more than 14 days, slipping close dates, forecast call; actions are recorded.
6. [human] CRO signs the quarterly forecast and compares it with Data's forecast and the plan; variances above 15% are explained to the CEO.

### Outputs and messages

- No bus message is required: state and activity logs are updated (`sales.activity.pipeline_review`, `sales.activity.monthly_kpi_snapshot`, `sales.activity.forecast_received`, `sales.activity.capacity`). Where a deal's start lag changes, the next `sales.proposal_sent` carries `delivery_start_lag_days`.

### SLA and controls

- Pipeline reviewed every Monday; coverage target 3.3x; below 3.0x for two consecutive weeks triggers a pipeline plan.
- Forecast accuracy target 80% in FY2026 (KPI `forecast_accuracy_percent`).
- Stage movement is made only by humans or by the documented triggers; the Pipeline and Forecast Agent is read-only on the CRM.

### Exceptions and escalation

- Forecast differs from Data's by more than 15%: CRO and the Chief Data and AI Officer (Dr Emeka Nwosu) reconcile within 5 BD.
- Delivery utilisation above 90%: the CRO and the Managing Partner, Delivery agree a start-date policy and may hold new Programme and Scale proposals.

## SOP-SALES-11: Offer, price, collateral and marketing-programme changes

**Owner**: Sales Operations Manager (CRO until Q2 FY2027).
**Trigger**: `executive.pricing_change_approved`, `product.pricing_change_proposed`, `product.agent_capability_added`, `product.roadmap_published`, `marketing.campaign_launched`, `marketing.content_published`, `marketing.event_scheduled`.
**Inputs**: body keys `tier`, `new_price_gbp` or `change_pct`, `capability`, `summary`, `expected_leads`, `campaign`, `event`, `title`.

### Steps

1. [agent] On `executive.pricing_change_approved`: update the price list override for the tier (new price or change percentage) with effect for proposals issued after the approval; existing proposals keep their price until expiry. The Deal Desk Agent re-checks any open proposals above the new price.
2. [agent] On `product.pricing_change_proposed`: log the proposal and raise a task for the deal desk impact analysis within 5 days (effect on open pipeline, renewals uplift, discount norms).
3. [agent] On `product.agent_capability_added`: record the capability and raise a task to update proposal templates and the demo within 10 days.
4. [agent] On `product.roadmap_published`: store the roadmap for pre-sales positioning; Solutions Consultant adjusts roadmap talking points (no unshipped capability is promised).
5. [agent] On `marketing.campaign_launched`: compute SDR capacity (SDRs at year end x 60 leads a month); if `expected_leads` exceeds 60% of capacity, raise a high-priority capacity task due in 5 days.
6. [agent] On `marketing.content_published`: add the asset to the enablement library.
7. [agent] On `marketing.event_scheduled`: raise a task to assign an account executive and target list for the event within 7 days.
8. [human] Sales Operations Manager updates the price book, CPQ templates and collateral; the CRO approves the final price list; Marketing and Sales agree win and loss messaging monthly.

### Outputs and messages

- No bus message is required; activity logs: `sales.activity.pricing_change_approved`, `sales.activity.pricing_change_proposed`, `sales.activity.capability_added`, `sales.activity.roadmap`, `sales.activity.campaign`, `sales.activity.content`, `sales.activity.event`.

### SLA and controls

- Price list updated within 1 BD of `executive.pricing_change_approved`; collateral updated within 10 days.
- Control: only Executive-approved price changes enter the price list; no ad hoc list price change by Sales.
- Control: capability claims use `product.agent_capability_added` as the sole source.

### Exceptions and escalation

- Price rise approved while a large proposal is open: the CRO and Finance decide whether to honour the old price (default: honour until the 30-day validity ends).
- Campaign leads exceed capacity: Marketing and Sales agree phasing; the Sales Director may bring forward an SDR requisition (`sales.hire_requested`).

## SOP-SALES-12: Planning, budget, OKRs and hiring

**Owner**: Chief Revenue Officer.
**Trigger**: `finance.budget_cycle_opened`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated`.
**Inputs**: body keys `budget_cycle_id`, `amount_gbp`, OKRs, strategy update; `economics.md` and `blueprint.md`; prior-year actuals.

### Steps

1. [agent] On `finance.budget_cycle_opened`: build the department submission for the planning year (the next fiscal year in Q4): people and non-people from `economics.md` section 1 (FY2026 £600k / £250k, FY2027 £1,300k / £800k, FY2028 £2,300k / £2,300k). Submit once per cycle.
2. [human] CRO reviews the submission against the quota plan and the pipeline; any increase above the §5.4 envelope is submitted as a separate, non-budgeted request.
3. [agent] Emit `sales.budget_submitted` to Finance.
4. [agent] On `executive.budget_approved`: store the approved budget and emit one `sales.hire_requested` per planned hire for the year, per `blueprint.md` section 5 (title, level, count, start quarter).
5. [human] CRO and the Chief People Officer (Grace Adeyemi) agree the sequence of requisitions; time to hire is 45 days; hiring gates (Q2 FY2027 qualified opportunities at 85% of plan) are applied.
6. [agent] On `executive.okrs_set`: store the OKRs; the Sales Operations Manager re-cuts quotas and KPI targets within 10 BD.
7. [agent] On `executive.strategy_updated`: log the update and raise a task to review the ICP, territories and quotas within 10 days.

### Outputs and messages

- `sales.budget_submitted` (to `finance`): `department` (`sales`), `budget_cycle_id`, `amount_gbp` (total), `people_gbp`, `non_people_gbp`, `summary`.
- `sales.hire_requested` (to `people`): `department` (`sales`), `role_title`, `level`, `count`, `start_quarter`, `summary`.
- Activity log: `sales.activity.budget_approved`, `sales.activity.okrs`, `sales.activity.strategy`.

### SLA and controls

- Budget submitted by the cycle deadline; approved budget loaded and requisitions raised within 5 BD.
- Control: new headcount outside the approved budget needs the CEO (`executive.headcount_approved`, COMPANY.md §9.3).
- Control: one budget submission per cycle id.

### Exceptions and escalation

- Approved envelope below the submission: the CRO re-phases hires (never discounts above authority to compensate); the CEO decides priorities.
- Strategy change alters the ICP or geography: the CRO updates the qualification rubric through SOP-SALES-01 change control.

## SOP-SALES-13: Receivables interlock and commission release

**Owner**: Sales Operations Manager (CRO until Q2 FY2027).
**Trigger**: `finance.invoice_overdue`, `finance.payment_received`.
**Inputs**: body keys `client_id`, `invoice_id`, `amount_gbp`, `days_overdue`; the deal and commission ledger.

### Steps

1. [agent] On `finance.invoice_overdue`: put the client on credit hold for new proposals; add the flag `client_invoice_overdue` to every open deal for that client; raise a high-priority task for a relationship call within 2 days.
2. [human] Account Executive (Senior Account Executive for £260k or more) calls the client sponsor, agrees a payment date with Finance, and records the reason (dispute, process delay, cash); disputes go to Legal and the engagement lead.
3. [human] While the hold is on, new proposals for the client are prepared but not issued without the CFO's release; the CRO decides whether to pause a pending contract signature.
4. [agent] On `finance.payment_received`: clear the credit hold for that client and release the next half of the accrued commission that is due (first payment, then the balance after the final milestone payment).
5. [human] Sales Operations Manager reconciles commission accruals and releases with Finance payroll monthly (SOP-SALES-15).

### Outputs and messages

- No bus message is required; state and activity logs are updated: `sales.activity.credit_hold`, `sales.activity.payment_received` (with `commission_released_gbp`). A new proposal hold is evidenced by the risk flag `client_invoice_overdue` and the approval route in SOP-SALES-03.

### SLA and controls

- Relationship call within 2 days of an overdue notice (collections ladder: reminder day 31, call day 38, finance-head escalation day 45, legal letter day 60, COMPANY.md §7).
- Control: commission is released only after cash; clawback if an invoice is written off.

### Exceptions and escalation

- Collections escalated (`finance.collections_escalated` goes to Legal and Executive): Sales supports with relationship history but does not negotiate.
- Client dispute: no new proposal until Legal and the CFO confirm.

## SOP-SALES-14: Crisis mode

**Owner**: Chief Revenue Officer.
**Trigger**: `executive.crisis_declared`.
**Inputs**: body keys `severity`, `summary`, `scope`; pipeline and forecast.

### Steps

1. [agent] Switch crisis mode on: from now on every new deal is priced with a maximum discount of 5%; any requested discount above 5% is reduced to 5%.
2. [agent] Raise a critical task to re-forecast the pipeline and brief the top-10 opportunities by weighted value within 2 days.
3. [human] CRO calls the top-10 sponsors within 2 days, confirms commitment and timing, and agrees client messaging with the CEO and Marketing's CMO (Sofia Lindqvist); no new proposal goes out without the CRO's review.
4. [human] Sales Director pauses outbound sequences that cite the affected area; SDRs hold prospect emails until Marketing issues crisis-approved wording.
5. [human] CRO reports daily to the CEO; crisis mode is lifted only by an instruction from the CEO recorded on the deal log.

### Outputs and messages

- No bus message is required; activity log `sales.activity.crisis` with the discount ceiling; proposals issued during the crisis carry the capped discount.

### SLA and controls

- Re-forecast and top-10 briefing within 2 days; daily report to the CEO.
- Control: no discount above 5% is offered during a crisis without the CEO's written approval.

### Exceptions and escalation

- Crisis affects a client's delivery: the CRO and the Managing Partner, Delivery agree a client position before any proposal is issued.
- Data breach or security incident affecting deals: IT Security and Legal direct the client communication; Sales makes none without their approval.

## SOP-SALES-15: Quota, commission and monthly performance review

**Owner**: Sales Operations Manager (CRO until Q2 FY2027). Agent: Pipeline and Forecast Agent.
**Trigger**: Monthly schedule (3rd business day).
**Inputs**: CRM, deal desk log, finance month-end close (`finance.month_end_closed`), commission ledger, KPI definitions (`kpis.md`).

### Steps

1. [agent] Compile the monthly pack: all KPIs in `kpis.md` with actual against FY target, quota attainment per carrier, pipeline coverage, stage conversion, discount log, renewal calendar, lost-deal reasons and model learning cases from SOP-SALES-01.
2. [human] Sales Operations Analyst (Sales Operations Manager until Q4 FY2028) checks the data against the CRM and Finance; any difference above 2% is explained.
3. [human] Sales Operations Manager prepares commission statements: accrued on signature at 1.7% of net contract value, released after cash (SOP-SALES-13), clawbacks, payroll instructions to Finance.
4. [human] CRO reviews the pack with the Sales Director, the CFO and the CMO (joint monthly performance review) and agrees actions.
5. [human] Targets are reset only through the budget cycle or an `executive.okrs_set` or `executive.strategy_updated` change.

### Outputs and messages

- No bus message is required: the pack is shared with Executive and Data (`data.kpi_report_published` is Data's own output). State is updated and activity logged: `sales.activity.monthly_kpi_snapshot`.

### SLA and controls

- Pack issued by business day 5; commission statements to Finance by business day 6.
- Control: commission statements are four-eyes reviewed (Sales Operations Manager and CFO's delegate); no commission is paid without a signed contract and, for the first half, the first cash receipt.

### Exceptions and escalation

- Commission dispute: the CRO decides within 5 BD with Finance; the Chief People Officer is consulted for employment-contract questions.
- KPI definition dispute: Data decides the definition; Sales may not restate a prior quarter without Data and Finance agreement.

## Policy constants

The following values are defined here once and mirrored as module constants in `agent.py` with the same value.

| Constant | Value | Source or rule |
|---|---|---|
| ICP employee range | 200 to 2,000 | COMPANY.md §2 |
| ICP industries | financial services, healthcare services, logistics, manufacturing, retail, professional services | COMPANY.md §2 |
| Qualification score threshold | 60 of 100 (size 30, industry 20, sponsor 25, pain 15, budget 10) | SOP-SALES-01 |
| US lead parking | US leads before 2027 | COMPANY.md §1 |
| Sales head discount authority | 10% | COMPANY.md §9.3 |
| Deal above which the CEO approves | £500,000 net | COMPANY.md §9.3 |
| Deal above which the Board approves | £1,500,000 net | COMPANY.md §9.3 |
| Crisis discount ceiling | 5% | SOP-SALES-14 |
| Keep uplift | CPI + 2%, cap 7%, planning CPI 3.0% | COMPANY.md §7 |
| Renewal proposal lead time | 60 days before term end | SOP-SALES-08 |
| Commission rate | 1.7% of net contract value | `economics.md` section 3.4 |
| Scoping SLA | 7 days | SOP-SALES-02 |
| Proposal due | 10 days from the request | SOP-SALES-03 |
| Security review SLA | 10 days | SOP-SALES-04 |
| Approval request due | 5 days | SOP-SALES-05 |
| Proposal validity | 30 days | SOP-SALES-03 |
| Contract due after acceptance | 14 days | SOP-SALES-06 |
| Stalled-deal chase | after 14 days (twice the scoping SLA) | SOP-SALES-02 |
| SDR capacity | 60 leads a month; campaign alert above 60% of capacity | SOP-SALES-11 |
| Capacity start lag | 14 days when utilisation above 85% or status `tight` | SOP-SALES-10 |
| Health score review | below 60, task within 5 days | SOP-SALES-08 |
| Churn flag response | executive call within 2 days | SOP-SALES-08 |
| RFP no-bid | value below £90,000, response window under 10 days, or outside ICP size | SOP-SALES-07 |
| Stage weights | qualified 0.15, scoped 0.21, proposal_build 0.25, proposal_sent 0.30, negotiation 0.60, contract 0.90, won 1.00, lost 0.00 | `economics.md` section 3.7 |
| Client decision window | planning mean 65 days by tier (Spark 40, Essential 45, Pilot 50, Sprint and Plus 60, Build 80, Programme and Enterprise 85, Scale 105) | `economics.md` section 3.7 |
| Loss reasons | price, competitor, no_decision, timing; plus executive_declined and client_churned | SOP-SALES-06 |
