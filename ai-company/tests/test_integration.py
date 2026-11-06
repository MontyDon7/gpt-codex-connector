"""Whole-company integration tests: all 12 department agents running together (strict mode).

Unit tests prove each department alone. These catch what only appears when departments talk to each other, such as
the crisis <-> incident feedback loop that multiplied events 25x until it was found in the first full-company run.
"""
from __future__ import annotations

import collections
import unittest

from core import Company, MockLLM


def make_company() -> Company:
    return Company(llm=MockLLM(), strict=True)


def topics(co: Company) -> list[str]:
    return [m.topic for m in co.bus.history]


def sim_days_of(co: Company, topic: str) -> list[int]:
    return [m.sim_time for m in co.bus.history if m.topic == topic]


CALDER = {"lead_id": "LD-1", "company": "Calder Freight Group", "employees": 650, "sector": "logistics",
          "contact_title": "Chief Financial Officer", "source": "referral", "service_interest": "forge",
          "pain": "manual dispatch planning"}
HARROW = {"lead_id": "LD-3", "company": "Harrow Retail Group", "employees": 400, "sector": "retail",
          "contact_title": "Chief Operating Officer", "source": "referral", "service_interest": "keep",
          "pain": "service desk backlog"}


class QuietYearTests(unittest.TestCase):
    def test_a_year_with_no_outside_events_is_clean_and_bounded(self) -> None:
        co = make_company()
        log = co.run(365)
        self.assertEqual([e for e in log if e.topic == "system.agent_error"], [])
        self.assertEqual(co.bus.dead_letters, [])
        # baseline is ~3.6k events; a runaway feedback loop between departments shows up as a large multiple
        self.assertLess(len(log), 8000)
        self.assertLess(len(co.bus.history), 2500)

    def test_every_department_is_alive(self) -> None:
        co = make_company()
        log = co.run(120)
        active = {e.department for e in log if not e.topic.startswith("system.")}
        self.assertEqual(active, set(co.agents))


class LeadToCashTests(unittest.TestCase):
    def test_inbound_lead_flows_from_marketing_to_a_signed_contract_and_delivery(self) -> None:
        co = make_company()
        co.inject("external.lead_inbound", CALDER, delay_days=2)
        co.run(300)
        seen = collections.Counter(topics(co))
        spine = ["marketing.lead_generated", "sales.lead_qualified", "sales.proposal_requested",
                 "delivery.scoping_completed", "finance.pricing_check_completed", "sales.proposal_sent",
                 "sales.deal_won", "legal.contract_drafted", "legal.contract_signed", "delivery.engagement_kickoff"]
        # billing and staffing are parallel branches after signature, so they are checked for presence only
        branches = ["finance.billing_schedule_created", "delivery.staffing_requested"]
        for t in spine + branches:
            self.assertGreater(seen[t], 0, f"chain broke before {t}")
        days = [min(sim_days_of(co, t)) for t in spine]
        self.assertEqual(days, sorted(days), "sequential lifecycle topics should occur in order")
        signed = min(sim_days_of(co, "legal.contract_signed"))
        for t in branches:
            self.assertGreaterEqual(min(sim_days_of(co, t)), signed, f"{t} should follow contract signature")

    def test_keep_deal_reaches_renewal(self) -> None:
        co = make_company()
        co.inject("external.lead_inbound", HARROW, delay_days=5)
        co.run(420)
        seen = collections.Counter(topics(co))
        for t in ("sales.deal_won", "legal.contract_signed", "customer_success.renewal_due",
                  "sales.renewal_proposal_sent"):
            self.assertGreater(seen[t], 0, f"missing {t}")
        signed, due = min(sim_days_of(co, "legal.contract_signed")), min(sim_days_of(co, "customer_success.renewal_due"))
        self.assertGreater(due - signed, 180, "renewal is due about 90 days before a 12-month term ends")


class BreachTests(unittest.TestCase):
    def test_breach_runs_once_through_security_legal_and_executive(self) -> None:
        co = make_company()
        co.inject("external.security_alert", {"alert_id": "AL-1", "severity": "critical",
                                              "personal_data_involved": True, "summary": "bulk export"},
                  delay_days=10)
        co.run(120)
        seen = collections.Counter(topics(co))
        self.assertEqual(seen["it_security.incident_detected"], 1, "one alert must be one incident")
        self.assertEqual(seen["executive.crisis_declared"], 1, "no crisis <-> incident feedback loop")
        self.assertEqual(seen["it_security.data_breach_confirmed"], 1)
        self.assertGreaterEqual(seen["legal.regulator_notification_filed"], 1)
        self.assertEqual(seen["it_security.incident_resolved"], 1)


class HiringTests(unittest.TestCase):
    def test_posted_role_becomes_a_provisioned_new_hire(self) -> None:
        co = make_company()
        posted = None
        for _ in range(400):
            co.step()
            found = [m for m in co.bus.history if m.topic == "people.job_posted"]
            if found:
                posted = found[0]
                break
        self.assertIsNotNone(posted, "no role was ever posted in 400 days")
        co.inject("external.candidate_applied", {
            "requisition_id": posted.body["requisition_id"], "candidate_id": "C-1", "candidate_name": "A. Candidate",
            "years_experience": 6, "skills_matched": ["a", "b", "c"], "skills_required": ["a", "b", "c"],
            "right_to_work": True, "expected_salary_gbp": 58000, "source": "referral"}, delay_days=3)
        co.run(150)
        seen = collections.Counter(topics(co))
        for t in ("people.offer_accepted", "people.new_hire_started", "it_security.access_provisioned",
                  "operations.workspace_ready"):
            self.assertGreater(seen[t], 0, f"missing {t}")


if __name__ == "__main__":
    unittest.main()
