"""Canonical cross-department topic map (binding; mirrored in CONVENTIONS.md).

TOPIC_SUBSCRIBERS maps ``<publisher>.<event>`` -> tuple of subscriber department ids.
The publisher is always the topic prefix.
"""

from __future__ import annotations

from .company import DEPARTMENTS


def _others(dept: str) -> tuple[str, ...]:
    return tuple(d for d in DEPARTMENTS if d != dept)


_BASE: dict[str, tuple[str, ...]] = {
    # --- executive ---
    "executive.strategy_updated": _others("executive"),
    "executive.okrs_set": _others("executive"),
    "executive.budget_approved": _others("executive"),
    "executive.headcount_approved": ("people", "finance"),
    "executive.deal_decision_made": ("sales", "finance", "legal"),
    "executive.pricing_change_approved": ("sales", "finance", "marketing", "product"),
    "executive.crisis_declared": _others("executive"),
    "executive.board_meeting_held": ("finance", "legal", "data"),
    # --- marketing ---
    "marketing.lead_generated": ("sales", "data"),
    "marketing.campaign_launched": ("sales", "finance", "data"),
    "marketing.content_published": ("sales",),
    "marketing.case_study_requested": ("customer_success",),
    "marketing.event_scheduled": ("sales", "operations"),
    "marketing.brand_incident_raised": ("executive", "legal"),
    # --- sales ---
    "sales.lead_qualified": ("marketing", "delivery", "data"),
    "sales.proposal_requested": ("delivery", "finance"),
    "sales.security_review_requested": ("it_security", "legal"),
    "sales.deal_approval_requested": ("executive", "finance", "legal"),
    "sales.proposal_sent": ("executive", "data"),
    "sales.deal_won": ("legal", "finance", "delivery", "customer_success", "executive", "data"),
    "sales.deal_lost": ("marketing", "executive", "data"),
    "sales.renewal_proposal_sent": ("customer_success", "finance", "legal"),
    # --- legal ---
    "legal.contract_drafted": ("sales",),
    "legal.contract_signed": ("finance", "delivery", "sales", "customer_success"),
    "legal.contract_risk_flagged": ("sales", "executive"),
    "legal.security_terms_reviewed": ("sales",),
    "legal.regulatory_change_noted": ("executive", "it_security", "people", "operations", "data", "product"),
    "legal.compliance_finding_raised": ("executive", "operations"),
    "legal.regulator_notification_filed": ("executive", "it_security"),
    "legal.client_dispute_raised": ("finance", "delivery", "customer_success", "executive"),
    "legal.ai_risk_review_completed": ("product", "executive", "data"),
    "legal.policy_update_published": ("people", "operations", "it_security"),
    # --- delivery ---
    "delivery.scoping_completed": ("sales", "finance"),
    "delivery.staffing_requested": ("people", "operations"),
    "delivery.engagement_kickoff": ("customer_success", "finance", "operations", "data"),
    "delivery.milestone_reached": ("finance", "customer_success"),
    "delivery.engagement_completed": ("finance", "customer_success", "sales", "data"),
    "delivery.capacity_forecast_updated": ("sales", "people", "executive", "finance"),
    "delivery.quality_issue_raised": ("customer_success", "executive"),
    "delivery.scope_change_requested": ("sales", "finance", "legal"),
    # --- finance ---
    "finance.pricing_check_completed": ("sales",),
    "finance.billing_schedule_created": ("delivery", "customer_success"),
    "finance.invoice_issued": ("customer_success", "data"),
    "finance.payment_received": ("sales", "customer_success", "data"),
    "finance.invoice_overdue": ("customer_success", "legal", "sales"),
    "finance.collections_escalated": ("legal", "executive"),
    "finance.budget_cycle_opened": _others("finance"),
    "finance.budget_consolidated": ("executive",),
    "finance.budget_variance_flagged": ("executive",),
    "finance.cash_forecast_updated": ("executive", "data"),
    "finance.month_end_closed": ("executive", "data"),
    # --- customer_success ---
    "customer_success.health_score_updated": ("delivery", "sales", "data"),
    "customer_success.renewal_due": ("sales", "finance", "legal"),
    "customer_success.renewal_confirmed": ("finance", "legal", "sales", "delivery", "data"),
    "customer_success.churn_risk_flagged": ("sales", "delivery", "executive"),
    "customer_success.client_churned": ("finance", "sales", "executive", "data"),
    "customer_success.expansion_opportunity_identified": ("sales",),
    "customer_success.feedback_received": ("delivery", "product", "marketing"),
    "customer_success.case_study_approved": ("marketing",),
    "customer_success.support_escalated": ("delivery", "product"),
    # --- people ---
    "people.requisition_opened": ("executive", "finance"),
    "people.job_posted": ("marketing",),
    "people.offer_accepted": ("finance", "legal"),
    "people.new_hire_started": ("it_security", "operations", "finance", "delivery"),
    "people.employee_left": ("it_security", "finance", "operations", "legal"),
    "people.contractor_engaged": ("finance", "legal", "it_security"),
    "people.engagement_survey_completed": ("executive", "delivery"),
    "people.compliance_training_completed": ("legal", "it_security"),
    # --- it_security ---
    "it_security.incident_detected": ("executive", "legal", "operations", "customer_success", "delivery"),
    "it_security.data_breach_confirmed": ("legal", "executive", "customer_success"),
    "it_security.incident_resolved": ("executive", "legal", "customer_success", "operations"),
    "it_security.access_provisioned": ("people", "operations"),
    "it_security.access_revoked": ("people", "legal"),
    "it_security.vulnerability_found": ("product", "operations"),
    "it_security.certification_status_updated": ("legal", "sales", "executive"),
    "it_security.security_questionnaire_completed": ("sales", "legal"),
    "it_security.vendor_risk_assessed": ("operations", "legal", "finance"),
    # --- operations ---
    "operations.vendor_review_requested": ("legal", "it_security", "finance"),
    "operations.vendor_approved": ("finance", "it_security"),
    "operations.workspace_ready": ("people",),
    "operations.process_improvement_proposed": ("executive",),
    "operations.continuity_test_completed": ("executive", "it_security"),
    "operations.procurement_order_placed": ("finance",),
    "operations.compliance_action_completed": ("legal",),
    # --- product ---
    "product.release_shipped": ("delivery", "customer_success", "marketing", "it_security"),
    "product.agent_capability_added": ("delivery", "sales", "marketing"),
    "product.roadmap_published": ("executive", "sales", "delivery", "marketing"),
    "product.ai_risk_review_requested": ("legal", "it_security", "data"),
    "product.pricing_change_proposed": ("finance", "sales", "executive"),
    "product.vulnerability_fixed": ("it_security",),
    # --- data ---
    "data.kpi_report_published": ("executive", "finance"),
    "data.forecast_updated": ("sales", "finance", "delivery", "executive"),
    "data.data_quality_issue_raised": ("operations", "product"),
    "data.agent_quality_report_published": ("product", "delivery", "executive"),
    "data.benchmark_ready": ("delivery", "marketing"),
}

# Every department submits a budget and may request hires.
_GENERATED: dict[str, tuple[str, ...]] = {}
for _d in DEPARTMENTS:
    _GENERATED[f"{_d}.budget_submitted"] = ("finance",) if _d != "finance" else ("executive",)
    _GENERATED[f"{_d}.hire_requested"] = ("people",) if _d != "people" else ("executive",)

TOPIC_SUBSCRIBERS: dict[str, tuple[str, ...]] = {**_BASE, **_GENERATED}

# Events from outside the company (clients, candidates, regulators...). Entry points for scenarios.
# Publisher is always the pseudo-sender "external".
EXTERNAL_TOPICS: dict[str, tuple[str, ...]] = {
    "external.lead_inbound": ("marketing",),
    "external.rfp_received": ("sales",),
    "external.client_scope_request": ("delivery",),
    "external.client_payment_received": ("finance",),
    "external.client_notice_of_termination": ("customer_success",),
    "external.client_feedback_submitted": ("customer_success",),
    "external.candidate_applied": ("people",),
    "external.security_alert": ("it_security",),
    "external.regulation_published": ("legal",),
    "external.vendor_quote_received": ("operations",),
    "external.market_data_published": ("data",),
    "external.technology_release_published": ("product",),
    "external.board_request": ("executive",),
}


def publisher_of(topic: str) -> str:
    return topic.split(".", 1)[0]


def publishes_for(dept: str) -> tuple[str, ...]:
    return tuple(sorted(t for t in TOPIC_SUBSCRIBERS if publisher_of(t) == dept))


def subscribes_for(dept: str) -> tuple[str, ...]:
    allmap = {**TOPIC_SUBSCRIBERS, **EXTERNAL_TOPICS}
    return tuple(sorted(t for t, subs in allmap.items() if dept in subs))


def validate_topic_map() -> list[str]:
    """Return a list of problems (empty when the map is consistent)."""
    problems = []
    for topic, subs in TOPIC_SUBSCRIBERS.items():
        if publisher_of(topic) not in DEPARTMENTS:
            problems.append(f"{topic}: unknown publisher")
        if not subs:
            problems.append(f"{topic}: no subscribers")
        for s in subs:
            if s not in DEPARTMENTS:
                problems.append(f"{topic}: unknown subscriber {s}")
            if s == publisher_of(topic):
                problems.append(f"{topic}: publisher subscribes to itself")
    for topic, subs in EXTERNAL_TOPICS.items():
        if publisher_of(topic) != "external" or any(x not in DEPARTMENTS for x in subs):
            problems.append(f"{topic}: bad external topic")
    for d in DEPARTMENTS:
        if not publishes_for(d):
            problems.append(f"{d}: publishes nothing")
        if not subscribes_for(d):
            problems.append(f"{d}: subscribes to nothing")
    return problems
