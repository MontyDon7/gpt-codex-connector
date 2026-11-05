"""Core simulation framework for Lumenhall Partners (see ../CONVENTIONS.md)."""

from .agent import DepartmentAgent
from .bus import BROADCAST, MessageBus
from .clock import SimClock
from .company import (DEPARTMENTS, Company, StubAgent, class_name_for, load_department_agent,
                      make_stub)
from .events import Event, EventLog
from .llm import LLMProvider, MockLLM
from .schema import Kpi, Message, Role, Task
from .topics import (EXTERNAL_TOPICS, TOPIC_SUBSCRIBERS, publishes_for, publisher_of, subscribes_for,
                     validate_topic_map)

__all__ = [
    "BROADCAST", "Company", "DEPARTMENTS", "DepartmentAgent", "EXTERNAL_TOPICS", "Event", "EventLog", "Kpi",
    "LLMProvider", "Message", "MessageBus", "MockLLM", "Role", "SimClock", "StubAgent", "TOPIC_SUBSCRIBERS",
    "Task", "class_name_for", "load_department_agent", "make_stub", "publishes_for",
    "publisher_of", "subscribes_for", "validate_topic_map",
]
