"""
skins.py - Unlockable cube skins and trail-effect definitions.
Every skin is drawn purely with primitives (no external art), keyed by a
palette + pattern + trail-effect combination.
"""

SKINS = [
    {
        "id": "classic",
        "name": "Classic Cube",
        "primary": (90, 200, 255),
        "secondary": (255, 255, 255),
        "pattern": "plain",
        "trail": "classic",
        "cost": 0,
    },
    {
        "id": "ice",
        "name": "Ice Cube",
        "primary": (170, 230, 255),
        "secondary": (255, 255, 255),
        "pattern": "facet",
        "trail": "ice",
        "cost": 15,
    },
    {
        "id": "fire",
        "name": "Fire Cube",
        "primary": (255, 110, 40),
        "secondary": (255, 210, 90),
        "pattern": "stripes",
        "trail": "fire",
        "cost": 25,
    },
    {
        "id": "neon",
        "name": "Neon Cube",
        "primary": (255, 40, 200),
        "secondary": (80, 255, 230),
        "pattern": "outline",
        "trail": "neon",
        "cost": 35,
    },
    {
        "id": "pixel",
        "name": "Pixel Cube",
        "primary": (120, 220, 120),
        "secondary": (40, 120, 60),
        "pattern": "grid",
        "trail": "pixel",
        "cost": 40,
    },
    {
        "id": "golden",
        "name": "Golden Cube",
        "primary": (255, 205, 70),
        "secondary": (255, 245, 200),
        "pattern": "facet",
        "trail": "sparkle",
        "cost": 60,
    },
    {
        "id": "crystal",
        "name": "Crystal Cube",
        "primary": (140, 190, 255),
        "secondary": (230, 245, 255),
        "pattern": "diamond",
        "trail": "ice",
        "cost": 70,
    },
    {
        "id": "shadow",
        "name": "Shadow Cube",
        "primary": (60, 55, 75),
        "secondary": (140, 60, 200),
        "pattern": "outline",
        "trail": "smoke",
        "cost": 80,
    },
    {
        "id": "galaxy",
        "name": "Galaxy Cube",
        "primary": (70, 40, 130),
        "secondary": (255, 255, 255),
        "pattern": "stars",
        "trail": "magic",
        "cost": 100,
    },
    {
        "id": "cyber",
        "name": "Cyber Cube",
        "primary": (20, 220, 200),
        "secondary": (255, 40, 140),
        "pattern": "grid",
        "trail": "lightning",
        "cost": 120,
    },
]

SKIN_BY_ID = {s["id"]: s for s in SKINS}

TRAIL_EFFECTS = ["classic", "ice", "fire", "neon", "pixel", "sparkle",
                  "smoke", "magic", "lightning", "rainbow"]


class SkinManager:
    """Tracks which skins/trails are unlocked and which are equipped."""

    def __init__(self, save_data):
        self.save_data = save_data
        self.save_data.setdefault("unlocked_skins", ["classic"])
        self.save_data.setdefault("equipped_skin", "classic")

    @property
    def equipped(self):
        return SKIN_BY_ID.get(self.save_data["equipped_skin"], SKIN_BY_ID["classic"])

    def is_unlocked(self, skin_id):
        return skin_id in self.save_data["unlocked_skins"]

    def unlock(self, skin_id):
        if skin_id not in self.save_data["unlocked_skins"]:
            self.save_data["unlocked_skins"].append(skin_id)
            return True
        return False

    def equip(self, skin_id):
        if self.is_unlocked(skin_id):
            self.save_data["equipped_skin"] = skin_id
            return True
        return False

    def try_purchase(self, skin_id):
        """Spend coins from save_data['coins'] to unlock a skin."""
        skin = SKIN_BY_ID.get(skin_id)
        if not skin or self.is_unlocked(skin_id):
            return False
        if self.save_data.get("coins", 0) >= skin["cost"]:
            self.save_data["coins"] -= skin["cost"]
            self.unlock(skin_id)
            return True
        return False