"""Scenario workflows for the data department.

Each scenario function only builds Messages (via ``bus.make_message``); the caller publishes them with
``Company.seed``. Amounts use COMPANY.md prices; the default client is Calder Freight Group (COMPANY.md §10).
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock

# COMPANY.md §3.2: Forge Pilot list price; §3.1 Compass Spark; §3.3 Keep Plus annual value.
FORGE_PILOT_GBP = 90_000
COMPASS_SPARK_GBP = 45_000
KEEP_PLUS_ANNUAL_GBP = 216_000


def _msg(bus: MessageBus, clock: SimClock, sender: str, topic: str, body: dict, offset: int = 0,
         recipient: str = "*") -> Message:
    return bus.make_message(sender, recipient, topic, body, sim_time=clock.day + offset)


def scenario_inbound_lead_to_win(bus: MessageBus, clock: SimClock, client: str = "Calder Freight Group",
                                 employees: int = 650, **params) -> list[Message]:
    """An inbound lead enters marketing (lead-to-cash chain, COMPANY.md §7.2) while external market data
    arrives at data, so the benchmark flow runs alongside the funnel."""
    return [
        _msg(bus, clock, "external", "external.lead_inbound",
             {"lead_id": "LD-00001", "company": client, "employees": employees, "summary": "Inbound enquiry"},
             recipient="marketing"),
        _msg(bus, clock, "external", "external.market_data_published",
             {"indicator": "uk_mid_market_ai_adoption_index", "value": 61.5, "period": "2026-Q1"},
             recipient="data"),
    ]


def scenario_pipeline_to_cash(bus: MessageBus, clock: SimClock, client: str = "Calder Freight Group",
                              client_id: str = "CL-0001", amount_gbp: int = FORGE_PILOT_GBP,
                              **params) -> list[Message]:
    """Funnel to cash events as the owning departments would emit them (all topics data subscribes to):
    lead, qualification, proposal, win, a lost deal, kickoff, 30% invoice, payment and completion.
    Data should report pipeline, bookings, billings, collections and a DSO of 30 days."""
    first_invoice = round(amount_gbp * 0.30)   # COMPANY.md §7: 30% on signature
    return [
        _msg(bus, clock, "marketing", "marketing.campaign_launched",
             {"campaign_id": "CMP-0001", "budget_gbp": 12_000, "summary": "Logistics operations webinar"}),
        _msg(bus, clock, "marketing", "marketing.lead_generated",
             {"lead_id": "LD-00001", "company": client}),
        _msg(bus, clock, "sales", "sales.lead_qualified",
             {"lead_id": "LD-00001", "client_name": client}, offset=1),
        _msg(bus, clock, "sales", "sales.proposal_sent",
             {"deal_id": "DL-0001", "proposal_id": "PR-0001", "client_id": client_id,
              "amount_gbp": amount_gbp, "service_line": "forge", "tier": "forge_pilot"}, offset=2),
        _msg(bus, clock, "sales", "sales.proposal_sent",
             {"deal_id": "DL-0002", "proposal_id": "PR-0002", "client_id": "CL-0002",
              "amount_gbp": COMPASS_SPARK_GBP, "service_line": "compass", "tier": "compass_spark"}, offset=2),
        _msg(bus, clock, "sales", "sales.deal_won",
             {"deal_id": "DL-0001", "client_id": client_id, "client_name": client,
              "amount_gbp": amount_gbp, "service_line": "forge", "tier": "forge_pilot"}, offset=5),
        _msg(bus, clock, "sales", "sales.deal_lost",
             {"deal_id": "DL-0002", "client_id": "CL-0002", "summary": "Lost on timing"}, offset=6),
        _msg(bus, clock, "delivery", "delivery.engagement_kickoff",
             {"engagement_id": "EN-0001", "client_id": client_id, "deal_id": "DL-0001"}, offset=8),
        _msg(bus, clock, "finance", "finance.invoice_issued",
             {"invoice_id": "INV-2026-0001", "client_id": client_id, "amount_gbp": first_invoice}, offset=8),
        _msg(bus, clock, "finance", "finance.payment_received",
             {"invoice_id": "INV-2026-0001", "client_id": client_id, "amount_gbp": first_invoice}, offset=38),
        _msg(bus, clock, "delivery", "delivery.engagement_completed",
             {"engagement_id": "EN-0001", "client_id": client_id}, offset=70),
    ]


def scenario_data_quality_defects(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Malformed and duplicated upstream events: a won deal without client_id, a negative invoice, a duplicate
    invoice id and a payload carrying contact details. Data should raise `data.data_quality_issue_raised`
    to operations and product and keep the contact details out of its logs."""
    return [
        _msg(bus, clock, "sales", "sales.deal_won",
             {"deal_id": "DL-0101", "amount_gbp": 120_000, "service_line": "compass"}),
        _msg(bus, clock, "finance", "finance.invoice_issued",
             {"invoice_id": "INV-2026-0101", "client_id": "CL-0101", "amount_gbp": -500}, offset=1),
        _msg(bus, clock, "finance", "finance.invoice_issued",
             {"invoice_id": "INV-2026-0102", "client_id": "CL-0101", "amount_gbp": 36_000}, offset=1),
        _msg(bus, clock, "finance", "finance.invoice_issued",
             {"invoice_id": "INV-2026-0102", "client_id": "CL-0101", "amount_gbp": 36_000}, offset=2),
        _msg(bus, clock, "customer_success", "customer_success.health_score_updated",
             {"client_id": "CL-0101", "score": 72, "contact_email": "buyer@example.invalid"}, offset=2),
    ]


def scenario_month_end_reporting(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Month-end: finance closes the month and updates the cash forecast, then a board meeting is held.
    Data should publish the KPI report, a forecast and a board pack (kpi_report_published, forecast_updated)."""
    return [
        _msg(bus, clock, "sales", "sales.proposal_sent",
             {"deal_id": "DL-0201", "client_id": "CL-0201", "amount_gbp": 260_000, "service_line": "forge",
              "tier": "forge_build"}),
        _msg(bus, clock, "sales", "sales.deal_won",
             {"deal_id": "DL-0201", "client_id": "CL-0201", "client_name": "Harbour & Vale Logistics",
              "amount_gbp": 260_000, "service_line": "forge"}, offset=1),
        _msg(bus, clock, "finance", "finance.month_end_closed",
             {"period": "2026-01", "revenue_gbp": 320_000, "summary": "January close"}, offset=2),
        _msg(bus, clock, "finance", "finance.cash_forecast_updated",
             {"closing_cash_gbp": 11_800_000, "horizon_days": 90}, offset=3),
        _msg(bus, clock, "executive", "executive.board_meeting_held",
             {"meeting_id": "BRD-2026-Q1", "summary": "Q1 board meeting"}, offset=4),
    ]


def scenario_retention_and_agent_governance(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Retention signals (renewal, health, churn), a regulatory change and an AI risk review cycle.
    Data should update Keep ARR, add the agent to the register and publish an agent quality report."""
    return [
        _msg(bus, clock, "sales", "sales.deal_won",
             {"deal_id": "DL-0301", "client_id": "CL-0301", "client_name": "Northgate Care Partners",
              "amount_gbp": KEEP_PLUS_ANNUAL_GBP, "annual_value_gbp": KEEP_PLUS_ANNUAL_GBP,
              "service_line": "keep", "tier": "keep_plus"}),
        _msg(bus, clock, "customer_success", "customer_success.health_score_updated",
             {"client_id": "CL-0301", "score": 81}, offset=1),
        _msg(bus, clock, "customer_success", "customer_success.renewal_confirmed",
             {"client_id": "CL-0301", "annual_value_gbp": KEEP_PLUS_ANNUAL_GBP, "service_line": "keep"},
             offset=2),
        _msg(bus, clock, "customer_success", "customer_success.client_churned",
             {"client_id": "CL-0302", "annual_value_gbp": 96_000, "service_line": "keep"}, offset=3),
        _msg(bus, clock, "legal", "legal.regulatory_change_noted",
             {"summary": "ICO guidance on retention of analytics data", "severity": "medium"}, offset=3),
        _msg(bus, clock, "product", "product.ai_risk_review_requested",
             {"agent_name": "delivery-qa-agent", "summary": "New QA agent for Forge Build"}, offset=4),
        _msg(bus, clock, "legal", "legal.ai_risk_review_completed",
             {"agent_name": "delivery-qa-agent", "outcome": "approved_with_conditions"}, offset=9),
    ]


def scenario_budget_cycle_and_crisis(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Annual budget cycle and OKRs, then a crisis declaration. Data should submit its budget
    (data.budget_submitted), map OKRs to metrics and switch to weekly reporting."""
    return [
        _msg(bus, clock, "finance", "finance.budget_cycle_opened",
             {"budget_cycle_id": "BUD-2027", "fiscal_year": 2027}),
        _msg(bus, clock, "executive", "executive.budget_approved",
             {"budget_cycle_id": "BUD-2027", "summary": "FY2027 budget approved"}, offset=20),
        _msg(bus, clock, "executive", "executive.okrs_set",
             {"okrs": ["Win rate 30%", "DSO 45 days"], "summary": "FY2027 OKRs"}, offset=21),
        _msg(bus, clock, "executive", "executive.strategy_updated",
             {"summary": "US expansion sequencing updated"}, offset=22),
        _msg(bus, clock, "executive", "executive.crisis_declared",
             {"severity": "high", "summary": "Major client concentration event"}, offset=30),
    ]


SCENARIOS = {
    "inbound_lead_to_win": scenario_inbound_lead_to_win,
    "pipeline_to_cash": scenario_pipeline_to_cash,
    "data_quality_defects": scenario_data_quality_defects,
    "month_end_reporting": scenario_month_end_reporting,
    "retention_and_agent_governance": scenario_retention_and_agent_governance,
    "budget_cycle_and_crisis": scenario_budget_cycle_and_crisis,
}
