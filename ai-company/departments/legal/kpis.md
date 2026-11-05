# Legal KPIs

Department: `legal` (contracts, compliance, regulatory change, data protection, AI-risk review, IP). Head: General Counsel, Callum Fraser (COMPANY.md §9.2). Agent class: `LegalAgent`. All figures are modeled assumptions in GBP unless stated. The agent produces first-pass analysis only; every KPI that depends on a legal judgement is measured on the human lawyer's decision, not the agent's draft.

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| contract_turnaround_days | Contract turnaround: `sales.deal_won` to first draft released after human review | days | 3 | 2 | 2 | lower is better | weekly | General Counsel (Commercial and Privacy Counsel from Q2 FY2027) |
| playbook_adherence_pct | Signed contracts with every clause at playbook standard or approved fallback | percent | 85 | 88 | 90 | higher is better | monthly | General Counsel (Commercial and Privacy Counsel from Q2 FY2027) |
| non_standard_liability_pct | Signed contracts with liability above 100% of annual fees or uncapped | percent | 10 | 8 | 6 | lower is better | monthly | General Counsel |
| deal_won_to_signed_days | Days from `sales.deal_won` to `legal.contract_signed` | days | 7 | 6 | 5 | lower is better | weekly | General Counsel (Contracts Specialist tracks from Q3 FY2027) |
| gc_escalation_response_hours | Hours from escalation raised to General Counsel decision | hours | 24 | 24 | 16 | lower is better | weekly | General Counsel |
| breach_notification_within_72h_pct | Notifiable personal data breaches reported to the ICO within 72 hours of awareness | percent | 100 | 100 | 100 | higher is better | per incident, reported monthly | General Counsel |
| regulatory_triage_days | Days from `external.regulation_published` to `legal.regulatory_change_noted` | days | 2 | 2 | 1 | lower is better | monthly | General Counsel (Privacy and Regulatory Counsel from Q1 FY2028) |
| ai_risk_review_days | Days from `product.ai_risk_review_requested` to `legal.ai_risk_review_completed` | days | 5 | 4 | 3 | lower is better | monthly | General Counsel (Privacy and Regulatory Counsel from Q1 FY2028) |
| compliance_training_completion_pct | Staff who completed mandatory compliance training by due date | percent | 95 | 96 | 98 | higher is better | monthly | General Counsel (Legal Operations Analyst chases from Q2 FY2028) |
| dsar_on_time_pct | Data subject access requests closed within one month (UK GDPR Art 12(3)) | percent | 98 | 99 | 99 | higher is better | monthly | General Counsel (Commercial and Privacy Counsel from Q2 FY2027) |
| legal_cost_pct_revenue | Legal department cost (people + non-people) as share of revenue | percent | 5.2 | 3.0 | 2.8 | lower is better | quarterly | General Counsel (with CFO) |

Eleven KPIs. The FY2026 targets above are the values exposed in `agent.py` as `KPIS`. Units follow `core.Kpi`: percent values are plain numbers (85, not 0.85), days and hours are plain numbers; `higher_is_better` is False for `contract_turnaround_days`, `non_standard_liability_pct`, `deal_won_to_signed_days`, `gc_escalation_response_hours`, `regulatory_triage_days`, `ai_risk_review_days` and `legal_cost_pct_revenue`.

## 2. Definitions and formulas

| KPI id | Formula | Notes and exclusions |
|---|---|---|
| contract_turnaround_days | calendar days from the `sales.deal_won` message to the human lawyer releasing the first draft to the client (`legal.contract_drafted` with a completed review task) | Standard-paper deals get a sample check; non-standard or >= £500k deals get full review (SOP-LEGAL-01). Change orders and renewals are measured from `delivery.scope_change_requested` / `customer_success.renewal_due`. The agent emits `legal.contract_drafted` immediately as a draft; the human review task is due in 3 days (standard) or 2 days (fallback/escalated) |
| playbook_adherence_pct | signed contracts where every clause position is `standard` or `fallback` with the approval recorded / all contracts signed in the period x 100 | An `escalate` position that is approved by General Counsel and CEO (COMPANY.md §9.3) counts as non-adherent for this KPI but compliant for governance. Positions are defined once in SOP-LEGAL-02 |
| non_standard_liability_pct | contracts signed with `liability_cap_multiple` > 1.0 or `uncapped_liability` / all contracts signed x 100 | Playbook standard is a cap of 100% of annual fees (SOP-LEGAL-02). Target below 10% is a modelled ceiling, not a COMPANY.md figure |
| deal_won_to_signed_days | `legal.contract_signed` day minus `sales.deal_won` day | Includes approval time for deals >= £500k (CEO) and > £1.5m (Board). The client's own signing delay is included. In the code `kpi_snapshot` measures draft-to-signature only (see note in section 3) |
| gc_escalation_response_hours | hours between an escalation task being raised (approval needed, breach decision, dispute) and the General Counsel recording a decision | Breach decisions are measured against the 72-hour clock instead. Target of 24 hours is a one-lawyer FY2026 commitment; 16 hours once Commercial and Privacy Counsel is the second approver for fallback positions |
| breach_notification_within_72h_pct | notifiable breaches with `legal.regulator_notification_filed` within 72 hours of awareness / notifiable breaches in the period x 100 | Notifiable = controller role and risk to individuals `likely` or `high` (UK GDPR Art 33(1)). The 72-hour limit is statutory and carried as `ICO_DEADLINE_HOURS` (COMPANY.md §9.3). Breaches where Lumenhall is processor are notified to the client controller within 48 hours instead and are excluded. A phased report counts as in time |
| regulatory_triage_days | days from `external.regulation_published` to `legal.regulatory_change_noted` | In the simulation triage is same-day; the target is a human-review standard |
| ai_risk_review_days | days from `product.ai_risk_review_requested` to the General Counsel signing off the recommendation in `legal.ai_risk_review_completed` | Prohibited or high-risk tiers may extend with a DPIA; the clock stops at the sign-off of the recommendation, not at the DPIA |
| compliance_training_completion_pct | staff who completed the assigned compliance course by the due date / staff assigned x 100 | Source: `people.compliance_training_completed` (`completion_pct`). Training below 95% creates a chase task within 7 days (SOP-LEGAL-06) |
| dsar_on_time_pct | DSARs closed within one calendar month of receipt (extendable by two months for complex requests, documented) / DSARs received x 100 | Source: DSAR register kept by Legal. No DSAR topic exists in `core/topics.py`; the register is fed manually (SOP-LEGAL-13) |
| legal_cost_pct_revenue | (legal people cost + non-people cost) / revenue x 100 | FY2026: £310k / £6.0m = 5.2%; FY2027: £580k / £19.5m = 3.0%; FY2028: £1,300k / £46.2m = 2.8% (COMPANY.md §5.1, §5.4) |

## 3. Reporting cadence and data sources

| Cadence | Report | Source | Audience |
|---|---|---|---|
| Weekly (Monday) | Matter and approvals review: open contracts, pending approvals, open tasks, open breaches | `legal.activity.weekly_matter_review` and the CLM | General Counsel |
| Monthly | KPI pack: all eleven KPIs, playbook exceptions, outside-counsel spend vs budget | `kpi_snapshot()` in the agent, CLM, breach and DSAR registers, Finance ledger | CEO, CFO |
| Quarterly | Regulatory horizon review and legal risk register | Regulatory Horizon notes, compliance findings | Executive team; Audit and Risk Committee (Marcus Ellery, chair) |
| Per incident | Breach clock status | Breach register | General Counsel, CISO, CEO |
| Annual | Contract playbook review, budget submission (`legal.budget_submitted`) | Playbook, `finance.budget_cycle_opened` | CFO, Board |

Data sources: the agent's state (`contracts`, `breaches`, `findings`, `training`, `policies`), the contract lifecycle messages (`legal.contract_drafted`, `legal.contract_signed`), the regulator notification record, Finance for revenue and spend, People for training completion, IT Security for incident facts.

Agent versus doc note: `kpi_snapshot()` computes `deal_won_to_signed_days` as signed day minus drafted day (the agent drafts on the deal-won day, so the two coincide in simulation), `playbook_adherence_pct` as non-escalated share of signed contracts, `breach_notification_within_72h_pct` and `compliance_training_completion_pct` (minimum course completion). The other KPIs report no actual yet.

## 4. Links to company targets

| Company target | Legal KPI | Link |
|---|---|---|
| Contracts signed quickly so billing starts (30% on signature, COMPANY.md §7) | contract_turnaround_days, deal_won_to_signed_days | Shorter time to signature accelerates the first invoice and DSO (finance `dso_days` <= 45, COMPANY.md §7) |
| Deal governance (COMPANY.md §9.3) | playbook_adherence_pct, non_standard_liability_pct, gc_escalation_response_hours | Deals >= £500k need CEO, > £1.5m Board; uncapped liability needs General Counsel and CEO |
| Compliance baseline: UK GDPR and DPA 2018, ISO 27001, Cyber Essentials Plus, SOC 2 Type II (COMPANY.md §8) | breach_notification_within_72h_pct, dsar_on_time_pct, compliance_training_completion_pct | Statutory deadlines and certification control evidence |
| AI agent governance (COMPANY.md §9.4) and alignment with the EU AI Act | ai_risk_review_days, regulatory_triage_days | Material changes to client-facing agents need an AI risk review before release |
| Operating cost control (COMPANY.md §5.1, §5.4) | legal_cost_pct_revenue | Department cost 5.2% / 3.0% / 2.8% of revenue |
| Revenue and margin protection (COMPANY.md §5.1) | non_standard_liability_pct | Caps liability exposure against fees (Forge Build £260k, Keep Plus £216k/yr, COMPANY.md §3.2, §3.3) |
