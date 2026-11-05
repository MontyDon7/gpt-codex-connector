# Legal Standard Operating Procedures

Department: `legal` (agent class `LegalAgent`). Head: Callum Fraser, General Counsel (COMPANY.md §9.2). Scope: commercial contracts, data protection and breach response, regulatory change, AI-risk review, disputes, vendor and people legal support, IP and brand, corporate governance. UK context: UK GDPR and the Data Protection Act 2018 (DPA 2018), ICO breach reporting within 72 hours (UK GDPR Art 33), Late Payment of Commercial Debts (Interest) Act 1998, Companies Act 2006 and Companies House, IR35 off-payroll rules, EU AI Act alignment. All figures are modelled assumptions, not real data.

**This department never gives binding legal advice.** In FY2026 there is one human lawyer, the General Counsel, so segregation of duties is achieved by agent-prepares / General Counsel-decides. Conventions used throughout:

- `[human]` steps are performed by the General Counsel (from Q2 FY2027 Commercial and Privacy Counsel may perform fallback-level steps; escalate-level and ICO decisions stay with the General Counsel). `[agent]` steps are performed by the Legal agent under the General Counsel as accountable owner. Agents may draft, analyse, monitor and propose; they may not sign contracts, notify regulators, send letters before action, or approve payments above £10,000 (COMPANY.md §9.4). Every agent output that carries a judgement has `advice_status: draft_for_human_lawyer_review` and `escalated_to: General Counsel` plus a disclaimer.
- Money in message bodies is `amount_gbp` ex VAT. Sim days are integers from Day 0 = 2026-01-05 (COMPANY.md §1); `due_day` keys are sim days.
- Business IDs follow CONVENTIONS section 4 (`CT-0001`, `DL-0001`, `CL-0001`, `INC-0001`, `VN-0001`, `EN-0001`, `INV-2026-0001`, `BUD-2027`). Legal-owned IDs: matter `MTR-0001`, compliance finding `CF-0001`, policy `POL-001`, AI review `AIR-001`, ICO filing ref `LEGAL-ICO-0001`.

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-LEGAL-01 | Deal won to contract and signature | `sales.deal_won`, `executive.deal_decision_made` | General Counsel (agent: contract desk) | Draft within 3 days; signed within 7 days of deal won |
| SOP-LEGAL-02 | Contract playbook and non-standard terms | `sales.deal_approval_requested` | General Counsel | Pre-approval review within 1 day; GC decision within 24 hours |
| SOP-LEGAL-03 | Security terms and certification warranties | `sales.security_review_requested`, `it_security.security_questionnaire_completed`, `it_security.certification_status_updated` | General Counsel (with CISO) | Security terms reviewed within 2 days |
| SOP-LEGAL-04 | Renewals and change orders | `customer_success.renewal_due`, `sales.renewal_proposal_sent`, `customer_success.renewal_confirmed`, `delivery.scope_change_requested` | General Counsel (Commercial and Privacy Counsel from Q2 FY2027) | Renewal draft within 3 days; change order drafted within 2 days |
| SOP-LEGAL-05 | Personal data breach and 72-hour ICO notification | `it_security.incident_detected`, `it_security.data_breach_confirmed`, `it_security.incident_resolved`, `executive.crisis_declared` | General Counsel (with CISO and CEO) | Matter opened within 1 day; ICO report within 72 hours of awareness |
| SOP-LEGAL-06 | Regulatory change, compliance findings and policy | `external.regulation_published`, `operations.compliance_action_completed`, `people.compliance_training_completed` | General Counsel | Triage within 2 days; policy update on closure of finding |
| SOP-LEGAL-07 | AI risk review | `product.ai_risk_review_requested` | General Counsel (Privacy and Regulatory Counsel from Q1 FY2028) | Review within 5 days |
| SOP-LEGAL-08 | Overdue invoices, disputes and letters before action | `finance.invoice_overdue`, `finance.collections_escalated` | General Counsel | Position note same day; letter reviewed within 3 days |
| SOP-LEGAL-09 | Vendor, contractor and employment legal support | `operations.vendor_review_requested`, `it_security.vendor_risk_assessed`, `people.contractor_engaged`, `people.offer_accepted`, `people.employee_left`, `it_security.access_revoked` | General Counsel (Commercial and Privacy Counsel from Q2 FY2027) | Vendor review within 5 days; employment documents within 3 days |
| SOP-LEGAL-10 | Brand, IP and misleading-claim incidents | `marketing.brand_incident_raised` | General Counsel | Triage within 1 day |
| SOP-LEGAL-11 | Governance, board and strategy | `executive.board_meeting_held`, `executive.okrs_set`, `executive.strategy_updated` | General Counsel | Minutes and registers within 10 days; Companies House within 14 days |
| SOP-LEGAL-12 | Budget, hiring and compliance calendar | `finance.budget_cycle_opened`, `executive.budget_approved`; monthly schedule (first day of month) | General Counsel | Budget submitted in the cycle; hire request in month of requisition |
| SOP-LEGAL-13 | Data subject access requests and privacy register | On receipt of a DSAR (manual intake) and weekly schedule | General Counsel (Commercial and Privacy Counsel from Q2 FY2027) | Closed within one month (UK GDPR Art 12(3)) |

Topic coverage: every subscribed topic is named in the Trigger of at least one SOP above, and every topic published by `legal` (`legal.ai_risk_review_completed`, `legal.budget_submitted`, `legal.client_dispute_raised`, `legal.compliance_finding_raised`, `legal.contract_drafted`, `legal.contract_risk_flagged`, `legal.contract_signed`, `legal.hire_requested`, `legal.policy_update_published`, `legal.regulator_notification_filed`, `legal.regulatory_change_noted`, `legal.security_terms_reviewed`) appears in the outputs of at least one SOP.

## Policy constants (single definition, mirrored in `agent.py`)

| Constant | Value | Source |
|---|---|---|
| CEO approval deal threshold | >= £500,000 total contract value (`DEAL_CEO_THRESHOLD_GBP`) | COMPANY.md §9.3 |
| Board approval deal threshold | > £1,500,000 (`DEAL_BOARD_THRESHOLD_GBP`) | COMPANY.md §9.3 |
| Standard payment terms | net 30 (`STANDARD_PAYMENT_DAYS`) | COMPANY.md §7 |
| Fallback payment terms | net 31 to 45, Finance head (CFO) and CEO approve (`FALLBACK_PAYMENT_DAYS` = 45); beyond 45 is escalate | COMPANY.md §9.3 |
| Keep minimum term | 12 months (`KEEP_MIN_TERM_MONTHS`) | COMPANY.md §3.3 |
| Keep uplift | CPI + 2.0% (`KEEP_UPLIFT_ADD_PCT`), cap 7.0% (`KEEP_UPLIFT_CAP_PCT`); planning CPI 3.0% if none supplied (`PLANNING_CPI_PCT`) | COMPANY.md §7; economics.md section 4 |
| Discount limit | 10% (`DEFAULT_DISCOUNT_LIMIT_PCT`); above needs Finance head and CEO | COMPANY.md §9.3 |
| ICO notification deadline | 72 hours (`ICO_DEADLINE_HOURS`) from awareness | UK GDPR Art 33(1); COMPANY.md §9.3 |
| Client (controller) breach notice standard | 48 hours (`CLIENT_BREACH_NOTICE_HOURS`) | Playbook |
| Signature lead time | standard 3 days, fallback 5, escalated 5 (`SIGNATURE_LEAD_DAYS`) | Playbook |
| Late payment interest | base rate 4.0% (`BASE_RATE_PCT`) + 8.0% (`LATE_PAYMENT_MARGIN_PCT`) | COMPANY.md §7; economics.md section 4 |
| Late payment fixed compensation | £40 under £1,000; £70 from £1,000 to under £10,000; £100 from £10,000 | Late Payment Act 1998 |
| Compliance training target | 95% (`TRAINING_TARGET_PCT`) | kpis.md |
| Regulation severity by days to effect | <= 30 critical; <= 90 high; <= 365 medium; otherwise low (default 180 days) | Playbook |
| Dispute severity by amount | >= £500,000 critical; >= £100,000 high; otherwise medium | Playbook |
| Rate card | Partner £2,400; Principal £1,800; Manager £1,400; Senior Consultant £1,050; Consultant £800; Analyst £550; AI agent-day £350 (`RATE_CARD_GBP`) | COMPANY.md §3.5 |

### Contract playbook (clause positions)

| Clause | Standard | Fallback (General Counsel approves) | Escalate (General Counsel and CEO) |
|---|---|---|---|
| Liability cap | Aggregate cap 100% of fees paid or payable in the 12 months before the claim (`liability_cap_multiple` <= 1.0) | Cap above 1.0x and up to 2.0x annual fees; super-cap for data protection breach | Above 2.0x annual fees, or uncapped (`uncapped_liability`) |
| Payment terms | Net 30 | Net 31 to 45 with CFO and CEO approval | Beyond net 45, pay-when-paid, set-off |
| IP ownership | Client owns bespoke deliverables on payment; Lumenhall keeps background IP, tools and agents (`ip_ownership: standard`) | `licensed_back`: as standard plus perpetual licence-back of non-confidential learnings | Any other value, e.g. `client_owns_all` (assignment including Lumenhall background IP) |
| Data terms | Lumenhall UK GDPR Art 28 DPA; UK IDTA or Addendum for transfers (`standard_dpa`) | `client_dpa`: client paper reviewed against the Art 28 checklist | No DPA, unreviewed controller-to-controller terms, unlimited data liability |
| Governing law | England and Wales | New York or Delaware for contracts with Lumenhall Partners Inc. only (from FY2027) | Any other law or exclusive foreign jurisdiction |
| Keep minimum term | 12 months | None | Below 12 months or termination for convenience inside the term |

Overall position of a contract = `escalated` if any clause escalates, else `fallback` if any falls back, else `standard`. Human review level: `full_review` if the position is not standard or the amount is >= £500,000, otherwise `sample_check`.

---

## SOP-LEGAL-01: Deal won to contract and signature

**Owner**: General Counsel, with the Legal agent as contract desk. Commercial and Privacy Counsel from Q2 FY2027; Contracts Specialist for logistics from Q3 FY2027.
**Trigger**: `sales.deal_won` (the deal is won and the contract is needed) and `executive.deal_decision_made` (the CEO or Board decision on a deal >= £500k or with non-standard terms).
**Inputs**: `deal_id`, `client_id`, `client_name`, `amount_gbp`, `service_line`, `tier`, `terms` (`liability_cap_multiple` or `uncapped_liability`, `payment_days`, `ip_ownership`, `data_terms`, `governing_law`, `min_term_months`), `contract_id` if pre-assigned, `engagement_id` if any; the contract playbook; the approvals matrix (COMPANY.md §9.3); any earlier `sales.deal_approval_requested` terms and `decision`.

### Steps

1. [agent] On `sales.deal_won`, choose the paper: MSA plus SOW for Compass and Forge, order form for Keep (`service_line` = `keep`). Allocate `CT-NNNN` unless one was supplied.
2. [agent] Compare each supplied term with the playbook (table above) and compute the overall position (standard / fallback / escalated) and highest severity.
3. [agent] Work out pending approvals: CEO if `amount_gbp` >= £500,000 and no approved decision; General Counsel and CEO if escalated and no approved decision; Board if `amount_gbp` > £1,500,000 and no Board approval flag.
4. [agent] If the position is escalated and the deal has not yet been flagged, emit `legal.contract_risk_flagged` (blocking) before the draft.
5. [agent] Emit `legal.contract_drafted` with `playbook_position`, `findings`, `approvals_required`, `billing_terms` (30/40/30 milestones with expenses at cost capped at 5% for Compass and Forge; monthly in advance with 12-month minimum for Keep; COMPANY.md §7), `human_review` level and `due_day` = today + signature lead time (3 / 5 / 5 days). Open a human review task due in 3 days (standard) or 2 days (fallback and escalated).
6. [human] General Counsel reviews: sample check for standard paper under £500k; full review otherwise. Records approvals (fallback: General Counsel; escalated: General Counsel and CEO; payment terms 31 to 45: CFO and CEO).
7. [agent] On `executive.deal_decision_made`, record the decision (`approved`, `rejected` or unclear). If approved, clear CEO/General Counsel approvals (a Board approval is only cleared by a `board_approved` flag); if rejected, cancel the contract.
8. [human] When no approvals are pending the contract is `awaiting_signature`; the authorised signatory (a human, never the agent) executes it. The agent models this as an internal confirmation after the signature lead time.
9. [agent] Emit `legal.contract_signed` with `signed_day`, `days_from_draft`, `signatories`, `billing_terms`, `payment_terms_days` = 30, `minimum_term_months` = 12 for Keep, and `work_may_start` = true. Finance builds the billing schedule from this and Delivery may kick off.

### Outputs and messages

- `legal.contract_drafted` (broadcast): `contract_id`, `deal_id`, `client_id`, `client_name`, `amount_gbp`, `service_line`, `tier`, `contract_type`, `playbook_position`, `status`, `approvals_required`, `findings`, `billing_terms`, `human_review`, `due_day`, `summary`, plus advice markers.
- `legal.contract_signed` (broadcast; Finance, Delivery, Sales, Customer Success): `contract_id`, `deal_id`, `client_id`, `client_name`, `amount_gbp`, `service_line`, `tier`, `signed_day`, `days_from_draft`, `payment_terms_days`, `billing_terms`, `work_may_start`, `summary`.
- `legal.contract_risk_flagged` (broadcast; Sales, Executive): when the position is escalated (see SOP-LEGAL-02).

### SLA and controls

- Draft within 3 days of `sales.deal_won`; signed within 7 days (KPIs `contract_turnaround_days`, `deal_won_to_signed_days`).
- No signature without recorded approvals; agents never sign (COMPANY.md §9.4). Work may not start until `legal.contract_signed`.
- Weekly Monday matter review lists contracts in `pending_approval` and `awaiting_signature`.

### Exceptions and escalation

- Deal >= £500k without a CEO decision: the contract stays `pending_approval`; the General Counsel chases the CEO via `sales.deal_approval_requested` / `executive.deal_decision_made`.
- Missing `terms`: the agent uses terms recorded at approval time; if none, it drafts from the playbook standard and flags `findings` empty for human completion.
- Client rejects the draft: the General Counsel negotiates within the playbook; any move to escalate returns to SOP-LEGAL-02.

---

## SOP-LEGAL-02: Contract playbook and non-standard terms

**Owner**: General Counsel (accountable for the playbook; reviewed annually in January).
**Trigger**: `sales.deal_approval_requested` (Sales asks for approval of a deal of >= £500k or one with non-standard terms).
**Inputs**: `deal_id`, `client_id`, `amount_gbp`, `service_line`, `terms`, client paper if any, the playbook table above.

### Steps

1. [agent] Store the `terms` against the `deal_id`, compute the playbook position per clause and overall position.
2. [agent] Open a task "Pre-approval legal review of deal" due in 1 day (priority high).
3. [agent] If any clause is `escalate` (uncapped liability, liability above 2.0x, `client_owns_all` IP, no DPA or non-standard data terms, other governing law, beyond net 45, Keep term under 12 months), emit `legal.contract_risk_flagged` with `blocking` true, `findings`, `required_approvers` and the recommendation "do not sign without General Counsel and CEO approval".
4. [human] General Counsel reviews the flag within 24 hours and advises the CEO. Options: reject, accept with mitigation (for example liability super-cap, insurance backing, shorter term), or approve (General Counsel and CEO under COMPANY.md §9.3).
5. [human] CEO records the decision through `executive.deal_decision_made`; Board approval is also required if the deal exceeds £1.5m (COMPANY.md §9.1, §9.3).
6. [agent] Keep the position on the contract record so `playbook_adherence_pct` and `non_standard_liability_pct` can be computed.

### Outputs and messages

- `legal.contract_risk_flagged`: `deal_id`, `client_id`, `contract_id` (empty before drafting), `amount_gbp`, `severity` (`low`, `medium`, `high` or `critical`; `critical` for uncapped liability), `blocking`, `findings` (clause, requested, position, severity, approvers, playbook text), `required_approvers`, `recommendation`, `summary`.

### SLA and controls

- Pre-approval review within 1 day; General Counsel decision within 24 hours (KPI `gc_escalation_response_hours`). A deal is flagged once only.
- Target: at most 10% of signed contracts with liability above 100% of annual fees or uncapped in FY2026 (KPI `non_standard_liability_pct`).

### Exceptions and escalation

- General Counsel unavailable: no deputy can approve escalate-level terms in FY2026; the CEO may defer the deal or ask outside counsel to advise and the General Counsel to ratify. From Q2 FY2027 Commercial and Privacy Counsel may approve fallback-level terms only.
- Disagreement between Sales and Legal: the CEO decides with the General Counsel's written risk note; the decision is recorded in the contract file.

---

## SOP-LEGAL-03: Security terms and certification warranties

**Owner**: General Counsel, with the CISO (Wei Zhang, COMPANY.md §9.2) for technical commitments.
**Trigger**: `sales.security_review_requested`, `it_security.security_questionnaire_completed` and `it_security.certification_status_updated`.
**Inputs**: `deal_id`, `client_id`, `requested_breach_notice_hours`, `audit_rights`, `certs_required` (for example `iso_27001`, `cyber_essentials_plus`, `soc2_type2`), `open_gaps` (questionnaire), `certification` and `status`; the certification register (ISO 27001 and Cyber Essentials Plus targeted for FY2026, SOC 2 Type II FY2027, COMPANY.md §8).

### Steps

1. [agent] On `sales.security_review_requested`, compare the requested breach-notice period with the standard: 48 hours or longer is standard; 24 to under 48 hours is fallback (General Counsel and CISO); under 24 hours is escalate (General Counsel, CISO and CEO). The statutory ICO limit stays 72 hours regardless.
2. [agent] Check `audit_rights`: `annual` or `on_incident` is standard; anything else (for example `unrestricted`) escalates to the General Counsel.
3. [agent] For each `certs_required`, check the register; any certification not `achieved` is a fallback finding: do not warrant it, give a roadmap date instead.
4. [agent] Include the questionnaire status (`not_received`, `completed`, `completed_with_gaps`) and emit `legal.security_terms_reviewed`; open a "General Counsel sign-off on security terms" task due in 2 days.
5. [human] General Counsel and CISO approve the response to the client and which warranties may appear in the contract.
6. [agent] On `it_security.security_questionnaire_completed`, record the status; if `open_gaps` > 0, open a task to review gaps against contract warranties (due 2 days).
7. [agent] On `it_security.certification_status_updated`, update the register. If the status is one of `lapsed`, `suspended`, `audit_failed`, `expired`, `withdrawn` and signed contracts warrant that certification, emit `legal.contract_risk_flagged` (not blocking) listing the affected contracts.
8. [human] General Counsel decides on client notice and remediation before any client contact.

### Outputs and messages

- `legal.security_terms_reviewed` (broadcast; Sales): `deal_id`, `client_id`, `findings`, `certifications`, `questionnaire_status`, `open_items`, `status` (`escalated_to_gc` or `reviewed_pending_gc_signoff`), `summary`.
- `legal.contract_risk_flagged`: `severity` high, `blocking` false, `certification`, `status`, `affected_contracts`, `contract_id`, `recommendation`, `summary`.

### SLA and controls

- Review within 2 days of the request. No certification is warranted unless its status is `achieved` in the register.

### Exceptions and escalation

- Client demands an unachieved certification as a condition of signature: escalate to General Counsel and CISO; Sales may offer a dated roadmap, never a false warranty.
- Lapsed certification with live warranties: General Counsel assesses contractual notice duties with outside counsel; CEO informed.

---

## SOP-LEGAL-04: Renewals and change orders

**Owner**: General Counsel (Commercial and Privacy Counsel from Q2 FY2027).
**Trigger**: `customer_success.renewal_due`, `sales.renewal_proposal_sent`, `customer_success.renewal_confirmed` and `delivery.scope_change_requested`.
**Inputs**: `client_id`, `client_name`, `contract_id`, `amount_gbp`, `tier`, `cpi_pct`, `uplift_pct`, `discount_pct`, `engagement_id`, `days_by_level` (change order days by rate-card level) or `amount_gbp`.

### Steps

1. [agent] On `customer_success.renewal_due`, compute the permitted uplift = min(CPI + 2.0%, 7.0%) with planning CPI 3.0% when absent, and the renewed annual value = current x (1 + uplift). Open a renewal contract (status `awaiting_client_confirmation`) and emit `legal.contract_drafted`.
2. [agent] On `sales.renewal_proposal_sent`, check `uplift_pct` against the 7.0% cap and `discount_pct` against 10%. If either is breached, emit `legal.contract_risk_flagged` (medium, not blocking) so the proposal is corrected.
3. [human] General Counsel or Commercial and Privacy Counsel reviews the renewal paper; a Keep term under 12 months or termination for convenience in the term is escalate.
4. [agent] On `customer_success.renewal_confirmed`, mark the renewal `awaiting_signature`, record the confirmed `amount_gbp`, and, as the human signatory executes, emit `legal.contract_signed` (with `minimum_term_months` 12).
5. [agent] On `delivery.scope_change_requested`, price the change order from `days_by_level` at the rate card (COMPANY.md §3.5) unless `amount_gbp` is given, open a `change_order` contract linked to `parent_contract_id` and the `engagement_id`, and emit `legal.contract_drafted` (rate-card basis; signed before work starts, COMPANY.md §7).
6. [human] The change order is signed before work starts; Delivery must not begin the extra work until `legal.contract_signed`.

### Outputs and messages

- `legal.contract_drafted`: for the renewal (`renewal`, `uplift_pct`, `renewal_amount_gbp`, `previous_contract_id`) and for the change order (`parent_contract_id`, `rate_card_basis`, `engagement_id`).
- `legal.contract_risk_flagged`: over-cap uplift or discount above 10% on a renewal proposal.
- `legal.contract_signed`: for the executed renewal or change order.

### SLA and controls

- Renewal draft within 3 days of `renewal_due`; change order drafted within 2 days; uplift never above 7.0% without General Counsel and CEO approval.

### Exceptions and escalation

- Client refuses any uplift: Customer Success and Sales negotiate; Legal confirms the contract terms; a below-CPI renewal is a commercial decision for the CRO and CFO, not Legal.
- Scope change without a signed change order: work stops and the matter goes to the General Counsel (revenue at risk for Finance).

---

## SOP-LEGAL-05: Personal data breach and 72-hour ICO notification

**Owner**: General Counsel, with the CISO and the CEO (COMPANY.md §9.3). Outside counsel breach panel on 24-hour call-out.
**Trigger**: `it_security.incident_detected`, `it_security.data_breach_confirmed`, `it_security.incident_resolved` and `executive.crisis_declared`.
**Inputs**: `incident_id`, `severity`, `personal_data_involved`, `records_affected`, `special_category`, `risk_to_individuals`, `lumenhall_role` (`controller` or `processor`), `aware_day`, `client_id`.

### Steps

1. [agent] On `it_security.incident_detected`, open a privileged matter (`MTR-NNNN`) and tasks: "open privileged matter; route all communications via counsel" (due 1 day) and, if personal data is involved, "preliminary personal data breach assessment" (due 1 day, critical).
2. [agent] On `it_security.data_breach_confirmed`, record the breach in the register (UK GDPR Art 33(5)) with `aware_day` and `deadline_day` = `aware_day` + 3 days (72 hours). Risk to individuals defaults to `high` if special category data or 1,000 or more records, otherwise `likely`.
3. [agent] Decide the route: `notifiable` = risk is `likely` or `high` and Lumenhall is controller. If Lumenhall is processor, open a task to notify the controller client within 48 hours (critical). If risk is `high`, open a data-subject communication task (UK GDPR Art 34, due 2 days).
4. [human] General Counsel with the CISO and the CEO decide and file the ICO report (UK GDPR Art 33; phased report allowed under Art 33(4) if facts are incomplete). The agent opens a critical task and schedules the filing confirmation 1 day out.
5. [agent] A daily deadline watch logs a warning when the breach is within 24 hours of the limit and a critical alert if the limit passes unfiled.
6. [agent] On the filing confirmation, emit `legal.regulator_notification_filed` with `filing_ref`, `deadline_hours` 72, `hours_elapsed`, `within_72h`, `risk_to_individuals`, `data_subjects_to_be_told`, `phased_report`, `severity` (critical if risk is high, otherwise high) and `filed_by` the General Counsel (human). If late, include `reason_for_delay`.
7. [agent] On `it_security.incident_resolved`, close the matter and open a privileged post-incident review task due in 14 days; log if a notifiable breach is still unfiled.
8. [agent] On `executive.crisis_declared`, open "issue legal hold and stand up privileged crisis channel" (due same day, critical) and log open breaches.
9. [human] General Counsel updates the breach register, notifies insurers (cyber policy) via Finance, and decides on client contractual notices.

### Outputs and messages

- `legal.regulator_notification_filed` (broadcast; Executive, IT Security): `incident_id`, `client_id`, `regulator` = ICO, `filing_ref`, `deadline_hours`, `hours_elapsed`, `within_72h`, `risk_to_individuals`, `data_subjects_to_be_told`, `phased_report`, `severity`, `filed_by`, `advice_status`, `summary`.

### SLA and controls

- Matter opened within 1 day; ICO report within 72 hours of awareness (KPI `breach_notification_within_72h_pct` = 100%); client controller notice within 48 hours where Lumenhall is processor.
- Agents never notify the regulator (COMPANY.md §9.4); only the General Counsel files. Comms about the incident run under privilege.

### Exceptions and escalation

- Facts unclear at hour 48: file a phased report; do not wait for completeness.
- General Counsel unreachable: CEO and outside counsel panel file; the General Counsel ratifies.
- Not notifiable (unlikely risk): the decision and reasoning are recorded in the breach register and signed by the General Counsel.

---

## SOP-LEGAL-06: Regulatory change, compliance findings and policy

**Owner**: General Counsel (Privacy and Regulatory Counsel from Q1 FY2028).
**Trigger**: `external.regulation_published`, `operations.compliance_action_completed` and `people.compliance_training_completed`.
**Inputs**: `regulation_id`, `title`, `jurisdiction`, `regulator`, `effective_in_days`, `summary`; `finding_id`, `policy_update_required`; training `course` and `completion_pct`.

### Steps

1. [agent] On `external.regulation_published`, classify impact areas by keyword: data protection (UK GDPR, ICO, DSAR), AI governance (AI Act, algorithm), employment, cyber security, tax, financial crime; owners: data protection to IT Security, Data, People, Operations; AI governance to Product and Data; employment to People; cyber to IT Security and Operations; tax and general to Operations.
2. [agent] Set severity from `effective_in_days`: <= 30 critical, <= 90 high, <= 365 medium, else low (default 180 when absent). Emit `legal.regulatory_change_noted` and open a General Counsel review task due in 2 days.
3. [agent] If severity is high or critical, raise `CF-NNNN` and emit `legal.compliance_finding_raised` with `action_owner`, `due_day` = today + min(`effective_in_days`, 60).
4. [human] General Counsel reviews the impact note and decides whether a policy change is needed.
5. [agent] On `operations.compliance_action_completed`, close the finding. If `policy_update_required` or the finding was marked as likely to need a policy (data protection, AI governance, employment, financial crime, cyber), publish a policy update: `POL-NNN`, version, `effective_day` = today + 14, training required for all staff. [human] General Counsel approves the wording before it goes live.
6. [agent] On `people.compliance_training_completed`, record the course completion. Below 95% opens a chase task due in 7 days.

### Outputs and messages

- `legal.regulatory_change_noted` (broadcast; Executive, IT Security, People, Operations, Data, Product): `regulation_id`, `title`, `jurisdiction`, `impact_areas`, `owners`, `effective_in_days`, `severity`, `policy_update_likely`, `llm_note`, `summary`.
- `legal.compliance_finding_raised` (broadcast; Executive, Operations): `finding_id`, `severity`, `title`, `areas`, `action_owner`, `due_day`, `summary`.
- `legal.policy_update_published` (broadcast; People, Operations, IT Security): `policy_id`, `title`, `version`, `finding_id`, `effective_day`, `training_required`, `audiences`, `summary`.

### SLA and controls

- Triage within 2 days (KPI `regulatory_triage_days`); compliance training completion of at least 95% (KPI `compliance_training_completion_pct`); quarterly regulatory horizon review in January, April, July and October.

### Exceptions and escalation

- Ambiguous law or conflicting regimes (for example UK versus EU AI Act obligations): General Counsel takes outside counsel advice; interim position recorded in the finding.
- Finding overdue past `due_day`: escalated to the COO (Beatrice Moreau) and reported to the Audit and Risk Committee.

---

## SOP-LEGAL-07: AI risk review

**Owner**: General Counsel (Privacy and Regulatory Counsel from Q1 FY2028); AI Risk Review Agent from FY2028.
**Trigger**: `product.ai_risk_review_requested` (material changes to client-facing agents need review, COMPANY.md §9.4).
**Inputs**: `review_id`, `agent_name`, `client_id`, `use_case_tags`, `uses_personal_data`, `automated_decisions`, `client_facing`, `eu_exposure`, `affects_employment`, `large_scale`.

### Steps

1. [agent] Tier the use case: `prohibited` (social scoring, workplace emotion recognition, untargeted face scraping, subliminal manipulation); `high_risk` (employment, worker management, credit scoring, education, essential services, biometric identification, law enforcement, critical infrastructure, safety component); `limited_risk` (client-facing, chatbot, synthetic content); otherwise `minimal_risk`.
2. [agent] Build conditions: named human oversight owner in the agent register; audit logging of outputs in client deliverables; for high risk, risk management, data governance, logging and human oversight controls plus a confirmed provider/deployer role; AI disclosure for limited and high risk; DPIA (UK GDPR Art 35) when personal data is used and the use is automated, high risk or large scale; human review route for significant automated decisions (UK GDPR Art 22); EU applicability check if `eu_exposure`.
3. [agent] Recommendation: `blocked_pending_gc` for prohibited, `cleared_with_conditions` if there are more than two conditions, otherwise `cleared_subject_to_standard_controls`. Open a sign-off task for the General Counsel due in 3 days.
4. [agent] Emit `legal.ai_risk_review_completed` with `status` = `recommendation_pending_gc_signoff`.
5. [human] General Counsel signs off or amends the recommendation. A prohibited or high-risk system is never released on the agent's recommendation alone.

### Outputs and messages

- `legal.ai_risk_review_completed` (broadcast; Product, Executive): `review_id`, `agent_name`, `client_id`, `risk_tier`, `dpia_required`, `conditions`, `recommendation`, `status`, `severity` (high for high_risk or prohibited, else low), `llm_note`, `summary`.

### SLA and controls

- Review within 5 days of the request (KPI `ai_risk_review_days`); recommendation to Product is always marked pending General Counsel sign-off.

### Exceptions and escalation

- Prohibited practice: block, notify the CPO (Anika Rao) and CEO, and record in the legal risk register.
- Client-owned AI system: Lumenhall's role (provider or deployer) is confirmed by the human lawyer and the client contract's AI clauses are reviewed.

---

## SOP-LEGAL-08: Overdue invoices, disputes and letters before action

**Owner**: General Counsel, with the CFO (Hannah Whitcombe) for the collections ladder.
**Trigger**: `finance.invoice_overdue` and `finance.collections_escalated` (collections ladder: reminder day 31, call day 38, finance-head escalation day 45, legal letter day 60, COMPANY.md §7).
**Inputs**: `invoice_id`, `client_id`, `client_name`, `amount_gbp`, `days_overdue`, `disputed`, `engagement_id`.

### Steps

1. [agent] On `finance.invoice_overdue`, compute the statutory position: interest = amount x (4.0% + 8.0%) x days / 365 and the fixed compensation (£40 / £70 / £100 by invoice size). Log it. If `days_overdue` is 45 or more, open a task to prepare a letter before action (due 5 days).
2. [agent] On `finance.collections_escalated` (day 60), draft the letter before action with interest and fixed compensation and open a task for the General Counsel to review and send, with 14 days for the client to respond (due 3 days).
3. [agent] If the invoice is `disputed`, open a privileged client-dispute matter (legal hold on, no admissions) and emit `legal.client_dispute_raised` with severity by amount (>= £500,000 critical, >= £100,000 high, otherwise medium).
4. [human] General Counsel decides the strategy: without-prejudice discussion and mediation before any claim; the General Counsel sends the letter, never the agent.
5. [human] CFO and Customer Success agree commercial concessions; Legal records any settlement in writing.

### Outputs and messages

- `legal.client_dispute_raised` (broadcast; Finance, Delivery, Executive): `matter_id`, `client_id`, `client_name`, `invoice_id`, `engagement_id`, `amount_gbp`, `severity`, `legal_hold`, `privileged`, `communication_guidance`, `next_step`, `summary`.

### SLA and controls

- Statutory position noted same day; letter reviewed within 3 days of day 60. Delivery pauses non-contractual extra work while a dispute is open, subject to the General Counsel's view of the contract.

### Exceptions and escalation

- Dispute above £500,000: CEO informed same day; outside counsel instructed (non-budgeted spend rules apply, COMPANY.md §9.3).
- Client insolvency signals: General Counsel advises Finance on proof of debt and set-off.

---

## SOP-LEGAL-09: Vendor, contractor and employment legal support

**Owner**: General Counsel (Commercial and Privacy Counsel from Q2 FY2027).
**Trigger**: `operations.vendor_review_requested`, `it_security.vendor_risk_assessed`, `people.contractor_engaged`, `people.offer_accepted`, `people.employee_left` and `it_security.access_revoked`.
**Inputs**: `vendor_id`, `vendor_name`, `processes_personal_data`, `has_dpa`, `data_outside_uk_eea`, `transfer_mechanism`, `risk_rating`; `contractor_id`, `contractor_name`; `candidate_name`, `employee_id`.

### Steps

1. [agent] On `operations.vendor_review_requested`, record the vendor facts and open a contract review task (DPA, liability, exit; due 5 days). Run the vendor checks: no Art 28 DPA where personal data is processed; restricted transfer outside the UK/EEA without IDTA, Addendum or adequacy; security risk rating high or critical.
2. [agent] On `it_security.vendor_risk_assessed`, add the risk rating and re-run the checks.
3. [agent] If there are issues and no finding has been raised for the vendor, emit `legal.compliance_finding_raised` (severity high, `action_owner` operations, `due_day` + 10, `issues` list). Operations may not approve the vendor until the finding is closed.
4. [agent] On `people.contractor_engaged`, open a task for the contractor agreement and IR35 status (confidentiality, IP assignment, data terms); from FY2027 issue a Status Determination Statement.
5. [agent] On `people.offer_accepted`, open a task for the employment contract, written particulars and right-to-work check before the start date (due 3 days), with restrictive covenants by level and IP assignment.
6. [agent] On `people.employee_left`, record the leaver and open a leaver check (covenants, confidentiality, return of property; due 5 days). On `it_security.access_revoked`, file the access-revocation evidence to the matter.
7. [human] General Counsel or Commercial and Privacy Counsel signs off vendor contracts and contractor agreements; an employment lawyer (outside counsel) reviews any dismissal or restrictive covenant dispute.

### Outputs and messages

- `legal.compliance_finding_raised`: `finding_id`, `vendor_id`, `severity`, `areas` (data_protection), `issues`, `action_owner`, `due_day`, `summary`.

### SLA and controls

- Vendor review within 5 days; employment documents within 3 days; no personal data processed by a vendor without a signed DPA.

### Exceptions and escalation

- Vendor refuses a DPA: escalate to the General Counsel and the CISO; use an alternative vendor or an agreed CISO exception.
- High-risk transfers: transfer risk assessment by outside counsel before approval.

---

## SOP-LEGAL-10: Brand, IP and misleading-claim incidents

**Owner**: General Counsel, with the CMO (Sofia Lindqvist) for brand matters.
**Trigger**: `marketing.brand_incident_raised`.
**Inputs**: `category` (for example `misleading_claim`, `data_exposure`, `trade_mark`, `impersonation`), `severity`, `summary`, evidence links.

### Steps

1. [agent] Open a high-priority task: preserve evidence, General Counsel decides on notice or takedown (due 1 day).
2. [agent] If the category is `misleading_claim` or `data_exposure`, raise a compliance finding (marketing compliance, `action_owner` operations, due in 5 days) and emit `legal.compliance_finding_raised`.
3. [human] General Counsel decides: cease-and-desist, platform takedown, trade mark filing, correction or withdrawal of the claim (CAP code and Consumer Protection from Unfair Trading regulations for advertising claims).
4. [human] If personal data is exposed, hand off to SOP-LEGAL-05.

### Outputs and messages

- `legal.compliance_finding_raised`: `finding_id`, `severity`, `areas` (marketing_compliance), `action_owner`, `due_day`, `summary`.

### SLA and controls

- Triage within 1 day; correction of a misleading claim within 5 days.

### Exceptions and escalation

- Claim about a named client or a client's data: General Counsel and the client's account owner decide jointly; no public statement without CEO approval.

---

## SOP-LEGAL-11: Governance, board and strategy

**Owner**: General Counsel (company secretarial role).
**Trigger**: `executive.board_meeting_held`, `executive.okrs_set` and `executive.strategy_updated`.
**Inputs**: `meeting_id`, `resolutions`, `okrs`, strategy flags (`us_expansion`, `new_service_line`, `acquisition`, `new_market`).

### Steps

1. [agent] On `executive.board_meeting_held`, open a task to file minutes, update statutory registers and make any Companies House changes within 14 days (task due 10 days).
2. [agent] On `executive.okrs_set`, record legal OKRs and align them to the KPI list in kpis.md.
3. [agent] On `executive.strategy_updated`, record flags. If `us_expansion` is set, open a 30-day task for US entity readiness: Delaware filings, state registrations, US contract templates (Lumenhall Partners Inc. from Q1 FY2027, COMPANY.md §1).
4. [human] General Counsel signs off the minutes, maintains the conflicts log and checks delegations of authority against COMPANY.md §9.3.

### Outputs and messages

- No public message; the activity events `legal.activity.board_governance`, `legal.activity.okrs_noted` and `legal.activity.strategy_noted` are logged. Open items flow into SOP-LEGAL-12 budget and hiring requests.

### SLA and controls

- Minutes and registers within 10 days; Companies House changes within 14 days; confirmation statement prepared each January.

### Exceptions and escalation

- A board resolution that conflicts with the delegations of authority: General Counsel advises the Chair, Priya Raman, before the minutes are filed.

---

## SOP-LEGAL-12: Budget, hiring and compliance calendar

**Owner**: General Counsel.
**Trigger**: `finance.budget_cycle_opened` and `executive.budget_approved`, plus the monthly schedule on the first day of each month.
**Inputs**: `fiscal_year`, `budget_id` (for example `BUD-2027`), the §5.4 envelope, the hiring plan in blueprint.md section 5, the monthly compliance calendar.

### Steps

1. [agent] On `finance.budget_cycle_opened`, prepare the legal budget for the target fiscal year (defaults to the next year from October) from `economics.md`: people, non-people by line, headcount humans and agents.
2. [agent] Emit `legal.budget_submitted` with `people_gbp`, `non_people_gbp`, `amount_gbp`, `non_people_lines_gbp`, `headcount_humans`, `headcount_agents` (£210k + £100k = £310k in FY2026; £330k + £250k = £580k in FY2027; £600k + £700k = £1,300k in FY2028).
3. [agent] On `executive.budget_approved`, record the approved envelope.
4. [agent] Each month, log the compliance calendar item: January confirmation statement and playbook review; April, July and October quarterly regulatory horizon review; April ICO data protection fee check; July insurance renewal pack (PI, cyber, D&O) with Finance; October open the budget input.
5. [agent] In the month of a requisition in the hiring plan (2027-01 Commercial and Privacy Counsel, 2027-04 Contracts Specialist, 2027-10 Privacy and Regulatory Counsel, 2028-01 Legal Operations Analyst), emit `legal.hire_requested` once with role, level, band and start quarter.
6. [human] General Counsel reviews and signs off the submission before the finance deadline.

### Outputs and messages

- `legal.budget_submitted` (to Finance): `department` = `legal`, `fiscal_year`, `budget_id`, `people_gbp`, `non_people_gbp`, `amount_gbp`, `non_people_lines_gbp`, `headcount_humans`, `headcount_agents`, `summary`.
- `legal.hire_requested` (to People): `department`, `role`, `level`, `count` = 1, `salary_band_gbp`, `start_quarter`, `summary`.

### SLA and controls

- Budget submitted inside the cycle (envelope per COMPANY.md §5.4); hire request raised in the requisition month; non-budgeted spend above £50k needs the CFO and above £250k the CEO (COMPANY.md §9.3).

### Exceptions and escalation

- Envelope overrun risk (outside counsel for a dispute or breach): General Counsel raises it with the CFO; a variance flag from Finance goes to the Executive.

---

## SOP-LEGAL-13: Data subject access requests and privacy register

**Owner**: General Counsel (Commercial and Privacy Counsel from Q2 FY2027).
**Trigger**: manual intake of a DSAR (email to the privacy mailbox) and a weekly schedule review; no topic exists for DSARs in `core/topics.py`, so the register is human-maintained.
**Inputs**: requester identity, scope, receipt date, systems holding data (People, IT Security, Sales CRM), exemptions.

### Steps

1. [human] Log the DSAR on receipt, verify identity, and set the deadline at one month (UK GDPR Art 12(3), DPA 2018).
2. [human] Ask IT Security, People and Sales to search systems; the Legal agent drafts the search request and tracks responses.
3. [human] Review for third-party data and exemptions (legal privilege, confidential references); redact and send.
4. [human] Extend by up to two months only for complexity or volume, and tell the requester within the first month.
5. [agent] Weekly, list open DSARs by days remaining and flag any at 7 days or fewer.

### Outputs and messages

- No public topic; the register feeds `dsar_on_time_pct` and the monthly KPI pack. A DSAR that reveals a breach goes to SOP-LEGAL-05.

### SLA and controls

- Closed within one month (KPI `dsar_on_time_pct` 98%); identity verification before disclosure; disclosure approved by the General Counsel.

### Exceptions and escalation

- Manifestly unfounded or excessive request: the General Counsel decides whether to refuse or charge a reasonable fee, with reasons recorded.
