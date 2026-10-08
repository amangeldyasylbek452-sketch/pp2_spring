"""
event_bus.py - Simple event bus for decoupled intra-game messaging.

Provides both immediate emit() and queued post() semantics. Systems can
subscribe to event types (strings) and receive events via callbacks. The
bus is intentionally small and synchronous by default, with an optional
queue processed once per frame by calling process_queue().

Example usage:
    bus = EventBus()
    bus.subscribe('player_damage', on_player_damage)
    bus.emit('player_damage', amount=10, source=enemy)

This enables decoupling of systems (combat, UI, quests, audio) and
simplifies refactors where systems shouldn't directly call each other.
"""
from __future__ import annotations

import typing as T
from collections import deque


class Event:
    def __init__(self, name: str, **data) -> None:
        self.name = name
        self.data = data


class EventBus:
    def __init__(self) -> None:
        # mapping: event_name -> list of handlers
        self._subs: dict[str, list[T.Callable[[Event], None]]] = {}
        self._queue: deque[Event] = deque()

    def subscribe(self, event_name: str, handler: T.Callable[[Event], None]) -> None:
        self._subs.setdefault(event_name, []).append(handler)

    def unsubscribe(self, event_name: str, handler: T.Callable[[Event], None]) -> None:
        handlers = self._subs.get(event_name)
        if not handlers:
            return
        try:
            handlers.remove(handler)
        except ValueError:
            pass

    def emit(self, event_name: str, **data) -> None:
        """Immediately dispatch an event to subscribers."""
        handlers = list(self._subs.get(event_name, []))
        if not handlers:
            return
        ev = Event(event_name, **data)
        for h in handlers:
            try:
                h(ev)
            except Exception:
                # swallow exceptions for robustness; systems should log if needed
                continue

    def post(self, event_name: str, **data) -> None:
        """Queue an event to be processed later via process_queue()."""
        self._queue.append(Event(event_name, **data))

    def process_queue(self) -> None:
        """Process all queued events in FIFO order."""
        while self._queue:
            ev = self._queue.popleft()
            handlers = list(self._subs.get(ev.name, []))
            for h in handlers:
                try:
                    h(ev)
                except Exception:
                    continue


# Module-level default bus for quick access
_default_bus: T.Optional[EventBus] = None


def default_bus() -> EventBus:
    global _default_bus
    if _default_bus is None:
        _default_bus = EventBus()
    return _default_bus
