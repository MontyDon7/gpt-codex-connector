# IT and Information Security Department Blueprint

Department id: `it_security`. Agent class: `ItSecurityAgent`. Head: Wei Zhang, Chief Information Security Officer (COMPANY.md §9.2). Budget envelope £460k / £920k / £2,300k (COMPANY.md §5.4). Headcount 2 / 5 / 9 humans and 2 / 4 / 8 AI agents (COMPANY.md §6.1).

## 1. Mission and scope

**Mission.** Keep Lumenhall Partners' client data, internal systems and AI agents safe and auditable, so that security is a reason clients buy from us and never a reason a deal stalls. All work is defensive.

**Scope (the department owns):**

1. **IT operations.** Laptops (managed Macs and Windows, full-disk encryption, MDM), identity provider and single sign-on, SaaS administration, email and collaboration tenancy, endpoint protection, backups, the office network at the London HQ, and the service desk.
2. **Identity and access management.** Joiner, mover and leaver provisioning (`people.new_hire_started` to `it_security.access_provisioned`; `people.employee_left` to `it_security.access_revoked`), quarterly access reviews, privileged access, MFA enforcement, contractor and associate access (`people.contractor_engaged`).
3. **Security operations and incident response.** Monitoring `external.security_alert`, triage, `it_security.incident_detected`, containment, `it_security.data_breach_confirmed` where personal data is involved, the 72-hour ICO clock run with Legal (COMPANY.md §9.3), and `it_security.incident_resolved` with a post-incident review.
4. **Governance, risk and compliance (GRC).** ISO 27001:2022 and Cyber Essentials Plus (certified by end FY2026), SOC 2 Type II (FY2027, before the US launch; COMPANY.md §8 assumptions 6 and 7), UK GDPR technical measures, policy library, risk register, internal audit, `it_security.certification_status_updated`.
5. **Third-party and vendor risk.** Security assessment of every new supplier (`operations.vendor_review_requested` to `it_security.vendor_risk_assessed`), annual re-assessment of critical suppliers, sub-processor register.
6. **Client assurance.** Security questionnaires, penetration-test summaries and trust-centre content for sales cycles (`sales.security_review_requested` to `it_security.security_questionnaire_completed`).
7. **Vulnerability and secure-release management.** Vulnerability scanning, patch SLAs, review of `product.release_shipped`, intake of `product.vulnerability_fixed`, `it_security.vulnerability_found`.
8. **AI-agent credential governance.** Co-owner with Data of the agent register (COMPANY.md §9.4): every agent has a named human owner, a unique non-human identity, scoped and expiring credentials stored in the secrets vault, quarterly recertification and a kill switch. Security review input to `product.ai_risk_review_requested`.

**Out of scope.** Legal advice and regulator notification (Legal files, `legal.regulator_notification_filed`); physical premises and facilities (Operations); HR disciplinary decisions (People); product code ownership (Product); procurement and contract negotiation (Operations and Legal). Agents in this department may draft, analyse, monitor and propose, and may not notify regulators, approve spend above £10,000, or make final access decisions for privileged roles (COMPANY.md §9.4).

**Service levels the department commits to (summarised; detail in `sops.md` and `kpis.md`):** standard access provisioned before day 1 of a new starter, leaver access revoked within 4 working hours of notice (immediately for involuntary exits), critical vulnerabilities patched within 7 days, security questionnaires returned within 3 working days, critical incident triage within 30 minutes of the alert during cover hours.

## 2. Org chart

```
Chief Executive Officer (Imogen Hartley)
└── Chief Information Security Officer (Wei Zhang)                       [head]
    ├── GRC Lead                                                         [manager, from Y2]
    │   ├── Agent: Compliance Evidence Collector Agent                   [from Y3]
    │   ├── Agent: Vendor Risk Agent                                     [from Y3]
    │   └── (questionnaire and certification work shared with the CISO in Y1)
    ├── Security Engineering Lead                                        [manager, from Y3]
    │   ├── Senior Security Specialist (Engineering) x2                  [senior_consultant; 1 from Y2, 2 in Y3]
    │   │   ├── Agent: Vulnerability and Patch Agent                     [from Y2]
    │   │   └── Agent: AI Agent Credential Governance Agent              [from Y2]
    │   └── Security Operations Specialist                               [consultant, from Y3]
    │       ├── Agent: Security Alert Triage Agent                       [from Y3]
    │       └── Agent: Phishing Triage Agent                             [from Y3]
    ├── Security and IT Operations Specialist x2                         [consultant; 1 from Y1, 2 in Y3]
    │   ├── Agent: Access Lifecycle Agent                                [from Y1]
    │   └── IT Support Analyst                                           [analyst, from Y2]
    └── Agent: IT Security department agent (ItSecurityAgent)            [from Y1, accountable: CISO]
```

Reporting notes: in FY2026 and until the GRC Lead and Senior Security Specialist (Engineering) start, the single Security and IT Operations Specialist reports directly to the CISO. In Y2 the Senior Security Specialist (Engineering) and the Security and IT Operations Specialist report to the CISO; from Y3 the Security Engineering Lead takes engineering and security operations reporting lines, and the CISO retains GRC, IT operations and the department agent. The CISO is the Data Protection technical contact; the statutory DPO function sits with Legal (General Counsel, COMPANY.md §9.2).

## 3. Roles

Level keys and bands come from COMPANY.md §6.2. Y1, Y2 and Y3 are year-end headcount (FY2026, FY2027, FY2028) and sum to the it_security row of COMPANY.md §6.1 (2 / 5 / 9).

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Information Security Officer | head | Chief Executive Officer | 1 | 1 | 1 | £140,000 to £200,000 (cash; plus equity) | Security strategy and budget, ISO 27001 and SOC 2 accountability, incident commander for severity high and critical, board and Audit and Risk Committee reporting, client-facing security escalations, agent-register co-owner, approver of risk acceptances, ICO breach decision with General Counsel and CEO |
| GRC Lead | manager | Chief Information Security Officer | 0 | 1 | 1 | £92,000 to £115,000 | Owns the ISMS, Statement of Applicability, risk register, policy library, internal audit programme, SOC 2 evidence calendar, auditor liaison, vendor risk programme, questionnaire quality; manager of the Compliance Evidence Collector Agent and Vendor Risk Agent |
| Security Engineering Lead | manager | Chief Information Security Officer | 0 | 0 | 1 | £92,000 to £115,000 | Leads security engineering and security operations: detection engineering, secure configuration baselines, secrets vault, cloud and SaaS posture, penetration-test remediation tracking, on-call rota owner; manager of the engineering and security operations specialists |
| Senior Security Specialist (Engineering) | senior_consultant | Chief Information Security Officer (Y2); Security Engineering Lead (Y3) | 0 | 1 | 2 | £72,000 to £90,000 | Vulnerability management and patch SLAs, endpoint detection and response tuning, logging and SIEM rules, secure-release review with Product, agent credential governance owner (vault, rotation, kill switch), incident response lead for medium and high |
| Security and IT Operations Specialist | consultant | Chief Information Security Officer | 1 | 1 | 2 | £55,000 to £70,000 | Identity provider, joiner-mover-leaver, MDM and laptop lifecycle, SaaS administration, backups and restore tests, quarterly access reviews, Cyber Essentials Plus technical scope; accountable owner of the Access Lifecycle Agent |
| Security Operations Specialist | consultant | Security Engineering Lead | 0 | 0 | 1 | £55,000 to £70,000 | Alert triage and first-line incident response, phishing reports, threat-intelligence digest, tabletop exercise logistics; accountable owner of the Security Alert Triage Agent and Phishing Triage Agent |
| IT Support Analyst | analyst | Security and IT Operations Specialist | 0 | 1 | 1 | £38,000 to £48,000 | Service desk, device build and shipping, onboarding hardware kits with Operations, account unlocks (with identity verification), asset register hygiene |
| **Total humans** | | | **2** | **5** | **9** | | |

Compensation assumptions used in `economics.md` (modelled base salaries, inside the bands above): CISO £140,000 in FY2026 (rebased to £150,000 from 2027-01-01, then £170,000 in FY2028 on SOC 2 Type II attainment); GRC Lead £96,000 then £100,000; Security Engineering Lead £108,000; Senior Security Specialist (Engineering) £78,000 then £84,000; Security and IT Operations Specialist £63,000 to £65,000 then £70,000; Security Operations Specialist £60,000; IT Support Analyst £42,000 then £44,000. Loaded cost is base x 1.28 (COMPANY.md §5.2). US hires carry the +15% uplift (COMPANY.md §6.2); no US-based security hire is planned before FY2028 H2 and none is included in the headcount above.

Average headcount and cost, derived from the start quarters in section 5, tie to the people envelope of COMPANY.md §5.4: FY2026 base £203k, loaded £260k; FY2027 base £366.5k, loaded £469k; FY2028 base £704k, loaded £901k. The full build-up is in `economics.md` section 2.

## 4. AI agents

Agent counts sum to the it_security row of COMPANY.md §6.1 (2 / 5... see totals: 2 / 4 / 8 agents). Every agent has a named human accountable owner, a unique non-human identity in the identity provider, credentials issued from the secrets vault with a maximum 90-day life, and an entry in the agent register (COMPANY.md §9.4). Agents never hold standing privileged access; elevated actions need a human-approved, time-boxed grant.

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| IT Security department agent (`ItSecurityAgent`) | Chief Information Security Officer | Department orchestrator: consumes the subscribed topics, opens incidents, drafts security questionnaire answers, tracks certification milestones, maintains KPI state, creates tasks for humans | May draft, classify, create tasks and publish `it_security.*` status topics. May not declare a breach to a regulator, accept a risk, change production security controls, or approve spend above £10,000 | 1 | 1 | 1 |
| Access Lifecycle Agent | Security and IT Operations Specialist | Executes the joiner-mover-leaver workflow against the identity provider and SaaS apps: standard role bundles for `access_provisioned`, immediate disablement for `access_revoked`, contractor expiry dates, evidence logging | Standard role bundles only (no admin or finance-approval rights); privileged grants need human approval; disables accounts but does not delete data or mailboxes (retention is a human decision with Legal); leaver revocation is time-boxed to 4 working hours | 1 | 1 | 1 |
| Vulnerability and Patch Agent | Senior Security Specialist (Engineering) | Correlates scanner output, product release notes and `product.vulnerability_fixed` against asset inventory; ranks by CVSS and exploitability; raises `it_security.vulnerability_found` and patch tickets; tracks SLA clock | Read-only on scanners and asset inventory; may open tickets and schedule non-production patch rings; production patching is human-approved; cannot suppress a finding without a human risk acceptance | 0 | 1 | 1 |
| AI Agent Credential Governance Agent | Senior Security Specialist (Engineering) | Maintains the agent register with Data: owner, purpose, data classes touched, scopes, credential age, last use; flags orphaned, over-scoped or stale credentials; prepares quarterly recertification packs; supports the kill switch | May request rotation and may disable an agent credential only under the documented kill-switch criteria (anomalous egress, owner departed, credential in public repository), with the owner and CISO notified within 15 minutes; cannot issue new credentials | 0 | 1 | 1 |
| Vendor Risk Agent | GRC Lead | Pre-screens suppliers on `operations.vendor_review_requested`: collects ISO 27001 and SOC 2 reports, DPA and sub-processor lists, runs the tiering questionnaire, drafts the risk rating | Drafts and recommends only; the rating published in `it_security.vendor_risk_assessed` for tier 1 and tier 2 suppliers is signed off by the GRC Lead; cannot approve a vendor | 0 | 0 | 1 |
| Compliance Evidence Collector Agent | GRC Lead | Pulls recurring SOC 2 and ISO 27001 evidence (access review exports, backup tests, training completion, change tickets) on the audit calendar and checks completeness; flags control drift | Read-only evidence collection from approved systems; never alters evidence or system configuration; findings are classified by a human before auditors see them | 0 | 0 | 1 |
| Security Alert Triage Agent | Security Operations Specialist | First-line triage of `external.security_alert` and detections: deduplicates, enriches, scores, drafts the incident summary, recommends containment | Recommends containment; may isolate a single non-production endpoint from the network under pre-approved playbooks; any production or executive device action and any severity high or critical declaration need a human | 0 | 0 | 1 |
| Phishing Triage Agent | Security Operations Specialist | Handles the reported-phishing mailbox: detonates and classifies, pulls matching messages tenant-wide under a pre-approved playbook, drafts staff feedback, trends campaigns | May quarantine messages matching a confirmed-malicious verdict; may not block domains at the gateway without human approval; never replies to external senders | 0 | 0 | 1 |
| **Total agents** | | | **2** | **4** | **8** | |

## 5. Hiring plan

All hires follow the people-department hiring chain (COMPANY.md §8 assumption 3: 45-day human time-to-hire; 5-day agent provisioning): `it_security.hire_requested` to `people.requisition_opened` to `executive.headcount_approved` to `people.job_posted`. Headcount within the approved budget envelope is pre-approved by the CEO at budget sign-off; any addition beyond the table below is a non-budgeted hire (COMPANY.md §9.3).

### FY2026 (quarterly)

| Quarter | Role | Count | Start | Trigger |
|---|---|---|---|---|
| Q1 FY2026 | Chief Information Security Officer (Wei Zhang) | 1 | Q1, day 1 | Founding executive team; ISO 27001 programme must start immediately to certify by year-end |
| Q1 FY2026 | Security and IT Operations Specialist | 1 | Q1 (start 2026-02-02) | 29 average humans in FY2026; all joiners need laptops and identity on day 1; first-line operator needed before the first client security review |
| Q2 FY2026 | Agents: Access Lifecycle Agent provisioned (5-day provisioning) | 1 agent | Q2 | After identity provider and role bundles are defined and the first 10 joiners processed manually |
| Q3 FY2026 | No human hire | 0 | n/a | Hold: ISO 27001 Stage 1 audit and Cyber Essentials Plus assessment; trigger for FY2027 hires is Stage 2 outcome |
| Q4 FY2026 | No human hire; requisitions for FY2027 GRC Lead and Senior Security Specialist opened | 0 | n/a | Trigger: ISO 27001 certificate issued (target by end FY2026) and SOC 2 Type II readiness plan approved |

The ItSecurityAgent is provisioned in Q1 FY2026 together with the department set-up (agent 1 of 2 in Y1).

### FY2027 (half-year)

| Half | Role | Count | Start | Trigger |
|---|---|---|---|---|
| H1 FY2027 | GRC Lead | 1 | Q2 (start 2027-04-01) | SOC 2 Type II observation window opens (6 months minimum) and the questionnaire volume exceeds 25 a quarter; CISO can no longer own evidence calendar and sales assurance together |
| H1 FY2027 | Senior Security Specialist (Engineering) | 1 | Q2 (start 2027-04-01) | Headcount passes 40 humans; vulnerability backlog and agent credential count exceed what one operator can govern |
| H1 FY2027 | Agents: Vulnerability and Patch Agent; AI Agent Credential Governance Agent | 2 agents | Q1 to Q2 | Agent estate passes 30 agents (COMPANY.md §6: 22 at FY2026 year-end, 70 at FY2027 year-end); credential recertification must be quarterly |
| H2 FY2027 | IT Support Analyst | 1 | Q3 (start 2027-07-01) | Headcount passes 55 humans; service desk tickets above 120 a month; frees the Operations Specialist for identity and SOC 2 control ownership |

### FY2028 (half-year)

| Half | Role | Count | Start | Trigger |
|---|---|---|---|---|
| H1 FY2028 | Security Engineering Lead | 1 | Q1 (start 2028-01-03) | Engineering and operations reporting lines exceed CISO span of control (4 direct humans plus 4 agents); US launch needs 24x5 cover plan |
| H1 FY2028 | Senior Security Specialist (Engineering) | 1 | Q2 (start 2028-04-03) | Platform assurance work for US region and client-specific environments; SOC 2 Type II renewal |
| H2 FY2028 | Security and IT Operations Specialist | 1 | Q3 (start 2028-07-03) | Headcount passes 150 humans; US onboarding at +15% band from COMPANY.md §6.2 is not planned in this role |
| H2 FY2028 | Security Operations Specialist | 1 | Q3 (start 2028-07-03) | Alert volume and phishing reports require a named human owner for the triage agents; follow-the-sun handover with the on-call rota |
| H1 to H2 FY2028 | Agents: Vendor Risk Agent; Compliance Evidence Collector Agent; Security Alert Triage Agent; Phishing Triage Agent | 4 agents | Q1 to Q3 | Vendor count above 120; annual SOC 2 and ISO 27001 surveillance cycles; alert volume above 3,000 a month |

Year-end totals: FY2026 2 humans and 2 agents; FY2027 5 humans and 4 agents; FY2028 9 humans and 8 agents (COMPANY.md §6.1).

## 6. Interfaces

Topics are from `core/topics.py` and CONVENTIONS section 7.3. `it_security` publishes: `access_provisioned`, `access_revoked`, `certification_status_updated`, `data_breach_confirmed`, `incident_detected`, `incident_resolved`, `security_questionnaire_completed`, `vendor_risk_assessed`, `vulnerability_found`, plus the generic `it_security.budget_submitted` (to finance) and `it_security.hire_requested` (to people).

### 6.1 Departments we serve (we publish, they act)

| Topic we publish | Consumers | Purpose |
|---|---|---|
| `it_security.security_questionnaire_completed` | sales, legal | Answered client questionnaire for the deal (`deal_id`, `client_id`); sales continues to `sales.proposal_sent` |
| `it_security.access_provisioned` | people, operations | Joiner has identity, devices and standard apps (`employee_id`); People closes onboarding, Operations confirms workspace |
| `it_security.access_revoked` | people, legal | Leaver access removed (`employee_id`, timestamp); Legal uses for retention and exit obligations |
| `it_security.incident_detected` | executive, legal, operations, customer_success, delivery | Severity-rated incident (`incident_id` INC-0001, `severity`, `summary`); Delivery and Customer Success check client exposure |
| `it_security.data_breach_confirmed` | legal, executive, customer_success | Personal data affected; starts the ICO 72-hour clock with Legal (`incident_id`, `affected_clients`, `records_estimate`) |
| `it_security.incident_resolved` | executive, operations, customer_success, legal | Closure with root cause and post-incident review date |
| `it_security.certification_status_updated` | legal, sales, executive | ISO 27001, Cyber Essentials Plus and SOC 2 status for contracts and sales claims |
| `it_security.vendor_risk_assessed` | operations, finance, legal | Risk tier and conditions for a supplier (`vendor_id` VN-0001); Operations then publishes `operations.vendor_approved` |
| `it_security.vulnerability_found` | operations, product | Vulnerability needing a product or platform fix (`severity`, `asset`, `due_day`) |

### 6.2 Departments we depend on (we subscribe)

| Topic we consume | Publisher | What we do |
|---|---|---|
| `external.security_alert` | external | Triage and open `INC-` incident; the spine of the security incident chain |
| `people.new_hire_started` / `people.employee_left` / `people.contractor_engaged` | people | Provision, revoke, or time-box contractor access |
| `sales.security_review_requested` | sales | Complete the client questionnaire within 3 working days (4 for custom or on-site audit requests) |
| `operations.vendor_review_requested` / `operations.vendor_approved` | operations | Assess suppliers; register approved suppliers and sub-processors |
| `operations.continuity_test_completed` | operations | Check backup and recovery evidence; feed ISO 27001 A.5.30 and SOC 2 availability evidence |
| `legal.policy_update_published` / `legal.regulatory_change_noted` | legal | Update the policy library and control mapping; assess technical impact (for example Cyber Security and Resilience Bill obligations when enacted) |
| `legal.regulator_notification_filed` | legal | Confirms ICO notice filed; incident moves to recovery and lessons learned |
| `people.compliance_training_completed` | people | Security-awareness completion as ISO 27001 and SOC 2 evidence; gate for access to client data |
| `product.release_shipped` / `product.vulnerability_fixed` | product | Secure-release checks; close vulnerability tickets after retest |
| `product.ai_risk_review_requested` | product | Security assessment of agent changes (data flows, credentials, prompt-injection exposure) feeding the Legal AI risk review |
| `executive.budget_approved` / `executive.okrs_set` / `executive.strategy_updated` / `executive.crisis_declared` | executive | Load budget and OKRs; crisis mode raises security monitoring and comms cadence |
| `finance.budget_cycle_opened` | finance | Prepare and send `it_security.budget_submitted` |

### 6.3 Standing forums

- Weekly security and operations stand-up (CISO, specialists, department agent summary).
- Monthly risk review chaired by the CISO with Legal, Operations and Data (risk register, vendors, agent register).
- Quarterly access review sign-off with each department head; quarterly Audit and Risk Committee security report (committee chair Marcus Ellery, COMPANY.md §9.1).
- Joint tabletop exercise with Legal and Executive twice a year, including a client-data breach and a compromised agent credential scenario.

## 7. Risks and dependencies

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| ISO 27001 certificate slips past end FY2026, delaying the US launch gate (COMPANY.md §8 assumption 6) and enterprise deals | Medium | High | Gap assessment in Q1; Stage 1 audit by end Q3; contractor-supported internal audit; Stage 2 booked 8 weeks before year-end; sales told to quote only "in progress" until `it_security.certification_status_updated` says certified | CISO |
| Key-person dependency: only 2 humans in FY2026, and one operator for identity, devices and IT | High | High | Runbooks and infrastructure-as-code for identity; break-glass accounts held by the CISO and CEO with sealed procedure; managed detection and response retainer (non-people budget); CISO deputises on incidents | CISO |
| Agent credential sprawl: 22 agents rising to 150 (COMPANY.md §6) each with tokens into client data | High | High | Non-human identity per agent, vault-issued 90-day credentials, least privilege per COMPANY.md §9.4, quarterly recertification, kill switch, public-repository secret scanning, egress monitoring | Senior Security Specialist (Engineering) |
| Client data breach involving personal data; ICO notification within 72 hours | Low to medium | Very high | Incident response plan, retained forensic firm, pre-drafted ICO template with Legal, tabletop twice a year, logging retention 12 months | CISO with General Counsel |
| Prompt injection or data leakage through client-facing agents | Medium | High | Security input to every AI risk review; output filtering; segregated client tenancies; human QA before client deliverables (COMPANY.md §9.4) | Security Engineering Lead (CISO in Y1 and Y2) |
| Phishing and business email compromise targeting finance (invoice fraud) and executives | High | High | MFA with phishing-resistant keys for finance and executives, payment-change call-back control with Finance, reported-phishing playbook, quarterly simulations | Security and IT Operations Specialist |
| Questionnaire volume (rising with 640 / 1,200 / 2,267 leads, COMPANY.md §5.3) stalls sales cycles | Medium | Medium | Questionnaire agent drafting, answer library, trust-centre page, SLA of 3 working days, KPI visibility to the CRO | GRC Lead (CISO in Y1) |
| Supplier concentration and sub-processor failure (cloud, LLM providers, identity provider) | Medium | High | Tiered vendor reviews, exit and data-return clauses via Legal, annual critical-supplier re-assessment, multi-region backups | GRC Lead |
| Hiring market for security engineers in London; 45-day time-to-hire (COMPANY.md §8) | Medium | Medium | Requisitions opened one quarter ahead, internal agent leverage, contractor bridge from the non-people budget | CISO with Chief People Officer |
| Compliance fatigue: SOC 2 and ISO 27001 evidence consumes the small team | Medium | Medium | Evidence automation (agent from Y3, scripted exports before), single control framework mapped to both standards | GRC Lead |

Dependencies: People for joiner and leaver notices in time (a leaver notice delayed beyond 4 working hours is a control breach attributable to the process, not to IT); Operations for hardware logistics and supplier onboarding; Legal for DPAs, regulator contact and policy approval; Product for fix capacity on vulnerabilities; Finance for the budget envelope and the tooling spend within the non-people lines (£200k / £450k / £1,400k, COMPANY.md §5.4).

## 8. Sources

- COMPANY.md §5.2 (loaded cost = base x 1.28, AI agent cost range, FY2026 average loaded cost)
- COMPANY.md §5.3 (commercial funnel volumes driving questionnaire demand)
- COMPANY.md §5.4 (it_security budget envelope: people £260k / £470k / £900k, non-people £200k / £450k / £1,400k, total £460k / £920k / £2,300k)
- COMPANY.md §6 and §6.1 (headcount plan: 2 / 5 / 9 humans, 2 / 4 / 8 agents for it_security)
- COMPANY.md §6.2 (level keys and salary bands; US +15%)
- COMPANY.md §8 (assumptions 3, 5, 6, 7: time-to-hire, on-costs, US launch gate, compliance baseline)
- COMPANY.md §9.1 (Board and Audit and Risk Committee)
- COMPANY.md §9.2 (Chief Information Security Officer: Wei Zhang; heads report to the CEO)
- COMPANY.md §9.3 (delegations of authority: non-budgeted spend, breach notification)
- COMPANY.md §9.4 (AI agent governance and the agent register)
- CONVENTIONS.md §3.1 (blueprint template) and §7 (lifecycle chains and topic table)
