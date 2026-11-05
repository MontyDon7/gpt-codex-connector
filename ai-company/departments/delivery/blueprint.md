# Delivery Department Blueprint

## 1. Mission and scope

The `delivery` department is Lumenhall's client delivery and consulting engine. It turns signed contracts into accepted deliverables across all three service lines (Compass advisory, Forge AI implementation, Keep managed-ops hand-over; COMPANY.md §3), using human consultants working alongside AI agents ("digital colleagues") under named human owners (COMPANY.md §2, §9.4). Its accountable head is Oliver Thackeray, Managing Partner, Delivery (COMPANY.md §9.2), reporting to the CEO.

**In scope**

- Scoping: converting a qualified lead or proposal request into a fixed-fee scope, team shape, assumptions and risks (`delivery.scoping_completed`).
- Staffing: matching named humans and agents to engagements, publishing capacity (`delivery.staffing_requested`, `delivery.capacity_forecast_updated`) and requesting hires (`delivery.hire_requested`).
- Engagement execution: kickoff, milestone plans, milestone acceptance and the 30/40/30 billing triggers (COMPANY.md §7), completion and hand-over to Keep (`delivery.engagement_kickoff`, `delivery.milestone_reached`, `delivery.engagement_completed`).
- Scope control: change requests, change orders at rate card (COMPANY.md §3.5), signed before work starts (`delivery.scope_change_requested`).
- Quality: the human Manager-or-above review gate on every client deliverable (COMPANY.md §4), defect tracking and post-engagement review (`delivery.quality_issue_raised`).
- Delivery-side planning input to the annual budget cycle (`delivery.budget_submitted`).

**Out of scope** (owned elsewhere): pricing policy and discounts (sales, finance), contract drafting and liability terms (legal), invoicing and collections (finance), renewals and client health after hand-over (customer_success), agent platform and model governance (data, product, it_security).

**Cost-of-revenue role.** Delivery plus customer_success is cost of revenue (COMPANY.md §5.1). Delivery's budget envelope is £2,980k / £7,400k / £15,000k for FY2026 to FY2028 (people £1,130k / £3,000k / £8,800k; COMPANY.md §5.4). Headcount is 14 / 46 / 104 humans and 6 / 22 / 52 AI agents at year-end (COMPANY.md §6.1). Delivery is the largest department: 37% of humans and 27% of agents in FY2026, 45% of humans and 35% of agents in FY2028.

**Operating principles**

1. Fixed-fee discipline: margin is made or lost in scoping and change control, so scope assumptions are written down and every out-of-scope request is priced at the rate card.
2. Human accountability: agents draft, analyse, monitor and propose; they never release a deliverable, sign a change order or make a staffing decision on their own (COMPANY.md §9.4).
3. Pyramid and utilisation targets: 70% blended billable utilisation (Analyst/Consultant 80%, Manager 65%, Principal 50%, Partner 35%) with the staffing pyramid in section 3 (COMPANY.md §4).
4. Quality before speed: no deliverable leaves without a Manager-or-above sign-off recorded against the engagement.

## 2. Org chart

Counts in brackets are year-end headcount Y1 / Y2 / Y3 (humans). Agents are in section 4 and attach to the human owners shown there.

```
Managing Partner, Delivery  [1 / 1 / 1]  (Oliver Thackeray; reports to Chief Executive Officer)
|
+-- Partner, Compass Advisory  [1 / 1 / 2]
|     +-- Principal, Engagement Lead  [1 / 2 / 6]   (shared pool; each Principal reports to the Partner of the line they lead)
|           +-- Engagement Manager  [2 / 6 / 14]
|           |     +-- Senior Consultant, Strategy and Operating Model  [2 / 6 / 14]
|           |     |     +-- Consultant  [1 / 6 / 14]
|           |     |     +-- Analyst  [1 / 5 / 11]  (analyst pool, supervised by Senior Consultants)
|           |     +-- Senior AI Solutions Engineer  [2 / 8 / 17]
|           |           +-- AI Implementation Consultant  [1 / 4 / 10]
|           +-- AI Delivery Manager (Agent Operations)  [1 / 2 / 4]
|
+-- Partner, AI Implementation (Forge)  [1 / 1 / 2]
|     +-- Principal, AI Delivery Architect  [0 / 1 / 3]
|
+-- Director, Delivery Quality and Methods  [0 / 1 / 1]
|     +-- Delivery Quality Specialist  [0 / 1 / 2]
|
+-- Resourcing and Capacity Manager  [0 / 1 / 2]
|
+-- PMO and Commercial Manager (scope and change)  [0 / 0 / 1]
```

Reporting rules:

- Engagement Managers report to the Principal Engagement Lead for their engagement portfolio; Senior Consultants and below report to the Engagement Manager on their current engagement, with a permanent line to a Senior Consultant, Manager or Principal "career counsellor" owned by People.
- Senior AI Solutions Engineers and AI Implementation Consultants report to Engagement Managers on Forge work, and to the Principal, AI Delivery Architect on technical standards.
- The AI Delivery Manager (Agent Operations) runs the delivery agent fleet and the hand-over of live agents into Keep, reporting to the Principal Engagement Lead for Forge engagements.
- Partner, Compass Advisory and Partner, AI Implementation (Forge) report to the Managing Partner, Delivery. Principals report to the Partner of their line.
- Director, Delivery Quality and Methods, Resourcing and Capacity Manager and PMO and Commercial Manager report directly to the Managing Partner and are independent of engagement P&L, so review and capacity calls are not made by the people who own the margin.

## 3. Roles

Y1/Y2/Y3 are year-end human headcount. Column sums equal COMPANY.md §6.1 (delivery: 14 / 46 / 104). Level keys and bands are from COMPANY.md §6.2 (London; US hires +15%).

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Managing Partner, Delivery | head | Chief Executive Officer | 1 | 1 | 1 | £140,000 to £200,000 (cash; plus equity) | Owns delivery P&L, gross-margin contribution (COMPANY.md §5.1), department budget, partner bench, client escalations, board-level delivery reporting; approves staffing exceptions and non-standard scope. |
| Partner, Compass Advisory | partner | Managing Partner, Delivery | 1 | 1 | 2 | £160,000 to £220,000 | Senior client relationship and quality authority on Compass Spark, Sprint and Programme; signs off scoping for Compass deals; sponsor-level executive engagement; target 35% billable. |
| Partner, AI Implementation (Forge) | partner | Managing Partner, Delivery | 1 | 1 | 2 | £160,000 to £220,000 | Same remit for Forge Pilot, Build and Scale; owns AI risk position on client builds with Legal and Product; approves any Forge scope above £260k. |
| Principal, Engagement Lead | principal | Partner of the line led | 1 | 2 | 6 | £120,000 to £155,000 | Accountable for a portfolio of 3 to 5 live engagements; part-time lead on Forge Build and Compass Programme teams (COMPANY.md §4); scope-change approver up to 15% of fee; target 50% billable. |
| Principal, AI Delivery Architect | principal | Partner, AI Implementation (Forge) | 0 | 1 | 3 | £120,000 to £155,000 | Technical design authority for agent builds and client-system integrations; reference architectures, security and data-flow reviews with it_security; owns Forge technical risk. |
| Director, Delivery Quality and Methods | principal | Managing Partner, Delivery | 0 | 1 | 1 | £120,000 to £155,000 | Owns the quality gate, methods library, post-engagement reviews and client-quality KPIs; chairs monthly quality board; independent of engagement P&L. |
| Engagement Manager | manager | Principal, Engagement Lead | 2 | 6 | 14 | £92,000 to £115,000 | Day-to-day engagement lead; plan, RAID log, milestone readiness, deliverable QA (Manager-or-above gate); staffing humans and agents; first-line scope-change handling; target 65% billable. |
| AI Delivery Manager (Agent Operations) | manager | Principal, Engagement Lead | 1 | 2 | 4 | £92,000 to £115,000 | Runs the delivery agent fleet (work queues, prompts, evaluation sets), agent-day utilisation, agent incident handling and hand-over of live agents to Keep with Customer Success. |
| Resourcing and Capacity Manager | manager | Managing Partner, Delivery | 0 | 1 | 2 | £92,000 to £115,000 | Weekly capacity forecast, staffing matching, bench and utilisation management, hiring triggers into People; owns `delivery.capacity_forecast_updated`. |
| PMO and Commercial Manager (scope and change) | manager | Managing Partner, Delivery | 0 | 0 | 1 | £92,000 to £115,000 | Change-order desk, fixed-fee margin tracking, milestone-billing evidence packs for finance, delivery reporting pack; takes over change administration once live engagements exceed 40. |
| Senior Consultant, Strategy and Operating Model | senior_consultant | Engagement Manager | 2 | 6 | 14 | £72,000 to £90,000 | Leads workstreams on Compass work (diagnostics, target operating model, business case); supervises Consultants and Analysts; reviews agent drafts before they reach the Manager gate. |
| Senior AI Solutions Engineer | senior_consultant | Engagement Manager | 2 | 8 | 17 | £72,000 to £90,000 | Designs and builds agents and workflows on Forge engagements, integrations with client systems, evaluation harnesses, runbooks; owns build quality for assigned agents. |
| Consultant | consultant | Senior Consultant, Strategy and Operating Model | 1 | 6 | 14 | £55,000 to £70,000 | Analysis, workshop delivery, process mapping, benchmarking and drafting on Compass work; target 80% billable. |
| AI Implementation Consultant | consultant | Senior AI Solutions Engineer | 1 | 4 | 10 | £55,000 to £70,000 | Configures agents, prompt and test suites, data preparation, user training and hypercare on Forge work; target 80% billable. |
| Delivery Quality Specialist | consultant | Director, Delivery Quality and Methods | 0 | 1 | 2 | £55,000 to £70,000 | Second-line review sampling, defect triage, client-readiness checklists, audit trail of agent output used in deliverables (COMPANY.md §9.4). |
| Analyst | analyst | Senior Consultant, Strategy and Operating Model | 1 | 5 | 11 | £38,000 to £48,000 | Data collection and cleaning, desk research, model building, slide production support; rotates across Compass and Forge; target 80% billable. |
| **Total humans** | | | **14** | **46** | **104** | | Equals COMPANY.md §6.1 delivery row. |

### 3.1 Level mix versus the staffing pyramid

Target pyramid (COMPANY.md §4): Partner 5%, Principal 10%, Manager 20%, Senior Consultant 30%, Consultant 25%, Analyst 10%. The Managing Partner (head level) is counted with Partners.

| Level | Y1 | Y1 % | Y2 | Y2 % | Y3 | Y3 % | Pyramid target |
|---|---|---|---|---|---|---|---|
| Partner (incl. Managing Partner) | 3 | 21% | 3 | 7% | 5 | 5% | 5% |
| Principal | 1 | 7% | 4 | 9% | 10 | 10% | 10% |
| Manager | 3 | 21% | 9 | 20% | 21 | 20% | 20% |
| Senior Consultant | 4 | 29% | 14 | 30% | 31 | 30% | 30% |
| Consultant | 2 | 14% | 11 | 24% | 26 | 25% | 25% |
| Analyst | 1 | 7% | 5 | 11% | 11 | 11% | 10% |
| **Total** | **14** | | **46** | | **104** | | |

FY2026 is deliberately top-heavy (a founding bench of senior people carries the first 24 clients while the pyramid is built); by FY2027 the shape is within 3 points of target at every level.

### 3.2 Implied cost per head (for reconciliation with economics.md)

Loaded cost = base x 1.28 (COMPANY.md §5.2). Average headcount in year is estimated from the hiring phasing in section 5.

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Opening headcount (1 January) | 0 (Day 0 is 2026-01-05) | 14 | 46 |
| Year-end headcount | 14 | 46 | 104 |
| Approx. average FTE in year | about 9 | about 29 | about 76 |
| People budget (COMPANY.md §5.4) | £1,130k | £3,000k | £8,800k |
| Implied loaded cost per average FTE | about £125k | about £103k | about £116k |

FY2028 sits above FY2027 because the cumulative level mix is more senior in absolute terms, and because 12 of the 58 FY2028 hires are New York based at base +15% (US launch Q1 FY2027, COMPANY.md §1, §6.2). The detailed role x average headcount x loaded cost build-up is owned by `economics.md`.

## 4. AI agents

Agent counts are year-end and equal COMPANY.md §6.1 (delivery: 6 / 22 / 52). All agents are registered in the agent register (Data and IT Security) with a named accountable human owner (COMPANY.md §9.4). Common limits for all delivery agents: no signing of contracts or change orders, no release of any client deliverable without Manager-or-above QA, no payment approval above £10,000, no final hiring or termination decisions, no regulator notifications, least-privilege access to client data under the data-processing agreement, and logging of every output used in a client deliverable. The internal cost-recovery rate is the AI agent-day at £350 on the rate card (COMPANY.md §3.5); fully loaded agent cost is £20k to £35k per agent-year (COMPANY.md §5.2).

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Research and Insight Agent | Senior Consultant, Strategy and Operating Model (per engagement); fleet owner: AI Delivery Manager (Agent Operations) | Desk research, market and sector scans, client document digests, interview synthesis for Compass diagnostics | Read-only on client data room; outputs are drafts with citations; cannot contact client staff or third parties | 1 | 4 | 9 |
| Analytics and Modelling Agent | Senior Consultant, Strategy and Operating Model | Data cleaning, process-mining style analysis, business-case and benchmark models, sensitivity runs | Works on a client sandbox copy; model outputs require human reviewer sign-off before use in any deliverable; no write access to client production systems | 1 | 3 | 8 |
| Drafting and Deliverables Agent | Engagement Manager | First drafts of decks, reports, SOWs, status reports, meeting notes and change-request narratives | Drafts only; every client-facing document passes a human Manager-or-above gate; cannot send to clients | 1 | 4 | 10 |
| QA Pre-Review Agent | Director, Delivery Quality and Methods | Automated pre-checks of deliverables: numbers tie to model, template and house-style compliance, consistency with signed scope, citation checks | Advisory only: can block submission to the review queue but cannot approve or release; findings logged to the engagement quality record | 1 | 3 | 7 |
| Engagement Monitoring Agent | Engagement Manager (portfolio view: Principal, Engagement Lead) | Watches plans, milestone dates, burn versus fee, RAID items and scope-creep signals; drafts weekly status; proposes `delivery.scope_change_requested` and escalations | Proposes and alerts; cannot change plans, dates or billing triggers; escalation thresholds set by the Principal (e.g. burn >85% of budgeted days before 70% of milestones) | 1 | 3 | 6 |
| Capacity Forecaster Agent | Resourcing and Capacity Manager (Y1: Managing Partner, Delivery) | Weekly supply and demand model from pipeline and live engagements; utilisation by level; early hiring-trigger flags | Proposes forecasts and staffing options only; assignments and `delivery.hire_requested` are confirmed by a human; cannot commit people to a client | 1 | 2 | 4 |
| Scoping Agent | Principal, Engagement Lead | Turns proposal requests and qualified leads into draft scope, assumptions, team shape and effort from the tier catalogue and historical actuals | Draft scope only; Partner signs off before `delivery.scoping_completed` is released; cannot set price or discounts | 0 | 1 | 3 |
| Integration Build Agent | Senior AI Solutions Engineer (per engagement); fleet owner: Principal, AI Delivery Architect | Generates and tests connectors, workflow code, evaluation sets and runbooks for client agent builds | Sandbox and client non-production only; production deployment requires human change approval and, for material client-facing agent changes, an AI risk review (COMPANY.md §9.4) | 0 | 2 | 5 |
| **Total agents** | | | | **6** | **22** | **52** |

Leverage check: agents per delivery human are 0.43 (FY2026), 0.48 (FY2027) and 0.50 (FY2028) on year-end counts, in line with the 0.5 to 0.65 band in COMPANY.md §2. Agent provisioning time is 5 days (COMPANY.md §8); new agents enter the register before first use.

## 5. Hiring plan

Time-to-hire is 45 days for humans (COMPANY.md §8), so every requisition (`delivery.hire_requested`, REQ-nnnn) must be raised at least one quarter before the start quarter below. Attrition of 14% (FY2026) falling to 11% (FY2028) creates backfill hires on top of the net adds shown; backfills are not counted in headcount and do not need a new headcount approval. Hires within the approved plan do not need `executive.headcount_approved`; anything above plan does (COMPANY.md §9.3).

### 5.1 FY2026 (quarterly), 14 net hires

| Quarter | Role | Count | Trigger |
|---|---|---|---|
| Q1 | Managing Partner, Delivery | 1 | Founding team; Day 0 = 2026-01-05 |
| Q1 | Partner, Compass Advisory | 1 | Founding team; first Compass Spark / Sprint pipeline |
| Q1 | Principal, Engagement Lead | 1 | Founding team; needed before the first engagement kickoff |
| Q1 | Engagement Manager | 1 | First signed engagement |
| Q1 | Senior Consultant, Strategy and Operating Model | 1 | First Compass engagement |
| Q2 | Partner, AI Implementation (Forge) | 1 | Series A closes Q2 (COMPANY.md §1); first Forge Pilot proposals |
| Q2 | Engagement Manager | 1 | 3 or more concurrent live engagements |
| Q2 | Senior AI Solutions Engineer | 1 | First Forge Pilot signed |
| Q3 | AI Delivery Manager (Agent Operations) | 1 | Second Forge engagement live; agent fleet above 4 |
| Q3 | Senior Consultant, Strategy and Operating Model | 1 | Forecast utilisation of existing Senior Consultants above 85% for 4 weeks |
| Q3 | Consultant | 1 | Same trigger as above; pyramid base |
| Q3 | AI Implementation Consultant | 1 | Forge Build pipeline (first Build proposal) |
| Q4 | Senior AI Solutions Engineer | 1 | Forge Build kickoff expected Q4 or Q1 FY2027 |
| Q4 | Analyst | 1 | Pyramid base; reduce Senior Consultant time on data preparation |
| | **Total FY2026** | **14** | |

Agent provisioning FY2026 (humans accountable in section 4): 6 agents, one of each of the first six agent types, provisioned within 5 days of the owning human starting.

### 5.2 FY2027 (half-year), 32 net hires

| Half | Role | Count | Trigger |
|---|---|---|---|
| H1 FY2027 | Principal, Engagement Lead | 1 | Live engagements per Principal above 5 |
| H1 FY2027 | Principal, AI Delivery Architect | 1 | More than 3 concurrent Forge builds; need a design authority |
| H1 FY2027 | Engagement Manager | 2 | Live engagements per Manager above 2.5 |
| H1 FY2027 | Resourcing and Capacity Manager | 1 | More than 20 delivery humans; spreadsheet staffing no longer controllable |
| H1 FY2027 | Senior Consultant, Strategy and Operating Model | 2 | Compass Sprint and Programme demand (35% revenue mix, COMPANY.md §5.1) |
| H1 FY2027 | Senior AI Solutions Engineer | 3 | Forge at 40% of revenue; capacity forecast flag for Q2 builds |
| H1 FY2027 | Consultant | 2 | Pyramid rebalancing toward target 25% |
| H1 FY2027 | AI Implementation Consultant | 1 | Forge Build demand |
| H1 FY2027 | Analyst | 2 | Pyramid rebalancing |
| | **Subtotal H1** | **15** | |
| H2 FY2027 | Director, Delivery Quality and Methods | 1 | More than 25 clients billed in year; independent quality function required before SOC 2 Type II audit window |
| H2 FY2027 | Engagement Manager | 2 | US launch (New York) and Forge Scale pipeline |
| H2 FY2027 | AI Delivery Manager (Agent Operations) | 1 | Delivery agent fleet above 15 |
| H2 FY2027 | Senior Consultant, Strategy and Operating Model | 2 | Utilisation trigger as above |
| H2 FY2027 | Senior AI Solutions Engineer | 3 | Keep hand-overs from Forge Build engagements |
| H2 FY2027 | Consultant | 3 | Pyramid base |
| H2 FY2027 | AI Implementation Consultant | 2 | Forge Build demand |
| H2 FY2027 | Delivery Quality Specialist | 1 | Follows Director hire |
| H2 FY2027 | Analyst | 2 | Pyramid base |
| | **Subtotal H2** | **17** | |
| | **Total FY2027** | **32** | Year-end 46 humans |

Agent provisioning FY2027: net +16 agents (6 to 22), including the first Scoping Agent (1) and Integration Build Agent (2) in H1.

### 5.3 FY2028 (half-year), 58 net hires

| Half | Role | Count | Trigger |
|---|---|---|---|
| H1 FY2028 | Partner, Compass Advisory | 1 | Compass above £12m revenue run-rate (COMPANY.md §5.1: £12.94m for FY2028) |
| H1 FY2028 | Principal, Engagement Lead | 2 | Portfolio per Principal above 5 live engagements |
| H1 FY2028 | Principal, AI Delivery Architect | 1 | More than 8 concurrent Forge builds |
| H1 FY2028 | Engagement Manager | 4 | Live engagements per Manager above 2.5 |
| H1 FY2028 | AI Delivery Manager (Agent Operations) | 1 | Delivery agent fleet above 35 |
| H1 FY2028 | Resourcing and Capacity Manager | 1 | Second capacity manager for the US pool |
| H1 FY2028 | Senior Consultant, Strategy and Operating Model | 4 | Utilisation trigger |
| H1 FY2028 | Senior AI Solutions Engineer | 5 | Forge Scale rollouts |
| H1 FY2028 | Consultant | 4 | Pyramid base |
| H1 FY2028 | AI Implementation Consultant | 3 | Forge demand |
| H1 FY2028 | Delivery Quality Specialist | 1 | More than 60 live engagements per year |
| H1 FY2028 | Analyst | 3 | Pyramid base |
| | **Subtotal H1** | **30** | |
| H2 FY2028 | Partner, AI Implementation (Forge) | 1 | Forge above £18m revenue run-rate (COMPANY.md §5.1: £18.48m for FY2028) |
| H2 FY2028 | Principal, Engagement Lead | 2 | Portfolio trigger |
| H2 FY2028 | Principal, AI Delivery Architect | 1 | Forge Scale design authority |
| H2 FY2028 | Engagement Manager | 4 | Live engagements trigger |
| H2 FY2028 | AI Delivery Manager (Agent Operations) | 1 | Agent fleet near 52 |
| H2 FY2028 | PMO and Commercial Manager (scope and change) | 1 | More than 40 live engagements; centralise change-order desk |
| H2 FY2028 | Senior Consultant, Strategy and Operating Model | 4 | Utilisation trigger |
| H2 FY2028 | Senior AI Solutions Engineer | 4 | Forge Scale and Keep Enterprise embedded teams |
| H2 FY2028 | Consultant | 4 | Pyramid base |
| H2 FY2028 | AI Implementation Consultant | 3 | Forge demand |
| H2 FY2028 | Analyst | 3 | Pyramid base |
| | **Subtotal H2** | **28** | |
| | **Total FY2028** | **58** | Year-end 104 humans; about 12 of the hires New York based |

Agent provisioning FY2028: net +30 agents (22 to 52), in line with the planned 15% annual fall in unit model and compute cost (COMPANY.md §8.4).

### 5.4 Hiring controls

- A requisition is raised through `delivery.hire_requested` with `role`, `level`, `count`, `start_quarter`, `trigger` and `engagement_ids` that justify it; the Resourcing and Capacity Manager (before FY2027 H1, the Managing Partner) owns the trigger test.
- Triggers are utilisation-based: forecast utilisation above target for 4 consecutive weeks at a level, or committed pipeline weighted at 50% or more exceeding available capacity within 90 days.
- Associates and subcontractors (COMPANY.md §5.2) cover peaks above plan, capped so that no engagement relies on them for more than 30% of days; they are not counted in headcount.

## 6. Interfaces

Topic names are as published in the topic map (`core/topics.py`; CONVENTIONS.md section 7).

### 6.1 Topics delivery publishes

| Topic | When | Main consumers |
|---|---|---|
| `delivery.scoping_completed` | Partner-approved scope with team shape, effort, assumptions and risks | sales, finance, legal |
| `delivery.staffing_requested` | Engagement needs named humans or agents beyond the current bench | people, operations, data |
| `delivery.capacity_forecast_updated` | Weekly forecast of supply, demand and utilisation | sales, finance, people, executive |
| `delivery.hire_requested` | Utilisation or pipeline trigger breached | people, finance, executive |
| `delivery.engagement_kickoff` | Client kickoff held, plan baselined | finance, customer_success, it_security |
| `delivery.milestone_reached` | Milestone accepted by the client; this is the 40% mid-point or 30% acceptance trigger for invoicing (COMPANY.md §7) | finance, customer_success |
| `delivery.scope_change_requested` | Client or team requests work outside the signed scope | sales, finance, legal |
| `delivery.quality_issue_raised` | Defect, miss or client complaint on a deliverable | customer_success, legal, product, data |
| `delivery.engagement_completed` | Final acceptance; hand-over to Keep or close-out | finance, customer_success, sales, data |
| `delivery.budget_submitted` | Annual budget cycle response (people, agents, subcontractors, tooling) | finance, executive |

### 6.2 Topics delivery subscribes to (26)

| Source dept | Topics | How delivery uses them |
|---|---|---|
| sales | `sales.lead_qualified`, `sales.proposal_requested`, `sales.deal_won` | Early capacity check, scoping, staffing and engagement set-up on win |
| legal | `legal.contract_signed`, `legal.client_dispute_raised` | Contract in force is the gate for kickoff and change orders; disputes trigger engagement review and hold on non-essential work |
| finance | `finance.billing_schedule_created`, `finance.budget_cycle_opened` | Align milestone plan to the 30/40/30 billing schedule; open delivery budget submission |
| executive | `executive.strategy_updated`, `executive.okrs_set`, `executive.budget_approved`, `executive.crisis_declared` | Re-prioritise capacity, set delivery OKRs, lock approved headcount and budget, switch to crisis staffing |
| customer_success | `customer_success.feedback_received`, `customer_success.health_score_updated`, `customer_success.churn_risk_flagged`, `customer_success.renewal_confirmed`, `customer_success.support_escalated` | Quality learning, protect at-risk accounts with staffing, link Forge hand-over to Keep, resource escalations |
| people | `people.new_hire_started`, `people.engagement_survey_completed` | Onboard and allocate new starters, act on burnout and utilisation risk |
| product | `product.agent_capability_added`, `product.release_shipped`, `product.roadmap_published` | Adopt new agent capabilities in delivery, plan Forge components, update methods |
| data | `data.agent_quality_report_published`, `data.benchmark_ready`, `data.forecast_updated` | Agent quality actions, benchmarks in Compass work, demand forecast into capacity model |
| it_security | `it_security.incident_detected` | Contain and pause affected engagements and agents; client notification support |
| external | `external.client_scope_request` | Intake of a client-originated request; classify as in-scope, change order or new proposal |

### 6.3 Services delivery depends on

- **sales**: qualified leads, win notifications, proposal timing; and a feedback loop of delivery actuals on effort per tier so scoping stays calibrated.
- **legal**: contract terms, change-order templates, AI risk reviews (`legal.ai_risk_review_completed`) for material client-facing agent changes, DPAs and sub-processor approvals.
- **finance**: milestone invoicing (within 2 business days of acceptance, COMPANY.md §7), rate card and margin reporting.
- **people**: recruiting, onboarding, performance and capability frameworks; New York payroll from FY2027.
- **product**: the delivery agent platform, reusable Forge components and the release calendar.
- **data**: agent quality reports, benchmarks, forecasts and the agent register (with it_security).
- **it_security**: access, client-data handling, incident response, ISO 27001 and SOC 2 controls over delivery environments.

### 6.4 Services delivery provides

- **customer_success**: a clean hand-over pack (runbooks, agent inventory, KPIs, open risks) at `delivery.engagement_completed` for every Forge engagement; Keep attach target is every Forge Build/Scale and at least 40% of Compass Programmes (COMPANY.md §2).
- **sales and executive**: capacity and delivery risk view for pipeline decisions; scoping effort estimates.
- **finance**: milestone evidence and percentage-of-completion inputs for revenue recognition (COMPANY.md §7).

## 7. Risks and dependencies

| # | Risk | Likelihood / impact | Mitigation and owner |
|---|---|---|---|
| 1 | **Utilisation shortfall** below 70% blended, because hiring runs ahead of signed work (Y1 gross margin target is only 48%, COMPANY.md §5.1) | Medium / High | Hire only on triggers in section 5.4; Resourcing and Capacity Manager owns weekly forecast; associates absorb peaks; Managing Partner can defer a hire cohort by one quarter |
| 2 | **Hiring lag**: 45-day time-to-hire (COMPANY.md §8) and competition for senior AI engineers in London and New York | High / Medium | Requisitions raised one quarter ahead; retained search partner for Principal and Partner roles; internal promotion path Consultant to Manager; associate bench |
| 3 | **Scope creep on fixed-fee work** eroding margin | High / High | Written assumptions at scoping; Engagement Monitoring Agent flags burn deviation; every change order signed before work starts (COMPANY.md §7); PMO desk from FY2028; Principal authority limits (15% of fee) |
| 4 | **Quality failure**: a deliverable or agent output with an error reaches a client | Medium / High | Manager-or-above gate on every deliverable (COMPANY.md §4); QA Pre-Review Agent; independent Director, Delivery Quality and Methods from H2 FY2027; sampled second-line review; `delivery.quality_issue_raised` within 1 business day |
| 5 | **Agent over-reliance or hallucination** in analysis and drafting | Medium / High | Agents draft only; citations required; human reviewer logged against every use of agent output (COMPANY.md §9.4); evaluation sets and `data.agent_quality_report_published` thresholds |
| 6 | **Key-person concentration**: Y1 delivery rests on 3 senior people (Managing Partner and 2 Partners) | Medium / High | Second Partner in post by Q2; documented methods; two named leads on every engagement above £120k |
| 7 | **Attrition** above the 14% FY2026 / 11% FY2028 plan (COMPANY.md §8) | Medium / Medium | Engagement survey actions (`people.engagement_survey_completed`), utilisation caps by level, promotion cycle, equity for Principal and above |
| 8 | **Client concentration**: any client above 15% of revenue breaches policy (COMPANY.md §8) | Low / High | Capacity allocation capped at 15% of delivery days per client; Partner review above 12% |
| 9 | **US launch strain** in FY2027: New York team starts without local delivery depth | Medium / Medium | First US engagements led by a UK Principal on rotation; US hires +15% base (COMPANY.md §6.2); US launch gated on ISO 27001 and SOC 2 Type II progress (COMPANY.md §8) |
| 10 | **Agent platform dependency** on product, data and third-party model providers; model-price fall assumption (15% a year, COMPANY.md §8) does not materialise | Medium / Medium | Multi-model routing, agent-day budget per engagement, quarterly cost review with data and finance |
| 11 | **Client data incident** involving an agent or consultant | Low / Critical | Least-privilege access, client sandbox copies, `it_security.incident_detected` handling, 72h ICO process led by General Counsel with CISO and CEO (COMPANY.md §9.3) |

Key dependencies: Series A funding closes in Q2 FY2026 (COMPANY.md §1); `executive.budget_approved` for each annual budget; People recruiting capacity; Product's delivery agent platform; Sales pipeline sufficient to keep the staffing pyramid utilised.

## 8. Sources

COMPANY.md sections cited in this blueprint:

- §1 Identity (Day 0, Series A timing, US office from Q1 FY2027)
- §2 Business model (leverage model, Keep attach target)
- §3.1 to §3.3 Service lines and pricing; §3.5 Rate card (change orders and agent-day)
- §4 Delivery model (utilisation targets, staffing pyramid, quality gate, typical team)
- §5.1 Revenue, clients, margin (gross margin and cost of revenue; Compass and Forge revenue by line)
- §5.2 Cost sanity check (loaded cost, agent cost range)
- §5.4 Department budget envelopes (delivery row)
- §6 Headcount plan and §6.1 by department (delivery row: 14 / 46 / 104 humans, 6 / 22 / 52 agents)
- §6.2 Levels and salary bands (US +15%)
- §7 Billing and commercial terms (30/40/30 milestones, change orders, invoicing within 2 business days)
- §8 Key assumptions (time-to-hire, attrition, model-cost decline, 15% client concentration, US launch gating)
- §9.2 Executive team (Oliver Thackeray, Managing Partner, Delivery)
- §9.3 Delegations of authority (headcount approval, ICO notification)
- §9.4 AI agent governance
- CONVENTIONS.md section 7 and `core/topics.py` for topic names
