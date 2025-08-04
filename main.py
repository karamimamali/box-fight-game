import pygame
import random
import time
from math import hypot, cos, sin, radians

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blade Balls")

WHITE = (255, 255, 255)
BALL_COLORS = [(255, 0, 0), (0, 0, 255)]
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

BALL_RADIUS = 30
BALL_SPEED = 4
POWERUP_SIZE = 30
BLADE_DURATION = 5
POWERUP_SPAWN_CHANCE = 0.32

clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont(None, 24)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 360)
        speed = random.uniform(3, 7)
        self.dx = cos(radians(angle)) * speed
        self.dy = sin(radians(angle)) * speed
        self.radius = random.randint(2, 5)
        self.color = color
        self.life = 60

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, win):
        if self.life > 0:
            pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radius)

class Ball:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.dx = random.choice([-1, 1]) * BALL_SPEED
        self.dy = random.choice([-1, 1]) * BALL_SPEED
        self.color = color
        self.health = 3
        self.has_blade = False
        self.blade_timer = 0

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x - BALL_RADIUS <= 0 or self.x + BALL_RADIUS >= WIDTH:
            self.dx *= -1
        if self.y - BALL_RADIUS <= 0 or self.y + BALL_RADIUS >= HEIGHT:
            self.dy *= -1
        if self.has_blade and time.time() - self.blade_timer > BLADE_DURATION:
            self.has_blade = False

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), BALL_RADIUS)
        if self.has_blade:
            for i in range(3):
                pygame.draw.circle(win, ORANGE, (int(self.x), int(self.y)), BALL_RADIUS + 3 + i, 2)

    def check_collision(self, other):
        dist = hypot(self.x - other.x, self.y - other.y)
        return dist < 2 * BALL_RADIUS

    def apply_blade(self):
        self.has_blade = True
        self.blade_timer = time.time()

    def separate_from(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        dist = hypot(dx, dy)
        if dist == 0:
            dist = 1
        overlap = 2 * BALL_RADIUS - dist
        if overlap > 0:
            push_x = dx / dist * overlap / 2
            push_y = dy / dist * overlap / 2
            self.x += push_x
            self.y += push_y
            other.x -= push_x
            other.y -= push_y

class PowerUp:
    def __init__(self, kind):
        self.kind = kind
        self.x = random.randint(POWERUP_SIZE, WIDTH - POWERUP_SIZE)
        self.y = random.randint(POWERUP_SIZE, HEIGHT - POWERUP_SIZE)
        self.rect = pygame.Rect(self.x, self.y, POWERUP_SIZE, POWERUP_SIZE)

    def draw(self, win):
        color = GREEN if self.kind == "health" else YELLOW
        pygame.draw.rect(win, color, self.rect)
        text = font.render(self.kind.capitalize(), True, BLACK)
        win.blit(text, (self.x, self.y - 20))

ball1 = Ball(100, 100, BALL_COLORS[0])
ball2 = Ball(700, 500, BALL_COLORS[1])
balls = [ball1, ball2]
powerups = []
last_powerup_spawn = time.time()
particles = []
game_over = False
winner = ""

running = True
while running:
    clock.tick(FPS)
    WIN.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        for ball in balls:
            ball.move()
            ball.draw(WIN)

        if ball1.check_collision(ball2):
            ball1.separate_from(ball2)
            if ball1.has_blade:
                ball2.health -= 1
                ball1.has_blade = False
            elif ball2.has_blade:
                ball1.health -= 1
                ball2.has_blade = False
            else:
                ball1.dx *= -1
                ball1.dy *= -1
                ball2.dx *= -1
                ball2.dy *= -1

        if time.time() - last_powerup_spawn >= 1:
            if random.random() < POWERUP_SPAWN_CHANCE:
                powerups.append(PowerUp(random.choice(["health", "blade", "blade"])))
            last_powerup_spawn = time.time()

        for pu in powerups:
            pu.draw(WIN)

        for ball in balls:
            ball_rect = pygame.Rect(ball.x - BALL_RADIUS, ball.y - BALL_RADIUS, 2 * BALL_RADIUS, 2 * BALL_RADIUS)
            for pu in powerups[:]:
                if ball_rect.colliderect(pu.rect):
                    if pu.kind == "health":
                        ball.health += 1
                    elif pu.kind == "blade":
                        ball.apply_blade()
                    powerups.remove(pu)

        health_font = pygame.font.SysFont(None, 30)
        WIN.blit(health_font.render(f"Red Health: {ball1.health}", True, BALL_COLORS[0]), (10, 10))
        WIN.blit(health_font.render(f"Blue Health: {ball2.health}", True, BALL_COLORS[1]), (10, 40))

        if ball1.health <= 0 or ball2.health <= 0:
            dead_ball = ball1 if ball1.health <= 0 else ball2
            for _ in range(40):
                particles.append(Particle(dead_ball.x, dead_ball.y, dead_ball.color))
            winner = "Blue" if ball1.health <= 0 else "Red"
            game_over = True
            game_over_time = pygame.time.get_ticks()

    for p in particles[:]:
        p.update()
        p.draw(WIN)
        if p.life <= 0:
            particles.remove(p)

    if game_over and len(particles) == 0:
        text = font.render(f"{winner} Wins!", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - 50, HEIGHT // 2))
        pygame.display.update()
        pygame.time.wait(3000)
        break

    pygame.display.update()

pygame.quit()
