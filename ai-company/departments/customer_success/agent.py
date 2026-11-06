"""Customer Success department agent (Chief Customer Officer's desk).

Owns client health scoring, onboarding handover, Keep support triage, renewals, churn prevention and
post-mortems, expansion signalling, case-study eligibility and the department budget submission.
All logic is deterministic and works offline with ``core.MockLLM``. See sops.md for the procedures
this module implements (SOP-CUSTOMER_SUCCESS-01 to -14).
"""

from __future__ import annotations

import math
import statistics
from dataclasses import replace
from datetime import timedelta
from typing import Callable, Optional

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# ---------------------------------------------------------------------------------------------
# KPIs (FY2026 targets, mirrors kpis.md section 1)
# ---------------------------------------------------------------------------------------------
KPIS: list[Kpi] = [
    Kpi("net_revenue_retention", "percent", 100.0, None),            # floor FY2026; 115 FY2027 (COMPANY.md §5.1)
    Kpi("gross_revenue_retention", "percent", 90.0, None),
    Kpi("logo_retention", "percent", 83.0, None),                    # COMPANY.md §5.1 planning rate
    Kpi("nps", "points", 40.0, None),
    Kpi("csat", "percent", 90.0, None),
    Kpi("avg_health_score", "points", 72.0, None),
    Kpi("green_client_share", "percent", 60.0, None),
    Kpi("keep_attach_forge_build_scale", "percent", 100.0, None),    # COMPANY.md §2: Keep attaches to every Build/Scale
    Kpi("keep_attach_compass_programme", "percent", 40.0, None),     # COMPANY.md §2 minimum (>=40%)
    Kpi("support_first_response_sla", "percent", 95.0, None),
    Kpi("at_risk_save_rate", "percent", 40.0, None),
    Kpi("qbr_completion_rate", "percent", 90.0, None),
    Kpi("onboarding_handover_days", "days", 15.0, None, higher_is_better=False),
    Kpi("cs_cost_pct_revenue", "percent", 2.3, None, higher_is_better=False),   # 140 / 6,000 (§5.4, §5.1)
]

# ---------------------------------------------------------------------------------------------
# Company facts used as constants
# ---------------------------------------------------------------------------------------------
# COMPANY.md §3.3 Keep tiers (monthly, annual, support days per quarter; Enterprise has an embedded team)
KEEP_TIERS: dict[str, dict] = {
    "keep_essential": {"monthly_gbp": 8000, "annual_gbp": 96000, "support_days_per_quarter": 5},
    "keep_plus": {"monthly_gbp": 18000, "annual_gbp": 216000, "support_days_per_quarter": 15},
    "keep_enterprise": {"monthly_gbp": 40000, "annual_gbp": 480000, "support_days_per_quarter": None},
}
# COMPANY.md §3.1 / §3.2 prices used for expansion signals
PRICES_GBP: dict[str, int] = {
    "compass_spark": 45000, "compass_sprint": 120000, "compass_programme": 350000,
    "forge_pilot": 90000, "forge_build": 260000, "forge_scale": 650000,
}
# COMPANY.md §2 land and expand: Keep attaches to every Forge Build/Scale and >=40% of Compass Programmes.
KEEP_ATTACH: dict[str, str] = {
    "forge_build": "keep_plus", "forge_scale": "keep_enterprise", "compass_programme": "keep_essential",
}
# Policy target, percent of completed engagements with a signed Keep contract within the window (kpis.md). The
# targets equal COMPANY.md §2 in every year: 100% of Forge Build and Scale, at least 40% of Compass Programmes. A
# Build or Scale client that has not signed by ATTACH_REOFFER_DAYS is re-offered a reduced scope; one that has not
# signed when the window closes is a policy exception escalated to the CEO (SOP-CUSTOMER_SUCCESS-08).
KEEP_ATTACH_POLICY_PCT: dict[str, float] = {"forge_build": 100.0, "forge_scale": 100.0, "compass_programme": 40.0}
ATTACH_WINDOW_DAYS = 365          # signed Keep contract within 12 months of completion counts as attached
ATTACH_REOFFER_DAYS = 90          # unattached Keep offer is re-offered at reduced scope after 90 days
# COMPANY.md §10 journey: Spark -> Pilot -> Build -> Keep Plus
UPSELL_PATH: dict[str, str] = {
    "compass_spark": "forge_pilot", "compass_sprint": "forge_pilot", "forge_pilot": "forge_build",
}
# COMPANY.md §7: Keep renewal uplift is CPI + 2%, capped at 7%. CPI planning assumption: economics.md section 4.
CPI_PLANNING_PCT = 3.0
RENEWAL_UPLIFT_PCT = min(CPI_PLANNING_PCT + 2.0, 7.0)
RENEWAL_LEAD_DAYS = 90            # renewal_due is emitted 90 days before term end (SOP-CUSTOMER_SUCCESS-07)
CLIENT_DECISION_WINDOW_DAYS = 14  # days between renewal proposal and client decision in the model
CLIENTS_PER_NAMED_CSM = 22        # coverage ceiling that triggers a hire request (economics.md section 3)
POST_MORTEM_DAYS = 21             # 15 business days
HANDOVER_TARGET_DAYS = 15         # contract signature to accepted handover (kpis.md onboarding_handover_days FY2026)
MIGRATED_CONTRACT_DAYS = 30       # a contract whose start day is >30 days before signature carries no onboarding clock
SIGNAL_WINDOW_DAYS = 30           # compound churn-risk signal window (sops.md shared constants)
SIGNAL_MIN_COUNT = 2              # distinct negative signals inside the window that flag churn risk
ENTERPRISE_NPS_FLAG_MAX = 3       # NPS 0 to 3 from a Keep Enterprise sponsor flags churn risk
CANCEL_KEYWORDS = ("cancel", "terminate", "not renew", "switch provider", "leave you", "end the contract")
SLA_BREACH_SUPPORT_HIT = 10.0     # support component reduction for each recorded SLA breach
# Support desk load model (sops.md, Keep support SLAs): the simulated first-response and resolution time of a ticket is
# its SLA target x (TICKET_LOAD_BASE + TICKET_LOAD_PER_OPEN x tickets already open on the desk). A ticket that
# carries measured `first_response_hours` / `resolution_hours` uses those instead.
TICKET_LOAD_BASE = 0.5
TICKET_LOAD_PER_OPEN = 0.25
P4_OPEN_DAYS = 5                  # a P4 ticket has no resolution target; it counts as open this many days
# Hiring triggers (blueprint.md section 5, sops.md SOP-CUSTOMER_SUCCESS-14), evaluated monthly unless stated
TICKETS_MONTH_FIRST_SPECIALIST = 30    # more than 30 tickets in a month: first Client Support Specialist
LIVE_KEEP_FIRST_SPECIALIST = 8         # more than 8 live Keep clients: first Client Support Specialist
TICKETS_MONTH_THIRD_SPECIALIST = 150   # more than 150 tickets in a month: third Client Support Specialist
SLA_HIRE_FLOOR_PCT = 95.0         # first-response SLA below this for two months raises a specialist request
SLA_HIRE_MONTHS = 2
RENEWALS_FOR_MANAGER = 30         # more than 30 Keep renewals in the next 12 months: Renewals and Commercial Manager
TIME_TO_HIRE_DAYS = 45            # COMPANY.md §8: the seat starts this many days after the request
ROLE_CSM = "Customer Success Manager"
ROLE_SPECIALIST = "Client Support Specialist"
ROLE_RENEWALS = "Renewals and Commercial Manager"

# COMPANY.md §5.4 department envelopes, GBP (people, non_people) by fiscal year
BUDGET_GBP: dict[int, tuple[int, int]] = {
    2026: (90000, 50000), 2027: (450000, 340000), 2028: (1240000, 390000),
}
# COMPANY.md §6.1 year-end humans and agents by fiscal year
HEADCOUNT: dict[int, tuple[int, int]] = {2026: (1, 1), 2027: (6, 5), 2028: (14, 12)}
# Planned year-end humans by hireable role (blueprint.md section 3; the CCO is the first named client manager and is
# not in this table). A request that takes a role above its plan is outside the approved headcount plan.
ROLE_PLAN: dict[str, dict[int, int]] = {
    ROLE_CSM: {2026: 0, 2027: 2, 2028: 6},
    ROLE_SPECIALIST: {2026: 0, 2027: 2, 2028: 3},
    ROLE_RENEWALS: {2026: 0, 2027: 0, 2028: 1},
}
ROLE_LEVEL: dict[str, str] = {ROLE_CSM: "manager", ROLE_SPECIALIST: "consultant", ROLE_RENEWALS: "manager"}

# ---------------------------------------------------------------------------------------------
# Health score model (SOP-CUSTOMER_SUCCESS-02)
# ---------------------------------------------------------------------------------------------
HEALTH_WEIGHTS: dict[str, float] = {
    "adoption": 0.25,     # agent usage, active users, tasks automated vs plan
    "delivery": 0.20,     # milestone status, quality issues, acceptance
    "engagement": 0.15,   # sponsor and champion contact, QBR attendance
    "commercial": 0.15,   # payment behaviour, dispute status
    "sentiment": 0.15,    # NPS and CSAT
    "support": 0.10,      # ticket severity, incidents affecting the client
}
GREEN_MIN = 75.0
AMBER_MIN = 50.0
CLEAR_RISK_MIN = 60.0
INITIAL_COMPONENTS: dict[str, float] = {
    "adoption": 65.0, "delivery": 75.0, "engagement": 80.0, "commercial": 90.0, "sentiment": 75.0,
    "support": 85.0,
}
SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
TICKET_PRIORITY = {"critical": "P1", "high": "P2", "medium": "P3", "low": "P4"}
SUPPORT_HIT = {"critical": 25.0, "high": 15.0, "medium": 5.0, "low": 0.0}
QUALITY_HIT = {"critical": 30.0, "high": 20.0, "medium": 10.0, "low": 5.0}

# Keep support SLAs: priority -> (first response target, resolution or workaround target), in hours.
# Essential and Plus run on business hours (a business day = 10 hours, 08:00 to 18:00 UK). Enterprise P1 and P2
# run 24x7 (COMPANY.md §3.3 24x7 incident cover). Targets are department assumptions (economics.md section 4).
SUPPORT_SLA: dict[str, dict[str, tuple[float, Optional[float]]]] = {
    "keep_essential": {"P1": (4, 10), "P2": (10, 30), "P3": (20, 50), "P4": (30, None)},
    "keep_plus": {"P1": (1, 4), "P2": (4, 20), "P3": (10, 30), "P4": (20, None)},
    "keep_enterprise": {"P1": (0.25, 4), "P2": (1, 8), "P3": (4, 20), "P4": (10, None)},
}
SAVEABLE_REASONS = ("price", "budget", "service_quality", "champion_left", "low_usage", "scope")


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


class CustomerSuccessAgent(DepartmentAgent):
    """Chief Customer Officer agent: keeps clients healthy, renewed and expanding."""

    SUBSCRIBES = subscribes_for("customer_success")
    PUBLISHES = publishes_for("customer_success")

    # state accessors ----------------------------------------------------------------------
    @property
    def clients(self) -> dict[str, dict]:
        return self.state.setdefault("clients", {})

    def _counter(self, name: str) -> int:
        counters = self.state.setdefault("counters", {})
        counters[name] = counters.get(name, 0) + 1
        return counters[name]

    def _handlers(self) -> dict[str, Callable[[Message], list[Message]]]:
        return {
            "sales.deal_won": self._on_deal_won,
            "legal.contract_signed": self._on_contract_signed,
            "finance.billing_schedule_created": self._on_billing_schedule,
            "delivery.engagement_kickoff": self._on_kickoff,
            "delivery.milestone_reached": self._on_milestone,
            "delivery.engagement_completed": self._on_engagement_completed,
            "delivery.quality_issue_raised": self._on_quality_issue,
            "finance.invoice_issued": self._on_invoice_issued,
            "finance.payment_received": self._on_payment_received,
            "finance.invoice_overdue": self._on_invoice_overdue,
            "external.client_feedback_submitted": self._on_feedback,
            "external.client_notice_of_termination": self._on_termination_notice,
            "sales.renewal_proposal_sent": self._on_renewal_proposal,
            "legal.client_dispute_raised": self._on_dispute,
            "it_security.incident_detected": self._on_incident_detected,
            "it_security.data_breach_confirmed": self._on_breach_confirmed,
            "it_security.incident_resolved": self._on_incident_resolved,
            "product.release_shipped": self._on_release_shipped,
            "marketing.case_study_requested": self._on_case_study_requested,
            "finance.budget_cycle_opened": self._on_budget_cycle,
            "executive.budget_approved": self._on_budget_approved,
            "executive.okrs_set": self._on_okrs_set,
            "executive.strategy_updated": self._on_strategy_updated,
            "executive.crisis_declared": self._on_crisis,
        }

    # contract -----------------------------------------------------------------------------
    def handle(self, message: Message) -> list[Message]:
        handler = self._handlers().get(message.topic)
        if handler is None:
            self.log_event("customer_success.activity.unhandled_topic", message.topic, message_id=message.id)
            return []
        out = handler(message)
        return list(out)

    def tick(self) -> list[Message]:
        """Queued decisions, daily renewal scan, weekly health refresh and capacity check, monthly hiring review,
        quarterly QBR tasks."""
        out: list[Message] = self._run_scheduled()
        day = self.clock.day
        for cid in sorted(self.clients):
            c = self.clients[cid]
            keep = c.get("keep")
            if not keep or c["status"] == "churned" or keep["renewal_notified"]:
                continue
            if keep["term_end_day"] - day <= RENEWAL_LEAD_DAYS:
                keep["renewal_notified"] = True
                amount = c["annual_value_gbp"]
                proposed = round(amount * (1 + RENEWAL_UPLIFT_PCT / 100.0))
                self.create_task(f"Renewal plan for {c['client_name']} ({cid})", 5, "high")
                out.append(self.emit("customer_success.renewal_due", {
                    "client_id": cid, "client_name": c["client_name"], "contract_id": keep["contract_id"],
                    "service_line": "keep", "tier": keep["tier"], "amount_gbp": amount,
                    "proposed_uplift_pct": RENEWAL_UPLIFT_PCT, "proposed_amount_gbp": proposed,
                    "due_day": keep["term_end_day"], "health_score": c["health"], "band": c["band"],
                    "summary": f"Keep renewal for {c['client_name']} due in {keep['term_end_day'] - day} days",
                }))
        self._handover_watch()
        self._attach_watch()
        if self.clock.every(7):
            out.extend(self._weekly_review())
        if self.clock.is_month_start:
            out.extend(self._monthly_hiring_review())
            if self.clock.date.month in (1, 4, 7, 10):
                self._schedule_qbrs()
        return out

    # deterministic queue of human decisions modelled by the agent (no private topics) ------------
    def _schedule(self, kind: str, delay_days: int, payload: dict) -> None:
        """Queue a decision for a later tick. A newer item of the same kind for the same client replaces the old."""
        queue = self.state.setdefault("scheduled", [])
        queue[:] = [i for i in queue if not (i["kind"] == kind and i["payload"].get("client_id") ==
                                             payload.get("client_id"))]
        queue.append({"seq": self._counter("sched"), "due_day": self.clock.day + delay_days, "kind": kind,
                      "payload": payload})

    def _run_scheduled(self) -> list[Message]:
        handlers = {"renewal_decision": self._on_renewal_decision, "save_deadline": self._on_save_deadline}
        out: list[Message] = []
        queue = self.state.setdefault("scheduled", [])
        while True:
            due = sorted((i for i in queue if i["due_day"] <= self.clock.day), key=lambda i: (i["due_day"], i["seq"]))
            if not due:
                return out
            queue.remove(due[0])
            out.extend(handlers[due[0]["kind"]](due[0]["payload"]))

    # core health model --------------------------------------------------------------------
    @staticmethod
    def score_of(components: dict[str, float]) -> float:
        """Weighted health score 0 to 100, one decimal place."""
        return round(sum(HEALTH_WEIGHTS[k] * components[k] for k in HEALTH_WEIGHTS), 1)

    @staticmethod
    def band_of(score: float) -> str:
        return "green" if score >= GREEN_MIN else "amber" if score >= AMBER_MIN else "red"

    def _get_client(self, body: dict) -> Optional[dict]:
        cid = body.get("client_id")
        if not cid:
            name = body.get("client_name")
            for existing in sorted(self.clients):
                if name and self.clients[existing]["client_name"] == name:
                    return self.clients[existing]
            return None
        if cid not in self.clients:
            self.clients[cid] = {
                "client_id": cid, "client_name": body.get("client_name", cid), "service_line": None,
                "tier": None, "annual_value_gbp": int(body.get("amount_gbp", 0) or 0), "status": "onboarding",
                "components": dict(INITIAL_COMPONENTS), "health": self.score_of(INITIAL_COMPONENTS),
                "band": self.band_of(self.score_of(INITIAL_COMPONENTS)), "risk_open": False,
                "risk_severity": None, "dispute": False, "keep": None, "last_touch_day": self.clock.day,
                "nps_last": None, "csat_last": None, "overdue": {}, "invoices": {}, "case_study_consent": False,
                "expansion_flags": [], "engagement_completed": False, "pre_notice_health": None,
                "open_incidents": [], "qbr_quarters": [], "negatives": {}, "flag_days": [], "churn_day": None,
                "contract_signed_day": None, "handover_pending": False, "handover_done_day": None,
                "handover_flagged": False,
            }
            self.log_event("customer_success.activity.client_record_opened", cid, client_id=cid)
        client = self.clients[cid]
        if body.get("client_name") and client["client_name"] == cid:
            client["client_name"] = body["client_name"]
        return client

    def _adjust(self, c: dict, **deltas: float) -> None:
        for key, delta in deltas.items():
            c["components"][key] = _clamp(c["components"][key] + delta)

    def _rescore(self, c: dict, reason: str, force: bool = False) -> list[Message]:
        prev_score, prev_band = c["health"], c["band"]
        score = self.score_of(c["components"])
        band = self.band_of(score)
        c["health"], c["band"] = score, band
        out: list[Message] = []
        if force or band != prev_band or abs(score - prev_score) >= 5.0:
            lowest = sorted(c["components"], key=lambda k: (c["components"][k], k))[:2]
            out.append(self.emit("customer_success.health_score_updated", {
                "client_id": c["client_id"], "client_name": c["client_name"], "health_score": score,
                "band": band, "previous_score": prev_score, "previous_band": prev_band, "reason": reason,
                "drivers": lowest, "service_line": c["service_line"], "tier": c["tier"],
                "amount_gbp": c["annual_value_gbp"],
                "summary": f"{c['client_name']} health {prev_score} -> {score} ({band}): {reason}",
            }))
        if band == "red":
            out.extend(self._flag_risk(c, "critical" if score < 35.0 else "high", reason))
        elif c["risk_open"] and score >= CLEAR_RISK_MIN and not c["dispute"] and not self._active_signals(c):
            c["risk_open"], c["risk_severity"] = False, None
            self.log_event("customer_success.activity.risk_cleared", c["client_id"], client_id=c["client_id"],
                           health_score=score)
        return out

    def _flag_risk(self, c: dict, severity: str, reason: str) -> list[Message]:
        if c["status"] == "churned":
            return []
        if c["risk_open"] and SEVERITY_RANK[severity] <= SEVERITY_RANK[c["risk_severity"] or "low"]:
            return []
        if not c["risk_open"]:
            c["flag_days"].append(self.clock.day)
        c["risk_open"], c["risk_severity"] = True, severity
        self.create_task(f"Save plan for {c['client_name']} ({c['client_id']}): {reason}", 2,
                         "critical" if severity == "critical" else "high")
        return [self.emit("customer_success.churn_risk_flagged", {
            "client_id": c["client_id"], "client_name": c["client_name"], "severity": severity,
            "reason": reason, "health_score": c["health"], "band": c["band"],
            "amount_gbp": c["annual_value_gbp"], "service_line": c["service_line"], "tier": c["tier"],
            "recommended_action": "executive sponsor call within 2 business days; save plan owned by CCO",
            "summary": f"Churn risk ({severity}) at {c['client_name']}: {reason}",
        })]

    def _touch(self, c: dict) -> None:
        c["last_touch_day"] = self.clock.day

    # compound churn-risk signals (SOP-CUSTOMER_SUCCESS-06) -------------------------------------
    def _note_negative(self, c: dict, key: str, kind: str) -> None:
        entry = c["negatives"].get(key)
        if entry is None:
            c["negatives"][key] = {"day": self.clock.day, "kind": kind}
        elif kind not in entry["kind"]:
            entry["kind"] = f"{entry['kind']} + {kind}"

    def _active_signals(self, c: dict) -> list[str]:
        """Kinds of negative signals inside the window, only when there are at least SIGNAL_MIN_COUNT distinct ones."""
        live = [e["kind"] for k, e in sorted(c["negatives"].items())
                if self.clock.day - e["day"] <= SIGNAL_WINDOW_DAYS]
        return live if len(live) >= SIGNAL_MIN_COUNT else []

    def _check_signals(self, c: dict) -> list[Message]:
        live = self._active_signals(c)
        if not live:
            return []
        return self._flag_risk(c, "high", f"compound client signals in {SIGNAL_WINDOW_DAYS} days: "
                                         + "; ".join(live))

    def _keep_tier(self, c: dict) -> str:
        return (c["keep"] or {}).get("tier") or "keep_essential"

    # lifecycle: onboarding ----------------------------------------------------------------
    def _on_deal_won(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b)
        if c is None:
            self.log_event("customer_success.activity.unmatched", "deal_won without client", message_id=m.id)
            return []
        c["service_line"] = b.get("service_line", c["service_line"])
        c["tier"] = b.get("tier", c["tier"])
        if b.get("amount_gbp"):
            c["annual_value_gbp"] = int(b["amount_gbp"])
        if c["status"] == "churned":
            c["status"] = "onboarding"
        self._touch(c)
        self.create_task(f"Welcome call and stakeholder map for {c['client_name']}", 2, "high")
        self.create_task(f"Agree success plan and health baseline for {c['client_name']}", 10, "medium")
        self.log_event("customer_success.activity.onboarding_started", c["client_name"], client_id=c["client_id"],
                       deal_id=b.get("deal_id"), tier=c["tier"])
        out = self._rescore(c, "new client baseline", force=True)
        out.extend(self._capacity_check())
        return out

    def _on_contract_signed(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b)
        if c is None:
            return []
        c["service_line"] = b.get("service_line", c["service_line"])
        c["tier"] = b.get("tier", c["tier"])
        out: list[Message] = []
        # onboarding clock (kpis.md onboarding_handover_days): starts at signature unless the contract is migrated
        if int(b.get("start_day", self.clock.day)) >= self.clock.day - MIGRATED_CONTRACT_DAYS:
            c["contract_signed_day"], c["handover_pending"], c["handover_flagged"] = self.clock.day, True, False
        if c["service_line"] == "keep" or str(c["tier"] or "").startswith("keep_"):
            tier = c["tier"] if c["tier"] in KEEP_TIERS else "keep_essential"
            start = int(b.get("start_day", self.clock.day))
            term_months = int(b.get("term_months", 12))
            annual = int(b.get("amount_gbp") or KEEP_TIERS[tier]["annual_gbp"])
            c["annual_value_gbp"] = annual
            c["keep"] = {"tier": tier, "contract_id": b.get("contract_id", "CT-0000"), "start_day": start,
                         "term_end_day": start + round(term_months * 365 / 12), "renewal_notified": False,
                         "renewal_proposed": False}
            c["status"] = "active"
            for entry in self.state.setdefault("attach_ledger", {}).values():
                if (entry["client_id"] == c["client_id"] and not entry["attached"]
                        and self.clock.day - entry["completed_day"] <= ATTACH_WINDOW_DAYS):
                    entry["attached"], entry["attached_day"] = True, self.clock.day
            self.create_task(f"Keep onboarding: monitoring, SLA and QBR calendar for {c['client_name']}", 5, "high")
            out.extend(self._rescore(c, "Keep contract signed", force=False))
        else:
            self.create_task(f"File contract {b.get('contract_id', '')} and confirm sponsor contacts", 3, "low")
        self._touch(c)
        self.log_event("customer_success.activity.contract_recorded", c["client_name"], client_id=c["client_id"],
                       contract_id=b.get("contract_id"), tier=c["tier"])
        return out

    def _on_billing_schedule(self, m: Message) -> list[Message]:
        c = self._get_client(m.body)
        if c is None:
            return []
        c["billing_schedule"] = {"contract_id": m.body.get("contract_id"),
                                 "milestones": m.body.get("milestones", [])}
        self.create_task(f"Confirm invoice contacts and PO references for {c['client_name']}", 3, "low")
        self.log_event("customer_success.activity.billing_schedule_noted", c["client_name"],
                       client_id=c["client_id"], contract_id=m.body.get("contract_id"))
        return []

    def _on_kickoff(self, m: Message) -> list[Message]:
        c = self._get_client(m.body)
        if c is None:
            return []
        c["status"] = "in_delivery" if c["status"] in ("onboarding", "in_delivery") else c["status"]
        c["engagement_id"] = m.body.get("engagement_id")
        self._touch(c)
        self._adjust(c, engagement=+5.0)
        self.create_task(f"Handover pack and sponsor check-in for {c['client_name']} kickoff", 5, "medium")
        self._complete_handover(c)
        self.log_event("customer_success.activity.kickoff_handover", c["client_name"], client_id=c["client_id"],
                       engagement_id=m.body.get("engagement_id"))
        return self._rescore(c, "engagement kicked off")

    def _on_milestone(self, m: Message) -> list[Message]:
        c = self._get_client(m.body)
        if c is None:
            return []
        self._touch(c)
        self._adjust(c, delivery=+5.0, engagement=+2.0)
        self.log_event("customer_success.activity.milestone_noted", c["client_name"], client_id=c["client_id"],
                       engagement_id=m.body.get("engagement_id"), milestone=m.body.get("milestone"))
        return self._rescore(c, "milestone reached")

    def _on_engagement_completed(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b)
        if c is None:
            return []
        tier = b.get("tier") or c["tier"]
        c["status"] = "active"
        c["engagement_completed"] = True
        if tier in KEEP_ATTACH:
            ledger_key = b.get("engagement_id") or f"{c['client_id']}:{tier}"
            self.state.setdefault("attach_ledger", {}).setdefault(ledger_key, {
                "client_id": c["client_id"], "tier": tier, "completed_day": self.clock.day,
                "attached": c["keep"] is not None, "attached_day": self.clock.day if c["keep"] else None,
                "reoffered": False, "lapsed": False})
        self._touch(c)
        self._adjust(c, delivery=+10.0)
        self.create_task(f"Closeout review and 30-day post-engagement check for {c['client_name']}", 30, "medium")
        self.create_task(f"Send post-engagement NPS survey to {c['client_name']} sponsor", 7, "medium")
        out = self._rescore(c, "engagement completed")
        eng = b.get("engagement_id", "")
        if eng in c["expansion_flags"] or c["dispute"] or c["band"] == "red":
            return out
        has_keep = c["keep"] is not None
        rec_tier, rec_line, rec_amount = None, None, 0
        if tier in KEEP_ATTACH and not has_keep:
            rec_tier, rec_line = KEEP_ATTACH[tier], "keep"
            rec_amount = KEEP_TIERS[rec_tier]["annual_gbp"]
        elif tier in UPSELL_PATH:
            rec_tier = UPSELL_PATH[tier]
            rec_line, rec_amount = "forge", PRICES_GBP[rec_tier]
        if rec_tier:
            c["expansion_flags"].append(eng)
            out.append(self.emit("customer_success.expansion_opportunity_identified", {
                "client_id": c["client_id"], "client_name": c["client_name"], "engagement_id": eng,
                "service_line": rec_line, "tier": rec_tier, "amount_gbp": rec_amount,
                "source_tier": tier, "health_score": c["health"],
                "rationale": "land-and-expand path from completed " + str(tier),
                "summary": f"Recommend {rec_tier} for {c['client_name']} after {tier}",
            }))
        return out

    # lifecycle: quality, billing -------------------------------------------------------------
    def _on_quality_issue(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b)
        if c is None:
            return []
        sev = b.get("severity", "medium")
        sev = sev if sev in SEVERITY_RANK else "medium"
        self._adjust(c, delivery=-QUALITY_HIT[sev], sentiment=-(QUALITY_HIT[sev] / 2.0))
        self.create_task(f"Recovery plan with delivery for {c['client_name']}: {b.get('summary', 'quality issue')}",
                         2, "high" if SEVERITY_RANK[sev] >= 3 else "medium")
        self.log_event("customer_success.activity.quality_issue_noted", c["client_name"], client_id=c["client_id"],
                       severity=sev)
        out = self._rescore(c, f"delivery quality issue ({sev})")
        if SEVERITY_RANK[sev] >= 3:
            out.extend(self._flag_risk(c, "high", f"delivery quality issue ({sev})"))
        return out

    def _on_invoice_issued(self, m: Message) -> list[Message]:
        c = self._get_client(m.body)
        if c is None:
            return []
        inv = m.body.get("invoice_id", f"INV-UNKNOWN-{self._counter('inv'):04d}")
        c["invoices"][inv] = int(m.body.get("amount_gbp", 0) or 0)
        self.log_event("customer_success.activity.invoice_noted", c["client_name"], client_id=c["client_id"],
                       invoice_id=inv)
        return []

    def _on_payment_received(self, m: Message) -> list[Message]:
        c = self._get_client(m.body)
        if c is None:
            return []
        inv = m.body.get("invoice_id")
        c["invoices"].pop(inv, None)
        c["overdue"].pop(inv, None)
        if not c["overdue"]:
            c["components"]["commercial"] = max(c["components"]["commercial"], 90.0)
        self._touch(c)
        self.log_event("customer_success.activity.payment_noted", c["client_name"], client_id=c["client_id"],
                       invoice_id=inv)
        return self._rescore(c, "payment received")

    def _on_invoice_overdue(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b)
        if c is None:
            return []
        days = int(b.get("days_overdue", 7))
        inv = b.get("invoice_id", f"INV-UNKNOWN-{self._counter('inv'):04d}")
        c["overdue"][inv] = days
        worst = max(c["overdue"].values())
        # COMPANY.md §7 ladder: reminder day 31, call day 38, finance-head escalation day 45
        commercial = 90.0 if worst <= 0 else 75.0 if worst < 31 else 50.0 if worst < 45 else 25.0
        c["components"]["commercial"] = min(c["components"]["commercial"], commercial)
        self.create_task(f"Relationship call with sponsor of {c['client_name']} alongside finance (day 38 step)",
                         max(0, 38 - days), "medium")
        self.log_event("customer_success.activity.overdue_noted", c["client_name"], client_id=c["client_id"],
                       invoice_id=inv, days_overdue=days)
        return self._rescore(c, f"invoice {inv} overdue {days} days")

    # feedback and support -------------------------------------------------------------------
    def _on_feedback(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b)
        if c is None:
            self.log_event("customer_success.activity.unmatched", "feedback without client", message_id=m.id)
            return []
        kind = b.get("kind", "nps")
        self._touch(c)
        out: list[Message] = []
        if kind == "support_ticket":
            return self._on_ticket(c, b)
        category = kind
        score = b.get("score")
        if kind == "nps" and score is not None:
            score = max(0, min(10, int(score)))
            c["nps_last"] = score
            category = "promoter" if score >= 9 else "passive" if score >= 7 else "detractor"
            c["components"]["sentiment"] = _clamp(score * 10.0)
            if category == "detractor":
                self._note_negative(c, "detractor", "detractor NPS")
                self.create_task(f"Close the loop with {c['client_name']} detractor within 2 business days", 2, "high")
        elif kind == "csat" and score is not None:
            score = max(1, min(5, int(score)))
            c["csat_last"] = score
            c["components"]["sentiment"] = _clamp((score - 1) * 25.0)
        elif kind == "complaint":
            self._note_negative(c, "complaint", "client complaint")
            self._adjust(c, sentiment=-20.0)
            self.create_task(f"Respond to complaint from {c['client_name']} within 1 business day", 1, "high")
        elif kind == "praise":
            self._adjust(c, sentiment=+10.0)
        theme = self.ask_llm(f"Summarise this client feedback in eight words: {b.get('text', '')}")
        out.extend(self._rescore(c, f"feedback {category}"))
        out.extend(self._check_signals(c))
        out.append(self.emit("customer_success.feedback_received", {
            "client_id": c["client_id"], "client_name": c["client_name"], "kind": kind, "score": score,
            "category": category, "severity": b.get("severity", "low"), "theme": theme,
            "text": b.get("text", ""), "service_line": c["service_line"],
            "summary": f"{kind} feedback from {c['client_name']}: {category}",
        }))
        if b.get("expansion_signal") and not c["dispute"]:
            out.append(self.emit("customer_success.expansion_opportunity_identified", {
                "client_id": c["client_id"], "client_name": c["client_name"],
                "service_line": b.get("expansion_service_line", "forge"),
                "tier": b.get("expansion_tier", "forge_pilot"),
                "amount_gbp": int(b.get("expansion_amount_gbp", PRICES_GBP["forge_pilot"])),
                "rationale": str(b.get("expansion_signal")), "health_score": c["health"],
                "summary": f"Client-voiced expansion signal at {c['client_name']}",
            }))
        return out

    def _open_tickets(self) -> int:
        return sum(1 for t in self.state.setdefault("tickets", []) if t["resolved_day"] > self.clock.day)

    def _on_ticket(self, c: dict, b: dict) -> list[Message]:
        sev = b.get("severity", "medium")
        sev = sev if sev in SEVERITY_RANK else "medium"
        prio = TICKET_PRIORITY[sev]
        tier = self._keep_tier(c)
        response_h, resolve_h = SUPPORT_SLA[tier][prio]
        ticket = b.get("ticket_id") or f"TKT-{self._counter('ticket'):04d}"
        round_the_clock = tier == "keep_enterprise" and prio in ("P1", "P2")
        due_days = 0 if round_the_clock else math.ceil(response_h / 10.0)
        # measured or simulated clocks, then breach tests against the Keep tier targets (SOP-CUSTOMER_SUCCESS-03)
        load = TICKET_LOAD_BASE + TICKET_LOAD_PER_OPEN * self._open_tickets()
        actual_resp = b.get("first_response_hours")
        actual_resp = round(response_h * load, 2) if actual_resp is None else float(actual_resp)
        actual_res = b.get("resolution_hours")
        if resolve_h is not None and actual_res is None:
            actual_res = round(resolve_h * load, 2)
        actual_res = None if resolve_h is None or actual_res is None else float(actual_res)
        response_breach = actual_resp > response_h
        resolution_breach = resolve_h is not None and actual_res is not None and actual_res > resolve_h
        hours_per_day = 24.0 if round_the_clock else 10.0
        open_days = P4_OPEN_DAYS if actual_res is None else max(1, math.ceil(actual_res / hours_per_day))
        self.state.setdefault("tickets", []).append({
            "ticket_id": ticket, "client_id": c["client_id"], "priority": prio, "keep_tier": tier,
            "day": self.clock.day, "month": self.clock.date.isoformat()[:7], "first_response_hours": actual_resp,
            "resolution_hours": actual_res, "response_breach": response_breach,
            "resolution_breach": resolution_breach, "resolved_day": self.clock.day + open_days})
        self.create_task(f"{prio} ticket {ticket} for {c['client_name']}: first response within {response_h}h",
                         due_days, "critical" if prio == "P1" else "high" if prio == "P2" else "medium")
        self._adjust(c, support=-SUPPORT_HIT[sev])
        breaches = int(response_breach) + int(resolution_breach)
        if breaches:
            self._adjust(c, support=-SLA_BREACH_SUPPORT_HIT * breaches)
            self.create_task(f"SLA breach on {prio} ticket {ticket} for {c['client_name']}: call the sponsor today; "
                             f"CCO review within 1 business day", 0, "high")
            self.log_event("customer_success.activity.sla_breach", ticket, client_id=c["client_id"], priority=prio,
                           keep_tier=tier, response_breach=response_breach, resolution_breach=resolution_breach,
                           first_response_hours=actual_resp, resolution_hours=actual_res)
        self.log_event("customer_success.activity.ticket_triaged", ticket, client_id=c["client_id"], priority=prio,
                       sla_response_hours=response_h, sla_resolution_hours=resolve_h, keep_tier=tier,
                       sla_breaches=breaches)
        if SEVERITY_RANK[sev] >= 3:
            self._note_negative(c, "severe_ticket", f"{prio} support ticket")
        out = self._rescore(c, f"{prio} support ticket" + (" with SLA breach" if breaches else ""))
        out.extend(self._check_signals(c))
        if SEVERITY_RANK[sev] >= 3:
            out.append(self.emit("customer_success.support_escalated", {
                "client_id": c["client_id"], "client_name": c["client_name"], "ticket_id": ticket,
                "severity": sev, "priority": prio, "keep_tier": tier, "sla_response_hours": response_h,
                "sla_resolution_hours": resolve_h, "sla_response_breach": response_breach,
                "sla_resolution_breach": resolution_breach, "summary": b.get("text", "client support escalation"),
                "engagement_id": c.get("engagement_id"),
            }))
        return out

    # churn prevention, renewals, churn ------------------------------------------------------
    def _on_dispute(self, m: Message) -> list[Message]:
        c = self._get_client(m.body)
        if c is None:
            return []
        c["dispute"] = True
        self._adjust(c, engagement=-15.0, sentiment=-25.0, commercial=-30.0)
        self.create_task(f"Hold expansion and renewal outreach for {c['client_name']}; align with legal", 1,
                         "critical")
        self.log_event("customer_success.activity.dispute_noted", c["client_name"], client_id=c["client_id"],
                       severity=m.body.get("severity"))
        out = self._rescore(c, "legal dispute raised")
        out.extend(self._flag_risk(c, "high", "legal dispute raised"))
        return out

    def _on_termination_notice(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b)
        if c is None:
            self.log_event("customer_success.activity.unmatched", "termination without client", message_id=m.id)
            return []
        reason = b.get("reason", "unspecified")
        notice = int(b.get("notice_period_days", 30))
        c["pre_notice_health"] = c["health"]
        c["termination_reason"] = reason
        self._adjust(c, sentiment=-40.0, engagement=-20.0)
        self.create_task(f"Executive save call with {c['client_name']} sponsor (reason: {reason})", 2, "critical")
        self.create_task(f"Prepare churn post-mortem file for {c['client_name']}", 10, "medium")
        self.log_event("customer_success.activity.termination_notice", c["client_name"], client_id=c["client_id"],
                       reason=reason, notice_period_days=notice)
        out = self._rescore(c, f"termination notice ({reason})")
        out.extend(self._flag_risk(c, "critical", f"termination notice ({reason})"))
        self._schedule("save_deadline", max(1, min(notice // 2, 14)),
                       {"client_id": c["client_id"], "reason": reason, "notice_period_days": notice})
        return out

    def _on_save_deadline(self, payload: dict) -> list[Message]:
        c = self._get_client(payload)
        if c is None or c["status"] == "churned":
            return []
        reason = payload.get("reason", "unspecified")
        pre = c["pre_notice_health"] if c["pre_notice_health"] is not None else c["health"]
        saved = reason in SAVEABLE_REASONS and pre >= 55.0 and not c["dispute"]
        if saved:
            c["components"]["sentiment"] = max(c["components"]["sentiment"], 60.0)
            c["components"]["engagement"] = max(c["components"]["engagement"], 70.0)
            c["risk_open"], c["risk_severity"], c["pre_notice_health"] = False, None, None
            self._touch(c)
            self.log_event("customer_success.activity.save_succeeded", c["client_name"], client_id=c["client_id"],
                           reason=reason)
            return self._rescore(c, "termination withdrawn after save plan", force=True)
        return self._churn(c, reason, "termination")

    def _on_renewal_proposal(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b)
        if c is None or not c["keep"]:
            self.log_event("customer_success.activity.unmatched", "renewal proposal without Keep contract",
                           message_id=m.id)
            return []
        c["keep"]["renewal_proposed"] = True
        c["keep"]["proposed_amount_gbp"] = int(b.get("amount_gbp") or c["annual_value_gbp"])
        self._touch(c)
        out: list[Message] = []
        if c["band"] == "red" or c["dispute"]:
            out.extend(self._flag_risk(c, "high", "renewal proposal issued to at-risk client"))
        self._schedule("renewal_decision", CLIENT_DECISION_WINDOW_DAYS,
                       {"client_id": c["client_id"], "contract_id": c["keep"]["contract_id"],
                        "client_decision": b.get("client_decision")})
        self.log_event("customer_success.activity.renewal_proposal_noted", c["client_name"],
                       client_id=c["client_id"], amount_gbp=c["keep"]["proposed_amount_gbp"])
        return out

    def _on_renewal_decision(self, payload: dict) -> list[Message]:
        c = self._get_client(payload)
        if c is None or not c["keep"] or c["status"] == "churned":
            return []
        decision = payload.get("client_decision")
        if decision is None:
            decision = "churn" if (c["band"] == "red" or c["dispute"]) else "renew"
        if decision == "churn":
            return self._churn(c, "non-renewal", "non_renewal")
        keep = c["keep"]
        previous = c["annual_value_gbp"]
        new_amount = int(keep.get("proposed_amount_gbp") or previous)
        keep["term_end_day"] += 365
        keep["renewal_notified"], keep["renewal_proposed"] = False, False
        c["annual_value_gbp"] = new_amount
        self._touch(c)
        self.create_task(f"Renewal onboarding and updated QBR calendar for {c['client_name']}", 10, "medium")
        return [self.emit("customer_success.renewal_confirmed", {
            "client_id": c["client_id"], "client_name": c["client_name"], "contract_id": keep["contract_id"],
            "service_line": "keep", "tier": keep["tier"], "amount_gbp": new_amount,
            "previous_amount_gbp": previous, "nrr_delta_gbp": new_amount - previous, "term_months": 12,
            "new_term_end_day": keep["term_end_day"], "summary": f"{c['client_name']} renewed Keep for 12 months",
        })]

    def _churn(self, c: dict, reason: str, churn_type: str) -> list[Message]:
        c["status"], c["risk_open"] = "churned", False
        due = self.clock.day + POST_MORTEM_DAYS
        self.create_task(f"Churn post-mortem for {c['client_name']} ({c['client_id']}) by day {due}",
                         POST_MORTEM_DAYS, "high")
        self.log_event("customer_success.activity.client_lost", c["client_name"], client_id=c["client_id"],
                       reason=reason, churn_type=churn_type)
        return [self.emit("customer_success.client_churned", {
            "client_id": c["client_id"], "client_name": c["client_name"], "amount_gbp": c["annual_value_gbp"],
            "reason": reason, "churn_type": churn_type, "service_line": c["service_line"], "tier": c["tier"],
            "health_at_churn": c["health"], "last_nps": c["nps_last"], "post_mortem_due_day": due,
            "summary": f"{c['client_name']} churned ({churn_type}): {reason}",
        })]

    # security incidents and releases ---------------------------------------------------------
    def _affected(self, body: dict) -> list[dict]:
        found = []
        for cid in sorted(set(body.get("affected_client_ids", []) or [])):
            c = self._get_client({"client_id": cid})
            if c is not None:
                found.append(c)
        return found

    def _on_incident_detected(self, m: Message) -> list[Message]:
        b = m.body
        sev = b.get("severity", "medium")
        sev = sev if sev in SEVERITY_RANK else "medium"
        out: list[Message] = []
        affected = self._affected(b)
        for c in affected:
            c["open_incidents"].append(b.get("incident_id", "INC-0000"))
            self._adjust(c, support=-SUPPORT_HIT[sev])
            self._touch(c)
            self.create_task(f"Holding statement and named-contact call for {c['client_name']} ({sev} incident)", 0,
                             "critical" if SEVERITY_RANK[sev] >= 3 else "high")
            out.extend(self._rescore(c, f"security incident {b.get('incident_id', '')} ({sev})"))
        if not affected and sev == "critical":
            for cid in sorted(self.clients):
                c = self.clients[cid]
                if c["keep"] and c["keep"]["tier"] == "keep_enterprise" and c["status"] != "churned":
                    self.create_task(f"Proactive incident briefing for Enterprise client {c['client_name']}", 0,
                                     "critical")
        self.log_event("customer_success.activity.incident_noted", b.get("incident_id", ""), severity=sev,
                       affected=[c["client_id"] for c in affected])
        return out

    def _on_breach_confirmed(self, m: Message) -> list[Message]:
        b = m.body
        out: list[Message] = []
        for c in self._affected(b):
            self._adjust(c, support=-40.0, sentiment=-30.0, engagement=-10.0)
            self.create_task(f"Executive call and data-protection support pack for {c['client_name']}", 0,
                             "critical")
            out.extend(self._rescore(c, "confirmed data breach affecting client"))
            out.extend(self._flag_risk(c, "critical", "confirmed data breach affecting client"))
        self.log_event("customer_success.activity.breach_noted", b.get("incident_id", ""),
                       affected=sorted(set(b.get("affected_client_ids", []) or [])))
        return out

    def _on_incident_resolved(self, m: Message) -> list[Message]:
        b = m.body
        out: list[Message] = []
        iid = b.get("incident_id", "INC-0000")
        for c in self._affected(b):
            if iid in c["open_incidents"]:
                c["open_incidents"].remove(iid)
            self._adjust(c, support=+20.0)
            self.create_task(f"Post-incident review and written RCA for {c['client_name']} ({iid})", 5, "high")
            out.extend(self._rescore(c, f"incident {iid} resolved"))
        self.log_event("customer_success.activity.incident_resolved_noted", iid)
        return out

    def _on_release_shipped(self, m: Message) -> list[Message]:
        b = m.body
        breaking = bool(b.get("breaking_change", False))
        keep_clients = [cid for cid in sorted(self.clients)
                        if self.clients[cid]["keep"] and self.clients[cid]["status"] != "churned"]
        if breaking:
            for cid in keep_clients:
                c = self.clients[cid]
                self.create_task(f"Change notice and change window for {c['client_name']} (release "
                                 f"{b.get('release_id', '')})", 5, "high")
        else:
            self.create_task(f"Add release {b.get('release_id', '')} to next QBR packs and client bulletin", 14,
                             "low")
        self.log_event("customer_success.activity.release_noted", b.get("release_id", ""), breaking_change=breaking,
                       keep_clients=len(keep_clients))
        return []

    # marketing references --------------------------------------------------------------------
    def _eligible_reference(self, c: dict) -> bool:
        return (c["band"] == "green" and not c["dispute"] and c["status"] != "churned"
                and (c["nps_last"] or 0) >= 9 and (c["engagement_completed"] or c["keep"] is not None))

    def _on_case_study_requested(self, m: Message) -> list[Message]:
        b = m.body
        c = self._get_client(b) if b.get("client_id") or b.get("client_name") else None
        if c is None:
            candidates = [self.clients[k] for k in sorted(self.clients) if self._eligible_reference(self.clients[k])]
            candidates.sort(key=lambda x: (-x["health"], x["client_id"]))
            c = candidates[0] if candidates else None
        if c is None or not self._eligible_reference(c):
            self.log_event("customer_success.activity.case_study_declined", m.id, request_id=b.get("request_id"),
                           reason="no eligible client (needs green band, NPS>=9, no dispute)")
            return []
        consent = bool(b.get("client_consent", c["case_study_consent"]))
        if not consent:
            self.create_task(f"Ask {c['client_name']} sponsor for case-study consent and legal sign-off", 5, "medium")
            self.log_event("customer_success.activity.case_study_consent_pending", c["client_name"],
                           client_id=c["client_id"])
            return []
        c["case_study_consent"] = True
        return [self.emit("customer_success.case_study_approved", {
            "client_id": c["client_id"], "client_name": c["client_name"], "request_id": b.get("request_id"),
            "usage_scope": "named", "approved_by": "Chief Customer Officer", "health_score": c["health"],
            "service_line": c["service_line"], "tier": c["tier"],
            "summary": f"Client {c['client_name']} approved as a named case study",
        })]

    # governance and planning -----------------------------------------------------------------
    def _fiscal_year(self, body: dict) -> int:
        if body.get("fiscal_year"):
            return int(body["fiscal_year"])
        budget_id = str(body.get("budget_id", ""))
        if budget_id.startswith("BUD-") and budget_id[4:].isdigit():
            return int(budget_id[4:])
        return self.clock.date.year + (1 if self.clock.date.month >= 10 else 0)

    def _on_budget_cycle(self, m: Message) -> list[Message]:
        fy = self._fiscal_year(m.body)
        key = min(max(fy, 2026), 2028)
        people, other = BUDGET_GBP[key]
        humans, agents = HEADCOUNT[key]
        budget_id = m.body.get("budget_id", f"BUD-{fy}")
        if budget_id in self.state.setdefault("budgets_submitted", []):
            return []
        self.state["budgets_submitted"].append(budget_id)
        return [self.emit("customer_success.budget_submitted", {
            "budget_id": budget_id, "department": "customer_success", "fiscal_year": fy,
            "people_gbp": people, "non_people_gbp": other, "amount_gbp": people + other,
            "headcount_humans": humans, "headcount_agents": agents, "cost_of_revenue": True,
            "summary": f"customer_success budget {budget_id}: {people + other} GBP",
        })]

    def _on_budget_approved(self, m: Message) -> list[Message]:
        self.state["approved_budget"] = {"budget_id": m.body.get("budget_id"),
                                         "amount_gbp": m.body.get("amount_gbp")}
        self.log_event("customer_success.activity.budget_approved_noted", str(m.body.get("budget_id", "")))
        return []

    def _on_okrs_set(self, m: Message) -> list[Message]:
        self.state["okrs"] = m.body.get("okrs", m.body)
        self.create_task("Map company OKRs to customer_success KPIs and update targets", 10, "medium")
        self.log_event("customer_success.activity.okrs_noted", "okrs received")
        return []

    def _on_strategy_updated(self, m: Message) -> list[Message]:
        self.state["strategy_note"] = m.body.get("summary", "")
        self.create_task("Review health model weights and playbooks against updated strategy", 14, "low")
        self.log_event("customer_success.activity.strategy_noted", m.body.get("summary", ""))
        return []

    def _on_crisis(self, m: Message) -> list[Message]:
        self.state["crisis_mode"] = True
        count = 0
        for cid in sorted(self.clients):
            c = self.clients[cid]
            if c["status"] != "churned" and (c["band"] != "green" or (c["keep"] and c["keep"]["tier"] ==
                                                                       "keep_enterprise")):
                self.create_task(f"Crisis outreach to {c['client_name']} sponsor", 1, "critical")
                count += 1
        self.log_event("customer_success.activity.crisis_mode", m.body.get("summary", "crisis declared"),
                       outreach_tasks=count)
        return []

    # scheduled behaviour -------------------------------------------------------------------
    def _weekly_review(self) -> list[Message]:
        out: list[Message] = []
        for cid in sorted(self.clients):
            c = self.clients[cid]
            if c["status"] == "churned":
                continue
            if self.clock.day - c["last_touch_day"] > 45:
                self._adjust(c, engagement=-3.0)
                out.extend(self._rescore(c, "no sponsor contact for over 45 days"))
        out.extend(self._capacity_check())
        self.log_event("customer_success.activity.weekly_health_review", f"day {self.clock.day}",
                       clients=len(self.clients))
        return out

    def _schedule_qbrs(self) -> None:
        quarter = f"{self.clock.date.year}-Q{self.clock.quarter}"
        for cid in sorted(self.clients):
            c = self.clients[cid]
            if c["keep"] and c["status"] != "churned" and quarter not in c["qbr_quarters"]:
                c["qbr_quarters"].append(quarter)
                self.create_task(f"QBR {quarter} for {c['client_name']} ({c['keep']['tier']})", 21, "medium")

    # onboarding handover and Keep attach watches ----------------------------------------------
    def _complete_handover(self, c: dict) -> None:
        """The handover pack is issued at delivery kickoff; the clock runs from contract signature."""
        if not c["handover_pending"] or c["contract_signed_day"] is None:
            return
        days = self.clock.day - c["contract_signed_day"]
        c["handover_pending"], c["handover_done_day"] = False, self.clock.day
        self.state.setdefault("handover_days", []).append(days)
        self.log_event("customer_success.activity.handover_completed", c["client_name"], client_id=c["client_id"],
                       handover_days=days, target_days=HANDOVER_TARGET_DAYS)
        if days > HANDOVER_TARGET_DAYS and not c["handover_flagged"]:
            self.create_task(f"Handover for {c['client_name']} took {days} days against {HANDOVER_TARGET_DAYS}: "
                             f"record the cause", 5, "medium")

    def _handover_watch(self) -> None:
        for cid in sorted(self.clients):
            c = self.clients[cid]
            if (c["handover_pending"] and not c["handover_flagged"] and c["status"] != "churned"
                    and self.clock.day - c["contract_signed_day"] > HANDOVER_TARGET_DAYS):
                c["handover_flagged"] = True
                self.create_task(f"Handover overdue for {c['client_name']}: {HANDOVER_TARGET_DAYS} days since "
                                 f"signature, agree the success plan and issue the handover pack", 1, "high")
                self.log_event("customer_success.activity.handover_overdue", c["client_name"], client_id=cid,
                               days_since_signature=self.clock.day - c["contract_signed_day"])

    def _attach_watch(self) -> None:
        """Re-offer at 90 days; at the window end an unattached Build or Scale is a policy exception (COMPANY.md §2)."""
        for key in sorted(self.state.setdefault("attach_ledger", {})):
            e = self.state["attach_ledger"][key]
            c = self.clients.get(e["client_id"])
            if e["attached"] or e["lapsed"] or c is None or c["status"] == "churned":
                continue
            age = self.clock.day - e["completed_day"]
            must_attach = e["tier"] in ("forge_build", "forge_scale")
            if age >= ATTACH_REOFFER_DAYS and not e["reoffered"]:
                e["reoffered"] = True
                self.create_task(f"Re-offer Keep (reduced Essential scope) to {c['client_name']} after "
                                 f"{e['tier']}", 5, "high" if must_attach else "medium")
                self.log_event("customer_success.activity.keep_reoffer", c["client_name"], client_id=c["client_id"],
                               tier=e["tier"], days_since_completion=age)
            if age >= ATTACH_WINDOW_DAYS:
                e["lapsed"] = True
                if must_attach:
                    self.create_task(f"Keep not attached within 12 months of {e['tier']} at {c['client_name']}: "
                                     f"policy exception for the CCO to record with the CEO (COMPANY.md §2)", 2,
                                     "critical")
                self.log_event("customer_success.activity.keep_attach_lapsed", c["client_name"],
                               client_id=c["client_id"], tier=e["tier"], policy_exception=must_attach)

    # hiring (SOP-CUSTOMER_SUCCESS-14) -----------------------------------------------------------
    def _seat_start_year(self) -> int:
        """Year the seat starts: request day plus the time to hire, rounded up to the next quarter start
        (seats start at quarter starts, blueprint.md section 5)."""
        earliest = self.clock.date_of(self.clock.day + TIME_TO_HIRE_DAYS)
        if earliest.day == 1 and earliest.month in (1, 4, 7, 10):
            return earliest.year
        return earliest.year + (1 if (earliest.month - 1) // 3 * 3 + 4 > 12 else 0)

    def _request_hire(self, role: str, count: int, trigger: str, **detail) -> Message:
        """Publish a hire request. A request that takes the role (or the department) above the year-end headcount plan
        for the year the seat would start in is marked as an escalation to the CEO (executive.headcount_approved)."""
        hires = self.state.setdefault("hires", {})
        after = hires.get(role, 0) + count
        plan_year = min(max(self._seat_start_year(), 2026), 2028)
        role_plan = ROLE_PLAN[role][plan_year]
        humans_after = 1 + sum(hires.values()) + count
        outside = after > role_plan or humans_after > HEADCOUNT[plan_year][0]
        hires[role] = after
        body = {
            "role_title": role, "level": ROLE_LEVEL[role], "count": count, "department": "customer_success",
            "trigger": trigger, "plan_year": plan_year, "planned_role_headcount": role_plan,
            "role_requested_total": after, "planned_department_humans": HEADCOUNT[plan_year][0],
            "outside_headcount_plan": outside,
            "approval_path": "people.requisition_opened then executive.headcount_approved",
            "summary": f"Request {count} {role}(s): {trigger}", **detail}
        if outside:
            body["escalated_to"] = "Chief Executive Officer"
            body["summary"] += f" (outside the FY{plan_year} headcount plan, CEO decision needed)"
            self.create_task(f"Escalate to the CEO: {role} request is outside the FY{plan_year} headcount plan "
                             f"({trigger})", 2, "critical")
            self.log_event("customer_success.activity.hire_escalated", role, count=count, plan_year=plan_year,
                           planned_role_headcount=role_plan, role_requested_total=after)
        return self.emit("customer_success.hire_requested", body)

    def _capacity_check(self) -> list[Message]:
        active = sum(1 for c in self.clients.values() if c["status"] != "churned")
        planned = 1 + self.state.setdefault("hires", {}).get(ROLE_CSM, 0)
        needed = max(1, math.ceil(active / CLIENTS_PER_NAMED_CSM))
        if needed <= planned:
            return []
        return [self._request_hire(
            ROLE_CSM, needed - planned, f"{active} active clients exceed {CLIENTS_PER_NAMED_CSM} per named CSM",
            active_clients=active, clients_per_csm_ceiling=CLIENTS_PER_NAMED_CSM)]

    def _monthly_hiring_review(self) -> list[Message]:
        """Support desk and renewals triggers, measured on the month just ended (blueprint.md section 5)."""
        prev = (self.clock.date.replace(day=1) - timedelta(days=1)).isoformat()[:7]
        reviewed = self.state.setdefault("reviewed_months", [])
        if prev in reviewed:
            return []
        reviewed.append(prev)
        out: list[Message] = []
        hires = self.state.setdefault("hires", {})
        month = [t for t in self.state.setdefault("tickets", []) if t["month"] == prev]
        live_keep = sum(1 for c in self.clients.values() if c["keep"] and c["status"] != "churned")
        streak = self.state.get("sla_months_below", 0)
        sla_pct = None
        if month:
            sla_pct = 100.0 * sum(1 for t in month if not t["response_breach"]) / len(month)
            streak = streak + 1 if sla_pct < SLA_HIRE_FLOOR_PCT else 0
        have = hires.get(ROLE_SPECIALIST, 0)
        want, reasons = have, []
        if len(month) > TICKETS_MONTH_FIRST_SPECIALIST:
            want, reasons = max(want, 1), reasons + [f"{len(month)} tickets in {prev}"]
        if live_keep > LIVE_KEEP_FIRST_SPECIALIST:
            want, reasons = max(want, 1), reasons + [f"{live_keep} live Keep clients"]
        if len(month) > TICKETS_MONTH_THIRD_SPECIALIST:
            want = max(want, 3)
        if streak >= SLA_HIRE_MONTHS:
            want, reasons, streak = max(want, have + 1), reasons + [
                f"first-response SLA below {SLA_HIRE_FLOOR_PCT:.0f}% for {SLA_HIRE_MONTHS} months"], 0
        self.state["sla_months_below"] = streak
        if want > have:
            out.append(self._request_hire(ROLE_SPECIALIST, want - have, "; ".join(reasons) or "support volume",
                                          tickets_in_month=len(month), live_keep_clients=live_keep,
                                          first_response_sla_pct=None if sla_pct is None else round(sla_pct, 1)))
        renewals = sum(1 for c in self.clients.values() if c["keep"] and c["status"] != "churned"
                       and 0 <= c["keep"]["term_end_day"] - self.clock.day <= 365)
        if renewals > RENEWALS_FOR_MANAGER and hires.get(ROLE_RENEWALS, 0) < 1:
            out.append(self._request_hire(ROLE_RENEWALS, 1, f"{renewals} Keep renewals in the next 12 months",
                                          renewals_next_12_months=renewals))
        self.log_event("customer_success.activity.monthly_hiring_review", prev, tickets=len(month),
                       live_keep=live_keep, requests=len(out))
        return out

    # reporting ------------------------------------------------------------------------------
    def kpi_snapshot(self) -> list[Kpi]:
        """KPIS with actuals measured from the state (a KPI with no data yet stays None; kpis.md section 2)."""
        actual: dict[str, float] = {}
        live = [c for c in self.clients.values() if c["status"] != "churned"]
        if live:
            actual["avg_health_score"] = round(statistics.fmean(c["health"] for c in live), 1)
            actual["green_client_share"] = round(100.0 * sum(1 for c in live if c["band"] == "green") / len(live), 1)
        tickets = self.state.get("tickets", [])
        if tickets:
            actual["support_first_response_sla"] = round(
                100.0 * sum(1 for t in tickets if not t["response_breach"]) / len(tickets), 1)
        if self.state.get("handover_days"):
            actual["onboarding_handover_days"] = float(statistics.median(self.state["handover_days"]))
        ledger = list(self.state.get("attach_ledger", {}).values())
        for kpi_id, tiers in (("keep_attach_forge_build_scale", ("forge_build", "forge_scale")),
                              ("keep_attach_compass_programme", ("compass_programme",))):
            rows = [e for e in ledger if e["tier"] in tiers]
            if rows:
                actual[kpi_id] = round(100.0 * sum(1 for e in rows if e["attached"]) / len(rows), 1)
        return [replace(k, actual=actual.get(k.name)) for k in KPIS]


def build_agent(llm, bus, clock, log) -> CustomerSuccessAgent:
    """Construct the department agent (does not register with the bus or publish)."""
    # COMPANY.md §9.2 head, §6.2 head band
    role = Role("Chief Customer Officer", "customer_success", "head", (1, 1, 1), (140000, 200000),
                "Chief Executive Officer")
    return CustomerSuccessAgent("customer_success", "customer_success", role, llm, bus, clock, log)
