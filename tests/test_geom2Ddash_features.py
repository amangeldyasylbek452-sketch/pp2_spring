import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "geom2Ddash"))

import main


class Geo2DDashFeaturesTest(unittest.TestCase):
    def test_menu_actions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "save.json"
            game = main.build_game(width=800, height=600, save_data={"coins": 0, "unlocked_skins": ["classic"], "equipped_skin": "classic", "last_world_id": "green_hills"}, save_path=path)
            game["menu_selection"] = 2
            main.activate_menu_selection(game)
            self.assertEqual(game["state"], "skin_menu")

    def test_menu_click_handler(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "save.json"
            game = main.build_game(width=800, height=600, save_data={"coins": 0, "unlocked_skins": ["classic"], "equipped_skin": "classic", "last_world_id": "green_hills"}, save_path=path)
            main.draw_menu(game)
            self.assertTrue(main.handle_menu_click(game, (90, 226)))
            self.assertEqual(game["state"], "playing")

    def test_save_data_and_worlds(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "save.json"
            data, _ = main.load_save_data(save_path)
            self.assertEqual(data["coins"], 0)
            self.assertGreaterEqual(len(main.get_world_options()), 3)

            data["equipped_skin"] = "ice"
            data["unlocked_skins"] = ["classic", "ice"]
            main.save_save_data(data, save_path)

            reloaded, _ = main.load_save_data(save_path)
            self.assertEqual(reloaded["equipped_skin"], "ice")
            self.assertIn("ice", reloaded["unlocked_skins"])


if __name__ == "__main__":
    unittest.main()
