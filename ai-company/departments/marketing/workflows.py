"""Marketing department scenarios: seed Messages that exercise the MarketingAgent.

Scenario functions only build Messages via ``bus.make_message``; callers publish them with
``Company.seed``. Prices follow COMPANY.md section 3; sample clients are fictional.
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock

DEPT = "marketing"


def scenario_inbound_lead_to_win(bus: MessageBus, clock: SimClock, lead_id: str = "LD-00001",
                                 company: str = "Calder Freight Group", employees: int = 650,
                                 sector: str = "logistics") -> list[Message]:
    """Inbound web enquiry from a 650-employee UK logistics group, then a sales-qualified follow-up.

    Expected chain: marketing scores the lead and emits marketing.lead_generated; sales qualifies it and
    marketing re-scores on sales.lead_qualified (cross-department chain, CONVENTIONS section 7.2).
    """
    d = clock.day
    return [
        bus.make_message("external", DEPT, "external.lead_inbound", {
            "lead_id": lead_id, "company": company, "employees": employees, "sector": sector,
            "source": "website_form", "contact_title": "Chief Operating Officer",
            "interest": "compass_spark", "summary": "Requested a Compass Spark diagnostic via the website",
        }, sim_time=d),
        bus.make_message("sales", DEPT, "sales.lead_qualified", {
            "lead_id": lead_id, "client_name": company, "service_line": "compass", "tier": "compass_spark",
            "amount_gbp": 45000, "summary": "Discovery call held; budget and sponsor confirmed",
        }, sim_time=d + 5),
    ]


def scenario_roadmap_campaign_launch(bus: MessageBus, clock: SimClock,
                                     release: str = "Forge Agent Studio 2.4",
                                     benchmark_id: str = "BM-2026-03") -> list[Message]:
    """Product roadmap, release and benchmark data arrive; marketing plans and launches a campaign.

    Expected chain: marketing.campaign_launched (to sales and data) and marketing.content_published.
    """
    d = clock.day
    return [
        bus.make_message("executive", DEPT, "executive.okrs_set", {
            "period": "FY2026-Q2", "summary": "Marketing OKR: 1,800 MQLs and 36 SQLs per quarter",
            "department": DEPT,
        }, sim_time=d),
        bus.make_message("product", DEPT, "product.roadmap_published", {
            "summary": "H2 roadmap: governance agent, document-intelligence connectors",
            "service_line": "forge",
        }, sim_time=d + 1),
        bus.make_message("data", DEPT, "data.benchmark_ready", {
            "benchmark_id": benchmark_id, "summary": "UK mid-market AI adoption benchmark, n=412 firms",
            "headline": "Only 18% of AI pilots reach production",
        }, sim_time=d + 3),
        bus.make_message("product", DEPT, "product.release_shipped", {
            "release": release, "service_line": "forge",
            "summary": "Agent evaluation harness and audit trail",
        }, sim_time=d + 7),
        bus.make_message("product", DEPT, "product.agent_capability_added", {
            "capability": "contract-review agent", "service_line": "forge",
            "summary": "New capability for Forge Build engagements",
        }, sim_time=d + 8),
    ]


def scenario_case_study_and_feedback(bus: MessageBus, clock: SimClock, client_id: str = "CL-0001",
                                     client_name: str = "Calder Freight Group") -> list[Message]:
    """A client approves a case study and gives positive feedback; sales loses a deal on proof points.

    Expected chain: marketing.content_published for the approved case study, content refresh after
    sales.deal_lost, and a nurture update from customer_success.feedback_received.
    """
    d = clock.day
    return [
        bus.make_message("customer_success", DEPT, "customer_success.case_study_approved", {
            "client_id": client_id, "client_name": client_name, "service_line": "forge",
            "tier": "forge_build", "amount_gbp": 260000,
            "summary": "Client legal approved quote and metrics: 31% faster dispatch planning",
        }, sim_time=d),
        bus.make_message("customer_success", DEPT, "customer_success.feedback_received", {
            "client_id": client_id, "client_name": client_name, "nps": 72,
            "summary": "Client praised the named client manager and the agent audit trail",
        }, sim_time=d + 2),
        bus.make_message("sales", DEPT, "sales.deal_lost", {
            "deal_id": "DL-0014", "client_name": "Harrow Quay Insurance", "service_line": "forge",
            "tier": "forge_pilot", "amount_gbp": 90000, "reason": "no_sector_reference",
            "summary": "Lost to a rival; buyer wanted an insurance sector case study",
        }, sim_time=d + 4),
    ]


def scenario_brand_crisis_response(bus: MessageBus, clock: SimClock) -> list[Message]:
    """Executive declares a crisis and a pricing change lands; marketing pauses activity and aligns messaging.

    Expected chain: campaigns paused, marketing.brand_incident_raised if reputational risk is found
    (to executive and legal), then pricing collateral refreshed on executive.pricing_change_approved.
    """
    d = clock.day
    return [
        bus.make_message("executive", DEPT, "executive.crisis_declared", {
            "crisis_id": "CR-0001", "severity": "high",
            "summary": "Supplier data incident reported in trade press; outbound campaigns on hold",
        }, sim_time=d),
        bus.make_message("executive", DEPT, "executive.pricing_change_approved", {
            "service_line": "keep", "tier": "keep_plus", "amount_gbp": 18000,
            "summary": "Keep Plus held at £18,000 per month; Essential tier repackaged",
        }, sim_time=d + 3),
        bus.make_message("executive", DEPT, "executive.strategy_updated", {
            "summary": "Priority sectors: logistics, insurance, healthcare services",
        }, sim_time=d + 10),
    ]


def scenario_budget_cycle_and_hiring(bus: MessageBus, clock: SimClock,
                                     cycle_id: str = "BUD-2027") -> list[Message]:
    """FY2027 budget cycle opens; marketing submits its budget; a job posting needs employer-brand support.

    Expected chain: marketing.budget_submitted and marketing.hire_requested, then employer-brand
    content on people.job_posted.
    """
    d = clock.day
    return [
        bus.make_message("finance", DEPT, "finance.budget_cycle_opened", {
            "budget_cycle": cycle_id, "due_day": d + 14, "summary": "FY2027 planning cycle opened",
        }, sim_time=d),
        bus.make_message("executive", DEPT, "executive.budget_approved", {
            "budget_cycle": cycle_id, "department": DEPT, "summary": "Envelope approved for FY2027",
        }, sim_time=d + 21),
        bus.make_message("people", DEPT, "people.job_posted", {
            "requisition_id": "REQ-0007", "department": "delivery",
            "summary": "Senior Consultant, AI Implementation, London; employer-brand post requested",
        }, sim_time=d + 24),
    ]


SCENARIOS = {
    "inbound_lead_to_win": scenario_inbound_lead_to_win,
    "roadmap_campaign_launch": scenario_roadmap_campaign_launch,
    "case_study_and_feedback": scenario_case_study_and_feedback,
    "brand_crisis_response": scenario_brand_crisis_response,
    "budget_cycle_and_hiring": scenario_budget_cycle_and_hiring,
}
