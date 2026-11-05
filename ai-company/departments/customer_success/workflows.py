"""Customer Success scenario seeds. Each function only builds Messages; the caller seeds them.

Sample clients: Calder Freight Group (COMPANY.md §10) and invented fictional clients.
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock

CALDER = {"client_id": "CL-0001", "client_name": "Calder Freight Group"}


def scenario_new_keep_client_onboarding(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Calder Freight signs Keep Plus after Forge Build: deal won, contract signed, billing set up, kickoff,
    first milestone and first invoice. Exercises the lead-to-cash chain (COMPANY.md §7 / CONVENTIONS 7.2 steps 6-9)
    and SOP-CUSTOMER_SUCCESS-01. Expect a health baseline and a QBR/onboarding task set."""
    client_id = params.get("client_id", CALDER["client_id"])
    name = params.get("client_name", CALDER["client_name"])
    day = clock.day
    base = {"client_id": client_id, "client_name": name}
    return [
        bus.make_message("sales", "*", "sales.deal_won",
                         {**base, "deal_id": "DL-0001", "amount_gbp": 216000, "service_line": "keep",
                          "tier": "keep_plus", "summary": "Keep Plus retainer after Forge Build"}, sim_time=day),
        bus.make_message("legal", "*", "legal.contract_signed",
                         {**base, "contract_id": "CT-0001", "amount_gbp": 216000, "service_line": "keep",
                          "tier": "keep_plus", "term_months": 12, "start_day": day + 1}, sim_time=day + 1),
        bus.make_message("finance", "*", "finance.billing_schedule_created",
                         {**base, "contract_id": "CT-0001", "milestones": ["monthly in advance"]},
                         sim_time=day + 2),
        bus.make_message("delivery", "*", "delivery.engagement_kickoff",
                         {**base, "engagement_id": "EN-0001", "service_line": "keep", "tier": "keep_plus"},
                         sim_time=day + 3),
        bus.make_message("delivery", "*", "delivery.milestone_reached",
                         {**base, "engagement_id": "EN-0001", "milestone": "monitoring live"}, sim_time=day + 10),
        bus.make_message("finance", "*", "finance.invoice_issued",
                         {**base, "invoice_id": "INV-2026-0001", "amount_gbp": 18000}, sim_time=day + 11),
    ]


def scenario_keep_renewal_cycle(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A Keep Plus client 65 days from term end: contract signed (back-dated), renewal_due fires on the first tick,
    sales sends a proposal, and the agent confirms the renewal after the client decision window.
    Exercises the renewal leg of CONVENTIONS 7.2 step 12 (renewal_due -> renewal_proposal_sent -> renewal_confirmed).
    Pass client_decision="churn" to drive the non-renewal path instead."""
    client_id = params.get("client_id", "CL-0002")
    name = params.get("client_name", "Harrowgate Logistics Ltd")
    decision = params.get("client_decision")
    day = clock.day
    base = {"client_id": client_id, "client_name": name}
    proposal = {**base, "contract_id": "CT-0002", "amount_gbp": 226800, "service_line": "keep",
                "tier": "keep_plus"}
    if decision:
        proposal["client_decision"] = decision
    return [
        bus.make_message("legal", "*", "legal.contract_signed",
                         {**base, "contract_id": "CT-0002", "amount_gbp": 216000, "service_line": "keep",
                          "tier": "keep_plus", "term_months": 12, "start_day": day - 300}, sim_time=day),
        bus.make_message("sales", "*", "sales.renewal_proposal_sent", proposal, sim_time=day + 7),
    ]


def scenario_termination_notice_save(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """External notice of termination from a Forge client that was healthy before the notice. Starts from a subscribed
    external topic. With reason="price" the save plan succeeds; with reason="insourcing_decision" the client churns.
    Exercises SOP-CUSTOMER_SUCCESS-06 and -10 (churn_risk_flagged, then health update or client_churned)."""
    client_id = params.get("client_id", "CL-0003")
    name = params.get("client_name", "Brightwater Mutual Insurance")
    reason = params.get("reason", "price")
    day = clock.day
    base = {"client_id": client_id, "client_name": name}
    return [
        bus.make_message("sales", "*", "sales.deal_won",
                         {**base, "deal_id": "DL-0003", "amount_gbp": 260000, "service_line": "forge",
                          "tier": "forge_build"}, sim_time=day),
        bus.make_message("external", "customer_success", "external.client_notice_of_termination",
                         {**base, "reason": reason, "notice_period_days": 30,
                          "summary": f"Notice received citing {reason}"}, sim_time=day + 2),
    ]


def scenario_feedback_and_support_escalation(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Calder Freight (Keep Enterprise) sends a detractor NPS, a P1 ticket and a promoter-style expansion signal.
    Starts from external.client_feedback_submitted. Exercises feedback_received, support_escalated (delivery, product)
    and expansion_opportunity_identified, plus the health model reaction."""
    day = clock.day
    base = dict(CALDER)
    return [
        bus.make_message("legal", "*", "legal.contract_signed",
                         {**base, "contract_id": "CT-0001", "amount_gbp": 480000, "service_line": "keep",
                          "tier": "keep_enterprise", "start_day": day}, sim_time=day),
        bus.make_message("external", "customer_success", "external.client_feedback_submitted",
                         {**base, "kind": "nps", "score": 5, "text": "Agent responses slowed after the last release"},
                         sim_time=day + 1),
        bus.make_message("external", "customer_success", "external.client_feedback_submitted",
                         {**base, "kind": "support_ticket", "severity": "critical", "ticket_id": "TKT-9001",
                          "text": "Dispatch agent returning wrong depot allocations"}, sim_time=day + 2),
        bus.make_message("external", "customer_success", "external.client_feedback_submitted",
                         {**base, "kind": "nps", "score": 9, "text": "Fast recovery, team was excellent",
                          "expansion_signal": "wants a second agent for warehouse planning"}, sim_time=day + 9),
    ]


def scenario_engagement_completed_expansion(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A Forge Build completes, triggering the Keep attach recommendation and a reference request. Exercises
    CONVENTIONS 7.2 step 11 (delivery.engagement_completed) and the marketing.case_study_requested handoff."""
    client_id = params.get("client_id", "CL-0004")
    name = params.get("client_name", "Ostler Precision Manufacturing")
    day = clock.day
    base = {"client_id": client_id, "client_name": name}
    return [
        bus.make_message("sales", "*", "sales.deal_won",
                         {**base, "deal_id": "DL-0004", "amount_gbp": 260000, "service_line": "forge",
                          "tier": "forge_build"}, sim_time=day),
        bus.make_message("delivery", "*", "delivery.engagement_completed",
                         {**base, "engagement_id": "EN-0004", "service_line": "forge", "tier": "forge_build"},
                         sim_time=day + 3),
        bus.make_message("external", "customer_success", "external.client_feedback_submitted",
                         {**base, "kind": "nps", "score": 10, "text": "Delivered ahead of plan"}, sim_time=day + 8),
        bus.make_message("marketing", "customer_success", "marketing.case_study_requested",
                         {**base, "request_id": "CSR-0001", "client_consent": True}, sim_time=day + 12),
    ]


def scenario_data_breach_client_impact(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A confirmed data breach touches a Keep Plus client. Exercises the security incident chain (CONVENTIONS 7.2):
    it_security.incident_detected -> data_breach_confirmed -> incident_resolved, with customer_success owning
    client comms and churn-risk flags. Also seeds an overdue invoice to show commercial health inputs."""
    client_id = params.get("client_id", "CL-0005")
    name = params.get("client_name", "Marlowe Health Partners")
    day = clock.day
    base = {"client_id": client_id, "client_name": name}
    incident = {"incident_id": "INC-0001", "affected_client_ids": [client_id], "severity": "critical",
                "personal_data": True}
    return [
        bus.make_message("legal", "*", "legal.contract_signed",
                         {**base, "contract_id": "CT-0005", "amount_gbp": 216000, "service_line": "keep",
                          "tier": "keep_plus", "start_day": day}, sim_time=day),
        bus.make_message("it_security", "*", "it_security.incident_detected", incident, sim_time=day + 1),
        bus.make_message("it_security", "*", "it_security.data_breach_confirmed", incident, sim_time=day + 2),
        bus.make_message("finance", "*", "finance.invoice_overdue",
                         {**base, "invoice_id": "INV-2026-0042", "days_overdue": 38, "amount_gbp": 18000},
                         sim_time=day + 3),
        bus.make_message("it_security", "*", "it_security.incident_resolved", incident, sim_time=day + 6),
        bus.make_message("finance", "*", "finance.payment_received",
                         {**base, "invoice_id": "INV-2026-0042", "amount_gbp": 18000}, sim_time=day + 8),
    ]


SCENARIOS = {
    "new_keep_client_onboarding": scenario_new_keep_client_onboarding,
    "keep_renewal_cycle": scenario_keep_renewal_cycle,
    "termination_notice_save": scenario_termination_notice_save,
    "feedback_and_support_escalation": scenario_feedback_and_support_escalation,
    "engagement_completed_expansion": scenario_engagement_completed_expansion,
    "data_breach_client_impact": scenario_data_breach_client_impact,
}
