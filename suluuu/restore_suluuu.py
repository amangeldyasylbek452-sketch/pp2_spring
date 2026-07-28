import shutil
import os

os.chdir(r"C:\Users\amang\Desktop\py\suluuu")

# Preserve current files while shifting sources back to their correct names.
steps = [
    ("lava.py", "requirements.txt"),
    ("achievements.py", "lava.py"),
    ("main.py", "camera.py"),
    ("particles.py", "ui.py"),
    ("requirements (3).txt", "main.py"),
    ("collectables.py", "constants.py"),
    ("level_generator.py", "collectables.py"),
    ("game.py", "platforms.py"),
    ("platforms.py", "level_generator.py"),
    ("player.py", "game.py"),
    ("README.md", "achievements.py"),
    ("constants.py", "README.md"),
]

for src, dst in steps:
    if not os.path.isfile(src):
        raise FileNotFoundError(f"Source file missing: {src}")
    shutil.copyfile(src, dst)

print("restore copy completed")
