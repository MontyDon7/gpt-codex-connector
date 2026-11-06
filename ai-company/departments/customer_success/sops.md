# Customer Success Standard Operating Procedures

Department: `customer_success` (agent class `CustomerSuccessAgent`). Head: Tobias Lindgren, Chief Customer Officer (COMPANY.md §9.2). Scope: client onboarding and handover, health scoring, Keep retainer support tiers and SLAs, client feedback, renewals, churn prevention, expansion signalling, QBRs, references. UK context: UK GDPR and Data Protection Act 2018 (Lumenhall is normally a processor for client data and must tell the client controller of a breach without undue delay, so the client can meet its own 72-hour ICO duty), UK Late Payment of Commercial Debts (Interest) Act for the collections context. Team in FY2026: 1 human (the Chief Customer Officer, from Q3) and 1 AI agent (COMPANY.md §6.1). All figures are modelled assumptions, not real data.

Conventions used throughout:

- `[human]` steps are performed by the Chief Customer Officer, or by the Customer Success Manager, Client Support Specialist, Client Support Lead, Customer Success Analyst or Renewals and Commercial Manager once in post (see blueprint.md for start dates). Until a role is hired, the Chief Customer Officer performs its `[human]` steps; before the CCO joins (Q3 FY2026) the Managing Partner, Delivery covers them. `[agent]` steps are performed by the Customer Success agents working under a named human owner. Agents may draft, analyse, monitor and propose; they may not send unreviewed client communications, promise service credits, change prices, make final termination decisions or notify regulators or clients of a personal-data breach (COMPANY.md §9.4).
- Money in message bodies is `amount_gbp` ex VAT. Sim days are integers from Day 0 = 2026-01-05 (COMPANY.md §1); `due_day` keys are sim days. Business IDs follow CONVENTIONS section 4: `CL-0001`, `DL-0001`, `CT-0001`, `EN-0001`, `INV-2026-0001`, `INC-0001`, `BUD-2027` (the budget cycle opened in October 2026 is `BUD-2027`).
- Business hours: a business day is 10 hours, 08:00 to 18:00 UK. SLAs in "business days" exclude UK bank holidays.

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-CUSTOMER_SUCCESS-01 | Client onboarding and handover | `sales.deal_won`, `legal.contract_signed`, `finance.billing_schedule_created`, `delivery.engagement_kickoff` | Customer Success Manager | Welcome call within 2 days of deal won; handover complete within 15 days of signature |
| SOP-CUSTOMER_SUCCESS-02 | Client health scoring and weekly review | `delivery.milestone_reached`, `delivery.quality_issue_raised`, weekly schedule (Monday) | Customer Success Analyst | Score updated same sim day as the signal; weekly review each Monday; quality-issue recovery plan within 2 days |
| SOP-CUSTOMER_SUCCESS-03 | Keep support triage and SLAs | `external.client_feedback_submitted` (kind `support_ticket`) | Client Support Specialist | First response by tier and priority (section "Shared constants"); P1 and P2 escalated to Delivery and Product immediately |
| SOP-CUSTOMER_SUCCESS-04 | Client feedback, NPS and CSAT | `external.client_feedback_submitted` (kinds `nps`, `csat`, `complaint`, `praise`) | Customer Success Analyst | Detractor contacted within 2 business days; complaint answered within 1 business day |
| SOP-CUSTOMER_SUCCESS-05 | Commercial signals: invoices, payments, overdue and disputes | `finance.invoice_issued`, `finance.payment_received`, `finance.invoice_overdue`, `legal.client_dispute_raised` | Customer Success Manager | Relationship call by day 38 of an overdue invoice; expansion and renewal outreach held same day on a dispute |
| SOP-CUSTOMER_SUCCESS-06 | Churn-risk flagging and save plans | Health band turns red (internal rescore), dispute, confirmed breach | Chief Customer Officer | Executive sponsor call within 2 business days of a flag; save plan agreed within 5 business days |
| SOP-CUSTOMER_SUCCESS-07 | Keep renewals | Daily renewal scan (90 days before term end), `sales.renewal_proposal_sent` | Renewals and Commercial Manager (Chief Customer Officer until Q1 FY2028) | `customer_success.renewal_due` at term end minus 90 days; renewal confirmed or churn recorded within 14 days of the client decision window |
| SOP-CUSTOMER_SUCCESS-08 | Engagement closeout and expansion signalling | `delivery.engagement_completed` | Renewals and Commercial Manager (Chief Customer Officer until Q1 FY2028) | Closeout review within 30 days; NPS survey 7 days after completion; Keep attach recommendation same sim day |
| SOP-CUSTOMER_SUCCESS-09 | Security incident and data-breach client communications | `it_security.incident_detected`, `it_security.data_breach_confirmed`, `it_security.incident_resolved` | Chief Customer Officer | Holding statement and named-contact call same day for affected clients; written RCA within 5 business days of resolution |
| SOP-CUSTOMER_SUCCESS-10 | Termination notice, save deadline and churn post-mortem | `external.client_notice_of_termination` | Chief Customer Officer | Executive save call within 2 business days; save deadline at half the notice period (maximum 14 days); post-mortem within 21 days (15 business days) of churn |
| SOP-CUSTOMER_SUCCESS-11 | QBRs and release communications | Quarterly schedule (first month of each quarter), `product.release_shipped` | Customer Success Manager | QBR held within 21 days of quarter start; breaking-change notice 5 days before the change window |
| SOP-CUSTOMER_SUCCESS-12 | Case-study and reference eligibility | `marketing.case_study_requested` | Chief Customer Officer | Eligibility answer within 5 business days of the request |
| SOP-CUSTOMER_SUCCESS-13 | Budget, OKRs, strategy and crisis response | `finance.budget_cycle_opened`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated`, `executive.crisis_declared` | Chief Customer Officer | Budget submitted within the Finance cycle deadline; OKR-to-KPI mapping within 10 days; crisis outreach to Enterprise and non-green clients within 1 day |
| SOP-CUSTOMER_SUCCESS-14 | Capacity and hiring | Weekly schedule (capacity check), monthly hiring review; `customer_success.hire_requested` raised when a trigger is crossed | Chief Customer Officer | Hire request raised the same week (capacity) or on the first day of the next month (support and renewals triggers) the trigger is crossed |

Topic coverage: every subscribed topic is the trigger of at least one SOP above, and every published topic appears in the outputs of at least one SOP (see the checklist at the end of this document).

## Shared constants

These values are defined once here and mirrored in `agent.py`. Changing one means changing both.

### Health score model

| Component | Weight | What it measures |
|---|---|---|
| adoption | 25% | Agent usage, active users, tasks automated against plan |
| delivery | 20% | Milestone status, quality issues, acceptance |
| engagement | 15% | Sponsor and champion contact, QBR attendance |
| commercial | 15% | Payment behaviour, dispute status |
| sentiment | 15% | NPS and CSAT |
| support | 10% | Ticket severity, incidents affecting the client |

Score = sum of weight x component, each component 0 to 100, rounded to one decimal place. Baseline for a new client: adoption 65, delivery 75, engagement 80, commercial 90, sentiment 75, support 85 = 76.5.

| Constant | Value |
|---|---|
| Green band | score 75 and above |
| Amber band | 50 to under 75 |
| Red band | under 50 |
| Risk cleared | score 60 or above and no open dispute |
| Critical risk | red band and score under 35; otherwise red is severity high |
| Rescore message | band change, or a move of 5 points or more, or a forced rescore (new baseline, save) |
| No-contact decay | engagement -3 each weekly review when no sponsor touch for more than 45 days |

Signal effects on components (each component stays between 0 and 100):

| Signal | Effect |
|---|---|
| `delivery.engagement_kickoff` | engagement +5 |
| `delivery.milestone_reached` | delivery +5, engagement +2 |
| `delivery.engagement_completed` | delivery +10 |
| `delivery.quality_issue_raised` critical / high / medium / low | delivery -30 / -20 / -10 / -5 and sentiment -15 / -10 / -5 / -2.5 |
| Support ticket P1 / P2 / P3 / P4 | support -25 / -15 / -5 / 0 |
| Keep SLA breach (each missed first-response or resolution target on a ticket) | support -10 (`SLA_BREACH_SUPPORT_HIT`) |
| Security incident detected, severity critical / high / medium / low | support -25 / -15 / -5 / 0 |
| `it_security.incident_resolved` | support +20 |
| `it_security.data_breach_confirmed` | support -40, sentiment -30, engagement -10 |
| `legal.client_dispute_raised` | engagement -15, sentiment -25, commercial -30 |
| `external.client_notice_of_termination` | sentiment -40, engagement -20 |
| NPS response | sentiment = score x 10 |
| CSAT response (1 to 5) | sentiment = (score - 1) x 25 |
| Complaint / praise | sentiment -20 / +10 |
| Overdue invoice, worst invoice days from invoice date: under 31 / 31 to 44 / 45 or more | commercial capped at 75 / 50 / 25 |
| `finance.payment_received` clearing all overdue invoices | commercial restored to at least 90 |

### Keep support SLAs

Priority mapping from ticket severity: critical = P1, high = P2, medium = P3, low = P4. First response / resolution or workaround, in hours:

| Priority | Keep Essential | Keep Plus | Keep Enterprise |
|---|---|---|---|
| P1 | 4 / 10 | 1 / 4 | 0.25 / 4 |
| P2 | 10 / 30 | 4 / 20 | 1 / 8 |
| P3 | 20 / 50 | 10 / 30 | 4 / 20 |
| P4 | 30 / none | 20 / none | 10 / none |

Clocks run on business hours (10-hour day), except Enterprise P1 and P2 which run 24x7 (COMPANY.md §3.3 24x7 incident cover). Clients without a Keep contract (for example in the 30-day post-engagement warranty window) are served at Keep Essential targets. A first-response task is due after ceil(first response hours / 10) days, or the same day for Enterprise P1 and P2. A ticket breaches when its first-response time exceeds the first-response target or its resolution time exceeds the resolution target of the client's tier and priority (P4 has no resolution target). The times are the measured `first_response_hours` and `resolution_hours` on the ticket when present; otherwise the simulation estimates each as target x (0.5 + 0.25 x tickets still open on the desk), so a quiet desk answers at half the target and a desk with more than two other open tickets starts to breach. A ticket stays open for ceil(resolution hours / 10) days (24 for Enterprise P1 and P2; 5 days for P4). Support days included: Essential 5 a quarter, Plus 15 a quarter, Enterprise an embedded team (COMPANY.md §3.3).

### Renewal, churn and capacity constants

| Constant | Value | Source |
|---|---|---|
| Renewal notice lead | 90 days before term end | Department assumption (economics.md section 4) |
| Planning CPI / renewal uplift | 3.0% / CPI + 2% = 5.0%, capped at 7% | COMPANY.md §7 |
| Client decision window after the renewal proposal | 14 days | Department assumption |
| Saveable termination reasons | price, budget, service_quality, champion_left, low_usage, scope | Department assumption |
| Save rule (agent model of CCO judgement) | reason saveable, health before the notice at least 55, and no open dispute | Department assumption |
| Save deadline | half the notice period, minimum 1 and maximum 14 days after the notice | Department assumption |
| Churn post-mortem | 21 days (15 business days) after `customer_success.client_churned` | Department assumption |
| Compound churn-risk signal window | 30 days (`SIGNAL_WINDOW_DAYS`) | Department assumption |
| Compound churn-risk signals needed to flag | 2 distinct signals in the window (`SIGNAL_MIN_COUNT`) | Department assumption |
| Clients per named client manager | 22 (`CLIENTS_PER_NAMED_CSM`) | economics.md section 4 |
| Reference eligibility | green band, last NPS 9 or above, no dispute, not churned, completed engagement or live Keep contract | Department assumption |
| Collections ladder (Finance owns) | reminder day 31, call day 38, finance-head escalation day 45, legal letter day 60 | COMPANY.md §7 |

### Support desk, handover, Keep attach and hiring constants

| Constant (code name) | Value | Source |
|---|---|---|
| `SLA_BREACH_SUPPORT_HIT` | 10 points of support component per breach | Department assumption |
| `TICKET_LOAD_BASE` | 0.5 (fraction of target at an empty desk) | Department assumption |
| `TICKET_LOAD_PER_OPEN` | 0.25 (added fraction per other open ticket) | Department assumption |
| `HANDOVER_TARGET_DAYS` | 15 days from contract signature (kpis.md FY2026) | kpis.md |
| `ATTACH_REOFFER_DAYS` | 90 days after completion | SOP-CUSTOMER_SUCCESS-08 |
| `ATTACH_WINDOW_DAYS` | 365 days after completion | kpis.md |
| `CLIENTS_PER_NAMED_CSM` | 22 clients per named client manager | economics.md section 4 |
| `TICKETS_MONTH_FIRST_SPECIALIST` | 30 (more than, tickets in a month) | blueprint.md section 5 |
| `LIVE_KEEP_FIRST_SPECIALIST` | 8 (more than, live Keep clients) | blueprint.md section 5 |
| `TICKETS_MONTH_THIRD_SPECIALIST` | 150 (more than, tickets in a month) | blueprint.md section 5 |
| `SLA_HIRE_FLOOR_PCT` | 95 (percent, first-response SLA for two months running) | blueprint.md section 5 |
| `RENEWALS_FOR_MANAGER` | 30 (more than, Keep renewals in the next 12 months) | blueprint.md section 5 |
| `TIME_TO_HIRE_DAYS` | 45 days | COMPANY.md §8 |

---

## SOP-CUSTOMER_SUCCESS-01: Client onboarding and handover

**Owner**: Customer Success Manager (Chief Customer Officer until the first manager joins in Q1 FY2027). Agent: Onboarding and Handover Agent (the department agent in the simulation).
**Trigger**: `sales.deal_won` (the commercial win), `legal.contract_signed` (terms and dates), `finance.billing_schedule_created` (billing set up), `delivery.engagement_kickoff` (delivery starts). The record opens on the first of these to arrive.
**Inputs**: `client_id`, `client_name`, `deal_id`, `contract_id`, `service_line`, `tier`, `amount_gbp`, `start_day`, `term_months`, billing milestones, `engagement_id`.

### Steps

1. [agent] On `sales.deal_won`, open the client record (status `onboarding`) with the baseline health components, store service line, tier and annual value, and create two tasks: welcome call and stakeholder map (due in 2 days) and success plan and health baseline (due in 10 days).
2. [human] Customer Success Manager holds the welcome call with the sponsor, names the day-to-day champion and the executive sponsor, and records the stakeholder map.
3. [agent] On `legal.contract_signed`, if the line is Keep (or the tier starts `keep_`), record the Keep contract: tier, contract id, start day, term (default 12 months, the minimum, COMPANY.md §3.3) and term-end day = start + term. Set status `active`. Create the Keep onboarding task (monitoring, SLA and QBR calendar, due in 5 days). For non-Keep contracts, create a filing task (due in 3 days).
4. [agent] On `finance.billing_schedule_created`, record the schedule and create a task to confirm invoice contacts and purchase-order references (due in 3 days).
5. [agent] On `delivery.engagement_kickoff`, set status `in_delivery`, add engagement +5 to the health model, and create the handover pack and sponsor check-in task (due in 5 days).
6. [human] Customer Success Manager agrees the success plan (outcomes, adoption targets, QBR dates, escalation path) with the sponsor and signs off the handover pack. The 15-day clock is stopped when the plan is agreed and the pack is accepted.
7. [agent] Record the handover duration for the `onboarding_handover_days` KPI: calendar days from `legal.contract_signed` to the delivery kickoff, when the handover pack is issued (a contract that starts more than 30 days before signature is a migration and has no clock). If no kickoff has arrived 15 days after signature, create a high-priority overdue task and log `customer_success.activity.handover_overdue` once; a handover that completes late creates a task to record the cause.

### Outputs and messages

- `customer_success.health_score_updated` to broadcast (`*`; sales, delivery, data): `client_id`, `client_name`, `health_score` (baseline 76.5), `band`, `previous_score`, `previous_band`, `reason` ("new client baseline", "Keep contract signed"), `drivers`, `service_line`, `tier`, `amount_gbp`, `summary`.
- Tasks: welcome call, success plan, Keep onboarding, invoice contacts, handover pack.
- Activity log: `customer_success.activity.client_record_opened`, `onboarding_started`, `contract_recorded`, `billing_schedule_noted`, `kickoff_handover`, `handover_completed`, `handover_overdue`.

### SLA and controls

- SLA: welcome call within 2 days of `sales.deal_won`; success plan within 10 days; handover complete within 15 days of `legal.contract_signed` (FY2026 target; 12 days FY2027, 10 days FY2028).
- Control: every Keep contract has a term-end day, otherwise it has no renewal clock; the Customer Success Analyst reconciles live Keep contracts to the renewal clock each week.
- Control: the handover pack is a client-facing document and is reviewed by a human before release (COMPANY.md §4).
- Evidence: stakeholder map and success plan stored against `client_id`.

### Exceptions and escalation

- Contract signed before the deal event (out of order): the record is created from the contract; the welcome tasks are created when `sales.deal_won` arrives.
- No `client_id` on any trigger: log `customer_success.activity.unmatched`, match by exact client name, otherwise create a task for the Customer Success Analyst to resolve within 1 day.
- Client without a named sponsor after 10 days: Chief Customer Officer calls the signatory; engagement component held at the baseline until a sponsor is named.
- A deal at or above £500k (COMPANY.md §9.3) gets the Chief Customer Officer as executive sponsor from day one.

---

## SOP-CUSTOMER_SUCCESS-02: Client health scoring and weekly review

**Owner**: Customer Success Analyst (Chief Customer Officer until Q3 FY2027). Agent: Client Health Score Agent.
**Trigger**: `delivery.milestone_reached` (delivery progress), `delivery.quality_issue_raised` (delivery quality), and a weekly schedule (every 7 sim days) for the health review. Signals from SOP-CUSTOMER_SUCCESS-03, -04, -05 and -09 also rescore through this procedure.
**Inputs**: `client_id`, `engagement_id`, `milestone`, `severity`, current component scores, last-touch day, open incidents.

### Steps

1. [agent] On `delivery.milestone_reached`, add delivery +5 and engagement +2, record the milestone and rescore.
2. [agent] On `delivery.quality_issue_raised`, reduce delivery and sentiment by the severity table (shared constants), create a recovery-plan task with Delivery (due in 2 days; high priority for high or critical severity) and rescore. For high or critical severity also flag churn risk (SOP-CUSTOMER_SUCCESS-06).
3. [agent] Rescore: compute the weighted score and band. Publish `customer_success.health_score_updated` when the band changes or the score moves by 5 points or more, with the two lowest components as `drivers`.
4. [agent] Weekly: for each active client with no sponsor touch for more than 45 days, reduce engagement by 3 and rescore; run the capacity check (SOP-CUSTOMER_SUCCESS-14); log `customer_success.activity.weekly_health_review`.
5. [human] Monday health review (Chief Customer Officer, Customer Success Managers, and the Managing Partner, Delivery for red and amber clients): walk every red client and every amber client that dropped band, assign a named owner and a date to each.
6. [human] Customer Success Analyst fixes input data (wrong client mapping, missing sponsor contact). Scores are never edited by hand; the signal is corrected and the model recalculates.

### Outputs and messages

- `customer_success.health_score_updated` to broadcast (`*`; sales, delivery, data): `client_id`, `client_name`, `health_score`, `band`, `previous_score`, `previous_band`, `reason`, `drivers`, `service_line`, `tier`, `amount_gbp`, `summary`.
- `customer_success.churn_risk_flagged` when the band is red (see SOP-CUSTOMER_SUCCESS-06).
- Tasks: recovery plan with Delivery.

### SLA and controls

- SLA: score recalculated in the same sim day as the signal; weekly review every Monday; recovery plan within 2 days of a quality issue.
- Control: weights and thresholds are fixed in the shared constants and reviewed annually (and on `executive.strategy_updated`, see SOP-CUSTOMER_SUCCESS-13); changes need Chief Customer Officer approval.
- Control: a score above 75 never replaces a human check; the Customer Success Manager confirms the champion is still in post at each QBR.

### Exceptions and escalation

- Quality issue at a client already red: rescore only; the open churn flag is not re-raised unless the severity is higher.
- Unknown client in a delivery signal: create the record with the baseline and log `customer_success.activity.client_record_opened`; the Customer Success Analyst confirms the mapping within 1 day.
- Score swings by more than 20 points in a week: Customer Success Analyst audits the inputs before the Monday review.

---

## SOP-CUSTOMER_SUCCESS-03: Keep support triage and SLAs

**Owner**: Client Support Specialist (Client Support Lead from Q1 FY2028; Chief Customer Officer until the first specialist joins in Q2 FY2027). Agent: Support Triage Agent.
**Trigger**: `external.client_feedback_submitted` with `kind` = `support_ticket` (a client raises a support request through the service desk or an account contact).
**Inputs**: `client_id`, `ticket_id` (generated `TKT-0001` style when missing), `severity`, `text`, client Keep tier, `engagement_id`.

### Steps

1. [agent] Identify the client and its Keep tier (clients without Keep are served at Essential targets). Map severity to priority: critical P1, high P2, medium P3, low P4. Look up first-response and resolution targets in the SLA table (shared constants).
2. [agent] Create the first-response task with the SLA wording (due after ceil(first-response hours / 10) days; same day for Enterprise P1 and P2). Priority of the task: critical for P1, high for P2, medium otherwise.
3. [agent] Reduce the support component (P1 25, P2 15, P3 5, P4 0) and rescore (SOP-CUSTOMER_SUCCESS-02).
4. [human] Client Support Specialist replies to the client within the first-response target, confirms priority with the client, and coordinates with the Delivery Keep pod for fixes. P1 and P2 are owned by the Client Support Lead from FY2028.
5. [agent] Record the ticket with its first-response and resolution times and test both against the tier targets. For each missed target record an SLA breach (`customer_success.activity.sla_breach`), reduce the support component by 10 on top of the severity reduction, and create a same-day task to call the sponsor with the Chief Customer Officer review within 1 business day. The `support_first_response_sla` KPI is the share of tickets with no first-response breach.
6. [agent] For P1 and P2, publish `customer_success.support_escalated` so Delivery and Product can act; include the SLA targets and the breach flags so the receiving department sees the clock.
7. [human] On resolution, confirm with the client, record the support-day drawdown against the quarterly entitlement (Essential 5, Plus 15), and send the CSAT survey (SOP-CUSTOMER_SUCCESS-04).
8. [human] Within 2 business days of closing a P1, hold a short review (cause, client impact, prevention) and attach it to the client record.

### Outputs and messages

- `customer_success.support_escalated` to broadcast (`*`; delivery, product): `client_id`, `client_name`, `ticket_id`, `severity`, `priority`, `keep_tier`, `sla_response_hours`, `sla_resolution_hours`, `sla_response_breach`, `sla_resolution_breach`, `summary`, `engagement_id`.
- `customer_success.health_score_updated` when the support component moves the band or the score by 5 points.
- Activity log: `customer_success.activity.ticket_triaged`, `sla_breach`.

### SLA and controls

- SLA: first response and resolution targets by tier and priority (shared constants); KPI `support_first_response_sla` target 95% in FY2026.
- Control: automatic acknowledgements do not stop the first-response clock. An agent may never downgrade a P1 or P2; only the Client Support Specialist or the Client Support Lead can, with the client's agreement.
- Control: ticket text containing personal data is handled under the data-processing agreement and least-privilege access (COMPANY.md §9.4).

### Exceptions and escalation

- P1 on Keep Enterprise: page the human on call and the Delivery Keep pod lead immediately; the Chief Customer Officer is informed within 1 hour (Client Support Lead from FY2028).
- A P1 or P2 that touches client personal data or looks like a security event is also reported to IT and Security (SOP-CUSTOMER_SUCCESS-09 applies when an incident is declared).
- Ticket from an unknown client: create the record, log it as unmatched and ask the Customer Success Analyst to confirm within 1 day; the clock starts at receipt.
- SLA breach: record the cause, call the client sponsor the same day, and the Chief Customer Officer reviews within 1 business day. Any service credit is a commercial concession approved under COMPANY.md §9.3.

---

## SOP-CUSTOMER_SUCCESS-04: Client feedback, NPS and CSAT

**Owner**: Customer Success Analyst (Chief Customer Officer until Q3 FY2027). Agent: Feedback and Voice-of-Client Agent.
**Trigger**: `external.client_feedback_submitted` with `kind` = `nps`, `csat`, `complaint` or `praise`. Surveys are sent quarterly (relationship NPS), 7 days after `delivery.engagement_completed` (post-engagement NPS) and on ticket closure (CSAT).
**Inputs**: `client_id`, `kind`, `score` (NPS 0 to 10, CSAT 1 to 5), `text`, `severity`, optional `expansion_signal`, `expansion_service_line`, `expansion_tier`, `expansion_amount_gbp`.

### Steps

1. [agent] Identify the client; log and drop to the Customer Success Analyst when no client can be matched. Touch the client record (resets the 45-day no-contact clock).
2. [agent] For NPS, clamp the score to 0 to 10, classify promoter (9 to 10), passive (7 to 8) or detractor (0 to 6) and set sentiment = score x 10. For CSAT clamp to 1 to 5 and set sentiment = (score - 1) x 25. For a complaint reduce sentiment by 20; for praise add 10.
3. [agent] Summarise the feedback in about eight words as a theme (the language model is optional; the mock model works offline).
4. [agent] Create follow-up tasks: close the loop with a detractor within 2 business days (high priority); respond to a complaint within 1 business day (high priority).
5. [agent] Rescore and publish `customer_success.health_score_updated` if the band moves or the score changes by 5 points or more.
6. [agent] Publish `customer_success.feedback_received` to Marketing, Delivery and Product.
7. [agent] When the client voices an expansion signal and there is no open dispute, publish `customer_success.expansion_opportunity_identified` (default Forge Pilot at £90,000, COMPANY.md §3.2); Sales owns the conversation (SOP-CUSTOMER_SUCCESS-08).
8. [human] The Customer Success Manager (Chief Customer Officer until hired) calls every detractor and every complaint author, records the root cause and any promised remedy, and tells the client what will change. Praise is passed to the delivery team and to Marketing as a case-study lead.

### Outputs and messages

- `customer_success.feedback_received` to broadcast (`*`; marketing, delivery, product): `client_id`, `client_name`, `kind`, `score`, `category` (promoter, passive, detractor, complaint, praise or the kind), `severity`, `theme`, `text`, `service_line`, `summary`.
- `customer_success.expansion_opportunity_identified` to broadcast (`*`; sales) when an expansion signal is present: `client_id`, `client_name`, `service_line`, `tier`, `amount_gbp`, `rationale`, `health_score`, `summary`.
- `customer_success.health_score_updated` as in SOP-CUSTOMER_SUCCESS-02.

### SLA and controls

- SLA: detractor contacted within 2 business days; complaint answered within 1 business day; relationship NPS survey each quarter to the sponsor and one other stakeholder.
- Control: NPS is reported only with at least 10 responses in the period; below that it is shown as provisional.
- Control: no agent replies to a complaint or offers a remedy; a human does (COMPANY.md §9.4).
- Control: survey invitations follow the client's contract and UK GDPR; the client can opt out.

### Exceptions and escalation

- Complaint alleging a data issue or regulatory breach: tell the General Counsel (Callum Fraser) and the Chief Information Security Officer (Wei Zhang) the same day and apply SOP-CUSTOMER_SUCCESS-09.
- NPS of 0 to 3 from a Keep Enterprise sponsor: Chief Customer Officer calls within 1 business day and the CEO is told.
- Free text mentioning cancellation: treat as a churn-risk flag (SOP-CUSTOMER_SUCCESS-06).

---

## SOP-CUSTOMER_SUCCESS-05: Commercial signals: invoices, payments, overdue and disputes

**Owner**: Customer Success Manager (Chief Customer Officer until the first manager joins). Finance owns collection; Customer Success owns the relationship.
**Trigger**: `finance.invoice_issued` (an invoice was raised), `finance.payment_received` (cash applied), `finance.invoice_overdue` (an invoice has passed a ladder stage), `legal.client_dispute_raised` (a client dispute is open).
**Inputs**: `client_id`, `invoice_id`, `amount_gbp`, `days_overdue`, `severity` of the dispute, contract and engagement ids.

### Steps

1. [agent] On `finance.invoice_issued`, record the open invoice against the client for the commercial view.
2. [agent] On `finance.payment_received`, clear the invoice; if no invoice remains overdue restore the commercial component to at least 90; touch the client; rescore.
3. [agent] On `finance.invoice_overdue`, store the days overdue. Set the commercial component to 75, 50 or 25 for worst invoice age under 31, 31 to 44, 45 or more days. Create a relationship-call task for the Customer Success Manager due at day 38 of the ladder (or today if later) and rescore. COMPANY.md §7 ladder: reminder day 31, call day 38, finance-head escalation day 45, legal letter day 60.
4. [human] On the day-38 step the Customer Success Manager joins Finance on a call with the sponsor to understand whether the delay is administrative (PO, approval) or a service dispute, and reports the finding to the Billing and Collections Specialist.
5. [agent] On `legal.client_dispute_raised`, mark the client in dispute, reduce engagement by 15, sentiment by 25 and commercial by 30, create a critical task to hold expansion and renewal outreach and align with Legal (due in 1 day), rescore and flag churn risk (high).
6. [human] The Chief Customer Officer and General Counsel agree the single client voice for the dispute. Customer Success keeps working on service delivery but does not discuss commercial positions.

### Outputs and messages

- `customer_success.health_score_updated` to broadcast (`*`): as in SOP-CUSTOMER_SUCCESS-02.
- `customer_success.churn_risk_flagged` to broadcast (`*`; sales, delivery, executive) on a dispute: `client_id`, `client_name`, `severity` (high), `reason` ("legal dispute raised"), `health_score`, `band`, `amount_gbp`, `service_line`, `tier`, `recommended_action`, `summary`.
- Tasks: day-38 relationship call; hold on outreach.

### SLA and controls

- SLA: call by day 38; dispute hold applied the same sim day.
- Control: no expansion recommendation (`customer_success.expansion_opportunity_identified`) and no renewal outreach while a dispute is open; the flag lifts only when Legal reports it closed and the score is at least 60.
- Control: Customer Success does not waive interest, issue credit notes or change terms; those belong to Finance and Legal (COMPANY.md §9.3).

### Exceptions and escalation

- Overdue invoice from a Keep Enterprise client: the Chief Customer Officer joins the day-38 call and tells the Chief Financial Officer (Hannah Whitcombe) before the day-45 escalation.
- Payment received without matching invoice id: apply to the client and log; Finance resolves the mapping.
- Dispute severity critical: the Chief Customer Officer informs the CEO the same day.

---

## SOP-CUSTOMER_SUCCESS-06: Churn-risk flagging and save plans

**Owner**: Chief Customer Officer (Tobias Lindgren).
**Trigger**: an internal rescore that puts a client in the red band (score under 50); also dispute (SOP-CUSTOMER_SUCCESS-05), high or critical quality issue (SOP-CUSTOMER_SUCCESS-02), confirmed data breach (SOP-CUSTOMER_SUCCESS-09), termination notice (SOP-CUSTOMER_SUCCESS-10) and a renewal proposal issued to a red or disputed client (SOP-CUSTOMER_SUCCESS-07).
**Inputs**: `client_id`, `health_score`, `band`, lowest two components (`drivers`), `amount_gbp`, tier, reason, last-touch day.

### Steps

1. [agent] When a client is red, set severity critical if the score is under 35, otherwise high. If a risk is already open at the same or higher severity, do nothing; a higher severity re-flags.
   Compound signals: a client that is not yet red is also flagged (severity high) when two distinct negative signals land inside 30 days. The signals are a detractor NPS (0 to 6), a client complaint and a high or critical support ticket; repeats of the same signal do not count twice. The flag reason lists the signals. The same signals keep an open flag from clearing while two or more are still inside the window.
2. [agent] Open the risk, create a save-plan task (due in 2 days; critical for critical severity, high otherwise) and publish `customer_success.churn_risk_flagged` with the recommended action: executive sponsor call within 2 business days; save plan owned by the CCO.
3. [human] Chief Customer Officer calls the executive sponsor within 2 business days, agrees the root cause with the client and names a save owner inside Lumenhall (Delivery Principal, Managing Partner or CEO for the largest accounts).
4. [human] Within 5 business days the save plan is written: what will change, by when, who is accountable, what the client will see, and how health will be re-measured. It is shared with Delivery and Sales.
5. [agent] When health recovers to 60 or above with no open dispute, close the risk (`customer_success.activity.risk_cleared`).
6. [human] Chief Customer Officer reviews all open flags in the Monday health review (SOP-CUSTOMER_SUCCESS-02) and reports them to the CEO monthly; flags on clients above £500k a year go to the CEO within 1 business day.

### Outputs and messages

- `customer_success.churn_risk_flagged` to broadcast (`*`; sales, delivery, executive): `client_id`, `client_name`, `severity`, `reason`, `health_score`, `band`, `amount_gbp`, `service_line`, `tier`, `recommended_action`, `summary`.
- Tasks: save plan for the named client.
- Activity log: `customer_success.activity.risk_cleared`.

### SLA and controls

- SLA: executive sponsor call within 2 business days of a flag; save plan within 5 business days; KPI `at_risk_save_rate` target 40% in FY2026 (clients still active 90 days after the flag).
- Control: one open flag per client; closing a flag needs the score at 60 or above and no dispute, or a Chief Customer Officer decision recorded with a reason.
- Control: Delivery and Sales must acknowledge the flag within 1 business day (they subscribe to the topic).

### Exceptions and escalation

- Client in dispute: the save plan is agreed with the General Counsel before the client sees it.
- Save requires a commercial concession: Sales head for a discount of 10% or less; Finance head and CEO above 10% or for non-standard terms (COMPANY.md §9.3).
- No improvement after 30 days: Chief Customer Officer takes the plan to the CEO for a go or no-go on further investment.

---

## SOP-CUSTOMER_SUCCESS-07: Keep renewals

**Owner**: Renewals and Commercial Manager (Chief Customer Officer until Q1 FY2028). Agent: Renewals and Expansion Agent.
**Trigger**: the daily renewal scan (a Keep term end 90 days away) and `sales.renewal_proposal_sent` (Sales has sent the proposal). The client decision is a queued item the agent processes on the tick 14 days after the proposal (no separate message).
**Inputs**: `client_id`, `contract_id`, tier, annual value, term-end day, health score and band, `amount_gbp` of the proposal, `client_decision`.

### Steps

1. [agent] Daily: for each non-churned Keep client not yet notified, if term-end day minus today is 90 days or fewer, mark it notified, create a renewal-plan task (due in 5 days, high priority) and publish `customer_success.renewal_due` with the current value, proposed uplift (5.0%, capped at 7%) and proposed amount.
2. [human] Renewals and Commercial Manager and the Customer Success Manager prepare the renewal plan: value delivered (adoption, SLA performance, support-day use), roadmap, risks, uplift rationale, option to move tier (Essential to Plus, Plus to Enterprise).
3. [human] Sales sends the proposal (Sales head authority up to a 10% discount; above that Finance head and CEO, COMPANY.md §9.3). Finance checks the pricing and Legal prepares the order form.
4. [agent] On `sales.renewal_proposal_sent`, record the proposal and the proposed amount, start the 14-day decision window and flag churn risk (high) if the client is red or in dispute.
5. [human] Customer Success runs the renewal conversation with the sponsor and confirms the decision in writing. A health review precedes the conversation.
6. [agent] On the decision timer: a confirmed renewal extends the term by 12 months, resets the renewal flags, creates a renewal-onboarding and QBR calendar task (due in 10 days) and publishes `customer_success.renewal_confirmed` with the new amount and the change. A decision to leave goes to SOP-CUSTOMER_SUCCESS-10. If no decision is recorded, the model assumes renewal unless the client is red or in dispute.
7. [human] Legal records the signed renewal; Finance updates the billing schedule and uplift from the renewal date.

### Outputs and messages

- `customer_success.renewal_due` to broadcast (`*`; sales, finance, legal): `client_id`, `client_name`, `contract_id`, `service_line` (keep), `tier`, `amount_gbp`, `proposed_uplift_pct`, `proposed_amount_gbp`, `due_day`, `health_score`, `band`, `summary`.
- `customer_success.renewal_confirmed` to broadcast (`*`; finance, legal, sales, delivery, data): `client_id`, `client_name`, `contract_id`, `service_line`, `tier`, `amount_gbp`, `previous_amount_gbp`, `nrr_delta_gbp`, `term_months`, `new_term_end_day`, `summary`.
- `customer_success.client_churned` on non-renewal (see SOP-CUSTOMER_SUCCESS-10).
- `customer_success.churn_risk_flagged` when a proposal goes to a red or disputed client.

### SLA and controls

- SLA: `customer_success.renewal_due` at 90 days before term end; Sales proposal sent within 15 business days of the notice; renewal decision within the 14-day window; renewal onboarding task within 10 days.
- Control: uplift is CPI + 2% capped at 7% (COMPANY.md §7); any lower uplift or discount is an approved concession.
- Control: no renewal is confirmed from an agent without a signed order from Legal.
- Control: renewals above £500k go through the deal-approval path (COMPANY.md §9.3).

### Exceptions and escalation

- Term end passes without a signed renewal: Chief Customer Officer and General Counsel decide whether to continue service under the existing terms and bill monthly while the paper is completed.
- Client asks to downgrade the tier: the change is a contraction in NRR; Chief Customer Officer approves with Sales and Finance.
- Proposal rejected for price: treat as a saveable reason under SOP-CUSTOMER_SUCCESS-10.

---

## SOP-CUSTOMER_SUCCESS-08: Engagement closeout and expansion signalling

**Owner**: Renewals and Commercial Manager (Chief Customer Officer until Q1 FY2028). Agent: Renewals and Expansion Agent.
**Trigger**: `delivery.engagement_completed` (a Compass or Forge engagement is accepted).
**Inputs**: `client_id`, `engagement_id`, `tier`, `service_line`, current health, dispute status, whether a Keep contract already exists, price list (COMPANY.md §3).

### Steps

1. [agent] Set the client to `active`, add delivery +10 and rescore. Create a closeout review and 30-day post-engagement check task (due in 30 days) and a post-engagement NPS survey task (due in 7 days).
2. [agent] Do not recommend anything if the engagement was already flagged, the client is in dispute or the client is red.
3. [agent] Apply the land-and-expand rules (COMPANY.md §2, §10): Forge Build without Keep recommends Keep Plus (£216,000 a year); Forge Scale recommends Keep Enterprise (£480,000); Compass Programme recommends Keep Essential (£96,000); Compass Spark and Compass Sprint recommend Forge Pilot (£90,000); Forge Pilot recommends Forge Build (£260,000).
4. [agent] Publish `customer_success.expansion_opportunity_identified` and record the engagement id so the same engagement is not recommended twice.
5. [human] Renewals and Commercial Manager reviews the recommendation with the Customer Success Manager and hands it to Sales (Chief Revenue Officer, Rahul Mehta) with the outcomes achieved, the sponsor's own words and the client's stated priorities.
6. [human] Sales owns the proposal; Customer Success joins the first conversation. For Forge Build and Scale the Keep proposal is part of the closeout meeting, since Keep is meant to attach to every Build and Scale (COMPANY.md §2).

### Outputs and messages

- `customer_success.expansion_opportunity_identified` to broadcast (`*`; sales): `client_id`, `client_name`, `engagement_id`, `service_line`, `tier`, `amount_gbp`, `source_tier`, `health_score`, `rationale`, `summary`.
- `customer_success.health_score_updated` as in SOP-CUSTOMER_SUCCESS-02.
- Tasks: closeout review, NPS survey.

### SLA and controls

- SLA: recommendation published on the same sim day as `delivery.engagement_completed`; closeout review within 30 days; NPS survey sent 7 days after completion.
- Control: COMPANY.md §2 is the rule: Keep attaches to every Forge Build and Scale, and to at least 40% of Compass Programmes. KPI `keep_attach_forge_build_scale` target is therefore 100% in every year and `keep_attach_compass_programme` target 40% (FY2028 stretch 45%). The agent keeps a ledger of completed Build, Scale and Programme engagements: attached when a Keep contract is live at completion or signed within 365 days. At 90 days unattached it creates a re-offer task (reduced Essential scope); when the 365-day window closes on a Build or Scale it logs `customer_success.activity.keep_attach_lapsed` and creates a critical task for the Chief Customer Officer to record the policy exception with the CEO. Unattached Build and Scale clients are listed at the monthly pack with the reason.
- Control: no recommendation while a dispute is open or the client is red.

### Exceptions and escalation

- Client declines Keep at closeout: record the reason (cost, in-house capability, timing); Renewals and Commercial Manager re-offers a reduced Essential scope within 90 days.
- Engagement completed early with unresolved quality issues: Delivery and Customer Success agree a remediation plan before any expansion approach.

---

## SOP-CUSTOMER_SUCCESS-09: Security incident and data-breach client communications

**Owner**: Chief Customer Officer (with the Chief Information Security Officer, Wei Zhang, and the General Counsel, Callum Fraser, who own the incident and the legal notifications).
**Trigger**: `it_security.incident_detected` (incident declared), `it_security.data_breach_confirmed` (personal data confirmed affected), `it_security.incident_resolved` (incident closed).
**Inputs**: `incident_id` (`INC-0001` style), `severity`, `affected_client_ids`, `personal_data` flag, resolution notes.

### Steps

1. [agent] On `it_security.incident_detected`, for each affected client reduce the support component by the severity (critical 25, high 15, medium 5), record the open incident and create a holding-statement and named-contact call task (due the same day; critical for critical or high severity).
2. [agent] If no client is named and the incident is critical, create a proactive briefing task for every live Keep Enterprise client (due the same day).
3. [human] Chief Customer Officer agrees the holding statement with the CISO and the General Counsel; the Customer Success Manager calls the sponsor of each affected client. The statement says what is known, what is not, and when the next update is.
4. [agent] On `it_security.data_breach_confirmed`, for each affected client reduce support by 40, sentiment by 30 and engagement by 10, create an executive call and data-protection support pack task (same day, critical) and flag churn risk (critical).
5. [human] The General Counsel decides notification content. Lumenhall, as processor, tells the client controller without undue delay so the client can notify the ICO within its own 72-hour deadline (COMPANY.md §9.3). Customer Success does not notify any regulator and does not describe legal obligations to the client.
6. [agent] On `it_security.incident_resolved`, remove the incident from each client, add support +20, create a post-incident review and written RCA task (due in 5 days) and rescore.
7. [human] Within 5 business days the Customer Success Manager walks the client through the RCA and the preventive actions agreed with IT and Security.

### Outputs and messages

- `customer_success.health_score_updated` (broadcast; sales, delivery, data) for each affected client.
- `customer_success.churn_risk_flagged` (critical) for each client affected by a confirmed breach: `client_id`, `client_name`, `severity`, `reason` ("confirmed data breach affecting client"), `health_score`, `band`, `amount_gbp`, `recommended_action`, `summary`.
- Tasks: holding statement, executive call, support pack, RCA.
- Activity log: `customer_success.activity.incident_noted`, `breach_noted`, `incident_resolved_noted`.

### SLA and controls

- SLA: holding statement and named-contact call the same day the incident is declared for affected clients; executive call the same day for a confirmed breach; RCA within 5 business days of resolution.
- Control: every external statement is approved by the General Counsel and the CISO; agents never send breach communications (COMPANY.md §9.4).
- Control: affected client list comes from IT and Security's `affected_client_ids`; Customer Success does not infer it.

### Exceptions and escalation

- Severity critical may lead to `executive.crisis_declared`, which changes the playbook (SOP-CUSTOMER_SUCCESS-13).
- Affected client is on a Keep Enterprise steering committee: the CEO attends the executive call.
- Incident with no confirmed client impact: no client is contacted unless a client asks; Customer Success prepares a reactive Q and A.

---

## SOP-CUSTOMER_SUCCESS-10: Termination notice, save deadline and churn post-mortem

**Owner**: Chief Customer Officer (Tobias Lindgren).
**Trigger**: `external.client_notice_of_termination` (a client serves notice). The save deadline is a queued item the agent processes on the tick; the non-renewal decision comes from SOP-CUSTOMER_SUCCESS-07.
**Inputs**: `client_id`, `reason`, `notice_period_days` (default 30), health before the notice, dispute status, contract terms.

### Steps

1. [agent] Record the reason, store the health score before the notice and reduce sentiment by 40 and engagement by 20; rescore and flag churn risk (critical).
2. [agent] Create two tasks: executive save call with the sponsor (due in 2 days, critical) and prepare the churn post-mortem file (due in 10 days).
3. [agent] Schedule the save deadline at half of the notice period, at least 1 and at most 14 days out.
4. [human] Chief Customer Officer calls the sponsor within 2 business days, listens, and confirms the true reason. Where price or scope is the issue, the Chief Revenue Officer and the Finance head are brought in under COMPANY.md §9.3.
5. [agent] At the save deadline: if the reason is in the saveable set (price, budget, service quality, champion left, low usage, scope), the health score before the notice was at least 55 and there is no dispute, treat the notice as withdrawn: raise sentiment to at least 60 and engagement to at least 70, clear the risk and publish a forced health update. Otherwise record the churn.
6. [agent] On churn, set the status to `churned`, create the post-mortem task (due in 21 days) and publish `customer_success.client_churned` with the reason, type (termination or non-renewal), the last NPS and the post-mortem due day.
7. [human] Within 21 days (15 business days) the Chief Customer Officer, the Customer Success Manager and the Delivery lead write a post-mortem: timeline, true cause, early signals missed, what to change. Lessons are shared with Sales, Delivery and Product, and the playbooks (SOP-CUSTOMER_SUCCESS-02 weights, -06 triggers) are updated if warranted.
8. [human] Customer Success tells Finance (the topic reaches `finance`) so billing stops and any final invoices follow the contract; Legal handles notice validity and exit obligations.

### Outputs and messages

- `customer_success.churn_risk_flagged` (critical) at notice.
- `customer_success.health_score_updated` after the notice and again after a save (forced).
- `customer_success.client_churned` to broadcast (`*`; finance, sales, executive, data): `client_id`, `client_name`, `amount_gbp`, `reason`, `churn_type`, `service_line`, `tier`, `health_at_churn`, `last_nps`, `post_mortem_due_day`, `summary`.
- No private topic is used: the save deadline is state held by the agent and acted on by `tick()`.

### SLA and controls

- SLA: executive save call within 2 business days; post-mortem within 21 days (15 business days) of churn.
- Control: the save rule in the agent is a deterministic model of the Chief Customer Officer's judgement; in production the CCO decides, and the agent only proposes.
- Control: the Board sees every churn above £250,000 of annual value in the next pack, with the post-mortem summary.

### Exceptions and escalation

- Notice period shorter than 4 days: the deadline is 1 day out and the CEO is informed.
- Client in dispute: no save attempt on commercial terms until Legal confirms the position; the save call concerns service only.
- Notice from a Keep Enterprise client or a client above 10% of revenue (the policy limit is 15%, COMPANY.md §8): the CEO joins the save call.

---

## SOP-CUSTOMER_SUCCESS-11: QBRs and release communications

**Owner**: Customer Success Manager (Chief Customer Officer until Q1 FY2027). Agent: QBR Preparation Agent (from FY2028).
**Trigger**: a quarterly schedule (the first month of each quarter: January, April, July, October) and `product.release_shipped` (a platform release with a `breaking_change` flag).
**Inputs**: Keep clients, tier, adoption and SLA data, support-day drawdown, releases in the quarter, renewal date, `release_id`, `breaking_change`.

### Steps

1. [agent] At the start of each quarter create a QBR task for every non-churned Keep client, once per quarter, due in 21 days (medium priority).
2. [agent] Build the pack: adoption against the success plan, SLA performance, tickets and support-day use (Essential 5 a quarter, Plus 15), releases, value delivered, renewal date and risks.
3. [human] Customer Success Manager reviews the pack, agrees the agenda with the sponsor and holds the QBR. Enterprise clients hold an executive steering committee with the Chief Customer Officer and Delivery lead (COMPANY.md §3.3).
4. [human] Actions are recorded with owners and dates; the next QBR starts with the action review.
5. [agent] On `product.release_shipped`, if the release is breaking, create a change-notice and change-window task for every live Keep client (due in 5 days, high priority). If it is not, create one task to add it to the next QBR packs and the client bulletin (due in 14 days).
6. [human] The Customer Success Manager sends the change notice (reviewed by a human before release), agrees the window with the client and informs the Delivery Keep pod.

### Outputs and messages

- Tasks only for QBRs and release notices; no topic is published directly by this SOP.
- If a QBR exposes a red or amber issue, the rescore messages in SOP-CUSTOMER_SUCCESS-02 and the flag in SOP-CUSTOMER_SUCCESS-06 apply.
- Activity log: `customer_success.activity.release_noted`.

### SLA and controls

- SLA: QBR held within 21 days of quarter start (KPI `qbr_completion_rate` 90% in FY2026); breaking-change notice at least 5 days before the change window.
- Control: material changes to a client-facing agent need an AI risk review (`product.ai_risk_review_requested`, `legal.ai_risk_review_completed`, COMPANY.md §9.4) before a change window is agreed.
- Control: every QBR pack is reviewed by a human before it reaches the client (COMPANY.md §4).

### Exceptions and escalation

- Client declines a QBR twice running: health engagement component drops by the no-contact rule and the Chief Customer Officer calls the executive sponsor.
- Breaking change with client-side dependencies: agree a deferral with Product; where it cannot wait, the Chief Customer Officer informs Sales and Finance of any commercial effect.

---

## SOP-CUSTOMER_SUCCESS-12: Case-study and reference eligibility

**Owner**: Chief Customer Officer (Tobias Lindgren).
**Trigger**: `marketing.case_study_requested` (Marketing asks for a client reference).
**Inputs**: `request_id`, optional `client_id` or `client_name`, `client_consent`, client health, band, last NPS, engagement and Keep status.

### Steps

1. [agent] Identify the client. If the request names none, shortlist eligible clients and pick the one with the highest health score (ties by client id).
2. [agent] Test eligibility: green band, last NPS 9 or above, no open dispute, not churned, and a completed engagement or a live Keep contract. If the client fails, log `customer_success.activity.case_study_declined` with the reason and do not publish.
3. [human] Chief Customer Officer confirms the client is a good public advocate and that no sensitive issue (incident, dispute, negotiation) is in flight.
4. [agent] If consent is missing, create a task to ask the sponsor for consent and Legal sign-off (due in 5 days); no approval is published yet.
5. [human] Customer Success Manager asks the sponsor; General Counsel signs off the wording and the usage scope. The client approves the final text.
6. [agent] With consent recorded, publish `customer_success.case_study_approved` with usage scope `named`, approver Chief Customer Officer and the request id.

### Outputs and messages

- `customer_success.case_study_approved` to broadcast (`*`; marketing): `client_id`, `client_name`, `request_id`, `usage_scope`, `approved_by`, `health_score`, `service_line`, `tier`, `summary`.
- Activity log: `customer_success.activity.case_study_consent_pending`, `case_study_declined`.

### SLA and controls

- SLA: eligibility answer within 5 business days of the request; consent and Legal sign-off within 15 business days.
- Control: nothing is published without the client's written consent and General Counsel sign-off; agents never approve a reference on their own.
- Control: client data in a case study is anonymised unless the usage scope is `named`.

### Exceptions and escalation

- No eligible client: Marketing is told which criterion failed most often so the programme can aim at the next cohort.
- Client withdraws consent after approval: Chief Customer Officer informs Marketing and Legal the same day; Marketing removes the material.

---

## SOP-CUSTOMER_SUCCESS-13: Budget, OKRs, strategy and crisis response

**Owner**: Chief Customer Officer (Tobias Lindgren), with the Chief Financial Officer for the budget cycle.
**Trigger**: `finance.budget_cycle_opened` (annual cycle opens in Q4), `executive.budget_approved` (the approved budget), `executive.okrs_set` (company objectives), `executive.strategy_updated` (strategy change), `executive.crisis_declared` (a declared crisis).
**Inputs**: `budget_id` (such as `BUD-2027`), `fiscal_year`, approved `amount_gbp`, OKRs, strategy summary, crisis summary, current client bands.

### Steps

1. [agent] On `finance.budget_cycle_opened`, derive the fiscal year (from the `budget_id`, else `fiscal_year`), prepare the submission at the COMPANY.md §5.4 envelope: people, non-people, headcount (humans and agents) and the cost-of-revenue flag. Submit once per budget id.
2. [human] Chief Customer Officer reviews the submission against the hiring triggers (clients per named manager, ticket volume, renewal calendar) and the SLA performance of the year.
3. [agent] On `executive.budget_approved`, record the approved budget id and amount.
4. [agent] On `executive.okrs_set`, store the OKRs and create a task to map them to the department KPIs and update targets (due in 10 days). On `executive.strategy_updated`, store the note and create a task to review health weights and playbooks (due in 14 days).
5. [human] Chief Customer Officer maps OKRs to the KPIs in kpis.md, agrees any target change with the CEO, and updates the health weights only with a written reason.
6. [agent] On `executive.crisis_declared`, set crisis mode and create a critical outreach task (due in 1 day) for every non-churned client that is not green or is on Keep Enterprise.
7. [human] Chief Customer Officer and Customer Success Managers call the named sponsors within 1 business day with the approved messages from the crisis lead; Customer Success logs every concern raised.

### Outputs and messages

- `customer_success.budget_submitted` to `finance`: `budget_id`, `department`, `fiscal_year`, `people_gbp`, `non_people_gbp`, `amount_gbp`, `headcount_humans`, `headcount_agents`, `cost_of_revenue` (true), `summary`.
- Tasks: OKR mapping, strategy review, crisis outreach.
- Activity log: `customer_success.activity.budget_approved_noted`, `okrs_noted`, `strategy_noted`, `crisis_mode`.

### SLA and controls

- SLA: budget submitted by the Finance cycle deadline (submissions due day 21 of the cycle); OKR mapping within 10 days; crisis outreach within 1 business day.
- Control: the submission equals the COMPANY.md §5.4 envelope (£140k / £790k / £1,630k) within £5k; any ask above the envelope needs the CFO (non-budgeted spend above £50k) or the CEO (above £250k, COMPANY.md §9.3).
- Control: new headcount outside the approved budget needs `executive.headcount_approved`.

### Exceptions and escalation

- A second `finance.budget_cycle_opened` for the same budget id is ignored.
- Crisis affecting data or the platform: Customer Success follows SOP-CUSTOMER_SUCCESS-09 for the client-facing part and the crisis lead for messaging.

---

## SOP-CUSTOMER_SUCCESS-14: Capacity and hiring

**Owner**: Chief Customer Officer (Tobias Lindgren).
**Trigger**: a weekly schedule (the capacity check runs with the Monday health review and on every new client) and a monthly hiring review on the first day of each month. The topic `customer_success.hire_requested` is the output; the approval path is `people.requisition_opened` and `executive.headcount_approved`.
**Inputs**: active (non-churned) clients, named client managers planned (the CCO counts as one), clients-per-manager ceiling of 22, tickets in the month just ended and their first-response breaches, live Keep clients, Keep renewals in the next 12 months, the year-end headcount plan by role (blueprint.md section 3).

### Steps

1. [agent] Weekly and on every new client: count active clients. Compute named client managers needed = ceil(active clients / 22), at least 1.
2. [agent] If the number needed exceeds the number planned, request the extra Customer Success Managers (level manager).
3. [agent] Monthly, for the month just ended (each month is reviewed once): request the first Client Support Specialist (level consultant) when tickets exceed 30 or live Keep clients exceed 8; an extra specialist when the first-response SLA was below 95% in two consecutive months with tickets; a third when tickets exceed 150; one Renewals and Commercial Manager when Keep renewals in the next 12 months exceed 30.
4. [agent] Headcount plan check on every request: the plan year is the fiscal year in which the seat would start (request day plus 45 days, rounded up to the next quarter start, because seats start at quarter starts). If the role total would exceed the year-end plan for that role, or the department would exceed its year-end humans (1 / 6 / 14), the request is published with `outside_headcount_plan` true and `escalated_to` Chief Executive Officer, and a critical task is created for the CCO to take it to the CEO. It is never held back or dropped.
5. [human] Chief Customer Officer reviews the request against the blueprint triggers (blueprint.md section 5), the approved budget and the pipeline of new logos from Sales. An escalated request needs the CEO's decision (`executive.headcount_approved`) before any requisition proceeds.
6. [human] People opens the requisition (`people.requisition_opened`) and the CEO approves headcount (`executive.headcount_approved`), always for an escalated request and for any hire outside the approved budget.
7. [human] Roles that rest on judgement stay human-triggered by the Chief Customer Officer and are not raised by the agent: Client Support Lead (desk of three plus the Enterprise 24x7 rota), Customer Success Analyst, and the second specialist for the Enterprise rota.

### Outputs and messages

- `customer_success.hire_requested` to `people`: `role_title` (Customer Success Manager, Client Support Specialist or Renewals and Commercial Manager), `level`, `count`, `department`, `trigger`, `plan_year`, `planned_role_headcount`, `role_requested_total`, `planned_department_humans`, `outside_headcount_plan`, `approval_path`, `escalated_to` (only when outside the plan), `summary`; plus `active_clients` and `clients_per_csm_ceiling` (capacity trigger) or `tickets_in_month`, `live_keep_clients`, `first_response_sla_pct` (support trigger) or `renewals_next_12_months`.
- Tasks: escalation to the CEO for a request outside the plan.
- Activity log: `customer_success.activity.hire_escalated`, `monthly_hiring_review`.

### SLA and controls

- SLA: capacity request raised the same sim week the ceiling is crossed; support and renewals requests on the first day of the following month; time-to-hire 45 days (COMPANY.md §8).
- Control: the CCO is counted as the first named client manager; in FY2026 the 23rd active client in the first three quarters raises a Customer Success Manager request that exceeds the FY2026 plan of one human, which is escalated to the CEO for a decision rather than silently ignored. From 18 August 2026 the same request is for a seat starting at the beginning of FY2027 (the blueprint's Q4 FY2026 requisition for Customer Success Manager 1) and is inside the plan.

### Exceptions and escalation

- Hiring slips: Delivery engagement leads cover named-client duties for clients still in a project; the Chief Customer Officer reallocates the largest accounts and informs the CEO.
- Client count falls below the ceiling after churn: the hire is not cancelled automatically; the Chief Customer Officer decides with Finance.

---

## Topic coverage checklist

Subscribed topics and the SOP that is their trigger: `sales.deal_won`, `legal.contract_signed`, `finance.billing_schedule_created`, `delivery.engagement_kickoff` (SOP-CUSTOMER_SUCCESS-01); `delivery.milestone_reached`, `delivery.quality_issue_raised` (SOP-CUSTOMER_SUCCESS-02); `external.client_feedback_submitted` (SOP-CUSTOMER_SUCCESS-03 for support tickets, SOP-CUSTOMER_SUCCESS-04 for NPS, CSAT, complaints and praise); `finance.invoice_issued`, `finance.payment_received`, `finance.invoice_overdue`, `legal.client_dispute_raised` (SOP-CUSTOMER_SUCCESS-05); `sales.renewal_proposal_sent` (SOP-CUSTOMER_SUCCESS-07); `delivery.engagement_completed` (SOP-CUSTOMER_SUCCESS-08); `it_security.incident_detected`, `it_security.data_breach_confirmed`, `it_security.incident_resolved` (SOP-CUSTOMER_SUCCESS-09); `external.client_notice_of_termination` (SOP-CUSTOMER_SUCCESS-10); `product.release_shipped` (SOP-CUSTOMER_SUCCESS-11); `marketing.case_study_requested` (SOP-CUSTOMER_SUCCESS-12); `finance.budget_cycle_opened`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated`, `executive.crisis_declared` (SOP-CUSTOMER_SUCCESS-13).

Published topics and the SOPs whose outputs carry them: `customer_success.health_score_updated` (-01, -02, -03, -04, -05, -08, -09, -10); `customer_success.churn_risk_flagged` (-05, -06, -09, -10); `customer_success.client_churned` (-07, -10); `customer_success.renewal_due` (-07); `customer_success.renewal_confirmed` (-07); `customer_success.expansion_opportunity_identified` (-04, -08); `customer_success.feedback_received` (-04); `customer_success.support_escalated` (-03); `customer_success.case_study_approved` (-12); `customer_success.budget_submitted` (-13); `customer_success.hire_requested` (-14).
