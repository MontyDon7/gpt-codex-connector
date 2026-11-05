# Legal Department Blueprint

## 1. Mission and scope

The Legal department protects Lumenhall Partners Ltd (UK, England and Wales) and, from Q1 FY2027, Lumenhall Partners Inc. (Delaware) by turning commercial intent into enforceable, standard-form contracts quickly, keeping the firm compliant with UK GDPR and the Data Protection Act 2018 (DPA 2018), tracking regulatory change, handling personal data breaches inside the 72-hour ICO window, reviewing AI systems for legal risk, and protecting the firm's IP and brand. It is led by the General Counsel, Callum Fraser, who reports to the CEO, Imogen Hartley (COMPANY.md §9.2).

**Operating principle: agents assist, qualified human lawyers decide.** The Legal agent (class `LegalAgent`) does first-pass analysis, drafting from the playbook, deadline tracking and routing. It never gives binding legal advice, never signs contracts and never notifies a regulator (COMPANY.md §9.4). Every judgement-bearing output carries `advice_status: draft_for_human_lawyer_review` and an escalation to the General Counsel. In FY2026 the General Counsel is the only human lawyer, so all escalations land with one person; outside counsel is the surge and specialist capacity (budget line in `economics.md`).

| Area | What Legal owns | Standing targets |
|---|---|---|
| Commercial contracts | MSA and SOW paper for Compass and Forge, Keep order forms, change orders, renewals; contract playbook (standard / fallback / escalate per clause) | Draft within 3 days of `sales.deal_won`; signed within 7 days; no more than 10% of contracts with non-standard liability |
| Deal risk | Pre-approval review of non-standard terms for `sales.deal_approval_requested`; `legal.contract_risk_flagged` | Deals >= £500k need CEO; > £1.5m Board; uncapped liability or non-standard IP/data terms need General Counsel and CEO (COMPANY.md §9.3) |
| Data protection | UK GDPR and DPA 2018 programme, Art 28 DPAs, DPIAs, DSARs, breach register (Art 33(5)), ICO registration and fee | ICO notification within 72 hours of awareness where notifiable (COMPANY.md §9.3); DSARs inside the one-month statutory deadline |
| Security and breach | Privileged matter for every incident, ICO and data-subject notification decisions, client contractual notices | General Counsel with CISO and CEO decide and file (COMPANY.md §9.3) |
| Regulatory change | Horizon scanning (UK, EU, US from FY2027), impact notes, compliance findings, policy updates | Triage within 2 days of `external.regulation_published` |
| AI risk | Legal review of client-facing and internal AI systems (EU AI Act tiering, UK AI regulatory principles, UK GDPR Art 22 and Art 35) | Review within 5 days of `product.ai_risk_review_requested` |
| Disputes and collections | Late Payment of Commercial Debts (Interest) Act position, letter before action at day 60 of the collections ladder (COMPANY.md §7), dispute handling under legal privilege | GC reviews letter within 3 days of `finance.collections_escalated` |
| Vendors, contractors, people | Vendor contract and DPA review, contractor agreements and IR35 status, employment contracts and restrictive covenants | DPA in place before any personal-data processing starts |
| IP and brand | Trade marks, client IP and licence terms, brand and misleading-claim incidents | Incident triaged within 1 day |
| Corporate governance | Board minutes, statutory registers, Companies House filings, insurance renewals (PI, cyber, D&O), delegations of authority | Companies House changes filed within 14 days |

Out of scope: tax advice (Finance with external advisers), security controls (IT Security), employment relations decisions (People; Legal advises), final commercial pricing (Sales and Finance). Legal is an operating-expense department, not cost of revenue (COMPANY.md §5.1). Its budget envelope is £310k / £580k / £1,300k (people £210k / £330k / £600k; non-people £100k / £250k / £700k) per COMPANY.md §5.4.

## 2. Org chart

```
General Counsel (head)                              Callum Fraser, reports to CEO
|
+-- Commercial and Privacy Counsel                  manager; joins Q2 FY2027
|     +-- Contracts Specialist                      consultant; joins Q3 FY2027
|     +-- Legal Operations Analyst                  analyst; joins Q2 FY2028
|
+-- Privacy and Regulatory Counsel                  manager; joins Q1 FY2028
|
+-- AI agents (see section 4), each with a named human owner
```

Reporting-line notes: in FY2026 the General Counsel is the only lawyer and personally runs every `[human]` step. From Q2 FY2027 Commercial and Privacy Counsel takes day-to-day contracts and data protection and is the second approver for fallback positions in the General Counsel's absence (not for escalate-level positions, which always need the General Counsel and CEO). The Contracts Specialist and the Legal Operations Analyst support Commercial and Privacy Counsel. Privacy and Regulatory Counsel (FY2028) owns the regulatory horizon, AI risk and the US/EU programme and reports to the General Counsel.

## 3. Roles

Headcount is year-end humans and sums to COMPANY.md §6.1: legal = 1 / 3 / 5. Level keys and bands are from COMPANY.md §6.2.

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| General Counsel | head | Chief Executive Officer | 1 | 1 | 1 | 140,000 to 200,000 (cash; plus equity) | Owns legal strategy and the contract playbook; approves fallback and escalate positions with the CEO; decides and files ICO notifications with the CISO and CEO; Board and Audit and Risk Committee legal reporting; outside counsel panel and budget; accountable owner of the Legal agent; Companies House and statutory registers |
| Commercial and Privacy Counsel | manager | General Counsel | 0 | 1 | 1 | 92,000 to 115,000 | Day-to-day contract negotiation and fallback approvals, Art 28 DPAs and DPIAs, DSAR handling, breach register, vendor contract review, owner of the Contract Review and Privacy and Breach agents |
| Privacy and Regulatory Counsel | manager | General Counsel | 0 | 0 | 1 | 92,000 to 115,000 | Regulatory horizon (UK, EU, US state law), policy library, AI risk reviews and EU AI Act alignment, ICO relationship, US/EU programme, owner of the Regulatory Horizon and AI Risk Review agents |
| Contracts Specialist | consultant | Commercial and Privacy Counsel | 0 | 1 | 1 | 55,000 to 70,000 | Contract drafting from playbook, signature logistics and e-signature, change orders and renewals, clause library, matter and obligations tracking in the CLM |
| Legal Operations Analyst | analyst | Commercial and Privacy Counsel | 0 | 0 | 1 | 38,000 to 48,000 | Legal KPI reporting, outside-counsel spend tracking, registers (policies, vendors, DPAs, trade marks), training completion chasing, CLM data quality |
| **Total humans** | | | **1** | **3** | **5** | | Equals COMPANY.md §6.1 row for legal |

### Planning salary points and cost check

Loaded cost = base x 1.28 (COMPANY.md §5.2). Planning bases sit inside the §6.2 bands. Average FTE reflects start quarter (Q1 start = 1.00, Q2 = 0.75, Q3 = 0.50, Q4 = 0.25 of a year). Commercial and Privacy Counsel and the Contracts Specialist take a 5% pay review at 2028-01-01. The full build-up is in `economics.md` section 2.

| Role | Planning base £ | Loaded £ | FY2026 avg FTE | FY2027 avg FTE | FY2028 avg FTE | FY2026 £k | FY2027 £k | FY2028 £k |
|---|---|---|---|---|---|---|---|---|
| General Counsel | 164,000 | 209,920 | 1.00 | 1.00 | 1.00 | 209.9 | 209.9 | 209.9 |
| Commercial and Privacy Counsel | 92,000 (96,600 in FY2028) | 117,760 (123,648) | 0 | 0.75 | 1.00 | 0 | 88.3 | 123.6 |
| Contracts Specialist | 55,000 (57,750 in FY2028) | 70,400 (73,920) | 0 | 0.50 | 1.00 | 0 | 35.2 | 73.9 |
| Privacy and Regulatory Counsel | 115,000 | 147,200 | 0 | 0 | 1.00 | 0 | 0 | 147.2 |
| Legal Operations Analyst | 44,000 | 56,320 | 0 | 0 | 0.75 | 0 | 0 | 42.2 |
| **Total people cost** | | | **1.00** | **2.25** | **4.75** | **209.9** | **333.4** | **596.9** |
| COMPANY.md §5.4 people envelope | | | | | | 210 | 330 | 600 |
| Delta | | | | | | -0.1 | +3.4 | -3.1 |

All three years are within the £5k tolerance.

## 4. AI agents

Agent counts sum to COMPANY.md §6.1: legal = 1 / 3 / 5. Every agent is registered in the agent register (Data and IT Security) with a named accountable human (COMPANY.md §9.4). All agents share these hard limits: they may draft, analyse, monitor and propose; they may not give binding legal advice, sign or execute contracts, notify the ICO or any regulator, send a letter before action, make admissions or settlement offers, or approve any payment above £10,000. In the simulation the single department agent `LegalAgent` implements the combined behaviour of the agents in this table; the human-only steps (signature, ICO filing) are modelled as delayed internal confirmations.

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Legal Operations Agent (`LegalAgent`) | General Counsel | Y1 all-in-one: opens contracts from `sales.deal_won`, compares terms with the playbook, drafts, tracks approvals, models signature, triages regulation, opens breach matters and runs the 72-hour clock, runs AI risk tiering, late-payment position, vendor and people legal checks, budget submission | Drafts and routes only; every output is marked draft for human lawyer review; cannot sign, file with a regulator, send letters or approve a fallback or escalate position | 1 | 1 | 1 |
| Contract Review Agent | Commercial and Privacy Counsel (General Counsel until Q2 FY2027) | Playbook comparison per clause, redline suggestions, renewal uplift check (CPI + 2%, cap 7%), change-order pricing from rate card | May mark standard clauses as standard and sample-check them; must send any fallback or escalate clause to a human; cannot agree a fallback | 0 | 1 | 1 |
| Privacy and Breach Agent | Commercial and Privacy Counsel | DSAR clock, breach register, 72-hour ICO deadline watch (warning at 24 hours left), Art 28 DPA checks for vendors | Cannot decide whether a breach is notifiable or file; raises tasks and deadline alerts only | 0 | 1 | 1 |
| Regulatory Horizon Agent | Privacy and Regulatory Counsel (General Counsel until Q1 FY2028) | Monitors `external.regulation_published`, classifies impact area, owners and severity, drafts compliance findings and policy-update notices | Cannot publish a policy without General Counsel sign-off; cannot interpret ambiguous law | 0 | 0 | 1 |
| AI Risk Review Agent | Privacy and Regulatory Counsel | Tiers AI use cases (prohibited / high / limited / minimal), lists conditions, DPIA trigger, drafts the `legal.ai_risk_review_completed` recommendation | Cannot clear a high-risk or prohibited system; recommendation stays `pending_gc_signoff` | 0 | 0 | 1 |
| **Total agents** | | | | **1** | **3** | **5** |

Agent cost is carried in non-people spend (AI compute and tooling) within the £100k / £250k / £700k envelope (economics.md section 1).

## 5. Hiring plan

Time-to-hire is 45 days for humans and 5 days for agent provisioning (COMPANY.md §8). Every human hire goes through `legal.hire_requested` then `people.requisition_opened`, then `executive.headcount_approved` (COMPANY.md §9.3). The agent emits `legal.hire_requested` in the month shown (month of the requisition) so the start quarter assumes offer acceptance about 45 days later.

### FY2026 (quarterly)

| Quarter | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| Q1 FY2026 | General Counsel (Callum Fraser) | 1 | Q1 FY2026 (in post from Day 0, 2026-01-05) | Founding executive team (COMPANY.md §9.2) |
| Q1 FY2026 | Legal Operations Agent | 1 agent | Q1 FY2026 | First `sales.deal_won` expected within the 75-day sales cycle |
| Q2 FY2026 | none | 0 | n/a | Series A closes; outside counsel handles financing documents |
| Q3 FY2026 | none | 0 | n/a | Watch trigger: more than 6 contracts open at once or contract turnaround above 5 days |
| Q4 FY2026 | none; FY2027 requisition prepared in the BUD-2027 budget submission | 0 | n/a | Annual budget cycle opens in Q4 |

### FY2027 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2027 | Commercial and Privacy Counsel | 1 | Q2 FY2027 (requisition 2027-01) | New logos 45 in the year, US entity (Inc.) set-up in Q1 FY2027, SOC 2 Type II contractual warranties, GC span of control |
| H1 FY2027 | Contract Review Agent; Privacy and Breach Agent | 2 agents | Q2 FY2027 | Commercial and Privacy Counsel in post as owner |
| H2 FY2027 | Contracts Specialist | 1 | Q3 FY2027 (requisition 2027-04) | More than 12 new contracts, renewals and change orders a month, or signature turnaround above 7 days |
| H2 FY2027 | Privacy and Regulatory Counsel | 1 | Q1 FY2028 (requisition 2027-10) | US launch, EU AI Act timelines, 110 humans, regulatory horizon backlog above 2 days triage target |

### FY2028 (half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 FY2028 | Legal Operations Analyst | 1 | Q2 FY2028 (requisition 2028-01) | Outside-counsel spend and registers exceed lawyer time; CLM data quality and KPI reporting |
| H1 FY2028 | Regulatory Horizon Agent; AI Risk Review Agent | 2 agents | Q1 FY2028 | Privacy and Regulatory Counsel in post as owner |

Year-end check: FY2026 = General Counsel = 1; FY2027 adds Commercial and Privacy Counsel and Contracts Specialist = 3; FY2028 adds Privacy and Regulatory Counsel and Legal Operations Analyst = 5. The Privacy and Regulatory Counsel requisition is raised in FY2027 but the hire starts in Q1 FY2028, so it is counted at the FY2028 year-end only. Attrition (14% falling to 11%, COMPANY.md §8) is backfilled within the same requisition. US-based legal hires carry the +15% band uplift (COMPANY.md §6.2); none are planned, with US counsel engaged under the outside-counsel and US/EU programme lines.

## 6. Interfaces

Topics are those in `core/topics.py` and CONVENTIONS.md §7.

### Legal publishes (prefix `legal.`)

| Topic | Consumers | When |
|---|---|---|
| `legal.contract_drafted` | sales (and others by subscription) | A draft contract, order form, change order or renewal is opened |
| `legal.contract_signed` | finance, delivery, sales, customer_success | A human authorised signatory has executed the contract |
| `legal.contract_risk_flagged` | sales, executive | Clause outside playbook, uncapped liability, over-cap uplift, or lapsed certification with warranty |
| `legal.security_terms_reviewed` | sales | Security terms of a deal reviewed (breach-notice period, audit rights, certification warranties) |
| `legal.regulatory_change_noted` | executive, it_security, people, operations, data, product | Regulation triaged |
| `legal.compliance_finding_raised` | executive, operations | A compliance action is needed |
| `legal.policy_update_published` | people, operations, it_security | Policy updated after a closed finding |
| `legal.regulator_notification_filed` | executive, it_security | The General Counsel (human) filed the ICO report |
| `legal.ai_risk_review_completed` | product, executive | AI risk review recommendation (pending General Counsel sign-off) |
| `legal.client_dispute_raised` | finance, delivery, executive | Disputed invoice enters a privileged matter |
| `legal.budget_submitted` | finance | Annual budget cycle response |
| `legal.hire_requested` | people | Hiring plan requisition |

### Legal subscribes to

| Source | Topics |
|---|---|
| sales | `sales.deal_won`, `sales.deal_approval_requested`, `sales.security_review_requested`, `sales.renewal_proposal_sent` |
| executive | `executive.deal_decision_made`, `executive.board_meeting_held`, `executive.budget_approved`, `executive.crisis_declared`, `executive.okrs_set`, `executive.strategy_updated` |
| customer_success | `customer_success.renewal_due`, `customer_success.renewal_confirmed` |
| delivery | `delivery.scope_change_requested` |
| finance | `finance.budget_cycle_opened`, `finance.invoice_overdue`, `finance.collections_escalated` |
| it_security | `it_security.incident_detected`, `it_security.data_breach_confirmed`, `it_security.incident_resolved`, `it_security.security_questionnaire_completed`, `it_security.certification_status_updated`, `it_security.vendor_risk_assessed`, `it_security.access_revoked` |
| operations | `operations.vendor_review_requested`, `operations.compliance_action_completed` |
| people | `people.offer_accepted`, `people.contractor_engaged`, `people.employee_left`, `people.compliance_training_completed` |
| product | `product.ai_risk_review_requested` |
| marketing | `marketing.brand_incident_raised` |
| external | `external.regulation_published` |

## 7. Risks and dependencies

| Risk | Impact | Mitigation |
|---|---|---|
| Single point of failure: one lawyer in FY2026 | Escalations queue behind the General Counsel; no cover for a breach in leave periods | Outside counsel retainer with 24-hour breach response; deputy named in the incident plan; Q2 FY2027 hire; agent deadline watch |
| Missed 72-hour ICO deadline | Enforcement exposure, reputational harm | Matter opened on `it_security.incident_detected`, clock starts at awareness, 24-hour warning, daily watch, pre-agreed filing template, phased report if facts incomplete (UK GDPR Art 33(4)) |
| Agents overreach into legal advice | Reliance on unreviewed output | Disclaimer and `advice_status` on every output, human review levels (full review for non-standard or >= £500k), agent limits in section 4 (COMPANY.md §9.4) |
| Non-standard terms agreed by Sales without Legal | Uncapped liability or IP loss | Playbook, `legal.contract_risk_flagged` blocking flag, approvals matrix (COMPANY.md §9.3); signature only after approvals recorded |
| Security warranties outrun certifications | Contractual breach if ISO 27001, Cyber Essentials Plus or SOC 2 Type II lapse or slip | No warranty of a certification not yet achieved; certification status feed from IT Security; flag on lapse |
| Regulatory surprise (EU AI Act, UK data reform, US state privacy laws) | Late compliance, client questionnaires failing | Quarterly horizon review, 2-day triage, owners assigned by area |
| Outside-counsel cost growth | Budget overrun in FY2028 (£340k line) | Panel with fixed-fee scopes, monthly spend reporting by the Legal Operations Analyst, approval above £50k per CFO (COMPANY.md §9.3) |
| Dependencies | Sales supplies accurate terms; IT Security supplies breach facts and certification status; Finance supplies overdue invoice data; Operations closes compliance actions; People supplies training completion |  Message contracts in section 6; escalation to the executive if a dependency stalls |

## 8. Sources

- COMPANY.md §1 (identity, entities, US entity from Q1 FY2027)
- COMPANY.md §3.2, §3.3, §3.5 (tier prices, Keep terms, rate card)
- COMPANY.md §5.1, §5.2, §5.4 (financial targets, cost of revenue, department envelopes)
- COMPANY.md §6.1, §6.2 (headcount by department, levels and salary bands)
- COMPANY.md §7 (billing and commercial terms, collections ladder, late payment interest)
- COMPANY.md §8 (key assumptions: time-to-hire, attrition, compliance baseline)
- COMPANY.md §9.2, §9.3, §9.4 (heads, delegations of authority, AI agent governance)
- CONVENTIONS.md §3, §6, §7 (document templates, agent contract, cross-department messaging)
