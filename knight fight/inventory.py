import json
from pathlib import Path


class Inventory:
    def __init__(self, data_path="data/items.json"):
        self.data_path = Path(data_path)
        self.items = {}
        self.load()

    def load(self):
        if self.data_path.exists():
            with self.data_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                self.items = {item["id"]: item for item in data.get("items", [])}
        else:
            self.items = {}

    def add(self, item_id, count=1):
        self.items[item_id] = self.items.get(item_id, {"id": item_id, "count": 0})
        self.items[item_id]["count"] = self.items[item_id].get("count", 0) + count

    def get_items(self):
        return list(self.items.values())
