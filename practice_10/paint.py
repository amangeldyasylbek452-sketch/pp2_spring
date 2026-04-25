import pygame
import sys

# Initialize Pygame and set up
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Draw Shapes in Pygame")
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill(WHITE)

    # Draw a square
    square_rect = pygame.Rect(50, 50, 150, 150)
    pygame.draw.rect(screen, BLUE, square_rect, 4) 

    # Draw a right triangle
    right_triangle_points = [(300, 50), (300, 200), (450, 200)]
    pygame.draw.polygon(screen, GREEN, right_triangle_points, 4)

    # Draw an equilateral triangle
    equilateral_triangle_points = [(600, 100), (520, 220), (680, 220)]
    pygame.draw.polygon(screen, RED, equilateral_triangle_points, 4)

    # Draw a rhombus
    rhombus_points = [(200, 350), (300, 300), (400, 350), (300, 420)]
    pygame.draw.polygon(screen, ORANGE, rhombus_points, 4)

    # Draw small labels
    font = pygame.font.SysFont(None, 28)
    label_square = font.render("Square", True, BLACK)
    label_right = font.render("Right Triangle", True, BLACK)
    label_equilateral = font.render("Equilateral Triangle", True, BLACK)
    label_rhombus = font.render("Rhombus", True, BLACK)

    screen.blit(label_square, (75, 210))
    screen.blit(label_right, (300, 210))
    screen.blit(label_equilateral, (540, 240))
    screen.blit(label_rhombus, (305, 430))

    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
