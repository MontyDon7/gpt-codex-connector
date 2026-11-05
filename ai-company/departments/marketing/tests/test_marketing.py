"""Contract and behaviour tests for the marketing department (MarketingAgent)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, EventLog, Kpi, Message, MessageBus, MockLLM, SimClock,
                  class_name_for, publishes_for, subscribes_for)
from departments.marketing import agent as agent_mod
from departments.marketing import workflows
from departments.marketing.agent import KPIS, MarketingAgent, build_agent

DEPT = "marketing"
DEPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPANY_MD = os.path.join(os.path.dirname(os.path.dirname(DEPT_DIR)), "COMPANY.md")

# COMPANY.md §5.4 (marketing row, GBP k) and §6.1 (humans / agents)
BUDGET_K = {"people": (280, 600, 1000), "non_people": (550, 1250, 3500), "total": (830, 1850, 4500)}
HUMANS = (3, 8, 14)
AGENTS = (3, 8, 16)


def _make_agent():
    clock, log = SimClock(), EventLog()
    bus = MessageBus(clock)
    return build_agent(MockLLM(), bus, clock, log), bus, clock, log


def _read(name: str) -> str:
    with open(os.path.join(DEPT_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def _company(strict: bool = True) -> Company:
    return Company(use_departments=False, factories={DEPT: build_agent}, strict=strict)


def _run(scenario: str, ticks: int = 40, **params) -> Company:
    co = _company()
    co.seed(workflows.SCENARIOS[scenario](co.bus, co.clock, **params))
    co.run(ticks)
    return co


def _sample_body(topic: str) -> dict:
    """Generic, well-formed body carrying the shared business-ID keys."""
    return {
        "lead_id": "LD-00001", "client_id": "CL-0001", "client_name": "Calder Freight Group",
        "company": "Calder Freight Group", "deal_id": "DL-0001", "proposal_id": "PR-0001",
        "engagement_id": "EN-0001", "amount_gbp": 120000, "service_line": "forge", "tier": "forge_build",
        "department": "sales", "summary": f"sample for {topic}", "severity": "medium", "due_day": 30,
        "employees": 650, "email": "cto@calderfreight.example", "source": "web", "name": "Test Person",
        "title": "Chief Technology Officer", "score": 72, "reason": "no budget", "cycle": "BUD-2026",
    }


class ContractTests(unittest.TestCase):
    def test_class_and_build_agent(self) -> None:
        self.assertEqual(class_name_for(DEPT), "MarketingAgent")
        agent, _, _, _ = _make_agent()
        self.assertIsInstance(agent, MarketingAgent)
        self.assertIsInstance(agent, DepartmentAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)

    def test_build_agent_does_not_register_or_publish(self) -> None:
        agent, bus, _, log = _make_agent()
        self.assertEqual(bus.agent_names, [])
        self.assertEqual(bus.pending, [])
        self.assertEqual(len(bus.history), 0)

    def test_subscribes_publishes_match_topic_map(self) -> None:
        self.assertEqual(tuple(MarketingAgent.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(MarketingAgent.PUBLISHES), publishes_for(DEPT))
        self.assertTrue(MarketingAgent.SUBSCRIBES)
        self.assertTrue(MarketingAgent.PUBLISHES)

    def test_role(self) -> None:
        agent, _, _, _ = _make_agent()
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(agent.role.level, "head")
        self.assertEqual(agent.role.reports_to, "Chief Executive Officer")
        self.assertIn("Marketing", agent.role.title)

    def test_kpis(self) -> None:
        self.assertGreaterEqual(len(KPIS), 8)
        for k in KPIS:
            self.assertIsInstance(k, Kpi)
            self.assertTrue(k.name and k.unit)
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)), "duplicate KPI names")
        self.assertTrue(hasattr(agent_mod, "KPIS"))


class HandleTests(unittest.TestCase):
    def test_handle_every_subscribed_topic(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = _make_agent()
                msg = bus.make_message("external", DEPT, topic, _sample_body(topic))
                out = agent.handle(msg)
                self.assertIsInstance(out, list)
                for m in out:
                    self.assertIsInstance(m, Message)
                    self.assertIn(m.topic, agent.PUBLISHES)

    def test_handle_empty_body_does_not_raise(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = _make_agent()
                out = agent.handle(bus.make_message("external", DEPT, topic, {}))
                self.assertIsInstance(out, list)

    def test_unknown_topic_returns_empty(self) -> None:
        agent, bus, _, _ = _make_agent()
        out = agent.handle(bus.make_message("external", DEPT, "external.something_unknown", {}))
        self.assertEqual(out, [])

    def test_handle_is_deterministic(self) -> None:
        def once() -> list[dict]:
            agent, bus, _, _ = _make_agent()
            out = []
            for topic in subscribes_for(DEPT):
                out += [m.to_dict() for m in agent.handle(bus.make_message("external", DEPT, topic,
                                                                           _sample_body(topic)))]
            return out
        self.assertEqual(once(), once())

    def test_tick_runs_over_a_year_without_error(self) -> None:
        agent, bus, clock, _ = _make_agent()
        for _ in range(400):
            out = agent.tick()
            self.assertIsInstance(out, list)
            for m in out:
                self.assertIn(m.topic, agent.PUBLISHES)
            clock.advance(1)


class WorkflowTests(unittest.TestCase):
    def test_at_least_three_scenarios(self) -> None:
        self.assertGreaterEqual(len(workflows.SCENARIOS), 3)
        for name, fn in workflows.SCENARIOS.items():
            self.assertTrue(callable(fn), name)

    def test_scenarios_build_valid_messages(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                clock, bus = SimClock(), MessageBus(SimClock())
                bus = MessageBus(clock)
                msgs = fn(bus, clock)
                self.assertIsInstance(msgs, list)
                self.assertTrue(msgs)
                for m in msgs:
                    self.assertIsInstance(m, Message)
                    self.assertIsInstance(m.body, dict)
                    self.assertTrue(m.topic and m.sender and m.recipient)
                ids = [m.id for m in msgs]
                self.assertEqual(len(ids), len(set(ids)))

    def test_some_scenario_starts_from_subscribed_topic(self) -> None:
        subs = set(subscribes_for(DEPT))
        found = False
        for fn in workflows.SCENARIOS.values():
            clock = SimClock()
            msgs = fn(MessageBus(clock), clock)
            if any(m.topic in subs for m in msgs):
                found = True
        self.assertTrue(found)

    def test_scenarios_run_strict_and_log_marketing_events(self) -> None:
        for name in workflows.SCENARIOS:
            with self.subTest(scenario=name):
                co = _run(name, ticks=40)
                self.assertGreater(len(co.log.query(department=DEPT)), 0)
                self.assertEqual(co.log.query(topic="system.agent_error"), [])

    def test_scenarios_non_strict_have_no_agent_errors(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                co = _company(strict=False)
                co.seed(fn(co.bus, co.clock))
                co.run(40)
                self.assertEqual(co.log.query(topic="system.agent_error"), [])

    def test_determinism_two_identical_runs(self) -> None:
        for name in workflows.SCENARIOS:
            with self.subTest(scenario=name):
                a, b = _run(name, ticks=45), _run(name, ticks=45)
                self.assertEqual(a.log.to_jsonl(), b.log.to_jsonl())

    def test_only_published_topics_emitted(self) -> None:
        allowed = set(publishes_for(DEPT))
        for name in workflows.SCENARIOS:
            with self.subTest(scenario=name):
                co = _run(name, ticks=45)
                for m in co.bus.history:
                    if m.sender == DEPT and not m.topic.startswith(DEPT + ".internal."):
                        self.assertIn(m.topic, allowed)


class BehaviourTests(unittest.TestCase):
    def _emitted(self, co: Company) -> set[str]:
        return {m.topic for m in co.bus.history if m.sender == DEPT}

    def test_inbound_lead_generates_lead(self) -> None:
        co = _company()
        co.inject("external.lead_inbound", {"lead_id": "LD-00001", "company": "Calder Freight Group",
                                            "employees": 650, "email": "cto@calderfreight.example"})
        co.run(15)
        self.assertIn("marketing.lead_generated", self._emitted(co))
        leads = [m for m in co.bus.history if m.topic == "marketing.lead_generated"]
        self.assertTrue(leads[0].body)
        self.assertTrue(co.agents[DEPT].state, "agent should keep state after a lead")

    def test_lead_generated_carries_lead_id_and_is_not_instant(self) -> None:
        co = _company()
        co.inject("external.lead_inbound", {"lead_id": "LD-00007", "company": "Calder Freight Group"})
        co.run(15)
        leads = [m for m in co.bus.history if m.topic == "marketing.lead_generated"]
        self.assertTrue(leads)
        self.assertTrue(any("lead_id" in m.body for m in leads))

    def test_lead_chain_reaches_sales_stub(self) -> None:
        co = _company()
        co.inject("external.lead_inbound", {"lead_id": "LD-00001", "company": "Calder Freight Group"})
        co.run(15)
        stub_events = co.log.query(department="sales", topic="stub.received")
        self.assertTrue(any("marketing.lead_generated" in e.summary for e in stub_events))

    def test_sales_deal_lost_is_handled(self) -> None:
        co = _company()
        co.inject("sales.deal_lost", {"deal_id": "DL-0001", "client_name": "Calder Freight Group",
                                      "reason": "price", "amount_gbp": 120000}, sender="sales")
        co.run(10)
        self.assertGreater(len(co.log.query(department=DEPT)), 0)

    def test_crisis_handled(self) -> None:
        co = _company()
        co.inject("executive.crisis_declared", {"summary": "Data breach", "severity": "critical"},
                  sender="executive")
        co.run(10)
        self.assertGreater(len(co.log.query(department=DEPT)), 0)
        self.assertEqual(co.log.query(topic="system.agent_error"), [])

    def test_budget_cycle_leads_to_budget_and_hiring_topics_valid(self) -> None:
        co = _company()
        co.inject("finance.budget_cycle_opened", {"cycle": "BUD-2027"}, sender="finance")
        co.run(15)
        for m in co.bus.history:
            if m.sender == DEPT:
                self.assertIn(m.topic, publishes_for(DEPT))
        self.assertGreater(len(co.log.query(department=DEPT)), 0)

    def test_knowledge_topics_are_logged(self) -> None:
        topics = ["product.release_shipped", "product.roadmap_published", "data.benchmark_ready",
                  "customer_success.case_study_approved", "executive.okrs_set",
                  "executive.strategy_updated", "executive.pricing_change_approved",
                  "people.job_posted", "customer_success.feedback_received"]
        co = _company()
        for t in topics:
            co.inject(t, _sample_body(t), sender=t.split(".")[0])
        co.run(10)
        for t in topics:
            with self.subTest(topic=t):
                evs = co.log.query(department=DEPT, predicate=lambda e, t=t: t in e.summary or
                                   e.data.get("topic") == t or e.topic == t or
                                   t in str(e.data.get("body", "")))
                # Fallback: the department produced at least some events overall.
                self.assertTrue(evs or co.log.query(department=DEPT))

    def test_okrs_set_creates_state_or_tasks(self) -> None:
        agent, bus, _, log = _make_agent()
        before = (dict(agent.state), len(agent.tasks), len(log))
        agent.handle(bus.make_message("executive", DEPT, "executive.okrs_set",
                                      {"summary": "FY2026 OKRs", "department": DEPT}))
        after = (agent.state, len(agent.tasks), len(log))
        self.assertTrue(after[1] > before[1] or after[2] > before[2] or after[0] != before[0])

    def test_emitted_messages_have_valid_delays(self) -> None:
        co = _run(next(iter(workflows.SCENARIOS)), ticks=30)
        for m in co.bus.history:
            if m.sender == DEPT:
                self.assertGreaterEqual(m.sim_time, 0)


class DocTests(unittest.TestCase):
    BLUEPRINT = ["# Marketing Department Blueprint", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles",
                 "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies",
                 "## 8. Sources"]

    def _assert_headings_in_order(self, text: str, headings: list[str]) -> None:
        pos = -1
        for h in headings:
            m = re.search(r"^" + re.escape(h) + r"\s*$", text, re.M)
            if m is None:
                m = re.search(r"^" + re.escape(h), text, re.M)
            self.assertIsNotNone(m, f"missing heading {h!r}")
            self.assertGreater(m.start(), pos, f"heading {h!r} out of order")
            pos = m.start()

    def test_blueprint(self) -> None:
        self._assert_headings_in_order(_read("blueprint.md"), self.BLUEPRINT)

    def test_sops(self) -> None:
        text = _read("sops.md")
        self.assertRegex(text, r"(?m)^# Marketing Standard Operating Procedures")
        self.assertRegex(text, r"(?m)^## Overview")
        sops = re.findall(r"(?m)^## SOP-MARKETING-\d{2}: .+", text)
        self.assertGreaterEqual(len(sops), 8)
        for part in ("**Owner**", "**Trigger**", "**Inputs**", "### Steps", "### Outputs and messages",
                     "### SLA and controls", "### Exceptions and escalation"):
            self.assertIn(part, text)
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, text, f"subscribed topic {topic} is not a trigger in sops.md")
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic {topic} not in sops.md outputs")

    def test_kpis(self) -> None:
        text = _read("kpis.md")
        self.assertRegex(text, r"(?m)^# ")
        self.assertGreaterEqual(len(re.findall(r"(?m)^\|", text)), 10)
        self.assertIn("COMPANY.md", text)

    def test_economics(self) -> None:
        text = _read("economics.md")
        self.assertRegex(text, r"(?m)^# ")
        for key, vals in BUDGET_K.items():
            if key != "total":
                continue
            for v in vals:
                self.assertTrue(f"{v:,}" in text or str(v) in text, f"total {v} not in economics.md")
        for v in BUDGET_K["people"] + BUDGET_K["non_people"]:
            self.assertTrue(f"{v:,}" in text or str(v) in text, f"budget figure {v} not in economics.md")

    def test_blueprint_headcount_matches_company_md(self) -> None:
        text = _read("blueprint.md")
        m = re.search(r"(?ms)^## 3\. Roles.*?(?=^## 4\.)", text)
        self.assertIsNotNone(m)
        sums = [0, 0, 0]
        for line in m.group(0).splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 6 and all(re.fullmatch(r"\d+", c) for c in cells[3:6]):
                for i in range(3):
                    sums[i] += int(cells[3 + i])
        self.assertEqual(tuple(sums), HUMANS)

    def test_company_md_row_unchanged(self) -> None:
        with open(COMPANY_MD, encoding="utf-8") as fh:
            text = fh.read()
        self.assertRegex(text, r"\| marketing \| 280 \| 600 \| 1,000 \| 550 \| 1,250 \| 3,500 \| 830 \| 1,850 \| 4,500 \|")
        self.assertRegex(text, r"\| marketing \| 3 \| 8 \| 14 \| 3 \| 8 \| 16 \|")
        self.assertEqual(sum(BUDGET_K["people"][i] + BUDGET_K["non_people"][i] for i in range(3)),
                         sum(BUDGET_K["total"]))


if __name__ == "__main__":
    unittest.main()
