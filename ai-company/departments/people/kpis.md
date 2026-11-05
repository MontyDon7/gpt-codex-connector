# People KPIs

> Department: `people` (HR: recruiting, onboarding, offboarding, payroll liaison, performance, culture, UK employment basics, human oversight of AI in HR decisions). Agent class: `PeopleAgent`. Head: Chief People Officer, Grace Adeyemi (COMPANY.md §9.2). All figures are modeled assumptions, not real data. Targets are consistent with COMPANY.md §5, §6 and §8.

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| time_to_hire_days | Time to hire (requisition opened to offer accepted) | days | 45 | 42 | 40 | lower is better | weekly | Talent Acquisition Partner (FY2026: CPO) |
| offer_acceptance_rate | Offer acceptance rate | percent | 80 | 82 | 85 | higher is better | monthly | Talent Acquisition Partner (FY2026: CPO) |
| attrition_rate_annualised | Voluntary and involuntary attrition (humans, trailing 12 months) | percent | 14 | 12.5 | 11 | lower is better | monthly | Chief People Officer |
| regretted_attrition_rate | Regretted attrition (rated 'strong' or above at last review) | percent | 6 | 5 | 4 | lower is better | monthly | Chief People Officer |
| cost_per_hire_gbp | Recruiting cost per hire (non-salary) | GBP | 2000 | 2200 | 4500 | lower is better | quarterly | People Operations Specialist (FY2026: CPO) |
| onboarding_completion_rate | New-hire onboarding checklist completed by day 30 | percent | 95 | 96 | 97 | higher is better | monthly | People Operations Specialist (FY2026: CPO) |
| day_one_readiness_rate | New hires with laptop, accounts and payroll set up on day 1 | percent | 95 | 97 | 98 | higher is better | per cohort | People Operations Specialist (FY2026: CPO) |
| engagement_score | Engagement survey index (eNPS-style composite, 0 to 100) | score | 72 | 74 | 76 | higher is better | quarterly | Chief People Officer |
| compliance_training_completion | Mandatory compliance training completed on time | percent | 98 | 98 | 99 | higher is better | monthly | People Operations Specialist (FY2026: CPO) |
| performance_review_completion | Performance reviews completed in cycle window | percent | 100 | 100 | 100 | higher is better | per cycle (half-yearly) | Chief People Officer |
| payroll_accuracy_rate | Payroll runs right-first-time (no post-run correction) | percent | 99.5 | 99.7 | 99.8 | higher is better | monthly | People Operations Specialist (FY2026: CPO) |
| human_oversight_coverage | AI-assisted HR decisions with recorded human decision-maker | percent | 100 | 100 | 100 | higher is better | monthly | Chief People Officer |
| diverse_shortlist_rate | Shortlists meeting the agreed diversity-of-slate standard | percent | 70 | 80 | 85 | higher is better | quarterly | Talent Acquisition Partner (FY2026: CPO) |
| hiring_plan_attainment | Hires started vs approved headcount plan (year-end humans) | percent | 100 | 100 | 100 | higher is better | monthly | Chief People Officer |
| people_cost_per_head_gbp | Average loaded people cost per average FTE | GBP | 138000 | 122000 | 120000 | lower is better | quarterly | Chief People Officer with Finance |

Owner role titles follow the department blueprint (`blueprint.md`); in FY2026 the department has 2 humans and 1 AI agent (COMPANY.md §6.1), so the CPO is the accountable owner wherever a delegate is not yet in post. Eight of these (time_to_hire_days, offer_acceptance_rate, attrition_rate_annualised, cost_per_hire_gbp, onboarding_completion_rate, engagement_score, compliance_training_completion, human_oversight_coverage) are exposed in `agent.py` as `KPIS` at FY2026 targets (see section 2, Agent `KPIS` mapping).

## 2. Definitions and formulas

Conventions: "humans" means employees and fixed-term staff on payroll, excluding contractors and AI agents. Business days are UK working days. Sim time is an integer `clock.day`; one sim day equals one calendar day for time-to-hire, and Day 0 is Monday 2026-01-05 (COMPANY.md §1).

### 2.1 `time_to_hire_days`
- **Formula:** mean over hires in the period of (day of `people.offer_accepted` minus day of `people.requisition_opened`). Period = trailing 90 days; median reported alongside the mean.
- **Targets:** 45 / 42 / 40 days. FY2026 equals the company assumption of 45 days (human) (COMPANY.md §8, item 3). Improvement comes from an in-house talent function and the screening agent.
- **Notes:** agent provisioning (5 days, COMPANY.md §8) is tracked separately as `agent_provisioning_days` (internal metric, not a headline KPI). Notice periods are excluded; the clock stops at acceptance, not start date.
- **Agent mapping:** `Kpi("time_to_hire_days", "days", 45.0, None, higher_is_better=False)`.

### 2.2 `offer_acceptance_rate`
- **Formula:** offers accepted / offers extended, in the period x 100. Offers withdrawn by Lumenhall are excluded from the denominator; counter-offers that end in a revised accepted offer count as accepted.
- **Targets:** 80 / 82 / 85 percent. Consultant-and-above roles typically sit around 80 to 85 percent in the UK market, hence the narrow range.
- **Agent mapping:** `Kpi("offer_acceptance_rate", "percent", 80.0, None)`.

### 2.3 `attrition_rate_annualised`
- **Formula:** (leavers in trailing 12 months / average humans over the same 12 months) x 100. Includes voluntary and involuntary leavers; excludes end of fixed-term contracts and contractor releases.
- **Targets:** 14 / 12.5 / 11 percent. FY2026 and FY2028 are the company assumptions (14% in Y1 to 11% in Y3, COMPANY.md §8, item 3); FY2027 is the linear midpoint.
- **Derived volume:** average humans 29 / 74 / 170 (COMPANY.md §6) gives about 4 / 9 / 19 expected leavers a year, which sizes backfill demand in section 4.
- **Agent mapping:** `Kpi("attrition_rate_annualised", "percent", 14.0, None, higher_is_better=False)`. Updated on each `people.employee_left`.

### 2.4 `regretted_attrition_rate`
- **Formula:** (leavers whose last review rating was 'strong' or 'exceptional' in trailing 12 months / average humans) x 100. Subset of 2.3.
- **Targets:** 6 / 5 / 4 percent (roughly 40 percent of total attrition in Y1 falling to about 36 percent in Y3 as performance management matures).
- **Control:** exit-interview themes reviewed quarterly with the executive team; any regretted leaver from `delivery` triggers a staffing check against `delivery.capacity_forecast_updated`.

### 2.5 `cost_per_hire_gbp`
- **Formula:** (agency fees + job boards and advertising + assessment tools + ATS licence share + referral bonuses + relocation) / hires started in the period. Excludes salary, internal People team cost and onboarding equipment (that is IT cost).
- **Targets:** £2,000 / £2,200 / £4,500. Derivation is in `economics.md`; in outline, the recruiting-related share of the `people` non-people budget (COMPANY.md §5.4: £100k / £300k / £1,100k) is about 60% / 55% / 45% (the remainder is HRIS and payroll bureau, learning and development, wellbeing, employment-law advice and, from FY2027, US set-up), divided by modeled hires of about 30 / 81 / 139 (section 4). FY2028 rises because of US hiring (relocation, immigration support, higher agency use).
- **Agent mapping:** `Kpi("cost_per_hire_gbp", "GBP", 2000.0, None, higher_is_better=False)`.

### 2.6 `onboarding_completion_rate`
- **Formula:** new hires with 100% of mandatory onboarding checklist items (contract signed, right-to-work check evidenced, payroll and pension enrolment, policies acknowledged, security induction, 30-day check-in held) done by day 30 / new hires reaching day 30 in the period x 100.
- **Targets:** 95 / 96 / 97 percent.
- **Right-to-work:** a missing or expired right-to-work check is an automatic fail for that hire regardless of other items and is reported as a compliance incident (UK civil penalty exposure up to £60,000 per illegal worker for a first breach).

### 2.7 `day_one_readiness_rate`
- **Formula:** hires where `it_security.access_provisioned` and `operations.workspace_ready` were both received on or before the start day (sim day of `people.new_hire_started`) / hires started in the period x 100.
- **Targets:** 95 / 97 / 98 percent.
- **Notes:** `people.requisition_opened` to start is long enough (45 days plus notice) that failure here is a process failure, not a capacity one. Late provisioning is attributed to the owning department in the monthly report.

### 2.8 `engagement_score`
- **Formula:** mean of five items (would recommend Lumenhall as a place to work, manager support, growth opportunity, workload sustainability, trust in leadership), each scored 0 to 100 from a 5-point scale; response rate must be at least 80% or the result is flagged as low-confidence. Reported from `people.engagement_survey_completed`.
- **Targets:** 72 / 74 / 76. Typical UK professional-services pulse scores are in the low-to-mid 70s; consultancy workload pressure is the main modeled risk.
- **Agent mapping:** `Kpi("engagement_score", "score", 72.0, None)`.
- **Privacy:** results shown only for groups of 5 or more respondents (UK GDPR data minimisation, COMPANY.md §8 item 7).

### 2.9 `compliance_training_completion`
- **Formula:** mandatory modules completed by due date / modules assigned and due in the period x 100. Modules: UK GDPR and data protection, information security and Cyber Essentials Plus awareness, anti-bribery and Modern Slavery Act, equality and harassment prevention (including the Employment Rights Act-era duties to take reasonable steps against sexual harassment), AI use and AI-governance policy, health and safety (DSE).
- **Targets:** 98 / 98 / 99 percent. Source topic: `people.compliance_training_completed`.
- **Agent mapping:** `Kpi("compliance_training_completion", "percent", 98.0, None)`.
- **Control:** overdue at 14 days escalates to line manager; at 30 days to department head; access reviews by `it_security` may be affected for persistent non-completion.

### 2.10 `performance_review_completion`
- **Formula:** reviews signed off by manager and employee within the cycle window / reviews due x 100. Cycles are half-yearly (mid-year check-in in July, annual review in January); probation reviews at 3 and 6 months count in the period they fall due.
- **Targets:** 100 / 100 / 100 percent. Zero tolerance because ratings feed promotion, bonus and capability decisions; any gap is a data-quality risk for fair-treatment claims.

### 2.11 `payroll_accuracy_rate`
- **Formula:** monthly payroll runs with zero post-submission corrections (underpayments, overpayments, wrong tax code, missed starter or leaver) / payroll runs x 100 for runs; also tracked at line level as errors per 1,000 payslips. The headline uses the line-level rate: 1 minus (payslips needing correction / payslips issued) x 100.
- **Targets:** 99.5 / 99.7 / 99.8 percent. At 29 average humans in FY2026 one error in a month is about 3.4 percent of payslips, so the target is pragmatically "no more than one correction a quarter".
- **Controls:** two-person review before submission to the payroll bureau, HMRC RTI submission on or before the pay date, starter and leaver data from People systems (not re-keyed), reconciliation to the Finance ledger (see `finance` close process).

### 2.12 `human_oversight_coverage`
- **Formula:** HR decisions where an AI agent produced a score, ranking, shortlist, flag or recommendation and a named human recorded the decision, with rationale, before any candidate or employee was notified / total AI-assisted HR decisions x 100.
- **Targets:** 100 / 100 / 100 percent. Aligned with the agent governance rule that agents may draft, analyse, monitor and propose but may not make final hiring or termination decisions (COMPANY.md §9.4), with UK GDPR Article 22 (no solely automated decisions with legal or similarly significant effect) and the UK AI regulatory principles (COMPANY.md §8 item 7).
- **Evidence:** decision log entry containing decision id, decision-maker, agent output reference, override flag. Override rate (human decision differs from agent recommendation) is monitored as a companion metric; a rate persistently below 2% triggers a rubber-stamping review.
- **Breach handling:** any decision executed without a recorded human is a severity `high` incident reported to the CPO and General Counsel within 1 business day.

### 2.13 `diverse_shortlist_rate`
- **Formula:** closed requisitions whose final-stage shortlist met the agreed slate standard (at least 2 candidates from under-represented groups where the applicant pool allowed, assessed on voluntarily provided, anonymised monitoring data) / closed requisitions with a shortlist x 100.
- **Targets:** 70 / 80 / 85 percent. Lower in Y1 because small volumes and niche AI-engineering pools limit the slate; rises with sourcing partnerships and structured interviews.
- **Control:** monitoring data held separately from hiring-panel view (Equality Act 2010 compliance; no positive discrimination in selection). Audit of screening-agent pass-through rates by group at least quarterly for adverse-impact patterns (four-fifths rule used as a trigger for review, not as a legal test).

### 2.14 `hiring_plan_attainment`
- **Formula:** humans at period end / planned year-end-humans pro-rated by month x 100, against the approved plan. Year-end plan: people department humans 2 / 5 / 10 within company 38 / 110 / 230 (COMPANY.md §6, §6.1).
- **Targets:** 100 / 100 / 100 percent, with a tolerance band of 95 to 105 percent before escalation; hiring above plan needs CEO approval via `executive.headcount_approved` (COMPANY.md §9.3).
- **Notes:** department-level attainment is reported for all 12 departments; `people` owns the company view.

### 2.15 `people_cost_per_head_gbp`
- **Formula:** (total salary + employer on-costs of all humans in the year) / average humans. Loaded cost = base x 1.28 (COMPANY.md §8 item 5).
- **Targets:** £138,000 / £122,000 / £120,000 per FTE, copied from the company people-cost build (COMPANY.md §5.2: 29 x £138k, 74 x £122k, 170 x £120k). The decline reflects the shift in mix toward more junior delivery staff.
- **Notes:** this is a company-level KPI reported by `people` and reconciled by `finance`; it is not a departmental spend measure.

### Agent `KPIS` mapping (FY2026 targets)

These 8 KPIs from section 1 are exposed in `agent.py`:

```python
KPIS = [
    Kpi("time_to_hire_days", "days", 45.0, None, higher_is_better=False),
    Kpi("offer_acceptance_rate", "percent", 80.0, None),
    Kpi("attrition_rate_annualised", "percent", 14.0, None, higher_is_better=False),
    Kpi("cost_per_hire_gbp", "GBP", 2000.0, None, higher_is_better=False),
    Kpi("onboarding_completion_rate", "percent", 95.0, None),
    Kpi("engagement_score", "score", 72.0, None),
    Kpi("compliance_training_completion", "percent", 98.0, None),
    Kpi("human_oversight_coverage", "percent", 100.0, None),
]
```

The remaining KPIs are reported in the monthly pack but may be left out of `KPIS` if the agent does not have the source events to compute them.

### Objectives and key results (OKRs)

OKRs are set each January from `executive.okrs_set` and reviewed quarterly. FY2026 department OKRs:

| Objective | Key results |
|---|---|
| O1. Hire the FY2026 plan without lowering the bar | KR1: 38 humans in post company-wide by 2026-12-31 (hiring_plan_attainment 100%). KR2: time_to_hire_days at or below 45. KR3: offer_acceptance_rate at or above 80%. |
| O2. Make day one work | KR1: day_one_readiness_rate at or above 95%. KR2: onboarding_completion_rate at or above 95%. KR3: zero right-to-work check failures. |
| O3. Keep the people we hire | KR1: attrition at or below 14%. KR2: engagement_score at or above 72. KR3: regretted attrition at or below 6%. |
| O4. Be a compliant, well-governed employer | KR1: compliance_training_completion at or above 98%. KR2: human_oversight_coverage 100% with zero unrecorded AI-assisted decisions. KR3: payroll_accuracy_rate at or above 99.5%. |

## 3. Reporting cadence and data sources

| KPI id | Source system or event | Computed by | Reviewed in |
|---|---|---|---|
| time_to_hire_days | ATS requisition and offer timestamps; `people.requisition_opened`, `people.offer_accepted` | PeopleAgent | Weekly People stand-up; monthly executive pack |
| offer_acceptance_rate | ATS offer records; `people.offer_accepted` vs offers extended | PeopleAgent | Monthly |
| attrition_rate_annualised | HRIS leaver records; `people.employee_left` | PeopleAgent, verified by Chief People Officer | Monthly executive pack; quarterly board pack |
| regretted_attrition_rate | HRIS leavers joined to performance ratings | Chief People Officer (human) | Monthly |
| cost_per_hire_gbp | Finance ledger (recruiting cost centre) and ATS hires | People Operations Specialist with `finance` | Quarterly; budget cycle (`finance.budget_cycle_opened`) |
| onboarding_completion_rate | HRIS onboarding checklist; `people.new_hire_started` plus day-30 check | PeopleAgent | Monthly |
| day_one_readiness_rate | `it_security.access_provisioned`, `operations.workspace_ready` vs start day | PeopleAgent | Per cohort; monthly |
| engagement_score | Survey tool export; `people.engagement_survey_completed` | PeopleAgent, reviewed by CPO | Quarterly pulse; annual full survey; board people update |
| compliance_training_completion | Learning platform export; `people.compliance_training_completed` | PeopleAgent | Monthly; also reported to `legal` and `it_security` |
| performance_review_completion | HRIS review module | Chief People Officer | Each cycle close; board people update |
| payroll_accuracy_rate | Payroll bureau variance report; HMRC RTI acknowledgements; Finance reconciliation | People Operations Specialist | Monthly after payroll close |
| human_oversight_coverage | HR decision log (decision id, agent output reference, decision-maker) | PeopleAgent produces, CPO attests | Monthly; quarterly sample audit by `legal` and `data` |
| diverse_shortlist_rate | ATS shortlist plus anonymised monitoring data | Talent Acquisition Partner | Quarterly |
| hiring_plan_attainment | HRIS headcount vs `executive.headcount_approved` and plan (COMPANY.md §6.1) | PeopleAgent | Monthly executive pack |
| people_cost_per_head_gbp | Payroll totals and on-cost schedule; reconciled with Finance | Chief People Officer with `finance` | Quarterly |

Cadence summary:

- **Weekly:** People stand-up covering open requisitions, pipeline, time to hire, upcoming starters, leavers in notice, open employee-relations cases (counts only, no case detail in the pack).
- **Monthly:** People KPI pack to the executive team (all KPIs above); payroll close sign-off; compliance training and right-to-work exception list.
- **Quarterly:** engagement pulse; cost per hire and people cost review with `finance`; AI-in-HR oversight audit (sample of decisions tested against the log); OKR review.
- **Half-yearly:** performance review cycle (July and January).
- **Annually:** budget cycle input (`people.budget_submitted`), full engagement survey, salary band review against COMPANY.md §6.2, gender and ethnicity pay gap analysis (statutory UK gender pay gap reporting applies once headcount reaches 250; the company plans to publish voluntarily from FY2028, when year-end humans reach 230).

Data handling: personal data in KPI sources is processed under UK GDPR and the Data Protection Act 2018 with role-based access; the KPI pack contains aggregates only and suppresses any group of fewer than 5 people.

Thresholds that trigger escalation (red status):

| KPI id | Amber | Red |
|---|---|---|
| time_to_hire_days | above target by 10% | above target by 25% |
| offer_acceptance_rate | 5 points below target | 10 points below target |
| attrition_rate_annualised | 2 points above target | 4 points above target |
| onboarding_completion_rate | 3 points below target | 6 points below target |
| engagement_score | 3 points below target | 6 points below target |
| compliance_training_completion | 2 points below target | 5 points below target |
| human_oversight_coverage | any value below 100% | any unrecorded decision with candidate or employee impact |
| payroll_accuracy_rate | 0.3 points below target | any missed pay date or HMRC RTI late filing |

## 4. Links to company targets

| People KPI | Rolls up to | Link |
|---|---|---|
| hiring_plan_attainment, time_to_hire_days | Headcount plan: humans 38 / 110 / 230 and agents 22 / 70 / 150 (COMPANY.md §6); department rows 2 / 5 / 10 humans and 1 / 3 / 6 agents (COMPANY.md §6.1) | Revenue targets of £6.0m / £19.5m / £46.2m (COMPANY.md §5.1) depend on delivery capacity arriving on time; a slipped hire cohort is a direct revenue risk. |
| attrition_rate_annualised, regretted_attrition_rate | Attrition assumption 14% (Y1) to 11% (Y3) and time-to-hire 45 days (COMPANY.md §8 item 3) | Backfills add to hiring volume; every point of attrition above plan costs roughly one extra hire per 100 heads and lowers utilisation (70% blended assumption, COMPANY.md §8 item 3). |
| people_cost_per_head_gbp | People cost in the cost sanity check: 29 x £138k, 74 x £122k, 170 x £120k (COMPANY.md §5.2) and loaded cost = base x 1.28 (COMPANY.md §8 item 5; salary bands COMPANY.md §6.2) | Feeds gross margin 48% / 58% / 64% through delivery and customer_success payroll (COMPANY.md §5.1). |
| cost_per_hire_gbp | `people` department budget envelope: non-people £100k / £300k / £1,100k, total £310k / £700k / £1,850k (COMPANY.md §5.4) | Recruiting spend must stay inside the non-people envelope; non-budgeted spend above £50k needs CFO approval (COMPANY.md §9.3). |
| compliance_training_completion, onboarding_completion_rate | Compliance baseline: UK GDPR and DPA 2018, ISO 27001, Cyber Essentials Plus (FY2026), SOC 2 Type II (FY2027) (COMPANY.md §8 item 7) | Training and induction records are audit evidence for ISO 27001 and SOC 2; ISO 27001 certification by end FY2026 gates the US launch (COMPANY.md §8 item 6). |
| human_oversight_coverage | AI agent governance: agents may not make final hiring or termination decisions (COMPANY.md §9.4); alignment with UK AI regulatory principles and EU AI Act (COMPANY.md §8 item 7) | Demonstrates to clients that Lumenhall applies to itself the oversight standards it advises on; relevant to Keep and Forge credibility (COMPANY.md §3). |
| engagement_score, regretted_attrition_rate, performance_review_completion | Utilisation 70% blended and delivery quality (COMPANY.md §8 item 3, §4); logo retention of 83% / 85% (COMPANY.md §5.1) | Senior consultant continuity drives client retention and net revenue retention of 115% / 118% (COMPANY.md §5.1). |
| payroll_accuracy_rate | Operating expense control (COMPANY.md §5.2) and statutory HMRC and Companies House obligations (COMPANY.md §8 item 7) | Payroll errors create employee-trust and penalty risk disproportionate to cost. |
| diverse_shortlist_rate | Board-level people governance (COMPANY.md §9.1) and hiring bar for senior hires | Reported to the board in the annual people update. |

Derived hiring volumes used for the above (assumptions, shown in `economics.md`): FY2026 about 30 hires assuming an opening headcount of about 12 at 2026-01-05 (net +26 to reach 38, plus about 4 backfills from 14% attrition on 29 average humans); FY2027 about 81 (net +72, plus about 9 backfills at 12.5% of 74); FY2028 about 139 (net +120, plus about 19 backfills at 11% of 170). Of these, the `people` department's own hires (2 / 5 / 10 humans) are a small share; most volume is `delivery` (14 / 46 / 104 humans, COMPANY.md §6.1).
