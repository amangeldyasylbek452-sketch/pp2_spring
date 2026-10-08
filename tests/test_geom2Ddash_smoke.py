import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "geom2Ddash"))

import main


class Geo2DDashSmokeTest(unittest.TestCase):
    def test_build_game_creates_core_components(self):
        game = main.build_game()
        self.assertIsNotNone(game["player"])
        self.assertIsNotNone(game["level"])
        self.assertIsNotNone(game["particles"])
        self.assertTrue(game["player"].alive)


if __name__ == "__main__":
    unittest.main()
