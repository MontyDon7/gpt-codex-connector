# Product Department Blueprint

## 1. Mission and scope

The Product department decides what Lumenhall Partners builds into its own AI agent platform and reusable Forge components, proves that it is safe and good enough before anyone relies on it, and makes sure the rest of the firm (Delivery, Sales, Marketing, Customer Success) knows what is available. It is led by the Chief Product Officer, Anika Rao, who reports to the CEO, Imogen Hartley (COMPANY.md §9.2).

"Product" here means the internal AI agent platform (the digital colleagues described in COMPANY.md §2 and §9.4), the reusable components that Forge engagements assemble (COMPANY.md §3.2), the Keep monitoring and optimisation tooling (COMPANY.md §3.3), and the way Compass, Forge and Keep are packaged and priced. Lumenhall does not sell software licences; its price list is fixed-fee projects and retainers (COMPANY.md §3). Product's job is to lower the cost and raise the quality of delivering them.

| Area | What Product owns | Standing targets |
|---|---|---|
| Roadmap and prioritisation | Quarterly roadmap built from client feedback, support escalations, strategy and OKRs; RICE-scored backlog; publication as `product.roadmap_published` | Committed items delivered; 20% of capacity always reserved for security fixes and client escalations |
| Stage gates | Five gates (G0 to G4) from intake to general availability, with evidence required at each | No agent or component reaches clients without passing G4 |
| AI model evaluation | Golden-set evaluation of every agent version and every candidate foundation model; regression control | Release score at or above 85 out of 100, no regression of more than 2 points (SOP-PRODUCT-04) |
| Red-teaming | Adversarial testing (prompt injection, data exfiltration, jailbreaks, tool misuse, bias probes) before release and after material change | Zero open critical or high findings on any live client-facing agent |
| AI risk review triggers | Deciding when a change is "material" under COMPANY.md §9.4 and raising `product.ai_risk_review_requested` to Legal, IT and Security and Data | 100% of material changes reviewed before release |
| Releases and capability announcements | Fortnightly release train, hotfixes, `product.release_shipped`, `product.agent_capability_added` | Release train every 14 days; hotfix within 2 business days |
| Vulnerability fixes | Fixing product-owned findings raised by IT and Security within the severity SLA; `product.vulnerability_fixed` | Fix due 2 days before the IT Security SLA expires so verification fits |
| Pricing and packaging proposals | Modelling and proposing changes to tiers, packaging and rate card; `product.pricing_change_proposed` | Finance models every proposal; Executive approves; Product never changes a price |
| Budget and hiring | Product budget submission and hire requests | Envelope of £270k / £620k / £1,960k (COMPANY.md §5.4) |

Out of scope: client delivery (Delivery), client relationship and renewals (Customer Success, Sales), the agent register and quality measurement (Data owns the evaluation harness and `data.agent_quality_report_published`; IT and Security co-own the register and credentials; Product consumes both and runs its own pre-release evaluation), legal sign-off on AI risk (Legal), vulnerability discovery (IT and Security), brand and campaigns (Marketing).

Product is an operating-expense department. Its cost is not part of cost of revenue (COMPANY.md §5.1). Its budget envelope is £270k / £620k / £1,960k (people £220k / £520k / £1,360k; non-people £50k / £100k / £600k) per COMPANY.md §5.4.

Note on agents: COMPANY.md §6.1 allows Product 0 AI agents in FY2026, 2 in FY2027 and 6 in FY2028. In FY2026 every Product activity is performed by the Chief Product Officer and, from Q4, the Product Manager. The simulated `ProductAgent` models the department's decision logic (what the humans decide and when); it is not a registered digital colleague in FY2026. The first registered Product agents arrive in Q2 FY2027 (section 4).

## 2. Org chart

```
Chief Product Officer (head)                         Anika Rao, reports to CEO
|
+-- Product Manager (1st)                            manager; joins Q4 FY2026
|     +-- Product Analyst x1                         analyst; joins Q2 FY2028
|     +-- Product Designer x1                        consultant; joins Q2 FY2028
|
+-- AI Evaluation and Red Team Lead                  manager; joins Q2 FY2027 (independent of builders)
|
+-- Product Manager (2nd)                            manager; joins Q4 FY2027
+-- Product Manager (3rd)                            manager; joins Q2 FY2028
|
+-- Senior AI Engineer (1st)                         senior_consultant; joins Q3 FY2027
|     (reports to CPO until the Director joins; then to Director of Agent Platform)
|
+-- Director of Agent Platform                       principal; joins Q1 FY2028
|     +-- Senior AI Engineer (1st, re-lined from CPO in Q1 FY2028)
|     +-- Senior AI Engineer (2nd)                   joins Q1 FY2028
|     +-- AI Engineer x2                             consultant; Q1 and Q2 FY2028
|
+-- AI agents (see section 4), each with a named human owner
```

Reporting-line notes: in FY2026 the CPO runs everything personally, with the Product Manager joining in Q4. In FY2027 the Product Managers, the AI Evaluation and Red Team Lead and the Senior AI Engineer all report to the CPO. In FY2028 the Director of Agent Platform takes engineering (Senior AI Engineers and AI Engineers). The AI Evaluation and Red Team Lead always reports to the CPO, never to the Director of Agent Platform, so that the people who test agents are not the people who build them. The Product Analyst and Product Designer report to the first Product Manager.

## 3. Roles

Headcount is year-end humans and sums to COMPANY.md §6.1: product = 2 / 5 / 12. Level keys and bands are from COMPANY.md §6.2.

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Product Officer | head | Chief Executive Officer | 1 | 1 | 1 | 140,000 to 200,000 (cash; plus equity) | Owns product strategy, roadmap, stage-gate decisions, release go/no-go, pricing and packaging proposals to the CEO, AI risk review requests (with the AI Evaluation and Red Team Lead), Product budget and hiring; decides release freezes; accountable for all Product agents until owners are in post |
| Director of Agent Platform | principal | Chief Product Officer | 0 | 0 | 1 | 120,000 to 155,000 | Owns platform architecture, engineering standards, build quality, secure-by-design practice, cost per agent-run, the engineering team and fix delivery against vulnerability SLAs |
| Product Manager | manager | Chief Product Officer | 1 | 2 | 3 | 92,000 to 115,000 | Owns a roadmap area (1st: agent platform and Forge components; 2nd from Q4 FY2027: Keep tooling and client-facing agent features; 3rd from Q2 FY2028: pricing, packaging and US readiness); backlog grooming and RICE scoring, client feedback synthesis, release notes, enablement with Delivery, Sales and Marketing; owner of the Roadmap and Feedback Synthesis Agent |
| AI Evaluation and Red Team Lead | manager | Chief Product Officer | 0 | 1 | 1 | 92,000 to 115,000 | Owns golden sets, evaluation method, model bake-offs, red-team programme and findings register, release evidence for G3 and G4, preparation of AI risk review requests; owner of the Evaluation and Red-Team Agents and the AI Risk Review Pack Agent |
| Senior AI Engineer | senior_consultant | Chief Product Officer (FY2027); Director of Agent Platform from Q1 FY2028 | 0 | 1 | 2 | 72,000 to 90,000 | Builds and hardens platform components, fixes product-owned vulnerabilities, runs release trains, maintains the evaluation harness integration with Data, SBOM and release gate evidence; owner of the Release and Vulnerability Tracking Agent |
| AI Engineer | consultant | Director of Agent Platform | 0 | 0 | 2 | 55,000 to 70,000 | Implements components, connectors, prompt and tool configurations, regression tests and fixes under senior review |
| Product Analyst | analyst | Product Manager | 0 | 0 | 1 | 38,000 to 48,000 | Backlog and usage analytics, feedback clustering checks, KPI reporting, pricing and packaging models with Finance; owner of the Pricing and Packaging Analysis Agent |
| Product Designer | consultant | Product Manager | 0 | 0 | 1 | 55,000 to 70,000 | Interaction design for client-facing agent experiences and Keep dashboards, accessibility, usability testing with client panels, human-in-the-loop and approval-flow design |
| **Total humans** | | | **2** | **5** | **12** | | Equals COMPANY.md §6.1 row for product |

### Planning salary points and cost check

Loaded cost = base x 1.28 (COMPANY.md §5.2). Planning base salaries sit inside the §6.2 bands. Average FTE reflects start quarter (Q1 start = 1.00, Q2 = 0.75, Q3 = 0.50, Q4 = 0.25 of a year). Base salaries step up at the annual review (January); the first Product Manager and the CPO therefore show a higher base in later years.

| Role | Planning base £ | Loaded £ | FY2026 avg FTE | FY2027 avg FTE | FY2028 avg FTE | FY2026 £k | FY2027 £k | FY2028 £k |
|---|---|---|---|---|---|---|---|---|
| Chief Product Officer | 145,000 / 152,000 / 165,000 | 185,600 / 194,560 / 211,200 | 1.00 | 1.00 | 1.00 | 185.6 | 194.6 | 211.2 |
| Director of Agent Platform | 140,000 | 179,200 | 0 | 0 | 1.00 | 0 | 0 | 179.2 |
| Product Manager (1st) | 105,000 / 110,000 / 114,000 | 134,400 / 140,800 / 145,920 | 0.25 | 1.00 | 1.00 | 33.6 | 140.8 | 145.9 |
| Product Manager (2nd) | 98,000 / 100,000 | 125,440 / 128,000 | 0 | 0.25 | 1.00 | 0 | 31.4 | 128.0 |
| Product Manager (3rd) | 96,000 | 122,880 | 0 | 0 | 0.75 | 0 | 0 | 92.2 |
| AI Evaluation and Red Team Lead | 100,000 / 104,000 | 128,000 / 133,120 | 0 | 0.75 | 1.00 | 0 | 96.0 | 133.1 |
| Senior AI Engineer (1st) | 85,000 / 88,000 | 108,800 / 112,640 | 0 | 0.50 | 1.00 | 0 | 54.4 | 112.6 |
| Senior AI Engineer (2nd) | 85,000 | 108,800 | 0 | 0 | 1.00 | 0 | 0 | 108.8 |
| AI Engineer (1st) | 66,000 | 84,480 | 0 | 0 | 1.00 | 0 | 0 | 84.5 |
| AI Engineer (2nd) | 64,000 | 81,920 | 0 | 0 | 0.75 | 0 | 0 | 61.4 |
| Product Analyst | 44,000 | 56,320 | 0 | 0 | 0.75 | 0 | 0 | 42.2 |
| Product Designer | 62,000 | 79,360 | 0 | 0 | 0.75 | 0 | 0 | 59.5 |
| **Total people cost** | | | **1.25** | **3.50** | **11.00** | **219.2** | **517.2** | **1,358.6** |
| COMPANY.md §5.4 people envelope | | | | | | 220 | 520 | 1,360 |
| Delta | | | | | | -0.8 | -2.8 | -1.4 |

All three years are within the £5k tolerance. The full build-up lives in `economics.md`.

## 4. AI agents

Agent counts sum to COMPANY.md §6.1: product = 0 / 2 / 6. Every agent is registered in the agent register (Data and IT and Security) and has a named accountable human (COMPANY.md §9.4). All Product agents share these hard limits: they may draft, analyse, score, monitor and propose; they may not release anything to a client, approve a stage gate, approve or waive an AI risk review, change a price, sign a contract, notify a regulator, or approve spend.

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Evaluation and Red-Team Agent | AI Evaluation and Red Team Lead | Runs golden-set evaluations on every release candidate and on each candidate foundation model, runs the automated adversarial suite (prompt injection, exfiltration, jailbreak, tool misuse), computes composite score and regression versus baseline, drafts the G3 and G4 evidence pack | Cannot pass or fail a gate; reports the score and findings. Any finding rated high or critical goes to the human owner the same day. Cannot close a finding without human re-test. Year 3 count is two (platform agents and Keep client agents) | 0 | 1 | 2 |
| Roadmap and Feedback Synthesis Agent | Product Manager | Clusters `customer_success.feedback_received` and `customer_success.support_escalated` by theme, computes RICE scores, drafts the quarterly roadmap and the roadmap-versus-delivery report | Proposes ranking only; cannot commit an item to the roadmap or change a committed item; cannot message clients | 0 | 1 | 1 |
| Release and Vulnerability Tracking Agent | Senior AI Engineer | Tracks release train readiness, SBOM and gate evidence, tracks product-owned findings from `it_security.vulnerability_found` against the severity clock, drafts release notes and fix summaries | Cannot ship, merge to production or mark a finding fixed; shipping and fix confirmation are human steps | 0 | 0 | 1 |
| AI Risk Review Pack Agent | AI Evaluation and Red Team Lead | Applies the risk-review trigger list (RT-1 to RT-8, SOP-PRODUCT-06), assembles the review request (change summary, data classes, use-case tags, evaluation and red-team evidence) for Legal, IT and Security and Data | Cannot decide that a change is not material when any trigger matches; cannot waive or interpret Legal's outcome; cannot lift a hold | 0 | 0 | 1 |
| Pricing and Packaging Analysis Agent | Product Analyst (Product Manager until the Analyst is hired) | Builds the revenue, margin and Keep-uplift sensitivity for a proposed tier, packaging or rate-card change using COMPANY.md §3 and §7 inputs; drafts the proposal | Cannot send a pricing proposal; cannot change the price book; outputs go through the Product Manager and CPO and are modelled by Finance | 0 | 0 | 1 |
| **Total agents** | | | | **0** | **2** | **6** |

Agent cost is carried in non-people spend (AI compute and tooling), at the £20k to £35k per agent-year range of COMPANY.md §5.2 (£24.0k in FY2027 and £20.5k in FY2028 per agent-year, falling about 15% a year per COMPANY.md §8).

## 5. Hiring plan

Time-to-hire is 45 days for humans and 5 days for agent provisioning (COMPANY.md §8). Every human hire goes through `product.hire_requested`, then `people.requisition_opened`, then `executive.headcount_approved`, because even hires inside the §5.4 budget need the CEO's headcount approval record (COMPANY.md §9.3). Requisitions open one quarter ahead of the start quarter.

### FY2026 (quarterly)

| Quarter | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| Q1 FY2026 | Chief Product Officer (Anika Rao) | 1 | Q1 FY2026 (in post from Day 0, 2026-01-05) | Founding executive team (COMPANY.md §9.2) |
| Q2 FY2026 | none | 0 | n/a | Series A (£10m) closes; CPO sets the first roadmap and the evaluation method personally |
| Q3 FY2026 | none; requisition for Product Manager opened | 0 | n/a | Trigger for requisition: open backlog above 15 items, or at least 3 live Forge agents needing release management, or the BUD-2027 cycle needing a second Product owner |
| Q4 FY2026 | Product Manager (1st) | 1 | Q4 FY2026 | Roadmap and backlog workload exceeds the CPO's capacity; needed as owner of the first synthesis agent in FY2027 |

### FY2027 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2027 | AI Evaluation and Red Team Lead | 1 | Q2 FY2027 | More than 5 live client-facing agents, US launch in Q1 FY2027 requiring EU AI Act and UK-aligned assurance evidence, SOC 2 Type II scope (COMPANY.md §8) |
| H1 FY2027 | Evaluation and Red-Team Agent | 1 agent | Q2 FY2027 | AI Evaluation and Red Team Lead in post as owner |
| H2 FY2027 | Senior AI Engineer (1st) | 1 | Q3 FY2027 | Open product-owned vulnerabilities above 5 or release train missed twice in a quarter; platform build load from 46 delivery humans (COMPANY.md §6.1) |
| H2 FY2027 | Roadmap and Feedback Synthesis Agent | 1 agent | Q3 FY2027 | Feedback and escalation volume above 40 items a month, or backlog older than 60 days above 20 items |
| H2 FY2027 | Product Manager (2nd) | 1 | Q4 FY2027 | Keep ARR of £6.5m (COMPANY.md §5.1) needs dedicated Keep tooling ownership; backlog above 30 items per Product Manager |

### FY2028 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2028 | Director of Agent Platform | 1 | Q1 FY2028 | Engineering team above 3 people; the CPO cannot be both strategy owner and engineering line manager |
| H1 FY2028 | Senior AI Engineer (2nd) | 1 | Q1 FY2028 | Platform scope across 104 delivery humans (COMPANY.md §6.1); fix and release capacity |
| H1 FY2028 | AI Engineer (1st) | 1 | Q1 FY2028 | Engineering backlog over 60 days of effort |
| H1 FY2028 | Product Manager (3rd) | 1 | Q2 FY2028 | US share of revenue at 30% (COMPANY.md §1) requires pricing, packaging and localisation ownership |
| H1 FY2028 | AI Engineer (2nd), Product Analyst, Product Designer | 3 | Q2 FY2028 | Client-facing agent UX scale (Keep Enterprise), analytics demand and Forge Scale rollout |
| H1 FY2028 | Evaluation and Red-Team Agent (2nd), Release and Vulnerability Tracking Agent, AI Risk Review Pack Agent | 3 agents | Q1 to Q2 FY2028 | Review requests above 8 a month; owners in post |
| H2 FY2028 | Pricing and Packaging Analysis Agent | 1 agent | Q3 FY2028 | Product Analyst in post as owner |

Year-end check: FY2026 = CPO + Product Manager = 2; FY2027 adds AI Evaluation and Red Team Lead, Senior AI Engineer, Product Manager (2nd) = 5; FY2028 adds Director of Agent Platform, Senior AI Engineer (2nd), AI Engineer x2, Product Manager (3rd), Product Analyst, Product Designer = 12. Agents: 0 / 2 / 6 (FY2027: Evaluation and Red-Team, Roadmap and Feedback Synthesis; FY2028 adds second Evaluation and Red-Team, Release and Vulnerability Tracking, AI Risk Review Pack, Pricing and Packaging Analysis). Attrition (14% falling to 11%, COMPANY.md §8) is handled as backfill within the same requisition and is not additive. US hires carry +15% on base (COMPANY.md §6.2); none are planned in Product.

## 6. Interfaces

Topics are those in `core/topics.py` and CONVENTIONS.md §7.

### Product publishes (prefix `product.`)

| Topic | Delivered to | Used for |
|---|---|---|
| `product.roadmap_published` | executive, sales, delivery, marketing | Quarterly roadmap: committed (Now), planned (Next) and themes (Later) |
| `product.release_shipped` | delivery, customer_success, marketing, it_security | A release (fortnightly train or hotfix) is live, with gate evidence and SBOM reference |
| `product.agent_capability_added` | delivery, sales, marketing | A new reusable agent capability is generally available and enablement is ready |
| `product.ai_risk_review_requested` | legal, it_security, data | Material change to a client-facing agent needs the review required by COMPANY.md §9.4 |
| `product.pricing_change_proposed` | finance, sales, executive | Proposal to change a tier, packaging or rate; Finance models, Executive decides |
| `product.vulnerability_fixed` | it_security | A product-owned finding is fixed and ready for re-scan |

Generic: `product.budget_submitted` (to finance) and `product.hire_requested` (to people).

### Product subscribes to (supply and trigger)

| Group | Topics | Why Product needs them |
|---|---|---|
| Strategy and budget | `executive.okrs_set`, `executive.strategy_updated`, `executive.budget_approved`, `executive.pricing_change_approved`, `executive.crisis_declared`, `finance.budget_cycle_opened` | Roadmap alignment, approved envelope, pricing decisions, release freeze or reprioritisation in a crisis, annual budget submission |
| Clients and quality | `customer_success.feedback_received`, `customer_success.support_escalated`, `data.agent_quality_report_published`, `data.data_quality_issue_raised` | Backlog evidence, hotfix triggers, agent quality floor, data defects that block releases |
| Risk, security and law | `legal.ai_risk_review_completed`, `legal.regulatory_change_noted`, `it_security.vulnerability_found` | Release hold or release, regulatory impact on product, fix deadlines |
| Technology | `external.technology_release_published` | New foundation model, framework or tool release to assess |

### Dependencies on other departments (data Product needs, by key)

| From | Needed | Body keys |
|---|---|---|
| Customer Success | Client feedback and escalations | `client_id`, `engagement_id`, `severity`, `summary`, `score` |
| Data | Agent quality scores, data defects | `report_id`, `agent`, `quality_score`, `coverage_pct`, `severity` |
| IT and Security | Vulnerability findings and deadlines | `vulnerability_id`, `severity`, `component`, `release_id`, `exploited_in_wild`, `due_day` |
| Legal | AI risk review result, regulatory change | `review_id`, `risk_tier`, `recommendation`, `conditions`, `dpia_required` |
| Executive | OKRs, strategy, approved budget and pricing, crisis | `objectives`, `budget_gbp`, `severity` |
| Finance | Budget cycle open, pricing model | `cycle_id`, `due_day` |

## 7. Risks and dependencies

| # | Risk | Likelihood / impact | Mitigation and owner |
|---|---|---|---|
| 1 | Key-person dependency: in FY2026 the CPO is the only human until Q4 and decides roadmap, gates and risk triggers alone | High / High | Gate and risk-review decisions are recorded in writing; the CEO is the second approver on any release freeze lift; Delivery's QA Lead reviews G4 evidence in FY2026; Product Manager hired Q4 FY2026 (CPO) |
| 2 | Release of a client-facing agent without an AI risk review (COMPANY.md §9.4) | Medium / Critical | The Release and Vulnerability Tracking Agent (and the CPO until it exists) blocks G4 without a matching `legal.ai_risk_review_completed`; KPI `ai_risk_review_coverage_pct` target 100 (AI Evaluation and Red Team Lead) |
| 3 | Marking one's own homework: builders also evaluating | Medium / High | AI Evaluation and Red Team Lead reports to the CPO, not engineering; Data runs an independent quality harness; annual external red-team (non-people spend) |
| 4 | Foundation-model dependency: provider change, deprecation, price rise or silent behaviour change | Medium / High | Model-agnostic platform; bake-off required for any switch (SOP-PRODUCT-05); Senior AI Engineer owns fallback provider; cost of model change falls about 15% a year (COMPANY.md §8) |
| 5 | Roadmap overload: Delivery and Sales ask for client-specific builds that never generalise | High / Medium | RICE with a minimum of 2.0, 20% capacity reserve, reuse rate tracked as KPI `platform_reuse_pct`; one-off client work goes through Delivery change orders at the rate card (COMPANY.md §3.5) |
| 6 | Unpatched product vulnerabilities breach the IT and Security SLA | Medium / High | Internal due date two days before SLA; fix capacity reserved; exploited vulnerabilities pre-empt the roadmap; owned by Senior AI Engineer (CPO until Q3 FY2027) |
| 7 | Regulatory change (EU AI Act, UK AI principles, UK GDPR) renders an agent non-compliant | Medium / High | `legal.regulatory_change_noted` triggers an impact review within 5 business days (SOP-PRODUCT-08); US launch (Q1 FY2027) adds state-law review |
| 8 | Pricing proposals eroding margin or conflicting with Keep CPI + 2% uplift terms | Medium / Medium | Finance models every proposal; no retrospective effect on signed contracts; Executive decides (COMPANY.md §9.3) |
| 9 | Hiring slippage (45-day time-to-hire) leaves evaluation or engineering understaffed | Medium / Medium | Requisitions one quarter ahead; contractors inside non-people budget if a start slips more than 30 days |
| 10 | Platform R&D spend growing faster than measured reuse savings | Medium / Medium | Platform reuse and cost per capability tracked in `economics.md` section 3; Finance reviews quarterly against §5.4 |

Key dependencies: Data for the evaluation harness and agent register; IT and Security for vulnerability findings, credentials and release scans; Legal for AI risk reviews and regulatory interpretation; Customer Success for feedback; Delivery for platform adoption; People for requisitions; Finance for budget and pricing models.

## 8. Sources

- COMPANY.md §1 (identity, fiscal year, US launch Q1 FY2027, GBP and USD planning rate)
- COMPANY.md §2 (business model, land and expand, leverage model with AI agents)
- COMPANY.md §3, §3.3 and §3.5 (price list, Keep tiers, rate card including the £350 AI agent-day)
- COMPANY.md §4 (delivery model, quality gate)
- COMPANY.md §5.1 and §5.2 (revenue, margin, loaded cost, agent cost range £20k to £35k)
- COMPANY.md §5.4 (product budget envelope: people £220k / £520k / £1,360k; non-people £50k / £100k / £600k; total £270k / £620k / £1,960k)
- COMPANY.md §6, §6.1 and §6.2 (headcount: product 2 / 5 / 12 humans and 0 / 2 / 6 agents; levels and salary bands)
- COMPANY.md §7 (Keep CPI + 2% uplift capped at 7%, change orders)
- COMPANY.md §8 (assumptions: attrition, time-to-hire, agent provisioning, falling model costs, compliance baseline)
- COMPANY.md §9.2 (Anika Rao as Chief Product Officer), §9.3 (delegations of authority) and §9.4 (AI agent governance, AI risk review)
- CONVENTIONS.md §3.1 (blueprint template) and §7 (topic lifecycle chains)
