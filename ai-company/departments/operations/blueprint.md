# Operations Department Blueprint

> Department id `operations`; agent class `OperationsAgent`. Head: Beatrice Moreau, Chief Operating Officer (COMPANY.md §9.2). All figures are fictional modeled assumptions consistent with COMPANY.md.

## 1. Mission and scope

**Mission.** Run the machinery that lets Lumenhall Partners grow from 38 humans at the end of FY2026 to 110 and then 230 (COMPANY.md §6) without losing control of spend, risk or the quality of the working environment. Operations buys what the firm needs at a fair price and with an audit trail, makes sure every new colleague has a desk and kit on day one, turns legal and regulatory findings into closed actions, keeps the firm able to operate through an incident, and runs the internal programmes and process improvements that keep the firm's own cost per head falling.

Operations is an operating-expense department, not cost of revenue (COMPANY.md §5.1). Its budget envelope is £300k / £700k / £1,650k (people £200k / £400k / £750k; non-people £100k / £300k / £900k) per COMPANY.md §5.4.

| Area | What Operations owns | Standing targets |
|---|---|---|
| Procurement and sourcing | Intake of quotes, the three-quote rule, sourcing recommendation, purchase orders (POs), spend thresholds and split-order control | Three quotes at or above £2,500; formal tender at or above £25,000; agents never approve payments above £10,000 (COMPANY.md §9.4); non-budgeted spend above £50k needs the CFO and above £250k the CEO (COMPANY.md §9.3) |
| Vendor management | Vendor onboarding requests, coordination of the security, legal and finance review, vendor register, performance scorecards, renewals and exit plans | New vendor processing personal or client data, with system access, or an AI platform: review regardless of value; other new vendors from £10,000 a year |
| Workspace and facilities | London HQ (Shoreditch) and, from Q1 FY2027, the New York City office; desks, equipment pool, supplies, health and safety, fire safety, display-screen equipment (DSE) assessments, event and meeting-space logistics | Desk and kit ready on or before each start day (`operations.workspace_ready`); leaver equipment recovered within 5 business days |
| Compliance actions | Turning `legal.compliance_finding_raised` into owned actions, tracking them to closure, evidencing closure to Legal, aligning operating procedures with `legal.policy_update_published` | Actions closed by severity: critical 5, high 10, medium 20, low 40 business days |
| Business continuity | Continuity plan, vendor and supplier contingency, annual test programme, incident and crisis logistics (jointly with IT Security) | At least 2 continuity tests in FY2026; Tier-1 systems recovery time objective (RTO) 4 hours |
| PMO and process improvement | Portfolio of internal programmes (US launch, ISO 27001 and SOC 2 operational readiness, systems roll-outs), process documentation, improvement proposals with a measured benefit | Proposal published to Executive when annualised benefit is at least £10,000; payback within 12 months |
| Budget and capacity | Operations budget submission, 80% budget-line warnings with Finance, quarterly capacity review | Budget envelopes per COMPANY.md §5.4 |

**Out of scope.** Payment release, ledger and bank approvals (Finance), contract drafting and negotiation of legal terms, regulator notification and policy authorship (Legal), security assessment of vendors, laptop imaging, accounts and access (IT Security), recruiting and employment administration (People), client-facing delivery and client programme management (Delivery), marketing event content (Marketing; Operations supplies venue, logistics and procurement).

Operating principle: Operations is a control function that must not become a bottleneck. Low-value, low-risk purchases and routine readiness tasks run on agent-prepared rails; judgement, approval and anything touching regulators, bank details or contracts stays with named humans.

## 2. Org chart

```
Chief Operating Officer (head)                       Beatrice Moreau, reports to CEO
|
+-- Operations Manager                               manager; joins Q3 FY2027
|     +-- Procurement and Workspace Specialist       consultant; joins Q4 FY2026 (reports to the COO until Q3 FY2027)
|     +-- Vendor Management Specialist x1            consultant; joins Q3 FY2028
|     +-- Workspace and Facilities Associate x1 (Q4 FY2027), x2 (Q3 FY2028)   analyst
|     +-- Operations Analyst x1 (Q4 FY2027), x2 (Q4 FY2028)                   analyst
|
+-- Compliance and Risk Specialist x1 (Q2 FY2027), x2 (Q3 FY2028)             consultant; reports to the COO
|
+-- PMO Lead                                         manager; joins Q3 FY2028
|     +-- PMO Analyst x1                             analyst; joins Q4 FY2028
|
+-- AI agents (see section 4), each with a named human owner
```

Reporting-line notes. In FY2026 the COO runs everything personally; the Procurement and Workspace Specialist joins in Q4 FY2026 and reports to the COO. From Q3 FY2027 the Operations Manager runs day-to-day operations, so the Procurement and Workspace Specialist, the Workspace and Facilities Associates, the Operations Analysts and (from FY2028) the Vendor Management Specialist report to the Operations Manager. The Compliance and Risk Specialist reports directly to the COO so that compliance tracking stays independent of the people who must close the actions. Until the PMO Lead joins (Q3 FY2028) the Operations Manager runs the programme office.

## 3. Roles

Headcount is year-end humans and sums to COMPANY.md §6.1: operations = 2 / 6 / 12. Level keys and bands are from COMPANY.md §6.2. Titles are the reference titles for `kpis.md`, `sops.md` and `agent.py`.

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Operating Officer | head | Chief Executive Officer | 1 | 1 | 1 | 140,000 to 200,000 (cash; plus equity) | Owns operations strategy and budget; approves purchase orders from £10,000 to £50,000; vendor and compliance escalations; continuity plan sponsor; PMO sponsor; covers every unfilled operations seat until it is hired; owner of the agent register entries for operations agents until each seat is filled |
| Operations Manager | manager | Chief Operating Officer | 0 | 1 | 1 | 92,000 to 115,000 | Runs day-to-day operations from Q3 FY2027: approves purchase orders from £2,500.01 to £10,000, process-improvement portfolio, business continuity plan and tests, quarterly capacity review; owner of the PMO and Process Agent and the Business Continuity Agent |
| Procurement and Workspace Specialist | consultant | Chief Operating Officer (to Q3 FY2027); then Operations Manager | 1 | 1 | 1 | 55,000 to 70,000 | Quote intake and three-quote comparison, purchase orders up to £2,500 (human or agent), vendor onboarding coordination, desk and equipment pool, new-hire workspace readiness, supplier relationships for facilities; owner of the Procurement and Vendor Agent and the Workspace and Onboarding Agent |
| Compliance and Risk Specialist | consultant | Chief Operating Officer | 0 | 1 | 2 | 55,000 to 70,000 | Tracks compliance findings and regulatory changes to closure, evidences closure to Legal, health and safety and fire-safety records, operating-risk register, continuity test evidence; owner of the Compliance Tracking Agent |
| Workspace and Facilities Associate | analyst | Operations Manager | 0 | 1 | 2 | 38,000 to 48,000 | Daily desk, kit and meeting-space operations, asset register, leaver equipment recovery, event logistics with Marketing, New York office day-to-day (second Associate from Q3 FY2028) |
| Operations Analyst | analyst | Operations Manager | 0 | 1 | 2 | 38,000 to 48,000 | Spend and PO analytics, KPI reporting for operations, vendor scorecard data, budget tracking inputs for Finance, process data collection |
| Vendor Management Specialist | consultant | Operations Manager | 0 | 0 | 1 | 55,000 to 70,000 | Vendor register ownership, quarterly performance reviews of critical vendors, renewal and exit planning, concentration monitoring; owner of the Vendor Performance Agent and the second Procurement and Vendor Agent |
| PMO Lead | manager | Chief Operating Officer | 0 | 0 | 1 | 92,000 to 115,000 | Portfolio of internal programmes, benefits tracking, steering committee papers, delivery of the process-improvement pipeline; takes over the PMO and Process Agent from the Operations Manager |
| PMO Analyst | analyst | PMO Lead | 0 | 0 | 1 | 38,000 to 48,000 | Programme plans, RAID logs (risks, assumptions, issues, dependencies), status reports, benefits data |
| **Total humans** | | | **2** | **6** | **12** | | Equals COMPANY.md §6.1 row for operations |

Year-end headcount check by role: FY2026 = COO + Procurement and Workspace Specialist = 2. FY2027 adds Compliance and Risk Specialist, Operations Manager, Workspace and Facilities Associate, Operations Analyst = 6. FY2028 adds Compliance and Risk Specialist (2nd), Workspace and Facilities Associate (2nd), Operations Analyst (2nd), Vendor Management Specialist, PMO Lead, PMO Analyst = 12.

### Planning salary points and cost check

Loaded cost = base x 1.28 (COMPANY.md §5.2). Planning base salaries sit inside the §6.2 bands and are held flat across years. Average FTE reflects the start quarter (Q1 start = 1.00, Q2 = 0.75, Q3 = 0.50, Q4 = 0.25 of a year).

| Role | Planning base £ | Loaded £ | FY2026 avg FTE | FY2027 avg FTE | FY2028 avg FTE | FY2026 £k | FY2027 £k | FY2028 £k |
|---|---|---|---|---|---|---|---|---|
| Chief Operating Officer | 140,000 | 179,200 | 1.00 | 1.00 | 1.00 | 179.2 | 179.2 | 179.2 |
| Procurement and Workspace Specialist | 58,000 | 74,240 | 0.25 | 1.00 | 1.00 | 18.6 | 74.2 | 74.2 |
| Compliance and Risk Specialist (1st) | 62,000 | 79,360 | 0 | 0.75 | 1.00 | 0 | 59.5 | 79.4 |
| Operations Manager | 96,000 | 122,880 | 0 | 0.50 | 1.00 | 0 | 61.4 | 122.9 |
| Workspace and Facilities Associate (1st) | 40,000 | 51,200 | 0 | 0.25 | 1.00 | 0 | 12.8 | 51.2 |
| Operations Analyst (1st) | 40,000 | 51,200 | 0 | 0.25 | 1.00 | 0 | 12.8 | 51.2 |
| PMO Lead | 98,000 | 125,440 | 0 | 0 | 0.50 | 0 | 0 | 62.7 |
| Vendor Management Specialist | 60,000 | 76,800 | 0 | 0 | 0.50 | 0 | 0 | 38.4 |
| Compliance and Risk Specialist (2nd) | 62,000 | 79,360 | 0 | 0 | 0.50 | 0 | 0 | 39.7 |
| Workspace and Facilities Associate (2nd) | 42,000 | 53,760 | 0 | 0 | 0.50 | 0 | 0 | 26.9 |
| Operations Analyst (2nd) | 40,000 | 51,200 | 0 | 0 | 0.25 | 0 | 0 | 12.8 |
| PMO Analyst | 40,000 | 51,200 | 0 | 0 | 0.25 | 0 | 0 | 12.8 |
| **Total people cost** | | | **1.25** | **3.75** | **8.50** | **197.8** | **400.0** | **751.4** |
| COMPANY.md §5.4 people envelope | | | | | | 200 | 400 | 750 |
| Delta | | | | | | -2.2 | 0.0 | +1.4 |

All three years are within the £5k tolerance. The full build-up lives in `economics.md`.

## 4. AI agents

Agent counts sum to COMPANY.md §6.1: operations = 1 / 4 / 8. Every agent is registered in the agent register (Data and IT Security) and has a named accountable human (COMPANY.md §9.4). All agents share these hard limits: they may draft, analyse, monitor and propose; they may not sign contracts, approve payments above £10,000, approve any purchase order above £2,500, change supplier bank details, accept a vendor risk on behalf of the CISO, notify a regulator, or close a compliance finding without a human attestation.

In code the whole department is one `OperationsAgent` class. The agent personas in this table are the registered agent-register entries that specialise it; in FY2026 a single registered agent (the Procurement and Vendor Agent) covers procurement, workspace and compliance tracking under the COO, and the later entries split the same behaviours as volume grows.

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Procurement and Vendor Agent | Procurement and Workspace Specialist (COO until Q4 FY2026; Vendor Management Specialist for the second agent from Q3 FY2028) | On `external.vendor_quote_received`: registers the quote against its RFQ, checks validity (30 days), counts compliant quotes, scores them, recommends a supplier, checks the budget line, requests vendor review for unapproved vendors (`operations.vendor_review_requested`) and places purchase orders within its authority (`operations.procurement_order_placed`); detects split orders | May release a PO of up to £2,500 on an approved vendor, within a budgeted line, with a single quote. Every other PO is prepared and routed to the human approver in the SOP-OPERATIONS-02 ladder. Cannot approve a sole-source exception, change supplier details or release a payment. Second agent (FY2028) covers New York spend and US vendors | 1 | 1 | 2 |
| Compliance Tracking Agent | Compliance and Risk Specialist (COO until Q2 FY2027) | Turns `legal.compliance_finding_raised` and `legal.regulatory_change_noted` into owned actions with due dates by severity, runs the weekly open-actions report, aligns procedures after `legal.policy_update_published`, emits `operations.compliance_action_completed` once a human has attested closure | Cannot close an action, cannot assess legal merit, cannot extend a due date set by Legal. Second agent (FY2028) covers the US entity and SOC 2 evidence | 0 | 1 | 2 |
| Workspace and Onboarding Agent | Procurement and Workspace Specialist (Workspace and Facilities Associate from Q4 FY2027 for daily running) | On `people.new_hire_started` and `it_security.access_provisioned`: reserves desk and equipment kit, checks stock, orders shortfalls up to £2,500, emits `operations.workspace_ready`; runs leaver asset recovery on `people.employee_left` | Cannot buy above £2,500, cannot decommission an asset without the Associate's confirmation, cannot reassign a desk contrary to the facilities plan | 0 | 1 | 1 |
| PMO and Process Agent | Operations Manager (COO until Q3 FY2027; PMO Lead for programmes from Q3 FY2028) | Maintains the internal programme portfolio from `executive.okrs_set` and `executive.strategy_updated`; turns `data.data_quality_issue_raised` into process-fix proposals; measures benefits; emits `operations.process_improvement_proposed` | Proposes only; cannot start a programme, cannot reassign people or budget, cannot publish a proposal below the £10,000 annualised benefit threshold | 0 | 1 | 1 |
| Vendor Performance Agent | Vendor Management Specialist | Builds monthly vendor scorecards (delivery, quality, incidents, spend against PO), watches contract notice dates (90 days for critical vendors, 60 days otherwise), proposes renewals and exits | Cannot terminate or renew a contract, cannot change a vendor's tier | 0 | 0 | 1 |
| Business Continuity Agent | Operations Manager | Maintains the continuity plan inventory, schedules the test programme, drafts test scenarios, records RTO and RPO results from exercises and live incidents (`it_security.incident_detected`, `it_security.incident_resolved`, `executive.crisis_declared`), emits `operations.continuity_test_completed` | Cannot declare a crisis, cannot invoke a vendor's disaster-recovery clause, cannot spend above £2,500 in an emergency without the human approver | 0 | 0 | 1 |
| **Total agents** | | | **1** | **4** | **8** | |

Agent cost is carried in non-people spend (AI compute and tooling), within the £100k / £300k / £900k non-people envelope, at the £20k to £35k per agent-year range of COMPANY.md §5.2 (see `economics.md` section 1).

## 5. Hiring plan

Time-to-hire is 45 days for humans and 5 days for agent provisioning (COMPANY.md §8, assumption 3). Every human hire goes through `operations.hire_requested` then `people.requisition_opened`, then `executive.headcount_approved`, because these hires are inside the approved §5.4 budget but still need the CEO's headcount approval record (COMPANY.md §9.3). Planned start quarters assume offer acceptance 45 days earlier.

### FY2026 (quarterly)

| Quarter | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| Q1 FY2026 | Chief Operating Officer (Beatrice Moreau) | 1 | Q1 FY2026 (in post from Day 0, 2026-01-05) | Founding executive team (COMPANY.md §9.2) |
| Q1 FY2026 | Procurement and Vendor Agent | 1 agent | Q1 FY2026 | First vendor quotes and the Series A programme spend (Q2) need an audit trail from the first order |
| Q2 FY2026 | none | 0 | n/a | COO runs procurement, workspace and compliance personally with the agent; flexible workspace contract and equipment pool set up |
| Q3 FY2026 | none; requisition for Procurement and Workspace Specialist opened | 0 | n/a | Requisition trigger: more than 6 new starters in a quarter, or more than 15 purchase requests a month, or workspace-ready misses on two consecutive cohorts |
| Q4 FY2026 | Procurement and Workspace Specialist | 1 | Q4 FY2026 | 38 humans by year end, New York office fit-out and annual budget cycle BUD-2027; the agent needs a human owner (COMPANY.md §9.4) |

### FY2027 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2027 | Workspace and Onboarding Agent | 1 agent | Q1 FY2027 | New York office opens (COMPANY.md §1) and 81 gross hires are planned for the year |
| H1 FY2027 | Compliance and Risk Specialist | 1 | Q2 FY2027 | SOC 2 Type II (COMPANY.md §8, assumption 7) and UK/EU regulatory findings above 2 open actions a month; COO span exceeded |
| H1 FY2027 | Compliance Tracking Agent | 1 agent | Q2 FY2027 | Compliance and Risk Specialist in post as owner |
| H2 FY2027 | Operations Manager | 1 | Q3 FY2027 | 110 humans by year end across two offices; COO span of control above 6 direct activities; process-improvement backlog above 10 |
| H2 FY2027 | PMO and Process Agent | 1 agent | Q3 FY2027 | Operations Manager in post as owner |
| H2 FY2027 | Workspace and Facilities Associate; Operations Analyst | 2 | Q4 FY2027 | More than 8 starters a month or two sites; KPI reporting and PO analytics backlog above 10 working days |

### FY2028 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2028 | Procurement and Vendor Agent (2nd); Compliance Tracking Agent (2nd) | 2 agents | Q1 to Q2 FY2028 | US entity spend and US compliance; 220 active vendors by year end (see `economics.md`) |
| H2 FY2028 | PMO Lead | 1 | Q3 FY2028 | More than 8 concurrent internal programmes or programme benefits above £400k a year |
| H2 FY2028 | Vendor Management Specialist; Vendor Performance Agent | 1 human + 1 agent | Q3 FY2028 | More than 150 active vendors or more than 25 critical vendors needing quarterly review |
| H2 FY2028 | Compliance and Risk Specialist (2nd) | 1 | Q3 FY2028 | Open compliance actions above 15 per specialist for two consecutive months |
| H2 FY2028 | Workspace and Facilities Associate (2nd) | 1 | Q3 FY2028 | New York headcount above 40 and 139 gross hires for the year |
| H2 FY2028 | Operations Analyst (2nd); PMO Analyst | 2 | Q4 FY2028 | Spend analytics for two entities; PMO reporting load |
| H2 FY2028 | Business Continuity Agent | 1 agent | Q4 FY2028 | SOC 2 and client contractual continuity requirements need continuous evidence |

Year-end check: FY2026 = COO + Procurement and Workspace Specialist = 2; FY2027 adds Compliance and Risk Specialist, Operations Manager, Workspace and Facilities Associate, Operations Analyst = 6; FY2028 adds PMO Lead, Vendor Management Specialist, Compliance and Risk Specialist (2nd), Workspace and Facilities Associate (2nd), Operations Analyst (2nd), PMO Analyst = 12. Agent check: 1 / 4 (adds Workspace and Onboarding, Compliance Tracking, PMO and Process) / 8 (adds Procurement and Vendor 2nd, Compliance Tracking 2nd, Vendor Performance, Business Continuity). Attrition (14% falling to 11%, COMPANY.md §8) is handled as backfill within the same requisition and is not additive. US-based operations hires, if any, carry the +15% band uplift (COMPANY.md §6.2); none are planned, as New York facilities are served by the London team plus contracted facilities management in non-people spend.

## 6. Interfaces

Topics are those in `core/topics.py` and CONVENTIONS.md §7.

### Operations publishes (prefix `operations.`)

| Topic | Delivered to | Used for |
|---|---|---|
| `operations.vendor_review_requested` | legal, it_security, finance | A new vendor, or a renewal due for re-review, needs contract, security and financial review |
| `operations.vendor_approved` | finance, it_security | Vendor cleared for use; Finance activates it in payables and IT Security verifies conditions before data flows |
| `operations.procurement_order_placed` | finance | A purchase order exists; Finance creates the commitment and matches the invoice |
| `operations.workspace_ready` | people | Desk, equipment and facilities ready for a named new starter |
| `operations.compliance_action_completed` | legal | A compliance finding has an evidenced, human-attested closure |
| `operations.continuity_test_completed` | executive, it_security | Result of a tabletop, technical or live-incident continuity test |
| `operations.process_improvement_proposed` | executive | Process improvement with benefit, cost and payback for Executive visibility |

Generic: `operations.budget_submitted` (to finance) and `operations.hire_requested` (to people).

### Operations subscribes to (supply and trigger)

| Group | Topics | Why Operations needs them |
|---|---|---|
| Sourcing | `external.vendor_quote_received` | Quotes arrive from suppliers (the only external entry point to Operations) |
| Vendor review | `it_security.vendor_risk_assessed` | Security tier, rating and conditions drive approval, rejection or conditions |
| People lifecycle | `people.new_hire_started`, `people.employee_left`, `it_security.access_provisioned`, `delivery.staffing_requested` | Workspace readiness, equipment recovery, desk capacity planning |
| Engagements and events | `delivery.engagement_kickoff`, `marketing.event_scheduled` | Client-site logistics, engagement rooms, venue and event procurement |
| Compliance | `legal.compliance_finding_raised`, `legal.regulatory_change_noted`, `legal.policy_update_published` | Action tracking and procedure alignment |
| Security and continuity | `it_security.incident_detected`, `it_security.incident_resolved`, `it_security.vulnerability_found`, `executive.crisis_declared` | Continuity logistics, vendor and asset response, post-incident continuity evidence |
| Process and strategy | `data.data_quality_issue_raised`, `executive.okrs_set`, `executive.strategy_updated` | Process fixes, programme portfolio alignment |
| Budget | `finance.budget_cycle_opened`, `executive.budget_approved` | Annual budget submission and release by quarter |

### Dependencies on other departments (data Operations needs, by key)

| From | Needed | Body keys |
|---|---|---|
| Suppliers (external) | Quote with price, validity, vendor details | `quote_id`, `rfq_id`, `vendor_id`, `vendor_name`, `amount_gbp`, `valid_until_day` |
| People | Starter details, start day, equipment profile, leaver last day | `employee_id`, `employee_name`, `start_day`, `equipment`, `location`, `last_day` |
| IT Security | Vendor risk tier and decision; access readiness | `vendor_id`, `tier`, `decision`, `conditions`, `employee_id` |
| Legal | Findings with severity, due day and policy updates | `finding_id`, `severity`, `due_day`, `policy_id` |
| Finance | Budget cycle and envelopes; PO and budget line status | `budget_cycle_id`, `fiscal_year` |
| Delivery | Engagement kickoff and staffing needs | `engagement_id`, `client_id`, `team_size`, `start_day` |
| Marketing | Event date, venue need, attendees, budget | `event_id`, `event_date_day`, `attendees`, `budget_gbp` |

## 7. Risks and dependencies

| # | Risk | Likelihood / impact | Mitigation and owner |
|---|---|---|---|
| 1 | Key-person dependency: in FY2026 the COO is the only human until Q4; one person receives quotes, approves orders and chases compliance with no segregation of duties | High / High | Agent prepares, never approves above £2,500; every PO above £2,500 has a second approver (CFO for the COO's own large orders, SOP-OPERATIONS-02); Finance matches invoices to POs independently; Procurement and Workspace Specialist hired Q4 FY2026 (COO) |
| 2 | Maverick and split purchasing: orders cut to dodge the £2,500 three-quote threshold or the approval ladder | Medium / High | Aggregation rule by vendor and category over 30 days; daily PO register scan by the Procurement and Vendor Agent; Finance "no PO, no pay" control (Finance Manager); monthly review of orders between £2,000 and £2,499 (Operations Manager) |
| 3 | Vendor concentration or insolvency of a critical supplier (cloud, AI platform, payroll bureau, office provider) | Medium / High | Critical-vendor list, exit plan and annual financial-health check; single supplier above 20% of cloud or AI spend reviewed with IT Security annually (Vendor Management Specialist; COO before) |
| 4 | Third-party data risk: a vendor starts processing client personal data before security and legal review | Medium / Critical | Vendor review is mandatory before any data flows regardless of value; IT Security blocks access until `operations.vendor_approved` conditions are verified (Procurement and Workspace Specialist; CISO Wei Zhang as decision owner) |
| 5 | Workspace not ready on day one, especially during New York opening and the 81 / 139 gross-hire years | Medium / Medium | Kit reserved when `delivery.staffing_requested` or the offer lands; buffer stock of 10% of annual starters; same-day agent order up to £2,500; people KPI day_one_readiness_rate is shared (Procurement and Workspace Specialist) |
| 6 | Compliance finding drifts past its due date because the action owner is busy | Medium / High | Due date set by severity (critical 5, high 10, medium 20, low 40 business days), weekly open-actions report, escalation to the COO at the due date and to the CEO 7 days later (Compliance and Risk Specialist) |
| 7 | Continuity plan exists on paper but untested; recovery objectives not met in a real incident | Medium / High | Two tests in FY2026, four from FY2027; every high or critical live incident counted as a test with findings (Operations Manager; COO before Q3 FY2027) |
| 8 | US launch (New York office Q1 FY2027) strains premises, payroll hosting, insurance and compliance set-up | Medium / High | Serviced office with short break clause before any long lease; US compliance checklist with Legal and Finance; launch gated on ARR and ISO 27001 (COMPANY.md §8, assumption 6) (COO) |
| 9 | Process-improvement proposals with overstated savings erode Executive trust | Medium / Medium | Benefit validated by Finance before `operations.process_improvement_proposed`; savings counted in KPI only after a 90-day post-implementation check (Operations Manager; PMO Lead from FY2028) |
| 10 | Operations budget overrun from workspace and New York fit-out, the largest non-people lines | Medium / Medium | 80% budget-line warning agreed with Finance (SOP-OPERATIONS-13); break clauses; COO holds a £30k FY2028 contingency released only through COMPANY.md §9.3 limits |

Key dependencies: Finance for budget, PO commitment and payment release; IT Security for vendor assessment, laptop imaging and access; Legal for findings, contracts and policy; People for starter and leaver data; Data for data-quality signals; Executive for OKRs and strategy.

## 8. Sources

- COMPANY.md §1 (identity, headquarters, New York office from Q1 FY2027, fiscal year, planning rate)
- COMPANY.md §5.1 (operating expense classification) and §5.2 (loaded cost, agent cost range)
- COMPANY.md §5.4 (operations budget envelope: people £200k / £400k / £750k; non-people £100k / £300k / £900k; total £300k / £700k / £1,650k)
- COMPANY.md §6, §6.1 (headcount: operations 2 / 6 / 12 humans; 1 / 4 / 8 agents) and §6.2 (levels and salary bands)
- COMPANY.md §8 (assumptions: attrition, time-to-hire, US launch gating, compliance baseline, ISO 27001, Cyber Essentials Plus, SOC 2)
- COMPANY.md §9.2 (Beatrice Moreau as COO), §9.3 (delegations of authority), §9.4 (AI agent governance)
- CONVENTIONS.md §3.1 (blueprint template), §4 (ID formats) and §7 (topic lifecycle chains: vendors, compliance, hiring, security incident, budgeting)
