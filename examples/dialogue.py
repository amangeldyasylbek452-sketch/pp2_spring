"""systems/dialogue.py — branching dialogue trees with a typewriter reveal."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DialogueLine:
    speaker: str
    text: str
    choices: list[tuple[str, str]] = field(default_factory=list)
    next_id: str | None = None
    on_enter: str | None = None


class DialogueTree:
    def __init__(self, nodes: dict[str, DialogueLine], start: str = "start") -> None:
        self.nodes = nodes
        self.start = start


class DialogueRunner:
    """Drives a DialogueTree: typewriter reveal + branching selection."""

    def __init__(self) -> None:
        self.tree: DialogueTree | None = None
        self.node_id: str | None = None
        self.revealed = 0
        self.char_timer = 0.0
        self.chars_per_sec = 42.0
        self.active = False
        self.selected_choice = 0
        self.on_event = None

    def start(self, tree: DialogueTree, on_event=None) -> None:
        self.tree = tree
        self.node_id = tree.start
        self.revealed = 0
        self.char_timer = 0.0
        self.active = True
        self.selected_choice = 0
        self.on_event = on_event
        self._fire_enter_event()

    def _fire_enter_event(self):
        node = self.current_node()
        if node and node.on_enter and self.on_event:
            self.on_event(node.on_enter)

    def current_node(self) -> DialogueLine | None:
        if not self.tree or self.node_id is None:
            return None
        return self.tree.nodes.get(self.node_id)

    def update(self, dt: float) -> None:
        node = self.current_node()
        if not node or not self.active:
            return
        if self.revealed < len(node.text):
            self.char_timer += dt * self.chars_per_sec
            self.revealed = min(len(node.text), int(self.char_timer))

    def is_fully_revealed(self) -> bool:
        node = self.current_node()
        return bool(node) and self.revealed >= len(node.text)

    def displayed_text(self) -> str:
        node = self.current_node()
        if not node:
            return ""
        return node.text[: self.revealed]

    def advance(self) -> None:
        node = self.current_node()
        if not node:
            self.active = False
            return
        if not self.is_fully_revealed():
            self.revealed = len(node.text)
            return
        if node.choices:
            _, next_id = node.choices[self.selected_choice]
            self.node_id = next_id
        elif node.next_id:
            self.node_id = node.next_id
        else:
            self.active = False
            return
        self.revealed = 0
        self.char_timer = 0.0
        self._fire_enter_event()

    def move_choice(self, delta: int) -> None:
        node = self.current_node()
        if node and node.choices:
            self.selected_choice = (self.selected_choice + delta) % len(node.choices)
