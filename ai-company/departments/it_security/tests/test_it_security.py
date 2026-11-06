"""Contract and behaviour tests for the it_security department (agent, workflows, docs, budget)."""

from __future__ import annotations

import os
import re
import unittest

from core import (Company, DepartmentAgent, Kpi, Message, MessageBus, MockLLM, SimClock, class_name_for,
                  publishes_for, subscribes_for)
from core.events import EventLog
from departments.it_security import agent as agent_mod
from departments.it_security import workflows
from departments.it_security.agent import KPIS, ItSecurityAgent, build_agent

DEPT = "it_security"
HERE = os.path.dirname(os.path.abspath(__file__))
DEPT_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(DEPT_DIR))

# COMPANY.md §5.4 it_security row (GBP k): people, non-people, total for FY2026..FY2028
BUDGET_PEOPLE = (260, 470, 900)
BUDGET_NON_PEOPLE = (200, 450, 1400)
BUDGET_TOTAL = (460, 920, 2300)
HEADCOUNT = (2, 5, 9)  # COMPANY.md §6.1 humans, year-end

DOC_HEADINGS = {
    "blueprint.md": [
        "# IT and Information Security Department Blueprint", "## 1. Mission and scope", "## 2. Org chart",
        "## 3. Roles", "## 4. AI agents", "## 5. Hiring plan", "## 6. Interfaces", "## 7. Risks and dependencies",
        "## 8. Sources",
    ],
    "sops.md": ["# IT and Security Standard Operating Procedures", "## Overview"],
    "kpis.md": [
        "# IT and Security KPIs", "## 1. KPI summary", "## 2. Definitions and formulas",
        "## 3. Reporting cadence and data sources", "## 4. Links to company targets",
    ],
    "economics.md": [
        "# IT and Information Security Economics", "## 1. Budget", "## 2. Headcount cost build-up",
        "## 3. Pricing and unit economics", "## 4. Assumptions", "## 5. Reconciliation to COMPANY.md",
    ],
}

BLUEPRINT_TITLES = (
    "Chief Information Security Officer", "GRC Lead", "Security Engineering Lead",
    "Senior Security Specialist (Engineering)", "Security and IT Operations Specialist",
    "Security Operations Specialist", "IT Support Analyst",
)


def read_doc(name: str) -> str:
    with open(os.path.join(DEPT_DIR, name), encoding="utf-8") as fh:
        return fh.read()


def make_env():
    """Fresh (company, agent) with only it_security live (other departments are stubs)."""
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
        "client_id": "CL-0007", "client_name": "Calder Freight Group", "deal_id": "DL-0001", "contract_id": "CT-0001",
        "engagement_id": "EN-0001", "amount_gbp": 60000, "department": "delivery", "role": "Consultant",
        "summary": f"test {topic}", "due_day": 30, "severity": "high", "employee_id": "EMP-0100",
        "vendor_id": "VN-0001", "vendor_name": "Test Vendor", "year": 2026, "budget_cycle_id": "BUD-2026",
    }


def external_sender(topic: str) -> str:
    return "external" if topic.startswith("external.") else topic.split(".", 1)[0]


class ContractTests(unittest.TestCase):
    def test_class_name(self) -> None:
        self.assertEqual(class_name_for(DEPT), "ItSecurityAgent")
        self.assertTrue(issubclass(ItSecurityAgent, DepartmentAgent))

    def test_build_agent(self) -> None:
        agent, bus, _, _ = standalone_agent()
        self.assertIsInstance(agent, ItSecurityAgent)
        self.assertEqual(agent.name, DEPT)
        self.assertEqual(agent.department, DEPT)
        self.assertEqual(bus.agent_names, [], "build_agent must not register with the bus")
        self.assertEqual(len(bus.pending), 0, "build_agent must not publish")

    def test_topic_map(self) -> None:
        self.assertEqual(tuple(ItSecurityAgent.SUBSCRIBES), subscribes_for(DEPT))
        self.assertEqual(tuple(ItSecurityAgent.PUBLISHES), publishes_for(DEPT))
        self.assertGreater(len(ItSecurityAgent.SUBSCRIBES), 0)
        self.assertGreater(len(ItSecurityAgent.PUBLISHES), 0)

    def test_kpis(self) -> None:
        self.assertEqual(len(KPIS), 12)
        self.assertTrue(all(isinstance(k, Kpi) for k in KPIS))
        names = [k.name for k in KPIS]
        self.assertEqual(len(names), len(set(names)))

    def test_kpis_mirror_doc(self) -> None:
        kpi_doc = read_doc("kpis.md")
        for k in KPIS:
            row = next((r for r in kpi_doc.splitlines() if r.startswith(f"| {k.name} |")), None)
            self.assertIsNotNone(row, f"{k.name} missing from kpis.md")
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertEqual(cells[2], k.unit, k.name)
            self.assertAlmostEqual(float(cells[3]), float(k.target), places=6, msg=k.name)
            self.assertEqual(cells[6].lower().startswith("higher"), k.higher_is_better, k.name)

    def test_role(self) -> None:
        agent, _, _, _ = standalone_agent()
        self.assertEqual(agent.role.department, DEPT)
        self.assertEqual(agent.role.level, "head")
        self.assertEqual(agent.role.title, "Chief Information Security Officer")

    def test_constants_match_sops(self) -> None:
        sops = read_doc("sops.md")
        a = agent_mod
        self.assertEqual(a.VULN_SLA_DAYS, {"critical": 7, "high": 30, "medium": 60, "low": 90})
        self.assertIn("Critical 7 days (24 hours if actively exploited), high 30 days, medium 60 days, low 90 days", sops)
        self.assertEqual(a.VULN_EXPLOITED_SLA_HOURS, 24)
        self.assertIn("Privileged accounts disabled in 1 hour, all access in 4 hours", sops)
        self.assertEqual((a.LEAVER_PRIVILEGED_HOURS, a.LEAVER_ALL_ACCESS_HOURS), (1, 4))
        self.assertIn("Triage in 30 min (critical/high), 4 clock hours (medium), 1 business day (low)", sops)
        self.assertEqual((a.TRIAGE_CRITICAL_HIGH_MINUTES, a.TRIAGE_MEDIUM_CLOCK_HOURS, a.TRIAGE_LOW_BUSINESS_DAYS),
                         (30, 4, 1))
        self.assertIn("Standard questionnaire 3 business days; bespoke or on-site audit request 4 business days", sops)
        self.assertEqual((a.QUESTIONNAIRE_STANDARD_BDAYS, a.QUESTIONNAIRE_BESPOKE_BDAYS), (3, 4))
        self.assertIn("Tier 1: 10 business days; Tier 2: 5 business days; Tier 3: 2 business days", sops)
        self.assertEqual(a.VENDOR_REVIEW_BDAYS, {1: 10, 2: 5, 3: 2})
        self.assertIn("credential rotation 90 days", sops)
        self.assertEqual(a.AGENT_CREDENTIAL_ROTATION_DAYS, 90)
        self.assertIn("£250k", sops)
        self.assertEqual(a.CISO_SIGNOFF_DEAL_GBP, 250_000)
        self.assertIn("expiry maximum 90 days", sops)
        self.assertEqual(a.RISK_ACCEPTANCE_MAX_DAYS, 90)
        self.assertEqual(a.ICO_NOTIFICATION_HOURS, 72)
        self.assertEqual(a.AGENT_PAYMENT_LIMIT_GBP, 10_000)

    def test_agent_role_titles_are_blueprint_titles(self) -> None:
        with open(os.path.join(DEPT_DIR, "agent.py"), encoding="utf-8") as fh:
            src = fh.read()
        blueprint = read_doc("blueprint.md")
        for title in BLUEPRINT_TITLES:
            self.assertIn(title, blueprint)
        for hired in re.findall(r'"([A-Z][A-Za-z ()]+(?:Specialist|Lead|Analyst|Officer)[A-Za-z ()]*)"', src):
            if hired in ("Chief Information Security Officer",):
                continue
            if hired.startswith("Chief") or hired.endswith("Officer"):
                continue  # other departments' heads (COMPANY.md section 9.2)
            self.assertIn(hired, BLUEPRINT_TITLES + ("Security and IT Operations Specialist",), hired)


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
                    self.assertTrue(m.topic.startswith("it_security."))
                    self.assertNotIn(".internal.", m.topic)

    def test_handle_tolerates_empty_body(self) -> None:
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                msg = bus.make_message(external_sender(topic), DEPT, topic, {}, sim_time=0)
                self.assertIsInstance(agent.handle(msg), list)

    def test_handle_tolerates_non_dict_and_garbage_values(self) -> None:
        garbage = {"severity": 7, "amount_gbp": "lots", "last_day": "soon", "findings": "none", "due_day": None,
                   "personal_data_involved": "maybe", "data_classes": 5, "evidence": {"a": 1}}
        for topic in subscribes_for(DEPT):
            with self.subTest(topic=topic):
                agent, bus, _, _ = standalone_agent()
                agent.handle(bus.make_message(external_sender(topic), DEPT, topic, garbage, sim_time=0))

    def test_unknown_topic_does_not_raise(self) -> None:
        agent, bus, _, _ = standalone_agent()
        msg = bus.make_message("sales", DEPT, "sales.lead_qualified_unknown", {}, sim_time=0)
        self.assertEqual(agent.handle(msg), [])

    def test_handle_is_deterministic(self) -> None:
        results = []
        for _ in range(2):
            agent, bus, _, log = standalone_agent()
            for topic in subscribes_for(DEPT):
                agent.handle(bus.make_message(external_sender(topic), DEPT, topic, sample_body(topic), sim_time=0))
            results.append(log.to_jsonl())
        self.assertEqual(results[0], results[1])

    def test_tick_runs_over_three_years_without_error(self) -> None:
        company, agent = make_env()
        company.run(1100)
        for m in agent.tick() or []:
            self.assertIn(m.topic, agent.PUBLISHES)
        self.assertGreater(len(company.log.query(department=DEPT)), 0)

    def test_tick_is_idempotent_within_a_day(self) -> None:
        agent, _, _, _ = standalone_agent()
        agent.tick()
        self.assertEqual(agent.tick(), [])


class WorkflowTests(unittest.TestCase):
    def test_scenarios_dict(self) -> None:
        self.assertGreaterEqual(len(workflows.SCENARIOS), 3)
        for name, fn in workflows.SCENARIOS.items():
            self.assertTrue(callable(fn))
            self.assertEqual(fn.__name__, f"scenario_{name}")

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

    def test_some_scenario_starts_from_subscribed_topic(self) -> None:
        subs = set(subscribes_for(DEPT))
        for name, fn in workflows.SCENARIOS.items():
            clock = SimClock()
            self.assertTrue(any(m.topic in subs for m in fn(MessageBus(clock), clock)), name)

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
    """Lifecycle behaviours: the right it_security topics are emitted for the right triggers."""

    def _run(self, topic: str, body: dict, days: int = 30, sender: str | None = None):
        company, agent = make_env()
        company.inject(topic, body, recipient=DEPT, sender=sender or external_sender(topic))
        company.run(days)
        return company, agent

    def _emitted(self, company: Company, topic: str | None = None) -> list:
        evs = [e for e in company.log.query(department=DEPT) if e.data.get("kind") == "emit"]
        return [e for e in evs if topic is None or e.topic == topic]

    def _topics(self, company: Company) -> set[str]:
        return {e.topic for e in self._emitted(company)}

    # hiring chain
    def test_new_hire_gets_access_provisioned(self) -> None:
        company, agent = self._run("people.new_hire_started", {
            "employee_id": "EMP-0050", "role": "Consultant", "department": "delivery", "start_day": 3}, 10, "people")
        ev = self._emitted(company, "it_security.access_provisioned")
        self.assertEqual(len(ev), 1)
        body = ev[0].data["body"]
        self.assertEqual(body["employee_id"], "EMP-0050")
        self.assertIn("email", body["access_bundle"])
        self.assertFalse(body["privileged"])
        self.assertEqual(agent.kpis["access_provisioning_sla_pct"].actual, 100.0)
        self.assertEqual(agent.kpis["mfa_coverage_pct"].actual, 100.0)

    def test_privileged_role_waits_for_ciso_approval(self) -> None:
        company, agent = self._run("people.new_hire_started", {
            "employee_id": "EMP-0051", "role": "Security and IT Operations Specialist", "department": "it_security"},
            5, "people")
        body = self._emitted(company, "it_security.access_provisioned")[0].data["body"]
        self.assertFalse(body["privileged"])
        self.assertTrue(body["pending_privileged_approval"])
        self.assertTrue(any("CISO to approve privileged" in t.title for t in agent.tasks.values()))

    def test_toxic_combination_is_blocked(self) -> None:
        company, _ = self._run("people.new_hire_started", {
            "employee_id": "EMP-0052", "role": "Head of Procurement Billing", "department": "finance"}, 5, "people")
        body = self._emitted(company, "it_security.access_provisioned")[0].data["body"]
        self.assertNotIn("supplier_master_edit", body["access_bundle"])
        self.assertTrue(any("toxic" in x for x in body["exceptions"]))

    def test_contractor_access_has_expiry_and_hold_without_background_check(self) -> None:
        company, _ = self._run("people.contractor_engaged", {
            "contractor_id": "CTR-0001", "role": "Analyst associate", "department": "data", "engagement_end_day": 60},
            10, "people")
        body = self._emitted(company, "it_security.access_provisioned")[0].data["body"]
        self.assertEqual(body["expires_day"], 60)
        company, agent = self._run("people.contractor_engaged", {
            "contractor_id": "CTR-0002", "background_check": False}, 10, "people")
        self.assertEqual(self._emitted(company, "it_security.access_provisioned"), [])
        self.assertIn("CTR-0002", agent.state["held_requests"])

    def test_leaver_gets_access_revoked(self) -> None:
        company, agent = self._run("people.employee_left", {
            "employee_id": "EMP-0012", "role": "Consultant", "department": "delivery", "last_day": 5,
            "involuntary": False}, 15, "people")
        ev = self._emitted(company, "it_security.access_revoked")
        self.assertEqual(len(ev), 1)
        body = ev[0].data["body"]
        self.assertEqual(body["employee_id"], "EMP-0012")
        self.assertEqual(body["revoked_at_day"], 5)
        self.assertLessEqual(agent.kpis["leaver_revocation_hours"].actual, 4.0)

    def test_involuntary_leaver_is_revoked_immediately_and_exfiltration_opens_incident(self) -> None:
        company, agent = self._run("people.employee_left", {
            "employee_id": "EMP-0019", "last_day": 20, "involuntary": True, "privileged": True,
            "exfiltration_suspected": True}, 5, "people")
        body = self._emitted(company, "it_security.access_revoked")[0].data["body"]
        self.assertEqual(body["revoked_at_day"], 0)
        self.assertEqual(body["revocation_hours"], 0.0)
        self.assertIn("it_security.incident_detected", self._topics(company))

    # incident chain
    def test_security_alert_critical_declares_incident(self) -> None:
        company, _ = self._run("external.security_alert", {
            "summary": "EDR ransomware precursor", "severity": "critical", "asset": "srv-fin-01",
            "indicator": "lsass-dump"}, 5)
        ev = self._emitted(company, "it_security.incident_detected")
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0].data["body"]["incident_id"], "INC-0001")
        self.assertEqual(ev[0].data["body"]["severity"], "critical")

    def test_low_alert_is_ticketed_not_declared(self) -> None:
        company, agent = self._run("external.security_alert", {"summary": "blocked attack", "severity": "low"}, 5)
        self.assertEqual(self._emitted(company, "it_security.incident_detected"), [])
        self.assertTrue(agent.tasks)

    def test_duplicate_alert_is_merged(self) -> None:
        company, agent = make_env()
        for _ in range(2):
            company.inject("external.security_alert", {"severity": "high", "asset": "a", "indicator": "i"},
                           recipient=DEPT, sender="external")
        company.run(3)
        self.assertEqual(len(self._emitted(company, "it_security.incident_detected")), 1)
        self.assertEqual(agent.state["incidents"]["INC-0001"]["alerts"], 2)

    def test_false_positive_closes_without_incident(self) -> None:
        company, agent = self._run("external.security_alert", {"severity": "critical", "true_positive": False}, 3)
        self.assertEqual(self._emitted(company, "it_security.incident_detected"), [])
        self.assertEqual(agent.state["false_positives"], 1)

    def test_phishing_simulation_feeds_report_rate(self) -> None:
        _, agent = self._run("external.security_alert", {
            "source": "phishing_simulation", "targeted": 40, "reported": 22, "clicked": 3}, 2)
        self.assertEqual(agent.kpis["phishing_simulation_report_rate_pct"].actual, 55.0)

    def test_personal_data_incident_chain_to_resolution(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_phishing_to_breach(company.bus, company.clock))
        company.run(20)
        topics = self._topics(company)
        for t in ("it_security.incident_detected", "it_security.data_breach_confirmed", "it_security.incident_resolved"):
            self.assertIn(t, topics)
        breach = self._emitted(company, "it_security.data_breach_confirmed")[0].data["body"]
        self.assertEqual(breach["incident_id"], "INC-0001")
        self.assertEqual(breach["due_day"], 3)  # awareness day 0 + 72 hours
        resolved = self._emitted(company, "it_security.incident_resolved")[0].data["body"]
        self.assertEqual(resolved["regulator_filing_ref"], "ICO-2026-CALDER-001")
        self.assertEqual(agent.state["incidents"]["INC-0001"]["status"], "resolved")
        self.assertEqual(agent.state["ico_late"], 0)

    def test_non_personal_data_incident_resolves_without_breach(self) -> None:
        company, agent = self._run("external.security_alert", {
            "severity": "high", "summary": "malware on managed laptop", "asset": "lt-1", "category": "malware",
            "personal_data_involved": False}, 5)
        topics = self._topics(company)
        self.assertIn("it_security.incident_resolved", topics)
        self.assertNotIn("it_security.data_breach_confirmed", topics)
        agent.kpi_snapshot()   # KPI actuals are rolled up on snapshot / month end
        self.assertLessEqual(agent.kpis["mttr_critical_incident_hours"].actual, 8.0)

    def test_breach_without_filing_escalates_then_closes(self) -> None:
        company, agent = self._run("external.security_alert", {
            "severity": "critical", "client_id": "CL-0007", "personal_data_involved": True, "summary": "exposure"}, 25)
        breaches = self._emitted(company, "it_security.data_breach_confirmed")
        self.assertGreaterEqual(len(breaches), 2, "an escalation update is expected at hour 60")
        self.assertTrue(any(b.data["body"].get("update") for b in breaches))
        self.assertIn("it_security.incident_resolved", self._topics(company))

    def test_crisis_security_opens_incident(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_crisis_response(company.bus, company.clock))
        company.run(10)
        topics = self._topics(company)
        self.assertIn("it_security.incident_detected", topics)
        self.assertIn("it_security.incident_resolved", topics)
        self.assertFalse(agent.state["crisis_mode"])

    def test_non_security_crisis_is_support_only(self) -> None:
        company, agent = self._run("executive.crisis_declared", {"summary": "Supplier outage", "severity": "high",
                                                                 "expected_duration_days": 3}, 6, "executive")
        self.assertEqual(self._emitted(company), [])
        self.assertFalse(agent.state["crisis_mode"])

    # vulnerabilities
    def test_release_findings_are_published_with_sla_due_days(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_vulnerability_lifecycle(company.bus, company.clock))
        company.run(3)
        found = {e.data["body"]["vulnerability_id"]: e.data["body"]
                 for e in self._emitted(company, "it_security.vulnerability_found")}
        self.assertEqual(found["VULN-9001"]["due_day"], 1)       # critical and exploited: 24 hours
        self.assertEqual(found["VULN-9002"]["due_day"], 30)      # high: 30 days
        self.assertNotIn("VULN-9003", found)                     # low is tracked, not published
        self.assertEqual(agent.state["vulns"]["VULN-9001"]["status"], "closed")

    def test_unfixed_high_finding_escalates_and_hits_kpi(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_vulnerability_lifecycle(company.bus, company.clock))
        company.run(130)
        escal = [e.data["body"] for e in self._emitted(company, "it_security.vulnerability_found")
                 if e.data["body"].get("escalation")]
        self.assertTrue(any(b["escalation"] == "Chief Product Officer" for b in escal))
        self.assertTrue(any(b["escalation"] == "Chief Executive Officer" for b in escal))
        self.assertLess(agent.kpis["critical_vuln_sla_pct"].actual, 100.0)

    def test_failed_rescan_reopens_finding(self) -> None:
        company, agent = make_env()
        company.inject("product.release_shipped", {"release_id": "R1", "findings": [
            {"vulnerability_id": "V1", "severity": "high", "summary": "x", "component": "c"}]}, DEPT, "product")
        company.inject("product.vulnerability_fixed", {"vulnerability_id": "V1", "rescan_clean": False}, DEPT, "product",
                       delay_days=1)
        company.run(3)
        self.assertEqual(agent.state["vulns"]["V1"]["status"], "open")
        self.assertTrue(any(e.data["body"].get("reopened") for e in self._emitted(company)))

    def test_risk_acceptance_is_capped_at_90_days_and_expires(self) -> None:
        company, agent = make_env()
        company.inject("product.release_shipped", {"release_id": "R2", "findings": [
            {"vulnerability_id": "V2", "severity": "high", "summary": "no patch", "component": "c",
             "risk_accepted_by_ciso": True, "risk_acceptance_days": 365, "vendor_patch_available": False}]},
            DEPT, "product")
        company.run(2)
        self.assertEqual(agent.state["vulns"]["V2"]["status"], "accepted")
        self.assertEqual(agent.state["vulns"]["V2"]["accept_expiry"], 90)
        company.run(95)
        self.assertEqual(agent.state["vulns"]["V2"]["status"], "open")

    # client assurance
    def test_questionnaire_sla_and_signoff(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_client_security_review(company.bus, company.clock))
        company.run(15)
        done = {e.data["body"]["deal_id"]: e.data["body"]
                for e in self._emitted(company, "it_security.security_questionnaire_completed")}
        self.assertEqual(set(done), {"DL-0014", "DL-0015"})
        self.assertTrue(done["DL-0014"]["ciso_signoff_required"])
        self.assertEqual(done["DL-0014"]["completed_day"], 3)
        self.assertEqual(done["DL-0014"]["outcome"], "passed_with_conditions")   # ISO 27001 not yet certified
        self.assertEqual(done["DL-0014"]["certificates_provided"], [])
        # bespoke questionnaires take 4 BUSINESS days (sops.md): day 2 is a Wednesday, so Tuesday = day 8
        self.assertEqual(done["DL-0015"]["completed_day"], 8)
        self.assertLessEqual(agent.kpis["security_questionnaire_turnaround_days"].actual, 5)

    def test_small_standard_questionnaire_needs_no_ciso_signoff(self) -> None:
        company, _ = self._run("sales.security_review_requested", {
            "deal_id": "DL-0099", "client_id": "CL-0002", "questionnaire_type": "caiq", "amount_gbp": 45000}, 8, "sales")
        body = self._emitted(company, "it_security.security_questionnaire_completed")[0].data["body"]
        self.assertFalse(body["ciso_signoff_required"])
        self.assertEqual(body["outcome"], "passed")

    # vendors and agents
    def test_vendor_review_tiers_and_sla(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_vendor_and_ai_risk(company.bus, company.clock))
        company.run(30)
        ev = self._emitted(company, "it_security.vendor_risk_assessed")
        self.assertEqual(len(ev), 1)
        body = ev[0].data["body"]
        self.assertEqual(body["tier"], 1)          # AI platform with client confidential data beats the hint of 2
        self.assertEqual(body["decision"], "approve_with_conditions")
        self.assertTrue(any("no training" in c for c in body["conditions"]))
        self.assertTrue(any("UK IDTA" in c for c in body["conditions"]))
        self.assertEqual(body["due_day"], 14)       # 10 business days from Monday 2026-01-05
        self.assertEqual(agent.kpis["vendor_assessments_on_time_pct"].actual, 100.0)
        self.assertTrue(agent.state["vendors"]["VN-0021"]["approved"])

    def test_vendor_tier_three_is_two_business_days(self) -> None:
        company, _ = self._run("operations.vendor_review_requested", {
            "vendor_id": "VN-0002", "vendor_name": "Stationery Co", "service": "office supplies"}, 6, "operations")
        body = self._emitted(company, "it_security.vendor_risk_assessed")[0].data["body"]
        self.assertEqual(body["tier"], 3)
        self.assertEqual(body["due_day"], 2)

    def test_vendor_refusing_evidence_is_rejected_at_tier_one(self) -> None:
        company, _ = self._run("operations.vendor_review_requested", {
            "vendor_id": "VN-0003", "data_classes": ["personal"], "evidence_refused": True}, 20, "operations")
        self.assertEqual(self._emitted(company, "it_security.vendor_risk_assessed")[0].data["body"]["decision"],
                         "reject")

    def test_vendor_approved_without_assessment_is_late_assessed(self) -> None:
        company, agent = self._run("operations.vendor_approved", {"vendor_id": "VN-0004", "data_classes": ["personal"]},
                                   20, "operations")
        self.assertIn("it_security.vendor_risk_assessed", self._topics(company))
        self.assertEqual(agent.kpis["vendor_assessments_on_time_pct"].actual, 0.0)

    def test_ai_risk_review_updates_register_and_flags_secret(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_vendor_and_ai_risk(company.bus, company.clock))
        company.run(5)
        rec = agent.state["agent_register"]["AGT-delivery-triage-02"]
        self.assertEqual(rec["status"], "blocked")
        self.assertEqual(rec["rotation_days"], 30)
        vulns = self._emitted(company, "it_security.vulnerability_found")
        self.assertTrue(any(v.data["body"]["component"] == "AGT-delivery-triage-02" for v in vulns))

    def test_ai_review_blocks_agent_with_payment_authority_over_limit(self) -> None:
        _, agent = self._run("product.ai_risk_review_requested", {
            "agent_id": "AGT-x", "max_autonomous_payment_gbp": 25000, "requested_by": "Chief Product Officer"}, 3, "product")
        self.assertEqual(agent.state["agent_register"]["AGT-x"]["status"], "blocked")

    def test_anomalous_agent_behaviour_raises_incident_and_suspends(self) -> None:
        company, agent = self._run("product.ai_risk_review_requested", {
            "agent_id": "AGT-sales", "anomalous_behaviour": True, "requested_by": "x"}, 3, "product")
        self.assertIn("it_security.incident_detected", self._topics(company))
        self.assertEqual(agent.state["agent_register"]["AGT-sales"]["status"], "suspended")

    def test_leaver_who_owns_an_agent_suspends_it(self) -> None:
        _, agent = self._run("people.employee_left", {"employee_id": "EMP-0077", "owned_agents": ["AGT-data"]}, 3,
                             "people")
        self.assertEqual(agent.state["agent_register"]["AGT-data"]["status"], "suspended")

    def test_credentials_rotate_within_policy(self) -> None:
        company, agent = make_env()
        company.run(200)
        self.assertGreater(agent.state["rotations"], 0)
        self.assertEqual(agent.kpis["agent_credential_compliance_pct"].actual, 100.0)
        for rec in agent.state["agent_register"].values():
            self.assertLessEqual(company.clock.day - rec["last_rotated_day"], rec["rotation_days"])

    # compliance and certification
    def test_training_continuity_and_policy_inputs_update_state(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_compliance_and_budget_cycle(company.bus, company.clock))
        company.run(60)
        self.assertEqual(agent.kpis["security_training_completion_pct"].actual, 92.0)
        self.assertIn("POL-AI-USE", agent.state["policies"])
        self.assertTrue(agent.state["continuity_tests"]["BCP-2026-01"]["rto_missed"])
        self.assertTrue(agent.state["regulatory_changes"])

    def test_budget_submission_matches_envelope(self) -> None:
        company, agent = make_env()
        company.seed(workflows.scenario_compliance_and_budget_cycle(company.bus, company.clock))
        company.run(30)
        body = self._emitted(company, "it_security.budget_submitted")[0].data["body"]
        self.assertEqual((body["people_gbp"], body["non_people_gbp"], body["amount_gbp"]), (470000, 450000, 920000))
        self.assertEqual(body["headcount_requested"], 5)
        self.assertEqual(self._emitted(company, "it_security.budget_submitted")[0].data["recipient"], "finance")
        company.run(20)
        self.assertEqual(agent.state["approved_budget"], 920000)

    def test_certification_status_published_and_iso_certified_by_year_end(self) -> None:
        company, agent = make_env()
        company.run(370)
        ev = self._emitted(company, "it_security.certification_status_updated")
        self.assertTrue(ev)
        by_cert: dict[str, list] = {}
        for e in ev:
            by_cert.setdefault(e.data["body"]["certification"], []).append(e.data["body"])
        self.assertEqual(set(by_cert), {"iso_27001", "cyber_essentials_plus", "soc2_type2"})
        self.assertEqual(by_cert["iso_27001"][-1]["status"], "certified")
        self.assertEqual(by_cert["cyber_essentials_plus"][-1]["status"], "certified")
        self.assertNotEqual(by_cert["soc2_type2"][-1]["status"], "certified")
        for bodies in by_cert.values():
            for b in bodies:
                for key in ("status", "readiness_pct", "open_nonconformities", "next_milestone", "summary"):
                    self.assertIn(key, b)
        self.assertEqual(agent.kpis["certification_milestones_on_track_pct"].actual, 100.0)

    def test_iso_certificate_triggers_fy2027_hire_requests(self) -> None:
        company, agent = make_env()
        company.run(370)
        roles = [e.data["body"]["role"] for e in self._emitted(company, "it_security.hire_requested")]
        self.assertIn("GRC Lead", roles)
        self.assertIn("Senior Security Specialist (Engineering)", roles)
        self.assertEqual(len(roles), len(set(roles)), "no duplicate requisitions")
        for e in self._emitted(company, "it_security.hire_requested"):
            self.assertEqual(e.data["recipient"], "people")

    def test_late_certification_when_controls_fail(self) -> None:
        company, agent = make_env()
        for i in range(8):   # eight failed continuity tests plus a low training rate degrade readiness
            company.inject("operations.continuity_test_completed", {"test_id": f"T{i}", "rto_met": False},
                           DEPT, "operations")
        company.inject("people.compliance_training_completed", {"course": "security", "completion_rate": 40}, DEPT,
                       "people")
        company.run(340)
        iso = agent.state["certs"]["iso_27001"]
        self.assertTrue(any(m["missed"] for m in iso["milestones"]) or iso["status"] != "certified")

    def test_all_emitted_topics_are_published_topics(self) -> None:
        for name, fn in workflows.SCENARIOS.items():
            with self.subTest(scenario=name):
                company, _ = make_env()
                company.seed(fn(company.bus, company.clock))
                company.run(120)
                for e in self._emitted(company):
                    self.assertIn(e.topic, publishes_for(DEPT))
                    self.assertNotIn(".internal.", e.topic)

    def test_every_published_topic_is_reachable_in_scenarios_or_ticks(self) -> None:
        seen: set[str] = set()
        for fn in workflows.SCENARIOS.values():
            company, _ = make_env()
            company.seed(fn(company.bus, company.clock))
            company.run(400)
            seen |= self._topics(company)
        for topic in publishes_for(DEPT):
            self.assertIn(topic, seen, f"{topic} never emitted")

    def test_state_is_updated_and_kpi_snapshot(self) -> None:
        _, agent = self._run("people.new_hire_started", {"employee_id": "EMP-0001", "department": "sales"}, 3, "people")
        self.assertTrue(agent.state["accounts"])
        snap = agent.kpi_snapshot()
        self.assertEqual([k.name for k in snap], [k.name for k in KPIS])
        self.assertTrue(all(isinstance(k, Kpi) for k in snap))
        no_data = [k.name for k in snap if k.actual is None]
        self.assertIn("phishing_simulation_report_rate_pct", no_data, "missing data must stay None, never 100")

    def test_no_wall_clock_or_uuid_in_sources(self) -> None:
        for fname in ("agent.py", "workflows.py"):
            with open(os.path.join(DEPT_DIR, fname), encoding="utf-8") as fh:
                src = fh.read()
            for banned in ("uuid4", "datetime.now", "date.today", "time.time(", "import requests",
                           "urllib.request", "import random"):
                self.assertNotIn(banned, src, f"{fname} contains {banned}")

    def test_agent_never_emits_internal_topics(self) -> None:
        with open(os.path.join(DEPT_DIR, "agent.py"), encoding="utf-8") as fh:
            self.assertNotIn("it_security.internal.", fh.read())


class DeterminismTests(unittest.TestCase):
    def test_full_run_is_reproducible(self) -> None:
        dumps = []
        for _ in range(2):
            company, _ = make_env()
            for fn in workflows.SCENARIOS.values():
                company.seed(fn(company.bus, company.clock))
            company.run(200)
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
        ids = re.findall(r"^## (SOP-IT_SECURITY-\d{2}): ", text, flags=re.M)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for sub in ("### Steps", "### Outputs and messages", "### SLA and controls", "### Exceptions and escalation"):
            self.assertGreaterEqual(text.count(sub), len(ids), sub)
        for field in ("**Owner**:", "**Trigger**:", "**Inputs**:"):
            self.assertGreaterEqual(text.count(field), len(ids), field)

    def test_sops_cover_subscribed_and_published_topics(self) -> None:
        text = read_doc("sops.md")
        for topic in publishes_for(DEPT):
            self.assertIn(topic, text, f"published topic {topic} not in sops.md")
        for topic in subscribes_for(DEPT):
            if topic == "it_security.internal":
                continue
            self.assertIn(topic, text, f"subscribed topic {topic} not in sops.md")

    def test_every_subscribed_topic_is_a_sop_trigger(self) -> None:
        text = read_doc("sops.md")
        triggers = re.findall(r"\*\*Trigger\*\*:(.*)", text)
        joined = "\n".join(triggers)
        for topic in subscribes_for(DEPT):
            if topic in ("finance.budget_cycle_opened",) or True:
                self.assertIn(topic, joined + text.split("## Overview", 1)[1].split("## SOP-", 1)[0], topic)

    def test_sops_mark_steps_human_or_agent(self) -> None:
        text = read_doc("sops.md")
        self.assertIn("[human]", text)
        self.assertIn("[agent]", text)

    def test_blueprint_mentions_head_and_agent_class(self) -> None:
        text = read_doc("blueprint.md")
        self.assertIn("Chief Information Security Officer", text)
        self.assertIn("ItSecurityAgent", text)

    def test_kpi_doc_has_twelve_kpis_matching_code(self) -> None:
        text = read_doc("kpis.md")
        section = text.split("## 1. KPI summary", 1)[1].split("## 2.", 1)[0]
        rows = [r for r in section.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)]
        self.assertEqual(len(rows), 12)
        self.assertEqual(len(rows), len(KPIS))
        self.assertEqual([r.split("|")[1].strip() for r in rows], [k.name for k in KPIS])

    def test_kpi_and_sop_owners_use_blueprint_titles(self) -> None:
        blueprint = read_doc("blueprint.md")
        text = read_doc("kpis.md").split("## 1. KPI summary", 1)[1].split("## 2.", 1)[0]
        for row in (r for r in text.splitlines() if re.match(r"^\| [a-z0-9_]+ \|", r)):
            owner = [c.strip() for c in row.strip("|").split("|")][-1]
            first = owner.split(" (")[0].split(" with ")[0].split(",")[0].strip()
            if first != "CISO":
                self.assertIn(first, blueprint, f"kpi owner {owner!r}")


class BudgetTests(unittest.TestCase):
    def test_company_md_row_is_what_we_expect(self) -> None:
        with open(os.path.join(ROOT, "COMPANY.md"), encoding="utf-8") as fh:
            row = next(r for r in fh.read().splitlines() if r.startswith("| it_security |") and "460" in r)
        nums = [int(c.replace(",", "")) for c in re.findall(r"[\d,]+", row)]
        self.assertEqual(tuple(nums[:3]), BUDGET_PEOPLE)
        self.assertEqual(tuple(nums[3:6]), BUDGET_NON_PEOPLE)
        self.assertEqual(tuple(nums[6:9]), BUDGET_TOTAL)

    def test_totals_are_internally_consistent(self) -> None:
        for p, n, t in zip(BUDGET_PEOPLE, BUDGET_NON_PEOPLE, BUDGET_TOTAL):
            self.assertEqual(p + n, t)

    def test_agent_constants_match_envelope(self) -> None:
        self.assertEqual(agent_mod.ENVELOPE_PEOPLE_GBP_K, BUDGET_PEOPLE)
        self.assertEqual(agent_mod.ENVELOPE_NON_PEOPLE_GBP_K, BUDGET_NON_PEOPLE)
        self.assertEqual(agent_mod.HEADCOUNT_PLAN, HEADCOUNT)

    def test_economics_states_envelope_totals(self) -> None:
        text = read_doc("economics.md")
        for total in ("460", "920", "2,300"):
            self.assertRegex(text, rf"(?<![\d,.]){re.escape(total)}(?![\d])", f"total {total} missing")
        for people in ("260", "470", "900"):
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
