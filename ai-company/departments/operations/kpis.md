# Operations KPIs

Department: `operations` (PMO, business operations, workspace and facilities, procurement and vendor management, compliance actions, business continuity, process improvement). Head: Chief Operating Officer, Beatrice Moreau (COMPANY.md §9.2). Agent class: `OperationsAgent`. All figures are modeled assumptions in GBP unless stated.

## 1. KPI summary

| KPI id | Name | Unit | FY2026 target | FY2027 target | FY2028 target | Direction | Frequency | Owner |
|---|---|---|---|---|---|---|---|---|
| workspace_ready_on_time_pct | New starters with desk and equipment ready on or before the start day | percent | 95 | 97 | 98 | higher is better | monthly | Procurement and Workspace Specialist (COO until Q4 FY2026) |
| asset_recovery_pct | Leaver equipment recovered within 5 business days of the last working day | percent | 90 | 95 | 97 | higher is better | monthly | Workspace and Facilities Associate (Procurement and Workspace Specialist until Q4 FY2027) |
| vendor_review_cycle_days | Business days from `operations.vendor_review_requested` to approval or rejection, median | days | 10 | 9 | 8 | lower is better | monthly | Procurement and Workspace Specialist (Vendor Management Specialist from Q3 FY2028; COO until Q4 FY2026) |
| three_quote_compliance_pct | Orders of £2,500 or more with three compliant quotes or an approved sole-source exception | percent | 98 | 99 | 99 | higher is better | monthly | Operations Manager (COO until Q3 FY2027) |
| po_coverage_pct | Third-party spend committed under an approved PO before the commitment, by value | percent | 90 | 95 | 97 | higher is better | monthly | Operations Manager (COO until Q3 FY2027) |
| procurement_cycle_days | Business days from first quote received to PO placed for orders of £2,500 or more, median | days | 7 | 6 | 5 | lower is better | monthly | Procurement and Workspace Specialist |
| procurement_savings_pct | Negotiated saving against the first compliant quote on competed orders | percent | 5 | 6 | 7 | higher is better | quarterly | Operations Manager (COO until Q3 FY2027) |
| compliance_actions_on_time_pct | Compliance actions closed on or before their due day | percent | 90 | 93 | 95 | higher is better | weekly | Compliance and Risk Specialist (COO until Q2 FY2027) |
| overdue_compliance_actions | Open compliance actions past their due day, at period end | count | 2 | 1 | 1 | lower is better | weekly | Compliance and Risk Specialist (COO until Q2 FY2027) |
| continuity_tests_completed | Continuity tests completed in the fiscal year (tabletop, technical or live incident) | count | 2 | 4 | 6 | higher is better | quarterly | Operations Manager (COO until Q3 FY2027) |
| continuity_rto_met_pct | Continuity tests meeting the recovery time objective | percent | 80 | 90 | 95 | higher is better | per test, quarterly roll-up | Operations Manager (COO until Q3 FY2027) |
| process_improvements_adopted | Process improvements implemented in the fiscal year | count | 6 | 14 | 24 | higher is better | quarterly | Operations Manager (PMO Lead from Q3 FY2028; COO until Q3 FY2027) |
| process_savings_gbp | Annualised savings from adopted improvements, validated by Finance | GBP | 60000 | 200000 | 480000 | higher is better | quarterly | Operations Manager (PMO Lead from Q3 FY2028; COO until Q3 FY2027) |
| programme_on_time_pct | Internal programme milestones delivered on or before the baseline date | percent | 80 | 85 | 88 | higher is better | monthly | Operations Manager (PMO Lead from Q3 FY2028; COO until Q3 FY2027) |
| budget_variance_pct | Absolute operations budget variance, year to date | percent | 5 | 4 | 3 | lower is better | monthly | Chief Operating Officer |
| vendor_approved_before_order_pct | New vendors requiring review that were approved before their first order or data access | percent | 100 | 100 | 100 | higher is better | monthly | Procurement and Workspace Specialist (COO until Q4 FY2026) |

Sixteen KPIs. The FY2026 targets above are the values exposed in `agent.py` as `KPIS`. Units follow `core.Kpi`: percent values are plain numbers (95, not 0.95); days and counts are plain numbers; `process_savings_gbp` is whole pounds (60000). `higher_is_better` is False for `vendor_review_cycle_days`, `procurement_cycle_days`, `overdue_compliance_actions` and `budget_variance_pct`, and True for all others.

## 2. Definitions and formulas

| KPI id | Formula | Notes and exclusions |
|---|---|---|
| workspace_ready_on_time_pct | starters where `operations.workspace_ready` was emitted on or before the start day / starters in the period x 100 | Start day is the sim day of `people.new_hire_started`. Shared with People's day_one_readiness_rate, which also requires IT access (`it_security.access_provisioned`). Remote and client-site-only starters count as ready when the kit is delivered by the start day. |
| asset_recovery_pct | leavers whose recorded equipment was returned within 5 business days of `last_day` / leavers in the period x 100 | Source `people.employee_left`. Devices not returned by day 5 are remote-wiped by IT Security (the KPI still counts them as not recovered). Excludes leavers with no issued equipment. |
| vendor_review_cycle_days | median business days between `operations.vendor_review_requested` and `operations.vendor_approved` (or recorded rejection) | Includes the IT Security tiering time (Tier 1: 10 business days, Tier 2: 5, Tier 3: 2) and Legal's contract review; excludes days the vendor spends answering questions (clock stops on `awaiting_vendor`). Target is a median across tiers, so it sits at or below the Tier 1 limit. |
| three_quote_compliance_pct | orders with total committed value at or above £2,500 that have three compliant written quotes or a documented sole-source exception approved one level above the order value / all such orders placed | Threshold is value over the contract term, capped at 36 months. Orders aggregated by vendor and category over 30 days. Exceptions are counted as compliant only when approved before the PO, so a retrospective exception counts as non-compliant. |
| po_coverage_pct | spend committed with a PO dated on or before the commitment / total third-party spend committed in the period x 100 | By value. Excludes rent, rates, utilities, payroll, tax and statutory payments ("no PO, no pay" exemptions agreed with Finance). Source: `operations.procurement_order_placed` against the Finance commitment register. |
| procurement_cycle_days | median business days from the first `external.vendor_quote_received` of an RFQ to `operations.procurement_order_placed` | Orders at or above £2,500 only. Clock pauses while a vendor review is open on a new vendor. Emergency orders under the crisis rule are excluded and reported separately. |
| procurement_savings_pct | (first compliant quote - final PO price) / first compliant quote x 100, weighted by value, on competed orders | Only hard price reductions at order time count; cost avoidance, volume rebates not yet received and savings from scope changes are excluded. Validated by Finance quarterly (Finance Manager). |
| compliance_actions_on_time_pct | actions closed with `closed_day <= due_day` / actions that fell due or were closed in the period x 100 | Due day is the earlier of the `due_day` Legal sets on `legal.compliance_finding_raised` and the severity SLA in SOP-OPERATIONS-08 (critical 5, high 10, medium 20, low 40 business days). Closure means a human attestation, not the agent's own update. |
| overdue_compliance_actions | open actions with `due_day < today` at the period end | Zero is the aspiration; the target allows for actions blocked by a third party, each logged with a named blocker and an agreed extension from Legal. Critical overdue actions are always escalated regardless of the target. |
| continuity_tests_completed | `operations.continuity_test_completed` messages in the fiscal year | A real high or critical incident (`it_security.incident_detected`) that activated continuity arrangements counts as a live test once its lessons-learned record is filed. Target FY2026: two tabletops; FY2027: two tabletops and two technical; FY2028: those four plus two live or vendor-failure scenarios. |
| continuity_rto_met_pct | tests with `rto_met = true` / tests completed x 100 | Recovery time objective 4 hours for Tier-1 systems (email, ledger, engagement workspace, identity), 24 hours for Tier-2. A test failing RPO but meeting RTO still counts as RTO met; RPO result is reported separately. |
| process_improvements_adopted | improvements with status `implemented` and a recorded owner and benefit | A proposal counts once, in the fiscal year of go-live. Includes improvements below the £10,000 publication threshold, which are not sent to Executive. |
| process_savings_gbp | sum of annualised run-rate savings (hours released x £45 notional cost per hour, or cash savings) for improvements implemented | Notional cost per hour matches the £45 used in `people` economics. Counted after a 90-day post-implementation check; Finance validates before the figure is reported to the Board. |
| programme_on_time_pct | programme milestones achieved on or before the baseline date / milestones due in the period x 100 | Internal programmes only (US launch operational readiness, ISO 27001 and SOC 2 operational actions, systems roll-outs, New York fit-out); client programmes sit with Delivery. A re-baseline approved by the COO is counted as a miss in the quarter it occurs. |
| budget_variance_pct | abs(actual YTD operations spend - budget YTD) / budget YTD x 100 | Budget is the COMPANY.md §5.4 envelope phased monthly. Finance fires `finance.budget_variance_flagged` above 10% or £25k; Operations investigates at 5%. |
| vendor_approved_before_order_pct | new vendors in scope of the review rule with `vendor_approved` dated before the first PO and before any data access / new vendors in scope x 100 | In scope: any new vendor with annual value of £10,000 or more, or processing personal or client data, with system access, or an AI platform. Anything below 100% is a control breach reported to the CFO and the CISO. |

Guardrail: no KPI is reported as met if its source register is incomplete for the period (for example, a missing PO register export). Figures reported to the Board come from the monthly close.

## 3. Reporting cadence and data sources

| Cadence | Report | Audience | KPIs covered | Source (modeled) |
|---|---|---|---|---|
| Weekly (Friday cut-off) | Open compliance actions and overdue list | COO, Compliance and Risk Specialist, General Counsel (Callum Fraser) for named overdue items | compliance_actions_on_time_pct, overdue_compliance_actions | Compliance action register; `legal.compliance_finding_raised` and `operations.compliance_action_completed` |
| Weekly (Monday) | PO and sourcing pipeline | COO, Operations Manager | procurement_cycle_days, three_quote_compliance_pct | RFQ and PO register; `external.vendor_quote_received`, `operations.procurement_order_placed` |
| Monthly (working day 6) | Operations scorecard | Executive team | workspace_ready_on_time_pct, asset_recovery_pct, vendor_review_cycle_days, po_coverage_pct, vendor_approved_before_order_pct, programme_on_time_pct, budget_variance_pct | `people.new_hire_started`, `people.employee_left`, vendor register, Finance commitment register, programme plans |
| Quarterly (within 10 working days of quarter end) | Procurement savings and process benefits review | CFO, COO | procurement_savings_pct, process_improvements_adopted, process_savings_gbp, continuity_tests_completed, continuity_rto_met_pct | RFQ files, benefits log, test records; Finance validation |
| Annual (Q4) | Budget cycle BUD-<year> and KPI target reset | Board via Finance | all | `finance.budget_cycle_opened`, `operations.budget_submitted`, `executive.budget_approved` |

Data-quality controls:

1. Every KPI has one named calculation owner (section 1) and a second reviewer from Finance or Data; the COO signs the monthly scorecard.
2. KPIs are recomputed from registers at month end, not carried forward from weekly views; restatements above 1 percentage point (or 1 day, or 1 action) are footnoted next month.
3. AI agent outputs (draft comparisons, scorecards, commentary) are labelled agent-drafted and reviewed by a human before circulation (COMPANY.md §9.4).
4. Spend KPIs reconcile to the Finance commitment register; differences above £5,000 are investigated before the scorecard is released.
5. Compliance KPIs count only human-attested closures; the agent cannot mark an action closed.

## 4. Links to company targets

| Company target (COMPANY.md) | Operations KPI(s) | How Operations moves or protects it |
|---|---|---|
| Operations budget £300k / £700k / £1,650k (§5.4) | budget_variance_pct | Monthly tracking against the envelope; 80% budget-line warnings with Finance (SOP-OPERATIONS-13). |
| Total cost £7.5m / £17.8m / £39.0m and non-people spend £3.5m / £8.8m / £18.6m (§5.2, §5.4) | procurement_savings_pct, three_quote_compliance_pct, po_coverage_pct | Competitive sourcing and PO discipline on the addressable share of company non-people spend; savings flow to EBITDA. |
| EBITDA -£1.5m / £1.7m / £7.2m (§5.1) | procurement_savings_pct, process_savings_gbp | Procurement savings (about £59k / £218k / £586k modeled) are cash price reductions at order time; process savings (£60k / £200k / £480k) are annualised hours released and cash from improvements. The two are measured on different events and are never counted twice (`economics.md` section 3). |
| Non-budgeted spend approvals: above £50k CFO, above £250k CEO (§9.3) | po_coverage_pct, three_quote_compliance_pct | Approval ladder in SOP-OPERATIONS-02 mirrors §9.3 and stops at the CFO or CEO as the amount requires. |
| Agents may not approve payments above £10,000 or sign contracts (§9.4) | po_coverage_pct | Agents place POs only up to £2,500 and approve nothing above £10,000; every PO above £2,500 carries a named human approver. |
| Compliance baseline: UK GDPR and DPA 2018, ISO 27001 and Cyber Essentials Plus (FY2026), SOC 2 Type II (FY2027), Companies House and HMRC obligations, EU AI Act alignment (§8, assumption 7) | compliance_actions_on_time_pct, overdue_compliance_actions, vendor_approved_before_order_pct | Findings from Legal become dated, owned actions; vendor review before data flows is part of the ISO 27001 supplier controls. |
| US launch gated on ARR and ISO 27001; New York office Q1 FY2027 (§1, §8, assumption 6) | programme_on_time_pct, workspace_ready_on_time_pct | Programme plan for the New York opening and US operational readiness; kit and desks ready for US starters. |
| Headcount 38 / 110 / 230 and gross hires 42 / 81 / 139 (§6.1; `people` economics) | workspace_ready_on_time_pct, asset_recovery_pct | Readiness and recovery scale with starters and leavers without adding operations headcount proportionally (2 / 6 / 12 humans). |
| Attrition 14% falling to 11% and time-to-hire 45 days (§8, assumption 3) | workspace_ready_on_time_pct | Workspace never extends time-to-productivity; kit reserved from `delivery.staffing_requested`. |
| Incident handling and client continuity obligations (§3.3: Keep Enterprise includes 24x7 incident cover) | continuity_tests_completed, continuity_rto_met_pct | Tested continuity arrangements support Keep Enterprise 24x7 incident cover and SOC 2 evidence. |

Cross-department dependencies: workspace readiness depends on `people.new_hire_started` being sent with an equipment profile; vendor cycle time depends on IT Security's tier SLAs (Tier 1: 10 business days, Tier 2: 5, Tier 3: 2) and Legal's contract review; compliance timeliness depends on Legal setting realistic due days and on action owners in other departments completing their steps; budget variance depends on Finance's commitment register.
