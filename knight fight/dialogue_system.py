import json
from pathlib import Path


class DialogueSystem:
    def __init__(self, data_path="data/dialogue.json"):
        self.data_path = Path(data_path)
        self.dialogue = {}
        self.load()

    def load(self):
        if self.data_path.exists():
            with self.data_path.open("r", encoding="utf-8") as handle:
                self.dialogue = json.load(handle)
        else:
            self.dialogue = {}

    def get_text(self, speaker, key):
        return self.dialogue.get(speaker, {}).get(key, "...")
