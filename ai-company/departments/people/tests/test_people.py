"""Contract tests for the people department (agent, workflows, docs, budget facts)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, EventLog, Kpi, Message, MessageBus, MockLLM, SimClock,
                  class_name_for, publishes_for, subscribes_for)
from departments.people import agent as people_agent
from departments.people import workflows as people_workflows
from departments.people.agent import KPIS, build_agent

DEPT = "people"
HERE = os.path.dirname(os.path.abspath(__file__))
DEPT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))

# COMPANY.md §5.4 people row (GBP thousands), §6.1 headcount
BUDGET_PEOPLE_K = (210, 400, 750)
BUDGET_NONPEOPLE_K = (100, 300, 1100)
BUDGET_TOTAL_K = (310, 700, 1850)
HUMANS = (2, 5, 10)
AGENTS = (1, 3, 6)

REQUIRED_HEADINGS = {
    "blueprint.md": [
        "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles", "## 4. AI agents",
        "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies", "## 8. Sources",
    ],
    "sops.md": ["## Overview"],
    "kpis.md": [
        "## 1. KPI summary", "## 2. Definitions and formulas", "## 3. Reporting cadence and data sources",
        "## 4. Links to company targets",
    ],
    "economics.md": [
        "## 1. Budget", "## 2. Headcount cost build-up", "## 3. Pricing and unit economics",
        "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md",
    ],
}


def make_company(**kwargs) -> Company:
    return Company(MockLLM(), factories={DEPT: build_agent}, use_departments=False, **kwargs)


def make_parts():
    clock = SimClock()
    bus = MessageBus(clock)
    log = EventLog(clock.date)
    return clock, bus, log, build_agent(MockLLM(), bus, clock, log)


def sample_body(topic: str) -> dict:
    """A rich, well-formed body usable for any subscribed topic."""
    return {
        "department": "delivery", "role_title": "Consultant", "level": "consultant", "headcount": 2,
        "requisition_id": "REQ-0001", "employee_id": "EMP-0001", "candidate_id": "CAND-0001",
        "candidate_name": "Priya Nair", "engagement_id": "EN-0001", "client_id": "CL-0001",
        "client_name": "Calder Freight Group", "summary": f"sample for {topic}", "severity": "medium",
        "amount_gbp": 60000, "due_day": 30, "start_day": 40, "reason": "resignation",
        "budget_cycle_id": "BUD-2026", "cycle_id": "BUD-2026", "requested_by": "delivery",
        "roles_needed": 2, "skills": ["ai_strategy"], "policy": "Employment Rights Act", "title": "sample",
    }


def headings_in(path: str) -> list[str]:
    with open(path, encoding="utf-8") as fh:
        return [ln.rstrip() for ln in fh if ln.startswith("#")]


class ContractTests(unittest.TestCase):
    def test_class_and_build_agent(self) -> None:
        clock, bus, log, agent = make_parts()
        self.assertEqual(class_name_for(DEPT), "PeopleAgent")
        self.assertIsInstance(agent, people_agent.PeopleAgent)
        self.assertIsInstance(agent, DepartmentAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)

    def test_build_agent_does_not_register_or_publish(self) -> None:
        clock, bus, log, agent = make_parts()
        self.assertEqual(bus.agent_names, [])
        self.assertEqual(bus.pending, [])

    def test_topic_maps(self) -> None:
        cls = people_agent.PeopleAgent
        self.assertEqual(tuple(cls.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(cls.PUBLISHES), publishes_for(DEPT))

    def test_role_matches_company_facts(self) -> None:
        agent = make_parts()[3]
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(len(agent.role.headcount_plan), 3)
        self.assertEqual(agent.role.level, "head")

    def test_kpis(self) -> None:
        self.assertGreaterEqual(len(KPIS), 8)
        self.assertTrue(all(isinstance(k, Kpi) for k in KPIS))
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))
        for n in names:
            self.assertRegex(n, r"^[a-z][a-z0-9_]*$")
        for k in KPIS:
            self.assertIsInstance(k.target, (int, float))


class HandleTests(unittest.TestCase):
    def test_handle_every_subscribed_topic(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                clock, bus, log, agent = make_parts()
                sender = topic.split(".", 1)[0]
                msg = bus.make_message(sender, DEPT, topic, sample_body(topic), sim_time=clock.day)
                out = agent.handle(msg)
                self.assertIsInstance(out, list)
                for m in out:
                    self.assertIsInstance(m, Message)
                    self.assertIn(m.topic, publishes_for(DEPT))
                    self.assertEqual(m.sender, DEPT)

    def test_handle_tolerates_empty_body(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                clock, bus, log, agent = make_parts()
                msg = bus.make_message(topic.split(".", 1)[0], DEPT, topic, {}, sim_time=clock.day)
                self.assertIsInstance(agent.handle(msg), list)

    def test_unknown_topic_returns_empty_list(self) -> None:
        clock, bus, log, agent = make_parts()
        msg = bus.make_message("finance", DEPT, "finance.month_end_closed", {}, sim_time=0)
        self.assertEqual(agent.handle(msg), [])

    def test_emitted_topics_are_published_topics(self) -> None:
        clock, bus, log, agent = make_parts()
        for topic in subscribes_for(DEPT):
            msg = bus.make_message(topic.split(".", 1)[0], DEPT, topic, sample_body(topic), sim_time=0)
            agent.handle(msg)
        for p in bus.pending:
            self.assertIn(p.topic, publishes_for(DEPT) + tuple(
                t for t in (p.topic,) if t.startswith("people.internal.")))

    def test_tick_returns_messages(self) -> None:
        clock, bus, log, agent = make_parts()
        for _ in range(400):
            out = agent.tick()
            self.assertIsInstance(out, list)
            for m in out:
                self.assertIn(m.topic, publishes_for(DEPT))
            clock.advance(1)


class BehaviourTests(unittest.TestCase):
    def _emitted(self, c: Company) -> set[str]:
        return {e.topic for e in c.log.query(department=DEPT) if e.data.get("kind") == "emit"}

    def test_hire_request_opens_requisition(self) -> None:
        c = make_company()
        c.inject("delivery.hire_requested", sample_body("delivery.hire_requested"), sender="delivery",
                 recipient=DEPT)
        c.run(5)
        self.assertIn("people.requisition_opened", self._emitted(c))
        self.assertTrue(c.log.query(department=DEPT))

    def test_headcount_approval_posts_job(self) -> None:
        c = make_company()
        c.inject("delivery.hire_requested", sample_body("delivery.hire_requested"), sender="delivery",
                 recipient=DEPT)
        c.run(3)
        c.inject("executive.headcount_approved", sample_body("executive.headcount_approved"),
                 sender="executive")
        c.run(5)
        self.assertIn("people.job_posted", self._emitted(c))

    def test_requisition_message_carries_ids(self) -> None:
        c = make_company()
        c.inject("delivery.hire_requested", sample_body("delivery.hire_requested"), sender="delivery",
                 recipient=DEPT)
        c.run(3)
        reqs = [m for m in c.bus.history if m.topic == "people.requisition_opened"]
        self.assertTrue(reqs)
        self.assertTrue(any(m.body for m in reqs))

    def test_strict_mode_hiring_chain_runs(self) -> None:
        c = make_company(strict=True)
        c.inject("delivery.hire_requested", sample_body("delivery.hire_requested"), sender="delivery",
                 recipient=DEPT)
        c.run(3)
        c.inject("executive.headcount_approved", sample_body("executive.headcount_approved"),
                 sender="executive")
        c.run(10)
        c.inject("external.candidate_applied", sample_body("external.candidate_applied"))
        c.run(60)
        for e in c.log.query(department=DEPT):
            self.assertNotEqual(e.topic, "system.agent_error")
        for t in self._emitted(c):
            self.assertIn(t, publishes_for(DEPT))

    def test_leaver_or_policy_messages_do_not_raise(self) -> None:
        c = make_company()
        c.inject("legal.regulatory_change_noted", sample_body("legal.regulatory_change_noted"),
                 sender="legal")
        c.inject("legal.policy_update_published", sample_body("legal.policy_update_published"),
                 sender="legal")
        c.inject("it_security.access_revoked", sample_body("it_security.access_revoked"),
                 sender="it_security")
        c.run(10)
        self.assertGreaterEqual(len(c.log.query(department=DEPT)), 3)


class ScenarioTests(unittest.TestCase):
    def test_scenarios_dict(self) -> None:
        self.assertGreaterEqual(len(people_workflows.SCENARIOS), 3)
        for name, fn in people_workflows.SCENARIOS.items():
            self.assertTrue(callable(fn))
            self.assertEqual(fn.__name__, f"scenario_{name}")

    def test_scenarios_build_valid_messages(self) -> None:
        for name, fn in people_workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                clock = SimClock()
                bus = MessageBus(clock)
                msgs = fn(bus, clock)
                self.assertIsInstance(msgs, list)
                self.assertTrue(msgs)
                ids = [m.id for m in msgs]
                self.assertEqual(len(ids), len(set(ids)))
                for m in msgs:
                    self.assertIsInstance(m, Message)
                    self.assertIsInstance(m.body, dict)
                    self.assertGreaterEqual(m.sim_time, 0)

    def test_at_least_one_scenario_starts_from_subscribed_topic(self) -> None:
        subs = set(subscribes_for(DEPT))
        found = False
        for fn in people_workflows.SCENARIOS.values():
            clock = SimClock()
            msgs = fn(MessageBus(clock), clock)
            if any(m.topic in subs for m in msgs):
                found = True
        self.assertTrue(found)

    def test_scenarios_run_strict_and_log_people_events(self) -> None:
        for name, fn in people_workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                c = make_company(strict=True)
                c.seed(fn(c.bus, c.clock))
                c.run(60)
                self.assertTrue(c.log.query(department=DEPT), f"{name} produced no people events")
                self.assertEqual(c.log.query(topic="system.agent_error"), [])

    def test_scenarios_emit_only_published_topics(self) -> None:
        for name, fn in people_workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                c = make_company(strict=True)
                c.seed(fn(c.bus, c.clock))
                c.run(60)
                for m in c.bus.history:
                    if m.sender == DEPT:
                        self.assertIn(m.topic, publishes_for(DEPT))

    def test_scenarios_deterministic(self) -> None:
        for name, fn in people_workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                outs = []
                for _ in range(2):
                    c = make_company(strict=True)
                    c.seed(fn(c.bus, c.clock))
                    c.run(60)
                    outs.append(c.log.to_jsonl())
                self.assertEqual(outs[0], outs[1])

    def test_all_scenarios_together_deterministic(self) -> None:
        outs = []
        for _ in range(2):
            c = make_company(strict=True)
            for fn in people_workflows.SCENARIOS.values():
                c.seed(fn(c.bus, c.clock))
            c.run(90)
            outs.append(c.log.to_jsonl())
        self.assertEqual(outs[0], outs[1])

    def test_scenarios_cover_hiring_lifecycle(self) -> None:
        c = make_company(strict=True)
        for fn in people_workflows.SCENARIOS.values():
            c.seed(fn(c.bus, c.clock))
        c.run(90)
        emitted = {m.topic for m in c.bus.history if m.sender == DEPT}
        self.assertIn("people.requisition_opened", emitted)


class DocTests(unittest.TestCase):
    def test_docs_exist_with_required_headings(self) -> None:
        for fname, required in REQUIRED_HEADINGS.items():
            path = os.path.join(DEPT_DIR, fname)
            self.assertTrue(os.path.isfile(path), f"missing {fname}")
            found = headings_in(path)
            for h in required:
                self.assertIn(h, found, f"{fname} missing heading {h!r}")
            self.assertTrue(found[0].startswith("# "), fname)

    def test_title_headings(self) -> None:
        expected = {"blueprint.md": "Blueprint", "sops.md": "Standard Operating Procedures",
                    "kpis.md": "KPIs", "economics.md": "Economics"}
        for fname, suffix in expected.items():
            first = headings_in(os.path.join(DEPT_DIR, fname))[0]
            self.assertIn("People", first)
            self.assertTrue(first.endswith(suffix), f"{fname}: {first!r}")

    def test_heading_order(self) -> None:
        for fname, required in REQUIRED_HEADINGS.items():
            found = headings_in(os.path.join(DEPT_DIR, fname))
            req = list(required)
            idx = [found.index(h) for h in req if h in found]
            self.assertEqual(idx, sorted(idx), f"{fname} headings out of order")

    def test_sops_count_and_triggers(self) -> None:
        with open(os.path.join(DEPT_DIR, "sops.md"), encoding="utf-8") as fh:
            text = fh.read()
        sops = re.findall(r"^## SOP-PEOPLE-(\d{2}): ", text, flags=re.M)
        self.assertGreaterEqual(len(sops), 8)
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, text, f"subscribed topic {topic} not referenced in sops.md")
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic {topic} not referenced in sops.md")
        for sub in ("**Owner**", "**Trigger**", "### Steps", "### SLA and controls"):
            self.assertIn(sub, text)

    def test_sops_mark_human_agent_steps(self) -> None:
        with open(os.path.join(DEPT_DIR, "sops.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)

    def test_kpis_doc_has_at_least_eight_rows_and_matches_agent(self) -> None:
        with open(os.path.join(DEPT_DIR, "kpis.md"), encoding="utf-8") as fh:
            text = fh.read()
        section = text.split("## 1. KPI summary", 1)[1].split("## 2.", 1)[0]
        rows = [ln for ln in section.splitlines() if ln.startswith("|")][2:]
        self.assertGreaterEqual(len(rows), 8)
        ids = {r.split("|")[1].strip().strip("`") for r in rows}
        for k in KPIS:
            self.assertIn(k.name, ids, f"agent KPI {k.name} missing from kpis.md summary")

    def test_blueprint_cites_company_and_human_oversight(self) -> None:
        with open(os.path.join(DEPT_DIR, "blueprint.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("COMPANY.md", text)
        self.assertNotRegex(text, r"\bTBD\b|lorem ipsum")
        self.assertIn("Chief People Officer", text)

    def test_no_placeholders_in_docs(self) -> None:
        for fname in REQUIRED_HEADINGS:
            with open(os.path.join(DEPT_DIR, fname), encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotRegex(text, r"\bTBD\b|(?i:lorem ipsum)", fname)

    def test_economics_matches_company_budget(self) -> None:
        with open(os.path.join(DEPT_DIR, "economics.md"), encoding="utf-8") as fh:
            text = fh.read()
        budget = text.split("## 1. Budget", 1)[1].split("## 2.", 1)[0]
        for value in BUDGET_TOTAL_K + BUDGET_PEOPLE_K + BUDGET_NONPEOPLE_K:
            self.assertIn(f"{value:,}", budget, f"budget value {value:,} not in economics section 1")
        recon = text.split("## 5. Reconciliation to COMPANY.md", 1)[1]
        self.assertIn("5.4", recon)

    def test_company_md_row_is_what_we_test_against(self) -> None:
        """Guards this test file against drift from COMPANY.md section 5.4 / 6.1."""
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            text = fh.read()
        cells = None
        for ln in text.splitlines():
            if ln.startswith("| people |"):
                cells = [c.strip().replace(",", "") for c in ln.strip("|").split("|")]
                if len(cells) == 10:
                    break
        self.assertIsNotNone(cells)
        nums = tuple(int(c) for c in cells[1:])
        self.assertEqual(nums[0:3], BUDGET_PEOPLE_K)
        self.assertEqual(nums[3:6], BUDGET_NONPEOPLE_K)
        self.assertEqual(nums[6:9], BUDGET_TOTAL_K)
        for p, n, t in zip(BUDGET_PEOPLE_K, BUDGET_NONPEOPLE_K, BUDGET_TOTAL_K):
            self.assertEqual(p + n, t)

    def test_blueprint_headcount_totals(self) -> None:
        with open(os.path.join(DEPT_DIR, "blueprint.md"), encoding="utf-8") as fh:
            text = fh.read()
        roles = text.split("## 3. Roles", 1)[1].split("## 4.", 1)[0]
        rows = [ln for ln in roles.splitlines() if ln.startswith("|")][2:]
        sums = [0, 0, 0]
        for r in rows:
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            if len(cells) < 6 or not all(c.isdigit() for c in cells[3:6]):
                continue
            for i in range(3):
                sums[i] += int(cells[3 + i])
        self.assertEqual(tuple(sums), HUMANS)
        agents = text.split("## 4. AI agents", 1)[1].split("## 5.", 1)[0]
        arows = [ln for ln in agents.splitlines() if ln.startswith("|")][2:]
        asums = [0, 0, 0]
        for r in arows:
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            if len(cells) < 7 or not all(c.isdigit() for c in cells[-3:]):
                continue
            for i in range(3):
                asums[i] += int(cells[-3 + i])
        self.assertEqual(tuple(asums), AGENTS)


class DeterminismTests(unittest.TestCase):
    def test_identical_runs_identical_logs(self) -> None:
        outs = []
        for _ in range(2):
            c = make_company(strict=True)
            c.inject("delivery.hire_requested", sample_body("delivery.hire_requested"),
                     sender="delivery", recipient=DEPT)
            c.inject("executive.headcount_approved", sample_body("x"), sender="executive", delay_days=2)
            c.inject("external.candidate_applied", sample_body("x"), delay_days=6)
            c.run(120)
            outs.append(c.log.to_jsonl())
        self.assertEqual(outs[0], outs[1])
        self.assertTrue(outs[0])


if __name__ == "__main__":
    unittest.main()
