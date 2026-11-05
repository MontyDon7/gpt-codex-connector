"""People department agent (recruiting, onboarding, offboarding, payroll liaison, performance,
culture, UK employment basics, human oversight of AI in HR decisions).

Lifecycle behaviour (CONVENTIONS.md section 7.2):
* Hiring: ``<d>.hire_requested`` -> ``people.requisition_opened`` -> ``executive.headcount_approved``
  -> ``people.job_posted`` -> ``external.candidate_applied`` -> ``people.offer_accepted`` ->
  ``people.new_hire_started`` -> ``it_security.access_provisioned`` + ``operations.workspace_ready``
  -> onboarding complete -> ``people.compliance_training_completed``.
* Leavers: resignation / human-approved dismissal -> ``people.employee_left`` ->
  ``it_security.access_revoked``.
* Contractors: ``delivery.staffing_requested`` -> bench check -> ``people.contractor_engaged``
  (IR35 status determination attached).
* Budgeting: ``finance.budget_cycle_opened`` -> ``people.budget_submitted``.
* Compliance: ``legal.policy_update_published`` / ``legal.regulatory_change_noted`` -> training.
* Culture: quarterly pulse -> ``people.engagement_survey_completed`` (from ``tick()``).

Human oversight (COMPANY.md §9.4): the agent screens, drafts and recommends only. Final hiring and
termination decisions are human; the simulation records them as ``decision_by`` fields. Protected
characteristics (Equality Act 2010) are stripped before any scoring.

All logic is deterministic, offline and works with ``core.MockLLM``.
"""

from __future__ import annotations

from dataclasses import replace

from core import DepartmentAgent, Kpi, Message, Role, publishes_for, subscribes_for

# --- Facts (COMPANY.md) ------------------------------------------------------------------------
# COMPANY.md §5.4: people budget envelope, £k, FY2026 / FY2027 / FY2028.
BUDGET_ENVELOPE_GBPK = {
    2026: {"people": 210, "non_people": 100, "total": 310},
    2027: {"people": 400, "non_people": 300, "total": 700},
    2028: {"people": 750, "non_people": 1100, "total": 1850},
}
# COMPANY.md §6.1: year-end humans by department (Y1, Y2, Y3).
HEADCOUNT_PLAN = {
    "executive": (3, 4, 5), "sales": (5, 14, 26), "marketing": (3, 8, 14), "delivery": (14, 46, 104),
    "finance": (2, 5, 10), "people": (2, 5, 10), "legal": (1, 3, 5), "it_security": (2, 5, 9),
    "operations": (2, 6, 12), "customer_success": (1, 6, 14), "product": (2, 5, 12), "data": (1, 3, 9),
}
# COMPANY.md §6.2: salary bands by level key (base salary, GBP, London; US hires +15%).
LEVEL_BANDS = {
    "analyst": (38000, 48000), "consultant": (55000, 70000), "senior_consultant": (72000, 90000),
    "manager": (92000, 115000), "principal": (120000, 155000), "partner": (160000, 220000),
    "head": (140000, 200000), "executive": (200000, 260000),
}
US_UPLIFT = 1.15              # COMPANY.md §6.2
ONCOST_MULTIPLIER = 1.28      # COMPANY.md §8 item 5 (employer on-costs 28%)
TIME_TO_HIRE_TARGET_DAYS = 45  # COMPANY.md §8 item 3
ATTRITION_TARGET_PCT = 14.0    # COMPANY.md §8 item 3 (Y1)
# COMPANY.md §9.3: spend delegations (non-budgeted spend > £50k CFO; > £250k CEO).
CFO_SPEND_THRESHOLD_GBP = 50000
CEO_SPEND_THRESHOLD_GBP = 250000
# COMPANY.md §9.1 / §9.3: executive hires go to the Board; new headcount outside budget to the CEO.
BOARD_LEVELS = ("head", "executive")

# --- Modeled HR assumptions (UK) --------------------------------------------------------------
NOTICE_DAYS_BY_LEVEL = {"analyst": 28, "consultant": 28, "senior_consultant": 56, "manager": 56,
                        "principal": 84, "partner": 90, "head": 90, "executive": 90}
PROBATION_MONTHS = 6
STATUTORY_HOLIDAY_DAYS = 28          # statutory minimum incl. bank holidays (5.6 weeks)
CONTRACTUAL_HOLIDAY_DAYS = 25        # plus bank holidays (modeled company policy)
OFFER_DECISION_DAYS = 14             # screening + interviews + panel decision, human-led
JOB_POST_DAYS_AFTER_APPROVAL = 2
REQUISITION_VALIDATION_DAYS = 1
SCREEN_SHORTLIST_THRESHOLD = 60
ONBOARDING_ESCALATION_DAYS = 2       # access/workspace missing this many days after start
TRAINING_COURSES = ("UK GDPR and data protection", "Information security awareness",
                    "Acceptable use of AI tools", "Anti-bribery and conflicts of interest",
                    "Equality, diversity and anti-harassment")
PROTECTED_KEYS = ("age", "date_of_birth", "dob", "gender", "sex", "ethnicity", "race", "religion",
                  "religion_or_belief", "marital_status", "pregnancy", "disability", "sexual_orientation",
                  "nationality", "gender_reassignment", "photo", "maiden_name")
# Modeled contractor day rates by level (GBP), for spend-delegation checks only.
CONTRACTOR_DAY_RATE_GBP = {"analyst": 300, "consultant": 450, "senior_consultant": 600, "manager": 750,
                           "principal": 950, "partner": 1200}
REGULATION_KEYWORDS = ("employment", "working time", "holiday", "pay", "equality", "discrimination",
                       "pension", "immigration", "right to work", "parental", "leave", "redundancy",
                       "whistleblow", "automated decision", "ai ", "data protection", "ico")

# FY2026 targets (must mirror kpis.md).
KPIS = [
    Kpi("time_to_hire_days", "days", 45.0, None, higher_is_better=False),
    Kpi("offer_acceptance_rate_pct", "percent", 85.0, None),
    Kpi("annualised_attrition_pct", "percent", 14.0, None, higher_is_better=False),
    Kpi("engagement_score", "score_out_of_100", 75.0, None),
    Kpi("compliance_training_completion_pct", "percent", 98.0, None),
    Kpi("day_one_readiness_pct", "percent", 95.0, None),
    Kpi("cost_per_hire_gbp", "gbp", 7500.0, None, higher_is_better=False),
    Kpi("leaver_access_revoked_24h_pct", "percent", 100.0, None),
    Kpi("right_to_work_before_start_pct", "percent", 100.0, None),
    Kpi("ai_hr_decisions_human_reviewed_pct", "percent", 100.0, None),
]


def _num(value, default=0.0) -> float:
    try:
        if isinstance(value, bool):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _pct(numerator: float, denominator: float):
    return None if not denominator else round(100.0 * numerator / denominator, 1)


class PeopleAgent(DepartmentAgent):
    SUBSCRIBES = subscribes_for("people")
    PUBLISHES = publishes_for("people")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        s = self.state
        s.update({
            "req_seq": 0, "emp_seq": 0, "cand_seq": 0, "contractor_seq": 0,
            "requisitions": {},       # REQ-id -> dict
            "candidates": {},         # candidate_id -> dict
            "employees": {},          # EMP-id -> dict (joiners processed by this agent)
            "leavers": {},            # EMP-id -> dict
            "contractors": {},        # contractor_id -> dict
            "growth_reqs": {},        # (department, year_index) -> count of growth requisitions
            "hires_ytd": {},          # department -> hires started (this agent's view)
            "bench_fte": 2,           # modeled delivery bench (unallocated consultants)
            "capacity": {},           # last delivery capacity forecast
            "policies": {},           # policy_id -> dict
            "regulatory_watch": [],
            "okrs": None, "strategy": None,
            "hiring_freeze": False, "freeze_reason": None,
            "approved_budget": {}, "budgets_submitted": {},
            "ai_decision_log": [],    # AI-assisted screening records, all human-reviewed
            "protected_fields_stripped": 0,
            "pulse_quarters": [],
            "payroll_months": [],
            "escalated": set(),
            "metrics": {
                "time_to_hire_samples": [], "offers_made": 0, "offers_accepted": 0, "offers_declined": 0,
                "hires": 0, "leavers": 0, "voluntary_leavers": 0, "day_one_ready": 0, "day_one_total": 0,
                "access_revoked_24h": 0, "access_revoked_total": 0, "rtw_before_start": 0, "rtw_total": 0,
                "training_assigned": 0, "training_completed": 0, "ai_decisions": 0, "ai_decisions_reviewed": 0,
                "recruiting_cost_gbp": 0.0, "engagement_score": None,
            },
        })

    # ------------------------------------------------------------------ routing
    def handle(self, message: Message) -> list[Message]:
        topic = message.topic
        body = message.body if isinstance(message.body, dict) else {}
        if topic.endswith(".hire_requested"):
            return self._on_hire_requested(message, body)
        routes = {
            "executive.headcount_approved": self._on_headcount_approved,
            "external.candidate_applied": self._on_candidate_applied,
            "it_security.access_provisioned": self._on_access_provisioned,
            "operations.workspace_ready": self._on_workspace_ready,
            "it_security.access_revoked": self._on_access_revoked,
            "delivery.staffing_requested": self._on_staffing_requested,
            "delivery.capacity_forecast_updated": self._on_capacity_forecast,
            "finance.budget_cycle_opened": self._on_budget_cycle_opened,
            "executive.budget_approved": self._on_budget_approved,
            "executive.crisis_declared": self._on_crisis_declared,
            "executive.okrs_set": self._on_okrs_set,
            "executive.strategy_updated": self._on_strategy_updated,
            "legal.policy_update_published": self._on_policy_update,
            "legal.regulatory_change_noted": self._on_regulatory_change,
            "people.internal.resignation_received": self._on_resignation,
            "people.internal.dismissal_decided": self._on_dismissal,
        }
        fn = routes.get(topic)
        if fn is None:
            self.log_event("people.activity.unhandled_topic", f"no behaviour for {topic}", topic=topic)
            return []
        return fn(message, body)

    # ------------------------------------------------------------------ helpers
    def _year(self) -> int:
        return max(1, min(3, self.clock.year_index))

    def _next_id(self, key: str, prefix: str, width: int = 4) -> str:
        self.state[key] += 1
        return f"{prefix}-{self.state[key]:0{width}d}"

    def _band_for(self, level: str, location: str = "London") -> tuple[int, int]:
        lo, hi = LEVEL_BANDS.get(level, LEVEL_BANDS["consultant"])
        if str(location).upper() in ("US", "USA", "UNITED STATES", "NEW YORK"):
            return int(lo * US_UPLIFT), int(hi * US_UPLIFT)
        return lo, hi

    def _find_requisition(self, body: dict, statuses: tuple[str, ...]):
        reqs = self.state["requisitions"]
        rid = body.get("requisition_id")
        if rid in reqs and reqs[rid]["status"] in statuses:
            return reqs[rid]
        dept, role = body.get("department"), body.get("role") or body.get("role_title")
        candidates = [r for r in reqs.values() if r["status"] in statuses]
        if dept:
            candidates = [r for r in candidates if r["department"] == dept] or []
        if role and candidates:
            by_role = [r for r in candidates if r["role"] == role]
            candidates = by_role or candidates
        return candidates[0] if candidates else None

    def _task(self, title: str, due_in_days: int = 5, priority: str = "medium"):
        return self.create_task(title, due_in_days=due_in_days, priority=priority)

    # ------------------------------------------------------------------ recruiting
    def _on_hire_requested(self, message: Message, body: dict) -> list[Message]:
        dept = body.get("department") or message.sender
        role = str(body.get("role") or body.get("role_title") or "Consultant")
        level = str(body.get("level") or "consultant")
        if level not in LEVEL_BANDS:
            level = "consultant"
        reason = str(body.get("reason") or "growth")
        location = body.get("location") or "London"
        reqs = self.state["requisitions"]
        # de-duplicate: an open requisition for the same department and role is not re-opened.
        for r in reqs.values():
            if r["department"] == dept and r["role"] == role and r["status"] in ("pending_approval", "approved", "posted") \
                    and r["source_message"] != message.id and r["reason"] == reason and not body.get("openings"):
                self.log_event("people.activity.duplicate_requisition", f"{dept} {role} already open as {r['id']}",
                               requisition_id=r["id"])
                return []
        lo, hi = self._band_for(level, location)
        year = self._year()
        plan = HEADCOUNT_PLAN.get(dept, (1, 1, 1))
        allowed_net_adds = plan[year - 1] - (plan[year - 2] if year > 1 else 0)
        key = (dept, year)
        growth_count = self.state["growth_reqs"].get(key, 0)
        outside_plan = False
        if reason != "backfill":
            growth_count += 1
            self.state["growth_reqs"][key] = growth_count
            outside_plan = growth_count > max(allowed_net_adds, 0)
        rid = self._next_id("req_seq", "REQ")
        approver = "board" if level in BOARD_LEVELS else ("ceo" if outside_plan else "ceo_standard_delegation")
        req = {
            "id": rid, "department": dept, "role": role, "level": level, "location": location, "reason": reason,
            "openings": int(_num(body.get("openings"), 1)) or 1, "filled": 0, "status": "pending_approval",
            "opened_day": self.clock.day, "band_gbp": (lo, hi), "outside_plan": outside_plan,
            "approver": approver, "source_message": message.id, "posted_day": None, "stale_flagged": False,
            "justification": str(body.get("justification") or body.get("summary") or ""),
        }
        reqs[rid] = req
        self.create_task(f"Validate {rid} ({role}, {dept}) against budget, band and plan", due_in_days=1,
                         priority="high" if outside_plan else "medium")
        self.log_event("people.activity.requisition_validated", f"{rid} {role} ({dept}) band {lo}-{hi}",
                       requisition_id=rid, outside_plan=outside_plan, hiring_freeze=self.state["hiring_freeze"])
        out_body = {
            "requisition_id": rid, "department": dept, "role": role, "level": level, "reason": reason,
            "openings": req["openings"], "salary_band_gbp": [lo, hi],
            "loaded_cost_max_gbp": int(hi * ONCOST_MULTIPLIER),
            "planned_year_end_headcount": plan[year - 1], "outside_approved_plan": outside_plan,
            "approval_route": approver, "hiring_freeze_exception_required": self.state["hiring_freeze"],
            "target_time_to_hire_days": TIME_TO_HIRE_TARGET_DAYS,
            "summary": f"{role} ({level}) for {dept}: {reason}",
        }
        return [self.emit("people.requisition_opened", out_body, delay_days=REQUISITION_VALIDATION_DAYS)]

    def _on_headcount_approved(self, message: Message, body: dict) -> list[Message]:
        req = self._find_requisition(body, ("pending_approval",))
        if req is None:
            self.log_event("people.activity.approval_unmatched", "headcount approval matched no open requisition",
                           body=body)
            return []
        decision = str(body.get("decision") or body.get("status") or "approved").lower()
        if body.get("approved") is False or decision in ("rejected", "denied", "declined", "deferred"):
            req["status"] = "cancelled"
            self.create_task(f"Close {req['id']}: headcount not approved; inform {req['department']} head", 2)
            self.log_event("people.activity.requisition_cancelled", f"{req['id']} not approved", requisition_id=req["id"])
            return []
        req["status"] = "approved"
        req["approved_day"] = self.clock.day
        lo, hi = req["band_gbp"]
        self.create_task(f"Draft job spec and inclusive advert for {req['id']} ({req['role']}); hiring manager to sign off", 2)
        self.create_task(f"Agree interview panel and structured scorecard for {req['id']}", 3)
        req["posted_day"] = self.clock.day + JOB_POST_DAYS_AFTER_APPROVAL
        req["status"] = "posted"
        advert = self._advert_copy(req)
        return [self.emit("people.job_posted", {
            "requisition_id": req["id"], "department": req["department"], "role": req["role"], "level": req["level"],
            "salary_band_gbp": [lo, hi], "location": req["location"], "openings": req["openings"],
            "channels": ["careers_page", "linkedin", "referral_scheme"] + (["specialist_agency"] if req["level"] in ("principal", "partner", "head", "executive") else []),
            "closing_day": self.clock.day + JOB_POST_DAYS_AFTER_APPROVAL + 28,
            "summary": advert,
        }, delay_days=JOB_POST_DAYS_AFTER_APPROVAL)]

    def _advert_copy(self, req: dict) -> str:
        lo, hi = req["band_gbp"]
        try:
            text = self.ask_llm(f"Write a two sentence inclusive job advert for {req['role']} at Lumenhall Partners, "
                                f"salary £{lo:,} to £{hi:,}. Salary range must be stated.")
        except Exception:  # LLM is optional; never let drafting break the lifecycle
            text = ""
        return text or f"{req['role']} at Lumenhall Partners, London. Salary £{lo:,} to £{hi:,}."

    def _strip_protected(self, body: dict) -> dict:
        clean = {}
        for k, v in body.items():
            if str(k).lower() in PROTECTED_KEYS:
                self.state["protected_fields_stripped"] += 1
                continue
            clean[k] = v
        return clean

    def _screen_score(self, clean: dict) -> int:
        score = 30
        years = _num(clean.get("years_experience"), 0.0)
        score += int(min(years, 10) * 3)
        skills = clean.get("skills_matched")
        required = clean.get("skills_required")
        if isinstance(skills, (list, tuple)) and isinstance(required, (list, tuple)) and required:
            score += int(40 * len(set(skills) & set(required)) / len(set(required)))
        elif isinstance(skills, (list, tuple)):
            score += min(40, 8 * len(skills))
        if clean.get("source") == "referral":
            score += 5
        override = clean.get("screen_score")
        if override is not None:
            score = int(_num(override, score))
        return max(0, min(100, score))

    def _on_candidate_applied(self, message: Message, body: dict) -> list[Message]:
        clean = self._strip_protected(body)
        req = self._find_requisition(clean, ("posted",))
        cid = str(clean.get("candidate_id") or self._next_id("cand_seq", "CAND", 5))
        name = str(clean.get("candidate_name") or clean.get("name") or cid)
        if req is None:
            self.state["candidates"][cid] = {"id": cid, "name": name, "status": "talent_pool", "day": self.clock.day}
            self.log_event("people.activity.talent_pool", f"{name} added to talent pool (no open requisition)", candidate_id=cid)
            return []
        score = self._screen_score(clean)
        recommend = score >= SCREEN_SHORTLIST_THRESHOLD and clean.get("right_to_work") is not False
        m = self.state["metrics"]
        m["ai_decisions"] += 1
        m["ai_decisions_reviewed"] += 1  # every AI-assisted screening outcome is queued for named human review
        self.state["ai_decision_log"].append({
            "candidate_id": cid, "requisition_id": req["id"], "score": score, "recommendation": "shortlist" if recommend else "reject_pending_human_review",
            "human_reviewer": "Recruiter" if req["level"] not in BOARD_LEVELS else "Chief People Officer",
            "inputs": sorted(k for k in clean if k not in ("candidate_name", "name")), "day": self.clock.day,
        })
        cand = {"id": cid, "name": name, "requisition_id": req["id"], "score": score, "status": "screened",
                "applied_day": self.clock.day, "expected_salary_gbp": _num(clean.get("expected_salary_gbp"), 0.0),
                "notice_days": clean.get("notice_period_days"), "right_to_work": clean.get("right_to_work", True),
                "offer_declined": bool(clean.get("offer_declined")), "source": clean.get("source", "careers_page")}
        self.state["candidates"][cid] = cand
        m["recruiting_cost_gbp"] += 3500.0 if clean.get("source") == "agency" else 900.0
        if not recommend:
            cand["status"] = "rejection_pending_human_review"
            self.create_task(f"Human review: confirm or overturn AI screen rejection of {cid} for {req['id']} (score {score})", 3)
            self.log_event("people.activity.screen_rejection_queued", f"{cid} score {score}; human to confirm", candidate_id=cid)
            return []
        cand["status"] = "shortlisted"
        self.create_task(f"Interview {name} ({cid}) for {req['id']}; panel scorecard, two interviewers, record decision", 7, "high")
        if cand["offer_declined"]:
            cand["status"] = "offer_declined"
            m["offers_made"] += 1
            m["offers_declined"] += 1
            self.create_task(f"Offer declined by {name}: capture reason and re-open shortlist for {req['id']}", 3)
            self.log_event("people.activity.offer_declined", f"{name} declined offer for {req['id']}", requisition_id=req["id"])
            return []
        return self._make_offer(req, cand, clean)

    def _make_offer(self, req: dict, cand: dict, clean: dict) -> list[Message]:
        lo, hi = req["band_gbp"]
        expected = cand["expected_salary_gbp"] or (lo + hi) / 2
        offer_salary = int(max(lo, min(hi, expected)))
        exception = expected > hi
        if exception:
            self.create_task(f"Pay exception: {cand['name']} expects £{int(expected):,} above band max £{hi:,}; CPO and CFO approval needed", 3, "high")
        notice = int(_num(cand["notice_days"], NOTICE_DAYS_BY_LEVEL.get(req["level"], 28))) or NOTICE_DAYS_BY_LEVEL.get(req["level"], 28)
        m = self.state["metrics"]
        m["offers_made"] += 1
        m["offers_accepted"] += 1
        accept_day = self.clock.day + OFFER_DECISION_DAYS
        start_day = accept_day + notice
        ttf = accept_day - req["opened_day"]
        m["time_to_hire_samples"].append(ttf)
        req["filled"] += 1
        if req["filled"] >= req["openings"]:
            req["status"] = "filled"
        cand["status"] = "offer_accepted"
        cand["start_day"] = start_day
        eid = self._next_id("emp_seq", "EMP")
        rtw_due = start_day - 1
        self.state["employees"][eid] = {
            "id": eid, "name": cand["name"], "department": req["department"], "role": req["role"], "level": req["level"],
            "requisition_id": req["id"], "start_day": start_day, "base_salary_gbp": offer_salary, "access": False,
            "workspace": False, "onboarded": False, "right_to_work_checked": False, "status": "pre_start",
            "probation_review_day": start_day + int(PROBATION_MONTHS * 30.4), "probation_flagged": False,
            "time_to_hire_days": ttf, "candidate_id": cand["id"],
        }
        self.create_task(f"Right-to-work check for {eid} before day one (due day {rtw_due}); statutory excuse needs original or share-code check", max(1, rtw_due - self.clock.day), "high")
        self.create_task(f"Issue contract and section 1 written statement for {eid} (due on or before day one); pension auto-enrolment set up", max(1, start_day - self.clock.day))
        self.log_event("people.activity.offer_accepted", f"{cand['name']} accepted {req['role']} ({req['id']}), starts day {start_day}",
                       employee_id=eid, time_to_hire_days=ttf)
        out = [self.emit("people.offer_accepted", {
            "requisition_id": req["id"], "employee_id": eid, "candidate_id": cand["id"], "candidate_name": cand["name"],
            "department": req["department"], "role": req["role"], "level": req["level"],
            "base_salary_gbp": offer_salary, "loaded_annual_cost_gbp": int(offer_salary * ONCOST_MULTIPLIER),
            "start_day": start_day, "notice_period_days": notice, "probation_months": PROBATION_MONTHS,
            "annual_leave_days": CONTRACTUAL_HOLIDAY_DAYS, "pay_exception": exception,
            "decision_by": "hiring_manager_and_chief_people_officer", "ai_role": "screening_recommendation_only",
            "right_to_work_check_due_day": rtw_due, "time_to_hire_days": ttf,
            "summary": f"{cand['name']} accepted {req['role']} in {req['department']}",
        }, delay_days=OFFER_DECISION_DAYS)]
        out.append(self.emit("people.new_hire_started", {
            "employee_id": eid, "requisition_id": req["id"], "employee_name": cand["name"], "department": req["department"],
            "role": req["role"], "level": req["level"], "start_day": start_day, "base_salary_gbp": offer_salary,
            "needs": ["laptop", "workspace", "access_provisioning", "payroll_setup"],
            "access_profile": req["department"], "right_to_work_verified": True,
            "summary": f"Day one for {cand['name']} ({req['role']})",
        }, delay_days=OFFER_DECISION_DAYS + notice))
        self.state["employees"][eid]["right_to_work_checked"] = True
        return out

    # ------------------------------------------------------------------ onboarding
    def _employee_by_message(self, body: dict):
        emps = self.state["employees"]
        eid = body.get("employee_id")
        if eid in emps:
            return emps[eid]
        name = body.get("employee_name") or body.get("name")
        pending = [e for e in emps.values() if not e["onboarded"] and e["status"] != "left"]
        if name:
            for e in pending:
                if e["name"] == name:
                    return e
        return pending[0] if pending else None

    def _on_access_provisioned(self, message: Message, body: dict) -> list[Message]:
        emp = self._employee_by_message(body)
        if emp is None:
            self.log_event("people.activity.access_unmatched", "access provisioned for unknown employee", body=body)
            return []
        emp["access"] = True
        self.log_event("people.activity.access_confirmed", f"{emp['id']} access ready", employee_id=emp["id"])
        return self._maybe_complete_onboarding(emp)

    def _on_workspace_ready(self, message: Message, body: dict) -> list[Message]:
        emp = self._employee_by_message(body)
        if emp is None:
            self.log_event("people.activity.workspace_unmatched", "workspace ready for unknown employee", body=body)
            return []
        emp["workspace"] = True
        self.log_event("people.activity.workspace_confirmed", f"{emp['id']} workspace ready", employee_id=emp["id"])
        return self._maybe_complete_onboarding(emp)

    def _maybe_complete_onboarding(self, emp: dict) -> list[Message]:
        if emp["onboarded"] or not (emp["access"] and emp["workspace"]):
            return []
        emp["onboarded"] = True
        emp["status"] = "active"
        m = self.state["metrics"]
        m["hires"] += 1
        m["day_one_total"] += 1
        m["rtw_total"] += 1
        m["rtw_before_start"] += 1 if emp["right_to_work_checked"] else 0
        if self.clock.day <= emp["start_day"] + 1:
            m["day_one_ready"] += 1
        self.state["hires_ytd"][emp["department"]] = self.state["hires_ytd"].get(emp["department"], 0) + 1
        self.create_task(f"30/60/90 day check-ins for {emp['id']}; buddy assigned; probation review day {emp['probation_review_day']}", 30)
        self.create_task(f"Add {emp['id']} to payroll (starter checklist, P45/starter declaration, NI, pension) before next cut-off", 5, "high")
        m["training_assigned"] += 1
        return [self.emit("people.compliance_training_completed", {
            "scope": "new_starter_induction", "employee_id": emp["id"], "department": emp["department"],
            "courses": list(TRAINING_COURSES), "completion_pct": 100.0, "completed_by_day": self.clock.day + 10,
            "population": 1, "completed": 1, "mandatory_before_system_access_extension": True,
            "summary": f"Induction compliance training completed by {emp['id']}",
        }, delay_days=10)] + self._count_training(1)

    def _count_training(self, completed: int) -> list:
        self.state["metrics"]["training_completed"] += completed
        return []

    # ------------------------------------------------------------------ offboarding
    def _on_resignation(self, message: Message, body: dict) -> list[Message]:
        return self._offboard(body, involuntary=False)

    def _on_dismissal(self, message: Message, body: dict) -> list[Message]:
        return self._offboard(body, involuntary=True)

    def _offboard(self, body: dict, involuntary: bool) -> list[Message]:
        eid = str(body.get("employee_id") or "")
        emp = self.state["employees"].get(eid) or {}
        dept = body.get("department") or emp.get("department") or "delivery"
        if involuntary and not body.get("human_decision_ref"):
            key = f"dismissal-held-{eid}"
            if key not in self.state["escalated"]:
                self.state["escalated"].add(key)
                self.create_task(f"HOLD: termination of {eid or 'employee'} lacks a recorded human decision and fair process (ACAS Code); Chief People Officer and GC review", 1, "critical")
            self.log_event("people.activity.termination_blocked", "agents may not make termination decisions", employee_id=eid)
            return []
        level = emp.get("level") or str(body.get("level") or "consultant")
        notice = int(_num(body.get("notice_period_days"), NOTICE_DAYS_BY_LEVEL.get(level, 28)))
        last_day = int(_num(body.get("last_day"), self.clock.day + (0 if involuntary and body.get("pay_in_lieu") else notice)))
        reason = str(body.get("reason") or ("dismissal" if involuntary else "resignation"))
        if eid in self.state["leavers"]:
            return []
        self.state["leavers"][eid or f"unlisted-{len(self.state['leavers'])+1}"] = {"day": self.clock.day, "last_day": last_day, "reason": reason, "department": dept}
        if emp:
            emp["status"] = "leaving"
        m = self.state["metrics"]
        m["leavers"] += 1
        m["voluntary_leavers"] += 0 if involuntary else 1
        self.create_task(f"Exit interview and knowledge handover for {eid or dept} by day {last_day}", max(1, last_day - self.clock.day))
        self.create_task(f"Final pay: accrued holiday, notice, expenses to payroll cut-off for {eid or dept}; return of equipment", max(1, last_day - self.clock.day))
        out = [self.emit("people.employee_left", {
            "employee_id": eid or None, "department": dept, "role": emp.get("role") or body.get("role"),
            "level": level, "reason": reason, "voluntary": not involuntary, "last_day": last_day,
            "notice_period_days": notice, "revoke_access_by_day": last_day, "involuntary": involuntary,
            "decision_ref": body.get("human_decision_ref"), "restrictive_covenants_apply": level in ("principal", "partner", "head", "executive"),
            "final_pay_items": ["salary_to_last_day", "accrued_holiday", "expenses", "pay_in_lieu_if_applicable"],
            "summary": f"{eid or 'Employee'} leaves {dept} on day {last_day} ({reason})",
        })]
        if not involuntary and body.get("regretted", True) and body.get("backfill", True) and dept in HEADCOUNT_PLAN:
            out.append(self.emit("people.hire_requested", {
                "department": dept, "role": emp.get("role") or body.get("role") or "Consultant", "level": level,
                "reason": "backfill", "summary": f"Backfill for {eid or 'leaver'}",
            }, recipient="executive", delay_days=1))
        return out

    def _on_access_revoked(self, message: Message, body: dict) -> list[Message]:
        eid = body.get("employee_id")
        leaver = self.state["leavers"].get(eid)
        if leaver is None and not self.state["leavers"]:
            self.log_event("people.activity.revocation_unmatched", "access revoked with no open leaver", body=body)
            return []
        if leaver is None:
            for k, v in self.state["leavers"].items():
                if not v.get("revoked"):
                    eid, leaver = k, v
                    break
        if leaver is None or leaver.get("revoked"):
            return []
        leaver["revoked"] = True
        within = self.clock.day <= leaver["last_day"] + 1
        m = self.state["metrics"]
        m["access_revoked_total"] += 1
        m["access_revoked_24h"] += 1 if within else 0
        if eid in self.state["employees"]:
            self.state["employees"][eid]["status"] = "left"
        if not within:
            self.create_task(f"Late access revocation for {eid}: log security event with CISO team", 1, "high")
        self.log_event("people.activity.offboarding_complete", f"{eid} access revoked; offboarding closed", employee_id=eid, within_sla=within)
        return []

    # ------------------------------------------------------------------ staffing and capacity
    def _on_staffing_requested(self, message: Message, body: dict) -> list[Message]:
        needed = int(_num(body.get("consultants_needed") or body.get("fte") or body.get("headcount"), 1)) or 1
        weeks = int(_num(body.get("duration_weeks"), 12)) or 12
        eng = body.get("engagement_id")
        level = str(body.get("level") or "consultant")
        bench = self.state["bench_fte"]
        from_bench = min(bench, needed)
        self.state["bench_fte"] = bench - from_bench
        shortfall = needed - from_bench
        out: list[Message] = []
        if from_bench:
            out.append(self.emit("people.internal.staffing_fulfilled", {
                "engagement_id": eng, "fte_from_bench": from_bench, "remaining_shortfall_fte": shortfall,
                "bench_fte_after": self.state["bench_fte"], "summary": f"{from_bench} FTE allocated from bench",
            }, recipient=message.sender if message.sender in HEADCOUNT_PLAN else "delivery"))
        if shortfall <= 0:
            self.create_task(f"Confirm bench allocation for {eng}", 2)
            return out
        rate = CONTRACTOR_DAY_RATE_GBP.get(level, 450)
        days = weeks * 5
        value = rate * days * shortfall
        approval = "ceo" if value > CEO_SPEND_THRESHOLD_GBP else ("cfo" if value > CFO_SPEND_THRESHOLD_GBP else "people_head")
        cid = self._next_id("contractor_seq", "CTR")
        self.state["contractors"][cid] = {"id": cid, "engagement_id": eng, "fte": shortfall, "value_gbp": value, "day": self.clock.day}
        start_day = int(_num(body.get("start_day"), self.clock.day + 10))
        self.create_task(f"IR35 status determination and right-to-work check for {cid} ({shortfall} FTE); supply via approved agency or PSC with SDS issued", 3, "high")
        if value > CFO_SPEND_THRESHOLD_GBP:
            self.create_task(f"Spend approval ({approval}) for contractor engagement {cid}, £{value:,}", 2, "high")
        out.append(self.emit("people.contractor_engaged", {
            "contractor_id": cid, "engagement_id": eng, "department": "delivery", "fte": shortfall, "level": level,
            "day_rate_gbp": rate, "planned_days": days, "contract_value_gbp": value, "amount_gbp": value,
            "start_day": start_day, "end_day": start_day + weeks * 7, "ir35_status": "outside_ir35_sds_issued" if level != "analyst" else "inside_ir35_via_umbrella_or_paye",
            "status_determination_statement_issued": True, "right_to_work_checked": True,
            "approval_required": approval, "requires_data_processing_terms": True,
            "summary": f"{shortfall} contractor FTE for {eng} ({weeks} weeks)",
        }, delay_days=2))
        if weeks >= 26:
            out.append(self.emit("people.hire_requested", {
                "department": "delivery", "role": "Consultant" if level == "consultant" else level.replace("_", " ").title(),
                "level": level, "reason": "convert_long_running_contractor", "openings": shortfall,
                "summary": f"Contractor on {eng} runs {weeks} weeks; convert to permanent",
            }, recipient="executive", delay_days=3))
        return out

    def _on_capacity_forecast(self, message: Message, body: dict) -> list[Message]:
        self.state["capacity"] = dict(body)
        util = _num(body.get("utilisation_pct") or body.get("utilization_pct"), 0.0)
        gap = _num(body.get("gap_fte") or body.get("shortfall_fte"), 0.0)
        if gap > 0 or util > 85:
            key = f"capacity-{self.clock.day // 14}"
            if key not in self.state["escalated"]:
                self.state["escalated"].add(key)
                self.create_task(f"Capacity gap {gap:g} FTE (utilisation {util:g}%): review hiring pipeline, bench and contractor bridge", 5, "high")
        elif util and util < 55:
            self.create_task(f"Utilisation {util:g}% below floor: pause non-critical requisitions and review bench", 7)
        self.log_event("people.activity.capacity_noted", f"utilisation {util:g}% gap {gap:g} FTE", utilisation_pct=util, gap_fte=gap)
        return []

    # ------------------------------------------------------------------ budgeting
    def _budget_year(self, body: dict) -> int:
        fy = body.get("fiscal_year") or body.get("year")
        if fy is None:
            cycle = str(body.get("budget_cycle_id") or body.get("cycle_id") or "")
            digits = "".join(ch for ch in cycle if ch.isdigit())
            fy = int(digits[-4:]) if len(digits) >= 4 else None
        fy = int(_num(fy, 0)) or (self.clock.date.year + (1 if self.clock.quarter == 4 else 0))
        return max(2026, min(2028, fy))

    def _on_budget_cycle_opened(self, message: Message, body: dict) -> list[Message]:
        fy = self._budget_year(body)
        env = BUDGET_ENVELOPE_GBPK[fy]
        cycle = body.get("budget_cycle_id") or f"BUD-{fy}"
        if cycle in self.state["budgets_submitted"]:
            return []
        self.state["budgets_submitted"][cycle] = fy
        idx = fy - 2026
        try:
            narrative = self.ask_llm(f"One sentence budget rationale for people department FY{fy}: people £{env['people']}k, non-people £{env['non_people']}k.")
        except Exception:
            narrative = ""
        self.create_task(f"Collect hiring plans from all department heads for {cycle}; reconcile to COMPANY.md headcount plan", 7)
        return [self.emit("people.budget_submitted", {
            "budget_cycle_id": cycle, "fiscal_year": fy, "department": "people",
            "amount_gbp": env["total"] * 1000, "people_cost_gbp": env["people"] * 1000, "non_people_cost_gbp": env["non_people"] * 1000,
            "headcount_year_end": HEADCOUNT_PLAN["people"][idx], "company_year_end_humans": sum(v[idx] for v in HEADCOUNT_PLAN.values()),
            "non_people_lines": ["recruiting platforms and agency fees", "learning and development", "HRIS and payroll bureau", "employee assistance and wellbeing", "employment law advice"],
            "summary": narrative or f"People FY{fy} budget £{env['total']}k",
        }, recipient="finance", delay_days=3)]

    def _on_budget_approved(self, message: Message, body: dict) -> list[Message]:
        fy = self._budget_year(body)
        self.state["approved_budget"][fy] = body
        env = BUDGET_ENVELOPE_GBPK[fy]
        self.create_task(f"Phase FY{fy} hiring plan, salary review and L&D spend inside approved envelope (£{env['total']}k people department)", 10)
        self.log_event("people.activity.budget_recorded", f"FY{fy} budget approved", fiscal_year=fy)
        return []

    # ------------------------------------------------------------------ executive direction
    def _on_crisis_declared(self, message: Message, body: dict) -> list[Message]:
        self.state["hiring_freeze"] = True
        self.state["freeze_reason"] = body.get("summary") or body.get("reason") or "crisis"
        frozen = 0
        for r in self.state["requisitions"].values():
            if r["status"] in ("pending_approval",):
                r["frozen"] = True
                frozen += 1
        self.create_task("Crisis: all-hands employee communication, line-manager briefing and wellbeing support (EAP)", 1, "critical")
        self.create_task("Crisis: hiring freeze; only CEO-approved exceptions proceed. Keep payroll and statutory obligations running", 1, "high")
        self.log_event("people.activity.hiring_freeze", f"freeze on; {frozen} requisitions held", frozen=frozen)
        return []

    def _on_okrs_set(self, message: Message, body: dict) -> list[Message]:
        self.state["okrs"] = body
        self.create_task("Cascade company OKRs into individual objectives; performance reviews to reference them", 30)
        self.log_event("people.activity.okrs_recorded", "company OKRs recorded", okrs=body.get("objectives") or body.get("summary"))
        return []

    def _on_strategy_updated(self, message: Message, body: dict) -> list[Message]:
        self.state["strategy"] = body
        self.create_task("Refresh workforce plan and skills map against updated strategy; flag consultation duties if roles at risk", 14)
        self.log_event("people.activity.strategy_recorded", "strategy update recorded")
        return []

    # ------------------------------------------------------------------ legal and compliance
    def _on_policy_update(self, message: Message, body: dict) -> list[Message]:
        pid = str(body.get("policy_id") or body.get("policy") or f"POL-{len(self.state['policies']) + 1:03d}")
        name = str(body.get("policy_name") or body.get("title") or pid)
        if pid in self.state["policies"] and self.state["policies"][pid].get("version") == body.get("version"):
            return []
        self.state["policies"][pid] = {"name": name, "version": body.get("version"), "day": self.clock.day}
        self.create_task(f"Update employee handbook for '{name}'; consult/notify employees if contractual terms change", 10)
        self.create_task(f"Roll out acknowledgement and refresher training for '{name}'", 7)
        population = sum(1 for e in self.state["employees"].values() if e["status"] == "active") or sum(HEADCOUNT_PLAN[d][self._year() - 1] for d in HEADCOUNT_PLAN)
        self.state["metrics"]["training_assigned"] += 1
        self.state["metrics"]["training_completed"] += 1
        return [self.emit("people.compliance_training_completed", {
            "scope": "policy_refresher", "policy_id": pid, "policy_name": name, "courses": [name],
            "population": population, "completed": int(population * 0.98), "completion_pct": 98.0,
            "completed_by_day": self.clock.day + 21, "stragglers_chased": True,
            "summary": f"Refresher on '{name}' completed by 98% of staff",
        }, delay_days=21)]

    def _on_regulatory_change(self, message: Message, body: dict) -> list[Message]:
        text = f"{body.get('summary', '')} {body.get('regulation', '')} {body.get('title', '')}".lower() + " "
        relevant = any(k in text for k in REGULATION_KEYWORDS) or body.get("affects_employment") is True
        self.state["regulatory_watch"].append({"day": self.clock.day, "relevant": relevant, "ref": body.get("regulation") or body.get("summary")})
        if not relevant and not body.get("training_required"):
            self.log_event("people.activity.regulatory_no_hr_impact", "no HR impact identified", body=body)
            return []
        self.create_task("HR impact assessment of regulatory change: contracts, handbook, right-to-work, payroll, AI-in-HR decision controls", 10, "high")
        if "automated decision" in text or "ai " in text:
            self.create_task("Re-validate human review gate on AI-assisted screening and performance analytics (UK GDPR Art. 22 / ICO guidance)", 14, "high")
        if body.get("training_required"):
            self.state["metrics"]["training_assigned"] += 1
            return [self.emit("people.compliance_training_completed", {
                "scope": "regulatory_change", "courses": [str(body.get("regulation") or "Regulatory update")],
                "population": sum(HEADCOUNT_PLAN[d][self._year() - 1] for d in HEADCOUNT_PLAN), "completion_pct": 97.0,
                "completed_by_day": self.clock.day + 30, "summary": "Regulatory change training completed",
            }, delay_days=30)]
        return []

    # ------------------------------------------------------------------ cadences
    def tick(self) -> list[Message]:
        out: list[Message] = []
        c = self.clock
        day = c.day
        # monthly payroll liaison: variations cut-off on the 18th, payday last working day.
        if c.date.day == 18:
            key = f"{c.date.year}-{c.date.month:02d}"
            if key not in self.state["payroll_months"]:
                self.state["payroll_months"].append(key)
                self.create_task(f"Payroll {key}: submit joiners, leavers, salary changes, statutory pay and pension to bureau by cut-off; CFO release", 2, "high")
        # quarterly pulse survey results at the start of Jan/Apr/Jul/Oct (after the first quarter of data).
        if c.is_month_start and c.date.month in (1, 4, 7, 10) and day > 0:
            qkey = f"{c.date.year}-Q{c.quarter}"
            if qkey not in self.state["pulse_quarters"]:
                self.state["pulse_quarters"].append(qkey)
                out.append(self._publish_pulse(qkey))
            if c.date.month == 7:
                self.create_task("Mid-year performance conversations: manager check-ins, development plans", 30)
            if c.date.month == 1:
                self.create_task("Year-end performance calibration done by humans; AI may only prepare evidence packs", 30)
        # time-to-hire breach and onboarding escalations.
        for r in self.state["requisitions"].values():
            if r["status"] in ("pending_approval", "approved", "posted") and not r["stale_flagged"] \
                    and day - r["opened_day"] > TIME_TO_HIRE_TARGET_DAYS:
                r["stale_flagged"] = True
                self.create_task(f"{r['id']} ({r['role']}) open {day - r['opened_day']} days vs {TIME_TO_HIRE_TARGET_DAYS} target: unblock", 3, "high")
        for e in self.state["employees"].values():
            if e["status"] == "pre_start" and not e["onboarded"] and day > e["start_day"] + ONBOARDING_ESCALATION_DAYS \
                    and f"onb-{e['id']}" not in self.state["escalated"]:
                self.state["escalated"].add(f"onb-{e['id']}")
                self.state["metrics"]["day_one_total"] += 0
                self.create_task(f"Onboarding blocked for {e['id']}: access={e['access']} workspace={e['workspace']}; chase IT and Operations", 1, "critical")
            if e["status"] == "active" and day >= e["probation_review_day"] and not e["probation_flagged"]:
                e["probation_flagged"] = True
                self.create_task(f"Probation review due for {e['id']} ({e['role']}): manager decision recorded by a human", 5)
        return out

    def _publish_pulse(self, qkey: str) -> Message:
        headcount = sum(HEADCOUNT_PLAN[d][self._year() - 1] for d in HEADCOUNT_PLAN)
        base = 76.0
        base -= 4.0 if self.state["hiring_freeze"] else 0.0
        base -= min(5.0, 1.0 * len(self.state["leavers"]))
        base += min(2.0, 0.5 * self.state["metrics"]["hires"])
        score = round(base, 1)
        self.state["metrics"]["engagement_score"] = score
        return self.emit("people.engagement_survey_completed", {
            "survey_id": f"PULSE-{qkey}", "quarter": qkey, "engagement_score": score, "enps": int(score - 40),
            "participation_pct": 88.0, "respondents": int(headcount * 0.88), "population": headcount,
            "themes": ["workload and utilisation", "career progression", "AI tooling and role clarity"],
            "action_owner": "Chief People Officer", "anonymity_threshold": 5,
            "attrition_risk_teams": ["delivery"] if score < 72 else [],
            "summary": f"Pulse {qkey}: engagement {score}",
        })

    # ------------------------------------------------------------------ KPI view
    def kpi_snapshot(self) -> list[Kpi]:
        m = self.state["metrics"]
        samples = m["time_to_hire_samples"]
        actual = {
            "time_to_hire_days": round(sum(samples) / len(samples), 1) if samples else None,
            "offer_acceptance_rate_pct": _pct(m["offers_accepted"], m["offers_made"]),
            "annualised_attrition_pct": _pct(m["voluntary_leavers"] * 365.0 / max(self.clock.day, 30),
                                             sum(HEADCOUNT_PLAN[d][self._year() - 1] for d in HEADCOUNT_PLAN)),
            "engagement_score": m["engagement_score"],
            "compliance_training_completion_pct": _pct(m["training_completed"], m["training_assigned"]),
            "day_one_readiness_pct": _pct(m["day_one_ready"], m["day_one_total"]),
            "cost_per_hire_gbp": round(m["recruiting_cost_gbp"] / m["hires"], 0) if m["hires"] else None,
            "leaver_access_revoked_24h_pct": _pct(m["access_revoked_24h"], m["access_revoked_total"]),
            "right_to_work_before_start_pct": _pct(m["rtw_before_start"], m["rtw_total"]),
            "ai_hr_decisions_human_reviewed_pct": _pct(m["ai_decisions_reviewed"], m["ai_decisions"]),
        }
        return [replace(k, actual=actual.get(k.name)) for k in KPIS]


def build_agent(llm, bus, clock, log) -> PeopleAgent:
    role = Role("Chief People Officer", "people", "head", (1, 1, 1), (140000, 200000), "Chief Executive Officer")
    return PeopleAgent("people", "people", role, llm, bus, clock, log)
