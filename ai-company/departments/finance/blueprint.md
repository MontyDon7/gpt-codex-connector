# Finance Department Blueprint

## 1. Mission and scope

The Finance department keeps Lumenhall Partners Ltd (and, from Q1 FY2027, Lumenhall Partners Inc.) solvent, correctly priced, accurately invoiced, promptly paid and fully accountable to its Board and investors. It is led by the Chief Financial Officer, Hannah Whitcombe, who reports to the CEO, Imogen Hartley (COMPANY.md §9.2).

Scope, in the order the money moves:

| Area | What Finance owns | Standing targets (COMPANY.md §7) |
|---|---|---|
| Pricing checks | Check every proposal against the price list (§3), discount authority (§9.3) and payment terms before `sales.proposal_sent`; publish `finance.pricing_check_completed` | Discount above 10% or non-standard payment terms needs Finance head and CEO approval |
| Billing | Build milestone schedules (30% / 40% / 30%) and Keep monthly-in-advance schedules from `legal.contract_signed`; issue invoices | Invoices issued within 2 business days of milestone acceptance |
| Collections | Net-30 terms; reminder day 31, call day 38, CFO escalation day 45, legal letter day 60; late-payment interest at 8% over base rate | DSO <= 45 days; bad debt < 1% of revenue |
| Revenue recognition | Percentage-of-completion for Compass and Forge; straight-line monthly for Keep | Month-end close accurate and on time |
| Accounting and close | Ledger, reconciliations, month-end close, statutory accounts, audit support, UK VAT (20%), US sales tax by state from FY2027 | `finance.month_end_closed` each month |
| FP&A and budgeting | Annual budget cycle (opens Q4), in-year variance monitoring, rolling cash forecast, board and investor reporting | Department budget envelopes per COMPANY.md §5.4 |
| Treasury | Cash, banking, GBP/USD exposure at the fixed planning rate of £1 = $1.27, payment approvals | Agents never approve payments above £10,000 (§9.4) |
| Spend control | Non-budgeted spend approvals (CFO above £50k, CEO above £250k, §9.3), vendor and contractor cost set-up | Policy: no client above 15% of revenue (§8) |

Out of scope: contract drafting (Legal), payroll policy and hiring decisions (People; Finance funds and reconciles), procurement execution (Operations), client relationship ownership (Customer Success, Sales).

Finance is an operating-expense department. Its cost is not part of cost of revenue (COMPANY.md §5.1). Its budget envelope is £310k / £730k / £1,500k (people £210k / £480k / £800k; non-people £100k / £250k / £700k) per COMPANY.md §5.4.

## 2. Org chart

```
Chief Financial Officer (head)                      Hannah Whitcombe, reports to CEO
|
+-- Finance Manager (FP&A and Commercial Finance)   manager; joins Q4 FY2026
|     +-- Finance Analyst x1 (FY2027), x2 (FY2028)  analyst
|     +-- [FY2027 only, until the Controller joins]
|           Senior Accountant x1                    senior_consultant
|           Billing and Collections Specialist x1   consultant
|
+-- Financial Controller                            principal; joins Q2 FY2028
|     +-- Senior Accountant x2 (from Q2 FY2028, existing hire re-lines)
|     +-- Billing and Collections Specialist x2 (from Q2 FY2028, existing hire re-lines)
|     +-- Treasury and Tax Specialist x1            senior_consultant; joins Q4 FY2028
|
+-- AI agents (see section 4), each with a named human owner
```

Reporting-line notes: in FY2026 the CFO runs everything personally with the Finance Manager joining in Q4. In FY2027 there is no Controller, so the Senior Accountant and the Billing and Collections Specialist report to the Finance Manager. From Q2 FY2028 they re-line to the Financial Controller, who owns the ledger, close, billing, collections and tax. Finance Analysts always report to the Finance Manager.

## 3. Roles

Headcount is year-end humans and sums to COMPANY.md §6.1: finance = 2 / 5 / 10. Level keys and bands are from COMPANY.md §6.2.

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Financial Officer | head | Chief Executive Officer | 1 | 1 | 1 | 140,000 to 200,000 (cash; plus equity) | Owns finance strategy, Board and Audit and Risk Committee reporting, investor reporting to Ashgrove Ventures and Tern Capital, funding and banking, pricing and discount approvals with the CEO, non-budgeted spend approvals above £50k, collections escalation at day 45, US entity set-up |
| Financial Controller | principal | Chief Financial Officer | 0 | 0 | 1 | 120,000 to 155,000 | Owns ledger integrity, month-end close, statutory accounts and audit, VAT and corporation tax compliance, internal controls (segregation of duties, journal approval), owner of Close and AP agents, SOC 2 financial-control evidence |
| Finance Manager | manager | Chief Financial Officer | 1 | 1 | 1 | 92,000 to 115,000 | FP&A and commercial finance: annual budget cycle, variance analysis, cash forecast, pricing-check sign-off, deal-desk modelling, board pack; owner of FP&A and Pricing agents; interim owner of billing and collections until the specialist is hired |
| Senior Accountant | senior_consultant | Finance Manager (FY2027); Financial Controller from Q2 FY2028 | 0 | 1 | 2 | 72,000 to 90,000 | Journals, bank and intercompany reconciliations, accruals, percentage-of-completion revenue schedules, deferred income, prepayments, payroll and expense posting, month-end close checklist; owner of Revenue Recognition and Close agents |
| Billing and Collections Specialist | consultant | Finance Manager (FY2027); Financial Controller from Q2 FY2028 | 0 | 1 | 2 | 55,000 to 70,000 | Issues and corrects invoices, cash application, runs the collections ladder (day 31 / 38 / 45 / 60), credit notes, client statements, disputes liaison with Legal and Customer Success; owner of Billing and Collections agent |
| Finance Analyst | analyst | Finance Manager | 0 | 1 | 2 | 38,000 to 48,000 | Budget data collection, utilisation-to-margin analysis with Delivery, KPI reporting, cash-forecast inputs, ad hoc analysis for Data and Executive, supplier invoice coding and review |
| Treasury and Tax Specialist | senior_consultant | Financial Controller | 0 | 0 | 1 | 72,000 to 90,000 | US sales tax and Delaware entity compliance, transfer pricing between Ltd and Inc., GBP/USD exposure and bank accounts, VAT returns, R&D tax credit claims, payment-run control |
| **Total humans** | | | **2** | **5** | **10** | | Equals COMPANY.md §6.1 row for finance |

### Planning salary points and cost check

Loaded cost = base x 1.28 (COMPANY.md §5.2). Planning base salaries sit inside the §6.2 bands. Average FTE reflects start quarter (Q1 start = 1.00, Q2 = 0.75, Q3 = 0.50, Q4 = 0.25 of a year).

| Role | Planning base £ | Loaded £ | FY2026 avg FTE | FY2027 avg FTE | FY2028 avg FTE | FY2026 £k | FY2027 £k | FY2028 £k |
|---|---|---|---|---|---|---|---|---|
| Chief Financial Officer | 140,000 | 179,200 | 1.00 | 1.00 | 1.00 | 179.2 | 179.2 | 179.2 |
| Financial Controller | 125,000 | 160,000 | 0 | 0 | 0.75 | 0 | 0 | 120.0 |
| Finance Manager | 92,000 | 117,760 | 0.25 | 1.00 | 1.00 | 29.4 | 117.8 | 117.8 |
| Senior Accountant (1st) | 78,000 | 99,840 | 0 | 1.00 | 1.00 | 0 | 99.8 | 99.8 |
| Senior Accountant (2nd) | 78,000 | 99,840 | 0 | 0 | 0.50 | 0 | 0 | 49.9 |
| Billing and Collections Specialist (1st) | 58,000 | 74,240 | 0 | 0.75 | 1.00 | 0 | 55.7 | 74.2 |
| Billing and Collections Specialist (2nd) | 58,000 | 74,240 | 0 | 0 | 0.75 | 0 | 0 | 55.7 |
| Finance Analyst (1st) | 40,000 | 51,200 | 0 | 0.50 | 1.00 | 0 | 25.6 | 51.2 |
| Finance Analyst (2nd) | 40,000 | 51,200 | 0 | 0 | 0.50 | 0 | 0 | 25.6 |
| Treasury and Tax Specialist | 78,000 | 99,840 | 0 | 0 | 0.25 | 0 | 0 | 25.0 |
| **Total people cost** | | | **1.25** | **4.25** | **7.75** | **208.6** | **478.1** | **798.4** |
| COMPANY.md §5.4 people envelope | | | | | | 210 | 480 | 800 |
| Delta | | | | | | -1.4 | -1.9 | -1.6 |

All three years are within the £5k tolerance. The full build-up lives in `economics.md`.

## 4. AI agents

Agent counts sum to COMPANY.md §6.1: finance = 2 / 5 / 9. Every agent is registered in the agent register and has a named accountable human (COMPANY.md §9.4). All agents share these hard limits: they may draft, analyse, monitor and propose; they may not approve payments above £10,000, sign contracts, approve discounts, post manual journals above £25,000 without human approval, or notify regulators or HMRC.

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Pricing and Deal Desk Agent | Finance Manager (CFO until Q4 FY2026) | On `sales.proposal_requested` and `delivery.scoping_completed`, check tier and price against COMPANY.md §3, discount against §9.3, payment terms against §7, margin against scoped team cost; emit `finance.pricing_check_completed` with `pricing_ok`, `discount_pct`, `approval_required` | May pass a proposal at list price and discount <= 10% with standard net-30 terms. Must route discount > 10% or non-standard terms to CFO and CEO, and any deal >= £500k to the deal-approval path. Cannot change a price | 1 | 1 | 1 |
| Billing and Collections Agent | Billing and Collections Specialist (Finance Manager until FY2027 hire) | Builds billing schedules from `legal.contract_signed`; drafts invoices on `delivery.milestone_reached`; applies cash on `external.client_payment_received`; runs the collections ladder; drafts reminder and call scripts | Drafts and issues standard invoices within 2 business days; sends day-31 reminder automatically; day-38 call and day-45 escalation need human action; cannot waive interest, issue credit notes, or write off any amount. Year 3 count is two (UK and US ledgers) | 1 | 1 | 2 |
| Close and Reconciliation Agent | Senior Accountant (Financial Controller from Q2 FY2028) | Runs the month-end close checklist, bank and intercompany reconciliations, accrual proposals, and flags unreconciled items older than 30 days; prepares the close pack for `finance.month_end_closed` | Proposes journals only; any journal above £25,000 or touching equity, tax or intercompany needs human posting. Cannot lock a period. Year 3 count is two (Ltd and Inc.) | 0 | 1 | 2 |
| FP&A and Cash Forecast Agent | Finance Manager | Consolidates `<d>.budget_submitted` into `finance.budget_consolidated`, monitors spend against COMPANY.md §5.4 envelopes, drafts variance commentary, produces 13-week rolling cash forecast | Flags variance > 10% of monthly envelope or any non-budgeted spend > £50k; cannot reallocate budget or approve spend | 0 | 1 | 1 |
| Revenue Recognition Agent | Senior Accountant | Calculates percentage-of-completion for Compass and Forge from `delivery.milestone_reached` and engagement progress; straight-line Keep schedules; reconciles deferred and accrued income | Proposes recognition entries; cannot change the method or recognise revenue ahead of evidence of progress; every release goes through human review before close | 0 | 1 | 1 |
| AP and Spend Control Agent | Financial Controller | Matches supplier invoices to approved vendors (`operations.vendor_approved`), contractors (`people.contractor_engaged`) and purchase orders (`operations.procurement_order_placed`); proposes payment runs; detects duplicate bills | Prepares the payment run; cannot release any payment above £10,000 and cannot add or change supplier bank details (human call-back verification required) | 0 | 0 | 1 |
| Audit and Compliance Evidence Agent | Financial Controller | Assembles audit packs, SOC 2 financial-control evidence and VAT and sales-tax working papers; tracks open audit requests | Read-only on the ledger; cannot respond to auditors or HMRC directly; every pack is reviewed by a human before release | 0 | 0 | 1 |
| **Total agents** | | | | **2** | **5** | **9** |

Agent cost is carried in non-people spend (AI compute and tooling), within the £100k / £250k / £700k non-people envelope, at the £20k to £35k per agent-year range of COMPANY.md §5.2.

## 5. Hiring plan

Time-to-hire is 45 days for humans and 5 days for agent provisioning (COMPANY.md §8). Every human hire goes through `finance.hire_requested` then `people.requisition_opened`, then `executive.headcount_approved`, because these hires are inside the approved §5.4 budget but still require the CEO's headcount approval record. Planned start quarters assume offer acceptance 45 days earlier.

### FY2026 (quarterly)

| Quarter | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| Q1 FY2026 | Chief Financial Officer (Hannah Whitcombe) | 1 | Q1 FY2026 (in post from Day 0, 2026-01-05) | Founding executive team (COMPANY.md §9.2) |
| Q1 FY2026 | Pricing and Deal Desk Agent; Billing and Collections Agent | 2 agents | Q1 FY2026 | First proposals expected within 75-day sales cycle; first milestone invoices due in Q2 |
| Q2 FY2026 | none | 0 | n/a | Series A (£10m) closes; CFO handles investor reporting and bank set-up personally |
| Q3 FY2026 | none; requisition for Finance Manager opened | 0 | n/a | Trigger for requisition: monthly invoices >= 12, or close taking more than 8 working days, or Series A reporting covenants live |
| Q4 FY2026 | Finance Manager | 1 | Q4 FY2026 | Annual budget cycle BUD-2027 opens in Q4 and needs a dedicated FP&A owner; agent owner role must be filled by a human |

### FY2027 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2027 | Senior Accountant | 1 | Q1 FY2027 | US entity (Inc.) set-up in Q1, SOC 2 Type II readiness (COMPANY.md §8) and 65-client billing base need a proper ledger owner |
| H1 FY2027 | Billing and Collections Specialist | 1 | Q2 FY2027 | Monthly invoices > 40 or DSO above 45 days for two consecutive months |
| H1 FY2027 | Close and Reconciliation Agent; FP&A and Cash Forecast Agent; Revenue Recognition Agent | 3 agents | Q1 FY2027 | Senior Accountant and Finance Manager in post as owners |
| H2 FY2027 | Finance Analyst | 1 | Q3 FY2027 | FP&A request backlog > 10 working days, FY2028 budget cycle approaching, Data and Executive reporting demand |

### FY2028 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2028 | Financial Controller | 1 | Q2 FY2028 | Revenue run-rate above £35m, statutory audit scope and two entities exceed CFO span; Senior Accountant and Billing and Collections Specialist re-line |
| H1 FY2028 | Billing and Collections Specialist | 1 | Q2 FY2028 | Monthly invoices > 100 (UK and US), US share of revenue at 30% |
| H1 FY2028 | Billing and Collections Agent (2nd); Close and Reconciliation Agent (2nd); AP and Spend Control Agent; Audit and Compliance Evidence Agent | 4 agents | Q1 to Q2 FY2028 | US ledger live; audit and SOC 2 evidence load |
| H2 FY2028 | Senior Accountant | 1 | Q3 FY2028 | Close taking more than 6 working days in two consecutive months, or reconciliation exceptions over 30 days old above 5 |
| H2 FY2028 | Finance Analyst | 1 | Q3 FY2028 | Budget cycle BUD-2029 preparation, 230 humans of budget holders |
| H2 FY2028 | Treasury and Tax Specialist | 1 | Q4 FY2028 | Transfer-pricing documentation, multi-state US sales tax and FX exposure exceed Controller capacity |

Year-end check: FY2026 = CFO + Finance Manager = 2; FY2027 adds Senior Accountant, Billing and Collections Specialist, Finance Analyst = 5; FY2028 adds Financial Controller, Billing and Collections Specialist, Senior Accountant, Finance Analyst, Treasury and Tax Specialist = 10. Attrition (14% falling to 11%, COMPANY.md §8) is handled as backfill within the same requisition and is not additive. US-based finance hires, if any, carry the +15% band uplift (COMPANY.md §6.2); none are planned, as US work is handled by the Treasury and Tax Specialist with outsourced US tax advisers under non-people spend.

## 6. Interfaces

Topics are those in `core/topics.py` and CONVENTIONS.md §7.

### Finance publishes (prefix `finance.`)

| Topic | Delivered to | Used for |
|---|---|---|
| `finance.pricing_check_completed` | sales | Result of the pricing and discount check on a proposal |
| `finance.billing_schedule_created` | delivery, customer_success | Milestone or Keep billing schedule agreed from signed contract |
| `finance.invoice_issued` | customer_success, data | Invoice raised after milestone acceptance or on Keep monthly cycle |
| `finance.payment_received` | sales, customer_success, data | Cash applied |
| `finance.invoice_overdue` | customer_success, legal, sales | Ladder stage reached (day 31 onwards) |
| `finance.collections_escalated` | legal, executive | Day 45 CFO escalation and day 60 legal letter |
| `finance.budget_cycle_opened` | all other departments | Annual budget cycle (BUD-YYYY) opens in Q4 |
| `finance.budget_consolidated` | executive | Consolidated budget against COMPANY.md §5.4 |
| `finance.budget_variance_flagged` | executive | In-year variance above threshold |
| `finance.cash_forecast_updated` | executive, data | Rolling cash forecast and runway |
| `finance.month_end_closed` | executive, data | Close completed with revenue, gross margin and DSO |

Generic: `finance.budget_submitted` (to executive) and `finance.hire_requested` (to people).

### Finance subscribes to (supply and trigger)

| Group | Topics | Why Finance needs them |
|---|---|---|
| Deal to cash | `sales.proposal_requested`, `sales.deal_approval_requested`, `sales.deal_won`, `sales.renewal_proposal_sent`, `legal.contract_signed`, `delivery.scoping_completed`, `delivery.engagement_kickoff`, `delivery.milestone_reached`, `delivery.scope_change_requested`, `delivery.engagement_completed`, `executive.deal_decision_made`, `external.client_payment_received`, `legal.client_dispute_raised`, `customer_success.renewal_due`, `customer_success.renewal_confirmed`, `customer_success.client_churned` | Pricing check, billing schedules, invoicing, cash application, change-order billing, collections holds on disputes, renewal and churn revenue effects |
| Budget and planning | `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated`, `executive.pricing_change_approved`, `executive.crisis_declared`, `executive.board_meeting_held`, `executive.headcount_approved`, `product.pricing_change_proposed`, all `<d>.budget_submitted`, `data.forecast_updated`, `data.kpi_report_published`, `delivery.capacity_forecast_updated`, `marketing.campaign_launched` | Budget approval, price-list changes, forecast inputs, programme-spend commitments |
| People and cost | `people.requisition_opened`, `people.offer_accepted`, `people.new_hire_started`, `people.employee_left`, `people.contractor_engaged` | Headcount cost tracking, payroll and contractor set-up, leaver final pay |
| Vendors and spend | `operations.vendor_review_requested`, `operations.vendor_approved`, `operations.procurement_order_placed`, `it_security.vendor_risk_assessed` | Vendor cost approval, purchase-order matching, spend authority (COMPANY.md §9.3) |

### Dependencies on other departments (data Finance needs, by key)

| From | Needed | Body keys |
|---|---|---|
| Sales | Tier, price, discount, payment terms | `deal_id`, `proposal_id`, `tier`, `amount_gbp`, `service_line` |
| Legal | Signed contract terms and dates | `contract_id`, `client_id`, `amount_gbp` |
| Delivery | Milestone acceptance, scope changes, utilisation | `engagement_id`, `milestone`, `amount_gbp` |
| Customer Success | Renewals, churn, Keep tier | `client_id`, `tier` |
| People | Offers, starters, leavers, contractors | `requisition_id`, `employee_id` |
| Operations | Approved vendors, purchase orders | `vendor_id`, `amount_gbp` |

## 7. Risks and dependencies

| # | Risk | Likelihood / impact | Mitigation and owner |
|---|---|---|---|
| 1 | Key-person dependency: in FY2026 the CFO is the only human until Q4 (one person approves, posts and reconciles; no segregation of duties) | High / High | Agents propose only; bank payment approvals dual-controlled with the CEO as second approver; external bookkeeping and accountant on a monthly retainer within non-people spend; Finance Manager hired Q4 FY2026 (CFO) |
| 2 | DSO drifts above 45 days or invoices late because milestone acceptance is not signalled by Delivery | Medium / High | `delivery.milestone_reached` is the only invoice trigger; weekly unbilled-WIP report to Delivery; 2-business-day invoice SLA tracked as a KPI (Billing and Collections Specialist) |
| 3 | Client concentration above 15% of revenue (COMPANY.md §8) or one large Forge Scale deal skews cash | Medium / High | Concentration check inside every pricing check and quarterly board pack; CFO flag to CEO and Board (Finance Manager) |
| 4 | Pricing leakage through uncontrolled discounting and non-standard terms | Medium / Medium | Pricing and Deal Desk Agent blocks any proposal above 10% discount until CFO and CEO approve (§9.3); monthly discount-leakage review |
| 5 | Revenue recognition error on percentage-of-completion (overstated progress, early recognition) | Medium / High | Revenue Recognition Agent proposes, Senior Accountant approves; Delivery sign-off on progress; auditor review at year-end |
| 6 | Payment fraud and mandate fraud (fake supplier bank details, CEO impersonation) | Medium / Critical | Agents cannot approve payments above £10,000 or change bank details (§9.4); call-back verification; dual approval above £10,000; Treasury and Tax Specialist owns the payment-run control from FY2028 |
| 7 | US launch (Q1 FY2027): Delaware entity, sales tax nexus by state, transfer pricing, USD billing at £1 = $1.27 planning rate; launch gated on >= £10m ARR run-rate and ISO 27001 (COMPANY.md §8) | Medium / High | Outsourced US tax adviser from Q4 FY2026; Senior Accountant owns the Inc. ledger from Q1 FY2027; FX-gain/loss policy approved by the Audit and Risk Committee (Marcus Ellery) |
| 8 | Statutory and tax compliance: Companies House filing, HMRC VAT, corporation tax, PAYE, R&D credit claims, Late Payment Act interest | Low / High | Compliance calendar owned by the Financial Controller (CFO until Q2 FY2028); no filings made by agents |
| 9 | Hiring slippage (45-day time-to-hire) leaves close or collections understaffed | Medium / Medium | Requisitions opened one quarter ahead of start; contract accountant bridge available inside non-people budget |
| 10 | Cash runway: EBITDA -£1.5m in FY2026 against a £13.5m total raise (COMPANY.md §1, §5.1) | Low / Critical | 13-week cash forecast published each month to Executive and Board; runway alert if forecast cash falls below 12 months of cost |

Key dependencies: People for approved requisitions; Legal for signed contracts and dispute flags; Delivery for milestone acceptance; Data for forecast and KPI inputs; IT and Security for finance-system access control (least privilege, access revoked on `people.employee_left`).

## 8. Sources

- COMPANY.md §1 (identity, fiscal year, GBP and USD planning rate, funding)
- COMPANY.md §3 (price list) and §3.5 (rate card for change orders)
- COMPANY.md §5.1 (revenue, gross margin, EBITDA) and §5.2 (loaded cost, agent cost range)
- COMPANY.md §5.3 (commercial funnel, sales and marketing cost for CAC context)
- COMPANY.md §5.4 (finance budget envelope: people £210k / £480k / £800k; non-people £100k / £250k / £700k; total £310k / £730k / £1,500k)
- COMPANY.md §6, §6.1 (headcount: finance 2 / 5 / 10 humans; 2 / 5 / 9 agents) and §6.2 (levels and salary bands)
- COMPANY.md §7 (billing terms, collections ladder, targets, revenue recognition)
- COMPANY.md §8 (assumptions: attrition, time-to-hire, US gating, concentration policy)
- COMPANY.md §9.2 (Hannah Whitcombe as CFO), §9.3 (delegations of authority), §9.4 (AI agent governance)
- CONVENTIONS.md §3.1 (blueprint template) and §7 (topic lifecycle chains)
