# People Standard Operating Procedures

These SOPs govern the People department (HR: recruiting, onboarding, offboarding, payroll liaison, performance, culture, UK employment basics and human oversight of AI in HR decisions) at Lumenhall Partners. The department is two humans and one AI agent in FY2026 (COMPANY.md §6.1), led by the Chief Peopleesof Officer Grace Adeyemi (COMPANY.md §9.2); the agent is `PeopleAgent`, accountable to the Chief People Officer. Prices, bands and targets are cited from COMPANY.md; time-to-hire is 45 days for humans and 5 days for agent provisioning, and human attrition is modelled at 14% in FY2026 falling to 11% in FY2028 (COMPANY.md §8).

Roles used below: **CPO** = Chief People Officer; **People Operations Specialist** = the first People hire (level `consultant`, from 2026-09-01; the CPO covers the seat until then); **Talent Acquisition Partner** = owns requisition-to-offer steps from FY2027 (until then the People Operations Specialist, with the CPO); **Hiring Manager** = the requesting department head or delegate; **PeopleAgent** = the AI agent. Under COMPANY.md §9.4 the agent may draft, analyse, monitor and propose, but never takes a final hiring or termination decision and never notifies regulators; every such decision carries a named human approver in the body key `decided_by`.

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-PEOPLE-01 | Requisition intake and triage | `<dept>.hire_requested` (all departments), `delivery.staffing_requested`, `delivery.capacity_forecast_updated` | People Operations Specialist | Requisition opened within 2 business days |
| SOP-PEOPLE-02 | Headcount approval and job posting | `executive.headcount_approved` | CPO | Job posted within 3 business days of approval |
| SOP-PEOPLE-03 | Candidate screening and interview | `external.candidate_applied` | People Operations Specialist | Human screen decision within 3 business days of application; offer decision within 45 days of posting |
| SOP-PEOPLE-04 | Offer, pre-employment checks and acceptance | Hiring decision recorded (internal, follows SOP-PEOPLE-03) | CPO | Offer issued within 2 business days of decision; checks closed before start date |
| SOP-PEOPLE-05 | Onboarding and day-one readiness | `people.new_hire_started` lifecycle; `it_security.access_provisioned`, `operations.workspace_ready` | People Operations Specialist | Access and workspace confirmed 2 business days before start; 30/60/90 check-ins held |
| SOP-PEOPLE-06 | Offboarding and leaver close-out | Resignation or dismissal recorded (internal); `it_security.access_revoked` | CPO | Access revoked on the last working day by 17:00; final pay on the next scheduled payday |
| SOP-PEOPLE-07 | Contractor and associate engagement | `delivery.staffing_requested` where the staffing gap is filled by a contractor or associate | People Operations Specialist | Status determination within 3 business days; contract before start |
| SOP-PEOPLE-08 | Annual budget and headcount planning | `finance.budget_cycle_opened`, `executive.budget_approved` | CPO | `people.budget_submitted` by the finance deadline; plan loaded within 5 business days of approval |
| SOP-PEOPLE-09 | Payroll liaison | Monthly schedule (payroll cut-off 20th); any `people.new_hire_started`, `people.employee_left` or pay change | People Operations Specialist | Payroll inputs to the bureau by cut-off; zero off-cycle payments caused by late inputs |
| SOP-PEOPLE-10 | Performance and calibration cycle | `executive.okrs_set`; schedule (mid-year review June, year-end review December) | CPO | Reviews complete within 20 business days of cycle open; calibration signed off within 5 business days of close |
| SOP-PEOPLE-11 | Engagement survey and culture | Quarterly schedule; `executive.strategy_updated` | CPO | Survey closed in 10 business days; results to executive and delivery within 5 business days; action plan within 15 |
| SOP-PEOPLE-12 | Compliance training, policy and regulatory change | `legal.policy_update_published`, `legal.regulatory_change_noted` | CPO | Training assigned within 5 business days of notice; 95% completion within 30 days |
| SOP-PEOPLE-13 | Grievance, disciplinary and employee relations | Case raised by employee or manager (internal) | CPO | Acknowledge within 2 business days; hearing within 10 business days; outcome in writing within 5 business days of hearing |
| SOP-PEOPLE-14 | Human oversight of AI in HR decisions | Every agent output that informs a person-affecting decision; quarterly audit schedule | CPO | 100% of person-affecting decisions carry a named human decider; quarterly audit report within 15 business days of quarter end |
| SOP-PEOPLE-15 | Crisis people response | `executive.crisis_declared` | CPO | Hiring freeze and staff communication within 1 business day |

Topic coverage check. Subscribed topics and the SOP that handles each: `delivery.capacity_forecast_updated` (01), `delivery.staffing_requested` (01, 07), `executive.budget_approved` (08), `executive.crisis_declared` (15), `executive.headcount_approved` (02), `executive.okrs_set` (10), `executive.strategy_updated` (11), `external.candidate_applied` (03), `finance.budget_cycle_opened` (08), `it_security.access_provisioned` (05), `it_security.access_revoked` (06), `legal.policy_update_published` (12), `legal.regulatory_change_noted` (12), `operations.workspace_ready` (05), and `customer_success.hire_requested`, `data.hire_requested`, `delivery.hire_requested`, `executive.hire_requested`, `finance.hire_requested`, `it_security.hire_requested`, `legal.hire_requested`, `marketing.hire_requested`, `operations.hire_requested`, `product.hire_requested`, `sales.hire_requested` (all 01). Published topics and the SOP that emits each: `people.requisition_opened` (01), `people.job_posted` (02), `people.offer_accepted` (04), `people.new_hire_started` (05), `people.employee_left` (06), `people.contractor_engaged` (07), `people.budget_submitted` (08), `people.engagement_survey_completed` (11), `people.compliance_training_completed` (12), `people.hire_requested` (08, for the People department's own growth roles).

Common conventions. Requisition ids use `REQ-0001`, employee ids `EMP-0001`, budget cycles `BUD-2026` (CONVENTIONS.md §4). Dates in sim time are integer days (`due_day`, `start_day`). Salary figures are base salary in `base_gbp`; loaded cost is base x 1.28 (COMPANY.md §5.2). Level keys and bands come from COMPANY.md §6.2 and US hires carry a +15% uplift once the New York office opens in Q1 FY2027 (COMPANY.md §1).

## SOP-PEOPLE-01: Requisition intake and triage

**Owner**: People Operations Specialist (accountable: CPO)
**Trigger**: `delivery.hire_requested`, `sales.hire_requested`, `marketing.hire_requested`, `finance.hire_requested`, `legal.hire_requested`, `it_security.hire_requested`, `operations.hire_requested`, `customer_success.hire_requested`, `product.hire_requested`, `data.hire_requested`, `executive.hire_requested`; also `delivery.staffing_requested` and `delivery.capacity_forecast_updated` as demand signals.
**Inputs**: requesting department, role title, level key, number of heads, justification (engagement, workload or backfill), target start day, whether the role is in the approved budget (COMPANY.md §5.4, §6.1), proposed band.

### Steps

1. [agent] Parse the request, normalise `role_title` and `level` to a COMPANY.md §6.2 level key, and reject malformed requests back to the requester with a reason.
2. [agent] Check the department's approved headcount for the year against COMPANY.md §6.1 plus approved changes: compute `in_plan = (current + open_reqs + requested) <= plan_year_end`.
3. [agent] For `delivery.capacity_forecast_updated`, compare forecast demand with bench and open requisitions; if the shortfall exceeds 1.0 FTE for two consecutive forecasts, draft a hire proposal and route it to the delivery head as a `delivery.hire_requested` equivalent for confirmation, never opening a requisition unprompted.
4. [agent] For `delivery.staffing_requested`, check the internal bench first and the requested start window; if no internal cover exists, set `route` to `permanent_hire` or `contractor` (continue in SOP-PEOPLE-07).
5. [agent] Draft the requisition: id from the bus counter (`REQ-0001` format), job family, level, band, loaded cost (base x 1.28), annualised budget impact, and a time-to-hire target of 45 days.
6. [human] People Operations Specialist reviews the draft against the compensation bands and internal equity (no offer above the band maximum without a CPO and CEO decision), and confirms `in_plan`.
7. [human] CPO approves opening the requisition. Out-of-plan requests are opened with `needs_approval: true` and wait for the CEO decision in SOP-PEOPLE-02 (COMPANY.md §9.3).
8. [agent] Emit `people.requisition_opened` to executive and finance, and create a People task "Await headcount approval for REQ-xxxx" with due day = request day + 3.

### Outputs and messages

- `people.requisition_opened` (recipient `*`; subscribers executive and finance): `requisition_id`, `department`, `role_title`, `level`, `count`, `band_gbp` (min and max), `loaded_cost_gbp`, `in_plan` (bool), `needs_approval` (bool), `target_start_day`, `justification`, `route`.
- People task for the People Operations Specialist; no other topics.

### SLA and controls

- Requisition opened within 2 business days of request; demand signals (capacity forecast) reviewed weekly.
- Control: every requisition has one named Hiring Manager and one budget owner; no duplicate requisitions for the same role and department (de-duplication on department, role and level within 30 days).
- Control: requisition volume reconciled monthly to the headcount plan in COMPANY.md §6.1 (FY2026 year-end target 38 humans).

### Exceptions and escalation

- Out-of-plan request: open with `needs_approval: true`; CEO approves via `executive.headcount_approved` (COMPANY.md §9.3).
- Request from the People department itself (own growth): emit `people.hire_requested` to executive (SOP-PEOPLE-08).
- Backfill for an unplanned leaver: opened within 1 business day, marked `justification: backfill`, still requires CPO sign-off.
- Hiring Manager disputes the level or band: CPO decides within 3 business days; disagreement escalates to the CEO.

## SOP-PEOPLE-02: Headcount approval and job posting

**Owner**: CPO
**Trigger**: `executive.headcount_approved`
**Inputs**: the approval message (`requisition_id`, `approved` flag, approver, any conditions), the open requisition record, the job-description library.

### Steps

1. [agent] Match the approval to the open requisition by `requisition_id`; if none is found, log an `people.activity.orphan_approval` event and create a task for the People Operations Specialist.
2. [agent] If `approved` is false or conditional, update the requisition state (`on_hold` or `rejected`), notify the requester via a task, and stop.
3. [agent] Draft the job advert from the library: role summary, level, salary band (published on the advert to meet pay-transparency expectations and the Equality Act 2010 duty not to discriminate), location (London or New York from Q1 FY2027), and right-to-work statement. Remove gendered or age-coded language and proxies for protected characteristics.
4. [human] People Operations Specialist and Hiring Manager approve the advert and the interview panel (minimum two interviewers, one from outside the immediate team) within 2 business days.
5. [agent] Select channels (job boards, referrals, specialist communities) and set the advert close date = posting day + 21.
6. [agent] Emit `people.job_posted` to marketing so employer-brand content and any paid promotion can be arranged, and record `posted_day` in state.
7. [agent] Create tasks: screen applications every 2 business days; weekly pipeline review with the Hiring Manager.

### Outputs and messages

- `people.job_posted` (recipient `*`; subscriber marketing): `requisition_id`, `department`, `role_title`, `level`, `band_gbp`, `channels` (list), `posted_day`, `close_day`, `location`.

### SLA and controls

- Job posted within 3 business days of approval (4 business days if a panel cannot be agreed).
- Control: only approved requisitions are posted; the posting is a hard gate on a recorded CEO or CPO approval.
- Control: advert text passes the inclusive-language check and always states a salary band within COMPANY.md §6.2.
- Referral policy: a referral bonus of £2,000 is paid half at start and half after the 6-month probation, subject to the referrer still being employed.

### Exceptions and escalation

- Approval received for a requisition already filled or withdrawn: log and close.
- No qualified applicants after 14 days: People Operations Specialist reviews the advert, band and channels; the CPO decides whether to engage a search firm (fee 20% of first-year base, approved as non-budgeted spend per COMPANY.md §9.3 if above £50k).
- Conditional approval (e.g. "after the Series A closes"): hold the requisition and re-check on `executive.budget_approved` or the stated date.

## SOP-PEOPLE-03: Candidate screening and interview

**Owner**: People Operations Specialist (accountable: CPO)
**Trigger**: `external.candidate_applied`
**Inputs**: candidate record (`candidate_id`, `name`, `requisition_id` or open role, CV summary, source, work-authorisation statement), job description and scorecard.

### Steps

1. [agent] Acknowledge receipt, log the candidate under the matching requisition, and check for duplicates and previous applications (retain per the retention schedule in step 9).
2. [agent] Produce a structured, criteria-based summary against the scorecard (skills, experience, evidence). The agent never rejects a candidate: it produces a recommendation with reasons and a confidence note for human review (SOP-PEOPLE-14).
3. [human] People Operations Specialist screens every application, including those the agent ranked low, using a sampling control: 100% of "do not progress" recommendations are reviewed during the first 90 days of any new scoring approach and 20% thereafter, selected by deterministic sampling.
4. [human] 30-minute screening call; reasonable adjustments offered at every stage on request (Equality Act 2010).
5. [human] Structured panel interview using the same questions and scoring rubric for every candidate for the role; scorecards completed before the debrief; no unstructured "culture fit" scoring.
6. [agent] Collate scorecards, flag outliers (score spread >2 points between interviewers) and draft the debrief pack; add the pipeline status to the weekly report.
7. [human] Hiring Manager and People Operations Specialist make the hiring decision and record `decided_by` and the reasons. For heads of department and above, the CEO decides; for executive appointments, the Remuneration Committee is consulted (COMPANY.md §9.1).
8. [human] Unsuccessful candidates receive a respectful decline within 5 business days of the decision, with feedback on request.
9. [agent] Apply retention: unsuccessful candidate data deleted after 6 months unless consent is given to retain for 12 months (UK GDPR storage-limitation principle).

### Outputs and messages

- Internal state and tasks only (`people.activity.candidate_screened`); the pipeline status is carried in the weekly digest.
- On a recorded decision to offer, the flow proceeds to SOP-PEOPLE-04.

### SLA and controls

- Application acknowledged the same business day; human screen decision within 3 business days; first interview within 10 business days of application; offer decision within 45 days of the job posting (COMPANY.md §8 time-to-hire).
- Controls: structured scorecards; blind CV review for the initial human screen where practicable (names and photos removed by the agent); diverse panel where possible; adverse-impact monitoring each quarter by gender and ethnicity on aggregated data, with the ratio of selection rates tested against the four-fifths rule as an investigation trigger (not as a legal threshold).
- No fully automated rejection (UK GDPR Article 22): a human must meaningfully review any adverse outcome.

### Exceptions and escalation

- Candidate declares a disability and asks for adjustments: People Operations Specialist arranges within 2 business days.
- Candidate with a conflict of interest (relative of an employee or a client contact): disclose to the CPO and General Counsel before any interview.
- Evidence of discrimination in a Hiring Manager's scoring: pause the requisition and escalate to the CPO; if substantiated, SOP-PEOPLE-13 applies.
- Unusual application volume (more than 150 for one role): switch to a longlist-then-shortlist process, with the longlist agreed by two humans.

## SOP-PEOPLE-04: Offer, pre-employment checks and acceptance

**Owner**: CPO
**Trigger**: hiring decision recorded under SOP-PEOPLE-03 (internal event `people.internal.offer_decision`); the candidate's written acceptance emits `people.offer_accepted`.
**Inputs**: the scorecard decision, requisition (level, band), compensation benchmark, candidate's current package and notice period.

### Steps

1. [agent] Draft an offer proposal: base within the §6.2 band for the level (analyst £38,000 to £48,000, consultant £55,000 to £70,000, senior consultant £72,000 to £90,000, manager £92,000 to £115,000, principal £120,000 to £155,000, partner £160,000 to £220,000), bonus eligibility, start date given notice period, probation of 6 months.
2. [human] CPO approves the offer. Offers above the band maximum need a CEO decision; head-of-department and executive offers go to the CEO and, for executive pay, the Remuneration Committee.
3. [human] People Operations Specialist makes a verbal offer and then issues the written offer subject to checks. The written offer sits within a statement of written particulars issued on or before day one (Employment Rights Act 1996 s.1, as amended).
4. [human] Pre-employment checks: right to work (Home Office online check or manual document check, with a copy retained), two references, identity, and for client-facing roles a basic DBS check where the client requires it. Credit or other checks are only run where proportionate and justified.
5. [human] If sponsorship is needed (Skilled Worker route), confirm the role meets the salary threshold and code requirements, assign a Certificate of Sponsorship under the sponsor licence, and allow an extra 4 to 8 weeks before the start date.
6. [human] Candidate signs the contract (digitally); counter-signature by the CPO or delegate. Contract terms are the standard template reviewed by the General Counsel; non-standard IP, restrictive covenants or data terms go to legal (COMPANY.md §9.3).
7. [agent] On acceptance, record the start date, set the checks task list, and emit `people.offer_accepted` to finance and legal with the employee identity, role, level, base, start day, and `decided_by`.
8. [agent] Create the `EMP-xxxx` record and add the new hire to the onboarding workflow (SOP-PEOPLE-05); remind the People Operations Specialist of outstanding checks 5 business days before the start date.

### Outputs and messages

- `people.offer_accepted` (recipient `*`; subscribers finance and legal): `employee_id`, `employee_name`, `requisition_id`, `department`, `role_title`, `level`, `base_gbp`, `start_day`, `contract_type` (`permanent`), `location`, `right_to_work_status`, `decided_by`.

### SLA and controls

- Offer issued within 2 business days of the decision; offer expires after 7 calendar days; target acceptance rate 85%.
- Controls: offer within band; two-person authorisation (CPO plus the hiring head); right-to-work check completed before the first day, never after (civil penalty for employing without a check, up to £60,000 per worker at the time of writing, treated here as a modelled risk, not a legal citation).
- Control: `offer_accepted` is emitted only once the signed contract is on file and `decided_by` is a human.

### Exceptions and escalation

- Right-to-work check fails or lapses: start date withheld; CPO and General Counsel decide; no work begins.
- Offer declined: record the reason, notify the Hiring Manager the same day, and reopen the pipeline (second-choice candidate only if the original scorecard shows a hire-level rating).
- Counter-offer above band: CPO and CEO decide; if refused, the candidate is told within 2 business days.
- Notice period longer than 3 months: hiring head and CPO agree either a buy-out or a delayed start.

## SOP-PEOPLE-05: Onboarding and day-one readiness

**Owner**: People Operations Specialist (accountable: CPO)
**Trigger**: `it_security.access_provisioned` and `operations.workspace_ready` (readiness confirmations for an accepted offer); the lifecycle is started by `people.offer_accepted` under SOP-PEOPLE-04 and the start day itself by the schedule in the new-hire record.
**Inputs**: `EMP-xxxx` record, start day, role and department, equipment profile, systems-access profile by role, buddy assignment.

### Steps

1. [agent] At offer acceptance, open the onboarding plan with milestones: pre-boarding (T-10 days), day one, week one, 30/60/90 days.
2. [agent] Request access and equipment through the lifecycle: the `people.new_hire_started` message (below) is emitted on the start day; for planning, tasks are created T-5 days to chase it_security and operations for confirmations.
3. [human] People Operations Specialist sends the welcome pack, confirms the start-date logistics, and assigns a buddy (not the line manager) and a named Hiring Manager induction owner.
4. [agent] On `it_security.access_provisioned`, record the access profile and the time taken (SLA: 5 days for agent provisioning is the corporate benchmark; humans target 2 business days before start). On `operations.workspace_ready`, record the desk, laptop and equipment serial against the `EMP-xxxx` record.
5. [human] Day one: right-to-work original documents seen if not already verified, contract signed copy filed, bank details and tax information collected (P45 or starter checklist), pension auto-enrolment communication issued within 6 weeks of the joining date (eligibility under the Pensions Act 2008), and the employee handbook and AI-use policy acknowledged.
6. [agent] Emit `people.new_hire_started` to it_security, operations, finance and delivery on the start day with the access profile, payroll start date and equipment list.
7. [human] Line manager sets objectives within 30 days; People Operations Specialist holds 30/60/90-day check-ins; the 6-month probation review is booked on day one.
8. [agent] Compile compliance training assignments (data protection, information security, anti-bribery, AI use) and release them to the new hire in week one (SOP-PEOPLE-12).

### Outputs and messages

- `people.new_hire_started` (recipient `*`; subscribers it_security, operations, finance, delivery): `employee_id`, `employee_name`, `department`, `role_title`, `level`, `start_day`, `manager`, `base_gbp`, `access_profile`, `equipment` (list), `location`, `requisition_id`.

### SLA and controls

- Access and workspace confirmed 2 business days before start; no hire starts work without a completed right-to-work check; 30/60/90 check-ins held 90% on time; 90-day new-hire retention target 97%.
- Control: payroll set-up complete before the first payroll cut-off after the start date (SOP-PEOPLE-09).
- Control: least-privilege access profile reviewed by the line manager within 30 days.

### Exceptions and escalation

- Access or workspace not confirmed 2 days before start: People Operations Specialist chases it_security or operations; if still open the day before, the start is moved by up to 3 days and the new hire told directly; escalation to the CPO and the COO.
- No-show on day one: call within 2 hours, then email, then notify the Hiring Manager; after 3 business days of silence escalate to the CPO and treat as a withdrawn acceptance (the offer lapses in writing).
- Under-18 or visa-conditional start: CPO approves arrangements (working-time and sponsorship conditions) before the start date.

## SOP-PEOPLE-06: Offboarding and leaver close-out

**Owner**: CPO
**Trigger**: resignation or dismissal recorded in the leaver case (internal event `people.internal.leaver_recorded`); close-out confirmed by `it_security.access_revoked`.
**Inputs**: resignation letter or termination decision, contract (notice period), holiday balance, outstanding expenses, assets issued, client commitments of the leaver.

### Steps

1. [human] Line manager informs the People Operations Specialist within 1 business day of a resignation; People Operations Specialist holds a conversation within 3 business days to understand the reason and discuss any retention option approved by the CPO.
2. [human] Confirm notice, last working day and handover plan; set garden leave only if the CPO and the General Counsel agree and the contract allows. Statutory minimum notice is observed for dismissals (1 week per full year of service up to 12 weeks, after the first month).
3. [agent] Compute the final pay inputs: salary to last day, accrued untaken holiday (statutory 28 days including bank holidays, pro rata), notice pay, expense claims and any bonus accrual; send to the payroll bureau via SOP-PEOPLE-09.
4. [human] Dismissals: no termination is decided by an agent. A named human decider and a second human reviewer sign off, a fair process is run (ACAS Code), and the General Counsel is consulted before any dismissal of an employee with over 2 years of service, a discrimination or whistleblowing claim, or a redundancy situation. The Employment Rights Act 2025 transitional changes are tracked through SOP-PEOPLE-12 and applied to the process as they commence.
5. [human] Exit interview within the last week; themes (reason for leaving, manager, pay, growth) logged without identifying individuals in aggregated reports.
6. [agent] Schedule the leaver checklist: laptop and asset return, system access end time, client handover, knowledge transfer, shared-mailbox forwarding and removal from distribution lists.
7. [agent] Emit `people.employee_left` to it_security, finance, operations and legal with the last working day and `access_end_time` (17:00 on the last day, or immediately for a summary dismissal or a security-sensitive departure).
8. [agent] On `it_security.access_revoked`, record the confirmation time and the assets returned; flag any gap between `access_end_time` and revocation (target: 0 hours, tolerance 4 hours).
9. [human] Final-pay P45 issued; reference policy applied (factual reference only); restrictive covenants and confidentiality reminders sent by the General Counsel's template.

### Outputs and messages

- `people.employee_left` (recipient `*`; subscribers it_security, finance, operations, legal): `employee_id`, `employee_name`, `department`, `role_title`, `last_day`, `access_end_time`, `leaver_type` (`resignation`|`dismissal`|`redundancy`|`end_of_contract`), `regretted` (bool), `final_pay_inputs`, `engagement_id` list where the leaver is on active engagements.

### SLA and controls

- Access revoked on the last working day by 17:00 (immediately for summary dismissal); final pay on the next scheduled payday; exit interviews held for 90% of voluntary leavers.
- Controls: attrition tracked against the modelled 14% (FY2026), 12.5% (FY2027) and 11% (FY2028) (COMPANY.md §8: 14% in Y1 to 11% in Y3; the FY2027 figure is the mid-point); regretted leavers reviewed monthly.
- Control: any leaver on a client engagement triggers a handover note to the delivery head and a staffing review (SOP-PEOPLE-01).

### Exceptions and escalation

- Gross misconduct allegation: suspend only as a neutral act, with CPO and General Counsel approval, and run SOP-PEOPLE-13.
- Leaver with privileged access, client data access or in a client-facing role: it_security informed before the employee is told, with access revoked in step with the conversation.
- Redundancy of 20 or more employees at one establishment within 90 days triggers statutory collective consultation (Trade Union and Labour Relations (Consolidation) Act 1992); not modelled in the baseline plan, so the CPO escalates to the CEO and General Counsel immediately.
- Dispute about final pay: CPO and CFO review within 3 business days.

## SOP-PEOPLE-07: Contractor and associate engagement

**Owner**: People Operations Specialist (accountable: CPO)
**Trigger**: `delivery.staffing_requested` where the gap is routed to a contractor or associate under SOP-PEOPLE-01 step 4; subcontractor spend sits in the delivery budget (COMPANY.md §5.2).
**Inputs**: engagement id, skill needed, duration, day rate, source (associate network or agency), client sensitivity of the work.

### Steps

1. [agent] Check that the staffing request cannot be filled by the bench or a fixed-term hire, and check the rate against the rate card ceiling for the equivalent level (e.g. a Senior Consultant equivalent must not exceed £1,050 day rate cost to the client, COMPANY.md §3.5; the contractor cost must leave the planned margin).
2. [human] People Operations Specialist conducts the employment status check using the HMRC CEST tool as a starting point and records reasons. Lumenhall is assumed to be a medium or large client for the off-payroll working rules (IR35), so Lumenhall issues a status determination statement and applies the result; a determination of "inside IR35" means fee-payer deductions of tax and National Insurance through payroll.
3. [human] General Counsel approves the contractor agreement (IP assignment, confidentiality, data-protection and security terms, no authority to bind Lumenhall); non-standard terms follow COMPANY.md §9.3.
4. [human] Engagement is placed with IT Security for access under a time-limited profile (end date equal to the contract end date) and a named Lumenhall sponsor.
5. [agent] Emit `people.contractor_engaged` to finance, legal and it_security with the contract details and a 14-day review reminder before the contract end.
6. [human] Monthly: the sponsor approves timesheets; finance pays against an approved purchase order only.

### Outputs and messages

- `people.contractor_engaged` (recipient `*`; subscribers finance, legal, it_security): `contractor_id` (`EMP-xxxx` series with prefix `CTR-` in the person record), `contractor_name`, `engagement_id`, `department`, `skill`, `day_rate_gbp`, `start_day`, `end_day`, `ir35_status` (`inside`|`outside`), `status_reason`, `max_days`, `sponsor`.

### SLA and controls

- Status determination within 3 business days; contract signed before the first day; no contractor starts without access scoping from it_security; contractor days reconciled monthly against the subcontractor budget line.
- Control: contractors may not exceed 12 continuous months without a CPO review (avoiding de facto employment and disguised permanent headcount).
- Control: contractors and associates handle client data only under the same confidentiality and DPA terms as employees (COMPANY.md §9.4).

### Exceptions and escalation

- Status determination disputed by the contractor: use the Lumenhall client-led disagreement process; unresolved cases go to the General Counsel and CFO within 30 days.
- Contractor request above £50,000 total value is non-budgeted spend needing CFO approval, and above £250,000 CEO approval (COMPANY.md §9.3).
- Contractor access misuse: it_security revokes immediately; People Operations Specialist records the incident and the General Counsel decides on contract termination.

## SOP-PEOPLE-08: Annual budget and headcount planning

**Owner**: CPO
**Trigger**: `finance.budget_cycle_opened` (opens in Q4); `executive.budget_approved` closes the cycle.
**Inputs**: COMPANY.md §6.1 headcount plan, §5.4 envelope, current headcount and open requisitions, attrition forecast, hiring plans from each department, salary-review budget, training and tooling needs.

### Steps

1. [agent] On `finance.budget_cycle_opened`, compile the People department's baseline from the current run-rate: average headcount x loaded cost (base x 1.28), recruitment fees, tooling, training and culture spend.
2. [agent] Collate all open and planned requisitions for the next year from every department and compute total hiring volume = growth hires plus attrition backfills at the modelled rate (14%, 12.5%, 11% by year; COMPANY.md §8).
3. [agent] Draft the People department's budget against the envelope in COMPANY.md §5.4 (FY2026 £310k, FY2027 £700k, FY2028 £1,850k) with line items for people, recruitment, HR systems, learning and development, wellbeing and employee relations support, employment-law advice and payroll-bureau fees.
4. [human] CPO reviews, adjusts and approves the submission; any ask beyond the envelope is marked as an incremental request with a business case.
5. [agent] Emit `people.budget_submitted` to finance with total, people cost, non-people cost and headcount ask by year.
6. [agent] If the People department's own growth roles are needed (e.g. a second recruiter), emit `people.hire_requested` to executive with justification.
7. [human] On `executive.budget_approved`, CPO confirms the approved envelope, the agent loads the approved headcount plan and quarterly hiring targets into state, and the People Operations Specialist publishes the pay-review and bonus timetable.
8. [agent] Cross-check approved department headcount against COMPANY.md §6.1 and flag any variance above 2 heads.

### Outputs and messages

- `people.budget_submitted` (recipient `finance`): `budget_cycle` (`BUD-2026`), `department` (`people`), `people_cost_gbp`, `non_people_cost_gbp`, `total_gbp`, `headcount` (humans), `agents` (count), `hires_planned`, `attrition_backfills`, `assumptions`.
- `people.hire_requested` (recipient `executive`): `department` (`people`), `role_title`, `level`, `count`, `justification`, `target_start_day`.

### SLA and controls

- Submission by the finance deadline (default 15 business days after the cycle opens); the plan is loaded within 5 business days of approval.
- Control: People submission equals people cost plus non-people cost with arithmetic checked; submission total within £5k of the envelope or accompanied by an explanation.
- Control: salary-review budget approved by the Remuneration Committee for executives and by the CEO for everyone else.

### Exceptions and escalation

- Approved budget lower than the ask: CPO re-plans within 5 business days; hiring plans are re-sequenced by delivery first, then revenue, then enabling functions.
- Budget cycle opened while a hiring freeze is active (SOP-PEOPLE-15): submit the plan with the freeze noted.
- Late departmental hiring input: the CPO escalates to the department head and, after 2 reminders, to the CFO.

## SOP-PEOPLE-09: Payroll liaison

**Owner**: People Operations Specialist (accountable: CPO; finance is the payroll approver)
**Trigger**: monthly schedule (cut-off the 20th; payday the last working day). Inputs are driven by `people.new_hire_started`, `people.employee_left`, pay changes and contractor payments.
**Inputs**: starter and leaver changes, salary changes, bonuses, expenses (from finance), statutory leave (sick, maternity, paternity, shared parental), pension contributions, tax codes.

### Steps

1. [agent] On the 15th, compile the monthly variation list from the HR records: starters (from `people.new_hire_started`), leavers (`people.employee_left`), salary and role changes, bonuses, overtime or on-call allowances, absence and statutory pay.
2. [human] People Operations Specialist verifies each variation against signed documents (contract, change letter, leaver form) and checks that no change lacks a named approver.
3. [human] Send the variation file to the outsourced payroll bureau by cut-off on the 20th; CFO delegate approves the payroll gross-to-net report before it is released.
4. [agent] Check the payroll draft against HR records: headcount reconciliation, total gross pay against budget (loaded cost per COMPANY.md §5.4), large deviations above 3% month on month, negative pay, and employees with no start or end dates.
5. [human] Payment approval: the CFO or delegate approves the BACS file; no payment of £10,000 or more to a single individual is released without a second human approver (agents may not approve payments above £10,000, COMPANY.md §9.4).
6. [human] The bureau submits the Real Time Information (RTI) Full Payment Submission to HMRC on or before payday; People Operations Specialist files the payslips and the reconciliation.
7. [agent] Monthly after payday: reconcile payroll cost to the budget, produce the people-cost variance report for finance, and record any off-cycle payment and its cause.
8. [human] Annual: P60 and P11D by the statutory dates, auto-enrolment re-enrolment every three years, and the holiday-year reset; apprenticeship levy and Statutory Sick Pay handled by the bureau and checked by the People Operations Specialist.

### Outputs and messages

- No new topic is published by this SOP; its effects are carried by `people.new_hire_started` and `people.employee_left` (SOP-PEOPLE-05 and SOP-PEOPLE-06) and the monthly People task and variance record in state.

### SLA and controls

- Variation file to the bureau by cut-off on the 20th; payroll accuracy at least 99.5% of payslips without correction; zero off-cycle payments caused by late People inputs.
- Controls: segregation of duties (the person who inputs a variation does not approve the BACS file); reconciliation of headcount between HR system, payroll and COMPANY.md §6.1; National Minimum Wage and National Living Wage compliance checks at each rate change (April).
- Control: payroll data contains special-category and financial data, so access is limited to the CPO, People Operations Specialist, finance approver and the bureau under a data-processing agreement.

### Exceptions and escalation

- Late starter or leaver after cut-off: off-cycle payment approved by the CFO and recorded; People Operations Specialist explains the cause in the monthly report.
- Underpayment found: corrected in the next run, or as an off-cycle payment within 3 business days if above £500 or causing hardship.
- Overpayment: recovery follows the contract and the Employment Rights Act 1996 deduction rules, agreed in writing with the employee, with General Counsel advice if the amount is above £1,000.
- Payroll bureau failure or breach: escalate to the CPO, CFO and CISO (and to the General Counsel under COMPANY.md §9.3 if a personal-data breach is suspected).

## SOP-PEOPLE-10: Performance and calibration cycle

**Owner**: CPO
**Trigger**: `executive.okrs_set` (company OKRs cascaded into individual objectives); schedule: mid-year review in June, year-end review in December.
**Inputs**: company OKRs, delivery utilisation (COMPANY.md §4), engagement outcomes, 360 feedback, client feedback, objective records.

### Steps

1. [agent] On `executive.okrs_set`, draft the cascade guidance and an objective template per level so each employee has 3 to 5 objectives aligned with the company OKRs; send to line managers as a task.
2. [human] Line managers agree objectives with each employee within 30 days of the OKRs being set; People Operations Specialist audits that 100% have objectives recorded.
3. [agent] At the mid-year and year-end review opening, pre-populate each review pack with objective progress, utilisation (analyst and consultant target 80%, manager 65%, principal 50%, partner 35%), client feedback themes and training completed. The agent provides evidence only, with no rating or ranking suggestion.
4. [human] Line manager writes the review and proposes a rating on a 4-point scale (exceeds, meets, partly meets, does not meet) with evidence; employee provides a self-review.
5. [human] Calibration meetings by department, chaired by the CPO, review rating distributions, check for bias patterns (by tenure, gender, ethnicity, part-time and location) using aggregated analytics from the agent, and agree final ratings.
6. [human] Promotion and pay recommendations are decided by the department head and the CPO, and approved by the CEO; Partner-level promotions are also notified to the Remuneration Committee (COMPANY.md §9.1).
7. [agent] Create the follow-up tasks: development plans for every "partly meets" and "does not meet" rating, and a performance improvement plan only after a named human approves it.
8. [human] Communicate outcomes in 1:1 conversations within 10 business days of calibration; pay changes take effect on the next payroll cut-off (SOP-PEOPLE-09).

### Outputs and messages

- No new topic is published by this SOP. Summary metrics (completion rate, rating distribution, regretted attrition) feed `people.engagement_survey_completed` context and the department KPIs; promotions and pay changes flow through payroll variations.

### SLA and controls

- Reviews complete within 20 business days of the cycle opening; calibration signed off within 5 business days of the cycle closing; 100% of employees hold documented objectives; 95% of reviews delivered on time.
- Controls: ratings and rankings are always set by humans; no agent output is used as the sole basis for a rating, promotion, pay change or dismissal (SOP-PEOPLE-14); distribution is monitored but not forced.
- Control: a performance improvement plan lasts 4 to 8 weeks, has written, measurable objectives, a named support person and is reviewed weekly.

### Exceptions and escalation

- Disputed rating: employee appeals to the CPO within 10 business days; the CPO or the CEO decides with a written reason.
- Capability concern during probation: addressed under the probation procedure; probation may be extended once by up to 3 months with written notice.
- Performance concern linked to ill health or disability: the People Operations Specialist takes occupational health advice and considers reasonable adjustments before any capability process (Equality Act 2010).

## SOP-PEOPLE-11: Engagement survey and culture

**Owner**: CPO
**Trigger**: quarterly schedule (pulse in March, June, September; full survey in November); `executive.strategy_updated` (communication and culture alignment).
**Inputs**: survey instrument (12 questions pulse, 40 questions annual), headcount list, prior scores, exit-interview themes, strategy update.

### Steps

1. [agent] At the quarterly schedule, build the survey from the question bank and the current headcount list; anonymity threshold: no result is shown for a group of fewer than 5 respondents.
2. [human] CPO approves the survey and announces it with a letter from the CEO; the survey runs for 10 business days with one reminder per week.
3. [agent] Compute the engagement index (average of the 5 core items on a 1 to 5 scale), eNPS (promoters 9 to 10 minus detractors 0 to 6), participation rate, and driver themes by department and level; the agent summarises free-text comments but never tries to identify the author.
4. [human] CPO and People Operations Specialist review the output, remove any potentially identifying comments, and write the narrative with the 3 priority actions.
5. [agent] Emit `people.engagement_survey_completed` to executive and delivery with the index, eNPS, participation and top themes.
6. [human] Delivery head and CPO agree a response within 15 business days; actions are tracked on the department task list and reviewed at the next pulse.
7. [human] On `executive.strategy_updated`, the CPO assesses the people implications (roles, culture, change load, hiring plan), briefs the executive team, and the People Operations Specialist updates the internal communications plan within 10 business days.

### Outputs and messages

- `people.engagement_survey_completed` (recipient `*`; subscribers executive and delivery): `survey_id`, `quarter`, `engagement_index`, `enps`, `participation_pct`, `top_themes` (list), `lowest_department`, `action_owner`, `at_risk_headcount`.

### SLA and controls

- Survey closes in 10 business days; results to executive and delivery within 5 business days of close; action plan within 15 business days.
- Targets: participation at least 85%, engagement index at least 4.0 of 5, eNPS at least +30 (department KPIs in `kpis.md`).
- Controls: anonymity threshold of 5; the survey data is processed under a lawful basis with a privacy notice; no individual-level data shared with managers.

### Exceptions and escalation

- Participation below 70%: the CPO investigates survey fatigue or trust and re-runs a short pulse within 4 weeks.
- A group scores more than 0.5 below the company average for two consecutive surveys: CPO and CEO review leadership and workload; escalate to the delivery head.
- Free text discloses harassment, a safeguarding concern or whistleblowing: the CPO treats it under SOP-PEOPLE-13 and the whistleblowing policy (Public Interest Disclosure Act 1998) without breaching anonymity unnecessarily.

## SOP-PEOPLE-12: Compliance training, policy and regulatory change

**Owner**: CPO
**Trigger**: `legal.policy_update_published`, `legal.regulatory_change_noted`
**Inputs**: the legal notice (policy or regulation, effective date, affected populations), training catalogue, completion records, `people.compliance_training_completed` history.

### Steps

1. [agent] On `legal.policy_update_published`, map the policy (for example data protection, anti-bribery, acceptable use, AI use) to the affected populations, and propose a training and acknowledgement plan with due dates.
2. [agent] On `legal.regulatory_change_noted`, assess the people impact: employment law, working-time, pay reporting, immigration, health and safety, AI regulation as it applies to HR (EU AI Act classifies employment AI as high-risk; the UK approach follows the principles set out in COMPANY.md §8.7). Draft a people-impact note and a list of People policies and templates to update.
3. [human] General Counsel and CPO agree the response (policy change, notice period, employee communication); changes to contracts or terms follow a consultation and consent process, never by unilateral variation.
4. [human] People Operations Specialist publishes the updated handbook sections, assigns training through the learning platform and records acknowledgements with a timestamp.
5. [agent] Chase completions at day 10, 20 and 25, report to line managers, and escalate non-completers on day 30.
6. [agent] When completion reaches the target (95% within 30 days, 100% within 60 days), emit `people.compliance_training_completed` to legal and it_security with the completion statistics.
7. [human] Annual: refresh the mandatory curriculum (UK GDPR and data protection, information security, anti-bribery and corruption, equality and unconscious bias, health and safety, AI use and human oversight) and confirm the evidence pack for ISO 27001 and Cyber Essentials Plus (FY2026) and SOC 2 Type II (FY2027) (COMPANY.md §8.7).

### Outputs and messages

- `people.compliance_training_completed` (recipient `*`; subscribers legal and it_security): `training_id`, `course`, `policy_ref`, `population` (count), `completed` (count), `completion_pct`, `overdue` (count), `due_day`, `completed_day`.

### SLA and controls

- Training assigned within 5 business days of notice; 95% completion within 30 days and 100% within 60 days; new joiners complete the mandatory curriculum within 14 days of starting.
- Controls: completion evidence retained for audit (ISO 27001 control, SOC 2 evidence); non-completion past day 60 is reported to the department head and the CPO, and access to client systems can be restricted by it_security on the CPO and CISO decision.
- Control: policy updates are version-controlled; the handbook shows the effective date and change summary.

### Exceptions and escalation

- Regulatory change with a short fuse (effective in under 30 days): the CPO calls an immediate review with the General Counsel and informs the CEO.
- Persistent non-completion by a senior leader: the CPO escalates to the CEO.
- A change affecting contracts (for example flexible-working or family-leave rights): the CPO and General Counsel agree communications and consultation before the change takes effect.

## SOP-PEOPLE-13: Grievance, disciplinary and employee relations

**Owner**: CPO (accountable: CEO for cases involving the CPO)
**Trigger**: a grievance, disciplinary concern, harassment complaint or whistleblowing report is raised (internal event `people.internal.case_opened`).
**Inputs**: the written complaint or manager report, relevant policies, ACAS Code of Practice on Disciplinary and Grievance Procedures, evidence, witness list.

### Steps

1. [human] People Operations Specialist acknowledges the case within 2 business days and records it in the confidential case log with severity (`low`|`medium`|`high`|`critical`).
2. [human] CPO assesses the case type: grievance, conduct, capability, harassment or discrimination, whistleblowing, or a safeguarding matter. Whistleblowing and harassment cases are always handled by the CPO personally.
3. [human] For allegations of serious misconduct, CPO and General Counsel decide on neutral suspension on full pay; suspension lasts no more than 10 business days without review.
4. [human] Appoint an impartial investigator (internal manager not involved, or an external HR investigator, procured against a purchase order, typical cost £4,000 to £8,000).
5. [human] Investigation within 10 business days: interviews, evidence, report with findings. No agent is used to assess credibility, draw conclusions or recommend sanctions. The agent may only schedule, organise documents and draft neutral meeting notes for human review.
6. [human] Disciplinary or grievance hearing with the right to be accompanied (Employment Relations Act 1999); a decision-maker who has not investigated the case; written outcome within 5 business days of the hearing with a right of appeal.
7. [human] Appeal heard by a senior leader not previously involved, within 10 business days of the appeal; the outcome is final.
8. [agent] Update the aggregate statistics (case type, time to close, outcomes) with no personal data in reports other than to the CPO, and flag any pattern by team, manager or protected characteristic for human review.
9. [human] The CPO informs the CEO of high or critical cases within 1 business day and the General Counsel of any case with litigation risk (tribunal claim, ACAS early conciliation).

### Outputs and messages

- No new cross-department topic. A resulting dismissal flows through SOP-PEOPLE-06 and `people.employee_left`; sensitive content is never put in message bodies, only the case reference and severity in internal state.

### SLA and controls

- Acknowledge in 2 business days; hearing within 10 business days of investigation completion; written outcome 5 business days after the hearing; 90% of cases closed within 40 business days.
- Controls: strict confidentiality (access limited to the CPO, People Operations Specialist and, as needed, the General Counsel); a fair, consistent process following the ACAS Code (an unreasonable failure to follow it can increase a tribunal award by up to 25%); retention of case files for 6 years after closure (limitation for contract claims) unless law requires otherwise.
- Control: quarterly report to the CEO on case volumes and themes, with no identifiable information.

### Exceptions and escalation

- Complaint concerns a head of department or the CEO: the CPO informs the Chair of the Board, Priya Raman (COMPANY.md §9.1), and an independent investigator is appointed. A complaint concerning the CPO goes to the CEO and the Chair.
- Threat of legal action or ACAS early conciliation: General Counsel takes the lead within 1 business day.
- Safeguarding, criminal or health-and-safety risk: report to the relevant authority through the General Counsel; People never contacts a regulator directly (COMPANY.md §9.4 prohibits agent notification and the General Counsel owns regulatory contact).

## SOP-PEOPLE-14: Human oversight of AI in HR decisions

**Owner**: CPO (accountable human owner of `PeopleAgent`, registered in the agent register per COMPANY.md §9.4)
**Trigger**: every agent output that informs a decision about a person (screening, ranking, offer proposals, performance evidence, payroll checks, case organisation); quarterly audit schedule (end of March, June, September, December).
**Inputs**: the agent register entry, the decision log (`decided_by`, `agent_input`, `outcome`, `override` flag), adverse-impact analytics, the Data Protection Impact Assessment (DPIA), and the EU AI Act and UK GDPR guidance noted by legal.

### Steps

1. [agent] Tag every output that could affect a person (hiring, pay, promotion, discipline, dismissal) as `person_affecting: true`, record its inputs, version, confidence and the reasons shown to the human, and store the record in the decision log.
2. [human] A named human reviews the output and takes the decision, recording `decided_by`, the decision and reasons. The decider must be able to explain the decision without referring to the model output, and must have the authority to disagree.
3. [agent] Block any automated step that would complete an adverse action without a human decision: the agent cannot send a rejection, issue an offer, change pay, trigger a leaver process or open a disciplinary case. It can only propose (COMPANY.md §9.4).
4. [agent] Monitor and report: override rate (human disagrees with the agent), score distributions by protected characteristic (aggregated), drift against the last quarter, and any case where an agent output was used without a recorded human decision.
5. [human] Quarterly audit: CPO and General Counsel review a 5% random sample (minimum 20 decisions) of person-affecting decisions, the monitoring report and any complaints; the CISO checks the access logs and data minimisation.
6. [human] Maintain the DPIA and the record of processing; candidates and employees are told in the privacy notice that an agent assists with screening and what rights they have (access, human review, to contest a decision under UK GDPR Article 22 and the Data Protection Act 2018).
7. [human] Material changes to the agent (a new scoring approach, new data, new model) need a documented risk review, with the General Counsel approving; if the agent is also used in client-facing work, the AI risk review route (`product.ai_risk_review_requested` then `legal.ai_risk_review_completed`) applies (COMPANY.md §9.4).
8. [human] Handle subject access requests and challenges: respond within one calendar month (extendable by up to 2 months for complex requests) with the logic, human reviewer and outcome of any decision about the individual.

### Outputs and messages

- No new cross-department topic. The decision log and quarterly audit report are stored in state and shared with the executive team and the General Counsel; any `people.*` message that results from an agent-assisted decision carries `decided_by` naming a human.

### SLA and controls

- 100% of person-affecting decisions carry a named human decider and reasons; 0 fully automated adverse decisions; audit report within 15 business days of quarter end; subject access responses within 30 days.
- Targets: human override rate between 5% and 30% (below 5% suggests rubber-stamping, above 30% suggests the tool is not helping); selection-rate ratio between 0.8 and 1.25 for each protected group in aggregated pipeline data, with deviations investigated.
- Controls: agent access is least-privilege (no access to health, trade-union, or disciplinary content except what is needed for scheduling); the agent runs only on the approved data and logs every action for audit; the agent may not use protected characteristics or proxies (postcode, school, gaps in CV, name) as scoring features.

### Exceptions and escalation

- Evidence of bias or a wrong decision caused by the agent: suspend that agent function the same day, the CPO and General Counsel review within 3 business days, and affected candidates or employees are reconsidered by a human.
- An agent output used without a recorded human decision: treated as a control failure, reported to the CEO, and the General Counsel considers whether a data-protection or discrimination issue exists.
- Regulatory change affecting AI in employment: handled under SOP-PEOPLE-12.

## SOP-PEOPLE-15: Crisis people response

**Owner**: CPO
**Trigger**: `executive.crisis_declared`
**Inputs**: the crisis declaration (type, severity, expected duration), headcount and open requisitions, wellbeing resources, communications plan.

### Steps

1. [agent] Within 1 hour, produce a people-impact summary: open requisitions, offers pending, new starters in the next 30 days, employees on client-critical engagements, leave booked and key-person dependencies.
2. [human] CPO and CEO decide the people stance. Where the crisis is financial, the default is a hiring freeze on non-delivery roles, with offers already accepted honoured. Where the crisis is a security incident, access reviews and communication come first.
3. [agent] Hold open requisitions marked `on_hold` and notify requesters by task; no new `people.job_posted` is emitted until the freeze is lifted by a human decision.
4. [human] People Operations Specialist and CPO brief employees within 1 business day (clear, factual, with a named contact), and brief line managers on what they may and may not say.
5. [human] Wellbeing: activate the employee assistance programme, offer manager check-ins, and review working patterns; for a physical or safety event, confirm the safety of all employees and record any riddor-reportable event with the General Counsel.
6. [human] Any redundancy proposal follows legal process: consultation, selection criteria, notice, with the General Counsel leading (see SOP-PEOPLE-06 exceptions); no redundancy decision is taken by an agent.
7. [agent] Report weekly on headcount, attrition and the freeze status until the CEO closes the crisis; on closure, reopen held requisitions in priority order of delivery first.

### Outputs and messages

- No new topic is published by the immediate crisis response; held requisitions resume through `people.job_posted` (SOP-PEOPLE-02) after the CEO lifts the freeze. People-impact summaries are shared as tasks with the CEO and the CPO.

### SLA and controls

- People-impact summary within 1 hour; staff communication within 1 business day; freeze status reported weekly; offers already accepted are honoured unless the CEO and General Counsel decide otherwise in writing.
- Control: the crisis log records every people decision with a named human, date and reason.

### Exceptions and escalation

- Crisis involving the death or serious injury of an employee: the CPO and CEO lead directly, notify the family, and the General Counsel handles any regulator contact.
- Crisis involving mass absence or loss of a key team: the CPO and the delivery head invoke the continuity plan, involving associates under SOP-PEOPLE-07.
- Crisis that includes a data breach by an employee: SOP-PEOPLE-13 and the incident process run in parallel.
