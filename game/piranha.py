import random

class Piranha:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = 2
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.movement_timer = 0
        self.movement_duration = random.randint(30, 90)  # Frames para mover em uma direção

    def change_direction(self):
        # Inverte a direção atual
        self.direction_x *= -1
        self.direction_y *= -1

    def update(self):
        self.movement_timer += 1
        if self.movement_timer >= self.movement_duration:
            self.movement_timer = 0
            self.movement_duration = random.randint(30, 90)
            self.direction_x = random.choice([-1, 1])
            self.direction_y = random.choice([-1, 1])

        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed 