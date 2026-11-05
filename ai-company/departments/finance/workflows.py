"""Finance department scenarios (Lumenhall Partners).

Each ``scenario_*`` function only builds Messages with ``bus.make_message``; the caller seeds them with
``Company.seed``. Prices follow COMPANY.md section 3, billing follows section 9 and the 30/40/30 milestone
split, and budget figures follow COMPANY.md section 5.4 (FY2027 totals, GBP). Clients are fictional
(COMPANY.md section 10).
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock

# FY2027 department budget totals in GBP (COMPANY.md section 5.4, Y2 total column).
_FY2027_BUDGETS_GBP = {
    "executive": 1_050_000, "sales": 2_100_000, "marketing": 1_850_000, "delivery": 7_400_000,
    "people": 700_000, "legal": 580_000, "it_security": 920_000, "operations": 700_000,
    "customer_success": 790_000, "product": 620_000, "data": 360_000,
}


def scenario_milestone_to_cash(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A Forge Build milestone is accepted, invoiced and then paid by the client.

    Expected chain: delivery.milestone_reached -> finance.invoice_issued (customer_success, data);
    external.client_payment_received -> finance.payment_received (sales, customer_success, data).
    The 40% mid-point of a 260,000 fee is 104,000 plus 20% VAT.
    """
    d = clock.day
    fee = params.get("contract_value_gbp", 260000)
    net = round(fee * 0.40)
    gross = round(net * 1.2)
    common = {
        "client_id": params.get("client_id", "CL-0001"),
        "client_name": params.get("client_name", "Calder Freight Group"),
        "engagement_id": params.get("engagement_id", "EN-0001"),
        "contract_id": params.get("contract_id", "CT-0001"),
        "service_line": "forge", "tier": "forge_build",
    }
    milestone = dict(common, milestone="M2 mid-point acceptance", billing_pct=40, amount_gbp=net,
                     summary=f"Mid-point milestone accepted by client sponsor; 40% of {fee:,} due",
                     due_day=d + 2)
    payment = dict(common, invoice_id=params.get("invoice_id", "INV-2026-0014"), amount_gbp=gross,
                   payment_method="BACS", reference="CALDER FREIGHT LUM INV-2026-0014",
                   summary=f"BACS receipt of {gross:,} (net {net:,} plus VAT) inside 30-day terms")
    return [
        bus.make_message("delivery", "finance", "delivery.milestone_reached", milestone, sim_time=d),
        bus.make_message("external", "finance", "external.client_payment_received", payment,
                         sim_time=d + params.get("days_to_pay", 24)),
    ]


def scenario_overdue_collections(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """An invoice goes unpaid past terms while the client raises a dispute with Legal.

    Expected chain: delivery.milestone_reached -> finance.invoice_issued; no payment arrives, so the
    dunning ladder produces finance.invoice_overdue (customer_success, legal, sales) and, with
    legal.client_dispute_raised, finance.collections_escalated (legal, executive).
    """
    d = clock.day
    cid = params.get("client_id", "CL-0008")
    cname = params.get("client_name", "Fenwick Precision Components")
    amount = params.get("amount_gbp", 36000)
    common = {"client_id": cid, "client_name": cname, "engagement_id": "EN-0008",
              "contract_id": "CT-0008", "service_line": "forge", "tier": "forge_pilot"}
    milestone = dict(common, milestone="M2 mid-point acceptance", billing_pct=40, amount_gbp=amount,
                     summary="Forge Pilot mid-point accepted; 40% of 90,000 due", due_day=d + 2)
    dispute = dict(common, invoice_id="INV-2026-0021", amount_gbp=round(amount * 1.2), severity="high",
                   summary="Client finance director withholds payment pending a quality review of the "
                           "supplier-quality triage agent and asks for a credit note",
                   due_day=d + 12)
    return [
        bus.make_message("delivery", "finance", "delivery.milestone_reached", milestone, sim_time=d),
        bus.make_message("legal", "finance", "legal.client_dispute_raised", dispute, sim_time=d + 45),
    ]


def scenario_annual_budget_cycle(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """The Q4 budget cycle for FY2027 runs from board strategy through department submissions.

    Expected chain: executive.strategy_updated + executive.okrs_set shape the guidance;
    <dept>.budget_submitted x11 (COMPANY.md section 5.4 Y2 totals) -> finance.budget_consolidated
    (executive) and finance.budget_variance_flagged where a submission exceeds its envelope.
    """
    d = clock.day
    overrun = params.get("delivery_overrun_gbp", 450000)
    msgs = [
        bus.make_message("executive", "finance", "executive.strategy_updated", {
            "summary": "Board confirms FY2027 plan: revenue 19.5m, EBITDA 1.7m (9%), 65 net new logos",
            "revenue_gbp": 19_500_000, "ebitda_gbp": 1_700_000, "severity": "medium"}, sim_time=d),
        bus.make_message("executive", "finance", "executive.okrs_set", {
            "summary": "FY2027 company OKRs: gross margin 58%, Keep ARR 6.5m, DSO under 45 days",
            "okrs": ["gross_margin_58pct", "keep_arr_6_5m", "dso_lt_45"]}, sim_time=d + 1),
    ]
    for i, (dept, total) in enumerate(_FY2027_BUDGETS_GBP.items()):
        amount = total + (overrun if dept == "delivery" else 0)
        msgs.append(bus.make_message(dept, "finance", f"{dept}.budget_submitted", {
            "department": dept, "fiscal_year": 2027, "amount_gbp": amount,
            "summary": f"{dept} FY2027 budget submission of {amount:,} (envelope {total:,})",
            "due_day": d + 20}, sim_time=d + 5 + i))
    return msgs


def scenario_large_deal_pricing_and_billing(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A 650,000 Forge Scale deal needs a pricing check, CEO approval, then billing on signature.

    Expected chain: sales.proposal_requested + delivery.scoping_completed -> finance.pricing_check_completed
    (sales); sales.deal_approval_requested -> executive.deal_decision_made; sales.deal_won +
    legal.contract_signed -> finance.billing_schedule_created (delivery, customer_success).
    """
    d = clock.day
    amount = params.get("amount_gbp", 650000)
    discount = params.get("discount_pct", 12)
    common = {"client_id": params.get("client_id", "CL-0006"),
              "client_name": params.get("client_name", "Northgate Retail Holdings"),
              "deal_id": params.get("deal_id", "DL-0006"), "proposal_id": "PR-0006",
              "service_line": "forge", "tier": "forge_scale", "amount_gbp": amount}
    return [
        bus.make_message("sales", "finance", "sales.proposal_requested", dict(
            common, summary="Forge Scale proposal for enterprise rollout across stores operations and "
                            "finance, 11 months; sales requests 12% discount", discount_pct=discount,
            due_day=d + 5), sim_time=d),
        bus.make_message("delivery", "finance", "delivery.scoping_completed", dict(
            common, summary="Scoping complete: 1,150 consultant-days and 900 agent-days, blended delivery "
                            "margin 47% before discount", margin_pct=47, due_day=d + 4), sim_time=d + 3),
        bus.make_message("sales", "finance", "sales.deal_approval_requested", dict(
            common, summary="Approval needed: contract value 650,000 with 12% discount (above the 10% "
                            "sales authority); Finance head and CEO sign-off required",
            discount_pct=discount, severity="high", due_day=d + 8), sim_time=d + 6),
        bus.make_message("sales", "finance", "sales.deal_won", dict(
            common, summary="Forge Scale won at 572,000 after approved 12% discount",
            amount_gbp=round(amount * (1 - discount / 100)), due_day=d + 21), sim_time=d + 14),
        bus.make_message("legal", "finance", "legal.contract_signed", dict(
            common, contract_id="CT-0006", amount_gbp=round(amount * (1 - discount / 100)),
            summary="MSA and SOW signed; 30/40/30 milestone billing, 30-day terms"), sim_time=d + 18),
    ]


def scenario_renewal_and_churn_cash_impact(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """One Keep Plus renewal is confirmed while another client churns, moving ARR and cash forecast.

    Expected chain: customer_success.renewal_due + renewal_confirmed -> renewal invoicing plan;
    customer_success.client_churned -> finance.cash_forecast_updated (executive, data) and
    finance.budget_variance_flagged if revenue falls short of plan.
    """
    d = clock.day
    kept = {"client_id": "CL-0007", "client_name": "Aldersgate Wealth Partners", "service_line": "keep",
            "tier": "keep_plus", "amount_gbp": 216000, "contract_id": "CT-0007"}
    lost = {"client_id": "CL-0009", "client_name": "Pennine Mutual Assurance", "service_line": "keep",
            "tier": params.get("tier", "keep_enterprise"), "amount_gbp": params.get("lost_arr_gbp", 480000),
            "contract_id": "CT-0009"}
    return [
        bus.make_message("customer_success", "finance", "customer_success.renewal_due", dict(
            kept, summary="Keep Plus renewal due in 60 days; 18,000 per month, uplift of 3% proposed",
            due_day=d + 60), sim_time=d),
        bus.make_message("customer_success", "finance", "customer_success.renewal_confirmed", dict(
            kept, summary="Renewal confirmed for 12 months at 216,000, billed monthly in advance"),
            sim_time=d + 20),
        bus.make_message("customer_success", "finance", "customer_success.client_churned", dict(
            lost, summary="Client served 90-day notice; Keep Enterprise retainer of 480,000 a year ends; "
                          "final invoice and unused prepayment to be settled", severity="high"),
            sim_time=d + 25),
    ]


def scenario_hiring_and_procurement_spend(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Headcount, a contractor and a vendor purchase need budget checks and spend approval.

    Expected chain: people.offer_accepted + people.new_hire_started -> payroll and headcount cost update;
    people.contractor_engaged and operations.procurement_order_placed -> budget check, with
    finance.budget_variance_flagged when non-budgeted spend exceeds the 50,000 CFO threshold.
    """
    d = clock.day
    po = params.get("po_amount_gbp", 68000)
    return [
        bus.make_message("people", "finance", "people.offer_accepted", {
            "candidate_id": "CAND-0042", "role": "Senior Consultant", "department": "delivery",
            "level": "senior_consultant", "base_salary_gbp": 84000, "start_day": d + 30,
            "summary": "Offer accepted at 84,000 base; loaded cost 107,520 (x1.28)"}, sim_time=d),
        bus.make_message("people", "finance", "people.new_hire_started", {
            "employee_id": "EMP-0057", "role": "Senior Consultant", "department": "delivery",
            "level": "senior_consultant", "base_salary_gbp": 84000,
            "summary": "Senior Consultant started; added to payroll run"}, sim_time=d + 30),
        bus.make_message("people", "finance", "people.contractor_engaged", {
            "contractor_id": "CON-0006", "role": "Data Engineer (contract)", "department": "data",
            "day_rate_gbp": 650, "days": 60, "amount_gbp": 39000,
            "summary": "Contractor engaged for 60 days at 650 per day; IR35 status determination attached"},
            sim_time=d + 10),
        bus.make_message("operations", "finance", "operations.procurement_order_placed", {
            "po_id": "PO-2026-0118", "vendor": "Quillstone Cloud Services", "department": "operations",
            "amount_gbp": po, "budgeted": False,
            "summary": f"Non-budgeted annual licence order of {po:,}; exceeds 50,000 CFO threshold",
            "severity": "medium", "due_day": d + 5}, sim_time=d + 12),
    ]


SCENARIOS = {
    "milestone_to_cash": scenario_milestone_to_cash,
    "overdue_collections": scenario_overdue_collections,
    "annual_budget_cycle": scenario_annual_budget_cycle,
    "large_deal_pricing_and_billing": scenario_large_deal_pricing_and_billing,
    "renewal_and_churn_cash_impact": scenario_renewal_and_churn_cash_impact,
    "hiring_and_procurement_spend": scenario_hiring_and_procurement_spend,
}
