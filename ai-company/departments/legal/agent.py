"""Legal department agent for Lumenhall Partners (contracts, compliance, privacy, AI risk, disputes).

The agent does first-pass analysis, drafting and tracking only. It never gives binding legal advice, never
signs contracts and never notifies regulators (COMPANY.md §9.4): every judgement-bearing output is marked as a
draft for review by a qualified human lawyer (the General Counsel) and the human steps (signature, ICO filing)
are modelled as delayed ``legal.internal.*`` confirmations.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# ---------------------------------------------------------------------------------------------------------
# Constants (facts copied from COMPANY.md; derived values commented)
# ---------------------------------------------------------------------------------------------------------
DISCLAIMER = ("Automated first-pass analysis by the Legal agent. It is not legal advice and is not binding. "
              "A qualified human lawyer (General Counsel) must review before anyone relies on or acts on it.")
ESCALATION_OWNER = "General Counsel"

DEAL_CEO_THRESHOLD_GBP = 500_000        # COMPANY.md §9.3: deal >= £500k needs CEO approval
DEAL_BOARD_THRESHOLD_GBP = 1_500_000    # COMPANY.md §9.3: deal > £1.5m needs Board approval
STANDARD_PAYMENT_DAYS = 30              # COMPANY.md §7: net 30
FALLBACK_PAYMENT_DAYS = 45              # playbook fallback (needs Finance head and CEO, COMPANY.md §9.3)
KEEP_MIN_TERM_MONTHS = 12               # COMPANY.md §3.3
KEEP_UPLIFT_ADD_PCT = 2.0               # COMPANY.md §7: CPI + 2%
KEEP_UPLIFT_CAP_PCT = 7.0               # COMPANY.md §7: cap 7%
PLANNING_CPI_PCT = 3.0                  # assumption (economics.md section 4) when no CPI is supplied
BASE_RATE_PCT = 4.0                     # assumption (economics.md section 4): Bank of England base rate
LATE_PAYMENT_MARGIN_PCT = 8.0           # COMPANY.md §7: 8% over base rate
ICO_DEADLINE_HOURS = 72                 # UK GDPR Art 33(1); COMPANY.md §9.3
CLIENT_BREACH_NOTICE_HOURS = 48         # playbook standard for contractual notice to a client (controller)
SIGNATURE_LEAD_DAYS = {"standard": 3, "fallback": 5, "escalated": 5}
DEFAULT_DISCOUNT_LIMIT_PCT = 10.0       # COMPANY.md §9.3: discount > 10% needs Finance head and CEO
TRAINING_TARGET_PCT = 95.0              # kpis.md compliance_training_completion_pct FY2026
RATE_CARD_GBP = {                       # COMPANY.md §3.5
    "partner": 2400, "principal": 1800, "manager": 1400, "senior_consultant": 1050,
    "consultant": 800, "analyst": 550, "agent_day": 350,
}
# COMPANY.md §5.4 department envelope (people, non-people) in GBP per fiscal year, and §6.1 headcount.
BUDGET_GBP = {2026: (210_000, 100_000), 2027: (330_000, 250_000), 2028: (600_000, 700_000)}
NON_PEOPLE_LINES_GBP = {
    2026: {"outside_counsel": 45_000, "clm_and_esignature": 12_000, "legal_research": 5_000,
           "ip_filings": 8_000, "regulatory_fees": 3_000, "ai_agents": 20_000, "training_cpd": 7_000,
           "us_eu_programme": 0},
    2027: {"outside_counsel": 105_000, "clm_and_esignature": 25_000, "legal_research": 10_000,
           "ip_filings": 14_000, "regulatory_fees": 6_000, "ai_agents": 40_000, "training_cpd": 10_000,
           "us_eu_programme": 40_000},
    2028: {"outside_counsel": 340_000, "clm_and_esignature": 60_000, "legal_research": 22_000,
           "ip_filings": 30_000, "regulatory_fees": 18_000, "ai_agents": 72_000, "training_cpd": 18_000,
           "us_eu_programme": 140_000},
}
HEADCOUNT = {2026: (1, 1), 2027: (3, 3), 2028: (5, 5)}   # (humans, agents) year-end, COMPANY.md §6.1

# (year, month, role, level, (band min, band max), start quarter label) requisitions (blueprint section 5)
HIRING_PLAN: tuple[tuple[int, int, str, str, tuple[int, int], str], ...] = (
    (2027, 1, "Commercial and Privacy Counsel", "manager", (92_000, 115_000), "Q2 FY2027"),
    (2027, 4, "Contracts Specialist", "consultant", (55_000, 70_000), "Q3 FY2027"),
    (2027, 10, "Privacy and Regulatory Counsel", "manager", (92_000, 115_000), "Q1 FY2028"),
    (2028, 1, "Legal Operations Analyst", "analyst", (38_000, 48_000), "Q2 FY2028"),
)

MONTHLY_CALENDAR = {
    1: "Companies House confirmation statement preparation; annual contract playbook review",
    4: "Quarterly regulatory horizon review; ICO data protection fee check",
    7: "Quarterly regulatory horizon review; insurance renewal pack (PI, cyber, D&O) with Finance",
    10: "Quarterly regulatory horizon review; open annual legal budget input (BUD cycle)",
}

# Contract playbook (blueprint section 2 of sops.md SOP-LEGAL-02): clause -> standard / fallback / escalate.
PLAYBOOK: dict[str, dict[str, Any]] = {
    "liability_cap": {
        "standard": "Aggregate cap of 100% of fees paid or payable in the 12 months before the claim",
        "fallback": "Cap up to 200% of annual fees with GC approval; super-cap for data protection breach",
        "escalate": "Cap above 200% of annual fees or uncapped (GC and CEO, COMPANY.md §9.3)",
    },
    "payment_terms": {
        "standard": "Net 30 days (COMPANY.md §7)",
        "fallback": "Net 31 to 45 days with Finance head and CEO approval (COMPANY.md §9.3)",
        "escalate": "Beyond net 45 days, pay-when-paid or set-off rights",
    },
    "ip_ownership": {
        "standard": "Client owns bespoke deliverables on payment; Lumenhall keeps background IP, tools, agents",
        "fallback": "As standard plus perpetual licence-back of non-confidential learnings",
        "escalate": "Assignment of all IP including Lumenhall background IP (GC and CEO)",
    },
    "data_terms": {
        "standard": "Lumenhall UK GDPR Art 28 data processing agreement; UK IDTA or Addendum if transfers",
        "fallback": "Client DPA reviewed against the Art 28 checklist with GC sign-off",
        "escalate": "No DPA, unreviewed controller-to-controller terms or unlimited data liability",
    },
    "governing_law": {
        "standard": "England and Wales, courts of England and Wales",
        "fallback": "New York or Delaware law for contracts with Lumenhall Partners Inc. only (from FY2027)",
        "escalate": "Any other governing law or exclusive foreign jurisdiction",
    },
    "min_term_months": {
        "standard": "Keep: 12-month minimum term (COMPANY.md §3.3)",
        "fallback": "None",
        "escalate": "Keep term below 12 months or termination for convenience inside the term",
    },
}
CLAUSE_APPROVERS = {
    "fallback": ["General Counsel"],
    "escalate": ["General Counsel", "Chief Executive Officer"],
    "payment_terms": ["Chief Financial Officer", "Chief Executive Officer"],
}
SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
FAILED_CERT_STATES = ("lapsed", "suspended", "audit_failed", "expired", "withdrawn")

# KPI list; FY2026 targets (kpis.md section 1).
KPIS = [
    Kpi("contract_turnaround_days", "days", 3.0, None, False),
    Kpi("playbook_adherence_pct", "percent", 85.0, None, True),
    Kpi("non_standard_liability_pct", "percent", 10.0, None, False),
    Kpi("deal_won_to_signed_days", "days", 7.0, None, False),
    Kpi("gc_escalation_response_hours", "hours", 24.0, None, False),
    Kpi("breach_notification_within_72h_pct", "percent", 100.0, None, True),
    Kpi("regulatory_triage_days", "days", 2.0, None, False),
    Kpi("ai_risk_review_days", "days", 5.0, None, False),
    Kpi("compliance_training_completion_pct", "percent", 95.0, None, True),
    Kpi("dsar_on_time_pct", "percent", 98.0, None, True),
    Kpi("legal_cost_pct_revenue", "percent", 5.2, None, False),
]


def _to_int(value: Any, default: int = 0) -> int:
    """Lenient int conversion that never raises."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def review_terms(terms: dict, service_line: str = "") -> list[dict]:
    """Compare requested commercial terms with the playbook. Returns one finding per supplied clause.

    Each finding: clause, requested, position (standard|fallback|escalate), severity, approvers, playbook.
    """
    findings: list[dict] = []

    def add(clause: str, requested: Any, position: str, severity: str, approvers: list[str]) -> None:
        findings.append({"clause": clause, "requested": requested, "position": position, "severity": severity,
                         "approvers": approvers, "playbook": PLAYBOOK[clause][position]})

    if "uncapped_liability" in terms or "liability_cap_multiple" in terms:
        if terms.get("uncapped_liability"):
            add("liability_cap", "uncapped", "escalate", "critical", CLAUSE_APPROVERS["escalate"])
        else:
            mult = _to_float(terms.get("liability_cap_multiple"), 1.0)
            if mult <= 1.0:
                add("liability_cap", f"{mult:g}x annual fees", "standard", "low", [])
            elif mult <= 2.0:
                add("liability_cap", f"{mult:g}x annual fees", "fallback", "medium", CLAUSE_APPROVERS["fallback"])
            else:
                add("liability_cap", f"{mult:g}x annual fees", "escalate", "high", CLAUSE_APPROVERS["escalate"])
    if "payment_days" in terms:
        days = _to_int(terms.get("payment_days"), STANDARD_PAYMENT_DAYS)
        if days <= STANDARD_PAYMENT_DAYS:
            add("payment_terms", f"net {days}", "standard", "low", [])
        elif days <= FALLBACK_PAYMENT_DAYS:
            add("payment_terms", f"net {days}", "fallback", "medium", CLAUSE_APPROVERS["payment_terms"])
        else:
            add("payment_terms", f"net {days}", "escalate", "high",
                CLAUSE_APPROVERS["payment_terms"] + ["General Counsel"])
    if "ip_ownership" in terms:
        ip = str(terms.get("ip_ownership"))
        if ip == "standard":
            add("ip_ownership", ip, "standard", "low", [])
        elif ip == "licensed_back":
            add("ip_ownership", ip, "fallback", "medium", CLAUSE_APPROVERS["fallback"])
        else:
            add("ip_ownership", ip, "escalate", "high", CLAUSE_APPROVERS["escalate"])
    if "data_terms" in terms:
        dt = str(terms.get("data_terms"))
        if dt == "standard_dpa":
            add("data_terms", dt, "standard", "low", [])
        elif dt == "client_dpa":
            add("data_terms", dt, "fallback", "medium", CLAUSE_APPROVERS["fallback"])
        else:
            add("data_terms", dt, "escalate", "high", CLAUSE_APPROVERS["escalate"])
    if "governing_law" in terms:
        law = str(terms.get("governing_law"))
        if law == "england_wales":
            add("governing_law", law, "standard", "low", [])
        elif law in ("new_york", "delaware"):
            add("governing_law", law, "fallback", "medium", CLAUSE_APPROVERS["fallback"])
        else:
            add("governing_law", law, "escalate", "high", CLAUSE_APPROVERS["escalate"])
    if "min_term_months" in terms and service_line in ("keep", ""):
        months = _to_int(terms.get("min_term_months"), KEEP_MIN_TERM_MONTHS)
        if months >= KEEP_MIN_TERM_MONTHS:
            add("min_term_months", months, "standard", "low", [])
        else:
            add("min_term_months", months, "escalate", "high",
                CLAUSE_APPROVERS["payment_terms"] + ["General Counsel"])
    return findings


def overall_position(findings: list[dict]) -> str:
    """Overall playbook position: escalated > fallback > standard."""
    positions = {f["position"] for f in findings}
    if "escalate" in positions:
        return "escalated"
    if "fallback" in positions:
        return "fallback"
    return "standard"


def max_severity(findings: list[dict]) -> str:
    """Highest severity across findings (low when there are none)."""
    return max((f["severity"] for f in findings), key=lambda s: SEVERITY_ORDER[s], default="low")


def classify_ai_use_case(body: dict) -> dict:
    """Deterministic EU AI Act style tiering (awareness only; the human lawyer decides)."""
    tags = {str(t) for t in (body.get("use_case_tags") or [])}
    prohibited = {"social_scoring", "workplace_emotion_recognition", "untargeted_face_scraping",
                  "subliminal_manipulation"}
    high_risk = {"employment", "worker_management", "credit_scoring", "education", "essential_services",
                 "biometric_identification", "law_enforcement", "critical_infrastructure", "safety_component"}
    if body.get("affects_employment"):
        tags.add("employment")
    if tags & prohibited:
        tier = "prohibited"
    elif tags & high_risk:
        tier = "high_risk"
    elif body.get("client_facing") or tags & {"chatbot", "synthetic_content", "emotion_recognition"}:
        tier = "limited_risk"
    else:
        tier = "minimal_risk"
    personal = bool(body.get("uses_personal_data"))
    automated = bool(body.get("automated_decisions"))
    conditions = ["Human oversight owner named in the agent register (COMPANY.md §9.4)",
                  "Agent outputs used in client deliverables logged for audit"]
    if tier == "prohibited":
        conditions = ["Do not build or deploy: practice appears prohibited (EU AI Act Art 5); escalate to GC"]
    if tier == "high_risk":
        conditions += ["Risk management, data governance, logging and human oversight controls (EU AI Act "
                       "high-risk requirements) if the system is placed on or used in the EU market",
                       "Conformity route and provider/deployer role confirmed by a human lawyer"]
    if tier in ("limited_risk", "high_risk"):
        conditions.append("Tell users they are interacting with an AI system / label synthetic content")
    dpia = personal and (automated or tier == "high_risk" or bool(body.get("large_scale")))
    if dpia:
        conditions.append("Data protection impact assessment before go-live (UK GDPR Art 35)")
    if automated:
        conditions.append("Meaningful human review route for significant solely automated decisions "
                          "(UK GDPR automated decision-making rules)")
    if body.get("eu_exposure") and tier != "minimal_risk":
        conditions.append("Confirm EU AI Act applicability and any EU representative requirement")
    decision = "blocked_pending_gc" if tier == "prohibited" else (
        "cleared_with_conditions" if len(conditions) > 2 else "cleared_subject_to_standard_controls")
    return {"risk_tier": tier, "dpia_required": dpia, "conditions": conditions, "recommendation": decision}


def classify_regulation(body: dict) -> dict:
    """Map a published regulation to impact areas, owners, severity and whether a policy change is likely."""
    text = " ".join(str(body.get(k, "")) for k in ("title", "summary", "regulation_id", "regulator")).lower()
    areas: list[str] = []
    owners: set[str] = set()
    rules = (
        (("gdpr", "data protection", "privacy", "ico", "data (use", "dsar"), "data_protection",
         ("it_security", "data", "people", "operations")),
        (("ai act", "artificial intelligence", "algorithm", "ai "), "ai_governance", ("product", "data")),
        (("employment", "worker", "right to work", "pay"), "employment", ("people",)),
        (("cyber", "security", "nis", "resilience"), "cyber_security", ("it_security", "operations")),
        (("tax", "vat", "hmrc"), "tax", ("operations",)),
        (("fraud", "bribery", "money laundering", "sanction"), "financial_crime", ("operations", "people")),
    )
    for keywords, area, who in rules:
        if any(k in text for k in keywords):
            areas.append(area)
            owners.update(who)
    if not areas:
        areas.append("general_regulatory")
        owners.add("operations")
    days = body.get("effective_in_days")
    days = _to_int(days, 180) if days is not None else 180
    severity = "critical" if days <= 30 else "high" if days <= 90 else "medium" if days <= 365 else "low"
    policy = bool({"data_protection", "ai_governance", "employment", "financial_crime", "cyber_security"} & set(areas))
    return {"impact_areas": areas, "owners": sorted(owners), "effective_in_days": days, "severity": severity,
            "policy_update_likely": policy}


class LegalAgent(DepartmentAgent):
    """First-pass legal operations agent. Human lawyers decide; the agent drafts, tracks and routes."""

    SUBSCRIBES = subscribes_for("legal")
    PUBLISHES = publishes_for("legal")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.state.update({
            "counters": {}, "contracts": {}, "deal_terms": {}, "deal_decisions": {}, "flagged_deals": [],
            "breaches": {}, "matters": {}, "findings": {}, "vendors": {}, "policies": [], "questionnaires": {},
            "certs": {"iso_27001": "in_progress", "cyber_essentials_plus": "in_progress",
                      "soc2_type2": "planned"},
            "okrs": {}, "board_meetings": [], "leavers": [], "hires_requested": [], "crisis_active": False,
            "training": {}, "budget": {}, "strategy_flags": [],
        })
        self._handlers: dict[str, Callable[[Message], list[Message]]] = {
            "sales.deal_won": self._on_deal_won,
            "sales.deal_approval_requested": self._on_deal_approval_requested,
            "sales.security_review_requested": self._on_security_review_requested,
            "sales.renewal_proposal_sent": self._on_renewal_proposal_sent,
            "executive.deal_decision_made": self._on_deal_decision_made,
            "executive.board_meeting_held": self._on_board_meeting_held,
            "executive.budget_approved": self._on_budget_approved,
            "executive.crisis_declared": self._on_crisis_declared,
            "executive.okrs_set": self._on_okrs_set,
            "executive.strategy_updated": self._on_strategy_updated,
            "customer_success.renewal_due": self._on_renewal_due,
            "customer_success.renewal_confirmed": self._on_renewal_confirmed,
            "delivery.scope_change_requested": self._on_scope_change_requested,
            "external.regulation_published": self._on_regulation_published,
            "finance.budget_cycle_opened": self._on_budget_cycle_opened,
            "finance.collections_escalated": self._on_collections_escalated,
            "finance.invoice_overdue": self._on_invoice_overdue,
            "it_security.access_revoked": self._on_access_revoked,
            "it_security.certification_status_updated": self._on_certification_status_updated,
            "it_security.data_breach_confirmed": self._on_data_breach_confirmed,
            "it_security.incident_detected": self._on_incident_detected,
            "it_security.incident_resolved": self._on_incident_resolved,
            "it_security.security_questionnaire_completed": self._on_questionnaire_completed,
            "it_security.vendor_risk_assessed": self._on_vendor_risk_assessed,
            "marketing.brand_incident_raised": self._on_brand_incident_raised,
            "operations.compliance_action_completed": self._on_compliance_action_completed,
            "operations.vendor_review_requested": self._on_vendor_review_requested,
            "people.compliance_training_completed": self._on_training_completed,
            "people.contractor_engaged": self._on_contractor_engaged,
            "people.employee_left": self._on_employee_left,
            "people.offer_accepted": self._on_offer_accepted,
            "product.ai_risk_review_requested": self._on_ai_risk_review_requested,
            "legal.internal.signature_due": self._on_signature_due,
            "legal.internal.ico_filing_due": self._on_ico_filing_due,
        }

    # ------------------------------------------------------------------------------------------------
    # framework contract
    # ------------------------------------------------------------------------------------------------
    @property
    def system_prompt(self) -> str:
        return (super().system_prompt + " You are an AI assistant, not a lawyer: never give binding legal "
                "advice, never sign or notify regulators, and always escalate to the General Counsel.")

    def handle(self, message: Message) -> list[Message]:
        """Route by topic. Returns only messages whose topics are in PUBLISHES."""
        handler = self._handlers.get(message.topic)
        if handler is None:
            self.log_event("legal.activity.unhandled_topic", f"no handler for {message.topic}",
                           message_id=message.id)
            return []
        return self._public(handler(message) or [])

    def tick(self) -> list[Message]:
        """Daily breach deadline watch, weekly matter review, monthly calendar and hiring cadence."""
        out: list[Message] = []
        self._watch_breach_deadlines()
        if self.clock.every(7):
            open_contracts = [c for c in self.state["contracts"].values()
                              if c["status"] in ("pending_approval", "awaiting_signature")]
            self.log_event("legal.activity.weekly_matter_review", "weekly matter and approvals review",
                           open_contracts=len(open_contracts), open_breaches=self._open_breach_count(),
                           open_tasks=sum(1 for t in self.tasks.values() if t.status in ("todo", "in_progress")))
        if self.clock.is_month_start:
            d = self.clock.date
            item = MONTHLY_CALENDAR.get(d.month, "Monthly compliance calendar and privilege housekeeping")
            self.log_event("legal.activity.monthly_compliance_review", item, month=d.isoformat()[:7])
            for year, month, role, level, band, start in HIRING_PLAN:
                key = f"{year}-{month:02d}-{role}"
                if (d.year, d.month) == (year, month) and key not in self.state["hires_requested"]:
                    self.state["hires_requested"].append(key)
                    out.append(self.emit("legal.hire_requested", {
                        "department": "legal", "role": role, "level": level, "count": 1,
                        "salary_band_gbp": list(band), "start_quarter": start,
                        "summary": f"Legal hiring plan requisition: {role} (blueprint section 5)"}))
        return self._public(out)

    # ------------------------------------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------------------------------------
    def _public(self, msgs: list[Message]) -> list[Message]:
        return [m for m in msgs if m.topic in self.PUBLISHES]

    def _next(self, prefix: str, width: int = 4) -> str:
        counters = self.state["counters"]
        counters[prefix] = counters.get(prefix, 0) + 1
        return f"{prefix}-{counters[prefix]:0{width}d}"

    def _pub(self, topic: str, body: dict, reply_to: Optional[str] = None, delay_days: int = 0) -> Message:
        """Emit a public message with the standard 'not legal advice' markers."""
        body = dict(body)
        body.setdefault("advice_status", "draft_for_human_lawyer_review")
        body.setdefault("escalated_to", ESCALATION_OWNER)
        body.setdefault("disclaimer", DISCLAIMER)
        return self.emit(topic, body, reply_to=reply_to, delay_days=delay_days)

    def _internal(self, topic: str, body: dict, delay_days: int) -> Message:
        return self.emit(topic, body, recipient="legal", delay_days=delay_days)

    def _narrative(self, prompt: str) -> str:
        """Optional LLM-written note; deterministic with MockLLM and never required for logic."""
        try:
            return str(self.ask_llm(prompt))
        except Exception:  # noqa: BLE001 - LLM use is optional, never let it break routing
            return ""

    def _open_breach_count(self) -> int:
        return sum(1 for b in self.state["breaches"].values() if b["notifiable"] and not b["filed"])

    def _fiscal_year(self) -> int:
        return max(2026, min(2028, self.clock.date.year))

    # ------------------------------------------------------------------------------------------------
    # contracts: deal won, approvals, signature
    # ------------------------------------------------------------------------------------------------
    def _open_contract(self, msg: Message, contract_type: str, deal_id: str, amount: int, terms: dict,
                       service_line: str, extra: Optional[dict] = None) -> list[Message]:
        b = msg.body
        out: list[Message] = []
        own_id = b.get("contract_id") if contract_type in ("msa_sow", "keep_order_form") else None
        contract_id = own_id or self._next("CT")
        findings = review_terms(terms, service_line)
        position = overall_position(findings)
        approved = self.state["deal_decisions"].get(deal_id) == "approved"
        pending: list[str] = []
        if amount >= DEAL_CEO_THRESHOLD_GBP and not approved and not b.get("ceo_approved"):
            pending.append("Chief Executive Officer")
        if position == "escalated" and not approved:
            pending += [a for a in ("General Counsel", "Chief Executive Officer") if a not in pending]
        if amount > DEAL_BOARD_THRESHOLD_GBP and not b.get("board_approved"):
            pending.append("Board")
        status = "pending_approval" if pending else "awaiting_signature"
        client_id = b.get("client_id", "")
        record = {"contract_id": contract_id, "deal_id": deal_id, "client_id": client_id,
                  "client_name": b.get("client_name", ""), "amount_gbp": amount, "service_line": service_line,
                  "tier": b.get("tier", ""), "contract_type": contract_type, "position": position,
                  "status": status, "approvals_pending": pending, "drafted_day": self.clock.day,
                  "signed_day": None, "warranties": list(terms.get("certification_warranties") or [])}
        if extra:
            record.update(extra)
        self.state["contracts"][contract_id] = record
        severity = max_severity(findings)
        body = {"contract_id": contract_id, "deal_id": deal_id, "client_id": client_id,
                "client_name": record["client_name"], "amount_gbp": amount, "service_line": service_line,
                "tier": record["tier"], "contract_type": contract_type, "playbook_position": position,
                "status": status, "approvals_required": pending, "findings": findings,
                "billing_terms": self._billing_terms(service_line, contract_type),
                "human_review": "full_review" if position != "standard" or amount >= DEAL_CEO_THRESHOLD_GBP
                else "sample_check",
                "due_day": self.clock.day + SIGNATURE_LEAD_DAYS[position], "summary":
                f"{contract_type} {contract_id} drafted from playbook ({position})"}
        if b.get("engagement_id"):
            body["engagement_id"] = b["engagement_id"]
        if extra:
            body.update({k: v for k, v in extra.items() if k not in body})
        if position == "escalated" and deal_id not in self.state["flagged_deals"]:
            self.state["flagged_deals"].append(deal_id)
            out.append(self._pub("legal.contract_risk_flagged", self._risk_body(
                deal_id, client_id, findings, contract_id, amount)))
        out.append(self._pub("legal.contract_drafted", body, reply_to=msg.id))
        self.create_task(f"Human lawyer review of {contract_id} ({position})",
                         due_in_days=2 if position != "standard" else 3,
                         priority="high" if position == "escalated" else "medium")
        if status == "awaiting_signature":
            self._internal("legal.internal.signature_due", {"contract_id": contract_id},
                           SIGNATURE_LEAD_DAYS[position])
        self.log_event("legal.activity.contract_drafted", body["summary"], contract_id=contract_id,
                       deal_id=deal_id, status=status, severity=severity)
        return out

    @staticmethod
    def _billing_terms(service_line: str, contract_type: str) -> str:
        if contract_type == "change_order":
            return "Rate card (COMPANY.md §3.5); signed before work starts (COMPANY.md §7)"
        if service_line == "keep" or contract_type in ("keep_order_form", "renewal"):
            return "Monthly in advance; 12-month minimum; uplift CPI + 2% capped at 7% (COMPANY.md §7)"
        return "Milestones 30% signature, 40% mid-point, 30% acceptance; expenses at cost capped 5% (§7)"

    def _risk_body(self, deal_id: str, client_id: str, findings: list[dict], contract_id: str,
                   amount: int) -> dict:
        esc = [f for f in findings if f["position"] == "escalate"]
        approvers = sorted({a for f in esc for a in f["approvers"]}) or ["General Counsel"]
        return {"deal_id": deal_id, "client_id": client_id, "contract_id": contract_id, "amount_gbp": amount,
                "severity": max_severity(findings), "blocking": True, "findings": esc or findings,
                "required_approvers": approvers,
                "recommendation": "Do not sign on these terms without GC and CEO approval (COMPANY.md §9.3)",
                "summary": f"{len(esc)} clause(s) outside playbook for {deal_id}"}

    def _on_deal_won(self, msg: Message) -> list[Message]:
        b = msg.body
        deal_id = b.get("deal_id", "unspecified")
        terms = b.get("terms") or self.state["deal_terms"].get(deal_id, {})
        service_line = b.get("service_line", "")
        ctype = "keep_order_form" if service_line == "keep" else "msa_sow"
        return self._open_contract(msg, ctype, deal_id, _to_int(b.get("amount_gbp")), dict(terms), service_line)

    def _on_deal_approval_requested(self, msg: Message) -> list[Message]:
        b = msg.body
        deal_id = b.get("deal_id", "unspecified")
        terms = dict(b.get("terms") or {})
        self.state["deal_terms"][deal_id] = terms
        amount = _to_int(b.get("amount_gbp"))
        findings = review_terms(terms, b.get("service_line", ""))
        position = overall_position(findings)
        out: list[Message] = []
        self.create_task(f"Pre-approval legal review of deal {deal_id}", due_in_days=1, priority="high")
        if position == "escalated" and deal_id not in self.state["flagged_deals"]:
            self.state["flagged_deals"].append(deal_id)
            out.append(self._pub("legal.contract_risk_flagged",
                                 self._risk_body(deal_id, b.get("client_id", ""), findings, "", amount),
                                 reply_to=msg.id))
        self.log_event("legal.activity.deal_terms_reviewed", f"{deal_id} position {position}",
                       deal_id=deal_id, amount_gbp=amount, position=position, findings=len(findings))
        return out

    def _on_deal_decision_made(self, msg: Message) -> list[Message]:
        b = msg.body
        deal_id = b.get("deal_id", "unspecified")
        raw = str(b.get("decision", "approved" if b.get("approved") else "")).lower()
        decision = "approved" if raw in ("approved", "approve", "yes") else (
            "rejected" if raw in ("rejected", "reject", "declined", "no") else "unclear")
        self.state["deal_decisions"][deal_id] = decision
        for c in self.state["contracts"].values():
            if c["deal_id"] != deal_id or c["status"] != "pending_approval":
                continue
            if decision == "rejected":
                c["status"] = "cancelled"
            elif decision == "approved":
                c["approvals_pending"] = [a for a in c["approvals_pending"]
                                          if a == "Board" and not b.get("board_approved")]
                if not c["approvals_pending"]:
                    c["status"] = "awaiting_signature"
                    self._internal("legal.internal.signature_due", {"contract_id": c["contract_id"]},
                                   SIGNATURE_LEAD_DAYS.get(c["position"], 5))
        self.log_event("legal.activity.deal_decision_recorded", f"{deal_id} {decision}", deal_id=deal_id,
                       decision=decision)
        return []

    def _on_signature_due(self, msg: Message) -> list[Message]:
        """Models the human authorised signatory executing the contract (agents never sign)."""
        c = self.state["contracts"].get(msg.body.get("contract_id", ""))
        if not c or c["status"] != "awaiting_signature":
            self.log_event("legal.activity.signature_skipped", "no contract awaiting signature",
                           contract_id=msg.body.get("contract_id", ""))
            return []
        c["status"] = "signed"
        c["signed_day"] = self.clock.day
        self.log_event("legal.activity.contract_signed", f"{c['contract_id']} executed by human signatory",
                       contract_id=c["contract_id"])
        body = {"contract_id": c["contract_id"], "deal_id": c["deal_id"], "client_id": c["client_id"],
                "client_name": c["client_name"], "amount_gbp": c["amount_gbp"],
                "service_line": c["service_line"], "tier": c["tier"], "contract_type": c["contract_type"],
                "signed_day": self.clock.day, "days_from_draft": self.clock.day - c["drafted_day"],
                "signatories": {"lumenhall": "Authorised signatory (human)", "client": "Client signatory"},
                "billing_terms": self._billing_terms(c["service_line"], c["contract_type"]),
                "payment_terms_days": STANDARD_PAYMENT_DAYS,
                "work_may_start": True, "advice_status": "executed_record",
                "summary": f"{c['contract_type']} {c['contract_id']} fully executed"}
        if c["service_line"] == "keep" or c["contract_type"] in ("keep_order_form", "renewal"):
            body["minimum_term_months"] = KEEP_MIN_TERM_MONTHS
        if c.get("engagement_id"):
            body["engagement_id"] = c["engagement_id"]
        return [self._pub("legal.contract_signed", body, reply_to=msg.id)]

    # ------------------------------------------------------------------------------------------------
    # security terms, certifications
    # ------------------------------------------------------------------------------------------------
    def _on_security_review_requested(self, msg: Message) -> list[Message]:
        b = msg.body
        deal_id = b.get("deal_id", "unspecified")
        findings: list[dict] = []
        hours = _to_int(b.get("requested_breach_notice_hours"), CLIENT_BREACH_NOTICE_HOURS)
        if hours >= CLIENT_BREACH_NOTICE_HOURS:
            pos, approvers = "standard", []
        elif hours >= 24:
            pos, approvers = "fallback", ["General Counsel", "Chief Information Security Officer"]
        else:
            pos, approvers = "escalate", ["General Counsel", "Chief Information Security Officer",
                                          "Chief Executive Officer"]
        findings.append({"clause": "breach_notice", "requested": f"{hours}h", "position": pos,
                         "approvers": approvers, "playbook": f"Standard: notify client within "
                         f"{CLIENT_BREACH_NOTICE_HOURS}h of confirmation; statutory ICO limit is "
                         f"{ICO_DEADLINE_HOURS}h"})
        audit = str(b.get("audit_rights", "annual"))
        if audit not in ("annual", "on_incident"):
            findings.append({"clause": "audit_rights", "requested": audit, "position": "escalate",
                             "approvers": ["General Counsel"],
                             "playbook": "Standard: annual audit on 30 days notice, or on incident"})
        for cert in b.get("certs_required") or []:
            status = self.state["certs"].get(cert, "unknown")
            if status != "achieved":
                findings.append({"clause": f"certification:{cert}", "requested": "warranted", "position":
                                 "fallback", "approvers": ["Chief Information Security Officer"],
                                 "playbook": f"Status is {status}: do not warrant; give roadmap date instead"})
        quest = self.state["questionnaires"].get(deal_id, "not_received")
        escalated = [f for f in findings if f["position"] == "escalate"]
        body = {"deal_id": deal_id, "client_id": b.get("client_id", ""), "findings": findings,
                "certifications": dict(self.state["certs"]), "questionnaire_status": quest,
                "open_items": len([f for f in findings if f["position"] != "standard"]),
                "status": "escalated_to_gc" if escalated else "reviewed_pending_gc_signoff",
                "summary": f"Security terms reviewed for {deal_id}: {len(findings)} point(s)"}
        self.create_task(f"GC sign-off on security terms for {deal_id}", due_in_days=2, priority="high")
        self.log_event("legal.activity.security_terms_reviewed", body["summary"], deal_id=deal_id)
        return [self._pub("legal.security_terms_reviewed", body, reply_to=msg.id)]

    def _on_questionnaire_completed(self, msg: Message) -> list[Message]:
        b = msg.body
        deal_id = b.get("deal_id", "unspecified")
        gaps = _to_int(b.get("open_gaps"), 0)
        self.state["questionnaires"][deal_id] = "completed_with_gaps" if gaps else "completed"
        if gaps:
            self.create_task(f"Review {gaps} questionnaire gap(s) against contract warranties for {deal_id}",
                             due_in_days=2, priority="high")
        self.log_event("legal.activity.questionnaire_recorded", f"{deal_id}: {gaps} open gaps",
                       deal_id=deal_id, open_gaps=gaps)
        return []

    def _on_certification_status_updated(self, msg: Message) -> list[Message]:
        b = msg.body
        cert = str(b.get("certification", "unknown"))
        status = str(b.get("status", "unknown"))
        self.state["certs"][cert] = status
        affected = sorted(c["contract_id"] for c in self.state["contracts"].values()
                          if cert in c.get("warranties", []) and c["status"] == "signed")
        self.log_event("legal.activity.certification_recorded", f"{cert}: {status}", certification=cert,
                       status=status, affected_contracts=affected)
        if status in FAILED_CERT_STATES and affected:
            return [self._pub("legal.contract_risk_flagged", {
                "severity": "high", "blocking": False, "certification": cert, "status": status,
                "affected_contracts": affected, "contract_id": affected[0],
                "recommendation": "Review warranty and notice obligations with GC before client contact",
                "summary": f"{cert} {status}: {len(affected)} contract(s) carry a security warranty"},
                reply_to=msg.id)]
        return []

    # ------------------------------------------------------------------------------------------------
    # renewals, change orders
    # ------------------------------------------------------------------------------------------------
    def _uplift_pct(self, cpi_pct: Any) -> float:
        cpi = _to_float(cpi_pct, PLANNING_CPI_PCT)
        return round(min(cpi + KEEP_UPLIFT_ADD_PCT, KEEP_UPLIFT_CAP_PCT), 2)

    def _on_renewal_due(self, msg: Message) -> list[Message]:
        b = msg.body
        uplift = self._uplift_pct(b.get("cpi_pct"))
        current = _to_int(b.get("amount_gbp"))
        renewed = int(round(current * (1 + uplift / 100)))
        extra = {"renewal": True, "uplift_pct": uplift, "renewal_amount_gbp": renewed,
                 "previous_contract_id": b.get("contract_id", "")}
        msg_like = msg
        out = self._open_contract(msg_like, "renewal", b.get("deal_id", b.get("client_id", "unspecified")),
                                  renewed, {}, "keep", extra)
        # renewal waits for the client's confirmation, not for a signature timer
        for c in self.state["contracts"].values():
            if c.get("renewal") and c["status"] == "awaiting_signature" and c["client_id"] == b.get("client_id", ""):
                c["status"] = "awaiting_client_confirmation"
        return out

    def _on_renewal_confirmed(self, msg: Message) -> list[Message]:
        b = msg.body
        client_id = b.get("client_id", "")
        match = [c for c in self.state["contracts"].values()
                 if c.get("renewal") and c["client_id"] == client_id
                 and c["status"] in ("awaiting_client_confirmation", "awaiting_signature")]
        if match:
            c = match[-1]
        else:
            cid = self._next("CT")
            c = {"contract_id": cid, "deal_id": b.get("deal_id", ""), "client_id": client_id,
                 "client_name": b.get("client_name", ""), "amount_gbp": _to_int(b.get("amount_gbp")),
                 "service_line": "keep", "tier": b.get("tier", ""), "contract_type": "renewal",
                 "position": "standard", "status": "awaiting_signature", "approvals_pending": [],
                 "drafted_day": self.clock.day, "signed_day": None, "warranties": [], "renewal": True}
            self.state["contracts"][cid] = c
        c["status"] = "awaiting_signature"
        if b.get("amount_gbp"):
            c["amount_gbp"] = _to_int(b.get("amount_gbp"))
        self.log_event("legal.activity.renewal_confirmed", f"{c['contract_id']} renewal confirmed",
                       contract_id=c["contract_id"], client_id=client_id)
        return self._on_signature_due(self.bus.make_message("legal", "legal", "legal.internal.signature_due",
                                                            {"contract_id": c["contract_id"]},
                                                            sim_time=self.clock.day))

    def _on_renewal_proposal_sent(self, msg: Message) -> list[Message]:
        b = msg.body
        uplift = _to_float(b.get("uplift_pct"), 0.0)
        discount = _to_float(b.get("discount_pct"), 0.0)
        problems = []
        if uplift > KEEP_UPLIFT_CAP_PCT:
            problems.append(f"Proposed uplift {uplift:g}% exceeds the {KEEP_UPLIFT_CAP_PCT:g}% cap (COMPANY.md §7)")
        if discount > DEFAULT_DISCOUNT_LIMIT_PCT:
            problems.append(f"Discount {discount:g}% exceeds 10%: Finance head and CEO approval (§9.3)")
        self.log_event("legal.activity.renewal_proposal_checked", f"{len(problems)} problem(s)",
                       client_id=b.get("client_id", ""), uplift_pct=uplift, discount_pct=discount)
        if not problems:
            return []
        return [self._pub("legal.contract_risk_flagged", {
            "severity": "medium", "blocking": False, "client_id": b.get("client_id", ""),
            "contract_id": b.get("contract_id", ""), "deal_id": b.get("deal_id", ""),
            "findings": problems, "recommendation": "Correct the renewal proposal before it is accepted",
            "summary": "; ".join(problems)}, reply_to=msg.id)]

    def _on_scope_change_requested(self, msg: Message) -> list[Message]:
        b = msg.body
        amount = _to_int(b.get("amount_gbp"))
        days = b.get("days_by_level") or {}
        if not amount and isinstance(days, dict):
            amount = sum(RATE_CARD_GBP.get(str(k), 0) * _to_int(v) for k, v in days.items())
        extra = {"parent_contract_id": b.get("contract_id", ""), "rate_card_basis": True,
                 "engagement_id": b.get("engagement_id", "")}
        class_msg = msg
        out = self._open_contract(class_msg, "change_order", b.get("deal_id", b.get("engagement_id", "")),
                                  amount, {}, b.get("service_line", ""), extra)
        return out

    # ------------------------------------------------------------------------------------------------
    # personal data breaches and incidents
    # ------------------------------------------------------------------------------------------------
    def _on_incident_detected(self, msg: Message) -> list[Message]:
        b = msg.body
        incident_id = b.get("incident_id", "unspecified")
        personal = bool(b.get("personal_data_involved") or b.get("personal_data"))
        self.state["matters"][incident_id] = {
            "matter_id": self._next("MTR"), "type": "security_incident", "personal_data": personal,
            "privileged": True, "status": "open", "opened_day": self.clock.day}
        self.create_task(f"Open privileged matter for {incident_id}; route all comms via counsel",
                         due_in_days=1, priority="high")
        if personal:
            self.create_task(f"Preliminary personal data breach assessment for {incident_id}",
                             due_in_days=1, priority="critical")
        self.log_event("legal.activity.incident_matter_opened", f"{incident_id} personal_data={personal}",
                       incident_id=incident_id, privileged=True)
        return []

    def _on_data_breach_confirmed(self, msg: Message) -> list[Message]:
        b = msg.body
        incident_id = b.get("incident_id", "unspecified")
        records = _to_int(b.get("records_affected"))
        special = bool(b.get("special_category"))
        risk = str(b.get("risk_to_individuals") or ("high" if special or records >= 1000 else "likely"))
        role = str(b.get("lumenhall_role", "controller"))
        aware = _to_int(b.get("aware_day"), self.clock.day)
        notifiable = risk in ("likely", "high") and role == "controller"
        breach = {"incident_id": incident_id, "aware_day": aware, "deadline_day": aware + ICO_DEADLINE_HOURS // 24,
                  "risk": risk, "role": role, "records_affected": records, "special_category": special,
                  "notifiable": notifiable, "filed": False, "client_id": b.get("client_id", ""),
                  "warned": False, "breached_deadline": False}
        self.state["breaches"][incident_id] = breach
        self.state["matters"].setdefault(incident_id, {"matter_id": self._next("MTR"), "privileged": True,
                                                        "status": "open", "personal_data": True,
                                                        "type": "personal_data_breach"})
        self.create_task(f"Record {incident_id} in breach register (UK GDPR Art 33(5))", due_in_days=1)
        if role == "processor":
            self.create_task(f"Notify controller client within {CLIENT_BREACH_NOTICE_HOURS}h for {incident_id}",
                             due_in_days=1, priority="critical")
        if risk == "high":
            self.create_task(f"Prepare data subject communication for {incident_id} (UK GDPR Art 34)",
                             due_in_days=2, priority="high")
        if notifiable:
            self.create_task(f"General Counsel with CISO and CEO: decide and file ICO report for "
                             f"{incident_id} before day {breach['deadline_day']}", due_in_days=1,
                             priority="critical")
            self._internal("legal.internal.ico_filing_due", {"incident_id": incident_id}, 1)
        self.log_event("legal.activity.breach_assessed", f"{incident_id} risk={risk} notifiable={notifiable}",
                       incident_id=incident_id, risk=risk, notifiable=notifiable, role=role,
                       deadline_day=breach["deadline_day"])
        return []

    def _on_ico_filing_due(self, msg: Message) -> list[Message]:
        """Models the General Counsel (human) filing the ICO report; the agent only records and announces it."""
        incident_id = msg.body.get("incident_id", "")
        breach = self.state["breaches"].get(incident_id)
        if not breach or breach["filed"] or not breach["notifiable"]:
            return []
        breach["filed"] = True
        elapsed = (self.clock.day - breach["aware_day"]) * 24
        within = elapsed <= ICO_DEADLINE_HOURS
        body = {"incident_id": incident_id, "client_id": breach["client_id"], "regulator": "ICO",
                "filing_ref": self._next("LEGAL-ICO"), "deadline_hours": ICO_DEADLINE_HOURS,
                "hours_elapsed": elapsed, "within_72h": within, "risk_to_individuals": breach["risk"],
                "data_subjects_to_be_told": breach["risk"] == "high",
                "phased_report": True, "severity": "critical" if breach["risk"] == "high" else "high",
                "filed_by": "General Counsel (human) with CISO and CEO (COMPANY.md §9.3)",
                "advice_status": "filed_by_human_lawyer",
                "summary": f"ICO notification for {incident_id} filed after {elapsed}h"}
        if not within:
            body["reason_for_delay"] = "Required under UK GDPR Art 33(1); document in breach register"
        self.log_event("legal.activity.ico_notification_recorded", body["summary"], incident_id=incident_id,
                       within_72h=within)
        return [self._pub("legal.regulator_notification_filed", body)]

    def _on_incident_resolved(self, msg: Message) -> list[Message]:
        incident_id = msg.body.get("incident_id", "unspecified")
        matter = self.state["matters"].get(incident_id)
        if matter:
            matter["status"] = "closed"
        open_filing = self.state["breaches"].get(incident_id, {}).get("notifiable") and not \
            self.state["breaches"].get(incident_id, {}).get("filed")
        self.create_task(f"Privileged post-incident review for {incident_id}; update breach register",
                         due_in_days=14)
        self.log_event("legal.activity.incident_closed", f"{incident_id} resolved", incident_id=incident_id,
                       unfiled_notification=bool(open_filing))
        return []

    def _on_crisis_declared(self, msg: Message) -> list[Message]:
        self.state["crisis_active"] = True
        self.create_task("Issue legal hold and stand up privileged crisis channel", due_in_days=0,
                         priority="critical")
        self.log_event("legal.activity.crisis_protocol", "legal hold and privilege protocol started",
                       open_breaches=self._open_breach_count())
        return []

    def _watch_breach_deadlines(self) -> None:
        for incident_id, br in sorted(self.state["breaches"].items()):
            if not br["notifiable"] or br["filed"]:
                continue
            if self.clock.day >= br["deadline_day"] and not br["breached_deadline"]:
                br["breached_deadline"] = True
                self.log_event("legal.activity.breach_deadline_missed", f"{incident_id} past 72h",
                               incident_id=incident_id, severity="critical")
            elif self.clock.day >= br["deadline_day"] - 1 and not br["warned"]:
                br["warned"] = True
                self.log_event("legal.activity.breach_deadline_warning", f"{incident_id} within 24h of 72h limit",
                               incident_id=incident_id, severity="high")

    # ------------------------------------------------------------------------------------------------
    # regulation, policy, training, compliance findings
    # ------------------------------------------------------------------------------------------------
    def _on_regulation_published(self, msg: Message) -> list[Message]:
        b = msg.body
        info = classify_regulation(b)
        title = b.get("title", b.get("regulation_id", "unnamed regulation"))
        note = self._narrative(f"Summarise for a non-lawyer, in two sentences, the likely impact of: {title}")
        body = {"regulation_id": b.get("regulation_id", ""), "title": title,
                "jurisdiction": b.get("jurisdiction", "UK"), "impact_areas": info["impact_areas"],
                "owners": info["owners"], "effective_in_days": info["effective_in_days"],
                "severity": info["severity"], "policy_update_likely": info["policy_update_likely"],
                "llm_note": note, "summary": f"{title}: {', '.join(info['impact_areas'])} "
                f"(effective in {info['effective_in_days']} days)"}
        out = [self._pub("legal.regulatory_change_noted", body, reply_to=msg.id)]
        if info["severity"] in ("high", "critical"):
            fid = self._next("CF")
            self.state["findings"][fid] = {"status": "open", "policy_update": info["policy_update_likely"],
                                           "title": title, "areas": info["impact_areas"]}
            out.append(self._pub("legal.compliance_finding_raised", {
                "finding_id": fid, "severity": info["severity"], "title": title, "areas": info["impact_areas"],
                "action_owner": info["owners"][0] if info["owners"] else "operations",
                "due_day": self.clock.day + min(info["effective_in_days"], 60),
                "summary": f"Compliance action needed before {title} takes effect"}, reply_to=msg.id))
        self.create_task(f"GC review of regulatory change: {title}", due_in_days=2, priority="high"
                         if info["severity"] in ("high", "critical") else "medium")
        self.log_event("legal.activity.regulation_triaged", body["summary"], severity=info["severity"])
        return out

    def _on_compliance_action_completed(self, msg: Message) -> list[Message]:
        b = msg.body
        fid = b.get("finding_id", "")
        finding = self.state["findings"].get(fid)
        needs_policy = bool(b.get("policy_update_required")) or bool(finding and finding["policy_update"])
        if finding:
            finding["status"] = "closed"
        self.log_event("legal.activity.compliance_action_closed", f"{fid or 'unreferenced'} closed",
                       finding_id=fid, policy_update=needs_policy)
        if not needs_policy:
            return []
        policy_id = self._next("POL", 3)
        self.state["policies"].append(policy_id)
        title = (finding or {}).get("title") or b.get("title", "Compliance policy")
        return [self._pub("legal.policy_update_published", {
            "policy_id": policy_id, "title": f"Policy update: {title}", "version": f"v{len(self.state['policies'])}",
            "finding_id": fid, "effective_day": self.clock.day + 14, "training_required": True,
            "audiences": ["all_staff"], "summary": f"{policy_id} published following closure of {fid}"},
            reply_to=msg.id)]

    def _on_training_completed(self, msg: Message) -> list[Message]:
        b = msg.body
        pct = b.get("completion_pct")
        if pct is None and b.get("completion_rate") is not None:
            pct = _to_float(b.get("completion_rate")) * 100
        pct = _to_float(pct, 100.0)
        course = str(b.get("course", "mandatory compliance"))
        self.state["training"][course] = pct
        if pct < TRAINING_TARGET_PCT:
            self.create_task(f"Chase overdue '{course}' training ({pct:.0f}% vs {TRAINING_TARGET_PCT:.0f}%)",
                             due_in_days=7)
        self.log_event("legal.activity.training_recorded", f"{course}: {pct:.0f}%", course=course,
                       completion_pct=pct, on_target=pct >= TRAINING_TARGET_PCT)
        return []

    # ------------------------------------------------------------------------------------------------
    # AI risk
    # ------------------------------------------------------------------------------------------------
    def _on_ai_risk_review_requested(self, msg: Message) -> list[Message]:
        b = msg.body
        info = classify_ai_use_case(b)
        review_id = b.get("review_id") or self._next("AIR", 3)
        note = self._narrative(f"List the top two legal risks for the AI feature: {b.get('agent_name', 'agent')}")
        self.create_task(f"GC sign-off on AI risk review {review_id} ({info['risk_tier']})",
                         due_in_days=3, priority="high" if info["risk_tier"] in ("high_risk", "prohibited")
                         else "medium")
        self.log_event("legal.activity.ai_risk_reviewed", f"{review_id} tier={info['risk_tier']}",
                       review_id=review_id, risk_tier=info["risk_tier"])
        return [self._pub("legal.ai_risk_review_completed", {
            "review_id": review_id, "agent_name": b.get("agent_name", ""), "client_id": b.get("client_id", ""),
            "risk_tier": info["risk_tier"], "dpia_required": info["dpia_required"],
            "conditions": info["conditions"], "recommendation": info["recommendation"],
            "status": "recommendation_pending_gc_signoff", "severity":
            "high" if info["risk_tier"] in ("high_risk", "prohibited") else "low", "llm_note": note,
            "summary": f"AI risk review {review_id}: {info['risk_tier']}, {len(info['conditions'])} condition(s)"},
            reply_to=msg.id)]

    # ------------------------------------------------------------------------------------------------
    # collections and disputes
    # ------------------------------------------------------------------------------------------------
    @staticmethod
    def _late_payment_fixed_sum(amount: int) -> int:
        """Late Payment of Commercial Debts (Interest) Act 1998 fixed compensation per invoice."""
        return 40 if amount < 1_000 else 70 if amount < 10_000 else 100

    def _statutory_interest(self, amount: int, days: int) -> float:
        rate = (BASE_RATE_PCT + LATE_PAYMENT_MARGIN_PCT) / 100
        return round(amount * rate * max(days, 0) / 365, 2)

    def _dispute(self, msg: Message, amount: int) -> Message:
        b = msg.body
        matter_id = self._next("MTR")
        self.state["matters"][matter_id] = {"matter_id": matter_id, "type": "client_dispute",
                                            "privileged": True, "status": "open",
                                            "invoice_id": b.get("invoice_id", "")}
        severity = "critical" if amount >= 500_000 else "high" if amount >= 100_000 else "medium"
        self.create_task(f"Dispute {matter_id}: legal hold, privilege protocol, GC strategy call",
                         due_in_days=1, priority="high")
        return self._pub("legal.client_dispute_raised", {
            "matter_id": matter_id, "client_id": b.get("client_id", ""), "client_name": b.get("client_name", ""),
            "invoice_id": b.get("invoice_id", ""), "engagement_id": b.get("engagement_id", ""),
            "amount_gbp": amount, "severity": severity, "legal_hold": True, "privileged": True,
            "communication_guidance": "No admissions or settlement offers; route client contact via counsel",
            "next_step": "Without-prejudice discussion and mediation before any claim is issued",
            "summary": f"Dispute {matter_id} on {b.get('invoice_id', 'unreferenced invoice')}"}, reply_to=msg.id)

    def _on_invoice_overdue(self, msg: Message) -> list[Message]:
        b = msg.body
        amount = _to_int(b.get("amount_gbp"))
        days = _to_int(b.get("days_overdue"), 0)
        interest = self._statutory_interest(amount, days)
        fixed = self._late_payment_fixed_sum(amount)
        self.log_event("legal.activity.late_payment_position", f"{b.get('invoice_id', '')}: interest £{interest}",
                       invoice_id=b.get("invoice_id", ""), days_overdue=days, interest_gbp=interest,
                       fixed_compensation_gbp=fixed)
        if days >= 45:
            self.create_task(f"Prepare letter before action for {b.get('invoice_id', 'invoice')}", due_in_days=5)
        if b.get("disputed"):
            return [self._dispute(msg, amount)]
        return []

    def _on_collections_escalated(self, msg: Message) -> list[Message]:
        b = msg.body
        amount = _to_int(b.get("amount_gbp"))
        days = _to_int(b.get("days_overdue"), 60)
        self.log_event("legal.activity.letter_before_action_drafted",
                       f"{b.get('invoice_id', '')} £{amount} at day {days}", invoice_id=b.get("invoice_id", ""),
                       interest_gbp=self._statutory_interest(amount, days),
                       fixed_compensation_gbp=self._late_payment_fixed_sum(amount))
        self.create_task(f"GC to review and send letter before action ({b.get('invoice_id', 'invoice')}); "
                         "14 days to respond", due_in_days=3, priority="high")
        if b.get("disputed"):
            return [self._dispute(msg, amount)]
        return []

    # ------------------------------------------------------------------------------------------------
    # vendors, contractors, people
    # ------------------------------------------------------------------------------------------------
    def _vendor_findings(self, rec: dict) -> list[str]:
        problems: list[str] = []
        if rec.get("processes_personal_data"):
            if not rec.get("has_dpa"):
                problems.append("No UK GDPR Art 28 data processing agreement")
            if rec.get("data_outside_uk_eea") and not rec.get("transfer_mechanism"):
                problems.append("Restricted transfer without IDTA, Addendum or adequacy route")
            if rec.get("risk_rating") in ("high", "critical"):
                problems.append("Security risk rating high: personal data processing needs CISO exception")
        return problems

    def _vendor_check(self, msg: Message, vendor_id: str) -> list[Message]:
        rec = self.state["vendors"].get(vendor_id, {})
        problems = self._vendor_findings(rec)
        self.log_event("legal.activity.vendor_reviewed", f"{vendor_id}: {len(problems)} issue(s)",
                       vendor_id=vendor_id, issues=problems)
        if not problems or rec.get("finding_raised"):
            return []
        rec["finding_raised"] = True
        fid = self._next("CF")
        self.state["findings"][fid] = {"status": "open", "policy_update": False, "title": f"Vendor {vendor_id}",
                                       "areas": ["data_protection"]}
        return [self._pub("legal.compliance_finding_raised", {
            "finding_id": fid, "vendor_id": vendor_id, "severity": "high", "areas": ["data_protection"],
            "issues": problems, "action_owner": "operations", "due_day": self.clock.day + 10,
            "summary": f"Vendor {vendor_id} not approvable on current terms: {'; '.join(problems)}"},
            reply_to=msg.id)]

    def _on_vendor_review_requested(self, msg: Message) -> list[Message]:
        b = msg.body
        vendor_id = b.get("vendor_id", "unspecified")
        rec = self.state["vendors"].setdefault(vendor_id, {})
        rec.update({k: b[k] for k in ("vendor_name", "processes_personal_data", "has_dpa",
                                       "data_outside_uk_eea", "transfer_mechanism") if k in b})
        self.create_task(f"Legal review of vendor contract {vendor_id} (DPA, liability, exit)", due_in_days=5)
        return self._vendor_check(msg, vendor_id)

    def _on_vendor_risk_assessed(self, msg: Message) -> list[Message]:
        b = msg.body
        vendor_id = b.get("vendor_id", "unspecified")
        rec = self.state["vendors"].setdefault(vendor_id, {})
        rec["risk_rating"] = b.get("risk_rating", b.get("rating", ""))
        return self._vendor_check(msg, vendor_id)

    def _on_contractor_engaged(self, msg: Message) -> list[Message]:
        b = msg.body
        sds = self._fiscal_year() >= 2027
        self.create_task(f"Contractor agreement and IR35 status for {b.get('contractor_name', 'contractor')}"
                         + (" (issue Status Determination Statement)" if sds else ""), due_in_days=3)
        self.log_event("legal.activity.contractor_reviewed", "IR35, confidentiality, IP assignment, data terms",
                       status_determination_required=sds, contractor_id=b.get("contractor_id", ""))
        return []

    def _on_offer_accepted(self, msg: Message) -> list[Message]:
        b = msg.body
        self.create_task(f"Employment contract and written particulars for {b.get('candidate_name', 'new hire')}"
                         "; right-to-work check before start", due_in_days=3)
        self.log_event("legal.activity.employment_documents", "contract, restrictive covenants by level, IP "
                       "assignment, right to work", employee_id=b.get("employee_id", ""))
        return []

    def _on_employee_left(self, msg: Message) -> list[Message]:
        b = msg.body
        self.state["leavers"].append(b.get("employee_id", "unspecified"))
        self.create_task(f"Leaver legal check for {b.get('employee_id', 'employee')}: covenants, confidentiality"
                         ", return of property", due_in_days=5)
        self.log_event("legal.activity.leaver_checked", "restrictive covenants and confidentiality reminder",
                       employee_id=b.get("employee_id", ""))
        return []

    def _on_access_revoked(self, msg: Message) -> list[Message]:
        self.log_event("legal.activity.access_revocation_evidenced", "leaver access evidence filed to matter",
                       employee_id=msg.body.get("employee_id", ""))
        return []

    # ------------------------------------------------------------------------------------------------
    # brand and IP
    # ------------------------------------------------------------------------------------------------
    def _on_brand_incident_raised(self, msg: Message) -> list[Message]:
        b = msg.body
        category = str(b.get("category", "unspecified"))
        self.create_task(f"Brand/IP incident ({category}): preserve evidence; GC decides on notice or takedown",
                         due_in_days=1, priority="high")
        self.log_event("legal.activity.brand_incident_triaged", category, category=category,
                       severity=b.get("severity", "medium"))
        if category in ("misleading_claim", "data_exposure"):
            fid = self._next("CF")
            self.state["findings"][fid] = {"status": "open", "policy_update": False, "title": category,
                                           "areas": ["marketing_compliance"]}
            return [self._pub("legal.compliance_finding_raised", {
                "finding_id": fid, "severity": b.get("severity", "medium"), "areas": ["marketing_compliance"],
                "action_owner": "operations", "due_day": self.clock.day + 5,
                "summary": f"Brand incident ({category}) needs claim substantiation or correction"},
                reply_to=msg.id)]
        return []

    # ------------------------------------------------------------------------------------------------
    # governance and budget
    # ------------------------------------------------------------------------------------------------
    def _on_board_meeting_held(self, msg: Message) -> list[Message]:
        b = msg.body
        self.state["board_meetings"].append(b.get("meeting_id", f"day-{self.clock.day}"))
        self.create_task("File minutes and update statutory registers; Companies House changes within 14 days",
                         due_in_days=10)
        self.log_event("legal.activity.board_governance", "minutes, registers, conflicts log",
                       resolutions=len(b.get("resolutions") or []))
        return []

    def _on_okrs_set(self, msg: Message) -> list[Message]:
        self.state["okrs"] = dict(msg.body.get("okrs") or {})
        self.log_event("legal.activity.okrs_noted", "legal OKRs aligned to KPI list", count=len(self.state["okrs"]))
        return []

    def _on_strategy_updated(self, msg: Message) -> list[Message]:
        b = msg.body
        flags = [k for k in ("us_expansion", "new_service_line", "acquisition", "new_market") if b.get(k)]
        self.state["strategy_flags"] = flags
        if "us_expansion" in flags:
            self.create_task("US entity readiness: Delaware filings, state registrations, US contract templates",
                             due_in_days=30)
        self.log_event("legal.activity.strategy_noted", f"flags: {', '.join(flags) or 'none'}", flags=flags)
        return []

    def _on_budget_approved(self, msg: Message) -> list[Message]:
        self.state["budget"] = {"approved": True, "body": dict(msg.body)}
        self.log_event("legal.activity.budget_recorded", "approved legal envelope recorded")
        return []

    def _on_budget_cycle_opened(self, msg: Message) -> list[Message]:
        b = msg.body
        fy = _to_int(b.get("fiscal_year"), 0) or (self.clock.date.year + 1 if self.clock.date.month >= 10
                                                   else self.clock.date.year)
        key = max(2026, min(2028, fy))
        people, non_people = BUDGET_GBP[key]
        humans, agents = HEADCOUNT[key]
        self.log_event("legal.activity.budget_prepared", f"FY{fy} legal budget", fiscal_year=fy)
        return [self._pub("legal.budget_submitted", {
            "department": "legal", "fiscal_year": fy, "budget_id": b.get("budget_id", f"BUD-{fy}"),
            "people_gbp": people, "non_people_gbp": non_people, "amount_gbp": people + non_people,
            "non_people_lines_gbp": NON_PEOPLE_LINES_GBP[key], "headcount_humans": humans,
            "headcount_agents": agents, "advice_status": "budget_submission",
            "summary": f"Legal FY{fy} budget £{(people + non_people) // 1000}k (COMPANY.md §5.4)"},
            reply_to=msg.id)]

    # ------------------------------------------------------------------------------------------------
    # reporting
    # ------------------------------------------------------------------------------------------------
    def kpi_snapshot(self) -> list[Kpi]:
        """KPIS with actuals computed from the agent's own state where it can (others stay None)."""
        signed = [c for c in self.state["contracts"].values() if c["status"] == "signed"]
        actual: dict[str, float] = {}
        if signed:
            actual["deal_won_to_signed_days"] = sum(c["signed_day"] - c["drafted_day"] for c in signed) / len(signed)
            actual["playbook_adherence_pct"] = 100.0 * sum(
                1 for c in signed if c["position"] != "escalated") / len(signed)
        filed = [b for b in self.state["breaches"].values() if b["notifiable"]]
        if filed:
            actual["breach_notification_within_72h_pct"] = 100.0 * sum(
                1 for b in filed if b["filed"] and not b["breached_deadline"]) / len(filed)
        if self.state["training"]:
            actual["compliance_training_completion_pct"] = min(self.state["training"].values())
        return [Kpi(k.name, k.unit, k.target, actual.get(k.name), k.higher_is_better) for k in KPIS]


def build_agent(llm, bus, clock, log) -> LegalAgent:
    """Construct the Legal agent (does not register with the bus and publishes nothing)."""
    role = Role("General Counsel", "legal", "head", (1, 1, 1), (140000, 200000), "Chief Executive Officer")
    return LegalAgent("legal", "legal", role, llm, bus, clock, log)
