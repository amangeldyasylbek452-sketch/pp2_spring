# Импортируем Pygame и файлы проекта.
import pygame
from racerMAX import WIDTH, HEIGHT, FPS, RacerGame
from ui import Button, draw_text, username_screen, WHITE, DARK, YELLOW, GREEN, RED
from persistence import load_settings, save_settings, load_leaderboard, save_score

# Запускаем Pygame.
pygame.init()

# Создаем окно игры.
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)
small_font = pygame.font.SysFont("Verdana", 16)

# Загружаем настройки из JSON-файла.
settings = load_settings()
username = "Player"
last_result = None


# Главное меню игры.
def main_menu():
    global username

    # Кнопки главного меню.
    buttons = [
        Button(100, 190, 200, 45, "Play", font),
        Button(100, 250, 200, 45, "Leaderboard", font),
        Button(100, 310, 200, 45, "Settings", font),
        Button(100, 370, 200, 45, "Quit", font)
    ]

    while True:
        clock.tick(FPS)

        # Проверяем действия игрока.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if buttons[0].clicked(event):
                username = username_screen(screen, clock, WIDTH, HEIGHT)
                return "play"
            if buttons[1].clicked(event):
                return "leaderboard"
            if buttons[2].clicked(event):
                return "settings"
            if buttons[3].clicked(event):
                pygame.quit()
                raise SystemExit

        # Рисуем фон и заголовок меню.
        screen.fill(DARK)
        draw_text(screen, "TSIS3 RACER", 36, WHITE, WIDTH // 2, 100)
        draw_text(screen, "Advanced Driving Game", 17, YELLOW, WIDTH // 2, 140)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()


# Экран таблицы рекордов.
def leaderboard_screen():
    back = Button(110, 530, 180, 42, "Back", font)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if back.clicked(event):
                return "menu"

        screen.fill(DARK)
        draw_text(screen, "Leaderboard Top 10", 28, WHITE, WIDTH // 2, 60)

        # Загружаем топ игроков из leaderboard.json.
        data = load_leaderboard()
        if not data:
            draw_text(screen, "No scores yet", 20, YELLOW, WIDTH // 2, 180)
        else:
            y = 115
            draw_text(screen, "Rank   Name       Score    Distance", 14, YELLOW, 35, 90, center=False)
            for i, row in enumerate(data, start=1):
                text = f"{i:<5} {row['name'][:8]:<9} {row['score']:<7} {row['distance']}m"
                surface = small_font.render(text, True, WHITE)
                screen.blit(surface, (35, y))
                y += 34

        back.draw(screen)
        pygame.display.flip()


# Экран настроек.
def settings_screen():
    global settings

    sound = Button(70, 160, 260, 42, "", font)
    color = Button(70, 230, 260, 42, "", font)
    difficulty = Button(70, 300, 260, 42, "", font)
    back = Button(110, 430, 180, 42, "Back", font)

    # Возможные цвета машины.
    colors = ["blue", "red", "green"]
    # Возможные уровни сложности.
    difficulties = ["easy", "normal", "hard"]

    while True:
        clock.tick(FPS)

        # Обновляем текст кнопок по текущим настройкам.
        sound.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        color.text = f"Car color: {settings['car_color']}"
        difficulty.text = f"Difficulty: {settings['difficulty']}"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # При клике меняем настройку и сохраняем ее.
            if sound.clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)

            if color.clicked(event):
                index = colors.index(settings["car_color"])
                settings["car_color"] = colors[(index + 1) % len(colors)]
                save_settings(settings)

            if difficulty.clicked(event):
                index = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                save_settings(settings)

            if back.clicked(event):
                return "menu"

        screen.fill(DARK)
        draw_text(screen, "Settings", 32, WHITE, WIDTH // 2, 80)
        sound.draw(screen)
        color.draw(screen)
        difficulty.draw(screen)
        back.draw(screen)
        pygame.display.flip()


# Экран после победы или проигрыша.
def game_over_screen(result, finished=False):
    retry = Button(95, 365, 210, 42, "Retry", font)
    menu = Button(95, 425, 210, 42, "Main Menu", font)

    title = "FINISHED!" if finished else "GAME OVER"
    color = GREEN if finished else RED

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if retry.clicked(event):
                return "play"
            if menu.clicked(event):
                return "menu"

        screen.fill(DARK)
        draw_text(screen, title, 36, color, WIDTH // 2, 105)
        draw_text(screen, f"Player: {username}", 20, WHITE, WIDTH // 2, 175)
        draw_text(screen, f"Score: {result['score']}", 20, WHITE, WIDTH // 2, 215)
        draw_text(screen, f"Distance: {result['distance']}m", 20, WHITE, WIDTH // 2, 250)
        draw_text(screen, f"Coins: {result['coins']}", 20, WHITE, WIDTH // 2, 285)
        retry.draw(screen)
        menu.draw(screen)
        pygame.display.flip()


# Запускает гонку и сохраняет результат.
def play_game():
    game = RacerGame(screen, clock, username, settings)
    status = game.run()

    # Данные для финального экрана.
    result = {
        "score": game.score,
        "distance": int(game.distance),
        "coins": game.coins
    }

    # Сохраняем результат в leaderboard.json.
    save_score(username, game.score, game.distance, game.coins)

    return game_over_screen(result, finished=(status == "finished"))


# Главный цикл переключает экраны.
def main():
    state = "menu"

    while True:
        if state == "menu":
            state = main_menu()
        elif state == "play":
            state = play_game()
        elif state == "leaderboard":
            state = leaderboard_screen()
        elif state == "settings":
            state = settings_screen()


if __name__ == "__main__":
    main()