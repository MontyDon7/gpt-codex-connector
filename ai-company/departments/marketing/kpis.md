# Marketing KPIs

Department: `marketing` (agent class `MarketingAgent`), headed by the Chief Marketing Officer, Sofia Lindqvist (COMPANY.md §9.2). Scope: brand, demand generation, content, events and lead generation. Budget: £830k / £1,850k / £4,500k (COMPANY.md §5.4). Headcount: 3 / 8 / 14 humans and 3 / 8 / 16 agents (COMPANY.md §6.1). All figures are modeled assumptions, not real data.

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| leads_generated | Leads generated (`marketing.lead_generated`) | count / year | 640 | 1,200 | 2,267 | higher is better | weekly | Chief Marketing Officer |
| lead_to_qualified_rate | Lead-to-qualified rate (leads accepted by Sales as `sales.lead_qualified`) | percent | 25.0 | 25.0 | 25.0 | higher is better | monthly | Demand Generation Manager |
| lead_response_hours | Inbound lead first-touch time (business hours, `external.lead_inbound` to `marketing.lead_generated`) | hours (p90) | 8 | 6 | 4 | lower is better | weekly | Demand Generation Manager |
| cost_per_lead | Marketing cost per lead | GBP | 1,297 | 1,542 | 1,985 | lower is better | monthly | Chief Marketing Officer |
| cost_per_qualified_lead | Marketing cost per sales-qualified lead | GBP | 5,188 | 6,167 | 7,937 | lower is better | monthly | Chief Marketing Officer |
| marketing_cost_per_new_logo | Marketing cost per new logo | GBP | 34,583 | 41,111 | 52,941 | lower is better | quarterly | Chief Marketing Officer |
| inbound_lead_share | Inbound share of leads (content, search, referral, events vs outbound) | percent | 45.0 | 50.0 | 55.0 | higher is better | monthly | Demand Generation Manager |
| us_lead_share | US share of leads generated | percent | 0.0 | 15.0 | 30.0 | target (track to plan) | quarterly | Chief Marketing Officer |
| content_assets_published | Long-form assets published (`marketing.content_published`) | count / year | 48 | 120 | 260 | higher is better | monthly | Content and Events Lead |
| content_qa_first_pass_rate | Agent-drafted content passing human QA first time | percent | 90.0 | 93.0 | 95.0 | higher is better | monthly | Content and Events Lead |
| events_run | Events and webinars scheduled and run (`marketing.event_scheduled`) | count / year | 6 | 14 | 26 | higher is better | quarterly | Content and Events Lead |
| case_studies_published | Approved client case studies published | count / year | 4 | 10 | 18 | higher is better | quarterly | Content and Events Lead |
| lost_deal_reactivation_rate | Lost deals (`sales.deal_lost`) re-engaged into nurture who return to qualified | percent | 8.0 | 10.0 | 12.0 | higher is better | quarterly | Demand Generation Manager |
| brand_incident_first_response_hours | Brand incident first response time (`marketing.brand_incident_raised`) | hours (p90) | 4 | 4 | 2 | lower is better | per incident, reviewed monthly | Chief Marketing Officer |
| budget_variance_pct | Marketing spend variance to approved budget (absolute) | percent | 5.0 | 5.0 | 5.0 | lower is better (ceiling) | monthly | Chief Marketing Officer |

## 2. Definitions and formulas

Fiscal year is the calendar year; Year 1 = FY2026 (COMPANY.md §1). Counts are for the full fiscal year. Rates and times are measured over the period reported.

| KPI id | Formula and rules |
|---|---|
| leads_generated | Count of distinct leads (`LD-nnnnn`) for which marketing emitted `marketing.lead_generated` in the period. Duplicates (same contact email or same company within 30 days) count once. Targets equal the commercial funnel (COMPANY.md §5.3: 640 / 1,200 / 2,267). |
| lead_to_qualified_rate | `sales.lead_qualified` count for leads created in the period / `leads_generated` for the same cohort x 100. Cohort basis, measured 90 days after creation, so the latest quarter is provisional. Target 25% (COMPANY.md §5.3, §8 item 2). |
| lead_response_hours | 90th percentile of business hours (Mon to Fri 08:00 to 18:00 UK) between receipt of `external.lead_inbound` and emission of `marketing.lead_generated` or a documented disqualification. Excludes bank holidays. |
| cost_per_lead | Marketing department total cost (people + non-people, `economics.md` §1) / `leads_generated`. FY2026: £830k / 640 = £1,297. FY2027: £1,850k / 1,200 = £1,542. FY2028: £4,500k / 2,267 = £1,985. |
| cost_per_qualified_lead | Marketing department total cost / qualified opportunities (funnel: 160 / 300 / 567, COMPANY.md §5.3). £830k / 160 = £5,188; £1,850k / 300 = £6,167; £4,500k / 567 = £7,937. |
| marketing_cost_per_new_logo | Marketing department total cost / new logos (24 / 45 / 85, COMPANY.md §5.1). £830k / 24 = £34,583; £1,850k / 45 = £41,111; £4,500k / 85 = £52,941. This is the marketing component of blended CAC (see section 4). |
| inbound_lead_share | Leads whose first touch is content, organic or paid search, referral, event or webinar / `leads_generated` x 100. The remainder is outbound sequences and partner introductions run with Sales. |
| us_lead_share | Leads with a US-domiciled company (HQ or contracting entity) / `leads_generated` x 100. Tracks the US share of revenue plan (0% / 15% / 30%, COMPANY.md §1); a miss of more than 5 points triggers a regional programme review. US programme spend begins before the Q1 FY2027 New York opening. |
| content_assets_published | Count of long-form assets (reports, benchmark papers, case studies, point-of-view articles, webinar recordings) published; one `marketing.content_published` message per asset. Social posts and newsletters are excluded. |
| content_qa_first_pass_rate | Agent-drafted assets approved by the human editor without substantive rewrite / agent-drafted assets reviewed x 100. A substantive rewrite is more than 20% of words changed or any factual correction. Supports the human QA rule in COMPANY.md §9.4. |
| events_run | Events and webinars held (each announced via `marketing.event_scheduled`), counting only those that took place. Sponsored third-party events count if Lumenhall had a speaking slot or booth. |
| case_studies_published | Case studies published with written client approval (`customer_success.case_study_approved`) after a `marketing.case_study_requested`. Anonymised studies count only if the client consented to anonymised use in the contract. |
| lost_deal_reactivation_rate | Lost deals tagged to nurture within 14 days of `sales.deal_lost` that reach `sales.lead_qualified` again within 12 months / lost deals tagged to nurture x 100. |
| brand_incident_first_response_hours | 90th percentile of hours between `marketing.brand_incident_raised` creation and the first documented response (holding statement or takedown request) by a named human. Severity `high` or `critical` incidents also notify the CEO via the executive subscription. |
| budget_variance_pct | `abs(actual spend - budget to date) / budget to date x 100`, programme (non-people) lines. Target is a ceiling of 5%; breach is reported to Finance ahead of `finance.budget_variance_flagged`. |

## 3. Reporting cadence and data sources

| Cadence | Forum | Content | Data source |
|---|---|---|---|
| Weekly | Marketing stand-up (CMO, Demand Generation Manager, Content and Events Lead) | leads_generated, lead_response_hours, content pipeline | CRM lead records, marketing-automation platform, agent activity log |
| Monthly | Marketing performance review, shared with the CRO | All monthly KPIs, spend vs budget, channel cost per lead | CRM, web analytics, finance month-end close (`finance.month_end_closed`), ad platforms |
| Quarterly | Business review with Sales, Data and Finance; input to the Board pack | Cost per new logo, cohort lead-to-qualified, events, case studies, reactivation, US share | Data department KPI report (`data.kpi_report_published`), Sales pipeline, `data.benchmark_ready` |
| Annually | Budget cycle (opens Q4, `finance.budget_cycle_opened`) | Target reset and `marketing.budget_submitted` | `economics.md`, prior-year actuals, OKRs (`executive.okrs_set`) |

Systems of record: the CRM for leads and attribution (UTM and first-touch rules), the marketing-automation platform for email and campaign tracking, web analytics for traffic and conversion, finance ledger for cost. The Data department owns the attribution model and signs off the reported figures each quarter; marketing may not restate a prior quarter without Data and Finance agreement.

Data quality controls: leads without a source field are excluded from `inbound_lead_share` and reported separately (must be below 2% of leads); consent basis (UK GDPR and PECR) is recorded per lead, and leads without a lawful basis are not contacted and not counted as `leads_generated`.

## 4. Links to company targets

| Company target | Source | How marketing KPIs roll up |
|---|---|---|
| Leads 640 / 1,200 / 2,267; 25% lead-to-qualified; qualified opportunities 160 / 300 / 567 | COMPANY.md §5.3 | `leads_generated` and `lead_to_qualified_rate` are the top of the funnel; every point lost on the 25% rate needs a proportional extra lead volume to protect the 24 / 45 / 85 new-logo plan (COMPANY.md §5.1). |
| Blended CAC per new logo £70k / £88k / £107k (total sales + marketing cost / new logos) | COMPANY.md §5.3, §5.4 | Marketing (£830k, £1,850k, £4,500k) plus Sales (£850k, £2,100k, £4,600k) = £1,680k / £3,950k / £9,100k; divided by 24 / 45 / 85 new logos = £70k / £87.8k / £107.1k. Marketing's share is `marketing_cost_per_new_logo` (about 49%, 47% and 49% of blended CAC). |
| Marketing programme spend £550k / £1,250k / £3,500k (non-people line of the department budget) | COMPANY.md §5.4, §5.2 | `budget_variance_pct` holds spend inside the envelope that rolls into the £0.6m / £1.9m / £4.1m marketing and sales programme line. |
| Revenue £6.0m / £19.5m / £46.2m; 24 / 65 / 140 active clients | COMPANY.md §5.1 | New-logo volume is the marketing-dependent part of active clients; the funnel KPIs are the leading indicators. |
| US share of revenue 0% / 15% / 30% | COMPANY.md §1 | `us_lead_share` is the leading indicator, given a 75-day sales cycle (COMPANY.md §5.3). |
| Win rate 30%, average sales cycle 75 / 75 / 70 days | COMPANY.md §5.3 | Lead quality (`lead_to_qualified_rate`) and case-study evidence (`case_studies_published`) support win rate; marketing does not own win rate. |
| Agent governance: no unreviewed client-facing release; named human owner per agent | COMPANY.md §9.4 | `content_qa_first_pass_rate` evidences human QA of agent-drafted content. |
| Retention and expansion (NRR 115% / 118%; Keep attach) | COMPANY.md §5.1, §2 | Case studies and event content support expansion marketing with Customer Success; no marketing KPI is tied directly to NRR. |

Headcount context: 3 humans in FY2026 (CMO plus two specialists) and 3 agents, growing to 8 and 8, then 14 and 16, so agent-drafted volume (`content_assets_published`, `content_qa_first_pass_rate`) scales faster than people cost. Target growth in `leads_generated` (+88% in FY2027, +89% in FY2028) is funded by a rise in programme spend from £550k to £1,250k to £3,500k; cost per lead therefore rises by about 19% and 29%, reflecting the move to paid channels and the US, not a loss of efficiency.

## 5. Targets reset rules

- Targets are reset only through the annual budget cycle or an `executive.strategy_updated` / `executive.okrs_set` change; in-year changes need CMO and CRO agreement and are recorded in the quarterly review.
- If `lead_to_qualified_rate` falls below 20% for two consecutive months, the Demand Generation Manager and a Sales lead jointly review lead definitions and ideal-client criteria (COMPANY.md §2) within 10 business days.
- If `cost_per_qualified_lead` exceeds target by more than 20% for a quarter, the lowest-performing channel loses programme spend in the next quarter.
