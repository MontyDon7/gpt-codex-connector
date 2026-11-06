"""Contract and behaviour tests for the sales department (agent, workflows, docs, budget)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from core.events import EventLog
from departments.sales import agent as sales_agent
from departments.sales import workflows
from departments.sales.agent import KPIS, SalesAgent, build_agent

DEPT = "sales"
HERE = os.path.dirname(os.path.abspath(__file__))
DEPT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))

# COMPANY.md §5.4 sales row (GBP k): people, non-people, total for FY2026..FY2028
BUDGET_PEOPLE = (600, 1300, 2300)
BUDGET_NON_PEOPLE = (250, 800, 2300)
BUDGET_TOTAL = (850, 2100, 4600)
HEADCOUNT = (5, 14, 26)  # COMPANY.md §6.1 humans, year-end

DOC_HEADINGS = {
    "blueprint.md": [
        "# Sales Department Blueprint", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles",
        "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies",
        "## 8. Sources",
    ],
    "sops.md": ["# Sales Standard Operating Procedures", "## Overview"],
    "kpis.md": [
        "# Sales KPIs", "## 1. KPI summary", "## 2. Definitions and formulas",
        "## 3. Reporting cadence and data sources", "## 4. Links to company targets",
    ],
    "economics.md": [
        "# Sales Economics", "## 1. Budget", "## 2. Headcount cost build-up",
        "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md",
    ],
}

DECISION_WINDOWS = {
    "compass_spark": 40, "keep_essential": 45, "forge_pilot": 50, "compass_sprint": 60, "keep_plus": 60,
    "forge_build": 80, "compass_programme": 85, "keep_enterprise": 85, "forge_scale": 105,
}


def read_doc(name: str) -> str:
    with open(os.path.join(DEPT_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def make_env():
    """Fresh (company, agent) with only sales live (other departments are stubs)."""
    company = Company(MockLLM(), factories={DEPT: build_agent}, use_departments=False, strict=True)
    return company, company.agents[DEPT]


def standalone_agent():
    clock = SimClock()
    bus = MessageBus(clock)
    log = EventLog(clock.date)
    return build_agent(MockLLM(), bus, clock, log), bus, clock, log


def sample_body(topic: str) -> dict:
    """A rich, well-formed body that uses the shared business-ID keys from CONVENTIONS section 4."""
    return {
        "client_id": "CL-0007", "client_name": "Calder Freight Group", "company": "Calder Freight Group",
        "deal_id": "DL-0001", "lead_id": "LD-00001", "proposal_id": "PR-0001", "contract_id": "CT-0001",
        "engagement_id": "EN-0001", "invoice_id": "INV-2026-0001", "rfp_id": "RFP-0001", "amount_gbp": 60000,
        "estimated_value_gbp": 120000, "service_line": "forge", "tier": "forge_pilot", "department": "sales",
        "summary": f"test {topic}", "due_day": 90, "discount_pct": 5, "milestone": "M1", "year": 2026,
        "period": "2026-10", "budget_cycle_id": "BUD-2026", "employees": 650, "sector": "logistics",
        "contact_role": "Chief Operating Officer", "score": 80, "stage": "mql", "pain": "backlog",
        "score_reasons": ["senior_buyer"], "decision": "approved", "severity": "high", "score_x": 1,
        "days_by_level": {"senior_consultant": 5}, "utilisation_pct": 90, "health_score": 40,
        "annual_value_gbp": 216000, "capability": "x", "certification": "ISO 27001", "status": "achieved",
        "expected_leads": 100, "campaign": "c", "event": "e", "title": "t",
    }


def external_sender(topic: str) -> str:
    return "external" if topic.startswith("external.") else topic.split(".", 1)[0]


def emitted(company: Company) -> list:
    return [e for e in company.log.query(department=DEPT) if e.data.get("kind") == "emit"]


def emitted_topics(company: Company) -> set[str]:
    return {e.topic for e in emitted(company)}


def run_scenario(name: str, days: int = 160):
    company, agent = make_env()
    company.seed(workflows.SCENARIOS[name](company.bus, company.clock))
    company.run(days)
    return company, agent


def mk(bus: MessageBus, topic: str, body: dict, sim_time: int = 0) -> Message:
    return bus.make_message(external_sender(topic), DEPT, topic, body, sim_time=sim_time)


class ContractTests(unittest.TestCase):
    def test_class_name(self) -> None:
        self.assertEqual(class_name_for(DEPT), "SalesAgent")
        self.assertTrue(issubclass(SalesAgent, DepartmentAgent))

    def test_build_agent(self) -> None:
        agent, bus, _, _ = standalone_agent()
        self.assertIsInstance(agent, SalesAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)
        self.assertEqual(bus.agent_names, [], "build_agent must not register with the bus")
        self.assertEqual(len(bus.pending), 0, "build_agent must not publish")

    def test_topic_map(self) -> None:
        self.assertEqual(tuple(SalesAgent.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(SalesAgent.PUBLISHES), publishes_for(DEPT))
        self.assertGreater(len(SalesAgent.SUBSCRIBES), 0)
        self.assertGreater(len(SalesAgent.PUBLISHES), 0)

    def test_every_subscribed_topic_has_a_handler(self) -> None:
        agent, _, _, _ = standalone_agent()
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, agent._handlers, topic)
        self.assertFalse([t for t in agent._handlers if ".internal." in t])

    def test_kpis(self) -> None:
        self.assertEqual(len(KPIS), 15)
        self.assertTrue(all(isinstance(k, Kpi) for k in KPIS))
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))

    def test_kpis_mirror_doc(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("\n## 2.", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)]
        self.assertEqual([r.split("|")[1].strip() for r in rows], [k.name for k in KPIS])
        for k, row in zip(KPIS, rows):
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            self.assertAlmostEqual(float(cells[3].replace(",", "")), float(k.target), places=6, msg=k.name)
            unit = cells[2].split("/")[0].strip().lower()
            self.assertEqual(unit, k.unit, k.name)
            self.assertEqual(cells[6] == "higher is better", k.higher_is_better, k.name)

    def test_role(self) -> None:
        agent, _, _, _ = standalone_agent()
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(agent.role.level, "head")
        self.assertEqual(agent.role.title, "Chief Revenue Officer")


class HandleTests(unittest.TestCase):
    def test_handle_every_subscribed_topic(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                out = agent.handle(mk(bus, topic, sample_body(topic)))
                self.assertIsInstance(out, list)
                for m in out:
                    self.assertIsInstance(m, Message)
                    self.assertIn(m.topic, agent.PUBLISHES)
                    self.assertNotIn(".internal.", m.topic)

    def test_handle_tolerates_empty_body(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                self.assertIsInstance(agent.handle(mk(bus, topic, {})), list)

    def test_handle_tolerates_rich_body_twice(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                body = sample_body(topic)
                agent.handle(mk(bus, topic, body))
                self.assertIsInstance(agent.handle(mk(bus, topic, body)), list)

    def test_unknown_topic_does_not_raise(self) -> None:
        agent, bus, _, log = standalone_agent()
        self.assertEqual(agent.handle(bus.make_message("marketing", DEPT, "marketing.not_a_topic", {},
                                                       sim_time=0)), [])
        self.assertTrue(log.query(topic="sales.activity.unhandled_topic"))

    def test_unmatched_deal_messages_are_logged_not_raised(self) -> None:
        agent, bus, _, log = standalone_agent()
        for topic in ("delivery.scoping_completed", "finance.pricing_check_completed",
                      "legal.contract_signed", "executive.deal_decision_made"):
            self.assertEqual(agent.handle(mk(bus, topic, {"deal_id": "DL-9999"})), [])
        self.assertEqual(len(log.query(topic="sales.activity.unmatched")), 4)

    def test_handle_is_deterministic(self) -> None:
        results = []
        for _ in range(2):
            agent, bus, _, log = standalone_agent()
            for topic in subscribes_for(DEPT):
                agent.handle(mk(bus, topic, sample_body(topic)))
            results.append(log.to_jsonl())
        self.assertEqual(results[0], results[1])

    def test_tick_runs_over_a_year_without_error(self) -> None:
        company, agent = make_env()
        company.run(370)
        for m in agent.tick() or []:
            self.assertIn(m.topic, agent.PUBLISHES)
        self.assertGreater(len(company.log.query(department=DEPT)), 0)
        self.assertTrue(company.log.query(topic="sales.activity.monthly_kpi_snapshot"))
        self.assertTrue(company.log.query(topic="sales.activity.pipeline_review"))


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
                self.assertIsInstance(msgs, list)
                self.assertGreater(len(msgs), 0)
                ids = [m.id for m in msgs]
                self.assertEqual(len(ids), len(set(ids)))
                for m in msgs:
                    self.assertIsInstance(m, Message)
                    self.assertIsInstance(m.body, dict)
                    self.assertIsInstance(m.sim_time, int)
                    self.assertGreaterEqual(m.sim_time, clock.day)

    def test_every_scenario_starts_from_subscribed_topics_only(self) -> None:
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
        for name in workflows.SCENARIOS:
            with self.subTest(scenario=name):
                company, _ = run_scenario(name, 150)
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
        for name in workflows.SCENARIOS:
            with self.subTest(scenario=name):
                dumps = [run_scenario(name, 150)[0].log.to_jsonl() for _ in range(2)]
                self.assertEqual(dumps[0], dumps[1])

    def test_scenarios_accept_default_args_only(self) -> None:
        for fn in workflows.SCENARIOS.values():
            clock = SimClock()
            fn(MessageBus(clock), clock)

    def test_full_run_is_reproducible(self) -> None:
        dumps = []
        for _ in range(2):
            company, _ = make_env()
            for fn in workflows.SCENARIOS.values():
                company.seed(fn(company.bus, company.clock))
            company.run(180)
            dumps.append(company.log.to_jsonl())
        self.assertEqual(dumps[0], dumps[1])
        self.assertTrue(dumps[0])


class EmissionTests(unittest.TestCase):
    def test_only_published_topics_are_emitted(self) -> None:
        for name in workflows.SCENARIOS:
            with self.subTest(scenario=name):
                company, _ = run_scenario(name, 150)
                for e in emitted(company):
                    self.assertIn(e.topic, publishes_for(DEPT))
                    self.assertNotIn(".internal.", e.topic)

    def test_log_events_never_collide_with_topic_argument(self) -> None:
        company, _ = make_env()
        for name, fn in workflows.SCENARIOS.items():
            company.seed(fn(company.bus, company.clock))
        company.run(30)
        self.assertEqual(company.log.query(topic="system.agent_error"), [])

    def test_published_topics_reached_across_scenarios(self) -> None:
        seen: set[str] = set()
        for name in workflows.SCENARIOS:
            company, _ = run_scenario(name, 150)
            seen |= emitted_topics(company)
        for topic in ("sales.lead_qualified", "sales.proposal_requested", "sales.security_review_requested",
                      "sales.deal_approval_requested", "sales.proposal_sent", "sales.deal_won",
                      "sales.deal_lost", "sales.renewal_proposal_sent"):
            self.assertIn(topic, seen)

    def test_budget_and_hiring_topics(self) -> None:
        company, agent = make_env()
        company.inject("finance.budget_cycle_opened", {"budget_cycle_id": "BUD-2027"}, sender="finance",
                       delay_days=280)  # Q4 FY2026: plan year 2
        company.inject("executive.budget_approved", {"budget_cycle_id": "BUD-2027"}, sender="executive",
                       delay_days=285)
        company.run(290)
        subs = [e for e in emitted(company) if e.topic == "sales.budget_submitted"]
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0].data["body"]["people_gbp"], 1_300_000)
        self.assertEqual(subs[0].data["body"]["non_people_gbp"], 800_000)
        hires = [e for e in emitted(company) if e.topic == "sales.hire_requested"]
        self.assertEqual(len(hires), len(sales_agent.HIRING_PLAN[2]))


class BehaviourTests(unittest.TestCase):
    def _lead(self, **kw) -> dict:
        body = {"lead_id": "LD-00500", "company": "Test Co", "employees": 500, "sector": "logistics",
                "contact_role": "Chief Executive Officer", "pain": "x", "stage": "mql", "score": 70,
                "tier": "compass_spark"}
        body.update(kw)
        return body

    def test_mql_lead_qualifies_and_requests_proposal(self) -> None:
        agent, bus, _, _ = standalone_agent()
        out = agent.handle(mk(bus, "marketing.lead_generated", self._lead()))
        self.assertEqual([m.topic for m in out], ["sales.lead_qualified", "sales.proposal_requested"])
        deal = next(iter(agent.state["deals"].values()))
        self.assertEqual(deal["stage"], "qualified")
        self.assertEqual(out[0].body["due_day"], 7)
        self.assertEqual(out[1].body["due_day"], 10)

    def test_nurture_lead_same_threshold_and_learning_case(self) -> None:
        agent, bus, _, log = standalone_agent()
        out = agent.handle(mk(bus, "marketing.lead_generated", self._lead(stage="nurture", score=40)))
        self.assertEqual(len(out), 2)
        self.assertEqual(len(agent.state["learning_cases"]), 1)
        self.assertTrue(log.query(topic="sales.activity.learning_case"))
        # the same lead with a low sales score is disqualified at the same threshold of 60
        weak = self._lead(lead_id="LD-00501", company="Weak Co", stage="nurture", contact_role="Analyst",
                          pain=None, sector="agriculture")
        self.assertEqual(agent.handle(mk(bus, "marketing.lead_generated", weak)), [])
        self.assertEqual(agent.state["learning_cases"].__len__(), 1)

    def test_mql_qualification_is_not_a_learning_case(self) -> None:
        agent, bus, _, _ = standalone_agent()
        agent.handle(mk(bus, "marketing.lead_generated", self._lead()))
        self.assertEqual(agent.state["learning_cases"], [])

    def test_lead_rubric_boundaries(self) -> None:
        agent, _, _, _ = standalone_agent()
        score, _ = agent._score_lead({"employees": 500, "sector": "Financial services", "contact_role": "CFO",
                                      "score_reasons": ["named_pain_point"], "budget_confirmed": True})
        self.assertEqual(score, 100)
        score, _ = agent._score_lead({"employees": 500, "sector": "retail"})
        self.assertEqual(score, 50)
        self.assertEqual(sales_agent.QUALIFICATION_THRESHOLD, 60)

    def test_us_lead_parked_and_out_of_icp_rejected(self) -> None:
        agent, bus, _, log = standalone_agent()
        self.assertEqual(agent.handle(mk(bus, "marketing.lead_generated", self._lead(country="US"))), [])
        self.assertTrue(log.query(topic="sales.activity.lead_parked"))
        self.assertEqual(agent.handle(mk(bus, "marketing.lead_generated",
                                         self._lead(lead_id="LD-1", employees=80))), [])
        self.assertTrue(log.query(topic="sales.activity.lead_disqualified"))

    def test_duplicate_lead_is_merged(self) -> None:
        agent, bus, _, _ = standalone_agent()
        agent.handle(mk(bus, "marketing.lead_generated", self._lead()))
        self.assertEqual(agent.handle(mk(bus, "marketing.lead_generated", self._lead())), [])
        self.assertEqual(len(agent.state["deals"]), 1)

    def test_decision_window_by_tier(self) -> None:
        for tier, days in DECISION_WINDOWS.items():
            with self.subTest(tier=tier):
                self.assertEqual(sales_agent.DECISION_WINDOW_DAYS[tier], days)
                agent, bus, _, _ = standalone_agent()
                agent.handle(mk(bus, "marketing.lead_generated", self._lead(tier=tier)))
                self.assertEqual(next(iter(agent.state["deals"].values()))["decision_lag_days"], days)

    def test_sales_cycle_is_about_ten_days_plus_window(self) -> None:
        _, agent = run_scenario("inbound_lead_to_signed_contract", 120)
        snap = {k.name: k for k in agent.kpi_snapshot()}
        self.assertAlmostEqual(snap["sales_cycle_days"].actual, 48, delta=3)  # 8 days to proposal + 40 window
        self.assertAlmostEqual(snap["proposal_turnaround_days"].actual, 8, delta=1)
        self.assertEqual(snap["new_logos_won"].actual, 1.0)
        self.assertEqual(snap["new_logo_acv_bookings_gbp"].actual, 45000.0)

    def test_pipeline_stage_negotiation_is_reached(self) -> None:
        company, agent = run_scenario("inbound_lead_to_signed_contract", 120)
        self.assertTrue(company.log.query(topic="sales.activity.negotiation"))
        _, agent = run_scenario("rfp_forge_scale_with_approvals", 80)
        deal = next(iter(agent.state["deals"].values()))
        self.assertEqual(deal["stage"], "negotiation")  # high contract risk = redlines
        self.assertEqual(agent.pipeline_by_stage()["negotiation"], 1)
        self.assertGreater(agent._weighted_pipeline(), 0.6 * 570000)

    def test_expansion_and_renewals_are_not_new_logos(self) -> None:
        _, agent = run_scenario("credit_hold_expansion", 160)
        stats = agent.state["stats"]
        self.assertEqual(stats["won"], 0)
        self.assertEqual(stats["bookings_gbp"], 0)
        self.assertEqual(stats["expansion_won"], 1)
        self.assertGreater(stats["expansion_and_renewal_bookings_gbp"], 0)
        _, agent = run_scenario("renewal_and_churn_defence", 60)
        stats = agent.state["stats"]
        self.assertEqual(stats["bookings_gbp"], 0)
        self.assertGreater(stats["expansion_and_renewal_bookings_gbp"], 200000)
        self.assertEqual(stats["renewals_confirmed"], 1)

    def test_change_order_is_not_a_new_logo(self) -> None:
        company, agent = make_env()
        company.inject("delivery.scope_change_requested", {
            "client_id": "CL-0110", "client_name": "X", "days_by_level": {"senior_consultant": 8},
            "outcome": "won"}, sender="delivery")
        company.run(5)
        deal = next(iter(agent.state["deals"].values()))
        self.assertTrue(deal["change_order"])
        self.assertEqual(deal["list_price_gbp"], 8400)  # 8 x 1,050 rate card
        self.assertEqual(deal["decision_lag_days"], sales_agent.CHANGE_ORDER_DECISION_DAYS)
        self.assertEqual(agent.state["stats"]["qualified"], 0)
        self.assertEqual(agent.state["stats"]["expansion_qualified"], 1)

    def test_funnel_kpis_split_by_source(self) -> None:
        agent, bus, _, _ = standalone_agent()
        stats = agent.state["stats"]
        stats.update({"leads": 10, "lead_qualified": 3, "qualified": 4, "expansion_qualified": 6,
                      "nl_proposals_sent": 2, "proposals_sent": 7, "won": 1, "lost": 1, "expansion_won": 5,
                      "expansion_lost": 3, "qualified_not_proposed": 4})
        snap = {k.name: k.actual for k in agent.kpi_snapshot()}
        self.assertAlmostEqual(snap["lead_to_qualified_rate"], 30.0)      # marketing leads only
        self.assertAlmostEqual(snap["qualified_to_proposal_rate"], 50.0)  # new-logo funnel only
        self.assertAlmostEqual(snap["win_rate"], 50.0)                    # expansion and pre-proposal losses out

    def test_pre_proposal_loss_is_excluded_from_win_rate(self) -> None:
        company, agent = make_env()
        company.inject("marketing.lead_generated", {
            "lead_id": "LD-1", "company": "Test Co", "employees": 500, "sector": "retail",
            "contact_role": "CEO", "pain": "p", "tier": "compass_spark"}, sender="marketing")
        company.run(1)
        deal = next(iter(agent.state["deals"].values()))
        company.inject("executive.deal_decision_made", {"deal_id": deal["deal_id"], "decision": "rejected"},
                       sender="executive")
        company.run(2)
        stats = agent.state["stats"]
        self.assertEqual((stats["won"], stats["lost"], stats["qualified_not_proposed"]), (0, 0, 1))
        self.assertIn("sales.deal_lost", emitted_topics(company))

    def test_credit_hold_blocks_proposal_until_release(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_credit_hold_expansion(company.bus, company.clock))
        company.run(15)
        deal = next(iter(agent.state["deals"].values()))
        self.assertTrue(deal["proposal_id"])
        self.assertTrue(deal["held"])
        self.assertEqual(deal["stage"], "proposal_build")
        self.assertNotIn("sales.proposal_sent", emitted_topics(company))
        self.assertTrue(company.log.query(topic="sales.activity.proposal_held"))
        company.run(10)  # payment received on day 20
        self.assertIn("sales.proposal_sent", emitted_topics(company))
        self.assertEqual(deal["stage"], "proposal_sent")
        self.assertNotIn("client_invoice_overdue", [f for f in agent._legal_flags(deal)])
        self.assertNotIn("non_standard_legal_terms", deal["approvals_needed"])

    def test_cfo_release_in_decision_lifts_hold(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_credit_hold_expansion(company.bus, company.clock)[:4])
        company.run(10)
        deal = next(iter(agent.state["deals"].values()))
        self.assertTrue(deal["held"])
        company.inject("executive.deal_decision_made", {"deal_id": deal["deal_id"], "decision": "approved",
                                                         "cfo_release": True}, sender="executive")
        company.run(2)
        self.assertEqual(deal["stage"], "proposal_sent")

    def test_commission_half_then_balance_and_clawback(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_inbound_lead_to_signed_contract(company.bus, company.clock))
        company.run(58)
        self.assertAlmostEqual(agent.state["commission_accrued_gbp"], 765.0)  # 1.7% of 45,000
        self.assertEqual(agent.state["commission_released_gbp"], 0)
        company.run(6)  # first payment, day 62
        self.assertAlmostEqual(agent.state["commission_released_gbp"], 382.5)
        company.run(10)  # a further ordinary payment must not release more
        company.inject("finance.payment_received", {"client_id": "CL-0101", "milestone": "M2 mid-point"},
                       sender="finance")
        company.run(2)
        self.assertAlmostEqual(agent.state["commission_released_gbp"], 382.5)
        company.run(35)  # final milestone payment, day 100
        self.assertAlmostEqual(agent.state["commission_released_gbp"], 765.0)

    def test_clawback_on_termination_within_90_days(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_inbound_lead_to_signed_contract(company.bus, company.clock)[:7])
        company.inject("customer_success.client_churned", {"client_id": "CL-0101"}, sender="customer_success",
                       delay_days=80)
        company.run(85)
        self.assertAlmostEqual(agent.state["commission_clawed_back_gbp"], 765.0)
        self.assertEqual(agent.state["commission_released_gbp"], 0)

    def test_no_clawback_after_90_days(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_inbound_lead_to_signed_contract(company.bus, company.clock)[:7])
        company.inject("customer_success.client_churned", {"client_id": "CL-0101"}, sender="customer_success",
                       delay_days=56 + 91)
        company.run(150)
        self.assertEqual(agent.state["commission_clawed_back_gbp"], 0)

    def test_crisis_caps_discount_and_ceo_lifts_it(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_crisis_discount_cap_and_lift(company.bus, company.clock))
        company.run(18)
        self.assertTrue(agent.state["crisis"])
        deal = next(iter(agent.state["deals"].values()))
        self.assertEqual(deal["discount_pct"], 5.0)
        sent = [e for e in emitted(company) if e.topic == "sales.proposal_sent"]
        self.assertEqual(sent[0].data["body"]["delivery_start_lag_days"], 14)
        company.run(5)  # day 20 lifting instruction
        self.assertFalse(agent.state["crisis"])
        self.assertTrue(company.log.query(topic="sales.activity.crisis_lifted"))

    def test_crisis_lifts_when_ceo_instruction_task_closed(self) -> None:
        company, agent = make_env()
        company.inject("executive.crisis_declared", {"severity": "high"}, sender="executive")
        company.run(3)
        self.assertTrue(agent.state["crisis"])
        agent.update_task(agent.state["crisis_task_id"], "done")
        company.run(2)
        self.assertFalse(agent.state["crisis"])

    def test_crisis_stays_on_after_review_period_but_raises_task(self) -> None:
        company, agent = make_env()
        company.inject("executive.crisis_declared", {"severity": "high"}, sender="executive")
        company.run(sales_agent.CRISIS_REVIEW_DAYS + 3)
        self.assertTrue(agent.state["crisis"])
        self.assertTrue(agent.state["crisis_review_raised"])

    def test_approvals_follow_delegations(self) -> None:
        company, agent = run_scenario("rfp_forge_scale_with_approvals", 20)
        reqs = [e for e in emitted(company) if e.topic == "sales.deal_approval_requested"]
        self.assertEqual(len(reqs), 1)
        body = reqs[0].data["body"]
        self.assertEqual(body["discount_pct"], 12.0)
        self.assertIn("discount_above_10pct", body["reasons"])
        self.assertIn("deal_at_least_500k", body["reasons"])
        self.assertEqual(body["approvers"], ["ceo", "finance_head"])
        self.assertFalse(body["board_notification"])
        self.assertEqual(agent.state["deals"]["DL-0001"]["net_gbp"], 572000)

    def test_proposal_not_released_while_approval_pending(self) -> None:
        company, _ = run_scenario("rfp_forge_scale_with_approvals", 15)
        self.assertNotIn("sales.proposal_sent", emitted_topics(company))
        company, _ = run_scenario("rfp_forge_scale_with_approvals", 20)
        self.assertIn("sales.proposal_sent", emitted_topics(company))

    def test_compliance_kpi_is_full_for_scenarios(self) -> None:
        _, agent = run_scenario("rfp_forge_scale_with_approvals", 30)
        snap = {k.name: k.actual for k in agent.kpi_snapshot()}
        self.assertEqual(snap["discount_policy_compliance_percent"], 100.0)
        self.assertAlmostEqual(snap["average_discount_percent"], 12.0)

    def test_renewal_uplift_cap_and_save_offer(self) -> None:
        company, agent = run_scenario("renewal_and_churn_defence", 10)
        proposals = [e.data["body"] for e in emitted(company) if e.topic == "sales.renewal_proposal_sent"]
        self.assertEqual(len(proposals), 2)
        self.assertEqual(proposals[0]["uplift_pct"], 6.5)  # CPI 4.5 + 2
        self.assertTrue(proposals[1]["save_offer"])
        self.assertEqual(proposals[1]["uplift_pct"], 0.0)
        self.assertEqual(agent.state["stats"]["renewals_on_time"], 2)
        self.assertLessEqual(max(p["uplift_pct"] for p in proposals), sales_agent.KEEP_UPLIFT_CAP_PCT)

    def test_churn_closes_open_deals(self) -> None:
        company, agent = run_scenario("renewal_and_churn_defence", 60)
        lost = [e.data["body"] for e in emitted(company) if e.topic == "sales.deal_lost"]
        self.assertTrue(any(b["reason"] == "client_churned" for b in lost))

    def test_capacity_start_lag_and_tasks(self) -> None:
        company, agent = run_scenario("engagement_completion_and_change_order", 20)
        self.assertEqual(sum(1 for d in agent.state["deals"].values() if d["change_order"]), 1)
        self.assertEqual(sum(1 for d in agent.state["deals"].values() if d["source"] == "engagement_completed"), 1)
        titles = " ".join(t.title for t in agent.tasks.values())
        self.assertIn("proposal templates", titles)
        topics = [e.topic for e in emitted(company)]
        self.assertEqual(topics.count("sales.lead_qualified"), 1)  # change orders are not announced as leads

    def test_security_waived_for_expansion(self) -> None:
        company, _ = run_scenario("engagement_completion_and_change_order", 20)
        self.assertNotIn("sales.security_review_requested", emitted_topics(company))

    def test_price_override_and_state(self) -> None:
        agent, bus, _, _ = standalone_agent()
        agent.handle(mk(bus, "executive.pricing_change_approved", {"tier": "forge_pilot", "change_pct": 10}))
        self.assertEqual(agent._price("forge_pilot"), 99000)
        self.assertTrue(agent.state)

    def test_no_wall_clock_or_uuid_in_sources(self) -> None:
        for fname in ("agent.py", "workflows.py"):
            with open(os.path.join(DEPT_DIR, fname), encoding="utf-8") as fh:
                src = fh.read()
            for banned in ("uuid4", "datetime.now", "date.today", "time.time(", "import requests",
                           "urllib.request"):
                self.assertNotIn(banned, src, f"{fname} contains {banned}")


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

    def test_sops_format(self) -> None:
        text = read_doc("sops.md")
        ids = re.findall(r"^## (SOP-SALES-\d{2}): ", text, flags=re.M)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for sub in ("### Steps", "### Outputs and messages", "### SLA and controls",
                    "### Exceptions and escalation"):
            self.assertGreaterEqual(text.count(sub), len(ids), sub)
        for field in ("**Owner**:", "**Trigger**:", "**Inputs**:"):
            self.assertGreaterEqual(text.count(field), len(ids), field)
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)

    def test_every_subscribed_topic_is_a_sop_trigger(self) -> None:
        text = read_doc("sops.md")
        triggers = " ".join(re.findall(r"^\*\*Trigger\*\*:(.*)$", text, flags=re.M))
        for topic in subscribes_for(DEPT):
            self.assertIn(f"`{topic}`", triggers, f"{topic} is not the Trigger of any SOP")

    def test_every_published_topic_is_in_sop_outputs(self) -> None:
        text = read_doc("sops.md")
        outputs = " ".join(part.split("### SLA and controls", 1)[0]
                           for part in text.split("### Outputs and messages")[1:])
        for topic in publishes_for(DEPT):
            self.assertIn(f"`{topic}`", outputs, f"{topic} missing from SOP outputs")

    def test_policy_constants_match_sops(self) -> None:
        text = read_doc("sops.md")
        section = text.split("## Policy constants", 1)[1]
        for needle in ("200 to 2,000", "60 of 100", "10%", "£500,000", "£1,500,000", "5%", "cap 7%",
                       "60 days before term end", "1.7%", "7 days", "10 days", "30 days", "14 days", "£90,000",
                       "negotiation 0.60", "Spark 40, Essential 45, Pilot 50, Sprint and Plus 60, Build 80, "
                       "Programme and Enterprise 85, Scale 105"):
            self.assertIn(needle, section, needle)
        a = sales_agent
        self.assertEqual((a.ICP_MIN_EMPLOYEES, a.ICP_MAX_EMPLOYEES), (200, 2000))
        self.assertEqual(a.QUALIFICATION_THRESHOLD, 60)
        self.assertEqual(a.DISCOUNT_SALES_HEAD_MAX_PCT, 10.0)
        self.assertEqual((a.DEAL_CEO_THRESHOLD_GBP, a.DEAL_BOARD_THRESHOLD_GBP), (500_000, 1_500_000))
        self.assertEqual(a.CRISIS_DISCOUNT_CEILING_PCT, 5.0)
        self.assertEqual((a.KEEP_UPLIFT_CAP_PCT, a.KEEP_UPLIFT_MARGIN_PCT, a.DEFAULT_CPI_PCT), (7.0, 2.0, 3.0))
        self.assertEqual(a.RENEWAL_LEAD_DAYS, 60)
        self.assertEqual(a.NEW_BUSINESS_COMMISSION_RATE, 0.017)
        self.assertEqual((a.SCOPING_SLA_DAYS, a.SECURITY_REVIEW_SLA_DAYS, a.PROPOSAL_VALIDITY_DAYS), (7, 10, 30))
        self.assertEqual(a.SDR_LEADS_PER_MONTH, 60)
        self.assertEqual(a.STAGE_WEIGHTS["negotiation"], 0.60)
        self.assertEqual(a.COMMISSION_CLAWBACK_DAYS, 90)
        self.assertEqual(a.PRICE_LIST["forge_pilot"][1], 90_000)

    def test_blueprint_mentions_head_and_agent_class(self) -> None:
        text = read_doc("blueprint.md")
        self.assertIn("Chief Revenue Officer", text)
        self.assertIn("SalesAgent", read_doc("kpis.md"))

    def test_kpi_doc_has_fifteen_kpis(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("\n## 2.", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)]
        self.assertEqual(len(rows), len(KPIS))
        self.assertEqual(len(rows), 15)

    def test_kpi_doc_company_targets_consistent(self) -> None:
        text = read_doc("kpis.md")
        row = next(r for r in text.splitlines() if r.startswith("| new_logos_won |"))
        cells = [c.strip() for c in row.strip("|").split("|")]
        self.assertEqual(cells[3:6], ["24", "45", "85"])  # COMPANY.md §5.1
        row = next(r for r in text.splitlines() if r.startswith("| sales_cycle_days |"))
        cells = [c.strip() for c in row.strip("|").split("|")]
        self.assertEqual(cells[3:6], ["75", "75", "70"])  # COMPANY.md §5.3


class BudgetTests(unittest.TestCase):
    def test_company_md_row_is_what_we_expect(self) -> None:
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            row = next(r for r in fh.read().splitlines() if r.startswith("| sales |") and "850" in r)
        nums = [int(c.replace(",", "")) for c in re.findall(r"[\d,]+", row)]
        self.assertEqual(tuple(nums[:3]), BUDGET_PEOPLE)
        self.assertEqual(tuple(nums[3:6]), BUDGET_NON_PEOPLE)
        self.assertEqual(tuple(nums[6:9]), BUDGET_TOTAL)

    def test_totals_are_internally_consistent(self) -> None:
        for p, n, t in zip(BUDGET_PEOPLE, BUDGET_NON_PEOPLE, BUDGET_TOTAL):
            self.assertEqual(p + n, t)

    def test_agent_budget_constants_match_company_md(self) -> None:
        for year, (people, non_people) in sales_agent.DEPT_BUDGET_GBP.items():
            self.assertEqual(people, BUDGET_PEOPLE[year - 1] * 1000)
            self.assertEqual(non_people, BUDGET_NON_PEOPLE[year - 1] * 1000)

    def test_economics_budget_table_matches_envelope(self) -> None:
        text = read_doc("economics.md")
        section = text.split("## 1. Budget", 1)[1].split("\n## 2.", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\|\s*\**\s*(Department total|Non-people subtotal)",
                                                           r, flags=re.I)]
        self.assertEqual(len(rows), 2)
        nums = [[float(x.replace(",", "")) for x in re.findall(r"-?\d[\d,]*\.?\d*", r.replace("**", ""))]
                for r in rows]
        for expected, got in zip(BUDGET_NON_PEOPLE, nums[0]):
            self.assertLessEqual(abs(expected - got), 5)
        for expected, got in zip(BUDGET_TOTAL, nums[1]):
            self.assertLessEqual(abs(expected - got), 5)
        people_row = next(r for r in section.splitlines() if r.startswith("| **People**"))
        people = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", people_row.split("|")[2:5].__str__())]
        for expected, got in zip(BUDGET_PEOPLE, people):
            self.assertLessEqual(abs(expected - got), 5)

    def test_non_people_lines_sum_to_subtotal(self) -> None:
        text = read_doc("economics.md")
        section = text.split("## 1. Budget", 1)[1].split("\n## 2.", 1)[0]
        table = section.split("Check:", 1)[0]
        lines = [r for r in table.splitlines() if r.startswith("| ") and not r.startswith("| **")
                 and not r.startswith("| Line") and not r.startswith("|---")]
        sums = [0.0, 0.0, 0.0]
        for r in lines:
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            for i in range(3):
                sums[i] += float(cells[1 + i].replace(",", ""))
        for expected, got in zip(BUDGET_NON_PEOPLE, sums):
            self.assertLessEqual(abs(expected - got), 5)

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

    def test_agent_count_in_blueprint_matches_company_md(self) -> None:
        text = read_doc("blueprint.md")
        self.assertIn("3 / 9 / 18", text)

    def test_hiring_plan_titles_exist_in_blueprint(self) -> None:
        text = read_doc("blueprint.md")
        for plan in sales_agent.HIRING_PLAN.values():
            for title, _level, _count, _quarter in plan:
                self.assertIn(f"| {title} |", text, title)


if __name__ == "__main__":
    unittest.main()
