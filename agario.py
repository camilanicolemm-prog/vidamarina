import pygame, sys, random, math

pygame.init()
WIDTH, HEIGHT = 960, 540
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini agar.io - Starter")
CLOCK = pygame.time.Clock()
FPS = 60

WORLD_W, WORLD_H = 2400, 2400  

def clamp(v, a, b): 
    return max(a, min(v, b))

def draw_grid(surf, camx, camy):
    surf.fill((18, 20, 26))
    color = (28, 32, 40)
    step = 64
    sx = -((camx) % step)
    sy = -((camy) % step)
    for x in range(int(sx), WIDTH, step):
        pygame.draw.line(surf, color, (x, 0), (x, HEIGHT))
    for y in range(int(sy), HEIGHT, step):
        pygame.draw.line(surf, color, (0, y), (WIDTH, y))

class food:
    __slots__ = ('x', 'y', 'r', 'col')
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.r = random.randint(3, 6)
        self.col = random.choice([
            (255, 173, 72), (170, 240, 170), (150, 200, 255),
            (255, 120, 160), (255, 220, 120)
        ])
    def draw(self, surf, camx, camy):
        pygame.draw.circle(surf, self.col, (int(self.x - camx), int(self.y - camy)), self.r)

class blob:
    def __init__(self, x, y, mass, color):
        self.x, self.y = x, y
        self.mass = mass
        self.color = color
        self.vx = 0.0
        self.vy = 0.0
        self.target = None
        self.alive = True
        
    @property
    def r(self):
        return max(6, int(math.sqrt(self.mass)))
    
    @property
    def speed(self):
        base = 260.0
        return max(60.0, base / (1.0 + 0.04 * self.r))
    
    def move_towards(self, tx, ty, dt):
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 1e-3:
            vx = (dx / dist) * self.speed
            vy = (dy / dist) * self.speed
        else:
            vx = vy = 0.0
        self.vx = self.vx * 0.85 + vx * 0.15
        self.vy = self.vy * 0.85 + vy * 0.15
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x = clamp(self.x, 0, WORLD_W)
        self.y = clamp(self.y, 0, WORLD_H)
        
    def draw(self, surf, camx, camy, outline=True):
        pygame.draw.circle(surf, self.color, (int(self.x - camx), int(self.y - camy)), self.r)
        if outline:
            pygame.draw.circle(surf, (255, 255, 255), (int(self.x - camx), int(self.y - camy)), self.r, 2)

class game:
    def __init__(self):
        self.reset()
        
    def reset(self):
        random.seed()
        self.player = blob(WORLD_W//2, WORLD_H//2, mass=600, color=(120,200,155))
        self.bots = []
        for _ in range(18):
            bx = random.randint(50, WORLD_W - 50)
            by = random.randint(50, WORLD_H - 50)
            mass = random.randint(200, 900)
            col = random.choice([
                (255, 144, 120), (255, 200, 90),
                (170, 240, 170), (160, 200, 255),
                (255, 120, 180)
            ])
            self.bots.append(blob(bx, by, mass, col))
        self.food = [food(random.randint(0, WORLD_W), random.randint(0, WORLD_H)) for _ in range(1200)]
        self.camx, self.camy = 0.0, 0.0
        self.time = 0.0
        self.state = "play"

    def update_camera(self, dt):
        self.camx = self.player.x - WIDTH // 2
        self.camy = self.player.y - HEIGHT // 2
        self.camx = clamp(self.camx, 0, WORLD_W - WIDTH)
        self.camy = clamp(self.camy, 0, WORLD_H - HEIGHT)

    def spawn_food_ring(self, cx, cy, count=40, radius=120):
        for i in range(count):
            ang = (i / count) * math.tau
            fx = cx + math.cos(ang) * radius + random.uniform(-10, 10)
            fy = cy + math.sin(ang) * radius + random.uniform(-10, 10)
            fx = clamp(fx, 0, WORLD_W)
            fy = clamp(fy, 0, WORLD_H)
            self.food.append(food(fx, fy))

    def update_player(self, dt):
        mx, my = pygame.mouse.get_pos()
        tx = self.camx + mx
        ty = self.camy + my
        self.player.move_towards(tx, ty, dt)
        
    def update_bots(self, dt):
        for b in self.bots:
            if not b.alive:
                continue
            threat = None
            prey = None
            mind = 1e9
            for other in self.bots + [self.player]:
                if other is b or not other.alive:
                    continue
                d = abs(other.x - b.x) + abs(other.y - b.y)
                if other.mass > b.mass * 1.35 and d < 480:
                    if d < mind:
                        mind = d
                        threat = other
                elif other.mass * 1.35 < b.mass and d < 420:
                    prey = other
            if threat is not None:
                tx = b.x - (threat.x - b.x)
                ty = b.y - (threat.y - b.y)
            elif prey is not None:
                tx, ty = prey.x, prey.y
            else:
                if b.target is None or random.random() < 0.005:
                    b.target = (random.randint(0, WORLD_W), random.randint(0, WORLD_H))
                tx, ty = b.target
            b.move_towards(tx, ty, dt)
            
    def eat_collisions(self):
        pr = self.player.r
        px, py = self.player.x, self.player.y
        remain_food = []
        for f in self.food:
            if abs(f.x - px) < pr + 12 and abs(f.y - py) < pr + 12:
                if (f.x - px)**2 + (f.y - py)**2 < (pr + f.r)**2:
                    self.player.mass += f.r * 0.9
                else:
                    remain_food.append(f)
            else:
                remain_food.append(f)
        self.food = remain_food
        
        for b in self.bots:
            if not b.alive:
                continue
            rsum = self.player.r - b.r * 0.95
            if rsum <= 0:
                continue
            if (b.x - px)**2 + (b.y - py)**2 < (rsum)**2 and self.player.mass > b.mass * 1.15:
                self.player.mass += b.mass * 0.8
                b.alive = False
                self.spawn_food_ring(b.x, b.y, count=50, radius=140)
                
        for b in self.bots:
            if not b.alive:
                continue
            if b.mass >= self.player.mass * 1.20:
                if (b.x - px)**2 + (b.y - py)**2 < (b.r - self.player.r)**2:
                    self.state = "gameover"
                    
    def dash(self):
        loss = self.player.mass * 0.05
        if self.player.mass - loss < 200:
            return
        self.player.mass -= loss
        mx, my = pygame.mouse.get_pos()
        tx, ty = self.camx + mx, self.camy + my
        dx, dy = tx - self.player.x, ty - self.player.y
        dist = math.hypot(dx, dy) + 1e-5
        self.player.vx += (dx / dist) * 900
        self.player.vy += (dy / dist) * 900
        
    def update(self, dt):
        if self.state != "play":
            return
        self.time += dt
        self.update_player(dt)
        self.update_bots(dt)
        self.eat_collisions()
        if len(self.food) < 1000:
            for _ in range(50):
                self.food.append(food(random.randint(0, WORLD_W), random.randint(0, WORLD_H)))
        if all(not b.alive for b in self.bots):
            self.state = "win"
        self.update_camera(dt)
                
    def draw(self):
        draw_grid(WINDOW, self.camx, self.camy)
        for f in self.food:
            fx, fy = int(f.x - self.camx), int(f.y - self.camy)
            if -10 <= fx <= WIDTH + 10 and -10 < fy < HEIGHT + 10:
                f.draw(WINDOW, self.camx, self.camy)
                
        for b in self.bots:
            if b.alive:
                b.draw(WINDOW, self.camx, self.camy)
                
        self.player.draw(WINDOW, self.camx, self.camy)
                
        pygame.draw.rect(WINDOW, (25, 28, 36), (10, 10, 300, 70), border_radius=8)
        font = pygame.font.SysFont(None, 24)
        WINDOW.blit(font.render(f"Mass: {int(self.player.mass)}", True, (235, 235, 245)), (20, 18))
        WINDOW.blit(font.render(f"mouse = mover / SPACE = dash (-5% masa)", True, (200, 220, 255)), (20, 44))
                
        if self.state == "gameover":
            t = pygame.font.SysFont(None, 48).render("GAME OVER", True, (255, 120, 120))
            r = t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            WINDOW.blit(t, r)
            s = pygame.font.SysFont(None, 28).render("[R] reiniciar - [ESC] salir", True, (235, 235, 245))
            WINDOW.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 26))
                    
        if self.state == "win":
            t = pygame.font.SysFont(None, 48).render("¡GANASTE!", True, (235, 235, 245))
            r = t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
            WINDOW.blit(t, r)
            s = pygame.font.SysFont(None, 28).render("Todos los bots fueron derrotados", True, (235, 235, 245))
            WINDOW.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 26))
                    
    def run(self):
        running = True
        while running:
            dt = CLOCK.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                    elif e.key == pygame.K_r:
                        self.reset()
                    elif e.key == pygame.K_SPACE and self.state == "play":
                        self.dash()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()


def main():
    g = game()
    g.run()

if __name__ == "__main__":
    main()
