import pygame, random, json, psycopg2
from datetime import datetime

pygame.init()

# -------------------- DB --------------------
conn = None
try:
    conn = psycopg2.connect(
        dbname="snake",
        user="postgres",
        password="1234",
        host="localhost"
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS players(
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS game_sessions(
        id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES players(id),
        score INTEGER,
        level_reached INTEGER,
        played_at TIMESTAMP DEFAULT NOW()
    )""")
except:
    conn = None

# -------------------- SCREEN --------------------
WIDTH, HEIGHT = 640, 480
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# -------------------- COLORS --------------------
WHITE=(255,255,255)
GREEN=(0,200,0)
RED=(200,0,0)
BLUE=(0,150,255)
GRAY=(100,100,100)
BLACK=(20,20,20)
YELLOW=(240,200,0)

font = pygame.font.SysFont(None,30)

# -------------------- SETTINGS --------------------
def load_settings():
    try:
        return json.load(open("settings.json"))
    except:
        return {"color":[0,200,0],"grid":True,"sound":True}

def save_settings(s):
    json.dump(s,open("settings.json","w"))

settings = load_settings()

# -------------------- DB FUNCTIONS --------------------
def get_player_id(username):
    if not conn: return None
    cur.execute("INSERT INTO players(username) VALUES(%s) ON CONFLICT DO NOTHING",(username,))
    cur.execute("SELECT id FROM players WHERE username=%s",(username,))
    return cur.fetchone()[0]

def save_score(username,score,level):
    if not conn: return
    pid = get_player_id(username)
    cur.execute("INSERT INTO game_sessions(player_id,score,level_reached) VALUES(%s,%s,%s)",
                (pid,score,level))

def get_best(username):
    if not conn: return 0
    cur.execute("""SELECT MAX(score) FROM game_sessions g
                   JOIN players p ON g.player_id=p.id
                   WHERE p.username=%s""",(username,))
    r=cur.fetchone()[0]
    return r or 0

def get_top():
    if not conn: return []
    cur.execute("""SELECT p.username,g.score,g.level_reached,g.played_at
                   FROM game_sessions g JOIN players p ON g.player_id=p.id
                   ORDER BY score DESC LIMIT 10""")
    return cur.fetchall()

# -------------------- GAME --------------------
state="menu"
username=""
input_active=True

# 🐍 snake
snake=[]
direction=(1,0)

# 🍎 food
food=None

# ☠️ poison
poison=None

# ⚡ power-up
power=None
power_type=None
power_end=0

# 🧱 obstacles
obstacles=set()

score=0
level=1
best=0

# -------------------- HELPERS --------------------
def rand_pos(exclude=set()):
    while True:
        p=(random.randrange(0,WIDTH//CELL),random.randrange(0,HEIGHT//CELL))
        if p not in exclude:
            return p

def reset():
    global snake,food,poison,power,score,level,obstacles
    snake=[(10,10),(9,10),(8,10)]  # 🐍 snake
    food=rand_pos(set(snake))      # 🍎 food
    poison=None                    # ☠️ poison
    power=None                     # ⚡ power-up
    obstacles=set()                # 🧱 obstacles
    score=0
    level=1

# -------------------- LOGIC --------------------
def move():
    global score,food,poison,power,power_type,power_end

    head=snake[0]
    new=(head[0]+direction[0],head[1]+direction[1])

    if new[0]<0 or new[1]<0 or new[0]>=WIDTH//CELL or new[1]>=HEIGHT//CELL:
        if power_type=="shield":
            return True
        return False

    if new in obstacles:
        return False

    if new in snake:
        if power_type=="shield":
            return True
        return False

    snake.insert(0,new)

    # 🍎 food
    if new==food:
        score+=10
        food=rand_pos(set(snake)|obstacles)
    else:
        snake.pop()

    # ☠️ poison
    if poison and new==poison:
        poison=None
        if len(snake)<=2:
            return False
        snake.pop()
        snake.pop()

    # ⚡ power-up
    if power and new==power:
        power_type=random.choice(["speed","slow","shield"])
        power_end=pygame.time.get_ticks()+5000
        power=None

    return True

def spawn():
    global poison,power
    if not poison and random.random()<0.01:
        poison=rand_pos(set(snake)|obstacles)
    if not power and random.random()<0.01:
        power=rand_pos(set(snake)|obstacles|{food})

def update_level():
    global level
    if score//50+1>level:
        level+=1
        if level>=3:
            for _ in range(5):
                obstacles.add(rand_pos(set(snake)))

# -------------------- DRAW --------------------
def draw_game():
    screen.fill(BLACK)

    if settings["grid"]:
        for x in range(0,WIDTH,CELL):
            pygame.draw.line(screen,GRAY,(x,0),(x,HEIGHT))
        for y in range(0,HEIGHT,CELL):
            pygame.draw.line(screen,GRAY,(0,y),(WIDTH,y))

    # 🧱 obstacles
    for o in obstacles:
        pygame.draw.rect(screen,GRAY,(o[0]*CELL,o[1]*CELL,CELL,CELL))

    # 🐍 snake
    for s in snake:
        pygame.draw.rect(screen,settings["color"],(s[0]*CELL,s[1]*CELL,CELL,CELL))

    # 🍎 food
    pygame.draw.rect(screen,YELLOW,(food[0]*CELL,food[1]*CELL,CELL,CELL))

    # ☠️ poison
    if poison:
        pygame.draw.rect(screen,RED,(poison[0]*CELL,poison[1]*CELL,CELL,CELL))

    # ⚡ power-up
    if power:
        pygame.draw.rect(screen,BLUE,(power[0]*CELL,power[1]*CELL,CELL,CELL))

    screen.blit(font.render(f"{username} Score:{score} Level:{level} Best:{best}",True,WHITE),(10,10))

# 🎮 MENU
def draw_menu():
    screen.fill(BLACK)
    screen.blit(font.render("Enter username:",True,WHITE),(200,150))
    screen.blit(font.render(username,True,WHITE),(200,200))
    screen.blit(font.render("ENTER play | L leaderboard | S settings",True,WHITE),(120,250))

# 🎮 LEADERBOARD
def draw_leaderboard():
    screen.fill(BLACK)
    y=50
    for i,row in enumerate(get_top()):
        txt=f"{i+1}. {row[0]} {row[1]}"
        screen.blit(font.render(txt,True,WHITE),(100,y))
        y+=30

# 🎮 SETTINGS
def draw_settings():
    screen.fill(BLACK)
    screen.blit(font.render("G - toggle grid",True,WHITE),(200,200))
    screen.blit(font.render("ESC - back",True,WHITE),(200,250))

# 🎮 GAME OVER
def draw_gameover():
    screen.fill(BLACK)
    screen.blit(font.render("GAME OVER",True,RED),(250,200))
    screen.blit(font.render("R - retry | M - menu",True,WHITE),(180,250))

# -------------------- MAIN --------------------
running=True
last=0

while running:
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False

        if e.type==pygame.KEYDOWN:

            if state=="menu":
                if e.key==pygame.K_RETURN:
                    best=get_best(username)
                    reset()
                    state="game"
                elif e.key==pygame.K_l:
                    state="leaderboard"
                elif e.key==pygame.K_s:
                    state="settings"
                elif e.key==pygame.K_BACKSPACE:
                    username=username[:-1]
                else:
                    username+=e.unicode

            elif state=="game":
                if e.key==pygame.K_UP and direction!=(0,1): direction=(0,-1)
                if e.key==pygame.K_DOWN and direction!=(0,-1): direction=(0,1)
                if e.key==pygame.K_LEFT and direction!=(1,0): direction=(-1,0)
                if e.key==pygame.K_RIGHT and direction!=(-1,0): direction=(1,0)

            elif state=="gameover":
                if e.key==pygame.K_r:
                    reset()
                    state="game"
                if e.key==pygame.K_m:
                    state="menu"

            elif state=="leaderboard":
                if e.key==pygame.K_ESCAPE:
                    state="menu"

            elif state=="settings":
                if e.key==pygame.K_g:
                    settings["grid"]=not settings["grid"]
                    save_settings(settings)
                if e.key==pygame.K_ESCAPE:
                    state="menu"

    if state=="game":
        speed=120
        if power_type=="speed": speed=70
        if power_type=="slow": speed=200

        if pygame.time.get_ticks()>power_end:
            power_type=None

        if pygame.time.get_ticks()-last>speed:
            if not move():
                save_score(username,score,level)
                state="gameover"
            spawn()
            update_level()
            last=pygame.time.get_ticks()

        draw_game()

    elif state=="menu":
        draw_menu()

    elif state=="leaderboard":
        draw_leaderboard()

    elif state=="settings":
        draw_settings()

    elif state=="gameover":
        draw_gameover()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()