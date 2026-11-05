"""Executive department agent (CEO office): deal, headcount, budget, pricing and crisis decisions.

Decision rules follow COMPANY.md section 9.3 (delegations of authority) and the SOPs in ``sops.md``.
Everything is deterministic and works with ``core.MockLLM``; the LLM is only used to draft holding text.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Optional

from core import (DEPARTMENTS, DepartmentAgent, Kpi, Message, Role, publishes_for,
                  subscribes_for)

# --- KPIs (FY2026 targets, see kpis.md) -------------------------------------------------------------
KPIS: list[Kpi] = [
    Kpi("revenue_gbp_m", "£m", 6.0, None, True),                   # COMPANY.md §5.1
    Kpi("ebitda_margin_pct", "percent", -25.0, None, True),        # COMPANY.md §5.1
    Kpi("active_clients", "count", 24.0, None, True),              # COMPANY.md §5.1
    Kpi("gross_margin_pct", "percent", 48.0, None, True),          # COMPANY.md §5.1
    Kpi("top_client_share_pct", "percent", 15.0, None, False),     # COMPANY.md §8 assumption 8
    Kpi("okr_attainment_pct", "percent", 75.0, None, True),
    Kpi("deal_decision_hours", "hours", 48.0, None, False),
    Kpi("headcount_decision_days", "days", 5.0, None, False),
    Kpi("board_pack_on_time_pct", "percent", 100.0, None, True),
    Kpi("crisis_declaration_hours", "hours", 4.0, None, False),
    Kpi("cash_runway_months", "months", 24.0, None, True),
]

# --- Company facts as constants ---------------------------------------------------------------------
REVENUE_PLAN_GBP = {2026: 6_000_000, 2027: 19_500_000, 2028: 46_200_000}            # COMPANY.md §5.1
ENVELOPE_PEOPLE_K = {2026: 500, 2027: 800, 2028: 900}                                # COMPANY.md §5.4
ENVELOPE_NONPEOPLE_K = {2026: 100, 2027: 250, 2028: 400}                             # COMPANY.md §5.4
ENVELOPE_TOTAL_K = {2026: 7_500, 2027: 17_800, 2028: 39_000}                         # COMPANY.md §5.4 totals
DEPT_ENVELOPE_K = {                                                                  # COMPANY.md §5.4
    "executive": (600, 1_050, 1_300), "sales": (850, 2_100, 4_600), "marketing": (830, 1_850, 4_500),
    "delivery": (2_980, 7_400, 15_000), "finance": (310, 730, 1_500), "people": (310, 700, 1_850),
    "legal": (310, 580, 1_300), "it_security": (460, 920, 2_300), "operations": (300, 700, 1_650),
    "customer_success": (140, 790, 1_630), "product": (270, 620, 1_960), "data": (140, 360, 1_410),
}
# Own submission: build-up from economics.md section 2 and 1 (GBP).
OWN_BUDGET_GBP = {
    2026: {"people_gbp": 500_300, "non_people_gbp": 100_000, "headcount": 3, "agents": 1},
    2027: {"people_gbp": 796_200, "non_people_gbp": 250_000, "headcount": 4, "agents": 2},
    2028: {"people_gbp": 897_300, "non_people_gbp": 400_000, "headcount": 5, "agents": 3},
}
HEADCOUNT_PLAN = {                                                                   # COMPANY.md §6.1 (humans)
    "executive": (3, 4, 5), "sales": (5, 14, 26), "marketing": (3, 8, 14), "delivery": (14, 46, 104),
    "finance": (2, 5, 10), "people": (2, 5, 10), "legal": (1, 3, 5), "it_security": (2, 5, 9),
    "operations": (2, 6, 12), "customer_success": (1, 6, 14), "product": (2, 5, 12), "data": (1, 3, 9),
}
LIST_PRICE_GBP = {                                                                   # COMPANY.md §3 (annual for Keep)
    "compass_spark": 45_000, "compass_sprint": 120_000, "compass_programme": 350_000,
    "forge_pilot": 90_000, "forge_build": 260_000, "forge_scale": 650_000,
    "keep_essential": 96_000, "keep_plus": 216_000, "keep_enterprise": 480_000,
}
EXEC_PLANNED_HIRES = {                                                               # blueprint.md section 5
    2027: [{"role_title": "Board and Investor Relations Manager", "level": "manager",
            "salary_band_gbp": (92_000, 115_000), "target_start_day": 364}],
    2028: [{"role_title": "Senior Strategy Consultant", "level": "senior_consultant",
            "salary_band_gbp": (72_000, 90_000), "target_start_day": 819}],
}

DEAL_CEO_THRESHOLD_GBP = 500_000        # COMPANY.md §9.3
DEAL_BOARD_THRESHOLD_GBP = 1_500_000    # COMPANY.md §9.3
CONCENTRATION_CAP_PCT = 15.0            # COMPANY.md §8 assumption 8
CONCENTRATION_WATCH_PCT = 10.0
DISCOUNT_SALES_HEAD_MAX_PCT = 10.0      # COMPANY.md §9.3
DISCOUNT_CEO_CEILING_PCT = 15.0         # economics.md A7
MIN_DEAL_GROSS_MARGIN_PCT = 35.0        # economics.md A8
PRICE_CHANGE_CEILING_PCT = 15.0
HIRING_HOLD_VARIANCE_PCT = 15.0         # economics.md A9
RUNWAY_FREEZE_MONTHS = 12.0
RUNWAY_CRISIS_MONTHS = 6.0
REVENUE_BEHIND_PCT = 10.0
KEY_CLIENT_CRISIS_PCT = 10.0
SPONSOR_CALL_ANNUAL_VALUE_GBP = 250_000
COLLECTIONS_SPONSOR_GBP = 100_000
ENGAGEMENT_FLOOR = 60.0
AGENT_QUALITY_FLOOR = 85.0
BOARD_RATIFICATION_DAYS = 5             # written consent route
BOARD_NOTICE_DAYS = 7
BOARD_MEMBERS = ["Priya Raman", "Imogen Hartley", "Tomas Beckett", "Adaeze Okafor", "Marcus Ellery"]  # §9.1


def _num(body: dict, key: str, default: float = 0.0) -> float:
    """Read a number from a message body without ever raising."""
    value = body.get(key, default)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return float(default)


def _has(body: dict, key: str) -> bool:
    return body.get(key) is not None


def _text(body: dict, key: str, default: str = "") -> str:
    value = body.get(key)
    return default if value is None or value == "" else str(value)


def _flag(body: dict, key: str) -> bool:
    value = body.get(key)
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "y")
    return bool(value)


class ExecutiveAgent(DepartmentAgent):
    """The CEO office: applies delegations of authority and publishes company-level decisions."""

    SUBSCRIBES = subscribes_for("executive")
    PUBLISHES = publishes_for("executive")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.state.update({
            "kpis": {k.name: k for k in KPIS},
            "decision_log": [],
            "deal_decisions": {},
            "headcount_decisions": {},
            "client_revenue_gbp": {},
            "approved_headcount": {},
            "hiring_holds": [],
            "crisis_active": {},
            "crisis_history": [],
            "pending_board": [],
            "okrs_years": [],
            "board_quarters": [],
            "exec_hires_requested": [],
            "certifications": {},
            "deal_hours": [],
            "counters": {"crisis": 0, "meeting": 0, "strategy": 0, "req": 0},
            "months_behind": 0,
            "runway_months": None,
            "liquidity_crisis": False,
        })

    # ------------------------------------------------------------------ helpers
    @property
    def fiscal_year(self) -> int:
        """Current fiscal year clamped to the modelled range FY2026 to FY2028."""
        return min(max(self.clock.date.year, 2026), 2028)

    @property
    def kpis(self) -> list[Kpi]:
        return list(self.state["kpis"].values())

    def kpi_snapshot(self) -> dict[str, Optional[float]]:
        """KPI name -> latest actual (None when unreported)."""
        return {k.name: k.actual for k in self.kpis}

    def _set_kpi(self, name: str, actual: float) -> None:
        kpi = self.state["kpis"].get(name)
        if kpi is not None:
            self.state["kpis"][name] = replace(kpi, actual=round(actual, 2))

    def _next(self, counter: str) -> int:
        self.state["counters"][counter] += 1
        return self.state["counters"][counter]

    def _record(self, kind: str, subject: str, outcome: str, **data: Any) -> None:
        """Append to the decision log and the event log."""
        entry = {"day": self.clock.day, "kind": kind, "subject": subject, "outcome": outcome}
        entry.update(data)
        self.state["decision_log"].append(entry)
        self.log_event(f"executive.activity.{kind}", f"{subject}: {outcome}", **data)

    def _median_set(self, bucket: str, value: float, kpi: str) -> None:
        values = self.state[bucket]
        values.append(value)
        ordered = sorted(values)
        mid = len(ordered) // 2
        median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
        self._set_kpi(kpi, median)

    def _client_share_pct(self, annual_gbp: float) -> float:
        return round(annual_gbp / REVENUE_PLAN_GBP[self.fiscal_year] * 100, 1)

    def _update_top_client(self) -> None:
        ledger = self.state["client_revenue_gbp"]
        if ledger:
            self._set_kpi("top_client_share_pct", self._client_share_pct(max(ledger.values())))

    def _crisis_active(self) -> bool:
        return bool(self.state["crisis_active"])

    # ------------------------------------------------------------------ dispatch
    def handle(self, message: Message) -> list[Message]:
        handler = getattr(self, "_on_" + message.topic.replace(".", "_"), None)
        if handler is None:
            self.log_event("executive.activity.unhandled_topic", message.topic, message_id=message.id)
            return []
        self.log_event("executive.activity.received", message.topic, message_id=message.id,
                       sender=message.sender)
        return list(handler(message) or [])

    # ------------------------------------------------------------------ SOP-01 deals
    def _on_sales_deal_approval_requested(self, m: Message) -> list[Message]:
        b = m.body
        deal_id = _text(b, "deal_id", f"DL-{m.id}")
        amount = _num(b, "amount_gbp")
        prior = self.state["deal_decisions"].get(deal_id)
        if prior is not None and prior["amount_gbp"] == amount:
            self.log_event("executive.activity.duplicate_request", deal_id, deal_id=deal_id)
            return []
        client_id = _text(b, "client_id", "CL-UNKNOWN")
        duration = max(_num(b, "duration_months", 12.0), 1.0)
        annual = amount * 12 / duration
        existing = self.state["client_revenue_gbp"].get(client_id, 0.0)
        concentration = self._client_share_pct(existing + annual)
        discount = _num(b, "discount_pct")
        margin = _num(b, "gross_margin_pct", -1.0) if _has(b, "gross_margin_pct") else None
        reasons: list[str] = []
        conditions: list[str] = []

        if amount < DEAL_CEO_THRESHOLD_GBP:
            decision, approver = "not_required", "Chief Revenue Officer (within delegation)"
            reasons.append("below_ceo_threshold_500k")
        else:
            if discount > DISCOUNT_CEO_CEILING_PCT:
                reasons.append("discount_above_15pct_ceiling")
            if margin is not None and margin < MIN_DEAL_GROSS_MARGIN_PCT:
                reasons.append("gross_margin_below_35pct_floor")
            if concentration > CONCENTRATION_CAP_PCT:
                reasons.append("client_concentration_above_15pct_cap")
            if reasons:
                decision, approver = "declined", "Chief Executive Officer"
            else:
                if discount > DISCOUNT_SALES_HEAD_MAX_PCT:
                    conditions.append("finance_head_concurrence")
                if _flag(b, "uncapped_liability") or _flag(b, "non_standard_terms"):
                    conditions.append("general_counsel_signoff")
                if concentration > CONCENTRATION_WATCH_PCT:
                    conditions.append("board_chair_notified_concentration")
                if amount > DEAL_BOARD_THRESHOLD_GBP:
                    decision, approver = "referred_to_board", "Chief Executive Officer (recommends); Board approves"
                    reasons.append("above_1_5m_board_approval_required")
                elif conditions:
                    decision, approver = "approved_with_conditions", "Chief Executive Officer"
                else:
                    decision, approver = "approved", "Chief Executive Officer"
                    reasons.append("all_controls_passed")

        out = {
            "deal_id": deal_id, "client_id": client_id, "client_name": _text(b, "client_name"),
            "amount_gbp": int(amount), "decision": decision, "approver": approver,
            "conditions": conditions, "reasons": reasons, "concentration_pct": concentration,
            "decided_day": self.clock.day, "board_ratified": False,
            "summary": f"{deal_id} {decision.replace('_', ' ')} at £{int(amount):,}",
        }
        for key in ("tier", "service_line"):
            if _has(b, key):
                out[key] = b[key]
        self.state["deal_decisions"][deal_id] = dict(out)
        hours = max(self.clock.day - m.sim_time, 0) * 24.0
        self._median_set("deal_hours", hours, "deal_decision_hours")
        self._record("deal_decision", deal_id, decision, amount_gbp=int(amount), concentration_pct=concentration)
        msgs = [self.emit("executive.deal_decision_made", out, reply_to=m.id)]
        if decision == "referred_to_board":
            final = dict(out)
            final["decision"] = "approved_with_conditions" if conditions else "approved"
            self.state["pending_board"].append({"due_day": self.clock.day + BOARD_RATIFICATION_DAYS,
                                                "kind": "deal", "payload": final})
        return msgs

    def _on_sales_proposal_sent(self, m: Message) -> list[Message]:
        b = m.body
        amount = _num(b, "amount_gbp")
        deal_id = _text(b, "deal_id", _text(b, "proposal_id", "DL-UNKNOWN"))
        if amount >= DEAL_CEO_THRESHOLD_GBP and deal_id not in self.state["deal_decisions"]:
            self.create_task(f"Confirm CEO approval request for {deal_id} (£{int(amount):,})", 3, "high")
            self._record("proposal_watch", deal_id, "approval_not_yet_requested", amount_gbp=int(amount))
        else:
            self.log_event("executive.activity.pipeline_seen", deal_id, deal_id=deal_id, amount_gbp=int(amount))
        return []

    def _on_sales_deal_won(self, m: Message) -> list[Message]:
        b = m.body
        deal_id = _text(b, "deal_id", "DL-UNKNOWN")
        client_id = _text(b, "client_id", "CL-UNKNOWN")
        amount = _num(b, "amount_gbp")
        annual = amount * 12 / max(_num(b, "duration_months", 12.0), 1.0)
        ledger = self.state["client_revenue_gbp"]
        ledger[client_id] = ledger.get(client_id, 0.0) + annual
        self._update_top_client()
        if amount >= DEAL_CEO_THRESHOLD_GBP and deal_id not in self.state["deal_decisions"]:
            self.create_task(f"Won deal {deal_id} had no recorded CEO approval", 2, "critical")
            self._record("control_exception", deal_id, "won_without_ceo_approval", amount_gbp=int(amount))
        else:
            self._record("client_ledger_updated", client_id, "deal_won", deal_id=deal_id,
                         annual_gbp=int(annual), share_pct=self._client_share_pct(ledger[client_id]))
        return []

    def _on_sales_deal_lost(self, m: Message) -> list[Message]:
        b = m.body
        deal_id = _text(b, "deal_id", "DL-UNKNOWN")
        amount = _num(b, "amount_gbp")
        if amount >= DEAL_CEO_THRESHOLD_GBP:
            self.create_task(f"Loss review for {deal_id} (£{int(amount):,}) with the CRO", 14, "medium")
        self._record("deal_lost", deal_id, "logged", amount_gbp=int(amount), reason=_text(b, "reason"))
        return []

    # ------------------------------------------------------------------ SOP-09 contract exceptions
    def _on_legal_contract_risk_flagged(self, m: Message) -> list[Message]:
        b = m.body
        deal_id = _text(b, "deal_id", "DL-UNKNOWN")
        level = _text(b, "risk_level", _text(b, "severity", "medium")).lower()
        mitigated = bool(b.get("mitigation"))
        if level in ("low", "medium"):
            self._record("contract_exception", deal_id, "noted_no_ceo_decision", risk_level=level)
            return []
        decision = "approved_with_conditions" if mitigated else "declined"
        out = {
            "deal_id": deal_id, "contract_id": _text(b, "contract_id"), "client_id": _text(b, "client_id"),
            "amount_gbp": int(_num(b, "amount_gbp")), "decision": decision, "exception": True,
            "approver": "Chief Executive Officer with General Counsel",
            "conditions": ["general_counsel_signoff", "mitigation_in_contract"] if mitigated else [],
            "reasons": [f"{level}_contract_risk", "mitigated" if mitigated else "no_mitigation_offered"],
            "decided_day": self.clock.day, "board_ratified": False,
            "summary": f"Contract exception for {deal_id}: {decision.replace('_', ' ')}",
        }
        self._record("contract_exception", deal_id, decision, risk_level=level)
        return [self.emit("executive.deal_decision_made", out, reply_to=m.id)]

    # ------------------------------------------------------------------ SOP-03 headcount
    def _on_people_requisition_opened(self, m: Message) -> list[Message]:
        return self._decide_headcount(m)

    def _on_people_hire_requested(self, m: Message) -> list[Message]:
        return self._decide_headcount(m)

    def _decide_headcount(self, m: Message) -> list[Message]:
        b = m.body
        dept = _text(b, "department", m.sender)
        req_id = _text(b, "requisition_id") or f"REQ-{self._next('req'):04d}"
        if req_id in self.state["headcount_decisions"]:
            self.log_event("executive.activity.duplicate_request", req_id, requisition_id=req_id)
            return []
        role_title = _text(b, "role_title", _text(b, "title", _text(b, "role", "unspecified role")))
        level = _text(b, "level")
        fy = self.fiscal_year
        year_index = fy - 2025
        critical = _flag(b, "critical_role")
        runway = self.state["runway_months"]
        reason = ""
        basis = ""
        if self._crisis_active() and not critical:
            reason = "crisis_hiring_freeze"
        elif runway is not None and runway < RUNWAY_FREEZE_MONTHS and not critical:
            reason = "cash_runway_below_12_months"
        elif dept in self.state["hiring_holds"] and not critical:
            reason = "department_hiring_hold_after_variance"
        else:
            plan = HEADCOUNT_PLAN.get(dept)
            key = f"{dept}:{fy}"
            used = self.state["approved_headcount"].get(key, 0)
            allowed = 0
            if plan:
                allowed = plan[year_index - 1] - (plan[year_index - 2] if year_index > 1 else 0)
            if _flag(b, "replacement"):
                basis = "backfill"
            elif _has(b, "in_budget") and not _flag(b, "in_budget"):
                basis = ""
            elif _flag(b, "in_budget") or used < allowed:
                basis = "in_plan"
                self.state["approved_headcount"][key] = used + 1
            if not basis:
                if b.get("business_case"):
                    basis = "business_case"
                else:
                    reason = "outside_approved_headcount_plan_no_business_case"

        if reason:
            self.state["headcount_decisions"][req_id] = {"decision": "declined", "reason": reason}
            self._record("headcount_decision", req_id, "declined", department=dept, reason=reason)
            recipient = m.sender if m.sender in DEPARTMENTS else "people"
            return [self.emit("executive.internal.headcount_declined",
                              {"requisition_id": req_id, "department": dept, "role_title": role_title,
                               "reason": reason, "decided_day": self.clock.day},
                              recipient=recipient, reply_to=m.id)]

        board_route = dept == "executive" or level in ("head", "executive")
        approver = ("Board of Directors" if board_route else
                    "Chief Executive Officer" if basis == "business_case" else
                    "Chief of Staff under CEO delegation")
        out = {
            "requisition_id": req_id, "department": dept, "role_title": role_title, "approved": True,
            "basis": basis, "approver": approver, "fiscal_year": fy, "decided_day": self.clock.day,
            "conditions": ["report_to_next_board"] if basis == "business_case" else [],
        }
        self.state["headcount_decisions"][req_id] = {"decision": "approved", "basis": basis}
        self._median_set_days(m)
        if board_route:
            self._record("headcount_decision", req_id, "referred_to_board", department=dept)
            self.state["pending_board"].append({"due_day": self.clock.day + BOARD_NOTICE_DAYS,
                                                "kind": "headcount", "payload": out})
            return []
        self._record("headcount_decision", req_id, "approved", department=dept, basis=basis)
        return [self.emit("executive.headcount_approved", out, reply_to=m.id)]

    def _median_set_days(self, m: Message) -> None:
        days = max(self.clock.day - m.sim_time, 0)
        business_days = days * 5 / 7
        values = self.state.setdefault("headcount_days", [])
        values.append(business_days)
        ordered = sorted(values)
        mid = len(ordered) // 2
        median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
        self._set_kpi("headcount_decision_days", median)

    # ------------------------------------------------------------------ SOP-04 budget and OKRs
    def _requested_fy(self, body: dict) -> tuple[int, bool]:
        """(fiscal year clamped to the model, provisional flag when outside FY2026-FY2028)."""
        default = self.clock.date.year + (1 if self.clock.date.month >= 10 else 0)
        fy = int(_num(body, "fiscal_year", default))
        return min(max(fy, 2026), 2028), fy > 2028

    def _on_finance_budget_cycle_opened(self, m: Message) -> list[Message]:
        fy, provisional = self._requested_fy(m.body)
        own = OWN_BUDGET_GBP[fy]
        body = {
            "department": "executive", "fiscal_year": fy, "budget_id": _text(m.body, "budget_id", f"BUD-{fy}"),
            "people_gbp": own["people_gbp"], "non_people_gbp": own["non_people_gbp"],
            "total_gbp": own["people_gbp"] + own["non_people_gbp"], "headcount": own["headcount"],
            "agents": own["agents"], "provisional": provisional,
            "summary": f"Executive FY{fy} budget: people plus non-people per economics.md",
        }
        self._record("budget_submission", f"BUD-{fy}", "submitted", total_gbp=body["total_gbp"])
        return [self.emit("executive.budget_submitted", body, recipient="finance", reply_to=m.id)]

    def _on_finance_budget_submitted(self, m: Message) -> list[Message]:
        b = m.body
        fy, _ = self._requested_fy(b)
        total = _num(b, "total_gbp")
        envelope = DEPT_ENVELOPE_K.get(_text(b, "department", "finance"), DEPT_ENVELOPE_K["finance"])[fy - 2026]
        over = total > envelope * 1000 * 1.02
        if over:
            self.create_task(f"Challenge {m.sender} FY{fy} submission above envelope", 5, "high")
        self._record("budget_review", f"{m.sender} FY{fy}", "above_envelope" if over else "within_envelope",
                     total_gbp=int(total), envelope_gbp=envelope * 1000)
        return []

    def _on_finance_budget_consolidated(self, m: Message) -> list[Message]:
        b = m.body
        fy, provisional = self._requested_fy(b)
        envelope = ENVELOPE_TOTAL_K[fy] * 1000
        total = _num(b, "total_gbp", float(envelope))
        within = total <= envelope * 1.02
        approved_total = int(total if within else envelope)
        reductions = 0 if within else int(total - envelope)
        by_dept = b.get("by_department")
        if not isinstance(by_dept, dict):
            by_dept = {d: DEPT_ENVELOPE_K[d][fy - 2026] * 1000 for d in DEPARTMENTS}
        out = {
            "budget_id": _text(b, "budget_id", f"BUD-{fy}"), "fiscal_year": fy,
            "status": "approved" if within else "approved_with_reductions",
            "approved_total_gbp": approved_total, "by_department": dict(sorted(by_dept.items())),
            "reductions_gbp": reductions, "provisional": provisional,
            "conditions": [] if within else ["return_to_envelope_before_release"],
            "decided_day": self.clock.day,
            "summary": f"FY{fy} budget {'approved' if within else 'approved with reductions'} at £{approved_total:,}",
        }
        self._record("budget_decision", out["budget_id"], out["status"], approved_total_gbp=approved_total)
        self.state["hiring_holds"] = []
        msgs = [self.emit("executive.budget_approved", out, reply_to=m.id)]
        msgs.extend(self._publish_okrs(fy))
        msgs.extend(self._request_exec_hires(fy))
        return msgs

    def _okr_objectives(self, fy: int) -> list[dict]:
        i = fy - 2026
        revenue = (6.0, 19.5, 46.2)[i]
        clients = (24, 65, 140)[i]
        ebitda = (-25, 9, 16)[i]
        gm = (48, 58, 64)[i]
        return [
            {"id": "O1", "objective": "Grow profitably through land and expand", "key_results": [
                f"Revenue of £{revenue}m", f"{clients} active clients", f"Gross margin of {gm}%"]},
            {"id": "O2", "objective": "Reach the planned profitability", "key_results": [
                f"EBITDA margin of {ebitda}%", "Every department within its budget envelope"]},
            {"id": "O3", "objective": "Decide fast and govern well", "key_results": [
                "Deal decisions within SLA", "Board packs issued 5 working days ahead", "OKR attainment of 75%"]},
            {"id": "O4", "objective": "Stay resilient", "key_results": [
                "No client above 15% of revenue", "Cash runway of 24 months or more",
                "Crisis declared within SLA when triggered"]},
        ]

    def _publish_okrs(self, fy: int) -> list[Message]:
        if fy in self.state["okrs_years"]:
            return []
        self.state["okrs_years"].append(fy)
        body = {"fiscal_year": fy, "objectives": self._okr_objectives(fy), "owner": "Chief Executive Officer",
                "effective_day": self.clock.day_of(self.clock.date.replace(year=fy, month=1, day=1)),
                "summary": f"Company OKRs for FY{fy}"}
        self._record("okrs", f"FY{fy}", "set", fiscal_year=fy)
        return [self.emit("executive.okrs_set", body)]

    def _request_exec_hires(self, fy: int) -> list[Message]:
        out: list[Message] = []
        for spec in EXEC_PLANNED_HIRES.get(fy, []):
            key = f"{fy}:{spec['role_title']}"
            if key in self.state["exec_hires_requested"]:
                continue
            self.state["exec_hires_requested"].append(key)
            body = {"department": "executive", "role_title": spec["role_title"], "level": spec["level"],
                    "salary_band_gbp": list(spec["salary_band_gbp"]), "target_start_day": spec["target_start_day"],
                    "justification": f"Approved FY{fy} headcount plan (blueprint.md section 5)", "in_budget": True,
                    "fiscal_year": fy}
            out.append(self.emit("executive.hire_requested", body, recipient="people"))
        return out

    # ------------------------------------------------------------------ SOP-05 performance and cash
    def _on_finance_month_end_closed(self, m: Message) -> list[Message]:
        b = m.body
        month = int(_num(b, "month", self.clock.date.month)) or 1
        ytd = _num(b, "ytd_revenue_gbp", _num(b, "revenue_gbp"))
        plan = REVENUE_PLAN_GBP[self.fiscal_year]
        phased = plan * min(max(month, 1), 12) / 12
        self._set_kpi("revenue_gbp_m", ytd / 1_000_000)
        if _has(b, "gross_margin_pct"):
            self._set_kpi("gross_margin_pct", _num(b, "gross_margin_pct"))
        if _has(b, "ebitda_margin_pct"):
            self._set_kpi("ebitda_margin_pct", _num(b, "ebitda_margin_pct"))
        elif _has(b, "ytd_ebitda_gbp") and ytd > 0:
            self._set_kpi("ebitda_margin_pct", _num(b, "ytd_ebitda_gbp") / ytd * 100)
        if _has(b, "active_clients"):
            self._set_kpi("active_clients", _num(b, "active_clients"))
        behind = ytd > 0 and ytd < phased * (1 - REVENUE_BEHIND_PCT / 100)
        if behind:
            self.state["months_behind"] += 1
            self.create_task(f"Re-forecast: YTD revenue £{int(ytd):,} vs phased plan £{int(phased):,}", 5, "high")
            if self.state["months_behind"] == 3:
                self.create_task("Inform the Chair: three consecutive months behind revenue plan", 3, "critical")
        else:
            self.state["months_behind"] = 0
        self._record("month_end_review", f"month {month}", "behind_plan" if behind else "on_plan",
                     ytd_revenue_gbp=int(ytd), phased_plan_gbp=int(phased))
        return []

    def _on_finance_budget_variance_flagged(self, m: Message) -> list[Message]:
        b = m.body
        dept = _text(b, "department", "unknown")
        variance = abs(_num(b, "variance_pct"))
        if variance >= HIRING_HOLD_VARIANCE_PCT:
            holds = self.state["hiring_holds"]
            if dept not in holds:
                holds.append(dept)
                holds.sort()
            self.create_task(f"Variance review with {dept} head and CFO ({variance:.1f}%)", 5, "high")
            outcome = "hiring_hold_set"
        else:
            outcome = "logged_for_monthly_review"
        self._record("variance_review", dept, outcome, variance_pct=variance)
        return []

    def _on_finance_cash_forecast_updated(self, m: Message) -> list[Message]:
        runway = _num(m.body, "runway_months", -1.0) if _has(m.body, "runway_months") else None
        if runway is None:
            self.log_event("executive.activity.cash_review", "no runway in forecast")
            return []
        self.state["runway_months"] = runway
        self._set_kpi("cash_runway_months", runway)
        self._record("cash_review", "cash forecast", "freeze" if runway < RUNWAY_FREEZE_MONTHS else "ok",
                     runway_months=runway)
        if runway < RUNWAY_CRISIS_MONTHS and not self.state["liquidity_crisis"]:
            self.state["liquidity_crisis"] = True
            return self._declare_crisis("liquidity", "critical", m, "cash-runway",
                                        f"Cash runway of {runway:.1f} months is below 6 months")
        return []

    def _on_data_kpi_report_published(self, m: Message) -> list[Message]:
        kpis = m.body.get("kpis")
        applied = 0
        if isinstance(kpis, dict):
            for name, value in sorted(kpis.items()):
                if name in self.state["kpis"] and isinstance(value, (int, float)) and not isinstance(value, bool):
                    self._set_kpi(name, float(value))
                    applied += 1
        self._record("kpi_updated", "data kpi report", "applied", kpis_applied=applied)
        return []

    def _on_data_forecast_updated(self, m: Message) -> list[Message]:
        delta = _num(m.body, "delta_pct")
        if delta <= -REVENUE_BEHIND_PCT:
            self.create_task(f"Rerun scenarios: forecast revised {delta:.1f}%", 5, "high")
            outcome = "scenario_task_created"
        else:
            outcome = "noted"
        self._record("forecast_review", _text(m.body, "metric", "forecast"), outcome, delta_pct=delta)
        return []

    # ------------------------------------------------------------------ SOP-06 crises
    def _declare_crisis(self, category: str, severity: str, m: Message, key: str, summary: str,
                        incident_id: str = "") -> list[Message]:
        active = self.state["crisis_active"]
        if key in active:
            self.log_event("executive.activity.crisis_already_active", key, crisis_id=active[key]["crisis_id"])
            return []
        seq = self._next("crisis")
        crisis_id = f"CRS-{seq:04d}"
        detected = int(_num(m.body, "detected_day", self.clock.day))
        hours = max(self.clock.day - detected, 0) * 24.0
        self._set_kpi("crisis_declaration_hours", hours)
        briefing = self.ask_llm(f"Draft a two-line internal holding statement for {category} crisis {crisis_id}: "
                                f"{summary}. Legal review required before any external use.")
        actions = ["Commander: Chief Executive Officer", "Daily crisis review at 09:00",
                   "Hiring freeze for non-critical requisitions", "General Counsel reviews all external statements"]
        if category == "data_breach":
            actions.append("General Counsel, CISO and CEO decide on ICO notification within 72 hours")
        body = {
            "crisis_id": crisis_id, "category": category, "severity": severity, "trigger_topic": m.topic,
            "incident_id": incident_id, "summary": summary, "commander": "Chief Executive Officer",
            "war_room_cadence": "daily 09:00", "next_review_day": self.clock.day + 1,
            "declared_day": self.clock.day, "actions": actions, "briefing": briefing,
        }
        if _has(m.body, "client_id"):
            body["client_id"] = m.body["client_id"]
        active[key] = dict(body)
        self._record("crisis_declared", crisis_id, category, severity=severity, incident_id=incident_id)
        msgs = [self.emit("executive.crisis_declared", body, reply_to=m.id)]
        if severity == "critical":
            msgs.extend(self._hold_board("crisis", ["Crisis briefing", summary], 1, "Chief Executive Officer",
                                         [f"Noted declaration of {crisis_id}"]))
        return msgs

    def _on_it_security_incident_detected(self, m: Message) -> list[Message]:
        b = m.body
        incident = _text(b, "incident_id", f"INC-{m.id}")
        severity = _text(b, "severity", "medium").lower()
        if severity == "critical":
            return self._declare_crisis("security_incident", "critical", m, incident,
                                        _text(b, "summary", "Critical security incident"), incident)
        if severity == "high":
            self.create_task(f"CEO briefing on high-severity incident {incident}", 1, "high")
        self._record("incident_watch", incident, f"{severity}_no_crisis")
        return []

    def _on_it_security_data_breach_confirmed(self, m: Message) -> list[Message]:
        b = m.body
        incident = _text(b, "incident_id", f"INC-{m.id}")
        if incident in self.state["crisis_active"]:
            self._record("breach_confirmed", incident, "crisis_already_active",
                         ico_deadline_day=self.clock.day + 3)
            return []
        return self._declare_crisis("data_breach", "critical", m, incident,
                                    _text(b, "summary", "Personal data breach confirmed"), incident)

    def _on_legal_regulator_notification_filed(self, m: Message) -> list[Message]:
        b = m.body
        incident = _text(b, "incident_id", f"REG-{m.id}")
        if incident in self.state["crisis_active"] or self._crisis_active():
            self._record("regulator_notified", incident, "crisis_already_active", regulator=_text(b, "regulator"))
            return []
        return self._declare_crisis("regulatory", "high", m, incident,
                                    _text(b, "summary", "Regulator notification filed"), incident)

    def _on_marketing_brand_incident_raised(self, m: Message) -> list[Message]:
        b = m.body
        severity = _text(b, "severity", "medium").lower()
        incident = _text(b, "incident_id", f"BRD-{m.id}")
        if severity == "critical":
            return self._declare_crisis("reputational", "critical", m, incident,
                                        _text(b, "summary", "Critical brand incident"), incident)
        if severity == "high":
            self.create_task(f"CEO review of brand incident {incident}", 2, "high")
        self._record("brand_incident", incident, f"{severity}_no_crisis")
        return []

    def _on_it_security_incident_resolved(self, m: Message) -> list[Message]:
        incident = _text(m.body, "incident_id")
        crisis = self.state["crisis_active"].pop(incident, None)
        if crisis is None:
            self._record("incident_resolved", incident or "unknown", "no_crisis_active")
            return []
        duration = self.clock.day - crisis["declared_day"]
        self.state["crisis_history"].append({"crisis_id": crisis["crisis_id"], "duration_days": duration})
        self.create_task(f"Post-incident review for {crisis['crisis_id']}", 14, "high")
        self._record("crisis_stood_down", crisis["crisis_id"], "stood_down", duration_days=duration)
        return []

    # ------------------------------------------------------------------ SOP-02 board and strategy
    def _hold_board(self, meeting_type: str, agenda: list[str], delay_days: int, requested_by: str,
                    decisions: Optional[list[str]] = None) -> list[Message]:
        seq = self._next("meeting")
        held = self.clock.day + delay_days
        body = {
            "meeting_id": f"BM-{self.fiscal_year}-{seq:02d}", "meeting_type": meeting_type, "agenda": list(agenda),
            "decisions": list(decisions or []), "attendees": list(BOARD_MEMBERS),
            "pack_issued_day": max(held - 7, self.clock.day) if meeting_type != "crisis" else held,
            "minutes_due_day": held + 7, "held_day": held, "requested_by": requested_by,
        }
        self._record("board_meeting", body["meeting_id"], meeting_type, held_day=held)
        return [self.emit("executive.board_meeting_held", body, delay_days=delay_days)]

    def _on_external_board_request(self, m: Message) -> list[Message]:
        b = m.body
        kind = _text(b, "kind", "ad_hoc_meeting")
        default_notice = 1 if self._crisis_active() else (5 if kind == "written_consent" else BOARD_NOTICE_DAYS)
        notice = int(_num(b, "notice_days", default_notice))
        agenda = list(b["agenda"]) if isinstance(b.get("agenda"), list) else [kind.replace("_", " ")]
        change = b.get("strategy_change")
        decisions = [f"Approved strategy change: {change}"] if change else []
        msgs = self._hold_board("ad_hoc", agenda, notice, _text(b, "requested_by", "Board"), decisions)
        if change:
            n = self._next("strategy")
            body = {"version": f"STR-{self.fiscal_year}-{n}", "summary": str(change)[:200],
                    "changes": [str(change)], "board_approved": True,
                    "effective_day": self.clock.day + notice, "decided_day": self.clock.day + notice}
            self._record("strategy", body["version"], "board_approved")
            msgs.append(self.emit("executive.strategy_updated", body, delay_days=notice))
        return msgs

    # ------------------------------------------------------------------ SOP-07 pricing, roadmap, regulation
    def _on_product_pricing_change_proposed(self, m: Message) -> list[Message]:
        b = m.body
        tier = _text(b, "tier")
        change_id = _text(b, "change_id", _text(b, "proposal_id", f"PRC-{m.id}"))
        old = _num(b, "old_price_gbp", float(LIST_PRICE_GBP.get(tier, 0)))
        if _has(b, "new_price_gbp") and old:
            pct = (_num(b, "new_price_gbp") - old) / old * 100
            new = _num(b, "new_price_gbp")
        else:
            pct = _num(b, "change_pct")
            new = old * (1 + pct / 100)
        margin = _num(b, "margin_impact_pct")
        reasons = []
        if abs(pct) > PRICE_CHANGE_CEILING_PCT:
            reasons.append("change_exceeds_15pct")
        if margin < 0:
            reasons.append("negative_margin_impact")
        if reasons:
            self._record("pricing_decision", change_id, "declined", change_pct=round(pct, 1))
            recipient = m.sender if m.sender in DEPARTMENTS else "product"
            return [self.emit("executive.internal.pricing_change_declined",
                              {"change_id": change_id, "tier": tier, "reasons": reasons,
                               "change_pct": round(pct, 1), "decided_day": self.clock.day},
                              recipient=recipient, reply_to=m.id)]
        out = {
            "change_id": change_id, "tier": tier, "service_line": _text(b, "service_line", tier.split("_")[0]),
            "old_price_gbp": int(old), "new_price_gbp": int(round(new)), "change_pct": round(pct, 1),
            "effective_day": self.clock.day + 30, "conditions": ["legal_review_of_open_proposals"],
            "approver": "Chief Executive Officer", "decided_day": self.clock.day,
        }
        self._record("pricing_decision", change_id, "approved", change_pct=round(pct, 1))
        return [self.emit("executive.pricing_change_approved", out, reply_to=m.id)]

    def _on_product_roadmap_published(self, m: Message) -> list[Message]:
        self.create_task("Review product roadmap at the next quarterly strategy review", 30, "low")
        self._record("roadmap_review", _text(m.body, "roadmap_id", "roadmap"), "queued_for_strategy_review")
        return []

    def _on_legal_regulatory_change_noted(self, m: Message) -> list[Message]:
        impact = _text(m.body, "impact", "operational").lower()
        priority = "high" if impact == "strategic" else "medium"
        self.create_task(f"Assess regulatory change: {_text(m.body, 'summary', 'see Legal note')}", 10, priority)
        self._record("regulatory_review", _text(m.body, "regulation", "regulation"),
                     "board_agenda" if impact == "strategic" else "task_created", impact=impact)
        return []

    # ------------------------------------------------------------------ SOP-08 clients
    def _on_customer_success_churn_risk_flagged(self, m: Message) -> list[Message]:
        b = m.body
        value = _num(b, "annual_value_gbp", _num(b, "amount_gbp"))
        client = _text(b, "client_id", "CL-UNKNOWN")
        if value >= SPONSOR_CALL_ANNUAL_VALUE_GBP:
            self.create_task(f"CEO sponsor call with {_text(b, 'client_name', client)}", 3, "high")
            outcome = "sponsor_call_task"
        else:
            outcome = "left_with_customer_success"
        self._record("churn_risk", client, outcome, annual_value_gbp=int(value))
        return []

    def _on_customer_success_client_churned(self, m: Message) -> list[Message]:
        b = m.body
        client = _text(b, "client_id", "CL-UNKNOWN")
        value = max(_num(b, "annual_value_gbp", _num(b, "amount_gbp")),
                    self.state["client_revenue_gbp"].get(client, 0.0))
        self.state["client_revenue_gbp"].pop(client, None)
        self._update_top_client()
        share = self._client_share_pct(value)
        if share >= KEY_CLIENT_CRISIS_PCT:
            return self._declare_crisis("key_client_loss", "high", m, f"{client}:churn",
                                        f"Loss of {_text(b, 'client_name', client)} ({share}% of planned revenue)")
        self.create_task(f"Lessons learned: churn of {client}", 14, "medium")
        self._record("client_churned", client, "lessons_task", share_pct=share)
        return []

    def _on_finance_collections_escalated(self, m: Message) -> list[Message]:
        b = m.body
        amount = _num(b, "amount_gbp")
        if amount >= COLLECTIONS_SPONSOR_GBP:
            self.create_task(f"CEO sponsor call on overdue {_text(b, 'invoice_id', 'invoice')}", 3, "high")
            outcome = "sponsor_call_task"
        else:
            outcome = "left_with_finance"
        self._record("collections", _text(b, "client_id", "client"), outcome, amount_gbp=int(amount),
                     days_overdue=int(_num(b, "days_overdue")))
        return []

    def _on_legal_client_dispute_raised(self, m: Message) -> list[Message]:
        b = m.body
        severity = _text(b, "severity", "medium").lower()
        amount = _num(b, "amount_gbp")
        client = _text(b, "client_id", "CL-UNKNOWN")
        if severity == "critical" and amount >= DEAL_CEO_THRESHOLD_GBP:
            return self._declare_crisis("client_dispute", "high", m, f"{client}:dispute",
                                        _text(b, "summary", f"Critical dispute with {client}"))
        if severity in ("high", "critical") or amount >= DEAL_CEO_THRESHOLD_GBP:
            self.create_task(f"CEO review of dispute with {client}", 1 if severity == "critical" else 3, "high")
        self._record("client_dispute", client, severity, amount_gbp=int(amount))
        return []

    def _on_delivery_quality_issue_raised(self, m: Message) -> list[Message]:
        b = m.body
        severity = _text(b, "severity", "medium").lower()
        if severity in ("high", "critical"):
            self.create_task(f"Executive sponsor for quality issue on {_text(b, 'engagement_id', 'engagement')}",
                             1 if severity == "critical" else 3, "critical" if severity == "critical" else "high")
        self._record("quality_issue", _text(b, "engagement_id", "engagement"), severity)
        return []

    # ------------------------------------------------------------------ SOP-10 governance
    def _on_legal_compliance_finding_raised(self, m: Message) -> list[Message]:
        severity = _text(m.body, "severity", "medium").lower()
        if severity in ("high", "critical"):
            self.create_task(f"Remediation owner and date for finding {_text(m.body, 'finding_id', 'finding')}",
                             5, "high")
        self._record("governance_review", _text(m.body, "finding_id", "finding"), severity)
        return []

    def _on_legal_ai_risk_review_completed(self, m: Message) -> list[Message]:
        outcome = _text(m.body, "outcome", "approved").lower()
        if outcome != "approved":
            self.create_task(f"Follow up AI risk review outcome '{outcome}'", 10, "medium")
        self._record("governance_review", _text(m.body, "review_id", "ai risk review"), outcome)
        return []

    def _on_it_security_certification_status_updated(self, m: Message) -> list[Message]:
        cert = _text(m.body, "certification", "unspecified")
        status = _text(m.body, "status", "unknown").lower()
        self.state["certifications"][cert] = status
        if status in ("lapsed", "suspended"):
            self.create_task(f"CEO decision on {cert} {status}: US launch gate at risk", 3, "high")
        self._record("certification_status", cert, status)
        return []

    def _on_operations_continuity_test_completed(self, m: Message) -> list[Message]:
        result = _text(m.body, "result", "passed").lower()
        if result in ("fail", "failed"):
            self.create_task("Remediate failed continuity test with the COO", 10, "high")
        self._record("governance_review", "continuity test", result)
        return []

    def _on_operations_process_improvement_proposed(self, m: Message) -> list[Message]:
        cost = _num(m.body, "estimated_cost_gbp", _num(m.body, "cost_gbp"))
        if cost > 250_000:
            owner, tier = "CEO", "ceo_decision"
        elif cost > 50_000:
            owner, tier = "CFO", "cfo_decision"
        else:
            owner, tier = "proposer head", "within_head_delegation"
        if tier != "within_head_delegation":
            self.create_task(f"{owner} to decide process improvement costing £{int(cost):,}", 5, "medium")
        self._record("process_improvement", _text(m.body, "proposal_id", "proposal"), tier, cost_gbp=int(cost))
        return []

    def _on_data_agent_quality_report_published(self, m: Message) -> list[Message]:
        score = _num(m.body, "quality_score", 100.0)
        critical = int(_num(m.body, "critical_issues"))
        if score < AGENT_QUALITY_FLOOR or critical > 0:
            self.create_task("CDAIO plan for agent quality below floor or open critical issues", 5, "high")
        self._record("agent_quality", "agent quality report", "below_floor" if score < AGENT_QUALITY_FLOOR else "ok",
                     quality_score=score, critical_issues=critical)
        return []

    def _on_delivery_capacity_forecast_updated(self, m: Message) -> list[Message]:
        shortfall = _num(m.body, "shortfall_fte")
        utilisation = _num(m.body, "utilisation_pct")
        if shortfall >= 3 or utilisation > 85:
            self.create_task("Prioritise delivery requisitions against capacity shortfall", 5, "high")
        self._record("capacity_review", "delivery capacity", "shortfall" if shortfall >= 3 or utilisation > 85
                     else "ok", shortfall_fte=shortfall, utilisation_pct=utilisation)
        return []

    def _on_people_engagement_survey_completed(self, m: Message) -> list[Message]:
        score = _num(m.body, "engagement_score", 100.0)
        if score < ENGAGEMENT_FLOOR:
            self.create_task("Leadership action plan for low engagement score", 14, "high")
        self._record("engagement_review", "engagement survey", "below_floor" if score < ENGAGEMENT_FLOOR else "ok",
                     engagement_score=score)
        return []

    # ------------------------------------------------------------------ cadences
    def tick(self) -> list[Message]:
        msgs: list[Message] = []
        date = self.clock.date
        if date.year <= 2028:
            msgs.extend(self._publish_okrs(self.fiscal_year))
        msgs.extend(self._process_board_queue())
        quarter_key = f"{date.year}-{date.month}"
        if (date.month in (1, 4, 7, 10) and date.day >= 15 and self.clock.is_weekday
                and quarter_key not in self.state["board_quarters"]):
            self.state["board_quarters"].append(quarter_key)
            msgs.extend(self._hold_board(
                "quarterly", ["KPIs and financials", "Pipeline and decisions log", "Risk register", "OKR review"],
                0, "Chief Executive Officer", ["Reviewed quarterly pack"]))
        if self.clock.is_month_start:
            self.log_event("executive.activity.monthly_kpi_review", date.isoformat(), kpis=self.kpi_snapshot())
        for crisis in self.state["crisis_active"].values():
            self.log_event("executive.activity.crisis_review", crisis["crisis_id"], category=crisis["category"])
        return msgs

    def _process_board_queue(self) -> list[Message]:
        due = [p for p in self.state["pending_board"] if p["due_day"] <= self.clock.day]
        if not due:
            return []
        self.state["pending_board"] = [p for p in self.state["pending_board"] if p["due_day"] > self.clock.day]
        decisions = [f"Approved {p['kind']} {p['payload'].get('deal_id') or p['payload'].get('requisition_id')}"
                     for p in due]
        msgs = self._hold_board("ad_hoc", ["Written resolutions"], 0, "Chief of Staff", decisions)
        for item in due:
            payload = dict(item["payload"])
            payload["approver"] = "Board of Directors"
            payload["decided_day"] = self.clock.day
            if item["kind"] == "deal":
                payload["board_ratified"] = True
                payload["summary"] = f"{payload['deal_id']} ratified by the Board at £{payload['amount_gbp']:,}"
                self._record("board_ratification", payload["deal_id"], payload["decision"])
                msgs.append(self.emit("executive.deal_decision_made", payload))
            else:
                self._record("board_ratification", payload["requisition_id"], "approved")
                msgs.append(self.emit("executive.headcount_approved", payload))
        return msgs


def build_agent(llm, bus, clock, log) -> ExecutiveAgent:
    """Construct the executive agent. Does not register with the bus or publish."""
    role = Role("Chief Executive Officer", "executive", "executive", (1, 1, 1), (200000, 260000), None)
    return ExecutiveAgent("executive", "executive", role, llm, bus, clock, log)
