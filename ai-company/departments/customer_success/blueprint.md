# Customer Success Department Blueprint

## 1. Mission and scope

The Customer Success department keeps Lumenhall's clients healthy, supported, renewed and expanding after the contract is signed. It is led by the Chief Customer Officer, Tobias Lindgren, who reports to the CEO, Imogen Hartley (COMPANY.md §9.2). It owns the client relationship once delivery starts, the Keep retainer support tiers and their SLAs, and the renewal and churn-prevention engine that carries net revenue retention of 115% in FY2027 and 118% in FY2028 (COMPANY.md §5.1).

| Area | What Customer Success owns | Standing targets |
|---|---|---|
| Onboarding and handover | Welcome call, stakeholder map, success plan and health baseline from `sales.deal_won` and `legal.contract_signed`; handover pack to the client at `delivery.engagement_kickoff` | Handover complete within 15 days of contract signature in FY2026 (kpis.md `onboarding_handover_days`) |
| Health scoring | Weighted 0 to 100 client health score (adoption, delivery, engagement, commercial, sentiment, support), weekly refresh, bands green, amber, red; publishes `customer_success.health_score_updated` | 60% of clients green and an average score of 72 in FY2026 |
| Keep support tiers and SLAs | Triage of every ticket by Keep tier (Essential, Plus, Enterprise, COMPANY.md §3.3), priority P1 to P4, first-response and resolution clocks, escalation to Delivery and Product via `customer_success.support_escalated` | 95% of tickets answered inside the first-response SLA |
| Voice of the client | NPS, CSAT, complaints and praise from `external.client_feedback_submitted`; publishes `customer_success.feedback_received` to Marketing, Delivery and Product | NPS 40 or better; detractors contacted within 2 business days |
| Renewals | `customer_success.renewal_due` 90 days before term end, renewal plan, uplift of CPI + 2% capped at 7% (COMPANY.md §7), `customer_success.renewal_confirmed` | Gross revenue retention 90% and logo retention 83% in FY2026 (COMPANY.md §5.1) |
| Churn prevention | At-risk detection, executive save plans, `customer_success.churn_risk_flagged`, termination-notice handling, post-mortem within 15 business days of `customer_success.client_churned` | 40% of flagged clients saved in FY2026 |
| Expansion signalling | Land-and-expand recommendations (Spark to Pilot to Build to Keep Plus, COMPANY.md §10) via `customer_success.expansion_opportunity_identified`; Sales owns the commercial conversation | Keep attached to 75% of Forge Build and Scale clients within 12 months of completion in FY2026 |
| Quarterly business reviews | QBR for every Keep client each quarter | 90% completed on time |
| References | Case-study eligibility and consent for Marketing (`customer_success.case_study_approved`) | Only green clients, NPS 9 or better, no open dispute |

Out of scope: selling new work and agreeing prices (Sales, with Finance under COMPANY.md §9.3), contract terms and disputes (Legal), delivering Keep monitoring and optimisation (Delivery), billing and collections (Finance; Customer Success supplies the relationship call at day 38), security incident response and breach notification (IT and Security, Legal; Customer Success owns client communications only).

Customer Success is part of cost of revenue: with Delivery it makes up the cost of revenue that sets gross margin (COMPANY.md §5.1, §5.4). Its budget envelope is £140k / £790k / £1,630k (people £90k / £450k / £1,240k; non-people £50k / £340k / £390k).

## 2. Org chart

```
Chief Customer Officer (head)                     Tobias Lindgren, reports to CEO; in post from Q3 FY2026
|
+-- Customer Success Manager x2 (FY2027), x6 (FY2028)          manager; named client managers (Keep Plus and above)
|
+-- Customer Success Analyst x1 (FY2027), x2 (FY2028)          analyst; health data, NPS and CSAT, QBR packs
|
+-- Renewals and Commercial Manager x1 (from Q1 FY2028)         manager; renewals, uplift, Keep attach
|
+-- Client Support Specialist x2 (FY2027, from Q2 and Q4)       consultant; Keep service desk
|     (report to the CCO until the Client Support Lead joins in Q1 FY2028)
|
+-- Client Support Lead x1 (from Q1 FY2028)                    manager; Keep service desk, 24x7 rota owner
|     +-- Client Support Specialist x3 (re-line from Q1 FY2028; third joins Q2 FY2028)
|
+-- AI agents (see section 4), each with a named human owner
```

Reporting-line notes: in FY2026 the Chief Customer Officer is the only human and joins in Q3, so the Managing Partner, Delivery (Oliver Thackeray) and the CEO hold sponsor relationships and sign off saves until then. In FY2027 the Customer Success Managers, Client Support Specialists and the Customer Success Analyst all report to the Chief Customer Officer. From Q1 FY2028 the Client Support Specialists re-line to the Client Support Lead, and renewals work moves to the Renewals and Commercial Manager.

## 3. Roles

Headcount is year-end humans and sums to COMPANY.md §6.1: customer_success = 1 / 6 / 14. Level keys and bands are from COMPANY.md §6.2.

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Customer Officer | head | Chief Executive Officer | 1 | 1 | 1 | 140,000 to 200,000 (cash; plus equity) | Owns retention, expansion and client health strategy; executive sponsor for Keep Enterprise clients and every red-band client; approves save plans and churn post-mortems; QBR sponsor for the largest clients; Board reporting on NRR, GRR and logo retention; approves case-study references; owner of the Health Score Agent until the Customer Success Analyst joins |
| Customer Success Manager | manager | Chief Customer Officer | 0 | 2 | 6 | 92,000 to 115,000 | Named client manager for up to 22 clients each (the CCO counts as the first named manager for the largest accounts); success plans, QBRs, sponsor and champion relationships, onboarding handover, escalation of delivery quality issues; owner of the Onboarding and Handover Agent and QBR Preparation Agent |
| Renewals and Commercial Manager | manager | Chief Customer Officer | 0 | 0 | 1 | 92,000 to 115,000 | Renewal calendar and plans from `customer_success.renewal_due`, uplift of CPI + 2% (cap 7%), Keep attach on Forge Build and Scale and on Compass Programmes, expansion hand-off to Sales; owner of the Renewals and Expansion Agent |
| Client Support Lead | manager | Chief Customer Officer | 0 | 0 | 1 | 92,000 to 115,000 | Owns the Keep service desk, SLA performance, P1 and P2 incident coordination with Delivery and IT and Security, the 24x7 Enterprise rota, support-day accounting; owner of the Support Triage Agent from FY2028 |
| Client Support Specialist | consultant | Chief Customer Officer (FY2027); Client Support Lead from Q1 FY2028 | 0 | 2 | 3 | 55,000 to 70,000 | First-line triage, ticket ownership against the SLA clock, client updates, hand-off to Delivery Keep pods, knowledge base upkeep, support-day drawdown records; owner of the Support Triage Agent in FY2027 |
| Customer Success Analyst | analyst | Chief Customer Officer | 0 | 1 | 2 | 38,000 to 48,000 | Health score data quality, weekly health review pack, NPS and CSAT collection and analysis, churn post-mortem data, QBR metrics, KPI reporting to Data; owner of the Health Score Agent and the Feedback and Voice-of-Client Agent |
| **Total humans** | | | **1** | **6** | **14** | | Equals COMPANY.md §6.1 row for customer_success |

### Planning salary points and cost check

Loaded cost = base x 1.28 (COMPANY.md §5.2). Planning base salaries sit inside the §6.2 bands. Average FTE reflects start quarter (Q1 start = 1.00, Q2 = 0.75, Q3 = 0.50, Q4 = 0.25 of a year).

| Role (seat) | Start | Planning base £ | Loaded £ | FY2026 avg FTE | FY2027 avg FTE | FY2028 avg FTE | FY2026 £k | FY2027 £k | FY2028 £k |
|---|---|---|---|---|---|---|---|---|---|
| Chief Customer Officer | Q3 FY2026 | 140,000 | 179,200 | 0.50 | 1.00 | 1.00 | 89.6 | 179.2 | 179.2 |
| Customer Success Manager 1 | Q1 FY2027 | 92,000 | 117,760 | 0 | 1.00 | 1.00 | 0 | 117.8 | 117.8 |
| Customer Success Manager 2 | Q3 FY2027 | 94,000 | 120,320 | 0 | 0.50 | 1.00 | 0 | 60.2 | 120.3 |
| Customer Success Manager 3 | Q1 FY2028 | 94,000 | 120,320 | 0 | 0 | 1.00 | 0 | 0 | 120.3 |
| Customer Success Manager 4 | Q2 FY2028 | 94,000 | 120,320 | 0 | 0 | 0.75 | 0 | 0 | 90.2 |
| Customer Success Manager 5 | Q3 FY2028 | 94,000 | 120,320 | 0 | 0 | 0.50 | 0 | 0 | 60.2 |
| Customer Success Manager 6 | Q4 FY2028 | 94,000 | 120,320 | 0 | 0 | 0.25 | 0 | 0 | 30.1 |
| Renewals and Commercial Manager | Q1 FY2028 | 100,000 | 128,000 | 0 | 0 | 1.00 | 0 | 0 | 128.0 |
| Client Support Lead | Q1 FY2028 | 95,000 | 121,600 | 0 | 0 | 1.00 | 0 | 0 | 121.6 |
| Client Support Specialist 1 | Q2 FY2027 | 55,000 | 70,400 | 0 | 0.75 | 1.00 | 0 | 52.8 | 70.4 |
| Client Support Specialist 2 | Q4 FY2027 | 55,000 | 70,400 | 0 | 0.25 | 1.00 | 0 | 17.6 | 70.4 |
| Client Support Specialist 3 | Q2 FY2028 | 55,000 | 70,400 | 0 | 0 | 0.75 | 0 | 0 | 52.8 |
| Customer Success Analyst 1 | Q3 FY2027 | 40,000 | 51,200 | 0 | 0.50 | 1.00 | 0 | 25.6 | 51.2 |
| Customer Success Analyst 2 | Q3 FY2028 | 40,000 | 51,200 | 0 | 0 | 0.50 | 0 | 0 | 25.6 |
| **Total people cost** | | | | **0.50** | **4.00** | **11.75** | **89.6** | **453.1** | **1,238.1** |
| COMPANY.md §5.4 people envelope | | | | | | | 90 | 450 | 1,240 |
| Delta | | | | | | | -0.4 | +3.1 | -1.9 |

All three years are within the £5k tolerance. The full build-up lives in `economics.md`. No US-based hires are planned (the +15% uplift in COMPANY.md §6.2 is not applied); US client hours are covered by a late UK shift, see risk 6.

## 4. AI agents

Agent counts sum to COMPANY.md §6.1: customer_success = 1 / 5 / 12. Every agent is registered in the agent register and has a named accountable human (COMPANY.md §9.4). In the simulation one department agent (`CustomerSuccessAgent`) implements all six roles below. All agents share these hard limits: they may draft, analyse, monitor and propose; they may not send a client communication that has not been reviewed by a human, approve or promise a service credit or concession, change a renewal price or discount (Sales and Finance, COMPANY.md §9.3), sign anything, make a final decision to accept or contest a termination, or notify a regulator or a client of a personal-data breach (COMPANY.md §9.4).

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Client Health Score Agent | Customer Success Analyst (Chief Customer Officer until Q3 FY2027; Managing Partner, Delivery before the CCO joins) | Maintains the weighted health score for every client from delivery, finance, support, security and feedback signals; publishes `customer_success.health_score_updated` and raises `customer_success.churn_risk_flagged` when a client turns red | May recompute scores and raise a flag. Cannot override a component by hand or close a risk flag; flags are closed only by the score recovering to 60 with no open dispute, or by the CCO | 1 | 1 | 2 |
| Support Triage Agent | Client Support Specialist (Client Support Lead from Q1 FY2028) | Classifies tickets from `external.client_feedback_submitted` into P1 to P4, starts the SLA clock for the client's Keep tier, creates the first-response task, raises `customer_success.support_escalated` for P1 and P2 | May classify and route. Cannot downgrade a P1 or P2, close a ticket, or promise a fix date or credit. P1 on Keep Enterprise pages the human on call at once | 0 | 1 | 2 |
| Renewals and Expansion Agent | Customer Success Manager (Renewals and Commercial Manager from Q1 FY2028) | Runs the daily renewal scan, publishes `customer_success.renewal_due` 90 days before term end with a proposed uplift, tracks `sales.renewal_proposal_sent`, publishes `customer_success.renewal_confirmed`; spots land-and-expand and Keep-attach opportunities and publishes `customer_success.expansion_opportunity_identified` | May propose an uplift inside CPI + 2% (cap 7%). Cannot send a proposal, discount, or confirm a renewal without the signed order; no expansion or renewal outreach while a dispute is open | 0 | 1 | 2 |
| Onboarding and Handover Agent | Customer Success Manager | Opens the client record from `sales.deal_won`, creates the welcome, success-plan and Keep onboarding tasks, tracks the 15-day handover target, confirms invoice contacts from `finance.billing_schedule_created` | May create tasks and draft handover packs. Cannot contact the client sponsor without human review of the draft | 0 | 1 | 2 |
| Feedback and Voice-of-Client Agent | Customer Success Analyst | Scores NPS and CSAT, themes free-text feedback, publishes `customer_success.feedback_received` to Marketing, Delivery and Product, prepares case-study candidate shortlists | May summarise and classify. Cannot reply to a complaint, offer a remedy, or approve a case study (CCO approves, with client consent and Legal sign-off) | 0 | 1 | 2 |
| QBR Preparation Agent | Customer Success Manager | Builds the quarterly business review pack for each Keep client: adoption, SLA performance, support-day drawdown, releases, value delivered, renewal date; schedules the QBR task | May draft the pack and schedule. A human Customer Success Manager reviews every pack before it reaches the client (COMPANY.md §4 quality gate applies to client-facing material) | 0 | 0 | 2 |
| **Total agents** | | | | **1** | **5** | **12** |

Agent cost is carried in non-people spend (AI compute and tooling) within the £50k / £340k / £390k envelope, using £25k / £22k / £20k per agent-year, inside the £20k to £35k range of COMPANY.md §5.2 (see `economics.md`).

## 5. Hiring plan

Time-to-hire is 45 days for humans and 5 days for agent provisioning (COMPANY.md §8). Every human hire goes through `customer_success.hire_requested` then `people.requisition_opened` then `executive.headcount_approved`, because the hires sit inside the approved §5.4 envelope but still need the CEO's headcount approval record. The capacity trigger is hard-wired into the agent: when active clients exceed 22 per named client manager, it publishes `customer_success.hire_requested` for a Customer Success Manager (SOP-CUSTOMER_SUCCESS-14). The Chief Customer Officer counts as the first named client manager.

### FY2026 (quarterly)

| Quarter | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| Q1 FY2026 | none; Keep sponsor cover by Managing Partner, Delivery (Oliver Thackeray) and the CEO | 0 | n/a | Few clients live; first Keep contracts expected after the first Forge Pilots complete |
| Q2 FY2026 | none; requisition for Chief Customer Officer opened | 0 | n/a | Series A (£10m) closes in Q2 (COMPANY.md §1); first Keep contract in negotiation |
| Q3 FY2026 | Chief Customer Officer (Tobias Lindgren) | 1 | Q3 FY2026 | First Keep contracts go live, Keep ARR heading to £1.5m (COMPANY.md §5.1); 24 clients in year need a single owner of retention |
| Q3 FY2026 | Client Health Score Agent | 1 agent | Q3 FY2026 | CCO in post as owner of the health model |
| Q4 FY2026 | none; requisition for Customer Success Manager 1 opened | 0 | n/a | Active clients above 22 per named client manager (the CCO) |

### FY2027 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2027 | Customer Success Manager 1 | 1 | Q1 FY2027 | Active clients above 22 (the CCO ceiling), 20 retained clients up for renewal conversation, US launch in Q1 (COMPANY.md §1) |
| H1 FY2027 | Client Support Specialist 1 | 1 | Q2 FY2027 | More than 8 live Keep clients or more than 30 tickets a month; first Keep Enterprise client needs a named desk owner |
| H1 FY2027 | Support Triage Agent; Onboarding and Handover Agent | 2 agents | Q2 FY2027 | Specialist and Customer Success Manager in post as owners |
| H2 FY2027 | Customer Success Manager 2 | 1 | Q3 FY2027 | Active clients above 44 (two named client managers) |
| H2 FY2027 | Customer Success Analyst 1 | 1 | Q3 FY2027 | Health review and NPS programme outgrow the CCO; owner for the Health Score Agent |
| H2 FY2027 | Renewals and Expansion Agent | 1 agent | Q3 FY2027 | Keep ARR above £3m and first 12-month renewals approaching |
| H2 FY2027 | Client Support Specialist 2 | 1 | Q4 FY2027 | Enterprise 24x7 rota needs at least two named people; US hours (13:00 to 23:00 UK) covered by a late shift |
| H2 FY2027 | Feedback and Voice-of-Client Agent | 1 agent | Q4 FY2027 | Analyst in post as owner |

### FY2028 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2028 | Customer Success Manager 3 | 1 | Q1 FY2028 | Active clients above 66 (three named client managers) |
| H1 FY2028 | Renewals and Commercial Manager | 1 | Q1 FY2028 | More than 30 Keep renewals in the 12-month calendar and Keep ARR on a path to £17.0m (COMPANY.md §5.1) |
| H1 FY2028 | Client Support Lead | 1 | Q1 FY2028 | Support desk of three people plus Enterprise 24x7 rota exceeds CCO span |
| H1 FY2028 | Customer Success Manager 4 | 1 | Q2 FY2028 | Active clients above 88 |
| H1 FY2028 | Client Support Specialist 3 | 1 | Q2 FY2028 | Monthly tickets above 150 or first-response SLA below 95% for two months |
| H1 FY2028 | Health Score Agent (2nd); Support Triage Agent (2nd); QBR Preparation Agent (1st) | 3 agents | Q1 to Q2 FY2028 | Client count above 65; US ledger and tickets live; QBR load above 60 packs a quarter |
| H2 FY2028 | Customer Success Manager 5 | 1 | Q3 FY2028 | Active clients above 110 |
| H2 FY2028 | Customer Success Analyst 2 | 1 | Q3 FY2028 | NPS and CSAT volume above one analyst; second health model owner for US clients |
| H2 FY2028 | Renewals and Expansion Agent (2nd); Onboarding and Handover Agent (2nd); QBR Preparation Agent (2nd) | 3 agents | Q3 FY2028 | Renewal volume and onboarding load |
| H2 FY2028 | Customer Success Manager 6 | 1 | Q4 FY2028 | Active clients above 132 |
| H2 FY2028 | Feedback and Voice-of-Client Agent (2nd) | 1 agent | Q4 FY2028 | Second analyst in post |

Year-end check: FY2026 = CCO = 1; FY2027 adds Customer Success Managers 1 and 2, Client Support Specialists 1 and 2, Customer Success Analyst 1 = 6; FY2028 adds Customer Success Managers 3 to 6, Renewals and Commercial Manager, Client Support Lead, Client Support Specialist 3, Customer Success Analyst 2 = 14. Agents: 1 / 5 / 12 (FY2028 adds Health 2nd, Triage 2nd, Renewals 2nd, Onboarding 2nd, Feedback 2nd, QBR x2 = 7). Attrition (14% falling to 11%, COMPANY.md §8) is handled as backfill inside the same requisition and is not additive.

## 6. Interfaces

Topics are those in `core/topics.py` and CONVENTIONS.md §7.

### Customer Success publishes (prefix `customer_success.`)

| Topic | Delivered to | Used for |
|---|---|---|
| `customer_success.health_score_updated` | sales, delivery, data | Band change or move of 5 points or more; baseline at onboarding |
| `customer_success.churn_risk_flagged` | sales, delivery, executive | Client turned red, dispute, termination notice, confirmed breach |
| `customer_success.client_churned` | finance, sales, executive, data | Non-renewal or termination became final; triggers the post-mortem |
| `customer_success.renewal_due` | sales, finance, legal | Keep term ends in 90 days; carries proposed uplift |
| `customer_success.renewal_confirmed` | finance, legal, sales, delivery, data | Keep renewed; carries new amount and NRR delta |
| `customer_success.expansion_opportunity_identified` | sales | Keep attach, Spark to Pilot to Build path, client-voiced signal |
| `customer_success.feedback_received` | marketing, delivery, product | Scored feedback with theme and category |
| `customer_success.support_escalated` | delivery, product | P1 and P2 tickets needing engineering or delivery action |
| `customer_success.case_study_approved` | marketing | Client and CCO approved a named case study |

Generic: `customer_success.budget_submitted` (to finance) and `customer_success.hire_requested` (to people).

### Customer Success subscribes to (supply and trigger)

| Group | Topics | Why Customer Success needs them |
|---|---|---|
| Onboarding | `sales.deal_won`, `legal.contract_signed`, `finance.billing_schedule_created`, `delivery.engagement_kickoff` | Open the client record, record the Keep contract and term dates, confirm invoice contacts, hand over at kickoff |
| Delivery health | `delivery.milestone_reached`, `delivery.quality_issue_raised`, `delivery.engagement_completed` | Delivery and engagement components of the health score; closeout, NPS survey and Keep attach |
| Commercial health | `finance.invoice_issued`, `finance.payment_received`, `finance.invoice_overdue`, `legal.client_dispute_raised` | Commercial component of the health score; day-38 relationship call; expansion and renewal holds during disputes |
| Client voice | `external.client_feedback_submitted`, `external.client_notice_of_termination` | Tickets, NPS, CSAT, complaints, praise and termination notices from the outside world |
| Renewals | `sales.renewal_proposal_sent` | Track the proposal and the client decision window |
| Security and releases | `it_security.incident_detected`, `it_security.data_breach_confirmed`, `it_security.incident_resolved`, `product.release_shipped` | Client communications on incidents; change notices and QBR content for releases |
| Marketing | `marketing.case_study_requested` | Reference eligibility and consent |
| Planning | `finance.budget_cycle_opened`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated`, `executive.crisis_declared` | Budget submission, KPI mapping, playbook review, crisis outreach |

### Dependencies on other departments (data Customer Success needs, by key)

| From | Needed | Body keys |
|---|---|---|
| Sales | Won deals and renewal proposals, client decision | `deal_id`, `client_id`, `tier`, `amount_gbp`, `client_decision` |
| Legal | Contract term, Keep tier, disputes | `contract_id`, `start_day`, `term_months`, `severity` |
| Delivery | Kickoff, milestones, quality issues, completion | `engagement_id`, `milestone`, `severity`, `tier` |
| Finance | Billing schedule, invoices, payments, overdue days | `invoice_id`, `amount_gbp`, `days_overdue` |
| IT and Security | Incident and breach scope | `incident_id`, `affected_client_ids`, `severity` |
| Product | Release notes and breaking-change flag | `release_id`, `breaking_change` |
| Marketing | Reference requests | `request_id`, `client_consent` |

## 7. Risks and dependencies

| # | Risk | Likelihood / impact | Mitigation and owner |
|---|---|---|---|
| 1 | Key-person dependency: one human (the CCO) from Q3 FY2026 to Q1 FY2027, with 24 clients in year and the first Keep contracts | High / High | Managing Partner, Delivery and the CEO hold the top sponsor relationships until the CCO starts; Health Score Agent flags every red client; hire request fires at 22 clients per named manager (Chief Customer Officer) |
| 2 | Keep SLA breach on a P1 for an Enterprise client (24x7 cover, COMPANY.md §3.3) while the desk has two people | Medium / High | Late-shift rota, pager to Delivery Keep pod lead, external out-of-hours call-out partner in non-people budget (economics.md); P1 reviewed by the CCO within one business day (Client Support Lead from FY2028) |
| 3 | Delivery quality issues erode health before Customer Success sees them | Medium / High | `delivery.quality_issue_raised` is a health trigger; recovery plan task within 2 business days; fortnightly Delivery and Customer Success review of amber and red clients (Chief Customer Officer) |
| 4 | Client concentration above 15% of revenue (COMPANY.md §8) makes one churn material | Medium / High | Top-client share reported quarterly with Finance; executive sponsor named for every client above £500k (Chief Customer Officer) |
| 5 | Security incident or data breach at a client: Lumenhall is a processor and must tell the client controller without undue delay so the client can meet its 72-hour ICO duty | Medium / Critical | Customer Success sends holding statements and named-contact calls (SOP-CUSTOMER_SUCCESS-09); content and timing agreed with General Counsel and CISO; agents never notify (Chief Customer Officer) |
| 6 | US launch (Q1 FY2027) needs support hours of 13:00 to 23:00 UK time | Medium / Medium | Late UK shift by Client Support Specialists; US-based support hire deferred beyond FY2028; trigger to revisit is US share above 25% of tickets (Client Support Lead) |
| 7 | Over-reliance on health score as a proxy: a green score can hide a champion who has left | Medium / Medium | Engagement component decays 3 points after 45 days without sponsor contact; QBR attendance tracked; champion-change is a manual risk flag (Customer Success Manager) |
| 8 | Renewal uplift (CPI + 2%) provokes price-driven churn in a high-inflation year | Medium / Medium | Uplift capped at 7% (COMPANY.md §7); value summary in every renewal proposal; price is a saveable churn reason with a 40% FY2026 save target (Renewals and Commercial Manager) |
| 9 | Dependency on clean signals from Finance, Delivery and Legal: a missed `legal.contract_signed` leaves a Keep client without a renewal clock | Medium / High | Daily reconciliation of live Keep contracts to the renewal clock; term-end dates cross-checked at each QBR (Customer Success Analyst) |

Key dependencies: Sales for the renewal proposals and expansion conversations; Delivery for Keep monitoring and issue resolution; Finance for billing accuracy and collections; Legal for disputes and contract terms; People for approved requisitions.

## 8. Sources

- COMPANY.md §1 (identity, funding, US launch timing)
- COMPANY.md §2 (land and expand; Keep attach targets)
- COMPANY.md §3.1 to §3.3 (prices and Keep tiers; support days; 24x7 cover)
- COMPANY.md §4 (quality gate)
- COMPANY.md §5.1 (retention, margin, cost of revenue, Keep ARR), §5.2 (loaded cost, agent cost range), §5.4 (customer_success envelope: people £90k / £450k / £1,240k; non-people £50k / £340k / £390k; total £140k / £790k / £1,630k)
- COMPANY.md §6.1 and §6.2 (headcount rows and salary bands)
- COMPANY.md §7 (Keep billing, CPI + 2% uplift capped at 7%, collections ladder)
- COMPANY.md §8 (attrition, time-to-hire, concentration policy)
- COMPANY.md §9.2 to §9.4 (head of department, delegations, AI agent governance)
- COMPANY.md §10 (sample client and land-and-expand journey)
