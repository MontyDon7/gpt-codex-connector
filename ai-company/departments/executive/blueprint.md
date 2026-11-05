# Executive Department Blueprint

## 1. Mission and scope

The Executive department is the CEO office of Lumenhall Partners Ltd. It sets strategy, runs the Board relationship, and holds the decision rights that the company reserves for the top of the house (`COMPANY.md §9.3`). It is deliberately small: 3 humans and 1 AI agent at the end of FY2026, growing to 5 humans and 3 agents by FY2028 (`COMPANY.md §6.1`).

**What the department owns**

| Area | Scope | Authority source |
|---|---|---|
| Strategy and OKRs | Annual strategy refresh, company OKRs, quarterly strategy reviews. Publishes `executive.strategy_updated` and `executive.okrs_set`. | `COMPANY.md §9.1` (Board approves any change to the strategy) |
| Board and investors | Quarterly Board, ad hoc Board meetings, Board packs, Audit and Risk and Remuneration committee support, investor updates for Ashgrove Ventures and Tern Capital. Publishes `executive.board_meeting_held`. | `COMPANY.md §9.1` |
| Deal approval | CEO approval of any deal with total contract value of £500,000 or more; referral of deals above £1.5m to the Board; approval of contract exceptions raised by Legal. Publishes `executive.deal_decision_made`. | `COMPANY.md §9.3` |
| Budget approval | Sets the annual envelope per department, approves the consolidated budget. Publishes `executive.budget_approved`. | `COMPANY.md §5.4`, `§9.1` |
| Headcount approval | CEO approval of new headcount outside the approved budget; Board approval of executive hires. Publishes `executive.headcount_approved`. | `COMPANY.md §9.3` |
| Pricing governance | Approval of list-price changes proposed by Product with Finance input. Publishes `executive.pricing_change_approved`. | `COMPANY.md §3` |
| Crisis command | Declaration and command of a company-wide crisis (breach, regulatory event, reputational event, key-client loss, liquidity). Publishes `executive.crisis_declared`. | `COMPANY.md §9.3` (breach notification) |

**Out of scope.** The department does not run sales, delivery, finance, legal or IT operations. It decides, sponsors and escalates; the 11 other department heads execute. Executive agents may draft, analyse, monitor and propose, but never sign contracts, release client deliverables, approve payments above £10,000, make final hiring or termination decisions, or notify regulators (`COMPANY.md §9.4`).

**Operating principle.** Decide inside a stated service level, record the rationale in the decision log, and broadcast the outcome on the bus so that Sales, Finance, Legal and People never wait on an informal message.

## 2. Org chart

```
Board of Directors (5 seats, COMPANY.md §9.1)
 |  Independent Chair: Priya Raman
 |  CEO: Imogen Hartley
 |  Investor directors: Tomas Beckett (Ashgrove Ventures), Adaeze Okafor (Tern Capital)
 |  Independent NED, Audit and Risk chair: Marcus Ellery
 |
Chief Executive Officer (Imogen Hartley)
 |-- Chief of Staff
 |     |-- Board and Investor Relations Manager          (from Q1 FY2027)
 |-- Strategy and Transformation Lead
 |     |-- Senior Strategy Consultant                    (from Q2 FY2028)
 |-- [AI] Executive Chief-of-Staff Agent                 (Y1)
 |-- [AI] Strategy Intelligence Agent                    (from Q2 FY2027)
 |-- [AI] Board and Investor Reporting Agent             (from Q1 FY2028)
 |
 `-- 11 department heads (dotted line for decisions, solid line for performance):
     Chief Revenue Officer, Chief Marketing Officer, Managing Partner Delivery, Chief Financial Officer,
     Chief People Officer, General Counsel, CISO, Chief Operating Officer, Chief Customer Officer,
     Chief Product Officer, Chief Data and AI Officer (COMPANY.md §9.2)
```

The Chief of Staff runs the decision desk (deal, headcount and budget approvals) and the Board calendar. The Strategy and Transformation Lead runs the strategy cycle, OKRs and cross-department transformation programmes. The CEO signs every decision the Chief of Staff does not hold under delegation (see Section 6 and SOP-EXECUTIVE-01).

## 3. Roles

Level keys and bands come from `COMPANY.md §6.2`. Y1/Y2/Y3 are year-end humans and sum to the executive row of `COMPANY.md §6.1` (3 / 4 / 5).

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Executive Officer | executive | Board of Directors | 1 | 1 | 1 | 200,000 to 260,000 (cash; plus equity) | Strategy; Board accountability; approves deals of £500k or more, non-budgeted spend above £250k, headcount outside budget; declares and commands crises; owns investor relations with the Chair; chairs the executive team |
| Chief of Staff | principal | Chief Executive Officer | 1 | 1 | 1 | 120,000 to 155,000 | Runs the decision desk and the decision log; prepares deal, headcount and budget decisions for CEO signature; owns the executive operating cadence (weekly executive meeting, monthly KPI review, quarterly Board); supervises the Executive Chief-of-Staff Agent |
| Strategy and Transformation Lead | manager | Chief Executive Officer | 1 | 1 | 1 | 92,000 to 115,000 | Annual strategy refresh and company OKRs; market and competitor scanning; scenario modelling for pricing and expansion decisions; US launch gate tracking (`COMPANY.md §8` assumption 6); supervises the Strategy Intelligence Agent |
| Board and Investor Relations Manager | manager | Chief of Staff | 0 | 1 | 1 | 92,000 to 115,000 | Board pack production, minutes, committee calendar; investor updates for Ashgrove Ventures and Tern Capital; liaison with the company secretary and Legal for the Delaware entity; supervises the Board and Investor Reporting Agent |
| Senior Strategy Consultant | senior_consultant | Strategy and Transformation Lead | 0 | 0 | 1 | 72,000 to 90,000 | Quantitative strategy work: market sizing, unit-economics models, scenario analysis for the US expansion and FY2029 planning; owns the strategy data room |
| **Total humans** | | | **3** | **4** | **5** | | Matches `COMPANY.md §6.1` |

## 4. AI agents

Every agent has a named accountable human owner and is registered in the agent register held by Data and IT Security (`COMPANY.md §9.4`). Average fully loaded agent cost is £20k to £35k per agent-year (`COMPANY.md §5.2`).

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Executive Chief-of-Staff Agent (`executive`, `ExecutiveAgent`) | Chief of Staff | Triages every inbound approval request on the bus; applies the delegation-of-authority rules; drafts decisions with rationale; runs the decision log, KPI actuals, crisis checklist and Board calendar | May draft, route and broadcast decisions that fall inside rules the CEO has pre-approved (for example in-plan headcount, deals that pass every control). Anything above £1.5m, any uncapped-liability or non-standard term, any breach of the 15% concentration cap, any executive hire and any crisis declaration is a recommendation that the CEO or Board ratifies. Never signs contracts, approves payments above £10,000, or notifies regulators | 1 | 1 | 1 |
| Strategy Intelligence Agent | Strategy and Transformation Lead | Monitors market data, competitor moves, forecast revisions and pricing proposals; produces scenario notes and strategy-refresh drafts | Analyse and propose only. Cannot publish a strategy change or approve a price change | 0 | 1 | 1 |
| Board and Investor Reporting Agent | Board and Investor Relations Manager | Assembles Board packs and investor updates from Finance, Data and Delivery reports; tracks Board action items | Drafts only. A human reviews every pack before it leaves the company. Cannot send external investor communications | 0 | 0 | 1 |
| **Total agents** | | | | **1** | **2** | **3** |

Totals match `COMPANY.md §6.1` (1 / 2 / 3 agents).

## 5. Hiring plan

Time-to-hire for humans is 45 days; agent provisioning takes 5 days (`COMPANY.md §8` assumption 3). All executive-department hires are approved by the Board (`COMPANY.md §9.1`) and are raised through `executive.hire_requested`. Start dates below are target dates.

### FY2026 (quarterly)

| Quarter | Role | Count | Start | Trigger |
|---|---|---|---|---|
| Q1 | Chief Executive Officer | 1 | 2026-01-05 (in post at Day 0) | Founding appointment |
| Q1 | Executive Chief-of-Staff Agent | 1 agent | 2026-01-12 | Series A budget baseline; agent provisioning 5 days |
| Q1 | Chief of Staff | 1 | 2026-03-01 | Executive team of 12 heads formed (`COMPANY.md §9.2`); decision volume above CEO capacity |
| Q2 | none | 0 | n/a | Series A closes in Q2 (`COMPANY.md §1`); hire freeze until cash received |
| Q3 | Strategy and Transformation Lead | 1 | 2026-07-01 | Series A funds received; strategy refresh needed ahead of FY2027 budget cycle |
| Q4 | none | 0 | n/a | FY2027 budget cycle in progress |

### FY2027 and FY2028 (half-year)

| Period | Role | Count | Start | Trigger |
|---|---|---|---|---|
| FY2027 H1 | Board and Investor Relations Manager | 1 | 2027-01-04 | US entity and Delaware governance; board cadence moves to quarterly plus Audit and Risk |
| FY2027 H1 | Strategy Intelligence Agent | 1 agent | 2027-04-01 | Scenario load for US launch gate |
| FY2027 H2 | none | 0 | n/a | Headcount 4 humans reached |
| FY2028 H1 | Senior Strategy Consultant | 1 | 2028-04-03 | FY2028 revenue plan of £46.2m needs dedicated quantitative strategy capacity |
| FY2028 H1 | Board and Investor Reporting Agent | 1 agent | 2028-01-17 | Reporting volume across 140 active clients |
| FY2028 H2 | none | 0 | n/a | Headcount 5 humans reached |

Year-end humans: 3 (FY2026), 4 (FY2027), 5 (FY2028). Year-end agents: 1, 2, 3.

## 6. Interfaces

Topics are those in `core/topics.py` (CONVENTIONS section 7). The department publishes 8 named topics plus `executive.budget_submitted` (to Finance) and `executive.hire_requested` (to People).

| Counterpart | Direction | Topics | What is exchanged |
|---|---|---|---|
| Sales (CRO) | in / out | in: `sales.deal_approval_requested`, `sales.proposal_sent`, `sales.deal_won`, `sales.deal_lost`; out: `executive.deal_decision_made`, `executive.pricing_change_approved`, `executive.okrs_set` | Deal approvals of £500k or more; pipeline visibility; targets |
| Finance (CFO) | in / out | in: `finance.budget_cycle_opened`, `finance.budget_submitted`, `finance.budget_consolidated`, `finance.budget_variance_flagged`, `finance.cash_forecast_updated`, `finance.month_end_closed`, `finance.collections_escalated`; out: `executive.budget_submitted`, `executive.budget_approved`, `executive.headcount_approved`, `executive.deal_decision_made` | Annual and in-year budget control; cash runway; collections escalation at day 45 |
| People (CPO) | in / out | in: `people.requisition_opened`, `people.hire_requested`, `people.engagement_survey_completed`; out: `executive.headcount_approved`, `executive.hire_requested` | Requisitions and approvals; engagement results |
| Legal (GC) | in / out | in: `legal.contract_risk_flagged`, `legal.client_dispute_raised`, `legal.compliance_finding_raised`, `legal.regulator_notification_filed`, `legal.regulatory_change_noted`, `legal.ai_risk_review_completed`; out: `executive.deal_decision_made`, `executive.board_meeting_held`, `executive.crisis_declared` | Contract exceptions; regulatory events; Board papers |
| IT Security (CISO) | in | `it_security.incident_detected`, `it_security.data_breach_confirmed`, `it_security.incident_resolved`, `it_security.certification_status_updated` | Crisis triggers; certification gates for US launch |
| Customer Success (CCO) | in | `customer_success.churn_risk_flagged`, `customer_success.client_churned` | Key-client risk; executive sponsor calls |
| Delivery (Managing Partner) | in | `delivery.capacity_forecast_updated`, `delivery.quality_issue_raised` | Capacity against sold work; quality escalations |
| Product (CPO) | in | `product.pricing_change_proposed`, `product.roadmap_published` | Price changes; roadmap alignment |
| Data (CDAIO) | in / out | in: `data.kpi_report_published`, `data.forecast_updated`, `data.agent_quality_report_published`; out: `executive.board_meeting_held`, `executive.okrs_set` | KPI actuals; forecasts; agent quality |
| Operations (COO) | in | `operations.continuity_test_completed`, `operations.process_improvement_proposed` | Continuity assurance; improvement proposals above delegation |
| Marketing (CMO) | in | `marketing.brand_incident_raised` | Reputational crisis trigger |
| Board and investors | in | `external.board_request` | Board and investor requests entering the company |
| All departments | out | `executive.strategy_updated`, `executive.okrs_set`, `executive.budget_approved`, `executive.crisis_declared` | Company-wide direction and crisis mobilisation |

Refusals (declined headcount, pricing or budget requests) are sent as direct messages in the `executive.internal.*` namespace to the requesting department (see Topic requests in the lead report).

## 7. Risks and dependencies

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Key-person dependency on one CEO and one Chief of Staff; no deputy for decisions | Medium | High | Written delegations (SOP-EXECUTIVE-01); Chair acts as escalation for deals above £1.5m; Senior Strategy Consultant in FY2028 deepens bench | CEO |
| Decision latency stalls deals (sales cycle is 75 days, `COMPANY.md §5.3`) | Medium | High | 2 business day SLA for deal decisions; agent triage on receipt; weekly decision desk | Chief of Staff |
| Client concentration breaches the 15% policy (`COMPANY.md §8` assumption 8) | Low | High | Concentration check built into every deal decision; Board notified of any client above 10% | CEO |
| Crisis declared too late (72h ICO clock, `COMPANY.md §9.3`) | Low | Critical | Crisis triggers in SOP-EXECUTIVE-06; 4 hour declaration target; Legal and CISO have authority to call the CEO directly | CEO |
| Budget overruns not caught until month end | Medium | Medium | Variance flags from Finance trigger hiring holds at 15% variance; monthly review | CFO and CEO |
| Executive hires delayed by Board calendar | Medium | Medium | Written Board consent route between quarterly meetings; ad hoc meetings with 5 days' notice | Chief of Staff |
| Agent mis-routes an approval | Low | Medium | Agent limits in Section 4; every agent decision logged; human ratification above thresholds | Chief of Staff |
| Series A timing (Q2 FY2026) slips | Low | High | Hiring plan gates Q3 hires on funds received; liquidity crisis trigger at runway below 6 months | CEO and CFO |

Dependencies: Finance for budget consolidation and cash forecasts; Data for KPI and forecast reports; Legal for deal and contract risk; People for requisition flow; all heads for timely submissions.

## 8. Sources

| Section | Used for |
|---|---|
| `COMPANY.md §1` | Funding, fiscal years, simulation start |
| `COMPANY.md §2` | Business model and leverage assumptions |
| `COMPANY.md §3` | Service lines and prices used in deal sizing |
| `COMPANY.md §4` | Delivery model references |
| `COMPANY.md §5.1` to `§5.4` | Revenue, margin, EBITDA, cost envelope for the department (£600k / £1,050k / £1,300k) |
| `COMPANY.md §6.1` | Headcount: 3 / 4 / 5 humans and 1 / 2 / 3 agents |
| `COMPANY.md §6.2` | Levels and salary bands |
| `COMPANY.md §8` | Assumptions (hiring time, attrition, US launch gate, concentration policy) |
| `COMPANY.md §9.1` to `§9.4` | Board, executive team, delegations of authority, AI governance |
