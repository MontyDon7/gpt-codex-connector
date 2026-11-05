"""Contract and behaviour tests for the executive department (agent, workflows, docs, budget)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from core.events import EventLog
from departments.executive import agent as agent_mod
from departments.executive import workflows
from departments.executive.agent import KPIS, ExecutiveAgent, build_agent

DEPT = "executive"
HERE = os.path.dirname(os.path.abspath(__file__))
DEPT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))

# COMPANY.md section 5.4 executive row (GBP k): people, non-people, total for FY2026..FY2028
BUDGET_PEOPLE = (500, 800, 900)
BUDGET_NON_PEOPLE = (100, 250, 400)
BUDGET_TOTAL = (600, 1050, 1300)
HEADCOUNT = (3, 4, 5)  # COMPANY.md section 6.1 humans, year-end

DOC_HEADINGS = {
    "blueprint.md": [
        "# Executive Department Blueprint", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles",
        "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies",
        "## 8. Sources",
    ],
    "sops.md": ["# Executive Standard Operating Procedures", "## Overview"],
    "kpis.md": [
        "# Executive KPIs", "## 1. KPI summary", "## 2. Definitions and formulas",
        "## 3. Reporting cadence and data sources", "## 4. Links to company targets",
    ],
    "economics.md": [
        "# Executive Economics", "## 1. Budget", "## 2. Headcount cost build-up",
        "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md",
    ],
}


def read_doc(name: str) -> str:
    with open(os.path.join(DEPT_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def make_env():
    """Fresh (company, agent) with only the executive live (other departments are stubs)."""
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
        "proposal_id": "PR-0001", "contract_id": "CT-0001", "engagement_id": "EN-0001",
        "incident_id": "INC-0001", "amount_gbp": 260000, "service_line": "forge", "tier": "forge_build",
        "department": "delivery", "summary": f"test {topic}", "due_day": 30, "discount_pct": 5,
        "fiscal_year": 2026, "severity": "medium", "variance_pct": 5.0, "runway_months": 20.0,
        "month": 3, "ytd_revenue_gbp": 1_500_000,
    }


def external_sender(topic: str) -> str:
    return "external" if topic.startswith("external.") else topic.split(".", 1)[0]


class ContractTests(unittest.TestCase):
    def test_class_name(self) -> None:
        self.assertEqual(class_name_for(DEPT), "ExecutiveAgent")
        self.assertTrue(issubclass(ExecutiveAgent, DepartmentAgent))

    def test_build_agent(self) -> None:
        agent, bus, _, _ = standalone_agent()
        self.assertIsInstance(agent, ExecutiveAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)
        self.assertEqual(bus.agent_names, [], "build_agent must not register with the bus")
        self.assertEqual(len(bus.pending), 0, "build_agent must not publish")

    def test_topic_map(self) -> None:
        self.assertEqual(tuple(ExecutiveAgent.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(ExecutiveAgent.PUBLISHES), publishes_for(DEPT))
        self.assertGreater(len(ExecutiveAgent.SUBSCRIBES), 0)
        self.assertGreater(len(ExecutiveAgent.PUBLISHES), 0)

    def test_every_subscribed_topic_has_a_real_handler(self) -> None:
        agent, _, _, _ = standalone_agent()
        for topic in subscribes_for(DEPT):
            self.assertTrue(hasattr(agent, "_on_" + topic.replace(".", "_")), topic)

    def test_kpis_shape(self) -> None:
        self.assertGreaterEqual(len(KPIS), 8)
        self.assertTrue(all(isinstance(k, Kpi) for k in KPIS))
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))

    def test_kpis_mirror_kpis_md_exactly(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("## 2.", 1)[0]
        rows = [[c.strip() for c in r.strip().strip("|").split("|")]
                for r in section.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)]
        self.assertEqual([r[0] for r in rows], [k.name for k in KPIS])
        by_name = {k.name: k for k in KPIS}
        for cells in rows:
            k = by_name[cells[0]]
            self.assertEqual(cells[2], k.unit, k.name)
            self.assertAlmostEqual(float(cells[3]), float(k.target), places=6, msg=k.name)
            self.assertEqual(cells[6].lower().startswith("higher"), k.higher_is_better, k.name)

    def test_role(self) -> None:
        agent, _, _, _ = standalone_agent()
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(agent.role.title, "Chief Executive Officer")


class ConstantsMatchDocsTests(unittest.TestCase):
    """Thresholds in code must equal the values written in COMPANY.md section 9.3 and sops.md."""

    def test_delegation_thresholds(self) -> None:
        self.assertEqual(agent_mod.DEAL_CEO_THRESHOLD_GBP, 500_000)
        self.assertEqual(agent_mod.DEAL_BOARD_THRESHOLD_GBP, 1_500_000)
        self.assertEqual(agent_mod.DISCOUNT_SALES_HEAD_MAX_PCT, 10.0)
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            company = fh.read()
        self.assertIn("Deal ≥ £500k", company)
        self.assertIn("Deal > £1.5m", company)
        self.assertIn("Discount ≤10%", company)

    def test_sops_state_the_same_numbers(self) -> None:
        sops = read_doc("sops.md")
        for token in ("£500,000", "£1,500,000", "15%", "10%", "35%", "12 months", "6 months", "72 hours"):
            self.assertIn(token, sops + read_doc("kpis.md"), token)
        self.assertEqual(agent_mod.CONCENTRATION_CAP_PCT, 15.0)
        self.assertEqual(agent_mod.CONCENTRATION_WATCH_PCT, 10.0)
        self.assertEqual(agent_mod.MIN_DEAL_GROSS_MARGIN_PCT, 35.0)
        self.assertEqual(agent_mod.RUNWAY_FREEZE_MONTHS, 12.0)
        self.assertEqual(agent_mod.RUNWAY_CRISIS_MONTHS, 6.0)
        self.assertEqual(agent_mod.PRICE_CHANGE_CEILING_PCT, 15.0)

    def test_company_facts_constants(self) -> None:
        self.assertEqual(agent_mod.REVENUE_PLAN_GBP, {2026: 6_000_000, 2027: 19_500_000, 2028: 46_200_000})
        self.assertEqual(agent_mod.ENVELOPE_TOTAL_K, {2026: 7_500, 2027: 17_800, 2028: 39_000})
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            company = fh.read()
        for dept, (a, b, c) in agent_mod.DEPT_ENVELOPE_K.items():
            row = next(r for r in company.splitlines() if r.startswith(f"| {dept} |") and "," in r
                       and len(re.findall(r"[\d,]+", r)) >= 9)
            nums = [int(x.replace(",", "")) for x in re.findall(r"[\d,]+", row)]
            self.assertEqual((a, b, c), tuple(nums[6:9]), dept)
        for key, total in agent_mod.ENVELOPE_TOTAL_K.items():
            self.assertEqual(sum(v[key - 2026] for v in agent_mod.DEPT_ENVELOPE_K.values()), total)

    def test_own_budget_matches_envelope(self) -> None:
        for i, fy in enumerate((2026, 2027, 2028)):
            own = agent_mod.OWN_BUDGET_GBP[fy]
            self.assertLessEqual(abs(own["people_gbp"] - BUDGET_PEOPLE[i] * 1000), 5000)
            self.assertEqual(own["non_people_gbp"], BUDGET_NON_PEOPLE[i] * 1000)
            self.assertLessEqual(abs(own["people_gbp"] + own["non_people_gbp"] - BUDGET_TOTAL[i] * 1000), 5000)
            self.assertEqual(own["headcount"], HEADCOUNT[i])


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
                    self.assertNotIn(".internal.", m.topic)
                    self.assertTrue(m.topic.startswith("executive."))

    def test_handle_tolerates_empty_body(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                msg = bus.make_message(external_sender(topic), DEPT, topic, {}, sim_time=0)
                self.assertIsInstance(agent.handle(msg), list)

    def test_handle_tolerates_odd_types(self) -> None:
        odd = {"amount_gbp": "n/a", "discount_pct": None, "runway_months": "x", "kpis": "bad",
               "agenda": "text", "variance_pct": [], "fiscal_year": "soon", "severity": 7}
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                msg = bus.make_message(external_sender(topic), DEPT, topic, odd, sim_time=0)
                self.assertIsInstance(agent.handle(msg), list)

    def test_unknown_topic_does_not_raise(self) -> None:
        agent, bus, _, _ = standalone_agent()
        msg = bus.make_message("sales", DEPT, "sales.lead_qualified_unknown", {}, sim_time=0)
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

    def test_tick_runs_over_three_years_without_error(self) -> None:
        company, agent = make_env()
        company.run(3 * 365 + 10)
        for m in agent.tick() or []:
            self.assertIn(m.topic, agent.PUBLISHES)
        self.assertGreater(len(company.log.query(department=DEPT)), 0)


class WorkflowTests(unittest.TestCase):
    def test_scenarios_dict(self) -> None:
        self.assertGreaterEqual(len(workflows.SCENARIOS), 3)
        for name, fn in workflows.SCENARIOS.items():
            self.assertTrue(callable(fn))
            self.assertEqual(fn.__name__, f"scenario_{name}")

    def test_every_scenario_function_is_registered(self) -> None:
        defined = {n for n in dir(workflows) if n.startswith("scenario_") and callable(getattr(workflows, n))}
        self.assertEqual(defined, {fn.__name__ for fn in workflows.SCENARIOS.values()})

    def test_scenarios_build_valid_messages(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                clock = SimClock()
                msgs = fn(MessageBus(clock), clock)
                self.assertGreater(len(msgs), 0)
                self.assertEqual(len({m.id for m in msgs}), len(msgs))
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
            self.assertTrue(all(m.topic in subs for m in msgs), name)

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
                company.run(90)
                self.assertGreater(len(company.log.query(department=DEPT)), 0)
                self.assertEqual(company.log.query(topic="system.agent_error"), [])

    def test_every_scenario_runs_with_all_departments_if_present(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company = Company(MockLLM(), factories={DEPT: build_agent}, strict=False)
                company.seed(fn(company.bus, company.clock))
                company.run(60)
                errors = [e for e in company.log.query(topic="system.agent_error") if e.department == DEPT]
                self.assertEqual(errors, [])

    def test_scenarios_are_deterministic(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                dumps = []
                for _ in range(2):
                    company, _ = make_env()
                    company.seed(fn(company.bus, company.clock))
                    company.run(60)
                    dumps.append(company.log.to_jsonl())
                self.assertEqual(dumps[0], dumps[1])

    def test_scenarios_accept_default_args_only(self) -> None:
        for fn in workflows.SCENARIOS.values():
            clock = SimClock()
            fn(MessageBus(clock), clock)


class BehaviourTests(unittest.TestCase):
    """Key lifecycle behaviours: the right executive topics are emitted for the right triggers."""

    def _inject(self, company: Company, topic: str, body: dict, sender: str | None = None) -> None:
        company.inject(topic, body, recipient=DEPT, sender=sender or external_sender(topic))

    def _emits(self, company: Company) -> list:
        return [e for e in company.log.query(department=DEPT) if e.data.get("kind") == "emit"]

    def _bodies(self, company: Company, topic: str) -> list[dict]:
        return [e.data["body"] for e in self._emits(company) if e.topic == topic]

    def _deal(self, **over) -> dict:
        body = {"deal_id": "DL-0100", "client_id": "CL-0100", "client_name": "Northgate Retail Holdings",
                "amount_gbp": 650_000, "duration_months": 12, "discount_pct": 5, "gross_margin_pct": 50}
        body.update(over)
        return body

    def _decide(self, **over) -> dict:
        company, _ = make_env()
        self._inject(company, "sales.deal_approval_requested", self._deal(**over))
        company.run(3)
        decisions = self._bodies(company, "executive.deal_decision_made")
        self.assertTrue(decisions)
        return decisions[0]

    # --- deals (SOP-01)
    def test_deal_below_threshold_not_required(self) -> None:
        self.assertEqual(self._decide(amount_gbp=499_999)["decision"], "not_required")

    def test_deal_at_threshold_approved_and_addressed(self) -> None:
        out = self._decide(amount_gbp=500_000)
        self.assertEqual(out["decision"], "approved")
        self.assertEqual(out["deal_id"], "DL-0100")
        self.assertIn("approver", out)

    def test_deal_discount_over_10_needs_finance_concurrence(self) -> None:
        out = self._decide(discount_pct=12)
        self.assertEqual(out["decision"], "approved_with_conditions")
        self.assertIn("finance_head_concurrence", out["conditions"])

    def test_deal_discount_over_15_declined(self) -> None:
        self.assertEqual(self._decide(discount_pct=16)["decision"], "declined")

    def test_deal_low_margin_declined(self) -> None:
        self.assertEqual(self._decide(gross_margin_pct=30)["decision"], "declined")

    def test_deal_uncapped_liability_needs_general_counsel(self) -> None:
        out = self._decide(uncapped_liability=True)
        self.assertIn("general_counsel_signoff", out["conditions"])

    def test_deal_concentration_cap_blocks(self) -> None:
        out = self._decide(amount_gbp=1_000_000, discount_pct=0)
        self.assertEqual(out["decision"], "declined")
        self.assertIn("client_concentration_above_15pct_cap", out["reasons"])

    def test_deal_above_1_5m_referred_then_ratified_by_board(self) -> None:
        company, _ = make_env()
        self._inject(company, "sales.deal_approval_requested",
                     self._deal(amount_gbp=1_800_000, duration_months=36))
        company.run(14)
        decisions = self._bodies(company, "executive.deal_decision_made")
        self.assertEqual([d["decision"] for d in decisions][0], "referred_to_board")
        self.assertTrue(any(d["board_ratified"] and d["approver"] == "Board of Directors" for d in decisions))
        self.assertTrue(self._bodies(company, "executive.board_meeting_held"))

    def test_deal_request_is_idempotent(self) -> None:
        company, _ = make_env()
        for _ in range(2):
            self._inject(company, "sales.deal_approval_requested", self._deal())
        company.run(3)
        self.assertEqual(len(self._bodies(company, "executive.deal_decision_made")), 1)

    def test_deal_won_updates_client_ledger_and_top_share(self) -> None:
        company, agent = make_env()
        self._inject(company, "sales.deal_won", self._deal(amount_gbp=300_000))
        company.run(2)
        self.assertEqual(agent.state["client_revenue_gbp"]["CL-0100"], 300_000)
        self.assertAlmostEqual(agent.kpi_snapshot()["top_client_share_pct"], 5.0)

    def test_deal_won_without_approval_is_exception(self) -> None:
        company, agent = make_env()
        self._inject(company, "sales.deal_won", self._deal())
        company.run(2)
        self.assertTrue(any("no recorded CEO approval" in t.title for t in agent.tasks.values()))

    def test_contract_exception_high_risk(self) -> None:
        company, _ = make_env()
        self._inject(company, "legal.contract_risk_flagged",
                     {"deal_id": "DL-0100", "risk_level": "high", "mitigation": "cap at 2x fees"})
        company.run(2)
        out = self._bodies(company, "executive.deal_decision_made")
        self.assertEqual(out[0]["decision"], "approved_with_conditions")

    # --- headcount (SOP-03)
    def test_headcount_in_plan_approved(self) -> None:
        company, _ = make_env()
        self._inject(company, "people.requisition_opened",
                     {"requisition_id": "REQ-1", "department": "delivery", "role_title": "Consultant"})
        company.run(2)
        out = self._bodies(company, "executive.headcount_approved")
        self.assertTrue(out and out[0]["approved"] and out[0]["basis"] == "in_plan")

    def test_headcount_out_of_plan_without_case_is_declined_visibly(self) -> None:
        company, _ = make_env()
        self._inject(company, "people.hire_requested",
                     {"requisition_id": "REQ-2", "department": "marketing", "in_budget": False})
        company.run(2)
        out = self._bodies(company, "executive.headcount_approved")
        self.assertTrue(out and out[0]["approved"] is False and out[0]["reason"])

    def test_headcount_out_of_plan_with_case_goes_to_ceo(self) -> None:
        company, _ = make_env()
        self._inject(company, "people.hire_requested",
                     {"requisition_id": "REQ-3", "department": "sales", "in_budget": False,
                      "business_case": "Pipeline coverage"})
        company.run(2)
        out = self._bodies(company, "executive.headcount_approved")
        self.assertEqual(out[0]["basis"], "business_case")
        self.assertEqual(out[0]["approver"], "Chief Executive Officer")

    def test_headcount_hold_and_freeze(self) -> None:
        company, agent = make_env()
        self._inject(company, "finance.budget_variance_flagged", {"department": "delivery", "variance_pct": 20})
        self._inject(company, "people.requisition_opened", {"requisition_id": "REQ-4", "department": "delivery"})
        company.run(2)
        out = self._bodies(company, "executive.headcount_approved")
        self.assertFalse(out[0]["approved"])
        self.assertEqual(out[0]["reason"], "department_hiring_hold_after_variance")
        self.assertIn("delivery", agent.state["hiring_holds"])

    def test_executive_hire_goes_to_board_queue(self) -> None:
        company, _ = make_env()
        self._inject(company, "people.hire_requested",
                     {"requisition_id": "REQ-5", "department": "executive", "in_budget": True})
        company.run(10)
        out = self._bodies(company, "executive.headcount_approved")
        self.assertEqual(out[0]["approver"], "Board of Directors")

    # --- budget and OKRs (SOP-04)
    def test_budget_cycle_submits_own_budget(self) -> None:
        company, _ = make_env()
        self._inject(company, "finance.budget_cycle_opened", {"fiscal_year": 2027})
        company.run(2)
        out = self._bodies(company, "executive.budget_submitted")
        self.assertEqual(out[0]["total_gbp"], 1_046_200)

    def test_consolidated_budget_approved_with_okrs_and_hire(self) -> None:
        company, _ = make_env()
        self._inject(company, "finance.budget_consolidated", {"fiscal_year": 2027, "total_gbp": 17_800_000})
        company.run(2)
        approved = self._bodies(company, "executive.budget_approved")
        self.assertEqual(approved[0]["status"], "approved")
        self.assertEqual(approved[0]["approved_total_gbp"], 17_800_000)
        self.assertTrue(self._bodies(company, "executive.okrs_set"))
        self.assertTrue(self._bodies(company, "executive.hire_requested"))

    def test_consolidated_budget_over_envelope_is_reduced(self) -> None:
        company, _ = make_env()
        self._inject(company, "finance.budget_consolidated", {"fiscal_year": 2027, "total_gbp": 18_400_000})
        company.run(2)
        approved = self._bodies(company, "executive.budget_approved")
        self.assertEqual(approved[0]["status"], "approved_with_reductions")
        self.assertEqual(approved[0]["approved_total_gbp"], 17_800_000)

    # --- performance and crises (SOP-05, SOP-06)
    def test_month_end_updates_kpis(self) -> None:
        company, agent = make_env()
        self._inject(company, "finance.month_end_closed",
                     {"month": 6, "ytd_revenue_gbp": 2_400_000, "gross_margin_pct": 44, "active_clients": 15})
        company.run(2)
        snap = agent.kpi_snapshot()
        self.assertAlmostEqual(snap["revenue_gbp_m"], 2.4)
        self.assertEqual(snap["active_clients"], 15)
        self.assertTrue(any("Re-forecast" in t.title for t in agent.tasks.values()))

    def test_low_runway_declares_liquidity_crisis(self) -> None:
        company, agent = make_env()
        self._inject(company, "finance.cash_forecast_updated", {"runway_months": 5})
        company.run(2)
        crises = self._bodies(company, "executive.crisis_declared")
        self.assertEqual(crises[0]["category"], "liquidity")
        self.assertEqual(agent.kpi_snapshot()["cash_runway_months"], 5.0)

    def test_critical_incident_declares_crisis_and_resolution_stands_down(self) -> None:
        company, agent = make_env()
        self._inject(company, "it_security.incident_detected", {"incident_id": "INC-9", "severity": "critical"})
        company.run(2)
        crises = self._bodies(company, "executive.crisis_declared")
        self.assertEqual(len(crises), 1)
        self.assertEqual(crises[0]["commander"], "Chief Executive Officer")
        self.assertTrue(agent.state["crisis_active"])
        self.assertTrue(self._bodies(company, "executive.board_meeting_held"))
        self._inject(company, "it_security.incident_resolved", {"incident_id": "INC-9"})
        company.run(2)
        self.assertFalse(agent.state["crisis_active"])
        self.assertTrue(any("Post-incident review" in t.title for t in agent.tasks.values()))

    def test_breach_confirmed_adds_ico_action_and_is_not_duplicated(self) -> None:
        company, _ = make_env()
        self._inject(company, "it_security.data_breach_confirmed", {"incident_id": "INC-8"})
        self._inject(company, "it_security.data_breach_confirmed", {"incident_id": "INC-8"})
        company.run(2)
        crises = self._bodies(company, "executive.crisis_declared")
        self.assertEqual(len(crises), 1)
        self.assertTrue(any("ICO" in a for a in crises[0]["actions"]))

    def test_non_critical_incident_does_not_declare_crisis(self) -> None:
        company, _ = make_env()
        self._inject(company, "it_security.incident_detected", {"incident_id": "INC-7", "severity": "medium"})
        company.run(2)
        self.assertEqual(self._bodies(company, "executive.crisis_declared"), [])

    def test_crisis_freezes_non_critical_hiring(self) -> None:
        company, _ = make_env()
        self._inject(company, "it_security.incident_detected", {"incident_id": "INC-6", "severity": "critical"})
        self._inject(company, "people.requisition_opened", {"requisition_id": "REQ-9", "department": "delivery"})
        company.run(2)
        out = self._bodies(company, "executive.headcount_approved")
        self.assertEqual(out[0]["reason"], "crisis_hiring_freeze")

    def test_key_client_churn_declares_crisis(self) -> None:
        company, _ = make_env()
        self._inject(company, "customer_success.client_churned",
                     {"client_id": "CL-9", "client_name": "Pennine Mutual Assurance", "annual_value_gbp": 650_000})
        company.run(2)
        self.assertEqual(self._bodies(company, "executive.crisis_declared")[0]["category"], "key_client_loss")

    # --- board and strategy (SOP-02), pricing (SOP-07)
    def test_board_request_with_strategy_change(self) -> None:
        company, _ = make_env()
        self._inject(company, "external.board_request",
                     {"kind": "ad_hoc_meeting", "strategy_change": "Defer New York office to Q3"})
        company.run(10)
        self.assertTrue(self._bodies(company, "executive.board_meeting_held"))
        self.assertTrue(self._bodies(company, "executive.strategy_updated"))

    def test_quarterly_board_is_held(self) -> None:
        company, _ = make_env()
        company.run(120)
        types = {b["meeting_type"] for b in self._bodies(company, "executive.board_meeting_held")}
        self.assertIn("quarterly", types)

    def test_okrs_published_for_the_year(self) -> None:
        company, _ = make_env()
        company.run(3)
        self.assertTrue(self._bodies(company, "executive.okrs_set"))

    def test_pricing_within_ceiling_approved(self) -> None:
        company, _ = make_env()
        self._inject(company, "product.pricing_change_proposed",
                     {"change_id": "PRC-1", "tier": "keep_plus", "new_price_gbp": 237_600,
                      "margin_impact_pct": 3})
        company.run(2)
        out = self._bodies(company, "executive.pricing_change_approved")
        self.assertEqual(out[0]["change_pct"], 10.0)

    def test_pricing_over_ceiling_returned_by_task(self) -> None:
        company, agent = make_env()
        self._inject(company, "product.pricing_change_proposed",
                     {"change_id": "PRC-2", "tier": "keep_plus", "new_price_gbp": 280_000,
                      "margin_impact_pct": 3})
        company.run(2)
        self.assertEqual(self._bodies(company, "executive.pricing_change_approved"), [])
        self.assertTrue(any("PRC-2" in t.title for t in agent.tasks.values()))

    # --- KPI feed
    def test_kpi_report_updates_known_kpis_only(self) -> None:
        company, agent = make_env()
        self._inject(company, "data.kpi_report_published",
                     {"kpis": {"okr_attainment_pct": 70, "unknown_kpi": 1}})
        company.run(2)
        self.assertEqual(agent.kpi_snapshot()["okr_attainment_pct"], 70.0)
        self.assertNotIn("unknown_kpi", agent.kpi_snapshot())

    # --- global invariants
    def test_all_emitted_topics_are_published_topics(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company, _ = make_env()
                company.seed(fn(company.bus, company.clock))
                company.run(90)
                for e in self._emits(company):
                    self.assertIn(e.topic, publishes_for(DEPT))
                    self.assertNotIn(".internal.", e.topic)

    def test_scenarios_cover_core_lifecycle_topics(self) -> None:
        seen: set[str] = set()
        for fn in workflows.SCENARIOS.values():
            company, _ = make_env()
            company.seed(fn(company.bus, company.clock))
            company.run(90)
            seen |= {e.topic for e in self._emits(company)}
        for topic in ("executive.deal_decision_made", "executive.headcount_approved",
                      "executive.budget_approved", "executive.crisis_declared", "executive.okrs_set",
                      "executive.pricing_change_approved", "executive.board_meeting_held"):
            self.assertIn(topic, seen)

    def test_no_wall_clock_or_uuid_in_sources(self) -> None:
        for fname in ("agent.py", "workflows.py"):
            with open(os.path.join(DEPT_DIR, fname), encoding="utf-8") as fh:
                src = fh.read()
            for banned in ("uuid4", "datetime.now", "date.today", "time.time(", "import requests",
                           "urllib.request"):
                self.assertNotIn(banned, src, f"{fname} contains {banned}")

    def test_log_event_never_receives_topic_in_data(self) -> None:
        with open(os.path.join(DEPT_DIR, "agent.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIsNone(re.search(r"log_event\([^)]*\btopic=", src))
        self.assertNotIn("executive.internal.", src)


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
                    idx = 0 if text.startswith(h) else text.find("\n" + h)
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
        ids = re.findall(r"^## (SOP-EXECUTIVE-\d{2}): ", text, flags=re.M)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for sub in ("### Steps", "### Outputs and messages", "### SLA and controls",
                    "### Exceptions and escalation"):
            self.assertGreaterEqual(text.count(sub), len(ids), sub)
        for field in ("**Owner**:", "**Trigger**:", "**Inputs**:"):
            self.assertGreaterEqual(text.count(field), len(ids), field)

    def test_sops_cover_subscribed_and_published_topics(self) -> None:
        text = read_doc("sops.md")
        triggers = "\n".join(re.findall(r"^\*\*Trigger\*\*:.*$", text, flags=re.M))
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, triggers, f"subscribed topic {topic} is not a SOP trigger")
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic {topic} not in sops.md")

    def test_sops_mark_steps_human_or_agent(self) -> None:
        text = read_doc("sops.md")
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)

    def test_blueprint_roles_use_blueprint_titles(self) -> None:
        text = read_doc("blueprint.md")
        for title in ("Chief Executive Officer", "Chief of Staff", "Strategy and Transformation Lead",
                      "Board and Investor Relations Manager", "Senior Strategy Consultant"):
            self.assertIn(title, text)
        kpis = read_doc("kpis.md")
        for title in ("Chief Executive Officer", "Chief of Staff", "Strategy and Transformation Lead"):
            self.assertIn(title, kpis)

    def test_kpi_doc_company_targets_consistent(self) -> None:
        text = read_doc("kpis.md")
        for kpi, expected in (("gross_margin_pct", ["48", "58", "64"]),
                              ("ebitda_margin_pct", ["-25", "9", "16"]),
                              ("revenue_gbp_m", ["6.0", "19.5", "46.2"]),
                              ("active_clients", ["24", "65", "140"])):
            row = next(r for r in text.splitlines() if r.startswith(f"| {kpi} |"))
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertEqual(cells[3:6], expected, kpi)  # COMPANY.md section 5.1


class BudgetTests(unittest.TestCase):
    def test_company_md_row_is_what_we_expect(self) -> None:
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            row = next(r for r in fh.read().splitlines() if r.startswith("| executive |") and "600" in r)
        nums = [int(c.replace(",", "")) for c in re.findall(r"[\d,]+", row)]
        self.assertEqual(tuple(nums[:3]), BUDGET_PEOPLE)
        self.assertEqual(tuple(nums[3:6]), BUDGET_NON_PEOPLE)
        self.assertEqual(tuple(nums[6:9]), BUDGET_TOTAL)

    def test_totals_are_internally_consistent(self) -> None:
        for p, n, t in zip(BUDGET_PEOPLE, BUDGET_NON_PEOPLE, BUDGET_TOTAL):
            self.assertEqual(p + n, t)

    def test_economics_budget_table_matches_envelope(self) -> None:
        text = read_doc("economics.md")
        section = text.split("## 1. Budget", 1)[1].split("\n## 2.", 1)[0]
        total_rows = [r for r in section.splitlines() if re.match(r"^\|\s*\**\s*Total", r, flags=re.I)]
        self.assertTrue(total_rows, "no Total row in budget table")
        nums = [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*\.?\d*", total_rows[0])]
        for expected, got in zip(BUDGET_TOTAL, nums[:3]):
            self.assertLessEqual(abs(expected - got), 5, f"total {got} vs envelope {expected}")
        people = next(r for r in section.splitlines() if "People" in r and r.startswith("|"))
        people = re.sub(r"\([^)]*\)", "", people)
        pnums = [float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*\.?\d*", people)]
        for expected, got in zip(BUDGET_PEOPLE, pnums[:3]):
            self.assertLessEqual(abs(expected - got), 5, f"people {got} vs envelope {expected}")

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


if __name__ == "__main__":
    unittest.main()
