"""Contract and behaviour tests for the product department (agent, workflows, docs, budget, KPIs, risk review)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from core.events import EventLog
from departments.product import agent as agent_mod
from departments.product import workflows
from departments.product.agent import KPIS, ProductAgent, build_agent

DEPT = "product"
HERE = os.path.dirname(os.path.abspath(__file__))
DEPT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))

# COMPANY.md §5.4 product row (GBP k): people, non-people, total for FY2026..FY2028
BUDGET_PEOPLE = (220, 520, 1360)
BUDGET_NON_PEOPLE = (50, 100, 600)
BUDGET_TOTAL = (270, 620, 1960)
HEADCOUNT = (2, 5, 12)  # COMPANY.md §6.1 humans, year-end

DOC_HEADINGS = {
    "blueprint.md": [
        "# Product Department Blueprint", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles",
        "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies",
        "## 8. Sources",
    ],
    "sops.md": ["# Product Standard Operating Procedures", "## Overview"],
    "kpis.md": [
        "# Product KPIs", "## 1. KPI summary", "## 2. Definitions and formulas",
        "## 3. Reporting cadence and data sources", "## 4. Links to company targets",
    ],
    "economics.md": [
        "# Product Economics", "## 1. Budget", "## 2. Headcount cost build-up",
        "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md",
    ],
}


def read_doc(name: str) -> str:
    with open(os.path.join(DEPT_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def make_env():
    """Fresh (company, agent) with only product live (other departments are stubs)."""
    company = Company(MockLLM(), factories={DEPT: build_agent}, use_departments=False, strict=True)
    return company, company.agents[DEPT]


def standalone_agent():
    clock = SimClock()
    bus = MessageBus(clock)
    log = EventLog(clock.date)
    return build_agent(MockLLM(), bus, clock, log), bus, clock, log


def sample_body(topic: str) -> dict:
    """A well-formed body that uses the shared business-ID keys from CONVENTIONS section 4."""
    return {
        "client_id": "CL-0007", "client_name": "Calder Freight Group", "deal_id": "DL-0001",
        "engagement_id": "EN-0001", "contract_id": "CT-0001", "amount_gbp": 60000, "service_line": "forge",
        "tier": "forge_build", "department": "sales", "summary": f"test {topic}", "due_day": 30,
        "severity": "high", "year": 2027, "budget_cycle_id": "BUD-2027", "score": 2,
    }


def rich_body(topic: str) -> dict:
    """Bodies shaped like the real publishers' messages (legal, it_security, data, executive, finance)."""
    base = sample_body(topic)
    rich = {
        "legal.ai_risk_review_completed": {
            "review_id": "AIR-0001", "agent_name": "Keep support triage agent", "risk_tier": "limited",
            "recommendation": "cleared_with_conditions", "conditions": ["human approval for closure"],
            "dpia_required": False, "status": "recommendation_pending_gc_signoff"},
        "it_security.vulnerability_found": {
            "vulnerability_id": "VULN-0001", "severity": "critical", "component": "retrieval", "cvss": 9.1,
            "exploited_in_wild": True, "due_day": 2, "release_id": "REL-0001", "sla_hours": 24},
        "data.agent_quality_report_published": {
            "report_id": "AQR-1", "agent": "triage agent", "quality_score": 72, "coverage_pct": 90},
        "executive.okrs_set": {"objectives": ["Ship 6 capabilities", {"title": "Raise reuse to 40%"}]},
        "executive.budget_approved": {"budget_cycle_id": "BUD-2027", "departments": {"product": 620000}},
        "legal.regulatory_change_noted": {"regulation_id": "REG-1", "title": "EU AI Act high-risk duties",
                                          "impact_areas": ["high-risk"], "severity": "high", "effective_day": 90},
        "external.technology_release_published": {"vendor": "Quillstone AI", "product": "Quillstone Large",
                                                 "version": "4.2", "release_type": "foundation model"},
        "customer_success.support_escalated": {"client_id": "CL-0003", "severity": "high", "category": "defect",
                                               "agent": "triage agent", "ticket_id": "SUP-1"},
        "executive.crisis_declared": {"crisis_id": "CRS-1", "category": "security", "severity": "critical"},
    }
    base.update(rich.get(topic, {}))
    return base


def external_sender(topic: str) -> str:
    return "external" if topic.startswith("external.") else topic.split(".", 1)[0]


class ContractTests(unittest.TestCase):
    def test_class_name(self) -> None:
        self.assertEqual(class_name_for(DEPT), "ProductAgent")
        self.assertTrue(issubclass(ProductAgent, DepartmentAgent))

    def test_build_agent(self) -> None:
        agent, bus, _, _ = standalone_agent()
        self.assertIsInstance(agent, ProductAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)
        self.assertEqual(bus.agent_names, [], "build_agent must not register with the bus")
        self.assertEqual(len(bus.pending), 0, "build_agent must not publish")

    def test_topic_map(self) -> None:
        self.assertEqual(tuple(ProductAgent.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(ProductAgent.PUBLISHES), publishes_for(DEPT))
        self.assertGreater(len(ProductAgent.SUBSCRIBES), 0)
        self.assertGreater(len(ProductAgent.PUBLISHES), 0)

    def test_head_role(self) -> None:
        agent, _, _, _ = standalone_agent()
        self.assertEqual(agent.role.title, "Chief Product Officer")
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(agent.role.level, "head")
        self.assertEqual(tuple(agent.role.headcount_plan), (1, 1, 1))
        self.assertEqual(tuple(agent.role.salary_band_gbp), (140000, 200000))
        self.assertEqual(agent.role.reports_to, "Chief Executive Officer")

    def test_kpis(self) -> None:
        self.assertGreaterEqual(len(KPIS), 8)
        self.assertTrue(all(isinstance(k, Kpi) for k in KPIS))
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))

    def test_kpis_mirror_kpis_md(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("\n## 2.", 1)[0]
        rows = {}
        for r in section.splitlines():
            if re.match(r"^\| [a-z0-9_]+ \|", r):
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                rows[cells[0]] = cells
        self.assertEqual(sorted(rows), sorted(k.name for k in KPIS))
        for k in KPIS:
            cells = rows[k.name]
            self.assertEqual(cells[2], k.unit, k.name)
            self.assertAlmostEqual(float(cells[3]), float(k.target), places=6, msg=k.name)
            self.assertEqual(cells[6].startswith("higher"), k.higher_is_better, k.name)

    def test_kpi_directions(self) -> None:
        by_name = {k.name: k for k in KPIS}
        for lower in ("open_critical_high_findings", "eval_cycle_days", "budget_variance_pct"):
            self.assertFalse(by_name[lower].higher_is_better, lower)
        for higher in ("roadmap_delivery_pct", "agent_quality_score", "capabilities_shipped"):
            self.assertTrue(by_name[higher].higher_is_better, higher)

    def test_fy2026_targets(self) -> None:
        expected = {"roadmap_delivery_pct": 70, "release_gate_first_pass_pct": 80, "agent_quality_score": 85,
                    "open_critical_high_findings": 0, "ai_risk_review_coverage_pct": 100, "vuln_fix_sla_pct": 90,
                    "release_cadence_adherence_pct": 85, "feedback_triage_sla_pct": 90, "capabilities_shipped": 6,
                    "platform_reuse_pct": 40, "eval_cycle_days": 5, "budget_variance_pct": 5}
        self.assertEqual({k.name: k.target for k in KPIS}, {k: float(v) for k, v in expected.items()})

    def test_constants_mirror_sops_table(self) -> None:
        doc = read_doc("sops.md").split("## Constants and thresholds", 1)[1]
        self.assertEqual(agent_mod.ROADMAP_MIN_RICE, 2.0)
        self.assertIn("2.0", doc)
        self.assertEqual(agent_mod.RESERVED_CAPACITY_PCT + agent_mod.COMMITTED_CAPACITY_PCT, 100)
        self.assertEqual(agent_mod.RESERVED_CAPACITY_PCT, 20)
        self.assertEqual((agent_mod.BETA_EVAL_SCORE, agent_mod.RELEASE_EVAL_SCORE), (80, 85))
        self.assertEqual((agent_mod.AGENT_QUALITY_FLOOR, agent_mod.AGENT_QUALITY_FREEZE), (80, 70))
        self.assertEqual((agent_mod.CLUSTER_MIN_CLIENTS, agent_mod.RELEASE_TRAIN_DAYS), (3, 14))
        self.assertEqual(agent_mod.VULN_SLA_DAYS, {"critical": 7, "high": 30, "medium": 60, "low": 90})
        self.assertEqual(agent_mod.VULN_VERIFY_BUFFER_DAYS, 2)
        self.assertEqual(agent_mod.AGENT_DAY_RATE_GBP, 350)
        self.assertEqual((agent_mod.NON_BUDGETED_SPEND_CFO_GBP, agent_mod.NON_BUDGETED_SPEND_CEO_GBP),
                         (50_000, 250_000))
        self.assertEqual(sorted(agent_mod.RISK_TRIGGERS), [f"RT-{i}" for i in range(1, 9)])
        for name in ("ROADMAP_MIN_RICE", "RESERVED_CAPACITY_PCT", "CLUSTER_MIN_CLIENTS", "RELEASE_TRAIN_DAYS",
                     "EVAL_MIN_CASES", "BETA_EVAL_SCORE", "RELEASE_EVAL_SCORE", "AGENT_QUALITY_FLOOR",
                     "AGENT_QUALITY_FREEZE", "VULN_VERIFY_BUFFER_DAYS", "BUDGET_SUBMISSION_DAY"):
            self.assertIn(name, doc)
            self.assertTrue(hasattr(agent_mod, name), name)


class HandleTests(unittest.TestCase):
    def test_handle_every_subscribed_topic(self) -> None:
        for topic in subscribes_for(DEPT):
            for label, make in (("plain", sample_body), ("rich", rich_body)):
                with self.subTest(topic=topic, body=label):
                    agent, bus, _, _ = standalone_agent()
                    msg = bus.make_message(external_sender(topic), DEPT, topic, make(topic), sim_time=0)
                    out = agent.handle(msg)
                    self.assertIsInstance(out, list)
                    for m in out:
                        self.assertIsInstance(m, Message)
                        self.assertIn(m.topic, agent.PUBLISHES)
                        self.assertTrue(m.topic.startswith("product."))
                        self.assertNotIn(".internal.", m.topic)

    def test_handle_tolerates_empty_body(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                msg = bus.make_message(external_sender(topic), DEPT, topic, {}, sim_time=0)
                self.assertIsInstance(agent.handle(msg), list)

    def test_handle_tolerates_wrong_types(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                body = {"severity": 5, "amount_gbp": "n/a", "objectives": 7, "conditions": "x", "due_day": "soon",
                        "quality_score": "high", "score": None, "departments": [], "impact_areas": "all"}
                self.assertIsInstance(agent.handle(bus.make_message(external_sender(topic), DEPT, topic, body,
                                                                    sim_time=0)), list)

    def test_unknown_topic_does_not_raise(self) -> None:
        agent, bus, _, _ = standalone_agent()
        msg = bus.make_message("sales", DEPT, "sales.lead_qualified_unknown", {}, sim_time=0)
        self.assertEqual(agent.handle(msg), [])

    def test_handle_is_deterministic(self) -> None:
        results = []
        for _ in range(2):
            agent, bus, _, log = standalone_agent()
            for topic in subscribes_for(DEPT):
                agent.handle(bus.make_message(external_sender(topic), DEPT, topic, rich_body(topic), sim_time=0))
            results.append(log.to_jsonl())
        self.assertEqual(results[0], results[1])

    def test_log_event_never_passes_topic_in_data(self) -> None:
        with open(os.path.join(DEPT_DIR, "agent.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotRegex(src, r"log_event\([^)]*\btopic=")

    def test_tick_runs_over_a_year_without_error(self) -> None:
        company, agent = make_env()
        company.run(370)
        self.assertGreater(len(company.log.query(department=DEPT)), 0)
        self.assertEqual(company.log.query(topic="system.agent_error"), [])
        for m in agent.tick() or []:
            self.assertIn(m.topic, agent.PUBLISHES)

    def test_only_published_topics_are_emitted_over_three_years(self) -> None:
        company, _ = make_env()
        company.run(3 * 365)
        emitted = {e.topic for e in company.log.query(department=DEPT) if e.data.get("kind") == "emit"}
        self.assertTrue(emitted <= set(publishes_for(DEPT)), emitted - set(publishes_for(DEPT)))
        self.assertFalse([t for t in emitted if ".internal." in t])


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
                msgs = fn(MessageBus(clock), clock)
                self.assertGreater(len(msgs), 0)
                ids = [m.id for m in msgs]
                self.assertEqual(len(ids), len(set(ids)))
                for m in msgs:
                    self.assertIsInstance(m, Message)
                    self.assertIsInstance(m.body, dict)
                    self.assertIsInstance(m.sim_time, int)
                    self.assertGreaterEqual(m.sim_time, clock.day)

    def test_scenarios_start_from_subscribed_topics(self) -> None:
        subs = set(subscribes_for(DEPT))
        for name, fn in workflows.SCENARIOS.items():
            clock = SimClock()
            msgs = fn(MessageBus(clock), clock)
            self.assertTrue(any(m.topic in subs for m in msgs), name)

    def test_scenarios_cover_most_subscribed_topics(self) -> None:
        seeded = set()
        for fn in workflows.SCENARIOS.values():
            clock = SimClock()
            seeded |= {m.topic for m in fn(MessageBus(clock), clock)}
        self.assertGreaterEqual(len(seeded & set(subscribes_for(DEPT))), 12)

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

    @staticmethod
    def _live_factories() -> dict:
        """Product plus the finished neighbours it talks to (Legal, Finance, Executive); others are stubs."""
        from departments.executive.agent import build_agent as build_exec
        from departments.finance.agent import build_agent as build_fin
        from departments.legal.agent import build_agent as build_legal
        return {DEPT: build_agent, "legal": build_legal, "finance": build_fin, "executive": build_exec}

    def test_every_scenario_runs_with_all_departments_if_present(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company = Company(MockLLM(), factories=self._live_factories(), use_departments=False,
                                  strict=False)
                company.seed(fn(company.bus, company.clock))
                company.run(45)
                errors = [e for e in company.log.query(topic="system.agent_error") if e.department == DEPT]
                self.assertEqual(errors, [])

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
            fn(MessageBus(clock), clock)


class BehaviourTests(unittest.TestCase):
    """Lifecycle behaviours: roadmap, stage-gated releases, capabilities, findings, risk review round trips."""

    def _emitted(self, company: Company, topic: str | None = None) -> list:
        return [e for e in company.log.query(department=DEPT)
                if e.data.get("kind") == "emit" and (topic is None or e.topic == topic)]

    def _inject_run(self, topic: str, body: dict, days: int = 30, sender: str | None = None):
        company, agent = make_env()
        company.inject(topic, body, recipient=DEPT, sender=sender or external_sender(topic))
        company.run(days)
        return company, agent

    def _company_until_review(self):
        """Run until Product has asked Legal for an AI risk review; return (company, agent, review body)."""
        company, agent = make_env()
        for _ in range(400):
            company.run(1)
            reqs = self._emitted(company, "product.ai_risk_review_requested")
            if reqs:
                return company, agent, reqs[0].data["body"]
        self.fail("no AI risk review was requested within 400 days")

    # roadmap ------------------------------------------------------------------------------------
    def test_okrs_publish_roadmap_with_reserved_capacity(self) -> None:
        company, _ = self._inject_run("executive.okrs_set", {"objectives": ["Ship 6 reusable capabilities"]}, 10)
        roadmaps = self._emitted(company, "product.roadmap_published")
        self.assertTrue(roadmaps)
        body = roadmaps[0].data["body"]
        self.assertEqual(body["reserved_capacity_pct"], 20)
        self.assertGreater(body["committed_count"], 0)
        self.assertEqual(body["committed_count"], len(body["committed"]))
        for item in body["committed"]:
            self.assertTrue(item["rice_score"] >= agent_mod.ROADMAP_MIN_RICE or item["exempt_reason"])
            self.assertEqual(item["gate_target"], "G4")

    def test_rice_formula_and_minimum(self) -> None:
        self.assertEqual(ProductAgent._rice(8, 2, 0.8, 5), 2.56)
        self.assertEqual(ProductAgent._rice(4, 0.5, 0.5, 6), 0.17)
        company, agent = self._inject_run("executive.okrs_set", {}, 5)
        backlog = agent.state["backlog"]
        committed = [i for i in backlog.values() if i["status"] == "committed"]
        self.assertTrue(committed)
        for item in backlog.values():
            if item["rice_score"] < agent_mod.ROADMAP_MIN_RICE and not item["exempt"]:
                self.assertNotEqual(item["status"], "committed", item["title"])

    def test_strategy_update_republishes_roadmap(self) -> None:
        company, _ = make_env()
        company.inject("executive.okrs_set", {}, recipient=DEPT, sender="executive")
        company.run(3)
        company.inject("executive.strategy_updated", {"objectives": ["US data-residency option"]},
                       recipient=DEPT, sender="executive")
        company.run(15)
        roadmaps = self._emitted(company, "product.roadmap_published")
        self.assertGreaterEqual(len(roadmaps), 2)
        self.assertIn("strategy_updated", {e.data["body"]["trigger"] for e in roadmaps})

    def test_quarterly_cadence_publishes_roadmap(self) -> None:
        company, _ = make_env()
        company.run(200)
        triggers = [e.data["body"]["trigger"] for e in self._emitted(company, "product.roadmap_published")]
        self.assertGreaterEqual(triggers.count("quarterly"), 2)

    # stage-gated releases and capabilities -------------------------------------------------------
    def test_release_train_ships_stage_gated_releases(self) -> None:
        company, agent = make_env()
        company.run(150)
        releases = self._emitted(company, "product.release_shipped")
        self.assertTrue(releases)
        for e in releases:
            b = e.data["body"]
            self.assertEqual(b["gate"], "G4")
            if b["client_facing"] and b["release_type"] != "hotfix":
                self.assertGreaterEqual(b["eval_score"], agent_mod.RELEASE_EVAL_SCORE)
                self.assertLessEqual(b["open_medium_findings"], agent_mod.MAX_OPEN_MEDIUM_FINDINGS)
        gates = [g for g in agent.state["gates"].values()]
        self.assertTrue(gates)
        self.assertTrue(any(g["stage"] == "G4" for g in gates))

    def test_capability_added_after_release(self) -> None:
        company, agent = make_env()
        company.run(250)
        caps = self._emitted(company, "product.agent_capability_added")
        self.assertTrue(caps)
        self.assertGreaterEqual(len(agent.state["capabilities"]), 1)
        self.assertEqual(agent.kpi_snapshot()[8].name, "capabilities_shipped")
        self.assertGreaterEqual(agent.kpi_snapshot()[8].actual, 1)

    def test_release_train_respects_14_day_cadence(self) -> None:
        company, _ = make_env()
        company.run(120)
        days = sorted({e.sim_time for e in self._emitted(company, "product.release_shipped")
                       if e.data["body"]["release_type"] != "hotfix"})
        self.assertTrue(days)
        for a, b in zip(days, days[1:]):
            self.assertGreaterEqual(b - a, 1)
        self.assertTrue(all(d % 7 == 3 for d in days), days)  # Day 0 is a Monday, trains ship on Thursdays

    # escalations and feedback ---------------------------------------------------------------------
    def test_high_severity_defect_escalation_ships_hotfix(self) -> None:
        body = {"client_id": "CL-0003", "severity": "high", "category": "defect", "agent": "triage agent",
                "ticket_id": "SUP-1", "summary": "Defect: wrong totals posted"}
        company, agent = self._inject_run("customer_success.support_escalated", body, 10)
        hotfixes = [e for e in self._emitted(company, "product.release_shipped")
                    if e.data["body"]["release_type"] == "hotfix"]
        self.assertTrue(hotfixes)
        self.assertEqual(agent.state["fb_on_time"], agent.state["fb_total"])

    def test_three_clients_form_a_feedback_cluster(self) -> None:
        company, agent = make_env()
        for cid in ("CL-0001", "CL-0002", "CL-0003"):
            company.inject("customer_success.feedback_received",
                           {"client_id": cid, "category": "defect", "agent": "a1", "score": 2},
                           recipient=DEPT, sender="customer_success")
        company.run(5)
        self.assertEqual(len(agent.state["clusters"]), 1)
        item = agent.state["backlog"][next(iter(agent.state["clusters"].values()))["item_id"]]
        self.assertEqual(item["source"], "feedback cluster")

    def test_security_escalation_does_not_ship_hotfix_directly(self) -> None:
        body = {"client_id": "CL-0003", "severity": "critical", "summary": "Agent leaked client data (security)"}
        company, _ = self._inject_run("customer_success.support_escalated", body, 5)
        self.assertEqual([e for e in self._emitted(company, "product.release_shipped")
                          if e.data["body"]["release_type"] == "hotfix"], [])

    # evaluation findings --------------------------------------------------------------------------
    def test_quality_below_freeze_creates_agent_freeze(self) -> None:
        body = {"report_id": "AQR-1", "agent": "triage agent", "quality_score": 68}
        _, agent = self._inject_run("data.agent_quality_report_published", body, 5)
        self.assertTrue([f for f in agent.state["freezes"].values() if f["agent"] == "triage agent"
                         and f["status"] == "active"])

    def test_quality_report_without_score_is_tolerated(self) -> None:
        company, agent = self._inject_run("data.agent_quality_report_published", {"report_id": "AQR-2"}, 5)
        self.assertEqual(agent.state["freezes"], {})
        self.assertEqual(company.log.query(topic="system.agent_error"), [])

    def test_quality_between_floor_and_freeze_creates_remediation_task_only(self) -> None:
        body = {"agent": "triage agent", "quality_score": 76}
        _, agent = self._inject_run("data.agent_quality_report_published", body, 5)
        self.assertEqual(agent.state["freezes"], {})
        self.assertTrue(any("Remediation" in t.title for t in agent.tasks.values()))

    def test_high_data_quality_issue_holds_and_opens_finding(self) -> None:
        body = {"dataset": "golden-set-kyc", "severity": "high"}
        _, agent = self._inject_run("data.data_quality_issue_raised", body, 5)
        self.assertTrue(agent.state["findings"])
        self.assertTrue(agent.state["data_holds"])

    # vulnerabilities ------------------------------------------------------------------------------
    def test_vulnerability_fix_round_trip(self) -> None:
        body = {"vulnerability_id": "VULN-0009", "severity": "critical", "component": "retrieval",
                "exploited_in_wild": True, "due_day": 1, "release_id": "REL-0001"}
        company, agent = self._inject_run("it_security.vulnerability_found", body, 10)
        fixed = self._emitted(company, "product.vulnerability_fixed")
        self.assertEqual(len(fixed), 1)
        fb = fixed[0].data["body"]
        self.assertEqual(fb["vulnerability_id"], "VULN-0009")
        self.assertEqual(agent.state["vulns"]["VULN-0009"]["internal_due_day"], 1)  # floor of one day

    def test_vulnerability_internal_due_is_two_days_before_it_security(self) -> None:
        company, agent = make_env()
        company.inject("it_security.vulnerability_found",
                       {"vulnerability_id": "VULN-0010", "severity": "high", "due_day": 30},
                       recipient=DEPT, sender="it_security")
        company.run(2)
        self.assertEqual(agent.state["vulns"]["VULN-0010"]["internal_due_day"], 28)

    def test_vulnerability_without_due_day_uses_sla(self) -> None:
        company, agent = make_env()
        company.inject("it_security.vulnerability_found", {"vulnerability_id": "V-1", "severity": "medium"},
                       recipient=DEPT, sender="it_security")
        company.run(1)
        v = agent.state["vulns"]["V-1"]
        self.assertEqual(v["it_due_day"] - v["received_day"], 60)

    # AI risk review round trips -------------------------------------------------------------------
    def test_risk_review_requested_with_triggers(self) -> None:
        _, _, body = self._company_until_review()
        self.assertRegex(body["review_id"], r"^AIR-\d{4}$")
        self.assertTrue(body["triggers"])
        self.assertTrue(all(t in agent_mod.RISK_TRIGGERS for t in body["triggers"]))
        self.assertIn("agent_name", body)

    def test_pending_legal_recommendation_is_not_final_clearance(self) -> None:
        company, agent, req = self._company_until_review()
        rid = req["review_id"]
        company.inject("legal.ai_risk_review_completed", {
            "review_id": rid, "agent_name": req["agent_name"], "risk_tier": "limited",
            "recommendation": "cleared_subject_to_standard_controls", "conditions": [],
            "status": "recommendation_pending_gc_signoff"}, recipient=DEPT, sender="legal")
        company.run(1)
        rec = agent.state["reviews"][rid]
        self.assertEqual(rec["status"], "awaiting_signoff")
        company.run(agent_mod.AI_SIGNOFF_DAYS + 2)
        self.assertEqual(agent.state["reviews"][rid]["status"], "cleared")

    def test_final_legal_clearance_lifts_hold_immediately(self) -> None:
        company, agent, req = self._company_until_review()
        rid = req["review_id"]
        company.inject("legal.ai_risk_review_completed", {
            "review_id": rid, "risk_tier": "minimal", "recommendation": "cleared_subject_to_standard_controls",
            "status": "signed_off"}, recipient=DEPT, sender="legal")
        company.run(1)
        self.assertEqual(agent.state["reviews"][rid]["status"], "cleared")

    def test_legal_outcome_key_is_accepted(self) -> None:
        company, agent, req = self._company_until_review()
        rid = req["review_id"]
        company.inject("legal.ai_risk_review_completed", {"review_id": rid, "outcome": "cleared"},
                       recipient=DEPT, sender="legal")
        company.run(1)
        self.assertEqual(agent.state["reviews"][rid]["status"], "cleared")

    def test_conditions_hold_until_evidenced(self) -> None:
        company, agent, req = self._company_until_review()
        rid = req["review_id"]
        company.inject("legal.ai_risk_review_completed", {
            "review_id": rid, "risk_tier": "limited", "recommendation": "cleared_with_conditions",
            "conditions": ["human approval", "log retention"], "status": "signed_off"},
            recipient=DEPT, sender="legal")
        company.run(1)
        self.assertEqual(agent.state["reviews"][rid]["status"], "conditions_pending")
        company.run(20)
        self.assertEqual(agent.state["reviews"][rid]["status"], "cleared")

    def test_blocked_review_blocks_item_and_never_clears(self) -> None:
        company, agent, req = self._company_until_review()
        rid = req["review_id"]
        company.inject("legal.ai_risk_review_completed", {
            "review_id": rid, "risk_tier": "prohibited", "recommendation": "blocked_pending_gc",
            "status": "recommendation_pending_gc_signoff"}, recipient=DEPT, sender="legal")
        company.run(10)
        self.assertEqual(agent.state["reviews"][rid]["status"], "blocked")
        self.assertTrue([i for i in agent.state["backlog"].values() if i["review_id"] == rid
                         and i["status"] == "blocked"] or req["ref"].startswith(("RT", "REG", "quality", "TECH")))

    def test_unknown_review_id_creates_reconciliation_task_only(self) -> None:
        company, agent = self._inject_run("legal.ai_risk_review_completed",
                                          {"review_id": "AIR-9999", "recommendation": "cleared"}, 3, "legal")
        self.assertEqual(self._emitted(company, "product.release_shipped"), [])
        self.assertTrue(any("unknown review" in t.title for t in agent.tasks.values()))

    def test_review_coverage_kpi_is_full(self) -> None:
        company, agent, _ = self._company_until_review()
        company.run(60)
        by_name = {k.name: k for k in agent.kpi_snapshot()}
        self.assertEqual(by_name["ai_risk_review_coverage_pct"].actual, 100.0)

    def test_full_round_trip_with_real_legal_agent(self) -> None:
        from departments.legal.agent import build_agent as build_legal
        company = Company(MockLLM(), factories={DEPT: build_agent, "legal": build_legal}, use_departments=False,
                          strict=True)
        company.run(200)
        self.assertTrue(self._emitted(company, "product.ai_risk_review_requested"))
        completed = [e for e in company.log.query(department="legal") if e.topic == "legal.ai_risk_review_completed"]
        self.assertTrue(completed)
        agent = company.agents[DEPT]
        self.assertTrue(agent.state["agent_register"])
        for rec in agent.state["reviews"].values():
            self.assertNotEqual(rec["status"], "requested", "Legal reply should have been processed")
        self.assertEqual(company.log.query(topic="system.agent_error"), [])

    # technology, regulation, crisis ---------------------------------------------------------------
    def test_regulatory_change_creates_exempt_compliance_item(self) -> None:
        body = {"regulation_id": "REG-1", "title": "EU AI Act high-risk duties", "impact_areas": ["high-risk"],
                "severity": "high", "effective_day": 200}
        _, agent = self._inject_run("legal.regulatory_change_noted", body, 3, "legal")
        items = [i for i in agent.state["backlog"].values() if i["source"] == "regulatory change"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["exempt"], "regulatory")

    def test_crisis_freezes_releases_but_not_hotfixes(self) -> None:
        company, agent = make_env()
        company.inject("executive.crisis_declared", {"crisis_id": "CRS-1", "category": "security",
                                                     "severity": "critical"}, recipient=DEPT, sender="executive")
        company.run(21)
        self.assertTrue([f for f in agent.state["freezes"].values() if f["scope"] == "all"])
        trains = [e for e in self._emitted(company, "product.release_shipped")
                  if e.data["body"]["release_type"] != "hotfix"]
        self.assertEqual(trains, [])

    def test_technology_release_is_assessed(self) -> None:
        body = {"vendor": "Quillstone AI", "product": "Quillstone Large", "version": "4.2",
                "release_type": "foundation model"}
        _, agent = self._inject_run("external.technology_release_published", body, 3)
        self.assertEqual(len(agent.state["tech"]), 1)

    # budget, pricing, hiring ----------------------------------------------------------------------
    def test_budget_cycle_submissions_match_envelopes(self) -> None:
        for cycle, year, total in (("BUD-2027", 2027, 620000), ("BUD-2028", 2028, 1960000)):
            with self.subTest(cycle=cycle):
                company, _ = self._inject_run("finance.budget_cycle_opened",
                                              {"budget_cycle_id": cycle, "year": year}, 5, "finance")
                subs = self._emitted(company, "product.budget_submitted")
                self.assertTrue(subs)
                self.assertEqual(subs[0].data["body"]["amount_gbp"], total)
                self.assertEqual(subs[0].data["body"]["department"], DEPT)

    def test_budget_submitted_in_q4_from_tick_cadence(self) -> None:
        company, _ = make_env()
        company.run(300)
        subs = self._emitted(company, "product.budget_submitted")
        self.assertEqual([e.data["body"]["amount_gbp"] for e in subs], [620000])

    def test_budget_approved_sets_variance(self) -> None:
        _, agent = self._inject_run("executive.budget_approved",
                                    {"budget_cycle_id": "BUD-2027", "departments": {"product": 600000}}, 3,
                                    "executive")
        self.assertAlmostEqual(agent.state["budget_variance_pct"], 20000 / 620000 * 100, places=6)

    def test_hire_requests_follow_blueprint_plan(self) -> None:
        company, _ = make_env()
        company.run(400)
        hires = self._emitted(company, "product.hire_requested")
        self.assertTrue(hires)
        self.assertEqual(hires[0].data["body"]["role"], "Product Manager")
        for e in hires:
            self.assertEqual(e.data["body"]["department"], DEPT)

    def test_pricing_proposal_is_emitted_for_cost_pressure(self) -> None:
        company, _ = self._inject_run("executive.strategy_updated",
                                      {"pricing_review": True, "agent_cost_per_agent_year_gbp": 60000}, 15,
                                      "executive")
        proposals = self._emitted(company, "product.pricing_change_proposed")
        self.assertTrue(proposals)

    def test_state_is_updated(self) -> None:
        _, agent = self._inject_run("executive.okrs_set", {}, 3)
        self.assertTrue(agent.state["roadmaps"])

    def test_no_wall_clock_or_uuid_in_sources(self) -> None:
        for fname in ("agent.py", "workflows.py"):
            with open(os.path.join(DEPT_DIR, fname), encoding="utf-8") as fh:
                src = fh.read()
            for banned in ("uuid4", "datetime.now", "date.today", "time.time(", "import requests",
                           "urllib.request", "import random"):
                self.assertNotIn(banned, src, f"{fname} contains {banned}")


class DeterminismTests(unittest.TestCase):
    def test_full_run_is_reproducible(self) -> None:
        dumps = []
        for _ in range(2):
            company, _ = make_env()
            for fn in workflows.SCENARIOS.values():
                company.seed(fn(company.bus, company.clock))
            company.run(120)
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
        ids = re.findall(r"^## (SOP-PRODUCT-\d{2}): ", text, flags=re.M)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for sub in ("### Steps", "### Outputs and messages", "### SLA and controls",
                    "### Exceptions and escalation"):
            self.assertGreaterEqual(text.count(sub), len(ids), sub)
        for field in ("**Owner**:", "**Trigger**:", "**Inputs**:"):
            self.assertGreaterEqual(text.count(field), len(ids), field)

    def test_every_subscribed_topic_is_a_sop_trigger(self) -> None:
        text = read_doc("sops.md")
        blocks = re.split(r"^## SOP-PRODUCT-\d{2}: ", text, flags=re.M)[1:]
        triggers = " ".join(re.search(r"\*\*Trigger\*\*:(.*)", b).group(1) for b in blocks)
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, triggers, f"subscribed topic {topic} is not the Trigger of any SOP")

    def test_every_published_topic_is_in_sop_outputs(self) -> None:
        text = read_doc("sops.md")
        outputs = "".join(re.findall(r"### Outputs and messages(.*?)### SLA and controls", text, flags=re.S))
        for topic in publishes_for(DEPT):
            self.assertIn(topic, outputs, f"published topic {topic} not in any SOP outputs")

    def test_sops_mark_steps_human_or_agent(self) -> None:
        text = read_doc("sops.md")
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)

    def test_sops_define_constants_table(self) -> None:
        text = read_doc("sops.md")
        self.assertIn("## Constants and thresholds", text)
        for rt in range(1, 9):
            self.assertIn(f"RT-{rt}", text)

    def test_blueprint_mentions_head_and_agent_class(self) -> None:
        text = read_doc("blueprint.md")
        self.assertIn("Chief Product Officer", text)
        self.assertIn("ProductAgent", text)

    def test_role_titles_in_agents_and_kpis_come_from_blueprint(self) -> None:
        blueprint = read_doc("blueprint.md")
        roles = blueprint.split("## 3. Roles", 1)[1].split("\n## 4.", 1)[0]
        titles = {r.strip().strip("|").split("|")[0].strip() for r in roles.splitlines()
                  if re.match(r"^\| [A-Z]", r) and not r.startswith("| Role title")}
        for role, *_ in agent_mod.HIRING_PLAN:
            self.assertIn(role, titles)
        self.assertIn("Chief Product Officer", titles)

    def test_kpi_doc_has_twelve_kpis(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("## 2.", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)]
        self.assertEqual(len(rows), 12)
        self.assertEqual(len(rows), len(KPIS))


class BudgetTests(unittest.TestCase):
    def test_company_md_row_is_what_we_expect(self) -> None:
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            row = next(r for r in fh.read().splitlines() if r.startswith("| product |") and "270" in r)
        nums = [int(c.replace(",", "")) for c in re.findall(r"[\d,]+", row)]
        self.assertEqual(tuple(nums[:3]), BUDGET_PEOPLE)
        self.assertEqual(tuple(nums[3:6]), BUDGET_NON_PEOPLE)
        self.assertEqual(tuple(nums[6:9]), BUDGET_TOTAL)

    def test_totals_are_internally_consistent(self) -> None:
        for p, n, t in zip(BUDGET_PEOPLE, BUDGET_NON_PEOPLE, BUDGET_TOTAL):
            self.assertEqual(p + n, t)

    def test_agent_envelope_constants_match_company_md(self) -> None:
        for i, year in enumerate((2026, 2027, 2028)):
            self.assertEqual(agent_mod.BUDGET_ENVELOPE_GBP_K[year],
                             (BUDGET_TOTAL[i], BUDGET_PEOPLE[i], BUDGET_NON_PEOPLE[i]))
            self.assertLessEqual(abs(agent_mod.PEOPLE_BUILD_UP_GBP_K[year] - BUDGET_PEOPLE[i]), 5)
            self.assertEqual(agent_mod.HEADCOUNT_PLAN[year][0], HEADCOUNT[i])

    def test_economics_states_envelope_totals(self) -> None:
        text = read_doc("economics.md")
        for total in ("270", "620", "1,960"):
            self.assertRegex(text, rf"(?<![\d,.]){re.escape(total)}(?![\d])", f"total {total} missing")
        for people in ("220", "520", "1,360"):
            self.assertRegex(text, rf"(?<![\d,.]){re.escape(people)}(?![\d])", f"people cost {people} missing")

    def test_economics_budget_table_matches_envelope(self) -> None:
        text = read_doc("economics.md")
        section = text.split("## 1. Budget", 1)[1].split("\n## 2.", 1)[0]
        total_rows = [r for r in section.splitlines() if re.match(r"^\|\s*\**\s*Total", r, flags=re.I)]
        self.assertTrue(total_rows, "no Total row in budget table")
        nums = [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*\.?\d*", total_rows[0])]
        for expected, got in zip(BUDGET_TOTAL, nums[:3]):
            self.assertLessEqual(abs(expected - got), 5, f"total {got} vs envelope {expected}")

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

    def test_blueprint_agents_are_zero_in_fy2026(self) -> None:
        text = read_doc("blueprint.md")
        section = text.split("## 4. AI agents", 1)[1].split("\n## 5.", 1)[0]
        sums = [0, 0, 0]
        for row in section.splitlines():
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) >= 7 and all(re.fullmatch(r"\d+", c) for c in cells[-3:]):
                for i in range(3):
                    sums[i] += int(cells[-3 + i])
        self.assertEqual(tuple(sums), (0, 2, 6))  # COMPANY.md §6.1 agents


if __name__ == "__main__":
    unittest.main()
