# Operations Standard Operating Procedures

Department: `operations` (agent class `OperationsAgent`). Head: Beatrice Moreau, Chief Operating Officer (COMPANY.md §9.2). Scope: procurement and sourcing, vendor management, workspace and facilities, compliance actions, business continuity, PMO and process improvement, budget and capacity. UK context: Health and Safety at Work etc. Act 1974, Regulatory Reform (Fire Safety) Order 2005, Health and Safety (Display Screen Equipment) Regulations 1992, UK GDPR and Data Protection Act 2018 (processor terms, Article 28), Late Payment of Commercial Debts Act, Bribery Act 2010 (gifts and hospitality from suppliers), Modern Slavery Act 2015 (supplier statement above the turnover threshold), IR35 for contractors (People owns the status determination). New York office from Q1 FY2027 (COMPANY.md §1).

Conventions used throughout:

- `[human]` steps are performed by the role named in each SOP; `[agent]` steps by `OperationsAgent` working under a named human owner. Agents may draft, analyse, monitor and propose; they may not sign contracts, approve payments above £10,000, approve any purchase order above £2,500, change supplier bank details, accept a vendor risk, notify a regulator or close a compliance finding (COMPANY.md §9.4).
- Role titles are those of `blueprint.md` section 3: **COO** = Chief Operating Officer (Beatrice Moreau); **Operations Manager** (joins Q3 FY2027); **Procurement and Workspace Specialist** (joins Q4 FY2026); **Compliance and Risk Specialist** (joins Q2 FY2027); **Workspace and Facilities Associate** (Q4 FY2027); **Operations Analyst** (Q4 FY2027); **Vendor Management Specialist** (Q3 FY2028); **PMO Lead** (Q3 FY2028); **PMO Analyst** (Q4 FY2028). Until a seat is filled the COO covers it, and where a role below names a successor ("Operations Manager (COO until Q3 FY2027)") the bracket says who covers. Other departments: **CFO** (Hannah Whitcombe), **Finance Manager**, **CISO** (Wei Zhang), **General Counsel** (Callum Fraser), **CPO** (Grace Adeyemi), **CEO** (Imogen Hartley).
- Money in message bodies is `amount_gbp` ex VAT unless the key says otherwise. For orders, `amount_gbp` is the total committed value over the contract term (capped at 36 months). US spend is converted at £1 = $1.27 (COMPANY.md §1).
- SLAs in "business days" exclude UK bank holidays. Sim days are integers from Day 0 = 2026-01-05 (COMPANY.md §1); one sim day is one calendar day, and `due_day` keys are sim days. Where a business-day SLA is implemented in the simulation it is converted to sim days using the table below.
- Business IDs follow CONVENTIONS section 4 (`VN-0001`, `EMP-0001`, `BUD-2027`) plus operations IDs: purchase order `PO-2026-0001`, request for quotation `RFQ-2026-0001`, compliance action `CA-0001`, continuity test `BCT-0001`, process improvement `PI-0001`. A finding keeps Legal's `finding_id` (`CF-0001`).

## Constants (defined once; mirrored in `agent.py`)

These are the only values for thresholds and SLAs. Every SOP below refers to them by name. `agent.py` defines each as a module constant with the same name and value.

### Spend, quotes and approvals

| Constant | Value | Meaning |
|---|---|---|
| THREE_QUOTE_THRESHOLD_GBP | 2,500 | Orders with committed value at or above this need three compliant written quotes. Below it, one written quote or published catalogue price |
| FORMAL_TENDER_THRESHOLD_GBP | 25,000 | At or above: formal RFQ pack with written scoring, Legal contract review and IT Security assessment whatever the data content |
| VENDOR_REVIEW_MIN_ANNUAL_GBP | 10,000 | A new vendor with annual value at or above this needs a vendor review. A review is also mandatory for any new vendor that processes personal or client data, has system or network access, or is an AI platform, whatever the value |
| AGENT_PO_LIMIT_GBP | 2,500 | An agent may release a PO below this value, single quote, approved vendor, budgeted line |
| AGENT_APPROVAL_CEILING_GBP | 10,000 | Agents never approve a payment above this (COMPANY.md §9.4). Orders above AGENT_PO_LIMIT_GBP are always human-approved |
| PO_LEVEL_2_LIMIT_GBP | 10,000 | Operations Manager approves above 2,500 and up to this (COO until Q3 FY2027) |
| PO_LEVEL_3_LIMIT_GBP | 50,000 | COO approves above 10,000 and up to this |
| PO_CFO_LIMIT_GBP | 250,000 | CFO approves above 50,000 and up to this; CEO above (COMPANY.md §9.3) |
| NON_BUDGETED_CFO_THRESHOLD_GBP | 50,000 | Non-budgeted spend above this needs the CFO; above 250,000 the CEO (COMPANY.md §9.3). Non-budgeted spend up to 50,000 follows the ladder above plus Finance Manager confirmation of a funding source |
| EMERGENCY_ORDER_LIMIT_GBP | 10,000 | Emergency order without three quotes, approved by the CFO on the COO's recommendation (as in SOP-FINANCE-14), reviewed retrospectively within 10 business days |
| QUOTE_VALIDITY_DAYS | 30 | A quote must be valid on the PO date and for at least 30 days from receipt, or the PO is placed within its stated validity |
| RFQ_RESPONSE_DAYS | 7 | Business days given to suppliers to respond |
| RFQ_EXCEPTION_DAYS | 10 | If fewer than three compliant quotes by this many business days after the RFQ is issued, the "fewer than three" exception route applies |
| MAX_COMMITMENT_TERM_MONTHS | 36 | Committed value is counted over at most 36 months |
| SPLIT_ORDER_WINDOW_DAYS | 30 | Orders to one vendor in one category within this window are aggregated when applying thresholds |
| BUDGET_WARNING_PCT | 80 | Budget-line usage at which the budget holder and Finance are warned (as in SOP-FINANCE-14) |

Approval ladder (value tested against the order's committed value; for non-budgeted spend the NON_BUDGETED rows also apply):

| Level | Committed value | Approver | Approval SLA (business days) | Sim days |
|---|---|---|---|---|
| 1 | below 2,500 | Procurement and Workspace Specialist (COO until Q4 FY2026); agent may release | same day | 0 |
| 2 | 2,500 to 10,000 | Operations Manager (COO until Q3 FY2027) | 2 | 2 |
| 3 | above 10,000 to 50,000 | COO | 3 | 3 |
| 4 | above 50,000 to 250,000 | CFO (with the COO's recommendation) | 5 | 5 |
| 5 | above 250,000 | CEO (CFO recommends) | 7 | 7 |

The requester cannot approve their own order, and the person raising a PO cannot approve its payment (Finance owns payment release). When the COO is also the requester at level 3 or above, the CFO is the approver.

Quote scoring: price 40 points, capability and fit 30, risk (security, financial standing, concentration) 20, terms and exit 10. Highest score wins; the lowest compliant price must be selected unless the written reasons for a higher-priced supplier are recorded and approved at the ladder level.

### Compliance, workspace, continuity and process

| Constant | Value | Meaning |
|---|---|---|
| COMPLIANCE_SLA_CRITICAL | 5 business days (7 sim days) | Time to close a critical finding action |
| COMPLIANCE_SLA_HIGH | 10 business days (14 sim days) | High |
| COMPLIANCE_SLA_MEDIUM | 20 business days (28 sim days) | Medium |
| COMPLIANCE_SLA_LOW | 40 business days (56 sim days) | Low |
| COMPLIANCE_ESCALATION_DAYS | 7 | On the due day the action is escalated to the COO; 7 sim days later to the CEO |
| POLICY_ALIGNMENT_DAYS | 10 business days (14 sim days) | Procedures aligned with a new policy after `legal.policy_update_published` |
| WORKSPACE_KIT_LEAD_TIME_DAYS | 2 | Delivery lead time for a kit that is not in stock |
| STOCK_BUFFER_PCT | 10 | Kit and desk buffer, as a percentage of planned annual starters |
| DESK_OCCUPANCY_WARNING_PCT | 90 | Peak desk occupancy that opens a capacity task |
| ASSET_RECOVERY_DAYS | 5 business days (7 sim days) | Return of equipment after the last working day |
| RTO_TIER1_HOURS | 4 | Recovery time objective for Tier-1 systems (email, ledger, engagement workspace, identity) |
| RTO_TIER2_HOURS | 24 | Tier-2 systems |
| RPO_TIER1_HOURS | 1 | Recovery point objective, Tier 1 |
| RPO_TIER2_HOURS | 24 | Tier 2 |
| PROCESS_PROPOSAL_MIN_SAVING_GBP | 10,000 | Annualised benefit at or above which a proposal is published to Executive |
| PROCESS_MAX_PAYBACK_MONTHS | 12 | Maximum payback for a proposal |
| NOTIONAL_HOURLY_COST_GBP | 45 | Value of an hour released (as in `people` economics) |
| CRITICAL_VENDOR_ANNUAL_GBP | 50,000 | A vendor at or above this annual spend, or a single point of failure, is critical |
| RENEWAL_DIARY_CRITICAL_DAYS | 90 | Renewal and exit review lead time for critical vendors before the notice date |
| RENEWAL_DIARY_OTHER_DAYS | 60 | Other vendors |
| OPS_BUDGET_SUBMISSION_DAY | 21 | Day of the budget cycle by which `operations.budget_submitted` is sent |

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-OPERATIONS-01 | Quote intake and competitive sourcing | `external.vendor_quote_received` | Procurement and Workspace Specialist (COO until Q4 FY2026) | Quote registered same day; RFQ complete within 7 business days; recommendation within 2 business days of the third quote |
| SOP-OPERATIONS-02 | Purchase orders, approval ladder and spend control | Approved sourcing recommendation (from SOP-01, 05, 07, 11); daily 16:00 PO register run | Operations Manager (COO until Q3 FY2027) | PO placed within the approval SLA: level 1 same day, level 2 two, level 3 three, level 4 five, level 5 seven business days |
| SOP-OPERATIONS-03 | Vendor onboarding review and approval | `it_security.vendor_risk_assessed` (review opened by SOP-01 or 04) | Procurement and Workspace Specialist (COO until Q4 FY2026) | Review request within 1 business day of need; vendor approved within 2 business days of a passed assessment |
| SOP-OPERATIONS-04 | Vendor performance, renewal and exit | Monthly schedule (first Monday) | Vendor Management Specialist (Procurement and Workspace Specialist until Q3 FY2028) | Scorecards by working day 6; renewal review 90 days (critical) or 60 days (other) before notice date |
| SOP-OPERATIONS-05 | New-hire workspace and equipment readiness | `people.new_hire_started`, `it_security.access_provisioned` | Procurement and Workspace Specialist (Workspace and Facilities Associate for daily running from Q4 FY2027) | Desk and kit ready on or before the start day |
| SOP-OPERATIONS-06 | Leaver asset recovery and desk release | `people.employee_left` | Workspace and Facilities Associate (Procurement and Workspace Specialist until Q4 FY2027) | Equipment recovered within 5 business days of the last day |
| SOP-OPERATIONS-07 | Event, engagement and staffing logistics | `marketing.event_scheduled`, `delivery.engagement_kickoff`, `delivery.staffing_requested` | Procurement and Workspace Specialist | Event RFQ issued within 2 business days; engagement logistics confirmed 2 business days before the start day |
| SOP-OPERATIONS-08 | Compliance findings and regulatory change actions | `legal.compliance_finding_raised`, `legal.regulatory_change_noted` | Compliance and Risk Specialist (COO until Q2 FY2027) | Action opened and owner assigned within 1 business day; closure by severity: critical 5, high 10, medium 20, low 40 business days |
| SOP-OPERATIONS-09 | Policy updates and procedure alignment | `legal.policy_update_published` | Compliance and Risk Specialist (COO until Q2 FY2027) | Procedures aligned within 10 business days of publication |
| SOP-OPERATIONS-10 | Business continuity, incident support and crisis logistics | `it_security.incident_detected`, `it_security.incident_resolved`, `executive.crisis_declared`; test schedule | Operations Manager (COO until Q3 FY2027) | Continuity logistics active within 1 hour of a high or critical incident; test result filed within 5 business days of resolution |
| SOP-OPERATIONS-11 | Third-party vulnerability and asset response | `it_security.vulnerability_found` | Operations Manager (COO until Q3 FY2027) | Affected vendor or asset owner identified within 1 business day; remediation plan within 2 business days for high or critical |
| SOP-OPERATIONS-12 | Process improvement and PMO | `data.data_quality_issue_raised`, `executive.okrs_set`, `executive.strategy_updated` | Operations Manager (PMO Lead for programmes from Q3 FY2028; COO until Q3 FY2027) | Programme plan aligned within 10 business days of OKRs or strategy; proposal within 10 business days of a qualifying issue |
| SOP-OPERATIONS-13 | Operations budget cycle and spend tracking | `finance.budget_cycle_opened`, `executive.budget_approved` | COO | Budget submitted by day 21 of the cycle; approved budget loaded within 3 business days |
| SOP-OPERATIONS-14 | Operations capacity and hiring | Quarterly schedule (first Monday of the quarter) | COO | Capacity review each quarter; hire request raised within 5 business days of a trigger breach |

Topic coverage (checked at the end of this document): every subscribed topic is the trigger of, or an explicit sub-trigger inside, at least one SOP above, and every published topic appears in the outputs of at least one SOP.

---

## SOP-OPERATIONS-01: Quote intake and competitive sourcing

**Owner**: Procurement and Workspace Specialist (COO until Q4 FY2026).
**Trigger**: `external.vendor_quote_received` (a supplier quote arrives in the procurement mailbox or portal).
**Inputs**: the quote (`quote_id`, `rfq_id`, `vendor_id`, `vendor_name`, `amount_gbp`, `term_months`, `valid_until_day`, `category`, `department` (the budget holder), `budgeted`), vendor flags (`processes_personal_data`, `system_access`, `ai_platform`), the vendor register, the budget line from Finance, the requester's business case, and any earlier quotes in the same `rfq_id`.

### Steps

1. [agent] Register the quote against its RFQ (create `RFQ-yyyy-nnnn` if the quote has no `rfq_id`), compute the committed value (`amount_gbp`, capped at 36 months) and the annual value (committed value / (term months / 12)).
2. [agent] Check validity: reject a quote whose `valid_until_day` is before today or less than QUOTE_VALIDITY_DAYS after receipt unless the PO will be placed inside its validity. Aggregate with other quotes or orders to the same vendor and category in the last SPLIT_ORDER_WINDOW_DAYS; use the aggregate value to select the path below.
3. [agent] Select the path by committed value: below THREE_QUOTE_THRESHOLD_GBP, the single-quote path; THREE_QUOTE_THRESHOLD_GBP to below FORMAL_TENDER_THRESHOLD_GBP, the three-quote path; FORMAL_TENDER_THRESHOLD_GBP and above, the formal tender path (RFQ pack, written scoring, Legal contract review and IT Security assessment regardless of data content).
4. [agent] Vendor check: if the vendor is not in the register as approved, and the annual value is at least VENDOR_REVIEW_MIN_ANNUAL_GBP or any of the data, system-access or AI flags is true, open a vendor review (SOP-OPERATIONS-03) and emit `operations.vendor_review_requested`; the order is held until `operations.vendor_approved`.
5. [agent] Single-quote path: if the vendor is approved (or needs no review), the budget line has room and `budgeted` is true, release the PO under SOP-OPERATIONS-02 at level 1 within AGENT_PO_LIMIT_GBP; otherwise route it to the human approver.
6. [agent] Three-quote and tender paths: hold the order until three compliant quotes are registered (or the exception route applies at RFQ_EXCEPTION_DAYS), then score them with the weights in the constants section and draft a recommendation with the price, savings against the first compliant quote, score sheet, vendor status and budget impact.
7. [human] Procurement and Workspace Specialist reviews the recommendation (tests that the quotes are like for like, scope is the same, no connected-party or conflict-of-interest issue under the Bribery Act 2010 policy), and records the decision and any negotiation outcome. Negotiated reductions are recorded against the first compliant quote for the procurement_savings_pct KPI.
8. [human] Approver per the ladder (SOP-OPERATIONS-02) approves, or approves a documented exception: sole source (no alternative exists, written justification), fewer than three quotes (market too narrow after RFQ_EXCEPTION_DAYS, evidence of invitations sent), or emergency (crisis rule in SOP-OPERATIONS-10).
9. [agent] Hand the approved recommendation to SOP-OPERATIONS-02 for PO placement, and close the RFQ with the unsuccessful bidders told within 5 business days.

### Outputs and messages

- `operations.vendor_review_requested` (recipient `*`; subscribers legal, it_security, finance): `vendor_id`, `vendor_name`, `service`, `data_classes`, `processes_personal_data`, `has_dpa`, `data_outside_uk_eea`, `annual_cost_gbp`, `amount_gbp`, `tier_hint` (1 to 3), `rfq_id`, `review_reason` (`new_vendor`), `requested_by`, `due_day`, `summary`.
- `operations.procurement_order_placed` (see SOP-OPERATIONS-02) when a single-quote order is released at level 1.
- Tasks for the Procurement and Workspace Specialist for the recommendation review.

### SLA and controls

- SLA: quote registered the same business day; RFQ response window RFQ_RESPONSE_DAYS (7 business days); recommendation within 2 business days of the third compliant quote; single-quote orders processed within 1 business day.
- Control: no order is split to stay below a threshold; aggregation in step 2 applies. A split order found afterwards is reported to the COO and Finance, and the retrospective three-quote check is recorded as a breach for three_quote_compliance_pct.
- Control: conflicts of interest are declared by the requester and the approver; gifts and hospitality from bidders above £50 are logged and referred to the COO during an open RFQ.
- Control: the agent never contacts a supplier to negotiate; negotiation is a human step.

### Exceptions and escalation

- Quote expired before approval: re-request, restarting the three-quote clock only for the affected supplier.
- Single compliant bidder: sole-source exception approved one level above the order value (COO minimum; CFO above PO_LEVEL_3_LIMIT_GBP).
- A bid at more than 30% below the others is checked for scope omission and supplier viability before it is scored.
- Supplier is a connected party to a Lumenhall employee: COO decides with the General Counsel; the order is escalated to the CFO regardless of value.

---

## SOP-OPERATIONS-02: Purchase orders, approval ladder and spend control

**Owner**: Operations Manager (COO until Q3 FY2027).
**Trigger**: an approved sourcing recommendation arriving from SOP-OPERATIONS-01, 05, 07 or 11 (internal hand-off, not a topic); and the daily PO register run at 16:00 UK time (schedule).
**Inputs**: approved recommendation, quotes, committed value, vendor status, budget line and usage from Finance's commitment register, requester and approver identities, the approval ladder in the constants section.

### Steps

1. [agent] Determine the approval level from the committed value (aggregated per SPLIT_ORDER_WINDOW_DAYS) using the ladder, and whether the spend is budgeted. For non-budgeted spend above NON_BUDGETED_CFO_THRESHOLD_GBP raise the level to CFO (and CEO above PO_CFO_LIMIT_GBP) (COMPANY.md §9.3).
2. [agent] Verify the preconditions: vendor approved (`operations.vendor_approved` held), three quotes or an approved exception, funding source confirmed, requester is not the approver, quote still valid.
3. [agent] At level 1 with all preconditions met, create the PO and release it the same day. At levels 2 to 5 create the PO in draft and a task for the named approver with the recommendation and score sheet attached.
4. [human] Approver approves, queries or rejects within the approval SLA. Approval is recorded with name, title and day; approval by email or chat is not valid.
5. [agent] On approval, release the PO to the vendor, record `po_id`, committed value, term, cost centre and budget line, and emit `operations.procurement_order_placed` so Finance creates the commitment and matches the invoice (SOP-FINANCE-14).
6. [agent] Check the budget line against the Finance register after each order: warn the budget holder and Finance at BUDGET_WARNING_PCT (80%) usage; if an order would take the line over 100% treat the excess as non-budgeted.
7. [agent] Daily 16:00 PO register run: look for split orders (several orders to the same vendor and category within SPLIT_ORDER_WINDOW_DAYS whose total is at least THREE_QUOTE_THRESHOLD_GBP), orders placed without a PO ("no PO, no pay" reports from Finance), POs without a goods or services receipt after 30 days, and approvals past their SLA.
8. [human] Operations Manager (COO until Q3 FY2027) reviews the weekly exceptions list; orders between £2,000 and £2,499 are sampled monthly for split-order pattern and any supplier with more than three sub-threshold orders in a quarter is re-sourced competitively.
9. [human] Finance Manager reconciles PO to invoice to receipt (three-way match); the Operations Analyst provides spend analytics to the COO monthly.

### Outputs and messages

- `operations.procurement_order_placed` (recipient `finance`): `po_id`, `rfq_id`, `vendor_id`, `vendor` (vendor name), `department` (budget holder), `amount_gbp`, `annual_cost_gbp`, `term_months`, `category`, `budgeted` (bool), `quotes_received`, `exception` (`none`|`sole_source`|`fewer_than_three`|`emergency`), `approval_level` (1 to 5), `approver_title`, `split_flag` (bool), `severity`, `due_day`, `summary`.
- Budget warnings: task for the budget holder; no topic.

### SLA and controls

- SLA: level 1 same day; level 2 two business days; level 3 three; level 4 five; level 5 seven. If an approver is unavailable for the SLA, the next level up approves; no PO is placed on a verbal approval.
- Control: agents release no PO above AGENT_PO_LIMIT_GBP (£2,500) and approve nothing above AGENT_APPROVAL_CEILING_GBP (£10,000) (COMPANY.md §9.4). The agent cannot add or change supplier bank details; Finance does that with a call-back to a known number.
- Control: segregation of duties: requester, approver and payer are three different people; the agent proposes only.
- Control: no PO, no pay except rent, rates, utilities, payroll, tax and statutory payments (agreed with Finance).
- Control: a PO is the contract reference for orders below FORMAL_TENDER_THRESHOLD_GBP using the standard terms; anything with non-standard liability, IP or data terms goes to the General Counsel (COMPANY.md §9.3).

### Exceptions and escalation

- Urgent order outside hours: COO may place an emergency order up to EMERGENCY_ORDER_LIMIT_GBP with CFO approval, flagged `exception: emergency` and reviewed within 10 business days.
- Price change between approval and PO above 5%: re-approval at the new value.
- Supplier invoice arrives with no PO: hold; notify the budget holder and Finance; repeated cases go to the COO as a control breach.
- Approver rejects: recorded reasons; the next-ranked quote may be recommended once.

---

## SOP-OPERATIONS-03: Vendor onboarding review and approval

**Owner**: Procurement and Workspace Specialist (COO until Q4 FY2026).
**Trigger**: `it_security.vendor_risk_assessed` (IT Security's assessment result). The review itself is opened by SOP-OPERATIONS-01 (new vendor) or SOP-OPERATIONS-04 (renewal and annual re-review) with `operations.vendor_review_requested`.
**Inputs**: vendor questionnaire answers and evidence (ISO 27001 certificate, SOC 2 report, DPA, sub-processor list, insurance certificates, financial accounts), IT Security's `tier`, `risk_rating`, `decision` and `conditions`, Legal's contract review, Finance's due diligence, open `legal.compliance_finding_raised` items linked to the vendor.

### Steps

1. [agent] Open the review when a vendor needs one: assign `vendor_id` (`VN-0001`), set `tier_hint` (Tier 1: processes client confidential or personal data, privileged access or an AI platform handling client content; Tier 2: internal confidential data; Tier 3: otherwise, matching IT Security's tiering), and emit `operations.vendor_review_requested` with a due day: Tier 1 within 10 business days, Tier 2 within 5, Tier 3 within 2 (plus 2 days for Operations to approve).
2. [human] Procurement and Workspace Specialist collects the evidence pack from the vendor and chases missing items weekly; the clock stops while the vendor answers (`awaiting_vendor`).
3. [agent] On `it_security.vendor_risk_assessed`, match to the open review by `vendor_id`; record `tier`, `risk_rating`, `decision` (`approve`|`approve_with_conditions`|`reject`), `conditions` and `reassess_day`.
4. [agent] Check for blockers: an open compliance finding linked to the vendor (SOP-OPERATIONS-08), no DPA where personal data is processed, or a high risk rating. A blocker keeps the vendor in `pending`.
5. [human] Procurement and Workspace Specialist (COO if the vendor is critical or the rating is high) confirms approval, with the CISO's decision and Legal's DPA on file. A high or critical risk that the business still needs is decided by the CFO, CISO and COO together (as in SOP-FINANCE-14), with written conditions.
6. [agent] On a decision of `approve` or `approve_with_conditions`, mark the vendor `approved` and emit `operations.vendor_approved` to Finance and IT Security. Release any held PO to SOP-OPERATIONS-02.
7. [agent] On a decision of `reject`, mark the vendor `rejected`, close the RFQ for that vendor, tell the requester, and recommend the next-ranked quote.
8. [human] Operations records the conditions owner (usually the budget holder) and the date by which each condition must be met; IT Security verifies conditions before data flows (SOP-IT_SECURITY-08).

### Outputs and messages

- `operations.vendor_review_requested` (recipient `*`; subscribers legal, it_security, finance): as in SOP-OPERATIONS-01.
- `operations.vendor_approved` (recipient `*`; subscribers finance, it_security): `vendor_id`, `vendor_name`, `tier`, `risk_rating`, `decision`, `conditions` (list), `approved_by` (role title), `payment_terms_days` (30), `annual_cost_gbp`, `amount_gbp`, `reassess_day`, `summary`.
- Vendor register entry and sub-processor list update (for IT Security and Legal).

### SLA and controls

- SLA: review requested within 1 business day of the need; total cycle median at or below the KPI target (vendor_review_cycle_days: 10 / 9 / 8 business days); `operations.vendor_approved` within 2 business days of a passed assessment.
- Control: vendor_approved_before_order_pct is 100%: no PO and no data to a vendor in scope before `operations.vendor_approved`. Any breach is reported to the CFO and CISO the same day.
- Control: default payment terms are 30 days and never shorter than the contract; bank details are verified by Finance with a call-back.
- Control: concentration check: a single supplier above 20% of cloud or AI spend is reviewed with the CISO annually (as in SOP-IT_SECURITY-08).

### Exceptions and escalation

- Vendor refuses to complete the assessment: the review closes after 30 days; the requester is told the vendor cannot be used for in-scope data.
- Urgent need before assessment: the vendor can be used only for non-personal, non-client, non-system-access work for up to 10 business days with the COO's written approval and the CISO informed; no data flows.
- Assessment rating high and no conditions agreed: reject, or escalate to the CFO, CISO and COO.

---

## SOP-OPERATIONS-04: Vendor performance, renewal and exit

**Owner**: Vendor Management Specialist (Procurement and Workspace Specialist until Q3 FY2028).
**Trigger**: monthly schedule (first Monday of the month); contract notice dates held in the vendor register.
**Inputs**: vendor register (term, notice date, value, tier, `reassess_day`), PO and invoice data, service incidents and tickets, scorecard results, IT Security's reassessment dates, Finance's financial-health flags.

### Steps

1. [agent] Build the monthly vendor scorecard for every critical vendor (annual spend at or above CRITICAL_VENDOR_ANNUAL_GBP or a single point of failure): delivery against SLA, quality or incident count, spend against PO, security or compliance findings, and responsiveness. Score 0 to 100; below 70 is flagged amber and below 55 red.
2. [human] Vendor Management Specialist holds a quarterly performance review with each critical vendor and an annual review with others of annual spend of £10,000 or more; actions are recorded with dates.
3. [agent] Diary the renewal: for each contract flag RENEWAL_DIARY_CRITICAL_DAYS (90) before the notice date for critical vendors and RENEWAL_DIARY_OTHER_DAYS (60) for others. At the flag create a renewal review task with usage, spend, price benchmark and alternatives.
4. [human] Decide renew, renegotiate, re-tender or exit. A renewal at or above THREE_QUOTE_THRESHOLD_GBP of committed value is re-sourced through SOP-OPERATIONS-01 unless a sole-source exception is approved. Exit plans are written for critical vendors (data return, transition, replacement timeline).
5. [agent] When a vendor's `reassess_day` or contract renewal falls due, or a vendor suffers a reported breach or insolvency event, emit `operations.vendor_review_requested` with `review_reason` of `annual_review`, `renewal` or `incident`.
6. [human] Finance is told of exits (so payables are closed); IT Security is told to revoke access and recover data; Legal manages notice.

### Outputs and messages

- `operations.vendor_review_requested` (recipient `*`; subscribers legal, it_security, finance): as in SOP-OPERATIONS-01 with `review_reason` set to `annual_review`, `renewal` or `incident`.
- Monthly scorecard pack to the COO and Finance (no topic).

### SLA and controls

- SLA: scorecards by working day 6; renewal review opened 90 days (critical) or 60 days (other) before the notice date; re-review request within 1 business day of an incident report.
- Control: no auto-renewal is allowed to roll without an explicit decision; contracts with evergreen clauses are flagged in the register.
- Control: single-supplier concentration above 20% of cloud or AI spend reviewed annually with the CISO.

### Exceptions and escalation

- Critical vendor in red for two consecutive months: COO escalation and an exit-plan test.
- Vendor insolvency or sanction notice: immediate hold on new POs, CFO and CISO informed the same day, contingency supplier invoked.

---

## SOP-OPERATIONS-05: New-hire workspace and equipment readiness

**Owner**: Procurement and Workspace Specialist (Workspace and Facilities Associate for daily running from Q4 FY2027; COO until Q4 FY2026).
**Trigger**: `people.new_hire_started` (starter confirmed with start day, location and equipment profile) and `it_security.access_provisioned` (accounts and device ready).
**Inputs**: `employee_id`, `employee_name`, `department`, `role_title`, `start_day`, `location` (London or New York), `equipment` (profile list), `access_profile`, the asset and desk registers, stock levels, the planned starters from SOP-OPERATIONS-07.

### Steps

1. [agent] On `it_security.access_provisioned`, record the `device_id` and access profile against the `employee_id` and check whether a workspace record exists; if none exists, create one and reserve a desk and kit (T-minus planning view).
2. [agent] On `people.new_hire_started`, create or update the workspace record, then check that a desk (or remote-working kit) and the equipment profile are available at the starter's location. Check the buffer: kit stock must not fall below STOCK_BUFFER_PCT (10%) of planned annual starters.
3. [agent] If everything is in stock, assign desk and kit, and emit `operations.workspace_ready` on the same day (`on_time` true).
4. [agent] If an item is out of stock, order the shortfall: within AGENT_PO_LIMIT_GBP the agent releases the PO (SOP-OPERATIONS-02 level 1) and emits `operations.procurement_order_placed` (`department` set to the budget holder; laptops to `it_security`); above it, route to the approver. Emit `operations.workspace_ready` after WORKSPACE_KIT_LEAD_TIME_DAYS (2) with `on_time` false and the reason in `summary`.
5. [human] Workspace and Facilities Associate (Procurement and Workspace Specialist until Q4 FY2027) prepares the desk, building pass, health and safety induction, fire-warden briefing and DSE self-assessment, and hands the kit over on day one with a signed asset form.
6. [agent] Record the asset serials against the `EMP-xxxx` record and add a DSE assessment task due within 4 weeks.
7. [agent] Check capacity: if peak-day desk occupancy planned for the next 30 days exceeds DESK_OCCUPANCY_WARNING_PCT (90%) at a site, raise a capacity task for the Operations Manager (COO until Q3 FY2027) (SOP-OPERATIONS-14).

### Outputs and messages

- `operations.workspace_ready` (recipient `people`): `employee_id`, `employee_name`, `name`, `location` (site and desk, for example `London HQ, desk 4.17`), `desk`, `equipment` (list), `start_day`, `ready_day`, `on_time` (bool), `summary`.
- `operations.procurement_order_placed` (recipient `finance`) for shortfall orders: keys as in SOP-OPERATIONS-02.
- Tasks for the Workspace and Facilities Associate.

### SLA and controls

- SLA: desk and kit ready on or before the start day (KPI workspace_ready_on_time_pct: 95 / 97 / 98%). The kit is reserved as soon as the offer is accepted (from People's planning) or at `it_security.access_provisioned`, whichever is earlier. Emit exactly one `operations.workspace_ready` per employee.
- Control: assets are issued against a signed form; a device is not handed over without IT Security's confirmation that it is enrolled and encrypted.
- Control: laptop purchases are charged to IT Security's budget; Operations holds only the peripheral and desk pool.
- Control: health and safety induction is recorded before the second working day.

### Exceptions and escalation

- Access or workspace not confirmed 2 business days before start: People and the COO are alerted (SOP-PEOPLE-05); the start may move by up to 3 days.
- Stock-out for more than 5 starters in a month: Operations Manager (COO until Q3 FY2027) opens a bulk order through SOP-OPERATIONS-01 and raises the buffer.
- New York starter and no desk contracted: use serviced-office hot desk; COO approves a month-by-month extension.

---

## SOP-OPERATIONS-06: Leaver asset recovery and desk release

**Owner**: Workspace and Facilities Associate (Procurement and Workspace Specialist until Q4 FY2027; COO until Q4 FY2026).
**Trigger**: `people.employee_left` (a resignation, dismissal, redundancy or end of contract is confirmed with a last working day).
**Inputs**: `employee_id`, `employee_name`, `department`, `last_day`, `leaver_type`, `access_end_time`, the asset register entry for the leaver (laptop, monitor, pass, cards, hardware keys), desk assignment, any PO approver or budget-holder roles, vendor relationships owned by the leaver.

### Steps

1. [agent] Retrieve the leaver's assets from the register and create a recovery checklist with the last day and the recovery deadline (last day plus ASSET_RECOVERY_DAYS, 5 business days).
2. [human] Workspace and Facilities Associate arranges return: handover at the office on the last day, or prepaid courier for remote and New York leavers; confirms receipt against serial numbers.
3. [agent] If not returned by the deadline, raise a task for IT Security to remote-wipe and lock the device (SOP-IT_SECURITY on leavers) and notify People so that final pay deductions follow the contract (People decides; no deduction is made without a lawful basis).
4. [agent] Release the desk and building pass; update desk occupancy; return usable kit to stock after IT Security's wipe and reimaging.
5. [agent] Check delegations: if the leaver was an approver, budget holder or requester on open RFQs or POs, reassign them to the line manager within 2 business days and tell Finance (no PO may remain with a departed requester as approver).
6. [agent] If the leaver owned a vendor relationship, reassign the owner in the vendor register and create a task for the manager.
7. [human] Close the checklist; record recovered or lost; lost assets are reported to the COO and Finance for write-off at net book value, and to the CISO if the device held data.

### Outputs and messages

- No topic is emitted. Outputs are the recovery checklist, tasks, asset register updates and `operations.activity.asset_recovery` log events. If an operations employee leaves, SOP-OPERATIONS-14 is triggered to raise a backfill `operations.hire_requested`.

### SLA and controls

- SLA: equipment recovered within 5 business days of the last working day (KPI asset_recovery_pct: 90 / 95 / 97%); desk released on the last day; delegations reassigned within 2 business days.
- Control: summary dismissals and security-sensitive departures: pass and kit recovered the same day with the manager present, and IT Security is told immediately.
- Control: unrecovered devices are remote-wiped; the asset register shows the date of the wipe.

### Exceptions and escalation

- Leaver refuses to return equipment: People and the General Counsel decide the letter and any recovery steps; Operations does not contact the leaver beyond the courier request.
- Device lost or stolen: report to IT Security as a security event (and the police if stolen); the CISO assesses whether the data loss is a personal data breach (General Counsel with CISO and CEO decide on ICO notification within 72 hours, COMPANY.md §9.3).

---

## SOP-OPERATIONS-07: Event, engagement and staffing logistics

**Owner**: Procurement and Workspace Specialist (COO until Q4 FY2026).
**Trigger**: `marketing.event_scheduled` (an event needs venue, catering and AV), `delivery.engagement_kickoff` (an engagement starts), `delivery.staffing_requested` (Delivery needs people, which drives kit and desk demand).
**Inputs**: event details (`event_id`, `event_type`, `city`, `capacity`, `due_day`, `estimated_cost_gbp`, `needs`), engagement details (`engagement_id`, `client_id`, `start_day`, `team_fte`, `ai_agents`), staffing details (`team`, `needed_by_day`, `shortfall_fte`, `sourcing`), approved venue and supplier lists, desk occupancy forecast, marketing and delivery budgets.

### Steps

1. [agent] On `marketing.event_scheduled`, compare `estimated_cost_gbp` with THREE_QUOTE_THRESHOLD_GBP. At or above it, issue an RFQ (three venue quotes) through SOP-OPERATIONS-01 with the event's `needs`; below it, take one written quote from an approved venue and place the order at level 1 where the vendor is approved. Marketing's events budget is the funding source (`department` = `marketing`).
2. [human] Procurement and Workspace Specialist confirms venue security, accessibility, insurance (public liability), and a data-protection clause for any attendee data handled by the venue; schedules the run-of-show with Marketing's Events Specialist.
3. [agent] On `delivery.engagement_kickoff`, create the engagement logistics checklist: engagement room or client-site arrangements, visitor passes, secure engagement workspace access request to IT Security, and any engagement-specific purchases (printing, travel kit) within the engagement's expense budget; orders below THREE_QUOTE_THRESHOLD_GBP are placed at level 1 and larger ones go through SOP-OPERATIONS-01.
4. [agent] On `delivery.staffing_requested`, convert `team` and `shortfall_fte` into planned starters, associates and contractors, add them to the desk and kit forecast for `needed_by_day`, and compare with the stock buffer and desk capacity (STOCK_BUFFER_PCT and DESK_OCCUPANCY_WARNING_PCT).
5. [agent] If the forecast exceeds stock plus buffer, order the shortfall: within AGENT_PO_LIMIT_GBP at level 1, otherwise through SOP-OPERATIONS-02. Include contractors and associates: building passes and kit are issued with an end date and return on the contract end date.
6. [human] Workspace and Facilities Associate (Procurement and Workspace Specialist until Q4 FY2027) confirms the logistics 2 business days before the event or start day and files the closure record (attendance, spend against budget) within 5 business days after.

### Outputs and messages

- `operations.procurement_order_placed` (recipient `finance`): venue, catering, AV, kit and engagement orders, with `department` set to the budget holder (`marketing`, `delivery`, or `operations`) and keys as in SOP-OPERATIONS-02.
- Tasks for the Workspace and Facilities Associate; no other topics.

### SLA and controls

- SLA: event RFQ issued within 2 business days of `marketing.event_scheduled`; logistics checklist created the same day as `delivery.engagement_kickoff`; logistics confirmed 2 business days before the event or start day.
- Control: event orders follow the same quote and approval thresholds as all spend; an event whose cost estimate rises above the next threshold is re-approved at the higher level.
- Control: gifts, hospitality and speaker fees follow the Bribery Act 2010 policy and are logged; no alcohol is bought without the budget holder's approval.
- Control: kit and passes issued to contractors and associates are recovered on contract end (SOP-OPERATIONS-06 applies).

### Exceptions and escalation

- Event venue cancels: re-source within 5 business days; Marketing and the COO are told the same day; deposits recovered under the contract by Legal.
- Delivery shortfall is filled by a subcontractor on short notice: kit and pass lead time of 2 days (WORKSPACE_KIT_LEAD_TIME_DAYS) is warned to Delivery and People.

---

## SOP-OPERATIONS-08: Compliance findings and regulatory change actions

**Owner**: Compliance and Risk Specialist (COO until Q2 FY2027).
**Trigger**: `legal.compliance_finding_raised` (a finding with `finding_id`, `severity`, `areas`, `action_owner`, `due_day`) and `legal.regulatory_change_noted` (a change in law or regulation affecting Operations).
**Inputs**: Legal's finding and impact assessment, the compliance action register, the policy and procedure library, the operating-risk register, owner availability, the relevant regulations (UK GDPR and DPA 2018, health and safety and fire law, supplier due diligence, Companies House and HMRC obligations, EU AI Act alignment for client AI systems).

### Steps

1. [agent] On `legal.compliance_finding_raised`, create an action `CA-nnnn` linked to `finding_id` with the severity and the due date: the earlier of Legal's `due_day` and the severity SLA (COMPLIANCE_SLA_CRITICAL 5, HIGH 10, MEDIUM 20, LOW 40 business days; 7, 14, 28, 56 sim days). If the finding names a vendor (`vendor_id`), mark the vendor `pending` in SOP-OPERATIONS-03 until the action closes.
2. [human] Compliance and Risk Specialist (COO until Q2 FY2027) confirms the action owner: Operations if `action_owner` is `operations` or the action is operational (premises, suppliers, records, health and safety), otherwise the department named by Legal; agrees the plan and evidence required with the General Counsel's team; records the blocker if the action depends on a third party.
3. [agent] On `legal.regulatory_change_noted`, assess impact on Operations (suppliers, premises, record keeping, procurement controls, continuity) from Legal's `impact_areas`, create actions for each impact with a due day ahead of the `effective_in_days` date, and update the operating-risk register.
4. [agent] Track each action weekly: status, owner, days to due, blockers and evidence collected. Send a reminder at 50% and at 80% of the elapsed period.
5. [human] Action owner completes the work and submits evidence (policy updated, supplier contract amended, training done, certificate renewed, inspection record).
6. [human] Compliance and Risk Specialist (COO until Q2 FY2027) reviews the evidence against the finding and attests closure with a name and date; the General Counsel's team may reject the evidence.
7. [agent] After the human attestation, emit `operations.compliance_action_completed` to Legal with `closed_day` and `on_time`. The agent never closes an action itself.
8. [agent] On the due day, if the action is open, escalate to the COO; COMPLIANCE_ESCALATION_DAYS (7) after the due day, escalate to the CEO (and, for critical findings, mention at the next Executive meeting).

### Outputs and messages

- `operations.compliance_action_completed` (recipient `legal`): `finding_id`, `action_id`, `title`, `severity`, `due_day`, `closed_day`, `on_time` (bool), `attested_by` (role title), `evidence_ref`, `policy_update_required` (bool), `summary`.
- Weekly open-actions report to the COO and General Counsel; tasks for action owners.

### SLA and controls

- SLA: action opened and owner assigned within 1 business day of the finding; closure within the severity SLA (KPI compliance_actions_on_time_pct: 90 / 93 / 95%); weekly open-actions report every Friday; overdue count against the KPI overdue_compliance_actions.
- Control: only a human attestation closes an action; evidence is retained for at least 6 years or the legal retention period, whichever is longer.
- Control: Operations never interprets legal advice or notifies regulators; those are for the General Counsel (COMPANY.md §9.4).
- Control: extensions to a due day set by Legal need Legal's written agreement, recorded with the reason.

### Exceptions and escalation

- Critical finding unresolved at 3 business days: COO, General Counsel and CEO review daily until closed.
- Action owner in another department does not respond: COO escalates to that department's head after 2 business days.
- Finding that implies a personal data breach: hand to IT Security and Legal at once (SOP-IT_SECURITY incident process); the 72-hour ICO clock is managed by Legal.

---

## SOP-OPERATIONS-09: Policy updates and procedure alignment

**Owner**: Compliance and Risk Specialist (COO until Q2 FY2027).
**Trigger**: `legal.policy_update_published` (a new or amended policy with `policy_id`, `title`, `version`, `effective_day`, `training_required`, `audiences`).
**Inputs**: the policy text, the operations procedures and checklists (this document, vendor and procurement procedures, workspace, health and safety and continuity procedures), the compliance action register, staff acknowledgement records from People.

### Steps

1. [agent] Match the policy to operations procedures by topic and list the SOPs and checklists affected; open a task for each.
2. [human] Compliance and Risk Specialist (COO until Q2 FY2027) updates procedures, forms, supplier terms and templates; where supplier contracts are affected, Legal approves the clause changes.
3. [agent] Track the update to completion and compare with the effective day; notify action owners and the COO of anything not aligned 5 business days before `effective_day`.
4. [human] Operations Manager (COO until Q3 FY2027) approves the revised procedures; People assigns training and records acknowledgement.
5. [agent] Update the policy-alignment record; if the policy closes a finding, link it to the action in SOP-OPERATIONS-08 for attestation.

### Outputs and messages

- No cross-department topic is emitted. Outputs: updated procedures, aligned register, tasks and `operations.activity.policy_aligned` log events. Closure of a related finding is reported through `operations.compliance_action_completed` in SOP-OPERATIONS-08.

### SLA and controls

- SLA: procedures aligned within POLICY_ALIGNMENT_DAYS (10 business days; 14 sim days) of publication and before `effective_day`.
- Control: version control on every procedure; the effective version at any date is reproducible for an audit (ISO 27001, SOC 2).

### Exceptions and escalation

- Policy conflicts with an existing supplier contract: Legal advises; Operations records a risk acceptance approved by the COO until the contract can be renegotiated.
- Alignment not feasible by the effective date: COO agrees a dated plan with the General Counsel.

---

## SOP-OPERATIONS-10: Business continuity, incident support and crisis logistics

**Owner**: Operations Manager (COO until Q3 FY2027).
**Trigger**: `it_security.incident_detected` (a security incident with `incident_id` and `severity`), `it_security.incident_resolved` (restoration and lessons), `executive.crisis_declared` (a company-wide crisis); and the continuity test schedule (below).
**Inputs**: the continuity plan (critical processes, systems tiers, people and supplier dependencies, alternate arrangements), the vendor register (critical vendors), the incident record (`incident_id`, `severity`, systems affected, detection and resolution days, restore time), crisis declaration details, the test calendar and previous test findings.

### Steps

1. [agent] On `it_security.incident_detected` with `severity` of `high` or `critical`, activate continuity logistics: list affected Tier-1 and Tier-2 systems and the processes that depend on them, check the vendor register for the affected third parties, pre-position alternate arrangements (remote working, alternate site, comms channel) and open a continuity task for the Operations Manager (COO until Q3 FY2027). For `low` and `medium`, record the incident only.
2. [human] Operations Manager (COO) confirms which continuity arrangements are needed, authorises alternate workspace or equipment orders (see the emergency rule below), and tells the COO and the incident lead (CISO) of any business-process impact.
3. [agent] On `executive.crisis_declared`, open the crisis logistics checklist: confirm contact trees, alternate premises, supplier and vendor contacts and critical deliveries; activate the emergency order rule; record the declaration in the continuity log.
4. [human] Emergency orders: an order up to EMERGENCY_ORDER_LIMIT_GBP (£10,000) without three quotes needs CFO approval on the COO's recommendation; above that, the standard ladder applies with a same-day approval SLA. Each emergency order is flagged `exception: emergency` and reviewed within 10 business days.
5. [agent] On `it_security.incident_resolved`, compute the recovery result: actual restore hours against RTO_TIER1_HOURS (4) or RTO_TIER2_HOURS (24) by the highest tier affected, and recovery point loss against RPO_TIER1_HOURS (1) or RPO_TIER2_HOURS (24). If the incident was high or critical, or continuity arrangements were activated, record it as a live-incident continuity test and schedule the lessons-learned review.
6. [human] Operations Manager (COO) runs the lessons-learned review within 5 business days of resolution (10 business days after a crisis declaration), records findings with owners and due dates, and updates the continuity plan.
7. [agent] Emit `operations.continuity_test_completed` once the review is complete, including for scheduled tabletop and technical exercises (below).
8. [agent] Schedule the annual test programme (below), prepare the scenario pack and collect results: findings become compliance-style actions tracked under SOP-OPERATIONS-08.

Test programme: FY2026 two tabletop exercises (cyber incident with loss of the engagement workspace; loss of the London HQ and a critical supplier); FY2027 two tabletop and two technical failover tests (jointly with IT Security, Tier-1 recovery within 4 hours); FY2028 those four plus two vendor-failure or live-incident scenarios. A live high or critical incident with a completed review counts as a test.

### Outputs and messages

- `operations.continuity_test_completed` (recipient `*`; subscribers executive, it_security): `test_id` (`BCT-0001`), `scenario`, `test_type` (`tabletop`|`technical`|`live_incident`|`vendor_failure`), `incident_id` (if live), `severity`, `rto_met` (bool), `rpo_met` (bool), `rto_hours_actual`, `findings` (list), `summary`.
- Tasks for continuity actions; emergency orders through SOP-OPERATIONS-02 (`operations.procurement_order_placed`, `exception: emergency`).

### SLA and controls

- SLA: continuity logistics active within 1 hour of a high or critical `it_security.incident_detected`; lessons-learned review and test result filed within 5 business days of `it_security.incident_resolved` (10 business days after `executive.crisis_declared`); two tests in FY2026, four in FY2027, six in FY2028 (KPI continuity_tests_completed); RTO met in 80 / 90 / 95% of tests (KPI continuity_rto_met_pct).
- Control: the Business Continuity Agent cannot declare a crisis or invoke a vendor's disaster-recovery clause; it only records and proposes.
- Control: continuity evidence is filed as ISO 27001 and SOC 2 evidence by IT Security on receipt of `operations.continuity_test_completed`.
- Control: client-contractual continuity commitments (Keep Enterprise 24x7 incident cover, COMPANY.md §3.3) are checked against the plan annually.

### Exceptions and escalation

- RTO missed in a Tier-1 test: a corrective action with owner and date within 5 business days; a second consecutive miss goes to the COO and CISO and, if material, to the Audit and Risk Committee chair (Marcus Ellery) through the CEO.
- Incident affecting personal data: Legal and IT Security lead on notification; Operations supports logistics only (SOP-IT_SECURITY incident process).
- Crisis declared with no premises: remote working with approved devices; the COO authorises temporary space (CFO if above EMERGENCY_ORDER_LIMIT_GBP).

---

## SOP-OPERATIONS-11: Third-party vulnerability and asset response

**Owner**: Operations Manager (COO until Q3 FY2027).
**Trigger**: `it_security.vulnerability_found` (a vulnerability with `vulnerability_id`, `severity`, the affected asset or supplier component, and a remediation deadline).
**Inputs**: the vulnerability record, the asset register (laptops, network and facilities devices, peripherals), the vendor register and contracts, supplier patch notices, IT Security's remediation deadline.

### Steps

1. [agent] Map the vulnerability to Operations-managed assets and suppliers: facility devices (door access, visitor systems, printers, meeting-room equipment), hardware in the asset pool, and third-party vendors whose products or services are affected. Record the owners.
2. [agent] If a vendor product is affected, check the vendor's patch status and contract (patch and notification obligations) and open a vendor issue in SOP-OPERATIONS-04; for a high or critical case emit `operations.vendor_review_requested` with `review_reason` set to `incident`.
3. [human] Operations Manager (COO until Q3 FY2027) agrees the remediation plan with IT Security within 2 business days for high or critical items: patch window, vendor fix, replacement or isolation of the asset.
4. [agent] If replacement hardware is needed, create the order through SOP-OPERATIONS-02: within AGENT_PO_LIMIT_GBP at level 1 (budget holder `it_security` for devices); otherwise to the approver. Place the order the same day for a critical item.
5. [human] Workspace and Facilities Associate (Procurement and Workspace Specialist until Q4 FY2027) executes the physical steps (swap, isolation, collection) and updates the asset register.
6. [agent] Close the item when IT Security confirms retest; record the outcome and the time to remediate.

### Outputs and messages

- `operations.procurement_order_placed` (recipient `finance`) for replacement hardware or urgent supplier fixes: keys as in SOP-OPERATIONS-02, with `exception` set to `emergency` when the three-quote rule is waived under EMERGENCY_ORDER_LIMIT_GBP.
- `operations.vendor_review_requested` for a vendor-related high or critical vulnerability, keys as in SOP-OPERATIONS-01 (`review_reason` = `incident`).
- Remediation tasks for the Workspace and Facilities Associate.

### SLA and controls

- SLA: affected assets and suppliers identified within 1 business day; remediation plan within 2 business days for high or critical, 10 business days for medium; remediation inside the deadline IT Security sets.
- Control: replacement orders still follow the ladder and the single-source emergency rule; split-order detection applies to bulk replacements.

### Exceptions and escalation

- Vendor will not patch: COO, CISO and General Counsel decide on replacement and contract remedies.
- No replacement available inside the deadline: isolate the asset and escalate to IT Security.

---

## SOP-OPERATIONS-12: Process improvement and PMO

**Owner**: Operations Manager (PMO Lead for programmes from Q3 FY2028; COO until Q3 FY2027).
**Trigger**: `data.data_quality_issue_raised` (a recurring data defect points to a broken process), `executive.okrs_set` (new objectives for the period), `executive.strategy_updated` (a change to the strategy in COMPANY.md).
**Inputs**: the data-quality issue (`issue_id`, `severity`, `check`, `dataset`, `source_department`, `due_day`), the OKRs and strategy changes, the programme portfolio and RAID logs, the benefits log, the process library, Finance's validation rules.

### Steps

1. [agent] On `data.data_quality_issue_raised`, log the issue against the process behind the dataset and count recurrences per `check` and `source_department` over a rolling 90 days. Severity `low` or `medium` with fewer than two occurrences is logged and tracked only.
2. [agent] For a qualifying issue (severity `high` or `critical`, or two or more occurrences in 90 days), draft a process improvement `PI-nnnn`: affected process, root cause hypothesis, change proposed, owner, implementation cost and the annualised saving calculated as occurrences per year multiplied by rework hours multiplied by NOTIONAL_HOURLY_COST_GBP (£45). Rework hours per occurrence: low 4, medium 12, high 40, critical 80.
3. [human] Operations Manager (COO until Q3 FY2027) and the process owner validate the estimate; Finance validates any cash saving; payback must be within PROCESS_MAX_PAYBACK_MONTHS (12).
4. [agent] If the annualised saving is at least PROCESS_PROPOSAL_MIN_SAVING_GBP (£10,000) and the change touches a client-facing process or costs more than £25,000, emit `operations.process_improvement_proposed` to Executive; below the threshold the improvement is tracked and counted in process_improvements_adopted without being published.
5. [agent] On `executive.okrs_set`, map each objective that depends on an operations capability to an internal programme or project, update the portfolio and the RAID log, and create tasks with owners and milestone dates; send the plan to the COO for approval within 10 business days.
6. [agent] On `executive.strategy_updated`, assess the impact on programmes, spend, premises and vendors, re-baseline the portfolio where needed (a re-baseline counts as a miss for programme_on_time_pct), and brief the COO.
7. [human] PMO (Operations Manager; PMO Lead from Q3 FY2028) runs the monthly steering meeting, updates the benefits log and reports programme_on_time_pct, process_improvements_adopted and process_savings_gbp.
8. [human] After go-live, run a 90-day post-implementation check; only then count the saving in process_savings_gbp, validated by Finance.

### Outputs and messages

- `operations.process_improvement_proposed` (recipient `executive`): `proposal_id` (`PI-0001`), `title`, `process`, `trigger_source` (`data_quality`|`okrs`|`strategy`|`review`), `source_issue_id`, `annualised_saving_gbp`, `implementation_cost_gbp`, `payback_months`, `owner` (role title), `due_day`, `severity`, `summary`.
- Programme portfolio, RAID log updates and steering papers; tasks for process owners.

### SLA and controls

- SLA: programme plan aligned within 10 business days of `executive.okrs_set` or `executive.strategy_updated`; qualifying improvement drafted within 10 business days of the issue; steering meeting monthly; savings counted only after 90 days and Finance validation.
- Control: agents propose only; the PMO and Process Agent cannot start a programme, reassign people or budget, or publish below the £10,000 threshold.
- Control: no benefit is double-counted: procurement savings (SOP-OPERATIONS-01) and process savings are measured on different events.

### Exceptions and escalation

- Proposal competes with a committed programme: COO decides order and funding; CEO if it changes the OKRs.
- Data-quality issue is a Data or Product fault rather than a process fault: forward to the source department's head and close the Operations item.

---

## SOP-OPERATIONS-13: Operations budget cycle and spend tracking

**Owner**: COO.
**Trigger**: `finance.budget_cycle_opened` (the annual budget cycle `BUD-yyyy` opens in Q4) and `executive.budget_approved` (the approved budget is released).
**Inputs**: the budget cycle (`budget_cycle_id`, `fiscal_year`, deadline), the COMPANY.md §5.4 envelope (operations: people £200k / £400k / £750k, non-people £100k / £300k / £900k), the headcount and hiring plan in `blueprint.md`, the agent plan, the spend register, vendor renewals and the workspace plan.

### Steps

1. [agent] On `finance.budget_cycle_opened`, open a budget task with the cycle id and the submission day (OPS_BUDGET_SUBMISSION_DAY, day 21), pull the operations spend by line, renewals due, planned headcount and agent plan, and prepare a draft submission by line.
2. [human] COO reviews the draft with the Operations Manager (from Q3 FY2027): headcount and start quarters, workspace and New York plan, vendor contract renewals, compliance and continuity costs, savings commitments.
3. [agent] Validate the draft: people cost equals average FTE multiplied by loaded cost (base x 1.28); non-people lines have owners; total is within 5% of the COMPANY.md §5.4 envelope, otherwise flag the difference for the COO.
4. [human] COO approves the submission; where it exceeds the envelope the COO attaches the business case; spend above the envelope needs the CFO (above £50k) or CEO (above £250k) approval under COMPANY.md §9.3.
5. [agent] Emit `operations.budget_submitted` to Finance with the people, non-people and total amounts, headcount and agents.
6. [agent] On `executive.budget_approved`, load the approved budget by line and quarter, set the 80% budget-line warnings and re-set the SOP-OPERATIONS-02 budget checks. Tell the owners of each line.
7. [human] COO reviews monthly spend against budget with the Operations Analyst (Operations Manager from Q3 FY2027); variance above 5% year to date is investigated, above 10% or £25k is expected to be flagged by Finance (`finance.budget_variance_flagged`).

### Outputs and messages

- `operations.budget_submitted` (recipient `finance`): `budget_cycle_id`, `fiscal_year`, `department` (`operations`), `people_gbp`, `non_people_gbp`, `total_gbp`, `amount_gbp`, `headcount`, `agents`, `summary`.
- Budget loaded record and tasks for line owners; no other topics.

### SLA and controls

- SLA: submission by day 21 of the cycle; approved budget loaded within 3 business days of `executive.budget_approved`; monthly spend review by working day 8.
- Control: all submissions use the same people-cost rule (loaded = base x 1.28); budget phasing follows the hiring plan; contingency (FY2028, £30k) is COO-held and releases only within COMPANY.md §9.3.
- Control: budget variance KPI (budget_variance_pct: 5 / 4 / 3%) tracked monthly.

### Exceptions and escalation

- Envelope cannot support a business need: COO takes the case to the CFO and CEO through Finance's consolidation (`finance.budget_consolidated`).
- Approved budget lower than submitted: COO re-phases hiring and agent start dates and records the decision.

---

## SOP-OPERATIONS-14: Operations capacity and hiring

**Owner**: COO.
**Trigger**: quarterly schedule (first Monday of the quarter); a trigger breach recorded during the quarter.
**Inputs**: workload counters (POs per month, vendor reviews open, starters per month, open compliance actions per specialist, programmes active), KPI results, the hiring plan, agent register, attrition and leaver data, the approved budget.

### Steps

1. [agent] Compute the capacity indicators: purchase orders raised per month, open vendor reviews, starters per month per Workspace and Facilities Associate, open compliance actions per Compliance and Risk Specialist, concurrent programmes per PMO resource, KPI attainment (average attainment of the 16 KPIs).
2. [agent] Compare each indicator with the trigger in `blueprint.md` section 5 (for example more than 15 purchase requests a month with no Procurement and Workspace Specialist; more than 8 starters a month; open compliance actions above 15 per specialist for two consecutive months; more than 150 active vendors).
3. [human] COO reviews the indicators with the Operations Manager (from Q3 FY2027), decides whether to hire, add an agent, move work between people or defer, and records the decision.
4. [agent] For each approved hire, emit `operations.hire_requested` to People with the role, level, band, start quarter and justification; the requisition then follows `people.requisition_opened` and `executive.headcount_approved` (COMPANY.md §9.3).
5. [agent] For a leaver in Operations (backfill) raise `operations.hire_requested` with `reason` of `backfill` within 5 business days of the leaver notice.
6. [human] COO updates the agent register for each agent added (owner, purpose, limits) with Data and IT Security (COMPANY.md §9.4).

### Outputs and messages

- `operations.hire_requested` (recipient `people`): `department` (`operations`), `role` (a title from `blueprint.md` section 3), `level` (level key), `salary_band_gbp`, `reason` (`growth`|`backfill`), `start_quarter`, `justification`, `severity`, `summary`.
- Quarterly capacity note to the COO and Finance; tasks for agent provisioning (5 days).

### SLA and controls

- SLA: capacity review in the first week of each quarter; request raised within 5 business days of a trigger breach; agent provisioned within 5 days (COMPANY.md §8, assumption 3).
- Control: no hire request is raised for a role outside the plan (2 / 6 / 12 humans, COMPANY.md §6.1) without COO approval and the CEO headcount approval route.
- Control: hiring requests always name a role title from `blueprint.md`.

### Exceptions and escalation

- Trigger breached but budget does not allow the hire: COO decides between a contractor (People handles IR35), an agent, or deferral, and informs the CFO.
- Key-person loss: the COO covers the seat and raises a backfill the same day.

---

## Topic coverage

Subscribed topics and the SOP that handles each: `data.data_quality_issue_raised` (12), `delivery.engagement_kickoff` (07), `delivery.staffing_requested` (07), `executive.budget_approved` (13), `executive.crisis_declared` (10), `executive.okrs_set` (12), `executive.strategy_updated` (12), `external.vendor_quote_received` (01), `finance.budget_cycle_opened` (13), `it_security.access_provisioned` (05), `it_security.incident_detected` (10), `it_security.incident_resolved` (10), `it_security.vendor_risk_assessed` (03), `it_security.vulnerability_found` (11), `legal.compliance_finding_raised` (08), `legal.policy_update_published` (09), `legal.regulatory_change_noted` (08), `marketing.event_scheduled` (07), `people.employee_left` (06), `people.new_hire_started` (05).

Published topics and the SOPs that emit them: `operations.vendor_review_requested` (01, 03, 04, 11), `operations.vendor_approved` (03), `operations.procurement_order_placed` (01, 02, 05, 07, 10, 11), `operations.workspace_ready` (05), `operations.compliance_action_completed` (08), `operations.continuity_test_completed` (10), `operations.process_improvement_proposed` (12), `operations.budget_submitted` (13), `operations.hire_requested` (14).
