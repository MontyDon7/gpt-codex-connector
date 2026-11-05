"""Tests for the data department (CONVENTIONS.md section 9)."""

from __future__ import annotations

import os
import re
import unittest
from datetime import date

from core import (TOPIC_SUBSCRIBERS, Company, DepartmentAgent, EventLog, Kpi, Message, MessageBus, MockLLM, SimClock,
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


def by_id(events, key: str) -> list:
    """One event per logical document (an emit is addressed once per subscriber department)."""
    seen, out = set(), []
    for e in events:
        k = e.data["body"][key]
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out


def at_date(d: date, **kw):
    """Agent whose clock stands on calendar date d."""
    clock, log, bus = make_parts()
    clock.advance(clock.day_of(d))
    return clock, log, bus, build_agent(MockLLM(), bus, clock, log)


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
        reports = by_id(co.log.query(department="data", topic="data.kpi_report_published"), "report_id")
        periods = [e.data["body"]["period"] for e in reports]
        self.assertIn("2026-01", periods)
        self.assertEqual(len(periods), len(set(periods)))            # one report per period
        self.assertTrue(any(e.data["body"]["reason"] == "board_pack" for e in reports))
        forecasts = by_id(co.log.query(department="data", topic="data.forecast_updated"), "forecast_id")
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
        self.assertEqual(len(by_id(reports, "report_id")), 1)
        self.assertEqual(len(reports), len(TOPIC_SUBSCRIBERS["data.agent_quality_report_published"]))
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
        crisis = by_id([e for e in reports if e.data["body"]["period"].startswith("crisis")], "report_id")
        self.assertGreaterEqual(len(crisis), 3)

    def test_benchmark_published_from_market_data(self) -> None:
        co = run_scenario("inbound_lead_to_win", ticks=3)
        bench = co.log.query(department="data", topic="data.benchmark_ready")
        self.assertEqual(len(by_id(bench, "benchmark_id")), 1)
        self.assertEqual(bench[0].data["body"]["min_cohort_size"], 5)

    def test_hire_requests_follow_blueprint(self) -> None:
        clock, log, bus = make_parts(day=451)  # 2027-04-01
        self.assertEqual(clock.date.isoformat(), "2027-04-01")
        agent = build_agent(MockLLM(), bus, clock, log)
        out = agent.tick()
        hires = [m for m in out if m.topic == "data.hire_requested"]
        self.assertEqual([m.body["role"] for m in hires], ["Senior Data Engineer"])
        self.assertEqual([m for m in agent.tick() if m.topic == "data.hire_requested"], [])


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


class DivergenceFixTests(unittest.TestCase):
    """Behaviour that sops.md and kpis.md define and the agent must follow."""

    def feed(self, agent, bus, topic, body, sim_time=0):
        return agent.handle(bus.make_message("external", "data", topic, body, sim_time=sim_time))

    def test_working_day_helper_counts_weekdays_only(self) -> None:
        wd = DataAgent._working_days_in_month_to
        self.assertEqual(wd(date(2026, 2, 1)), 0)    # Sunday
        self.assertEqual(wd(date(2026, 2, 3)), 2)    # Tuesday
        self.assertEqual(wd(date(2026, 2, 6)), 5)
        self.assertEqual(DataAgent._deadline_of_period("2026-01"), date(2026, 2, 4))  # WD3 of February
        self.assertEqual(DataAgent._deadline_of_period("2026-12"), date(2027, 1, 5))

    def test_report_on_time_and_late_by_working_day_3(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 2, 4))   # Wednesday, working day 3
        agent._publish_kpi_report("2026-01", "month_end_closed")
        self.assertEqual((agent.state["monthly_reports_published"], agent.state["reports_on_time"]), (1, 1))
        agent2 = at_date(date(2026, 2, 5))[3]                 # Thursday, working day 4
        agent2._publish_kpi_report("2026-01", "month_end_closed")
        self.assertEqual(agent2.state["reports_on_time"], 0)
        self.assertEqual(agent2.state["late_reports"], 1)
        self.assertEqual(agent2.kpi_actuals()[0].actual, 0.0)
        self.assertTrue(any("Late KPI report" in t.title for t in agent2.tasks.values()))
        self.assertTrue(agent2.state["report_turnaround_breach"])

    def test_board_and_crisis_reports_do_not_count_toward_on_time(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 2, 20))
        agent._publish_kpi_report("board-day-1", "board_pack")
        self.assertEqual(agent.state["monthly_reports_published"], 0)
        self.assertIsNone(agent.kpi_actuals()[0].actual)

    def test_coarse_clock_skipping_month_start_is_measured_late(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 1, 28))
        self.feed(agent, bus, "marketing.lead_generated", {"lead_id": "LD-1"})
        clock.advance_days(9)                                 # Thursday 2026-02-06, WD5
        self.assertFalse(clock.is_month_start)
        out = agent.tick()
        self.assertEqual({m.topic for m in out} & {"data.kpi_report_published"}, {"data.kpi_report_published"})
        self.assertEqual(agent.state["late_reports"], 1)

    def test_tick_on_first_working_days_is_on_time(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 1, 28))
        self.feed(agent, bus, "marketing.lead_generated", {"lead_id": "LD-1"})
        clock.advance_days(5)                                 # Monday 2026-02-02, WD1
        agent.tick()
        self.assertEqual((agent.state["reports_on_time"], agent.state["late_reports"]), (1, 0))

    def test_emits_are_addressed_to_topic_subscribers(self) -> None:
        for name in ("pipeline_to_cash", "data_quality_defects", "month_end_reporting",
                     "retention_and_agent_governance", "budget_cycle_and_crisis", "inbound_lead_to_win"):
            co = run_scenario(name, ticks=75)
            for e in co.log.query(department="data"):
                if e.data.get("kind") != "emit":
                    continue
                self.assertNotEqual(e.data["recipient"], "*", e.topic)
                self.assertIn(e.data["recipient"], TOPIC_SUBSCRIBERS[e.topic], e.topic)

    def test_each_subscriber_gets_exactly_one_copy(self) -> None:
        co = run_scenario("budget_cycle_and_crisis", ticks=35)
        for topic in ("data.budget_submitted",):
            got = [e.data["recipient"] for e in co.log.query(department="data", topic=topic)]
            self.assertEqual(sorted(got), sorted(TOPIC_SUBSCRIBERS[topic]))
        co = run_scenario("data_quality_defects", ticks=5)
        got = [e.data["recipient"] for e in co.log.query(department="data", topic="data.data_quality_issue_raised")]
        for r in TOPIC_SUBSCRIBERS["data.data_quality_issue_raised"]:
            self.assertIn(r, got)

    def test_forecast_includes_revenue_and_capacity(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 3, 2))
        self.feed(agent, bus, "sales.proposal_sent", {"deal_id": "DL-1", "amount_gbp": 100_000})
        self.feed(agent, bus, "sales.deal_won", {"deal_id": "DL-9", "client_id": "CL-9", "amount_gbp": 216_000,
                                                 "service_line": "keep", "annual_value_gbp": 365_000})
        self.feed(agent, bus, "delivery.engagement_kickoff", {"engagement_id": "EN-1", "client_id": "CL-9"})
        self.feed(agent, bus, "finance.invoice_issued", {"invoice_id": "INV-1", "amount_gbp": 10_000})
        out = agent._publish_forecast("test")
        self.assertEqual({m.recipient for m in out}, set(TOPIC_SUBSCRIBERS["data.forecast_updated"]))
        b = out[0].body
        self.assertEqual(b["forecast_bookings_gbp"], 30_000.0)
        self.assertEqual(b["keep_revenue_gbp"], 90_000.0)                # 365,000 x 90 / 365
        self.assertEqual(b["project_revenue_gbp"], 12_000.0)             # 40% of forecast bookings
        self.assertEqual(b["forecast_revenue_gbp"], 102_000.0)
        self.assertEqual(b["forecast_revenue_low_gbp"], round(102_000 * 0.85, 2))
        self.assertEqual(b["forecast_cash_inflow_gbp"], 10_000.0)
        self.assertEqual(b["expected_new_engagements"], 0.3)
        self.assertEqual(b["capacity_demand_fte"], round((1 + 0.3) * 3.0, 2))
        self.assertEqual(b["capacity_required_headcount"], round(round(1.3 * 3.0, 2) / 0.70, 2))

    def test_out_of_cycle_hire_blocked_in_fy2026_by_headcount_plan(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 3, 2))
        for i in range(12):
            agent.state["feed_topics"].append(f"x.topic{i}")
        self.assertEqual(agent._out_of_cycle_hires(), [])
        self.assertEqual(agent.state["hire_slots_requested"], [])
        self.assertTrue(log.query(department="data", topic="data.activity.hire_blocked_by_plan"))

    def test_out_of_cycle_hire_on_feed_count_in_fy2027(self) -> None:
        clock, log, bus, agent = at_date(date(2027, 2, 1))        # FY2027 Q1: planned request is Q2
        for i in range(11):
            agent.state["feed_topics"].append(f"x.topic{i}")
        out = agent._out_of_cycle_hires()
        self.assertEqual({m.recipient for m in out}, {"people"})
        body = out[0].body
        self.assertEqual((body["role"], body["start_quarter"], body["out_of_cycle"]),
                         ("Senior Data Engineer", "FY2027 Q2", True))
        self.assertEqual(agent._out_of_cycle_hires(), [])         # not requested twice
        clock.advance(60)                                         # the calendar request is skipped for the slot
        quarterly = [m for m in agent._quarterly_cadence() if m.topic == "data.hire_requested"]
        self.assertEqual([m.body["role"] for m in quarterly], [])
        self.assertTrue(any("CEO approval" in t.title for t in agent.tasks.values()))

    def test_out_of_cycle_hire_on_dq_pass_rate_two_months(self) -> None:
        clock, log, bus, agent = at_date(date(2027, 2, 1))
        agent.state.update(checks_run=100, checks_failed=10)      # 90% pass rate
        agent._update_dq_streak()
        self.assertEqual(agent._out_of_cycle_hires(), [])
        agent._update_dq_streak()
        out = agent._out_of_cycle_hires()
        self.assertEqual([m.body["role"] for m in out], ["Senior Data Engineer"])

    def test_out_of_cycle_hire_on_report_turnaround_and_headcount_cap(self) -> None:
        clock, log, bus, agent = at_date(date(2027, 2, 1))
        agent.state["report_turnaround_breach"] = True
        agent.state["feed_topics"].extend(f"x.t{i}" for i in range(11))
        roles = [m.body["role"] for m in agent._out_of_cycle_hires()]
        self.assertEqual(roles, ["Senior Data Engineer", "BI and Analytics Analyst"])  # 1 + 2 = 3 humans
        self.assertEqual(len(agent.state["hire_slots_requested"]), 2)
        # FY2027 plan holds 3 humans: nothing further can be requested for FY2027 starts
        self.assertEqual(agent._out_of_cycle_hires(), [])

    def test_health_score_range_check(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 3, 2))
        out = self.feed(agent, bus, "customer_success.health_score_updated", {"client_id": "CL-1", "score": 140})
        self.assertEqual({m.topic for m in out}, {"data.data_quality_issue_raised"})
        self.assertIn("out of range", out[0].body["summary"])
        self.assertNotIn("CL-1", agent.state["health"])
        self.assertEqual(agent.state["health_out_of_range"], 1)
        clock.advance(1)
        self.feed(agent, bus, "customer_success.health_score_updated", {"client_id": "CL-2", "score": -3})
        self.assertNotIn("CL-2", agent.state["health"])
        self.assertEqual(self.feed(agent, bus, "customer_success.health_score_updated",
                                   {"client_id": "CL-3", "score": 0}), [])
        self.assertEqual(agent.state["health"]["CL-3"], 0.0)
        out = self.feed(agent, bus, "customer_success.health_score_updated", {"client_id": "CL-4", "score": "bad"})
        self.assertIn("not a number", out[0].body["summary"])
        self.assertNotIn("CL-4", agent.state["health"])

    def test_crisis_ends_when_task_closed(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 3, 2))
        self.feed(agent, bus, "executive.crisis_declared", {"severity": "high"}, sim_time=clock.day)
        self.assertTrue(agent.state["crisis_mode"])
        tid = agent.state["crisis_task_id"]
        self.assertEqual(agent.tasks[tid].priority, "critical")
        clock.advance(7)
        self.assertTrue(any(m.body["reason"] == "crisis_weekly" for m in agent.tick()))
        agent.update_task(tid, "done")
        clock.advance(1)
        out = agent.tick()
        self.assertFalse(agent.state["crisis_mode"])
        self.assertEqual([m.body["reason"] for m in out if m.recipient == "executive"], ["crisis_closed"])
        clock.advance(6)
        self.assertEqual([m for m in agent.tick() if m.body.get("reason") == "crisis_weekly"], [])
        self.assertTrue(log.query(department="data", topic="data.activity.crisis_closed"))

    def test_crisis_times_out(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 3, 2))
        self.feed(agent, bus, "executive.crisis_declared", {}, sim_time=clock.day)
        clock.advance(89)
        agent.tick()
        self.assertTrue(agent.state["crisis_mode"])
        clock.advance(1)
        agent.tick()
        self.assertFalse(agent.state["crisis_mode"])
        self.assertTrue(any("timed out" in t.title for t in agent.tasks.values()))
        # a redeclaration opens a new crisis and a new task
        self.feed(agent, bus, "executive.crisis_declared", {}, sim_time=clock.day)
        self.assertTrue(agent.state["crisis_mode"])

    def test_quarterly_agent_report_with_empty_register(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 4, 1))
        out = agent.tick()
        reports = [m for m in out if m.topic == "data.agent_quality_report_published"]
        self.assertEqual({m.recipient for m in reports}, set(TOPIC_SUBSCRIBERS["data.agent_quality_report_published"]))
        self.assertEqual(reports[0].body["agents_registered"], 0)
        self.assertIsNone(reports[0].body["coverage_pct"])
        self.assertEqual(len(agent.tasks), 2)

    def test_quarter_cadence_follows_fiscal_year_start(self) -> None:
        from departments.data import agent as mod
        clock, log, bus, agent = at_date(date(2026, 4, 1))
        self.assertEqual(agent._fiscal_quarter_of(date(2026, 4, 1)), 2)
        original = mod.FISCAL_YEAR_START_MONTH
        mod.FISCAL_YEAR_START_MONTH = 4                  # fiscal year starting in April
        try:
            self.assertEqual(agent._fiscal_quarter_of(date(2026, 4, 1)), 1)
            self.assertEqual(agent._fiscal_quarter_of(date(2027, 1, 20)), 4)
            self.assertEqual(agent._fiscal_year_of(date(2027, 1, 20)), 2026)
            self.assertEqual(agent._fiscal_quarter_start(), date(2026, 4, 1))
            clock.advance_days(15)
            self.assertEqual(agent._fiscal_quarter_start(), date(2026, 4, 1))
            c2, l2, b2, a2 = at_date(date(2026, 5, 1))
            self.assertEqual(a2.tick(), [])             # May is not a quarter start for an April fiscal year
            self.assertEqual(len(a2.tasks), 0)
            c3, l3, b3, a3 = at_date(date(2026, 4, 1))
            a3.tick()
            self.assertEqual(len(a3.tasks), 2)
            c4, l4, b4, a4 = at_date(date(2026, 7, 1))
            a4.tick()
            self.assertEqual(len(a4.tasks), 2)
            c5, l5, b5, a5 = at_date(date(2026, 1, 5))
            self.assertEqual(a5.tick(), [])             # January is mid-year here
            self.assertEqual(len(a5.tasks), 0)
        finally:
            mod.FISCAL_YEAR_START_MONTH = original

    def test_quarterly_runs_once_per_quarter_and_catches_missed_start(self) -> None:
        clock, log, bus, agent = at_date(date(2026, 3, 30))
        agent.tick()
        clock.advance_days(5)                              # 2026-04-04: coarse clock skipped April 1
        agent.tick()
        self.assertEqual(len(agent.tasks), 2)
        clock.advance_days(1)
        agent.tick()
        self.assertEqual(len(agent.tasks), 2)


if __name__ == "__main__":
    unittest.main()
