"""People department scenarios (Lumenhall Partners).

Each ``scenario_*`` function only builds Messages with ``bus.make_message``; the caller seeds them with
``Company.seed``. Bands follow COMPANY.md section 6.2, headcount and budget follow sections 5.4 and 6.1,
governance follows section 9.3 (new headcount outside budget needs the CEO) and section 9.4 (AI agents may
shortlist and draft but never make final hiring or termination decisions). Names are fictional.
"""

from __future__ import annotations

from core import Message, MessageBus, SimClock

# COMPANY.md §6.2 base salary bands in GBP (London).
_BANDS_GBP = {
    "analyst": (38_000, 48_000), "consultant": (55_000, 70_000),
    "senior_consultant": (72_000, 90_000), "manager": (92_000, 115_000),
    "principal": (120_000, 155_000),
}
# COMPANY.md §5.4 people department budget, FY2026 / FY2027 / FY2028 in GBP.
_PEOPLE_BUDGET_GBP = {"FY2026": 310_000, "FY2027": 700_000, "FY2028": 1_850_000}
_LOADING = 1.28  # COMPANY.md §5.4: loaded cost = base x 1.28.


def scenario_hire_to_start(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A delivery manager asks for a Senior Consultant; applicants arrive after the job goes live.

    Expected chain: delivery.hire_requested -> people.requisition_opened (executive, finance) ->
    executive.headcount_approved -> people.job_posted (marketing); external.candidate_applied (x3, AI
    shortlist, human decision) -> people.offer_accepted (finance, legal) -> people.new_hire_started
    (it_security, operations, finance, delivery) -> it_security.access_provisioned and
    operations.workspace_ready.
    """
    d = clock.day
    req = params.get("requisition_id", "REQ-2026-014")
    level = params.get("level", "senior_consultant")
    lo, hi = _BANDS_GBP[level]
    title = params.get("title", "Senior Consultant, Forge")
    msgs = [
        bus.make_message("delivery", "people", "delivery.hire_requested", {
            "requisition_id": req, "title": title, "level": level, "count": 1,
            "salary_band_gbp": [lo, hi], "start_by_day": d + 75, "reason": "Forge Build pipeline coverage",
            "budgeted": True, "summary": f"Delivery requests 1 x {title} ({level}, GBP {lo:,} to {hi:,})",
        }, sim_time=d),
        bus.make_message("executive", "people", "executive.headcount_approved", {
            "requisition_id": req, "title": title, "level": level, "count": 1,
            "approved_by": "Imogen Hartley", "budget_line": "FY2026 headcount plan",
            "summary": f"CEO approves {req} within the approved FY2026 plan",
        }, sim_time=d + 4),
    ]
    candidates = [("CAND-0101", "Priya Raman", 0.86), ("CAND-0102", "Tom Albright", 0.74),
                  ("CAND-0103", "Chiamaka Obi", 0.69)]
    for i, (cid, name, score) in enumerate(candidates):
        msgs.append(bus.make_message("external", "people", "external.candidate_applied", {
            "candidate_id": cid, "name": name, "requisition_id": req, "title": title,
            "source": ["LinkedIn", "referral", "careers page"][i], "screening_score": score,
            "right_to_work": "to_verify", "summary": f"{name} applies for {req}",
        }, sim_time=d + 12 + 2 * i))
    return msgs


def scenario_new_hire_onboarding(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Day one for a hired consultant: IT access and workspace confirmations return to People.

    Expected chain: it_security.access_provisioned and operations.workspace_ready -> people onboarding
    checklist (UK right-to-work check, contract signed, probation set) and mandatory training (GDPR,
    information security, AI use policy) -> people.compliance_training_completed (legal, it_security); a
    30-day new-hire engagement pulse (people.engagement_survey_completed, executive) follows.
    """
    d = clock.day
    emp = params.get("employee_id", "EMP-0042")
    name = params.get("name", "Priya Raman")
    return [
        bus.make_message("it_security", "people", "it_security.access_provisioned", {
            "employee_id": emp, "name": name, "systems": ["email", "sso", "engagement_workspace", "hris"],
            "mfa_enrolled": True, "device_id": "LH-LT-0213", "summary": f"Access provisioned for {name}",
        }, sim_time=d),
        bus.make_message("operations", "people", "operations.workspace_ready", {
            "employee_id": emp, "name": name, "location": "London HQ, desk 4.17",
            "equipment": "laptop, monitor",
            "summary": f"Workspace and equipment ready for {name}",
        }, sim_time=d),
        bus.make_message("people", "executive", "people.engagement_survey_completed", {
            "survey_id": "PULSE-NEWHIRE-30D", "scope": "new_hires_30_day", "response_rate_pct": 92,
            "enps": 38, "summary": "30-day new-hire pulse closed",
        }, sim_time=d + 32),
    ]


def scenario_leaver_offboarding(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A consultant resigns; People runs the exit and confirms access revocation.

    Expected chain: people.employee_left (it_security, operations, finance, legal) ->
    it_security.access_revoked (people, legal) -> final pay and holiday-pay liaison with payroll, P45,
    exit interview and knowledge-transfer tasks.
    """
    d = clock.day
    emp = params.get("employee_id", "EMP-0019")
    last_day = d + params.get("notice_days", 30)
    return [
        bus.make_message("people", "it_security", "people.employee_left", {
            "employee_id": emp, "name": params.get("name", "Marcus Whitfield"),
            "title": "Consultant, Compass", "department": "delivery", "last_working_day": last_day,
            "reason": "resignation", "notice_weeks": 4, "regretted": True,
            "summary": "Resignation accepted; 4 weeks notice, handover plan agreed with engagement lead",
        }, sim_time=d),
        bus.make_message("it_security", "people", "it_security.access_revoked", {
            "employee_id": emp, "systems_revoked": ["email", "sso", "engagement_workspace", "hris"],
            "devices_recovered": True, "summary": f"All access revoked for {emp} at end of last working day",
        }, sim_time=last_day),
    ]


def scenario_budget_and_okr_cycle(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Annual planning: Finance opens the cycle, Executive sets OKRs and approves budgets.

    Expected chain: finance.budget_cycle_opened -> people.budget_submitted (finance);
    executive.okrs_set and executive.strategy_updated -> people KPI and plan refresh;
    executive.budget_approved -> people hire_requested for the approved Y2 roles (executive).
    People budget per COMPANY.md section 5.4: GBP 310k / 700k / 1,850k.
    """
    d = clock.day
    fy = params.get("fiscal_year", "FY2027")
    budget = _PEOPLE_BUDGET_GBP.get(fy, 700_000)
    return [
        bus.make_message("finance", "people", "finance.budget_cycle_opened", {
            "fiscal_year": fy, "submission_due_day": d + 14, "template": "dept_budget_v3",
            "summary": f"{fy} budget cycle opened; submissions due in 14 days",
        }, sim_time=d),
        bus.make_message("executive", "people", "executive.strategy_updated", {
            "version": "2026-H2", "priorities": ["grow Forge", "scale Keep", "AI governance"],
            "summary": "Strategy refreshed for the next planning horizon",
        }, sim_time=d + 3),
        bus.make_message("executive", "people", "executive.okrs_set", {
            "fiscal_year": fy, "objectives": ["Hire and retain delivery talent", "Embed AI governance"],
            "summary": f"{fy} company OKRs set",
        }, sim_time=d + 5),
        bus.make_message("executive", "people", "executive.budget_approved", {
            "fiscal_year": fy, "department": "people", "approved_total_gbp": budget,
            "summary": f"People budget of GBP {budget:,} approved for {fy}",
        }, sim_time=d + 24),
    ]


def scenario_regulatory_and_policy_change(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Employment-law change flows from Legal into policy updates and refreshed staff training.

    Expected chain: external.regulation_published is handled by legal; legal.regulatory_change_noted and
    legal.policy_update_published reach people -> handbook and contract-template review, line-manager
    briefing, people.compliance_training_completed (legal, it_security) after the refresher.
    """
    d = clock.day
    return [
        bus.make_message("legal", "people", "legal.regulatory_change_noted", {
            "regulation_id": params.get("regulation_id", "REG-UK-EMP-2026-03"),
            "title": "Employment Rights Act 2025 phased measures: day-one flexible working and "
                     "strengthened family-leave rights",
            "jurisdiction": "UK", "effective_day": d + 90, "severity": "medium",
            "affected": ["people", "operations"],
            "summary": "Employment-law change noted for HR policy review",
        }, sim_time=d),
        bus.make_message("legal", "people", "legal.policy_update_published", {
            "policy_id": "POL-HR-007", "title": "Flexible Working and Family Leave Policy v3",
            "version": "3.0", "effective_day": d + 60, "training_required": True,
            "summary": "Updated flexible working and family leave policy published",
        }, sim_time=d + 20),
    ]


def scenario_delivery_surge_hiring(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """Delivery signals a capacity shortfall; People weighs contractors against permanent hires.

    Expected chain: delivery.capacity_forecast_updated and delivery.staffing_requested ->
    people.contractor_engaged (legal, it_security, finance; IR35 status determination) and
    people.requisition_opened for permanent roles (executive, finance). Several Forge Build engagements
    start together at Calder Freight Group and two further fictional clients.
    """
    d = clock.day
    gap = params.get("gap_fte", 6)
    return [
        bus.make_message("delivery", "people", "delivery.capacity_forecast_updated", {
            "horizon_weeks": 12, "demand_fte": 38, "supply_fte": 38 - gap, "gap_fte": gap,
            "utilisation_pct": 84, "skills_short": ["ML engineer", "senior consultant"],
            "summary": f"12-week capacity gap of {gap} FTE across Forge squads",
        }, sim_time=d),
        bus.make_message("delivery", "people", "delivery.staffing_requested", {
            "engagement_id": params.get("engagement_id", "EN-0001"), "client_name": "Calder Freight Group",
            "tier": "forge_build", "roles": [{"title": "ML engineer", "level": "consultant", "count": 2},
                                            {"title": "Engagement manager", "level": "manager", "count": 1}],
            "start_day": d + 21, "summary": "Staffing request for Forge Build squad at Calder Freight Group",
        }, sim_time=d + 1),
        bus.make_message("delivery", "people", "delivery.hire_requested", {
            "requisition_id": "REQ-2026-021", "title": "ML Engineer", "level": "consultant", "count": 2,
            "salary_band_gbp": list(_BANDS_GBP["consultant"]), "budgeted": False,
            "reason": "Sustained Forge demand; contractors bridge to permanent hire",
            "summary": "Two additional ML engineers outside approved plan, CEO approval needed",
        }, sim_time=d + 2),
    ]


def scenario_crisis_response_people(bus: MessageBus, clock: SimClock, **params) -> list[Message]:
    """A crisis is declared; People protects staff welfare, hiring pace and engagement.

    Expected chain: executive.crisis_declared -> hiring freeze review, wellbeing and comms plan, manager
    briefings; a pulse survey follows and people.engagement_survey_completed reaches executive and
    delivery.
    """
    d = clock.day
    return [
        bus.make_message("executive", "people", "executive.crisis_declared", {
            "crisis_id": params.get("crisis_id", "CR-2026-02"), "kind": "client_loss_and_cost_pressure",
            "severity": "high", "summary": "Loss of a major client; cost-control measures under review",
            "actions": ["freeze non-critical hiring", "protect delivery capacity"],
        }, sim_time=d),
        bus.make_message("people", "executive", "people.engagement_survey_completed", {
            "survey_id": "PULSE-CRISIS-01", "scope": "all_staff", "response_rate_pct": 88, "enps": 21,
            "top_themes": ["job security", "workload", "communication"],
            "summary": "Crisis pulse survey closed; eNPS down 17 points on last quarter",
        }, sim_time=d + 10),
    ]


SCENARIOS = {
    "hire_to_start": scenario_hire_to_start,
    "new_hire_onboarding": scenario_new_hire_onboarding,
    "leaver_offboarding": scenario_leaver_offboarding,
    "budget_and_okr_cycle": scenario_budget_and_okr_cycle,
    "regulatory_and_policy_change": scenario_regulatory_and_policy_change,
    "delivery_surge_hiring": scenario_delivery_surge_hiring,
    "crisis_response_people": scenario_crisis_response_people,
}
