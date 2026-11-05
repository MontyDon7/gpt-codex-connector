# People Department Blueprint

> Department id `people`; agent class `PeopleAgent`. Head: Grace Adeyemi, Chief People Officer (COMPANY.md §9.2). All figures are fictional modeled assumptions.

## 1. Mission and scope

**Mission.** Hire, onboard, develop, pay correctly and, when necessary, part with Lumenhall's people, fast enough to staff the growth plan (38 humans at end FY2026, 110 at end FY2027, 230 at end FY2028; COMPANY.md §6) and fairly enough to hold attrition at the modelled 14% falling to 11% (COMPANY.md §8, assumption 3). The department also keeps the company inside UK employment law while it adds a US entity from Q1 FY2027 (COMPANY.md §1).

**In scope**

- Recruiting: requisition intake, job posting, sourcing, interview coordination, offer and contract preparation, pre-employment checks (right to work, references, DBS only where the role requires it), time-to-hire target 45 days for humans (COMPANY.md §8).
- Onboarding: contract and statement of written particulars (day-one right under the Employment Rights framework), Day 1 to Day 90 plan, equipment and access requests to `it_security` and `operations`.
- Offboarding: resignation and dismissal administration, exit interview, final pay liaison, access revocation, knowledge hand-over, alumni record.
- Payroll liaison: monthly payroll inputs (starters, leavers, changes, bonus, expenses) to the outsourced payroll bureau; RTI submissions are the bureau's, approval of the run is Finance's. People never releases payment.
- Performance and reward: twice-yearly review cycle, promotion calibration, annual salary review inside the bands of COMPANY.md §6.2, bonus accrual inputs to Finance.
- Culture and engagement: quarterly pulse survey, annual engagement survey, internal mobility, learning budget, wellbeing, equality, diversity and inclusion (EDI) reporting.
- UK employment basics: contracts, probation (6 months standard), notice, statutory leave and pay (holiday, SSP, maternity/paternity, shared parental), working time, flexible working requests, grievance and disciplinary under the ACAS Code, redundancy and TUPE (advice from `legal`), right-to-work compliance, pension auto-enrolment, gender pay gap reporting once headcount reaches 250 (not within the plan horizon, voluntary reporting from FY2028).
- Contractors and associates: engagement checks (IR35 status determination, owned by `legal` and `finance`) and onboarding; the spend sits in `delivery` (COMPANY.md §5.2).
- Human oversight of AI in HR decisions: no HR decision with legal or similarly significant effect (hire, reject, dismiss, promote, discipline, pay) is made solely by an AI agent (COMPANY.md §9.4; UK GDPR Art 22 and the DPA 2018 automated-decision rules). Agents screen, summarise, schedule and flag; a named human decides and records the reason.

**Out of scope.** Payroll processing and payment release (`finance`), contract drafting and employment litigation (`legal`), laptop and account provisioning (`it_security`), desks and the New York office fit-out (`operations`), consultant staffing to engagements (`delivery`, which raises demand; People supplies the people).

**Budget and headcount (binding).** £310k / £700k / £1,850k total for FY2026 / FY2027 / FY2028, of which people cost £210k / £400k / £750k and non-people £100k / £300k / £1,100k (COMPANY.md §5.4). Humans at year end 2 / 5 / 10; AI agents 1 / 3 / 6 (COMPANY.md §6.1).

## 2. Org chart

```
Chief Executive Officer (Imogen Hartley, executive)
└── Chief People Officer  (Grace Adeyemi, head)                     Y1
    ├── People Operations Specialist                                Y1 (2nd in Y3)
    │   ├── People Operations Specialist (second)                   Y3
    │   └── People Coordinator                                      Y2
    ├── Talent Acquisition Partner                                  Y2
    │   └── Recruiter                                               Y3
    ├── HR Business Partner                                         Y2
    │   ├── US People Partner                                       Y3
    │   ├── Learning and Culture Specialist                         Y3
    │   └── Reward and People Analytics Associate                   Y3
    └── AI agents (see section 4)
        ├── Recruiting Coordinator Agent        (owner: Talent Acquisition Partner; Y1 interim owner: Chief People Officer)
        ├── Onboarding Concierge Agent          (owner: People Operations Specialist)
        ├── People Analytics Agent              (owner: HR Business Partner)
        ├── HR Helpdesk and Case Triage Agent   (owner: HR Business Partner)
        ├── Offboarding Agent                   (owner: People Operations Specialist)
        └── Engagement Pulse Agent              (owner: Learning and Culture Specialist)
```

Notes on the tree: in Y1 the Chief People Officer and one People Operations Specialist run everything; recruiting is shared with hiring managers and, from Q2 FY2026, a retained agency panel (non-people spend, see section 7). The Reward and People Analytics Associate reports to the HR Business Partner until a Manager-level reward lead is justified (not in plan).

## 3. Roles

Level keys and bands are from COMPANY.md §6.2. Y1/Y2/Y3 are year-end humans. Totals: Y1 = 2, Y2 = 5, Y3 = 10, matching COMPANY.md §6.1.

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief People Officer | head | Chief Executive Officer | 1 | 1 | 1 | £140,000 to £200,000 (cash; plus equity) | Owns people strategy, headcount plan and budget; sits on the Remuneration Committee as executive attendee; approves offers within band and flags out-of-band offers to the CEO; senior employee relations (grievance appeals, dismissals, settlement agreements with `legal`); accountable owner of every HR AI agent until delegated; submits `people.budget_submitted`. |
| People Operations Specialist | consultant | Chief People Officer (Y1 to Y2); People Operations Specialist lead seat is the first hire, no manager-level layer in plan | 1 | 1 | 2 | £55,000 to £70,000 | HRIS data integrity, contracts and written particulars, right-to-work checks, onboarding and offboarding administration, payroll inputs to the bureau, absence and leave, pension and benefits administration, record retention (UK GDPR), policy publication. Y3 second seat adds payroll and benefits specialism. |
| Talent Acquisition Partner | senior_consultant | Chief People Officer | 0 | 1 | 1 | £72,000 to £90,000 | Runs `people.requisition_opened` to `people.offer_accepted`: intake with hiring managers, job ads, agency panel and fee control, structured interview design, shortlist review of agent screening output, offer approval routing, time-to-hire and quality-of-hire reporting, candidate data retention (6 months unless consent). |
| HR Business Partner | senior_consultant | Chief People Officer | 0 | 1 | 1 | £72,000 to £90,000 | Employee relations casework (grievance, disciplinary, capability, flexible working, long-term sickness) under the ACAS Code, performance and calibration cycles, promotion panel secretary, manager coaching, EDI actions, reviews every AI-assisted HR output touching an individual. Covers the US through an employer-of-record partner until the US People Partner starts. |
| People Coordinator | analyst | People Operations Specialist | 0 | 1 | 1 | £38,000 to £48,000 | Interview and induction scheduling, candidate comms, new-starter logistics, document chasing, helpdesk tier 1 queue, compliance training completion chasing, expenses of the people team. |
| Recruiter | consultant | Talent Acquisition Partner | 0 | 0 | 1 | £55,000 to £70,000 | In-house sourcing and first-stage screening for consultant and analyst volume hiring in delivery; graduate and apprentice pipeline; reduces agency use. |
| Learning and Culture Specialist | consultant | HR Business Partner | 0 | 0 | 1 | £55,000 to £70,000 | Learning budget and academy curriculum with `delivery`, mandatory compliance training calendar (with `legal` and `it_security`), engagement survey design and action tracking, internal comms and events, wellbeing programme. |
| US People Partner | senior_consultant | HR Business Partner | 0 | 0 | 1 | £72,000 to £90,000 (London band; US hire at +15% per COMPANY.md §6.2, planning base £92,000) | US employment administration (at-will contracts, state-by-state leave, I-9 and E-Verify, benefits via PEO), US recruiting coordination, US payroll liaison; reports dotted line to the Chief People Officer. |
| Reward and People Analytics Associate | analyst | HR Business Partner | 0 | 0 | 1 | £38,000 to £48,000 | Salary benchmarking against bands, pay-equity and EDI analytics, attrition and engagement dashboards, bonus accrual inputs to Finance, headcount reconciliation with `finance`. |
| **Total humans** |  |  | **2** | **5** | **10** |  |  |

Cost cross-check (loaded = base x 1.28, average headcount; full build-up in `economics.md`): the planning bases used are Chief People Officer £145,000, People Operations Specialist £60,000, Talent Acquisition Partner £82,000, HR Business Partner £85,000, People Coordinator £42,000, Recruiter £62,000, Learning and Culture Specialist £62,000, US People Partner £92,000, Reward and People Analytics Associate £46,000. Start dates in section 5 give base-years of 165.0 (Y1), 312.4 (Y2) and 586.3 (Y3), i.e. people cost of £210k, £400k and £750k (COMPANY.md §5.4).

## 4. AI agents

All agents are registered in the agent register (COMPANY.md §9.4), each has a named human owner, and none of them takes a final decision on hiring, rejection, termination, pay or discipline. Agents run on the `PeopleAgent` class (Y1 one logical agent; further agents are provisioned in 5 days each, COMPANY.md §8 assumption 3).

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Recruiting Coordinator Agent | Talent Acquisition Partner (Chief People Officer until that hire starts in FY2027) | Drafts job ads from requisition data, publishes approved ads, ranks inbound applications against the role scorecard (`external.candidate_applied`), schedules interviews, drafts candidate emails, tracks pipeline and time-to-hire against the 45-day target. | May draft, rank, schedule and chase. May not reject a candidate without human sign-off on the reject list (every reject batch is reviewed by a person and the reason logged); may not send offers or state salary above band; ranking uses only job-related criteria, never name, age, photo, nationality, gender or postcode proxies; candidate data deleted after 6 months. | 1 | 1 | 1 |
| Onboarding Concierge Agent | People Operations Specialist | Builds the Day 1 to Day 90 checklist on `people.offer_accepted`, chases right-to-work documents and signed contracts, triggers equipment and access requests, tracks compliance training (`people.compliance_training_completed`), answers new-starter questions from policy library. | May create tasks, send reminders, publish `people.new_hire_started` only after a human confirms start-day attendance and right-to-work check. May not mark a right-to-work check as passed. | 0 | 1 | 1 |
| People Analytics Agent | HR Business Partner | Monthly headcount, attrition, time-to-hire, offer-acceptance and pay-band compliance reporting; drafts `people.budget_submitted` workings; flags attrition hot spots and promotion-rate disparities for human review. | Read-only on HRIS; individual-level outputs go only to the HR Business Partner and Chief People Officer; no predictive "flight risk" scoring of named individuals shown to line managers; any new model goes through an AI risk review (`product.ai_risk_review_requested`) and a data protection impact assessment. | 0 | 1 | 1 |
| HR Helpdesk and Case Triage Agent | HR Business Partner | First-line answers on leave, sick pay, expenses, benefits and policy; triages cases (grievance, harassment, whistleblowing, health) to the right human within 4 working hours. | Answers from the published policy library only; any message mentioning discrimination, harassment, bullying, whistleblowing, pregnancy, disability or legal action is escalated to the HR Business Partner and never answered by the agent; no advice on an individual's disciplinary outcome. | 0 | 0 | 1 |
| Offboarding Agent | People Operations Specialist | On `people.employee_left` preparation: leaver checklist, exit interview scheduling, handover notes, final-pay inputs, access revocation requests, alumni and reference log. | Drafts and chases only; cannot approve final pay, settlement terms or reference wording (human approval; settlement agreements via `legal`). | 0 | 0 | 1 |
| Engagement Pulse Agent | Learning and Culture Specialist | Runs the quarterly pulse and annual survey, clusters free-text themes, drafts action plans and tracks completion (`people.engagement_survey_completed`). | Reports only at group size 5 or more to protect anonymity; no individual attribution of responses; action plans approved by a human lead before circulation. | 0 | 0 | 1 |
| **Total agents** |  |  | **1** | **3** | **6** |

Check against COMPANY.md §6.1: 1 / 3 / 6. Cumulative by year: Y1 {Recruiting Coordinator}; Y2 adds Onboarding Concierge and People Analytics (Y2 = Recruiting Coordinator + Onboarding Concierge + People Analytics = 3); Y3 adds HR Helpdesk and Case Triage, Offboarding, Engagement Pulse (= 6). The table's Y1, Y2, Y3 columns show the count of that agent in service at year end.

## 5. Hiring plan

### 5.1 Department's own hires

Quarterly for FY2026, then by half-year for FY2027 and FY2028. The 45-day time-to-hire is for external hires; start quarter means first working day. "Trigger" is the event that releases the requisition (headcount approval follows COMPANY.md §9.3: outside-budget headcount needs `executive.headcount_approved`).

| Period | Role | Count | Start (date) | Trigger |
|---|---|---|---|---|
| FY2026 Q1 | Chief People Officer (Grace Adeyemi) | 1 | 2026-01-05 (simulation Day 0) | In place at start of operations; base £145,000 |
| FY2026 Q2 | (no hire; retained agency panel and Recruiting Coordinator Agent carry volume) | 0 | n/a | Series A closes Q2 FY2026 (COMPANY.md §1); hiring pace roughly doubles |
| FY2026 Q3 | People Operations Specialist | 1 | 2026-09-01 | Humans on payroll pass 20 and monthly starters exceed 3; manual onboarding SLA at risk |
| FY2026 Q4 | (no hire) | 0 | n/a | Year-end humans 38; People total 2 |
| FY2027 H1 | Talent Acquisition Partner | 1 | 2027-04-01 | Plan to add 72 net humans in FY2027; agency spend above £25k a quarter for two quarters, or time-to-hire above 55 days |
| FY2027 H2 | HR Business Partner | 1 | 2027-08-01 | Headcount above 70 and open employee-relations cases above 6; US entity live from Q1 FY2027 needs a people case owner |
| FY2027 H2 | People Coordinator | 1 | 2027-10-01 | Interview and induction scheduling above 25 events a month |
| FY2028 H1 | Recruiter | 1 | 2028-04-01 | Planned hires of about 139 in FY2028 (section 5.2); agency fee budget at 60% of cap by end Q1 |
| FY2028 H1 | People Operations Specialist (second) | 1 | 2028-04-01 | Headcount above 170; payroll and benefits administration above one person's capacity (about 1 HR administrator per 90 to 100 employees) |
| FY2028 H2 | Learning and Culture Specialist | 1 | 2028-07-01 | Headcount above 200; engagement score below target two quarters running, or learning budget (non-people) above £150k |
| FY2028 H2 | US People Partner | 1 | 2028-08-01 | US share of revenue 30% in FY2028 (COMPANY.md §1) and US headcount above 25 |
| FY2028 H2 | Reward and People Analytics Associate | 1 | 2028-10-01 | Annual pay review across 230 humans; pay-equity analysis needed for investor and customer assurance |

Sums: Y1 = 1 + 1 = 2; Y2 = 2 + 3 = 5; Y3 = 5 + 5 = 10 (matches COMPANY.md §6.1).

### 5.2 Company hiring volume the department must deliver (derived)

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Year-end humans | 38 | 110 | 230 |
| Average humans | 29 | 74 | 170 |
| Attrition rate (14% FY2026, 11% FY2028 per COMPANY.md §8; 13% FY2027 interpolated at about 12.5%, rounded) | 14% | 13% | 11% |
| Leavers (rate x average humans) | about 4 | about 10 | about 19 |
| Net adds | not derivable from COMPANY.md (opening headcount of 2026-01-05 is not stated); first-year hires planned in `economics.md` | 72 | 120 |
| Gross hires (net adds + leavers) | see `economics.md` | about 82 | about 139 |
| Hires per month, average | | about 7 | about 12 |

Of FY2027 gross hires, about 36 are delivery consultants and analysts in volume campaigns; the delivery head supplies demand through `delivery.hire_requested` and `delivery.capacity_forecast_updated`. Offer acceptance target 85%, so offers made are about 18% above hires.

### 5.3 Capacity rule

One Talent Acquisition Partner plus Recruiting Coordinator Agent covers about 60 hires a year with agency support for senior roles; one Recruiter adds about 50. One People Operations Specialist covers about 100 employees of administration with the Onboarding Concierge Agent. Hires above these ratios trigger the next role in the table.

## 6. Interfaces

Topics are from `core/topics.py` and CONVENTIONS.md section 7.

**People publishes (10):** `people.requisition_opened`, `people.job_posted`, `people.offer_accepted`, `people.new_hire_started`, `people.employee_left`, `people.compliance_training_completed`, `people.engagement_survey_completed`, `people.contractor_engaged`, `people.hire_requested`, `people.budget_submitted`.

**People subscribes to (25):** `executive.hire_requested`, `executive.headcount_approved`, `executive.okrs_set`, `executive.strategy_updated`, `executive.budget_approved`, `executive.crisis_declared`, `finance.budget_cycle_opened`, `finance.hire_requested`, `sales.hire_requested`, `marketing.hire_requested`, `delivery.hire_requested`, `delivery.staffing_requested`, `delivery.capacity_forecast_updated`, `legal.hire_requested`, `legal.policy_update_published`, `legal.regulatory_change_noted`, `it_security.hire_requested`, `it_security.access_provisioned`, `it_security.access_revoked`, `operations.hire_requested`, `operations.workspace_ready`, `product.hire_requested`, `customer_success.hire_requested`, `data.hire_requested`, `external.candidate_applied`.

| Counterpart | They give People | People gives them | Topics |
|---|---|---|---|
| executive | Headcount approvals, OKRs, strategy and budget decisions, crisis instructions (for example a redundancy freeze) | Requisition status, hiring forecast, annual people budget | `executive.headcount_approved`, `executive.hire_requested`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated`, `executive.crisis_declared`; `people.requisition_opened`, `people.budget_submitted` |
| finance | Budget cycle opening, hire requests for the finance team; payroll run approval | Budget submission, payroll inputs, headcount reconciliation, bonus accrual inputs | `finance.budget_cycle_opened`, `finance.hire_requested`; `people.budget_submitted`, `people.new_hire_started`, `people.employee_left` |
| delivery | The largest demand source: hiring requests and staffing demand, capacity forecasts | Candidates, start dates, contractor onboarding, reply to staffing requests with hire or contractor route | `delivery.hire_requested`, `delivery.staffing_requested`, `delivery.capacity_forecast_updated`; `people.requisition_opened`, `people.offer_accepted`, `people.new_hire_started`, `people.contractor_engaged`, `people.hire_requested` |
| sales, marketing, product, customer_success, data, operations, it_security, legal | Hire requests for their teams | Requisition opened, job posted, offer accepted, new hire started | `<dept>.hire_requested`; `people.requisition_opened`, `people.job_posted`, `people.offer_accepted`, `people.new_hire_started` |
| legal | Employment-law updates, regulatory change notes (for example Employment Rights Act commencement, right-to-work rule changes), policy updates; contract templates, IR35 and settlement advice | New starters and leavers for contract and policy acknowledgement; contractor engagements for IR35 check | `legal.policy_update_published`, `legal.regulatory_change_noted`; `people.new_hire_started`, `people.employee_left`, `people.contractor_engaged`, `people.compliance_training_completed` |
| it_security | Access provisioned and revoked confirmations; joiner-mover-leaver controls | Start and leave dates; mandatory security training completion | `it_security.access_provisioned`, `it_security.access_revoked`; `people.new_hire_started`, `people.employee_left`, `people.compliance_training_completed` |
| operations | Workspace readiness (desk, equipment, building access) | Start dates 10 working days ahead; leaver dates | `operations.workspace_ready`; `people.offer_accepted`, `people.new_hire_started`, `people.employee_left` |
| external | Candidate applications | Acknowledgements, interview invitations, outcomes | `external.candidate_applied`; `people.job_posted` |

Service levels People commits to (detailed in `sops.md` and `kpis.md`): requisition opened within 2 working days of an approved hire request; job posted within 3 working days of requisition; offer issued within 2 working days of final-interview decision; contract and written particulars issued before day one; workspace and access request raised 10 working days before start; leaver access revocation request raised the same day notice is accepted (immediately for dismissals).

## 7. Risks and dependencies

| Risk or dependency | Effect | Control or mitigation |
|---|---|---|
| Single point of failure in Y1: the Chief People Officer plus one specialist for 38 humans | Missed starter paperwork, delayed offers, key-person risk | Retained agency panel from Q2 FY2026, Recruiting Coordinator Agent, outsourced payroll bureau and HR advice line, documented SOPs, second person from Q3 FY2026 |
| Time-to-hire above 45 days against a plan that needs about 82 hires in FY2027 | Delivery under-staffed, utilisation target of 70% unreachable (COMPANY.md §4), revenue slippage | Volume campaigns, talent pipeline for consultant and analyst levels, agency fallback with fee cap 20% of first-year base, early Talent Acquisition Partner hire |
| Attrition above plan (14% FY2026) | Replacement cost about 25% of base for consultants and more for managers; client continuity risk | Pulse survey, stay interviews, promotion calibration, pay inside bands, exit-interview analytics reviewed quarterly |
| Biased or opaque AI in recruitment and performance | Equality Act 2010 indirect discrimination claims, UK GDPR Art 22 and ICO enforcement, reputational damage for an AI consultancy | Human decision on every hire, reject and dismissal (COMPANY.md §9.4); documented scorecards; quarterly adverse-impact check by the People Analytics Agent reviewed by the HR Business Partner; DPIA for each HR AI tool; AI risk review via `product.ai_risk_review_requested` for model changes |
| Right-to-work and contractor-status errors | Civil penalties of up to £60,000 per illegal worker (first breach, current rate), IR35 liabilities | Original document check or Home Office online check before day one; checks recorded in HRIS; IR35 determinations via `legal` and `finance` before any `people.contractor_engaged` |
| Employment-law change (Employment Rights framework, flexible working, fire-and-rehire, day-one rights) | Policy and contract drift | Subscription to `legal.regulatory_change_noted` and `legal.policy_update_published`; policy owner per document; annual handbook review |
| Employee data breach (HRIS, payroll, health data, special-category data) | ICO notification within 72 hours (COMPANY.md §9.3), fines, loss of trust | Least-privilege HRIS roles, `it_security` access reviews, retention schedule (candidates 6 months, leavers 6 years for payroll records), agents have no write access to payroll |
| US expansion from Q1 FY2027 | At-will, state leave and wage laws, I-9, benefits mismatch | Employer-of-record or PEO until US People Partner (FY2028), US counsel via `legal`, +15% pay premium (COMPANY.md §6.2) |
| Dependence on `it_security` and `operations` for day-one readiness | Starters without laptop or access | 10-working-day lead time, `operations.workspace_ready` and `it_security.access_provisioned` tracked as start blockers; Onboarding Concierge Agent escalates at 5 days |
| Budget pressure (people cost £210k / £400k / £750k fixed by envelope) | Cannot hire ahead of need | Hiring triggers in section 5.1 are capacity-based; extra headcount needs `executive.headcount_approved` (COMPANY.md §9.3); non-people lines (agency, job boards, HRIS, learning, benefits admin, EAP) flex first |

Non-people spend (£100k / £300k / £1,100k per COMPANY.md §5.4) covers HRIS and payroll bureau fees, job boards and the agency panel, background checks, learning budget, engagement tooling, employee assistance programme, and the US employer-of-record fee from FY2027; the line detail is in `economics.md`.

## 8. Sources

- COMPANY.md §1 (identity, US entity from Q1 FY2027, funding timing)
- COMPANY.md §2 (leverage model, agents under named human owners)
- COMPANY.md §4 (delivery pyramid and utilisation that drive hiring demand)
- COMPANY.md §5.2 (cost lines, loaded cost = base x 1.28, agent cost range)
- COMPANY.md §5.4 (People budget envelope: 210 / 400 / 750 people; 100 / 300 / 1,100 non-people; 310 / 700 / 1,850 total)
- COMPANY.md §6 and §6.1 (humans 2 / 5 / 10 and agents 1 / 3 / 6 for people)
- COMPANY.md §6.2 (levels and salary bands; US +15%)
- COMPANY.md §8 (attrition 14% to 11%, time-to-hire 45 days, agent provisioning 5 days, on-costs 28%, compliance baseline)
- COMPANY.md §9.2 (Chief People Officer: Grace Adeyemi; all heads report to CEO)
- COMPANY.md §9.3 (delegations: new headcount, data breach notification)
- COMPANY.md §9.4 (AI agent governance: no final hiring or termination decisions by agents)
- CONVENTIONS.md §3.1 (blueprint headings) and §7 (topic map, via `core/topics.py`)
