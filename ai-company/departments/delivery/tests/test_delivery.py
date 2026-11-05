"""Contract and behaviour tests for the delivery department (Lumenhall Partners)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from core import (Company, DepartmentAgent, EventLog, Kpi, Message, MessageBus, MockLLM, SimClock,
                  class_name_for, publishes_for, subscribes_for)
from departments.delivery import agent as agent_mod
from departments.delivery.agent import KPIS, build_agent

DEPT = "delivery"
DEPT_DIR = Path(__file__).resolve().parent.parent
ROOT = DEPT_DIR.parent.parent

# COMPANY.md §5.4 delivery row (GBP k): people, non-people, total for Y1..Y3
BUDGET_TOTALS_K = (2980, 7400, 15000)
BUDGET_PEOPLE_K = (1130, 3000, 8800)
BUDGET_NONPEOPLE_K = (1850, 4400, 6200)

SAMPLE_BODIES = {
    "customer_success.churn_risk_flagged": {"client_id": "CL-0001", "client_name": "Calder Freight Group",
                                            "severity": "high", "summary": "Sponsor disengaged"},
    "customer_success.feedback_received": {"client_id": "CL-0001", "client_name": "Calder Freight Group",
                                           "score": 6, "summary": "Slow milestone sign-off"},
    "customer_success.health_score_updated": {"client_id": "CL-0001", "score": 58, "engagement_id": "EN-0001"},
    "customer_success.renewal_confirmed": {"client_id": "CL-0001", "contract_id": "CT-0001",
                                           "amount_gbp": 260000},
    "customer_success.support_escalated": {"client_id": "CL-0001", "engagement_id": "EN-0001",
                                           "severity": "high", "summary": "Agent output wrong"},
    "data.agent_quality_report_published": {"summary": "Weekly agent quality", "pass_rate": 0.93},
    "data.benchmark_ready": {"summary": "Utilisation benchmark ready"},
    "data.forecast_updated": {"summary": "Pipeline forecast", "amount_gbp": 5000000},
    "executive.budget_approved": {"department": "delivery", "amount_gbp": 2980000},
    "executive.crisis_declared": {"summary": "Cash crisis", "severity": "critical"},
    "executive.okrs_set": {"summary": "FY2026 OKRs"},
    "executive.strategy_updated": {"summary": "Focus on forge"},
    "external.client_scope_request": {"client_id": "CL-0001", "client_name": "Calder Freight Group",
                                      "engagement_id": "EN-0001", "summary": "Add two data sources",
                                      "amount_gbp": 30000},
    "finance.billing_schedule_created": {"client_id": "CL-0001", "contract_id": "CT-0001",
                                         "engagement_id": "EN-0001"},
    "finance.budget_cycle_opened": {"budget_cycle": "BUD-2026", "due_day": 30},
    "it_security.incident_detected": {"incident_id": "INC-0001", "severity": "high", "summary": "Phishing"},
    "legal.client_dispute_raised": {"client_id": "CL-0001", "contract_id": "CT-0001", "severity": "high",
                                    "summary": "Disputed deliverable"},
    "legal.contract_signed": {"client_id": "CL-0001", "client_name": "Calder Freight Group",
                              "contract_id": "CT-0001", "deal_id": "DL-0001", "service_line": "forge",
                              "tier": "forge_build", "amount_gbp": 260000},
    "people.engagement_survey_completed": {"score": 71, "summary": "Q3 pulse"},
    "people.new_hire_started": {"employee_id": "EMP-0001", "role": "Consultant", "department": "delivery"},
    "product.agent_capability_added": {"summary": "Document extraction agent v2"},
    "product.release_shipped": {"summary": "Platform release 1.4"},
    "product.roadmap_published": {"summary": "FY2026 H2 roadmap"},
    "sales.deal_won": {"client_id": "CL-0001", "client_name": "Calder Freight Group", "deal_id": "DL-0001",
                       "service_line": "forge", "tier": "forge_build", "amount_gbp": 260000},
    "sales.lead_qualified": {"lead_id": "LD-00001", "client_name": "Calder Freight Group",
                             "service_line": "compass"},
    "sales.proposal_requested": {"client_id": "CL-0001", "client_name": "Calder Freight Group",
                                 "deal_id": "DL-0001", "service_line": "forge", "tier": "forge_build",
                                 "amount_gbp": 260000},
}


def _make_company(**kw) -> Company:
    return Company(llm=MockLLM(), factories={DEPT: build_agent}, use_departments=False, strict=True, **kw)


def _fresh_agent():
    clock = SimClock()
    log = EventLog(clock.date)
    bus = MessageBus(clock)
    return build_agent(MockLLM(), bus, clock, log), bus, clock, log


def _emitted_topics(log: EventLog) -> set[str]:
    return {e.topic for e in log.query(department=DEPT) if e.data.get("kind") == "emit"}


def _run_scenario(fn, ticks: int = 40):
    co = _make_company()
    co.seed(fn(co.bus, co.clock))
    co.run(ticks)
    return co


class ContractTests(unittest.TestCase):
    def test_build_agent(self):
        agent, bus, _, _ = _fresh_agent()
        self.assertEqual(type(agent).__name__, class_name_for(DEPT))
        self.assertEqual(class_name_for(DEPT), "DeliveryAgent")
        self.assertIsInstance(agent, DepartmentAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)
        self.assertEqual(bus.agent_names, [])  # build_agent must not register
        self.assertEqual(len(bus.pending), 0)  # and must not publish

    def test_class_exists(self):
        self.assertTrue(hasattr(agent_mod, "DeliveryAgent"))

    def test_topic_map(self):
        cls = agent_mod.DeliveryAgent
        self.assertEqual(tuple(cls.SUBSCRIBES), tuple(subscribes_for(DEPT)))
        self.assertEqual(tuple(cls.PUBLISHES), tuple(publishes_for(DEPT)))
        self.assertGreaterEqual(len(cls.SUBSCRIBES), 20)
        self.assertEqual(len(cls.PUBLISHES), 8)

    def test_role_headcount(self):
        agent, *_ = _fresh_agent()
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(agent.role.reports_to, "Chief Executive Officer")

    def test_kpis(self):
        self.assertGreaterEqual(len(KPIS), 8)
        for k in KPIS:
            self.assertIsInstance(k, Kpi)
            self.assertRegex(k.name, r"^[a-z][a-z0-9_]*$")
        self.assertEqual(len({k.name for k in KPIS}), len(KPIS))

    def test_handle_every_subscribed_topic(self):
        agent, bus, clock, log = _fresh_agent()
        allowed = set(agent.PUBLISHES)
        prefix = DEPT + ".internal."
        for topic in agent.SUBSCRIBES:
            body = SAMPLE_BODIES.get(topic, {"summary": "generic"})
            msg = bus.make_message("external", DEPT, topic, body, sim_time=clock.day)
            out = agent.handle(msg)
            self.assertIsInstance(out, list, topic)
            for m in out:
                self.assertIsInstance(m, Message, topic)
                self.assertTrue(m.topic in allowed or m.topic.startswith(prefix), f"{topic} -> {m.topic}")
        # every subscribed topic leaves a trace in the log
        self.assertGreater(len(log.query(department=DEPT)), 0)

    def test_handle_tolerates_sparse_bodies(self):
        agent, bus, clock, _ = _fresh_agent()
        for topic in agent.SUBSCRIBES:
            msg = bus.make_message("external", DEPT, topic, {}, sim_time=clock.day)
            self.assertIsInstance(agent.handle(msg), list, topic)

    def test_unknown_topic_does_not_raise(self):
        agent, bus, clock, _ = _fresh_agent()
        msg = bus.make_message("external", DEPT, "external.something_else", {}, sim_time=clock.day)
        self.assertEqual(agent.handle(msg), [])

    def test_tick_returns_messages(self):
        agent, _, clock, _ = _fresh_agent()
        for _ in range(35):
            out = agent.tick()
            self.assertIsInstance(out, list)
            for m in out:
                self.assertTrue(m.topic in agent.PUBLISHES or m.topic.startswith("delivery.internal."))
            clock.advance(1)


class ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from departments.delivery import workflows
        cls.workflows = workflows

    def test_scenarios_registered(self):
        sc = self.workflows.SCENARIOS
        self.assertGreaterEqual(len(sc), 3)
        for name, fn in sc.items():
            self.assertTrue(fn.__name__.startswith("scenario_"), name)
            self.assertTrue(callable(fn))

    def test_scenarios_build_valid_messages(self):
        subs = set(subscribes_for(DEPT))
        started_from_own_sub = False
        for name, fn in self.workflows.SCENARIOS.items():
            co = _make_company()
            msgs = fn(co.bus, co.clock)
            self.assertIsInstance(msgs, list, name)
            self.assertGreater(len(msgs), 0, name)
            for m in msgs:
                self.assertIsInstance(m, Message, name)
                self.assertIsInstance(m.body, dict, name)
                self.assertIsInstance(m.sim_time, int, name)
            if any(m.topic in subs for m in msgs):
                started_from_own_sub = True
        self.assertTrue(started_from_own_sub)

    def test_scenarios_run_strict(self):
        for name, fn in self.workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                co = _run_scenario(fn)
                self.assertGreater(len(co.log.query(department=DEPT)), 0)
                self.assertEqual(co.log.query(topic="system.agent_error"), [])
                for topic in _emitted_topics(co.log):
                    self.assertIn(topic, publishes_for(DEPT))

    def test_scenarios_deterministic(self):
        for name, fn in self.workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                a = _run_scenario(fn).log.to_jsonl()
                b = _run_scenario(fn).log.to_jsonl()
                self.assertEqual(a, b)

    def test_scenarios_do_not_mutate_ids_unexpectedly(self):
        """Building a scenario twice on fresh buses yields identical message dicts."""
        for name, fn in self.workflows.SCENARIOS.items():
            c1, c2 = _make_company(), _make_company()
            m1 = [m.to_dict() for m in fn(c1.bus, c1.clock)]
            m2 = [m.to_dict() for m in fn(c2.bus, c2.clock)]
            self.assertEqual(m1, m2, name)


class BehaviourTests(unittest.TestCase):
    def _inject_and_run(self, topic: str, ticks: int = 30, **extra):
        co = _make_company()
        body = dict(SAMPLE_BODIES[topic])
        body.update(extra)
        co.inject(topic, body, recipient=DEPT)
        co.run(ticks)
        return co

    def test_proposal_request_yields_scoping(self):
        co = self._inject_and_run("sales.proposal_requested")
        self.assertIn("delivery.scoping_completed", _emitted_topics(co.log))

    def test_deal_won_triggers_mobilisation(self):
        co = _make_company()
        co.inject("sales.deal_won", SAMPLE_BODIES["sales.deal_won"], recipient=DEPT)
        co.inject("legal.contract_signed", SAMPLE_BODIES["legal.contract_signed"], recipient=DEPT)
        co.inject("finance.billing_schedule_created", SAMPLE_BODIES["finance.billing_schedule_created"],
                  recipient=DEPT)
        co.run(40)
        topics = _emitted_topics(co.log)
        self.assertTrue({"delivery.staffing_requested", "delivery.engagement_kickoff"} & topics, topics)

    def test_scope_request_yields_scope_change(self):
        co = self._inject_and_run("external.client_scope_request")
        self.assertIn("delivery.scope_change_requested", _emitted_topics(co.log))

    def test_support_escalation_or_dispute_raises_quality_issue(self):
        co = _make_company()
        co.inject("customer_success.support_escalated", SAMPLE_BODIES["customer_success.support_escalated"],
                  recipient=DEPT)
        co.inject("data.agent_quality_report_published",
                  {"summary": "Quality below threshold", "pass_rate": 0.62, "severity": "high",
                   "engagement_id": "EN-0001"}, recipient=DEPT)
        co.run(30)
        events = co.log.query(department=DEPT)
        self.assertTrue(events)
        emitted = _emitted_topics(co.log)
        self.assertTrue(
            "delivery.quality_issue_raised" in emitted or "delivery.scope_change_requested" in emitted
            or any(e.topic.startswith("delivery.activity.") for e in events), emitted)

    def test_capacity_forecast_emitted_on_forecast_or_tick(self):
        co = _make_company()
        co.inject("data.forecast_updated", SAMPLE_BODIES["data.forecast_updated"], recipient=DEPT)
        co.inject("sales.lead_qualified", SAMPLE_BODIES["sales.lead_qualified"], recipient=DEPT)
        co.run(35)
        self.assertIn("delivery.capacity_forecast_updated", _emitted_topics(co.log))

    def test_emitted_messages_use_delivery_prefix_and_sender(self):
        co = _make_company()
        co.inject("sales.proposal_requested", SAMPLE_BODIES["sales.proposal_requested"], recipient=DEPT)
        co.run(20)
        sent = [m for m in co.bus.history if m.sender == DEPT]
        self.assertTrue(sent)
        for m in sent:
            self.assertTrue(m.topic.startswith("delivery."), m.topic)

    def test_agent_state_updated(self):
        co = _make_company()
        co.inject("sales.proposal_requested", SAMPLE_BODIES["sales.proposal_requested"], recipient=DEPT)
        co.run(10)
        self.assertTrue(co.agents[DEPT].state)

    def test_agent_creates_tasks(self):
        co = _make_company()
        co.inject("sales.deal_won", SAMPLE_BODIES["sales.deal_won"], recipient=DEPT)
        co.inject("legal.contract_signed", SAMPLE_BODIES["legal.contract_signed"], recipient=DEPT)
        co.run(15)
        self.assertGreater(len(co.agents[DEPT].tasks), 0)

    def test_crisis_and_incident_handled(self):
        co = _make_company()
        co.inject("executive.crisis_declared", SAMPLE_BODIES["executive.crisis_declared"], recipient=DEPT)
        co.inject("it_security.incident_detected", SAMPLE_BODIES["it_security.incident_detected"],
                  recipient=DEPT)
        co.run(10)
        self.assertEqual(co.log.query(topic="system.agent_error"), [])
        self.assertTrue(co.log.query(department=DEPT))

    def test_non_strict_run_has_no_agent_errors(self):
        co = Company(llm=MockLLM(), factories={DEPT: build_agent}, use_departments=False, strict=False)
        for topic in subscribes_for(DEPT):
            co.inject(topic, SAMPLE_BODIES.get(topic, {"summary": "x"}), recipient=DEPT)
        co.run(30)
        self.assertEqual(co.log.query(topic="system.agent_error"), [])


class DocumentTests(unittest.TestCase):
    def _read(self, name: str) -> str:
        path = DEPT_DIR / name
        self.assertTrue(path.exists(), f"{name} missing")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _assert_in_order(testcase, text: str, headings: list[str]):
        pos = 0
        for h in headings:
            m = re.search(r"^" + re.escape(h), text[pos:], re.M)
            testcase.assertIsNotNone(m, f"heading not found (or out of order): {h}")
            pos += m.end()

    def test_blueprint_headings(self):
        text = self._read("blueprint.md")
        self.assertRegex(text, r"^# .+Blueprint", )
        self._assert_in_order(self, text, [
            "# ", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles", "## 4. AI agents",
            "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies", "## 8. Sources"])

    def test_sops_headings(self):
        text = self._read("sops.md")
        self._assert_in_order(self, text, ["# ", "## Overview"])
        sops = re.findall(r"^## SOP-DELIVERY-(\d{2}): .+$", text, re.M)
        self.assertGreaterEqual(len(sops), 8)
        for sub in ("**Owner**", "**Trigger**", "**Inputs**", "### Steps", "### Outputs and messages",
                    "### SLA and controls", "### Exceptions and escalation"):
            self.assertGreaterEqual(text.count(sub), len(sops), sub)
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)

    def test_sops_cover_topics(self):
        text = self._read("sops.md")
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic {topic} not in sops")
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, text, f"subscribed topic {topic} not in sops")

    def test_kpis_headings(self):
        text = self._read("kpis.md")
        self._assert_in_order(self, text, [
            "# ", "## 1. KPI summary", "## 2. Definitions and formulas",
            "## 3. Reporting cadence and data sources", "## 4. Links to company targets"])

    def test_kpis_doc_matches_agent_kpis(self):
        text = self._read("kpis.md")
        for k in KPIS:
            self.assertIn(k.name, text, f"KPI {k.name} missing from kpis.md")

    def test_economics_headings(self):
        text = self._read("economics.md")
        self._assert_in_order(self, text, [
            "# ", "## 1. Budget", "## 2. Headcount cost build-up",
            "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md"])

    def test_economics_budget_matches_company_md(self):
        text = self._read("economics.md")
        for total in BUDGET_TOTALS_K:
            self.assertTrue(f"{total:,}" in text or str(total) in text, f"total {total}k not in economics.md")
        self.assertIn("5.4", text)

    def test_company_md_row_is_what_we_test(self):
        company = (ROOT / "COMPANY.md").read_text(encoding="utf-8")
        row = next(line for line in company.splitlines() if line.startswith("| delivery |") and "1,130" in line)
        cells = [c.strip().replace(",", "") for c in row.strip("|").split("|")]
        nums = tuple(int(c) for c in cells[1:])
        self.assertEqual(nums[:3], BUDGET_PEOPLE_K)
        self.assertEqual(nums[3:6], BUDGET_NONPEOPLE_K)
        self.assertEqual(nums[6:], BUDGET_TOTALS_K)
        for p, n, t in zip(BUDGET_PEOPLE_K, BUDGET_NONPEOPLE_K, BUDGET_TOTALS_K):
            self.assertEqual(p + n, t)

    def test_blueprint_headcount_matches_company_md(self):
        text = self._read("blueprint.md")
        for needle in ("14", "46", "104"):
            self.assertIn(needle, text)

    def test_no_placeholders_or_emojis(self):
        for name in ("blueprint.md", "sops.md", "kpis.md", "economics.md"):
            text = self._read(name)
            self.assertNotRegex(text, r"\bTBD\b|lorem ipsum", name)
            self.assertIsNone(re.search("[\U0001F300-\U0001FAFF☀-➿]", text), name)


if __name__ == "__main__":
    unittest.main()
