"""Contract and behaviour tests for the legal department (agent, workflows, docs, budget, KPIs)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from core.events import EventLog
from departments.legal import workflows
from departments.legal import agent as legal_agent
from departments.legal.agent import (KPIS, LegalAgent, build_agent, classify_ai_use_case, classify_regulation,
                                     review_terms)

DEPT = "legal"
HERE = os.path.dirname(os.path.abspath(__file__))
DEPT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))

# COMPANY.md section 5.4 legal row (GBP k): people, non-people, total for FY2026..FY2028
BUDGET_PEOPLE = (210, 330, 600)
BUDGET_NON_PEOPLE = (100, 250, 700)
BUDGET_TOTAL = (310, 580, 1300)
HEADCOUNT = (1, 3, 5)  # COMPANY.md section 6.1 humans, year-end

DOC_HEADINGS = {
    "blueprint.md": [
        "# Legal Department Blueprint", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles",
        "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies",
        "## 8. Sources",
    ],
    "sops.md": ["# Legal Standard Operating Procedures", "## Overview", "## Policy constants",
                "### Contract playbook (clause positions)"],
    "kpis.md": [
        "# Legal KPIs", "## 1. KPI summary", "## 2. Definitions and formulas",
        "## 3. Reporting cadence and data sources", "## 4. Links to company targets",
    ],
    "economics.md": [
        "# Legal Economics", "## 1. Budget", "## 2. Headcount cost build-up",
        "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md",
    ],
}


def read_doc(name: str) -> str:
    with open(os.path.join(DEPT_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def make_env():
    """Fresh (company, agent) with only legal live (other departments are stubs)."""
    company = Company(MockLLM(), factories={DEPT: build_agent}, use_departments=False, strict=True)
    return company, company.agents[DEPT]


def standalone_agent():
    clock = SimClock()
    bus = MessageBus(clock)
    log = EventLog(clock.date)
    return build_agent(MockLLM(), bus, clock, log), bus, clock, log


def sample_body(topic: str) -> dict:
    """A rich well-formed body using the shared business-ID keys from CONVENTIONS section 4."""
    return {
        "client_id": "CL-0007", "client_name": "Calder Freight Group", "deal_id": "DL-0001",
        "contract_id": "CT-0001", "engagement_id": "EN-0001", "invoice_id": "INV-2026-0001",
        "incident_id": "INC-0001", "vendor_id": "VN-0001", "employee_id": "EMP-0001", "amount_gbp": 60000,
        "service_line": "forge", "tier": "forge_build", "department": "sales", "summary": f"test {topic}",
        "due_day": 30, "discount_pct": 5, "uplift_pct": 4.0, "days_overdue": 60, "records_affected": 1200,
        "lumenhall_role": "controller", "title": "Data (Use and Access) Act guidance", "effective_in_days": 60,
        "completion_pct": 90, "fiscal_year": 2027, "review_id": "AIR-001",
        "use_case_tags": ["employment"], "uses_personal_data": True, "certification": "iso_27001",
        "status": "achieved", "open_gaps": 1, "terms": {"liability_cap_multiple": 1.5, "payment_days": 45},
        "days_by_level": {"consultant": 5}, "category": "misleading_claim", "finding_id": "CF-0001",
        "okrs": {"o1": "x"}, "us_expansion": True, "decision": "approved", "risk_rating": "high",
        "processes_personal_data": True, "has_dpa": False, "contractor_name": "Sam Rowe",
        "candidate_name": "Alex Doe",
    }


def external_sender(topic: str) -> str:
    return "external" if topic.startswith("external.") else topic.split(".", 1)[0]


def emitted(company: Company) -> list:
    return [e for e in company.log.query(department=DEPT) if e.data.get("kind") == "emit"]


def emitted_topics(company: Company) -> set[str]:
    return {e.topic for e in emitted(company)}


def emits_of(company: Company, topic: str) -> list:
    return [e for e in emitted(company) if e.topic == topic]


class ContractTests(unittest.TestCase):
    def test_class_name(self) -> None:
        self.assertEqual(class_name_for(DEPT), "LegalAgent")
        self.assertTrue(issubclass(LegalAgent, DepartmentAgent))

    def test_build_agent(self) -> None:
        agent, bus, _, _ = standalone_agent()
        self.assertIsInstance(agent, LegalAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)
        self.assertEqual(bus.agent_names, [], "build_agent must not register with the bus")
        self.assertEqual(len(bus.pending), 0, "build_agent must not publish")

    def test_topic_map(self) -> None:
        self.assertEqual(tuple(LegalAgent.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(LegalAgent.PUBLISHES), publishes_for(DEPT))
        self.assertGreater(len(LegalAgent.SUBSCRIBES), 0)
        self.assertGreater(len(LegalAgent.PUBLISHES), 0)

    def test_kpis(self) -> None:
        self.assertEqual(len(KPIS), 11)
        self.assertTrue(all(isinstance(k, Kpi) for k in KPIS))
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))
        for expected in ("contract_turnaround_days", "breach_notification_within_72h_pct", "dsar_on_time_pct",
                         "legal_cost_pct_revenue"):
            self.assertIn(expected, names)

    def test_kpis_match_doc_targets(self) -> None:
        kpi_doc = read_doc("kpis.md")
        for k in KPIS:
            self.assertIn(f"| {k.name} |", kpi_doc, f"{k.name} missing from kpis.md")
            row = next(r for r in kpi_doc.splitlines() if r.startswith(f"| {k.name} |"))
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertAlmostEqual(float(cells[3]), float(k.target), places=6, msg=k.name)
            self.assertEqual(cells[2], k.unit, k.name)
            direction = "higher is better" if k.higher_is_better else "lower is better"
            self.assertEqual(cells[6], direction, k.name)

    def test_kpi_direction_of_known_kpis(self) -> None:
        by_name = {k.name: k for k in KPIS}
        lower = ("contract_turnaround_days", "non_standard_liability_pct", "deal_won_to_signed_days",
                 "gc_escalation_response_hours", "regulatory_triage_days", "ai_risk_review_days",
                 "legal_cost_pct_revenue")
        for name, kpi in by_name.items():
            self.assertEqual(kpi.higher_is_better, name not in lower, name)

    def test_role(self) -> None:
        agent, _, _, _ = standalone_agent()
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(agent.role.level, "head")
        self.assertEqual(agent.role.title, "General Counsel")


class HandleTests(unittest.TestCase):
    def test_handle_every_subscribed_topic(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                msg = bus.make_message(external_sender(topic), DEPT, topic, sample_body(topic), sim_time=0)
                out = agent.handle(msg)
                self.assertIsInstance(out, list)
                for m in out:
                    self.assertIsInstance(m, Message)
                    self.assertIn(m.topic, agent.PUBLISHES)
                    self.assertTrue(m.topic.startswith("legal."))
                    self.assertFalse(m.topic.startswith("legal.internal."))

    def test_handle_tolerates_empty_body(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                msg = bus.make_message(external_sender(topic), DEPT, topic, {}, sim_time=0)
                self.assertIsInstance(agent.handle(msg), list)

    def test_unknown_topic_does_not_raise(self) -> None:
        agent, bus, _, _ = standalone_agent()
        msg = bus.make_message("sales", DEPT, "sales.unknown_event", {}, sim_time=0)
        self.assertEqual(agent.handle(msg), [])

    def test_handle_is_deterministic(self) -> None:
        results = []
        for _ in range(2):
            agent, bus, _, log = standalone_agent()
            for topic in subscribes_for(DEPT):
                agent.handle(bus.make_message(external_sender(topic), DEPT, topic, sample_body(topic),
                                              sim_time=0))
            results.append(log.to_jsonl())
        self.assertEqual(results[0], results[1])

    def test_tick_runs_over_a_year_without_error(self) -> None:
        company, agent = make_env()
        company.run(370)
        for m in agent.tick() or []:
            self.assertIn(m.topic, agent.PUBLISHES)
        self.assertGreater(len(company.log.query(department=DEPT)), 0)


class WorkflowTests(unittest.TestCase):
    def test_scenarios_dict(self) -> None:
        self.assertGreaterEqual(len(workflows.SCENARIOS), 3)
        for name, fn in workflows.SCENARIOS.items():
            self.assertTrue(callable(fn))
            self.assertEqual(fn.__name__, f"scenario_{name}")
            self.assertTrue(hasattr(workflows, fn.__name__))

    def test_every_scenario_function_is_registered(self) -> None:
        defined = {n for n in dir(workflows) if n.startswith("scenario_") and callable(getattr(workflows, n))}
        registered = {fn.__name__ for fn in workflows.SCENARIOS.values()}
        self.assertEqual(defined, registered)

    def test_scenarios_build_valid_messages(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                clock = SimClock()
                bus = MessageBus(clock)
                msgs = fn(bus, clock)
                self.assertIsInstance(msgs, list)
                self.assertGreater(len(msgs), 0)
                ids = [m.id for m in msgs]
                self.assertEqual(len(ids), len(set(ids)))
                for m in msgs:
                    self.assertIsInstance(m, Message)
                    self.assertIsInstance(m.body, dict)
                    self.assertIsInstance(m.sim_time, int)
                    self.assertGreaterEqual(m.sim_time, clock.day)

    def test_some_scenario_starts_from_subscribed_topic(self) -> None:
        subs = set(subscribes_for(DEPT))
        for name, fn in workflows.SCENARIOS.items():
            clock = SimClock()
            msgs = fn(MessageBus(clock), clock)
            self.assertTrue(any(m.topic in subs for m in msgs), name)

    def test_amounts_are_numeric_gbp(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            clock = SimClock()
            for m in fn(MessageBus(clock), clock):
                for key, val in m.body.items():
                    if key.endswith("_gbp") and val is not None:
                        self.assertIsInstance(val, (int, float), f"{name}:{m.topic}:{key}")
                        self.assertNotIsInstance(val, bool)

    def test_every_scenario_runs_strict(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company, _ = make_env()
                company.seed(fn(company.bus, company.clock))
                company.run(60)
                self.assertGreater(len(company.log.query(department=DEPT)), 0)
                self.assertEqual(company.log.query(topic="system.agent_error"), [])

    def test_every_scenario_runs_with_all_departments_if_present(self) -> None:
        """Auto-discovery run (stubs fill gaps); legal must not break other agents' handling."""
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company = Company(MockLLM(), factories={DEPT: build_agent}, strict=False)
                company.seed(fn(company.bus, company.clock))
                company.run(45)
                legal_errors = [e for e in company.log.query(topic="system.agent_error")
                                  if e.department == DEPT]
                self.assertEqual(legal_errors, [])

    def test_scenarios_are_deterministic(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                dumps = []
                for _ in range(2):
                    company, _ = make_env()
                    company.seed(fn(company.bus, company.clock))
                    company.run(45)
                    dumps.append(company.log.to_jsonl())
                self.assertEqual(dumps[0], dumps[1])

    def test_scenarios_accept_default_args_only(self) -> None:
        for fn in workflows.SCENARIOS.values():
            clock = SimClock()
            fn(MessageBus(clock), clock)  # must not require params


class BehaviourTests(unittest.TestCase):
    """Lifecycle behaviours: the right legal topics are emitted for the right triggers, with human gates."""

    def _run(self, topic: str, body: dict, days: int = 45, sender: str | None = None):
        company, agent = make_env()
        company.inject(topic, body, recipient=DEPT, sender=sender or external_sender(topic))
        company.run(days)
        return company, agent

    def _scenario(self, name: str, days: int = 60):
        company, agent = make_env()
        company.seed(workflows.SCENARIOS[name](company.bus, company.clock))
        company.run(days)
        return company, agent

    @staticmethod
    def _day(event) -> int:
        return event.sim_time

    def test_deal_won_draft_released_only_after_review_then_signed(self) -> None:
        company, agent = self._scenario("deal_won_to_contract")
        drafted = emits_of(company, "legal.contract_drafted")
        signed = emits_of(company, "legal.contract_signed")
        self.assertEqual(len(drafted), 1)
        self.assertEqual(len(signed), 1)
        body = drafted[0].data["body"]
        self.assertEqual(body["playbook_position"], "standard")
        self.assertEqual(body["human_review"], "sample_check")
        self.assertEqual(self._day(drafted[0]), legal_agent.REVIEW_SLA_DAYS["standard"])
        self.assertEqual(body["turnaround_days"], 3)
        self.assertEqual(self._day(signed[0]), 3 + legal_agent.SIGNATURE_LEAD_DAYS["standard"])
        self.assertEqual(signed[0].data["body"]["advice_status"], "executed_record")
        self.assertTrue(signed[0].data["body"]["work_may_start"])
        self.assertEqual(signed[0].data["body"]["payment_terms_days"], 30)
        self.assertGreater(self._day(signed[0]), self._day(drafted[0]))

    def test_review_task_completed_when_draft_released(self) -> None:
        company, agent = self._scenario("deal_won_to_contract")
        reviews = [t for t in agent.tasks.values() if t.title.startswith("Human lawyer review")]
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].status, "done")
        self.assertEqual(reviews[0].due, legal_agent.REVIEW_SLA_DAYS["standard"])

    def test_nothing_drafted_before_review_sla(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_deal_won_to_contract(company.bus, company.clock))
        company.run(2)  # days 0 and 1: review still open
        self.assertEqual(emits_of(company, "legal.contract_drafted"), [])
        contract = next(iter(agent.state["contracts"].values()))
        self.assertFalse(contract["released"])
        self.assertEqual(agent.state["contracts"][contract["contract_id"]]["status"], "awaiting_signature")

    def test_non_standard_terms_flagged_before_draft_and_review_is_two_days(self) -> None:
        company, agent = self._scenario("non_standard_terms_escalation")
        flagged = emits_of(company, "legal.contract_risk_flagged")
        drafted = emits_of(company, "legal.contract_drafted")
        signed = emits_of(company, "legal.contract_signed")
        self.assertEqual(len(flagged), 1, "a deal is flagged once only")
        self.assertTrue(flagged[0].data["body"]["blocking"])
        self.assertEqual(flagged[0].data["body"]["severity"], "critical")
        self.assertEqual(set(flagged[0].data["body"]["required_approvers"]),
                         {"General Counsel", "Chief Executive Officer"})
        self.assertEqual(len(drafted), 1)
        self.assertEqual(drafted[0].data["body"]["playbook_position"], "escalated")
        self.assertEqual(drafted[0].data["body"]["human_review"], "full_review")
        self.assertEqual(drafted[0].data["body"]["turnaround_days"], legal_agent.REVIEW_SLA_DAYS["escalated"])
        self.assertLessEqual(self._day(flagged[0]), self._day(drafted[0]))
        self.assertEqual(len(signed), 1)
        self.assertGreaterEqual(self._day(signed[0]), self._day(drafted[0]))

    def test_contract_not_signed_without_ceo_decision(self) -> None:
        body = {"deal_id": "DL-0009", "client_id": "CL-0009", "client_name": "Big Co", "amount_gbp": 650000,
                "service_line": "forge", "tier": "forge_scale"}
        company, agent = self._run("sales.deal_won", body, days=30)
        self.assertEqual(len(emits_of(company, "legal.contract_drafted")), 1)
        self.assertEqual(emits_of(company, "legal.contract_signed"), [])
        contract = next(iter(agent.state["contracts"].values()))
        self.assertEqual(contract["status"], "pending_approval")
        self.assertEqual(contract["approvals_pending"], ["Chief Executive Officer"])

    def test_board_approval_required_above_threshold(self) -> None:
        body = {"deal_id": "DL-0010", "client_id": "CL-0010", "amount_gbp": 1_600_000, "service_line": "forge"}
        company, agent = make_env()
        company.inject("sales.deal_won", body, recipient=DEPT, sender="sales")
        company.inject("executive.deal_decision_made", {"deal_id": "DL-0010", "decision": "approved"},
                       recipient=DEPT, sender="executive")
        company.run(30)
        contract = next(iter(agent.state["contracts"].values()))
        self.assertEqual(contract["status"], "pending_approval")
        self.assertIn("Board", contract["approvals_pending"])
        self.assertEqual(emits_of(company, "legal.contract_signed"), [])

    def test_rejected_deal_cancels_contract_and_is_never_released(self) -> None:
        body = {"deal_id": "DL-0011", "client_id": "CL-0011", "amount_gbp": 700_000, "service_line": "forge"}
        company, agent = make_env()
        company.inject("sales.deal_won", body, recipient=DEPT, sender="sales")
        company.inject("executive.deal_decision_made", {"deal_id": "DL-0011", "decision": "rejected"},
                       recipient=DEPT, sender="executive")
        company.run(30)
        contract = next(iter(agent.state["contracts"].values()))
        self.assertEqual(contract["status"], "cancelled")
        self.assertEqual(emits_of(company, "legal.contract_drafted"), [])
        self.assertEqual(emits_of(company, "legal.contract_signed"), [])

    def test_agent_never_signs_before_release(self) -> None:
        agent, bus, clock, log = standalone_agent()
        agent.handle(bus.make_message("sales", DEPT, "sales.deal_won", sample_body("x") | {"terms": {}},
                                      sim_time=0))
        cid = next(iter(agent.state["contracts"]))
        self.assertEqual(agent._on_signature_due({"contract_id": cid}), [])
        self.assertNotEqual(agent.state["contracts"][cid]["status"], "signed")

    def test_playbook_review_terms(self) -> None:
        std = review_terms({"liability_cap_multiple": 1.0, "payment_days": 30, "ip_ownership": "standard",
                            "data_terms": "standard_dpa", "governing_law": "england_wales"})
        self.assertEqual({f["position"] for f in std}, {"standard"})
        fb = review_terms({"liability_cap_multiple": 1.5, "payment_days": 45})
        self.assertEqual([f["position"] for f in fb], ["fallback", "fallback"])
        esc = review_terms({"uncapped_liability": True, "payment_days": 60, "governing_law": "france"})
        self.assertEqual({f["position"] for f in esc}, {"escalate"})
        self.assertEqual(legal_agent.overall_position(std), "standard")
        self.assertEqual(legal_agent.overall_position(fb), "fallback")
        self.assertEqual(legal_agent.overall_position(esc), "escalated")
        self.assertEqual(legal_agent.max_severity(esc), "critical")
        self.assertEqual(review_terms({}), [])
        short_keep = review_terms({"min_term_months": 6}, "keep")
        self.assertEqual(short_keep[0]["position"], "escalate")

    def test_policy_constants_mirror_sops(self) -> None:
        text = read_doc("sops.md")
        self.assertEqual(legal_agent.DEAL_CEO_THRESHOLD_GBP, 500_000)
        self.assertEqual(legal_agent.DEAL_BOARD_THRESHOLD_GBP, 1_500_000)
        self.assertEqual(legal_agent.ICO_DEADLINE_HOURS, 72)
        self.assertEqual(legal_agent.CLIENT_BREACH_NOTICE_HOURS, 48)
        self.assertEqual(legal_agent.SIGNATURE_LEAD_DAYS, {"standard": 3, "fallback": 5, "escalated": 5})
        self.assertEqual(legal_agent.REVIEW_SLA_DAYS, {"standard": 3, "fallback": 2, "escalated": 2})
        self.assertEqual(legal_agent.KEEP_UPLIFT_CAP_PCT, 7.0)
        for const in ("DEAL_CEO_THRESHOLD_GBP", "DEAL_BOARD_THRESHOLD_GBP", "STANDARD_PAYMENT_DAYS",
                      "FALLBACK_PAYMENT_DAYS", "KEEP_MIN_TERM_MONTHS", "KEEP_UPLIFT_CAP_PCT",
                      "DEFAULT_DISCOUNT_LIMIT_PCT", "ICO_DEADLINE_HOURS", "CLIENT_BREACH_NOTICE_HOURS",
                      "SIGNATURE_LEAD_DAYS", "REVIEW_SLA_DAYS", "GC_DECISION_HOURS", "DSAR_DEADLINE_DAYS",
                      "TRAINING_TARGET_PCT", "RATE_CARD_GBP"):
            self.assertIn(const, text, f"{const} missing from sops.md policy constants")

    def test_no_stale_blueprint_section_reference(self) -> None:
        with open(os.path.join(DEPT_DIR, "agent.py"), encoding="utf-8") as fh:
            self.assertNotIn("blueprint section 2 of sops.md", fh.read())

    # --- breach ---------------------------------------------------------------------------------------
    def test_breach_notified_to_ico_within_72_hours(self) -> None:
        company, agent = self._scenario("personal_data_breach_72h", days=10)
        filed = emits_of(company, "legal.regulator_notification_filed")
        self.assertEqual(len(filed), 1)
        body = filed[0].data["body"]
        self.assertEqual(body["regulator"], "ICO")
        self.assertTrue(body["within_72h"])
        self.assertLessEqual(body["hours_elapsed"], legal_agent.ICO_DEADLINE_HOURS)
        self.assertEqual(body["deadline_hours"], 72)
        self.assertEqual(body["risk_to_individuals"], "high")  # 1,800 records >= 1,000
        self.assertTrue(body["data_subjects_to_be_told"])
        self.assertIn("human", body["filed_by"])
        breach = agent.state["breaches"]["INC-0001"]
        self.assertTrue(breach["notifiable"] and breach["filed"])
        self.assertEqual(breach["deadline_day"], breach["aware_day"] + 3)
        self.assertEqual([t for t in agent.tasks.values() if "Article 34" in t.title], [])
        kpi = {k.name: k for k in agent.kpi_snapshot()}["breach_notification_within_72h_pct"]
        self.assertEqual(kpi.actual, 100.0)

    def test_breach_opens_privileged_matter_and_tasks(self) -> None:
        _, agent = self._scenario("personal_data_breach_72h", days=3)
        self.assertTrue(agent.state["matters"]["INC-0001"]["privileged"])
        titles = " | ".join(t.title for t in agent.tasks.values())
        self.assertIn("privileged matter", titles)
        self.assertIn("breach register", titles)
        self.assertIn("Art 34", titles)
        self.assertIn("file ICO report", titles)

    def test_processor_breach_is_not_notified_to_ico_but_to_client(self) -> None:
        body = {"incident_id": "INC-0002", "records_affected": 50, "lumenhall_role": "processor",
                "client_id": "CL-0001"}
        company, agent = self._run("it_security.data_breach_confirmed", body, days=10, sender="it_security")
        self.assertEqual(emits_of(company, "legal.regulator_notification_filed"), [])
        self.assertFalse(agent.state["breaches"]["INC-0002"]["notifiable"])
        self.assertTrue(any("Notify controller client within 48h" in t.title for t in agent.tasks.values()))

    def test_unlikely_risk_breach_not_notifiable(self) -> None:
        body = {"incident_id": "INC-0003", "records_affected": 2, "risk_to_individuals": "unlikely"}
        company, agent = self._run("it_security.data_breach_confirmed", body, days=10, sender="it_security")
        self.assertEqual(emits_of(company, "legal.regulator_notification_filed"), [])

    def test_late_filing_is_reported_as_outside_72h(self) -> None:
        agent, bus, clock, log = standalone_agent()
        agent.handle(bus.make_message("it_security", DEPT, "it_security.data_breach_confirmed",
                                      {"incident_id": "INC-0004", "records_affected": 5000, "aware_day": 0},
                                      sim_time=0))
        clock.advance(5)
        out = agent._on_ico_filing_due({"incident_id": "INC-0004"})
        self.assertEqual(len(out), 1)
        self.assertFalse(out[0].body["within_72h"])
        self.assertIn("reason_for_delay", out[0].body)
        kpi = {k.name: k for k in agent.kpi_snapshot()}["breach_notification_within_72h_pct"]
        self.assertEqual(kpi.actual, 0.0)  # filed after the deadline: not within 72 hours

    def test_deadline_watch_warns_then_alerts_for_unfiled_breach(self) -> None:
        agent, bus, clock, log = standalone_agent()
        agent.state["breaches"]["INC-0005"] = {
            "incident_id": "INC-0005", "aware_day": 0, "deadline_day": 3, "risk": "high", "role": "controller",
            "records_affected": 9, "special_category": False, "notifiable": True, "filed": False,
            "client_id": "", "warned": False, "breached_deadline": False}
        clock.advance(2)
        agent.tick()
        clock.advance(1)
        agent.tick()
        topics = [e.topic for e in log.query(department=DEPT)]
        self.assertIn("legal.activity.breach_deadline_warning", topics)
        self.assertIn("legal.activity.breach_deadline_missed", topics)

    # --- AI risk --------------------------------------------------------------------------------------
    def test_ai_risk_review_high_risk(self) -> None:
        company, agent = self._scenario("ai_risk_review_high_risk", days=10)
        done = emits_of(company, "legal.ai_risk_review_completed")
        self.assertEqual(len(done), 1)
        body = done[0].data["body"]
        self.assertEqual(body["review_id"], "AIR-900")
        self.assertEqual(body["risk_tier"], "high_risk")
        self.assertTrue(body["dpia_required"])
        self.assertEqual(body["status"], "recommendation_pending_gc_signoff")
        self.assertEqual(body["recommendation"], "cleared_with_conditions")
        self.assertEqual(body["severity"], "high")
        self.assertTrue(any("Data protection impact assessment" in c for c in body["conditions"]))
        self.assertTrue(any("sign-off on AI risk review" in t.title for t in agent.tasks.values()))

    def test_ai_tiers(self) -> None:
        self.assertEqual(classify_ai_use_case({"use_case_tags": ["social_scoring"]})["risk_tier"], "prohibited")
        self.assertEqual(classify_ai_use_case({"use_case_tags": ["social_scoring"]})["recommendation"],
                         "blocked_pending_gc")
        self.assertEqual(classify_ai_use_case({"affects_employment": True})["risk_tier"], "high_risk")
        self.assertEqual(classify_ai_use_case({"client_facing": True})["risk_tier"], "limited_risk")
        self.assertEqual(classify_ai_use_case({})["risk_tier"], "minimal_risk")
        self.assertEqual(classify_ai_use_case({})["recommendation"], "cleared_subject_to_standard_controls")

    def test_ai_risk_signoff_is_modelled_and_measured(self) -> None:
        company, agent = self._scenario("ai_risk_review_high_risk", days=10)
        review = agent.state["ai_reviews"]["AIR-900"]
        self.assertEqual(review["signoff_day"] - review["requested_day"], legal_agent.AI_SIGNOFF_DAYS)
        kpi = {k.name: k for k in agent.kpi_snapshot()}["ai_risk_review_days"]
        self.assertEqual(kpi.actual, float(legal_agent.AI_SIGNOFF_DAYS))
        self.assertTrue(kpi.on_track)

    # --- regulatory change ----------------------------------------------------------------------------
    def test_regulatory_change_to_policy_chain(self) -> None:
        company, agent = self._scenario("regulation_to_policy", days=30)
        noted = emits_of(company, "legal.regulatory_change_noted")
        findings = emits_of(company, "legal.compliance_finding_raised")
        policies = emits_of(company, "legal.policy_update_published")
        self.assertEqual(len(noted), 1)
        self.assertIn("ai_governance", noted[0].data["body"]["impact_areas"])
        self.assertEqual(noted[0].data["body"]["severity"], "high")  # 75 days
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].data["body"]["finding_id"], "CF-0001")
        self.assertEqual(len(policies), 1)
        self.assertTrue(policies[0].data["body"]["training_required"])
        self.assertEqual(policies[0].data["body"]["finding_id"], "CF-0001")
        self.assertEqual(agent.state["findings"]["CF-0001"]["status"], "closed")
        self.assertEqual({k.name: k for k in agent.kpi_snapshot()}["regulatory_triage_days"].actual, 0.0)

    def test_regulation_severity_bands(self) -> None:
        for days, severity in ((10, "critical"), (30, "critical"), (60, "high"), (200, "medium"),
                               (400, "low")):
            self.assertEqual(classify_regulation({"title": "UK GDPR update", "effective_in_days": days})
                             ["severity"], severity)
        self.assertEqual(classify_regulation({})["impact_areas"], ["general_regulatory"])

    def test_low_severity_regulation_raises_no_finding(self) -> None:
        body = {"regulation_id": "R-1", "title": "Minor tax admin note", "effective_in_days": 500}
        company, _ = self._run("external.regulation_published", body, days=5)
        self.assertEqual(len(emits_of(company, "legal.regulatory_change_noted")), 1)
        self.assertEqual(emits_of(company, "legal.compliance_finding_raised"), [])

    # --- disputes, renewals, security, vendors ------------------------------------------------------------
    def test_overdue_invoice_dispute_raises_matter(self) -> None:
        company, agent = self._scenario("overdue_invoice_dispute", days=30)
        disputes = emits_of(company, "legal.client_dispute_raised")
        self.assertGreaterEqual(len(disputes), 1)
        body = disputes[0].data["body"]
        self.assertTrue(body["legal_hold"] and body["privileged"])
        self.assertEqual(body["severity"], "medium")  # £90k is below the £100k high band
        
    def test_renewal_uplift_check(self) -> None:
        company, agent = self._scenario("renewal_uplift_check", days=30)
        drafted = emits_of(company, "legal.contract_drafted")[0].data["body"]
        self.assertEqual(drafted["uplift_pct"], 5.5)  # CPI 3.5 + 2.0 under the 7% cap
        self.assertEqual(drafted["renewal_amount_gbp"], 227880)
        flagged = emits_of(company, "legal.contract_risk_flagged")
        self.assertEqual(len(flagged), 1)
        self.assertIn("exceeds", flagged[0].data["body"]["summary"])
        signed = emits_of(company, "legal.contract_signed")
        self.assertEqual(len(signed), 1)
        self.assertEqual(signed[0].data["body"]["minimum_term_months"], 12)

    def test_uplift_is_capped(self) -> None:
        agent, _, _, _ = standalone_agent()
        self.assertEqual(agent._uplift_pct(9.0), 7.0)
        self.assertEqual(agent._uplift_pct(None), 5.0)

    def test_security_review_flags_short_notice_and_unachieved_certs(self) -> None:
        company, agent = self._scenario("security_review_and_scope_change", days=20)
        reviewed = emits_of(company, "legal.security_terms_reviewed")
        self.assertEqual(len(reviewed), 1)
        body = reviewed[0].data["body"]
        self.assertEqual(body["status"], "escalated_to_gc")
        clauses = {f["clause"] for f in body["findings"]}
        self.assertIn("breach_notice", clauses)
        self.assertIn("certification:soc2_type2", clauses)
        self.assertIn("audit_rights", clauses)

    def test_change_order_priced_from_rate_card(self) -> None:
        company, agent = self._scenario("security_review_and_scope_change", days=20)
        co = [c for c in agent.state["contracts"].values() if c["contract_type"] == "change_order"]
        self.assertEqual(len(co), 1)
        self.assertEqual(co[0]["amount_gbp"], 10 * 1050 + 20 * 350)
        drafted = [e for e in emits_of(company, "legal.contract_drafted")
                   if e.data["body"]["contract_type"] == "change_order"]
        self.assertEqual(len(drafted), 1)
        self.assertIn("Rate card", drafted[0].data["body"]["billing_terms"])

    def test_vendor_without_dpa_raises_finding(self) -> None:
        company, agent = self._scenario("vendor_without_dpa", days=10)
        findings = emits_of(company, "legal.compliance_finding_raised")
        self.assertEqual(len(findings), 1)
        issues = " ".join(findings[0].data["body"]["issues"])
        self.assertIn("Art 28", issues)
        self.assertIn("Restricted transfer", issues)

    def test_certification_failure_flags_signed_contracts(self) -> None:
        agent, bus, clock, log = standalone_agent()
        agent.state["contracts"]["CT-0001"] = {"contract_id": "CT-0001", "status": "signed",
                                                "warranties": ["iso_27001"]}
        out = agent.handle(bus.make_message("it_security", DEPT, "it_security.certification_status_updated",
                                            {"certification": "iso_27001", "status": "lapsed"}, sim_time=0))
        self.assertEqual([m.topic for m in out], ["legal.contract_risk_flagged"])
        self.assertEqual(out[0].body["affected_contracts"], ["CT-0001"])

    def test_budget_submission_matches_company_md(self) -> None:
        for fy, idx in ((2026, 0), (2027, 1), (2028, 2)):
            agent, bus, clock, log = standalone_agent()
            out = agent.handle(bus.make_message("finance", DEPT, "finance.budget_cycle_opened",
                                                {"fiscal_year": fy}, sim_time=0))
            body = out[0].body
            self.assertEqual(body["people_gbp"], BUDGET_PEOPLE[idx] * 1000)
            self.assertEqual(body["non_people_gbp"], BUDGET_NON_PEOPLE[idx] * 1000)
            self.assertEqual(body["amount_gbp"], BUDGET_TOTAL[idx] * 1000)
            self.assertEqual(sum(body["non_people_lines_gbp"].values()), body["non_people_gbp"])
            self.assertEqual(body["headcount_humans"], HEADCOUNT[idx])

    def test_hire_requests_follow_blueprint_plan(self) -> None:
        company, agent = make_env()
        company.run(1100)
        hires = emits_of(company, "legal.hire_requested")
        roles = [e.data["body"]["role"] for e in hires]
        self.assertEqual(roles, [r[2] for r in legal_agent.HIRING_PLAN])
        blueprint = read_doc("blueprint.md")
        for role in roles:
            self.assertIn(role, blueprint)

    def test_all_emitted_topics_are_published_topics_and_advice_marked(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company, _ = make_env()
                company.seed(fn(company.bus, company.clock))
                company.run(60)
                for e in emitted(company):
                    self.assertIn(e.topic, publishes_for(DEPT))
                    self.assertNotIn(".internal.", e.topic)
                    body = e.data["body"]
                    self.assertIn("advice_status", body)
                    self.assertEqual(body["escalated_to"], "General Counsel")
                    self.assertIn("not legal advice", body["disclaimer"].lower())

    def test_log_event_never_passes_topic_kwarg(self) -> None:
        for e in make_env()[0].log.query(department=DEPT):
            self.assertNotIn("topic", e.data)
        company, _ = make_env()
        for fn in workflows.SCENARIOS.values():
            company.seed(fn(company.bus, company.clock))
        company.run(60)
        for e in company.log.query(department=DEPT):
            self.assertNotIn("topic", e.data, e.topic)

    def test_no_wall_clock_or_uuid_in_sources(self) -> None:
        for fname in ("agent.py", "workflows.py"):
            with open(os.path.join(DEPT_DIR, fname), encoding="utf-8") as fh:
                src = fh.read()
            for banned in ("uuid4", "datetime.now", "date.today", "time.time(", "import requests",
                           "urllib.request"):
                self.assertNotIn(banned, src, f"{fname} contains {banned}")


class KpiTests(unittest.TestCase):
    """kpi_snapshot derives actuals from the event flow."""

    def _full_run(self, days: int = 90):
        company, agent = make_env()
        for fn in workflows.SCENARIOS.values():
            company.seed(fn(company.bus, company.clock))
        company.run(days)
        return company, agent

    def test_snapshot_mirrors_kpis(self) -> None:
        agent, _, _, _ = standalone_agent()
        snap = agent.kpi_snapshot()
        self.assertEqual([k.name for k in snap], [k.name for k in KPIS])
        for k, s in zip(KPIS, snap):
            self.assertEqual((k.unit, k.target, k.higher_is_better), (s.unit, s.target, s.higher_is_better))

    def test_fresh_agent_has_no_event_based_actuals(self) -> None:
        agent, _, _, _ = standalone_agent()
        actual = {k.name: k.actual for k in agent.kpi_snapshot()}
        self.assertEqual({n for n, a in actual.items() if a is not None}, {"legal_cost_pct_revenue"})
        self.assertEqual(actual["legal_cost_pct_revenue"], 5.2)

    def test_most_kpis_have_actuals_after_scenarios(self) -> None:
        _, agent = self._full_run()
        actual = {k.name: k.actual for k in agent.kpi_snapshot()}
        for name in ("contract_turnaround_days", "playbook_adherence_pct", "non_standard_liability_pct",
                     "deal_won_to_signed_days", "gc_escalation_response_hours",
                     "breach_notification_within_72h_pct", "regulatory_triage_days", "ai_risk_review_days",
                     "legal_cost_pct_revenue"):
            self.assertIsNotNone(actual[name], name)
        self.assertIsNone(actual["dsar_on_time_pct"])  # no DSAR logged in the scenarios
        self.assertIsNone(actual["compliance_training_completion_pct"])

    def test_deal_won_to_signed_measures_from_deal_won_day(self) -> None:
        company, agent = make_env()
        company.inject("sales.deal_won", {"deal_id": "DL-0020", "client_id": "CL-0020", "amount_gbp": 100000,
                                          "service_line": "forge", "terms": {}},
                       recipient=DEPT, sender="sales", delay_days=4)
        company.run(30)
        contract = next(iter(agent.state["contracts"].values()))
        self.assertEqual(contract["requested_day"], 4)
        expected = contract["signed_day"] - 4
        self.assertEqual({k.name: k for k in agent.kpi_snapshot()}["deal_won_to_signed_days"].actual,
                         float(expected))
        self.assertEqual(expected, 6)  # 3 days review + 3 days signature lead

    def test_deal_won_to_signed_includes_approval_wait(self) -> None:
        agent, bus, clock, log = standalone_agent()
        c = {"contract_id": "CT-9", "contract_type": "msa_sow", "status": "signed", "requested_day": 2,
             "signed_day": 12, "position": "standard", "released_day": 5}
        agent.state["contracts"]["CT-9"] = c
        k = {k.name: k for k in agent.kpi_snapshot()}
        self.assertEqual(k["deal_won_to_signed_days"].actual, 10.0)
        self.assertEqual(k["contract_turnaround_days"].actual, 3.0)

    def test_renewals_excluded_from_deal_won_to_signed(self) -> None:
        _, agent = self._full_run()
        won = [c for c in agent.state["contracts"].values()
               if c["status"] == "signed" and c["contract_type"] in ("msa_sow", "keep_order_form")]
        self.assertTrue(won)
        value = {k.name: k for k in agent.kpi_snapshot()}["deal_won_to_signed_days"].actual
        self.assertAlmostEqual(value, sum(c["signed_day"] - c["requested_day"] for c in won) / len(won))

    def test_gc_escalation_response_is_24_hours(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_non_standard_terms_escalation(company.bus, company.clock))
        company.run(10)
        escs = agent.state["escalations"]
        self.assertEqual(len(escs), 1)
        e = next(iter(escs.values()))
        self.assertEqual(e["decided_day"] - e["raised_day"], legal_agent.GC_DECISION_HOURS // 24)
        k = {k.name: k for k in agent.kpi_snapshot()}["gc_escalation_response_hours"]
        self.assertEqual(k.actual, 24.0)
        self.assertTrue(k.on_track)

    def test_standard_deal_raises_no_escalation(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_deal_won_to_contract(company.bus, company.clock))
        company.run(10)
        self.assertEqual(agent.state["escalations"], {})

    def test_non_standard_liability_share(self) -> None:
        agent, bus, clock, log = standalone_agent()
        for i, flag in enumerate((True, False, False, False)):
            agent.state["contracts"][f"CT-{i}"] = {
                "contract_id": f"CT-{i}", "contract_type": "msa_sow", "status": "signed", "position": "standard",
                "requested_day": 0, "released_day": 1, "signed_day": 3, "non_standard_liability": flag}
        k = {k.name: k for k in agent.kpi_snapshot()}
        self.assertEqual(k["non_standard_liability_pct"].actual, 25.0)
        self.assertEqual(k["playbook_adherence_pct"].actual, 100.0)

    def test_uncapped_liability_contract_counts_as_non_standard(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_non_standard_terms_escalation(company.bus, company.clock))
        company.run(20)
        k = {k.name: k for k in agent.kpi_snapshot()}
        self.assertEqual(k["non_standard_liability_pct"].actual, 100.0)
        self.assertEqual(k["playbook_adherence_pct"].actual, 0.0)

    def test_training_kpi_uses_minimum_completion(self) -> None:
        agent, bus, clock, log = standalone_agent()
        for course, pct in (("gdpr", 99), ("security", 88)):
            agent.handle(bus.make_message("people", DEPT, "people.compliance_training_completed",
                                          {"course": course, "completion_pct": pct}, sim_time=0))
        self.assertEqual({k.name: k for k in agent.kpi_snapshot()}["compliance_training_completion_pct"].actual,
                         88)
        self.assertTrue(any("Chase overdue" in t.title for t in agent.tasks.values()))

    # --- DSAR ------------------------------------------------------------------------------------------
    def test_dsar_kpi_from_manual_intake(self) -> None:
        agent, bus, clock, log = standalone_agent()
        a, b, c = agent.log_dsar_received(), agent.log_dsar_received(), agent.log_dsar_received()
        self.assertEqual((a, b, c), ("DSAR-0001", "DSAR-0002", "DSAR-0003"))
        self.assertIsNone({k.name: k for k in agent.kpi_snapshot()}["dsar_on_time_pct"].actual)
        clock.advance(10)
        self.assertTrue(agent.log_dsar_closed(a))
        self.assertFalse(agent.log_dsar_closed(a))
        self.assertFalse(agent.log_dsar_closed("DSAR-9999"))
        clock.advance(25)  # day 35: b and c are open and past the one-month deadline
        agent.log_dsar_closed(b)  # closed late
        k = {k.name: k for k in agent.kpi_snapshot()}["dsar_on_time_pct"]
        self.assertAlmostEqual(k.actual, 100.0 / 3)  # a on time; b late; c open and overdue
        topics = [e.topic for e in log.query(department=DEPT)]
        self.assertIn("legal.activity.dsar_received", topics)
        self.assertIn("legal.activity.dsar_closed", topics)

    def test_dsar_weekly_warning_and_closed_on_time(self) -> None:
        company, agent = make_env()
        ref = agent.log_dsar_received("DSAR-0100")
        company.run(30)
        warnings = [e for e in company.log.query(department=DEPT)
                    if e.topic == "legal.activity.dsar_deadline_warning"]
        self.assertTrue(warnings)
        self.assertTrue(all(w.data["days_remaining"] <= legal_agent.DSAR_WARNING_DAYS for w in warnings))
        self.assertTrue(agent.log_dsar_closed(ref))
        self.assertEqual({k.name: k for k in agent.kpi_snapshot()}["dsar_on_time_pct"].actual, 100.0)


class DeterminismTests(unittest.TestCase):
    def test_full_run_is_reproducible(self) -> None:
        dumps = []
        for _ in range(2):
            company, _ = make_env()
            for fn in workflows.SCENARIOS.values():
                company.seed(fn(company.bus, company.clock))
            company.run(90)
            dumps.append(company.log.to_jsonl())
        self.assertEqual(dumps[0], dumps[1])
        self.assertTrue(dumps[0])


class DocsTests(unittest.TestCase):
    def test_docs_exist_and_have_required_headings(self) -> None:
        for name, headings in DOC_HEADINGS.items():
            with self.subTest(doc=name):
                text = read_doc(name)
                last = -1
                for h in headings:
                    idx = text.find("\n" + h) if not text.startswith(h) else 0
                    self.assertGreaterEqual(idx, 0, f"{name}: missing heading {h!r}")
                    self.assertGreater(idx, last, f"{name}: heading {h!r} out of order")
                    last = idx

    def test_docs_have_no_placeholders(self) -> None:
        for name in DOC_HEADINGS:
            text = read_doc(name)
            for bad in ("TBD", "lorem ipsum", "TODO", "XXX"):
                self.assertNotIn(bad, text, f"{name} contains {bad}")

    def test_sops_at_least_eight_with_subsections(self) -> None:
        text = read_doc("sops.md")
        ids = re.findall(r"^## (SOP-LEGAL-\d{2}): ", text, flags=re.M)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for sub in ("### Steps", "### Outputs and messages", "### SLA and controls",
                    "### Exceptions and escalation"):
            self.assertGreaterEqual(text.count(sub), len(ids), sub)
        for field in ("**Owner**:", "**Trigger**:", "**Inputs**:"):
            self.assertGreaterEqual(text.count(field), len(ids), field)

    def test_every_sop_trigger_names_a_topic_or_schedule(self) -> None:
        text = read_doc("sops.md")
        for sop in re.split(r"^## (?=SOP-LEGAL-\d{2}: )", text, flags=re.M)[1:]:
            trigger = re.search(r"^\*\*Trigger\*\*:(.*)$", sop, flags=re.M)
            self.assertIsNotNone(trigger, sop[:40])
            self.assertTrue(re.search(r"`[a-z_]+\.[a-z_]+`|DSAR|schedule", trigger.group(1)), sop[:40])

    def test_sops_cover_subscribed_and_published_topics(self) -> None:
        text = read_doc("sops.md")
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic {topic} not in sops.md")
        triggers = "\n".join(re.findall(r"^\*\*Trigger\*\*:(.*)$", text, flags=re.M))
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, triggers, f"subscribed topic {topic} is not the Trigger of any SOP")

    def test_published_topics_appear_in_sop_outputs(self) -> None:
        text = read_doc("sops.md")
        outputs = "\n".join(re.findall(r"### Outputs and messages\n(.*?)(?=\n###|\n---|\Z)", text, flags=re.S))
        for topic in publishes_for(DEPT):
            self.assertIn(topic, outputs, f"{topic} not in any SOP outputs")

    def test_sops_mark_steps_human_or_agent(self) -> None:
        text = read_doc("sops.md")
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)

    def test_sops_policy_constants_and_playbook_present(self) -> None:
        text = read_doc("sops.md")
        for clause in ("Liability cap", "Payment terms", "IP ownership", "Data terms", "Governing law",
                       "Keep minimum term"):
            self.assertIn(f"| {clause} |", text)
        self.assertEqual(set(legal_agent.PLAYBOOK),
                         {"liability_cap", "payment_terms", "ip_ownership", "data_terms", "governing_law",
                          "min_term_months"})

    def test_sop_owners_use_blueprint_titles(self) -> None:
        blueprint = read_doc("blueprint.md")
        text = read_doc("sops.md")
        for title in ("General Counsel", "Commercial and Privacy Counsel", "Privacy and Regulatory Counsel",
                      "Contracts Specialist", "Legal Operations Analyst"):
            self.assertIn(f"| {title} |", blueprint)
        for owner in re.findall(r"^\*\*Owner\*\*:(.*)$", text, flags=re.M):
            self.assertIn("General Counsel", owner)

    def test_blueprint_mentions_head_and_agent_class(self) -> None:
        text = read_doc("blueprint.md")
        self.assertIn("General Counsel", text)
        self.assertIn("LegalAgent", text)
        self.assertIn("Callum Fraser", text)

    def test_blueprint_states_no_binding_legal_advice(self) -> None:
        self.assertRegex(read_doc("blueprint.md").lower(), r"binding legal advice|not legal advice")

    def test_kpi_doc_has_eleven_kpis_matching_code(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("## 2.", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)]
        self.assertEqual(len(rows), 11)
        self.assertEqual(len(rows), len(KPIS))
        self.assertEqual([r.split("|")[1].strip() for r in rows], [k.name for k in KPIS])

    def test_kpi_doc_defines_every_kpi_formula(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 2. Definitions and formulas", 1)[1].split("## 3.", 1)[0]
        for k in KPIS:
            self.assertIn(f"| {k.name} |", section, k.name)

    def test_kpi_doc_company_targets_consistent(self) -> None:
        text = read_doc("kpis.md")
        row = next(r for r in text.splitlines() if r.startswith("| legal_cost_pct_revenue |"))
        cells = [c.strip() for c in row.strip("|").split("|")]
        self.assertEqual(cells[3:6], ["5.2", "3.0", "2.8"])  # (310/6000, 580/19500, 1300/46200) COMPANY.md 5.1, 5.4
        row = next(r for r in text.splitlines() if r.startswith("| breach_notification_within_72h_pct |"))
        self.assertEqual([c.strip() for c in row.strip("|").split("|")][3:6], ["100", "100", "100"])

    def test_cost_pct_revenue_derivation(self) -> None:
        for fy, expected in ((2026, 5.2), (2027, 3.0), (2028, 2.8)):
            people, non_people = legal_agent.BUDGET_GBP[fy]
            self.assertEqual(round(100 * (people + non_people) / legal_agent.REVENUE_GBP[fy], 1), expected)


class BudgetTests(unittest.TestCase):
    def test_company_md_row_is_what_we_expect(self) -> None:
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            row = next(r for r in fh.read().splitlines() if r.startswith("| legal |") and "310" in r)
        nums = [int(c.replace(",", "")) for c in re.findall(r"[\d,]+", row)]
        self.assertEqual(tuple(nums[:3]), BUDGET_PEOPLE)
        self.assertEqual(tuple(nums[3:6]), BUDGET_NON_PEOPLE)
        self.assertEqual(tuple(nums[6:9]), BUDGET_TOTAL)

    def test_headcount_row_in_company_md(self) -> None:
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            row = next(r for r in fh.read().splitlines() if r.startswith("| legal |") and "| 3 |" in r)
        nums = [int(c) for c in re.findall(r"\d+", row)]
        self.assertEqual(tuple(nums[:3]), HEADCOUNT)
        self.assertEqual(tuple(legal_agent.HEADCOUNT[y][0] for y in (2026, 2027, 2028)), HEADCOUNT)

    def test_totals_are_internally_consistent(self) -> None:
        for p, n, t in zip(BUDGET_PEOPLE, BUDGET_NON_PEOPLE, BUDGET_TOTAL):
            self.assertEqual(p + n, t)

    def test_code_budget_constants_match_company_md(self) -> None:
        for i, fy in enumerate((2026, 2027, 2028)):
            people, non_people = legal_agent.BUDGET_GBP[fy]
            self.assertEqual((people, non_people), (BUDGET_PEOPLE[i] * 1000, BUDGET_NON_PEOPLE[i] * 1000))
            self.assertEqual(sum(legal_agent.NON_PEOPLE_LINES_GBP[fy].values()), non_people)

    def test_economics_states_envelope_totals(self) -> None:
        text = read_doc("economics.md")
        for total in ("310", "580", "1,300"):
            self.assertRegex(text, rf"(?<![\d,.]){re.escape(total)}(?![\d])", f"total {total} missing")
        for people in ("210", "330", "600"):
            self.assertRegex(text, rf"(?<![\d,.]){people}(?![\d])", f"people cost {people} missing")

    def test_economics_budget_table_matches_envelope(self) -> None:
        text = read_doc("economics.md")
        section = text.split("## 1. Budget", 1)[1].split("\n## 2.", 1)[0]
        for label, expected in (("Total", BUDGET_TOTAL), ("Non-people total", BUDGET_NON_PEOPLE)):
            rows = [r for r in section.splitlines()
                    if re.match(rf"^\|\s*\**\s*{re.escape(label)}", r, flags=re.I)]
            self.assertTrue(rows, f"no {label} row in budget table")
            nums = [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*\.?\d*", rows[0])]
            for exp, got in zip(expected, nums[:3]):
                self.assertLessEqual(abs(exp - got), 5, f"{label} {got} vs envelope {exp}")

    def test_economics_non_people_lines_match_code(self) -> None:
        text = read_doc("economics.md")
        section = text.split("### 1.1 Budget by line", 1)[1].split("Check:", 1)[0]
        values = {2026: [], 2027: [], 2028: []}
        lines = [r for r in section.splitlines() if r.startswith("|")][2:]
        for row in lines:
            cells = [c.strip() for c in row.strip("|").split("|")]
            if any(w in cells[0] for w in ("People", "total", "Total")):
                continue
            for fy, cell in zip((2026, 2027, 2028), cells[1:4]):
                values[fy].append(int(cell))
        for fy in values:
            self.assertEqual(sorted(values[fy]), sorted(v // 1000 for v in legal_agent.NON_PEOPLE_LINES_GBP[fy].values()))

    def test_headcount_cost_buildup_within_5k_of_envelope(self) -> None:
        text = read_doc("economics.md")
        section = text.split("## 2. Headcount cost build-up", 1)[1].split("\n## 3.", 1)[0]
        for label in ("Total",):
            row = next(r for r in section.splitlines() if re.match(rf"^\|\s*\**\s*{label}", r))
            nums = [float(x) for x in re.findall(r"\d+\.\d", row)]
            self.assertLessEqual(abs(nums[-3] - BUDGET_PEOPLE[0]), 5)
            self.assertLessEqual(abs(nums[-2] - BUDGET_PEOPLE[1]), 5)
            self.assertLessEqual(abs(nums[-1] - BUDGET_PEOPLE[2]), 5)

    def test_headcount_in_blueprint_matches_company_md(self) -> None:
        text = read_doc("blueprint.md")
        section = text.split("## 3. Roles", 1)[1].split("\n## 4.", 1)[0]
        sums = [0, 0, 0]
        for row in section.splitlines():
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) >= 8 and all(re.fullmatch(r"\d+", c) for c in cells[3:6]):
                for i in range(3):
                    sums[i] += int(cells[3 + i])
        self.assertEqual(tuple(sums), HEADCOUNT)

    def test_hiring_plan_roles_in_blueprint_within_bands(self) -> None:
        text = read_doc("blueprint.md")
        for year, month, role, level, band, start in legal_agent.HIRING_PLAN:
            self.assertIn(f"| {role} |", text)
            self.assertLessEqual(band[0], band[1])
            self.assertIn(f"{band[0]:,}", text)


if __name__ == "__main__":
    unittest.main()
