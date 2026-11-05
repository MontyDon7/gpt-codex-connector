"""Deterministic in-process message bus.

Rules
- ``publish`` queues a message (idempotent per message id).
- ``step`` delivers every queued message whose ``sim_time <= clock.day`` (all of
  them if no clock was given), ordered by (sim_time, publish order). Messages
  published while handling are queued for the NEXT step.
- recipient == "*": delivered to every subscriber of the topic except the sender,
  in sorted agent-name order. Otherwise delivered only to the named agent.
- Messages to unknown agents / with no subscribers go to ``dead_letters``.
"""

from __future__ import annotations

import fnmatch
from typing import TYPE_CHECKING, Callable, Optional

from .schema import Message

if TYPE_CHECKING:  # pragma: no cover
    from .agent import DepartmentAgent
    from .clock import SimClock

BROADCAST = "*"


class MessageBus:
    def __init__(self, clock: Optional["SimClock"] = None,
                 on_error: Optional[Callable[[str, Message, Exception], None]] = None) -> None:
        self.clock = clock
        self.on_error = on_error  # None => exceptions from handle() propagate
        self._agents: dict[str, "DepartmentAgent"] = {}
        self._subs: dict[str, list[str]] = {}  # agent name -> topic patterns
        self._pending: list[tuple[int, Message]] = []  # (publish seq, message)
        self._seen: set[str] = set()
        self._seq = 0
        self._id_counter = 0
        self.history: list[Message] = []  # every message, in delivery order (one entry per message)
        self.dead_letters: list[Message] = []

    # registration -------------------------------------------------------
    def register(self, agent: "DepartmentAgent", subscriptions: Optional[list[str]] = None) -> None:
        if agent.name in self._agents:
            raise ValueError(f"agent already registered: {agent.name}")
        self._agents[agent.name] = agent
        self._subs[agent.name] = []
        for pattern in (subscriptions if subscriptions is not None else agent.subscriptions):
            self.subscribe(agent.name, pattern)

    def subscribe(self, name: str, pattern: str) -> None:
        if name not in self._agents:
            raise KeyError(f"unknown agent: {name}")
        if pattern not in self._subs[name]:
            self._subs[name].append(pattern)

    def unsubscribe(self, name: str, pattern: str) -> None:
        if pattern in self._subs.get(name, []):
            self._subs[name].remove(pattern)

    @property
    def agent_names(self) -> list[str]:
        return sorted(self._agents)

    def subscribers_of(self, topic: str) -> list[str]:
        return sorted(n for n, pats in self._subs.items()
                      if any(fnmatch.fnmatchcase(topic, p) for p in pats))

    # publishing ---------------------------------------------------------
    def next_id(self, sender: str = "msg") -> str:
        self._id_counter += 1
        return f"MSG-{self._id_counter:06d}"

    def publish(self, message: Message) -> bool:
        """Queue a message. Returns False if this id was already published."""
        if message.id in self._seen:
            return False
        self._seen.add(message.id)
        self._seq += 1
        self._pending.append((self._seq, message))
        return True

    def make_message(self, sender: str, recipient: str, topic: str, body: Optional[dict] = None,
                     reply_to: Optional[str] = None, sim_time: Optional[int] = None) -> Message:
        """Build (but do not publish) a Message with a fresh deterministic id."""
        if sim_time is None:
            sim_time = self.clock.day if self.clock is not None else 0
        return Message(self.next_id(sender), sender, recipient, topic, dict(body or {}), sim_time, reply_to)

    @property
    def pending(self) -> list[Message]:
        return [m for _, m in sorted(self._pending, key=lambda t: (t[1].sim_time, t[0]))]

    # delivery -----------------------------------------------------------
    def _recipients(self, msg: Message) -> list[str]:
        if msg.recipient == BROADCAST:
            return [n for n in self.subscribers_of(msg.topic) if n != msg.sender]
        return [msg.recipient] if msg.recipient in self._agents else []

    def step(self) -> list[Message]:
        """Deliver all due messages once. Returns the messages delivered this step."""
        now = self.clock.day if self.clock is not None else None
        due = [t for t in self._pending if now is None or t[1].sim_time <= now]
        due.sort(key=lambda t: (t[1].sim_time, t[0]))
        due_ids = {t[0] for t in due}
        self._pending = [t for t in self._pending if t[0] not in due_ids]
        delivered: list[Message] = []
        for _, msg in due:
            recipients = self._recipients(msg)
            if not recipients:
                self.dead_letters.append(msg)
                continue
            delivered.append(msg)
            self.history.append(msg)
            for name in recipients:
                try:
                    replies = self._agents[name].handle(msg) or []
                except Exception as exc:  # noqa: BLE001
                    if self.on_error is None:
                        raise
                    self.on_error(name, msg, exc)
                    continue
                for reply in replies:
                    self.publish(reply)
        return delivered

    def drain(self, max_rounds: int = 10) -> int:
        """Call step() until nothing is due or ``max_rounds`` is reached. Returns messages delivered."""
        total = 0
        for _ in range(max_rounds):
            delivered = self.step()
            total += len(delivered)
            now = self.clock.day if self.clock is not None else None
            if not any(now is None or m.sim_time <= now for _, m in self._pending):
                break
        return total
