"""Finance department agent for Lumenhall Partners (FP&A, billing, collections, treasury, close, pricing checks).

Owns the order-to-cash spine of CONVENTIONS.md 7.2 (contract signed -> billing schedule -> invoice -> payment /
overdue ladder), the pricing check on proposals, the annual budget cycle, the monthly close, cash forecasting and
spend-commitment control. All figures are modelled assumptions; every company fact is copied from COMPANY.md and
tagged in a comment. Deterministic: no wall clock, no randomness, ids from deterministic counters.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from typing import Any, Optional

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# --------------------------------------------------------------------------------------------------------------
# Company facts (copied from COMPANY.md; section tags in comments)
# --------------------------------------------------------------------------------------------------------------
PRICE_LIST_GBP = {  # COMPANY.md §3.1-3.3 (list prices ex-VAT; Keep = annual price)
    "compass spark": 45_000, "compass sprint": 120_000, "compass programme": 350_000,
    "forge pilot": 90_000, "forge build": 260_000, "forge scale": 650_000,
    "keep essential": 96_000, "keep plus": 216_000, "keep enterprise": 480_000,
}
DAY_RATES_GBP = {  # COMPANY.md §3.5
    "partner": 2_400, "principal": 1_800, "manager": 1_400, "senior_consultant": 1_050,
    "consultant": 800, "analyst": 550, "agent_day": 350,
}
USD_PER_GBP = 1.27                  # COMPANY.md §1 fixed planning rate
PAYMENT_TERMS_DAYS = 30             # COMPANY.md §8 net 30
VAT_RATE = 0.20                     # COMPANY.md §8 (UK clients)
LATE_INTEREST_OVER_BASE = 0.08      # COMPANY.md §8
ASSUMED_BASE_RATE = 0.04            # modelled assumption (economics.md): Bank rate 4.0%
LADDER_REMINDER, LADDER_CALL, LADDER_ESCALATE, LADDER_LEGAL = 31, 38, 45, 60   # COMPANY.md §8 (days from issue)
BILLING_SPLIT = (0.30, 0.40, 0.30)  # COMPANY.md §8 signature / mid-point / acceptance
INVOICE_SLA_BUSINESS_DAYS = 2       # COMPANY.md §8
DISCOUNT_SALES_LIMIT_PCT = 10.0     # COMPANY.md §9.3
DEAL_CEO_APPROVAL_GBP = 500_000     # COMPANY.md §9.3
DEAL_BOARD_APPROVAL_GBP = 1_500_000  # COMPANY.md §9.3
UNBUDGETED_CFO_GBP, UNBUDGETED_CEO_GBP = 50_000, 250_000   # COMPANY.md §9.3
AGENT_PAYMENT_LIMIT_GBP = 10_000    # COMPANY.md §9.4: agents may not approve payments above this
LOADED_COST_FACTOR = 1.28           # COMPANY.md §5.4
COST_OF_REVENUE_RATIO = {1: 0.52, 2: 0.42, 3: 0.36}        # COMPANY.md §5.4 (1 - gross margin)
GROSS_MARGIN_TARGET_PCT = {1: 48.0, 2: 58.0, 3: 64.0}      # COMPANY.md §5.1
EBITDA_GBP = {1: -1_500_000, 2: 1_700_000, 3: 7_200_000}   # COMPANY.md §5.1
REVENUE_PLAN_GBP = {1: 6_000_000, 2: 19_500_000, 3: 46_200_000}   # COMPANY.md §5.1
FIRST_FISCAL_YEAR = 2026
SERIES_A_GBP, SERIES_A_DATE = 10_000_000, date(2026, 5, 29)       # COMPANY.md §1 (Q2 FY2026; day modelled)
OPENING_CASH_GBP = 2_600_000        # modelled assumption: part of the 2025 £3.5m seed unspent at 2026-01-05
MIN_PRICING_MARGIN_PCT = 30.0       # modelled floor below which a quote is sent back for rework
RENEWAL_UPLIFT_PCT = 5.4            # CPI (assumed 3.4%) + 2%, cap 7%  (COMPANY.md §8)
RENEWAL_UPLIFT_CAP_PCT = 7.0

# COMPANY.md §5.4 envelopes in GBP: dept -> ((people Y1..Y3), (non-people Y1..Y3))
ENVELOPES_GBP = {
    "executive": ((500, 800, 900), (100, 250, 400)), "sales": ((600, 1300, 2300), (250, 800, 2300)),
    "marketing": ((280, 600, 1000), (550, 1250, 3500)), "delivery": ((1130, 3000, 8800), (1850, 4400, 6200)),
    "finance": ((210, 480, 800), (100, 250, 700)), "people": ((210, 400, 750), (100, 300, 1100)),
    "legal": ((210, 330, 600), (100, 250, 700)), "it_security": ((260, 470, 900), (200, 450, 1400)),
    "operations": ((200, 400, 750), (100, 300, 900)), "customer_success": ((90, 450, 1240), (50, 340, 390)),
    "product": ((220, 520, 1360), (50, 100, 600)), "data": ((90, 250, 1000), (50, 110, 410)),
}
HEADCOUNT_PLAN = {  # COMPANY.md §6.1 year-end humans (Y1, Y2, Y3)
    "executive": (3, 4, 5), "sales": (5, 14, 26), "marketing": (3, 8, 14), "delivery": (14, 46, 104),
    "finance": (2, 5, 10), "people": (2, 5, 10), "legal": (1, 3, 5), "it_security": (2, 5, 9),
    "operations": (2, 6, 12), "customer_success": (1, 6, 14), "product": (2, 5, 12), "data": (1, 3, 9),
}
BUDGET_DEPARTMENTS = tuple(sorted(ENVELOPES_GBP))

# FY2026 targets (kpis.md); actuals filled in as the simulation runs.
KPIS: list[Kpi] = [
    Kpi("dso_days", "days", 45.0, None, False),                          # COMPANY.md §8
    Kpi("invoice_timeliness_pct", "percent", 95.0, None, True),          # issued within 2 business days
    Kpi("bad_debt_pct_revenue", "percent", 1.0, None, False),            # COMPANY.md §8 (< 1% of revenue)
    Kpi("overdue_ar_over_60_pct", "percent", 8.0, None, False),
    Kpi("collections_ladder_adherence_pct", "percent", 90.0, None, True),
    Kpi("month_end_close_days", "days", 8.0, None, False),
    Kpi("forecast_accuracy_pct", "percent", 90.0, None, True),
    Kpi("cash_runway_months", "months", 18.0, None, True),
    Kpi("gross_margin_pct", "percent", 48.0, None, True),                # COMPANY.md §5.1 FY2026
    Kpi("ebitda_margin_pct", "percent", -25.0, None, True),              # COMPANY.md §5.1 FY2026
    Kpi("budget_variance_pct", "percent", 5.0, None, False),
    Kpi("pricing_check_sla_pct", "percent", 95.0, None, True),
]


def _num(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _s(value: Any, default: str = "") -> str:
    return default if value is None else str(value)


def _first(body: dict, *keys: str, default: Any = None) -> Any:
    for key in keys:
        if body.get(key) not in (None, ""):
            return body[key]
    return default


def _slug(topic: str) -> str:
    return topic.replace(".", "_")


class FinanceAgent(DepartmentAgent):
    """Lumenhall finance: CFO-office agent. Drafts, reconciles, monitors and proposes; humans approve (§9.3/§9.4)."""

    SUBSCRIBES = subscribes_for("finance")
    PUBLISHES = publishes_for("finance")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.kpis: dict[str, Kpi] = {k.name: k for k in KPIS}
        self.state.update({
            "price_list": dict(PRICE_LIST_GBP), "proposals": {}, "schedules": {}, "invoices": {},
            "inv_seq": {}, "disputes": {}, "decisions": {}, "bookings_gbp": 0.0, "billed_net_ytd": 0.0,
            "collected_gross_ytd": 0.0, "bad_debt_gbp": 0.0, "credit_notes": 0, "invoices_raised": 0,
            "on_time_invoices": 0, "pricing_checks": 0, "pricing_on_time": 0, "pricing_days_total": 0.0, "margin_sum": 0.0,
            "days_to_pay": [], "periods": {}, "close_queue": [], "cur_month": None, "closes": 0,
            "budget_cycles": {}, "approved_budget": {}, "commitments": {}, "flagged": {}, "headcount": {}, "open_requisitions": {},
            "contractors": {}, "vendors": {}, "forecast_errors": [], "crisis_mode": False, "series_a_booked": False,
            "last_cash_day": -1, "hire_requested": False, "unapplied_cash_gbp": 0.0, "renewals": {},
            "capacity": {}, "okrs": {}, "board_packs": 0, "cash_gbp": None, "handled": 0, "unmapped": 0,
            "billing_exceptions": 0,
        })
        self._handlers = self._build_handlers()

    # ------------------------------------------------------------------ dispatch
    def _build_handlers(self) -> dict:
        h = {
            "sales.proposal_requested": self._on_proposal_requested,
            "delivery.scoping_completed": self._on_scoping_completed,
            "sales.deal_approval_requested": self._on_deal_approval_requested,
            "sales.deal_won": self._on_deal_won,
            "executive.deal_decision_made": self._on_deal_decision,
            "legal.contract_signed": self._on_contract_signed,
            "delivery.engagement_kickoff": self._on_kickoff,
            "delivery.milestone_reached": self._on_milestone,
            "delivery.engagement_completed": self._on_engagement_completed,
            "delivery.scope_change_requested": self._on_scope_change,
            "external.client_payment_received": self._on_payment,
            "legal.client_dispute_raised": self._on_dispute,
            "sales.renewal_proposal_sent": self._on_renewal_proposal,
            "customer_success.renewal_due": self._on_renewal_due,
            "customer_success.renewal_confirmed": self._on_renewal_confirmed,
            "customer_success.client_churned": self._on_churn,
            "product.pricing_change_proposed": self._on_pricing_change_proposed,
            "executive.pricing_change_approved": self._on_pricing_change_approved,
            "executive.budget_approved": self._on_budget_approved,
            "executive.headcount_approved": self._on_headcount_approved,
            "executive.crisis_declared": self._on_crisis,
            "executive.board_meeting_held": self._on_board_meeting,
            "executive.okrs_set": self._on_okrs,
            "executive.strategy_updated": self._on_strategy,
            "delivery.capacity_forecast_updated": self._on_capacity_forecast,
            "data.forecast_updated": self._on_data_forecast,
            "data.kpi_report_published": self._on_data_kpi_report,
            "marketing.campaign_launched": self._on_campaign_launched,
            "operations.procurement_order_placed": self._on_procurement_order,
            "operations.vendor_review_requested": self._on_vendor_review_requested,
            "operations.vendor_approved": self._on_vendor_approved,
            "it_security.vendor_risk_assessed": self._on_vendor_risk,
            "people.requisition_opened": self._on_requisition_opened,
            "people.offer_accepted": self._on_offer_accepted,
            "people.new_hire_started": self._on_new_hire_started,
            "people.employee_left": self._on_employee_left,
            "people.contractor_engaged": self._on_contractor_engaged,
        }
        for dept in BUDGET_DEPARTMENTS:
            if dept != "finance":
                h[f"{dept}.budget_submitted"] = self._on_budget_submitted
        return h

    def handle(self, message: Message) -> list[Message]:
        handler = self._handlers.get(message.topic)
        self.log_event(f"finance.activity.{_slug(message.topic)}", f"{message.topic} from {message.sender}",
                       message_id=message.id, known=handler is not None)
        if handler is None:
            self.state["unmapped"] += 1
            return []
        body = message.body if isinstance(message.body, dict) else {}
        out = handler(message, body) or []
        self.state["handled"] += 1
        self._refresh_kpis()
        return out

    # ------------------------------------------------------------------ small helpers
    def _fy(self) -> int:
        return max(1, min(3, self.clock.year_index))

    def _bday_offset(self, n: int) -> int:
        """Calendar days from today until n business days ahead."""
        days, left = 0, n
        while left > 0:
            days += 1
            if (self.clock.date + timedelta(days=days)).weekday() < 5:
                left -= 1
        return days

    def _narrative(self, prompt: str, fallback: str) -> str:
        try:
            text = self.ask_llm(prompt)
        except Exception:  # noqa: BLE001 - narrative is optional, never block the ledger
            return fallback
        return text if text else fallback

    def _ids(self, body: dict) -> dict:
        return {k: body[k] for k in ("client_id", "deal_id", "proposal_id", "contract_id", "engagement_id")
                if body.get(k) not in (None, "")}

    def _task(self, title: str, due: Optional[int] = None, priority: str = "medium") -> str:
        return self.create_task(title, due, priority).id

    def _set_kpi(self, name: str, actual: float) -> None:
        self.kpis[name] = replace(self.kpis[name], actual=round(actual, 2))

    def _product(self, body: dict, value: float = 0.0) -> str:
        raw = _s(_first(body, "product", "offer", "service", "offering", "tier", default="")).lower().strip()
        if raw in self.state["price_list"]:
            return raw
        for name in self.state["price_list"]:
            if name in raw and raw:
                return name
        for name, price in self.state["price_list"].items():
            if value and abs(price - value) < 1:
                return name
        return "fixed fee"

    def _value(self, body: dict, product: str) -> float:
        v = _num(_first(body, "value_gbp", "contract_value_gbp", "total_contract_value_gbp", "amount_gbp",
                        "price_gbp", "quoted_price_gbp", "tcv_gbp", default=0))
        return v if v > 0 else float(self.state["price_list"].get(product, 0))

    # ------------------------------------------------------------------ pricing check
    def _on_proposal_requested(self, msg: Message, body: dict) -> list[Message]:
        key = _s(_first(body, "proposal_id", "deal_id", default=msg.id))
        product = self._product(body)
        self.state["proposals"][key] = {
            "requested_day": self.clock.day, "ids": self._ids(body), "product": product,
            "value": self._value(body, product), "discount_pct": _num(body.get("discount_pct")),
            "terms": int(_num(body.get("payment_terms_days"), PAYMENT_TERMS_DAYS)), "checked": False,
        }
        self._task(f"Pricing check for {key} ({product}); awaiting delivery scope", self.clock.day + 2)
        return []

    def _on_scoping_completed(self, msg: Message, body: dict) -> list[Message]:
        key = _s(_first(body, "proposal_id", "deal_id", default=msg.id))
        prop = self.state["proposals"].setdefault(key, {
            "requested_day": self.clock.day, "ids": {}, "product": "fixed fee", "value": 0.0, "discount_pct": 0.0,
            "terms": PAYMENT_TERMS_DAYS, "checked": False})
        prop["ids"].update(self._ids(body))
        product = self._product(body) if _first(body, "product", "offer", "service") else prop["product"]
        prop["product"] = product
        quote = _num(_first(body, "quoted_price_gbp", "price_gbp", "value_gbp", "amount_gbp"), prop["value"])
        prop["value"] = quote or prop["value"]
        prop["discount_pct"] = _num(body.get("discount_pct"), prop["discount_pct"])
        prop["effort"] = body.get("effort_days") if isinstance(body.get("effort_days"), dict) else None
        prop["terms"] = int(_num(body.get("payment_terms_days"), prop["terms"]))
        return self._run_pricing_check(msg, key, prop, body)

    def _effort_cost(self, effort: Any) -> float:
        """Standard delivery cost of the scoped effort: day rate x cost ratio (FY cost of revenue, COMPANY.md §5.4)."""
        ratio = COST_OF_REVENUE_RATIO[self._fy()]
        total = 0.0
        if isinstance(effort, dict):
            for level, days in effort.items():
                total += DAY_RATES_GBP.get(_s(level).lower(), 0) * _num(days)
        return total * ratio

    def _run_pricing_check(self, msg: Message, key: str, prop: dict, body: dict, change_order: bool = False,
                           renewal: bool = False, delay: Optional[int] = None) -> list[Message]:
        quote = prop["value"]
        list_price = float(self.state["price_list"].get(prop["product"], 0)) or quote
        discount = prop["discount_pct"]
        if not discount and list_price and quote and quote < list_price:
            discount = round((1 - quote / list_price) * 100, 1)
        cost = self._effort_cost(prop.get("effort")) or quote * COST_OF_REVENUE_RATIO[self._fy()]
        margin = round((1 - cost / quote) * 100, 1) if quote else 0.0
        issues: list[str] = []
        approvers: list[str] = []
        if discount > DISCOUNT_SALES_LIMIT_PCT:
            issues.append(f"discount {discount:.1f}% exceeds {DISCOUNT_SALES_LIMIT_PCT:.0f}% sales authority")
            approvers += ["Chief Financial Officer", "Chief Executive Officer"]
        if prop["terms"] != PAYMENT_TERMS_DAYS:
            issues.append(f"non-standard payment terms net {prop['terms']}")
            approvers += [a for a in ("Chief Financial Officer", "Chief Executive Officer") if a not in approvers]
        if quote > DEAL_BOARD_APPROVAL_GBP:
            issues.append("contract value above £1.5m: Board notified and approves")
            approvers.append("Board")
        elif quote >= DEAL_CEO_APPROVAL_GBP:
            issues.append("contract value at or above £500k: CEO approval via deal_approval_requested")
            approvers.append("Chief Executive Officer")
        status = "approved"
        if margin < MIN_PRICING_MARGIN_PCT and quote:
            status, _ = "rework_required", issues.append(f"margin {margin:.1f}% below {MIN_PRICING_MARGIN_PCT:.0f}% floor")
        elif issues:
            status = "approval_required"
        if delay is None:
            delay = 2 if quote >= DEAL_CEO_APPROVAL_GBP else 1
        turnaround = (self.clock.day + delay) - prop.get("requested_day", self.clock.day)
        prop["checked"] = True
        self.state["pricing_checks"] += 1
        self.state["pricing_on_time"] += 1 if turnaround <= 1 else 0
        self.state["pricing_days_total"] += max(turnaround, 0)
        self.state["margin_sum"] += margin
        rationale = self._narrative(
            f"Summarise the pricing check for {key}: {prop['product']} at £{quote:,.0f}, margin {margin}%, "
            f"discount {discount}%, issues {issues}", f"{prop['product']} priced at £{quote:,.0f}, margin {margin}%.")
        out = self.emit("finance.pricing_check_completed", {
            **prop["ids"], **{k: v for k, v in self._ids(body).items()}, "proposal_id": key if key.startswith("PR-") else
            body.get("proposal_id", key), "product": prop["product"], "quoted_price_gbp": quote,
            "list_price_gbp": list_price, "discount_pct": discount, "gross_margin_pct": margin, "status": status,
            "payment_terms_days": prop["terms"], "issues": issues, "required_approvers": approvers,
            "change_order": change_order, "renewal": renewal, "turnaround_days": turnaround, "rationale": rationale,
        }, recipient="sales", reply_to=msg.id, delay_days=delay)
        return [out]

    def _on_deal_approval_requested(self, msg: Message, body: dict) -> list[Message]:
        key = _s(_first(body, "deal_id", "proposal_id", default=msg.id))
        value = _num(_first(body, "value_gbp", "contract_value_gbp", "total_contract_value_gbp", "amount_gbp"))
        discount = _num(body.get("discount_pct"))
        self.state["decisions"][key] = {"status": "finance_review", "value": value, "day": self.clock.day}
        route = "Board" if value > DEAL_BOARD_APPROVAL_GBP else "Chief Executive Officer"
        self._task(f"CFO margin and credit review for {key} (£{value:,.0f}, {discount:.1f}% discount) before {route}",
                   self.clock.day + 2, "high")
        prop = {"requested_day": self.clock.day, "ids": self._ids(body), "product": self._product(body, value),
                "value": value, "discount_pct": discount, "terms": int(_num(body.get("payment_terms_days"),
                PAYMENT_TERMS_DAYS)), "checked": False}
        return self._run_pricing_check(msg, key, prop, body, delay=1)

    def _on_deal_decision(self, msg: Message, body: dict) -> list[Message]:
        key = _s(_first(body, "deal_id", "proposal_id", default=msg.id))
        decision = _s(_first(body, "decision", "status", default="unknown")).lower()
        self.state["decisions"][key] = {"status": decision, "day": self.clock.day}
        if decision in ("approved", "approve", "conditionally_approved"):
            self._task(f"Run credit check and set up customer record for approved deal {key}", self.clock.day + 3)
        return []

    def _on_pricing_change_proposed(self, msg: Message, body: dict) -> list[Message]:
        ref = _s(_first(body, "change_id", "proposal_id", "product", default=msg.id))
        product = self._product(body)
        new_price = _num(_first(body, "new_price_gbp", "proposed_price_gbp", "price_gbp"),
                         self.state["price_list"].get(product, 0))
        old = float(self.state["price_list"].get(product, new_price))
        change_pct = round((new_price / old - 1) * 100, 1) if old else 0.0
        self._task(f"Model margin and ARR impact of pricing change {ref} ({change_pct:+.1f}% on {product})",
                   self.clock.day + 3)
        prop = {"requested_day": self.clock.day, "ids": {}, "product": product, "value": new_price,
                "discount_pct": 0.0, "terms": PAYMENT_TERMS_DAYS, "checked": False}
        prop["ids"] = {}
        return self._run_pricing_check(msg, ref, prop, {"proposal_id": ref}, delay=2)

    def _on_pricing_change_approved(self, msg: Message, body: dict) -> list[Message]:
        product = self._product(body)
        new_price = _num(_first(body, "new_price_gbp", "approved_price_gbp", "price_gbp"))
        if product in self.state["price_list"] and new_price > 0:
            self.state["price_list"][product] = new_price
            self._task(f"Load new {product} list price £{new_price:,.0f} into billing; grandfather signed contracts",
                       self.clock.day + 5)
        return []

    def _on_renewal_proposal(self, msg: Message, body: dict) -> list[Message]:
        key = _s(_first(body, "proposal_id", "renewal_id", "client_id", default=msg.id))
        product = self._product(body)
        current = _num(_first(body, "current_value_gbp", "current_acv_gbp"), self.state["price_list"].get(product, 0))
        value = _num(_first(body, "value_gbp", "proposed_value_gbp", "amount_gbp"),
                     current * (1 + RENEWAL_UPLIFT_PCT / 100))
        uplift = round((value / current - 1) * 100, 1) if current else 0.0
        prop = {"requested_day": self.clock.day, "ids": self._ids(body), "product": product, "value": value,
                "discount_pct": 0.0, "terms": PAYMENT_TERMS_DAYS, "checked": False}
        out = self._run_pricing_check(msg, key, prop, body, renewal=True, delay=1)
        if uplift > RENEWAL_UPLIFT_CAP_PCT:
            self._task(f"Renewal {key} uplift {uplift:.1f}% exceeds CPI+2% cap of {RENEWAL_UPLIFT_CAP_PCT:.0f}%", None, "high")
        return out

    # ------------------------------------------------------------------ order to cash
    def _on_deal_won(self, msg: Message, body: dict) -> list[Message]:
        product = self._product(body)
        value = self._value(body, product)
        self.state["bookings_gbp"] += value
        self._task(f"Credit check, VAT/KYC and PO capture for won deal {_s(body.get('deal_id'), msg.id)} "
                   f"(£{value:,.0f})", self.clock.day + 3, "high" if value >= DEAL_CEO_APPROVAL_GBP else "medium")
        return []

    def _on_contract_signed(self, msg: Message, body: dict) -> list[Message]:
        product = self._product(body)
        value = self._value(body, product)
        ids = self._ids(body)
        key = _s(_first(body, "contract_id", "engagement_id", "deal_id", default=msg.id))
        country = _s(body.get("country"), "UK").upper()
        terms = int(_num(body.get("payment_terms_days"), PAYMENT_TERMS_DAYS))
        if product.startswith("keep"):
            monthly = round(value / 12, 2)
            milestones = [{"idx": 0, "label": "month 1 in advance", "pct": round(100 / 12, 2), "amount": monthly,
                           "trigger": "signature", "status": "open", "invoice_id": None}]
            kind = "retainer"
        else:
            kind = "fixed"
            labels = (("signature", "signature"), ("mid-point milestone", "milestone"), ("acceptance", "acceptance"))
            milestones = [{"idx": i, "label": lbl, "pct": BILLING_SPLIT[i] * 100,
                           "amount": round(value * BILLING_SPLIT[i], 2), "trigger": trg, "status": "open",
                           "invoice_id": None} for i, (lbl, trg) in enumerate(labels)]
        sched = {"key": key, "ids": ids, "product": product, "total_net": value, "country": country, "terms": terms,
                 "kind": kind, "milestones": milestones, "months_billed": 0, "active": True,
                 "po_number": body.get("po_number"), "po_required": bool(body.get("po_required")), "next_bill_day": None,
                 "expenses_cap_gbp": round(value * 0.05, 2), "renewal": bool(body.get("renewal"))}
        self.state["schedules"][key] = sched
        out: list[Message] = []
        out.append(self.emit("finance.billing_schedule_created", {
            **ids, "schedule_id": f"BS-{key}", "product": product, "total_net_gbp": value, "payment_terms_days": terms,
            "currency": "USD" if country == "US" else "GBP", "vat_rate": 0.0 if country == "US" else VAT_RATE,
            "milestones": [{"label": m["label"], "pct": m["pct"], "amount_gbp": m["amount"], "trigger": m["trigger"]}
                           for m in milestones],
            "billing_model": "monthly in advance, 12-month minimum term" if kind == "retainer" else
            "30% signature / 40% mid-point / 30% acceptance", "expenses_cap_gbp": sched["expenses_cap_gbp"],
        }, reply_to=msg.id, delay_days=1))
        if value:
            out += self._bill_milestone(sched, 0, trigger="signature", reply_to=msg.id,
                                        extra_delay=self._bday_offset(INVOICE_SLA_BUSINESS_DAYS))
        else:
            self.state["billing_exceptions"] += 1
            self._task(f"Contract {key} has no value on signature message; confirm schedule with Legal", None, "high")
        if kind == "retainer":
            sched["months_billed"] = 1
        return out

    def _find_schedule(self, body: dict) -> Optional[dict]:
        for k in ("contract_id", "engagement_id", "deal_id"):
            if body.get(k) and body[k] in self.state["schedules"]:
                return self.state["schedules"][body[k]]
        for s in self.state["schedules"].values():
            if any(body.get(k) and s["ids"].get(k) == body[k] for k in ("engagement_id", "contract_id", "deal_id")):
                return s
        client = body.get("client_id")
        if client:
            matches = [s for s in self.state["schedules"].values() if s["ids"].get("client_id") == client and s["active"]]
            if matches:
                return matches[-1]
        return None

    def _next_invoice_id(self) -> str:
        year = self.clock.date.year
        seq = self.state["inv_seq"].get(year, 0) + 1
        self.state["inv_seq"][year] = seq
        return f"INV-{year}-{seq:04d}"

    def _bill_milestone(self, sched: dict, idx: int, trigger: str, reply_to: Optional[str] = None,
                        extra_delay: int = 0, amount: Optional[float] = None, label: Optional[str] = None) -> list[Message]:
        ms = sched["milestones"][idx]
        if ms["status"] == "invoiced":  # duplicate-billing control
            self.state["billing_exceptions"] += 1
            self.log_event("finance.activity.duplicate_billing_blocked", f"{sched['key']} milestone {idx} already billed",
                           invoice_id=ms["invoice_id"])
            return []
        net = round(amount if amount is not None else ms["amount"], 2)
        return self._issue_invoice(sched, ms["label"] if label is None else label, net, trigger, reply_to, extra_delay, ms)

    def _issue_invoice(self, sched: dict, label: str, net: float, trigger: str, reply_to: Optional[str],
                       delay: int, ms: Optional[dict] = None) -> list[Message]:
        if net <= 0:
            return []
        hold_for_po = sched["po_required"] and not sched["po_number"]
        if hold_for_po:
            delay += 3
            self._task(f"Obtain purchase order for {sched['key']} before invoicing is released", self.clock.day + 3, "high")
        inv_id = self._next_invoice_id()
        issue_day = self.clock.day + delay
        us = sched["country"] == "US"
        vat = 0.0 if us else round(net * VAT_RATE, 2)
        terms = sched["terms"]
        rec = {"id": inv_id, "schedule": sched["key"], "ids": dict(sched["ids"]), "label": label, "net": net, "vat": vat,
               "gross": round(net + vat, 2), "issue_day": issue_day, "due_day": issue_day + terms, "terms": terms,
               "paid": 0.0, "status": "open", "stages": [], "hold": False, "trigger": trigger,
               "currency": "USD" if us else "GBP"}
        self.state["invoices"][inv_id] = rec
        if ms is not None:
            ms["status"], ms["invoice_id"] = "invoiced", inv_id
        self.state["invoices_raised"] += 1
        sla_ok = delay <= self._bday_offset(INVOICE_SLA_BUSINESS_DAYS) and not hold_for_po
        self.state["on_time_invoices"] += 1 if sla_ok else 0
        self.state["billed_net_ytd"] += net
        period = self.clock.date_of(issue_day).strftime("%Y-%m")
        self._period(period)["billed_net"] += net
        needs_review = net >= 100_000
        if needs_review:
            self._task(f"CFO review of invoice {inv_id} (£{net:,.0f} net) before release", issue_day, "high")
        body = {**sched["ids"], "invoice_id": inv_id, "schedule_id": f"BS-{sched['key']}", "description": label,
                "net_gbp": net, "vat_gbp": vat, "gross_gbp": rec["gross"], "currency": rec["currency"],
                "amount_usd": round(rec["gross"] * USD_PER_GBP, 2) if us else None, "issue_day": issue_day,
                "due_day": rec["due_day"], "payment_terms_days": terms, "trigger": trigger,
                "within_sla": sla_ok, "human_release_required": needs_review}
        return [self.emit("finance.invoice_issued", body, reply_to=reply_to, delay_days=delay)]

    def _period(self, period: str) -> dict:
        return self.state["periods"].setdefault(period, {"billed_net": 0.0, "collected": 0.0, "credit_notes": 0.0})

    def _on_kickoff(self, msg: Message, body: dict) -> list[Message]:
        sched = self._find_schedule(body)
        if sched is None:
            self.state["billing_exceptions"] += 1
            self._task(f"Engagement {_s(body.get('engagement_id'), msg.id)} kicked off with no billing schedule; "
                       "chase Legal for signed contract", self.clock.day + 1, "critical")
            return []
        sched["ids"].update(self._ids(body))
        if sched["kind"] == "retainer" and sched["next_bill_day"] is None:
            nxt = self.clock.date.replace(day=1) + timedelta(days=32)
            sched["next_bill_day"] = self.clock.day_of(nxt.replace(day=1))
        self._task(f"Open project code and WIP ledger for {sched['key']}", self.clock.day + 1, "low")
        return []

    def _milestone_index(self, sched: dict, body: dict) -> Optional[int]:
        n = len(sched["milestones"])
        no = body.get("milestone_no", body.get("milestone_index"))
        if isinstance(no, int) and not isinstance(no, bool) and 1 <= no <= n:
            return no - 1
        name = _s(_first(body, "milestone", "milestone_name", "name", default="")).lower()
        if any(w in name for w in ("final", "accept", "complet", "handover")):
            return n - 1
        if "mid" in name and n > 1:
            return 1
        for ms in sched["milestones"]:
            if ms["status"] == "open":
                return ms["idx"]
        return None

    def _on_milestone(self, msg: Message, body: dict) -> list[Message]:
        sched = self._find_schedule(body)
        if sched is None:
            # No signed-contract schedule on file: bill the accepted milestone from the message itself (so cash is
            # not delayed) on an ad-hoc one-line schedule, and raise a task to reconcile it with Legal.
            self.state["billing_exceptions"] += 1
            ref = _s(_first(body, "engagement_id", "contract_id", "deal_id", default=msg.id))
            self._task(f"Milestone accepted with no billing schedule ({ref}); invoiced ad hoc, confirm with Legal",
                       self.clock.day + 1, "high")
            amount = _num(_first(body, "invoice_amount_gbp", "amount_gbp", "net_gbp"))
            if amount <= 0:
                return []
            label = _s(_first(body, "milestone", "milestone_name", default="milestone acceptance"))
            sched = {"key": ref, "ids": self._ids(body), "product": self._product(body, amount), "total_net": amount,
                     "country": _s(body.get("country"), "UK").upper(), "terms": int(_num(body.get("payment_terms_days"),
                     PAYMENT_TERMS_DAYS)), "kind": "fixed", "months_billed": 0, "active": True, "po_number": body.get("po_number"),
                     "po_required": bool(body.get("po_required")), "next_bill_day": None, "adhoc": True,
                     "expenses_cap_gbp": round(amount * 0.05, 2), "renewal": False,
                     "milestones": [{"idx": 0, "label": label, "pct": 100.0, "amount": amount,
                                     "trigger": "milestone", "status": "open", "invoice_id": None}]}
            self.state["schedules"][ref] = sched
        if sched["kind"] == "retainer":
            return []
        idx = self._milestone_index(sched, body)
        if idx is None:
            self.log_event("finance.activity.milestone_all_billed", sched["key"])
            return []
        amount = _num(body.get("invoice_amount_gbp")) or None
        return self._bill_milestone(sched, idx, trigger="milestone_acceptance", reply_to=msg.id,
                                    extra_delay=self._bday_offset(INVOICE_SLA_BUSINESS_DAYS), amount=amount)

    def _on_engagement_completed(self, msg: Message, body: dict) -> list[Message]:
        sched = self._find_schedule(body)
        out: list[Message] = []
        if sched is None:
            self._task(f"Engagement {_s(body.get('engagement_id'), msg.id)} completed with no billing schedule", None, "high")
            return out
        if sched["kind"] == "fixed":
            open_ms = [m for m in sched["milestones"] if m["status"] == "open"]
            for ms in open_ms:  # acceptance recorded: bill whatever is left, oldest first
                out += self._bill_milestone(sched, ms["idx"], trigger="engagement_completed", reply_to=msg.id,
                                            extra_delay=self._bday_offset(INVOICE_SLA_BUSINESS_DAYS))
            sched["active"] = False
        self._task(f"Close WIP and release project {sched['key']}; margin review against pricing check", self.clock.day + 5, "low")
        return out

    def _on_scope_change(self, msg: Message, body: dict) -> list[Message]:
        key = _s(_first(body, "change_id", "scope_change_id", "engagement_id", default=msg.id))
        sched = self._find_schedule(body)
        days = _num(body.get("additional_days"))
        level = _s(body.get("level"), "senior_consultant").lower()
        value = _num(_first(body, "value_gbp", "amount_gbp", "change_value_gbp"), days * DAY_RATES_GBP.get(level, 1_050))
        if sched is not None and value > 0:  # change orders at rate card, signed before work starts (§8)
            sched["total_net"] += value
            idx = len(sched["milestones"])
            sched["milestones"].append({"idx": idx, "label": f"change order {key}", "pct": 0.0, "amount": value,
                                        "trigger": "change_order_signed", "status": "open", "invoice_id": None})
        self._task(f"Confirm change order {key} (£{value:,.0f}) is signed before billable work starts",
                   self.clock.day + 2, "high")
        prop = {"requested_day": self.clock.day, "ids": self._ids(body),
                "product": sched["product"] if sched else "fixed fee", "value": value, "discount_pct": 0.0,
                "terms": sched["terms"] if sched else PAYMENT_TERMS_DAYS, "checked": False}
        # rate-card change orders are priced from the day-rate card, so list price is the quote itself
        self.state["price_list"].setdefault("change order", value)
        return self._run_pricing_check(msg, key, prop, {**body, "proposal_id": key}, change_order=True, delay=1)

    # ------------------------------------------------------------------ cash in and collections
    def _days_late_interest(self, rec: dict, day: int) -> float:
        overdue = max(0, day - rec["due_day"])
        rate = ASSUMED_BASE_RATE + LATE_INTEREST_OVER_BASE
        return round((rec["gross"] - rec["paid"]) * rate * overdue / 365, 2)

    def _on_payment(self, msg: Message, body: dict) -> list[Message]:
        amount = _num(_first(body, "amount_gbp", "amount", "gross_gbp"))
        inv = self.state["invoices"].get(_s(body.get("invoice_id")))
        if inv is None:
            candidates = [i for i in self.state["invoices"].values() if i["status"] != "paid" and
                          (not body.get("client_id") or i["ids"].get("client_id") == body.get("client_id"))]
            exact = [i for i in candidates if amount and abs((i["gross"] - i["paid"]) - amount) < 0.01]
            pick = exact or candidates
            inv = sorted(pick, key=lambda i: (i["issue_day"], i["id"]))[0] if pick else None
        if inv is None or amount <= 0:
            self.state["unapplied_cash_gbp"] += max(amount, 0)
            self._task(f"Unapplied receipt £{amount:,.0f} from {_s(body.get('client_id'), 'unknown client')}; "
                       "bank reconciliation exception", self.clock.day + 1, "high")
            return [self.emit("finance.payment_received", {
                **self._ids(body), "invoice_id": None, "amount_gbp": amount, "status": "unapplied",
                "reconciled": False}, reply_to=msg.id, delay_days=1)]
        outstanding = round(inv["gross"] - inv["paid"], 2)
        applied = min(amount, outstanding)
        inv["paid"] = round(inv["paid"] + applied, 2)
        self.state["unapplied_cash_gbp"] += round(amount - applied, 2)
        self.state["collected_gross_ytd"] += applied
        self._period(self.clock.date.strftime("%Y-%m"))["collected"] += applied
        settled = inv["paid"] >= inv["gross"] - 0.01
        if settled:
            inv["status"], inv["paid_day"] = "paid", self.clock.day
            self.state["days_to_pay"].append(self.clock.day - inv["issue_day"])
        status = "settled" if settled else "part_paid"
        interest = self._days_late_interest(inv, self.clock.day) if settled else 0.0
        return [self.emit("finance.payment_received", {
            **inv["ids"], **self._ids(body), "invoice_id": inv["id"], "amount_gbp": applied, "status": status,
            "outstanding_gbp": round(inv["gross"] - inv["paid"], 2), "days_to_pay": self.clock.day - inv["issue_day"],
            "late_interest_claimable_gbp": interest, "reconciled": True, "overpayment_gbp": round(amount - applied, 2),
        }, reply_to=msg.id, delay_days=1)]

    def _on_dispute(self, msg: Message, body: dict) -> list[Message]:
        client = body.get("client_id")
        held = 0
        for inv in self.state["invoices"].values():
            matches = (body.get("invoice_id") and inv["id"] == body["invoice_id"]) or \
                (not body.get("invoice_id") and client and inv["ids"].get("client_id") == client)
            if matches and inv["status"] != "paid":
                inv["hold"] = True
                held += 1
        self.state["disputes"][_s(_first(body, "dispute_id", "client_id", default=msg.id))] = {
            "day": self.clock.day, "held": held, "reason": _s(body.get("reason"), "unspecified")}
        self._task(f"Collections paused on {held} invoice(s) for {_s(client, 'client')} (dispute); agree credit note "
                   "or reinstate ladder", self.clock.day + 5, "high")
        return []

    def _collections(self) -> list[Message]:
        out: list[Message] = []
        for inv_id in sorted(self.state["invoices"]):
            inv = self.state["invoices"][inv_id]
            if inv["status"] == "paid" or inv["hold"] or self.clock.day < inv["issue_day"]:
                continue
            age = self.clock.day - inv["issue_day"]
            outstanding = round(inv["gross"] - inv["paid"], 2)
            base = {**inv["ids"], "invoice_id": inv_id, "amount_gbp": outstanding, "days_outstanding": age,
                    "days_overdue": max(0, age - inv["terms"]), "late_interest_gbp": self._days_late_interest(inv, self.clock.day)}
            if age >= LADDER_REMINDER and "reminder" not in inv["stages"]:
                inv["stages"].append("reminder")
                out.append(self.emit("finance.invoice_overdue", {**base, "stage": "reminder"}))
            if age >= LADDER_CALL and "call" not in inv["stages"]:
                inv["stages"].append("call")
                self._task(f"Chase call to AP contact for {inv_id} (£{outstanding:,.0f}, day {age})", self.clock.day + 2, "medium")
            if age >= LADDER_ESCALATE and "escalate" not in inv["stages"]:
                inv["stages"].append("escalate")
                out.append(self.emit("finance.collections_escalated", {
                    **base, "stage": "finance_head_escalation", "owner": "Chief Financial Officer"}))
            if age >= LADDER_LEGAL and "legal" not in inv["stages"]:
                inv["stages"].append("legal")
                out.append(self.emit("finance.collections_escalated", {
                    **base, "stage": "legal_letter", "owner": "General Counsel"}))
            if age >= 120 and "written_off" not in inv["stages"]:  # provision proposal; write-off itself needs CFO + CEO
                inv["stages"].append("written_off")
                self.state["bad_debt_gbp"] += round(outstanding / (1 + (VAT_RATE if inv["vat"] else 0)), 2)
                self._task(f"Proposed bad debt write-off {inv_id} £{outstanding:,.0f}: CFO and CEO sign-off", None, "high")
        return out

    # ------------------------------------------------------------------ renewals and churn
    def _on_renewal_due(self, msg: Message, body: dict) -> list[Message]:
        value = _num(_first(body, "value_gbp", "renewal_value_gbp", "acv_gbp", "amount_gbp"))
        key = _s(_first(body, "renewal_id", "contract_id", "client_id", default=msg.id))
        self.state["renewals"][key] = {"due_day": _num(body.get("renewal_day"), self.clock.day + 60), "value": value,
                                       "status": "due"}
        self._task(f"Renewal {key}: confirm term, CPI+2% uplift (cap {RENEWAL_UPLIFT_CAP_PCT:.0f}%) and open AR "
                   "before renewal proposal", self.clock.day + 5)
        return []

    def _on_renewal_confirmed(self, msg: Message, body: dict) -> list[Message]:
        key = _s(_first(body, "renewal_id", "contract_id", "client_id", default=msg.id))
        if key in self.state["renewals"]:
            self.state["renewals"][key]["status"] = "confirmed"
        payload = {**body, "renewal": True}
        product = self._product(body)
        value = self._value(body, product)
        if not value:
            self._task(f"Renewal confirmed for {key} without value; confirm billing with Customer Success", None, "high")
            return []
        payload.setdefault("contract_id", _s(_first(body, "renewal_contract_id", "contract_id",
                                                    default=f"{key}-R")))
        if payload["contract_id"] in self.state["schedules"]:
            payload["contract_id"] = f"{payload['contract_id']}-R{self.clock.day}"
        return self._on_contract_signed(msg, payload)

    def _on_churn(self, msg: Message, body: dict) -> list[Message]:
        client = body.get("client_id")
        out: list[Message] = []
        for s in self.state["schedules"].values():
            if client and s["ids"].get("client_id") == client:
                s["active"] = False
                for ms in s["milestones"]:
                    if ms["status"] == "open":
                        ms["status"] = "cancelled"
        exposure = 0.0
        for inv in sorted(self.state["invoices"].values(), key=lambda i: i["id"]):
            if client and inv["ids"].get("client_id") == client and inv["status"] != "paid" and not inv["hold"]:
                exposure += inv["gross"] - inv["paid"]
                age = self.clock.day - inv["issue_day"]
                if age >= LADDER_REMINDER and "escalate" not in inv["stages"]:
                    inv["stages"].append("escalate")
                    out.append(self.emit("finance.collections_escalated", {
                        **inv["ids"], "invoice_id": inv["id"], "amount_gbp": round(inv["gross"] - inv["paid"], 2),
                        "days_outstanding": age, "stage": "churned_client_exposure", "owner": "Chief Financial Officer"},
                        reply_to=msg.id))
        self._task(f"Churned client {_s(client, 'unknown')}: stop billing, cancel future milestones, review "
                   f"£{exposure:,.0f} open exposure for provision", self.clock.day + 3, "high")
        return out

    # ------------------------------------------------------------------ budget cycle
    def _cycle_for(self, fy_year: int) -> dict:
        key = f"BUD-{fy_year}"
        return self.state["budget_cycles"].setdefault(key, {
            "id": key, "fy": fy_year, "opened_day": self.clock.day, "deadline_day": self.clock.day + 21,
            "submissions": {}, "consolidated": False, "finance_submitted": False})

    def _open_budget_cycle(self, fy_year: int) -> list[Message]:
        cycle = self._cycle_for(fy_year)
        idx = max(1, min(3, fy_year - FIRST_FISCAL_YEAR + 1))
        env_total = sum(sum(p[idx - 1] + n[idx - 1] for p, n in [v]) for v in ENVELOPES_GBP.values())
        out = [self.emit("finance.budget_cycle_opened", {
            "budget_cycle_id": cycle["id"], "fiscal_year": fy_year, "deadline_day": cycle["deadline_day"],
            "guidance": {"loaded_cost_factor": LOADED_COST_FACTOR, "usd_per_gbp": USD_PER_GBP,
                         "payment_terms_days": PAYMENT_TERMS_DAYS, "planning_envelope_gbp_k": env_total,
                         "submission_format": "people_gbp, non_people_gbp, total_gbp, headcount, agents"}})]
        fin_people, fin_non = ENVELOPES_GBP["finance"][0][idx - 1], ENVELOPES_GBP["finance"][1][idx - 1]
        out.append(self.emit("finance.budget_submitted", {
            "budget_cycle_id": cycle["id"], "people_gbp": fin_people * 1000, "non_people_gbp": fin_non * 1000,
            "total_gbp": (fin_people + fin_non) * 1000, "headcount": HEADCOUNT_PLAN["finance"][idx - 1]},
            recipient="executive", delay_days=10))
        cycle["finance_submitted"] = True
        self._task(f"Chase departmental budget submissions for {cycle['id']} (deadline day {cycle['deadline_day']})",
                   cycle["deadline_day"], "high")
        return out

    def _on_budget_submitted(self, msg: Message, body: dict) -> list[Message]:
        fy_year = int(_num(body.get("fiscal_year"), self.clock.date.year + (1 if self.clock.date.month >= 10 else 0)))
        cycle = self.state["budget_cycles"].get(_s(body.get("budget_cycle_id"))) or self._cycle_for(fy_year)
        total = _num(body.get("total_gbp"), _num(body.get("people_gbp")) + _num(body.get("non_people_gbp")))
        cycle["submissions"][msg.sender] = {"total": total, "people": _num(body.get("people_gbp")),
                                            "non_people": _num(body.get("non_people_gbp")),
                                            "headcount": body.get("headcount"), "day": self.clock.day}
        return self._maybe_consolidate(cycle, force=False)

    def _maybe_consolidate(self, cycle: dict, force: bool) -> list[Message]:
        if cycle["consolidated"]:
            return []
        missing = [d for d in BUDGET_DEPARTMENTS if d != "finance" and d not in cycle["submissions"]]
        if missing and not force:
            return []
        idx = max(1, min(3, cycle["fy"] - FIRST_FISCAL_YEAR + 1))
        total = sum(s["total"] for s in cycle["submissions"].values())
        fin = (ENVELOPES_GBP["finance"][0][idx - 1] + ENVELOPES_GBP["finance"][1][idx - 1]) * 1000
        total += fin
        envelope = sum((p[idx - 1] + n[idx - 1]) * 1000 for p, n in ENVELOPES_GBP.values())
        over = {}
        for dept, sub in cycle["submissions"].items():
            env = (ENVELOPES_GBP[dept][0][idx - 1] + ENVELOPES_GBP[dept][1][idx - 1]) * 1000 if dept in ENVELOPES_GBP else 0
            if env and sub["total"] > env * 1.05:
                over[dept] = round(sub["total"] - env, 2)
        cycle["consolidated"] = True
        if missing:
            self._task(f"Budget {cycle['id']} consolidated with missing submissions: {', '.join(missing)}", None, "high")
        revenue = REVENUE_PLAN_GBP[idx]
        return [self.emit("finance.budget_consolidated", {
            "budget_cycle_id": cycle["id"], "fiscal_year": cycle["fy"], "total_cost_gbp": round(total, 2),
            "planning_envelope_gbp": envelope, "variance_to_envelope_gbp": round(total - envelope, 2),
            "departments_over_envelope": over, "missing_submissions": missing, "revenue_plan_gbp": revenue,
            "ebitda_plan_gbp": EBITDA_GBP[idx], "recommendation": "approve" if not over and not missing else
            "approve_with_conditions"}, delay_days=2)]

    def _on_budget_approved(self, msg: Message, body: dict) -> list[Message]:
        cycle_id = _s(body.get("budget_cycle_id"), f"BUD-{self.clock.date.year}")
        self.state["approved_budget"] = {"cycle": cycle_id, "day": self.clock.day, "detail": body}
        if cycle_id in self.state["budget_cycles"]:
            self.state["budget_cycles"][cycle_id]["approved"] = True
        self._task(f"Load approved budget {cycle_id} into ledger and variance reporting; issue delegations "
                   "and spend limits to heads", self.clock.day + 5, "high")
        return []

    # ------------------------------------------------------------------ spend control and people cost
    def _commit(self, dept: str, amount: float, what: str, msg: Message) -> list[Message]:
        dept = dept if dept in ENVELOPES_GBP else "operations"
        fy = self._fy()
        committed = self.state["commitments"].setdefault(dept, 0.0) + amount
        self.state["commitments"][dept] = committed
        envelope = ENVELOPES_GBP[dept][1][fy - 1] * 1000
        out: list[Message] = []
        if amount > UNBUDGETED_CEO_GBP:
            self._task(f"CEO approval needed for {what} £{amount:,.0f} (> £250k)", self.clock.day + 2, "critical")
        elif amount > UNBUDGETED_CFO_GBP:
            self._task(f"CFO approval needed for {what} £{amount:,.0f} (> £50k)", self.clock.day + 2, "high")
        if amount > AGENT_PAYMENT_LIMIT_GBP:
            self._task(f"Human approval for payment of {what} (£{amount:,.0f} exceeds £10k agent limit)", self.clock.day + 3, "high")
        pct = committed / envelope * 100 if envelope else 0
        level = "over_budget" if pct > 100 else ("at_risk" if pct >= 90 else None)
        if level and self.state["flagged"].get(dept) != level:
            self.state["flagged"][dept] = level
            out.append(self.emit("finance.budget_variance_flagged", {
                "department": dept, "category": "non_people", "committed_ytd_gbp": round(committed, 2),
                "annual_envelope_gbp": envelope, "utilisation_pct": round(pct, 1), "severity": level,
                "trigger": what, "action": "CFO review; freeze discretionary spend" if level == "over_budget"
                else "monitor; heads to confirm forecast"}, reply_to=msg.id))
        return out

    def _on_campaign_launched(self, msg: Message, body: dict) -> list[Message]:
        spend = _num(_first(body, "budget_gbp", "spend_gbp", "cost_gbp", "amount_gbp"))
        return self._commit("marketing", spend, f"campaign {_s(body.get('campaign_id'), msg.id)}", msg) if spend else []

    def _on_procurement_order(self, msg: Message, body: dict) -> list[Message]:
        amount = _num(_first(body, "amount_gbp", "value_gbp", "total_gbp"))
        dept = _s(_first(body, "department", "requesting_department", "dept", default="operations"))
        vendor = _s(_first(body, "vendor_id", "vendor"), "unknown vendor")
        v = self.state["vendors"].get(vendor)
        if vendor != "unknown vendor" and (v is None or v.get("status") != "approved"):
            self._task(f"PO for {vendor} raised before vendor approval; hold payment until onboarded", None, "high")
        return self._commit(dept, amount, f"PO {_s(body.get('order_id'), msg.id)} to {vendor}", msg) if amount else []

    def _on_vendor_review_requested(self, msg: Message, body: dict) -> list[Message]:
        vendor = _s(_first(body, "vendor_id", "vendor"), msg.id)
        self.state["vendors"][vendor] = {"status": "in_review", "day": self.clock.day}
        self._task(f"Financial due diligence on {vendor}: Companies House accounts, credit score, concentration, "
                   "bank detail verification", self.clock.day + 5)
        return []

    def _on_vendor_approved(self, msg: Message, body: dict) -> list[Message]:
        vendor = _s(_first(body, "vendor_id", "vendor"), msg.id)
        self.state["vendors"][vendor] = {"status": "approved", "day": self.clock.day}
        self._task(f"Create supplier record for {vendor}; bank details verified by call-back before first payment run",
                   self.clock.day + 2, "medium")
        return []

    def _on_vendor_risk(self, msg: Message, body: dict) -> list[Message]:
        vendor = _s(_first(body, "vendor_id", "vendor"), msg.id)
        risk = _s(_first(body, "risk_rating", "risk", "rating"), "unrated").lower()
        v = self.state["vendors"].setdefault(vendor, {"status": "in_review", "day": self.clock.day})
        v["risk"] = risk
        if risk in ("high", "critical"):
            v["status"] = "payment_hold"
            self._task(f"Payment hold on {vendor} (security risk {risk}) pending Operations decision", None, "high")
        return []

    def _on_requisition_opened(self, msg: Message, body: dict) -> list[Message]:
        """Finance budget check on a People requisition. This must NOT emit finance.hire_requested: People would
        treat it as a new hire request and open another requisition, which Finance would check again (a loop that
        produced ~1,000 requisitions in two simulated years). An over-plan requisition is flagged as a budget
        variance instead; the approval decision itself belongs to Executive."""
        dept = _s(_first(body, "department", "dept"), "unknown")
        req = _s(body.get("requisition_id"), msg.id)
        self._task(f"Confirm requisition {req} ({dept}) is within approved headcount budget", self.clock.day + 3)
        salary = _num(_first(body, "salary_gbp", "base_salary_gbp", "salary"))
        plan = HEADCOUNT_PLAN.get(dept)
        planned = plan[self._fy() - 1] if plan else None
        in_flight = self.state["open_requisitions"].setdefault(dept, [])
        if req not in in_flight:
            in_flight.append(req)
        committed = self.state["headcount"].get(dept, 0) + len(in_flight)
        if planned is None or committed <= planned:
            return []
        key = f"req:{dept}:{self._fy()}"
        if self.state["flagged"].get(key):
            return []
        self.state["flagged"][key] = "over"
        return [self.emit("finance.budget_variance_flagged", {
            "department": dept, "category": "people", "requisition_id": req,
            "role": _s(body.get("role"), "unspecified"), "year_end_plan": planned,
            "committed_headcount": committed,
            "annual_loaded_cost_gbp": round(salary * LOADED_COST_FACTOR, 2), "severity": "over_budget",
            "trigger": "requisition would take committed headcount beyond the approved year-end plan"},
            reply_to=msg.id)]

    def _release_requisition(self, dept: str, req: str) -> None:
        in_flight = self.state["open_requisitions"].get(dept, [])
        if req and req in in_flight:
            in_flight.remove(req)
        elif in_flight and not req:
            in_flight.pop(0)

    def _on_headcount_approved(self, msg: Message, body: dict) -> list[Message]:
        dept = _s(_first(body, "department", "dept"), "unknown")
        if body.get("approved") is False or _s(body.get("decision")).lower() in ("declined", "rejected", "denied"):
            self._release_requisition(dept, _s(body.get("requisition_id")))
        self._task(f"Add approved headcount for {dept} to payroll forecast and variance baseline",
                   self.clock.day + 5, "medium")
        return []

    def _on_offer_accepted(self, msg: Message, body: dict) -> list[Message]:
        dept = _s(_first(body, "department", "dept"), "unknown")
        salary = _num(_first(body, "salary_gbp", "base_salary_gbp", "salary"))
        loaded = round(salary * LOADED_COST_FACTOR, 2)
        out: list[Message] = []
        hc = self.state["headcount"]
        hc[dept] = hc.get(dept, 0) + 1
        self._release_requisition(dept, _s(body.get("requisition_id")))
        plan = HEADCOUNT_PLAN.get(dept)
        if plan and hc[dept] > plan[self._fy() - 1] and self.state["flagged"].get(f"hc:{dept}") != "over":
            self.state["flagged"][f"hc:{dept}"] = "over"
            out.append(self.emit("finance.budget_variance_flagged", {
                "department": dept, "category": "people", "accepted_hires_ytd": hc[dept],
                "year_end_plan": plan[self._fy() - 1], "annual_loaded_cost_gbp": loaded, "severity": "over_budget",
                "trigger": "offer accepted beyond approved year-end headcount"}, reply_to=msg.id))
        self._task(f"Payroll setup, P45/starter checklist and £{loaded:,.0f} loaded cost accrual for {dept} hire",
                   self.clock.day + 5)
        return out

    def _on_new_hire_started(self, msg: Message, body: dict) -> list[Message]:
        self._task(f"Add {_s(body.get('employee_id'), 'new starter')} to next payroll run (PAYE/NI/pension auto-enrolment)",
                   self.clock.day + 7)
        return []

    def _on_employee_left(self, msg: Message, body: dict) -> list[Message]:
        dept = _s(_first(body, "department", "dept"), "unknown")
        self.state["headcount"][dept] = max(0, self.state["headcount"].get(dept, 0) - 1)
        self._task(f"Final pay, accrued holiday and expense clearance for leaver {_s(body.get('employee_id'), msg.id)}",
                   self.clock.day + 5)
        return []

    def _on_contractor_engaged(self, msg: Message, body: dict) -> list[Message]:
        rate = _num(_first(body, "day_rate_gbp", "rate_gbp"))
        days = _num(_first(body, "days", "planned_days"), 20)
        cost = rate * days
        self.state["contractors"][_s(_first(body, "contractor_id", "name"), msg.id)] = cost
        self._task(f"Contractor accrual £{cost:,.0f}; confirm IR35 status determination before first invoice",
                   self.clock.day + 3)
        dept = _s(_first(body, "department", "dept"), "delivery")
        return self._commit(dept, cost, "contractor engagement", msg) if cost else []

    # ------------------------------------------------------------------ executive, data, delivery signals
    def _on_crisis(self, msg: Message, body: dict) -> list[Message]:
        self.state["crisis_mode"] = True
        self._task("Crisis mode: freeze discretionary spend, daily cash position, review credit lines", self.clock.day, "critical")
        return [self._cash_forecast("crisis_declared", msg, scenario="downside", delay=0)]

    def _on_board_meeting(self, msg: Message, body: dict) -> list[Message]:
        self.state["board_packs"] += 1
        self._task("Board pack: management accounts, cash forecast, covenant and delegations log", self.clock.day + 1, "high")
        return [self._cash_forecast("board_meeting", msg, delay=1)]

    def _on_okrs(self, msg: Message, body: dict) -> list[Message]:
        self.state["okrs"] = body
        return []

    def _on_strategy(self, msg: Message, body: dict) -> list[Message]:
        self._task("Reflect strategy update in 3-year financial model and next forecast", self.clock.day + 10, "medium")
        return []

    def _on_capacity_forecast(self, msg: Message, body: dict) -> list[Message]:
        util = _num(_first(body, "utilisation_pct", "utilization_pct", "forecast_utilisation_pct"))
        self.state["capacity"] = {"utilisation_pct": util, "day": self.clock.day}
        if util and util < 65.0:
            self._task(f"Forecast utilisation {util:.0f}% is below 65%: bench cost review with Delivery", None, "medium")
        return [self._cash_forecast("capacity_forecast_updated", msg, delay=1)]

    def _on_data_forecast(self, msg: Message, body: dict) -> list[Message]:
        predicted = _num(_first(body, "revenue_gbp", "forecast_revenue_gbp", "revenue_forecast_gbp"))
        actual = self.state["billed_net_ytd"]
        if predicted > 0 and actual > 0:
            self.state["forecast_errors"].append(abs(predicted - actual) / actual)
        return []

    def _on_data_kpi_report(self, msg: Message, body: dict) -> list[Message]:
        return []

    # ------------------------------------------------------------------ cash forecast
    def _cash_position(self) -> float:
        total, day, d = OPENING_CASH_GBP, self.clock.day, self.clock.start
        for i in range(day):  # day-by-day plan burn (modelled; includes Series A receipt)
            cur = self.clock.date_of(i)
            fy = max(1, min(3, cur.year - FIRST_FISCAL_YEAR + 1))
            total += EBITDA_GBP[fy] / 365
        if self.clock.date >= SERIES_A_DATE:
            total += SERIES_A_GBP
        return round(total, 2)

    def _cash_forecast(self, reason: str, msg: Optional[Message] = None, scenario: str = "base", delay: int = 0) -> Message:
        now = self.clock.day
        open_inv = [i for i in self.state["invoices"].values() if i["status"] != "paid"]
        avg_pay = (sum(self.state["days_to_pay"]) / len(self.state["days_to_pay"])) if self.state["days_to_pay"] else 38.0

        def expected(within: int) -> float:
            return round(sum(i["gross"] - i["paid"] for i in open_inv if not i["hold"] and
                             max(i["issue_day"] + avg_pay, now) <= now + within), 2)
        fy = self._fy()
        burn = EBITDA_GBP[fy] / 12
        cash = self._cash_position()
        runway = round(cash / -burn, 1) if burn < 0 else 99.0
        if scenario == "downside":
            runway = round(runway * 0.7, 1) if runway < 99 else 36.0
        self.state["cash_gbp"], self.state["runway_months"] = cash, runway
        self.state["last_cash_day"] = now
        return self.emit("finance.cash_forecast_updated", {
            "as_of_day": now, "horizon_weeks": 13, "scenario": scenario, "reason": reason, "cash_gbp": cash,
            "ar_gross_gbp": round(sum(i["gross"] - i["paid"] for i in open_inv), 2),
            "ar_overdue_gbp": round(sum(i["gross"] - i["paid"] for i in open_inv if now > i["due_day"] and not i["hold"]), 2),
            "expected_collections_30d_gbp": expected(30), "expected_collections_60d_gbp": expected(60),
            "expected_collections_90d_gbp": expected(90), "plan_net_burn_monthly_gbp": round(burn, 2),
            "runway_months": runway, "assumed_days_to_pay": round(avg_pay, 1), "crisis_mode": self.state["crisis_mode"],
        }, reply_to=msg.id if msg else None, delay_days=delay)

    # ------------------------------------------------------------------ month end close
    def _dso(self) -> Optional[float]:
        open_gross = sum(i["gross"] - i["paid"] for i in self.state["invoices"].values() if i["status"] != "paid")
        issued = [i for i in self.state["invoices"].values() if self.clock.day - 90 <= i["issue_day"] <= self.clock.day]
        billed = sum(i["gross"] for i in issued)
        if billed > 0:
            return round(open_gross / billed * 90, 1)
        d = self.state["days_to_pay"]
        return round(sum(d) / len(d), 1) if d else None

    def _close_period(self, period: str, msg_reply: Optional[str] = None) -> list[Message]:
        p = self._period(period)
        now = self.clock.day
        open_inv = [i for i in self.state["invoices"].values() if i["status"] != "paid"]
        ar = sum(i["gross"] - i["paid"] for i in open_inv)
        overdue = sum(i["gross"] - i["paid"] for i in open_inv if now > i["due_day"])
        wip = sum(m["amount"] for s in self.state["schedules"].values() if s["kind"] == "fixed" and s["active"]
                  for m in s["milestones"] if m["status"] == "open")
        exceptions = self.state["unapplied_cash_gbp"] > 0 or self.state["billing_exceptions"] > 0
        days_to_close = 8 if exceptions else 7  # FY2026 target 8 (kpis.md)
        self.state["closes"] += 1
        self._set_kpi("month_end_close_days", days_to_close)
        out = [self.emit("finance.month_end_closed", {
            "period": period, "working_days_to_close": days_to_close, "revenue_recognised_gbp": round(p["billed_net"], 2),
            "billings_net_gbp": round(p["billed_net"], 2), "cash_collected_gbp": round(p["collected"], 2),
            "ar_gross_gbp": round(ar, 2), "ar_overdue_gbp": round(overdue, 2), "dso_days": self._dso(),
            "unbilled_milestones_gbp": round(wip, 2), "bad_debt_provision_gbp": round(self.state["bad_debt_gbp"], 2),
            "unapplied_cash_gbp": round(self.state["unapplied_cash_gbp"], 2),
            "checklist": {"bank_reconciliation": not self.state["unapplied_cash_gbp"], "ar_ledger_to_gl": True,
                          "payroll_accruals": True, "vat_return_prepared": period[-2:] in ("03", "06", "09", "12"),
                          "intercompany": True},
            "commentary": self._narrative(f"Write a two-line CFO commentary on the {period} close: billings "
                                          f"£{p['billed_net']:,.0f}, collections £{p['collected']:,.0f}",
                                          f"{period} closed in {days_to_close} working days."),
        }, reply_to=msg_reply)]
        if period[-2:] in ("03", "06", "09", "12"):
            self._task(f"Prepare and file VAT return for quarter ending {period}", self.clock.day + 20, "high")
        return out

    # ------------------------------------------------------------------ tick (cadences)
    def tick(self) -> list[Message]:
        out: list[Message] = []
        today = self.clock.date
        self._refresh_kpis()
        # Series A receipt (COMPANY.md §1, Q2 FY2026)
        if not self.state["series_a_booked"] and today >= SERIES_A_DATE:
            self.state["series_a_booked"] = True
            self.log_event("finance.activity.series_a_received", "£10m Series A received (modelled date)",
                           amount_gbp=SERIES_A_GBP)
        # month boundary: queue the close for working day 5, run VAT/AP cadences, retainer billing
        month_key = today.strftime("%Y-%m")
        if self.state["cur_month"] != month_key:
            previous = self.state["cur_month"]
            self.state["cur_month"] = month_key
            if previous:
                self.state["close_queue"].append({"period": previous, "due_day": self.clock.day + self._bday_offset(5)})
            out += self._bill_retainers()
            out += self._capacity_check()
        for item in list(self.state["close_queue"]):
            if self.clock.day >= item["due_day"]:
                self.state["close_queue"].remove(item)
                out += self._close_period(item["period"])
                out.append(self._cash_forecast("month_end_close"))
        # annual budget cycle opens 1 October for the following fiscal year (CONVENTIONS.md 7.2)
        next_fy = today.year + 1
        if today.month >= 10 and f"BUD-{next_fy}" not in self.state["budget_cycles"] and today.month < 13:
            out += self._open_budget_cycle(next_fy)
        for cycle in list(self.state["budget_cycles"].values()):
            if not cycle["consolidated"] and cycle.get("finance_submitted") and self.clock.day >= cycle["deadline_day"] + 2:
                out += self._maybe_consolidate(cycle, force=True)
        # fortnightly rolling 13-week forecast
        if self.clock.every(14) and self.state["last_cash_day"] != self.clock.day and self.clock.day > 0:
            out.append(self._cash_forecast("fortnightly_refresh"))
        out += self._collections()
        return out

    def _bill_retainers(self) -> list[Message]:
        out: list[Message] = []
        for key in sorted(self.state["schedules"]):
            s = self.state["schedules"][key]
            if s["kind"] != "retainer" or not s["active"] or s["next_bill_day"] is None:
                continue
            if self.clock.day >= s["next_bill_day"]:
                monthly = round(s["total_net"] / 12, 2)
                s["months_billed"] += 1
                nxt = (self.clock.date.replace(day=1) + timedelta(days=32)).replace(day=1)
                s["next_bill_day"] = self.clock.day_of(nxt)
                label = f"retainer month {s['months_billed']} in advance"
                out += self._issue_invoice(s, label, monthly, "monthly_in_advance", None, 0)
        return out

    def _capacity_check(self) -> list[Message]:
        """Finance volume check: request a Billing and Collections Specialist once open ledger volume outgrows 2 humans."""
        open_count = sum(1 for i in self.state["invoices"].values() if i["status"] != "paid")
        if open_count >= 20 and not self.state["hire_requested"]:
            self.state["hire_requested"] = True
            return [self.emit("finance.hire_requested", {
                "department": "finance", "role": "Billing and Collections Specialist", "level": "consultant",
                "salary_band_gbp": [55_000, 70_000], "justification": f"{open_count} open invoices; collections "
                "and cash application exceed capacity of two humans plus agents", "requested_by": "finance",
                "within_budget": True}, recipient="people")]
        return []

    # ------------------------------------------------------------------ KPI roll-up
    def _refresh_kpis(self) -> None:
        s = self.state
        dso = self._dso()
        if dso is not None:
            self._set_kpi("dso_days", dso)
        if s["billed_net_ytd"] > 0:
            self._set_kpi("bad_debt_pct_revenue", s["bad_debt_gbp"] / s["billed_net_ytd"] * 100)
        if s["invoices_raised"]:
            self._set_kpi("invoice_timeliness_pct", s["on_time_invoices"] / s["invoices_raised"] * 100)
            open_inv = [i for i in s["invoices"].values() if i["status"] != "paid"]
            open_gross = sum(i["gross"] - i["paid"] for i in open_inv)
            over60 = sum(i["gross"] - i["paid"] for i in open_inv if self.clock.day - i["issue_day"] > 60)
            if open_gross > 0:
                self._set_kpi("overdue_ar_over_60_pct", over60 / open_gross * 100)
            due = sum(i["gross"] for i in s["invoices"].values() if i["due_day"] <= self.clock.day)
            if due > 0:
                paid_due = sum(i["paid"] for i in s["invoices"].values() if i["due_day"] <= self.clock.day)
                self._set_kpi("collections_ladder_adherence_pct", min(100.0, paid_due / due * 100))
        if s["pricing_checks"]:
            self._set_kpi("pricing_check_sla_pct", s["pricing_on_time"] / s["pricing_checks"] * 100)
            self._set_kpi("gross_margin_pct", s["margin_sum"] / s["pricing_checks"])  # quoted margin
        if s["forecast_errors"]:
            self._set_kpi("forecast_accuracy_pct", max(0.0, 100 - sum(s["forecast_errors"]) / len(s["forecast_errors"]) * 100))
        if s.get("runway_months") is not None:
            self._set_kpi("cash_runway_months", s["runway_months"])
        if s["commitments"]:
            worst = max(s["commitments"][d] / (ENVELOPES_GBP[d][1][self._fy() - 1] * 1000)
                        for d in s["commitments"] if d in ENVELOPES_GBP)
            self._set_kpi("budget_variance_pct", max(0.0, (worst - 1) * 100))

    def kpi_snapshot(self) -> list[Kpi]:
        """Current KPI values (targets from KPIS, actuals from the ledger)."""
        self._refresh_kpis()
        return [self.kpis[k.name] for k in KPIS]


def build_agent(llm, bus, clock, log) -> FinanceAgent:
    role = Role("Chief Financial Officer", "finance", "head", (1, 1, 1), (140000, 200000),  # COMPANY.md §6.2
                "Chief Executive Officer")
    return FinanceAgent("finance", "finance", role, llm, bus, clock, log)
