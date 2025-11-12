import pygame
import sys
import random

pygame.init()

# --- Configuración general ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vida Marina - Versión Final Plus")
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# --- Recursos gráficos y sonidos ---
fondo = pygame.image.load("fondo.png")
pez_img = pygame.image.load("Pez.png")
pez_img = pygame.transform.scale(pez_img, (50, 50))
alga_img = pygame.image.load("alga.png")
alga_img = pygame.transform.scale(alga_img, (40, 60))
basura_img = pygame.image.load("papel.png")
basura_img = pygame.transform.scale(basura_img, (40, 40))
lata_img = pygame.image.load("lata.png")
lata_img = pygame.transform.scale(lata_img, (35, 45))
llanta_img = pygame.image.load("llanta.png")
llanta_img = pygame.transform.scale(llanta_img, (55, 55))

sonido_comer = pygame.mixer.Sound("bite.mp3")
sonido_malo = pygame.mixer.Sound("error.mp3")

# --- Jugador (pez) ---
fish = pez_img.get_rect(topleft=(WIDTH // 2, HEIGHT - 60))
fish_speed = 7

# --- Listas de objetos ---
algas = []
basuras = []
latas = []
llantas = []

# --- Eventos temporizados ---
SPAWN_ALGA_EVENT = pygame.USEREVENT + 1
SPAWN_BASURA_EVENT = pygame.USEREVENT + 2
SPAWN_LATA_EVENT = pygame.USEREVENT + 3
SPAWN_LLANTA_EVENT = pygame.USEREVENT + 4
pygame.time.set_timer(SPAWN_ALGA_EVENT, 1000)
pygame.time.set_timer(SPAWN_BASURA_EVENT, 1300)
pygame.time.set_timer(SPAWN_LATA_EVENT, 1700)
pygame.time.set_timer(SPAWN_LLANTA_EVENT, 2200)

def spawn_alga():
    x = random.randint(30, WIDTH - 30)
    rect = alga_img.get_rect(midtop=(x, -10))
    speed = random.randint(3, 6)
    algas.append({"rect": rect, "speed": speed})

def spawn_basura():
    x = random.randint(30, WIDTH - 30)
    rect = basura_img.get_rect(midtop=(x, -10))
    speed = random.randint(3, 6)
    basuras.append({"rect": rect, "speed": speed})

def spawn_lata():
    x = random.randint(30, WIDTH - 30)
    rect = lata_img.get_rect(midtop=(x, -10))
    speed = random.randint(2, 4)  # más lenta
    latas.append({"rect": rect, "speed": speed})

def spawn_llanta():
    x = random.randint(30, WIDTH - 30)
    rect = llanta_img.get_rect(midtop=(x, -10))
    speed = random.randint(1, 3)  # aún más lenta
    llantas.append({"rect": rect, "speed": speed})

# --- Puntos y estado ---
puntos = 0
META = 10
game_over = False
win = False

def draw_text(text, x, y, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# --- Bucle principal ---
while True:
    screen.blit(fondo, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SPAWN_ALGA_EVENT and not game_over and not win:
            spawn_alga()
        if event.type == SPAWN_BASURA_EVENT and not game_over and not win:
            spawn_basura()
        if event.type == SPAWN_LATA_EVENT and not game_over and not win:
            spawn_lata()
        if event.type == SPAWN_LLANTA_EVENT and not game_over and not win:
            spawn_llanta()
        if event.type == pygame.KEYDOWN and (game_over or win):
            if event.key == pygame.K_r:
                puntos = 0
                algas.clear()
                basuras.clear()
                latas.clear()
                llantas.clear()
                fish.topleft = (WIDTH // 2, HEIGHT - 60)
                game_over = False
                win = False

    # --- Movimiento del pez ---
    keys = pygame.key.get_pressed()
    if not game_over and not win:
        if keys[pygame.K_LEFT]: fish.x -= fish_speed
        if keys[pygame.K_RIGHT]: fish.x += fish_speed
        if keys[pygame.K_UP]: fish.y -= fish_speed
        if keys[pygame.K_DOWN]: fish.y += fish_speed
    fish.clamp_ip(screen.get_rect())

    # --- Algas (comida) ---
    for a in algas[:]:
        if not game_over and not win:
            a["rect"].y += a["speed"]
        if a["rect"].top > HEIGHT:
            algas.remove(a)
        elif fish.colliderect(a["rect"]):
            algas.remove(a)
            puntos += 1
            sonido_comer.play()
            if puntos >= META:
                win = True

    # --- Basura ---
    for b in basuras[:]:
        if not game_over and not win:
            b["rect"].y += b["speed"]
        if b["rect"].top > HEIGHT:
            basuras.remove(b)
        elif fish.colliderect(b["rect"]):
            basuras.remove(b)
            puntos -= 1
            sonido_malo.play()
            if puntos < 0:
                game_over = True

    # --- Latas ---
    for l in latas[:]:
        if not game_over and not win:
            l["rect"].y += l["speed"]
        if l["rect"].top > HEIGHT:
            latas.remove(l)
        elif fish.colliderect(l["rect"]):
            latas.remove(l)
            puntos -= 2
            sonido_malo.play()
            if puntos < 0:
                game_over = True

    # --- Llantas ---
    for t in llantas[:]:
        if not game_over and not win:
            t["rect"].y += t["speed"]
        if t["rect"].top > HEIGHT:
            llantas.remove(t)
        elif fish.colliderect(t["rect"]):
            llantas.remove(t)
            puntos -= 3
            sonido_malo.play()
            if puntos < 0:
                game_over = True

    # --- Dibujar ---
    for a in algas:
        screen.blit(alga_img, a["rect"].topleft)
    for b in basuras:
        screen.blit(basura_img, b["rect"].topleft)
    for l in latas:
        screen.blit(lata_img, l["rect"].topleft)
    for t in llantas:
        screen.blit(llanta_img, t["rect"].topleft)
    screen.blit(pez_img, fish.topleft)

    draw_text(f"Puntos: {puntos}", 10, 10)
    draw_text("Come algas 🪸  Evita basura 🗑️, latas 🥫 y llantas 🛞  -  R para reiniciar", 10, HEIGHT - 30, (200, 200, 200))

    if win:
        draw_text("¡Ganaste! 🐠", WIDTH // 2 - 100, HEIGHT // 2, (255, 255, 0))
    if game_over:
        draw_text("¡Perdiste! 😢", WIDTH // 2 - 100, HEIGHT // 2, (255, 100, 100))

    pygame.display.flip()
    clock.tick(60)
