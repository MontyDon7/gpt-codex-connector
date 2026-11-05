# IT and Information Security Economics

> All figures are modeled assumptions in line with typical industry ranges, not real data. Facts are taken from COMPANY.md and cited inline. Money is GBP and ex-VAT unless stated. Owner: Wei Zhang, Chief Information Security Officer (COMPANY.md §9.2). Role titles, bases and start dates follow `blueprint.md` sections 3 and 5; KPI ids follow `kpis.md`; procedures and constants follow `sops.md`.

## 1. Budget

Department scope: IT operations, identity and access, security operations and incident response, GRC (ISO 27001, Cyber Essentials Plus, SOC 2 Type II), vendor risk, client assurance, vulnerability management and AI-agent credential governance. IT and Security is an operating-expense department, not cost of revenue (COMPANY.md §5.1). Laptop and hardware purchases, office network and facilities sit with Operations (see section 4); cyber insurance premium sits with Finance; this department supplies the underwriting evidence.

### 1.1 Budget by line (£k)

| Line | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| **People (loaded, see section 2)** | **260** | **470** | **900** |
| AI agents: compute, model usage and licences (2 / 4 / 8 agents at year end) | 40 | 70 | 135 |
| Managed detection and response, EDR and logging/SIEM (24x7 incl. US from FY2028) | 40 | 85 | 310 |
| Identity provider, SSO, MDM, password manager, secrets vault and privileged access | 30 | 55 | 170 |
| Certification and audit fees: ISO 27001 (Stage 1/2, surveillance), Cyber Essentials Plus, SOC 2 Type II, readiness consultancy | 40 | 105 | 250 |
| Penetration testing (CREST-accredited) and red-team exercises | 20 | 40 | 105 |
| Vulnerability scanning, attack-surface and cloud posture tooling | 10 | 25 | 95 |
| Security awareness training and phishing simulation | 6 | 12 | 28 |
| Incident response and forensics retainer | 10 | 18 | 55 |
| GRC, trust-centre and vendor-risk tooling | 0 | 25 | 55 |
| US data residency, log retention, backup and disaster-recovery security | 0 | 0 | 120 |
| Contractor bridge (security engineering cover while roles are open) | 0 | 0 | 40 |
| Training, certifications and professional memberships (CISSP, ISACA, CREST) | 4 | 10 | 25 |
| Contingency (unallocated, CISO-held; spend above £50k follows COMPANY.md §9.3) | 0 | 5 | 12 |
| **Non-people total** | **200** | **450** | **1,400** |
| **Total (people + non-people)** | **460** | **920** | **2,300** |

Check: non-people FY2026 40+40+30+40+20+10+6+10+0+0+0+4+0 = 200; FY2027 70+85+55+105+40+25+12+18+25+0+0+10+5 = 450; FY2028 135+310+170+250+105+95+28+55+55+120+40+25+12 = 1,400. Totals: 260+200 = 460; 470+450 = 920; 900+1,400 = 2,300.

### 1.2 Ratios

| Ratio | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Revenue (COMPANY.md §5.1), £k | 6,000 | 19,500 | 46,200 |
| Department cost as % of revenue (cost of assurance) | 7.7% | 4.7% | 5.0% |
| Department cost as % of total company cost (§5.2: 7.5m / 17.8m / 39.0m) | 6.1% | 5.2% | 5.9% |
| Average company humans (29 / 74 / 170) per average department human (2.0 / 4.0 / 7.75) | 14.5 | 18.5 | 21.9 |
| Department cost per average company human, £k | 15.9 | 12.4 | 13.5 |
| Non-people share of department cost | 43% | 49% | 61% |

The FY2028 non-people step-up is the US launch (24x7 monitoring, US data residency, a second set of audits) and a security estate that grows with 150 agents (§6.1). The FY2026 cost-of-assurance ratio is high because certification is a fixed cost carried by small revenue.

## 2. Headcount cost build-up

Loaded cost = base salary x 1.28 (employer NI, pension, benefits, bonus accrual; COMPANY.md §5.2, §8 item 5). Base salaries sit inside the COMPANY.md §6.2 bands in `blueprint.md` section 3. Average FTE is weighted by start quarter (a start in a quarter counts for the whole of that quarter's remaining quarters: Q1 start 1.00, Q2 start 0.75, Q3 start 0.50). No US-based hire is included (+15% uplift not applied; blueprint section 3).

### 2.1 FY2026 (year-end humans 2; average 2.0 FTE)

| Role | Level key | Band (£) | Base (£k) | Avg FTE | Base cost (£k) | Loaded (£k) |
|---|---|---|---|---|---|---|
| Chief Information Security Officer | head | 140,000 to 200,000 | 140 | 1.00 | 140.0 | 179.2 |
| Security and IT Operations Specialist (starts Q1, 2026-02-02) | consultant | 55,000 to 70,000 | 63 | 1.00 | 63.0 | 80.6 |
| **Total** | | | | **2.00** | **203.0** | **259.8** |

### 2.2 FY2027 (year-end humans 5; average 4.0 FTE)

| Role | Level key | Band (£) | Base (£k) | Avg FTE | Base cost (£k) | Loaded (£k) |
|---|---|---|---|---|---|---|
| Chief Information Security Officer (rebased 2027-01-01) | head | 140,000 to 200,000 | 150 | 1.00 | 150.0 | 192.0 |
| GRC Lead (starts Q2, 2027-04-01) | manager | 92,000 to 115,000 | 96 | 0.75 | 72.0 | 92.2 |
| Senior Security Specialist (Engineering) (starts Q2, 2027-04-01) | senior_consultant | 72,000 to 90,000 | 78 | 0.75 | 58.5 | 74.9 |
| Security and IT Operations Specialist | consultant | 55,000 to 70,000 | 65 | 1.00 | 65.0 | 83.2 |
| IT Support Analyst (starts Q3, 2027-07-01) | analyst | 38,000 to 48,000 | 42 | 0.50 | 21.0 | 26.9 |
| **Total** | | | | **4.00** | **366.5** | **469.1** |

### 2.3 FY2028 (year-end humans 9; average 7.75 FTE)

| Role | Level key | Band (£) | Base (£k) | Avg FTE | Base cost (£k) | Loaded (£k) |
|---|---|---|---|---|---|---|
| Chief Information Security Officer (SOC 2 Type II attained) | head | 140,000 to 200,000 | 170 | 1.00 | 170.0 | 217.6 |
| GRC Lead | manager | 92,000 to 115,000 | 100 | 1.00 | 100.0 | 128.0 |
| Security Engineering Lead (starts Q1, 2028-01-03) | manager | 92,000 to 115,000 | 108 | 1.00 | 108.0 | 138.2 |
| Senior Security Specialist (Engineering) no. 1 | senior_consultant | 72,000 to 90,000 | 84 | 1.00 | 84.0 | 107.5 |
| Senior Security Specialist (Engineering) no. 2 (starts Q2, 2028-04-03) | senior_consultant | 72,000 to 90,000 | 84 | 0.75 | 63.0 | 80.6 |
| Security and IT Operations Specialist no. 1 | consultant | 55,000 to 70,000 | 70 | 1.00 | 70.0 | 89.6 |
| Security and IT Operations Specialist no. 2 (starts Q3, 2028-07-03) | consultant | 55,000 to 70,000 | 70 | 0.50 | 35.0 | 44.8 |
| Security Operations Specialist (starts Q3, 2028-07-03) | consultant | 55,000 to 70,000 | 60 | 0.50 | 30.0 | 38.4 |
| IT Support Analyst | analyst | 38,000 to 48,000 | 44 | 1.00 | 44.0 | 56.3 |
| **Total** | | | | **7.75** | **704.0** | **901.1** |

Year-end headcount reconciles to the blueprint role table: FY2026 1+1 = 2; FY2027 1+1+1+1+1 = 5; FY2028 1+1+1+2+2+1+1 = 9 (CISO, GRC Lead, Security Engineering Lead, two Senior Security Specialists (Engineering), two Security and IT Operations Specialists, Security Operations Specialist, IT Support Analyst).

### 2.4 AI agent cost (inside the non-people agent line)

Fully loaded agent cost (compute, model usage, licences, monitoring) is £20k to £35k per agent-year (COMPANY.md §5.2) and falls about 15% a year (§8 item 4).

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Agents at year end (blueprint section 4) | 2 | 4 | 8 |
| Average agents in year (start quarters) | 1.75 | 3.0 | 6.0 |
| Agent line, £k | 40 | 70 | 135 |
| Implied cost per average agent-year, £k | 22.9 | 23.3 | 22.5 |

FY2026: ItSecurityAgent from Q1 and Access Lifecycle Agent from Q2. FY2027: Vulnerability and Patch Agent and AI Agent Credential Governance Agent in H1. FY2028: Vendor Risk, Compliance Evidence Collector, Security Alert Triage and Phishing Triage agents across Q1 to Q3. Security agents carry more than average monitoring and logging overhead, which offsets the 15% unit cost decline.

## 3. Pricing and unit economics

The department sells nothing externally and has no price list. Its economics are cost of assurance and cost per controlled event, each allocated from the build-up above (management allocation, not additional budget).

### 3.1 Cost per controlled event

| Unit | Volume assumption (FY2026 / FY2027 / FY2028) | Cost allocation (£k, FY2026 / FY2027 / FY2028) | Cost per unit |
|---|---|---|---|
| Client security questionnaire (SOP-IT_SECURITY-07) | 40 / 130 / 260 (about 6% / 11% / 11.5% of 640 / 1,200 / 2,267 leads, §5.3) | 31 / 64 / 66: CISO 15% then GRC Lead 50% and CISO 5%, then GRC Lead 40%, plus agent drafting | about £780 / £490 / £255 |
| Joiner or leaver access event (SOP-IT_SECURITY-04 and 05) | 46 / 92 / 158 (joiners 42 / 82 / 139 and leavers 4 / 10 / 19, from §6.1 headcount and attrition 14% to 11%) | 55 / 75 / 104: Security and IT Operations Specialist, IT Support Analyst share and Access Lifecycle Agent | about £1,200 / £815 / £660 |
| Registered AI agent governed (SOP-IT_SECURITY-10) | 22 / 70 / 150 agents at year end (§6.1) | 18 / 69 / 119: CISO 10%, Senior Security Specialist (Engineering) 40% and governance agent from FY2027 | about £810 / £990 / £790 |
| Average human protected (endpoint, identity, MDR tooling) | 29 / 74 / 170 average humans | tooling lines 80 / 165 / 575 (EDR/MDR, identity, vulnerability) | about £2.8k / £2.2k / £3.4k |

Reading: questionnaire cost falls about two thirds as the GRC Lead and answer-library automation arrive, supporting the 3-day turnaround KPI (`security_questionnaire_turnaround_days`, target 3 / 2 / 2 days) without adding people per questionnaire. Per-event access cost falls as the agent executes the standard bundles. Cost per governed agent is flat at about £0.8k to £1.0k because governance scales with agent count only after the dedicated specialist and agent are in place.

### 3.2 Cost of assurance versus risk

| Item | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Department cost, £k | 460 | 920 | 2,300 |
| Cost of assurance (% of revenue) | 7.7% | 4.7% | 5.0% |
| Certification and audit fees as % of department cost | 8.7% | 11.4% | 10.9% |
| Penetration testing and IR retainer, £k | 30 | 58 | 160 |
| Revenue gated by security review: Keep ARR at year end (§5.1), £m | 1.5 | 6.5 | 17.0 |

The commercial case rests on two facts from COMPANY.md: US launch is gated on ISO 27001 by end FY2026 and SOC 2 Type II in FY2027 (§8 item 6), and enterprise procurement commonly stalls on security review (kpis.md section 4). A one-month slip in ISO 27001 certification costs little in the budget but puts the launch gate and the Keep ARR ramp at risk.

### 3.3 Make or buy: security operations

| Option | FY2028 cost, £k | Coverage | Choice |
|---|---|---|---|
| Managed detection and response retainer plus Security Operations Specialist | 310 (line) plus 38 (half-year of specialist) | 24x7 with US hours, human on-call rota | Chosen |
| In-house 24x5 analyst rota (about 5 FTE) | about 5 x 77 = 385 base-loaded (60 base x 1.28 each) | 24x5 only | Rejected: hiring in London 45 days per role, key-person risk, above the people envelope |

The retainer is bought in FY2026 to cover the thin team (blueprint section 7, key-person risk) and scaled with the estate.

### 3.4 Sensitivities (effect on the department, £k unless stated)

| Driver | Change | Effect |
|---|---|---|
| GRC Lead hire slips one quarter (45-day time-to-hire, §8 item 3) | Start moves from Q2 to Q3 FY2027 | Saves about 23 (0.25 FTE x 92) but CISO carries SOC 2 evidence and questionnaires; `certification_milestones_on_track_pct` and turnaround at risk |
| Agent count +20% above plan | +4 agents at year-end FY2027 to 74 | About +24 to +26 in the agent line at £23k each, and +6% register workload |
| SOC 2 Type II observation window extended by 3 months | FY2027 | Auditor and consultancy fees +25 to +40; US launch gate slips |
| ISO 27001 Stage 2 fails with major nonconformity | FY2026 | Re-audit fee about 15 to 20 and consultancy +10; certificate slips past year end |
| Penetration testing scope doubles (US region, more client environments) | FY2028 | +50 to +80 in the pentest line |
| Critical incident with forensic retainer drawn down | any year | +25 to +60 beyond retainer; funded from contingency, above £50k needs CFO (§9.3) |
| Security hire at US +15% uplift (§6.2) | FY2028 H2 | +15% on base: about +10 on a £70k base (loaded +13); not in plan |

## 4. Assumptions

1. Loaded cost is base x 1.28 (COMPANY.md §5.2, §8 item 5). Base salaries rise about 3% a year for continuing roles; the CISO is rebased from £140k to £150k on 2027-01-01 and to £170k in FY2028 on SOC 2 Type II attainment (blueprint section 3).
2. FY2026 average FTE of 2.00 counts the Security and IT Operations Specialist (start 2026-02-02) as a Q1 start for the full year (quarter-weighting convention used for every hire); a day-count weighting would give 1.92 FTE and £253k loaded, a £7k difference that is absorbed by recruitment and onboarding cost in the same year.
3. Humans (38 / 110 / 230 at year end, 29 / 74 / 170 average) and agents (22 / 70 / 150) are taken from COMPANY.md §6 and §6.1; the department does not set them.
4. Hiring follows the people chain: 45-day human time-to-hire and 5-day agent provisioning (§8 item 3); requisitions are opened a quarter ahead (blueprint section 5).
5. The agent line is fully loaded at £20k to £35k per agent-year (§5.2) falling about 15% a year (§8 item 4), offset by monitoring overhead.
6. Laptops and hardware kits are bought from the Operations hardware budget (blueprint section 5 hardware kits with Operations); only licences, MDM, EDR and security tooling are in this budget. Cyber insurance premium sits with Finance.
7. Certification fees assume ISO 27001 Stage 1 in Q3 and Stage 2 by end FY2026, Cyber Essentials Plus in FY2026, SOC 2 Type II observation window from Q1 FY2027 (six months minimum) and annual surveillance audits thereafter (blueprint section 1, §8 items 6 and 7).
8. Questionnaire, joiner, leaver and vendor volumes are derived from funnel and headcount facts (§5.3, §6.1, attrition in §8 item 3) with percentages stated in section 3.1; they are volume assumptions, not forecasts.
9. Allocations in section 3 are management allocations for unit economics only and do not change the budget.
10. The contingency line is CISO-held and small; any non-budgeted spend above £50k needs the CFO and above £250k the CEO (§9.3). Headcount outside this plan needs `executive.headcount_approved`.
11. Agents may not approve spend above £10,000 (§9.4; blueprint section 1).

## 5. Reconciliation to COMPANY.md

COMPANY.md §5.4 it_security row (£k): people 260 / 470 / 900, non-people 200 / 450 / 1,400, total 460 / 920 / 2,300. COMPANY.md §6.1: humans 2 / 5 / 9, agents 2 / 4 / 8.

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| People per section 2 (computed), £k | 259.8 | 469.1 | 901.1 |
| People as shown in section 1 (rounded to envelope), £k | 260 | 470 | 900 |
| Non-people per section 1, £k | 200 | 450 | 1,400 |
| **Department total (this document), £k** | **460** | **920** | **2,300** |
| COMPANY.md §5.4 total, £k | 460 | 920 | 2,300 |
| Delta, £k | 0 | 0 | 0 (computed 2,301.1 vs 2,300, within £5k) |

Headcount reconciles to COMPANY.md §6.1: humans 2 / 5 / 9 and agents 2 / 4 / 8, matching `blueprint.md` sections 3 and 4. KPI targets in `kpis.md` are sized to this funded team, and the cost-of-assurance ratios (7.7% / 4.7% / 5.0%) match `kpis.md` section 4. The department's totals roll into the §5.2 and §5.4 company totals (£7.5m / £17.8m / £39.0m).
