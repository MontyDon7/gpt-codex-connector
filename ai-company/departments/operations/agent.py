"""Operations department agent for Lumenhall Partners (COO office: procurement, vendors, workspace, compliance
actions, continuity, PMO and process improvement, operations budget).

Implements the SOPs in ``sops.md``. Every threshold below is a named constant with the value (and name) defined
once in the "Constants" section of ``sops.md``. Agents prepare, release low-value orders and propose; humans approve
anything above GBP 2,500 and attest every compliance closure (COMPANY.md 9.3 and 9.4). Human steps that the
simulation cannot see (approvals, attestations, asset returns) are modelled deterministically from the agent's own
state inside ``tick`` and never through internal topics. Deterministic: no wall clock, no randomness.
"""

from __future__ import annotations

import math
import re
from dataclasses import replace
from datetime import date, timedelta
from typing import Any, Optional

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# --------------------------------------------------------------------------------------------------------------
# Constants (sops.md "Constants"; names and values are identical)
# --------------------------------------------------------------------------------------------------------------
THREE_QUOTE_THRESHOLD_GBP = 2_500
FORMAL_TENDER_THRESHOLD_GBP = 25_000
VENDOR_REVIEW_MIN_ANNUAL_GBP = 10_000
AGENT_PO_LIMIT_GBP = 2_500
AGENT_APPROVAL_CEILING_GBP = 10_000          # COMPANY.md 9.4
PO_LEVEL_2_LIMIT_GBP = 10_000
PO_LEVEL_3_LIMIT_GBP = 50_000
PO_CFO_LIMIT_GBP = 250_000                   # COMPANY.md 9.3
NON_BUDGETED_CFO_THRESHOLD_GBP = 50_000      # COMPANY.md 9.3
EMERGENCY_ORDER_LIMIT_GBP = 10_000
QUOTE_VALIDITY_DAYS = 30
RFQ_RESPONSE_DAYS = 7
RFQ_EXCEPTION_DAYS = 10                      # business days
MAX_COMMITMENT_TERM_MONTHS = 36
SPLIT_ORDER_WINDOW_DAYS = 30
BUDGET_WARNING_PCT = 80
# approval SLA in sim days by ladder level 1..5 (0 / 2 / 3 / 5 / 7)
APPROVAL_SLA_DAYS = {1: 0, 2: 2, 3: 3, 4: 5, 5: 7}
QUOTE_WEIGHTS = {"price": 40, "fit": 30, "risk": 20, "terms": 10}

COMPLIANCE_SLA_CRITICAL = 7                  # sim days (5 business days)
COMPLIANCE_SLA_HIGH = 14                     # 10 business days
COMPLIANCE_SLA_MEDIUM = 28                   # 20 business days
COMPLIANCE_SLA_LOW = 56                      # 40 business days
COMPLIANCE_SLA_DAYS = {"critical": COMPLIANCE_SLA_CRITICAL, "high": COMPLIANCE_SLA_HIGH,
                       "medium": COMPLIANCE_SLA_MEDIUM, "low": COMPLIANCE_SLA_LOW}
COMPLIANCE_ESCALATION_DAYS = 7
POLICY_ALIGNMENT_DAYS = 14                   # 10 business days
WORKSPACE_KIT_LEAD_TIME_DAYS = 2
STOCK_BUFFER_PCT = 10
DESK_OCCUPANCY_WARNING_PCT = 90
ASSET_RECOVERY_DAYS = 7                      # 5 business days
RTO_TIER1_HOURS = 4
RTO_TIER2_HOURS = 24
RPO_TIER1_HOURS = 1
RPO_TIER2_HOURS = 24
PROCESS_PROPOSAL_MIN_SAVING_GBP = 10_000
PROCESS_MAX_PAYBACK_MONTHS = 12
NOTIONAL_HOURLY_COST_GBP = 45
CRITICAL_VENDOR_ANNUAL_GBP = 50_000
RENEWAL_DIARY_CRITICAL_DAYS = 90
RENEWAL_DIARY_OTHER_DAYS = 60
OPS_BUDGET_SUBMISSION_DAY = 21

# SOP-level values that are not in the constants table but are stated in the SOP text
VENDOR_APPROVAL_BDAYS = 2                    # SOP-03: approved within 2 business days of a passed assessment
VENDOR_REVIEW_BDAYS = {1: 10, 2: 5, 3: 2}    # SOP-03 step 1: due day by tier (plus the approval days)
PAYMENT_TERMS_DAYS = 30                      # SOP-03 control
LESSONS_LEARNED_BDAYS = 5                    # SOP-10: after resolution
LESSONS_LEARNED_CRISIS_BDAYS = 10            # SOP-10: after a crisis declaration
REWORK_HOURS = {"low": 4, "medium": 12, "high": 40, "critical": 80}   # SOP-12 step 2
DQ_WINDOW_DAYS = 90                          # SOP-12 step 1
OCCURRENCES_PER_WINDOW_ANNUALISED = 4        # four 90-day windows a year

# Modelled assumptions (economics.md): kit prices, opening stock, desk capacity
KIT_PRICE_GBP = {"laptop": 1_650, "desk_kit": 420}
OPENING_STOCK = {"laptop": 6, "desk_kit": 6}
PLANNED_STARTERS = {1: 42, 2: 81, 3: 139}    # COMPANY.md 6.1 / people economics (gross hires)
DESK_CAPACITY = {"London": 40, "New York": 12}
REPLACEMENT_PRICE_GBP = {"door access": 950, "printer": 1_200, "meeting": 1_800, "default": 1_250}
ENGAGEMENT_KIT_GBP_PER_FTE = 350
ESTIMATED_IMPLEMENTATION_GBP = {"low": 1_500, "medium": 3_000, "high": 6_000, "critical": 9_000}

# COMPANY.md 5.4 operations envelope and 6.1 plan: (FY2026, FY2027, FY2028)
BUDGET_PEOPLE_GBP = (197_800, 400_000, 751_400)      # economics.md section 2 build-up (base x 1.28)
BUDGET_NON_PEOPLE_GBP = (100_000, 300_000, 900_000)
HEADCOUNT_PLAN = (2, 6, 12)
AGENT_PLAN = (1, 4, 8)
FIRST_FISCAL_YEAR = 2026

# Role titles (blueprint.md section 3) and the date each seat is filled (COO covers an unfilled seat)
COO = "Chief Operating Officer"
CFO = "Chief Financial Officer"
CEO = "Chief Executive Officer"
PWS = "Procurement and Workspace Specialist"
OPS_MANAGER = "Operations Manager"
COMPLIANCE_SPECIALIST = "Compliance and Risk Specialist"
WF_ASSOCIATE = "Workspace and Facilities Associate"
OPS_ANALYST = "Operations Analyst"
VENDOR_SPECIALIST = "Vendor Management Specialist"
PMO_LEAD = "PMO Lead"
PMO_ANALYST = "PMO Analyst"
ROLE_TITLES = (COO, OPS_MANAGER, PWS, COMPLIANCE_SPECIALIST, WF_ASSOCIATE, OPS_ANALYST, VENDOR_SPECIALIST,
               PMO_LEAD, PMO_ANALYST)
ROLE_START = {PWS: date(2026, 10, 1), COMPLIANCE_SPECIALIST: date(2027, 4, 1), OPS_MANAGER: date(2027, 7, 1),
              WF_ASSOCIATE: date(2027, 10, 1), OPS_ANALYST: date(2027, 10, 1),
              VENDOR_SPECIALIST: date(2028, 7, 1), PMO_LEAD: date(2028, 7, 1), PMO_ANALYST: date(2028, 10, 1)}
ROLE_COVER = {PWS: COO, COMPLIANCE_SPECIALIST: COO, OPS_MANAGER: COO, WF_ASSOCIATE: PWS, OPS_ANALYST: OPS_MANAGER,
              VENDOR_SPECIALIST: PWS, PMO_LEAD: OPS_MANAGER, PMO_ANALYST: PMO_LEAD}
ROLE_LEVEL_BAND = {  # title -> (level key, salary band GBP), COMPANY.md 6.2
    OPS_MANAGER: ("manager", (92_000, 115_000)), PWS: ("consultant", (55_000, 70_000)),
    COMPLIANCE_SPECIALIST: ("consultant", (55_000, 70_000)), WF_ASSOCIATE: ("analyst", (38_000, 48_000)),
    OPS_ANALYST: ("analyst", (38_000, 48_000)), VENDOR_SPECIALIST: ("consultant", (55_000, 70_000)),
    PMO_LEAD: ("manager", (92_000, 115_000)), PMO_ANALYST: ("analyst", (38_000, 48_000)),
}
# (role, start year, start quarter); the requisition is raised in the previous quarter (45-day time-to-hire)
HIRING_PLAN = (
    (PWS, 2026, 4), (COMPLIANCE_SPECIALIST, 2027, 2), (OPS_MANAGER, 2027, 3), (WF_ASSOCIATE, 2027, 4),
    (OPS_ANALYST, 2027, 4), (COMPLIANCE_SPECIALIST, 2028, 3), (WF_ASSOCIATE, 2028, 3), (VENDOR_SPECIALIST, 2028, 3),
    (PMO_LEAD, 2028, 3), (OPS_ANALYST, 2028, 4), (PMO_ANALYST, 2028, 4),
)

# Registered vendors that exist before the simulation (framework suppliers); announced to Finance on first use
SEED_VENDORS = {
    "VN-0001": ("Hartwell Workplace Supplies", "workspace_equipment"),
    "VN-0002": ("Chalk Lane Devices", "it_hardware"),
    "VN-0003": ("Quayside Event Venues", "events"),
    "VN-0004": ("Brightmoor Print and Courier", "engagement_logistics"),
}

# Continuity test programme (SOP-10): (month, day, test_type, scenario) per calendar (= fiscal) year
TEST_PROGRAMME = {
    2026: ((5, 19, "tabletop", "Cyber incident with loss of the engagement workspace"),
           (11, 17, "tabletop", "Loss of the London HQ and a critical supplier")),
    2027: ((3, 16, "tabletop", "Ransomware with loss of the engagement workspace"),
           (5, 18, "technical", "Tier-1 failover: email, ledger, engagement workspace, identity"),
           (9, 14, "tabletop", "Loss of the London HQ and New York office connectivity"),
           (11, 16, "technical", "Tier-1 restore from backup with point-in-time recovery")),
    2028: ((2, 15, "tabletop", "Ransomware with loss of the engagement workspace"),
           (4, 18, "technical", "Tier-1 failover: email, ledger, engagement workspace, identity"),
           (7, 11, "vendor_failure", "Failure of the primary cloud AI platform vendor"),
           (9, 12, "tabletop", "Loss of both offices and a critical supplier"),
           (10, 17, "technical", "Tier-1 restore from backup with point-in-time recovery"),
           (11, 14, "vendor_failure", "Insolvency of the identity provider")),
}
CRISIS_REVIEW_FALLBACK_DAYS = 30             # modelled: crisis logistics stand down / test filed if no resolution
TECHNICAL_RTO_HOURS = (3.2, 4.6, 2.9, 3.8, 3.4, 4.2)   # modelled results of successive technical exercises

SEVERITIES = ("low", "medium", "high", "critical")

# FY2026 targets (kpis.md): ids, units, targets and directions are defined there
KPIS: list[Kpi] = [
    Kpi("workspace_ready_on_time_pct", "percent", 95.0, None, True),
    Kpi("asset_recovery_pct", "percent", 90.0, None, True),
    Kpi("vendor_review_cycle_days", "days", 10.0, None, False),
    Kpi("three_quote_compliance_pct", "percent", 98.0, None, True),
    Kpi("po_coverage_pct", "percent", 90.0, None, True),
    Kpi("procurement_cycle_days", "days", 7.0, None, False),
    Kpi("procurement_savings_pct", "percent", 5.0, None, True),
    Kpi("compliance_actions_on_time_pct", "percent", 90.0, None, True),
    Kpi("overdue_compliance_actions", "count", 2.0, None, False),
    Kpi("continuity_tests_completed", "count", 2.0, None, True),
    Kpi("continuity_rto_met_pct", "percent", 80.0, None, True),
    Kpi("process_improvements_adopted", "count", 6.0, None, True),
    Kpi("process_savings_gbp", "GBP", 60000.0, None, True),
    Kpi("programme_on_time_pct", "percent", 80.0, None, True),
    Kpi("budget_variance_pct", "percent", 5.0, None, False),
    Kpi("vendor_approved_before_order_pct", "percent", 100.0, None, True),
]


# --------------------------------------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------------------------------------
def _num(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    return int(_num(value, default))


def _s(value: Any, default: str = "") -> str:
    return default if value is None else str(value)


def _first(body: dict, *keys: str, default: Any = None) -> Any:
    for key in keys:
        if body.get(key) not in (None, ""):
            return body[key]
    return default


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "y")
    return bool(value)


def _list(value: Any) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, dict):
        return list(value)
    return [value]


def _sev(value: Any, default: str = "medium") -> str:
    v = _s(value, default).lower()
    v = {"info": "low", "minor": "low", "major": "high", "severe": "critical"}.get(v, v)
    return v if v in SEVERITIES else default


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    return float(ordered[mid]) if n % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0


def _level_for(value: float) -> int:
    """Approval ladder level for a committed value (sops.md approval ladder)."""
    if value < THREE_QUOTE_THRESHOLD_GBP:
        return 1
    if value <= PO_LEVEL_2_LIMIT_GBP:
        return 2
    if value <= PO_LEVEL_3_LIMIT_GBP:
        return 3
    if value <= PO_CFO_LIMIT_GBP:
        return 4
    return 5


class OperationsAgent(DepartmentAgent):
    """Lumenhall operations: COO-office agent. Drafts, tracks, releases small orders and proposes; humans approve."""

    SUBSCRIBES = subscribes_for("operations")
    PUBLISHES = publishes_for("operations")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.kpis: dict[str, Kpi] = {k.name: k for k in KPIS}
        vendors = {vid: {"name": name, "category": cat, "status": "approved", "announced": False, "seed": True,
                         "flags": {}, "tier": 3, "risk_rating": "low", "held": [], "review_requested_day": None,
                         "approved_day": 0, "first_order_day": None, "in_scope": False, "reassess_day": None,
                         "reassess_requested": False, "dpa_cleared": False, "assessment": None}
                   for vid, (name, cat) in SEED_VENDORS.items()}
        self.state.update({
            "seq": {"po": 0, "rfq": 0, "ca": 0, "bct": 0, "pi": 0, "vn": len(SEED_VENDORS), "prg": 0},
            "vendors": vendors, "vendor_names": {v["name"].lower(): k for k, v in vendors.items()},
            "rfqs": {}, "orders": [], "event_rfqs": {}, "engagement_rfqs": {},
            "employees": {}, "stock": dict(OPENING_STOCK), "inbound": [], "demand": {}, "desk_seq": {}, "desks": {},
            "ready_total": 0, "ready_on_time": 0, "leavers": {}, "leaver_seq": 0,
            "actions": {}, "attest_queue": [], "policies": {}, "reports": 0,
            "incidents": {}, "tests": {}, "test_seq": {"technical": 0}, "crisis_mode": False, "crisis_day": None,
            "crisis_pending": {}, "crises": [], "vulns": {},
            "dq_log": [], "improvements": {}, "programmes": {}, "milestones_due": 0, "milestones_on_time": 0,
            "budget_cycles": {}, "approved_budget": {}, "budget_warned": {}, "hire_requests": {},
            "reviewed_quarters": [], "savings_pct_first": 0.0, "savings_pct_saved": 0.0, "review_cycles": [],
            "procurement_cycles": [], "three_quote_total": 0, "three_quote_ok": 0, "handled": 0, "unmapped": 0,
            "capacity": {}, "scorecard_months": [], "split_breaches": 0,
        })
        self._seed_programmes()
        self._handlers = self._build_handlers()

    # ------------------------------------------------------------------ dispatch
    def _build_handlers(self) -> dict:
        return {
            "external.vendor_quote_received": self._on_quote,
            "it_security.vendor_risk_assessed": self._on_vendor_risk,
            "people.new_hire_started": self._on_new_hire,
            "it_security.access_provisioned": self._on_access_provisioned,
            "people.employee_left": self._on_employee_left,
            "marketing.event_scheduled": self._on_event,
            "delivery.engagement_kickoff": self._on_kickoff,
            "delivery.staffing_requested": self._on_staffing,
            "legal.compliance_finding_raised": self._on_finding,
            "legal.regulatory_change_noted": self._on_regulatory_change,
            "legal.policy_update_published": self._on_policy_update,
            "it_security.incident_detected": self._on_incident_detected,
            "it_security.incident_resolved": self._on_incident_resolved,
            "executive.crisis_declared": self._on_crisis,
            "it_security.vulnerability_found": self._on_vulnerability,
            "data.data_quality_issue_raised": self._on_data_quality,
            "executive.okrs_set": self._on_okrs,
            "executive.strategy_updated": self._on_strategy,
            "finance.budget_cycle_opened": self._on_budget_cycle,
            "executive.budget_approved": self._on_budget_approved,
        }

    def handle(self, message: Message) -> list[Message]:
        handler = self._handlers.get(message.topic)
        self.log_event("operations.activity." + message.topic.replace(".", "_"),
                       f"{message.topic} from {message.sender}", message_id=message.id, known=handler is not None)
        if handler is None:
            self.state["unmapped"] += 1
            return []
        body = message.body if isinstance(message.body, dict) else {}
        out = handler(message, body) or []
        self.state["handled"] += 1
        self._refresh_kpis()
        return out

    # ------------------------------------------------------------------ generic helpers
    def _fy(self) -> int:
        return max(1, min(3, self.clock.year_index))

    def _next(self, key: str) -> int:
        self.state["seq"][key] += 1
        return self.state["seq"][key]

    def _bday_offset(self, n: int) -> int:
        """Calendar days from today until n business days ahead."""
        days, left = 0, n
        while left > 0:
            days += 1
            if (self.clock.date + timedelta(days=days)).weekday() < 5:
                left -= 1
        return days

    def _bdays_between(self, d0: int, d1: int) -> int:
        """Business days in (d0, d1]."""
        return sum(1 for d in range(d0 + 1, d1 + 1) if self.clock.date_of(d).weekday() < 5)

    def _holder(self, role: str) -> str:
        """The title that covers a seat today (the COO covers every unfilled seat)."""
        seen = 0
        while role != COO and seen < 5:
            if self.clock.date >= ROLE_START.get(role, date(9999, 1, 1)):
                return role
            role = ROLE_COVER.get(role, COO)
            seen += 1
        return COO

    def _task(self, title: str, due_in: Optional[int] = None, priority: str = "medium") -> str:
        return self.create_task(title, due_in, priority).id

    def _set_kpi(self, name: str, actual: float) -> None:
        self.kpis[name] = replace(self.kpis[name], actual=round(actual, 2))

    def _title(self, vendor_id: str) -> str:
        return self.state["vendors"].get(vendor_id, {}).get("name", vendor_id)

    # ================================================================== vendors (SOP-01, 03, 04)
    def _vendor_for(self, body: dict) -> str:
        """Find or create the vendor record named in a message; returns the vendor id."""
        v = self.state["vendors"]
        vid = _s(_first(body, "vendor_id"))
        name = _s(_first(body, "vendor_name", "vendor", "supplier"))
        if not vid and name:
            vid = self.state["vendor_names"].get(name.lower(), "")
        if not vid:
            vid = f"VN-{self._next('vn'):04d}"
        if vid not in v:
            v[vid] = {"name": name or vid, "category": _s(body.get("category"), "general"), "status": "new",
                      "announced": False, "seed": False, "flags": {}, "tier": 3, "risk_rating": "unrated",
                      "held": [], "review_requested_day": None, "approved_day": None, "first_order_day": None,
                      "in_scope": False, "reassess_day": None, "reassess_requested": False,
                      "dpa_cleared": False, "assessment": None}
        if name and v[vid]["name"] == vid:
            v[vid]["name"] = name
        self.state["vendor_names"][v[vid]["name"].lower()] = vid
        flags = v[vid]["flags"]
        for k in ("processes_personal_data", "system_access", "ai_platform"):
            if k in body:
                flags[k] = flags.get(k, False) or _truthy(body[k])
        if "has_dpa" in body:
            flags["has_dpa"] = _truthy(body["has_dpa"])
        if "data_outside_uk_eea" in body:
            flags["data_outside_uk_eea"] = _truthy(body["data_outside_uk_eea"])
        return vid

    def _needs_review(self, vid: str, annual: float) -> bool:
        rec = self.state["vendors"][vid]
        if rec["status"] == "approved":
            return False
        f = rec["flags"]
        return (annual >= VENDOR_REVIEW_MIN_ANNUAL_GBP or f.get("processes_personal_data", False)
                or f.get("system_access", False) or f.get("ai_platform", False))

    def _tier_hint(self, vid: str) -> int:
        f = self.state["vendors"][vid]["flags"]
        if f.get("processes_personal_data") or f.get("system_access") or f.get("ai_platform"):
            return 1
        return 3

    def _request_review(self, vid: str, reason: str, annual: float, amount: float, rfq_id: str,
                        service: str = "") -> list[Message]:
        rec = self.state["vendors"][vid]
        f = rec["flags"]
        tier = self._tier_hint(vid)
        classes = (["personal_data"] if f.get("processes_personal_data") else []) + (
            ["client_confidential"] if f.get("ai_platform") else [])
        due = self.clock.day + self._bday_offset(VENDOR_REVIEW_BDAYS[tier] + VENDOR_APPROVAL_BDAYS)
        if reason == "new_vendor":
            rec["status"], rec["in_scope"] = "in_review", True
            rec["review_requested_day"] = self.clock.day
        body = {
            "vendor_id": vid, "vendor_name": rec["name"], "vendor": rec["name"],
            "service": service or rec["category"], "data_classes": classes,
            "processes_personal_data": bool(f.get("processes_personal_data")),
            "has_dpa": bool(f.get("has_dpa", False)) if f.get("processes_personal_data") else True,
            "data_outside_uk_eea": bool(f.get("data_outside_uk_eea", False)),
            "ai_platform": bool(f.get("ai_platform")), "privileged_access": bool(f.get("system_access")),
            "annual_cost_gbp": round(annual, 2), "amount_gbp": round(amount, 2), "tier_hint": tier,
            "rfq_id": rfq_id, "review_reason": reason, "requested_by": self._holder(PWS), "due_day": due,
            "severity": "high" if tier == 1 else "medium",
            "summary": f"Vendor review for {rec['name']} ({reason}); tier hint {tier}, annual value {annual:,.0f}",
        }
        return [self.emit("operations.vendor_review_requested", body)]

    def _announce(self, vid: str) -> list[Message]:
        """Tell Finance and IT Security about a pre-registered approved vendor on first use."""
        rec = self.state["vendors"][vid]
        if rec["status"] != "approved" or rec["announced"]:
            return []
        rec["announced"] = True
        return [self._emit_approved(vid, 0, [], "approve", "pre-registered framework supplier")]

    def _emit_approved(self, vid: str, delay: int, conditions: list, decision: str, note: str) -> Message:
        rec = self.state["vendors"][vid]
        a = rec.get("assessment") or {}
        annual = _num(rec.get("annual"), 0.0)
        critical = annual >= CRITICAL_VENDOR_ANNUAL_GBP
        reassess = _int(a.get("reassess_day"), self.clock.day + 365)
        rec["reassess_day"] = reassess
        body = {
            "vendor_id": vid, "vendor_name": rec["name"], "vendor": rec["name"], "tier": rec.get("tier", 3),
            "risk_rating": rec.get("risk_rating", "low"), "decision": decision, "conditions": list(conditions),
            "approved_by": COO if critical else self._holder(PWS), "payment_terms_days": PAYMENT_TERMS_DAYS,
            "annual_cost_gbp": round(annual, 2), "amount_gbp": round(_num(rec.get("amount"), 0.0), 2),
            "reassess_day": reassess, "critical": critical,
            "summary": f"{rec['name']} approved ({decision}); {note}",
        }
        return self.emit("operations.vendor_approved", body, delay_days=delay)

    def _on_vendor_risk(self, msg: Message, body: dict) -> list[Message]:
        vid = self._vendor_for(body)
        rec = self.state["vendors"][vid]
        decision = _s(body.get("decision"), "approve").lower()
        rating = _s(_first(body, "risk_rating", "rating"), "low").lower()
        rec["assessment"] = {"decision": decision, "conditions": _list(body.get("conditions")),
                             "reassess_day": body.get("reassess_day"), "day": self.clock.day}
        rec["tier"] = _int(body.get("tier"), rec.get("tier", 3)) or 3
        rec["risk_rating"] = rating
        if rec["status"] == "approved" and rec["announced"]:
            if decision == "reject" or rating in ("high", "critical"):
                self._task(f"{vid}: reassessment rated {rating}; COO, CISO and CFO to decide (SOP-OPERATIONS-03)",
                           2, "high")
            if body.get("reassess_day") is not None:
                rec["reassess_day"], rec["reassess_requested"] = _int(body["reassess_day"]), False
            return []
        return self._decide_vendor(vid)

    def _vendor_blockers(self, vid: str) -> list[str]:
        rec = self.state["vendors"][vid]
        blockers: list[str] = []
        if any(a["status"] != "closed" and a.get("vendor_id") == vid for a in self.state["actions"].values()):
            blockers.append("open compliance finding linked to the vendor")
        f = rec["flags"]
        if f.get("processes_personal_data") and f.get("has_dpa") is False and not rec["dpa_cleared"]:
            blockers.append("no data processing agreement (UK GDPR Article 28)")
        if rec["risk_rating"] in ("high", "critical"):
            blockers.append("high risk rating needs the CFO, CISO and COO decision")
        return blockers

    def _decide_vendor(self, vid: str) -> list[Message]:
        """SOP-03 steps 3 to 7: act on IT Security's assessment."""
        rec = self.state["vendors"][vid]
        a = rec["assessment"] or {}
        decision = a.get("decision", "approve")
        out: list[Message] = []
        if decision == "reject":
            rec["status"] = "rejected"
            self._task(f"{vid} rejected after assessment: tell requester and recommend next-ranked quote", 1, "high")
            for rfq_id in list(rec["held"]):
                out += self._reject_held(rfq_id, vid)
            rec["held"] = []
            return out
        blockers = self._vendor_blockers(vid)
        if blockers:
            rec["status"] = "pending"
            self._task(f"{vid} pending: {'; '.join(blockers)}", 3, "high")
            self.log_event("operations.activity.vendor_pending", f"{vid}: {len(blockers)} blocker(s)",
                           vendor_id=vid, blockers=blockers)
            return []
        delay = self._bday_offset(1)
        rec["status"] = "approved"
        rec["announced"] = True
        rec["approved_day"] = self.clock.day + delay
        if rec["review_requested_day"] is not None:
            self.state["review_cycles"].append(self._bdays_between(rec["review_requested_day"],
                                                                  self.clock.day + delay))
        out.append(self._emit_approved(vid, delay, a.get("conditions", []),
                                       "approve_with_conditions" if a.get("conditions") else "approve",
                                       f"tier {rec['tier']}, risk {rec['risk_rating']}"))
        for rfq_id in list(rec["held"]):
            rfq = self.state["rfqs"].get(rfq_id)
            if rfq and rfq["status"] == "held":
                out += self._place_rfq(rfq, rfq["winner"], rfq["exception"], delay)
        rec["held"] = []
        return out

    def _reject_held(self, rfq_id: str, vid: str) -> list[Message]:
        rfq = self.state["rfqs"].get(rfq_id)
        if not rfq or rfq["status"] != "held":
            return []
        rfq["rejected_vendors"].append(vid)
        alternatives = [q for q in rfq["quotes"] if q["vendor_id"] not in rfq["rejected_vendors"]
                        and self.state["vendors"][q["vendor_id"]]["status"] != "rejected"]
        if rfq["alt_tried"] or not alternatives:
            rfq["status"] = "closed"
            self._task(f"{rfq_id}: no approvable supplier left; re-run sourcing", 2, "high")
            return []
        rfq["alt_tried"] = True
        rfq["status"] = "open"
        return self._decide_rfq(rfq, rfq["exception"], exclude=rfq["rejected_vendors"])

    # ================================================================== procurement (SOP-01, 02)
    def _aggregate(self, vid: str, category: str, exclude_po: str = "") -> float:
        horizon = self.clock.day - SPLIT_ORDER_WINDOW_DAYS
        return sum(o["committed"] for o in self.state["orders"] if o["vendor_id"] == vid and
                   o["category"] == category and o["day"] >= horizon and o["po_id"] != exclude_po)

    def _approval(self, value: float, budgeted: bool, department: str, exception: str,
                  emergency: bool) -> tuple[int, str]:
        """Ladder level and approver title (sops.md approval ladder and COMPANY.md 9.3)."""
        level = _level_for(value)
        if not budgeted:
            if value > PO_CFO_LIMIT_GBP:
                level = 5
            elif value > NON_BUDGETED_CFO_THRESHOLD_GBP:
                level = max(level, 4)
        if exception in ("sole_source", "fewer_than_three"):
            level = min(5, max(level + 1, 3))        # approved one level above the order value, COO minimum
        approver = {1: self._holder(PWS), 2: self._holder(OPS_MANAGER), 3: COO, 4: CFO, 5: CEO}[level]
        if level == 3 and department == "operations":
            approver = CFO                            # the COO is the requester: the CFO approves
        if emergency and value <= EMERGENCY_ORDER_LIMIT_GBP:
            approver = CFO                            # emergency order approved by the CFO on the COO's advice
        return level, approver

    def _agent_can_release(self, committed: float) -> bool:
        return committed < AGENT_PO_LIMIT_GBP and committed <= AGENT_APPROVAL_CEILING_GBP

    def _on_quote(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        amount = _num(_first(body, "amount_gbp", "price_gbp", "total_gbp"))
        if amount <= 0:
            self._task("Quote received without a value; ask the supplier to resubmit with a priced quote", 2)
            return []
        valid_until = body.get("valid_until_day")
        if valid_until is not None and _int(valid_until) < self.clock.day:
            self._task(f"Quote {_s(body.get('quote_id'), msg.id)} expired before registration; re-request it", 2)
            self.log_event("operations.activity.quote_rejected", "quote expired", quote_id=_s(body.get("quote_id")))
            return []
        term = max(1, _int(body.get("term_months"), 12))
        capped = min(term, MAX_COMMITMENT_TERM_MONTHS)
        committed = amount * capped / term
        annual = committed / (capped / 12.0)
        vid = self._vendor_for(body)
        rfq_id = _s(_first(body, "rfq_id"))
        if not rfq_id and body.get("event_id") in s["event_rfqs"]:
            rfq_id = s["event_rfqs"][body["event_id"]]
        if not rfq_id and body.get("engagement_id") in s["engagement_rfqs"]:
            rfq_id = s["engagement_rfqs"][body["engagement_id"]]
        rfq = s["rfqs"].get(rfq_id) if rfq_id else None
        if rfq is None:
            rfq = self._new_rfq(rfq_id, vid, body, committed)
        if rfq["status"] not in ("open",):
            self.log_event("operations.activity.late_quote", f"{rfq['id']} already {rfq['status']}", rfq_id=rfq["id"])
            return []
        qid = _s(body.get("quote_id"), f"Q-{msg.id}")
        if any(q["quote_id"] == qid for q in rfq["quotes"]):
            return []
        quote = {"quote_id": qid, "vendor_id": vid, "amount": amount, "committed": committed, "annual": annual,
                 "term": term, "valid_until": None if valid_until is None else _int(valid_until),
                 "day": self.clock.day, "fit": _num(body.get("fit_score"), 70.0),
                 "risk": _num(body.get("risk_score"), 70.0), "terms": _num(body.get("terms_score"), 70.0),
                 "compliant": body.get("compliant") is not False}
        rfq["quotes"].append(quote)
        if rfq["first_day"] is None:
            rfq["first_day"] = self.clock.day
        if _truthy(body.get("emergency")):
            rfq["emergency"] = True
        rec = s["vendors"][vid]
        rec["annual"], rec["amount"] = annual, committed
        short = quote["valid_until"] is not None and quote["valid_until"] - self.clock.day < QUOTE_VALIDITY_DAYS
        self.log_event("operations.activity.quote_registered", f"{qid} in {rfq['id']} ({len(rfq['quotes'])})",
                       rfq_id=rfq["id"], vendor_id=vid, committed=round(committed, 2), path=rfq["path"],
                       short_validity=short)
        if rfq["path"] == "single" or rfq["emergency"] and committed <= EMERGENCY_ORDER_LIMIT_GBP:
            return self._decide_rfq(rfq, "emergency" if rfq["emergency"] and rfq["path"] != "single" else "none")
        compliant = [q for q in rfq["quotes"] if q["compliant"]]
        if len(compliant) >= 3:
            return self._decide_rfq(rfq, "none")
        return []

    def _new_rfq(self, rfq_id: str, vid: str, body: dict, committed: float) -> dict:
        s = self.state
        rfq_id = rfq_id or f"RFQ-{self.clock.date.year}-{self._next('rfq'):04d}"
        category = _s(body.get("category"), s["vendors"][vid]["category"] or "general")
        aggregate = committed + self._aggregate(vid, category)
        path = self._path(aggregate)
        rfq = {"id": rfq_id, "path": path, "committed": committed, "aggregate": aggregate, "category": category,
               "department": _s(body.get("department"), "operations"), "budgeted": body.get("budgeted") is not False,
               "first_day": None, "quotes": [], "status": "open", "exception": "none", "emergency": False,
               "split": aggregate >= THREE_QUOTE_THRESHOLD_GBP > committed, "winner": None, "rejected_vendors": [],
               "alt_tried": False, "ref": _s(_first(body, "event_id", "engagement_id")), "service": _s(body.get("service"))}
        s["rfqs"][rfq_id] = rfq
        if rfq["split"]:
            self._task(f"{rfq_id}: split-order pattern for {self._title(vid)} ({aggregate:,.0f} in "
                       f"{SPLIT_ORDER_WINDOW_DAYS} days); COO and Finance informed, three quotes now required", 1, "high")
        return rfq

    @staticmethod
    def _path(value: float) -> str:
        if value < THREE_QUOTE_THRESHOLD_GBP:
            return "single"
        return "tender" if value >= FORMAL_TENDER_THRESHOLD_GBP else "three_quote"

    def _score(self, quotes: list[dict]) -> list[tuple[float, dict]]:
        """Weighted score: price 40, fit 30, risk 20, terms 10 (sops.md quote scoring)."""
        low = min(q["committed"] for q in quotes)
        rows = []
        for q in quotes:
            points = (QUOTE_WEIGHTS["price"] * low / q["committed"] + QUOTE_WEIGHTS["fit"] * q["fit"] / 100.0
                      + QUOTE_WEIGHTS["risk"] * q["risk"] / 100.0 + QUOTE_WEIGHTS["terms"] * q["terms"] / 100.0)
            rows.append((round(points, 2), q))
        return sorted(rows, key=lambda r: (-r[0], r[1]["committed"], r[1]["quote_id"]))

    def _decide_rfq(self, rfq: dict, exception: str, exclude: Optional[list] = None) -> list[Message]:
        usable = [q for q in rfq["quotes"] if q["compliant"] and q["vendor_id"] not in (exclude or [])
                  and self.state["vendors"][q["vendor_id"]]["status"] != "rejected"
                  and (q["valid_until"] is None or q["valid_until"] >= self.clock.day)]
        if not usable:
            rfq["status"] = "open"
            self._task(f"{rfq['id']}: no valid compliant quote left; re-request quotes", 2, "high")
            return []
        scored = self._score(usable)
        winner = scored[0][1]
        lowest = min(usable, key=lambda q: q["committed"])
        if winner is not lowest:
            self._task(f"{rfq['id']}: recommended supplier is not the lowest price; record written reasons and have "
                       "them approved at the ladder level", 2)
        first = rfq["quotes"][0]["committed"]
        rfq["winner"], rfq["exception"] = winner, exception
        rfq["scores"] = [(p, q["quote_id"]) for p, q in scored]
        rfq["savings_basis"] = (first, winner["committed"])
        vid = winner["vendor_id"]
        out: list[Message] = []
        if self._needs_review(vid, winner["annual"]) or self.state["vendors"][vid]["status"] in ("in_review", "pending"):
            rec = self.state["vendors"][vid]
            rec["annual"], rec["amount"] = winner["annual"], winner["committed"]
            if rec["status"] in ("new", "unreviewed"):
                out += self._request_review(vid, "new_vendor", winner["annual"], winner["committed"], rfq["id"],
                                            rfq["service"] or rfq["category"])
            rfq["status"] = "held"
            if rfq["id"] not in rec["held"]:
                rec["held"].append(rfq["id"])
            self.log_event("operations.activity.order_held", f"{rfq['id']} held for vendor review of {vid}",
                           rfq_id=rfq["id"], vendor_id=vid)
            return out
        return out + self._place_rfq(rfq, winner, exception, 0)

    def _place_rfq(self, rfq: dict, winner: dict, exception: str, base_delay: int) -> list[Message]:
        vid = winner["vendor_id"]
        rec = self.state["vendors"][vid]
        if rec["status"] in ("new", "unreviewed"):          # below every review trigger: register as approved
            rec["status"], rec["approved_day"] = "approved", self.clock.day
        out = self._announce(vid)
        emergency = rfq["emergency"] and winner["committed"] <= EMERGENCY_ORDER_LIMIT_GBP
        if emergency:
            exception = "emergency"
        value = max(winner["committed"], rfq["aggregate"]) if rfq["split"] else winner["committed"]
        level, approver = self._approval(value, rfq["budgeted"], rfq["department"], exception, emergency)
        sla = 0 if (emergency or rfq["emergency"]) else APPROVAL_SLA_DAYS[level]
        agent_release = (level == 1 and exception == "none" and rfq["budgeted"] and not rfq["split"]
                         and rec["status"] == "approved" and self._agent_can_release(winner["committed"]))
        rfq["status"] = "ordered"
        if winner["valid_until"] is not None and winner["valid_until"] < self.clock.day + base_delay + sla:
            self._task(f"{rfq['id']}: quote validity ends before the PO date; re-confirm the price (min "
                       f"{QUOTE_VALIDITY_DAYS} days validity from receipt)", 1, "high")
        out.append(self._emit_po(
            vid, rfq["department"], rfq["category"], winner["committed"], winner["term"], rfq["budgeted"], rfq["id"],
            len([q for q in rfq["quotes"] if q["compliant"]]), exception, level, approver, base_delay + sla,
            rfq["split"], "agent" if agent_release else "human_approver",
            f"{rfq['path'].replace('_', ' ')} order for {rec['name']}", competed=rfq["path"] != "single",
            first_quote_day=rfq["first_day"]))
        first, final = rfq["savings_basis"]
        if rfq["path"] != "single" and exception == "none" and first > 0:
            self.state["savings_pct_first"] += first
            self.state["savings_pct_saved"] += max(0.0, first - final)
        return out

    def _emit_po(self, vid: str, department: str, category: str, committed: float, term: int, budgeted: bool,
                 rfq_id: str, quotes: int, exception: str, level: int, approver: str, delay: int, split: bool,
                 released_by: str, summary: str, competed: bool = False, first_quote_day: Optional[int] = None,
                 framework: bool = False) -> Message:
        s = self.state
        rec = s["vendors"][vid]
        po_id = f"PO-{self.clock.date.year}-{self._next('po'):04d}"
        capped = min(max(1, term), MAX_COMMITMENT_TERM_MONTHS)
        annual = committed / (capped / 12.0)
        placed = self.clock.day + delay
        if rec["first_order_day"] is None:
            rec["first_order_day"] = placed
        severity = "high" if level >= 4 or exception != "none" else ("medium" if level >= 2 else "low")
        body = {
            "po_id": po_id, "rfq_id": rfq_id, "vendor_id": vid, "vendor": rec["name"], "vendor_name": rec["name"],
            "department": department, "category": category, "amount_gbp": round(committed, 2),
            "annual_cost_gbp": round(annual, 2), "term_months": capped, "budgeted": budgeted,
            "quotes_received": quotes, "exception": exception, "approval_level": level, "approver_title": approver,
            "released_by": released_by, "split_flag": split, "severity": severity, "due_day": placed + 30,
            "summary": f"{po_id} {summary}: {committed:,.0f} over {capped} months, level {level} approved by {approver}",
        }
        msg = self.emit("operations.procurement_order_placed", body, recipient="finance", delay_days=delay)
        s["orders"].append({"po_id": po_id, "vendor_id": vid, "category": category, "committed": committed,
                            "day": self.clock.day, "placed_day": placed, "department": department,
                            "annual": annual, "exception": exception, "level": level})
        if committed >= THREE_QUOTE_THRESHOLD_GBP:
            s["three_quote_total"] += 1
            if framework or quotes >= 3 or exception in ("sole_source", "fewer_than_three", "emergency"):
                s["three_quote_ok"] += 1
            if first_quote_day is not None and exception != "emergency":
                s["procurement_cycles"].append(self._bdays_between(first_quote_day, placed))
        if split:
            s["split_breaches"] += 1
        self._budget_usage(department, annual)
        return msg

    def _budget_usage(self, department: str, annual: float) -> None:
        """SOP-02 step 6: warn at BUDGET_WARNING_PCT of the operations non-people line."""
        if department != "operations":
            return
        fy = self.clock.date.year
        approved = self.state["approved_budget"].get(fy)
        if not approved:
            return
        year_orders = sum(o["annual"] for o in self.state["orders"] if o["department"] == "operations")
        line = approved["non_people_gbp"]
        pct = 100.0 * year_orders / line if line else 0.0
        if pct >= BUDGET_WARNING_PCT and not self.state["budget_warned"].get(fy):
            self.state["budget_warned"][fy] = True
            self._task(f"Operations non-people budget FY{fy} at {pct:.0f}% (warning at {BUDGET_WARNING_PCT}%): "
                       "inform Finance and the budget holder", 2, "high")

    def _simple_order(self, vid: str, department: str, category: str, amount: float, summary: str,
                      framework: bool = True, delay_extra: int = 0, term: int = 12) -> list[Message]:
        """Catalogue or framework call-off: single quote below the limit, framework price otherwise."""
        rec = self.state["vendors"][vid]
        out = self._announce(vid)
        split = False
        if not framework:
            agg = amount + self._aggregate(vid, category)
            split = agg >= THREE_QUOTE_THRESHOLD_GBP > amount
            if split:
                self._task(f"Split-order check: {rec['name']} orders total {agg:,.0f} in {SPLIT_ORDER_WINDOW_DAYS} days; "
                           "report to COO and Finance", 1, "high")
        level, approver = self._approval(amount, True, department, "none", False)
        sla = APPROVAL_SLA_DAYS[level]
        release = "agent" if (level == 1 and not split and self._agent_can_release(amount)) else "human_approver"
        if release != "agent" and level > 1:
            self._task(f"Approve {summary} ({amount:,.0f}) as {approver} within {sla} days", sla or 1)
        quotes = 3 if (framework and amount >= THREE_QUOTE_THRESHOLD_GBP) else 1
        out.append(self._emit_po(vid, department, category, amount, term, True, "", quotes, "none", level, approver,
                                 sla + delay_extra, split, release,
                                 summary + (" (call-off under the framework competed with three quotes)"
                                            if quotes == 3 else ""), framework=framework))
        return out

    # ------------------------------------------------------------------ logistics orders (SOP-07)
    def _open_logistics(self, kind: str, ref: str, estimated: float, department: str, category: str,
                        service: str, needs: list) -> list[Message]:
        """Event or engagement purchase: order below the threshold, otherwise open an RFQ."""
        s = self.state
        reg = s["event_rfqs"] if kind == "event" else s["engagement_rfqs"]
        if ref in reg:
            return []
        if estimated < THREE_QUOTE_THRESHOLD_GBP:
            reg[ref] = "ordered"
            return self._simple_order("VN-0003" if kind == "event" else "VN-0004", department, category, estimated,
                                      f"{kind} {ref} {service}", framework=False)
        rfq_id = f"RFQ-{self.clock.date.year}-{self._next('rfq'):04d}"
        reg[ref] = rfq_id
        s["rfqs"][rfq_id] = {
            "id": rfq_id, "path": self._path(estimated), "committed": estimated, "aggregate": estimated,
            "category": category, "department": department, "budgeted": True, "first_day": None, "quotes": [],
            "status": "open", "exception": "none", "emergency": False, "split": False, "winner": None,
            "rejected_vendors": [], "alt_tried": False, "ref": ref, "service": service,
            "issued_day": self.clock.day, "needs": needs}
        self._task(f"Issue RFQ {rfq_id} for {kind} {ref} within 2 business days ({', '.join(map(str, needs))}); "
                   f"three quotes needed, suppliers have {RFQ_RESPONSE_DAYS} business days", 2)
        return []

    def _on_event(self, msg: Message, body: dict) -> list[Message]:
        ref = _s(_first(body, "event_id"), msg.id)
        cost = _num(_first(body, "estimated_cost_gbp", "budget_gbp", "amount_gbp"))
        self._task(f"Event {ref}: confirm venue security, accessibility, public liability and data-protection clause",
                   max(1, _int(body.get("due_day"), self.clock.day + 7) - self.clock.day - 2))
        if cost <= 0:
            return []
        return self._open_logistics("event", ref, cost, "marketing", "events", _s(body.get("event_type"), "event"),
                                    _list(body.get("needs")))

    def _on_kickoff(self, msg: Message, body: dict) -> list[Message]:
        ref = _s(_first(body, "engagement_id"), msg.id)
        fte = self._fte(body.get("team_fte"))
        start = _int(body.get("start_day"), self.clock.day)
        self._task(f"Engagement {ref}: logistics checklist (room or client-site passes, secure workspace access request "
                   f"to IT Security) confirmed 2 days before day {start}", max(1, start - self.clock.day - 2))
        est = ENGAGEMENT_KIT_GBP_PER_FTE * math.ceil(fte) if fte > 0 else 0
        if est <= 0:
            return []
        return self._open_logistics("engagement", ref, float(est), "delivery", "engagement_logistics",
                                    "printing and travel kit", ["printing", "travel kit"])

    @staticmethod
    def _fte(value: Any) -> float:
        if isinstance(value, dict):
            return sum(_num(v) for v in value.values())
        if isinstance(value, (list, tuple)):
            return sum(_num(v.get("fte") if isinstance(v, dict) else v) for v in value)
        return _num(value)

    def _on_staffing(self, msg: Message, body: dict) -> list[Message]:
        ref = _s(_first(body, "engagement_id"), msg.id)
        gap = self._fte(body.get("shortfall_fte"))
        starters = math.ceil(gap) if gap > 0 else 0
        needed_by = _int(body.get("needed_by_day"), self.clock.day + WORKSPACE_KIT_LEAD_TIME_DAYS)
        self.state["demand"][ref] = {"starters": starters, "needed_by": needed_by}
        if needed_by - self.clock.day < WORKSPACE_KIT_LEAD_TIME_DAYS and starters:
            self._task(f"{ref}: kit and pass lead time is {WORKSPACE_KIT_LEAD_TIME_DAYS} days; warn Delivery and People",
                       1, "high")
        out: list[Message] = []
        for item in ("laptop", "desk_kit"):
            short = self._pending_demand() - self._available(item)
            if short > 0:
                dept = "it_security" if item == "laptop" else "operations"
                vid = "VN-0002" if item == "laptop" else "VN-0001"
                out += self._order_kits(item, short, vid, dept, f"forecast shortfall for {ref}")
        self._capacity_check()
        return out

    def _pending_demand(self) -> int:
        return sum(d["starters"] for d in self.state["demand"].values() if d["needed_by"] >= self.clock.day)

    def _available(self, item: str) -> int:
        return self.state["stock"][item] + sum(i["qty"] for i in self.state["inbound"] if i["item"] == item)

    def _order_kits(self, item: str, qty: int, vid: str, department: str, why: str) -> list[Message]:
        amount = float(KIT_PRICE_GBP[item] * qty)
        category = "it_hardware" if item == "laptop" else "workspace_equipment"
        out = self._simple_order(vid, department, category, amount, f"{qty} x {item.replace('_', ' ')}: {why}")
        self.state["inbound"].append({"day": out[-1].sim_time + WORKSPACE_KIT_LEAD_TIME_DAYS, "item": item, "qty": qty})
        return out

    def _buffer(self) -> int:
        return math.ceil(PLANNED_STARTERS[self._fy()] * STOCK_BUFFER_PCT / 100.0)

    def _capacity_check(self) -> None:
        for site, cap in DESK_CAPACITY.items():
            taken = len(self.state["desks"].get(site, {}))
            pct = 100.0 * taken / cap
            if pct > DESK_OCCUPANCY_WARNING_PCT and not self.state["capacity"].get(site):
                self.state["capacity"][site] = self.clock.day
                self._task(f"{site}: desk occupancy {pct:.0f}% exceeds {DESK_OCCUPANCY_WARNING_PCT}%; capacity review "
                           "for the Operations Manager (SOP-OPERATIONS-14)", 5, "high")

    # ================================================================== workspace (SOP-05, 06)
    def _employee(self, eid: str) -> dict:
        return self.state["employees"].setdefault(eid, {
            "id": eid, "reserved": [], "device_id": "", "ready": False, "access": False, "name": "", "site": "London",
            "start_day": None})

    def _on_access_provisioned(self, msg: Message, body: dict) -> list[Message]:
        eid = _s(_first(body, "employee_id", "contractor_id"), f"EMP-{msg.id}")
        emp = self._employee(eid)
        emp["access"] = True
        emp["device_id"] = _s(body.get("device_id"), emp["device_id"])
        if emp["ready"]:
            return []
        for item in ("laptop", "desk_kit"):
            if item not in emp["reserved"] and self.state["stock"][item] > 0:
                self.state["stock"][item] -= 1
                emp["reserved"].append(item)
        self.log_event("operations.activity.kit_reserved", f"{eid} reserved {emp['reserved']}", employee_id=eid)
        out: list[Message] = []
        for item in emp["reserved"]:
            out += self._maybe_restock(item)
        return out

    def _assign_desk(self, eid: str, site: str) -> str:
        desks = self.state["desks"].setdefault(site, {})
        if eid in desks:
            return desks[eid]
        seq = self.state["desk_seq"].get(site, 0) + 1
        self.state["desk_seq"][site] = seq
        label = f"4.{9 + seq:02d}" if site == "London" else f"NY-{seq:02d}"
        desks[eid] = label
        return label

    def _on_new_hire(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        eid = _s(_first(body, "employee_id"), f"EMP-{msg.id}")
        emp = self._employee(eid)
        if emp["ready"]:
            return []                                    # exactly one workspace_ready per employee
        name = _s(_first(body, "employee_name", "name", "candidate_name"), eid)
        loc = _s(body.get("location"), "London")
        site = "New York" if "new york" in loc.lower() or loc.upper() in ("NY", "NYC", "US") else "London"
        start = _int(body.get("start_day"), self.clock.day)
        listed = [_s(e) for e in _list(_first(body, "equipment", "needs"))]
        equipment = [e for e in listed if e not in ("workspace", "access_provisioning", "payroll_setup")] or [
            "laptop", "monitor", "dock", "keyboard_and_mouse"]
        emp.update({"name": name, "site": site, "start_day": start})
        remote = "remote" in loc.lower()
        needs = ["desk_kit"] + (["laptop"] if not listed or "laptop" in [e.lower() for e in listed] else [])
        short = []
        for item in needs:
            if item in emp["reserved"]:
                continue
            if s["stock"][item] > 0:
                s["stock"][item] -= 1
                emp["reserved"].append(item)
            else:
                short.append(item)
        out: list[Message] = []
        for item in short:                                # stock-out: order the shortfall now, ready after the lead time
            dept = "it_security" if item == "laptop" else "operations"
            out += self._simple_order("VN-0002" if item == "laptop" else "VN-0001", dept,
                                      "it_hardware" if item == "laptop" else "workspace_equipment",
                                      float(KIT_PRICE_GBP[item]), f"{item.replace('_', ' ')} for {eid} (stock-out)")
            emp["reserved"].append(item)
        for item in needs:                                # replenish the buffer after each draw-down
            out += self._maybe_restock(item)
        desk = "remote kit" if remote else self._assign_desk(eid, site)
        place = "Remote working kit" if remote else (
            f"London HQ, desk {desk}" if site == "London" else f"New York office, desk {desk}")
        delay = WORKSPACE_KIT_LEAD_TIME_DAYS if short else 0
        on_time = not short
        emp["ready"] = True
        s["ready_total"] += 1
        s["ready_on_time"] += 1 if on_time else 0
        self._task(f"Starter {eid}: health and safety induction, fire warden briefing, DSE assessment within 4 weeks, "
                   "signed asset form", 3 if on_time else 5)
        self._capacity_check()
        reason = "" if on_time else f" after a stock-out of {', '.join(short)} (lead time {delay} days)"
        out.append(self.emit("operations.workspace_ready", {
            "employee_id": eid, "employee_name": name, "name": name, "location": place, "desk": desk, "site": site,
            "department": _s(body.get("department")), "equipment": equipment, "start_day": start,
            "ready_day": self.clock.day + delay, "on_time": on_time,
            "summary": f"Desk and kit ready for {name}{reason}",
        }, recipient="people", delay_days=delay))
        return out

    def _maybe_restock(self, item: str) -> list[Message]:
        s = self.state
        buf = self._buffer()
        if self._available(item) >= buf:
            return []
        qty = 2 * buf - self._available(item)
        dept = "it_security" if item == "laptop" else "operations"
        return self._order_kits(item, qty, "VN-0002" if item == "laptop" else "VN-0001", dept,
                                f"replenish to buffer of {buf} ({STOCK_BUFFER_PCT}% of planned starters)")

    def _on_employee_left(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        eid = _s(_first(body, "employee_id"), f"EMP-{msg.id}")
        if eid in s["leavers"]:
            return []
        s["leaver_seq"] += 1
        last = _int(body.get("last_day"), self.clock.day)
        involuntary = _truthy(body.get("involuntary"))
        slow = s["leaver_seq"] % 10 == 0                  # deterministic: every tenth leaver is slow to return kit
        recovery = last if involuntary else (last + ASSET_RECOVERY_DAYS + 2 if slow else last + 3)
        s["leavers"][eid] = {"id": eid, "last_day": last, "deadline": last + ASSET_RECOVERY_DAYS, "recovery_day": recovery,
                             "status": "open", "within": None, "department": _s(body.get("department")),
                             "wiped": False}
        self._task(f"Leaver {eid}: recovery checklist, serial numbers, pass and desk release; deadline day "
                   f"{last + ASSET_RECOVERY_DAYS}", max(1, last - self.clock.day), "high" if involuntary else "medium")
        self._task(f"Leaver {eid}: reassign approver, budget-holder and requester roles to the line manager within "
                   "2 business days", 2)
        out: list[Message] = []
        if _s(body.get("department")) == "operations":
            role = _s(_first(body, "role", "role_title"))
            role = role if role in ROLE_LEVEL_BAND else OPS_ANALYST
            out += self._hire_request(role, "backfill", f"Backfill for {eid} within 5 business days of notice")
        return out

    # ================================================================== compliance (SOP-08, 09)
    def _new_action(self, source: str, title: str, severity: str, legal_due: Optional[int], owner: str,
                    finding_id: str = "", vendor_id: str = "", policy_update: bool = False) -> dict:
        s = self.state
        n = self._next("ca")
        due = self.clock.day + COMPLIANCE_SLA_DAYS[severity]
        if legal_due is not None:
            due = min(due, max(self.clock.day, legal_due))
        span = max(1, due - self.clock.day)
        late = n % 5 == 0                                  # deterministic: every fifth action is closed late
        attest = due + 2 if late else self.clock.day + max(1, int(span * (0.6 if owner == "operations" else 0.8)))
        action = {"id": f"CA-{n:04d}", "source": source, "title": title, "severity": severity, "created": self.clock.day,
                  "due_day": due, "owner": owner, "finding_id": finding_id, "vendor_id": vendor_id, "status": "open",
                  "attest_day": attest, "closed_day": None, "on_time": None, "escalated_coo": False,
                  "escalated_ceo": False, "policy_update": policy_update, "reminded": []}
        s["actions"][action["id"]] = action
        s["attest_queue"].append({"action_id": action["id"], "attest_day": attest})
        return action

    def _on_finding(self, msg: Message, body: dict) -> list[Message]:
        fid = _s(_first(body, "finding_id"), f"CF-{msg.id}")
        if any(a["finding_id"] == fid for a in self.state["actions"].values()):
            return []
        sev = _sev(body.get("severity"))
        owner = _s(body.get("action_owner"), "operations")
        title = _s(_first(body, "title", "summary"), fid)
        vid = _s(body.get("vendor_id"))
        legal_due = body.get("due_day")
        action = self._new_action("finding", title, sev, None if legal_due is None else _int(legal_due), owner, fid, vid,
                                  _truthy(_first(body, "policy_update_required", "policy_update_likely"))
                                  or "policy" in title.lower())
        if vid:
            rec = self.state["vendors"].get(vid)
            if rec is not None and rec["status"] in ("approved", "in_review"):
                if rec["status"] == "in_review":
                    rec["status"] = "pending"
            self.log_event("operations.activity.vendor_marked_pending", f"{vid} pending until {action['id']} closes",
                           vendor_id=vid, action_id=action["id"])
        self._task(f"{action['id']} ({fid}, {sev}): confirm owner {owner}, plan and evidence with the General Counsel's team; "
                   f"due day {action['due_day']}", 1, "critical" if sev == "critical" else "high" if sev == "high" else "medium")
        if sev == "critical":
            self._task(f"{action['id']}: critical finding; COO, General Counsel and CEO review daily until closed", 1,
                       "critical")
        return []

    def _on_regulatory_change(self, msg: Message, body: dict) -> list[Message]:
        owners = [_s(o).lower() for o in _list(body.get("owners"))]
        if owners and "operations" not in owners:
            self.log_event("operations.activity.regulatory_change_noted", "no operations impact", title=_s(body.get("title")))
            return []
        areas = [_s(a) for a in _list(body.get("impact_areas"))] or ["general_regulatory"]
        sev = _sev(body.get("severity"), "medium")
        title = _s(_first(body, "title", "regulation_id", "summary"), "regulatory change")
        effective = _int(body.get("effective_in_days"), 180)
        for area in areas:
            if any(a["source"] == "regulatory_change" and a["title"] == f"{title}: {area}"
                   for a in self.state["actions"].values()):
                continue
            ahead = max(7, effective - 7) if effective > 0 else 7
            action = self._new_action("regulatory_change", f"{title}: {area}", sev, self.clock.day + ahead, "operations")
            self._task(f"{action['id']}: assess {area} impact of {title} on suppliers, premises, records and continuity; "
                       f"update the operating-risk register by day {action['due_day']}", 3)
        return []

    def _on_policy_update(self, msg: Message, body: dict) -> list[Message]:
        pid = _s(_first(body, "policy_id"), f"POL-{msg.id}")
        if pid in self.state["policies"]:
            return []
        effective = _int(body.get("effective_day"), self.clock.day + POLICY_ALIGNMENT_DAYS)
        due = min(self.clock.day + POLICY_ALIGNMENT_DAYS, effective)
        title = _s(body.get("title"), pid)
        text = (title + " " + _s(body.get("summary"))).lower()
        sops = ["SOP-OPERATIONS-08"] + [n for k, n in (("supplier", "SOP-OPERATIONS-01"), ("vendor", "SOP-OPERATIONS-03"),
                                                       ("data", "SOP-OPERATIONS-03"), ("equipment", "SOP-OPERATIONS-05"),
                                                       ("continuity", "SOP-OPERATIONS-10"), ("purchas", "SOP-OPERATIONS-02"))
                                       if k in text]
        self.state["policies"][pid] = {"title": title, "due": due, "effective": effective, "sops": sorted(set(sops)),
                                       "aligned": False, "warned": False, "finding_id": _s(body.get("finding_id"))}
        for sop in sorted(set(sops)):
            self._task(f"Align {sop} and its checklists with {pid} ({title}) by day {due}", max(1, due - self.clock.day))
        return []

    # ================================================================== continuity (SOP-10, 11)
    def _tier_for(self, text: str, severity: str) -> int:
        t = text.lower()
        keys = ("email", "ledger", "engagement workspace", "identity", "sso", "tier 1", "tier-1", "tier1")
        return 1 if severity == "critical" or any(k in t for k in keys) else 2

    def _on_incident_detected(self, msg: Message, body: dict) -> list[Message]:
        iid = _s(_first(body, "incident_id"), f"INC-{msg.id}")
        sev = _sev(body.get("severity"), "low")
        rec = self.state["incidents"].setdefault(iid, {"severity": sev, "detected": self.clock.day, "active": False,
                                                       "tier": 2, "resolved": False, "test": False})
        rec["severity"] = sev
        if sev in ("high", "critical"):
            rec["active"] = True
            rec["tier"] = self._tier_for(_s(body.get("summary")) + " " + _s(body.get("category")), sev)
            self._task(f"{iid} ({sev}): continuity logistics active; list affected tier {rec['tier']} systems, third "
                       "parties and alternate arrangements; confirm with the Operations Manager", 0, "critical")
            self.log_event("operations.activity.continuity_activated", f"{iid} {sev}", incident_id=iid, tier=rec["tier"])
        else:
            self.log_event("operations.activity.incident_recorded", f"{iid} {sev} recorded only", incident_id=iid)
        return []

    def _on_incident_resolved(self, msg: Message, body: dict) -> list[Message]:
        iid = _s(_first(body, "incident_id"), f"INC-{msg.id}")
        rec = self.state["incidents"].setdefault(iid, {"severity": _sev(body.get("severity"), "low"), "detected": None,
                                                       "active": False, "tier": 2, "resolved": False, "test": False})
        sev = _sev(body.get("severity"), rec["severity"])
        rec["resolved"] = True
        if not (sev in ("high", "critical") or rec["active"]):
            return []
        if rec["test"]:
            return []
        tier = rec["tier"] if rec["active"] else self._tier_for(_s(body.get("summary")), sev)
        hours = _num(_first(body, "time_to_resolve_hours", "restore_hours", "rto_hours_actual"), 0.0)
        loss = _num(_first(body, "data_loss_hours", "rpo_hours_actual"), 0.0)
        crisis = iid in self.state["crisis_pending"] or self.state["crisis_mode"]
        rec["test"] = True
        if self.state["crisis_pending"].pop(iid, None) is not None:
            self.state["crisis_mode"] = False
        bdays = LESSONS_LEARNED_CRISIS_BDAYS if crisis else LESSONS_LEARNED_BDAYS
        findings = [f"Root cause: {_s(body.get('root_cause'), 'see the post-incident review')}"] + (
            [f"{_int(body.get('follow_up_actions'))} follow-up actions from IT Security"] if body.get("follow_up_actions")
            else [])
        return [self._emit_test("live_incident", f"Live {sev} incident {iid}", iid, sev, tier, hours, loss, findings,
                                self._bday_offset(bdays))]

    def _emit_test(self, test_type: str, scenario: str, incident_id: str, severity: str, tier: int, hours: float,
                   loss_hours: float, findings: list, delay: int) -> Message:
        s = self.state
        rto = RTO_TIER1_HOURS if tier == 1 else RTO_TIER2_HOURS
        rpo = RPO_TIER1_HOURS if tier == 1 else RPO_TIER2_HOURS
        rto_met, rpo_met = hours <= rto, loss_hours <= rpo
        test_id = f"BCT-{self._next('bct'):04d}"
        s["tests"][test_id] = {"day": self.clock.day + delay, "type": test_type, "rto_met": rto_met, "rpo_met": rpo_met}
        findings = list(findings)
        if not rto_met:
            findings.append(f"RTO missed: {hours:g}h against {rto}h; corrective action with owner within 5 business days")
        if not rpo_met:
            findings.append(f"RPO missed: {loss_hours:g}h of data loss against {rpo}h")
        return self.emit("operations.continuity_test_completed", {
            "test_id": test_id, "scenario": scenario, "test_type": test_type, "incident_id": incident_id,
            "severity": severity, "tier": tier, "rto_target_hours": rto, "rpo_target_hours": rpo,
            "rto_met": rto_met, "rpo_met": rpo_met, "rto_hours_actual": hours, "rpo_hours_actual": loss_hours,
            "result": "passed" if rto_met and rpo_met else "failed", "findings": findings,
            "summary": f"{test_type} test {test_id} ({scenario}): RTO {'met' if rto_met else 'missed'}, "
                       f"RPO {'met' if rpo_met else 'missed'}"}, delay_days=delay)

    def _on_crisis(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        cid = _s(_first(body, "crisis_id"), f"CRS-{msg.id}")
        if cid in s["crises"]:
            return []
        s["crises"].append(cid)
        s["crisis_mode"], s["crisis_day"] = True, self.clock.day
        iid = _s(body.get("incident_id"))
        self._task(f"Crisis {cid}: confirm contact trees, alternate premises, supplier contacts and critical deliveries; "
                   "emergency order rule active (up to 10,000 with CFO approval)", 0, "critical")
        self.log_event("operations.activity.crisis_logistics", f"{cid} logistics checklist opened", crisis_id=cid)
        inc = s["incidents"].get(iid)
        if inc and inc["active"] and not inc["resolved"] and not inc["test"]:
            s["crisis_pending"][iid] = {"crisis_id": cid, "fallback_day": self.clock.day + CRISIS_REVIEW_FALLBACK_DAYS}
            return []                                       # the live-incident test follows the incident's resolution
        hours = _num(_first(body, "restore_hours", "time_to_resolve_hours"), 0.0)
        s["tests"]["crisis:" + cid] = {"day": self.clock.day}
        return [self._emit_test("live_incident", f"Crisis {cid}: {_s(body.get('category'), 'company-wide crisis')}", iid,
                                _sev(body.get("severity"), "high"), 1, hours, _num(body.get("data_loss_hours")),
                                ["Crisis logistics checklist exercised", "Contact trees and alternate premises confirmed"],
                                self._bday_offset(LESSONS_LEARNED_CRISIS_BDAYS))]

    def _on_vulnerability(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        vuln = _s(_first(body, "vulnerability_id"), f"VULN-{msg.id}")
        sev = _sev(body.get("severity"), "medium")
        if vuln in s["vulns"]:
            return []
        s["vulns"][vuln] = {"severity": sev, "day": self.clock.day}
        text = (_s(body.get("component")) + " " + _s(body.get("summary"))).lower()
        due = _int(body.get("due_day"), self.clock.day + 5)
        self._task(f"{vuln} ({sev}): identify Operations-managed assets and suppliers affected within 1 business day; "
                   f"remediation deadline day {due}", 1, "high" if sev in ("high", "critical") else "medium")
        if sev not in ("high", "critical"):
            return []
        out: list[Message] = []
        for vid, rec in sorted(s["vendors"].items()):
            if rec["name"].lower() in text and not rec.get("seed"):
                out += self._request_review(vid, "incident", _num(rec.get("annual")), _num(rec.get("amount")), "")
        keys = [k for k in REPLACEMENT_PRICE_GBP if k != "default" and k in text]
        hardware = keys or [k for k in ("hardware", "firmware", "device", "laptop", "router") if k in text]
        if hardware:
            price = REPLACEMENT_PRICE_GBP[keys[0]] if keys else REPLACEMENT_PRICE_GBP["default"]
            out += self._simple_order("VN-0001", "it_security", "it_hardware", float(price),
                                      f"replacement hardware for {vuln} ({sev})", framework=False)
        return out

    # ================================================================== process and PMO (SOP-12)
    def _seed_programmes(self) -> None:
        seed = (("New York office fit-out", ((289, "Serviced office contracted"), (380, "Fit-out complete"))),
                ("ISO 27001 and SOC 2 operational actions", ((120, "ISO 27001 stage 1 actions closed"),
                                                              (330, "SOC 2 Type I evidence pack"))),
                ("US launch operational readiness", ((250, "Vendor and entity set-up"), (400, "Go-live readiness"))))
        for name, miles in seed:
            pid = f"PRG-{self._next('prg'):03d}"
            self.state["programmes"][pid] = {"name": name, "rebaselined": False, "milestones": [
                {"due_day": d, "name": n, "status": "open", "shift": 0} for d, n in miles]}

    def _on_data_quality(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        sev = _sev(body.get("severity"), "low")
        check = _s(body.get("check"), "unspecified")
        source = _s(_first(body, "source_department", "department"), "unknown")
        iid = _s(body.get("issue_id"), msg.id)
        s["dq_log"].append({"day": self.clock.day, "check": check, "source": source})
        window = [e for e in s["dq_log"] if e["check"] == check and e["source"] == source
                  and e["day"] >= self.clock.day - DQ_WINDOW_DAYS]
        n = len(window)
        qualifies = sev in ("high", "critical") or n >= 2
        key = f"{check}|{source}"
        if not qualifies:
            self.log_event("operations.activity.dq_tracked", f"{check} from {source} tracked ({n})", issue_id=iid)
            return []
        imp = s["improvements"].get(key)
        if imp is None:
            imp = {"id": f"PI-{self._next('pi'):04d}", "key": key, "check": check, "source": source, "severity": sev,
                   "created": self.clock.day, "published": False, "issue_id": iid, "adopt_day": self.clock.day + 60,
                   "adopted": False, "counted": False}
            s["improvements"][key] = imp
            self._task(f"{imp['id']}: validate the estimate and owner for the {check} fix with the process owner; Finance "
                       "validates any cash saving", 5)
        if SEVERITIES.index(sev) > SEVERITIES.index(imp["severity"]):
            imp["severity"] = sev
        hours = REWORK_HOURS[imp["severity"]]
        saving = n * OCCURRENCES_PER_WINDOW_ANNUALISED * hours * NOTIONAL_HOURLY_COST_GBP
        cost = ESTIMATED_IMPLEMENTATION_GBP[imp["severity"]]
        payback = round(cost / (saving / 12.0), 1) if saving else 999.0
        imp.update({"saving": saving, "cost": cost, "payback": payback, "issue_id": iid})
        if imp["published"] or saving < PROCESS_PROPOSAL_MIN_SAVING_GBP or payback > PROCESS_MAX_PAYBACK_MONTHS:
            self.log_event("operations.activity.improvement_tracked", f"{imp['id']} saving {saving:,.0f}", proposal_id=imp["id"],
                           published=imp["published"])
            return []
        imp["published"] = True
        owner = self._holder(OPS_MANAGER)
        return [self.emit("operations.process_improvement_proposed", {
            "proposal_id": imp["id"], "title": f"Fix recurring {check} defects from {source}",
            "process": f"{source} {check} data flow", "trigger_source": "data_quality", "source_issue_id": iid,
            "annualised_saving_gbp": saving, "implementation_cost_gbp": cost, "estimated_cost_gbp": cost,
            "payback_months": payback, "owner": owner, "due_day": self.clock.day + self._bday_offset(10),
            "severity": imp["severity"],
            "summary": f"{imp['id']}: {n} occurrence(s) in {DQ_WINDOW_DAYS} days; saving {saving:,.0f} a year at "
                       f"{NOTIONAL_HOURLY_COST_GBP}/hour, payback {payback} months"}, recipient="executive")]

    def _on_okrs(self, msg: Message, body: dict) -> list[Message]:
        items = _list(_first(body, "okrs", "objectives"))
        names = [_s(i.get("objective") or i.get("name") or i.get("title")) if isinstance(i, dict) else _s(i) for i in items]
        for name in [n for n in names if n][:8]:
            pid = f"PRG-{self._next('prg'):03d}"
            self.state["programmes"][pid] = {"name": name, "rebaselined": False, "milestones": [
                {"due_day": self.clock.day + d, "name": f"{name}: {label}", "status": "open", "shift": 0}
                for d, label in ((45, "plan baselined"), (90, "first benefit"))]}
        self._task("Align the programme portfolio and RAID log with the new OKRs; send the plan to the COO within "
                   "10 business days", self._bday_offset(10), "high")
        return []

    def _on_strategy(self, msg: Message, body: dict) -> list[Message]:
        n = 0
        for prog in self.state["programmes"].values():
            open_ms = [m for m in prog["milestones"] if m["status"] == "open"]
            if open_ms:
                prog["rebaselined"] = True
                n += 1                                           # one miss per re-baselined programme
                for m in open_ms:
                    m["shift"] = 30
        self.state["milestones_due"] += n                       # a re-baseline counts as a miss
        self._task("Assess the strategy update on programmes, spend, premises and vendors; brief the COO", 5)
        return []

    # ================================================================== budget and capacity (SOP-13, 14)
    def _budget_year(self, body: dict) -> int:
        fy = _int(_first(body, "fiscal_year"), 0)
        if fy:
            return fy
        m = re.search(r"(20\d\d)", _s(_first(body, "budget_cycle_id", "budget_id")))
        if m:
            return int(m.group(1))
        return self.clock.date.year + (1 if self.clock.date.month >= 10 else 0)

    def _on_budget_cycle(self, msg: Message, body: dict) -> list[Message]:
        fy = self._budget_year(body)
        cycle = _s(body.get("budget_cycle_id"), f"BUD-{fy}")
        if cycle in self.state["budget_cycles"]:
            return []
        idx = max(0, min(2, fy - FIRST_FISCAL_YEAR))
        people, non_people = BUDGET_PEOPLE_GBP[idx], BUDGET_NON_PEOPLE_GBP[idx]
        total = people + non_people
        envelope = (200_000 + 100_000, 400_000 + 300_000, 750_000 + 900_000)[idx]
        gap_pct = 100.0 * abs(total - envelope) / envelope
        deadline = body.get("deadline_day")
        delay = OPS_BUDGET_SUBMISSION_DAY
        if deadline is not None:
            delay = max(0, min(OPS_BUDGET_SUBMISSION_DAY, _int(deadline) - self.clock.day))
        self.state["budget_cycles"][cycle] = {"fy": fy, "opened": self.clock.day, "submit_day": self.clock.day + delay}
        if gap_pct > 5.0:
            self._task(f"{cycle}: operations draft is {gap_pct:.1f}% from the COMPANY.md 5.4 envelope; COO to attach the "
                       "business case", 3, "high")
        self._task(f"{cycle}: COO reviews headcount, workspace and New York plan, renewals, compliance and continuity costs "
                   f"before submission on day {OPS_BUDGET_SUBMISSION_DAY} of the cycle", max(1, delay - 2))
        return [self.emit("operations.budget_submitted", {
            "budget_cycle_id": cycle, "fiscal_year": fy, "department": "operations", "people_gbp": people,
            "non_people_gbp": non_people, "total_gbp": total, "amount_gbp": total,
            "people_cost_gbp": people, "non_people_cost_gbp": non_people, "headcount": HEADCOUNT_PLAN[idx],
            "agents": AGENT_PLAN[idx],
            "summary": f"Operations {cycle}: people {people:,}, non-people {non_people:,}, total {total:,}; "
                       f"{HEADCOUNT_PLAN[idx]} humans and {AGENT_PLAN[idx]} agents"}, recipient="finance",
            delay_days=delay)]

    def _on_budget_approved(self, msg: Message, body: dict) -> list[Message]:
        fy = self._budget_year(body)
        idx = max(0, min(2, fy - FIRST_FISCAL_YEAR))
        self.state["approved_budget"][fy] = {"day": self.clock.day, "people_gbp": BUDGET_PEOPLE_GBP[idx],
                                             "non_people_gbp": BUDGET_NON_PEOPLE_GBP[idx]}
        self._task(f"Load the approved FY{fy} budget by line and quarter within 3 business days; set the "
                   f"{BUDGET_WARNING_PCT}% budget-line warnings and tell line owners", self._bday_offset(3))
        return []

    def _hire_request(self, role: str, reason: str, why: str) -> list[Message]:
        level, band = ROLE_LEVEL_BAND[role]
        key = f"{role}|{reason}|{self.clock.date.year}|{self.clock.quarter}|{len(self.state['hire_requests'])}" \
            if reason == "backfill" else f"{role}|{reason}|{self.clock.date.year}|{self.clock.quarter}"
        if key in self.state["hire_requests"]:
            return []
        self.state["hire_requests"][key] = self.clock.day
        return [self.emit("operations.hire_requested", {
            "department": "operations", "role": role, "level": level, "salary_band_gbp": list(band), "reason": reason,
            "start_quarter": self._start_quarter(role), "justification": why,
            "severity": "medium", "summary": f"Operations requests {role} ({reason}): {why}"}, recipient="people")]

    def _start_quarter(self, role: str) -> str:
        for r, y, q in HIRING_PLAN:
            if r == role and (y, q) >= (self.clock.date.year, self.clock.quarter):
                return f"Q{q} FY{y}"
        return f"Q{self.clock.quarter + 1 if self.clock.quarter < 4 else 1} FY{self.clock.date.year}"

    # ================================================================== scheduled behaviour
    def tick(self) -> list[Message]:
        s = self.state
        out: list[Message] = []
        day, today = self.clock.day, self.clock.date
        for item in list(s["inbound"]):
            if day >= item["day"]:
                s["stock"][item["item"]] += item["qty"]
                s["inbound"].remove(item)
        for lv in s["leavers"].values():
            if lv["status"] == "open":
                if day >= lv["recovery_day"]:
                    lv["status"], lv["within"] = "recovered", lv["recovery_day"] <= lv["deadline"]
                    self.log_event("operations.activity.asset_recovery", f"{lv['id']} equipment recovered",
                                   employee_id=lv["id"], within_deadline=lv["within"])
                elif day > lv["deadline"] and not lv["wiped"]:
                    lv["wiped"], lv["within"] = True, False
                    self._task(f"{lv['id']}: equipment not returned; IT Security to remote-wipe and lock, People to be told",
                               1, "high")
        for item in list(s["attest_queue"]):
            if day >= item["attest_day"]:
                s["attest_queue"].remove(item)
                out += self._attest(s["actions"][item["action_id"]])
        out += self._compliance_watch()
        out += self._rfq_exceptions()
        out += self._scheduled_tests()
        if s["crisis_mode"] and s["crisis_day"] is not None and day >= s["crisis_day"] + CRISIS_REVIEW_FALLBACK_DAYS:
            s["crisis_mode"] = False
        for iid, p in list(s["crisis_pending"].items()):
            if day >= p["fallback_day"]:
                del s["crisis_pending"][iid]
                s["incidents"][iid]["test"] = True
                out.append(self._emit_test("live_incident", f"Crisis {p['crisis_id']}", iid, "critical", 1, 0.0, 0.0,
                                           ["Incident not yet resolved at the crisis review date"], 0))
        for imp in s["improvements"].values():
            if not imp["adopted"] and day >= imp["adopt_day"]:
                imp["adopted"] = True
            if imp["adopted"] and not imp["counted"] and day >= imp["adopt_day"] + 90:
                imp["counted"] = True                           # saving counted after the 90-day check
        for prog in s["programmes"].values():
            for m in prog["milestones"]:
                if m["status"] == "open" and day >= m["due_day"] + m["shift"]:
                    m["status"] = "done"
                    if not m["shift"]:                          # a re-baselined milestone was counted as a miss already
                        s["milestones_due"] += 1
                        s["milestones_on_time"] += 1
        for pid, pol in s["policies"].items():
            if not pol["aligned"] and day >= pol["due"] - 2:
                pol["aligned"] = True
                self.log_event("operations.activity.policy_aligned", f"{pid} aligned", policy_id=pid, sops=pol["sops"])
        if today.weekday() == 0 and today.month in (1, 4, 7, 10) and today.day <= 7 and (
                today.year, self.clock.quarter) not in [tuple(q) for q in s["reviewed_quarters"]]:
            out += self._quarterly_review()
        if today.weekday() == 0 and today.day <= 7 and today.strftime("%Y-%m") not in s["scorecard_months"]:
            s["scorecard_months"].append(today.strftime("%Y-%m"))
            out += self._vendor_monthly()
        if today.weekday() == 4:
            open_actions = [a for a in s["actions"].values() if a["status"] == "open"]
            self.log_event("operations.activity.open_actions_report", f"{len(open_actions)} open compliance actions",
                           open=len(open_actions), overdue=sum(1 for a in open_actions if a["due_day"] < day))
        self._refresh_kpis()
        return out

    def _attest(self, action: dict) -> list[Message]:
        """Deterministic model of the human attestation that closes an action (agents never close actions)."""
        s = self.state
        if action["status"] != "open":
            return []
        action["status"], action["closed_day"] = "closed", self.clock.day
        action["on_time"] = self.clock.day <= action["due_day"]
        attester = self._holder(COMPLIANCE_SPECIALIST)
        vid = action["vendor_id"]
        out: list[Message] = []
        if vid and vid in s["vendors"]:
            s["vendors"][vid]["dpa_cleared"] = True
            if s["vendors"][vid]["status"] == "pending" and s["vendors"][vid]["assessment"] is not None:
                out += self._decide_vendor(vid)
        if action["source"] != "finding":
            self.log_event("operations.activity.action_closed", f"{action['id']} closed", action_id=action["id"],
                           attested_by=attester)
            return out
        out.append(self.emit("operations.compliance_action_completed", {
            "finding_id": action["finding_id"], "action_id": action["id"], "title": action["title"],
            "severity": action["severity"], "due_day": action["due_day"], "closed_day": self.clock.day,
            "on_time": action["on_time"], "attested_by": attester,
            "evidence_ref": f"EVD-{action['id']}", "policy_update_required": action["policy_update"],
            "summary": f"{action['id']} for {action['finding_id']} closed {'on time' if action['on_time'] else 'late'}; "
                       f"attested by {attester}"}, recipient="legal"))
        return out

    def _compliance_watch(self) -> list[Message]:
        day = self.clock.day
        for a in self.state["actions"].values():
            if a["status"] != "open":
                continue
            span = max(1, a["due_day"] - a["created"])
            for pct in (50, 80):
                if pct not in a["reminded"] and day >= a["created"] + span * pct // 100 and day < a["due_day"]:
                    a["reminded"].append(pct)
                    self.log_event("operations.activity.action_reminder", f"{a['id']} at {pct}% of its period",
                                   action_id=a["id"])
            if day >= a["due_day"] and not a["escalated_coo"]:
                a["escalated_coo"] = True
                self._task(f"{a['id']} ({a['severity']}) is due; escalated to the COO", 0, "high")
            if day >= a["due_day"] + COMPLIANCE_ESCALATION_DAYS and not a["escalated_ceo"]:
                a["escalated_ceo"] = True
                self._task(f"{a['id']} is {COMPLIANCE_ESCALATION_DAYS} days overdue; escalated to the CEO", 0, "critical")
        return []

    def _rfq_exceptions(self) -> list[Message]:
        """SOP-01: fewer than three quotes after RFQ_EXCEPTION_DAYS business days takes the exception route."""
        out: list[Message] = []
        for rfq in list(self.state["rfqs"].values()):
            if rfq["status"] != "open" or rfq["path"] == "single" or not rfq["quotes"]:
                continue
            if self._bdays_between(rfq["first_day"], self.clock.day) >= RFQ_EXCEPTION_DAYS and len(rfq["quotes"]) < 3:
                kind = "sole_source" if len(rfq["quotes"]) == 1 else "fewer_than_three"
                self._task(f"{rfq['id']}: {kind.replace('_', ' ')} exception after {RFQ_EXCEPTION_DAYS} business days; "
                           "approver one level above the order value signs the justification", 1)
                out += self._decide_rfq(rfq, kind)
        return out

    def _scheduled_tests(self) -> list[Message]:
        out: list[Message] = []
        today = self.clock.date
        for i, (month, dom, kind, scenario) in enumerate(TEST_PROGRAMME.get(today.year, ())):
            key = f"sched:{today.year}:{i}"
            if key in self.state["tests"] or today < date(today.year, month, dom):
                continue
            self.state["tests"][key] = {"day": self.clock.day}
            if kind == "tabletop":
                hours, loss = 3.0, 0.5
            else:
                n = self.state["test_seq"]["technical"]
                self.state["test_seq"]["technical"] = n + 1
                hours, loss = TECHNICAL_RTO_HOURS[n % len(TECHNICAL_RTO_HOURS)], 0.5
            findings = [f"{kind.replace('_', ' ').title()} exercise: scenario pack run with the Operations Manager and CISO",
                        "Update contact trees and the supplier contingency list"]
            out.append(self._emit_test(kind, scenario, "", "medium", 1, hours, loss, findings, 0))
        return out

    def _quarterly_review(self) -> list[Message]:
        s = self.state
        s["reviewed_quarters"].append([self.clock.date.year, self.clock.quarter])
        active = [v for v in s["vendors"].values() if v["status"] == "approved" and not v["seed"]]
        s["capacity"]["last_review"] = {"day": self.clock.day, "pos": len(s["orders"]), "open_actions": sum(
            1 for a in s["actions"].values() if a["status"] == "open"), "active_vendors": len(active),
            "starters": s["ready_total"]}
        self.log_event("operations.activity.capacity_review", "quarterly capacity review", **s["capacity"]["last_review"])
        out: list[Message] = []
        y, q = self.clock.date.year, self.clock.quarter
        ny, nq = (y, q + 1) if q < 4 else (y + 1, 1)
        for role, sy, sq in HIRING_PLAN:
            if (sy, sq) == (ny, nq):
                out += self._hire_request(role, "growth", f"Planned start Q{sq} FY{sy} (blueprint.md section 5); "
                                                           "45-day time-to-hire")
        return out

    def _vendor_monthly(self) -> list[Message]:
        """SOP-04: monthly scorecard and re-review requests for vendors whose reassessment date has arrived."""
        out: list[Message] = []
        for vid, rec in sorted(self.state["vendors"].items()):
            if rec["status"] != "approved" or rec.get("seed") or rec["reassess_day"] is None:
                continue
            lead = RENEWAL_DIARY_CRITICAL_DAYS if _num(rec.get("annual")) >= CRITICAL_VENDOR_ANNUAL_GBP \
                else RENEWAL_DIARY_OTHER_DAYS
            if not rec["reassess_requested"] and self.clock.day >= rec["reassess_day"] - lead:
                rec["reassess_requested"] = True
                out += self._request_review(vid, "annual_review", _num(rec.get("annual")), _num(rec.get("amount")), "")
        self.log_event("operations.activity.vendor_scorecards", "monthly vendor scorecards built",
                       vendors=len(self.state["vendors"]))
        return out

    # ================================================================== KPI bookkeeping
    def _refresh_kpis(self) -> None:
        s = self.state
        if s["ready_total"]:
            self._set_kpi("workspace_ready_on_time_pct", 100.0 * s["ready_on_time"] / s["ready_total"])
        done = [lv for lv in s["leavers"].values() if lv["within"] is not None]
        if done:
            self._set_kpi("asset_recovery_pct", 100.0 * sum(1 for lv in done if lv["within"]) / len(done))
        if s["review_cycles"]:
            self._set_kpi("vendor_review_cycle_days", _median(s["review_cycles"]))
        if s["three_quote_total"]:
            self._set_kpi("three_quote_compliance_pct", 100.0 * s["three_quote_ok"] / s["three_quote_total"])
        if s["orders"]:
            self._set_kpi("po_coverage_pct", 100.0)       # every commitment is a PO placed before the commitment
        if s["procurement_cycles"]:
            self._set_kpi("procurement_cycle_days", _median(s["procurement_cycles"]))
        if s["savings_pct_first"]:
            self._set_kpi("procurement_savings_pct", 100.0 * s["savings_pct_saved"] / s["savings_pct_first"])
        closed = [a for a in s["actions"].values() if a["status"] == "closed"]
        overdue = [a for a in s["actions"].values() if a["status"] == "open" and a["due_day"] < self.clock.day]
        if closed or overdue:
            self._set_kpi("compliance_actions_on_time_pct",
                          100.0 * sum(1 for a in closed if a["on_time"]) / (len(closed) + len(overdue)))
        if s["actions"]:
            self._set_kpi("overdue_compliance_actions", len(overdue))
        if s["tests"]:
            real = [t for k, t in s["tests"].items() if "rto_met" in t]
            self._set_kpi("continuity_tests_completed", len(real))
            if real:
                self._set_kpi("continuity_rto_met_pct", 100.0 * sum(1 for t in real if t["rto_met"]) / len(real))
        adopted = [i for i in s["improvements"].values() if i["adopted"]]
        if s["improvements"]:
            self._set_kpi("process_improvements_adopted", len(adopted))
            self._set_kpi("process_savings_gbp", sum(i.get("saving", 0) for i in s["improvements"].values() if i["counted"]))
        if s["milestones_due"]:
            self._set_kpi("programme_on_time_pct", 100.0 * s["milestones_on_time"] / s["milestones_due"])
        scope = [v for v in s["vendors"].values() if v["in_scope"] and v["first_order_day"] is not None]
        if scope:
            ok = sum(1 for v in scope if v["approved_day"] is not None and v["approved_day"] <= v["first_order_day"])
            self._set_kpi("vendor_approved_before_order_pct", 100.0 * ok / len(scope))
        approved = s["approved_budget"].get(self.clock.date.year)
        if approved and approved["non_people_gbp"]:
            spent = sum(o["annual"] for o in s["orders"] if o["department"] == "operations")
            phased = approved["non_people_gbp"] * max(1, self.clock.date.timetuple().tm_yday) / 365.0
            self._set_kpi("budget_variance_pct", min(100.0, 100.0 * abs(spent - phased) / phased))


def build_agent(llm, bus, clock, log) -> OperationsAgent:
    """Factory used by core.company discovery. The head of department is the COO (COMPANY.md 9.2, blueprint.md)."""
    role = Role(COO, "operations", "head", (1, 1, 1), (140000, 200000), CEO)
    return OperationsAgent("operations", "operations", role, llm, bus, clock, log)
