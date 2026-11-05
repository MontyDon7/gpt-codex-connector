"""Company: wires the 12 department agents onto one bus/clock/log and runs ticks."""

from __future__ import annotations

import importlib
import os
import sys
from datetime import date
from typing import Callable, Mapping, Optional

from .agent import DepartmentAgent
from .bus import MessageBus
from .clock import DEFAULT_START, SimClock
from .events import EventLog
from .llm import LLMProvider, MockLLM
from .schema import Message, Role

DEPARTMENTS: tuple[str, ...] = (
    "executive", "sales", "marketing", "delivery", "finance", "people",
    "legal", "it_security", "operations", "customer_success", "product", "data",
)

AgentFactory = Callable[[LLMProvider, MessageBus, SimClock, EventLog], DepartmentAgent]


def class_name_for(dept: str) -> str:
    """'it_security' -> 'ItSecurityAgent'."""
    return "".join(p.capitalize() for p in dept.split("_")) + "Agent"


class StubAgent(DepartmentAgent):
    """Placeholder used when a department has not (yet) shipped agent.py. Logs what it receives."""

    def handle(self, message: Message) -> list[Message]:
        self.log_event("stub.received", f"{message.topic} from {message.sender}", message_id=message.id)
        return []


def make_stub(dept: str, llm: LLMProvider, bus: MessageBus, clock: SimClock, log: EventLog) -> StubAgent:
    from . import topics  # lazy: topics imports DEPARTMENTS from this module
    role = Role(title=f"Head of {dept}", department=dept, level="head", reports_to="Chief Executive Officer")
    agent = StubAgent(dept, dept, role, llm, bus, clock, log)
    agent.SUBSCRIBES = topics.subscribes_for(dept)
    agent.PUBLISHES = topics.publishes_for(dept)
    return agent


def _ensure_root_on_path() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)


def load_department_agent(dept: str, llm: LLMProvider, bus: MessageBus, clock: SimClock,
                          log: EventLog) -> Optional[DepartmentAgent]:
    """Import ``departments.<dept>.agent`` and call its ``build_agent``; None if the module doesn't exist yet.
    Errors raised inside an existing module propagate."""
    _ensure_root_on_path()
    modname = f"departments.{dept}.agent"
    try:
        module = importlib.import_module(modname)
    except ModuleNotFoundError as exc:
        if exc.name in (modname, f"departments.{dept}", "departments"):
            return None
        raise
    return module.build_agent(llm, bus, clock, log)


class Company:
    """Registers one agent per department id and runs the simulation.

    factories: optional {dept_id: factory} overriding discovery for those ids.
    use_departments: if False, never import departments/* (stubs only).
    strict: if True (default) agent exceptions propagate; if False they are logged
            as 'system.agent_error' events and the run continues.
    """

    def __init__(self, llm: Optional[LLMProvider] = None, factories: Optional[Mapping[str, AgentFactory]] = None,
                 start: date = DEFAULT_START, use_departments: bool = True, strict: bool = True,
                 max_rounds_per_tick: int = 10) -> None:
        self.llm: LLMProvider = llm or MockLLM()
        self.clock = SimClock(start)
        self.log = EventLog(start)
        self.bus = MessageBus(self.clock, on_error=None if strict else self._on_error)
        self.max_rounds_per_tick = max_rounds_per_tick
        self.agents: dict[str, DepartmentAgent] = {}
        factories = dict(factories or {})
        unknown = set(factories) - set(DEPARTMENTS)
        if unknown:
            raise ValueError(f"unknown department ids: {sorted(unknown)}")
        for dept in DEPARTMENTS:
            agent = None
            if dept in factories:
                agent = factories[dept](self.llm, self.bus, self.clock, self.log)
            elif use_departments:
                agent = load_department_agent(dept, self.llm, self.bus, self.clock, self.log)
            if agent is None:
                agent = make_stub(dept, self.llm, self.bus, self.clock, self.log)
            if agent.name != dept:
                raise ValueError(f"agent for {dept} must have name == department id, got {agent.name!r}")
            self.agents[dept] = agent
            self.bus.register(agent)

    def _on_error(self, name: str, msg: Message, exc: Exception) -> None:
        self.log.append(self.clock.day, name, "system.agent_error", f"{type(exc).__name__}: {exc}",
                        {"message_id": msg.id, "topic": msg.topic})

    # seeding ------------------------------------------------------------
    def inject(self, topic: str, body: Optional[dict] = None, recipient: str = "*",
               sender: str = "external", delay_days: int = 0) -> Message:
        """Publish a message from outside the company (e.g. an inbound lead)."""
        msg = self.bus.make_message(sender, recipient, topic, body, sim_time=self.clock.day + delay_days)
        self.bus.publish(msg)
        return msg

    def seed(self, messages: list[Message]) -> None:
        for m in messages:
            self.bus.publish(m)

    # running ------------------------------------------------------------
    def step(self) -> None:
        """One tick: every agent.tick() (DEPARTMENTS order), drain the bus, advance the clock."""
        for dept in DEPARTMENTS:
            for msg in self.agents[dept].tick() or []:
                self.bus.publish(msg)
        self.bus.drain(self.max_rounds_per_tick)
        self.log.append(self.clock.day, "system", "system.tick", f"day {self.clock.day}",
                        {"date": self.clock.date.isoformat(), "pending": len(self.bus.pending)})
        self.clock.advance(1)

    def run(self, ticks: int) -> EventLog:
        for _ in range(ticks):
            self.step()
        return self.log
