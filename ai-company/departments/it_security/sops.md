# IT and Security Standard Operating Procedures

Department: `it_security` (agent class `ItSecurityAgent`). Head: Chief Information Security Officer (Wei Zhang, COMPANY.md §9.2). Headcount: 2 humans and 2 AI agents in FY2026, 5 and 4 in FY2027, 9 and 8 in FY2028 (COMPANY.md §6.1). Budget: £460k / £920k / £2,300k (COMPANY.md §5.4). Management system scope: ISO 27001 and Cyber Essentials Plus in FY2026, SOC 2 Type II in FY2027 before US launch (COMPANY.md §2, §9). All procedures are defensive. All SLAs are modeled assumptions.

Common conventions used in every SOP:
- Severity scale (body key `severity`): `low`, `medium`, `high`, `critical`. Critical = confirmed compromise of client data, domain-admin or production control plane, or loss of the Slack/Google Workspace tenant. High = confirmed compromise of a single privileged identity, ransomware precursor, or exploited internet-facing vulnerability. Medium = contained phishing click, malware on a managed laptop. Low = policy deviation, blocked attack.
- Roles: CISO (Wei Zhang), Security and IT Operations Specialist (human, in post from Q1 FY2026), Senior Security Specialist (Engineering) (human, from Q2 FY2027), GRC Lead (human, from Q2 FY2027); titles as in `blueprint.md` section 3. AI agents: `ItSecurityAgent` (triage, evidence, workflow) and the Access Lifecycle Agent (joiner/mover/leaver execution), both registered in the agent register (COMPANY.md §9.4). Until the FY2027 hires land, the CISO and Security and IT Operations Specialist cover all [human] steps, with the CISO covering the Senior Security Specialist (Engineering) and GRC Lead duties; the CISO is the named escalation owner throughout.
- Agents may draft, analyse, monitor and propose. Agents may not notify regulators, sign contracts, approve payments above £10,000 or make final hiring or termination decisions (COMPANY.md §9.4). Every SOP step that would cross that line is marked [human].
- Time is measured in simulation days for message scheduling (`delay_days`) and in business hours/clock hours in SLAs. "Clock hours" ignore weekends; "business hours" are 09:00-17:30 UK.
- Evidence for every SOP is stored in the ISMS evidence register (ticket id, date, approver) and sampled quarterly by the GRC Lead for ISO 27001 internal audit.

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-IT_SECURITY-01 | Security alert triage and incident declaration | `external.security_alert` | CISO | Triage in 30 min (critical/high), 4 clock hours (medium), 1 business day (low); declaration decision in 1 hour |
| SOP-IT_SECURITY-02 | Personal data breach assessment and regulator liaison | `legal.regulator_notification_filed` (follows `it_security.data_breach_confirmed`) | CISO with General Counsel | Breach assessment in 12 clock hours; ICO notification by Legal within 72 hours of awareness; closure report in 10 business days |
| SOP-IT_SECURITY-03 | Crisis mode response | `executive.crisis_declared` | CISO | Crisis bridge open in 30 min; first situation report in 2 hours; then every 4 hours |
| SOP-IT_SECURITY-04 | Joiner and contractor access provisioning | `people.new_hire_started`, `people.contractor_engaged` | Security and IT Operations Specialist | Laptop and baseline access ready before day 1 09:00; contractor access in 2 business days |
| SOP-IT_SECURITY-05 | Leaver access revocation | `people.employee_left` | Security and IT Operations Specialist | Privileged accounts disabled in 1 hour, all access in 4 hours of last working time; verified in 1 business day |
| SOP-IT_SECURITY-06 | Vulnerability intake, triage and release security gate | `product.release_shipped`, `product.vulnerability_fixed` | Senior Security Specialist (Engineering) (CISO until hired) | Critical 7 days (24 hours if actively exploited), high 30 days, medium 60 days, low 90 days to remediate; verify fix in 2 business days |
| SOP-IT_SECURITY-07 | Customer security questionnaire and security review | `sales.security_review_requested` | GRC Lead (CISO until hired) | Standard questionnaire 3 business days; bespoke or on-site audit request 4 business days |
| SOP-IT_SECURITY-08 | Third-party and AI vendor risk assessment | `operations.vendor_review_requested`, `operations.vendor_approved` | GRC Lead (CISO until hired) | Tier 1: 10 business days; Tier 2: 5 business days; Tier 3: 2 business days; onboarding controls verified in 5 business days of approval |
| SOP-IT_SECURITY-09 | Certification and compliance programme | `legal.regulatory_change_noted`, `legal.policy_update_published`, `people.compliance_training_completed`, `operations.continuity_test_completed` | GRC Lead (CISO until hired) | Regulatory impact assessment in 10 business days; policy attestation 95% in 30 days; certification status published monthly |
| SOP-IT_SECURITY-10 | AI agent register and credential governance | `product.ai_risk_review_requested` | CISO | Security review in 5 business days; credential rotation 90 days; quarterly register review |
| SOP-IT_SECURITY-11 | Annual budget cycle and department planning | `finance.budget_cycle_opened`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated` | CISO | Budget submitted by finance deadline; plan re-baselined in 10 business days of approval |
| SOP-IT_SECURITY-12 | Security hiring request | Capacity trigger (schedule: monthly review) | CISO | Request raised within 5 business days of trigger breach |

## SOP-IT_SECURITY-01: Security alert triage and incident declaration

**Owner**: CISO (Wei Zhang); on-call rota: Security and IT Operations Specialist then CISO.
**Trigger**: `external.security_alert` (sender `external`). Sources: Google Workspace alert centre, endpoint detection and response (EDR) console, cloud audit log detections, phishing mailbox reports, a client or the NCSC reporting a concern, threat-intelligence feeds.
**Inputs**: alert body (`summary`, `severity`, optional `client_id`, `asset`, `source`, `indicator`), asset inventory, identity logs, EDR telemetry, current client engagement list (to learn whether client data is in scope).

### Steps
1. [agent] Ingest the alert, deduplicate against open incidents using asset plus indicator, and create a ticket `INC-<year>-<seq>` with initial severity from the alert body.
2. [agent] Enrich: pull last 24 hours of sign-ins for the identity, EDR process tree for the host, mailbox rule changes, and cloud audit events; attach to the ticket.
3. [agent] Classify against the playbook library (phishing, credential compromise, malware, exposed secret, data exposure, vulnerability exploitation, availability/denial of service, insider misuse, third-party/supplier incident). Propose a severity and recommended containment.
4. [human] Security and IT Operations Specialist validates the classification within the triage SLA, confirms or changes severity, and records the decision.
5. [human] If true positive at medium or above, contain: isolate host via EDR, disable or reset the identity and revoke refresh tokens and API keys, block the indicator at the mail gateway and DNS filter. Containment is logged with timestamp and operator.
6. [human] Declare an incident when any of: confirmed unauthorised access, malware execution on a managed asset, any exposure of client or personal data, or severity high or critical. Name the incident commander (CISO by default) and open a private incident channel.
7. [agent] On declaration, emit `it_security.incident_detected` to the leadership and operational audience; for client data in scope set `client_id` so Customer Success and Delivery can brief the engagement lead. Start the incident timeline and decision log.
8. [human] CISO assesses whether personal data is involved. If yes or unknown for client data, go to SOP-IT_SECURITY-02. If severity is critical and business operations are materially threatened, CISO recommends crisis declaration to the CEO, who owns `executive.crisis_declared` (SOP-IT_SECURITY-03).
9. [human] Eradicate and recover: rebuild or restore from known-good, rotate all secrets in the blast radius, re-enable accounts with MFA re-enrolment, monitor for 7 days.
10. [human] Hold a blameless post-incident review within 5 business days; record root cause, detection gap, control changes and owners with due dates.
11. [agent] When the CISO marks recovery complete and the review is booked, emit `it_security.incident_resolved` with root cause and lessons-learned reference; update the incident metrics (mean time to detect, mean time to contain, mean time to recover).

### Outputs and messages
- `it_security.incident_detected` (recipient `*`): `incident_id`, `severity`, `summary`, `client_id` (if applicable), `personal_data_involved` (bool or `unknown`), `containment_status`, `incident_commander`, `due_day` (next update).
- `it_security.incident_resolved` (recipient `*`): `incident_id`, `severity`, `summary`, `root_cause`, `time_to_contain_hours`, `time_to_resolve_hours`, `client_id`, `follow_up_actions` (count).
- Ticket, timeline and evidence in the ISMS evidence register; post-incident review document.

### SLA and controls
- Triage: 30 minutes for critical or high, 4 clock hours for medium, 1 business day for low. Incident declaration decision within 1 hour of confirmed true positive.
- `incident_detected` emitted within 1 hour of declaration. Leadership update cadence: every 4 hours for critical, every business day for high.
- Controls: two-person rule for destructive containment on production systems; all containment actions logged; evidence preserved (disk image or log export hashed with SHA-256) before rebuild; incident register reviewed monthly by the CISO and quarterly by the Audit and Risk Committee; tabletop exercise twice a year.
- ISO 27001 Annex A mapping (2022): A.5.24-A.5.28 incident management, A.8.15 logging, A.8.16 monitoring.

### Exceptions and escalation
- Alert cannot be validated within SLA: escalate to the CISO, who may declare provisionally. A provisional declaration is downgraded within 24 hours if disproved.
- CISO unavailable: the Security and IT Operations Specialist acts as incident commander and informs the CEO; if both unavailable, the Chief Operating Officer holds authority to isolate systems.
- Alert involves a person (insider): inform General Counsel and Chief People Officer before any employee-facing action; no unilateral disciplinary steps.
- Alert involves an AI agent: suspend the agent credentials immediately under SOP-IT_SECURITY-10 and notify the accountable human owner.

## SOP-IT_SECURITY-02: Personal data breach assessment and regulator liaison

**Owner**: CISO, jointly with the General Counsel (Callum Fraser). The CEO approves notification content per the delegation of authority (COMPANY.md §9.3).
**Trigger**: An incident under SOP-IT_SECURITY-01 where personal data may be affected; this SOP then produces `it_security.data_breach_confirmed`. The inbound trigger topic for the closing phase is `legal.regulator_notification_filed` (sender `legal`, recipients include `it_security`).
**Inputs**: incident ticket, data map and record of processing activities (RoPA), affected client contracts and data processing agreements (DPA), client contact list, forensic findings, Legal's draft ICO notification.

### Steps
1. [human] Within 12 clock hours of awareness, the CISO and General Counsel establish the facts: what personal data, whose (client employees, candidates, our staff), how many data subjects, how it was exposed, whether it was encrypted, whether exposure is ongoing.
2. [agent] Pull the matching RoPA entries and DPA clauses, list affected clients and contractual notification windows (typically 24 to 72 hours for processors), and draft a data-subject and risk summary for review.
3. [human] Decide whether the event is a personal data breach under UK GDPR Article 4(12). If yes, record the "awareness" timestamp; the 72-hour ICO clock under UK GDPR Article 33 runs from that moment.
4. [agent] On the CISO's confirmation, emit `it_security.data_breach_confirmed` to Legal, Executive and Customer Success with the facts known. Include `hours_since_awareness` so recipients can track the 72-hour limit.
5. [human] General Counsel decides on ICO notification and Article 34 notice to data subjects (high risk to individuals). Where Lumenhall is processor, notify the controller client without undue delay per the DPA. Agents never notify regulators (COMPANY.md §9.4).
6. [human] Customer Success and the engagement lead notify affected clients in agreed wording; CISO provides technical briefing. Insurance broker (cyber policy) notified by the CFO within the policy notice period.
7. [agent] Upon receiving `legal.regulator_notification_filed`, record the filing reference and date in the incident ticket, compute elapsed hours from awareness against 72, and open follow-up tasks for ICO queries (target answer in 2 business days).
8. [human] Remediate root cause, offer affected individuals monitoring where warranted, and update the DPIA and RoPA.
9. [human] Closure report to the Audit and Risk Committee within 10 business days of containment, covering timeline, decisions, ICO correspondence and control changes.
10. [agent] Feed completion into `it_security.incident_resolved` (SOP-IT_SECURITY-01 step 11) with `regulator_filing_ref`.

### Outputs and messages
- `it_security.data_breach_confirmed` (recipient `*`): `incident_id`, `severity`, `summary`, `client_id`, `data_categories` (list), `data_subjects_estimate` (int), `hours_since_awareness`, `due_day` (ICO deadline day).
- Task for the incident ticket: ICO follow-up with owner and `due_day`.
- Indirectly feeds `it_security.incident_resolved` with `regulator_filing_ref`.

### SLA and controls
- Assessment inside 12 clock hours; `data_breach_confirmed` emitted within 2 hours of CISO confirmation; ICO notification within 72 hours of awareness (Legal owns); closure report in 10 business days.
- Controls: breach log maintained even for breaches not notified, with reasoning (UK GDPR Article 33(5)); notification text reviewed by two people; evidence handling and chain of custody maintained; annual breach simulation with Legal.
- Delegations: breach notification decisions rest with General Counsel with CISO and CEO (COMPANY.md §9.3).

### Exceptions and escalation
- Scope unknown at hour 48: General Counsel files a phased notification to ICO to avoid missing the 72-hour limit; CISO updates as facts firm up.
- Breach originates at a supplier: treat as controller-to-processor chain, request supplier incident report within 24 hours, and open a vendor risk reassessment (SOP-IT_SECURITY-08).
- Filing delayed beyond 60 hours without a decision: automatic escalation to CEO and General Counsel by the agent and a flag on the incident record.

## SOP-IT_SECURITY-03: Crisis mode response

**Owner**: CISO (technical lead); Crisis commander is the CEO (Imogen Hartley).
**Trigger**: `executive.crisis_declared` (broadcast by the Executive department).
**Inputs**: crisis declaration body (`summary`, `severity`, scope), open incident register, business continuity plan, system recovery priorities, privileged access inventory.

### Steps
1. [agent] On receipt, freeze non-essential change: block merges to protected infrastructure branches, pause scheduled access reviews and low-priority vendor assessments, and notify the on-call rota.
2. [human] CISO opens the crisis bridge within 30 minutes, nominates a deputy, and confirms with the CEO which systems must stay online (client delivery platform, email, finance systems).
3. [human] Apply emergency access controls: step-up authentication for administrators, time-boxed break-glass accounts (maximum 4 hours, dual approval, session recorded), temporary tightening of conditional access rules.
4. [agent] Compile the situation report every 4 hours: incidents open, systems affected, containment status, pending decisions, regulatory clocks running. Distribute to the crisis commander.
5. [human] Coordinate with Operations on the continuity plan invocation, with Legal on regulator and client communications, with Customer Success on client holding statements.
6. [human] Stand down only on the CEO's instruction: remove break-glass accounts, restore standard conditional access, restore change windows, and run a recovery verification checklist.
7. [agent] Close the crisis log, create follow-up tasks (lessons learned, control changes, evidence for auditors) and update the risk register.

### Outputs and messages
- Internal situation reports (activity log under `it_security.activity.*`); tasks for post-crisis actions.
- `it_security.incident_resolved` (recipient `*`) once the underlying incident is closed: `incident_id`, `severity`, `summary`, `root_cause`, `time_to_resolve_hours`.

### SLA and controls
- Bridge in 30 minutes, first situation report in 2 hours, then every 4 hours; stand-down checklist complete within 1 business day.
- Controls: break-glass use reviewed within 1 business day; every emergency change retro-approved by the CISO in the change log within 2 business days; access granted during crisis expires automatically.

### Exceptions and escalation
- CISO unreachable for 30 minutes: the Security and IT Operations Specialist assumes command and the COO is informed.
- Crisis declared for a non-security cause (for example a supplier outage or a regulatory event): the department switches to supporting role: protect identity and data, run the situation report and do not initiate new security change.

## SOP-IT_SECURITY-04: Joiner and contractor access provisioning

**Owner**: Security and IT Operations Specialist (the Access Lifecycle Agent drafts and executes the low-risk steps).
**Trigger**: `people.new_hire_started` (employees) and `people.contractor_engaged` (contractors, associates, and subcontracted consultants).
**Inputs**: message body (`employee_id` or `contractor_id`, `role`, `department`, `start_day`, `manager`, `engagement_end_day` for contractors), role-based access control (RBAC) matrix, device stock, onboarding checklist from People and Operations.

### Steps
1. [agent] Look up the role in the RBAC matrix and generate the access bundle: baseline (email, calendar, chat, document store, password manager, MFA enrolment), departmental applications, and client workspaces only where the manager names the engagement.
2. [agent] Check for toxic combinations (for example finance payment approval plus supplier master data edit) and block bundles that violate segregation of duties.
3. [human] Manager approves access beyond baseline in the ticket; for privileged access, the CISO approves. Client workspaces need engagement lead approval and a signed confidentiality agreement on file.
4. [human] Prepare the managed laptop: full-disk encryption, EDR agent, mobile device management enrolment, screen lock policy, UK keyboard and region settings; ship or hand over on day 1.
5. [agent] Create accounts with a unique identity, enforce hardware-key or authenticator MFA at first sign-in, apply least-privilege groups, and set an expiry date for contractors (never later than contract end).
6. [human] Day 1: deliver 30-minute security induction (acceptable use, phishing, data classification, AI tool policy); the hire signs the information security policy attestation.
7. [agent] Verify provisioning (account active, MFA enrolled, device compliant) and emit `it_security.access_provisioned` to People and Operations.
8. [agent] Schedule a 30-day access check with the manager to confirm access is still appropriate.

### Outputs and messages
- `it_security.access_provisioned` (recipient `*`): `employee_id` or `contractor_id`, `department`, `role`, `access_bundle` (list of systems), `privileged` (bool), `expires_day` (contractors only), `device_compliant` (bool).
- Provisioning ticket with approvals and evidence.

### SLA and controls
- Employee access ready before 09:00 on day 1; contractor access within 2 business days of `people.contractor_engaged`; `access_provisioned` within 1 hour of verification.
- Controls: no shared accounts; privileged access needs CISO approval and quarterly recertification; contractor accounts auto-expire; joiner tickets sampled monthly for approval evidence; ISO 27001 Annex A.5.15-A.5.18 and A.8.2.

### Exceptions and escalation
- Urgent same-day start without approved ticket: baseline access only, no client workspace, no privileged groups; manager approval within 24 hours or access is suspended.
- Contractor from a third country or without background check: General Counsel and People review before access; escalate to CISO.
- Device stock-out: loan device from the buffer pool (3 devices) with same hardening; replacement order raised to Operations.

## SOP-IT_SECURITY-05: Leaver access revocation

**Owner**: Security and IT Operations Specialist (the Access Lifecycle Agent executes).
**Trigger**: `people.employee_left` (body includes `employee_id`, `last_day`, `reason_category`, `involuntary` flag).
**Inputs**: leaver record, account and device inventory, application owner list, shared mailbox and delegated access list, open tickets assigned to the leaver.

### Steps
1. [agent] Compile the leaver's access inventory across identity provider, SaaS applications, source code hosting, cloud consoles, password manager vaults, shared drives and API tokens owned by the person.
2. [human] For involuntary leavers or high-risk cases (privileged, finance, source code access), the CISO schedules revocation to coincide with the exit meeting and coordinates with the Chief People Officer.
3. [agent] At last working time: suspend the identity, revoke sessions and refresh tokens, remove from all groups, disable MFA devices, forward mail to the manager for 30 days, and transfer document ownership.
4. [human] Recover the laptop and devices; remote-wipe if not returned within 5 business days; revoke any hardware keys.
5. [agent] Rotate shared secrets the leaver knew (shared mailbox passwords, service accounts, API keys, client portal credentials) and open tasks for owners.
6. [agent] Verify no active sessions or sign-ins post last day; flag any sign-in attempts to the CISO.
7. [agent] Emit `it_security.access_revoked` to People and Legal; archive the account after 30 days, delete after 90 days per retention schedule.

### Outputs and messages
- `it_security.access_revoked` (recipient `*`): `employee_id`, `department`, `revoked_systems` (list), `revoked_at_day`, `devices_recovered` (bool), `secrets_rotated` (count), `exceptions` (list).
- Leaver ticket with signed asset return form.

### SLA and controls
- Privileged accounts disabled within 1 hour and all access within 4 hours of last working time; verification within 1 business day; `access_revoked` within 1 hour of verification.
- Controls: monthly reconciliation of HR leavers against active accounts (target zero orphan accounts); quarterly sample of 10 leavers by the GRC Lead; ISO 27001 Annex A.5.11 and A.6.5.

### Exceptions and escalation
- Notice given ahead of last day: apply reduced-access ("garden leave") profile on the day notice is given where the person holds privileged or client access.
- Legal hold on the leaver's data: suspend deletion, notify General Counsel, retain the archive.
- Evidence of data exfiltration before leaving: open an incident under SOP-IT_SECURITY-01 and inform General Counsel and Chief People Officer.

## SOP-IT_SECURITY-06: Vulnerability intake, triage and release security gate

**Owner**: Senior Security Specialist (Engineering) from Q2 FY2027; CISO and Security and IT Operations Specialist in FY2026. Product owns fixes (Chief Product Officer).
**Trigger**: `product.release_shipped` (release gate evidence and post-release scan) and `product.vulnerability_fixed` (fix verification). Also scheduled: weekly authenticated scan of the estate, monthly external attack-surface scan, annual third-party penetration test by a CREST-accredited provider, continuous software composition analysis (SCA) and secret scanning on repositories.
**Inputs**: release body (`release_id`, `product`, `version`, `change_summary`), scanner output, software bill of materials (SBOM), threat intelligence on exploited vulnerabilities, asset criticality, fix body (`vulnerability_id`, `release_id`, `fix_summary`).

### Steps
1. [agent] On `product.release_shipped`, run the post-release scan (dependency, container image, configuration and secrets) on the released artefact and compare with the pre-release gate baseline.
2. [agent] Score each finding with CVSS v3.1 or v4 base score, adjust for exploit availability (known exploited vulnerabilities catalogue), internet exposure and data sensitivity, and assign severity.
3. [human] Senior Security Specialist (Engineering) (or CISO) validates findings above medium, removes false positives, and sets remediation targets: critical 7 days (24 hours if on the CISA known exploited vulnerabilities list or actively exploited), high 30 days, medium 60 days, low 90 days.
4. [agent] For each valid finding at medium or above, emit `it_security.vulnerability_found` to Product and Operations with the evidence and deadline, and open a tracking ticket.
5. [human] For critical findings with active exploitation, apply compensating controls immediately (WAF rule, feature flag off, network block) and, if exploitation is evidenced, open an incident under SOP-IT_SECURITY-01.
6. [agent] On `product.vulnerability_fixed`, re-scan the affected asset and validate the fix against the finding; close the ticket if verified, otherwise reopen with the failed evidence and notify Product.
7. [human] Approve risk acceptances only for findings that cannot be fixed within SLA: CISO signs, expiry maximum 90 days, compensating control recorded, reviewed by GRC Lead.
8. [agent] Update the vulnerability metrics: mean time to remediate, SLA breach count, open critical and high count, and release gate pass rate.

### Outputs and messages
- `it_security.vulnerability_found` (recipient `*`): `vulnerability_id`, `severity`, `summary`, `component`, `release_id`, `cvss`, `exploited_in_wild` (bool), `due_day`.
- Verification result recorded in the ticket; closure feeds the KPI for mean time to remediate.

### SLA and controls
- Findings published within 1 business day of confirmation; remediation SLA by severity as above; verification within 2 business days of `product.vulnerability_fixed`.
- Controls: release gate blocks go-live for any open critical or high finding without CISO-signed exception; secret scanning blocks merge; SBOM stored per release; annual penetration test findings tracked to closure; Cyber Essentials Plus patching rule of 14 days for critical and high vendor patches applied across all devices.

### Exceptions and escalation
- SLA breached: automatic escalation to the Chief Product Officer at 100% of SLA and to the CEO at 150% for critical and high.
- Vendor patch not available: raise a risk acceptance, apply compensating controls and notify the vendor risk owner.
- Responsible disclosure report from outside researcher: acknowledge within 2 business days, triage under this SOP, no legal threats; General Counsel informed.

## SOP-IT_SECURITY-07: Customer security questionnaire and security review

**Owner**: GRC Lead from Q2 FY2027; CISO in FY2026 and until the hire starts. Sales is the requester (Chief Revenue Officer, Rahul Mehta).
**Trigger**: `sales.security_review_requested` (body includes `deal_id`, `client_id`, `client_name`, `questionnaire_type`, `due_day`, `contract_value` (`amount_gbp`), `data_access_required`).
**Inputs**: the client questionnaire (for example CAIQ, SIG Lite, bespoke spreadsheet, or a procurement portal), the answer library, current certificates (ISO 27001, Cyber Essentials Plus, later SOC 2 Type II), policies, penetration test summary, sub-processor list, data flow diagram for the proposed engagement.

### Steps
1. [agent] Parse the request and classify: standard (answer library coverage above 80%), bespoke, or on-site audit request. Estimate effort and confirm the deadline.
2. [agent] Draft answers from the approved answer library with a source reference for each answer; mark questions with no approved answer as gaps.
3. [human] GRC Lead (or CISO until hired) reviews the draft; subject-matter experts (Security and IT Operations Specialist, Data, Legal) answer gaps. No answer states a control that is not operating; unsure answers are escalated, never guessed.
4. [human] Flag commercial and legal issues (right to audit, uncapped liability, data residency, sub-processors, AI model training on client data) to Legal in the review thread; these items are Legal's to negotiate.
5. [human] CISO signs off the final response when the deal is at or above £250k or the questionnaire asks for commitments beyond standard policy.
6. [agent] Emit `it_security.security_questionnaire_completed` to Sales and Legal with the result, open gaps and any customer-requested remediation commitments. Add new approved answers to the library.
7. [human] Hold a client security call if requested; record outcomes in the CRM note and the review ticket.
8. [agent] Track follow-up questions for 5 business days after delivery; close the ticket on deal outcome.

### Outputs and messages
- `it_security.security_questionnaire_completed` (recipient `*`; direct replies to `sales` and `legal` where appropriate): `deal_id`, `client_id`, `client_name`, `outcome` (`passed`|`passed_with_conditions`|`gaps_open`), `open_gaps` (count), `commitments` (list), `certificates_provided` (list), `completed_day`.
- Answer library updates with reviewer and date.

### SLA and controls
- Standard: 3 business days; bespoke or on-site audit request: 4 business days (the on-site visit itself is scheduled with the client); a status update to Sales within 1 business day if the deadline is at risk.
- Controls: answer library reviewed quarterly and after every certificate change; two-person review for bespoke content; contractual commitments logged in the commitments register and tracked into delivery; no sharing of internal pentest reports without an NDA and CISO approval.

### Exceptions and escalation
- Client demands a control Lumenhall does not have (for example named SOC 2 Type II report in FY2026): answer honestly with the roadmap date, escalate to Sales head and CISO for a decision on the commercial risk.
- Questionnaire deadline impossible: inform Sales on day 1 and agree a partial response or call; escalate to CRO.
- Large deal (above £500k) with unresolved high-risk gaps: CISO notifies Sales and the CEO before the `sales.deal_approval_requested` step.

## SOP-IT_SECURITY-08: Third-party and AI vendor risk assessment

**Owner**: GRC Lead from Q2 FY2027; CISO in FY2026 and until the hire starts. Operations (Chief Operating Officer Beatrice Moreau) requests; Finance and Legal consume the result.
**Trigger**: `operations.vendor_review_requested` (body includes `vendor_id`, `vendor_name`, `service`, `data_classes`, `annual_cost_gbp` (`amount_gbp`), `tier_hint`, `due_day`) and `operations.vendor_approved` (post-approval control verification).
**Inputs**: vendor questionnaire and evidence pack (ISO 27001 certificate, SOC 2 report, penetration test summary, DPA, sub-processor list, data location, AI model training terms), Lumenhall data classification, existing vendor register.

### Steps
1. [agent] Tier the vendor: Tier 1 if it processes client confidential or personal data, has privileged network or tenant access, or is an AI model or agent platform handling client content; Tier 2 if it handles internal confidential data; Tier 3 otherwise.
2. [agent] Send the tier-appropriate questionnaire, collect evidence, and draft a risk summary scoring governance, data protection, access control, encryption, incident response, resilience, sub-processors, and (for AI vendors) training-data use, model isolation and retention.
3. [human] GRC Lead (CISO until hired) reviews certificates for scope and date (a certificate that excludes the service in use does not count), reads the SOC 2 exceptions section, and checks UK GDPR transfer mechanism (UK IDTA or UK Addendum to EU SCCs, adequacy) for any non-UK processing.
4. [human] Legal confirms DPA terms; CISO decides residual risk: approve, approve with conditions (for example SSO and SCIM required, no training on our data, data residency in UK or EEA), or reject.
5. [agent] Emit `it_security.vendor_risk_assessed` to Operations, Legal and Finance with tier, score, conditions and recommended contract review date.
6. [agent] On `operations.vendor_approved`, verify the conditions are implemented before data flows: SSO enforced, admin accounts reviewed, API keys held in the secret manager, DPA filed, vendor added to the register and the sub-processor list.
7. [human] Schedule reassessment: Tier 1 annually, Tier 2 every two years, Tier 3 at renewal. Monitor vendor breach news and certificate expiry weekly.
8. [agent] Open a task for any unmet condition and block go-live in the access system until cleared.

### Outputs and messages
- `it_security.vendor_risk_assessed` (recipient `*`): `vendor_id`, `vendor_name`, `tier` (1-3), `risk_rating` (`low`|`medium`|`high`), `decision` (`approve`|`approve_with_conditions`|`reject`), `conditions` (list), `reassess_day`, `severity`.
- Updated vendor register and sub-processor list.

### SLA and controls
- Tier 1: 10 business days; Tier 2: 5; Tier 3: 2; verification of conditions within 5 business days of approval; `vendor_risk_assessed` within 1 hour of the CISO decision.
- Controls: no Tier 1 vendor receives client data before assessment; evidence retained for audit; spend above £50k handled via CFO delegation (COMPANY.md §9.3) after the security decision; concentration risk reviewed annually (single supplier above 20% of cloud or AI spend).

### Exceptions and escalation
- Urgent client-driven tooling request: provisional 30-day Tier 1 approval with synthetic or non-client data only; full assessment completed inside the window.
- Vendor refuses evidence: default to reject for Tier 1; escalate to COO if the vendor is business critical, and record a risk acceptance signed by the CEO.
- Vendor reports an incident: treat as a trigger for SOP-IT_SECURITY-01 and request the vendor's incident report within 24 hours.

## SOP-IT_SECURITY-09: Certification and compliance programme

**Owner**: GRC Lead from Q2 FY2027; CISO in FY2026 and until the hire starts.
**Trigger**: `legal.regulatory_change_noted`, `legal.policy_update_published`, `people.compliance_training_completed`, `operations.continuity_test_completed`. Scheduled: monthly certification status review; quarterly internal audit; annual management review.
**Inputs**: ISMS scope and Statement of Applicability, risk register, control library mapped to ISO 27001:2022, Cyber Essentials Plus, SOC 2 Trust Services Criteria, UK GDPR and DPA 2018, internal audit plan, certification body calendar, training completion data, continuity test report, policy register.

### Steps
1. [agent] On `legal.regulatory_change_noted` (body includes `regulation`, `effective_day`, `summary`), map the change to the control library, identify impacted controls, policies and client commitments, and draft an impact note.
2. [human] GRC Lead or CISO validates the impact, assigns control owners and due dates, and updates the risk register and Statement of Applicability if controls change; material changes go to the CEO and the Audit and Risk Committee.
3. [agent] On `legal.policy_update_published` (body includes `policy_id`, `version`, `effective_day`), update the policy register, compare the new text with the mapped controls, and raise an attestation task for staff.
4. [human] Update affected procedures and technical standards within 10 business days of a policy change; confirm exceptions with the policy owner.
5. [agent] On `people.compliance_training_completed` (body includes `course`, `completion_rate`, `cohort`), update the training evidence register, compute completion against the 95% target and flag overdue staff to their managers; accounts of persistently non-compliant staff are reviewed by People after 30 days.
6. [agent] On `operations.continuity_test_completed` (body includes `test_id`, `scenario`, `rto_met`, `rpo_met`, `findings`), file the test as evidence for the business continuity and ICT readiness controls and open tasks for findings, with owners and due dates.
7. [human] Run the quarterly internal audit: sample controls (access reviews, change records, backups restore tests, supplier reviews, training), record nonconformities, and track corrective actions to closure within 60 days (minor) or 30 days (major).
8. [human] Prepare for external audits: ISO 27001 Stage 1 and Stage 2 audits (target certification by end FY2026), Cyber Essentials Plus technical verification (FY2026), SOC 2 Type II observation period of six months starting Q1 FY2027 for completion before US launch. Hold management review at least annually.
9. [agent] Each month, compile certification readiness (controls implemented, evidence complete, open nonconformities, audit dates) and emit `it_security.certification_status_updated` to Legal, Sales and Executive. Emit immediately on a change of status (audit passed, certificate issued, certificate suspended).

### Outputs and messages
- `it_security.certification_status_updated` (recipient `*`): `certification` (`iso_27001`|`cyber_essentials_plus`|`soc2_type2`), `status` (`planned`|`in_progress`|`audit_scheduled`|`certified`|`at_risk`|`suspended`), `readiness_pct`, `open_nonconformities`, `next_milestone`, `next_milestone_day`, `summary`.
- Updated policy register, training register, risk register and evidence register.

### SLA and controls
- Regulatory change impact note within 10 business days of `legal.regulatory_change_noted`; policy attestation at least 95% within 30 days; continuity test findings tracked with owners within 5 business days; monthly status within 3 business days of month-end.
- Controls: single source of truth for the Statement of Applicability; internal audit independent of control owners (GRC Lead audits, not the control owner; CISO reviews); evidence retention seven years; Sales may quote certification only at the stated status.
- Related KPIs and certificates are quoted in client questionnaires only after the status is `certified` (SOP-IT_SECURITY-07).

### Exceptions and escalation
- Audit date at risk or readiness below 80% eight weeks before audit: CISO informs CEO and Chief Operating Officer; consider moving the date rather than failing the audit.
- Major nonconformity found by an external auditor: CISO notifies CEO and General Counsel the same day; Sales told to pause certification claims where certificate scope is affected.
- Conflict between regulatory change and current client commitments: Legal decides, CISO advises on controls.

## SOP-IT_SECURITY-10: AI agent register and credential governance

**Owner**: CISO. The Chief Data and AI Officer (Dr Emeka Nwosu) is co-owner for model and data risk; each agent has a named accountable human owner (COMPANY.md §9.4).
**Trigger**: `product.ai_risk_review_requested` (body includes `agent_id`, `change_summary`, `client_facing` (bool), `data_classes`, `requested_by`). Scheduled: monthly credential rotation check; quarterly register review.
**Inputs**: agent register (agent id, purpose, accountable human owner, autonomy limits, data scope, credentials, model and provider, last review date), proposed change description, DPIA, secrets manager inventory, audit logs of agent actions.

### Steps
1. [agent] On the request, load the agent's register entry (or create a pending entry for a new agent) and summarise the change in terms of data, tools, permissions and autonomy.
2. [agent] Check the security baseline: a unique non-human identity per agent (no shared credentials), credentials stored in the secrets manager (never in prompts, code or environment files), least-privilege scopes, short-lived tokens where the platform allows, audit logging enabled, egress allow-list, and prompt-injection exposure for any tool that reads untrusted content.
3. [human] Security reviewer (CISO or Senior Security Specialist (Engineering)) tests the guardrails: attempt prompt-injection through every input channel, verify that agent actions above £10,000 payment, signing, regulator notification and final hiring or termination decisions are blocked, and confirm client data stays within the data processing agreement.
4. [human] CISO decides: approve, approve with conditions, or block. Conditions typically include human-in-the-loop approval on write actions, rate limits, narrower scopes and 30-day enhanced monitoring.
5. [agent] Record the decision and conditions in the register, update the review date, and send the outcome to the requester through the ticket thread; Legal's AI risk review (`legal.ai_risk_review_completed`) is tracked as a parallel dependency, not duplicated here.
6. [agent] Rotate each agent credential every 90 days (high-privilege every 30 days), revoke credentials for any agent not used in 30 days, and diff the register against the live identity provider monthly to detect unregistered agent identities.
7. [human] Accountable owners recertify each agent quarterly: purpose still valid, permissions still least-privilege, outputs sampled for quality. Failed recertification suspends the agent.
8. [agent] Emit an incident under SOP-IT_SECURITY-01 when anomalous agent behaviour is detected (excess API calls, out-of-scope data access, repeated guardrail hits).

### Outputs and messages
- Register updates and review outcome in the ticket reply to Product, Legal and Data (task and log events under `it_security.activity.*`).
- On anomalous behaviour: `it_security.incident_detected` (see SOP-IT_SECURITY-01 for body keys).
- Where an agent finding is a software weakness: `it_security.vulnerability_found` (see SOP-IT_SECURITY-06) with `component` set to the agent id.

### SLA and controls
- Security review within 5 business days; urgent client-facing changes within 2 business days with CISO approval; credential rotation 90 days; quarterly register review; zero unregistered agent identities.
- Controls: agent register is the authoritative inventory (22 agents at FY2026 year-end across all departments, COMPANY.md §6); material changes to client-facing agents need both security and legal sign-off; agent outputs used in client deliverables are logged for audit.

### Exceptions and escalation
- Unregistered agent identity found: suspend immediately, notify the owning department head, treat as a low severity incident.
- Owner leaves the company: agent suspended until a new accountable owner accepts in the register (linked to SOP-IT_SECURITY-05).
- Disagreement between Product and Security on approval: CEO decides, with the decision and risk acceptance recorded.

## SOP-IT_SECURITY-11: Annual budget cycle and department planning

**Owner**: CISO, with finance business partner (CFO Hannah Whitcombe's team) as counterpart.
**Trigger**: `finance.budget_cycle_opened` (starts annual cycle in Q4), `executive.budget_approved` (approval and envelopes), `executive.okrs_set` (company objectives), `executive.strategy_updated` (strategy change).
**Inputs**: current spend by line, headcount plan (COMPANY.md §6.1), certification and audit calendar, tooling contracts and renewal dates, incident and vulnerability trends, client commitments, the approved envelope (COMPANY.md §5.4: £460k FY2026, £920k FY2027, £2,300k FY2028).

### Steps
1. [agent] On `finance.budget_cycle_opened`, build the draft budget from run rate, contracts and planned hires: people costs from average headcount times loaded cost (base x 1.28), plus non-people lines (tooling, certification and audit fees, penetration testing, training, cyber insurance contribution, managed detection and response, SOC 2 auditor fees).
2. [human] CISO reviews trade-offs and the risk case for each material line (for example a managed 24/7 detection service versus in-house cover), and confirms the plan stays inside the indicative envelope.
3. [agent] Emit `it_security.budget_submitted` to Finance with the line items, headcount request and a written risk statement.
4. [human] Answer Finance queries within 2 business days; revise if the CFO challenges.
5. [agent] On `executive.budget_approved`, load the approved envelope as the department budget, set monthly spend tracking, and flag variances above 10% of any line to the CISO.
6. [agent] On `executive.okrs_set`, translate company objectives into department key results (for example ISO 27001 certified by year end, mean time to remediate, access review completion) and update the KPI targets in the agent state.
7. [human] On `executive.strategy_updated` (for example a US launch date shift or a new industry vertical), CISO assesses impact on certification timing, data residency, supplier changes and headcount, and records the decision.
8. [agent] Re-baseline the department plan within 10 business days and notify the CISO of any dependencies that change.

### Outputs and messages
- `it_security.budget_submitted` (recipient `finance`): `department` (`it_security`), `amount_gbp` (total), `people_gbp`, `non_people_gbp`, `headcount_requested`, `summary`, `risk_statement`, `due_day`.
- Updated department OKR and budget state; variance alerts as tasks.

### SLA and controls
- Budget submitted by the finance deadline (default 15 business days after the cycle opens); queries answered within 2 business days; re-baseline within 10 business days of approval.
- Controls: non-budgeted spend above £50k needs CFO approval and above £250k CEO approval (COMPANY.md §9.3); every contract renewal over £25k flagged 90 days in advance; certification fees ring-fenced.

### Exceptions and escalation
- Approved envelope lower than the submitted risk-based need: CISO documents the residual risk and takes it to the CEO and the Audit and Risk Committee; no silent deferral of a certification control.
- In-year cost shock (for example a Cyber insurance premium rise or a critical vendor price increase): variance report to Finance within 5 business days.

## SOP-IT_SECURITY-12: Security hiring request

**Owner**: CISO. People (Chief People Officer Grace Adeyemi) runs recruitment; the CEO approves headcount outside the approved plan (COMPANY.md §9.3).
**Trigger**: Schedule: monthly capacity review on the first working day, or an event: a capacity trigger is breached (open critical and high vulnerabilities above 15 for two consecutive months, alert queue above 150 per specialist, questionnaire backlog above 6 or over 5 business days old, access review overdue by 30 days, or an audit date at risk through resourcing).
**Inputs**: KPI dashboard, approved headcount plan (2 humans FY2026, 5 FY2027, 9 FY2028; COMPANY.md §6.1), current roles and levels (COMPANY.md §6.2), alert and ticket volumes, agent utilisation.

### Steps
1. [agent] Compute capacity: tickets per person per month, queue ageing, questionnaire turnaround, share of work handled by agents, and project the next two quarters.
2. [human] CISO decides whether to add an agent capability first (preferred where the task is repeatable and low risk), re-prioritise, or hire. Specific roles in order of expected need: GRC Lead and Senior Security Specialist (Engineering) (FY2027, with the IT Support Analyst in H2), then Security Engineering Lead, a second Senior Security Specialist (Engineering), a second Security and IT Operations Specialist and the Security Operations Specialist (FY2028).
3. [agent] Draft the role request: role title, level, band from COMPANY.md §6.2, justification, trigger metric, start quarter, and the effect on the budget.
4. [human] CISO signs the request; if within the approved plan, it proceeds; if outside, it is escalated for CEO approval through `executive.headcount_approved`.
5. [agent] Emit `it_security.hire_requested` to People; track the requisition and make sure access provisioning (SOP-IT_SECURITY-04) is ready for the start date.
6. [human] Participate in interviews, including a practical exercise (alert triage or control design) and reference checks; security hires pass enhanced vetting (BPSS equivalent for privileged roles).

### Outputs and messages
- `it_security.hire_requested` (recipient `people`): `department` (`it_security`), `role`, `level`, `headcount` (int), `start_quarter`, `justification`, `trigger_metric`, `severity` (urgency), `budgeted` (bool).

### SLA and controls
- Request raised within 5 business days of the trigger breach; People acknowledges within 2 business days; target time to fill 60 days for Consultant, Analyst and GRC Lead roles and 90 days for the Senior Security Specialist (Engineering) and Security Engineering Lead roles.
- Controls: requests cite the budgeted headcount plan; hires outside plan need CEO approval; separation of duties maintained during hiring cover (privileged access not given to temporary cover without vetting).

### Exceptions and escalation
- Role unfilled beyond target time: CISO considers a short-term contractor under SOP-IT_SECURITY-04 with time-boxed access, or an interim managed security service, within the non-people budget.
- Single point of failure (one person holds a critical function): CISO documents the continuity gap in the risk register and requests priority hiring.
