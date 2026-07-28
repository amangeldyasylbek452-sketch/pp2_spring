"""
achievements.py
---------------
A tiny achievement system. Each achievement has a condition function that is
checked against the current run's stats every frame. When newly unlocked, a
toast notification is queued for the UI to display briefly.
"""


class Achievement:
    def __init__(self, key, title, description, condition):
        self.key = key
        self.title = title
        self.description = description
        self.condition = condition   # function(stats_dict) -> bool
        self.unlocked = False


class AchievementSystem:
    def __init__(self):
        self.achievements = [
            Achievement("first_coin", "First Coin!", "Collect your first coin.",
                        lambda s: s["coins"] >= 1),
            Achievement("coin_collector", "Coin Collector", "Collect 25 coins in one run.",
                        lambda s: s["coins"] >= 25),
            Achievement("high_climber", "High Climber", "Reach a height of 500m.",
                        lambda s: s["height"] >= 500),
            Achievement("sky_scraper", "Sky Scraper", "Reach a height of 1500m.",
                        lambda s: s["height"] >= 1500),
            Achievement("survivor", "Survivor", "Survive for 60 seconds.",
                        lambda s: s["time"] >= 60),
            Achievement("iron_will", "Iron Will", "Survive for 3 minutes.",
                        lambda s: s["time"] >= 180),
            Achievement("power_hungry", "Power Hungry", "Collect 5 power-ups in one run.",
                        lambda s: s["powerups_collected"] >= 5),
            Achievement("combo_master", "Combo Master", "Reach a x5 coin combo.",
                        lambda s: s["max_combo"] >= 5),
        ]
        self.toast_queue = []
        self.toast_timer = 0.0
        self.current_toast = None

    def reset_session_flags(self):
        """Call at the start of a new run so achievements can re-trigger
        their unlock toast feel fresh each run, while still only counting
        truly-unlocked-once achievements toward the overall list."""
        pass

    def check(self, stats):
        for ach in self.achievements:
            if not ach.unlocked and ach.condition(stats):
                ach.unlocked = True
                self.toast_queue.append(ach)

    def update(self, dt):
        if self.current_toast is None and self.toast_queue:
            self.current_toast = self.toast_queue.pop(0)
            self.toast_timer = 3.0
        elif self.current_toast is not None:
            self.toast_timer -= dt
            if self.toast_timer <= 0:
                self.current_toast = None

    def unlocked_count(self):
        return sum(1 for a in self.achievements if a.unlocked)
