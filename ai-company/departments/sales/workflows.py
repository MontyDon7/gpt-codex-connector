"""Sales department scenarios (Lumenhall Partners).

Each ``scenario_*`` function only builds Messages with ``bus.make_message``; the caller seeds them with
``Company.seed``. Prices, discount authority and approval thresholds follow COMPANY.md sections 3 and 9.3,
the funnel follows section 5.3, and client decision windows follow ``economics.md`` section 3.7 (Compass Spark
40 days, Forge Scale 105 days). Clients are fictional (COMPANY.md section 10). Client outcomes are fixed by the
``outcome`` hint so every scenario is deterministic.
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock


def scenario_inbound_lead_to_signed_contract(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """An MQL logistics lead becomes a Compass Spark new logo, signs, and pays in two instalments.

    Expected chain: marketing.lead_generated (mql) -> sales.lead_qualified (marketing, delivery, data) and
    sales.proposal_requested (delivery, finance); delivery.scoping_completed + finance.pricing_check_completed
    + it_security.security_questionnaire_completed + legal.security_terms_reviewed -> sales.security_review_
    requested and sales.proposal_sent; after the 40-day window sales.deal_won; legal.contract_signed accrues
    commission; finance.payment_received releases half, then the balance on the final milestone.
    """
    d = clock.day
    lead = params.get("lead_id", "LD-00101")
    common = {"lead_id": lead, "client_id": params.get("client_id", "CL-0101")}
    amount = params.get("amount_gbp", 45000)
    return [
        bus.make_message("marketing", "sales", "marketing.lead_generated", {
            **common, "company": params.get("client_name", "Calder Freight Group"),
            "client_name": params.get("client_name", "Calder Freight Group"),
            "contact_name": "Imogen Vale", "contact_role": "Chief Operating Officer", "employees": 650,
            "sector": "logistics", "source": "referral", "score": 88, "stage": "mql", "severity": "high",
            "score_reasons": ["icp_size", "icp_sector", "senior_buyer", "named_pain_point"],
            "pain": "Manual exception handling across 14 depots", "service_line": "compass",
            "tier": "compass_spark", "amount_gbp": amount, "outcome": "won",
            "summary": "MQL: logistics operator wants an AI opportunity assessment"}, sim_time=d),
        bus.make_message("delivery", "sales", "delivery.scoping_completed", dict(
            common, tier="compass_spark", service_line="compass", amount_gbp=amount,
            estimated_value_gbp=amount, duration_weeks=4, summary="Spark scoped: 4 weeks, 3 workshops",
            due_day=d + 4), sim_time=d + 4),
        bus.make_message("finance", "sales", "finance.pricing_check_completed", dict(
            common, tier="compass_spark", amount_gbp=amount, approved=True, max_discount_pct=10,
            margin_pct=52, summary="Pricing check passed at list price"), sim_time=d + 5),
        bus.make_message("it_security", "sales", "it_security.security_questionnaire_completed", dict(
            common, blocking_gaps=[], summary="Client security questionnaire answered, no gaps"),
            sim_time=d + 7),
        bus.make_message("legal", "sales", "legal.security_terms_reviewed", dict(
            common, summary="DPA and liability cap on standard terms"), sim_time=d + 8),
        bus.make_message("legal", "sales", "legal.contract_signed", dict(
            common, contract_id="CT-0101", amount_gbp=amount, summary="Compass Spark SOW signed"),
            sim_time=d + 56),
        bus.make_message("finance", "sales", "finance.payment_received", dict(
            common, invoice_id="INV-2026-0101", amount_gbp=round(amount * 0.3 * 1.2),
            milestone="M1 signature", summary="30% signature invoice paid"), sim_time=d + 62),
        bus.make_message("finance", "sales", "finance.payment_received", dict(
            common, invoice_id="INV-2026-0103", amount_gbp=round(amount * 0.3 * 1.2),
            milestone="Final acceptance", final_milestone=True, summary="Final milestone invoice paid"),
            sim_time=d + 100),
    ]


def scenario_mql_and_nurture_triage(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Marketing hands over mql and nurture leads; the same 60-point desk check applies to both.

    Expected chain: an mql lead and a nurture lead that scores 60+ on the sales rubric both produce
    sales.lead_qualified and sales.proposal_requested (the nurture one is recorded as a learning case); a
    nurture lead outside the 200 to 2,000 employee range is disqualified; a US lead before 2027 is parked.
    """
    d = clock.day
    base = {"source": "website_form", "service_line": "forge"}
    return [
        bus.make_message("marketing", "sales", "marketing.lead_generated", dict(
            base, lead_id="LD-00201", company="Fenwick Precision Components", employees=420,
            sector="manufacturing", contact_role="Managing Director", score=71, stage="mql",
            score_reasons=["icp_size", "senior_buyer"], pain="Scrap rate and supplier-quality triage",
            tier="forge_pilot", summary="MQL: manufacturer wants a quality-triage pilot"), sim_time=d),
        bus.make_message("marketing", "sales", "marketing.lead_generated", dict(
            base, lead_id="LD-00202", company="Aldersgate Wealth Partners", employees=310,
            sector="financial services", contact_role="Head of Operations", score=48, stage="nurture",
            score_reasons=["icp_size", "named_pain_point"], pain="KYC backlog", budget_confirmed=True,
            service_line="compass", summary="Nurture: marketing score 48, sales rubric 90"), sim_time=d + 1),
        bus.make_message("marketing", "sales", "marketing.lead_generated", dict(
            base, lead_id="LD-00203", company="Hollis & Reeve Logistics", employees=45,
            sector="logistics", contact_role="Office Manager", score=30, stage="nurture",
            summary="Nurture: small firm outside the ICP size band"), sim_time=d + 2),
        bus.make_message("marketing", "sales", "marketing.lead_generated", dict(
            base, lead_id="LD-00204", company="Hudson Yards Freight", employees=800, country="US",
            sector="logistics", contact_role="Chief Executive Officer", score=80, stage="mql",
            summary="MQL from New York before the US launch"), sim_time=d + 3),
    ]


def scenario_rfp_forge_scale_with_approvals(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A 650,000 Forge Scale RFP with a 12% discount request needs Finance head, CEO and security sign-off.

    Expected chain: external.rfp_received -> sales.lead_qualified + sales.proposal_requested (source rfp);
    scoping and pricing gates -> sales.security_review_requested + sales.deal_approval_requested (discount above
    10% and net 572,000 at least 500,000); executive.deal_decision_made releases sales.proposal_sent; a high
    contract risk reopens the CEO and General Counsel approval; after the 105-day window sales.deal_won.
    """
    d = clock.day
    amount = params.get("amount_gbp", 650000)
    discount = params.get("requested_discount_pct", 12)
    common = {"client_id": params.get("client_id", "CL-0106"), "deal_id": "DL-0001"}
    return [
        bus.make_message("external", "sales", "external.rfp_received", dict(
            common, rfp_id="RFP-0006", client_name="Northgate Retail Holdings", employees=1_400,
            industry="retail", estimated_value_gbp=amount, tier="forge_scale",
            requested_discount_pct=discount, outcome="won", due_day=d + 28,
            requirements="Store operations and finance automation across 120 sites",
            summary="Invitation to tender: 11-month store operations transformation"), sim_time=d),
        bus.make_message("delivery", "sales", "delivery.scoping_completed", dict(
            common, tier="forge_scale", service_line="forge", estimated_value_gbp=amount,
            duration_weeks=44, effort_days=2_050, summary="Scoped at 1,150 consultant-days and 900 agent-days",
            due_day=d + 8), sim_time=d + 8),
        bus.make_message("finance", "sales", "finance.pricing_check_completed", dict(
            common, tier="forge_scale", amount_gbp=amount, approved=True, max_discount_pct=15,
            margin_pct=47, approval_required=True, summary="Margin 47% before discount; CEO sign-off needed"),
            sim_time=d + 9),
        bus.make_message("it_security", "sales", "it_security.security_questionnaire_completed", dict(
            common, blocking_gaps=[], summary="Security evidence pack accepted"), sim_time=d + 14),
        bus.make_message("legal", "sales", "legal.security_terms_reviewed", dict(
            common, summary="Standard terms, liability capped at fees"), sim_time=d + 15),
        bus.make_message("executive", "sales", "executive.deal_decision_made", dict(
            common, decision="approved", conditions=["payment on 30/40/30 milestones"],
            summary="CEO and Finance head approve 12% discount"), sim_time=d + 16),
        bus.make_message("legal", "sales", "legal.contract_risk_flagged", dict(
            common, severity="high", summary="Client redlines propose uncapped data-breach liability"),
            sim_time=d + 60),
        bus.make_message("legal", "sales", "legal.contract_signed", dict(
            common, contract_id="CT-0106", summary="MSA and SOW signed after negotiation"), sim_time=d + 135),
    ]


def scenario_renewal_and_churn_defence(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A healthy Keep Plus client is renewed with the capped uplift; an unhealthy Enterprise client is saved or lost.

    Expected chain: customer_success.renewal_due -> sales.renewal_proposal_sent (uplift CPI + 2%, cap 7%, 90
    days ahead so on time); churn_risk_flagged and a health score below 60 create executive-call and review tasks
    and a save offer (uplift waived) on the next renewal; renewal_confirmed books the renewal; client_churned
    closes the open deal of that client (sales.deal_lost).
    """
    d = clock.day
    kept = {"client_id": "CL-0107", "client_name": "Aldersgate Wealth Partners", "contract_id": "CT-0107",
            "tier": "keep_plus", "annual_value_gbp": 216_000}
    risky = {"client_id": "CL-0109", "client_name": "Pennine Mutual Assurance", "contract_id": "CT-0109",
             "tier": "keep_enterprise", "annual_value_gbp": 480_000}
    return [
        bus.make_message("customer_success", "sales", "customer_success.renewal_due", dict(
            kept, cpi_pct=params.get("cpi_pct", 4.5), health_score=82, due_day=d + 90,
            summary="Keep Plus renewal in 90 days"), sim_time=d),
        bus.make_message("customer_success", "sales", "customer_success.health_score_updated", dict(
            risky, score=48, summary="Health score fell to 48 after two missed QBRs"), sim_time=d + 3),
        bus.make_message("customer_success", "sales", "customer_success.churn_risk_flagged", dict(
            risky, severity="high", summary="Sponsor left; procurement is re-tendering"), sim_time=d + 4),
        bus.make_message("customer_success", "sales", "customer_success.renewal_due", dict(
            risky, due_day=d + 75, summary="Keep Enterprise renewal in 75 days; client at risk"),
            sim_time=d + 5),
        bus.make_message("customer_success", "sales", "customer_success.expansion_opportunity_identified", dict(
            risky, tier="forge_pilot", service_line="forge", outcome="lost", loss_reason="timing",
            summary="Forge pilot discussed alongside the save plan"), sim_time=d + 6),
        bus.make_message("customer_success", "sales", "customer_success.renewal_confirmed", dict(
            kept, amount_gbp=round(kept["annual_value_gbp"] * 1.065), summary="Renewal confirmed for 12 months"),
            sim_time=d + 30),
        bus.make_message("customer_success", "sales", "customer_success.client_churned", dict(
            risky, severity="high", summary="90-day notice served; retainer ends"), sim_time=d + 40),
    ]


def scenario_credit_hold_expansion(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """An overdue invoice puts a client on credit hold, so its expansion proposal is prepared but not issued.

    Expected chain: finance.invoice_overdue -> credit hold and relationship-call task; expansion opportunity ->
    sales.proposal_requested; scoping and pricing gates -> proposal built and held (no sales.proposal_sent);
    finance.payment_received clears the hold and releases the proposal (sales.proposal_sent).
    """
    d = clock.day
    client = {"client_id": params.get("client_id", "CL-0108"), "deal_id": "DL-0001"}
    return [
        bus.make_message("finance", "sales", "finance.invoice_overdue", dict(
            client, invoice_id="INV-2026-0044", amount_gbp=43_200, days_overdue=34,
            summary="Forge Pilot milestone invoice 34 days overdue"), sim_time=d),
        bus.make_message("customer_success", "sales", "customer_success.expansion_opportunity_identified", dict(
            client, client_name="Fenwick Precision Components", tier="forge_build", service_line="forge",
            employees=420, industry="manufacturing", outcome="won",
            summary="Sponsor wants to scale the triage agent to three plants"), sim_time=d + 1),
        bus.make_message("delivery", "sales", "delivery.scoping_completed", dict(
            client, tier="forge_build", estimated_value_gbp=260_000, summary="Build scoped across three plants"),
            sim_time=d + 5),
        bus.make_message("finance", "sales", "finance.pricing_check_completed", dict(
            client, tier="forge_build", approved=True, max_discount_pct=10, summary="Pricing check passed"),
            sim_time=d + 6),
        bus.make_message("finance", "sales", "finance.payment_received", dict(
            client, invoice_id="INV-2026-0044", amount_gbp=43_200, milestone="M2 mid-point",
            summary="Overdue invoice settled; CFO releases the hold"), sim_time=d + 20),
    ]


def scenario_crisis_discount_cap_and_lift(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A crisis caps discounts at 5% until the CEO lifts it; delivery capacity is tight meanwhile.

    Expected chain: executive.crisis_declared -> crisis mode and critical re-forecast task;
    delivery.capacity_forecast_updated (92% utilisation) -> 14-day start lag quoted; a Forge Pilot RFP asking for
    15% is priced at 5% (proposal_sent carries delivery_start_lag_days 14); the CEO's lifting instruction on
    executive.crisis_declared switches crisis mode off.
    """
    d = clock.day
    return [
        bus.make_message("executive", "sales", "executive.crisis_declared", {
            "crisis_id": "CRS-0001", "category": "data_breach", "severity": "high",
            "summary": "Supplier data incident under investigation; client messaging held"}, sim_time=d),
        bus.make_message("delivery", "sales", "delivery.capacity_forecast_updated", {
            "utilisation_pct": 92, "capacity_status": "tight",
            "summary": "Utilisation 92% next quarter"}, sim_time=d + 1),
        bus.make_message("external", "sales", "external.rfp_received", {
            "rfp_id": "RFP-0012", "client_id": "CL-0112", "client_name": "Brannock Healthcare Services",
            "employees": 900, "industry": "healthcare_services", "estimated_value_gbp": 95_000,
            "tier": "forge_pilot", "requested_discount_pct": 15, "due_day": d + 24, "outcome": "won",
            "summary": "Tender for a clinical-admin automation pilot"}, sim_time=d + 2),
        bus.make_message("delivery", "sales", "delivery.scoping_completed", {
            "client_id": "CL-0112", "tier": "forge_pilot", "estimated_value_gbp": 95_000,
            "summary": "Pilot scoped in 8 weeks"}, sim_time=d + 5),
        bus.make_message("finance", "sales", "finance.pricing_check_completed", {
            "client_id": "CL-0112", "tier": "forge_pilot", "approved": True, "max_discount_pct": 15,
            "summary": "Finance accepts up to 15%; crisis ceiling applies in Sales"}, sim_time=d + 6),
        bus.make_message("it_security", "sales", "it_security.security_questionnaire_completed", {
            "client_id": "CL-0112", "blocking_gaps": [], "summary": "Questionnaire answered, no gaps"},
            sim_time=d + 9),
        bus.make_message("legal", "sales", "legal.security_terms_reviewed", {
            "client_id": "CL-0112", "summary": "Standard terms"}, sim_time=d + 10),
        bus.make_message("executive", "sales", "executive.crisis_declared", {
            "crisis_id": "CRS-0001", "status": "lifted", "severity": "high",
            "summary": "CEO lifts crisis mode after the incident is closed"}, sim_time=d + 20),
    ]


def scenario_engagement_completion_and_change_order(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Delivery completes a Forge Pilot and requests extra days, opening an expansion and a change order.

    Expected chain: delivery.engagement_completed (forge_pilot) -> expansion deal for Forge Build
    (sales.lead_qualified + sales.proposal_requested); delivery.scope_change_requested (8 senior consultant
    days and 4 agent days at the rate card, 9,800) -> change-order deal and sales.proposal_requested only;
    product.agent_capability_added and marketing.campaign_launched raise enablement and SDR capacity tasks.
    """
    d = clock.day
    client = {"client_id": params.get("client_id", "CL-0110"), "client_name": "Brannock Healthcare Services"}
    return [
        bus.make_message("delivery", "sales", "delivery.engagement_completed", dict(
            client, engagement_id="EN-0110", tier="forge_pilot", service_line="forge", employees=900,
            industry="healthcare_services", summary="Forge Pilot accepted; sponsor asks for scale-up"),
            sim_time=d),
        bus.make_message("delivery", "sales", "delivery.scope_change_requested", dict(
            client, engagement_id="EN-0111", tier="forge_build",
            days_by_level={"senior_consultant": 8, "ai_agent_day": 4}, extra_days=12,
            summary="Client adds a second data source: 8 consultant days and 4 agent days"), sim_time=d + 3),
        bus.make_message("product", "sales", "product.agent_capability_added", {
            "capability": "Document-extraction agent with human review queue",
            "summary": "Shipped in production for two clients"}, sim_time=d + 5),
        bus.make_message("marketing", "sales", "marketing.campaign_launched", {
            "campaign": "Healthcare operations roundtable", "expected_leads": 55,
            "summary": "Webinar series; 55 leads expected in the first month"}, sim_time=d + 6),
    ]


SCENARIOS = {
    "inbound_lead_to_signed_contract": scenario_inbound_lead_to_signed_contract,
    "mql_and_nurture_triage": scenario_mql_and_nurture_triage,
    "rfp_forge_scale_with_approvals": scenario_rfp_forge_scale_with_approvals,
    "renewal_and_churn_defence": scenario_renewal_and_churn_defence,
    "credit_hold_expansion": scenario_credit_hold_expansion,
    "crisis_discount_cap_and_lift": scenario_crisis_discount_cap_and_lift,
    "engagement_completion_and_change_order": scenario_engagement_completion_and_change_order,
}
