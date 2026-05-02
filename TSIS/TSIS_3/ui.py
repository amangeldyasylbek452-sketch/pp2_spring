# Этот файл отвечает за интерфейс.
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
DARK = (25, 25, 25)
GREEN = (20, 180, 80)
RED = (220, 60, 60)
YELLOW = (255, 210, 80)
BLUE = (70, 140, 255)


# Класс кнопки для меню.
class Button:
    # Создаем прямоугольник кнопки и ее текст.
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

    # Рисуем кнопку на экране.
    def draw(self, screen):
        # Если мышка на кнопке, меняем цвет.
        mouse_pos = pygame.mouse.get_pos()
        color = GREEN if self.rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    # Проверяет клик по кнопке.
    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


# Удобная функция для вывода текста.
def draw_text(screen, text, size, color, x, y, center=True):
    font = pygame.font.SysFont("Verdana", size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


# Экран ввода имени игрока.
def username_screen(screen, clock, width, height):
    username = ""
    font = pygame.font.SysFont("Verdana", 24)

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # Обрабатываем клавиши.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 12 and event.unicode.isprintable():
                    username += event.unicode

        # Рисуем поле ввода.
        screen.fill(DARK)
        draw_text(screen, "Enter username", 32, WHITE, width // 2, 180)
        pygame.draw.rect(screen, WHITE, (80, 260, width - 160, 50), 2, border_radius=8)
        input_text = font.render(username, True, WHITE)
        screen.blit(input_text, (95, 270))
        draw_text(screen, "Press ENTER to start", 18, YELLOW, width // 2, 350)
        pygame.display.flip()