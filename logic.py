import random
from typing import List, Tuple, Optional

# Тип цвета: RGB (0-255)
Color = Tuple[int, int, int]

# Размеры экрана (можно будет изменить при интеграции с интерфейсом)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DELETE_ZONE = ((0, 0), (100, 100))  # Левая верхняя зона для удаления (x1, y1), (x2, y2)

class Ball:
    def __init__(self, x: float, y: float, radius: float, color: Color, vx: float = 0, vy: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = vx
        self.vy = vy
        self.in_inventory = False

    def move(self):
        if not self.in_inventory:
            self.x += self.vx
            self.y += self.vy
            # Останавливаем на границах экрана
            if self.x - self.radius < 0:
                self.x = self.radius
                self.vx = -self.vx
            if self.x + self.radius > SCREEN_WIDTH:
                self.x = SCREEN_WIDTH - self.radius
                self.vx = -self.vx
            if self.y - self.radius < 0:
                self.y = self.radius
                self.vy = -self.vy
            if self.y + self.radius > SCREEN_HEIGHT:
                self.y = SCREEN_HEIGHT - self.radius
                self.vy = -self.vy

    def is_in_delete_zone(self) -> bool:
        (x1, y1), (x2, y2) = DELETE_ZONE
        return x1 <= self.x <= x2 and y1 <= self.y <= y2

    def distance_to(self, other: 'Ball') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def can_merge_with(self, other: 'Ball') -> bool:
        return self.distance_to(other) < self.radius + other.radius

    def merge_color(self, other: 'Ball') -> Color:
        # Интересное смешивание: HSV, но для простоты — случайное смешивание с небольшим шумом
        r = min(255, max(0, int((self.color[0] + other.color[0]) / 2 + random.randint(-10, 10))))
        g = min(255, max(0, int((self.color[1] + other.color[1]) / 2 + random.randint(-10, 10))))
        b = min(255, max(0, int((self.color[2] + other.color[2]) / 2 + random.randint(-10, 10))))
        # Если результат почти белый — делаем его менее белым
        if r > 220 and g > 220 and b > 220:
            r, g, b = 200, 200, 200
        return (r, g, b)

class Inventory:
    def __init__(self, size: int = 5):
        self.size = size
        self.slots: List[Optional[Ball]] = [None] * size

    def add_ball(self, ball: Ball) -> bool:
        for i in range(self.size):
            if self.slots[i] is None:
                self.slots[i] = ball
                ball.in_inventory = True
                return True
        return False  # Нет места

    def remove_ball(self, idx: int) -> Optional[Ball]:
        if 0 <= idx < self.size and self.slots[idx] is not None:
            ball = self.slots[idx]
            self.slots[idx] = None
            if ball:
                ball.in_inventory = False
            return ball
        return None

    def get_balls(self) -> List[Ball]:
        return [b for b in self.slots if b is not None]

class GameLogic:
    def __init__(self):
        self.balls: List[Ball] = []
        self.inventory = Inventory()

    def spawn_ball(self, x: float, y: float, radius: float, color: Color, vx: float = 0, vy: float = 0):
        self.balls.append(Ball(x, y, radius, color, vx, vy))

    def update(self):
        # Двигаем шарики
        for ball in self.balls:
            ball.move()
        # Смешиваем шарики при касании
        merged = set()
        for i, ball1 in enumerate(self.balls):
            for j, ball2 in enumerate(self.balls):
                if i >= j or i in merged or j in merged:
                    continue
                if ball1.can_merge_with(ball2):
                    new_color = ball1.merge_color(ball2)
                    ball1.color = new_color
                    ball2.color = new_color
                    merged.add(i)
                    merged.add(j)
        # Удаляем шарики из delete-зоны
        self.balls = [b for b in self.balls if not b.is_in_delete_zone()]

    def suck_ball_to_inventory(self, x: float, y: float) -> bool:
        # Находим ближайший шарик к координате (x, y)
        candidates = [b for b in self.balls if not b.in_inventory]
        if not candidates:
            return False
        closest = min(candidates, key=lambda b: ((b.x - x) ** 2 + (b.y - y) ** 2))
        if ((closest.x - x) ** 2 + (closest.y - y) ** 2) ** 0.5 <= closest.radius:
            if self.inventory.add_ball(closest):
                self.balls.remove(closest)
                return True
        return False

    def spit_ball_from_inventory(self, idx: int, x: float, y: float, vx: float = 0, vy: float = 0) -> bool:
        ball = self.inventory.remove_ball(idx)
        if ball:
            ball.x = x
            ball.y = y
            ball.vx = vx
            ball.vy = vy
            self.balls.append(ball)
            return True
        return False

    def get_balls(self) -> List[Ball]:
        return self.balls

    def get_inventory(self) -> List[Ball]:
        return self.inventory.get_balls()