import pygame
import os
import random
import math

class GameMap:
    def __init__(self):
        self.tile_size = 64  # Aumentado para 64x64 pixels
        self.width = 12  # 800/64
        self.height = 9   # 600/64
        
        # Carregar imagens
        self.images = {}
        self.load_images()
        
        # Criar um mapa básico
        self.map_data = self.generate_map()
        
    def load_images(self):
        # Criar texturas básicas para cada tipo de terreno
        # Grama
        grass_img = pygame.Surface((self.tile_size, self.tile_size))
        grass_img.fill((34, 139, 34))  # Verde escuro
        # Adicionar detalhes à grama
        for _ in range(20):
            x = random.randint(0, self.tile_size-1)
            y = random.randint(0, self.tile_size-1)
            pygame.draw.circle(grass_img, (0, 100, 0), (x, y), 2)
        self.images['grass'] = grass_img
        
        # Caminho
        path_img = pygame.Surface((self.tile_size, self.tile_size))
        path_img.fill((210, 180, 140))  # Marrom claro
        # Adicionar textura de terra
        for _ in range(30):
            x = random.randint(0, self.tile_size-1)
            y = random.randint(0, self.tile_size-1)
            pygame.draw.circle(path_img, (180, 150, 100), (x, y), 1)
        self.images['path'] = path_img
        
        # Água
        water_img = pygame.Surface((self.tile_size, self.tile_size))
        water_img.fill((0, 0, 139))  # Azul escuro
        # Adicionar ondulações
        for y in range(0, self.tile_size, 8):
            for x in range(self.tile_size):
                offset = math.sin(x * 0.2) * 2
                pygame.draw.line(water_img, (0, 0, 180), 
                               (x, int(y + offset)), (x, int(y + offset + 4)), 1)
        self.images['water'] = water_img
        
        # Castelo
        castle_img = pygame.Surface((self.tile_size, self.tile_size))
        castle_img.fill((169, 169, 169))  # Cinza
        # Adicionar detalhes do castelo
        # Muralhas principais
        pygame.draw.rect(castle_img, (120, 120, 120), (0, 0, self.tile_size, self.tile_size), 4)
        
        # Torres maiores
        tower_width = 20
        tower_height = 30
        pygame.draw.rect(castle_img, (100, 100, 100), 
                        (5, 5, tower_width, tower_height))
        pygame.draw.rect(castle_img, (100, 100, 100), 
                        (self.tile_size-tower_width-5, 5, tower_width, tower_height))
        
        # Ameias nas torres
        for i in range(3):
            x1 = 5 + i * 7
            x2 = self.tile_size - tower_width - 5 + i * 7
            pygame.draw.rect(castle_img, (80, 80, 80), (x1, 2, 5, 8))
            pygame.draw.rect(castle_img, (80, 80, 80), (x2, 2, 5, 8))
        
        # Porta do castelo com arco
        door_width = 24
        door_height = 32
        door_x = self.tile_size//2 - door_width//2
        door_y = self.tile_size - door_height
        # Porta principal
        pygame.draw.rect(castle_img, (60, 60, 60), 
                        (door_x, door_y, door_width, door_height))
        # Arco da porta
        pygame.draw.arc(castle_img, (80, 80, 80),
                       (door_x, door_y-10, door_width, 20),
                       0, math.pi, 2)
        
        self.images['castle'] = castle_img
        
        # Floresta
        forest_img = pygame.Surface((self.tile_size, self.tile_size))
        forest_img.fill((0, 100, 0))  # Verde muito escuro
        # Adicionar árvores mais detalhadas
        for _ in range(3):
            x = random.randint(10, self.tile_size-10)
            y = random.randint(20, self.tile_size-10)
            # Tronco mais largo
            trunk_width = 6
            trunk_height = 20
            pygame.draw.rect(forest_img, (101, 67, 33), 
                           (x-trunk_width//2, y, trunk_width, trunk_height))
            # Copa mais detalhada (várias camadas)
            for i in range(3):
                radius = 12 - i * 2
                pygame.draw.circle(forest_img, (0, 100+i*20, 0), 
                                 (x, y-5-i*4), radius)
        self.images['forest'] = forest_img
        
    def generate_map(self):
        # Criar um mapa básico com grama
        map_data = [['grass' for x in range(self.width)] for y in range(self.height)]
        
        # Adicionar alguns caminhos
        for x in range(2, 10):
            map_data[5][x] = 'path'
            map_data[6][x] = 'path'
        
        # Adicionar um pequeno lago
        for y in range(1, 4):
            for x in range(8, 11):
                map_data[y][x] = 'water'
                
        # Adicionar uma pequena floresta
        for y in range(7, 9):
            for x in range(1, 4):
                map_data[y][x] = 'forest'
                
        # Adicionar um castelo
        for y in range(1, 3):
            for x in range(1, 3):
                map_data[y][x] = 'castle'
                
        return map_data
    
    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.map_data[y][x]
                image = self.images[tile_type]
                screen.blit(image, (x * self.tile_size, y * self.tile_size)) 