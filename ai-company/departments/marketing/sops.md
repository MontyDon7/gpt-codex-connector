# Marketing Standard Operating Procedures

These procedures govern the `marketing` department (brand, demand generation, content, events, lead generation; agent class `MarketingAgent`). The department head is the Chief Marketing Officer, Sofia Lindqvist (COMPANY.md §9.2). Department budget is £830k in FY2026 (£280k people, £550k non-people), £1,850k in FY2027 and £4,500k in FY2028 (COMPANY.md §5.4). Headcount is 3 humans and 3 AI agents at end FY2026, 8 and 8 at end FY2027, 14 and 16 at end FY2028 (COMPANY.md §6.1). The lead target the SOPs serve is 640 / 1,200 / 2,267 leads for FY2026 / FY2027 / FY2028 (COMPANY.md §5.3).

Conventions used throughout:

- Steps are marked `[human]` or `[agent]`. Agents draft, analyse, score, monitor and propose; they never publish externally-attributed claims, approve spend above £10,000, or release client names without the human approvals named in the SOP (COMPANY.md §9.4).
- Role names are working titles: **CMO** (Sofia Lindqvist), **Demand Generation Lead**, **Content and Events Lead**, and the marketing agents **Lead Qualification Agent**, **Content Drafting Agent** and **Campaign Analytics Agent**. Each agent has the CMO or a named lead as accountable owner and is listed in the agent register (COMPANY.md §9.4).
- "Business day" means Monday to Friday excluding UK bank holidays. SLAs are measured from message receipt on the bus.
- Business IDs follow CONVENTIONS.md §4: lead `LD-00001`, client `CL-0001`, deal `DL-0001`, budget cycle `BUD-2026`, requisition `REQ-0001`. Marketing adds three department-local IDs: campaign `CMP-2026-01`, content item `CNT-2026-001`, event `EVT-2026-01`.
- Email and outbound controls common to every SOP: UK GDPR and DPA 2018 lawful basis recorded per contact (legitimate interest for corporate B2B contacts, consent for individuals and sole traders), PECR opt-out honoured within 1 business day via the central suppression list, ASA/CAP Code substantiation for every performance claim, no client name, logo or quote without written client approval.

## Overview

| SOP id | Title | Trigger | Owner | SLA |
|---|---|---|---|---|
| SOP-MARKETING-01 | Inbound lead intake, scoring and hand-off | `external.lead_inbound` | Demand Generation Lead | Scored and published within 1 business day |
| SOP-MARKETING-02 | Sales-accepted lead feedback loop | `sales.lead_qualified` | Demand Generation Lead | Attribution updated within 2 business days |
| SOP-MARKETING-03 | Lost-deal analysis and nurture re-entry | `sales.deal_lost` | Demand Generation Lead | Reason coded within 3 business days; nurture within 10 |
| SOP-MARKETING-04 | Campaign planning, approval and launch | `executive.okrs_set` or `executive.strategy_updated` | CMO | Quarterly plan within 10 business days of trigger; each campaign brief to launch within 15 business days |
| SOP-MARKETING-05 | Content production and publication | `product.release_shipped`, `product.agent_capability_added`, `product.roadmap_published` or `data.benchmark_ready` | Content and Events Lead | First draft within 3 business days; publication within 8 business days |
| SOP-MARKETING-06 | Case study request and harvest | Monthly schedule (first business day) | Content and Events Lead | Requests raised within 2 business days of cut-off |
| SOP-MARKETING-07 | Case study approval and publication | `customer_success.case_study_approved` | Content and Events Lead | Published within 10 business days of approval |
| SOP-MARKETING-08 | Event scheduling and follow-up | Quarterly schedule (first business day of quarter) | Content and Events Lead | Event announced at least 28 days ahead; follow-up within 2 business days of event |
| SOP-MARKETING-09 | Brand incident detection and escalation | Daily brand-monitoring schedule | CMO | Triage within 2 hours (business hours); escalation within 4 hours |
| SOP-MARKETING-10 | Crisis communications standstill | `executive.crisis_declared` | CMO | Outbound paused within 1 hour; holding statement drafted within 4 hours |
| SOP-MARKETING-11 | Pricing change collateral refresh | `executive.pricing_change_approved` | Demand Generation Lead | Public price references corrected within 3 business days |
| SOP-MARKETING-12 | Annual budget submission | `finance.budget_cycle_opened` and `executive.budget_approved` | CMO | Submission by cycle deadline; approved envelope loaded within 5 business days |
| SOP-MARKETING-13 | Marketing hiring request and job advertising | `people.job_posted` | CMO | Requisition rationale within 5 business days of need; job post amplified within 3 business days |
| SOP-MARKETING-14 | Client feedback and voice-of-customer capture | `customer_success.feedback_received` | Content and Events Lead | Coded within 5 business days |
| SOP-MARKETING-15 | Monthly marketing performance review | Monthly schedule (3rd business day) | CMO | Pack issued by business day 5 |

## SOP-MARKETING-01: Inbound lead intake, scoring and hand-off

**Owner:** Demand Generation Lead (accountable: CMO). Agent: Lead Qualification Agent.
**Trigger:** `external.lead_inbound` (website form, event badge scan, webinar registration, referral, direct email to the shared inbox, partner introduction).
**Inputs:** message body keys `lead_id`, `company`, `contact_name`, `contact_role`, `employees`, `sector`, `source`, `message`; Companies House record; consent and lawful-basis flag; existing CRM records (to detect existing clients and open deals).

### Steps

1. [agent] Validate the payload: required keys present, email syntax valid, no duplicate `lead_id` within the last 90 days; on duplicate, merge and stop.
2. [agent] Check the suppression list and consent flag. Suppressed or opted-out contacts are recorded and closed with no further action.
3. [agent] Enrich: employee count, sector, UK or US registration, ownership (exclude companies where Lumenhall already has an open deal; route those to the owning account executive without creating a new lead).
4. [agent] Score 0 to 100 using the lead-scoring model: ICP fit 50 points (200 to 2,000 employees = 20; target sector among financial services, healthcare services, logistics, manufacturing, retail, professional services = 15; board-level or director-and-above contact = 15), intent 30 points (named pain point in message = 10; requested a conversation or diagnostic = 15; repeat visit to pricing page or two or more content downloads = 5), source quality 20 points (referral or partner = 20; event or webinar = 14; organic or paid search = 10; cold list = 4).
5. [agent] Classify: score 60 or above is a marketing-qualified lead (MQL); 40 to 59 goes to nurture; below 40 is recorded and closed with a polite automated reply.
6. [human] Demand Generation Lead reviews every MQL scoring 60 to 74 and every lead from a company above 2,000 employees or outside the UK before hand-off (sampling 10% of 75-plus scores weekly for model drift).
7. [agent] For accepted MQLs, assemble the hand-off record: summary of pain point, suggested service line (`compass`, `forge` or `keep`), source, and a recommended first call objective. Do not quote prices in the record beyond COMPANY.md §3 list prices.
8. [agent] Publish `marketing.lead_generated` to sales and data; log an activity event with the score breakdown so the decision is auditable.
9. [agent] Send the contact an acknowledgement from the shared inbox, naming a response window of 2 business days.

### Outputs and messages

- `marketing.lead_generated` (to `sales`, `data`): `lead_id`, `company`, `contact_name`, `contact_role`, `employees`, `sector`, `score`, `source`, `service_line`, `summary`, `severity` (`low`, `medium` or `high` mapped from score bands 60 to 69, 70 to 84, 85 and above).
- Internal state: lead ledger entry (`stage` = `mql` | `nurture` | `closed`), running count against the 640-lead FY2026 target (COMPANY.md §5.3).
- Activity log: `marketing.activity.lead_scored`.

### SLA and controls

- Lead scored and hand-off published within 1 business day of receipt; same business day for referral and partner sources.
- Scoring model changes require CMO approval and a back-test over the previous 90 days; no change within a quarter without the CMO's signature.
- Weekly audit by the Demand Generation Lead: 20 random closed leads and 20 random MQLs checked against the scoring rubric; error rate above 10% triggers model review.
- UK GDPR: lawful basis and source stored on the lead record; data subject access requests routed to Legal within 1 business day.

### Exceptions and escalation

- Lead from a named competitor, a journalist or a regulator: do not score; route to the CMO within 1 business day.
- Lead claiming urgency or a board mandate: Demand Generation Lead phones within 4 business hours and flags to the Chief Revenue Officer (Rahul Mehta).
- Payload fails validation twice: log `marketing.activity.lead_rejected` and notify the Data department by direct message for pipeline repair.

## SOP-MARKETING-02: Sales-accepted lead feedback loop

**Owner:** Demand Generation Lead. Agent: Campaign Analytics Agent.
**Trigger:** `sales.lead_qualified` (sales has accepted a lead as a qualified opportunity).
**Inputs:** body keys `lead_id`, `deal_id`, `client_name`, `service_line`, `amount_gbp` (estimated), `owner`; the originating marketing lead record; campaign and content touch history.

### Steps

1. [agent] Match `lead_id` to the marketing ledger; mark stage `sales_accepted` and record elapsed days from `marketing.lead_generated`.
2. [agent] Attribute the opportunity: first touch, last touch and a weighted multi-touch model (40% first, 40% last, 20% spread across middle touches). Store against the campaign (`CMP-`) and content items (`CNT-`).
3. [agent] Update the running conversion metrics: lead-to-qualified rate against the 25% benchmark (COMPANY.md §5.3), cost per qualified opportunity by channel, and pipeline value sourced.
4. [agent] If the lead's score was 60 to 74 and it converted, flag it as a model learning case for the weekly audit.
5. [human] Demand Generation Lead reviews any week in which lead-to-qualified falls below 20% or exceeds 35% and decides whether to tighten or relax the 60-point MQL threshold (recorded decision, effective next Monday).
6. [agent] Create a task for the Content and Events Lead if the opportunity cites a content gap (for example "asked for an example in logistics"); this feeds SOP-MARKETING-05.

### Outputs and messages

- No bus message is required; state is updated and a task created. Activity log: `marketing.activity.lead_attributed`.
- Where the opportunity is the first from a new campaign, the agent adds the campaign to the next `marketing.campaign_launched` performance note (SOP-MARKETING-15).

### SLA and controls

- Attribution updated within 2 business days of receipt.
- Attribution reconciles to the sales CRM at month end; unattributed qualified opportunities must be below 5%.
- Marketing-sourced pipeline is reported only after the sales CRM confirms the stage; marketing may not self-declare qualification.

### Exceptions and escalation

- `lead_id` not found in the marketing ledger: record as sales-sourced and notify the Demand Generation Lead; do not claim marketing credit.
- Disagreement between sales and marketing on source credit: CMO and Chief Revenue Officer resolve within 5 business days; default is the earliest documented touch.

## SOP-MARKETING-03: Lost-deal analysis and nurture re-entry

**Owner:** Demand Generation Lead. Agents: Campaign Analytics Agent, Lead Qualification Agent.
**Trigger:** `sales.deal_lost`.
**Inputs:** body keys `deal_id`, `client_name`, `reason` (price, competitor, timing, scope, no-decision, security), `competitor`, `amount_gbp`, `service_line`; the marketing record for the originating lead.

### Steps

1. [agent] Code the loss reason into the marketing taxonomy (price, competitor, timing, fit, trust and proof, no decision) and attach to the lead record.
2. [agent] If the originating lead came from marketing, compute the cost of acquisition spent on it (channel cost allocation plus event cost share) and add to the lost-opportunity cost ledger.
3. [agent] Identify messaging gaps: if two or more losses in a rolling 30 days share a reason (for example "trust and proof" in financial services), raise a task for the Content and Events Lead to commission a proof asset (case study, benchmark or reference call pack).
4. [human] Demand Generation Lead decides re-entry: `timing` and `no decision` losses re-enter nurture at 90 days; `competitor` and `price` losses re-enter at 180 days with a competitor-comparison asset; `security` losses re-enter only after the relevant certification milestone (COMPANY.md §8, assumption 7).
5. [agent] Schedule the nurture re-entry with `delay_days` and write the planned date to state; suppress marketing email to the contact in the interim except transactional messages.
6. [agent] Add the competitor to the competitive-intelligence watchlist if named in two or more losses.

### Outputs and messages

- No external bus message by default. When a single reason accounts for 3 or more losses in a month, the agent emits `marketing.content_published` only after the resulting proof asset is approved (see SOP-MARKETING-05); until then the finding appears in the monthly review.
- Activity log: `marketing.activity.loss_coded`; task: "Commission proof asset for <reason>".

### SLA and controls

- Reason coded within 3 business days; nurture decision within 10 business days.
- Win/loss coding is audited quarterly against sales' own loss reasons; mismatch above 15% triggers a joint review.
- No contact is added back to marketing email within 90 days of a loss if they have opted out or asked to be left alone.

### Exceptions and escalation

- Loss to a client of a competitor with a named reference: CMO informs the Chief Revenue Officer within 2 business days.
- Loss alleging misleading marketing claims: route immediately under SOP-MARKETING-09.

## SOP-MARKETING-04: Campaign planning, approval and launch

**Owner:** CMO (execution: Demand Generation Lead). Agents: Campaign Analytics Agent, Content Drafting Agent.
**Trigger:** `executive.okrs_set` or `executive.strategy_updated` (quarterly plan refresh); individual campaign briefs are raised from the approved quarterly plan.
**Inputs:** OKRs and strategy body keys (`period`, `objectives`, `priorities`, `target_sectors`); the approved marketing budget (SOP-MARKETING-12); funnel targets from COMPANY.md §5.3; last quarter's performance pack.

### Steps

1. [agent] Translate the OKRs into marketing targets: leads, MQL volume, pipeline sourced, and budget by programme (events, paid search and social, content and SEO, partnerships, PR and analyst relations). Show the derivation from COMPANY.md §5.3 (for FY2026: 640 leads for 160 qualified opportunities, 80 proposals and 24 wins).
2. [agent] Draft the quarterly plan: 3 to 5 campaigns with audience, offer, channels, budget, expected leads and cost per lead, owner and kill criteria.
3. [human] CMO reviews and approves the plan. Any single campaign above £50k non-budgeted spend needs CFO approval, above £250k CEO approval (COMPANY.md §9.3).
4. [agent] For each approved campaign create the brief and the campaign record `CMP-YYYY-NN`; draft messaging, landing page copy and email sequence; assemble the target account list (200 to 2,000 employees in target sectors).
5. [human] Content and Events Lead and Demand Generation Lead run the pre-launch checklist: ASA/CAP claim substantiation, UK GDPR lawful basis on every list, PECR suppression run within 24 hours of send, tracking tags tested, brand review, sales briefed with a one-page enablement note.
6. [human] CMO signs off launch. For any campaign naming a regulated outcome (for example "FCA-compliant") the General Counsel's team reviews the copy first.
7. [agent] On launch date, publish `marketing.campaign_launched` and start daily monitoring against the kill criteria (cost per lead more than 40% above plan after 2 weeks, or spam complaint rate above 0.1%).
8. [human] Demand Generation Lead holds a fortnightly in-flight review; campaigns that miss kill criteria are paused or revised with a recorded decision.

### Outputs and messages

- `marketing.campaign_launched` (to `sales`, `finance`, `data`): `campaign_id`, `name`, `channel`, `target_sectors`, `budget_gbp`, `start_day`, `end_day`, `expected_leads`, `audience_size`, `summary`.
- Finance uses `budget_gbp` to accrue programme spend; Data uses `campaign_id` for attribution joins.
- Internal state: campaign ledger; tasks for the Content and Events Lead and Demand Generation Lead.

### SLA and controls

- Quarterly plan within 10 business days of the trigger; brief to launch within 15 business days; no campaign launches without a signed pre-launch checklist.
- Programme spend must stay within the approved envelope (COMPANY.md §5.4); a campaign that would breach the quarterly programme line by more than 10% needs CMO and CFO approval before commitment.
- Paid spend commitments over £10,000 are human-approved; agents cannot place them (COMPANY.md §9.4).

### Exceptions and escalation

- OKRs reduce marketing priority or cut targets mid-quarter: re-plan within 5 business days and notify the CFO of any accrual released.
- A campaign's audience list is found to contain unsolicited individual subscribers: stop send, run SOP-MARKETING-09, and notify the General Counsel (Callum Fraser) within 4 business hours.

## SOP-MARKETING-05: Content production and publication

**Owner:** Content and Events Lead. Agent: Content Drafting Agent.
**Trigger:** `product.release_shipped`, `product.agent_capability_added`, `product.roadmap_published` or `data.benchmark_ready`; also any task raised by SOP-MARKETING-02, -03 or -14.
**Inputs:** the trigger body (`release_id`, `capability`, `summary`, `benchmark_id`, `metric`, `period`, `sector`); editorial calendar; brand guidelines; approved claims register.

### Steps

1. [agent] Classify the trigger: product release or capability (launch post and sales one-pager), roadmap (customer-facing summary only, never dates beyond the committed quarter), benchmark (thought-leadership report and sector-specific cuts).
2. [agent] Check the approved claims register. Any quantitative claim (for example "reduces cycle time by 30%") must cite a data source and sample; claims not on the register are flagged `needs_evidence`.
3. [agent] Draft the asset: long-form article (1,200 to 1,800 words), LinkedIn post set (3 variants), sales one-pager, and where relevant a webinar outline; apply brand voice (plain, specific, British English, no unverified superlatives).
4. [human] Content and Events Lead edits and fact-checks. Benchmarks derived from client data must be anonymised with a minimum cohort of 8 clients, confirmed by the Data department's note on the release.
5. [human] Subject-matter expert reviews technical accuracy (Product for releases, Data for benchmarks). Roadmap content additionally requires the Chief Product Officer's (Anika Rao) approval before anything forward-looking is published.
6. [human] Legal review (General Counsel's team) is mandatory for: regulatory statements, comparisons with named competitors, AI safety or compliance claims (UK AI regulatory principles, EU AI Act alignment), and any client reference.
7. [agent] Schedule publication in the editorial calendar and distribute (website, LinkedIn, newsletter, sales enablement folder).
8. [agent] On publication, publish `marketing.content_published` and track 30-day views, downloads and influenced pipeline.

### Outputs and messages

- `marketing.content_published` (to `sales`): `content_id`, `title`, `format` (`article`, `report`, `webinar`, `one_pager`, `case_study`), `topic`, `service_line`, `sector`, `url`, `summary`, `published_day`.
- Internal state: content ledger with approval trail (author agent, human editor, SME, legal where applicable).

### SLA and controls

- First draft within 3 business days of trigger; publication within 8 business days (benchmark reports within 15).
- Every published asset has an approval trail retained for 24 months; agent outputs used externally are logged for audit (COMPANY.md §9.4).
- Roadmap content is subject to a forward-looking statement review; no delivery dates beyond the next quarter.

### Exceptions and escalation

- SME or Legal review overdue by more than 3 business days: Content and Events Lead escalates to the CMO, who escalates to the relevant department head.
- Factual error found after publication: correct within 1 business day, note the correction on the page and log `marketing.activity.content_corrected`; errors in client-facing claims go to SOP-MARKETING-09.

## SOP-MARKETING-06: Case study request and harvest

**Owner:** Content and Events Lead. Agent: Content Drafting Agent.
**Trigger:** Monthly schedule (first business day of the month); also an ad hoc request from the Chief Revenue Officer for a named proof gap.
**Inputs:** list of completed engagements and high-health clients supplied by customer success; current proof gaps by sector and service line (from SOP-MARKETING-03); sector priority list.

### Steps

1. [agent] Compile the candidate list: engagements completed in the last 60 days or retained clients with a health score at or above the healthy threshold, ranked by sector gap, measurable outcome and client advocacy.
2. [human] Content and Events Lead selects up to 2 candidates per month in FY2026 (up to 4 per month from FY2027), prioritising proof for financial services, healthcare services and logistics.
3. [agent] Prepare the request pack: proposed headline, outcomes to quantify, interview questions, usage scope (name, logo, quote, metrics) and the permission wording agreed with Legal.
4. [agent] Publish `marketing.case_study_requested` to customer success; record the request as `pending` with a chase date at 10 business days.
5. [human] If there is no response by the chase date, Content and Events Lead contacts the customer success owner directly; the client is never approached by marketing without customer success consent.
6. [agent] Close the request as `declined` if the client refuses or lapses after 30 business days; record the reason.

### Outputs and messages

- `marketing.case_study_requested` (to `customer_success`): `client_id`, `client_name`, `engagement_id`, `service_line`, `sector`, `usage_scope`, `due_day`, `summary`.
- Internal state: case study pipeline (`requested`, `approved`, `drafting`, `published`, `declined`).

### SLA and controls

- Requests raised within 2 business days of the monthly cut-off.
- No client is named in any asset until customer success reports written client approval (SOP-MARKETING-07).
- Pipeline target: at least 6 published case studies in FY2026, rising with client base.

### Exceptions and escalation

- Client in dispute, in arrears or with a churn risk flag: never request; customer success owns that conversation.
- Client works in a regulated sector with additional publicity restrictions: the request pack is reviewed by Legal before dispatch.

## SOP-MARKETING-07: Case study approval and publication

**Owner:** Content and Events Lead. Agent: Content Drafting Agent.
**Trigger:** `customer_success.case_study_approved`.
**Inputs:** body keys `client_id`, `client_name`, `engagement_id`, `approved_scope` (name, logo, quote, metrics), `approver` (client contact), `expiry_day`, `summary`; the pending request from SOP-MARKETING-06.

### Steps

1. [agent] Match the approval to the pending request and verify `approved_scope`; if the scope is narrower than requested, restrict the draft accordingly (for example anonymised sector description only).
2. [agent] Draft the case study (challenge, approach, outcome, quote) using only metrics confirmed by the client and the delivery team; mark every figure with its source.
3. [human] Content and Events Lead interviews the client sponsor (30 minutes, recorded with consent) and finalises the draft.
4. [human] Client sponsor signs off the final copy in writing; customer success is copied.
5. [human] Legal reviews the final text and the use of the logo and quote against the client's contract terms.
6. [agent] Publish across the website, sales enablement library and LinkedIn; set the review date at 12 months or `expiry_day`, whichever is earlier.
7. [agent] Publish `marketing.content_published` with `format` = `case_study` and the usage scope retained in state.

### Outputs and messages

- `marketing.content_published` (to `sales`): `content_id`, `format` = `case_study`, `client_id`, `client_name` (only if named in scope), `service_line`, `sector`, `url`, `summary`.
- Internal state: case study status `published`; expiry diary entry; removal task created for `expiry_day`.

### SLA and controls

- Published within 10 business days of approval; client sign-off on final copy is mandatory and is stored with the asset.
- Metrics must reconcile to delivery records; a discrepancy above 5% blocks publication until resolved.
- Expiry enforcement: assets are taken down within 2 business days of expiry or of a client withdrawal request.

### Exceptions and escalation

- Client withdraws approval after publication: remove within 1 business day and log `marketing.activity.case_study_withdrawn`; notify customer success and Legal.
- Delivery disputes an outcome figure: hold publication, raise to the Managing Partner, Delivery (Oliver Thackeray) via customer success.

## SOP-MARKETING-08: Event scheduling and follow-up

**Owner:** Content and Events Lead. Agent: Campaign Analytics Agent.
**Trigger:** Quarterly schedule (first business day of each quarter), plus ad hoc when the quarterly plan (SOP-MARKETING-04) approves a new event.
**Inputs:** approved events budget; target sector calendar; speaker availability from delivery and executive; venue quotes; capacity in operations.

### Steps

1. [agent] Propose the event calendar for the quarter: client roundtables (20 to 30 attendees, London), sector breakfasts (40 to 60), webinars (100 to 300 registrants) and third-party conferences (sponsorship or speaking only). FY2026 allocation is mostly roundtables and webinars; US events begin only after the New York office opens in Q1 FY2027 (COMPANY.md §1).
2. [agent] Estimate cost per event (venue, catering, speakers, invitations) and expected leads, and compute cost per qualified opportunity assuming the 25% lead qualification benchmark (COMPANY.md §5.3).
3. [human] CMO approves the calendar; any sponsorship above £50k non-budgeted needs CFO approval (COMPANY.md §9.3).
4. [human] Content and Events Lead books the venue and speakers, issues the Calendar hold and agrees on the run-of-show with operations.
5. [agent] Publish `marketing.event_scheduled` to sales and operations at least 28 days before the event, with attendees' capacity, venue and logistics needs.
6. [agent] Run invitation sequences to the target account list and sales-nominated clients; handle registration within the UK GDPR consent rules.
7. [human] Event day: staff the event, capture badge scans, record attendee feedback.
8. [agent] Within 2 business days after the event, ingest attendees as `external.lead_inbound`-equivalent leads (source `event`) through the SOP-MARKETING-01 scoring path, and send the follow-up sequence.

### Outputs and messages

- `marketing.event_scheduled` (to `sales`, `operations`): `event_id`, `name`, `event_type`, `date_day`, `venue`, `city`, `capacity`, `budget_gbp`, `target_sectors`, `speakers`, `summary`.
- Internal state: event ledger (registrants, attendees, leads, pipeline influenced).

### SLA and controls

- Announced at least 28 days ahead; invitations sent at least 21 days ahead.
- Event cost per attendee above £350 or cost per lead above 150% of plan triggers a post-event review; two consecutive misses retire the format.
- Venue contracts above £10,000 are signed under the Delegations of Authority (COMPANY.md §9.3); marketing never signs contracts as an agent.

### Exceptions and escalation

- Speaker drop-out within 7 days: Content and Events Lead appoints a named substitute from delivery and informs the CMO; if no substitute, convert to a virtual session.
- Attendance below 50% of registrants: send a recording to no-shows within 24 hours; operations is notified if venue catering must be reduced.

## SOP-MARKETING-09: Brand incident detection and escalation

**Owner:** CMO. Agent: Campaign Analytics Agent (monitoring).
**Trigger:** Daily brand-monitoring schedule (social, press, review sites, search results) and any inbound report from staff, clients or sales.
**Inputs:** monitoring feed; brand guidelines; list of approved spokespeople; incident severity matrix.

### Steps

1. [agent] Scan for mentions: negative press, social complaints, impersonation, misuse of the Lumenhall name, mistaken claims in our own content, leaks of client names or confidential material.
2. [agent] Triage against the severity matrix: `low` (isolated negative comment, no reach), `medium` (verified inaccuracy or complaint with 1,000 or more views), `high` (credible press, client complaint, regulator or ASA contact, impersonation), `critical` (confirmed data or client confidentiality exposure, regulatory action, executive misconduct allegation).
3. [human] CMO confirms severity within 2 business hours of the alert (business hours, 09:00 to 18:00 UK).
4. [agent] For `medium` and above, draft the incident record: facts known, evidence links, affected parties, proposed response options.
5. [agent] Publish `marketing.brand_incident_raised` for `high` and `critical` immediately and for `medium` when it involves a client or legal exposure.
6. [human] CMO and the General Counsel agree on the response; only approved spokespeople communicate externally; no marketing agent posts publicly in response to an incident.
7. [human] If personal data is involved, hand to the General Counsel and the CISO under the data breach process; ICO notification (72 hours) is for Legal, not Marketing (COMPANY.md §9.3).
8. [agent] Monitor for 14 days after closure and record lessons learned in the incident log.

### Outputs and messages

- `marketing.brand_incident_raised` (to `executive`, `legal`): `incident_ref`, `severity`, `category` (`misinformation`, `impersonation`, `client_complaint`, `confidentiality`, `press`, `regulatory`), `channel`, `reach_estimate`, `summary`, `recommended_action`, `due_day`.
- Internal state: incident log with timestamps, decisions and approver.

### SLA and controls

- Triage within 2 business hours; `high` and `critical` published to the bus within 4 hours; `critical` also phoned to the CEO (Imogen Hartley) and the General Counsel.
- Every incident record retained for 6 years; post-incident review within 10 business days for `high` and `critical`.
- Impersonation incidents are reported to the platform within 1 business day and logged for the CISO.

### Exceptions and escalation

- Out-of-hours `critical` alert: CMO on-call phones the CEO; the agent publishes the message and pauses scheduled social and email sends.
- If Legal advises litigation hold, marketing preserves all related content and stops editing the affected assets.

## SOP-MARKETING-10: Crisis communications standstill

**Owner:** CMO. Agents: Content Drafting Agent, Campaign Analytics Agent.
**Trigger:** `executive.crisis_declared`.
**Inputs:** body keys `crisis_id`, `category`, `severity`, `summary`, `spokesperson`, `comms_lead`; scheduled outbound calendar; live campaign ledger.

### Steps

1. [agent] Immediately pause all scheduled social posts, email sends, paid ads and event invitations (except messages already sent), and write the paused list to state.
2. [agent] Review the live campaign ledger and flag any campaign whose message could be read as insensitive or misleading in the crisis context (for example a "security-first" campaign during a security incident).
3. [human] CMO confirms with the crisis lead which channels stay paused, which resume, and whether a holding statement is needed; decisions are recorded.
4. [agent] Draft a holding statement and Q&A for the executive and legal review; no draft is released without the spokesperson's and the General Counsel's approval.
5. [human] CMO coordinates with Customer Success and Sales so that client-facing teams use the same wording.
6. [agent] On crisis closure (executive release), prepare a resume plan: re-sequence campaigns, reschedule events, restore paused sends in priority order.
7. [human] CMO approves the resume plan and the Campaign Analytics Agent reports the effect on lead volume in the next monthly review.

### Outputs and messages

- When a crisis creates a brand exposure that is not already reported, the agent publishes `marketing.brand_incident_raised` (to `executive`, `legal`) with `severity` taken from the crisis and `category` = `crisis_related`.
- `marketing.campaign_launched` is emitted only on the resume of a paused campaign, with `resumed` = true and the new `start_day`.
- Internal state: paused-list, holding statement version history, resume plan.

### SLA and controls

- Outbound paused within 1 hour of the declaration; holding statement drafted within 4 hours; approved statement is the only external language.
- No agent-generated content is used in crisis communications without human approval and Legal review.
- Pause covers all brand and sales sequences marketing controls; sales sequences are paused by direct notification to the Chief Revenue Officer's team.

### Exceptions and escalation

- A scheduled send goes out during the standstill: log `marketing.activity.standstill_breach`, notify the CMO within 30 minutes, and assess retraction with Legal.
- A journalist or client demands comment: the CMO is the only point of contact until the spokesperson is confirmed.

## SOP-MARKETING-11: Pricing change collateral refresh

**Owner:** Demand Generation Lead. Agent: Content Drafting Agent.
**Trigger:** `executive.pricing_change_approved`.
**Inputs:** body keys `service_line`, `tier`, `old_price_gbp`, `new_price_gbp`, `effective_day`, `rationale`; the current list in COMPANY.md §3; inventory of assets containing prices.

### Steps

1. [agent] Search the asset inventory (website, proposal templates, sales one-pagers, decks, email sequences, event slides, case studies) for the affected tier and compute the update list with an owner per asset.
2. [agent] Draft updated copy for each asset; prices are always in GBP ex-VAT; US prices in USD at the planning rate in COMPANY.md §1 once the US launches.
3. [human] Demand Generation Lead confirms that no price is published before `effective_day`, and checks that grandfathered or in-flight proposals are left unchanged by sales.
4. [agent] Schedule the website and library updates for `effective_day`; withdraw superseded PDFs and add a redirect.
5. [human] Content and Events Lead checks every public-facing page after the update; a second person verifies a 10% sample of internal assets.
6. [agent] Notify the sales team through the enablement library and the sales channel on the same day.
7. [human] CMO reviews whether messaging needs adjusting (for example a rise on Forge Pilot affecting the land-and-expand story) and records any new positioning.

### Outputs and messages

- `marketing.content_published` (to `sales`): `content_id`, `format` = `price_update`, `tier`, `effective_day`, `summary`.
- Internal state: asset inventory marked `updated` with timestamp; withdrawn asset list.

### SLA and controls

- Public price references corrected within 3 business days of `effective_day` (and never earlier); sales enablement the same day.
- Misquoted public prices are a trading-standards risk (Consumer Protection from Unfair Trading Regulations apply to B2C, and the CAP Code requires accuracy for B2B); any known inaccuracy is corrected within 1 business day.
- Coverage check: zero known assets still showing the old price 10 business days after `effective_day`.

### Exceptions and escalation

- Asset cannot be located or is owned by a client: record and notify the owning department.
- Pricing change is reversed or amended before `effective_day`: the agent cancels scheduled updates and re-plans within 1 business day.

## SOP-MARKETING-12: Annual budget submission

**Owner:** CMO. Agent: Campaign Analytics Agent.
**Trigger:** `finance.budget_cycle_opened` (opens in Q4); approval step triggered by `executive.budget_approved`.
**Inputs:** body keys `budget_cycle` (`BUD-2026` format), `deadline_day`, `guidance`; previous year actuals; funnel targets (COMPANY.md §5.3); headcount plan (COMPANY.md §6.1); CAC target (COMPANY.md §5.3).

### Steps

1. [agent] Build the zero-based non-people budget by programme: events, paid and social, content and SEO, partnerships, PR and analyst relations, tools and platforms (marketing automation, CRM licences, analytics), agencies and freelancers.
2. [agent] Build the people budget from the headcount plan: average headcount in the year x base salary x 1.28 loaded cost (COMPANY.md §5.2); show the derivation.
3. [agent] Reconcile the programme budget to the funnel: leads needed, cost per lead and cost per qualified opportunity; cross-check the blended CAC per new logo target (COMPANY.md §5.3).
4. [human] CMO reviews, challenges and signs the submission; the CMO also states the minimum viable budget and the consequences of a cut.
5. [agent] Publish `marketing.budget_submitted` to finance with total, people, non-people and key assumptions.
6. [human] CMO attends the CFO's challenge session and records agreed amendments.
7. [agent] On `executive.budget_approved`, load the approved envelope into the department ledger, allocate quarterly phasing (heavier in Q1 and Q3 for events) and create variance-tracking tasks.
8. [human] CMO cascades the approved budget to leads within 5 business days.

### Outputs and messages

- `marketing.budget_submitted` (to `finance`): `budget_cycle`, `department` = `marketing`, `amount_gbp` (total), `people_gbp`, `non_people_gbp`, `headcount_humans`, `headcount_agents`, `assumptions`, `summary`.
- Internal state: approved budget, quarterly phasing, committed spend and variance tracker.

### SLA and controls

- Submission by `deadline_day`; approved envelope loaded within 5 business days of `executive.budget_approved`.
- The submission must reconcile to the department row in COMPANY.md §5.4 within £5k; any variance requires a written note.
- Spend above the approved envelope is blocked in the ledger and needs CFO approval above £50k and CEO approval above £250k (COMPANY.md §9.3).

### Exceptions and escalation

- Approved budget below the submission: re-plan campaigns within 5 business days, tell the CEO which targets are at risk, and ask finance to confirm whether lead targets in COMPANY.md §5.3 remain valid.
- Monthly variance above 10% of plan: raise to the CFO; sustained for 2 months, CMO presents a recovery plan.

## SOP-MARKETING-13: Marketing hiring request and job advertising

**Owner:** CMO. Agent: Campaign Analytics Agent (capacity analysis); Content Drafting Agent (job advertising copy).
**Trigger:** `people.job_posted` (a marketing or company role is advertised and marketing amplifies it); hiring requests originate from the capacity trigger below.
**Inputs:** body keys `requisition_id`, `role`, `department`, `location`, `salary_band_gbp`, `posting_url`, `closing_day`; marketing hiring plan; employer-brand assets.

### Steps

1. [agent] Monitor workload and lead volume monthly: if lead flow, content backlog or event load has exceeded plan by more than 20% for 2 consecutive months, or the approved hiring plan has a role starting next quarter, raise a hire request recommendation.
2. [human] CMO drafts the business case: role, level key from COMPANY.md §6.2, salary band, expected output and the budget line it sits in.
3. [agent] Publish `marketing.hire_requested` to people with the role, level, rationale and start date; the CEO approves new headcount outside budget (COMPANY.md §9.3).
4. [human] People department opens the requisition; marketing does not advertise a role before `people.job_posted` is received.
5. [agent] On `people.job_posted`, draft employer-brand posts, targeted outreach to relevant communities and a careers page link for the role; check that salary bands are shown if the job advertisement is required to state them.
6. [human] CMO or Content and Events Lead approves the copy and the paid recruitment budget (capped at £2,000 per role without CMO sign-off).
7. [agent] Report applications by source to People weekly until the role closes.

### Outputs and messages

- `marketing.hire_requested` (to `people`): `role`, `level` (a level key from COMPANY.md §6.2), `department` = `marketing`, `justification`, `target_start_day`, `salary_band_gbp`, `budget_line`.
- Activity log: `marketing.activity.job_amplified` with `requisition_id`, channels and spend.

### SLA and controls

- Hire request submitted at least 60 days before the intended start date (human time-to-hire is 45 days, COMPANY.md §8).
- Job post amplified within 3 business days of `people.job_posted`.
- Job adverts follow the Equality Act 2010: no age, gender or similar preferences; adverts reviewed by People.

### Exceptions and escalation

- Role not approved: hold the advertising plan and tell the CMO; do not advertise.
- Advertising spend per hire above 2% of base salary triggers a channel review.

## SOP-MARKETING-14: Client feedback and voice-of-customer capture

**Owner:** Content and Events Lead. Agent: Content Drafting Agent.
**Trigger:** `customer_success.feedback_received`.
**Inputs:** body keys `client_id`, `client_name`, `engagement_id`, `score` (NPS-style 0 to 10), `sentiment`, `themes`, `verbatim`, `summary`.

### Steps

1. [agent] Code the feedback by theme (outcomes, speed, communication, price, AI agent quality, support) and by sector; record `score` and sentiment on the client's marketing profile.
2. [agent] Identify testimonial candidates: scores of 9 or 10 with a usable verbatim; add to the case study candidate pool (SOP-MARKETING-06) only with customer success consent.
3. [agent] Identify messaging risks: any theme appearing in 3 or more negative pieces of feedback in a quarter is added to the monthly review.
4. [human] Content and Events Lead reviews the themes, adapts messaging (for example removing a claim that clients say we under-deliver) and informs Product where themes concern agent quality.
5. [agent] Remove clients scoring 6 or below from any promotional or newsletter segment pending a customer success decision; do not send marketing content to a client in an open escalation.
6. [agent] Add the feedback to the voice-of-customer library; verbatims are tagged by consent status.

### Outputs and messages

- No bus message by default. A qualifying positive testimonial results in a pending entry that triggers SOP-MARKETING-06; a negative theme raises a task for the Content and Events Lead.
- Activity log: `marketing.activity.feedback_coded`.

### SLA and controls

- Coded within 5 business days.
- Client verbatims are internal by default; external use requires customer success and client written permission (SOP-MARKETING-07).
- Feedback data is personal data (client contacts) and is handled under UK GDPR with a 24-month retention.

### Exceptions and escalation

- Feedback alleges a regulatory, safety or ethical issue: route to the CMO and the General Counsel within 1 business day.
- Feedback names an individual employee: do not circulate beyond customer success and People.

## SOP-MARKETING-15: Monthly marketing performance review

**Owner:** CMO. Agent: Campaign Analytics Agent.
**Trigger:** Monthly schedule (third business day of the month, after the finance month-end close).
**Inputs:** lead ledger; campaign and event ledgers; content metrics; approved budget and actuals; CRM pipeline and win data; Data department benchmark and KPI report.

### Steps

1. [agent] Compile the month: leads by source, MQL rate, lead-to-qualified conversion against 25% (COMPANY.md §5.3), pipeline sourced, cost per lead, cost per qualified opportunity, content output and engagement, event performance, brand incidents.
2. [agent] Compute spend against the envelope (COMPANY.md §5.4): year-to-date non-people spend, accrued and committed commitments, and forecast to year end.
3. [agent] Compute progress against the FY2026 targets in `kpis.md` and flag any KPI more than 15% off plan.
4. [human] CMO reviews and annotates the pack, reconciles to finance's month-end figures, and records decisions: reallocate budget, pause campaigns, change thresholds.
5. [human] CMO presents to the Chief Revenue Officer in the monthly pipeline review and sends the pack to the CEO and the CFO.
6. [agent] Update state and KPIs from the signed pack; raise tasks for each decision.
7. [agent] Where a campaign is retired or extended, emit the corresponding `marketing.campaign_launched` update (for example with `status` = `extended`) so sales and finance can see the change.

### Outputs and messages

- `marketing.campaign_launched` (to `sales`, `finance`, `data`) only for new, resumed or materially changed campaigns, with `campaign_id`, `status`, `budget_gbp`, `summary`.
- `marketing.content_published` (to `sales`) for the monthly sales enablement digest, with `format` = `digest`.
- Internal state: KPI snapshot (`leads_generated`, `mql_rate`, `cost_per_lead`, `pipeline_sourced_gbp`), decisions log.

### SLA and controls

- Pack issued by the fifth business day; finance reconciliation difference under £2,500; any unreconciled item is listed with an owner.
- Targets and definitions live in `kpis.md`; the review cannot redefine a KPI mid-year without CEO approval.
- Spend above the cumulative envelope by more than 10% requires immediate CFO notice (SOP-MARKETING-12).

### Exceptions and escalation

- Missed lead target for two consecutive months: CMO and Chief Revenue Officer hold a joint recovery session within 5 business days.
- Data quality issue in a source system: Campaign Analytics Agent notes the limitation in the pack and the Data department is notified.
