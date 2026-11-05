"""Delivery department scenarios (Lumenhall Partners).

Each ``scenario_*`` function only builds Messages with ``bus.make_message``; the caller seeds them with
``Company.seed``. Prices follow COMPANY.md section 3 and billing follows section 9 (30/40/30 milestones).
Sample clients are fictional (COMPANY.md section 10).
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock


def scenario_proposal_scoping(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Sales asks delivery to scope a Forge Build for Calder Freight Group.

    Expected chain: sales.proposal_requested -> delivery.scoping_completed (sales, finance) and a
    staffing view; finance then runs its pricing check.
    """
    d = clock.day
    body = {
        "client_id": params.get("client_id", "CL-0001"),
        "client_name": params.get("client_name", "Calder Freight Group"),
        "deal_id": params.get("deal_id", "DL-0001"),
        "proposal_id": params.get("proposal_id", "PR-0001"),
        "service_line": "forge",
        "tier": params.get("tier", "forge_build"),
        "amount_gbp": params.get("amount_gbp", 260000),
        "summary": "Forge Build: dispatch exception triage, proof-of-delivery matching and carrier "
                   "invoice reconciliation agents integrated with the client TMS; 5 months",
        "due_day": d + 5,
    }
    return [bus.make_message("sales", "delivery", "sales.proposal_requested", body, sim_time=d)]


def scenario_deal_won_to_kickoff(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A Forge Pilot is won, the contract is signed and billing is set up.

    Expected chain: sales.deal_won + legal.contract_signed + finance.billing_schedule_created ->
    delivery.staffing_requested (people, operations) -> delivery.engagement_kickoff, then milestones.
    """
    d = clock.day
    common = {
        "client_id": params.get("client_id", "CL-0002"),
        "client_name": params.get("client_name", "Harbourline Insurance Brokers"),
        "deal_id": params.get("deal_id", "DL-0002"),
        "service_line": "forge",
        "tier": params.get("tier", "forge_pilot"),
        "amount_gbp": params.get("amount_gbp", 90000),
    }
    won = dict(common, summary="Forge Pilot won: claims-intake triage agent for one 40-person team, "
                               "10 weeks, start in 2 weeks", due_day=d + 14)
    signed = dict(common, contract_id=params.get("contract_id", "CT-0002"),
                  summary="MSA and SOW signed; fixed fee, 30/40/30 milestone billing")
    billing = dict(common, contract_id=params.get("contract_id", "CT-0002"),
                   engagement_id=params.get("engagement_id", "EN-0002"),
                   invoice_id="INV-2026-0002",
                   summary="Billing schedule: 30% on signature (£27,000), 40% mid-point (£36,000), "
                           "30% on acceptance (£27,000)")
    return [
        bus.make_message("sales", "delivery", "sales.deal_won", won, sim_time=d),
        bus.make_message("legal", "delivery", "legal.contract_signed", signed, sim_time=d + 2),
        bus.make_message("finance", "delivery", "finance.billing_schedule_created", billing, sim_time=d + 3),
    ]


def scenario_client_scope_change(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Client asks for extra work mid-engagement, which should become a priced change order.

    Expected chain: external.client_scope_request -> delivery.scope_change_requested (sales, finance, legal),
    priced at the COMPANY.md section 3.5 rate card.
    """
    d = clock.day
    body = {
        "client_id": params.get("client_id", "CL-0001"),
        "client_name": params.get("client_name", "Calder Freight Group"),
        "engagement_id": params.get("engagement_id", "EN-0001"),
        "service_line": "forge",
        "tier": "forge_build",
        "summary": "Client COO asks to add a customs-documentation agent and two further depots to scope; "
                   "est. 24 consultant-days plus 30 agent-days",
        "requested_days": params.get("requested_days", 24),
        "agent_days": params.get("agent_days", 30),
        "amount_gbp": params.get("amount_gbp", 24 * 800 + 30 * 350),
        "severity": "medium",
        "due_day": d + 7,
    }
    return [bus.make_message("external", "delivery", "external.client_scope_request", body, sim_time=d)]


def scenario_quality_escalation(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """An agent quality regression and a client support escalation hit one live engagement.

    Expected chain: data.agent_quality_report_published + customer_success.support_escalated ->
    delivery.quality_issue_raised (customer_success, executive), remediation tasks, human review.
    """
    d = clock.day
    cid = params.get("client_id", "CL-0003")
    cname = params.get("client_name", "Fenwick Precision Components")
    eid = params.get("engagement_id", "EN-0003")
    report = {
        "client_id": cid, "client_name": cname, "engagement_id": eid, "service_line": "forge",
        "summary": "Weekly agent quality report: supplier-quality triage agent accuracy fell from 94% to 86% "
                   "after an ERP schema change; below the 92% release threshold",
        "metric": "accuracy", "value": 0.86, "threshold": 0.92, "severity": "high",
    }
    escalation = {
        "client_id": cid, "client_name": cname, "engagement_id": eid, "service_line": "forge",
        "summary": "Client quality director reports 17 misrouted non-conformance reports in 3 days and "
                   "asks for a root-cause review before the mid-point milestone",
        "severity": "high", "due_day": d + 3,
    }
    return [
        bus.make_message("data", "delivery", "data.agent_quality_report_published", report, sim_time=d),
        bus.make_message("customer_success", "delivery", "customer_success.support_escalated", escalation,
                         sim_time=d + 1),
    ]


def scenario_capacity_crunch(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Several wins land together while the pipeline forecast rises, stressing staffing capacity.

    Expected chain: sales.deal_won x3 + data.forecast_updated -> delivery.staffing_requested (people,
    operations) and delivery.capacity_forecast_updated (sales, people, executive, finance).
    """
    d = clock.day
    wins = [
        ("CL-0004", "Marlowe & Teague Legal LLP", "DL-0004", "compass", "compass_sprint", 120000),
        ("CL-0005", "Brightwater Health Services", "DL-0005", "forge", "forge_build", 260000),
        ("CL-0006", "Northgate Retail Holdings", "DL-0006", "forge", "forge_scale", 650000),
    ]
    msgs = [
        bus.make_message("sales", "delivery", "sales.deal_won", {
            "client_id": cid, "client_name": name, "deal_id": did, "service_line": line, "tier": tier,
            "amount_gbp": amt, "summary": f"{tier.replace('_', ' ').title()} won, start within 3 weeks",
            "due_day": d + 21}, sim_time=d + i)
        for i, (cid, name, did, line, tier, amt) in enumerate(wins)
    ]
    msgs.append(bus.make_message("data", "delivery", "data.forecast_updated", {
        "summary": "Pipeline forecast raised: weighted delivery demand 14% above bench capacity for the next "
                   "two quarters, mainly Senior Consultant and Manager hours",
        "demand_gap_pct": params.get("demand_gap_pct", 14), "severity": "medium"}, sim_time=d + 3))
    return msgs


def scenario_security_incident_on_client_work(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A security incident touches a live client engagement, then the client sends a dispute notice.

    Expected chain: it_security.incident_detected -> delivery pauses affected agent runs and flags quality;
    legal.client_dispute_raised -> delivery gathers evidence and may raise delivery.quality_issue_raised.
    """
    d = clock.day
    cid = params.get("client_id", "CL-0001")
    cname = params.get("client_name", "Calder Freight Group")
    eid = params.get("engagement_id", "EN-0001")
    incident = {
        "incident_id": "INC-0001", "severity": params.get("severity", "high"),
        "summary": "Leaked API token for the engagement sandbox found in a public code snippet; "
                   "token revoked, client TMS test data may have been queried",
        "client_id": cid, "client_name": cname, "engagement_id": eid,
    }
    dispute = {
        "client_id": cid, "client_name": cname, "engagement_id": eid, "contract_id": "CT-0001",
        "summary": "Client general counsel disputes the mid-point milestone invoice, citing the sandbox "
                   "incident and delayed acceptance testing",
        "amount_gbp": 104000, "severity": "high", "due_day": d + 10,
    }
    return [
        bus.make_message("it_security", "delivery", "it_security.incident_detected", incident, sim_time=d),
        bus.make_message("legal", "delivery", "legal.client_dispute_raised", dispute, sim_time=d + 4),
    ]


def scenario_churn_risk_recovery(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Customer success flags churn risk on a Keep retainer, then reports a falling health score.

    Expected chain: customer_success.churn_risk_flagged + health_score_updated -> delivery recovery plan,
    possibly delivery.quality_issue_raised; later renewal_confirmed returns the account to steady state.
    """
    d = clock.day
    cid = params.get("client_id", "CL-0007")
    cname = params.get("client_name", "Aldersgate Wealth Partners")
    base = {"client_id": cid, "client_name": cname, "service_line": "keep", "tier": "keep_plus"}
    return [
        bus.make_message("customer_success", "delivery", "customer_success.churn_risk_flagged", dict(
            base, summary="Sponsor changed; new COO questions retainer value after two missed agent SLAs",
            amount_gbp=216000, severity="high", due_day=d + 14), sim_time=d),
        bus.make_message("customer_success", "delivery", "customer_success.health_score_updated", dict(
            base, summary="Health score fell from 78 to 54 in 30 days", health_score=54, previous_score=78),
            sim_time=d + 1),
        bus.make_message("customer_success", "delivery", "customer_success.renewal_confirmed", dict(
            base, summary="Renewal confirmed for 12 months after recovery plan and executive review",
            amount_gbp=216000), sim_time=d + 30),
    ]


SCENARIOS = {
    "proposal_scoping": scenario_proposal_scoping,
    "deal_won_to_kickoff": scenario_deal_won_to_kickoff,
    "client_scope_change": scenario_client_scope_change,
    "quality_escalation": scenario_quality_escalation,
    "capacity_crunch": scenario_capacity_crunch,
    "security_incident_on_client_work": scenario_security_incident_on_client_work,
    "churn_risk_recovery": scenario_churn_risk_recovery,
}
