"""Tests for the customer_success department."""

import os
import unittest

from core import (Company, EventLog, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from departments.customer_success import workflows
from departments.customer_success.agent import (CustomerSuccessAgent, KPIS, SUPPORT_SLA, build_agent)

DEPT = "customer_success"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED = {
    "blueprint.md": ["# ", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles", "## 4. AI agents",
                     "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies", "## 8. Sources"],
    "sops.md": ["# ", "## Overview", "## SOP-CUSTOMER_SUCCESS-01:", "### Steps", "### Outputs and messages",
                "### SLA and controls", "### Exceptions and escalation"],
    "kpis.md": ["# ", "## 1. KPI summary", "## 2. Definitions and formulas",
                "## 3. Reporting cadence and data sources", "## 4. Links to company targets"],
    "economics.md": ["# ", "## 1. Budget", "## 2. Headcount cost build-up", "## 3. Pricing and unit economics",
                     "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md"],
}


def make_agent():
    clock = SimClock()
    bus = MessageBus(clock)
    log = EventLog(clock.start)
    agent = build_agent(MockLLM(), bus, clock, log)
    return agent, bus, clock, log


def run_scenario(name, ticks=70, **params):
    company = Company(use_departments=False, factories={DEPT: build_agent})
    company.seed(workflows.SCENARIOS[name](company.bus, company.clock, **params))
    company.run(ticks)
    return company


def topics_emitted(company):
    return [e.topic for e in company.log.query(department=DEPT) if e.topic.startswith("customer_success.")
            and not e.topic.startswith("customer_success.activity.")]


class BuildTests(unittest.TestCase):
    def test_build_agent(self):
        agent, *_ = make_agent()
        self.assertIsInstance(agent, CustomerSuccessAgent)
        self.assertEqual(class_name_for(DEPT), type(agent).__name__)
        self.assertEqual((agent.name, agent.department), (DEPT, DEPT))
        self.assertEqual(agent.role.title, "Chief Customer Officer")

    def test_topic_map(self):
        self.assertEqual(CustomerSuccessAgent.SUBSCRIBES, subscribes_for(DEPT))
        self.assertEqual(CustomerSuccessAgent.PUBLISHES, publishes_for(DEPT))

    def test_kpis(self):
        self.assertGreaterEqual(len(KPIS), 8)
        self.assertTrue(all(isinstance(k, Kpi) for k in KPIS))
        self.assertEqual(len({k.name for k in KPIS}), len(KPIS))

    def test_sla_tiers_ordered(self):
        for prio in ("P1", "P2", "P3", "P4"):
            self.assertLess(SUPPORT_SLA["keep_enterprise"][prio][0], SUPPORT_SLA["keep_plus"][prio][0] + 1e-9)
            self.assertLess(SUPPORT_SLA["keep_plus"][prio][0], SUPPORT_SLA["keep_essential"][prio][0])


class ScenarioTests(unittest.TestCase):
    def test_scenarios_build_valid_messages(self):
        self.assertGreaterEqual(len(workflows.SCENARIOS), 3)
        for name, fn in workflows.SCENARIOS.items():
            self.assertEqual(fn.__name__, "scenario_" + name)
            company = Company(use_departments=False, factories={DEPT: build_agent})
            msgs = fn(company.bus, company.clock)
            self.assertTrue(msgs, name)
            for m in msgs:
                self.assertIsInstance(m, Message)
                self.assertIsInstance(m.body, dict)

    def test_scenarios_run_and_log(self):
        for name in workflows.SCENARIOS:
            company = run_scenario(name)
            self.assertGreaterEqual(len(company.log.query(department=DEPT)), 1, name)

    def test_one_scenario_starts_from_subscribed_topic(self):
        company = Company(use_departments=False, factories={DEPT: build_agent})
        subs = set(subscribes_for(DEPT))
        starts = [name for name, fn in workflows.SCENARIOS.items()
                  if any(m.topic in subs for m in fn(company.bus, company.clock))]
        self.assertGreaterEqual(len(starts), 1)

    def test_determinism(self):
        for name in workflows.SCENARIOS:
            self.assertEqual(run_scenario(name).log.to_jsonl(), run_scenario(name).log.to_jsonl(), name)


class HandleTests(unittest.TestCase):
    def test_every_subscribed_topic_returns_valid_messages(self):
        for topic in subscribes_for(DEPT):
            for body in ({}, {"client_id": "CL-0099", "client_name": "Test Client Ltd", "severity": "high"}):
                agent, bus, clock, log = make_agent()
                msg = bus.make_message("external", DEPT, topic, body)
                out = agent.handle(msg)
                self.assertIsInstance(out, list, topic)
                for m in out:
                    self.assertIsInstance(m, Message)
                    self.assertTrue(m.topic in agent.PUBLISHES or m.topic.startswith("customer_success.internal."),
                                    (topic, m.topic))

    def test_unknown_topic_is_logged(self):
        agent, bus, *_ = make_agent()
        out = agent.handle(bus.make_message("sales", DEPT, "sales.lead_qualified", {}))
        self.assertEqual(out, [])

    def test_health_model_weights_sum_to_one(self):
        from departments.customer_success.agent import HEALTH_WEIGHTS
        self.assertAlmostEqual(sum(HEALTH_WEIGHTS.values()), 1.0)
        self.assertEqual(CustomerSuccessAgent.band_of(75.0), "green")
        self.assertEqual(CustomerSuccessAgent.band_of(74.9), "amber")
        self.assertEqual(CustomerSuccessAgent.band_of(49.9), "red")


class BehaviourTests(unittest.TestCase):
    def test_onboarding_emits_health_baseline(self):
        company = run_scenario("new_keep_client_onboarding", ticks=20)
        agent = company.agents[DEPT]
        client = agent.clients["CL-0001"]
        self.assertEqual(client["keep"]["tier"], "keep_plus")
        self.assertIn("customer_success.health_score_updated", topics_emitted(company))
        self.assertEqual(client["band"], "green")

    def test_renewal_cycle_confirms_with_uplift(self):
        company = run_scenario("keep_renewal_cycle", ticks=40)
        topics = topics_emitted(company)
        self.assertIn("customer_success.renewal_due", topics)
        self.assertIn("customer_success.renewal_confirmed", topics)
        confirmed = [m for m in company.bus.history if m.topic == "customer_success.renewal_confirmed"][0]
        self.assertEqual(confirmed.body["amount_gbp"], 226800)
        self.assertEqual(confirmed.body["nrr_delta_gbp"], 10800)

    def test_renewal_cycle_churn_path(self):
        company = run_scenario("keep_renewal_cycle", ticks=40, client_decision="churn")
        self.assertIn("customer_success.client_churned", topics_emitted(company))
        self.assertNotIn("customer_success.renewal_confirmed", topics_emitted(company))
        self.assertEqual(company.agents[DEPT].clients["CL-0002"]["status"], "churned")

    def test_termination_save_and_churn(self):
        saved = run_scenario("termination_notice_save", ticks=30)
        self.assertIn("customer_success.churn_risk_flagged", topics_emitted(saved))
        self.assertNotIn("customer_success.client_churned", topics_emitted(saved))
        self.assertNotEqual(saved.agents[DEPT].clients["CL-0003"]["status"], "churned")
        lost = run_scenario("termination_notice_save", ticks=30, reason="insourcing_decision")
        self.assertIn("customer_success.client_churned", topics_emitted(lost))

    def test_feedback_chain(self):
        company = run_scenario("feedback_and_support_escalation", ticks=20)
        topics = topics_emitted(company)
        for t in ("customer_success.feedback_received", "customer_success.support_escalated",
                  "customer_success.expansion_opportunity_identified", "customer_success.churn_risk_flagged"):
            self.assertIn(t, topics)
        esc = [m for m in company.bus.history if m.topic == "customer_success.support_escalated"][0]
        self.assertEqual(esc.body["priority"], "P1")
        self.assertEqual(esc.body["sla_response_hours"], 0.25)

    def test_engagement_completed_expansion_and_case_study(self):
        company = run_scenario("engagement_completed_expansion", ticks=30)
        topics = topics_emitted(company)
        exp = [m for m in company.bus.history
               if m.topic == "customer_success.expansion_opportunity_identified"][0]
        self.assertEqual((exp.body["tier"], exp.body["amount_gbp"]), ("keep_plus", 216000))
        self.assertIn("customer_success.case_study_approved", topics)

    def test_breach_flags_client_and_recovers_payment(self):
        company = run_scenario("data_breach_client_impact", ticks=20)
        flags = [m for m in company.bus.history if m.topic == "customer_success.churn_risk_flagged"]
        self.assertTrue(flags)
        self.assertEqual(flags[0].body["severity"], "critical")
        self.assertEqual(company.agents[DEPT].clients["CL-0005"]["overdue"], {})

    def test_budget_submission_matches_company_envelope(self):
        agent, bus, clock, log = make_agent()
        for budget_id, total in (("BUD-2026", 140000), ("BUD-2027", 790000), ("BUD-2028", 1630000)):
            out = agent.handle(bus.make_message("finance", "*", "finance.budget_cycle_opened",
                                                {"budget_id": budget_id}))
            self.assertEqual(out[0].topic, "customer_success.budget_submitted")
            self.assertEqual(out[0].body["amount_gbp"], total)

    def test_capacity_triggers_hire_request(self):
        agent, bus, clock, log = make_agent()
        out = []
        for i in range(1, 24):
            out += agent.handle(bus.make_message("sales", "*", "sales.deal_won", {
                "client_id": f"CL-{i:04d}", "client_name": f"Client {i}", "service_line": "forge",
                "tier": "forge_pilot", "amount_gbp": 90000}))
        hires = [m for m in out if m.topic == "customer_success.hire_requested"]
        self.assertEqual(len(hires), 1)
        self.assertEqual(hires[0].body["role_title"], "Customer Success Manager")

    def test_overdue_invoice_lowers_commercial_component(self):
        agent, bus, clock, log = make_agent()
        agent.handle(bus.make_message("sales", "*", "sales.deal_won", {"client_id": "CL-0001"}))
        before = agent.clients["CL-0001"]["components"]["commercial"]
        agent.handle(bus.make_message("finance", "*", "finance.invoice_overdue",
                                      {"client_id": "CL-0001", "invoice_id": "INV-2026-0001", "days_overdue": 50}))
        self.assertLess(agent.clients["CL-0001"]["components"]["commercial"], before)


class DocTests(unittest.TestCase):
    def test_docs_exist_with_required_headings(self):
        for fname, headings in REQUIRED.items():
            path = os.path.join(HERE, fname)
            self.assertTrue(os.path.exists(path), fname)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            pos = -1
            for h in headings:
                idx = text.find(h, pos + 1) if h != "# " else text.find("# ")
                self.assertGreater(idx, -1, f"{fname}: missing heading {h!r}")
                pos = max(pos, idx) if h != "# " else pos

    def test_sops_cover_topics_and_at_least_eight(self):
        with open(os.path.join(HERE, "sops.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertGreaterEqual(text.count("\n## SOP-CUSTOMER_SUCCESS-"), 8)
        for topic in subscribes_for(DEPT):
            self.assertIn(topic, text, f"subscribed topic not in sops: {topic}")
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic not in sops: {topic}")

    def test_kpis_doc_lists_every_agent_kpi(self):
        with open(os.path.join(HERE, "kpis.md"), encoding="utf-8") as fh:
            text = fh.read()
        for k in KPIS:
            self.assertIn(f"| {k.name} |", text, k.name)


if __name__ == "__main__":
    unittest.main()
