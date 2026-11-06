"""Operations department scenarios (Lumenhall Partners).

Each ``scenario_*`` function only builds Messages with ``bus.make_message``; the caller seeds them with
``Company.seed``. Thresholds follow ``sops.md`` (three quotes from GBP 2,500, vendor review from GBP 10,000 a year or
for data, system access and AI vendors, approval ladder 0/2/3/5/7 days), COMPANY.md 9.3 and 9.4. Vendors, people and
amounts are fictional (COMPANY.md section 10). Body keys match what the producing departments really send.
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock


def scenario_small_orders_and_logistics(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Low-value spend is released at once; larger event and engagement spend opens an RFQ.

    Expected chain: external.vendor_quote_received (1,800, new vendor below every review trigger) ->
    operations.procurement_order_placed (level 1, same day); marketing.event_scheduled (below 2,500) -> immediate
    event PO to the panel venue; delivery.staffing_requested drives the kit forecast.
    """
    d = clock.day
    amount = params.get("amount_gbp", 1800)
    return [
        bus.make_message("external", "operations", "external.vendor_quote_received", {
            "quote_id": "Q-2026-0101", "vendor_id": "VN-0201", "vendor_name": "Aldwych Office Interiors",
            "amount_gbp": amount, "term_months": 12, "valid_until_day": d + 30, "category": "facilities",
            "department": "operations", "budgeted": True,
            "summary": "Quote for ergonomic task chairs for the Shoreditch floor"}, sim_time=d),
        bus.make_message("marketing", "operations", "marketing.event_scheduled", {
            "event_id": "EVT-0101", "event_type": "client_roundtable", "city": "London", "capacity": 20,
            "due_day": d + 40, "estimated_cost_gbp": 2100, "needs": ["venue_booking", "catering"],
            "summary": "Small client roundtable in London"}, sim_time=d + 2),
        bus.make_message("delivery", "operations", "delivery.staffing_requested", {
            "engagement_id": "EN-0101", "client_id": "CL-0101", "tier": "forge_build",
            "team": [{"level": "consultant", "fte": 2.0}], "needed_by_day": d + 10,
            "shortfall_fte": {"consultant": 2}, "sourcing": "hire or subcontractor",
            "summary": "Staff a Forge Build engagement; two consultants short"}, sim_time=d + 3),
    ]


def scenario_competitive_sourcing_vendor_review(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Three quotes for an AI platform; the winner needs a vendor review before the order is placed.

    Expected chain: three external.vendor_quote_received on one rfq_id -> operations.vendor_review_requested
    (legal, it_security, finance); it_security.vendor_risk_assessed -> operations.vendor_approved (finance,
    it_security) -> operations.procurement_order_placed after the level-3 approval SLA (18,000 to 30,000).
    """
    d = clock.day
    rfq = params.get("rfq_id", "RFQ-2026-0900")
    quotes = (("Q-2026-0201", "VN-0202", "Marlowe Analytics Cloud", 26000, 30), ("Q-2026-0202", "VN-0203",
              "Kestrel Model Platform", 28500, 32), ("Q-2026-0203", "VN-0204", "Tamarind Data Systems", 31000, 35))
    msgs = [bus.make_message("external", "operations", "external.vendor_quote_received", {
        "quote_id": qid, "rfq_id": rfq, "vendor_id": vid, "vendor_name": name, "amount_gbp": amt, "term_months": 12,
        "valid_until_day": d + valid + 20, "category": "ai_platform", "department": "delivery", "budgeted": True,
        "processes_personal_data": True, "ai_platform": True, "has_dpa": True, "data_outside_uk_eea": False,
        "fit_score": 85 - 3 * i, "risk_score": 80, "terms_score": 70,
        "summary": f"{name} quote for an annual AI platform licence"}, sim_time=d + 1 + 2 * i)
        for i, (qid, vid, name, amt, valid) in enumerate(quotes)]
    msgs.append(bus.make_message("it_security", "operations", "it_security.vendor_risk_assessed", {
        "vendor_id": "VN-0202", "vendor_name": "Marlowe Analytics Cloud", "tier": 1, "risk_rating": "medium",
        "decision": "approve_with_conditions", "conditions": ["SSO and SCIM enforced before go-live",
                                                              "no training on Lumenhall or client data"],
        "reassess_day": d + 400, "severity": "medium", "service": "ai_platform", "due_day": d + 12},
        sim_time=d + params.get("assessed_after", 12)))
    return msgs


def scenario_new_starters_and_stock_out(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Eight starters in three days exhaust the kit pool; late starters wait for the 2-day kit lead time.

    Expected chain: people.new_hire_started + it_security.access_provisioned -> operations.workspace_ready (people)
    on the same day (on_time true) or after 2 days (on_time false) on a stock-out, with laptop orders charged to
    it_security through operations.procurement_order_placed (finance).
    """
    d = clock.day
    n = params.get("starters", 8)
    msgs: list[Message] = []
    for i in range(n):
        eid = f"EMP-{100 + i:04d}"
        start = d + 1 + i // 3
        msgs.append(bus.make_message("it_security", "operations", "it_security.access_provisioned", {
            "employee_id": eid, "department": "delivery", "role": "Consultant", "access_bundle": "delivery_baseline",
            "device_compliant": True, "within_sla": True, "exceptions": [], "due_day": start + 30},
            sim_time=start - 1 if i < 3 else d + 1))
        msgs.append(bus.make_message("people", "operations", "people.new_hire_started", {
            "employee_id": eid, "requisition_id": f"REQ-{100 + i:04d}", "employee_name": f"Starter {i + 1}",
            "department": "delivery", "role": "Consultant", "level": "consultant", "start_day": start,
            "needs": ["laptop", "workspace", "access_provisioning", "payroll_setup"], "access_profile": "delivery",
            "right_to_work_verified": True, "summary": f"Day one for starter {i + 1}"}, sim_time=start))
    return msgs


def scenario_leaver_and_backfill(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """An Operations analyst resigns: asset recovery, desk release and a backfill request.

    Expected chain: people.employee_left -> recovery checklist and, because the leaver is in operations,
    operations.hire_requested (people) with reason backfill; no topic for the asset recovery itself.
    """
    d = clock.day
    return [bus.make_message("people", "operations", "people.employee_left", {
        "employee_id": "EMP-0031", "department": "operations", "role": "Operations Analyst", "level": "analyst",
        "reason": "resignation", "voluntary": True, "last_day": d + 21, "notice_period_days": 21,
        "revoke_access_by_day": d + 21, "involuntary": False, "summary": "Operations analyst leaves on day "
        f"{d + 21}"}, sim_time=d)]


def scenario_compliance_finding_to_closure(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A high finding becomes an owned action and is closed only after a (modelled) human attestation.

    Expected chain: legal.compliance_finding_raised (high, due in 20 days) -> action due in 14 days (HIGH SLA);
    after the attestation operations.compliance_action_completed (legal) with closed_day and on_time. A regulatory
    change and a policy update are aligned in parallel (no topic).
    """
    d = clock.day
    return [
        bus.make_message("legal", "operations", "legal.compliance_finding_raised", {
            "finding_id": params.get("finding_id", "CF-0101"), "severity": "high",
            "title": "Supplier contracts lack UK GDPR Article 28 terms", "areas": ["data_protection"],
            "action_owner": "operations", "due_day": d + 20,
            "summary": "Update supplier contract templates and chase signed DPAs for processors"}, sim_time=d),
        bus.make_message("legal", "operations", "legal.regulatory_change_noted", {
            "regulation_id": "REG-0101", "title": "Data (Use and Access) Act commencement order",
            "jurisdiction": "UK", "impact_areas": ["data_protection"], "owners": ["it_security", "operations"],
            "effective_in_days": 90, "severity": "high", "policy_update_likely": True,
            "summary": "Data protection changes affecting supplier records"}, sim_time=d + 2),
        bus.make_message("legal", "operations", "legal.policy_update_published", {
            "policy_id": "POL-0101", "title": "Supplier data protection policy", "version": "v2",
            "effective_day": d + 30, "training_required": True, "audiences": ["all_staff"],
            "summary": "Supplier due diligence and processor terms"}, sim_time=d + 5),
    ]


def scenario_incident_and_continuity(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A critical incident, a crisis declaration and a resolution that misses the Tier-1 RTO.

    Expected chain: it_security.incident_detected (critical) -> continuity logistics; executive.crisis_declared;
    it_security.incident_resolved (6 hours against the 4-hour Tier-1 RTO) -> operations.continuity_test_completed
    (executive, it_security) with rto_met false; it_security.vulnerability_found for a printer firmware flaw ->
    replacement order for it_security.
    """
    d = clock.day
    hours = params.get("restore_hours", 6.0)
    return [
        bus.make_message("it_security", "operations", "it_security.incident_detected", {
            "incident_id": "INC-0101", "severity": "critical", "summary": "Ransomware on the engagement workspace",
            "personal_data_involved": False, "containment_status": "containment_in_progress",
            "incident_commander": "Chief Information Security Officer", "due_day": d, "category": "ransomware"},
            sim_time=d),
        bus.make_message("executive", "operations", "executive.crisis_declared", {
            "crisis_id": "CRS-0101", "category": "cyber", "severity": "critical", "incident_id": "INC-0101",
            "summary": "Crisis declared after ransomware on the engagement workspace",
            "commander": "Chief Executive Officer", "declared_day": d + 1}, sim_time=d + 1),
        bus.make_message("it_security", "operations", "it_security.incident_resolved", {
            "incident_id": "INC-0101", "severity": "critical", "summary": "Ransomware contained and restored",
            "root_cause": "Phished credentials without MFA", "time_to_contain_hours": 3.0,
            "time_to_resolve_hours": hours, "follow_up_actions": 3, "due_day": d + 7}, sim_time=d + 3),
        bus.make_message("it_security", "operations", "it_security.vulnerability_found", {
            "vulnerability_id": "VULN-0101", "severity": "high", "summary": "Meeting-room printer firmware flaw",
            "component": "printer firmware", "cvss": 8.1, "exploited_in_wild": False, "due_day": d + 14},
            sim_time=d + 4),
    ]


def scenario_process_and_budget_cycle(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Recurring data defects become a published process improvement; the budget cycle runs to approval.

    Expected chain: data.data_quality_issue_raised (critical) -> operations.process_improvement_proposed
    (executive); executive.okrs_set + strategy_updated -> programme portfolio; finance.budget_cycle_opened ->
    operations.budget_submitted on day 21 (finance); executive.budget_approved loads the budget.
    """
    d = clock.day
    return [
        bus.make_message("data", "operations", "data.data_quality_issue_raised", {
            "issue_id": "DQ-0101", "severity": "critical", "check": "schema", "dataset": "finance.invoice_issued",
            "source_department": "finance", "department": "finance", "due_day": d + 5,
            "summary": "Invoice records repeatedly rejected for missing PO references"}, sim_time=d),
        bus.make_message("executive", "operations", "executive.okrs_set", {
            "summary": "FY2027 OKRs", "okrs": ["us_launch_ready", "iso_27001_certified", "workspace_ready_97pct"]},
            sim_time=d + 3),
        bus.make_message("executive", "operations", "executive.strategy_updated", {
            "summary": "Board confirms New York office opening", "severity": "medium"}, sim_time=d + 6),
        bus.make_message("finance", "operations", "finance.budget_cycle_opened", {
            "budget_cycle_id": "BUD-2027", "fiscal_year": 2027, "deadline_day": d + 10 + 21}, sim_time=d + 10),
        bus.make_message("executive", "operations", "executive.budget_approved", {
            "budget_id": "BUD-2027", "fiscal_year": 2027, "status": "approved"}, sim_time=d + 45),
    ]


SCENARIOS = {
    "small_orders_and_logistics": scenario_small_orders_and_logistics,
    "competitive_sourcing_vendor_review": scenario_competitive_sourcing_vendor_review,
    "new_starters_and_stock_out": scenario_new_starters_and_stock_out,
    "leaver_and_backfill": scenario_leaver_and_backfill,
    "compliance_finding_to_closure": scenario_compliance_finding_to_closure,
    "incident_and_continuity": scenario_incident_and_continuity,
    "process_and_budget_cycle": scenario_process_and_budget_cycle,
}
