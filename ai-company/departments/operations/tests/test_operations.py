"""Contract and behaviour tests for the operations department (agent, workflows, docs, budget, thresholds)."""

from __future__ import annotations

import ast
import os
import re
import unittest
from datetime import date

from core import (Company, DepartmentAgent, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from core.events import EventLog
from departments.operations import agent as ops_agent
from departments.operations import workflows
from departments.operations.agent import KPIS, OperationsAgent, build_agent

DEPT = "operations"
HERE = os.path.dirname(os.path.abspath(__file__))
DEPT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))

# COMPANY.md 5.4 operations row (GBP k): people, non-people, total for FY2026..FY2028; 6.1 humans and agents
BUDGET_PEOPLE = (200, 400, 750)
BUDGET_NON_PEOPLE = (100, 300, 900)
BUDGET_TOTAL = (300, 700, 1650)
HUMANS = (2, 6, 12)
AGENTS = (1, 4, 8)
LOWER_IS_BETTER = {"vendor_review_cycle_days", "procurement_cycle_days", "overdue_compliance_actions",
                   "budget_variance_pct"}

DOC_HEADINGS = {
    "blueprint.md": ["# Operations Department Blueprint", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles",
                     "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies",
                     "## 8. Sources"],
    "sops.md": ["# Operations Standard Operating Procedures", "## Overview"],
    "kpis.md": ["# Operations KPIs", "## 1. KPI summary", "## 2. Definitions and formulas",
                "## 3. Reporting cadence and data sources", "## 4. Links to company targets"],
    "economics.md": ["# Operations Economics", "## 1. Budget", "## 2. Headcount cost build-up",
                     "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md"],
}


def read_doc(name: str) -> str:
    with open(os.path.join(DEPT_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def read_source(name: str) -> str:
    with open(os.path.join(DEPT_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def make_env():
    """Fresh (company, agent) with only operations live (other departments are stubs)."""
    company = Company(MockLLM(), factories={DEPT: build_agent}, use_departments=False, strict=True)
    return company, company.agents[DEPT]


def standalone_agent():
    clock = SimClock()
    bus = MessageBus(clock)
    log = EventLog(clock.date)
    return build_agent(MockLLM(), bus, clock, log), bus, clock, log


def sample_body(topic: str) -> dict:
    """A rich body usable for any subscribed topic."""
    return {
        "department": "delivery", "employee_id": "EMP-0001", "employee_name": "Priya Nair", "engagement_id": "EN-0001",
        "client_id": "CL-0001", "summary": f"sample for {topic}", "severity": "high", "amount_gbp": 60000,
        "due_day": 30, "start_day": 40, "last_day": 20, "finding_id": "CF-0001", "vendor_id": "VN-0301",
        "vendor_name": "Sample Supplier", "incident_id": "INC-0001", "vulnerability_id": "VULN-0001",
        "policy_id": "POL-001", "issue_id": "DQ-0001", "check": "schema", "source_department": "finance",
        "budget_cycle_id": "BUD-2027", "fiscal_year": 2027, "event_id": "EVT-0001", "estimated_cost_gbp": 3000,
        "team_fte": {"consultant": 3}, "shortfall_fte": {"consultant": 2}, "needed_by_day": 12, "okrs": ["a", "b"],
        "owners": ["operations"], "impact_areas": ["data_protection"], "effective_in_days": 60,
        "time_to_resolve_hours": 3, "decision": "approve", "risk_rating": "low", "tier": 1, "quote_id": "Q-1",
        "term_months": 12, "component": "printer firmware", "crisis_id": "CRS-0001",
    }


def sender_of(topic: str) -> str:
    return topic.split(".", 1)[0]


def msg_for(bus: MessageBus, clock: SimClock, topic: str, body: dict, day=None) -> Message:
    return bus.make_message(sender_of(topic), DEPT, topic, body, sim_time=clock.day if day is None else day)


def emitted(bus: MessageBus, topic: str) -> list[Message]:
    return [m for m in bus.pending if m.topic == topic]


def quote(qid: str, vid: str, name: str, amount: float, rfq: str = "", **extra) -> dict:
    body = {"quote_id": qid, "vendor_id": vid, "vendor_name": name, "amount_gbp": amount, "term_months": 12,
            "valid_until_day": 90, "category": "software", "department": "delivery", "budgeted": True}
    if rfq:
        body["rfq_id"] = rfq
    body.update(extra)
    return body


def approve_vendors(agent: OperationsAgent, *ids: str) -> None:
    """Pre-approve vendors so ladder tests are not affected by the vendor review hold."""
    for vid in ids:
        agent._vendor_for({"vendor_id": vid, "vendor_name": f"Supplier {vid}"})
        agent.state["vendors"][vid].update({"status": "approved", "announced": True})


def three_quotes(agent, bus, clock, amount: float, rfq: str = "RFQ-T-1", **extra) -> None:
    approve_vendors(agent, "VN-0401", "VN-0402", "VN-0403")
    for i, vid in enumerate(("VN-0401", "VN-0402", "VN-0403")):
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                             quote(f"{rfq}-Q{i}", vid, f"Supplier {vid}", amount + 100 * i, rfq, **extra)))


class ContractTests(unittest.TestCase):
    def test_class_name(self) -> None:
        self.assertEqual(class_name_for(DEPT), "OperationsAgent")
        self.assertTrue(issubclass(OperationsAgent, DepartmentAgent))

    def test_build_agent(self) -> None:
        agent, bus, _, _ = standalone_agent()
        self.assertIsInstance(agent, OperationsAgent)
        self.assertEqual((agent.name, agent.department), (DEPT, DEPT))
        self.assertEqual(bus.agent_names, [])
        self.assertEqual(len(bus.pending), 0)

    def test_topic_map(self) -> None:
        self.assertEqual(tuple(OperationsAgent.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(OperationsAgent.PUBLISHES), publishes_for(DEPT))
        self.assertGreater(len(OperationsAgent.SUBSCRIBES), 0)
        self.assertGreater(len(OperationsAgent.PUBLISHES), 0)

    def test_head_role_matches_blueprint_and_company(self) -> None:
        agent = standalone_agent()[0]
        self.assertEqual(agent.role.title, "Chief Operating Officer")
        self.assertEqual(agent.role.level, "head")
        self.assertEqual(agent.role.reports_to, "Chief Executive Officer")
        self.assertEqual(agent.role.headcount_plan, (1, 1, 1))
        self.assertEqual(agent.role.salary_band_gbp, (140000, 200000))

    def test_kpis_match_doc(self) -> None:
        self.assertEqual(len(KPIS), 16)
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("## 2.", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)]
        self.assertEqual(len(rows), len(KPIS))
        for k in KPIS:
            self.assertIsInstance(k, Kpi)
            row = next(r for r in rows if r.startswith(f"| {k.name} |"))
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertEqual(cells[2], k.unit, k.name)
            self.assertEqual(float(cells[3]), k.target, k.name)
            self.assertEqual(cells[6] == "higher is better", k.higher_is_better, k.name)
            self.assertEqual(k.higher_is_better, k.name not in LOWER_IS_BETTER, k.name)
        self.assertEqual(next(k for k in KPIS if k.name == "process_savings_gbp").target, 60000)

    def test_constants_match_sops_md(self) -> None:
        text = read_doc("sops.md").split("## Overview", 1)[0]
        seen = 0
        for line in text.splitlines():
            m = re.match(r"^\| ([A-Z][A-Z0-9_]+) \| ([^|]+) \|", line)
            if not m or m.group(1) == "Constant":
                continue
            name, raw = m.group(1), m.group(2).strip()
            self.assertTrue(hasattr(ops_agent, name), f"agent.py lacks constant {name}")
            sim = re.search(r"\((\d+) sim days\)", raw)
            value = int(sim.group(1)) if sim else (int(raw.replace(",", "")) if re.fullmatch(r"[\d,]+", raw) else None)
            if value is not None:
                self.assertEqual(getattr(ops_agent, name), value, name)
            seen += 1
        self.assertGreaterEqual(seen, 35)

    def test_ladder_matches_sops_md(self) -> None:
        text = read_doc("sops.md").split("## Overview", 1)[0]
        rows = [r for r in text.splitlines() if re.match(r"^\| [1-5] \|", r)]
        self.assertEqual(len(rows), 5)
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            self.assertEqual(ops_agent.APPROVAL_SLA_DAYS[int(cells[0])], int(cells[4]))
        self.assertEqual(ops_agent.APPROVAL_SLA_DAYS, {1: 0, 2: 2, 3: 3, 4: 5, 5: 7})
        self.assertEqual(ops_agent.THREE_QUOTE_THRESHOLD_GBP, 2500)
        self.assertEqual(ops_agent.FORMAL_TENDER_THRESHOLD_GBP, 25000)

    def test_role_titles_are_blueprint_titles(self) -> None:
        roles = read_doc("blueprint.md").split("## 3. Roles", 1)[1].split("## 4.", 1)[0]
        for title in ops_agent.ROLE_TITLES:
            self.assertIn(f"| {title} |", roles, title)
        for title, start in ops_agent.ROLE_START.items():
            self.assertIn(title, ops_agent.ROLE_TITLES)
            self.assertIsInstance(start, date)


class HandleTests(unittest.TestCase):
    def test_handle_every_subscribed_topic(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, clock, _ = standalone_agent()
                out = agent.handle(msg_for(bus, clock, topic, sample_body(topic)))
                self.assertIsInstance(out, list)
                for m in out:
                    self.assertIsInstance(m, Message)
                    self.assertIn(m.topic, publishes_for(DEPT))
                    self.assertEqual(m.sender, DEPT)

    def test_handle_tolerates_empty_and_odd_bodies(self) -> None:
        odd = {"amount_gbp": "n/a", "team_fte": "x", "okrs": "one", "owners": None, "start_day": "soon",
               "equipment": "laptop", "impact_areas": "all", "severity": 7}
        for topic in subscribes_for(DEPT):
            for body in ({}, odd):
                with self.subTest(topic=topic, body=bool(body)):
                    agent, bus, clock, _ = standalone_agent()
                    self.assertIsInstance(agent.handle(msg_for(bus, clock, topic, dict(body))), list)

    def test_unknown_topic_returns_empty_list(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        self.assertEqual(agent.handle(bus.make_message("finance", DEPT, "finance.month_end_closed", {}, sim_time=0)), [])

    def test_no_internal_topics_and_only_published_topics(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        for topic in subscribes_for(DEPT):
            agent.handle(msg_for(bus, clock, topic, sample_body(topic)))
        for _ in range(400):
            agent.tick()
            clock.advance(1)
        self.assertTrue(bus.pending)
        for m in bus.pending:
            self.assertIn(m.topic, publishes_for(DEPT))
            self.assertNotIn(".internal.", m.topic)

    def test_log_event_never_passes_topic_keyword(self) -> None:
        for name in ("agent.py", "workflows.py"):
            tree = ast.parse(read_source(name))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "log_event":
                    self.assertNotIn("topic", [kw.arg for kw in node.keywords], f"{name}:{node.lineno}")
        self.assertNotIn("operations.internal", read_source("agent.py"))

    def test_tick_returns_messages_of_published_topics(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        for _ in range(500):
            out = agent.tick()
            self.assertIsInstance(out, list)
            for m in out:
                self.assertIn(m.topic, publishes_for(DEPT))
            clock.advance(1)


class ProcurementTests(unittest.TestCase):
    def test_below_threshold_po_placed_immediately_at_level_1(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        approve_vendors(agent, "VN-0501")
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received", quote("Q1", "VN-0501", "S", 2499)))
        pos = emitted(bus, "operations.procurement_order_placed")
        self.assertEqual(len(pos), 1)
        self.assertEqual(pos[0].sim_time, clock.day)
        b = pos[0].body
        self.assertEqual((b["approval_level"], b["released_by"], b["exception"]), (1, "agent", "none"))
        self.assertEqual(pos[0].recipient, "finance")
        self.assertEqual(b["vendor_id"], "VN-0501")
        for key in ("po_id", "rfq_id", "vendor", "department", "amount_gbp", "annual_cost_gbp", "term_months",
                    "budgeted", "quotes_received", "approval_level", "approver_title", "split_flag", "severity",
                    "due_day", "summary"):
            self.assertIn(key, b)

    def test_at_threshold_waits_for_three_quotes_then_delays_by_approval_sla(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        approve_vendors(agent, "VN-0401", "VN-0402", "VN-0403")
        for i, vid in enumerate(("VN-0401", "VN-0402")):
            agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                                 quote(f"Q{i}", vid, vid, 2500 + 50 * i, "RFQ-A")))
        self.assertEqual(emitted(bus, "operations.procurement_order_placed"), [])
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received", quote("Q3", "VN-0403", "x", 2700, "RFQ-A")))
        pos = emitted(bus, "operations.procurement_order_placed")
        self.assertEqual(len(pos), 1)
        self.assertEqual(pos[0].sim_time, clock.day + 2)
        self.assertEqual((pos[0].body["approval_level"], pos[0].body["quotes_received"]), (2, 3))
        self.assertEqual(pos[0].body["amount_gbp"], 2500)          # the cheapest compliant quote wins on price

    def test_ladder_levels_approvers_and_delays(self) -> None:
        cases = ((2500, 2, 2, "Chief Operating Officer"), (10000, 2, 2, "Chief Operating Officer"),
                 (10001, 3, 3, "Chief Operating Officer"), (50000, 3, 3, "Chief Operating Officer"),
                 (50001, 4, 5, "Chief Financial Officer"), (250000, 4, 5, "Chief Financial Officer"),
                 (250001, 5, 7, "Chief Executive Officer"))
        for amount, level, delay, approver in cases:
            with self.subTest(amount=amount):
                agent, bus, clock, _ = standalone_agent()
                three_quotes(agent, bus, clock, amount)             # the cheapest of the three equals the amount
                pos = emitted(bus, "operations.procurement_order_placed")
                self.assertEqual(len(pos), 1)
                b = pos[0].body
                self.assertEqual(b["amount_gbp"], amount)
                self.assertEqual(b["approval_level"], level)
                self.assertEqual(pos[0].sim_time, clock.day + delay)
                self.assertEqual(b["approver_title"], approver)

    def test_non_budgeted_spend_raises_the_approval_level(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        three_quotes(agent, bus, clock, 30000, budgeted=False)
        b = emitted(bus, "operations.procurement_order_placed")[0].body
        self.assertEqual(b["approval_level"], 3)                   # up to 50,000 follows the ladder
        agent, bus, clock, _ = standalone_agent()
        three_quotes(agent, bus, clock, 60000, "RFQ-T-2", budgeted=False)
        self.assertEqual(emitted(bus, "operations.procurement_order_placed")[0].body["approver_title"],
                         "Chief Financial Officer")

    def test_vendor_needing_review_holds_order_until_vendor_approved(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        for i, vid in enumerate(("VN-0601", "VN-0602", "VN-0603")):
            agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                                 quote(f"Q{i}", vid, f"Vendor {i}", 18000 + 500 * i, "RFQ-B", ai_platform=True)))
        reviews = emitted(bus, "operations.vendor_review_requested")
        self.assertEqual(len(reviews), 1)
        rb = reviews[0].body
        self.assertEqual(rb["vendor_id"], "VN-0601")
        for key in ("vendor_name", "processes_personal_data", "has_dpa", "data_outside_uk_eea", "annual_cost_gbp",
                    "tier_hint", "rfq_id", "review_reason", "data_classes", "due_day", "ai_platform"):
            self.assertIn(key, rb)
        self.assertEqual((rb["tier_hint"], rb["review_reason"]), (1, "new_vendor"))
        self.assertEqual(emitted(bus, "operations.procurement_order_placed"), [])
        out = agent.handle(msg_for(bus, clock, "it_security.vendor_risk_assessed", {
            "vendor_id": "VN-0601", "vendor_name": "Vendor 0", "tier": 1, "risk_rating": "medium",
            "decision": "approve_with_conditions", "conditions": ["SSO and SCIM"], "reassess_day": 400}))
        approved = [m for m in out if m.topic == "operations.vendor_approved"]
        orders = [m for m in out if m.topic == "operations.procurement_order_placed"]
        self.assertEqual(len(approved), 1)
        self.assertEqual(len(orders), 1)
        self.assertGreaterEqual(orders[0].sim_time, approved[0].sim_time)
        for key in ("vendor_id", "vendor_name", "tier", "risk_rating", "decision", "conditions", "approved_by",
                    "payment_terms_days", "annual_cost_gbp", "reassess_day"):
            self.assertIn(key, approved[0].body)
        self.assertEqual(approved[0].body["conditions"], ["SSO and SCIM"])
        self.assertEqual(orders[0].body["vendor_id"], "VN-0601")

    def test_personal_data_vendor_below_value_threshold_still_needs_review(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                             quote("Q1", "VN-0701", "Survey Co", 900, processes_personal_data=True)))
        self.assertEqual(len(emitted(bus, "operations.vendor_review_requested")), 1)
        self.assertEqual(emitted(bus, "operations.procurement_order_placed"), [])

    def test_rejected_vendor_falls_to_next_ranked_quote_once(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        for i, vid in enumerate(("VN-0801", "VN-0802", "VN-0803")):
            agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                                 quote(f"Q{i}", vid, f"V{i}", 20000 + 1000 * i, "RFQ-R", ai_platform=True)))
        out = agent.handle(msg_for(bus, clock, "it_security.vendor_risk_assessed",
                                   {"vendor_id": "VN-0801", "decision": "reject", "risk_rating": "high", "tier": 1}))
        self.assertEqual([m for m in out if m.topic == "operations.procurement_order_placed"], [])
        self.assertEqual([m.body["vendor_id"] for m in out if m.topic == "operations.vendor_review_requested"],
                         ["VN-0802"])

    def test_laptops_are_bought_by_operations_and_charged_to_it_security(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        agent.state["stock"]["laptop"] = 0
        agent.handle(msg_for(bus, clock, "people.new_hire_started", {"employee_id": "EMP-0900", "start_day": 5}))
        laptop = [m for m in emitted(bus, "operations.procurement_order_placed") if m.body["department"] == "it_security"]
        self.assertTrue(laptop)
        self.assertEqual(laptop[0].body["category"], "it_hardware")
        self.assertLess(laptop[0].body["amount_gbp"], ops_agent.AGENT_PO_LIMIT_GBP)
        self.assertEqual(laptop[0].sim_time, clock.day)

    def test_emergency_order_up_to_10k_is_cfo_approved_without_three_quotes(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        approve_vendors(agent, "VN-0901")
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                             quote("Q1", "VN-0901", "Rapid Hire Ltd", 8000, emergency=True)))
        pos = emitted(bus, "operations.procurement_order_placed")
        self.assertEqual(len(pos), 1)
        self.assertEqual((pos[0].body["exception"], pos[0].body["approver_title"]), ("emergency", "Chief Financial Officer"))
        self.assertEqual(pos[0].sim_time, clock.day)

    def test_fewer_than_three_quotes_takes_exception_route_after_ten_business_days(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        approve_vendors(agent, "VN-1001", "VN-1002")
        for i, vid in enumerate(("VN-1001", "VN-1002")):
            agent.handle(msg_for(bus, clock, "external.vendor_quote_received", quote(f"Q{i}", vid, vid, 6000 + i, "RFQ-X")))
        for _ in range(8):
            agent.tick()
            clock.advance(1)
        self.assertEqual(emitted(bus, "operations.procurement_order_placed"), [])
        for _ in range(10):
            agent.tick()
            clock.advance(1)
        pos = emitted(bus, "operations.procurement_order_placed")
        self.assertEqual(len(pos), 1)
        self.assertEqual((pos[0].body["exception"], pos[0].body["quotes_received"]), ("fewer_than_three", 2))
        self.assertGreaterEqual(pos[0].body["approval_level"], 3)  # approved one level above the order value

    def test_split_orders_are_aggregated(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        approve_vendors(agent, "VN-1101")
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received", quote("Q1", "VN-1101", "S", 1800, category="c")))
        self.assertEqual(len(emitted(bus, "operations.procurement_order_placed")), 1)
        clock.advance(5)
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received", quote("Q2", "VN-1101", "S", 1800, category="c")))
        self.assertEqual(len(emitted(bus, "operations.procurement_order_placed")), 1, "second order needs three quotes")
        self.assertTrue(any(t.title.startswith("RFQ-") and "split-order" in t.title for t in agent.tasks.values()))

    def test_expired_quote_is_rejected(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        clock.advance(10)
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                             quote("Q1", "VN-1201", "S", 1000, valid_until_day=3)))
        self.assertEqual(bus.pending, [])

    def test_agent_never_approves_above_its_limits(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        three_quotes(agent, bus, clock, 9000)
        for m in emitted(bus, "operations.procurement_order_placed"):
            self.assertNotEqual(m.body["released_by"], "agent")
        self.assertFalse(agent._agent_can_release(ops_agent.AGENT_PO_LIMIT_GBP))
        self.assertTrue(agent._agent_can_release(ops_agent.AGENT_PO_LIMIT_GBP - 1))


class WorkspaceTests(unittest.TestCase):
    def hire(self, agent, bus, clock, eid="EMP-0200", **extra):
        body = {"employee_id": eid, "employee_name": "Tom Albright", "department": "delivery", "role": "Consultant",
                "start_day": clock.day, "needs": ["laptop", "workspace", "access_provisioning", "payroll_setup"]}
        body.update(extra)
        return agent.handle(msg_for(bus, clock, "people.new_hire_started", body))

    def test_workspace_ready_same_day_when_in_stock(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = self.hire(agent, bus, clock)
        ready = [m for m in out if m.topic == "operations.workspace_ready"]
        self.assertEqual(len(ready), 1)
        b = ready[0].body
        self.assertEqual(ready[0].sim_time, clock.day)
        self.assertEqual(ready[0].recipient, "people")
        self.assertTrue(b["on_time"])
        self.assertEqual((b["employee_id"], b["employee_name"], b["name"]), ("EMP-0200", "Tom Albright", "Tom Albright"))
        self.assertIn("London HQ, desk", b["location"])
        for key in ("desk", "equipment", "start_day", "ready_day", "summary"):
            self.assertIn(key, b)

    def test_stock_out_delays_two_days_with_on_time_false(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        agent.state["stock"].update({"laptop": 0, "desk_kit": 0})
        out = self.hire(agent, bus, clock)
        ready = [m for m in out if m.topic == "operations.workspace_ready"][0]
        self.assertEqual(ready.sim_time, clock.day + ops_agent.WORKSPACE_KIT_LEAD_TIME_DAYS)
        self.assertFalse(ready.body["on_time"])
        self.assertEqual(ready.body["ready_day"], clock.day + 2)
        self.assertTrue([m for m in out if m.topic == "operations.procurement_order_placed"])
        self.assertEqual(agent.kpis["workspace_ready_on_time_pct"].actual, 0.0)

    def test_exactly_one_workspace_ready_per_employee(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        self.hire(agent, bus, clock)
        again = self.hire(agent, bus, clock)
        self.assertEqual([m for m in again if m.topic == "operations.workspace_ready"], [])
        self.assertEqual(len(emitted(bus, "operations.workspace_ready")), 1)

    def test_access_provisioned_reserves_kit_and_buffer_triggers_restock(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        for i in range(2):
            agent.handle(msg_for(bus, clock, "it_security.access_provisioned", {"employee_id": f"EMP-03{i}", "device_id": "D"}))
        self.assertEqual(agent.state["stock"]["laptop"], 4)
        restock = [m for m in emitted(bus, "operations.procurement_order_placed") if m.body["department"] == "it_security"]
        self.assertEqual(len(restock), 1)
        self.assertEqual(restock[0].body["approval_level"], 2)          # 9,900 is above the agent's 2,500
        self.assertEqual(restock[0].sim_time, clock.day + 2)
        self.assertNotEqual(restock[0].body["released_by"], "agent")

    def test_new_york_starter_gets_new_york_desk(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = self.hire(agent, bus, clock, location="New York")
        self.assertIn("New York office, desk NY-", [m for m in out if m.topic == "operations.workspace_ready"][0].body["location"])

    def test_leaver_recovery_deadline_is_seven_sim_days(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        agent.handle(msg_for(bus, clock, "people.employee_left", {"employee_id": "EMP-0040", "last_day": 10, "department": "delivery"}))
        lv = agent.state["leavers"]["EMP-0040"]
        self.assertEqual(lv["deadline"], 10 + ops_agent.ASSET_RECOVERY_DAYS)
        for _ in range(25):
            agent.tick()
            clock.advance(1)
        self.assertEqual(lv["status"], "recovered")
        self.assertEqual(agent.kpis["asset_recovery_pct"].actual, 100.0)
        self.assertEqual(bus.pending, [])

    def test_operations_leaver_triggers_backfill_hire_request(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = agent.handle(msg_for(bus, clock, "people.employee_left", {
            "employee_id": "EMP-0041", "department": "operations", "role": "Operations Analyst", "last_day": 9}))
        hr = [m for m in out if m.topic == "operations.hire_requested"]
        self.assertEqual(len(hr), 1)
        self.assertEqual((hr[0].body["role"], hr[0].body["reason"], hr[0].recipient), ("Operations Analyst", "backfill", "people"))
        self.assertEqual(hr[0].body["level"], "analyst")


class ComplianceTests(unittest.TestCase):
    def finding(self, agent, bus, clock, severity="high", due=None, fid="CF-0100", **extra):
        body = {"finding_id": fid, "severity": severity, "title": "Test finding", "action_owner": "operations"}
        if due is not None:
            body["due_day"] = due
        body.update(extra)
        return agent.handle(msg_for(bus, clock, "legal.compliance_finding_raised", body))

    def test_due_day_follows_severity_sla(self) -> None:
        for sev, days in (("critical", 7), ("high", 14), ("medium", 28), ("low", 56)):
            with self.subTest(severity=sev):
                agent, bus, clock, _ = standalone_agent()
                self.finding(agent, bus, clock, sev)
                self.assertEqual(agent.state["actions"]["CA-0001"]["due_day"], days)

    def test_legal_due_day_wins_when_earlier(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        self.finding(agent, bus, clock, "low", due=10)
        self.assertEqual(agent.state["actions"]["CA-0001"]["due_day"], 10)

    def test_completion_only_after_attestation_in_tick(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        self.assertEqual(self.finding(agent, bus, clock, "high"), [])
        self.assertEqual(emitted(bus, "operations.compliance_action_completed"), [])
        self.assertEqual(len(agent.state["attest_queue"]), 1)
        sent = []
        for _ in range(20):
            sent += [m for m in agent.tick() if m.topic == "operations.compliance_action_completed"]
            clock.advance(1)
        self.assertEqual(len(sent), 1)
        b = sent[0].body
        self.assertEqual(sent[0].recipient, "legal")
        self.assertEqual((b["finding_id"], b["action_id"], b["severity"]), ("CF-0100", "CA-0001", "high"))
        self.assertTrue(b["on_time"])
        self.assertLessEqual(b["closed_day"], b["due_day"])
        self.assertEqual(b["attested_by"], "Chief Operating Officer")       # COO covers the seat until Q2 FY2027
        self.assertEqual(agent.state["attest_queue"], [])

    def test_attested_by_changes_when_specialist_is_in_post(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        clock.advance_days(clock.day_of(date(2027, 5, 3)))
        self.assertEqual(agent._holder(ops_agent.COMPLIANCE_SPECIALIST), "Compliance and Risk Specialist")
        self.assertEqual(agent._holder(ops_agent.OPS_MANAGER), "Chief Operating Officer")
        self.assertEqual(agent._holder(ops_agent.WF_ASSOCIATE), "Procurement and Workspace Specialist")

    def test_every_fifth_action_closes_late(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        for i in range(5):
            self.finding(agent, bus, clock, "medium", fid=f"CF-02{i}")
        sent = []
        for _ in range(60):
            sent += [m for m in agent.tick() if m.topic == "operations.compliance_action_completed"]
            clock.advance(1)
        self.assertEqual(len(sent), 5)
        self.assertEqual(sorted(m.body["on_time"] for m in sent), [False, True, True, True, True])
        self.assertEqual(agent.kpis["compliance_actions_on_time_pct"].actual, 80.0)

    def test_duplicate_finding_does_not_duplicate_action(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        self.finding(agent, bus, clock)
        self.finding(agent, bus, clock)
        self.assertEqual(len(agent.state["actions"]), 1)

    def test_vendor_finding_keeps_vendor_pending_until_attested_closure(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                             quote("Q1", "VN-1301", "Panel Co", 1200, processes_personal_data=True, has_dpa=False)))
        self.finding(agent, bus, clock, "high", fid="CF-0300", vendor_id="VN-1301", action_owner="operations")
        out = agent.handle(msg_for(bus, clock, "it_security.vendor_risk_assessed", {
            "vendor_id": "VN-1301", "decision": "approve", "risk_rating": "low", "tier": 1, "conditions": []}))
        self.assertEqual([m for m in out if m.topic == "operations.vendor_approved"], [])
        self.assertEqual(agent.state["vendors"]["VN-1301"]["status"], "pending")
        later = []
        for _ in range(20):
            later += agent.tick()
            clock.advance(1)
        topics = [m.topic for m in later]
        self.assertIn("operations.compliance_action_completed", topics)
        self.assertIn("operations.vendor_approved", topics)
        self.assertIn("operations.procurement_order_placed", topics)

    def test_regulatory_change_creates_actions_and_policy_update_is_aligned(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        agent.handle(msg_for(bus, clock, "legal.regulatory_change_noted", {
            "title": "New supplier rules", "impact_areas": ["data_protection", "tax"], "owners": ["operations"],
            "effective_in_days": 90, "severity": "high"}))
        self.assertEqual(len(agent.state["actions"]), 2)
        agent.handle(msg_for(bus, clock, "legal.policy_update_published", {"policy_id": "POL-9", "title": "Supplier policy",
                                                                           "effective_day": 30}))
        self.assertEqual(agent.state["policies"]["POL-9"]["due"], ops_agent.POLICY_ALIGNMENT_DAYS)
        for _ in range(20):
            agent.tick()
            clock.advance(1)
        self.assertTrue(agent.state["policies"]["POL-9"]["aligned"])


class ContinuityTests(unittest.TestCase):
    def resolve(self, agent, bus, clock, severity="high", hours=3.0, iid="INC-0200", **extra):
        body = {"incident_id": iid, "severity": severity, "time_to_resolve_hours": hours, "summary": "email outage"}
        body.update(extra)
        return agent.handle(msg_for(bus, clock, "it_security.incident_resolved", body))

    def test_high_incident_resolution_emits_continuity_test(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        agent.handle(msg_for(bus, clock, "it_security.incident_detected", {"incident_id": "INC-0200", "severity": "high",
                                                                           "summary": "email outage"}))
        out = self.resolve(agent, bus, clock, "high", 3.0)
        tests = [m for m in out if m.topic == "operations.continuity_test_completed"]
        self.assertEqual(len(tests), 1)
        b = tests[0].body
        self.assertEqual((b["test_type"], b["incident_id"], b["rto_met"], b["rpo_met"]), ("live_incident", "INC-0200", True, True))
        self.assertRegex(b["test_id"], r"^BCT-\d{4}$")
        self.assertGreater(tests[0].sim_time, clock.day)                    # after the lessons-learned review
        for key in ("scenario", "severity", "rto_hours_actual", "findings", "summary"):
            self.assertIn(key, b)

    def test_low_and_medium_incidents_are_recorded_only(self) -> None:
        for sev in ("low", "medium"):
            with self.subTest(severity=sev):
                agent, bus, clock, _ = standalone_agent()
                agent.handle(msg_for(bus, clock, "it_security.incident_detected", {"incident_id": "INC-1", "severity": sev}))
                self.assertEqual(self.resolve(agent, bus, clock, sev, iid="INC-1"), [])

    def test_rto_boundaries_by_tier(self) -> None:
        for hours, tier_text, met in ((4.0, "email", True), (4.1, "email", False), (24.0, "intranet", True),
                                      (24.5, "intranet", False)):
            with self.subTest(hours=hours, tier=tier_text):
                agent, bus, clock, _ = standalone_agent()
                agent.handle(msg_for(bus, clock, "it_security.incident_detected",
                                     {"incident_id": "INC-2", "severity": "high", "summary": f"{tier_text} outage"}))
                out = self.resolve(agent, bus, clock, "high", hours, iid="INC-2", summary=f"{tier_text} outage")
                self.assertEqual([m.body["rto_met"] for m in out if m.topic == "operations.continuity_test_completed"], [met])

    def test_rpo_miss_is_reported_separately(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = self.resolve(agent, bus, clock, "critical", 2.0, data_loss_hours=3)
        b = [m for m in out if m.topic == "operations.continuity_test_completed"][0].body
        self.assertTrue(b["rto_met"])
        self.assertFalse(b["rpo_met"])
        self.assertTrue(any("RPO" in f for f in b["findings"]))

    def test_crisis_declaration_emits_test_and_waits_for_a_known_open_incident(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = agent.handle(msg_for(bus, clock, "executive.crisis_declared", {"crisis_id": "CRS-1", "category": "supplier"}))
        self.assertEqual(len([m for m in out if m.topic == "operations.continuity_test_completed"]), 1)
        self.assertGreaterEqual([m for m in out][0].sim_time - clock.day, 10 - 4)
        agent, bus, clock, _ = standalone_agent()
        agent.handle(msg_for(bus, clock, "it_security.incident_detected", {"incident_id": "INC-3", "severity": "critical"}))
        out = agent.handle(msg_for(bus, clock, "executive.crisis_declared", {"crisis_id": "CRS-2", "incident_id": "INC-3"}))
        self.assertEqual(out, [])
        out = self.resolve(agent, bus, clock, "critical", 5.0, iid="INC-3")
        tests = [m for m in out if m.topic == "operations.continuity_test_completed"]
        self.assertEqual(len(tests), 1)
        self.assertFalse(tests[0].body["rto_met"])
        self.assertEqual(self.resolve(agent, bus, clock, "critical", 5.0, iid="INC-3"), [])

    def test_scheduled_tests_follow_the_programme(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        for _ in range(365):
            agent.tick()
            clock.advance(1)
        tests = emitted(bus, "operations.continuity_test_completed")
        self.assertEqual([m.body["test_type"] for m in tests], ["tabletop", "tabletop"])     # FY2026: two tabletops
        self.assertEqual(agent.kpis["continuity_tests_completed"].actual, 2)
        self.assertEqual(agent.kpis["continuity_rto_met_pct"].actual, 100.0)

    def test_vulnerability_orders_replacement_for_it_security_and_dedupes(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        body = {"vulnerability_id": "V-1", "severity": "critical", "component": "door access controller", "due_day": 3}
        out = agent.handle(msg_for(bus, clock, "it_security.vulnerability_found", body))
        pos = [m for m in out if m.topic == "operations.procurement_order_placed"]
        self.assertEqual(len(pos), 1)
        self.assertEqual((pos[0].body["department"], pos[0].sim_time), ("it_security", clock.day))
        self.assertEqual(agent.handle(msg_for(bus, clock, "it_security.vulnerability_found", body)), [])
        low = dict(body, vulnerability_id="V-2", severity="low")
        self.assertEqual(agent.handle(msg_for(bus, clock, "it_security.vulnerability_found", low)), [])


class ProcessAndBudgetTests(unittest.TestCase):
    def issue(self, agent, bus, clock, severity, check="schema", n=1):
        out = []
        for i in range(n):
            out += agent.handle(msg_for(bus, clock, "data.data_quality_issue_raised", {
                "issue_id": f"DQ-{i}", "severity": severity, "check": check, "source_department": "finance"}))
            clock.advance(1)
        return out

    def test_critical_issue_publishes_proposal_above_threshold(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = self.issue(agent, bus, clock, "critical")
        props = [m for m in out if m.topic == "operations.process_improvement_proposed"]
        self.assertEqual(len(props), 1)
        b = props[0].body
        self.assertEqual(props[0].recipient, "executive")
        self.assertEqual(b["annualised_saving_gbp"], 1 * 4 * 80 * ops_agent.NOTIONAL_HOURLY_COST_GBP)
        self.assertGreaterEqual(b["annualised_saving_gbp"], ops_agent.PROCESS_PROPOSAL_MIN_SAVING_GBP)
        self.assertLessEqual(b["payback_months"], ops_agent.PROCESS_MAX_PAYBACK_MONTHS)
        self.assertRegex(b["proposal_id"], r"^PI-\d{4}$")
        self.assertEqual(b["trigger_source"], "data_quality")

    def test_below_threshold_is_tracked_but_not_published(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        self.assertEqual(self.issue(agent, bus, clock, "high"), [])          # 4 x 40 x 45 = 7,200
        self.assertEqual(len(agent.state["improvements"]), 1)
        self.assertEqual(self.issue(agent, bus, clock, "low", "format", 1), [])

    def test_recurrence_in_window_qualifies(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = self.issue(agent, bus, clock, "high", n=2)                       # 8 x 40 x 45 = 14,400
        self.assertEqual(len([m for m in out if m.topic == "operations.process_improvement_proposed"]), 1)

    def test_savings_counted_only_after_ninety_day_check(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        self.issue(agent, bus, clock, "critical")
        for _ in range(100):
            agent.tick()
            clock.advance(1)
        self.assertEqual(agent.kpis["process_improvements_adopted"].actual, 1)
        self.assertEqual(agent.kpis["process_savings_gbp"].actual, 0)
        for _ in range(60):
            agent.tick()
            clock.advance(1)
        self.assertEqual(agent.kpis["process_savings_gbp"].actual, 14400)

    def test_budget_submitted_on_day_21_and_matches_company_envelope(self) -> None:
        for fy, idx in ((2026, 0), (2027, 1), (2028, 2)):
            with self.subTest(fy=fy):
                agent, bus, clock, _ = standalone_agent()
                out = agent.handle(msg_for(bus, clock, "finance.budget_cycle_opened", {
                    "budget_cycle_id": f"BUD-{fy}", "fiscal_year": fy, "deadline_day": clock.day + 21}))
                sub = [m for m in out if m.topic == "operations.budget_submitted"]
                self.assertEqual(len(sub), 1)
                self.assertEqual(sub[0].sim_time, clock.day + ops_agent.OPS_BUDGET_SUBMISSION_DAY)
                self.assertEqual(sub[0].recipient, "finance")
                b = sub[0].body
                self.assertAlmostEqual(b["total_gbp"], BUDGET_TOTAL[idx] * 1000, delta=5000)
                self.assertAlmostEqual(b["people_gbp"], BUDGET_PEOPLE[idx] * 1000, delta=5000)
                self.assertAlmostEqual(b["non_people_gbp"], BUDGET_NON_PEOPLE[idx] * 1000, delta=5000)
                self.assertEqual((b["headcount"], b["agents"], b["department"]), (HUMANS[idx], AGENTS[idx], "operations"))
                self.assertEqual(b["total_gbp"], b["people_gbp"] + b["non_people_gbp"])
                self.assertEqual(agent.handle(msg_for(bus, clock, "finance.budget_cycle_opened", {
                    "budget_cycle_id": f"BUD-{fy}", "fiscal_year": fy})), [])

    def test_first_monday_of_quarter_requests_planned_hire(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        target = clock.day_of(date(2026, 7, 6))
        sent = []
        while clock.day <= target:
            sent += [m for m in agent.tick() if m.topic == "operations.hire_requested"]
            clock.advance(1)
        self.assertEqual(len(sent), 1)
        b = sent[0].body
        self.assertEqual((b["role"], b["reason"], b["level"], sent[0].recipient),
                         ("Procurement and Workspace Specialist", "growth", "consultant", "people"))
        self.assertEqual(b["salary_band_gbp"], [55000, 70000])
        self.assertEqual(b["start_quarter"], "Q4 FY2026")

    def test_event_and_kickoff_logistics(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = agent.handle(msg_for(bus, clock, "marketing.event_scheduled", {"event_id": "EVT-9", "estimated_cost_gbp": 9500,
                                                                             "due_day": 40}))
        self.assertEqual(out, [])                                         # RFQ opened, three venue quotes needed
        rfq_id = agent.state["event_rfqs"]["EVT-9"]
        approve_vendors(agent, "VN-1401", "VN-1402", "VN-1403")
        for i, vid in enumerate(("VN-1401", "VN-1402", "VN-1403")):
            agent.handle(msg_for(bus, clock, "external.vendor_quote_received",
                                 quote(f"E{i}", vid, vid, 9000 + 100 * i, event_id="EVT-9")))
        pos = emitted(bus, "operations.procurement_order_placed")
        self.assertEqual(len(pos), 1)
        self.assertEqual((pos[0].body["department"], pos[0].body["rfq_id"]), ("marketing", rfq_id))
        small = agent.handle(msg_for(bus, clock, "delivery.engagement_kickoff", {
            "engagement_id": "EN-7", "start_day": 20, "team_fte": {"consultant": 2, "analyst": 1}}))
        self.assertEqual([m.body["department"] for m in small if m.topic == "operations.procurement_order_placed"], ["delivery"])

    def test_okrs_and_strategy_update_programmes(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        before = len(agent.state["programmes"])
        agent.handle(msg_for(bus, clock, "executive.okrs_set", {"okrs": ["a", {"objective": "b"}]}))
        self.assertEqual(len(agent.state["programmes"]), before + 2)
        agent.handle(msg_for(bus, clock, "executive.strategy_updated", {}))
        self.assertTrue(all(p["rebaselined"] for p in agent.state["programmes"].values()))


class InterfaceTests(unittest.TestCase):
    """Body keys that other departments already read, from their real producers and consumers."""

    def test_vendor_review_requested_keys_read_by_legal_it_security_finance(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        for i in range(3):
            agent.handle(msg_for(bus, clock, "external.vendor_quote_received", quote(
                f"Q{i}", f"VN-150{i}", f"Vendor {i}", 15000 + i, "RFQ-I", processes_personal_data=True, has_dpa=True)))
        b = emitted(bus, "operations.vendor_review_requested")[0].body
        for key in ("vendor_id", "vendor_name", "processes_personal_data", "has_dpa", "data_outside_uk_eea",
                    "data_classes", "service", "tier_hint", "annual_cost_gbp",
                    "amount_gbp", "due_day", "ai_platform", "privileged_access"):
            self.assertIn(key, b)
        self.assertIsInstance(b["data_classes"], list)

    def test_input_keys_of_other_departments_are_understood(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        # people.new_hire_started as produced by departments/people (employee_id, employee_name, role, needs, start_day)
        out = agent.handle(msg_for(bus, clock, "people.new_hire_started", {
            "employee_id": "EMP-0777", "requisition_id": "REQ-1", "employee_name": "Chiamaka Obi", "department": "delivery",
            "role": "Consultant", "level": "consultant", "start_day": 3, "base_salary_gbp": 60000,
            "needs": ["laptop", "workspace", "access_provisioning", "payroll_setup"], "access_profile": "delivery"}))
        ready = [m for m in out if m.topic == "operations.workspace_ready"][0].body
        self.assertEqual(ready["employee_id"], "EMP-0777")
        self.assertEqual(ready["employee_name"], "Chiamaka Obi")
        self.assertNotIn("workspace", ready["equipment"])
        # it_security.vendor_risk_assessed keys: vendor_id, vendor_name, tier, risk_rating, decision, conditions, reassess_day
        agent.handle(msg_for(bus, clock, "external.vendor_quote_received", quote("Q1", "VN-1601", "AI Co", 800, ai_platform=True)))
        out = agent.handle(msg_for(bus, clock, "it_security.vendor_risk_assessed", {
            "vendor_id": "VN-1601", "vendor_name": "AI Co", "tier": 1, "risk_rating": "medium",
            "decision": "approve_with_conditions", "conditions": ["c1"], "reassess_day": 500, "severity": "medium",
            "service": "ai", "due_day": 9}))
        approved = [m for m in out if m.topic == "operations.vendor_approved"][0].body
        self.assertEqual((approved["vendor_id"], approved["tier"], approved["risk_rating"], approved["reassess_day"]),
                         ("VN-1601", 1, "medium", 500))
        # legal.compliance_finding_raised keys: finding_id, severity, areas, action_owner, due_day, vendor_id
        agent.handle(msg_for(bus, clock, "legal.compliance_finding_raised", {
            "finding_id": "CF-0900", "vendor_id": "VN-1601", "severity": "high", "areas": ["data_protection"],
            "issues": ["No DPA"], "action_owner": "operations", "due_day": 5}))
        self.assertEqual(agent.state["actions"]["CA-0001"]["finding_id"], "CF-0900")

    def test_compliance_completed_and_continuity_keys_for_consumers(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        agent.handle(msg_for(bus, clock, "legal.compliance_finding_raised", {"finding_id": "CF-1", "severity": "low"}))
        sent = []
        for _ in range(60):
            sent += [m for m in agent.tick() if m.topic == "operations.compliance_action_completed"]
            clock.advance(1)
        for key in ("finding_id", "action_id", "title", "severity", "due_day", "closed_day", "on_time", "attested_by",
                    "evidence_ref", "policy_update_required", "summary"):
            self.assertIn(key, sent[0].body)
        out = agent.handle(msg_for(bus, clock, "it_security.incident_resolved", {
            "incident_id": "INC-9", "severity": "critical", "time_to_resolve_hours": 2}))
        b = [m for m in out if m.topic == "operations.continuity_test_completed"][0].body
        for key in ("test_id", "rto_met", "rpo_met", "findings", "result"):      # it_security and executive read these
            self.assertIn(key, b)
        self.assertEqual(b["result"], "passed")

    def test_process_proposal_carries_cost_key_read_by_executive(self) -> None:
        agent, bus, clock, _ = standalone_agent()
        out = agent.handle(msg_for(bus, clock, "data.data_quality_issue_raised",
                                   {"issue_id": "DQ-1", "severity": "critical", "check": "schema", "source_department": "sales"}))
        self.assertIn("estimated_cost_gbp", out[0].body)


class ScenarioTests(unittest.TestCase):
    def test_scenarios_dict(self) -> None:
        self.assertGreaterEqual(len(workflows.SCENARIOS), 3)
        for name, fn in workflows.SCENARIOS.items():
            self.assertTrue(callable(fn), name)

    def test_scenarios_build_valid_messages(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                clock = SimClock()
                msgs = fn(MessageBus(clock), clock)
                self.assertTrue(msgs)
                self.assertEqual(len({m.id for m in msgs}), len(msgs))
                for m in msgs:
                    self.assertIsInstance(m, Message)
                    self.assertGreaterEqual(m.sim_time, 0)

    def test_scenarios_start_from_subscribed_topics(self) -> None:
        subs = set(subscribes_for(DEPT))
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                clock = SimClock()
                self.assertTrue(any(m.topic in subs for m in fn(MessageBus(clock), clock)))

    def test_scenarios_run_strict_and_emit_only_published_topics(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company, _ = make_env()
                company.seed(fn(company.bus, company.clock))
                company.run(150)
                self.assertTrue(company.log.query(department=DEPT), name)
                self.assertEqual(company.log.query(topic="system.agent_error"), [])
                for m in company.bus.history:
                    if m.sender == DEPT:
                        self.assertIn(m.topic, publishes_for(DEPT))

    def test_scenarios_cover_the_published_lifecycle_topics(self) -> None:
        seen = set()
        for name, fn in workflows.SCENARIOS.items():
            company, _ = make_env()
            company.seed(fn(company.bus, company.clock))
            company.run(150)
            seen |= {m.topic for m in company.bus.history if m.sender == DEPT}
        self.assertEqual(seen, set(publishes_for(DEPT)))

    def test_stock_out_scenario_marks_late_starters(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_new_starters_and_stock_out(company.bus, company.clock))
        company.run(10)
        ready = [m for m in company.bus.history if m.topic == "operations.workspace_ready"]
        self.assertEqual(len(ready), 8)
        self.assertEqual(len({m.body["employee_id"] for m in ready}), 8)
        self.assertEqual(sorted(m.body["on_time"] for m in ready), [False] * 2 + [True] * 6)

    def test_vendor_review_scenario_orders_after_approval(self) -> None:
        company, _ = make_env()
        company.seed(workflows.scenario_competitive_sourcing_vendor_review(company.bus, company.clock))
        company.run(40)
        topics = [m.topic for m in company.bus.history if m.sender == DEPT]
        self.assertLess(topics.index("operations.vendor_review_requested"), topics.index("operations.vendor_approved"))
        self.assertLess(topics.index("operations.vendor_approved"), topics.index("operations.procurement_order_placed"))

    def test_scenarios_deterministic(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                logs = []
                for _ in range(2):
                    company, _ = make_env()
                    company.seed(fn(company.bus, company.clock))
                    company.run(120)
                    logs.append(company.log.to_jsonl())
                self.assertEqual(logs[0], logs[1])
                self.assertTrue(logs[0])

    def test_all_scenarios_together_deterministic_and_clean(self) -> None:
        logs = []
        for _ in range(2):
            company, _ = make_env()
            for fn in workflows.SCENARIOS.values():
                company.seed(fn(company.bus, company.clock))
            company.run(400)
            self.assertEqual(company.log.query(topic="system.agent_error"), [])
            logs.append(company.log.to_jsonl())
        self.assertEqual(logs[0], logs[1])


class DocsTests(unittest.TestCase):
    def test_docs_exist_with_required_headings_in_order(self) -> None:
        for name, headings in DOC_HEADINGS.items():
            with self.subTest(doc=name):
                text = read_doc(name)
                found = [ln.rstrip() for ln in text.splitlines() if ln.startswith("#")]
                idx = []
                for h in headings:
                    self.assertIn(h, found, f"{name} missing {h!r}")
                    idx.append(found.index(h))
                self.assertEqual(idx, sorted(idx))

    def test_docs_have_no_placeholders(self) -> None:
        for name in DOC_HEADINGS:
            text = read_doc(name)
            self.assertNotRegex(text, r"\bTBD\b|(?i:lorem ipsum)|\bTODO\b|\bXXX\b", name)

    def test_sops_structure_and_topic_coverage(self) -> None:
        text = read_doc("sops.md")
        ids = re.findall(r"^## (SOP-OPERATIONS-\d{2}): ", text, flags=re.M)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for sub in ("### Steps", "### Outputs and messages", "### SLA and controls", "### Exceptions and escalation"):
            self.assertGreaterEqual(text.count(sub), len(ids), sub)
        for field in ("**Owner**:", "**Trigger**:", "**Inputs**:"):
            self.assertGreaterEqual(text.count(field), len(ids), field)
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic {topic} not in sops.md")
        triggers = " ".join(re.findall(r"^\*\*Trigger\*\*:.*$", text, flags=re.M))
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, triggers, f"subscribed topic {topic} is not the Trigger of any SOP")

    def test_blueprint_mentions_head(self) -> None:
        text = read_doc("blueprint.md")
        self.assertIn("Chief Operating Officer", text)
        self.assertIn("COMPANY.md", text)

    def test_blueprint_headcount_totals(self) -> None:
        text = read_doc("blueprint.md")
        roles = text.split("## 3. Roles", 1)[1].split("## 4.", 1)[0]
        sums = [0, 0, 0]
        for r in [ln for ln in roles.splitlines() if ln.startswith("|")][2:]:
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            if len(cells) >= 6 and all(c.isdigit() for c in cells[3:6]):
                for i in range(3):
                    sums[i] += int(cells[3 + i])
        self.assertEqual(tuple(sums), HUMANS)
        agents = text.split("## 4. AI agents", 1)[1].split("## 5.", 1)[0]
        asums = [0, 0, 0]
        for r in [ln for ln in agents.splitlines() if ln.startswith("|")][2:]:
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            if len(cells) >= 7 and all(c.isdigit() for c in cells[-3:]):
                for i in range(3):
                    asums[i] += int(cells[-3 + i])
        self.assertEqual(tuple(asums), AGENTS)

    def test_economics_budget_and_people_cost(self) -> None:
        text = read_doc("economics.md")
        budget = text.split("## 1. Budget", 1)[1].split("## 2.", 1)[0]
        for value in BUDGET_TOTAL + BUDGET_PEOPLE + BUDGET_NON_PEOPLE:
            self.assertIn(f"{value:,}", budget)
        self.assertRegex(budget, r"\*\*Total \(people \+ non-people\)\*\*")
        self.assertIn("5.4", text.split("## 5. Reconciliation to COMPANY.md", 1)[1])
        for idx, people in enumerate(ops_agent.BUDGET_PEOPLE_GBP):
            self.assertAlmostEqual(people, BUDGET_PEOPLE[idx] * 1000, delta=5000)       # within 5k of COMPANY.md 5.4
        for idx, non in enumerate(ops_agent.BUDGET_NON_PEOPLE_GBP):
            self.assertEqual(non, BUDGET_NON_PEOPLE[idx] * 1000)

    def test_company_md_row_is_what_we_test_against(self) -> None:
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            text = fh.read()
        cells = None
        for ln in text.splitlines():
            if ln.startswith("| operations |"):
                c = [x.strip().replace(",", "") for x in ln.strip("|").split("|")]
                if len(c) == 10:
                    cells = c
                    break
        self.assertIsNotNone(cells)
        nums = tuple(int(x) for x in cells[1:])
        self.assertEqual(nums[0:3], BUDGET_PEOPLE)
        self.assertEqual(nums[3:6], BUDGET_NON_PEOPLE)
        self.assertEqual(nums[6:9], BUDGET_TOTAL)


class DeterminismTests(unittest.TestCase):
    def test_identical_runs_identical_logs(self) -> None:
        logs = []
        for _ in range(2):
            company, _ = make_env()
            company.inject("external.vendor_quote_received", quote("Q1", "VN-1701", "S", 1500), sender="external")
            company.inject("people.new_hire_started", sample_body("x"), sender="people", delay_days=3)
            company.inject("legal.compliance_finding_raised", sample_body("x"), sender="legal", delay_days=2)
            company.run(200)
            logs.append(company.log.to_jsonl())
        self.assertEqual(logs[0], logs[1])
        self.assertTrue(logs[0])


if __name__ == "__main__":
    unittest.main()
