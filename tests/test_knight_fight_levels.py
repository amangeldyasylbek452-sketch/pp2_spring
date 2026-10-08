import importlib.util
import sys
from pathlib import Path


def test_level_two_and_three_can_be_instantiated():
    root = Path(__file__).resolve().parents[1] / "knight fight"
    sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location("knight_fight_level", root / "level.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    level2 = module.Level2()
    level3 = module.Level3()

    assert level2.name == "The Cursed Kingdom"
    assert level3.name == "Dragon's Castle"
    assert level2.portal is not None
    assert level3.portal is not None
