# Lumenhall Partners: AI-run consultancy simulation

A fictional, AI-run management consultancy (all facts and figures are modeled assumptions, not real data) and an offline, deterministic, standard-library-only multi-agent simulation of it.

- `COMPANY.md` canonical company facts (pricing, headcount, financial targets, governance)
- `CONVENTIONS.md` binding contract for the 12 department teams (file layout, doc templates, topic map)
- `core/` simulation framework (clock, event log, message bus, MockLLM, agent base class, Company)
- `departments/<id>/` one folder per department (blueprint, SOPs, KPIs, economics, agent, workflows, tests)

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
