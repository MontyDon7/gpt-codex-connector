# Lumenhall Partners: AI-run consultancy simulation

A fictional, AI-run management consultancy (all facts and figures are modeled assumptions, not real data) and an offline, deterministic, standard-library-only multi-agent simulation of it.

- `COMPANY.md` canonical company facts (pricing, headcount, financial targets, governance)
- `CONVENTIONS.md` binding contract for the 12 department teams (file layout, doc templates, topic map)
- `core/` simulation framework (clock, event log, message bus, MockLLM, agent base class, Company)
- `departments/<id>/` one folder per department (blueprint, SOPs, KPIs, economics, agent, workflows, tests)

## Status

All 12 departments are complete: blueprint, SOPs, KPIs, economics, a working agent, scenarios and tests each.

| Department | Tests | | Department | Tests |
|---|---|---|---|---|
| executive | 75 | | people | 35 |
| sales | 75 | | legal | 95 |
| marketing | 32 | | it_security | 82 |
| delivery | 34 | | operations | 78 |
| finance | 48 | | product | 81 |
| customer_success | 56 | | data | 53 |

Plus the core framework tests and 7 whole-company integration tests (`tests/test_integration.py`): 770 tests in total.

How the company works end to end (verified by the integration tests):

- **Lead to cash:** `external.lead_inbound` -> marketing scores and hands over -> sales qualifies -> delivery scopes -> finance checks pricing -> proposal -> deal won -> legal contract -> billing schedule and staffing -> kickoff -> milestones -> invoices -> payment. Keep deals reach `customer_success.renewal_due` 90 days before term end.
- **Security breach:** one alert becomes one incident, one executive crisis, one `data_breach_confirmed`, a regulator filing and a resolution.
- **Hiring:** department `hire_requested` -> `people.requisition_opened` -> `executive.headcount_approved` -> `job_posted` -> offer -> `new_hire_started` -> IT access and workspace provisioned.

Two cross-department feedback loops were found only by running every department together and are now guarded by tests: an incident/crisis loop (IT/Security and Executive) and a requisition loop (Finance and People). If you add or change an agent, run the integration tests: a loop shows up as event counts far above the quiet-year baseline (about 3.6k events and 850 messages a year).

## Known approximations

- All figures are modeled assumptions. Department budgets tie to `COMPANY.md` section 5.4, and each department's tests check this.
- AI agent cost per agent-year differs by department (the heavy client-agent runtime sits in Delivery). In aggregate, departments' AI compute and tooling lines come to roughly 1.0m / 2.9m / 5.4m GBP against the 0.9m / 2.4m / 5.2m in `COMPANY.md` section 5.2, so FY2027 is about 19% over.
- Human approvals (contract release, ICO filing, General Counsel sign-off, compliance attestation) are simulated deterministically in each agent's `tick()` with documented delays.
- `MockLLM` produces canned text, so no result depends on a real model.

## Run the tests (Python 3.13, no dependencies)

From the repository root:

```
python3 -m unittest discover -s ai-company -t ai-company
```

Or from inside `ai-company/`: `python3 -m unittest discover -t . -s .`

## Run a simulation

From inside `ai-company/`:

```
python3 -m core 30 --jsonl /tmp/events.jsonl
```

This builds a `Company` (auto-discovering `departments/<id>/agent.py`; departments without an agent fall back to logging stubs), runs 30 simulated days and prints event counts per department. In code:

```python
from core import Company
company = Company()                       # MockLLM, strict errors
company.inject("external.lead_inbound", {"lead_id": "LD-00001", "company": "Calder Freight Group"})
log = company.run(60)                     # EventLog
print(log.to_jsonl())
```
