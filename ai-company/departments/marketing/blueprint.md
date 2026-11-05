# Marketing Department Blueprint

## 1. Mission and scope

**Mission.** Make Lumenhall Partners the first name a mid-size firm's board sponsor thinks of when an operational pain point meets AI, and convert that attention into qualified pipeline at a cost that supports the blended CAC targets in COMPANY.md §5.3 (£70k / £88k / £107k per new logo, sales and marketing combined). Tagline in all assets: "Strategy that keeps running." (COMPANY.md §1).

**Department head.** Sofia Lindqvist, Chief Marketing Officer, reports to the CEO (Imogen Hartley), member of the 12-person executive team (COMPANY.md §9.2).

**Funnel responsibility (COMPANY.md §5.3).** Marketing owns the top of the funnel up to the point Sales accepts a lead as qualified:

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Leads generated (marketing-qualified) | 640 | 1,200 | 2,267 |
| Qualified opportunities (25% of leads) | 160 | 300 | 567 |
| New logos needed | 24 | 45 | 85 |
| Marketing budget, £k (people + programme) | 830 | 1,850 | 4,500 |
| Marketing cost per lead (budget / leads) | about £1.3k | about £1.5k | about £2.0k |

The rise in cost per lead reflects the planned shift from UK founder-network and referral demand towards paid, event and US demand (US share of revenue 15% FY2027, 30% FY2028, COMPANY.md §1).

**In scope**

- Brand and positioning: messaging architecture for Compass, Forge and Keep (COMPANY.md §3), visual identity, tone of voice, brand-incident response.
- Demand generation: inbound lead capture and qualification (`external.lead_inbound` to `marketing.lead_generated`), paid search and LinkedIn programmes, email nurture, account-based marketing for named mid-market targets in financial services, healthcare services, logistics, manufacturing, retail and professional services.
- Content and thought leadership: reports, benchmarks (with Data), webinars, blog, case studies (with Customer Success and client consent), SEO and AI-search visibility.
- Events and partnerships: owned roundtables and dinners, sponsored conferences, partner co-marketing. From Q1 FY2027, New York events for the US launch.
- Product and service marketing: launch and pricing communications for new agent capabilities and service tiers, working from Product's roadmap and Executive's approved pricing.
- Marketing operations: CRM and marketing-automation hygiene, attribution, campaign reporting, consent and preference management (UK GDPR, PECR).

**Out of scope**

- Lead qualification beyond the marketing-qualified threshold, proposals, pricing negotiation, discounting (Sales; COMPANY.md §9.3).
- Contracts, claims review and regulatory marketing rules (Legal reviews all published case studies, comparative claims and testimonials).
- Client-facing communications during delivery and renewals (Customer Success).
- Recruiting-brand and job-board spend (People; Marketing supplies employer-brand assets when `people.job_posted` arrives).

**Guardrails.** No named client appears in any asset without a signed consent form held by Legal. No claim of measured client outcome is published without a source in the delivery record (QA by the engagement Manager). AI agents draft and analyse only; no agent publishes externally without human approval (COMPANY.md §9.4).

## 2. Org chart

```
Chief Executive Officer (Imogen Hartley)
└── Chief Marketing Officer (Sofia Lindqvist)                        [head]
    ├── Demand Generation Lead                                       [from Q2 FY2027]
    │   ├── Demand Generation Specialist (x1 FY2027, x2 FY2028)
    │   └── Marketing Analyst (x1 FY2027, x2 FY2028)
    ├── Senior Product Marketing Specialist (x1 FY2027, x2 FY2028)
    ├── Marketing Operations Specialist (x1 FY2026, x2 FY2028)
    ├── Content Marketing Specialist (x1 FY2026 to FY2027, x2 FY2028)
    └── Events Specialist (x1 FY2027, x2 FY2028)

AI agents (each with a named human owner, section 4)
├── Lead Qualification Agent          owner: Demand Generation Lead (CMO until Q2 FY2027)
├── Content Drafting Agent            owner: Content Marketing Specialist
├── Campaign Analytics Agent          owner: Marketing Operations Specialist
├── SEO and Search Visibility Agent   owner: Content Marketing Specialist
├── Event Logistics Agent             owner: Events Specialist
├── Brand Monitoring Agent            owner: Chief Marketing Officer
├── Case Study Production Agent       owner: Senior Product Marketing Specialist
└── Account-Based Marketing Research Agent  owner: Demand Generation Lead
```

Year-1 shape: three humans (CMO, Marketing Operations Specialist, Content Marketing Specialist) plus three agents. The CMO personally runs demand generation, brand, product marketing and events until the Demand Generation Lead and Events Specialist start in FY2027; during that period the agents carry qualification, drafting and reporting load.

## 3. Roles

Salary bands are the COMPANY.md §6.2 band for the level key. Planned base salaries inside the band are given in the notes below the table. Y1, Y2, Y3 are year-end humans (COMPANY.md §6.1 row: 3 / 8 / 14).

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Marketing Officer | head | Chief Executive Officer | 1 | 1 | 1 | 140,000 to 200,000 (cash; plus equity) | Owns brand, pipeline target and marketing budget; sits on the executive team; approves all externally published content and event commitments above £15k; owns brand-incident response with Legal; presents the funnel to the Board each quarter. |
| Demand Generation Lead | manager | Chief Marketing Officer | 0 | 1 | 1 | 92,000 to 115,000 | Owns lead volume and lead-to-qualified rate; channel mix and paid budget; ABM programme; SLA with Sales on lead hand-off; accountable owner of Lead Qualification and ABM Research agents. |
| Demand Generation Specialist | consultant | Demand Generation Lead | 0 | 1 | 2 | 55,000 to 70,000 | Runs paid search, LinkedIn and email nurture; landing pages and A/B tests; webinar registration funnels; routes `external.lead_inbound` exceptions the agent cannot classify. |
| Senior Product Marketing Specialist | senior_consultant | Chief Marketing Officer | 0 | 1 | 2 | 72,000 to 90,000 | Messaging and positioning for Compass, Forge and Keep; launch plans when `product.agent_capability_added` or `executive.pricing_change_approved` lands; sales enablement collateral; owns case-study programme with Customer Success; competitive briefs. |
| Marketing Operations Specialist | consultant | Chief Marketing Officer | 1 | 1 | 2 | 55,000 to 70,000 | CRM and automation hygiene; lead scoring model; attribution; consent and suppression lists (UK GDPR, PECR); budget tracking against programme lines; owner of Campaign Analytics Agent. |
| Content Marketing Specialist | consultant | Chief Marketing Officer | 1 | 1 | 2 | 55,000 to 70,000 | Editorial calendar; reports, benchmarks (with Data) and blog; ghost-writing for partners; web and SEO; owner of Content Drafting and SEO agents; final human edit before publication. |
| Events Specialist | consultant | Chief Marketing Officer | 0 | 1 | 2 | 55,000 to 70,000 | Roundtables, dinners, sponsored conferences and webinars; venue and speaker logistics; post-event lead follow-up; New York events from Q1 FY2027; owner of Event Logistics Agent. |
| Marketing Analyst | analyst | Demand Generation Lead | 0 | 1 | 2 | 38,000 to 48,000 | Weekly funnel and channel reporting; cohort analysis of lead to win; data pulls for Board pack; QA of Campaign Analytics Agent outputs. |
| **Total humans** | | | **3** | **8** | **14** | | Equals COMPANY.md §6.1 marketing row (3 / 8 / 14). |

**Planned base salaries (inside band), used for the people-cost check.**

| Role | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Chief Marketing Officer | £145,000 | £148,000 (£150,000 from FY2028) | £150,000 |
| Demand Generation Lead | n/a | £94,000 (£95,000 from FY2028) | £95,000 |
| Demand Generation Specialist | n/a | £60,000 | £60,000 (new FY2028 hire £62,000) |
| Senior Product Marketing Specialist | n/a | £80,000 | £80,000 (new FY2028 hire £82,000) |
| Marketing Operations Specialist | £62,000 | £63,000 (£64,000 from FY2028) | £64,000 (new hire £66,000) |
| Content Marketing Specialist | £58,000 | £59,000 (£60,000 from FY2028) | £60,000 (new hire £58,000) |
| Events Specialist | n/a | £60,000 | £60,000 (new FY2028 hire £62,000) |
| Marketing Analyst | n/a | £44,000 (£45,000 from FY2028) | £45,000 (new FY2028 hire £46,000) |

**People-cost reconciliation to COMPANY.md §5.4** (loaded cost = base x 1.28, COMPANY.md §5.2; start-of-quarter start dates from section 5; US hires are not planned in the department's own headcount before FY2028, so no +15% uplift is applied). Full build-up lives in `economics.md`; this is the cross-check.

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Average base payroll in year | £220.5k | £471.5k | £781k |
| x 1.28 loaded | £282k | £604k | £1,000k |
| COMPANY.md §5.4 people budget | £280k | £600k | £1,000k |
| Variance | +£2k | +£4k | £0 |

All three years are within the £5k tolerance.

## 4. AI agents

Every agent is registered in the agent register (Data and IT Security) with a named human owner and operates under COMPANY.md §9.4: agents draft, analyse, monitor and propose; they never publish externally, sign anything, commit spend above their limits, or contact a regulator. Totals: 3 / 8 / 16 (COMPANY.md §6.1 marketing row). Average fully loaded cost is within the £20k to £35k per agent-year range in COMPANY.md §5.2.

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Lead Qualification Agent | Demand Generation Lead (CMO until Q2 FY2027) | Enriches and scores each `external.lead_inbound` (firm size 200 to 2,000 employees, sector fit, named pain point, board-level sponsor signal), classifies as marketing-qualified or nurture, and drafts the `marketing.lead_generated` hand-off. | May score, tag and route leads and write to CRM. May not send first-touch email to a prospect without human template approval; may not mark a lead as disqualified for a named enterprise target without human review; suppresses any contact on the PECR or unsubscribe list automatically. | 1 | 2 | 3 |
| Content Drafting Agent | Content Marketing Specialist | Drafts blog posts, report sections, newsletters, LinkedIn posts, webinar scripts and sales one-pagers from approved messaging and published research. | Drafts only; nothing is published without Content Marketing Specialist edit and CMO approval. Cannot cite a client by name, quote a client outcome or state a price not in COMPANY.md §3. All drafts carry a source list. | 1 | 2 | 3 |
| Campaign Analytics Agent | Marketing Operations Specialist | Weekly and monthly funnel, channel, cost-per-lead and attribution reports; anomaly alerts on spend pacing and conversion; feeds `data.kpi_report_published` consumers. | Read-only on ad platforms and CRM; cannot change bids or budgets. Flags to a human when spend pacing deviates more than 15% from plan or lead-to-qualified rate falls below 18%. | 1 | 1 | 2 |
| SEO and Search Visibility Agent | Content Marketing Specialist | Keyword and topic research, on-page recommendations, tracking of Lumenhall visibility in search and in AI-assistant answers for target queries. | Recommends and drafts metadata; web changes are made by a human. No purchase of links or sponsored placements. | 0 | 1 | 2 |
| Event Logistics Agent | Events Specialist | Builds run-of-show, invitee lists, reminder sequences and post-event follow-up lists; reconciles registrations and attendance; drafts `marketing.event_scheduled` details. | Cannot sign venue or sponsorship contracts; any single commitment above £5k requires Events Specialist approval and above £15k requires CMO. Invitations only to contacts with valid consent. | 0 | 1 | 2 |
| Brand Monitoring Agent | Chief Marketing Officer | Monitors press, social and review sites for mentions of Lumenhall, executives and key client sectors; classifies severity and drafts a `marketing.brand_incident_raised` notice for human review. | Detect and draft only. Never posts, replies or comments publicly. Severity 1 (legal, data breach, executive misconduct allegation) is escalated to the CMO within 15 minutes of detection during business hours. | 0 | 1 | 2 |
| Case Study Production Agent | Senior Product Marketing Specialist | After `customer_success.case_study_approved`, assembles the delivery facts, metrics and quotes into a draft case study with source references for engagement Manager and Legal review. | Uses only documented, client-approved material. Cannot contact the client or publish. Every metric must cite a delivery record. | 0 | 0 | 1 |
| Account-Based Marketing Research Agent | Demand Generation Lead | Builds target account lists and trigger-event dossiers (leadership change, regulatory pressure, results announcements) for ABM tiers; supplies Sales with account briefs. | Public sources and licensed data only. No scraping behind logins, no personal data beyond business contact details. Lists are reviewed by Demand Generation Lead before use. | 0 | 0 | 1 |
| **Total agents** | | | | **3** | **8** | **16** |

Y1 agents (Lead Qualification, Content Drafting, Campaign Analytics) are provisioned in the first month (5-day provisioning, COMPANY.md §8). Agent-to-human ratio in the department is 1.0 in FY2026 falling to 1.14 by FY2028, above the company leverage target because marketing work is document and data heavy; human review gates remain on every external output.

## 5. Hiring plan

Hires are requested through `marketing.hire_requested`, which triggers People's requisition flow and then CEO headcount approval (`executive.headcount_approved`); average time to hire is 45 days (COMPANY.md §8), so requisitions are opened roughly one quarter before the start date. Start dates are the first day of the stated quarter. The CMO is in seat from the start of FY2026 and counted in Y1.

### FY2026 (quarterly)

| Quarter | Role | Count | Trigger |
|---|---|---|---|
| Q1 | Chief Marketing Officer (in seat at simulation day 0, Monday 2026-01-05) | 1 | Founding executive team |
| Q2 | Marketing Operations Specialist | 1 | Series A closes in Q2 (COMPANY.md §1); CRM and lead scoring must be live before paid programmes scale; 160 qualified opportunities needed in the year |
| Q3 | Content Marketing Specialist | 1 | First three published engagements make case studies and a benchmark report possible; editorial cadence of two pieces per month cannot be sustained by CMO plus agent alone |
| Q4 | none (requisitions for FY2027 roles opened in Q4) | 0 | Budget cycle opened by `finance.budget_cycle_opened`; FY2027 plan approved via `executive.budget_approved` |

FY2026 year-end total: 3 humans, 3 agents.

### FY2027 (by half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 | Demand Generation Lead | 1 | Q2 | Lead volume run rate above 80 per month; CMO span of control exceeds 4 directs plus 3 agents; owner needed for Lead Qualification Agent |
| H1 | Senior Product Marketing Specialist | 1 | Q2 | Three or more new service or agent capability launches in a half (Product roadmap) and Sales enablement backlog above 6 weeks |
| H2 | Demand Generation Specialist | 1 | Q3 | Paid and nurture programmes exceed £60k per quarter; US launch campaigns |
| H2 | Events Specialist | 1 | Q3 | At least 2 events per quarter after New York opens in Q1 FY2027; event logistics hours above 0.5 FTE |
| H2 | Marketing Analyst | 1 | Q4 | Weekly funnel reporting and Board cohort analysis exceed 0.4 FTE of Marketing Operations Specialist capacity |

FY2027 year-end total: 8 humans (5 hires), 8 agents. Cost of lead and pipeline growth is gated: if year-to-date qualified opportunities are below 85% of plan at the end of Q2, the Demand Generation Specialist, Events Specialist and Analyst requisitions are held until the CEO re-approves.

### FY2028 (by half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 | Senior Product Marketing Specialist | 1 | Q2 | US messaging localisation and vertical packaging for 30% US revenue share |
| H2 | Demand Generation Specialist | 1 | Q3 | Programme spend above £250k per quarter; separate US and UK paid channels |
| H2 | Marketing Operations Specialist | 1 | Q3 | Two regions, two consent regimes (UK GDPR/PECR and US state privacy and CAN-SPAM); Series B-grade attribution reporting |
| H2 | Content Marketing Specialist | 1 | Q4 | US editorial voice and ghost-writing programme; webinar cadence doubles |
| H2 | Events Specialist | 1 | Q4 | New York and London event calendar above 3 events per quarter |
| H2 | Marketing Analyst | 1 | Q4 | Two-region reporting and ABM account-level analytics |

FY2028 year-end total: 14 humans (6 hires), 16 agents (Case Study Production and ABM Research agents added in FY2028; Lead Qualification and Content Drafting agents scale to 3 each).

Agent additions: Y1 provisioned at start (3). FY2027 adds SEO and Search Visibility, Event Logistics and Brand Monitoring agents plus one more each of Lead Qualification and Content Drafting (net +5). FY2028 adds Case Study Production and ABM Research agents plus one each of Lead Qualification, Content Drafting, Campaign Analytics, SEO, Event Logistics and Brand Monitoring (net +8).

## 6. Interfaces

Topics are those in the department topic map (CONVENTIONS section 7, `core/topics.py`).

### Marketing publishes

| Topic | Consumers (primary) | When |
|---|---|---|
| `marketing.lead_generated` | Sales, Data | A lead meets the marketing-qualified threshold; hand-off with source, firm size, sector, pain point and score. |
| `marketing.campaign_launched` | Sales, Finance, Data | A campaign goes live; carries budget and target lead volume so Finance can track programme spend. |
| `marketing.content_published` | Sales, Customer Success | A report, case study or post is published after human approval. |
| `marketing.event_scheduled` | Sales, Operations | An event date and venue are confirmed; Operations arranges space and travel. |
| `marketing.case_study_requested` | Customer Success | Marketing asks for a client reference or case study from a completed or live engagement. |
| `marketing.brand_incident_raised` | Executive, Legal | A reputational or compliance risk in public view needs a response. |
| `marketing.budget_submitted` | Finance | Annual budget submission in answer to `finance.budget_cycle_opened`. |
| `marketing.hire_requested` | People | A hiring trigger in section 5 is reached. |

### Marketing subscribes

| Topic | Source | Marketing response |
|---|---|---|
| `external.lead_inbound` | External | Qualify and score; publish `marketing.lead_generated` or place in nurture. |
| `sales.lead_qualified` | Sales | Close the loop on lead source quality; update lead-to-qualified rate and channel attribution. |
| `sales.deal_lost` | Sales | Record loss reason; feed positioning and competitive messaging reviews. |
| `customer_success.case_study_approved` | Customer Success | Start case-study production with Legal review. |
| `customer_success.feedback_received` | Customer Success | Mine for quotes, themes and testimonial candidates (consent first). |
| `data.benchmark_ready` | Data | Turn the benchmark into a report, webinar and press release. |
| `product.agent_capability_added` | Product | Plan launch content and Sales enablement. |
| `product.release_shipped` | Product | Update web and collateral; schedule a launch post. |
| `product.roadmap_published` | Product | Align quarterly editorial and launch calendar. |
| `executive.okrs_set` | Executive | Set marketing OKRs and funnel targets. |
| `executive.strategy_updated` | Executive | Revise messaging and ICP priorities. |
| `executive.budget_approved` | Executive | Release programme budget by quarter. |
| `executive.pricing_change_approved` | Executive | Update every published price reference and enablement material within two business days. |
| `executive.crisis_declared` | Executive | Pause scheduled posts and campaigns; switch to crisis communications under Executive direction. |
| `finance.budget_cycle_opened` | Finance | Prepare and submit `marketing.budget_submitted`. |
| `people.job_posted` | People | Supply employer-brand assets and promote the role if People requests. |

### Departments depended on

- **Sales** (rate of acceptance of leads, win and loss reasons, enablement needs): shared lead SLA; unaccepted marketing-qualified leads are reviewed weekly.
- **Customer Success** (references, case studies, feedback): consent and timing for any client-facing story.
- **Data** (benchmarks, KPI reports, attribution models): shared definitions for lead, MQL and qualified opportunity.
- **Product** (roadmap, release notes, capability claims): marketing claims must match shipped capability.
- **Legal** (claims review, privacy, case-study consent) and **People** (hiring, employer brand), **Finance** (budget, programme spend), **Operations** (events logistics, vendor onboarding), **IT Security** (marketing stack access, data handling).

### Departments served

Sales (leads, enablement, content), Customer Success (advocacy and expansion content), Executive (Board funnel reporting, brand and crisis communications), People (employer brand), Delivery (thought-leadership authors, case-study subject matter).

## 7. Risks and dependencies

| Risk | Likelihood / impact | Mitigation | Owner |
|---|---|---|---|
| Lead volume below plan (640 / 1,200 / 2,267 leads) because UK founder-network demand saturates | Medium / High: each 10% shortfall in leads costs about 2.4 new logos in FY2026 at plan conversion | Diversify channels by Q3 FY2026 (events, partnerships, paid search); monthly pipeline-cover review with Sales; hiring gates in section 5 | CMO |
| Cost per lead inflation as paid channels scale and US launch begins | Medium / Medium | Channel-level CAC floor; reallocate programme budget monthly; cap any single channel at 35% of programme spend | Demand Generation Lead |
| Unapproved AI-generated claim published (factual error, uncited client result, price quoted wrongly) | Low / High | Human edit and CMO approval gate; source list required on every draft; claims log reviewed by Legal quarterly; agents have no publishing rights (COMPANY.md §9.4) | Content Marketing Specialist |
| Client confidentiality breach in a case study | Low / High | Written consent held by Legal; Legal reviews every case study; Case Study Production Agent restricted to approved delivery records | Senior Product Marketing Specialist |
| PECR/UK GDPR breach through unlawful outreach or stale consent | Low / High (ICO fine, reputational) | Consent and suppression managed by Marketing Operations; Lead Qualification Agent auto-suppresses opt-outs; quarterly list audit with Legal; US state privacy rules assessed before the New York launch | Marketing Operations Specialist |
| Brand incident (negative press, delivery failure surfaced publicly, security incident) | Low / High | Brand Monitoring Agent from FY2027; incident playbook with Legal and Executive; holding statements prepared for the top five scenarios | CMO |
| Key-person dependence on the CMO in FY2026 (single point of failure for brand, demand and events) | High / Medium | Agents carry routine load; Marketing Operations Specialist documents all runbooks; Demand Generation Lead hired Q2 FY2027 | CMO and CEO |
| Slow hiring (45-day time-to-hire) delays programme launches | Medium / Medium | Requisitions opened a full quarter ahead; agency or freelance cover capped at £40k per year inside non-people budget | CMO and Chief People Officer |
| Marketing stack outage or compromised ad account | Low / Medium | Two-person admin rule on ad accounts; MFA; access via IT Security provisioning | Marketing Operations Specialist |
| Dependence on Product for accurate capability claims and on Customer Success for references | Medium / Medium | Quarterly alignment on roadmap and reference pipeline; `product.agent_capability_added` is the only source for capability marketing | Senior Product Marketing Specialist |

**Key dependencies.** Series A funding timing (Q2 FY2026) for programme spend; Finance for budget release (`executive.budget_approved`); Sales for timely lead acceptance (target within 1 business day); Data for benchmarks; Legal for consent and claim review; Customer Success for approved case studies; IT Security for marketing-stack access and certification evidence (ISO 27001 achieved by end FY2026, which is a key proof point in FY2027 enterprise content).

## 8. Sources

- COMPANY.md §1 Identity (tagline, geography, US launch, Series A timing, fiscal year)
- COMPANY.md §2 Business model (land and expand, ideal client)
- COMPANY.md §3 Service lines and pricing (Compass, Forge, Keep; rate card)
- COMPANY.md §5.2 Cost sanity check (loaded cost, programme spend, agent cost range)
- COMPANY.md §5.3 Commercial funnel (leads, qualified opportunities, CAC)
- COMPANY.md §5.4 Department budget envelopes (marketing: people 280 / 600 / 1,000; non-people 550 / 1,250 / 3,500; total 830 / 1,850 / 4,500)
- COMPANY.md §6 and §6.1 Headcount plan (marketing 3 / 8 / 14 humans, 3 / 8 / 16 agents)
- COMPANY.md §6.2 Levels and salary bands
- COMPANY.md §8 Key assumptions (time-to-hire, agent provisioning)
- COMPANY.md §9.2 Executive team; §9.3 Delegations of authority; §9.4 AI agent governance
- CONVENTIONS.md section 7 and `core/topics.py` (marketing topic map)
