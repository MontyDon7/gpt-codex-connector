"""Data and Analytics department agent for Lumenhall Partners.

The agent is the firm's metrics single source of truth in the simulation: it consumes lifecycle events from
the other departments, validates them (data quality checks), keeps deterministic firm-wide metrics
(pipeline, bookings, billings, collections, engagements, Keep ARR, client health), tracks forecast error and
publishes the monthly KPI report, forecasts, quality issues, agent quality reports and benchmarks.
See blueprint.md, sops.md, kpis.md and economics.md in this directory.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from typing import Callable, Optional

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# KPIs: FY2026 targets from kpis.md (COMPANY.md §5.4 budget, §5.3 funnel and §7 DSO targets underpin them).
KPIS: list[Kpi] = [
    Kpi("kpi_report_on_time_rate", "percent", 95.0, None, True),
    Kpi("data_quality_pass_rate", "percent", 95.0, None, True),
    Kpi("forecast_mape_bookings", "percent", 15.0, None, False),
    Kpi("certified_metric_coverage", "percent", 80.0, None, True),
    Kpi("certified_dashboard_share", "percent", 70.0, None, True),
    Kpi("dq_issue_mttr_days", "days", 5.0, None, False),
    Kpi("access_review_completion", "percent", 100.0, None, True),
    Kpi("agent_eval_coverage", "percent", 80.0, None, True),
    Kpi("client_data_segregation_breaches", "count", 0.0, None, False),
    Kpi("retention_schedule_compliance", "percent", 95.0, None, True),
    Kpi("platform_cost_per_active_client_gbp", "GBP", 2100.0, None, False),
]

# COMPANY.md §5.3: planning win rate used until enough decisions are observed.
PLANNING_WIN_RATE = 0.30
MIN_DECISIONS_FOR_OBSERVED_WIN_RATE = 5
FORECAST_HORIZON_DAYS = 90
MIN_FORECAST_BAND_PCT = 15.0          # kpis.md FY2026 MAPE target

# COMPANY.md §5.4: data budget envelope in GBP by year index (people, non-people).
BUDGET_GBP = {1: (90_000, 50_000), 2: (250_000, 110_000), 3: (1_000_000, 410_000)}
# COMPANY.md §6.1: data headcount (humans, agents) at year end by year index.
HEADCOUNT = {1: (1, 1), 2: (3, 3), 3: (9, 7)}

# blueprint.md section 5: (fiscal year index, quarter of request) -> roles to request (45-day time-to-hire).
HIRING_REQUESTS: dict[tuple[int, int], tuple[tuple[str, str, str], ...]] = {
    (2, 2): (("Senior Data Engineer", "senior_consultant", "FY2027 Q3"),),
    (2, 3): (("BI and Analytics Analyst", "consultant", "FY2027 Q4"),),
    (2, 4): (("Principal Data Architect", "principal", "FY2028 Q1"),
             ("Data Engineering Manager", "manager", "FY2028 Q1"),
             ("Senior Forecasting Scientist", "senior_consultant", "FY2028 Q1")),
    (3, 1): (("Data Governance Lead", "manager", "FY2028 Q2"),
             ("Senior Data Engineer", "senior_consultant", "FY2028 Q2")),
    (3, 3): (("BI and Analytics Analyst", "consultant", "FY2028 Q4"),),
}

# Required body keys per ingested topic (data quality check: completeness).
REQUIRED_KEYS: dict[str, tuple[str, ...]] = {
    "marketing.lead_generated": ("lead_id",),
    "sales.lead_qualified": ("lead_id",),
    "sales.proposal_sent": ("deal_id", "amount_gbp"),
    "sales.deal_won": ("deal_id", "client_id", "amount_gbp"),
    "sales.deal_lost": ("deal_id",),
    "delivery.engagement_kickoff": ("engagement_id", "client_id"),
    "delivery.engagement_completed": ("engagement_id",),
    "finance.invoice_issued": ("invoice_id", "amount_gbp"),
    "finance.payment_received": ("invoice_id", "amount_gbp"),
    "customer_success.health_score_updated": ("client_id", "score"),
    "customer_success.renewal_confirmed": ("client_id",),
    "customer_success.client_churned": ("client_id",),
}

# Topics whose first id key must be unique (data quality check: uniqueness).
UNIQUE_KEYS: dict[str, str] = {
    "sales.deal_won": "deal_id",
    "finance.invoice_issued": "invoice_id",
    "delivery.engagement_kickoff": "engagement_id",
}

# Client-identifying contact fields that never enter firm-wide marts or logs (client-data segregation).
PII_KEYS = ("email", "phone", "contact_email", "contact_phone", "address", "password", "token", "api_key")

# Issue SLA in days by severity (sops.md SOP-DATA-08).
ISSUE_SLA_DAYS = {"critical": 1, "high": 2, "medium": 5, "low": 10}


def _num(value: object) -> Optional[float]:
    """Return value as float if it is a real number (not bool), else None."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


class DataAgent(DepartmentAgent):
    """Chief Data and AI Officer agent: metrics, quality, forecasts and reporting."""

    SUBSCRIBES = subscribes_for("data")
    PUBLISHES = publishes_for("data")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.state.update({
            "events_seen": 0, "leads_generated": 0, "leads_qualified": 0, "campaigns": 0,
            "campaign_spend_gbp": 0.0, "proposals_sent": 0, "deals_won": 0, "deals_lost": 0,
            "bookings_gbp": 0.0, "lost_value_gbp": 0.0, "invoiced_gbp": 0.0, "collected_gbp": 0.0,
            "engagements_started": 0, "engagements_completed": 0, "renewals": 0, "churned_clients": 0,
            "keep_arr_gbp": 0.0, "checks_run": 0, "checks_failed": 0, "issues_raised": 0,
            "issues_suppressed": 0, "pii_fields_redacted": 0, "segregation_breaches": 0,
            "reports_published": 0, "reports_on_time": 0, "forecasts_published": 0, "market_points": 0,
            "benchmarks": 0, "crisis_mode": False, "retention_review_pending": False,
            "strategy_review_pending": False, "recognised_revenue_gbp": None, "cash_forecast": None,
            "okrs": None, "approved_budget": None,
            "open_pipeline": {}, "seen_ids": {}, "clients": {}, "health": {}, "active_engagements": {},
            "invoices": {}, "dso_samples": [], "bookings_ledger": [], "forecast_history": [],
            "mape_samples": [], "reported_periods": [], "forecast_months": [], "issue_keys": [],
            "agent_register": {}, "decisions": 0, "hire_requests_sent": [], "market": {},
            "bookings_by_line": {}, "pipeline_by_line": {},
        })
        self._handlers: dict[str, Callable[[Message], list[Message]]] = {
            "marketing.lead_generated": self._on_lead_generated,
            "marketing.campaign_launched": self._on_campaign_launched,
            "sales.lead_qualified": self._on_lead_qualified,
            "sales.proposal_sent": self._on_proposal_sent,
            "sales.deal_won": self._on_deal_won,
            "sales.deal_lost": self._on_deal_lost,
            "delivery.engagement_kickoff": self._on_engagement_kickoff,
            "delivery.engagement_completed": self._on_engagement_completed,
            "finance.invoice_issued": self._on_invoice_issued,
            "finance.payment_received": self._on_payment_received,
            "finance.month_end_closed": self._on_month_end_closed,
            "finance.cash_forecast_updated": self._on_cash_forecast_updated,
            "finance.budget_cycle_opened": self._on_budget_cycle_opened,
            "customer_success.health_score_updated": self._on_health_score,
            "customer_success.renewal_confirmed": self._on_renewal_confirmed,
            "customer_success.client_churned": self._on_client_churned,
            "executive.board_meeting_held": self._on_board_meeting,
            "executive.budget_approved": self._on_budget_approved,
            "executive.crisis_declared": self._on_crisis_declared,
            "executive.okrs_set": self._on_okrs_set,
            "executive.strategy_updated": self._on_strategy_updated,
            "legal.regulatory_change_noted": self._on_regulatory_change,
            "legal.ai_risk_review_completed": self._on_ai_risk_review_completed,
            "product.ai_risk_review_requested": self._on_ai_risk_review_requested,
            "external.market_data_published": self._on_market_data,
        }

    # ------------------------------------------------------------------ core
    def handle(self, message: Message) -> list[Message]:
        """Validate, ingest and react to one message. Never raises on a well-formed message."""
        handler = self._handlers.get(message.topic)
        if handler is None:
            self.log_event("data.activity.unhandled_topic", f"no handler for {message.topic}",
                           message_id=message.id)
            return []
        self.state["events_seen"] += 1
        out: list[Message] = []
        body = message.body if isinstance(message.body, dict) else {}
        out.extend(self._validate(message, body))
        self.log_event("data.activity.ingested", f"{message.topic} from {message.sender}",
                       message_id=message.id, source_topic=message.topic, body=self._scrub(body))
        out.extend(handler(message))
        return out

    def tick(self) -> list[Message]:
        """Monthly report and forecast, quarterly agent report and hiring requests, weekly crisis reports."""
        out: list[Message] = []
        if self.clock.is_month_start:
            first = self.clock.date.replace(day=1)
            prev = first - timedelta(days=1)
            if self.state["events_seen"] > 0:
                out.extend(self._publish_kpi_report(f"{prev.year}-{prev.month:02d}", "monthly_schedule"))
                out.extend(self._publish_forecast("monthly_schedule"))
            if self.clock.date.month in (1, 4, 7, 10):
                out.extend(self._quarterly_cadence())
        elif self.state["crisis_mode"] and self.state["events_seen"] > 0 and self.clock.every(7):
            out.extend(self._publish_kpi_report(f"crisis-day-{self.clock.day}", "crisis_weekly"))
        return out

    # ------------------------------------------------------------ validation
    @staticmethod
    def _scrub_dict(body: dict) -> tuple[dict, int]:
        clean = {k: v for k, v in body.items() if k not in PII_KEYS}
        return clean, len(body) - len(clean)

    def _scrub(self, body: dict) -> dict:
        """Strip contact details so they never reach firm-wide logs or marts."""
        clean, removed = self._scrub_dict(body)
        self.state["pii_fields_redacted"] += removed
        return clean

    def _validate(self, message: Message, body: dict) -> list[Message]:
        """Run completeness, validity and uniqueness checks; at most one issue per defect per month."""
        topic = message.topic
        problems: list[tuple[str, str, str]] = []   # (check, detail, severity)
        required = REQUIRED_KEYS.get(topic, ())
        if required:
            self.state["checks_run"] += 1
            missing = tuple(k for k in required if body.get(k) in (None, ""))
            if missing:
                money = any(k == "amount_gbp" for k in missing) or topic.startswith("finance.")
                problems.append(("completeness", "missing " + ",".join(missing),
                                 "high" if money else "medium"))
        if "amount_gbp" in body:
            self.state["checks_run"] += 1
            amount = _num(body.get("amount_gbp"))
            if amount is None or amount < 0:
                problems.append(("validity", "amount_gbp is not a non-negative number", "high"))
        key = UNIQUE_KEYS.get(topic)
        if key and body.get(key):
            self.state["checks_run"] += 1
            seen = self.state["seen_ids"].setdefault(topic, [])
            if body[key] in seen:
                problems.append(("uniqueness", f"duplicate {key} {body[key]}", "medium"))
            else:
                seen.append(body[key])
        out: list[Message] = []
        for check, detail, severity in problems:
            self.state["checks_failed"] += 1
            out.extend(self._raise_issue(message, check, detail, severity))
        return out

    def _raise_issue(self, message: Message, check: str, detail: str, severity: str) -> list[Message]:
        period = f"{self.clock.date.year}-{self.clock.date.month:02d}"
        issue_key = f"{message.topic}|{check}|{detail.split(' ')[0]}|{period}"
        if issue_key in self.state["issue_keys"]:
            self.state["issues_suppressed"] += 1
            return []
        self.state["issue_keys"].append(issue_key)
        self.state["issues_raised"] += 1
        issue_id = f"DQ-{self.state['issues_raised']:04d}"
        msg = self.emit("data.data_quality_issue_raised", {
            "issue_id": issue_id, "severity": severity, "check": check, "dataset": message.topic,
            "source_message_id": message.id, "source_department": message.sender,
            "department": message.sender, "due_day": self.clock.day + ISSUE_SLA_DAYS[severity],
            "summary": f"{check} check failed on {message.topic}: {detail}",
        })
        return [msg]

    # -------------------------------------------------------------- metrics
    def _decisions(self) -> int:
        return self.state["deals_won"] + self.state["deals_lost"]

    def _win_rate(self) -> Optional[float]:
        d = self._decisions()
        return self.state["deals_won"] / d if d else None

    def _open_pipeline(self) -> float:
        return float(sum(self.state["open_pipeline"].values()))

    def _dq_pass_rate(self) -> Optional[float]:
        run = self.state["checks_run"]
        return round(100.0 * (run - self.state["checks_failed"]) / run, 2) if run else None

    def _mape(self) -> Optional[float]:
        s = self.state["mape_samples"]
        return round(sum(s) / len(s), 2) if s else None

    def _dso(self) -> Optional[float]:
        s = self.state["dso_samples"]
        return round(sum(s) / len(s), 2) if s else None

    def _active_clients(self) -> int:
        return sum(1 for c in self.state["clients"].values() if c.get("status") == "active")

    def metrics(self) -> dict:
        """Deterministic snapshot of the firm-wide metrics (definitions in kpis.md section 2)."""
        s = self.state
        wr = self._win_rate()
        gen, qual = s["leads_generated"], s["leads_qualified"]
        health = list(s["health"].values())
        return {
            "leads_generated": gen, "leads_qualified": qual,
            "lead_to_qualified_rate": round(qual / gen, 4) if gen else None,
            "proposals_sent": s["proposals_sent"], "open_deals": len(s["open_pipeline"]),
            "open_pipeline_gbp": round(self._open_pipeline(), 2),
            "deals_won": s["deals_won"], "deals_lost": s["deals_lost"],
            "win_rate": round(wr, 4) if wr is not None else None,
            "bookings_gbp": round(s["bookings_gbp"], 2),
            "active_engagements": len(s["active_engagements"]),
            "engagements_completed": s["engagements_completed"],
            "invoiced_gbp": round(s["invoiced_gbp"], 2), "collected_gbp": round(s["collected_gbp"], 2),
            "outstanding_receivables_gbp": round(s["invoiced_gbp"] - s["collected_gbp"], 2),
            "dso_days": self._dso(), "keep_arr_gbp": round(s["keep_arr_gbp"], 2),
            "active_clients": self._active_clients(), "churned_clients": s["churned_clients"],
            "client_health_avg": round(sum(health) / len(health), 2) if health else None,
            "recognised_revenue_gbp": s["recognised_revenue_gbp"],
            "campaigns": s["campaigns"], "campaign_spend_gbp": round(s["campaign_spend_gbp"], 2),
            "agents_registered": len(s["agent_register"]),
        }

    def kpi_actuals(self) -> list[Kpi]:
        """KPIS with whatever actuals the agent can measure from the event stream."""
        s = self.state
        reg = s["agent_register"]
        evaluated = sum(1 for a in reg.values() if a.get("status") != "under_review")
        actual = {
            "kpi_report_on_time_rate": (round(100.0 * s["reports_on_time"] / s["reports_published"], 2)
                                        if s["reports_published"] else None),
            "data_quality_pass_rate": self._dq_pass_rate(),
            "forecast_mape_bookings": self._mape() if len(s["mape_samples"]) >= 4 else None,
            "agent_eval_coverage": round(100.0 * evaluated / len(reg), 2) if reg else None,
            "client_data_segregation_breaches": float(s["segregation_breaches"]),
        }
        return [replace(k, actual=actual.get(k.name)) for k in KPIS]

    # ------------------------------------------------------------- reports
    def _publish_kpi_report(self, period: str, reason: str) -> list[Message]:
        if period in self.state["reported_periods"]:
            return []
        self.state["reported_periods"].append(period)
        self.state["reports_published"] += 1
        if self.clock.date.day <= 5 or reason == "month_end_closed":
            self.state["reports_on_time"] += 1
        m = self.metrics()
        narrative = self.ask_llm(f"Summarise the firm KPI report for {period}: pipeline "
                                 f"{m['open_pipeline_gbp']} GBP, bookings {m['bookings_gbp']} GBP.")
        msg = self.emit("data.kpi_report_published", {
            "report_id": f"KR-{self.state['reports_published']:04d}", "period": period, "reason": reason,
            "metrics": m,
            "kpis": [{"name": k.name, "target": k.target, "actual": k.actual} for k in self.kpi_actuals()],
            "sources": ["sales", "marketing", "delivery", "finance", "customer_success"],
            "narrative": narrative,
            "summary": (f"KPI report {period}: pipeline GBP {m['open_pipeline_gbp']:,.0f}, bookings "
                        f"GBP {m['bookings_gbp']:,.0f}, invoiced GBP {m['invoiced_gbp']:,.0f}, "
                        f"collected GBP {m['collected_gbp']:,.0f}, active engagements "
                        f"{m['active_engagements']}"),
        })
        return [msg]

    def _score_forecasts(self) -> None:
        """Score every forecast whose 90-day window has fully elapsed (absolute percentage error)."""
        for fc in self.state["forecast_history"]:
            if fc.get("scored") or self.clock.day < fc["day"] + FORECAST_HORIZON_DAYS:
                continue
            end = fc["day"] + FORECAST_HORIZON_DAYS
            actual = sum(a for d, a in self.state["bookings_ledger"] if fc["day"] <= d < end)
            fc["scored"] = True
            fc["actual_gbp"] = actual
            if actual > 0:
                fc["ape_pct"] = round(abs(actual - fc["forecast_gbp"]) / actual * 100.0, 2)
                self.state["mape_samples"].append(fc["ape_pct"])

    def _publish_forecast(self, reason: str) -> list[Message]:
        month = f"{self.clock.date.year}-{self.clock.date.month:02d}"
        if month in self.state["forecast_months"]:
            return []
        self.state["forecast_months"].append(month)
        self._score_forecasts()
        observed = self._decisions() >= MIN_DECISIONS_FOR_OBSERVED_WIN_RATE
        wr = self._win_rate() if observed else PLANNING_WIN_RATE
        pipeline = self._open_pipeline()
        forecast = round(pipeline * (wr or 0.0), 2)
        mape = self._mape()
        band = max(mape or 0.0, MIN_FORECAST_BAND_PCT) / 100.0
        self.state["forecasts_published"] += 1
        self.state["forecast_history"].append({"day": self.clock.day, "forecast_gbp": forecast})
        open_deals = len(self.state["open_pipeline"])
        msg = self.emit("data.forecast_updated", {
            "forecast_id": f"FC-{self.state['forecasts_published']:04d}", "reason": reason,
            "horizon_days": FORECAST_HORIZON_DAYS, "open_pipeline_gbp": round(pipeline, 2),
            "win_rate_used": round(wr or 0.0, 4), "basis": "observed" if observed else "planning",
            "forecast_bookings_gbp": forecast, "low_gbp": round(forecast * (1 - band), 2),
            "high_gbp": round(forecast * (1 + band), 2), "mape_pct": mape,
            "expected_new_engagements": round(open_deals * (wr or 0.0), 2),
            "active_engagements": len(self.state["active_engagements"]),
            "outstanding_receivables_gbp": round(self.state["invoiced_gbp"] - self.state["collected_gbp"], 2),
            "summary": (f"90-day bookings forecast GBP {forecast:,.0f} from pipeline GBP {pipeline:,.0f} "
                        f"at {(wr or 0.0):.0%} win rate"),
        })
        return [msg]

    def _publish_agent_report(self, reason: str, agent: Optional[str] = None,
                              outcome: Optional[str] = None) -> list[Message]:
        reg = self.state["agent_register"]
        evaluated = sum(1 for a in reg.values() if a.get("status") != "under_review")
        coverage = round(100.0 * evaluated / len(reg), 2) if reg else None
        body = {
            "report_id": f"AQ-{self.state.get('agent_reports', 0) + 1:04d}", "report_type": reason,
            "agents_registered": len(reg), "agents_evaluated": evaluated, "coverage_pct": coverage,
            "under_review": sorted(n for n, a in reg.items() if a.get("status") == "under_review"),
            "rejected": sorted(n for n, a in reg.items() if a.get("status") == "rejected"),
            "summary": f"Agent quality report ({reason}): {evaluated} of {len(reg)} agents evaluated",
        }
        if agent:
            body["agent"] = agent
            body["outcome"] = outcome
        self.state["agent_reports"] = self.state.get("agent_reports", 0) + 1
        return [self.emit("data.agent_quality_report_published", body)]

    def _quarterly_cadence(self) -> list[Message]:
        """Quarterly: agent quality report, access review and retention review tasks, hiring requests."""
        out: list[Message] = []
        month = self.clock.date.month
        quarter = (month - 1) // 3 + 1
        if self.state["agent_register"]:
            out.extend(self._publish_agent_report("quarterly"))
        self.create_task(f"Complete FY quarter {quarter} access review and client-data segregation test",
                         due_in_days=30, priority="high")
        self.create_task("Review retention schedule and delete expired datasets", due_in_days=30)
        for role, level, start in HIRING_REQUESTS.get((self.clock.year_index, quarter), ()):
            key = f"{role}|{start}"
            if key in self.state["hire_requests_sent"]:
                continue
            self.state["hire_requests_sent"].append(key)
            out.append(self.emit("data.hire_requested", {
                "department": "data", "role": role, "level": level, "count": 1, "start_quarter": start,
                "summary": f"Data requests {role} to start {start} (blueprint hiring plan)",
            }))
        return out

    # ------------------------------------------------------ ingest handlers
    def _on_lead_generated(self, m: Message) -> list[Message]:
        lead = m.body.get("lead_id")
        if lead and lead in self.state["seen_ids"].setdefault("lead", []):
            return []
        if lead:
            self.state["seen_ids"]["lead"].append(lead)
        self.state["leads_generated"] += 1
        return []

    def _on_campaign_launched(self, m: Message) -> list[Message]:
        self.state["campaigns"] += 1
        spend = _num(m.body.get("budget_gbp", m.body.get("amount_gbp")))
        if spend and spend > 0:
            self.state["campaign_spend_gbp"] += spend
        return []

    def _on_lead_qualified(self, m: Message) -> list[Message]:
        lead = m.body.get("lead_id")
        seen = self.state["seen_ids"].setdefault("qualified", [])
        if lead and lead in seen:
            return []
        if lead:
            seen.append(lead)
        self.state["leads_qualified"] += 1
        return []

    def _on_proposal_sent(self, m: Message) -> list[Message]:
        deal = m.body.get("deal_id")
        amount = _num(m.body.get("amount_gbp"))
        if not deal or amount is None or amount < 0:
            return []
        if deal not in self.state["open_pipeline"]:
            self.state["proposals_sent"] += 1
        self.state["open_pipeline"][deal] = amount
        line = m.body.get("service_line")
        if line:
            self.state["pipeline_by_line"][deal] = line
        return []

    def _on_deal_won(self, m: Message) -> list[Message]:
        deal = m.body.get("deal_id")
        amount = _num(m.body.get("amount_gbp"))
        if deal in self.state["seen_ids"].get("won", []):
            return []
        if deal:
            self.state["seen_ids"].setdefault("won", []).append(deal)
        quoted = self.state["open_pipeline"].pop(deal, None) if deal else None
        line = m.body.get("service_line") or self.state["pipeline_by_line"].pop(deal, None)
        value = amount if amount is not None and amount >= 0 else (quoted or 0.0)
        self.state["deals_won"] += 1
        self.state["bookings_gbp"] += value
        self.state["bookings_ledger"].append((m.sim_time, value))
        if line:
            by = self.state["bookings_by_line"]
            by[line] = by.get(line, 0.0) + value
        client = m.body.get("client_id")
        if client:
            self.state["clients"][client] = {"name": m.body.get("client_name"), "status": "active"}
        if line == "keep":
            annual = _num(m.body.get("annual_value_gbp"))
            self.state["keep_arr_gbp"] += annual if annual is not None else value
        return []

    def _on_deal_lost(self, m: Message) -> list[Message]:
        deal = m.body.get("deal_id")
        if deal in self.state["seen_ids"].get("lost", []):
            return []
        if deal:
            self.state["seen_ids"].setdefault("lost", []).append(deal)
        value = self.state["open_pipeline"].pop(deal, None) if deal else None
        self.state["pipeline_by_line"].pop(deal, None)
        self.state["deals_lost"] += 1
        self.state["lost_value_gbp"] += value or 0.0
        return []

    def _on_engagement_kickoff(self, m: Message) -> list[Message]:
        eid = m.body.get("engagement_id")
        if eid and eid not in self.state["active_engagements"]:
            self.state["active_engagements"][eid] = m.body.get("client_id")
            self.state["engagements_started"] += 1
        return []

    def _on_engagement_completed(self, m: Message) -> list[Message]:
        self.state["active_engagements"].pop(m.body.get("engagement_id"), None)
        self.state["engagements_completed"] += 1
        return []

    def _on_invoice_issued(self, m: Message) -> list[Message]:
        inv = m.body.get("invoice_id")
        amount = _num(m.body.get("amount_gbp"))
        if not inv or amount is None or amount < 0 or inv in self.state["invoices"]:
            return []
        self.state["invoices"][inv] = {"amount": amount, "day": m.sim_time}
        self.state["invoiced_gbp"] += amount
        return []

    def _on_payment_received(self, m: Message) -> list[Message]:
        amount = _num(m.body.get("amount_gbp"))
        if amount is None or amount < 0:
            return []
        self.state["collected_gbp"] += amount
        inv = self.state["invoices"].get(m.body.get("invoice_id"))
        if inv is not None:
            self.state["dso_samples"].append(max(0, m.sim_time - inv["day"]))
        return []

    def _on_health_score(self, m: Message) -> list[Message]:
        score, client = _num(m.body.get("score")), m.body.get("client_id")
        if client and score is not None:
            self.state["health"][client] = score
        return []

    def _on_renewal_confirmed(self, m: Message) -> list[Message]:
        self.state["renewals"] += 1
        annual = _num(m.body.get("annual_value_gbp", m.body.get("amount_gbp")))
        if annual and annual > 0:
            self.state["keep_arr_gbp"] += annual
        client = m.body.get("client_id")
        if client:
            self.state["clients"].setdefault(client, {"name": m.body.get("client_name")})["status"] = "active"
        return []

    def _on_client_churned(self, m: Message) -> list[Message]:
        client = m.body.get("client_id")
        self.state["churned_clients"] += 1
        if client in self.state["clients"]:
            self.state["clients"][client]["status"] = "churned"
        self.state["health"].pop(client, None)
        annual = _num(m.body.get("annual_value_gbp", m.body.get("amount_gbp")))
        if annual and annual > 0:
            self.state["keep_arr_gbp"] = max(0.0, self.state["keep_arr_gbp"] - annual)
        return []

    # ------------------------------------------------- finance and executive
    def _on_month_end_closed(self, m: Message) -> list[Message]:
        revenue = _num(m.body.get("revenue_gbp"))
        if revenue is not None:
            self.state["recognised_revenue_gbp"] = revenue
        period = m.body.get("period") or f"{self.clock.date.year}-{self.clock.date.month:02d}"
        return self._publish_kpi_report(str(period), "month_end_closed")

    def _on_cash_forecast_updated(self, m: Message) -> list[Message]:
        self.state["cash_forecast"] = self._scrub_dict(m.body)[0]
        return self._publish_forecast("cash_forecast_updated")

    def _on_budget_cycle_opened(self, m: Message) -> list[Message]:
        fy = m.body.get("fiscal_year")
        year_idx = fy - 2025 if isinstance(fy, int) else self.clock.year_index + 1
        year_idx = max(1, min(3, year_idx))
        people, non_people = BUDGET_GBP[year_idx]
        humans, agents = HEADCOUNT[year_idx]
        msg = self.emit("data.budget_submitted", {
            "department": "data", "budget_cycle_id": m.body.get("budget_cycle_id", f"BUD-{2025 + year_idx}"),
            "amount_gbp": people + non_people, "people_gbp": people, "non_people_gbp": non_people,
            "headcount_humans": humans, "headcount_agents": agents,
            "summary": f"Data budget FY{2025 + year_idx}: GBP {people + non_people:,} (COMPANY.md 5.4)",
        })
        return [msg]

    def _on_budget_approved(self, m: Message) -> list[Message]:
        self.state["approved_budget"] = self._scrub_dict(m.body)[0]
        self.create_task("Reconcile data platform spend and headcount to the approved budget", due_in_days=14)
        return []

    def _on_board_meeting(self, m: Message) -> list[Message]:
        return self._publish_kpi_report(f"board-day-{m.sim_time}", "board_pack")

    def _on_crisis_declared(self, m: Message) -> list[Message]:
        self.state["crisis_mode"] = True
        self.create_task("Crisis mode: weekly KPI snapshots and daily cash and pipeline checks",
                         due_in_days=1, priority="critical")
        return self._publish_kpi_report(f"crisis-day-{m.sim_time}", "crisis_declared")

    def _on_okrs_set(self, m: Message) -> list[Message]:
        self.state["okrs"] = self._scrub_dict(m.body)[0]
        self.create_task("Map new OKRs to certified metrics and update registry targets", due_in_days=10)
        return []

    def _on_strategy_updated(self, m: Message) -> list[Message]:
        self.state["strategy_review_pending"] = True
        self.create_task("Review metric definitions and dashboards against the updated strategy",
                         due_in_days=20)
        return []

    # ------------------------------------------------- governance handlers
    def _on_regulatory_change(self, m: Message) -> list[Message]:
        self.state["retention_review_pending"] = True
        severity = m.body.get("severity", "medium")
        self.create_task("Assess regulatory change for retention, privacy and access rules: "
                         + str(m.body.get("summary", ""))[:80],
                         due_in_days=14, priority="high" if severity in ("high", "critical") else "medium")
        return []

    def _agent_key(self, body: dict) -> str:
        return str(body.get("agent_name") or body.get("agent_id") or body.get("agent")
                   or body.get("review_id") or body.get("summary") or "unnamed-agent")

    def _on_ai_risk_review_requested(self, m: Message) -> list[Message]:
        key = self._agent_key(m.body)
        self.state["agent_register"].setdefault(key, {"status": "under_review", "requested_day": m.sim_time})
        self.create_task(f"Add {key} to the evaluation harness and agent register", due_in_days=7)
        return []

    def _on_ai_risk_review_completed(self, m: Message) -> list[Message]:
        key = self._agent_key(m.body)
        outcome = str(m.body.get("outcome", "approved"))
        status = "rejected" if outcome.startswith("reject") else "approved"
        entry = self.state["agent_register"].setdefault(key, {"requested_day": m.sim_time})
        entry["status"] = status
        entry["completed_day"] = m.sim_time
        return self._publish_agent_report("post_review", agent=key, outcome=outcome)

    def _on_market_data(self, m: Message) -> list[Message]:
        self.state["market_points"] += 1
        indicator = str(m.body.get("indicator", "market_index"))
        self.state["market"][indicator] = m.body.get("value")
        self.state["benchmarks"] += 1
        wr, dso = self._win_rate(), self._dso()
        msg = self.emit("data.benchmark_ready", {
            "benchmark_id": f"BM-{self.state['benchmarks']:04d}", "indicator": indicator,
            "market_value": m.body.get("value"), "period": m.body.get("period"),
            "internal_win_rate": round(wr, 4) if wr is not None else None, "internal_dso_days": dso,
            "min_cohort_size": 5,
            "summary": f"Benchmark {indicator} refreshed from external market data",
        })
        return [msg]


def build_agent(llm, bus, clock, log) -> DataAgent:
    """Construct the data department agent (the Company registers it on the bus)."""
    role = Role("Chief Data and AI Officer", "data", "head", (1, 1, 1), (140000, 200000),
                "Chief Executive Officer")
    return DataAgent("data", "data", role, llm, bus, clock, log)
