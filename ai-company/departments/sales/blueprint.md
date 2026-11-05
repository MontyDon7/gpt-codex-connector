# Sales Department Blueprint

## 1. Mission and scope

**Mission.** Win the right mid-size clients at the planned price and the planned pace, and keep them: turn the leads Marketing hands over into signed Compass, Forge and Keep work, protect price discipline under the delegations in COMPANY.md §9.3, and put a renewal proposal in front of every Keep client before the term ends. Sales owns the commercial funnel from the moment Marketing emits `marketing.lead_generated` to the moment a client accepts (`sales.deal_won`) or declines (`sales.deal_lost`), plus Keep renewal proposals and expansion offers to existing clients. The company-level result Sales is held to is the blended CAC in COMPANY.md §5.3 (£70k / £88k / £107k per new logo, sales plus marketing cost divided by new logos).

**Department head.** Rahul Mehta, Chief Revenue Officer, reports to the CEO (Imogen Hartley) and sits on the 12-person executive team (COMPANY.md §9.2). The CRO is the "Sales head" in the delegations table: approves discounts up to 10% and refers everything above to the Finance head and the CEO (COMPANY.md §9.3).

**Funnel responsibility (COMPANY.md §5.3, §5.1).**

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Leads received from Marketing (all stages) | 640 | 1,200 | 2,267 |
| Qualified opportunities (25% of leads) | 160 | 300 | 567 |
| Proposals (50% of qualified) | 80 | 150 | 283 |
| New logos (30% win rate) | 24 | 45 | 85 |
| New-logo bookings at ACV (£250k / £300k / £330k) | £6.0m | £13.5m | £28.05m |
| Average sales cycle (qualification to acceptance) | 75 days | 75 days | 70 days |
| Sales budget, £k (people + non-people) | 850 | 2,100 | 4,600 |

**In scope**

- Lead qualification: desk-check and discovery of every `marketing.lead_generated` (stage `mql` or `nurture`) against the ideal-client profile (COMPANY.md §2), acceptance as a qualified opportunity (`sales.lead_qualified`) and the scoping request to Delivery and Finance (`sales.proposal_requested`).
- Proposal and deal desk: assembling proposals from Delivery's scoping and Finance's pricing check, discount and terms governance, approval routing under COMPANY.md §9.3 (`sales.deal_approval_requested`), security and contract-risk gates (`sales.security_review_requested`), proposal issue (`sales.proposal_sent`) and the close (`sales.deal_won`, `sales.deal_lost`).
- RFP triage and response (`external.rfp_received`) including bid and no-bid decisions.
- Land and expand: next-offer proposals after an engagement completes, expansion opportunities from Customer Success, and change orders at rate card (COMPANY.md §3.5) after `delivery.scope_change_requested`.
- Keep renewals proposals: price and term proposal at CPI + 2% (cap 7%, COMPANY.md §7) at least 60 days before term end, save offers for at-risk clients (`sales.renewal_proposal_sent`).
- Pipeline management, forecast inputs, quota and commission administration, sales enablement.
- Pricing and discount authority inside the company delegations; price list maintenance when Executive approves a change.

**Out of scope**

- Lead generation, brand, content and events (Marketing). Sales supplies feedback via `sales.lead_qualified` and `sales.deal_lost`.
- Solution scoping and effort estimates (Delivery, `delivery.scoping_completed`); cost and margin checks (Finance, `finance.pricing_check_completed`).
- Contract drafting, negotiation of legal terms, signature (Legal; AI agents never sign, COMPANY.md §9.4).
- Client onboarding, health management, support and the renewal date calendar (Customer Success owns `customer_success.renewal_due`).
- Invoicing and collections (Finance). Sales supports collections through relationship calls when `finance.invoice_overdue` lands.
- Approval of a price change itself (Executive, `executive.pricing_change_approved`).

**Guardrails.** No proposal leaves Sales without a Delivery scoping pack and a Finance pricing check. No discount above 10% and no non-standard payment terms without the Finance head and CEO. No deal of £500k or more without the CEO, and no deal above £1.5m without the Board (COMPANY.md §9.3). Agents draft, score, monitor and propose; they never sign, approve a discount, release a proposal without human review, or commit the company to a price (COMPANY.md §9.4).

## 2. Org chart

```
Chief Executive Officer (Imogen Hartley)
└── Chief Revenue Officer (Rahul Mehta)                               [head]
    ├── Sales Director (x1 from Q2 FY2027, x2 from Q2 FY2028)         [principal]
    │   ├── Senior Account Executive (x1 FY2026, x2 FY2027, x4 FY2028)
    │   ├── Account Executive (x1 FY2026, x3 FY2027, x5 FY2028)
    │   ├── Sales Development Representative (x1 FY2026, x3 FY2027, x5 FY2028)
    │   └── Solutions Consultant (x1 FY2026, x2 FY2027, x3 FY2028)
    ├── Sales Operations Manager (from Q2 FY2027)
    │   ├── Deal Desk Analyst (from Q3 FY2028)
    │   ├── Sales Operations Analyst (from Q4 FY2028)
    │   └── Proposal Writer (from Q4 FY2028)
    └── Renewals and Expansion Manager (x1 from Q3 FY2027, x2 from Q4 FY2028)

AI agents (each with a named human owner, section 4)
├── Lead Triage Agent                      owner: Sales Operations Manager (CRO until Q2 FY2027)
├── Proposal Drafting Agent                owner: Solutions Consultant
├── Pipeline and Forecast Agent            owner: Sales Operations Manager (CRO until Q2 FY2027)
├── Deal Desk Agent                        owner: Sales Operations Manager (CRO until Q2 FY2027)
├── Renewals Radar Agent                   owner: Renewals and Expansion Manager
├── RFP Response Agent                     owner: Solutions Consultant
└── Account Research Agent                 owner: Senior Account Executive
```

Year-1 shape: five humans (CRO, Senior Account Executive, Account Executive, Sales Development Representative, Solutions Consultant) plus three agents. Until the Sales Director starts, the Senior Account Executive, Account Executive, Sales Development Representative and Solutions Consultant report to the CRO. The CRO personally carries deal desk and sales operations in FY2026 (with Finance running the pricing check, `finance.pricing_check_completed`) and covers renewals, of which there are none before the first 12-month Keep term ends in FY2027. In FY2026 the Senior Account Executive and the Account Executive carry the new-logo quota; the CRO leads every pursuit at or above £500k.

## 3. Roles

Salary bands are the COMPANY.md §6.2 band for the level key. Y1, Y2, Y3 are year-end humans (COMPANY.md §6.1 row: 5 / 14 / 26).

| Role title | Level key | Reports to | Y1 | Y2 | Y3 | Salary band GBP | Key responsibilities |
|---|---|---|---|---|---|---|---|
| Chief Revenue Officer | head | Chief Executive Officer | 1 | 1 | 1 | 140,000 to 200,000 (cash; plus equity) | Owns the revenue plan, quota, pricing and discount authority up to 10%; leads pursuits of £500k or more; approves proposals and renewal save offers; presents pipeline and forecast to the Board each quarter; owns commission plan with the CFO. |
| Sales Director | principal | Chief Revenue Officer | 0 | 1 | 2 | 120,000 to 155,000 | Player-coach for the account executive team (carries half a quota); weekly pipeline review; deal reviews before proposal issue; coaching; hiring; second director from Q2 FY2028 covers strategic accounts and US pursuits. |
| Senior Account Executive | manager | Sales Director (CRO until Q2 FY2027) | 1 | 2 | 4 | 92,000 to 115,000 | Owns qualified opportunities from £260k, runs discovery with the board sponsor, leads proposal and negotiation, owner of the Account Research Agent; carries a new-logo quota. |
| Account Executive | senior_consultant | Sales Director (CRO until Q2 FY2027) | 1 | 3 | 5 | 72,000 to 90,000 | Owns Compass Spark, Sprint, Forge Pilot and Keep Essential opportunities and expansion deals; runs proposals and negotiation; carries a new-logo quota. |
| Sales Development Representative | analyst | Sales Director (CRO until Q2 FY2027) | 1 | 3 | 5 | 38,000 to 48,000 | Works the lead queue: desk-check, first discovery call within the SLA, outbound sourcing of the 35% to 45% of leads that are not marketing-sourced; keeps CRM clean; supervises the Lead Triage Agent day to day. |
| Solutions Consultant | senior_consultant | Sales Director (CRO until Q2 FY2027) | 1 | 2 | 3 | 72,000 to 90,000 | Technical and commercial pre-sales: demos, scoping workshops with Delivery, security questionnaire answers with IT Security, RFP technical sections; owner of the Proposal Drafting and RFP Response agents. |
| Sales Operations Manager | manager | Chief Revenue Officer | 0 | 1 | 1 | 92,000 to 115,000 | CRM, CPQ and forecast hygiene; deal desk (discount and terms checks, approval packs); quota and commission administration with Finance; pipeline and forecast reporting; owner of the Lead Triage, Pipeline and Forecast and Deal Desk agents. |
| Renewals and Expansion Manager | manager | Chief Revenue Officer | 0 | 1 | 2 | 92,000 to 115,000 | Owns every Keep renewal proposal and save offer; expansion plays with Customer Success; owner of the Renewals Radar Agent; carries a renewal and expansion quota. |
| Deal Desk Analyst | consultant | Sales Operations Manager | 0 | 0 | 1 | 55,000 to 70,000 | Prepares approval packs, checks margin and terms against policy, maintains the price book and discount log; takes over day-to-day deal desk from the Sales Operations Manager. |
| Sales Operations Analyst | consultant | Sales Operations Manager | 0 | 0 | 1 | 55,000 to 70,000 | Weekly funnel and conversion reporting, quota attainment, commission statements, forecast accuracy tracking; QA of Pipeline and Forecast Agent outputs. |
| Proposal Writer | consultant | Sales Operations Manager | 0 | 0 | 1 | 55,000 to 70,000 | Owns the proposal and RFP template library, edits agent drafts to house style, assembles RFP responses to deadline. |
| **Total humans** | | | **5** | **14** | **26** | | Equals COMPANY.md §6.1 sales row (5 / 14 / 26). |

**Planned base salaries (inside band), by hire cohort, used for the people-cost check.** Loaded cost is base x 1.28 (COMPANY.md §5.2).

| Cohort (role, start) | Base (£) | Loaded (£k) |
|---|---|---|
| Chief Revenue Officer, in seat day 0 (£185,000 from FY2027) | 180,000 | 230.4 |
| Senior Account Executive, in seat day 0 | 110,000 | 140.8 |
| Account Executive, in seat day 0 | 88,000 | 112.6 |
| Sales Development Representative, in seat day 0 | 46,000 | 58.9 |
| Solutions Consultant, Q3 FY2026 | 86,000 | 110.1 |
| Sales Director, Q2 FY2027 | 155,000 | 198.4 |
| Sales Development Representative, Q2 FY2027 | 47,000 | 60.2 |
| Account Executive, Q2 FY2027 | 90,000 | 115.2 |
| Sales Operations Manager, Q2 FY2027 | 110,000 | 140.8 |
| Senior Account Executive, Q3 FY2027 | 113,000 | 144.6 |
| Sales Development Representative, Q3 FY2027 | 47,000 | 60.2 |
| Solutions Consultant, Q3 FY2027 | 90,000 | 115.2 |
| Renewals and Expansion Manager, Q3 FY2027 | 105,000 | 134.4 |
| Account Executive, Q4 FY2027 | 90,000 | 115.2 |
| Senior Account Executive, Q2 FY2028 and Q4 FY2028 | 105,000 | 134.4 |
| Sales Director, Q2 FY2028 | 145,000 | 185.6 |
| Sales Development Representative, Q2 FY2028 and Q4 FY2028 | 42,000 | 53.8 |
| Account Executive, Q3 FY2028 and Q4 FY2028 | 78,000 | 99.8 |
| Deal Desk Analyst, Q3 FY2028 | 58,000 | 74.2 |
| Solutions Consultant, Q3 FY2028 | 80,000 | 102.4 |
| Renewals and Expansion Manager, Q4 FY2028 | 100,000 | 128.0 |
| Sales Operations Analyst, Q4 FY2028 | 58,000 | 74.2 |
| Proposal Writer, Q4 FY2028 | 58,000 | 74.2 |

**People-cost reconciliation to COMPANY.md §5.4** (average FTE counts a hire from the first day of the start quarter; no US-based hire is planned inside this department's own headcount, so no +15% uplift is applied). The full build-up by role is in `economics.md` section 2.

| | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Average FTE in year | 4.5 | 10.25 | 19.25 |
| Loaded cost of average FTE (base x 1.28) | £597.8k | £1,301.1k | £2,303.0k |
| COMPANY.md §5.4 people budget | £600k | £1,300k | £2,300k |
| Variance | -£2.2k | +£1.1k | +£3.0k |

All three years are within the £5k tolerance. Commission is not in the people line: it is a non-people line (`economics.md` sections 1 and 3.4).

## 4. AI agents

Every agent is registered in the agent register (Data and IT Security) with a named human owner and operates under COMPANY.md §9.4: agents draft, analyse, monitor and propose; they never sign a contract, approve a discount, release a client-facing proposal without human review, approve a payment above £10,000 or contact a regulator. Totals: 3 / 9 / 18 (COMPANY.md §6.1 sales row). Direct cost is about £5k to £8k per agent-year inside the sales AI compute line; the §5.2 range of £20k to £35k per agent-year is the fully loaded figure including shared platform and oversight carried elsewhere.

| Agent name | Accountable human owner | Purpose | Autonomy limits | Y1 | Y2 | Y3 |
|---|---|---|---|---|---|---|
| Lead Triage Agent | Sales Operations Manager (CRO until Q2 FY2027) | Receives each `marketing.lead_generated` (stage `mql` or `nurture`), checks the ICP, applies the sales qualification score, drafts the discovery brief and the `sales.lead_qualified` and `sales.proposal_requested` messages. | May score, tag, route and write CRM notes. May not disqualify a lead from a company above 2,000 employees or a named strategic target without human review; may not email a prospect without an approved template; suppresses contacts on the PECR or unsubscribe list. | 1 | 2 | 3 |
| Proposal Drafting Agent | Solutions Consultant (Senior Account Executive until Q3 FY2026) | Assembles the proposal from the Delivery scoping pack and Finance pricing check: scope, deliverables, team, timeline, price, milestone billing (30/40/30), terms summary. | Drafts only. Cannot quote a price outside the price list and approved discount, cannot add non-standard terms, cannot send; every proposal is reviewed by an Account Executive or above and approved by the Sales Director or CRO before issue. | 1 | 2 | 4 |
| Pipeline and Forecast Agent | Sales Operations Manager (CRO until Q2 FY2027) | Weekly pipeline review, stage ageing, weighted forecast against the `data.forecast_updated` view, quota attainment, stalled-deal chasing, monthly KPI snapshot. | Read-only on CRM; cannot move a deal stage or change a close date; flags deals stalled more than 14 days in `qualified` or `scoped` and forecast variance above 15%. | 1 | 1 | 2 |
| Deal Desk Agent | Sales Operations Manager (CRO until Q2 FY2027) | Computes discount and net price, evaluates the approval routes in COMPANY.md §9.3, drafts `sales.deal_approval_requested` packs, logs every discount decision. | Cannot approve any discount or term; cannot waive a Finance pricing cap; applies the 5% crisis ceiling when crisis mode is on. | 0 | 1 | 2 |
| Renewals Radar Agent | Renewals and Expansion Manager | Tracks Keep terms, health scores and churn flags, drafts renewal proposals (CPI + 2%, cap 7%) and save offers, tracks the 60-day lead time. | Cannot waive uplift above the CRO authority (10% discount) or send a renewal proposal without human review; escalates any client with health score below 60. | 0 | 1 | 2 |
| RFP Response Agent | Solutions Consultant | Applies the bid and no-bid rules, builds the answer library response, drafts compliance matrices and security answers with IT Security. | Drafts only; no submission without Solutions Consultant and Sales Director review; no commitment to uncapped liability or non-standard IP terms (General Counsel and CEO, COMPANY.md §9.3). | 0 | 1 | 2 |
| Account Research Agent | Senior Account Executive | Prepares account and sponsor briefs (public sources and licensed data), trigger events, org maps and call plans for pursuits and expansion. | Public and licensed sources only; no scraping behind logins; business contact data only; no outreach. | 0 | 1 | 3 |
| **Total agents** | | | **3** | **9** | **18** | |

Y1 agents (Lead Triage, Proposal Drafting, Pipeline and Forecast) are provisioned in the first week (5-day provisioning, COMPANY.md §8). Agent-to-human ratio is 0.6 in FY2026, 0.64 in FY2027 and 0.69 in FY2028; the senior human gate on every outbound proposal and every price remains.

## 5. Hiring plan

Hires are requested through `sales.hire_requested`, which triggers People's requisition flow and then CEO headcount approval (`executive.headcount_approved`); time to hire is 45 days (COMPANY.md §8), so requisitions open roughly one quarter before the start date. Start dates are the first day of the stated quarter. The FY2027 and FY2028 requests are raised when `executive.budget_approved` lands in Q4 of the preceding year.

### FY2026 (quarterly)

| Quarter | Role | Count | Trigger |
|---|---|---|---|
| Q1 | Chief Revenue Officer, Senior Account Executive, Account Executive, Sales Development Representative (in seat at simulation day 0, Monday 2026-01-05) | 4 | Founding sales team hired with the seed round; 640 leads and 80 proposals needed in the year |
| Q2 | none | 0 | Series A closes in Q2 (COMPANY.md §1); hiring held until the funding is in place |
| Q3 | Solutions Consultant | 1 | First Forge proposals need technical pre-sales; Delivery principals spend more than 20% of their time on scoping calls |
| Q4 | none (requisitions for FY2027 roles opened) | 0 | Budget cycle opened by `finance.budget_cycle_opened`; FY2027 plan approved via `executive.budget_approved` |

FY2026 year-end total: 5 humans, 3 agents.

### FY2027 (by half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 | Sales Director | 1 | Q2 | CRO span above 5 directs; weekly pipeline above 60 open deals; deal reviews cannot be done by the CRO alone |
| H1 | Sales Development Representative | 1 | Q2 | Lead volume above 60 per month per SDR (SDR capacity, `economics.md` section 3.6); 1,200 leads in the year |
| H1 | Account Executive | 1 | Q2 | Open proposals per quota-carrying executive above 25 |
| H1 | Sales Operations Manager | 1 | Q2 | CRO still running deal desk, forecast and commission; forecast accuracy below 80% |
| H2 | Senior Account Executive | 1 | Q3 | Pipeline of £500k-plus pursuits above 3 open at once; US pursuits begin |
| H2 | Sales Development Representative | 1 | Q3 | Lead volume 100 per month against a capacity of 120 |
| H2 | Solutions Consultant | 1 | Q3 | Scoping workshops above 12 per month; security questionnaires queued more than 5 days |
| H2 | Renewals and Expansion Manager | 1 | Q3 | First Keep terms ending (12-month minimum term from FY2026 start dates); more than 8 renewals due in the next two quarters |
| H2 | Account Executive | 1 | Q4 | Year-to-date new logos at or above 85% of plan and proposals per executive above 25 |

FY2027 year-end total: 14 humans (9 hires), 9 agents. Gate: if qualified opportunities year-to-date are below 85% of plan at the end of Q2, the Q3 and Q4 requisitions are held until the CEO re-approves.

### FY2028 (by half-year)

| Half | Role | Count | Start quarter | Trigger |
|---|---|---|---|---|
| H1 | Senior Account Executive | 1 | Q2 | US share of pipeline above 25%; 85 new logos need 7.6 average quota carriers |
| H1 | Sales Director | 1 | Q2 | Strategic accounts and US pursuits need a dedicated director; first director span above 8 |
| H1 | Sales Development Representative | 1 | Q2 | Lead volume above 170 per month |
| H2 | Account Executive | 1 | Q3 | Proposals per quota carrier above 38 |
| H2 | Deal Desk Analyst | 1 | Q3 | More than 25 priced deals a month; approval packs per month above 8 |
| H2 | Solutions Consultant | 1 | Q3 | Scoping workshops above 20 per month |
| H2 | Senior Account Executive | 1 | Q4 | Pursuits of £500k or more above 6 open |
| H2 | Account Executive | 1 | Q4 | Pipeline coverage below 3.3x for two consecutive months |
| H2 | Sales Development Representative | 1 | Q4 | Lead volume 189 per month against a capacity of 240 |
| H2 | Renewals and Expansion Manager | 1 | Q4 | Keep client count above 40; renewals due in a quarter above 15 |
| H2 | Sales Operations Analyst | 1 | Q4 | Weekly reporting above 0.4 FTE of the Sales Operations Manager |
| H2 | Proposal Writer | 1 | Q4 | Proposals above 280 a year; RFP volume above 3 per month |

FY2028 year-end total: 26 humans (12 hires), 18 agents. Agent additions: Y1 provisioned at start (3). FY2027 adds Deal Desk, Renewals Radar, RFP Response and Account Research agents plus one more each of Lead Triage and Proposal Drafting (net +6). FY2028 adds one Lead Triage, two Proposal Drafting, one each of Pipeline and Forecast, Deal Desk, Renewals Radar and RFP Response, and two Account Research agents (net +9).

## 6. Interfaces

Topics are those in the department topic map (CONVENTIONS section 7, `core/topics.py`).

### Sales publishes

| Topic | Consumers (primary) | When |
|---|---|---|
| `sales.lead_qualified` | Marketing, Delivery, Data | A lead is accepted as a qualified opportunity (also for expansion and RFP deals); carries `lead_id`, `deal_id`, `client_name`, `tier`, `employees`. |
| `sales.proposal_requested` | Delivery, Finance | Scoping and a pricing check are requested; carries the requested discount and the scoping due date. |
| `sales.security_review_requested` | IT Security, Legal | The proposal is built and needs the security questionnaire and terms review before it can be sent. |
| `sales.deal_approval_requested` | Executive, Finance, Legal | A discount above 10%, non-standard terms, a deal of £500k or more, a deal above £1.5m or non-standard legal terms needs approval. |
| `sales.proposal_sent` | Executive, Data | The proposal has been issued to the client. |
| `sales.deal_won` | Legal, Finance, Delivery, Customer Success, Executive, Data | The client accepts; triggers contract drafting, billing schedule and staffing. |
| `sales.deal_lost` | Marketing, Executive, Data | The deal is lost or declined; carries the loss reason. |
| `sales.renewal_proposal_sent` | Customer Success, Finance, Legal | A Keep renewal proposal is issued. |
| `sales.budget_submitted` | Finance | Annual budget submission in answer to `finance.budget_cycle_opened`. |
| `sales.hire_requested` | People | A hiring trigger in section 5 is reached. |

### Sales subscribes

| Topic | Source | Sales response (SOP) |
|---|---|---|
| `marketing.lead_generated` | Marketing | Qualify (stage `mql` first; `nurture` desk-check) and accept or return (SOP-SALES-01). |
| `marketing.campaign_launched` | Marketing | Plan SDR capacity against the expected leads (SOP-SALES-11). |
| `marketing.content_published` | Marketing | Add to the enablement library (SOP-SALES-11). |
| `marketing.event_scheduled` | Marketing | Assign an account executive and target list (SOP-SALES-11). |
| `external.rfp_received` | External | Bid or no-bid decision (SOP-SALES-07). |
| `delivery.scoping_completed` | Delivery | Gate for proposal build (SOP-SALES-02). |
| `finance.pricing_check_completed` | Finance | Gate and discount cap for proposal build (SOP-SALES-03). |
| `it_security.security_questionnaire_completed`, `legal.security_terms_reviewed`, `legal.contract_risk_flagged`, `it_security.certification_status_updated` | IT Security, Legal | Security and legal gates (SOP-SALES-04). |
| `executive.deal_decision_made` | Executive | Release or stop the proposal (SOP-SALES-05). |
| `legal.contract_drafted`, `legal.contract_signed` | Legal | Contract hand-off and commission accrual (SOP-SALES-06). |
| `customer_success.renewal_due`, `customer_success.renewal_confirmed`, `customer_success.churn_risk_flagged`, `customer_success.client_churned`, `customer_success.health_score_updated` | Customer Success | Renewals and churn defence (SOP-SALES-08). |
| `customer_success.expansion_opportunity_identified`, `delivery.engagement_completed`, `delivery.scope_change_requested` | Customer Success, Delivery | Expansion and change orders (SOP-SALES-09). |
| `data.forecast_updated`, `delivery.capacity_forecast_updated` | Data, Delivery | Pipeline and capacity inputs (SOP-SALES-10). |
| `executive.pricing_change_approved`, `product.pricing_change_proposed`, `product.agent_capability_added`, `product.roadmap_published` | Executive, Product | Price list and enablement (SOP-SALES-11). |
| `finance.budget_cycle_opened`, `executive.budget_approved`, `executive.okrs_set`, `executive.strategy_updated` | Finance, Executive | Planning, budget and hiring (SOP-SALES-12). |
| `finance.invoice_overdue`, `finance.payment_received` | Finance | Receivables interlock and commission release (SOP-SALES-13). |
| `executive.crisis_declared` | Executive | Crisis mode (SOP-SALES-14). |

### Departments depended on

- **Marketing:** lead volume and quality; the shared lead SLA (accepted or returned within 2 business days for `mql`, 5 for `nurture`). Unaccepted marketing-qualified leads are reviewed weekly.
- **Delivery:** scoping within 3 to 8 business days by tier; start dates and capacity; Principals join pursuits of £260k or more.
- **Finance:** pricing check within 1 business day; discount and margin floors; collections; commission payments through payroll.
- **Legal:** security terms, contract drafting, contract risk, signature (Sales never signs).
- **IT Security:** security questionnaires and certification evidence (ISO 27001 achieved by end FY2026, SOC 2 Type II FY2027, COMPANY.md §8).
- **Customer Success:** renewal calendar, health scores, churn flags, expansion leads.
- **Executive:** deal decisions, price changes, OKRs, strategy, crisis mode, budget.
- **Data, Product, People:** forecast, capability claims and pricing proposals, requisitions.

### Departments served

Executive (pipeline and forecast, Board reporting), Delivery (committed starts and scope), Finance (booked deals, billing inputs), Customer Success (client commercial history, renewal proposals), Marketing (acceptance and loss feedback), Legal (deal context).

## 7. Risks and dependencies

| Risk | Likelihood / impact | Mitigation | Owner |
|---|---|---|---|
| Lead volume or quality below plan (640 / 1,200 / 2,267); each point of lead-to-qualified below 25% costs about 6 qualified opportunities in FY2026 | Medium / High | Weekly acceptance review with Marketing; sales-sourced outbound (35% to 45% of leads); hold-and-release hiring gate at Q2 FY2027 | Chief Revenue Officer |
| Win rate below 30%: each 5 points is 4 to 14 fewer new logos a year (80 / 150 / 283 proposals) and a blended CAC rise of about 20% | Medium / High | Qualification discipline at 60-point score; Solutions Consultant on every Forge pursuit; win and loss reviews with Marketing | Sales Director |
| Discount creep above the 6% average erodes margin (each point removes £60k of FY2026 revenue) | Medium / Medium | Deal desk checks on every proposal; discounts above 10% need the Finance head and CEO; crisis ceiling 5% | Sales Operations Manager |
| Key-person dependence on the CRO in FY2026 (quota, deal desk, forecast, pursuits of £500k or more) | High / Medium | Agents carry triage, drafting and reporting; Sales Operations Manager and Sales Director hired Q2 FY2027 | Chief Revenue Officer and CEO |
| Delivery capacity tight at signature (utilisation above 85%) forces a 14-day start lag or loses the deal | Medium / Medium | `delivery.capacity_forecast_updated` feeds proposal start dates; weekly capacity check with the Managing Partner, Delivery | Sales Director |
| Slow security or legal gates stretch the sales cycle beyond 75 days | Medium / Medium | 10-day security SLA; standard terms and evidence pack (certifications); Solutions Consultant answer library | Solutions Consultant |
| Over-promising capability in proposals (agent claims not shipped) | Low / High | `product.agent_capability_added` is the only source for capability claims; Proposal Drafting Agent restricted to approved claims; Legal review of non-standard claims | Solutions Consultant |
| Client concentration above 15% of revenue (policy, COMPANY.md §8) | Low / High | Deal desk flags concentration on every approval pack; Finance supplies the figure | Chief Revenue Officer |
| Renewal proposals late (under 60 days) or uplift wrongly applied to at-risk clients | Medium / Medium | Renewals Radar Agent tracks term end; uplift waived for at-risk clients; Renewals and Expansion Manager hired Q3 FY2027 | Renewals and Expansion Manager |
| Quota or commission dispute from ambiguous deal credit | Low / Medium | Commission plan documents (`economics.md` section 3.4); deal desk log; Finance pays from signed contracts only | Sales Operations Manager |
| Slow hiring (45 days) delays capacity relative to the lead plan | Medium / Medium | Requisitions a full quarter ahead; Sales Director covers as a player-coach | Chief Revenue Officer and Chief People Officer |

**Key dependencies.** Marketing lead supply, Delivery scoping and capacity, Finance pricing check, Legal contract turnaround, Series A funding in Q2 FY2026 for hiring, the ISO 27001 certification at the end of FY2026 as a proof point for enterprise buyers, and Customer Success for the renewal calendar.

## 8. Sources

- COMPANY.md §1 Identity (US launch Q1 FY2027, Series A timing, fiscal year, FX rate)
- COMPANY.md §2 Business model (ideal client, land and expand)
- COMPANY.md §3.1 to §3.5 Service lines, pricing and rate card
- COMPANY.md §5.1 Revenue and clients (new logos, ACV)
- COMPANY.md §5.2 Cost sanity check (loaded cost, agent cost range)
- COMPANY.md §5.3 Commercial funnel (leads, qualified, proposals, win rate, sales cycle, blended CAC)
- COMPANY.md §5.4 Department budget envelopes (sales: people 600 / 1,300 / 2,300; non-people 250 / 800 / 2,300; total 850 / 2,100 / 4,600)
- COMPANY.md §6 and §6.1 Headcount plan (sales 5 / 14 / 26 humans; 3 / 9 / 18 agents)
- COMPANY.md §6.2 Levels and salary bands
- COMPANY.md §7 Billing and commercial terms (milestones, Keep uplift, change orders, payment terms)
- COMPANY.md §8 Key assumptions (win rate, time to hire, certifications)
- COMPANY.md §9.2 Executive team; §9.3 Delegations of authority; §9.4 AI agent governance
- CONVENTIONS.md section 7 and `core/topics.py` (sales topic map)
