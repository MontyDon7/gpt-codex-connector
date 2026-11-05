# Data and Analytics Department Blueprint

## 1. Mission and scope

The Data and Analytics department (id `data`, led by the Chief Data and AI Officer, Dr Emeka Nwosu; COMPANY.md §9.2) is the firm's single source of truth for numbers. Its mission is to make every management decision at Lumenhall Partners, and every AI agent that acts on the firm's behalf, rest on metrics that are defined once, computed once and reproducible by anyone (COMPANY.md §1).

Scope:

1. **Firm-wide metrics and reporting.** Own the metric registry (definition, formula, source system, owner, certification status) and publish the monthly firm KPI report (`data.kpi_report_published`) to Executive and Finance. Pipeline, bookings, billings, collections, active engagements, client health and Keep ARR are computed from the event stream, never keyed in by hand.
2. **Data engineering.** Own the data platform: ingestion from operational systems and from the department event stream, the warehouse, transformation layers (raw, staged, certified marts) and the semantic layer.
3. **Business intelligence.** Own dashboard governance: every dashboard has an owner, a certified metric set and a review date; uncertified dashboards are labelled as such.
4. **Forecasting.** Produce and track the pipeline-weighted bookings forecast, the revenue and cash-inflow forecast and delivery demand signals (`data.forecast_updated`), with forecast error tracked and published.
5. **Data governance.** Own data classification, retention, access control and client-data segregation (client data stays in client-scoped stores under the data-processing agreement; COMPANY.md §9.4), working with IT Security and Legal.
6. **AI agent quality.** Run the agent evaluation harness and publish the agent quality report (`data.agent_quality_report_published`); maintain the agent register jointly with IT Security (COMPANY.md §9.4).
7. **Benchmarks.** Convert external market data and anonymised cross-client delivery data into benchmarks for Delivery and Marketing (`data.benchmark_ready`).

Out of scope: statutory accounts and month-end close (Finance), client-facing delivery analytics built inside a client engagement (Delivery), security monitoring (IT Security), and product telemetry design (Product), although Data consumes and certifies their outputs.

Operating principles: one definition per metric; certify before you publish; least privilege by default; agents propose, humans approve; no client-identifiable data in firm-wide marts.

## 2. Org chart

```
Chief Data and AI Officer (head)  Dr Emeka Nwosu  -> reports to Chief Executive Officer
|-- Principal Data Architect (principal)                  [Y3]
|-- Data Engineering Manager (manager)                    [Y3]
|     `-- Senior Data Engineer (senior_consultant)        [Y2: 1, Y3: 2]
|-- Data Governance Lead (manager)                        [Y3]
|-- Senior Forecasting Scientist (senior_consultant)      [Y3]
`-- BI and Analytics Analyst (consultant)                 [Y2: 1, Y3: 2]

AI agents (digital colleagues, all with a named human owner; see section 4)
|-- Metrics and KPI Reporting Agent      owner: Chief Data and AI Officer
|-- Data Quality Monitor Agent           owner: Senior Data Engineer (Chief Data and AI Officer until hired)
|-- Forecasting Agent                    owner: Senior Forecasting Scientist (Chief Data and AI Officer until hired)
|-- Agent Quality Evaluation Agent       owner: Principal Data Architect
|-- Benchmark Agent                      owner: Senior Forecasting Scientist
`-- Governance and Lineage Agent         owner: Data Governance Lead
```

In Y2 the Senior Data Engineer reports directly to the head; from Y3 the Data Engineering Manager takes the engineers. The BI and Analytics Analysts report to the Chief Data and AI Officer in Y2 and to the Principal Data Architect from Y3 (the architect owns the semantic layer and dashboard standards).

## 3. Roles

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Data and AI Officer | head | Chief Executive Officer | 1 | 1 | 1 | 140,000 to 200,000 (cash; plus equity) | Data and AI strategy, metric registry ownership, board and executive reporting, agent register co-owner, department budget |
| Principal Data Architect | principal | Chief Data and AI Officer | 0 | 0 | 1 | 120,000 to 155,000 | Platform architecture, semantic layer, dashboard standards, client-data segregation design, owner of Agent Quality Evaluation Agent |
| Data Engineering Manager | manager | Chief Data and AI Officer | 0 | 0 | 1 | 92,000 to 115,000 | Pipelines, warehouse operations, data quality SLAs, on-call rota, line management of engineers |
| Data Governance Lead | manager | Chief Data and AI Officer | 0 | 0 | 1 | 92,000 to 115,000 | Classification, retention schedule, access reviews, DPIAs with Legal, certification of metrics, owner of Governance and Lineage Agent |
| Senior Data Engineer | senior_consultant | Chief Data and AI Officer (Y2); Data Engineering Manager (Y3) | 0 | 1 | 2 | 72,000 to 90,000 | Ingestion, transformation models, data tests, observability, owner of Data Quality Monitor Agent |
| Senior Forecasting Scientist | senior_consultant | Chief Data and AI Officer | 0 | 0 | 1 | 72,000 to 90,000 | Forecast methodology, backtests and error tracking, benchmark methodology, owner of Forecasting and Benchmark Agents |
| BI and Analytics Analyst | consultant | Chief Data and AI Officer (Y2); Principal Data Architect (Y3) | 0 | 1 | 2 | 55,000 to 70,000 | Dashboards, ad-hoc analysis, report production, metric documentation, dashboard review calendar |
| **Total humans** | | | **1** | **3** | **9** | | Matches COMPANY.md §6.1 (data: 1 / 3 / 9) |

Salary bases used in `economics.md` (all inside the §6.2 bands): head £140,000 (Y1, Y2) and £150,000 (Y3); Principal Data Architect £145,000; Data Engineering Manager £112,000; Data Governance Lead £108,000; Senior Data Engineer £82,000; Senior Forecasting Scientist £90,000; BI and Analytics Analyst £62,000. US hires carry +15% (COMPANY.md §6.2); none are planned before FY2028.

## 4. AI agents

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Metrics and KPI Reporting Agent (the `data` department agent in the simulation) | Chief Data and AI Officer | Consumes lifecycle events, computes pipeline, bookings, billings, collections, engagement and Keep ARR metrics; drafts the monthly KPI report | May publish internal reports; board-pack figures need human sign-off before external use; cannot change a certified metric definition | 1 | 1 | 1 |
| Data Quality Monitor Agent | Senior Data Engineer (Chief Data and AI Officer until the engineer starts) | Runs completeness, validity, uniqueness and freshness checks on events and tables; raises `data.data_quality_issue_raised` | May quarantine a record in the staging layer; may not delete source data or alter certified marts | 0 | 1 | 2 |
| Forecasting Agent | Senior Forecasting Scientist (Chief Data and AI Officer until hired) | Re-runs the bookings, revenue and capacity forecasts, computes error versus actuals | Publishes forecasts with confidence band; model or assumption changes need human approval | 0 | 1 | 1 |
| Agent Quality Evaluation Agent | Principal Data Architect | Runs the evaluation harness over registered AI agents: accuracy, escalation rate, policy breaches | Read-only on agent logs; cannot disable an agent (escalates to the agent owner and IT Security) | 0 | 0 | 1 |
| Benchmark Agent | Senior Forecasting Scientist | Builds anonymised benchmarks from external market data and cross-client delivery data | Minimum cohort size of 5 clients; never exposes client-identifiable values | 0 | 0 | 1 |
| Governance and Lineage Agent | Data Governance Lead | Maintains lineage graph, retention clock and access-review evidence | Proposes deletions and access removals; execution needs human approval | 0 | 0 | 1 |
| **Total agents** | | | | **1** | **3** | **7** |

Totals match COMPANY.md §6.1 (data agents: 1 / 3 / 7). Per COMPANY.md §9.4 none of these agents may sign contracts, release client deliverables without human QA, approve payments above £10,000, make hiring or termination decisions, or notify regulators.

## 5. Hiring plan

Time-to-hire is 45 days for humans (COMPANY.md §8.3), so `data.hire_requested` is raised at least one quarter before the start quarter. Approval is by the CEO (`executive.headcount_approved`, COMPANY.md §9.3); these roles are inside the approved §6.1 headcount.

### FY2026 (by quarter)

| Quarter | Role | Count | Start | Trigger |
|---|---|---|---|---|
| Q1 | none (department agent only; Finance and Operations cover warehouse administration) | 0 | n/a | Seed phase: single agent computes metrics |
| Q2 | none | 0 | n/a | Series A closes (COMPANY.md §1); head search runs through People |
| Q3 | Chief Data and AI Officer (Dr Emeka Nwosu) | 1 | Q3 (2026-07-01, half-year in post) | Series A funded; 24 new logos target needs governed metrics |
| Q4 | none | 0 | n/a | Budget cycle for FY2027 opens (`finance.budget_cycle_opened`) |

Year-end humans: 1.

### FY2027 and FY2028 (by half-year)

| Half-year | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| FY2027 H1 | none | 0 | n/a | Head and agents carry the load while the platform is built |
| FY2027 H2 | Senior Data Engineer | 1 | Q3 | More than 10 source feeds, or data quality pass rate below 95% for two months |
| FY2027 H2 | BI and Analytics Analyst | 1 | Q4 | More than 25 live dashboards, or KPI report turnaround above 3 working days |
| FY2028 H1 | Principal Data Architect | 1 | Q1 | SOC 2 Type II evidence and US data-residency design (COMPANY.md §8.6, §8.7) |
| FY2028 H1 | Data Engineering Manager | 1 | Q1 | Two or more engineers and an on-call rota |
| FY2028 H1 | Senior Forecasting Scientist | 1 | Q1 | Forecast error target (MAPE 8%) needs dedicated methodology owner; 85 new logos target |
| FY2028 H1 | Data Governance Lead | 1 | Q2 | More than 100 registered metrics and agents (agent register 150 agents, COMPANY.md §6) |
| FY2028 H1 | Senior Data Engineer | 1 | Q2 | US entity ingestion, second region |
| FY2028 H2 | BI and Analytics Analyst | 1 | Q4 | More than 140 active clients needing client-level health dashboards |

Year-end humans: FY2027 3, FY2028 9 (matches COMPANY.md §6.1). Agent provisioning takes 5 days (COMPANY.md §8.3): Data Quality Monitor and Forecasting Agents in FY2027 Q1, Agent Quality Evaluation, Benchmark and Governance and Lineage Agents in FY2028 Q1, and the second Data Quality Monitor Agent in FY2028 Q2.

## 6. Interfaces

Topic names are from the authoritative map in `core/topics.py` and CONVENTIONS.md §7.

| Direction | Counterparty | Topics | Purpose |
|---|---|---|---|
| Depends on | Marketing | `marketing.lead_generated`, `marketing.campaign_launched` | Top of the funnel: leads, campaign spend and reach |
| Depends on | Sales | `sales.lead_qualified`, `sales.proposal_sent`, `sales.deal_won`, `sales.deal_lost` | Pipeline, win rate, bookings |
| Depends on | Delivery | `delivery.engagement_kickoff`, `delivery.engagement_completed` | Active engagements, capacity demand, benchmarks |
| Depends on | Finance | `finance.invoice_issued`, `finance.payment_received`, `finance.month_end_closed`, `finance.cash_forecast_updated`, `finance.budget_cycle_opened` | Billings, collections, DSO, close-aligned reporting, budget cycle |
| Depends on | Customer Success | `customer_success.health_score_updated`, `customer_success.renewal_confirmed`, `customer_success.client_churned` | Client health, retention, Keep ARR |
| Depends on | Executive | `executive.board_meeting_held`, `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.strategy_updated` | Board pack timing, targets, reporting cadence |
| Depends on | Legal | `legal.regulatory_change_noted`, `legal.ai_risk_review_completed` | Retention and privacy rule changes, AI risk outcomes |
| Depends on | Product | `product.ai_risk_review_requested` | New or changed agents enter the register and evaluation harness |
| Depends on | External | `external.market_data_published` | Market indices for benchmarks |
| Serves | Executive, Finance | `data.kpi_report_published` | Monthly firm KPI report |
| Serves | Sales, Finance, Delivery, Executive | `data.forecast_updated` | Bookings, revenue and capacity forecasts |
| Serves | Operations, Product | `data.data_quality_issue_raised` | Data defects needing a process or product fix |
| Serves | Product, Delivery, Executive | `data.agent_quality_report_published` | AI agent quality results |
| Serves | Delivery, Marketing | `data.benchmark_ready` | Benchmarks for scoping and content |
| Serves | Finance, People | `data.budget_submitted`, `data.hire_requested` | Generic budget and hiring flows |

Shared obligations: IT Security owns access provisioning and the security controls on the platform; Data owns classification, access policy content and quarterly access reviews. Legal owns the retention basis and DPIAs; Data operationalises them. Both the agent register and the incident response for data breaches (`it_security.data_breach_confirmed`) involve Data as a technical responder even though it does not subscribe to that topic.

## 7. Risks and dependencies

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Metric definitions drift between departments (for example "revenue" meaning billed, recognised or cash) | Board sees conflicting numbers | High | Single registry; certified definitions in `kpis.md`; every report names the metric id |
| Upstream event missing keys or duplicated | Wrong pipeline or billings | High | Validation on ingest; duplicate guard; `data.data_quality_issue_raised` to Operations |
| Cross-client leakage in shared marts or agent prompts | Contract breach, UK GDPR exposure | Low, severe | Client-scoped stores, row-level security, no client PII in firm marts, k >= 5 anonymity for benchmarks |
| Key-person risk: one human in Y1 and three in Y2 | Reporting and platform outages | High in Y1 and Y2 | Documented runbooks, agents run all routine reporting, backup by Finance analyst for month-end |
| Forecast over-trust | Hiring and spend decisions on poor forecasts | Medium | Confidence band on every forecast; MAPE published; manual override logged |
| Warehouse and agent compute cost grows faster than revenue | Budget overrun (COMPANY.md §5.4) | Medium | Monthly platform cost review, auto-suspend, query cost caps |
| Hiring lag for scarce data talent (45-day time-to-hire) | Roadmap slips | Medium | Quarter-ahead requests; contractor bridge via `people.contractor_engaged` |
| Regulatory change to retention or AI rules | Rework | Medium | Subscribe to `legal.regulatory_change_noted`; retention schedule reviewed quarterly |

Dependencies: People (hiring), IT Security (identity, secrets, platform hardening), Finance (ledger as source of truth for money), Legal (DPIA, retention basis), Product (telemetry).

## 8. Sources

- COMPANY.md §1 (identity, fiscal year, simulation start)
- COMPANY.md §2 (business model, leverage)
- COMPANY.md §3 (service lines and pricing)
- COMPANY.md §5.1 (revenue, clients, Keep ARR targets)
- COMPANY.md §5.3 (commercial funnel and win rate)
- COMPANY.md §5.4 (department budget envelope)
- COMPANY.md §6, §6.1, §6.2 (headcount, levels, salary bands)
- COMPANY.md §7 (billing terms, DSO)
- COMPANY.md §8 (assumptions: time-to-hire, compliance baseline)
- COMPANY.md §9.2, §9.3, §9.4 (heads, delegations, AI agent governance)
- COMPANY.md §10 (sample client)
