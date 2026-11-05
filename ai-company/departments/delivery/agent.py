"""Delivery department agent for Lumenhall Partners (DeliveryAgent).

Owns the engagement lifecycle after a deal is won: scoping, staffing humans and AI agents,
kickoff, milestones, scope changes, quality issues, capacity forecasting and budget submission.
Humans stay accountable: every client deliverable is QA-reviewed by a Manager or above before
release (COMPANY.md §4, §9.4); this agent drafts, plans, monitors and proposes.
"""

from __future__ import annotations

import dataclasses
import math

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# ---------------------------------------------------------------------------
# Company facts (copied from COMPANY.md, never invented here)
# ---------------------------------------------------------------------------

# COMPANY.md §3.1 to §3.3: tier -> (service line, list price GBP, duration weeks)
# Keep price is the annual value (12-month minimum term).
TIERS: dict[str, dict] = {
    "compass_spark": {"line": "compass", "price": 45_000, "weeks": 4, "name": "Compass Spark"},
    "compass_sprint": {"line": "compass", "price": 120_000, "weeks": 10, "name": "Compass Sprint"},
    "compass_programme": {"line": "compass", "price": 350_000, "weeks": 26, "name": "Compass Programme"},
    "forge_pilot": {"line": "forge", "price": 90_000, "weeks": 9, "name": "Forge Pilot"},
    "forge_build": {"line": "forge", "price": 260_000, "weeks": 22, "name": "Forge Build"},
    "forge_scale": {"line": "forge", "price": 650_000, "weeks": 44, "name": "Forge Scale"},
    "keep_essential": {"line": "keep", "price": 96_000, "weeks": 52, "name": "Keep Essential"},
    "keep_plus": {"line": "keep", "price": 216_000, "weeks": 52, "name": "Keep Plus"},
    "keep_enterprise": {"line": "keep", "price": 480_000, "weeks": 52, "name": "Keep Enterprise"},
}
DEFAULT_TIER_FOR_LINE = {"compass": "compass_sprint", "forge": "forge_pilot", "keep": "keep_essential"}

# COMPANY.md §3.5 rate card (change orders and extra days only)
RATE_CARD_GBP = {"partner": 2400, "principal": 1800, "manager": 1400, "senior_consultant": 1050,
                 "consultant": 800, "analyst": 550, "ai_agent_day": 350}

# COMPANY.md §6.2 salary bands (base, GBP)
BANDS_GBP = {"analyst": (38_000, 48_000), "consultant": (55_000, 70_000),
             "senior_consultant": (72_000, 90_000), "manager": (92_000, 115_000),
             "principal": (120_000, 155_000), "partner": (160_000, 220_000)}
LOADING = 1.28                      # COMPANY.md §5.4 loaded cost = base x 1.28
PAID_DAYS = 260                     # modelled assumption: weekdays a loaded salary is spread over
AGENT_COST_PER_DAY_GBP = 90         # modelled assumption: compute, tooling and oversight per agent-day

# COMPANY.md §4 billable utilisation targets by level
UTILISATION_TARGET = {"analyst": 0.80, "consultant": 0.80, "senior_consultant": 0.75, "manager": 0.65,
                      "principal": 0.50, "partner": 0.35}
LEVELS = tuple(UTILISATION_TARGET)
LEVEL_TITLES = {"analyst": "Analyst", "consultant": "Consultant", "senior_consultant": "Senior Consultant",
                "manager": "Manager", "principal": "Principal", "partner": "Partner"}

# COMPANY.md §5.4 delivery envelope (GBP): (people, non-people) for FY2026, FY2027, FY2028
BUDGET_GBP = {2026: (1_130_000, 1_850_000), 2027: (3_000_000, 4_400_000), 2028: (8_800_000, 6_200_000)}
# COMPANY.md §6.1 delivery headcount (humans, agents) at year-end
HEADCOUNT_PLAN = {2026: (14, 6), 2027: (46, 22), 2028: (104, 52)}

# COMPANY.md §7: milestone billing 30% signature, 40% mid-point, 30% acceptance
MILESTONE_PCT = {"mid_point_review": 40, "acceptance": 30}

# Modelled staffing templates: FTE per level over the engagement, AI agents, human lead level.
# COMPANY.md §4: Forge Build typical team is 1 Principal (part time), 1 Manager, 2 Senior Consultants,
# 1 Consultant and 3 to 5 agents; FTE below are time-averaged allocations.
TEAMS: dict[str, dict] = {
    "compass_spark": {"fte": {"principal": 0.1, "manager": 0.4, "senior_consultant": 1.0, "consultant": 0.5},
                      "agents": 1},
    "compass_sprint": {"fte": {"principal": 0.15, "manager": 0.5, "senior_consultant": 1.0,
                               "consultant": 1.0}, "agents": 2},
    "compass_programme": {"fte": {"principal": 0.15, "manager": 0.5, "senior_consultant": 1.0,
                                  "consultant": 1.0, "analyst": 0.5}, "agents": 3},
    "forge_pilot": {"fte": {"principal": 0.1, "manager": 0.4, "senior_consultant": 1.0, "consultant": 0.6},
                    "agents": 2},
    "forge_build": {"fte": {"principal": 0.1, "manager": 0.5, "senior_consultant": 1.5, "consultant": 1.0},
                    "agents": 4},
    "forge_scale": {"fte": {"principal": 0.2, "manager": 0.8, "senior_consultant": 2.0, "consultant": 1.5,
                            "analyst": 0.5}, "agents": 6},
    "keep_essential": {"fte": {"manager": 0.1, "consultant": 0.3}, "agents": 1},
    "keep_plus": {"fte": {"manager": 0.2, "senior_consultant": 0.4, "consultant": 0.3}, "agents": 2},
    "keep_enterprise": {"fte": {"manager": 0.5, "senior_consultant": 1.0, "consultant": 1.0}, "agents": 3},
}

# Modelled starting roster at simulation day 0 (humans excluding the department head), and AI agents.
INITIAL_ROSTER = {"partner": 1, "principal": 1, "manager": 2, "senior_consultant": 3, "consultant": 2,
                  "analyst": 1}
INITIAL_AGENTS = 3

MARGIN_FLOOR_PCT = 35.0             # engagement gross margin below which scoping flags a pricing risk
SCOPING_DAYS = {"compass": 2, "forge": 4, "keep": 3}
HIRE_LEAD_DAYS = 56                 # modelled time to fill a delivery role
CONTRACTOR_LEAD_DAYS = 10           # modelled time to bring on a subcontractor
FORECAST_EVERY_DAYS = 14
HIRE_REQUEST_COOLDOWN_DAYS = 28
QUALITY_REMEDIATION_DAYS = {"low": 3, "medium": 7, "high": 10, "critical": 14}

# FY2026 targets, mirrored in kpis.md. Names are the snake_case KPI ids.
KPIS = [
    Kpi("billable_utilisation_pct", "percent", 70.0, None),                 # COMPANY.md §4
    Kpi("engagement_gross_margin_pct", "percent", 45.0, None),
    Kpi("on_time_milestone_pct", "percent", 90.0, None),
    Kpi("client_csat", "score_out_of_5", 4.4, None),
    Kpi("qa_first_pass_rate_pct", "percent", 85.0, None),
    Kpi("scope_change_capture_pct", "percent", 80.0, None),
    Kpi("scoping_turnaround_days", "days", 3.0, None, False),
    Kpi("time_to_staff_days", "days", 10.0, None, False),
    Kpi("ai_agent_leverage_ratio", "agents_per_human", 0.5, None),          # COMPANY.md §2
    Kpi("quality_issues_per_engagement", "count", 0.3, None, False),
]


def _norm(value: object) -> str:
    """Normalise free text such as 'Forge Build' to 'forge_build'."""
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _round(value: float, places: int = 1) -> float:
    return round(value, places)


class DeliveryAgent(DepartmentAgent):
    """Managing Partner, Delivery's digital colleague: scoping, staffing, milestones and quality."""

    SUBSCRIBES = subscribes_for("delivery")
    PUBLISHES = publishes_for("delivery")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.state.update({
            "engagements": {},                       # EN id -> engagement record
            "scoped": {},                            # proposal_id -> scoping record
            "pipeline": [],                          # qualified leads (weighted demand)
            "roster": dict(INITIAL_ROSTER),          # level -> humans (excluding head)
            "agents": INITIAL_AGENTS,
            "seq": {"EN": 0, "QI": 0, "CO": 0},
            "quality_issues": {},
            "change_orders": {},
            "hire_requests": {},                     # level -> {"day": int, "count": int}
            "last_forecast_day": -FORECAST_EVERY_DAYS,
            "crisis_mode": False,
            "strategy": {},
            "okrs": [],
            "benchmarks": {},
            "external_forecast": {},
            "capabilities": [],
            "budgets": {},
            "metrics": {"milestones": 0, "on_time": 0, "qa_checked": 0, "qa_first_pass": 0, "csat": [],
                        "margins": [], "scoping_days": [], "staffing_days": [], "scope_requests": 0,
                        "scope_converted": 0, "quality_issues": 0, "completed": 0},
        })
        self._handlers = {
            "sales.proposal_requested": self._on_proposal_requested,
            "sales.lead_qualified": self._on_lead_qualified,
            "sales.deal_won": self._on_deal_won,
            "legal.contract_signed": self._on_contract_signed,
            "finance.billing_schedule_created": self._on_billing_schedule,
            "people.new_hire_started": self._on_new_hire,
            "external.client_scope_request": self._on_scope_request,
            "customer_success.support_escalated": self._on_support_escalated,
            "customer_success.feedback_received": self._on_feedback,
            "customer_success.health_score_updated": self._on_health_score,
            "customer_success.churn_risk_flagged": self._on_churn_risk,
            "customer_success.renewal_confirmed": self._on_renewal_confirmed,
            "data.agent_quality_report_published": self._on_agent_quality_report,
            "data.benchmark_ready": self._on_benchmark,
            "data.forecast_updated": self._on_forecast,
            "legal.client_dispute_raised": self._on_dispute,
            "it_security.incident_detected": self._on_security_incident,
            "finance.budget_cycle_opened": self._on_budget_cycle,
            "executive.budget_approved": self._on_budget_approved,
            "executive.crisis_declared": self._on_crisis,
            "executive.okrs_set": self._on_okrs,
            "executive.strategy_updated": self._on_strategy,
            "people.engagement_survey_completed": self._on_survey,
            "product.agent_capability_added": self._on_capability,
            "product.release_shipped": self._on_release,
            "product.roadmap_published": self._on_roadmap,
        }

    # ------------------------------------------------------------------ dispatch
    def handle(self, message: Message) -> list[Message]:
        handler = self._handlers.get(message.topic)
        if handler is None:
            self.log_event("delivery.activity.unhandled_topic", f"no handler for {message.topic}")
            return []
        return handler(message)

    # ------------------------------------------------------------------ helpers
    def _next(self, prefix: str, width: int = 4) -> str:
        seq = self.state["seq"]
        seq[prefix] += 1
        return f"{prefix}-{seq[prefix]:0{width}d}"

    def _tier_of(self, body: dict) -> str:
        """Resolve a tier key from body tier / service_line / amount_gbp."""
        tier = _norm(body.get("tier"))
        if tier in TIERS:
            return tier
        line = _norm(body.get("service_line"))
        candidates = [k for k, v in TIERS.items() if not line or v["line"] == line] or list(TIERS)
        amount = body.get("amount_gbp")
        if isinstance(amount, (int, float)) and amount > 0:
            def gap(key: str) -> float:
                price = TIERS[key]["price"]
                spans = [price, price / 12] if TIERS[key]["line"] == "keep" else [price]
                return min(abs(price_ - amount) for price_ in spans)
            return min(candidates, key=gap)
        return DEFAULT_TIER_FOR_LINE.get(line, "compass_sprint")

    def _day_cost(self, level: str) -> float:
        low, high = BANDS_GBP[level]
        return (low + high) / 2 * LOADING / PAID_DAYS

    def _plan_cost(self, tier: str) -> dict:
        """Direct cost of the staffing template: humans at loaded mid-band, agents at modelled cost."""
        spec, team = TIERS[tier], TEAMS[tier]
        weeks = spec["weeks"]
        human = sum(self._day_cost(lv) * fte * weeks * 5 for lv, fte in team["fte"].items())
        agent = AGENT_COST_PER_DAY_GBP * team["agents"] * weeks * 5
        human_days = sum(team["fte"].values()) * weeks * 5
        cost = human + agent
        margin = (spec["price"] - cost) / spec["price"] * 100
        return {"human_cost_gbp": int(human), "agent_cost_gbp": int(agent), "cost_gbp": int(cost),
                "margin_pct": _round(margin), "human_days": _round(human_days),
                "agent_days": team["agents"] * weeks * 5}

    def _alloc_totals(self) -> dict[str, float]:
        totals = {lv: 0.0 for lv in LEVELS}
        for eng in self.state["engagements"].values():
            if eng["status"] in ("staffed", "active"):
                for lv, fte in eng["alloc"].items():
                    totals[lv] += fte
        return totals

    def _free_capacity(self) -> dict[str, float]:
        """Billable FTE still free by level (headcount x utilisation target minus allocations)."""
        alloc = self._alloc_totals()
        return {lv: self.state["roster"].get(lv, 0) * UTILISATION_TARGET[lv] - alloc[lv] for lv in LEVELS}

    def _shortfall(self, tier: str) -> dict[str, float]:
        free = self._free_capacity()
        gaps = {}
        for lv, fte in TEAMS[tier]["fte"].items():
            gap = fte - max(free[lv], 0.0)
            if gap > 0.05:
                gaps[lv] = _round(gap, 2)
        return gaps

    def _utilisation_pct(self) -> float:
        humans = sum(self.state["roster"].values())
        return _round(sum(self._alloc_totals().values()) / humans * 100) if humans else 0.0

    def _find_engagement(self, body: dict) -> dict | None:
        engs = self.state["engagements"]
        eid = body.get("engagement_id")
        if eid in engs:
            return engs[eid]
        for key in ("deal_id", "contract_id"):
            ref = body.get(key)
            if ref:
                for eng in engs.values():
                    if eng.get(key) == ref:
                        return eng
        cid = body.get("client_id")
        if cid:
            live = [e for e in engs.values() if e["client_id"] == cid and e["status"] != "completed"]
            if live:
                return live[-1]
        return None

    def _new_engagement(self, body: dict) -> dict:
        tier = self._tier_of(body)
        spec = TIERS[tier]
        eid = body.get("engagement_id") or self._next("EN")
        fee = int(body.get("amount_gbp") or spec["price"])
        if spec["line"] == "keep" and fee < spec["price"]:
            fee = spec["price"]      # a monthly figure was supplied; engagement fee is annual value
        eng = {
            "id": eid, "client_id": body.get("client_id"), "client_name": body.get("client_name"),
            "deal_id": body.get("deal_id"), "contract_id": body.get("contract_id"),
            "proposal_id": body.get("proposal_id"), "tier": tier, "service_line": spec["line"],
            "fee_gbp": fee, "status": "won", "contract_signed": False, "billing_ready": False,
            "won_day": self.clock.day, "staffing_day": None, "start_day": None, "end_day": None,
            "milestones": [], "holds": {}, "alloc": {}, "agents": 0, "change_orders": [],
            "quality_issues": [], "slipped_days": 0, "qi_since_milestone": 0, "plan": self._plan_cost(tier),
            "kickoff_sent": False,
        }
        self.state["engagements"][eid] = eng
        self.create_task(f"Name engagement lead and QA reviewer for {eid} ({spec['name']})", 3, "high")
        return eng

    def _milestones_for(self, eng: dict) -> list[dict]:
        start, tier = eng["start_day"], eng["tier"]
        days = TIERS[tier]["weeks"] * 7
        if eng["service_line"] == "keep":
            monthly = eng["fee_gbp"] // 12
            return [{"name": "monthly_service_review", "no": i, "pct": 0, "amount_gbp": monthly,
                     "billable": False, "due": start + 30 * i, "done": False} for i in range(1, 13)]
        mid = start + round(days * 0.5)
        end = start + days
        return [
            {"name": "mid_point_review", "no": 1, "pct": MILESTONE_PCT["mid_point_review"], "billable": True,
             "due": mid, "done": False},
            {"name": "acceptance", "no": 2, "pct": MILESTONE_PCT["acceptance"], "billable": True,
             "due": end, "done": False},
        ]

    def _record_quality_issue(self, eng: dict | None, body: dict, source: str, severity: str,
                              summary: str, root_cause: str, ref: str | None = None) -> list[Message]:
        """Open a quality issue, hold the next milestone, emit delivery.quality_issue_raised."""
        key = (eng["id"] if eng else body.get("client_id"), source, ref)
        seen = self.state["quality_issues"]
        if any(q["key"] == key for q in seen.values()):
            self.log_event("delivery.activity.quality_issue_deduplicated", f"{source} already tracked",
                           source=source)
            return []
        qid = self._next("QI")
        days = QUALITY_REMEDIATION_DAYS[severity]
        resolve_day = self.clock.day + days
        seen[qid] = {"key": key, "id": qid, "source": source, "severity": severity, "status": "open",
                     "opened_day": self.clock.day, "resolve_day": resolve_day}
        self.state["metrics"]["quality_issues"] += 1
        if eng:
            eng["quality_issues"].append(qid)
            eng["qi_since_milestone"] += 1
            if severity in ("medium", "high", "critical"):
                eng["holds"][f"quality:{qid}"] = resolve_day
        self.create_task(f"Remediate {qid} ({severity}): {summary}", days,
                         "critical" if severity == "critical" else "high" if severity == "high" else "medium")
        msg = self.emit("delivery.quality_issue_raised", {
            "quality_issue_id": qid,
            "engagement_id": eng["id"] if eng else body.get("engagement_id"),
            "client_id": eng["client_id"] if eng else body.get("client_id"),
            "service_line": eng["service_line"] if eng else body.get("service_line"),
            "severity": severity, "summary": summary, "source": source, "root_cause": root_cause,
            "remediation_due_day": resolve_day,
            "owner": "Delivery Manager (human QA owner)",
            "milestone_hold": bool(eng and severity in ("medium", "high", "critical")),
        })
        return [msg]

    # ------------------------------------------------------------------ scoping
    def _on_proposal_requested(self, msg: Message) -> list[Message]:
        body = msg.body
        tier = self._tier_of(body)
        spec, team = TIERS[tier], TEAMS[tier]
        plan = self._plan_cost(tier)
        shortfall = self._shortfall(tier)
        lead_days = 0
        if shortfall:
            lead_days = CONTRACTOR_LEAD_DAYS if max(shortfall.values()) <= 1.0 else HIRE_LEAD_DAYS
        price = int(body.get("amount_gbp") or spec["price"])
        discount_pct = _round((1 - price / spec["price"]) * 100) if price < spec["price"] else 0.0
        risks = {
            "compass": ["Sponsor availability for interviews", "Data access for the diagnostic"],
            "forge": ["Client system access and API readiness", "Data quality in source systems",
                      "AI risk review needed before go-live"],
            "keep": ["Handover from build team to run team", "Incident cover hours match client expectation"],
        }[spec["line"]]
        if plan["margin_pct"] < MARGIN_FLOOR_PCT:
            risks.append(f"Modelled margin {plan['margin_pct']}% below {MARGIN_FLOOR_PCT}% floor")
        if shortfall:
            gaps = ", ".join(f"{lv} {gap} FTE" for lv, gap in shortfall.items())
            risks.append("Staffing shortfall: " + gaps)
        note = self.ask_llm(f"Summarise the delivery approach for a {spec['name']} "
                            f"for {body.get('client_name')}.")
        delay = SCOPING_DAYS[spec["line"]]
        self.state["scoped"][body.get("proposal_id") or msg.id] = {"tier": tier, "day": self.clock.day}
        self.state["metrics"]["scoping_days"].append(delay)
        self.create_task(f"Principal review of scoping for {body.get('proposal_id') or body.get('deal_id')}",
                         delay, "high")
        self.log_event("delivery.activity.scoping_started", f"scoping {spec['name']}", tier=tier,
                       margin_pct=plan["margin_pct"])
        out = self.emit("delivery.scoping_completed", {
            "proposal_id": body.get("proposal_id"), "deal_id": body.get("deal_id"),
            "client_id": body.get("client_id"), "client_name": body.get("client_name"),
            "service_line": spec["line"], "tier": tier, "duration_weeks": spec["weeks"],
            "list_price_gbp": spec["price"], "amount_gbp": price, "discount_pct": discount_pct,
            "team_fte": dict(team["fte"]), "ai_agents": team["agents"],
            "effort_human_days": plan["human_days"], "effort_agent_days": plan["agent_days"],
            "estimated_cost_gbp": plan["cost_gbp"], "estimated_margin_pct": plan["margin_pct"],
            "margin_floor_breached": plan["margin_pct"] < MARGIN_FLOOR_PCT,
            "staffing_shortfall_fte": shortfall, "earliest_start_offset_days": delay + lead_days,
            "risks": risks, "assumptions": ["Fixed fee; changes via signed change order at rate card",
                                           "Client SME time of 2 days per week",
                                           "Every deliverable passes Manager-or-above QA before release"],
            "scoping_note": str(note)[:240], "qa_reviewer_level": "manager",
            "executive_approval_likely": price >= 500_000,
        }, delay_days=delay)
        return [out]

    def _on_lead_qualified(self, msg: Message) -> list[Message]:
        body = msg.body
        tier = self._tier_of(body)
        prob = float(body.get("probability", 0.3) or 0.3)
        self.state["pipeline"].append({"lead_id": body.get("lead_id"), "client_id": body.get("client_id"),
                                       "tier": tier, "prob": min(max(prob, 0.0), 1.0),
                                       "day": self.clock.day})
        self.create_task(f"Pre-scoping call with {body.get('company') or body.get('client_name') or 'lead'}",
                         5, "low")
        self.log_event("delivery.activity.pipeline_noted", f"qualified lead as {TIERS[tier]['name']}",
                       tier=tier, lead_id=body.get("lead_id"))
        return []

    # ------------------------------------------------------------------ win to kickoff
    def _on_deal_won(self, msg: Message) -> list[Message]:
        body = msg.body
        eng = self._find_engagement(body)
        if eng is None:
            eng = self._new_engagement(body)
        else:
            eng["deal_id"] = eng["deal_id"] or body.get("deal_id")
        self.state["pipeline"] = [p for p in self.state["pipeline"]
                                  if p.get("client_id") is None or p["client_id"] != body.get("client_id")]
        if eng["fee_gbp"] >= 500_000:
            self.create_task(f"Partner sponsor and steering committee for {eng['id']}", 5, "high")
        self.log_event("delivery.activity.engagement_opened", f"{eng['id']} opened for {eng['tier']}",
                       engagement_id=eng["id"], fee_gbp=eng["fee_gbp"])
        return []

    def _on_contract_signed(self, msg: Message) -> list[Message]:
        body = msg.body
        co_id = body.get("change_order_id")
        if co_id or _norm(body.get("contract_type") or body.get("type")) == "change_order":
            return self._on_change_order_signed(msg)
        eng = self._find_engagement(body) or self._new_engagement(body)
        eng["contract_signed"] = True
        eng["contract_id"] = body.get("contract_id") or eng["contract_id"]
        eng["client_id"] = eng["client_id"] or body.get("client_id")
        out: list[Message] = []
        if eng["status"] == "won":
            out += self._request_staffing(eng, msg)
        out += self._maybe_kickoff(eng, msg)
        return out

    def _request_staffing(self, eng: dict, msg: Message) -> list[Message]:
        tier = eng["tier"]
        team = TEAMS[tier]
        shortfall = self._shortfall(tier)
        lead = 0
        if shortfall:
            lead = CONTRACTOR_LEAD_DAYS if max(shortfall.values()) <= 1.0 else HIRE_LEAD_DAYS
        eng["alloc"] = dict(team["fte"])
        eng["agents"] = team["agents"]
        eng["status"] = "staffed"
        eng["staffing_day"] = self.clock.day
        eng["staff_lead_days"] = 3 + lead
        self.state["metrics"]["staffing_days"].append(3 + lead)
        self.state["agents"] = max(self.state["agents"], self._agents_in_use())
        out: list[Message] = []
        out.append(self.emit("delivery.staffing_requested", {
            "engagement_id": eng["id"], "client_id": eng["client_id"], "contract_id": eng["contract_id"],
            "service_line": eng["service_line"], "tier": tier, "duration_weeks": TIERS[tier]["weeks"],
            "team": [{"level": lv, "title": LEVEL_TITLES[lv], "fte": fte} for lv, fte in team["fte"].items()],
            "ai_agents": team["agents"], "needed_by_day": self.clock.day + 3 + lead,
            "shortfall_fte": shortfall, "sourcing": ("internal bench" if not shortfall else
                                                     "subcontractor" if lead == CONTRACTOR_LEAD_DAYS
                                                     else "hire or subcontractor"),
            "workspace_needs": ["client project workspace", "agent sandbox", "least-privilege client access"],
            "summary": f"Staff {TIERS[tier]['name']} for {eng['client_name'] or eng['client_id']}",
        }, reply_to=msg.id))
        for lv, gap in shortfall.items():
            out += self._maybe_request_hire(lv, gap, f"shortfall on {eng['id']}", eng["id"])
        self.create_task(f"Confirm named team and agent owners for {eng['id']}", 3, "high")
        return out

    def _agents_in_use(self) -> int:
        return sum(e["agents"] for e in self.state["engagements"].values()
                   if e["status"] in ("staffed", "active"))

    def _on_billing_schedule(self, msg: Message) -> list[Message]:
        eng = self._find_engagement(msg.body)
        if eng is None:
            self.log_event("delivery.activity.billing_schedule_orphan", "no matching engagement",
                           contract_id=msg.body.get("contract_id"))
            return []
        eng["billing_ready"] = True
        return self._maybe_kickoff(eng, msg)

    def _maybe_kickoff(self, eng: dict, msg: Message) -> list[Message]:
        if eng["kickoff_sent"] or not (eng["contract_signed"] and eng["billing_ready"]):
            return []
        if eng["status"] == "won":
            return []
        eng["kickoff_sent"] = True
        lead = int(eng.get("staff_lead_days", 5))
        start = self.clock.day + max(lead, 5)
        eng["start_day"] = start
        eng["end_day"] = start + TIERS[eng["tier"]]["weeks"] * 7
        eng["milestones"] = self._milestones_for(eng)
        eng["status"] = "active"
        lead_level = "principal" if eng["fee_gbp"] >= 250_000 else "manager"
        team = TEAMS[eng["tier"]]
        self.log_event("delivery.activity.kickoff_scheduled", f"{eng['id']} starts day {start}",
                       engagement_id=eng["id"], start_day=start)
        return [self.emit("delivery.engagement_kickoff", {
            "engagement_id": eng["id"], "client_id": eng["client_id"], "client_name": eng["client_name"],
            "contract_id": eng["contract_id"], "deal_id": eng["deal_id"],
            "service_line": eng["service_line"], "tier": eng["tier"], "amount_gbp": eng["fee_gbp"],
            "start_day": start, "end_day": eng["end_day"], "duration_weeks": TIERS[eng["tier"]]["weeks"],
            "engagement_lead_level": lead_level, "qa_reviewer_level": "manager",
            "ai_agents": team["agents"], "team_fte": dict(team["fte"]),
            "milestones": [{"name": m["name"], "due_day": m["due"], "billing_pct": m["pct"]}
                           for m in eng["milestones"][:2]],
            "needs_workspace": True, "needs_access": True,
            "summary": f"Kickoff {TIERS[eng['tier']]['name']} for {eng['client_name'] or eng['client_id']}",
        }, reply_to=msg.id, delay_days=2)]

    def _on_new_hire(self, msg: Message) -> list[Message]:
        body = msg.body
        dept = body.get("department")
        if dept not in (None, "delivery"):
            self.log_event("delivery.activity.new_hire_other_department", f"ignored hire for {dept}")
            return []
        level = _norm(body.get("level"))
        if level not in LEVELS:
            title = _norm(body.get("role") or body.get("title"))
            level = next((lv for lv in LEVELS if lv in title), "consultant")
        count = int(body.get("count", 1) or 1)
        self.state["roster"][level] = self.state["roster"].get(level, 0) + count
        req = self.state["hire_requests"].get(level)
        if req:
            req["count"] = max(0, req["count"] - count)
        self.create_task(f"Onboard {LEVEL_TITLES[level]} into delivery bench with buddy and QA shadowing",
                         10, "medium")
        self.log_event("delivery.activity.bench_updated", f"+{count} {level}",
                       roster=dict(self.state["roster"]), utilisation_pct=self._utilisation_pct())
        return []

    # ------------------------------------------------------------------ scope changes
    def _on_scope_request(self, msg: Message) -> list[Message]:
        body = msg.body
        self.state["metrics"]["scope_requests"] += 1
        eng = self._find_engagement(body)
        desc = str(body.get("description") or body.get("summary") or "client scope request")
        human_days = float(body.get("estimated_days") or min(40, 3 + len(desc) // 40))
        mix = {"manager": 0.2, "senior_consultant": 0.5, "consultant": 0.3}
        agent_days = _round(human_days * 0.6)
        value = sum(RATE_CARD_GBP[lv] * human_days * share for lv, share in mix.items())
        value += RATE_CARD_GBP["ai_agent_day"] * agent_days
        value = int(round(value, -1))
        fee = eng["fee_gbp"] if eng else 0
        absorbable = human_days <= 2 or (fee and value < 0.02 * fee)
        if absorbable:
            self.state["metrics"]["scope_converted"] += 1     # handled inside tolerance, no leakage
            self.log_event("delivery.activity.scope_absorbed",
                           f"{human_days} days absorbed within tolerance", value_gbp=value,
                           engagement_id=eng["id"] if eng else None)
            self.create_task("Log absorbed scope item and set expectation with client sponsor", 2, "low")
            return []
        team_fte = sum(eng["alloc"].values()) if eng and eng["alloc"] else 3.0
        impact = max(1, math.ceil(human_days / max(team_fte, 1.0)))
        co_id = self._next("CO")
        self.state["change_orders"][co_id] = {"id": co_id, "engagement_id": eng["id"] if eng else None,
                                              "value_gbp": value, "impact_days": impact, "status": "proposed",
                                              "human_days": human_days, "agent_days": agent_days}
        if eng:
            eng["change_orders"].append(co_id)
        self.create_task(f"Hold out-of-scope work on {co_id} until change order is signed", 1, "high")
        return [self.emit("delivery.scope_change_requested", {
            "change_order_id": co_id, "engagement_id": eng["id"] if eng else body.get("engagement_id"),
            "client_id": eng["client_id"] if eng else body.get("client_id"),
            "contract_id": eng["contract_id"] if eng else body.get("contract_id"),
            "service_line": eng["service_line"] if eng else None,
            "summary": desc[:200], "extra_human_days": human_days, "extra_agent_days": agent_days,
            "rate_basis": "rate card", "amount_gbp": value, "schedule_impact_days": impact,
            "requires_signature_before_work": True,
            "requested_by": body.get("requested_by", "client sponsor"),
            "urgency": body.get("urgency", "normal"),
        }, reply_to=msg.id)]

    def _on_change_order_signed(self, msg: Message) -> list[Message]:
        body = msg.body
        co = self.state["change_orders"].get(body.get("change_order_id"))
        if co is None:
            self.log_event("delivery.activity.change_order_unknown", "signed change order not tracked",
                           change_order_id=body.get("change_order_id"))
            return []
        co["status"] = "signed"
        self.state["metrics"]["scope_converted"] += 1
        eng = self.state["engagements"].get(co["engagement_id"])
        if eng:
            eng["fee_gbp"] += co["value_gbp"]
            for m in eng["milestones"]:
                if not m["done"] and m["name"] != "monthly_service_review":
                    m["due"] += co["impact_days"]
            if eng["end_day"]:
                eng["end_day"] += co["impact_days"]
        self.log_event("delivery.activity.change_order_signed", f"{co['id']} signed, work released",
                       change_order_id=co["id"], value_gbp=co["value_gbp"])
        return []

    # ------------------------------------------------------------------ quality and client health
    def _on_support_escalated(self, msg: Message) -> list[Message]:
        body = msg.body
        eng = self._find_engagement(body)
        sev = body.get("severity") if body.get("severity") in QUALITY_REMEDIATION_DAYS else "medium"
        return self._record_quality_issue(
            eng, body, "support_escalation", sev,
            str(body.get("summary") or "Client support escalation on delivered work"),
            "To be confirmed in root-cause review", ref=body.get("ticket_id") or msg.id)

    def _on_feedback(self, msg: Message) -> list[Message]:
        body = msg.body
        score = body.get("csat", body.get("score"))
        if not isinstance(score, (int, float)):
            self.log_event("delivery.activity.feedback_logged", "qualitative feedback recorded")
            return []
        if score > 5:                              # NPS-style 0 to 10 scores normalised to 5
            score = score / 2
        self.state["metrics"]["csat"].append(float(score))
        eng = self._find_engagement(body)
        if score <= 3.0:
            sev = "high" if score <= 2.0 else "medium"
            return self._record_quality_issue(eng, body, "client_feedback", sev,
                                              str(body.get("comment") or body.get("summary")
                                                  or f"Low client satisfaction score {score}"),
                                              "Expectation gap or deliverable quality", ref=msg.id)
        self.log_event("delivery.activity.feedback_logged", f"CSAT {score} recorded", csat=score)
        return []

    def _on_health_score(self, msg: Message) -> list[Message]:
        body = msg.body
        score = body.get("health_score", body.get("score"))
        eng = self._find_engagement(body)
        if isinstance(score, (int, float)) and score < 60:
            self.create_task(f"Partner call with sponsor: health score {score} for "
                             f"{body.get('client_id') or 'client'}", 3, "high")
            if eng:
                self.log_event("delivery.activity.health_watch", f"{eng['id']} on watch, score {score}",
                               engagement_id=eng["id"])
            return []
        self.log_event("delivery.activity.health_noted", f"health score {score}", score=score)
        return []

    def _on_churn_risk(self, msg: Message) -> list[Message]:
        body = msg.body
        eng = self._find_engagement(body)
        drivers = " ".join(str(d) for d in (body.get("drivers") or [body.get("reason") or ""])).lower()
        self.create_task(f"Recovery plan for churn risk at {body.get('client_id') or 'client'}", 5, "high")
        if any(w in drivers for w in ("delivery", "quality", "delay", "milestone", "deliverable")):
            return self._record_quality_issue(
                eng, body, "churn_risk", "high" if body.get("severity") in ("high", "critical") else "medium",
                f"Churn risk linked to delivery: {drivers[:120]}", "Delivery performance cited by client",
                ref=msg.id)
        self.log_event("delivery.activity.churn_risk_noted", "not delivery-driven; supporting CS plan")
        return []

    def _on_renewal_confirmed(self, msg: Message) -> list[Message]:
        body = msg.body
        tier = self._tier_of(body)
        if TIERS[tier]["line"] != "keep":
            self.log_event("delivery.activity.renewal_noted", "non-Keep renewal, no delivery action")
            return []
        eng = self._find_engagement(body)
        if eng and eng["service_line"] == "keep" and eng["status"] != "completed":
            if eng["end_day"]:
                eng["end_day"] += 365
            self.log_event("delivery.activity.keep_term_extended", f"{eng['id']} extended 12 months",
                           engagement_id=eng["id"])
            return []
        new = self._new_engagement({**body, "tier": tier})
        new["contract_signed"] = True
        new["billing_ready"] = True
        out = self._request_staffing(new, msg)
        out += self._maybe_kickoff(new, msg)
        return out

    def _on_agent_quality_report(self, msg: Message) -> list[Message]:
        body = msg.body
        score = body.get("quality_score_pct", body.get("accuracy_pct", body.get("score")))
        self.state["agent_quality"] = {"day": self.clock.day, "score": score}
        eng = self._find_engagement(body)
        below = body.get("below_threshold") or (isinstance(score, (int, float)) and score < 90)
        if not below:
            self.log_event("delivery.activity.agent_quality_ok", f"agent quality {score}")
            return []
        sev = "high" if isinstance(score, (int, float)) and score < 80 else "medium"
        return self._record_quality_issue(
            eng, body, "agent_quality_report", sev,
            f"AI agent output quality {score} below 90 threshold ({body.get('agent_id') or 'agent'})",
            "Agent output drift or inadequate human QA sampling", ref=body.get("report_id") or msg.id)

    def _on_dispute(self, msg: Message) -> list[Message]:
        body = msg.body
        eng = self._find_engagement(body)
        sev = body.get("severity") if body.get("severity") in QUALITY_REMEDIATION_DAYS else "high"
        out = self._record_quality_issue(eng, body, "client_dispute", sev,
                                         str(body.get("summary") or "Client dispute on delivery"),
                                         "Under legal review", ref=body.get("dispute_id") or msg.id)
        if eng:
            eng["holds"]["dispute"] = self.clock.day + 21
        self.create_task("Preserve engagement records and QA evidence for legal", 2, "high")
        return out

    def _on_security_incident(self, msg: Message) -> list[Message]:
        body = msg.body
        sev = body.get("severity") if body.get("severity") in QUALITY_REMEDIATION_DAYS else "medium"
        eng = self._find_engagement(body)
        self.create_task("Suspend and rotate AI agent credentials on affected engagements", 1,
                         "critical" if sev in ("high", "critical") else "high")
        if sev in ("high", "critical") and (eng or body.get("client_data_affected")):
            summary = str(body.get("summary") or "Security incident affecting delivery")
            return self._record_quality_issue(eng, body, "security_incident", sev, summary,
                                              "Security incident; see IT Security",
                                              ref=body.get("incident_id") or msg.id)
        self.log_event("delivery.activity.incident_noted", f"incident {sev} noted, no client impact")
        return []

    # ------------------------------------------------------------------ planning inputs
    def _on_benchmark(self, msg: Message) -> list[Message]:
        self.state["benchmarks"].update(msg.body.get("benchmarks", {k: v for k, v in msg.body.items()
                                                                    if isinstance(v, (int, float))}))
        self.log_event("delivery.activity.benchmark_loaded", "benchmarks stored for scoping calibration")
        return []

    def _on_forecast(self, msg: Message) -> list[Message]:
        self.state["external_forecast"] = {k: v for k, v in msg.body.items() if isinstance(v, (int, float))}
        self.log_event("delivery.activity.demand_forecast_loaded", "company forecast stored")
        return []

    def _on_survey(self, msg: Message) -> list[Message]:
        score = msg.body.get("engagement_score", msg.body.get("score"))
        if isinstance(score, (int, float)) and score < 70:
            self.create_task("Delivery team survey follow-up: workload and utilisation review", 10, "medium")
        self.log_event("delivery.activity.survey_noted", f"survey score {score}")
        return []

    def _on_capability(self, msg: Message) -> list[Message]:
        self.state["capabilities"].append(msg.body.get("capability") or msg.body.get("summary") or msg.id)
        self.create_task("Assess new agent capability for in-flight and scoped engagements", 10, "medium")
        self.log_event("delivery.activity.capability_noted", "new agent capability recorded")
        return []

    def _on_release(self, msg: Message) -> list[Message]:
        if msg.body.get("breaking_change"):
            self.create_task("Regression-test client agents against breaking platform release", 5, "high")
        self.log_event("delivery.activity.release_noted", f"release {msg.body.get('version', '')} noted")
        return []

    def _on_roadmap(self, msg: Message) -> list[Message]:
        self.log_event("delivery.activity.roadmap_noted", "product roadmap noted for scoping")
        return []

    # ------------------------------------------------------------------ governance and budget
    def _fiscal_year(self, body: dict) -> int:
        fy = body.get("fiscal_year")
        if isinstance(fy, int):
            return min(max(fy, 2026), 2028)
        d = self.clock.date
        return min(max(d.year + (1 if d.month >= 10 else 0), 2026), 2028)

    def _on_budget_cycle(self, msg: Message) -> list[Message]:
        fy = self._fiscal_year(msg.body)
        people, other = BUDGET_GBP[fy]
        humans, agents = HEADCOUNT_PLAN[fy]
        self.create_task(f"Prepare FY{fy} delivery budget pack for Managing Partner sign-off", 5, "high")
        return [self.emit("delivery.budget_submitted", {
            "budget_cycle_id": msg.body.get("budget_cycle_id") or f"BUD-{fy}", "fiscal_year": fy,
            "department": "delivery", "people_gbp": people, "non_people_gbp": other,
            "amount_gbp": people + other, "headcount_humans": humans, "headcount_agents": agents,
            "summary": f"Delivery FY{fy} budget: people, AI compute and tooling, subcontractors, T&E",
        }, recipient="finance", reply_to=msg.id, delay_days=3)]

    def _on_budget_approved(self, msg: Message) -> list[Message]:
        body = msg.body
        approved = body.get("budgets", {}).get("delivery") if isinstance(body.get("budgets"), dict) else None
        approved = approved or body.get("delivery_amount_gbp")
        self.state["budgets"][body.get("budget_cycle_id") or f"FY{self.clock.date.year}"] = approved
        self.log_event("delivery.activity.budget_approved", "approved budget recorded", approved_gbp=approved)
        return []

    def _on_crisis(self, msg: Message) -> list[Message]:
        self.state["crisis_mode"] = True
        self.create_task("Crisis posture: confirm client commitments, pause discretionary hiring", 1,
                         "critical")
        self.log_event("delivery.activity.crisis_posture", "crisis mode set", crisis=msg.body.get("summary"))
        return []

    def _on_okrs(self, msg: Message) -> list[Message]:
        okrs = msg.body.get("okrs") or msg.body.get("objectives") or []
        self.state["okrs"] = okrs
        self.log_event("delivery.activity.okrs_recorded", f"{len(okrs)} company OKRs recorded")
        return []

    def _on_strategy(self, msg: Message) -> list[Message]:
        self.state["strategy"] = {k: v for k, v in msg.body.items() if isinstance(v, (str, int, float, list))}
        self.log_event("delivery.activity.strategy_recorded", "strategy update recorded")
        return []

    # ------------------------------------------------------------------ hiring and capacity
    def _maybe_request_hire(self, level: str, gap_fte: float, reason: str,
                            engagement_id: str | None = None) -> list[Message]:
        if self.state["crisis_mode"]:
            return []
        req = self.state["hire_requests"].get(level)
        if req and req["count"] > 0 and self.clock.day - req["day"] < HIRE_REQUEST_COOLDOWN_DAYS:
            return []
        count = max(1, math.ceil(gap_fte / UTILISATION_TARGET[level]))
        self.state["hire_requests"][level] = {"day": self.clock.day, "count": count}
        low, high = BANDS_GBP[level]
        return [self.emit("delivery.hire_requested", {
            "department": "delivery", "role": f"{LEVEL_TITLES[level]}, Delivery", "level": level,
            "count": count, "salary_band_gbp": [low, high], "reason": reason,
            "engagement_id": engagement_id, "needed_by_day": self.clock.day + HIRE_LEAD_DAYS,
            "summary": f"{count} x {LEVEL_TITLES[level]} to restore bench capacity",
        }, recipient="people")]

    def _demand_by_level(self) -> dict[str, float]:
        demand = self._alloc_totals()
        for lead in self.state["pipeline"]:
            for lv, fte in TEAMS[lead["tier"]]["fte"].items():
                demand[lv] += fte * lead["prob"]
        return demand

    def tick(self) -> list[Message]:
        out: list[Message] = []
        day = self.clock.day
        # release lapsed holds and close remediated quality issues
        for eng in self.state["engagements"].values():
            for key in [k for k, due in eng["holds"].items() if due is not None and day >= due]:
                del eng["holds"][key]
        for qi in self.state["quality_issues"].values():
            if qi["status"] == "open" and day >= qi["resolve_day"]:
                qi["status"] = "resolved"
                self.log_event("delivery.activity.quality_issue_resolved", f"{qi['id']} remediated",
                               quality_issue_id=qi["id"])
        out += self._tick_milestones()
        if day - self.state["last_forecast_day"] >= FORECAST_EVERY_DAYS and day > 0:
            out += self._tick_capacity_forecast()
        return out

    def _tick_milestones(self) -> list[Message]:
        out: list[Message] = []
        day = self.clock.day
        for eng in self.state["engagements"].values():
            if eng["status"] != "active" or eng["start_day"] is None or day < eng["start_day"]:
                continue
            pending = [m for m in eng["milestones"] if not m["done"]]
            if not pending:
                continue
            m = pending[0]
            if day < m["due"]:
                continue
            if eng["holds"]:
                eng["slipped_days"] += 1
                if eng["slipped_days"] in (1, 7, 14):
                    self.log_event("delivery.activity.milestone_held", f"{eng['id']} {m['name']} held by "
                                   + ", ".join(sorted(eng["holds"])), engagement_id=eng["id"])
                continue
            out += self._complete_milestone(eng, m)
        return out

    def _complete_milestone(self, eng: dict, m: dict) -> list[Message]:
        day = self.clock.day
        m["done"] = True
        metrics = self.state["metrics"]
        metrics["milestones"] += 1
        on_time = day <= m["due"] + 2
        metrics["on_time"] += 1 if on_time else 0
        first_pass = eng["qi_since_milestone"] == 0
        metrics["qa_checked"] += 1
        metrics["qa_first_pass"] += 1 if first_pass else 0
        eng["qi_since_milestone"] = 0
        amount = m.get("amount_gbp") or int(eng["fee_gbp"] * m["pct"] / 100)
        out = [self.emit("delivery.milestone_reached", {
            "engagement_id": eng["id"], "client_id": eng["client_id"], "contract_id": eng["contract_id"],
            "service_line": eng["service_line"], "tier": eng["tier"], "milestone": m["name"],
            "milestone_no": m["no"], "billing_pct": m["pct"], "amount_gbp": amount,
            "invoice_trigger": m["billable"], "due_day": m["due"], "accepted_day": day,
            "on_time": on_time, "qa_signed_off_by": "Manager or above", "qa_first_pass": first_pass,
            "summary": f"{m['name']} reached for {eng['id']}",
        })]
        last = not [x for x in eng["milestones"] if not x["done"]]
        if last:
            out += self._complete_engagement(eng)
        return out

    def _complete_engagement(self, eng: dict) -> list[Message]:
        metrics = self.state["metrics"]
        plan = eng["plan"]
        duration = max(TIERS[eng["tier"]]["weeks"] * 7, 1)
        cost = plan["cost_gbp"] * (1 + eng["slipped_days"] / duration)
        for co_id in eng["change_orders"]:
            co = self.state["change_orders"][co_id]
            if co["status"] == "signed":
                cost += co["human_days"] * self._day_cost("senior_consultant") + \
                    co["agent_days"] * AGENT_COST_PER_DAY_GBP
        margin = _round((eng["fee_gbp"] - cost) / eng["fee_gbp"] * 100)
        metrics["margins"].append(margin)
        metrics["completed"] += 1
        eng["status"] = "completed"
        eng["alloc"] = {}
        eng["agents"] = 0
        csat = round(sum(metrics["csat"]) / len(metrics["csat"]), 2) if metrics["csat"] else None
        status = "term_ended" if eng["service_line"] == "keep" else "accepted"
        self.create_task(f"Lessons-learned review and case study candidacy for {eng['id']}", 10, "medium")
        return [self.emit("delivery.engagement_completed", {
            "engagement_id": eng["id"], "client_id": eng["client_id"], "client_name": eng["client_name"],
            "contract_id": eng["contract_id"], "service_line": eng["service_line"], "tier": eng["tier"],
            "amount_gbp": eng["fee_gbp"], "status": status, "end_day": self.clock.day,
            "slipped_days": eng["slipped_days"], "quality_issues": len(eng["quality_issues"]),
            "change_orders": len(eng["change_orders"]), "gross_margin_pct": margin, "client_csat": csat,
            "next_step": "keep_retainer_conversation" if eng["service_line"] != "keep" else "renewal",
            "summary": f"{eng['id']} {status}",
        }, delay_days=3)]

    def _tick_capacity_forecast(self) -> list[Message]:
        self.state["last_forecast_day"] = self.clock.day
        roster, free = self.state["roster"], self._free_capacity()
        demand, alloc = self._demand_by_level(), self._alloc_totals()
        gaps: dict[str, float] = {}
        for lv in LEVELS:
            cap = roster.get(lv, 0) * UTILISATION_TARGET[lv]
            if demand[lv] - cap > 0.25:
                gaps[lv] = _round(demand[lv] - cap, 2)
        humans = sum(roster.values())
        util = self._utilisation_pct()
        agents = max(self.state["agents"], self._agents_in_use())
        leverage = _round(agents / humans, 2) if humans else 0.0
        out = [self.emit("delivery.capacity_forecast_updated", {
            "horizon_days": 90, "headcount_humans": humans, "headcount_agents": agents,
            "utilisation_pct": util, "target_utilisation_pct": 70.0,
            "committed_fte_by_level": {lv: _round(v, 2) for lv, v in alloc.items() if v},
            "free_fte_by_level": {lv: _round(v, 2) for lv, v in free.items()},
            "gap_fte_by_level": gaps, "weighted_pipeline_leads": len(self.state["pipeline"]),
            "ai_agent_leverage_ratio": leverage, "hire_recommended": bool(gaps),
            "active_engagements": sum(1 for e in self.state["engagements"].values()
                                      if e["status"] == "active"),
            "summary": f"Utilisation {util}%; gaps: {gaps or 'none'}",
        })]
        for lv, gap in gaps.items():
            out += self._maybe_request_hire(lv, gap, "capacity forecast gap over 90 days")
        return out

    # ------------------------------------------------------------------ KPIs
    def kpi_snapshot(self) -> list[Kpi]:
        """KPIS with actuals filled from observed state (None where no data yet)."""
        m = self.state["metrics"]
        humans = sum(self.state["roster"].values())

        def avg(xs: list) -> float | None:
            return _round(sum(xs) / len(xs), 2) if xs else None

        engs = max(len(self.state["engagements"]), 1)
        actuals = {
            "billable_utilisation_pct": self._utilisation_pct() if humans else None,
            "engagement_gross_margin_pct": avg(m["margins"]),
            "on_time_milestone_pct": (_round(m["on_time"] / m["milestones"] * 100)
                                      if m["milestones"] else None),
            "client_csat": avg(m["csat"]),
            "qa_first_pass_rate_pct": (_round(m["qa_first_pass"] / m["qa_checked"] * 100)
                                       if m["qa_checked"] else None),
            "scope_change_capture_pct": (_round(m["scope_converted"] / m["scope_requests"] * 100)
                                         if m["scope_requests"] else None),
            "scoping_turnaround_days": avg(m["scoping_days"]),
            "time_to_staff_days": avg(m["staffing_days"]),
            "ai_agent_leverage_ratio": _round(max(self.state["agents"], self._agents_in_use()) / humans, 2)
            if humans else None,
            "quality_issues_per_engagement": (_round(m["quality_issues"] / engs, 2)
                                              if self.state["engagements"] else None),
        }
        return [dataclasses.replace(k, actual=actuals.get(k.name)) for k in KPIS]


def build_agent(llm, bus, clock, log) -> DeliveryAgent:
    """Construct the delivery agent. Does not register with the bus or publish."""
    # COMPANY.md §9.2: Managing Partner, Delivery; §6.2 head band
    role = Role("Managing Partner, Delivery", "delivery", "head", (1, 1, 1), (140_000, 200_000),
                "Chief Executive Officer")
    return DeliveryAgent("delivery", "delivery", role, llm, bus, clock, log)
