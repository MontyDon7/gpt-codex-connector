"""Sales department agent: lead qualification, proposals, deal desk, renewals proposals and pipeline.

Facts are taken from COMPANY.md (prices section 3, funnel section 5.3, budget section 5.4, terms section 7,
delegations of authority section 9.3). All behaviour is deterministic and works with ``core.MockLLM``.
"""

from __future__ import annotations

import random
from typing import Optional

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# ---------------------------------------------------------------------------------------------------------
# Company facts (module constants)
# ---------------------------------------------------------------------------------------------------------
PRICE_LIST: dict[str, tuple[str, int]] = {  # COMPANY.md §3.1 to §3.3: tier -> (service_line, list price GBP)
    "compass_spark": ("compass", 45_000),
    "compass_sprint": ("compass", 120_000),
    "compass_programme": ("compass", 350_000),
    "forge_pilot": ("forge", 90_000),
    "forge_build": ("forge", 260_000),
    "forge_scale": ("forge", 650_000),
    "keep_essential": ("keep", 96_000),    # annual value (8,000 per month)
    "keep_plus": ("keep", 216_000),        # annual value (18,000 per month)
    "keep_enterprise": ("keep", 480_000),  # annual value (40,000 per month)
}
RATE_CARD: dict[str, int] = {  # COMPANY.md §3.5 (change orders and extra days only)
    "partner": 2_400, "principal": 1_800, "manager": 1_400, "senior_consultant": 1_050,
    "consultant": 800, "analyst": 550, "ai_agent_day": 350,
}
NEXT_OFFER: dict[str, str] = {  # land-and-expand ladder, COMPANY.md §2 and §10
    "compass_spark": "forge_pilot", "compass_sprint": "forge_pilot", "compass_programme": "keep_plus",
    "forge_pilot": "forge_build", "forge_build": "keep_plus", "forge_scale": "keep_enterprise",
}
QUALIFICATION_THRESHOLD = 60                                           # SOP-SALES-01 step 7
ICP_MIN_EMPLOYEES, ICP_MAX_EMPLOYEES = 200, 2_000                      # COMPANY.md §2
ICP_INDUSTRIES = ("financial_services", "healthcare_services", "logistics", "manufacturing", "retail",
                  "professional_services")                             # COMPANY.md §2
SENIOR_ROLE_MARKERS = ("chief", "ceo", "cfo", "coo", "cto", "cio", "cdo", "vp ", "vice president",
                       "managing director", "director", "partner", "head of", "president")


def _norm_sector(value) -> str:
    """Normalise a sector label ('Financial services', 'healthcare') to the ICP vocabulary."""
    key = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return "healthcare_services" if key == "healthcare" else key


DISCOUNT_SALES_HEAD_MAX_PCT = 10.0                                     # COMPANY.md §9.3
DEAL_CEO_THRESHOLD_GBP = 500_000                                       # COMPANY.md §9.3
DEAL_BOARD_THRESHOLD_GBP = 1_500_000                                   # COMPANY.md §9.3
CRISIS_DISCOUNT_CEILING_PCT = 5.0                                      # sales policy (economics.md section 3)
KEEP_UPLIFT_CAP_PCT = 7.0                                              # COMPANY.md §7 (CPI + 2%, cap 7%)
KEEP_UPLIFT_MARGIN_PCT = 2.0                                           # COMPANY.md §7
DEFAULT_CPI_PCT = 3.0                                                  # planning assumption
RENEWAL_LEAD_DAYS = 60                                                 # renewal proposal >= 60 days before term end
NEW_BUSINESS_COMMISSION_RATE = 0.017                                   # economics.md section 3
SCOPING_SLA_DAYS = 7
SECURITY_REVIEW_SLA_DAYS = 10
PROPOSAL_VALIDITY_DAYS = 30
DECISION_WINDOW_DAYS: dict[str, int] = {                               # economics.md section 3.7 (planning mean 65)
    "compass_spark": 40, "keep_essential": 45, "forge_pilot": 50, "compass_sprint": 60, "keep_plus": 60,
    "forge_build": 80, "compass_programme": 85, "keep_enterprise": 85, "forge_scale": 105,
}
DEFAULT_DECISION_LAG_DAYS = 65                                         # planning mean when the tier is unknown
CHANGE_ORDER_DECISION_DAYS = 14                                        # change orders are signed before work starts
NEGOTIATION_AT_FRACTION = 0.7                                          # redlines / verbal yes at 70% of the window
NEW_LOGO_SOURCES = ("inbound", "outbound", "referral", "rfp")          # kpis.md section 2
COMMISSION_FIRST_RELEASE_SHARE = 0.5                                   # economics.md section 3.4
COMMISSION_CLAWBACK_DAYS = 90                                          # economics.md section 3.4
CLAWBACK_OVERDUE_DAYS = 60                                             # invoice overdue and written off
CRISIS_REVIEW_DAYS = 30                                                # CEO confirmation task (SOP-SALES-14)
CRISIS_LIFT_STATUSES = ("lifted", "resolved", "closed", "stood_down", "cleared", "ended")
SDR_LEADS_PER_MONTH = 60                                               # leads one SDR plus agent can work
SDR_HEADCOUNT_BY_YEAR = {1: 1, 2: 3, 3: 5}                             # blueprint.md section 3
US_LAUNCH_YEAR = 2027                                                  # COMPANY.md §1 (Q1 FY2027)
WIN_RATE = 0.30                                                        # COMPANY.md §5.3
LOSS_REASONS = ("price", "competitor", "no_decision", "timing")

STAGE_WEIGHTS: dict[str, float] = {  # probability of winning from each stage (economics.md section 3)
    "qualified": 0.15, "scoped": 0.21, "proposal_build": 0.25, "proposal_sent": 0.30,
    "negotiation": 0.60, "contract": 0.90, "won": 1.0, "lost": 0.0,
}
OPEN_STAGES = ("qualified", "scoped", "proposal_build", "proposal_sent", "negotiation", "contract")

DEPT_BUDGET_GBP: dict[int, tuple[int, int]] = {  # COMPANY.md §5.4: (people, non-people) per year index
    1: (600_000, 250_000), 2: (1_300_000, 800_000), 3: (2_300_000, 2_300_000),
}
# Planned hires (title, level, count, start quarter label) by year index; mirrors blueprint.md section 5.
HIRING_PLAN: dict[int, tuple[tuple[str, str, int, str], ...]] = {
    2: (
        ("Sales Director", "principal", 1, "Q2 FY2027"),
        ("Sales Development Representative", "analyst", 1, "Q2 FY2027"),
        ("Account Executive", "senior_consultant", 1, "Q2 FY2027"),
        ("Sales Operations Manager", "manager", 1, "Q2 FY2027"),
        ("Senior Account Executive", "manager", 1, "Q3 FY2027"),
        ("Sales Development Representative", "analyst", 1, "Q3 FY2027"),
        ("Solutions Consultant", "senior_consultant", 1, "Q3 FY2027"),
        ("Renewals and Expansion Manager", "manager", 1, "Q3 FY2027"),
        ("Account Executive", "senior_consultant", 1, "Q4 FY2027"),
    ),
    3: (
        ("Senior Account Executive", "manager", 1, "Q2 FY2028"),
        ("Sales Director", "principal", 1, "Q2 FY2028"),
        ("Sales Development Representative", "analyst", 1, "Q2 FY2028"),
        ("Account Executive", "senior_consultant", 1, "Q3 FY2028"),
        ("Deal Desk Analyst", "consultant", 1, "Q3 FY2028"),
        ("Solutions Consultant", "senior_consultant", 1, "Q3 FY2028"),
        ("Senior Account Executive", "manager", 1, "Q4 FY2028"),
        ("Account Executive", "senior_consultant", 1, "Q4 FY2028"),
        ("Sales Development Representative", "analyst", 1, "Q4 FY2028"),
        ("Renewals and Expansion Manager", "manager", 1, "Q4 FY2028"),
        ("Sales Operations Analyst", "consultant", 1, "Q4 FY2028"),
        ("Proposal Writer", "consultant", 1, "Q4 FY2028"),
    ),
}

# FY2026 targets; identical to kpis.md section 1 (COMPANY.md §5.1 and §5.3).
KPIS: list[Kpi] = [
    Kpi("new_logos_won", "count", 24, None, True),
    Kpi("win_rate", "percent", 30.0, None, True),
    Kpi("lead_to_qualified_rate", "percent", 25.0, None, True),
    Kpi("qualified_to_proposal_rate", "percent", 50.0, None, True),
    Kpi("sales_cycle_days", "days", 75, None, False),
    Kpi("blended_cac_gbp", "gbp", 70_000, None, False),
    Kpi("new_logo_acv_bookings_gbp", "gbp", 6_000_000, None, True),
    Kpi("pipeline_coverage_ratio", "ratio", 3.3, None, True),
    Kpi("average_discount_percent", "percent", 6.0, None, False),
    Kpi("proposal_turnaround_days", "days", 10, None, False),
    Kpi("forecast_accuracy_percent", "percent", 80.0, None, True),
    Kpi("renewal_proposal_on_time_percent", "percent", 90.0, None, True),
    Kpi("quota_attainment_percent", "percent", 90.0, None, True),
    Kpi("cost_per_proposal_gbp", "gbp", 10_625, None, False),
    Kpi("discount_policy_compliance_percent", "percent", 100.0, None, True),
]


def _num(value, default: float = 0.0) -> float:
    """Best-effort numeric coercion that never raises."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class SalesAgent(DepartmentAgent):
    """Chief Revenue Officer agent: owns the deal chain from qualified lead to won/lost and renewals."""

    SUBSCRIBES = subscribes_for("sales")
    PUBLISHES = publishes_for("sales")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.state.update({
            "deals": {}, "seq": {"deal": 0, "proposal": 0, "lead": 0, "client": 0},
            "clients": {}, "holds": [], "at_risk": {}, "health": {}, "renewals": {},
            "price_overrides": {}, "capabilities": [], "certifications": {}, "library": [],
            "pending_price_changes": [], "okrs": {}, "forecast": {}, "budget_cycles": [],
            "crisis": False, "crisis_started_day": None, "crisis_task_id": None, "crisis_review_raised": False,
            "start_lag_days": 0, "commission_accrued_gbp": 0.0, "commission_released_gbp": 0.0,
            "commission_clawed_back_gbp": 0.0, "commissions": {}, "leads_seen": [], "learning_cases": [],
            "signed_clients": [], "new_logo_clients": [],
            "stats": {"leads": 0, "leads_mql": 0, "leads_nurture": 0, "lead_qualified": 0,
                      "qualified_nurture": 0, "qualified": 0, "expansion_qualified": 0,
                      "proposals_sent": 0, "nl_proposals_sent": 0, "won": 0, "lost": 0,
                      "expansion_won": 0, "expansion_lost": 0, "qualified_not_proposed": 0,
                      "bookings_gbp": 0.0, "expansion_and_renewal_bookings_gbp": 0.0,
                      "discount_weighted": 0.0, "list_sent_gbp": 0.0, "compliant_proposals": 0,
                      "turnaround_days_sum": 0, "renewal_proposals": 0, "renewals_on_time": 0,
                      "renewals_confirmed": 0, "churned": 0, "approvals_requested": 0, "cycle_days_sum": 0},
        })
        self._handlers = {
            "marketing.lead_generated": self._on_lead_generated,
            "marketing.campaign_launched": self._on_campaign_launched,
            "marketing.content_published": self._on_content_published,
            "marketing.event_scheduled": self._on_event_scheduled,
            "delivery.scoping_completed": self._on_scoping_completed,
            "finance.pricing_check_completed": self._on_pricing_check_completed,
            "it_security.security_questionnaire_completed": self._on_security_questionnaire,
            "legal.security_terms_reviewed": self._on_security_terms,
            "legal.contract_risk_flagged": self._on_contract_risk,
            "legal.contract_drafted": self._on_contract_drafted,
            "legal.contract_signed": self._on_contract_signed,
            "executive.deal_decision_made": self._on_deal_decision,
            "external.rfp_received": self._on_rfp_received,
            "customer_success.renewal_due": self._on_renewal_due,
            "customer_success.renewal_confirmed": self._on_renewal_confirmed,
            "customer_success.churn_risk_flagged": self._on_churn_risk,
            "customer_success.client_churned": self._on_client_churned,
            "customer_success.health_score_updated": self._on_health_score,
            "customer_success.expansion_opportunity_identified": self._on_expansion,
            "delivery.engagement_completed": self._on_engagement_completed,
            "delivery.scope_change_requested": self._on_scope_change,
            "delivery.capacity_forecast_updated": self._on_capacity_forecast,
            "data.forecast_updated": self._on_forecast,
            "executive.pricing_change_approved": self._on_pricing_change_approved,
            "product.pricing_change_proposed": self._on_pricing_change_proposed,
            "product.agent_capability_added": self._on_capability_added,
            "product.roadmap_published": self._on_roadmap,
            "it_security.certification_status_updated": self._on_certification,
            "finance.budget_cycle_opened": self._on_budget_cycle_opened,
            "executive.budget_approved": self._on_budget_approved,
            "executive.okrs_set": self._on_okrs_set,
            "executive.strategy_updated": self._on_strategy_updated,
            "executive.crisis_declared": self._on_crisis,
            "finance.invoice_overdue": self._on_invoice_overdue,
            "finance.payment_received": self._on_payment_received,
        }

    # ------------------------------------------------------------------------------------------------
    # framework entry points
    # ------------------------------------------------------------------------------------------------
    def handle(self, message: Message) -> list[Message]:
        """Route on topic; unknown topics are logged and ignored. Only public sales.* topics are returned."""
        handler = self._handlers.get(message.topic)
        if handler is None:
            self.log_event("sales.activity.unhandled_topic", f"ignored {message.topic}", source_topic=message.topic)
            return []
        out = handler(message) or []
        return [m for m in out if m.topic in self.PUBLISHES]

    def tick(self) -> list[Message]:
        """Weekly pipeline review (Mondays), monthly KPI snapshot (1st) and gate chasing (daily)."""
        if self.clock.date.weekday() == 0:
            self._weekly_pipeline_review()
        if self.clock.is_month_start:
            self._monthly_snapshot()
        self._chase_stalled_deals()
        self._crisis_check()
        out: list[Message] = []
        for deal in list(self.state["deals"].values()):
            if deal["stage"] in ("proposal_sent", "negotiation") and deal.get("decision_day") is not None:
                out.extend(self._client_decision_due(deal))
        return out

    # ------------------------------------------------------------------------------------------------
    # small helpers
    # ------------------------------------------------------------------------------------------------
    def _note(self, event: str, summary: str, **data) -> None:
        self.log_event(f"sales.activity.{event}", summary, **data)

    def _seq(self, key: str) -> int:
        self.state["seq"][key] += 1
        return self.state["seq"][key]

    def _bump_seq(self, key: str, identifier: str) -> None:
        """Keep a counter ahead of externally supplied ids such as 'DL-0007'."""
        digits = "".join(ch for ch in str(identifier).rsplit("-", 1)[-1] if ch.isdigit())
        if digits:
            self.state["seq"][key] = max(self.state["seq"][key], int(digits))

    def _client_id(self, body: dict) -> str:
        name = str(body.get("client_name") or body.get("company") or "")
        cid = body.get("client_id") or self.state["clients"].get(name)
        if not cid:
            cid = f"CL-{self._seq('client'):04d}"
        else:
            self._bump_seq("client", cid)
        if name:
            self.state["clients"][name] = cid
        return str(cid)

    def _price(self, tier: str) -> int:
        override = self.state["price_overrides"].get(tier)
        return int(override if override else PRICE_LIST[tier][1])

    def _sdr_count(self) -> int:
        return SDR_HEADCOUNT_BY_YEAR.get(max(1, min(3, self.clock.year_index)), 1)

    def _find_deal(self, body: dict) -> Optional[dict]:
        deals = self.state["deals"]
        did = body.get("deal_id")
        if did in deals:
            return deals[did]
        for key in ("proposal_id", "lead_id", "engagement_id"):
            if body.get(key):
                for deal in deals.values():
                    if deal.get(key) == body[key]:
                        return deal
        cid = body.get("client_id")
        if cid:
            open_deals = [d for d in deals.values() if d["client_id"] == cid and d["stage"] in OPEN_STAGES]
            if open_deals:
                return open_deals[-1]
        return None

    def _open_deals_for(self, client_id: str) -> list[dict]:
        return [d for d in self.state["deals"].values()
                if d["client_id"] == client_id and d["stage"] in OPEN_STAGES]

    def _new_deal(self, body: dict, tier: str, source: str, **extra) -> dict:
        deal_id = body.get("deal_id")
        if deal_id and deal_id not in self.state["deals"]:
            self._bump_seq("deal", deal_id)
        else:
            deal_id = f"DL-{self._seq('deal'):04d}"
        line = PRICE_LIST[tier][0]
        deal = {
            "deal_id": deal_id, "client_id": self._client_id(body),
            "client_name": str(body.get("client_name") or body.get("company") or "Unnamed client"),
            "lead_id": body.get("lead_id"), "service_line": line, "tier": tier,
            "list_price_gbp": int(_num(body.get("list_price_gbp"), 0) or self._price(tier)),
            "discount_pct": 0.0, "requested_discount_pct": max(0.0, _num(body.get("requested_discount_pct"))),
            "net_gbp": 0, "stage": "qualified", "source": source, "created_day": self.clock.day,
            "requested_day": self.clock.day, "scoping_day": None, "proposal_day": None,
            "gates": {"scoping": False, "pricing": False, "questionnaire": False, "terms": False},
            "approval": None, "approvals_needed": [], "proposal_id": None, "contract_id": None,
            "engagement_id": body.get("engagement_id"), "risk_flags": [], "chased": False,
            "outcome_hint": body.get("outcome"), "loss_reason_hint": body.get("loss_reason"),
            "decision_lag_days": int(_num(body.get("decision_lag_days"), CHANGE_ORDER_DECISION_DAYS
                                          if extra.get("change_order") else
                                          DECISION_WINDOW_DAYS.get(tier, DEFAULT_DECISION_LAG_DAYS))),
            "non_standard_terms": bool(body.get("non_standard_payment_terms")),
            "employees": int(_num(body.get("employees"))), "industry": body.get("industry"),
            "security_waived": False, "change_order": False, "pricing_cap_pct": None,
            "held": False, "cfo_released": False, "new_logo": False, "decision_day": None, "negotiation_day": None,
        }
        deal.update(extra)
        self.state["deals"][deal_id] = deal
        return deal

    def _deal_body(self, deal: dict, **extra) -> dict:
        body = {
            "deal_id": deal["deal_id"], "client_id": deal["client_id"], "client_name": deal["client_name"],
            "service_line": deal["service_line"], "tier": deal["tier"],
            "amount_gbp": deal["net_gbp"] or deal["list_price_gbp"],
        }
        if deal.get("lead_id"):
            body["lead_id"] = deal["lead_id"]
        if deal.get("proposal_id"):
            body["proposal_id"] = deal["proposal_id"]
        if deal.get("contract_id"):
            body["contract_id"] = deal["contract_id"]
        if deal.get("engagement_id"):
            body["engagement_id"] = deal["engagement_id"]
        body.update(extra)
        return body

    def _qualify_and_request(self, deal: dict, summary: str, reply_to: Optional[str] = None,
                             announce_lead: bool = True) -> list[Message]:
        """Emit lead_qualified (new logos and expansion) then proposal_requested to delivery and finance."""
        out: list[Message] = []
        deal["stage"] = "qualified"
        deal["requested_day"] = self.clock.day
        self.state["stats"]["qualified" if deal["source"] in NEW_LOGO_SOURCES else "expansion_qualified"] += 1
        if announce_lead:
            out.append(self.emit("sales.lead_qualified", self._deal_body(
                deal, employees=deal["employees"], industry=deal["industry"], source=deal["source"],
                summary=summary, due_day=self.clock.day + SCOPING_SLA_DAYS), reply_to=reply_to))
        out.append(self.emit("sales.proposal_requested", self._deal_body(
            deal, source=deal["source"], summary=f"Scope and price {deal['tier']} for {deal['client_name']}",
            requested_discount_pct=deal["requested_discount_pct"], change_order=deal["change_order"],
            scoping_due_day=self.clock.day + SCOPING_SLA_DAYS,
            due_day=self.clock.day + SCOPING_SLA_DAYS + 3), reply_to=reply_to))
        return out

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-01 lead qualification
    # ------------------------------------------------------------------------------------------------
    def _score_lead(self, body: dict) -> tuple[int, list[str]]:
        """Deterministic qualification score (0 to 100) and the reasons behind it.

        Rubric is SOP-SALES-01 step 4: size 30, ICP sector 20, board-level sponsor 25, defined
        pain 15, budget confirmed 10. Reads Marketing's lead keys (`sector`, `contact_role`,
        `score_reasons`) as well as the CRM-native ones (`industry`, `board_sponsor`, `pain`).
        """
        score, reasons = 0, []
        employees = int(_num(body.get("employees")))
        if ICP_MIN_EMPLOYEES <= employees <= ICP_MAX_EMPLOYEES:
            score += 30
            reasons.append("size_in_icp")
        if _norm_sector(body.get("sector") or body.get("industry")) in ICP_INDUSTRIES:
            score += 20
            reasons.append("icp_industry")
        mkt_reasons = body.get("score_reasons") or ()
        if isinstance(mkt_reasons, str):
            mkt_reasons = (mkt_reasons,)
        role = str(body.get("contact_role") or body.get("contact_title") or "").lower()
        if (body.get("board_sponsor", body.get("has_sponsor")) or "senior_buyer" in mkt_reasons
                or any(t in role for t in SENIOR_ROLE_MARKERS)):
            score += 25
            reasons.append("board_sponsor")
        if body.get("pain") or body.get("need") or "named_pain_point" in mkt_reasons:
            score += 15
            reasons.append("defined_pain")
        if body.get("budget_confirmed"):
            score += 10
            reasons.append("budget_confirmed")
        return score, reasons

    @staticmethod
    def _lead_source(value) -> str:
        """Map Marketing's channel (referral, event, webinar, ...) to the deal source of kpis.md."""
        key = str(value or "").lower()
        if key in ("referral", "partner"):
            return "referral"
        return "outbound" if key.startswith("outbound") else "inbound"

    def _on_lead_generated(self, msg: Message) -> list[Message]:
        b = msg.body
        lead_id = b.get("lead_id") or f"LD-{self._seq('lead'):05d}"
        company = str(b.get("company") or b.get("client_name") or "Unknown company")
        if b.get("lead_id"):
            if lead_id in self.state["leads_seen"]:
                self._note("lead_duplicate", f"{lead_id} {company} already worked", lead_id=lead_id)
                return []
            self.state["leads_seen"].append(lead_id)
        stage = "nurture" if str(b.get("stage") or "mql").lower() == "nurture" else "mql"
        stats = self.state["stats"]
        stats["leads"] += 1
        stats[f"leads_{stage}"] += 1
        score, reasons = self._score_lead(b)
        employees = int(_num(b.get("employees")))
        in_size = ICP_MIN_EMPLOYEES <= employees <= ICP_MAX_EMPLOYEES
        if str(b.get("country") or b.get("region") or "UK").upper() in ("US", "USA") \
                and self.clock.date.year < US_LAUNCH_YEAR:
            self._note("lead_parked", f"{lead_id} {company}: US lead before US launch", lead_id=lead_id)
            return []
        if any(d["client_name"] == company and d["stage"] in OPEN_STAGES for d in self.state["deals"].values()):
            self._note("lead_duplicate", f"{lead_id} {company} merged into the open deal", lead_id=lead_id)
            return []
        # Same 60-point desk check for both marketing stages (SOP-SALES-01 step 7).
        if not in_size or score < QUALIFICATION_THRESHOLD:
            self._note("lead_disqualified", f"{lead_id} {company} ({stage}) score {score}", lead_id=lead_id,
                       score=score, reasons=reasons, stage=stage)
            return []
        tier = str(b.get("tier") or "")
        if tier not in PRICE_LIST:
            interest = str(b.get("service_interest") or b.get("service_line") or "compass")
            tier = {"compass": "compass_spark", "forge": "forge_pilot", "keep": "keep_essential"}.get(
                interest, "compass_spark")
        stats["lead_qualified"] += 1
        stats[f"qualified_{stage}"] = stats.get(f"qualified_{stage}", 0) + 1
        deal = self._new_deal({**b, "lead_id": lead_id, "client_name": company}, tier,
                              self._lead_source(b.get("source")), score=score, marketing_stage=stage)
        self._note("lead_qualified", f"{lead_id} {company} ({stage}) score {score} -> {deal['deal_id']}",
                   lead_id=lead_id, deal_id=deal["deal_id"], score=score, reasons=reasons, stage=stage)
        if stage == "nurture":
            self.state["learning_cases"].append({
                "lead_id": lead_id, "deal_id": deal["deal_id"], "company": company, "sales_score": score,
                "marketing_score": b.get("score"), "day": self.clock.day})
            self._note("learning_case", f"{lead_id} nurture lead qualified on the sales rubric (score {score}); "
                       "reported to Marketing's weekly audit", lead_id=lead_id, sales_score=score,
                       marketing_score=b.get("score"))
        if str(b.get("severity", "")).lower() == "high" or deal["source"] == "referral":
            self.create_task(f"Same-day contact for {company} ({lead_id})", due_in_days=0, priority="high")
        return self._qualify_and_request(
            deal, f"{company} qualified (score {score}); first offer {tier}", reply_to=msg.id)

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-03 proposal build, pricing and deal desk
    # ------------------------------------------------------------------------------------------------
    def _on_scoping_completed(self, msg: Message) -> list[Message]:
        deal = self._find_deal(msg.body)
        if deal is None:
            self._note("unmatched", "scoping_completed without a known deal", source_topic=msg.topic)
            return []
        deal["gates"]["scoping"] = True
        deal["scoping_day"] = self.clock.day
        if deal["stage"] == "qualified":
            deal["stage"] = "scoped"
        if msg.body.get("estimated_value_gbp") and not deal["change_order"]:
            deal["scoped_value_gbp"] = int(_num(msg.body["estimated_value_gbp"]))
        return self._progress(deal, msg.id)

    def _on_pricing_check_completed(self, msg: Message) -> list[Message]:
        deal = self._find_deal(msg.body)
        if deal is None:
            self._note("unmatched", "pricing_check_completed without a known deal", source_topic=msg.topic)
            return []
        deal["gates"]["pricing"] = True
        if msg.body.get("approved") is False:
            deal["pricing_cap_pct"] = 0.0
            self.create_task(f"Re-price {deal['deal_id']}: finance rejected the proposed discount",
                             due_in_days=3, priority="high")
        elif msg.body.get("max_discount_pct") is not None:
            deal["pricing_cap_pct"] = max(0.0, _num(msg.body["max_discount_pct"]))
        return self._progress(deal, msg.id)

    def _price_deal(self, deal: dict) -> None:
        """Apply discount ceilings and work out the approvals that section 9.3 requires."""
        disc = deal["requested_discount_pct"]
        ceiling = CRISIS_DISCOUNT_CEILING_PCT if self.state["crisis"] else 100.0
        if deal["pricing_cap_pct"] is not None:
            ceiling = min(ceiling, deal["pricing_cap_pct"])
        disc = min(disc, ceiling)
        deal["discount_pct"] = round(disc, 2)
        deal["net_gbp"] = int(round(deal["list_price_gbp"] * (1 - disc / 100.0)))
        needs: list[str] = []
        if deal["discount_pct"] > DISCOUNT_SALES_HEAD_MAX_PCT:
            needs.append("discount_above_10pct")
        if deal["non_standard_terms"]:
            needs.append("non_standard_payment_terms")
        if deal["net_gbp"] >= DEAL_CEO_THRESHOLD_GBP:
            needs.append("deal_at_least_500k")
        if deal["net_gbp"] > DEAL_BOARD_THRESHOLD_GBP:
            needs.append("deal_above_1_5m")
        if self._legal_flags(deal):
            needs.append("non_standard_legal_terms")
        deal["approvals_needed"] = needs

    @staticmethod
    def _legal_flags(deal: dict) -> list[str]:
        """Risk flags that need General Counsel and CEO; a credit hold is a Finance matter, not a legal one."""
        return [f for f in deal["risk_flags"] if f != "client_invoice_overdue"]

    def _approvers(self, needs: list[str]) -> list[str]:
        approvers: list[str] = []
        if {"discount_above_10pct", "non_standard_payment_terms"} & set(needs):
            approvers += ["finance_head", "ceo"]
        if "deal_at_least_500k" in needs:
            approvers.append("ceo")
        if "deal_above_1_5m" in needs:
            approvers.append("board")
        if "non_standard_legal_terms" in needs:
            approvers += ["general_counsel", "ceo"]
        return sorted(set(approvers))

    def _progress(self, deal: dict, reply_to: Optional[str]) -> list[Message]:
        """Advance a deal as gates clear: build the proposal, request reviews and approvals, send it."""
        out: list[Message] = []
        g = deal["gates"]
        if deal["stage"] in ("won", "lost", "contract") or deal["proposal_day"] is not None:
            return out
        if deal["proposal_id"] is None:
            if not (g["scoping"] and g["pricing"]):
                return out
            deal["proposal_id"] = f"PR-{self._seq('proposal'):04d}"
            deal["stage"] = "proposal_build"
            self._price_deal(deal)
            self._note("proposal_built", f"{deal['proposal_id']} {deal['net_gbp']} GBP", deal_id=deal["deal_id"],
                       discount_pct=deal["discount_pct"], approvals=list(deal["approvals_needed"]))
            if deal["security_waived"]:
                g["questionnaire"] = g["terms"] = True
            else:
                out.append(self.emit("sales.security_review_requested", self._deal_body(
                    deal, summary=f"Security questionnaire and terms review for {deal['client_name']}",
                    due_day=self.clock.day + SECURITY_REVIEW_SLA_DAYS), reply_to=reply_to))
            if deal["approvals_needed"]:
                deal["approval"] = "pending"
                out.append(self._request_approval(deal, reply_to))
            elif deal["discount_pct"] > 0:
                self._note("discount_approved", f"{deal['deal_id']} {deal['discount_pct']}% within sales head "
                           "authority", deal_id=deal["deal_id"])
        if deal["approvals_needed"] and deal["approval"] is None:  # risk flagged after the proposal was built
            deal["approval"] = "pending"
            out.append(self._request_approval(deal, reply_to))
        ready = (g["questionnaire"] and g["terms"] and deal["approval"] in (None, "approved")
                 and deal["proposal_id"] is not None)
        if ready and self._on_hold(deal):
            # SOP-SALES-13 step 3: prepared but not issued without the CFO's release.
            if not deal["held"]:
                deal["held"] = True
                self.create_task(f"Credit hold: obtain CFO release before issuing proposal {deal['proposal_id']} to "
                                 f"{deal['client_name']}", due_in_days=2, priority="high")
                self._note("proposal_held", f"{deal['deal_id']} prepared but held (client on credit hold)",
                           deal_id=deal["deal_id"], client_id=deal["client_id"])
        elif ready:
            out.extend(self._send_proposal(deal, reply_to))
        return out

    def _on_hold(self, deal: dict) -> bool:
        return deal["client_id"] in self.state["holds"] and not deal["cfo_released"]

    def _request_approval(self, deal: dict, reply_to: Optional[str]) -> Message:
        self.state["stats"]["approvals_requested"] += 1
        needs = list(deal["approvals_needed"])
        return self.emit("sales.deal_approval_requested", self._deal_body(
            deal, discount_pct=deal["discount_pct"], reasons=needs, approvers=self._approvers(needs),
            board_notification="deal_above_1_5m" in needs,
            summary=f"{deal['client_name']} {deal['tier']} net {deal['net_gbp']} GBP requires "
                    f"{', '.join(self._approvers(needs))}", due_day=self.clock.day + 5), reply_to=reply_to)

    def _send_proposal(self, deal: dict, reply_to: Optional[str]) -> list[Message]:
        deal["stage"] = "proposal_sent"
        deal["proposal_day"] = self.clock.day
        deal["held"] = False
        stats = self.state["stats"]
        stats["proposals_sent"] += 1
        stats["nl_proposals_sent"] += 1 if deal["source"] in NEW_LOGO_SOURCES else 0
        stats["discount_weighted"] += deal["discount_pct"] * deal["list_price_gbp"]
        stats["list_sent_gbp"] += deal["list_price_gbp"]
        stats["turnaround_days_sum"] += self.clock.day - deal["requested_day"]
        stats["compliant_proposals"] += 1 if (not deal["approvals_needed"] or deal["approval"] == "approved") else 0
        summary = (f"Proposal {deal['proposal_id']} for {deal['client_name']}: {deal['tier']} "
                   f"{deal['net_gbp']} GBP after {deal['discount_pct']}% discount")
        if self.state["start_lag_days"]:
            summary += f"; delivery start lag {self.state['start_lag_days']} days (capacity)"
        out = [self.emit("sales.proposal_sent", self._deal_body(
            deal, list_price_gbp=deal["list_price_gbp"], discount_pct=deal["discount_pct"],
            delivery_start_lag_days=self.state["start_lag_days"], summary=summary,
            due_day=self.clock.day + PROPOSAL_VALIDITY_DAYS), reply_to=reply_to)]
        lag = deal["decision_lag_days"]  # the client's answer is polled by tick(); no internal topic is used
        deal["negotiation_day"] = self.clock.day + max(1, int(lag * NEGOTIATION_AT_FRACTION))
        deal["decision_day"] = self.clock.day + lag
        return out

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-04 security review and contract terms
    # ------------------------------------------------------------------------------------------------
    def _on_security_questionnaire(self, msg: Message) -> list[Message]:
        deal = self._find_deal(msg.body)
        if deal is None:
            self._note("unmatched", "security questionnaire without a known deal", source_topic=msg.topic)
            return []
        deal["gates"]["questionnaire"] = True
        if msg.body.get("blocking_gaps"):
            deal["risk_flags"].append("security_gap")
            self.create_task(f"Close security gaps for {deal['deal_id']}", due_in_days=5, priority="high")
            deal["approvals_needed"] = sorted(set(deal["approvals_needed"]) | {"non_standard_legal_terms"})
        return self._progress(deal, msg.id)

    def _on_security_terms(self, msg: Message) -> list[Message]:
        deal = self._find_deal(msg.body)
        if deal is None:
            self._note("unmatched", "security terms review without a known deal", source_topic=msg.topic)
            return []
        deal["gates"]["terms"] = True
        return self._progress(deal, msg.id)

    def _on_contract_risk(self, msg: Message) -> list[Message]:
        deal = self._find_deal(msg.body)
        severity = str(msg.body.get("severity", "medium"))
        if deal is None:
            self._note("unmatched", "contract risk without a known deal", source_topic=msg.topic)
            return []
        self._note("contract_risk", f"{deal['deal_id']} risk {severity}", deal_id=deal["deal_id"],
                   severity=severity)
        if deal["stage"] == "proposal_sent":  # client has returned redlines: commercial terms under discussion
            deal["stage"] = "negotiation"
        if severity in ("high", "critical"):
            deal["risk_flags"].append(msg.body.get("summary", "contract_risk"))
            deal["approvals_needed"] = sorted(set(deal["approvals_needed"]) | {"non_standard_legal_terms"})
            self.create_task(f"Negotiate contract risk on {deal['deal_id']}", due_in_days=3, priority="high")
            if deal["proposal_id"] is not None and deal["proposal_day"] is None:
                deal["approval"] = None
                return self._progress(deal, msg.id)
        return []

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-05 deal approval and SOP-SALES-06 close
    # ------------------------------------------------------------------------------------------------
    def _on_deal_decision(self, msg: Message) -> list[Message]:
        deal = self._find_deal(msg.body)
        if deal is None:
            self._note("unmatched", "deal decision without a known deal", source_topic=msg.topic)
            return []
        decision = str(msg.body.get("decision", "approved"))
        self._note("deal_decision", f"{deal['deal_id']} {decision}", deal_id=deal["deal_id"])
        if decision.startswith("reject") or decision == "declined":
            return self._lose(deal, "executive_declined", msg.id)
        deal["approval"] = "approved"
        if msg.body.get("cfo_release"):
            deal["cfo_released"] = True
        return self._progress(deal, msg.id)

    def _outcome(self, deal: dict) -> tuple[bool, str]:
        """Deterministic client answer: the outcome hint if given, else a seeded draw at the 30% win rate."""
        hint = deal["outcome_hint"]
        rng = random.Random(f"sales-outcome:{deal['deal_id']}")
        won = (hint == "won") if hint in ("won", "lost") else rng.random() < WIN_RATE
        reason = deal["loss_reason_hint"] or LOSS_REASONS[rng.randrange(len(LOSS_REASONS))]
        return won, reason

    def _client_decision_due(self, deal: dict) -> list[Message]:
        """Daily poll (SOP-SALES-06): at 70% of the decision window the client returns redlines or a verbal yes
        (stage `negotiation`); on the decision day the answer is recorded (won or lost)."""
        out: list[Message] = []
        won, reason = self._outcome(deal)
        if deal["stage"] == "proposal_sent" and won and self.clock.day >= (deal.get("negotiation_day") or 0):
            deal["stage"] = "negotiation"
            self._note("negotiation", f"{deal['deal_id']} in negotiation", deal_id=deal["deal_id"])
        if self.clock.day >= deal["decision_day"]:
            out = self._win(deal, None) if won else self._lose(deal, reason, None)
        return out

    def _win(self, deal: dict, reply_to: Optional[str]) -> list[Message]:
        deal["stage"] = "contract"
        deal["won_day"] = self.clock.day
        stats = self.state["stats"]
        cid = deal["client_id"]
        # A new logo is a client with no earlier signed engagement won through a new-business source.
        deal["new_logo"] = (deal["source"] in NEW_LOGO_SOURCES and cid not in self.state["signed_clients"]
                            and cid not in self.state["new_logo_clients"])
        if deal["new_logo"]:
            self.state["new_logo_clients"].append(cid)
            stats["won"] += 1
            stats["bookings_gbp"] += deal["net_gbp"]
            stats["cycle_days_sum"] += self.clock.day - deal["requested_day"]
        else:
            stats["expansion_won"] += 1
            stats["expansion_and_renewal_bookings_gbp"] += deal["net_gbp"]
        return [self.emit("sales.deal_won", self._deal_body(
            deal, discount_pct=deal["discount_pct"], source=deal["source"],
            summary=f"{deal['client_name']} accepted {deal['tier']} at {deal['net_gbp']} GBP",
            due_day=self.clock.day + 14), reply_to=reply_to)]

    def _lose(self, deal: dict, reason: str, reply_to: Optional[str]) -> list[Message]:
        if deal["stage"] in ("won", "lost"):
            return []
        stats = self.state["stats"]
        if deal["proposal_day"] is None:
            stats["qualified_not_proposed"] += 1  # excluded from win_rate (kpis.md section 2)
        elif deal["source"] in NEW_LOGO_SOURCES:
            stats["lost"] += 1
        else:
            stats["expansion_lost"] += 1
        deal["stage"] = "lost"
        return [self.emit("sales.deal_lost", self._deal_body(
            deal, reason=reason, summary=f"{deal['client_name']} {deal['tier']} lost: {reason}"),
            reply_to=reply_to)]

    def _on_contract_drafted(self, msg: Message) -> list[Message]:
        deal = self._find_deal(msg.body)
        if deal is None:
            self._note("unmatched", "contract drafted without a known deal", source_topic=msg.topic)
            return []
        deal["contract_id"] = msg.body.get("contract_id", deal["contract_id"])
        self.create_task(f"Walk {deal['client_name']} through contract {deal['contract_id']}", due_in_days=3,
                         priority="high")
        self._note("contract_drafted", f"{deal['deal_id']} contract {deal['contract_id']}",
                   deal_id=deal["deal_id"])
        return []

    def _on_contract_signed(self, msg: Message) -> list[Message]:
        deal = self._find_deal(msg.body)
        if deal is None:
            self._note("unmatched", "contract signed without a known deal", source_topic=msg.topic)
            return []
        deal["contract_id"] = msg.body.get("contract_id", deal["contract_id"])
        deal["stage"] = "won"
        if deal["client_id"] not in self.state["signed_clients"]:
            self.state["signed_clients"].append(deal["client_id"])
        accrual = 0.0
        if deal["deal_id"] not in self.state["commissions"]:
            accrual = round(deal["net_gbp"] * NEW_BUSINESS_COMMISSION_RATE, 2)
            self.state["commission_accrued_gbp"] += accrual
            self.state["commissions"][deal["deal_id"]] = {
                "client_id": deal["client_id"], "accrued_gbp": accrual, "released_gbp": 0.0,
                "signed_day": self.clock.day, "release_day": None, "status": "accrued"}
        self._note("contract_signed", f"{deal['deal_id']} signed; commission accrued {accrual}",
                   deal_id=deal["deal_id"], commission_gbp=accrual)
        return []

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-07 RFP response
    # ------------------------------------------------------------------------------------------------
    def _on_rfp_received(self, msg: Message) -> list[Message]:
        b = msg.body
        value = int(_num(b.get("estimated_value_gbp")))
        employees = int(_num(b.get("employees"), ICP_MIN_EMPLOYEES))
        due_day = int(_num(b.get("due_day"), self.clock.day + 21))
        reasons = []
        if value < PRICE_LIST["forge_pilot"][1]:
            reasons.append("value_below_minimum_engagement")
        if due_day - self.clock.day < 10:
            reasons.append("response_window_under_10_days")
        if not (ICP_MIN_EMPLOYEES <= employees <= ICP_MAX_EMPLOYEES):
            reasons.append("outside_icp_size")
        if reasons:
            self._note("rfp_no_bid", f"RFP {b.get('rfp_id', '?')} no-bid: {', '.join(reasons)}",
                       rfp_id=b.get("rfp_id"), reasons=reasons)
            return []
        tier = str(b.get("tier") or "")
        if tier not in PRICE_LIST:
            fixed = sorted((p, t) for t, (line, p) in PRICE_LIST.items() if line != "keep" and p <= value)
            tier = fixed[-1][1] if fixed else "forge_pilot"
        deal = self._new_deal(b, tier, "rfp", rfp_id=b.get("rfp_id"))
        self._note("rfp_bid", f"RFP {b.get('rfp_id', '?')} bid -> {deal['deal_id']}", rfp_id=b.get("rfp_id"),
                   deal_id=deal["deal_id"])
        out = self._qualify_and_request(deal, f"RFP from {deal['client_name']}; response due day {due_day}",
                                        reply_to=msg.id)
        for m in out:
            m.body["rfp_due_day"] = due_day
        return out

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-08 renewals and churn defence
    # ------------------------------------------------------------------------------------------------
    def _on_renewal_due(self, msg: Message) -> list[Message]:
        b = msg.body
        client_id = b.get("client_id")
        if not client_id:
            self._note("unmatched", "renewal_due without client_id", source_topic=msg.topic)
            return []
        tier = str(b.get("tier") or "keep_plus")
        previous = int(_num(b.get("annual_value_gbp"), _num(b.get("amount_gbp"))) or
                       PRICE_LIST.get(tier, ("keep", 216_000))[1])
        cpi = _num(b.get("cpi_pct"), DEFAULT_CPI_PCT)
        uplift = min(cpi + KEEP_UPLIFT_MARGIN_PCT, KEEP_UPLIFT_CAP_PCT)
        at_risk = client_id in self.state["at_risk"] or _num(b.get("health_score"), 100) < 60
        if at_risk:
            uplift = 0.0  # save offer: uplift waived, within the 10% sales head authority
        new_value = int(round(previous * (1 + uplift / 100.0)))
        proposal_id = f"PR-{self._seq('proposal'):04d}"
        term_end = int(_num(b.get("due_day"), self.clock.day + RENEWAL_LEAD_DAYS))
        on_time = term_end - self.clock.day >= RENEWAL_LEAD_DAYS
        stats = self.state["stats"]
        stats["renewal_proposals"] += 1
        stats["renewals_on_time"] += 1 if on_time else 0
        self.state["renewals"][client_id] = {"proposal_id": proposal_id, "amount_gbp": new_value,
                                             "previous_gbp": previous, "uplift_pct": uplift}
        self._note("renewal_proposal", f"{client_id} {previous} -> {new_value} (uplift {uplift}%)",
                   client_id=client_id, on_time=on_time, save_offer=at_risk)
        return [self.emit("sales.renewal_proposal_sent", {
            "client_id": client_id, "client_name": b.get("client_name", ""), "contract_id": b.get("contract_id"),
            "proposal_id": proposal_id, "service_line": "keep", "tier": tier, "amount_gbp": new_value,
            "previous_amount_gbp": previous, "uplift_pct": uplift, "save_offer": at_risk,
            "summary": f"Keep renewal {tier}: {new_value} GBP per year (uplift {uplift}%, cap 7%)",
            "due_day": term_end}, reply_to=msg.id)]

    def _on_renewal_confirmed(self, msg: Message) -> list[Message]:
        client_id = msg.body.get("client_id")
        self.state["stats"]["renewals_confirmed"] += 1
        self.state["at_risk"].pop(client_id, None)
        amount = _num(msg.body.get("amount_gbp"), self.state["renewals"].get(client_id, {}).get("amount_gbp", 0))
        self.state["stats"]["expansion_and_renewal_bookings_gbp"] += amount
        self._note("renewal_confirmed", f"{client_id} renewed at {amount}", client_id=client_id)
        return []

    def _on_churn_risk(self, msg: Message) -> list[Message]:
        client_id = msg.body.get("client_id", "unknown")
        severity = str(msg.body.get("severity", "medium"))
        self.state["at_risk"][client_id] = severity
        self.create_task(f"Executive call with {client_id} within 2 days (churn risk {severity})",
                         due_in_days=2, priority="high" if severity in ("high", "critical") else "medium")
        self._note("churn_risk", f"{client_id} flagged {severity}", client_id=client_id, severity=severity)
        return []

    def _on_client_churned(self, msg: Message) -> list[Message]:
        client_id = msg.body.get("client_id")
        self.state["stats"]["churned"] += 1
        self.state["at_risk"].pop(client_id, None)
        out: list[Message] = []
        for deal in self._open_deals_for(client_id) if client_id else []:
            out.extend(self._lose(deal, "client_churned", msg.id))
        clawed = self._clawback(client_id, "client_terminated")
        self._note("client_churned", f"{client_id} churned; {len(out)} open deals closed", client_id=client_id,
                   commission_clawed_back_gbp=clawed)
        return out

    def _on_health_score(self, msg: Message) -> list[Message]:
        client_id = msg.body.get("client_id", "unknown")
        score = _num(msg.body.get("score", msg.body.get("health_score")), 100)
        self.state["health"][client_id] = score
        if score < 60:
            self.create_task(f"Account review for {client_id}: health score {score:g}", due_in_days=5,
                             priority="high")
        self._note("health_score", f"{client_id} score {score:g}", client_id=client_id, score=score)
        return []

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-09 expansion and change orders
    # ------------------------------------------------------------------------------------------------
    def _expansion_deal(self, body: dict, tier: str, source: str, reply_to: str) -> list[Message]:
        client_id = self._client_id(body)
        for open_deal in self._open_deals_for(client_id):
            if open_deal["tier"] == tier:
                self._note("expansion_duplicate", f"{client_id} already has open {tier}", client_id=client_id)
                return []
        deal = self._new_deal({**body, "client_id": client_id}, tier, source, security_waived=True)
        return self._qualify_and_request(
            deal, f"{deal['client_name']} expansion to {tier} ({source})", reply_to=reply_to)

    def _on_expansion(self, msg: Message) -> list[Message]:
        b = msg.body
        tier = str(b.get("tier") or "")
        if tier not in PRICE_LIST:
            tier = "keep_essential" if b.get("service_line") == "keep" else "forge_pilot"
        if not b.get("client_id") and not b.get("client_name"):
            self._note("unmatched", "expansion without a client", source_topic=msg.topic)
            return []
        return self._expansion_deal(b, tier, "expansion", msg.id)

    def _on_engagement_completed(self, msg: Message) -> list[Message]:
        b = msg.body
        tier = str(b.get("tier") or "")
        self._note("engagement_completed", f"{b.get('engagement_id', '?')} completed ({tier})",
                   engagement_id=b.get("engagement_id"))
        nxt = NEXT_OFFER.get(tier)
        if not nxt or not (b.get("client_id") or b.get("client_name")):
            return []
        return self._expansion_deal(b, nxt, "engagement_completed", msg.id)

    def _on_scope_change(self, msg: Message) -> list[Message]:
        b = msg.body
        days_by_level = dict(b.get("days_by_level") or {})
        if not days_by_level and b.get("extra_days"):
            days_by_level = {str(b.get("level", "senior_consultant")): _num(b["extra_days"])}
        amount = int(sum(RATE_CARD.get(level, 0) * _num(d) for level, d in days_by_level.items()))
        if amount <= 0:
            self._note("change_order_unpriced", "scope change without priceable days", source_topic=msg.topic)
            return []
        tier = str(b.get("tier") or "forge_build")
        tier = tier if tier in PRICE_LIST else "forge_build"
        deal = self._new_deal({**b, "list_price_gbp": amount}, tier, "change_order",
                              security_waived=True, change_order=True)
        deal["gates"]["scoping"] = True  # delivery has already scoped the change
        deal["stage"] = "scoped"
        self._note("change_order", f"{deal['deal_id']} {amount} GBP at rate card", deal_id=deal["deal_id"],
                   days_by_level=days_by_level)
        return self._qualify_and_request(deal, "Change order at rate card", reply_to=msg.id, announce_lead=False)

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-10 pipeline and forecast inputs
    # ------------------------------------------------------------------------------------------------
    def _on_capacity_forecast(self, msg: Message) -> list[Message]:
        util = _num(msg.body.get("utilisation_pct"), 70.0)
        tight = util > 85.0 or msg.body.get("capacity_status") == "tight"
        self.state["start_lag_days"] = 14 if tight else 0
        self._note("capacity", f"utilisation {util:g}%: start lag {self.state['start_lag_days']} days",
                   utilisation_pct=util)
        return []

    def _on_forecast(self, msg: Message) -> list[Message]:
        self.state["forecast"] = dict(msg.body)
        weighted = self._weighted_pipeline()
        self._note("forecast_received", f"data forecast stored; weighted pipeline {weighted:.0f}",
                   weighted_pipeline_gbp=weighted)
        return []

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-11 offer, price and collateral changes
    # ------------------------------------------------------------------------------------------------
    def _on_pricing_change_approved(self, msg: Message) -> list[Message]:
        b = msg.body
        tier = b.get("tier")
        if tier in PRICE_LIST:
            new_price = b.get("new_price_gbp")
            if new_price is None and b.get("change_pct") is not None:
                new_price = PRICE_LIST[tier][1] * (1 + _num(b["change_pct"]) / 100.0)
            if new_price:
                self.state["price_overrides"][tier] = int(round(_num(new_price)))
        self._note("pricing_change_approved", f"price list updated for {tier}", tier=tier)
        return []

    def _on_pricing_change_proposed(self, msg: Message) -> list[Message]:
        self.state["pending_price_changes"].append(dict(msg.body))
        self.create_task("Deal desk impact analysis of proposed price change", due_in_days=5)
        self._note("pricing_change_proposed", "proposed price change logged for impact analysis")
        return []

    def _on_capability_added(self, msg: Message) -> list[Message]:
        cap = str(msg.body.get("capability", msg.body.get("summary", "new capability")))
        self.state["capabilities"].append(cap)
        self.create_task(f"Update proposal templates and demo for: {cap}", due_in_days=10)
        self._note("capability_added", cap)
        return []

    def _on_roadmap(self, msg: Message) -> list[Message]:
        self.state["roadmap"] = dict(msg.body)
        self._note("roadmap", "product roadmap stored for pre-sales positioning")
        return []

    def _on_certification(self, msg: Message) -> list[Message]:
        cert = str(msg.body.get("certification", "unknown"))
        status = str(msg.body.get("status", "unknown"))
        self.state["certifications"][cert] = status
        self._note("certification", f"{cert}: {status}", certification=cert, status=status)
        return []

    def _on_campaign_launched(self, msg: Message) -> list[Message]:
        expected = int(_num(msg.body.get("expected_leads")))
        capacity = self._sdr_count() * SDR_LEADS_PER_MONTH
        if expected > 0.6 * capacity:
            self.create_task(f"Plan SDR capacity for campaign (about {expected} leads, capacity {capacity})",
                             due_in_days=5, priority="high")
        self._note("campaign", f"campaign {msg.body.get('campaign', '?')}: {expected} leads expected",
                   expected_leads=expected, capacity=capacity)
        return []

    def _on_content_published(self, msg: Message) -> list[Message]:
        self.state["library"].append(str(msg.body.get("title", msg.body.get("summary", "content"))))
        self._note("content", "asset added to the sales enablement library")
        return []

    def _on_event_scheduled(self, msg: Message) -> list[Message]:
        name = msg.body.get("event", msg.body.get("summary", "event"))
        self.create_task(f"Assign account executive and target list for {name}", due_in_days=7)
        self._note("event", f"event {name}: coverage task created")
        return []

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-12 planning, budget and hiring
    # ------------------------------------------------------------------------------------------------
    def _plan_year(self) -> int:
        """Budget cycles open in Q4 for the next fiscal year."""
        return max(1, min(3, self.clock.year_index + (1 if self.clock.date.month >= 10 else 0)))

    def _on_budget_cycle_opened(self, msg: Message) -> list[Message]:
        year = self._plan_year()
        cycle = msg.body.get("budget_cycle_id", f"BUD-{2025 + year}")
        if cycle in self.state["budget_cycles"]:
            return []
        self.state["budget_cycles"].append(cycle)
        people, non_people = DEPT_BUDGET_GBP[year]
        return [self.emit("sales.budget_submitted", {
            "department": "sales", "budget_cycle_id": cycle, "amount_gbp": people + non_people,
            "people_gbp": people, "non_people_gbp": non_people,
            "summary": f"Sales budget {cycle}: people {people}, non-people {non_people}"},
            recipient="finance", reply_to=msg.id)]

    def _on_budget_approved(self, msg: Message) -> list[Message]:
        year = self._plan_year()
        self.state["approved_budget"] = dict(msg.body)
        out = []
        for title, level, count, quarter in HIRING_PLAN.get(year, ()):
            out.append(self.emit("sales.hire_requested", {
                "department": "sales", "role_title": title, "level": level, "count": count,
                "start_quarter": quarter, "summary": f"{count} x {title} ({level}) starting {quarter}"},
                recipient="people", reply_to=msg.id))
        self._note("budget_approved", f"budget approved; {len(out)} hire requests raised", hires=len(out))
        return out

    def _on_okrs_set(self, msg: Message) -> list[Message]:
        self.state["okrs"] = dict(msg.body)
        self._note("okrs", "company OKRs stored; quota plan to be re-cut")
        return []

    def _on_strategy_updated(self, msg: Message) -> list[Message]:
        self.state["strategy"] = dict(msg.body)
        if self._lifts_crisis(msg.body):
            self._lift_crisis("CEO instruction on executive.strategy_updated")
        self._note("strategy", "strategy update logged; territory and ICP review scheduled")
        self.create_task("Review ICP, territories and quotas against strategy update", due_in_days=10)
        return []

    @staticmethod
    def _lifts_crisis(body: dict) -> bool:
        return bool(body.get("lifted") or body.get("crisis_lifted") or body.get("lift_crisis")
                    or str(body.get("status") or "").lower() in CRISIS_LIFT_STATUSES)

    def _on_crisis(self, msg: Message) -> list[Message]:
        """`executive.crisis_declared` switches crisis mode on; the same topic with a lifting status is the
        CEO's instruction that lifts it (SOP-SALES-14 step 5)."""
        if self._lifts_crisis(msg.body):
            self._lift_crisis("CEO instruction on executive.crisis_declared")
            return []
        if not self.state["crisis"]:
            self.state["crisis_started_day"] = self.clock.day
            self.state["crisis_review_raised"] = False
        self.state["crisis"] = True
        self.create_task("Crisis: re-forecast pipeline and brief top-10 opportunities", due_in_days=2,
                         priority="critical")
        self.state["crisis_task_id"] = self.create_task(
            "Crisis: record the CEO's instruction to lift crisis mode on the deal log (mark done when received)",
            due_in_days=CRISIS_REVIEW_DAYS, priority="high").id
        self._note("crisis", f"crisis mode: discount ceiling {CRISIS_DISCOUNT_CEILING_PCT}%",
                   severity=msg.body.get("severity", "high"))
        return []

    def _lift_crisis(self, how: str) -> None:
        if self.state["crisis"]:
            self.state["crisis"] = False
            self._note("crisis_lifted", f"crisis mode lifted: {how}", how=how)

    def _crisis_check(self) -> None:
        """Daily: the CEO instruction is recorded by closing the lift task; after 30 days a confirmation task is
        raised but the mode stays on until the CEO instructs otherwise."""
        if not self.state["crisis"]:
            return
        task = self.tasks.get(self.state["crisis_task_id"] or "")
        if task is not None and task.status in ("done", "cancelled"):
            self._lift_crisis("CEO instruction recorded (lift task closed)")
        elif (not self.state["crisis_review_raised"]
              and self.clock.day - (self.state["crisis_started_day"] or 0) >= CRISIS_REVIEW_DAYS):
            self.state["crisis_review_raised"] = True
            self.create_task("Crisis mode open 30 days: ask the CEO whether to lift or extend", due_in_days=2,
                             priority="high")

    # ------------------------------------------------------------------------------------------------
    # SOP-SALES-13 receivables interlock
    # ------------------------------------------------------------------------------------------------
    def _on_invoice_overdue(self, msg: Message) -> list[Message]:
        client_id = msg.body.get("client_id")
        if client_id and client_id not in self.state["holds"]:
            self.state["holds"].append(client_id)
        for deal in self._open_deals_for(client_id) if client_id else []:
            if "client_invoice_overdue" not in deal["risk_flags"]:
                deal["risk_flags"].append("client_invoice_overdue")
            deal["cfo_released"] = False
        clawed = 0.0
        if client_id and msg.body.get("written_off") and \
                _num(msg.body.get("days_overdue"), CLAWBACK_OVERDUE_DAYS) >= CLAWBACK_OVERDUE_DAYS:
            clawed = self._clawback(client_id, "invoice_written_off", window=False)
        self.create_task(f"Relationship call: {client_id} invoice {msg.body.get('invoice_id', '')} overdue",
                         due_in_days=2, priority="high")
        self._note("credit_hold", f"{client_id} on credit hold for new proposals", client_id=client_id,
                   commission_clawed_back_gbp=clawed)
        return []

    @staticmethod
    def _is_final_payment(body: dict) -> bool:
        milestone = str(body.get("milestone") or "").lower()
        return bool(body.get("final_milestone") or body.get("final_payment") or body.get("final")
                    or "final" in milestone or milestone.startswith("m3"))

    def _on_payment_received(self, msg: Message) -> list[Message]:
        """Clear the credit hold (CFO release), release held proposals and release commission after cash."""
        b = msg.body
        client_id = b.get("client_id")
        out: list[Message] = []
        if client_id in self.state["holds"]:
            self.state["holds"].remove(client_id)
            for deal in self._open_deals_for(client_id):
                deal["cfo_released"] = True
                out.extend(self._progress(deal, msg.id))
        final = self._is_final_payment(b)
        released_now = 0.0
        for c in self.state["commissions"].values():
            if c["status"] == "clawed_back" or (client_id and c["client_id"] != client_id):
                continue
            outstanding = round(c["accrued_gbp"] - c["released_gbp"], 2)
            if outstanding <= 0:
                continue
            if final:
                amount, c["status"] = outstanding, "released"
            elif c["status"] == "accrued":
                amount, c["status"] = round(c["accrued_gbp"] * COMMISSION_FIRST_RELEASE_SHARE, 2), "half_released"
            else:
                continue
            c["released_gbp"] = round(c["released_gbp"] + amount, 2)
            c["release_day"] = self.clock.day
            released_now += amount
        self.state["commission_released_gbp"] = round(self.state["commission_released_gbp"] + released_now, 2)
        self._note("payment_received", f"{client_id} paid; hold cleared; commission released {released_now:.2f}",
                   client_id=client_id, final_milestone=final, commission_released_now_gbp=released_now,
                   commission_released_gbp=self.state["commission_released_gbp"])
        return out

    def _clawback(self, client_id, reason: str, window: bool = True) -> float:
        """Claw back commission on a client's deals: termination inside 90 days of signature, or a written-off
        invoice more than 60 days overdue (economics.md section 3.4)."""
        total = 0.0
        for c in self.state["commissions"].values():
            if c["client_id"] != client_id or c["status"] == "clawed_back":
                continue
            if window and self.clock.day - c["signed_day"] > COMMISSION_CLAWBACK_DAYS:
                continue
            total += c["accrued_gbp"]
            self.state["commission_released_gbp"] = round(self.state["commission_released_gbp"] - c["released_gbp"], 2)
            c["status"], c["clawback_reason"], c["released_gbp"] = "clawed_back", reason, 0.0
        self.state["commission_clawed_back_gbp"] = round(self.state["commission_clawed_back_gbp"] + total, 2)
        return round(total, 2)

    # ------------------------------------------------------------------------------------------------
    # pipeline analytics and cadences
    # ------------------------------------------------------------------------------------------------
    def _weighted_pipeline(self) -> float:
        return sum(d["net_gbp"] * STAGE_WEIGHTS[d["stage"]] if d["net_gbp"]
                   else d["list_price_gbp"] * STAGE_WEIGHTS[d["stage"]]
                   for d in self.state["deals"].values() if d["stage"] in OPEN_STAGES)

    def pipeline_by_stage(self) -> dict[str, int]:
        counts = {s: 0 for s in OPEN_STAGES}
        for d in self.state["deals"].values():
            if d["stage"] in counts:
                counts[d["stage"]] += 1
        return counts

    def kpi_snapshot(self) -> list[Kpi]:
        """Current KPIs with actuals where the agent can measure them from its own state."""
        s = self.state["stats"]
        decided = s["won"] + s["lost"]  # new-logo proposals decided; pre-proposal losses are excluded
        actuals = {
            "new_logos_won": float(s["won"]),
            "win_rate": 100.0 * s["won"] / decided if decided else None,
            "lead_to_qualified_rate": 100.0 * s["lead_qualified"] / s["leads"] if s["leads"] else None,
            "qualified_to_proposal_rate": (100.0 * s["nl_proposals_sent"] / s["qualified"]
                                           if s["qualified"] else None),
            "sales_cycle_days": s["cycle_days_sum"] / s["won"] if s["won"] else None,
            "average_discount_percent": (s["discount_weighted"] / s["list_sent_gbp"]
                                         if s["list_sent_gbp"] else None),
            "new_logo_acv_bookings_gbp": float(s["bookings_gbp"]),
            "proposal_turnaround_days": (s["turnaround_days_sum"] / s["proposals_sent"]
                                         if s["proposals_sent"] else None),
            "renewal_proposal_on_time_percent": (100.0 * s["renewals_on_time"] / s["renewal_proposals"]
                                                 if s["renewal_proposals"] else None),
            "discount_policy_compliance_percent": (100.0 * s["compliant_proposals"] / s["proposals_sent"]
                                                   if s["proposals_sent"] else None),
        }
        return [Kpi(k.name, k.unit, k.target, actuals.get(k.name), k.higher_is_better) for k in KPIS]

    def _weekly_pipeline_review(self) -> None:
        self._note("pipeline_review", f"weekly review: weighted pipeline {self._weighted_pipeline():.0f} GBP",
                   stages=self.pipeline_by_stage(), weighted_pipeline_gbp=round(self._weighted_pipeline(), 2),
                   crisis=self.state["crisis"])

    def _monthly_snapshot(self) -> None:
        snap = {k.name: k.actual for k in self.kpi_snapshot() if k.actual is not None}
        self._note("monthly_kpi_snapshot", f"month start {self.clock.date.isoformat()}", kpis=snap)

    def _chase_stalled_deals(self) -> None:
        for deal in self.state["deals"].values():
            if deal["stage"] in ("qualified", "scoped") and not deal["chased"] and \
                    self.clock.day - deal["requested_day"] > 2 * SCOPING_SLA_DAYS:
                deal["chased"] = True
                self.create_task(f"Chase delivery and finance gates on {deal['deal_id']}", due_in_days=1,
                                 priority="high")
                self._note("gate_chase", f"{deal['deal_id']} stalled in {deal['stage']}", deal_id=deal["deal_id"])


def build_agent(llm, bus, clock, log) -> SalesAgent:
    """Construct the sales agent (does not register with the bus and does not publish)."""
    role = Role("Chief Revenue Officer", "sales", "head", (1, 1, 1), (140000, 200000), "Chief Executive Officer")
    return SalesAgent("sales", "sales", role, llm, bus, clock, log)
