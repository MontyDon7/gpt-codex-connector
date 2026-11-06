"""Product department scenarios (Lumenhall Partners).

Each ``scenario_*`` function only builds Messages with ``bus.make_message``; the caller seeds them with
``Company.seed``. Figures are modelled assumptions: prices follow COMPANY.md section 3 (agent-day rate 350, section
3.5), budget envelopes follow COMPANY.md section 5.4 (Product FY2027 620k, FY2028 1,960k) and gate thresholds follow
the "Constants and thresholds" table in sops.md. Clients are fictional (COMPANY.md section 10).
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock


def scenario_quarterly_roadmap_planning(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """The CEO sets OKRs and then shifts strategy; Product re-scores the backlog and republishes the roadmap.

    Expected chain: executive.okrs_set -> product.roadmap_published (executive, sales, delivery, marketing);
    executive.strategy_updated (US launch) -> a re-planned product.roadmap_published and a pricing review.
    """
    d = clock.day
    return [
        bus.make_message("executive", "product", "executive.okrs_set", {
            "quarter": params.get("quarter", "FY2026 Q2"),
            "objectives": ["Ship 6 reusable agent capabilities in FY2026", "Reach 40% platform reuse on Forge",
                           "Keep open critical findings at zero"],
            "summary": "Company OKRs for the quarter: capability shipping, reuse and agent quality"},
            sim_time=d),
        bus.make_message("executive", "product", "executive.strategy_updated", {
            "summary": "Board approves US launch from Q1 FY2027: data residency and USD price list needed",
            "objectives": ["US data-residency option for Keep agents"], "severity": "medium"},
            sim_time=d + 9),
    ]


def scenario_stage_gated_release_with_risk_review(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A client-facing capability that widens tool permissions needs an AI risk review before it ships.

    Expected chain: executive.okrs_set -> product.roadmap_published; the committed item passes G1 to G4 on the
    14-day release train; RT-1 raises product.ai_risk_review_requested (legal, it_security, data);
    legal.ai_risk_review_completed arrives marked pending General Counsel sign-off, so the release stays held until
    sign-off (about 3 days) and only then does product.release_shipped and product.agent_capability_added follow.
    """
    d = clock.day
    review_id = params.get("review_id", "AIR-0001")
    return [
        bus.make_message("executive", "product", "executive.okrs_set", {
            "quarter": "FY2026 Q2",
            "objectives": ["Client-facing support triage agent for Keep with ticket-update permission"],
            "summary": "OKR: widen the Keep support agent to update tickets (new tool permission, RT-1)"},
            sim_time=d),
        bus.make_message("legal", "product", "legal.ai_risk_review_completed", {
            "review_id": review_id, "agent_name": params.get("agent_name", "Keep support triage agent"),
            "client_id": params.get("client_id", "CL-0007"), "risk_tier": "limited",
            "recommendation": "cleared_with_conditions", "conditions": ["Human approval for ticket closure",
                                                                         "Log retention 12 months"],
            "dpia_required": False, "status": "recommendation_pending_gc_signoff", "severity": "low",
            "summary": f"AI risk review {review_id}: limited risk, 2 conditions, pending General Counsel sign-off"},
            sim_time=d + params.get("legal_reply_day", 35)),
    ]


def scenario_feedback_cluster_and_hotfix(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Three clients report the same extraction defect and one escalation is high severity.

    Expected chain: customer_success.feedback_received x3 -> feedback cluster (3 distinct clients) and a RICE-scored
    backlog item; customer_success.support_escalated (high, defect) -> triage in 1 business day and a hotfix
    product.release_shipped (hotfix); no product.* message contacts the client directly.
    """
    d = clock.day
    agent = params.get("agent", "invoice-extraction agent")
    msgs = []
    for i, (cid, cname) in enumerate([("CL-0003", "Calder Freight Group"), ("CL-0005", "Fenwick Precision Components"),
                                      ("CL-0008", "Northgate Retail Holdings")]):
        msgs.append(bus.make_message("customer_success", "product", "customer_success.feedback_received", {
            "client_id": cid, "client_name": cname, "agent": agent, "category": "defect", "score": 2,
            "summary": f"{agent} misreads multi-currency totals on supplier invoices",
            "severity": "medium"}, sim_time=d + i * 3))
    msgs.append(bus.make_message("customer_success", "product", "customer_success.support_escalated", {
        "client_id": "CL-0003", "client_name": "Calder Freight Group", "engagement_id": "EN-0003",
        "agent": agent, "category": "defect", "severity": "high", "ticket_id": "SUP-0412",
        "summary": f"Defect: {agent} posted wrong totals to the ledger for two days; client finance is blocked"},
        sim_time=d + 10))
    return msgs


def scenario_vulnerability_and_quality_regression(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A critical exploited vulnerability arrives while an agent's quality score falls below the freeze line.

    Expected chain: it_security.vulnerability_found (critical, exploited) -> internal due date two days before the IT
    and Security SLA, hotfix and product.vulnerability_fixed (it_security); data.agent_quality_report_published with
    a score of 68 -> release freeze for that agent; a report without a score is tolerated.
    """
    d = clock.day
    return [
        bus.make_message("it_security", "product", "it_security.vulnerability_found", {
            "vulnerability_id": params.get("vulnerability_id", "VULN-0001"), "severity": "critical",
            "summary": "Prompt-injection path lets retrieved content trigger an unapproved tool call",
            "component": "agent platform retrieval layer", "release_id": "REL-0001", "cvss": 9.1,
            "exploited_in_wild": True, "due_day": d + 1, "sla_hours": 24}, sim_time=d),
        bus.make_message("data", "product", "data.agent_quality_report_published", {
            "report_id": "AQR-0001", "agent": "Forge supplier-quality triage agent", "quality_score": 68,
            "coverage_pct": 92, "summary": "Quarterly agent quality report: one agent below the freeze score"},
            sim_time=d + 3),
        bus.make_message("data", "product", "data.agent_quality_report_published", {
            "report_id": "AQR-0002", "coverage_pct": 95,
            "summary": "Fleet report without a composite score"}, sim_time=d + 5),
    ]


def scenario_technology_regulation_and_crisis(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A model release, a regulatory change and a critical security crisis hit the product plan.

    Expected chain: external.technology_release_published -> bake-off and model-change assessment (RT-2);
    legal.regulatory_change_noted -> impact assessment, exempt compliance item and a replan;
    executive.crisis_declared -> release freeze, hotfixes continue, roadmap republished.
    """
    d = clock.day
    return [
        bus.make_message("external", "product", "external.technology_release_published", {
            "vendor": "Quillstone AI", "product": "Quillstone Large", "version": "4.2",
            "release_type": "foundation model", "summary": "New foundation model version with lower cost per task"},
            sim_time=d),
        bus.make_message("legal", "product", "legal.regulatory_change_noted", {
            "regulation_id": "REG-2026-AI-07", "title": "EU AI Act obligations for high-risk employment systems",
            "summary": "EU AI Act high-risk obligations apply to employment screening agents",
            "impact_areas": ["high-risk", "eu "], "severity": "high", "effective_day": d + 120}, sim_time=d + 4),
        bus.make_message("executive", "product", "executive.crisis_declared", {
            "crisis_id": "CRS-0001", "category": "security", "severity": "critical",
            "summary": "Critical security incident under investigation; non-essential change frozen"},
            sim_time=d + 20),
    ]


def scenario_budget_pricing_and_hiring(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """The BUD-2027 cycle opens, Product submits 620k, the budget is approved and a price change is approved.

    Expected chain: finance.budget_cycle_opened -> product.budget_submitted (finance); executive.budget_approved ->
    spend tracking and hire plan; executive.pricing_change_approved -> implementation tasks; the quarterly cadence
    in tick() emits product.hire_requested (people) and a product.pricing_change_proposed (finance, executive).
    """
    d = clock.day
    return [
        bus.make_message("finance", "product", "finance.budget_cycle_opened", {
            "budget_cycle_id": "BUD-2027", "year": 2027, "deadline_day": d + 21,
            "summary": "FY2027 budget cycle opened; submissions due day 21"}, sim_time=d),
        bus.make_message("executive", "product", "executive.budget_approved", {
            "budget_cycle_id": "BUD-2027", "year": 2027, "departments": {"product": 620000},
            "summary": "FY2027 budget approved; Product envelope 620k"}, sim_time=d + 40),
        bus.make_message("executive", "product", "executive.pricing_change_approved", {
            "pricing_change_id": params.get("pricing_change_id", "PCH-0001"), "service_line": "forge",
            "tier": "agent_day", "current_gbp": 350, "approved_gbp": 365,
            "summary": "Agent-day rate moves to 365 from the next quarter"}, sim_time=d + 45),
    ]


SCENARIOS = {
    "quarterly_roadmap_planning": scenario_quarterly_roadmap_planning,
    "stage_gated_release_with_risk_review": scenario_stage_gated_release_with_risk_review,
    "feedback_cluster_and_hotfix": scenario_feedback_cluster_and_hotfix,
    "vulnerability_and_quality_regression": scenario_vulnerability_and_quality_regression,
    "technology_regulation_and_crisis": scenario_technology_regulation_and_crisis,
    "budget_pricing_and_hiring": scenario_budget_pricing_and_hiring,
}
