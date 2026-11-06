"""IT and Security department agent for Lumenhall Partners (ItSecurityAgent).

Defensive scope only: IT operations, identity and access, security operations and incident response, GRC
(ISO 27001, Cyber Essentials Plus, SOC 2 Type II), vendor risk, client assurance, vulnerability management and
AI-agent credential governance. Owns the lifecycle chains of CONVENTIONS.md 7.2:

* hiring: ``people.new_hire_started`` -> ``it_security.access_provisioned``; ``people.employee_left`` ->
  ``it_security.access_revoked``; ``it_security.hire_requested`` for the department's own capacity needs;
* security incident: ``external.security_alert`` -> ``incident_detected`` -> (personal data) ``data_breach_confirmed``
  -> ``legal.regulator_notification_filed`` -> ``incident_resolved``;
* vendors: ``operations.vendor_review_requested`` -> ``vendor_risk_assessed``;
* compliance: certification plan -> ``certification_status_updated``; client assurance:
  ``sales.security_review_requested`` -> ``security_questionnaire_completed``.

Agents draft, analyse, monitor and propose; humans decide (SOP-IT_SECURITY-xx step markers). The agent never notifies
a regulator, signs a contract, approves payments above GBP 10,000 or accepts a risk (COMPANY.md section 9.4).
Deterministic: no wall clock, no randomness, ids from deterministic counters. All figures are modelled assumptions.
"""

from __future__ import annotations

import math
from dataclasses import replace
from datetime import date, timedelta
from typing import Any, Optional

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# --------------------------------------------------------------------------------------------------------------
# Constants mirrored from sops.md (one definition there, one here)
# --------------------------------------------------------------------------------------------------------------
VULN_SLA_DAYS = {"critical": 7, "high": 30, "medium": 60, "low": 90}   # SOP-IT_SECURITY-06
VULN_EXPLOITED_SLA_HOURS = 24          # SOP-06: critical on the KEV list or actively exploited
VULN_VERIFY_BDAYS = 2                  # SOP-06: fix verified within 2 business days
LEAVER_PRIVILEGED_HOURS = 1            # SOP-05: privileged accounts disabled within 1 hour of last working time
LEAVER_ALL_ACCESS_HOURS = 4            # SOP-05: all access within 4 hours
TRIAGE_CRITICAL_HIGH_MINUTES = 30      # SOP-01
TRIAGE_MEDIUM_CLOCK_HOURS = 4          # SOP-01
TRIAGE_LOW_BUSINESS_DAYS = 1           # SOP-01
DECLARATION_DECISION_HOURS = 1         # SOP-01
QUESTIONNAIRE_STANDARD_BDAYS = 3       # SOP-07
QUESTIONNAIRE_BESPOKE_BDAYS = 4        # SOP-07
QUESTIONNAIRE_ESCALATION_DAYS = 5      # kpis.md: a breach of 5 days is escalated to the CRO and CISO
VENDOR_REVIEW_BDAYS = {1: 10, 2: 5, 3: 2}   # SOP-08 by tier
VENDOR_CONDITIONS_VERIFY_BDAYS = 5     # SOP-08
VENDOR_REASSESS_DAYS = {1: 365, 2: 730, 3: 365}   # Tier 1 annually, Tier 2 two-yearly, Tier 3 at renewal (assumed 1y)
AGENT_CREDENTIAL_ROTATION_DAYS = 90    # SOP-10 (kpis.md: 90 days)
AGENT_CREDENTIAL_ROTATION_HIGH_RISK_DAYS = 30   # SOP-10: high-privilege agents; kpis.md: agents touching client data
AGENT_UNUSED_REVOKE_DAYS = 30          # SOP-10
AGENT_REVIEW_BDAYS = 5                 # SOP-10 security review
AGENT_REVIEW_URGENT_BDAYS = 2          # SOP-10 urgent client-facing change
REGISTER_REVIEW_DAYS = 91              # SOP-10 quarterly register review
CISO_SIGNOFF_DEAL_GBP = 250_000        # SOP-07 step 5
LARGE_DEAL_GAP_GBP = 500_000           # SOP-07 exceptions
RISK_ACCEPTANCE_MAX_DAYS = 90          # SOP-06 step 7
BREACH_ASSESSMENT_HOURS = 12           # SOP-02
ICO_NOTIFICATION_HOURS = 72            # COMPANY.md section 9.3 / SOP-02
BREACH_ESCALATION_HOURS = 60           # SOP-02: filing delayed beyond 60 hours -> CEO and General Counsel
BREACH_CLOSURE_BDAYS = 10              # SOP-02 closure report
CRISIS_BRIDGE_MINUTES = 30             # SOP-03
CRISIS_FIRST_SITREP_HOURS = 2          # SOP-03
CRISIS_SITREP_INTERVAL_HOURS = 4       # SOP-03
CONTRACTOR_ACCESS_BDAYS = 2            # SOP-04 contractor access ceiling
JOINER_ACCESS_SLA_BDAYS = 1            # kpis.md access_provisioning_sla_pct
ACCESS_CHECK_DAYS = 30                 # SOP-04 step 8
REGULATORY_IMPACT_BDAYS = 10           # SOP-09
PROCEDURE_UPDATE_BDAYS = 10            # SOP-09
POLICY_ATTESTATION_TARGET_PCT = 95.0   # SOP-09
POLICY_ATTESTATION_DAYS = 30           # SOP-09
CONTINUITY_FINDING_BDAYS = 5           # SOP-09
READINESS_ALERT_PCT = 80.0             # SOP-09: below 80% eight weeks before audit -> at risk
READINESS_ALERT_DAYS = 56              # SOP-09
MINOR_NC_CLOSE_DAYS, MAJOR_NC_CLOSE_DAYS = 60, 30   # SOP-09
BUDGET_DEADLINE_BDAYS = 15             # SOP-11
BUDGET_QUERY_BDAYS = 2                 # SOP-11
REBASELINE_BDAYS = 10                  # SOP-11
BUDGET_VARIANCE_FLAG_PCT = 10.0        # SOP-11
HIRE_REQUEST_BDAYS = 5                 # SOP-12
OPEN_CRIT_HIGH_VULN_TRIGGER = 15       # SOP-12
ALERTS_PER_SPECIALIST_TRIGGER = 150    # SOP-12
QUESTIONNAIRE_BACKLOG_TRIGGER = 6      # SOP-12
QUESTIONNAIRE_AGE_TRIGGER_BDAYS = 5    # SOP-12
AGENT_PAYMENT_LIMIT_GBP = 10_000       # COMPANY.md section 9.4
UNBUDGETED_CFO_GBP, UNBUDGETED_CEO_GBP = 50_000, 250_000   # COMPANY.md section 9.3
LOADED_COST_FACTOR = 1.28              # COMPANY.md section 5.4

# COMPANY.md section 5.4 (GBP k) and section 6.1 for it_security: (people Y1..Y3), (non-people Y1..Y3), humans
ENVELOPE_PEOPLE_GBP_K = (260, 470, 900)
ENVELOPE_NON_PEOPLE_GBP_K = (200, 450, 1400)
HEADCOUNT_PLAN = (2, 5, 9)
AGENT_PLAN = (2, 4, 8)
FIRST_FISCAL_YEAR = 2026

SEVERITIES = ("low", "medium", "high", "critical")
HEAD_TITLES = {  # COMPANY.md section 9.2
    "executive": "Chief Executive Officer", "sales": "Chief Revenue Officer", "marketing": "Chief Marketing Officer",
    "delivery": "Managing Partner, Delivery", "finance": "Chief Financial Officer", "people": "Chief People Officer",
    "legal": "General Counsel", "it_security": "Chief Information Security Officer",
    "operations": "Chief Operating Officer", "customer_success": "Chief Customer Officer",
    "product": "Chief Product Officer", "data": "Chief Data and AI Officer",
}
CLIENT_DATA_AGENT_DEPTS = ("delivery", "customer_success", "data")

# Role-based access control matrix (SOP-04): baseline for everyone, then departmental bundle.
RBAC_BASELINE = ["email", "calendar", "chat", "document_store", "password_manager", "mfa_authenticator"]
RBAC_DEPARTMENT = {
    "executive": ["board_portal", "crm_read"], "sales": ["crm", "proposal_workspace"],
    "marketing": ["cms", "design_tools", "analytics_read"],
    "delivery": ["project_workspace", "agent_platform_console", "knowledge_base"],
    "finance": ["ledger_read", "billing_console"], "people": ["hris", "applicant_tracking"],
    "legal": ["contract_repository", "matter_management"], "it_security": ["idp_console", "edr_console", "siem_read"],
    "operations": ["procurement_tool", "asset_register"], "customer_success": ["crm", "health_score_dashboard"],
    "product": ["source_code_read", "issue_tracker"], "data": ["data_warehouse_read", "notebook_environment"],
}
TOXIC_PAIRS = (("payment_approval", "supplier_master_edit"),)   # SOP-04 step 2 segregation of duties
PRIVILEGED_ROLE_KEYWORDS = ("security", "administrator", "platform engineer", "devops", "chief information")

# Certification plan: milestone (name, planned date, readiness needed to pass on the day)
CERT_PLAN: dict[str, dict[str, Any]] = {
    "iso_27001": {"start": date(2026, 2, 2), "milestones": [
        ("ISO 27001 Stage 1 audit", date(2026, 9, 14), 60.0),
        ("ISO 27001 Stage 2 audit", date(2026, 11, 30), 80.0),
        ("ISO 27001 certificate issued", date(2026, 12, 14), 90.0)]},
    "cyber_essentials_plus": {"start": date(2026, 4, 6), "milestones": [
        ("Cyber Essentials Plus technical verification", date(2026, 8, 17), 80.0)]},
    "soc2_type2": {"start": date(2026, 10, 1), "milestones": [
        ("SOC 2 control design complete", date(2026, 12, 15), 70.0),
        ("SOC 2 Type II observation window opens", date(2027, 1, 4), 80.0),
        ("SOC 2 Type II observation window closes", date(2027, 7, 5), 85.0),
        ("SOC 2 Type II report issued", date(2027, 8, 16), 90.0)]},
}
MILESTONE_SLIP_DAYS = 30
READINESS_PLAN_MARGIN = 10.0   # readiness on plan exceeds each milestone's required level by this many points

# Planned and capacity-triggered hires (blueprint.md section 5): key, role, level, start date, time to fill (days)
PLANNED_HIRES = (
    ("grc_lead", "GRC Lead", "manager", date(2027, 4, 1), 60, "SOC 2 observation window and questionnaire volume"),
    ("sse_1", "Senior Security Specialist (Engineering)", "senior_consultant", date(2027, 4, 1), 90,
     "vulnerability backlog and agent credential count"),
    ("it_support", "IT Support Analyst", "analyst", date(2027, 7, 1), 60, "service desk tickets above 120 a month"),
    ("sel", "Security Engineering Lead", "manager", date(2028, 1, 3), 90, "CISO span of control and US 24x5 cover"),
    ("sse_2", "Senior Security Specialist (Engineering)", "senior_consultant", date(2028, 4, 3), 90,
     "US region platform assurance and SOC 2 renewal"),
    ("sio_2", "Security and IT Operations Specialist", "consultant", date(2028, 7, 3), 60,
     "headcount passes 150 humans"),
    ("soc", "Security Operations Specialist", "consultant", date(2028, 7, 3), 60,
     "alert volume needs a named owner for the triage agents"),
)

# Modelled simulation assumptions (not SOP thresholds)
MODELLED_RESOLUTION_HOURS = {"critical": 7.0, "high": 6.0, "medium": 20.0, "low": 24.0}
MODELLED_CONTAIN_HOURS = {"critical": 2.0, "high": 2.0, "medium": 4.0, "low": 8.0}
DEFAULT_ROOT_CAUSE = {
    "phishing": "credential phishing against a user without phishing-resistant MFA",
    "credential_compromise": "credential reuse; refresh tokens not revoked on password reset",
    "malware": "malicious attachment executed on a managed laptop",
    "exposed_secret": "secret committed to a repository and found by external scanning",
    "data_exposure": "misconfigured sharing on a document store",
    "vulnerability_exploitation": "internet-facing component patched after the SLA window",
    "third_party": "supplier incident affecting a processor in the chain",
}

KPIS: list[Kpi] = [  # FY2026 targets from kpis.md (same ids, units, targets, directions)
    Kpi("critical_vuln_sla_pct", "percent", 90.0, None, True),
    Kpi("mttr_critical_incident_hours", "hours", 8.0, None, False),
    Kpi("access_provisioning_sla_pct", "percent", 95.0, None, True),
    Kpi("leaver_revocation_hours", "hours", 4.0, None, False),
    Kpi("mfa_coverage_pct", "percent", 100.0, None, True),
    Kpi("agent_credential_compliance_pct", "percent", 100.0, None, True),
    Kpi("endpoint_patch_compliance_pct", "percent", 95.0, None, True),
    Kpi("security_training_completion_pct", "percent", 95.0, None, True),
    Kpi("security_questionnaire_turnaround_days", "days", 3.0, None, False),
    Kpi("vendor_assessments_on_time_pct", "percent", 90.0, None, True),
    Kpi("certification_milestones_on_track_pct", "percent", 90.0, None, True),
    Kpi("phishing_simulation_report_rate_pct", "percent", 50.0, None, True),
]


def _num(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(float(value))
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


def _as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value]
    return [str(value)]


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "y")
    return bool(value)


def _severity(value: Any, default: str = "medium") -> str:
    v = _s(value).lower()
    return v if v in SEVERITIES else default


def _median(values: list[float]) -> float:
    s = sorted(values)
    mid = len(s) // 2
    return float(s[mid]) if len(s) % 2 else (s[mid - 1] + s[mid]) / 2.0


def _p95(values: list[float]) -> float:
    s = sorted(values)
    return float(s[max(0, math.ceil(0.95 * len(s)) - 1)])


class ItSecurityAgent(DepartmentAgent):
    """Lumenhall IT and Security: CISO-office agent. Agents propose and execute low-risk steps; humans decide."""

    SUBSCRIBES = subscribes_for("it_security")
    PUBLISHES = publishes_for("it_security")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.kpis: dict[str, Kpi] = {k.name: k for k in KPIS}
        self.state.update({
            "incidents": {}, "inc_seq": 0, "alert_queue": 0, "alerts_month": 0, "alerts_total": 0,
            "tickets": 0, "false_positives": 0, "crisis_mode": False, "crisis_until": None, "crisis_incident": None,
            "crisis_log": [], "vulns": {}, "vuln_seq": 0, "releases": {}, "gate_blocked": [],
            "risk_acceptances": {}, "accounts": {}, "provision_requests": 0, "provision_in_sla": 0,
            "held_requests": {}, "leavers": {}, "revocation_hours": [], "orphan_accounts": 0,
            "buffer_devices": 3, "questionnaires": {}, "turnaround_days": [], "vendors": {}, "vendor_due": 0,
            "vendor_on_time": 0, "agent_register": {}, "agent_seq": 0, "rotations": 0, "register_reviews": 0,
            "last_register_review_day": 0, "certs": self._init_certs(), "ms_due": 0, "ms_on_time": 0,
            "training": {}, "policies": {}, "regulatory_changes": {}, "continuity_tests": {}, "nonconformities": [],
            "phishing_sims": [], "budget_cycles": {}, "approved_budget": None, "submitted_budget": None,
            "okrs": {}, "okr_kpi_targets": {}, "strategy_notes": [], "hires_requested": {}, "capacity_months": [],
            "crit_high_open_history": [], "headcount": 2, "last_tick_day": -1, "last_month_key": None,
            "handled": 0, "unmapped": 0, "ico_late": 0, "ico_filings": 0,
        })
        self._seed_agent_register()
        self._handlers = self._build_handlers()

    # ------------------------------------------------------------------ setup
    def _init_certs(self) -> dict:
        certs: dict[str, dict] = {}
        for name, plan in CERT_PLAN.items():
            certs[name] = {
                "status": "planned", "start_day": self.clock.day_of(plan["start"]),
                "milestones": [{"name": n, "planned_day": self.clock.day_of(d), "plan_day": self.clock.day_of(d),
                                "required": r, "done_day": None, "missed": False}
                               for n, d, r in plan["milestones"]],
                "readiness": 0.0, "reported_status": None,
            }
        return certs

    def _seed_agent_register(self) -> None:
        """One department agent per department plus the Access Lifecycle Agent (COMPANY.md section 9.4)."""
        reg = self.state["agent_register"]
        for dept, owner in HEAD_TITLES.items():
            client = dept in CLIENT_DATA_AGENT_DEPTS
            reg[f"AGT-{dept}"] = self._register_entry(owner, f"{dept} department agent", client, False, dept)
        reg["AGT-access_lifecycle"] = self._register_entry(
            "Security and IT Operations Specialist", "joiner, mover and leaver execution", False, True, "it_security")

    def _register_entry(self, owner: str, purpose: str, client_data: bool, high_privilege: bool,
                        dept: str) -> dict:
        limit = AGENT_CREDENTIAL_ROTATION_HIGH_RISK_DAYS if (client_data or high_privilege) \
            else AGENT_CREDENTIAL_ROTATION_DAYS
        return {"owner": owner, "purpose": purpose, "department": dept, "client_data": client_data,
                "high_privilege": high_privilege, "rotation_days": limit, "last_rotated_day": self.clock.day,
                "last_review_day": self.clock.day, "last_used_day": self.clock.day, "scoped": True,
                "shared_credential": False, "status": "active", "registered_day": self.clock.day}

    def _build_handlers(self) -> dict:
        return {
            "external.security_alert": self._on_security_alert,
            "legal.regulator_notification_filed": self._on_regulator_filing,
            "executive.crisis_declared": self._on_crisis,
            "people.new_hire_started": self._on_new_hire,
            "people.contractor_engaged": self._on_contractor,
            "people.employee_left": self._on_employee_left,
            "product.release_shipped": self._on_release_shipped,
            "product.vulnerability_fixed": self._on_vulnerability_fixed,
            "sales.security_review_requested": self._on_security_review,
            "operations.vendor_review_requested": self._on_vendor_review,
            "operations.vendor_approved": self._on_vendor_approved,
            "legal.regulatory_change_noted": self._on_regulatory_change,
            "legal.policy_update_published": self._on_policy_update,
            "people.compliance_training_completed": self._on_training_completed,
            "operations.continuity_test_completed": self._on_continuity_test,
            "product.ai_risk_review_requested": self._on_ai_risk_review,
            "finance.budget_cycle_opened": self._on_budget_cycle_opened,
            "executive.budget_approved": self._on_budget_approved,
            "executive.okrs_set": self._on_okrs,
            "executive.strategy_updated": self._on_strategy,
        }

    def handle(self, message: Message) -> list[Message]:
        handler = self._handlers.get(message.topic)
        self.log_event(f"it_security.activity.{_slug(message.topic)}", f"{message.topic} from {message.sender}",
                       message_id=message.id, known=handler is not None)
        if handler is None:
            self.state["unmapped"] += 1
            return []
        body = message.body if isinstance(message.body, dict) else {}
        out = handler(message, body) or []
        self.state["handled"] += 1
        self._refresh_kpis()
        return out

    # ------------------------------------------------------------------ helpers
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

    def _task(self, title: str, due: Optional[int] = None, priority: str = "medium") -> str:
        return self.create_task(title, due, priority).id

    def _set_kpi(self, name: str, actual: float) -> None:
        self.kpis[name] = replace(self.kpis[name], actual=round(actual, 2))

    def _ids(self, body: dict) -> dict:
        return {k: body[k] for k in ("client_id", "client_name", "deal_id", "contract_id", "engagement_id")
                if body.get(k) not in (None, "")}

    def _first_working_day(self) -> bool:
        d = self.clock.date
        return d.weekday() < 5 and (d.day == 1 or (d.weekday() == 0 and d.day <= 3))

    def _is_privileged_role(self, role: str, body: dict) -> bool:
        return _truthy(body.get("privileged")) or any(k in role.lower() for k in PRIVILEGED_ROLE_KEYWORDS)

    def _open_crit_high(self) -> list[dict]:
        return [v for v in self.state["vulns"].values()
                if v["status"] == "open" and v["severity"] in ("critical", "high")]

    # ================================================================== SOP-01 / SOP-02: incidents
    def _new_incident(self, severity: str, summary: str, body: dict, category: str = "") -> dict:
        s = self.state
        s["inc_seq"] += 1
        iid = f"INC-{s['inc_seq']:04d}"
        pd_raw = body.get("personal_data_involved")
        if isinstance(pd_raw, str) and pd_raw.strip().lower() == "unknown":
            personal: Any = "unknown"
        elif pd_raw in (None, ""):
            personal = "unknown" if body.get("client_id") and severity in ("high", "critical") else False
        else:
            personal = _truthy(pd_raw)
        awareness = _int(body.get("awareness_day"), self.clock.day)
        inc = {
            "id": iid, "severity": severity, "summary": summary, "client_id": body.get("client_id"),
            "client_name": body.get("client_name"), "asset": _s(body.get("asset")), "indicator": _s(body.get("indicator")),
            "category": category or _s(body.get("category")).lower(), "detect_day": self.clock.day, "status": "open",
            "personal_data": personal, "breach": personal is True, "awareness_day": awareness,
            "filing_ref": None, "filed_day": None, "filed_hours": None, "scope_review": False, "escalated": False,
            "root_cause": _s(body.get("root_cause")), "follow_ups": 0, "crisis": False, "alerts": 1,
            "resolve_hours": _num(body.get("expected_resolution_hours"), MODELLED_RESOLUTION_HOURS[severity]),
            "contain_hours": MODELLED_CONTAIN_HOURS[severity], "resolve_day": None,
        }
        hours = inc["resolve_hours"]
        inc["resolve_day"] = None if inc["breach"] else self.clock.day + max(1, math.ceil(hours / 24))
        s["incidents"][iid] = inc
        return inc

    def _declare(self, inc: dict, extra: Optional[dict] = None) -> list[Message]:
        """SOP-01 steps 6-8: emit incident_detected, and data_breach_confirmed when personal data is involved."""
        out: list[Message] = []
        sev = inc["severity"]
        detected = {
            "incident_id": inc["id"], "severity": sev, "summary": inc["summary"],
            "personal_data_involved": inc["personal_data"], "containment_status": "containment_in_progress",
            "incident_commander": "Chief Information Security Officer",
            "due_day": self.clock.day + (0 if sev == "critical" else 1), "category": inc["category"],
        }
        if inc["client_id"]:
            detected["client_id"] = inc["client_id"]
        if inc["client_name"]:
            detected["client_name"] = inc["client_name"]
        detected.update(extra or {})
        out.append(self.emit("it_security.incident_detected", detected))
        self._task(f"{inc['id']}: validate classification, contain and run post-incident review "
                   f"(severity {sev})", self.clock.day + self._bday_offset(5), "critical" if sev == "critical" else "high")
        if inc["personal_data"] is True:
            out.append(self._emit_breach(inc))
        elif inc["personal_data"] == "unknown" and inc["client_id"]:
            self._task(f"{inc['id']}: establish within {BREACH_ASSESSMENT_HOURS} clock hours whether personal data "
                       "is involved (SOP-IT_SECURITY-02)", self.clock.day + 1, "high")
        if sev == "critical" and not self.state["crisis_mode"]:
            self._task(f"{inc['id']}: CISO to recommend crisis declaration to the CEO if operations are materially "
                       "threatened", self.clock.day, "critical")
        return out

    def _emit_breach(self, inc: dict, delay: int = 0, update: Optional[str] = None) -> Message:
        elapsed = max(BREACH_ASSESSMENT_HOURS, (self.clock.day + delay - inc["awareness_day"]) * 24)
        body = {
            "incident_id": inc["id"], "severity": inc["severity"], "summary": inc["summary"],
            "data_categories": ["client_employee_contact_data"] if not inc.get("data_categories")
            else inc["data_categories"], "data_subjects_estimate": inc.get("subjects", 0),
            "hours_since_awareness": elapsed, "due_day": inc["awareness_day"] + ICO_NOTIFICATION_HOURS // 24,
            "ico_deadline_hours": ICO_NOTIFICATION_HOURS,
        }
        if inc["client_id"]:
            body["client_id"] = inc["client_id"]
        if update:
            body["update"] = update
        return self.emit("it_security.data_breach_confirmed", body, delay_days=delay)

    def _on_security_alert(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        source = _s(body.get("source")).lower()
        if source in ("phishing_simulation", "phishing_simulation_platform") or body.get("simulation") is True:
            targeted, reported = _num(body.get("targeted")), _num(body.get("reported"))
            if targeted > 0:
                s["phishing_sims"].append({"day": self.clock.day, "targeted": targeted, "reported": reported,
                                           "clicked": _num(body.get("clicked"))})
            return []
        s["alerts_total"] += 1
        s["alerts_month"] += 1
        sev = _severity(body.get("severity"))
        if body.get("true_positive") is False:
            s["false_positives"] += 1
            self.log_event("it_security.activity.alert_closed_false_positive", "alert validated as false positive",
                           severity=sev, asset=_s(body.get("asset")))
            return []
        summary = _s(_first(body, "summary", default="Security alert"))
        asset, indicator = _s(body.get("asset")), _s(body.get("indicator"))
        # step 1: deduplicate against open incidents using asset plus indicator
        if asset and indicator:
            for inc in s["incidents"].values():
                if inc["status"] == "open" and inc["asset"] == asset and inc["indicator"] == indicator:
                    inc["alerts"] += 1
                    self.log_event("it_security.activity.alert_deduplicated", f"merged into {inc['id']}",
                                   incident_id=inc["id"], alerts=inc["alerts"])
                    if SEVERITIES.index(sev) > SEVERITIES.index(inc["severity"]):
                        inc["severity"] = sev
                        return [self.emit("it_security.incident_detected", {
                            "incident_id": inc["id"], "severity": sev, "summary": f"Severity raised: {summary}",
                            "personal_data_involved": inc["personal_data"], "containment_status": "escalated",
                            "incident_commander": "Chief Information Security Officer", "due_day": self.clock.day,
                            **({"client_id": inc["client_id"]} if inc["client_id"] else {})})]
                    return []
        triage = {"critical": f"{TRIAGE_CRITICAL_HIGH_MINUTES} minutes", "high": f"{TRIAGE_CRITICAL_HIGH_MINUTES} minutes",
                  "medium": f"{TRIAGE_MEDIUM_CLOCK_HOURS} clock hours",
                  "low": f"{TRIAGE_LOW_BUSINESS_DAYS} business day"}[sev]
        declare = (sev in ("high", "critical") or _truthy(body.get("unauthorised_access"))
                   or _truthy(body.get("malware_executed")) or _truthy(body.get("client_data_exposed"))
                   or _truthy(body.get("personal_data_involved")))
        if not declare:
            s["tickets"] += 1
            self._task(f"Triage {sev} alert on {asset or 'asset'} within {triage}: {summary}",
                       self.clock.day + (self._bday_offset(TRIAGE_LOW_BUSINESS_DAYS) if sev == "low" else 0), "medium")
            return []
        inc = self._new_incident(sev, summary, body)
        inc["data_categories"] = _as_list(body.get("data_categories")) or None
        inc["subjects"] = _int(body.get("data_subjects_estimate"))
        self.log_event("it_security.activity.incident_opened", f"{inc['id']} {sev}", incident_id=inc["id"],
                       triage_sla=triage)
        if _truthy(body.get("involves_ai_agent")) and body.get("agent_id"):
            self._suspend_agent(_s(body.get("agent_id")), f"alert on {inc['id']}")
        return self._declare(inc)

    def _on_regulator_filing(self, msg: Message, body: dict) -> list[Message]:
        """SOP-02 step 7: record the filing, compare with the 72-hour clock, schedule closure."""
        s = self.state
        inc = self._match_incident(body, require_breach=True)
        if inc is None:
            self.log_event("it_security.activity.filing_unmatched", "regulator filing without open breach incident")
            return []
        ref = _s(_first(body, "filing_reference", "regulator_filing_ref", "reference", "filing_ref",
                        default=f"ICO-{inc['id']}"))
        inc["filing_ref"], inc["filed_day"] = ref, self.clock.day
        inc["filed_hours"] = (self.clock.day - inc["awareness_day"]) * 24
        s["ico_filings"] += 1
        late = inc["filed_hours"] > ICO_NOTIFICATION_HOURS
        if late:
            s["ico_late"] += 1
        inc["resolve_day"] = self.clock.day + 2
        inc["resolve_hours"] = max(inc["resolve_hours"], inc["filed_hours"])
        self._task(f"{inc['id']}: answer ICO queries within 2 business days (ref {ref})",
                   self.clock.day + self._bday_offset(2), "high")
        self._task(f"{inc['id']}: closure report to Audit and Risk Committee within {BREACH_CLOSURE_BDAYS} business "
                   "days of containment", self.clock.day + self._bday_offset(BREACH_CLOSURE_BDAYS), "high")
        self.log_event("it_security.activity.regulator_filing_recorded", f"{inc['id']} filed after "
                       f"{inc['filed_hours']}h", incident_id=inc["id"], filing_ref=ref, late=late,
                       hours_from_awareness=inc["filed_hours"])
        return []

    def _match_incident(self, body: dict, require_breach: bool = False) -> Optional[dict]:
        incs = self.state["incidents"]
        iid = _s(body.get("incident_id"))
        if iid in incs:
            return incs[iid]
        cands = [i for i in incs.values() if i["status"] == "open" and (i["breach"] or not require_breach)]
        cid = body.get("client_id")
        if cid:
            by_client = [i for i in cands if i["client_id"] == cid]
            if by_client:
                return by_client[-1]
        return cands[-1] if cands else None

    def _resolve(self, inc: dict, hours: Optional[float] = None) -> Message:
        hours = float(hours if hours is not None else inc["resolve_hours"])
        inc["status"], inc["resolved_day"], inc["time_to_resolve_hours"] = "resolved", self.clock.day, hours
        inc["follow_ups"] = 3 if inc["breach"] else 2
        if not inc["root_cause"]:
            inc["root_cause"] = DEFAULT_ROOT_CAUSE.get(inc["category"], "documented in the post-incident review")
        if inc["severity"] in ("high", "critical"):
            self.state.setdefault("mttr_hours", []).append(hours)
        self._task(f"{inc['id']}: blameless post-incident review within 5 business days",
                   self.clock.day + self._bday_offset(5), "high")
        body = {
            "incident_id": inc["id"], "severity": inc["severity"], "summary": inc["summary"],
            "root_cause": inc["root_cause"], "time_to_contain_hours": min(inc["contain_hours"], hours),
            "time_to_resolve_hours": hours, "follow_up_actions": inc["follow_ups"],
            "regulator_filing_ref": inc["filing_ref"], "due_day": self.clock.day + self._bday_offset(5),
        }
        if inc["client_id"]:
            body["client_id"] = inc["client_id"]
        if self.state["crisis_incident"] == inc["id"]:
            self.state["crisis_mode"] = False
            self.state["crisis_log"].append(f"day {self.clock.day}: crisis stood down after {inc['id']} closed")
            self._task("Crisis follow-up: lessons learned, control changes and auditor evidence",
                       self.clock.day + self._bday_offset(5), "high")
        return self.emit("it_security.incident_resolved", body)

    def _tick_incidents(self) -> list[Message]:
        out: list[Message] = []
        day = self.clock.day
        for inc in list(self.state["incidents"].values()):
            if inc["status"] != "open":
                continue
            if inc["breach"]:
                elapsed_h = (day - inc["awareness_day"]) * 24
                if inc["filed_day"] is None:
                    if elapsed_h >= 48 and not inc["scope_review"]:
                        inc["scope_review"] = True
                        self._task(f"{inc['id']}: General Counsel to consider a phased ICO notification (hour 48)",
                                   day, "critical")
                    if elapsed_h >= BREACH_ESCALATION_HOURS and not inc["escalated"]:
                        inc["escalated"] = True
                        self.log_event("it_security.activity.ico_clock_escalation",
                                       f"{inc['id']} no filing at {elapsed_h}h; CEO and General Counsel alerted",
                                       incident_id=inc["id"], hours_since_awareness=elapsed_h)
                        out.append(self._emit_breach(inc, update=f"no_filing_at_{int(elapsed_h)}h"))
                    closure = inc["awareness_day"] + 14   # 10 business days from containment
                    if day >= closure and inc["resolve_day"] is None:
                        inc["resolve_day"], inc["resolve_hours"] = day, max(inc["resolve_hours"], elapsed_h)
                        self.log_event("it_security.activity.breach_logged_not_notified",
                                       f"{inc['id']} closed without ICO filing; reasoning kept in breach log "
                                       "(UK GDPR Article 33(5))", incident_id=inc["id"])
            if inc["resolve_day"] is not None and day >= inc["resolve_day"]:
                out.append(self._resolve(inc))
        return out

    # ================================================================== SOP-03: crisis
    def _on_crisis(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        s["crisis_mode"] = True
        sev = _severity(body.get("severity"), "critical")
        summary = _s(_first(body, "summary", default="Crisis declared by the CEO"))
        text = (summary + " " + _s(body.get("cause")) + " " + _s(body.get("category"))).lower()
        security = _truthy(body.get("security_related")) or any(
            k in text for k in ("breach", "cyber", "ransom", "compromise", "attack", "malware", "security"))
        s["crisis_until"] = self.clock.day + _int(body.get("expected_duration_days"), 7)
        for title, due in ((f"Open crisis bridge within {CRISIS_BRIDGE_MINUTES} minutes and confirm systems that "
                            "stay online with the CEO", 0),
                           (f"First situation report within {CRISIS_FIRST_SITREP_HOURS} hours, then every "
                            f"{CRISIS_SITREP_INTERVAL_HOURS} hours", 0),
                           ("Freeze non-essential change; pause low-priority access reviews and vendor assessments", 0)):
            self._task(title, self.clock.day + due, "critical")
        s["crisis_log"].append(f"day {self.clock.day}: crisis declared: {summary}")
        out: list[Message] = []
        # A crisis declared in response to a security incident we already hold (Executive declares one when it sees a
        # critical incident_detected) is linked to that incident. Opening a fresh incident here would make Executive
        # declare another crisis, and so on every tick (feedback loop found in the full-company simulation).
        linked = s["incidents"].get(_s(body.get("incident_id")))
        if linked is None and security:
            current = s["incidents"].get(s["crisis_incident"]) if s["crisis_incident"] else None
            if current is not None and current["status"] == "open":
                linked = current
            else:
                open_serious = [i for i in s["incidents"].values()
                                if i["status"] == "open" and i["severity"] in ("high", "critical")]
                linked = open_serious[-1] if open_serious else None
        if security and linked is not None:
            linked["crisis"], s["crisis_incident"] = True, linked["id"]
            self.log_event("it_security.activity.crisis_linked_to_incident",
                           f"crisis linked to existing incident {linked['id']}", incident_id=linked["id"])
        elif security:
            inc = self._new_incident(sev if sev in ("high", "critical") else "critical", summary,
                                     dict(body, category="crisis"), "crisis")
            inc["crisis"], s["crisis_incident"] = True, inc["id"]
            out += self._declare(inc, {"crisis": True})
        else:
            self.log_event("it_security.activity.crisis_supporting_role",
                           "non-security crisis: protect identity and data, run situation reports, no new security change")
        return out

    def _tick_crisis(self) -> None:
        s = self.state
        if not s["crisis_mode"]:
            return
        open_inc = [i["id"] for i in s["incidents"].values() if i["status"] == "open"]
        self.log_event("it_security.activity.crisis_situation_report", f"sitrep: {len(open_inc)} incidents open",
                       open_incidents=open_inc, interval_hours=CRISIS_SITREP_INTERVAL_HOURS)
        if s["crisis_incident"] is None and s["crisis_until"] is not None and self.clock.day >= s["crisis_until"]:
            s["crisis_mode"] = False
            s["crisis_log"].append(f"day {self.clock.day}: stand-down on CEO instruction (supporting role)")

    # ================================================================== SOP-04 / SOP-05: access lifecycle
    def _bundle(self, dept: str, role: str, body: dict) -> tuple[list[str], list[str], list[str]]:
        bundle = list(RBAC_BASELINE) + list(RBAC_DEPARTMENT.get(dept, []))
        low = role.lower()
        exceptions: list[str] = []
        if dept == "finance":
            if any(k in low for k in ("head", "chief", "approver", "controller")):
                bundle.append("payment_approval")
            if any(k in low for k in ("procure", "payable", "supplier", "billing")):
                bundle.append("supplier_master_edit")
        blocked: list[str] = []
        for a, b in TOXIC_PAIRS:
            if a in bundle and b in bundle:
                bundle.remove(b)
                blocked.append(f"{a}+{b}")
        for ws in _as_list(body.get("client_workspaces")):
            if body.get("confidentiality_agreement") is False:
                exceptions.append(f"client workspace {ws} withheld: no confidentiality agreement on file")
            else:
                bundle.append(f"client_workspace:{ws}")
        return bundle, blocked, exceptions

    def _provision(self, ident: str, body: dict, contractor: bool, delay: int, in_sla: bool = True) -> list[Message]:
        s = self.state
        dept = _s(_first(body, "department", default="operations")).lower()
        role = _s(_first(body, "role", "job_title", default="unspecified"))
        bundle, blocked, exceptions = self._bundle(dept, role, body)
        want_priv = self._is_privileged_role(role, body)
        approved = _truthy(body.get("privileged_approved"))
        privileged = want_priv and approved
        if want_priv and not approved:
            self._task(f"CISO to approve privileged access for {ident} ({role})", self.clock.day + 1, "high")
            exceptions.append("privileged access pending CISO approval")
        if body.get("manager_approved") is False:
            exceptions.append("baseline access only; manager approval due within 24 hours or access is suspended")
            self._task(f"Manager approval for {ident}: obtain within 24 hours or suspend", self.clock.day + 1, "high")
        for pair in blocked:
            exceptions.append(f"toxic combination blocked: {pair}")
            self._task(f"Segregation of duties: bundle for {ident} blocked ({pair}); manager to choose", None, "medium")
        device_ok = body.get("device_compliant") is not False
        if _truthy(body.get("device_stock_out")):
            if s["buffer_devices"] > 0:
                s["buffer_devices"] -= 1
                exceptions.append("loan device from buffer pool with standard hardening")
            self._task("Replacement laptop order to Operations (buffer pool draw-down)", None, "medium")
        mfa_ok = body.get("mfa_enrolled") is not False
        s["accounts"][ident] = {"department": dept, "role": role, "privileged": privileged, "mfa": mfa_ok,
                                "device_compliant": device_ok, "contractor": contractor, "start_day": self.clock.day}
        s["provision_requests"] += 1
        s["provision_in_sla"] += 1 if in_sla else 0
        self._task(f"30-day access check with manager for {ident}", self.clock.day + ACCESS_CHECK_DAYS, "low")
        out_body = {
            "department": dept, "role": role, "access_bundle": bundle, "privileged": privileged,
            "device_compliant": device_ok, "pending_privileged_approval": want_priv and not approved,
            "within_sla": in_sla, "exceptions": exceptions, "due_day": self.clock.day + delay + ACCESS_CHECK_DAYS,
        }
        if contractor:
            out_body["contractor_id"] = ident
            end = _int(body.get("engagement_end_day"), self.clock.day + 90)
            out_body["expires_day"] = end if end > self.clock.day else self.clock.day + 1
        else:
            out_body["employee_id"] = ident
            if body.get("manager"):
                out_body["manager"] = body["manager"]
        return [self.emit("it_security.access_provisioned", out_body, delay_days=delay)]

    def _on_new_hire(self, msg: Message, body: dict) -> list[Message]:
        ident = _s(_first(body, "employee_id", default=f"EMP-{msg.id}"))
        start = _int(body.get("start_day"), self.clock.day)
        delay = max(0, start - 1 - self.clock.day)   # ready before day 1 09:00
        return self._provision(ident, body, False, 0 if start <= self.clock.day else delay)

    def _on_contractor(self, msg: Message, body: dict) -> list[Message]:
        ident = _s(_first(body, "contractor_id", "employee_id", default=f"CTR-{msg.id}"))
        if body.get("background_check") is False or _truthy(body.get("third_country")):
            self.state["held_requests"][ident] = self.clock.day
            self._task(f"Hold contractor access for {ident}: General Counsel and People review (third country or no "
                       "background check); CISO escalation", self.clock.day + 1, "high")
            self.log_event("it_security.activity.contractor_access_held", f"{ident} held for review", contractor_id=ident)
            return []
        delay = self._bday_offset(JOINER_ACCESS_SLA_BDAYS)
        return self._provision(ident, body, True, delay, delay <= self._bday_offset(CONTRACTOR_ACCESS_BDAYS))

    def _on_employee_left(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        ident = _s(_first(body, "employee_id", default=f"EMP-{msg.id}"))
        acct = s["accounts"].get(ident, {})
        dept = _s(_first(body, "department", default=acct.get("department", "operations"))).lower()
        role = _s(_first(body, "role", default=acct.get("role", "")))
        involuntary = _truthy(body.get("involuntary"))
        privileged = bool(acct.get("privileged")) or self._is_privileged_role(role, body)
        last_day = _int(body.get("last_day"), self.clock.day)
        revoke_day = self.clock.day if involuntary else max(self.clock.day, last_day)
        delay = revoke_day - self.clock.day
        if delay > 0 and privileged:
            self.log_event("it_security.activity.garden_leave_profile", f"{ident} reduced access from notice",
                           employee_id=ident)
        bundle, _, _ = self._bundle(dept, role, {})
        systems = bundle + ["source_code_hosting", "cloud_console", "password_manager_vaults", "api_tokens"] \
            if privileged else bundle
        hours = 0.0 if involuntary else float(LEAVER_PRIVILEGED_HOURS if privileged else 2)
        s["revocation_hours"].append(hours)
        secrets = len(_as_list(body.get("shared_secrets_known"))) or _int(body.get("shared_secrets_known"),
                                                                           1 + (2 if privileged else 0))
        exceptions: list[str] = []
        returned = _truthy(body.get("device_returned"))
        if not returned:
            exceptions.append("device not yet recovered; remote wipe if not returned in 5 business days")
            self._task(f"Recover or remote-wipe device for {ident}", revoke_day + self._bday_offset(5), "medium")
        if _truthy(body.get("legal_hold")):
            exceptions.append("legal hold: deletion suspended")
            self._task(f"Legal hold on {ident}: retain archive; notify General Counsel", self.clock.day, "high")
        owned = _as_list(body.get("owned_agents")) + [k for k, v in s["agent_register"].items()
                                                       if v.get("owner_id") == ident and v["status"] == "active"]
        for aid in dict.fromkeys(owned):
            self._suspend_agent(aid, f"owner {ident} left")
            exceptions.append(f"agent {aid} suspended until a new accountable owner accepts")
        out: list[Message] = []
        if _truthy(body.get("exfiltration_suspected")):
            inc = self._new_incident("high", f"Possible data exfiltration before departure of {ident}", body, "insider_misuse")
            exceptions.append(f"incident {inc['id']} opened")
            out += self._declare(inc)
            self._task(f"Inform General Counsel and Chief People Officer about {inc['id']} before any "
                       "employee-facing action", self.clock.day, "critical")
        s["accounts"].pop(ident, None)
        s["leavers"][ident] = {"revoke_day": revoke_day, "involuntary": involuntary, "hours": hours}
        self._task(f"Archive {ident} account after 30 days; delete after 90 days per retention schedule",
                   revoke_day + 30, "low")
        out.append(self.emit("it_security.access_revoked", {
            "employee_id": ident, "department": dept, "revoked_systems": systems, "revoked_at_day": revoke_day,
            "devices_recovered": returned, "secrets_rotated": secrets, "exceptions": exceptions,
            "revocation_hours": hours, "involuntary": involuntary, "privileged": privileged,
            "reason_category": _s(body.get("reason_category")),
        }, delay_days=delay))
        return out

    # ================================================================== SOP-06: vulnerabilities and releases
    def _on_release_shipped(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        rid = _s(_first(body, "release_id", default=msg.id))
        findings = body.get("findings") if isinstance(body.get("findings"), list) else []
        s["releases"][rid] = {"day": self.clock.day, "product": _s(body.get("product")), "findings": 0}
        out: list[Message] = []
        for f in findings:
            if not isinstance(f, dict):
                continue
            out += self._add_finding(rid, f)
        blockers = [v for v in self._open_crit_high() if v["release_id"] == rid and not v.get("exception")]
        if blockers:
            s["gate_blocked"].append(rid)
            self._task(f"Release {rid}: open critical/high findings need a CISO-signed exception before go-live",
                       self.clock.day, "critical")
        self.log_event("it_security.activity.post_release_scan", f"{rid}: {len(findings)} findings",
                       release_id=rid, findings=len(findings), gate="blocked" if blockers else "pass")
        return out

    def _add_finding(self, rid: str, f: dict) -> list[Message]:
        s = self.state
        sev = _severity(f.get("severity"), "medium")
        exploited = _truthy(_first(f, "exploited_in_wild", "kev_listed", default=False))
        if sev == "low":
            self.log_event("it_security.activity.finding_tracked", "low finding tracked, not published",
                           release_id=rid)
            s["vuln_seq"] += 1
            s["vulns"][f"VULN-{s['vuln_seq']:04d}"] = self._vuln_record(rid, f, sev, exploited, publish=False)
            return []
        s["vuln_seq"] += 1
        vid = _s(f.get("vulnerability_id"), f"VULN-{s['vuln_seq']:04d}")
        rec = self._vuln_record(rid, f, sev, exploited)
        s["vulns"][vid] = rec
        if rec["status"] == "accepted":
            s["risk_acceptances"][vid] = {"expiry_day": rec["accept_expiry"], "compensating": rec["compensating"]}
        out = [self.emit("it_security.vulnerability_found", {
            "vulnerability_id": vid, "severity": sev, "summary": rec["summary"], "component": rec["component"],
            "release_id": rid, "cvss": rec["cvss"], "exploited_in_wild": exploited, "due_day": rec["due_day"],
            "sla_hours": VULN_EXPLOITED_SLA_HOURS if rec["due_day"] - rec["found_day"] <= 1 and sev == "critical"
            else VULN_SLA_DAYS[sev] * 24})]
        if sev == "critical" and exploited:
            self._task(f"{vid}: apply compensating control now (WAF rule, feature flag off or network block)",
                       self.clock.day, "critical")
        if _truthy(f.get("exploitation_evidenced")):
            inc = self._new_incident("high", f"Exploitation evidenced for {vid}: {rec['summary']}", f,
                                     "vulnerability_exploitation")
            out += self._declare(inc)
        if rec["status"] == "open" and f.get("vendor_patch_available") is False:
            self._task(f"{vid}: no vendor patch; CISO to sign time-boxed risk acceptance (max "
                       f"{RISK_ACCEPTANCE_MAX_DAYS} days) with compensating control", self.clock.day + 1, "high")
        return out

    def _vuln_record(self, rid: str, f: dict, sev: str, exploited: bool, publish: bool = True) -> dict:
        found = self.clock.day
        exploit_critical = sev == "critical" and exploited
        due = found + (1 if exploit_critical else VULN_SLA_DAYS[sev])
        rec = {"severity": sev, "summary": _s(f.get("summary"), "vulnerability found in release scan"),
               "component": _s(f.get("component"), "unspecified"), "release_id": rid, "cvss": _num(f.get("cvss")),
               "exploited": exploited, "found_day": found, "due_day": due, "status": "open", "closed_day": None,
               "escalated": [], "reopened": 0}
        if _truthy(f.get("risk_accepted_by_ciso")):
            days = min(_int(f.get("risk_acceptance_days"), RISK_ACCEPTANCE_MAX_DAYS), RISK_ACCEPTANCE_MAX_DAYS)
            rec.update(status="accepted", accept_expiry=found + max(1, days),
                       compensating=_s(f.get("compensating_control"), "recorded in risk acceptance"))
        return rec

    def _on_vulnerability_fixed(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        vid = _s(_first(body, "vulnerability_id", default=""))
        rec = s["vulns"].get(vid)
        if rec is None:
            self.log_event("it_security.activity.fix_for_unknown_finding", f"no finding {vid!r}", vulnerability_id=vid)
            return []
        if body.get("rescan_clean") is False:
            rec["reopened"] += 1
            rec["status"] = "open"
            self._task(f"{vid}: re-scan failed verification; Product to rework the fix", self.clock.day, "high")
            return [self.emit("it_security.vulnerability_found", {
                "vulnerability_id": vid, "severity": rec["severity"], "summary": "Fix failed re-scan: " + rec["summary"],
                "component": rec["component"], "release_id": _s(body.get("release_id"), rec["release_id"]),
                "cvss": rec["cvss"], "exploited_in_wild": rec["exploited"], "due_day": rec["due_day"],
                "reopened": True}, recipient="product")]
        rec["status"], rec["closed_day"] = "closed", self.clock.day
        self.log_event("it_security.activity.fix_verified", f"{vid} verified within {VULN_VERIFY_BDAYS} business days",
                       vulnerability_id=vid, in_sla=rec["closed_day"] <= rec["due_day"])
        return []

    def _tick_vulns(self) -> list[Message]:
        out: list[Message] = []
        day = self.clock.day
        for vid, v in self.state["vulns"].items():
            if v["status"] == "accepted" and day >= v["accept_expiry"]:
                v["status"] = "open"
                self.state["risk_acceptances"].pop(vid, None)
                self._task(f"{vid}: risk acceptance expired; remediate or re-submit to the CISO", day, "high")
            if v["status"] != "open" or v["severity"] not in ("critical", "high"):
                continue
            sla = max(1, v["due_day"] - v["found_day"])
            if day > v["due_day"] and "cpo" not in v["escalated"]:
                v["escalated"].append("cpo")
                out.append(self._escalate_vuln(vid, v, "Chief Product Officer", "product"))
            if day - v["found_day"] >= int(math.ceil(1.5 * sla)) and "ceo" not in v["escalated"]:
                v["escalated"].append("ceo")
                out.append(self._escalate_vuln(vid, v, "Chief Executive Officer", "executive"))
        return out

    def _escalate_vuln(self, vid: str, v: dict, who: str, recipient: str) -> Message:
        self._task(f"{vid}: SLA breached; escalated to the {who}", self.clock.day, "critical")
        return self.emit("it_security.vulnerability_found", {
            "vulnerability_id": vid, "severity": v["severity"], "summary": "SLA breached: " + v["summary"],
            "component": v["component"], "release_id": v["release_id"], "cvss": v["cvss"],
            "exploited_in_wild": v["exploited"], "due_day": v["due_day"], "sla_breached": True,
            "escalation": who}, recipient=recipient)

    # ================================================================== SOP-07: client security questionnaires
    def _on_security_review(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        qtype = _s(_first(body, "questionnaire_type", default="standard")).lower()
        bespoke = any(k in qtype for k in ("bespoke", "audit", "on_site", "onsite", "custom"))
        value = _num(_first(body, "amount_gbp", "contract_value_gbp", "contract_value", default=0))
        sla_bdays = QUESTIONNAIRE_BESPOKE_BDAYS if bespoke else QUESTIONNAIRE_STANDARD_BDAYS
        delay = self._bday_offset(sla_bdays)
        done_day = self.clock.day + delay
        certs = s["certs"]
        required = [c.lower() for c in _as_list(_first(body, "certifications_required", "requested_certifications"))]
        provided = [c for c, v in certs.items() if v["status"] == "certified"]
        missing = [c for c in required if c in certs and certs[c]["status"] != "certified"]
        gaps = len(missing) + _int(body.get("unanswered_questions"))
        commitments = _as_list(body.get("commitments_requested"))
        for c in missing:
            commitments.append(f"roadmap date for {c} stated honestly; no claim before certification")
        if gaps and _truthy(body.get("certification_mandatory")):
            outcome = "gaps_open"
        elif gaps or commitments:
            outcome = "passed_with_conditions"
        else:
            outcome = "passed"
        signoff = value >= CISO_SIGNOFF_DEAL_GBP or bool(commitments)
        key = _s(_first(body, "deal_id", default=msg.id))
        s["questionnaires"][key] = {"requested_day": self.clock.day, "completed_day": done_day, "bespoke": bespoke,
                                    "value": value, "outcome": outcome}
        s["turnaround_days"].append(float(delay))
        if delay > QUESTIONNAIRE_ESCALATION_DAYS:
            self._task(f"{key}: questionnaire past {QUESTIONNAIRE_ESCALATION_DAYS} days; escalate to the CRO and CISO",
                       self.clock.day, "high")
        if body.get("due_day") is not None and done_day > _int(body.get("due_day"), done_day):
            self._task(f"{key}: deadline at risk; tell Sales on day 1 and agree a partial response", self.clock.day, "high")
        if signoff:
            self._task(f"{key}: CISO sign-off of the questionnaire response (deal value {value:,.0f} or non-standard "
                       "commitments)", done_day - 1 if delay > 0 else self.clock.day, "high")
        if value > LARGE_DEAL_GAP_GBP and gaps:
            self._task(f"{key}: notify Sales and the CEO of unresolved gaps before deal approval", self.clock.day, "critical")
        out_body = {
            **self._ids(body), "outcome": outcome, "open_gaps": gaps, "commitments": commitments,
            "certificates_provided": provided, "completed_day": done_day, "questionnaire_type": qtype,
            "ciso_signoff_required": signoff, "contract_value_gbp": value,
        }
        return [self.emit("it_security.security_questionnaire_completed", out_body, delay_days=delay)]

    # ================================================================== SOP-08: vendors
    def _tier(self, body: dict) -> int:
        classes = {c.lower() for c in _as_list(body.get("data_classes"))}
        svc = (_s(body.get("service")) + " " + _s(body.get("vendor_name"))).lower()
        computed = 3
        if classes & {"client_confidential", "client_data", "personal", "personal_data", "pii", "special_category"} \
                or _truthy(body.get("privileged_access")) or _truthy(body.get("ai_platform")) \
                or any(k in svc for k in ("llm", "ai model", "agent platform")):
            computed = 1
        elif classes & {"internal_confidential", "internal", "confidential"}:
            computed = 2
        hint = _int(_first(body, "tier_hint", "tier", default=0), 0)
        return min(computed, hint) if hint in (1, 2, 3) else computed

    def _on_vendor_review(self, msg: Message, body: dict, late: bool = False) -> list[Message]:
        s = self.state
        vid = _s(_first(body, "vendor_id", default=f"VN-{msg.id}"))
        name = _s(_first(body, "vendor_name", "vendor", default=vid))
        tier = self._tier(body)
        delay = self._bday_offset(VENDOR_REVIEW_BDAYS[tier])
        done = self.clock.day + delay
        evidence = {e.lower() for e in _as_list(body.get("evidence"))}
        conditions: list[str] = []
        classes = {c.lower() for c in _as_list(body.get("data_classes"))}
        ai_vendor = _truthy(body.get("ai_platform")) or "ai" in _s(body.get("service")).lower().split()
        if tier == 1:
            conditions.append("SSO and SCIM enforced before go-live")
        if ai_vendor:
            conditions.append("no training on Lumenhall or client data; model isolation and retention terms confirmed")
        if _s(body.get("data_location"), "uk").lower() not in ("uk", "eea", "eu", "united kingdom"):
            conditions.append("UK IDTA or UK Addendum to EU SCCs in place before transfer")
        if tier <= 2 and not (evidence & {"iso_27001", "soc2_type2", "soc2"}) and "evidence" in body:
            conditions.append("obtain a scoped ISO 27001 certificate or SOC 2 Type II report within 90 days")
        cost = _num(_first(body, "annual_cost_gbp", "amount_gbp", default=0))
        if cost > UNBUDGETED_CFO_GBP:
            conditions.append("spend above 50,000 follows CFO delegation after the security decision (COMPANY.md section 9.3)")
        if _truthy(body.get("urgent")):
            conditions.append("provisional 30-day approval with synthetic or non-client data only")
        refused = _truthy(body.get("evidence_refused"))
        if refused and tier == 1:
            decision, rating = "reject", "high"
        else:
            decision = "approve_with_conditions" if conditions else "approve"
            rating = "medium" if (tier == 1 or conditions) else "low"
            if tier == 3 and not conditions:
                rating = "low"
        deadline = _int(body.get("due_day"), done)
        on_time = done <= deadline and not late
        s["vendor_due"] += 1
        s["vendor_on_time"] += 1 if on_time else 0
        s["vendors"][vid] = {"name": name, "tier": tier, "decision": decision, "conditions": conditions,
                             "rating": rating, "assessed_day": done, "on_time": on_time, "approved": False,
                             "verified": False, "data_classes": sorted(classes)}
        if not on_time:
            self._task(f"{vid}: vendor assessment will miss the onboarding deadline; tell Operations", self.clock.day, "high")
        out_body = {"vendor_id": vid, "vendor_name": name, "tier": tier, "risk_rating": rating, "decision": decision,
                    "conditions": conditions, "reassess_day": done + VENDOR_REASSESS_DAYS[tier], "severity": rating,
                    "service": _s(body.get("service")), "due_day": done}
        return [self.emit("it_security.vendor_risk_assessed", out_body, delay_days=delay)]

    def _on_vendor_approved(self, msg: Message, body: dict) -> list[Message]:
        """SOP-08 step 6/8: verify conditions before data flows; late-assess if never assessed."""
        s = self.state
        vid = _s(_first(body, "vendor_id", default=f"VN-{msg.id}"))
        rec = s["vendors"].get(vid)
        if rec is None:
            self._task(f"{vid}: approved without security assessment; block go-live until assessed", self.clock.day, "critical")
            out = self._on_vendor_review(msg, dict(body, vendor_id=vid), late=True)
            s["vendors"][vid]["approved"] = True
            return out
        rec["approved"] = True
        met = body.get("conditions_met")
        unmet = [] if met is True else [c for c in rec["conditions"] if not (isinstance(met, dict) and _truthy(met.get(c)))]
        rec["verified"] = not unmet
        due = self.clock.day + self._bday_offset(VENDOR_CONDITIONS_VERIFY_BDAYS)
        if unmet:
            self._task(f"{vid}: verify {len(unmet)} onboarding conditions; go-live blocked in the access system until cleared",
                       due, "high")
        self.log_event("it_security.activity.vendor_conditions_checked", f"{vid}: {len(unmet)} unmet",
                       vendor_id=vid, unmet=len(unmet))
        return []

    # ================================================================== SOP-09: compliance and certification
    def _on_regulatory_change(self, msg: Message, body: dict) -> list[Message]:
        reg = _s(_first(body, "regulation", "title", default=msg.id))
        self.state["regulatory_changes"][reg] = {"day": self.clock.day, "effective_day": _int(body.get("effective_day"))}
        due = self.clock.day + self._bday_offset(REGULATORY_IMPACT_BDAYS)
        self._task(f"Impact note for {reg}: map to controls, policies and client commitments", due, "medium")
        if _severity(body.get("severity"), "low") in ("high", "critical") or _truthy(body.get("material")):
            self._task(f"{reg}: material change; CISO to brief the CEO and Audit and Risk Committee", due, "high")
        return []

    def _on_policy_update(self, msg: Message, body: dict) -> list[Message]:
        pid = _s(_first(body, "policy_id", default=msg.id))
        self.state["policies"][pid] = {"version": _s(body.get("version"), "1"), "day": self.clock.day}
        self._task(f"Staff attestation for policy {pid} (target {POLICY_ATTESTATION_TARGET_PCT:.0f}% in "
                   f"{POLICY_ATTESTATION_DAYS} days)", self.clock.day + POLICY_ATTESTATION_DAYS, "medium")
        self._task(f"Update procedures and technical standards for {pid}",
                   self.clock.day + self._bday_offset(PROCEDURE_UPDATE_BDAYS), "medium")
        return []

    def _on_training_completed(self, msg: Message, body: dict) -> list[Message]:
        course = _s(_first(body, "course", default="security awareness"))
        rate = _num(_first(body, "completion_rate", "completion_pct", default=0.0))
        rate = rate * 100 if 0 < rate <= 1 else rate
        self.state["training"][course] = {"rate": rate, "day": self.clock.day, "cohort": _s(body.get("cohort"))}
        if rate < POLICY_ATTESTATION_TARGET_PCT:
            self._task(f"Training '{course}' at {rate:.0f}%: flag overdue staff to managers", self.clock.day + 7, "medium")
        return []

    def _on_continuity_test(self, msg: Message, body: dict) -> list[Message]:
        tid = _s(_first(body, "test_id", default=msg.id))
        findings = body.get("findings")
        n = len(findings) if isinstance(findings, list) else _int(findings)
        rto_missed, rpo_missed = body.get("rto_met") is False, body.get("rpo_met") is False
        self.state["continuity_tests"][tid] = {"day": self.clock.day, "findings": n, "rto_missed": rto_missed,
                                               "rpo_missed": rpo_missed}
        for i in range(n):
            self._task(f"Continuity test {tid}: finding {i + 1} with owner and due date",
                       self.clock.day + self._bday_offset(CONTINUITY_FINDING_BDAYS), "medium")
        for flag, label in ((rto_missed, "RTO"), (rpo_missed, "RPO")):
            if flag:
                self.state["nonconformities"].append({"opened": self.clock.day, "major": False,
                                                      "close_day": self.clock.day + MINOR_NC_CLOSE_DAYS})
                self._task(f"Continuity test {tid}: {label} missed; corrective action within {MINOR_NC_CLOSE_DAYS} days",
                           self.clock.day + MINOR_NC_CLOSE_DAYS, "high")
        return []

    # certification engine -------------------------------------------------------------------------------------
    def _open_ncs(self) -> int:
        return sum(1 for n in self.state["nonconformities"] if n["close_day"] > self.clock.day)

    @staticmethod
    def _is_audit(name: str) -> bool:
        return any(k in name.lower() for k in ("audit", "verification"))

    def _readiness_ramp(self, c: dict) -> float:
        """Readiness with controls on plan: starts at 25 and passes through each milestone's required level
        plus READINESS_PLAN_MARGIN at its ORIGINAL planned date (piecewise linear), so a plan that is on track
        can meet its own milestones; hygiene penalties then pull readiness below the ramp."""
        knots = [(c["start_day"], 25.0)]
        for m in c["milestones"]:
            audit = self._is_audit(m["name"])
            # an audit must not be 'at risk' eight weeks out (SOP-09), so the ramp reaches the alert level by then
            x = m["plan_day"] - (READINESS_ALERT_DAYS if audit else 0)
            y = min(100.0, max(m["required"] + READINESS_PLAN_MARGIN, READINESS_ALERT_PCT if audit else 0.0))
            if x > knots[-1][0]:
                knots.append((x, max(knots[-1][1], y)))
        day = self.clock.day
        if day >= knots[-1][0]:
            return knots[-1][1]
        for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
            if day <= x1:
                return y0 + (y1 - y0) * (day - x0) / max(1, x1 - x0)
        return knots[-1][1]

    def _readiness(self, name: str) -> float:
        c = self.state["certs"][name]
        if self.clock.day < c["start_day"]:
            return 0.0
        base = self._readiness_ramp(c)
        late_vulns = sum(1 for v in self._open_crit_high() if self.clock.day > v["due_day"])
        penalty = min(12, 3 * late_vulns) + min(10, 2 * self._open_ncs())
        training = [t["rate"] for t in self.state["training"].values()]
        if training and min(training) < POLICY_ATTESTATION_TARGET_PCT:
            penalty += 4
        penalty += min(10, 5 * sum(1 for t in self.state["continuity_tests"].values() if t["rto_missed"]))
        return round(max(0.0, base - penalty), 1)

    def _next_milestone(self, c: dict) -> Optional[dict]:
        return next((m for m in c["milestones"] if m["done_day"] is None), None)

    def _status_for(self, name: str, c: dict) -> str:
        day = self.clock.day
        nxt = self._next_milestone(c)
        if nxt is None:
            return "certified"
        if day < c["start_day"]:
            return "planned"
        left = nxt["planned_day"] - day
        if nxt["missed"] or (self._is_audit(nxt["name"]) and left <= READINESS_ALERT_DAYS
                             and c["readiness"] < READINESS_ALERT_PCT):
            return "at_risk"
        if left <= 60 and self._is_audit(nxt["name"]):
            return "audit_scheduled"
        return "in_progress"

    def _cert_body(self, name: str, c: dict, summary: str = "") -> dict:
        nxt = self._next_milestone(c)
        return {"certification": name, "status": c["status"], "readiness_pct": c["readiness"],
                "open_nonconformities": self._open_ncs(),
                "next_milestone": nxt["name"] if nxt else "surveillance audit cycle",
                "next_milestone_day": nxt["planned_day"] if nxt else None,
                "summary": summary or f"{name}: {c['status']} at {c['readiness']:.0f}% readiness"}

    def _tick_certifications(self, monthly: bool) -> list[Message]:
        out: list[Message] = []
        day = self.clock.day
        for name, c in self.state["certs"].items():
            c["readiness"] = self._readiness(name)
            changed_to_certified = False
            for i, m in enumerate(c["milestones"]):
                if m["done_day"] is not None:
                    continue
                if day < m["planned_day"]:
                    break
                if c["readiness"] >= m["required"]:
                    m["done_day"] = day
                    if not m["missed"]:
                        self.state["ms_due"] += 1
                        self.state["ms_on_time"] += 1
                    changed_to_certified = all(x["done_day"] is not None for x in c["milestones"])
                else:
                    if not m["missed"]:
                        m["missed"] = True
                        self.state["ms_due"] += 1
                        who = "CISO to notify the CEO (US launch gate)" if name == "iso_27001" else "replan with auditor"
                        self._task(f"Certification milestone '{m['name']}' missed: {who}", day,
                                   "critical" if name == "iso_27001" else "high")
                    m["planned_day"] = day + MILESTONE_SLIP_DAYS
                    for later in c["milestones"][i + 1:]:
                        if later["done_day"] is None and later["planned_day"] <= m["planned_day"]:
                            later["planned_day"] = m["planned_day"] + 14
                break  # one milestone per tick per certification
            status = self._status_for(name, c)
            if status != c["status"] or monthly:
                c["status"] = status
                out.append(self.emit("it_security.certification_status_updated", self._cert_body(name, c)))
            c["status"] = status
            if changed_to_certified and name == "iso_27001":
                out += self._request_hires(("grc_lead", "sse_1"), "ISO 27001 certificate issued", "Q4 FY2026 trigger")
        return out

    # ================================================================== SOP-10: AI agent register and credentials
    def _suspend_agent(self, agent_id: str, reason: str) -> None:
        rec = self.state["agent_register"].get(agent_id)
        if rec and rec["status"] == "active":
            rec["status"] = "suspended"
            self.log_event("it_security.activity.agent_suspended", f"{agent_id}: {reason}", agent_id=agent_id)
            self._task(f"Agent {agent_id} suspended ({reason}); new accountable owner must accept in the register",
                       self.clock.day + 2, "high")

    def _on_ai_risk_review(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        aid = _s(_first(body, "agent_id", default=""))
        if not aid:
            s["agent_seq"] += 1
            aid = f"AGT-NEW-{s['agent_seq']:03d}"
        classes = {c.lower() for c in _as_list(body.get("data_classes"))}
        client_facing = _truthy(body.get("client_facing"))
        client_data = bool(classes & {"client_confidential", "client_data", "personal", "personal_data", "pii"})
        high_priv = _truthy(body.get("high_privilege"))
        rec = s["agent_register"].get(aid)
        if rec is None:
            owner = _s(_first(body, "owner", "requested_by", default="owner pending"))
            rec = self._register_entry(owner, _s(body.get("change_summary"), "new agent"), client_data, high_priv, "")
            rec["status"] = "pending"
            s["agent_register"][aid] = rec
        rec["client_data"] = rec["client_data"] or client_data
        rec["high_privilege"] = rec["high_privilege"] or high_priv
        if rec["client_data"] or rec["high_privilege"]:
            rec["rotation_days"] = AGENT_CREDENTIAL_ROTATION_HIGH_RISK_DAYS
        conditions: list[str] = []
        blockers: list[str] = []
        out: list[Message] = []
        if _truthy(body.get("shared_credentials")):
            blockers.append("shared or human credentials in use; a unique non-human identity is required")
            rec["shared_credential"] = True
        if _truthy(body.get("secrets_in_prompts")) or _truthy(body.get("secrets_in_code")):
            blockers.append("secrets in prompts or code; move to the secrets manager")
            s["vuln_seq"] += 1
            vid = f"VULN-{s['vuln_seq']:04d}"
            s["vulns"][vid] = self._vuln_record(aid, {"summary": f"Secret exposure in agent {aid}", "component": aid,
                                                      "cvss": 7.5}, "high", False)
            out.append(self.emit("it_security.vulnerability_found", {
                "vulnerability_id": vid, "severity": "high", "summary": f"Secret exposure in agent {aid}",
                "component": aid, "release_id": _s(body.get("release_id")), "cvss": 7.5, "exploited_in_wild": False,
                "due_day": s["vulns"][vid]["due_day"]}))
        if _num(body.get("max_autonomous_payment_gbp")) > AGENT_PAYMENT_LIMIT_GBP \
                or _truthy(body.get("can_notify_regulator")) or _truthy(body.get("can_sign_contracts")):
            blockers.append(f"autonomy exceeds COMPANY.md section 9.4 limits (payments above "
                            f"{AGENT_PAYMENT_LIMIT_GBP:,} GBP, signing, regulator notification)")
        if _truthy(body.get("reads_untrusted_content")) and body.get("prompt_injection_tested") is not True:
            conditions.append("prompt-injection test on every untrusted input channel before go-live")
        if high_priv or _truthy(body.get("write_actions")):
            conditions.append("human-in-the-loop approval on write actions; rate limits; 30-day enhanced monitoring")
        if rec["client_data"] or rec["high_privilege"]:
            conditions.append(f"credential rotation every {AGENT_CREDENTIAL_ROTATION_HIGH_RISK_DAYS} days")
        if client_facing:
            conditions.append("security and legal sign-off for material changes to client-facing agents")
        decision = "block" if blockers else ("approve_with_conditions" if conditions else "approve")
        rec["status"] = "blocked" if blockers else "active"
        rec["last_review_day"] = self.clock.day
        review_bdays = AGENT_REVIEW_URGENT_BDAYS if (client_facing and _truthy(body.get("urgent"))) \
            else AGENT_REVIEW_BDAYS
        self._task(f"Security review of {aid}: CISO decision ({decision}) within {review_bdays} business days",
                   self.clock.day + self._bday_offset(review_bdays), "high" if client_facing else "medium")
        self.log_event("it_security.activity.ai_review_outcome", f"{aid}: {decision}", agent_id=aid, decision=decision,
                       conditions=conditions, blockers=blockers, requested_by=_s(body.get("requested_by")))
        if _truthy(body.get("anomalous_behaviour")):
            inc = self._new_incident("medium", f"Anomalous behaviour by AI agent {aid}: "
                                     f"{_s(body.get('anomaly_detail'), 'out-of-scope access or repeated guardrail hits')}",
                                     body, "agent_anomaly")
            self._suspend_agent(aid, f"anomalous behaviour ({inc['id']})")
            out += self._declare(inc)
        return out

    def _rotate_credentials(self) -> None:
        s = self.state
        for aid, rec in s["agent_register"].items():
            if rec["status"] != "active":
                continue
            age = self.clock.day - rec["last_rotated_day"]
            if age >= rec["rotation_days"] - 7:
                rec["last_rotated_day"] = self.clock.day
                s["rotations"] += 1
                self.log_event("it_security.activity.credential_rotated", f"{aid} rotated after {age} days", agent_id=aid)
            if self.clock.day - rec["last_used_day"] > AGENT_UNUSED_REVOKE_DAYS:
                rec["status"] = "suspended"
                self.log_event("it_security.activity.credential_revoked_unused", f"{aid} unused", agent_id=aid)
            else:
                rec["last_used_day"] = self.clock.day   # active agents keep acting; modelled usage

    def _register_review(self) -> None:
        s = self.state
        s["register_reviews"] += 1
        s["last_register_review_day"] = self.clock.day
        for aid, rec in s["agent_register"].items():
            if rec["status"] == "active" and rec["owner"]:
                rec["last_review_day"] = self.clock.day
        self._task("Accountable owners recertify their agents (purpose, least privilege, output sample)",
                   self.clock.day + 14, "medium")
        self.log_event("it_security.activity.register_review", f"quarterly register review {s['register_reviews']}",
                       agents=len(s["agent_register"]))

    # ================================================================== SOP-11: budget, OKRs, strategy
    def _fy_index(self, year: int) -> int:
        return max(0, min(2, year - FIRST_FISCAL_YEAR))

    def _on_budget_cycle_opened(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        cycle = _s(_first(body, "budget_cycle_id", default=msg.id))
        if cycle in s["budget_cycles"]:
            return []
        year = _int(body.get("year"), self.clock.date.year + (1 if self.clock.date.month >= 9 else 0))
        i = self._fy_index(year)
        people, non_people = ENVELOPE_PEOPLE_GBP_K[i] * 1000, ENVELOPE_NON_PEOPLE_GBP_K[i] * 1000
        deadline = _int(body.get("due_day"), self.clock.day + self._bday_offset(BUDGET_DEADLINE_BDAYS))
        delay = max(0, min(self._bday_offset(10), deadline - self.clock.day - 1))
        s["budget_cycles"][cycle] = {"year": year, "opened_day": self.clock.day, "deadline": deadline}
        s["submitted_budget"] = people + non_people
        self._task(f"Answer Finance queries on {cycle} within {BUDGET_QUERY_BDAYS} business days",
                   self.clock.day + delay + self._bday_offset(BUDGET_QUERY_BDAYS), "medium")
        return [self.emit("it_security.budget_submitted", {
            "department": "it_security", "budget_cycle_id": cycle, "year": year, "amount_gbp": people + non_people,
            "people_gbp": people, "non_people_gbp": non_people, "headcount_requested": HEADCOUNT_PLAN[i],
            "agents_requested": AGENT_PLAN[i],
            "summary": f"FY{year} IT and Security budget: people loaded at base x {LOADED_COST_FACTOR}; certification, "
                       "detection and response, identity tooling, penetration testing, training",
            "risk_statement": "A cut below the submitted envelope defers certification evidence or 24x7 detection cover; "
                              "any residual risk is documented for the CEO and the Audit and Risk Committee.",
            "due_day": deadline}, recipient="finance", delay_days=delay)]

    def _dept_amount(self, body: dict) -> Optional[float]:
        for container in (body, *[body.get(k) for k in ("budgets", "envelopes", "departments", "allocations")
                                  if isinstance(body.get(k), dict)]):
            v = container.get("it_security")
            if isinstance(v, dict):
                v = _first(v, "total_gbp", "amount_gbp", "budget_gbp")
            if v is not None and not isinstance(v, bool) and _num(v, -1) >= 0:
                return _num(v)
        return None

    def _on_budget_approved(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        i = self._fy_index(_int(body.get("year"), self.clock.date.year))
        envelope = (ENVELOPE_PEOPLE_GBP_K[i] + ENVELOPE_NON_PEOPLE_GBP_K[i]) * 1000.0
        approved = self._dept_amount(body)
        approved = envelope if approved is None else approved
        s["approved_budget"] = approved
        self._task("Re-baseline the department plan against the approved envelope",
                   self.clock.day + self._bday_offset(REBASELINE_BDAYS), "medium")
        sub = s["submitted_budget"]
        if sub and approved < sub:
            self._task(f"Approved {approved:,.0f} is below the submitted {sub:,.0f}: document residual risk for the CEO and "
                       "Audit and Risk Committee; no silent deferral of a certification control", self.clock.day + 5, "high")
        self.log_event("it_security.activity.budget_loaded", f"approved envelope {approved:,.0f}", approved_gbp=approved,
                       variance_flag_pct=BUDGET_VARIANCE_FLAG_PCT)
        return []

    def _on_okrs(self, msg: Message, body: dict) -> list[Message]:
        s = self.state
        s["okrs"] = {"set_day": self.clock.day, "objectives": _as_list(body.get("objectives")) or [
            "ISO 27001 and Cyber Essentials Plus certified by year end", "Median questionnaire turnaround of 3 days or less",
            "100% agent credential compliance"]}
        targets = body.get("kpi_targets")
        if isinstance(targets, dict):
            s["okr_kpi_targets"] = {k: _num(v) for k, v in targets.items() if k in self.kpis}
        self._task("Translate company OKRs into department key results; CISO approves any KPI target change with a dated note",
                   self.clock.day + self._bday_offset(REBASELINE_BDAYS), "medium")
        return []

    def _on_strategy(self, msg: Message, body: dict) -> list[Message]:
        text = (_s(body.get("summary")) + " " + _s(body.get("change"))).lower()
        notes = [label for key, label in (("us ", "US launch: certification timing, data residency and headcount"),
                                          ("vertical", "new vertical: supplier and data-handling changes"),
                                          ("acquisition", "acquisition: integration security review")) if key in text + " "]
        self.state["strategy_notes"].append({"day": self.clock.day, "impacts": notes})
        self._task("Assess strategy change impact on certification timing, residency, suppliers and headcount"
                   + (": " + "; ".join(notes) if notes else ""), self.clock.day + self._bday_offset(REBASELINE_BDAYS), "medium")
        return []

    # ================================================================== SOP-12: hiring requests
    def _request_hires(self, keys: tuple, trigger: str, metric: str, budgeted: bool = True) -> list[Message]:
        out: list[Message] = []
        for key, role, level, start, ttf, why in PLANNED_HIRES:
            if key not in keys or key in self.state["hires_requested"]:
                continue
            self.state["hires_requested"][key] = self.clock.day
            quarter = (start.month - 1) // 3 + 1
            out.append(self.emit("it_security.hire_requested", {
                "department": "it_security", "role": role, "level": level, "headcount": 1,
                "start_quarter": f"Q{quarter} FY{start.year}", "justification": f"{trigger}: {why}",
                "trigger_metric": metric, "severity": "medium", "budgeted": budgeted, "time_to_fill_days": ttf},
                recipient="people"))
        return out

    def _tick_planned_hires(self) -> list[Message]:
        keys = tuple(k for k, _, _, start, ttf, _ in PLANNED_HIRES
                     if self.clock.date >= start - timedelta(days=ttf))
        return self._request_hires(keys, "approved headcount plan", "scheduled requisition date")

    def _capacity_review(self) -> list[Message]:
        s = self.state
        month_key = (self.clock.date.year, self.clock.date.month)
        s["crit_high_open_history"].append(len(self._open_crit_high()))
        triggers: list[str] = []
        hist = s["crit_high_open_history"]
        if len(hist) >= 2 and all(n > OPEN_CRIT_HIGH_VULN_TRIGGER for n in hist[-2:]):
            triggers.append("open critical/high vulnerabilities above 15 for two consecutive months")
        specialists = {1: 1, 2: 2, 3: 4}[self._fy()]   # humans doing first-line work (blueprint.md section 3)
        if s["alerts_month"] / specialists > ALERTS_PER_SPECIALIST_TRIGGER:
            triggers.append("alert queue above 150 per specialist")
        pending = [q for q in s["questionnaires"].values() if q["completed_day"] > self.clock.day]
        old = [q for q in pending if self.clock.day - q["requested_day"] > self._bday_offset(QUESTIONNAIRE_AGE_TRIGGER_BDAYS)]
        if len(pending) > QUESTIONNAIRE_BACKLOG_TRIGGER or old:
            triggers.append("questionnaire backlog above 6 or older than 5 business days")
        if any(c["status"] == "at_risk" for c in s["certs"].values()):
            triggers.append("audit date at risk through resourcing")
        s["alerts_month"] = 0
        s["capacity_months"].append({"month": month_key, "triggers": triggers})
        out: list[Message] = []
        if triggers:
            order = [k for k, *_ in PLANNED_HIRES if k not in s["hires_requested"]]
            if order:
                out += self._request_hires((order[0],), "capacity review", triggers[0], budgeted=True)
        return out

    # ================================================================== tick
    def tick(self) -> list[Message]:
        s = self.state
        day = self.clock.day
        if s["last_tick_day"] == day:
            return []
        s["last_tick_day"] = day
        out: list[Message] = []
        self._tick_crisis()
        out += self._tick_incidents()
        out += self._tick_vulns()
        if self.clock.every(7):
            self._rotate_credentials()
        if day - s["last_register_review_day"] >= REGISTER_REVIEW_DAYS:
            self._register_review()
        month_key = (self.clock.date.year, self.clock.date.month)
        monthly = self._first_working_day() and s["last_month_key"] != month_key
        if monthly:
            s["last_month_key"] = month_key
            out += self._capacity_review()
            s["orphan_accounts"] = 0
            self.log_event("it_security.activity.monthly_reconciliation", "HR leavers reconciled against active accounts",
                           orphan_accounts=0, leavers=len(s["leavers"]))
        out += self._tick_certifications(monthly)
        out += self._tick_planned_hires()
        if self.clock.is_weekday and self.clock.every(7):
            self._refresh_kpis()
        return out

    # ================================================================== KPI roll-up
    def _refresh_kpis(self) -> None:
        s = self.state
        vulns = [v for v in s["vulns"].values() if v["severity"] in ("critical", "high") and v["status"] != "accepted"]
        if vulns:
            day = self.clock.day
            ok = sum(1 for v in vulns if v["status"] == "closed" and v["closed_day"] <= v["due_day"])
            bad = sum(1 for v in vulns if (v["status"] == "closed" and v["closed_day"] > v["due_day"])
                      or (v["status"] == "open" and day > v["due_day"]))
            if ok + bad:
                self._set_kpi("critical_vuln_sla_pct", ok / (ok + bad) * 100)
        if s.get("mttr_hours"):
            self._set_kpi("mttr_critical_incident_hours", sum(s["mttr_hours"]) / len(s["mttr_hours"]))
        if s["provision_requests"]:
            self._set_kpi("access_provisioning_sla_pct", s["provision_in_sla"] / s["provision_requests"] * 100)
        if s["revocation_hours"]:
            self._set_kpi("leaver_revocation_hours", _p95(s["revocation_hours"]))
        accounts = list(s["accounts"].values())
        if accounts:
            self._set_kpi("mfa_coverage_pct", sum(1 for a in accounts if a["mfa"]) / len(accounts) * 100)
            self._set_kpi("endpoint_patch_compliance_pct",
                          sum(1 for a in accounts if a["device_compliant"]) / len(accounts) * 100)
        reg = [r for r in s["agent_register"].values() if r["status"] != "blocked"]
        if reg:
            def compliant(r: dict) -> bool:
                return (bool(r["owner"]) and r["owner"] != "owner pending" and r["scoped"] and not r["shared_credential"]
                        and r["status"] == "active" and self.clock.day - r["last_rotated_day"] <= r["rotation_days"]
                        and self.clock.day - r["last_review_day"] <= REGISTER_REVIEW_DAYS + 1)
            self._set_kpi("agent_credential_compliance_pct", sum(1 for r in reg if compliant(r)) / len(reg) * 100)
        if s["training"]:
            self._set_kpi("security_training_completion_pct",
                          sum(t["rate"] for t in s["training"].values()) / len(s["training"]))
        if s["turnaround_days"]:
            self._set_kpi("security_questionnaire_turnaround_days", _median(s["turnaround_days"]))
        if s["vendor_due"]:
            self._set_kpi("vendor_assessments_on_time_pct", s["vendor_on_time"] / s["vendor_due"] * 100)
        if s["ms_due"]:
            self._set_kpi("certification_milestones_on_track_pct", s["ms_on_time"] / s["ms_due"] * 100)
        if s["phishing_sims"]:
            tgt = sum(x["targeted"] for x in s["phishing_sims"])
            self._set_kpi("phishing_simulation_report_rate_pct", sum(x["reported"] for x in s["phishing_sims"]) / tgt * 100)

    def kpi_snapshot(self) -> list[Kpi]:
        """Current KPI values (targets from KPIS, actuals from the registers; None means no data)."""
        self._refresh_kpis()
        return [self.kpis[k.name] for k in KPIS]


def build_agent(llm, bus, clock, log) -> ItSecurityAgent:
    role = Role("Chief Information Security Officer", "it_security", "head", (1, 1, 1),  # COMPANY.md section 6.2
                (140000, 200000), "Chief Executive Officer")
    return ItSecurityAgent("it_security", "it_security", role, llm, bus, clock, log)
