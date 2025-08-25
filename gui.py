import pygame
import sys
import random
from logic import GameLogic, SCREEN_WIDTH, SCREEN_HEIGHT, DELETE_ZONE

# --- Настройки ---
START_BALLS = 50
BALL_RADIUS = 30
FPS = 60
INVENTORY_SLOT_SIZE = 50
INVENTORY_MARGIN = 10

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Шарики")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

game = GameLogic()

# Генерация случайных цветов
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (255, 128, 0), (128, 0, 255), (0, 128, 255)
]

# Спавним стартовые шарики
for _ in range(START_BALLS):
    x = random.randint(BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS)
    y = random.randint(BALL_RADIUS, SCREEN_HEIGHT - BALL_RADIUS)
    color = random.choice(COLORS)
    vx = random.uniform(-3, 3)
    vy = random.uniform(-3, 3)
    game.spawn_ball(x, y, BALL_RADIUS, color, vx, vy)

def draw_ball(ball):
    pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), int(ball.radius))
    pygame.draw.circle(screen, (0,0,0), (int(ball.x), int(ball.y)), int(ball.radius), 2)

def draw_inventory(inventory):
    balls = inventory
    for i in range(5):
        x = INVENTORY_MARGIN + i * (INVENTORY_SLOT_SIZE + INVENTORY_MARGIN)
        y = SCREEN_HEIGHT - INVENTORY_SLOT_SIZE - INVENTORY_MARGIN
        rect = pygame.Rect(x, y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)
        pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), rect, 2, border_radius=10)
        if i < len(balls):
            ball = balls[i]
            bx = x + INVENTORY_SLOT_SIZE // 2
            by = y + INVENTORY_SLOT_SIZE // 2
            pygame.draw.circle(screen, ball.color, (bx, by), int(ball.radius * 0.7))
            pygame.draw.circle(screen, (0,0,0), (bx, by), int(ball.radius * 0.7), 2)

def draw_delete_zone():
    (x1, y1), (x2, y2) = DELETE_ZONE
    rect = pygame.Rect(x1, y1, x2-x1, y2-y1)
    pygame.draw.rect(screen, (255, 100, 100), rect)
    pygame.draw.rect(screen, (200, 0, 0), rect, 3)
    text = font.render("Удалить", True, (0,0,0))
    screen.blit(text, (x1+10, y1+10))

def get_inventory_slot_at_pos(pos):
    mx, my = pos
    y = SCREEN_HEIGHT - INVENTORY_SLOT_SIZE - INVENTORY_MARGIN
    for i in range(5):
        x = INVENTORY_MARGIN + i * (INVENTORY_SLOT_SIZE + INVENTORY_MARGIN)
        rect = pygame.Rect(x, y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)
        if rect.collidepoint(mx, my):
            return i
    return None

# --- Игровой цикл ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button == 1:  # ЛКМ — всосать шарик
                if my < SCREEN_HEIGHT - INVENTORY_SLOT_SIZE - 2*INVENTORY_MARGIN:
                    game.suck_ball_to_inventory(mx, my)
            elif event.button == 3:  # ПКМ — выплюнуть из инвентаря
                slot = get_inventory_slot_at_pos((mx, my))
                if slot is not None:
                    # Выплёвываем в центр экрана
                    game.spit_ball_from_inventory(slot, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, random.uniform(-3,3), random.uniform(-3,3))

    game.update()

    screen.fill((255,255,255))
    draw_delete_zone()
    for ball in game.get_balls():
        draw_ball(ball)
    draw_inventory(game.get_inventory())

    pygame.display.flip()
    clock.tick(FPS)