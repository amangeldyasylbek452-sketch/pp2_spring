import math
import pygame
import sys

# Initialize Pygame and set up
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Paint - Brush and Shapes")
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)

color_names = {
    "black": "Black",
    "blue": "Blue",
    "red": "Red",
    "green": "Green",
}
color_values = {
    "black": BLACK,
    "blue": BLUE,
    "red": RED,
    "green": GREEN,
}
current_color_name = "black"

# Create a canvas surface to keep drawings persistent
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# Current tool state
mode = "brush"
drawing = False
start_pos = None
prev_pos = None

# Text rendering helper
font = pygame.font.SysFont(None, 24)

shape_names = {
    "brush": "Brush",
    "square": "Square",
    "right_triangle": "Right Triangle",
    "equilateral_triangle": "Equilateral Triangle",
    "rhombus": "Rhombus",
    "circle": "Circle",
}


def normalize_rect(start, end):
    x1, y1 = start
    x2, y2 = end
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    return pygame.Rect(left, top, width, height)


def draw_shape(surface, tool, start, end, color):
    if tool == "square":
        rect = normalize_rect(start, end)
        size = min(rect.width, rect.height)
        rect.width = rect.height = size
        pygame.draw.rect(surface, color, rect, 3)

    elif tool == "right_triangle":
        rect = normalize_rect(start, end)
        points = [
            (rect.left, rect.top),
            (rect.left, rect.bottom),
            (rect.right, rect.bottom),
        ]
        pygame.draw.polygon(surface, color, points, 3)

    elif tool == "equilateral_triangle":
        rect = normalize_rect(start, end)
        side = min(rect.width, rect.height)
        if side == 0:
            return
        x = rect.left
        y = rect.top
        # Draw a flat base
        p1 = (x, y + side)
        p2 = (x + side, y + side)
        apex_x = x + side / 2
        apex_y = y + side - side * math.sqrt(3) / 2
        points = [(p1[0], p1[1]), (p2[0], p2[1]), (apex_x, apex_y)]
        pygame.draw.polygon(surface, color, points, 3)

    elif tool == "rhombus":
        rect = normalize_rect(start, end)
        width = rect.width
        height = rect.height
        if width == 0 or height == 0:
            return
        center_x = rect.left + width / 2
        center_y = rect.top + height / 2
        points = [
            (center_x, rect.top),
            (rect.right, center_y),
            (center_x, rect.bottom),
            (rect.left, center_y),
        ]
        pygame.draw.polygon(surface, color, points, 3)

    elif tool == "circle":
        rect = normalize_rect(start, end)
        radius = min(rect.width, rect.height) // 2
        if radius == 0:
            return
        center = (rect.left + rect.width // 2, rect.top + rect.height // 2)
        pygame.draw.circle(surface, color, center, radius, 3)

def draw_preview(surface, tool, start, end):
    if not start or not end or tool == "brush":
        return
    if tool == "square":
        rect = normalize_rect(start, end)
        size = min(rect.width, rect.height)
        rect.width = rect.height = size
        pygame.draw.rect(surface, GRAY, rect, 1)
    elif tool == "right_triangle":
        rect = normalize_rect(start, end)
        points = [
            (rect.left, rect.top),
            (rect.left, rect.bottom),
            (rect.right, rect.bottom),
        ]
        pygame.draw.polygon(surface, GRAY, points, 1)
    elif tool == "equilateral_triangle":
        rect = normalize_rect(start, end)
        side = min(rect.width, rect.height)
        if side == 0:
            return
        x = rect.left
        y = rect.top
        p1 = (x, y + side)
        p2 = (x + side, y + side)
        apex_x = x + side / 2
        apex_y = y + side - side * math.sqrt(3) / 2
        pygame.draw.polygon(surface, GRAY, [p1, p2, (apex_x, apex_y)], 1)
    elif tool == "rhombus":
        rect = normalize_rect(start, end)
        width = rect.width
        height = rect.height
        if width == 0 or height == 0:
            return
        center_x = rect.left + width / 2
        center_y = rect.top + height / 2
        points = [
            (center_x, rect.top),
            (rect.right, center_y),
            (center_x, rect.bottom),
            (rect.left, center_y),
        ]
        pygame.draw.polygon(surface, GRAY, points, 1)


def draw_instructions():
    instructions = [
        "Tools: 0=Brush, 1=Square, 2=Right Triangle, 3=Equilateral Triangle, 4=Rhombus, 5=Circle",
        "Colors: B=Blue, R=Red, G=Green, K=Black",
        "Click and drag for shapes. Drag with left mouse for freehand brush.",
        "Press C to clear canvas, ESC to quit.",
        f"Current tool: {shape_names.get(mode, mode)}",
        f"Current color: {color_names.get(current_color_name, current_color_name)}",
    ]
    for index, text in enumerate(instructions):
        label = font.render(text, True, BLACK)
        screen.blit(label, (10, 10 + index * 22))


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_0:
                mode = "brush"
            elif event.key == pygame.K_1:
                mode = "square"
            elif event.key == pygame.K_2:
                mode = "right_triangle"
            elif event.key == pygame.K_3:
                mode = "equilateral_triangle"
            elif event.key == pygame.K_4:
                mode = "rhombus"
            elif event.key == pygame.K_5:
                mode = "circle"
            elif event.key == pygame.K_b:
                current_color_name = "blue"
            elif event.key == pygame.K_r:
                current_color_name = "red"
            elif event.key == pygame.K_g:
                current_color_name = "green"
            elif event.key == pygame.K_k:
                current_color_name = "black"
            elif event.key == pygame.K_c:
                canvas.fill(WHITE)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drawing = True
                start_pos = event.pos
                prev_pos = event.pos
                if mode == "brush":
                    pygame.draw.circle(canvas, color_values[current_color_name], event.pos, 4)

        elif event.type == pygame.MOUSEMOTION:
            if drawing and mode == "brush" and prev_pos:
                pygame.draw.line(canvas, color_values[current_color_name], prev_pos, event.pos, 8)
                prev_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                end_pos = event.pos
                if mode != "brush" and start_pos:
                    draw_shape(canvas, mode, start_pos, end_pos, color_values[current_color_name])
                drawing = False
                prev_pos = None

    screen.fill(WHITE)
    screen.blit(canvas, (0, 0))


    if drawing and mode != "brush" and start_pos:
        mouse_pos = pygame.mouse.get_pos()
        draw_preview(screen, mode, start_pos, mouse_pos)

    draw_instructions()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
