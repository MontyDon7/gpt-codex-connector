"""Tests for the data department (CONVENTIONS.md section 9)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, EventLog, Kpi, Message, MessageBus, MockLLM, SimClock,
                  publishes_for, subscribes_for)
from departments.data import workflows
from departments.data.agent import KPIS, DataAgent, build_agent

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLUEPRINT_HEADINGS = ["# Data and Analytics Department Blueprint", "## 1. Mission and scope", "## 2. Org chart",
                      "## 3. Roles", "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces",
                      "## 7. Risks and dependencies", "## 8. Sources"]
KPI_HEADINGS = ["# Data and Analytics KPIs", "## 1. KPI summary", "## 2. Definitions and formulas",
                "## 3. Reporting cadence and data sources", "## 4. Links to company targets"]
ECON_HEADINGS = ["# Data and Analytics Economics", "## 1. Budget", "## 2. Headcount cost build-up",
                 "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md"]


def read_doc(name: str) -> str:
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def make_parts(day: int = 0):
    clock = SimClock()
    clock.advance(day)
    log = EventLog(clock.start)
    bus = MessageBus(clock)
    return clock, log, bus


def make_company() -> Company:
    return Company(use_departments=False, factories={"data": build_agent})


def run_scenario(name: str, ticks: int = 80, **params) -> Company:
    co = make_company()
    co.seed(workflows.SCENARIOS[name](co.bus, co.clock, **params))
    co.run(ticks)
    return co


def table_rows(section: str) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        if line.startswith("|") and not re.match(r"^\|[\s\-|]+\|$", line):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows[1:]  # drop header


def section_of(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


class AgentContractTests(unittest.TestCase):
    def test_build_agent_returns_data_agent(self) -> None:
        clock, log, bus = make_parts()
        agent = build_agent(MockLLM(), bus, clock, log)
        self.assertIsInstance(agent, DataAgent)
        self.assertIsInstance(agent, DepartmentAgent)
        self.assertEqual(agent.name, "data")
        self.assertEqual(agent.department, "data")
        self.assertEqual(agent.role.title, "Chief Data and AI Officer")
        self.assertEqual(agent.role.reports_to, "Chief Executive Officer")
        self.assertEqual(len(bus.agent_names), 0)  # build_agent must not register
        self.assertEqual(len(log), 0)              # and must not publish or log

    def test_topic_lists_equal_map(self) -> None:
        self.assertEqual(DataAgent.SUBSCRIBES, subscribes_for("data"))
        self.assertEqual(DataAgent.PUBLISHES, publishes_for("data"))
        self.assertEqual(len(DataAgent.SUBSCRIBES), 25)

    def test_handle_every_subscribed_topic(self) -> None:
        for topic in subscribes_for("data"):
            with self.subTest(topic=topic):
                clock, log, bus = make_parts()
                agent = build_agent(MockLLM(), bus, clock, log)
                msg = bus.make_message("external", "data", topic, {"summary": "probe"}, sim_time=0)
                out = agent.handle(msg)
                self.assertIsInstance(out, list)
                for m in out:
                    self.assertIsInstance(m, Message)
                    self.assertIn(m.topic, publishes_for("data"))
                self.assertGreaterEqual(len(log.query(department="data")), 1)

    def test_handle_unknown_topic_returns_empty(self) -> None:
        clock, log, bus = make_parts()
        agent = build_agent(MockLLM(), bus, clock, log)
        msg = bus.make_message("sales", "data", "sales.deal_approval_requested", {}, sim_time=0)
        self.assertEqual(agent.handle(msg), [])

    def test_kpis(self) -> None:
        self.assertGreaterEqual(len(KPIS), 8)
        for k in KPIS:
            self.assertIsInstance(k, Kpi)
            self.assertRegex(k.name, r"^[a-z][a-z0-9_]*$")
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))


class MetricTests(unittest.TestCase):
    def test_pipeline_to_cash_metrics(self) -> None:
        co = run_scenario("pipeline_to_cash")
        m = co.agents["data"].metrics()
        self.assertEqual(m["leads_generated"], 1)
        self.assertEqual(m["leads_qualified"], 1)
        self.assertEqual(m["proposals_sent"], 2)
        self.assertEqual(m["open_pipeline_gbp"], 0.0)
        self.assertEqual(m["deals_won"], 1)
        self.assertEqual(m["deals_lost"], 1)
        self.assertEqual(m["win_rate"], 0.5)
        self.assertEqual(m["bookings_gbp"], 90_000.0)       # Forge Pilot, COMPANY.md section 3.2
        self.assertEqual(m["invoiced_gbp"], 27_000.0)       # 30% on signature, COMPANY.md section 7
        self.assertEqual(m["collected_gbp"], 27_000.0)
        self.assertEqual(m["outstanding_receivables_gbp"], 0.0)
        self.assertEqual(m["dso_days"], 30.0)
        self.assertEqual(m["active_engagements"], 0)
        self.assertEqual(m["engagements_completed"], 1)
        self.assertEqual(m["active_clients"], 1)
        self.assertEqual(m["campaign_spend_gbp"], 12_000.0)

    def test_open_pipeline_counts_unresolved_proposals(self) -> None:
        clock, log, bus = make_parts()
        agent = build_agent(MockLLM(), bus, clock, log)
        for i, amt in enumerate((90_000, 260_000), start=1):
            agent.handle(bus.make_message("sales", "*", "sales.proposal_sent",
                                          {"deal_id": f"DL-000{i}", "amount_gbp": amt}, sim_time=0))
        self.assertEqual(agent.metrics()["open_pipeline_gbp"], 350_000.0)
        agent.handle(bus.make_message("sales", "*", "sales.deal_lost", {"deal_id": "DL-0001"}, sim_time=1))
        self.assertEqual(agent.metrics()["open_pipeline_gbp"], 260_000.0)

    def test_keep_arr_renewal_and_churn(self) -> None:
        co = run_scenario("retention_and_agent_governance", ticks=20)
        m = co.agents["data"].metrics()
        self.assertEqual(m["keep_arr_gbp"], 2 * 216_000 - 96_000)  # win + renewal - churn
        self.assertEqual(m["churned_clients"], 1)
        self.assertEqual(m["client_health_avg"], 81.0)

    def test_monthly_cadence_and_forecast(self) -> None:
        co = make_company()
        co.seed(workflows.scenario_month_end_reporting(co.bus, co.clock))
        co.run(40)  # crosses 2026-02-01 (day 27)
        reports = co.log.query(department="data", topic="data.kpi_report_published")
        periods = [e.data["body"]["period"] for e in reports]
        self.assertIn("2026-01", periods)
        self.assertEqual(len(periods), len(set(periods)))            # one report per period
        self.assertTrue(any(e.data["body"]["reason"] == "board_pack" for e in reports))
        forecasts = co.log.query(department="data", topic="data.forecast_updated")
        self.assertGreaterEqual(len(forecasts), 1)
        months = [e.sim_time for e in forecasts]
        self.assertEqual(len(months), len(set(months)))
        self.assertEqual(co.agents["data"].state["recognised_revenue_gbp"], 320_000)

    def test_forecast_uses_planning_win_rate_then_scores_error(self) -> None:
        clock, log, bus = make_parts()
        agent = build_agent(MockLLM(), bus, clock, log)
        agent.handle(bus.make_message("sales", "*", "sales.proposal_sent",
                                      {"deal_id": "DL-0001", "amount_gbp": 100_000}, sim_time=0))
        out = agent._publish_forecast("test")
        self.assertEqual(out[0].body["basis"], "planning")
        self.assertEqual(out[0].body["forecast_bookings_gbp"], 30_000.0)  # 30% planning win rate
        self.assertEqual(out[0].body["low_gbp"], 25_500.0)                # +/- 15% minimum band
        agent.handle(bus.make_message("sales", "*", "sales.deal_won",
                                      {"deal_id": "DL-0001", "client_id": "CL-0001", "amount_gbp": 40_000},
                                      sim_time=10))
        clock.advance(95)
        agent._publish_forecast("test_later")
        self.assertEqual(agent._mape(), 25.0)  # |40000-30000| / 40000

    def test_agent_register_and_quality_report(self) -> None:
        co = run_scenario("retention_and_agent_governance", ticks=20)
        reports = co.log.query(department="data", topic="data.agent_quality_report_published")
        self.assertEqual(len(reports), 1)
        body = reports[0].data["body"]
        self.assertEqual(body["agents_registered"], 1)
        self.assertEqual(body["coverage_pct"], 100.0)
        self.assertEqual(body["outcome"], "approved_with_conditions")

    def test_budget_submitted_matches_company_envelope(self) -> None:
        co = run_scenario("budget_cycle_and_crisis", ticks=35)
        sub = co.log.query(department="data", topic="data.budget_submitted")
        self.assertEqual(len(sub), 1)
        body = sub[0].data["body"]
        self.assertEqual(body["amount_gbp"], 360_000)      # COMPANY.md section 5.4, FY2027
        self.assertEqual(body["headcount_humans"], 3)      # COMPANY.md section 6.1
        self.assertEqual(body["headcount_agents"], 3)

    def test_crisis_triggers_weekly_reports(self) -> None:
        co = run_scenario("budget_cycle_and_crisis", ticks=60)
        reports = co.log.query(department="data", topic="data.kpi_report_published")
        crisis = [e for e in reports if e.data["body"]["period"].startswith("crisis")]
        self.assertGreaterEqual(len(crisis), 3)

    def test_benchmark_published_from_market_data(self) -> None:
        co = run_scenario("inbound_lead_to_win", ticks=3)
        bench = co.log.query(department="data", topic="data.benchmark_ready")
        self.assertEqual(len(bench), 1)
        self.assertEqual(bench[0].data["body"]["min_cohort_size"], 5)

    def test_hire_requests_follow_blueprint(self) -> None:
        clock, log, bus = make_parts(day=451)  # 2027-04-01
        self.assertEqual(clock.date.isoformat(), "2027-04-01")
        agent = build_agent(MockLLM(), bus, clock, log)
        out = agent.tick()
        hires = [m for m in out if m.topic == "data.hire_requested"]
        self.assertEqual([m.body["role"] for m in hires], ["Senior Data Engineer"])
        self.assertEqual(agent.tick() and [m for m in agent.tick() if m.topic == "data.hire_requested"], [])


class DataQualityTests(unittest.TestCase):
    def test_defects_raise_issues_and_hide_contact_details(self) -> None:
        co = run_scenario("data_quality_defects", ticks=5)
        issues = co.log.query(department="data", topic="data.data_quality_issue_raised")
        checks = sorted(e.data["body"]["check"] for e in issues)
        self.assertIn("completeness", checks)
        self.assertIn("validity", checks)
        self.assertIn("uniqueness", checks)
        for e in issues:
            self.assertIn(e.data["body"]["severity"], ("low", "medium", "high", "critical"))
            self.assertGreater(e.data["body"]["due_day"], e.sim_time - 1)
        self.assertNotIn("buyer@example.invalid", co.log.to_jsonl())
        agent = co.agents["data"]
        self.assertGreaterEqual(agent.state["pii_fields_redacted"], 1)
        self.assertLess(agent._dq_pass_rate(), 100.0)
        # the duplicate invoice must not double count billings
        self.assertEqual(agent.metrics()["invoiced_gbp"], 36_000.0)

    def test_repeat_defects_suppressed_within_month(self) -> None:
        clock, log, bus = make_parts()
        agent = build_agent(MockLLM(), bus, clock, log)
        for i in range(5):
            agent.handle(bus.make_message("sales", "*", "sales.deal_won",
                                          {"deal_id": f"DL-{i}", "amount_gbp": 10}, sim_time=0))
        self.assertEqual(agent.state["issues_raised"], 1)
        self.assertEqual(agent.state["issues_suppressed"], 4)

    def test_clean_events_pass(self) -> None:
        co = run_scenario("pipeline_to_cash")
        self.assertEqual(co.log.query(department="data", topic="data.data_quality_issue_raised"), [])
        self.assertEqual(co.agents["data"]._dq_pass_rate(), 100.0)


class ScenarioTests(unittest.TestCase):
    def test_scenarios_registered(self) -> None:
        self.assertGreaterEqual(len(workflows.SCENARIOS), 3)
        for name, fn in workflows.SCENARIOS.items():
            self.assertEqual(fn.__name__, f"scenario_{name}")

    def test_scenarios_build_valid_messages(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                clock, _, bus = make_parts()
                msgs = fn(bus, clock)
                self.assertTrue(msgs)
                for m in msgs:
                    self.assertIsInstance(m, Message)
                    self.assertIsInstance(m.body, dict)
                    self.assertIsInstance(m.sim_time, int)

    def test_every_subscribed_topic_is_seeded_by_some_scenario(self) -> None:
        clock, _, bus = make_parts()
        seeded = {m.topic for fn in workflows.SCENARIOS.values() for m in fn(bus, clock)}
        self.assertEqual(set(subscribes_for("data")) - seeded, set())

    def test_scenarios_run_and_log_data_events(self) -> None:
        for name in workflows.SCENARIOS:
            with self.subTest(scenario=name):
                co = run_scenario(name, ticks=75)
                self.assertGreaterEqual(len(co.log.query(department="data")), 1)

    def test_one_scenario_starts_from_a_subscribed_topic_and_one_is_a_chain(self) -> None:
        clock, _, bus = make_parts()
        first = {m.topic for m in workflows.scenario_pipeline_to_cash(bus, clock)}
        self.assertTrue(first & set(subscribes_for("data")))
        chain = [m.topic for m in workflows.scenario_inbound_lead_to_win(bus, clock)]
        self.assertIn("external.lead_inbound", chain)

    def test_determinism(self) -> None:
        for name in workflows.SCENARIOS:
            with self.subTest(scenario=name):
                a = run_scenario(name, ticks=60).log.to_jsonl()
                b = run_scenario(name, ticks=60).log.to_jsonl()
                self.assertEqual(a, b)


class DocumentTests(unittest.TestCase):
    def assert_headings(self, doc: str, headings: list[str]) -> None:
        text = read_doc(doc)
        pos = -1
        for h in headings:
            m = re.search(rf"^{re.escape(h)}\s*$", text, re.M)
            self.assertIsNotNone(m, f"{doc}: missing heading {h!r}")
            self.assertGreater(m.start(), pos, f"{doc}: heading out of order {h!r}")
            pos = m.start()

    def test_blueprint_headings(self) -> None:
        self.assert_headings("blueprint.md", BLUEPRINT_HEADINGS)

    def test_kpis_headings(self) -> None:
        self.assert_headings("kpis.md", KPI_HEADINGS)

    def test_economics_headings(self) -> None:
        self.assert_headings("economics.md", ECON_HEADINGS)

    def test_sops_structure(self) -> None:
        text = read_doc("sops.md")
        self.assertTrue(text.startswith("# Data and Analytics Standard Operating Procedures"))
        self.assertRegex(text, r"(?m)^## Overview\s*$")
        sops = re.findall(r"(?m)^## (SOP-DATA-\d\d): ", text)
        self.assertGreaterEqual(len(sops), 8)
        self.assertEqual(sops, sorted(set(sops)))
        blocks = re.split(r"(?m)^## SOP-DATA-\d\d: ", text)[1:]
        for sid, block in zip(sops, blocks):
            for h in ("### Steps", "### Outputs and messages", "### SLA and controls",
                      "### Exceptions and escalation", "**Owner**", "**Trigger**", "**Inputs**"):
                self.assertIn(h, block, f"{sid} missing {h}")
            self.assertRegex(block, r"\[human\]")
            self.assertRegex(block, r"\[agent\]")

    def test_sops_cover_every_topic(self) -> None:
        text = read_doc("sops.md")
        blocks = re.split(r"(?m)^## SOP-DATA-\d\d: ", text)[1:]
        triggers = " ".join(re.search(r"\*\*Trigger\*\*[^\n]*", b).group(0) for b in blocks)
        for topic in subscribes_for("data"):
            self.assertIn(topic, triggers, f"{topic} is not the trigger of any SOP")
        outputs = " ".join(b.split("### Outputs and messages", 1)[1].split("### SLA", 1)[0] for b in blocks)
        for topic in publishes_for("data"):
            self.assertIn(topic, outputs, f"{topic} is not in any SOP output")

    def test_no_placeholders(self) -> None:
        for doc in ("blueprint.md", "sops.md", "kpis.md", "economics.md"):
            text = read_doc(doc)
            for bad in ("TBD", "lorem", "TODO", "XXX"):
                self.assertNotIn(bad, text, f"{doc} contains {bad}")

    def test_kpi_table_matches_agent(self) -> None:
        rows = table_rows(section_of(read_doc("kpis.md"), "## 1. KPI summary", "## 2."))
        rows = [r for r in rows if r and re.match(r"^[a-z][a-z0-9_]*$", r[0])]
        self.assertGreaterEqual(len(rows), 8)
        doc = {r[0]: float(r[3].replace(",", "")) for r in rows}
        direction = {r[0]: r[6].lower().startswith("higher") for r in rows}
        self.assertEqual(set(doc), {k.name for k in KPIS})
        for k in KPIS:
            self.assertEqual(doc[k.name], k.target, k.name)
            self.assertEqual(direction[k.name], k.higher_is_better, k.name)

    def test_blueprint_headcount_matches_company(self) -> None:
        text = read_doc("blueprint.md")
        roles = [r for r in table_rows(section_of(text, "## 3. Roles", "## 4."))
                 if r[0] and not r[0].startswith("**")]
        sums = [sum(int(r[i]) for r in roles) for i in (3, 4, 5)]
        self.assertEqual(sums, [1, 3, 9])                      # COMPANY.md section 6.1
        bands = {"head": (140000, 200000), "principal": (120000, 155000), "manager": (92000, 115000),
                 "senior_consultant": (72000, 90000), "consultant": (55000, 70000)}
        for r in roles:
            lo, hi = (int(x.replace(",", "")) for x in re.findall(r"[\d,]{6,}", r[6])[:2])
            self.assertEqual((lo, hi), bands[r[1]], r[0])
        agents = [r for r in table_rows(section_of(text, "## 4. AI agents", "## 5."))
                  if r[0] and not r[0].startswith("**")]
        self.assertEqual([sum(int(r[i]) for r in agents) for i in (4, 5, 6)], [1, 3, 7])

    def test_blueprint_org_chart_lists_every_role(self) -> None:
        text = read_doc("blueprint.md")
        chart = section_of(text, "## 2. Org chart", "## 3.")
        roles = [r[0] for r in table_rows(section_of(text, "## 3. Roles", "## 4.")) if not r[0].startswith("**")]
        for role in roles:
            self.assertIn(role, chart)

    def test_economics_reconciles_to_company_envelope(self) -> None:
        text = read_doc("economics.md")
        rows = {r[0]: r[1:] for r in table_rows(section_of(text, "## 1. Budget", "## 2."))}
        total = [int(x.replace(",", "")) for x in rows["**Department total**"]]
        self.assertEqual(total, [140, 360, 1410])               # COMPANY.md section 5.4
        non_people = [int(x.replace(",", "")) for x in rows["**Non-people total**"]]
        people = [int(x.replace(",", "")) for x in rows["People (humans, loaded)"]]
        self.assertEqual(non_people, [50, 110, 410])
        self.assertEqual(people, [90, 250, 1000])
        lines = [v for k, v in rows.items() if k.startswith("Non-people:")]
        for col in range(3):
            self.assertEqual(sum(int(v[col].replace(",", "")) for v in lines), non_people[col])

    def test_economics_cost_build_up_matches_budget(self) -> None:
        text = read_doc("economics.md")
        build = section_of(text, "## 2. Headcount cost build-up", "## 3.")
        for year, expected in (("FY2026", 90), ("FY2027", 250), ("FY2028", 1000)):
            block = build.split(f"### {year}", 1)[1].split("###", 1)[0]
            roles = [r for r in table_rows(block) if r[0] and not r[0].startswith("**")]
            cost = sum(float(r[4]) for r in roles)
            self.assertLessEqual(abs(cost - expected), 5, year)
            for r in roles:
                base, loaded = int(r[1].replace(",", "")), int(r[2].replace(",", ""))
                self.assertAlmostEqual(base * 1.28, loaded, delta=1)   # COMPANY.md section 5.2


if __name__ == "__main__":
    unittest.main()
