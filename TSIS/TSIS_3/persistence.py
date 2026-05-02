# Этот файл работает с JSON-сохранением.
import json
import os

# Папка, где лежит проект.
BASE_DIR = os.path.dirname(__file__)
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")

# Настройки по умолчанию.
DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal"
}


# Загружает JSON или создает файл, если его нет.
def load_json(path, default_data):
    # Если файла нет, создаем его.
    if not os.path.exists(path):
        save_json(path, default_data)
        return default_data.copy()

    # Пробуем прочитать файл.
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    # Если файл сломан, возвращаем стандартные данные.
    except Exception:
        save_json(path, default_data)
        return default_data.copy()


# Сохраняет данные в JSON.
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Загружает настройки игры.
def load_settings():
    settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)

    # Добавляем недостающие настройки.
    for key, value in DEFAULT_SETTINGS.items():
        if key not in settings:
            settings[key] = value

    return settings


# Сохраняет настройки игры.
def save_settings(settings):
    save_json(SETTINGS_FILE, settings)


# Загружает таблицу рекордов.
def load_leaderboard():
    return load_json(LEADERBOARD_FILE, [])


# Добавляет новый результат игрока.
def save_score(username, score, distance, coins):
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": username,
        "score": int(score),
        "distance": int(distance),
        "coins": int(coins)
    })

    # Сортируем игроков по score.
    leaderboard.sort(key=lambda item: item["score"], reverse=True)
    # Оставляем только топ-10.
    leaderboard = leaderboard[:10]

    save_json(LEADERBOARD_FILE, leaderboard)