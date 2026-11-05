# Finance Standard Operating Procedures

Department: `finance` (agent class `FinanceAgent`). Head: Hannah Whitcombe, Chief Financial Officer (COMPANY.md §9.2). Scope: FP&A, accounting, billing, collections, treasury, budgeting and pricing checks. UK context: HMRC (VAT under Making Tax Digital, PAYE Real Time Information, Corporation Tax), Companies House, UK Late Payment of Commercial Debts (Interest) Act, UK GAAP (FRS 102). Team in FY2026: 2 humans and 2 AI agents (COMPANY.md §6.1), so segregation of duties is achieved by agent-prepares / human-approves / CFO-releases rather than by headcount. All figures are modelled assumptions, not real data.

Conventions used throughout:

- `[human]` steps are performed by the CFO, or by the Finance Manager once in post (joins Q4 FY2026; until then the CFO is the only human and performs every `[human]` step marked Finance Manager); `[agent]` steps by the Finance agent working under a named human owner. Agents may draft, analyse, monitor and propose; they may not approve or release payments above £10,000, sign contracts or notify regulators (COMPANY.md §9.4).
- Money in message bodies is `amount_gbp` ex VAT unless the key says `total_gbp`. VAT is 20% for UK clients (COMPANY.md §7). US clients are quoted in USD at £1 = $1.27 (COMPANY.md §1) from FY2027.
- SLAs in "business days" exclude UK bank holidays. Sim days are integers from Day 0 = 2026-01-05 (COMPANY.md §1); `due_day` keys are sim days.
- Business IDs follow CONVENTIONS section 4: `CL-0001`, `DL-0001`, `PR-0001`, `CT-0001`, `EN-0001`, `INV-2026-0001`, `REQ-0001`, `VN-0001`, `BUD-2027` (budget cycle id carries the fiscal year being budgeted, so the cycle opened in October 2026 is `BUD-2027`).

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-FINANCE-01 | Pricing check on proposals | `sales.proposal_requested`, `delivery.scoping_completed` | Finance Manager (agent: pricing desk) | Pricing check completed within 1 business day of scoping |
| SOP-FINANCE-02 | Deal desk, discounts and price changes | `sales.deal_approval_requested`, `executive.deal_decision_made`, `product.pricing_change_proposed`, `executive.pricing_change_approved` | CFO | Finance opinion within 1 business day; discount >10% decision within 2 business days |
| SOP-FINANCE-03 | Contract to billing schedule | `sales.deal_won`, `legal.contract_signed`, `delivery.engagement_kickoff` | Finance Manager | Billing schedule within 2 business days of signed contract |
| SOP-FINANCE-04 | Milestone invoicing and revenue recognition | `delivery.milestone_reached` | Finance Manager | Invoice issued within 2 business days of milestone acceptance |
| SOP-FINANCE-05 | Change orders and engagement close-out | `delivery.scope_change_requested`, `delivery.engagement_completed` | Finance Manager | Change order priced within 2 business days; close-out within 5 business days |
| SOP-FINANCE-06 | Cash application | `external.client_payment_received` | Finance Manager (agent: cash application) | Matched within 1 business day; unmatched cash investigated within 3 |
| SOP-FINANCE-07 | Collections ladder | Daily schedule (ageing run, 07:00 UK) | CFO (agent: collections) | Reminder day 31, call day 38, CFO escalation day 45, legal letter day 60 |
| SOP-FINANCE-08 | Disputes, credit notes and bad debt | `legal.client_dispute_raised` | CFO | Dispute hold applied same day; credit note decision within 5 business days |
| SOP-FINANCE-09 | Keep renewals, churn and revenue reversal | `customer_success.renewal_due`, `sales.renewal_proposal_sent`, `customer_success.renewal_confirmed`, `customer_success.client_churned` | Finance Manager | Renewal pricing check within 2 business days; churn billing stop same day |
| SOP-FINANCE-10 | Month-end close | Schedule: working day 1 of each month | CFO | Close complete by working day 8 in FY2026 (WD6 FY2027, WD5 FY2028); variance flags same day |
| SOP-FINANCE-11 | Cash forecast and treasury | Weekly schedule (Monday), `data.forecast_updated`, `delivery.capacity_forecast_updated`, `data.kpi_report_published` | CFO (agent: treasury analyst) | 13-week forecast refreshed every Monday by 12:00; ad hoc refresh within 1 business day of an input change |
| SOP-FINANCE-12 | Annual budget cycle | Schedule: 1 October opens cycle; `<dept>.budget_submitted` from all departments; `executive.budget_approved` | CFO | Cycle opened 1 Oct; submissions due day 21 of cycle; consolidated within 3 business days of last submission |
| SOP-FINANCE-13 | Headcount cost control and payroll | `people.requisition_opened`, `executive.headcount_approved`, `people.offer_accepted`, `people.new_hire_started`, `people.employee_left`, `people.contractor_engaged` | Finance Manager | Headcount cost check within 2 business days of requisition; payroll data frozen WD-5 of each month |
| SOP-FINANCE-14 | Vendor onboarding, procurement and supplier payments | `operations.vendor_review_requested`, `it_security.vendor_risk_assessed`, `operations.vendor_approved`, `operations.procurement_order_placed`, `marketing.campaign_launched` | Finance Manager | Vendor set-up within 2 business days of approval; supplier invoices paid on agreed terms (default 30 days) |
| SOP-FINANCE-15 | Board reporting, strategy, OKRs and crisis response | `executive.board_meeting_held`, `executive.okrs_set`, `executive.strategy_updated`, `executive.crisis_declared` | CFO | Board pack draft 5 business days before board; crisis liquidity view within 24 hours |
| SOP-FINANCE-16 | Finance capacity and hiring | Quarterly schedule (first Monday of the quarter) | CFO | Capacity review each quarter; request raised within 5 business days of a trigger breach |

Topic coverage (checked at the end of this document): every subscribed topic is the trigger of, or an explicit sub-trigger inside, at least one SOP above, and every published topic appears in the outputs of at least one SOP.

---

## SOP-FINANCE-01: Pricing check on proposals

**Owner**: Finance Manager, with the Finance agent as pricing desk. CFO is the escalation point.
**Trigger**: `sales.proposal_requested` (sales asks for pricing support on a proposal) and `delivery.scoping_completed` (delivery has sized the work). Both are needed; the check runs when the second arrives, or on the first plus a 2 business day timer.
**Inputs**: `proposal_id`, `deal_id`, `client_id`, `service_line`, `tier`, requested `amount_gbp`, requested discount, payment terms requested, delivery scoping (days by level, agent-days, expected subcontractors, expected expenses), price list (COMPANY.md §3), rate card (COMPANY.md §3.5), standard terms (COMPANY.md §7), approval limits (COMPANY.md §9.3).

### Steps

1. [agent] Match the two triggers by `proposal_id`; if only one is present after 2 business days, ask the missing department via a task and log the delay.
2. [agent] Compare the proposed fee to list price for the tier (for example Forge Build £260,000, Compass Sprint £120,000, Keep Plus £18,000 per month) and compute the discount percentage = (list - proposed) / list.
3. [agent] Cost the engagement bottom-up: delivery days x loaded day cost by level, agent-days at £350 rate-card equivalent cost basis (internal cost £20k to £35k per agent-year), subcontractors, capped expenses (5% of fee, COMPANY.md §7). Compute engagement gross margin = (fee - cost) / fee.
4. [agent] Test against policy: discount <= 10% (sales head authority); engagement gross margin >= 40% in FY2026 and >= 50% in FY2027 and FY2028 (modelled floors, set below the company margin of 48% / 58% / 64% to allow for loss-leading Spark and Pilot entry deals); payment terms must be net 30, 30/40/30 milestones for Compass and Forge, monthly in advance for Keep.
5. [agent] Flag any deviation: discount >10%, non-standard terms (net 60, milestone weighting changes, payment on completion only), fee below floor margin, uncapped expenses, USD billing without hedge note.
6. [human] Finance Manager reviews the draft check and any flags, and signs off. Deviations go to SOP-FINANCE-02.
7. [agent] Emit the result to sales and record the check in the proposal file with the calculation attached.

### Outputs and messages

- `finance.pricing_check_completed` to `sales`: `proposal_id`, `deal_id`, `client_id`, `service_line`, `tier`, `amount_gbp`, `list_price_gbp`, `discount_pct`, `margin_pct`, `terms_ok` (bool), `approval_required` (`none` | `finance_and_ceo`), `severity` (`low` when compliant, `medium` for deviation, `high` for below-floor margin), `summary`.
- A finance task `pricing-review/<proposal_id>` if human review is outstanding.

### SLA and controls

- SLA: check issued within 1 business day of both inputs; if the deal is >= £500k total contract value, flag to SOP-FINANCE-02 in the same message.
- Control: no proposal leaves sales with a discount >10% or non-standard payment terms without a recorded `approval_required` decision (COMPANY.md §9.3).
- Control: agent cannot waive a policy breach; it can only flag it. Margin floor overrides need CFO plus CEO.
- Evidence: calculation workbook reference stored with `proposal_id`; sample of 10% of checks re-performed monthly by the Finance Manager.

### Exceptions and escalation

- Fee below margin floor: CFO review within 1 business day; CFO may approve a loss-leader up to a £25,000 negative variance to floor, above that the CEO decides.
- Missing scoping after 2 business days: escalate to the delivery head (Oliver Thackeray) via task; sales is told pricing is provisional.
- USD quote (from FY2027): apply £1 = $1.27 planning rate and add a currency note; any other rate needs CFO approval.

---

## SOP-FINANCE-02: Deal desk, discounts and price changes

**Owner**: CFO (Hannah Whitcombe).
**Trigger**: `sales.deal_approval_requested` (deals >= £500k total contract value, or discount >10%, or non-standard terms), `executive.deal_decision_made` (the CEO or Board decision), `product.pricing_change_proposed` (a proposed list-price or packaging change), `executive.pricing_change_approved` (the approved change).
**Inputs**: `deal_id`, `client_id`, `amount_gbp` (total contract value), discount, terms, concentration data (client revenue as % of forecast annual revenue), pricing check from SOP-FINANCE-01, price book version, current rate card.

### Steps

1. [agent] On `sales.deal_approval_requested`, build the deal desk pack: total contract value, fee by line, margin, cash profile (milestone dates against 30/40/30), working-capital impact, DSO effect, client concentration against the 15% policy limit (COMPANY.md §8).
2. [human] CFO reviews the pack and records a written finance opinion (support, support with conditions, or oppose) for the CEO. Discounts >10% or non-standard terms need the CFO and CEO jointly (COMPANY.md §9.3); deals > £1.5m also go to the Board.
3. [agent] Attach the opinion to the deal record and send it to `executive` via the deal approval thread (task assigned to the CEO's office).
4. [agent] On `executive.deal_decision_made`, record the decision (approved, approved with conditions, declined) against the deal; update the pipeline-weighted cash forecast input (SOP-FINANCE-11).
5. [human] On `product.pricing_change_proposed`, Finance Manager models the revenue, margin and cash impact on the three service lines over 12 months, including effect on existing Keep CPI + 2% uplift (cap 7%, COMPANY.md §7) and Compass/Forge price lists.
6. [human] CFO submits the finance view to the CEO. No agent changes the price book.
7. [agent] On `executive.pricing_change_approved`, update the price book version, the pricing-check parameters (SOP-FINANCE-01) and the billing templates (SOP-FINANCE-03) with an effective date; changes never apply retrospectively to signed contracts.

### Outputs and messages

- `finance.pricing_check_completed` to `sales`: re-issued for deals changed after approval, with `deal_id`, `proposal_id`, `amount_gbp`, `discount_pct`, `approval_required`, `summary` (finance opinion).
- `finance.cash_forecast_updated` to `executive`, `data`: refreshed after a deal decision or price change that moves expected cash by more than £150,000 in the 13-week window (see SOP-FINANCE-11 for body keys).
- Task `deal-desk/<deal_id>` and `price-book/<version>` records.

### SLA and controls

- SLA: finance opinion within 1 business day of `sales.deal_approval_requested`; CFO and CEO decision on discount >10% within 2 business days.
- Control: price book is version-controlled; every deal references a version. Quarterly reconciliation of signed fees to price book by the Finance Manager.
- Control: no concession on payment terms is accepted verbally; it must be in the contract or schedule (SOP-FINANCE-03).

### Exceptions and escalation

- Concentration breach (a client would exceed 15% of forecast revenue): CFO tells the CEO and Board chair (Priya Raman) before signature.
- Deal declined after the pricing check was issued: mark the proposal closed, remove from forecast same day.
- Price change that conflicts with signed multi-year Keep terms: General Counsel (Callum Fraser) consulted via the `legal` task queue before approval.

---

## SOP-FINANCE-03: Contract to billing schedule

**Owner**: Finance Manager.
**Trigger**: `sales.deal_won` (open a customer record and credit check), `legal.contract_signed` (create the billing schedule), `delivery.engagement_kickoff` (confirm dates and activate the schedule).
**Inputs**: `deal_id`, `contract_id`, `client_id`, `client_name`, `service_line`, `tier`, `amount_gbp`, signed contract and order form, client billing contact, PO number, VAT status, kickoff date and milestone plan from delivery.

### Steps

1. [agent] On `sales.deal_won`, create the customer in the ledger (ledger id aligned to `client_id`), run a Companies House and credit-agency check (modelled: score >= 60 acceptable), and request VAT number validation for VAT-registered clients. Record the credit result.
2. [human] Finance Manager approves new-customer set-up, and any client with a credit score under 60 receives tighter terms (50% on signature) subject to CFO approval.
3. [agent] On `legal.contract_signed`, read the signed contract terms and compare them with the pricing check (SOP-FINANCE-01). Mismatches (fee, terms, expenses) are queued for human review and block issue of the schedule.
4. [agent] Draft the billing schedule. Compass and Forge: 30% on signature, 40% at the mid-point milestone, 30% on acceptance, expenses at cost capped at 5% of fee (COMPANY.md §7). Example, Forge Build £260,000: £78,000 on signature, £104,000 at mid-point, £78,000 on acceptance, plus 20% VAT on each. Keep: monthly in advance (Keep Plus £18,000 per month), 12-month minimum, uplift CPI + 2% capped at 7% at anniversary.
5. [human] Finance Manager reviews the schedule; CFO approves any schedule that departs from standard terms.
6. [agent] On `delivery.engagement_kickoff`, bind the schedule to the `engagement_id`, set `due_day` per milestone and set up revenue recognition: percentage-of-completion for fixed fee, straight-line monthly for Keep (COMPANY.md §7).
7. [agent] Issue the signature-milestone invoice immediately (SOP-FINANCE-04 step 4) so cash arrives with the engagement start.
8. [agent] Publish the schedule to delivery and customer success.

### Outputs and messages

- `finance.billing_schedule_created` to `delivery`, `customer_success`: `contract_id`, `engagement_id`, `client_id`, `client_name`, `service_line`, `tier`, `amount_gbp`, `schedule` (list of `{milestone, pct, amount_gbp, due_day}`), `terms` (`net_30`), `po_required` (bool), `summary`.
- `finance.invoice_issued` for the signature milestone (see SOP-FINANCE-04).

### SLA and controls

- SLA: schedule published within 2 business days of `legal.contract_signed`; signature invoice within 2 business days of signing.
- Control: three-way match between contract, pricing check and schedule (fee, terms, VAT) before publish; sum of milestones must equal contract value to the penny.
- Control: customer master-data changes (bank details, billing address) need a call-back to a known contact; never accept changes by email alone.

### Exceptions and escalation

- Contract signed with non-standard terms not seen in the pricing check: stop, escalate to CFO and General Counsel the same day.
- Kickoff slips >10 business days after signature: tell delivery and customer success, keep the signature invoice (it is earned on signature), defer the mid-point date.
- No client PO where the client requires one: hold the invoice, chase via customer success; invoices without a required PO are routinely rejected by procurement systems.

---

## SOP-FINANCE-04: Milestone invoicing and revenue recognition

**Owner**: Finance Manager.
**Trigger**: `delivery.milestone_reached` (client has accepted a milestone; for Keep, the monthly invoice runs on a schedule on the 25th for the next month).
**Inputs**: `engagement_id`, `milestone`, acceptance evidence (client sign-off email or acceptance certificate), billing schedule, `client_id`, percentage-complete from delivery, PO number, approved expenses.

### Steps

1. [agent] Match `milestone_reached` to the milestone in the billing schedule; reject milestone IDs that are not in the schedule and raise a task for delivery.
2. [agent] Verify acceptance evidence is attached and dated; the invoice date is the acceptance date or later, never earlier.
3. [agent] Pull approved, capped expenses billable at cost with receipts; confirm the engagement is within the 5% cap.
4. [agent] Draft the invoice: invoice id `INV-<year>-<nnnn>` (sequential, no gaps), amount, 20% VAT for UK clients, due date = invoice date + 30 days, PO number, remittance details, late-payment-interest wording (8% over base rate).
5. [human] Finance Manager approves every invoice before issue. Invoices over £100,000 ex VAT are also approved by the CFO.
6. [agent] Issue the invoice to the client billing contact, log it in the receivables ledger and set the collections clock (SOP-FINANCE-07).
7. [agent] Post revenue: fixed-fee engagements recognise revenue on percentage-of-completion using delivery's estimate; the gap between recognised revenue and billed amount is carried as accrued income (unbilled) or deferred income (billed ahead).
8. [human] Finance Manager reviews the percentage-of-completion estimate monthly with the engagement Manager at close (SOP-FINANCE-10) and records any estimate change as a catch-up.

### Outputs and messages

- `finance.invoice_issued` to `customer_success`, `data`: `invoice_id`, `client_id`, `engagement_id`, `milestone`, `amount_gbp`, `vat_gbp`, `total_gbp`, `due_day`, `po_number`, `service_line`, `summary`.

### SLA and controls

- SLA: invoice issued within 2 business days of milestone acceptance (COMPANY.md §7); target 95% on time, 100% within 4 business days.
- Control: the invoice sequence has no gaps or duplicates; the agent cannot delete an issued invoice, only raise a credit note (SOP-FINANCE-08).
- Control: segregation of duties: the agent drafts, the Finance Manager approves, nobody who approves an invoice can edit customer bank details.
- Control: monthly reconciliation of billing schedule against invoices issued, against delivery's milestone log.

### Exceptions and escalation

- Milestone reported by delivery without client acceptance: hold the invoice, ask the engagement Manager to obtain written acceptance; do not bill on delivery's word.
- Client disputes acceptance after invoice issue: SOP-FINANCE-08.
- Delivery reports a milestone earlier than scheduled by more than 30 days: CFO reviews for cut-off and cash-forecast effects before invoicing.

---

## SOP-FINANCE-05: Change orders and engagement close-out

**Owner**: Finance Manager.
**Trigger**: `delivery.scope_change_requested` (change order at rate card; core work is fixed fee), `delivery.engagement_completed` (final milestone accepted, wrap-up).
**Inputs**: `engagement_id`, `client_id`, change description, additional days by level, agent-days, rate card (COMPANY.md §3.5: Partner £2,400, Principal £1,800, Manager £1,400, Senior Consultant £1,050, Consultant £800, Analyst £550, AI agent-day £350), signed change order, final billing and cost position.

### Steps

1. [agent] On `delivery.scope_change_requested`, price the change at rate card by level and agent-day; subtotal, VAT and implied margin; flag any manual discount.
2. [human] Finance Manager confirms pricing and checks that the change order is signed by the client before work starts (COMPANY.md §7); legal is already notified by the topic.
3. [agent] Add a change milestone to the billing schedule, billed on completion of the change or monthly in arrears for changes longer than 4 weeks.
4. [agent] Update the engagement budget and forecast revenue; tell delivery if the new total pushes the contract into a higher approval tier (CEO deal approval at £500k, Board at £1.5m).
5. [agent] On `delivery.engagement_completed`, reconcile all milestones, change orders and expenses: confirm every accepted milestone is invoiced, release remaining deferred income, true up percentage-of-completion to 100%.
6. [agent] Compute final engagement gross margin and variance to the pricing check; store as pricing-model feedback.
7. [human] Finance Manager signs off close-out; any unbilled work above £5,000 is either billed or written off with CFO approval.
8. [agent] If the engagement has a Keep follow-on, hand the schedule to SOP-FINANCE-09.

### Outputs and messages

- `finance.pricing_check_completed` to `sales`: re-issued for the change order with `engagement_id`, `proposal_id` (change order reference), `amount_gbp`, `discount_pct`, `margin_pct`, `summary`.
- `finance.invoice_issued` for change orders and final milestone (body keys as SOP-FINANCE-04).
- `finance.billing_schedule_created` to `delivery`, `customer_success`: amended schedule with `engagement_id`, `schedule`, `amount_gbp` when a change order alters the total.

### SLA and controls

- SLA: change order priced within 2 business days; close-out reconciliation within 5 business days of completion.
- Control: no change work starts without a signed change order; delivery cannot log time against a change code until finance activates it.
- Control: write-offs of unbilled work require CFO approval above £5,000 and CEO above £25,000.

### Exceptions and escalation

- Work already performed without a signed change order: CFO and delivery head decide to bill, absorb or negotiate; the amount absorbed is recorded as scope leakage in the KPI pack.
- Final margin below 30%: post-mortem with delivery and sales, reported to the CEO in the next month-end pack.

---

## SOP-FINANCE-06: Cash application

**Owner**: Finance Manager, with the Finance agent as cash-application agent.
**Trigger**: `external.client_payment_received` (BACS/Faster Payments/CHAPS receipt, or bank-feed line from the bank).
**Inputs**: bank transaction (date, amount, payer name, reference), open receivables ledger, remittance advice if any, `invoice_id` or reference text.

### Steps

1. [agent] Parse the bank line and attempt a match by invoice reference, then by amount plus client, then by remittance advice.
2. [agent] Check amount: exact match is applied; partial payment applied to the oldest invoice, creating a short-pay item; over-payment held as unallocated credit.
3. [agent] Compute `days_to_pay` = payment date minus invoice date and update client payment-behaviour history (average days to pay, late count).
4. [agent] For late payments, compute statutory interest at 8% over Bank of England base rate (Late Payment Act) and record the claim; interest is claimed only on CFO instruction for strategic clients.
5. [human] Finance Manager approves any unallocated cash, write-offs of small differences (<= £25) and refunds of over-payments before they are made; over-payment refunds above £10,000 need the CFO.
6. [agent] Clear the invoice, stop its collections clock and post the receipt to the bank ledger.
7. [agent] Publish the receipt and refresh the 13-week cash forecast (SOP-FINANCE-11).

### Outputs and messages

- `finance.payment_received` to `sales`, `customer_success`, `data`: `invoice_id`, `client_id`, `amount_gbp`, `days_to_pay`, `matched` (bool), `short_pay_gbp`, `engagement_id`, `summary`.
- `finance.cash_forecast_updated` when a receipt exceeds £150,000 or is more than 7 days early or late versus forecast.

### SLA and controls

- SLA: matched and posted within 1 business day; unmatched cash resolved within 3 business days; match rate target 95% automatic.
- Control: daily bank reconciliation by the Finance Manager (statement to ledger); unallocated cash balance reported at each month-end.
- Control: remittance and bank-detail changes are verified by call-back; the agent cannot change a supplier or client bank record.

### Exceptions and escalation

- Payment from a payer name that does not match any client (possible third party or fraud): hold unallocated, Finance Manager calls the client, CFO informed after 3 business days.
- Duplicate payment: refund request raised, approved by CFO, paid by dual authorisation.
- Payment received for an invoice under dispute: apply, record, and tell legal and customer success; do not close the dispute record automatically.

---

## SOP-FINANCE-07: Collections ladder

**Owner**: CFO; the Finance agent runs the ageing daily as the collections agent.
**Trigger**: daily schedule: the receivables ageing run at 07:00 UK time on every business day.
**Inputs**: receivables ledger, due dates (invoice date + 30 days), dispute holds, customer success account notes, payment history, contact list for each client (billing contact, sponsor, CFO or finance director).

### Steps

1. [agent] Age every open invoice. Day 0 is the invoice date; the invoice is due on day 30; overdue begins on day 31 (COMPANY.md §7).
2. [agent] Day 31: send the reminder email to the billing contact with invoice copy and bank details; publish the overdue event.
3. [human] Day 38: Finance Manager telephones the billing contact and, if needed, the client sponsor; log the promised payment date.
4. [human] Day 45: CFO (Hannah Whitcombe) escalates in writing to the client sponsor and their finance director; the agent publishes the escalation.
5. [human] Day 60: CFO instructs a formal letter before action (legal letter) with late-payment interest and statutory compensation (£40 / £70 / £100 by debt size under the Late Payment Act); General Counsel (Callum Fraser) issues it.
6. [agent] Before every step, check for a dispute hold, a promise-to-pay still in time, or a payment in transit; skip the step and log why.
7. [agent] Track promises to pay; a broken promise moves the invoice to the next step immediately.
8. [human] Past day 90 or on insolvency signals (CCJ, winding-up petition, Gazette notice): treat as a bad-debt candidate (SOP-FINANCE-08) and consider a credit hold on new work.

### Outputs and messages

- `finance.invoice_overdue` to `customer_success`, `legal`, `sales`: `invoice_id`, `client_id`, `amount_gbp`, `days_overdue`, `stage` (`reminder` | `call`), `engagement_id`, `summary`.
- `finance.collections_escalated` to `legal`, `executive`: `invoice_id`, `client_id`, `amount_gbp`, `days_overdue`, `stage` (`cfo_escalation` | `legal_letter`), `severity` (`high` at day 45, `critical` at day 60 or above £100,000), `summary`.

### SLA and controls

- SLA: ladder executed on the exact day, with a tolerance of 1 business day; 100% of invoices past day 31 have a logged action; DSO <= 45 days and bad debt < 1% of revenue (COMPANY.md §7).
- Control: only the CFO can authorise the day-60 legal letter and any credit hold; agent actions are limited to reminders and scheduling.
- Control: weekly ageing review in the finance meeting; any invoice > £100,000 overdue is reviewed by the CEO's office via the escalation event.
- Control: client concentration alert if one client holds > 15% of total receivables.

### Exceptions and escalation

- Client in a genuine dispute: apply SOP-FINANCE-08; stop automatic reminders but keep the clock visible.
- Strategic client (top 5 by revenue): CFO and CRO (Rahul Mehta) agree a tailored approach before the day-38 call.
- Client says they have paid: Finance Manager checks the bank within 4 business hours and asks for remittance proof; no further chasing until confirmed.

---

## SOP-FINANCE-08: Disputes, credit notes and bad debt

**Owner**: CFO.
**Trigger**: `legal.client_dispute_raised` (a client contests an invoice, a deliverable or a contract term).
**Inputs**: `client_id`, `engagement_id`, disputed invoice IDs and amounts, the nature of the dispute, legal's initial assessment, delivery's evidence, customer success's view of the relationship.

### Steps

1. [agent] Place a dispute hold on the disputed invoices; stop reminders and the legal-letter step in SOP-FINANCE-07, while keeping the ageing visible.
2. [agent] Quantify exposure: disputed amount, undisputed amount still payable, accrued revenue at risk, bad-debt provision effect, effect on the 13-week cash forecast.
3. [human] Finance Manager asks the client to pay the undisputed portion on the original due date and records the answer.
4. [human] CFO, General Counsel, delivery head and Chief Customer Officer (Tobias Lindgren) agree the commercial position: hold, partial credit, full credit, or reject.
5. [human] If a credit note is agreed, CFO approves; credit notes above £25,000 also need CEO approval. The agent drafts the credit note, never issues it.
6. [agent] Issue the approved credit note referencing the original invoice, reverse revenue in the correct period, and recompute VAT; update the forecast and the provisions schedule.
7. [human] Bad debt: when an amount is more than 90 days overdue and not in dispute, or the client is insolvent, CFO approves a provision (50% at 90 days, 100% at 120 days) and write-off at 180 days with a VAT bad-debt relief claim after 6 months.

### Outputs and messages

- `finance.cash_forecast_updated` to `executive`, `data`: reflects disputed cash moved out of the 13-week window; keys `horizon_weeks`, `closing_cash_gbp`, `min_cash_gbp`, `at_risk_gbp`, `summary`.
- `finance.collections_escalated` to `legal`, `executive`: if the CFO moves a failed dispute to the final stage; keys `invoice_id`, `client_id`, `amount_gbp`, `stage`, `severity`.
- `finance.invoice_issued`: credit note posted as a negative invoice entry with `invoice_id` (credit note reference), `amount_gbp` (negative), `summary`.

### SLA and controls

- SLA: hold applied same business day; commercial position agreed within 5 business days; credit note issued within 2 business days of approval.
- Control: credit notes and write-offs are never posted by the person who raised them; provisions are reviewed at every month-end (SOP-FINANCE-10).
- Control: dispute log reviewed monthly by the CFO and General Counsel; total disputed value reported in the KPI pack.

### Exceptions and escalation

- Dispute amount > £150,000 or > 5% of monthly revenue: CEO informed within 24 hours; Board Audit and Risk Committee chair (Marcus Ellery) informed at next meeting.
- Evidence of delivery fault: hand to delivery quality process and customer success; finance keeps the hold until the position is agreed.

---

## SOP-FINANCE-09: Keep renewals, churn and revenue reversal

**Owner**: Finance Manager.
**Trigger**: `customer_success.renewal_due` (renewal window opens, typically 90 days before term end), `sales.renewal_proposal_sent` (proposal goes to the client), `customer_success.renewal_confirmed` (client renews), `customer_success.client_churned` (client leaves).
**Inputs**: `client_id`, `contract_id`, current Keep tier and monthly fee (Essential £8,000, Plus £18,000, Enterprise £40,000), anniversary date, CPI at the time of renewal, payment history, usage and support days from delivery.

### Steps

1. [agent] On `customer_success.renewal_due`, prepare the renewal pricing pack: current annual value, uplift of CPI + 2% capped at 7% (COMPANY.md §7), payment history (any late invoices), support-day usage, net revenue retention contribution.
2. [human] Finance Manager reviews; clients with more than two late payments in the last 12 months are flagged to sales to consider moving to quarterly in advance billing.
3. [agent] On `sales.renewal_proposal_sent`, check the proposed price and terms against the pack; a pricing check is issued if the fee, tier or terms differ from the uplift formula.
4. [agent] On `customer_success.renewal_confirmed`, create the new term billing schedule (12 months monthly in advance), apply the uplift from the anniversary, and update ARR and deferred income.
5. [agent] On `customer_success.client_churned`, stop future billing at the termination date, issue any final invoice, release accrual and deferred income, record the churn in the revenue bridge, and reassess any open receivables.
6. [human] Finance Manager reviews the churn entry and approves any pro-rata credits (Keep minimum term is 12 months, so early termination fees are billed per contract).
7. [agent] Update the ARR waterfall: opening ARR, new, expansion, contraction, churn, closing (target year-end ARR £1.5m FY2026, £6.5m FY2027, £17.0m FY2028, COMPANY.md §5.1).

### Outputs and messages

- `finance.pricing_check_completed` to `sales`: renewal check with `client_id`, `contract_id`, `amount_gbp` (annual), `uplift_pct`, `terms_ok`, `summary`.
- `finance.billing_schedule_created` to `delivery`, `customer_success`: renewal schedule with `contract_id`, `client_id`, `service_line` (`keep`), `tier`, `amount_gbp`, `schedule`.
- `finance.invoice_issued`: final invoice or early-termination invoice with the standard keys.
- `finance.cash_forecast_updated` to `executive`, `data` when churn removes more than £150,000 of forecast annual billing.

### SLA and controls

- SLA: renewal pricing pack within 2 business days of `customer_success.renewal_due`; billing stopped on the same day as `client_churned`; new term billed from the anniversary date without gap.
- Control: no Keep invoice is generated after a termination date without CFO sign-off; ARR is reconciled to the billing system every month-end.
- Control: uplift applied uniformly per the formula; discretionary waivers need CFO and CRO approval.

### Exceptions and escalation

- Churn of a client with outstanding invoices: collections continue (SOP-FINANCE-07); legal informed immediately.
- Churn of a client representing > 5% of ARR: CEO and CFO review the forecast the same day; budget variance flagged at the next close (SOP-FINANCE-10).

---

## SOP-FINANCE-10: Month-end close

**Owner**: CFO (Hannah Whitcombe), with the Finance Manager as close lead.
**Trigger**: schedule: first working day of each month (WD1) starts the close for the prior month; target completion is WD8 in FY2026, WD6 in FY2027 and WD5 in FY2028 (kpis.md `month_end_close_days`). Quarter-end and year-end add a VAT return and a statutory step.
**Inputs**: bank statements, receivables and payables ledgers, billing schedules, delivery's percentage-of-completion estimates and timesheets, payroll journals, expense claims, supplier accruals, fixed-asset list, prior-period budget, accruals list from operations and procurement.

### Steps

1. [agent] WD1: freeze the period (no back-dated invoices), pull bank feeds, run cut-off checks on deliveries and invoices raised in the last 5 days of the month.
2. [agent] WD1 to WD2: post recurring journals: depreciation, prepayment release, deferred income release, accrued income for percentage-of-completion, Keep straight-line revenue.
3. [human] WD2: Finance Manager and engagement Managers agree percentage-of-completion on each fixed-fee engagement; catch-up adjustments are posted with a note.
4. [agent] WD2: reconcile bank, receivables control, payables control, payroll, VAT control and intercompany (US entity from Q1 FY2027); list unreconciled items by age and size.
5. [agent] WD3: accrue unbilled supplier costs (from procurement orders and contractor engagements) and estimate bad-debt provision (50% over 90 days, 100% over 120 days).
6. [human] WD3 to WD4: Finance Manager reviews reconciliations, journals above £5,000, and accrual reasonableness; CFO reviews all manual journals above £25,000 and any prior-period adjustment.
7. [agent] WD4: produce the management accounts: P&L, balance sheet, cash flow, revenue by line (Compass, Forge, Keep), gross margin (cost of revenue = delivery + customer_success, COMPANY.md §5.1), department spend vs budget.
8. [agent] WD5: run budget-vs-actual by department; flag any variance above 10% and £25,000 on a monthly or year-to-date basis, or any overspend above 5% of annual budget.
9. [human] WD5: CFO and Finance Manager review commentary with department heads for flagged variances; update the forecast for the rest of the year.
10. [human] WD7 to WD8 (FY2026 target WD8): CFO signs off the close and publishes it; the agent distributes the pack to executive and data.
11. [agent] Archive the close file (reconciliations, journals, reviews) with a checklist for audit support.
12. [human] Payroll and tax: PAYE/NIC RTI submission and payment by the 22nd (19th if paying by post), VAT return quarterly via Making Tax Digital (1 month and 7 days after quarter end), Corporation Tax per statutory dates; the Finance Manager prepares, the CFO approves.

### Outputs and messages

- `finance.month_end_closed` to `executive`, `data`: `period` (`2026-01`, etc.), `revenue_gbp`, `gross_margin_pct`, `ebitda_gbp`, `cash_gbp`, `dso_days`, `bad_debt_pct`, `close_day` (working day), `open_items` (int), `summary`.
- `finance.budget_variance_flagged` to `executive`: `department`, `period`, `budget_gbp`, `actual_gbp`, `variance_gbp`, `variance_pct`, `severity` (`medium` > 10% and £25,000, `high` > 20% or > £100,000), `summary`.
- `finance.cash_forecast_updated` to `executive`, `data`: refreshed with actuals (SOP-FINANCE-11).

### SLA and controls

- SLA: close by WD8 in FY2026 (WD6 in FY2027, WD5 in FY2028 as automation improves; kpis.md `month_end_close_days`); 100% of balance sheet accounts reconciled; zero unreconciled bank items older than 30 days.
- Control: preparer and reviewer are different people for every reconciliation and journal; journals above £25,000 need CFO review; the agent can post only recurring and rule-based journals with a pre-approved template.
- Control: close checklist with sign-off per task; variance commentary mandatory for every flagged department.
- Control: access to the ledger is least privilege; period lock enforced after sign-off; reopening a period needs CFO written approval and is logged.

### Exceptions and escalation

- Close slips past WD8: CFO informs the CEO and Audit and Risk Committee chair (Marcus Ellery) with a recovery plan.
- Material error discovered after sign-off (> £50,000 or > 1% of monthly revenue): restate in the following period with disclosure, CFO informs the Audit and Risk Committee chair.
- Cut-off dispute with delivery: CFO decides on revenue timing in line with percentage-of-completion policy; delivery head (Oliver Thackeray) is informed.

---

## SOP-FINANCE-11: Cash forecast and treasury

**Owner**: CFO; the Finance agent acts as treasury analyst.
**Trigger**: weekly schedule on Monday morning; plus event triggers `data.forecast_updated` (new revenue and pipeline forecast from the data team), `delivery.capacity_forecast_updated` (staffing changes that move payroll and subcontractor spend), `data.kpi_report_published` (KPI refresh that moves collections assumptions), and ad hoc refreshes called by SOPs 02, 06, 08 and 09.
**Inputs**: bank balances, 13-week receivables schedule by `due_day` and client payment behaviour, billing schedules (signature, mid-point, acceptance dates), payroll run, supplier payment run, tax calendar (PAYE 22nd, VAT quarterly, Corporation Tax), pipeline-weighted new business, funding events (seed £3.5m, Series A £10m in Q2 FY2026, COMPANY.md §1), capex.

### Steps

1. [agent] Build the opening balance from reconciled bank balances (SOP-FINANCE-06).
2. [agent] Project receipts: each open or scheduled invoice by client's historic days-to-pay (not the contract due date), with a probability haircut for disputed and overdue items; add pipeline-weighted new-business billing from the data forecast.
3. [agent] Project payments: payroll (monthly, last working day), PAYE and NIC on the 22nd, pension, supplier runs (weekly on Thursday), subcontractors and associates, VAT quarterly, Corporation Tax, rent and insurance, capex, bonus accruals.
4. [agent] Compute weekly closing cash, minimum cash point, months of runway on trailing 3-month net burn, and a downside case (10% fewer receipts, 15 days slower collection).
5. [human] CFO reviews the forecast on Monday and records management actions: slow supplier run, bring forward invoices, draw on facilities, pause non-budgeted spend.
6. [human] Treasury policy checks: minimum liquidity of £3.0m (modelled policy, equal to roughly six months of FY2026 net burn plus buffer) and no more than 75% of cash with any one bank; surplus cash held in instant-access or short-term money-market deposits, no speculative instruments.
7. [agent] Publish the forecast and update the long-range FY cash view used by the Board.
8. [human] Foreign exchange from FY2027: US contracts quoted in USD at £1 = $1.27 planning rate; CFO sets hedging policy once USD receipts exceed £1m a year.

### Outputs and messages

- `finance.cash_forecast_updated` to `executive`, `data`: `horizon_weeks` (13), `opening_cash_gbp`, `closing_cash_gbp`, `min_cash_gbp`, `min_cash_week`, `runway_months`, `downside_closing_cash_gbp`, `at_risk_gbp`, `severity` (`low`, `medium` if forecast cash falls below £4.0m, `high` below £3.0m, `critical` below £2.0m), `summary`.

### SLA and controls

- SLA: Monday forecast by 12:00; event-driven refresh within 1 business day; forecast accuracy: 4-week-ahead closing cash within +/-10%.
- Control: forecast is reconciled each week to actual cash and the variance explained; model changes are version-controlled; the agent may not move cash or change payment runs.
- Control: bank mandates require two authorisers (CFO plus Finance Manager) for any payment above £10,000; any payment above £50,000 needs the CFO and a second named signatory (CEO above £250,000, COMPANY.md §9.3).
- Control: no payment instructions accepted by email without call-back.

### Exceptions and escalation

- `min_cash_gbp` below £3.0m in any forecast week: CFO informs the CEO the same day and presents a plan to the Board within 5 business days.
- Weekly slippage of receipts above £250,000: CFO reviews the top 5 debtors with customer success and sales.
- Series A funding delay: treasury plan reforecast; discretionary spend freeze (marketing programme, T&E) proposed to the CEO.

---

## SOP-FINANCE-12: Annual budget cycle

**Owner**: CFO.
**Trigger**: schedule: 1 October opens the cycle for the next fiscal year (calendar year), publishing `finance.budget_cycle_opened`. Every department's `<dept>.budget_submitted` (customer_success, data, delivery, executive, it_security, legal, marketing, operations, people, product, sales) triggers intake; `executive.budget_approved` closes the cycle.
**Inputs**: COMPANY.md revenue and cost targets (§5.1 to §5.4), prior-year actuals, headcount plan (§6.1), salary bands (§6.2), department submissions (people cost from headcount x loaded cost = base x 1.28, non-people spend by line), strategy and OKRs.

### Steps

1. [human] CFO sets the planning guidance: revenue and margin targets, headcount ceilings by department, loaded cost factor 1.28, AI cost deflator (unit costs fall about 15% a year, COMPANY.md §8), inflation, FX rate.
2. [agent] Open the cycle: create `BUD-<next FY>`, issue the template and timeline: submissions due day 21 (late October), challenge sessions in week 4, consolidation by 15 November, executive review in November, Board approval at the December meeting.
3. [agent] Intake: on each `<dept>.budget_submitted`, validate the submission: people cost equals average headcount x average loaded cost, non-people lines have owners, no hidden headcount beyond the plan, and totals within the guidance (flag > 5% above envelope).
4. [human] Finance Manager runs a 45-minute challenge session with each department head; the CFO decides the envelope for the department.
5. [agent] Consolidate: P&L by department, cost of revenue (delivery + customer success) and operating expenses, EBITDA, cash flow, headcount, capex. Check that department totals reconcile to the company total and that EBITDA ties to the targets (for example -£1.5m FY2026, £1.7m FY2027, £7.2m FY2028, COMPANY.md §5.1).
6. [human] CFO reviews the consolidation with the CEO; open issues are resolved by trade-off (headcount timing, programme spend).
7. [agent] Publish the consolidated budget to executive for approval; record the decision.
8. [agent] On `executive.budget_approved`, load the approved budget as the baseline for variance reporting (SOP-FINANCE-10), create department cost centres and spending limits (non-budgeted spend > £50,000 needs the CFO, > £250,000 the CEO, COMPANY.md §9.3).
9. [human] Quarterly reforecast: mid-year and Q3 reforecast with department heads; changes outside approved envelope need CEO approval.

### Outputs and messages

- `finance.budget_cycle_opened` to all departments: `budget_cycle_id` (`BUD-2027`), `fiscal_year`, `due_day`, `guidance` (loaded cost factor, headcount ceilings by `department`), `summary`.
- `finance.budget_consolidated` to `executive`: `budget_cycle_id`, `total_gbp`, `people_gbp`, `non_people_gbp`, `revenue_gbp`, `ebitda_gbp`, `departments_received` (list), `departments_over_envelope` (list), `summary`.
- `finance.budget_variance_flagged` to `executive` when a department submission exceeds its envelope by more than 5% or £25,000: `department`, `budget_gbp`, `submitted_gbp`, `variance_gbp`, `variance_pct`, `severity`.
- `finance.budget_submitted` to `executive`: finance's own department submission into the cycle (`department`=`finance`, `budget_cycle_id`, `amount_gbp`, `people_gbp`, `non_people_gbp`), prepared by the Finance Manager (CFO until Q4 FY2026) and tied to the COMPANY.md §5.4 envelope of £310k / £730k / £1,500k.
- `finance.hire_requested` is not used here; finance's own requests are in SOP-FINANCE-16.

### SLA and controls

- SLA: cycle opens 1 October; all 11 non-finance departments submit by day 21; consolidation within 3 business days of the last submission; Board-ready budget by the first week of December.
- Control: a department that has not submitted by the due date is chased on day 22 by the agent and escalated to the CEO on day 25; the CFO may set its budget at prior-year run rate plus agreed growth.
- Control: consolidated totals must equal the sum of department submissions; the agent runs a tie-out check against COMPANY.md §5.4 and flags a mismatch greater than £5,000 per department.
- Control: version history of every budget model; approval recorded in the board minutes.

### Exceptions and escalation

- Aggregate submissions exceed the target cost envelope by more than 3%: CFO and CEO set a reduction plan in the challenge round.
- Late funding or revenue shock (see SOP-FINANCE-15): reopen the cycle; CFO brings a revised baseline to the Board.

---

## SOP-FINANCE-13: Headcount cost control and payroll

**Owner**: Finance Manager; CFO approves anything outside approved budget.
**Trigger**: `people.requisition_opened` (a requisition is raised and needs a finance check), `executive.headcount_approved` (the CEO has approved headcount outside the approved budget or confirmed an in-budget requisition), `people.offer_accepted` (a candidate has accepted at a salary), `people.new_hire_started` (starter joins payroll), `people.employee_left` (leaver, final pay and cost release), `people.contractor_engaged` (contractor or associate engaged).
**Inputs**: `requisition_id`, `department`, role, level key, salary band (COMPANY.md §6.2), approved headcount plan (COMPANY.md §6.1), offer details (base salary, start date), leaver details (last working day, notice, holiday owed), contractor rate and term, IR35 status.

### Steps

1. [agent] On `people.requisition_opened`, check the role against the approved plan: department, level, band, quarter, and remaining headcount budget; compute loaded cost = base x 1.28 (employer NI, pension, benefits and bonus accrual) and the in-year cost based on start date.
2. [human] Finance Manager confirms the requisition is within budget or marks it as non-budgeted; non-budgeted requisitions wait for `executive.headcount_approved` (COMPANY.md §9.3).
3. [agent] On `executive.headcount_approved`, add the approved role to the establishment, update the department forecast and cost centre, and tell the cash forecast (SOP-FINANCE-11).
4. [agent] On `people.offer_accepted`, validate the salary against band and budget (flag any offer above the band maximum or more than 5% above the approved cost); create the payroll draft with the start date. US hires carry a +15% salary uplift (COMPANY.md §6.2).
5. [human] Finance Manager approves; CFO approves any exception above band or any one-off sign-on payment above £10,000.
6. [agent] On `people.new_hire_started`, set up the employee in payroll (RTI Full Payment Submission on or before the first pay date, auto-enrolment pension assessment, tax code from HMRC or emergency code), and allocate the cost to the department.
7. [agent] On `people.employee_left`, calculate final pay, accrued holiday, notice, any bonus accrual release, and remove the cost from the forecast from the last working day; raise a P45 and update the headcount.
8. [agent] On `people.contractor_engaged`, set up the contractor as a supplier (SOP-FINANCE-14), check the engagement against subcontractor budget and IR35 determination from legal; accrue monthly cost.
9. [human] Payroll run: Finance Manager prepares payroll by WD-5 of the month, CFO approves the BACS file the day before pay day (last working day of the month); payments are released under dual authorisation.
10. [agent] Reconcile payroll to the ledger and headcount register every month at close (SOP-FINANCE-10).

### Outputs and messages

- `finance.cash_forecast_updated` to `executive`, `data`: refreshed payroll and subcontractor lines after an approved hire, leaver or contractor, with `horizon_weeks`, `closing_cash_gbp`, `min_cash_gbp`, `summary`; emitted if the change exceeds £10,000 a month.
- `finance.hire_requested` to `people`: finance's budget-check response to `people.requisition_opened` with `requisition_id`, `department`, `role`, `salary_gbp`, `annual_loaded_cost_gbp`, `within_budget` (bool), `year_end_headcount_plan`, `requested_by`.
- `finance.budget_variance_flagged` to `executive`: when a requisition or offer breaches the approved people budget; `department`, `period`, `variance_gbp`, `variance_pct`, `severity`, `summary`.

### SLA and controls

- SLA: headcount cost check within 2 business days of `people.requisition_opened`; offer validation within 1 business day of `people.offer_accepted`; leaver final pay on the next pay run or within 10 business days if earlier by contract.
- Control: no payroll change without a signed HR change form (new hire, leaver, pay change); payroll changes reconciled to HR system monthly; payroll output reviewed by two humans.
- Control: salary above the level band maximum is not accepted without CFO and CPO (Grace Adeyemi) approval; the agent cannot change a salary.
- Control: bank-details changes by employees verified by call-back.

### Exceptions and escalation

- Offer above band or budget: CFO and Chief People Officer decide; CEO if the annual cost exceeds £150,000.
- Leaver with a clawback (sign-on, relocation, training) owed: payroll deducts only with written employee consent; otherwise legal advises.
- Contractor whose engagement could be treated as employment (IR35 risk): legal and CFO decide on status before the first payment.

---

## SOP-FINANCE-14: Vendor onboarding, procurement and supplier payments

**Owner**: Finance Manager.
**Trigger**: `operations.vendor_review_requested` (a new supplier is being reviewed), `it_security.vendor_risk_assessed` (security's assessment completed), `operations.vendor_approved` (vendor approved for use), `operations.procurement_order_placed` (a purchase order exists), `marketing.campaign_launched` (a campaign commits programme spend).
**Inputs**: `vendor_id` (`VN-0001`), vendor details, quote, contract term, risk rating, PO value, budget line, supplier invoice, delivery or services-received confirmation, bank details form.

### Steps

1. [agent] On `operations.vendor_review_requested`, open a vendor record in draft, check the quote against budget, and compute annual cost and commitment; flag any commitment above £50,000 (CFO) or £250,000 (CEO).
2. [agent] On `it_security.vendor_risk_assessed`, record the rating; high-risk vendors are blocked from set-up until the CFO and CISO (Wei Zhang) agree conditions.
3. [human] Finance Manager performs due diligence: Companies House status, VAT number validation, sanctions screening, and a bank-details call-back to a known number before any payment.
4. [agent] On `operations.vendor_approved`, activate the vendor in the payables ledger with payment terms (default 30 days, never shorter than the contract) and the approver record.
5. [agent] On `operations.procurement_order_placed`, create the commitment against the budget line and accrue expected cost in the period it will be received; warn the department head at 80% of the budget line used.
6. [agent] On `marketing.campaign_launched`, check campaign spend against the marketing programme budget, set a monthly phasing and a trigger for the variance report; alert if committed spend is > 10% over plan.
7. [agent] On supplier invoice receipt, do a three-way match (PO, services received, invoice) and code to the correct cost centre; the agent proposes payments but does not release them.
8. [human] Weekly supplier run on Thursday: Finance Manager prepares, CFO approves; payments over £10,000 need two approvers, over £50,000 the CFO plus a named second signatory, over £250,000 the CEO (COMPANY.md §9.3).
9. [agent] Reconcile supplier statements monthly; chase duplicate or unmatched invoices; the agent never changes bank details.

### Outputs and messages

- `finance.budget_variance_flagged` to `executive`: for over-commitment, with `department`, `period`, `budget_gbp`, `committed_gbp`, `variance_gbp`, `variance_pct`, `severity`, `summary`.
- `finance.cash_forecast_updated` to `executive`, `data`: when a commitment adds more than £25,000 to the 13-week outflow, with `horizon_weeks`, `closing_cash_gbp`, `min_cash_gbp`, `summary`.

### SLA and controls

- SLA: vendor active within 2 business days of `operations.vendor_approved`; supplier invoices coded within 3 business days; paid on terms (default 30 days); early-payment discounts taken only when annualised value exceeds 15%.
- Control: three-way match; no PO, no pay (except utilities, rent, tax, payroll); changes to supplier bank details need a call-back and a second human approver.
- Control: split purchasing is prohibited (multiple orders to avoid approval limits are aggregated); the agent flags patterns.
- Control: segregation: the person who raises a PO cannot approve its payment; the agent proposes only.

### Exceptions and escalation

- Vendor requested urgently without review: CFO may approve a one-off order up to £10,000 with a retrospective review within 10 business days.
- Invoice arrives for goods not ordered: hold, notify operations; if repeated, flag to CFO as possible fraud.
- Vendor risk high or critical and still required: CFO, CISO and COO (Beatrice Moreau) decide, written conditions to the vendor file.

---

## SOP-FINANCE-15: Board reporting, strategy, OKRs and crisis response

**Owner**: CFO.
**Trigger**: `executive.board_meeting_held` (post-meeting actions and next-meeting preparation), `executive.okrs_set` (new OKRs affecting finance KPIs and targets), `executive.strategy_updated` (change to the strategy in COMPANY.md; needs financial model update), `executive.crisis_declared` (a company-wide crisis).
**Inputs**: the latest close pack, cash forecast, budget, KPI pack, board minutes and actions, the strategy change, OKR targets, crisis description and severity.

### Steps

1. [agent] On `executive.board_meeting_held`, extract the finance actions and decisions from the minutes; create tasks with owners and dates; update the finance calendar for the next meeting (quarterly plus ad hoc, COMPANY.md §9.1).
2. [agent] Five business days before each board meeting, assemble the board pack draft: management accounts, cash and runway, revenue by line, KPI scorecard, forecast versus budget, key risks, deal approvals above £1.5m.
3. [human] CFO finalises the pack with the CEO and, ahead of Audit and Risk Committee meetings, with the committee chair (Marcus Ellery).
4. [agent] On `executive.okrs_set`, map company OKRs to finance KPIs (DSO, bad debt, close days, forecast accuracy, margin) and update the KPI definitions with the new targets.
5. [agent] On `executive.strategy_updated`, re-run the financial model for the changed assumptions (revenue mix, pricing, expansion timing, hiring pace), producing before/after revenue, EBITDA and cash.
6. [human] CFO reviews the impact and tells the CEO; if EBITDA or minimum cash moves materially (> £250,000 or below policy), a reforecast is presented at the next board meeting.
7. [agent] On `executive.crisis_declared`, produce a 24-hour liquidity view: cash on hand, 13-week outflows that cannot be deferred, receipts at risk, available levers.
8. [human] CFO and CEO decide immediate controls: freeze on non-essential spend, payment-run timing, hiring pause, banking facility contact; every action is recorded and reviewed at the next board.
9. [agent] Run daily cash and collections updates until the CEO closes the crisis.

### Outputs and messages

- `finance.cash_forecast_updated` to `executive`, `data`: crisis or strategy-change forecast with `horizon_weeks`, `closing_cash_gbp`, `min_cash_gbp`, `runway_months`, `downside_closing_cash_gbp`, `severity`, `summary`.
- `finance.budget_variance_flagged` to `executive`: when a strategy change or crisis moves department spend beyond approved limits: `department`, `period`, `variance_gbp`, `variance_pct`, `severity`, `summary`.

### SLA and controls

- SLA: board pack draft 5 business days before the meeting, final 2 business days before; crisis liquidity view within 24 hours; strategy-change model within 5 business days.
- Control: board numbers come only from the closed period and the latest signed-off forecast; any pro-forma figure is labelled.
- Control: agents prepare packs; the CFO signs; the agent does not publish to external parties or investors.
- Control: investor reporting to Ashgrove Ventures (Tomas Beckett) and Tern Capital (Adaeze Okafor) is sent by the CFO only, on the monthly or quarterly cycle agreed in the investment agreements.

### Exceptions and escalation

- Liquidity forecast below £2.0m in any week: CFO to the CEO and Board chair (Priya Raman) within 24 hours with a funding plan.
- Covenant, facility or investor-reporting breach: General Counsel and CFO notify the board committee chair immediately.
- Crisis involving a data breach: security and legal lead; finance supports with cost tracking, insurance notification and cash forecasting.

---

## SOP-FINANCE-16: Finance capacity and hiring

**Owner**: CFO.
**Trigger**: quarterly schedule (first Monday of each quarter) and capacity-trigger breaches monitored by the agent.
**Inputs**: invoice volume, supplier invoice volume, journals per month, close days, headcount plan for finance (2 humans and 2 agents in FY2026; 5 and 5 in FY2027; 10 and 9 in FY2028, COMPANY.md §6.1), error rates, audit and tax calendar, planned US entity launch (Q1 FY2027).

### Steps

1. [agent] Compute capacity metrics each quarter: invoices issued per FTE, bank lines reconciled per FTE, close days vs target, journals above manual threshold, rework rate, overtime proxy.
2. [agent] Compare with the triggers: more than 120 customer invoices a month per human, close slipping beyond the target close day (WD8 in FY2026) for two consecutive months, more than 3% invoice errors, VAT or statutory deadline at risk, or US entity formation approaching.
3. [human] CFO reviews against the approved plan (COMPANY.md §6.1) and decides between automation (agent configuration), additional agent capacity, and a human hire; levels follow COMPANY.md §6.2 (for example Finance Analyst at consultant level, £55,000 to £70,000).
4. [human] CFO prepares the justification: workload data, cost = base x 1.28, alternatives, and the risk of not hiring.
5. [agent] Raise the hire request to the people team with the role, level, start quarter and justification; track the requisition through SOP-FINANCE-13.
6. [human] If the role is outside the approved plan, CEO approval is needed (`executive.headcount_approved`).
7. [human] Training and cover: the Finance Manager keeps procedures current, a named deputy for each critical process (payroll, bank release, VAT) and a quarterly access review.

### Outputs and messages

- `finance.hire_requested` to `people`: `department` (`finance`), `role`, `level` (level key), `salary_band_gbp`, `reason`, `start_quarter`, `justification`, `severity`, `summary`.

### SLA and controls

- SLA: capacity review completed in the first 10 business days of each quarter; hire request raised within 5 business days of a trigger breach.
- Control: no hire request without a CFO-signed justification; the plan never exceeds the finance headcount in COMPANY.md §6.1 without approval.
- Control: key-person risk register: payroll, bank release and VAT submission each have a trained deputy; the quarterly access review confirms least privilege.

### Exceptions and escalation

- Close slips or payroll error during the period before a hire arrives: the CFO engages an interim or contract accountant (within the subcontractor budget) and informs the CEO.
- Audit or statutory deadline at risk: escalate to the Audit and Risk Committee chair.

---

## Appendix A: Control summary

| Control | Applies to | Preparer | Reviewer / approver | Evidence |
|---|---|---|---|---|
| Invoice approval before issue | SOP-04, 05 | Finance agent | Finance Manager; CFO over £100,000 | Invoice workflow log |
| Payment release (dual authorisation) | SOP-11, 13, 14 | Finance agent proposes | Finance Manager plus CFO; > £50,000 CFO plus named signatory; > £250,000 CEO | Bank mandate log |
| Agent payment limit | All | Finance agent | May not approve or release above £10,000 (COMPANY.md §9.4) | Agent register entry |
| Credit notes and write-offs | SOP-08 | Finance agent drafts | CFO; CEO above £25,000 | Approval record |
| Journals | SOP-10 | Agent (rule-based) or Finance Manager | Different person; CFO above £25,000 | Journal log |
| Bank reconciliation | SOP-06, 10 | Finance agent | Finance Manager, daily | Reconciliation file |
| Supplier bank details | SOP-14 | Finance Manager | Call-back plus second human | Call-back log |
| Pricing and discount authority | SOP-01, 02 | Finance agent | Finance Manager; CFO and CEO above 10% discount | Pricing check record |
| Treasury policy | SOP-11 | Finance agent | CFO | Weekly forecast and policy test |
| Budget baseline | SOP-12 | Finance agent | CFO; CEO and Board | Board minutes |

## Appendix B: Topic coverage matrix

Triggers (every subscribed topic mapped to an SOP):

| Subscribed topic | SOP |
|---|---|
| `customer_success.client_churned`, `customer_success.renewal_confirmed`, `customer_success.renewal_due`, `sales.renewal_proposal_sent` | SOP-FINANCE-09 |
| `data.forecast_updated`, `data.kpi_report_published`, `delivery.capacity_forecast_updated` | SOP-FINANCE-11 |
| `delivery.engagement_completed`, `delivery.scope_change_requested` | SOP-FINANCE-05 |
| `delivery.engagement_kickoff`, `legal.contract_signed`, `sales.deal_won` | SOP-FINANCE-03 |
| `delivery.milestone_reached` | SOP-FINANCE-04 |
| `delivery.scoping_completed`, `sales.proposal_requested` | SOP-FINANCE-01 |
| `executive.board_meeting_held`, `executive.crisis_declared`, `executive.okrs_set`, `executive.strategy_updated` | SOP-FINANCE-15 |
| `executive.budget_approved` and every `<dept>.budget_submitted` | SOP-FINANCE-12 |
| `executive.deal_decision_made`, `executive.pricing_change_approved`, `product.pricing_change_proposed`, `sales.deal_approval_requested` | SOP-FINANCE-02 |
| `executive.headcount_approved`, `people.contractor_engaged`, `people.employee_left`, `people.new_hire_started`, `people.offer_accepted`, `people.requisition_opened` | SOP-FINANCE-13 |
| `external.client_payment_received` | SOP-FINANCE-06 |
| `it_security.vendor_risk_assessed`, `operations.procurement_order_placed`, `operations.vendor_approved`, `operations.vendor_review_requested`, `marketing.campaign_launched` | SOP-FINANCE-14 |
| `legal.client_dispute_raised` | SOP-FINANCE-08 |

Published topics (every published topic appears in the outputs of at least one SOP):

| Published topic | SOPs |
|---|---|
| `finance.pricing_check_completed` | 01, 02, 05, 09 |
| `finance.billing_schedule_created` | 03, 05, 09 |
| `finance.invoice_issued` | 03, 04, 05, 08, 09 |
| `finance.payment_received` | 06 |
| `finance.invoice_overdue` | 07 |
| `finance.collections_escalated` | 07, 08 |
| `finance.budget_cycle_opened` | 12 |
| `finance.budget_consolidated` | 12 |
| `finance.budget_variance_flagged` | 10, 12, 13, 14, 15 |
| `finance.cash_forecast_updated` | 02, 06, 08, 09, 10, 11, 13, 14, 15 |
| `finance.month_end_closed` | 10 |
| `finance.budget_submitted` | 12 |
| `finance.hire_requested` | 13, 16 |
