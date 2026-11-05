"""Marketing department agent (brand, demand generation, content, events, lead generation).

Lifecycle behaviour (CONVENTIONS.md section 7.2, "Lead to cash to renewal", step 1):
``external.lead_inbound`` -> score and qualify -> ``marketing.lead_generated`` (sales, data).
Also: content and launch calendar driven by product events, case-study sourcing from client
feedback, brand-incident escalation, loss-reason learning from ``sales.deal_lost``, budget
submission and a monthly/quarterly cadence from ``tick()``.

All logic is deterministic, offline and works with ``core.MockLLM``.
"""

from __future__ import annotations

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# --- Facts (COMPANY.md) ------------------------------------------------------------------------
# COMPANY.md §5.4: marketing budget envelope, £k (people, non-people) for FY2026 / FY2027 / FY2028.
BUDGET_ENVELOPE_GBPK = {
    2026: {"people": 280, "non_people": 550, "total": 830},
    2027: {"people": 600, "non_people": 1250, "total": 1850},
    2028: {"people": 1000, "non_people": 3500, "total": 4500},
}
# COMPANY.md §5.3: leads needed per year (25% qualify downstream), FY2026 to FY2028.
LEAD_TARGETS = {2026: 640, 2027: 1200, 2028: 2267}
# COMPANY.md §3: tier prices used to size an inbound lead's likely entry offer.
ENTRY_TIERS = {
    "compass": ("compass_spark", 45000),
    "forge": ("forge_pilot", 90000),
    "keep": ("keep_essential", 96000),
}

# Ideal-customer-profile levers (modeled assumptions).
MQL_THRESHOLD = 50
TARGET_SECTORS = {"logistics", "financial_services", "insurance", "retail", "manufacturing",
                  "energy", "healthcare", "public_sector", "professional_services"}
SENIOR_TITLES = ("chief", "ceo", "cfo", "coo", "cto", "cio", "cdo", "vp", "vice president",
                 "director", "head of", "managing director", "partner")
SOURCE_POINTS = {"referral": 25, "event": 20, "direct": 15, "webinar": 15, "content_download": 10,
                 "paid_search": 8, "paid_social": 5, "organic_search": 8, "partner": 20}
FREE_MAIL_DOMAINS = ("gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "icloud.com")
DISQUALIFIED_TITLES = ("student", "intern", "researcher", "journalist")

# Average cost per lead by source (£, modeled) for spend attribution.
COST_PER_LEAD_GBP = {"referral": 0, "event": 310, "direct": 0, "webinar": 140, "content_download": 85,
                     "paid_search": 260, "paid_social": 210, "organic_search": 40, "partner": 120}

# COMPANY.md §6.1 headcount plan (humans) and §6.2 bands; used for the single hire request per year.
OPEN_ROLES = {
    2026: ("Demand Generation Manager", "manager", (92000, 115000)),
    2027: ("Content and Events Lead", "manager", (92000, 115000)),
    2028: ("Product Marketing Manager", "senior_consultant", (72000, 90000)),
}

# FY2026 targets (must mirror kpis.md).
KPIS = [
    Kpi("marketing_leads_generated", "count", 640.0, None),
    Kpi("lead_to_sql_rate", "percent", 25.0, None),
    Kpi("marketing_sourced_pipeline_gbp", "gbp", 12000000.0, None),
    Kpi("cost_per_qualified_lead_gbp", "gbp", 900.0, None, higher_is_better=False),
    Kpi("lead_response_time_hours", "hours", 4.0, None, higher_is_better=False),
    Kpi("content_pieces_published", "count", 96.0, None),
    Kpi("events_held", "count", 12.0, None),
    Kpi("case_studies_published", "count", 8.0, None),
    Kpi("brand_incidents_open_over_48h", "count", 0.0, None, higher_is_better=False),
    Kpi("marketing_budget_variance_pct", "percent", 5.0, None, higher_is_better=False),
]

_SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class MarketingAgent(DepartmentAgent):
    SUBSCRIBES = subscribes_for("marketing")
    PUBLISHES = publishes_for("marketing")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.state.update({
            "lead_counter": 0,
            "leads": {},                 # lead_id -> record
            "mql_count": 0,
            "nurture_count": 0,
            "disqualified_count": 0,
            "sql_count": 0,              # sales.lead_qualified feedback
            "pipeline_gbp": 0.0,
            "spend_gbp": 0.0,
            "leads_by_source": {},
            "sql_by_source": {},
            "content_published": 0,
            "case_studies_published": 0,
            "case_studies_requested": {},    # client_id -> day
            "events_held": 0,
            "events": [],
            "campaigns": {},
            "campaigns_paused": False,
            "crisis_mode": False,
            "brand_incidents": {},       # incident_id -> {raised_day, severity, ...}
            "loss_reasons": {},
            "okrs": {},
            "budget_approved": {},
            "budget_submitted_years": [],
            "hire_requested_years": [],
            "strategy_version": 0,
            "pricing_refresh_pending": False,
            "last_month_key": None,
            "last_quarter_key": None,
            "job_posts_amplified": 0,
            "response_hours_total": 0.0,
            "response_count": 0,
            "kpis": {},
        })
        self._handlers = {
            "external.lead_inbound": self._on_lead_inbound,
            "sales.lead_qualified": self._on_sales_lead_qualified,
            "sales.deal_lost": self._on_deal_lost,
            "customer_success.case_study_approved": self._on_case_study_approved,
            "customer_success.feedback_received": self._on_feedback_received,
            "data.benchmark_ready": self._on_benchmark_ready,
            "executive.budget_approved": self._on_budget_approved,
            "executive.crisis_declared": self._on_crisis_declared,
            "executive.okrs_set": self._on_okrs_set,
            "executive.pricing_change_approved": self._on_pricing_change,
            "executive.strategy_updated": self._on_strategy_updated,
            "finance.budget_cycle_opened": self._on_budget_cycle_opened,
            "people.job_posted": self._on_job_posted,
            "product.agent_capability_added": self._on_capability_added,
            "product.release_shipped": self._on_release_shipped,
            "product.roadmap_published": self._on_roadmap_published,
        }

    # ------------------------------------------------------------------ routing
    def handle(self, message: Message) -> list[Message]:
        handler = self._handlers.get(message.topic)
        if handler is None:
            self.log_event("marketing.activity.unhandled", f"no handler for {message.topic}")
            return []
        try:
            out = handler(message) or []
        except (KeyError, TypeError, ValueError, AttributeError) as exc:  # malformed body: never raise
            self.log_event("marketing.activity.error", f"could not process {message.topic}: {exc!r}")
            return []
        self._refresh_kpis()
        return list(out)

    # ------------------------------------------------------------------ helpers
    def _fy(self) -> int:
        return 2026 + min(max(self.clock.year_index, 0), 2)

    def _next_lead_id(self) -> str:
        self.state["lead_counter"] += 1
        return f"LD-{self.state['lead_counter']:05d}"

    def _score_lead(self, body: dict) -> tuple[int, list[str]]:
        """ICP and intent scoring, 0 to 100. Returns (score, reasons)."""
        score, why = 0, []
        employees = int(body.get("employees") or 0)
        if employees >= 1000:
            score += 30; why.append("enterprise_size")
        elif employees >= 250:
            score += 25; why.append("target_size")
        elif employees >= 100:
            score += 15; why.append("lower_mid_size")
        elif employees >= 50:
            score += 5; why.append("small_company")
        sector = str(body.get("sector") or body.get("industry") or "").lower()
        if sector in TARGET_SECTORS:
            score += 15; why.append("target_sector")
        title = str(body.get("contact_title") or body.get("title") or "").lower()
        if any(t in title for t in SENIOR_TITLES):
            score += 20; why.append("senior_buyer")
        source = str(body.get("source") or "direct").lower()
        pts = SOURCE_POINTS.get(source, 5)
        score += pts; why.append(f"source_{source}")
        if body.get("service_interest") or body.get("service_line"):
            score += 10; why.append("stated_service_interest")
        if body.get("budget_gbp") and float(body["budget_gbp"]) >= 45000:
            score += 10; why.append("budget_at_or_above_entry_tier")
        email = str(body.get("email") or "").lower()
        if any(email.endswith("@" + d) for d in FREE_MAIL_DOMAINS):
            score -= 30; why.append("free_mail_domain")
        if any(t in title for t in DISQUALIFIED_TITLES):
            score -= 50; why.append("non_buyer_persona")
        return max(0, min(100, score)), why

    def _suggest_offer(self, body: dict, employees: int) -> tuple[str, str, int]:
        line = str(body.get("service_interest") or body.get("service_line") or "").lower()
        if line not in ENTRY_TIERS:
            line = "compass" if employees < 1000 else "forge"
        tier, price = ENTRY_TIERS[line]
        return line, tier, price

    def _launch_content(self, kind: str, title: str, trigger: str, delay_days: int, **extra) -> Message:
        """Plan and schedule publication of a content asset; emits marketing.content_published."""
        asset_id = f"CNT-{self.state['content_published'] + 1:04d}"
        task = self.create_task(f"Produce {kind}: {title}", due_in_days=max(delay_days - 1, 1), priority="medium")
        body = {"asset_id": asset_id, "content_type": kind, "title": title, "trigger": trigger,
                "task_id": task.id, "summary": f"{kind}: {title}"}
        body.update(extra)
        self.state["content_published"] += 1
        return self.emit("marketing.content_published", body, delay_days=delay_days)

    # ------------------------------------------------------------------ external.lead_inbound
    def _on_lead_inbound(self, msg: Message) -> list[Message]:
        body = msg.body
        lead_id = body.get("lead_id") or self._next_lead_id()
        company = body.get("company") or body.get("client_name") or "Unknown company"
        employees = int(body.get("employees") or 0)
        source = str(body.get("source") or "direct").lower()
        score, reasons = self._score_lead(body)
        by_src = self.state["leads_by_source"]
        by_src[source] = by_src.get(source, 0) + 1
        self.state["spend_gbp"] += COST_PER_LEAD_GBP.get(source, 100)
        # Speed-to-lead: human or agent response inside the SLA window; referrals first.
        response_hours = 1.0 if source == "referral" else 2.5 if score >= MQL_THRESHOLD else 8.0
        self.state["response_hours_total"] += response_hours
        self.state["response_count"] += 1

        record = {"lead_id": lead_id, "company": company, "score": score, "source": source,
                  "employees": employees, "received_day": self.clock.day, "reasons": reasons}

        if "non_buyer_persona" in reasons or "free_mail_domain" in reasons and score < 25:
            record["status"] = "disqualified"
            self.state["disqualified_count"] += 1
            self.state["leads"][lead_id] = record
            self.log_event("marketing.activity.lead_disqualified",
                           f"{lead_id} {company} disqualified (score {score})", lead_id=lead_id, score=score)
            return []

        if score < MQL_THRESHOLD:
            record["status"] = "nurture"
            self.state["nurture_count"] += 1
            self.state["leads"][lead_id] = record
            self.create_task(f"Enrol {company} ({lead_id}) in 90-day nurture sequence", due_in_days=3, priority="low")
            self.log_event("marketing.activity.lead_nurtured",
                           f"{lead_id} {company} scored {score} < {MQL_THRESHOLD}; nurture",
                           lead_id=lead_id, score=score)
            return []

        line, tier, price = self._suggest_offer(body, employees)
        record.update({"status": "mql", "service_line": line, "tier": tier, "est_value_gbp": price})
        self.state["leads"][lead_id] = record
        self.state["mql_count"] += 1
        self.state["pipeline_gbp"] += price
        priority = "high" if score >= 75 or source == "referral" else "medium"
        self.create_task(f"Hand over {company} ({lead_id}) to sales with enrichment pack", due_in_days=1,
                         priority=priority)
        out = self.emit("marketing.lead_generated", {
            "lead_id": lead_id, "client_name": company, "company": company, "employees": employees,
            "sector": body.get("sector") or body.get("industry"), "source": source,
            "lead_score": score, "score_reasons": reasons, "service_line": line, "tier": tier,
            "amount_gbp": price, "contact_title": body.get("contact_title") or body.get("title"),
            "severity": "low" if priority == "medium" else "medium",
            "summary": f"MQL {lead_id}: {company}, score {score}, source {source}",
            "response_hours": response_hours,
        }, delay_days=1)
        return [out]

    # ------------------------------------------------------------------ sales.lead_qualified (feedback loop)
    def _on_sales_lead_qualified(self, msg: Message) -> list[Message]:
        body = msg.body
        lead_id = body.get("lead_id")
        rec = self.state["leads"].get(lead_id)
        self.state["sql_count"] += 1
        source = (rec or {}).get("source") or str(body.get("source") or "direct")
        sql = self.state["sql_by_source"]
        sql[source] = sql.get(source, 0) + 1
        if rec is not None:
            rec["status"] = "sql"
        amount = float(body.get("amount_gbp") or 0)
        if amount and rec is not None:
            self.state["pipeline_gbp"] += max(amount - float(rec.get("est_value_gbp") or 0), 0)
        self.log_event("marketing.activity.sql_feedback",
                       f"sales accepted {lead_id or 'lead'} from source {source}", lead_id=lead_id, source=source)
        out: list[Message] = []
        # Source quality check: after 10 MQLs, a source below 15% acceptance gets re-scoped.
        leads_total = self.state["mql_count"]
        if leads_total >= 10 and self.state["sql_count"] / leads_total < 0.15:
            self.create_task("Tighten ICP scoring: MQL to SQL acceptance below 15%", due_in_days=7, priority="high")
        # Opportunity-stage account-based follow-up: relevant case study to the buying committee.
        if body.get("client_name") or (rec and rec.get("company")):
            name = body.get("client_name") or rec["company"]
            self.create_task(f"Send sector proof pack to {name} buying committee", due_in_days=3, priority="medium")
        return out

    # ------------------------------------------------------------------ sales.deal_lost
    def _on_deal_lost(self, msg: Message) -> list[Message]:
        body = msg.body
        reason = str(body.get("loss_reason") or body.get("reason") or "unspecified").lower()
        lr = self.state["loss_reasons"]
        lr[reason] = lr.get(reason, 0) + 1
        client = body.get("client_name") or body.get("deal_id") or "unknown account"
        out: list[Message] = []
        if reason in ("competitor", "no_differentiation", "price", "brand_awareness"):
            self.create_task(f"Win/loss review: {client} lost on '{reason}'; update battlecard and messaging",
                             due_in_days=10, priority="medium")
        self.create_task(f"Add {client} to 180-day re-engagement nurture", due_in_days=14, priority="low")
        if lr[reason] >= 3 and reason in ("competitor", "no_differentiation", "brand_awareness"):
            cid = f"CMP-LOSS-{reason.upper()}-{self._fy()}"
            if cid not in self.state["campaigns"]:
                self.state["campaigns"][cid] = {"name": f"Counter-positioning: {reason}", "start_day": self.clock.day}
                out.append(self.emit("marketing.campaign_launched", {
                    "campaign_id": cid, "name": f"Counter-positioning: {reason}", "channel": "linkedin_and_email",
                    "budget_gbp": 18000, "target_segment": "lost_deals_and_lookalikes",
                    "summary": f"Win-back and positioning campaign after 3 losses on {reason}",
                }, delay_days=7))
                self.state["spend_gbp"] += 18000
        self.log_event("marketing.activity.loss_reason_recorded", f"{client}: {reason}", reason=reason)
        return out

    # ------------------------------------------------------------------ customer_success.*
    def _on_case_study_approved(self, msg: Message) -> list[Message]:
        body = msg.body
        client = body.get("client_name") or body.get("client_id") or "client"
        cid = body.get("client_id")
        self.state["case_studies_published"] += 1
        self.state["case_studies_requested"].pop(cid, None)
        # Case study pipeline: legal-approved quote check, design, layout, 2 weeks to publish.
        title = f"Case study: {client}" + (f" ({body.get('engagement_id')})" if body.get("engagement_id") else "")
        out = [self._launch_content("case_study", title, "customer_success.case_study_approved", 14,
                                    client_id=cid, client_name=client, engagement_id=body.get("engagement_id"))]
        self.create_task(f"Brief sales enablement on new case study for {client}", due_in_days=15, priority="low")
        return out

    def _on_feedback_received(self, msg: Message) -> list[Message]:
        body = msg.body
        client = body.get("client_name") or body.get("client_id") or "client"
        cid = body.get("client_id")
        score = body.get("nps", body.get("score"))
        sentiment = str(body.get("sentiment") or "").lower()
        public = bool(body.get("public") or str(body.get("channel") or "").lower() in
                      ("review_site", "social", "press", "linkedin", "x", "glassdoor"))
        severity = str(body.get("severity") or "low").lower()
        out: list[Message] = []
        negative = sentiment == "negative" or (isinstance(score, (int, float)) and score <= 6)
        positive = sentiment == "positive" or (isinstance(score, (int, float)) and score >= 9)
        if negative and public:
            sev = severity if severity in _SEVERITY_RANK else "medium"
            if sev == "low":
                sev = "medium"
            out.append(self._raise_brand_incident(
                f"Public negative feedback from {client}", sev, "client_feedback", cid, body.get("summary")))
        elif negative:
            self.create_task(f"Hold {client} out of advocacy and campaign lists (negative feedback)",
                             due_in_days=2, priority="medium")
            self.log_event("marketing.activity.advocacy_suppressed", f"{client} suppressed from advocacy")
        elif positive:
            if cid and cid not in self.state["case_studies_requested"]:
                self.state["case_studies_requested"][cid] = self.clock.day
                out.append(self.emit("marketing.case_study_requested", {
                    "client_id": cid, "client_name": client, "engagement_id": body.get("engagement_id"),
                    "service_line": body.get("service_line"), "nps": score,
                    "due_day": self.clock.day + 45,
                    "summary": f"Case study candidate: {client} (positive feedback)",
                }, delay_days=2))
            else:
                self.log_event("marketing.activity.testimonial_logged", f"testimonial from {client}")
        else:
            self.log_event("marketing.activity.feedback_logged", f"neutral feedback from {client}")
        return out

    def _raise_brand_incident(self, title: str, severity: str, source: str, client_id, detail) -> Message:
        n = len(self.state["brand_incidents"]) + 1
        iid = f"BI-{n:04d}"
        self.state["brand_incidents"][iid] = {"raised_day": self.clock.day, "severity": severity, "title": title}
        self.create_task(f"Brand incident {iid}: draft holding statement ({severity})", due_in_days=1,
                         priority="critical" if severity in ("high", "critical") else "high")
        return self.emit("marketing.brand_incident_raised", {
            "incident_id": iid, "title": title, "severity": severity, "source": source,
            "client_id": client_id, "detail": detail,
            "summary": f"{iid}: {title}", "due_day": self.clock.day + 1,
        })

    # ------------------------------------------------------------------ data.benchmark_ready
    def _on_benchmark_ready(self, msg: Message) -> list[Message]:
        body = msg.body
        name = body.get("benchmark_name") or body.get("title") or "AI adoption benchmark"
        sample = body.get("sample_size")
        extra = {"sample_size": sample} if sample else {}
        out = [self._launch_content("research_report", f"{name} report", "data.benchmark_ready", 14,
                                    gated=True, **extra)]
        self.create_task("Prepare press and analyst outreach for benchmark release (embargo list)",
                         due_in_days=10, priority="medium")
        # A gated research report anchors a lead-capture campaign.
        cid = f"CMP-BENCH-{self.state['content_published']:03d}"
        self.state["campaigns"][cid] = {"name": f"{name} lead capture", "start_day": self.clock.day + 14}
        out.append(self.emit("marketing.campaign_launched", {
            "campaign_id": cid, "name": f"{name} lead capture", "channel": "email_linkedin_paid_social",
            "budget_gbp": 24000, "target_segment": "cio_cdo_coo_mid_enterprise",
            "summary": "Gated benchmark report with paid amplification",
        }, delay_days=14))
        self.state["spend_gbp"] += 24000
        return out

    # ------------------------------------------------------------------ executive.*
    def _on_budget_approved(self, msg: Message) -> list[Message]:
        body = msg.body
        fy = int(body.get("fiscal_year") or body.get("year") or self._fy())
        envelope = BUDGET_ENVELOPE_GBPK.get(fy)
        approved = body.get("departments", {}).get("marketing") if isinstance(body.get("departments"), dict) else None
        total = approved if isinstance(approved, (int, float)) else (envelope or {}).get("total")
        self.state["budget_approved"][fy] = total
        self.log_event("marketing.activity.budget_confirmed", f"FY{fy} marketing budget £{total}k", fiscal_year=fy)
        out: list[Message] = []
        if fy in OPEN_ROLES and fy not in self.state["hire_requested_years"]:
            title, level, band = OPEN_ROLES[fy]
            self.state["hire_requested_years"].append(fy)
            out.append(self.emit("marketing.hire_requested", {
                "role_title": title, "level": level, "salary_band_gbp": list(band), "department": "marketing",
                "fiscal_year": fy, "summary": f"Marketing hire request for FY{fy}: {title}",
                "justification": "Headcount plan COMPANY.md §6.1",
            }))
        return out

    def _on_crisis_declared(self, msg: Message) -> list[Message]:
        self.state["crisis_mode"] = True
        self.state["campaigns_paused"] = True
        self.create_task("Crisis: pause scheduled social, email and paid campaigns; hold all outbound content",
                         due_in_days=0, priority="critical")
        self.create_task("Crisis: prepare approved holding lines with legal and executive comms", due_in_days=1,
                         priority="critical")
        self.log_event("marketing.activity.crisis_mode", f"crisis declared: {msg.body.get('summary', '')}",
                       severity=msg.body.get("severity", "high"))
        return []

    def _on_okrs_set(self, msg: Message) -> list[Message]:
        okrs = msg.body.get("okrs") if isinstance(msg.body.get("okrs"), (dict, list)) else msg.body
        self.state["okrs"] = {"received_day": self.clock.day, "payload": okrs}
        self.create_task("Translate company OKRs into marketing quarterly plan and KPI targets",
                         due_in_days=10, priority="high")
        self.log_event("marketing.activity.okrs_received", "company OKRs received")
        return []

    def _on_pricing_change(self, msg: Message) -> list[Message]:
        body = msg.body
        self.state["pricing_refresh_pending"] = True
        tier = body.get("tier") or "affected tiers"
        self.create_task(f"Update website pricing, decks and proposal collateral for {tier}",
                         due_in_days=5, priority="high")
        self.create_task("Pull pricing mentions from live campaigns and scheduled posts until updated",
                         due_in_days=1, priority="high")
        self.log_event("marketing.activity.pricing_refresh", f"pricing change for {tier}", tier=tier)
        return []

    def _on_strategy_updated(self, msg: Message) -> list[Message]:
        self.state["strategy_version"] += 1
        self.create_task("Refresh positioning and messaging house against updated company strategy",
                         due_in_days=14, priority="medium")
        self.log_event("marketing.activity.strategy_received", f"strategy v{self.state['strategy_version']}")
        return []

    # ------------------------------------------------------------------ finance.budget_cycle_opened
    def _on_budget_cycle_opened(self, msg: Message) -> list[Message]:
        fy = int(msg.body.get("fiscal_year") or msg.body.get("year") or self._fy() + (1 if self._fy() < 2028 else 0))
        envelope = BUDGET_ENVELOPE_GBPK.get(fy) or BUDGET_ENVELOPE_GBPK[min(max(fy, 2026), 2028)]
        if fy in self.state["budget_submitted_years"]:
            self.log_event("marketing.activity.budget_resubmission_skipped", f"FY{fy} already submitted")
            return []
        self.state["budget_submitted_years"].append(fy)
        leads = LEAD_TARGETS.get(fy, LEAD_TARGETS[2028])
        programme = envelope["non_people"]
        out = self.emit("marketing.budget_submitted", {
            "department": "marketing", "fiscal_year": fy,
            "people_gbpk": envelope["people"], "non_people_gbpk": programme, "total_gbpk": envelope["total"],
            "amount_gbp": envelope["total"] * 1000,
            "lead_target": leads,
            "cost_per_lead_gbp": round(programme * 1000 / leads),
            "summary": f"FY{fy} marketing budget £{envelope['total']}k supporting {leads} leads",
        })
        return [out]

    # ------------------------------------------------------------------ people.job_posted
    def _on_job_posted(self, msg: Message) -> list[Message]:
        body = msg.body
        title = body.get("role_title") or body.get("title") or "open role"
        self.state["job_posts_amplified"] += 1
        self.create_task(f"Amplify job post '{title}' on LinkedIn and careers page; employer-brand creative",
                         due_in_days=3, priority="low")
        self.state["spend_gbp"] += 400
        self.log_event("marketing.activity.job_post_amplified", f"employer brand support for {title}")
        return []

    # ------------------------------------------------------------------ product.*
    def _on_capability_added(self, msg: Message) -> list[Message]:
        body = msg.body
        cap = body.get("capability") or body.get("name") or body.get("summary") or "new agent capability"
        out = [self._launch_content("product_announcement", f"Introducing: {cap}", "product.agent_capability_added", 7)]
        self.create_task(f"Update Forge and Keep agent catalogue pages for '{cap}'", due_in_days=5, priority="medium")
        if self.state["campaigns_paused"]:
            self.log_event("marketing.activity.launch_held", "crisis mode: announcement scheduled but paid push held")
            return out
        cid = f"CMP-CAP-{self.state['content_published']:03d}"
        self.state["campaigns"][cid] = {"name": f"Capability launch: {cap}", "start_day": self.clock.day + 7}
        out.append(self.emit("marketing.campaign_launched", {
            "campaign_id": cid, "name": f"Capability launch: {cap}", "channel": "email_linkedin",
            "budget_gbp": 9000, "target_segment": "forge_and_keep_clients_and_prospects",
            "summary": f"Launch campaign for {cap}",
        }, delay_days=7))
        self.state["spend_gbp"] += 9000
        return out

    def _on_release_shipped(self, msg: Message) -> list[Message]:
        body = msg.body
        rel = body.get("release") or body.get("version") or body.get("name") or "latest release"
        out = [self._launch_content("release_note", f"What's new: {rel}", "product.release_shipped", 5)]
        self.create_task(f"Customer newsletter slot for release {rel}", due_in_days=7, priority="low")
        return out

    def _on_roadmap_published(self, msg: Message) -> list[Message]:
        self.create_task("Plan H2 content and launch calendar against published product roadmap",
                         due_in_days=10, priority="medium")
        self.state["calendar_synced_day"] = self.clock.day
        self.log_event("marketing.activity.roadmap_synced", "content calendar aligned to roadmap")
        return []

    # ------------------------------------------------------------------ tick (cadences)
    def tick(self) -> list[Message]:
        out: list[Message] = []
        clock = self.clock
        if clock.is_month_start:
            month_key = (clock.date.year, clock.date.month)
            if month_key != self.state["last_month_key"]:
                self.state["last_month_key"] = month_key
                self.create_task("Publish monthly marketing report: pipeline, CPL, content, events", due_in_days=5,
                                 priority="medium")
                self.log_event("marketing.activity.monthly_review",
                               f"month {month_key[0]}-{month_key[1]:02d} review opened")
                if not self.state["campaigns_paused"]:
                    out.append(self._launch_content(
                        "thought_leadership", f"Monthly insight article {month_key[0]}-{month_key[1]:02d}",
                        "tick.monthly_cadence", 10))
                # Quarter start: schedule the next client and prospect event.
                if month_key[1] in (1, 4, 7, 10):
                    qkey = (month_key[0], month_key[1])
                    if qkey != self.state["last_quarter_key"]:
                        self.state["last_quarter_key"] = qkey
                        if not self.state["crisis_mode"]:
                            out.append(self._schedule_event(qkey))
        self._refresh_kpis()
        return out

    def _schedule_event(self, qkey: tuple) -> Message:
        n = len(self.state["events"]) + 1
        eid = f"EVT-{qkey[0]}-{n:03d}"
        kind = "executive_roundtable" if n % 2 else "ai_operations_breakfast"
        capacity = 24 if kind == "executive_roundtable" else 60
        held_day = self.clock.day + 45
        self.state["events"].append({"event_id": eid, "kind": kind, "day": held_day})
        self.state["events_held"] += 1
        self.state["spend_gbp"] += 6500 if kind == "executive_roundtable" else 9500
        self.create_task(f"Run {kind.replace('_', ' ')} {eid}: venue, speakers, invitations", due_in_days=40,
                         priority="medium")
        return self.emit("marketing.event_scheduled", {
            "event_id": eid, "event_type": kind, "city": "London", "capacity": capacity,
            "due_day": held_day, "estimated_cost_gbp": 6500 if kind == "executive_roundtable" else 9500,
            "needs": ["venue_booking", "catering", "av_and_security_pass"],
            "summary": f"{kind.replace('_', ' ')} in London, {capacity} guests",
        })

    # ------------------------------------------------------------------ KPI bookkeeping
    def _refresh_kpis(self) -> None:
        st = self.state
        mql, sql = st["mql_count"], st["sql_count"]
        total_inbound = mql + st["nurture_count"] + st["disqualified_count"]
        actual = {
            "marketing_leads_generated": float(mql),
            "lead_to_sql_rate": round(100.0 * sql / mql, 1) if mql else None,
            "marketing_sourced_pipeline_gbp": float(st["pipeline_gbp"]),
            "cost_per_qualified_lead_gbp": round(st["spend_gbp"] / mql, 1) if mql else None,
            "lead_response_time_hours": round(st["response_hours_total"] / st["response_count"], 2)
            if st["response_count"] else None,
            "content_pieces_published": float(st["content_published"]),
            "events_held": float(st["events_held"]),
            "case_studies_published": float(st["case_studies_published"]),
            "brand_incidents_open_over_48h": float(sum(
                1 for i in st["brand_incidents"].values() if self.clock.day - i["raised_day"] > 2)),
        }
        st["inbound_total"] = total_inbound
        st["kpis"] = {k: v for k, v in actual.items() if v is not None}

    def kpi_snapshot(self) -> list[Kpi]:
        """KPIS with current actuals filled in (FY2026 targets unchanged)."""
        self._refresh_kpis()
        return [Kpi(k.name, k.unit, k.target, self.state["kpis"].get(k.name), k.higher_is_better) for k in KPIS]


def build_agent(llm, bus, clock, log) -> MarketingAgent:
    # COMPANY.md §6.1 / §6.2: Chief Marketing Officer, head level, 1 in every year, £140k to £200k.
    role = Role("Chief Marketing Officer", "marketing", "head", (1, 1, 1), (140000, 200000),
                "Chief Executive Officer")
    return MarketingAgent("marketing", "marketing", role, llm, bus, clock, log)
