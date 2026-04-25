import pygame
import random
import os

pygame.init()
pygame.mixer.init()



pygame.mixer.music.load("C:/Users/amang/Desktop/py/practice_10/music.mp3")
pygame.mixer.music.play(-1)

# Screen
WIDTH, HEIGHT = 640, 480
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
BLACK = (0, 0, 0)
BG_COLOR = (15, 15, 30)
BLUE = (0, 180, 255)
BROWN = (139, 69, 19)

# States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
state = STATE_MENU

# Snake
snake_pos = [(WIDTH // 2, HEIGHT // 2)]
direction = (CELL_SIZE, 0)

# Food
food_pos = (100, 100)

score = 0
level = 1
LEVEL_STEP = 5

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)

PLAY_AREA = pygame.Rect(20, 20, WIDTH - 40, HEIGHT - 40)


def reset_game():
    global snake_pos, direction, food_pos, score, level
    snake_pos = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL_SIZE, 0)
    score = 0
    level = 1
    food_pos = place_food()


def get_speed():
    return 6 + (level - 1) * 2  # increases every level


def place_food():
    while True:
        pos = (
            random.randrange(PLAY_AREA.left, PLAY_AREA.right, CELL_SIZE),
            random.randrange(PLAY_AREA.top, PLAY_AREA.bottom, CELL_SIZE)
        )
        if pos not in snake_pos:
            return pos


def move_snake():
    global food_pos, score, level

    head_x, head_y = snake_pos[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)

    snake_pos.insert(0, new_head)

    if new_head == food_pos:
        score += 1
        level = score // LEVEL_STEP + 1
        food_pos = place_food()
    else:
        snake_pos.pop()


def check_collision():
    head = snake_pos[0]
    if not PLAY_AREA.collidepoint(head):
        return True
    if head in snake_pos[1:]:
        return True
    return False


def draw_background():
    screen.fill(BG_COLOR)

    # simple stars decoration
    for _ in range(30):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.circle(screen, (40, 40, 80), (x, y), 1)


def draw_snake():
    for segment in snake_pos:
        pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, DARK_GREEN, (segment[0]+4, segment[1]+4, CELL_SIZE-8, CELL_SIZE-8))


def draw_apple():
    x, y = food_pos

    # apple body
    pygame.draw.circle(screen, RED, (x + 10, y + 10), 9)

    # highlight
    pygame.draw.circle(screen, (255, 120, 120), (x + 7, y + 7), 3)

    # stem
    pygame.draw.rect(screen, BROWN, (x + 9, y - 2, 3, 6))

    # leaf
    pygame.draw.ellipse(screen, GREEN, (x + 12, y - 4, 8, 5))


def draw_ui():
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, HEIGHT - 30))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (WIDTH - 140, HEIGHT - 30))


def draw_menu():
    draw_background()
    screen.blit(big_font.render("SNAKE", True, BLUE), (WIDTH//2 - 100, 150))
    screen.blit(font.render("Press ENTER to Start", True, WHITE), (WIDTH//2 - 150, 250))
    pygame.display.flip()


def draw_game_over():
    screen.blit(big_font.render("GAME OVER", True, RED), (WIDTH//2 - 150, HEIGHT//2 - 40))
    screen.blit(font.render("Press R to Restart", True, WHITE), (WIDTH//2 - 130, HEIGHT//2 + 20))
    pygame.display.flip()


def draw():
    draw_background()
    pygame.draw.rect(screen, BLUE, PLAY_AREA, 3)

    draw_snake()
    draw_apple()
    draw_ui()

    pygame.display.flip()


def main():
    global direction, state

    running = True
    reset_game()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if state == STATE_MENU:
                    if event.key == pygame.K_RETURN:
                        state = STATE_PLAYING

                elif state == STATE_PLAYING:
                    if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                        direction = (0, -CELL_SIZE)
                    elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                        direction = (0, CELL_SIZE)
                    elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                        direction = (-CELL_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                        direction = (CELL_SIZE, 0)

                elif state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        reset_game()
                        state = STATE_PLAYING

        if state == STATE_MENU:
            draw_menu()

        elif state == STATE_PLAYING:
            move_snake()
            if check_collision():
                state = STATE_GAME_OVER
            draw()

        elif state == STATE_GAME_OVER:
            draw_game_over()

        clock.tick(get_speed())

    pygame.quit()


if __name__ == "__main__":
    main()