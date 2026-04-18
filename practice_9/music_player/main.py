import pygame
import os

pygame.init()
pygame.mixer.init()


music_folder = r'C:\Users\amang\Desktop\py\practice_9\music_player\music'

songs = [os.path.join(music_folder, f)
         for f in os.listdir(music_folder)
         if f.endswith(('.mp3', '.wav'))]

if not songs:
    print("No music files found")
    pygame.quit()
    exit()

durations = [pygame.mixer.Sound(s).get_length() for s in songs]


current_index = 0
is_paused = False
current_time = 0


WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

clock = pygame.time.Clock()

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (0, 200, 0)
RED = (200, 0, 0)


font = pygame.font.SysFont("Arial", 28)
small_font = pygame.font.SysFont("Arial", 22)


def format_time(t):
    t = int(t)
    m = t // 60
    s = t % 60
    return f"{m:02}:{s:02}"

def play():
    global is_paused
    pygame.mixer.music.load(songs[current_index])
    pygame.mixer.music.play()
    is_paused = False

def stop():
    global is_paused
    pygame.mixer.music.stop()
    is_paused = False

def pause():
    global is_paused
    pygame.mixer.music.pause()
    is_paused = True

def unpause():
    global is_paused
    pygame.mixer.music.unpause()
    is_paused = False

def next_track():
    global current_index
    current_index = (current_index + 1) % len(songs)
    play()

def prev_track():
    global current_index
    current_index = (current_index - 1) % len(songs)
    play()


running = True

while running:
    screen.fill(BLUE)

    
    song_name = os.path.basename(songs[current_index])
    title = font.render(f"Now Playing: {song_name}", True, BLACK)
    screen.blit(title, (50, 50))

    
    y_offset = 120
    for i, song in enumerate(songs):
        name = os.path.basename(song)

        if i == current_index:
            text = small_font.render(f"> {i+1}. {name}", True, RED)
        else:
            text = small_font.render(f"{i+1}. {name}", True, BLACK)

        screen.blit(text, (50, y_offset + i * 30))


    if pygame.mixer.music.get_busy():
        current_time = pygame.mixer.music.get_pos() / 1000

    total_time = durations[current_index]

    start = format_time(current_time)
    end = format_time(total_time)

    time_text = font.render(f"{start} / {end}", True, BLACK)
    screen.blit(time_text, (50, 400))

  
    bar_x1, bar_x2 = 50, 900
    bar_y = 450

    pygame.draw.line(screen, GRAY, (bar_x1, bar_y), (bar_x2, bar_y), 6)

    if total_time > 0:
        progress = current_time / total_time
    else:
        progress = 0

    circle_x = bar_x1 + progress * (bar_x2 - bar_x1)

    pygame.draw.line(screen, GREEN, (bar_x1, bar_y), (circle_x, bar_y), 6)
    pygame.draw.circle(screen, BLACK, (int(circle_x), bar_y), 8)

  
    controls = [
        "P = Play / Resume",
        "S = Stop",
        "N = Next",
        "B = Previous",
        "Q = Quit"
    ]

    for i, c in enumerate(controls):
        text = small_font.render(c, True, BLACK)
        screen.blit(text, (700, 50 + i * 30))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

            elif event.key == pygame.K_p:
                if is_paused:
                    unpause()
                elif not pygame.mixer.music.get_busy():
                    play()

            elif event.key == pygame.K_s:
                stop()

            elif event.key == pygame.K_n:
                next_track()

            elif event.key == pygame.K_b:
                prev_track()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()