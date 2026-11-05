# IT and Security KPIs

Department: `it_security` (agent class `ItSecurityAgent`). Head: Chief Information Security Officer, Wei Zhang (COMPANY.md §9.2). All figures are modeled assumptions in line with typical industry ranges, not real data. Scope is defensive only: IT operations, information security, identity and access, incident response, certification, vendor risk and AI-agent credential governance.

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| critical_vuln_sla_pct | Critical/high vulnerabilities remediated within SLA | percent | 90 | 95 | 97 | Higher is better | Weekly | Security Engineer (reports to CISO) |
| mttr_critical_incident_hours | Mean time to resolve critical/high incidents | hours | 8 | 6 | 4 | Lower is better | Monthly | Security Engineer / CISO |
| access_provisioning_sla_pct | Joiner/mover access provisioned within SLA (1 working day) | percent | 95 | 97 | 98 | Higher is better | Weekly | IT and Identity Manager |
| leaver_revocation_hours | Leaver access revoked, 95th percentile | hours | 4 | 2 | 1 | Lower is better | Monthly | IT and Identity Manager |
| mfa_coverage_pct | Human accounts with phishing-resistant or app-based MFA | percent | 100 | 100 | 100 | Higher is better | Weekly | IT and Identity Manager |
| agent_credential_compliance_pct | AI agents with named owner, scoped credential and rotation in date | percent | 100 | 100 | 100 | Higher is better | Weekly | CISO (register custodian) |
| endpoint_patch_compliance_pct | Managed endpoints and servers within patch window | percent | 95 | 97 | 98 | Higher is better | Weekly | IT and Identity Manager |
| security_training_completion_pct | Staff completing mandatory security training on time | percent | 95 | 97 | 98 | Higher is better | Monthly | CISO with People |
| security_questionnaire_turnaround_days | Client security questionnaire turnaround, median | days | 3 | 2 | 2 | Lower is better | Monthly | Security and Compliance Analyst (AI-assisted) |
| vendor_assessments_on_time_pct | New and renewing vendors risk-assessed before onboarding/renewal | percent | 90 | 95 | 98 | Higher is better | Monthly | Security and Compliance Analyst |
| certification_milestones_on_track_pct | Certification plan milestones delivered on schedule | percent | 90 | 90 | 90 | Higher is better | Monthly | CISO |
| phishing_simulation_report_rate_pct | Phishing simulation: staff reporting the lure | percent | 50 | 60 | 70 | Higher is better | Quarterly | Security and Compliance Analyst |

Twelve KPIs. `agent.py` exposes the FY2026 targets as `KPIS: list[core.Kpi]` under the same ids (units as above, direction mapped to `higher_is_better`).

## 2. Definitions and formulas

Severity follows CONVENTIONS.md (`low`, `medium`, `high`, `critical`). Vulnerability severity maps CVSS v3.1/v4.0 base score adjusted for exploitability (CISA KEV listing, internet exposure) to the same four levels.

**critical_vuln_sla_pct.** Of critical and high findings (`it_security.vulnerability_found`) whose SLA clock ended in the period, the share closed (fix verified by re-scan, or compensating control approved by the CISO) before the SLA expired. Formula: `closed_in_sla / (closed_in_sla + closed_late + open_past_sla) x 100`. SLAs: critical 7 days (24 hours if on the KEV list or actively exploited), high 30 days. Excludes accepted risks with a signed, time-boxed risk acceptance, which are reported separately. Product-owned findings clock stops on `product.vulnerability_fixed`.

**mttr_critical_incident_hours.** Mean hours from `it_security.incident_detected` (detection timestamp) to `it_security.incident_resolved` (service restored and threat contained) for high and critical incidents closed in the period. Formula: `sum(resolved_at - detected_at) / count`. Sim days are converted at 24 hours per day. Also tracked, not targeted: mean time to detect and mean time to contain. At FY2026 volume (low single-digit high/critical incidents per quarter) the metric is reported with the count and the median alongside.

**access_provisioning_sla_pct.** Access requests for joiners (`people.new_hire_started`), contractors (`people.contractor_engaged`) and movers completed within one working day of an approved request (the day-one standard laptop, identity, MFA and baseline application bundle). Formula: `provisioned_in_sla / total_requests x 100`. Each completion is emitted as `it_security.access_provisioned`. Role-specific elevated access needs manager and data-owner approval and is measured from approval, not request.

**leaver_revocation_hours.** 95th percentile of hours between the employee's leaving time (`people.employee_left`) and confirmed disablement of identity, sessions, tokens, shared-vault entries and device enrolment (`it_security.access_revoked`). Formula: `P95(revoked_at - leave_effective_at)`. Dismissals and gross-misconduct leavers are revoked at or before notification and counted at zero hours; any revocation after the leave time is a control breach and reported to the CISO.

**mfa_coverage_pct.** Active human accounts (staff, contractors, privileged admin) with MFA enforced by conditional access, divided by all active human accounts. Formula: `mfa_enforced / active_human_accounts x 100`. Target is 100%, with zero exceptions beyond a 7-day new-account grace window. Admin and break-glass accounts must use phishing-resistant methods (FIDO2 keys); the metric is reported separately for admins. SMS-only enrolment does not count from FY2027.

**agent_credential_compliance_pct.** Share of registered AI agents (COMPANY.md §9.4, §6.1: 22 / 70 / 150 agents at year end) meeting all four conditions: (1) named accountable human owner in the agent register, (2) credential scoped to least privilege and approved data classes (no shared or human credentials), (3) secret rotated within policy (90 days; 30 days for agents touching client data), (4) access reviewed in the last quarter. Formula: `agents_meeting_all_four / registered_agents x 100`. An unregistered agent found in the estate is a finding and counts as non-compliant. Agent provisioning (5-day standard, COMPANY.md §8) cannot complete without registration.

**endpoint_patch_compliance_pct.** Managed endpoints (laptops, mobile, servers, cloud workloads) with all critical and high OS and application patches applied inside the patch window (critical 14 days, others 30 days) divided by managed devices. Formula: `compliant_devices / managed_devices x 100`. Devices unseen by the MDM for more than 14 days count as non-compliant. This is the evidence measure for the Cyber Essentials Plus 14-day patching requirement.

**security_training_completion_pct.** Staff (including contractors) who completed assigned security awareness and data-protection training by its due date, divided by staff due. Source event: `people.compliance_training_completed`. Formula: `completed_on_time / assigned x 100`. New starters must complete within 14 days of start; overdue accounts are escalated to line managers at day 7 past due and restricted at day 21.

**security_questionnaire_turnaround_days.** Median calendar days from `sales.security_review_requested` to `it_security.security_questionnaire_completed`. Formula: `median(completed_day - requested_day)`. Excludes time awaiting client clarification. Answers drawn from the approved evidence library are drafted by the agent and signed off by a human reviewer before release (COMPANY.md §9.4). Because security review gates deal timing, a breach of 5 days is escalated to the CRO and CISO.

**vendor_assessments_on_time_pct.** Vendors (including AI and data sub-processors) assessed to a risk tier and approved or declined before onboarding or contract renewal, divided by vendors due. Triggers: `operations.vendor_review_requested`, `operations.vendor_approved`, `product.ai_risk_review_requested`. Output: `it_security.vendor_risk_assessed`. Formula: `assessed_before_deadline / vendors_due x 100`. SLAs: critical-tier (client data, production access) 10 working days, standard 5, low 2. Assessing after onboarding counts as a miss.

**certification_milestones_on_track_pct.** Milestones in the certification plan due in the period (ISO 27001 Stage 1/Stage 2 audit and statement of applicability, internal audit, management review, Cyber Essentials Plus technical verification, SOC 2 Type II control design and observation window) that were delivered by their planned date. Formula: `milestones_on_time / milestones_due x 100`. Status changes are published as `it_security.certification_status_updated`. A missed milestone on the ISO 27001 path triggers a CEO notification because the US launch gate depends on it (COMPANY.md §8, item 6).

**phishing_simulation_report_rate_pct.** In each quarterly simulation, the share of targeted staff who report the lure through the report-phish button, divided by those targeted. Formula: `reported / targeted x 100`. Click rate is tracked alongside (target under 8% FY2026, 5% FY2027, 3% FY2028) but never used to discipline individuals.

Security outcomes that are tracked as indicators but are not targeted KPIs (so a good score cannot be gamed by under-reporting): confirmed personal-data breaches (`it_security.data_breach_confirmed`), reportable-to-ICO count, phishing-driven account compromises, and exception/risk-acceptance count. The department commits to zero breaches that reach ICO notification as an outcome, but the KPI set rewards detection and response quality rather than a count that could be suppressed.

## 3. Reporting cadence and data sources

| Cadence | Audience | Content |
|---|---|---|
| Daily | IT and Security team | Open incidents, SLA-breaching vulnerabilities, unprovisioned requests, leavers pending revocation |
| Weekly | CISO | `critical_vuln_sla_pct`, `access_provisioning_sla_pct`, `mfa_coverage_pct`, `agent_credential_compliance_pct`, `endpoint_patch_compliance_pct` |
| Monthly | Executive team (COO, CEO, General Counsel, CRO, CPO) | Full KPI table vs target, incident post-incident review summaries, questionnaire backlog, vendor pipeline |
| Quarterly | Board Audit and Risk Committee | Certification status, risk register top ten, incident and near-miss trends, phishing simulation, agent register attestation, open risk acceptances |
| Annual | Board, auditors | KPI targets reset with budget cycle (`it_security.budget_submitted`), ISMS management review |

Data sources:

| KPI | System of record | Collected by |
|---|---|---|
| critical_vuln_sla_pct | Vulnerability scanner and ticket system (findings, SLA clocks) | Agent, automated daily |
| mttr_critical_incident_hours | Incident register (INC-nnnn records, timestamps) | Agent from bus events and incident tickets |
| access_provisioning_sla_pct, leaver_revocation_hours | Identity provider audit log joined to HR joiner/leaver feed | Agent, automated |
| mfa_coverage_pct | Identity provider conditional-access report | Agent, automated |
| agent_credential_compliance_pct | Agent register, secrets-manager rotation metadata, quarterly access review | Agent; sampled by human monthly |
| endpoint_patch_compliance_pct | MDM and patch-management console | Agent, automated |
| security_training_completion_pct | Learning platform, cross-checked with People (`people.compliance_training_completed`) | Agent |
| security_questionnaire_turnaround_days | Questionnaire tracker linked to `sales.security_review_requested` | Agent |
| vendor_assessments_on_time_pct | Vendor risk register, procurement and contract calendar | Agent with Operations |
| certification_milestones_on_track_pct | ISMS project plan and auditor correspondence | CISO, human-verified |
| phishing_simulation_report_rate_pct | Phishing simulation platform | Security and Compliance Analyst |

Integrity rules: KPI values calculated by the agent are spot-checked monthly by a human against source systems (10% sample); targets are set in the budget cycle and changed only with CISO approval and a dated note; any KPI missing data is reported as "no data", never as 100%.

Review cadence for OKRs: the department sets quarterly OKRs aligned to `executive.okrs_set`. Illustrative FY2026 objectives: (O1) Achieve ISO 27001 certification and Cyber Essentials Plus by year end (KR: Stage 2 passed, zero major nonconformities, `certification_milestones_on_track_pct` at or above 90); (O2) Keep client trust through fast, accurate security assurance (KR: median questionnaire turnaround of 3 days or less, zero deals lost to a security review delay); (O3) Govern every AI agent credential (KR: 100% on `agent_credential_compliance_pct`, rotation automated for all agents by Q3).

## 4. Links to company targets

| Company target (COMPANY.md) | How the department contributes | KPIs |
|---|---|---|
| §8 item 6: US launch gated on ISO 27001 by end FY2026 and SOC 2 Type II in FY2027 before the Q1 FY2027 US office; item 7 compliance baseline (UK GDPR, ISO 27001, Cyber Essentials Plus FY2026, SOC 2 Type II FY2027) | Certification delivery and the control evidence behind it | `certification_milestones_on_track_pct`, `endpoint_patch_compliance_pct`, `mfa_coverage_pct`, `security_training_completion_pct` |
| §5.1 revenue of £6.0m / £19.5m / £46.2m and §5.3 sales cycle of 75 days (70 days FY2028) | Fast security review removes a common stall in enterprise procurement; faster questionnaires protect the 75-day cycle and the win rate of 30% | `security_questionnaire_turnaround_days` |
| §5.1 net revenue retention (115% / 118%) and Keep ARR (£1.5m / £6.5m / £17.0m) | Clients renew managed-ops retainers only if their data and the agents running on it are demonstrably safe | `agent_credential_compliance_pct`, `mttr_critical_incident_hours`, `critical_vuln_sla_pct` |
| §6.1 AI agents (22 / 70 / 150) and §9.4 governance (named owner, least privilege, agent register, no regulator notification by agents) | Register custody and credential governance scale with agent count; 5-day agent provisioning (§8 item 3) depends on the access process | `agent_credential_compliance_pct`, `access_provisioning_sla_pct` |
| §6.1 humans (38 / 110 / 230) and §8 item 3 (time-to-hire 45 days) | Day-one access for every joiner so utilisation of 70% is not lost to waiting; clean revocation for attrition of 14% falling to 11% | `access_provisioning_sla_pct`, `leaver_revocation_hours` |
| §9.3 customer data breach notification (ICO within 72 hours, General Counsel with CISO and CEO) | Fast detection and resolution give the decision-makers inside-72-hour evidence; agents do not notify regulators | `mttr_critical_incident_hours` and the breach indicators |
| §5.4 department envelope: £460k / £920k / £2,300k (people £260k / £470k / £900k; non-people £200k / £450k / £1,400k) and §6.1 headcount 2 / 5 / 9 humans, 2 / 4 / 8 agents | Targets are sized to be achievable with the funded team; cost of assurance falls as a percentage of revenue (about 7.7% FY2026, 4.7% FY2027, 5.0% FY2028 of revenue) | All KPIs; vendor and certification KPIs drive the non-people budget |
| §8 item 8 no client concentration above 15% | Security incidents at one large client are contained by tenant-level segregation; reported inside incident metrics | `mttr_critical_incident_hours` |

Cost-of-assurance ratio (derived, reported annually, not a targeted KPI): department total budget divided by revenue = 460 / 6,000 = 7.7%; 920 / 19,500 = 4.7%; 2,300 / 46,200 = 5.0% (COMPANY.md §5.1, §5.4). The FY2028 uptick reflects US expansion (SOC 2 scope, US data residency, 24x7 monitoring).
