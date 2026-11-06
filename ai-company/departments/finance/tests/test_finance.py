"""Contract and behaviour tests for the finance department (agent, workflows, docs, budget)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from core.events import EventLog
from departments.finance import agent as agent_module
from departments.finance import workflows
from departments.finance.agent import KPIS, FinanceAgent, build_agent

DEPT = "finance"
HERE = os.path.dirname(os.path.abspath(__file__))
DEPT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))

# COMPANY.md §5.4 finance row (GBP k): people, non-people, total for FY2026..FY2028
BUDGET_PEOPLE = (210, 480, 800)
BUDGET_NON_PEOPLE = (100, 250, 700)
BUDGET_TOTAL = (310, 730, 1500)
HEADCOUNT = (2, 5, 10)  # COMPANY.md §6.1 humans, year-end

DOC_HEADINGS = {
    "blueprint.md": [
        "# Finance Department Blueprint", "## 1. Mission and scope", "## 2. Org chart", "## 3. Roles",
        "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies",
        "## 8. Sources",
    ],
    "sops.md": ["# Finance Standard Operating Procedures", "## Overview"],
    "kpis.md": [
        "# Finance KPIs", "## 1. KPI summary", "## 2. Definitions and formulas",
        "## 3. Reporting cadence and data sources", "## 4. Links to company targets",
    ],
    "economics.md": [
        "# Finance Economics", "## 1. Budget", "## 2. Headcount cost build-up",
        "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md",
    ],
}


def read_doc(name: str) -> str:
    path = os.path.join(DEPT_DIR, name)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def make_env():
    """Fresh (company, agent) with only finance live (other departments are stubs)."""
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
        "invoice_id": "INV-2026-0001", "amount_gbp": 60000, "service_line": "forge",
        "tier": "forge_build", "department": "sales", "summary": f"test {topic}", "due_day": 30,
        "discount_pct": 5, "milestone": "M1", "year": 2026, "period": "2026-10",
        "budget_cycle_id": "BUD-2026",
    }


def external_sender(topic: str) -> str:
    return "external" if topic.startswith("external.") else topic.split(".", 1)[0]


class ContractTests(unittest.TestCase):
    def test_class_name(self) -> None:
        self.assertEqual(class_name_for(DEPT), "FinanceAgent")
        self.assertTrue(issubclass(FinanceAgent, DepartmentAgent))

    def test_build_agent(self) -> None:
        agent, bus, _, _ = standalone_agent()
        self.assertIsInstance(agent, FinanceAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)
        self.assertEqual(bus.agent_names, [], "build_agent must not register with the bus")
        self.assertEqual(len(bus.pending), 0, "build_agent must not publish")

    def test_topic_map(self) -> None:
        self.assertEqual(tuple(FinanceAgent.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(FinanceAgent.PUBLISHES), publishes_for(DEPT))
        self.assertGreater(len(FinanceAgent.SUBSCRIBES), 0)
        self.assertGreater(len(FinanceAgent.PUBLISHES), 0)

    def test_kpis(self) -> None:
        self.assertGreaterEqual(len(KPIS), 8)
        self.assertTrue(all(isinstance(k, Kpi) for k in KPIS))
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))
        for expected in ("dso_days", "month_end_close_days", "forecast_accuracy_pct", "gross_margin_pct"):
            self.assertIn(expected, names)

    def test_kpis_match_doc_targets(self) -> None:
        kpi_doc = read_doc("kpis.md")
        for k in KPIS:
            self.assertIn(f"| {k.name} |", kpi_doc, f"{k.name} missing from kpis.md")
            row = next(r for r in kpi_doc.splitlines() if r.startswith(f"| {k.name} |"))
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertAlmostEqual(float(cells[3]), float(k.target), places=6, msg=k.name)

    def test_kpi_direction_of_known_kpis(self) -> None:
        by_name = {k.name: k for k in KPIS}
        self.assertFalse(by_name["dso_days"].higher_is_better)
        self.assertFalse(by_name["month_end_close_days"].higher_is_better)
        self.assertTrue(by_name["forecast_accuracy_pct"].higher_is_better)

    def test_role(self) -> None:
        agent, _, _, _ = standalone_agent()
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(agent.role.level, "head")


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
                    self.assertTrue(m.topic.startswith("finance."))

    def test_handle_tolerates_empty_body(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                msg = bus.make_message(external_sender(topic), DEPT, topic, {}, sim_time=0)
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

    def test_tick_runs_over_a_year_without_error(self) -> None:
        company, agent = make_env()
        company.run(370)
        for m in agent.tick() or []:
            self.assertIn(m.topic, agent.PUBLISHES)
        self.assertGreater(len(company.log.query(department=DEPT)), 0)


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
                bus = MessageBus(clock)
                msgs = fn(bus, clock)
                self.assertIsInstance(msgs, list)
                self.assertGreater(len(msgs), 0)
                ids = [m.id for m in msgs]
                self.assertEqual(len(ids), len(set(ids)))
                for m in msgs:
                    self.assertIsInstance(m, Message)
                    self.assertIsInstance(m.body, dict)
                    self.assertIsInstance(m.sim_time, int)
                    self.assertGreaterEqual(m.sim_time, clock.day)

    def test_some_scenario_starts_from_subscribed_topic(self) -> None:
        subs = set(subscribes_for(DEPT))
        for name, fn in workflows.SCENARIOS.items():
            clock = SimClock()
            msgs = fn(MessageBus(clock), clock)
            self.assertTrue(any(m.topic in subs for m in msgs), name)

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

    def test_every_scenario_runs_with_all_departments_if_present(self) -> None:
        """Auto-discovery run (stubs fill gaps); finance must not break other agents' handling."""
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company = Company(MockLLM(), factories={DEPT: build_agent}, strict=False)
                company.seed(fn(company.bus, company.clock))
                company.run(45)
                finance_errors = [e for e in company.log.query(topic="system.agent_error")
                                  if e.department == DEPT]
                self.assertEqual(finance_errors, [])

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
            fn(MessageBus(clock), clock)  # must not require params


class BehaviourTests(unittest.TestCase):
    """Key lifecycle behaviours: the right finance topics are emitted for the right triggers."""

    def _run(self, topic: str, body: dict, days: int = 45, sender: str | None = None):
        company, agent = make_env()
        company.inject(topic, body, recipient=DEPT, sender=sender or external_sender(topic))
        company.run(days)
        return company, agent

    def _emitted(self, company: Company) -> list:
        return [e for e in company.log.query(department=DEPT) if e.data.get("kind") == "emit"]

    def _emitted_topics(self, company: Company) -> set[str]:
        return {e.topic for e in self._emitted(company)}

    def test_client_payment_emits_payment_received(self) -> None:
        body = {"client_id": "CL-0007", "client_name": "Calder Freight Group",
                "invoice_id": "INV-2026-0001", "amount_gbp": 60000}
        company, _ = self._run("external.client_payment_received", body)
        self.assertIn("finance.payment_received", self._emitted_topics(company))

    def test_milestone_reached_emits_invoice(self) -> None:
        body = {"client_id": "CL-0007", "client_name": "Calder Freight Group",
                "engagement_id": "EN-0001", "amount_gbp": 60000, "milestone": "M1"}
        company, _ = self._run("delivery.milestone_reached", body)
        self.assertIn("finance.invoice_issued", self._emitted_topics(company))

    def test_contract_signed_creates_billing_schedule(self) -> None:
        body = {"client_id": "CL-0007", "client_name": "Calder Freight Group", "contract_id": "CT-0001",
                "amount_gbp": 260000, "service_line": "forge", "tier": "forge_build"}
        company, _ = self._run("legal.contract_signed", body)
        self.assertIn("finance.billing_schedule_created", self._emitted_topics(company))

    def test_deal_approval_request_gets_pricing_check(self) -> None:
        body = {"deal_id": "DL-0001", "client_id": "CL-0007", "client_name": "Calder Freight Group",
                "amount_gbp": 260000, "tier": "forge_build", "service_line": "forge", "discount_pct": 25}
        company, _ = self._run("sales.deal_approval_requested", body)
        self.assertIn("finance.pricing_check_completed", self._emitted_topics(company))

    def test_pricing_check_carries_deal_id(self) -> None:
        body = {"deal_id": "DL-0042", "client_id": "CL-0007", "amount_gbp": 260000,
                "tier": "forge_build", "service_line": "forge", "discount_pct": 5}
        company, _ = self._run("sales.deal_approval_requested", body)
        checks = [e for e in self._emitted(company) if e.topic == "finance.pricing_check_completed"]
        self.assertTrue(checks)
        self.assertTrue(any(e.data["body"].get("deal_id") == "DL-0042" for e in checks))

    def test_budget_submissions_lead_to_consolidation_or_log(self) -> None:
        company, agent = make_env()
        company.inject("finance.budget_cycle_opened", {"budget_cycle_id": "BUD-2027", "year": 2027},
                       sender="finance")
        for dept in ("sales", "marketing", "delivery", "people", "legal", "it_security", "operations",
                     "customer_success", "product", "data", "executive"):
            company.inject(f"{dept}.budget_submitted",
                           {"department": dept, "amount_gbp": 100000, "budget_cycle_id": "BUD-2027"},
                           sender=dept)
        company.run(60)
        topics = self._emitted_topics(company)
        self.assertTrue(topics, "finance should emit something while running a budget cycle")
        self.assertIn("finance.budget_consolidated", topics)

    def test_requisition_budget_check_never_emits_hire_requested(self) -> None:
        """Regression: replying to people.requisition_opened with finance.hire_requested made People open another
        requisition for every check (about 1,000 requisitions in two simulated years)."""
        body = {"requisition_id": "REQ-0001", "department": "delivery", "role": "Consultant",
                "salary_gbp": 62000}
        company, _ = self._run("people.requisition_opened", body, sender="people")
        self.assertGreater(len(company.log.query(department=DEPT)), 0)
        self.assertNotIn("finance.hire_requested", self._emitted_topics(company))
        self.assertNotIn("finance.budget_variance_flagged", self._emitted_topics(company))   # within plan

    def test_over_plan_requisition_is_flagged_once_as_a_budget_variance(self) -> None:
        plan = agent_module.HEADCOUNT_PLAN["delivery"][0]
        company, agent = make_env()
        for i in range(plan + 3):
            company.inject("people.requisition_opened", {"requisition_id": f"REQ-{i:04d}", "department": "delivery",
                                                         "role": "Consultant", "salary_gbp": 62000}, recipient=DEPT, sender="people")
        company.run(10)
        flags = [m for m in company.bus.history if m.topic == "finance.budget_variance_flagged"
                 and m.body.get("category") == "people"]
        self.assertEqual(len(flags), 1, "flagged once per department and year, not once per requisition")
        self.assertEqual(flags[0].body["year_end_plan"], plan)
        self.assertNotIn("finance.hire_requested", self._emitted_topics(company))

    def test_all_emitted_topics_are_published_topics(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company, _ = make_env()
                company.seed(fn(company.bus, company.clock))
                company.run(60)
                for e in self._emitted(company):
                    self.assertIn(e.topic, publishes_for(DEPT))

    def test_overdue_invoice_flow_reachable_in_a_scenario(self) -> None:
        """At least one scenario drives the receivables chain (invoice -> overdue -> collections)."""
        chain = {"finance.invoice_issued", "finance.invoice_overdue", "finance.collections_escalated"}
        seen: set[str] = set()
        for fn in workflows.SCENARIOS.values():
            company, _ = make_env()
            company.seed(fn(company.bus, company.clock))
            company.run(120)
            seen |= self._emitted_topics(company)
        self.assertTrue(seen & chain, f"no receivables topics emitted; saw {sorted(seen)}")

    def test_month_end_close_cadence(self) -> None:
        company, _ = make_env()
        company.run(100)
        topics = self._emitted_topics(company)
        self.assertIn("finance.month_end_closed", topics)

    def test_state_is_updated(self) -> None:
        body = {"client_id": "CL-0007", "client_name": "Calder Freight Group",
                "invoice_id": "INV-2026-0001", "amount_gbp": 60000}
        _, agent = self._run("external.client_payment_received", body)
        self.assertTrue(agent.state, "agent should record state after handling a payment")

    def test_no_wall_clock_or_uuid_in_sources(self) -> None:
        for fname in ("agent.py", "workflows.py"):
            with open(os.path.join(DEPT_DIR, fname), encoding="utf-8") as fh:
                src = fh.read()
            for banned in ("uuid4", "datetime.now", "date.today", "time.time(", "import requests",
                           "urllib.request"):
                self.assertNotIn(banned, src, f"{fname} contains {banned}")


class DeterminismTests(unittest.TestCase):
    def test_full_run_is_reproducible(self) -> None:
        dumps = []
        for _ in range(2):
            company, _ = make_env()
            for fn in workflows.SCENARIOS.values():
                company.seed(fn(company.bus, company.clock))
            company.run(90)
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
        ids = re.findall(r"^## (SOP-FINANCE-\d{2}): ", text, flags=re.M)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for sub in ("### Steps", "### Outputs and messages", "### SLA and controls",
                    "### Exceptions and escalation"):
            self.assertGreaterEqual(text.count(sub), len(ids), sub)
        for field in ("**Owner**", "**Trigger**", "**Inputs**"):
            self.assertGreaterEqual(text.count(field), len(ids), field)

    def test_sops_cover_subscribed_and_published_topics(self) -> None:
        text = read_doc("sops.md")
        # every published topic must appear in the SOPs; core subscribed topics must trigger a SOP
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic {topic} not in sops.md")
        for topic in ("external.client_payment_received", "delivery.milestone_reached",
                      "sales.deal_approval_requested", "legal.contract_signed",
                      "executive.budget_approved"):
            self.assertIn(topic, text, f"subscribed topic {topic} not in sops.md")

    def test_sops_mark_steps_human_or_agent(self) -> None:
        text = read_doc("sops.md")
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)

    def test_blueprint_mentions_head_and_agent_class(self) -> None:
        text = read_doc("blueprint.md")
        self.assertIn("Chief Financial Officer", text)

    def test_kpi_doc_has_at_least_eight_kpis(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("## 2.", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)]
        self.assertGreaterEqual(len(rows), 8)
        self.assertEqual(len(rows), len(KPIS))

    def test_kpi_doc_company_targets_consistent(self) -> None:
        text = read_doc("kpis.md")
        row = next(r for r in text.splitlines() if r.startswith("| gross_margin_pct |"))
        cells = [c.strip() for c in row.strip("|").split("|")]
        self.assertEqual(cells[3:6], ["48", "58", "64"])  # COMPANY.md §5.1
        row = next(r for r in text.splitlines() if r.startswith("| ebitda_margin_pct |"))
        cells = [c.strip() for c in row.strip("|").split("|")]
        self.assertEqual(cells[3:6], ["-25", "9", "16"])  # COMPANY.md §5.1


class BudgetTests(unittest.TestCase):
    def test_company_md_row_is_what_we_expect(self) -> None:
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            row = next(r for r in fh.read().splitlines() if r.startswith("| finance |") and "310" in r)
        nums = [int(c.replace(",", "")) for c in re.findall(r"[\d,]+", row)]
        self.assertEqual(tuple(nums[:3]), BUDGET_PEOPLE)
        self.assertEqual(tuple(nums[3:6]), BUDGET_NON_PEOPLE)
        self.assertEqual(tuple(nums[6:9]), BUDGET_TOTAL)

    def test_totals_are_internally_consistent(self) -> None:
        for p, n, t in zip(BUDGET_PEOPLE, BUDGET_NON_PEOPLE, BUDGET_TOTAL):
            self.assertEqual(p + n, t)

    def test_economics_states_envelope_totals(self) -> None:
        text = read_doc("economics.md")
        for total in ("310", "730", "1,500"):
            self.assertRegex(text, rf"(?<![\d,.]){re.escape(total)}(?![\d])", f"total {total} missing")
        for people in ("210", "480", "800"):
            self.assertRegex(text, rf"(?<![\d,.]){people}(?![\d])", f"people cost {people} missing")

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


if __name__ == "__main__":
    unittest.main()
