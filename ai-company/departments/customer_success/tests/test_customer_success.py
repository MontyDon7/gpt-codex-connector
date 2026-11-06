"""Tests for the customer_success department."""

import os
import unittest

from core import (Company, EventLog, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from core.topics import TOPIC_SUBSCRIBERS
from departments.customer_success import workflows
from departments.customer_success import agent as agent_module
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
                    self.assertIn(m.topic, agent.PUBLISHES, topic)

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


def deal(bus, agent, cid="CL-0001", **extra):
    return agent.handle(bus.make_message("sales", "*", "sales.deal_won", {"client_id": cid, "client_name": cid,
                                                                       **extra}))


def ticket(bus, agent, severity="medium", cid="CL-0001", **extra):
    return agent.handle(bus.make_message("external", DEPT, "external.client_feedback_submitted", {
        "client_id": cid, "client_name": cid, "kind": "support_ticket", "severity": severity, **extra}))


def advance(clock, agent, days):
    out = []
    for _ in range(days):
        clock.advance()
        out += agent.tick()
    return out


def read_table(text, header_start):
    """Rows (list of cell strings) of the markdown table whose header row starts with header_start."""
    lines = text.splitlines()
    i = next(n for n, line in enumerate(lines) if line.startswith(header_start))
    rows = []
    for line in lines[i + 2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


class InternalTopicTests(unittest.TestCase):
    def test_no_internal_topic_in_log_or_bus(self):
        for name in workflows.SCENARIOS:
            company = run_scenario(name, ticks=70)
            self.assertFalse([m.topic for m in company.bus.history if ".internal." in m.topic], name)
            self.assertFalse([e.topic for e in company.log.query(department=DEPT) if ".internal." in e.topic], name)
        for params in ({}, {"client_decision": "churn"}):
            company = run_scenario("keep_renewal_cycle", ticks=40, **params)
            self.assertFalse([m.topic for m in company.bus.history if ".internal." in m.topic])

    def test_source_does_not_mention_internal_namespace(self):
        with open(os.path.join(HERE, "agent.py"), encoding="utf-8") as fh:
            self.assertNotIn("customer_success.internal", fh.read())

    def test_renewal_decision_waits_for_the_decision_window(self):
        agent, bus, clock, log = make_agent()
        agent.handle(bus.make_message("legal", "*", "legal.contract_signed", {
            "client_id": "CL-0002", "client_name": "Harrowgate", "service_line": "keep", "tier": "keep_plus",
            "amount_gbp": 216000, "start_day": clock.day - 300}))
        agent.handle(bus.make_message("sales", "*", "sales.renewal_proposal_sent", {
            "client_id": "CL-0002", "amount_gbp": 226800}))
        self.assertEqual(len(agent.state["scheduled"]), 1)
        early = advance(clock, agent, agent_module.CLIENT_DECISION_WINDOW_DAYS - 1)
        self.assertNotIn("customer_success.renewal_confirmed", [m.topic for m in early])
        late = advance(clock, agent, 1)
        self.assertIn("customer_success.renewal_confirmed", [m.topic for m in late])
        self.assertEqual(agent.state["scheduled"], [])

    def test_save_deadline_is_tick_driven(self):
        agent, bus, clock, log = make_agent()
        deal(bus, agent, "CL-0003")
        agent.handle(bus.make_message("external", DEPT, "external.client_notice_of_termination", {
            "client_id": "CL-0003", "reason": "insourcing_decision", "notice_period_days": 30}))
        self.assertEqual(agent.state["scheduled"][0]["kind"], "save_deadline")
        self.assertEqual(agent.state["scheduled"][0]["due_day"], 14)
        out = advance(clock, agent, 14)
        self.assertEqual([m.topic for m in out if m.topic == "customer_success.client_churned"],
                         ["customer_success.client_churned"])


class SupportSlaTests(unittest.TestCase):
    def test_measured_times_within_sla_record_no_breach(self):
        agent, bus, clock, log = make_agent()
        deal(bus, agent)
        ticket(bus, agent, "high", first_response_hours=10, resolution_hours=30)   # keep_essential P2 is 10 / 30
        t = agent.state["tickets"][0]
        self.assertFalse(t["response_breach"] or t["resolution_breach"])
        self.assertEqual(agent.kpi_snapshot()[[k.name for k in KPIS].index("support_first_response_sla")].actual,
                         100.0)

    def test_breach_is_recorded_and_hits_support_component(self):
        agent, bus, clock, log = make_agent()
        deal(bus, agent)
        before = agent.clients["CL-0001"]["components"]["support"]
        ticket(bus, agent, "medium", first_response_hours=21, resolution_hours=51)  # P3 essential is 20 / 50
        t = agent.state["tickets"][0]
        self.assertTrue(t["response_breach"] and t["resolution_breach"])
        expected = before - agent_module.SUPPORT_HIT["medium"] - 2 * agent_module.SLA_BREACH_SUPPORT_HIT
        self.assertEqual(agent.clients["CL-0001"]["components"]["support"], expected)
        events = [e for e in log.query(department=DEPT) if e.topic == "customer_success.activity.sla_breach"]
        self.assertEqual(len(events), 1)
        self.assertNotIn("topic", events[0].data)
        self.assertTrue(any("SLA breach" in task.title for task in agent.tasks.values()))

    def test_breach_uses_the_clients_keep_tier_targets(self):
        agent, bus, clock, log = make_agent()
        agent.handle(bus.make_message("legal", "*", "legal.contract_signed", {
            "client_id": "CL-0001", "client_name": "CL-0001", "service_line": "keep", "tier": "keep_enterprise",
            "start_day": clock.day}))
        ticket(bus, agent, "critical", first_response_hours=0.5)       # enterprise P1 first response is 0.25
        self.assertTrue(agent.state["tickets"][0]["response_breach"])
        ticket(bus, agent, "critical", cid="CL-0002", first_response_hours=0.5)   # no Keep: essential P1 is 4
        self.assertFalse(agent.state["tickets"][1]["response_breach"])

    def test_simulated_times_breach_only_when_the_desk_is_loaded(self):
        agent, bus, clock, log = make_agent()
        deal(bus, agent)
        for _ in range(6):
            ticket(bus, agent, "high")
        flags = [t["response_breach"] for t in agent.state["tickets"]]
        self.assertEqual(flags[:3], [False, False, False])
        self.assertTrue(flags[-1])
        sla = agent.kpi_snapshot()[[k.name for k in KPIS].index("support_first_response_sla")].actual
        self.assertEqual(sla, round(100.0 * flags.count(False) / len(flags), 1))

    def test_support_escalated_carries_breach_flags(self):
        agent, bus, clock, log = make_agent()
        deal(bus, agent)
        out = ticket(bus, agent, "critical", first_response_hours=9)
        esc = [m for m in out if m.topic == "customer_success.support_escalated"][0]
        self.assertTrue(esc.body["sla_response_breach"])

    def test_sla_kpi_has_no_actual_before_any_ticket(self):
        agent, *_ = make_agent()
        self.assertTrue(all(k.actual is None for k in agent.kpi_snapshot()))


class HandoverTests(unittest.TestCase):
    def test_handover_days_measured_from_signature_to_kickoff(self):
        agent, bus, clock, log = make_agent()
        sign = {"client_id": "CL-0001", "client_name": "A", "service_line": "forge", "tier": "forge_build",
                "start_day": clock.day}
        agent.handle(bus.make_message("legal", "*", "legal.contract_signed", sign))
        advance(clock, agent, 6)
        agent.handle(bus.make_message("delivery", "*", "delivery.engagement_kickoff", {"client_id": "CL-0001"}))
        self.assertEqual(agent.state["handover_days"], [6])
        actual = {k.name: k.actual for k in agent.kpi_snapshot()}
        self.assertEqual(actual["onboarding_handover_days"], 6.0)

    def test_overdue_handover_flags_once_and_late_completion_is_recorded(self):
        agent, bus, clock, log = make_agent()
        agent.handle(bus.make_message("legal", "*", "legal.contract_signed", {
            "client_id": "CL-0001", "client_name": "A", "service_line": "forge", "tier": "forge_build",
            "start_day": clock.day}))
        advance(clock, agent, agent_module.HANDOVER_TARGET_DAYS + 3)
        overdue = [e for e in log.query(department=DEPT) if e.topic == "customer_success.activity.handover_overdue"]
        self.assertEqual(len(overdue), 1)
        agent.handle(bus.make_message("delivery", "*", "delivery.engagement_kickoff", {"client_id": "CL-0001"}))
        self.assertEqual(agent.state["handover_days"], [agent_module.HANDOVER_TARGET_DAYS + 3])

    def test_migrated_contract_has_no_onboarding_clock(self):
        agent, bus, clock, log = make_agent()
        clock.advance(100)
        agent.handle(bus.make_message("legal", "*", "legal.contract_signed", {
            "client_id": "CL-0001", "client_name": "A", "service_line": "keep", "tier": "keep_plus",
            "start_day": clock.day - 300}))
        agent.handle(bus.make_message("delivery", "*", "delivery.engagement_kickoff", {"client_id": "CL-0001"}))
        self.assertEqual(agent.state.get("handover_days", []), [])


class KeepAttachTests(unittest.TestCase):
    def test_policy_matches_company_md(self):
        targets = {k.name: k.target for k in KPIS}
        self.assertEqual(targets["keep_attach_forge_build_scale"], 100.0)       # COMPANY.md §2: every Build/Scale
        self.assertGreaterEqual(targets["keep_attach_compass_programme"], 40.0)  # COMPANY.md §2: at least 40%
        self.assertEqual(agent_module.KEEP_ATTACH_POLICY_PCT["forge_build"], 100.0)
        self.assertEqual(agent_module.KEEP_ATTACH_POLICY_PCT["forge_scale"], 100.0)
        self.assertEqual(agent_module.KEEP_ATTACH_POLICY_PCT["compass_programme"], 40.0)
        self.assertEqual(set(agent_module.KEEP_ATTACH), {"forge_build", "forge_scale", "compass_programme"})

    def _complete(self, bus, agent, cid, tier, eng):
        deal(bus, agent, cid)
        return agent.handle(bus.make_message("delivery", "*", "delivery.engagement_completed", {
            "client_id": cid, "client_name": cid, "engagement_id": eng, "tier": tier}))

    def test_attach_rate_measured_from_completions_and_signed_keep(self):
        agent, bus, clock, log = make_agent()
        self._complete(bus, agent, "CL-0001", "forge_build", "EN-0001")
        self._complete(bus, agent, "CL-0002", "forge_scale", "EN-0002")
        self.assertEqual({k.name: k.actual for k in agent.kpi_snapshot()}["keep_attach_forge_build_scale"], 0.0)
        agent.handle(bus.make_message("legal", "*", "legal.contract_signed", {
            "client_id": "CL-0001", "client_name": "CL-0001", "service_line": "keep", "tier": "keep_plus",
            "start_day": clock.day}))
        self.assertEqual({k.name: k.actual for k in agent.kpi_snapshot()}["keep_attach_forge_build_scale"], 50.0)

    def test_compass_programme_tracked_separately(self):
        agent, bus, clock, log = make_agent()
        self._complete(bus, agent, "CL-0003", "compass_programme", "EN-0003")
        actual = {k.name: k.actual for k in agent.kpi_snapshot()}
        self.assertEqual(actual["keep_attach_compass_programme"], 0.0)
        self.assertIsNone(actual["keep_attach_forge_build_scale"])

    def test_unattached_build_is_reoffered_then_escalated_as_policy_exception(self):
        agent, bus, clock, log = make_agent()
        self._complete(bus, agent, "CL-0001", "forge_build", "EN-0001")
        advance(clock, agent, agent_module.ATTACH_REOFFER_DAYS)
        topics = [e.topic for e in log.query(department=DEPT)]
        self.assertIn("customer_success.activity.keep_reoffer", topics)
        self.assertNotIn("customer_success.activity.keep_attach_lapsed", topics)
        advance(clock, agent, agent_module.ATTACH_WINDOW_DAYS - agent_module.ATTACH_REOFFER_DAYS)
        lapsed = [e for e in log.query(department=DEPT) if e.topic == "customer_success.activity.keep_attach_lapsed"]
        self.assertEqual(len(lapsed), 1)
        self.assertTrue(lapsed[0].data["policy_exception"])
        self.assertTrue(any("policy exception" in t.title and t.priority == "critical"
                            for t in agent.tasks.values()))

    def test_keep_already_live_counts_as_attached(self):
        agent, bus, clock, log = make_agent()
        agent.handle(bus.make_message("legal", "*", "legal.contract_signed", {
            "client_id": "CL-0001", "client_name": "CL-0001", "service_line": "keep", "tier": "keep_plus",
            "start_day": clock.day}))
        self._complete(bus, agent, "CL-0001", "forge_build", "EN-0001")
        self.assertEqual({k.name: k.actual for k in agent.kpi_snapshot()}["keep_attach_forge_build_scale"], 100.0)


class HiringTests(unittest.TestCase):
    def _fill(self, bus, agent, n):
        out = []
        for i in range(1, n + 1):
            out += deal(bus, agent, f"CL-{i:04d}", service_line="forge", tier="forge_pilot", amount_gbp=90000)
        return [m for m in out if m.topic == "customer_success.hire_requested"]

    def test_fy2026_csm_request_is_an_escalation_not_a_silent_breach(self):
        agent, bus, clock, log = make_agent()
        hires = self._fill(bus, agent, 23)
        self.assertEqual(len(hires), 1)
        body = hires[0].body
        self.assertTrue(body["outside_headcount_plan"])
        self.assertEqual(body["escalated_to"], "Chief Executive Officer")
        self.assertEqual(body["plan_year"], 2026)
        self.assertEqual(body["planned_role_headcount"], 0)
        self.assertIn("executive.headcount_approved", body["approval_path"])
        self.assertTrue(any(t.priority == "critical" and "Escalate to the CEO" in t.title
                            for t in agent.tasks.values()))
        self.assertIn("customer_success.activity.hire_escalated", [e.topic for e in log.query(department=DEPT)])
        self.assertEqual(TOPIC_SUBSCRIBERS["customer_success.hire_requested"], ("people",))

    def test_q4_request_for_a_fy2027_seat_is_inside_the_plan(self):
        agent, bus, clock, log = make_agent()
        clock.advance(clock.day_of(clock.date.replace(month=11, day=2)))
        hires = self._fill(bus, agent, 23)
        self.assertFalse(hires[0].body["outside_headcount_plan"])
        self.assertEqual(hires[0].body["plan_year"], 2027)
        self.assertNotIn("escalated_to", hires[0].body)

    def test_csm_request_beyond_the_role_plan_escalates_again(self):
        agent, bus, clock, log = make_agent()
        clock.advance(clock.day_of(clock.date.replace(month=2, day=2, year=2027)))
        bodies = [m.body for m in self._fill(bus, agent, 67)]
        self.assertEqual([b["outside_headcount_plan"] for b in bodies], [False, False, True])

    def _tickets_in_month(self, bus, agent, clock, n, **extra):
        deal(bus, agent, "CL-0001")
        for i in range(n):
            ticket(bus, agent, "low", ticket_id=f"TKT-{i:04d}", first_response_hours=1, **extra)

    def test_first_specialist_requested_when_tickets_exceed_30_in_a_month(self):
        agent, bus, clock, log = make_agent()
        clock.advance(clock.day_of(clock.date.replace(month=1, day=20, year=2027)))
        self._tickets_in_month(bus, agent, clock, 31)
        out = advance(clock, agent, 14)       # reaches 1 February 2027
        hires = [m for m in out if m.topic == "customer_success.hire_requested"]
        self.assertEqual([m.body["role_title"] for m in hires], ["Client Support Specialist"])
        self.assertEqual(hires[0].body["level"], "consultant")
        self.assertFalse(hires[0].body["outside_headcount_plan"])
        self.assertEqual(hires[0].body["tickets_in_month"], 31)

    def test_thirty_tickets_is_not_enough_and_a_month_is_reviewed_once(self):
        agent, bus, clock, log = make_agent()
        clock.advance(clock.day_of(clock.date.replace(month=1, day=20, year=2027)))
        self._tickets_in_month(bus, agent, clock, 30)
        out = advance(clock, agent, 40)
        self.assertEqual([m for m in out if m.topic == "customer_success.hire_requested"], [])

    def test_specialist_request_in_fy2026_is_escalated(self):
        agent, bus, clock, log = make_agent()
        clock.advance(clock.day_of(clock.date.replace(month=3, day=20)))
        self._tickets_in_month(bus, agent, clock, 31)
        out = advance(clock, agent, 14)
        hire = [m for m in out if m.topic == "customer_success.hire_requested"][0]
        self.assertTrue(hire.body["outside_headcount_plan"])

    def test_two_months_below_sla_floor_requests_an_extra_specialist(self):
        agent, bus, clock, log = make_agent()
        clock.advance(clock.day_of(clock.date.replace(month=1, day=2, year=2027)))
        deal(bus, agent, "CL-0001")
        out = []
        for _ in range(2):                                       # two months, one missed response each
            ticket(bus, agent, "low", first_response_hours=99)
            out += advance(clock, agent, 32)
        hires = [m for m in out if m.topic == "customer_success.hire_requested"]
        self.assertEqual(len(hires), 1)
        self.assertIn("first-response SLA below 95%", hires[0].body["trigger"])

    def test_renewals_manager_requested_above_30_renewals(self):
        agent, bus, clock, log = make_agent()
        clock.advance(clock.day_of(clock.date.replace(month=12, day=20, year=2027)))
        for i in range(31):
            agent.handle(bus.make_message("legal", "*", "legal.contract_signed", {
                "client_id": f"CL-{i + 1:04d}", "client_name": "C", "service_line": "keep", "tier": "keep_essential",
                "start_day": clock.day - 100}))
        out = advance(clock, agent, 14)
        roles = [m.body["role_title"] for m in out if m.topic == "customer_success.hire_requested"]
        self.assertIn("Renewals and Commercial Manager", roles)
        self.assertEqual(roles.count("Renewals and Commercial Manager"), 1)

    def test_only_documented_roles_are_ever_requested(self):
        self.assertEqual(set(agent_module.ROLE_PLAN), {"Customer Success Manager", "Client Support Specialist",
                                                       "Renewals and Commercial Manager"})


class DocCodeConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(HERE, "kpis.md"), encoding="utf-8") as fh:
            cls.kpis_md = fh.read()
        with open(os.path.join(HERE, "sops.md"), encoding="utf-8") as fh:
            cls.sops_md = fh.read()

    def test_kpis_mirror_kpis_md_exactly(self):
        rows = read_table(self.kpis_md, "| KPI id |")
        self.assertEqual([r[0] for r in rows], [k.name for k in KPIS])
        for row, k in zip(rows, KPIS):
            self.assertEqual(row[2], k.unit, k.name)
            self.assertEqual(float(row[3]), k.target, k.name)
            self.assertEqual(row[6] == "higher is better", k.higher_is_better, k.name)

    def test_support_sla_table_equals_code(self):
        rows = read_table(self.sops_md, "| Priority | Keep Essential |")
        tiers = ("keep_essential", "keep_plus", "keep_enterprise")
        for row in rows:
            for tier, cell in zip(tiers, row[1:]):
                first, second = [x.strip() for x in cell.split("/")]
                want = (float(first), None if second == "none" else float(second))
                self.assertEqual(SUPPORT_SLA[tier][row[0]], want, (tier, row[0]))

    def test_health_constants_equal_code(self):
        weights = {r[0]: float(r[1].rstrip("%")) / 100 for r in read_table(self.sops_md, "| Component | Weight |")}
        self.assertEqual(weights, agent_module.HEALTH_WEIGHTS)
        for needle in ("score 75 and above", "50 to under 75", "score 60 or above"):
            self.assertIn(needle, self.sops_md)
        self.assertEqual((agent_module.GREEN_MIN, agent_module.AMBER_MIN, agent_module.CLEAR_RISK_MIN),
                         (75.0, 50.0, 60.0))

    def test_threshold_constants_are_documented_with_code_values(self):
        sops = self.sops_md
        expected = {
            "SLA_BREACH_SUPPORT_HIT": agent_module.SLA_BREACH_SUPPORT_HIT,
            "TICKET_LOAD_BASE": agent_module.TICKET_LOAD_BASE,
            "TICKET_LOAD_PER_OPEN": agent_module.TICKET_LOAD_PER_OPEN,
            "TICKETS_MONTH_FIRST_SPECIALIST": agent_module.TICKETS_MONTH_FIRST_SPECIALIST,
            "LIVE_KEEP_FIRST_SPECIALIST": agent_module.LIVE_KEEP_FIRST_SPECIALIST,
            "TICKETS_MONTH_THIRD_SPECIALIST": agent_module.TICKETS_MONTH_THIRD_SPECIALIST,
            "SLA_HIRE_FLOOR_PCT": agent_module.SLA_HIRE_FLOOR_PCT,
            "RENEWALS_FOR_MANAGER": agent_module.RENEWALS_FOR_MANAGER,
            "CLIENTS_PER_NAMED_CSM": agent_module.CLIENTS_PER_NAMED_CSM,
            "HANDOVER_TARGET_DAYS": agent_module.HANDOVER_TARGET_DAYS,
            "ATTACH_REOFFER_DAYS": agent_module.ATTACH_REOFFER_DAYS,
            "ATTACH_WINDOW_DAYS": agent_module.ATTACH_WINDOW_DAYS,
            "TIME_TO_HIRE_DAYS": agent_module.TIME_TO_HIRE_DAYS,
        }
        constants = {r[0].strip("`"): r[1] for r in read_table(sops, "| Constant (code name) | Value |")}
        for name, value in expected.items():
            self.assertIn(name, constants, name)
            self.assertEqual(float(constants[name].split()[0].replace(",", "")), float(value), name)

    def test_keep_attach_targets_agree_with_company_md(self):
        rows = {r[0]: r for r in read_table(self.kpis_md, "| KPI id |")}
        self.assertEqual(rows["keep_attach_forge_build_scale"][3:6], ["100", "100", "100"])
        self.assertTrue(all(float(x) >= 40 for x in rows["keep_attach_compass_programme"][3:6]))
        self.assertNotIn("75% (FY2026)", self.sops_md)


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
