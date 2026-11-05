"""Legal scenario seeds. Each function only builds Messages; the caller publishes them with Company.seed()."""

from __future__ import annotations

from core import Message, MessageBus, SimClock


def scenario_deal_won_to_contract(bus: MessageBus, clock: SimClock, deal_id: str = "DL-0001",
                                  client_id: str = "CL-0001", client_name: str = "Calder Freight Group",
                                  amount_gbp: int = 260000, tier: str = "forge_build",
                                  service_line: str = "forge", **params) -> list[Message]:
    """Lead-to-cash step 6-7: a standard-paper Forge Build is won; expect contract_drafted then contract_signed.

    Amount is the Forge Build list price (COMPANY.md §3.2).
    """
    return [bus.make_message("sales", "*", "sales.deal_won", {
        "deal_id": deal_id, "client_id": client_id, "client_name": client_name, "amount_gbp": amount_gbp,
        "service_line": service_line, "tier": tier,
        "terms": {"liability_cap_multiple": 1.0, "payment_days": 30, "ip_ownership": "standard",
                  "data_terms": "standard_dpa", "governing_law": "england_wales"}}, sim_time=clock.day)]


def scenario_non_standard_terms_escalation(bus: MessageBus, clock: SimClock, deal_id: str = "DL-0002",
                                           client_id: str = "CL-0002", client_name: str = "Harbourgate Mutual",
                                           amount_gbp: int = 650000, **params) -> list[Message]:
    """Forge Scale (£650k, COMPANY.md §3.2) with uncapped liability and full IP assignment.

    Chain: deal_approval_requested -> legal.contract_risk_flagged -> executive.deal_decision_made (approved,
    day+2) -> deal_won (day+3) -> contract_drafted -> contract_signed. Needs GC and CEO (COMPANY.md §9.3).
    """
    terms = {"uncapped_liability": True, "payment_days": 45, "ip_ownership": "client_owns_all",
             "data_terms": "standard_dpa", "governing_law": "england_wales"}
    base = {"deal_id": deal_id, "client_id": client_id, "client_name": client_name, "amount_gbp": amount_gbp,
            "service_line": "forge", "tier": "forge_scale"}
    return [
        bus.make_message("sales", "*", "sales.deal_approval_requested", {**base, "terms": terms},
                         sim_time=clock.day),
        bus.make_message("executive", "*", "executive.deal_decision_made",
                         {"deal_id": deal_id, "decision": "approved"}, sim_time=clock.day + 2),
        bus.make_message("sales", "*", "sales.deal_won", {**base, "terms": terms}, sim_time=clock.day + 3),
    ]


def scenario_personal_data_breach_72h(bus: MessageBus, clock: SimClock, incident_id: str = "INC-0001",
                                      records_affected: int = 1800, **params) -> list[Message]:
    """Security incident chain: incident_detected then data_breach_confirmed (Lumenhall as controller).

    Expect a privileged matter, a 72-hour ICO clock and legal.regulator_notification_filed within 72 hours.
    """
    return [
        bus.make_message("it_security", "*", "it_security.incident_detected", {
            "incident_id": incident_id, "severity": "high", "personal_data_involved": True,
            "summary": "Mis-sent candidate data export"}, sim_time=clock.day),
        bus.make_message("it_security", "*", "it_security.data_breach_confirmed", {
            "incident_id": incident_id, "severity": "high", "records_affected": records_affected,
            "special_category": False, "lumenhall_role": "controller", "aware_day": clock.day},
            sim_time=clock.day),
    ]


def scenario_regulation_to_policy(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Compliance chain: external.regulation_published -> regulatory_change_noted -> compliance_finding_raised
    -> operations.compliance_action_completed (day+10) -> legal.policy_update_published."""
    finding_id = params.get("finding_id", "CF-0001")
    return [
        bus.make_message("external", "legal", "external.regulation_published", {
            "regulation_id": "EU-AI-GL-2026-04", "title": "EU AI Act guidance on high-risk classification",
            "jurisdiction": "EU", "regulator": "European Commission", "effective_in_days": 75,
            "summary": "Guidelines on AI Act high-risk system classification for employment use cases"},
            sim_time=clock.day),
        bus.make_message("operations", "legal", "operations.compliance_action_completed", {
            "finding_id": finding_id, "summary": "AI use register updated"}, sim_time=clock.day + 10),
    ]


def scenario_ai_risk_review_high_risk(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Product asks for an AI risk review of a client-facing shift-allocation agent affecting workers."""
    return [bus.make_message("product", "*", "product.ai_risk_review_requested", {
        "review_id": "AIR-900", "agent_name": "Shift Allocation Agent", "client_id": "CL-0001",
        "use_case_tags": ["worker_management"], "uses_personal_data": True, "automated_decisions": True,
        "client_facing": True, "eu_exposure": False}, sim_time=clock.day)]


def scenario_overdue_invoice_dispute(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Collections ladder reaches day 60 on a disputed £90k Forge Pilot invoice (COMPANY.md §3.2, §7)."""
    base = {"invoice_id": "INV-2026-0007", "client_id": "CL-0003", "client_name": "Northvale Clinics",
            "amount_gbp": 90000, "days_overdue": 60, "disputed": True}
    return [
        bus.make_message("finance", "*", "finance.invoice_overdue", {**base, "days_overdue": 45},
                         sim_time=clock.day),
        bus.make_message("finance", "*", "finance.collections_escalated", base, sim_time=clock.day + 15),
    ]


def scenario_renewal_uplift_check(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Keep Plus renewal (£216k/yr, COMPANY.md §3.3): renewal_due, a proposal with an over-cap 9% uplift, then
    confirmation. Expect contract_drafted, contract_risk_flagged and contract_signed."""
    base = {"client_id": "CL-0001", "client_name": "Calder Freight Group", "amount_gbp": 216000,
            "tier": "keep_plus", "service_line": "keep", "contract_id": "CT-0001"}
    return [
        bus.make_message("customer_success", "*", "customer_success.renewal_due", {**base, "cpi_pct": 3.5},
                         sim_time=clock.day),
        bus.make_message("sales", "*", "sales.renewal_proposal_sent", {**base, "uplift_pct": 9.0},
                         sim_time=clock.day + 1),
        bus.make_message("customer_success", "*", "customer_success.renewal_confirmed",
                         {**base, "amount_gbp": 227880}, sim_time=clock.day + 5),
    ]


def scenario_vendor_without_dpa(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Operations asks for a vendor review; the vendor processes personal data with no DPA."""
    return [bus.make_message("operations", "*", "operations.vendor_review_requested", {
        "vendor_id": "VN-0001", "vendor_name": "Quillstream Transcription Ltd", "processes_personal_data": True,
        "has_dpa": False, "data_outside_uk_eea": True}, sim_time=clock.day)]


def scenario_security_review_and_scope_change(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Sales asks for security terms review (client wants 12h breach notice and SOC 2); delivery then requests
    a change order priced from the rate card (COMPANY.md §3.5)."""
    return [
        bus.make_message("sales", "*", "sales.security_review_requested", {
            "deal_id": "DL-0004", "client_id": "CL-0004", "requested_breach_notice_hours": 12,
            "audit_rights": "unrestricted", "certs_required": ["soc2_type2", "iso_27001"]},
            sim_time=clock.day),
        bus.make_message("delivery", "*", "delivery.scope_change_requested", {
            "engagement_id": "EN-0001", "client_id": "CL-0001", "client_name": "Calder Freight Group",
            "contract_id": "CT-0001", "days_by_level": {"senior_consultant": 10, "agent_day": 20}},
            sim_time=clock.day + 1),
    ]


SCENARIOS = {
    "deal_won_to_contract": scenario_deal_won_to_contract,
    "non_standard_terms_escalation": scenario_non_standard_terms_escalation,
    "personal_data_breach_72h": scenario_personal_data_breach_72h,
    "regulation_to_policy": scenario_regulation_to_policy,
    "ai_risk_review_high_risk": scenario_ai_risk_review_high_risk,
    "overdue_invoice_dispute": scenario_overdue_invoice_dispute,
    "renewal_uplift_check": scenario_renewal_uplift_check,
    "vendor_without_dpa": scenario_vendor_without_dpa,
    "security_review_and_scope_change": scenario_security_review_and_scope_change,
}
