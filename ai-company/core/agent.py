"""Base class for the 12 department agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Optional

from .bus import MessageBus
from .clock import SimClock
from .events import Event, EventLog
from .llm import LLMProvider
from .schema import Message, Role, Task


class DepartmentAgent(ABC):
    """Abstract department agent.

    Subclasses set class attributes SUBSCRIBES / PUBLISHES (use
    ``core.topics.subscribes_for(dept)`` / ``publishes_for(dept)``) and
    implement ``handle``. Optionally override ``tick`` (called once per
    simulated tick, before message delivery).
    """

    SUBSCRIBES: tuple[str, ...] = ()
    PUBLISHES: tuple[str, ...] = ()

    def __init__(self, name: str, department: str, role: Role, llm: LLMProvider,
                 bus: MessageBus, clock: SimClock, log: EventLog) -> None:
        self.name = name
        self.department = department
        self.role = role
        self.llm = llm
        self.bus = bus
        self.clock = clock
        self.log = log
        self.state: dict = {}          # free-form agent memory
        self.tasks: dict[str, Task] = {}

    # contract -----------------------------------------------------------
    @property
    def subscriptions(self) -> tuple[str, ...]:
        return tuple(self.SUBSCRIBES)

    @abstractmethod
    def handle(self, message: Message) -> list[Message]:
        """React to a delivered message. Return Messages to publish (messages
        already sent via emit() may be returned or omitted; the bus de-duplicates)."""

    def tick(self) -> list[Message]:
        """Per-tick scheduled behaviour (cadences, reminders). Default: nothing."""
        return []

    # helpers ------------------------------------------------------------
    def emit(self, topic: str, body: Optional[dict] = None, recipient: str = "*",
             reply_to: Optional[str] = None, delay_days: int = 0) -> Message:
        """Build, publish and log a message from this department.

        topic must start with '<department>.'; if PUBLISHES is non-empty the topic
        must be listed there or be in the '<department>.internal.*' namespace.
        ``delay_days`` schedules delivery in the future.
        """
        prefix = self.department + "."
        if not topic.startswith(prefix):
            raise ValueError(f"{self.department} may only publish topics starting with {prefix!r}, got {topic!r}")
        if self.PUBLISHES and topic not in self.PUBLISHES and not topic.startswith(prefix + "internal."):
            raise ValueError(f"topic {topic!r} is not in {type(self).__name__}.PUBLISHES")
        msg = self.bus.make_message(self.name, recipient, topic, body, reply_to,
                                    sim_time=self.clock.day + delay_days)
        self.bus.publish(msg)
        self.log_event(topic, f"emit -> {recipient}", message_id=msg.id, recipient=recipient,
                       body=msg.body, kind="emit")
        return msg

    def reply(self, to: Message, topic: str, body: Optional[dict] = None) -> Message:
        """emit() addressed to the sender of ``to`` with reply_to set."""
        return self.emit(topic, body, recipient=to.sender, reply_to=to.id)

    def log_event(self, topic: str, summary: str = "", **data) -> Event:
        return self.log.append(self.clock.day, self.department, topic, summary, data)

    def ask_llm(self, prompt: str) -> str:
        return self.llm.complete(self.system_prompt, prompt)

    @property
    def system_prompt(self) -> str:
        return (f"You are the {self.role.title} agent of the {self.department} department at "
                f"Lumenhall Partners, an AI management consultancy. Follow COMPANY.md facts exactly.")

    # tasks --------------------------------------------------------------
    def create_task(self, title: str, due_in_days: Optional[int] = None, priority: str = "medium",
                    depends_on: tuple[str, ...] = ()) -> Task:
        tid = f"TSK-{self.department}-{len(self.tasks) + 1:04d}"
        due = None if due_in_days is None else self.clock.day + due_in_days
        task = Task(tid, title, self.name, "todo", priority, due, tuple(depends_on))
        self.tasks[tid] = task
        return task

    def update_task(self, task_id: str, status: str) -> Task:
        task = replace(self.tasks[task_id], status=status)
        self.tasks[task_id] = task
        return task
