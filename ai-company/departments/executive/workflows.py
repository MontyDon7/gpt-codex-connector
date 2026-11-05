"""Executive department scenarios (Lumenhall Partners).

Each ``scenario_*`` function only builds Messages with ``bus.make_message``; the caller seeds them with
``Company.seed``. Prices follow COMPANY.md section 3, delegations follow section 9.3 and department
budgets follow section 5.4. Clients are fictional (COMPANY.md section 10).
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock


def scenario_large_deal_approval(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A 650,000 Forge Scale deal and a 1.8m Compass Programme deal need CEO and Board decisions.

    Expected chain: sales.proposal_sent -> sales.deal_approval_requested -> executive.deal_decision_made
    (approved_with_conditions for the 12% discount; referred_to_board for the 1.8m deal, then ratified
    by the Board after the written-consent window); sales.deal_won updates the concentration ledger.
    """
    d = clock.day
    amount = params.get("amount_gbp", 650000)
    discount = params.get("discount_pct", 12)
    big = params.get("board_amount_gbp", 1_800_000)
    deal = {"deal_id": "DL-0006", "client_id": "CL-0006", "client_name": "Northgate Retail Holdings",
            "service_line": "forge", "tier": "forge_scale", "amount_gbp": amount, "duration_months": 11}
    large = {"deal_id": "DL-0011", "client_id": "CL-0011", "client_name": "Harbourline Logistics Group",
             "service_line": "compass", "tier": "compass_programme", "amount_gbp": big,
             "duration_months": 24}
    return [
        bus.make_message("sales", "executive", "sales.proposal_sent", dict(
            deal, proposal_id="PR-0006", summary="Forge Scale proposal issued to the client board"),
            sim_time=d),
        bus.make_message("sales", "executive", "sales.deal_approval_requested", dict(
            deal, discount_pct=discount, gross_margin_pct=47,
            summary="Contract value 650,000 with 12% discount; Finance head concurrence needed"),
            sim_time=d + 2),
        bus.make_message("sales", "executive", "sales.deal_approval_requested", dict(
            large, discount_pct=5, gross_margin_pct=52,
            summary="Multi-year Compass Programme framework above the 1.5m Board threshold"),
            sim_time=d + 3),
        bus.make_message("sales", "executive", "sales.deal_won", dict(
            deal, summary="Forge Scale won after approved discount"), sim_time=d + 20),
    ]


def scenario_headcount_and_budget_cycle(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """The Q4 budget cycle plus headcount requests inside and outside the approved plan.

    Expected chain: finance.budget_cycle_opened -> executive.budget_submitted (finance);
    finance.budget_consolidated -> executive.budget_approved + executive.okrs_set +
    executive.hire_requested (people); people.requisition_opened and people.hire_requested ->
    executive.headcount_approved (or a recorded refusal when outside plan with no business case).
    """
    d = clock.day
    fy = params.get("fiscal_year", 2027)
    return [
        bus.make_message("finance", "executive", "finance.budget_cycle_opened", {
            "budget_id": f"BUD-{fy}", "fiscal_year": fy, "summary": f"FY{fy} budget cycle opens"},
            sim_time=d),
        bus.make_message("people", "executive", "people.requisition_opened", {
            "requisition_id": "REQ-0101", "department": "delivery", "role_title": "Senior Consultant",
            "level": "senior_consultant", "in_budget": True,
            "summary": "Backfill-free in-plan hire for the Forge Build team"}, sim_time=d + 1),
        bus.make_message("people", "executive", "people.hire_requested", {
            "requisition_id": "REQ-0102", "department": "sales", "role_title": "Enterprise Account Director",
            "level": "manager", "in_budget": False,
            "business_case": "Pipeline coverage of 3.1x needs a second enterprise seller",
            "summary": "Out-of-plan hire with business case"}, sim_time=d + 2),
        bus.make_message("people", "executive", "people.requisition_opened", {
            "requisition_id": "REQ-0103", "department": "marketing", "role_title": "Events Coordinator",
            "level": "associate", "in_budget": False, "summary": "Out-of-plan hire, no business case"},
            sim_time=d + 3),
        bus.make_message("finance", "executive", "finance.budget_submitted", {
            "department": "delivery", "fiscal_year": fy, "total_gbp": 8_100_000,
            "summary": "Delivery submission above its 7.4m envelope"}, sim_time=d + 10),
        bus.make_message("finance", "executive", "finance.budget_consolidated", {
            "budget_id": f"BUD-{fy}", "fiscal_year": fy, "total_gbp": params.get("total_gbp", 18_400_000),
            "summary": "Consolidated submissions are 3.4% above the 17.8m envelope"}, sim_time=d + 20),
    ]


def scenario_data_breach_crisis(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A confirmed personal data breach forces a crisis declaration and an emergency Board meeting.

    Expected chain: it_security.incident_detected (critical) -> executive.crisis_declared (all other
    departments) + executive.board_meeting_held; it_security.data_breach_confirmed and
    legal.regulator_notification_filed attach to the open crisis; it_security.incident_resolved stands
    the crisis down and creates a post-incident review task.
    """
    d = clock.day
    inc = params.get("incident_id", "INC-0007")
    return [
        bus.make_message("it_security", "executive", "it_security.incident_detected", {
            "incident_id": inc, "severity": "critical", "detected_day": d,
            "summary": "Exfiltration from a client data workspace detected by monitoring"}, sim_time=d),
        bus.make_message("it_security", "executive", "it_security.data_breach_confirmed", {
            "incident_id": inc, "records": 4200, "client_id": "CL-0001",
            "summary": "Personal data of 4,200 client employees confirmed affected"}, sim_time=d + 1),
        bus.make_message("legal", "executive", "legal.regulator_notification_filed", {
            "incident_id": inc, "regulator": "ICO",
            "summary": "ICO notification filed inside the 72-hour window"}, sim_time=d + 2),
        bus.make_message("it_security", "executive", "it_security.incident_resolved", {
            "incident_id": inc, "summary": "Containment complete and access revoked"}, sim_time=d + 12),
    ]


def scenario_cash_pressure_and_performance(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Month-end results fall behind plan while the cash forecast shows a runway below six months.

    Expected chain: finance.month_end_closed (behind plan) -> re-forecast task; finance.budget_variance_flagged
    sets a hiring hold; finance.cash_forecast_updated with runway under 6 months -> executive.crisis_declared
    (liquidity) and a hiring freeze on later requisitions.
    """
    d = clock.day
    runway = params.get("runway_months", 5.0)
    return [
        bus.make_message("finance", "executive", "finance.month_end_closed", {
            "month": 6, "ytd_revenue_gbp": 2_400_000, "gross_margin_pct": 44, "ebitda_margin_pct": -31,
            "active_clients": 15, "summary": "June close: YTD revenue 2.4m against 3.0m phased plan"},
            sim_time=d),
        bus.make_message("finance", "executive", "finance.budget_variance_flagged", {
            "department": "marketing", "variance_pct": 18.0,
            "summary": "Marketing programme spend 18% over phased budget"}, sim_time=d + 1),
        bus.make_message("finance", "executive", "finance.cash_forecast_updated", {
            "runway_months": runway, "summary": "Forecast burn leaves under six months of cash"},
            sim_time=d + 3),
        bus.make_message("people", "executive", "people.requisition_opened", {
            "requisition_id": "REQ-0201", "department": "delivery", "role_title": "Consultant",
            "in_budget": True, "summary": "In-plan hire during liquidity crisis"}, sim_time=d + 5),
    ]


def scenario_pricing_and_client_risk(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A 10% Keep Plus price rise is proposed while the largest Keep client threatens to churn.

    Expected chain: product.pricing_change_proposed -> executive.pricing_change_approved (sales,
    finance, marketing, product); customer_success.churn_risk_flagged -> CEO sponsor-call task;
    customer_success.client_churned -> crisis assessment when the client is 10% or more of plan revenue.
    """
    d = clock.day
    return [
        bus.make_message("product", "executive", "product.pricing_change_proposed", {
            "change_id": "PRC-0003", "tier": "keep_plus", "service_line": "keep",
            "old_price_gbp": 216000, "new_price_gbp": 237600, "margin_impact_pct": 3.5,
            "summary": "10% annual uplift on Keep Plus after two new agent capabilities"}, sim_time=d),
        bus.make_message("customer_success", "executive", "customer_success.churn_risk_flagged", {
            "client_id": "CL-0009", "client_name": "Pennine Mutual Assurance", "annual_value_gbp": 480000,
            "summary": "Keep Enterprise client unhappy with response times"}, sim_time=d + 4),
        bus.make_message("customer_success", "executive", "customer_success.client_churned", {
            "client_id": "CL-0009", "client_name": "Pennine Mutual Assurance", "annual_value_gbp": 650000,
            "summary": "Client served notice after failed recovery plan"}, sim_time=d + 40),
    ]


SCENARIOS = {
    "large_deal_approval": scenario_large_deal_approval,
    "headcount_and_budget_cycle": scenario_headcount_and_budget_cycle,
    "data_breach_crisis": scenario_data_breach_crisis,
    "cash_pressure_and_performance": scenario_cash_pressure_and_performance,
    "pricing_and_client_risk": scenario_pricing_and_client_risk,
}
