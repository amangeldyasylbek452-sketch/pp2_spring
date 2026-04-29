import pygame
import sys
import datetime

pygame.init()


# SCREEN SETUP
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("PaintPRO")
clock = pygame.time.Clock()



# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
YELLOW = (255, 220, 0)

GRAY = (200, 200, 200)
DARK_GRAY = (130, 130, 130)



# CANVAS
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)



# TOOLS SETTINGS
current_tool = "pencil"
current_color = BLACK
brush_size = 5

size_buttons = [
    {"label": "1", "size": 2, "rect": pygame.Rect(720, 10, 40, 30)},
    {"label": "2", "size": 5, "rect": pygame.Rect(770, 10, 40, 30)},
    {"label": "3", "size": 10, "rect": pygame.Rect(820, 10, 40, 30)},
]



# TEXT SETTINGS
font = pygame.font.SysFont(None, 24)
text_font = pygame.font.SysFont(None, 28)

text_mode = False
text_buffer = ""
text_position = None



# STATE VARIABLES
drawing = False
start_pos = None
last_pos = None

save_message = ""
message_time = 0



# HELPER FUNCTIONS
def draw_text(text, pos, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, pos)


def normalize_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def flood_fill(surface, pos, fill_color):
    x, y = pos
    target_color = surface.get_at((x, y))[:3]

    if target_color == fill_color:
        return

    stack = [(x, y)]
    while stack:
        px, py = stack.pop()
        if px < 0 or px >= WIDTH or py < 0 or py >= HEIGHT:
            continue

        if surface.get_at((px, py))[:3] != target_color:
            continue

        surface.set_at((px, py), fill_color)

        stack += [(px+1, py), (px-1, py), (px, py+1), (px, py-1)]


def save_canvas(surface):
    filename = f"canvas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pygame.image.save(surface, filename)
    return filename


# UI DRAWING
def draw_toolbar():
    pygame.draw.rect(screen, GRAY, (700, 0, 200, 80))

    draw_text("Size:", (705, 12))

    for btn in size_buttons:
        color = DARK_GRAY if btn["size"] == brush_size else WHITE
        pygame.draw.rect(screen, color, btn["rect"])
        pygame.draw.rect(screen, BLACK, btn["rect"], 1)

        label = font.render(btn["label"], True, BLACK)
        screen.blit(label, label.get_rect(center=btn["rect"].center))

    draw_text(f"Tool: {current_tool}", (705, 45))
    draw_text(f"Color: {current_color}", (705, 65))


def draw_preview(start, end):
    if current_tool == "line":
        pygame.draw.line(screen, DARK_GRAY, start, end, 2)

    elif current_tool == "rectangle":
        pygame.draw.rect(screen, DARK_GRAY, normalize_rect(start, end), 1)

    elif current_tool == "circle":
        rect = normalize_rect(start, end)
        radius = min(rect.width, rect.height) // 2
        center = rect.center
        pygame.draw.circle(screen, DARK_GRAY, center, radius, 1)


def render_text_preview():
    if text_mode and text_position:
        preview = text_font.render(text_buffer + "|", True, current_color)
        screen.blit(preview, text_position)



# MAIN LOOP
running = True
while running:

    for event in pygame.event.get():

        # EXIT
        if event.type == pygame.QUIT:
            running = False

        # KEYBOARD
        elif event.type == pygame.KEYDOWN:

            # TEXT INPUT MODE
            if text_mode:
                if event.key == pygame.K_RETURN:
                    canvas.blit(text_font.render(text_buffer, True, current_color), text_position)
                    text_mode = False
                    text_buffer = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]

                else:
                    text_buffer += event.unicode
                continue

            # TOOL SWITCH
            if event.key == pygame.K_p: current_tool = "pencil"
            if event.key == pygame.K_l: current_tool = "line"
            if event.key == pygame.K_q: current_tool = "rectangle"
            if event.key == pygame.K_c: current_tool = "circle"
            if event.key == pygame.K_f: current_tool = "fill"
            if event.key == pygame.K_t: current_tool = "text"

            # COLOR SWITCH
            if event.key == pygame.K_b: current_color = BLUE
            if event.key == pygame.K_r: current_color = RED
            if event.key == pygame.K_g: current_color = GREEN
            if event.key == pygame.K_k: current_color = BLACK

            # SAVE
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_message = save_canvas(canvas)
                message_time = pygame.time.get_ticks()

        #  MOUSE DOWN
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_tool == "fill":
                flood_fill(canvas, event.pos, current_color)

            elif current_tool == "text":
                text_mode = True
                text_position = event.pos

            else:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos

        # MOUSE MOVE
        elif event.type == pygame.MOUSEMOTION:
            if drawing and current_tool == "pencil":
                pygame.draw.line(canvas, current_color, last_pos, event.pos, brush_size)
                last_pos = event.pos

        # MOUSE UP
        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                if current_tool == "line":
                    pygame.draw.line(canvas, current_color, start_pos, event.pos, brush_size)

                elif current_tool == "rectangle":
                    pygame.draw.rect(canvas, current_color, normalize_rect(start_pos, event.pos), brush_size)

                elif current_tool == "circle":
                    rect = normalize_rect(start_pos, event.pos)
                    pygame.draw.circle(canvas, current_color, rect.center, min(rect.width, rect.height)//2, brush_size)

                drawing = False


  
  #RENDER
    screen.fill(WHITE)
    screen.blit(canvas, (0, 0))

    if drawing:
        draw_preview(start_pos, pygame.mouse.get_pos())

    draw_toolbar()
    render_text_preview()

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()