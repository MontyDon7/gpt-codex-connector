# Product Standard Operating Procedures

Department: `product` (agent class `ProductAgent`). Head: Anika Rao, Chief Product Officer (COMPANY.md §9.2). Scope: product management and R&D for Compass, Forge and Keep and the internal AI agent platform; roadmap prioritisation, stage gates, AI model evaluation and red-teaming, AI risk review triggers with Legal. Context: UK-first, US from Q1 FY2027; alignment with the EU AI Act and UK AI regulatory principles for client AI systems, UK GDPR and DPA 2018, ISO 27001, Cyber Essentials Plus and SOC 2 Type II (COMPANY.md §8). All figures are modelled assumptions, not real data.

Team: in FY2026 Product has 2 humans (CPO, plus the Product Manager from Q4) and no registered AI agents (COMPANY.md §6.1). Conventions used throughout:

- `[human]` steps are performed by the role named in the SOP's Owner line, or by the Chief Product Officer when that role is not yet in post (Product Manager from Q4 FY2026, AI Evaluation and Red Team Lead from Q2 FY2027, Senior AI Engineer from Q3 FY2027, Director of Agent Platform from Q1 FY2028). `[agent]` steps are performed by the Product agent named in `blueprint.md` section 4 once it exists; before that, by the CPO using scripted tooling. Agents may draft, score, evaluate, monitor and propose; they may not release anything to a client, pass a stage gate, approve or waive an AI risk review, change a price, sign a contract, approve spend or notify a regulator (COMPANY.md §9.4).
- Money in message bodies is `amount_gbp` ex VAT. US clients are quoted in USD at £1 = $1.27 (COMPANY.md §1).
- SLAs in "business days" exclude UK bank holidays. Sim days are integers from Day 0 = 2026-01-05 (COMPANY.md §1); `due_day` keys are sim days.
- Business IDs follow CONVENTIONS section 4 where they exist (`CL-0001`, `EN-0001`, `BUD-2027`). Product-specific IDs: roadmap `RM-2026Q1`, release `REL-0001`, capability `CAP-0001`, AI risk review `AIR-0001`, red-team finding `RTF-0001`, gate record `GATE-0001`, pricing change `PCH-0001`, feedback item `FB-0001`.
- Thresholds quoted in SOPs are defined once, in section "Constants and thresholds" at the end of this document, and mirrored exactly in `agent.py`.
- Severity vocabulary is `low` | `medium` | `high` | `critical` (CONVENTIONS section 4).

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-PRODUCT-01 | Quarterly roadmap planning and publication | `executive.okrs_set`, `executive.strategy_updated`; quarterly schedule (first Monday of the quarter) | Chief Product Officer | Draft 10 business days before quarter start; published within 5 business days of quarter start; re-plan within 5 business days of a strategy change |
| SOP-PRODUCT-02 | Client feedback and support escalation triage | `customer_success.feedback_received`, `customer_success.support_escalated` | Product Manager (CPO until Q4 FY2026) | High or critical escalation triaged in 1 business day; other items in 3 business days |
| SOP-PRODUCT-03 | Stage gates, release train and capability launch | Release train schedule (every 14 days); gate G4 decision | Chief Product Officer (Senior AI Engineer runs the train from Q3 FY2027) | Train every 14 days; hotfix within 2 business days; capability announced within 2 business days of G4 |
| SOP-PRODUCT-04 | AI model evaluation and red-teaming | `data.agent_quality_report_published`, `data.data_quality_issue_raised`; release candidate frozen | AI Evaluation and Red Team Lead (CPO until Q2 FY2027) | Evaluation report within 5 business days of candidate freeze in FY2026 (4 in FY2027, 3 in FY2028); quality-floor breach actioned within 2 business days |
| SOP-PRODUCT-05 | Technology watch and model change assessment | `external.technology_release_published` | Senior AI Engineer (CPO until Q3 FY2027) | Triage within 2 business days; full bake-off within 10 business days when shortlisted |
| SOP-PRODUCT-06 | AI risk review: triggers, request and close-out | Material-change trigger (RT-1 to RT-8) raised by SOP-03, 04, 05 or 08; `legal.ai_risk_review_completed` | AI Evaluation and Red Team Lead (CPO until Q2 FY2027) | Request within 2 business days of identifying a trigger and always before client release; Legal's target is 5 business days; release hold until outcome |
| SOP-PRODUCT-07 | Vulnerability remediation | `it_security.vulnerability_found` | Senior AI Engineer (CPO until Q3 FY2027) | Fix due 2 days before IT and Security SLA (critical 7 days, 24 hours if exploited; high 30; medium 60; low 90) |
| SOP-PRODUCT-08 | Regulatory change impact on product | `legal.regulatory_change_noted` | Chief Product Officer | Impact assessment within 5 business days |
| SOP-PRODUCT-09 | Pricing and packaging change proposals | Quarterly pricing review (schedule); `executive.pricing_change_approved`; rate-card trigger | Chief Product Officer (Product Manager prepares) | Proposal to Finance within 10 business days of a trigger; implementation tasks within 2 business days of approval |
| SOP-PRODUCT-10 | Annual budget cycle and hiring | `finance.budget_cycle_opened`, `executive.budget_approved`; quarterly capacity review | Chief Product Officer | Budget submitted by day 21 of the cycle; hire request one quarter ahead of start |
| SOP-PRODUCT-11 | Crisis response and release freeze | `executive.crisis_declared`; quality-floor breach | Chief Product Officer | Freeze decision within 4 business hours of declaration; review every 5 business days |

Topic coverage (checked at the end of this document): every subscribed topic is the trigger of at least one SOP above, and every published topic appears in the outputs of at least one SOP.

---

## SOP-PRODUCT-01: Quarterly roadmap planning and publication

**Owner**: Chief Product Officer (Anika Rao), with the Product Manager preparing the backlog and the Roadmap and Feedback Synthesis Agent drafting the ranking from FY2027.
**Trigger**: `executive.okrs_set` and `executive.strategy_updated` (direction from the CEO), and the quarterly schedule: first Monday of each quarter publishes the roadmap; the draft starts 10 business days earlier.
**Inputs**: the OKRs (`objectives`, `quarter`), strategy changes, feedback clusters and escalations from SOP-PRODUCT-02, evaluation findings (SOP-PRODUCT-04), vulnerability backlog (SOP-PRODUCT-07), regulatory impacts (SOP-PRODUCT-08), approved budget, engineering and evaluation capacity in person-weeks, Delivery pipeline of Forge engagements (via Delivery), Sales requests.

### Steps

1. [agent] Collect all candidate items into the backlog with source, evidence (client ids, count of clients affected) and the owner of the underlying need.
2. [agent] Score each item with RICE: reach (clients and engagements affected in the quarter), impact (0.25, 0.5, 1, 2 or 3), confidence (50%, 80% or 100%) and effort in person-weeks: `rice_score = reach x impact x confidence / effort`. Rank by score.
3. [human] Product Manager reviews scores, corrects reach and effort with Delivery and Customer Success, and marks items that are exempt from the minimum score: compliance and regulatory items, security fixes, and items required by an OKR.
4. [human] Apply capacity: reserve 20% for security fixes and client escalations; commit items in score order to the remaining 80% of capacity. Any item below a RICE score of 2.0 is not committed unless exempt.
5. [human] CPO reviews against OKRs and strategy, resolves conflicts with Delivery (Oliver Thackeray), Sales (Rahul Mehta) and Customer Success (Tobias Lindgren), and approves the three lists: committed ("Now", the quarter), planned ("Next", the following quarter) and themes ("Later").
6. [human] CPO confirms that every committed client-facing agent change carries an AI risk review need check (SOP-PRODUCT-06) and a gate plan (SOP-PRODUCT-03).
7. [agent] Publish the roadmap and create tasks and gate records for each committed item.
8. [human] On `executive.strategy_updated`, within 5 business days re-run steps 2 to 5 for any item whose strategic fit changed and republish if any committed item is added, removed or re-dated.

### Outputs and messages

- `product.roadmap_published` (recipient `*`, delivered to executive, sales, delivery, marketing): `roadmap_id`, `quarter`, `committed` (list of `{item_id, title, rice_score, service_line, gate_target}`), `planned` (list of item titles), `themes` (list), `committed_count`, `reserved_capacity_pct` (20), `trigger` (`quarterly` | `okrs_set` | `strategy_updated`), `summary`.
- Tasks `roadmap/<roadmap_id>` and one gate record `GATE-xxxx` per committed item.

### SLA and controls

- SLA: draft complete 10 business days before the quarter starts; published within 5 business days of the quarter starting; re-plan within 5 business days of a strategy change.
- Control: no item is committed without a named human owner, a RICE score or an exemption reason, and a gate target.
- Control: Delivery and Sales may request items; they cannot commit them. One-off client work is handled as a Delivery change order at the rate card (COMPANY.md §3.5), not a roadmap item.
- Evidence: scoring sheet version-controlled; quarterly roadmap delivery measured by KPI `roadmap_delivery_pct`.

### Exceptions and escalation

- Capacity below the committed score list: CPO defers the lowest-ranked item and states this in the publication; an item an OKR depends on escalates to the CEO.
- Conflict between Delivery and Sales priorities: CPO decides on RICE and strategic fit and records the decision; either head may appeal to the CEO.
- No OKRs received by quarter start: publish on the previous quarter's OKRs and flag the gap to the Chief of Staff in Executive.

---

## SOP-PRODUCT-02: Client feedback and support escalation triage

**Owner**: Product Manager (Chief Product Officer until the Product Manager joins in Q4 FY2026).
**Trigger**: `customer_success.feedback_received` (client feedback, CSAT and survey comments) and `customer_success.support_escalated` (a support case Customer Success could not resolve with the client's agent or Keep service).
**Inputs**: `client_id`, `engagement_id`, `severity`, `summary`, `score` (1 to 5 where given), `category`, current agent version in use, evaluation history for that agent, Keep tier of the client (COMPANY.md §3.3).

### Steps

1. [agent] Log the item as `FB-xxxx`, link to the client and agent, and classify it as defect, quality issue, capability request, usability, pricing or compliance.
2. [agent] Cluster with open items on the same theme over the trailing 90 days; flag a cluster once at least 3 different clients are affected.
3. [human] For `customer_success.support_escalated` of severity high or critical, triage within 1 business day: confirm reproducibility, check the latest evaluation and red-team results for the agent, and decide hotfix, workaround, or planned fix.
4. [human] If a defect is a security weakness, hand to SOP-PRODUCT-07; if it needs a change that matches a risk trigger, hand to SOP-PRODUCT-06 before any fix is released.
5. [human] For hotfixes: open the fast path in SOP-PRODUCT-03 (hotfix within 2 business days, evaluation limited to the affected capability plus a regression sample).
6. [human] For clusters and capability requests: score with RICE and add to the backlog for the next planning (SOP-PRODUCT-01). A cluster of 3 or more clients with a quality score below 3 raises priority to "high".
7. [human] Tell Customer Success the decision (workaround, hotfix date, or roadmap quarter) through the task thread so the client is told by their client manager, not by Product.

### Outputs and messages

- `product.release_shipped` (hotfix path only): see SOP-PRODUCT-03 for body keys, with `release_type` = `hotfix`.
- Backlog items `FB-xxxx` with RICE input; tasks for the owner of each decision.
- No client is contacted by Product directly.

### SLA and controls

- SLA: severity high or critical escalations triaged within 1 business day; all other items within 3 business days (KPI `feedback_triage_sla_pct`).
- Control: every escalation has a recorded decision (hotfix, workaround, planned, rejected with reason).
- Control: agents summarise and cluster; they do not decide to ignore an item.

### Exceptions and escalation

- Escalation exposes a data-handling or safety issue with a live client agent: treat as SOP-PRODUCT-11 candidate and notify the CPO immediately; consider disabling the capability for that client with Customer Success.
- Feedback indicating a client-affecting incident: pass to IT and Security via Customer Success; Product participates in post-incident review.
- Repeated feedback from a Keep Enterprise client on the same defect (more than 2 escalations in 30 days): CPO and Chief Customer Officer jointly review within 2 business days.

---

## SOP-PRODUCT-03: Stage gates, release train and capability launch

**Owner**: Chief Product Officer. The Senior AI Engineer runs the release train from Q3 FY2027 and the Director of Agent Platform owns engineering delivery from Q1 FY2028.
**Trigger**: the fortnightly release train (every 14 days; Day 0 is a Monday, trains ship on Thursdays), a G4 decision on a candidate, and the hotfix path from SOP-PRODUCT-02 and SOP-PRODUCT-07.
**Inputs**: gate record `GATE-xxxx`, evaluation report (SOP-PRODUCT-04), red-team findings register, vulnerability scan baseline and SBOM, AI risk review outcome (SOP-PRODUCT-06), rollback plan, release notes draft, enablement pack for Delivery, Sales, Marketing and Customer Success.

### Steps

1. [human] Gate G0 Intake: item exists in the backlog with a named owner (SOP-PRODUCT-01). Exit: item committed or exempt.
2. [human] Gate G1 Problem validated: evidence from at least 3 different clients, or an OKR or regulatory mandate; RICE score at or above 2.0 (or exempt); success measure defined.
3. [human] Gate G2 Design and feasibility: feasibility spike done, cost per agent-run estimated, golden evaluation set of at least 200 cases built, red-team plan written, risk-review trigger check recorded (RT-1 to RT-8).
4. [human] Gate G3 Beta: internal or pilot use only with consent of the client; evaluation composite score at least 80; first red-team round complete with no open critical findings; AI risk review requested if any trigger applies (SOP-PRODUCT-06).
5. [agent] Before the train, assemble the G4 evidence pack: composite score (at least 85), regression versus the live baseline (no worse than 2 points), zero open critical or high findings and at most 3 open medium findings with owner and date, pre-release scan with zero open critical or high vulnerabilities, SBOM stored, AI risk review cleared where required, rollback plan tested, release notes and enablement pack ready.
6. [human] CPO decides G4 go or no-go and records it. For client-facing agents the AI Evaluation and Red Team Lead must sign the evidence, and a Manager or above in Delivery reviews the client impact (COMPANY.md §4 quality gate). No agent passes a gate.
7. [human] Ship the release; for hotfixes run a reduced gate (affected capability plus regression sample, no open critical or high findings, CPO decision) and ship within 2 business days.
8. [agent] Publish the release notice. When the release adds a new reusable capability that is generally available and enablement is ready, publish the capability announcement within 2 business days.
9. [human] Post-release: IT and Security runs the post-release scan (SOP-IT_SECURITY-06); Product monitors the first 14 days for regressions; a regression above the tolerance triggers rollback.

### Outputs and messages

- `product.release_shipped` (recipient `*`, delivered to delivery, customer_success, marketing, it_security): `release_id`, `product`, `version`, `release_type` (`train` | `hotfix`), `change_summary`, `client_facing` (bool), `eval_score`, `gate` (`G4`), `ai_risk_review_id` (or empty), `sbom_ref`, `open_medium_findings`, `severity`, `summary`.
- `product.agent_capability_added` (recipient `*`, delivered to delivery, sales, marketing): `capability_id`, `name`, `service_line`, `release_id`, `eval_score`, `enablement_ready` (bool), `use_cases` (list), `limitations` (list), `summary`.
- Gate records `GATE-xxxx` with decision, evidence references and approver.

### SLA and controls

- SLA: train every 14 days (KPI `release_cadence_adherence_pct`); hotfix within 2 business days; capability announcement within 2 business days of G4.
- Control: a release that touches a client-facing agent without a matching cleared AI risk review is blocked (KPI `ai_risk_review_coverage_pct` target 100).
- Control: G4 evidence is hashed with the release; any edit after the evaluation voids the pass.
- Control: the person who builds a change does not approve its G4 evidence. In FY2026 the CPO decides and Delivery's QA Lead reviews.
- Control: release freeze in force (SOP-PRODUCT-11) overrides the train.

### Exceptions and escalation

- G4 failed: candidate returns to G3; CPO decides whether the train ships without it. A candidate that fails twice triggers a design review within 5 business days.
- Fix needed on live client agent but evidence incomplete: CPO may approve a hotfix with compensating controls (feature flag, client agent restricted) and a 5-business-day follow-up; the exception is logged and reported to the CEO in the monthly pack.
- Missed train: record reason, ship within 5 business days, and brief Customer Success so client commitments are not made on the missed date.

---

## SOP-PRODUCT-04: AI model evaluation and red-teaming

**Owner**: AI Evaluation and Red Team Lead (Chief Product Officer until the Lead joins in Q2 FY2027). Evaluation and Red-Team Agent does the runs from Q2 FY2027.
**Trigger**: `data.agent_quality_report_published` (Data's harness report on registered agents), `data.data_quality_issue_raised` (a defect in a dataset or feed a product component uses), and a candidate frozen for G3 or G4 (SOP-PRODUCT-03).
**Inputs**: candidate agent or component version, golden evaluation sets (at least 200 cases per agent), baseline scores of the live version, red-team playbook (prompt injection, indirect injection through retrieved content, data exfiltration, jailbreak, tool and permission misuse, bias and harmful-output probes, denial of wallet), Data's report body (`report_id`, `agent`, `quality_score`, `coverage_pct`, `under_review`, `rejected`), data defect body (`dataset`, `severity`, `summary`).

### Steps

1. [agent] For each frozen candidate, run the golden set (at least 200 cases, stratified by use case, with at least 20% adversarial or edge cases) and compute the composite score from 0 to 100: weights 40% task accuracy, 20% groundedness and citation correctness, 15% safety and refusal behaviour, 15% robustness to injection and jailbreak, 10% cost and latency within target.
2. [agent] Compare to the live baseline; compute regression in points; run the automated adversarial suite and open findings `RTF-xxxx` with severity.
3. [human] AI Evaluation and Red Team Lead reviews a 10% sample of agent-scored cases (minimum 20) and all high or critical findings, and runs manual adversarial testing for any client-facing agent. Disagreement with the agent score is resolved in favour of the lower score until investigated.
4. [human] Issue the evaluation report with recommendation: pass G3 or G4, fail, or pass with conditions. Gate decisions remain with the CPO (SOP-PRODUCT-03).
5. [agent] On `data.agent_quality_report_published`, compare the reported `quality_score` of each live agent with the quality floor: below 80, open a remediation task within 2 business days; below 70, hand to SOP-PRODUCT-11 for a release freeze on that agent and notify Customer Success and Delivery.
6. [agent] On `data.data_quality_issue_raised` with severity high or critical, identify dependent agents and components, hold their G4 candidates and re-run affected evaluations after the fix.
7. [human] Track evaluation compute against budget: alert the CPO at 90% of the monthly line.
8. [human] Re-test every fixed finding; only a human may close a finding. A finding with a risk acceptance needs the CISO (Wei Zhang) and CPO, expires within 90 days.
9. [human] Material evaluation results (a score drop of more than 5 points versus baseline, a new high or critical class of finding, or a quality-floor breach) are passed to SOP-PRODUCT-06 as a trigger (RT-6).

### Outputs and messages

- Evaluation report `EVAL-xxxx` with: `candidate`, `composite_score`, `baseline_score`, `regression_pts`, `findings_open` by severity, `recommendation`.
- No topic is published from this SOP alone. Its results feed `product.release_shipped` (SOP-PRODUCT-03), `product.ai_risk_review_requested` (SOP-PRODUCT-06) and release freezes (SOP-PRODUCT-11).
- Remediation tasks and findings `RTF-xxxx` visible to Data and IT and Security.

### SLA and controls

- SLA: evaluation report within 5 business days of freeze in FY2026, 4 in FY2027, 3 in FY2028 (KPI `eval_cycle_days`); quality-floor breach actioned within 2 business days.
- Control: release gate thresholds are composite score at least 85, regression at most 2 points, zero open critical or high findings, at most 3 open medium findings.
- Control: golden sets are version-controlled and hashed; sets are refreshed quarterly and never include test cases used in training or prompt tuning.
- Control: agents cannot pass, fail or close; Product's own score never overrides a lower Data score.

### Exceptions and escalation

- Agent and human scores differ by more than 5 points on the sample: Lead re-scores the full sample before the report is issued.
- Harness unavailable (Data): Product evaluates with its own sets, labels the report "provisional", and the G4 decision requires CPO and Data's Chief Data and AI Officer (Dr Emeka Nwosu) acknowledgement.
- A high or critical finding on a live client agent: notify CPO immediately; the CPO decides on feature restriction with Customer Success the same day; IT and Security informed if a vulnerability.

---

## SOP-PRODUCT-05: Technology watch and model change assessment

**Owner**: Senior AI Engineer (Chief Product Officer until the engineer joins in Q3 FY2027), with the AI Evaluation and Red Team Lead for evaluation.
**Trigger**: `external.technology_release_published` (a new foundation model, framework, agent tooling or vendor release; body keys `vendor`, `product`, `version`, `release_type`, `summary`).
**Inputs**: the release notice, current platform dependency list, current model baseline scores, cost per 1,000 tasks, vendor terms and data-processing terms, licence and sub-processor list (via Legal and IT and Security).

### Steps

1. [agent] Classify the release: foundation model, framework or library, tool or connector, security-relevant, deprecation or end-of-life of something in use.
2. [human] Within 2 business days decide: ignore, watch, shortlist for bake-off, or urgent (deprecation, security, price change affecting live agents).
3. [human] For shortlisted models, run a bake-off on the golden sets (at least 200 cases) with identical prompts and tools; measure composite score, cost per 1,000 tasks, latency and refusal behaviour; run the adversarial suite.
4. [human] Decide adoption: a model replaces the incumbent only if its composite score is at least 3 points higher, or equal with at least a 10% lower cost, and the cost per 1,000 tasks does not rise by more than 10%. Fixes for deprecation or security may proceed on parity.
5. [human] Any change of foundation model family, provider or major version in a client-facing agent is a risk trigger (RT-2): hand to SOP-PRODUCT-06 before rollout. Check the vendor's data-processing terms with Legal and the vendor risk assessment with IT and Security (operations vendor process) before any client data is sent.
6. [human] Plan the rollout through the normal gates (SOP-PRODUCT-03), with rollback to the previous model for 30 days.
7. [agent] When a technology release enables a genuinely new client-visible capability, add it to the backlog (SOP-PRODUCT-01); the capability announcement follows G4.

### Outputs and messages

- `product.ai_risk_review_requested` where RT-2 or another trigger applies (see SOP-PRODUCT-06 for body keys).
- Assessment record `TECH-xxxx` (decision, scores, cost, rollout plan); tasks for gates and vendor review.
- No client-visible message is sent until G4.

### SLA and controls

- SLA: triage within 2 business days; full bake-off within 10 business days of shortlisting; urgent items within 1 business day.
- Control: no model switch without a bake-off report, an AI risk review where triggered, and a rollback path.
- Control: no client confidential data in vendor evaluations unless the vendor is approved (operations and IT and Security vendor processes).

### Exceptions and escalation

- A vendor deprecation with less than 60 days' notice for a live agent: CPO escalates to the CEO and Delivery head in 1 business day and runs the fast path with parity acceptance.
- A model release that is materially better and cheaper (more than 10 points better or 30% cheaper): CPO briefs Delivery and Sales; adoption still follows the gates.

---

## SOP-PRODUCT-06: AI risk review: triggers, request and close-out

**Owner**: AI Evaluation and Red Team Lead (Chief Product Officer until the Lead joins in Q2 FY2027). The AI Risk Review Pack Agent drafts requests from FY2028.
**Trigger**: a material-change trigger raised in SOP-PRODUCT-02, 03, 04, 05 or 08, and `legal.ai_risk_review_completed` (Legal's outcome). COMPANY.md §9.4: material changes to client-facing agents require an AI risk review (`product.ai_risk_review_requested` then `legal.ai_risk_review_completed`).
**Inputs**: change description, agent register entry, list of data classes, use-case tags, evaluation and red-team evidence, DPIA status, client contract terms (via Legal), Legal's outcome body (`review_id`, `agent_name`, `client_id`, `risk_tier` = `minimal_risk` | `limited_risk` | `high_risk` | `prohibited`, `dpia_required`, `conditions`, `recommendation` = `cleared_subject_to_standard_controls` | `cleared_with_conditions` | `blocked_pending_gc`, `status`).

### Steps

1. [agent] Check the change against the trigger list. A change is material, and a review is required, if any of the following is true:
   - RT-1: new or widened tool or action permission for a client-facing agent (write access, sending messages, payments, external API calls).
   - RT-2: change of foundation model family, provider or major version in a client-facing agent.
   - RT-3: new data class: personal data, special-category data, or client confidential data not covered by an existing review or DPA.
   - RT-4: increased autonomy: removal or relaxation of a human approval step or the Manager review gate (COMPANY.md §4).
   - RT-5: new use case in a high-risk area (employment, credit scoring, education, essential services, biometric identification, law enforcement, critical infrastructure, safety component) or a practice that may be prohibited.
   - RT-6: guardrail, system prompt or retrieval-source change that alters safety behaviour, or an evaluation composite drop of more than 5 points versus baseline.
   - RT-7: first deployment in a new jurisdiction (US from Q1 FY2027, EU exposure) or a new regulated client sector.
   - RT-8: automated decisions with legal or similarly significant effect on individuals, or new automated profiling.
2. [agent] If any trigger matches, draft the request and the evidence pack; the agent cannot decide that a matching change is not material.
3. [human] Lead reviews, adds the risk narrative and confirms the use-case tags, then CPO approves sending.
4. [human] Emit the request. Place a release hold on the change and record the hold on the gate record (SOP-PRODUCT-03). Legal and IT and Security (credentials, prompt-injection exposure) and Data (register, evaluation harness) review in parallel.
5. [human] On `legal.ai_risk_review_completed`: if `recommendation` is `cleared_subject_to_standard_controls`, lift the hold; if `cleared_with_conditions`, create tasks for each condition (DPIA before go-live where `dpia_required`, user labelling, human review route) and lift the hold only when every condition is evidenced; if `blocked_pending_gc`, or `risk_tier` is `prohibited`, stop the work, notify Delivery and Sales if a client commitment exists, and escalate to the CPO and General Counsel (Callum Fraser).
6. [human] Update the agent register entry with the outcome and conditions (with Data and IT and Security); record in the evidence log used for ISO 27001 and SOC 2.
7. [human] If the change is no longer needed or changes scope materially after the request, re-submit; a review applies only to the change described.

### Outputs and messages

- `product.ai_risk_review_requested` (recipient `*`, delivered to legal, it_security, data): `review_id` (`AIR-xxxx`), `agent_name`, `client_id` (or empty for the platform), `client_facing` (bool), `change_summary`, `triggers` (list of `RT-n`), `data_classes` (list), `use_case_tags` (list), `uses_personal_data` (bool), `automated_decisions` (bool), `affects_employment` (bool), `large_scale` (bool), `eu_exposure` (bool), `eval_score`, `open_findings`, `requested_by`, `severity`, `summary`.
- Release hold and release-lift records on the gate record; condition tasks `AIR-xxxx/<n>`.

### SLA and controls

- SLA: request raised within 2 business days of identifying a trigger and always before the release goes to a client; Legal's target is 5 business days (Legal KPI); the hold stays until the outcome and every condition is evidenced.
- Control: coverage of material changes is a KPI (`ai_risk_review_coverage_pct`, target 100%). A release without a request is reported to the CEO and General Counsel the same day.
- Control: agents never waive or interpret the review; Product never self-certifies.
- Control: records retained for audit; quarterly sample of 10 releases by IT and Security's GRC Lead for completeness.

### Exceptions and escalation

- Urgent security fix that matches a trigger: hotfix may ship with compensating controls if the CPO and CISO approve and the request is raised the same day; Legal is told within 4 hours.
- Disagreement with Legal's conditions: CPO and General Counsel discuss within 2 business days; the CEO decides only if unresolved, and the decision is recorded.
- No Legal outcome after 5 business days: chase through the Legal task queue; after 8 business days the CPO escalates to the CEO. The hold is never lifted by silence.

---

## SOP-PRODUCT-07: Vulnerability remediation

**Owner**: Senior AI Engineer (Chief Product Officer until the engineer joins in Q3 FY2027; Director of Agent Platform accountable from Q1 FY2028).
**Trigger**: `it_security.vulnerability_found` (a finding in a Product-owned component).
**Inputs**: `vulnerability_id`, `severity`, `summary`, `component`, `release_id`, `cvss`, `exploited_in_wild` (bool), `due_day` (IT and Security's SLA date), affected clients and agents, SBOM, existing release train plan.

### Steps

1. [agent] Register the finding, compute the internal due date: IT and Security `due_day` minus 2 days so that re-scan verification fits; never less than 1 day after receipt.
2. [human] Triage within 1 business day: confirm component ownership and exposure; for `exploited_in_wild` or critical, decide compensating controls now (feature flag off, WAF rule with IT and Security, restrict the capability) and notify Customer Success if clients are affected.
3. [human] Plan the fix: critical fixes pre-empt the roadmap (the reserved 20% capacity covers them); high and medium fixes enter the next train; low fixes are batched.
4. [human] Implement and review the fix, run the regression sample and the adversarial subset relevant to the component; check that the fix does not match a risk trigger (RT-1 to RT-8). If it does, hand to SOP-PRODUCT-06.
5. [human] Ship via the hotfix or train path (SOP-PRODUCT-03) and confirm the fix is live.
6. [agent] Emit the fix notice to IT and Security with the release reference.
7. [human] If IT and Security's re-scan fails, reopen the finding, treat as late for the KPI, and escalate to the CPO.
8. [human] If a fix cannot meet the SLA, request a risk acceptance from the CISO with compensating controls (maximum 90 days).

### Outputs and messages

- `product.vulnerability_fixed` (delivered to it_security): `vulnerability_id`, `release_id`, `component`, `fix_summary`, `fixed_day`, `on_time` (bool), `severity`, `summary`.
- `product.release_shipped` for the hotfix or train that carries the fix (SOP-PRODUCT-03 body keys).
- Remediation task `vuln/<vulnerability_id>` with internal due date.

### SLA and controls

- SLA: remediation SLAs mirror IT and Security: critical 7 days (24 hours if actively exploited), high 30 days, medium 60 days, low 90 days. Planned fix duration targets: critical 4 days (1 day if exploited), high 14, medium 30, low 60. Product's internal due date is 2 days before the IT and Security date (KPI `vuln_fix_sla_pct`).
- Control: only a human confirms a fix; the Release and Vulnerability Tracking Agent only tracks the clock.
- Control: open critical or high findings block G4 for the affected component (SOP-PRODUCT-03).

### Exceptions and escalation

- Critical exploited vulnerability with no fix within 24 hours: CPO and CISO decide with the CEO whether to take the capability offline; an incident under SOP-IT_SECURITY-01 may be opened by IT and Security, and `executive.crisis_declared` may follow (SOP-PRODUCT-11).
- Vulnerability in a third-party dependency with no upstream fix: compensating control and a CISO risk acceptance, with weekly review until fixed.
- Findings arriving faster than capacity: CPO re-plans the reserved 20% and reports the shortfall to the CEO and the Chief Information Security Officer.

---

## SOP-PRODUCT-08: Regulatory change impact on product

**Owner**: Chief Product Officer, with Legal (General Counsel) interpreting the law.
**Trigger**: `legal.regulatory_change_noted` (Legal has assessed a new or changed regulation; body keys `regulation_id`, `regulator`, `title`, `severity`, `owners`, `impact_areas`, `effective_day`, `summary`).
**Inputs**: the Legal note, the register of live agents and components, data flows, client sectors, current evaluation and red-team evidence, EU AI Act, UK AI principles, UK GDPR and DPA 2018, US state-law developments from FY2027.

### Steps

1. [agent] Map the regulation to agents, components, data classes and client sectors; list candidate impacts.
2. [human] Within 5 business days, CPO reviews with the AI Evaluation and Red Team Lead and Legal: no impact, product change needed, evaluation or red-team change needed, or client communication needed.
3. [human] Where a product change is needed, create a backlog item exempt from the minimum RICE score (compliance) with the regulatory effective date as the deadline; add to the next roadmap (SOP-PRODUCT-01) or sooner for a deadline inside the quarter.
4. [human] If the change affects how a client-facing agent behaves, treat as a risk trigger (RT-5, RT-7 or RT-8 as applicable) and run SOP-PRODUCT-06.
5. [human] Update evaluation golden sets and the red-team playbook for the new requirement (SOP-PRODUCT-04).
6. [human] Tell Delivery and Customer Success through the task thread when clients need to be informed; Legal and the client manager lead any client message.

### Outputs and messages

- `product.ai_risk_review_requested` where a trigger applies (SOP-PRODUCT-06 body keys).
- Impact assessment `REG-xxxx` (decision, owner, due day) and backlog items; updated evaluation and red-team plans.
- If the regulatory effective date moves a committed item, a re-plan under SOP-PRODUCT-01 and `product.roadmap_published`.

### SLA and controls

- SLA: impact assessment within 5 business days of the Legal note; compliance backlog items scheduled to land at least 10 business days before the effective date.
- Control: product never interprets the regulation itself; interpretation rests with Legal.
- Control: assessment record retained for ISO 27001 and SOC 2 evidence.

### Exceptions and escalation

- Effective date inside 30 days and the change cannot be shipped: CPO escalates to the CEO and General Counsel in 1 business day with options (restrict capability, suspend for affected clients, interim controls).
- Legal severity `high` or `critical`: assessment within 2 business days.

---

## SOP-PRODUCT-09: Pricing and packaging change proposals

**Owner**: Chief Product Officer; the Product Manager prepares the proposal and the Pricing and Packaging Analysis Agent drafts the models from FY2028. Finance models, Executive decides. Product never changes a price.
**Trigger**: the quarterly pricing review (first month of each quarter), `executive.pricing_change_approved` (the CEO's decision, for implementation tasks), and a rate-card trigger (agent-day economics: break-even above 90 billed agent-days per agent-year, or margin on a 50%-billed agent below 30%).
**Inputs**: price list (COMPANY.md §3), rate card (§3.5), Keep terms (CPI + 2% uplift capped at 7%, §7), win rate and discount data from Sales and Finance, delivery cost per tier, agent-day cost, competitor and client signals, reuse savings (`economics.md` section 3).

### Steps

1. [human] Product Manager identifies the change: tier definition, packaging (what is included in Keep Essential, Plus or Enterprise, support days), a new option, or a rate-card adjustment. A list-price change must state which tiers and lines.
2. [agent] Build the model: revenue effect per 1% price change by line, effect on Keep uplift, margin per tier, and effect on discount mix. Check the guardrail: modelled gross margin at or above the company gross margin target for the year (48%, 58%, 64%, COMPANY.md §5.1).
3. [human] CPO reviews, checks for conflicts with signed multi-year Keep terms (Legal consulted) and for client communication implications.
4. [human] Emit the proposal to Finance, Sales and Executive. Finance models revenue, margin and cash (SOP-FINANCE-02) and gives the finance view to the CEO; Sales gives win-rate evidence.
5. [human] CEO decides (COMPANY.md §9.3) and Executive emits `executive.pricing_change_approved` if approved. Changes never apply retrospectively to signed contracts.
6. [human] On `executive.pricing_change_approved`: within 2 business days create tasks to update packaging documents, enablement for Sales and Delivery, the evaluation of cost per agent-run if the pricing depends on a capability, and the rate-card references in the platform. The price book itself is updated by Finance.

### Outputs and messages

- `product.pricing_change_proposed` (delivered to finance, sales, executive): `change_id` (`PCH-xxxx`), `service_line`, `tier`, `change_type` (`list_price` | `packaging` | `rate_card` | `new_option`), `current_price_gbp`, `proposed_price_gbp`, `change_pct`, `margin_pct`, `annual_revenue_effect_gbp`, `effective_day`, `rationale`, `severity`, `summary`.
- Tasks for enablement and packaging updates after approval.

### SLA and controls

- SLA: proposal to Finance within 10 business days of a trigger; implementation tasks within 2 business days of approval.
- Control: a proposal that conflicts with the guardrail (margin below target) needs the CPO to state the strategic reason and CFO and CEO agreement (COMPANY.md §9.3).
- Control: the proposal carries the model and assumptions; Finance re-performs the model before the CEO sees it.

### Exceptions and escalation

- A price change that would affect signed clients: General Counsel consulted before the proposal is sent.
- Competitive or client pressure for an urgent discount scheme: handled by Sales and Finance through the deal desk (SOP-FINANCE-02); Product contributes the product view only.

---

## SOP-PRODUCT-10: Annual budget cycle and hiring

**Owner**: Chief Product Officer.
**Trigger**: `finance.budget_cycle_opened` (the annual cycle opens on 1 October, id `BUD-<next year>`), `executive.budget_approved` (the approved envelope), and the quarterly capacity review (first Monday of each quarter).
**Inputs**: `cycle_id`, `due_day`, COMPANY.md §5.4 envelope and headcount (§6.1), roadmap needs, hiring triggers in `blueprint.md` section 5, current and forecast spend by line, agent cost per agent-year, utilisation of engineering and evaluation capacity.

### Steps

1. [agent] On `finance.budget_cycle_opened`, build the draft: people cost from the hiring plan (loaded base x 1.28, weighted by start quarter), non-people by line (agents, evaluation compute, platform R&D, tooling, research, external assurance, training, contingency).
2. [human] CPO checks the draft against the COMPANY.md §5.4 envelope: people plus non-people for FY2027 is £620k (people £520k, non-people £100k) and for FY2028 £1,960k (people £1,360k, non-people £600k); explains and justifies any difference.
3. [human] Submit by day 21 of the cycle. Items beyond the envelope go as separate, ranked options, never inside the base number.
4. [human] On `executive.budget_approved`, load the approved envelope, update spend tracking, and update the hiring plan; where the budget is cut, re-rank roadmap items and tell Delivery and Sales what moves.
5. [human] Hire requests: at each quarterly capacity review check each trigger in `blueprint.md` section 5 (for example open backlog above 15 items, open product-owned vulnerabilities above 5, more than 5 live client-facing agents); raise a request one quarter ahead of the planned start.
6. [human] Monthly: track variance against the envelope; Finance raises `finance.budget_variance_flagged` above 10% or £25k; CPO explains to the CFO within 3 business days.
7. [human] Spend authority: within budget the CPO approves; non-budgeted spend above £50k needs the CFO and above £250k the CEO (COMPANY.md §9.3).

### Outputs and messages

- `product.budget_submitted` (delivered to finance): `cycle_id`, `department` (`product`), `people_gbp`, `non_people_gbp`, `amount_gbp` (total), `headcount_plan` (humans and agents), `options` (list of ranked extras with amount), `summary`.
- `product.hire_requested` (delivered to people): `role` (blueprint title), `level` (level key), `count`, `start_quarter`, `reason`, `trigger`, `salary_band_gbp`, `summary`. Raised for: Product Manager (request Q3 FY2026, start Q4); AI Evaluation and Red Team Lead (request Q1 FY2027, start Q2); Senior AI Engineer (request Q2 FY2027, start Q3); Product Manager (2nd; request Q3 FY2027, start Q4); Director of Agent Platform, Senior AI Engineer (2nd), AI Engineer (1st) (request Q4 FY2027, start Q1 FY2028); Product Manager (3rd), AI Engineer (2nd), Product Analyst, Product Designer (request Q1 FY2028, start Q2).
- Updated tracking sheet and hiring plan.

### SLA and controls

- SLA: budget submitted by day 21 of the cycle; hire request raised one quarter before the start date; variance explanation within 3 business days of a flag.
- Control: every hire needs the CEO's `executive.headcount_approved` record even inside the budget (COMPANY.md §9.3); the CPO does not extend offers.
- Control: no hire or spend above the envelope by assumption; agents draft and track only.

### Exceptions and escalation

- Draft exceeds the envelope: CPO removes lowest-ranked items first, keeping security, assurance and compliance spend last to cut; the CFO decides on any residual request.
- Requisition slips beyond 45 days: contractor bridge inside the non-people contingency up to £20k; above that, CFO approval.

---

## SOP-PRODUCT-11: Crisis response and release freeze

**Owner**: Chief Product Officer.
**Trigger**: `executive.crisis_declared` (the CEO declares a crisis; body keys `crisis_id`, `severity`, `category`, `summary`), a quality-floor breach (agent below 70, SOP-PRODUCT-04), or a CPO decision after a critical finding on a live agent.
**Inputs**: crisis body, live agent register, release calendar, open critical and high findings, client exposure by agent (Customer Success), evaluation status.

### Steps

1. [human] Within 4 business hours decide the product position: no change, freeze non-essential releases, freeze one capability or agent, or disable a capability for affected clients (with Customer Success).
2. [human] A freeze stops the release train and G3 and G4 decisions for the affected scope; hotfixes and security fixes continue under the reduced gate (SOP-PRODUCT-03).
3. [agent] List live clients and agents in scope, open findings, and in-flight releases; draft the position note for the CEO and affected department heads.
4. [human] If the crisis is a security or data incident, support IT and Security (CISO) and Legal: provide component information, logs and fix options; do not communicate with clients or regulators directly.
5. [human] Review the freeze every 5 business days; lift only when the cause is resolved, evidence is recorded, and (for the CPO's own freezes) the CEO agrees when severity is critical.
6. [human] After lifting, hold a post-incident review within 10 business days: root cause, gate gaps, evaluation additions, roadmap changes.
7. [human] Re-plan the roadmap if the freeze exceeds one train (SOP-PRODUCT-01).

### Outputs and messages

- When a freeze or lift changes committed dates: `product.roadmap_published` (SOP-PRODUCT-01 body keys, `trigger` = `crisis`), delivered to executive, sales, delivery and marketing.
- When a freeze stops a release scheduled for clients: no `product.release_shipped` is emitted for the held release; the task thread records the hold.
- Freeze record `FRZ-xxxx` (scope, reason, decision-maker, review dates) and tasks for the post-incident review.

### SLA and controls

- SLA: freeze decision within 4 business hours of declaration; review every 5 business days; post-incident review within 10 business days of lifting.
- Control: a freeze lift needs the CPO and, for a critical crisis, the CEO.
- Control: agents list and draft; they do not freeze, lift or communicate externally.

### Exceptions and escalation

- Crisis arising from a client-facing agent behaving unsafely: disable the capability for affected clients immediately (CPO decision, Customer Success informed) and open an AI risk review (SOP-PRODUCT-06) before re-enabling.
- Crisis unrelated to Product (for example a finance or people crisis): confirm no impact, keep the release train, and offer capacity to the crisis owner if asked.

---

## Constants and thresholds

These values are defined once here and mirrored exactly as constants in `agent.py`.

| Constant | Value | Used in |
|---|---|---|
| ROADMAP_MIN_RICE | 2.0 (minimum RICE score to commit an item; compliance, security and OKR-required items exempt) | SOP-01, SOP-03 G1 |
| RICE impact scale | 0.25, 0.5, 1, 2, 3 | SOP-01 |
| RICE confidence scale | 0.5, 0.8, 1.0 | SOP-01 |
| RESERVED_CAPACITY_PCT | 20 (security fixes and client escalations); committed capacity 80 | SOP-01, SOP-07 |
| CLUSTER_MIN_CLIENTS | 3 distinct clients within 90 days make a feedback cluster; also the G1 evidence minimum | SOP-02, SOP-03 |
| TRIAGE_SLA_DAYS_HIGH | 1 business day (severity high or critical) | SOP-02 |
| TRIAGE_SLA_DAYS_STANDARD | 3 business days | SOP-02 |
| RELEASE_TRAIN_DAYS | 14 | SOP-03 |
| HOTFIX_SLA_DAYS | 2 business days | SOP-02, SOP-03, SOP-07 |
| EVAL_MIN_CASES | 200 golden-set cases per agent | SOP-03, SOP-04 |
| BETA_EVAL_SCORE | 80 (gate G3) | SOP-03 |
| RELEASE_EVAL_SCORE | 85 (gate G4) | SOP-03, SOP-04 |
| REGRESSION_TOLERANCE_PTS | 2 | SOP-03, SOP-04 |
| MAX_OPEN_MEDIUM_FINDINGS | 3 at G4; zero open critical or high | SOP-03, SOP-04 |
| AGENT_QUALITY_FLOOR | 80 (remediation task within 2 business days) | SOP-04 |
| AGENT_QUALITY_FREEZE | 70 (release freeze for that agent) | SOP-04, SOP-11 |
| REVIEW_SCORE_DROP_PTS | 5 (evaluation drop that triggers an AI risk review, RT-6) | SOP-04, SOP-06 |
| EVAL_COMPUTE_ALERT_PCT | 90 of the monthly evaluation compute line | SOP-04 |
| MODEL_SWITCH_MARGIN_PTS | 3 (composite score advantage to replace a model) | SOP-05 |
| MODEL_SWITCH_MAX_COST_INCREASE_PCT | 10 (cost per 1,000 tasks) | SOP-05 |
| TECH_TRIAGE_DAYS | 2 business days | SOP-05 |
| RISK_REVIEW_REQUEST_DAYS | 2 business days from identifying a trigger | SOP-06 |
| RISK_REVIEW_LEGAL_TARGET_DAYS | 5 business days (Legal's target; escalate to CEO at 8) | SOP-06 |
| RISK_TRIGGERS | RT-1 to RT-8 as listed in SOP-06 | SOP-06 |
| VULN_SLA_DAYS | critical 7, high 30, medium 60, low 90; actively exploited 1 | SOP-07 |
| VULN_VERIFY_BUFFER_DAYS | 2 (internal due date = IT and Security due date minus 2, minimum 1 day) | SOP-07 |
| VULN_FIX_PLAN_DAYS | critical 4 (exploited 1), high 14, medium 30, low 60 | SOP-07 |
| REGULATORY_IMPACT_DAYS | 5 business days (2 if severity high or critical) | SOP-08 |
| PRICING_PROPOSAL_DAYS | 10 business days | SOP-09 |
| AGENT_DAY_RATE_GBP | 350 (COMPANY.md §3.5) | SOP-09 |
| AGENT_DAY_BREAKEVEN_MAX_DAYS | 90 billed agent-days per agent-year (rate-card review trigger) | SOP-09 |
| AGENT_DAY_MIN_MARGIN_PCT | 30 (margin on a 50%-billed agent; rate-card review trigger) | SOP-09 |
| PRICING_MIN_MARGIN_PCT | 48 / 58 / 64 for FY2026 / FY2027 / FY2028 (company gross margin target) | SOP-09 |
| BUDGET_SUBMISSION_DAY | 21 (day of the cycle) | SOP-10 |
| BUDGET_ENVELOPE_GBP_K | total 270 / 620 / 1,960; people 220 / 520 / 1,360; non-people 50 / 100 / 600 (COMPANY.md §5.4) | SOP-10 |
| NON_BUDGETED_SPEND_CFO_GBP / CEO_GBP | 50,000 / 250,000 (COMPANY.md §9.3) | SOP-10 |
| CRISIS_FREEZE_HOURS | 4 business hours | SOP-11 |
| CRISIS_REVIEW_DAYS | 5 business days | SOP-11 |

## Topic coverage

| Topic | Direction | SOP |
|---|---|---|
| `customer_success.feedback_received` | subscribe | SOP-PRODUCT-02 |
| `customer_success.support_escalated` | subscribe | SOP-PRODUCT-02 |
| `data.agent_quality_report_published` | subscribe | SOP-PRODUCT-04 |
| `data.data_quality_issue_raised` | subscribe | SOP-PRODUCT-04 |
| `executive.budget_approved` | subscribe | SOP-PRODUCT-10 |
| `executive.crisis_declared` | subscribe | SOP-PRODUCT-11 |
| `executive.okrs_set` | subscribe | SOP-PRODUCT-01 |
| `executive.pricing_change_approved` | subscribe | SOP-PRODUCT-09 |
| `executive.strategy_updated` | subscribe | SOP-PRODUCT-01 |
| `external.technology_release_published` | subscribe | SOP-PRODUCT-05 |
| `finance.budget_cycle_opened` | subscribe | SOP-PRODUCT-10 |
| `it_security.vulnerability_found` | subscribe | SOP-PRODUCT-07 |
| `legal.ai_risk_review_completed` | subscribe | SOP-PRODUCT-06 |
| `legal.regulatory_change_noted` | subscribe | SOP-PRODUCT-08 |
| `product.roadmap_published` | publish | SOP-PRODUCT-01 (also SOP-PRODUCT-08, SOP-PRODUCT-11) |
| `product.release_shipped` | publish | SOP-PRODUCT-03 (also SOP-PRODUCT-02, SOP-PRODUCT-07) |
| `product.agent_capability_added` | publish | SOP-PRODUCT-03 |
| `product.ai_risk_review_requested` | publish | SOP-PRODUCT-06 (also SOP-PRODUCT-05, SOP-PRODUCT-08) |
| `product.pricing_change_proposed` | publish | SOP-PRODUCT-09 |
| `product.vulnerability_fixed` | publish | SOP-PRODUCT-07 |
| `product.budget_submitted` | publish | SOP-PRODUCT-10 |
| `product.hire_requested` | publish | SOP-PRODUCT-10 |
