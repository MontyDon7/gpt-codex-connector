"""Product department agent for Lumenhall Partners (roadmap, stage gates, releases, AI evaluation, AI risk review).

Runs the lifecycle of SOP-PRODUCT-01..11: RICE-scored quarterly roadmap and publication, stage-gated release trains
(G0 to G4, ``product.release_shipped``), reusable agent capabilities, evaluation and red-team findings, AI risk review
requests to Legal (``product.ai_risk_review_requested``) and close-out (``legal.ai_risk_review_completed``), product
vulnerability remediation, regulatory impact, pricing proposals, budget and hiring.

In FY2026 COMPANY.md section 6.1 gives Product 0 AI agents: the simulated ProductAgent models the decision logic of
the two humans (Chief Product Officer; Product Manager from Q4). Registered Product agents arrive from Q2 FY2027
(blueprint section 5). Agents here draft, score, evaluate and propose; gate decisions, risk-review waivers and
price changes stay human (COMPANY.md section 9.4), so every gate decision is recorded as a human decision.
All figures are modelled assumptions. Deterministic: no wall clock, no randomness (zlib.crc32 of stable keys).
"""

from __future__ import annotations

import zlib
from dataclasses import replace
from datetime import timedelta
from typing import Any, Optional

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# --------------------------------------------------------------------------------------------------------------
# Constants and thresholds (sops.md "Constants and thresholds"; mirrored exactly)
# --------------------------------------------------------------------------------------------------------------
ROADMAP_MIN_RICE = 2.0                          # SOP-01 minimum RICE to commit (compliance, security, OKR exempt)
RICE_IMPACT_SCALE = (0.25, 0.5, 1, 2, 3)        # SOP-01
RICE_CONFIDENCE_SCALE = (0.5, 0.8, 1.0)         # SOP-01
RESERVED_CAPACITY_PCT = 20                      # SOP-01 / SOP-07: security fixes and client escalations
COMMITTED_CAPACITY_PCT = 100 - RESERVED_CAPACITY_PCT
CLUSTER_MIN_CLIENTS = 3                         # SOP-02 cluster threshold; also G1 evidence minimum
CLUSTER_WINDOW_DAYS = 90                        # SOP-02 trailing window
TRIAGE_SLA_DAYS_HIGH = 1                        # business days, severity high or critical
TRIAGE_SLA_DAYS_STANDARD = 3                    # business days
RELEASE_TRAIN_DAYS = 14                         # SOP-03; Day 0 is a Monday, trains ship on Thursdays
RELEASE_TRAIN_OFFSET = 3                        # Thursday
HOTFIX_SLA_DAYS = 2                             # business days
EVAL_MIN_CASES = 200                            # golden-set cases per agent
BETA_EVAL_SCORE = 80                            # gate G3
RELEASE_EVAL_SCORE = 85                         # gate G4
REGRESSION_TOLERANCE_PTS = 2
MAX_OPEN_MEDIUM_FINDINGS = 3                    # at G4; zero open critical or high
AGENT_QUALITY_FLOOR = 80                        # remediation task within 2 business days
AGENT_QUALITY_FREEZE = 70                       # release freeze for that agent
REVIEW_SCORE_DROP_PTS = 5                       # evaluation drop that triggers an AI risk review (RT-6)
EVAL_COMPUTE_ALERT_PCT = 90                     # of the monthly evaluation compute line
MODEL_SWITCH_MARGIN_PTS = 3
MODEL_SWITCH_MAX_COST_INCREASE_PCT = 10
TECH_TRIAGE_DAYS = 2                            # business days
RISK_REVIEW_REQUEST_DAYS = 2                    # business days from identifying a trigger
RISK_REVIEW_LEGAL_TARGET_DAYS = 5               # Legal's target; escalate to the CEO at 8
RISK_REVIEW_ESCALATE_DAYS = 8
RISK_TRIGGERS = {
    "RT-1": "new or widened tool or action permission for a client-facing agent",
    "RT-2": "change of foundation model family, provider or major version in a client-facing agent",
    "RT-3": "new data class: personal, special-category or client confidential data",
    "RT-4": "increased autonomy: human approval or Manager review gate removed or relaxed",
    "RT-5": "new use case in a high-risk area (employment, credit, education, essential services, biometrics)",
    "RT-6": "guardrail, system prompt or retrieval change altering safety behaviour, or score drop over 5 points",
    "RT-7": "first deployment in a new jurisdiction (US from Q1 FY2027, EU exposure) or regulated sector",
    "RT-8": "automated decisions with legal or similarly significant effect on individuals",
}
VULN_SLA_DAYS = {"critical": 7, "high": 30, "medium": 60, "low": 90}   # IT and Security SLA mirror
VULN_EXPLOITED_SLA_DAYS = 1
VULN_VERIFY_BUFFER_DAYS = 2                     # internal due = IT and Security due minus 2, minimum 1 day
VULN_FIX_PLAN_DAYS = {"critical": 4, "high": 14, "medium": 30, "low": 60}
VULN_FIX_PLAN_EXPLOITED_DAYS = 1
REGULATORY_IMPACT_DAYS = 5                      # business days (2 if severity high or critical)
REGULATORY_IMPACT_DAYS_HIGH = 2
REGULATORY_LEAD_BDAYS = 10                      # compliance items land 10 business days before effective date
PRICING_PROPOSAL_DAYS = 10                      # business days
AGENT_DAY_RATE_GBP = 350                        # COMPANY.md §3.5
AGENT_DAY_BREAKEVEN_MAX_DAYS = 90               # rate-card review trigger
AGENT_DAY_MIN_MARGIN_PCT = 30                   # margin on a 50%-billed agent; rate-card review trigger
AGENT_BILLED_DAYS_PLAN = 110                    # 50% of 220 working days (economics.md 3.4)
AGENT_COST_PER_YEAR_GBP = {1: 25_000, 2: 24_000, 3: 20_500}   # economics.md 3.4
COMPANY_AGENTS_YEAR_END = {1: 22, 2: 70, 3: 150}              # economics.md 1.2 (COMPANY.md §6.1)
PRICING_MIN_MARGIN_PCT = {1: 48.0, 2: 58.0, 3: 64.0}          # COMPANY.md §5.1 gross margin target
PRICE_LIST_GBP = {                               # COMPANY.md §3 (Keep = annual price)
    "keep essential": 96_000, "keep plus": 216_000, "keep enterprise": 480_000,
}
BUDGET_SUBMISSION_DAY = 21                      # day of the cycle
BUDGET_ENVELOPE_GBP_K = {                       # COMPANY.md §5.4 product row: (total, people, non-people)
    2026: (270, 220, 50), 2027: (620, 520, 100), 2028: (1960, 1360, 600),
}
PEOPLE_BUILD_UP_GBP_K = {2026: 219.2, 2027: 517.2, 2028: 1358.6}   # economics.md section 2 (within £5k of envelope)
HEADCOUNT_PLAN = {2026: (2, 0), 2027: (5, 2), 2028: (12, 6)}       # COMPANY.md §6.1 (humans, agents), year end
NON_BUDGETED_SPEND_CFO_GBP = 50_000             # COMPANY.md §9.3
NON_BUDGETED_SPEND_CEO_GBP = 250_000
EVAL_COMPUTE_LINE_GBP_K = {1: 18, 2: 20, 3: 60}                    # economics.md 1.1
EVAL_RUN_COST_GBP = 450                         # modelled compute cost of one full golden-set run
CRISIS_FREEZE_HOURS = 4                         # business hours
CRISIS_REVIEW_DAYS = 5                          # business days (modelled as 7 calendar days)
EVAL_CYCLE_DAYS_BY_FY = {1: 5, 2: 4, 3: 3}      # SOP-04 evaluation report SLA (business days)
CAPACITY_PERSON_WEEKS = {1: 24, 2: 70, 3: 200}  # modelled engineering plus evaluation capacity per quarter
FIRST_FISCAL_YEAR = 2026

# Hiring plan (blueprint section 5; requests one quarter before the start quarter).
# (role, level, count, request (fy, quarter), start (fy, quarter), salary band GBP, trigger)
HIRING_PLAN = [
    ("Product Manager", "manager", 1, (2026, 3), (2026, 4), (92_000, 115_000),
     "open backlog above 15 items or the BUD-2027 cycle needing a second Product owner"),
    ("AI Evaluation and Red Team Lead", "manager", 1, (2027, 1), (2027, 2), (92_000, 115_000),
     "more than 5 live client-facing agents, US launch and SOC 2 Type II scope"),
    ("Senior AI Engineer", "senior_consultant", 1, (2027, 2), (2027, 3), (72_000, 90_000),
     "open product-owned vulnerabilities above 5 or release train missed twice in a quarter"),
    ("Product Manager", "manager", 1, (2027, 3), (2027, 4), (92_000, 115_000),
     "Keep ARR of 6.5m needs Keep tooling ownership; backlog above 30 items per Product Manager"),
    ("Director of Agent Platform", "principal", 1, (2027, 4), (2028, 1), (120_000, 155_000),
     "engineering team above 3 people; CPO cannot be strategy owner and engineering line manager"),
    ("Senior AI Engineer", "senior_consultant", 1, (2027, 4), (2028, 1), (72_000, 90_000),
     "platform scope across 104 delivery humans; fix and release capacity"),
    ("AI Engineer", "consultant", 1, (2027, 4), (2028, 1), (55_000, 70_000),
     "engineering backlog over 60 days of effort"),
    ("Product Manager", "manager", 1, (2028, 1), (2028, 2), (92_000, 115_000),
     "US share of revenue at 30% requires pricing, packaging and localisation ownership"),
    ("AI Engineer", "consultant", 1, (2028, 1), (2028, 2), (55_000, 70_000),
     "client-facing agent UX scale and Forge Scale rollout"),
    ("Product Analyst", "analyst", 1, (2028, 1), (2028, 2), (38_000, 48_000),
     "analytics demand and pricing models with Finance"),
    ("Product Designer", "consultant", 1, (2028, 1), (2028, 2), (55_000, 70_000),
     "client-facing agent experience scale for Keep Enterprise"),
]

# Candidate backlog catalogue (modelled). Each quarter admits three items; later waves reuse the catalogue.
# (title, service_line, reach clients, impact, confidence, effort person-weeks, kind, client_facing, triggers, exempt)
CATALOG = [
    ("Reusable document-extraction agent component", "forge", 8, 2, 0.8, 5, "capability", True, (), None),
    ("Evaluation harness integration with Data", "platform", 6, 2, 1.0, 3, "platform", False, (), None),
    ("Client-facing support triage agent for Keep", "keep", 7, 3, 0.8, 8, "capability", True, ("RT-1", "RT-3"), None),
    ("Agent run cost and latency dashboard", "platform", 5, 1, 0.8, 3, "platform", False, (), None),
    ("Invoice-chasing assistant with send permission", "forge", 6, 3, 0.5, 9, "capability", True,
     ("RT-1", "RT-4"), None),
    ("Prompt-injection guard for retrieval sources", "platform", 9, 2, 0.8, 4, "capability", True, ("RT-6",),
     "security"),
    ("Reusable human-approval workflow component", "forge", 9, 2, 0.8, 5, "capability", True, (), None),
    ("Connector for legacy ERP exports", "forge", 4, 0.5, 0.5, 6, "platform", False, (), None),
    ("Meeting-notes summarisation agent", "compass", 7, 1, 0.8, 4, "capability", True, ("RT-3",), None),
    ("Keep usage analytics and agent health view", "keep", 7, 1, 0.8, 4, "platform", False, (), None),
    ("Policy-question assistant for HR teams", "forge", 5, 2, 0.8, 6, "capability", True, ("RT-5", "RT-3"), None),
    ("Golden-set refresh automation", "platform", 5, 2, 0.8, 3, "platform", False, (), None),
    ("US data-residency option for Keep agents", "keep", 6, 2, 0.8, 7, "capability", True, ("RT-7",), None),
    ("Multi-agent orchestration template for Forge Scale", "forge", 6, 3, 0.8, 9, "capability", True,
     ("RT-1",), None),
]

# FY2026 targets (kpis.md); actuals filled in as the simulation runs.
KPIS: list[Kpi] = [
    Kpi("roadmap_delivery_pct", "percent", 70.0, None, True),
    Kpi("release_gate_first_pass_pct", "percent", 80.0, None, True),
    Kpi("agent_quality_score", "score", 85.0, None, True),
    Kpi("open_critical_high_findings", "count", 0.0, None, False),
    Kpi("ai_risk_review_coverage_pct", "percent", 100.0, None, True),
    Kpi("vuln_fix_sla_pct", "percent", 90.0, None, True),
    Kpi("release_cadence_adherence_pct", "percent", 85.0, None, True),
    Kpi("feedback_triage_sla_pct", "percent", 90.0, None, True),
    Kpi("capabilities_shipped", "count", 6.0, None, True),
    Kpi("platform_reuse_pct", "percent", 40.0, None, True),
    Kpi("eval_cycle_days", "days", 5.0, None, False),
    Kpi("budget_variance_pct", "percent", 5.0, None, False),
]

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
SECURITY_WORDS = ("vulnerab", "security", "exfiltrat", "injection", "data leak", "leaked", "breach", "exposed")
DEFECT_WORDS = ("defect", "bug", "regression", "crash", "error", "incorrect", "wrong", "fails", "broken", "outage")
PRICING_WORDS = ("price", "pricing", "cost", "discount", "package", "packaging", "tier", "rate card")


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


def _bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "y")
    return bool(value)


def _slug(topic: str) -> str:
    return topic.replace(".", "_")


def _hash(key: str) -> int:
    return zlib.crc32(key.encode("utf-8"))


def _sev(value: Any, default: str = "medium") -> str:
    sev = _s(value, default).lower().strip()
    return sev if sev in SEVERITY_RANK else default


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    return float(ordered[mid]) if n % 2 else (ordered[mid - 1] + ordered[mid]) / 2


class ProductAgent(DepartmentAgent):
    """Lumenhall product: CPO-office agent. Scores, evaluates, drafts and proposes; humans decide gates (§9.4)."""

    SUBSCRIBES = subscribes_for("product")
    PUBLISHES = publishes_for("product")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.kpis: dict[str, Kpi] = {k.name: k for k in KPIS}
        self.state.update({
            "backlog": {}, "item_seq": 0, "roadmaps": {}, "roadmap_seq": 0, "last_committed": [], "okrs": {},
            "gates": {}, "gate_seq": 0, "releases": {}, "release_seq": 0, "train_no": 0, "trains_scheduled": 0,
            "trains_on_time": 0, "trains_frozen": 0, "capabilities": {}, "cap_seq": 0, "caps_by_fy": {},
            "reviews": {}, "review_seq": 0, "material_total": 0, "material_covered": 0, "held_releases": [],
            "live_agents": {}, "agent_scores": {}, "agent_register": {}, "findings": {}, "finding_seq": 0,
            "evals": 0, "first_pass": 0, "first_attempts": 0, "eval_days": [], "eval_runs_month": {},
            "vulns": {}, "vuln_fixed": 0, "vuln_on_time": 0, "feedback": {}, "fb_seq": 0, "fb_total": 0,
            "fb_on_time": 0, "clusters": {}, "escalations": {}, "hotfix_seq": 0, "freezes": {}, "freeze_seq": 0,
            "data_holds": {}, "tech": {}, "tech_seq": 0, "regs": {}, "reg_seq": 0, "pricing": {}, "price_seq": 0,
            "pricing_overrides": {}, "budget_cycles": {}, "approved_budget": {}, "hires_requested": [],
            "reviewed_quarters": [], "price_reviews": [], "last_quality_report": None, "quality_reports": 0,
            "delivered": [], "ever_committed": [], "budget_variance_pct": None, "handled": 0, "unmapped": 0,
            "compute_alerted": [], "crisis_mode": False,
        })
        self._handlers = {
            "customer_success.feedback_received": self._on_feedback,
            "customer_success.support_escalated": self._on_escalation,
            "data.agent_quality_report_published": self._on_quality_report,
            "data.data_quality_issue_raised": self._on_data_quality_issue,
            "executive.budget_approved": self._on_budget_approved,
            "executive.crisis_declared": self._on_crisis,
            "executive.okrs_set": self._on_okrs,
            "executive.pricing_change_approved": self._on_pricing_approved,
            "executive.strategy_updated": self._on_strategy,
            "external.technology_release_published": self._on_technology_release,
            "finance.budget_cycle_opened": self._on_budget_cycle_opened,
            "it_security.vulnerability_found": self._on_vulnerability,
            "legal.ai_risk_review_completed": self._on_review_completed,
            "legal.regulatory_change_noted": self._on_regulatory_change,
        }

    # ------------------------------------------------------------------ dispatch
    def handle(self, message: Message) -> list[Message]:
        handler = self._handlers.get(message.topic)
        self.log_event(f"product.activity.{_slug(message.topic)}", f"{message.topic} from {message.sender}",
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

    def _bdays_between(self, start_day: int, end_day: int) -> int:
        count = 0
        for d in range(start_day + 1, end_day + 1):
            if self.clock.date_of(d).weekday() < 5:
                count += 1
        return count

    def _quarter_key(self) -> str:
        d = self.clock.date
        return f"{d.year}Q{(d.month - 1) // 3 + 1}"

    def _task(self, title: str, due_in_days: Optional[int] = None, priority: str = "medium") -> str:
        return self.create_task(title, due_in_days, priority).id

    def _set_kpi(self, name: str, actual: float) -> None:
        self.kpis[name] = replace(self.kpis[name], actual=round(actual, 2))

    def _next(self, key: str, prefix: str, width: int = 4) -> str:
        self.state[key] += 1
        return f"{prefix}-{self.state[key]:0{width}d}"

    def _owner(self, role: str) -> str:
        """Who performs a [human] step now: the named role, or the CPO until that role is in post (SOP header)."""
        d = self.clock.date
        qi = d.year * 4 + (d.month - 1) // 3
        in_post = {"Product Manager": 2026 * 4 + 3, "AI Evaluation and Red Team Lead": 2027 * 4 + 1,
                   "Senior AI Engineer": 2027 * 4 + 2, "Director of Agent Platform": 2028 * 4}
        return role if role in in_post and qi >= in_post[role] else "Chief Product Officer"

    def _narrative(self, prompt: str, fallback: str) -> str:
        try:
            text = self.ask_llm(prompt)
        except Exception:  # noqa: BLE001 - narrative is optional, never block the lifecycle
            return fallback
        return text if text else fallback

    def _is_quarter_review_day(self) -> bool:
        d = self.clock.date
        return d.weekday() == 0 and d.day <= 7 and d.month in (1, 4, 7, 10)

    def _freeze_all(self) -> Optional[dict]:
        for fz in self.state["freezes"].values():
            if fz["status"] == "active" and fz["scope"] == "all":
                return fz
        return None

    def _frozen_agents(self) -> set[str]:
        return {fz["agent"] for fz in self.state["freezes"].values() if fz["status"] == "active"
                and fz["scope"] == "agent"}

    # ------------------------------------------------------------------ backlog and RICE (SOP-01)
    @staticmethod
    def _rice(reach: float, impact: float, confidence: float, effort: float) -> float:
        return round(reach * impact * confidence / effort, 2) if effort > 0 else 0.0

    def _add_item(self, title: str, service_line: str, reach: float, impact: float, confidence: float,
                  effort: float, source: str, exempt: Optional[str] = None, kind: str = "platform",
                  client_facing: bool = False, triggers: tuple = (), deadline_day: Optional[int] = None,
                  priority: str = "normal") -> dict:
        for item in self.state["backlog"].values():
            if item["title"] == title and item["status"] not in ("shipped", "blocked", "done"):
                return item
        impact = min(RICE_IMPACT_SCALE, key=lambda v: abs(v - impact))
        confidence = min(RICE_CONFIDENCE_SCALE, key=lambda v: abs(v - confidence))
        item_id = self._next("item_seq", "BL")
        item = {"item_id": item_id, "title": title, "service_line": service_line, "reach": reach, "impact": impact,
                "confidence": confidence, "effort": effort, "rice_score": self._rice(reach, impact, confidence, effort),
                "source": source, "exempt": exempt, "kind": kind, "client_facing": client_facing,
                "triggers": list(triggers), "clients": int(reach), "status": "backlog", "gate": "G0",
                "gate_id": None, "added_day": self.clock.day, "committed_day": None, "attempts": 0,
                "review_id": None, "review": "none", "report_day": None, "frozen_day": None, "evidence_ok": False,
                "deadline_day": deadline_day, "priority": priority, "eval": None, "mediums": 0, "version_no": 0,
                "owner": self._owner("Product Manager")}
        self.state["backlog"][item_id] = item
        return item

    def _seed_quarter_backlog(self) -> None:
        d = self.clock.date
        qi = (d.year - FIRST_FISCAL_YEAR) * 4 + (d.month - 1) // 3
        scale = {1: 1.0, 2: 1.5, 3: 2.0}[self._fy()]
        for j in range(3):
            n = 3 * qi + j
            title, line, reach, impact, conf, effort, kind, facing, triggers, exempt = CATALOG[n % len(CATALOG)]
            wave = n // len(CATALOG) + 1
            self._add_item(title if wave == 1 else f"{title} (wave {wave})", line, round(reach * scale),
                           impact, conf, effort, "planning backlog", exempt, kind, facing, triggers)

    def _capacity(self) -> tuple[float, float]:
        total = float(CAPACITY_PERSON_WEEKS[self._fy()])
        return total, total * COMMITTED_CAPACITY_PCT / 100

    def _plan_roadmap(self, trigger: str, delay: int = 0) -> Optional[Message]:
        """Score, apply the 80% capacity rule and publish (SOP-PRODUCT-01 steps 2 to 7)."""
        quarter = self._quarter_key()
        rm_id = f"RM-{quarter}"
        live = [i for i in self.state["backlog"].values() if i["status"] in ("backlog", "committed")]
        in_flight = [i for i in live if i["status"] == "committed"]
        rest = [i for i in live if i["status"] == "backlog"]
        order = sorted(in_flight, key=lambda i: i["item_id"]) + sorted(
            rest, key=lambda i: (-i["rice_score"], i["item_id"]))
        _, commit_cap = self._capacity()
        used, committed, planned, themes = 0.0, [], [], []
        for item in order:
            eligible = item["rice_score"] >= ROADMAP_MIN_RICE or bool(item["exempt"])
            if eligible and (used + item["effort"] <= commit_cap or item["status"] == "committed"):
                used += item["effort"]
                committed.append(item)
            elif eligible:
                planned.append(item)
            else:
                themes.append(item)
        for item in committed:
            if item["status"] != "committed":
                item["status"], item["committed_day"] = "committed", self.clock.day
                item["gate_id"] = self._next("gate_seq", "GATE")
                self.state["gates"][item["gate_id"]] = {"gate_id": item["gate_id"], "item_id": item["item_id"],
                                                        "stage": "G0", "decision": "intake", "hold": None,
                                                        "approver": self._owner("Chief Product Officer")}
                if item["item_id"] not in self.state["ever_committed"]:
                    self.state["ever_committed"].append(item["item_id"])
            elif item["gate_id"] in self.state["gates"]:
                pass
        for item in planned:  # deferred for capacity: stays in the backlog as "Next"
            item["status"] = "backlog"
        d = self.clock.date
        seq = self.state["roadmaps"].get(rm_id, {}).get("revision", 0) + 1
        rm = {"roadmap_id": rm_id, "quarter": quarter, "committed_ids": [i["item_id"] for i in committed],
              "revision": seq, "day": self.clock.day, "trigger": trigger}
        self.state["roadmaps"][rm_id] = rm
        previous = set(self.state["last_committed"])
        self.state["last_committed"] = rm["committed_ids"]
        self._task(f"Roadmap {rm_id} rev {seq}: confirm owners, gate plans and risk-review need checks "
                   f"for {len(committed)} committed items", self._bday_offset(5), "high")
        theme_names = sorted({i["service_line"] for i in themes + planned})
        body = {
            "roadmap_id": rm_id, "quarter": quarter, "revision": seq,
            "committed": [{"item_id": i["item_id"], "title": i["title"], "rice_score": i["rice_score"],
                           "service_line": i["service_line"], "gate_target": "G4",
                           "exempt_reason": i["exempt"] or ""} for i in committed],
            "planned": [i["title"] for i in planned[:8]], "themes": theme_names or ["platform reuse"],
            "committed_count": len(committed), "reserved_capacity_pct": RESERVED_CAPACITY_PCT,
            "committed_capacity_person_weeks": round(used, 1), "trigger": trigger,
            "summary": f"Roadmap {rm_id}: {len(committed)} committed, {len(planned)} planned, "
                       f"{RESERVED_CAPACITY_PCT}% reserved for security fixes and client escalations",
        }
        changed = set(rm["committed_ids"]) != previous
        self.log_event("product.activity.roadmap_planned", f"{rm_id} rev {seq} ({trigger})",
                       committed=len(committed), planned=len(planned), below_min_rice=len(themes),
                       changed=changed, date=d.isoformat())
        return self.emit("product.roadmap_published", body, delay_days=delay)

    # ------------------------------------------------------------------ OKRs and strategy (SOP-01)
    def _items_from_direction(self, body: dict, source: str) -> int:
        added = 0
        raw = _first(body, "objectives", "okrs", "priorities", "themes", default=[])
        if isinstance(raw, dict):
            raw = list(raw.values())
        if isinstance(raw, str):
            raw = [raw]
        for entry in raw if isinstance(raw, list) else []:
            text = _s(entry.get("title") or entry.get("objective") or entry.get("name") if isinstance(entry, dict)
                      else entry).strip()
            if not text:
                continue
            before = len(self.state["backlog"])
            self._add_item(f"{source.upper()} priority: {text[:80]}", "platform", 6, 2, 0.8, 4,
                           source, exempt=source, kind="platform")
            added += len(self.state["backlog"]) - before
        return added

    def _on_okrs(self, msg: Message, body: dict) -> list[Message]:
        self.state["okrs"] = {k: v for k, v in body.items() if k in ("objectives", "okrs", "quarter", "summary")}
        self._items_from_direction(body, "okr")
        self._seed_quarter_backlog()
        rm = self._plan_roadmap("okrs_set", delay=1)
        return [rm] if rm else []

    def _on_strategy(self, msg: Message, body: dict) -> list[Message]:
        before = set(self.state["last_committed"])
        added = self._items_from_direction(body, "strategy")
        if _bool(body.get("pricing_review")) or body.get("agent_cost_per_agent_year_gbp") is not None:
            if body.get("agent_cost_per_agent_year_gbp") is not None:
                self.state["pricing_overrides"]["agent_cost"] = _num(body["agent_cost_per_agent_year_gbp"])
            out = self._pricing_review("strategy_updated")
        else:
            out = []
        self._task("Re-run RICE and capacity for items whose strategic fit changed (strategy update)",
                   self._bday_offset(5), "medium")
        rm_id = f"RM-{self._quarter_key()}"
        if rm_id in self.state["roadmaps"] or self.state["last_committed"] or added:
            # Only republish when a committed item is added, removed or re-dated (SOP-01 step 8).
            preview = self._plan_roadmap("strategy_updated", delay=self._bday_offset(3))
            if preview is not None:
                if set(self.state["last_committed"]) == before and not added:
                    self.log_event("product.activity.roadmap_unchanged", "strategy update: committed set unchanged",
                                   republished=True)
                out.append(preview)
        return out

    # ------------------------------------------------------------------ feedback and escalations (SOP-02)
    def _classify(self, body: dict) -> str:
        cat = _s(body.get("category")).lower()
        text = f"{cat} {_s(body.get('summary')).lower()}"
        if cat in ("defect", "quality", "capability_request", "usability", "pricing", "compliance"):
            return cat
        if any(w in text for w in PRICING_WORDS):
            return "pricing"
        if "compliance" in text or "regulat" in text:
            return "compliance"
        if any(w in text for w in SECURITY_WORDS) or any(w in text for w in DEFECT_WORDS):
            return "defect"
        if "request" in text or "would like" in text or "feature" in text:
            return "capability_request"
        if "slow" in text or "confus" in text or "hard to use" in text:
            return "usability"
        return "quality"

    def _log_feedback(self, msg: Message, body: dict, high_sla: bool, kind: str) -> dict:
        fb_id = self._next("fb_seq", "FB")
        category = self._classify(body)
        sla = TRIAGE_SLA_DAYS_HIGH if high_sla else TRIAGE_SLA_DAYS_STANDARD
        lag = 1 if high_sla else 2
        if self.state["crisis_mode"] or self._freeze_all():
            lag += 1  # crisis posture slows routine triage, high items are still taken the next business day
            lag = min(lag, sla) if high_sla else lag
        client = _s(body.get("client_id"), "unknown")
        score = _num(body.get("score"), 0.0) or None
        rec = {"fb_id": fb_id, "client_id": client, "category": category, "severity": _sev(body.get("severity"), "low"),
               "score": score, "day": self.clock.day, "agent": _s(_first(body, "agent", "agent_name"), ""),
               "kind": kind, "triage_lag_bdays": lag, "summary": _s(body.get("summary"))[:160]}
        self.state["feedback"][fb_id] = rec
        self.state["fb_total"] += 1
        self.state["fb_on_time"] += 1 if lag <= sla else 0
        return rec

    def _cluster(self, rec: dict) -> Optional[dict]:
        theme = rec["category"] if not rec["agent"] else f"{rec['category']}:{rec['agent']}"
        window = [f for f in self.state["feedback"].values() if self.clock.day - f["day"] <= CLUSTER_WINDOW_DAYS
                  and (f["category"] if not f["agent"] else f"{f['category']}:{f['agent']}") == theme]
        clients = sorted({f["client_id"] for f in window if f["client_id"] != "unknown"})
        if len(clients) < CLUSTER_MIN_CLIENTS:
            return None
        scores = [f["score"] for f in window if f["score"]]
        low_quality = len(scores) >= CLUSTER_MIN_CLIENTS and sum(scores) / len(scores) < 3
        cluster = self.state["clusters"].get(theme)
        if cluster is None:
            cluster = {"theme": theme, "clients": clients, "priority": "high" if low_quality else "normal",
                       "item_id": None, "day": self.clock.day}
            self.state["clusters"][theme] = cluster
            item = self._add_item(f"Resolve recurring {theme.replace(':', ' for ')} feedback", "platform",
                                  len(clients), 3 if low_quality else 2, 0.8, 3, "feedback cluster",
                                  priority=cluster["priority"], client_facing=rec["category"] != "pricing")
            cluster["item_id"] = item["item_id"]
            self._task(f"Feedback cluster '{theme}' reaches {len(clients)} clients: add to next roadmap "
                       f"({item['item_id']}, RICE {item['rice_score']})", self._bday_offset(3),
                       "high" if low_quality else "medium")
        else:
            cluster["clients"] = clients
        return cluster

    def _on_feedback(self, msg: Message, body: dict) -> list[Message]:
        rec = self._log_feedback(msg, body, high_sla=False, kind="feedback")
        self._cluster(rec)
        self.log_event("product.activity.feedback_logged", f"{rec['fb_id']} {rec['category']}",
                       client_id=rec["client_id"], triage_lag_bdays=rec["triage_lag_bdays"])
        return []

    def _on_escalation(self, msg: Message, body: dict) -> list[Message]:
        sev = _sev(body.get("severity"), "medium")
        high = SEVERITY_RANK[sev] >= 3
        rec = self._log_feedback(msg, body, high_sla=high, kind="escalation")
        cluster = self._cluster(rec)
        client = rec["client_id"]
        ticket = _s(_first(body, "ticket_id", "escalation_id", default=rec["fb_id"]))
        self.state["escalations"].setdefault(client, []).append(self.clock.day)
        recent = [d for d in self.state["escalations"][client] if self.clock.day - d <= 30]
        if len(recent) > 2:
            self._task(f"Repeated escalations from {client} ({len(recent)} in 30 days): joint review with the Chief "
                       "Customer Success Officer within 2 business days", self._bday_offset(2), "high")
        text = f"{rec['category']} {_s(body.get('summary')).lower()}"
        decision = "planned"
        out: list[Message] = []
        if high:
            if any(w in text for w in SECURITY_WORDS):
                decision = "security_handoff"
                self._task(f"Escalation {ticket} indicates a security weakness: hand to vulnerability remediation "
                           "and notify the CPO immediately (SOP-PRODUCT-07, SOP-PRODUCT-11 candidate)",
                           self._bday_offset(1), "critical")
            elif rec["category"] == "defect":
                decision = "hotfix"
                agent_name = rec["agent"] or "client agent"
                out.append(self._ship_hotfix(
                    msg, f"Hotfix for escalation {ticket}: {_s(body.get('summary'), 'client-facing defect')[:120]}",
                    component=agent_name, client_facing=True, agent_name=agent_name, client_id=client,
                    flags=body, reply_to=msg.id))
            else:
                decision = "workaround"
                self._task(f"Escalation {ticket}: agree workaround with Customer Success and score for the "
                           "next roadmap", self._bday_offset(TRIAGE_SLA_DAYS_HIGH), "high")
        elif cluster is None and rec["category"] in ("capability_request", "usability"):
            decision = "backlog"
        self.log_event("product.activity.escalation_triaged", f"{ticket}: {decision}", client_id=client,
                       severity=sev, decision=decision, fb_id=rec["fb_id"])
        self._task(f"Tell Customer Success the decision on {ticket} ({decision}) through the task thread; "
                   "client contact stays with the client manager", self._bday_offset(1))
        return [m for m in out if m is not None]

    # ------------------------------------------------------------------ AI risk review (SOP-06)
    @staticmethod
    def _detect_triggers(flags: dict) -> list[str]:
        found: list[str] = []
        explicit = flags.get("triggers")
        if isinstance(explicit, (list, tuple)):
            found += [t for t in explicit if t in RISK_TRIGGERS]
        checks = (("RT-1", ("new_tool_permission", "tools_added", "widened_permissions", "write_access")),
                  ("RT-2", ("model_change", "foundation_model_change", "model_family_change")),
                  ("RT-3", ("new_data_class", "uses_personal_data", "special_category_data")),
                  ("RT-4", ("increased_autonomy", "relaxed_human_approval")),
                  ("RT-5", ("high_risk_use_case", "affects_employment")),
                  ("RT-6", ("guardrail_change", "system_prompt_change", "retrieval_source_change")),
                  ("RT-7", ("new_jurisdiction", "eu_exposure")),
                  ("RT-8", ("automated_decisions", "automated_profiling")))
        for code, keys in checks:
            if any(_bool(flags.get(k)) for k in keys):
                found.append(code)
        return sorted(set(found))

    def _request_review(self, *, ref: str, agent_name: str, client_id: str, client_facing: bool, summary: str,
                        triggers: list[str], eval_score: Optional[float] = None, open_findings: int = 0,
                        flags: Optional[dict] = None, item: Optional[dict] = None) -> Message:
        flags = flags or {}
        review_id = self._next("review_seq", "AIR")
        tags = [t for t in flags.get("use_case_tags", []) if isinstance(t, str)] if isinstance(
            flags.get("use_case_tags"), list) else []
        if item and not tags:
            tags = [item["service_line"], item["kind"]]
        personal = _bool(flags.get("uses_personal_data")) or "RT-3" in triggers
        employment = _bool(flags.get("affects_employment")) or "RT-5" in triggers
        automated = _bool(flags.get("automated_decisions")) or "RT-8" in triggers
        eu = _bool(flags.get("eu_exposure")) or "RT-7" in triggers
        classes = ["client confidential"] + (["personal data"] if personal else [])
        body = {
            "review_id": review_id, "agent_name": agent_name, "client_id": client_id, "client_facing": client_facing,
            "change_summary": summary, "triggers": triggers, "data_classes": classes,
            "use_case_tags": tags or ["general"], "uses_personal_data": personal,
            "automated_decisions": automated, "affects_employment": employment,
            "large_scale": _bool(flags.get("large_scale")), "eu_exposure": eu, "eval_score": eval_score,
            "open_findings": open_findings, "requested_by": self._owner("AI Evaluation and Red Team Lead"),
            "severity": "high" if (automated or employment) else "medium", "ref": ref,
            "summary": f"AI risk review {review_id} requested for {agent_name}: {', '.join(triggers)}",
        }
        self.state["reviews"][review_id] = {"review_id": review_id, "ref": ref, "agent_name": agent_name,
                                            "status": "requested", "day": self.clock.day, "triggers": triggers,
                                            "item_id": item["item_id"] if item else None, "client_id": client_id,
                                            "lift_day": None, "conditions": []}
        self.state["material_covered"] += 1
        if item:
            item["review_id"], item["review"] = review_id, "requested"
            gate = self.state["gates"].get(item["gate_id"])
            if gate:
                gate["hold"] = review_id
        self._task(f"Track AI risk review {review_id}: release hold until Legal's outcome and every condition is "
                   f"evidenced (target {RISK_REVIEW_LEGAL_TARGET_DAYS} business days, escalate at "
                   f"{RISK_REVIEW_ESCALATE_DAYS})", self._bday_offset(RISK_REVIEW_LEGAL_TARGET_DAYS), "high")
        return self.emit("product.ai_risk_review_requested", body, delay_days=self._bday_offset(1))

    def _on_review_completed(self, msg: Message, body: dict) -> list[Message]:
        review_id = _s(body.get("review_id"))
        rec = self.state["reviews"].get(review_id)
        raw = _s(_first(body, "recommendation", "outcome", default="")).lower().strip()
        tier = _s(body.get("risk_tier")).lower()
        conditions = body.get("conditions") if isinstance(body.get("conditions"), list) else []
        if "block" in raw or tier == "prohibited":
            outcome = "blocked"
        elif "condition" in raw or (conditions and ("clear" in raw or "approv" in raw)):
            outcome = "conditions"
        elif "clear" in raw or "approv" in raw or "standard" in raw:
            outcome = "cleared"
        else:
            outcome = "unknown"
        self.log_event("product.activity.review_outcome", f"{review_id}: {outcome}", risk_tier=tier,
                       recommendation=raw, known_review=rec is not None)
        if rec is None:
            self._task(f"Legal outcome for unknown review {review_id or '(no id)'}: reconcile with the request "
                       "register", self._bday_offset(2), "medium")
            return []
        rec["risk_tier"], rec["recommendation"], rec["outcome"] = tier, raw, outcome
        agent = _s(body.get("agent_name"), rec["agent_name"])
        self.state["agent_register"][agent] = {"review_id": review_id, "tier": tier, "outcome": outcome,
                                               "conditions": len(conditions), "day": self.clock.day}
        out: list[Message] = []
        if outcome == "cleared":
            rec["status"], rec["lift_day"] = "cleared", self.clock.day
            out += self._lift_hold(review_id)
        elif outcome == "conditions":
            rec["status"], rec["conditions"] = "conditions_pending", list(conditions)
            extra = 7 if _bool(body.get("dpia_required")) else 0
            rec["lift_day"] = self.clock.day + 3 * max(1, len(conditions)) + extra
            for n, cond in enumerate(conditions or ["standard conditions"], start=1):
                self._task(f"{review_id}/{n}: evidence condition '{_s(cond)[:100]}' before go-live",
                           self._bday_offset(5), "high")
            if _bool(body.get("dpia_required")):
                self._task(f"{review_id}: complete DPIA before go-live", self._bday_offset(7), "high")
        elif outcome == "blocked":
            rec["status"] = "blocked"
            out += self._block_review(review_id, rec)
        else:
            self._task(f"Legal outcome {review_id} not interpretable ({raw or 'empty'}): chase Legal; hold stays",
                       self._bday_offset(1), "high")
        return out

    def _lift_hold(self, review_id: str) -> list[Message]:
        rec = self.state["reviews"][review_id]
        out: list[Message] = []
        for item in self.state["backlog"].values():
            if item["review_id"] == review_id:
                item["review"] = "cleared"
                gate = self.state["gates"].get(item["gate_id"])
                if gate:
                    gate["hold"] = None
        for held in list(self.state["held_releases"]):
            if held["review_id"] == review_id:
                self.state["held_releases"].remove(held)
                out.append(self._emit_release(**held["release"], delay=self._bday_offset(1)))
        rec["status"] = "cleared"
        return out

    def _block_review(self, review_id: str, rec: dict) -> list[Message]:
        out: list[Message] = []
        self._task(f"AI risk review {review_id} blocked/prohibited: stop work, tell Delivery and Sales of any "
                   "client commitment, escalate to the CPO and General Counsel", self._bday_offset(1), "critical")
        removed = False
        for item in self.state["backlog"].values():
            if item["review_id"] == review_id and item["status"] != "shipped":
                item["status"], item["review"] = "blocked", "blocked"
                removed = True
        self.state["held_releases"] = [h for h in self.state["held_releases"] if h["review_id"] != review_id]
        if removed:
            rm = self._plan_roadmap("replan", delay=self._bday_offset(1))
            if rm:
                out.append(rm)
        return out

    # ------------------------------------------------------------------ evaluation, findings, quality (SOP-04)
    def _score_candidate(self, item: dict, attempt: int) -> dict:
        h = _hash(f"{item['item_id']}:{attempt}")
        score = 84 + (h % 12)                                  # 84..95
        mediums = (h // 7) % 5                                 # 0..4
        high = 1 if (h // 31) % 23 == 0 else 0
        baseline = self.state["agent_scores"].get(item["title"])
        regression = 0 if baseline is None else max(0, (h // 13) % 4 - 1)
        return {"score": float(score), "mediums": mediums, "high": high, "regression": regression,
                "baseline": baseline}

    def _open_findings(self, item: dict, ev: dict) -> list[str]:
        ids: list[str] = []
        for sev, n in (("high", ev["high"]), ("medium", ev["mediums"])):
            for _ in range(n):
                fid = self._next("finding_seq", "RTF")
                self.state["findings"][fid] = {"finding_id": fid, "item_id": item["item_id"], "severity": sev,
                                               "status": "open", "day": self.clock.day, "live": False,
                                               "class": "prompt injection" if sev == "high" else "robustness"}
                ids.append(fid)
        return ids

    def _on_quality_report(self, msg: Message, body: dict) -> list[Message]:
        self.state["quality_reports"] += 1
        self.state["last_quality_report"] = _s(body.get("report_id"), msg.id)
        agent = _s(_first(body, "agent", "agent_name"), "")
        raw = _first(body, "quality_score", "composite_score", "score")
        score = _num(raw, -1.0) if raw is not None else -1.0
        if score < 0 and agent:
            score = _num(self.state["agent_scores"].get(agent), -1.0)   # fall back to our own last evaluation
        if score < 0:
            self.log_event("product.activity.quality_report_no_score", "report carries no score; no floor check",
                           report_id=self.state["last_quality_report"], agent=agent, coverage_pct=body.get("coverage_pct"))
            return []
        agent = agent or "fleet"
        previous = self.state["agent_scores"].get(agent)
        self.state["agent_scores"][agent] = score
        out: list[Message] = []
        if previous is not None and previous - score > REVIEW_SCORE_DROP_PTS and agent in self.state["live_agents"]:
            self.state["material_total"] += 1
            out.append(self._request_review(
                ref=f"quality:{agent}", agent_name=agent, client_id=_s(body.get("client_id")),
                client_facing=True, summary=f"Quality score dropped {previous - score:.1f} points to {score:.1f}",
                triggers=["RT-6"], eval_score=score, flags=body))
        if score < AGENT_QUALITY_FREEZE:
            out += self._freeze_agent(agent, score)
        elif score < AGENT_QUALITY_FLOOR:
            self._task(f"Remediation for {agent}: quality score {score:.1f} below floor {AGENT_QUALITY_FLOOR}",
                       self._bday_offset(2), "high")
        elif agent in self._frozen_agents():
            self._lift_agent_freeze(agent)
        return out

    def _freeze_agent(self, agent: str, score: float) -> list[Message]:
        if agent in self._frozen_agents():
            return []
        fz_id = self._next("freeze_seq", "FRZ")
        self.state["freezes"][fz_id] = {"freeze_id": fz_id, "scope": "agent", "agent": agent, "status": "active",
                                        "day": self.clock.day, "severity": "high", "reason": f"score {score:.1f}",
                                        "review_day": self.clock.day + 7}
        self._task(f"Release freeze {fz_id} on {agent} (quality {score:.1f} below {AGENT_QUALITY_FREEZE}): tell "
                   "Customer Success and Delivery", self._bday_offset(1), "critical")
        return []

    def _lift_agent_freeze(self, agent: str) -> None:
        for fz in self.state["freezes"].values():
            if fz["status"] == "active" and fz["scope"] == "agent" and fz["agent"] == agent:
                fz["status"], fz["lifted_day"] = "lifted", self.clock.day
                self._task(f"Freeze {fz['freeze_id']} lifted for {agent}: record evidence, post-incident review",
                           self._bday_offset(10), "medium")

    def _on_data_quality_issue(self, msg: Message, body: dict) -> list[Message]:
        sev = _sev(body.get("severity"), "medium")
        dataset = _s(_first(body, "dataset", "feed", "source"), "unknown dataset")
        self.log_event("product.activity.data_issue", f"{dataset}: {sev}", severity=sev)
        if SEVERITY_RANK[sev] < 3:
            return []
        dependents = [i["item_id"] for i in self.state["backlog"].values()
                      if i["status"] == "committed" and i["gate"] in ("G3", "G4")]
        key = f"{dataset}:{self.clock.day}"
        self.state["data_holds"][key] = {"items": dependents, "release_day": self.clock.day + 7, "dataset": dataset}
        fid = self._next("finding_seq", "RTF")
        self.state["findings"][fid] = {"finding_id": fid, "item_id": None, "severity": sev, "status": "open",
                                       "day": self.clock.day, "live": True, "class": f"data defect: {dataset}"}
        self._task(f"Hold G4 candidates ({len(dependents)}) dependent on {dataset}; re-run evaluations after fix "
                   f"({fid})", self._bday_offset(2), "high")
        return []

    # ------------------------------------------------------------------ release trains and gates (SOP-03)
    def _agent_name(self, item: dict) -> str:
        return item["title"]

    def _emit_release(self, *, product: str, version: str, release_type: str, change_summary: str,
                      client_facing: bool, eval_score: float, ai_risk_review_id: str, open_medium: int,
                      release_id: Optional[str] = None, reply_to: Optional[str] = None, delay: int = 0,
                      severity: str = "low", extra: Optional[dict] = None) -> Message:
        release_id = release_id or self._next("release_seq", "REL")
        body = {"release_id": release_id, "product": product, "version": version, "release_type": release_type,
                "change_summary": change_summary, "client_facing": client_facing, "eval_score": eval_score,
                "gate": "G4", "ai_risk_review_id": ai_risk_review_id, "sbom_ref": f"SBOM-{release_id}",
                "open_medium_findings": open_medium, "severity": severity,
                "summary": f"{release_type} {version} shipped: {change_summary[:100]}", **(extra or {})}
        self.state["releases"][release_id] = {"day": self.clock.day + delay, "type": release_type,
                                              "client_facing": client_facing, "version": version}
        return self.emit("product.release_shipped", body, reply_to=reply_to, delay_days=delay)

    def _ship_hotfix(self, msg: Optional[Message], summary: str, component: str, client_facing: bool,
                     agent_name: str = "", client_id: str = "", flags: Optional[dict] = None,
                     reply_to: Optional[str] = None, vuln_ids: Optional[list] = None,
                     severity: str = "medium") -> Optional[Message]:
        """Reduced gate (SOP-03 step 7): affected capability plus regression sample, no open critical/high, CPO decision."""
        triggers = self._detect_triggers(flags or {})
        release_id = self._next("release_seq", "REL")
        n = self._next("hotfix_seq", "HF", 3)
        score = float(self.state["agent_scores"].get(agent_name) or self.state["agent_scores"].get("fleet") or 90.0)
        extra = {"hotfix_ref": n, "component": component, "vulnerability_ids": vuln_ids or []}
        release = dict(product=component, version=f"hotfix.{n[-3:]}", release_type="hotfix", change_summary=summary,
                       client_facing=client_facing, eval_score=score, ai_risk_review_id="", open_medium=0,
                       release_id=release_id, reply_to=reply_to, severity=severity, extra=extra)
        if client_facing and triggers:
            self.state["material_total"] += 1
            review = self._request_review(ref=release_id, agent_name=agent_name or component, client_id=client_id,
                                          client_facing=True, summary=summary, triggers=triggers,
                                          eval_score=score, flags=flags)
            release["ai_risk_review_id"] = review.body["review_id"]
            self.state["held_releases"].append({"review_id": review.body["review_id"], "release": release})
            self.log_event("product.activity.hotfix_held", f"{release_id} held for {review.body['review_id']}",
                           triggers=triggers)
            return review
        return self._emit_release(**release, delay=self._bday_offset(HOTFIX_SLA_DAYS))

    def _on_train_day(self) -> bool:
        return self.clock.day >= RELEASE_TRAIN_OFFSET and (self.clock.day - RELEASE_TRAIN_OFFSET) % RELEASE_TRAIN_DAYS == 0

    def _advance_item(self, item: dict, out: list[Message], included: list[dict]) -> None:
        """Move one committed item through G0 to G4. Every decision is a recorded human decision (CPO, QA review)."""
        gate = self.state["gates"].get(item["gate_id"])
        if gate is None or item["agent_frozen"] if "agent_frozen" in item else False:
            return
        if self._agent_name(item) in self._frozen_agents() or (gate["hold"] and item["gate"] != "G3"):
            return
        build_days = max(7, int(item["effort"] * 7 // 2))
        age = self.clock.day - (item["committed_day"] or 0)
        if item["gate"] == "G0":
            if item["clients"] >= CLUSTER_MIN_CLIENTS or item["exempt"]:
                item["gate"] = gate["stage"] = "G1"
                gate["decision"] = "G1 problem validated"
            else:
                self._task(f"{item['item_id']} lacks evidence from {CLUSTER_MIN_CLIENTS} clients for G1", None, "low")
                return
        if item["gate"] == "G1" and age >= build_days // 2:
            item["gate"] = gate["stage"] = "G2"
            gate["decision"] = f"G2 design done; golden set {EVAL_MIN_CASES}+ cases; risk trigger check recorded"
            gate["golden_cases"] = EVAL_MIN_CASES + (_hash(item["item_id"]) % 40)
        if item["gate"] == "G2" and age >= build_days:
            beta = self._score_candidate(item, 0)
            if beta["score"] < BETA_EVAL_SCORE:
                return
            item["gate"] = gate["stage"] = "G3"
            gate["decision"] = f"G3 beta; composite {beta['score']:.0f}"
            if item["triggers"] and not item["review_id"]:
                self.state["material_total"] += 1
                out.append(self._request_review(
                    ref=item["item_id"], agent_name=self._agent_name(item), client_id="",
                    client_facing=item["client_facing"], summary=f"Gate G3 beta for {item['title']}",
                    triggers=list(item["triggers"]), eval_score=beta["score"], item=item,
                    flags={"use_case_tags": [item["service_line"], item["kind"]]}))
            item["frozen_day"] = self.clock.day
            n = EVAL_CYCLE_DAYS_BY_FY[self._fy()] + (1 if _hash(item["item_id"]) % 3 == 0 else 0)
            item["report_day"] = self.clock.day + self._bday_offset(n)
            item["eval_days"] = n
            self.state["evals"] += 1
            self._count_eval_run()
            return
        if item["gate"] != "G3" or item["report_day"] is None or self.clock.day < item["report_day"]:
            return
        if any(h["items"] and item["item_id"] in h["items"] and self.clock.day < h["release_day"]
               for h in self.state["data_holds"].values()):
            return
        if not item["evidence_ok"]:
            item["attempts"] += 1
            ev = self._score_candidate(item, item["attempts"])
            ok = (ev["score"] >= RELEASE_EVAL_SCORE and ev["regression"] <= REGRESSION_TOLERANCE_PTS
                  and ev["high"] == 0 and ev["mediums"] <= MAX_OPEN_MEDIUM_FINDINGS)
            self.state["eval_days"].append(item.get("eval_days", EVAL_CYCLE_DAYS_BY_FY[self._fy()]))
            if item["attempts"] == 1:
                self.state["first_attempts"] += 1
                self.state["first_pass"] += 1 if ok else 0
            self._open_findings(item, ev)
            item["eval"], item["mediums"] = ev, ev["mediums"]
            gate["decision"] = f"G4 {'pass' if ok else 'fail'}; composite {ev['score']:.0f}"
            self.log_event("product.activity.g4_evaluation", f"{item['item_id']} attempt {item['attempts']}: "
                           f"{'pass' if ok else 'fail'}", score=ev["score"], regression=ev["regression"],
                           high=ev["high"], medium=ev["mediums"])
            if not ok:
                item["frozen_day"] = self.clock.day
                item["report_day"] = self.clock.day + self._bday_offset(EVAL_CYCLE_DAYS_BY_FY[self._fy()])
                self.state["evals"] += 1
                self._count_eval_run()
                for f in self.state["findings"].values():  # fixes re-tested by a human before the next attempt
                    if f["item_id"] == item["item_id"] and f["status"] == "open" and f["severity"] == "high":
                        f["status"] = "closed"
                if item["attempts"] >= 2:
                    self._task(f"{item['item_id']} failed G4 twice: design review within 5 business days",
                               self._bday_offset(5), "high")
                return
            item["evidence_ok"] = True
        if item["triggers"] and item["review"] != "cleared":
            gate["decision"] = "G4 evidence passed; release hold for AI risk review"
            return
        if item["review"] == "conditions_pending":
            return
        item["gate"] = gate["stage"] = "G4"
        gate["decision"] = "G4 go (CPO decision; Delivery QA Lead reviewed client impact)"
        item["status"] = "shipped"
        included.append(item)

    def _count_eval_run(self) -> None:
        month = self.clock.date.strftime("%Y-%m")
        self.state["eval_runs_month"][month] = self.state["eval_runs_month"].get(month, 0) + 1

    def _run_train(self) -> list[Message]:
        freeze = self._freeze_all()
        if freeze is not None:
            self.state["trains_frozen"] += 1
            self.log_event("product.activity.train_cancelled", f"release train held by {freeze['freeze_id']}",
                           freeze_id=freeze["freeze_id"])
            return []
        self.state["trains_scheduled"] += 1
        self.state["trains_on_time"] += 1
        self.state["train_no"] += 1
        out: list[Message] = []
        included: list[dict] = []
        for item in sorted((i for i in self.state["backlog"].values() if i["status"] == "committed"),
                           key=lambda i: i["item_id"]):
            self._advance_item(item, out, included)
        fixed = [v for v in self.state["vulns"].values() if v["status"] == "planned" and v["fix_day"] <= self.clock.day
                 and v["route"] == "train"]
        n = self.state["train_no"]
        version = f"{self.clock.date.year}.{n:02d}"
        client_facing = any(i["client_facing"] for i in included)
        review_ids = [i["review_id"] for i in included if i["review_id"]]
        scores = [i["eval"]["score"] for i in included if i["eval"]]
        platform = float(self.state["agent_scores"].get("fleet") or (88 + _hash(f"train:{n}") % 8))
        pieces = [i["title"] for i in included] + [f"fix {v['vulnerability_id']}" for v in fixed]
        summary = ("; ".join(pieces) if pieces else "platform maintenance: dependency pins, regression sample")
        release_id = self._next("release_seq", "REL")
        out.append(self._emit_release(
            product="Agent platform", version=version, release_type="train", change_summary=summary,
            client_facing=client_facing, eval_score=round(min(scores) if scores else platform, 1),
            ai_risk_review_id=review_ids[0] if review_ids else "", open_medium=sum(i["mediums"] for i in included),
            release_id=release_id, extra={"item_ids": [i["item_id"] for i in included]}))
        for v in fixed:
            out.append(self._complete_fix(v, release_id))
        for item in included:
            out += self._announce(item, release_id)
            if item["client_facing"]:
                self.state["live_agents"][self._agent_name(item)] = {"release_id": release_id,
                                                                     "day": self.clock.day}
                if item["eval"]:
                    self.state["agent_scores"][self._agent_name(item)] = item["eval"]["score"]
            for f in self.state["findings"].values():
                if f["item_id"] == item["item_id"] and f["status"] == "open":
                    f["live"] = item["client_facing"]
            if item["item_id"] not in self.state["delivered"]:
                self.state["delivered"].append(item["item_id"])
        return out

    def _announce(self, item: dict, release_id: str) -> list[Message]:
        """Capability announcement within 2 business days of G4 when GA and enablement are ready (SOP-03 step 8)."""
        if item["kind"] != "capability":
            return []
        cap_id = self._next("cap_seq", "CAP")
        fy = str(self.clock.date.year)
        self.state["caps_by_fy"][fy] = self.state["caps_by_fy"].get(fy, 0) + 1
        self.state["capabilities"][cap_id] = {"item_id": item["item_id"], "release_id": release_id}
        self._task(f"Enablement pack for {cap_id} ready for Delivery, Sales, Marketing and Customer Success",
                   self._bday_offset(2))
        return [self.emit("product.agent_capability_added", {
            "capability_id": cap_id, "name": item["title"], "service_line": item["service_line"],
            "release_id": release_id, "eval_score": item["eval"]["score"] if item["eval"] else None,
            "enablement_ready": True, "use_cases": [item["title"], f"{item['service_line']} engagements"],
            "limitations": ["human review of outputs for client-facing use", "golden-set coverage "
                            f"{EVAL_MIN_CASES}+ cases; new domains need re-evaluation"],
            "summary": f"Capability {cap_id} generally available: {item['title']}"},
            delay_days=self._bday_offset(2))]

    # ------------------------------------------------------------------ vulnerabilities (SOP-07)
    def _on_vulnerability(self, msg: Message, body: dict) -> list[Message]:
        vid = _s(_first(body, "vulnerability_id", "finding_id", "id"), msg.id)
        sev = _sev(body.get("severity"), "medium")
        exploited = _bool(body.get("exploited_in_wild"))
        sla = VULN_EXPLOITED_SLA_DAYS if (exploited and sev in ("critical", "high")) or (
            exploited and sev == "critical") else VULN_SLA_DAYS[sev]
        it_due = _num(body.get("due_day"), self.clock.day + sla)
        if body.get("due_day") is None and exploited:
            it_due = self.clock.day + VULN_EXPLOITED_SLA_DAYS
        due = int(max(it_due - VULN_VERIFY_BUFFER_DAYS, self.clock.day + 1))
        plan = VULN_FIX_PLAN_EXPLOITED_DAYS if exploited and sev == "critical" else VULN_FIX_PLAN_DAYS[sev]
        route = "hotfix" if sev in ("critical", "high") or exploited else "train"
        fix_day = self.clock.day + plan
        self.state["vulns"][vid] = {
            "vulnerability_id": vid, "severity": sev, "component": _s(body.get("component"), "agent platform"),
            "release_id": _s(body.get("release_id")), "exploited": exploited, "it_due_day": int(it_due),
            "internal_due_day": due, "fix_day": fix_day, "route": route, "status": "planned",
            "received_day": self.clock.day, "summary": _s(body.get("summary"))[:160],
            "client_facing": _bool(body.get("client_facing", True))}
        self._task(f"vuln/{vid}: {sev}{' (exploited)' if exploited else ''} fix by day {due} "
                   f"(IT and Security due day {int(it_due)}); triage within 1 business day",
                   max(1, due - self.clock.day), "critical" if sev == "critical" or exploited else "high"
                   if sev == "high" else "medium")
        if exploited or sev == "critical":
            self._task(f"vuln/{vid}: decide compensating controls now (flag off, WAF rule, restrict capability) and "
                       "tell Customer Success if clients are affected", 1, "critical")
        return []

    def _complete_fix(self, vuln: dict, release_id: str) -> Message:
        vuln["status"], vuln["fixed_day"] = "fixed", self.clock.day
        on_time = self.clock.day <= vuln["internal_due_day"]
        self.state["vuln_fixed"] += 1
        self.state["vuln_on_time"] += 1 if on_time else 0
        if not on_time:
            self._task(f"vuln/{vuln['vulnerability_id']} missed internal due day {vuln['internal_due_day']}: "
                       "CISO risk acceptance if the IT and Security SLA is also at risk", 1, "high")
        return self.emit("product.vulnerability_fixed", {
            "vulnerability_id": vuln["vulnerability_id"], "release_id": release_id, "component": vuln["component"],
            "fix_summary": f"{vuln['severity']} finding in {vuln['component']} fixed and regression sample run",
            "fixed_day": self.clock.day, "on_time": on_time, "severity": vuln["severity"],
            "due_day": vuln["it_due_day"],
            "summary": f"{vuln['vulnerability_id']} fixed in {release_id}, ready for re-scan"})

    def _run_vuln_hotfixes(self) -> list[Message]:
        out: list[Message] = []
        for vid in sorted(self.state["vulns"]):
            v = self.state["vulns"][vid]
            if v["status"] != "planned" or v["route"] != "hotfix" or v["fix_day"] > self.clock.day:
                continue
            release_id = self._next("release_seq", "REL")
            n = self._next("hotfix_seq", "HF", 3)
            score = float(self.state["agent_scores"].get("fleet") or 90.0)
            out.append(self._emit_release(
                product=v["component"], version=f"hotfix.{n[-3:]}", release_type="hotfix",
                change_summary=f"Security fix for {vid} ({v['severity']})", client_facing=v["client_facing"],
                eval_score=score, ai_risk_review_id="", open_medium=0, release_id=release_id,
                severity="high" if v["severity"] in ("critical", "high") else "medium",
                extra={"hotfix_ref": n, "vulnerability_ids": [vid]}))
            out.append(self._complete_fix(v, release_id))
        return out

    # ------------------------------------------------------------------ technology watch (SOP-05)
    def _on_technology_release(self, msg: Message, body: dict) -> list[Message]:
        rid = self._next("tech_seq", "TECH")
        rtype = _s(_first(body, "release_type", "type"), "").lower()
        text = f"{rtype} {_s(body.get('summary')).lower()} {_s(body.get('product')).lower()}"
        if any(w in text for w in ("deprecat", "end-of-life", "end of life", "eol")):
            kind, decision = "deprecation", "urgent"
        elif any(w in text for w in ("security", "cve", "vulnerab")):
            kind, decision = "security-relevant", "urgent"
        elif any(w in text for w in ("model", "foundation", "llm")):
            kind, decision = "foundation model", "shortlist"
        elif any(w in text for w in ("framework", "library", "sdk")):
            kind, decision = "framework or library", "watch"
        else:
            kind, decision = "tool or connector", "watch"
        out: list[Message] = []
        rec = {"tech_id": rid, "vendor": _s(body.get("vendor")), "product": _s(body.get("product")),
               "version": _s(body.get("version")), "kind": kind, "decision": decision, "day": self.clock.day}
        if decision == "shortlist":
            h = _hash(f"{rid}:{rec['product']}:{rec['version']}")
            gain = (h % 9) - 2                                   # -2..6 composite points versus incumbent
            cost_change = ((h // 11) % 25) - 8                   # -8..16 % cost per 1,000 tasks
            adopt = (gain >= MODEL_SWITCH_MARGIN_PTS or (gain == 0 and cost_change <= -10)) \
                and cost_change <= MODEL_SWITCH_MAX_COST_INCREASE_PCT
            rec.update({"score_gain_pts": gain, "cost_change_pct": cost_change, "adopt": adopt})
            decision = "adopt_via_gates" if adopt else "keep_incumbent"
            rec["decision"] = decision
            self._task(f"{rid} bake-off on the {EVAL_MIN_CASES}-case golden sets: gain {gain:+d} points, cost "
                       f"{cost_change:+d}% per 1,000 tasks, decision {decision}", self._bday_offset(10), "medium")
            live_facing = [a for a in self.state["live_agents"]]
            if adopt and live_facing:
                self.state["material_total"] += 1
                out.append(self._request_review(
                    ref=rid, agent_name="agent platform (foundation model change)", client_id="", client_facing=True,
                    summary=f"Move to {rec['product']} {rec['version']} from {rec['vendor']} for live client-facing agents",
                    triggers=["RT-2"], eval_score=None, flags={"model_change": True}))
            if adopt:
                self._add_item(f"Adopt {rec['product']} {rec['version']} for platform agents", "platform", 8, 2,
                               0.8, 4, "technology watch", triggers=("RT-2",) if live_facing else ())
        elif decision == "urgent":
            self._task(f"{rid} urgent ({kind}): assess live agents within 1 business day, fast path with parity "
                       "acceptance and a CPO brief to the CEO if notice is under 60 days", 1, "high")
        else:
            self._task(f"{rid} triage ({decision}) within {TECH_TRIAGE_DAYS} business days", self._bday_offset(
                TECH_TRIAGE_DAYS), "low")
        self.state["tech"][rid] = rec
        self.log_event("product.activity.tech_assessed", f"{rid}: {kind} -> {rec['decision']}")
        return out

    # ------------------------------------------------------------------ regulatory change (SOP-08)
    def _on_regulatory_change(self, msg: Message, body: dict) -> list[Message]:
        reg_id = _s(_first(body, "regulation_id", "id"), msg.id)
        sev = _sev(body.get("severity"), "medium")
        days = REGULATORY_IMPACT_DAYS_HIGH if SEVERITY_RANK[sev] >= 3 else REGULATORY_IMPACT_DAYS
        effective = int(_num(body.get("effective_day"), self.clock.day + 180))
        areas = [a for a in (body.get("impact_areas") or []) if isinstance(a, str)] if isinstance(
            body.get("impact_areas"), list) else []
        text = (" ".join(areas) + " " + _s(body.get("summary")) + " " + _s(body.get("title"))).lower()
        rec_id = self._next("reg_seq", "REG")
        triggers: list[str] = []
        if any(w in text for w in ("high-risk", "high risk", "employment", "credit", "biometric")):
            triggers.append("RT-5")
        if any(w in text for w in ("eu ", "united states", "us state", "jurisdiction", "ai act", "cross-border")):
            triggers.append("RT-7")
        if any(w in text for w in ("automated decision", "profiling", "article 22")):
            triggers.append("RT-8")
        impact = "product_change" if (triggers or "ai" in text or "agent" in text or "model" in text) else "no_impact"
        self.state["regs"][rec_id] = {"reg_id": reg_id, "severity": sev, "effective_day": effective,
                                      "triggers": triggers, "impact": impact, "day": self.clock.day}
        self._task(f"{rec_id}: impact assessment of {reg_id} with Legal and the evaluation lead", self._bday_offset(days),
                   "high" if days == REGULATORY_IMPACT_DAYS_HIGH else "medium")
        out: list[Message] = []
        if impact == "product_change":
            land_by = max(self.clock.day + 1, effective - int(REGULATORY_LEAD_BDAYS * 7 / 5))
            self._add_item(f"Compliance change: {_s(body.get('title'), reg_id)[:80]}", "platform", 8, 2, 1.0, 3,
                           "regulatory change", exempt="regulatory", kind="platform", deadline_day=land_by)
            if effective - self.clock.day <= 30:
                self._task(f"{rec_id}: effective date inside 30 days: escalate to the CEO and General Counsel with "
                           "options in 1 business day", 1, "critical")
            if triggers and self.state["live_agents"]:
                self.state["material_total"] += 1
                out.append(self._request_review(
                    ref=rec_id, agent_name="client-facing agents (regulatory change)", client_id="",
                    client_facing=True, summary=f"Regulatory change {reg_id} alters client-facing agent behaviour",
                    triggers=triggers, flags={"triggers": triggers, "eu_exposure": "RT-7" in triggers}))
            quarter_end = (self.clock.date.replace(day=1) + timedelta(days=95)).replace(day=1)
            if self.clock.day_of(quarter_end) > land_by:
                rm = self._plan_roadmap("replan", delay=self._bday_offset(days))
                if rm:
                    out.append(rm)
        return out

    # ------------------------------------------------------------------ pricing (SOP-09)
    def _pricing_review(self, trigger: str) -> list[Message]:
        fy = self._fy()
        cost = self.state["pricing_overrides"].get("agent_cost", AGENT_COST_PER_YEAR_GBP[fy])
        breakeven = cost / AGENT_DAY_RATE_GBP
        margin = (1 - cost / (AGENT_DAY_RATE_GBP * AGENT_BILLED_DAYS_PLAN)) * 100
        out: list[Message] = []
        rate_trigger = breakeven > AGENT_DAY_BREAKEVEN_MAX_DAYS or margin < AGENT_DAY_MIN_MARGIN_PCT
        if rate_trigger:
            guard = PRICING_MIN_MARGIN_PCT[fy]
            proposed = int(-(-cost / (AGENT_BILLED_DAYS_PLAN * (1 - guard / 100)) // 5) * 5)
            current = AGENT_DAY_RATE_GBP
            new_margin = round((1 - cost / (proposed * AGENT_BILLED_DAYS_PLAN)) * 100, 1)
            effect = (proposed - current) * AGENT_BILLED_DAYS_PLAN * COMPANY_AGENTS_YEAR_END[fy]
            out.append(self._emit_pricing(
                "agent", "agent_day", "rate_card", current, proposed, new_margin, effect,
                f"Break-even {breakeven:.0f} billed agent-days (limit {AGENT_DAY_BREAKEVEN_MAX_DAYS}) and margin "
                f"{margin:.1f}% on a 50%-billed agent (floor {AGENT_DAY_MIN_MARGIN_PCT}%)", trigger))
        for theme, cluster in sorted(self.state["clusters"].items()):
            if theme.startswith("pricing") and not cluster.get("proposed"):
                cluster["proposed"] = True
                price = PRICE_LIST_GBP["keep plus"]
                out.append(self._emit_pricing(
                    "keep", "keep_plus", "packaging", price, price, PRICING_MIN_MARGIN_PCT[fy], 0.0,
                    f"Pricing feedback from {len(cluster['clients'])} clients: clarify what Keep Plus includes "
                    "(support days, agent coverage)", trigger))
        self.log_event("product.activity.pricing_review", f"{trigger}: {len(out)} proposal(s)",
                       breakeven_days=round(breakeven, 1), margin_pct=round(margin, 1))
        return out

    def _emit_pricing(self, line: str, tier: str, change_type: str, current: float, proposed: float, margin: float,
                      effect: float, rationale: str, trigger: str) -> Message:
        change_id = self._next("price_seq", "PCH")
        pct = round((proposed / current - 1) * 100, 1) if current else 0.0
        guard = PRICING_MIN_MARGIN_PCT[self._fy()]
        below = margin < guard
        nxt = (self.clock.date.replace(day=1) + timedelta(days=95)).replace(day=1)
        self.state["pricing"][change_id] = {"change_id": change_id, "type": change_type, "day": self.clock.day,
                                            "status": "proposed"}
        self._task(f"{change_id}: Finance re-performs the model; Sales supplies win-rate evidence; General Counsel "
                   "consulted if signed clients are affected", self._bday_offset(PRICING_PROPOSAL_DAYS), "medium")
        return self.emit("product.pricing_change_proposed", {
            "change_id": change_id, "service_line": line, "tier": tier, "change_type": change_type,
            "current_price_gbp": current, "proposed_price_gbp": proposed, "change_pct": pct,
            "margin_pct": round(margin, 1), "annual_revenue_effect_gbp": round(effect, 2),
            "effective_day": self.clock.day_of(nxt), "rationale": rationale + (
                f"; margin below the {guard:.0f}% guardrail: CPO to state the strategic reason, CFO and CEO agree"
                if below else ""), "severity": "high" if below else "medium",
            "trigger": trigger, "summary": f"Pricing proposal {change_id} ({change_type}) for {tier}: {pct:+.1f}%"},
            delay_days=self._bday_offset(2))

    def _on_pricing_approved(self, msg: Message, body: dict) -> list[Message]:
        ref = _s(_first(body, "change_id", "proposal_id", "pricing_change_id"), msg.id)
        if ref in self.state["pricing"]:
            self.state["pricing"][ref]["status"] = "approved"
        for title in ("Update packaging documents and rate-card references in the platform",
                      "Enablement for Sales and Delivery on the approved change",
                      "Re-evaluate cost per agent-run if pricing depends on a capability"):
            self._task(f"{ref}: {title}", self._bday_offset(2), "medium")
        self.log_event("product.activity.pricing_approved", ref)
        return []

    # ------------------------------------------------------------------ budget and hiring (SOP-10)
    def _budget_year_from(self, cycle_id: str, body: dict) -> int:
        digits = "".join(c for c in cycle_id if c.isdigit())
        year = int(_num(_first(body, "fiscal_year", "year"), 0)) or (int(digits[-4:]) if len(digits) >= 4 else 0)
        return year or (self.clock.date.year + (1 if self.clock.date.month >= 10 else 0))

    def _submit_budget(self, cycle_id: str, year: int, deadline: Optional[int], reply_to: Optional[str]) -> list[Message]:
        cyc = self.state["budget_cycles"].setdefault(cycle_id, {"submitted": False, "opened_day": self.clock.day})
        if cyc["submitted"]:
            return []
        cyc["submitted"] = True
        total, people, non_people = BUDGET_ENVELOPE_GBP_K[max(2026, min(2028, year))]
        agents_line = {2026: 0, 2027: 30, 2028: 92}[max(2026, min(2028, year))]
        build_up = PEOPLE_BUILD_UP_GBP_K[max(2026, min(2028, year))]
        limit = deadline if deadline is not None else cyc["opened_day"] + BUDGET_SUBMISSION_DAY
        delay = max(0, min(7, int(limit) - self.clock.day - 1))
        humans, agents = HEADCOUNT_PLAN[max(2026, min(2028, year))]
        self._task(f"Check {cycle_id} draft against the COMPANY.md section 5.4 envelope and submit by day "
                   f"{int(limit)}", delay, "high")
        options = [{"rank": 1, "item": "Extra external red-team and AI assurance ahead of SOC 2",
                    "amount_gbp": 25_000},
                   {"rank": 2, "item": "Additional evaluation compute for quarterly golden-set refresh",
                    "amount_gbp": 15_000}]
        return [self.emit("product.budget_submitted", {
            "cycle_id": cycle_id, "budget_cycle_id": cycle_id, "fiscal_year": year, "department": "product",
            "people_gbp": people * 1000, "non_people_gbp": non_people * 1000, "amount_gbp": total * 1000,
            "total_gbp": total * 1000, "build_up_people_gbp": round(build_up * 1000),
            "headcount_plan": {"humans": humans, "agents": agents, "product_agents_cost_gbp": agents_line * 1000},
            "options": options,
            "summary": f"Product {cycle_id} submission: £{total}k (people £{people}k, non-people £{non_people}k); "
                       f"extras shown as ranked options outside the base"},
            recipient="finance", reply_to=reply_to, delay_days=delay)]

    def _on_budget_cycle_opened(self, msg: Message, body: dict) -> list[Message]:
        cycle_id = _s(_first(body, "budget_cycle_id", "cycle_id", "id"), f"BUD-{self.clock.date.year + 1}")
        year = self._budget_year_from(cycle_id, body)
        deadline = _first(body, "deadline_day", "due_day")
        return self._submit_budget(cycle_id, year, int(_num(deadline)) if deadline is not None else None, msg.id)

    def _on_budget_approved(self, msg: Message, body: dict) -> list[Message]:
        cycle_id = _s(_first(body, "budget_cycle_id", "cycle_id"), f"BUD-{self.clock.date.year}")
        year = max(2026, min(2028, self._budget_year_from(cycle_id, body)))
        approved = None
        deps = body.get("departments")
        if isinstance(deps, dict) and isinstance(deps.get("product"), (int, float)):
            approved = float(deps["product"])
        elif isinstance(body.get("product_gbp"), (int, float)):
            approved = float(body["product_gbp"])
        envelope = BUDGET_ENVELOPE_GBP_K[year][0] * 1000
        self.state["approved_budget"] = {"cycle": cycle_id, "day": self.clock.day, "approved_gbp": approved}
        if approved is not None and envelope:
            self.state["budget_variance_pct"] = abs(approved - envelope) / envelope * 100
            if approved < envelope:
                self._task(f"{cycle_id} approved at £{approved:,.0f} (envelope £{envelope:,.0f}): re-rank roadmap "
                           "items and tell Delivery and Sales what moves", self._bday_offset(3), "high")
        elif self.state["budget_variance_pct"] is None:
            self.state["budget_variance_pct"] = 0.0
        self._task(f"Load approved budget {cycle_id}, update spend tracking and the hiring plan",
                   self._bday_offset(5), "medium")
        return []

    def _hire_requests(self) -> list[Message]:
        out: list[Message] = []
        d = self.clock.date
        current = (d.year, (d.month - 1) // 3 + 1)
        for idx, (role, level, count, request_q, start_q, band, trigger) in enumerate(HIRING_PLAN):
            if idx in self.state["hires_requested"] or current < request_q:
                continue
            self.state["hires_requested"].append(idx)
            out.append(self.emit("product.hire_requested", {
                "role": role, "level": level, "count": count, "department": "product",
                "start_quarter": f"Q{start_q[1]} FY{start_q[0]}", "reason": f"growth: {role} #{idx + 1} - {trigger}",
                "trigger": trigger, "salary_band_gbp": [band[0], band[1]],
                "justification": f"{role} planned from Q{start_q[1]} FY{start_q[0]} per blueprint section 5; "
                                 "requisition a quarter ahead, CEO headcount approval still required",
                "requested_by": "Chief Product Officer",
                "summary": f"Hire request: {role} starting Q{start_q[1]} FY{start_q[0]}"}, recipient="people"))
        return out

    # ------------------------------------------------------------------ crisis and freeze (SOP-11)
    def _on_crisis(self, msg: Message, body: dict) -> list[Message]:
        sev = _sev(body.get("severity"), "high")
        category = _s(body.get("category")).lower()
        crisis_id = _s(_first(body, "crisis_id", "id"), msg.id)
        unrelated = category in ("finance", "people", "legal", "market", "economic", "financial", "hr")
        self.state["crisis_mode"] = True
        if unrelated and sev != "critical":
            self._task(f"Crisis {crisis_id}: no product impact confirmed; keep release train and offer capacity "
                       "to the crisis owner", self._bday_offset(1), "medium")
            self.log_event("product.activity.crisis_assessed", f"{crisis_id}: no change", category=category)
            return []
        fz_id = self._next("freeze_seq", "FRZ")
        self.state["freezes"][fz_id] = {
            "freeze_id": fz_id, "scope": "all", "agent": "", "status": "active", "day": self.clock.day,
            "severity": sev, "reason": crisis_id, "review_day": self.clock.day + 7,
            "lift_day": self.clock.day + (28 if sev == "critical" else 14), "crisis_id": crisis_id}
        self._task(f"{fz_id}: freeze non-essential releases and G3/G4 decisions; position note for the CEO within "
                   f"{CRISIS_FREEZE_HOURS} business hours; hotfixes and security fixes continue", 0, "critical")
        out: list[Message] = []
        if self.state["last_committed"]:
            rm = self._plan_roadmap("crisis", delay=1)
            if rm:
                out.append(rm)
        return out

    def _review_freezes(self) -> list[Message]:
        out: list[Message] = []
        for fz in sorted(self.state["freezes"].values(), key=lambda f: f["freeze_id"]):
            if fz["status"] != "active":
                continue
            if fz["scope"] == "agent":
                if self.clock.day >= fz["day"] + 28:  # stale agent freezes go to the CPO for a decision
                    self._task(f"{fz['freeze_id']} on {fz['agent']} open 28 days: CPO decision", None, "high")
                    fz["day"] = self.clock.day
                continue
            if self.clock.day >= fz["lift_day"]:
                fz["status"], fz["lifted_day"] = "lifted", self.clock.day
                self.state["crisis_mode"] = bool(self._freeze_all())
                self._task(f"{fz['freeze_id']} lifted (CPO{' and CEO' if fz['severity'] == 'critical' else ''}): "
                           "post-incident review within 10 business days", self._bday_offset(10), "high")
                if self.state["last_committed"]:
                    rm = self._plan_roadmap("crisis", delay=1)
                    if rm:
                        out.append(rm)
            elif self.clock.day >= fz["review_day"]:
                fz["review_day"] += 7
                self._task(f"{fz['freeze_id']} five-business-day review: cause resolved? evidence recorded?",
                           self._bday_offset(1), "high")
        return out

    # ------------------------------------------------------------------ tick (cadences)
    def tick(self) -> list[Message]:
        out: list[Message] = []
        d = self.clock.date
        if self._is_quarter_review_day():
            qkey = self._quarter_key()
            if qkey not in self.state["reviewed_quarters"]:
                self.state["reviewed_quarters"].append(qkey)
                self._seed_quarter_backlog()
                rm = self._plan_roadmap("quarterly")
                if rm:
                    out.append(rm)
                out += self._hire_requests()
        if d.weekday() == 0 and 8 <= d.day <= 14 and d.month in (1, 4, 7, 10) and \
                self._quarter_key() not in self.state["price_reviews"]:
            self.state["price_reviews"].append(self._quarter_key())
            out += self._pricing_review("quarterly")
        if self._on_train_day():
            out += self._run_train()
        out += self._run_vuln_hotfixes()
        out += self._release_due_holds()
        out += self._review_freezes()
        out += self._review_chase()
        out += self._budget_fallback()
        self._eval_compute_check()
        self._refresh_kpis()
        return out

    def _release_due_holds(self) -> list[Message]:
        out: list[Message] = []
        for rid in sorted(self.state["reviews"]):
            rec = self.state["reviews"][rid]
            if rec["status"] == "conditions_pending" and rec["lift_day"] is not None and \
                    self.clock.day >= rec["lift_day"]:
                rec["status"] = "cleared"
                self.log_event("product.activity.review_conditions_evidenced", rid)
                out += self._lift_hold(rid)
        for key in sorted(self.state["data_holds"]):
            hold = self.state["data_holds"][key]
            if hold["items"] and self.clock.day >= hold["release_day"]:
                hold["items"] = []
                for f in self.state["findings"].values():
                    if f["class"] == f"data defect: {hold['dataset']}" and f["status"] == "open":
                        f["status"] = "closed"
                self.log_event("product.activity.data_hold_lifted", hold["dataset"])
        return out

    def _review_chase(self) -> list[Message]:
        for rid in sorted(self.state["reviews"]):
            rec = self.state["reviews"][rid]
            if rec["status"] != "requested":
                continue
            age = self._bdays_between(rec["day"], self.clock.day)
            if age >= RISK_REVIEW_ESCALATE_DAYS and not rec.get("escalated"):
                rec["escalated"] = True
                self._task(f"{rid}: no Legal outcome after {RISK_REVIEW_ESCALATE_DAYS} business days: escalate to the "
                           "CEO; hold stays", 1, "critical")
            elif age >= RISK_REVIEW_LEGAL_TARGET_DAYS and not rec.get("chased"):
                rec["chased"] = True
                self._task(f"{rid}: chase Legal task queue (target {RISK_REVIEW_LEGAL_TARGET_DAYS} business days "
                           "passed)", 1, "high")
        return []

    def _budget_fallback(self) -> list[Message]:
        d = self.clock.date
        if d.month != 10 or d.day < 8:
            return []
        year = d.year + 1
        cycle_id = f"BUD-{year}"
        if self.state["budget_cycles"].get(cycle_id, {}).get("submitted"):
            return []
        # The cycle opens on 1 October (finance.budget_cycle_opened); if it did not reach us, submit anyway.
        self.state["budget_cycles"].setdefault(cycle_id, {"submitted": False, "opened_day": self.clock.day_of(
            d.replace(day=1))})
        return self._submit_budget(cycle_id, year, None, None)

    def _eval_compute_check(self) -> None:
        month = self.clock.date.strftime("%Y-%m")
        line = EVAL_COMPUTE_LINE_GBP_K[self._fy()] * 1000 / 12
        spend = self.state["eval_runs_month"].get(month, 0) * EVAL_RUN_COST_GBP
        if line and spend >= line * EVAL_COMPUTE_ALERT_PCT / 100 and month not in self.state["compute_alerted"]:
            self.state["compute_alerted"].append(month)
            self._task(f"Evaluation compute at {spend / line * 100:.0f}% of the monthly line (alert "
                       f"{EVAL_COMPUTE_ALERT_PCT}%): tell the CPO", 1, "medium")

    # ------------------------------------------------------------------ KPI roll-up
    def _refresh_kpis(self) -> None:
        s = self.state
        if s["ever_committed"]:
            self._set_kpi("roadmap_delivery_pct", len(s["delivered"]) / len(s["ever_committed"]) * 100)
        if s["first_attempts"]:
            self._set_kpi("release_gate_first_pass_pct", s["first_pass"] / s["first_attempts"] * 100)
        live_scores = [s["agent_scores"][a] for a in s["live_agents"] if a in s["agent_scores"]]
        if live_scores:
            self._set_kpi("agent_quality_score", sum(live_scores) / len(live_scores))
        live_findings = [f for f in s["findings"].values() if f["live"] and f["status"] == "open"
                         and SEVERITY_RANK[f["severity"]] >= 3]
        self._set_kpi("open_critical_high_findings", len(live_findings))
        if s["material_total"]:
            self._set_kpi("ai_risk_review_coverage_pct", min(100.0, s["material_covered"] / s["material_total"] * 100))
        if s["vuln_fixed"]:
            self._set_kpi("vuln_fix_sla_pct", s["vuln_on_time"] / s["vuln_fixed"] * 100)
        if s["trains_scheduled"]:
            self._set_kpi("release_cadence_adherence_pct", s["trains_on_time"] / s["trains_scheduled"] * 100)
        if s["fb_total"]:
            self._set_kpi("feedback_triage_sla_pct", s["fb_on_time"] / s["fb_total"] * 100)
        self._set_kpi("capabilities_shipped", s["caps_by_fy"].get(str(self.clock.date.year), 0))
        if s["capabilities"]:  # modelled estimate: each live capability lifts Forge reuse by 8 points, cap 75
            self._set_kpi("platform_reuse_pct", min(75.0, 8.0 * len(s["capabilities"])))
        if s["eval_days"]:
            self._set_kpi("eval_cycle_days", _median([float(x) for x in s["eval_days"]]))
        if s["budget_variance_pct"] is not None:
            self._set_kpi("budget_variance_pct", s["budget_variance_pct"])

    def kpi_snapshot(self) -> list[Kpi]:
        """Current KPI values (targets from KPIS, actuals from the lifecycle state)."""
        self._refresh_kpis()
        return [self.kpis[k.name] for k in KPIS]


def build_agent(llm, bus, clock, log) -> ProductAgent:
    role = Role("Chief Product Officer", "product", "head", (1, 1, 1), (140000, 200000),  # COMPANY.md §6.2
                "Chief Executive Officer")
    return ProductAgent("product", "product", role, llm, bus, clock, log)
