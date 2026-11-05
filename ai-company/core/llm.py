"""LLM abstraction. Everything runs offline against MockLLM; a real provider
only needs a ``complete(system, prompt) -> str`` method."""

from __future__ import annotations

from typing import Callable, Optional, Protocol, Union, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    def complete(self, system: str, prompt: str) -> str: ...


Response = Union[str, Callable[[str, str], str]]


class MockLLM:
    """Deterministic scripted LLM.

    ``script`` is an ordered mapping/list of (keyword, response). The first
    keyword found (case-insensitive) in ``system + "\\n" + prompt`` wins. A
    response may be a string or a callable(system, prompt) -> str. With no
    match, ``default`` is returned (or a deterministic echo of the prompt).
    Every call is recorded in ``calls`` as (system, prompt, response).
    """

    def __init__(self, script: Optional[Union[dict, list]] = None, default: Optional[str] = None) -> None:
        items = script.items() if isinstance(script, dict) else (script or [])
        self.script: list[tuple[str, Response]] = [(k.lower(), v) for k, v in items]
        self.default = default
        self.calls: list[tuple[str, str, str]] = []

    def add(self, keyword: str, response: Response) -> None:
        self.script.append((keyword.lower(), response))

    def complete(self, system: str, prompt: str) -> str:
        haystack = f"{system}\n{prompt}".lower()
        response: Optional[str] = None
        for keyword, resp in self.script:
            if keyword in haystack:
                response = resp(system, prompt) if callable(resp) else resp
                break
        if response is None:
            if self.default is not None:
                response = self.default
            else:
                first = " ".join(prompt.split())[:80]
                response = f"[mock] {first}"
        self.calls.append((system, prompt, response))
        return response
