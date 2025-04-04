import pygame
import os
import random
import math
from opensimplex import OpenSimplex

class Chunk:
    def __init__(self, x, y, tile_size, width, height, noise_gen):
        self.x = x  # Coordenada x do chunk no mundo
        self.y = y  # Coordenada y do chunk no mundo
        self.tile_size = tile_size
        self.width = width
        self.height = height
        self.noise_gen = noise_gen  # Usa o mesmo gerador de ruído do GameMap
        self.tiles = self.generate_chunk()
        
    def generate_chunk(self):
        tiles = [[None for x in range(self.width)] for y in range(self.height)]
        
        # Parâmetros ajustados para melhor definição do terreno
        scale = 25.0
        water_threshold = -0.35
        forest_threshold = 0.2
        path_threshold = 0.35
        castle_chance = 0.001
        
        # Offset grande o suficiente para evitar problemas com números negativos
        world_offset = 10000
        
        for y in range(self.height):
            for x in range(self.width):
                # Coordenadas absolutas no mundo com offset para lidar com negativos
                world_x = x + (self.x + world_offset) * self.width
                world_y = y + (self.y + world_offset) * self.height
                
                # Usar múltiplas camadas de ruído para mais variedade
                base_value = self.noise_gen.noise2(world_x / scale, world_y / scale)
                detail_value = self.noise_gen.noise2(world_x / (scale/2), world_y / (scale/2)) * 0.5
                value = (base_value + detail_value) / 1.5
                
                # Determinar tipo de terreno
                if value < water_threshold:
                    tiles[y][x] = 'water'
                elif value < 0:
                    tiles[y][x] = 'grass'
                elif value < forest_threshold:
                    tiles[y][x] = 'forest'
                elif value < path_threshold:
                    tiles[y][x] = 'path'
                else:
                    tiles[y][x] = 'grass'
                    
                # Castelos só em grama, longe da água
                if tiles[y][x] == 'grass' and random.random() < castle_chance:
                    # Verifica se há água próxima
                    has_water_nearby = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            check_y = y + dy
                            check_x = x + dx
                            if (0 <= check_y < self.height and 
                                0 <= check_x < self.width and 
                                tiles[check_y][check_x] == 'water'):
                                has_water_nearby = True
                                break
                    if not has_water_nearby:
                        tiles[y][x] = 'castle'
        
        return tiles

class GameMap:
    def __init__(self):
        self.tile_size = 64
        self.chunk_size = 12  # Tamanho de cada chunk em tiles
        self.view_distance = 2  # Quantos chunks são visíveis em cada direção
        
        # Seed fixo para garantir consistência no mapa
        self.world_seed = random.randint(0, 1000000)
        self.noise_gen = OpenSimplex(seed=self.world_seed)
        
        # Dicionário para armazenar chunks carregados
        self.chunks = {}
        
        # Carregar texturas
        self.images = {}
        self.load_images()
        
        # Posição da câmera (em tiles)
        self.camera_x = 0
        self.camera_y = 0
        
    def get_chunk_key(self, chunk_x, chunk_y):
        return f"{chunk_x},{chunk_y}"
        
    def get_or_create_chunk(self, chunk_x, chunk_y):
        key = self.get_chunk_key(chunk_x, chunk_y)
        if key not in self.chunks:
            self.chunks[key] = Chunk(chunk_x, chunk_y, self.tile_size, 
                                   self.chunk_size, self.chunk_size,
                                   self.noise_gen)  # Passa o gerador de ruído
        return self.chunks[key]
        
    def update_chunks(self, player_x, player_y):
        # Converter posição do jogador para coordenadas de chunk
        chunk_x = int(player_x / (self.tile_size * self.chunk_size))
        chunk_y = int(player_y / (self.tile_size * self.chunk_size))
        
        # Atualizar chunks visíveis
        visible_chunks = set()
        for y in range(chunk_y - self.view_distance, chunk_y + self.view_distance + 1):
            for x in range(chunk_x - self.view_distance, chunk_x + self.view_distance + 1):
                key = self.get_chunk_key(x, y)
                visible_chunks.add(key)
                if key not in self.chunks:
                    self.chunks[key] = Chunk(x, y, self.tile_size, 
                                           self.chunk_size, self.chunk_size,
                                           self.noise_gen)
        
        # Remover chunks fora da vista
        keys_to_remove = []
        for key in self.chunks:
            if key not in visible_chunks:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self.chunks[key]
            
    def get_tile_at(self, world_x, world_y):
        # Converter coordenadas do mundo para coordenadas de chunk e tile
        chunk_x = math.floor(world_x / (self.tile_size * self.chunk_size))
        chunk_y = math.floor(world_y / (self.tile_size * self.chunk_size))
        
        # Garantir que as coordenadas do tile dentro do chunk sejam sempre positivas
        tile_x = int(world_x - chunk_x * self.tile_size * self.chunk_size) // self.tile_size
        tile_y = int(world_y - chunk_y * self.tile_size * self.chunk_size) // self.tile_size
        
        # Garantir que estamos dentro dos limites do chunk
        if tile_x < 0:
            tile_x += self.chunk_size
            chunk_x -= 1
        if tile_y < 0:
            tile_y += self.chunk_size
            chunk_y -= 1
            
        chunk = self.get_or_create_chunk(chunk_x, chunk_y)
        if 0 <= tile_y < len(chunk.tiles) and 0 <= tile_x < len(chunk.tiles[0]):
            return chunk.tiles[tile_y][tile_x]
        return 'grass'  # Tile padrão
        
    def world_to_screen(self, world_x, world_y, camera_x, camera_y):
        screen_x = world_x - camera_x
        screen_y = world_y - camera_y
        return screen_x, screen_y
        
    def screen_to_world(self, screen_x, screen_y, camera_x, camera_y):
        world_x = screen_x + camera_x
        world_y = screen_y + camera_y
        return world_x, world_y

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
        
    def draw(self, screen, camera_x, camera_y):
        # Calcular quais chunks estão visíveis
        start_chunk_x = int(camera_x / (self.tile_size * self.chunk_size)) - self.view_distance
        start_chunk_y = int(camera_y / (self.tile_size * self.chunk_size)) - self.view_distance
        end_chunk_x = start_chunk_x + (self.view_distance * 2) + 1
        end_chunk_y = start_chunk_y + (self.view_distance * 2) + 1
        
        # Desenhar todos os chunks visíveis
        for chunk_y in range(start_chunk_y, end_chunk_y):
            for chunk_x in range(start_chunk_x, end_chunk_x):
                chunk = self.get_or_create_chunk(chunk_x, chunk_y)
                
                # Calcular posição na tela
                chunk_screen_x = chunk_x * self.chunk_size * self.tile_size - camera_x
                chunk_screen_y = chunk_y * self.chunk_size * self.tile_size - camera_y
                
                # Desenhar tiles do chunk
                for y in range(self.chunk_size):
                    for x in range(self.chunk_size):
                        tile_type = chunk.tiles[y][x]
                        screen_x = chunk_screen_x + x * self.tile_size
                        screen_y = chunk_screen_y + y * self.tile_size
                        
                        # Só desenhar se estiver na tela
                        if (-self.tile_size <= screen_x <= screen.get_width() and
                            -self.tile_size <= screen_y <= screen.get_height()):
                            screen.blit(self.images[tile_type], (screen_x, screen_y)) 