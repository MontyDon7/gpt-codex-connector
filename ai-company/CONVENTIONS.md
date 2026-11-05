# CONVENTIONS: Binding Contract for Department Teams

This document is binding. Facts live in `COMPANY.md`; framework code lives in `core/` (do not edit `core/`, `COMPANY.md` or this file; raise conflicts in your final report instead). All code is Python 3.13, **standard library only**, tests use `unittest` (pytest is not available).

## 1. Departments and ownership

Exactly 12 department ids (also `core.DEPARTMENTS`): `executive, sales, marketing, delivery, finance, people, legal, it_security, operations, customer_success, product, data`.

A department team owns **only** `ai-company/departments/<id>/**`. The `__init__.py` files (`departments/__init__.py`, `departments/<id>/__init__.py`, `departments/<id>/tests/__init__.py`) already exist; leave them empty.

## 2. Required file layout (per department `<id>`)

```
ai-company/departments/<id>/
  __init__.py            (exists, do not edit)
  blueprint.md           org chart, roles, hiring plan
  sops.md                standard operating procedures
  kpis.md                KPI definitions and targets
  economics.md           budget, pricing, unit economics
  agent.py               class <Id>Agent(DepartmentAgent) + build_agent(llm, bus, clock, log)
  workflows.py           scenario functions that seed Messages
  tests/__init__.py      (exists)
  tests/test_<id>.py     unittest tests
```

Class name = CamelCase of the id plus `Agent`: `SalesAgent`, `ItSecurityAgent`, `CustomerSuccessAgent` (`core.class_name_for(id)` returns it). Additional helper modules are allowed (e.g. `departments/<id>/models.py`) but the files above are mandatory.

## 3. Markdown document templates (required headings, in this order)

Use the exact heading text. You may add `###` subsections and extra `##` sections AFTER the required ones. Write real, specific content: tables with numbers, named roles, concrete thresholds. No placeholders, no "TBD", no lorem ipsum.

### 3.1 `blueprint.md`
```
# <Department Name> Department Blueprint
## 1. Mission and scope
## 2. Org chart            (indented tree or mermaid; head at top; every role in section 3 appears)
## 3. Roles                (table: Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities)
## 4. AI agents            (table: Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3)
## 5. Hiring plan          (quarterly for FY2026, then FY2027 and FY2028 by half-year; role, count, start quarter, trigger)
## 6. Interfaces           (which departments you depend on / serve; reference topics from CONVENTIONS section 7)
## 7. Risks and dependencies
## 8. Sources              (list of COMPANY.md sections cited)
```
Role-table Y1/Y2/Y3 sums MUST equal your row in COMPANY.md §6.1 (humans), agent-table sums must equal the agent columns. Level keys and salary bands must come from COMPANY.md §6.2.

### 3.2 `sops.md`
```
# <Department Name> Standard Operating Procedures
## Overview               (table: SOP id | Title | Trigger | Owner | SLA)
## SOP-<ID>-01: <Title>   (repeat; at least 8 SOPs; <ID> = upper-case dept id, e.g. SOP-IT_SECURITY-01)
   **Owner** / **Trigger** (a topic name from section 7 or a schedule) / **Inputs**
   ### Steps               (numbered; mark each step [human] or [agent])
   ### Outputs and messages (topics emitted with the body keys used)
   ### SLA and controls
   ### Exceptions and escalation
```
Every topic your department subscribes to in section 7 must be the trigger of at least one SOP, and every topic you publish must appear in at least one SOP's outputs.

### 3.3 `kpis.md`
```
# <Department Name> KPIs
## 1. KPI summary          (table: KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner)
## 2. Definitions and formulas
## 3. Reporting cadence and data sources
## 4. Links to company targets   (how these KPIs roll up to COMPANY.md §5; cite sections)
```
At least 8 KPIs. `KPI id` is snake_case. The same KPIs (FY2026 target) must be exposed in `agent.py` as `KPIS: list[core.Kpi]`.

### 3.4 `economics.md`
```
# <Department Name> Economics
## 1. Budget               (table FY2026/FY2027/FY2028 in £k: people, non-people by line, total)
## 2. Headcount cost build-up   (role x average headcount x loaded cost; loaded = base x 1.28)
## 3. Pricing and unit economics (department-appropriate: price lists, cost per unit, margins, CAC, DSO, cost per hire, etc.)
## 4. Assumptions
## 5. Reconciliation to COMPANY.md   (state the §5.4 envelope row and show your totals match it to within £5k, or explain the delta)
```
The department total must match your row in COMPANY.md §5.4. Numbers must be internally consistent (rows sum, units stated, GBP unless stated).

## 4. Naming rules

| Thing | Rule | Example |
|---|---|---|
| Department id | lower snake_case, exactly the 12 above | `customer_success` |
| Topic | `<publisher_dept>.<event>`; event is past-tense snake_case | `sales.deal_won` |
| Agent `name` | equals the department id | `"sales"` |
| Message sender | the department id (or `external` for outside-world events) | `"sales"` |
| Document ids | prefix + zero-padded number (below) | `CL-0007` |
| SOP ids | `SOP-<DEPT_ID_UPPER>-NN` | `SOP-SALES-03` |
| Scenario functions | `scenario_<snake_name>` | `scenario_inbound_lead_to_win` |
| Test files | `tests/test_<id>.py`, classes `*Tests` | `test_sales.py` |
| Dates in docs | ISO 8601 `2026-01-05`; sim time in code is an `int` day (`clock.day`) | |
| Money | GBP numbers in code are plain `int`/`float` pounds, field suffix `_gbp`; docs use £ | `amount_gbp: 260000` |

Business ID formats (zero-padded): client `CL-0001`, lead `LD-00001`, deal `DL-0001`, proposal `PR-0001`, contract `CT-0001`, engagement `EN-0001`, invoice `INV-2026-0001`, requisition `REQ-0001`, incident `INC-0001`, vendor `VN-0001`, employee `EMP-0001`, budget cycle `BUD-2026`.

Use these shared body keys whenever applicable: `client_id`, `client_name`, `deal_id`, `proposal_id`, `contract_id`, `engagement_id`, `invoice_id`, `amount_gbp`, `service_line` (`compass`|`forge`|`keep`), `tier` (e.g. `forge_build`), `department`, `summary`, `due_day` (int sim day), `severity` (`low`|`medium`|`high`|`critical`). A message body is a plain JSON-serialisable `dict`.

## 5. Citing COMPANY.md facts

- Never restate a company fact from memory; copy it from `COMPANY.md` exactly (names, prices, headcount, margins).
- Cite as `(COMPANY.md §5.1)` inline in docs, and list cited sections in blueprint section 8.
- In code, put facts in module constants with a comment `# COMPANY.md §3.2`. Do not invent prices, tiers, people names or targets that conflict with COMPANY.md; derived numbers must be shown with their derivation.
- If a fact you need does not exist, derive it from existing facts and state the assumption in `economics.md` section 4. Invented clients and people are allowed only if fictional and not real firms.

## 6. Agent contract (`agent.py`)

```python
from core import DepartmentAgent, Kpi, Message, Role, class_name_for, publishes_for, subscribes_for

KPIS = [Kpi("win_rate", "percent", 30.0, None), ...]       # FY2026 targets from kpis.md

class SalesAgent(DepartmentAgent):
    SUBSCRIBES = subscribes_for("sales")                    # MUST use the map, never hand-copy
    PUBLISHES = publishes_for("sales")

    def handle(self, message: Message) -> list[Message]:    # route on message.topic
        ...
    def tick(self) -> list[Message]:                        # optional; cadences via self.clock
        ...

def build_agent(llm, bus, clock, log) -> SalesAgent:
    role = Role("Chief Revenue Officer", "sales", "head", (1, 1, 1), (140000, 200000), "Chief Executive Officer")
    return SalesAgent("sales", "sales", role, llm, bus, clock, log)
```

Rules:
1. `build_agent` only constructs; it must NOT register with the bus (`Company` does) and must not publish.
2. `name == department == <id>`.
3. `handle` must act on EVERY topic in `SUBSCRIBES` (unknown topics: log and return `[]`). It must be deterministic given inputs, `clock`, and the (Mock) LLM, and never raise on a well-formed message.
4. Use helpers: `self.emit(topic, body, recipient="*", reply_to=None, delay_days=0)` (publishes + logs; enforces the topic prefix and the PUBLISHES list), `self.reply(msg, topic, body)`, `self.log_event(topic, summary, **data)` (use topics under `<id>.activity.*` for non-message events), `self.ask_llm(prompt)` (system prompt is built for you), `self.create_task(...)`, `self.state` (free-form dict).
5. Only publish topics from section 7. Need a private topic? Use the `<id>.internal.*` namespace (not validated, not delivered to other departments unless addressed as a direct message).
6. LLM use must be optional: all logic must work with `core.MockLLM()` (default). Never call the network.
7. Randomness: none, or `random.Random(<fixed seed string>)` instance owned by the agent. No wall-clock time, no `uuid4`: ids come from `self.bus.next_id()` or from deterministic counters in `self.state`.
8. Cadences (monthly close, quarterly review, annual budget) are driven from `tick()` using `self.clock` (`clock.date`, `clock.every(n)`, `clock.is_month_start`), emitting only topics you own.
9. Prefer replying with the cross-department business-ID keys from section 4 so downstream agents can correlate (e.g. every message in a deal chain carries `deal_id`; engagement chain carries `engagement_id`).

## 7. Cross-department messaging

### 7.1 Rules
- Topic = `<publisher_dept>.<event>`; only the publisher department may emit it. Direct delivery: `recipient="<dept>"`; broadcast: `recipient="*"` (delivered to all subscribers except the sender). **Default to `"*"`**; use direct recipients for replies.
- The bus is delivered in rounds; a message emitted while handling is delivered in the next round of the same tick (up to 10 rounds per tick), then carried into the next tick. Use `delay_days` for future-dated actions.
- The map in `core/topics.py` is authoritative (`TOPIC_SUBSCRIBERS`, `EXTERNAL_TOPICS`, `publishes_for`, `subscribes_for`). If this table and the code differ, the code wins and the discrepancy goes in your report.
- Outside-world events enter through `external.*` topics (sender `external`); see 7.4.

### 7.2 Lifecycle chains (the spine of the business)

**Lead to cash to renewal**
1. `external.lead_inbound` -> marketing qualifies -> `marketing.lead_generated` (sales, data)
2. sales -> `sales.lead_qualified` (marketing, delivery, data) -> `sales.proposal_requested` (delivery, finance)
3. delivery -> `delivery.scoping_completed` (sales, finance); finance -> `finance.pricing_check_completed` (sales)
4. sales -> `sales.security_review_requested` (it_security, legal) -> `it_security.security_questionnaire_completed`, `legal.security_terms_reviewed`
5. sales -> `sales.proposal_sent` (executive, data); deals >= £500k: `sales.deal_approval_requested` -> `executive.deal_decision_made` (COMPANY.md §9.3)
6. sales -> `sales.deal_won` (legal, finance, delivery, customer_success, executive, data) or `sales.deal_lost`
7. legal -> `legal.contract_drafted` -> `legal.contract_signed` (finance, delivery, sales, customer_success)
8. finance -> `finance.billing_schedule_created` (delivery, customer_success); delivery -> `delivery.staffing_requested` (people, operations) -> `delivery.engagement_kickoff` (customer_success, finance, operations, data)
9. delivery -> `delivery.milestone_reached` (finance, customer_success) -> finance `finance.invoice_issued` (customer_success, data)
10. client pays: `external.client_payment_received` -> `finance.payment_received` (sales, customer_success, data); or not: `finance.invoice_overdue` (customer_success, legal, sales) -> `finance.collections_escalated` (legal, executive)
11. delivery -> `delivery.scope_change_requested` (sales, finance, legal) for change orders; `delivery.engagement_completed` (finance, customer_success, sales, data)
12. customer_success -> `customer_success.renewal_due` (sales, finance, legal) -> `sales.renewal_proposal_sent` -> `customer_success.renewal_confirmed` (finance, legal, sales, delivery, data) or `customer_success.client_churned` (finance, sales, executive, data); risk path: `customer_success.churn_risk_flagged`

**Hiring:** any dept `<d>.hire_requested` -> people -> `people.requisition_opened` (executive, finance) -> `executive.headcount_approved` (people, finance) -> `people.job_posted` (marketing) -> `external.candidate_applied` -> `people.offer_accepted` (finance, legal) -> `people.new_hire_started` (it_security, operations, finance, delivery) -> `it_security.access_provisioned` + `operations.workspace_ready` (people). Leavers: `people.employee_left` -> `it_security.access_revoked`.

**Budgeting (annual, opens in Q4):** `finance.budget_cycle_opened` (all) -> every dept `<d>.budget_submitted` (finance) -> `finance.budget_consolidated` (executive) -> `executive.budget_approved` (all). In-year: `finance.budget_variance_flagged` (executive), `finance.month_end_closed`, `finance.cash_forecast_updated`.

**Compliance:** `external.regulation_published` -> `legal.regulatory_change_noted` (executive, it_security, people, operations, data, product) -> `legal.compliance_finding_raised` (executive, operations) -> `operations.compliance_action_completed` (legal); `legal.policy_update_published` (people, operations, it_security); `people.compliance_training_completed`; certifications: `it_security.certification_status_updated` (legal, sales, executive); AI governance: `product.ai_risk_review_requested` -> `legal.ai_risk_review_completed`.

**Security incident:** `external.security_alert` -> `it_security.incident_detected` (executive, legal, operations, customer_success, delivery) -> if personal data: `it_security.data_breach_confirmed` (legal, executive, customer_success) -> `legal.regulator_notification_filed` (executive, it_security) (ICO within 72h) -> `it_security.incident_resolved`; severity `critical` may trigger `executive.crisis_declared` (all).

**Vendors:** `operations.vendor_review_requested` (legal, it_security, finance) -> `it_security.vendor_risk_assessed` -> `operations.vendor_approved` (finance, it_security).

### 7.3 Per-department topic table (generated from `core/topics.py`)

Generic topics (all departments): every department `<d>` publishes `<d>.budget_submitted` (to `finance`; finance's own goes to `executive`) and `<d>.hire_requested` (to `people`; people's own goes to `executive`). They are omitted from the lists below. `external.*` topics (sender `external`) are listed under Subscribes.

**executive**

- Publishes (prefix `executive.`): `board_meeting_held`, `budget_approved`, `crisis_declared`, `deal_decision_made`, `headcount_approved`, `okrs_set`, `pricing_change_approved`, `strategy_updated`
- Subscribes: `customer_success.churn_risk_flagged`, `customer_success.client_churned`, `data.agent_quality_report_published`, `data.forecast_updated`, `data.kpi_report_published`, `delivery.capacity_forecast_updated`, `delivery.quality_issue_raised`, `external.board_request`, `finance.budget_consolidated`, `finance.budget_cycle_opened`, `finance.budget_variance_flagged`, `finance.cash_forecast_updated`, `finance.collections_escalated`, `finance.month_end_closed`, `it_security.certification_status_updated`, `it_security.data_breach_confirmed`, `it_security.incident_detected`, `it_security.incident_resolved`, `legal.ai_risk_review_completed`, `legal.client_dispute_raised`, `legal.compliance_finding_raised`, `legal.contract_risk_flagged`, `legal.regulator_notification_filed`, `legal.regulatory_change_noted`, `marketing.brand_incident_raised`, `operations.continuity_test_completed`, `operations.process_improvement_proposed`, `people.engagement_survey_completed`, `people.requisition_opened`, `product.pricing_change_proposed`, `product.roadmap_published`, `sales.deal_approval_requested`, `sales.deal_lost`, `sales.deal_won`, `sales.proposal_sent`, `finance.budget_submitted`, `people.hire_requested`

**sales**

- Publishes (prefix `sales.`): `deal_approval_requested`, `deal_lost`, `deal_won`, `lead_qualified`, `proposal_requested`, `proposal_sent`, `renewal_proposal_sent`, `security_review_requested`
- Subscribes: `customer_success.churn_risk_flagged`, `customer_success.client_churned`, `customer_success.expansion_opportunity_identified`, `customer_success.health_score_updated`, `customer_success.renewal_confirmed`, `customer_success.renewal_due`, `data.forecast_updated`, `delivery.capacity_forecast_updated`, `delivery.engagement_completed`, `delivery.scope_change_requested`, `delivery.scoping_completed`, `executive.budget_approved`, `executive.crisis_declared`, `executive.deal_decision_made`, `executive.okrs_set`, `executive.pricing_change_approved`, `executive.strategy_updated`, `external.rfp_received`, `finance.budget_cycle_opened`, `finance.invoice_overdue`, `finance.payment_received`, `finance.pricing_check_completed`, `it_security.certification_status_updated`, `it_security.security_questionnaire_completed`, `legal.contract_drafted`, `legal.contract_risk_flagged`, `legal.contract_signed`, `legal.security_terms_reviewed`, `marketing.campaign_launched`, `marketing.content_published`, `marketing.event_scheduled`, `marketing.lead_generated`, `product.agent_capability_added`, `product.pricing_change_proposed`, `product.roadmap_published`

**marketing**

- Publishes (prefix `marketing.`): `brand_incident_raised`, `campaign_launched`, `case_study_requested`, `content_published`, `event_scheduled`, `lead_generated`
- Subscribes: `customer_success.case_study_approved`, `customer_success.feedback_received`, `data.benchmark_ready`, `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.pricing_change_approved`, `executive.strategy_updated`, `external.lead_inbound`, `finance.budget_cycle_opened`, `people.job_posted`, `product.agent_capability_added`, `product.release_shipped`, `product.roadmap_published`, `sales.deal_lost`, `sales.lead_qualified`

**delivery**

- Publishes (prefix `delivery.`): `capacity_forecast_updated`, `engagement_completed`, `engagement_kickoff`, `milestone_reached`, `quality_issue_raised`, `scope_change_requested`, `scoping_completed`, `staffing_requested`
- Subscribes: `customer_success.churn_risk_flagged`, `customer_success.feedback_received`, `customer_success.health_score_updated`, `customer_success.renewal_confirmed`, `customer_success.support_escalated`, `data.agent_quality_report_published`, `data.benchmark_ready`, `data.forecast_updated`, `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.strategy_updated`, `external.client_scope_request`, `finance.billing_schedule_created`, `finance.budget_cycle_opened`, `it_security.incident_detected`, `legal.client_dispute_raised`, `legal.contract_signed`, `people.engagement_survey_completed`, `people.new_hire_started`, `product.agent_capability_added`, `product.release_shipped`, `product.roadmap_published`, `sales.deal_won`, `sales.lead_qualified`, `sales.proposal_requested`

**finance**

- Publishes (prefix `finance.`): `billing_schedule_created`, `budget_consolidated`, `budget_cycle_opened`, `budget_variance_flagged`, `cash_forecast_updated`, `collections_escalated`, `invoice_issued`, `invoice_overdue`, `month_end_closed`, `payment_received`, `pricing_check_completed`
- Subscribes: `customer_success.client_churned`, `customer_success.renewal_confirmed`, `customer_success.renewal_due`, `data.forecast_updated`, `data.kpi_report_published`, `delivery.capacity_forecast_updated`, `delivery.engagement_completed`, `delivery.engagement_kickoff`, `delivery.milestone_reached`, `delivery.scope_change_requested`, `delivery.scoping_completed`, `executive.board_meeting_held`, `executive.budget_approved`, `executive.crisis_declared`, `executive.deal_decision_made`, `executive.headcount_approved`, `executive.okrs_set`, `executive.pricing_change_approved`, `executive.strategy_updated`, `external.client_payment_received`, `it_security.vendor_risk_assessed`, `legal.client_dispute_raised`, `legal.contract_signed`, `marketing.campaign_launched`, `operations.procurement_order_placed`, `operations.vendor_approved`, `operations.vendor_review_requested`, `people.contractor_engaged`, `people.employee_left`, `people.new_hire_started`, `people.offer_accepted`, `people.requisition_opened`, `product.pricing_change_proposed`, `sales.deal_approval_requested`, `sales.deal_won`, `sales.proposal_requested`, `sales.renewal_proposal_sent`, all `<d>.budget_submitted`

**people**

- Publishes (prefix `people.`): `compliance_training_completed`, `contractor_engaged`, `employee_left`, `engagement_survey_completed`, `job_posted`, `new_hire_started`, `offer_accepted`, `requisition_opened`
- Subscribes: `delivery.capacity_forecast_updated`, `delivery.staffing_requested`, `executive.budget_approved`, `executive.crisis_declared`, `executive.headcount_approved`, `executive.okrs_set`, `executive.strategy_updated`, `external.candidate_applied`, `finance.budget_cycle_opened`, `it_security.access_provisioned`, `it_security.access_revoked`, `legal.policy_update_published`, `legal.regulatory_change_noted`, `operations.workspace_ready`, all `<d>.hire_requested`

**legal**

- Publishes (prefix `legal.`): `ai_risk_review_completed`, `client_dispute_raised`, `compliance_finding_raised`, `contract_drafted`, `contract_risk_flagged`, `contract_signed`, `policy_update_published`, `regulator_notification_filed`, `regulatory_change_noted`, `security_terms_reviewed`
- Subscribes: `customer_success.renewal_confirmed`, `customer_success.renewal_due`, `delivery.scope_change_requested`, `executive.board_meeting_held`, `executive.budget_approved`, `executive.crisis_declared`, `executive.deal_decision_made`, `executive.okrs_set`, `executive.strategy_updated`, `external.regulation_published`, `finance.budget_cycle_opened`, `finance.collections_escalated`, `finance.invoice_overdue`, `it_security.access_revoked`, `it_security.certification_status_updated`, `it_security.data_breach_confirmed`, `it_security.incident_detected`, `it_security.incident_resolved`, `it_security.security_questionnaire_completed`, `it_security.vendor_risk_assessed`, `marketing.brand_incident_raised`, `operations.compliance_action_completed`, `operations.vendor_review_requested`, `people.compliance_training_completed`, `people.contractor_engaged`, `people.employee_left`, `people.offer_accepted`, `product.ai_risk_review_requested`, `sales.deal_approval_requested`, `sales.deal_won`, `sales.renewal_proposal_sent`, `sales.security_review_requested`

**it_security**

- Publishes (prefix `it_security.`): `access_provisioned`, `access_revoked`, `certification_status_updated`, `data_breach_confirmed`, `incident_detected`, `incident_resolved`, `security_questionnaire_completed`, `vendor_risk_assessed`, `vulnerability_found`
- Subscribes: `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.strategy_updated`, `external.security_alert`, `finance.budget_cycle_opened`, `legal.policy_update_published`, `legal.regulator_notification_filed`, `legal.regulatory_change_noted`, `operations.continuity_test_completed`, `operations.vendor_approved`, `operations.vendor_review_requested`, `people.compliance_training_completed`, `people.contractor_engaged`, `people.employee_left`, `people.new_hire_started`, `product.ai_risk_review_requested`, `product.release_shipped`, `product.vulnerability_fixed`, `sales.security_review_requested`

**operations**

- Publishes (prefix `operations.`): `compliance_action_completed`, `continuity_test_completed`, `process_improvement_proposed`, `procurement_order_placed`, `vendor_approved`, `vendor_review_requested`, `workspace_ready`
- Subscribes: `data.data_quality_issue_raised`, `delivery.engagement_kickoff`, `delivery.staffing_requested`, `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.strategy_updated`, `external.vendor_quote_received`, `finance.budget_cycle_opened`, `it_security.access_provisioned`, `it_security.incident_detected`, `it_security.incident_resolved`, `it_security.vendor_risk_assessed`, `it_security.vulnerability_found`, `legal.compliance_finding_raised`, `legal.policy_update_published`, `legal.regulatory_change_noted`, `marketing.event_scheduled`, `people.employee_left`, `people.new_hire_started`

**customer_success**

- Publishes (prefix `customer_success.`): `case_study_approved`, `churn_risk_flagged`, `client_churned`, `expansion_opportunity_identified`, `feedback_received`, `health_score_updated`, `renewal_confirmed`, `renewal_due`, `support_escalated`
- Subscribes: `delivery.engagement_completed`, `delivery.engagement_kickoff`, `delivery.milestone_reached`, `delivery.quality_issue_raised`, `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.strategy_updated`, `external.client_feedback_submitted`, `external.client_notice_of_termination`, `finance.billing_schedule_created`, `finance.budget_cycle_opened`, `finance.invoice_issued`, `finance.invoice_overdue`, `finance.payment_received`, `it_security.data_breach_confirmed`, `it_security.incident_detected`, `it_security.incident_resolved`, `legal.client_dispute_raised`, `legal.contract_signed`, `marketing.case_study_requested`, `product.release_shipped`, `sales.deal_won`, `sales.renewal_proposal_sent`

**product**

- Publishes (prefix `product.`): `agent_capability_added`, `ai_risk_review_requested`, `pricing_change_proposed`, `release_shipped`, `roadmap_published`, `vulnerability_fixed`
- Subscribes: `customer_success.feedback_received`, `customer_success.support_escalated`, `data.agent_quality_report_published`, `data.data_quality_issue_raised`, `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.pricing_change_approved`, `executive.strategy_updated`, `external.technology_release_published`, `finance.budget_cycle_opened`, `it_security.vulnerability_found`, `legal.ai_risk_review_completed`, `legal.regulatory_change_noted`

**data**

- Publishes (prefix `data.`): `agent_quality_report_published`, `benchmark_ready`, `data_quality_issue_raised`, `forecast_updated`, `kpi_report_published`
- Subscribes: `customer_success.client_churned`, `customer_success.health_score_updated`, `customer_success.renewal_confirmed`, `delivery.engagement_completed`, `delivery.engagement_kickoff`, `executive.board_meeting_held`, `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.strategy_updated`, `external.market_data_published`, `finance.budget_cycle_opened`, `finance.cash_forecast_updated`, `finance.invoice_issued`, `finance.month_end_closed`, `finance.payment_received`, `legal.ai_risk_review_completed`, `legal.regulatory_change_noted`, `marketing.campaign_launched`, `marketing.lead_generated`, `product.ai_risk_review_requested`, `sales.deal_lost`, `sales.deal_won`, `sales.lead_qualified`, `sales.proposal_sent`

### 7.4 External entry points (`external.*`, delivered to one department each)

`external.lead_inbound` (marketing), `external.rfp_received` (sales), `external.client_scope_request` (delivery), `external.client_payment_received` (finance), `external.client_notice_of_termination` and `external.client_feedback_submitted` (customer_success), `external.candidate_applied` (people), `external.security_alert` (it_security), `external.regulation_published` (legal), `external.vendor_quote_received` (operations), `external.market_data_published` (data), `external.technology_release_published` (product), `external.board_request` (executive).

### 7.5 Needing a topic that does not exist
Do not edit `core/topics.py`. Use the `<id>.internal.*` namespace for private flows, and list the proposed new public topic (publisher, subscribers, body keys) under "Topic requests" in your final report so the integrator can add it.

## 8. `workflows.py` contract

```python
from core import Message, MessageBus, SimClock

def scenario_inbound_lead_to_win(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Short docstring: what business situation this seeds and what chain it should trigger."""
    return [bus.make_message("external", "marketing", "external.lead_inbound",
                             {"lead_id": "LD-00001", "company": "Calder Freight Group", "employees": 650},
                             sim_time=clock.day)]

SCENARIOS = {"inbound_lead_to_win": scenario_inbound_lead_to_win}
```
- Scenario functions only **build** Messages (via `bus.make_message`) and return them; the caller publishes with `Company.seed(msgs)`. Sender is `"external"` for outside-world events or your department id.
- At least 3 scenarios per department, all listed in `SCENARIOS`; at least one must start from one of YOUR subscribed topics and at least one must exercise a cross-department chain from section 7.2. Parameterise with defaults (no required args beyond `bus`, `clock`). Use sample client "Calder Freight Group" (COMPANY.md §10) or invented fictional clients; amounts must use COMPANY.md prices.

## 9. Tests (`tests/test_<id>.py`)

- `unittest` only; run from the repo root: `python3 -m unittest discover -s ai-company -t ai-company`. Import with `from core import ...` and `from departments.<id>.agent import build_agent`.
- Required tests: (1) `build_agent` returns `<Id>Agent` with `name == "<id>"`; (2) `SUBSCRIBES`/`PUBLISHES` equal the topic map; (3) every scenario in `SCENARIOS` builds valid Messages; (4) a `Company(use_departments=False, factories={"<id>": build_agent})` run of each scenario completes with no exception and logs at least one event from `<id>`; (5) handle() on each subscribed topic returns `list[Message]` whose topics are all in `PUBLISHES`; (6) markdown docs exist and contain every required heading from section 3; (7) KPI list has >= 8 items; (8) determinism: two identical runs give identical `log.to_jsonl()`.
- Tests must not depend on other departments' code being present (use stubs).
- Integration-level full-company runs are done later by the integrator; they use `Company()` with auto-discovery of `departments.<id>.agent.build_agent`.

## 10. Quality bar and done checklist

1. All four `.md` docs follow the templates, contain real numbers consistent with COMPANY.md (headcount §6.1, bands §6.2, budget §5.4, prices §3).
2. `python3 -m unittest discover -s ai-company -t ai-company` passes (run it; fix failures in your own files only).
3. No edits outside `ai-company/departments/<id>/`. No network, no third-party packages, no files outside the repo dir, no secrets.
4. Final report lists: files created, test result, any COMPANY.md/topic conflicts, "Topic requests".
5. Style: type hints, short docstrings, line length <= 110, no emojis, British English in prose.
