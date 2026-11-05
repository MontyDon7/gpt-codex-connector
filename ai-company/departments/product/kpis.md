# Product KPIs

Department: `product` (product management and R&D for Compass, Forge and Keep and the internal AI agent platform; roadmap prioritisation, stage gates, AI model evaluation and red-teaming, AI risk review triggers with Legal). Head: Chief Product Officer, Anika Rao (COMPANY.md §9.2). Agent class: `ProductAgent`. All figures are modeled assumptions, not real data.

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| roadmap_delivery_pct | Committed roadmap items delivered in the quarter | percent | 70 | 75 | 80 | higher is better | quarterly | Product Manager (Chief Product Officer until Q4 FY2026) |
| release_gate_first_pass_pct | Release candidates passing gate G4 at first attempt | percent | 80 | 85 | 88 | higher is better | monthly | AI Evaluation and Red Team Lead (Chief Product Officer until Q2 FY2027) |
| agent_quality_score | Mean composite quality score of live client-facing agents, 0 to 100 | score | 85 | 87 | 89 | higher is better | quarterly | AI Evaluation and Red Team Lead (Chief Product Officer until Q2 FY2027) |
| open_critical_high_findings | Open critical or high red-team findings on live client-facing agents | count | 0 | 0 | 0 | lower is better | weekly | AI Evaluation and Red Team Lead (Chief Product Officer until Q2 FY2027) |
| ai_risk_review_coverage_pct | Material changes with an AI risk review requested before release | percent | 100 | 100 | 100 | higher is better | monthly | AI Evaluation and Red Team Lead (Chief Product Officer until Q2 FY2027) |
| vuln_fix_sla_pct | Product-owned vulnerabilities fixed by the internal due date | percent | 90 | 93 | 95 | higher is better | monthly | Senior AI Engineer (Chief Product Officer until Q3 FY2027) |
| release_cadence_adherence_pct | Release trains shipped on the 14-day schedule | percent | 85 | 90 | 92 | higher is better | monthly | Senior AI Engineer (Chief Product Officer until Q3 FY2027) |
| feedback_triage_sla_pct | Client feedback and escalations triaged within SLA | percent | 90 | 93 | 95 | higher is better | weekly | Product Manager (Chief Product Officer until Q4 FY2026) |
| capabilities_shipped | New reusable agent capabilities generally available in the year (cumulative) | count | 6 | 14 | 28 | higher is better | quarterly | Chief Product Officer |
| platform_reuse_pct | Forge engagements using at least one reusable platform component | percent | 40 | 60 | 75 | higher is better | quarterly | Product Manager (Chief Product Officer until Q4 FY2026) |
| eval_cycle_days | Business days from release candidate frozen to evaluation report issued | days | 5 | 4 | 3 | lower is better | monthly | AI Evaluation and Red Team Lead (Chief Product Officer until Q2 FY2027) |
| budget_variance_pct | Absolute Product budget variance, year to date | percent | 5 | 4 | 3 | lower is better | monthly | Chief Product Officer |

Twelve KPIs. The FY2026 targets above are the values exposed in `agent.py` as `KPIS`. Units follow `core.Kpi`: percent values are plain numbers (80, not 0.80), counts are plain numbers, `score` is a number on a 0 to 100 scale, and `days` are business days. `higher_is_better` is False for `open_critical_high_findings`, `eval_cycle_days` and `budget_variance_pct`.

Ownership note: Product has two humans in FY2026 (COMPANY.md §6.1), so the Chief Product Officer owns every KPI until the roles named in brackets are filled (Product Manager Q4 FY2026, AI Evaluation and Red Team Lead Q2 FY2027, Senior AI Engineer Q3 FY2027). From Q1 FY2028 the Director of Agent Platform is accountable for `vuln_fix_sla_pct` and `release_cadence_adherence_pct`, with the Senior AI Engineer remaining the calculation owner. No agent owns a KPI.

## 2. Definitions and formulas

| KPI id | Formula | Notes and exclusions |
|---|---|---|
| roadmap_delivery_pct | committed items reaching gate G4 (or marked done for non-agent work) by quarter end / committed items on `product.roadmap_published` for the quarter x 100 | Committed means the "Now" list. Items removed by an `executive.strategy_updated` decision or an `executive.crisis_declared` freeze are excluded and footnoted. Security fixes in the reserved 20% capacity are not counted. |
| release_gate_first_pass_pct | release candidates that meet every G4 criterion on the first formal evaluation / release candidates evaluated x 100 | G4 criteria in SOP-PRODUCT-03 and SOP-PRODUCT-04: composite score at least 85, regression at most 2 points, zero open critical or high red-team findings, at most 3 open medium findings, AI risk review cleared where required. A re-test after a fix counts as a second attempt. |
| agent_quality_score | mean of the latest composite score (0 to 100) of every live client-facing agent, weighted equally per agent | Source is the Data harness (`data.agent_quality_report_published`, key `quality_score`) with Product's own pre-release scores as fallback. The FY2026 target equals the release gate score of 85. A single agent below 80 triggers remediation, below 70 a release freeze (SOP-PRODUCT-04). |
| open_critical_high_findings | count of red-team findings rated critical or high that are open on agents in production at the Friday cut-off | Target is 0 as a hard policy. A finding with a signed, time-boxed risk acceptance from the CISO is shown separately. Ratings follow IT and Security severity (critical, high, medium, low). |
| ai_risk_review_coverage_pct | material changes where `product.ai_risk_review_requested` was emitted before the release / material changes released x 100 | A change is material if any of triggers RT-1 to RT-8 in SOP-PRODUCT-06 matches. A release without a request is a policy breach reported to the CEO and General Counsel (Callum Fraser) the same day. Rule of record: COMPANY.md §9.4. |
| vuln_fix_sla_pct | product-owned findings with `product.vulnerability_fixed` emitted on or before the internal due date / findings whose internal due date fell in the period x 100 | Internal due date = IT and Security `due_day` minus 2 days (floor of 1 day after receipt). Critical SLA 7 days (1 day if `exploited_in_wild`), high 30, medium 60, low 90 (SOP-PRODUCT-07, mirrors the IT and Security SOP). Findings reopened after a failed re-scan count as late. |
| release_cadence_adherence_pct | release trains shipped within 1 business day of the scheduled date / release trains scheduled x 100 | The train runs every 14 days (SOP-PRODUCT-03). A train cancelled by `executive.crisis_declared` is excluded. Hotfixes are not trains. |
| feedback_triage_sla_pct | items triaged within SLA / items received x 100 | SLA: support escalations of severity high or critical within 1 business day; all other feedback and escalations within 3 business days (SOP-PRODUCT-02). Source topics: `customer_success.feedback_received`, `customer_success.support_escalated`. |
| capabilities_shipped | count of `product.agent_capability_added` messages emitted in the fiscal year | A capability counts once, at general availability, with enablement ready. Model or connector upgrades that do not add a client-visible capability are releases, not capabilities. Targets 6, 14, 28 cumulative for the year. |
| platform_reuse_pct | Forge engagements closed or in delivery in the period that use at least one reusable platform component / Forge engagements in delivery or closed in the period x 100 | Delivery confirms usage at engagement close-out (`delivery.engagement_completed`). Ties to the leverage model in COMPANY.md §2 and to gross margin. |
| eval_cycle_days | business days between candidate freeze and issue of the evaluation report (score, findings, gate recommendation) | Median across the period. Measured for G3 and G4 evaluations. Evaluation compute cap and sample size rules in SOP-PRODUCT-04. |
| budget_variance_pct | abs(actual YTD spend - budget YTD spend) / budget YTD spend x 100 | Budget is the COMPANY.md §5.4 envelope phased monthly. Finance flags a department above 10% or £25k, whichever is lower, via `finance.budget_variance_flagged`. |

Guardrail: no KPI is reported as met on a gate evidence set that was edited after the evaluation ran. Evaluation sets are version-controlled and hashed per release.

## 3. Reporting cadence and data sources

| Cadence | Report | Audience | KPIs covered | Source system (modeled) |
|---|---|---|---|---|
| Weekly (Friday cut-off) | Product operating review | CPO, Product Manager, AI Evaluation and Red Team Lead, Senior AI Engineer | open_critical_high_findings, feedback_triage_sla_pct | Findings register, feedback and escalation queue from `customer_success.feedback_received` and `customer_success.support_escalated` |
| Fortnightly | Release train review | CPO, Delivery, Customer Success, IT and Security | release_cadence_adherence_pct, release_gate_first_pass_pct, eval_cycle_days | Release calendar, evaluation reports, SBOM and scan results |
| Monthly (working day 8) | Product management pack | Executive team, Finance | vuln_fix_sla_pct, ai_risk_review_coverage_pct, budget_variance_pct, eval_cycle_days | Vulnerability tracker (from `it_security.vulnerability_found`), risk-review register, Finance ledger extract |
| Quarterly (within 15 working days of quarter end) | Roadmap and quality review | Executive team, Board (Audit and Risk Committee chair Marcus Ellery for AI risk items) | roadmap_delivery_pct, agent_quality_score, capabilities_shipped, platform_reuse_pct | `product.roadmap_published` history, `data.agent_quality_report_published`, `delivery.engagement_completed` |
| Annual (Q4) | Budget BUD-<year> submission and KPI target reset | Finance, Executive | all | `finance.budget_cycle_opened`, `product.budget_submitted`, `executive.budget_approved` |

Data-quality controls:

1. Every KPI has one named calculation owner (section 1) and a second reviewer; the CPO signs the monthly pack.
2. Gate decisions, risk-review requests and findings are logged with ids (`GATE-`, `AIR-`, `RTF-`) so KPI counts can be re-derived.
3. Restatements of a prior period KPI of more than 2 percentage points are footnoted in the next quarterly review.
4. AI agent outputs (draft roadmap ranking, evaluation scores, pricing models) are labelled as agent-drafted and reviewed by a human before circulation (COMPANY.md §9.4). Agents never pass a gate or release to a client.
5. Quality scores come from the Data harness where available; Product's own scores may not be used to override a lower Data score.

## 4. Links to company targets

| Company target (COMPANY.md) | Product KPI(s) | How Product moves or protects it |
|---|---|---|
| Revenue £6.0m / £19.5m / £46.2m and Forge share of 40% (§5.1) | capabilities_shipped, platform_reuse_pct | Reusable components shorten Forge builds and make Forge Pilot to Forge Build to Forge Scale faster to deliver and price confidently (§3.2). |
| Gross margin 48% / 58% / 64% (§5.1) | platform_reuse_pct, release_cadence_adherence_pct | Reuse lowers delivery days per engagement; stable releases avoid rework in cost of revenue (delivery plus customer_success, §5.1). |
| Keep ARR £1.5m / £6.5m / £17.0m at year end (§5.1) | agent_quality_score, feedback_triage_sla_pct, open_critical_high_findings | Keep retention depends on live agents staying good and on fast response to client feedback; retained-client NRR of 115% and 118% (§5.1). |
| Agent leverage 0.5 rising to 0.5 to 0.65 agents per delivery human (§2) | capabilities_shipped, release_gate_first_pass_pct | New capabilities and a reliable gate let more work be handed to agents without quality loss. |
| AI agent governance and AI risk review (§9.4) | ai_risk_review_coverage_pct, open_critical_high_findings, agent_quality_score | No client-facing agent change is released without Legal's review; critical and high findings never remain open in production. |
| Compliance baseline: ISO 27001, Cyber Essentials Plus, SOC 2 Type II, EU AI Act and UK AI principles alignment (§8) | vuln_fix_sla_pct, ai_risk_review_coverage_pct | Fix SLAs, SBOMs, gate evidence and review records are audit evidence for ISO 27001 and SOC 2. |
| Product budget £270k / £620k / £1,960k (§5.4) | budget_variance_pct | Monthly variance against the envelope; non-budgeted spend above £50k needs the CFO and above £250k the CEO (§9.3). |
| Headcount 2 / 5 / 12 humans and 0 / 2 / 6 agents (§6.1) | eval_cycle_days, release_gate_first_pass_pct | Evaluation cycle time falls from 5 to 3 days as the AI Evaluation and Red Team Lead and evaluation agents come online. |
| US launch Q1 FY2027 (§1, §8) | ai_risk_review_coverage_pct | US state-law and EU exposure review of agent changes before US clients use them. |

Cross-department dependencies: roadmap delivery depends on Delivery adopting `product.release_shipped` and `product.agent_capability_added`; agent quality depends on `data.agent_quality_report_published`; fix SLAs depend on `it_security.vulnerability_found` carrying a correct `due_day`; review coverage depends on Legal returning `legal.ai_risk_review_completed` within its own 5-day target.
