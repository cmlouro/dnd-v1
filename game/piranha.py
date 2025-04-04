import random
import pygame
import os
import math

class Piranha:
    def __init__(self, x, y, game_map):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = 2
        self.direction = random.uniform(0, 2 * math.pi)  # Direção aleatória
        self.game_map = game_map  # Referência para o mapa
        
        # Carrega e ajusta a imagem da piranha
        self.image = pygame.image.load(os.path.join('assets', 'images', 'piranha-fish.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.original_image = self.image
            
    def is_in_water(self, x, y):
        # Verifica se a posição está em água
        return self.game_map.get_tile_at(x, y) == 'water'
            
    def update(self):
        # Calcula a próxima posição
        next_x = self.x + self.speed * math.cos(self.direction)
        next_y = self.y + self.speed * math.sin(self.direction)
        
        # Só move se a próxima posição estiver na água
        if self.is_in_water(next_x, next_y):
            self.x = next_x
            self.y = next_y
        else:
            # Se vai sair da água, muda a direção
            self.direction = random.uniform(0, 2 * math.pi)
        
        # Muda de direção aleatoriamente com menos frequência
        if random.random() < 0.01:  # 1% de chance por frame
            self.direction = random.uniform(0, 2 * math.pi)
            
    def draw(self, screen, camera_x, camera_y):
        # Calcula a posição na tela
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Só desenha se estiver visível na tela
        if (-self.width <= screen_x <= screen.get_width() + self.width and
            -self.height <= screen_y <= screen.get_height() + self.height):
            # Rotaciona a imagem na direção do movimento
            angle = math.degrees(self.direction)
            rotated_image = pygame.transform.rotate(self.original_image, -angle - 90)
            screen.blit(rotated_image, (
                screen_x - rotated_image.get_width()/2,
                screen_y - rotated_image.get_height()/2
            )) 