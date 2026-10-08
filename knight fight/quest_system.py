import json
import os
from pathlib import Path


class QuestSystem:
    def __init__(self, data_path="data/quests.json"):
        self.data_path = Path(data_path)
        self.quests = []
        self.load()

    def load(self):
        if self.data_path.exists():
            with self.data_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                self.quests = data.get("quests", [])
        else:
            self.quests = []

    def save(self):
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with self.data_path.open("w", encoding="utf-8") as handle:
            json.dump({"quests": self.quests}, handle, indent=2)

    def get_active_quest(self):
        return next((quest for quest in self.quests if not quest.get("completed", False)), None)

    def complete(self, quest_id):
        for quest in self.quests:
            if quest.get("id") == quest_id:
                quest["completed"] = True
                self.save()
                return True
        return False
